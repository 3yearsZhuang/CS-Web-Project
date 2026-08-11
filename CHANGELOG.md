# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Security
- 修复管理员强制 2FA 在 HTTP 层**完全失效**的真实安全缺陷：原 `Depends(require_admin_2fa)` 误传**工厂函数本身**（而非 `require_admin_2fa()` 实例），FastAPI 将返回的 `Admin2FARequired` 实例当作依赖终值丢弃、门禁 `__call__` 从不执行；`admin_users` / `admin_roles` / `admin_events` / `admin_community` 四域 + `workbench /stats/api-usage` 此前裸奔或缺失 2FA 强制。5 处改为 `Depends(require_admin_2fa())`，与 `require_permission` 同构（根因经 `get_dependant` 内省确认）。
- 补齐 ER-26 深遗留：`requirements.txt` / `requirements.lock` / `requirements-dev.lock` 三处 cryptography 约束由 45.0.7 同步升至 **50.0.0**（此前仅 pyproject + uv.lock 升级，而 CI 实际用 `pip install -r requirements-dev.lock` 安装、pip_audit 审计这两个锁文件——CI 安装/审计路径此前仍是含 13 条 CVE-2026-* 的 45.0.7）。

### Added
- 新增 admin RBAC 路由 HTTP 层真实 DB 集成测试 `test_http_admin.py`（5 条，沙箱真实 PostgreSQL 全过）：4 个 admin 域权限接线无权限→403 / 授权→200，管理员 2FA 门禁 superuser 无 2FA→422、启用→200，及 `workbench /stats/api-usage` 同源缺陷回归（未鉴权→401）。
- 并发/竞态集成测试（ER-44）：新增 `tools/tests/integration/test_concurrency_integration.py`（8 测试，真实 Redis + PostgreSQL，`asyncio.gather` 并发压测）——限流 30 并发恰 5 放行（Lua ZSET 原子性）、黑名单同/异 jti 并发幂等与隔离、降级窗口并发内存兜底；refresh token 同 token 并发轮换 ×10 全部放行且同 family、revoke 与 refresh 并发竞争终态一致、revoke_all 后旧 token 按复用拒绝。

### Fixed
- 社区/活动/工具集 `tags` 过滤 JSONB 退化根因修复：列类型为 `JSON().with_variant(JSONB)` 时 `contains` 编译成字符串 `LIKE` 且实际调用抛 `invalid input syntax for type json`，统一改 `type_coerce(列, JSONB).contains([tag])` 走 `@>`；共 5 处同源（community_repo.py:113 / community.py:121 / event_repo.py:36 / tools_repo.py:40 / tools_repo.py:235）。
- 修复组件注册表 `POST /api/v1/tools/component-registry` 真实请求 500：路由误声明 `response_model=dict` 而 service 返回 `ComponentItemOut` 模型，移除 `response_model` 后恢复（tools.py:606）。
- 全量测试失败清零（2026-08-11，10 个全部定位修复）：`test_dependency_manifest` 抓出 ER-26 双源漂移（cryptography 约束三处同步 50.0.0，见 Security）；`test_maintenance_tasks` 修正 ER-27 提顶层后的 monkeypatch 目标（patch `retention.ExceptionService`）；`test_phase4_community` 适配 ER-22 异步落库（白盒 flush + refresh）；`test_rate_limit` ×2 修复 Redis 模式下 `ratelimit:*` 键跨运行残留（autouse fixture 固定内存限流）；`api/v1` 分页断言 ×4 补 `total_pages` 键；`test_queue_worker` 修 `_QUEUE_ENABLED` 模块常量 patch + arq 闭包 `Function.name`（`__qualname__` vs `__name__`）显式对齐。全量 432 passed / 0 failed。

### Added
- 集成测试体系加固（ER-02 / ER-11 收口，方案A 分层组合闭环）：新增 3 个 repo 层真实 DB 集成测试文件（`test_repositories_community.py` 8 / `test_repositories_events.py` 6 / `test_repositories_tools.py` 7）+ 3 个 HTTP 层真实 DB 测试文件（`test_http_community.py` / `test_http_events.py` / `test_http_tools.py`），共 24 测试在真实 PostgreSQL（`fff_test`）全量通过；运行范式 `uv run python -m pytest <file> -v -o addopts="" -p no:cov`。

### Changed
- Auxilio 学习助手数据访问收敛：`execute_tool` 直连 SQL 迁至新仓储 `app/repositories/auxilio_tool_repo.py`（`AuxilioToolRepository`），行为不变。
- `LLM_DAILY_BUDGET` 落地生效：每日每用户 token 预算拦截（单位：千 tokens/日，默认 200 = 20 万 tokens；0 = 不限制），达上限后停止调用模型并提示，防成本失控。
- 运维与发布部署护栏（P1 收口，ER-29/33/34/35/36/37/38/39/40）：`docker-compose.yml` 全服务补 `mem_limit`/`cpus` 与 `stop_grace_period`、`backend`/`worker`/`cs-website` healthcheck + `cs-website→backend` 就绪门控、`backend`/`worker` 挂 `logs` 卷持久化；后端 Dockerfile 改多 worker（`--workers`，exec 形式保优雅停机）；`REQUIRE_REDIS_FOR_SECURITY` 默认 `true`、`DB_AUTO_CREATE_DATABASE` 默认 `false`、`SECRET_KEY`/`TOTP_ENCRYPTION_KEY`/`AUTH_SESSION_SECRET` 加必填守卫；新增 `scripts/check_version_sync.py` + `make check-version` + e2e.yml 四源版本 CI 校验。
- 代码质量与架构（P1 收口，ER-22/24/25/26/27/30/32）：新建 `app/core/constants.py` 集中 12 个命名常量并替换 10 处散落魔法数字（ER-24）；浏览计数改 Redis 原子计数 + 异步批量落库，请求路径零 DB 写、view_count 变最终一致（ER-22）；发布与迁移解耦——compose 默认 `DB_AUTO_MIGRATE=false` + 独立一次性 `migrate` 服务（alembic upgrade head），backend/worker 依赖其完成后启动（ER-30）；循环依赖去味——`user_service`/`exception_retention` 惰性 import 提顶层（实测无真循环，保留合法 `get_session` 惰性）（ER-27）；前端 `yaml` 升级消除 CVE-2023-2251、后端 `cryptography` 升至 50.0.0 全清 13 条 CVE-2026-*（OSV 69 包审计）（ER-25/26）；`tools/docs/README.md` 索引树错乱修复（ER-32）。
- 覆盖率门禁（ER-45）：新增 `tools/scripts/diff_coverage.py`（仅标准库，coverage.xml + git diff 新增行 → app/** 新增行覆盖率 <80% 即 exit 1）；ci.yml checkout 加 `fetch-depth: 0` + PR 事件跑 diff 覆盖率门禁；`pytest.ini` addopts 移除全局 `--cov`（本地/单文件测试不再被 fail_under 拖累，CI 显式 `--cov` 保留）；`.coveragerc` `fail_under` 70→72。
- 前端消费者契约对齐（ER-47）：引入 `openapi-typescript`，从后端 `openapi.baseline.json` 生成 `src/shared/api/backend-api.d.ts`（提交入库，`pnpm gen:api-types` 幂等）；`backend-client.ts` 的 `BackendUser`/`BackendTokenPair` 及 7 个 `*Like` 接口全部改引用生成 schema，ts-check 编译期拦截前后端字段漂移（并据此修复 5 个 auth 路由的 TokenPair 透传与测试 mock 字段缺失）；ci.yml 加「API types drift gate」——baseline 变更未重生成类型即 CI 红。
- 测试基础设施加固（ER-43/ER-41）：集成测试消除固定 id=1 依赖——conftest 新增 `admin_user` fixture（显式创建超级用户返回 id），4 个集成测试文件 19 处硬编码 `1` 全替换、`integration_db_ready` 移除 id=1 幂等补（ER-43）；服务单测不再绕 `__init__`——4 个服务测试文件 9 处 `Service.__new__()` 全部改真实 `__init__(db=mock_db)`，无参 `_make` 重构为 pytest fixture（user/rbac），带参构造保持函数但内部改真实构造（ER-41）。

## [0.9.9]

### Security
- 社区 `tags` 过滤参数化，消除 SQL 注入气味（ER-01）；社区 IP 哈希密钥配置化 fail-fast（ER-17）。
- 修复 Auxilio 工具用量越权获取全站数据（ER-18）；`workbench /stats/api-usage` 改强制管理员 + 2FA；LLM 提示注入结构化隔离加固（ER-19）；RBAC 缓存失效改 fail-closed（ER-20）；后台高危面管理员强制启用 2FA。

### Fixed / Performance
- 社区帖子列表交互标记 N+1 批量预取（ER-16）；关注用户列表计数/关注态 N+1 批量预取（ER-21）。

### Changed / Governance
- OpenAPI 契约门禁修复（CI 比对路径）+ 基线重冻（ER-04）；生产 `LOG_PROFILE=prod`（ER-05）；`/metrics` Prometheus 端点（ER-06）；死链审计脚本入库 + CI 门禁（ER-09）；前端覆盖率门禁 + PR diff-coverage（ER-13）；E2E nightly 全栈（ER-14）；路由层直写收敛到 `WorkbenchService` / `AuxilioService`（CodeGov-B1）；BFF 安全边界 CI（AL-1）；根索引补登 `项目演变历史.md`（ER-31）；Node 版本统一到 22；`uv.lock` 重生成。

## [0.9.8]
### Added
- 工作台（Workbench）前端模块：个人待办、番茄钟播放器、GitHub 热力图、API 调用统计、考试倒计时、快捷便签、学习助手对话等 widget（注册表配置驱动）。
- Auxilio 学习助手：基于规则的技能 + 可选 LLM（OpenAI 兼容 / Anthropic 双协议流式），SSE 流式对话，会话持久化。
- 后端 `/api/v1/workbench/*` 与 `/api/v1/auxilio/*` 路由及对应服务（`contribution_service`、`auxilio_agent`、`llm_client`）、`api_usage` 统计中间件。
- 数据表：`contribution_cache`、`api_call_logs`、`conversations`、`chat_messages`、`focus_sessions`。
- 可选 LLM 配置（`LLM_PROVIDER` / `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`）。
