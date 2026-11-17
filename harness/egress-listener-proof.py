import http.server
import json
from pathlib import Path
import socket
import subprocess
import threading
import urllib.request

root=Path(__file__).resolve().parents[1]
run=root/Path(json.loads((root/'config/active-run.json').read_text())['path'])
hits=[]
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        hits.append(self.server.address_family)
        self.send_response(200);self.end_headers();self.wfile.write(b'local-fixture')
    def log_message(self,*args):pass
class IPv6Server(http.server.HTTPServer):
    address_family=socket.AF_INET6
    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6,socket.IPV6_V6ONLY,1)
        super().server_bind()
servers=[http.server.HTTPServer(('127.0.0.1',17442),Handler),IPv6Server(('::1',17442),Handler)]
try:
    for server in servers: threading.Thread(target=server.serve_forever,daemon=True).start()
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
    for url in ['http://127.0.0.1:17442/','http://[::1]:17442/']:
        assert opener.open(url,timeout=3).status==200
    before=len(hits)
    result=subprocess.run(['python3',str(root/'harness/run-command.py'),'--label','egress-active-listener','--timeout','30','--cwd',str(root),'--','node','harness/egress-negative.cjs'],cwd=root,capture_output=True,text=True,timeout=40)
    assert result.returncode==0,result.stdout
    assert len(hits)==before,(before,len(hits))
    (run/'egress-active-listener.json').write_text(json.dumps({'baseline_hits':before,'sandboxed_test_hits':len(hits)-before,'ipv4_listener':True,'ipv6_listener':True,'assertion':'PASS'},indent=2)+'\n')
    print(result.stdout[-1000:]);print('ACTIVE_LISTENER_ZERO_HITS_CONFIRMED')
finally:
    for server in servers:server.shutdown();server.server_close()
