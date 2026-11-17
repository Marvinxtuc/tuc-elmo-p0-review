import datetime
import json
from pathlib import Path
import urllib.request
import urllib.error

root=Path(__file__).resolve().parents[1]
run=root/Path(json.loads((root/'config/active-run.json').read_text())['path'])
values=dict(line.split('=',1) for line in (root/'secrets/app.env').read_text().splitlines() if line and not line.startswith('#'))
key=values['ADMIN_API_KEYS'].split(',')[0].strip()
headers={'Content-Type':'application/json','Accept':'application/json, text/event-stream','Authorization':'Bearer '+key,'mcp-protocol-version':'2025-03-26'}
results=[]
for index,(method,params) in enumerate([
 ('initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'synthetic-b1-client','version':'1'}}),
 ('tools/list',{}),
 ('tools/call',{'name':'create_prompts','arguments':{'brand_id':'tuc-p0-internal','prompts':['unapproved']}}),
 ('tools/call',{'name':'update_prompt','arguments':{'id':'unapproved','name':'unapproved'}}),
 ('tools/call',{'name':'get_opportunities','arguments':{'brand_id':'tuc-p0-internal'}}),
]):
 request=urllib.request.Request('http://127.0.0.1:17300/api/mcp',data=json.dumps({'jsonrpc':'2.0','id':index+1,'method':method,'params':params}).encode(),headers=headers)
 try: response=urllib.request.urlopen(request,timeout=10)
 except urllib.error.HTTPError as error: response=error
 body=json.loads(response.read())
 assert response.status==200,(method,response.status,body)
 if method=='tools/list':
  names=[tool['name'] for tool in body['result']['tools']]
  assert 'create_prompts' not in names and 'update_prompt' not in names
 if method=='tools/call' and params['name'] in ['create_prompts','update_prompt']:
  assert 'error' in body or body.get('result',{}).get('isError') is True,body
 results.append({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':method,'params':params,'status':response.status,'response':body})
(run/'mcp-negative.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'cases':len(results),'write_tools_hidden':True,'write_calls_rejected':True}))
