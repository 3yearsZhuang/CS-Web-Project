# 文档（根级 · 跨项目/编排层）

> 本目录只放**跨项目 / 编排层**的通用内容与记录，作为全栈仓库的统一文档入口。
> 前后端各自的强相关文档仍留在各自子仓库(submodule) 内（见文末"子仓库文档索引"），实现"统一入口、单一权威、零漂移"。

## 根级文档

| 文档 | 说明 |
|---|---|
| [RootDoc-FEArch.md](RootDoc-FEArch.md) | 前端目录/架构方法论（以 CS-Web-Frontend 真实结构为锚，唯一权威） |
| [RootDoc-EngConv.md](RootDoc-EngConv.md) | 通用工程规范（命名 / DRY / 圈复杂度 / 错误处理 / 安全 / 配置 / 测试 / Git / 中文排版） |
| [RootDoc-Deploy.md](RootDoc-Deploy.md) | 全栈部署 / 运维（本地并行启动、容器化部署、健康检查、回滚、数据卷） |
| [RootDoc-MigEval.md](RootDoc-MigEval.md) | 迁移可行性 + 多数据库支持评估报告 |
| [RootDoc-ADR.md](RootDoc-ADR.md) | 架构决策（ADR）索引 / 边界上下文 / 数据流 / 韧性 / BFF 交互风格（设计决策 SSOT，L0） |
| [Onboarding.md](Onboarding.md) | 新开发者/新管理员第一天教程（环境→本地→部署→排障，含「当前真实进度」标注） |
| [CHANGELOG.md](../CHANGELOG.md) | 全项目变更记录唯一权威（Keep a Changelog 格式，覆盖 `[Unreleased]` → `[0.9.1]`；2026-08-17 起并入原 `项目演变历史.md` 全量内容并删除该文件；跨项目版本锚点以此为准） |
| [api-reference.html](api-reference.html) | API 参考（ReDoc 查看器，由 `openapi.baseline.json` 经 `make gen-api-docs` 生成，请勿手改；入口说明见 [api-reference.md](api-reference.md)） |
| [项目待办v2.md](项目待办v2.md) | 项目待办 / 进行中事项 + ADR 待评估项存放处（与 `RootDoc-ADR.md` 索引联动；2026-08-18 起原 `项目待办事项.md` 并入本文件） |
| [RootDoc-ModuleMap.md](RootDoc-ModuleMap.md) | 三端业务模块 ↔ API 契约映射 SSOT（2026-08-19：命名规范 / 三端落点 / 门禁 / 违约点红线 / 变更记录，配套 `make check-module-naming`；2026-08-20 由 `模块命名映射表.md` 改名） |
| [RootDoc-ICP-Filing.md](RootDoc-ICP-Filing.md) | ICP 备案填报信息（原 `.codebuddy/` 迁入，2026-08-20：服务内容描述 / 基本信息表 / 填报指引） |
| [RootDoc-DocHealth.md](RootDoc-DocHealth.md) | 文档结构健康诊断与合并方案（2026-08-20：重复/过度引用/分散/失准 四维取证 + 逆向目标结构 + P0~P3 合并瘦身清单；含原 DocEval/DupAudit 结论） |

## 子仓库文档索引（原地保留，非迁移）

| 仓库 | 入口 | 内容 |
|---|---|---|
| `CS-Web-Backend/tools/docs/` | [README.md](../CS-Web-Backend/tools/docs/README.md) | 后端 FastAPI 文档索引：`BackDoc-01-Arch.md`（架构 + 业务模块契约 Part B）、`BackDoc-02-Sec.md`（安全）、`BackDoc-03-Conv.md`（工程约定）、`BackDoc-Infra.md`（基础设施） |
| `CS-Web-Frontend/tools/docs/` | [README.md](../CS-Web-Frontend/tools/docs/README.md) | 前端文档：`FrontDoc-01-Arch.md`（架构 + 业务模块契约 Part B + 前后端联动）、`FrontDoc-03-Conv.md`（编码规范，对标后端 BackDoc-03-Conv.md）、`FrontDoc-02-Sec.md`（安全）、`FrontDoc-UID.md`（UI 设计规范 + Markdown 编辑器 §14）、`FrontDoc-Ops.md`（运维）、`FrontDoc-i18n.md`（国际化迁移指南） |
| `CS-Mobile/tools/docs/` | `README.md`（移动端子仓库未在 GitHub 暴露，见本地 `CS-Mobile/tools/docs/`） | 移动端文档：uni-app 单码双端架构/构建、ApiClient 薄层与 token 安全存储、U-02~U-04 依赖；`arch/` 归档 7 份移动端架构方案（高层架构/系统设计/UserStory/部署/安全/调研/资料摘要，G1~G5 审核通过，唯一权威） |

---

## 新增文档登记规范

为避免再次出现文档漂移 / 孤儿文档 / 死链，新增或合并文档时须遵守以下规则：

- **归入位置**：跨项目 / 编排层内容放入根 `docs/`（本目录）；端侧强相关内容放入对应子仓库的 `tools/docs/`（`CS-Web-Backend/tools/docs/` 或 `CS-Web-Frontend/tools/docs/`）。
- **必须登记**：新增文档须在本文档地图 / 索引登记，否则视为孤儿文档，易被死链引用或遗漏。
  - 根级文档 → 上方「根级文档」表；
  - 端侧文档 → 对应子仓库文档索引（如 `CS-Web-Backend/tools/docs/README.md`），根级仅保留入口链接（见「子仓库文档索引」表）。
- **删除 / 合并同步**：任何文档删除或合并须同步更新本文档地图、子仓库文档索引与相关正文引用，避免遗留已失效的文档名。

---

## 信息缺口声明

- **CHANGELOG.md 归属（跨项目版本锚点）**：变更记录与发布说明统一为**根仓 `CHANGELOG.md`**（Keep a Changelog 格式，唯一权威；原 `docs/项目演变历史.md` 已于 2026-08-17 并入本文件并删除）。前端子仓库自 2026-08-17 起不再维护独立 CHANGELOG（薄锚点文件已删除），版本锚点一律以根仓 `CHANGELOG.md` 为准；后端无独立 CHANGELOG 文件，版本同步以 `pyproject.toml` / `app/__init__.py.__version__` / `uv.lock` 为准（详见根 README「版本号单一源」）。

---

## 文档治理规范（Doc Governance）

> 本文档是项目文档的**所有权与引用规则（单一事实源 SSOT）**（2026-08-20 由原 `docs/README.md` 并入本文，该文件已删除）。新增或修改任何文档前，先查下方 §所有权矩阵 与 §反模式清单。本文件本身属 L0 根级治理章节，随本 `README.md` 登记。

### 三层文档架构

| 层 | 位置 | 角色 | 代表文档 |
|----|------|------|----------|
| **L0 项目级** | `docs/` | 跨仓全局唯一权威 | Onboarding(入口)、README(索引)、RootDoc-EngConv(工程约定)、RootDoc-Deploy(部署运维)、RootDoc-MigEval(迁移)、api-reference(契约·生成)、RootDoc-ADR(设计决策) |
| **L1 子仓架构** | `*/tools/docs/*-01-Arch.md` | 各仓唯一权威 | BackDoc-01-Arch、FrontDoc-01-Arch、MobileDoc-01-Arch（架构＋模块契约＋前后端联动） |
| **L2 子仓专题** | `*/tools/docs/*` | 只引用上层、不重述 | *-Sec、*-Conv、FrontDoc-Ops/UID、capsule-tabs、MobileDoc-Sec/Conv |

**引用方向：L2 → L1 → L0，单向。** 禁止反向承载内容（例如 L0 不得把 L1 的架构细节抄过来重述）。

> **移动端前缀规定（2026-08-20 确立）**：CS-Mobile 子仓文档统一前缀为 `MobileDoc-`（如 `MobileDoc-01-Arch.md`、`MobileDoc-02-Sec.md`、`MobileDoc-03-Conv.md`）。当前移动端权威文档仍为 `CS-Mobile/tools/docs/arch/`（G1~G5 审核通过，唯一权威）；`MobileDoc-*` 属**待建**，须以 `arch/` 方案为输入提炼。

### 所有权矩阵（同一主题只在一处定义）

| 主题 | 唯一归属 | 严禁重复出现的位置 |
|------|----------|--------------------|
| 命名 / 质量红线 / 错误处理 / 安全配置 / 测试 / Git 约定 | `RootDoc-EngConv.md` | Onboarding 附录 A、*-Conv 的全量重述 |
| 禁止事项 / 禁止清单 | `RootDoc-EngConv.md`（通用红线）；**前端编码侧→`FrontDoc-03-Conv.md §12`、UI 视觉侧→`FrontDoc-UID.md §11`**（仓内差异） | Onboarding A.1（入口指针，不复述） |
| 防再犯清单（安全教训） | `*-Sec.md`「教训」节 | Onboarding A.7 |
| 架构 / 模块契约 / 前后端联动 | 子仓 `*-01-Arch.md`（L1） | RootDoc-FEArch（仅桥接索引）、根 CHANGELOG.md |
| 迁移可行性 / 执行细节 | `RootDoc-MigEval.md` | 根 CHANGELOG.md、FrontDoc-Ops |
| ADR / 边界上下文 / 数据流图 / 健壮函数 / BFF 交互风格 | `RootDoc-ADR.md`（索引/速查）＋ 根 `CHANGELOG.md`（完整记录）＋ `项目待办v2.md`（待评估） | 原演变历史分卷（活文档不得引用） |
| 安全要点（每模块） | `*-01-Arch.md` 摘要 ＋ `*-Sec.md` 深潜 | — |
| API 契约 | `api-reference.md`（由 `openapi.baseline.json` 生成） | 任何手写重复 |

### 反模式清单（红线）

1. **历史文档不得承载活内容（仅主索引可被活文档引用）**：原 `项目演变历史-0.9.x.md` 等分卷与 `项目演变历史.md` 已于 2026-08-17 全量并入根 `CHANGELOG.md` 并删除；活文档**仅可引用根 `CHANGELOG.md`**；规划长文（工作台改造方案 / 功能模块可见性方案）已于 2026-08-18 归档删除（未完成残余项见 `项目待办v2.md`）。
2. **同一事实只写一次**：定义处写全，其余处只链接，不重述。
3. **跨仓相对链接深度必须正确**：子仓 `tools/docs/` → 根 `docs/` 须 `../../../docs/...`（3 级上溯）；根 `docs/` → 子仓须 `../CS-Web-*/...`（1 级上溯）；子仓 ↔ 子仓须 `../../../CS-Web-*/tools/docs/...`（3 级上溯）。
4. **专题文档（L2）不得重述上层（L0/L1）SSOT**。
5. **新增文档必须登记**到本 `README.md` 索引（见上方「新增文档登记规范」）。
6. **版本号必须四处同步（强制）**：后端 `pyproject.toml` 的 `version`、后端 `app/__init__.py` 的 `__version__`、前端 `package.json` 的 `version`、后端 `uv.lock`（根包）须一致；改版本须四处一起改，任一遗漏即视为缺陷。
7. **术语一致（强制）**：repo 层统一称「子仓库(submodule)」；代码内模块称「子模块 / 模块」；禁止在 repo 层用「子模块」指代子仓库。

> 历史收口：2026-08-09 至 2026-08-18 期间已完成死链修复、ADR 抽离、演变历史并入 CHANGELOG、超大文档导航注入等治理动作，结论沉淀于对应 SSOT；2026-08-20 起治理规范并入本文件。
