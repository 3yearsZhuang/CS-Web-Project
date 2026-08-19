# DeepSeek Harness（DSH）集成评估报告

> 状态：评估稿（决策依据）｜日期：2026-08-19｜对象：工作台「学习助手 Auxilio」
> 结论速览：**可集成，但 DSH 是 Agent 运行时而非模型 API——"用上 DeepSeek 模型"无需 DSH（改配置即可）；"Agent 化"无需整体替换，更优路径是「取其优点融合」（第九章：F1 自研吸收 → F2 按需桥接 DSH 能力）。路径 A（接模型）随时可并行。**

---

## 一、背景与目标

工作台「学习助手」（Auxilio）当前是自研的轻量 Agent 对话：SSE 流式 + 7 个业务工具 + 规则模式降级。DeepSeek 于 2026-08-13 发布开发者预览版 DeepSeek Harness（v0.1，MIT 开源），官方公式 **Model + Harness = Agent**。

本次评估目标：判断学习助手能否集成 DSH、以何种方式集成、成本与风险如何，作为后续实施（预期路线 B → C）的决策依据。

## 二、概念澄清（本报告最重要的前提）

| 维度 | 学习助手 Auxilio（现状） | DeepSeek Harness（DSH） |
|---|---|---|
| 本质 | 已是一个自研轻量 Agent harness | DeepSeek 官方 Agent 运行时（8-13 v0.1 预览，MIT 开源） |
| 技术栈 | Python FastAPI + httpx | Node / TypeScript（Cordis 微内核，一切皆插件） |
| 能力 | 7 业务工具、最多 3 轮工具循环、规则模式降级 | 沙箱、长任务、多 Agent、联网搜索、Skill、上下文管理、Agent 预设、4 运行模式 |
| 模型接入 | OpenAI 兼容 + Anthropic 双协议流式 | 模型适配器插件（可换任意模型） |
| 部署形态 | FastAPI 进程内 | 独立进程（`npx @deepseek-ai/dsh web` 起 Web UI） |

**关键结论：DSH ≠ 模型 API。** 学习助手现有 `llm_client` 已支持 OpenAI 兼容协议，接入 DeepSeek 模型只改配置、不引入 DSH；引入 DSH 意味着把 Agent 编排层替换/外包，属于架构级改动。

## 三、学习助手现状盘点（集成锚点）

### 3.1 代码位置

| 层 | 文件 | 职责 |
|---|---|---|
| API | `app/api/v1/auxilio.py` | `/api/v1/auxilio/chat`（SSE）、conversations、messages |
| 编排 | `app/services/auxilio_agent.py` | `run_chat` 事件流（delta/tool_call/tool_result/done/error）；`TOOL_SCHEMAS` 7 工具；`MAX_TOOL_ROUNDS=3`；`build_system_prompt`；`_user_llm_overrides`；预算拦截 |
| 模型 | `app/services/llm_client.py` | OpenAI 兼容 + Anthropic 双协议流式；`check_enabled` 未配置抛 `LLMConfigError` |
| 画像 | `app/services/auxilio_service.py` | `analyze_learning_profile`：薄弱标签（正确率 < 60%）+ 资源推荐 |
| 数据 | `app/repositories/auxilio_tool_repo.py` | 只读数据访问（考试/任务/资源/用量/番茄钟） |
| 模型 | `app/models/conversation.py` `llm_usage.py` `llm_config.py` | 会话/消息/用量埋点/用户级 LLM 配置（TOTP 加密 key） |
| 前端 | `src/modules/workbench/widgets/assistant-chat.tsx`、`llm-widget.tsx` | SSE 流式 UI + 工具调用状态卡 |

### 3.2 硬约束（集成必须保持）

1. **认证**：所有 auxilio 接口需 `get_current_active_user`（JWT），规则模式亦需登录。
2. **预算**：`LLM_DAILY_BUDGET`（默认 200K tokens/日）在 `run_chat` 调用模型前按用户累加拦截。
3. **落库**：`conversations` / `chat_messages`（含 tool_calls JSONB）/ `llm_usage_logs`（provider/model/token/延迟/状态）。
4. **安全**：ER-19 提示注入隔离（`wrap_user_profile_field` / `wrap_untrusted_tool_result` 结构化包裹 UGC 与工具结果）；ER-18 API 用量管理员可见性。
5. **降级**：无 LLM 配置时规则模式摘要，保证功能不缺失。

## 四、DSH 技术剖析

- **内核**：Cordis 微内核仅负责插件加载/卸载/依赖；模型、工具、技能、会话、沙箱、存储、循环、调度、UI 均为插件，配置层自由组合替换，不改源码。
- **四种模式**：标准（完整工具组合）/ PTC（模型生成代码组合多轮工具调用）/ 极简（仅 shell + 文件编辑，用于最小环境基准测试）/ 创造（运行时检查、内存中试验插件、组合新模式）。
- **可追溯**：append-only 会话日志记录模型看到的一切（系统提示词/思维链/工具调用与结果/子 Agent/上下文注入）；Trajectory 视图按来源查看，支持恢复、分叉、检索、回放。
- **部署**：`npx @deepseek-ai/dsh web` 一键启动 Web UI；源码安装见 GitHub `deepseek-ai/deepseek-harness`。
- **定位**：对标 Claude Code / Codex，主打编程与办公场景（管理项目、长任务、多 Agent、Skill、联网搜索）。
- **成熟度**：v0.1 开发者预览版，官方声明核心插件与基础接口将快速迭代演进。

## 五、集成路径评估

### 路径 A · 接 DeepSeek 模型（零代码，不引入 DSH）

- **做法**：`LLM_PROVIDER=openai`、`LLM_BASE_URL=https://api.deepseek.com/v1`、`LLM_MODEL=deepseek-chat`（或 `deepseek-reasoner`）；用户也可在「用量与设置」自填 base_url/key/model（`llm_configs` 已支持）。
- **收益**：学习助手立刻获得 DeepSeek 推理能力；预算/落库/降级/ER-19 全部沿用。
- **成本**：约 0（仅配置）。风险：低（走稳定模型 API）。
- **定位**：独立于 B/C，随时可做；也是 B/C 的前置收益。

### 路径 B · DSH 作引擎（适配器桥接，中等成本）

- **做法**：DSH 独立进程承载 Agent 编排，FastAPI 侧新增桥接层把 DSH 事件流翻译为现有 `delta/tool_call/tool_result/done/error`，前端 UI 不变。
- **五大待解问题**：
  1. **跨语言部署**：DSH 为 Node 进程，需纳入 docker-compose 生命周期管理（健康检查/重启/资源限制）。
  2. **认证打通**：DSH 自带会话体系 vs 现有 JWT。候选：DSH 独立会话 + 用户映射表；或桥接层代理注入。
  3. **业务工具插件化**：7 个工具注册为 DSH 插件（契合"一切皆插件"），或实现为 HTTP 工具回调 FastAPI（`analyze_learning_profile` 等数据仍在 FastAPI 侧）。
  4. **落库与预算**：`llm_usage_logs` 记账与 `LLM_DAILY_BUDGET` 拦截上移至桥接层；DSH 长任务多轮调用可能放大 token 消耗，须按用户强制。
  5. **ER-19 对齐**：DSH 工具结果注入方式需套用现有不可信数据包裹模板，防提示注入逃逸。
- **收益**：学习助手获得真实 Agent 能力（沙箱/长任务/多 Agent/Trajectory），前端体验保留。
- **成本**：PoC 0.5–1 天 + 正式集成 3–5 天（估）。风险：中（预览版接口漂移、跨语言运维）。
- **前置条件**：PoC 通过 go/no-go 门（见 §6 阶段 0）。

### 路径 C · 全面替换（DSH Web UI 托管，高成本）

- **做法**：前端改用 DSH Web UI（iframe 嵌入工作台卡片或独立页），业务 API 仅作 DSH 的 HTTP 工具。
- **成本**：前端工作台 `llm-widget` 重做；破坏 DnaCard 像素风格一致性；认证/预算/审计迁移全部由 DSH 承担或重写。
- **风险**：高（体验断层、预览版锁定）。**不建议一步到位**，仅在 B 稳定运行后按演进路线进入。

## 六、推荐演进路线（B → C 分阶段）

| 阶段 | 内容 | 验收/决策门 |
|---|---|---|
| 0 · PoC（0.5–1 天） | 本地起 DSH web（标准模式）；注册 1 个业务工具插件（`analyze_learning_profile` HTTP 回调 FastAPI）；验证事件流可桥接 | go：工具回调成功 + SSE 桥接可行 → 进阶段 1；no-go：退回路径 A |
| 1 · 桥接集成（3–5 天） | Python 桥接层翻译事件流；认证映射；7 工具插件化；预算/落库上移；ER-19 对齐 | go：对话体验与现有一致 + 预算/落库不回归 → 灰度 |
| 2 · 渐进切换 | 引擎可配置切换（现有 `run_chat` ↔ DSH 桥接），按用户灰度 | go：灰度稳定 → 默认 DSH |
| 3 · 全面替换（C） | 评估前端换 DSH Web UI，工作台卡片重做，体验一致性专项 | 仅在产品定位确认转向后启动 |

## 七、风险登记

| # | 风险 | 等级 | 缓解 |
|---|---|---|---|
| R1 | DSH v0.1 预览版接口快速迭代，漂移 | 中 | 桥接层隔离 DSH API；锁版本；PoC 先行 |
| R2 | 跨语言部署复杂度（Node 服务运维） | 中 | docker-compose 托管 + 健康检查；阶段 1 验收 |
| R3 | 认证与数据合规（DSH 自带会话存储 vs 现有落库/审计） | 中 | 用户映射表 + 桥接层统一记账 |
| R4 | 预算失控（长任务放大 token 消耗） | 高 | `LLM_DAILY_BUDGET` 拦截上移桥接层，按用户强制 |
| R5 | ER-19 提示注入边界被破坏 | 高 | 工具结果注入模板对齐；保留包裹逻辑 |
| R6 | 路径 C UI 断层（像素风 DnaCard） | 中 | 阶段 3 单独评审，不混入 B |

## 八、决策建议

1. **短期**：路径 A 随时可做（改配置），独立于 B/C，先拿 DeepSeek 推理收益。
2. **中期**：路径 B 以阶段 0 PoC 验证后投入；不满足 go 门则回退 A，避免预览版锁定。
3. **长期**：路径 C 仅在 B 稳定运行、产品定位确认转向后启动。
4. **落地纪律**：本报告为评估文档，无代码改动，不涉及 SSOT/CHANGELOG；进入实施时须在 `docs/项目待办事项-优先级重排.md` 登记待办并同步 CHANGELOG。
5. **融合优先（2026-08-19 补充）**：按第九章 F1 自研吸收先行，取代 B/C 整引擎路线；路径 A 随时并行。

## 九、融合方案（取其优点，不二选一）

在 B（整引擎替换）/ C（全面替换）之外，存在更优第三条路：**吸收式融合**——保留现有业务内核，把 DSH 的高价值设计思想在现有 Python 架构内自研落地，避免预览版锁定（R1）。

### 9.1 取舍清单

| 取舍 | 项 | 理由 |
|---|---|---|
| 保留 | 学习画像/资源推荐、7 业务工具、规则降级、预算、ER-19、落库、JWT 认证 | 业务深度与既有安全/合规硬约束 |
| 吸收 | Trajectory 事件日志、工具声明式注册、Agent 预设、联网搜索（可选） | 高价值、低成本、可自研 |
| 延后 | 沙箱执行、多 Agent、PTC、DSH Web UI | 学习助手短对话场景低相关；有需求再评估 |

### 9.2 融合架构

- **编排层**：`run_chat` 对话主链路与事件流协议不变（前端零改动）。
- **工具层**（吸收"一切皆插件"思想）：`TOOL_SCHEMAS` 从硬编码 dict + `execute_tool` if/elif 链，改为**声明式注册表**（schema + handler 映射）；新增工具只需注册，执行器遍历注册表；每工具可独立启用/停用（按 Agent 预设）。
- **会话层**（吸收 Trajectory）：对话全事件流（delta/tool_call/tool_result/usage/error）append-only 落库（新表 `chat_events`），支持回放与调试；现有 `chat_messages` 保留为对外快照。
- **预设层**（吸收 Agent 预设）：定义场景预设（如"考试冲刺"/"资源检索"/"通用答疑"），每预设 = 系统提示词模板 + 工具子集 + 模型参数；工作台可切换。
- **可选增强（F2）**：联网搜索工具（外部资源并入推荐）；沙箱执行工具（"边学边练"，P2 延后）。

### 9.3 融合路径

- **F1 自研吸收**（推荐先行）：上述吸收项全部在 Python 架构内实现。成本低、无 Node 依赖、无预览版接口锁定、每改动点可独立回滚（符合协作约定）。
- **F2 能力桥接**（按需）：当确需 DSH 独有能力（联网/沙箱）时，DSH 独立进程仅作"能力插件源"，通过桥接层把能力注册为现有 `run_chat` 的一个工具——范围比路径 B 小（不替换编排、不碰 UI），风险受控（R2/R3/R4/R5 均在桥接层单点收敛）。

### 9.4 实施拆分（一次一个改动点，逐点确认）

1. **融合点 1**：工具声明式注册表（改造 `auxilio_agent.TOOL_SCHEMAS` + `execute_tool`，行为不变，纯重构）
2. **融合点 2**：Trajectory 事件日志（新表 `chat_events` + `run_chat` 落事件，前端不变）
3. **融合点 3**：Agent 预设（提示词模板 + 工具子集组合）
4. **融合点 4**（可选）：联网搜索 / 沙箱（F2 桥接入口）
5. **并行**：路径 A 接 DeepSeek 模型（配置级，随时可做）

### 9.5 与既有路线关系

- 路径 A（接 DeepSeek 模型）：并行不冲突，随时可做，先拿推理收益。
- 路径 B/C：被融合方案取代为 F1→F2 演进；DSH 从"引擎/UI"降级为"能力插件源"，跨语言部署与认证打通等风险显著缩小。

## 附录 A · 关键配置项

`LLM_PROVIDER`（none/openai/anthropic，默认 none）、`LLM_API_KEY`、`LLM_BASE_URL`（OpenAI 兼容网关，可指 Ollama/vLLM/DeepSeek）、`LLM_MODEL`（默认 gpt-4o-mini）、`LLM_TIMEOUT`（默认 60s）、`LLM_MAX_TOKENS`（默认 1024）、`LLM_DAILY_BUDGET`（默认 200，千 tokens/日，0=不限）。

## 附录 B · 参考链接

- DeepSeek Harness 官方页：https://www.deepseek.com/harness/
- GitHub：https://github.com/deepseek-ai/deepseek-harness（MIT，v0.1）
- 发布报道：科创板日报（2026-08-13/14）、上证报·中国证券网（2026-08-13）
- 相关实践：DeepSeek Harness 三维评测（BestHub，AgentLoop 集成）
