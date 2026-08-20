# RootDoc-WritingGuide｜文档编写规范总纲（Reference · 全项目文档写作 SSOT，优先级高于任何单文档旧约定）

> 更新人：3yearsZ
> 更新日：2026-08-20
> 版本：1.0.1 · 七夕（Diátaxis R 类规范，全项目文档写作 SSOT）
> Diátaxis：R（Reference · 回答「是什么」，提供全项目文档的分类框架、行文规范、架构模板、术语表的精确权威定义；不包含可执行步骤）
> 适用读者：全仓贡献者 / 文档作者 / Reviewer / 发布负责人；已完成 Onboarding 并了解项目结构
> 变更触发：新增文档类型 / 规范层级调整 / 模板结构变更 / 术语表更新

> **SSOT 分工声明**：
> - 本文档是「**全项目文档写作规范的唯一权威（SSOT）**」——涵盖分类框架（Diátaxis）、行文质量（Google 中文落地）、架构模板（Arc42）、规范术语（RFC 2119）四个层级。
> - 本文档优先级高于任何单文档中的旧约定；其他文档中的写作约定若与本文冲突，以本文为准。
> - 单文档中的实例应用 → 各 `-01-Arch.md`（Arc42 模板实例）、`-02-Sec.md` / `-03-Conv.md`（RFC 2119 实例）、`RootDoc-EngConv.md`（跨仓约定实例）。
> - 文档健康度度量与治理行动 → [RootDoc-DocHealth.md](RootDoc-DocHealth.md)（Explanation）。
> - 模块契约详情 → [RootDoc-ModuleMap.md](RootDoc-ModuleMap.md)（Reference）。

> **治理红线**：
> - MUST NOT 在未经 Diátaxis 分类标注的情况下创建新文档；所有文档 MUST 在头部声明 T/H/R/E 类型（+L3/L4 叠加标注）
> - MUST 在新建或重写文档时使用本文规定的 6 行元数据头部，顺序不可变
> - MUST NOT 在 Arch 类文档中混入 RFC 2119 约束；RFC 2119 仅用于 `-02-Sec` / `-03-Conv` / `RootDoc-EngConv`
> - MUST 在文档变更时同步更新本文档 §1.2 分类映射表

---

## 快速索引

| 章节 | 主题 | 概述 | 适用文档 | 代码位置 |
|------|------|------|----------|----------|
| **§0 规范层级** | 四层规范体系总览 | L1 Diátaxis + L2 Google + L3 Arc42 + L4 RFC 2119 | 全部文档 | — |
| **§1 Diátaxis 分类** | 四类文档定义 + 全文档映射 | T/H/R/E 定义、禁止混入项、全仓分类表 | 全部文档 | `docs/`、`CS-Web-Backend/tools/docs/`、`CS-Web-Frontend/tools/docs/`、`CS-Mobile/tools/docs/` |
| **§2 Google 写作规范** | 中文落地检查清单 | 句子/段落/用词/代码四大维度 | 全部文档 | — |
| **§3 Arc42 模板** | 架构文档 8 章结构 | 目标→上下文→构建块→运行时→部署→ADR→风险→术语 | 仅 `*-01-Arch.md`、`RootDoc-FEArch.md` | `CS-Web-Backend/tools/docs/BackDoc-01-Arch.md`、`CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md`、`CS-Mobile/tools/docs/MobileDoc-01-Arch.md`、`docs/RootDoc-FEArch.md` |
| **§4 RFC 2119** | 四级术语表 + 示例 | MUST/MUST NOT/SHOULD/SHOULD NOT/MAY + 规范类结构模板 | `*-02-Sec.md`、`*-03-Conv.md`、`RootDoc-EngConv.md` | `CS-Web-Backend/tools/docs/BackDoc-02-Sec.md`、`CS-Web-Frontend/tools/docs/FrontDoc-02-Sec.md`、`CS-Mobile/tools/docs/MobileDoc-02-Sec.md`、`docs/RootDoc-EngConv.md` |
| **§5 生效与例外** | 生效范围 + 例外声明 | 新建文档严格遵守；既有文档按 P1-P4 阶段重写 | 全部文档 | — |

---

## 0. 规范层级与适用范围

本规范为**全项目文档写作的 SSOT**，优先级高于任何单文档中的旧约定。

| 层级 | 规范 | 适用文档 |
|------|------|---------|
| L1 分类框架 | **Diátaxis**（按读者目的分四类） | 全部文档 MUST 在头部标注类型 |
| L2 行文质量 | **Google 技术写作规范**（中文落地版） | 全部文档 MUST 遵守检查清单 |
| L3 架构模板 | **Arc42 精简版**（8 章结构） | 仅 `*-01-Arch.md` 和 `RootDoc-FEArch.md` |
| L4 规范术语 | **RFC 2119**（四级关键词） | `*-02-Sec.md`、`*-03-Conv.md`、`RootDoc-EngConv.md` |

---

## 1. Diátaxis 分类映射（全文档 SSOT）

### 1.1 四类文档定义与禁止事项

| 类型 | 缩写 | 读者心态 | 文档承诺 | **禁止混入** |
|------|------|----------|----------|-------------|
| **教程 Tutorial** | T | "我想学，手把手带我走" | 读完 = 做成一件可验证的事 | API 参数表、设计背景、替代方案 |
| **操作指南 How-to** | H | "我要解决一个具体问题" | 读完 = 解决该问题 | 概念解释、入门说明、通用原理 |
| **参考 Reference** | R | "我要查某个事实" | 准确、完整、结构化 | 步骤教程、主观评价、决策理由 |
| **解释 Explanation** | E | "我想理解为什么" | 讲清背景、决策、权衡 | 操作步骤、详细参数列表 |

### 1.2 全文档分类映射表

#### 根仓 `docs/`

| 文档 | 类型 | 说明 |
|------|------|------|
| [Onboarding.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/Onboarding.md) | **T** 教程 | 新成员 30 分钟跑通全栈 |
| [README.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/README.md) | R+E | 参考（文档索引）+ 解释（治理规则） |
| [RootDoc-ADR.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-ADR.md) | **E** 解释 | 架构决策记录（讲为什么） |
| [RootDoc-Deploy.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-Deploy.md) | **H** 操作 | 生产部署步骤 |
| [RootDoc-DocHealth.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-DocHealth.md) | R | 文档健康度报告（事实清单） |
| [RootDoc-EngConv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-EngConv.md) | R+L4 | 跨仓工程约定（启用 RFC 2119） |
| [RootDoc-FEArch.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-FEArch.md) | E+L3 | 前端架构解释（叠加 Arc42） |
| [RootDoc-ICP-Filing.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-ICP-Filing.md) | H | ICP 备案操作指南 |
| [RootDoc-MigEval.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-MigEval.md) | E | 迁移评估解释（背景与权衡） |
| [RootDoc-ModuleMap.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/RootDoc-ModuleMap.md) | R | 模块-契约映射表（纯参考） |
| [api-reference.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/api-reference.md) | R | OpenAPI 参考文档 |
| [项目待办v2.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/docs/项目待办v2.md) | R | 待办事实清单（非 Diátaxis 正式类） |

#### 后端 `CS-Web-Backend/tools/docs/`

| 文档 | 类型 | 说明 |
|------|------|------|
| [BackDoc-01-Arch.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-01-Arch.md) | **E+L3** | 后端架构（Arc42） |
| [BackDoc-02-Sec.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-02-Sec.md) | **R+L4** | 安全规范（RFC 2119） |
| [BackDoc-03-Conv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-03-Conv.md) | **R+L4** | 编码规范（RFC 2119） |
| [BackDoc-Infra.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-Infra.md) | H | 基础设施操作指南 |
| [BackDoc-Refactor-CommunityService.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/BackDoc-Refactor-CommunityService.md) | E | 重构方案解释 |
| [README.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Backend/tools/docs/README.md) | R | 文档索引 |

#### 前端 `CS-Web-Frontend/tools/docs/`

| 文档 | 类型 | 说明 |
|------|------|------|
| [FrontDoc-01-Arch.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md) | **E+L3** | 前端架构（Arc42） |
| [FrontDoc-02-Sec.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-02-Sec.md) | **R+L4** | 安全规范（RFC 2119） |
| [FrontDoc-03-Conv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-03-Conv.md) | **R+L4** | 编码规范（RFC 2119） |
| [FrontDoc-UID.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-UID.md) | R | UI 设计参考 |
| [FrontDoc-Ops.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-Ops.md) | H | 运维操作指南 |
| [FrontDoc-Design-Unification-Plan.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-Design-Unification-Plan.md) | E | 设计统一计划解释 |
| [FrontDoc-Workbench-ReviewPrompt.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/FrontDoc-Workbench-ReviewPrompt.md) | R | Review Prompt 参考 |
| [README.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Web-Frontend/tools/docs/README.md) | R | 文档索引 |

#### 移动端 `CS-Mobile/tools/docs/`

| 文档 | 类型 | 说明 |
|------|------|------|
| [MobileDoc-01-Arch.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Mobile/tools/docs/MobileDoc-01-Arch.md) | **E+L3** | 移动架构（Arc42） |
| [MobileDoc-02-Sec.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Mobile/tools/docs/MobileDoc-02-Sec.md) | **R+L4** | 安全规范（RFC 2119） |
| [MobileDoc-03-Conv.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Mobile/tools/docs/MobileDoc-03-Conv.md) | **R+L4** | 编码规范（RFC 2119） |
| `arch/*.md`（6 篇） | E | 早期设计解释（逐步收敛到 Arch） |
| [README.md](file:///Users/3yearszhuang/Documents/FztbuCS-Project/CS-Mobile/tools/docs/README.md) | R | 文档索引 |

### 1.3 文档头部元数据强制格式

```markdown
# 文档名｜简短副标题
> 更新人：3yearsZ
> 更新日：YYYY-MM-DD
> 版本：X.Y.Z
> Diátaxis：[T/H/R/E]（+L3=Arc42，+L4=RFC2119）
> 适用读者：<例如：后端开发者 / 新成员 / 运维>
```

**MUST** 包含全部 6 行，顺序不可变。

---

## 2. Google 技术写作规范 · 中文落地检查清单

**提交文档前 MUST 自检，全部打勾。**

### 2.1 句子与段落
- [ ] 单句 ≤ 25 个中文字（超过则拆成两句）
- [ ] 单段 ≤ 3 句话（超过则拆分或用列表）
- [ ] 使用主动语态：用"你 + 动词"，不用"可以被执行""将被处理"
- [ ] 每个"它 / 这 / 其 / 该"都能一眼找到先行词（找不到则重复名词）
- [ ] 不使用双重否定（"并非不允许" → "允许"）

### 2.2 用词与术语
- [ ] 全文术语统一（例：不说"接口"又说"API"，二选一一以贯之）
- [ ] 缩写首次出现时标注全称（例：BFF = Backend for Frontend）
- [ ] 不用模糊词："大概""可能""尽量""基本" → 改成精确表述或删除
- [ ] 数字用阿拉伯数字（"3 个"不是"三个"；"第 2 步"不是"第二步"）
- [ ] 代码、命令、配置项 MUST 用反引号包裹（`` `uv sync` `` 不是 uv sync）

### 2.3 列表与结构
- [ ] 能用列表就不用段落（操作步骤 MUST 用有序列表）
- [ ] 列表项对称：要么全是名词短语，要么全是完整句子，不混用
- [ ] 章节层级不超过 4 级（# → ## → ### → ####，不使用 #####）
- [ ] 每篇文档开头 MUST 有「一句话承诺」：告诉读者"读完本文你能____"
- [ ] 指路式引用 ≤ 2 个 / 篇（超过则说明本文定位不清，需要重构）

### 2.4 代码与示例
- [ ] 每个代码块 MUST 有语言标注（```python 不是 ```）
- [ ] 代码块下方 MUST 有 1 句话解释：「这段代码在做什么」
- [ ] 示例 MUST 可复制运行（不含占位符 `your-token-here`，除非明确标注）
- [ ] 命令行示例前不加 `$`（直接写命令，方便复制）

---

## 3. Arc42 精简版 · 架构文档模板（仅 Arch 类使用）

`*-01-Arch.md` 和 `RootDoc-FEArch.md` **MUST** 使用以下 8 章结构，章名不可改、顺序不可变。不需要的章节写「本节不适用」并说明原因。

```markdown
# XxxDoc-01-Arch｜Xxx 架构设计

> （元数据 6 行，见 §1.3）

---

## 1. 目标与约束
- 业务目标：该子系统要解决什么问题
- 技术约束：语言 / 框架 / 部署方式 / 不可变的外部依赖
- 质量目标：性能 / 安全 / 可维护性的优先级排序

## 2. 上下文与范围
- 上游：谁调用我（列出系统 / 模块名）
- 下游：我调用谁（DB / Cache / 第三方 API）
- 不在范围内：明确列出本架构 **不负责** 的内容

## 3. 构建块视图（核心）
- 模块划分：一级模块列表 + 各自职责（1 模块 ≤ 1 句话）
- 模块依赖图：用 Mermaid 画出依赖关系（禁止循环依赖）
- 关键接口：模块之间的核心契约（函数 / 类 / API 路由）

## 4. 运行时视图
- 典型场景 1：<例如：用户注册流程> 用时序图
- 典型场景 2：<例如：异常处理流程> 用时序图
- 只画最关键的 2-3 个场景，不超过 3 个

## 5. 部署视图
- 部署拓扑：各组件部署位置（容器 / 虚拟机 / Serverless）
- 配置管理：敏感配置 / 环境变量的来源与注入方式
- 扩缩容策略：水平 / 垂直扩展的触发条件

## 6. 架构决策（ADR 摘要）
| 编号 | 决策 | 选项 | 理由 |
|------|------|------|------|
| ADR-01 | <选了什么> | <替代方案 A/B> | <为什么选这个> |

- 只列 **已不可逆** 的决策，实验性内容不算
- 详细内容链接到 RootDoc-ADR.md

## 7. 风险与技术债务
- 已知风险：<列出 + 缓解措施>
- 技术债务：<列出 + 计划偿还时间>

## 8. 术语表
| 术语 | 定义 |
|------|------|
|  |  |

- 仅列本系统特有的、可能产生歧义的术语
```

---

## 4. RFC 2119 · 规范类文档强制术语表（仅 Sec/Conv/EngConv 使用）

`*-02-Sec.md`、`*-03-Conv.md`、`RootDoc-EngConv.md` 中的 **每条规则 MUST 使用以下四级关键词**，禁止使用"应该""建议""最好"等模糊表述。

| 关键词（英文大写） | 中文对应 | 含义 | 违反严重度 |
|-------------------|----------|------|-----------|
| **MUST** | 必须 | 绝对要求，不满足就是错误 | P0 阻塞 |
| **MUST NOT** | 禁止 | 绝对禁止，出现就是错误 | P0 阻塞 |
| **SHOULD** | 应当 | 推荐做法，有充分理由可以不做，但 MUST 说明理由 | P1 建议 |
| **SHOULD NOT** | 不应当 | 不推荐做法，有充分理由可以做，但 MUST 说明理由 | P1 建议 |
| **MAY** | 可以 | 可选，随作者或团队决定 | P2 可选 |

### 4.1 使用示例

```markdown
### §3.1 数据库访问
- **MUST** 使用 SQLAlchemy ORM，**MUST NOT** 拼接原始 SQL 字符串。
- **SHOULD** 为所有查询添加索引提示，除非经压测确认无需索引。
- **MAY** 使用 Redis 缓存热点数据，缓存过期时间由业务方决定。
```

### 4.2 规范类文档结构强制

```markdown
# XxxDoc-03-Conv｜Xxx 编码规范

> （元数据 6 行）

---

## 0. 适用范围
- 适用：<哪些代码 / 哪些模块>
- 不适用：<明确列出例外>

## 1. <主题 1>
### 1.1 <规则分组>
- 每条规则 MUST 以 RFC 2119 关键词开头
- 每条规则一行，不嵌套多层列表

## 2. <主题 2>
...

## N. 检查清单（提交前 MUST 打勾）
- [ ] <自动检查命令>（例：`make lint` 全通过）
- [ ] <人工检查点 1>
- [ ] <人工检查点 2>
```

---

## 5. 生效与例外

1. 本规范自 2026-08-20 起生效，所有 **新建文档** MUST 严格遵守。
2. 既有文档在 P1-P4 阶段按计划重写，重写前按旧约定，重写后按本规范。
3. 例外 MUST 在对应文档头部元数据下方增加「例外声明」块，说明：
   - 违反了本规范哪一条
   - 为什么必须违反（技术理由、业务紧急度等）
   - 计划修复时间

---

## 自检清单（文档变更时 MUST 逐项核对）

| 检查项 | 说明 |
|--------|------|
| [ ] 头部 6 行元数据完整且顺序正确 | 更新人 / 更新日 / 版本 / Diátaxis / 适用读者 / 变更触发 |
| [ ] Diátaxis 分类标注正确 | T / H / R / E （+L3 Arc42 / +L4 RFC 2119 叠加标注） |
| [ ] 快速索引表与正文章节对齐 | 章节 / 主题 / 概述 / 代码位置准确 |
| [ ] SSOT 分工声明无冲突 | 权威归属清晰，不与其他文档职责重叠 |
| [ ] 治理红线以 RFC 2119 关键词标记 | MUST / MUST NOT / SHOULD 明确 |
| [ ] 代码位置索引可定位 | 文件路径精确，符号名准确 |
| [ ] §1.2 分类映射表已同步 | 新增/删除文档 MUST 更新分类表 |
| [ ] 无指路式引用 > 2 个 / 篇 | 超过则说明文档定位不清 |
