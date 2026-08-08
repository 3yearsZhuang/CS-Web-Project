# 文档（根级 · 跨项目/编排层）

> 本目录只放**跨项目 / 编排层**的通用内容与记录，作为全栈仓库的统一文档入口。
> 前后端各自的强相关文档仍留在各自子仓库(submodule) 内（见文末"子仓库文档索引"），实现"统一入口、单一权威、零漂移"。

## 根级文档

| 文档 | 说明 |
|---|---|
| [RootDoc-FEArch.md](RootDoc-FEArch.md) | 前端通用目录/架构准则（框架无关，唯一权威） |
| [RootDoc-EngConv.md](RootDoc-EngConv.md) | 通用工程规范（命名 / DRY / 圈复杂度 / 错误处理 / 安全 / 配置 / 测试 / Git / 中文排版） |
| [RootDoc-Deploy.md](RootDoc-Deploy.md) | 全栈部署 / 运维（本地并行启动、容器化部署、健康检查、回滚、数据卷） |
| [RootDoc-MigEval.md](RootDoc-MigEval.md) | 迁移可行性 + 多数据库支持评估报告 |
| [Onboarding.md](Onboarding.md) | 新开发者/新管理员第一天教程（环境→本地→部署→排障，含「当前真实进度」标注） |
| [tools-workbench-redesign-plan.md](tools-workbench-redesign-plan.md) | 工具页 → 工作台改造方案（历史方案，已部分落地 0.9.8，保留为对照记录） |
| [CHANGELOG.md](../CHANGELOG.md) | 发布说明（Keep a Changelog 格式，按版本记录显著变更） |
| [api-reference.md](api-reference.md) | API 参考（由 `openapi.baseline.json` 0.9.8 冻结契约自动生成，请勿手改） |

## 子仓库文档索引（原地保留，非迁移）

| 仓库 | 入口 | 内容 |
|---|---|---|
| `CS-Web-Backend/tools/docs/` | [README.md](../../CS-Web-Backend/tools/docs/README.md) | 后端 FastAPI 文档索引：`BackDoc-01-Arch.md`（架构 + 业务模块契约 Part B，原 `BackDoc-Mods.md` 并入）、`BackDoc-02-Sec.md`（安全）、`BackDoc-Conv.md`（工程约定）、`BackDoc-Infra.md`（基础设施，原 `BackDoc-MigV` 已并入） |
| `CS-Web-Frontend/tools/docs/` | [README.md](../../CS-Web-Frontend/tools/docs/README.md) | 前端文档：`FrontDoc-01-Arch.md`（架构 + 业务模块契约 Part B + 前后端联动）、`FrontDoc-02-Sec.md`（安全）、`FrontDoc-UID.md`（UI 设计规范 + Markdown 编辑器 §14，原 FrontDoc-MDE 并入）、`FrontDoc-Ops.md`（运维）、`FrontDoc-i18n.md`（国际化迁移指南）；PG 迁移归档已并入根 [`RootDoc-MigEval.md`](RootDoc-MigEval.md) §八；发布说明 [`CHANGELOG.md`](../../CS-Web-Frontend/CHANGELOG.md) |

---

## 新增文档登记规范

为避免再次出现文档漂移 / 孤儿文档 / 死链，新增或合并文档时须遵守以下规则：

- **归入位置**：跨项目 / 编排层内容放入根 `docs/`（本目录）；端侧强相关内容放入对应子仓库的 `tools/docs/`（`CS-Web-Backend/tools/docs/` 或 `CS-Web-Frontend/tools/docs/`）。
- **必须登记**：新增文档须在本文档地图 / 索引登记，否则视为孤儿文档，易被死链引用或遗漏。
  - 根级文档 → 上方「根级文档」表；
  - 端侧文档 → 对应子仓库文档索引（如 `CS-Web-Backend/tools/docs/README.md`），根级仅保留入口链接（见「子仓库文档索引」表）。
- **删除 / 合并同步**：任何文档删除或合并（如 `BackDoc-MigV` 并入 `BackDoc-Infra`、`BackDoc-SLO` 并入 `RootDoc-Deploy.md` 的 §七）须同步更新本文档地图、子仓库文档索引与相关正文引用，避免遗留已失效的文档名。

---

## 信息缺口声明

- ~~**api-reference 文档尚未生成**~~ → **已解决（2026-08-08）**：已生成 `docs/api-reference.md`（由 `openapi.baseline.json` 0.9.8 冻结契约自动生成）并登记至上方「根级文档」表。
- ~~**前端子仓库内部死链（FrontDoc-PGMig 引用 FrontDoc-Evo）**~~ → **已核正（2026-08-08）**：链接 href 实际指向 `docs/项目演变历史-0.9.1.md#附录前端演进路线图与迁移文档原-frontdocevomd`（锚点存在、非死链）；已将显示文本从易误导的「FrontDoc-Evo.md」改为「项目演变历史-0.9.1.md 附录（原 FrontDoc-Evo.md）」。
- **CHANGELOG.md 归属（跨项目版本锚点）**：跨项目的发布说明（版本锚点）统一落在**根仓 `CHANGELOG.md`**（Keep a Changelog 格式，含 0.9.8 工作台 / Auxilio 等跨端变更），由根仓维护；根 README「详细文档导航 / 版本号单一源」与本文档地图「根级文档」表均指向它。前端子仓库另有其本地 `CS-Web-Frontend/CHANGELOG.md`（前端侧变更、可选维护），已在「子仓库文档索引」登记，**不**作为跨项目锚点；后端无独立 CHANGELOG 文件，版本同步以 `pyproject.toml` / `app/__init__.py.__version__` / `uv.lock` 为准（详见根 README「版本号单一源」）。
