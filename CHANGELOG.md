# Changelog

> 全项目变更记录**唯一权威文件**（Keep a Changelog 格式，覆盖 `[Unreleased]` → `[0.9.1]`）。
> 格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，每条变动统一为「分类 + 一行精简 bullet」，原编号（ADR / ER / PRR / Phase / M / R / F / G / B / CodeGov / DocGov / AL）内联保留以便追溯。
> 规划类长文（工具页→工作台改造方案、功能模块可见性方案）已于 2026-08-18 归档处置（C-20）：落地结论见各版本 `Added`/`Changed`，未完成残余项见 `docs/项目待办事项-优先级重排.md`（C-21 起为待办 SSOT）。
> 原拆分归档（0.9.1 / 0.9.5~0.9.7 / 0.9.8 / 0.9.9）与 `docs/项目演变历史.md` 已于 2026-08-17 全量并入本文件后删除（不保留 archive 副本）；全仓活文档引用历史统一以本文件为准。编号体系见文末速查表。

---

## [Unreleased]

> 进行中 / 下一波次变更累积区；发版时由 `scripts/tag_and_release.sh` 自动转为具体版本号 + 日期。已闭环项不在此滞留（见 `docs/项目待办事项-优先级重排.md`）。

### Added

- **演示模式（后端未连接降级演示）**：后端不可达（自动降级）或手动开启（`?demo=1` / 登录页「进入演示模式」入口）时，BFF 层按内置 mock 路由表返回示例数据，覆盖 17 条路由——auth 登录闭环（login-email/me/profile）、公告、活动（列表/详情/我的报名）、社区（分类/标签/帖子/成员）、加入申请（mine/提交）、通知未读数、公开主页；未覆盖端点（admin 后台 / tools 工具 / SSE 流式）返回 `DEMO_NOT_IMPLEMENTED` 占位。全局 `[ DEMO ]` 横幅明确标识来源（手动/自动）并提供退出/重试连接；`GET /api/demo/status` 供前端查询状态；自动降级带 30s TTL 惰性重探测 + 3s fetch 超时，后端恢复自动回到真实模式。实现：`src/shared/demo/`（`demo-mode.ts` 判定+mock 表、`mock-data/` 各模块）、`src/shared/constants/demo.ts`（cookie/参数常量，服务端与客户端同源）、`src/components/demo/`（`demo-mode-init.tsx` URL 开关、`demo-banner.tsx` 横幅）、`src/app/api/demo/status/route.ts`。mock 字段对齐翻译函数契约（后端 TZModel 系 camelCase / 纯 BaseModel 系 snake_case）。验证：ts-check 10 基线零新增、vitest 234 passed。演进方案 3（demo Routes 伪后端）列入待办 P2-8。
- **工作台 Schema 配置驱动卡（Phase A 内核）**：新增 `src/modules/workbench/schema/`（`widget-schema.ts` 类型+校验器 / `use-schema-data.ts` 三源数据 hook / `use-schema-widgets.ts` 配置集合 / `schema-widget-renderer.tsx` 渲染器），六种卡型（count/list/progress/countdown/note/link）全部复用 WorkbenchCard 外壳；成员粘贴 JSON 声明（`wb_schema_widgets`）即可自建简单卡，零代码。能力边界：流式/状态机/音频/加密/复杂图形类卡仍走手写组件。api 数据源白名单（`/api/workbench/**`+`/api/tools/**` 前缀）防契约漂移。`widget-registry.ts` 注册内置 `schema-widget` 卡；i18n 补 `schemaWidget`/`schemaEmpty`/`schemaEmptyHint`；`BACKUP_KEYS` 纳入 `wb_schema_widgets`。设计文档见 `docs/workbench-schema-widget-design.md`（Phase A 已实现）。
- **工作台 Schema 卡 Phase B（简易表单，零代码建卡）**：新增 `schema/schema-card-form.tsx` 内嵌于布局设置面板——标题/类型/数据源（local key 自动补 `wb_` / api url）三要素即可建卡，list 类型可选逗号分隔字段 key；提交经校验器、错误就地展示；面板内可管理（删除）已建卡。i18n 补表单与六类型标签词条（zh+en+类型声明）。普通成员不再需要手写 JSON。
- **工作台任务与便签合并卡**：`today-tasks` + `quick-notes` 合并为 `tasks-and-notes`（`widgets/tasks-and-notes.tsx`），今日待办 + 快捷便签双区共存（各自持久化 `wb_tasks`/`wb_notes`，零数据迁移），新增「便签转今日任务」（✓ 按钮）；删除两个旧组件文件；i18n 补 `tasksAndNotes`/`noteToTask`。
- **精简方案 §6 决策·活动设置面板接入（admin-events-settings）**：将此前从未接入的活动模块设置面板挂载到 `admin-events-panel.tsx`（工具栏新增 Settings 按钮，内联可折叠展开，复用 `adminEvents` i18n namespace 与后端 `/api/admin/events/settings` 接口），恢复管理端活动参数配置能力（标题/描述/日期等上限与默认容量批量保存）。ts-check 10 基线零新增。

### Changed

- **工作台卡片统一外壳（WorkbenchCard）**：新增 `src/modules/workbench/workbench-card.tsx`（DnaCard corner + meta-mono 标题头 + 右上操作区 + loading/empty/error 三态），收敛 7 个注册 widget 的重复样板（today-tasks / quick-notes / exam-countdown / github-heatmap / llm-widget / pomodoro）；greeting-bar（顶部全宽状态条）与 workbench 布局设置面板保留定制结构。
- **Phase 2 / D5 文档治理（RootDoc-Deploy §八 CI 分工）**：ER-09 文档死链审计已由根仓 `.github/workflows/ci.yml` 的 `Docs dead links (ER-09)` 步骤（`scripts/check/check_dead_links.py --base . --docs docs`）覆盖，更新分工表 Jenkinsfile 行备注与「能力缺口」说明，标记缺口已闭合（与 Jenkinsfile 双保险）。
- **Phase 2 / D3 文档治理（公共组件调研报告 §2.1）**：澄清前端组件权威清单以 `src/components/README.md` 为准，报告 §2.1 保留本报告视角的补充分类（含各组件变体与 `use*`/`*Provider` 细节）并加指针链接，消除双源维护漂移。（注：方案原计划"§2.1 与 RootDoc-FEArch §2.1 重复"前提不成立——后者为方法论、不含组件清单，故不删除详细清单。）
- **Phase 2 / 前端依赖治理（package.json）**：`pino-pretty`（仅 dev 日志美化，`src/shared/logger.ts` 以 `NODE_ENV !== 'production'` 门控、生产走 NDJSON）从 `dependencies` 移入 `devDependencies`，缩小生产依赖面；`tw-animate-css` 经核实被 `src/app/globals.css:27` `@import` 引用，**保留**（方案原"未引用"前提不成立）。
- **Phase 2 / 脚本治理（S1+S2，修复 c146d38 重命名回归）**：① 三个 db 脚本（update/healthcheck/export_db_to_desktop）`$SCRIPT_DIR/..` → `../..`，修复 2026-08-17 从 `scripts/` 挪入 `scripts/db/`（纯改名、未同步相对路径）导致的失效（根 `.env` / 根 `docker-compose.yml` 恢复正确指向）；同步修正脚本头用法注释与 `RootDoc-Deploy.md` 残留的移动前路径。② S2 新增 `scripts/db/lib/health-probe.sh`（`probe_backend_health` / `probe_frontend_health`），`update.sh`（轮询）与 `healthcheck.sh`（单次）收敛为 source 调用，消除两条 `docker compose exec` 探测命令重复；`update.sh` 补 `HEALTH_CONNECT_TIMEOUT=3` 保持原内联连接超时语义。③ S1 决策：`backup_db.sh` 复用不可行（其加载 BE 仓 `.env` 且自带保留期清理会在桌面误删旧备份），`export_db_to_desktop.sh` 保留自身 `pg_dump`（参数与 `backup_db.sh` 一致），仅修真 bug。
- **Phase 3 / B4 时区统一（utcnow → now_utc）**：`datetime.utcnow()` 4 处（`app/api/v1/auxilio.py:88,119` / `app/services/auxilio_agent.py:151` / `app/services/contribution_service.py:79`）全部收敛为 `app/core/timezone.py` 的 `now_utc()`（aware UTC），消除对集中工具与「禁止 utcnow」约定的绕过；顺带修复两处潜伏 naive/aware 比较 TypeError（`auxilio_agent.py` 的 `end_time - now`、`contribution_service.py` 的 `now - fetched_at`——DB 列实为 TIMESTAMPTZ 返回 aware）。对齐 3 个模型列声明为 `DateTime(timezone=True)`（`Exam.start_time/end_time`、`ContributionCache.fetched_at`，与迁移/CLAUDE.md 约定一致，无 schema 变更）。
- **Phase 3 / B3 分页响应模型（total_pages 算法统一）**：新增 `app/schemas/pagination.py` 的 `compute_total_pages(total, size)`（`max(1, ceil(total/size))`，`size<=0` 守卫防除零），`PaginatedResponse` 内部改用它，并统一 `user_service.py`（原 `(total+page_size-1)//page_size`，0 数据时 0）与 `admin_events.py`（原 `1 if total>0 else 0`，0 数据时 0）两处手算 → 消除 0 vs 1 边界漂移（0 数据统一为 1 页）；顺带把 `user_service.py` 列表查询收敛为 B2 的 `paginate()`（闭环 B2 最后残留）。响应模型结构（`EventListOut`/`AdminUserListOut` 保持 page/page_size 形态）不变，**无 API 契约变更、前端无需改动**。
- **Phase 3 / B1 事务统一——有意延后（2026-08-19 决策）**：142 处 `db.commit()`（37 文件）中仅 72 处方法末提交可安全迁移，**70 处中途提交**依赖早期提交可见性（如 auth_service 提交后查 totp/发 token）、19 处条件提交（`if commit:`）、24 个方法多次提交、27 处 try/except 窗口——装饰器统一会改变中途提交的事务边界语义，零功能收益、回归风险高。与门槛#5「有意延后」同款处置：触发条件为「新代码强制 `@transactional`」或「单独排期逐方法迁移 + 配测试」（触发条件记录于本文件「项目精简方案全案收口」条目）。至此**项目精简方案全案收口**：Phase 1 ✅ / Phase 2 ✅ / Phase 3（B3/B4 ✅、B5 核实无需动作 ✅、B1 决策延后 ⏸）。
- **精简方案 §6 决策·API 参考接生成器（D1）**：`docs/api-reference.md`（437 行手写、头部谎称"由 0.9.8 冻结契约自动生成"但全仓无生成器，必然漂移）压缩为入口页；主体改为 `docs/api-reference.html`（ReDoc 交互查看器，由 `openapi.baseline.json` 经新增 `make gen-api-docs`（`@redocly/cli`，npx 免装依赖）真实生成，永不漂移）；`docs/README.md` 索引改指向 html；契约变更流程（`contract-baseline` → `gen-api-docs`）写入入口页。死链检查 0 错误。
- **精简方案 C2·e2e.yml 重复检查去重**：删除 `e2e.yml` 与根仓 `ci.yml` 重复的版本四源同步（ER-33）与文档死链（ER-09）两步（已确认 `ci.yml` 在 `push [main, master]` + PR 全覆盖这三项门禁含契约）；`e2e.yml` 回归纯 E2E（push:main + nightly + 手动），职责清晰、减少冗余运行。
- **精简方案 F2·Modal 遮罩/ESC 收敛**：`ModalShell`（`components/primitives`）新增 `size`（md/lg）与 `scrollable` 两个**向后兼容** prop；`event-modals.tsx` 创建/编辑活动模态框从手写遮罩（宽双列 + 内滚动，且此前**缺 ESC / 焦点陷阱 / 滚动锁定**）收敛为 `<ModalShell size="lg" scrollable>`，补齐键盘可达性；`submit-resource-modal.tsx` 保留手写（motion 入场动画 + display-serif/ArkDivider 装饰标题为资源站特色视觉，收敛必回归，记录决策）。user/role modals 此前已收敛。ts-check 10 基线零新增。
- **精简方案 C3·子仓 CI 职责评估**：梳理 BE/FE 子仓 ci.yml、FE audit.yml、根仓 ci.yml/e2e.yml 与 Jenkinsfile——职责边界清晰、无实质重复（子仓=代码级门禁 / 根仓=基线级契约+版本+死链+全栈 E2E / FE audit.yml=依赖审计 / Jenkinsfile=自托管等价备用，死链与契约为其与 GH Actions 的有意双保险）；仅修正根仓 ci.yml 头部注释「依赖审计」归属（实为 FE 独立 audit.yml）。
- **项目精简方案全案收口（`docs/项目精简方案.md` 已并入本文件并删除本体）**：2026-08-19 的代码/文件/文档冗余审计与精简全部落地或明确决策——Phase 1（删 3 个前端孤立文件 / formatDate 收敛 / 后端卫生 .gitignore+去 BOM / Makefile check-contract 修复 + CHANGELOG 治理 / D2 待办清理）；Phase 2（B2 分页收敛 / #7 依赖 pino-pretty / #8 脚本 S1+S2 / #9 文档 D3+D5）；Phase 3（B3 分页模型 / B4 时区 / B5 核实无需动作 / B1 有意延后）；§6 两项（活动设置面板接入 / API 参考接 redocly 生成器）；F2 Modal 收敛；C2 e2e 去重；C3 CI 职责评估。**执行中发现并修正 4 处方案前提错误**：tw-animate-css 实际被 `globals.css:27` 引用→保留（原"未引用"错）；D3 与 `RootDoc-FEArch` §2.1 不重复（后者为方法论）→保清单+加指针；S1 `backup_db.sh` 不可复用（env 源 + 桌面清理副作用）→保留自身 pg_dump；B2 用模块级 `paginate()` helper（仅 1 个 repo 继承 BaseRepository，类方法不适用）。**附带修复**：c146d38 脚本重命名回归（3 脚本相对路径失效）、2 处 naive/aware 时区比较 TypeError、3 列模型/迁移不一致对齐（`DateTime(timezone=True)`）。**已排除项（勿重复审计）**：`worker.py`/`rbac_init.py`/`db_initializer.py`（注册型非死代码）、前端 26 个 `*.test.*`（测试套件）、根仓临时文件（gitignore 覆盖）、`openapi.baseline.json`（仅根仓一份）、环境变量三处罗列（教程 vs 权威有意分工）、`data/`/`__pycache__`（已忽略）。

### Fixed

- **工作台数据备份遗漏 + 拖拽手柄移动端失效 + 热力图标题错显示**：① `BACKUP_KEYS` 补 `wb_github_username`/`wb_widget_prefs`（导出/清空后恢复不再丢 GitHub 绑定与布局偏好）；② 拖拽手柄 `opacity-0 group-hover` → `opacity-50` 常显 + `touch-none`，触屏可按住拖拽排序；③ `widget-registry.ts` 中 `github-heatmap` 的 `titleKey` 误写 `'examCountdown'`（卡片标题错显示「考试倒计时」）→ 改为 `'githubHeatmap'`，i18n 补 `githubHeatmap`/`heatmapNoData`；硬编码「绑定」→ `t('heatmapBind')`。

## [1.0.0.七夕] - 2026-08-19

> **1.0.0 正式版 · 代号「七夕」（2026-08-19）** —— 首个稳定发布版本。六道 1.0.0 发布门槛全部明确并闭环：#1 契约门禁 + 管理员强制 2FA + ER-01（已闭环）、#2 管理员审计不丢（R17 闭环）、#3 端到端验收闭环（E2E 发布前必过，根仓 `e2e.yml` 加 `push:main` 保证 `main` 始终「可发布绿」）、#4 多实例幂等（arq cron 单点调度）、#6 D10 功能边界（Wiki/活动评价入 1.0、DM/相册延后）。门槛#5 外部监控有意延后（见下方 Known Limitations，风险接受）。四源核心版本号统一升 `1.0.0`（`make check-version` 通过），并引入**发布代号**机制：本版代号 `七夕`（七夕节当日发布），展示版 `1.0.0.七夕`。发布工具链见 `scripts/tag_and_release.sh`（F-9）。
>
> **版本号规则（2026-08-19 起）**：机器版本（pyproject / `app/__init__.__version__` / package.json `version` / uv.lock）保持 PEP 440 / semver 合规的三段式（如 `1.0.0`）；`codename`（节日标签如 `七夕` 或 MMDD 日期如 `0819`）为纯展示的发布代号，拼成 `1.0.0.七夕` / `1.0.0.0819`，仅用于页脚与 CHANGELOG 标题。npm / PEP 440 不允许 4 段或非 ASCII，故打包文件只用核心段。

### Added

- **P1-4 / C-15 BFF route 骨架生成器（方向 B/C 真交付）**：新建 `tools/scripts/fe/gen/bff-routes.mjs`，解析 `../openapi.baseline.json`（扫描 172 个 OpenAPI 路由操作），按「剥 `/api/v1` + `{param}`→`[param]`」对齐既有手写 BFF 约定，产出使用通用 handler 原语（`proxyBackend`/`bodyOrEmpty`/`arrayFrom`/`okJson`/`errJson`/`readJsonBody`）的 route 骨架。目录重映射（后端 `community/comments`↔前端 `replies`、`community/posts`↔前端 `topics`）与 Next 16 `Promise<{...}>` 动态路由签名均已对齐。`isCovered` 用精确归一匹配对账（修正前缀误判后 **109 COVERED / 63 NEW**，避免父路由误覆盖子路由）。默认 **dry-run** 落到 `.bff-scaffold/`（63 骨架 + `manifest.json` + `RECONCILE.md`），绝不覆盖 `src`；`--write` 仅新建不存在文件。生成器内部 `createSourceFile` 校验 **63/0**，并以临时 scoped `tsconfig` 跑**项目真实 tsc** 交叉验证 **0 报错**；其间发现并修复 `paramsType` 模板漏闭合泛型 `>`（`Promise<{...}` 缺 `>`）的真实 TS1005 bug（非校验器误报）。**随后 `--write` 落地**：仅新建 43 个单段骨架到 `src/app/api`（6 个已存在 route 命中 `existsSync` 跳过、0 覆盖），覆盖率 123/49；写模式漏 `mkdirSync` 父目录致首次 `--write` 崩溃（ENOENT），已补 `mkdirSync(dirname(...),{recursive:true})` 修复。交付后 `pnpm ts-check` 10 基线零新增、`pnpm check:bff-boundary` 通过。**覆盖率检测复盘修复**：`normalizeProxyPath` 原未剔除 GET 代理模板末尾的 `${url.search}` 查询串，致已交付的 15 个 GET 骨架/手写路由被误判 NEW（22→7）；已剔除该查询串使归一一致。最终对账 **165 COVERED / 7 NEW**（172 操作后）：剩余 7 个均为预存在手写路由（6 个用 raw `fetch` 直连后端、扫描器仅识别 `proxyBackend` 的 `path:` 故盲区；1 个 `auth/login` 手写代理到 `/auth/login-email` 属不同端点），均已被 `existsSync` 守卫正确跳过、非 C-15 缺口。

### Fixed

- **学习助手接口恢复基线契约**：提交 `4b09a9d` 曾将 auxilio 精简为 chat/path/recommend 并改挂 `/tools` 前缀，与契约基线（`/api/v1/auxilio/*`）及前端 BFF 脱节，且 chat 端点调用的 `service.chat` 等方法不存在 → LLM 区域误报「请先登录」（BFF 把 404 强转 401）。现恢复：`POST /auxilio/chat`（SSE 流式）、`GET /auxilio/conversations`、`GET /auxilio/conversations/{id}/messages`，新增 `GET /tools/auxilio`（薄弱点分析，`analysis_router`）；删除坏的 path/recommend；`get_db` 改为从 `app.database` 导入。前端 BFF 两个路由改透传真实状态码（不再 404→401）。OpenAPI 与基线逐项一致，冒烟：新端点未登录 401、旧路径 404。
- **LLM 配置与对话历史持久化修复**：① API Key 保存失败——前端 BFF `/api/workbench/llm-config` PUT 透传 camelCase（`apiKey`/`baseUrl`），与后端及 OpenAPI 基线 snake_case 契约（`api_key`/`base_url`）不符致 `api_key_encrypted` 恒为 NULL，BFF 增加字段映射；② assistant 回复不落库——`AuxilioService.persist_assistant_message` 用 `async with self.db.begin()` 包裹，而 chat 流式期间查询已 autobegin 事务，`begin()` 抛 `InvalidRequestError` 被 `except: pass` 吞掉，改为显式 `add + commit`（与 `create_conversation_with_user_msg` 一致）。端到端验证：BFF 保存返回 `configured: true` 且掩码可读回；规则模式对话的 assistant 消息与标题正常落库。

- **前端 BFF 代理路径 doubled `/community` 段修复（P1-4 / C-15 复查）**：复查发现手写 BFF route 存在系统性路径 bug——proxy 路径多一段 `/community`（`/community/community/...`、`/admin/community/community/...`），约 16 个文件 31 处；而 `proxyBackend` 已拼 `${API_PREFIX='/api/v1'}${path}`，后端 `community`/`admin_community` router 又各挂 prefix `/community`/`/admin/community`，导致前端代理到不存在的后端端点（404）。以 `/community/community/`→`/community/` 定向去重（尾随 `/` 形式天然规避 `admin_community.py:272 @router.post("/community")` 的真实 `/api/v1/admin/community/community` 合法例外，对应前端 `admin/community/series`）；验证 `grep '/community/community/'` 0 残留、`pnpm ts-check` 10 基线零新增。副作用：生成器覆盖率由误算 109/63 更正为 **123 COVERED / 49 NEW**（14 个操作从 NEW 转 COVERED），`--write` 仅新建 43。

- **前端 SSR hydration 安全化 + 登录态零延迟注水（根除 `/tools` Hydration failed）**：① 项目级 `useLocalStorage` schema 演进隐患根治——对象类型持久化偏好（`WidgetPrefs`/`PomodoroSettings` 等）原直接回写 `JSON.parse` 值不与默认合并，旧 localStorage schema 演进后缺字段致 `prefs.order is not iterable` 崩溃；新增 `mergeDefaultsWithStored`（仅当默认与存储值均为非数组普通对象时浅合并，数组/原语/类型不一致原样透传）；并使 hook SSR 安全（`useState` 首帧用 `initial` 匹配 SSR、存储值仅挂载后 `useEffect` 读入、监听 `storage` 事件跨标签页同步）。② `/tools` Hydration mismatch 根因修复——`tools` 注册表 `guest:false`（需登录），而 `useAuth` 乐观 `sessionMarker`（读 localStorage）使客户端首帧渲染 `<main>`、服务端（无 window）渲染 `null` → 结构冲突；`use-auth.ts` 新增 `hydrated` 挂载标志，乐观登录态仅 mount 后生效，首帧与 SSR 一致（保留硬刷新不闪登出）。③ SSR cookie 注水（关闭此前权衡项的「本次未做」）——新增 `server-only` 模块 `shared/server-auth.ts`（`getServerUser = cache(async)` 读 `ACCESS_COOKIE`/`REFRESH_COOKIE` 经合成 `Request` 携 cookie 头调 `proxyBackend('/auth/me')` 复用 `toSafeUserFromBackend`，后端不可达/任何异常降级 null）；根 `layout.tsx`（Server Component）解析服务端用户、`SWRProvider` 新增 `fallback` prop 经 `SWRConfig` 注入 `/api/auth/me` 初始值，使 SSR 与客户端首帧登录态一致、零延迟且无 hydration 警告（客户端挂载后 revalidate 自愈）。验证：`/tools` 200、未登录 SSR 一致渲染 `null`、伪造 cookie 请求安全降级 null（proxyBackend 分支无崩溃）、`pnpm ts-check` 10 基线零新增（13 总数 = 10 基线 + 3 用户在制 `WidgetSizeKey`/`WidgetSizeSpec` WIP 错误，非本次引入）。

### Changed

- **D10 功能边界拍板（1.0.0 scope）**：社区四件套边界确定——Wiki、活动评价纳入 1.0.0 规划（随 1.0 交付跟进）；私信 DM、相册延后至 P1 波次（1.0.0 不含）。活动评价随已有活动模块在 1.0 补；Wiki 作为新模块规划推进。
- **1.0.0 发布门槛#3 定义补列并闭环（SSOT 同步）**：门槛#3 原清单未枚举，已于 2026-08-19 补列定义为「端到端验收闭环（E2E 发布前必过）」——真实 docker-compose 全栈部署形态下核心用户旅程 E2E 全绿，作为 1.0.0 发布前必过（非仅 nightly）；**已于 2026-08-19 闭环**：根仓 `e2e.yml` 加 `push:main` 触发，合并到 `main` 即跑全栈 E2E，保证默认分支「可发布绿」（保留 nightly + 手动），对应 P0-4。见 `docs/项目待办事项-优先级重排.md`。

- **发布工程收口（F-9 / C 收口）**：新增 `scripts/tag_and_release.sh`——自动撰写 changelog（将 `[Unreleased]` → 指定版本 + 日期）并同步四源版本号（pyproject / `__init__.__version__` / package.json / uv.lock），跑 `make check-version` 自检后给出打 tag 指令；版本号四源统一升 `1.0.0`，`make check-version` 通过。

- **P1-4 / C-15 BFF 样板生成（方向 A 首步·通用响应原语，已启动）**：勘察纠正——C-15 缺口非类型（前端 `gen:api-types` 已用 `openapi-typescript` 从 `openapi.baseline.json` 生成 `backend-api.d.ts`）；真正重复在 140 个 `route.ts` 运行骨架的样板（body 兜底 / 数组提取 / 成功·错误响应 + Cookie 接线 / 安全读体）。`backend-client.ts` 已有成熟 `to*` schema 翻译助手（~13 个），故本次只抽**通用 handler 原语**：新增 `bodyOrEmpty` / `arrayFrom` / `okJson` / `errJson` / `readJsonBody`（与 `proxyBackend`/`normalizeError`/Cookie 助手同文件）。示范重构 `src/app/api/tools/component-registry/route.ts`（GET/POST）改用原语，行为不变。`ts-check` 无新增错误（仅基线 10 处无关错误）；`check:bff-boundary` 通过。后续：将更多 route.ts 迁移到原语，再上 route 骨架生成器（B/C）。**本 batch 已迁移 4 个 route.ts**（component-registry/overview/favorites/follows，覆盖纯 GET、软错误分支 + 自定义 map 三种模式），ts-check 无新增错误（基线 10）、check:bff-boundary 通过。

- **AR-S2 周期任务空转循环治理（轻量闭环）**：`exception_retention` / `token_gc` / `data_retention` 三处启动钩子由常驻 `asyncio.create_task` 循环改为启动兜底跑一次 `_purge_once()`，消除每实例每 worker 各起空转循环；跨实例幂等仍由各 `_purge_once` 内的 `pg_try_advisory_xact_lock` 保证（仅一个实例真正执行）。`view_count` 因进程内存 `_pending` 需周期落库，循环保留（已用 Redis `getset` 原子保证单点）。周期性调度已落地（方案 B）：`WorkerSettings.cron_jobs` 注册 `token_gc`（每小时）/ `data_retention`（每日 03:00）/ `exception_retention`（每日 03:30）三个 cron 任务，由 arq Redis 锁保证集群内单点；web 启动兜底（`startup_*`）保留为 cold-start 兜底。新增 `app/services/maintenance_cron.py` 包装层接收 arq 注入的 `ctx` 并复用既有 `*_INTERVAL_SECONDS` 禁用开关。`test_maintenance_tasks.py` 同步修复因轻量闭环删除循环导致的陈旧测试并补充 cron 覆盖。

- **R17-closeout 管理员审计不丢（门槛#2 闭环）**：逐处核验原 12 处 best-effort `audit.record()`。其中 3 处为管理员操作审计（`password_reset.approve/reject`、`join.approve/reject`，`actor_id=admin_id`），迁 `record_atomic` 并移除其提前 `commit()`，使「状态变更 + 审计」同事务原子提交（审计写失败则整体回滚，杜绝审计丢失）；其余 9 处为 用户级/混合 helper（`auth_service`×8、`event_service._audit`），判定非关键、有主事务兜底（`_record_login_history` / 用户创建已落库），仅加 `# 非关键审计，允许 best-effort` 注释。同步修复 `auth_service` 构造函数（`AuditService()`→`AuditService(self.db)`），使既有的 `create_user_with_audit` 管理员建号原子审计真正可用（原默认构造会令 `record_atomic` 抛 RuntimeError）。`user_service._audit_admin`（`AuditService().record()` best-effort 管理员审计）超出原 12 处范围，记为 P2 后续，本次未改。4 文件 `py_compile` 通过。

- **P2-7 `user_service._audit_admin` 管理员审计原子化（门槛#2 补强）**：`user_service` 构造函数注入 `AuditService(self.db)`，使 `_audit_admin` 由 best-effort `AuditService().record()` 改为 `record_atomic` 同事务提交；同步移除 4 处管理员操作（user.update / enable·disable / reset_password / delete）的提前 `commit()`，使「状态变更 + 审计」原子提交，审计写失败整体回滚（杜绝管理员审计丢失）。`py_compile` 通过；管理员路径集成测试应覆盖。

- **P1-1 `GET /health/security` 脱敏（ER-48 / AR-S1 闭环）**：选择 A1 方案——保留无鉴权运维探针（k8s/探针约定），但移除返回体中 `auth` 配置姿态块（`AUTH_ENABLED`、`TOTP_ENCRYPTION_KEY_set`），仅保留组件健康/连通性状态（`rate_limiter` / `token_blacklist` / `migration` / `multi_instance`），杜绝向匿名探针泄露安全态势。新增断言测试 `test_health_security_does_not_leak_auth_posture`（`tools/tests/core/test_app_factory.py`）验证返回体不含 `auth`/`enabled`/`totp_encryption_key_set`。`main.py:214` 改后 `py_compile` 通过。

- **P1-2 / C-16 部分治理（方向 C）**：仅治真代码味——`user_service` 管理员删号级联清理原用 `text(f"DELETE FROM {table} WHERE user_id=:i")` 动态拼接表名（f-string 插值），改为三条字面量 `text()` 语句（表名取自固定白名单，无注入风险）；顺带修正 `await self.db.delete(target)` 原被误缩进进 `for` 循环（每表执行一次）的隐患，移出循环（同事务内 `db.delete` 幂等，行为不变）。其余 23 处 `self.db.execute` 均为参数化 SQLAlchemy Core 查询（非注入风险，纯架构债），按方向 C 骑乘 C-17 上帝模块拆分时下沉 repository，不在 1.0.0 前单独全量重构。`py_compile` 通过；`app/services` 内已无 `text(f"` 动态 SQL 残留。

- **P1-3 门面与验证器收口（按代码重释；AR-M1…X1 原定义已随初版 SSOT 删除）**：子项① 清理死代码——`app/core/validators.validate_email` 全仓零调用（email 实际由 schema 的 pydantic `EmailStr` + `validate_email_length` 承担），删除该函数及其在 `tools/tests/core/test_validators.py` 的测试类；保留 `MAX_EMAIL_LENGTH` 常量（仍被 `auth`/`password_reset` schema 引用）。`py_compile` 通过，`test_validators.py` 13 passed，全仓无 `validate_email` 残留引用。后续子项（email 校验一致性审查、门面 facade 勘察）待继续。

- **P1-3 子项② email 校验一致性审查（已完成，不改宽松约定）**：结论——输入侧（`UserBase`/`RegisterRequest`/`ResetRequestCreate` 等）用 `EmailStr` 强格式 + `validate_email_length` 长度上限（MAX_EMAIL_LENGTH=100），双保险；输出侧 `UserOut.email: str` **仅长度校验、不强制格式**，属有意设计（历史/测试数据可能用保留域名 @test.local/@example，改回 `EmailStr` 会让管理员用户列表因 422 变空）。新增 `tools/tests/schemas/test_email_validation.py`（8 passed）锁住两套行为作回归护栏，重点护栏 `UserOut` 不被误改 `EmailStr`。

- **P1-3 子项③ façade 勘察（已完成，未改代码）**：DI 门面主体健康——`app/dependencies_services.py` 集中 32 个 `get_X_service` 工厂，绝大多数 router 经 `Depends(get_X_service)` 注入，路由聚合（`app/api/v1/__init__.py` 单一 `api_router`）也干净。发现门面泄漏（绕过 facade 手搓 service）：`TOTPService` 无工厂→`feature_visibility.py` 内联 `TOTPService(db)`；`AuxilioService` 有工厂但 `auxilio.py` 仍内联 3 处；`WorkbenchService`/`ContributionService` 无工厂→`workbench.py` 内联 2 处；`community.py:122/671` 直接 `Depends(get_db)` 手搓查询（待确认是否真无 service 可代）；`middleware/rbac.py:111` 非 Depends 上下文另行评估。

- **P1-3 子项④ façade 收口（方向 B 首点，已完成）**：补齐缺失的 `get_totp_service` 工厂（`app/dependencies_services.py`，与 `get_auth_service` 同级、注入请求级 `AsyncSession`），并将 `app/api/v1/feature_visibility.py:93` 的 `totp = TOTPService(db)` 改为经 `Depends(get_totp_service)` 注入；同步清理该 endpoint 因改走 facade 而变为死代码的 `db` 参数与 `AsyncSession`/`get_db`/`TOTPService` 三处 import。`py_compile` 通过；router 层已无 `TOTPService(db)` 内联；`test_totp.py`/`test_totp_service.py`/`test_app_factory.py` 共 21 passed。余下泄漏（auxilio/workbench/community）待后续点收口。

- **P1-3 子项④ façade 收口（续点 A · workbench，已完成）**：新增 `get_workbench_service`/`get_contribution_service` 工厂（`app/dependencies_services.py`，与既有工厂同范式注入请求级 `AsyncSession`）；将 `app/api/v1/workbench.py` 三处 endpoint 内联 `WorkbenchService(db)`/`ContributionService(db)` 改为经 `Depends(get_workbench_service)`/`get_contribution_service` 注入，并删除相应 endpoint 因此变死的 `db` 参数（其余 endpoint 仍用 `db`/`AsyncSession`/`get_db`，保留）。`ContributionService`/`WorkbenchService` 仅作参数类型注解，import 保留。`py_compile` 通过；router 层已无 `WorkbenchService(`/`ContributionService(` 内联。

- **P1-3 子项④ façade 收口（续点 B · auxilio，已完成）**：`app/api/v1/auxilio.py` 的 `chat` endpoint 注入 `service: AuxilioService = Depends(get_auxilio_service)`（工厂早已存在），将 3 处内联 `AuxilioService(db)`（append_user_message / create_conversation_with_user_msg / persist_assistant_message）收敛为同一注入实例；`db` 参数因该 endpoint 仍需裸 `db.execute`/`db.add`/`db.commit` 与 `auxilio_agent.run_chat(db,...)` 而保留。`py_compile` 通过；router 层已无 `AuxilioService(` 内联。

- **P1-3 子项④ façade 收口（续点 C · community，勘察结论：延期）**：`community.py:122`（`list_members`，FTS + JSONB 裸查询）与 `community.py:671`（`list_tags`，裸查询 + Python 聚合）均为**无 service 包裹的裸查询 endpoint**，全仓无 `list_members`/`list_tags` service 方法可代。最小 facade 收口（仅走现有工厂）不适用；若要做需新建 service/repo 方法抽取查询，属 C-16「service 直查下沉」/ C-17 上帝模块拆分范畴，不在本次最小收口内——判定延期，不改 community.py（与 C-16 方向 C 不越界口径一致）。

- **Auxilio v1 上线（LLM 对话重构收口）**：LLM 对话升级为「Auxilio v1」卡片（`widgets/llm-widget.tsx`，primary 左主列、对话优先布局）；头部「用量与设置」统一按钮展开用量统计 + 模型接入设置面板；工作台布局改为问候条顶部全宽 + Auxilio v1 左主列 + 其余功能右栏；删除旧 `/tools/auxilio` 分析页与工具区入口（前后端可见性注册表同步删 `tools-auxilio`、`wb-assistant-chat` 并入 `wb-llm-usage`）。

- **工作台（Workbench）像素化（方案 A 完整融合，FrontDoc-UID §15.12）**：`/tools` 页根已带 `pixel-page`，本次把可见工作台推入融合层——① 9 个 widget 盒装卡（greeting/today-tasks/github-heatmap/llm-widget/quick-notes/pomodoro/exam-countdown/llm-usage-stats/assistant-chat）`card-minimal`→共享 `<DnaCard corner={…}>`（角标 HI/TSK/GIT/AUX/NOTE/FCS/EXM/MEM/CHAT），非嵌入态独立卡保留 `card-minimal` 避免 DnaCard 嵌套；② `today-tasks` 任务列表 `<ul>/<li>`→**A 索引铁路** `.idx-rail`（序号/标题/元数据含逾期态/箭头），新增 `.dna-card .idx-rail .idx` 作用域遮罩跟随卡面；③ 顶部 4 CTA 转 `pixel-outline`、「清空」转新增 `pixel-danger`，各 widget 内按钮（刷新/用量入口/保存/newChat/发送/番茄钟三键/便签新增）统一转 `pixel`/`pixel-outline`；④ 顶部新增可见 `<SectionMarker>[ 01 ] 工作台</SectionMarker>`；⑤ `globals.css` 新增 `.btn-pixel-danger`/`.btn-pixel-danger-sm` 与 `.dna-card .idx-rail .idx` 覆盖。`ts-check` 持基线 10 错、`lint` 持基线 3 错、next build 通过，无新增回归。

- **P1-6 / C-19 前端数据获取收敛（共享原语）**：新建客户端共享原语 `src/shared/hooks/use-api-request.ts`——`apiRequest<T>(path, init?)` 薄封装（自动 JSON 序列化 body + Content-Type、统一错误提取兼容 `message`/`error`、网络异常兜底、不抛异常返回 `{ok,status,data,error}`）+ `useApiRequest<T>(path, options?)` hook 版（data/error/loading 态 + `run()`/`immediate`）；新增 `isRawBody` 检测，对 `FormData`/`Blob`/`URLSearchParams` body 原样透传以支撑文件上传。与后端 `server-only` `backend-client.ts` 互补，构成全栈请求原语对。
- **P1-6 / C-19 前端数据获取收敛（全域迁移·覆盖）**：按用户拍板的 **B 策略**（组件内联 fetch 仿 `useFollow` 抽专用 `use-*` hook；已是 `use-*` 的就地换 `apiRequest`）全域迁移，覆盖 community（15 文件：6 manager + 8 非 manager + notification-bell）/ admin-*（14）/ tools/*（11，含 exam/task/dev-center）/ auth-profile（7）/ events（2）/ about（1）/ workbench（5，仅非 SSE 部分）/ shared-hooks（3）/ misc（3），合计约 61 文件。每文件 `pnpm ts-check` 全程 10 基线零新增，调用方无感。
- **P1-6 / C-19 前端数据获取收敛（闭环结论）**：客户端裸 `fetch(` 全域清零，仅余受控排除项（BFF `route.ts` / `server-only` `backend-client.ts` / 原语自身 / SWR 基础设施 `swr-provider`·`use-auth` / `assistant-chat` SSE 流式），C-19 客户端收敛彻底闭环。

---

### Known Limitations

- **门槛#5 外部监控/可观测性有意延后（风险接受）**：1.0.0 不含集中式 APM / 外部告警链路（Prometheus `/metrics` 端点已具备，但缺 Grafana / Alertmanager 等外部看板与告警）。依据 SSOT 门槛#5 决策：当前用户规模 <200，运维风险可接受，不阻塞 1.0.0；规模化触发后立项（见 P2-4 / EX-1）。发布后须由运维按 `BackDoc-SLO.md` 自行接入监控，本项不作为 1.0.0 验收项，特此显式记录以免事后误读为遗漏。
- **上帝服务拆分（C-17）与 repo 巨型文件（C-18）延后至 1.0.0 之后**：`user_service.py` / `auth_service.py` / `community_repo.py` 等仍 >700 行，属已知架构债，已在 SSOT 降为 P2（"查询层治理"专题，分阶段可回滚），不在 1.0.0 验收范围。
- **DM 私信 / 相册延后至 P1 波次**：依 D10 边界拍板，1.0.0 不含。

## [0.9.9]

### Security

- **ER-01** 社区 `tags` 过滤参数化（`community_repo.py`），消除 SQL 注入气味；**ER-17** 社区 IP 匿名化哈希密钥配置化（`COMMUNITY_IP_HASH_SECRET`），缺失/过短启动 fail-fast。
- **ER-18** 修复 Auxilio 工具用量越权获取全站数据（`get_api_usage_stats` 加 `user_id` + `is_admin_role` 门禁）；`workbench /stats/api-usage` 改强制管理员 + 2FA。
- **ER-19** LLM 提示注入结构化隔离（`wrap_user_profile_field` / `wrap_untrusted_tool_result` 显式标注 UGC/工具结果「不可信、严禁当指令」）。
- **ER-20** RBAC 缓存失效 fail-open → fail-closed（高危路径 `raise_on_failure=True`），消除降权后权限残留窗口。
- **管理员强制 2FA（P0）**：新增 `require_admin_2fa` 工厂；admin 四域 + workbench 接入（未启用即拒 `TWO_FACTOR_NOT_SETUP`）。修复原 `Depends(require_admin_2fa)` 误传工厂函数本身致门禁在 HTTP 层完全失效的真实安全缺陷——5 处改 `Depends(require_admin_2fa())`，`test_http_admin.py` 5/5 全过。
- **ER-26** 补齐深遗留：`requirements.txt` / `requirements.lock` / `requirements-dev.lock` 三处 cryptography 约束由 45.0.7 同步升至 50.0.0（CI 实际装这两锁，此前仍含 13 条 CVE-2026-*）。

### Performance

- **ER-16** 社区帖子列表交互标记 N+1 批量预取（`get_interaction_target_ids`，2N→2）。
- **ER-21** 关注用户列表计数/关注态 N+1 批量预取（`bulk_counts` + `bulk_is_following`，~3N→3）。

### Added

- **工作台 LLM 化**（规划：工具页→工作台改造方案）：Auxilio 升级 LLM Agent（OpenAI 兼容 + Anthropic 双协议 SSE 流式、7 个 Skills 工具调用、无 key 自动降级规则模式）；`conversations` / `chat_messages` 表；前端对话 UI（流式打字机 + 工具调用状态卡 + 历史会话）；LLM 用量统计 + 用户级 API Key（`llm_configs`，AES-256-GCM 复用 TOTP 加密原语）；新增 `GET /workbench/stats/llm-usage`、`GET/PUT /workbench/llm-config`。
- **功能模块可见性管理**（规划：功能模块可见性管理方案）：后端 `feature_visibility` 路由（GET 公开 + PUT root + 2FA 校验 + 审计，复用 `settings` 表、无新表/迁移）；前端全组件可见性注册表（37 组件 5 组）+ `VisibilityGate` + 导航/user-menu 改造 + 管理面板。
- **测试体系加固（ER-02/11/12）**：repo 层真实 DB 集成测试 3 文件 21（community 8 / events 6 / tools 7）；HTTP 层 3 文件 + `test_http_admin` 共 24+5；安全/合规服务单测 12（`test_compliance_services` 7 + `test_admin_2fa` 5）；E2E 改 nightly 全栈（ER-14）。
- **并发/竞态集成测试（ER-44）**：`test_concurrency_integration.py` 8 测试（真实 Redis + PG，`asyncio.gather` 并发）：限流 30 并发恰 5 放行（Lua ZSET 原子性）、黑名单同/异 jti 幂等与隔离、令牌并发轮换 ×10 同 family、revoke 与 refresh 终态一致。
- **覆盖率门禁（ER-45）**：`diff_coverage.py`（仅标准库，新增行覆盖率 <80% 即 exit 1）+ ci.yml PR diff gate；`pytest.ini` 移除全局 `--cov`；`.coveragerc` fail_under 70→72。

### Changed

- **社区 God Module 拆分收官（ER-15 Phase 0~4）**：`community_utils` 提取（Phase 0）→ 通知事件化（Phase 1）→ 互动服务拆分 `community_interaction`（Phase 2）→ Post/Comment/Notification/Favorite/Feed 服务（Phase 3）→ Category/Report/Series/Feed 服务（Phase 4），删除 `community_service.py`；API 契约不变、432 passed 无回归、OpenAPI 零漂移。
- **错误码业务自治**：Auth/Community/Event/Authorization/User 5 域 `errors.py`（51 处调用点，`ErrorCode.<域>.X` 形式不变）。
- **治理 / 可观测 / 文档（ER-04/05/06/08/09/10/31 + DocGov-C / CodeGov-B1 / F2 / AL-1）**：OpenAPI 契约门禁修复 + 基线重冻 176 路由（ER-04）；生产 `LOG_PROFILE=prod`（ER-05）；`/metrics` Prometheus 端点（ER-06）；死链审计脚本 + CI（ER-09）；前端覆盖率 + PR diff-coverage 80%（ER-13）；E2E nightly 全栈（ER-14）；路由层直写收敛 `WorkbenchService` / `AuxilioService`（CodeGov-B1）；BFF 安全边界 CI（AL-1）；根文档索引补登演变历史（ER-31）；Node 统一 22；`uv.lock` 重生成。
- **运维与发布部署护栏（ER-29/33~40）**：compose 全服务 `mem_limit`/`cpus`/healthcheck/优雅停机/日志卷；多 worker（`--workers`，exec 形式保优雅停机）；`REQUIRE_REDIS_FOR_SECURITY=true`；`DB_AUTO_CREATE_DATABASE=false`；密钥必填守卫（`SECRET_KEY`/`TOTP_ENCRYPTION_KEY`/`AUTH_SESSION_SECRET`）；`check_version_sync.py` + `make check-version` + e2e.yml 四源版本 CI 校验（ER-33）。
- **代码质量与架构（ER-22/24~27/30/32）**：`constants.py` 集中 12 常量（ER-24）；浏览计数 Redis 原子 + 异步批量落库（最终一致，ER-22）；发布与迁移解耦（独立 `migrate` 服务，ER-30）；循环依赖去味（`user_service`/`exception_retention` 惰性提顶层，ER-27）；cryptography 50.0.0 清 CVE（ER-26）；`tools/docs` 索引修复（ER-32）。
- **ER-28 RBAC 单向解耦核查（架构质量）**：`sys.modules` 探测确认 `rbac_service→rbac_assignments→rbac_seed_data`、`rbac_init→rbac_seed_data` 为严格单向 DAG，无任何反向/循环依赖，「四模块互相 import」描述已过时；AL-6 的 RBAC 单向解耦目标已达成，无需代码改动（2026-08-11 结论）。
- **ER-46 测试目录结构核查（测试）**：评估后维持 `tools/tests` 与 `app/` 分离的现有布局——迁移影响 39 处代码内引用 + 6 个文档/CHANGELOG 引用 + conftest `ROOT_DIR` 层级 + import 方式 + CI 路径，成本高风险低，与「可低优先」定位相符（2026-08-11 结论）。
- **仓库根目录清理（CS-01，P1 清理）**：根 `.gitignore` 追加 `*.txt` 临时日志段 + `.trae-cn/`；`phase3-*.json` 阶段产物归档移出根目录；`dump.rdb` 等已忽略产物按需清理（2026-08-13 收口）。
- **前端消费者契约（ER-47）**：`openapi-typescript` 生成 `backend-api.d.ts`（12387 行入库）；`backend-client` 引用生成 schema，ts-check 拦截字段漂移，修 5 个 auth 路由 + 测试 mock；ci.yml API types drift gate。
- **测试基础设施（ER-41/43）**：消除固定 id=1 依赖（新增 `admin_user` fixture，19 处硬编码 `1` 替换）；服务单测改真实 `__init__(db=mock_db)`（9 处 `Service.__new__()` 重构为 fixture）。
- **架构快赢（ER-55/56）**：`config.py` 按域拆 6 子模型（database/security/web/rate_limit/ops/business），`Settings` 多继承保持 `settings.X` 扁平；`events.py` 复用模块级应急 loop 消除启动期反复 `asyncio.run`；`COMMUNITY_LIMITS`/`MENTION_PATTERN` 迁入 `constants.py` 单一来源。
- **版本四源对齐 0.9.9（ER-10）**：pyproject / `__init__.__version__` / package.json / uv.lock 统一。
- **仓库死代码/死配置/临时文件清理（C-1~C-6，2026-08-17）**：前端 0 字节临时文件 `git rm --cached` + `_tmp_*` 忽略（C-1）；删后端 `.coverage.Mac.*` 残留（C-2）；删 `pyproject.toml` 死配置段 `[tool.basedpyright]`（C-3）；删前端死代码 `mail.ts` + `nodemailer`/`@types/nodemailer` 依赖 + 清理 `index.ts` 注释（C-5，F-A1）；删一次性 Alembic 修复脚本 `scripts/sync_alembic_version_ids.sql`（C-6，F-A2）；根仓 `be_err.txt` 等经核实不存在（C-4，CS-01）。
- **依赖声明双轨收敛为 uv 单源（C-7，N-07/CS-05）**：`pyproject.toml`+`uv.lock` 为唯一来源，`requirements*` 六份由 `uv export` 重新生成；`pyproject` 增 dev extra；Makefile 加 `deps-export`；`test_dependency_manifest.py` 改验 `pyproject ⊆ uv.lock`。
- **三份 .gitignore 公共段漂移补齐（C-8，N-04）**：根/后端/前端 `.gitignore` 补齐 `.devlogs/`/`.dev.pid`/`.trae-cn/`/`.workbuddy/`；新增 `scripts/check/check_gitignore_sync.py` + `make check-gitignore-sync`（正/负向测试通过）。
- **CI 系统双轨定位（C-9，N-08）**：保留 `Jenkinsfile` 作等价备用；`RootDoc-Deploy.md` 新增 §八 CI 分工表（ci.yml 主验证门禁 / Jenkinsfile 备用+ER-09），原 §八顺延 §九。
- **三份 .env.example 职责矩阵（C-10，N-14）**：17 组变量职责矩阵入 `RootDoc-EngConv.md` §5.1（含前端遗留变量说明）。
- **文档地图与状态修正（C-11/C-12/C-13，F-*）**：孤儿调研文档 `docs/公共组件调研报告.md` 登记入 `docs/README.md` 文档地图（C-11，F-B1）；社区重构文档 `BackDoc-Refactor-CommunityService.md` 状态改"已完成"+§8 排期+测试路径修正+索引同步（C-12，F-8/F-B3）；历史分卷 `项目演变历史-0.9.5/0.9.6/0.9.7.md` 合并为 `项目演变历史-0.9.5~0.9.7.md` 并删三卷、同步索引（C-13，F-B2）。
- **前端 CHANGELOG 补 0.9.9 锚点（C-14，F-4 关联）**：`CS-Web-Frontend/CHANGELOG.md` 补 `[0.9.9]` 段+链接+header 边界说明（权威以根仓 CHANGELOG 为准）。

### Fixed

- **tags JSONB 过滤根因修复**：列类型 `JSON().with_variant(JSONB)` 时 `contains` 退化为字符串 `LIKE` 且实际调用抛 `invalid input syntax for type json`；统一 `type_coerce(列, JSONB).contains([tag])` 走 `@>`（5 处同源：community_repo.py:113 / community.py:121 / event_repo.py:36 / tools_repo.py:40 / tools_repo.py:235）。
- **组件注册表 500**：`POST /api/v1/tools/component-registry` 误声明 `response_model=dict` 与返回 `ComponentItemOut` 不匹配，移除 `response_model` 后恢复（tools.py:606）。
- **全量测试失败清零（2026-08-11，10 个全部定位修复）**：dependency_manifest cryptography 双源漂移、maintenance_tasks monkeypatch 目标、phase4 view_count 异步、rate_limit Redis 键跨运行残留、api/v1 分页断言补 `total_pages`、queue_worker 闭包 `Function.name` 对齐；终态 432 passed / 0 failed / 1 skipped。

### Docs

- **文档冲突修正（版本事实 0.9.8 → 0.9.9，2026-08-17）**：`文档冲突审查` 多份页面版本号对齐 0.9.9——待办 F-11 四源版本（F-1）、`RootDoc-Deploy`（F-2）、根 README（F-3）、`api-reference`/`README` 0.9.8 冻结契约标注（F-4）、Onboarding 进度（F-5/F-10）、多份后端文档页眉刷新 0.9.9（F-6）随上述 C-* 动作一并修正；社区重构文档状态（F-8）见 C-12。剩余 F-9（alembic heads 实测复核）转入待办 `项目待办事项-优先级重排.md`。
- **规划长文归档处置（C-20，2026-08-18）**：`docs/plans/` 两份规划（工具页→工作台改造方案、功能模块可见性管理方案）落地结论均已归档于 `[0.9.8]`/`[0.9.9]` Added，无需重复登记；未完成残余项（LeetCode 热力图、每周复盘卡、系统状态角标、浏览器 Notification 可选增强、数据导出、可见性定时上下线）移交 `docs/项目待办事项.md`（2026-08-18 并入 `docs/项目待办事项-优先级重排.md`，见 C-21）；删除 `docs/plans/` 文件夹，同步根文档地图（`docs/README.md`）与 `docs/DocGovernance.md` 引用。
- **待办 SSOT 合并（C-21，2026-08-18）**：原 `docs/项目待办事项.md`（待办 SSOT）经全量条目对照并入 `docs/项目待办事项-优先级重排.md` 后删除——已迁移条目（P0/P1/P2/P3 主体）按重排结果生效；未迁移条目新建「附录 A」收纳（AR-M3、F-9、LeetCode 热力图、可见性-定时上下线、ER-49/50·51/52/54·57、Phase 4 纵深）；同步修正 D10（已拍板：Wiki/活动评价纳入 1.0、DM/相册延后 P1）与 AR-S2（轻量闭环已落地）结论；重排文件升级为待办唯一权威跟踪（SSOT）；全仓 14 个文档引用点统一改指新文件名。
- **文档治理收口固化（DocGov，2026-08-09 批次，2026-08-19 补登）**：系统性跨仓死链修复（13 处 + 1 提及，根→子仓 `../CS-Web-*`、子仓→根 `../../../docs/`、子仓↔子仓 `../../../CS-Web-*/tools/docs/`）；坏锚点修复 3 处（`BackDoc-Infra` `#六迁移验证`→`#六迁移验证migration_verification`、`RootDoc-MigEval` 全角 slug 归一，共 2+1 处）；ADR 抽离 `RootDoc-ADR.md`（设计决策 SSOT）并解除活文档对归档演变历史的链接（17 处 markdown + 1 处代码注释）；超大文档章节速查导航注入（5 份 600+ 行：`FrontDoc-01-Arch`/`BackDoc-01-Arch`/`BackDoc-Infra`/`FrontDoc-UID`/`FrontDoc-Ops`），幂等脚本 GitHub-slugify 生成；版本号四源同步约定（pyproject/`__version__`/package.json/uv.lock，改版本须四处同改）+ 术语一致约定（repo 层「子仓库(submodule)」、代码内「子模块/模块」）固化入 `docs/DocGovernance.md` §3 反模式；`monorepo-doc-audit` Skill 锚点腐化审计脚本固化（全角标点 slug 口径）。复跑双审计确认 0 死链 + 0 坏锚点。

---

## [0.9.8]

### Added

- **工作台（Workbench）前端模块**：个人待办、番茄钟播放器、GitHub 热力图、API 调用统计、考试倒计时、快捷便签、学习助手对话等 widget（注册表配置驱动）。
- **Auxilio 学习助手**：基于规则的技能 + 可选 LLM（OpenAI 兼容 / Anthropic 双协议流式），SSE 流式对话，会话持久化。
- **后端路由与服务**：`/api/v1/workbench/*` 与 `/api/v1/auxilio/*`（`contribution_service` / `auxilio_agent` / `llm_client`）、`api_usage` 统计中间件；数据表 `contribution_cache` / `api_call_logs` / `conversations` / `chat_messages` / `focus_sessions`；可选 LLM 配置（`LLM_PROVIDER` / `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`）。
- **中文全文检索可靠化（FTS）**：Alembic 迁移 `chinese_fts_zhparser`（DO $$ 条件安装 zhparser + chinese 配置，不可用时回退 simple）；community 改用 `settings.FTS_CONFIG`；`docker/db` 自定义镜像。
- **分页契约**：`PaginatedResponse` 增 `total_pages`；`PaginationParams` 支持 `page`/`page_size` 别名。
- **i18n 收尾**：约 800+ keys、24+ namespaces（admin-events/roles/notifications/join/logs、communit&#x79;*、tools*、events、auth 等）；经核查前端 `.ts/.tsx` 已无硬编码中文、无 snake_case 后端字段残留。
- **R14 备份中断修复**：compose 新增 `backup` sidecar（每日 03:00 `backup_db.sh`，保留 14 天）+ `backups` 持久卷。
- **L9 数据保留策略**：`data_retention.py`（登录 90 天 / 审计 365 天，advisory lock 防多实例重复）；`LOGIN_HISTORY_RETENTION_DAYS` / `AUDIT_LOG_RETENTION_DAYS`。

### Changed

- 部署拆分：`Makefile dev-up` 改 tmux 统一会话（`cs-dev`）；前端风格 camelCase 全量统一（0 命中残留）；安全静态扫描脚本 `scan_security.py` 接入 CI（G1 门禁补充）。
- 文档重叠核查：`CLAUDE.md`/`AGENTS.md`、`MigEval`/`MigV`、`FrontDoc-Ops`/`BackDoc-Conv`、`RootDoc-EngConv` 分工清晰不重叠，无需合并；前端 `tools/docs/` 补 `README.md` 索引。

### Fixed

- **前端构建体积优化**：`.build` 由 4.4G 降至 44M（清理 Turbopack 缓存 + 统一 tsup 输出 `dist/server.js`）；修复 `tools/scripts/*` 的 `projectRoot` 路径 bug（误指 `tools/` 而非根）。
- **BFF 健康检查转发路径 bug**：`/api/health` 改转发 `${BACKEND_URL}/health`（后端 root 路由，非 `/api/v1/health`）。

### Docs

- **P2/P3 过时段归档**：R1（SQLite 写瓶颈）/ R10（多实例速率限制）/ R20（单实例扩展）/ L6（PWA）/ L9（数据保留）等经代码核查已实现；部分条目因架构演进（前后端分离、BFF 收口）已过时，从待办移除归档。

---

## [0.9.7]

> 含 0.9.5 / 0.6 / 0.7 版本号演进 + 1.0.0 准备期 + P0/P1/P2 闭环（2026-08-06）。

### Changed

- **版本号演进**：0.9.5 / 0.9.6 / 0.9.7 连续升至 0.9.7（前端 `package.json`、后端 `__version__`、前端 `CHANGELOG` 锚点同步；后端 `__version__` 由 1.0.0 校正回归至 0.9.x 语义版本线）。
- **1.0.0 准备期 Blockers/GA 闭环**：B3 前端容器移除 `SQLITE_DB_PATH` 统一纯 BFF；G1 `pnpm audit` 改阻断；G2 固化 pytest 依赖（对齐 `requirements-dev.lock`）；G3 冻结 `/api/v1/**` 契约（`openapi.baseline.json` 159 路由 + `make contract-check`）；G4 onboarding 手册 + 文档顶部真实进度标注。
- **B1 纯 BFF 收口**：删除前端 `src/modules/*/server/` 9 模块 79 文件 + `src/shared/db` + `audit.ts`（孤儿死代码，业务流量早已薄转发后端）；通知事件总线 `appBus` 移除（无 `emit` 调用）；1.0.0 Blocker B1 闭环。

### Added

- **P0 闭环**：Phase 6 社区搜索 GIN+tsvector + 事件总线跨实例（ADR-014，arq/Redis 广播，`MULTI_INSTANCE` 开关）；PRR-P0-1 安全关键路径 Service 单测 63（password_reset/verification/totp/oauth/email）；PRR-P0-2 备份脚本 `backup_db.sh`（RTO=4h/RPO=24h）；PRR-P0-3 SLO 可观测性基线 `BackDoc-SLO.md`；P0-后端CI GitHub Actions `ci.yml`（与 Jenkinsfile 对等）。
- **P1 闭环**：`data/` 占位固化；文档对齐真实态；前端 SQLite 清除；CI 集成测试；前端 CI 漏洞阻断；前端仓库清理；前端大页面拆分；新手手册 `Onboarding`；pytest 依赖固化；方案B 波次2/3 收敛；密钥轮换 runbook `BackDoc-KeyRotation`；Alembic downgrade 往返 + 多 head 修复；Redis+workers 校验；Dependabot；`console.error` 清理；健康检查 `/health/events`、`/health/security`。
- **P2 闭环（1.1 规划项提前完成）**：CI 集成测试手动触发 + E2E（PRR-P2-7）；OTel 导出 `otel-collector`（PRR-P2-8）；前端 SWR（PRR-P2-9）；邮件 arq 队列（PRR-P2-10）。

### Fixed

- **验收-3** SQLite 归档 + Alembic 单一 head（`d6e7f8g9h0i1`）；**验收-4** 测试全绿（前端 108 passed / 后端 268 passed 41 skipped）；Phase 1 BFF 验证 1-6 全过（修复 9 个契约 bug）。

### Docs

- **P2 真伪核查归档**：SI5 TOTP_ENCRYPTION_KEY 断言 / 限流 jti Redis 降级 / ADR-014 事件总线 / Phase 2-5 Drizzle 已过时 等经代码核查确认已实现或过时，从待办移除。

---

## [0.9.6]

### Changed

- 版本号由 0.9.5 升至 0.9.6（前端 `package.json`、后端 `__version__`、前端 `CHANGELOG` 锚点同步）。

---

## [0.9.5]

### Changed

- 版本号统一升至 0.9.5（前端 `package.json`、后端 `__version__`、前端 `CHANGELOG` 锚点同步）；后端 `__version__` 由 1.0.0 校正回归至 0.9.x 语义版本线。

---

## [0.9.1]

> 含 0.9.1 发布 + 0.9.2–0.9.4 连续迭代（2026-07-29 ~ 2026-08-05）。
> 注：0.9.2–0.9.4 为 0.9.1 发布后、0.9.5 版本号统一前的连续迭代期，未打独立 patch 版本，其内容（文档整合、前后端分离迁移历史、Repository 收官、前端重建、前端架构准则、数据迁移、方案B、设计优化、i18n、文档合并、超长页面拆分）已并入本节。

### Added

- **ADR 架构决策基线（ADR-001~013/015/016，部分已随前后端分离演进）**：Next.js 全栈（已演进为前后端分离，后端 FastAPI+PG 承载业务）/ 模块化分层 / RBAC / SQLite 写瓶颈应对（已迁 PG）/ 事件驱动通知 / Markdown 安全净化 / API 无版本前缀 / 细粒度 RBAC / 单节点部署（已具备多实例骨架）/ 事件监听器显式初始化 / Repository 抽象层 / TOTP 2FA + GitHub OAuth / 活动系统。完整 ADR 记录见 `RootDoc-ADR.md`。
- **0.9.1 功能**：社区系统（版块/主题/回复/楼中楼/Markdown/点赞收藏/@提及/搜索）、技术文章（系列/目录）、内网考试（判分/排名/组卷）、学习资源站、协会任务发布、Auxilio 规则引擎 Agent、活动系统（CRUD/报名/签到/归档/月历）、用户公开主页/技术档案、成员名录、入社申请、全站公告、站内通知。
- **安全加固**：TOTP 2FA（管理员强制）+ GitHub OAuth + jti 防重放；密码策略升级；细粒度 RBAC；全站安全响应头（CSP/HSTS 等）；速率限制精细化；敏感数据脱敏；SQL 注入审计 100% prepared statement；统一输入验证（zod）；Markdown 白名单净化；对象级权限（IDOR）；登录历史+异常告警；会话管理增强；高危操作二次确认；依赖漏洞扫描；Cookie `__Host-` 前缀；社区图片 session 访问控制；安全审计日志。
- **架构与工程质量**：模块化架构 + 事件总线；Litestream 流式备份；pino 结构化日志；健康检查 `/api/health`；请求 ID 注入；错误率监控 / Sentry 可选；CI build+审计；单元测试 308 + E2E 25（Playwright）；用户等级/积分；Git hooks+CI；441+ 单测全绿。
- **基础设施**：Docker + Caddy 部署；Litestream 本地/S3 备份；Cloudflare Tunnel。

### Changed

- 统一错误处理（`AppError` + `ERROR_STATUS_MAP`）；提取 EASE 动画常量；19 页面统一 CollapsingHero；安全头迁移 `proxy.ts`；server-only 边界澄清；`AuditContext` 下沉 `shared/types`；社区三模块合并 community；App/API 路由重组；TopicDetail 拆分；生产启动强制校验；模块级权限守卫 `requireModuleAdmin`；活动日历双视图。
- **前后端分离迁移（历史痕迹，2026-08-01）**：前端由全栈单体降级为 BFF 薄转发，后端 FastAPI+PG 承载全部业务；Drizzle/SQLite 36 表 → SQLAlchemy/PG 42+ 表；Phase 0~6 全量迁移（含 scrypt→bcrypt 懒升级、中文 FTS GIN+tsvector、事件总线跨实例 ADR-014）。原迁移叙事已合并，本文件不再复述细节。
- **数据迁移 SQLite→PG（2026-08-05）**：业务数据全量入库、外键完整、类型转换正确、UUID→Integer 主键重映射；7 项验证全过；迁移脚本 `migrate-sqlite-to-pg.mjs` 已实现（后随 BFF 收口删除）。
- **方案B 统一 camelCase 传输契约（2026-08-05）**：后端 `TZModel` camelCase；前端 `backend-client` 翻译层；修复 9 个联调缺陷；全栈 camelCase 统一完成。
- **前端重建/架构/i18n/设计优化/文档合并/超长页面拆分（2026-08-03~08-05）**：前端重建适配 community v2；`RootDoc-FEArch` 定稿；i18n 11 主页面 + admin；前端设计评审 13 项修复；超长页面拆分（profile 1303→290 等 8 页面 <500 行，29 passed）；文档合并去重（`FrontDoc-General`→`RootDoc-FEArch` 等）。

### Fixed

- **ADR-016** 活动日期格式比较缺陷；**ADR-017** 跨模块日期比较；**ADR-015** 2FA 端点限流/Origin 校验、GitHub OAuth 绕过、密码重置事务、默认弱口令等；**ADR-013** 事件监听器隐式初始化致通知静默。
- **安全审计修复（OWASP Top 10）**：🔴严重 0 / 🟠高 4 ✅ / 🟡中 7 ✅ / 🟢低 5 ✅；`ROLE_MODULE_MAP` + `requireModuleAdmin`、HKDF-SHA256 TOTP 密钥、CSP nonce、`AUTH_COOKIE_NAME __Host-`、pino 日志替换 `console.error` 等。

### Docs

- ADR 记录 19 条（含 ADR-014 跨实例事件总线于 2026-08-06 落地）；风险登记表 R1-R20。
- 文档体系：`FrontDoc-Ops` / `FrontDoc-01-Arch` / `FrontDoc-02-Sec` / `Onboarding` 整合；`RootDoc-*` 根级文档建立。

---

## 编号体系速查表

| 前缀                            | 含义                                   | 主要出处                   |
| ----------------------------- | ------------------------------------ | ---------------------- |
| `ADR-xxx`                     | 架构决策记录（Architecture Decision Record） | [0.9.1]                |
| `ER-xx`                       | 1.0.0 收口工程项（安全/治理/质量/测试）             | [0.9.9] / [Unreleased] |
| `PRR-*`                       | 1.0.0 发布就绪度审查项                       | [0.9.7] / [0.9.9]      |
| `Phase 0~6`                   | 数据迁移执行阶段                             | [0.9.1]                |
| `M1/M2…` `P1/P2/P3`           | 里程碑 / 文档合并优先级                        | 项目待办事项-优先级重排.md       |
| `R1~R20`                      | 风险登记表（Risk）                          | [0.9.1]                |
| `L1~L10`                      | 法律/合规类待办条目                           | 项目待办事项-优先级重排.md       |
| `F1~F3`                       | 前端设计评审项                              | [0.9.1]                |
| `D1~D4`                       | 前后端分离迁移决策                            | [0.9.1]                |
| `B1~B3`                       | 1.0.0 发布阻塞项（Blocker）                 | [0.9.7]                |
| `G1~G4`                       | 1.0.0 GA 缺口                          | [0.9.7]                |
| `CodeGov-*` `DocGov-*` `AL-*` | 代码/文档治理项、BFF 安全边界                    | [0.9.9]                |
| `C-1~C-21`                    | 0.9.9 时代清理/重构交付项（C-1~C-14、C-20、C-21 已执行归档，C-15~C-19 架构重构待办） | [0.9.9] / 项目待办事项-优先级重排.md |
| `F-1~F-9`                     | 文档冲突审查项（F-1~F-8 已随清理修正，F-9 待办）      | [0.9.9] / 项目待办事项-优先级重排.md |
| `N-01~N-14`                   | 规范化建议项（已落地部分见 C-*，残余 N-01/N-12/N-13/F-9 待办） | 项目待办事项-优先级重排.md |

> 本文件（根 CHANGELOG.md）为全项目变更记录单一事实源；活文档（L0/L1/L2）引用历史请以本文件为准。待办跟踪唯一权威见 `docs/项目待办事项-优先级重排.md`。
