"""Negative + positive tests for agent_model_gate.py and agentctl.py. Fixtures live in a temp dir; the real
~/.claude config is never modified.   Run:  C:\\Python314\\python.exe -m unittest discover -s <this dir> -v
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CP = Path(__file__).resolve().parents[1]
REAL_HOME = CP.parent
GATE = REAL_HOME / "hooks" / "agent_model_gate.py"
LINT = CP / "agentctl.py"


def agent_md(name, model="sonnet", effort="medium", turns="10", extra="", desc="Reviews things when X changes."):
    fm = [f"name: {name}", f"description: {desc}", "tools:", "- Read"]
    if model:
        fm.append(f"model: {model}")
    if effort:
        fm.append(f"effort: {effort}")
    if turns:
        fm.append(f"maxTurns: {turns}")
    if extra:
        fm.append(extra)
    return "---\n" + "\n".join(fm) + "\n---\n\nBody.\n"


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class Fixture:
    """A fake ~/.claude plus a fake workspace with one canonical project."""

    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cp-test-"))
        self.home = self.tmp / "home"
        self.repo = self.tmp / "repo"
        (self.home / "hooks").mkdir(parents=True)
        (self.home / "control-plane").mkdir(parents=True)
        shutil.copy(GATE, self.home / "hooks" / "agent_model_gate.py")
        write(self.home / "settings.json", json.dumps({
            "model": "sonnet", "effortLevel": "medium", "env": {"CLAUDE_CODE_SUBAGENT_MODEL": "sonnet"},
            "modelSettings": {"claude-opus-5-5": {"effortLevel": "high"}},
            "hooks": {"PreToolUse": [{"matcher": "Agent", "hooks": [
                {"type": "command", "command": "python", "args": ["agent_model_gate.py"]}]}]}}))
        write(self.home / "agent_routing.json", json.dumps({
            "groups": {"A": {"agents": ["code-reviewer", "<language-reviewer-slot>"]}},
            "language_reviewer_slot": {"by_extension": {".py": "code-reviewer"}},
            "_control_plane_v2": {"disabled_unresolved_agents": []}}))
        write(self.home / "CLAUDE.md", "global rules\n")
        write(self.home / "agents" / "code-reviewer.md", agent_md("code-reviewer"))
        write(self.home / "agents" / "legacy-thing.md", agent_md("legacy-thing", extra="deprecated: true\nsuperseded_by: code-reviewer"))
        write(self.home / "agents" / "opus-thing.md", agent_md("opus-thing", model="opus", effort="high"))
        write(self.home / "skills" / "demo-skill" / "SKILL.md", "---\nname: demo-skill\ndescription: Demo.\n---\n" + "word " * 200)
        (self.repo / "proj" / ".claude" / "agents").mkdir(parents=True)
        (self.repo / ".claude" / "agents").mkdir(parents=True)
        write(self.repo / "proj" / "CLAUDE.md", "project rules\n")
        write(self.repo / "proj" / ".claude" / "agents" / "proj-reviewer.md", agent_md("proj-reviewer"))
        self.projects = self.tmp / "projects.json"
        write(self.projects, json.dumps({"repo_root": str(self.repo), "canonical": {"proj": {"workspace_prefix": "proj-"}},
                                         "temporary_copies": [], "limits": {}}))

    def env(self, **extra):
        e = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "CLAUDE_CODE_SUBAGENT_MODEL")}
        e["CLAUDE_CONTROL_PLANE_HOME"] = str(self.home)
        e["CLAUDE_CODE_SUBAGENT_MODEL"] = "sonnet"
        e.update(extra)
        return e

    def gate(self, tool_input=None, tool="Agent", raw=None, cwd=None, **env):
        payload = raw if raw is not None else json.dumps({"tool_name": tool, "tool_input": tool_input or {}, "cwd": str(cwd or self.repo)})
        r = subprocess.run([sys.executable, str(GATE)], input=payload.encode("utf-8"), capture_output=True, env=self.env(**env))
        out = r.stdout.decode("utf-8")
        decision = json.loads(out)["hookSpecificOutput"]["permissionDecision"] if out.strip() else "allow"
        return r.returncode, decision, out + r.stderr.decode("utf-8")

    def lint(self, strict=True):
        args = [sys.executable, str(LINT), "--home", str(self.home), "--repo", str(self.repo),
                "--projects", str(self.projects), "--no-write"] + (["--strict"] if strict else [])
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
        return r.returncode, r.stdout + r.stderr

    def cleanup(self):
        shutil.rmtree(self.tmp, ignore_errors=True)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.cleanup)

    def test_sonnet_canonical_agent_allowed(self):
        self.assertEqual(self.f.gate({"subagent_type": "code-reviewer"})[:2], (0, "allow"))

    def test_explicit_sonnet_alias_and_full_ids(self):
        for m in ("sonnet", "claude-sonnet-5-5", "claude-sonnet-5-6", "claude-sonnet-6-0"):
            self.assertEqual(self.f.gate({"subagent_type": "code-reviewer", "model": m})[1], "allow", m)

    def test_explicit_opus_denied(self):
        for m in ("opus", "claude-opus-5-5", "Opus"):
            rc, dec, msg = self.f.gate({"subagent_type": "code-reviewer", "model": m})
            self.assertEqual((rc, dec), (0, "deny"), m)
            self.assertIn("consent", msg)

    def test_lower_families_and_old_sonnet_denied(self):
        for m in ("haiku", "claude-haiku-4-5-20251001", "fable", "claude-fable-5-1", "claude-sonnet-5", "claude-sonnet-4-5", "claude-sonnet-5-4", "gpt-5"):
            self.assertEqual(self.f.gate({"subagent_type": "code-reviewer", "model": m})[1], "deny", m)

    def test_agent_file_declaring_opus_denied(self):
        self.assertEqual(self.f.gate({"subagent_type": "opus-thing"})[1], "deny")

    def test_project_override_precedence(self):
        # project-local opus overrides a global sonnet agent -> must be denied
        write(self.f.repo / "proj" / ".claude" / "agents" / "code-reviewer.md", agent_md("code-reviewer", model="opus", effort="high"))
        self.assertEqual(self.f.gate({"subagent_type": "code-reviewer"}, cwd=self.f.repo / "proj")[1], "deny")
        # outside that project the global sonnet definition applies
        self.assertEqual(self.f.gate({"subagent_type": "code-reviewer"}, cwd=self.f.repo)[1], "allow")
        # project-local sonnet overrides a global opus agent -> allowed inside the project, denied outside
        write(self.f.repo / "proj" / ".claude" / "agents" / "opus-thing.md", agent_md("opus-thing"))
        self.assertEqual(self.f.gate({"subagent_type": "opus-thing"}, cwd=self.f.repo / "proj")[1], "allow")
        self.assertEqual(self.f.gate({"subagent_type": "opus-thing"}, cwd=self.f.repo)[1], "deny")

    def test_missing_agent_is_reported_not_blocked_when_subagent_model_is_sonnet(self):
        rc, dec, msg = self.f.gate({"subagent_type": "does-not-exist"})
        self.assertEqual((rc, dec), (0, "allow"))
        self.assertIn("no definition", msg)

    def test_missing_agent_fails_closed_when_inherited_model_is_not_sonnet(self):
        rc, dec, _ = self.f.gate({"subagent_type": "does-not-exist"}, CLAUDE_CODE_SUBAGENT_MODEL="opus")
        self.assertEqual((rc, dec), (0, "deny"))

    def test_deprecated_agent_denied_with_successor(self):
        rc, dec, msg = self.f.gate({"subagent_type": "legacy-thing"})
        self.assertEqual((rc, dec), (0, "deny"))
        self.assertIn("code-reviewer", msg)

    def _rules(self, markers):
        write(self.f.home / "control-plane" / "deprecated_agents.json", json.dumps({"rules": [
            {"project": "proj", "path_markers": markers, "agents": {"old-01": "proj-reviewer"}}]}))

    def test_path_rule_denies_legacy_alias_even_without_frontmatter_flag(self):
        self._rules(["proj"])
        write(self.f.repo / "proj" / ".claude" / "agents" / "old-01.md", agent_md("old-01"))
        wt = self.f.repo / "proj_wt_x"  # a worktree copy of an older branch: no deprecated flag, path still matches
        write(wt / ".claude" / "agents" / "old-01.md", agent_md("old-01"))
        for cwd in (self.f.repo / "proj", wt):
            rc, dec, msg = self.f.gate({"subagent_type": "old-01"}, cwd=cwd)
            self.assertEqual((rc, dec), (0, "deny"), cwd)
            self.assertIn("proj-reviewer", msg)

    def test_path_rule_does_not_leak_to_other_projects(self):
        self._rules(["proj"])
        other = self.f.repo / "elsewhere"
        write(other / ".claude" / "agents" / "old-01.md", agent_md("old-01"))
        self.assertEqual(self.f.gate({"subagent_type": "old-01"}, cwd=other)[1], "allow")

    def test_malformed_rules_file_fails_closed_for_agent_calls_only(self):
        write(self.f.home / "control-plane" / "deprecated_agents.json", "{broken")
        write(self.f.repo / "proj" / ".claude" / "agents" / "old-01.md", agent_md("old-01"))
        self.assertEqual(self.f.gate({"subagent_type": "old-01"}, cwd=self.f.repo / "proj")[0], 2)
        self.assertEqual(self.f.gate({"command": "ls"}, tool="Bash")[:2], (0, "allow"))

    def test_invalid_effort_denied(self):
        write(self.f.home / "agents" / "bad-effort.md", agent_md("bad-effort", effort="max"))
        self.assertEqual(self.f.gate({"subagent_type": "bad-effort"})[1], "deny")

    def test_malformed_payload_fails_closed(self):
        for raw in ("{not json", "[]", "\"str\""):
            self.assertEqual(self.f.gate(raw=raw)[0], 2, raw)

    def test_non_agent_tools_untouched(self):
        self.assertEqual(self.f.gate({"command": "echo hi", "model": "opus"}, tool="Bash")[:2], (0, "allow"))

    def test_utf16_payload_decoded(self):
        payload = json.dumps({"tool_name": "Agent", "tool_input": {"subagent_type": "code-reviewer", "model": "opus"}, "cwd": str(self.f.repo)})
        r = subprocess.run([sys.executable, str(GATE)], input=payload.encode("utf-16"), capture_output=True, env=self.f.env())
        self.assertIn("deny", r.stdout.decode("utf-8"))


class LintTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()
        self.addCleanup(self.f.cleanup)

    def test_clean_fixture_passes_strict(self):
        write(self.f.home / "agents" / "opus-thing.md", agent_md("opus-thing"))  # make it Sonnet
        write(self.f.home / "agents" / "legacy-thing.md", agent_md("legacy-thing", extra="deprecated: true\nsuperseded_by: code-reviewer"))
        rc, out = self.f.lint()
        self.assertEqual(rc, 0, out)

    def test_agent_loading_missing_skill_fails_then_existing_skill_passes(self):
        self._clean()
        write(self.f.home / "agents" / "loader.md", agent_md("loader", extra="skills:\n- no-such-skill"))
        rc, out = self.f.lint()
        self.assertEqual(rc, 2, out)
        self.assertIn("SKILL_UNRESOLVED", out)
        write(self.f.home / "agents" / "loader.md", agent_md("loader", extra="skills:\n- demo-skill"))
        self.assertEqual(self.f.lint()[0], 0)

    def test_tier_mismatch_is_reported_but_not_fatal(self):
        self._clean()
        routing = self.f.home / "agent_routing.json"
        data = json.loads(routing.read_text(encoding="utf-8"))
        data["risk_routing"] = {"effort_tiers": {"T4": {"effort": "xhigh"}}, "agent_effort_tier": {"code-reviewer": "T4"}}
        routing.write_text(json.dumps(data), encoding="utf-8")
        rc, out = self.f.lint()
        self.assertEqual(rc, 0, out)
        data["risk_routing"]["agent_effort_tier"]["ghost-agent"] = "T4"
        routing.write_text(json.dumps(data), encoding="utf-8")
        rc, out = self.f.lint()
        self.assertEqual(rc, 2, out)
        self.assertIn("TIER_UNRESOLVED", out)

    def test_runnable_opus_agent_fails_strict(self):
        rc, out = self.f.lint()  # fixture ships opus-thing.md as a runnable Opus agent
        self.assertEqual(rc, 2, out)
        self.assertIn("MODEL", out)

    def _clean(self):
        write(self.f.home / "agents" / "opus-thing.md", agent_md("opus-thing"))

    def test_missing_route_fails_then_restore_passes(self):
        self._clean()
        routing = self.f.home / "agent_routing.json"
        good = routing.read_text(encoding="utf-8")
        data = json.loads(good)
        data["groups"]["A"]["agents"].append("fake-missing-agent")
        routing.write_text(json.dumps(data), encoding="utf-8")
        rc, out = self.f.lint()
        self.assertEqual(rc, 2, out)
        self.assertIn("ROUTE_UNRESOLVED", out)
        routing.write_text(good, encoding="utf-8")
        self.assertEqual(self.f.lint()[0], 0)

    def test_route_to_deprecated_agent_fails(self):
        self._clean()
        routing = self.f.home / "agent_routing.json"
        data = json.loads(routing.read_text(encoding="utf-8"))
        data["groups"]["A"]["agents"].append("legacy-thing")
        routing.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(self.f.lint()[0], 2)

    def test_turn_cap_and_exception(self):
        self._clean()
        write(self.f.home / "agents" / "big.md", agent_md("big", turns="50"))
        self.assertEqual(self.f.lint()[0], 2)
        write(self.f.home / "agents" / "big.md", agent_md("big", turns="50", extra="turnException: true"))
        self.assertEqual(self.f.lint()[0], 0)

    def test_invalid_effort_fails(self):
        self._clean()
        write(self.f.home / "agents" / "x.md", agent_md("x", effort="max"))
        self.assertEqual(self.f.lint()[0], 2)

    def test_opus_without_high_effort_fails(self):
        write(self.f.home / "agents" / "opus-thing.md", agent_md("opus-thing", model="opus", effort="xhigh"))
        rc, out = self.f.lint()
        self.assertEqual(rc, 2)
        self.assertIn("OPUS_EFFORT", out)

    def test_workspace_leak_fails(self):
        self._clean()
        write(self.f.repo / ".claude" / "agents" / "proj-auditor.md", agent_md("proj-auditor"))
        rc, out = self.f.lint()
        self.assertEqual(rc, 2, out)
        self.assertIn("WORKSPACE_LEAK", out)

    def test_duplicate_name_in_scope_fails(self):
        self._clean()
        write(self.f.home / "agents" / "dup-a.md", agent_md("dup"))
        write(self.f.home / "agents" / "dup-b.md", agent_md("dup"))
        self.assertEqual(self.f.lint()[0], 2)

    def test_non_agent_file_in_agents_dir_fails(self):
        self._clean()
        write(self.f.repo / "proj" / ".claude" / "agents" / "NOTES.md", "# just notes\n")
        rc, out = self.f.lint()
        self.assertEqual(rc, 2, out)
        self.assertIn("FRONTMATTER", out)

    def test_oversized_project_context_fails(self):
        self._clean()
        write(self.f.repo / "proj" / "CLAUDE.md", "x" * 17000)
        rc, out = self.f.lint()
        self.assertEqual(rc, 2, out)
        self.assertIn("CONTEXT_SIZE", out)

    def test_missing_gate_hook_fails(self):
        self._clean()
        s = json.loads((self.f.home / "settings.json").read_text(encoding="utf-8"))
        s["hooks"]["PreToolUse"] = []
        (self.f.home / "settings.json").write_text(json.dumps(s), encoding="utf-8")
        rc, out = self.f.lint()
        self.assertEqual(rc, 2, out)
        self.assertIn("GATE_MISSING", out)

    def test_subagent_model_env_must_be_sonnet(self):
        self._clean()
        s = json.loads((self.f.home / "settings.json").read_text(encoding="utf-8"))
        s["env"]["CLAUDE_CODE_SUBAGENT_MODEL"] = "opus"
        (self.f.home / "settings.json").write_text(json.dumps(s), encoding="utf-8")
        self.assertEqual(self.f.lint()[0], 2)

    def test_worktree_counted_separately_from_canonical(self):
        self._clean()
        wt = self.f.repo / "proj_wt_a"
        (wt / ".claude" / "agents").mkdir(parents=True)
        write(wt / ".claude" / "agents" / "proj-reviewer.md", agent_md("proj-reviewer"))
        write(wt / ".git", f"gitdir: {self.f.repo / 'proj' / '.git' / 'worktrees' / 'a'}\n")
        r = subprocess.run([sys.executable, str(LINT), "--home", str(self.f.home), "--repo", str(self.f.repo),
                            "--projects", str(self.f.projects), "--no-write", "--json"], capture_output=True, text=True, encoding="utf-8")
        counts = json.loads(r.stdout)["counts"]
        self.assertEqual(counts["worktree_dirs"], 1)
        self.assertEqual(counts["worktree_and_copy_agent_definitions"], 1)
        self.assertEqual(counts["canonical_agents"], 4)  # code-reviewer, legacy-thing, opus-thing, proj-reviewer


class RealConfigSmoke(unittest.TestCase):
    """Read-only checks against the real machine configuration."""

    def test_real_settings_install_gate_and_sonnet_default(self):
        s = json.loads((REAL_HOME / "settings.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(s["model"], "sonnet")
        self.assertEqual(s["env"]["CLAUDE_CODE_SUBAGENT_MODEL"], "sonnet")
        blocks = [b for b in s["hooks"]["PreToolUse"] if b.get("matcher") == "Agent"]
        self.assertTrue(any("agent_model_gate.py" in json.dumps(b) for b in blocks))

    def test_real_gate_denies_opus_and_allows_sonnet(self):
        env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PROJECT_DIR"}
        def run(model):
            p = json.dumps({"tool_name": "Agent", "tool_input": {"subagent_type": "code-reviewer", "model": model}, "cwd": "D:/Repo"})
            r = subprocess.run([sys.executable, str(GATE)], input=p.encode(), capture_output=True, env=env)
            return "deny" in r.stdout.decode()
        self.assertTrue(run("opus"))
        self.assertTrue(run("claude-opus-5-5"))
        self.assertTrue(run("haiku"))
        self.assertFalse(run("sonnet"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
