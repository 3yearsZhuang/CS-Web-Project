# 功能模块可见性管理（Feature Module Visibility）— 设计规划

> 版本：草案 v1（2026-08-07）
> 状态：规划阶段（待评审，未落地代码）
> 范围：CS-Web-Backend + CS-Web-Frontend（monorepo 两个 submodule）
> 目标：root 管理员可在后台管理"功能模块是否对哪类用户展示"，并对每次修改执行**弹窗二次确认 + 2FA 验证**，复用现有代码逻辑，仅对源代码做最小必要改动。

---

## 0. 背景与现状（已通过代码探索核实）

| 维度 | 现状 | 结论 |
|---|---|---|
| 功能模块/菜单 | 前端**硬编码配置数组**（`navbar.tsx` 的 `NAV_LINKS`、各页面 `AdminTab`），后端**无** menu/nav 概念 | 可见性规则需新增后端数据源，前端改为从后端拉取 |
| 可见性过滤维度 | 前端仅两层：`requireAuth`（是否登录）+ `user.role`（admin/root）明文比较 | 需扩展为"未登录 / 已登录 / 管理员"三态规则 |
| 2FA | 后端 `TOTPService.verify(user_id, code)` 完整可用；前端 `useTwoFA` + BFF `/api/auth/2fa/verify` 完整 | **直接复用**，无需新写算法 |
| 二次确认弹窗 | 前端全局 `ConfirmProvider` + `useConfirm()`（danger/warning/info 变体）已就绪 | **直接复用** |
| 审计日志 | 后端 `POST /api/v1/audit/logs`（操作者身份服务端推导、防伪造）+ 前端 BFF `/api/admin/actions/*` | **直接复用**为修改留痕 |
| 站点设置存储 | 后端已有通用 `Setting` 模型（`module`+`key`→JSON `value`） | **直接复用**存储可见性配置 |
| 权限闸门 | BFF `requireRoot(req)` / 后端 `is_superuser` | 配置接口挂 root 守卫 |

**核心结论**：本功能所有"安全/交互/存储"底座均已存在，规划重点是**薄增量层 + 数据流打通**，不重写任何核心逻辑。

---

## 1. 数据模型设计（复用 `Setting`，零新表）

新增一条设置记录（存于现有 `settings` 表，无需 Alembic 迁移新表）：

```
module = "feature_visibility"
key    = "<功能模块标识，如 tools / community / events / about>"
value  = JSON: {
  "guest":     true/false,   // 未登录是否可见
  "member":    true/false,   // 已登录（普通用户）是否可见
  "admin":     true/false    // 管理员（admin/root）是否可见
}
```

- 全站所有受管模块的配置聚合在 `key` 维度；亦可改用单条 `key="all"` 存整个映射对象，二选一（推荐**按模块多行**，便于缓存与单点更新）。
- 读取走后端已存在的 `Setting` 仓储/服务（确认 `app/services` 是否有 `SettingService`；若无，新增一个轻量读取函数复用 `Setting` 模型与 `get_db`）。

---

## 2. 后端改动（CS-Web-Backend）

### 2.1 新增 Schema — `app/schemas/feature_visibility.py`
- `VisibilityRule`（guest/member/admin 三布尔）
- `ModuleVisibility`（module_key + VisibilityRule）
- `FeatureVisibilityConfig`（list[ModuleVisibility]）—— 列表响应
- `UpdateVisibilityRequest`（module_key + VisibilityRule）

### 2.2 新增路由 — `app/api/v1/admin/feature_visibility.py`
挂在 `/api/v1/admin` 下（与现有 admin 路由一致），全部依赖 `require_root`：

| 方法 | 路径 | 说明 | 守卫 |
|---|---|---|---|
| GET | `/admin/feature-visibility` | 拉取全部模块可见性 | `require_root`（is_superuser） |
| PUT | `/admin/feature-visibility/{module_key}` | 更新单模块可见性 | `require_root` + **2FA 校验** |

> 注意：PUT 接口内部**复用 `TOTPService.verify_or_raise(current_user.id, totp_code)`**（来自 `app/services/totp_service.py`）校验 2FA；请求体含 `totp_code` 字段。**强制 2FA（决策 B）**：落库前先检查 `current_user` 的 2FA 启用状态（读 `TwoFactorAuth.enabled`），未启用即抛 `TWO_FACTOR_NOT_SETUP` 拒绝修改，不允许"未启用直接放行"绕过。

### 2.3 2FA 校验接入（复用）
在 PUT handler 中注入 `TOTPService`，于落库前调用 `await totp_service.verify_or_raise(current_user.id, body.totp_code)`。验证失败抛 `TOTP_INVALID`，前端弹错。

### 2.4 审计留痕（复用）
更新成功后**调用 `AuditService.record`**（或 `POST /api/v1/audit/logs`）记录一条：
- `action = "feature_visibility.update"`
- `resource_type = "feature_module"`，`resource_id = module_key`
- `actor` 由服务端从 `current_user` 推导（不信任客户端）
- 详情含新旧规则

### 2.5 注册路由
在 `app/api/v1/__init__.py` 或 `app/main.py` 的 admin 路由聚合处 `include` 新路由，保持与 `admin/users`、`admin/roles` 一致的前缀风格。

---

## 3. 前端改动（CS-Web-Frontend）

### 3.1 BFF 路由 — `src/app/api/admin/feature-visibility/route.ts`（及 `[moduleKey]/route.ts`）
- 服务端 Route Handler，复用 `backend-client.ts` 转发到 `/api/v1/admin/feature-visibility*`
- 挂 `requireRoot(req)` 守卫（来自 `src/shared/security/guards.ts`）
- camelCase ↔ snake_case 翻译沿用现有 `backend-client` 逻辑

### 3.2 可见性 Hook — `src/modules/admin/.../use-feature-visibility.ts`
- `fetchConfig()`：GET 拉取全部模块规则（SWR）
- `updateModule(key, rule, totpCode)`：PUT 提交（含 2FA 码）

### 3.3 管理 UI — 新增 `src/modules/admin/ui/feature-visibility-panel.tsx`
在 `/admin` 页新增一个 Tab（与现有 `roles/users/logs` Tab 平级），展示模块列表 + 三态开关（guest/member/admin）。保存流程：
1. 用户点击"保存" → 调 `useConfirm()` 弹**二次确认弹窗**（复用 `confirm-dialog.tsx`）显示"将把 X 模块对 Y 类用户 显示/隐藏，此操作影响全站，确认？"
2. 确认后 → 弹出 **2FA 输入**（复用现有 `two-factor-form.tsx` / `useTwoFA` 的验证码输入 UI，仅取 `verify` 调用）
3. 2FA 通过 → 调 `updateModule` 提交 → 成功 Toast + `mutate` 刷新

### 3.4 前端导航渲染改造（核心数据源切换）
改造 `src/components/layout/navbar.tsx` 与 `user-menu.tsx`（管理员入口）：
- 原 `NAV_LINKS` 的硬编码 `requireAuth` 改为从可见性配置计算：
  - `guest` 控制未登录可见；`member` 控制已登录可见；`admin` 控制管理员可见
  - 示例：`/tools` 的规则 `{guest:false, member:true, admin:true}` 等价于原 `requireAuth:true`
- 通过 SWR 拉取的 `FeatureVisibilityConfig` 做过滤；配置未加载时**降级为原硬编码行为**（保证可用性，fail-open 安全边界见 §5）
- `user-menu.tsx` 的 `/admin` 入口显隐也改为读 `feature_visibility` 中 `admin` 模块规则（不再纯靠 `role` 明文）

---

## 4. 受管模块清单（初版，含 admin 入口 · 决策 C）
初版纳入导航级模块：`about` / `events` / `community` / `tools` / `admin`（`admin` 入口本身可被隐藏，支撑"维护模式"场景）。后续可扩展至 `/profile`、`/join` 等。

---

## 5. 安全约束与边界
1. **root 专属**：配置读写均挂 `require_root`（后端 `is_superuser` + BFF `requireRoot` 双闸门）。
2. **2FA 强校验（决策 B）**：PUT 更新必须携带有效 TOTP，且 root **必须已启用 2FA**，否则拒绝（防"未启用直接放行"被绕过）。
3. **审计不可绕过**：所有变更经 `AuditService` 服务端落库，actor 身份服务端推导。
4. **前端降级策略**：可见性配置加载失败/网络异常时，前端**回退到原硬编码规则**（fail-open），避免整站导航消失；但真实权限闸门仍在 BFF/后端，前端隐藏不等于接口不可达（保持现有安全模型）。
5. **无新表迁移风险**：复用 `settings` 表，无需 Alembic 新迁移；但需在种子/初始化中保证默认可见性记录存在（否则首次读为空，触发降级）。

---

## 6. 落地步骤（建议顺序）
1. 后端 Schema + 路由 + 2FA/审计接入（§2），本地 `make dev-backend` 联调 Swagger。
2. 确认 `Setting` 读取服务/函数存在，补默认值种子。
3. 前端 BFF 路由 + Hook（§3.1–3.2）。
4. 前端管理面板 + 二次确认 + 2FA 输入（§3.3）。
5. 前端导航渲染改造（§3.4），SWR 拉取 + 降级逻辑。
6. 端到端验证：root 修改 → 二次确认弹窗 → 2FA 输入 → 全站导航即时变化 → 审计日志出现一条记录。
7. 更新 `openapi.baseline.json` 与 `docs/` 相关说明（若有接口契约基线）。

---

## 7. 决策点（已确认 · 2026-08-07）
- **A. 存储：按模块多行** ✅ —— `settings` 表每行一个 `module_key`，便于缓存与单点更新。
- **B. 2FA：强制要求** ✅ —— root 若未启用 2FA，PUT 更新接口直接拒绝（不允许"未启用直接放行"绕过）。
- **C. 受管范围：包含 `admin` 入口自身** ✅ —— 初版受管模块含 `about`/`events`/`community`/`tools`/`admin`（`admin` 入口可隐藏，支撑"维护模式"）。
- **D. 定时上下线：本期不做** ⏸ —— 留作后续迭代。

> 据此更新 §2.2 / §3.4 / §4 的约束：PUT 接口在 `verify_or_raise` 前显式检查 `current_user` 的 2FA 启用状态，未启用即抛 `TWO_FACTOR_NOT_SETUP`；§4 模块清单补入 `admin`。
