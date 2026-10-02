"""Tests for hooks/pm_bridge_stop_gate.py. Run: py -3 tools/test_pm_bridge_stop_gate.py"""
import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parent.parent / "hooks" / "pm_bridge_stop_gate.py"
sys.path.insert(0, str(HOOK.parent))
from pm_bridge_stop_gate import classify  # noqa: E402

failures = 0


def check(label, cond, detail=""):
    global failures
    if cond:
        print(f"  PASS  {label}")
    else:
        failures += 1
        print(f"  FAIL  {label} -- {detail}")


DENY = [
    r"node D:\Repo\pm-bridge\src\cli\operatorStop.js --operator",
    "cd D:/Repo/pm-bridge && node src/cli/operatorStop.js --operator",
    "echo '{\"op\":\"off\",\"args\":{},\"callerBuildId\":\"x\"}' | node src/cli/orchestratorLifecycle.js",
    "node -e \"import('./src/orchestratorClient.js').then(m=>m.stopOrchestrator())\"",
    "node - <<'EOF'\nconst { stopOrchestrator } = await import('./src/orchestratorClient.js');\nawait stopOrchestrator();\nEOF",
    "curl -X POST -H 'Authorization: Bearer t' http://127.0.0.1:8765/shutdown",
    "Invoke-RestMethod -Method Post http://127.0.0.1:8765/shutdown",
    "node -e \"fetch('http://127.0.0.1:8765/shutdown',{method:'POST'})\"",
    "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'orchestrator.js' } | Stop-Process -Force",
    "taskkill /F /PID 27616 # D:\\Repo\\pm-bridge\\.pm-bridge-generations\\x\\src\\orchestrator.js",
    "powershell -Command \"Stop-Process -Id (Get-Content state/orchestrator.json | ConvertFrom-Json).pid\"",
]
ALLOW = [
    "git add src/cli/operatorStop.js src/cli/orchestratorLifecycle.js",
    "grep -n operatorStop src/cli/*.js",
    "node --no-warnings tests/test_lifecycle_refusal_branches.mjs",
    "echo '{\"op\":\"status\",\"args\":{},\"callerBuildId\":\"x\"}' | node src/cli/orchestratorLifecycle.js",
    "curl -s -H 'Authorization: Bearer t' http://127.0.0.1:8765/status",
    "node -e \"const s=JSON.parse(require('fs').readFileSync('state/orchestrator.json','utf8'));console.log(s.pid)\"",
    "taskkill /F /IM chrome.exe",
    "npm test",
]

print("denied: every shell path that switches the orchestrator off")
for cmd in DENY:
    check(f"deny: {cmd[:90]!r}", classify(cmd) is not None, "was allowed")
print("allowed: mentions, reads, status, unrelated kills")
for cmd in ALLOW:
    check(f"allow: {cmd[:90]!r}", classify(cmd) is None, f"denied as: {classify(cmd)}")

print("hook protocol")
out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": DENY[0]}}),
                     capture_output=True, text=True)
payload = json.loads(out.stdout) if out.stdout.strip() else {}
check("a denied command emits permissionDecision deny",
      payload.get("hookSpecificOutput", {}).get("permissionDecision") == "deny", out.stdout)
out = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"tool_name": "Bash", "tool_input": {"command": ALLOW[0]}}),
                     capture_output=True, text=True)
check("an allowed command emits nothing", out.stdout.strip() == "" and out.returncode == 0, out.stdout)
out = subprocess.run([sys.executable, str(HOOK)], input="not json", capture_output=True, text=True)
check("malformed input fails open (exit 0, no decision)", out.returncode == 0 and out.stdout.strip() == "", out.stdout)

print(f"\n{'all pm_bridge_stop_gate assertions passed' if failures == 0 else f'{failures} failed'}")
sys.exit(1 if failures else 0)
