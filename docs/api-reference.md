# API 参考（FztbuCS-Project）

> **权威契约**：`openapi.baseline.json`（仓库根，契约冻结基线，由 `make contract-baseline` 导出）。
> **查看器**：[api-reference.html](api-reference.html) —— ReDoc 交互式查看器，由基线经 `make gen-api-docs` 真实生成（`@redocly/cli`），**请勿手改**（历史手写版已于 2026-08-19 移除，手写必然与基线漂移，见 CHANGELOG）。
> 基础路径：`/api/v1`；认证：`OAuth2PasswordBearer`（`Authorization: Bearer <token>`）；传输格式：camelCase。

## 契约变更流程

1. 修改后端路由 / 模型后，`make contract-check` 校验与基线差异；
2. 评审通过后 `make contract-baseline` 刷新 `openapi.baseline.json`；
3. `make gen-api-docs` 重新生成 `docs/api-reference.html`，与基线同步提交。
