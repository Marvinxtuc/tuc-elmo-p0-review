import datetime
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
root=Path(__file__).resolve().parents[1]
run=root/Path(json.loads((root/'config/active-run.json').read_text())['path'])
records=json.loads((run/'processes.json').read_text())
for label in sys.argv[1:]:
    row=next(item for item in records if item['label']==label)
    pid=row['pid']
    check=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True)
    if check.returncode:
        print(json.dumps({'label':label,'state':'ALREADY_STOPPED'}));continue
    assert any(token in check.stdout for token in ['pnpm','src/index.ts','.output/server/index.mjs']),check.stdout
    os.killpg(pid,signal.SIGTERM)
    for attempt in range(60):
        if subprocess.run(['ps','-p',str(pid)],stdout=subprocess.DEVNULL).returncode:break
        time.sleep(.1)
    else: raise SystemExit('Shutdown incomplete')
    with (run/'stop-events.jsonl').open('a') as stream:
        stream.write(json.dumps({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':label,'state':'STOPPED'})+'\n')
    print(json.dumps({'label':label,'state':'STOPPED'}))
