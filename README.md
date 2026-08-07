# FztbuCS-Project

> 计算机协会官网平台 · 前后端分离 + 根级编排

> **当前真实进度（2026-08-07）**：版本 **0.9.8 → 1.0.0 准备期**。后端 FastAPI + PostgreSQL 已为唯一业务数据源；前端为 BFF 薄转发层。前端 `src/modules/*/server/`（9 模块直连业务层）与 `src/shared/db`（SQLite 双引擎）、`src/shared/security/audit.ts`（本地审计）**已于 2026-08-06 整体删除并验证**（经全仓库引用扫描确认为孤儿死代码，业务早已 `src/app/api/**` 薄转发后端），Blocker **B1 已闭环**；前端审计改走后端 `POST /api/v1/audit/logs`。2026-08-07 进一步清理 SQLite 残留：删除遗留脚本（`create-user`/`seed-exam-data`/`migrate-sqlite-to-pg`）与 `better-sqlite3` 依赖，E2E 改经后端 API 建号。完整待办见 `docs/项目待办事项.md`。

本仓库为**编排/部署仓库（monorepo 外层）**，通过 Git Submodule 收敛前后端两个独立源码仓库，并在根级统一管理全栈容器编排与启动命令。

> **新手先看下方「快速开始」章节**：5 分钟上手 + 端口/版本号/关键 env 等高频事实速查（单一事实源，集中维护，其余文档引用不重复散写）。

## 目录结构

```text
FztbuCS-Project/
├── CS-Web-Backend/        # submodule：FastAPI 后端（REST API + PostgreSQL + Alembic）
├── CS-Web-Frontend/       # submodule：Next.js 前端（UI + BFF 薄转发）
├── docker-compose.yml     # 根级全栈编排（db + backend + redis + worker + frontend）
├── .env.example           # 全栈环境变量模板
├── Makefile               # 统一命令入口
└── docs/                  # 根级文档（编排/部署/通用规范，入口见 docs/README.md）
```

## 快速开始

> 本仓库高频事实（端口、版本号、关键 env、路径约定）以本「快速开始」章节为**单一事实源**：变动只改此处，其他文档引用即可，不再重复散写。工程原则见 [`docs/RootDoc-EngConv.md`](docs/RootDoc-EngConv.md)；完整部署见 [`docs/RootDoc-Deploy.md`](docs/RootDoc-Deploy.md)。

### 首次克隆（含 submodule）

```bash
git clone <root-repo-url> FztbuCS-Project
cd FztbuCS-Project
git submodule update --init --recursive
```

### 本地开发（并行起前后端）

```bash
make setup        # 首次：生成 .env（如已用容器，可不做此步）
make dev-up       # 并行起后端(:9000 热重载) + 前端(:2333 dev)
# 或分别：make dev-backend / make dev-frontend
# 停止：make dev-down
```

启动后：

| 服务 | 本地访问地址 | 说明 |
|---|---|---|
| 前端（Next.js） | http://localhost:2333 | 业务 UI |
| 后端 Swagger | http://localhost:9000/docs | 仅本地 `make dev-up` 暴露 |
| 前端 BFF 转发目标 | http://localhost:9000 | 见前端 `.env` 的 `BACKEND_URL` |

### 容器化部署（全栈一键起）

```bash
make setup        # 首次：cp .env.example .env，并填写全部密钥
# 编辑 .env：DATABASE_PASSWORD / SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET
# 前端默认绑定 127.0.0.1:2333；后续由部署者自行配置 HTTPS 反向代理
make up           # docker compose up -d --build（db+backend+redis+worker+frontend）
make ps           # 查看状态
make logs         # 跟踪日志
make down         # 停止
```

- 前端：由 Compose 绑定到 `127.0.0.1:2333`，后续外部反向代理指向该地址。
- 临时直连测试可将端口映射改为 `0.0.0.0:2333:2333`，正式环境不建议直接暴露。
- 后端 Swagger：`http://<host>:9000/docs`。

### 高频事实速查表（单一事实源）

**端口约定**

| 场景 | 端口 | 依据 |
|---|---|---|
| **容器编排内**（Docker 服务间） | 后端 **8000** | `docker-compose.yml` 的 `backend.expose: "8000"`；前端容器 `BACKEND_URL=http://backend:8000` |
| **本地开发**（宿主机直连） | 后端 **9000** | 根 `Makefile` 的 `BACKEND_PORT := 9000` → `run.py --env 1 --port 9000` |
| 前端 | 2333 | `Makefile` / `.env` 固定 |
| 外部反向代理（可选） | 80/443 | 由部署者自行配置，转发到 `127.0.0.1:2333` |

- `run.py` 默认端口为 `8000`；**本地 9000 来自 `Makefile` 的 `--port 9000` 覆盖**，非默认值。
- 两者指向**同一后端服务，仅场景不同**——不存在"该用哪个"的问题。文档中若看到 8000/9000 混写，均遵循此表。

**版本号单一源**

| 端 | 版本号字段 | 文件位置 |
|---|---|---|
| 前端 | `package.json` → `version` | `CS-Web-Frontend/package.json` |
| 后端 | `__version__` | `CS-Web-Backend/app/__init__.py` |
| 发布说明锚点 | `CHANGELOG.md` | `CS-Web-Frontend/CHANGELOG.md` |

- 改版本号**三处同步**：前端 `package.json` + 后端 `app/__init__.py.__version__` + 前端 `CHANGELOG.md` 锚点。
- 当前语义版本线：`0.9.x`（尚未进入 1.0.0）。

**架构一句话**

- 前端是**纯 BFF 薄转发**：`src/app/api/**/route.ts` 仅转发到后端 `/api/v1/**`，无本地业务数据库。
- 后端是**唯一业务/数据 owner**：FastAPI + PostgreSQL（Alembic 管理 schema），JWT 双 token 认证。

### 常见问答（FAQ）

**Q：后端到底 8000 还是 9000？**
A：容器内 8000，本地 9000，见上表。两者都对。

**Q：改了端口为什么联调不通？**
A：本地用 `make dev-up`（9000）；直接 `python run.py` 默认是 8000。确认用的是 Makefile 还是裸跑。

**Q：版本号在哪改？**
A：三处同步（见上表），缺一不可，否则 CI/CHANGELOG 对不上。

**Q：前端能直连数据库吗？**
A：不能。前端仅 BFF 转发，业务数据全在后端 PG。

### 详细文档导航

| 我想了解 | 看这里 |
|---|---|
| 完整部署 / 回滚 / 备份 | [`docs/RootDoc-Deploy.md`](docs/RootDoc-Deploy.md) |
| 工程原则 / 命名 / 红线 | [`docs/RootDoc-EngConv.md`](docs/RootDoc-EngConv.md) |
| 前端架构 / 目录设计 | [`docs/RootDoc-FEArch.md`](docs/RootDoc-FEArch.md) |
| 入职流程 / 环境搭建 | [`docs/Onboarding.md`](docs/Onboarding.md) |
| 数据迁移评估 | [`docs/RootDoc-MigEval.md`](docs/RootDoc-MigEval.md) |
| 历史变更 | [`docs/项目演变历史.md`](docs/项目演变历史.md) |

## 环境变量

见 `.env.example`，关键项：

| 变量 | 用途 | 必填 |
|------|------|------|
| `DATABASE_PASSWORD` | PostgreSQL 密码 | ✅ |
| `SECRET_KEY` | 后端 JWT 签名密钥（≥32B） | ✅ |
| `TOTP_ENCRYPTION_KEY` | 后端 2FA 加密密钥（≥32B） | ✅ |
| `AUTH_SESSION_SECRET` | 前端 Session 密钥（≥32B） | ✅ |
| `ALLOWED_ORIGINS` | 前后端 CORS / Origin 白名单 | 生产 ✅ |
| `NEXT_PUBLIC_SITE_URL` | 站点 URL | 生产 ✅ |
| `TRUST_PROXY` | 是否信任反向代理头（默认 `false`；外部反代配置后设为 `true`） | 按部署方式 |

## 架构

```text
浏览器 ──> 外部反向代理（可选）──> 127.0.0.1:2333 cs-website(Next.js BFF)
                                          │ BACKEND_URL=http://backend:8000
                                          ▼
                                     backend(FastAPI :8000) ──> db(PostgreSQL:5432)
```

- 前端 BFF 通过内部网络 `cs-net` 直连后端，无需暴露后端公网端口。
- 生产模式使用安全 Cookie，正式访问应由外部反向代理提供 HTTPS；`http://127.0.0.1:2333` 主要用于部署验证。
- 前端为纯 BFF/展示层，**不持有业务数据**；全部业务数据由后端 PostgreSQL 承载（前端已 100% 移除 SQLite 相关代码、脚本与依赖）。
- 数据卷：`pgdata`（PG）、根级 `data/`（上传文件）。

## Submodule 说明

```bash
# 更新所有子仓库到各自最新提交
git submodule update --remote --merge

# 子仓库内的改动请进入各自目录操作并独立提交/推送
cd CS-Web-Backend && git pull && git push
```

## 文档地图

跨项目/编排层文档统一在根 `docs/`（单一权威、零漂移）：

| 文档 | 说明 |
|---|---|
| [docs/README.md](docs/README.md) | 根级文档索引 + 子仓库文档入口 |
| [docs/RootDoc-FEArch.md](docs/RootDoc-FEArch.md) | 前端通用目录/架构准则（框架无关） |
| [docs/RootDoc-EngConv.md](docs/RootDoc-EngConv.md) | 通用工程规范（两端共用） |
| [docs/RootDoc-Deploy.md](docs/RootDoc-Deploy.md) | 全栈部署 / 运维 |
| [docs/RootDoc-MigEval.md](docs/RootDoc-MigEval.md) | 迁移可行性 + 多数据库支持评估报告（含执行记录；原 `docs/data-migration/` 已并入本文件） |
| [docs/Onboarding.md](docs/Onboarding.md) | 入职手册 / 环境搭建 |
| [docs/项目演变历史.md](docs/项目演变历史.md) | 历史变更记录（按版本，索引） |
| [docs/项目待办事项.md](docs/项目待办事项.md) | 待办清单 |

前后端专项文档保留在各 submodule：后端 `CS-Web-Backend/docs/`、前端 `CS-Web-Frontend/tools/docs/`。
