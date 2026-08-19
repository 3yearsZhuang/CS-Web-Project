# 工作台 Schema 配置驱动卡设计（schema widget）

> 状态：**Phase A 已实现（2026-08-19）**，设计稿归档备查
> 适用：`CS-Web-Frontend/src/modules/workbench/`
> 背景：成员覆盖「普通社团成员 + 开发者」两类 → 让普通成员通过 JSON 声明即可自建简单卡，开发者可手写复杂组件。

---

## 1. 背景与目标

现状：工作台有 7 个注册 widget（`widget-registry.ts`），已统一到 `WorkbenchCard` 外壳（`workbench-card.tsx`）。但新增 widget 仍需写 React 组件 + 注册 + i18n，普通成员无法自助。

目标：
1. **普通成员**：填一段 JSON（或后续经简易表单）声明字段与数据源 → 运行时自动渲染成工作台卡片，零代码。
2. **开发者**：保留手写组件路径（现有 `WIDGETS` 数组）；或扩展 `SchemaWidgetType` 增加新卡型。
3. **与现有架构无缝衔接**：复用 `WorkbenchCard` 外壳、`WIDGET_SIZE_SPECS` 尺寸系统、`wb_` localStorage 持久化与备份。

## 2. 能力边界（先划清，避免做半吊子）

**Schema 卡只覆盖「简单数据展示/轻交互」**。判定规则：卡片若需要以下任一能力 → **不纳入 schema，走手写组件**：

| 能力 | 现有示例 | 结论 |
|---|---|---|
| SSE 流式 / 打字机 | `assistant-chat` | 手写 |
| 状态机 + 定时器 + WebAudio + IndexedDB | `pomodoro` | 手写 |
| 加密配置写入（API Key） | `llm-config` | 手写 |
| 复杂图形网格（53×7 热力图） | `github-heatmap` | 手写 |
| 数字/文本/列表/进度/倒计时/链接/便签 | 新增 schema 卡 | **schema** |

一句话判定：**「流式 / 状态机 / 音频 / 加密 / 复杂图形」任一命中 → 手写**；其余纯展示与轻增删 → schema。

## 3. WidgetSchema 定义

新增 `src/modules/workbench/schema/widget-schema.ts`（类型 + 校验器）：

```ts
export type SchemaWidgetType =
  | 'count'      // 数字 + 标签
  | 'list'       // 字段列表
  | 'progress'   // 进度环/条
  | 'countdown'  // 倒计时
  | 'note'       // 本地便签（可编辑）
  | 'link';      // 快捷链接集合

export interface SchemaField {
  key: string;
  label?: string;       // 显示名，缺省用 key
  kind?: 'text' | 'date' | 'number' | 'status';
  /** list 行点击目标：href 模板，支持 {key} 插值，如 /tools/exam/{id} */
  href?: string;
}

export type SchemaData =
  | { kind: 'local'; key: string; default?: unknown }                 // localStorage（wb_ 前缀）
  | { kind: 'api'; url: string; path?: string }                       // 复用现有 API（见 §5 白名单）
  | { kind: 'static'; value: unknown[] };                             // 静态示例数据

export interface SchemaWidgetConfig {
  id: string;                    // 唯一 id（kebab-case），如 'counter-courses'
  title: string;                 // 显示标题（成员自拟，暂不进 i18n）
  corner?: string;               // 角标 2-3 字符，缺省取 type 缩写（CNT/LST/PRG/CDN/NTE/LNK）
  type: SchemaWidgetType;
  size?: WidgetSizeKey;          // 缺省 1x2
  sizeOptions?: WidgetSizeKey[]; // 缺省 ['1x1','1x2','2x1','2x2']
  data: SchemaData;
  fields?: SchemaField[];        // list 用
  options?: {
    target?: number;             // progress 目标值
    dateKey?: string;            // countdown 目标日期字段
    accent?: 'primary' | 'destructive' | 'emerald'; // 计数/进度强调色
  };
}
```

**示例（普通成员可直接粘贴）**：

```json
{
  "id": "courses-left",
  "title": "剩余课程",
  "type": "count",
  "data": { "kind": "local", "key": "wb_courses", "default": [] }
}
```

```json
{
  "id": "my-deadlines",
  "title": "我的截止日",
  "type": "list",
  "data": { "kind": "local", "key": "wb_deadlines", "default": [] },
  "fields": [
    { "key": "title", "label": "事项" },
    { "key": "due", "label": "截止", "kind": "date" },
    { "key": "status", "kind": "status" }
  ]
}
```

## 4. 内置类型渲染约定（全部基于 WorkbenchCard）

| type | children 渲染 | 备注 |
|---|---|---|
| `count` | 大数字 + 标签（复用 `display-serif tabular-nums` 与 `github-heatmap` 同款） | 空数据 → 显示 0 |
| `list` | `idx-rail` 列表（复用 `today-tasks` 行样式），字段按 `fields` 排列；`href` 支持插值 | 空 → empty 三态 |
| `progress` | 内联 SVG 进度环（复用 `pomodoro` 环形写法，无动画依赖） | `target` 缺省 100 |
| `countdown` | 最大项大号倒计时 + 其余列表（复用 `exam-countdown` 结构） | `dateKey` 定位目标 |
| `note` | 可编辑便签列表（复用 `quick-notes`） | 数据写回 localStorage |
| `link` | 链接列表（icon + 标题 + 描述） | href 直链 |

规则：
- 标题头/角标/操作区/三态全部由 `WorkbenchCard` 提供 → **schema 渲染器零重复样板**。
- 空态：`data` 为空数组/空对象 → `empty` 三态（文案用类型默认，如「暂无数据」）。
- 尺寸降级：`size` 为 `1x1` 时隐藏次要字段/副信息（复用 §7 的降级策略）。

## 5. 数据源约束（安全与契约）

- **`local`**：key 必须 `wb_` 前缀，否则校验拒绝（防污染非工作台数据）。
- **`api`**：**只允许复用现有已存在端点**，白名单校验：
  - 前缀白名单：`/api/workbench/**`、`/api/tools/**`（前端 BFF 层），且 `url` 中不得含 `${...}` 模板注入（防 SSRF/契约漂移）。
  - **不新增后端路由** → 不触发 openapi baseline 契约门禁（`make check-contract`）。
  - `path` 为响应体字段路径（如 `data.items`），用点号取数，不做任意代码执行。
- **`static`**：仅用于首次示例/演示，导入恢复时保留。

## 6. 两类成员使用路径

**普通成员（零代码）**：
1. 打开工作台 → 布局设置面板 → 「添加 Schema 卡」。
2. 粘贴 JSON（或 Phase B 的简易表单）→ 校验通过 → 写入 `wb_schema_widgets`。
3. 运行时由 `SchemaWidgetRenderer` 渲染；可拖拽/改尺寸/隐藏（与现有 widget 一致）。

**开发者**：
- 路径 A：扩展 `SchemaWidgetType` + 在渲染器 `switch` 中新增分支（适合简单卡）。
- 路径 B：手写组件注册进 `WIDGETS`（适合复杂卡，现状不变）。
- 新增 schema 类型时同步更新校验器与文档。

## 7. 与现有架构的衔接（实现清单）

| 项 | 文件 | 说明 |
|---|---|---|
| 类型 + 校验器 | 新增 `schema/widget-schema.ts` | 类型、白名单、`parseSchemaConfig`（含错误消息） |
| 渲染器 | 新增 `schema/schema-widget-renderer.tsx` | `type` 分发到各渲染子件，全部包 `WorkbenchCard` |
| 合并注册 | 改 `widget-registry.ts` | 导出 `SCHEMA_TYPES` 常量（供渲染器用）；`WIDGETS` 末尾追加内置 `schema` 卡（id 固定 `schema-widget`，渲染器内按 `wb_schema_widgets` 数据渲染多张卡） |
| 存储 | 新增 hook `schema/use-schema-widgets.ts` | 包 `useLocalStorage('wb_schema_widgets', [])`，含 parse+校验 |
| 备份 | 改 `workbench.tsx` `BACKUP_KEYS` | 追加 `wb_schema_widgets`（顺带覆盖布局重置一致性） |
| 布局合并 | 改 `workbench.tsx` `orderedWidgets` | 将 schema 卡按用户 order/hidden 与内置卡统一处理；`hidden`/`sizes` 复用 `wb_widget_prefs` |

**渲染骨架（示意）**：

```tsx
// widget-registry.ts 追加
{
  id: 'schema-widget',
  titleKey: 'schemaWidget',
  component: SchemaWidgetRenderer, // 内部渲染全部 schema 卡
  defaultSize: '2x2',
  sizeOptions: ['1x1', '1x2', '2x1', '2x2', '2x3'],
}
```

```tsx
// schema-widget-renderer.tsx（示意）
export function SchemaWidgetRenderer() {
  const { configs } = useSchemaWidgets();
  return (
    <div className="flex flex-col gap-4">
      {configs.map((cfg) => (
        <SchemaCard key={cfg.id} config={cfg} />
      ))}
    </div>
  );
}
```

## 8. 实施阶段拆解（每步独立可回滚）

- **Phase A（内核）**：类型 + 校验器 + 渲染器（count/list/progress/countdown/note/link 六型）+ registry 内置卡 + `useSchemaWidgets` + 备份。交付：普通成员可粘贴 JSON 生成卡。
- **Phase B（易用性）**：布局设置面板内嵌「添加 Schema 卡」简易表单（标题/类型/数据源 key/字段），生成 JSON 免手写。
- **Phase C（社区）**：预置模板库（如「本周考试倒计时」「社团待办」「学习进度」）一键导入；文档 + 示例 JSON 归档。

建议先做 Phase A，验证 JSON 工作流再上表单。

## 9. 风险与需拍板项

| # | 决策点 | 选项 | 建议 |
|---|---|---|---|
| 1 | schema 卡标题是否进 i18n | A 成员自拟单语言（简单） / B 走 i18n（规范但成员需维护词条） | **A**，标题是成员私有内容 |
| 2 | api 数据源白名单 | A 仅 `/api/workbench/**`+`/api/tools/**` 前缀 / B 任意 GET | **A**，安全 + 契约稳定 |
| 3 | 多张 schema 卡合并为一张内置卡 vs 每卡独立注册 | A 合并（本设计） / B 动态独立注册 | **A**，避免与 dnd/registry 耦合 |
| 4 | Phase B 表单优先级 | A 紧随内核 / B 观察 JSON 使用后再定 | **B**，先验证真实需求 |
| 5 | 是否允许 schema 卡自定义组件渲染 | A 不允许（纯声明） / B 允许 escape hatch | **A**（Phase A），复杂需求走手写路径 |

---

*评审通过后，按 Phase A 落地并同步模块 README 与 CHANGELOG。*
