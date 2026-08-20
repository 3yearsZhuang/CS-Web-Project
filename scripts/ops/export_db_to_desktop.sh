#!/usr/bin/env bash
# =============================================================================
# export_db_to_desktop.sh —— 根级：导出开发环境 PostgreSQL 备份到用户桌面
#
# 用法：
#   ./scripts/db/export_db_to_desktop.sh                  # 默认导出到 ~/Desktop
#   ./scripts/db/export_db_to_desktop.sh /自定义/目录      # 指定输出目录
#
# 说明：
#   - 复用 CS-Web-Backend/tools/scripts/backup_db.sh 的备份逻辑（pg_dump 自定义格式 + gzip）。
#   - 连接参数取自根 .env（DATABASE_HOST / PORT / NAME / USER / PASSWORD）。
#   - 开发环境通常 DATABASE_HOST=localhost（见 Makefile 注释），docker-compose 内为 db。
#   - 导出文件：<桌面>/domefff_<时间戳>.sql.gz
#
# 前置：
#   - 本机已安装 postgresql 客户端（pg_dump / gzip）。
#   - 开发库正在运行（本地 PG 或 docker compose 的 db 服务）。
# =============================================================================

set -euo pipefail

# ---- 路径定位 ----
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="${REPO_ROOT}/.env"

# ---- 加载环境变量（根 .env）----
if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
else
  echo "[错误] 未找到根 .env（请先 make setup 生成并填写 DATABASE_PASSWORD）" >&2
  exit 1
fi

DB_HOST_OVERRIDE="${DATABASE_HOST_OVERRIDE:-}"
DB_HOST="${DB_HOST_OVERRIDE:-${DATABASE_HOST:-localhost}}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_NAME="${DATABASE_NAME:-domefff}"
DB_USER="${DATABASE_USER:-postgres}"
DB_PASSWORD="${DATABASE_PASSWORD:?请在 .env 中设置 DATABASE_PASSWORD}"

# 容器内服务名（db）在宿主机不可直连：若 .env 是 db 且未显式 override，回退 localhost。
# 也可用 env DATABASE_HOST_OVERRIDE=localhost 强制指定。
if [[ -z "$DB_HOST_OVERRIDE" && "$DATABASE_HOST" == "db" ]]; then
  echo "[信息] .env 中 DATABASE_HOST=db（容器服务名），宿主机不可直连，回退到 localhost"
  DB_HOST="localhost"
fi

# ---- 输出目录：默认桌面 ----
DESKTOP_DIR="$HOME/Desktop"
OUT_DIR="${1:-$DESKTOP_DIR}"

if [[ ! -d "$OUT_DIR" ]]; then
  echo "[信息] 输出目录 $OUT_DIR 不存在，自动创建"
  mkdir -p "$OUT_DIR"
fi

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${OUT_DIR}/${DB_NAME}_${TIMESTAMP}.sql.gz"

echo "[导出] 数据库 $DB_NAME @ ${DB_HOST}:${DB_PORT} -> $BACKUP_FILE"

# ---- 执行备份（自定义格式 + gzip，与 backup_db.sh 一致）----
PGPASSWORD="$DB_PASSWORD" pg_dump \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  --no-owner \
  --no-privileges \
  --format=custom \
  --verbose \
  2>"${BACKUP_FILE%.sql.gz}.err" | gzip > "$BACKUP_FILE"

# ---- 完整性校验 ----
if gzip -t "$BACKUP_FILE" 2>/dev/null; then
  echo "[校验] gzip 完整性检查通过"
else
  echo "[错误] gzip 完整性检查失败，备份可能损坏: $BACKUP_FILE" >&2
  exit 1
fi

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[完成] 已导出: $BACKUP_FILE ($BACKUP_SIZE)"
echo "[摘要] 数据库=$DB_NAME 文件=$BACKUP_FILE 大小=$BACKUP_SIZE"
