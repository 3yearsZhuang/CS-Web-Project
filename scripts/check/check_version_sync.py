#!/usr/bin/env python3
"""校验项目版本号四源一致（ER-33）。

版本号单一事实来源须同步于以下四处，任一不一致即视为错误并退出码 1：
  1. CS-Web-Backend/pyproject.toml         -> [project].version
  2. CS-Web-Backend/app/__init__.py        -> __version__
  3. CS-Web-Frontend/package.json          -> version
  4. CS-Web-Backend/uv.lock                -> 包 cs-web-backend 的 version

仅依赖标准库（tomllib 需 Python >= 3.11，与项目 requires-python 一致）。
适配 CI：exit code 非 0 即失败。
"""
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _read_pyproject() -> str:
    with open(ROOT / "CS-Web-Backend" / "pyproject.toml", "rb") as f:
        data = tomllib.load(f)
    return str(data["project"]["version"])


def _read_init_version() -> str:
    text = (ROOT / "CS-Web-Backend" / "app" / "__init__.py").read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if not m:
        raise RuntimeError("app/__init__.py 未找到 __version__")
    return m.group(1)


def _read_package_json() -> str:
    data = json.loads(
        (ROOT / "CS-Web-Frontend" / "package.json").read_text(encoding="utf-8")
    )
    return str(data["version"])


def _read_uvlock_package() -> str:
    with open(ROOT / "CS-Web-Backend" / "uv.lock", "rb") as f:
        data = tomllib.load(f)
    for pkg in data.get("package", []):
        if pkg.get("name") == "cs-web-backend":
            return str(pkg["version"])
    raise RuntimeError("uv.lock 未找到包 cs-web-backend")


def main() -> int:
    sources = {
        "pyproject.toml [project].version": _read_pyproject(),
        "app/__init__.py __version__": _read_init_version(),
        "package.json version": _read_package_json(),
        "uv.lock (cs-web-backend)": _read_uvlock_package(),
    }

    distinct = set(sources.values())
    if len(distinct) == 1:
        (version,) = distinct
        print(f"[版本校验通过] 四源一致 = {version}")
        return 0

    print("[版本校验失败] 四源版本号不一致：", file=sys.stderr)
    for label, value in sources.items():
        marker = "  " if value == next(iter(distinct)) else "!!"
        print(f"  {marker} {label} = {value}", file=sys.stderr)
    print(
        "请同步更新：pyproject.toml / app/__init__.py / package.json / uv.lock"
        "（cs-web-backend）四处版本号。",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
