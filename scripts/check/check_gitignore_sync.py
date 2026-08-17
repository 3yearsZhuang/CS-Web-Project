#!/usr/bin/env python3
"""三份 .gitignore 公共段一致性校验（C-8 / N-04，2026-08-17）。

根 / 后端 / 前端各有一份 .gitignore，公共段必须保持一致（gitignore 不支持 include，
只能「复制 + 校验」防漂移）。本脚本以「公共段关键条目白名单」为锚：对每份 .gitignore
的公共段，断言白名单条目全部存在，缺失即退出码 1。

运行：python3 scripts/check/check_gitignore_sync.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# 公共段关键条目（三份 .gitignore 均须包含；根级额外的 overview.md / *_err.txt 等
# 根专属条目不在此列，属预期差异，不做校验）。
CANONICAL = [
    ".env",
    ".env.local",
    ".env.*.local",
    "*.log",
    ".devlogs/",
    ".dev.pid",
    ".vscode/",
    ".idea/",
    "*.iml",
    "*.swp",
    "*.swo",
    "*~",
    ".codebuddy/",
    ".trae-cn/",
    ".workbuddy/",
    ".DS_Store",
    "Thumbs.db",
    "ehthumbs.db",
    "Desktop.ini",
    "._*",
    "data/",
    "backups/",
    "dump.rdb",
    "*.rdb",
    "appendonlydir/",
]

TARGETS = [
    ("根", ROOT / ".gitignore"),
    ("后端", ROOT / "CS-Web-Backend" / ".gitignore"),
    ("前端", ROOT / "CS-Web-Frontend" / ".gitignore"),
]


def _public_section(text: str) -> set[str]:
    """提取公共段：从含「公共段」的标题行起，到下一个含「专属段」的标题行止。"""
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if "公共段" in l), 0)
    end = next(
        (i for i, l in enumerate(lines[start + 1 :], start + 1) if "专属段" in l),
        len(lines),
    )
    return {
        l.strip()
        for l in lines[start + 1 : end]
        if l.strip() and not l.startswith("#")
    }


def main() -> int:
    failed = False
    for label, path in TARGETS:
        if not path.exists():
            print(f"[{label}] 缺失文件: {path}")
            failed = True
            continue
        section = _public_section(path.read_text(encoding="utf-8"))
        missing = [e for e in CANONICAL if e not in section]
        if missing:
            failed = True
            print(f"[{label}] 公共段缺失 {len(missing)} 项: {missing}")
        else:
            print(f"[{label}] 公共段 OK（{len(CANONICAL)} 项全齐）")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
