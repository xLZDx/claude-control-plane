import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_from_claude_home as ex  # noqa: E402
import track  # noqa: E402


class SecretScanTests(unittest.TestCase):
    def test_flags_github_token(self):
        self.assertTrue(ex.scan_text("x ghp_" + "A" * 30))

    def test_flags_private_key_header(self):
        self.assertTrue(ex.scan_text("-----BEGIN RSA PRIVATE KEY-----"))

    def test_flags_assigned_secret(self):
        self.assertTrue(ex.scan_text('api_key = "abcdefgh12345678"'))

    def test_flags_public_ip_but_not_private(self):
        self.assertTrue(ex.scan_text("host 203.0.113.7"))
        self.assertFalse(ex.scan_text("host 192.168.1.5 and 127.0.0.1"))

    def test_flags_real_email_but_not_placeholders(self):
        self.assertTrue(ex.scan_text("mail someone@gmail.com"))
        self.assertFalse(ex.scan_text("test@example.com git@github.com 1+x@users.noreply.github.com"))

    def test_flags_chatgpt_conversation_link(self):
        self.assertTrue(ex.scan_text("https://chatgpt.com/c/6abf8c09-621c-83eb-a5f1-855dd621ce18"))

    def test_plain_policy_text_is_clean(self):
        self.assertFalse(ex.scan_text("Opus is never automatic; use the sonnet alias."))


def write(p: Path, text: str | bytes = "x") -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text if isinstance(text, bytes) else text.encode())
    return p


class PublicationBoundaryTests(unittest.TestCase):
    """The exporter must publish only personal plain-text policy, never vendor or binary material."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.src = Path(self._td.name) / "src"
        write(self.src / "CLAUDE.md", "# contract")
        write(self.src / "skills" / "mine" / "SKILL.md", "# mine")

    def exported(self) -> set[str]:
        return {rel for rel, _ in ex.iter_source_files(self.src)}

    def test_personal_skill_is_exported(self):
        self.assertIn("skills/mine/SKILL.md", self.exported())

    def test_synced_vendor_directory_is_excluded(self):
        write(self.src / "skills" / "synced" / "pkg" / "docx" / "SKILL.md", "# vendor")
        self.assertFalse([p for p in self.exported() if "/synced/" in p])

    def test_skill_shipping_its_own_license_is_excluded(self):
        write(self.src / "skills" / "vendorpkg" / "SKILL.md", "# vendor")
        write(self.src / "skills" / "vendorpkg" / "LICENSE.txt", "proprietary")
        self.assertFalse([p for p in self.exported() if "vendorpkg" in p])

    def test_binary_and_font_assets_are_excluded_even_in_personal_skill(self):
        write(self.src / "skills" / "mine" / "assets" / "f.woff2", b"\x00\x01")
        write(self.src / "skills" / "mine" / "logo.png", b"\x89PNG")
        out = self.exported()
        self.assertNotIn("skills/mine/assets/f.woff2", out)
        self.assertNotIn("skills/mine/logo.png", out)

    def test_runtime_state_and_caches_are_excluded(self):
        write(self.src / "tools" / "gate" / "decisions.jsonl", "{}")
        write(self.src / "tools" / ".pytest_cache" / "v" / "nodeids", "[]")
        out = self.exported()
        self.assertNotIn("tools/gate/decisions.jsonl", out)
        self.assertFalse([p for p in out if ".pytest_cache" in p])

    def test_secret_in_source_aborts_export_and_publishes_nothing(self):
        write(self.src / "agents" / "a.md", "token = \"abcdefgh12345678\"")
        repo = Path(self._td.name) / "repo"
        repo.mkdir()
        self.assertEqual(ex.export(self.src, repo), 2)
        self.assertFalse((repo / "mirror").exists())


def run(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True).stdout


class TrackBoundaryTests(unittest.TestCase):
    """track.py must never commit anything the exporter did not produce and scan."""

    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        root = Path(self._td.name)
        self.src = root / "src"
        write(self.src / "CLAUDE.md", "# contract")
        self.repo = root / "repo"
        self.repo.mkdir()
        run(self.repo, "init", "-q", "-b", "main")
        run(self.repo, "config", "user.name", "t")
        run(self.repo, "config", "user.email", "t@example.com")
        write(self.repo / "README.md", "base")
        run(self.repo, "add", "-A")
        run(self.repo, "commit", "-q", "-m", "base")

    def head(self) -> str:
        return run(self.repo, "rev-parse", "HEAD").strip()

    def test_clean_change_is_committed_with_noreply_identity(self):
        before = self.head()
        self.assertEqual(track.track(self.src, self.repo), 0)
        self.assertNotEqual(self.head(), before)
        self.assertIn("users.noreply.github.com", run(self.repo, "log", "-1", "--format=%ae"))
        self.assertIn("mirror/CLAUDE.md", run(self.repo, "ls-files"))

    def test_second_run_without_changes_makes_no_commit(self):
        track.track(self.src, self.repo)
        head = self.head()
        self.assertEqual(track.track(self.src, self.repo), 0)
        self.assertEqual(self.head(), head)

    def test_unrelated_secret_file_blocks_track_without_commit_or_staging(self):
        stray = write(self.repo / "notes.txt", "token = \"abcdefgh12345678\"")
        before = self.head()
        self.assertEqual(track.track(self.src, self.repo), 4)
        self.assertEqual(self.head(), before)
        self.assertTrue(stray.exists(), "original worktree must be preserved")
        self.assertEqual(run(self.repo, "diff", "--cached", "--name-only").strip(), "")

    def test_unrelated_modified_tracked_file_blocks_track(self):
        write(self.repo / "README.md", "edited")
        before = self.head()
        self.assertEqual(track.track(self.src, self.repo), 4)
        self.assertEqual(self.head(), before)

    def test_secret_in_source_blocks_commit(self):
        write(self.src / "agents" / "a.md", "ghp_" + "B" * 30)
        before = self.head()
        self.assertEqual(track.track(self.src, self.repo), 2)
        self.assertEqual(self.head(), before)

    def test_secret_that_reaches_the_index_is_caught_and_unstaged(self):
        original = ex.export

        def leaky_export(src, repo, dry_run=False):
            rc = original(src, repo, dry_run)
            write(repo / "mirror" / "agents" / "leak.md", "ghp_" + "C" * 30)
            return rc

        ex.export = leaky_export
        try:
            before = self.head()
            self.assertEqual(track.track(self.src, self.repo), 2)
        finally:
            ex.export = original
        self.assertEqual(self.head(), before)
        self.assertEqual(run(self.repo, "diff", "--cached", "--name-only").strip(), "")


if __name__ == "__main__":
    unittest.main()
