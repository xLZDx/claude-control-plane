import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[2] / "hooks"
PY = r"C:\Python314\python.exe"


def human(text="работай"):
    return {"type": "user", "message": {"role": "user", "content": [{"type": "text", "text": text}]}}


class RepeatWorkGateTest(unittest.TestCase):
    def setUp(self):
        self.state = Path(tempfile.mkdtemp(prefix="rw_state_"))
        self.work = Path(tempfile.mkdtemp(prefix="rw_tr_"))
        self.repo = Path(tempfile.mkdtemp(prefix="rw_repo_"))
        self.env = dict(os.environ, CLAUDE_REPEAT_WORK_STATE=str(self.state))
        self.env.pop("CLAUDE_REPEAT_WORK_GATE", None)
        self.git("init", "-q")
        self.git("config", "user.email", "t@example.com")
        self.git("config", "user.name", "t")
        self.git("config", "commit.gpgsign", "false")

    def git(self, *a):
        subprocess.run(["git", *a], cwd=self.repo, check=True, capture_output=True)

    def commit_file(self, name, text, msg):
        (self.repo / name).write_text(text, encoding="utf-8")
        self.git("add", name)
        self.git("commit", "-q", "-m", msg)

    def history(self, n):
        for i in range(n):
            (self.repo / "harness.py").write_text(f"v{i}\n", encoding="utf-8")
            (self.repo / "runner.py").write_text(f"v{i}\n", encoding="utf-8")
            self.git("add", "harness.py", "runner.py")
            self.git("commit", "-q", "-m", f"step {i}")

    def stage_next(self, *names):
        for name in names or ("harness.py", "runner.py"):
            (self.repo / name).write_text("next\n", encoding="utf-8")
            self.git("add", name)

    def pre(self, rows, command='git commit -m "wire thing"'):
        tp = self.work / "t.jsonl"
        tp.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        payload = {"session_id": "s1", "transcript_path": str(tp), "cwd": str(self.repo),
                   "tool_input": {"command": command}}
        r = subprocess.run([PY, "-s", str(HOOKS / "repeat_work_gate.py")], input=json.dumps(payload),
                           capture_output=True, text=True, env=self.env, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)["hookSpecificOutput"] if r.stdout.strip() else None

    def keep_going_released(self, rows):
        tp = self.work / "t.jsonl"
        tp.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        payload = {"session_id": "s1", "transcript_path": str(tp),
                   "last_assistant_message": "Заблокировано, остались запуски, жду вашего решения. " * 10}
        r = subprocess.run([PY, "-s", str(HOOKS / "keep_going_gate.py")], input=json.dumps(payload),
                           capture_output=True, text=True, env=self.env, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return not r.stdout.strip()

    def test_fresh_work_and_non_commit_commands_pass(self):
        self.history(2)
        self.stage_next()
        self.assertIsNone(self.pre([human()]))
        self.assertIsNone(self.pre([human()], "git status"))

    def test_third_similar_commit_is_warned_once(self):
        self.history(3)
        self.stage_next()
        out = self.pre([human()])
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("3 earlier commits", out["permissionDecisionReason"])
        self.assertIsNone(self.pre([human()]))  # shown once per file set

    def test_unrelated_files_pass_even_with_long_history(self):
        self.history(6)
        self.stage_next("other.txt", "other2.txt")
        self.assertIsNone(self.pre([human()], 'git commit -m "docs for something else"'))

    def test_eighth_similar_commit_escalates_until_operator_writes(self):
        self.history(8)
        self.stage_next()
        rows = [human()]
        out = self.pre(rows)
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("AskUserQuestion", out["permissionDecisionReason"])
        self.assertEqual(self.pre(rows)["permissionDecision"], "deny")  # still denied while unanswered
        self.assertTrue(self.keep_going_released(rows))
        self.assertIsNone(self.pre(rows + [human("да, продолжай")]))
        self.assertFalse(self.keep_going_released(rows + [human("да, продолжай")]))

    def test_shared_log_files_are_ignored(self):
        for i in range(6):
            self.commit_file("DECISION_LOG.md", f"{i}\n", f"unrelated change {i}")
        (self.repo / "DECISION_LOG.md").write_text("x\n", encoding="utf-8")
        self.git("add", "DECISION_LOG.md")
        self.assertIsNone(self.pre([human()]))

    def test_single_shared_file_is_not_repeated_work(self):
        self.history(8)
        self.stage_next("harness.py")
        self.assertIsNone(self.pre([human()]))

    def test_kill_switch(self):
        self.history(8)
        self.stage_next()
        self.env["CLAUDE_REPEAT_WORK_GATE"] = "off"
        self.assertIsNone(self.pre([human()]))


if __name__ == "__main__":
    unittest.main()
