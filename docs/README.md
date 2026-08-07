# 文档（根级 · 跨项目/编排层）

> 本目录只放**跨项目 / 编排层**的通用内容与记录，作为全栈仓库的统一文档入口。
> 前后端各自的强相关文档仍留在各自 submodule 内（见文末"子仓库文档索引"），实现"统一入口、单一权威、零漂移"。

## 根级文档

| 文档 | 说明 |
|---|---|
| [RootDoc-FEArch.md](RootDoc-FEArch.md) | 前端通用目录/架构准则（框架无关，唯一权威） |
| [RootDoc-EngConv.md](RootDoc-EngConv.md) | 通用工程规范（命名 / DRY / 圈复杂度 / 错误处理 / 安全 / 配置 / 测试 / Git / 中文排版） |
| [RootDoc-Deploy.md](RootDoc-Deploy.md) | 全栈部署 / 运维（本地并行启动、容器化部署、健康检查、回滚、数据卷） |
| [RootDoc-MigEval.md](RootDoc-MigEval.md) | 迁移可行性 + 多数据库支持评估报告 |
| [Onboarding.md](Onboarding.md) | 新开发者/新管理员第一天教程（环境→本地→部署→排障，含「当前真实进度」标注） |

## 子仓库文档索引（原地保留，非迁移）

| 仓库 | 入口 | 内容 |
|---|---|---|
| `CS-Web-Backend/docs/` | [README.md](../../CS-Web-Backend/docs/README.md) | 后端 FastAPI 文档索引：`BackDoc-Arch` / `BackDoc-Conv` / `BackDoc-Sec` / `BackDoc-Infra` / `BackDoc-Mods` / `BackDoc-MigV` |
| `CS-Web-Frontend/tools/docs/` | `FrontDoc-*.md` | 前端文档：`FrontDoc-Arch`（架构+API）、`FrontDoc-UID`、`FrontDoc-Sec`、`FrontDoc-Ops`、`FrontDoc-Evo`（ADR）、`FrontDoc-MDE`、`FrontDoc-PGMig`（供开发者中心 `/api/dev-docs` 运行时读取） |
