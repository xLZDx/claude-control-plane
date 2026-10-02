#!/usr/bin/env python3
"""Offline eval runner. Never starts a model.

  run_eval.py --router            deterministic router vs fixtures (agent selection precision/recall, tier, flagged)
  run_eval.py --score <run.json>  score recorded reviewer outputs; run.json = {"<fixture id>": [findings...]}

Exit code 1 when the router eval has a failing fixture (usable as a regression gate after editing agent_routing.json).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from route import load_routing, route  # noqa: E402
from score import load_case, score  # noqa: E402

FIXTURES = HERE / "fixtures"


def load_change(case_dir: Path, case: dict) -> dict:
    files = {rel: (case_dir / "files" / rel).read_text(encoding="utf-8") for rel in case["files"]}
    return {"files": files, "stack_tags": case["stack_tags"], "unit_kind": case.get("unit_kind")}


def router_eval(routing_path: Path | None = None) -> tuple[list[dict], dict]:
    routing = load_routing(routing_path)
    rows = []
    for d in sorted(p for p in FIXTURES.iterdir() if (p / "case.json").exists()):
        case = load_case(d)
        want = case["routing"]
        got = route(load_change(d, case), routing)
        expected, allowed = set(want["expected_agents"]), set(want.get("allowed_extra_agents", []))
        selected = set(got["agents"])
        missing = sorted(expected - selected)
        unnecessary = sorted(selected - expected - allowed)
        forbidden_hit = sorted(selected & set(want["forbidden_agents"]))
        flagged_ok = sorted(got["flagged"]) == sorted(want["expected_flagged"])
        tier_ok = got["tier"] == want["expected_tier"]
        rows.append({"id": case["id"], "ok": not (missing or unnecessary or forbidden_hit) and flagged_ok and tier_ok,
                     "selected": sorted(selected), "missing": missing, "unnecessary": unnecessary, "forbidden_hit": forbidden_hit,
                     "tier": got["tier"], "expected_tier": want["expected_tier"], "flagged": got["flagged"],
                     "expected_flagged": want["expected_flagged"]})
    exp_total = sum(len(r["selected"]) - len(r["unnecessary"]) + len(r["missing"]) for r in rows)
    sel_total = sum(len(r["selected"]) for r in rows)
    tp = sum(len(r["selected"]) - len(r["unnecessary"]) for r in rows)
    summary = {"fixtures": len(rows), "passed": sum(r["ok"] for r in rows),
               "selection_precision": round(tp / sel_total, 3) if sel_total else 1.0,
               "selection_recall": round(tp / exp_total, 3) if exp_total else 1.0,
               "unnecessary_invocations": sum(len(r["unnecessary"]) for r in rows),
               "missing_invocations": sum(len(r["missing"]) for r in rows),
               "avg_agents_per_change": round(sel_total / len(rows), 2) if rows else 0}
    return rows, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--router", action="store_true")
    ap.add_argument("--score", metavar="RUN_JSON")
    ap.add_argument("--routing", metavar="PATH")
    a = ap.parse_args()
    if a.router:
        rows, summary = router_eval(Path(a.routing) if a.routing else None)
        for r in rows:
            print(("PASS " if r["ok"] else "FAIL ") + r["id"].ljust(36) + f" tier={r['tier']} agents={r['selected']}"
                  + (f" MISSING={r['missing']}" if r["missing"] else "") + (f" UNNECESSARY={r['unnecessary']}" if r["unnecessary"] else "")
                  + (f" FORBIDDEN={r['forbidden_hit']}" if r["forbidden_hit"] else "")
                  + ("" if r["tier"] == r["expected_tier"] else f" TIER(expected {r['expected_tier']})")
                  + ("" if r["flagged"] == r["expected_flagged"] else f" FLAGGED={r['flagged']} expected {r['expected_flagged']}"))
        print(json.dumps(summary))
        return 0 if summary["passed"] == summary["fixtures"] else 1
    if a.score:
        run = json.loads(Path(a.score).read_text(encoding="utf-8"))
        out = []
        for fid, findings in run.items():
            out.append(score(load_case(FIXTURES / fid), findings))
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
