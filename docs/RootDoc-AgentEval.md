# RootDoc-AgentEval：Aervox-harness 与 Agent 路线结合评估（Explanation · 评估结论与结合方式）

> 更新人：3yearsZ
> 更新日：2026-09-14
> 版本：1.0.1 · 七夕（Diátaxis E 类，统一解释类文档规范）
> Diátaxis：E（Explanation · 回答「能不能结合、以什么方式结合」，提供评估取证与结论；不包含可执行步骤）
> 适用读者：架构师 / Agent 路线实施者；已了解 `docs/项目待办v2.md` 的 AG-P0~P6 规划
> 变更触发：Aervox-harness 重大版本演进 / 结合方式落地（升级为 ADR）/ AG 路线范围调整

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

**结论**：**能结合，且价值高——方式是「规范/模式移植（A）+ MCP 互联（B）」，不是合并**。最重要的发现：本项目 AG 路线（`项目待办v2.md` AG-P0~P6）中的规划项，Aervox 已用另一套技术栈**实现了一遍并写成规范文档**——AG-P3/P5 的设计成本已被预付。

## 2. AG 路线逐项映射（设计输入对照表）

| 本项目 AG 条目 | Aervox 对应物 | 状态与借鉴要点 |
|---|---|---|
| AG-P0 运行时（✅ 已完成） | turns/turn_attempts/turn_stream_events + 状态机 | 本项目已闭环；Aervox 更细的是 **lease TTL + fencing token + 崩溃恢复续跑**（从事件流+工具账本重建上下文、禁止重复副作用），可作为 AG-P0 的增强方向 |
| AG-P3-01 建议收件箱 | `agent_inbox_items`（followup/steer 两类） | **现成实现**；表结构与"注入对话上下文的组装顺序"可直接移植 |
| AG-P3-02 自动化规则 | `proactive_trigger_rules` + ProactiveArbitrator（冷却/静音时段/每小时频次水位） | **现成实现**；裁决器三参数是防打扰的成熟设计，建议照搬参数模型 |
| AG-P3-03 每日简报 | diary 包（素材窗口管线 + Worker 消费生成） | **现成实现**；"素材窗口采集 → 生成失败不影响主流程"的降级设计与本项目验收标准一致 |
| AG-P5-01 Skill 风险分级 | 工具三级安全 `read_only / write_with_approval / privileged` | **现成实现**；本项目五级方案可折叠映射（privileged 一律拒绝走管理员通道的原则值得保留） |
| AG-P5-02/03 行动提案 + 审批 | `tool_approvals`（参数 hash 精确匹配授权）+ full-access 模式开关 | **现成实现**；argsHash 精确授权账本直接解决"一次授权无限复用"的越权问题 |
| Skills 渐进披露 | SKILL.md 规范 + 系统提示词只注入名称+描述、按需读全文 | 对齐 Anthropic Skills 规范；与本 AG-P5 的 schema 化 Skills 互补（声明式低门槛 + 结构化高保障） |
| AG-P6-03 长期记忆治理 | memory_nodes/edges 图式记忆 + FTS5 + 向量 RRF 混合检索 + 主动画像独立加密 vault | **现成实现**；"授权胶囊开关、关闭即物理擦除"的隐私模式（ADR-018/019）可整体借鉴 |
| AG-P4 GitHub 项目教练 | 最接近的是 Home Assistant/小米健康外部客户端模式（integration-manager） | 仅模式可借鉴（外部集成的授权门控 + 健康检查），无现成对应 |

## 3. 结合方式评估（按可行性排序）

### 3.1 方式 A：规范/模式移植（✅ 推荐，零运行时依赖）

把 AVX-HAR-001 与上述对照表中的设计作为 AG-P3/P5 的**设计输入**，翻译为 Python 落进 `agent_runs`/Skills 体系。设计思想不受版权约束，同作者更无障碍。其 `packages/agent-loop`（8.3k 行、几乎零依赖、纯端口架构 ports.ts）与 FastAPI 依赖注入风格天然对齐；`packages/contracts`（Zod→OpenAPI 3.1 流式契约）可作 Auxilio SSE 契约的范本。**注意**：移植以规范文档为准，不照抄未验证的实现路径（见 §4.2 缺口清单）。

### 3.2 方式 B：MCP 互联（✅ 可行，短期产品价值最高）

Aervox 自研 MCP 客户端（Streamable HTTP + JSON-RPC，协议版本 2025-06-18，不依赖第三方 SDK），插件清单声明 `mcpServers` 即可接入。结合形态：**本项目 FastAPI 把 Auxilio Skills 暴露为 MCP Server**（Python 官方 SDK 成熟），桌宠端即插即用读取学习画像/错题/复习队列/专注统计——正好补上其 SQLite 单用户没有的服务端数据；Aervox 侧的本地能力（系统空闲感知、剪贴板采集、托盘 Kill Switch）是 Web 端做不到的差异化。**方向不可逆**：Aervox 明令单用户禁 tenantId + SQLite 单写者，只能作客户端/个人壳，不能当多用户平台的服务端引擎。MCP Server 化本身就是 AG-P5 Skill 体系的自然交付物（已登记为 `项目待办v2.md` AG-P5-08），不是额外工程。

### 3.3 方式 C：抽包作为库（⚠️ 有条件）

仅 `@aervox/agent-loop` 值得抽取，但它是 TS——Python 后端只能移植不能 import；`repositories/schema` 与 SQLite/libsql 深度绑定，对 PostgreSQL 后端无用。

### 3.4 方式 D：深度合并（❌ 不可行）

四层硬冲突：SQLite 单用户 vs PostgreSQL 多租户、明令禁 tenantId vs 多社团、Vue/Element Plus vs Next.js、AGPL vs 平台代码。没有一层能平滑合并。

## 4. 风险与约束

### 4.1 许可证边界

Aervox 代码为 **AGPL-3.0-or-later**（强传染 + 网络条款），文档为 CC BY-NC-SA 4.0。当前两仓同为本人项目，思想/规范移植与自用代码搬运无障碍；**若 CS 平台未来接受他人贡献或变更开源性，代码级搬运前 MUST 复核 AGPL 义务**，进程隔离 + 网络交互（方式 B）是传统上最安全的边界。

### 4.2 对象成熟度缺口（AVX-HAR-001 §2.2 自认清单）

异步 Outbox 驱动 Loop 未做；Step 级 ModelRun/ContextManifest 未接线；工具沙箱未完整落地；pi Adapter 空实现、DSH Adapter 仅 stdio 骨架；CR-033~035 为纸面提案；apps/mobile 无源码；运行时数据表近乎全空（无生产运行验证）；anthropic 预设可配置但执行层直接拒绝（单协议：仅 OpenAI 兼容）——**本项目双协议（含 Anthropic）是优势，移植时 MUST 保留**。

### 4.3 节奏约束

本项目 AG-P0~P2 刚完成、AG-P3 未启动。按 §5 路径推进，不与主线抢资源。

## 5. 落地路径

1. **立即（零成本，✅ 已完成）**：本评估文档登记 + `RootDoc-ADR.md` §5.2 指针 + `项目待办v2.md` 设计输入声明与 AG-P5-08 条目。
2. **AG-P3 启动时**：建议收件箱/自动化规则/每日简报三件套直接按 §2 对照表移植 Aervox 表结构与裁决器参数，省一轮设计评审。
3. **AG-P5 启动时**：交付 AG-P5-08（FastAPI MCP Server），第一批暴露学习画像/错题/复习队列三类只读 Skill，形成「社团平台（Web）+ 个人桌宠（桌面）」双端共享一份数据的产品闭环。
