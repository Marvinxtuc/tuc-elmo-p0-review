#!/usr/bin/env python3
import json
from pathlib import Path
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

root = Path(__file__).resolve().parents[1]
counts = {17331: 0, 17332: 0}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        counts[self.server.server_port] += 1
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"local fixture")

    def log_message(self, *_args):
        pass


servers = [ThreadingHTTPServer(("127.0.0.1", port), Handler) for port in counts]
for server in servers:
    threading.Thread(target=server.serve_forever, daemon=True).start()

node = root / "runtime/node-v24.22.3-darwin-arm64/bin/node"
code = """
import http from 'node:http';
const outcomes = [];
for (const port of [17331, 17332]) {
  outcomes.push(await new Promise(resolve => {
    const request = http.get(`http://127.0.0.1:${port}/`, response => {
      response.resume();
      response.on('end', () => resolve({port, status: response.statusCode}));
    });
    request.on('error', error => resolve({port, error: error.code}));
    request.setTimeout(2000, () => request.destroy(new Error('timeout')));
  }));
}
console.log(JSON.stringify(outcomes));
"""
try:
    result = subprocess.run(
        ["/usr/bin/sandbox-exec", "-f", str(root / "config/runtime.sb"),
         str(node), "--input-type=module", "-e", code],
        capture_output=True, text=True, timeout=10,
    )
    outcomes = json.loads(result.stdout)
    assert result.returncode == 0, result.stderr
    assert outcomes[0]["error"] in {"EPERM", "EACCES"}, outcomes
    assert outcomes[1]["status"] == 200, outcomes
    assert counts == {17331: 0, 17332: 1}, counts
    print(json.dumps({"assertions": "PASS", "outcomes": outcomes, "fixture_requests": counts}))
finally:
    for server in servers:
        server.shutdown()
        server.server_close()
