# RootDoc-ADR：架构决策与系统演进（Explanation · 为什么我们选择了当前架构）

> 更新人：3yearsZ
> 更新日：2026-08-20
> 版本：1.0.1 · 七夕（Diátaxis E 类样板，统一解释类文档规范）
> Diátaxis：E（Explanation · 回答「为什么」，提供决策背景、动机与权衡；不包含可执行步骤）
> 适用读者：架构师 / 技术负责人 / 新加入的高级工程师；已了解项目基本架构
> 变更触发：重大架构决策发布 / 技术栈迁移完成 / 系统边界调整 / 韧性机制变更

> **SSOT 分工声明**：
> - 本文档是「**跨仓库架构决策记录（ADR）、演进背景、边界上下文**」的唯一权威（SSOT）。
> - 完整 ADR 决策历史索引 → 根 [CHANGELOG.md](CHANGELOG.md)（含 ADR-001 ~ ADR-019 的完整记录表）。
> - 当前架构视图（模块依赖、运行时序列、部署拓扑）→ 各子仓 `-01-Arch.md`（Arc42 架构总览）。
> - 模块契约详情 → `BackDoc-ModuleContracts.md`（Reference 类型，RFC2119 约束）。
> - 工程约定与红线 → `RootDoc-EngConv.md` / 各子仓 `-02-Sec` / `-03-Conv`。

> **治理红线**：禁止在 `CHANGELOG.md` 历史章节中复述本文档的核心内容；ADR 新决策 MUST 在本文档登记索引，同时在 `CHANGELOG.md` 写入完整决策记录。

---

## 1. 背景与动机：为什么需要这些架构决策

本项目（CS-Web / CS-Mobile）的架构演进经历了三个主要阶段，每个阶段都对应着明确的业务需求和技术约束：

| 阶段 | 时间跨度 | 核心目标 | 技术形态 |
|---|---|---|---|
| **Phase 1**：单体原型 | 0.6.x ~ 0.8.x | 快速验证 MVP 业务可行性 | Next.js Monolith + SQLite（WAL 模式） |
| **Phase 2**：模块化重构 | 0.9.0 ~ 0.9.1 | 解决单体耦合、支持多端扩展 | 模块化目录结构 + Drizzle ORM + Repository 抽象 |
| **Phase 3**：前后端分离 | 0.9.2 ~ 1.0.1 | 支撑多端（Web + MP + APK）+ 强化安全边界 | Next.js BFF（薄转发）+ FastAPI + PostgreSQL |

**当前（Phase 3）面临的核心技术挑战**：
1. 多端统一身份认证（Web Cookie + MP Token + APK Token 三态管理）
2. BFF 薄转发与后端厚业务的职责边界
3. 条件编译下的双端行为收敛
4. 从 SQLite 到 PostgreSQL 的数据迁移与一致性保证

本文档记录了应对这些挑战的关键架构决策、权衡分析和当前状态。

---

## 2. 决策时间线（ADR 索引与动机）

> 完整 ADR 决策记录（ADR-001 ~ ADR-019）见 [CHANGELOG.md](CHANGELOG.md)。下表为 SSOT 索引，聚焦当前 Phase 3 生效的关键决策。

### 2.1 Phase 1 决策（已收官，作为演进背景）

| ADR | 决策主题 | 决策结论 | 权衡分析 |
|---|---|---|---|
| **ADR-001** | 模块化目录结构 | 按业务域拆分 `modules/`，每域自包含 `server/types/ui` | 选型 A：按技术层拆分（传统 MVC）× 耦合严重<br>选型 B：按业务域拆分 ✓ 内聚高、易维护 |
| **ADR-002** | 数据库双引擎抽象 | Drizzle ORM + `DATABASE_DIALECT` 切换 SQLite/PG | 选型 A：原生 SQL × 方言锁定<br>选型 B：ORM 抽象 ✓ 迁移成本可控 |
| **ADR-005** | Repository 抽象层 | `getRepositories()` 屏蔽方言差异 | 选型 A：Service 直接操作 ORM × 业务逻辑耦合<br>选型 B：Repository 封装 ✓ 测试友好、方言可替换 |

### 2.2 Phase 2 决策（已收官，为 Phase 3 铺路）

| ADR | 决策主题 | 决策结论 | 权衡分析 |
|---|---|---|---|
| **ADR-009** | 前后端分离 + 全量迁移至 PG | 前端降级为 BFF（薄转发），后端承载全部业务/认证/邮件 | 选型 A：保留 Monolith + 新增移动端 API × 状态管理复杂、安全边界模糊<br>选型 B：BFF + 独立后端 ✓ 职责清晰、多端统一、安全强化 |
| **ADR-018** | 0.9.1 预发布就绪包 | 建立 SLO + Alerting + Load Test + Restore Drill + Runbook + Rollback + CI 加固 | 选型 A：仅做功能完成 × 生产风险高<br>选型 B：工程完备性 ✓ 可观测、可回滚、可恢复 |
| **ADR-019** | 前端重建适配 Community v2 | 2026-08-03 前端重建，适配新架构 | 选型 A：在旧前端上打补丁 × 技术债累积<br>选型 B：重建 ✓ 架构清晰、技术栈对齐 |

### 2.3 Phase 3 决策（当前生效，持续演进中）

| ADR | 决策主题 | 决策结论 | 权衡分析 |
|---|---|---|---|
| **ADR-020**（新增） | Diátaxis 文档分类体系 | 全部项目文档按 T/H/R/E 分类重写，消除混合类型 | 选型 A：保持现状 × 文档职责模糊、维护成本高<br>选型 B：严格分类 ✓ 读者预期一致、SSOT 权限清晰 |
| **ADR-021**（新增） | BFF 薄转发边界 | BFF 只做认证代理 + Zod 校验 + 错误翻译，不承载业务逻辑 | 选型 A：BFF 承载部分业务 × 职责边界模糊<br>选型 B：纯薄转发 ✓ 后端为唯一业务权威、多端一致 |
| **ADR-022**（新增） | Token 安全存储策略 | MP：沙箱存储；APK：EncryptedSharedPreferences；Web：HttpOnly Cookie | 选型 A：三端统一存储方案 × MP 无安全存储、APK 可 Root<br>选型 B：端差异化方案 ✓ 各端采用当前最安全方案 |

---

## 3. 边界上下文（Bounded Context）

### 3.1 当前架构（BFF 视角）

```
                 ┌─────────────────────────────────────┐
                 │        Next.js BFF（薄转发）          │
                 │  ┌──────────┐  ┌──────────────────┐  │
                 │  │  Auth    │  │  Community       │  │
                 │  │ (Cookie) │  │ (community/members)│
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

**关键边界说明**：
- **BFF → 后端**：仅通过 `backend-client.ts` 统一代理；**MUST NOT** 在 BFF 中直接访问数据库或写入业务逻辑。
- **后端 → BFF**：返回标准 JSON，`backend-client.ts` 负责 `snake_case → camelCase` 翻译。
- **前端组件 → BFF**：仅通过 Next.js Route Handler（`src/app/api/**/route.ts`）调用；**MUST NOT** 绕过 BFF 直连后端。

### 3.2 迁移前架构（历史对照，仅作演进参考）

```
                 ┌─────────────────────────────────────┐
                 │           Next.js Monolith           │
                 │  ┌──────────┐  ┌──────────────────┐  │
                 │  │  Auth    │  │  Community       │  │
                 │  │ (session)│  │ (community/members)│
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
                                 │   SQLite    │ (WAL 模式)
                                 └─────────────┘
```

**Phase 1 → Phase 2 → Phase 3 的核心差异**：

| 维度 | Phase 1（单体） | Phase 2（模块化） | Phase 3（前后端分离） |
|---|---|---|---|
| 数据库 | SQLite（单体直连） | SQLite + PG（Repository 抽象） | PostgreSQL（后端独占） |
| 认证 | Server-side Session | JWT + Server-side Session | JWT + HttpOnly Cookie（BFF 托管） |
| 业务逻辑 | Next.js Service 层 | Next.js Service 层（模块化） | FastAPI 后端（BFF 仅薄转发） |
| 部署 | 单容器 | 单容器 | BFF 容器 + 后端容器（独立伸缩） |
| 多端支持 | 仅 Web | Web + 预留 MP/APK | Web + MP + APK（统一后端 API） |

---

## 4. 数据流与韧性机制

### 4.1 当前数据流（BFF 视角）

```
用户请求
  → Next.js Route Handler（src/app/api/**/route.ts）
  → assertAllowedOrigin + Zod body 校验
  → proxyBackend（shared/backend-client.ts）
       ├── 注入 Authorization: Bearer <JWT>（从 HttpOnly Cookie）
       ├── 401 静默刷新（调用后端 /auth/refresh 轮换令牌）
       └── snake_case → camelCase 响应翻译
  → 后端 FastAPI（require_permission enforce + 业务逻辑 + PostgreSQL）
  → 响应（normalizeError 错误规范化 + setAuthCookies/clearAuthCookies）
```

**关键韧性机制**：

| 机制 | 实现位置 | 防护目标 | 当前状态 |
|---|---|---|---|
| `rateLimit` | BFF `shared/security/security.ts` | 接口防刷 | ✅ 运行时 |
| `requireModuleAdmin` | BFF `modules/admin/server/require.ts` | 细粒度模块级守卫（UI 兜底） | ✅ 运行时 |
| `assertOwnership` | 后端 `app/core/security.py` | 对象级权限（IDOR） | ✅ 运行时（已迁移至后端） |
| JWT 401 静默刷新 | BFF `backend-client.ts` | Token 过期无感刷新 | ✅ 运行时 |
| Origin 白名单校验 | BFF `shared/security/security.ts` | Login CSRF 防护 | ✅ 运行时 |

> **已移除的遗留机制**（Phase 1/2 单体时代遗留，BFF 运行时不再使用）：`withTransaction`、`sanitizeMarkdown`、`appBus.emit/on` 事件总线。这些功能在 Phase 3 中已由后端承载。

### 4.2 BFF 交互风格约定

| 交互类型 | 实现方式 | 约束 |
|---|---|---|
| 页面导航 | Next.js `Link` / `useRouter` | MUST 使用客户端路由，禁原生 `<a>` 直连 |
| BFF → 后端 API 调用 | `shared/backend-client.ts` 统一代理 | MUST 通过此入口，MUST NOT `fetch(后端地址)` |
| 前端 → BFF API 调用 | `fetch('/api/...')` + 统一错误拦截 | MUST 使用 `src/lib/api-client.ts` 封装 |
| 跨服务通信（预留） | REST + JSON | 当前无跨服务需求 |

---

## 5. 结论与展望

### 5.1 当前状态总结

| 维度 | 状态 | 说明 |
|---|---|---|
| **架构模式** | ✅ 已稳定 | BFF + FastAPI + PG 三层架构，职责边界清晰 |
| **多端支持** | ✅ MVP 就绪 | Web（BFF）+ MP（小程序直连后端）+ APK（Android 直连后端） |
| **安全边界** | ✅ 已强化 | JWT HttpOnly Cookie + Origin 白名单 + RBAC enforce 在后端 |
| **可观测性** | ✅ 已建立 | pino 结构化日志 + /api/health + SLO 基线（见各子仓 Ops 文档） |
| **文档体系** | 🔄 重构中 | P0-P4 文档规范重写，统一 Diátaxis 分类 + Arc42 架构模板 |

### 5.2 未来演进方向

| 方向 | 预期时间 | 说明 |
|---|---|---|
| **移动端独立 BFF** | 完整版 | 当 MP/APK 业务复杂度增长时，考虑为移动端引入独立 BFF 层（当前 MVP 直连后端） |
| **微服务拆分** | 完整版 | 当单 FastAPI 实例承载模块 > 10 个时，考虑拆分为 Auth / Community / Exam 等独立服务 |
| **事件驱动** | 完整版 | 引入消息队列（Redis Streams / RabbitMQ）替代当前的同步调用链，提升解耦与韧性 |
| **SSO/OAuth** | 完整版 | 微信登录 / Google 登录 / 企业 SSO 集成 |
| **国际化** | MVP 持续 | i18n 词条管理（见 `FrontDoc-03-Conv.md` §6） |

### 5.3 一句话总结

> **当前系统已完成从单体原型到前后端分离架构的关键转型，BFF 薄转发 + FastAPI 厚业务 + PostgreSQL 强一致性的三层架构为多端统一、安全强化和未来扩展奠定了坚实基础。**

---

> ↩ **返回根级文档地图**：[README.md](README.md) · **完整 ADR 历史**：[CHANGELOG.md](CHANGELOG.md) · **当前架构视图**：[FrontDoc-01-Arch.md](../CS-Web-Frontend/tools/docs/FrontDoc-01-Arch.md) · **后端架构**：[BackDoc-01-Arch.md](../CS-Web-Backend/tools/docs/BackDoc-01-Arch.md) · **移动端架构**：[MobileDoc-01-Arch.md](../CS-Mobile/tools/docs/MobileDoc-01-Arch.md) · **工程约定**：[RootDoc-EngConv.md](RootDoc-EngConv.md)
