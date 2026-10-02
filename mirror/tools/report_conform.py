"""Bring an HTML report up to the operator's mandated report format.

Two elements are mandatory in every HTML report, in every project (operator instruction,
2026-08-17), and both are mechanical, so they are injected rather than re-typed by hand:

  1. a copy-page button that puts the whole rendered report text on the clipboard;
  2. a provenance block directly under the header: project name, absolute project folder,
     git remote (plus branch and HEAD when available).

Both are inserted as a single bar immediately after </header>, so placement does not depend on
the report's own layout. The injected CSS reads the page's own custom properties with literal
fallbacks (`var(--surface, #fff)`), so the bar adopts whatever palette the report already uses
instead of fighting it.

Idempotent: re-running replaces the previously injected block rather than stacking copies, so it
doubles as the way to refresh provenance after a commit.

    python report_conform.py <file-or-dir> [...]           # inject or refresh
    python report_conform.py <file-or-dir> --check         # report only, exit 1 if work is due
    python report_conform.py <dir> --project-name "Name"   # override the derived project name

Language of the labels follows the file: `*_ru.html` / `*.ru.html` get Russian, everything else
English. Pass --lang ru|en to force it.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

BEGIN = "<!-- report-conform:begin -->"
END = "<!-- report-conform:end -->"
SCRIPT_BEGIN = "<!-- report-conform:script:begin -->"
SCRIPT_END = "<!-- report-conform:script:end -->"

LABELS = {
    "en": {
        "project": "Project",
        "folder": "Folder",
        "git": "Git",
        "idle": "Copy page",
        "done": "Copied",
        "fail": "Select manually",
        "no_remote": "no remote configured",
        "not_git": "not a git repository",
    },
    "ru": {
        "project": "Проект",
        "folder": "Папка",
        "git": "Git",
        "idle": "Копировать страницу",
        "done": "Скопировано",
        "fail": "Выделите вручную",
        "no_remote": "remote не настроен",
        "not_git": "не git-репозиторий",
    },
}

STYLE = """<style id="rc-style">
.rc-bar{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem;flex-wrap:wrap;
  margin:1.4rem 0 0;padding:0.9rem 1.05rem;background:var(--surface,#fff);
  border:1px solid var(--border,var(--rule,#d9d9d9));
  border-left:3px solid var(--accent,#6a6a6a);border-radius:3px}
.rc-bar dl{display:grid;grid-template-columns:auto 1fr;gap:0.4rem 1rem;margin:0;min-width:0;
  font-family:ui-monospace,"Cascadia Code","SF Mono",Consolas,monospace;font-size:0.74rem;line-height:1.5}
.rc-bar dt{color:var(--text-3,var(--muted,#888));text-transform:uppercase;letter-spacing:0.08em;
  font-size:0.66rem;white-space:nowrap;padding-top:0.15em}
.rc-bar dd{margin:0;color:var(--text,var(--ink,#222));word-break:break-word;min-width:0}
.rc-copy{flex:none;cursor:pointer;white-space:nowrap;
  font-family:ui-monospace,"Cascadia Code","SF Mono",Consolas,monospace;
  font-size:0.68rem;letter-spacing:0.08em;text-transform:uppercase;
  color:var(--accent,#6a6a6a);background:var(--surface-2,var(--surface,#fff));
  border:1px solid var(--border,var(--rule,#d9d9d9));border-radius:2px;padding:0.45em 0.85em}
.rc-copy:hover{border-color:var(--accent,#6a6a6a)}
.rc-copy:focus-visible{outline:2px solid var(--accent,#6a6a6a);outline-offset:2px}
.rc-copy.is-done{color:var(--ok,#1c6f53);border-color:currentColor}
.rc-copy.is-fail{color:var(--bad,#9e2f2a);border-color:currentColor}
</style>"""

SCRIPT = """<script>
(function () {
  var btn = document.getElementById('rc-copy');
  if (!btn) { return; }

  function pageText() {
    // Hide the button so its own label never lands in the copied text.
    var previous = btn.style.display;
    btn.style.display = 'none';
    var root = document.querySelector('.wrap') || document.body;
    var text = (root.innerText || root.textContent || '').replace(/\\n{3,}/g, '\\n\\n').trim();
    btn.style.display = previous;
    return text;
  }

  function legacyCopy(text) {
    var field = document.createElement('textarea');
    field.value = text;
    field.setAttribute('readonly', '');
    field.style.position = 'fixed';
    field.style.top = '-1000px';
    document.body.appendChild(field);
    field.select();
    var copied = false;
    try { copied = document.execCommand('copy'); } catch (err) { copied = false; }
    document.body.removeChild(field);
    return copied;
  }

  function report(state) {
    btn.textContent = btn.getAttribute('data-' + state);
    btn.classList.toggle('is-done', state === 'done');
    btn.classList.toggle('is-fail', state === 'fail');
    window.setTimeout(function () {
      btn.textContent = btn.getAttribute('data-idle');
      btn.classList.remove('is-done', 'is-fail');
    }, 2400);
  }

  btn.addEventListener('click', function () {
    var text = pageText();
    // Some hosts block the async clipboard API inside the artifact iframe, so the
    // execCommand path stays as a real fallback rather than an assumed success.
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(
        function () { report('done'); },
        function () { report(legacyCopy(text) ? 'done' : 'fail'); }
      );
    } else {
      report(legacyCopy(text) ? 'done' : 'fail');
    }
  });
})();
</script>"""


def _git(args: list[str], cwd: Path) -> str | None:
    try:
        done = subprocess.run(
            ["git", "-C", str(cwd)] + args, capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    return done.stdout.strip() or None


def _project_name_from_remote(remote: str | None) -> str | None:
    """Repo name from the origin URL, e.g. https://github.com/owner/Fitness-App.git -> Fitness-App.

    A worktree's own toplevel directory (D:/Repo/_wt-gates-efgh, D:/Repo/Fitness_App, ...) is not a
    stable project identity: the same repository can be checked out under many worktree directory
    names, and reports generated from a temporary worktree would otherwise show that worktree's
    name as the "project". The origin remote is shared by every worktree of the same repo, so it is
    the stable source of truth for the project name; the directory name is only a fallback.
    """
    if not remote:
        return None
    cleaned = remote.strip().rstrip("/\\")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]
    parts = [p for p in re.split(r"[\\/:]+", cleaned) if p]
    return parts[-1] if parts else None


def project_facts(html_file: Path, name_override: str | None) -> dict[str, str | None]:
    directory = html_file.resolve().parent
    root = _git(["rev-parse", "--show-toplevel"], directory)
    if root:
        root_path = Path(root)
    else:
        # Outside git, the containing folder is the best available stand-in for the project --
        # except when it is the reports/ folder itself, which names nothing.
        root_path = directory.parent if directory.name.lower() == "reports" else directory
    remote = _git(["remote", "get-url", "origin"], directory)
    return {
        "root": str(root_path).replace("/", "\\") if sys.platform == "win32" else str(root_path),
        "name": name_override or _project_name_from_remote(remote) or root_path.name,
        "remote": remote,
        "branch": _git(["rev-parse", "--abbrev-ref", "HEAD"], directory),
        "head": _git(["rev-parse", "--short", "HEAD"], directory),
        "is_git": bool(root),
    }


def detect_lang(html_file: Path, forced: str | None, text: str) -> str:
    if forced:
        return forced
    stem = html_file.name.lower()
    if stem.endswith("_ru.html") or ".ru." in stem or stem.endswith("-ru.html"):
        return "ru"
    if stem.endswith("_en.html") or ".en." in stem:
        return "en"
    # No suffix to go by: a report written in Russian still needs Russian labels, and Cyrillic
    # is a reliable enough signal once it is more than an occasional quoted word.
    letters = sum(1 for ch in text if ch.isalpha())
    cyrillic = sum(1 for ch in text if "Ѐ" <= ch <= "ӿ")
    return "ru" if letters and cyrillic / letters > 0.25 else "en"


def build_block(facts: dict, lang: str) -> str:
    label = LABELS[lang]
    if facts["remote"]:
        git_value = facts["remote"]
        if facts["branch"]:
            git_value += f" &mdash; {facts['branch']}"
            if facts["head"]:
                git_value += f" @ {facts['head']}"
    else:
        git_value = label["no_remote"] if facts["is_git"] else label["not_git"]

    return (
        f"{BEGIN}\n{STYLE}\n"
        f'<div class="rc-bar">\n'
        f"  <dl>\n"
        f'    <dt>{label["project"]}</dt><dd>{facts["name"]}</dd>\n'
        f'    <dt>{label["folder"]}</dt><dd>{facts["root"]}</dd>\n'
        f'    <dt>{label["git"]}</dt><dd>{git_value}</dd>\n'
        f"  </dl>\n"
        f'  <button id="rc-copy" class="rc-copy" type="button"\n'
        f'          data-idle="{label["idle"]}" data-done="{label["done"]}"\n'
        f'          data-fail="{label["fail"]}">{label["idle"]}</button>\n'
        f"</div>\n{END}"
    )


def anchor(text: str) -> int | None:
    """Offset at which the bar belongs: directly under the report's header.

    A real <header> element is the clean case. Plenty of reports instead open with an eyebrow,
    an <h1> and a lede paragraph inside the wrapper, with no header element at all -- for those,
    the equivalent position is after the title block, i.e. past the <p> runs that follow the <h1>.
    """
    close = re.search(r"</header\s*>", text, flags=re.I)
    if close:
        return close.end()

    title = re.search(r"</h1\s*>", text, flags=re.I)
    if not title:
        return None
    at = title.end()
    while True:
        following = re.match(r"\s*<p\b[^>]*>.*?</p\s*>", text[at:], flags=re.I | re.S)
        if not following:
            return at
        at += following.end()


def strip_previous(text: str) -> str:
    text = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END), "", text, flags=re.S)
    text = re.sub(re.escape(SCRIPT_BEGIN) + r".*?" + re.escape(SCRIPT_END), "", text, flags=re.S)
    return text


def conform(html_file: Path, name_override: str | None, forced_lang: str | None) -> str:
    """-> 'injected' | 'refreshed' | 'no-header'"""
    original = html_file.read_text(encoding="utf-8")
    had_block = BEGIN in original

    text = strip_previous(original)
    at = anchor(text)
    if at is None:
        return "no-header"

    facts = project_facts(html_file, name_override)
    block = build_block(facts, detect_lang(html_file, forced_lang, text))
    text = text[:at] + "\n\n" + block + text[at:]

    payload = f"\n{SCRIPT_BEGIN}\n{SCRIPT}\n{SCRIPT_END}\n"
    # Land the script inside the document rather than after </html>: browsers tolerate a trailing
    # script, but a file on disk should still be a valid document.
    tail = None
    for closer in (r"</body\s*>", r"</html\s*>"):
        found = list(re.finditer(closer, text, flags=re.I))
        if found:
            tail = found[-1].start()
            break
    text = text + payload if tail is None else text[:tail] + payload + text[tail:]

    html_file.write_text(text, encoding="utf-8", newline="")
    return "refreshed" if had_block else "injected"


def iter_reports(targets: list[str]):
    for raw in targets:
        path = Path(raw)
        if path.is_dir():
            yield from sorted(path.glob("*.html"))
        elif path.is_file():
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="Conform HTML reports to the mandated format.")
    parser.add_argument("targets", nargs="+", help="report files or directories of reports")
    parser.add_argument("--check", action="store_true", help="report only; exit 1 if work is due")
    parser.add_argument("--project-name", default=None, help="override the derived project name")
    parser.add_argument("--lang", choices=["ru", "en"], default=None, help="force label language")
    args = parser.parse_args()

    pending: list[Path] = []
    counts = {"injected": 0, "refreshed": 0, "no-header": 0}

    for report in iter_reports(args.targets):
        if args.check:
            text = report.read_text(encoding="utf-8")
            if BEGIN not in text:
                pending.append(report)
                print(f"  MISSING  {report}")
            continue
        result = conform(report, args.project_name, args.lang)
        counts[result] += 1
        marker = {"injected": "+", "refreshed": "~", "no-header": "!"}[result]
        print(f"  {marker} {result:<10} {report}")

    if args.check:
        if pending:
            print(f"{len(pending)} report(s) missing the mandated block")
            return 1
        print("all reports carry the mandated block")
        return 0

    print(
        f"injected {counts['injected']}, refreshed {counts['refreshed']}, "
        f"skipped {counts['no-header']} (no </header> to anchor to)"
    )
    return 1 if counts["no-header"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
