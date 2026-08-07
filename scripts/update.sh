#!/usr/bin/env bash
# =============================================================================
# update.sh —— 根级：轻量更新部署服务
#
# 用法：
#   ./scripts/update.sh              # 自动检测变更的服务并更新
#   ./scripts/update.sh --all        # 强制重建全部服务（不含 db/redis/caddy）
#   ./scripts/update.sh backend      # 仅更新指定服务（backend / frontend / all）
#   ./scripts/update.sh --no-pull    # 跳过 git pull，仅用当前代码重建
#   ./scripts/update.sh --no-cache   # 强制无缓存构建（慢，仅排查问题时用）
#
# 说明：
#   - 基于根 docker-compose.yml，只重建有代码变更的服务，利用 Docker 层缓存加速。
#   - backend 代码变更时自动同时重建 worker（共享构建上下文）。
#   - 更新后自动健康检查（后端 /health + 前端 /api/health）。
#   - 不动 db / redis / caddy（无代码构建，无需重建）。
#
# 前置：
#   - 已完成首次部署（make up），.env 已配置。
#   - 服务器有网络访问（git pull 需要仓库可达）。
# =============================================================================

set -euo pipefail

# ---- 配置 ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"
HEALTH_TIMEOUT=60    # 健康检查轮询超时（秒）
HEALTH_INTERVAL=2    # 轮询间隔（秒）

# ---- 颜色输出 ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${CYAN}>>>${NC} $*"; }
ok()    { echo -e "${GREEN}✓${NC} $*"; }
warn()  { echo -e "${YELLOW}⚠${NC} $*"; }
fail()  { echo -e "${RED}✗${NC} $*" >&2; }

# ---- 参数解析 ----
DO_PULL=true
NO_CACHE=""
TARGET=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-pull)  DO_PULL=false; shift ;;
    --no-cache) NO_CACHE="--no-cache"; shift ;;
    --all)      TARGET="all"; shift ;;
    backend|Backend|BACKEND)     TARGET="backend"; shift ;;
    frontend|Frontend|FRONTEND)  TARGET="frontend"; shift ;;
    -h|--help)
      echo "用法: ./scripts/update.sh [--all | backend | frontend] [--no-pull] [--no-cache]"
      echo ""
      echo "选项:"
      echo "  (无参数)    自动检测变更的服务并更新"
      echo "  --all       强制重建 backend + worker + cs-website"
      echo "  backend     仅更新后端（含 worker）"
      echo "  frontend    仅更新前端"
      echo "  --no-pull   跳过 git pull"
      echo "  --no-cache  无缓存构建（慢）"
      exit 0 ;;
    *)
      fail "未知参数: $1（用 --help 查看用法）"
      exit 1 ;;
  esac
done

cd "$PROJECT_ROOT"

# ---- 前置检查 ----
if [[ ! -f "$COMPOSE_FILE" ]]; then
  fail "未找到 docker-compose.yml，请在项目根目录执行"
  exit 1
fi

if [[ ! -f "$PROJECT_ROOT/.env" ]]; then
  fail "未找到 .env，请先执行 make setup"
  exit 1
fi

# ---- 检测变更的服务 ----
detect_changes() {
  local changed=()

  if [[ "$DO_PULL" == true ]]; then
    info "拉取最新代码（含 submodule）..."
    # 记录 pull 前的 submodule commit
    local backend_before frontend_before
    backend_before=$(git submodule status CS-Web-Backend 2>/dev/null | awk '{print $1}' || echo "")
    frontend_before=$(git submodule status CS-Web-Frontend 2>/dev/null | awk '{print $1}' || echo "")

    git pull --recurse-submodules --quiet || {
      fail "git pull 失败，请手动解决冲突后重试"
      exit 1
    }

    local backend_after frontend_after
    backend_after=$(git submodule status CS-Web-Backend 2>/dev/null | awk '{print $1}' || echo "")
    frontend_after=$(git submodule status CS-Web-Frontend 2>/dev/null | awk '{print $1}' || echo "")

    if [[ "$backend_before" != "$backend_after" ]]; then
      changed+=("backend")
      ok "检测到 CS-Web-Backend 代码变更"
    else
      info "CS-Web-Backend 无变更"
    fi

    if [[ "$frontend_before" != "$frontend_after" ]]; then
      changed+=("frontend")
      ok "检测到 CS-Web-Frontend 代码变更"
    else
      info "CS-Web-Frontend 无变更"
    fi
  else
    info "跳过 git pull（--no-pull）"
    changed+=("backend" "frontend")
  fi

  # 输出结果
  echo "${changed[@]}"
}

# ---- 确定要构建的服务 ----
BUILD_SERVICES=""

if [[ -n "$TARGET" ]]; then
  case "$TARGET" in
    all)
      BUILD_SERVICES="backend worker cs-website"
      info "强制重建全部服务"
      ;;
    backend)
      BUILD_SERVICES="backend worker"
      info "仅更新后端（含 worker）"
      ;;
    frontend)
      BUILD_SERVICES="cs-website"
      info "仅更新前端"
      ;;
  esac
else
  info "自动检测变更..."
  mapfile -t CHANGED < <(detect_changes)

  for svc in "${CHANGED[@]}"; do
    case "$svc" in
      backend)  BUILD_SERVICES="$BUILD_SERVICES backend worker" ;;
      frontend) BUILD_SERVICES="$BUILD_SERVICES cs-website" ;;
    esac
  done

  BUILD_SERVICES=$(echo "$BUILD_SERVICES" | xargs)  # 去首尾空格
fi

if [[ -z "$BUILD_SERVICES" ]]; then
  ok "无服务代码变更，无需更新"
  exit 0
fi

info "将重建服务: ${BUILD_SERVICES}"

# ---- 构建 ----
info "构建镜像（利用 Docker 层缓存）..."
docker compose -f "$COMPOSE_FILE" build $NO_CACHE $BUILD_SERVICES

# ---- 启动新容器 ----
info "切换到新容器..."
docker compose -f "$COMPOSE_FILE" up -d $BUILD_SERVICES

# ---- 健康检查 ----
check_health() {
  local service="$1"
  local check_cmd="$2"
  local label="$3"
  local elapsed=0

  echo -n "  等待 ${label} 就绪"
  while [[ $elapsed -lt $HEALTH_TIMEOUT ]]; do
    if docker compose -f "$COMPOSE_FILE" exec -T "$service" $check_cmd >/dev/null 2>&1; then
      echo ""
      ok "${label} 健康"
      return 0
    fi
    echo -n "."
    sleep $HEALTH_INTERVAL
    elapsed=$((elapsed + HEALTH_INTERVAL))
  done
  echo ""
  fail "${label} 健康检查超时（${HEALTH_TIMEOUT}s）"
  return 1
}

info "健康检查..."

# 后端 /health（容器内 curl）
if echo "$BUILD_SERVICES" | grep -qw "backend"; then
  check_health "backend" \
    "python -c \"import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).status==200 else 1)\"" \
    "后端" || warn "后端健康检查未通过，请检查日志: docker compose logs backend"
fi

# 前端 /api/health（容器内 curl，转发到后端 /health）
if echo "$BUILD_SERVICES" | grep -qw "cs-website"; then
  check_health "cs-website" \
    "sh -c 'curl -sf http://127.0.0.1:2333/api/health >/dev/null'" \
    "前端" || warn "前端健康检查未通过，请检查日志: docker compose logs cs-website"
fi

# ---- 总结 ----
echo ""
ok "更新完成！"
info "已更新: ${BUILD_SERVICES}"
echo ""
echo "  查看日志:   docker compose logs -f"
echo "  查看状态:   docker compose ps"
echo "  手动回滚:   git -C CS-Web-Backend checkout <旧commit> && docker compose build backend worker && docker compose up -d backend worker"
