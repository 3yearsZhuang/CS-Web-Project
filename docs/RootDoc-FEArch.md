# 前端项目 · 内容设计规范与目录设计艺术（RootDoc-FEArch · CS-Web-Frontend 方法论）

> **当前进度 / 真实状态（2026-08-09）**：本文档已从「框架无关的通用前端准则」收敛为本项目（`CS-Web-Frontend`）专属方法论，所有骨架、示例、阈值均以本仓库真实代码为锚。真实态：Next.js 16 App Router BFF 薄转发层，运行时不再读写数据库；业务/认证/RBAC/迁移全在后端（`CS-Web-Backend`，FastAPI + PostgreSQL）。阅读本文请以本仓库 `src/` 为参照，勿套用其他项目结构。
>
> 更新人：3yearsZ
> 最后更新：2026-08-09（收敛为项目专属方法论，补齐「方法论 ↔ 规范」引用桥）
> 覆盖：前端目录 / 组件分层 / 复用阈值 / 样式法则 / 接入仪式 / 协作约束

**权威位置**：本文档是「本项目前端目录 / 架构方法论」的唯一权威。架构事实见 [`FrontDoc-01-Arch.md`](../CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md)，编码规范见 [`FrontDoc-03-Conv.md`](../CS-Web-Frontend/tools/docs/FrontDoc-03-Conv.md)，视觉与交互规范见 [`FrontDoc-UID.md`](../CS-Web-Frontend/tools/docs/FrontDoc-UID.md)，通用工程规范见 [`RootDoc-EngConv.md`](RootDoc-EngConv.md)。

---

## 零、方法论 ↔ 规范 引用桥

本文档回答「怎么组织」；规范文档回答「长什么样 / 事实是什么」。三者分工、互不重复：

| 本文档（方法论，怎么组织） | 落点规范（本项目事实 / 视觉） |
|---|---|
| §2.1 分层即内容 | `UID §5.0` 全局组件体系与复用契约、`Conv §7` 组件复用契约、`components/README.md` |
| §2.3 配置即内容数据 | `Arch §1.2.4` 工作台 widget-registry、`Conv §8` widget 注册表、`UID §4.8` capsule-tabs 配置表 |
| §2.5 样式内容法则 | `Conv §5` 样式令牌、`UID §1` 颜色系统 / `§3.5` Token 速查表、`src/app/globals.css` |
| §3.2 项目骨架 | `Arch §1.1` 项目结构、`src/` 目录树 |
| §3.4 模块化（按业务域） | `Arch §1.2` 模块层级与依赖矩阵、`modules/README.md` |
| §6 协作约束 | `RootDoc-EngConv.md §八` 通用禁令 + `Conv §1` 分层铁律（本文档仅保留前端特有） |

> 新增页面 / 组件的完整接入流程见 `docs/Onboarding.md` 附录 A。

---

## 一、设计哲学（三句话）

1. **内容按「原子 → 有机体」生长**：UI 从最小不可分单元组合出来，而非从页面反向切碎。
2. **目录按「职责 → 模块」收口**：每个目录有且只有一个明确的职责边界。
3. **配置按「单块 → 聚合」暴露，样式按「变量 → 优先级」克制**：配置即数据，样式不靠 `!important` 强权。

项目的可维护性不来自功能多少，而来自**每一次新增都落在既定格子里**。

视觉表达层（本项目的「设计艺术」）由 `UID §0` 定义：编辑式技术极简——杂志版面 × 工业终端，直角克制、数字优先、低饱和动效。本文档只负责其背后的**工程秩序**。

---

## 二、内容设计规范（Content Design）

### 2.1 分层即内容（Atomic Design 落地）

本项目组件按**五层 + 业务域**组织，**绝不按文件后缀**（`.tsx` / `.ts` / `.css`）分组：

| 层级 | 目录 | 定义 | 本项目代表 |
|------|------|------|------|
| **primitives**（atoms） | `components/primitives/` | 无业务语义的通用原子件 | `button` `input` `spinner` `loading` `section-nav` `inline-tabs` `filter-bar` `confirm-dialog` |
| **layout**（organisms） | `components/layout/` | 页面级骨架与导航 | `navbar` `footer` `collapsing-hero` `floating-capsule-sidebar` |
| **effects** | `components/effects/` | 入场 / 过渡动效原语 | `motion-primitives` `mobius-ring` `page-transition` `scroll-indicator` |
| **feedback** | `components/feedback/` | 加载 / 空 / 错 / 成功四态 | `toast` `empty-state` `fallback` `announcement-banner` |
| **根级 root-level** | `components/`（顶层） | 跨页面全局件 | `avatar` `user-menu` `notification-bell` `theme-provider` `tech-tag-selector` |
| **features**（业务域） | `modules/*/` | 特定功能集合（`types/` + `ui/`） | `auth` `community` `events` `tools` `workbench` … |

**黄金法则**：写新 UI 前先查现有原子件（见 `components/README.md` 清单）；不存在且满足「重复 ≥ 2 次 / 职责单一 / 可独立存在 / 可配置化」才新建。

### 2.2 内容边界契约

- **展示组件** 与 **容器/数据逻辑** 分离：UI 组件只管渲染，数据获取 / 状态管理抽到 `shared/hooks/`、模块内 `ui/hooks/` 或 BFF 层（`shared/backend-client.ts`）。
- **同名组件绝不散落多目录**（反例：同一组件在 `components/`、`modules/x/ui/`、`app/*/` 各一份）。
- 业务数据一律经 BFF API 路由（`src/app/api/**/route.ts` → `backend-client.ts` 转发后端），组件**禁止直接** `fetch` 后端地址。

### 2.3 配置即内容数据

- 运行时消费的「组件清单 / 功能开关」派生为聚合对象，**配置即数据驱动渲染**。
- 本项目实例：
  - `shared/config/`：`avatar-presets` / `admin-avatars` / `header-images` / `auth-constants`
  - `modules/workbench/widget-registry.ts`：widget 声明数组（id / slot / titleKey / component），`workbench.tsx` 按 slot 分组渲染
  - `tools/docs/capsule-tabs.md`：各页面悬浮胶囊 Tab 配置表（`UID §4.8`）
- 配置入口用 ASCII 表 / 注释说明每个导出项。

### 2.4 复用阈值（量化红线）

| 信号 | 阈值 | 动作 |
|------|------|------|
| 重复 UI 结构 | ≥ 2 次 | 抽取为 primitives 原子件（`GENERAL 2.4`，见 `components/README.md`） |
| 组件总行数 | > 500 | 必须拆分 |
| 样式代码 | > 200 行 | 拆出 / 提取 |
| 逻辑代码 | > 150 行 | 提为 hook / util |
| 状态变量 | > 10 个 | 拆子组件 + 状态管理 |
| 导入依赖 | > 10 个 | 提取服务层 |

**拆分四法**：按功能 / 按 UI 层级 / 按关注点 / 提取通用容器。

### 2.5 样式内容法则

- **禁用 `!important`**（仅第三方注入样式例外，且须集中、须审批）。
- 覆盖优先级链（从高到低尝试）：
  1. 原子类 / 工具类（Tailwind 任意值，如 `text-[var(--primary)]`）
  2. 提高选择器特异性
  3. 设计令牌（CSS 变量，`globals.css` 集中定义）
  4. 组件作用域样式
  5. 全局样式（谨慎）
  6. `!important`（末位手段）
- 主题切换一律走 CSS 变量（`:root` 浅色 / `.dark` 深色），不用 `!important` 强刷。
- 颜色 / 圆角 / 阴影 / z-index / 动效时长全部走 `globals.css` token，禁止散落硬编码 hex（见 `UID §1 / §3.5`）。

### 2.6 接入仪式（防「配置了不显示 / 注册了不生效」）

新增可插拔模块（widget、侧边栏组件、路由、Provider），**声明 → 配置 → 注册 三处缺一不可**：

1. 类型 / 接口中声明（如 `workbench` 的 widget 类型）
2. 配置文件中启用并排位（如 `widget-registry.ts` 的 `WIDGETS`）
3. 在注册表 / 渲染器中登记（多入口相互独立，勿只登一处）

> 落地实例：`Arch §1.2.4` 工作台「新增 widget 三步」；`UID §4.8` 新增页面同步 capsule-tabs 配置表。

---

## 三、目录设计艺术（Directory Art）

### 3.1 按职责分层，拒绝技术分层

```text
❌ app/ components/  utils/     ← 按类型机械分组
✅ app/ components/  modules/  shared/   ← 按职责分组（采用）
```

### 3.2 项目骨架（CS-Web-Frontend 真实结构）

> 项目**真实目录树**的权威位置为前端架构文档 [`FrontDoc-01-Arch.md`](../CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md) §1.1（项目结构）；**模块层级与依赖矩阵**见其 §1.2。本方法论不再复述目录树，仅强调其组织原则——**按职责分层，拒绝技术分层**（见 §3.1）。

> 与「通用前端骨架」的差异即本项目取舍（见 §四）：无 `stores/`（状态走 hooks + SWR + localStorage）、无独立 `styles/`（收敛于 `app/globals.css`）、无 `services/`（统一走 `shared/backend-client.ts` + `app/api/`）、无 `assets/`（图片以 `shared/config/*-presets.ts` 常量引用）。

### 3.3 复杂组件 = 子目录即模块

```text
workbench/widgets/pomodoro/
├── pomodoro-player.tsx   # 组合件：番茄钟 + 播放器二合一（< 500 行）
├── use-pomodoro.ts       # 状态机（focus/shortBreak/longBreak）
├── music-panel.tsx       # 上传音乐（IndexedDB）
├── settings-panel.tsx    # 配置面板
└── constants.ts          # SVG stroke 色板（集中收口）
```

每个复杂组件自带 `hooks/` / `types.ts` / `index.ts` 桶导出 →「目录即模块」，深层引用用路径别名 `@/` 消除。

### 3.4 模块化（按业务域）· 主线

> 本项目模块化的**事实与依赖矩阵**权威为 [`FrontDoc-01-Arch.md`](../CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md) §1.2（模块层级与依赖矩阵）；`server/` 遗留直连层已于 2026-08-06 B1 收口删除，服务端逻辑由后端承载（见 Arch §1.1）。本方法论仅沉淀其三条组织规则：

**三条规则**
1. 只在 ≥ 2 个业务域都用时，才提进 `components/`（根级或 primitives）
2. 域内有复用，就在域内建子目录，不往外推
3. 每域自带 `types/`，自包含不依赖外域

### 3.5 扁平优先，勿过度嵌套

嵌套 ≤ 3 层；深路径用路径别名消除。

### 3.6 命名即文档

| 类型 | 格式 | 示例 |
|------|------|------|
| UI 组件 | `PascalCase.tsx` | `Button` `SearchBar` |
| Hook | `useXxx.ts` | `useCollapsingHero` `usePomodoro` |
| 工具函数 | `[功能]-utils.ts` | `event-date` `pagination` |
| 类型定义 | `types.ts`（模块内）或 `shared/types/` | `role-types` `user-types` |
| 路由 | `[name]` / `[param]` / `[...catch-all]` | `index` `[slug]` `[category]` |

### 3.7 文档伴随代码

- 目录级 `README.md` 列清组件清单与分类原则：`components/README.md`、`modules/README.md`、`modules/workbench/README.md`
- 每个组件 / 页面必须有 JSDoc 头注释（格式见 `Conv §6`）
- 配置入口用表 / 注释说明每个导出

### 3.8 工程化闭环（可维护性的分水岭）

- 状态：hooks + SWR（`swr-provider`）+ localStorage，无全局事件总线依赖
- 测试：Vitest 单元测试 437+、Playwright E2E 25+（`tools/tests/`）
- CI：根仓 `Makefile` / 前端 `ci.yml` 自动跑 type-check + lint + build + test + 依赖审计（`pnpm audit`）
- 锁包管理器：`packageManager` 字段（pnpm）

---

## 四、项目取舍速查

| 维度 | 本项目决策 | 规避反模式 |
|------|-----------|---------|
| 配置 | 单职责小块 + 索引聚合（`shared/config/`、`widget-registry.ts`） | 巨型 config 单点膨胀 |
| 组件 | 五层全局体系 + 目录即模块 + 桶导出 | 同名组件散落多目录 |
| 类型 | 模块内 `types.ts` / `shared/types/` | 全堆进单个文件 |
| 文档 | 目录 README + 配置表 + JSDoc 头注释 | 只写代码不写「为何」 |
| 状态 | hooks + SWR + localStorage（无 `stores/`） | 事件总线满天飞 |
| 数据访问 | 统一 `shared/backend-client.ts` + BFF API（无 `services/`） | 组件直连后端 / 散落 fetch |
| 样式 | `globals.css` token + Tailwind 任意值 | 散落 hex / `!important` |
| 复用 | 重复 ≥ 2 次即抽取（`GENERAL 2.4`） | 复制粘贴结构 |
| 测试 | Vitest + Playwright，拆分即补测 | 无测试体系 |
| 分层 | 严格但务实 | 「为分层而分层」硬塞分类 |

---

## 五、落地清单（新增页面 / 组件开局）

- [ ] 先查 `components/README.md` 与 `modules/README.md` 现有件，满足「重复 ≥ 2 次」才新建
- [ ] 全局件放 `components/{primitives,layout,effects,feedback}` 或根级；业务件放 `modules/<域>/ui/`
- [ ] 类型放模块内 `types.ts`，跨域类型放 `shared/types/`
- [ ] 数据一律走 BFF API（`app/api/**/route.ts`），禁止组件直连后端
- [ ] 颜色 / 圆角 / 阴影 / z-index / 动效全走 `globals.css` token
- [ ] 组件 < 500 行、逻辑 < 150 行（超则拆 hook / 子组件）
- [ ] 补 JSDoc 头注释（`Conv §6`）与目录 README 登记
- [ ] 新增可插拔件完成「声明 → 配置 → 注册」三步（§2.6）
- [ ] `tsc --noEmit` + `eslint` 0 错误，涉及交互补 Vitest / Playwright
- [ ] 视觉规范自查：对照 `UID §12` 新增页面 Checklist

---

**一句话内核**：*内容按「原子 → 有机体」生长，目录按「职责 → 模块」收口，配置按「单块 → 聚合」暴露，样式按「变量 → 优先级」克制。*

---

## 六、协作约束（强约束 · 前端特有）

> 通用禁令（最小范围、保持一致、禁止炫技等）见 [`RootDoc-EngConv.md §八`](RootDoc-EngConv.md)。本节仅补充**前端特有的硬性约束**，优先级高于上方「倡导式」准则。任何代码改动、AI 协作均须遵守。
> 若某条无法满足，必须显式说明原因并给出替代方案，不得用"这样更好"这类模糊理由带过。

### 6.1 目录与文件

1. 禁止擅自新建目录、拆分文件、重命名已有模块；新增必须基于现有目录结构放置（见 §3.2 骨架）。
2. 修改前先读取相关现有文件，风格、命名、组织方式必须与现有代码保持一致。
3. 同一功能的代码必须集中在约定位置，禁止为单一功能分散创建多个新文件。

### 6.2 组件

1. 禁止重复创建通用 UI 组件（Button、Input、Modal、Table、Form 等）；必须从 `components/primitives/` 或项目组件库中选取（`UID §5.0` 复用契约）。
2. 业务组件必须遵循项目现有封装范式：props 定义、事件命名、状态管理、样式引用方式统一。
3. 禁止把简单组件过度拆分为多个无复用价值的小文件。
4. 组件新增必须说明复用场景；仅在确定会被多处使用时才允许抽离为独立组件（与 §2.4「重复 ≥ 2 次」阈值一致）。

### 6.3 代码风格

1. 命名规范：组件文件 `PascalCase`；工具函数 / hook / 常量 `camelCase`；类型 / 接口 `PascalCase`；CSS 类名遵循项目现有约定（Tailwind + `globals.css` 工具类）。（与 §3.6 一致）
2. 禁止使用魔法数字、硬编码颜色、硬编码断点，必须使用项目已定义的设计令牌或常量。（与 §2.5 设计令牌一致）
3. 禁止在组件中写死样式块；样式必须按项目约定集中管理或使用已有工具类。（与 §2.5 一致）
4. 代码必须简洁直接，禁止为炫技引入不必要的抽象或设计模式。

### 6.4 依赖与技术

1. 禁止引入未在 `package.json` 中声明的依赖，或未经评审的新库。
2. 禁止同时使用多种实现同类功能的库。
3. 禁止使用项目已明确弃用的 API、语法或写法（如 `server/` 直连层、SQLite）。
4. 必须使用项目已选定的框架能力解决问题（Next.js App Router + Turbopack），不自行封装与框架等价的底层能力。

### 6.5 修改范围

1. 禁止删除或修改与当前需求无关的现有代码、注释、测试（前端补充：含 `app/` 路由页拆分纪律，详见上方 §3 分层）。
2. 每处修改必须说明理由，不能回答"这样更好"之类的模糊理由（前端补充：组件 / 样式改动须同步说明对现有设计系统的影响）。

### 6.6 输出要求

1. 先简要列出计划修改的文件和改动点，经确认后再输出具体代码。
2. 输出代码时只输出改动部分或完整文件，禁止输出大段解释性废话。
3. 若某项约束无法满足，必须明确说明原因，并给出替代方案。

---

## 变更记录

| 日期 | 变更 |
|------|------|
| 2026-08-09 | 收敛为项目专属方法论：① 移除「框架无关 / 适用于任意前端项目」定位，全部骨架 / 示例以 `CS-Web-Frontend` 真实结构为锚；② 新增 §零「方法论 ↔ 规范引用桥」（FEArch ↔ UID / Arch / EngConv 分工映射）；③ §2.1 分层改为本项目五层全局体系 + 业务域；④ §3.2 骨架替换为真实 `src/` 树并说明取舍；⑤ §3.4 模块化改为 `types/` + `ui/` 两层（`server/` 已删）；⑥ §四取舍速查、§五落地清单全部改列项目实际决策；⑦ 保留被引用章节锚点（§2.3 / §2.4 / §2.6 / §3.3 / §3.4 / §6.3.2 等） |
| 2026-08-09（治理） | 降级为桥接索引：§3.2 项目骨架、§3.4 模块化移除与 `FrontDoc-01-Arch.md` 重复的目录树 / 模块树，改为指向其 §1.1 / §1.2 的桥接指针（消除架构叙述双份漂移，落实 README 治理规范的所有权矩阵「RootDoc-FEArch 仅桥接索引」） |
