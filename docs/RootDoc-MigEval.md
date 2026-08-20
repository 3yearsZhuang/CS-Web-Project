# RootDoc-MigEval：数据迁移与多数据库支持评估（Explanation · 为什么选择当前单一 PostgreSQL 架构）

> 更新人：3yearsZ
> 更新日：2026-08-20
> 版本：1.0.1 · 七夕（Diátaxis E 类样板，统一解释类文档规范）
> Diátaxis：E（Explanation · 回答「为什么」，提供迁移决策背景、评估过程与结论；不包含可执行步骤）
> 适用读者：架构师 / 后端开发者 / DBA；已了解项目架构与数据层现状
> 变更触发：数据迁移完成 / 数据库选型变更 / 多引擎支持重新评估

> **SSOT 分工声明**：
> - 本文档是「**SQLite → PostgreSQL 数据迁移决策与评估记录**」的唯一权威（SSOT）。
> - 迁移执行步骤与验证命令 → [BackDoc-Infra.md](../CS-Web-Backend/tools/docs/BackDoc-Infra.md) 附录 A（Reference）。
> - 迁移后部署流程 → [RootDoc-Deploy.md](RootDoc-Deploy.md)（How-to）。
> - 架构决策总览 → [RootDoc-ADR.md](RootDoc-ADR.md) §2（ADR-009 前后端分离决策）。
> - Alembic 迁移链现状 → [BackDoc-Infra.md](../CS-Web-Backend/tools/docs/BackDoc-Infra.md) §3（数据库与事务）。

> **治理红线**：
> - MUST NOT 在任何新代码或文档中引入 SQLite 作为生产数据库；后端唯一生产库为 PostgreSQL
> - MUST 在 Alembic 迁移链新增 head 时同步更新本文档 §4.1 的迁移链现状
> - SHOULD 在评估新数据库引擎或多引擎支持时参考本文档 §2 的评估框架与障碍清单
> - MUST NOT 撤销本文档的迁移决策（SQLite → PG 单程迁移），如需重新评估 MUST 发起新的 ADR

---

## 1. 背景与动机：为什么要从 SQLite 迁移到 PostgreSQL

### 1.1 迁移前架构（Phase 1 单体）

项目最初使用 **Next.js Monolith + SQLite（WAL 模式）** 作为单体原型架构，核心目标是快速验证 MVP 业务可行性。SQLite 的零配置特性适合快速启动，但随着项目演进暴露出以下瓶颈：

| 瓶颈 | 影响 |
|---|---|
| **并发写入限制** | SQLite 单写者模型，多 worker 部署时写锁竞争 |
| **数据完整性** | 无外键约束（或需手动 `PRAGMA foreign_keys=ON`），历史数据可能存在引用残缺 |
| **功能受限** | 无 `JSONB`、无 `PARTIAL UNIQUE INDEX`、无 `ILIKE`、无 `FOR UPDATE SKIP LOCKED` |
| **多端扩展困难** | 小程序/APK 新增 API 时需共享数据，SQLite 文件复制/同步成本高 |
| **安全边界模糊** | 数据库与业务代码在同一进程，无法独立隔离；多实例部署时数据一致性难保证 |

### 1.2 迁移决策的核心动因

2026-08 决定执行 Phase 3（前后端分离），将架构从单体演进为 **BFF（薄转发）+ FastAPI（厚业务）+ PostgreSQL（强一致性）**。数据库迁移是架构转型的核心环节，需要回答三个关键问题：

1. 数据能否完整迁移？
2. 迁移的技术复杂度和风险等级？
3. 前端是否需要保留多数据库支持（SQLite/PG 双引擎）？

---

## 2. 评估过程与发现

### 2.1 源数据盘点（SQLite `data/app.db`）

| 指标 | 数值 | 评估 |
|---|---|---|
| **数据库文件** | ~1.4 MB（不含 WAL） | 数据量很小 |
| **业务表总数** | 43 张 | 结构清晰 |
| **业务行总数** | ~1,700 行 | 迁移脚本无性能压力 |
| **核心用户数** | 15 人 | 低风险 |
| **静态资源** | 11 个图片文件（~0.5 MB） | 需随 DB 路径拷贝 |
| **空壳资源文件** | 6 个 4 字节占位文件 | 无可迁移内容 |

**数据价值分层**：

| 层次 | 内容 | 迁移价值 |
|---|---|---|
| **核心必迁** | users(15)、community_posts(2)+comments(3)+categories(4)、events(7)、exams(2)+questions(6)+options(20)、role_permissions(81)、component_registry 种子(54 项) | 高 |
| **可选迁移** | admin_actions(43)、login_history(32)、notifications(22)、community_post_views(13) | 中（审计痕迹、个人通知价值低） |
| **明确舍弃** | sessions(75)、FTS5 虚拟表(4)、resource-files 空壳(6)、activity_participations(0) | 低（PG 已用 JWT/PG 全文检索替代） |

### 2.2 核心障碍识别

评估发现迁移存在 **5 大技术障碍**：

| 障碍 | 风险等级 | 影响范围 | 解决方案 |
|---|---|---|---|
| **主键类型不兼容** | 🔴 最高 | 19 张表含 `user_id`/`author_id` 外键 | UUID→Integer 映射表 + 按外键依赖序导入 |
| **认证字段差异** | 🟡 中 | users 表 | scrypt→bcrypt 懒升级 + role 单列→多对多映射 |
| **结构差异** | 🟡 中 | FTS5 虚拟表、admin_actions→audit_logs、sessions→JWT | 明确取舍清单 |
| **类型转换** | 🟡 中 | 布尔 0/1→Boolean、ISO 字符串→timestamp、JSON 文本→jsonb | 逐列映射 |
| **序列同步** | 🟢 低 | 所有自增主键表 | 迁移后 `setval` 对齐 |

**核心发现**：迁移不是「逐表 COPY」，而是**先建 UUID→Integer 映射表，按外键依赖顺序逐层导入**。

### 2.3 多数据库支持评估

| 评估对象 | 现状 | 结论 |
|---|---|---|
| **前端（CS-Web-Frontend）** | 曾实现 SQLite/PG 双引擎（`shared/db/drivers/`），统一 `DbEngine` 接口 | ❌ 2026-08-07 已全部删除，前端降级为纯 BFF，零 SQLite |
| **后端（CS-Web-Backend）** | 仅 PostgreSQL，`DATABASE_URL` 硬编码为 `postgresql+asyncpg`，SQLAlchemy 2.0 PG 向写法 | ❌ 不建议引入多引擎，铁律「SQLite 禁止作生产库」 |

**决策**：项目铁律明确「**SQLite 禁止作生产库**」，后端唯一生产库 = PostgreSQL。前端历史双引擎仅用于迁移过渡期，已随 Phase 3 清理全部删除。

---

## 3. 迁移执行与风险控制

### 3.1 迁移脚本设计

迁移脚本（`migrate-sqlite-to-pg.mjs`，已于 2026-08-07 随 SQLite 清理删除）采用以下设计：

1. **UUID→Integer 全局映射**：在内存维护所有主表的主键映射
2. **严格按外键依赖序导入**：`roles → users → categories → posts → comments → events → exams → resources → component_registry`
3. **类型转换层**：布尔、日期、JSON 文本的自动转换
4. **幂等重跑保护**：按 email/username 去重，支持 `RESET=1` 清空后重导
5. **静态资源迁移**：avatars/community-images 拷贝到后端静态目录并更新 URL

### 3.2 风险控制矩阵

| 风险 | 缓解措施 | 状态 |
|---|---|---|
| 主键重映射遗漏导致外键悬空 | 严格按依赖序 + 迁移后 FK 完整性校验 + 行数对账 | ✅ 已验证 |
| 密码/2FA 兼容 | scrypt 哈希原样搬移 + `password_compat` 懒升级为 bcrypt（零停机） | ✅ 已验证 |
| 日期/布尔/JSON 类型转换错误 | 逐列映射 + 先 dry-run 再实际导入 | ✅ 已验证 |
| 种子数据与已有角色冲突 | 按 email/username 去重，跳过已存在的 seed 角色/管理员 | ✅ 已验证 |
| 数据本身缺失 | 明确取舍清单，resource 空壳文件直接舍弃 | ✅ 已验证 |

### 3.3 迁移结果

| 指标 | 结果 |
|---|---|
| 迁移表数 | 19 张核心业务表全部入库 |
| 外键完整性 | ✅ 完整（无悬空引用） |
| 类型转换 | ✅ 正确（布尔/日期/JSON） |
| 密码兼容 | ✅ scrypt→bcrypt 懒升级正常 |
| 静态资源 | ✅ 已随迁到后端静态目录 |
| 集成测试 | ✅ 全绿（432 passed） |
| OpenAPI 契约 | ✅ 零漂移 |

---

## 4. 当前状态与结论

### 4.1 现行 PostgreSQL 迁移链（2026-08-20）

当前迁移链为单一线性链，head（最新迁移）为 **`e5f6a7b8c9d0`**：

```text
… → a3b4c5d6e7f8(chinese_fts_zhparser)
  → b0b1c2d3e4f5(add_workbench_tables)
  → c2d3e4f5a6b7(add_focus_sessions)
  → d3e4f5a6b7c8(add_llm_usage_logs+llm_configs)
  → d4e5f6a7b8c9(add_chat_events_trajectory)
  → e5f6a7b8c9d0(add_user_llm_feature_toggles)  ← HEAD
```

| 迁移 ID | 内容 | 日期 |
|---|---|---|
| `a3b4c5d6e7f8` | 中文全文检索 zhparser 条件安装 | 2026-08-07 |
| `b0b1c2d3e4f5` | 工作台表（workbench） | 2026-08-08 |
| `c2d3e4f5a6b7` | `focus_sessions`（番茄钟） | 2026-08-08 |
| `d3e4f5a6b7c8` | `llm_usage_logs` + `llm_configs` | 2026-08-08 |
| `d4e5f6a7b8c9` | `chat_events` Trajectory 事件日志 | 2026-08-19 |
| `e5f6a7b8c9d0` | `llm_configs` 用户级功能开关 ← **HEAD** | 2026-08-20 |

### 4.2 架构定位

| 维度 | 2026-08-05 评估时点 | 2026-08-20 当前状态 |
|---|---|---|
| 前端 | 已原生支持 SQLite/PG 双引擎 | ❌ 已删除全部 SQLite 代码，纯 BFF |
| 后端 | 仅 PostgreSQL | ✅ 保持不变 |
| 迁移脚本 | 已规划并实现 | ❌ 已删除（数据已迁移完成） |
| 数据源 | SQLite + PG 双源 | ✅ 单一 PostgreSQL 真源 |

### 4.3 一句话结论

> **数据迁移（Phase 3 核心）已成功完成：19 张核心业务表全量入库、外键完整、类型转换正确、密码兼容正常。系统已从 SQLite 单体架构平滑演进为 BFF + FastAPI + PostgreSQL 三层架构，不再需要多数据库支持。**

---

> ↩ **返回根级文档地图**：[README.md](README.md) · **架构决策**：[RootDoc-ADR.md](RootDoc-ADR.md) · **后端基础设施**：[BackDoc-Infra.md](../CS-Web-Backend/tools/docs/BackDoc-Infra.md) · **全栈部署**：[RootDoc-Deploy.md](RootDoc-Deploy.md)
