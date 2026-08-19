#!/usr/bin/env bash
#
# tag_and_release.sh — 发布工具链（F-9：changelog 自动撰写 + 四源版本/代号同步）
#
# 作用：
#   1. 将四源**核心版本号**（pyproject / app/__init__.__version__ / package.json / uv.lock）
#      统一改写为目标核心版本；
#   2. 将发布代号（codename）同步到 package.json("codename") 与 app/__init__.__codename__
#      （代号可为节日标签如「七夕」或 MMDD 日期如「0819」；留空表示纯核心版本）；
#   3. 将 CHANGELOG 的 `## [Unreleased]` 头重命名为 `## [<核心版本>[.<代号>]] - <date>`；
#   4. 跑 `make check-version` 校验四源核心版本 + 代号一致；
#   5. 打印后续打 tag / 推送指令（本脚本**不**自动打 tag、不推送，避免误发）。
#
# 用法：
#   ./scripts/tag_and_release.sh 1.0.1                 # 纯核心版本，无代号
#   ./scripts/tag_and_release.sh 1.0.1 七夕            # 代号「七夕」
#   ./scripts/tag_and_release.sh 1.0.1 0819            # 代号「0819」（MMDD 日期）
#   ./scripts/tag_and_release.sh 1.0.1 七夕 2026-09-01  # 指定日期 + 代号
#   ./scripts/tag_and_release.sh 1.0.1 2026-09-01      # 指定日期，无代号
#
# 版本号规则（2026-08-19 起）：
#   机器版本保持 PEP 440 / semver 合规的三段式（如 1.0.0）；codename 为纯展示的发布代号，
#   拼成 1.0.0.七夕 / 1.0.0.0819。npm / PEP 440 不允许 4 段或非 ASCII，故打包文件只用核心段。
#
# 安全：仅就地改写上述版本文件 + CHANGELOG 头（均 git 跟踪、可 review/回滚）；
#       不删除任何文件、不自动打 tag、不推送远程。
#
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "用法: $0 <core-version> [codename] [date:YYYY-MM-DD]" >&2
  exit 2
fi

VERSION="$1"; shift

# 解析剩余参数：YYYY-MM-DD 视为日期，其余视为 codename
CODENAME=""
DATE=""
for arg in "$@"; do
  if [[ "$arg" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    DATE="$arg"
  else
    CODENAME="$arg"
  fi
done
DATE="${DATE:-$(date +%Y-%m-%d)}"

# 核心版本号必须是严格三段式（codename 单独传，禁止把 1.0.0.七夕 当作核心版本）
if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "错误：核心版本号格式不合法：$VERSION（期望严格三段式如 1.0.0）" >&2
  exit 2
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYPROJECT="$ROOT/CS-Web-Backend/pyproject.toml"
INIT="$ROOT/CS-Web-Backend/app/__init__.py"
PKG="$ROOT/CS-Web-Frontend/package.json"
UVLOCK="$ROOT/CS-Web-Backend/uv.lock"
CHANGELOG="$ROOT/CHANGELOG.md"

DISPLAY="$VERSION"
if [[ -n "$CODENAME" ]]; then
  DISPLAY="$VERSION.$CODENAME"
fi

echo ">>> 核心版本: $VERSION   代号: ${CODENAME:-（无）}   展示版: $DISPLAY   ($DATE)"

# --- 1. 四源核心版本同步 ---
# pyproject.toml: [project] version
perl -i -pe 's/^(version = )"[0-9].*?"$/$1"'"$VERSION"'"  if $. == 3;' "$PYPROJECT"
# app/__init__.py: __version__ = "..."
perl -i -pe 's/^(__version__ = )"[0-9].*?"$/$1"'"$VERSION"'"/' "$INIT"
# package.json: "version": "..."
perl -i -pe 's/^(\s*"version": )"[0-9].*?"(,?)$/$1"'"$VERSION"'"$2/' "$PKG"
# uv.lock: cs-web-backend 包的 version（仅替换紧随 name = "cs-web-backend" 的那一行）
perl -0777 -i -pe 's/(name = "cs-web-backend"\nversion = )"[0-9].*?"/${1}"'"$VERSION"'"/' "$UVLOCK"

echo ">>> 已更新四源核心版本文件"

# --- 2. codename 同步（package.json + __init__，两处须同时设置/清空）---
# package.json: "codename": "..." 存在则替换，否则在 version 行后插入
if grep -q '"codename"' "$PKG"; then
  perl -i -pe "s/(\"codename\": )\"[^\"]*\"/\$1\"$CODENAME\"/" "$PKG"
else
  perl -i -pe "s/(\"version\": \"[^\"]*\",)/\$1\n  \"codename\": \"$CODENAME\",/" "$PKG"
fi
# app/__init__.py: __codename__ = "..." 存在则替换，否则在 __version__ 行后插入
if grep -q '__codename__' "$INIT"; then
  perl -i -pe 's/^(__codename__ = )"[^\"]*"/$1"'"$CODENAME"'"/' "$INIT"
else
  perl -i -pe 's/^(__version__ = )"[^\"]*"/$1"'"$VERSION"'"\n__codename__ = "'"$CODENAME"'"/' "$INIT"
fi

echo ">>> 已同步 codename -> '$CODENAME'"

# --- 3. CHANGELOG 头重命名 ---
if grep -q '^## \[Unreleased\]' "$CHANGELOG"; then
  perl -i -pe "s/^## \[Unreleased\]\$/## [$DISPLAY] - $DATE/" "$CHANGELOG"
  echo ">>> CHANGELOG: [Unreleased] -> [$DISPLAY] - $DATE"
else
  echo "!!! 警告：CHANGELOG 未找到 '## [Unreleased]' 头，跳过重命名（请手动处理）" >&2
fi

# --- 4. 四源一致性自检（核心版本 + 代号）---
echo ">>> 校验四源版本/代号一致（make check-version）"
( cd "$ROOT" && python3 scripts/check/check_version_sync.py )

# --- 5. 后续指令 ---
echo
echo ">>> 发布就绪。请人工复核后执行："
echo "    git add -A && git commit -m \"release: v$DISPLAY\""
echo "    git tag -a v$VERSION -m \"Release v$DISPLAY ($DATE)\""
echo "    git push origin main --tags"
echo "    （CI 将在 push:main 自动跑全栈 E2E 门槛#3 验收）"
