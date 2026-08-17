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
| ADR / 边界上下文 / 数据流图 / 健壮函数 / BFF 交互风格 | `RootDoc-ADR.md`（索引/速查）＋ 根 `CHANGELOG.md`（完整记录）＋ `项目待办事项.md`（待评估） | 原演变历史分卷（2026-08-17 并入根 CHANGELOG.md；活文档不得引用） |
| 安全要点（每模块） | `*-01-Arch.md` 摘要 ＋ `*-Sec.md` 深潜 | — |
| API 契约 | `api-reference.md`（由 `openapi.baseline.json` 生成） | 任何手写重复 |

## 3. 反模式清单（红线）

1. **历史文档不得承载活内容（仅主索引可被活文档引用）**：原 `项目演变历史-0.9.x.md` 等分卷与 `项目演变历史.md` 已于 2026-08-17 全量并入根 `CHANGELOG.md` 并删除；活文档**仅可引用根 `CHANGELOG.md`**，原 `docs/archive/` 分卷不得再引用；规划长文见 `docs/plans/`。
2. **同一事实只写一次**：定义处写全，其余处只链接，不重述。
3. **跨仓相对链接深度必须正确**（当前存在系统性错误，见 §4）：
   - 子仓 `tools/docs/` → 根 `docs/`：`../../../docs/...`（3 级上溯）
   - 根 `docs/` → 子仓：`../CS-Web-*/...`（1 级上溯）
   - 子仓 ↔ 子仓：`../../../CS-Web-*/tools/docs/...`（3 级上溯）
4. **专题文档（L2）不得重述上层（L0/L1）SSOT**。
5. **新增文档必须登记**到 `docs/README.md` 索引（见其「新增文档登记规范」）。
6. **版本号必须四处同步（强制）**：后端 `CS-Web-Backend/pyproject.toml` 的 `version`、后端 `CS-Web-Backend/app/__init__.py` 的 `__version__`、前端 `CS-Web-Frontend/package.json` 的 `version`、后端 `CS-Web-Backend/uv.lock`（根包 `cs-web-backend`）须保持一致；**改版本须四处一起改**，任一遗漏即视为缺陷（发布前自检）。
7. **术语一致（强制）**：repo 层统一称「子仓库(submodule)」；代码内模块称「子模块 / 模块」（仅指代码模块，非 repo）。**禁止在 repo 层用「子模块」指代子仓库**。

## 4. 治理收口待办（非本文件范围，按优先级）

- [x] **系统性跨仓链接深度错误（已完成 2026-08-09）**：全部 13 处死链 + 1 处行内提及已修正（根→子仓 `../CS-Web-*`、子仓→根 `../../../docs/`、子仓↔子仓 `../../../CS-Web-*/tools/docs/`）。重跑死链审计确认 **0 死链**；`../../src/`、`../../.env.example`、`../AGENTS.md` 等同仓正确引用均未被误改。
- [x] 抽离 `演变历史-0.9.1` 中的 ADR 索引 / 边界上下文 / 数据流图 / 健壮函数 / BFF 交互风格 → 新建 `RootDoc-ADR.md`（设计决策 SSOT，2026-08-09 完成；归档对应章节改为指针）。
- [x] 收敛「禁止事项」：`Onboarding.md` 附录 A.1/A.6 改为入口指针（通用红线→`RootDoc-EngConv §二`、前端编码→`FrontDoc-Conv §12`、UI 视觉→`FrontDoc-UID §11`）；`FrontDoc-UID.md` §11 改名「UI 专属禁止清单」仅留 UI 项；`*-Conv` 仅保留仓内差异（2026-08-09 完成）。
- [x] `RootDoc-FEArch.md` 降级为桥接索引（§3.2 项目骨架、§3.4 模块化移除与 `FrontDoc-01-Arch` 重复的目录树 / 模块树，改为指向其 §1.1 / §1.2 的桥接指针；仅沉淀方法论规则），2026-08-09 完成。
- [x] 解除活文档对 `演变历史-0.9.1` 的链接（FrontDoc-Ops / FrontDoc-01-Arch / FrontDoc-02-Sec / RootDoc-MigEval / 前端 README 共 17 处 markdown 链接 + 1 处代码注释/路径引用，已全部改指 `RootDoc-ADR`（ADR 演进 SSOT）/ `RootDoc-MigEval §八`（迁移）；另有 `RootDoc-ADR.md` 自身保留指向归档的指针，作为唯一桥接），2026-08-09 完成。

## 5. 文档结构优化收口（2026-08-09 批次 A，已完成）

- [x] **Onboarding ADR 指针纠偏**：A.4/A.5/A.7 三处原指向被掏空归档 `项目演变历史-0.9.1.md` 的 ADR 指针，改为 → `RootDoc-ADR.md`（L0 索引/速查）+ 根 `CHANGELOG.md`（完整记录）+ `项目待办事项.md`（待评估）。消除"活文档引用只读归档"的红线违反。
- [x] **孤儿文档登记**：`项目待办事项.md`、`FeatureModuleVisibility-Plan.md` 补登 `docs/README.md` 根级表。（FeatureModuleVisibility-Plan.md 已于 2026-08-09 并入 `项目演变历史-0.9.9.md`，2026-08-17 随全量合并抽离至 `docs/plans/功能可见性管理方案.md`）
- [x] **历史引用边界强化**（§2 矩阵 + §3 反模式 #1 改写）：明确活文档**仅可引用变更记录主索引根 `CHANGELOG.md`**，禁止引用已删除的 `docs/archive/` 下 `项目演变历史-0.9.x` 等分卷（2026-08-17 并入根 CHANGELOG.md）；ADR 完整记录归属主索引、待评估项归 `项目待办事项.md`。
- [x] **坏锚点修复**（锚点审计发现）：`BackDoc-Infra.md#六迁移验证`→`#六迁移验证migration_verification`（后端 tools/docs/README、FrontDoc-Ops 共 2 处）、`RootDoc-MigEval.md#八前端迁移执行细节原-frontdoc-pgmigm-…`→`…frontdoc-pgmigmd…`（前端 README），共 3 处。
- [x] **FrontDoc-01-Arch Part B 契约 SSOT 边界**：开头加桥接说明——原始端点契约权威为 `docs/api-reference.md`（自动生成），Part B 仅做模块视图 + BFF 翻译层，不重复罗列原始参数（保留 L1 模块契约权威，未掏空正文）。
- [x] **审计固化**：Skill `monorepo-doc-audit` 新增 `scripts/audit_anchors.py`（锚点腐化审计，已修全角标点 slug 口径）。复跑确认 **0 死链 + 0 坏锚点**。

## 6. 文档结构优化收口（2026-08-09 批次 B，已完成）

- [x] **超大文档章节速查（目录导航）注入**（优化项 #4）：对 5 份 600+ 行的超大文档，用幂等脚本在其首个 `##` 前注入 `## 章节速查（导航）` 块（自动剥离旧块、GitHub slugify 生成锚点、标题去重加 -1/-2），降低长文档跳读成本：
  - `FrontDoc-01-Arch.md`：2 H2 + 97 H3（结构以 H3 为主，H2<5 时条件纳入 H3）。
  - `BackDoc-01-Arch.md`：21 H2。
  - `BackDoc-Infra.md`：7 H2。
  - `FrontDoc-UID.md`：17 H2。
  - `FrontDoc-Ops.md`：17 H2。
- [x] **版本号四处同步约定**（优化项 #6 之一）：新增 §3 反模式 #6——`pyproject.toml` version / `__init__.py` `__version__` / `package.json` version / `uv.lock` 根包须一致，改版本须四处一起改，发布前自检。
- [x] **术语一致约定**（优化项 #6 之一）：新增 §3 反模式 #7——repo 层统一「子仓库(submodule)」，代码内模块用「子模块/模块」，禁止在 repo 层用「子模块」指代子仓库。审计全仓 `子模块`/`子仓库` 用法：未发现 repo 层误用（既有用法均为代码级模块或规则定义本身），故无文件改动，仅固化约定。
- [x] **复跑双审计确认**：注入导航块 + 固化约定后重跑 → **0 死链（235 链接）+ 0 坏锚点（196 锚点）**，全仓文档链路与锚点整洁状态维持。
