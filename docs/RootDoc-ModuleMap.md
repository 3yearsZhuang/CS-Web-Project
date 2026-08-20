# RootDoc-ModuleMap｜三端模块命名与契约映射表

> 更新人：3yearsZ
> 更新日：2026-08-21
> 版本：1.0.0
> Diátaxis：R（Reference · 三端业务模块命名与 API 契约的唯一权威映射表）
> 适用读者：前端 / 后端 / 移动端开发者、架构师、CI 维护者
> 变更触发：新增业务模块、API 契约变更、目录结构调整

> **SSOT 声明**：本文档是「三端（前端 / 后端 / 移动端）业务模块命名与 API 资源名的对应关系」的唯一权威正文。配套规范细节见 [RootDoc-EngConv.md](RootDoc-EngConv.md) §3「三端业务模块命名」。

---

## 快速索引

| 章节 | 主题 | 概述 | 代码位置 |
|------|------|------|----------|
| **§1 命名规范原则** | 三端模块命名 = API 资源名 | 命名规则、目录落位、组件归属、依赖方向 | `src/modules/`、`src/app/api/`、`app/api/v1/` |
| **§2 三端模块映射表** | 资源名 → 三端目录全映射 | 16 个契约资源的前端 / BFF / 移动端 / 后端文件对应 | — |
| **§3 门禁** | 契约冻结 + 模块命名校验 | `make contract-check`、`make check-module-naming` 等门禁命令 | `scripts/check/` |
| **§4 违约点红线** | 禁止触碰的既有约定 | 前端改名红线、后端收包红线、services 命名红线 | — |
| **§5 变更记录** | 历史变更与里程碑 | D 方向 7 波次收口详情 | — |

---

## §1 命名规范原则

### 1.1 核心规则

1. **三端业务模块名 = API 资源名**：取自 `openapi.baseline.json` 中 `/api/v1` 路径第一段（复数）。URL 契约冻结（179 路由，`contract-check` 门禁）是唯一无争议锚点。
2. **落位规则**：
   - 前端 / 移动端：`src/modules/<资源>/`
   - 后端：`app/api/v1/<资源>.py`（tools 子域收 `app/api/v1/tools/` 包）
3. **组件归属**：业务组件 / hook 一律进所属模块（`ui/` + `ui/hooks/`）。公共层 `components/` 只留跨 ≥2 域复用件。
4. **依赖方向**：禁止公共层依赖业务层（数据经业务域容器注入，见 `announcement-banner-client` 范例）。
5. **新增业务模块流程**：先入契约（`make contract-baseline`）→ 三端目录同名 → `check-module-naming` 校验通过 → 本表登记。

### 1.2 不变量约束（RFC 2119）

- **MUST** 三端业务模块名与 API 资源名保持一致（复数形式）
- **MUST NOT** 公共层 `components/` 依赖业务层 `src/modules/*`
- **MUST NOT** 后端 `api/v1/` 平铺文件未经授权收包
- **MUST** 新增业务组件 / hook 归入所属模块的 `ui/` 子目录
- **SHOULD** 跨 ≥2 域复用的组件提升至公共层前评审

---

## §2 三端模块映射表

### 2.1 完整映射

| 契约资源 | 前端 `src/modules/` | 前端 BFF / 页面 | 移动端 `src/modules/` | 后端 `app/api/v1/` | 备注 |
|---|---|---|---|---|---|
| `admin` | `admin` | `app/admin` + `app/api/admin` | —（规划） | `admin_users/roles/events/community.py` + `password_resets.py` | 后端 4 文件 + password_resets 映射资源 `admin` |
| `announcements` | `announcements` | `app/api/announcements` | —（规划） | `announcements.py` | 公告横幅容器见 `announcement-banner-client` |
| `audit` | — | admin 面板（BFF `app/api/admin` 内） | —（规划） | `audit.py` | 无独立前端模块，管理员面板消费 |
| `auth` | `auth` | `app/api/auth` + `app/login` | `auth` | `auth.py` | 2FA / 登录域 |
| `auxilio` | — | —（学习助手对话入口在页面内） | —（规划） | `auxilio.py` | 学习助手独立域 |
| `avatars` | — | `app/api/avatars` | — | `profile.py` 子路由 | 子资源，挂 profile 域（无独立文件） |
| `community` | `community` | `app/community` + `app/api/community` | —（规划） | `community.py` + `admin_community.py` | — |
| `events` | `events` | `app/events` + `app/api/events` | —（规划） | `events.py` + `admin_events.py` | — |
| `exceptions` | — | — | — | `exceptions.py` + `dev_exceptions.py`(DEBUG) | 基础设施，无前端模块 |
| `feature-visibility` | — | `app/api/feature-visibility` | — | `tools/feature_visibility.py` | 功能开关，无独立模块（挂 tools 包） |
| `join` | `join` | `app/api/join` | —（规划） | `join.py` | — |
| `notifications` | `notifications` | `app/notifications` + `app/api/notifications` | —（规划） | `notifications.py` | — |
| `profile` | `profile` | `app/profile` + `app/api/profile` | `profile` | `profile.py` | 含 avatars 子路由 |
| `rbac` | —（admin 面板内） | `app/api/admin` | —（规划） | `rbac/` 包 | 权限管理，无独立前端模块 |
| `tools` | `tools` | `app/tools` + `app/api/tools` | —（规划） | `tools/` 包（exam / resource / task / points / component_registry / feature_visibility） | 后端子资源收包 |
| `users` | `users` | `app/users` + `app/api/users` | —（规划） | `users.py` | — |
| `workbench` | `workbench` | `app/api/workbench` | —（规划） | `workbench.py` | — |

> 「—（规划）」：移动端尚未建该域（MVP 仅 auth / profile），按上表目录名直接建即可，无迁移成本。

### 2.2 代码位置索引

| 端 | 目录 | 示例 |
|---|---|---|
| **前端** | `CS-Web-Frontend/src/modules/<资源>/` | `src/modules/auth/`、`src/modules/community/` |
| **前端 BFF** | `CS-Web-Frontend/src/app/api/<资源>/route.ts` | `src/app/api/auth/route.ts`、`src/app/api/community/route.ts` |
| **移动端** | `CS-Mobile/src/modules/<资源>/` | `src/modules/auth/`、`src/modules/profile/` |
| **后端路由** | `CS-Web-Backend/app/api/v1/<资源>.py` | `app/api/v1/auth.py`、`app/api/v1/profile.py` |
| **后端服务** | `CS-Web-Backend/app/services/<资源>/` | `app/services/auth/`、`app/services/community/` |
| **后端仓库** | `CS-Web-Backend/app/repositories/<资源>/` | `app/repositories/user/`、`app/repositories/event/` |

---

## §3 门禁

### 3.1 门禁命令与约束

| 门禁 | 命令 | 约束 | 频率 |
|---|---|---|---|
| 契约冻结 | `make contract-check` | `/api/v1` 契约与 `openapi.baseline.json` 零漂移（179 路由） | 每次 PR |
| 模块命名 | `make check-module-naming` | 前端 / 移动端 `src/modules/` + 后端 `app/api/v1/` 模块名 ⊆ 契约资源名 | 每次 PR |
| 前端 | `pnpm run ts-check` + `pnpm test -- --run` | 10 基线错误零新增；vitest 全绿 | 每次 PR |
| 移动端 | `vue-tsc --noEmit` | 零错误 | 每次 PR |
| 后端 | compileall + venv import 链 + pytest（子仓 CI） | import 链全通；pytest 需 docker PG/Redis | 每次 PR |

### 3.2 新增模块自检清单

- [ ] 已在 `openapi.baseline.json` 中注册对应资源路由
- [ ] 三端目录已按资源名创建（前端 / 移动端 `src/modules/<资源>/`，后端 `app/api/v1/<资源>.py`）
- [ ] 组件 / hook 已归入所属模块 `ui/` 子目录
- [ ] `make check-module-naming` 通过
- [ ] 门禁全量通过（契约 + ts-check + 测试）
- [ ] 本文档映射表已更新

---

## §4 违约点红线

| 约定 | 位置 | 违约行为 | 授权状态 |
|---|---|---|---|
| 前端禁止改名 / 新建模块目录 | `docs/RootDoc-FEArch.md` §6.3 | `modules/` 目录改名、新建业务域目录 | ❌ 禁止 |
| 后端 api/v1 每资源一文件 | `CS-Web-Backend/AGENTS.md` | api/v1 平铺文件收包（tools 已授权收包，新增收包须再授权） | ⚠️ 需审批 |
| 后端 services `<x>_service.py` 命名 | `CS-Web-Backend/AGENTS.md` | services 收域包（auth / community / event / user / rbac 已授权，新增须再授权） | ⚠️ 需审批 |
| 移动端 M1–M6 用例域 | `CS-Mobile/tools/docs/arch/系统设计.md` | 已弃用（2026-08-19），代码以资源域为准 | ❌ 禁止（已弃用） |

### 4.1 不变量约束（RFC 2119）

- **MUST NOT** 未经审批将后端 `api/v1/` 平铺文件收包为目录
- **MUST NOT** 未经审批将后端 services 从 `<x>_service.py` 收包为域包
- **MUST NOT** 在前端 `modules/` 下创建未在 API 契约中注册的资源目录
- **MUST NOT** 在移动端使用已弃用的 M1–M6 用例域命名
- **MUST** 触碰既有约定前暂停并获得用户授权

---

## §5 变更记录

- **2026-08-21 v1.0.0**：P4-3 重写，补充 6 行元数据、快速索引、RFC 2119 约束、代码位置索引、自检清单
- **2026-08-19 建立**：D 方向 7 波次收口——① 前端 hooks 归位 `ui/hooks/`（15 个）+ 模块复数改名（`user→users` 等 3 个）+ profile 域归位 + app/ 散落业务组件归位（20 文件）；② 后端 services 5 域包化（16 文件）+ `api/v1/tools/` 收包（6 文件，契约零漂移）；③ 移动端资源域骨架（`modules/{auth,profile}` + `shared/`，弃用 M1–M6）；④ 门禁 `check-module-naming` 接入根 CI；⑤ 遗留项：公告横幅跨层依赖根治（A2：归位 + 注入式容器）、services 单数命名保留（B1 有意为之）

---

> ↩ **返回根级文档地图**：[README.md](README.md) · **跨仓工程约定**：[RootDoc-EngConv.md](RootDoc-EngConv.md) · **变更记录**：[CHANGELOG.md](CHANGELOG.md)