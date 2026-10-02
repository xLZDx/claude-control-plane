"""One view of what every Claude Code session on this machine has been doing.

Seven sessions each talk into their own terminal, so work that was reported can still go unseen.
This reads the session transcripts under ~/.claude/projects and prints a single table: which
project each session is in, when the operator last spoke to it, what it is doing right now, and
what it committed, pushed or published in the window.

Read-only. It opens transcript files and nothing else -- no git writes, no repository access, no
messages into other sessions.

    py -3 session_digest.py                     # last 24h, all sessions
    py -3 session_digest.py --since 3h          # narrower window
    py -3 session_digest.py --all               # include sessions idle longer than the window
    py -3 session_digest.py --html out.html     # house-format report (run report_conform.py after)

Transcripts are large (tens of MB), so every file is streamed line by line and only the fields
that end up on screen are kept.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS = Path.home() / ".claude" / "projects"

ARTIFACT_URL = re.compile(r"https://claude\.ai/code/artifact/[0-9a-f-]{36}")
# git prints `[branch 1a2b3c4] subject` on a successful commit
COMMIT_LINE = re.compile(r"\[([\w./-]+)\s+([0-9a-f]{7,40})\]\s*(.+)")
PUSH_CMD = re.compile(r"\bgit\s+push\b")
NOISE = ("<system-reminder>", "<task-notification>", "<local-command-stdout>", "Caveat: The messages below")


def parse_ts(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None


def local(dt: datetime | None) -> str:
    return dt.astimezone().strftime("%d.%m %H:%M") if dt else "--"


def parse_window(raw: str) -> timedelta:
    unit = raw[-1].lower()
    scale = {"h": "hours", "d": "days", "m": "minutes"}.get(unit)
    if not scale:
        raise argparse.ArgumentTypeError("window looks like 3h, 90m or 2d")
    return timedelta(**{scale: float(raw[:-1])})


def texts_of(message: dict) -> list[str]:
    """Every plain-text fragment of a message, tool calls and tool results excluded."""
    content = message.get("content")
    if isinstance(content, str):
        return [content]
    out = []
    for blk in content or []:
        if isinstance(blk, dict) and blk.get("type") == "text" and blk.get("text"):
            out.append(blk["text"])
    return out


def tool_uses(message: dict):
    for blk in message.get("content") or []:
        if isinstance(blk, dict) and blk.get("type") == "tool_use":
            yield blk.get("name"), blk.get("input") or {}


def tool_results(message: dict):
    for blk in message.get("content") or []:
        if isinstance(blk, dict) and blk.get("type") == "tool_result":
            body = blk.get("content")
            if isinstance(body, str):
                yield body
            else:
                for part in body or []:
                    if isinstance(part, dict) and part.get("type") == "text":
                        yield part.get("text", "")


def is_operator_text(raw: str) -> bool:
    stripped = raw.strip()
    return bool(stripped) and not any(stripped.startswith(n) or n in stripped[:200] for n in NOISE)


def read_session(path: Path, cutoff: datetime) -> dict | None:
    cwds: Counter = Counter()
    title = branch = None
    last_seen = last_operator = last_reply = None
    operator_text = reply_text = ""
    artifacts: list[tuple[datetime, str]] = []
    commits: list[tuple[datetime, str, str, str]] = []
    pushes: list[tuple[datetime, str]] = []

    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            kind = row.get("type")
            if kind == "ai-title":
                title = row.get("aiTitle") or title
                continue

            ts = parse_ts(row.get("timestamp"))
            if ts and (last_seen is None or ts > last_seen):
                last_seen = ts
            if row.get("cwd"):
                cwds[row["cwd"]] += 1
            if row.get("gitBranch"):
                branch = row["gitBranch"]

            if kind not in ("user", "assistant"):
                continue
            message = row.get("message") or {}
            recent = ts is not None and ts >= cutoff

            if kind == "user":
                for raw in texts_of(message):
                    if is_operator_text(raw) and ts and (last_operator is None or ts >= last_operator):
                        last_operator, operator_text = ts, raw
                if recent:
                    for body in tool_results(message):
                        for found in COMMIT_LINE.finditer(body):
                            commits.append((ts, found.group(1), found.group(2), found.group(3).strip()))
                        for url in ARTIFACT_URL.findall(body):
                            artifacts.append((ts, url))
                continue

            for raw in texts_of(message):
                if ts and (last_reply is None or ts >= last_reply):
                    last_reply, reply_text = ts, raw
                if recent:
                    for url in ARTIFACT_URL.findall(raw):
                        artifacts.append((ts, url))
            if recent:
                for name, params in tool_uses(message):
                    command = params.get("command") if isinstance(params.get("command"), str) else ""
                    if command and PUSH_CMD.search(command):
                        pushes.append((ts, command.strip()))

    if last_seen is None:
        return None

    seen: set[str] = set()
    unique_artifacts = []
    for ts, url in artifacts:
        if url not in seen:
            seen.add(url)
            unique_artifacts.append((ts, url))
    unique_commits = []
    seen_sha: set[str] = set()
    for ts, br, sha, subject in commits:
        if sha not in seen_sha:
            seen_sha.add(sha)
            unique_commits.append((ts, br, sha, subject))

    return {
        "id": path.stem,
        "title": title or "",
        "project": (cwds.most_common(1)[0][0] if cwds else "?"),
        "branch": branch or "",
        "last_seen": last_seen,
        "last_operator": last_operator,
        "operator_text": operator_text.strip(),
        "last_reply": last_reply,
        "reply_text": reply_text.strip(),
        "artifacts": unique_artifacts,
        "commits": unique_commits,
        "pushes": pushes,
    }


def collect(window: timedelta, keep_idle: bool) -> list[dict]:
    now = datetime.now(timezone.utc)
    cutoff = now - window
    found = []
    for path in PROJECTS.glob("*/*.jsonl"):
        if not keep_idle and datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < cutoff:
            continue
        session = read_session(path, cutoff)
        if session:
            found.append(session)
    found.sort(key=lambda s: s["last_seen"], reverse=True)
    return found


def clip(raw: str, limit: int) -> str:
    flat = " ".join(raw.split())
    return flat if len(flat) <= limit else flat[: limit - 1] + "…"


def render_text(sessions: list[dict], window: str) -> str:
    lines = [f"{len(sessions)} session(s) active in the last {window}", ""]
    for s in sessions:
        lines.append(f"{s['id'][:8]}  {s['project']}  [{s['branch']}]")
        if s["title"]:
            lines.append(f"    title      {clip(s['title'], 90)}")
        lines.append(f"    operator   {local(s['last_operator'])}  {clip(s['operator_text'], 90)}")
        lines.append(f"    now        {local(s['last_reply'])}  {clip(s['reply_text'], 90)}")
        for ts, br, sha, subject in s["commits"]:
            lines.append(f"    commit     {local(ts)}  {sha[:8]} [{br}] {clip(subject, 70)}")
        for ts, command in s["pushes"]:
            lines.append(f"    push       {local(ts)}  {clip(command, 80)}")
        for ts, url in s["artifacts"]:
            lines.append(f"    artifact   {local(ts)}  {url}")
        if not (s["commits"] or s["pushes"] or s["artifacts"]):
            lines.append("    (nothing committed, pushed or published in this window)")
        lines.append("")
    return "\n".join(lines)


LABELS = {
    "ru": {
        "title": "Пульс сессий",
        "eyebrow": "Все сессии Claude Code",
        "window": "окно",
        "h1": "Пульс сессий",
        "dek": "{n} активных сессий. За окно: {c} коммитов, {p} пушей, {a} опубликованных отчётов.",
        "untitled": "без названия",
        "branch": "ветка",
        "operator": "Последняя реплика оператора",
        "now": "Чем занята сейчас",
        "quiet": "ничего не закоммичено, не запушено и не опубликовано в этом окне",
    },
    "en": {
        "title": "Session Pulse",
        "eyebrow": "Every Claude Code session",
        "window": "window",
        "h1": "Session Pulse",
        "dek": "{n} active sessions. In this window: {c} commits, {p} pushes, {a} published reports.",
        "untitled": "untitled",
        "branch": "branch",
        "operator": "Operator last spoke",
        "now": "Doing right now",
        "quiet": "nothing committed, pushed or published in this window",
    },
}


def render_html(sessions: list[dict], window: str, lang: str = "ru") -> str:
    label = LABELS[lang]
    e = html.escape
    stamp = datetime.now().astimezone().strftime("%d.%m.%Y %H:%M")
    total_commits = sum(len(s["commits"]) for s in sessions)
    total_pushes = sum(len(s["pushes"]) for s in sessions)
    total_artifacts = sum(len(s["artifacts"]) for s in sessions)

    cards = []
    for s in sessions:
        events = []
        for ts, br, sha, subject in s["commits"]:
            events.append(
                f'<li><span class="tag commit">commit</span><span class="when">{local(ts)}</span>'
                f'<code>{e(sha[:8])}</code> <span class="branch">{e(br)}</span> {e(clip(subject, 110))}</li>'
            )
        for ts, command in s["pushes"]:
            events.append(
                f'<li><span class="tag push">push</span><span class="when">{local(ts)}</span>'
                f"<code>{e(clip(command, 90))}</code></li>"
            )
        for ts, url in s["artifacts"]:
            events.append(
                f'<li><span class="tag artifact">artifact</span><span class="when">{local(ts)}</span>'
                f'<a href="{e(url)}">{e(url)}</a></li>'
            )
        if not events:
            events.append(f'<li class="quiet">{label["quiet"]}</li>')

        subtitle = e(s["title"] or label["untitled"])
        if s["branch"]:
            subtitle += f' &middot; {label["branch"]} {e(s["branch"])}'

        cards.append(
            f"""<article class="session">
  <h2>{e(s['project'])} <span class="sid">{e(s['id'][:8])}</span></h2>
  <p class="title">{subtitle}</p>
  <dl class="pulse">
    <dt>{label['operator']}</dt><dd><span class="when">{local(s['last_operator'])}</span> {e(clip(s['operator_text'], 260))}</dd>
    <dt>{label['now']}</dt><dd><span class="when">{local(s['last_reply'])}</span> {e(clip(s['reply_text'], 260))}</dd>
  </dl>
  <ul class="events">{''.join(events)}</ul>
</article>"""
        )

    return f"""<title>{label['title']}</title>
<style>
:root {{
  --ground:#eef0f3; --surface:#fff; --surface-2:#f5f6f9; --ink:#15181e; --text:#15181e;
  --text-2:#3d4550; --text-3:#6e7885; --rule:#d4d9e0; --border:#d4d9e0;
  --accent:#1d5c86; --brass:#8a6420; --good:#2c6a4d; --warn:#a0561d; --ok:#2c6a4d; --bad:#97362e;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#111419; --surface:#181c23; --surface-2:#1e232b; --ink:#dfe3ea; --text:#dfe3ea;
    --text-2:#aeb6c2; --text-3:#7e8896; --rule:#2b313a; --border:#2b313a;
    --accent:#6fb3dc; --brass:#c9a24e; --good:#63b389; --warn:#d08a4e; --ok:#63b389; --bad:#d9736a;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#111419; --surface:#181c23; --surface-2:#1e232b; --ink:#dfe3ea; --text:#dfe3ea;
  --text-2:#aeb6c2; --text-3:#7e8896; --rule:#2b313a; --border:#2b313a;
  --accent:#6fb3dc; --brass:#c9a24e; --good:#63b389; --warn:#d08a4e; --ok:#63b389; --bad:#d9736a;
}}
body {{ margin:0; background:var(--ground); color:var(--text);
  font-family:Georgia,"Iowan Old Style",serif; font-size:16px; line-height:1.6; }}
.wrap {{ max-width:56rem; margin:0 auto; padding:3rem 1.5rem 4.5rem;
  display:flex; flex-direction:column; gap:2rem; }}
header.masthead {{ display:flex; flex-direction:column; gap:0.8rem;
  padding-bottom:1.4rem; border-bottom:2px solid var(--ink); }}
.eyebrow {{ margin:0; font-family:ui-monospace,Consolas,monospace; font-size:0.7rem;
  letter-spacing:0.15em; text-transform:uppercase; color:var(--brass); }}
h1 {{ margin:0; font-family:ui-sans-serif,"Segoe UI",system-ui,sans-serif; font-weight:750;
  font-size:clamp(1.9rem,5vw,2.8rem); line-height:1.06; letter-spacing:-0.026em; color:var(--ink); }}
.dek {{ margin:0; color:var(--text-2); }}
.session {{ background:var(--surface); border:1px solid var(--border); border-radius:3px;
  padding:1.1rem 1.25rem; }}
.session h2 {{ margin:0; font-family:ui-sans-serif,"Segoe UI",system-ui,sans-serif;
  font-size:1.05rem; font-weight:700; color:var(--ink); word-break:break-word; }}
.sid {{ font-family:ui-monospace,Consolas,monospace; font-size:0.72rem; color:var(--text-3);
  font-weight:400; margin-left:0.4rem; }}
.title {{ margin:0.15rem 0 0.9rem; font-size:0.85rem; color:var(--text-3); }}
.pulse {{ display:grid; grid-template-columns:auto 1fr; gap:0.35rem 1rem; margin:0 0 0.9rem;
  font-size:0.85rem; }}
.pulse dt {{ font-family:ui-monospace,Consolas,monospace; font-size:0.64rem; letter-spacing:0.08em;
  text-transform:uppercase; color:var(--text-3); white-space:nowrap; padding-top:0.25em; }}
.pulse dd {{ margin:0; color:var(--text-2); min-width:0; }}
.when {{ font-family:ui-monospace,Consolas,monospace; font-size:0.72rem; color:var(--text-3);
  margin-right:0.5rem; }}
.events {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:0.35rem;
  border-top:1px solid var(--rule); padding-top:0.8rem; font-size:0.82rem; }}
.events li {{ display:flex; align-items:baseline; gap:0.5rem; flex-wrap:wrap; color:var(--text-2); }}
.events code {{ font-family:ui-monospace,Consolas,monospace; font-size:0.78rem;
  background:var(--surface-2); border:1px solid var(--border); border-radius:2px; padding:0 0.3em; }}
.events a {{ color:var(--accent); word-break:break-all; }}
.events .quiet {{ color:var(--text-3); font-style:italic; }}
.tag {{ font-family:ui-monospace,Consolas,monospace; font-size:0.62rem; letter-spacing:0.08em;
  text-transform:uppercase; border:1px solid currentColor; border-radius:2px; padding:0.05em 0.4em; }}
.tag.commit {{ color:var(--accent); }}
.tag.push {{ color:var(--warn); }}
.tag.artifact {{ color:var(--good); }}
.branch {{ font-family:ui-monospace,Consolas,monospace; font-size:0.74rem; color:var(--text-3); }}
</style>

<div class="wrap">

<header class="masthead">
  <p class="eyebrow">{label['eyebrow']} &middot; {label['window']} {e(window)} &middot; {e(stamp)}</p>
  <h1>{label['h1']}</h1>
  <p class="dek">{label['dek'].format(n=len(sessions), c=total_commits, p=total_pushes, a=total_artifacts)}</p>
</header>

{''.join(cards)}

</div>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="What every Claude Code session has been doing.")
    parser.add_argument("--since", default="24h", help="window, e.g. 3h, 90m, 2d (default 24h)")
    parser.add_argument("--all", action="store_true", help="include sessions idle longer than the window")
    parser.add_argument(
        "--html",
        default=None,
        help="write the house-format report pair here; pass <NAME>.html and the Russian "
        "<NAME>.ru.html is written alongside it",
    )
    args = parser.parse_args()

    window = parse_window(args.since)
    sessions = collect(window, args.all)
    print(render_text(sessions, args.since))

    if args.html:
        # The house format is a pair, so the tool emits both rather than leaving the second
        # language as something to remember by hand.
        english = Path(args.html)
        if english.name.endswith(".ru.html"):
            english = english.with_name(english.name[: -len(".ru.html")] + ".html")
        russian = english.with_name(english.name[: -len(".html")] + ".ru.html")
        english.parent.mkdir(parents=True, exist_ok=True)
        for path, lang in ((russian, "ru"), (english, "en")):
            path.write_text(render_html(sessions, args.since, lang), encoding="utf-8", newline="")
            print(f"written {path}")
        print("Run report_conform.py on both to add the mandated block.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
