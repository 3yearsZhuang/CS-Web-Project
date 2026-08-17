# FztbuCS-Project 可删除 / 可精简项清理清单

> 生成日期：2026-08-17
> 范围：整个项目（根仓 + CS-Web-Backend + CS-Web-Frontend）的文档 / 配置 / 代码 / 构建产物
> 方法：全仓 grep 引用关系 + `git ls-files` + 文档治理（DocGovernance）交叉核对；本文是对 `文档冲突审查`、`规范化建议`、`架构评审` 三份交付物的去重整合，并补充探查新发现
> 定位：**清理行动清单（分析交付物，未改动任何文件）**。逐项附证据与风险，按"安全删除 → 确认后删除 → 精简合并 → 架构重构"分级

---

## 一、🟢 可直接删除（低风险、已确认）

> 这类多为误跟踪的临时/构建产物与死配置，删除不影响功能。

| # | 项 | 路径 | 证据 | 处理 |
|---|---|---|---|---|
| C-1 | 前端 0 字节临时文件 | `CS-Web-Frontend/_tmp_33626_f9f46e08578f93e13cfb3c6884bfc357` | git 已跟踪，0 B，`.gitignore` 无 `_tmp_*` 模式 | `git rm --cached` + 补 `_tmp_*` 忽略（对应 N-02）**✅ 已执行 2026-08-17** |
| C-2 | 后端覆盖率残留 | `CS-Web-Backend/.coverage.Mac.*`（约 585 KB，未跟踪） | 后端 `.gitignore` 已含 `.coverage.*`，仅工作区残留 | 直接删 + 保持忽略（对应 X-4）**✅ 已执行 2026-08-17** |
| C-3 | 后端死配置段 | `CS-Web-Backend/pyproject.toml:46-51` `[tool.basedpyright]` | CI 仅跑 mypy，pyright 未进流水线；requirements-dev 注释明言"统一 mypy" | 删除该段（对应 N-05）**✅ 已执行 2026-08-17（TOML 校验通过）** |
| C-4 | 根仓临时文件 | `be_err.txt` 等（见 CS-01） | 当前工作区 `find` 未命中，疑似已清理；若仍在其它路径则按 CS-01 清理 | 二次确认后删除 **✅ 已核实：未发现 be_err.txt，无需操作** |

---

## 二、🟡 删除前需确认（中风险，先核实再删）

| # | 项 | 路径 | 证据 | 确认点 / 风险 |
|---|---|---|---|---|
| C-5 | **前端死代码 + 死依赖** | `CS-Web-Frontend/src/shared/utils/mail.ts`（2 KB）；`package.json:35 nodemailer`、`package.json:54 @types/nodemailer` | `mail.ts` 仅被 `src/shared/utils/index.ts:8` 的**注释示例**引用（无真实 import）；`sendVerificationCode/sendMail` 全仓 src 内除自身与注释外 0 引用；覆盖率 `FNDA:0`；前端 README 自承"nodemailer 为迁移前遗留，运行时未使用"（邮件由后端 aiosmtplib 承载） | 删 `mail.ts` + 移除两个依赖，并清理 `index.ts:8` 注释。删除前 grep 一次 `sendVerificationCode` 全局无引用即可（对应新发现 F-A1）**✅ 已执行 2026-08-17**（删 `mail.ts` + 移除 `nodemailer`/`@types/nodemailer` 依赖 + 清理 `index.ts:8` 注释） |
| C-6 | 后端一次性 Alembic 修复脚本 | `CS-Web-Backend/scripts/sync_alembic_version_ids.sql`（2.3 KB） | 全仓 grep 唯一命中是文件自身注释中的用法示例；内容为 2026-08-14 一次性 `UPDATE alembic_version` 旧 id 修复，未被 Makefile/CI/文档引用 | 若各环境 `alembic_version` 已为新 id（迁移已完成），可删或移入 `tools/docs/` 归档并登记触发条件（对应新发现 F-A2）**✅ 已执行 2026-08-17**（直接删除文件，迁移已完成确认） |

---

## 三、🟦 可精简 / 合并 / 收敛（配置与文档去重）

> 这类不删功能，而是消除重复与漂移，符合项目自有 DRY / SSOT 原则。

| # | 项 | 路径 | 证据 | 建议 |
|---|---|---|---|---|
| C-7 | **依赖声明双轨收敛** | `pyproject.toml`+`uv.lock` 与 `requirements.txt`/`requirements.lock`/`requirements-dev.lock`/`requirements-dev.txt`/`requirements-queue.txt`（六份） | `ci.yml:48` 实际 `pip install --require-hashes -r requirements-dev.lock`；五份 requirements 均被 `tools/tests/core/test_dependency_manifest.py` 校验引用（非死文件） | 收敛为 **uv 唯一**（CI 改 `uv sync --locked`）或 pip-tools 唯一；属决策项，合并进既有 CS-05（对应 N-07）**✅ 已执行 2026-08-17（方案A'：uv 单源 + pyproject dev extra + `uv export` 重生成两锁 + Makefile `deps-export`；runtime 锁验证等价、dev 锁 14 工具版本更新；`test_dependency_manifest.py` 改验 pyproject⊆uv.lock）** |
| C-8 | **三份 .gitignore 公共段漂移** | 根 / 后端 / 前端 `.gitignore` | 公共段（`.trae-cn/`/`.workbuddy/`/`.devlogs/`）根仓 3 行、后端/前端各 0 行 | 根级作公共段唯一权威，子仓仅留语言专属段 + CI 一致性校验（对应 N-04）**✅ 已执行 2026-08-17（后端/前端补齐 `.devlogs/`/`.dev.pid`/`.trae-cn/`/`.workbuddy/`，`_tmp_*` 归位前端专属段；新增 `scripts/check/check_gitignore_sync.py` + `make check-gitignore-sync` 并入 `check`，正/负向测试通过）** |
| C-9 | **CI 系统双轨** | `CS-Web-Backend/Jenkinsfile`（5 KB）与 `.github/workflows/ci.yml` | 两者测试环境/步骤高度重合 | 确认 Jenkins 去留：废弃则删并注释；在用则 RootDoc-Deploy 明确分工（对应 N-08）**✅ 已执行 2026-08-17（B 方案：删除尝试被否后保留，`RootDoc-Deploy.md` 新增 §八 CI 分工表——ci.yml 主验证门禁 / Jenkinsfile 等价备用+ER-09；原 §八→§九）** |
| C-10 | **三份 .env.example 职责不清** | 根 / 后端 / 前端 `.env.example` | README 只说根级是"全栈模板"，未定义三层变量归属矩阵 | RootDoc-EngConv §五 或 README 增加 env 变量职责矩阵（层 × 变量 × 归属）（对应 N-14）**✅ 已执行 2026-08-17（矩阵入 `RootDoc-EngConv.md` §5.1，17 组变量 + 前端遗留变量说明）** |
| C-11 | **孤儿调研文档未登记** | `docs/公共组件调研报告.md`（8.4 KB） | 全仓 grep `公共组件调研报告` 唯一命中即文件自身（外部引用 0）；`docs/README.md` 文档地图未登记，违反项目 DocGovernance「新增文档须登记，否则孤儿」 | 二选一：① 在文档地图补登记（归"参考/调研"）；② 移入 `docs/archive/` 并标"已完成调研"（对应新发现 F-B1）**✅ 已执行 2026-08-17（① 登记入 `docs/README.md` 根级文档表，归参考/调研类）** |
| C-12 | **社区重构文档归档** | `CS-Web-Backend/tools/docs/BackDoc-Refactor-CommunityService.md` | 页眉/索引标"规划中"但正文 `:53/:70` 记已完成（2026-08-11）；代码已删 `community_service.py` | 除改状态为"已完成"外，可移入 `tools/docs/archive/` 减少活文档噪声（对应 F-B3，叠加文档冲突审查 F-8）**✅ 已执行 2026-08-17（A 方案：文档状态改已完成 + §8 排期 + 测试路径修正 + 索引节标题/条目同步，无「规划中」残留）** |
| C-13 | **历史分卷合并（弱候选）** | `docs/项目演变历史-0.9.5.md`(66) / `0.9.6.md`(51) / `0.9.7.md`(105) | 主索引 `项目演变历史.md:24` 明言"原合并于一个文件，现按版本拆分"；三份连续且体量极小（共 222 行） | 若坚持"按版本拆分"约定则保留；若重文件数精简可合并为 `项目演变历史-0.9.5~0.9.7.md`。**需先确认是否违反现有约定**（对应 F-B2）**✅ 已执行 2026-08-17（B 方案：合并为 `项目演变历史-0.9.5~0.9.7.md` 单文件 182 行，三卷删除，索引合并行 + line 24 说明改写 + 0.9.8 前序引用同步）** |
| C-14 | **前端 CHANGELOG 缺 0.9.9 锚点** | `CS-Web-Frontend/CHANGELOG.md` | 仅有 `[Unreleased]/[0.9.8]/[0.9.7]/[0.9.6]/[0.9.1]`，缺 `[0.9.9]`；根 CHANGELOG 有 `[0.9.9]` | 补 0.9.9 锚点 + 链接，或明确"前端 CHANGELOG 仅留锚点、跨项目以根仓为准"的边界说明（轻微漂移）**✅ 已执行 2026-08-17（补 `[0.9.9]` 段 + 链接 + header 边界说明「跨项目权威以根仓 CHANGELOG 为准」）** |

---

## 四、🟥 架构层精简（非简单删除，属重构，引用架构评审）

> 这些是"精简"的深层形态——消除冗余实现与膨胀，需按既有待办节奏推进，不在此次"删除"范畴。

| # | 项 | 位置 | 说明 | 关联 |
|---|---|---|---|---|
| C-15 | 前端 BFF 样板膨胀 | 141 个 `route.ts` + `backend-client.ts`（594 行） | 参数解析/错误归一/字段映射每路由重复；建议以 `openapi.baseline.json` 生成 route 骨架 | 架构评审 D-A3（P1） |
| C-16 | service 层 28 处直查 `self.db.execute` | `community_post._enrich_posts`、`user_service:500` 等 | 查询逻辑散落，repo 无法复用；建议下沉至 repository | 架构评审 M-A3 / M4（P1） |
| C-17 | 上帝服务残留 | `user_service.py` 844 行 / `auth_service.py` 775 行 | 建议按 ER-15 范式拆 UserService/AuthService | 架构评审 M-A1（P1） |
| C-18 | repository 巨型文件 | `community_repo.py` 718 行（7 类）/ `tools_repo.py` 621 行 | 与已拆 service 子域不对齐 | 架构评审 M-A2（P2） |
| C-19 | 前端数据获取分散 | 40 个模块文件手写 `fetch+useState` | 建议封装 `useApiRequest`（SWR）收敛 | 架构评审 D-A4（P1） |

> 注：C-15~C-19 是**重构机会**而非"可删除文件"，列出是为完整性；落地见 `deliverables/FztbuCS-Project-architecture-review-2026-08-17.md` 与 `docs/项目待办事项.md`。

---

## 五、🚫 已核实"不可删 / 非问题"（避免误删）

- **`community_service.py` 兼容 re-export 残留**：不存在；`community_utils.py` 仍被 5 处活跃引用，是存活模块。
- **`src/shared/db`**：已按 B1 闭环删除干净。
- **0 字节 `__init__.py`**：Python 包标识，必须保留。
- **后端 `scripts/` 与前端 `.mjs` 脚本**：除 C-6 的 SQL 外，其余均被 Makefile/CI/package.json 引用，非死脚本。
- **根 README vs docs/README**：已核实互补（README 自陈单一事实源，docs/README 仅作索引），无重复维护。
- **`FrontDoc-PGMig → FrontDoc-Evo` 死链**：2026-08-08 已核正，当前无此二文件。
- **`capsule-tabs.md`**：被多处引用，非孤儿（命名前缀例外已登记）。
- **node_modules / 构建缓存**：已被 .gitignore 忽略，未入库，不该手动删。

---

## 六、建议执行顺序

1. **波次 1（随手做，零风险）**：C-1、C-2、C-3、C-4 —— **全部已执行 2026-08-17**。
2. **波次 2（需你拍板/确认）**：C-5、C-6 —— **已执行 2026-08-17**；C-9、C-7 已并入波次 3 决策项。
3. **波次 3（文档/配置收敛 + 决策项）**：C-7（A' uv 单源）、C-8（补齐+校验脚本）、C-9（B 保留+分工）、C-10（矩阵入 EngConv）、C-11（登记文档地图）、C-12（状态修正保留）、C-13（合并单文件）、C-14（补锚点+边界说明）—— **全部已执行 2026-08-17**。
4. **波次 4（架构重构，非删除）**：C-15~C-19，进既有待办体系，建议 0.9.9 发布后评估。

> 最高性价比两项：**C-5**（删前端死依赖 `nodemailer`，缩 `pnpm-lock` 体积、消供应链攻击面）与 **C-11**（消除孤儿文档以符合项目自有 DocGovernance 红线），证据最充分、风险最低，建议优先。

---

*本文最初为分析清单（未改动文件）；**波次 1~3（C-1~C-14）已全部按用户指令执行**（2026-08-17，含决策项 C-7/C-9），各条目见 ✅ 标记。改动分散在根仓 / 后端 / 前端，多数未提交（待用户确认后分批提交）；波次 4（C-15~C-19）为架构重构，进既有待办体系。*
