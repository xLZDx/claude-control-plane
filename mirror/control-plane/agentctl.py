#!/usr/bin/env python3
"""Control Plane v3: registry generator + mechanical lint for agents, skills, routing and context size.

    C:\\Python314\\python.exe agentctl.py --strict

Exit codes: 0 = clean, 2 = at least one policy error (with --strict), 3 = internal failure (fail closed).
Fixtures for negative tests: --home <fake .claude> --repo <fake workspace> --no-write.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ALLOWED_EFFORT = {"low", "medium", "high", "xhigh"}
SONNET_ID = re.compile(r"^claude-sonnet-(\d+)-(\d+)(?:-\d{8})?$")
BUILTINS = {"Explore", "Plan", "general-purpose", "claude", "claude-code-guide", "statusline-setup",
            "<language-reviewer-slot>"}
DEFAULT_LIMITS = {"global_instruction_tokens": 6000, "project_instruction_tokens": 4000, "max_turns": 25,
                  "skill_thin_front_door_tokens": 800, "skill_stub_tokens": 150}


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def model_ok(model: str | None) -> bool:
    """Automatic agents: the `sonnet` alias or an explicit Sonnet id >= 5.5. Everything else is denied."""
    if not model:
        return False
    m = model.strip().lower()
    if m == "sonnet":
        return True
    hit = SONNET_ID.match(m)
    return bool(hit) and (int(hit.group(1)), int(hit.group(2))) >= (5, 5)


def parse_frontmatter(text: str):
    t = text.lstrip("\ufeff")
    m = re.match(r"---\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|$)", t, re.S)
    if not m:
        return None, t
    fm: dict = {}
    cur = None
    block = None
    for line in m.group(1).splitlines():
        if block is not None:
            if line.startswith((" ", "\t")) or not line.strip():
                fm[block] = (fm[block] + " " + line.strip()).strip()
                continue
            block = None
        item = re.match(r"^\s*-\s+(.*)$", line)
        if item and cur is not None and isinstance(fm.get(cur), list):
            fm[cur].append(item.group(1).strip().strip("'\""))
            continue
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not kv:
            continue
        cur, val = kv.group(1), kv.group(2).strip()
        if val in ("", None):
            fm[cur] = []
        elif val in (">", "|", ">-", "|-"):
            fm[cur] = ""
            block = cur
        elif val.startswith("[") and val.endswith("]"):
            fm[cur] = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
        else:
            fm[cur] = val.strip("'\"")
    return fm, t[m.end():]


def scalar(fm: dict, key: str):
    v = fm.get(key)
    if isinstance(v, str):
        return re.sub(r"\s+#.*$", "", v).strip().strip("'\"") or None
    return None


def as_list(v) -> list[str]:
    if isinstance(v, list):
        return [str(x) for x in v]
    if isinstance(v, str) and v:
        return [x.strip() for x in v.split(",") if x.strip()]
    return []


class Lint:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, severity: str, code: str, scope: str, name: str, path: str, message: str) -> None:
        self.items.append({"severity": severity, "code": code, "scope": scope, "name": name,
                           "path": path, "message": message})

    def errors(self) -> list[dict]:
        return [i for i in self.items if i["severity"] == "error"]


def classify_dir(p: Path, cfg: dict, repo: Path):
    name = p.name
    canon = cfg.get("canonical", {})
    if name in canon:
        return ("historical" if canon[name].get("historical_nonrunnable") else "canonical"), name
    if name in cfg.get("temporary_copies", []):
        return "temporary_copy", None
    git = p / ".git"
    if git.is_file():
        owner = None
        try:
            m = re.search(r"gitdir:\s*(.+)", read(git))
            if m:
                gd = Path(m.group(1).strip())
                root = gd.parent.parent.parent  # <repo>/.git/worktrees/<name>
                if root.parent.resolve() == repo.resolve() or root.parent == repo:
                    owner = root.name
        except OSError:
            pass
        return "worktree", owner
    return "other_copy", None


def load_agents(adir: Path, scope: str, klass: str):
    out = []
    if not adir.exists():
        return out
    for f in sorted(adir.glob("*.md")):
        text = read(f)
        fm, body = parse_frontmatter(text)
        fmd = fm or {}
        out.append({
            "scope": scope, "scope_class": klass, "name": scalar(fmd, "name") or f.stem, "file": f.stem,
            "path": str(f), "frontmatter_ok": fm is not None,
            "description": (fmd.get("description") if isinstance(fmd.get("description"), str) else "") or "",
            "model": scalar(fmd, "model"), "effort": scalar(fmd, "effort"), "maxTurns": scalar(fmd, "maxTurns"),
            "turnException": (scalar(fmd, "turnException") or "").lower() == "true",
            "tools": as_list(fmd.get("tools")), "skills": as_list(fmd.get("skills")),
            "deprecated": (scalar(fmd, "deprecated") or "").lower() == "true",
            "superseded_by": scalar(fmd, "superseded_by"), "tokens_est": tokens(text), "sha": sha(f),
            "_body": body,
        })
    return out


def load_skills(sdir: Path, scope: str, klass: str):
    out = []
    if not sdir.exists():
        return out
    for f in sorted(sdir.glob("*/SKILL.md")):
        text = read(f)
        fm, _ = parse_frontmatter(text)
        fmd = fm or {}
        refs = [x for x in (f.parent / "references").glob("*")] if (f.parent / "references").exists() else []
        out.append({"scope": scope, "scope_class": klass, "name": scalar(fmd, "name") or f.parent.name,
                    "dir": f.parent.name, "path": str(f), "frontmatter_ok": fm is not None,
                    "description": scalar(fmd, "description") or "", "tokens_est": tokens(text),
                    "references": len(refs), "references_tokens": sum(tokens(read(r)) for r in refs if r.is_file()),
                    "sha": sha(f)})
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--home", default=str(Path.home() / ".claude"))
    ap.add_argument("--repo", default=None)
    ap.add_argument("--projects", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    home = Path(a.home)
    cfg_path = Path(a.projects) if a.projects else home / "control-plane" / "projects.json"
    cfg = json.loads(read(cfg_path)) if cfg_path.exists() else {"canonical": {}, "temporary_copies": []}
    limits = {**DEFAULT_LIMITS, **cfg.get("limits", {})}
    repo = Path(a.repo or cfg.get("repo_root", "D:/Repo"))
    out = Path(a.out) if a.out else home / "control-plane"
    lint = Lint()

    settings_path = home / "settings.json"
    routing_path = home / "agent_routing.json"
    settings = json.loads(read(settings_path))
    routing = json.loads(read(routing_path))

    # ---- discovery -------------------------------------------------------------------------
    agents: list[dict] = []
    skills: list[dict] = []
    contexts: list[dict] = []
    worktrees: list[dict] = []

    agents += load_agents(home / "agents", "global", "global")
    skills += load_skills(home / "skills", "global", "global")
    g_ctx = sum(tokens(read(x)) for x in (home / "CLAUDE.md", home / "AGENTS.md") if x.exists())
    contexts.append({"scope": "global", "scope_class": "global", "tokens_est": g_ctx,
                     "limit": limits["global_instruction_tokens"]})
    if (repo / ".claude").exists():
        agents += load_agents(repo / ".claude" / "agents", "workspace", "workspace")
        skills += load_skills(repo / ".claude" / "skills", "workspace", "workspace")
    w_ctx = sum(tokens(read(x)) for x in (repo / "CLAUDE.md", repo / "AGENTS.md") if x.exists())
    contexts.append({"scope": "workspace", "scope_class": "workspace", "tokens_est": w_ctx,
                     "limit": limits["project_instruction_tokens"]})

    dir_classes: dict[str, tuple[str, str | None]] = {}
    if repo.exists():
        for p in sorted((x for x in repo.iterdir() if x.is_dir()), key=lambda x: x.name.lower()):
            klass, owner = classify_dir(p, cfg, repo)
            has_claude = (p / ".claude").exists()
            if klass in ("canonical", "historical"):
                agents += load_agents(p / ".claude" / "agents", p.name, klass)
                skills += load_skills(p / ".claude" / "skills", p.name, klass)
                tot = sum(tokens(read(x)) for x in (p / "CLAUDE.md", p / "AGENTS.md") if x.exists())
                contexts.append({"scope": p.name, "scope_class": klass, "tokens_est": tot,
                                 "limit": limits["project_instruction_tokens"]})
                dir_classes[p.name] = (klass, owner)
            elif has_claude:
                wa = load_agents(p / ".claude" / "agents", p.name, klass)
                ws = load_skills(p / ".claude" / "skills", p.name, klass)
                worktrees.append({"scope": p.name, "scope_class": klass, "owner": owner, "agents": len(wa),
                                  "skills": len(ws), "_sha": {x["file"]: x["sha"] for x in wa}})
                dir_classes[p.name] = (klass, owner)

    canon_by_scope: dict[str, dict[str, str]] = {}
    for x in agents:
        canon_by_scope.setdefault(x["scope"], {})[x["file"]] = x["sha"]
    for w in worktrees:
        base = canon_by_scope.get(w["owner"] or "", {})
        mine = w.pop("_sha")
        w["drift_files"] = sorted({k for k in set(base) | set(mine) if base.get(k) != mine.get(k)}) if base else None

    runnable_scopes = {"global", "workspace", "canonical"}
    for x in agents:
        x["runnable"] = x["scope_class"] in runnable_scopes and not x["deprecated"]

    # ---- policy checks: agents -------------------------------------------------------------
    max_turns_cap = int(limits["max_turns"])
    historical_models = []
    for x in agents:
        where = (x["scope"], x["name"], x["path"])
        if x["scope_class"] == "historical":
            if x["model"] and not model_ok(x["model"]):
                historical_models.append({k: x[k] for k in ("scope", "name", "path", "model")})
            continue
        if x["scope_class"] not in runnable_scopes:
            continue
        if not x["frontmatter_ok"]:
            lint.add("error", "FRONTMATTER", *where, "file in agents/ has no parseable frontmatter; it is not a runnable agent definition")
            continue
        if x["file"] != x["name"]:
            lint.add("warn", "NAME_STEM", *where, f"name '{x['name']}' differs from file stem '{x['file']}'")
        if not x["description"].strip():
            lint.add("error", "NO_TRIGGER", *where, "missing description (the routing trigger)")
        if x["deprecated"]:
            if not x["superseded_by"]:
                lint.add("warn", "DEPRECATED_NO_SUCCESSOR", *where, "deprecated agent without superseded_by")
            continue
        if x["model"] is None:
            lint.add("warn", "MODEL_INHERITED", *where, "model not declared; relies on CLAUDE_CODE_SUBAGENT_MODEL")
        elif not model_ok(x["model"]):
            lint.add("error", "MODEL", *where, f"model '{x['model']}' is not allowed for automatic agents (sonnet alias / Sonnet >= 5.5 only; Opus needs per-run operator consent and never runs automatically)")
        if x["model"] and x["model"].lower().startswith("opus") and x["effort"] != "high":
            lint.add("error", "OPUS_EFFORT", *where, "Opus is allowed only at effort=high")
        if x["effort"] is None:
            lint.add("warn", "EFFORT_INHERITED", *where, "effort not declared; falls back to the default (medium)")
        elif x["effort"] not in ALLOWED_EFFORT:
            lint.add("error", "EFFORT", *where, f"effort '{x['effort']}' not in {sorted(ALLOWED_EFFORT)}")
        if x["maxTurns"] is None:
            lint.add("warn", "TURNS_INHERITED", *where, "maxTurns not declared")
        elif not x["maxTurns"].isdigit():
            lint.add("error", "TURNS", *where, f"maxTurns '{x['maxTurns']}' is not an integer")
        elif int(x["maxTurns"]) > max_turns_cap and not x["turnException"]:
            lint.add("error", "TURNS_CAP", *where, f"maxTurns {x['maxTurns']} > {max_turns_cap}; add 'turnException: true' with a written reason to keep it")
        if not x["tools"]:
            lint.add("warn", "TOOLS_UNSPECIFIED", *where, "tools not declared (inherits every tool)")
        if x["tokens_est"] > 1200 and x["scope_class"] != "historical":
            lint.add("info", "PROMPT_SIZE", *where, f"~{x['tokens_est']} tokens; candidate for skill/reference extraction")

    # duplicates inside one scope, shadowing across scopes
    seen: dict[tuple[str, str], str] = {}
    for x in agents:
        if not x["frontmatter_ok"]:
            continue
        key = (x["scope"], x["name"].lower())
        if key in seen:
            lint.add("error", "DUPLICATE", x["scope"], x["name"], x["path"], f"duplicate agent name in scope (also {seen[key]})")
        seen[key] = x["path"]
    global_names = {x["name"] for x in agents if x["scope"] == "global" and x["frontmatter_ok"]}
    shadowed = sorted({(x["scope"], x["name"]) for x in agents if x["scope"] not in ("global",) and x["scope_class"] in ("canonical", "workspace") and x["name"] in global_names})

    # workspace scope must not carry project agents
    for x in agents:
        if x["scope"] != "workspace":
            continue
        prefixes = [c.get("workspace_prefix") for c in cfg.get("canonical", {}).values() if c.get("workspace_prefix")]
        pinned = "workspace-scoped copy" in x["_body"]
        if pinned or any(x["name"].startswith(p) for p in prefixes):
            lint.add("error", "WORKSPACE_LEAK", "workspace", x["name"], x["path"], "project-specific agent loaded from workspace scope; it must live in its own project's .claude/agents")

    # ---- policy checks: settings / gate ------------------------------------------------------
    sub_model = settings.get("env", {}).get("CLAUDE_CODE_SUBAGENT_MODEL")
    global_model_ok = model_ok(settings.get("model")) and model_ok(sub_model)
    if not model_ok(settings.get("model")):
        lint.add("error", "SETTINGS_MODEL", "global", "settings.model", str(settings_path), f"default model '{settings.get('model')}' is not allowed")
    if not model_ok(sub_model):
        lint.add("error", "SETTINGS_SUBAGENT_MODEL", "global", "env.CLAUDE_CODE_SUBAGENT_MODEL", str(settings_path), f"subagent model '{sub_model}' is not allowed")
    if settings.get("effortLevel") not in ALLOWED_EFFORT:
        lint.add("error", "SETTINGS_EFFORT", "global", "effortLevel", str(settings_path), f"default effort '{settings.get('effortLevel')}' invalid")
    for mk, mv in (settings.get("modelSettings") or {}).items():
        if "opus" in mk and (mv or {}).get("effortLevel") not in (None, "high"):
            lint.add("error", "SETTINGS_OPUS_EFFORT", "global", mk, str(settings_path), "Opus effort must be high")
    gate_ok = False
    for block in (settings.get("hooks", {}).get("PreToolUse") or []):
        if block.get("matcher") == "Agent" and any("agent_model_gate.py" in json.dumps(h) for h in block.get("hooks", [])):
            gate_ok = True
    gate_file = home / "hooks" / "agent_model_gate.py"
    if gate_ok and gate_file.exists():
        try:
            compile(read(gate_file), str(gate_file), "exec")
        except SyntaxError as e:
            gate_ok = False
            lint.add("error", "GATE_SYNTAX", "global", "agent_model_gate.py", str(gate_file), str(e))
    else:
        gate_ok = False
    if not gate_ok:
        lint.add("error", "GATE_MISSING", "global", "agent_model_gate.py", str(gate_file), "Agent model gate not installed on the PreToolUse Agent matcher")

    # ---- routing -----------------------------------------------------------------------------
    disabled = set((routing.get("_control_plane_v2") or {}).get("disabled_unresolved_agents", []))
    resolvable = {x["name"] for x in agents if x["scope"] == "global" and x["frontmatter_ok"] and not x["deprecated"]}
    deprecated_global = {x["name"] for x in agents if x["scope"] == "global" and x["deprecated"]}
    refs: dict[str, str] = {}
    for gname, group in (routing.get("groups") or {}).items():
        for n in group.get("agents", []):
            if isinstance(n, str):
                refs.setdefault(n, f"groups.{gname}")
    for n in (routing.get("triggers") or {}):
        refs.setdefault(n, "triggers")
    for ext, n in ((routing.get("language_reviewer_slot") or {}).get("by_extension") or {}).items():
        refs.setdefault(n, f"language_reviewer_slot.by_extension[{ext}]")
    for tier, spec in ((routing.get("risk_routing") or {}).get("tiers") or {}).items():
        for n in spec.get("agents", []):
            refs.setdefault(n, f"risk_routing.tiers.{tier}")
    unresolved = sorted(n for n in refs if n not in BUILTINS and n not in resolvable and n not in disabled)
    for n in unresolved:
        lint.add("error", "ROUTE_UNRESOLVED", "global", n, str(routing_path), f"routing references '{n}' ({refs[n]}) which is not a runnable global agent and not in disabled_unresolved_agents")
    for n in sorted(set(refs) & deprecated_global):
        lint.add("error", "ROUTE_DEPRECATED", "global", n, str(routing_path), f"routing references deprecated agent '{n}'")
    legacy_disabled = sorted(n for n in refs if n in disabled)
    orphans = sorted(n for n in resolvable if n not in refs)
    for n in orphans:
        lint.add("warn", "ORPHAN_AGENT", "global", n, str(home / "agents" / f"{n}.md"), "global agent not referenced by any routing group/trigger/risk tier")
    rr = routing.get("risk_routing") or {}
    tier_of = rr.get("agent_effort_tier") or {}
    tier_effort = {k: v.get("effort") for k, v in (rr.get("effort_tiers") or {}).items()}
    global_by_name = {x["name"]: x for x in agents if x["scope"] == "global" and x["frontmatter_ok"]}
    for n, t in tier_of.items():
        a_ = global_by_name.get(n)
        if a_ is None:
            lint.add("error", "TIER_UNRESOLVED", "global", n, str(routing_path), f"agent_effort_tier names '{n}' which is not a global agent")
        elif tier_effort.get(t) != a_["effort"]:
            lint.add("warn", "TIER_MISMATCH", "global", n, a_["path"], f"declares effort '{a_['effort']}' but routing tier {t} means '{tier_effort.get(t)}'")
    if rr:
        for n in sorted(resolvable - set(tier_of)):
            lint.add("warn", "NO_TIER", "global", n, str(routing_path), "runnable global agent has no effort tier in risk_routing.agent_effort_tier")
    for prof, pv in (routing.get("stack_profiles") or {}).items():
        if not prof.startswith("_") and not Path(prof).exists() and not (isinstance(pv, dict) and pv.get("historical")):
            lint.add("warn", "STALE_STACK_PROFILE", "global", prof, str(routing_path), "stack profile path does not exist and is not marked historical")

    # ---- skills --------------------------------------------------------------------------------
    skill_names = {s["name"] for s in skills if s["scope_class"] in ("global", "workspace", "canonical")}
    for x in agents:
        used = set(x["skills"])
        for s in skill_names:
            if "-" in s and re.search(rf"skills[/\\]{re.escape(s)}\b|`{re.escape(s)}`", x["_body"]):
                used.add(s)
        x["skills_used"] = sorted(used)
    for x in agents:
        if x["scope_class"] not in ("global", "workspace", "canonical") or not x["frontmatter_ok"] or x["deprecated"]:
            continue
        for sname in x["skills"]:
            ok = any(s["name"] == sname and s["scope"] in (x["scope"], "global", "workspace") for s in skills)
            if not ok:
                lint.add("error", "SKILL_UNRESOLVED", x["scope"], x["name"], x["path"], f"agent loads skill '{sname}' which does not exist in its project or global scope")
    for s in skills:
        s["agents_using_it"] =sorted({x["name"] for x in agents if s["name"] in x["skills_used"] and x["scope"] in (s["scope"], "global", "workspace")})
        if s["scope_class"] not in ("global", "workspace", "canonical"):
            continue
        where = (s["scope"], s["name"], s["path"])
        if not s["frontmatter_ok"] or not s["description"]:
            lint.add("error", "SKILL_NO_DESCRIPTION", *where, "SKILL.md without frontmatter description")
        if s["tokens_est"] > limits["skill_thin_front_door_tokens"] and s["references"] == 0:
            lint.add("warn", "SKILL_FAT_FRONT_DOOR", *where, f"~{s['tokens_est']} tokens and no references/")
        if s["tokens_est"] < limits["skill_stub_tokens"] and s["scope"] == "global":
            lint.add("warn", "SKILL_STUB", *where, f"~{s['tokens_est']} tokens: too thin to carry a method")
        # *-reference skills are model-invoked by description; only *-contract skills are expected to be preloaded.
        if s["name"].endswith("-contract") and not s["agents_using_it"]:
            lint.add("warn", "SKILL_NO_CONSUMER", *where, "contract skill with no agent that loads it")

    # ---- instruction context ---------------------------------------------------------------------
    for c in contexts:
        c["over_target"] = c["scope_class"] != "historical" and c["tokens_est"] > c["limit"]
        if c["over_target"]:
            lint.add("error", "CONTEXT_SIZE", c["scope"], "CLAUDE.md+AGENTS.md", "", f"~{c['tokens_est']} tokens > {c['limit']}")

    # ---- registries ----------------------------------------------------------------------------
    def pub(x):
        return {k: v for k, v in x.items() if not k.startswith("_")}

    canon_agents = [pub(x) for x in agents if x["scope_class"] in ("global", "workspace", "canonical")]
    hist_agents = [pub(x) for x in agents if x["scope_class"] == "historical"]
    canon_skills = [s for s in skills if s["scope_class"] in ("global", "workspace", "canonical")]
    hist_skills = [s for s in skills if s["scope_class"] == "historical"]
    wt_agents = sum(w["agents"] for w in worktrees)
    wt_skills = sum(w["skills"] for w in worktrees)
    counts = {
        "canonical_agents": len(canon_agents),
        "canonical_runnable_agents": sum(1 for x in agents if x["runnable"]),
        "deprecated_agents": sum(1 for x in agents if x["deprecated"]),
        "historical_agents": len(hist_agents),
        "worktree_and_copy_agent_definitions": wt_agents,
        "all_discovered_agent_definitions": len(canon_agents) + len(hist_agents) + wt_agents,
        "canonical_skills": len(canon_skills),
        "historical_skills": len(hist_skills),
        "worktree_and_copy_skill_definitions": wt_skills,
        "all_discovered_skill_definitions": len(canon_skills) + len(hist_skills) + wt_skills,
        "worktree_dirs": sum(1 for w in worktrees if w["scope_class"] == "worktree"),
        "temporary_copy_dirs": sum(1 for w in worktrees if w["scope_class"] == "temporary_copy"),
        "other_copy_dirs": sum(1 for w in worktrees if w["scope_class"] == "other_copy"),
        "model_violations": sum(1 for i in lint.items if i["code"] == "MODEL"),
        "historical_nonrunnable_nonsonnet": len(historical_models),
        "unresolved_routes": len(unresolved),
        "disabled_legacy_routes": len(legacy_disabled),
        "errors": len(lint.errors()),
        "warnings": sum(1 for i in lint.items if i["severity"] == "warn"),
    }
    report = {
        "policy": {"global_model_ok": global_model_ok, "agent_model_gate_installed": gate_ok,
                   "default_effort": settings.get("effortLevel")},
        "counts": counts, "findings": lint.items, "historical_nonrunnable_model_declarations": historical_models,
        "unresolved_routing_agents": unresolved, "disabled_legacy_routing_agents": legacy_disabled,
        "orphan_global_agents": orphans, "project_agents_shadowing_global": [list(s) for s in shadowed],
        "instruction_context": contexts,
    }

    if not a.no_write:
        out.mkdir(parents=True, exist_ok=True)
        dump = lambda name, obj: (out / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        dump("agent_registry.json", {"counts": counts, "agents": canon_agents + hist_agents})
        dump("skill_registry.json", {"counts": counts, "skills": canon_skills + hist_skills})
        dump("worktree_summary.json", {"worktrees": worktrees})
        dump("GLOBAL_AGENTS.json", [x for x in canon_agents if x["scope"] == "global"])
        dump("GLOBAL_SKILLS.json", [s for s in canon_skills if s["scope"] == "global"])
        comp: dict = {}
        for x in canon_agents + hist_agents:
            if x["scope"] in ("global",):
                continue
            comp.setdefault(x["scope"], {"scope_class": x["scope_class"], "agents": [], "skills": []})["agents"].append(x["name"])
        for s in canon_skills + hist_skills:
            if s["scope"] == "global":
                continue
            comp.setdefault(s["scope"], {"scope_class": s["scope_class"], "agents": [], "skills": []})["skills"].append(s["name"])
        for c in contexts:
            comp.setdefault(c["scope"], {"scope_class": c["scope_class"], "agents": [], "skills": []})["instruction_tokens"] = c["tokens_est"]
        dump("PROJECT_AI_COMPONENTS.json", comp)
        dump("lint_report.json", report)
        lines = ["# Control Plane v3 lint report", "",
                 f"- canonical agents: {counts['canonical_agents']} (runnable {counts['canonical_runnable_agents']}, deprecated {counts['deprecated_agents']}, historical {counts['historical_agents']})",
                 f"- worktree/copy agent definitions: {counts['worktree_and_copy_agent_definitions']} in {counts['worktree_dirs']} worktrees + {counts['temporary_copy_dirs']} temporary + {counts['other_copy_dirs']} other copies",
                 f"- all discovered agent definitions: {counts['all_discovered_agent_definitions']}",
                 f"- canonical skills: {counts['canonical_skills']}; worktree/copy skill definitions: {counts['worktree_and_copy_skill_definitions']}",
                 f"- model violations: {counts['model_violations']}; historical non-runnable non-Sonnet: {counts['historical_nonrunnable_nonsonnet']}",
                 f"- unresolved routes: {counts['unresolved_routes']}; disabled legacy routes: {counts['disabled_legacy_routes']}",
                 f"- settings model policy: {'PASS' if global_model_ok else 'FAIL'}; Agent model gate: {'PASS' if gate_ok else 'FAIL'}",
                 f"- errors: {counts['errors']}; warnings: {counts['warnings']}", ""]
        for sev in ("error", "warn"):
            rows = [i for i in lint.items if i["severity"] == sev]
            if rows:
                lines.append(f"## {sev.upper()} ({len(rows)})")
                lines += [f"- {i['code']} | {i['scope']} | {i['name']} | {i['message']}" for i in rows[:200]]
                lines.append("")
        lines.append("## Instruction context")
        lines += [f"- {c['scope']} ({c['scope_class']}): ~{c['tokens_est']} / {c['limit']}{'  OVER' if c['over_target'] else ''}" for c in contexts]
        (out / "LINT_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    if a.json:
        print(json.dumps(report, ensure_ascii=False))
    else:
        print(json.dumps(counts, ensure_ascii=False))
        print("MODEL_POLICY=" + ("PASS" if global_model_ok and gate_ok and counts["model_violations"] == 0 else "FAIL"))
        for i in lint.errors()[:40]:
            print(f"ERROR {i['code']} [{i['scope']}] {i['name']}: {i['message']}")
    return 2 if (a.strict and lint.errors()) else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # fail closed on internal error
        print(f"agentctl internal failure: {exc!r}", file=sys.stderr)
        sys.exit(3)
