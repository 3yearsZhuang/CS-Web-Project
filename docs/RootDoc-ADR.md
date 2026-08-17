# RootDoc-ADR：架构决策与系统设计 SSOT

> 文档层级：**L0（根级 `docs/`，跨仓库权威）**
> 角色：架构决策（ADR）索引、边界上下文、数据流、韧性机制、BFF 交互风格的**唯一权威位置（SSOT）**
> 来源：2026-08-09 文档治理重构，从 0.9.1 演变分卷抽离上述活内容（原归档已并入根 `CHANGELOG.md` 后删除）
> 关联：完整 ADR 决策记录见 `[CHANGELOG.md](../CHANGELOG.md)`；前端权威架构见 `[FrontDoc-01-Arch.md](../CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md)`；治理规则见 `[DocGovernance.md](./DocGovernance.md) §2（所有权矩阵）
> 治理红线：禁止在根 `CHANGELOG.md` 历史章节中复述以下内容（对应章节已改为指向本文档的指针）

---

## 一、架构决策记录（ADR）索引

> ADR-001 ~ ADR-019 的完整决策记录已迁移至根 `CHANGELOG.md`（已实施项）与 `项目待办事项.md`（待评估项）。本节为索引速查 SSOT。

| ADR | 主题 | 状态 | 摘要 |
|-----|------|------|------|
| ADR-001 | 模块化目录结构 | ✅ 已实施 | 按业务域拆分 `modules/`，每域自包含 server/types/ui |
| ADR-002 | 数据库双引擎抽象 | ✅ 已实施 | Drizzle ORM + `DATABASE_DIALECT` 切换 SQLite/PG |
| ADR-005 | Repository 抽象层 | ✅ 已实施 | `getRepositories()` 屏蔽方言差异 |
| ADR-009 | 前后端分离 + 全量迁移至后端 PG | ✅ 已收官 | 前端降级为 BFF，运行时不再读写 SQLite；后端承载全部业务/认证/邮件 |
| ADR-018 | 0.9.1 预发布就绪包 | ✅ 已实施 | SLO + alerting + load test + restore drill + runbook + rollback + CI 加固 |
| ADR-019 | 前端重建适配 community v2 | ✅ 已实施 | 2026-08-03 前端重建 |

> 完整 ADR 表（含 ADR-003/004/006-008/010-017）见根 `[CHANGELOG.md](../CHANGELOG.md)`。

---

## 二、边界上下文（Bounded Context）

> 当前 BFF 视角的权威架构图见 `[FrontDoc-01-Arch.md](../CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md) Part A`。下方「当前（BFF 视角）」为 SSOT 快照；「迁移前单体」仅作演进对照，归档快照见根 `CHANGELOG.md`（0.9.1 分卷已并入）。

**当前（BFF 视角）**：

```
                 ┌─────────────────────────────────────┐
                 │        Next.js BFF（薄转发）          │
                 │  ┌──────────┐  ┌──────────────────┐  │
                 │  │  Auth    │  │  Community       │  │
                 │  │ (Cookie) │  │ (community/community/members)│
                 │  └────┬─────┘  └────────┬─────────┘  │
                 │       │ backend-client.ts  │          │
                 │  ┌────┴─────┐  ┌────────┴─────────┐  │
                 │  │ Notification│  │  Events          │  │
                 │  └──────────┘  └──────────────────┘  │
                 │  ┌──────────┐  ┌──────────────────┐  │
                 │  │  Tools   │  │  Admin (UI 兜底)  │  │
                 │  │(exam/...)│  │                  │  │
                 │  └──────────┘  └──────────────────┘  │
                 └──────────────────────┬──────────────┘
                                        │ JWT + snake_case→camelCase
                                 ┌──────┴──────┐
                                 │ FastAPI + PG │ （后端承载业务/认证/邮件/RBAC enforce）
                                 └─────────────┘
```

**迁移前（单体，历史对照）**：

```
                 ┌─────────────────────────────────────┐
                 │           Next.js Monolith           │
                 │  ┌──────────┐  ┌──────────────────┐  │
                 │  │  Auth    │  │  Community       │  │
                 │  │ (session)│  │ (community/community/members)│
                 │  └────┬─────┘  └────────┬─────────┘  │
                 │       │ event bus       │            │
                 │  ┌────┴─────┐  ┌────────┴─────────┐  │
                 │  │ Notification│  │  Events          │  │
                 │  └──────────┘  └──────────────────┘  │
                 │  ┌──────────┐  ┌──────────────────┐  │
                 │  │  Tools   │  │  Admin           │  │
                 │  │(exam/...)│  │ (audit/ops)      │  │
                 │  └──────────┘  └──────────────────┘  │
                 └──────────────────────┬──────────────┘
                                        │ DbEngine / getDb()
                                 ┌──────┴──────┐
                                 │   SQLite    │ (-> PostgreSQL, see Part B；ADR-009 收官多数模块经 Repository 抽象)
                                 └─────────────┘
```

---

## 三、数据流图

**当前（BFF 视角）**：

```
用户请求
  -> Next.js Route Handler（src/app/api/**/route.ts）
  -> assertAllowedOrigin + Zod body 校验
  -> proxyBackend（shared/backend-client.ts）
       ├── 注入 Authorization: Bearer <JWT>（从 HttpOnly Cookie）
       ├── 401 静默刷新（调用后端 /auth/refresh 轮换令牌）
       └── snake_case → camelCase 响应翻译
  -> 后端 FastAPI（require_permission enforce + 业务逻辑 + PostgreSQL）
  -> 响应（normalizeError 错误规范化 + setAuthCookies/clearAuthCookies）
```

**迁移前（单体，历史对照）**：

```
用户请求
  -> proxy.ts（安全头/限流/requestId）
  -> Next.js Route Handler
  -> requireAuth/requirePermission
  -> Service（业务规则）
  -> DbEngine / getDb()（ADR-009 收官：多数模块经 Repository，少量 auth 子模块仍直连 getDb()）
  -> SQLite（WAL）
  -> 响应（结构化日志 + requestId）
事件分支：
  Service -> appBus.emit -> Notification listener -> DB
```

---

## 四、健壮函数（Resilience）清单

> ⚠️ 以下函数位置多为**迁移前单体遗留代码**，运行时不被 BFF API 路由引用（BFF 薄转发到后端，由后端承载业务逻辑）。保留此清单作为历史审计证据，新增韧性逻辑应在后端实现。

| 函数 | 位置 | 防护 | 运行时状态 |
|------|------|------|:---:|
| `assertOwnership` | `modules/auth/server/permission.ts` | 对象级权限（IDOR） | ⚠️ 遗留 |
| `withTransaction` | `shared/db.ts` | 写操作原子性 | ⚠️ 遗留 |
| `rateLimit` | `shared/security/security.ts` | 接口防刷（BFF 自身用） | ✅ 运行时 |
| `sanitizeMarkdown` | `shared/utils/markdown.ts` | XSS 防护 | ⚠️ 遗留 |
| `requireModuleAdmin` | `modules/admin/server/require.ts` | 细粒度模块级守卫（UI 兜底） | ✅ 运行时 |

> ★ = BFF 运行时核心 · ⚠️ = 迁移前单体遗留，运行时不被 API 路由引用，待清理

---

## 五、BFF 交互风格约定

> ⚠️ 标注项为迁移前单体遗留机制，BFF 运行时不再使用。

- **页面导航**：Next.js Link / `useRouter`
- **API 调用（BFF → 后端）**：`shared/backend-client.ts` 统一代理（注入 JWT、401 静默刷新、snake_case→camelCase 翻译）
- ~~**API 调用（前端 → BFF）**：`fetch` + 统一错误拦截（`src/lib/api-client.ts`）~~ ⚠️ 遗留路径，已不存在
- ~~**事件通知**：`appBus.emit/on`（进程内）~~ ⚠️ 遗留事件总线，业务通知由后端承载
- **跨服务（未来）**：REST + JSON

---

> 本文档为活文档（L0 SSOT）。原 0.9.1 演变分卷对应章节（Part A 索引章节）已改为指向本文档的指针；其完整内容仅保留迁移叙事（Part B）作为历史痕迹。
