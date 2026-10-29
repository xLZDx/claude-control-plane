import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HOOK = Path(__file__).resolve().parents[2] / "hooks" / "session_supervisor_gate.py"
spec = importlib.util.spec_from_file_location("session_supervisor_gate", HOOK)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

PDCC_CWD = "D:\\Repo\\Personal_Decision_Command_Center"


def transcript(tmp: Path, text: str) -> str:
    path = tmp / "t.jsonl"
    entry = {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}
    path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
    return str(path)


class SessionSupervisorGateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        gate.SUPERVISOR_DIR = self.tmp / "sup"
        self.key = "k1"

    def run_gate(self, text, mode="live", cwd=PDCC_CWD, **extra):
        payload = {"session_id": "s1", "cwd": cwd, "transcript_path": transcript(self.tmp, text), **extra}
        return gate.decide(payload, mode, progress_key=lambda _cwd: self.key)

    def test_classify(self):
        self.assertEqual(gate.classify("Сделал часть. Продолжить дальше?"), "ASK_OPERATOR")
        self.assertEqual(gate.classify("Жду ваш GO на миграцию"), "ASK_OPERATOR")
        self.assertEqual(gate.classify("Блокер: OA-011 Telegram, нет credential"), "SAFE_STOP")
        self.assertEqual(gate.classify("Все гейты закрыты, итог APPROVE=GO"), "COMPLETE")
        self.assertEqual(gate.classify("Закоммитил WQ-17f и остановился на чекпойнте."), "IDLE")
        self.assertEqual(gate.classify(""), "IDLE")
        self.assertEqual(gate.classify("Вот промпт для новой сессии:\n```\nсделай X\n```"), "COMPLETE")
        for offer in ("Могу сделать это сам, если вы откроете новую сессию.", "Пришлите отдельное «ГО» на список.",
                      "Let me know if you want me to continue.", "Если хотите, проверю ещё раз."):
            self.assertEqual(gate.classify(offer), "ASK_OPERATOR", offer)

    def test_keep_going_closing_lines_are_a_legitimate_stop(self):
        for text in ("Сервис восстановлен.\n\nБлокеры: OPERATOR - коммит не запрашивался; сервис восстановлен.",
                     "Готово.\nБлокеры: EXTERNAL - таймер после показа окна вопроса хуком не реализуется",
                     "Блокеры: PROHIBITED - полные тесты запрещены",
                     "Блокеры: нет",
                     "Выполнимых задач не осталось"):
            self.assertEqual(gate.classify(text), "COMPLETE", text)
        # the same words in the middle of a long text must not excuse a plain stop
        self.assertEqual(gate.classify("Закоммитил и остановился на чекпойнте. Без блокеров."), "IDLE")

    def test_waiting_on_ci_is_its_own_category(self):
        shot = ("Жду результатов проверки verify-linux на коммите c3408b2f для PR #76 — фоновое ожидание "
                "уже запущено, и я сообщу, когда оно завершится.")
        self.assertEqual(gate.classify(shot), "WAITING")
        self.assertEqual(gate.classify("CI ещё идёт, лог пуст. Фоновое ожидание вернёт управление по завершении."), "WAITING")
        self.assertEqual(gate.classify("Waiting for CI checks on the head; will report back."), "WAITING")
        shot2 = ("Ждали зря: прогон сразу упал. Прогон запущен заново, сейчас идёт скачивание get-pip.py. "
                 "Пока он работает, начну готовить правку ci.yml. Через несколько минут проверю лог.")
        self.assertEqual(gate.classify(shot2), "WAITING")
        self.assertEqual(gate.classify("Когда прогон завершится, сверю результат."), "WAITING")
        self.assertEqual(gate.classify("The tests are running in the background; I'll check back in 10 minutes."), "WAITING")
        self.assertEqual(gate.classify("Жду ваш GO на мерж."), "ASK_OPERATOR")  # operator wait wins
        # the Stop hook cannot help a wait (the event may finish later): it allows and leaves it to the watchdog
        self.assertIsNone(self.run_gate(shot))
        self.assertIn('"reason": "WAITING"', (gate.SUPERVISOR_DIR / "supervisor.jsonl").read_text(encoding="utf-8"))

    def test_project_mapping(self):
        cases = {
            PDCC_CWD: "pdcc",
            "D:\\Repo\\PDCC_wt_gov\\apps": "pdcc",
            "D:\\Repo\\AIRA\\core": "aira",
            "D:\\Repo\\Fitness_App\\mobile": "fitness",
            "D:\\Repo\\ERP": "erp",
            "D:\\Repo\\ERP_MVP1_WORKTREE\\frontend-web": "erp",
            "D:\\Repo\\Ferma": "ferma",
            "D:\\Repo\\AI_trading_assistance": "trading",
            "D:\\Repo\\Remote_Quality_Delivery_Office_Platform_rqdo\\backend": "rqdo",
        }
        for cwd, key in cases.items():
            self.assertEqual(gate.project_of(cwd), key, cwd)

    def test_unlisted_stale_and_lookalike_ignored(self):
        for cwd in (
            "D:\\rqdo-platform.STALE-2026-07-31",
            "D:\\Repo\\rqdo-platform.STALE-2026-07-31",
            "D:\\Repo",  # workspace root: cross-project sessions
            "C:\\Users\\koros",
            "D:\\Repo\\pm-bridge",  # shared daemon: never resumed
            "D:\\Repo\\pm-bridge-codex",
            "D:\\Repo\\Ferma_Independent_Audit_2026-08-25",
            "D:\\Repo\\PDCC_private_backups",
        ):
            self.assertIsNone(gate.project_of(cwd), cwd)

    def test_any_other_project_gets_generic_supervision(self):
        for cwd in ("D:\\Repo\\TENDER", "D:\\Repo\\ERPX", "D:\\Repo\\AIRAFOO", "D:\\Repo\\Life_Companion\\src"):
            self.assertEqual(gate.project_of(cwd), "other", cwd)
        out = self.run_gate("остановился на чекпойнте", cwd="D:\\Repo\\TENDER")
        self.assertEqual(out["decision"], "block")
        self.assertIn(gate.OTHER_HINT, out["reason"])

    def test_idle_stop_is_blocked_live_with_project_hint(self):
        out = self.run_gate("Закоммитил и остановился на чекпойнте.", cwd="D:\\Repo\\Ferma")
        self.assertEqual(out["decision"], "block")
        self.assertIn("FERMA_POST_AUDIT_PRODUCT_EXECUTION_PLAN.md", out["reason"])

    def test_dry_run_never_blocks_but_logs(self):
        self.assertIsNone(self.run_gate("остановился на чекпойнте", mode="dry-run"))
        log = (gate.SUPERVISOR_DIR / "supervisor.jsonl").read_text(encoding="utf-8")
        self.assertIn("would_block", log)
        self.assertIn('"project": "pdcc"', log)

    def test_legitimate_stops_are_allowed(self):
        for text in ("Нужен ваш GO.", "Готов ли продолжить?", "Блокер OA-012 Android", "Все гейты закрыты"):
            self.assertIsNone(self.run_gate(text), text)

    def test_stop_hook_active_never_blocks(self):
        self.assertIsNone(self.run_gate("остановился", stop_hook_active=True))

    def test_nudge_cap_then_escalate(self):
        results = [self.run_gate("остановился на чекпойнте") for _ in range(gate.MAX_NUDGES + 1)]
        self.assertTrue(all(r for r in results[:-1]))
        self.assertIsNone(results[-1])
        self.assertIn("ESCALATE", (gate.SUPERVISOR_DIR / "supervisor.jsonl").read_text(encoding="utf-8"))

    def test_progress_resets_counter(self):
        for _ in range(gate.MAX_NUDGES):
            self.run_gate("остановился на чекпойнте")
        self.key = "k2"
        self.assertEqual(self.run_gate("остановился на чекпойнте")["decision"], "block")

    def test_off_mode(self):
        self.assertIsNone(self.run_gate("остановился", mode="off"))


if __name__ == "__main__":
    unittest.main()
