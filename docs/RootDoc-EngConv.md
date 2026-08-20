# RootDoc-EngConv：跨仓通用工程约定（命名 / 版本 / 安全红线 / Makefile / 所有权矩阵）

> 更新人：3yearsZ
> 更新日：2026-08-20
> 版本：1.0.1（版本基线对齐 1.0.1；冻结契约 `/api/v1`、版本三源同步、Alembic 线性链、禁硬编码密钥、DDD 分层）
> Diátaxis：R（Reference · 规范参考 · 三仓通用工程约定 L0 唯一权威）
> 适用读者：全仓贡献者、后端/前端/移动端 reviewer、发布负责人、运维侧部署人员
> 变更触发：新增/重命名仓库或子模块 / 版本号升级策略变动 / Alembic 链约定变更 / 密钥或安全红线变动 / Makefile 收敛目标变动 / 所有权矩阵调整
>
> **SSOT（唯一权威）声明**：本文档是 FztbuCS monorepo **三仓通用工程约定 L0** 的唯一权威输入。三仓内部（CS-Web-Backend / CS-Web-Frontend / CS-Mobile）的实现级约定以各自 `-03-Conv.md` 为权威；三仓安全实现级约束以 `-02-Sec.md` 为权威（本文档仅收录**跨仓共享的通用安全红线**，不重述实现细节）；命名门禁完整映射以 [RootDoc-ModuleMap.md](./RootDoc-ModuleMap.md) 为唯一权威。
>
> **关联索引**：根仓方法论总览 → [README.md](../README.md)；完整资源域命名门禁 → [RootDoc-ModuleMap.md](./RootDoc-ModuleMap.md)；派生事实自动化脚本 → `tools/gen_doc_facts.py` + 根仓 `Makefile`；后端实现约定 → [BackDoc-03-Conv.md](../CS-Web-Backend/tools/docs/BackDoc-03-Conv.md)；前端实现约定 → [FrontDoc-03-Conv.md](../CS-Web-Frontend/tools/docs/FrontDoc-03-Conv.md)；移动端实现约定 → [MobileDoc-03-Conv.md](../CS-Mobile/tools/docs/MobileDoc-03-Conv.md)

---

## 0. 文档速览：约束密度总表

| 章节 | 主题 | MUST 条数 | MUST NOT 条数 | SHOULD 条数 | MAY 条数 | 关键代码入口 |
|------|------|-----------|--------------|------------|----------|-------------|
| §1 | 共享术语表与命名门禁（资源域/模块/接口/列） | 10 | 8 | 5 | 3 | [RootDoc-ModuleMap.md](./RootDoc-ModuleMap.md)、`backend/app/models/`、`frontend/src/lib/api/`、`mobile/shared/api/` |
| §2 | 版本同步与 Alembic 迁移链 | 7 | 6 | 4 | 2 | 三仓 `pyproject.toml` / `package.json` / `__init__.py`、Alembic `versions/`、`tools/gen_doc_facts.py` |
| §3 | 通用安全红线 + 跨仓 DDD 分层 | 9 | 8 | 4 | 2 | 三仓 `.env.example`、`backend/app/api/deps.py`、`frontend/server/bff.ts`、`mobile/shared/api/client.ts` |
| §4 | Makefile 收敛 + 提交规范 | 7 | 6 | 4 | 2 | 根仓 `Makefile`、`backend/Makefile`、`frontend/Makefile`、`.pre-commit-config.yaml` |
| §5 | 所有权矩阵 + 跨仓反模式 | 8 | 7 | 5 | 2 | 三仓 `tools/docs/` 目录头、README 所有权声明 |
| §6 | — | **41（合计）** | **35（合计）** | **22（合计）** | **11（合计）** | — |

---

## 1. 共享术语表与命名门禁（资源域 / 模块 / 接口 / 列）

### 1.1 概述（一句话定位）

FztbuCS monorepo 由三仓 + 一文档仓协作：后端（FastAPI + SQLAlchemy + Alembic）、前端（BFF + Next.js + shadcn）、移动端（uni-app x，双端：Android APK + 微信小程序）、docs（项目根文档与 L0 规范）。本节定义三仓共享术语、资源域命名门禁、目录与接口/列命名的 MUST 约束，避免三仓漂移。**完整模块→资源域→代码路径→文档归属映射以 RootDoc-ModuleMap.md 为唯一权威。**

### 1.2 术语定义与命名清单

#### 1.2.1 共享术语表（三仓必须统一语义，任何文档/代码/接口注释不得偏离）

| 术语 | 定义（三仓共享语义） | 关联文档 |
|---|---|---|
| **L0 / L1 / L2 文档分层** | L0：根仓 docs（方法论/规范/跨仓）；L1：子仓 Arch（`-01-Arch.md`，Arc42 架构总览）；L2：子仓 专题（`-02-Sec` 安全、`-03-Conv` 约定、`MobileDoc-02-*` 移动专题） | [README.md](../README.md) |
| **MVP / 完整版** | MVP = 仅"邮箱+密码登录 + TOTP 可选 + 六大核心模块（用户/考试/协会/活动/社区/AI）+ 小程序 + 后端"；完整版 = 预留（微信登录/push 推送/订阅消息/生物识别/付费增值） | 各 Arch §2.3 目标矩阵 |
| **安全红线 vs 工程约定** | 安全红线（Sec）= 违反即安全漏洞（RFC2119 MUST/MUST NOT 高密度）；工程约定（Conv）= 可偏离但 MUST 在 CR 说明理由（RFC2119 SHOULD 密度偏高 + MUST/MUST NOT 作底线） | `-02-Sec.md` / `-03-Conv.md` 系列 |
| **SSOT / Double-source** | SSOT = 唯一真相源（每类事实仅一份权威文档/路径）；Double-source = 两处同时维护易漂移，为反模式，需收敛 | SSOT 声明在各文档头部 |
| **DDD 分层（跨仓）** | 后端：`api`（Controller）→ `services`（Service）→ `repositories`（DAO）→ `models`（Model）→ `schemas`（DTO）→ `core`；前端 BFF：`server/`（路由层）→ 业务层（复用后端 Service 定义但仅作转发）→ `lib/api/`（契约层，禁止自定义 DTO） | 后端 Arch §3 + Frontend Arch §3 |
| **资源域（Resource Domain）** | 三仓共享命名：`users`、`auth`、`exams`、`associations`、`activities`、`community`、`ai`、`admin`；新增模块 MUST 先登记 8 项到 RootDoc-ModuleMap.md | [RootDoc-ModuleMap.md](./RootDoc-ModuleMap.md) |
| **冻结契约 `/api/v1`** | `/api/v1` 前缀 **不变**；后端 FastAPI、前端 BFF、移动端 ApiClient 三处路径/字段/枚举 MUST 对齐；字段/枚举变更 MUST 遵循「新增 + 兼容窗口 + 弃用 + 移除」四阶段；见 Backend Arch §4.4.2 | [BackDoc-01-Arch.md](../CS-Web-Backend/tools/docs/BackDoc-01-Arch.md) |

#### 1.2.2 命名门禁清单（实现 MUST 遵循）

| 类别 | 规则 | 例外（若有） |
|---|---|---|
| **三仓根目录名** | `CS-Web-Backend` / `CS-Web-Frontend` / `CS-Mobile` / `docs`（根仓）；**不变** | 无 |
| **Python 后端资源模块** | `app/{domain}/` 小写蛇形：`users` / `auth` / `exams` / `associations` / `activities` / `community` / `ai` / `admin` | `core/`、`middleware/` 为非资源域 |
| **前端 BFF 路由** | `app/api/[domain]/route.ts` 小写 kebab：`users` / `auth` / `exams` / `associations` / `activities` / `community` / `ai` / `admin` | `dashboard`、`settings` 为 UI 页面非 API 域 |
| **前端 API 契约层** | `frontend/src/lib/api/{domain}.ts` 小写蛇形资源域对应；文件名 = 域；内部导出 `export type {Domain}DTO` 复用后端枚举/字段 | 禁止自定义 DTO；与 `/api/v1` 对齐 |
| **移动端 API 契约层** | `mobile/shared/api/{domain}.ts` 同上；snake_case→camelCase 仅在 ApiClient 自动翻译层转换，不得手写字段重命名 | |
| **数据库表名** | 蛇形复数：`users`、`exam_questions`、`association_members`、`activity_registrations`、`community_posts`、`ai_sessions` | Alembic 迁移 MUST 与模块同步；见 §2 |
| **数据库列名** | 蛇形；外键 `{singular}_id`（`user_id`、`exam_id`）；时间戳 `created_at`、`updated_at`（DATETIME 后端 TZ=UTC 存，UI 层转本地时区） | |
| **JSON 响应字段** | 蛇形：与表列一致，BFF 层不做字段风格转换，**仅前端 `lib/api` 层统一 snake_case→camelCase 转换** | |
| **枚举命名** | 后端 `UserRole(str, Enum)` PascalCase；JSON 值 snake_case（`"club_leader"`）；前端/移动端复用，禁止本地重新定义副本 | |
| **文档分类号** | `RootDoc-*` 根仓 L0；`BackDoc-01-Arch`、`BackDoc-02-Sec`、`BackDoc-03-Conv` 子仓 L1/L2；FrontDoc/MobileDoc 同理；禁止随意新增 `<Repo>Doc-04-*` | 完整目录 [RootDoc-Catalog.md](./RootDoc-Catalog.md) |

### 1.3 约束（RFC2119 分层）

**MUST（铁律红线）：**
1. 新增业务域模块（如 `finance`、`shop`）**MUST** 先在 [RootDoc-ModuleMap.md](./RootDoc-ModuleMap.md) 登记 8 项：Python 模块名、前端路由、移动端端点、数据库表名、API DTO 前缀、权限前缀、Owner、L2 文档；**MUST NOT** 先写代码后补登记。
2. 三仓共享术语 **MUST** 与 §1.2.1 表保持一致；**MUST NOT** 在代码/文档/接口注释中混用「社团/协会」「考试/测评」「帖子/动态」等双术语 —— 统一用「协会（association）」「考试（exam）」「帖子（post）」。
3. `/api/v1` 冻结契约 **MUST** 三仓对齐：后端 FastAPI、前端 BFF、移动端 ApiClient 路径/字段/枚举 MUST 一致；**MUST NOT** 任何一端私自新增/重命名字段。
4. 数据库表名/列名 **MUST** 蛇形复数/蛇形单数；**MUST NOT** 使用 PascalCase/camelCase 命名数据库对象。
5. 前端/移动端契约层 DTO **MUST** 复用后端输出的 snake_case 字段，在翻译层自动转 camelCase；**MUST NOT** 在业务组件手写字段别名（`const examId = exam.exam_id`）。
6. 外键列 **MUST** `{singular}_id`；多对多关联表 **MUST** `{a}_{b}_association`（如 `user_role_association`），禁止无命名规则的多对多中间表。
7. `created_at` / `updated_at` **MUST** 使用后端 UTC DATETIME；**MUST NOT** 在数据库端使用 `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` 自动更新（统一由 SQLAlchemy `server_default` + `onupdate` 控制）。
8. 枚举 JSON 值 **MUST** snake_case；**MUST NOT** 返回 PascalCase（避免 UI/契约层漂移）。
9. 文档分类号 **MUST** 严格按 §1.2.2 第 10 条；新增文档 MUST 在 `RootDoc-Catalog.md` 登记；**MUST NOT** 私自创建 `<Repo>Doc-04-*`、`Doc-*` 等乱序分类号。
10. 根仓 docs 目录 **MUST** 仅保留 L0 跨仓文档 + 引用索引；子仓内部文档 **MUST** 位于 `<Repo>/tools/docs/`，**MUST NOT** 散落在子仓根目录、`app/`、`src/` 业务目录。

**MUST NOT（禁止事项）：**
1. **MUST NOT** 子仓文档直接「引用 L1 内部约定」到根仓 docs；根仓只保留 L0 权威 + SSOT 指路链接。
2. **MUST NOT** 同一事实在 ≥2 处同时维护（例如版本号同时写在 `pyproject.toml` + `README.md`）；见 §2 三源同步治理。
3. **MUST NOT** 为"缩短 URL"或"适配旧系统"引入 `/api/v2`、`/internal`、`/legacy`、`/rpc` 等第二套 API 前缀；`/api/v1` **不变**。
4. **MUST NOT** 前端/移动端定义本地「角色枚举」"避开后端枚举漂移"；角色/状态/审核结果等枚举 **MUST** 从后端契约权威导入；本地副本 = Double-source，禁止。
5. **MUST NOT** 数据库表使用英文缩写（如 `usr`、`exm`、`asso`）—— 必须全拼写（`users`、`exams`、`associations`）。
6. **MUST NOT** 在 JSON 响应里混用蛇形 + 驼峰；**MUST** 全蛇形，由翻译层在消费端统一转换。
7. **MUST NOT** 模块目录名称复数/单数混用；`app/users/`（复数）= 资源域；`app/user.py`（单数）= 单文件模块；禁止 `app/user/` + `app/users/` 同时存在。
8. **MUST NOT** 允许同一功能同时存在两套 API（REST + GraphQL + gRPC）；当前唯一契约 = REST JSON `/api/v1`。

**SHOULD（建议事项）：**
1. **SHOULD** 每个资源域提供 `conftest.py`（后端）/ `*.test.ts`（前端）/ `*spec.ts`（移动）按域分组；便于按域独立跑回归测试。
2. **SHOULD** 文档中出现术语时，首次出现以超链接跳转到 RootDoc-ModuleMap.md 对应域；降低读者查询成本。
3. **SHOULD** 字段命名考虑未来扩展性：避免 `status` 这种无命名空间字段；优先 `review_status`、`registration_status` 等。
4. **SHOULD** 新增接口/表/字段前，用 RootDoc-ModuleMap.md 门禁清单先自查；CR 前提交人 MUST 在 PR 描述打钩（见 §6.2）。
5. **SHOULD** 三仓所有路由前缀、资源域名、目录名通过 `gen_doc_facts.py` 的自动化一致性检查（可扩展模块契约门控）。

**MAY（可选配置）：**
1. **MAY** 为前端提供内部 `domainToZod()` 辅助模板；但生成结果 **MUST** 与后端 OpenAPI schema 字段一致，不得自定义差异。
2. **MAY** 提供 `/api/openapi.json` 生成前端契约自动脚本；但生成产物 MUST 为只读，**MUST NOT** 提交人手工修改生成文件。
3. **MAY** 开发期临时在本地注释里用缩写（`# assoc = association`）；但提交 MUST 全拼。

### 1.4 自检 CheckList

- [ ] 新模块/新域：RootDoc-ModuleMap.md 8 项登记完成
- [ ] 共享术语：代码/文档 grep 0 处术语不一致（社团/协会、考试/测评 等）
- [ ] `/api/v1` 冻结契约：三端路径/字段/枚举 100% 对齐；无自定义差异
- [ ] 数据库对象：蛇形规范检查；无 PascalCase / 缩写 / 单复数混乱
- [ ] 文档分类号：`RootDoc-Catalog.md` 登记齐全，无乱序 `<Repo>Doc-04-*`
- [ ] 子仓文档位置：`<Repo>/tools/docs/`；根 docs 仅 L0 + 索引

---

## 2. 版本同步与 Alembic 迁移链

### 2.1 概述（一句话定位）

FztbuCS monorepo 采用语义化版本 `MAJOR.MINOR.PATCH`；同一发布版本号在三仓 + 根仓文档同时出现，必须通过「三源同步 + 脚本自动校验」统一治理。后端 Alembic 迁移链 MUST 线性链 + head 唯一；禁止分支合并头。`gen_doc_facts.py` 作为派生事实唯一权威生成器，Makefile 目标 `make gen-doc-facts` 一键同步。

### 2.2 配置与脚本清单

| 项 | 所在路径 | 说明 |
|---|---|---|
| **三仓版本号权威来源** | 后端 `pyproject.toml` [project] version | 唯一「人改」源；前端 package.json、后端 `app/__init__.py`、文档元数据版本号均从此派生 |
| 前端版本号 | `frontend/package.json` version | 由 `gen_doc_facts.py` 校验/同步；禁止人工改动 |
| 后端运行时版本 | `backend/app/__init__.py: __version__` | 同上；禁止人工改动 |
| 根文档元数据版本 | 所有 `*-Doc.md` 头部版本 | 同上；禁止人工改动 |
| `uv.lock` / `pnpm-lock.yaml` | 各仓库锁文件 | 依赖升级 MUST 同步更新；**禁止裸改 lock** |
| Alembic 版本目录 | `backend/alembic/versions/*.py` | 线性链；head 唯一 |
| `gen_doc_facts.py` | `tools/gen_doc_facts.py` | 派生事实唯一生成器：版本一致性 / Alembic 头 / 模块→契约对齐 / 测试存在检查 |
| `make gen-doc-facts` | 根仓 `Makefile`、子仓 `Makefile` | CI 前置：任何发布合并前 MUST 跑并 0 diff |

### 2.3 约束（RFC2119 分层）

**MUST（铁律红线）：**
1. **唯一版本源原则**：版本号升级 **MUST** 只在后端 `pyproject.toml` 人工修改；**MUST NOT** 同时人工修改前端 `package.json`、后端 `__init__.py`、文档头版本号（由脚本派生）。
2. **版本三源一致性**：发布合并前 `make gen-doc-facts` **MUST** 输出 0 diff（三源版本号完全对齐；Alembic 头匹配；模块契约对齐；测试存在检查通过）。
3. **语义化版本规则**：**MUST** 严格遵循 SemVer —— MAJOR 不兼容变更；MINOR 新增向后兼容功能；PATCH 向后兼容修复；**MUST NOT** 用 4 段版本号、日期版本号、前缀 `v`（发布标签除外 `git tag v1.2.3`）。
4. **Alembic 线性链**：所有 migration 文件 **MUST** 组成一条线性链（每个 revision 都有且只有一个 `down_revision`）；**MUST NOT** 存在多个 head 或 merge 迁移。
5. **Alembic 迁移归属**：每个 migration 文件 **MUST** 在 docstring 标注所属资源域（`# Domain: exams`）；新增域 MUST 与 RootDoc-ModuleMap.md 登记一致。
6. **锁文件改动**：依赖升级 **MUST** 通过包管理器（`uv add` / `pnpm add`）修改，`uv.lock` / `pnpm-lock.yaml` **MUST** 同时变更；**MUST NOT** 手工编辑锁文件。
7. **`/api/v1` 契约冻结版本映射**：每次 MAJOR 升级前 **MUST** 评估契约变更；**MUST NOT** 在 MAJOR 版本不变的前提下，对 `/api/v1` 做 breaking change（字段删除/枚举收缩）。

**MUST NOT（禁止事项）：**
1. **MUST NOT** 直接修改 `gen_doc_facts.py` 的派生事实输出（如文档中的 `<!-- FACT: ... -->` 块）；**MUST** 修改输入源 + 重跑脚本。
2. **MUST NOT** 在 migration 文件中省略 `down_revision`；**MUST NOT** 以 `down_revision = None` 创建新 base，只能有 1 个 base。
3. **MUST NOT** 三仓版本号「各自独立演进」；monorepo 版本 MUST 统一，避免前端 `v1.1.0` 搭配后端 `v1.0.3` 这种漂移。
4. **MUST NOT** PATCH 版本新增功能；所有新增功能 MUST 走 MINOR 或 MAJOR。
5. **MUST NOT** 手动删改 migration 文件后不清 Alembic 历史；如果必须回滚 MUST 使用 `alembic downgrade` 而非删除文件。
6. **MUST NOT** 在 CI 流水线「绕过」`gen_doc_facts.py` 检查；发布分支合入前 MUST 通过。

**SHOULD（建议事项）：**
1. **SHOULD** 每次 MINOR/MAJOR 升级时，在 CHANGELOG.md 增加对应「版本发布块」并附变更摘要；PATCH 版本 SHOULD 追加在同版本块末尾。
2. **SHOULD** Alembic 迁移在提交前跑 `alembic check` 与目标库 schema 0 diff；防止 head 一致但实际 schema 漂移。
3. **SHOULD** 依赖升级前锁定大版本；避免跨大版本（如 `sqlalchemy 1.4 → 2.0`）无回归直上。
4. **SHOULD** PR 描述附 `gen_doc_facts.py` diff 片段；便于 CR reviewer 一眼验证对齐状态。

**MAY（可选配置）：**
1. **MAY** 在开发分支临时把版本号升为 `MAJOR.MINOR.PATCH-dev`（如 `1.0.2-dev`），但发布前 MUST 改为正式号。
2. **MAY** 引入 `release-please` / `changesets` 等自动化发布工具；但 MUST 保留后端 `pyproject.toml` 为唯一版本源，不引入双源。

### 2.4 自检 CheckList

- [ ] 版本三源：`pyproject.toml`、`package.json`、`app/__init__.py`、文档头一致；`make gen-doc-facts` 0 diff
- [ ] Alembic：`alembic heads` 仅 1 条；`alembic check` 与目标 DB schema 0 diff
- [ ] 语义化：MAJOR/MINOR/PATCH 语义正确；无 4 段/日期版本
- [ ] 锁文件：通过包管理器升级；无手工改动痕迹
- [ ] `/api/v1` 契约：breaking change 未出现在同 MAJOR 版本内

---

## 3. 通用安全红线 + 跨仓 DDD 分层约束

### 3.1 概述（一句话定位）

本节收录「三仓都需要遵守的通用安全铁律」和「跨仓 DDD 分层协作不变量」。具体实现级安全约束（鉴权细节、密钥算法、存储方案、前端 BFF、端侧 token）的权威以各 `-02-Sec.md` 为准；本文档只定义跨仓共享的底线约束，避免各 Sec 重复表述。

### 3.2 红线与分层清单

| 类别 | 通用红线 / 分层不变量 | 权威实现文档 |
|---|---|---|
| **KEY-01 无硬编码密钥** | 密钥/凭证/secret **禁止硬编码进代码/配置文件**；仅存环境变量 `.env` 或外部密钥管理器 | 各仓 `.env.example` + BackSec §4 |
| **LOG-01 日志禁记 PII** | 日志/埋点/错误上报禁止记录：密码、token、TOTP、手机号、邮箱、身份证号；生产日志 MUST 脱敏 | BackSec §1 / FrontSec §5 / MobileSec §1 N6 |
| **DB-01 SQL 参数化** | 禁止字符串拼接 SQL；数据库访问 MUST 参数化（SQLAlchemy ORM / Core）| BackSec §1 |
| **RBAC-01 后端 enforce** | 权限校验 **必须在后端 enforce**；前端/移动端 UI 隐藏 ≠ 权限校验，仅作 UX 提示 | BackSec §1 / FrontSec §3 / MobileSec §2 E 越权 |
| **TLS-01 全链路 HTTPS** | 南北向生产 MUST HTTPS（TLS 1.2+）；禁止 HTTP 明文；本地开发 127 除外 | BackSec §3 / FrontSec §1 / MobileSec §3 |
| **DDD-01 后端 DDD 分层** | `api → services → repositories → models → schemas → core`；禁止跨层跳过 | BackDoc-01-Arch §3.1.2 |
| **DDD-02 前端契约层** | `src/lib/api/` = 契约唯一收口；业务组件禁止直接 `fetch('/api/v1/...')`；BFF 禁止自定义 DTO | FrontDoc-01-Arch §3 / BackDoc-ModuleContracts Part B |
| **DDD-03 移动端 ApiClient** | `shared/api/client.ts` = 唯一收口；业务页面禁止直接 uni.request / wx.request | MobileDoc-01-Arch §3 / MobileSec §1 N2 |
| **DDD-04 模块间隔离** | 后端禁止模块 A 直接 import 模块 B 的 ORM Session 私有内部实现；仅允许 services 层互调或 event bus 解耦 | BackDoc-ModuleContracts |

### 3.3 约束（RFC2119 分层）

**MUST（铁律红线）：**
1. **KEY-01 MUST**：密钥/凭证（`SECRET_KEY`、`DB_PASSWORD`、`GITHUB_CLIENT_SECRET`、微信 `AppSecret`、LANGSMITH_API_KEY、任意 OAuth secret）**MUST** 仅存储在 `.env`（本地）/ CI secrets / Vault（生产）；**MUST NOT** 进入 Git、CI 日志明文、发布包。
2. **LOG-01 MUST**：所有日志输出（`print`/`logger.info`/`console.log`/`uni.showToast`/全局错误上报）**MUST** 脱敏，禁止密码、token、TOTP、手机、邮箱、身份证、openid、unionid、API key 明文。
3. **DB-01 MUST**：数据库访问 **MUST** 参数化；**MUST NOT** 字符串拼接 SQL（`f"SELECT * FROM users WHERE id={uid}"` 这类格式禁止）。
4. **RBAC-01 MUST**：所有写操作 + 敏感读操作 **MUST** 后端执行 `require_permission()` / 资源归属校验；**MUST NOT** 认为「前端隐藏按钮 = 权限校验通过」。
5. **TLS-01 MUST**：生产部署南北向 **MUST** HTTPS；**MUST NOT** 80 端口明文（本地 127.0.0.1 除外）。
6. **DDD-01 MUST**：后端 DDD 分层 MUST `api → services → repositories → models`；`api` 层 **MUST NOT** 直接 `db.execute()` 绕过 services + repositories。
7. **DDD-02 MUST**：前端业务组件 **MUST** 通过 `src/lib/api/{domain}.ts` 契约层或 BFF 路由发起请求；**MUST NOT** 组件内 `fetch('/api/v1/...')` 直连后端。
8. **DDD-03 MUST**：移动端业务页面 **MUST** 通过 `shared/api/client.ts` ApiClient + domain 文件；**MUST NOT** 页面直接 `uni.request` / `wx.request` / 硬编码后端地址。
9. **DDD-04 MUST**：模块 A 访问模块 B 的数据 **MUST** 通过 B 的 services 公开接口或 event bus；**MUST NOT** 直接 import B 的 repositories / models 私有内部实现。

**MUST NOT（禁止事项）：**
1. **MUST NOT** 在注释、README、PR 描述、CHANGELOG 中粘贴任何真实 secret / token / key；若示例需要 MUST 使用占位符 `***` 或 `"your-api-key"`。
2. **MUST NOT** 前端/移动端「自行实现登录态校验」替代后端 `/auth/me`；会话有效 **MUST** 由后端权威判断。
3. **MUST NOT** 前端 BFF 层「自定义 DTO」与后端 schema 不一致；BFF **MUST** 原样透传后端响应字段（snake_case），仅在前端契约层统一转 camelCase。
4. **MUST NOT** 后端 `schemas.py` DTO 直接复用 `models.py` ORM 对象到响应；**MUST** 使用 `model_validate` / DTO 白名单控制暴露字段。
5. **MUST NOT** 移动端直接访问数据库（O4 铁律）；即使 uni-app 支持 SQLite，MVP **MUST NOT** 引入。
6. **MUST NOT** 跨仓共享 `SECRET_KEY` 或 JWT 签名密钥的任何多份副本；唯一权威 = 后端 `.env`。
7. **MUST NOT** 在 BFF / 移动端 / 前端 以任何形式复制「权限判断逻辑」副本（如本地 `if user.role == 'admin'` 允许展示 = OK，但禁止用于数据层过滤/准入判断）。
8. **MUST NOT** 三仓内不同模块使用不同加密哈希算法（bcrypt / PBKDF2 / md5 混杂）；**MUST** 统一：密码 = bcrypt、TOTP seed = AES-GCM、JWT = 标准库。

**SHOULD（建议事项）：**
1. **SHOULD** CI 跑 `gitleaks` / `trufflehog` 扫描历史提交（含 PR 增量），一旦检出 secret MUST 阻断 + 通知密钥持有者立即轮换。
2. **SHOULD** 后端 DDD 模块各自独立 `pyproject.toml` 依赖组（可选），避免模块 A 依赖模块 B 的私有依赖版本；目前单仓通过「services 层接口」隔离足够。
3. **SHOULD** 前端/移动端请求异常 MUST 统一到 `ClientError`（code/message/retryable/source）四字段；禁止把堆栈/SQL/内部路径暴露到 UI。
4. **SHOULD** 三仓都在 Makefile 提供统一 lint/typecheck/test 入口；便于 `make ci` 全链路检查。

**MAY（可选配置）：**
1. **MAY** 引入 `pre-commit-hook` 跑 `gitleaks` 本地增量扫描；CI MUST 也跑一遍避免本地关闭 hook 绕过。
2. **MAY** 完整版引入 event bus（NATS / Redis Pub/Sub）替代模块间 services 互调，进一步解耦；MVP MUST 保持 services 直调最简。

### 3.4 自检 CheckList

- [ ] KEY-01：三仓 + CI 日志 grep 0 命中真实 secret；代码中只有 `os.getenv` 读取
- [ ] LOG-01：三仓日志输出 0 明文 token/密码/手机/邮箱
- [ ] DB-01：后端 0 处字符串拼接 SQL；全部 ORM / Core 参数化
- [ ] RBAC-01：所有写操作 + 敏感读 后端 require_permission 100%；前端 UI 隐藏仅作 UX
- [ ] TLS-01：生产部署 Nginx/Caddy 强制 HTTPS + HSTS；80 重定向 443
- [ ] DDD 分层：后端 0 处 api→db 直连；前端 0 处组件直 fetch；移动端 0 处页面直 request
- [ ] 模块隔离：模块间互调仅经 services 公开接口或 event bus；0 处跨模块 import repositories/models

---

## 4. Makefile 收敛 + 提交规范（Conventional Commits）

### 4.1 概述（一句话定位）

FztbuCS monorepo 三仓 MUST 提供统一入口 `Makefile`；根仓再汇总成「一键级联调用」。本节定义收敛目标、入口对齐清单、以及 Git 提交消息的 Conventional Commits 规范。所有 CI 流水线 MUST 通过 Makefile 统一入口驱动，避免各仓脚本漂移。

### 4.2 收敛目标与提交规范清单

#### 4.2.1 Makefile 入口对齐（三仓都 MUST 提供以下 target）

| Makefile target | 功能 | 根仓联动 |
|---|---|---|
| `make init` | 安装依赖 + 环境变量模板 + pre-commit hooks | 根 `make init` = 三仓 `make init` 级联 |
| `make lint` | 代码风格检查（ruff / eslint / 对应 linter） | 根 `make lint` = 三仓 `make lint` 级联 |
| `make typecheck` | 类型检查（mypy / tsc） | 根 `make typecheck` = 三仓级联 |
| `make test` | 单元/集成测试（pytest / vitest / 对应） | 根 `make test` = 三仓级联 |
| `make test-e2e` | E2E / 端到端测试（若存在） | 根 `make test-e2e` = 三仓级联（可选） |
| `make docs-health` | 文档健康检查（死链/占位符/引用一致性） | 根 `make docs-health` = 汇总 + 报告 |
| `make gen-doc-facts` | 派生事实自动同步（版本/迁移/模块契约/测试） | 根 `make gen-doc-facts` = 三仓各跑 + 汇总 diff |
| `make ci` | 全链路 CI：lint → typecheck → test → docs-health → gen-doc-facts | 根 `make ci` = 三仓级联 |
| `make run` / `make dev` | 本地启动（后端 uvicorn / 前端 next dev / 移动对应） | 根 `make run-backend` 等；三仓并行启动按需文档说明 |

#### 4.2.2 提交消息规范：Conventional Commits

| 结构 | 格式 | 说明 |
|---|---|---|
| 基础格式 | `<type>(<scope>): <subject>` | 首字母小写；subject 不超过 72 字符 |
| type 清单 | `feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `build` / `ci` / `chore` / `revert` | 必须选其一；禁止自定义 type |
| scope（可选） | 受影响域：`auth`、`exams`、`mobile`、`frontend-bff`、`ci`、`docs-l0` | |
| Body / Footer | body 空一行 + 多段说明；footer `BREAKING CHANGE: <desc>` 或 `Fixes #123` | BREAKING CHANGE 对应 MAJOR 版本升级 |

### 4.3 约束（RFC2119 分层）

**MUST（铁律红线）：**
1. 三仓 **MUST** 至少提供 4.2.1 表列出的 9 个 target（`test-e2e` MAY 空实现但 target 必须存在，输出「No e2e tests for this repo」）。
2. CI 流水线 **MUST** 通过调用 Makefile target（而非直接 shell 命令）执行 lint/typecheck/test/gen-doc-facts；**MUST NOT** 直接在 `.github/workflows/*.yml` 硬编码 `pytest` / `eslint .` 绕过。
3. `make gen-doc-facts` **MUST** 在发布合入前作为 CI 强制门；**MUST NOT** 「CI 超时而跳过」，超时 MUST 调优脚本而非绕过。
4. `make ci` **MUST** 失败立即阻断合入；**MUST NOT** 允许「已知失败先 merge 后续修」。
5. 提交消息 **MUST** 采用 Conventional Commits 基础格式；**MUST NOT** 「随便写一句」无 type 的 commit（如「修复」「更新」「改了点东西」）。
6. `BREAKING CHANGE:` footer **MUST** 只在 MAJOR 版本升级的 PR 出现；**MUST NOT** MINOR/PATCH 合入引入 breaking change 却不带 footer。
7. pre-commit hooks **MUST** 至少包含：`ruff --fix`（后端）/ `eslint --fix`（前端）+ 代码格式化；提交前本地 **MUST** 跑 `make lint`。

**MUST NOT（禁止事项）：**
1. **MUST NOT** 三仓 Makefile 各自随意扩展 target 命名（如 `make check` 替代 `make lint`）；必须 4.2.1 表统一命名。
2. **MUST NOT** 允许「我本地跑通就行 CI 过不过先 merge」；CI 失败 MUST 本地 `make ci` 复现修完再 push。
3. **MUST NOT** 提交 messages 使用中英文混写（除非 scope 是专有名词）；统一用英文 type/scope，subject 中文/英文任选但 MUST 语义清晰。
4. **MUST NOT** 一个 commit 同时包含多域大改动（如 `feat(auth): add 2FA + fix exams bug + docs update`）；**MUST** 拆 commit 或至少 PR 描述明确拆分。
5. **MUST NOT** 在 Makefile target 内引入交互提示（`read -p "继续吗？"`）；CI 无头环境 MUST 非交互执行。
6. **MUST NOT** `.env` / 密钥文件 / 锁文件 **MUST NOT** 通过 Makefile 直接修改；Makefile 只读（运行、测试、检查），不写用户配置。

**SHOULD（建议事项）：**
1. **SHOULD** 提供 `.pre-commit-config.yaml` 启用 Conventional Commits 校验 hook（commitlint）；避免 CI 才发现格式错。
2. **SHOULD** `make ci` 输出分级摘要（✅ 通过数量 + ❌ 失败数量 + 耗时），便于快速定位失败项。
3. **SHOULD** 根仓 `Makefile` 提供 `make help` 列出所有 target + 简短说明；新成员 `make help` 即可上手。
4. **SHOULD** 提交 PR 时附 `make ci` 本地全绿截图或摘要； reviewer 看到 CI 失败可先让提交人自查本地 `make ci`。

**MAY（可选配置）：**
1. **MAY** 引入 `cz-cli` 交互式 commit 生成；不强求，但提交结果 MUST 最终是 Conventional Commits 格式。
2. MVP 期 **MAY** `test-e2e` target 是 no-op（打印无 e2e 测试），完整版上线前 MUST 补上 Playwright / 对应框架。

### 4.4 自检 CheckList

- [ ] 三仓 Makefile：9 个 target 全部存在；`make -n ci` 0 errors
- [ ] CI workflows：通过 `make <target>` 调用；0 处硬编码 pytest / eslint 命令
- [ ] `make gen-doc-facts`：CI 必跑；发布分支合入前 0 diff
- [ ] 最近 20 条 commit：100% Conventional Commits 格式；0 处「随便写」commit
- [ ] `BREAKING CHANGE:` footer 仅在 MAJOR PR 出现；MINOR/PATCH 0 处
- [ ] pre-commit hooks 已启用（后端 ruff 修复 + 前端 eslint 修复）

---

## 5. 所有权矩阵 + 跨仓反模式

### 5.1 概述（一句话定位）

三仓文档、模块、CI、部署各有 Owner；跨仓协作 MUST 走「对应 Owner CR → 跨仓影响评估 → 变更门禁打钩」流程。本节定义 L0/L1/L2 文档、关键模块、CI/部署、安全红线的 Owner 矩阵，并收录跨仓高频反模式（禁止事项清单），减少「改了后端忘记同步前端」「文档漂移双源」这类协作事故。

### 5.2 所有权矩阵清单

| 类别 | 资产 | Owner（主责） | 协作 Owner（需会签） | 变更触发后 MUST 通知 |
|---|---|---|---|---|
| **L0 根仓文档** | RootDoc-*、README.md、CHANGELOG.md、项目待办v2.md | 3yearsZ（项目主理人） | 三仓 Lead（Back/Front/Mobile Lead） | 全员（README / CHANGELOG 公告） |
| **L1 架构文档** | BackDoc-01-Arch、FrontDoc-01-Arch、MobileDoc-01-Arch、RootDoc-FEArch | 对应子仓 Lead | 3yearsZ + 跨端接口受影响方 | 对应子仓频道 + 主理人 |
| **L2 子仓专题** | BackDoc-02-Sec / -03-Conv、FrontDoc-02-Sec / -03-Conv、MobileDoc-02-Sec / -03-Conv | 对应子仓 Lead | 安全 Owner（BackOwner 代全栈）+ 受影响方 | 子仓频道 |
| **G 级深层设计** | arch/ 目录 G1~G5（移动端）、Backend Arch Part B 模块契约 | 对应原作者 | 对应子仓 Lead + 3yearsZ | 子仓频道 + 主理人 |
| **关键模块（后端）** | `app/auth`（认证/鉴权/RBAC）、`app/core`（配置/异常/安全/限流）、Alembic 迁移链、`app/services/auxilio_agent.py` | Backend Lead | 3yearsZ + Security Owner | 后端频道 + 主理人 |
| **关键模块（前端）** | `server/bff.ts`（BFF 转发 + Zod）、`middleware.ts`（路由保护）、`src/lib/api/`（契约层）、AuthProvider | Frontend Lead | 3yearsZ + Backend Lead（契约对齐） | 前端频道 + 后端 Lead |
| **关键模块（移动）** | `shared/api/client.ts`（ApiClient）、`shared/utils/storage.ts`（安全存储）、条件编译分支、`manifest.json` | Mobile Lead | 3yearsZ + Backend Lead（契约对齐） | 移动频道 + 后端 Lead |
| **CI / 发布 / 部署** | `.github/workflows/*`、根 `Makefile` 级联、Dockerfile、Nginx/Caddy 反向代理、Compose 编排 | DevOps/3yearsZ | 三仓 Lead（受影响） + Security Owner（密钥相关） | 全员频道 |
| **密钥/安全配置** | `.env.example`、`.env.*` 模板、CI secrets、生产 Vault 密钥名 | Security Owner（Backend Lead 代） | 3yearsZ + DevOps | 仅主理人 + DevOps（最小知） |
| **审计日志 / 合规** | `admin_actions`、`login_history` 表结构；埋点字段；GDPR/最小必要字段 | Backend Lead + 3yearsZ | 合规联系人（若有） | 后端频道 + 主理人 |

### 5.3 约束（RFC2119 分层）

**MUST（铁律红线）：**
1. **Owner 变更前置 CR**：任何属于上表「关键模块 / 关键文档」的变更 **MUST** 对应 Owner 审批后才合入；**MUST NOT** 跨模块 PR 跳过 Owner review。
2. **跨仓影响评估 3 问**：若变更涉及 `/api/v1` 契约、资源域命名、Alembic 迁移、枚举、通用安全红线 **MUST** 在 PR 描述回答 3 问：① 是否影响三仓？② 需要同步改哪些文档/模块？③ 发布顺序（迁移 → 后端 → BFF → 前端/移动）；**MUST NOT** 留空。
3. **Double-source 禁止**：任何事实（版本号、枚举、权限、模块契约、文档引用）**MUST** 只有一个权威源；**MUST NOT** 两处同时维护（例：禁止 README 同时写版本号 + pyproject.toml；禁止前端本地重定义枚举）。
4. **反向引用唯一权威**：文档间引用 **MUST** 指到 L0/L1/L2 对应权威文档；**MUST NOT** 直接引用代码行号、commit SHA、临时截图作为「规范来源」。
5. **PR 拆分原则**：跨仓大变更 **MUST** 拆为 3+ PR（后端先 → BFF → 前端/移动 → 文档）；**MUST NOT** 一 PR 改三仓导致回滚困难。
6. **回滚预案**：若 PR 涉及 breaking change 或 DB migration **MUST** 在 PR 描述附「如何回滚」（`alembic downgrade -1`、回滚 commit、功能开关）；**MUST NOT** 无回滚预案直合 main。
7. **安全 Owner 一票否决**：密钥/鉴权/限流/审计日志类变更 **MUST** 安全 Owner 会签；安全 Owner **MUST** 有权一票否决高风险变更。
8. **变更最小化**：每次 PR **MUST** 聚焦单个逻辑单元；**MUST NOT** 在同一 PR 中「fix bug + refactor + add feature + update docs」混合提交（便于回滚）。

**MUST NOT（禁止事项）：**
1. **MUST NOT** 直接 push 到 main / master（除非 hotfix 经主理人 + Owner 双签）；所有变更 MUST 走 PR → CR → CI → merge。
2. **MUST NOT** 以「临时方案先上，以后再改」心态合入代码；临时方案 MUST 附明确 TODO + issue 追踪，且不破坏现有约束。
3. **MUST NOT** 在不通知受影响 Owner 的情况下修改他人负责模块的「公共接口」（services 公开方法、DTO、枚举、路由前缀）。
4. **MUST NOT** 引入「双重标准」：某条通用安全红线在后端遵守、前端/移动端不遵守（例：后端日志脱敏、前端却 console.log(token)）。
5. **MUST NOT** 「为了快」绕过 CI / pre-commit / 门禁合入；效率让步于质量与安全。
6. **MUST NOT** 发布版本后未同步更新 CHANGELOG.md / RootDoc-Catalog.md / 派生事实；版本发布 MUST 配套所有派生事实同步。
7. **MUST NOT** 同一功能模块的接口文档、实现代码、测试代码分布在 3 个互不相关的目录；按「资源域聚合」就近放置。

**SHOULD（建议事项）：**
1. **SHOULD** 每个 PR 附「影响矩阵」表格：哪些模块/文档/部署受影响、对应 Owner 是否会签通过；便于 reviewer 一眼全览。
2. **SHOULD** 每周项目例会同步「变更后仍未解决的 Double-source」与「跨仓漂移告警」（通过 `make docs-health` 输出）。
3. **SHOULD** 关键模块 Owner 离职/换岗时 MUST 明确交接文档 + 权限（Git、CI secrets、生产密钥访问）；避免无人维护。
4. **SHOULD** 引入 CODEOWNERS 文件（GitHub/GitLab）自动按路径分配 reviewer；减少「忘记 @Owner」导致的漏审。
5. **SHOULD** 安全 Owner 每月一次轻量安全巡检：密钥检查、审计缺失、权限漂移、Alembic 分支、未关闭的高危 issue。

**MAY（可选配置）：**
1. **MAY** 小型变更（文档 typo、UI 样式不影响契约）**MAY** 单仓 Lead 自审自合；但仍需 `make ci` 通过。
2. **MAY** 引入 feature flag（功能开关）对大功能灰度上线；降低 breaking change 风险，但 feature flag MUST 配套「清理计划」（几个版本内移除）。

### 5.4 自检 CheckList

- [ ] 所有权矩阵：关键模块 / 关键文档 / 密钥 / CI 均有明确 Owner；无无人负责项
- [ ] 近 10 条 PR：对应 Owner 审批通过；跨仓 PR 回答了 3 问 + 发布顺序
- [ ] Double-source：`make gen-doc-facts` 0 diff；`make docs-health` 0 条引用漂移
- [ ] PR 拆分：跨仓变更拆 ≥3 PR（后端→BFF→前端/移动→文档），无「一 PR 改三仓」
- [ ] Breaking change / Alembic migration PR：附回滚预案
- [ ] CODEOWNERS（若启用）路径匹配 Owner 矩阵；自动分配 reviewer 生效
- [ ] 近月安全巡检：有记录；密钥/权限/Alembic/审计未关闭高危项已处理

---

## 6. 变更门禁 + Pre-commit 必查清单（Reference 型文档强制尾章）

> 每次提交涉及命名门禁、版本/Alembic、通用安全、DDD 分层、Makefile、跨仓协作的任何变更前，提交人 MUST 逐项自查并在 PR 描述打钩；CR 审核人 MUST 核对并在未打钩时打回。

### §6.1 通用门禁（所有跨仓变更适用）

- [ ] 变更是否影响 §1–§5 任一 MUST/MUST NOT 约束？若是本节约束文字 MUST 已同步更新
- [ ] `make ci`（lint + typecheck + test + docs-health + gen-doc-facts）本地全绿；CI 失败 MUST 先本地复现修复
- [ ] 6 行元数据头：版本号、变更日期已同步更新（若改动文档本身）
- [ ] 三仓版本三源：`make gen-doc-facts` 0 diff；无派生事实漂移
- [ ] 跨仓影响 3 问已回答：① 是否影响三仓？② 同步改哪些？③ 发布顺序？

### §6.2 命名门禁（§1 相关）

- [ ] 新模块/新域：RootDoc-ModuleMap.md 8 项登记完成；RootDoc-Catalog.md 新文档已登记
- [ ] 术语：代码/文档 grep 0 处术语不一致；`association` / `exam` / `post` 统一
- [ ] `/api/v1` 冻结契约：三端路径/字段/枚举 100% 对齐；无 breaking change
- [ ] 数据库对象：蛇形规范检查；无 PascalCase / 缩写 / 单复数混乱
- [ ] 文档位置：子仓文档在 `<Repo>/tools/docs/`；根 docs 仅 L0 + 索引

### §6.3 版本 + Alembic 门禁（§2 相关）

- [ ] 版本升级：仅改后端 `pyproject.toml`；其他三处由脚本派生；版本语义 SemVer 正确
- [ ] Alembic：`alembic heads` 仅 1 条；`alembic check` 0 diff；迁移归属 domain 标注齐全
- [ ] 锁文件：通过包管理器升级；无手工编辑
- [ ] CHANGELOG.md：MINOR/MAJOR 版本有对应发布块

### §6.4 安全 + DDD 门禁（§3 相关）

- [ ] KEY-01：三仓 + CI 日志 0 真实 secret；gitleaks（若启用）无告警
- [ ] LOG-01：0 明文 token/密码/手机/邮箱
- [ ] DB-01：0 字符串拼接 SQL；RBAC-01：写 + 敏感读后端 enforce 100%
- [ ] DDD 分层：后端 api→services→repositories→models；前端契约层收口；移动端 ApiClient 收口；0 处跨层/直连
- [ ] TLS-01：生产部署 HTTPS + HSTS；80→443 重定向

### §6.5 Makefile + 提交门禁（§4 相关）

- [ ] 三仓 Makefile 9 target 全部存在；命名与 §4.2.1 表完全对齐
- [ ] CI workflows 仅调用 Makefile target；0 处硬编码命令
- [ ] 近 20 commit：100% Conventional Commits；breaking change 仅在 MAJOR
- [ ] pre-commit hooks 启用；`make lint` 本地 0 errors

### §6.6 所有权 + 反模式门禁（§5 相关）

- [ ] 关键模块/文档变更：对应 Owner review 通过；安全变更 Security Owner 会签
- [ ] 跨仓大变更拆 ≥3 PR；回滚预案齐全（break change / Alembic）
- [ ] Double-source：`gen-doc_facts.py` + `docs-health` 0 漂移；0 处双源维护
- [ ] PR 最小化：单 PR 单逻辑单元；无 fix+refactor+feature 混合
- [ ] CODEOWNERS 生效；无漏审关键路径

---

> ↩ **返回根仓方法论总览**：[README.md](../README.md) · **完整资源域命名门禁**：[RootDoc-ModuleMap.md](./RootDoc-ModuleMap.md) · **后端约定实现**：[BackDoc-03-Conv.md](../CS-Web-Backend/tools/docs/BackDoc-03-Conv.md) · **前端约定实现**：[FrontDoc-03-Conv.md](../CS-Web-Frontend/tools/docs/FrontDoc-03-Conv.md) · **移动端约定实现**：[MobileDoc-03-Conv.md](../CS-Mobile/tools/docs/MobileDoc-03-Conv.md)
