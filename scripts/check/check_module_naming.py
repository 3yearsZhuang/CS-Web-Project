#!/usr/bin/env python3
"""check_module_naming.py — 三端业务模块命名与 API 契约对齐校验（2026-08-19 引入，D 方案 CI 固化）

规则（「模块名 = API 资源名」，见待办 SSOT P2-9）：
  1. 从 前端 src/modules/、移动端 src/modules/、后端 app/api/v1/ 收集业务模块名
  2. 与 openapi.baseline.json 中 /api/v1 路径第一段资源名集合比对
  3. 三端模块名必须 ⊆ 契约资源名集合（允许契约有而模块未建，禁止模块名游离于契约外）

特殊情况映射：
  - 后端 admin_*.py 与 password_resets.py → 资源 admin（URL 前缀 /admin/*）
  - 后端 dev_exceptions.py（DEBUG only，不在基线）→ 忽略
  - 后端 api/v1/tools/ 包 → 资源 tools（exam/resource/task/points/component_registry/feature_visibility 为子资源）

退出码：0 通过；1 失败（打印差异，需先入契约或修正模块名）。
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "openapi.baseline.json"


def api_resources() -> set[str]:
    """从冻结基线提取 /api/v1 第一段资源名集合。"""
    spec = json.loads(BASELINE.read_text(encoding="utf-8"))
    segs: set[str] = set()
    for path in spec.get("paths", {}):
        m = re.match(r"^/api/v1/([^/]+)", path)
        if m:
            segs.add(m.group(1))
    return segs


def collect_dir_modules(base: Path) -> set[str]:
    """收集目录下的一级子目录名（模块目录）。"""
    if not base.is_dir():
        return set()
    return {p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")}


def collect_backend_v1() -> set[str]:
    """收集后端 app/api/v1 业务模块（.py 文件名 + tools 包）。"""
    d = ROOT / "CS-Web-Backend" / "app" / "api" / "v1"
    mods: set[str] = set()
    for p in sorted(d.glob("*.py")):
        name = p.stem
        if name == "__init__" or name == "dev_exceptions":
            continue
        if name.startswith("admin_") or name == "password_resets":
            name = "admin"
        mods.add(name)
    if (d / "tools").is_dir():
        mods.add("tools")
    return mods


def main() -> int:
    resources = api_resources()
    fe = collect_dir_modules(ROOT / "CS-Web-Frontend" / "src" / "modules")
    mo = collect_dir_modules(ROOT / "CS-Mobile" / "src" / "modules")
    be = collect_backend_v1()

    errors: list[str] = []
    for label, mods in (("前端 src/modules", fe), ("移动端 src/modules", mo), ("后端 app/api/v1", be)):
        extra = sorted(mods - resources)
        if extra:
            errors.append(f"{label} 存在不在契约中的模块名: {extra}")

    if errors:
        print("[check-module-naming] FAIL")
        for e in errors:
            print("  -", e)
        print(f"  契约资源名（{len(resources)}）: {sorted(resources)}")
        return 1

    print(
        f"[check-module-naming] OK（前端 {len(fe)} / 移动端 {len(mo)} / "
        f"后端 {len(be)} 模块名全部对齐契约，共 {len(resources)} 个资源）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
