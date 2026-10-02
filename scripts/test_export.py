import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import export_from_claude_home as ex  # noqa: E402


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
        self.assertFalse(ex.scan_text("test@example.com git@github.com"))

    def test_flags_chatgpt_conversation_link(self):
        self.assertTrue(ex.scan_text("https://chatgpt.com/c/6abf8c09-621c-83eb-a5f1-855dd621ce18"))

    def test_plain_policy_text_is_clean(self):
        self.assertFalse(ex.scan_text("Opus is never automatic; use the sonnet alias."))


if __name__ == "__main__":
    unittest.main()
