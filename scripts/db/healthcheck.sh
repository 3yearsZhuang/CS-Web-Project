#!/usr/bin/env bash
# =============================================================================
# healthcheck.sh —— 根级：定时自检脚本
#
# 用法：
#   ./scripts/db/healthcheck.sh                # 执行全部检查，失败项输出红色，全部通过 exit 0
#   ./scripts/db/healthcheck.sh --quiet        # 只输出异常项（用于 cron 静默运行）
#   ./scripts/db/healthcheck.sh --json         # 以 JSON 格式输出检查结果
#   ./scripts/db/healthcheck.sh --only disk,bak # 仅运行指定检查项（逗号分隔）
#
# 检查项（对齐 RootDoc-Deploy.md §七 告警规则）：
#   container  所有 compose 服务容器状态为 Up/healthy
#   health     后端 /health + /readyz，前端 /api/health 返回 200
#   endpoints  核心端点无 5xx（最近 100 条日志聚合）
#   disk       磁盘使用率 < 85%
#   bak        最近 26h 内有新的备份文件
#   logerr     最近 1 小时 ERROR 日志数量与摘要
#
# 使用场景：
#   1. 手动巡检：./scripts/db/healthcheck.sh
#   2. 定时自检：加入宿主机 crontab 或 compose sidecar
#   3. 告警触发：有失败项时 exit 非 0，配合 cron MAILTO/外部告警
# =============================================================================

set -uo pipefail

# ---- 配置 ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.yml"

# ---- 共享健康探测（lib/health-probe.sh）----
# shellcheck source=lib/health-probe.sh
source "$SCRIPT_DIR/lib/health-probe.sh"

# 阈值
DISK_USAGE_THRESHOLD=85       # 磁盘使用率告警阈值 %
BACKUP_MAX_AGE_HOURS=26       # 备份最大老化（小时，含 2h 缓冲）
LOGERR_WINDOW_MIN=60          # ERROR 日志窗口（分钟）
LOGERR_WARN_COUNT=10          # 窗口内 ERROR 数量告警阈值
HEALTH_CONNECT_TIMEOUT=5      # 健康端点连接超时（秒）
ERROR_LOG_TAIL=100            # 检查 5xx 时 tail 的日志条数

# 输出格式
QUIET=false
JSON=false
ONLY=""

# 统计
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
JSON_RESULTS="[]"

# ---- 颜色 ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

info()   { $QUIET || echo -e "${CYAN}>>>${NC} $*"; }
ok()     { $QUIET || echo -e "  ${GREEN}✓${NC} $*"; }
warn()   { echo -e "  ${YELLOW}!${NC} $*" >&2; }
fail()   { echo -e "  ${RED}✗${NC} $*" >&2; }
banner() { $QUIET || echo -e "\n${BOLD}${1}${NC}"; }

# ---- 参数解析 ----
while [[ $# -gt 0 ]]; do
  case "$1" in
    --quiet|-q)   QUIET=true; shift ;;
    --json|-j)    JSON=true; shift ;;
    --only|-o)    ONLY="$2"; shift 2 ;;
    --help|-h)
      sed -n '2,30p' "$0" | sed 's/^# \?//'
      exit 0 ;;
    *)
      echo "未知参数: $1（用 --help 查看用法）" >&2
      exit 1 ;;
  esac
done

cd "$PROJECT_ROOT"

# ---- 工具函数 ----
# 追加一条 JSON 结果
json_add() {
  local name="$1" status="$2" detail="$3"
  JSON_RESULTS=$(echo "$JSON_RESULTS" | python3 -c \
    "import sys,json; d=json.load(sys.stdin); d.append({'name':'$name','status':'$status','detail':json.loads('''$(echo "$detail" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')''')}); print(json.dumps(d))")
}

# 检查是否包含某个子检查
has_check() {
  if [[ -z "$ONLY" ]]; then return 0; fi
  [[ ",$ONLY," == *",$1,"* ]]
}

# 记录检查结果
record() {
  local name="$1" status="$2" detail="$3"
  TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
  case "$status" in
    PASS) PASSED_CHECKS=$((PASSED_CHECKS + 1)) ;;
    FAIL) FAILED_CHECKS=$((FAILED_CHECKS + 1)) ;;
    WARN) ;; # 警告不计入失败
  esac
  if $JSON; then
    json_add "$name" "$status" "$detail"
  fi
}

# ---- 检查：容器状态 ----
check_container() {
  has_check "container" || return
  banner "1/6 容器状态"

  local unhealthy=()
  # 取所有容器状态列
  while IFS=$'\t' read -r name state; do
    [[ -z "$name" ]] && continue
    if [[ "$state" == Up*"(healthy)"* ]] || [[ "$state" == Up* ]]; then
      ok "[$name] $state"
    else
      unhealthy+=("$name: $state")
      fail "[$name] $state"
    fi
  done < <(docker compose -f "$COMPOSE_FILE" ps --format '{{.Name}}\t{{.State}}')

  if [[ ${#unhealthy[@]} -eq 0 ]]; then
    record "container" "PASS" "全部容器正常"
  else
    record "container" "FAIL" "${unhealthy[*]}"
  fi
}

# ---- 检查：健康端点 ----
check_health() {
  has_check "health" || return
  banner "2/6 健康端点"

  local failed=()

  # 后端 /health（容器内探测，见 lib/health-probe.sh —— 与 update.sh 共用）
  if docker compose -f "$COMPOSE_FILE" ps backend | grep -q "Up"; then
    if probe_backend_health "$COMPOSE_FILE" "$HEALTH_CONNECT_TIMEOUT"; then
      ok "backend /health → 200"
    else
      fail "backend /health 失败"
      failed+=("backend /health")
    fi
  else
    warn "backend 容器未运行，跳过 /health 检查"
  fi

  # 后端 /readyz（探 DB + Redis）
  if docker compose -f "$COMPOSE_FILE" ps backend | grep -q "Up"; then
    local rz_body
    if rz_body=$(docker compose -f "$COMPOSE_FILE" exec -T backend python -c \
      "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/readyz',timeout=$HEALTH_CONNECT_TIMEOUT).read().decode(),end='')" 2>/dev/null); then
      ok "backend /readyz → ok"
    else
      fail "backend /readyz 失败（DB/Redis 不可达？）"
      failed+=("backend /readyz")
    fi
  fi

  # 前端 /api/health（容器内探测，转发后端 /health，见 lib/health-probe.sh）
  if docker compose -f "$COMPOSE_FILE" ps cs-website | grep -q "Up"; then
    if probe_frontend_health "$COMPOSE_FILE" "$HEALTH_CONNECT_TIMEOUT"; then
      ok "frontend /api/health → 200"
    else
      fail "frontend /api/health 失败（BFF→后端链路不通？）"
      failed+=("frontend /api/health")
    fi
  else
    warn "cs-website 容器未运行，跳过前端检查"
  fi

  if [[ ${#failed[@]} -eq 0 ]]; then
    record "health" "PASS" "全部健康端点正常"
  else
    record "health" "FAIL" "${failed[*]}"
  fi
}

# ---- 检查：核心端点 5xx ----
check_endpoints() {
  has_check "endpoints" || return
  banner "3/6 核心端点 5xx（最近 ${ERROR_LOG_TAIL} 条日志）"

  local errors=()

  for svc in backend cs-website; do
    if ! docker compose -f "$COMPOSE_FILE" ps "$svc" | grep -q "Up"; then
      warn "$svc 未运行，跳过 5xx 检查"
      continue
    fi
    local count
    count=$(docker compose -f "$COMPOSE_FILE" logs --tail "$ERROR_LOG_TAIL" "$svc" 2>/dev/null \
      | grep -cE '"status"[ :]+5[0-9]{2}| status=5[0-9]{2}| 5[0-9]{2} ' || true)
    if [[ "$count" -eq 0 ]]; then
      ok "[$svc] 无 5xx"
    else
      fail "[$svc] 检测到 $count 条 5xx 响应"
      errors+=("$svc:${count}")
    fi
  done

  if [[ ${#errors[@]} -eq 0 ]]; then
    record "endpoints" "PASS" "核心端点无 5xx"
  else
    record "endpoints" "FAIL" "${errors[*]}"
  fi
}

# ---- 检查：磁盘 ----
check_disk() {
  has_check "disk" || return
  banner "4/6 磁盘使用率（阈值 ${DISK_USAGE_THRESHOLD}%）"

  local failed=()
  # 检查项目根所在分区 + Docker 数据根目录（默认 /var/lib/docker）
  for dir in "$PROJECT_ROOT" /var/lib/docker; do
    [[ -e "$dir" ]] || continue

    local line usage mount
    # df 参数在 Linux/macOS 不同，这里用 Posix 默认输出的第五列（pcent）和第六列（mount）
    # 例: Filesystem 1K-blocks Used Available Use% Mounted
    line=$(df -P "$dir" 2>/dev/null | tail -n1)
    if [[ -z "$line" ]]; then
      warn "df -P $dir 失败，跳过"
      continue
    fi
    # Use% 第 5 列；Mount 第 6 列（含空格时 df -P 已把路径在 Filesystem 列用 'shared' 表示，但挂载点仍是最后一列，通常无空格）
    usage=$(echo "$line" | awk '{gsub("%",""); print $5}')
    mount=$(echo "$line" | awk '{print $NF}')

    # 校验 usage 为数字
    if [[ ! "$usage" =~ ^[0-9]+$ ]]; then
      warn "无法解析 $dir 使用率: line=$line"
      continue
    fi

    if [[ "$usage" -lt "$DISK_USAGE_THRESHOLD" ]]; then
      ok "[$mount] ${usage}% < ${DISK_USAGE_THRESHOLD}%"
    else
      fail "[$mount] ${usage}% ≥ ${DISK_USAGE_THRESHOLD}% 告警"
      failed+=("$mount:${usage}%")
    fi
  done

  if [[ ${#failed[@]} -eq 0 ]]; then
    record "disk" "PASS" "磁盘使用率正常"
  else
    record "disk" "FAIL" "${failed[*]}"
  fi
}

# ---- 检查：备份 ----
check_bak() {
  has_check "bak" || return
  banner "5/6 备份新鲜度（${BACKUP_MAX_AGE_HOURS}h 内）"

  # 查找备份文件：根级 backups/ 目录、后端 compose 的 backups 卷挂载路径、根脚本导出目录
  local candidates=(
    "$PROJECT_ROOT/backups"
    "$PROJECT_ROOT/CS-Web-Backend/backups"
    "/opt/cs-backup"
  )

  local newest="" newest_ts=0 found_dir=""
  for dir in "${candidates[@]}"; do
    [[ -d "$dir" ]] || continue
    local f
    while IFS= read -r -d '' f; do
      local ts
      ts=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null || continue)
      if [[ "$ts" -gt "$newest_ts" ]]; then
        newest_ts=$ts
        newest="$f"
        found_dir="$dir"
      fi
    done < <(find "$dir" -maxdepth 2 -type f \( -name "*.sql.gz" -o -name "*.dump" -o -name "*.sql" \) -print0 2>/dev/null)
  done

  if [[ -z "$newest" ]]; then
    warn "未找到备份文件（搜索路径: ${candidates[*]}）—— 如使用 Docker 卷需挂载到宿主"
    record "bak" "WARN" "未找到备份文件"
    return
  fi

  local age_hours
  age_hours=$(( ( $(date +%s) - newest_ts ) / 3600 ))
  if [[ "$age_hours" -le "$BACKUP_MAX_AGE_HOURS" ]]; then
    ok "最新备份: $(basename "$newest") · ${age_hours}h 前 · 目录: $found_dir"
    record "bak" "PASS" "最新备份 ${age_hours}h 前"
  else
    fail "最新备份已 ${age_hours}h 前（超过 ${BACKUP_MAX_AGE_HOURS}h）: $(basename "$newest")"
    record "bak" "FAIL" "最新备份 ${age_hours}h 前"
  fi
}

# ---- 检查：ERROR 日志 ----
check_logerr() {
  has_check "logerr" || return
  banner "6/6 最近 ${LOGERR_WINDOW_MIN} 分钟 ERROR 日志（阈值 ${LOGERR_WARN_COUNT} 条）"

  local total=0
  local samples=()

  for svc in backend cs-website worker caddy; do
    if ! docker compose -f "$COMPOSE_FILE" ps "$svc" | grep -q "Up"; then
      continue
    fi
    # 取日志（自 since=$LOGERR_WINDOW_MIN 分钟前），统计 ERROR 并取前 3 条样例
    local count
    local since="${LOGERR_WINDOW_MIN}m"
    count=$(docker compose -f "$COMPOSE_FILE" logs --since "$since" "$svc" 2>/dev/null \
      | grep -ciE 'level="?error"?|ERROR|Exception|Traceback' || true)
    total=$((total + count))

    if [[ "$count" -gt 0 ]]; then
      local sample
      sample=$(docker compose -f "$COMPOSE_FILE" logs --since "$since" "$svc" 2>/dev/null \
        | grep -iE 'level="?error"?|ERROR|Exception|Traceback' \
        | head -n 3 | sed 's/^/    /')
      samples+=("[$svc] $count 条")
      warn "[$svc] $count 条 ERROR"
      echo -e "${DIM}${sample}${NC}"
    else
      ok "[$svc] 无 ERROR"
    fi
  done

  if [[ "$total" -eq 0 ]]; then
    record "logerr" "PASS" "无 ERROR 日志"
  elif [[ "$total" -lt "$LOGERR_WARN_COUNT" ]]; then
    record "logerr" "WARN" "共 ${total} 条 ERROR（低于告警阈值）"
  else
    record "logerr" "FAIL" "共 ${total} 条 ERROR：${samples[*]}"
  fi
}

# ---- 主流程 ----
main() {
  [[ -f "$COMPOSE_FILE" ]] || { echo "未找到 $COMPOSE_FILE" >&2; exit 1; }

  $QUIET || echo -e "${BOLD}=== FztbuCS-Project 自检 $(date '+%Y-%m-%d %H:%M:%S') ===${NC}"

  check_container
  check_health
  check_endpoints
  check_disk
  check_bak
  check_logerr

  # ---- 总结 ----
  if $JSON; then
    echo "$JSON_RESULTS" | python3 -m json.tool
  fi

  if ! $QUIET && ! $JSON; then
    echo ""
    echo -e "===== 自检总结 ====="
    echo -e "  总检查项: ${BOLD}${TOTAL_CHECKS}${NC}"
    [[ $PASSED_CHECKS -gt 0 ]] && echo -e "  ${GREEN}通过: ${PASSED_CHECKS}${NC}"
    [[ $FAILED_CHECKS -gt 0 ]] && echo -e "  ${RED}失败: ${FAILED_CHECKS}${NC}"
    if [[ $FAILED_CHECKS -gt 0 ]]; then
      echo -e "${RED}  ⚠ 有失败项，请查看上方详情${NC}"
      echo -e "  日志排查:  docker compose logs -f"
      echo -e "  容器状态:  docker compose ps"
    else
      echo -e "  ${GREEN}✓ 全部通过${NC}"
    fi
  fi

  # 有 FAIL（不含 WARN）时 exit 非 0，便于 cron 告警
  [[ $FAILED_CHECKS -eq 0 ]]
}

main "$@"
