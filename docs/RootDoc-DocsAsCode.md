# RootDoc-DocsAsCode｜文档即代码（Docs-as-Code）工程标准（Reference · 文档工程治理 L0 唯一权威）

> 更新人：3yearsZ
> 更新日：2026-08-24
> 版本：1.0.0
> Diátaxis：R（Reference · 回答「是什么」，提供文档工程全流程的事实定义：核心原则、生命周期、Definition of Done、工具链、CI 门禁、生成规则、质量度量；不包含可执行步骤）
> 适用读者：文档作者 / Reviewer / CI 维护者 / 发布负责人 / 文档 Owner
> 变更触发：文档工程流程调整 / 工具链或脚本增减 / CI 文档门禁变更 / 质量度量口径变化

> **SSOT 分工声明**：
> - 本文档是「**文档即代码（Docs-as-Code）工程标准的唯一权威（SSOT）**」——定义文档与代码同等的管理方式：版本控制、评审、CI 门禁、发布、度量。
> - 文档「怎么写」（Diátaxis / Google / Arc42 / RFC 2119 / 6 行元数据头）→ [RootDoc-WritingGuide.md](RootDoc-WritingGuide.md)（Reference）。
> - 文档「健康度诊断与治理行动」→ [RootDoc-DocHealth.md](RootDoc-DocHealth.md)（Explanation）。
> - 跨仓工程约定（版本四源 / 所有权矩阵 / Makefile / Conventional Commits / CI）→ [RootDoc-EngConv.md](RootDoc-EngConv.md)（Reference）。
> - 文档目录与所有权 → [README.md](README.md)（Reference）。

> **治理红线**：
> - MUST NOT 以「纯手写文档」绕过文档 CI 门禁；文档变更 MUST 走与代码相同的 PR → 评审 → CI → 合并流程
> - MUST NOT 手改任何生成类文档（`api-reference.*`、文档内 `<!-- FACT: -->` 派生事实块、前端契约快照）；MUST 修改输入源后重跑生成
> - MUST 在新增/删除文档时同步登记到 README.md 索引与 RootDoc-WritingGuide.md §1.2 分类映射表
> - MUST 每次文档 PR 提交前本地跑 `make check-docs` 且 0 失败；发布前 `make check` 全绿
> - SHOULD 每月执行一次文档健康检查（版本锚定 / 死链 / 引用密度 / 内容重复）

---

## 快速索引

| 章节 | 主题 | 内容 |
|------|------|------|
| §1 | 核心原则 | 文档=代码的 6 条原则与对应机制 |
| §2 | 文档生命周期 | 创建 → 本地检查 → PR 评审 → CI 门禁 → 合并 → 发布 → 度量 |
| §3 | Definition of Done | 一篇文档「完成」的可检查定义 |
| §4 | 工具链全景 | 脚本 / Makefile target / 检查范围映射 |
| §5 | CI 文档门禁 | 根 CI 中承载的文档相关门禁 |
| §6 | 生成 vs 手写 | 生成类文档清单与只读红线 |
| §7 | 质量度量 | 死链 / 版本 / 契约 / 模块 / 派生事实 口径 |
| §8 | 职责与例外 | 文档 Owner、变更门禁、例外声明 |
| §9 | 自检清单 | 提交前 MUST 逐项核对 |

---

## 1. 核心原则

| # | 原则 | 事实定义 | 对应机制 |
|---|------|----------|----------|
| P1 | 文档是代码 | 文档与源码同库、同 PR、同评审、同 CI、同发布节奏 | 根仓 + 子仓 Git 管理、PR 流程 |
| P2 | 单一事实源 | 每类事实仅一份权威；其余文档只引用不重述 | [RootDoc-WritingGuide.md](RootDoc-WritingGuide.md) §1、[README.md](README.md) 所有权矩阵 |
| P3 | 生成优先 | 可派生事实 MUST 由脚本生成，MUST NOT 手写维护 | `gen_doc_facts.py`、OpenAPI 导出、`make gen-api-docs` |
| P4 | 可自动检查 | 每条规范 MUST 可被脚本或清单检查，禁止「仅靠自觉」 | `scripts/check/*`、根 CI workflow |
| P5 | 度量驱动 | 文档健康度可量化，防止回归 | [RootDoc-DocHealth.md](RootDoc-DocHealth.md)、`make check-docs` |
| P6 | 结构一致 | 元数据头 / Diátaxis / Arc42 / RFC 2119 强制统一 | [RootDoc-WritingGuide.md](RootDoc-WritingGuide.md) L1–L4 |

---

## 2. 文档生命周期

| 阶段 | 动作 | 强制检查项（MUST / SHOULD） |
|------|------|------------------------------|
| 1. 创建 | 确定 Diátaxis 类型 + 6 行元数据头 + 位置 | 元数据 6 行完整且顺序正确；归位正确目录（根 `docs/` 或子仓 `tools/docs/`）；分类映射表登记 |
| 2. 本地检查 | 跑文档自检命令 | `make check-docs` 0 失败；`make gen-doc-facts --dry-run` 派生事实 0 报告项；版本四源一致 |
| 3. PR 评审 | 提交 PR 并附自检清单 | §9 自检清单打钩；Owner review 通过；跨仓变更回答「影响 3 问」（[RootDoc-EngConv.md](RootDoc-EngConv.md) §5.3） |
| 4. CI 门禁 | 根 CI + 子仓 CI 自动执行 | 见 §5；门禁失败 MUST 本地复现修复后重推，MUST NOT 绕过 |
| 5. 合并 | 门禁全绿后合并 | 无「先合并后续修」；单 PR 单逻辑单元 |
| 6. 发布 | 版本 / CHANGELOG / 派生事实同步 | 版本升级仅改后端 `pyproject.toml`，其余脚本派生；CHANGELOG 补发布块 |
| 7. 度量 | 每月文档健康检查 | 版本锚定 / 死链 / 引用密度 / 内容重复四项指标复核 |

---

## 3. Definition of Done（DoD）

一篇文档达到「完成」MUST 满足以下全部可检查项：

- [ ] 6 行元数据头完整且顺序正确（[RootDoc-WritingGuide.md](RootDoc-WritingGuide.md) §1.3）
- [ ] Diátaxis 类型标注正确（T/H/R/E，含 +L3 Arc42 / +L4 RFC 2119 叠加标注）
- [ ] 已登记到 README.md 索引 + RootDoc-WritingGuide.md §1.2 分类映射表
- [ ] 头部引用 ≤ 2；无「指路式引用」连环跳转
- [ ] 未手改任何生成类内容（`<!-- FACT: -->` 块、`api-reference.*`、契约快照）
- [ ] `make check-docs` 本地 0 失败
- [ ] 提交消息符合 Conventional Commits（`docs(...)` type，[RootDoc-EngConv.md](RootDoc-EngConv.md) §4.2.2）
- [ ] 对应 Owner review 通过；跨仓变更已回答「影响 3 问」

---

## 4. 工具链全景

| 脚本 / 目标 | 检查内容 | 调用方式 | 门禁级别 |
|-------------|----------|----------|----------|
| `scripts/doc/gen_doc_facts.py` | 派生事实：Alembic head / 版本四源 / 三端模块↔契约 / 测试存在 | `make gen-doc-facts`（同步）/ `make check-doc-facts`（只查） | 发布门禁 |
| `scripts/check/check_dead_links.py` | 文档内部链接死链审计（ER-09） | `make check-docs-links` | CI 门禁 |
| `scripts/check/check_version_sync.py` | 版本四源一致：`pyproject.toml` / `__init__.py` / `package.json` / `uv.lock`（ER-33） | `make check-version` | CI 门禁 |
| `scripts/check/check_module_naming.py` | 三端业务模块名 ⊆ 契约资源名（P2-9） | `make check-module-naming` | CI 门禁 |
| `scripts/check/check_gitignore_sync.py` | `.gitignore` 公共段一致性（C-8 / N-04） | `make check-gitignore-sync` | 自检 |
| `CS-Web-Backend/tools/scripts/contract/export_openapi.py` | API 契约冻结 / 基线比对（G3 / ER-04） | `make contract-check` / `make contract-baseline` | CI 门禁 |
| 前端契约快照比对 | 前端内嵌 `openapi.baseline.json` 与根基线逐字节一致 | 根 CI diff 步骤 | CI 门禁 |
| `make check` | 全量自检聚合（契约 + 文档 + 边界 + 版本 + 命名 + gitignore） | `make check` | 发布门禁 |

---

## 5. CI 文档门禁

根 `.github/workflows/ci.yml` 的 `cross-repo-gates` job 承载的文档相关门禁：

| 门禁 | 检查内容 | 来源编号 |
|------|----------|----------|
| API 契约冻结 | 后端当前 `/api/v1` 契约 vs 根基线，差异即失败 | G3 / ER-04 |
| 前端契约快照同步 | 前端快照 vs 根基线逐字节一致 | G3 |
| 版本四源一致 | `pyproject.toml` / `__init__.py` / `package.json` / `uv.lock` | ER-33 |
| 文档死链 | 内部链接指向不存在文件即失败 | ER-09 |
| 模块命名对齐 | 三端模块名 ⊆ 契约资源名 | P2-9 |

---

## 6. 生成 vs 手写

| 生成产物 | 生成命令 | 输入源 | 手改红线 |
|----------|----------|--------|----------|
| `docs/api-reference.html` / `api-reference.md` | `make gen-api-docs` | `openapi.baseline.json` | MUST NOT 手改，需更新基线后重生成 |
| 文档内 Alembic head / 版本号锚定 | `make gen-doc-facts` | Alembic 迁移文件 / 后端 `pyproject.toml` | MUST NOT 手改，修改输入源后重跑 |
| 前端 `openapi.baseline.json` 快照 | 根仓基线复制 + `pnpm gen:api-types` | 根基线 | MUST NOT 手改，契约变更走 `contract-baseline` 评审流程 |
| 文档内 `<!-- FACT: ... -->` 派生事实块 | `make gen-doc-facts` | 对应权威输入源 | MUST NOT 手改 |

---

## 7. 质量度量

| 指标 | 口径 | 检查命令 | 目标阈值 |
|------|------|----------|----------|
| 死链数 | 指向不存在文件 / 无效锚点的内链 | `make check-docs-links` | 0 |
| 版本四源漂移 | 四处版本号不一致项 | `make check-version` | 0 |
| 契约漂移 | 当前 OpenAPI vs 冻结基线差异 | `make contract-check` | 0 diff |
| 契约快照漂移 | 根基线 vs 前端快照差异 | 根 CI diff 步骤 | 0 |
| 模块命名越界 | 三端模块名 ∉ 契约资源名 | `make check-module-naming` | 0 |
| 派生事实漂移 | `gen_doc_facts --dry-run` 报告项 | `make check-doc-facts` | 0 |
| 文档健康度 | 版本锚定 / 引用密度 / 内容重复 | 每月人工 + 脚本复核 | 见 [RootDoc-DocHealth.md](RootDoc-DocHealth.md) |

---

## 8. 职责与例外

- 文档 Owner 矩阵：L0/L1/L2 文档、关键模块、CI/发布的 Owner 归属以 [README.md](README.md) 所有权矩阵与 [RootDoc-EngConv.md](RootDoc-EngConv.md) §5 为权威（本文档不重述）。
- 变更门禁：涉及本文档 §1–§7 任一 MUST/MUST NOT 的变更，MUST 同步更新本文档约束文字并走对应 Owner 评审。
- 例外声明：违反本文档任一条 MUST，MUST 在文档头部元数据下方增加「例外声明」块，说明违反条款、技术理由、计划修复时间（[RootDoc-WritingGuide.md](RootDoc-WritingGuide.md) §5.3）。

---

## 9. 自检清单（文档变更时 MUST 逐项核对）

| 检查项 | 说明 |
|--------|------|
| [ ] 6 行元数据头完整且顺序正确 | 更新人 / 更新日 / 版本 / Diátaxis / 适用读者 / 变更触发 |
| [ ] Diátaxis 分类标注正确 | T / H / R / E（+L3 Arc42 / +L4 RFC 2119 叠加） |
| [ ] README.md 索引 + WritingGuide §1.2 分类映射表已登记 | 新增/删除文档 MUST 同步 |
| [ ] 头部引用 ≤ 2；无指路式引用 | 超过则说明文档定位不清 |
| [ ] 无生成类内容手改 | `<!-- FACT: -->` 块、api-reference、契约快照均为只读 |
| [ ] `make check-docs` 本地 0 失败 | 死链 / 派生事实 / 版本四源全绿 |
| [ ] 提交消息 Conventional Commits | `docs(...)` type，subject ≤ 72 字符 |
| [ ] 对应 Owner review 通过 | 跨仓变更已答「影响 3 问」 |

---

> ↩ **返回根级文档地图**：[README.md](README.md) · **文档编写规范**：[RootDoc-WritingGuide.md](RootDoc-WritingGuide.md) · **文档健康治理**：[RootDoc-DocHealth.md](RootDoc-DocHealth.md) · **跨仓工程约定**：[RootDoc-EngConv.md](RootDoc-EngConv.md) · **变更记录**：[CHANGELOG.md](../CHANGELOG.md)
