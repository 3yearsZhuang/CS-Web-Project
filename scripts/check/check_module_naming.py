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


# 资源 → 模块 的多对一映射（2026-11 引入）。
# 背景：契约按 URL 资源切分，同一业务域可能铺开成多个并列资源（如 Agent 域 =
# agent-briefing / agent-inbox / agent-rules / agent-weekly-review），而代码按域收敛为
# 一个模块（src/modules/agent/、app/api/v1/agent_*.py）。旧规则「模块名必须等于资源名」
# 对这种形状无解，只能二选一：把域拆成 4 个模块（违背域内聚），或每次新增子资源就让门禁红。
# 新规则：模块集合 ⊆（资源集合 ∪ 映射键集合），映射的取值必须真实存在于契约资源中，
# 即"允许域合并，但不允许凭空造名"。映射本身登记在 RootDoc-ModuleMap.md，此处为机器可读副本。
DOMAIN_ALIASES: dict[str, set[str]] = {
    # 模块名 -> 被它有条件吸收的契约资源
    "agent": {"agent-briefing", "agent-inbox", "agent-rules", "agent-weekly-review"},
}


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

    # 映射健全性：别名吸收的资源必须真实存在（防止改名后映射变成僵尸白名单）
    for alias, absorbed in DOMAIN_ALIASES.items():
        zombie = sorted(absorbed - resources)
        if zombie:
            errors.append(
                f"DOMAIN_ALIASES['{alias}'] 指向不存在的契约资源: {zombie}"
                "（资源改名/删除后须同步更新映射）"
            )

    allowed = resources | set(DOMAIN_ALIASES)

    def _matches(name: str) -> bool:
        """模块名是否落到契约资源或域映射上。

        Python 模块名只能用下划线（`agent_briefing.py`），URL 资源名用连字符
        （`/api/v1/agent-briefing`）——同一资源的两种书写被视为等价。
        """
        return name in allowed or name.replace("_", "-") in allowed

    for label, mods in (("前端 src/modules", fe), ("移动端 src/modules", mo), ("后端 app/api/v1", be)):
        extra = sorted(m for m in mods if not _matches(m))
        if extra:
            errors.append(f"{label} 存在不在契约中的模块名: {extra}")

    if errors:
        print("[check-module-naming] FAIL")
        for e in errors:
            print("  -", e)
        print(f"  契约资源名（{len(resources)}）: {sorted(resources)}")
        print(f"  域合并映射（{len(DOMAIN_ALIASES)}）: {sorted(DOMAIN_ALIASES)}")
        return 1

    print(
        f"[check-module-naming] OK（前端 {len(fe)} / 移动端 {len(mo)} / "
        f"后端 {len(be)} 模块名全部对齐契约，共 {len(resources)} 个资源"
        f" + {len(DOMAIN_ALIASES)} 个域合并映射）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
