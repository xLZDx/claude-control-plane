"""Score reviewer output against a seeded-defect fixture. Never launches a model.

Findings file: JSON list of {"agent", "severity", "file", "line"?, "claim", "tokens"?, "latency_s"?}
Fixture:       eval/fixtures/<id>/case.json  (see README.md)

Matching: a finding matches an expected defect when the file is the same and either the cited line is within
`line_tolerance` of the seeded line or the claim matches the defect's `keywords` regex.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

SEV = ["NIT", "MINOR", "MAJOR", "BLOCKER"]


def matches(finding: dict, defect: dict, tol: int) -> bool:
    if Path(str(finding.get("file", ""))).as_posix() != defect["file"]:
        return False
    line, want = finding.get("line"), defect.get("line")
    if line is not None and want is not None and abs(int(line) - int(want)) <= tol:
        return True
    return bool(re.search(defect["keywords"], str(finding.get("claim", "")), re.I))


def score(case: dict, findings: list[dict]) -> dict:
    tol = int(case.get("line_tolerance", 3))
    defects = case["seeded_defects"]
    per = {d["id"]: [] for d in defects}
    extra = []
    for f in findings:
        hit = [d for d in defects if matches(f, d, tol)]
        if hit:
            for d in hit:
                per[d["id"]].append(f)
        elif f.get("severity", "").upper() in ("BLOCKER", "MAJOR") and not any(re.search(a, str(f.get("claim", "")), re.I) for a in case.get("acceptable_extra", [])):
            extra.append(f)
    found = [d for d in defects if per[d["id"]]]
    escaped = [d["id"] for d in defects if not per[d["id"]]]
    duplicates = sum(max(0, len({f["agent"] for f in per[d["id"]]}) - 1) for d in defects)
    unique = sum(1 for d in defects if len({f["agent"] for f in per[d["id"]]}) == 1)
    sev_ok = sum(1 for d in found if any(SEV.index(str(f.get("severity", "NIT")).upper()) >= SEV.index(d["min_severity"]) for f in per[d["id"]]))
    reported_serious = [f for f in findings if str(f.get("severity", "")).upper() in ("BLOCKER", "MAJOR")]
    tp = sum(1 for f in reported_serious if any(matches(f, d, tol) for d in defects))
    return {
        "case": case["id"], "defects": len(defects), "found": len(found), "escaped": escaped,
        "recall": round(len(found) / len(defects), 3) if defects else 1.0,
        "severity_adequate": sev_ok, "findings_total": len(findings),
        "false_positive_blocker_major": len(extra),
        "precision_blocker_major": round(tp / len(reported_serious), 3) if reported_serious else 1.0,
        "duplicate_findings": duplicates, "unique_findings": unique,
        "agents": sorted({f["agent"] for f in findings}),
        "tokens": sum(int(f.get("tokens", 0)) for f in findings), "latency_s": round(sum(float(f.get("latency_s", 0)) for f in findings), 2),
    }


def load_case(fixture_dir: Path) -> dict:
    return json.loads((fixture_dir / "case.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        raise SystemExit("usage: score.py <fixture_dir> <findings.json>")
    c = load_case(Path(sys.argv[1]))
    print(json.dumps(score(c, json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))), indent=2, ensure_ascii=False))
