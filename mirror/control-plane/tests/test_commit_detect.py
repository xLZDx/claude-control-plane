import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[2] / "hooks"
sys.path.insert(0, str(HOOKS))
from _commit_detect import is_commit_command  # noqa: E402

PY = r"C:\Python314\python.exe"


class CommitDetectTest(unittest.TestCase):
    def test_real_commits_are_detected(self):
        for cmd in ['git commit -m "x"', "git add a && git commit -m x", "cd repo && git commit -am 'x'",
                    'git commit -F - <<\'EOF\'\nmsg\nEOF', "echo hi; git commit", "FOO=1 git commit -m x",
                    'git commit -m "$(cat <<\'EOF\'\nmsg git commit\nEOF\n)"', "if true; then git commit -m x; fi"]:
            self.assertTrue(is_commit_command(cmd), cmd)

    def test_mentions_are_not_commits(self):
        for cmd in ['echo "git commit is blocked"', "python -c \"print('git commit')\"",
                    "python - <<'EOF'\nsubprocess.run(['git', 'commit'])\nx = 'git commit -m a'\nEOF",
                    "grep -rn 'git commit' hooks", "git status", "git log --grep=commit"]:
            self.assertFalse(is_commit_command(cmd), cmd)

    def test_decision_log_gate_ignores_mention_in_heredoc(self):
        repo = Path(tempfile.mkdtemp(prefix="cd_repo_"))
        subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
        cmd = "python - <<'EOF'\nprint('git commit')\nEOF"
        payload = {"session_id": "s", "cwd": str(repo), "tool_input": {"command": cmd}}
        r = subprocess.run([PY, "-s", str(HOOKS / "decision_log_gate.py")], input=json.dumps(payload),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "")  # no deny
        real = {"session_id": "s", "cwd": str(repo), "tool_input": {"command": 'git commit -m "x"'}}
        r = subprocess.run([PY, "-s", str(HOOKS / "decision_log_gate.py")], input=json.dumps(real),
                           capture_output=True, text=True, timeout=30)
        self.assertIn("deny", r.stdout)  # a real commit without the decision log is still blocked


if __name__ == "__main__":
    unittest.main()
