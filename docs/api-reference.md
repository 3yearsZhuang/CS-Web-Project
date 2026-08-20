# API 参考（FztbuCS-Project）

> 更新人：3yearsZ
> 更新日：2026-08-20
> 版本：1.0.0
> Diátaxis：R（Reference · 回答「是什么」，提供项目 OpenAPI 契约的查看入口与变更流程；内容由 openapi.baseline.json 自动生成，MUST NOT 手改）
> 适用读者：全仓开发者 / 接口联调测试者 / Reviewer；已完成 Onboarding 并了解后端架构
> 变更触发：后端路由/模型变更 / 契约基线刷新 / API 文档重新生成

> **SSOT 声明**：
> - 本文档是「**项目 API 契约的查看入口与变更流程**」的唯一权威（SSOT）。
> - API 字段级权威 = `openapi.baseline.json`（仓库根，契约冻结基线）。
> - 交互式查看器 = [api-reference.html](api-reference.html)（ReDoc 自动生成，`@redocly/cli`）。
> - 路由与模块归属 = [RootDoc-ModuleMap.md](RootDoc-ModuleMap.md)（Reference）。
> - 后端业务模块接口契约 = [BackDoc-ModuleContracts.md](../CS-Web-Backend/tools/docs/BackDoc-ModuleContracts.md)（Reference）。
>
> **治理红线**：
> - MUST NOT 手改 `api-reference.html` 或本文档中的 API 描述；所有内容从 `openapi.baseline.json` 自动生成
> - MUST 在后端路由/模型变更后执行 `make contract-check` 校验与基线差异
> - MUST 在评审通过后执行 `make contract-baseline` 刷新基线
> - MUST 在基线刷新后执行 `make gen-api-docs` 重新生成 `api-reference.html`
> - 契约冻结范围：`/api/v1` 前缀路径不变；字段/枚举变更 MUST 遵循「新增+兼容窗口+弃用+移除」四阶段

---

## 快速索引

| 章节 | 主题 | 概述 | 代码位置 |
|------|------|------|----------|
| **§1 契约来源** | 基线文件 + 查看器 | `openapi.baseline.json` + ReDoc HTML | 仓库根 `openapi.baseline.json`、`docs/api-reference.html` |
| **§2 基础信息** | 路径/认证/格式 | `/api/v1`、OAuth2PasswordBearer、camelCase | `app/api/v1/`、`app/core/deps.py` |
| **§3 契约变更流程** | 5 步操作序列 | check → baseline → gen-docs → commit → review | `make contract-check`、`make contract-baseline`、`make gen-api-docs` |

---

## §1 契约来源

| 项 | 值 |
|----|----|
| **权威基线** | `openapi.baseline.json`（仓库根，契约冻结基线，由 `make contract-baseline` 导出） |
| **交互式查看器** | [api-reference.html](api-reference.html) —— ReDoc 查看器，由基线经 `make gen-api-docs` 真实生成（`@redocly/cli`），**请勿手改** |
| **路由与模块映射** | [RootDoc-ModuleMap.md](RootDoc-ModuleMap.md)（资源名→三端目录映射） |
| **后端接口契约** | [BackDoc-ModuleContracts.md](../CS-Web-Backend/tools/docs/BackDoc-ModuleContracts.md)（模块级路由/鉴权/配置） |

---

## §2 基础信息

| 项 | 值 |
|----|----|
| **基础路径** | `/api/v1` |
| **认证方式** | `OAuth2PasswordBearer`（`Authorization: Bearer <token>`） |
| **传输格式** | `camelCase`（JSON 请求/响应字段） |
| **冻结范围** | 路径前缀 `/api/v1` 不变；字段/枚举变更遵循「新增+兼容+弃用+移除」四阶段 |

---

## §3 契约变更流程

```
1. 修改后端路由 / 模型
2. make contract-check  ← 校验与基线差异
3. 评审通过 → make contract-baseline  ← 刷新 openapi.baseline.json
4. make gen-api-docs  ← 重新生成 api-reference.html
5. 与基线同步提交，走正常 PR Review
```

---

## 自检清单（API 变更时 MUST 逐项核对）

| 检查项 | 命令 / 说明 |
|--------|------------|
| [ ] `make contract-check` 全通过 | 无 diff 或 diff 为预期变更 |
| [ ] `make contract-baseline` 已执行 | `openapi.baseline.json` 已刷新 |
| [ ] `make gen-api-docs` 已执行 | `api-reference.html` 已重新生成 |
| [ ] BackDoc-ModuleContracts.md 已同步 | 模块级接口契约表已更新 |
| [ ] RootDoc-ModuleMap.md 已同步 | 路由归属映射已更新 |
| [ ] 字段兼容策略已评估 | 新增字段有兼容窗口，弃用字段已标注 |
