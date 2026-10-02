"""Regression test for report_conform.py's project-name derivation.

Guards against the specific bug found and fixed 2026-08-21: a report generated from inside a
temporary git worktree (e.g. D:/Repo/_wt-gates-efgh, a worktree of the Fitness-App repo checked
out under an unrelated directory name) reported PROJECT as that worktree's own directory basename
instead of the repository's real identity. `git rev-parse --show-toplevel` returns each worktree's
own path, so basename-of-toplevel is not a stable project identity across worktrees of the same
repo; the origin remote URL is shared by every worktree and is the correct source of truth.

Standalone script, no pytest dependency -- run directly:

    py -3 C:/Users/koros/.claude/tools/test_report_conform.py

Exits 0 on success, 1 with a message on the first failing assertion.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report_conform  # noqa: E402


def _run_git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git"] + args, cwd=cwd, check=True, capture_output=True, text=True)


def _project_name_from_remote_cases() -> None:
    cases = [
        ("https://github.com/xLZDx/Fitness-App.git", "Fitness-App"),
        ("https://github.com/xLZDx/Fitness-App", "Fitness-App"),
        ("git@github.com:xLZDx/Fitness-App.git", "Fitness-App"),
        ("D:\\Repo\\bare-repos\\Fitness-App.git", "Fitness-App"),
        (None, None),
    ]
    for remote, expected in cases:
        got = report_conform._project_name_from_remote(remote)
        assert got == expected, f"_project_name_from_remote({remote!r}) = {got!r}, expected {expected!r}"


def _worktree_identity_is_stable() -> None:
    """The regression case: two worktrees of the same repo, different directory names.

    project_facts() must report the SAME project name for both -- derived from origin, not from
    each worktree's own directory basename -- and that name must NOT equal either worktree's
    directory name (both are deliberately named unlike the repo, mirroring _wt-gates-efgh).
    """
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        main_repo = base / "some-unrelated-dirname"
        main_repo.mkdir()
        _run_git(["init", "-q"], main_repo)
        _run_git(["config", "user.email", "test@example.com"], main_repo)
        _run_git(["config", "user.name", "Test"], main_repo)
        _run_git(["remote", "add", "origin", "https://github.com/xLZDx/Fitness-App.git"], main_repo)
        (main_repo / "README.md").write_text("x", encoding="utf-8")
        _run_git(["add", "README.md"], main_repo)
        _run_git(["commit", "-q", "-m", "init"], main_repo)
        _run_git(["branch", "-M", "master"], main_repo)

        worktree_dir = base / "_wt-totally-different-name"
        _run_git(["worktree", "add", "-b", "side", str(worktree_dir)], main_repo)

        reports_main = main_repo / "reports"
        reports_main.mkdir()
        html_main = reports_main / "r.html"
        html_main.write_text("<html><body></body></html>", encoding="utf-8")

        reports_wt = worktree_dir / "reports"
        reports_wt.mkdir()
        html_wt = reports_wt / "r.html"
        html_wt.write_text("<html><body></body></html>", encoding="utf-8")

        facts_main = report_conform.project_facts(html_main, None)
        facts_wt = report_conform.project_facts(html_wt, None)

        assert facts_main["name"] == "Fitness-App", facts_main["name"]
        assert facts_wt["name"] == "Fitness-App", facts_wt["name"]
        assert facts_wt["name"] != worktree_dir.name, (
            f"regression: project name fell back to the worktree directory name {worktree_dir.name!r}"
        )
        assert facts_main["name"] != main_repo.name, (
            f"regression: project name fell back to the toplevel directory name {main_repo.name!r}"
        )


def _no_remote_falls_back_to_directory_name() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        repo = base / "no-remote-repo"
        repo.mkdir()
        _run_git(["init", "-q"], repo)
        _run_git(["config", "user.email", "test@example.com"], repo)
        _run_git(["config", "user.name", "Test"], repo)
        (repo / "README.md").write_text("x", encoding="utf-8")
        _run_git(["add", "README.md"], repo)
        _run_git(["commit", "-q", "-m", "init"], repo)

        reports = repo / "reports"
        reports.mkdir()
        html = reports / "r.html"
        html.write_text("<html><body></body></html>", encoding="utf-8")

        facts = report_conform.project_facts(html, None)
        assert facts["name"] == "no-remote-repo", facts["name"]


def main() -> int:
    tests = [
        _project_name_from_remote_cases,
        _worktree_identity_is_stable,
        _no_remote_falls_back_to_directory_name,
    ]
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            print(f"FAIL {test.__name__}: {exc}")
            return 1
        except subprocess.CalledProcessError as exc:
            print(f"FAIL {test.__name__}: git command failed: {exc.stderr}")
            return 1
        print(f"PASS {test.__name__}")
    print("all report_conform regression tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
