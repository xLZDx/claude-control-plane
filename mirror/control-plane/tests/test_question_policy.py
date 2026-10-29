import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "hooks" / "question_policy.py"
PY = r"C:\Python314\python.exe"


def iso(minutes_ago):
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat().replace("+00:00", "Z")


def human(minutes_ago, text="работай дальше"):
    return {"type": "user", "timestamp": iso(minutes_ago), "message": {"role": "user", "content": [{"type": "text", "text": text}]}}


def bridge_call(minutes_ago, tid):
    return {"type": "assistant", "timestamp": iso(minutes_ago), "message": {"role": "assistant", "content": [
        {"type": "tool_use", "id": tid, "name": "mcp__pm-bridge__gpt_session_peek", "input": {}}]}}


def bridge_result(minutes_ago, tid, text="gpt_session_peek error: This operation was aborted"):
    return {"type": "user", "timestamp": iso(minutes_ago), "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": tid, "content": [{"type": "text", "text": text}]}]}}


def cron_prompt(minutes_ago, meta=True):
    """Shaped like a real scheduled-task row (see session 11012554): isMeta, turnOrigin=scheduled, promptSource=system."""
    row = {"type": "user", "timestamp": iso(minutes_ago), "turnOrigin": "scheduled", "promptSource": "system",
           "message": {"role": "user", "content": "AUTONOMOUS RESUME: continue the plan"}}
    if meta:
        row["isMeta"] = True
    return row


def question(recommended_first=True, text="Как поступить с зависшим мостом?"):
    rec = {"label": "Подождать 30 минут (Recommended)", "description": "ничего не ломаем"}
    other = {"label": "Перезапустить мост", "description": "сбивает чужие сессии"}
    return {"questions": [{"question": text, "header": "Мост", "multiSelect": False,
                           "options": [rec, other] if recommended_first else [other, rec]}]}


class QuestionPolicyTest(unittest.TestCase):
    def setUp(self):
        self.state = Path(tempfile.mkdtemp(prefix="qp_state_"))
        self.work = Path(tempfile.mkdtemp(prefix="qp_tr_"))

    def run_hook(self, rows, tool_input=None, config=None, env=None):
        if config is not None:
            (self.state / "config.json").write_text(json.dumps(config), encoding="utf-8")
        tp = self.work / "t.jsonl"
        tp.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        payload = {"hook_event_name": "PreToolUse", "tool_name": "AskUserQuestion", "session_id": "abcd1234ef",
                   "transcript_path": str(tp), "tool_input": tool_input or question()}
        e = dict(os.environ, CLAUDE_QUESTION_POLICY_STATE=str(self.state))
        e.pop("CLAUDE_QUESTION_POLICY", None)
        e.update(env or {})
        r = subprocess.run([PY, "-s", str(HOOK)], input=json.dumps(payload), capture_output=True, text=True, env=e, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)["hookSpecificOutput"] if r.stdout.strip() else None

    def ledger(self):
        p = self.state / "auto_answers.jsonl"
        return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []

    def test_screenshot_case_bridge_error_does_not_reset_the_clock(self):
        # operator last wrote 258 min ago; the bridge errored 0.13 min (8 s) before the question
        rows = [human(258), bridge_call(5, "b1"), bridge_result(0.13, "b1")]
        out = self.run_hook(rows)
        self.assertEqual(out["permissionDecision"], "allow")
        self.assertEqual(list(out["updatedInput"]["answers"].values()), ["Подождать 30 минут (Recommended)"])
        self.assertEqual(self.ledger()[0]["action"], "auto-accepted")

    def test_default_threshold_is_five_minutes(self):
        self.assertIsNone(self.run_hook([human(4)]))  # operator wrote 4 min ago -> still around
        self.assertEqual(self.run_hook([human(6)])["permissionDecision"], "allow")  # 6 min of silence -> accept

    def test_many_bridge_replies_and_cron_prompts_do_not_count(self):
        rows = [human(40)]
        for i in range(6):
            rows += [bridge_call(3 - i * 0.4, f"b{i}"), bridge_result(2.9 - i * 0.4, f"b{i}", "ok: still generating")]
        rows.append(cron_prompt(0.5))
        self.assertEqual(self.run_hook(rows)["permissionDecision"], "allow")

    def test_scheduled_turn_is_not_the_operator_even_without_the_meta_flag(self):
        self.assertEqual(self.run_hook([human(40), cron_prompt(0.5, meta=False)])["permissionDecision"], "allow")

    def test_operator_message_resets_the_clock(self):
        rows = [human(300), bridge_result(1, "x"), human(2)]
        self.assertIsNone(self.run_hook(rows))

    def test_tail_without_any_operator_message_uses_lower_bound(self):
        rows = [bridge_call(90, "b1"), bridge_result(80, "b1"), bridge_call(1, "b2"), bridge_result(0.1, "b2")]
        self.assertEqual(self.run_hook(rows)["permissionDecision"], "allow")  # tail spans 90 min, no operator text

    def test_empty_transcript_shows_the_question(self):
        self.assertIsNone(self.run_hook([]))

    def test_destructive_question_is_never_auto_accepted(self):
        q = question()
        q["questions"][0]["header"] = "Удалить ветку"
        self.assertIsNone(self.run_hook([human(600)], tool_input=q))
        self.assertEqual(self.ledger()[0]["action"], "kept-for-operator-destructive")

    def test_destructive_words_are_scanned_only_in_the_header(self):
        # real case 2026-10-25: "волне W2 (удаление аккаунта, ...)" in the text must not block the auto-answer
        q = question(text="Удалить ветку и сделать force push? Проверка по волне W2 (удаление аккаунта)")
        q["questions"][0]["options"][0]["label"] = "Удалить ветку (Recommended)"
        q["questions"][0]["options"][1]["description"] = "удалит данные"
        self.assertEqual(self.run_hook([human(600)], tool_input=q)["permissionDecision"], "allow")

    def test_format_violations_are_still_denied(self):
        out = self.run_hook([human(600)], tool_input=question(recommended_first=False))
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("must be first", out["permissionDecisionReason"])

    def test_config_threshold_and_switches_are_honoured(self):
        self.assertIsNone(self.run_hook([human(20)], config={"idle_minutes": 30}))
        self.assertEqual(self.run_hook([human(40)], config={"idle_minutes": 30})["permissionDecision"], "allow")
        self.assertIsNone(self.run_hook([human(600)], config={"auto_accept": False}))
        self.assertIsNone(self.run_hook([human(600)], env={"CLAUDE_QUESTION_POLICY": "off"}))

    def test_live_config_file_is_five_minutes(self):
        live = json.loads(Path(r"D:\tmp\claude_question_policy\config.json").read_text(encoding="utf-8"))
        self.assertEqual(live["idle_minutes"], 5)


if __name__ == "__main__":
    unittest.main()
