# 文档（根级 · 跨项目/编排层）

> 本目录只放**跨项目 / 编排层**的通用内容与记录，作为全栈仓库的统一文档入口。
> 前后端各自的强相关文档仍留在各自子仓库(submodule) 内（见文末"子仓库文档索引"），实现"统一入口、单一权威、零漂移"。

## 根级文档

| 文档 | 说明 |
|---|---|
| [RootDoc-FEArch.md](RootDoc-FEArch.md) | 前端目录/架构方法论（以 CS-Web-Frontend 真实结构为锚，唯一权威） |
| [RootDoc-EngConv.md](RootDoc-EngConv.md) | 通用工程规范（命名 / DRY / 圈复杂度 / 错误处理 / 安全 / 配置 / 测试 / Git / 中文排版） |
| [RootDoc-Deploy.md](RootDoc-Deploy.md) | 全栈部署 / 运维（本地并行启动、容器化部署、健康检查、回滚、数据卷） |
| [RootDoc-MigEval.md](RootDoc-MigEval.md) | 迁移可行性 + 多数据库支持评估报告 |
| [RootDoc-ADR.md](RootDoc-ADR.md) | 架构决策（ADR）索引 / 边界上下文 / 数据流 / 韧性 / BFF 交互风格（设计决策 SSOT，L0） |
| [Onboarding.md](Onboarding.md) | 新开发者/新管理员第一天教程（环境→本地→部署→排障，含「当前真实进度」标注） |
| [CHANGELOG.md](../CHANGELOG.md) | 全项目变更记录唯一权威（Keep a Changelog 格式，覆盖 `[Unreleased]` → `[0.9.1]`；2026-08-17 起并入原 `项目演变历史.md` 全量内容并删除该文件；跨项目版本锚点以此为准） |
| [api-reference.html](api-reference.html) | API 参考（ReDoc 查看器，由 `openapi.baseline.json` 经 `make gen-api-docs` 生成，请勿手改；入口说明见 [api-reference.md](api-reference.md)） |
| [项目待办事项-优先级重排.md](项目待办事项-优先级重排.md) | 项目待办 / 进行中事项 + ADR 待评估项存放处（与 `RootDoc-ADR.md` 索引联动；2026-08-18 起原 `项目待办事项.md` 并入本文件） |
| [DocGovernance.md](DocGovernance.md) | 文档治理规范（三层架构 + 所有权矩阵 + 反模式清单，SSOT 规则） |
| [公共组件调研报告.md](公共组件调研报告.md) | 前后端公共组件调研（2026-08-12：组件库 / 共享层位置与清单，参考 / 调研类） |

## 子仓库文档索引（原地保留，非迁移）

| 仓库 | 入口 | 内容 |
|---|---|---|
| `CS-Web-Backend/tools/docs/` | [README.md](../CS-Web-Backend/tools/docs/README.md) | 后端 FastAPI 文档索引：`BackDoc-01-Arch.md`（架构 + 业务模块契约 Part B）、`BackDoc-02-Sec.md`（安全）、`BackDoc-Conv.md`（工程约定）、`BackDoc-Infra.md`（基础设施） |
| `CS-Web-Frontend/tools/docs/` | [README.md](../CS-Web-Frontend/tools/docs/README.md) | 前端文档：`FrontDoc-01-Arch.md`（架构 + 业务模块契约 Part B + 前后端联动）、`FrontDoc-Conv.md`（编码规范，对标后端 BackDoc-Conv.md）、`FrontDoc-02-Sec.md`（安全）、`FrontDoc-UID.md`（UI 设计规范 + Markdown 编辑器 §14）、`FrontDoc-Ops.md`（运维）、`FrontDoc-i18n.md`（国际化迁移指南） |
| `CS-Mobile/tools/docs/` | [README.md](../CS-Mobile/tools/docs/README.md) | 移动端文档：uni-app 单码双端架构/构建、ApiClient 薄层与 token 安全存储、U-02~U-04 依赖（规划文档 MobileDoc-01-Arch / 02-Sec / Conv 待建） |

---

## 新增文档登记规范

为避免再次出现文档漂移 / 孤儿文档 / 死链，新增或合并文档时须遵守以下规则：

- **归入位置**：跨项目 / 编排层内容放入根 `docs/`（本目录）；端侧强相关内容放入对应子仓库的 `tools/docs/`（`CS-Web-Backend/tools/docs/` 或 `CS-Web-Frontend/tools/docs/`）。
- **必须登记**：新增文档须在本文档地图 / 索引登记，否则视为孤儿文档，易被死链引用或遗漏。
  - 根级文档 → 上方「根级文档」表；
  - 端侧文档 → 对应子仓库文档索引（如 `CS-Web-Backend/tools/docs/README.md`），根级仅保留入口链接（见「子仓库文档索引」表）。
- **删除 / 合并同步**：任何文档删除或合并须同步更新本文档地图、子仓库文档索引与相关正文引用，避免遗留已失效的文档名。

---

## 信息缺口声明

- **CHANGELOG.md 归属（跨项目版本锚点）**：变更记录与发布说明统一为**根仓 `CHANGELOG.md`**（Keep a Changelog 格式，唯一权威；原 `docs/项目演变历史.md` 已于 2026-08-17 并入本文件并删除）。前端子仓库自 2026-08-17 起不再维护独立 CHANGELOG（薄锚点文件已删除），版本锚点一律以根仓 `CHANGELOG.md` 为准；后端无独立 CHANGELOG 文件，版本同步以 `pyproject.toml` / `app/__init__.py.__version__` / `uv.lock` 为准（详见根 README「版本号单一源」）。
