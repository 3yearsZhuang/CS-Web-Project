# 全栈部署 / 运维（RootDoc-Deploy）

> 更新人：3yearsZ
> 最后更新：2026-08-05（统一 RootDoc 命名）
> 根级编排层的部署唯一权威。覆盖：本地开发并行启动、容器化全栈部署（db+backend+frontend+caddy）、回滚、数据卷与备份。
> 深链接（各端专项，勿在此重复）：前端 `CS-Web-Frontend/tools/docs/FrontDoc-Ops.md`（Docker/Caddy/SLO/Runbook）、后端 `CS-Web-Backend/docs/BackDoc-Infra.md`（运维端点 `/health /readyz /metrics/json /status`）。

---

## 一、架构总览

```text
浏览器 ──HTTPS──> Caddy(:80/:443) ──> cs-website(Next.js BFF :2333)
                                          │ BACKEND_URL=http://backend:8000
                                          ▼
                                     backend(FastAPI :8000) ──> db(PostgreSQL:5432)
```

- 前端 BFF 通过内部网络 `cs-net` 直连后端，后端不暴露公网端口（容器 `expose: 8000`，仅内网）。
- 公网只暴露 Caddy（80/443，自动 HTTPS）。
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
| `TRUST_PROXY` | 是否信任反向代理头（Caddy 后须 true） | 生产 ✅ |

> 本地覆盖用不跟踪的 `.env.local`；后端开发模板 `.env.development`（最全参考样板），见后端 `docs/BackDoc-Conv.md` §7。

---

## 三、本地开发（并行起前后端）

```bash
make dev-up        # 并行起后端(:9000 热重载) + 前端(:2333 dev)
# 或分别：make dev-backend / make dev-frontend
```

- 后端：`python run.py --env 1 --port 9000` → Swagger `http://localhost:9000/docs`
- 前端：`pnpm dev` → `http://localhost:2333`

---

## 四、容器化部署（全栈一键）

```bash
make setup        # 首次：cp .env.example .env，并填写全部密钥
# 编辑 .env：DATABASE_PASSWORD / SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET
# 有域名：把 deploy/caddy/Caddyfile 中的 cs.yourdomain.com 改为你的域名
make up           # docker compose up -d --build（db+backend+frontend+caddy）
make ps           # 查看状态
make logs         # 跟踪日志
make rebuild      # 强制重建并重启
make down         # 停止
```

- 无域名：去掉 compose 里的 `caddy` 服务，直接访问 `http://<host>:2333`。
- 后端 Swagger：`http://<host>:9000/docs`（容器内 `expose: 8000`，仅内网，不映射公网端口）。

**关键行为**：
- 后端 `DB_AUTO_CREATE_DATABASE=true` + `DB_AUTO_MIGRATE=true` → 空库自动建库并 `alembic upgrade head`。
- `build.context` 指向各自 submodule 目录（`./CS-Web-Backend`、`./CS-Web-Frontend`），Dockerfile 内路径相对自身，无需改动。

---

## 五、健康检查与运维端点

| 端点 | 鉴权 | 说明 |
|---|---|---|
| `GET /health` | 公开 | liveness 浅检查（进程存活） |
| `GET /readyz` | 公开 | readiness，不通返回 **503** |
| `GET /metrics/json` | 超级用户 | 单实例内存指标 JSON |
| `GET /status` | 超级用户 | 各组件状态明细 |

> 标准 OTel 指标经 OTLP **推送**到 collector（Jaeger/Tempo/otel-collector），再由 Grafana 消费；默认 `OTEL_ENABLED=False` 完全 no-op。详见后端 `docs/BackDoc-Infra.md`。

---

## 六、回滚与故障处置

- **后端回滚**：迁移可 `alembic downgrade`（见后端 `docs/BackDoc-MigV.md`）；代码回滚 = 重建该 submodule 镜像。
- **前端回滚**：重建 `cs-website` 镜像（前端为纯 BFF，无本地状态库）。
- **数据卷**：`pgdata` 持久化 PG；`data/` 持久化上传文件；删除容器不删卷（`docker compose down` 不加 `-v`）。

> 专项 Runbook（Docker 部署细节、Caddy 配置、恢复演练）见前端 `FrontDoc-Ops.md`。
