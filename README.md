# FztbuCS-Project

> 计算机协会官网平台 · 前后端分离 + 根级编排

> **当前真实进度（2026-08-08）**：版本 **0.9.8 → 1.0.0 准备期**。后端 FastAPI + PostgreSQL 为唯一业务数据源；前端为纯 BFF 薄转发层（`src/modules/*/server/`、`src/shared/db`、本地审计等直连层已整体删除，B1 闭环；审计走后端 `POST /api/v1/audit/logs`，E2E 经后端 API 建号）。完整待办见 `docs/项目待办事项.md`。

本仓库为**编排/部署仓库（monorepo 外层）**，通过 Git 子仓库(submodule) 收敛前后端两个独立源码仓库，并在根级统一管理全栈容器编排与启动命令。

> **新手先看下方「快速开始」章节**：5 分钟上手 + 端口/版本号/关键 env 等高频事实速查（单一事实源，集中维护，其余文档引用不重复散写）。

## 目录结构

```text
FztbuCS-Project/
├── CS-Web-Backend/        # 子仓库(submodule)：FastAPI 后端（REST API + PostgreSQL + Alembic）
├── CS-Web-Frontend/       # 子仓库(submodule)：Next.js 前端（UI + BFF 薄转发）
├── docker-compose.yml     # 根级全栈编排（db + backend + redis + worker + frontend）
├── .env.example           # 全栈环境变量模板
├── Makefile               # 统一命令入口
└── docs/                  # 根级文档（编排/部署/通用规范，入口见 docs/README.md）
```

## 核心特性

> 以下能力在 **0.9.8** 中已具备；认证相关接口统一前缀 `/api/v1`，完整契约见后端 Swagger 与仓库根 `openapi.baseline.json`。

- **统一工作台（Workbench）**：个人数据聚合视图，集中呈现 GitHub 贡献热力图、API 调用统计、番茄钟专注记录、LLM 用量等（端点见「使用示例 · 工作台」）。
- **Auxilio 学习助手**：SSE 流式对话，支持会话管理与 Skills 工具调用；前端「助手对话」入口即对应其接口。
- **GitHub 贡献热力图**：同步并渲染用户 GitHub 贡献日历（`GET /api/v1/workbench/contributions/github`）。
- **API 调用统计**：按用户/端点聚合接口调用量与趋势（`GET /api/v1/workbench/stats/api-usage`）。
- **番茄钟专注记录**：记录专注时段并统计分布（`POST /api/v1/workbench/focus-sessions`、`GET /api/v1/workbench/stats/pomodoro`）。
- **双 Token 认证与 2FA**：邮箱验证码注册/登录、JWT 双 token、可选 TOTP 二次验证（见「使用示例 · 认证流程」）。
- **业务域**：`/users`、`/rbac`、`/events`、`/community`、`/announcements`、`/notifications`、`/join`、`/tools`、`/audit` 等，详见后端 Swagger。

## 快速开始

> 本仓库高频事实（端口、版本号、关键 env、路径约定）以本「快速开始」章节为**单一事实源**：变动只改此处，其他文档引用即可，不再重复散写。工程原则见 [`docs/RootDoc-EngConv.md`](docs/RootDoc-EngConv.md)；完整部署见 [`docs/RootDoc-Deploy.md`](docs/RootDoc-Deploy.md)。

### 首次克隆（含子仓库(submodule)）

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
| 后端 | `pyproject.toml` → `version` | `CS-Web-Backend/pyproject.toml` |
| 后端 | `__version__` | `CS-Web-Backend/app/__init__.py` |
| 后端 | `uv.lock` 依赖锁定版本 | `CS-Web-Backend/uv.lock` |

- 改版本号**四处同步**：前端 `package.json` + 后端 `pyproject.toml` + 后端 `app/__init__.py.__version__` + 后端 `uv.lock`（依赖锁定随版本一起更新）。
- 发布说明（版本锚点）：[`CHANGELOG.md`](CHANGELOG.md)，按 Keep a Changelog 维护，记录各版本显著变更（0.9.8 含工作台 / Auxilio 等新增能力）。
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
A：四处同步（见上表），缺一不可，否则 CI/CHANGELOG 对不上。

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
| 发布说明（版本锚点） | [`CHANGELOG.md`](CHANGELOG.md) |

## 安装

> 最小可运行前置：Git、Python 3.13+、Node 22+ + pnpm 9；生产 / 容器部署另需 Docker + Compose（PostgreSQL 16 由容器自动拉起）。
> 推荐先按上方「快速开始」用 `make` 一键起；本节给出**分步手动安装**与 env 填写细节，便于排错与精细化控制。

### 环境要求

| 工具 | 版本 | 用途 |
|---|---|---|
| Git | 较新版本 | 拉取含子仓库(submodule) 的仓库 |
| Python | **3.13+**（与 `CS-Web-Backend/pyproject.toml` 一致；3.9 会因 `X \| None` 语法失败） | 后端运行 / 测试 |
| Node.js | **22+**（与 `CS-Web-Frontend/package.json` 的 `engines.node: ">=22"` 一致） | 前端运行 / 构建 |
| pnpm | 9.0.0 | 前端包管理（CI 锁定此版本，`package.json` 已禁 npm/yarn） |
| Docker + Compose | 新版 | 容器化全栈部署（PG 16 自动起） |

### 方式一：本地开发（子仓库(submodule)分别安装）

后端：

```bash
cd CS-Web-Backend
python3.13 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"                 # 运行时 + pytest 全家桶
cp .env.example .env                      # 填写下方 4 个必填密钥
```

前端：

```bash
cd CS-Web-Frontend
pnpm install                              # 强制 pnpm（preinstall 阶段拦截 npm/yarn）
cp .env.example .env                      # 至少填 AUTH_SESSION_SECRET / ALLOWED_ORIGINS / NEXT_PUBLIC_SITE_URL
```

起服务（任选其一）：

```bash
# 根目录一键并行（tmux 托管：后端 :9000 + 前端 :2333）
make setup && make dev-up

# 或分别起
make dev-backend      # 仅后端（热重载）
make dev-frontend     # 仅前端（dev）
```

### 方式二：容器化一键部署

```bash
make setup            # cp .env.example .env
# 编辑 .env，填齐 4 个必填密钥（见下）
make up               # docker compose up -d --build（db+backend+redis+worker+frontend）
make ps               # 查看状态
make logs             # 跟踪日志
```

### 生成必填密钥

`.env` 中以下 4 项**必须**随机生成（≥32 字节），不要留 `GENERATE_*` / `CHANGE_ME` 占位符，否则后端启动即报错：

```bash
openssl rand -hex 32   # 分别对 SECRET_KEY / TOTP_ENCRYPTION_KEY / AUTH_SESSION_SECRET 执行
```

| 变量 | 用途 | 必填 |
|---|---|---|
| `DATABASE_PASSWORD` | PostgreSQL 密码 | ✅ |
| `SECRET_KEY` | 后端 JWT 签名密钥（≥32B） | ✅ |
| `TOTP_ENCRYPTION_KEY` | 后端 2FA 加密密钥（≥32B） | ✅ |
| `AUTH_SESSION_SECRET` | 前端 Session 密钥（≥32B） | ✅ |

> 其余可选变量（SMTP / GitHub OAuth / REDIS_URL / MULTI_INSTANCE / QUEUE_ENABLED 等）见 `.env.example` 内联注释，按需开启。

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

## 使用示例

> 后端 REST API 统一前缀 `/api/v1`，传输使用 **camelCase**。本地开发后端在 `http://localhost:9000`，容器内为 `backend:8000`（前端 BFF 经内部网络直连，不暴露公网）。
> 完整契约见后端 Swagger：`http://localhost:9000/docs`，以及仓库根 `openapi.baseline.json`（已冻结，CI 比对门禁）。

### 认证流程（curl）

**1) 发送邮箱验证码**（注册前置）：

```bash
curl -X POST http://localhost:9000/api/v1/auth/send-code \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com"}'
# => {"ok":true,"message":"验证码已发送"}
```

**2) 注册**（邮箱 + 密码 + 验证码，自动登录返回双 token）：

```bash
curl -X POST http://localhost:9000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Str0ng#Passw0rd","code":"123456"}'
# => {"accessToken":"...","refreshToken":"...","tokenType":"bearer","expiresIn":900,"requires2fa":false}
```

**3) 登录**（JSON，用户名 + 密码），拿双 token：

```bash
curl -X POST http://localhost:9000/api/v1/auth/login-json \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"Str0ng#Passw0rd"}'
# => {"accessToken":"...","refreshToken":"...","tokenType":"bearer","expiresIn":900}
```

**4) 携带 token 获取当前用户**：

```bash
curl http://localhost:9000/api/v1/auth/me \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
# => {"user":{"id":1,"email":"alice@example.com","username":"alice",...},"roles":["user"],"twoFactorEnabled":false}
```

> token 轮换：`POST /api/v1/auth/refresh` 传 `{"refreshToken":"..."}` 换取新双 token；登出 `POST /api/v1/auth/logout`（带 `Authorization` 头，可选 body 带 `refreshToken`）。
> 其他业务域均挂在 `/api/v1` 下：`/users`、`/rbac`、`/events`、`/community`、`/announcements`、`/notifications`、`/join`、`/tools`、`/audit` 等，详见 Swagger。

### 工作台（Workbench）示例

工作台聚合个人数据，接口均挂在 `/api/v1/workbench` 下，需携带 `Authorization: Bearer <ACCESS_TOKEN>`（认证流程见上）。

**API 调用统计**：

```bash
curl http://localhost:9000/api/v1/workbench/stats/api-usage \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
# => {"userId":1,"totalCalls":1280,"byEndpoint":[{"path":"/api/v1/...","count":42}],"periodDays":30}
```

**GitHub 贡献热力图**：

```bash
curl http://localhost:9000/api/v1/workbench/contributions/github \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
# => {"userId":1,"username":"alice","contributions":[{"date":"2026-08-01","count":5}, ...]}
```

**番茄钟专注记录**（写入一条专注时段）：

```bash
curl -X POST http://localhost:9000/api/v1/workbench/focus-sessions \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"startedAt":"2026-08-08T09:00:00Z","endedAt":"2026-08-08T09:25:00Z","task":"阅读文档"}'
# => {"id":42,"durationMin":25,"createdAt":"2026-08-08T09:25:00Z"}
```

> 其余工作台端点：`GET /api/v1/workbench/stats/pomodoro`（专注统计）、`GET /api/v1/workbench/stats/llm-usage`（LLM 用量）、`GET /api/v1/workbench/llm-config` 与 `PUT /api/v1/workbench/llm-config`（LLM 配置）。响应统一 camelCase。

### Auxilio 学习助手（SSE 流式对话）

Auxilio 提供流式对话能力，接口挂在 `/api/v1/auxilio` 下。`POST /api/v1/auxilio/chat` 以 SSE（`text/event-stream`）返回增量 `delta` 事件，支持 OpenAI / Anthropic 双协议与 Skills 工具调用。

**后端直连（curl，SSE）**：

```bash
curl -N -X POST http://localhost:9000/api/v1/auxilio/chat \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"解释一下 RBAC 的最小权限原则"}]}'
# => event: delta   {"type":"delta","text":"RBAC..."}
#    event: usage   {"type":"usage","promptTokens":..,"completionTokens":..}
#    event: done    {"type":"done","title":"RBAC 最小权限原则"}
```

**前端（经 BFF 转发）**：

```ts
const res = await fetch('/api/auxilio/chat', {
  method: 'POST',
  credentials: 'include',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ messages: [{ role: 'user', content: '解释 RBAC' }] }),
});
const reader = res.body!.getReader();
const decoder = new TextDecoder();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  console.log(decoder.decode(value)); // SSE 增量事件
}
```

> 会话管理：`GET /api/v1/auxilio/conversations`（会话列表）、`GET /api/v1/auxilio/conversations/{conversationId}/messages`（消息历史）。前端「助手对话」入口即对应上述接口。

### 前端（BFF 薄转发）

前端不持有业务数据，所有读写都经 `src/app/api/**/route.ts` 转发到后端。新增一个 BFF 路由的标准写法（出自 `src/app/api/tools/component-registry/route.ts`）：

```ts
// src/app/api/<module>/<resource>/route.ts
import { normalizeError, proxyBackend } from '@/shared/backend-client';
import { NextResponse } from 'next/server';

export async function GET(req: Request) {
  const proxy = await proxyBackend(req, { path: '/<module>/<resource>' });
  if (proxy.status !== 200) {
    return NextResponse.json(normalizeError(proxy.body, '获取失败'), { status: proxy.status });
  }
  return NextResponse.json({ data: proxy.body });
}
```

浏览器侧调用前端同源的 `/api/...` 路由（由 BFF 转发到后端，携带凭证走 Cookie/Session）：

```ts
const res = await fetch('/api/tools/component-registry', { credentials: 'include' });
const { data } = await res.json();
```

> 业务数据一律在后端 PostgreSQL；前端**禁止**重建本地数据库直连层（`src/modules/*/server/`、`src/shared/db` 已删除，勿复活）。

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

## 子仓库说明(submodule)

```bash
# 更新所有子仓库到各自最新提交
git submodule update --remote --merge

# 子仓库内的改动请进入各自目录操作并独立提交/推送
cd CS-Web-Backend && git pull && git push
```

## 贡献指南

> 协作红线与完整规范见 [`docs/RootDoc-EngConv.md`](docs/RootDoc-EngConv.md) 与 [`docs/Onboarding.md`](docs/Onboarding.md)。以下是 PR 前必须完成的最小清单。

### 分支与 PR 流程

1. 从 `main`（或对应 release 分支）切出功能分支：`feat/xxx`、`fix/xxx`。
2. 子仓库改动进入各自目录独立提交 / 推送（本仓库为子仓库(submodule) 编排层，详见「子仓库说明(submodule)」）。
3. 提交前在**本端**跑通自检（见下）再提 PR；**不要**依赖助手自动 commit/push。
4. 改了 API 契约须同步 OpenAPI：根目录 `make contract-baseline`（评审通过后写基线）或 `make contract-check`（CI 门禁，差异即失败）。

### 提交信息格式

遵循 `<type>(<scope>): <subject>`，type ∈ `feat / fix / refactor / chore / docs / test`：

```text
feat(auth): 支持邮箱登录主路径
fix(community): 修复分页越界导致的 500
docs: 补充 README 使用示例
```

### 代码风格与质量红线

- **后端**：`black`（target py313）+ `flake8` + `mypy` 门禁；分层单向 `api → service → repository → model`；时间统一 `now_utc()` + `TZModel`；业务异常抛 `BaseAppException` 子类，路由内不吞异常。
- **前端**：`pnpm run ts-check`（tsc）+ `pnpm run lint:build`（eslint）+ `pnpm test -- --run`（vitest）全绿；组件 `PascalCase`、文件 `kebab-case`、barrel 统一 `index.ts`；`server-only` 边界（含 `nodemailer`/`crypto`/`fs`/`pino` 的文件首行 `import 'server-only'`）。
- **通用**：单文件 ≤ ~300 行（py）/ ~500 行（组件）；圈复杂度 ≤ 10；同一逻辑出现 3 次才抽公共函数；禁止硬编码密钥 / 主机端口 / 魔法值；新增配置必须同步 `.env.example`。

### 测试要求

- 后端：`cd CS-Web-Backend && python -m pytest`（需 PostgreSQL 测试库，`conftest.py` 拒绝非 `test` 库名）。
- 前端：`pnpm test -- --run` + `pnpm run ts-check` + `pnpm run lint:build` 全绿。
- 测试数据必须模拟真实写入路径，覆盖正向 / 反向 / 边界三类。

### PR 自检清单

- [ ] 提交信息符合 `<type>(<scope>):` 格式
- [ ] 后端 `pytest` / 前端 `ts-check` + `lint:build` + `test` 全绿
- [ ] 新增 / 修改 API 已同步 OpenAPI（必要时 `make contract-baseline`）
- [ ] 新增配置项已同步 `.env.example`
- [ ] 仅改动完成任务所需最小范围，未顺手重构无关代码
- [ ] 新功能数据访问只走后端，前端仅 BFF 转发（未重建 `src/modules/*/server/` 或 `shared/db`）
- [ ] 文档变更已同步对应权威位置（见 Onboarding 附录 A.5 变更同步检查清单）

## 文档地图

**唯一文档地图：**[`docs/README.md`](docs/README.md)（根级文档索引 + 各子仓库文档入口，新增/合并/删除文档须先登记于此）。

- 跨项目/编排层文档统一在根 `docs/`（单一权威、零漂移）：`RootDoc-FEArch`（前端通用准则）、`RootDoc-EngConv`（通用工程规范）、`RootDoc-Deploy`（全栈部署/运维）、`RootDoc-MigEval`（迁移评估）、`Onboarding`（新开发者/管理员上手）、`api-reference`（API 参考，由 openapi 契约自动生成）、`CHANGELOG`（发布说明）、`项目演变历史`（历史变更）、`项目待办事项`——完整清单与说明见文档地图。
- 前后端专项文档保留在各子仓库(submodule)：后端 `CS-Web-Backend/tools/docs/`（入口 `README.md`）、前端 `CS-Web-Frontend/tools/docs/`（入口 `README.md`）。
