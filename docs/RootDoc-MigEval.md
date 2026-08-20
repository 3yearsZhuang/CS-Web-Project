# 数据迁移与多数据库支持评估报告（RootDoc-MigEval）

> 更新人：3yearsZ
> 最后更新：2026-08-20（更新 Alembic head 至 `e5f6a7b8c9d0`，版本锚定 1.0.1）
> 评估内容时点：2026-08-05（归档说明见下）
> 评估对象：`CS-Web-Frontend/data/app.db`（SQLite，旧前端单体数据库）
> 目标库：`CS-Web-Backend` 后端 PostgreSQL（库名 `domefff`，Alembic 管理）
> 评估日期：2026-08-05
>
> ⚠️ **归档说明（2026-08-07，2026-08-09 补充）**：本报告为迁移**执行前**的时点评估记录，文中"前端已原生支持 SQLite/PG 双引擎""`shared/db` 为迁移过渡期保留"等描述反映 2026-08-05 状态。迁移已于 2026-08-05 完成，前端 `src/shared/db/*`、遗留脚本与 `better-sqlite3` 依赖已于 2026-08-06/07 全部删除，当前前端零 SQLite、纯 BFF。本文保留作为迁移决策历史审计证据。

---

## 一、结论摘要

| 评估项 | 结论 |
|---|---|
| **数据能否完整迁移** | ✅ **可以迁移，但「非直迁」**——数据本身完整可读、行数小、结构清晰，但主键体系（UUID→Integer）需全量重映射，必须写专门迁移脚本，不能 `sqlite3` 直导或原样 INSERT |
| **迁移复杂度** | 🔴 **中等偏高**（主键重映射 + 认证字段变更 + FTS/会话表结构差异 + 外键顺序），是全程最重的一块 |
| **多数据库支持** | ✅ **前端已原生支持**（SQLite/PG 双引擎已落地）；**后端当前不支持**，但引入成本可控 |

---

## 二、源数据（SQLite `data/app.db`）盘点

### 2.1 体积与内容

- **数据库文件**：`app.db` 约 1.4MB（不含 WAL），实际数据量很小。
- **目录内静态资源**（需一并迁移，数据库只存路径）：
  - `avatars/`：10 个文件（约 0.5MB，jpg/png）
  - `community-images/`：1 个文件（23KB）
  - `resource-files/`：6 个文件（每个仅 4 字节，**均为空壳占位**，实际无内容）

### 2.2 各表行数（43 张表，共 ~1700 行业务数据）

| 表 | 行数 | 迁移价值 | 表 | 行数 | 迁移价值 |
|---|---|---|---|---|---|
| component_registry_variants | 1458 | 高（种子） | notifications | 22 | 低（个人通知） |
| component_registry_guides | 54 | 高（种子） | community_post_views | 13 | 低 |
| component_registry_items | 54 | 高（种子） | events | 7 | 中 |
| role_permissions | 81 | 高 | resources | 6 | 中 |
| **users** | **15** | **高（核心）** | community_categories | 4 | 高 |
| admin_actions | 43 | 中（审计→audit_logs） | exam_questions | 6 | 中 |
| login_history | 32 | 低 | exam_question_options | 20 | 中 |
| **sessions** | **75** | **低（PG 无此表）** | exams | 2 | 中 |
| community_posts | 2 | 高 | notifications 等 | ~20 | 中 |

**关键判断**：
- **真正有业务迁移价值的核心数据**：users(15)、community_posts(2)+comments(3)+categories(4)、events(7)、resources(6)、exams(2)+questions(6)+options(20)、component_registry 种子（54 项）、roles(6)+role_permissions(81)。
- **低价值可舍弃**：sessions(75)、login_history(32)、notifications(22)、admin_actions(43)、FTS 虚拟表、activity_participations(0)、各 0 行空表。
- 无任何历史大表，总数据规模很小，**迁移脚本不存在性能压力**。

### 2.3 静态资源

`resource-files/` 下 6 个文件全部为 **4 字节空文件**（`user-001-*.pdf/.png`），属测试占位，**无可迁移内容**。`avatars/` 与 `community-images/` 有真实图片，需按路径随 DB 迁移或拷贝。

---

## 三、源 Schema 与目标 PG Schema 差异分析

> 目标库 `domefff` 已用 Alembic 建好 52 张表（含全部 36 张业务表），且已有 1 个 seed 用户（admin@example.com）。

### 3.1 🔴 核心障碍：主键类型不兼容（最高风险）

| 维度 | SQLite 源 | PostgreSQL 目标 |
|---|---|---|
| users.id | **TEXT/UUID**（如 `acca09cc-0b3b-...`） | **Integer 自增**（serial） |
| 全部关联表外键 | TEXT（引用 UUID） | Integer |

**影响范围**：19 张表含 `user_id`/`author_id` 等对 users 的外键，全部需在迁移时把 UUID **映射为新的自增 Integer**。且不止用户——`community_posts`、`events`、`exams` 等每张表自身的主键也是 UUID，同样要重映射为新序列 ID，其子表（comments、reactions、options 等）的 `parent_id`/`post_id` 同步重映射。

这意味着迁移不是「逐表 COPY」，而是**先建 UUID→Integer 映射表，按外键依赖顺序逐层导入**。

### 3.2 认证字段差异（影响用户导入）

| 项 | SQLite 源 | PG 目标 |
|---|---|---|
| 密码哈希 | scrypt（旧） | bcrypt（新），支持**懒升级** |
| 主键 | UUID | Integer |
| 角色 | users 单列 `role`（'admin'/'root'/'user'） | 多对多 `user_roles` 关联表 |
| 登录态 | 自建 session（HttpOnly cookie） | JWT（access/refresh token） |

**迁移要点**：
- 密码 scrypt 哈希可直接搬移，登录时走 `password_compat` 懒升级为 bcrypt（**零停机，已设计好**）。
- 角色需把 SQLite 的 `role` 单列值映射到 PG `roles` 表对应角色 + `user_roles` 关联。
- PG 的 `users` 需要 `username`（非空唯一），而 SQLite 无此字段，需**从 display_name/email 派生**。
- `sessions` 表 PG 不存在 → 旧登录态作废，用户需重新登录（可接受）。

### 3.3 结构差异（需映射/舍弃）

| 差异项 | 处理 |
|---|---|
| SQLite `community_posts_fts*`（FTS5 虚拟表，4 张） | PG 用 GIN+tsvector 或 ILIKE，**迁移时舍弃**，数据存于 community_posts 主表 |
| SQLite `admin_actions` → PG `audit_logs` | 两表结构差异大，按 OQ-1 决策映射或**舍弃**（审计为操作痕迹，价值低） |
| SQLite `sessions` → PG 无 | **舍弃**（JWT 化） |
| Integer 布尔 0/1 → PG `Boolean` | 需类型转换 |
| ISO 字符串日期 → PG `timestamp with time zone` | 需解析转换 |
| JSON 文本（`'[]'`）→ PG `jsonb` | 需反序列化转换 |
| Integer 主键自增 | 导入时需保留/指定 id 或重建，注意**序列同步**（`setval`） |

### 3.4 兼容性良好之处

- `community_posts` 等表列结构（kind/category_id/author_id/title/content_markdown/status/...）**PG 与 SQLite 高度一致**，逻辑字段一一对应。
- 组件注册表、考试等种子数据字段映射清晰。
- 数据量极小，单脚本事务可完成，无需分批。

---

## 四、迁移路径评估

### 4.1 迁移脚本（必须新建）

`CS-Web-Frontend/tools/scripts/migrate-sqlite-to-pg.mjs`（迁移计划 Phase 6 已规划并实现、于 2026-08-05 完成数据迁移；**该脚本已于 2026-08-07 随 SQLite 清理一并删除，见文首归档说明**），用法与执行细节见本文 §八，实际执行结果见 `../CHANGELOG.md` 的"数据迁移"节）：
1. 读 SQLite → 建 `UUID → Integer` 全局映射（含 users、events、community_posts 等所有主表）。
2. 按外键依赖顺序导入：`roles` → `users`（派生 username、映射角色、scrypt 哈希搬移）→ `community_categories` → `community_posts` → `community_comments` → `events` → `exams/questions/options` → `resources` → `component_registry*` 等。
3. 类型转换：布尔、日期 ISO→tz、JSON 文本→jsonb。
4. 收尾：PG 自增序列 `setval` 对齐；跳过已存在的 seed 角色/管理员；幂等重跑保护。
5. 静态资源：`avatars/`、`community-images/` 拷贝到后端静态目录并更新 URL。

### 4.2 目标库现状影响

PG `domefff` 已有 1 个 seed 用户（admin）和预置角色（8 个）。迁移脚本必须**按 email/username 去重**，避免与 seed 冲突。

### 4.3 可行性与风险评级

| 风险 | 等级 | 说明 |
|---|---|---|
| 主键重映射遗漏导致外键悬空 | 🔴 P1 | 需严格按依赖序 + 迁移后校验（FK 完整性 + 行数对账） |
| 密码/2FA 兼容 | 🟢 低 | 懒升级方案已就绪 |
| 日期/布尔/JSON 类型转换错误 | 🟡 中 | 需逐列映射，建议先 dry-run |
| 种子数据与已有角色冲突 | 🟡 中 | 去重策略 |
| 数据本身缺失（resource 空文件、低价值表） | 🟢 低 | 明确取舍清单即可 |

**总体可行性**：✅ **数据能完整迁移到新库**，但必须走专用映射脚本，**不可直导**。

---

## 五、多数据库支持评估

### 5.1 前端（CS-Web-Frontend）——✅ 评估时点已原生支持双引擎（代码已于 2026-08-07 删除）

`src/shared/db/drivers/` 曾实现 **SQLite 与 PG 双引擎**：
- `sqlite-driver.ts`（better-sqlite3）+ `pg-driver.ts`（postgres.js），统一 `DbEngine` 接口。
- `DATABASE_PROVIDER=sqlite|pg` 运行时切换，`?` 占位符自动转 PG `$1`。
- `drizzle.config.ts` 同样支持双 dialect。

> 注：当前前端已降级为纯 BFF（薄转发到后端），`shared/db` 双引擎代码已于 2026-08-07 删除，业务数据统一走后端 PG。

### 5.2 后端（CS-Web-Backend）——⚠️ 当前仅 PostgreSQL，但引入成本可控

**现状**：
- `app/core/config.py`：`DATABASE_URL` 硬编码组装为 `postgresql+asyncpg`。
- `app/database.py`：`create_async_engine`，默认 PG，无方言抽象。
- `app/models/*`：SQLAlchemy 2.0，`Integer`/`Boolean`/`DateTime(timezone=True)`/`JSONB` 均为 PG 向写法。
- `alembic/`：单一 PG head 迁移链。

**若引入多库（如同时支持 SQLite/PostgreSQL）需改造**：
1. **Config 层**：`DATABASE_URL` 增加方言判断（`sqlite+aiosqlite://` / `postgresql+asyncpg://`）。
2. **Model 层**：SQLAlchemy 用 `Generic` 类型 + `TypeDecorator`/`Variant` 抽象主键（UUID vs Integer）、JSON、Boolean——这是最重的部分，几乎所有模型都要动。
3. **迁移**：Alembic 需为 SQLite/PG 分别维护迁移链（`alembic.ini` 多 env 或分目录），当前迁移大量使用 PG 特性（`jsonb`、`partial unique index`、`ON CONFLICT`）。
4. **Repository 层**：部分查询用了 PG 特定 SQL（`ILIKE`、`FOR UPDATE SKIP LOCKED`、`ON CONFLICT`）需加方言分支。
5. **测试**：现有 integration 测试面向 PG。

### 5.3 建议

- **不建议**给后端引入多数据库——项目铁律明确「**SQLite 禁止作生产库**」，后端唯一生产库 = PostgreSQL。多库只会增加维护成本，收益低。
- **正确姿势**：前端**曾**保留双引擎用于「迁移过渡期」开发兜底；**生产数据统一走后端 PG**。
>
> ℹ️ 变更记录见 `../CHANGELOG.md`，待办条目见 `项目待办事项-优先级重排.md`。
- 若要「本地无 PG 也能跑」，更轻的方案是 **Docker 起 PG**（根级 `docker-compose.yml` 已内置），而非维护 SQLite 方言。

---

## 六、行动建议清单

> ℹ️ 变更记录见 `../CHANGELOG.md`，待办条目见 `项目待办事项-优先级重排.md`。

---

## 七、现行 PostgreSQL 迁移链现状（1.0.1 更新，原 0.9.8 补录）

> 本章为 2026-08-08 起始补录（0.9.8）、2026-08-20 更新 head，反映当前（1.0.1）代码实际迁移状态，与上文 2026-08-05 评估时点记录互补。

### 7.1 当前数据源

- 唯一数据源：后端 **PostgreSQL**（库名 `domefff`），由 **Alembic** 管理迁移。
- 前端为纯 BFF，**零 SQLite**、无本地库；历史 SQLite→PG 脚本 `CS-Web-Frontend/tools/scripts/migrate-sqlite-to-pg.mjs` 已于 2026-08-07 随 SQLite 清理一并删除（见文首归档说明），现行不存在 SQLite 双引擎。

### 7.2 现行 Alembic 迁移链（截至 2026-08-20）

当前迁移链为单一线性链，现行 head（最新迁移）为 **`e5f6a7b8c9d0`**（add `llm_configs` 用户级功能开关，2026-08-20）；此前的 `d3e4f5a6b7c8`（add `llm_usage_logs` + `llm_configs`）与 `d4e5f6a7b8c9`（add `chat_events_trajectory`）为链上节点：

```text
… → a3b4c5d6e7f8(chinese_fts_zhparser)
  → b0b1c2d3e4f5(add_workbench_tables)
  → c2d3e4f5a6b7(add_focus_sessions)
  → d3e4f5a6b7c8(add_llm_usage_logs+llm_configs)
  → d4e5f6a7b8c9(add_chat_events_trajectory)
  → e5f6a7b8c9d0(add_user_llm_feature_toggles)  ← HEAD
```

| 迁移 ID | 内容 | 创建日期 |
|---------|------|----------|
| `a3b4c5d6e7f8` | 中文全文检索 zhparser 条件安装（不可用时静默回退 `simple`） | 2026-08-07 |
| `b0b1c2d3e4f5` | 工作台表（workbench） | 2026-08-08 |
| `c2d3e4f5a6b7` | `focus_sessions`（番茄钟追踪） | 2026-08-08 |
| `d3e4f5a6b7c8` | `llm_usage_logs` + `llm_configs`（LLM 用量与配置） | 2026-08-08 |
| `d4e5f6a7b8c9` | `chat_events` Trajectory 事件日志（学习助手全事件 append-only） | 2026-08-19 |
| `e5f6a7b8c9d0` | `llm_configs` 用户级功能开关（web_search_enabled / trajectory_enabled）← **HEAD** | 2026-08-20 |

> 注：`a3b4c5d6e7f8` 是中文检索可靠性化的关键里程碑，属现行链上的中间节点，并非 head。

### 7.3 部署自动迁移

- 容器编排内后端 `DB_AUTO_MIGRATE=true` → 空库自动 `alembic upgrade head`（head = `e5f6a7b8c9d0`）；库已最新则无操作。详见 `docs/RootDoc-Deploy.md` §四。
- 回滚：`alembic downgrade` 可逐级回退；生产建议先独立迁移 job 再起多 worker（见 `CS-Web-Backend/tools/docs/BackDoc-Infra.md` §六）。

### 7.4 与本文评估时点记录的关系

- 上文第一~六章为 2026-08-05「迁移执行前」评估，文中"前端已原生支持 SQLite/PG 双引擎"等描述均已在 2026-08-07 清理后失效（见文首归档说明）。
- 本章（§七）为现行 PostgreSQL 单一事实源补充，确认**无 SQLite 双引擎、无 `migrate-sqlite-to-pg.mjs`**，迁移链以 Alembic 线性管理。

---

## 附：验证依据

- 源库：`CS-Web-Frontend/data/app.db` 43 张表，~1700 行（含 1458 组件变体种子），users 15 人（UUID 主键）。
- 目标库：`domefff` 本地 PG 运行中，52 张表（Alembic 建），已有 1 seed 用户。
- 迁移计划：后端 `CS-Web-Backend/tools/docs/BackDoc-Infra.md` §六 迁移验证 Phase 6 已规划数据迁移脚本，**脚本 `migrate-sqlite-to-pg.mjs` 已于 2026-08-05 实现并跑通（19 张表全部入库，外键完整、类型转换正确），该脚本已于 2026-08-07 删除**。
- 主键差异：后端 `app/models/user.py` 明确 `id: Mapped[int]`；SQLite users 为 TEXT UUID。
- 现行 Alembic head（2026-08-20）：**`e5f6a7b8c9d0`**（详见本文 §七）；此前里程碑 `d3e4f5a6b7c8`、`focus_sessions` 迁移 `c2d3e4f5a6b7`。

---

## 八、前端迁移执行细节

> 状态：✅ **已归档**（2026-08-07）。迁移已于 2026-08-05 执行完成（19 张表全量入库）；迁移脚本 `tools/scripts/migrate-sqlite-to-pg.mjs` 与前端全部 SQLite 依赖（`better-sqlite3`）已于 2026-08-07 随清理删除。如需重跑（不应发生），可从 git 历史恢复脚本并临时安装依赖。
> 关联：数据库双引擎演进与迁移规划见本文 §八；前端架构见 `CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md`。

### 8.1 迁移历史概述

旧前端单体库 `data/app.db`（SQLite）的业务数据于 2026-08-05 迁移至后端 PostgreSQL（库 `domefff`）。

**为什么不能直导**：SQLite 主键为 TEXT/UUID，PG 为 Integer 自增；迁移脚本建立了「UUID -> Integer」映射、按外键依赖序逐层导入，并处理认证字段与类型转换。详见本文 §八（迁移执行细节）。

**迁移结果**：19 张表全量入库，外键完整、类型转换正确、静态资源已随迁（验证记录见本文「附：验证依据」）。

### 8.2 迁移范围与取舍

**会迁移的表（业务数据，行数与 SQLite 一致）**

| 模块 | 表 |
|------|----|
| 用户/认证 | users、user_roles、two_factor_auth |
| 社区 | community_categories、community_posts、community_comments |
| 活动 | events、event_registrations |
| 考试 | exams、exam_questions、exam_question_options |
| 资源/组件 | resources、component_registry_items / _variants / _guides |
| 其他 | notifications、join_applications、announcements、tasks、task_claims、points_transactions、settings |

**明确舍弃（PG 无对应表或低价值）**

- `sessions` / `login_history`：PG 用 JWT，无此表，**旧登录态作废，用户需重新登录**
- `admin_actions`：审计操作痕迹，低价值，并入 PG `audit_logs`（不做逐条映射）
- FTS 虚拟表（`community_posts_fts*`）：SQLite 专属，PG 用 ILIKE/GIN，数据在主表已保留
- `resource-files/` 下的 6 个 4 字节空壳文件：无可迁移内容

### 8.3 关键实现与注意事项（踩坑记录）

**8.3.1 主键重映射（最高风险）**
- 全部 UUID/TEXT 主键 -> PG Integer 自增序列，脚本在内存维护 `UUID->Integer` 映射。
- **19 张表**含 `user_id`/`author_id` 外键，须按映射回填；否则外键悬空。
- 导入顺序严格按外键依赖：roles -> users -> categories -> posts -> comments -> events -> exams -> resources -> component -> 其余。

**8.3.2 认证字段差异**
- SQLite `users.role` 单列 -> PG `user_roles` 多对多（`admin`->admin、`user`->user）。
- `root` 角色：PG 无此角色 -> 映射为 `is_superuser=true` + 挂 `admin` 角色。
- `username`：SQLite 无此字段，由 email 前缀/display_name 派生，冲突自动加 `_1` 后缀。
- 密码：scrypt 哈希**原样搬移**，登录时后端 `password_compat` 懒升级为 bcrypt（零停机）。

**8.3.3 类型转换**
- Integer 布尔 0/1 -> PG `boolean`
- ISO / `YYYY-MM-DD HH:MM:SS` 日期 -> PG `timestamptz`
- JSON 文本（`'[]'`）-> PG `jsonb`
- 组件注册表：SQLite `item.id` 是 `cmp-button` 形式（**≠ slug**，slug 是 `button`），variants/guides 的 `item_id` 引用的是 **id** 而非 slug —— 脚本按 `item.id` 回填，勿误用 slug。

**8.3.4 社区图片 URL 重写**
- 旧前端社区图 URL 为 `/api/community/images/`，后端为 `/api/community/community/images/`。
- 脚本会自动将 `content_markdown` 中的 `/api/community/images/` 重写为 `/api/community/community/images/`。

**8.3.5 幂等与 RESET**
- users 按 email 去重；component 按 slug/唯一约束去重。
- `RESET=1` 会 `TRUNCATE` 业务表（**仅 PG 中确实存在的表**；`sessions`/`login_history` 不在 RESET 列表，因为它们未迁移到 PG）`RESTART IDENTITY CASCADE`，保留 `roles`/`users` 种子后重导。
- RESET 后必须为「已存在用户」补登记 PG id 映射，否则后续外键悬空（脚本已处理）。

**8.3.6 events 列表字段必须为 `[]` 而非 `null`**
- PG `events.tags/topics/registration_fields` 为 jsonb 可存 `null`，但后端 `EventOut` 定义为 `List[str] = []`（非 Optional），`null` 会导致活动列表/详情接口响应校验 422。
- 脚本已用 `toJson(e.x, [])` 兜底为空数组；勿改用 `null` 兜底。

### 8.4 静态资源迁移与迁移后验证

> ℹ️ 待办条目（静态资源手动复制、迁移后验证清单）见 [项目待办事项-优先级重排.md](./项目待办事项-优先级重排.md)。

### 8.5 关联文档

- 迁移规划 / 双引擎演进：见本文 §八
- 运维 / 回滚流程：`CS-Web-Frontend/tools/docs/FrontDoc-Ops.md`
- 后端迁移计划与验证：`CS-Web-Backend/tools/docs/BackDoc-Infra.md` §六 迁移验证

---

## 九、信息缺口声明（1.0.1）

- **迁移 head 与任务参数卡不一致**：本文任务参数卡标注"迁移 head = `a3b4c5d6e7f8`"，但当前代码（2026-08-20）实际 Alembic head 为 **`e5f6a7b8c9d0`**（`a3b4c5d6e7f8` 为链上中间里程碑，提供中文检索 zhparser 能力；`d3e4f5a6b7c8`/`d4e5f6a7b8c9` 为后续节点）。本文以代码实际状态为准写入 §七；参数卡口径需由主理人校正。
- **`focus_sessions` 迁移 ID 已确认**：`c2d3e4f5a6b7`，与参数卡一致。
- **SQLite 双引擎 / `migrate-sqlite-to-pg.mjs`**：已删除并归档（见文首），现行无此能力，无待补数据。
- **外部链接核查**：本文引用的 `BackDoc-Infra.md` / `CHANGELOG.md` / `项目待办事项-优先级重排.md` 均存在，无坏链；已删除文件（`migrate-sqlite-to-pg.mjs`、`BackDoc-MigV.md`）均在正文显式标注"已删除/已并入"，非失效引用。
