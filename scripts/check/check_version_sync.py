#!/usr/bin/env python3
"""校验项目版本号四源一致（ER-33）+ 发布代号（codename）一致。

核心版本号（PEP 440 / semver 合规三段式）单一事实来源须同步于以下四处，任一不一致即退出码 1：
  1. CS-Web-Backend/pyproject.toml         -> [project].version
  2. CS-Web-Backend/app/__init__.py        -> __version__
  3. CS-Web-Frontend/package.json          -> version
  4. CS-Web-Backend/uv.lock                -> 包 cs-web-backend 的 version

发布代号（codename，如 "七夕" / "0819"，纯展示）须同时存在于：
  - CS-Web-Frontend/package.json           -> "codename"
  - CS-Web-Backend/app/__init__.py         -> __codename__
两处须同时设置或同时为空，展示版 = "{核心版本}.{codename}"（如 1.0.0.七夕）。

仅依赖标准库（tomllib 需 Python >= 3.11，与项目 requires-python 一致）。
适配 CI：exit code 非 0 即失败。
"""
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

# 脚本位于 scripts/check/ 下，需向上三级到项目根（2026-08-17 随 scripts 重排修正）。
ROOT = Path(__file__).resolve().parents[2]


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


def _read_pkg_codename() -> str | None:
    data = json.loads(
        (ROOT / "CS-Web-Frontend" / "package.json").read_text(encoding="utf-8")
    )
    val = data.get("codename")
    return val if val else None


def _read_init_codename() -> str | None:
    text = (ROOT / "CS-Web-Backend" / "app" / "__init__.py").read_text(
        encoding="utf-8"
    )
    m = re.search(r'__codename__\s*=\s*"([^"]*)"', text)
    return m.group(1) if (m and m.group(1)) else None


def main() -> int:
    sources = {
        "pyproject.toml [project].version": _read_pyproject(),
        "app/__init__.py __version__": _read_init_version(),
        "package.json version": _read_package_json(),
        "uv.lock (cs-web-backend)": _read_uvlock_package(),
    }

    distinct = set(sources.values())
    if len(distinct) != 1:
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

    (version,) = distinct
    print(f"[版本校验通过] 四源核心版本一致 = {version}")

    # --- codename 一致性 ---
    codenames = {
        "package.json codename": _read_pkg_codename(),
        "app/__init__.py __codename__": _read_init_codename(),
    }
    present = {k: v for k, v in codenames.items() if v is not None}
    if len(present) == 0:
        print("[代号校验] 本次发布无 codename（纯核心版本）")
        return 0
    if len(present) != len(codenames):
        print(
            "[代号校验失败] codename 仅在一处定义，package.json 与 __init__ 必须同时设置或同时为空：",
            file=sys.stderr,
        )
        for label, value in codenames.items():
            print(f"  !! {label} = {value!r}", file=sys.stderr)
        return 1
    if len(set(present.values())) != 1:
        print("[代号校验失败] codename 取值不一致：", file=sys.stderr)
        for label, value in codenames.items():
            print(f"  !! {label} = {value!r}", file=sys.stderr)
        return 1
    (codename,) = set(present.values())
    print(f"[代号校验通过] codename 一致 = {codename!r}（展示版 {version}.{codename}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
