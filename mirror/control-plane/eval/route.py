"""Deterministic reviewer router: the code form of agent_routing.json (no LLM, no network).

route(change, routing) -> {"tier": R0..R3, "agents": [...], "flagged": [...], "reasons": {agent: why}}

Implements the per-unit algorithm of the routing file: group D replaces the roster for tests; group A (language lens +
silent-failure-hunter) always applies to code; group B agents fire only on a concrete trigger; S is flag-only; the
E/R/T/N/P groups are never spawned automatically.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DOC_EXT = {".md", ".txt", ".rst", ".adoc"}
RISK_PATH = re.compile(r"(?i)(^|/)(auth|rbac|session|tenan|login|permission|crypto|secret|payments?|ledger|billing|migrations?)")
S_PATH = re.compile(r"(?i)(^|/)(auth|rbac|session|tenan|login|permission|crypto|secret)")
RISK_CONTENT = re.compile(r"(?i)(password|api[_-]?key|jwt|oauth|tenant_id|request\.(json|body)|ElementTree|pickle\.loads|subprocess|eval\(|"
                          r"DROP\s+TABLE|DELETE\s+FROM|ALTER\s+TABLE)")
S_FLAG = re.compile(r"(?i)(ElementTree|lxml|pickle\.loads|yaml\.load\(|subprocess|shell=True|eval\(|requests\.(get|post)\(|"
                    r"tenant_id|Depends\(|Authorization|jwt|password|secret)")


def glob_to_re(glob: str) -> re.Pattern:
    out, i = "", 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif glob.startswith("**", i):
            out += ".*"
            i += 2
        elif glob[i] == "*":
            out += "[^/]*"
            i += 1
        elif glob[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(glob[i])
            i += 1
    return re.compile("^" + out + "$")


def matches_any(path: str, globs: list[str]) -> bool:
    return any(glob_to_re(g).match(path) for g in globs)


def is_doc(path: str) -> bool:
    p = path.lower()
    return Path(p).suffix in DOC_EXT or p.startswith("docs/") or "/docs/" in p


def is_test(path: str) -> bool:
    return matches_any(path, ["tests/**", "test/**", "**/tests/**", "**/test_*.py"])


def trigger_fires(name: str, trig: dict, files: dict[str, str], tags: set[str], unit_kind: str | None) -> str | None:
    req = set(trig.get("stack_tags_required", []))
    if req and not (req & tags):
        return None
    for path, text in files.items():
        if trig.get("paths") and matches_any(path, trig["paths"]):
            return f"path {path} matches {trig['paths']}"
        for imp in trig.get("imports", []):
            if re.search(rf"(?m)^\s*(from|import)\b.*\b{re.escape(imp)}\b", text):
                return f"import of {imp} in {path}"
    rx = trig.get("content_regex")
    if rx:
        need = 3 if "3+" in str(trig.get("threshold", "")) else 1
        hits = sum(len(re.findall(r, t)) for t in files.values() for r in rx)
        if hits >= need:
            return f"{hits} content matches"
    if trig.get("unit_kind") and unit_kind in trig["unit_kind"]:
        return f"unit kind {unit_kind}"
    return None


def route(change: dict, routing: dict) -> dict:
    files: dict[str, str] = change["files"]
    tags = set(change.get("stack_tags", []))
    unit_kind = change.get("unit_kind")
    paths = list(files)
    groups = routing["groups"]
    auto_b = [a for a in groups["B_domain_triggered"]["agents"]]
    never_auto = set(groups["E_deferred_style"]["agents"]) | set(groups["R_reactive_on_failure"]["agents"]) \
        | set(groups["T_task_scoped"]["agents"]) | set(groups["N_recon"]["agents"]) | set(groups["P_planning"]["agents"]) \
        | set(groups["S_opt_in_only"]["agents"])
    reasons: dict[str, str] = {}
    selected: list[str] = []
    flagged: list[str] = []

    if all(is_doc(p) for p in paths):
        return {"tier": "R0", "agents": [], "flagged": [], "reasons": {"*": "documentation-only change"}}

    if all(is_test(p) or is_doc(p) for p in paths):
        for a in groups["D_test"]["agents"]:
            if a == "functional-test-reviewer":
                selected.append(a)
                reasons[a] = "group D: tests/ unit replaces the roster"
    else:
        slot = routing["language_reviewer_slot"]["by_extension"]
        disabled = set((routing.get("_control_plane_v2") or {}).get("disabled_unresolved_agents", []))
        for p in paths:
            lens = slot.get(Path(p).suffix)
            if lens and lens not in disabled and lens not in selected:
                selected.append(lens)
                reasons[lens] = f"group A language lens for {Path(p).suffix}"
        selected.append("silent-failure-hunter")
        reasons["silent-failure-hunter"] = "group A baseline"
        code_files = {p: t for p, t in files.items() if not is_doc(p)}
        for name in auto_b:
            if name in selected or name in never_auto:
                continue
            trig = (routing.get("triggers") or {}).get(name)
            if not trig:
                continue
            why = trigger_fires(name, trig, code_files, tags, unit_kind)
            if why:
                selected.append(name)
                reasons[name] = why
        if any(is_test(p) for p in paths) and "functional-test-reviewer" not in selected:
            selected.append("functional-test-reviewer")
            reasons["functional-test-reviewer"] = "a changed file is a test"

    if any(S_FLAG.search(t) for t in files.values()) or any(S_PATH.search(p) for p in paths):
        flagged.append("security-reviewer")  # group S is opt-in only: flagged for the operator, never spawned
    risky = bool(flagged) or any(RISK_PATH.search(p) for p in paths) or any(RISK_CONTENT.search(t) for t in files.values())
    tier = "R3" if risky else ("R1" if len(selected) <= 1 else "R2")
    return {"tier": tier, "agents": selected, "flagged": flagged, "reasons": reasons}


def load_routing(path: Path | None = None) -> dict:
    p = path or (Path.home() / ".claude" / "agent_routing.json")
    return json.loads(p.read_text(encoding="utf-8-sig"))
