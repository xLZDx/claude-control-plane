"""Tests for PM mode as a program-mode trigger (2026-08-26).

The change is small and its failure mode is silent in BOTH directions, which is why it is tested
rather than eyeballed:

  * too permissive -- a stale `orchestrator.json` left by a crashed process would disable the
    report gates indefinitely, in every project, with nothing to show for it;
  * too strict -- if `pm_mode_active()` never returns True, everything keeps working exactly as
    before and the sessions the operator complained about keep stopping. That is the failure that
    looks like success, so every case below asserts a behaviour CHANGE between PM-off and PM-on,
    not merely that the hooks still run.

Run:  py -3 test_pm_mode_gates.py
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path

HOOKS = Path(r"C:\Users\koros\.claude\hooks")
sys.path.insert(0, str(HOOKS))

import _report_common as rc  # noqa: E402

FAILURES: list[str] = []


def check(label: str, cond: bool, detail: str = "") -> None:
    print(f"  {'PASS' if cond else 'FAIL'}  {label}")
    if not cond:
        if detail:
            print(f"        {detail.strip()[:400]}")
        FAILURES.append(label)


@contextmanager
def listener(*, accept: bool = True):
    """A real socket on a real port -- the only honest stand-in for a live orchestrator.

    It must ACCEPT, not merely listen. `pm_mode_active` probes by connecting and closing, so a
    listener that never accepts fills its backlog after the first probe and every later one is
    refused or times out -- which looks exactly like "PM mode went off by itself". That is not
    hypothetical: it produced two false failures on this suite's first run, and it is the same
    shape as a bug in the thing under test, so the fixture models the real server instead.
    """
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    sock.listen(64)
    stop = False

    def drain():
        while not stop:
            try:
                conn, _ = sock.accept()
                conn.close()
            except OSError:
                return

    thread = threading.Thread(target=drain, daemon=True) if accept else None
    if thread:
        thread.start()
    try:
        yield sock.getsockname()[1]
    finally:
        stop = True
        sock.close()


def dead_port() -> int:
    """A port nothing is listening on: bind, read the number, release it."""
    with listener(accept=False) as port:
        pass
    return port


def write_state(state_dir: Path, port: int, age_seconds: float = 0.0) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "orchestrator.json"
    path.write_text(json.dumps({"pid": 4242, "port": port, "startedAt": "x"}), encoding="utf-8")
    if age_seconds:
        old = time.time() - age_seconds
        os.utime(path, (old, old))


def transcript_with_unanswered_handover(path: Path, report: str, url: str) -> None:
    """An assistant handover with no operator message after it -- what `report_gate` denies on."""
    rows = [
        {"type": "user", "message": {"content": "сделай отчёт"}},
        {"type": "assistant",
         "message": {"content": [{"type": "text", "text": f"Готово: {report}\n{url}"}]}},
    ]
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")


def run_hook(script: str, payload: dict, env_extra: dict) -> tuple[int, str]:
    env = dict(os.environ)
    env.update(env_extra)
    done = subprocess.run(
        [sys.executable, str(HOOKS / script)],
        input=json.dumps(payload, ensure_ascii=False),
        capture_output=True, text=True, env=env, timeout=60,
    )
    return done.returncode, (done.stdout or "") + (done.stderr or "")


REPORT = r"reports\PM_TEST_REPORT.ru.html"
URL = "https://claude.ai/code/artifact/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="pm_mode_test_"))
    state = tmp / "state"
    hook_state = tmp / "hookstate"
    transcript = tmp / "session.jsonl"
    transcript_with_unanswered_handover(transcript, REPORT, URL)

    # ---- pm_mode_active: detection itself -----------------------------------------------------
    print("pm_mode_active")
    os.environ["PM_BRIDGE_STATE_DIR"] = str(state)
    check("no state file -> off", rc.pm_mode_active() is False)

    write_state(state, dead_port())
    check("state file but nothing listening -> off (stale record ignored)",
          rc.pm_mode_active() is False)

    with listener() as port:
        write_state(state, port)
        check("state file + live port -> on", rc.pm_mode_active() is True)

        write_state(state, port, age_seconds=rc.PM_MODE_MAX_AGE_SECONDS + 60)
        check("live port but record older than the age bound -> off",
              rc.pm_mode_active() is False)

        write_state(state, port)
        check("program_mode_active is true from PM mode alone, with no declaration in transcript",
              rc.program_mode_active(str(transcript)) is True)

    del os.environ["PM_BRIDGE_STATE_DIR"]

    # ---- skill_hint: the instruction that actually made sessions stop -------------------------
    print("skill_hint")
    check("step 6 says STOP when PM mode is off", "ОСТАНОВИТЬСЯ" in rc.skill_hint(False))
    check("step 6 says CONTINUE when PM mode is on", "ПРОДОЛЖАТЬ" in rc.skill_hint(True))
    check("the two variants genuinely differ", rc.skill_hint(True) != rc.skill_hint(False))

    # ---- report_gate: unanswered handover ------------------------------------------------------
    print("report_gate (unanswered handover -> git commit)")
    payload = {
        "tool_input": {"command": "git commit -m x"},
        "transcript_path": str(transcript),
        "cwd": str(tmp),
    }
    base_env = {"CLAUDE_HOOK_STATE_DIR": str(hook_state), "PM_BRIDGE_STATE_DIR": str(state)}

    write_state(state, dead_port())  # PM mode off
    code, out = run_hook("report_gate.py", payload, base_env)
    check("PM off -> commit DENIED on the unanswered handover", '"deny"' in out, out)

    with listener() as port:
        write_state(state, port)  # PM mode on
        code, out = run_hook("report_gate.py", payload, base_env)
        check("PM on  -> same commit ALLOWED", code == 0 and '"deny"' not in out, out)

    # The pre-existing path must keep working: PM mode is an ADDITIONAL trigger, not a replacement
    # for the operator's marker phrase, and a regression there would be invisible (the gate would
    # simply start denying commits again in every long run that relies on the phrase).
    declared = tmp / "declared.jsonl"
    declared.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in [
        {"type": "user", "message": {"content": "не останавливаться после каждого сабгейта"}},
        {"type": "assistant",
         "message": {"content": [{"type": "text", "text": f"{REPORT}\n{URL}"}]}},
    ]), encoding="utf-8")
    write_state(state, dead_port())  # PM mode off, so only the declaration can allow this
    code, out = run_hook("report_gate.py", payload | {"transcript_path": str(declared)}, base_env)
    check("declared program mode still allows with PM mode off (no regression)",
          code == 0 and '"deny"' not in out, out)

    # ---- report_due: the continue nudge --------------------------------------------------------
    print("report_due (continue nudge after a handover)")
    due_payload = {
        "last_assistant_message": f"Отчёт: {REPORT}\n{URL}",
        "transcript_path": str(transcript),
        "cwd": str(tmp),
    }

    write_state(state, dead_port())  # PM mode off
    code, out = run_hook("report_due.py", due_payload, base_env)
    check("PM off -> no nudge", "ПМ-РЕЖИМ" not in out, out)

    with listener() as port:
        write_state(state, port)  # PM mode on
        code, out = run_hook("report_due.py", due_payload, base_env)
        check("PM on  -> nudged to continue", "ПМ-РЕЖИМ" in out, out)
        check("the nudge blocks the stop", '"block"' in out, out)

        code, out2 = run_hook("report_due.py", due_payload, base_env)
        check("second stop for the same report is NOT nudged again (cannot livelock)",
              "ПМ-РЕЖИМ" not in out2, out2)

        other = due_payload | {
            "last_assistant_message":
                f"Отчёт: {REPORT}\nhttps://claude.ai/code/artifact/11111111-2222-3333-4444-555555555555"
        }
        code, out3 = run_hook("report_due.py", other, base_env)
        check("a DIFFERENT report is nudged (dedup is per report, not per session)",
              "ПМ-РЕЖИМ" in out3, out3)

        plain = due_payload | {"last_assistant_message": "Починил опечатку в комментарии."}
        code, out4 = run_hook("report_due.py", plain, base_env)
        check("an ordinary turn with no handover is never nudged", "ПМ-РЕЖИМ" not in out4, out4)

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURE(S): " + "; ".join(FAILURES))
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
