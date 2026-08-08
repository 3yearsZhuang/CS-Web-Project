# 通用工程规范（跨项目提炼）（RootDoc-EngConv）

> 更新人：3yearsZ
> 最后更新：2026-08-05（统一 RootDoc 命名）
> 从后端 `CS-Web-Backend/tools/docs/BackDoc-Conv.md` 与前端 `CS-Web-Frontend/tools/docs/FrontDoc-UID.md` 提炼的**框架无关**通用原则。
> 本项目（FztbuCS-Project）内的 Python/FastAPI 与 TypeScript/Next.js 代码均适用。
> 端侧强相关的完整规范仍以各子仓库为权威（见文末深链接），此处只收通用原则，避免重复漂移。
>
> **约定类文档边界**：通用（两端共用）规范以本文件为权威；**后端专项**约定见 `CS-Web-Backend/tools/docs/BackDoc-Conv.md`；**前端专项**约定见 `CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md`（架构与约定）与 `FrontDoc-UID.md`（UI 规范）；`docs/Onboarding.md` 附录 A 为面向新人的**聚合摘要（非权威）**，细则一律指回上述权威文件。三份约定文件与聚合摘要出现冲突时，以各自的权威文件为准。

---

## 一、命名规范

| 对象 | 规范 | 示例 |
|---|---|---|
| 类 | `PascalCase` | `User`, `Button` |
| 函数/方法 | `snake_case`（py）/ `camelCase`（ts）；私有以 `_` 开头（py） | `_hash_password`, `getUser` |
| 常量 | `UPPER_SNAKE_CASE` | `DEFAULT_PAGE_SIZE` |
| 组件（前端） | `PascalCase`，文件与默认导出同名 | `Button.tsx` → `Button` |
| 配置文件/桶导出 | `index.ts` / `index.py` | 聚合导出 |

---

## 二、代码质量红线

### 单一职责与规模

- 单一职责：一个模块/函数只做一件事；禁止把多个业务域塞进同一个文件。
- 文件大小：单文件超 **~300 行（py）/ ~500 行（组件）** 必须评估拆分。
- 函数长度：明显超过一屏（约 50–80 行逻辑）或含多个处理阶段时，按语义拆辅助函数。

### DRY 与抽象（三次法则）

- 同一段逻辑在 **3 处**出现，必须抽公共函数；1–2 处直接写，**不要预先抽象**。
- 出现真实重复才复用；不要因为两段代码暂时相似就过早抽象。

### 圈复杂度

- 单函数圈复杂度建议 ≤ **10**；超过用早返回、查表、策略对象拆分。
- 避免深度嵌套 `if/elif` 链，优先改写为「条件 → 动作」映射。

### 魔法值与单一事实源

- **禁止散落的魔法值**：重复出现的字面量（版本号、地址、状态码字符串…）必须收敛到单一来源。
- **禁止硬编码**：不写死 host:port、密钥、颜色、断点；一律走设计令牌/常量/配置。

---

## 三、错误处理约定

- 业务失败用统一的异常基类表达，由全局处理器映射状态码与响应体；禁止在路由里吞异常返回自定义格式。
- 禁止空 catch / 静默吞错：必须记录或向上抛；错误信息保留上下文但**不得泄露敏感信息**（密钥、令牌、密码）。
- 外部输入（HTTP/文件/外部 API）必须校验；内部代码信任类型，不重复校验。

---

## 四、安全约定

- **禁止硬编码**密钥、令牌、密码、生产凭证；统一从配置或环境变量读取。
- 使用成熟库做密码哈希/加密，禁止自实现加密。
- SQL 用参数化查询，禁止字符串拼接。
- 日志禁止记录密码、token、个人敏感信息。

---

## 五、配置约定

- 所有配置项收敛到单一 `Settings`/`config` 源；**新增配置必须同步模板**（`.env.example` / `config/index.ts`），否则他人无法知道配置项。
- 本地覆盖用不跟踪的 local 文件（`.env.local`）。
- 每个功能一块独立配置文件，统一 `index` 聚合导出（"单块 → 聚合"）。

---

## 六、测试约定

- 测试覆盖至少覆盖正向、反向、边界三类路径。
- **测试数据必须模拟真实写入路径**：UI/API 写什么格式，测试就构造什么格式；禁止用"看起来合理"的格式掩盖分支。
- 必须覆盖边界用例（空字符串、null、临界值），不只测 happy path。

---

## 七、Git 与提交

- **提交格式**：`<type>(<scope>): <subject>`，type：`feat / fix / refactor / chore / docs / test`。
- **不主动 commit / push**，除非用户明确要求。
- 禁止提交：`*.db`、`logs/`、密钥、本地环境覆盖文件。
- **侵入性操作**（删文件、改公共接口、改数据库结构）**先说明范围再做**。

---

## 八、修改范围（协作约束）

1. 只改动完成任务所必需的最小范围，禁止顺手重构无关代码。
2. 修改前先读取相关现有文件，风格、命名、组织方式必须与现有代码保持一致。
3. 若现有实现已能满足需求，优先复用而非重写；禁止为炫技引入不必要的抽象。
4. 禁止引入未声明的新依赖 / 未经评审的新库；禁止同时使用多种实现同类功能的库。

---

## 九、中文排版规则（前端专属补充）

> 本条为**前端专属**排版约定，通用文档（本文件）仅作引用性收录。完整规范以前端权威文档 [`FrontDoc-UID.md`](CS-Web-Frontend/tools/docs/FrontDoc-UID.md) 为准。

- 汉字之间不留空格。
- 中英文之间留空格。
- 中文与数字之间留空格。

---

## 十、前端工程约定（React Compiler / 语义色板 / widget registry / i18n）

> 本条为**前端专属**工程约定，完整规范以 `CS-Web-Frontend/tools/docs/`（`FrontDoc-UID.md` / `FrontDoc-01-Arch.md`）为准；此处收通用原则，避免重复漂移。
> 适用代码：`CS-Web-Frontend/src/**`（Next.js 16 + React 19 + Tailwind v4）。

### 10.1 React Compiler 红线

前端按 React Compiler 语义编写（自动记忆组件与 Hook 返回值），以下为不可违反的红线：

- **Hook 返回值不得混入 ref 对象**：`useMemo` / 自定义 Hook 的返回值若包含 `useRef` 产物，React Compiler 会误将其当作可记忆值缓存，导致引用错乱；需记忆的状态与 ref 必须分开返回。
- **`useCallback` 闭包用到 ref 时，ref 必须列入依赖数组**：`ref.current` 变化不被自动追踪，漏写依赖会读到过期值。

> 现状：当前 `CS-Web-Frontend/next.config.ts` 尚未显式开启 `compiler.reactCompiler`，上述红线作为**防御性约定**先行落实；编译器启用后即为硬性约束。[待填写：确认 React Compiler 是否已在 0.9.8 启用]

### 10.2 颜色：项目令牌 + Tailwind 语义色板，禁止硬编码 hex

- 颜色必须走**项目令牌**（`var(--primary)` / `var(--foreground)` / `var(--muted-foreground)` / `var(--destructive)` / `var(--border)` / `var(--chart-1..n)`）或 **Tailwind 语义色板**（emerald / amber / red / blue / green 等），**禁止散落硬编码十六进制**（如 `#1a2b3c`）。
- 例外：SVG `stroke` / `fill` 无法用类名时，集中收口到常量文件（如 `CS-Web-Frontend/src/modules/workbench/widgets/pomodoro/constants.ts`）并注释色板来源，不得就地写 hex。
- 依据：工作台模块约定（`CS-Web-Frontend/src/modules/workbench/README.md` §6.3.2）。

### 10.3 工作台 widget：必须在 registry 注册

- 新增工作台（workbench）widget 必须三步：① 在 `CS-Web-Frontend/src/modules/workbench/widget-registry.ts` 的 `WIDGETS` 数组声明（`id` / `slot` / `titleKey`）；② 组装组件（建议放 `src/modules/workbench/widgets/`）；③ 工作台按 `slot`（`full` / `main` / `side`）自动渲染。
- `widget-registry` 是渲染的**唯一事实源**：未注册的组件不出现在工作台；布局显隐由用户偏好 `wb_widget_prefs`（localStorage）驱动，无需改骨架。
- 新增 widget 通常还需配套 i18n 词条（见 10.4）与（如涉及）后端 `/api/workbench/**` 路由（经前端 BFF 薄转发）。

### 10.4 i18n：workbench namespace 三处词条

- 工作台文案统一走 `useTranslations('workbench')`，词条定义在 `CS-Web-Frontend/src/i18n/messages/tools.ts`。
- 新增 / 修改一条 workbench 文案，必须同步**三处**，否则 `AppMessages` 类型编译失败或运行时缺译：
  1. **类型（interface）**：`interface ToolsMessages` 内 `workbench: { ... }` 块新增 key；
  2. **中文（zhCN）**：`zhCN: ToolsMessages` 对象内 `workbench: { ... }` 给出中文串；
  3. **英文（en）**：`en: ToolsMessages` 对象内 `workbench: { ... }` 给出英文串。
- 聚合入口 `CS-Web-Frontend/src/i18n/languages/{zh-CN,en}.ts` 与类型 `CS-Web-Frontend/src/i18n/types.ts` 自动展开，无需手动登记。

---

## 十一、深链接（端侧完整规范）

| 端 | 权威文档 |
|---|---|
| 后端 | `CS-Web-Backend/tools/docs/BackDoc-Conv.md`（编码规范、命名、质量红线、安全/错误处理约定） |
| 前端 | `CS-Web-Frontend/tools/docs/FrontDoc-UID.md`（视觉与交互设计规范）、根级 `docs/Onboarding.md` 附录 A.6（编码规范补充、server-only 边界） |
| 前端通用 | `../docs/RootDoc-FEArch.md`（目录设计艺术，跨项目） |
