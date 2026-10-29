import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "hooks" / "repeat_work_start.py"
PY = r"C:\Python314\python.exe"


class RepeatWorkStartTest(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="rws_repo_"))
        for a in (["init", "-q"], ["config", "user.email", "t@example.com"], ["config", "user.name", "t"],
                  ["config", "commit.gpgsign", "false"]):
            self.git(*a)

    def git(self, *a):
        subprocess.run(["git", *a], cwd=self.repo, check=True, capture_output=True)

    def commits(self, n, subject="T04 queue check on phone"):
        for i in range(n):
            (self.repo / f"probe_{i}.py").write_text(str(i), encoding="utf-8")
            self.git("add", ".")
            self.git("commit", "-q", "-m", f"{subject} {i}")

    def run_hook(self, prompt, env=None):
        payload = {"prompt": prompt, "cwd": str(self.repo)}
        r = subprocess.run([PY, "-s", str(HOOK)], input=json.dumps(payload), capture_output=True, text=True,
                           env=dict(os.environ, **(env or {})), timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"] if r.stdout.strip() else None

    def test_russian_prompt_with_task_id_matches_english_commits(self):
        self.commits(3)
        ctx = self.run_hook("проверь T04 на телефоне и закрой задачу")
        self.assertIn("3 commits", ctx)
        self.assertIn("t04", ctx)

    def test_fewer_than_three_commits_is_silent(self):
        self.commits(2)
        self.assertIsNone(self.run_hook("проверь T04 на телефоне и закрой задачу"))

    def test_unrelated_prompt_is_silent(self):
        self.commits(5)
        self.assertIsNone(self.run_hook("напиши отчёт про выручку за квартал"))

    def test_automated_and_short_prompts_are_skipped(self):
        self.commits(5)
        self.assertIsNone(self.run_hook("T04"))
        self.assertIsNone(self.run_hook("<task-notification> T04 finished and some more text here"))

    def test_kill_switch(self):
        self.commits(5)
        self.assertIsNone(self.run_hook("проверь T04 на телефоне и закрой задачу", {"CLAUDE_REPEAT_WORK_START": "off"}))


if __name__ == "__main__":
    unittest.main()
