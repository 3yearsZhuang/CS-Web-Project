# Onboarding 手册（新开发者 / 新管理员第一天）

> 一份「环境 → 本地跑通 → 部署上线 → 常见故障排查」一条龙傻瓜式教程。
> 配套权威文档：`docs/README.md`（文档地图）、`docs/RootDoc-Deploy.md`（部署运维）。

---

## 0. 当前真实进度（先读这一段，避免被"目标态"误导）

截至 2026-08-07，项目处于 **0.9.8 → 1.0.0 准备期**。请务必区分"真实态"与"目标态"：

| 维度 | 真实态（当前代码） | 目标态（1.0.0 计划） |
|---|---|---|
| 架构 | 前后端分离：FastAPI 后端（PG）+ Next.js 前端（BFF 薄转发） | 同左，且前端**纯 BFF** |
| 数据存储 | 业务数据 100% 在后端 PostgreSQL；前端 **零 SQLite 依赖**（`shared/db` 双引擎代码、遗留脚本、`better-sqlite3` 依赖已于 2026-08-07 全部删除） | 同左（已达成） |
| 前端 `src/modules/*/server/` | **已全部删除**（B1 收口完成，业务 100% 走后端 API + 前端 BFF 薄转发） | 同左 |
| 契约 | `/api/v1/**` 已落地，camelCase 传输 | 冻结契约 + OpenAPI 比对门禁 |
| 安全门禁 | 前端 `pnpm audit` 已改为 moderate 阻断；后端 pytest 依赖已固化 | CI 全绿 + 测试阶段可复现 |
| 文档 | 本手册 + 根级 `docs/` 已建 | 各文档顶部加"真实进度"标注（进行中） |

> 当前前端已是**纯 BFF**：`src/modules/*/server/`、`src/shared/db` 均已删除，业务数据统一在后端 PostgreSQL。新功能一律走后端 API + 前端 BFF 转发。

---

## 1. 环境准备（开发者）

### 1.1 工具链

| 工具 | 版本 | 用途 |
|---|---|---|
| Git | 任意新版本 | 拉取含 submodule 的仓库 |
| Python | **3.13+**（与后端 `pyproject.toml` 一致；3.9 会因 `X \| None` 语法失败） | 后端运行 / 测试 |
| Node.js | 22 | 前端运行 / 构建 |
| pnpm | 9.0.0 | 前端包管理（CI 锁定此版本） |
| Docker + Compose | 新版 | 容器化全栈部署 |
| PostgreSQL | 16（容器自动起） | 生产/测试数据库 |

### 1.2 克隆仓库（含 submodule）

```bash
git clone <root-repo-url> FztbuCS-Project
cd FztbuCS-Project
git submodule update --init --recursive
```

### 1.3 后端环境

```bash
cd CS-Web-Backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"        # 安装运行时 + pytest 全家桶（G2 已固化版本）
cp .env.example .env            # 填写 DATABASE_PASSWORD / SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET
```

### 1.4 前端环境

```bash
cd CS-Web-Frontend
pnpm install
cp .env.example .env            # 至少填 AUTH_SESSION_SECRET / ALLOWED_ORIGINS / NEXT_PUBLIC_SITE_URL
```

---

## 2. 本地跑通

### 2.1 一键并行起（推荐）

```bash
# 在仓库根目录
make setup        # 首次：cp .env.example .env
make dev-up       # 后端 :9000 热重载 + 前端 :2333 dev 同时前台运行
```

- 前端：http://localhost:2333
- 后端 Swagger：http://localhost:9000/docs（本地 `make dev-up` 经 `run.py --port 9000` 暴露）
- 前端 BFF 经 `BACKEND_URL=http://localhost:9000` 转发（见前端 `.env`）

> 端口约定：本地开发后端经 `run.py --port 9000` 暴露 9000；容器编排内后端服务端口为 8000，前端 BFF 经 `backend:8000` 直连（容器内 `expose: 8000`，不映射公网）。两者指向同一服务，仅场景不同。

### 2.2 分开起（调试某一端）

```bash
make dev-backend    # 仅后端
make dev-frontend   # 仅前端
```

### 2.3 验证跑通

- 打开前端 → 注册账号（验证码）→ 登录 → 访问 `/profile` 看到完整用户信息。
- 后端 `/auth/me` 返回 200 + 用户字段（camelCase）。
- 健康检查：`GET /api/health`（前端 BFF 转发到后端 `/health`）。

### 2.4 跑测试（验收-4 前置）

```bash
# 后端（需 PostgreSQL 测试库，pytest 自动加载 .env.test 并拒绝非 test 库名）
cd CS-Web-Backend && python -m pytest

# 前端
cd CS-Web-Frontend && pnpm test -- --run
pnpm run ts-check && pnpm run lint:build
```

---

## 3. 部署上线（管理员）

### 3.1 容器化全栈（生产推荐）

```bash
# 仓库根目录
make setup
# 编辑 .env：填齐 4 个密钥；前端默认绑定 127.0.0.1:2333
make up            # docker compose up -d --build
make ps            # 查看状态
make logs          # 跟踪日志
```

- 前端绑定宿主机回环地址 `127.0.0.1:2333`，后续由部署者自行配置 HTTPS 反向代理。
- 后端不暴露公网，前端 BFF 经内部网络 `cs-net` 直连 `backend:8000`。
- 数据卷：`pgdata`（PG）、根级 `data/`（上传文件）、`backups/`（备份）。

> 生产模式使用 `Secure` Cookie。直接访问 HTTP 端口仅用于部署验证；正式使用应由外部反向代理提供 HTTPS，并在 `.env` 中将 `TRUST_PROXY` 设为 `true`。

### 3.2 回滚 / 备份

- 回滚：保留上一镜像标签，`docker compose up -d --force-recreate` 指定旧标签；详见 `RootDoc-Deploy.md`。
- 备份：PG 用 `pg_dump` 到 `backups/`；确保 `DATABASE_PASSWORD` 不泄露。

---

## 4. 常见故障排查

| 现象 | 可能原因 | 处理 |
|---|---|---|
| 后端启动报 `TOTP_ENCRYPTION_KEY` / `SECRET_KEY` 未设置 | `.env` 缺密钥 | 补全 4 个必填密钥后重启 |
| 前端登录后始终 401 / requireAdmin 守卫 401 | BFF 未拿到后端身份（`/auth/me` 失败） | 确认 `BACKEND_URL` 可达；查后端 `/health` |
| 前端 dev 报 `preload is not defined` | Next16+ 自定义 server + next-intl dev 期已知非致命错误 | 忽略，不影响构建 |
| `pnpm audit` CI 失败 | 生产依赖存在 moderate+ 漏洞（G1 已阻断） | 升级依赖或团队评审后加豁免；不要直接放开 `continue-on-error` |
| `X | None` 语法导入失败 | 本地 Python < 3.10 | 升级到 3.13+ |
| SQLite 相关报错（前端） | `shared/db` 冗余层与 `better-sqlite3` 依赖已全部删除（B1 收口 + 2026-08-07 SQLite 清理） | 新代码一律走后端 API + 前端 BFF 转发，前端零 SQLite |
| 后端测试连到生产库 | pytest 未加载 `.env.test` | 确保 `tests/` 配置拒绝非 test 库名 |
| **前端活动/社区内容全部加载失败、登录无响应（BFF 路由全 500），但首页 `/` 正常 200** | **tsx watch 热重载缓存损坏**（多见于大规模删代码后）。后端与数据库均正常（可直连 `http://localhost:9000/api/v1/events` 验证 200） | **冷重启前端 dev server**：`make restart-frontend`（释放 :2333 并重新 `pnpm dev`，自动探活）。无需改代码 |

---

## 5. 提交 / PR 自检速记

- 前端：`pnpm run ts-check` + `pnpm run lint:build` + `pnpm test -- --run` 全绿。
- 后端：`python -m pytest` 全绿；`mypy` / `black` / `flake8` 门禁通过。
- 新功能数据访问**只走后端**，前端仅做 BFF 转发（`src/modules/*/server/` 与 `shared/db` 均已删除，勿重建直连层）。
- 改了 API 契约：同步更新 OpenAPI（`/api/v1/**` 冻结前需评审）。

---

# 附录 A：前端工程规则（原 FrontDoc-Onboard.md 第 8 节）

> Source of truth：禁止事项、模块协作契约、ADR 编号规则、文档维护 lifecycle、编码规范、server-only 边界的唯一权威位置。
> 变更触发：新增移除依赖、模块结构调整、ADR 新增、文档结构变更、新增安全/工程发现。

## A.1 禁止事项

1. **禁止引入 react-dev-inspector**：与 Next.js 16 + Turbopack 不兼容，DOM 注入致开发模式渲染 16-24s。移除组件引用 + 从 package.json 删除 `react-dev-inspector` / `@react-dev-inspector/babel-plugin`。
2. **禁止引入 Vite 相关依赖**：Next.js + Turbopack 不兼容 Vite，引入会污染控制台 404。`vitest` 可保留（仅测试）。
3. **禁止跨模块直接 import server 代码**：业务模块间（auth ↔ community ↔ events ↔ tools ↔ notification）必须走事件总线。`admin` 聚合层例外，可调用被管理模块 `server/index.ts` 公开 API。跨模块类型引用必须用 `import type`。
4. **禁止在 types/index.ts 引入运行时依赖**：仅纯类型 + 常量，否则破坏 server-only 边界（见 ADR-010 / M11 `AuditContext` 下沉）。
5. **禁止模块间循环依赖**：类型引用使用 `import type` 确保编译后无运行时依赖。

## A.2 设计规范

所有前端开发必须严格遵守 `CS-Web-Frontend/tools/docs/FrontDoc-UID.md`（编辑式技术极简 & 悬浮胶囊导航设计规范），新增页面/组件/视觉交互逐项对照 Checklist。

## A.3 模块化开发规范

- 每个模块：`server/`（已随 B1 收口整体删除，业务走后端）+ `types/`（类型）+ `ui/`（组件）。
- 模块间通信矩阵：允许 `import from @/shared/...`、事件总线；禁止直接 import 另一模块 `server/` 或 `api/`。
- 通信决策树：① 只需类型 → `import type`；② 通用工具 → `@/shared/...`；③ B 是被 admin 管理的模块 → 直接调 `B/server/index.ts`；④ 否则 → 事件总线 `appBus` 发布，B 监听。
- 事件总线：发布 `<模块>.<动作>`（如 `topic.created`）；订阅方 `try/catch` 吞错不抛出。
- 依赖矩阵维护：新增/修改模块依赖必须同步 `FrontDoc-01-Arch.md`「2.3 直接导入依赖矩阵」（架构不变量 FF1）。

## A.4 ADR 引用规则

- 何时创建：影响多模块/引入移除关键技术依赖/改变模块通信/不可逆决策/安全相关 → 记录 ADR。
- 格式：`### ADR-XXX` + 状态/上下文/决策/替代方案/后果/可逆性/实施记录，统一记录在 `项目演变历史-0.9.1.md`「附录：前端演进路线图与迁移文档」的架构决策记录（ADR）索引章节，完整决策记录见 `项目演变历史.md`。
- 锚点规则：GitHub 风格（标题转小写 + 空格转连字符 + 去标点，中文保留）。
- 编号：连续递增（ADR-015…），废弃不回收；状态必须反映实施事实（防再犯 #2）。

## A.5 文档维护流程

- 每个系统维度有且仅有一个权威位置（Source-of-Truth 无重复规则）：禁止事项→本附录 A.1；ADR→`项目演变历史-0.9.1.md`（附录演进文档）/ `项目演变历史.md`；风险→`项目演变历史.md` R 表；依赖矩阵→`FrontDoc-01-Arch.md` 2.3；安全发现→`FrontDoc-02-Sec.md`；API 契约→`FrontDoc-01-Arch.md` Part B；环境变量→`FrontDoc-Ops.md` Part A。
- 变更同步检查清单（PR 自检模板）：
  - [ ] `pnpm run ts-check` 通过
  - [ ] 调目录结构 → `FrontDoc-01-Arch.md` Part A
  - [ ] 新增/修改 API → `FrontDoc-01-Arch.md` Part B
  - [ ] 新增管理员权限 → `FrontDoc-02-Sec.md` Part 2
  - [ ] 架构决策 → `项目演变历史-0.9.1.md` 附录 / `项目演变历史.md` 新增 ADR
  - [ ] 新增禁止事项 → 本附录 A.1
  - [ ] 新增页面/组件 → `FrontDoc-UID.md`
  - [ ] 新增环境变量 → `FrontDoc-Ops.md` Part A + `README.md` 环境变量表
  - [ ] 修 bug → 立即 grep 同模式跨模块扫描，审计结果写入 ADR「审计确认安全」清单（防再犯 #6）

## A.6 编码规范补充

- 文件命名：`kebab-case`；组件文件名与默认导出名一致；barrel 统一 `index.ts`。
- 导入顺序：① React/Next 官方 ② 第三方库 ③ shared 基础设施 ④ 其他模块（仅 `import type`）⑤ 本模块内部。
- **server-only 边界**（详见 ADR-010）：任何 import `nodemailer`/`crypto`/`fs`/`pino` 的文件首行 `import 'server-only'`，客户端组件禁止 import；barrel 导出 server-only 内容自身也需标记。`src/server.ts` 自定义服务器下 Next.js `server-only` 不生效，已用 `src/shared/server-only.ts` 本地空实现 + `tsconfig.json` paths + `vitest.config.ts` alias 兜底。`shared/logger.ts` 因 pino 同构性显式记录为例外（不加 server-only）。

## A.7 防再犯清单（explanation）

源自实际缺陷归纳（ADR-015/016/017、R4/R16/R17 等），修改相关代码前逐条对照：

1. **日期比较：ISO 与 SQLite `datetime()` 字典序陷阱**——`T`(0x54) > 空格(0x20) 致同日过期被判定未过期。修复统一 `datetime(col) > datetime('now')` 归一化；空串 `expiresAt` 用 `|| null` 归一化（不拦截空串会静默隐藏）；回归测试用真实写入格式。
2. **文档与实施状态脱节**——ADR 状态/R 表/里程碑为活文档，单次编辑须交叉检查，跨章节合并后 grep 验证条目唯一性。
3. **测试覆盖与缺陷暴露错位**——测试数据必须模拟真实写入路径（UI 写 ISO 就用 ISO），覆盖边界用例（当天已过期/空串/null）。
4. **server-only 边界假合规**——加 `import 'server-only'` 后须实际从客户端 import 验证报错；自定义 dev server 需本地空实现 + tsconfig + vitest 三重映射；例外须显式记录。
5. **迁移幂等性与事务安全**——`CREATE+INSERT+DROP+RENAME` 必须 `db.transaction()` 包裹；迁移检测旧 schema 特征而非"表存在就迁移"；FK 语义：审计表 `SET NULL`、业务表 `CASCADE`。
6. **跨模块同类缺陷系统排查**——修一处立即 grep 同模式扫描，审计结果写入 ADR「审计确认安全」清单。
7. **同一字段多消费方不一致**——审计字段须 grep 所有读取点，鉴权路径（越权高危）与展示路径（数据陈旧）一并覆盖。

> 元规则：① 任何"两端约定"（日期格式/文档与代码/测试与生产写入路径）必须显式校验两端一致；② 任何 bug 修复必须触发同模式 grep 扫描。

---

# 附录 B：后端工程约定（原 BackDoc-Onboard.md 精要）

> 完整架构 / 编码规范 / 业务模块见 `CS-Web-Backend/docs/` 下的 `BackDoc-01-Arch.md` / `BackDoc-Conv.md` / `BackDoc-Mods.md`。此处仅保留"必须守住的不变量"与"加一个 API 资源"配方。

## B.1 必须守住的不变量（速览）

1. **分层单向**：api → service → repository → model，禁止反向/跨层。
2. **DB 会话**：路由 `Depends(get_db)`，路由外 `async with get_session()`；均不自动提交——repo 只 flush，service 显式 commit。
3. **时间列**：ORM 一律 `DateTime(timezone=True)`；取当前时间用 `now_utc()`（`app/core/timezone.py`），禁止 `datetime.now()`/`utcnow()`。
4. **出参时间**：带 datetime 的响应模型继承 `TZModel`（自动转本地时区）。
5. **权限**：依赖注入 `Depends(require_permission("res","act"))`，不用装饰器。
6. **业务异常**：抛 `BaseAppException` 子类，不在路由吞异常。
7. **中间件短路**：`return JSONResponse(...)`，不 `raise HTTPException`。
8. **日志**：`get_logger`，不 `print`、不直接配 handler。
9. **Redis 可降级**：限流/缓存把 Redis 当增强项，非强依赖。
10. **迁移铁律**：全环境仅 Alembic；禁止 `Base.metadata.create_all`；建库用 `DB_AUTO_CREATE_DATABASE`。
11. **时区**：核心存 UTC，展示走 `settings.TIMEZONE`；必须装 `tzdata`。
12. **新增 datetime 响应模型必须继承 `TZModel`**，不手写 per-field serializer。

## B.2 加一个 API 资源（配方）

完整配方在 `CS-Web-Backend/AGENTS.md`「加一个 API 资源」。要点：

1. `models/<x>.py` → 登记到 `models/__init__.py`
2. `schemas/<x>.py`（Pydantic v2；带 datetime 继承 `TZModel`）
3. `repositories/<x>_repo.py`（继承 `BaseRepository`）
4. `services/<x>_service.py`（组合 repo）
5. `api/v1/<x>.py` → 注册到 `api/v1/__init__.py`
6. Alembic 建表/迁移
7. `tools/tests/` 镜像补测试
8. 业务模块在 `BackDoc-Mods.md` 对应节登记（或新建 `tools/docs/modules/<name>.md` 并登记到 `tools/docs/README.md`）

> **中心注册点**（必须登记，否则不生效）：ORM 模型、业务异常、中间件、配置项、API router、启动/关闭任务（`@register_startup`/`@register_shutdown`）、测试子包 `__init__.py`。

## B.3 后端常见坑

| 坑 | 说明 |
|---|---|
| 任务/路由不生效 | 99% 忘记在中心注册点登记（`models/__init__.py`、`v1/__init__.py`、`lifecycle/__init__.py`） |
| 启动失败"时区非法" | 缺 `tzdata`（尤其 Windows/alpine），确保已装 |
| 时间多了/少了 8 小时 | 用了 naive `datetime`；统一 `now_utc()` + `TZModel` |
| 测试连不上库 | `.env.test` 需 `DATABASE_URL` 指向库名含 `test` 的库（`conftest.py` 校验） |
| 改了配置但无效 | 没同步 `.env.example`，或字段名与 `Settings` 不一致 |
| `alembic check` 报 drift | 别改历史迁移文件，新增增量迁移 |
