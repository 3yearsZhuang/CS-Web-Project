# FztbuCS-Project 规范化差距分析报告

> 生成日期：2026-08-17
> 调研范围：根仓（编排层）+ 两个子仓库(submodule)（CS-Web-Backend / CS-Web-Frontend）
> 调研深度：根级文档地图、工程规范、CI 工作流、依赖声明、Git 元数据、代码结构与残留物
> 定位：**分析交付物（非正式文档）**。如采纳，建议按 DocGovernance 登记进 `docs/README.md` 与 `docs/项目待办事项.md`，条目拆入对应优先级区。

---

## 一、摘要（TL;DR）

项目工程化成熟度**整体较高**：文档治理（三层 SSOT + 死链/锚点审计）、CI 门禁（契约冻结、覆盖率、供应链审计、版本四源同步）、后端 432 测试全绿、部署护栏齐备，均已达到相当规范的水平。

但调研仍发现 **14 项未被既有待办覆盖或未完全覆盖的差距**，其中 **3 项 P0（安全/流程风险）**、**8 项 P1（工程化/治理）**、**3 项 P2（优化）**。最需要立即关注的三件事：

1. **`.env.development` 含真实密钥被 git 跟踪提交**（违反自家「密钥不入库」红线，历史不可逆）；
2. **前端工作分支 `Z.0813` 与 CI 触发分支（main/master）脱节**（该分支 push 无任何门禁，且 submodule gitlink 指向它而非 main）；
3. **前端 0 字节临时文件 `_tmp_33626_...` 已入库**（仓库污染，可立即清理）。

---

## 二、项目现状快照

| 维度 | 现状 |
|---|---|
| 定位 | 高校计算机协会官网平台；根仓编排 + 前后端 submodule |
| 版本线 | **0.9.9 → 1.0.0 准备期**（P1+P2 全量完成后发 0.9.9；待办清零后发 1.0.0） |
| 后端 | FastAPI + PostgreSQL 16 + Redis + arq worker；分层 api→service→repository→model；Alembic 迁移 |
| 前端 | Next.js 16 BFF 薄转发（442 个 ts/tsx），不持有业务数据；next-intl i18n |
| 测试 | 后端 432 passed（含真实 PG/Redis 集成测试）；前端 Vitest 起步（覆盖率门槛 11%，待递增） |
| 文档 | 三层 L0/L1/L2 SSOT；DocGovernance 所有权矩阵；死链 0 + 坏锚点 0 |
| CI | 后端 ci.yml（lint/type/test/契约/审计/覆盖率门禁）；前端 ci.yml + audit.yml；根仓 e2e.yml（nightly） |
| 发布 | Keep a Changelog 手工维护；`make contract-baseline` 契约冻结；四源版本同步 + `make check-version` 门禁 |

## 三、规范化成熟度盘点（强项，非差距）

以下已规范到位，建议**维持现状**，不在本次建议范围内：

- ✅ 文档治理：三层文档架构、SSOT 所有权矩阵、反模式清单、死链/锚点双审计自动化（`scripts/check_dead_links.py` + `audit_anchors.py`）
- ✅ 契约管理：`openapi.baseline.json` 冻结 + CI 比对门禁 + 前端 `openapi-typescript` 生成类型 + drift gate（ER-47）
- ✅ 质量门禁：后端 black/flake8/mypy + PR diff 覆盖率 80%；前端 ts-check/lint/test + diff 覆盖率；BFF 安全边界扫描（AL-1）
- ✅ 供应链安全：pip_audit（双 lock 文件）+ cyclonedx SBOM + piplicenses 许可门禁 + pnpm audit（moderate+ 阻断）+ 每周定时审计
- ✅ 版本治理：四源（pyproject / `__init__.__version__` / package.json / uv.lock）同步 + `check_version_sync.py` CI 门禁
- ✅ 部署护栏：compose healthcheck/资源限制/优雅停机/迁移分离/日志持久化/多 worker（ER-29~ER-40）
- ✅ 待办治理：`项目待办事项.md` P0-P3 分级 + 决策清单 D1~D10 + 已完成项归档附录
- ✅ 环境卫生：前端 `.env`/`devserver.log`/`tsbuildinfo` 均正确未跟踪；`.coverage.*` 已忽略

---

## 四、差距分析（按优先级）

### P0 ｜安全 / 流程风险（建议尽快处理）

#### N-01 密钥入库：`.env.development` 含真实密钥被 git 跟踪

- **证据**：`CS-Web-Backend/.env.development` 被 git 跟踪（`git ls-files` 命中），其中 `SECRET_KEY=368715...`、`TOTP_ENCRYPTION_KEY=96888d...`、`DATABASE_PASSWORD=pg_1e7...` 为**真实生成值**（非 `.env.example` 的 `GENERATE_*` 占位符）。
- **影响**：违反自家红线（RootDoc-EngConv §四「禁止硬编码密钥」/ §五「密钥不入库」）；Git 历史永久保留，一旦仓库对外可见即泄露；若该密钥被复用/推演到其他环境，风险扩大。
- **方案**：
  - **方案 A（推荐）**：`.env.development` 改名为 `.env.development.example`（占位符）入库，真实文件 gitignore + 本地重建；同时**轮换**当前密钥。
  - 方案 B：保留入库但仅作「本地开发专用」并加 `gitleaks` pre-commit/CI 扫描兜底（治标，不治本）。
  - 方案 C：`git filter-repo` 清洗历史（成本高，仅仓库公开前需要）。
- **关联**：RootDoc-EngConv §四/§五；N-06（钩子）可顺带落地 gitleaks。

#### N-02 仓库污染：前端 0 字节临时文件已提交入库

- **证据**：`CS-Web-Frontend/_tmp_33626_f9f46e08578f93e13cfb3c6884bfc357`（0 字节）已被 git 跟踪；`.gitignore` 无 `_tmp_*` 模式。
- **影响**：仓库混入运行时噪音产物；同类文件后续仍可能再次误入库。
- **方案**：`git rm --cached` + `.gitignore` 追加 `_tmp_*`；顺带清理后端工作区残留的 `.coverage.Mac.pid*`（585KB，未跟踪但占空间）。
- **风险**：极低，立即可做。

#### N-03 前端工作分支与 CI 触发分支脱节

- **证据**：前端当前工作分支为 `Z.0813`（`git branch --show-current`），且 submodule gitlink 指向 `b0b6bd5 (Z.0813)`；但前端 ci.yml `on.push.branches: [main, master]` 仅覆盖 main/master，`Z.0813` 上的 push **不触发 CI**；同时前端 main 已落后于工作分支。
- **影响**：工作分支改动零门禁覆盖，质量防线只在合并时生效；发版时若漏切回 main 或漏合并，gitlink 指向的分支与发布分支不一致，容易产生「CI 绿但线上是未验证代码」的错觉。
- **方案**：
  - 方案 A（推荐）：约定「开发分支 → PR 合入 main → 从 main 发版」，submodule 指针只前进到 main 上的提交；CI 维持 PR-to-main 触发（已覆盖）。
  - 方案 B：CI `push` 扩大到所有分支（资源开销大，意义有限）。
  - 方案 C：开发分支命名规范化（`feat/*`、`fix/*`）+ Onboarding/README 文档化「工作分支与发版分支」流程。
- **关联**：README「分支与 PR 流程」、Onboarding。

### P1 ｜工程化 / 治理

#### N-04 `.gitignore` 公共段三份复制，已发生漂移

- **证据**：根/后端/前端 `.gitignore` 各自维护一份「公共段」（注释自称三者一致），但漂移已发生：根级含 `.trae-cn/`、`.workbuddy/`、`.devlogs/` 三行，后端与前端公共段**均缺失**（`grep -c` 均为 0）。
- **影响**：违反自家 DRY 原则（RootDoc-EngConv §二）；后续任一仓误提交工具目录/agent 数据时，另两仓不会同步防护。
- **方案**：
  - 方案 A（推荐）：根级 `.gitignore` 作为公共段**唯一权威**，子仓仅保留语言专属段（公共段改为「引用根级」或维护脚本同步 + CI 一致性校验）。
  - 方案 B：补全三处缺失行（治标，漂移会复发）。
- **关联**：RootDoc-EngConv §二 DRY；N-06 可顺带加 CI 校验脚本。

#### N-05 死配置：`pyproject.toml` 中 `[tool.basedpyright]` 残留

- **证据**：`CS-Web-Backend/pyproject.toml:48-51` 存在 `[tool.basedpyright]` 段，但 CI 实际使用 mypy（`ci.yml` 的 `python -m mypy`），且 `requirements-dev.txt` 注释明言「统一使用 mypy，不再并行维护 pyright」。
- **影响**：误导读者以为项目采用 basedpyright；工具链声明与实现不一致。
- **方案**：删除该段；若有意保留备用，加注释说明（推荐删除）。
- **风险**：极低，立即可做。

#### N-06 本地 Git 钩子缺失（pre-commit / commitlint）

- **证据**：三仓均无 `.pre-commit-config.yaml`、`.husky`；前端 package.json 无 husky/lint-staged；CI 无 commit message 校验步骤。
- **影响**：提交格式规范（RootDoc-EngConv §七 `<type>(<scope>):`）与质量红线靠自觉；CI 是最后防线，但无法拦截不合规的 commit message（CI 中无对应检查），坏提交信息会永久留在历史里。
- **方案**：
  - 后端：`pre-commit` framework（black --check / flake8 / mypy 增量 + gitleaks 密钥扫描）。
  - 前端：`husky` + `lint-staged`（eslint/tsc 增量）+ `commitlint` 校验提交格式。
  - 注意与协作约束兼容：RootDoc-EngConv §七「不主动 commit/push」仅约束 agent，本地钩子不冲突。
- **关联**：N-01（gitleaks）、N-04（CI 校验）、RootDoc-EngConv §七。

#### N-07 依赖声明双轨（uv 生态 vs pip 生态）

- **证据**：后端同时存在 `pyproject.toml + uv.lock`（uv 生态）与 `requirements.txt + requirements.lock + requirements-dev.lock`（pip/pip-tools 生态）；CI 实际走 pip（`pip install --require-hashes -r requirements-dev.lock`），README 推荐 uv。历史上已发生 cryptography 三处漂移事故（ER-26）。
- **影响**：依赖声明分散在 5 个文件中，双 lock 需同步更新，漂移风险高；ER-26 即实证。
- **方案**：
  - 方案 A（推荐）：收敛为 **uv 唯一**（pyproject + uv.lock），CI 改 `uv sync --locked`（uv 已支持 hash 锁定）。
  - 方案 B：收敛为 pip-tools 唯一（删除 pyproject/uv.lock，README 同步）。
  - 方案 C（保守）：维持双轨 + CI 增加「uv.lock 与 requirements.lock 一致性校验」。
- **关联**：既有待办 **CS-05**（requirements 三份统一 pyproject）——本项是其延伸（lock 双轨 + CI 安装路径），建议合并为同一 P2 条目推进。

#### N-08 双 CI 系统并存：Jenkinsfile 与 GitHub Actions

- **证据**：`CS-Web-Backend/Jenkinsfile`（5KB）与 `.github/workflows/ci.yml` 并存，两者测试环境/步骤高度重合（同一批环境变量、同样的 compose 测试服务）。
- **影响**：CI 逻辑双份维护易漂移；职责边界未文档化，新人困惑「到底哪个生效」。
- **方案**：a) 若 Jenkins 已废弃 → 删除 Jenkinsfile 并注释说明；b) 若在用 → 在 RootDoc-Deploy 明确分工（如 Jenkins 仅负责部署流水线，GA 负责验证）。
- **风险**：需你确认 Jenkins 实际使用情况后处理。

#### N-09 协作设施缺失：PR/Issue 模板、CODEOWNERS、SECURITY.md

- **证据**：根 `.github/` 仅 `workflows/`，无 `PULL_REQUEST_TEMPLATE.md`、`ISSUE_TEMPLATE/`、`CODEOWNERS`、`SECURITY.md`（三仓均无）。
- **影响**：PR 描述质量依赖个人自觉（README 已有 PR 自检清单，但无模板强制）；安全漏洞无标准报告入口。
- **方案**：PR 模板（对齐 README「PR 自检清单」）、Issue 模板（bug/feature）、`CODEOWNERS`（子仓已有明确归属，根仓可加）、`SECURITY.md`（若仓库将公开/开源则必须）。
- **关联**：README「贡献指南」。

#### N-10 前端覆盖率门槛形同虚设，无递增排期

- **证据**：`vitest.config.ts` 阈值 `lines: 11 / functions: 8 / branches: 7 / statements: 10`（注释自述为「基线地板」），并注明「后续随测试补全渐进上调至 50%」，但**无正式条目排期**。
- **影响**：前端仍是测试盲区（CS-02 已登记补测试）；11% 门槛无法阻止覆盖率下滑，形同虚设。
- **方案**：与 CS-02 联动制定递增路线（如按模块推进：primitives → hooks → 动效组件；每模块覆盖后上调阈值），并登记为正式待办条目。
- **关联**：既有待办 **CS-02**、**ER-13**。

#### N-11 文档版本标注滞后：api-reference 标注 0.9.8，实际基线已 0.9.9

- **证据**：`docs/api-reference.md` 与 `docs/README.md:18` 均标注「0.9.8 冻结契约」，但 `openapi.baseline.json` 内 `"version": "0.9.9"`（ER-04 基线重冻已生效）。
- **影响**：文档事实滞后于实现；新人按文档引用旧契约版本。
- **方案**：重新生成 `api-reference.md`（自动生成文件，一次命令可同步）；`docs/README.md` 描述行同步更新。
- **风险**：极低，立即可做。

### P2 ｜优化 / 可选

#### N-12 前端无 AGENTS.md（后端有）

- **证据**：`CS-Web-Backend/AGENTS.md`（11KB）+ `CLAUDE.md` 存在；前端无对应文件。
- **影响**：agent 协作上下文不一致，跨端任务时前端规范缺失入口。
- **方案**：前端补 AGENTS.md，或根仓建统一 agent 规范（对齐现有 FrontDoc-* 体系）。

#### N-13 发布流程无 tag 自动化

- **证据**：CHANGELOG 手工维护（Keep a Changelog，合理）；但无 release workflow（tag 触发自动生成 Release Notes / 同步 CHANGELOG）。
- **影响**：单人/小团队手工发布尚可接受；随协作者增多，tag 与 CHANGELOG 容易脱节。
- **方案**：a) 维持手工 + 发布 checklist 文档化（低优先）；b) 引入 release-please 或轻量 release.yml（tag → notes 自动生成）。

#### N-14 env 模板职责边界未文档化（根级 vs 子仓级）

- **证据**：根 `.env.example`（2.7KB）+ 后端 `.env.example`（8.8KB）+ 前端 `.env.example`（1.5KB）三份并存，README 只说根级是「全栈环境变量模板」，未明确三层 env 变量的**职责矩阵**（哪些变量归哪层定义）。
- **影响**：新增配置时不确定该写哪层模板（RootDoc-EngConv §五要求「新增配置必须同步 .env.example」但没说同步哪份）。
- **方案**：在 RootDoc-EngConv §五或 README 增加 env 变量职责矩阵表（层 × 变量 × 归属）。

---

## 五、与既有待办的对照（去重声明）

| 本报告条目 | 既有待办 | 关系 |
|---|---|---|
| N-07 依赖双轨 | CS-05（requirements 三份统一 pyproject） | **延伸合并**：CS-05 只覆盖 txt 三份，本项补 lock 双轨 + CI 安装路径 |
| N-10 前端覆盖率 | CS-02（前端测试盲区）、ER-13（覆盖率门禁） | **补充排期**：CS-02 补测试，本项补「阈值递增路线」 |
| N-04 gitignore | CS-01（根目录临时文件清理） | **不同面**：CS-01 清文件，本项管 ignore 规则 DRY |
| N-06 钩子 / N-01 gitleaks | 无既有条目 | 全新 |
| N-02 / N-03 / N-05 / N-08 / N-09 / N-11 / N-12 / N-13 / N-14 | 无既有条目 | 全新 |

> 说明：CS-01（`be_err.txt` 等根目录临时文件 + `.trae-cn/` 跟踪问题）与本报告 N-04 相关但聚焦不同，N-04 侧重公共段漂移的结构性问题；两者可一并处理。

---

## 六、建议落地路线图

### 波次 1 ｜立即收口（低风险，随手做）
1. **N-02**：前端 `git rm --cached _tmp_*` + `.gitignore` 追加 `_tmp_*`；清理后端 `.coverage.Mac.*` 工作区残留
2. **N-05**：删除 pyproject.toml 中 `[tool.basedpyright]` 死配置
3. **N-11**：重新生成 `api-reference.md` + 更新 docs/README 版本标注
4. **N-04 缓解**：补全后端/前端公共段缺失的 3 行（治标，根治随 N-04 方案 A 推进）

### 波次 2 ｜P0 安全与流程（需你拍板后执行）
1. **N-01**：确认 `.env.development` 用途 → 改 `.example` 入库 + 密钥轮换 + gitleaks 接入（可并入 N-06 钩子）
2. **N-03**：明确前端分支策略（推荐方案 A：一律合 main 发版），文档化 + 修正 submodule 指针指向 main
3. **N-06**：后端 pre-commit + 前端 husky/lint-staged/commitlint

### 波次 3 ｜治理与长期（进入待办体系）
1. **N-07 + CS-05**：依赖单轨化决策（uv or pip-tools）→ 合并为一个 P2 条目
2. **N-08**：确认 Jenkins 去留 → 删除或文档化分工
3. **N-09**：PR/Issue 模板、CODEOWNERS、SECURITY.md
4. **N-10 + CS-02**：前端测试补齐 + 覆盖率阈值递增路线（正式登记）
5. **N-12 / N-13 / N-14**：按需推进

---

## 七、证据索引（调研记录）

| 发现 | 核验方式 |
|---|---|
| `.env.development` 被跟踪且含真实密钥 | `git ls-files` + grep 键值（`SECRET_KEY=368715...` 等） |
| `_tmp_33626_...` 入库 | `git -C CS-Web-Frontend ls-files` 命中 |
| 前端分支 Z.0813 / main 落后 | `git branch --show-current` + `git log --oneline -3` |
| CI 触发分支 | 前端 ci.yml `on.push.branches: [main, master]` |
| gitignore 公共段漂移 | 三仓 `.gitignore` grep `.trae-cn/`/`.workbuddy/`/`.devlogs/`（根 3 / 后端 0 / 前端 0） |
| basedpyright 死配置 | pyproject.toml:48-51 + ci.yml mypy + requirements-dev.txt 注释 |
| 无 Git 钩子 | 三仓无 `.pre-commit-config.yaml`/`.husky`；package.json 无 husky/lint-staged |
| 依赖双轨 | pyproject+uv.lock 与 requirements*.txt/lock 并存；ci.yml pip 安装 |
| Jenkinsfile 并存 | CS-Web-Backend/Jenkinsfile 存在，与 ci.yml 步骤重合 |
| 协作设施缺失 | 根 `.github/` 仅 workflows/ |
| 前端覆盖率门槛 | vitest.config.ts thresholds 11/8/7/10 |
| api-reference 版本滞后 | docs/api-reference.md 头注「0.9.8」vs baseline `"version": "0.9.9"` |
| 前端无 AGENTS.md | 目录对比（后端有，前端无） |
| env 三层模板 | 根/后端/前端 `.env.example` 体积对比 + README 描述 |

---

*本报告为分析交付物，未改动任何代码/配置。如需将任意条目登记进 `docs/项目待办事项.md` 或开始波次 1 落地，请告知。*
