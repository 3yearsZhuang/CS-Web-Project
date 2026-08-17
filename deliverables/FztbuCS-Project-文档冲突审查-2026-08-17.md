# FztbuCS-Project 文档冲突与过时项审查报告

> 生成日期：2026-08-17
> 审查范围：根仓 `docs/`（18 篇）、`CS-Web-Backend/tools/docs/`（7 篇）、`CS-Web-Frontend/tools/docs/`（8 篇）、根 `README.md` / `CHANGELOG.md`，以及 `.workbuddy/memory/` 项目记忆
> 方法：通读全部文档 × 对照真实代码/配置（版本四源、openapi.baseline.json、app/ 结构、docker-compose、Makefile、package.json、pyproject.toml）
> 定位：**分析交付物（非正式文档）**。如需落地修正，建议按 DocGovernance 登记进 `docs/项目待办事项.md`。

---

## 一、事实基准（已核实，作为判定标准）

| 项 | 真实值 | 核验来源 |
|---|---|---|
| 版本号四源 | **均为 0.9.9** | `CS-Web-Backend/pyproject.toml:3`、`app/__init__.py:5`、`CS-Web-Frontend/package.json:3`、`CS-Web-Backend/uv.lock` 根包 `cs-web-backend`（:435） |
| `openapi.baseline.json` 契约版本 | **0.9.9** | `openapi.baseline.json:4566` `info.version` |
| 社区 God Module 重构 | **已完成（2026-08-11）**，`community_service.py` 已删除 | `BackDoc-Refactor-CommunityService.md:53/70` + `app/services/` 实测无该文件 |
| 前端 CHANGELOG | 仅有 `[Unreleased]/[0.9.8]/[0.9.7]/[0.9.6]/[0.9.1]`，**缺 [0.9.9]** | `CS-Web-Frontend/CHANGELOG.md` |

> 注：`uv.lock` 根包真实名称是 **`cs-web-backend`**，不是项目记忆旧记载的 `fastapi-witchcat-framework`（见第九节）。

---

## 二、🛑 高严重度（当前版本事实被错写为 0.9.8）

### F-1 ｜`docs/项目待办事项.md` 事实表 F-11 称四源"均 0.9.8"
- **证据**：`:431` — `F-11｜版本四源：…当前均 0.9.8（已核验一致）`。
- **冲突**：同一文件 `:407` 记 `R1 版本漂移（四源 0.9.8 vs 文档 0.9.9）`；而真实四源均为 **0.9.9**。`F-11` 既与真实状态矛盾，也与该文件自身 R1 自相矛盾。
- **影响**：该文件是"未完成任务的唯一权威跟踪"，版本事实错误会误导发布/CI 判断。
- **建议**：F-11 改为"当前均 **0.9.9**（已核验一致）"。

### F-2 ｜`docs/RootDoc-Deploy.md` 断言 `__version__ = "0.9.8"`
- **证据**：`:5` — `对应版本：0.9.8（后端 … __version__ = "0.9.8"）`；同文档 `:4/:44/:53/:335` 均标 "0.9.8"。
- **真实值**：`app/__init__.py:5` → `__version__ = "0.9.9"`。
- **建议**：全文 0.9.8 → 0.9.9；页眉"最后更新/对应版本"同步；运行环境、Auxilio、信息缺口段标号一并更新。

### F-3 ｜根 `README.md` 自封"单一事实源"，却写"0.9.8 准备期"
- **证据**：`:5` — `当前真实进度（2026-08-08）：版本 0.9.8 → 1.0.0 准备期`；`:25` `以下能力在 0.9.8 中已具备`；`:104` `0.9.8 含工作台 / Auxilio`；且 `:9/:37/:80` 自陈"单一事实源，变动只改此处"。
- **真实值**：0.9.9 已于 2026-08-09 发布（CHANGELOG 有 `[0.9.9]` 段 `:39`）。
- **影响**：根 README 是新人第一入口，与其"单一事实源"定位直接冲突，传播面最广。
- **建议**：`:5` 改"**0.9.9（已发布）→ 1.0.0 准备期**"；`:25/:104` 的 0.9.8 改为 0.9.9 或"当前版本"。

---

## 三、🟡 中严重度

### F-4 ｜`docs/api-reference.md` 与 `docs/README.md` 误标冻结契约为 "0.9.8"
- **证据**：`api-reference.md:3` — `由 openapi.baseline.json（0.9.8 冻结契约）自动生成`；`docs/README.md:18` — `api-reference.md | API 参考（由 openapi.baseline.json 0.9.8 冻结契约自动生成…）`。
- **真实值**：`openapi.baseline.json` 的 `info.version = "0.9.9"`；且 `api-reference.md` **内容已含 0.9.9 路由**（`/api/v1/rbac/*`、`/api/v1/admin/*`、`/api/v1/tools/component-registry/*` 等），即**非内容缺失，仅为版本标签误标**。
- **影响**：误将已冻结基线标低一个版本，易让人误判"0.9.9 变更尚未冻结"，干扰契约门禁认知。
- **建议**：两处"0.9.8 冻结契约"→"0.9.9 冻结契约"；或直接 `make contract-baseline` 重新生成 api-reference 使其与 baseline 自洽。

### F-5 ｜`docs/Onboarding.md` 顶部进度仍写 0.9.8
- **证据**：`:10` — `截至 2026-08-07，项目处于 0.9.8 → 1.0.0 准备期`；`:189` `截至 0.9.8，该卡片尚未在 widget-registry.ts 的 WIDGETS 中注册`。
- **真实值**：当前 0.9.9。`:189` 的"卡片未注册"事实本身仍准（`widget-registry.ts` 确无 `api-usage-stats`），仅时间标注过时。
- **建议**：`:10` 改 0.9.9；`:189` 的"截至 0.9.8"改为"截至 0.9.9（仍待注册）"。

### F-8 ｜社区 service 重构——索引/页眉标"规划中"，正文+代码已"已完成"
- **证据（矛盾双方）**：
  - `CS-Web-Backend/tools/docs/README.md:89` — `BackDoc-Refactor-CommunityService.md | …**规划中，不阻塞 0.9.9/1.0.0**`
  - `BackDoc-Refactor-CommunityService.md:3` — `状态：规划中（safe-start）…不阻塞 0.9.9/1.0.0 收口`
  - 同文档 `:53` — `✅ 已完成（2026-08-11）：…community_service.py 删除…AL-2 五服务闭环`；`:70` — `community_service.py …✅ 已删除`
- **真实值**：代码已删除 `community_service.py`，五服务闭环（见基准表）。
- **建议**：该文档页眉状态改为"已完成（2026-08-11）"，并同步 `tools/docs/README.md:89` 描述（去掉"规划中/不阻塞"）。

---

## 四、🟢 低严重度

### F-6 ｜多份文档"最后更新 0.9.8"页眉未随 0.9.9 刷新
- **证据**：`BackDoc-01-Arch.md:4`、`BackDoc-02-Sec.md:7`、`BackDoc-Conv.md:4`、`BackDoc-Infra.md:4`、`RootDoc-Deploy.md:4`、`RootDoc-MigEval.md`（多处"0.9.8 补录/现状"）。
- **说明**：`RootDoc-MigEval.md` 的"0.9.8 补录"属可接受的历史快照注记；整体说明这些文档未覆盖 0.9.9 新增内容（社区拆分、admin 2FA 修复等）。
- **建议**：批量将页眉"最后更新"刷新至 0.9.9，并补一句"0.9.9 增量见 CHANGELOG"。

### F-7 ｜`docs/项目待办事项.md` 内部 R1 vs F-11 形成"版本漂移未闭环"观感
- **证据**：`:407` R1 记"四源 0.9.8 vs 文档 0.9.9"，但 `:431` F-11 仍写四源 0.9.8。
- **建议**：随 F-1 一并修正 F-11 即可消除（并确认 R1 留档措辞与现状一致）。

### F-9 ｜`BackDoc-Infra.md` 声称 Alembic "单一线性 head = d3e4f5a6b7c8" 需实测复核
- **证据**：`BackDoc-Infra.md:182` — `当前 Alembic 单一 head 为 d3e4f5a6b7c8（线性链、无分支）`，且 `:371` 表总数"[待填写]"。
- **风险点**：`36bbae24c38c_initial_schema.py` 未被任何迁移引用为 `down_revision`，疑似存在多 head / 断链风险；静态 grep 无法完全确认。
- **建议**：在目标库执行 `alembic heads` 核实是否单一线性 head；若为多 head 则合并/补链，并据实更新文档（含精确表数）。

### F-10 ｜`docs/Onboarding.md:189` "api-usage 卡片未注册"措辞过时
- 事实仍准（widget-registry 确无该卡片），仅"截至 0.9.8"在 0.9.9 下略过时。见 F-5 建议一并修订。

---

## 五、✅ 经核查一致、无需修正的项（避免重复劳动）

以下文档声明与真实代码/配置**一致**，本次未发现冲突：
- **技术栈与依赖**：FastAPI 0.139、SQLAlchemy 2.0 async、Next.js 16 + React 19、Node≥22/Python≥3.13、arq 0.28、OTel 1.42.1、redis 5.0.4、pyjwt 2.13 —— 与 `pyproject.toml` / `package.json` / `engines` 一致。
- **服务端口/路径/命令**：后端 9000、容器 8000、前端 2333、PG 5432、库 domefff —— 与 `Makefile` / `docker-compose.yml` / `RootDoc-Deploy.md` / `Onboarding.md` 一致。
- **运维端点**：`/health`、`/health/events`、`/health/security`、`/readyz`、`/metrics/json`、`/status` 均存在，与文档一致。
- **API 路由覆盖**：`api-reference.md` 所列 rbac / admin_* / component-registry / community / workbench / auxilio 等路径，与 `app/api/v1/` 实际路由对应一致。
- **架构拆分**：社区 service 子域拆分、配置文件 `config_parts/` 拆分、错误码业务自治 —— 与代码一致。
- **死链/孤儿文档**：遍历三套文档树与根 README 的全部相对链接/锚点，**未发现死链**（前端 `FrontDoc-PGMig→FrontDoc-Evo` 死链已于 2026-08-08 修复）。

---

## 六、文档体系外的相关提示（非文档冲突，供参考）

今日另两份交付物已覆盖，此处不展开，仅列关联：
- `deliverables/FztbuCS-Project-规范化建议-2026-08-17.md` 的 **N-11**（api-reference 0.9.8 vs baseline 0.9.9）即本报告 F-4；**N-02/N-03/N-06/N-08** 等为仓库卫生/流程问题，不在文档冲突范畴。
- `deliverables/FztbuCS-Project-architecture-review-2026-08-17.md` 为架构评估，与文档事实无冲突。

---

## 七、修复优先级清单（可立即执行）

| 顺序 | 项 | 文件 | 动作 |
|---|---|---|---|
| 1 | F-3 | `README.md` | `:5/:25/:104` 0.9.8 → 0.9.9 |
| 2 | F-2 | `docs/RootDoc-Deploy.md` | 全文 0.9.8 → 0.9.9（含页眉） |
| 3 | F-1 | `docs/项目待办事项.md` | F-11 四源"均 0.9.8"→"均 0.9.9"；核对 R1 留档 |
| 4 | F-4 | `docs/api-reference.md` + `docs/README.md:18` | "0.9.8 冻结契约"→"0.9.9 冻结契约"（或重生成） |
| 5 | F-5 | `docs/Onboarding.md` | `:10` 0.9.8→0.9.9；`:189` 时间标注更新 |
| 6 | F-8 | `BackDoc-Refactor-CommunityService.md` + `CS-Web-Backend/tools/docs/README.md:89` | 状态"规划中"→"已完成（2026-08-11）" |
| 7 | F-6 | 多份后端/部署文档页眉 | "最后更新"刷新至 0.9.9 |
| 8 | F-9 | `BackDoc-Infra.md` | `alembic heads` 实测后据实更新 head 与表数 |

> 前三项目（F-1/F-2/F-3）把当前版本事实错写为 0.9.8，且其中两处文件自诩为权威/单一事实源，传播风险最高，建议优先修正。

---

## 八、附：项目记忆（`MEMORY.md`）过时项

- **位置**：`/Users/3yearszhuang/Documents/FztbuCS-Project/.workbuddy/memory/MEMORY.md` 版本号四源约定第④条。
- **问题**：记载 `CS-Web-Backend/uv.lock（根包 fastapi-witchcat-framework）`，但 `uv.lock` 实际根包名为 **`cs-web-backend`**（`fastapi-witchcat-framework` 已不存在）。
- **影响**：该记忆会误导后续会话对"第四版本源"的查找，属项目记忆陈旧。
- **建议**：将第④条更正为 `CS-Web-Backend/uv.lock（根包 cs-web-backend）`。（不在仓库文档范畴，已在本会话单独修正。）

*本报告未改动任何代码/配置/文档，仅记录冲突与建议。如需将任意项登记进 `docs/项目待办事项.md` 或开始落地，请告知。*
