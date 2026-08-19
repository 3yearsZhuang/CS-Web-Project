#!/usr/bin/env bash
#
# clean-artifacts.sh — 安全清理项目构建可再生产物与确定无用文件（范围 A+B）。
#
# 安全设计（防误删跟踪源码，避免 2026-08-19 把 tools/scripts/fe/build 当产物删的事故）：
#   1) 仅针对"构建/缓存/日志/临时"白名单模式，绝不按裸目录名一刀切。
#   2) 对每个候选目标，先确认其【不被 git 跟踪】才删除；被跟踪的（如
#      tools/scripts/fe/build 这类以 build 命名的源码目录）一律 SKIP 并告警。
#   3) 依赖目录 node_modules / .venv 默认不在范围（属 C 类，需 --with-deps 显式开启）。
#   4) 默认 --dry-run 预览；--apply 才真删。强烈建议先 --dry-run 复核再 apply。
#
# 用法：
#   ./scripts/clean-artifacts.sh                      # 预览（dry-run）
#   ./scripts/clean-artifacts.sh --apply              # 真删（A+B）
#   ./scripts/clean-artifacts.sh --apply --with-deps  # 含依赖（C）
#
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

APPLY=0
WITH_DEPS=0
for a in "$@"; do
  case "$a" in
    --apply) APPLY=1 ;;
    --with-deps) WITH_DEPS=1 ;;
    --dry-run) APPLY=0 ;;
    -h|--help) sed -n '3,16p' "$0"; exit 0 ;;
    *) echo "未知参数: $a" >&2; echo "用法: $0 [--dry-run|--apply] [--with-deps]" >&2; exit 2 ;;
  esac
done

mode=$([ "$APPLY" -eq 1 ] && echo APPLY || echo DRY-RUN)

# 找包含某路径的 git 仓库根（兼容 submodule：子模块 .git 为文件也认）
repo_for() {
  local d="$1"
  while [ "$d" != "/" ] && [ -n "$d" ]; do
    if [ -e "$d/.git" ]; then echo "$d"; return 0; fi
    d="$(dirname "$d")"
  done
  return 1
}

# 是否被 git 跟踪（在其所属仓库内判定；submodule 用各自索引）
is_tracked() {
  local p="$1" repo rel
  repo="$(repo_for "$p")" || return 1
  rel="${p#$repo/}"
  git -C "$repo" ls-files --error-unmatch "$rel" >/dev/null 2>&1
}

TOTAL_KB=0

safe_delete() {
  local path="$1"
  if is_tracked "$path"; then
    echo "  SKIP (tracked, 源码不删): $path"
    return
  fi
  if [ ! -e "$path" ]; then return; fi
  local kb
  kb="$(du -sk "$path" 2>/dev/null | cut -f1 || true)"
  kb="${kb:-0}"
  TOTAL_KB=$((TOTAL_KB + kb))
  if [ "$APPLY" -eq 1 ]; then
    rm -rf "$path"
    echo "  DEL [${kb}KB]: $path"
  else
    echo "  (dry-run) DEL [${kb}KB]: $path"
  fi
}

echo "== clean-artifacts ($mode) =="

# 1) 显式构件目录（注意：bare 'build' 故意不列，避免误伤源码；跟踪守卫作兜底）
for d in CS-Web-Frontend/.build CS-Web-Backend/.build .devlogs; do
  safe_delete "$d"
done

# 2) 依赖目录（仅 --with-deps 才纳入）
if [ "$WITH_DEPS" -eq 1 ]; then
  for d in CS-Web-Frontend/node_modules CS-Web-Backend/.venv; do
    safe_delete "$d"
  done
fi

# 3) 目录类缓存（统一排除 .git / node_modules / .venv 内部）
for pat in __pycache__ .pytest_cache .mypy_cache .ruff_cache .uv_cache .coverage .next dist out .turbo; do
  while IFS= read -r p; do
    [ -n "$p" ] && safe_delete "$p"
  done < <(find . -type d -name "$pat" -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' 2>/dev/null)
done

# 4) 文件类（.pyc / .tsbuildinfo / 日志 / 临时 / coverage 文件）
while IFS= read -r p; do
  [ -n "$p" ] && safe_delete "$p"
done < <(find . \( -name '*.pyc' -o -name '*.tsbuildinfo' -o -name '*.log' -o -name '_tmp_*' -o -name '.coverage*' \) -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' 2>/dev/null)

echo "== done (预计释放约 $((TOTAL_KB / 1024))MB$([ "$WITH_DEPS" -eq 0 ] && echo '；依赖 node_modules/.venv 未包含（--with-deps 可含）') =="
