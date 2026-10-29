import argparse
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "hooks"))
spec = importlib.util.spec_from_file_location("session_watchdog", ROOT / "session_watchdog.py")
wd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wd)


def item(sid, category, idle):
    return {"session_id": sid, "project": "pdcc", "cwd": "D:\\Repo\\Personal_Decision_Command_Center",
            "idle_min": idle, "category": category, "stalled": True, "transcript": "x"}


class WatchdogThrottleTest(unittest.TestCase):
    def setUp(self):
        wd.STATE_DIR = Path(tempfile.mkdtemp())
        self.resumed = []
        wd.resume = lambda it, budget, timeout: self.resumed.append(it["session_id"]) or "exit=0"
        wd.acts_so_far = lambda sid: 0
        self.hour = 0
        wd.resumes_last_hour = lambda: self.hour
        wd.scan = lambda idle, age, wait: [item("old", "IDLE", 9000), item("fresh", "IDLE", 30), item("ci", "WAITING", 15),
                                           item("mid", "IDLE", 500)]

    def args(self, **kw):
        base = dict(idle_min=20, max_age_h=0, wait_min=10, act=True, budget=10.0, timeout=60, json=False,
                    projects="", max_per_run=2, max_per_hour=6)
        base.update(kw)
        return argparse.Namespace(**base)

    def test_run_cap_and_priority(self):
        wd.run(self.args())
        self.assertEqual(self.resumed, ["ci", "fresh"])  # CI wait first, then most recently active

    def test_hourly_cap_defers_everything(self):
        self.hour = 6
        wd.run(self.args())
        self.assertEqual(self.resumed, [])

    def test_hourly_cap_leaves_partial_room(self):
        self.hour = 5
        wd.run(self.args())
        self.assertEqual(self.resumed, ["ci"])

    def test_report_only_never_resumes(self):
        wd.run(self.args(act=False))
        self.assertEqual(self.resumed, [])


class WatchdogWindowTest(unittest.TestCase):
    """Only sessions that were active within the last two hours are touched; older ones are left alone."""

    def make(self, minutes_quiet, text="Закоммитил и остановился на чекпойнте."):
        import json
        import os
        import time

        path = Path(tempfile.mkdtemp()) / "s-1.jsonl"
        rows = [{"type": "user", "cwd": "D:\\Repo\\ERP", "message": {"role": "user", "content": "работай"}},
                {"type": "assistant", "cwd": "D:\\Repo\\ERP", "message": {"content": [
                    {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "git status"}}]}},
                {"type": "user", "cwd": "D:\\Repo\\ERP", "message": {"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": "t1", "content": "clean"}]}},
                {"type": "assistant", "cwd": "D:\\Repo\\ERP", "message": {"content": [{"type": "text", "text": text}]}}]
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        past = time.time() - minutes_quiet * 60
        os.utime(path, (past, past))
        return path

    def inspect(self, minutes_quiet, **kw):
        import time

        return wd.inspect(self.make(minutes_quiet, **kw), time.time(), 20, 2, 10)

    def test_default_window_is_one_hour(self):
        import sys as _sys

        old_argv = _sys.argv
        try:
            _sys.argv = ["x"]
            ap_default = [a for a in open(ROOT / "session_watchdog.py", encoding="utf-8").read().splitlines() if '"--max-age-h"' in a][0]
        finally:
            _sys.argv = old_argv
        self.assertIn("default=2,", ap_default)

    def test_window_edges(self):
        self.assertIsNone(self.inspect(5))      # still warm: a live terminal may be in use
        self.assertTrue(self.inspect(30)["stalled"])   # quiet 30 min, active within the hour -> resume
        self.assertTrue(self.inspect(100)["stalled"])  # 100 min, inside two hours -> resume
        self.assertIsNone(self.inspect(150))    # older than two hours -> left alone
        self.assertIsNone(self.inspect(60 * 24 * 8))  # 8 days -> left alone

    def test_ci_wait_inside_window_is_woken_after_ten_minutes(self):
        self.assertIsNone(self.inspect(5, text="Жду результатов CI, сообщу когда завершится."))
        self.assertTrue(self.inspect(15, text="Жду результатов CI, сообщу когда завершится.")["stalled"])
        self.assertTrue(self.inspect(90, text="Жду результатов CI, сообщу когда завершится.")["stalled"])
        self.assertIsNone(self.inspect(150, text="Жду результатов CI, сообщу когда завершится."))


class WatchdogOneShotTest(unittest.TestCase):
    def write(self, rows):
        import json

        path = Path(tempfile.mkdtemp()) / "s.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        return path

    def user(self, text):
        return {"type": "user", "message": {"role": "user", "content": text}}

    def answer(self, text="ok"):
        return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}

    def test_single_prompt_no_tools_is_one_shot(self):
        self.assertTrue(wd.is_one_shot(self.write([self.user("Ответь одним словом: ok"), self.answer()])))

    def test_tool_call_means_real_work(self):
        tool = {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "1", "name": "Bash", "input": {}}]}}
        self.assertFalse(wd.is_one_shot(self.write([self.user("проверь"), tool, self.answer("готово")])))

    def test_second_prompt_means_a_conversation(self):
        self.assertFalse(wd.is_one_shot(self.write([self.user("раз"), self.answer(), self.user("два"), self.answer()])))

    def test_tool_results_and_meta_do_not_count_as_prompts(self):
        result = {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "1", "content": "x"}]}}
        meta = {"type": "user", "isMeta": True, "message": {"role": "user", "content": "hook context"}}
        self.assertTrue(wd.is_one_shot(self.write([self.user("раз"), meta, result, self.answer()])))

    def test_inspect_skips_one_shot_even_in_window(self):
        import os
        import time

        path = self.write([{**self.user("Ответь одним словом: ok"), "cwd": "D:\\Repo\\ERP"},
                           {**self.answer("Остановился на чекпойнте."), "cwd": "D:\\Repo\\ERP"}])
        past = time.time() - 30 * 60
        os.utime(path, (past, past))
        self.assertIsNone(wd.inspect(path, time.time(), 20, 2, 10))


if __name__ == "__main__":
    unittest.main()
