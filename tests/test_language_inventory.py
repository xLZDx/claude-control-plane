"""Behavioral tests for the read-only local Git language inventory.

The tests create only temporary Git repositories with synthetic files.
They never touch a user's repository or send source content over the network.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.audit_tracked_language import classify, decode_text, scan


def run_git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True, capture_output=True, text=True,
    )


class LanguageInventoryTests(unittest.TestCase):
    def test_classification_preserves_locales_and_historical_evidence(self) -> None:
        self.assertEqual(
            classify("mobile/lib/l10n/app_ru.arb"), "LOCALE_OR_STRUCTURED_DATA_PRESERVE"
        )
        self.assertEqual(
            classify("governance/reviews/old-review.md"), "HISTORICAL_OR_EVIDENCE_REVIEW"
        )
        self.assertEqual(
            classify("docs/TDD_RU.md"), "TRANSLATABLE_PROSE_REVIEW"
        )
        self.assertEqual(
            classify("src/main.py"), "CODE_COMMENTS_OR_STRINGS_REVIEW"
        )

    def test_text_decoding_rejects_binary_data(self) -> None:
        self.assertIsNone(decode_text(b"ab\x00cd"))
        self.assertEqual(decode_text("Русский".encode("utf-8")), "Русский")

    def test_scan_uses_committed_blob_not_dirty_worktree(self) -> None:
        with tempfile.TemporaryDirectory(prefix="git-language-inventory-") as name:
            root = Path(name)
            run_git(root, "init")
            (root / "README.md").write_text("# Привет\n", encoding="utf-8")
            (root / "app.py").write_text("# English only\n", encoding="utf-8")
            run_git(root, "add", "README.md", "app.py")
            run_git(
                root, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "-m", "fixture",
            )
            head = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True,
            ).strip()

            (root / "README.md").write_text("# English in working tree\n", encoding="utf-8")
            report = scan(root, max_bytes=10000)
            self.assertEqual(report["head"], head)
            self.assertEqual(report["match_count"], 1)
            self.assertEqual(report["matches"][0]["path"], "README.md")
            self.assertTrue(report["is_complete"])

    def test_large_file_is_reported_as_incomplete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="git-language-limits-") as name:
            root = Path(name)
            run_git(root, "init")
            (root / "README.md").write_text("# Привет\n", encoding="utf-8")
            run_git(root, "add", "README.md")
            run_git(
                root, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                "commit", "-m", "fixture",
            )
            report = scan(root, max_bytes=3)
            self.assertFalse(report["is_complete"])
            self.assertEqual(report["skipped_too_large"], ["README.md"])


if __name__ == "__main__":
    unittest.main()
