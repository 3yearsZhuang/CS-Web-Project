# 模块命名映射表（三端 ↔ API 契约）

> **唯一权威（SSOT）**：三端（前端 / 后端 / 移动端）业务模块命名与 API 契约的对应关系。
> 建立：2026-08-19（三端模块化规范化重构 P2-9，D 方向 7 波次收口后）。
> 配套门禁：`make check-module-naming`（`scripts/check/check_module_naming.py`）——三端模块名必须 ⊆ 契约资源名，已接入根 CI。
> 规范细节：`docs/RootDoc-EngConv.md`「三端业务模块命名」小节为索引，本表为唯一权威正文（避免双源漂移）。

---

## 一、命名规范原则

1. **三端业务模块名 = API 资源名**：取自 `openapi.baseline.json` 中 `/api/v1` 路径第一段（**复数**）；URL 契约冻结（179 路由，`contract-check` 门禁）是唯一无争议锚点。
2. **落位**：前端/移动端 `src/modules/<资源>/`；后端 `app/api/v1/<资源>.py`（tools 子域收 `app/api/v1/tools/` 包）。
3. **组件归属**：业务组件 / hook 一律进所属模块（`ui/` + `ui/hooks/`）；公共层 `components/` 只留跨 ≥2 域复用件；**禁止公共层依赖业务层**（数据经业务域容器注入，见 `announcement-banner-client` 范例）。
4. **services 层**：后端业务逻辑落 `app/services/<域>/` 包（auth/community/event/user/rbac 已包化）或 `<x>_service.py`（既有约定，单数命名有意保留，见待办 P2-9）。
5. **新增业务模块流程**：先入契约（`make contract-baseline`）→ 三端目录同名 → `check-module-naming` 校验通过 → 本表登记。

---

## 二、三端模块映射表

| 契约资源 | 前端 `src/modules/` | 前端 BFF / 页面 | 移动端 `src/modules/` | 后端 `app/api/v1/` | 备注 |
|---|---|---|---|---|---|
| `admin` | `admin` | `app/admin` + `app/api/admin` | —（规划） | `admin_users/roles/events/community.py` + `password_resets.py` | 后端 4 文件 + password_resets 映射资源 `admin` |
| `announcements` | `announcements` | `app/api/announcements` | —（规划） | `announcements.py` | 公告横幅容器见 `announcement-banner-client` |
| `audit` | — | admin 面板（BFF `app/api/admin` 内） | —（规划） | `audit.py` | 无独立前端模块，管理员面板消费 |
| `auth` | `auth` | `app/api/auth` + `app/login` | `auth` | `auth.py` | 2FA/登录域 |
| `auxilio` | — | —（学习助手对话入口在页面内） | —（规划） | `auxilio.py` | 学习助手独立域 |
| `avatars` | — | `app/api/avatars` | — | `profile.py` 子路由 | 子资源，挂 profile 域（无独立文件） |
| `community` | `community` | `app/community` + `app/api/community` | —（规划） | `community.py` + `admin_community.py` | |
| `events` | `events` | `app/events` + `app/api/events` | —（规划） | `events.py` + `admin_events.py` | |
| `exceptions` | — | — | — | `exceptions.py` + `dev_exceptions.py`(DEBUG) | 基础设施，无前端模块 |
| `feature-visibility` | — | `app/api/feature-visibility` | — | `tools/feature_visibility.py` | 功能开关，无独立模块（挂 tools 包） |
| `join` | `join` | `app/api/join` | —（规划） | `join.py` | |
| `notifications` | `notifications` | `app/notifications` + `app/api/notifications` | —（规划） | `notifications.py` | |
| `profile` | `profile` | `app/profile` + `app/api/profile` | `profile` | `profile.py` | 含 avatars 子路由 |
| `rbac` | —（admin 面板内） | `app/api/admin` | —（规划） | `rbac/` 包 | 权限管理，无独立前端模块 |
| `tools` | `tools` | `app/tools` + `app/api/tools` | —（规划） | `tools/` 包（exam/resource/task/points/component_registry/feature_visibility） | 后端子资源收包 |
| `users` | `users` | `app/users` + `app/api/users` | —（规划） | `users.py` | |
| `workbench` | `workbench` | `app/api/workbench` | —（规划） | `workbench.py` | |

> 「—（规划）」：移动端尚未建该域（MVP 仅 auth/profile），按上表目录名直接建即可，无迁移成本。

---

## 三、门禁

| 门禁 | 命令 | 约束 |
|---|---|---|
| 契约冻结 | `make contract-check` | `/api/v1` 契约与 `openapi.baseline.json` 零漂移（179 路由） |
| 模块命名 | `make check-module-naming` | 前端/移动端 `src/modules/` + 后端 `app/api/v1/` 模块名 ⊆ 契约资源名 |
| 前端 | `pnpm run ts-check` + `pnpm test -- --run` | 10 基线错误零新增；vitest 全绿 |
| 移动端 | `vue-tsc --noEmit` | 零错误 |
| 后端 | compileall + venv import 链 + pytest（子仓 CI） | import 链全通；pytest 需 docker PG/Redis |

---

## 四、违约点红线（触碰既有约定须暂停并获用户授权）

| 约定 | 位置 | 违约行为 |
|---|---|---|
| 前端禁止改名/新建模块目录 | `docs/RootDoc-FEArch.md` §6.3 | `modules/` 目录改名、新建业务域目录 |
| 后端 api/v1 每资源一文件 | `CS-Web-Backend/AGENTS.md` | api/v1 平铺文件收包（tools 已授权收包，新增收包须再授权） |
| 后端 services `<x>_service.py` 命名 | `CS-Web-Backend/AGENTS.md` | services 收域包（auth/community/event/user/rbac 已授权，新增须再授权） |
| 移动端 M1–M6 用例域 | `CS-Mobile/tools/docs/arch/系统设计.md` | 已弃用（2026-08-19），代码以资源域为准 |

---

## 五、变更记录

- **2026-08-19 建立**：D 方向 7 波次收口——① 前端 hooks 归位 `ui/hooks/`（15 个）+ 模块复数改名（`user→users` 等 3 个）+ profile 域归位 + app/ 散落业务组件归位（20 文件）；② 后端 services 5 域包化（16 文件）+ `api/v1/tools/` 收包（6 文件，契约零漂移）；③ 移动端资源域骨架（`modules/{auth,profile}` + `shared/`，弃用 M1–M6）；④ 门禁 `check-module-naming` 接入根 CI；⑤ 遗留项：公告横幅跨层依赖根治（A2：归位 + 注入式容器）、services 单数命名保留（B1 有意为之）。
