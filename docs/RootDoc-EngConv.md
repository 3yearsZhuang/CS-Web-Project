# 通用工程规范（跨项目提炼）（RootDoc-EngConv）

> 更新人：3yearsZ
> 最后更新：2026-08-05（统一 RootDoc 命名）
> 从后端 `CS-Web-Backend/tools/docs/BackDoc-Conv.md` 与前端 `../CS-Web-Frontend/tools/docs/FrontDoc-UID.md` 提炼的**框架无关**通用原则。
> 本项目（FztbuCS-Project）内的 Python/FastAPI 与 TypeScript/Next.js 代码均适用。
> 端侧强相关的完整规范仍以各子仓库为权威（见文末深链接），此处只收通用原则，避免重复漂移。
>
> **约定类文档边界**：通用（两端共用）规范以本文件为权威；**后端专项**约定见 `CS-Web-Backend/tools/docs/BackDoc-Conv.md`；**前端专项**约定见 `../CS-Web-Frontend/tools/docs/FrontDoc-Conv.md`（编码规范）、`FrontDoc-01-Arch.md`（架构与约定）与 `FrontDoc-UID.md`（UI 规范）；`docs/Onboarding.md` 附录 A 为面向新人的**聚合摘要（非权威）**，细则一律指回上述权威文件。约定文件与聚合摘要出现冲突时，以各自的权威文件为准。

---

## 一、命名规范

| 对象 | 规范 | 示例 |
|---|---|---|
| 类 | `PascalCase` | `User`, `Button` |
| 函数/方法 | `snake_case`（py）/ `camelCase`（ts）；私有以 `_` 开头（py） | `_hash_password`, `getUser` |
| 常量 | `UPPER_SNAKE_CASE` | `DEFAULT_PAGE_SIZE` |
| 组件（前端） | `PascalCase`，文件与默认导出同名 | `Button.tsx` → `Button` |
| 配置文件/桶导出 | `index.ts` / `index.py` | 聚合导出 |

### 三端业务模块命名（2026-08-19 确立，P2-9）

**正文权威**：[`模块命名映射表.md`](模块命名映射表.md)（唯一权威：三端模块 ↔ 契约资源映射、门禁、违约点红线、变更记录）——本小节仅保留速查，避免双源漂移。

**速查**：三端业务模块名 = API 资源名（`openapi.baseline.json` 中 `/api/v1` 路径第一段，复数）——前端/移动端 `src/modules/<资源>/`、后端 `app/api/v1/<资源>.py`（tools 子域收 `api/v1/tools/` 包）；业务组件进所属模块 `ui/` + `ui/hooks/`，公共层只留跨 ≥2 域复用件。
**门禁**：`make check-module-naming`（`scripts/check/check_module_naming.py`）强制三端模块名 ⊆ 契约资源名，已接入根 CI PR 门禁（P2-9，2026-08-19）。
**新增业务模块流程**：先定 API 资源名（走 `make contract-baseline` 入契约）→ 三端目录同名 → `check-module-naming` 校验通过 → 映射表登记。

---

## 二、代码质量红线

### 单一职责与规模

- 单一职责：一个模块/函数只做一件事；禁止把多个业务域塞进同一个文件。
- 文件大小：单文件超 **~300 行（py）/ ~500 行（组件）** 必须评估拆分。
- 函数长度：明显超过一屏（约 50–80 行逻辑）或含多个处理阶段时，按语义拆辅助函数。

### DRY 与抽象（三次法则）

- 同一段逻辑在 **3 处**出现，必须抽公共函数；1–2 处直接写，**不要预先抽象**。
- 出现真实重复才复用；不要因为两段代码暂时相似就过早抽象。

### 圈复杂度

- 单函数圈复杂度建议 ≤ **10**；超过用早返回、查表、策略对象拆分。
- 避免深度嵌套 `if/elif` 链，优先改写为「条件 → 动作」映射。

### 魔法值与单一事实源

- **禁止散落的魔法值**：重复出现的字面量（版本号、地址、状态码字符串…）必须收敛到单一来源。
- **禁止硬编码**：不写死 host:port、密钥、颜色、断点；一律走设计令牌/常量/配置。

---

## 三、错误处理约定

- 业务失败用统一的异常基类表达，由全局处理器映射状态码与响应体；禁止在路由里吞异常返回自定义格式。
- 禁止空 catch / 静默吞错：必须记录或向上抛；错误信息保留上下文但**不得泄露敏感信息**（密钥、令牌、密码）。
- 外部输入（HTTP/文件/外部 API）必须校验；内部代码信任类型，不重复校验。

---

## 四、安全约定

- **禁止硬编码**密钥、令牌、密码、生产凭证；统一从配置或环境变量读取。
- 使用成熟库做密码哈希/加密，禁止自实现加密。
- SQL 用参数化查询，禁止字符串拼接。
- 日志禁止记录密码、token、个人敏感信息。

---

## 五、配置约定

- 所有配置项收敛到单一 `Settings`/`config` 源；**新增配置必须同步模板**（`.env.example` / `config/index.ts`），否则他人无法知道配置项。
- 本地覆盖用不跟踪的 local 文件（`.env.local`）。
- 每个功能一块独立配置文件，统一 `index` 聚合导出（"单块 → 聚合"）。

### 5.1 环境变量职责矩阵（层 × 变量 × 归属）

> 三份模板：根 `.env.example`（全栈模板，驱动 docker-compose）、后端 `CS-Web-Backend/.env.example`（最全）、前端 `CS-Web-Frontend/.env.example`（BFF 运行时 + 遗留记录）。改配置时按此矩阵定归属层；新增变量须同步对应模板（见 §五 首条）。

| 变量 | 归属层 | 用途 | 备注 |
|---|---|---|---|
| `DATABASE_HOST/PORT/NAME/USER/PASSWORD` | 根 + 后端 | PostgreSQL 连接 | 共享：根驱动 compose `db` 服务（HOST=`db`），后端驱动 SQLAlchemy（HOST=`localhost`） |
| `DATABASE_URL` | 后端 | 完整连接串 | 后端专属，与拆分字段二选一 |
| `DB_POOL_SIZE` 等 `DB_POOL_*` | 后端 | 连接池参数 | 后端专属（有默认值） |
| `SECRET_KEY` | 根 + 后端 | JWT 签名密钥（≥32B） | 共享：根模板必填，compose 注入 backend |
| `TOTP_ENCRYPTION_KEY` | 根 + 后端 | 2FA 加密密钥（≥32B） | 共享 |
| `ALLOWED_ORIGINS` | 根 + 后端 + 前端 | CORS / Origin 白名单 | 三层共享，可同一份 |
| `NEXT_PUBLIC_SITE_URL` | 根 + 前端 | 站点 URL（metadata base） | 前端运行时 |
| `TRUST_PROXY` | 根 + 后端 + 前端 | 信任反向代理头 | 共享 |
| `AUTH_SESSION_SECRET` | 根 + 后端 | 会话 token HMAC 密钥 | 权威在后端；前端模板已标遗留 |
| `BACKEND_URL` | 前端 | BFF 转发后端地址 | 前端专属 |
| `PASSWORD_RESET_DEFAULT` | 根 + 后端 | 管理员重置默认密码 | 前端模板已标遗留 |
| `SMTP_*` | 根 + 后端 | 邮件发送（后端 aiosmtplib） | 前端模板已标遗留 |
| `GITHUB_*` | 根 + 后端 | GitHub OAuth | 前端模板已标遗留 |
| `REDIS_URL` / `REQUIRE_REDIS_FOR_SECURITY` | 根 + 后端 | Redis 队列 / 缓存 | 共享，可选 |
| `QUEUE_ENABLED` / `MULTI_INSTANCE` | 根 + 后端 | 异步队列 / 多实例广播 | 共享，可选 |
| `LLM_*` | 后端 | Auxilio LLM（openai / anthropic） | 后端专属；根模板未列（默认 `none` 可运行） |
| `COMMUNITY_IP_HASH_SECRET` | 根 + 后端 | 社区浏览去重 IP 哈希 | 共享，可选 |

> 前端模板中的「迁移前单体遗留变量」（`AUTH_SESSION_SECRET` / `SMTP_*` / `PASSWORD_RESET_DEFAULT` / `GITHUB_*`）仅为记录：运行时不被前端 API 引用（认证 / 邮件 / OAuth 已由后端承载），权威在后端，待后续清理。

---

## 六、测试约定

- 测试覆盖至少覆盖正向、反向、边界三类路径。
- **测试数据必须模拟真实写入路径**：UI/API 写什么格式，测试就构造什么格式；禁止用"看起来合理"的格式掩盖分支。
- 必须覆盖边界用例（空字符串、null、临界值），不只测 happy path。

---

## 七、Git 与提交

- **提交格式**：`<type>(<scope>): <subject>`，type：`feat / fix / refactor / chore / docs / test`。
- **不主动 commit / push**，除非用户明确要求。
- 禁止提交：`*.db`、`logs/`、密钥、本地环境覆盖文件。
- **侵入性操作**（删文件、改公共接口、改数据库结构）**先说明范围再做**。

---

## 八、修改范围（协作约束）

1. 只改动完成任务所必需的最小范围，禁止顺手重构无关代码。
2. 修改前先读取相关现有文件，风格、命名、组织方式必须与现有代码保持一致。
3. 若现有实现已能满足需求，优先复用而非重写；禁止为炫技引入不必要的抽象。
4. 禁止引入未声明的新依赖 / 未经评审的新库；禁止同时使用多种实现同类功能的库。

---

## 九、中文排版规则（前端专属补充）

> 本条为**前端专属**排版约定，通用文档（本文件）仅作引用性收录。完整规范以前端权威文档 [`FrontDoc-UID.md`](../CS-Web-Frontend/tools/docs/FrontDoc-UID.md) 为准。

- 汉字之间不留空格。
- 中英文之间留空格。
- 中文与数字之间留空格。

---

## 十、前端工程约定（React Compiler / 语义色板 / widget registry / i18n）

> 本条原为前端专属工程约定的通用原则收录，现已全部迁移至前端专项规范 [`../CS-Web-Frontend/tools/docs/FrontDoc-Conv.md`](../CS-Web-Frontend/tools/docs/FrontDoc-Conv.md)（§3 React Compiler 红线、§5 样式令牌、§8 工作台 widget 注册表、§9 i18n）。**禁止事项分发**：前端**编码侧**禁止项汇总见 `FrontDoc-Conv.md §12`；**UI 视觉**禁止项见 `FrontDoc-UID.md §11`；后端见 `BackDoc-Conv.md`；本 §二 仅保留框架无关的通用红线。此处不再重复，避免双份漂移。

---

## 十一、深链接（端侧完整规范）

| 端 | 权威文档 |
|---|---|
| 后端 | `CS-Web-Backend/tools/docs/BackDoc-Conv.md`（编码规范、命名、质量红线、安全/错误处理约定） |
| 前端编码 | `../CS-Web-Frontend/tools/docs/FrontDoc-Conv.md`（前端编码规范、TS/React/Next.js 约定、样式令牌、组件契约） |
| 前端视觉 | `../CS-Web-Frontend/tools/docs/FrontDoc-UID.md`（视觉与交互设计规范）；前端编码规范（含 server-only 边界）见 `../CS-Web-Frontend/tools/docs/FrontDoc-Conv.md`，根级 `docs/Onboarding.md` 附录 A.6 仅为入口指针 |
| 前端方法论 | `../docs/RootDoc-FEArch.md`（目录设计艺术，CS-Web-Frontend 专属方法论） |
