#!/usr/bin/env python3
"""派生事实自动同步（降低代码变更后的文档维护成本）。

用法:
    python scripts/doc/gen_doc_facts.py           # 同步派生事实到文档 + 打印报告
    python scripts/doc/gen_doc_facts.py --dry-run # 只打印报告，不改写文档

派生并同步的事实:
    1) Alembic head —— 从 CS-Web-Backend/alembic/versions 计算 head，替换文档中硬编码 head
    2) 版本四处同步 —— 校验 pyproject/__init__/package.json/uv.lock 一致
    3) 三端模块 ↔ 契约 —— 对比 openapi.baseline.json 与三端 modules/ 目录，报告越界
    4) 测试存在性 —— 扫描后端 tools/tests 与前端 src test 文件，报告缺失（供待办参考）

设计要点:
    - 只对"含 head 标记 且 恰好一处 12 位 hex"的行做替换 → 幂等且不会误伤迁移清单多 hex 行。
    - 不涉及 git 操作；由调用方决定如何提交。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # 项目根
BACKEND = ROOT / "CS-Web-Backend"
FRONTEND = ROOT / "CS-Web-Frontend"
MOBILE = ROOT / "CS-Mobile"

HEX12 = r"[0-9a-f]{12}"
# 行内包含这些标记之一且恰好一个 hex → 视为"head 引用"，同步替换
HEAD_MARKERS = re.compile(r"(单一\s*head|head\s*[为=]|最新含|Alembic head|迁移.*head)")
HEAD_LINE = re.compile(HEX12)


def resolve(rel: str) -> Path:
    return (ROOT / rel) if rel.startswith(("docs", "scripts")) else ROOT / rel


# ---- 1) Alembic head ----
# 解析口径（2026-11 修复）：revision / down_revision 必须以 **Python 模块属性**为准，
# 不能依赖 docstring 里的「Revision ID: / Revises:」。历史教训：9 个新迁移只写了
# 属性、没写 docstring，旧实现直接跳过它们 → 报告 head=f7a8b9c0d1e2（真实 f4a5b6c7d8e9），
# 且多 head 时「取字典序最大」把分叉错误静默吞掉。故：
#   1) 属性优先，docstring 仅作属性缺失时的兜底；
#   2) 一个迁移文件解析不出 revision → 直接判定事实不可信（fail closed）；
#   3) head 数 ≠ 1 → 判定迁移分叉（fail closed），不再挑选。
_REVISION_ATTR = re.compile(
    r"^[ \t]*revision[ \t]*(?::[^=\n]+)?=[ \t]*['\"]([0-9a-zA-Z_]+)['\"]", re.M
)
_DOWN_ATTR = re.compile(r"^[ \t]*down_revision[ \t]*(?::[^=\n]+)?=[ \t]*(.+)$", re.M)


def _parse_down(raw: str) -> tuple[list[str], bool]:
    """解析 down_revision 赋值右侧。返回 (父 revision 列表, 是否合法)。

    合法形态：None / "abc" / ("a", "b") / ["a", "b"]。
    **merge 节点必须返回全部父**——只取第一个父会把第二个父误判成 head
    （进而把合法合并节点报成「迁移链分叉」）。
    """
    rhs = raw.split("#", 1)[0].strip()
    if rhs in ("None", ""):
        return [], True
    single = re.fullmatch(r"['\"]([0-9a-zA-Z_]+)['\"]", rhs)
    if single:
        return [single.group(1)], True
    seq = re.fullmatch(r"[\(\[]\s*(.*?)\s*[\)\]]", rhs, re.S)
    if seq:
        items = re.findall(r"['\"]([0-9a-zA-Z_]+)['\"]", seq.group(1))
        return items, True
    return [], False


def _revision_pair(text: str) -> tuple[tuple[str, list[str]], str | None]:
    """提取 (revision, [down_revision...]) 与文件内解析问题描述（None 表示正常）。

    down_revision 支持多父（merge 节点），因此返回列表而非单值。
    """
    rid: str | None = None
    m = _REVISION_ATTR.search(text)
    if m:
        rid = m.group(1)
    else:
        dm = re.search(r"Revision ID:\s*(\S+)", text)
        if dm:
            rid = dm.group(1)
    if not rid:
        return ("", []), "缺少 revision（属性与 docstring 均未找到）"

    downs: list[str] = []
    d = _DOWN_ATTR.search(text)
    if d:
        parents, ok = _parse_down(d.group(1))
        if not ok:
            return (rid, downs), f"down_revision 形态无法解析: {d.group(1).strip()[:60]}"
        downs.extend(parents)
    else:
        dm = re.search(r"Revises:\s*([^\s]+)", text)  # docstring 兜底
        if dm and dm.group(1) not in ("None", ""):
            downs.append(dm.group(1))
    return (rid, downs), None


def alembic_heads() -> tuple[list[str], list[str]]:
    """从 alembic/versions/*.py 建 revision 图，返回 (heads, problems)。

    problems 非空（解析失败）或多 head，均由调用方判定为事实不可信。
    """
    has_child: set[str] = set()
    all_revs: set[str] = set()
    problems: list[str] = []
    for f in sorted((BACKEND / "alembic" / "versions").glob("*.py")):
        pair, err = _revision_pair(f.read_text(encoding="utf-8", errors="ignore"))
        rid, downs = pair
        if err:
            problems.append(f"{f.name}: {err}")
            continue
        all_revs.add(rid)
        has_child.update(downs)  # down 是某个节点的父（有子）
    heads = sorted(r for r in all_revs if r not in has_child)
    if not all_revs:
        problems.append("未解析到任何 revision（alembic/versions 为空或全部解析失败）")
    elif len(heads) != 1:
        problems.append(
            "迁移链分叉：head 数为 %d（必须单 head）→ %s" % (len(heads), ", ".join(heads))
        )
    return heads, problems


# ---- 需要同步 head 的文档行 ----
HEAD_TARGETS = [
    ROOT / "docs/RootDoc-Deploy.md",
    ROOT / "docs/RootDoc-MigEval.md",
    BACKEND / "tools/docs/BackDoc-Infra.md",
    BACKEND / "tools/docs/BackDoc-01-Arch.md",
]


def _disp(path: Path) -> str:
    """文档路径展示：仓库内用相对路径，仓库外（测试/临时目录）退回绝对路径。"""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _head_drift(path: Path, head: str) -> list[str]:
    """返回该文档中与当前 head 不一致的行（为空表示已同步）。"""
    if not path.exists():
        return []
    stale: list[str] = []
    for i, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not HEAD_MARKERS.search(ln):
            continue
        hexes = HEAD_LINE.findall(ln)
        # 恰好一个 hex 才算 head 引用；多 hex 行（迁移清单）不参与判定
        if len(hexes) == 1 and hexes[0] != head:
            stale.append(f"{_disp(path)}:{i} 引用 {hexes[0]} ≠ 当前 head {head}")
    return stale


def sync_alembic_head(head: str, check_only: bool) -> tuple[int, list[str]]:
    """替换各目标文档中的 head 引用。返回 (改动处数, 漂移清单)。

    check_only=True 时只报告漂移、不改写文档（供 `make check-doc-facts` 门禁使用）。
    """
    changed = 0
    drift: list[str] = []
    for path in HEAD_TARGETS:
        if not path.exists():
            continue
        if check_only:
            drift.extend(_head_drift(path, head))
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines(keepends=True)
        out: list[str] = []
        for ln in lines:
            if HEAD_MARKERS.search(ln):
                hexes = HEAD_LINE.findall(ln)
                # 仅当恰好一个 hex 且不等于当前 head 才替换（幂等）
                if len(hexes) != 1:
                    out.append(ln)
                    continue
                new_ln = re.sub(HEX12, head, ln)
                if new_ln != ln:
                    changed += 1
                out.append(new_ln)
            else:
                out.append(ln)
        if changed_lines_needed(out, text):
            path.write_text("".join(out), encoding="utf-8")
    return changed, drift


def changed_lines_needed(out: list[str], orig: str) -> bool:
    return "".join(out) != orig


# ---- 2) 版本四处同步 ----
def version_facts() -> dict[str, str]:
    def gv(path: Path, pat: str) -> str:
        try:
            m = re.search(pat, path.read_text(encoding="utf-8"))
        except Exception:
            return ""
        return m.group(1) if m else ""
    return {
        "pyproject": gv(BACKEND / "pyproject.toml", r'version\s*=\s*"([^"]+)"'),
        "__init__": gv(
            BACKEND / "app/__init__.py", r'__version__\s*=\s*"([^"]+)"'
        ),
        "package.json": gv(FRONTEND / "package.json", r'"version"\s*:\s*"([^"]+)"'),
        "uv.lock": (re.search(r'name = "cs-web-backend"[^]]*?version = "([^"]+)"',
                              (BACKEND / "uv.lock").read_text(encoding="utf-8"))
                    or [None, None, None, None]),  # placeholder, 见下
    }


def check_versions() -> list[str]:
    "返回不一致项；空则表示四处一致。"
    v = {}
    v = version_facts()
    # uv.lock 处理简化：直接匹配
    uv = (BACKEND / "uv.lock").read_text(encoding="utf-8")
    m = re.search(r'name = "cs-web-backend"[\s\S]*?version = "([^"]+)"', uv)
    uv_ver = m.group(1) if m else ""
    vals = {k: x for k, x in v.items() if k != "uv.lock"}
    vals["uv.lock"] = uv_ver
    bad = sorted({k: val for k, val in vals.items() if val and val != list(vals.values())[0]}.keys())
    return bad if vals.get("pyproject") else []


# ---- 3) 模块 ↔ 契约 ----
def contract_resources() -> set[str]:
    p = ROOT / "openapi.baseline.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    paths = data.get("paths", {})
    res: set[str] = set()
    for path in paths:
        if path.startswith("/api/v1/"):
            seg = path.split("/")[3]
            if seg == "test":
                continue  # 忽略 /api/v1/test/* 调试路由
            res.add(seg)
    return res


def contract_size() -> tuple[int, int]:
    """返回 (契约路由数, 契约资源数)，口径与 check_module_naming.py 一致。"""
    data = json.loads((ROOT / "openapi.baseline.json").read_text(encoding="utf-8"))
    routes = sum(1 for p in data.get("paths", {}) if p.startswith("/api/v1/"))
    return routes, len(contract_resources())


# 需要在文档中同步的契约规模行：只认带「路由」「个契约资源」后缀的数字，
# 且该行同一句式只出现一次（避免误伤区间 / 迁移清单 / 历史记录）。
ROUTE_COUNT_RE = re.compile(r"\d+(?=\s*路由)")
RESOURCE_COUNT_RE = re.compile(r"\d+(?=\s*个契约资源)")
CONTRACT_SIZE_TARGETS = [ROOT / "docs/RootDoc-ModuleMap.md"]


def _contract_size_drift(routes: int, resources: int) -> list[str]:
    drift: list[str] = []
    for path in CONTRACT_SIZE_TARGETS:
        if not path.exists():
            continue
        for i, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pat, want, label in (
                (ROUTE_COUNT_RE, routes, "路由数"),
                (RESOURCE_COUNT_RE, resources, "资源数"),
            ):
                found = pat.findall(ln)
                if len(found) == 1 and found[0] != str(want):
                    drift.append(
                        f"{_disp(path)}:{i} {label} = {found[0]} ≠ 当前 {want}"
                    )
            if len(ROUTE_COUNT_RE.findall(ln)) > 1:
                drift.append(
                    f"{_disp(path)}:{i} 单行出现多个「路由数」，无法自动同步（需人工改写）"
                )
    return drift


def sync_contract_size(routes: int, resources: int) -> int:
    """把契约规模同步进文档，返回改动处数。"""
    changed = 0
    for path in CONTRACT_SIZE_TARGETS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        out: list[str] = []
        for ln in text.splitlines(keepends=True):
            new = ln
            if len(ROUTE_COUNT_RE.findall(ln)) == 1:
                new = ROUTE_COUNT_RE.sub(str(routes), new)
            if len(RESOURCE_COUNT_RE.findall(ln)) == 1:
                new = RESOURCE_COUNT_RE.sub(str(resources), new)
            if new != ln:
                changed += 1
            out.append(new)
        if changed_lines_needed(out, text):
            path.write_text("".join(out), encoding="utf-8")
    return changed



def module_dirs(kind: str) -> set[str]:
    base = {"backend": BACKEND / "app/api/v1",
            "frontend": FRONTEND / "src/modules",
            "mobile": MOBILE / "src/modules"}[kind]
    if not base.is_dir():
        return set()
    return {d.name for d in base.iterdir()
            if d.is_dir() and not d.name.startswith(("__", "."))}


def check_modules() -> list[str]:
    "返回越界/缺失模块报告行（信息性）。"

    def _matches(name: str, allowed: set[str]) -> bool:
        # 与 check_module_naming.py 同口径：下划线写法与连字符契约资源名等价
        return name in allowed or name.replace("_", "-") in allowed

    contract = contract_resources()
    # 域合并映射与门禁同源，避免两处规则漂移（导入失败时退化为纯资源比对）
    try:
        sys.path.insert(0, str(ROOT / "scripts" / "check"))
        from check_module_naming import DOMAIN_ALIASES  # type: ignore

        allowed = contract | set(DOMAIN_ALIASES)
    except Exception:  # noqa: BLE001 - 文档脚本不应因门禁模块缺失而崩溃
        allowed = contract

    backend = {d for d in module_dirs("backend") if d != "tools"}  # tools 为子域包
    tools_path = BACKEND / "app/api/v1/tools"
    tools_sub = {d.name for d in tools_path.glob("*") if d.is_dir() and not d.name.startswith(("__", "."))} if tools_path.is_dir() else set()
    backend |= tools_sub
    frontend = module_dirs("frontend")
    mobile = module_dirs("mobile")
    lines: list[str] = []
    for kind, mods in (("backend", backend), ("frontend", frontend), ("mobile", mobile)):
        extra = sorted(m for m in mods if not _matches(m, allowed))
        if extra:
            lines.append(f"  [{kind}] 越界(不在契约): {', '.join(extra)}")
    return lines


# ---- 4) 测试存在性 ----
def check_tests() -> list[str]:
    "扫描后端/前端模块测试，报告缺少专属测试的模块（信息性）。"
    lines: list[str] = []
    back_tests = {f.name for f in (ROOT / "CS-Web-Backend/tools/tests").rglob("test_*.py")
                  if "__pycache__" not in f.parts}
    fe_tests = [f for f in (FRONTEND / "src").rglob("*.test.*")
                if re.search(r"\.test\.(ts|tsx)$", f.name) and "__pycache__" not in f.parts]
    # 粗略：后端 services 子包域缺失对应 test_ 前缀
    svc = [d.name for d in (BACKEND / "app/services").glob("*")
           if d.is_dir() and not d.name.startswith(("__", "."))]
    for s in svc:
        if not any(t.startswith(f"test_{s}") for t in back_tests):
            lines.append(f"  [backend] service 域缺测试: {s}")
    lines.append(f"  [frontend] *.test.* 计数: {len(fe_tests)}（模块级缺失见待办 W-6~W-8）")
    return lines


def main() -> int:
    check_only = "--dry-run" in sys.argv
    heads, head_problems = alembic_heads()
    head = heads[0] if len(heads) == 1 else ""
    print(f"=== DOC-FACTS（head={head or '无法确定'}，dry-run={check_only}）===")

    # 事实不可信（解析失败 / 多 head）→ 直接失败，不再"挑一个"继续跑
    if head_problems:
        print("[alembic head] 事实不可信：")
        for p in head_problems:
            print(f"  - {p}")
        return 2

    drift: list[str] = []
    if check_only:
        print(f"[alembic head] 当前 = {head}")
        _, drift = sync_alembic_head(head, check_only=True)
    else:
        changed, _ = sync_alembic_head(head, check_only=False)
        print(f"[alembic head] 同步文档改动 {changed} 行")

    bad = check_versions()
    print("[version] " + ("OK（四处一致）" if not bad else f"不一致: {', '.join(bad)}"))

    mod = check_modules()
    print("[modules]" + ("" if not mod else "\n" + "\n".join(mod)))
    if not mod:
        print("  OK（三端模块 ⊆ 契约资源）")

    routes, resources = contract_size()
    if check_only:
        drift.extend(_contract_size_drift(routes, resources))
    else:
        n = sync_contract_size(routes, resources)
        print(f"[契约规模] {routes} 路由 / {resources} 资源；同步文档改动 {n} 行")
    if check_only:
        print(f"[契约规模] 当前 = {routes} 路由 / {resources} 资源")

    print("[tests]")
    for t in check_tests():
        print(t)

    if drift:
        print("[drift] 文档派生事实与代码不一致：")
        for d in drift:
            print(f"  - {d}")

    if check_only:
        print("\n(--dry-run 未改写文档)")

    ok = not bad and not mod and not drift
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())