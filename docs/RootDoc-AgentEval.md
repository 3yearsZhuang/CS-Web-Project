# RootDoc-AgentEval：Aervox-harness 与 Agent 路线结合评估（Explanation · 评估结论与结合方式）

> 更新人：3yearsZhuang
> 更新日：2026-10-05
> 版本：1.0.2 · Diátaxis E 类，统一解释类文档规范
> Diátaxis：E（Explanation · 回答「能不能结合、以什么方式结合」，提供评估取证与结论；不包含可执行步骤）
> 适用读者：架构师 / Agent 路线实施者；已了解 `docs/项目待办v2.md` 的 AG-P0~P6 规划
> 变更触发：Aervox-harness 重大版本演进 / 结合方式落地（升级为 ADR）/ AG 路线范围调整
> **修订记录**：1.0.2（2026-10-05）——上游 9/14 评估基线后演进 133 提交（AVX-HAR-001 v0.7.0 → v0.7.6）：ADR-021 内核独立与双许可分层、CR-032 裁决器落地深化、CAP-033 授权模型细化、diary 域成型、思隅 CLI 宿主加入；§1/§2/§3.2/§4.1/§5 同步修订。

> **SSOT 分工声明**：
> - 本文档是「**Aervox-harness（思隅）与本项目 Agent 路线结合评估**」的唯一权威（SSOT）。
> - 架构决策索引与演进 → [RootDoc-ADR.md](RootDoc-ADR.md)；AG 待办与状态 → [项目待办v2.md](项目待办v2.md)。
> - 设计落地时的规范输入：Aervox-harness 仓库 `docs/reference/agent-harness-loop.md`（AVX-HAR-001 v0.7，位于本仓库外的本地路径 `~/Documents/Z-Projects/Aervox-harness/`，仓库外文档不纳入死链审计）。
> - 完整评估记录历史 → 根 [CHANGELOG.md](../CHANGELOG.md)。

> **治理红线**：
> - 结合方式一经落地实施（如 MCP Server 交付），MUST 在本文档更新结论状态并在 `RootDoc-ADR.md` 登记为正式 ADR。
> - 引用 Aervox 侧规范/代码 MUST 遵守其许可证边界（代码 AGPL-3.0-or-later；文档 CC BY-NC-SA 4.0，见 §4.1）。

---

## 1. 评估对象与结论

**评估对象**：`~/Documents/Z-Projects/Aervox-harness`（Aervox｜思隅）——同作者（3yearszhuang，373 提交中占 241）的另一个项目：TS 全栈 monorepo（约 10.6 万行），Fastify API + 独立 Worker + Electron 桌宠 + Vue3 Web + Capacitor 壳，SQLite(WAL) 本地单用户真源。"harness" 指 **Agent Harness Loop**：Turn→Attempt→Step 三级执行状态机，带租约/fencing token、崩溃恢复续跑、多步工具循环、事件持久化 SSE 重放。项目仅 23 天（2026-08-23 起），788 个测试用例，Diátaxis 文档治理，安全设计（工具三级安全级别 + argsHash 审批账本 + Skills 渐进披露）远超项目年龄。

**2026-10-05 基线刷新**（评估日 9/14 以来 +133 提交，规范 v0.7.0 → **v0.7.6**，文档体系已 Diátaxis 化并外移历史归档至 `Aervox-docs-archive`）：

- **ADR-021（2026-10-03 裁决）内核独立**：`@aervox/core` 独立包（执行器、ControlContext 执行预算、审批 SPI、工具沙箱），**Apache-2.0** 发布，主仓其余源码维持 AGPLv3——双许可分层结构成立；
- **CR-054 model-runtime v3**：状态持久化与启动恢复（WIP 存档）；
- **CR-032 / CAP-030 主动提醒深化落地**：全局防打扰裁决器（冷却/静音时段/每小时频次水位）+ 托盘一键熔断 + 感知源目录含 `system.idle_state` + 主动动作插件派发；
- **CAP-033 主动智能模式**（Specified，明确不得声称 Ready）：`full_profile_v1` 独立确认、`FullProfileActionGrant`（动作类别/目标 scope/授权修订/可撤销快照）、七天原始副本提炼；
- **diary 域成型**：`packages/diary` 领域服务 + `/v1/diaries/*` + 每日日记查询/计划/窗口调度；`practice-review` 包（练习/错题本/间隔复习调度算法）独立；
- **新宿主形态**：思隅 CLI（`siyu`，CR-058）、P2P 局域网同步切片（ITER-028）、HLS 本地智能体研究执行器（CR-057）；`apps/mobile` Capacitor 壳 CR-055 待评审；
- **能力治理**：新增能力注册表（AVX-CAP-REG-001 v0.5.0）与需求追踪基线，区分「规范成熟度」与「生产就绪度」；MCP 在上游仍为 F 类（尚无正式 Adapter）。

**结论**：**能结合，且价值高——方式是「规范/模式移植（A）+ MCP 互联（B）」，不是合并**。最重要的发现：本项目 AG 路线（`项目待办v2.md` AG-P0~P6）中的规划项，Aervox 已用另一套技术栈**实现了一遍并写成规范文档**——AG-P3/P5 的设计成本已被预付。1.0.2 修订结论不变，但**许可证边界显著放宽（内核 Apache-2.0）**，且 AG-P5-08 MCP 互联因 CLI 宿主加入而价值升格。

## 2. AG 路线逐项映射（设计输入对照表）

| 本项目 AG 条目 | Aervox 对应物 | 状态与借鉴要点 |
|---|---|---|
| AG-P0 运行时（✅ 已完成） | turns/turn_attempts/turn_stream_events + 状态机 | 本项目已闭环；Aervox 更细的是 **lease TTL + fencing token + 崩溃恢复续跑**（从事件流+工具账本重建上下文、禁止重复副作用）；CR-054 model-runtime v3 的状态持久化与启动恢复进一步充实该参照 |
| AG-P3-01 建议收件箱（✅ 后端+前端已落地 2026-10-05） | `agent_inbox_items`（followup/steer 两类） | 表结构与"注入对话上下文的组装顺序"已按本表移植；上游 claim/ack 消费语义与过期回收 Worker 仍可作后续增强参照 |
| AG-P3-02 自动化规则 | CR-032 / CAP-030 已落地的全局防打扰裁决器 + `proactive_trigger_rules` + ProactiveArbitrator | **参照升级（1.0.2）**：裁决器三参数（冷却/静音时段/每小时频次水位）已生产落地并新增托盘一键熔断；感知源目录含 `system.idle_state`（空闲感知）；主动动作支持插件派发。移植时照搬参数模型，"一键熔断"对应本项目的功能可见性开关语义 |
| AG-P3-03 每日简报 | diary 包（素材窗口管线 + Worker 消费生成） | **参照升级（1.0.2）**：diary 已成型为独立领域包（领域服务 + `/v1/diaries/*` API + 每日查询/计划/窗口调度），移植面从表结构扩大到"窗口调度 + 失败降级 + API 形状" |
| AG-P3-04 每周复盘 | diary 周期产物 + workbench 统计 | 同上，随 AG-P3-03 一并设计 |
| AG-P3-05 事件触发建议 | CAP-033 感知源目录（`system.idle_state` 等）+ 触发规则 | 幂等键/去重键已在本项目 AG-P3-01 落库；上游 `system.idle_state` 属桌面端独有能力，Web 端无对应物，不移植 |
| AG-P5-01 Skill 风险分级 | 工具三级安全 `read_only / write_with_approval / privileged` + **工具 Prompt 约束登记**（BASE_TOOL_GUIDANCE / customGuidance，v0.7.6 新增强化） | 三级折叠映射 + privileged 拒绝原则照旧；**新增**：工具必须在系统提示词登记调用时机与约束，未登记不得进入生产可用清单——本项目的 Skill 注册表应吸收 |
| AG-P5-02/03 行动提案 + 审批 | `tool_approvals`（参数 hash 精确匹配授权）+ CAP-033 `FullProfileActionGrant`（动作类别/目标 scope/**授权修订**/可撤销快照） | **参照升级（1.0.2）**：argsHash 账本照搬不变；CAP-033 引入"授权修订链"（授权为可撤销的修订版本而非一次性 token）——本项目审批模型吸收该形状，但注意 CAP-033 为 Specified 非 Ready，取模型不取实现 |
| Skills 渐进披露 | SKILL.md 规范 + 系统提示词只注入名称+描述、按需读全文 | 对齐 Anthropic Skills 规范；与本 AG-P5 的 schema 化 Skills 互补 |
| AG-P6-03 长期记忆治理 | memory_nodes/edges 图式记忆 + FTS5 + 向量 RRF 混合检索 + 主动画像独立加密 vault | "授权胶囊开关、关闭即物理擦除"的隐私模式照旧借鉴；上游队列 ITER-003（记忆清理/召回资格）执行中，届时可二轮借鉴 |
| AG-P4 GitHub 项目教练 | CAP-034 Home Assistant / CAP-035 运动健康的 integration-manager 模式（**1.0.2 新增**） | 外部集成的授权门控 + 健康检查 + 实体默认禁用/白名单模式可整体借鉴到 GitHub OAuth 同步设计；仍无现成对应 |

## 3. 结合方式评估（按可行性排序）

### 3.1 方式 A：规范/模式移植（✅ 推荐，零运行时依赖）

把 AVX-HAR-001 与上述对照表中的设计作为 AG-P3/P5 的**设计输入**，翻译为 Python 落进 `agent_runs`/Skills 体系。设计思想不受版权约束，同作者更无障碍。其 `packages/agent-loop`（8.3k 行、几乎零依赖、纯端口架构 ports.ts）与 FastAPI 依赖注入风格天然对齐；`packages/contracts`（Zod→OpenAPI 3.1 流式契约）可作 Auxilio SSE 契约的范本。**注意**：移植以规范文档为准，不照抄未验证的实现路径（见 §4.2 缺口清单）。

### 3.2 方式 B：MCP 互联（✅ 可行，短期产品价值最高）

Aervox 自研 MCP 客户端（Streamable HTTP + JSON-RPC，协议版本 2025-06-18，不依赖第三方 SDK），插件清单声明 `mcpServers` 即可接入。结合形态：**本项目 FastAPI 把 Auxilio Skills 暴露为 MCP Server**（Python 官方 SDK 成熟），桌宠端即插即用读取学习画像/错题/复习队列/专注统计——正好补上其 SQLite 单用户没有的服务端数据；Aervox 侧的本地能力（系统空闲感知、剪贴板采集、托盘 Kill Switch）是 Web 端做不到的差异化。**方向不可逆**：Aervox 明令单用户禁 tenantId + SQLite 单写者，只能作客户端/个人壳，不能当多用户平台的服务端引擎。MCP Server 化本身就是 AG-P5 Skill 体系的自然交付物（已登记为 `项目待办v2.md` AG-P5-08），不是额外工程。**1.0.2 修订**：上游 MCP 仍为 F 类（尚无正式 Adapter），而新宿主形态（Electron 桌宠 + `siyu` CLI）扩大了潜在消费端——本项目先行交付 MCP Server 的产品价值进一步升格。

### 3.3 方式 C：抽包作为库（⚠️ 有条件）

仅 `@aervox/agent-loop` 值得抽取，但它是 TS——Python 后端只能移植不能 import；`repositories/schema` 与 SQLite/libsql 深度绑定，对 PostgreSQL 后端无用。

### 3.4 方式 D：深度合并（❌ 不可行）

四层硬冲突：SQLite 单用户 vs PostgreSQL 多租户、明令禁 tenantId vs 多社团、Vue/Element Plus vs Next.js、AGPL vs 平台代码。没有一层能平滑合并。

## 4. 风险与约束

### 4.1 许可证边界

**1.0.2 修订（依 ADR-021，2026-10-03 裁决）**：Aervox 已进入**双许可分层**——`@aervox/core` 独立内核包（执行器、ControlContext、审批 SPI、工具沙箱）以 **Apache-2.0** 发布（单一版权人再许可，包内附许可文本）；主仓其余源码维持 **AGPLv3**，文档维持 CC BY-NC-SA 4.0。对本项目的影响：

- **内核级内容**（执行器/审批 SPI/工具沙箱的模式与代码级参照）：Apache-2.0，搬运与衍生无传染义务，仅需保留许可与声明；
- **主仓其余内容**（宿主、业务域、Worker、diary 等应用层）：AGPLv3——规范/思想移植无障碍；**代码级搬运前仍 MUST 复核**（若本平台未来接受他人贡献或变更开源性，AGPL 网络条款的复核义务不变），进程隔离 + 网络交互（方式 B）仍是最安全边界；
- 当前两仓同为本人项目，实际风险有限；上表为对外贡献/开源场景下的长期护栏。

历史基线（9/14 评估）"Aervox 代码 AGPL-3.0-or-later 整体适用"的表述自此作废。

### 4.2 对象成熟度缺口（AVX-HAR-001 §2.2 自认清单）

异步 Outbox 驱动 Loop 未做；Step 级 ModelRun/ContextManifest 未接线；工具沙箱未完整落地；pi Adapter 空实现、DSH Adapter 仅 stdio 骨架；CR-033~035 为纸面提案；apps/mobile 无源码；运行时数据表近乎全空（无生产运行验证）；anthropic 预设可配置但执行层直接拒绝（单协议：仅 OpenAI 兼容）——**本项目双协议（含 Anthropic）是优势，移植时 MUST 保留**。

### 4.3 节奏约束

本项目 AG-P0~P2 刚完成、AG-P3 未启动。按 §5 路径推进，不与主线抢资源。

## 5. 落地路径

1. **立即（零成本，✅ 已完成）**：本评估文档登记 + `RootDoc-ADR.md` §5.2 指针 + `项目待办v2.md` 设计输入声明与 AG-P5-08 条目。
2. **AG-P3 启动时（✅ 已启动，2026-10-03~05）**：AG-P3-01 建议收件箱已按 §2 对照表完成后端切片（迁移 `c1d2e3f4a5b6`、幂等产生、惰性回收、状态机 + API）与前端切片（工作台 widget + BFF）；AG-P3-06 起步切片（arq cron 双 sweep：收件箱定时回收 + 过期活动归档）已落地。
3. **AG-P3-02/03（下一步，按 1.0.2 修订输入）**：自动化规则 + 裁决器按 **CR-032 已落地的三参数模型**（冷却/静音时段/每小时频次水位，另增"一键熔断"对应功能可见性开关）移植；每日简报按 **diary 域的窗口调度 + 失败降级 + `/v1/diaries/*` API 形状**移植；两者完成后 AG-P3-05 事件触发以 `idempotency_key` 去重键接入（`system.idle_state` 属桌面端独有，不移植）。
4. **AG-P5 启动时**：交付 AG-P5-08（FastAPI MCP Server），第一批暴露学习画像/错题/复习队列三类只读 Skill，形成「社团平台（Web）+ 个人桌宠（桌面）+ CLI」多端共享一份数据的产品闭环；审批模型采用 argsHash 账本 + **CAP-033 授权修订链形状**（可撤销修订版本，取模型不取实现）；Skill 注册表吸收 v0.7.6 的**工具 Prompt 约束登记**（未登记调用时机/约束的工具不得进入生产可用清单）。
5. **持续**：上游以能力注册表（AVX-CAP-REG-001）区分规范成熟度与生产就绪度——每次修订本评估时按其状态复核对照表（Specified/Ready 与 候选/远期），**只移植 Ready 或参数级模型，不移植 Specified 的未验证实现路径**。
