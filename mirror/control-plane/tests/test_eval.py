"""The eval must be able to FAIL: negative controls for the router eval and checks for the scorer (no model is run)."""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

EVAL = Path(__file__).resolve().parents[1] / "eval"
sys.path.insert(0, str(EVAL))
from run_eval import FIXTURES, router_eval  # noqa: E402
from route import load_routing  # noqa: E402
from score import load_case, score  # noqa: E402


def run_with(mutator):
    data = copy.deepcopy(load_routing())
    mutator(data)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "routing.json"
        p.write_text(json.dumps(data), encoding="utf-8")
        return router_eval(p)


class RouterEval(unittest.TestCase):
    def test_real_routing_passes_every_fixture(self):
        rows, summary = router_eval()
        failing = [r["id"] for r in rows if not r["ok"]]
        self.assertEqual(failing, [], rows)
        self.assertGreaterEqual(summary["fixtures"], 15)
        self.assertEqual(summary["unnecessary_invocations"], 0)

    def test_removing_a_trigger_is_detected_as_missing(self):
        def mut(d):
            d["triggers"]["fastapi-reviewer"]["imports"] = ["no_such_module"]
        rows, summary = run_with(mut)
        bad = {r["id"] for r in rows if "fastapi-reviewer" in r["missing"]}
        self.assertEqual(bad, {"f04_download_without_project_check", "f15_tenant_from_request_body"})
        self.assertLess(summary["selection_recall"], 1.0)

    def test_overbroad_trigger_is_detected_as_unnecessary(self):
        def mut(d):
            d["triggers"]["a11y-architect"] = {"paths": ["**/*"]}
        rows, summary = run_with(mut)
        self.assertGreater(summary["unnecessary_invocations"], 0)
        self.assertTrue(any("a11y-architect" in r["forbidden_hit"] for r in rows))
        self.assertLess(summary["selection_precision"], 1.0)

    def test_a_router_that_picks_nothing_fails_recall(self):
        def mut(d):
            d["groups"]["B_domain_triggered"]["agents"] = []
            d["language_reviewer_slot"]["by_extension"] = {}
        rows, summary = run_with(mut)
        self.assertGreater(summary["missing_invocations"], 0)
        self.assertLess(summary["passed"], summary["fixtures"])

    def test_docs_only_negative_control_selects_nothing(self):
        rows, _ = router_eval()
        r = next(x for x in rows if x["id"] == "f10_docs_typo_only")
        self.assertEqual((r["selected"], r["tier"]), ([], "R0"))


class Fixtures(unittest.TestCase):
    def test_every_seeded_defect_points_at_a_real_line_and_leaves_no_hint(self):
        for d in sorted(p for p in FIXTURES.iterdir() if (p / "case.json").exists()):
            case = load_case(d)
            for sd in case["seeded_defects"]:
                lines = (d / "files" / sd["file"]).read_text(encoding="utf-8").splitlines()
                self.assertLessEqual(sd["line"], len(lines), d.name)
                text = "\n".join(lines).lower()
                for hint in ("seeded", "defect", "bug here", "vulnerab", "todo", "fixme"):
                    self.assertNotIn(hint, text, f"{d.name} leaks the answer via '{hint}'")
            self.assertTrue(case["routing"]["expected_tier"] in {"R0", "R1", "R2", "R3"})


class Scorer(unittest.TestCase):
    CASE = {"id": "x", "line_tolerance": 2, "acceptable_extra": [],
            "seeded_defects": [{"id": "D1", "file": "src/a.py", "line": 10, "min_severity": "MAJOR", "keywords": r"idempot"},
                               {"id": "D2", "file": "src/b.py", "line": 5, "min_severity": "BLOCKER", "keywords": r"tenant"}]}

    def test_recall_escape_duplicates_and_false_positives(self):
        findings = [
            {"agent": "reliability-reviewer", "severity": "MAJOR", "file": "src/a.py", "line": 11, "claim": "retry without key"},
            {"agent": "code-reviewer", "severity": "MINOR", "file": "src/a.py", "line": 30, "claim": "duplicate delivery lacks idempotency"},
            {"agent": "python-reviewer", "severity": "MAJOR", "file": "src/c.py", "line": 1, "claim": "unrelated style worry"},
        ]
        s = score(self.CASE, findings)
        self.assertEqual((s["found"], s["escaped"]), (1, ["D2"]))
        self.assertEqual(s["recall"], 0.5)
        self.assertEqual(s["duplicate_findings"], 1)
        self.assertEqual(s["false_positive_blocker_major"], 1)
        self.assertEqual(s["precision_blocker_major"], 0.5)

    def test_severity_below_minimum_is_not_adequate(self):
        s = score(self.CASE, [{"agent": "a", "severity": "MINOR", "file": "src/b.py", "line": 5, "claim": "x"}])
        self.assertEqual((s["found"], s["severity_adequate"]), (1, 0))

    def test_no_findings_means_everything_escaped(self):
        s = score(self.CASE, [])
        self.assertEqual((s["recall"], s["escaped"]), (0.0, ["D1", "D2"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
