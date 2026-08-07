# FztbuCS-Project

> 计算机协会官网平台 · 前后端分离 + 根级编排

> **当前真实进度（2026-08-07）**：版本 **0.9.7 → 1.0.0 准备期**。后端 FastAPI + PostgreSQL 已为唯一业务数据源；前端为 BFF 薄转发层。前端 `src/modules/*/server/`（9 模块直连业务层）与 `src/shared/db`（SQLite 双引擎）、`src/shared/security/audit.ts`（本地审计）**已于 2026-08-06 整体删除并验证**（经全仓库引用扫描确认为孤儿死代码，业务早已 `src/app/api/**` 薄转发后端），Blocker **B1 已闭环**；前端审计改走后端 `POST /api/v1/audit/logs`。2026-08-07 进一步清理 SQLite 残留：删除遗留脚本（`create-user`/`seed-exam-data`/`migrate-sqlite-to-pg`）与 `better-sqlite3` 依赖，E2E 改经后端 API 建号。完整待办见 `项目待办事项.md`。

本仓库为**编排/部署仓库（monorepo 外层）**，通过 Git Submodule 收敛前后端两个独立源码仓库，并在根级统一管理全栈容器编排与启动命令。

## 目录结构

```text
FztbuCS-Project/
├── CS-Web-Backend/        # submodule：FastAPI 后端（REST API + PostgreSQL + Alembic）
├── CS-Web-Frontend/       # submodule：Next.js 前端（UI + BFF 薄转发）
├── deploy/caddy/          # Caddy 反向代理配置（自动 HTTPS）
├── docker-compose.yml     # 根级全栈编排（db + backend + frontend + caddy）
├── .env.example           # 全栈环境变量模板
├── Makefile               # 统一命令入口
└── docs/                  # 根级文档（编排/部署/通用规范，入口见 docs/README.md）
```

## 快速开始

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
```

### 容器化部署（全栈一键起）

```bash
make setup        # 首次：cp .env.example .env，并填写全部密钥
# 编辑 .env：DATABASE_PASSWORD / SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET
# 有域名：把 deploy/caddy/Caddyfile 中的 cs.yourdomain.com 改为你的域名
make up           # docker compose up -d --build（db+backend+frontend+caddy）
make ps           # 查看状态
make logs         # 跟踪日志
make down         # 停止
```

- 无域名：去掉 compose 里的 `caddy` 服务，直接访问 `http://<host>:2333`。
- 后端 Swagger：`http://<host>:9000/docs`（容器内 `expose: 8000`，不映射公网端口，仅内网）。

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
| `TRUST_PROXY` | 是否信任反向代理头（Caddy 后须 true） | 生产 ✅ |

## 架构

```text
浏览器 ──HTTPS──> Caddy(:80/:443) ──> cs-website(Next.js BFF :2333)
                                          │ BACKEND_URL=http://backend:8000
                                          ▼
                                     backend(FastAPI :8000) ──> db(PostgreSQL:5432)
```

- 前端 BFF 通过内部网络 `cs-net` 直连后端，无需暴露后端公网端口。
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

前后端专项文档保留在各 submodule：后端 `CS-Web-Backend/docs/`、前端 `CS-Web-Frontend/tools/docs/`。
