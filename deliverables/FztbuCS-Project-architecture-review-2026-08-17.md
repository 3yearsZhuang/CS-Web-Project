# FztbuCS-Project 软件架构全面评估报告

> **评估日期**：2026-08-17
> **评估对象**：CS-Web-Backend（FastAPI + SQLAlchemy 2.0 async + PostgreSQL）+ CS-Web-Frontend（Next.js 16 + React 19 + TypeScript）+ 根编排层（docker-compose）
> **评估方法**：源码静态审查（结构 / 规模 / 分层 / 依赖 / 缓存 / 查询 / 安全 / 测试）+ 文档交叉验证（docs/ 索引、项目待办事项、CHANGELOG）
> **结论速览**：整体架构成熟度高，**基础设施远优于业务实现**——缓存 / 事件 / 队列 / 异常 / 可观测性设施完备且设计考究（可降级、幂等、锁保护），但业务层存在**缓存利用率极低、上帝服务残留、前端数据获取分散、BFF 样板膨胀**四类主要问题。全部建议按「收益 × 成本」排出 P0/P1/P2 三级，详见文末路线图。

---

## 0. 架构总览

```text
浏览器 ──> 反向代理(可选) ──> cs-website (Next.js 16 BFF :2333)
                                    │ 141 个 route.ts 薄转发
                                    ▼
                              backend (FastAPI :8000/9000)
                              ├── api → service → repository → model（分层单向）
                              ├── core: cache/queue/events/rate_limit/exceptions/
                              │         lifecycle/loguru/otel（可降级、可插拔）
                              ├── RBAC（TTL 缓存 + 显式失效）
                              └── PostgreSQL（Alembic 22 个迁移）
                                      ▲
                        redis（缓存/限流/队列/计数，可降级内存）
                        worker（arq 队列，QUEUE_ENABLED）
                        otel-collector / migrate / backup（编排层）
```

**关键基线数据**：

| 指标 | 数值 | 备注 |
|---|---|---|
| 后端源码 | ~29,500 行 / 319 py 文件 | 约定单文件 ≤300 行 |
| 后端测试 | 102 个 py 文件，集成测试 432 passed | 覆盖率门禁 72%（branch） |
| 后端分层 | api → service → repository → model | 单向依赖 |
| 前端源码 | ~67,000 行 / 428 html + 375 ts/tsx | 约定单组件 ≤500 行 |
| 前端测试 | 20 个 test 文件 | 明显偏薄 |
| BFF 路由 | 141 个手写 route.ts | 纯转发 + 字段映射 |
| 缓存设施 | DegradableCache（Redis→内存降级 + 冷却半开） | 业务侧仅 2 处使用 |
| 事件总线 | 进程内 + 跨实例 arq 广播 | fire-and-forget，无重试/死信 |
| 契约管理 | openapi.baseline.json + openapi-typescript 生成类型 | CI 差异门禁 |

---

## 1. 模块划分与职责边界

### 1.1 现状（✅ 优点）

- **后端分层模型清晰且被严格执行**：api 只做参数校验与响应编排，业务在 service，SQL 在 repository，模型集中在 `app/models/`（29 个文件）。依赖方向单向，core 不依赖 queue（惰性 import，「删模块即净」）。
- **社区 God Module 已收口（ER-15）**：`community_service.py` 1088 行单类已按子域拆分（community_post / comment / interaction / feed 等），通知已事件化（Phase 1 完成），是模块治理的示范。
- **前端按业务域分模块**：`src/modules/` 下 10 个域（auth/admin/community/events/tools/workbench…），每个域内 ui/types 分离；共享原语收敛在 `src/components/primitives/`（button/input/dialog…，均带测试）。
- 基础设施模块高度内聚：cache / queue / events / rate_limit / exceptions / lifecycle 各自独立成包，接口小而稳定。

### 1.2 发现的问题（⚠️）

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| M1 | **上帝服务残留**：`user_service.py` 单类 844 行（约定 300），`auth_service.py` 775 行 | UserService 一个类混装普通用户 CRUD + 管理员 CRUD + 资料 + 头像 + 密码校验/冲突检测 | 单点修改风险高，测试构造复杂，新人理解成本高 |
| M2 | **repository 巨型文件**：`community_repo.py` 718 行含 7 个 Repository 类；`tools_repo.py` 621 行 | 7 类 / 文件 | 与 service 拆分的子域不对齐，耦合度高 |
| M3 | **路由文件超限**：`api/v1/community.py` 695 行 | 25 个端点 / 文件 | 超过约定，难 review |
| M4 | **repository 边界渗透**：service 层 28 处直接 `self.db.execute(...)` | `community_post.py:_enrich_posts` 直查 User/CommunityCategory；`user_service.py:500` 手写 DELETE SQL | 查询逻辑分散，repo 无法复用/替换，测试 mock 困难 |
| M5 | **前端职责重复**：admin 域 19 个组件大而全 | `admin-events-panel.tsx` 491 行 + `event-modals.tsx` 472 行，与 `modules/events/ui/month-calendar.tsx`（464 行）存在重复的日历/表单逻辑 | 同一业务两套实现，改一处漏一处 |
| M6 | **通知职责散落**：announcement 模块仅 1 个组件，公告横幅实现在 `components/feedback/announcement-banner.tsx` | 模块边界与实现位置不一致 | 找代码靠猜，模块地图失真 |

### 1.3 优化建议

| 建议 | 做法 | 预期收益 | 优先级 |
|---|---|---|---|
| M-A1 | 按 ER-15 社区拆分的成熟范式拆 `UserService`：`UserService`（普通 CRUD）+ `UserAdminService`（管理员操作）+ `ProfileService`（资料/头像）+ `PasswordService`（改密/重置） | 单类回归 ≤350 行；修改面隔离；并行开发；复用既有 Phase 0~4 安全启动经验（基线测试 → 抽纯函数 → 拆类 → CI 闸门） | **P1**（0.9.9 收口后） |
| M-A2 | `community_repo.py` 按子域拆 4~5 个文件（post/comment/interaction/follow/report+series） | 与已拆分的 service 对齐，repo 复用率上升 | P2 |
| M-A3 | 28 处 `db.execute` 下沉至对应 repository（`_enrich_posts` 改走 `user_repo.get_by_ids` 等） | repo 成为唯一查询入口；单元测试可 mock repo 而非 mock session | **P1** |
| M-A4 | 前端 events 域抽共享日历/表单组件（admin 与 events 共用） | 消除双实现，单点维护 | P2 |
| M-A5 | 公告横幅移入 `modules/announcement/` 或文档显式登记归属 | 模块地图与实际一致 | P3 |

---

## 2. 数据流与依赖关系

### 2.1 现状（✅ 优点）

- **事件驱动已落地**：`core/events.py` 进程内总线 + 跨实例 arq 广播（防回环），社区通知（mention/comment_reply/like/favorite/follow）已全部事件化，业务失败不误发、通知失败不阻塞业务——**解耦方向正确**。
- **RBAC 用 FastAPI 依赖组合**：`require_permission` 以 Depends 形式声明，天然参与依赖解析与缓存，比装饰器方案健壮。
- **前端纯 BFF 薄转发**：业务数据唯一 owner 是后端 PG，前端零本地业务库（B1 闭环），并有 `check-bff-boundary.mjs` 脚本防回退。
- 依赖方向整体单向（core ← queue / core ← services），惰性 import 打破循环依赖。

### 2.2 发现的问题（⚠️）

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| D1 | **事件总线 fire-and-forget 无可靠投递**：订阅者异常仅记日志，无重试 / 死信 / 持久化；事件无 payload schema（弱类型字典） | `events.py:emit` → `loop.create_task` 即返回；广播失败静默降级 | 通知类副作用丢失不可追踪；事件升级（加字段）无编译期保护 |
| D2 | **服务实例化无统一容器**：`EventService(db, audit=None)` 手工 new，AuditService 默认构造 | 各 service 构造签名不统一 | 测试需记住每个构造参数；跨服务协作靠手搓 |
| D3 | **BFF 141 个 route.ts 手写样板膨胀**：参数解析 / 错误归一化 / 字段映射（snake→camel）每路由重复 | `backend-client.ts` 594 行 + 141 个 route.ts；`toEventItem`/`toUserItem` 等映射散落 | 新增 1 个 API 要写 2~3 处代码；映射漂移（前后端契约双源） |
| D4 | **前端数据获取不统一**：40 个模块文件手写 `fetch + useState/useEffect`，SWR 仅 auth/feature-visibility 等 4 处使用 | `shared/hooks/` 无 use-request；`swr-provider.tsx` 存在但未普及 | loading/error/缓存失效逻辑每处重写；无请求去重与缓存一致性 |
| D5 | **前后端类型双源**：`modules/*/types/index.ts`（如 tools 501 行）手工定义，与 `backend-api.d.ts`（openapi 生成 12,387 行）并存 | 手工类型可绕开契约 | 后端改字段，前端类型可能静默漂移 |

### 2.3 优化建议

| 建议 | 做法 | 预期收益 | 优先级 |
|---|---|---|---|
| D-A1 | 事件 payload 用 `TypedDict` 定义 + 订阅侧校验；通知类事件经 arq 任务投递（自带 retry），消费失败进死信/告警 | 事件升级有编译期保护；副作用可追踪可重试 | **P1** |
| D-A2 | 约定 service 构造统一（`*Service(db)` 仅依赖 session + 显式传入协作者），或轻量引入容器（如 `factory` 模块） | 测试构造统一，协作清晰 | P2（先文档化约定） |
| D-A3 | **BFF 样板生成**：以 openapi.baseline.json 为源生成 route.ts 骨架（路径 + 转发 + 错误归一化），开发只补字段映射；或将通用映射收进 `backend-client.ts` 的 `mapTo` 助手 | 新增 API 只需声明式配置；消除 1000+ 行重复 | **P1** |
| D-A4 | 封装 `useApiRequest`（基于 SWR 或轻量自研：loading/error/去重/mutate），将 40 处手写 fetch 收敛 | 数据获取一致；缓存命中与失效统一；减少重复状态代码 | **P1** |
| D-A5 | 业务类型从 `backend-api.d.ts` 派生（Pick/Omit 组合），逐步删除 `modules/*/types` 手工重复定义 | 契约单一来源，编译期发现漂移 | P1/P2 渐进 |

---

## 3. 性能瓶颈

### 3.1 现状（✅ 优点，后端基础设施优秀）

- **写放大治理典范**：`view_count.py` 用 Redis 原子 `incr` 计数 + 窗口去重 + `getset(0)` 周期批量落库，请求路径零 DB 写，且失败不丢计数（增量滞留 Redis）。
- **RBAC 权限缓存**：TTL + grant/revoke 显式失效 + 批量 `delete_many`（几千用户一次往返），revoke 路径失效失败即中止（拒绝服务优于残留权限）。
- **无 N+1**：`_enrich_posts` 用 `IN` 批量预取 author/category/interaction，一次往返。
- **中间件用纯 ASGI 而非 BaseHTTPMiddleware**：避免每请求 anyio task group 开销（5 层中间件场景下显著）。
- 连接池容量启动校验（worker×pool vs max_connections）、GIN 全文检索、bcrypt 在线程池执行、索引设计有注释说明（主键不重复加索引）——细节打磨到位。

### 3.2 发现的问题（⚠️）

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| P1 | **缓存设施完备但业务几乎未用**：`@cached` 装饰器业务零使用；`get_cache()` 仅 view_count 计数与 RBAC 权限 2 处 | 公告列表/分类列表/活动列表/设置项/积分排行榜/公开资料/统计等读接口每次穿透 DB | 高读流量下 DB 是最大瓶颈；设施投入被浪费 |
| P2 | **工作台聚合可能串行**：GitHub 贡献（外网请求）+ API 统计 + 番茄钟 + LLM 用量多个数据源 | `workbench.py` 421 行聚合端点 | 外网延迟叠加拖慢整页 |
| P3 | **事件通知 1 事件 1 DB 写**：通知事件化后每事件独立 session 落库，无批量/节流 | `notification_events.py` 订阅者 | 高频互动场景下通知表写放大 |
| P4 | **前端 i18n 大文件全量打包**：`messages/admin.ts` 1666 行、`tools.ts` 1384 行 | 客户端 bundle 含全量翻译 | 首屏 JS 体积增加；CJK 字体仍外链 Google Fonts @import（已评估保留，1.x 优化项） |
| P5 | **auxilio 会话消息全量加载**：无分页证据 | `GET /auxilio/conversations/{id}/messages` | 长会话响应体膨胀 |

### 3.3 优化建议

| 建议 | 做法 | 预期收益 | 优先级 |
|---|---|---|---|
| P-A1 | **热点读接口加缓存**（设施已就绪，改动最小）：公告列表（TTL 60s + 写后 delete）、分类列表、活动列表（按 month/status key）、`EventService.get_settings`、积分排行榜（TTL 30s） | 列表类接口 DB 命中率大幅下降；改动集中在 service 层 + 写点失效，风险低 | **P0** |
| P-A2 | 工作台并行化（`asyncio.gather`）+ 结果 TTL 缓存（如 5min） | 外网延迟不叠加；重复访问零回源 | **P1** |
| P-A3 | 通知落库批量（累积 100ms 窗口合并 insert）或降频 | 通知表写入量降一个量级 | P2 |
| P-A4 | i18n 按语言/按页面动态导入（next-intl 支持）；定期 bundle 分析（`@next/bundle-analyzer`） | 首屏 JS 减少 | **P1** |
| P-A5 | auxilio 消息接口分页（page/page_size） | 长会话响应稳定 | P2 |

---

## 4. 可扩展性与可维护性

### 4.1 现状（✅ 优点）

- **生命周期注册表**：`@register_startup/shutdown(priority, critical)` 插件式扩展，新增后台任务零侵入 main.py；多 worker 用 advisory lock 串行化（建库/迁移/RBAC seed/GC 任务均锁保护）。
- **可降级组件**：缓存/限流/队列全部「Redis 不可用 → 内存/eager 兜底」，单实例零成本跑通，多实例按 env 渐进开启（MULTI_INSTANCE/QUEUE_ENABLED）。
- **契约与文档治理**：openapi.baseline.json 冻结 + CI 差异门禁；ADR 索引、SSOT 文档地图、CHANGELOG 版本锚点——扩展功能有明确的「改哪里、记哪里」路径。
- 工具链完备：ts-check / lint:build / vitest / playwright / BFF 边界检查 / diff 覆盖率门禁（80%）。

### 4.2 发现的问题（⚠️）

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| X1 | **行数/复杂度约定无工具强制**：约定 ≤300/500 行，实际多个文件 2~3 倍超限 | user_service 844 / auth_service 775 / community_repo 718 / backend-client 594 / admin-events-panel 491 | 约定靠人工 review，回归成本高 |
| X2 | **前端测试偏薄**：20 个测试文件 vs 后端 102；重点集中在 primitives 与 hooks | admin/community/tools 业务组件几乎无测试 | 重构（如 D-A4 收敛 fetch）风险无保护网 |
| X3 | **依赖文件多轨并存**：`uv.lock` / `requirements.lock` / `requirements-dev.lock` / `requirements.txt` / `requirements-dev.txt` / `requirements-queue.txt` 六份 | pyproject 声明 uv 为包管理 | 新增依赖要同步多处，易漂移 |
| X4 | **构建卫生**：仓库根残留 `.coverage.Mac.pid24284.*`（585KB） | 沙箱跑 pytest --cov 的产物 | 仓库体积膨胀；.gitignore 覆盖不全 |

### 4.3 优化建议

| 建议 | 做法 | 预期收益 | 优先级 |
|---|---|---|---|
| X-A1 | CI 加**行数门禁脚本**（如 `tools/scripts/check_file_size.py`：py≤300/组件≤500，白名单登记存量超限） | 约定从「口头」变「机器」，新增超限即 CI 红 | **P1** |
| X-A2 | 前端补关键路径测试：auth 流程、community 列表/详情、admin CRUD 冒烟（优先在 D-A4 重构前补） | 数据层重构有回归保护 | **P1** |
| X-A3 | 依赖文件收敛：以 `uv.lock` 为唯一源，删除/归档 requirements*.txt（保留 requirements-queue.txt 作为可选说明） | 依赖单一事实源，符合仓库既定 SSOT 原则 | P2 |
| X-A4 | 清理 `.coverage.*` 残留并补 .gitignore | 仓库干净 | P3 |

---

## 5. 安全性与错误处理

### 5.1 现状（✅ 优点，本维度整体优秀）

- **统一异常体系**：`BaseAppException` 树（认证/授权/冲突/校验/未找到…）+ `traceback_id` + 全局 handler + 异常落库（exception_log）+ 日志关联 request_id——错误处理范式教科书级。
- **认证纵深**：JWT 双 token（access 15min + refresh 7d）+ refresh 轮换 + 登出/改密即时黑名单失效；TOTP 2FA + 备份码 + 密钥加密存储（TOTP_ENCRYPTION_KEY）；邮箱验证码 + 密码重置审批流。
- **密码安全**：bcrypt（72 字节截断显式防护）+ 线程池执行（不阻塞事件循环）；密码历史防重用。
- **请求防护**：全局限流 + 认证接口独立限流（Redis 后端跨实例一致）+ body 大小限制 + CORS 白名单 + 安全头（CSP nonce / HSTS / X-Frame-Options: DENY / nosniff / Referrer-Policy / Permissions-Policy）。
- **审计与治理**：audit 审计日志、登录历史、数据保留策略、token GC、RBAC 撤权缓存即失效（revoke 失败拒绝服务）。

### 5.2 发现的问题（⚠️）

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| S1 | **AUTH_ENABLED=False 全局旁路**：生产误配则全部接口视为超级用户 | `dependencies.py:_auth_bypass_user` 注释「切勿用于生产」 | 防御性开关：非 dev 环境应启动即拒绝 |
| S2 | **CSP 生产可收紧**：`style-src 'unsafe-inline'`、`script-src 'unsafe-eval'` | next.config.ts 注释已说明 dev 需要 + F2 nonce 规划 | XSS 缓解强度可再提升（低风险，因无用户可控内联脚本） |
| S3 | **bcrypt rounds 隐式默认**：`bcrypt.gensalt()` 未显式指定 cost | security.py:63 | 建议显式常量 + 登录延迟回归测试（防成本被悄悄调低） |
| S4 | **事件通知失败无告警通道**：订阅者异常仅日志（与 D1 同源） | events.py `_safe_run` | 副作用静默丢失，SLA 不可观测 |

### 5.3 优化建议

| 建议 | 做法 | 预期收益 | 优先级 |
|---|---|---|---|
| S-A1 | 启动守卫：`AUTH_ENABLED=False` 且 `ENV != dev` 时 fail fast | 消除误配风险 | **P1** |
| S-A2 | 显式 `bcrypt.gensalt(rounds=BCRYPT_ROUNDS)` 常量 + 登录耗时阈值测试 | 密码哈希强度受控、可测 | P2 |
| S-A3 | 按 F2 规划推进 CSP nonce 全覆盖，移除 style 的 unsafe-inline | 安全头达生产级 | P2 |
| S-A4 | 事件失败计数暴露到 /metrics + 日志告警（与 D-A1 合并） | 副作用可观测 | **P1**（随 D-A1） |

---

## 6. 代码规范与项目结构

### 6.1 现状（✅ 优点）

- 后端 black / flake8 / mypy 门禁，前端 tsc / eslint 门禁，均进 CI；命名规范（组件 PascalCase / 文件 kebab-case / barrel index.ts）、`server-only` 边界（nodemailer/crypto/fs/pino 文件首行强制）执行严格。
- 版本号四源同步（pyproject / __init__.__version__ / package.json / uv.lock）有文档强制；`docs/README.md` 文档地图登记制防孤儿文档。
- 提交规范（conventional commits）+ PR 自检清单 + diff 覆盖率门禁，工程纪律在同规模项目里属上游水平。

### 6.2 发现的问题（⚠️）

| # | 问题 | 证据 | 影响 |
|---|---|---|---|
| C1 | 超限文件无机器约束（同 X1） | 见 M1/M2/M3 | 规范执行靠自觉 |
| C2 | 前端测试文件位置分散：`*.test.tsx` 与组件同目录 vs 集中 | vitest 配置 | 可维护性弱（次要） |
| C3 | `app/api/v1/__init__.py` 路由注册 30+ 行手工 include_router，tags 与文件散落 | 模块索引 | 新增路由容易漏 tag/prefix（次要） |

### 6.3 优化建议

| 建议 | 做法 | 预期收益 | 优先级 |
|---|---|---|---|
| C-A1 | 与 X-A1 合并：行数/圈复杂度进 CI（复用 pyproject 的 ruff/black 或独立脚本） | 规范机器化 | **P1** |
| C-A2 | 路由注册可改为「每模块自注册」约定（模块内 `router = APIRouter(prefix=..., tags=[...])`，中心只 include） | 新增路由一处改动 | P2 |

---

## 7. 优化路线图汇总

> 优先级 = 收益（性能/效率/维护性）× 成本（改动量/风险）综合排序。括号内为关联维度。

### P0 —— 立即可做（低风险高收益）

| # | 建议 | 收益 | 影响面 |
|---|---|---|---|
| P-A1 | 热点读接口加缓存（公告/分类/活动列表/设置/排行榜） | 列表接口 DB 命中率大幅提升，高读流量下 P95 显著改善 | 后端 service + 写点失效，改 5~8 个文件 |
| D-A4 / P-A2 | 前端统一数据获取层 + 工作台并行化 | 消除重复状态代码；外网延迟不叠加 | 前端，可渐进 |

### P1 —— 近期（0.9.9 收口后 / 1.0.0 前）

| # | 建议 | 收益 | 影响面 |
|---|---|---|---|
| M-A1 | 拆分 UserService / AuthService（复用 ER-15 范式） | 单类 ≤350 行，修改面隔离 | 后端重构 + 回归 |
| M-A3 | 28 处 service 直查下沉 repo | 分层纯度恢复，测试可 mock | 后端 |
| D-A1 / S-A4 | 事件 payload 化 + 重试/死信 + 失败指标 | 副作用可靠可观测 | 后端 core/events |
| D-A3 | BFF 路由样板生成 | 新增 API 成本 ↓70% | 前端工具链 |
| D-A5 | 前端类型单一来源 | 契约零漂移 | 前端 |
| X-A1 / C-A1 | 行数/圈复杂度 CI 门禁 | 规范机器化 | 工程基建 |
| X-A2 | 前端关键路径测试补强 | 重构保护网 | 前端 |
| S-A1 | AUTH_ENABLED 非 dev 启动守卫 | 消除误配风险 | 后端启动 |
| P-A4 | i18n 按需加载 + bundle 分析 | 首屏 JS 缩减 | 前端 |

### P2 —— 远期 / 按需

| # | 建议 | 收益 |
|---|---|---|
| M-A2 / M-A4 | community_repo 拆分、前端 events/admin 组件复用 | 维护性 |
| D-A2 | service 构造约定文档化 / 轻量容器 | 测试与协作 |
| P-A3 / P-A5 | 通知批量落库、auxilio 消息分页 | 性能 |
| S-A2 / S-A3 | bcrypt rounds 显式化、CSP nonce 全覆盖 | 安全 |
| X-A3 / X-A4 | 依赖文件收敛、构建残留清理 | 治理 |
| M-A5 / C-A2 | 模块归属登记、路由自注册 | 规范 |

---

## 8. 优化后的综合影响

**系统性能**：P0 缓存落地后，读多写少的列表/统计接口从「每次全表/分页查询」变为「TTL 内零回源」，DB 并发压力下降一个量级；工作台并行化消除外网延迟叠加；对 <200 用户的内网规模，缓存收益主要体现为**延迟稳定**（p50 抖动消失），对更大规模则是**DB 连接与 IO 的直接节省**。

**开发效率**：BFF 样板生成 + 前端统一数据层 + 类型单一来源三项，使「新增一个业务接口」从「写路由 + 写映射 + 写类型 + 写状态管理」4 处工作收敛为 1~2 处；UserService 拆分后多人并行开发同一用户域不再互相阻塞。估算常规新功能开发量减少 20~30%。

**可维护性**：CI 行数门禁 + 前端测试补强 + 事件可靠投递，把「靠自觉」的约束变成「机器拦截」，重构（如未来微服务拆分，ADR-ROADMAP-001 已预留评估）有回归保护网；事件/契约/文档三套 SSOT 机制已就位，本报告的优化建议可无缝纳入 `docs/项目待办事项.md` 的 P0/P1/P2 分级跟踪体系。

---

## 附：评估局限

- 本文基于静态源码审查，未跑基准测试；P-A1 的量化收益建议落地后用 `/metrics` 的 p50/p95 对比验证。
- 部分判断（如 auxilio 全量加载、工作台串行）来自代码形态推断，落地前需读对应端点实现确认。
- 前端 bundle 体积建议用 `@next/bundle-analyzer` 实测后决定 i18n 拆分优先级。
