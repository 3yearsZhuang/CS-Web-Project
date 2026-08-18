# 文档治理规范（Doc Governance）

> 本文件是项目文档的**所有权与引用规则（单一事实源 SSOT）**。新增或修改任何文档前，先查 §2 所有权矩阵与 §3 反模式清单。
> 本文件本身属于 L0（根级）治理文档，由 `docs/README.md` 登记。

## 1. 三层文档架构

| 层 | 位置 | 角色 | 代表文档 |
|----|------|------|----------|
| **L0 项目级** | `docs/` | 跨仓全局唯一权威 | Onboarding(入口)、README(索引)、RootDoc-EngConv(工程约定)、RootDoc-Deploy(部署运维)、RootDoc-MigEval(迁移)、api-reference(契约·生成)、RootDoc-ADR(设计决策) |
| **L1 子仓架构** | `*/tools/docs/*-01-Arch.md` | 各仓唯一权威 | BackDoc-01-Arch、FrontDoc-01-Arch（架构＋模块契约＋前后端联动） |
| **L2 子仓专题** | `*/tools/docs/*` | 只引用上层、不重述 | *-Sec、*-Conv、FrontDoc-Ops/UID/i18n、capsule-tabs |

**引用方向：L2 → L1 → L0，单向。** 禁止反向承载内容（例如 L0 不得把 L1 的架构细节抄过来重述）。

## 2. 所有权矩阵（同一主题只在一处定义）

| 主题 | 唯一归属 | 严禁重复出现的位置 |
|------|----------|--------------------|
| 命名 / 质量红线 / 错误处理 / 安全配置 / 测试 / Git 约定 | `RootDoc-EngConv.md` | Onboarding 附录 A、*-Conv 的全量重述 |
| 禁止事项 / 禁止清单 | `RootDoc-EngConv.md`（通用红线）；**前端编码侧→`FrontDoc-Conv.md §12`、UI 视觉侧→`FrontDoc-UID.md §11`**（仓内差异） | Onboarding A.1（2026-08-09 已改为入口指针，不再复述） |
| 防再犯清单（安全教训） | `*-Sec.md`「教训」节 | Onboarding A.7 |
| 架构 / 模块契约 / 前后端联动 | 子仓 `*-01-Arch.md`（L1） | RootDoc-FEArch（仅桥接索引）、根 CHANGELOG.md |
| 迁移可行性 / 执行细节 | `RootDoc-MigEval.md` | 根 CHANGELOG.md、FrontDoc-Ops |
| ADR / 边界上下文 / 数据流图 / 健壮函数 / BFF 交互风格 | `RootDoc-ADR.md`（索引/速查）＋ 根 `CHANGELOG.md`（完整记录）＋ `项目待办事项-优先级重排.md`（待评估） | 原演变历史分卷（2026-08-17 并入根 CHANGELOG.md；活文档不得引用） |
| 安全要点（每模块） | `*-01-Arch.md` 摘要 ＋ `*-Sec.md` 深潜 | — |
| API 契约 | `api-reference.md`（由 `openapi.baseline.json` 生成） | 任何手写重复 |

## 3. 反模式清单（红线）

1. **历史文档不得承载活内容（仅主索引可被活文档引用）**：原 `项目演变历史-0.9.x.md` 等分卷与 `项目演变历史.md` 已于 2026-08-17 全量并入根 `CHANGELOG.md` 并删除；活文档**仅可引用根 `CHANGELOG.md`**，原 `docs/archive/` 分卷不得再引用；规划长文（工作台改造方案 / 功能模块可见性方案）已于 2026-08-18 归档删除（C-20，落地结论见根 `CHANGELOG.md`，未完成残余项见 `项目待办事项-优先级重排.md`）。
2. **同一事实只写一次**：定义处写全，其余处只链接，不重述。
3. **跨仓相对链接深度必须正确**（当前存在系统性错误，见 §4）：
   - 子仓 `tools/docs/` → 根 `docs/`：`../../../docs/...`（3 级上溯）
   - 根 `docs/` → 子仓：`../CS-Web-*/...`（1 级上溯）
   - 子仓 ↔ 子仓：`../../../CS-Web-*/tools/docs/...`（3 级上溯）
4. **专题文档（L2）不得重述上层（L0/L1）SSOT**。
5. **新增文档必须登记**到 `docs/README.md` 索引（见其「新增文档登记规范」）。
6. **版本号必须四处同步（强制）**：后端 `CS-Web-Backend/pyproject.toml` 的 `version`、后端 `CS-Web-Backend/app/__init__.py` 的 `__version__`、前端 `CS-Web-Frontend/package.json` 的 `version`、后端 `CS-Web-Backend/uv.lock`（根包 `cs-web-backend`）须保持一致；**改版本须四处一起改**，任一遗漏即视为缺陷（发布前自检）。
7. **术语一致（强制）**：repo 层统一称「子仓库(submodule)」；代码内模块称「子模块 / 模块」（仅指代码模块，非 repo）。**禁止在 repo 层用「子模块」指代子仓库**。

## 4. 历史收口记录

> 2026-08-09 至 2026-08-18 期间已完成系统性死链修复、ADR 抽离、禁止事项收敛、演变历史并入根 CHANGELOG、超大文档导航注入等文档治理动作，相关结论均已沉淀于对应 SSOT 文档（`RootDoc-ADR.md` / 根 `CHANGELOG.md` / `项目待办事项-优先级重排.md`）。本文件仅保留现行规则，历史收口明细不再赘述。
