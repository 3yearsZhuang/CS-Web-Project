# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Auxilio 学习助手数据访问收敛：`execute_tool` 直连 SQL 迁至新仓储 `app/repositories/auxilio_tool_repo.py`（`AuxilioToolRepository`），行为不变。
- `LLM_DAILY_BUDGET` 落地生效：每日每用户 token 预算拦截（单位：千 tokens/日，默认 200 = 20 万 tokens；0 = 不限制），达上限后停止调用模型并提示，防成本失控。

## [0.9.8]
### Added
- 工作台（Workbench）前端模块：个人待办、番茄钟播放器、GitHub 热力图、API 调用统计、考试倒计时、快捷便签、学习助手对话等 widget（注册表配置驱动）。
- Auxilio 学习助手：基于规则的技能 + 可选 LLM（OpenAI 兼容 / Anthropic 双协议流式），SSE 流式对话，会话持久化。
- 后端 `/api/v1/workbench/*` 与 `/api/v1/auxilio/*` 路由及对应服务（`contribution_service`、`auxilio_agent`、`llm_client`）、`api_usage` 统计中间件。
- 数据表：`contribution_cache`、`api_call_logs`、`conversations`、`chat_messages`、`focus_sessions`。
- 可选 LLM 配置（`LLM_PROVIDER` / `LLM_API_KEY` / `LLM_BASE_URL` / `LLM_MODEL`）。
