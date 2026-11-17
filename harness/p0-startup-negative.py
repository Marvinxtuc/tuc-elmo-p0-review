import json
from pathlib import Path
import subprocess

root=Path(__file__).resolve().parents[1]
run=root/Path(json.loads((root/'config/active-run.json').read_text())['path'])
results=[]
cases=[
 ('default-no-app-env',['node','-e',"const a=require('node:assert/strict');a.equal(process.env.TUC_P0_OFFLINE,'1');a.equal(process.env.SCRAPE_TARGETS,'stub:stub');a.equal(process.env.RUNS_PER_PROMPT,'1');a.ok(globalThis[Symbol.for('tuc.p0.policy-loaded')]);console.log('DEFAULT_POLICY_ENFORCED')"],0,'DEFAULT_POLICY_ENFORCED'),
 ('conflict-offline',['env','TUC_P0_OFFLINE=0','node','-e','process.exit(0)'],1,'P0_OFFLINE_REQUIRED'),
 ('conflict-provider',['env','SCRAPE_TARGETS=openai-api:chatgpt','node','-e','process.exit(0)'],1,'P0_CONFIG_SCRAPE_TARGETS'),
 ('conflict-judge',['env','TYPESAFE_API_KEY=synthetic-account-b','node','-e','process.exit(0)'],1,'P0_CONFIG_TYPESAFE_API_KEY'),
 ('conflict-fanout',['env','RUNS_PER_PROMPT=2','node','-e','process.exit(0)'],1,'P0_CONFIG_RUNS_PER_PROMPT'),
 ('direct-worker',['env','-u','NODE_OPTIONS','node','--import','tsx','apps/worker/src/index.ts'],1,'enforced offline launcher'),
 ('direct-cli',['env','-u','NODE_OPTIONS','node','--import','tsx','apps/cli/src/index.ts','lab','brainstorm'],1,'enforced offline launcher'),
 ('cli-research',['pnpm','elmo','lab','brainstorm'],1,'P0 CLI is read-only'),
]
for label,command,expected,text in cases:
    label='startup-'+label
    result=subprocess.run(['python3',str(root/'harness/run-command.py'),'--label',label,'--timeout','25','--',*command],cwd=root,capture_output=True,text=True,timeout=35)
    log=(run/'logs'/f'{label}.log').read_text()
    assert (result.returncode==0)==(expected==0),(label,result.returncode,log[-1000:])
    assert text in log,(label,log[-1000:])
    results.append({'label':label,'exit_code':result.returncode,'assertion':'PASS','evidence':f'logs/{label}.log'})
(run/'startup-negative.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
