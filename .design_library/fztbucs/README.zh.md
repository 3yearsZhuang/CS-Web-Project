# fztbucs 设计系统

**fztbucs** 设计系统的重建 —— 一个围绕"编辑式技术极简"（Editorial Tech Minimalism）构建的 Web 产品。
本系统专为以内容为先的 Web 界面而生，既需要编辑式排版的温润质感，又需要技术化工具的精确性。

> *"编辑式技术极简 (Editorial Tech Minimalism) — 浅色模式强调色：深蓝 #1e40af；深色模式强调色：琥珀金 #d4a574"* — 出自 `colors_and_type.css` 的源注释

## 来源

- **结构化规范：** `.design_library/fztbucs/css.json`、`colors_and_type.css` 以及 `components/*.json`
- **组件：** 6 个已文档化组件，涵盖导航、反馈、数据录入与内容展示面
- **品牌所有者：** fztbucs

## 本设计系统涵盖内容

- **基础（Foundations）** — 颜色（浅色/深色）、排版（Fraunces / JetBrains Mono / Noto Sans SC）、间距、圆角、阴影与动效
- **组件（Components）** — 6 个已文档化组件：Button（按钮）、Input（输入框）、Card（卡片）、Navbar（导航栏）、Toast（轻提示）、Avatar（头像）
- **示例幻灯片与 UI 套件** — `preview/` 中的参考预览，以及 `ui_kits/` 中完整可点击的 UI 套件（如有）

---

## 内容基础

### 语气与语调

fztbucs 采用以中文为主体、编辑式技术化的语体。文案精准、从容，并具有视觉自觉：标题与标签读起来像是出自某位出版物设计师之手，而非通用 SaaS 产品。语气专业、中性，绝不啰嗦，且产品 UI 中完全不使用 emoji。英文仅出现在功能性标签（类名、token 别名、组件解剖结构）以及简短的大写等宽标签中，如章节标记 `[01]`、`[02]`。当界面需要强调时，它依赖排版本身 —— 一个衬线斜体关键词或一个小号大写等宽标签 —— 而非感叹号或亲昵的口语化表达。

### 具体文案示例（取自源文件）

- 设计理念：*"编辑式技术极简 (Editorial Tech Minimalism)"*
- 浅色模式说明：*"浅色模式强调色：深蓝 #1e40af"*
- 深色模式说明：*"深色模式强调色：琥珀金 #d4a574"*
- 工具类描述：*"运行时字体组合栈"*
- 按钮系统标签：*"统一按钮系统 — 编辑式技术极简"*
- 章节标记风格：*`[01] [02] 风格`* 以及大写等宽标签

### 生成文案时

- 以中文起首；英文仅保留 token 名、类名与简短的大写标签。
- 偏好精确、近乎目录式的描述，而非营销式的华丽辞藻。
- 使用大写等宽标签（`[01]`、`[02]`）作为章节或段落标记。
- 避免 emoji、感叹号密集的句式，以及通用的 CTA（行动号召）话术。
- 仅在无衬线正文内对单字强调时，使用衬线斜体。

---

## 视觉基础

### 颜色

调色板建立在一组刻意的对比之上：温暖的浅粉红页面，与冷静的深海军蓝强调色。浅色模式下，页面背景为 `#fdf5f7`，前景文字为近黑紫的 `#1e1233`，主要操作色为深海军蓝 `#1e40af`。卡片与浮层干净地置于白色 `#ffffff` 之上；次级表面使用 `#f0e8ee`，弱化背景使用 `#f8eef2`。强调色槽 `#e8ecf5` 提供冷调蓝灰，用于高亮而不与主要色相争。

语义色极少且功能明确：危险操作为锐利的红 `#e7000b`；成功、警告、信息均取自图表色阶，而非引入额外色相。浅色模式的图表色阶自 `#1e40af` 延展至 `#ec4899`、`#14b8a6`、`#6366f1` 与 `#8b5cf6`。Logo 色则补充了一套柔和渐变语汇：`#4070e0`、`#80a0f0`、`#a0d0f0`、`#f0b0c0` 与 `#f0c0d0`。

深色模式下，调色板剧烈反转：背景变为 `#000000`，卡片变为 `#0a0a0a`，前景文字转为温暖的 `#f5f5f4`。主要强调色由海军蓝切换为琥珀金 `#d4a574`，描边环同样跟随这一金色。图表色针对深色表面重新平衡，转为 `#d4a574`、`#5bc9c5`、`#e88565`、`#c77dba` 与 `#8b9dc3`。整体氛围在浅色模式下如画廊般静谧，在深色模式下则如夜间编辑部。

### 排版

排版系统明确采用三重复合结构。**Fraunces**（中文回退为 `Noto Serif SC`）负责展示与编辑式标题 —— 使用 `350` 的偏细字重，开启光学尺寸调节，行高收紧至约 `1.05`。**JetBrains Mono** 负责所有元信息文本：大写章节标记、标签、按钮、错误信息与标签，字号为 `11px` 或 `12px`，字间距介于 `0.08em` 与 `0.15em` 之间。**Noto Sans SC** 承载正文与 UI 标签，通过 Google Fonts 加载，字重范围 `300..700`。

由于 CSS 在运行时仅引入 Noto Sans SC 与 Noto Serif SC，Fraunces 与 JetBrains Mono 预期由使用方项目提供（通常通过 Next.js 的字体优化）。已指定回退链：Fraunces 的回退链为 `Noto Serif SC`、`Songti SC`，再到通用衬线；JetBrains Mono 的回退链为 `SFMono-Regular`、`Menlo`、`Monaco`、`Consolas`，再到通用等宽。

### 间距

间距以 `4px` 为基准锚定。圆角 token 为 `0.25rem`（`4px`），由此衍生出从 `radius-sm`（`calc(var(--radius) - 4px)`）到 `radius-4xl`（`calc(var(--radius) + 16px)`）的刻度。按钮使用宽裕的内边距（中号为 `0.75rem 1.5rem`，小号为 `0.375rem 0.75rem`），输入框则采用紧凑的内部内边距并撑满整宽。Z 轴层级同样被 token 化，从 `10` 直至覆盖层的 `9998`。

### 圆角

- **`0px`** — 按钮、卡片、标签、徽章与 Toast 容器的默认值；方角边是品牌标志。
- **`4px`** — 仅用于输入框（`INPUT_CLASS` 例外）；这是控件组中唯一出现圆角之处。
- **`28px`** — 保留用于胶囊形元素。
- **`22px`** — 用于胶囊内部的条目。

近乎彻底的无圆角是刻意的：它让界面拥有印刷页面或技术文档的质感，而非传统的圆角 Web 应用。

### 阴影 / 层级

仅定义两层阴影，且都极度克制：

1. **浮层（level 1）：** `0 4px 24px rgba(0, 0, 0, 0.04)` — 用于下拉菜单、浮层与小尺寸浮动面板。
2. **模态（level 2）：** `0 8px 40px rgba(0, 0, 0, 0.08)` — 用于对话框与更大尺寸的覆盖层。

层级并不用于区分卡片与页面；卡片依赖白色（`#ffffff`）背景衬托于粉红 `#fdf5f7` 页面之上。阴影哲学是"悄声细语" —— 表面保持扁平，直到它们真正需要悬浮。

### 描边、背景与动效

描边细如发丝且低对比：浅色模式为 `rgba(30, 18, 51, 0.08)`，深色模式为 `rgba(255, 255, 255, 0.06)`。输入框描边稍强，透明度为 `0.1`。专用工具类 `.hairline` 以 `1px` 实线 `var(--border)` 分隔编辑式区块。动效使用自定义缓动 `cubic-bezier(0.16, 1, 0.3, 1)`（`--ease-ark`），时长从快速反馈的 `200ms`，到电影级主视觉揭示的 `800ms`，再到史诗级转场的 `1400ms`。

---

## 组件模式

| 组件 | 预览 | 契约 | CSS 来源 | 关键事实 | 关键洞察 |
|---|---|---|---|---|---|
| Button | `preview/component-button.html` | `components/button.json` | `colors_and_type.css`（`.btn-primary`、`.btn-outline`、`.btn-danger`） | 变体：primary / outline / danger；尺寸 md/sm；状态 default/hover/disabled/loading。方角 `0px` 圆角，`12px` / `11px` 大写等宽，`0.1em` 字间距。 | 按钮是"方盒中的等宽标签" —— 即使是主要操作，也像编辑式图注而非圆角 CTA。 |
| Input | `preview/component-input.html` | `components/input.json` | `preview-only`（仅预览） | 以 `input`、`textarea` 或 `select` 渲染；状态 default/error/disabled。标签为字段上方的元信息等宽图注；错误为 `11px` 等宽危险文本。字段圆角为系统唯一例外，取 `4px`。 | fztbucs 偏好显式的堆叠标签而非浮动标签；表单字段读起来像带标签的标本行。 |
| Card | `preview/component-card.html` | `components/card.json` | `preview-only`（仅预览） | 可选 header/body/footer 解剖结构；状态 default/hover；密度 default/minimal。方角，`1px` `var(--border)` 描边，悬停时描边转为 `var(--primary)`。 | 卡片是扁平的白色编辑式容器；层级保留给浮层，绝不用于卡片。 |
| Navbar | `preview/component-navbar.html` | `components/navbar.json` | `preview-only`（仅预览） | 固定顶部 flex 行，含品牌标识、链接、操作；浅色/深色主题；default/scrolled 状态。链接为 `12px` 等宽大写，字间距 `0.05em`；底部 `1px` 实线 `var(--border)` 描边。 | 导航栏本质上是印刷出版物的页眉 —— 一个 Logo、等宽导航标签，以及一项主要操作。 |
| Toast | `preview/component-toast.html` | `components/toast.json` | `preview-only`（仅预览） | 变体 info/success/error；flex 行，左侧 `3px` 强调色描边。背景 `var(--card)`，文字 `13px` 无衬线正文。 | Toast 使用着色左缘而非背景着色，使表面始终保持一致白色。 |
| Avatar | `preview/component-avatar.html` | `components/avatar.json` | `preview-only`（仅预览） | 尺寸 sm/md/lg（`24px` / `40px` / `64px`）；default/fallback 状态。圆形溢出，配 `muted` 背景与 `muted-foreground` 首字母。 | 头像是系统中唯一圆形元素；其余所有组件均为方角。 |

---

## 索引

- `README.md` — 本文件
- `colors_and_type.css` — 颜色、排版、圆角、阴影、间距的 CSS 变量
- `components.css` — 从预览页提取的聚合组件 CSS（本次重建中不存在；Button 类请依赖 `colors_and_type.css`）
- `css.json` — 结构化 token 元数据
- `components/` — 组件契约：`button.json`、`input.json`、`card.json`、`navbar.json`、`toast.json`、`avatar.json`
- `preview/` — 设计系统标签页使用的小型 HTML 卡片
- `ui_kits/{type}/` — 完整可点击的重现套件
- `SKILL.md` — 智能体 skill 清单

---

## 注意事项 / 已知替代

1. **Fraunces 与 JetBrains Mono** 通过 CSS 变量（`--font-fraunces`、`--font-jetbrains`）引用，但未被 `colors_and_type.css` 加载。当这些变量未定义时，我们以 **Noto Serif SC** 替代 Fraunces，以 **SFMono-Regular / Menlo / Monaco** 替代 JetBrains Mono。若要达到像素级准确的品牌效果，使用方项目必须注入真实的 Fraunces 与 JetBrains Mono 字体。
2. **除 Button 之外的组件** 仅依据其 JSON 契约文档化；在结构化规范提取中并无聚合的 `components.css` 或预览 HTML 证据。这些行的 CSS 来源标注为 `preview-only`（仅预览），意味着实现细节应从组件契约与全局 token 推导。
3. **本系统是从既有前端代码重建**，而非从零开始的 Figma 库。部分尺寸（例如标注为"编码于前端工具文件中"的输入框精确内边距值）是从代码模式推断而来，而非在设计文件中直接观测所得。
4. **具体的产品 UI 文案**（按钮标签、表单占位符、空状态文字）并未出现在所提取的结构化规范中。上方案例文案取自 CSS 注释与组件元数据；真实的产品文案应遵循内容基础中描述的"以中文为先、编辑式技术化"的语体。
