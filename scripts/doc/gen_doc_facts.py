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
def _revision_pair(text: str) -> tuple[str, str | None] | None:
    "从迁移文件文本提取 (revision, down_revision)。down_revision 兼容 docstring Revises: 与 Python 属性。"
    rm = re.search(r"Revision ID:\s*(\S+)", text)
    if not rm:
        return None
    rid = rm.group(1)
    down: str | None = None
    dm = re.search(r"Revises:\s*([^\s]+)", text)
    if dm:
        down = None if dm.group(1) in ("None", "") else dm.group(1)
    else:
        dm2 = re.search(r"down_revision\s*[^=]*=\s*['\"]([^'\"]+)['\"]", text)
        if dm2:
            down = dm2.group(1)
    return rid, down


def alembic_head() -> str:
    """从 alembic/versions/*.py 解析 revision/down_revision 图，返回 head（无子节点者）。"""
    versions = (BACKEND / "alembic" / "versions").glob("*.py")
    has_child: set[str] = set()
    all_revs: set[str] = set()
    for f in versions:
        pair = _revision_pair(f.read_text(encoding="utf-8", errors="ignore"))
        if not pair:
            continue
        rid, down = pair
        all_revs.add(rid)
        if down:
            has_child.add(down)  # down 是某个节点的父（有子）
    heads = sorted(r for r in all_revs if r not in has_child)
    # 线性链约定：多 head 时选「最近的」——以 Create Date 最新者（见 Alembic 单一 head 约定）
    if not heads:
        return ""
    if len(heads) == 1:
        return heads[0]
    return heads[-1]  # 兜底：取字典序最大；正常应单 head


# ---- 需要同步 head 的文档行 ----
HEAD_TARGETS = [
    ROOT / "docs/RootDoc-Deploy.md",
    ROOT / "docs/RootDoc-MigEval.md",
    BACKEND / "tools/docs/BackDoc-Infra.md",
    BACKEND / "tools/docs/BackDoc-01-Arch.md",
]


def sync_alembic_head(head: str, check_only: bool) -> int:
    "替换各目标文档中的 head 引用。返回改动处数。"
    changed = 0
    for path in HEAD_TARGETS:
        if not path.exists():
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
        if not check_only and changed_lines_needed(out, text):
            path.write_text("".join(out), encoding="utf-8")
        # 供外层判断：与实际比较在新旧函数内处理
    return changed


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
    contract = contract_resources()
    backend = {d for d in module_dirs("backend") if d != "tools"}  # tools 为子域包
    tools_path = BACKEND / "app/api/v1/tools"
    tools_sub = {d.name for d in tools_path.glob("*") if d.is_dir() and not d.name.startswith(("__", "."))} if tools_path.is_dir() else set()
    backend |= tools_sub
    frontend = module_dirs("frontend")
    mobile = module_dirs("mobile")
    lines: list[str] = []
    for kind, mods in (("backend", backend), ("frontend", frontend), ("mobile", mobile)):
        extra = sorted(mods - contract)
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
    head = alembic_head()
    print(f"=== DOC-FACTS（head={head}，dry-run={check_only}）===")

    changed = 0
    if check_only:
        print(f"[alembic head] 当前 = {head}")
    else:
        changed = sync_alembic_head(head, check_only=False)
        print(f"[alembic head] 同步文档改动 {changed} 行")

    bad = check_versions()
    print("[version] " + ("OK（四处一致）" if not bad else f"不一致: {', '.join(bad)}"))

    mod = check_modules()
    print("[modules]" + ("" if not mod else "\n" + "\n".join(mod)))
    if not mod:
        print("  OK（三端模块 ⊆ 契约资源）")

    print("[tests]")
    for t in check_tests():
        print(t)

    if check_only:
        print("\n(--dry-run 未改写文档)")

    bare = head and not bad and not mod
    return 0 if bare else 2 if (bad or mod) else 0


if __name__ == "__main__":
    sys.exit(main())