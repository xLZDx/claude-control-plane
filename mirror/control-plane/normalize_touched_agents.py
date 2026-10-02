from pathlib import Path
import subprocess

repos=[
Path(r"D:\Repo\AI_trading_assistance"),
Path(r"D:\Repo\ERP"),
Path(r"D:\Repo\Fitness_App"),
Path(r"D:\Repo\Personal_Decision_Command_Center"),
Path(r"D:\Repo\Remote_Quality_Delivery_Office_Platform_rqdo"),
Path(r"D:\Repo\TENDER"),
Path(r"D:\Repo\Virtual_marketing_company"),
Path(r"D:\Repo\db-test-tool-analysis"),
]

def run(repo,*args):
    return subprocess.run(["git","-C",str(repo),*args],capture_output=True,check=False)

fixed=[]
for repo in repos:
    r=run(repo,"diff","--name-only","--",".claude/agents")
    names=r.stdout.decode("utf-8","replace").splitlines()
    for rel in names:
        path=repo/rel
        if not path.is_file() or path.suffix.lower()!=".md":
            continue
        cur=path.read_bytes()
        # Recover repository-preferred EOL/BOM from HEAD when tracked.
        h=run(repo,"show",f"HEAD:{rel}")
        orig=h.stdout if h.returncode==0 else b""
        bom=orig.startswith(b"\xef\xbb\xbf") if orig else cur.startswith(b"\xef\xbb\xbf")
        body=cur[3:] if cur.startswith(b"\xef\xbb\xbf") else cur
        text=body.decode("utf-8","replace").replace("\r\n","\n").replace("\r","\n")
        # Remove only trailing blank lines; keep content whitespace intact.
        text=text.rstrip("\n")+"\n"
        eol="\r\n" if b"\r\n" in orig else "\n"
        out=text.replace("\n",eol).encode("utf-8")
        if bom:
            out=b"\xef\xbb\xbf"+out
        if out!=cur:
            path.write_bytes(out)
            fixed.append(str(path))
print(f"NORMALIZED={len(fixed)}")
for x in fixed:
    print(x)
