# 工作台（Workbench）代码审查请求 — 优化版

## 一、原请求的问题诊断

| # | 问题 | 说明 |
|---|------|------|
| 1 | **位置错误** | 说「`/tools` 目录」，但工作台代码**不在** `/tools` 目录。`/tools` 只是前端页面路由（`src/app/tools/page.tsx`）。`CS-Web-Frontend/tools/` 与 `CS-Web-Backend/tools/` 放的是部署脚本与文档，不是工作台实现。 |
| 2 | **边界模糊** | 未区分前端 React 组件 / BFF 路由 / 后端 FastAPI，执行者极易遗漏其中一侧。 |
| 3 | **维度空泛** | 「性能 / 可维护性 / 用户体验 / 代码结构 / 扩展性」是五个名词，没有检查点，输出易流于空话。 |
| 4 | **无输出格式** | 未约定每个问题如何呈现，结果散乱、无法对比。 |
| 5 | **无优先级** | 未约定严重度分级，无法指导「先改哪个」。 |

## 二、优化后的请求（可直接复用）

> 请对本项目「工作台（Workbench）」功能做一次代码质量审查，按下列文件清单逐一检查，不要只看单个文件：
>
> **前端（React / Next.js + TypeScript）**
> - `CS-Web-Frontend/src/app/tools/page.tsx` — `/tools` 页面入口
> - `CS-Web-Frontend/src/modules/workbench/` 整个目录，重点：
>   - `workbench.tsx`（组合 + 备份 + 布局显隐 + dnd 拖拽网格，约 420 行）
>   - `widget-registry.ts`（声明→配置→注册 + slot 分组）
>   - `types.ts`（尺寸规格系统 `WIDGET_SIZE_SPECS` / `GRID_COLS`）
>   - `widgets/` 下全部组件：`greeting-bar`、`today-tasks`、`quick-notes`、`exam-countdown`、`github-heatmap`、`llm-widget`、`llm-usage-stats`、`assistant-chat`（SSE 流式）、`pomodoro/*`
>   - `hooks/`（`use-clock`、`use-local-storage`、`use-idb-media`）、`lib/ambient-audio.ts`
> - `CS-Web-Frontend/src/app/api/workbench/**` — BFF 路由（`stats/api-usage`、`stats/pomodoro`、`stats/llm-usage`、`focus-sessions`、`llm-config`、`contributions/github`）
>
> **后端（FastAPI + SQLAlchemy async）**
> - `CS-Web-Backend/app/api/v1/workbench.py`
> - `CS-Web-Backend/app/services/workbench_service.py`
> - 相关 model：`app/models/focus.py`、`llm_config.py`、`api_usage.py`、`llm_usage.py`
>
> 从以下 5 个维度审查，每个维度落实到具体检查点：
>
> 1. **性能**：SSE 流式渲染是否每次 delta 都全量复制消息数组（`assistant-chat` 的 `appendDelta`）；`ResizeObserver` 测量是否节流；dnd-kit 拖拽是否引发不必要的整网格重渲染；后端聚合查询是否 N+1、缺索引、缺缓存（GitHub 热力图已有 6h 缓存，其余统计是否缺失）。
> 2. **可维护性**：`workbench.tsx` 是否职责过重（组合 / 备份 / 布局 / dnd 混在一起）；`widget-registry.ts` 中每个 widget 的 `titleKey` 是否与 i18n key 一致且存在（重点核查 `github-heatmap` 的 `titleKey`）；类型是否安全；是否存在重复逻辑。
> 3. **用户体验**：移动端拖拽体验；SSR/CSR hydration 是否闪烁；数据备份（导出/导入/清空）的提示与二次确认是否到位；空状态 / 加载态 / 错误态是否齐全；可访问性（键盘可达、aria）。
> 4. **代码结构**：widget 注册表的「声明→配置→注册」模式是否真正做到「新增 widget 零改动骨架」；slot 分组（full / primary / main+side）是否清晰；hooks 抽取是否到位。
> 5. **扩展性**：新增一个 widget 的实际成本（需要改哪几处）；尺寸规格系统是否够用；后端新增一个统计端点是否需要复制粘贴大量样板。
>
> **输出格式**：每个问题按下列结构输出，并按严重度分级：
> - 【位置】文件:行号
> - 【问题】一句话描述
> - 【影响】对性能 / 可维护 / UX / 结构 / 扩展性的具体后果
> - 【改进方向】具体、可执行的改法
> - 【优先级】P0（正确性 / 安全，必须修）/ P1（明显技术债）/ P2（锦上添花）
>
> 最后给出一张「问题清单总表」+「Top 5 优先修复项」。

## 三、一个佐证：为什么"位置"必须写对

原请求的「`/tools` 目录」会让执行者误入 `CS-Web-Frontend/tools/`（部署脚本 + 文档）。而真实实现分散在三处：

- 前端模块：`src/modules/workbench/`（8+ 个 widget 组件）
- 页面入口：`src/app/tools/page.tsx`
- 后端：`app/api/v1/workbench.py` + `app/services/workbench_service.py`

## 四、一个佐证：为什么"维度必须落地为检查点"

泛泛地问「可维护性」，执行者通常说不出具体问题。落地为检查点后，可以立刻暴露真实缺陷。例如已发现的一处：`widget-registry.ts` 中 `github-heatmap` 的 `titleKey` 被写成 `'examCountdown'`（与考试倒计时重复），而 i18n 词条里**根本没有** `githubHeatmap` 这个 key——这类问题只有把「核查 titleKey 与 i18n key 一致性」写成检查点才会被揪出。
