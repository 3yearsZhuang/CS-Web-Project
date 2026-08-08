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
| [tools-workbench-redesign-plan.md](tools-workbench-redesign-plan.md) | 工具页 → 工作台改造方案（草稿） |

## 子仓库文档索引（原地保留，非迁移）

| 仓库 | 入口 | 内容 |
|---|---|---|
| `CS-Web-Backend/tools/docs/` | [README.md](../../CS-Web-Backend/tools/docs/README.md) | 后端 FastAPI 文档索引：`BackDoc-01-Arch` / `BackDoc-Conv` / `BackDoc-02-Sec` / `BackDoc-Infra`（原 `BackDoc-MigV` 已并入）/ `BackDoc-Mods` |
| `CS-Web-Frontend/tools/docs/` | `FrontDoc-*.md` | 前端文档：`FrontDoc-Arch`（架构+API）、`FrontDoc-UID`、`FrontDoc-Sec`、`FrontDoc-Ops`、`FrontDoc-Evo`（ADR）、`FrontDoc-MDE`、`FrontDoc-PGMig`（供开发者中心 `/api/dev-docs` 运行时读取） |

---

## 新增文档登记规范

为避免再次出现文档漂移 / 孤儿文档 / 死链，新增或合并文档时须遵守以下规则：

- **归入位置**：跨项目 / 编排层内容放入根 `docs/`（本目录）；端侧强相关内容放入对应子仓库的 `tools/docs/`（`CS-Web-Backend/tools/docs/` 或 `CS-Web-Frontend/tools/docs/`）。
- **必须登记**：新增文档须在本文档地图 / 索引登记，否则视为孤儿文档，易被死链引用或遗漏。
  - 根级文档 → 上方「根级文档」表；
  - 端侧文档 → 对应子仓库文档索引（如 `CS-Web-Backend/tools/docs/README.md`），根级仅保留入口链接（见「子仓库文档索引」表）。
- **删除 / 合并同步**：任何文档删除或合并（如 `BackDoc-MigV` 并入 `BackDoc-Infra`、`BackDoc-SLO` 并入 `RootDoc-Deploy.md` 的 §七）须同步更新本文档地图、子仓库文档索引与相关正文引用，避免遗留已失效的文档名。
