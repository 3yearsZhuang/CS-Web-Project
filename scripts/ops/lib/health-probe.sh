#!/usr/bin/env bash
# =============================================================================
# health-probe.sh —— 容器内健康端点探测（共享 lib）
#
# 供 scripts/ops/update.sh（轮询）与 scripts/ops/healthcheck.sh（单次）source 复用。
# 两脚本原各自内联 docker compose exec 探测命令（c146d38 引入重复），收敛于此。
#
# 用法（被调用方 source 后）：
#   probe_backend_health <compose_file> <timeout_s>    # 后端 /health（容器内 127.0.0.1:8000，python urllib）
#   probe_frontend_health <compose_file> <timeout_s>   # 前端 /api/health（容器内 127.0.0.1:2333，curl，转发后端 /health）
#
# 约定：两函数返回 0=健康 / 非0=不健康；stderr 已静默；
#       调用方负责轮询 / 记录 / 超时策略（本 lib 不含业务逻辑）。
# =============================================================================

# 探测后端 /health（与 update.sh/healthcheck.sh 原内联命令行为一致）
probe_backend_health() {
  local compose_file="$1" timeout_s="$2"
  docker compose -f "$compose_file" exec -T backend python -c \
    "import urllib.request,sys; r=urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=${timeout_s}); sys.exit(0 if r.status==200 else 1)" 2>/dev/null
}

# 探测前端 /api/health（BFF 转发后端 /health；curl -sf 静默失败，-m 防悬挂）
probe_frontend_health() {
  local compose_file="$1" timeout_s="$2"
  docker compose -f "$compose_file" exec -T cs-website sh -c \
    "curl -sf -m ${timeout_s} http://127.0.0.1:2333/api/health >/dev/null" 2>/dev/null
}
