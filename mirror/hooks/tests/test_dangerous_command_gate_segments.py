"""Functional tests for dangerous_command_gate.find_hits: separators, leaders, wrapper options.

Contract: find_hits(command) returns [] when the command is allowed and a non-empty list when a
destructive command is detected anywhere in the command line.
"""
import sys
import unittest
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HOOKS_DIR))

import dangerous_command_gate as gate  # noqa: E402


class BlockedMixin:
    def assert_blocked(self, commands):
        for cmd in commands:
            with self.subTest(cmd=cmd):
                self.assertTrue(gate.find_hits(cmd), f"expected BLOCK for: {cmd!r}")

    def assert_allowed(self, commands):
        for cmd in commands:
            with self.subTest(cmd=cmd):
                self.assertEqual(gate.find_hits(cmd), [], f"expected ALLOW for: {cmd!r}")


class TestSeparatorsAndLeaders(BlockedMixin, unittest.TestCase):
    def test_lone_ampersand_then_destructive(self):
        self.assert_blocked(["echo hi & rm -rf ~", "sleep 1 &rm -rf ~", "echo hi & git reset --hard"])

    def test_subshell_and_group(self):
        self.assert_blocked(["(rm -rf ~)", "{ rm -rf ~; }", "( (rm -rf ~) )", "(git reset --hard)"])

    def test_negation(self):
        self.assert_blocked(["! rm -rf ~", "! git reset --hard"])

    def test_compound_keywords(self):
        self.assert_blocked([
            "if true; then rm -rf ~; fi",
            "for d in x; do git reset --hard; done",
            "if false; then echo a; else rm -rf ~; fi",
            "if false; then echo a; elif true; then git clean -fdx; fi",
            "while true; do rm -rf /; done",
            "until false; do git branch -D main; done",
            "if rm -rf ~; then echo ok; fi",
        ])

    def test_uppercase_keywords(self):
        self.assert_blocked(["IF true; THEN rm -rf ~; FI"])


class TestGitGlobalOptions(BlockedMixin, unittest.TestCase):
    def test_blocked_with_global_options(self):
        self.assert_blocked([
            "git -C ../repo reset --hard",
            "git -C . clean -fdx",
            "git -c core.x=y branch -D main",
            "git --git-dir=.git reset --hard",
            "git --git-dir .git reset --hard",
            "git --work-tree . -C x reset --hard",
            "git --no-pager reset --hard",
            "git -C a -c k=v push --delete origin x",
            "git -C ../repo push origin :old",
        ])

    def test_allowed_with_global_options(self):
        self.assert_allowed([
            "git -C ../repo status",
            "git -C . log --oneline",
            "git -c core.x=y fetch",
            "git --git-dir=.git status",
            "git -C ../repo restore --staged f",
        ])


class TestWrapperOptions(BlockedMixin, unittest.TestCase):
    def test_blocked_through_wrappers(self):
        self.assert_blocked([
            "sudo -u root rm -rf /",
            "sudo -g wheel rm -rf /",
            "sudo -H rm -rf /",
            "timeout -s KILL 5 rm -rf /",
            "timeout --kill-after 3 10 rm -rf /",
            "doas -u root rm -rf /",
            "sudo rm -rf /",
            "sudo -u root git -C x reset --hard",
        ])

    def test_allowed_through_wrappers(self):
        self.assert_allowed(["sudo -u root ls /", "timeout -s KILL 5 ls", "doas -u root ls", "sudo -H ls"])


class TestWrapperLongOptionsAndTerminator(BlockedMixin, unittest.TestCase):
    def test_blocked_long_options_and_double_dash(self):
        self.assert_blocked([
            "sudo --user root rm -rf /",
            "sudo --group wheel rm -rf /",
            "sudo --user=root rm -rf /",
            "sudo -- rm -rf /",
            "sudo -u root -- rm -rf /",
            "doas -- rm -rf /",
            "sudo --host h --user root git reset --hard",
        ])

    def test_allowed_long_options_and_double_dash(self):
        self.assert_allowed(["sudo -- ls /", "sudo --user root ls /", "sudo -u root -- ls /", "doas -- ls"])


class TestNoFalsePositives(BlockedMixin, unittest.TestCase):
    def test_redirections_not_separators(self):
        self.assert_allowed(["cmd 2>&1", "cmd &> out.log", "cmd >&2", "cmd 2>&1 | tee x", "cmd >& out.log"])

    def test_benign_separators(self):
        self.assert_allowed(["echo hi & echo there", "a && b", "a || b", "echo a; echo b"])

    def test_benign_git_and_rm(self):
        self.assert_allowed([
            "git restore --staged f",
            "rm file.txt",
            "git push origin main",
            "git status",
            "git branch -d merged",
        ])

    def test_keyword_words_as_arguments(self):
        self.assert_allowed(["echo then rm -rf", "echo do git reset --hard", "echo ! rm -rf ~"])


class TestBaselines(BlockedMixin, unittest.TestCase):
    def test_previously_blocked_still_blocked(self):
        self.assert_blocked([
            "rm -rf /",
            "git reset --hard",
            "git branch -D x",
            "git push --delete origin x",
            "sudo rm -rf /",
            'bash -c "rm -rf ~"',
            "git clean -fd",
            "echo a && rm -rf ~",
            "echo a; rm -rf ~",
            "echo $(rm -rf ~)",
        ])


class TestSegmentsUnit(unittest.TestCase):
    def test_segments_strip_leaders_and_split_ampersand(self):
        self.assertEqual(gate.segments("echo hi & rm -rf ~"), ["echo hi", "rm -rf ~"])
        self.assertIn("rm -rf ~", gate.segments("(rm -rf ~)"))
        self.assertIn("git reset --hard", gate.segments("do git reset --hard"))

    def test_skip_git_global_options(self):
        f = gate.skip_git_global_options
        self.assertEqual(f(["git", "-C", "x", "reset", "--hard"]), ["git", "reset", "--hard"])
        self.assertEqual(f(["git", "--git-dir=.git", "status"]), ["git", "status"])
        self.assertEqual(f(["git", "--git-dir", ".git", "status"]), ["git", "status"])
        self.assertEqual(f(["git"]), ["git"])


if __name__ == "__main__":
    unittest.main()
