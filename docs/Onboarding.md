# Onboarding 教程（新人第一天：从 0 到提第一个 PR）

> 更新人：3yearsZ
> 更新日：2026-08-20
> 版本：1.0.1 · 七夕（版本基线对齐 1.0.1；子模块指针 cfa270a / 884f68a / ceb1f9b）
> Diátaxis：T（Tutorial · 学习导向 · 新人第一天完整路径；完成本教程 = 本地跑通 + 测试全绿 + 工作台体验 + 提第一个 PR）
> 适用读者：第一次接触本项目的全栈/前端/后端/移动端开发者、首次部署的管理员、需要快速重建开发环境的贡献者
> 学习时长：约 60 分钟（不含依赖下载时间）

> **SSOT 分工声明**：本教程是**学习路径的唯一权威**（按步即成功，为新人而写）。目标导向的具体操作（单场景 How-to）见 [RootDoc-Deploy.md](RootDoc-Deploy.md)；实现级约束（MUST/MUST NOT）见 [RootDoc-EngConv.md](RootDoc-EngConv.md)、各子仓 `-02-Sec.md` / `-03-Conv.md`；架构决策动机见各 `-01-Arch.md`。本教程不与它们冲突，交叉引用仅作"深入阅读"指针。
>
> **前置红线（在开始第 1 步前 MUST 确认）**：
> 1. 本机 Python ≥ 3.13、Node.js ≥ 22、pnpm = 9.x、Docker + Compose 可用；Python 3.12 及以下会因 `X | None` 语法在导入阶段直接失败。
> 2. 可用磁盘 ≥ 15GB（容器镜像 + 依赖安装 + PG 数据卷 + 前端 node_modules）。
> 3. 可访问 GitHub（含子模块拉取）；国内网络建议配置 npm/pip/uv 镜像。
> 4. 本机 8000 / 9000 / 2333 / 5432 四个端口空闲；被占用时本教程步骤 3 会显式告知如何处理。

> **你将学到什么（按顺序完成以下里程碑）**：
> 1. ✅ 拉取仓库 + 子模块初始化（10 min）
> 2. ✅ 前后端分别安装依赖 + 填写本地环境变量（15 min）
> 3. ✅ 一键本地并行启动：前端 2333 + 后端 9000 + PG 5432（5 min）
> 4. ✅ 完成三项跑通验证：注册/登录 /profile 完整 + /auth/me 200 + /health 200（10 min）
> 5. ✅ 跑测试 + Lint：后端 pytest 全绿、前端 ts-check + lint:build + test 全绿（15 min）
> 6. ✅ 体验工作台 /tools（热力图 + 学习助手 Auxilio）（5 min）
> 7. ✅ 提交第一个 PR 的自检清单（5 min）

---

## 第 0 步：确认环境（5 min · 在任何代码命令之前）

本教程**每一步都有明确的成功验证标志**；如果某一步标志未出现，**不要继续下一步**，先翻到 §8 常见故障排查定位。

### 0.1 工具链版本验证（MUST 全部通过再继续）

```bash
# 在任意目录执行以下 6 条；全部输出版本号且满足版本约束即通过
git --version            # 任意新版本均可
python3 --version        # 期望输出：Python 3.13.x （3.12.x 及以下不接受）
node --version           # 期望输出：v22.x  （v21 及以下不接受）
pnpm --version           # 期望输出：9.x   （8.x 或 10.x CI 不兼容）
docker --version         # 任意带 compose 的新版本
docker compose version   # compose v2 插件形式（非 docker-compose 连字符）
```

**成功标志**：6 条命令全部打印版本，无 `command not found`；Python/Node 满足最低版本。

**未通过的处理**：
- Python：`brew install python@3.13`（macOS）或从 python.org 下载；安装后用 `python3.13 --version` 确认。
- Node.js：推荐 `nvm install 22 && nvm use 22`；或 `brew install node@22`。
- pnpm：`corepack enable && corepack prepare pnpm@9.15.0 --activate` 或 `npm i -g pnpm@9`。
- Docker：从 docker.com 装 Docker Desktop（自带 compose v2）。

### 0.2 端口空闲验证

```bash
# macOS/Linux；4 条全部无输出即空闲
lsof -i :8000 -i :9000 -i :2333 -i :5432 || true
```

**成功标志**：空输出（或仅 `COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME` 表头、后续无进程行）。

**未通过的处理**：记录占用 PID，用 `kill <PID>` 释放；或阅读 §8.1「端口冲突」改用替代端口。

---

## 第 1 步：拉取仓库 + 子模块初始化（10 min）

### 1.1 Clone 根仓

```bash
# 你本地存放项目的父目录；例如 ~/Code
cd <your-workspace-parent>
git clone <your-fork-or-upstream-url> FztbuCS-Project
cd FztbuCS-Project
```

### 1.2 初始化三个子模块

```bash
# 在根目录执行；首次会下载 CS-Web-Backend、CS-Web-Frontend、CS-Mobile
git submodule update --init --recursive
```

**SHOULD** 执行后确认三个子目录均非空：

```bash
ls CS-Web-Backend/app/main.py  CS-Web-Frontend/package.json  CS-Mobile/package.json
# 成功标志：3 条路径均存在（即无 "No such file or directory"）
```

### 1.3 （可选但推荐）配置用户信息

```bash
git config user.name  "<Your Name>"
git config user.email "<your-github-email@example.com>"
# 子模块内各自 commit 也需要；可使用 --global 一次性全局配置
```

---

## 第 2 步：后端环境初始化（15 min）

### 2.1 安装 Python 依赖

```bash
cd CS-Web-Backend
# 方式 A：推荐使用 uv（已锁 uv.lock，速度是 venv/pip 的 3~5 倍）
uv sync

# 方式 B（没有 uv 的临时替代）：
# python3.13 -m venv .venv
# source .venv/bin/activate
# pip install -e ".[test]"
```

**成功标志**：`uv sync` 末尾 `Resolved <N> packages`，无红色错误；结束后 `ls .venv/bin/python` 存在（方式 A 自动建 venv）。

### 2.2 生成本地 `.env` 并填写 4 个必填密钥

```bash
# 在 CS-Web-Backend 目录内；.env.development 是"最全本地开发模板"
cp .env.development .env
```

打开新建的 `.env`，**MUST** 修改以下 4 行（留空会导致启动阶段直接抛异常）：

| 变量 | 建议值（本地开发） | 说明 |
|---|---|---|
| `DATABASE_PASSWORD` | `devpgpass123`（任意非空字符串） | PostgreSQL 超级用户密码 |
| `SECRET_KEY` | `python -c "import secrets; print(secrets.token_urlsafe(48))"` 运行输出 | JWT 签名密钥，≥ 32 字节 |
| `TOTP_ENCRYPTION_KEY` | 同上，再生成一条**不同的** | 2FA TOTP seed 加密密钥，≥ 32 字节 |
| `AUTH_SESSION_SECRET` | 同上，再生成一条**不同的** | 前端 BFF Cookie 加密密钥，≥ 32 字节 |

> **生成三条随机密钥的一条命令**：
> ```bash
> python -c "import secrets; [print(secrets.token_urlsafe(48)) for _ in range(3)]"
> ```

**成功标志**：`.env` 文件 4 个变量全部被赋值，行尾没有引号包裹值（uvicorn/pydantic 会自动去引号，加了引号反而会把引号当值的一部分）。

### 2.3 启动 PostgreSQL（本地开发）

```bash
# 方式 A：用根级 docker compose 仅起数据库（推荐，端口 5432，库名 domefff）
cd ..        # 回到项目根目录
docker compose up -d db redis
# 等 10 秒让 PG 初始化；然后确认容器健康
docker compose ps
# 期望：db 服务 STATE = Up (healthy)，redis = Up
```

方式 B（已有本机 PG）：创建用户 `postgres` / 数据库 `domefff`，并在 `.env` 里把 `DATABASE_HOST/PORT/USER/PASSWORD` 对齐到本机实例。**SHOULD** 使用方式 A 以避免环境差异。

### 2.4 执行 Alembic 迁移建表

```bash
cd CS-Web-Backend
source .venv/bin/activate   # 方式 B venv 才需要；uv run 会自动激活
alembic upgrade head
```

**成功标志**：末尾打印 `INFO  [alembic.runtime.migration] Running upgrade  -> <revision-hex>, <migration message>`；最后一条是最新 head（`make gen-doc-facts` 可查 head 编号）。没有 `ERROR` / `Traceback`。

**验证表已建**：

```bash
cd .. && docker compose exec -T db psql -U postgres -d domefff -c "\dt"
# 成功标志：列出 users / roles / permissions / exams / events / posts 等 30+ 张表
```

---

## 第 3 步：前端环境初始化（5 min）

### 3.1 安装 pnpm 依赖

```bash
cd CS-Web-Frontend
pnpm install
```

**成功标志**：末尾 `Progress: resolved <N>, reused <M>, downloaded <K>, added <L>`，无 `ERR_PNPM_*` 红色错误。

### 3.2 生成前端 `.env`

```bash
cp .env.example .env
```

打开 `.env`，至少填这三项（其余留默认即可）：

| 变量 | 本地开发建议值 | 说明 |
|---|---|---|
| `AUTH_SESSION_SECRET` | **与后端 `.env` 同一条**（前后端共享，否则会话加解密互踢） | 必须与后端一致 |
| `ALLOWED_ORIGINS` | `http://localhost:2333,http://127.0.0.1:2333` | 写端点 Origin 白名单 |
| `NEXT_PUBLIC_SITE_URL` | `http://localhost:2333` | 登录回调 / OAuth 跳转拼接 |

> **可选 LLM 配置**（不填也能跑，Auxilio 自动降级为纯规则推荐）：按 [RootDoc-Deploy.md](RootDoc-Deploy.md) §二 2.2 节 `LLM_*` 项补充。

**成功标志**：`.env` 3 项齐全；`AUTH_SESSION_SECRET` 与后端 `.env` 值完全一致（逐字符）。

---

## 第 4 步：一键并行起前后端（5 min）

### 4.1 根级 `make dev-up`

```bash
cd ..   # 回到项目根目录

# 首次建议先 make setup（把根 .env.example 拷到根 .env；主要是 docker compose 用）
make setup
# 根级 .env 中 DATABASE_PASSWORD 与 CS-Web-Backend/.env 保持一致即可；其余默认

# 前台同时起：后端 :9000（python run.py --port 9000 热重载）+ 前端 :2333（pnpm dev）
make dev-up
```

### 4.2 等待双方启动成功

两个进程会同时输出日志。**耐心等待 60 秒**（首次 pnpm dev 编译需要时间）。

**后端就绪标志**：日志出现 `Uvicorn running on http://0.0.0.0:9000` + `Application startup complete`。

**前端就绪标志**：日志出现 `ready started server on 0.0.0.0:2333, url: http://localhost:2333`（Next.js）。

### 4.3 三条独立 curl 验证（不通过 MUST 不要进入下一步）

新开一个终端窗口，回到根目录：

```bash
# 验证 1：后端 /health 浅检查（liveness）
curl -s http://localhost:9000/health
# 期望：{"status":"ok"}   （200 OK）

# 验证 2：前端 BFF → 后端 的健康检查转发
curl -s http://localhost:2333/api/health
# 期望：{"status":"ok"}   （200 OK）；若 500 → 前端 BACKEND_URL 没指到 9000，查前端 .env

# 验证 3：后端 OpenAPI 文档页返回 200（不必打开浏览器，curl head 即可）
curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/docs
# 期望：200
```

三条全部成功 → 进入第 5 步的浏览器交互验收。任何一条失败 → 跳到 §8 故障排查对应条目。

---

## 第 5 步：浏览器跑通验证（10 min · 三条路径，每条都有明确成功画面）

### 5.1 路径 A：注册 → 登录 → 完整个人信息页（/profile）

1. 打开 **http://localhost:2333**
2. 点右上角「注册」→ 填真实邮箱（本地开发会把验证码打印到**后端 stdout 日志**）→ 提交
3. 切回后端终端窗口找一行类似 `[EmailService] verification code for a@b.com: 123456` → 把 6 位码粘到注册验证页 → 完成注册
4. 自动跳登录页 → 输入刚注册的邮箱/密码 → 登录
5. 点右上角头像 → 「个人中心」→ 跳 `/profile`

**成功标志（全部出现才算通过）**：
- 页面标题「个人中心 - FztbuCS」
- 基本信息卡片：头像（有默认 SVG，不是空白占位）、昵称、邮箱、角色标签（普通成员/社干/管理员）
- 安全卡片：「密码已设置」字样；TOTP 开关可点击（开/关都允许，Tutorial 期不必开启）
- 页面无 404 / 500 错误边界卡；F12 Console 无红色 `Uncaught`

### 5.2 路径 B：/auth/me 响应字段完整性

保持登录态（浏览器已拿到 Cookie），在同一浏览器开新 Tab 访问：
**http://localhost:9000/api/v1/auth/me**（后端直连，跳过 BFF 便于排查 Cookie/BFF 层问题）

**成功标志**：JSON 响应 200，包含至少以下字段（camelCase，不是 snake_case）：
```json
{
  "id": 1,
  "email": "you@example.com",
  "nickname": "...",
  "roles": [{ "key": "member", "name": "普通成员" }],
  "permissions": [...],
  "createdAt": "2026-08-20T00:00:00+08:00"
}
```

字段缺失或蛇形命名 → 跳 §8.6「字段风格错位」。

### 5.3 路径 C：退出登录 → 再登录

个人中心右上角头像 → 「退出登录」→ 被踢回 `/login`。

**成功标志**：
- 再次访问 `/profile` 被 302 跳回 `/login`（鉴权守卫生效）
- 重新输入密码可再次登录（refresh token 没有被复用检测误踢）

三条路径全过 → 本地跑通验收完成。你已具备「改代码 → 本地验证」的基础环境。

---

## 第 6 步：跑测试 + Lint（15 min · 提 PR 前 MUST 全绿）

### 6.1 后端：pytest 全量 + mypy 静态

```bash
cd CS-Web-Backend
source .venv/bin/activate   # 非 uv 方式需要；uv run 可省略

# 6.1.1 单元 + 特性 + 集成测试（pytest 自动加载 .env.test，库名含 test 才允许执行，防止误扫生产）
python -m pytest -q
```

**成功标志**：末尾 `=<N> passed in <T>s`，**0 failed / 0 error**；没有 `SKIP` 超过 5 个（超过的话查 tests/README.md 看是否漏装可选依赖）。

```bash
# 6.1.2 静态类型检查（RootEngConv §二 红线；CI 同配置）
mypy app/              # 允许少量 warnings，但 MUST 0 error
# 6.1.3 代码风格 + Lint
black --check app/     # CI 阻断；未格式化用 black app/ 修复
flake8 app/            # CI 阻断
```

**成功标志**：三条命令 `exit code 0`；任何一条非零 → §8.7「后端测试/Lint 失败」。

### 6.2 前端：ts-check + lint:build + test

```bash
cd CS-Web-Frontend

pnpm run ts-check      # tsc --noEmit；类型对齐（与后端 OpenAPI 生成类型对照）
pnpm run lint:build    # ESLint + 生产构建产物静态检查；不含运行时
pnpm test -- --run     # Vitest 单次跑，不 watch
```

**成功标志**：三条命令全部 0 error；test 末尾 `Test Files <M> passed | <N> failed`，`<N>=0`。

> 以上四条命令（pytest + mypy + ts-check + test）**MUST** 在你提 PR 前在本地跑过一遍并全绿；CI 会重跑，不一致会被打回。

---

## 第 7 步：体验工作台 /tools（5 min）

保持登录态，访问 **http://localhost:2333/tools**。

顶部有两个 InlineTabs：「工作台」（默认）与「学习助手」。

### 7.1 工作台：GitHub 贡献热力图绑定

1. 在「GitHub 贡献热力图」卡输入框填你的 GitHub 用户名 → 点「绑定」
2. 等待 ≤ 10 秒（首次后端抓公开页缓存 6h，未命中会慢）

**成功标志**：出现 53×7 绿色方格热力图 + 徽章显示「总贡献数」与「连续天数 streak」。失败则卡片提示错误原因（用户不存在 / 限流 403）。

### 7.2 学习助手 Tab：Auxilio 对话

切到「学习助手」Tab → 在底部输入框发 `你能帮我做什么？`。

**成功标志（两种之一）**：
- 若根 `.env` 配了 `LLM_PROVIDER!=none`：流式打字机逐字输出，且有"调用工具"状态卡展示
- 若未配 LLM：规则模式兜底回复，告诉你"当前未接入模型，可在设置中配置"；**不会报错或白屏**（降级路径 MUST 生效）

---

## 第 8 步：常见故障排查（任何步骤失败先查本节）

本节按**最常出现 → 最少出现**排序；条目号与上方步骤号对应。

### 8.1 端口冲突（第 0.2 步未通过）

| 冲突端口 | 临时替代方案 | 永久修复 |
|---|---|---|
| 2333（前端） | `PORT=2334 pnpm dev` + 同步改前端 `.env` 的 `ALLOWED_ORIGINS` / `NEXT_PUBLIC_SITE_URL` | `lsof -ti :2333 | xargs kill -9` 释放旧进程 |
| 9000（后端） | `python run.py --env 1 --port 9001` + 前端 `.env` 的 `BACKEND_URL=http://localhost:9001` | 同上，杀 PID |
| 5432（PG） | docker compose 的 db 服务 `ports: "55432:5432"` 映射（不建议）+ 同步后端 `.env` `DATABASE_PORT=55432` | 卸载本机 PostgreSQL 或停掉 brew service |
| 8000（容器内部后端） | 本教程本地开发不用 8000；冲突只影响 docker compose 生产部署，见 [RootDoc-Deploy.md](RootDoc-Deploy.md) | — |

### 8.2 子模块为空 / 缺失（第 1.2 步失败）

```bash
# 彻底重来子模块（不会丢失你在子仓的改动，因为那在各自 .git 里）
git submodule deinit -f --all
git submodule update --init --recursive
# 再次验证
ls CS-Web-Backend/app/main.py
```

仍为空 → 检查你的 GitHub 权限：是否为当前仓组织成员、SSH Key 是否生效（`ssh -T git@github.com` 应返回 Hi <username>）。

### 8.3 Python 导入报 `SyntaxError: invalid syntax` 指向 `X | None`（第 2.1 步）

**100% 原因是 Python < 3.10**。`X | None` 联合类型语法在 3.10 才引入；本项目 requires-python >= 3.13。

```bash
# 确认实际运行的 python 版本
python  --version    # 若仍是 3.9.x → PATH 里旧版本优先
python3 --version    # 若仍不是 3.13 → 重装
which python         # 看解析到哪个可执行文件
```

修复：`uv sync` 会自动按 `requires-python` 选解释器；或显式 `uv python install 3.13 && uv sync --python 3.13`。

### 8.4 `alembic upgrade head` 报 `connection refused`（第 2.4 步）

容器 db 服务没起来或端口错配：

```bash
cd <project-root>
docker compose ps              # db STATE 应为 Up (healthy)
docker compose logs db --tail 50
# 常见原因：DATABASE_PASSWORD 根级 .env 与后端 .env 不一致
# → 统一密码后 docker compose down && docker compose up -d db 重启
```

### 8.5 前端登录后 401 无限重定向登录页（第 5.1 步）

排查顺序（从上到下逐一验证）：
1. 后端 `/health` 是否 200（直连 localhost:9000，绕过 BFF）。不是 → §8.4 起后端。
2. 前端 `.env` 的 `AUTH_SESSION_SECRET` 与后端 `.env` 的完全一致。不一致会导致 Cookie 签名校验失败 → 每次 `/auth/me` 都匿名。
3. 前端 `.env` 的 `BACKEND_URL=http://localhost:9000`。不要写成 `127.0.0.1` 或 `0.0.0.0`（Cookie 同源策略匹配会诡异）。
4. 冷重启前端 dev server：`make restart-frontend`（tsx watch 热重载缓存损坏常见表现：BFF 路由全 500 但首页正常；见 RootDoc-Deploy 历史 §四 注意项）。

### 8.6 第 5.2 步字段为 snake_case（`created_at` 而非 `camelCase`）

契约 1.0.1 规定传输字段是 camelCase。出现蛇形说明：
- 后端 `TZModel` 或 `BaseResponse` 的 `by_alias=True` 别名未生效 → 查 schemas/base.py 配置。
- 或你开了未合并的老分支 → 切回 main 并对齐子模块指针 `git submodule update`。

### 8.7 第 6 步测试 / Lint 失败

后端 pytest 失败最常见的 3 类：

| 错误关键词 | 根因 | 处理 |
|---|---|---|
| `database "domefff" does not exist` 或 `rejected: not a test database` | 没加载 `.env.test`；`conftest.py` 强制库名含 `test` | `cp .env.test .env.test.local` 并确认 `DATABASE_URL` 里 dbname 含 `test`；或 `pytest -c pytest.ini` 显式用配置 |
| `EMAIL_EXISTS` / 注册接口唯一约束冲突 | 上次跑的测试 user 残留（cleanup 不幂等） | `docker compose exec -T db psql -U postgres -d domefff_test -c "TRUNCATE users CASCADE;"` 清表后重跑 |
| mypy `Cannot find implementation or library stub for module named "xxx"` | 缺 stub 包或 mypy.ini 未 ignore | 按错误提示 `uv add --dev types-xxx`；或在 `mypy.ini` 的 `[mypy-xxx]` 下加 `ignore_missing_imports = True` |

前端失败最常见的 2 类：
- `pnpm run lint:build` 报 `eslint` 规则 → 跟着提示文件行号修；或 `pnpm run lint:build -- --fix` 自动修能修的。
- `ts-check` 报 `Type X is not assignable to type Y` 在契约 DTO → 重新生成前端类型：`make gen-openapi-types`（根 Makefile，从后端 `/openapi.json` 拉取并覆盖前端 `src/lib/api/generated.types.ts`）。

### 8.8 `pnpm audit` CI 阻断（不是本节故障，但你提 PR 会遇到）

前端 `package.json` 的 audit 已升级为 **moderate+ 即阻断**。本地看到 `pnpm audit` 有 moderate+ → 不要强行 `continue-on-error`：
1. 先 `pnpm audit --fix` 自动升级可升级版本；
2. 仍有漏洞 → 查漏洞路径是否 `devDependencies`：是 → 加 Waiver 并 @reviewer 审批；否 → 必须升级到修复版本或替换同类库。

---

## 第 9 步：提第一个 PR（5 min · 自检打钩清单）

**在你修改任何代码后，提交前 MUST 逐项检查并在 PR Description 打钩**。CR 审核人看到未打钩的项会直接打回。

### 9.1 通用自检（所有 PR 适用）

- [ ] 第 6 步四项（pytest / mypy / ts-check / frontend test）在本地已跑且全绿；粘贴终端最后 10 行到 PR Comment。
- [ ] 若新增/修改了 API Schema：`make gen-doc-facts` 本地 **0 diff**（OpenAPI 基线 + 版本三源 + 文档派生事实同步）。
- [ ] 文档改动：若是 Reference/Explanation 类，已同步修改对应 L1/L2 权威文档（`-01-Arch` / `-02-Sec` / `-03-Conv`），而不是只在本 Onboarding 改。
- [ ] 跨仓关联：若改了后端 `/api/v1` DTO，前端 `openapi.baseline.json` 与类型生成同步 PR 已关联（或同一 PR 同时改三仓指针）。
- [ ] **没有把密钥 / token / 密码 / .env 内容写进 commit**（`git diff HEAD` 再过一遍 grep SECRET/KEY/PASS/TOKEN）。

### 9.2 前端 PR 加检

- [ ] `pnpm run lint:build` 通过；新增代码无裸 `any`。
- [ ] 新增页面/组件已对照 [FrontDoc-UID.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-UID.md) 视觉 Checklist；UI 截图附 PR。
- [ ] 写端点走 BFF → `assertAllowedOrigin` + Zod Schema + `proxyBackend` 调用链（见 [FrontDoc-03-Conv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-03-Conv.md) §2 调用链图）。

### 9.3 后端 PR 加检

- [ ] DDD 分层单向（api → service → repository → model），无反向 import。
- 新增 datetime 响应继承 `TZModel`；取时间用 `now_utc()`；没有 `datetime.now()` / `.utcnow()`。
- Alembic 迁移仅增量；未修改任何历史迁移文件。
- 新增角色/权限：同步 `services/rbac/rbac_seed_data.py` 与 RBAC init 顺序；避免上生产后默认角色缺失。
- 业务异常抛 `BaseAppException` 子类；路由不裸 `raise HTTPException`。

### 9.4 移动端 PR（若涉及）

- [ ] 业务代码 0 处裸 `wx.` / `plus.` 调用（CI grep 扫描）；端差异收敛进 `shared/utils/*.ts` 或 `platform/`。
- [ ] Pinia persist 仅白名单；token/SafeUser/权限未持久化（见 [MobileDoc-03-Conv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Mobile/tools/docs/MobileDoc-03-Conv.md) §4.2.2）。
- [ ] 小程序包体（主包）构建未超 1.8MB；`pnpm run build:mp-weixin` 输出体积附 PR Comment。

打钩完成 → 正常 `git push <your-fork> <branch>` 开 PR。等待 reviewer 反馈即可。

---

## 第 10 步：深入路径（Tutorial 结束后的自学导航）

完成全部 9 步后你已成为可独立贡献的开发者；根据你的方向选择深入入口：

| 你想做什么 | 第一站（权威 SSOT） | 第二站（实现级细节） |
|---|---|---|
| 理解整体架构与选型动机 | [README.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/README.md) → RootDoc-WritingGuide 总纲 | 对应子仓 `-01-Arch.md` Arc42 8 章 |
| 改前端页面/组件/BFF 路由 | [FrontDoc-03-Conv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-03-Conv.md) | [FrontDoc-UID.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-UID.md)（视觉）+ [FrontDoc-02-Sec.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-02-Sec.md)（安全） |
| 改后端 API / 模块 / 迁移 | [BackDoc-03-Conv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-03-Conv.md) | [BackDoc-ModuleContracts.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-ModuleContracts.md)（各模块 RFC2119 契约） |
| 改移动端 uni-app x / 双端差异 | [MobileDoc-03-Conv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Mobile/tools/docs/MobileDoc-03-Conv.md) | [MobileDoc-02-Sec.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Mobile/tools/docs/MobileDoc-02-Sec.md)（双端存储/SSL Pinning/供应链） |
| 部署上线 / 运维 Runbook | [RootDoc-Deploy.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-Deploy.md) | [BackDoc-Infra.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-Infra.md) / FrontDoc-Ops.md |
| 通用跨仓工程红线 + 命名门禁 + 版本三源 | [RootDoc-EngConv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-EngConv.md) | RootDoc-ModuleMap.md |

---

> ↩ **返回文档地图**：[README.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/README.md) · **Tutorial 配套 How-to（部署）**：[RootDoc-Deploy.md](RootDoc-Deploy.md) · **工程约定权威**：[RootDoc-EngConv.md](RootDoc-EngConv.md) · **架构入口**：三仓 `-01-Arch.md`
