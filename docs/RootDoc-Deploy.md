# 全栈部署 / 运维（RootDoc-Deploy）

> 更新人：3yearsZ
> 最后更新：2026-08-08（补充 0.9.8 部署要点：可选 LLM_* 环境变量与 Auxilio 降级、/health 健康检查端点、Node>=22 / Python>=3.13 运行环境、docker-compose 子仓库(submodule) 构建上下文）
> 对应版本：0.9.8（后端 `CS-Web-Backend/app/__init__.py` `__version__ = "0.9.8"`）。部署文档权威基线，端侧细节见深链接。
> 根级编排层的部署唯一权威。覆盖：本地开发并行启动、容器化全栈部署（db+backend+redis+worker+frontend）、回滚、数据卷与备份。
> 深链接（各端专项，勿在此重复）：前端 `CS-Web-Frontend/tools/docs/FrontDoc-Ops.md`（Docker/外部反向代理/SLO/Runbook）、后端 `CS-Web-Backend/tools/docs/BackDoc-Infra.md`（运维端点 `/health /readyz /metrics/json /status`）。跨端 SLO 与可观测性基线见本文 **§七**。

---

## 一、架构总览

```text
浏览器 ──> 外部反向代理（可选）──> 127.0.0.1:2333 cs-website(Next.js BFF)
                                          │ BACKEND_URL=http://backend:8000
                                          ▼
                                     backend(FastAPI :8000) ──> db(PostgreSQL:5432)
```

- 前端 BFF 通过内部网络 `cs-net` 直连后端，后端不暴露公网端口（容器 `expose: 8000`，仅内网）。

> 端口约定：容器编排内后端服务端口固定为 **8000**（前端 `BACKEND_URL=http://backend:8000`）；本地开发经 `Makefile` 的 `run.py --port 9000` 暴露 **9000** 供宿主机直连。两者指向同一服务，仅场景不同。
- 前端仅绑定宿主机回环地址 `127.0.0.1:2333`；后续由部署者自行配置外部反向代理和 HTTPS。
- 数据卷：`pgdata`（PostgreSQL）、根级 `data/`（上传文件）。前端为纯 BFF 层，无本地数据库备份（业务数据统一由 PostgreSQL 承载，原 Litestream/SQLite 备份体系已移除）。

---

## 二、环境与密钥

见根 `.env.example`。必填密钥（缺任一导致启动失败或功能降级）：

| 变量 | 用途 | 必填 |
|------|------|------|
| `DATABASE_PASSWORD` | PostgreSQL 密码 | ✅ |
| `SECRET_KEY` | 后端 JWT 签名密钥（≥32B） | ✅ |
| `TOTP_ENCRYPTION_KEY` | 后端 2FA 加密密钥（≥32B） | ✅ |
| `AUTH_SESSION_SECRET` | 前端 Session 密钥（≥32B） | ✅ |
| `ALLOWED_ORIGINS` | 前后端 CORS / Origin 白名单 | 生产 ✅ |
| `NEXT_PUBLIC_SITE_URL` | 站点 URL | 生产 ✅ |
| `TRUST_PROXY` | 是否信任反向代理头（默认 `false`；外部反代配置后设为 `true`） | 按部署方式 |

> 本地覆盖用不跟踪的 `.env.local`；后端开发模板 `.env.development`（最全参考样板），见后端 `CS-Web-Backend/tools/docs/BackDoc-Conv.md` §7。

### 2.1 运行环境要求（0.9.8）

| 组件 | 最低版本 | 依据 |
|------|----------|------|
| Node.js（前端 BFF 构建/运行） | `>=22` | 前端 `CS-Web-Frontend/package.json` `engines.node` |
| Python（后端运行时） | `>=3.13` | 后端 `CS-Web-Backend/pyproject.toml` `requires-python`；镜像 `python:3.13-slim` |

> 低于上述版本会导致前端依赖解析失败或后端镜像构建失败，部署前须确认本地与 CI 环境达标。

### 2.2 可选环境变量：LLM 学习助手（Auxilio，0.9.8 新增）

Auxilio 为内置学习助手 Agent；其 LLM 能力通过以下可选变量开启，**未配置时 `LLM_PROVIDER` 默认 `none`，Auxilio 自动降级为纯规则推荐模式（不调用任何外部模型，不影响其他功能）**：

| 变量 | 用途 | 必填 | 默认值 |
|------|------|------|--------|
| `LLM_PROVIDER` | LLM 供应商：`openai`（OpenAI 兼容协议）/ `anthropic` / `none`（禁用→规则模式） | 否 | `none` |
| `LLM_API_KEY` | 供应商 API Key（仅存 `.env`，不落库/日志/前端） | 否（开启 LLM 时必填） | 空 |
| `LLM_BASE_URL` | OpenAI 兼容自定义网关（DeepSeek / 通义 / Kimi / 本地 vLLM） | 否 | 空 |
| `LLM_MODEL` | 模型名（如 `gpt-4o-mini`） | 否 | `gpt-4o-mini` |
| `LLM_TIMEOUT` | 单次调用超时（秒） | 否 | `60` |
| `LLM_MAX_TOKENS` | 单次回复最大 token | 否 | `1024` |
| `LLM_DAILY_BUDGET` | 单用户每日调用预算（0=不限制，防成本失控） | 否 | `200` |

> 仅当 `LLM_PROVIDER` 设为 `openai` / `anthropic` 时才需配套 `LLM_API_KEY`（及可选 `LLM_BASE_URL` / `LLM_MODEL`）。`none` 模式下全部 LLM 变量可留空。
> 注意：根 `.env.example` 当前未列出上述 `LLM_*` 项（代码默认值已可运行），如需显式示例可补充；详见文末「信息缺口声明」。

---

## 三、本地开发（并行起前后端）

```bash
make dev-up        # 并行起后端(:9000 热重载) + 前端(:2333 dev)
# 或分别：make dev-backend / make dev-frontend
```

- 后端：`python run.py --env 1 --port 9000` → Swagger `http://localhost:9000/docs`
  - 注：`run.py` 默认端口为 8000，`Makefile` 显式传 `--port 9000`；容器编排内则为 8000（见架构图）。
- 前端：`pnpm dev` → `http://localhost:2333`

---

## 四、容器化部署（全栈一键）

```bash
make setup        # 首次：cp .env.example .env，并填写全部密钥
# 编辑 .env：DATABASE_PASSWORD / SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET
# 前端默认绑定 127.0.0.1:2333；后续由部署者自行配置 HTTPS 反向代理
make up           # docker compose up -d --build（db+backend+redis+worker+frontend）
make ps           # 查看状态
make logs         # 跟踪日志
make rebuild      # 强制重建并重启
make down         # 停止
```

- 前端访问入口：`http://127.0.0.1:2333`（服务器本机验证）；外部反向代理应转发到该地址。
- 如需临时从其他机器直连测试，可将端口映射改为 `0.0.0.0:2333:2333`，正式环境不建议这样暴露。
- 后端 Swagger：`http://<host>:9000/docs`（本地 `make dev-up` 暴露；容器编排内后端为 `:8000`，由前端 BFF 经 `backend:8000` 直连，不映射公网）。

> 生产模式使用 `Secure` Cookie。正式使用必须由外部反向代理提供 HTTPS；直接使用 HTTP 端口主要用于部署验证。

**关键行为**：
- 后端 `DB_AUTO_CREATE_DATABASE=true` + `DB_AUTO_MIGRATE=true` → 空库自动建库并 `alembic upgrade head`。
- `build.context` 指向各自子仓库(submodule) 目录（`./CS-Web-Backend`、`./CS-Web-Frontend`），Dockerfile 内路径相对自身，无需改动。

---

## 五、健康检查与运维端点

| 端点 | 鉴权 | 说明 |
|---|---|---|
| `GET /health` | 公开 | liveness 浅检查（进程存活） |
| `GET /health/events` | 公开 | 事件总线各事件监听器数量（运维快速定位事件链路） |
| `GET /health/security` | 公开 | 限流/会话黑名单/迁移/多实例安全组件状态 |
| `GET /readyz` | 公开 | readiness，不通返回 **503** |
| `GET /metrics/json` | 超级用户 | 单实例内存指标 JSON |
| `GET /status` | 超级用户 | 各组件状态明细 |

> 健康检查根路径为 `/health`（**非** `/api/v1/health`）：运维/探针端点挂在根 `root_router` 上，不受 `API_V1_STR=/api/v1` 前缀影响。

> 标准 OTel 指标经 OTLP **推送**到 collector（Jaeger/Tempo/otel-collector），再由 Grafana 消费；默认 `OTEL_ENABLED=False` 完全 no-op。详见后端 `CS-Web-Backend/tools/docs/BackDoc-Infra.md`。

---

## 六、回滚与故障处置

- **后端回滚**：迁移可 `alembic downgrade`（见后端 `CS-Web-Backend/tools/docs/BackDoc-Infra.md` §六 迁移验证）；代码回滚 = 重建该子仓库(submodule) 镜像。
- **前端回滚**：重建 `cs-website` 镜像（前端为纯 BFF，无本地状态库）。
- **数据卷**：`pgdata` 持久化 PG；`data/` 持久化上传文件；删除容器不删卷（`docker compose down` 不加 `-v`）。

> 专项 Runbook（Docker 部署细节、外部反向代理接入、恢复演练）见前端 `CS-Web-Frontend/tools/docs/FrontDoc-Ops.md`。

---

## 六·A、开发库 → 生产库迁移（PG → PG）

> 本项目唯一数据源是后端 PostgreSQL（前端为纯 BFF，无本地库），因此"环境间迁移"本质是 **PostgreSQL → PostgreSQL 的库迁移**，不是 SQLite→PG（历史 SQLite→PG 映射脚本 `migrate-sqlite-to-pg.mjs` 已删除，不适用）。
> 备份/恢复统一用 `CS-Web-Backend/tools/scripts/backup_db.sh`；导出到桌面用根级 `scripts/export_db_to_desktop.sh`。

### 1. 导出（开发环境）

```bash
# 根级脚本：导出开发库到 ~/Desktop（默认）
./scripts/export_db_to_desktop.sh
# 或指定目录
./scripts/export_db_to_desktop.sh /path/to/out

# 也可用后端脚本直接备份（容器内 db 服务名可直连时）
./CS-Web-Backend/tools/scripts/backup_db.sh /path/to/backup
```

- 连接参数取自根 `.env` 的 `DATABASE_HOST/PORT/NAME/USER/PASSWORD`。
- 根 `.env` 中 `DATABASE_HOST=db` 是 docker-compose 容器内服务名，宿主机不可直连。`export_db_to_desktop.sh` 已内置回退：当 `.env` 为 `db` 且未显式指定时自动改用 `localhost`；也可用 `DATABASE_HOST_OVERRIDE=localhost` 强制指定。
- 输出：`domefff_<时间戳>.sql.gz`（`pg_dump --format=custom` + gzip，已做完整性校验）。

### 2. 传输到生产服务器

```bash
scp /Users/you/Desktop/domefff_*.sql.gz user@prod-host:/opt/cs-backup/
```

> 备份含全部业务数据（含用户密码哈希），**禁止提交进仓库、禁止经不安全渠道传输**。

### 3. 恢复（生产环境）

**情形 A：生产是空库（推荐）**

```bash
# 在生产机：先起 db 服务，再用根脚本的 --restore 模式（读取生产 .env）
cd /path/to/FztbuCS-Project
./CS-Web-Backend/tools/scripts/backup_db.sh --restore /opt/cs-backup/domefff_xxx.sql.gz
# 或直接在 db 容器内 pg_restore
docker compose exec -T db pg_restore -U postgres --no-owner --no-privileges -d domefff \
  < /opt/cs-backup/domefff_xxx.sql
```

**情形 B：生产已有 seed 数据（admin 用户、预置角色）**

直接灌会撞主键/唯一约束。需按 `docs/RootDoc-MigEval.md` 的"按 email/username 去重"策略处理，或先清空 `pgdata` 卷再导入：

```bash
docker compose down
docker volume rm fztbucs-project_pgdata   # 卷名以实际为准
docker compose up -d db
# 再执行情形 A 的恢复
```

### 4. 收尾（防后续插入主键冲突）

导入后重建所有自增序列，使其对齐当前最大值：

```bash
docker compose exec db psql -U postgres -d domefff -c \
  "SELECT setval(pg_get_serial_sequence(tbl.relname,'id'), COALESCE((SELECT MAX(id) FROM tbl),1)) \
   FROM pg_class tbl JOIN pg_namespace ns ON ns.oid=table(tbl).relnamespace \
   WHERE tbl.relkind='r' AND EXISTS (SELECT 1 FROM information_schema.columns c \
     WHERE c.table_name=tbl.relname AND c.column_name='id' AND c.data_type='integer');"
```

> 实际逐表 `setval` 更稳妥；上面为示意。启动 `backend` 后其 `DB_AUTO_MIGRATE=true` 会把 schema 补齐到 head（已最新则无操作）。

### 5. 校验

- 行数核对：关键表 `users / community_posts / events / exams / roles` 与源库对账。
- 外键完整性：抽查 FK 无悬空（参考 `RootDoc-MigEval.md` §4.3 的 P1 风险项）。
- 静态资源：`data/`（头像 `avatars/`、社区图 `community-images/`）需单独 `rsync` 到生产 `data/` 卷，数据库只存路径。

### 6. 密钥注意

生产 `DATABASE_PASSWORD / SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET` 必须与开发**不同**（密钥不可复用，见 `RootDoc-EngConv.md` §四）。若迁移用户密码哈希（scrypt），后端已支持懒升级到 bcrypt，登录时自动升级，可正常登录。

---

> 专项 Runbook（Docker 部署细节、外部反向代理接入、恢复演练）见前端 `CS-Web-Frontend/tools/docs/FrontDoc-Ops.md`。

---

## 七、SLO 与可观测性基线

> 本章为根级编排层的 SLO 与可观测性基线单一事实源。前端 BFF 端点级 SLO / 错误预算消耗规则 / 评审流程见前端 `CS-Web-Frontend/tools/docs/FrontDoc-Ops.md` Part B（两者为补充关系，非重复）。

# SLO 与可观测性基线（1.0.0）

> 适用范围：CS-Web-Backend + CS-Web-Frontend
> 版本：1.0.0 起计划生效，后续版本按实际运行数据迭代

---

### 可用性

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| API 可用性 | 99%（每月停机 ≤ 438 分钟） | `/health` + `/readyz` 探针成功率，按月统计 |
| 前端页面可用性 | 99% | 首页 HTTP 200 成功率 |

### 延迟

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| API p95 延迟 | < 500ms | FastAPI 请求日志 `duration_ms` 字段 |
| API p99 延迟 | < 2000ms | 同上 |
| 前端首屏加载（LCP） | < 2.5s | 浏览器 Performance API（1.1 接入 RUM） |

### 数据持久性

| 指标 | 目标 | 测量方式 |
|------|------|----------|
| 数据库备份 RPO | ≤ 24h | 每日 03:00 cron 全量备份 |
| 数据库恢复 RTO | ≤ 4h | 从备份恢复到服务可用 |
| 备份保留 | 14 天 | `backup_db.sh` 自动清理过期文件 |

---

### 错误预算

月度错误预算 = 总分钟数 × (1 - SLO) = 43200 × 1% = **432 分钟/月**

错误预算耗尽时的行动：
- 冻结非紧急变更，集中精力修复稳定性问题
- 评估是否需要调整 SLO 目标（而非放松标准）

---

### 可观测性基线

**日志**

| 组件 | 格式 | 关键字段 |
|------|------|----------|
| 后端 | loguru JSON（prod profile） | timestamp, level, request_id, user_id, method, path, status, duration_ms |
| 前端 | pino NDJSON | timestamp, level, request_id, msg |

日志保留：文件轮转 10 MB × 30 天（后端），pino 日志按部署环境配置。

**健康检查端点**

| 端点 | 用途 | 检查内容 |
|------|------|----------|
| `GET /health` | liveness | 进程存活（浅检查） |
| `GET /health/events` | 事件 | 事件总线各事件监听器数量 |
| `GET /health/security` | 安全 | 限流/会话黑名单/迁移/多实例安全组件状态 |
| `GET /readyz` | readiness | 数据库连通性，不通返回 503 |
| `GET /metrics/json` | 指标 | 请求数/延迟分布/错误率（需 system:monitor 权限） |
| `GET /status` | 详细状态 | 应用配置/连接池/版本（需 system:monitor 权限） |

**告警规则（最小集）**

以下告警通过日志监控或外部探针实现，1.0.0 不依赖 Prometheus：

| 告警 | 条件 | 级别 | 通知方式 |
|------|------|------|----------|
| 服务不可用 | `/health` 连续 3 次失败（间隔 10s） | P0 | 日志 + 邮件 |
| 数据库不可达 | `/readyz` 连续 2 次返回 503 | P0 | 日志 + 邮件 |
| 错误率飙升 | 5xx 占比 > 5%（5 分钟窗口） | P1 | 日志 |
| 备份失败 | `backup_db.sh` exit code ≠ 0 | P1 | cron 日志 |
| 磁盘空间不足 | 磁盘使用率 > 85% | P1 | 系统监控 |

**OpenTelemetry（可选增强）**

1.0.0 默认关闭 OTel。如需启用：

```env
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
OTEL_SERVICE_NAME=cs-web-backend
```

启用后自动埋点 FastAPI / SQLAlchemy / Redis，traces + metrics 经 OTLP 导出。

---

### 运维巡检清单

每日：
- 确认备份脚本执行成功（检查 `backups/` 目录最新文件）
- 浏览错误日志中的 ERROR 级别条目

每周：
- 检查磁盘空间和日志文件大小
- 验证 `/readyz` 响应正常

每月：
- 评估 SLO 达成情况
- 检查错误预算消耗
- 评估是否需要调整 SLO 目标

每季度：
- 执行一次数据库恢复演练
- 审查告警规则有效性

---

## 八、信息缺口声明（0.9.8）

- **`.env.example` 未列出 `LLM_*` 变量**：后端 `CS-Web-Backend/app/core/config.py` 已定义 `LLM_PROVIDER/LLM_API_KEY/LLM_BASE_URL/LLM_MODEL/LLM_TIMEOUT/LLM_MAX_TOKENS/LLM_DAILY_BUDGET`，默认 `LLM_PROVIDER=none` 即可运行；如要求示例值显式化，需补 `.env.example`（超出本文档范围，标记待办）。
- **运行环境版本以代码为准**：Node>=22 / Python>=3.13 取自 `package.json` 与 `pyproject.toml`，后续升级须同步本文 §2.1。
- **迁移 head 以 `CS-Web-Backend/alembic` 实际链为准**：现行 Alembic head 为 `d3e4f5a6b7c8`（详见 `docs/RootDoc-MigEval.md` §七），本文不重复迁移细节。
