#!/usr/bin/env python3
"""文档死链审计（ER-09）：可复现的 PR 门禁脚本。

扫描仓库内 Markdown 文档的内部链接，报告：
- 断文件链接（指向不存在的本地 .md / 资源）——硬性错误，退出码 1。
- 缺失锚点（#anchor 在目标文件中找不到对应标题）——启发式，默认警告；
  仅当 ``--strict-anchors`` 时计为错误（避免 CJK 标题 slug 近似导致误杀）。

仅依赖标准库，CI 无需额外安装。用法：

    python3 scripts/check/check_dead_links.py                 # 扫描 ./docs 与根级 *.md
    python3 scripts/check/check_dead_links.py --root . --strict-anchors
    python3 scripts/check/check_dead_links.py --docs docs --base .

链接解析规则：
- http(s):// 外链跳过（不审计可达性）。
- 相对路径基于「当前文件所在目录」解析；以 ``/`` 开头基于仓库根。
- 锚点 slug 近似 GitHub/CommonMark：小写拉丁、空格转连字符、保留 CJK 与
  ``-_``，去除其余标点；标题归一化后比对。
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 匹配行内链接 [text](target) 与参考式定义 [text]: target
LINK_RE = re.compile(r"\[[^\]]*\]\(\s*(?P<target>[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
REF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(?P<target>\S+)", re.MULTILINE)

# 匹配 Markdown 标题（# Title），含可能的尾随 {#custom-anchor}
HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.*?)\s*#*\s*$", re.MULTILINE)
CUSTOM_ANCHOR_RE = re.compile(r"\{#(?P<anchor>[^}]+)\}\s*$")


def slugify(text: str) -> str:
    """近似 GitHub 标题 slug。"""
    text = CUSTOM_ANCHOR_RE.sub("", text).strip()
    out: list[str] = []
    for ch in text.lower():
        if ch.isspace():
            out.append("-")
        elif ch.isalnum() or ch in "-_" or "一" <= ch <= "鿿":
            out.append(ch)
        # 其余标点直接丢弃
    s = "".join(out)
    # 折叠连续连字符
    while "--" in s:
        s = s.replace("--", "-")
    return s.strip("-")


def extract_heading_anchors(md_text: str) -> set[str]:
    """返回文件中所有标题对应的锚点集合（含自定义 {anchor}）。"""
    anchors: set[str] = set()
    for m in HEADING_RE.finditer(md_text):
        title = m.group("title").strip()
        custom = CUSTOM_ANCHOR_RE.search(title)
        if custom:
            anchors.add(custom.group("anchor").strip())
        else:
            anchors.add(slugify(title))
    return anchors


def iter_md_files(base: Path, docs_dir: Path) -> list[Path]:
    files: list[Path] = []
    if docs_dir.is_dir():
        files.extend(sorted(docs_dir.rglob("*.md")))
    # 根级 .md
    files.extend(sorted(base.glob("*.md")))
    # 去重（根级可能也被 rglob 覆盖时）
    seen = set()
    uniq: list[Path] = []
    for f in files:
        rp = f.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(f)
    return uniq


def audit(base: Path, docs_dir: Path, strict_anchors: bool) -> tuple[int, int]:
    errors = 0
    warnings = 0
    md_files = iter_md_files(base, docs_dir)

    # 预构建：文件 -> 锚点集合
    anchors_cache: dict[Path, set[str]] = {}
    for f in md_files:
        try:
            anchors_cache[f] = extract_heading_anchors(f.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] 无法读取 {f}: {exc}", file=sys.stderr)
            anchors_cache[f] = set()

    for f in md_files:
        try:
            text = f.read_text(encoding="utf-8")
        except Exception:
            continue
        for rx in (LINK_RE, REF_RE):
            for m in rx.finditer(text):
                target = m.group("target").strip()
                # 跳过外链与纯锚点（同文件锚点不跨文件审计）
                if target.startswith(("http://", "https://", "mailto:")):
                    continue
                if target.startswith("#"):
                    anchor = target[1:]
                    if anchor and anchor not in anchors_cache.get(f, set()):
                        msg = f"{f}: 锚点未找到 #{anchor}"
                        if strict_anchors:
                            print(f"[error] {msg}", file=sys.stderr)
                            errors += 1
                        else:
                            print(f"[warn] {msg}", file=sys.stderr)
                            warnings += 1
                    continue

                # 拆分 path 与 anchor
                path_part, _, anchor_part = target.partition("#")
                if path_part.startswith("/"):
                    resolved = (base / path_part.lstrip("/")).resolve()
                else:
                    resolved = (f.parent / path_part).resolve()
                if not resolved.exists():
                    print(
                        f"[error] {f}: 断链接 {target} -> {resolved}",
                        file=sys.stderr,
                    )
                    errors += 1
                    continue
                if anchor_part and resolved in anchors_cache:
                    if anchor_part not in anchors_cache[resolved]:
                        msg = f"{f}: 锚点未找到 {target}"
                        if strict_anchors:
                            print(f"[error] {msg}", file=sys.stderr)
                            errors += 1
                        else:
                            print(f"[warn] {msg}", file=sys.stderr)
                            warnings += 1

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Markdown 文档死链审计")
    parser.add_argument("--base", default=".", help="仓库根目录（默认当前目录）")
    parser.add_argument("--docs", default="docs", help="文档目录（默认 docs）")
    parser.add_argument(
        "--strict-anchors",
        action="store_true",
        help="将缺失锚点也计为错误（默认仅警告）",
    )
    args = parser.parse_args()

    base = Path(args.base).resolve()
    docs_dir = base / args.docs
    print(f"[info] 扫描文档：{docs_dir} + 根级 *.md", file=sys.stderr)
    errors, warnings = audit(base, docs_dir, args.strict_anchors)
    print(
        f"[info] 完成：{errors} 个错误，{warnings} 个警告",
        file=sys.stderr,
    )
    if errors:
        print(f"[fail] 发现 {errors} 个死链，门禁不通过。", file=sys.stderr)
        return 1
    print("[ok] 未发现断文件链接。", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
