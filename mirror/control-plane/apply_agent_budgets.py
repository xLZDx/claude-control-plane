from pathlib import Path
import re

ROOT=Path("D:/Repo")

POLICY={
"Personal_Decision_Command_Center":{
    "_default":("high",12),
    "pdcc-sec-reviewer":("xhigh",14),
    "pdcc-privacy-reviewer":("xhigh",14),
    "pdcc-dsr-reviewer":("xhigh",14),
    "pdcc-redteam-reviewer":("xhigh",14),
    "pdcc-consensus-adjudicator":("xhigh",14),
    "pdcc-ai-boundary-reviewer":("xhigh",14),
    "pdcc-gov-reviewer":("high",12),
    "pdcc-rel-reviewer":("high",12),
    "pdcc-ops-reviewer":("high",12),
    "pdcc-db-reviewer":("high",12),
    "pdcc-connector-reviewer":("high",12),
    "pdcc-semantic-reviewer":("high",12),
    "pdcc-test-reviewer":("high",12),
    "pdcc-ux-reviewer":("high",10),
    "arch-01":("high",12),
    "design-01":("high",12),
    "silent-bugs-01":("high",12),
    "code-01":("medium",10),
    "python-01":("medium",10),
    "ai-01":("medium",8),"data-01":("medium",8),"gov-01":("medium",8),
    "priv-01":("medium",8),"qa-01":("medium",8),"red-01":("medium",8),
    "rel-01":("medium",8),"sec-01":("medium",8),"ux-01":("medium",8),
},
"Fitness_App":{
    "_default":("medium",10),
    "clinical-safety-gate":("xhigh",16),
    "recommendation-adversary":("high",12),
    "recommendation-engine-architect":("high",14),
    "fitness-recommendation-orchestrator":("high",14),
    "biomechanics-technique-analyst":("high",12),
    "fitness-data-scientist":("high",12),
    "evidence-guideline-reviewer":("high",12),
    "chronic-condition-exercise-specialist":("high",12),
    "pregnancy-postpartum-coach":("high",12),
    "older-adult-functional-coach":("high",12),
    "youth-adolescent-coach":("high",12),
    "musculoskeletal-physiotherapist":("high",12),
    "regulatory-compliance-reviewer":("high",12),
},
"Remote_Quality_Delivery_Office_Platform_rqdo":{
    "_default":("high",12),
    "rqdo-release-decision-auditor":("xhigh",14),
    "rqdo-tenancy-auditor":("xhigh",14),
    "rqdo-privacy-compliance-auditor":("xhigh",14),
    "rqdo-ci-supply-chain-auditor":("xhigh",14),
    "rqdo-architecture-guard":("high",12),
    "rqdo-evidence-integrity-auditor":("high",12),
    "rqdo-orchestrator-lifecycle-auditor":("high",12),
    "rqdo-sre-observability-auditor":("high",12),
    "rqdo-doc-state-drift-auditor":("medium",8),
},
"TENDER":{
    "_default":("high",10),
    "scope-discipline-reviewer":("medium",8),
},
"Virtual_marketing_company":{
    "_default":("medium",8),
    "distribution-operator":("high",12),
    "devils-advocate":("high",10),
},
"db-test-tool-analysis":{
    "_default":("medium",10),
    "db-testing-tool-orchestrator":("high",12),
    "qa-adversary":("xhigh",12),
    "security-secrets-database-guard":("xhigh",12),
    "model-risk-governance-specialist":("xhigh",12),
    "quant-risk-manager":("xhigh",12),
    "sql-semantics-compiler-engineer":("high",12),
    "data-lineage-governance-auditor":("high",12),
    "principal-data-quality-architect":("high",12),
    "cross-database-dialect-specialist":("high",12),
    "etl-reconciliation-specialist":("high",12),
    "performance-scalability-reviewer":("high",12),
    "sre-observability-reproducibility-reviewer":("high",12),
    "python-fastapi-platform-architect":("high",12),
},
}

def patch(path:Path, effort:str, turns:int)->bool:
    text=path.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        return False
    end=text.find("\n---",3)
    if end<0:
        return False
    front=text[:end+1]
    rest=text[end+1:]
    def set_field(src,key,value):
        pat=rf"(?m)^{re.escape(key)}:\s*[^\r\n]*$"
        line=f"{key}: {value}"
        if re.search(pat,src):
            return re.sub(pat,line,src,count=1)
        return src.rstrip("\n")+"\n"+line+"\n"
    new=set_field(front,"model","sonnet")
    new=set_field(new,"effort",effort)
    new=set_field(new,"maxTurns",str(turns))
    out=new+rest
    if out!=text:
        path.write_text(out,encoding="utf-8")
        return True
    return False

changed=[]
for project,cfg in POLICY.items():
    ad=ROOT/project/".claude"/"agents"
    if not ad.exists():
        continue
    # A policy key that matches no agent file silently falls back to _default (this once left the RQDO tenancy
    # and privacy auditors on high instead of xhigh), so stale names are a hard error.
    stale=sorted(k for k in cfg if k!="_default" and not (ad/f"{k}.md").exists())
    if stale:
        raise SystemExit(f"{project}: policy names with no agent file: {stale}")
    default=cfg["_default"]
    for path in sorted(ad.glob("*.md")):
        if path.name=="USAGE_POLICY.md":
            continue
        effort,turns=cfg.get(path.stem,default)
        if patch(path,effort,turns):
            changed.append((project,path.stem,effort,turns))
print(f"PATCHED={len(changed)}")
for row in changed:
    print("|".join(map(str,row)))
