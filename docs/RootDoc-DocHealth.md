# 文档结构健康诊断与合并方案（RootDoc-DocHealth）

> 更新人：3yearsZ
> 最后更新：2026-08-20
> 目标：诊断现有文档体系的四类结构性问题（**重复 / 过度引用 / 分散 / 失准**），给出逆向目标结构与合并/瘦身方案，供决策后执行。**本报告仅诊断不改动文件。**
> 方法：逆向目标结构 → 聚焦高发区（根 `docs/` + 前端 `tools/docs/` + 跨仓索引）取证 → 评估是否需全量。
> 结论：聚焦取证已覆盖系统性问题，**无需全量遍历**（全量多为同类重复）。

---

## 一、结论速览

| 维度 | 严重度 | 核心问题 |
|---|---|---|
| 失准 | **高** | 全线文档版本锚定停滞在 **0.9.8**（实际已 1.0.1·七夕）；存在未决占位符 `[待填写]`；个别 "0.9.x 尚未进入 1.0" 表述与事实冲突 |
| 重复 | 高 | 前端 UI 三件套（UID / UIStandard / UIButton）按钮内容三重重叠；版本号/组件清单/错误码等多处散写 |
| 过度引用 | 中-高 | 每文档头部 4~8 个"关联/权威见"链接；"XX已迁移至YY"指针式文档；索引套索引导致读者连环跳转 |
| 分散 | 中 | 前端 `tools/docs/` 10 篇；根 `docs/` ~15 篇；多个单主题小文档/纯指路文档 |

处置建议：**先修失准（低成本高价值）→ 再合并前端 UI 三件套（消除重复）→ 收敛指路式引用 → 保留已经不散的端侧文档**。

---

## 二、失准证据（与项目实际不符）

**版本锚定全线停滞在 0.9.8**（当前实际 **1.0.1·七夕，2026-08-19 发布**）：

| 文档 | 失准表述 | 位置 |
|---|---|---|
| 根 `README.md` | 「当前语义版本线：0.9.x（尚未进入 1.0.0）」 | [README.md](README.md#L107) |
| 根 `README.md` | 「以下能力在 0.9.8 中已具备」 | README.md L26 |
| `RootDoc-Deploy.md` | 全文多处锚定「0.9.8」，最后更新 2026-08-08；`对应版本：0.9.8` | [RootDoc-Deploy.md](RootDoc-Deploy.md#L4-L5) |
| `RootDoc-MigEval.md` | 章节标题「0.9.8 补录，2026-08-08」 | RootDoc-MigEval.md L180 |
| `BackDoc-01-Arch` / `Conv` / `Infra` | 最后更新 2026-08-08、锚定 v0.9.8；`BackDoc-Infra` 断言「Alembic 单一 head `d3e4f5a6b7c8`」与后续新增迁移冲突 | [BackDoc-Infra.md](../CS-Web-Backend/tools/docs/BackDoc-Infra.md) |
| `Onboarding.md` | 「截至 0.9.8，api-usage-stats 尚未注册」+ `[待填写：确认是否随 1.0.0 注册]` | [Onboarding.md](Onboarding.md) |
| `FrontDoc-Ops` / `02-Sec` / `i18n` | 最后更新 2026-08-05，落后于 2026-08-19/20 的工作台/契约变更 | — |

**未决占位符**：`BackDoc-Infra.md`「表总数精确值 [待填写]」；`Onboarding.md` `[待填写：…]` —— 属未完成内容，不应出现在权威文档正文。

> 间接佐证：移动端归档 `arch/material_digest.md` §3 X1 已自行标注「0.9.8准备期 vs 1.0.0已发布 的版本状态表述冲突」，说明该问题是体系性的。

## 三、重复证据

- **前端 UI 三件套重叠**：`FrontDoc-UID.md`（UI 设计规范主文档）+ `FrontDoc-UIStandard.md`（「按钮/输入框/徽章/Tab/分页/Modal/z-index 唯一权威」SSOT）+ `FrontDoc-UIButton.md`（按钮审计与迁移史）——**按钮**的变体、尺寸、禁止项、审计统计在三份中均有承载，指向解耦并未消除重复，只是把重复从正文转成了跨文档依赖。
- **高频事实多处散写**：版本号（以上四处）、SLO（Deploy/Ops/Arch 各提）、组件清单（UID/UIStandard/前端 modules README/Arch）、错误码体系（移动端 Arch/系统设计 与后端）——靠"单一事实源+引用"约束，实际产生大量指路语句而非收敛。

## 四、过度引用证据

- 每篇头部「关联：…」普遍 4~8 个链接（如 `FrontDoc-01-Arch`、`BackDoc-02-Sec`、`README.md` 头部）。
- 指路式语句高密度：`Onboarding.md` 附录把禁止事项拆成「→ 见 FrontDoc-03-Conv §12 / FrontDoc-UID §11」；`FrontDoc-i18n.md` / `Ops.md` 内多行「剩余待迁移清单已迁移至 `docs/项目待办v2.md`」——读者要拼凑一个完整事实需跨 3~5 篇。
- README 治理规范的「所有权矩阵」本身鼓励"只引用、不重述"，副作用是**引用攀高**。

## 五、分散证据

- 前端 `tools/docs/`：10 篇（01-Arch / 02-Sec / Conv / UID / UIStandard / UIButton / Ops / i18n / Workbench-ReviewPrompt / capsule-tabs + README）。
- 根 `docs/`：~15 篇，含调研报告、临时评估、纯索引等。
- 单主题小文档：`capsule-tabs.md`（Tab 配置数据）、`FrontDoc-i18n.md`（迁移指南）、`FrontDoc-Workbench-ReviewPrompt.md`（prompt 模板）——各自为一主题成型，贡献了碎片数。

## 六、逆向目标结构（靶子）

目标：**每仓极少数权威文档，每篇自包含核心事实，读者打开即用，不被连环跳转绑架。**

| 仓 | 现状 | 目标 |
|---|---|---|
| 根 `docs/` | ~15 篇 | **6–8 篇**：README(索引)、Onboarding(入口，修失准)、RootDoc-EngConv(通用规范SSOT)、RootDoc-Deploy(部署)、CHANGELOG*(记录) + RootDoc-ADR(决策索引)、README 治理规范(治理)，保留 ModuleMap/待办两种特殊 SSOT；调研/评估/碎片合并或归档 |
| 前端 `tools/docs/` | 10 篇 | **4–5 篇**：01-Arch、Conv(并入 i18n/Ops)、UID(合并 UIStandard/UIButton)、02-Sec、capsule-tabs(或并入 Conv) |
| 后端 `tools/docs/` | 5 篇 | 基本健康，仅更新失准、回填 `[待填写]` |
| 移动端 `tools/docs/` | 3 篇 + arch 归档 | 3 篇（刚建，已收敛，不动） |

## 七、合并/瘦身清单与优先级

| 优先级 | 动作 | 目标文档 |
|---|---|---|
| **P0·修失准** | ✅ 已执行（2026-08-20）：全线版本锚定 0.9.8 → 1.0.1；清 `[待填写]`；校正 Alembic head 至 `e5f6a7b8c9d0` | 根 README、Deploy、MigEval、Onboarding、后端 BackDoc-* |
| **P1·合并前端 UI** | ✅ 已执行（2026-08-20）：UIButton+UID+UIStandard 并入单一 `FrontDoc-UID.md`（UIButton 审计史并 CHANGELOG；删两篇） | `FrontDoc-UID.md` |
| **P2·收敛指路** | ✅ 已执行（2026-08-20）：i18n 并入 Conv §9、Ops 保留（权衡）；全前端头部「关联」收敛 ≤2；删 `FrontDoc-i18n.md` | Conv、README |
| **P3·归档分散** | ✅ 已执行（2026-08-20）：`capsule-tabs.md` 并入 UID §4.8 并删；`公共组件调研报告.md` 删除（结论已登记）；gen 产物 `api-reference.html` 保留 | 根 docs、前端 docs |
| **跳过** | 后端 5 篇与移动端 3 篇已达收敛形态，不合并 | — |

> **P0–P3 全部落地（2026-08-20）**。收敛效果：前端 `tools/docs/` 由 10 篇降至 **6 篇**；根 `docs/` 由 ~15 篇降至 ~12 篇（删临时评估/调研）；UI 规范收敛为 `FrontDoc-UID.md` 单一权威。剩余健康动作：周期性（发版/每次协议变更时）核对「当前真实进度」版本与 Alembic head，避免再次漂移。

### 7.1 P0 执行明细（2026-08-20）

- 根 `README.md`：版本锚定 L26/L107 → 1.0.1。
- `RootDoc-Deploy.md`：头部 + §2.1/§2.2/§九 锚定 1.0.1；Alembic head 引用校正。
- `RootDoc-MigEval.md`：版本锚定 1.0.1；迁移链 head 更新至 `e5f6a7b8c9d0`（补 `d4e5f6a7b8c9`）；§九 参数卡口径校正。
- `Onboarding.md`：`[待填写]` 占位符闭环（核对 api-usage-stats 未注册）；版本锚定 1.0.1。
- 后端 `BackDoc-Infra.md`：head 校正 + 清 `[待填写]` 表计数；`BackDoc-01-Arch/Conv`：header 版本基线 1.0.1。

> ⚠️ 本报告所涉"合并/归档"均为**建议**，均需逐项授权后执行（遵循本项目"先确认再改动"协作约束）。

## 八、是否全量的结论

聚焦取证结果显示失准/重复为**系统性**（版本全线、UI 三件套），分散/过度引用为**模式性**。全量遍历预期多为同类重复，**收益递减**。建议按 §七 的 P0→P3 分批执行即可，无需全量即席盘点。