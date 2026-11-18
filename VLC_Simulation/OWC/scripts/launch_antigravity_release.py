"""Detached Antigravity master handoff runner; does not execute tests itself."""
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'manuscript/research_draft_v2/release_audit'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    exe=Path(os.environ['LOCALAPPDATA'])/'agy/bin/agy.exe'
    if not exe.is_file():raise FileNotFoundError(exe)
    prompt=(ROOT/'antigravity_report/COMPLETE_RELEASE_AUTONOMOUSLY.md').read_text(encoding='utf-8')
    status={'status':'RUNNING','launcher_pid':os.getpid(),'started_IST':datetime.now(timezone(timedelta(hours=5,minutes=30))).isoformat(),'handoff':'antigravity_report/COMPLETE_RELEASE_AUTONOMOUSLY.md','stdout_log':'release_audit/antigravity_master_worker.log'}
    path=OUT/'ANTIGRAVITY_MASTER_WORKER.json'
    path.write_text(json.dumps(status,indent=2),encoding='utf-8')
    with (OUT/'antigravity_master_worker.log').open('w',encoding='utf-8') as log:
        proc=subprocess.Popen([str(exe),'--dangerously-skip-permissions','--output-format','text','-p',prompt],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        status['antigravity_pid']=proc.pid
        path.write_text(json.dumps(status,indent=2),encoding='utf-8')
        exitcode=proc.wait()
    status.update(status='CLI_EXITED_CHECK_FINAL_REPORT',exit_code=exitcode,ended_IST=datetime.now(timezone(timedelta(hours=5,minutes=30))).isoformat(),final_report_exists=(OUT/'ANTIGRAVITY_RELEASE_FINAL_REPORT.md').exists())
    path.write_text(json.dumps(status,indent=2),encoding='utf-8')

if __name__=='__main__':main()
