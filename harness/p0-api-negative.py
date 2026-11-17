import datetime
import json
from pathlib import Path
import urllib.request
import urllib.error

root=Path(__file__).resolve().parents[1]
run=root/Path(json.loads((root/'config/active-run.json').read_text())['path'])
records=[]
for route in ['/api/v1/brands','/api/v1/prompts','/api/v1/reports','/api/auth/sign-in/email', '/_server/onboarding', '/api/v1/opportunities']:
    request=urllib.request.Request('http://127.0.0.1:17300'+route, data=b'{}', headers={'Content-Type':'application/json'},method='POST')
    try: response=urllib.request.urlopen(request,timeout=10)
    except urllib.error.HTTPError as error: response=error
    body=response.read().decode()
    assert response.status==403,(route,response.status,body)
    assert json.loads(body)['code']=='P0_READ_ONLY'
    records.append({'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'route':route,'status':response.status,'body':json.loads(body)})
(run/'api-negative.json').write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps(records,indent=2))
