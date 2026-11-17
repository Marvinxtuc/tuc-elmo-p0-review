#!/usr/bin/env python3
import datetime
import json
import os
from pathlib import Path
import subprocess
import urllib.error
import urllib.request

root = Path(__file__).resolve().parents[1]
run = Path(json.loads((root / "config/active-run.json").read_text())["path"])
app = dict(line.split("=", 1) for line in (root / "secrets/app.env").read_text().splitlines() if line)
environment = dict(os.environ)
environment["DOCKER_HOST"] = f"unix://{root}/runtime/colima/tuc-p0/docker.sock"
environment["DOCKER_CONFIG"] = str(root / "runtime/docker-client")
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def query(sql):
    result = subprocess.run([
        "docker", "exec", "tuc-elmo-p0-postgres", "psql", "-U", "tuc_p0",
        "-d", "tuc_elmo_p0_test", "-At", "-c", sql,
    ], env=environment, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def snapshot():
    return query("""SELECT jsonb_build_object(
      'at_utc', now(),
      'runs', (SELECT count(*) FROM prompt_runs),
      'prompts', (SELECT count(*) FROM prompts),
      'opportunities', (SELECT count(*) FROM brand_opportunities),
      'schedules', (SELECT count(*) FROM pgboss.schedule),
      'queued', (SELECT coalesce(jsonb_agg(to_jsonb(j)), '[]'::jsonb) FROM
        (SELECT name, state, count(*) FROM pgboss.job
         WHERE state IN ('created','retry','active') GROUP BY name,state ORDER BY name,state) j)
    );""")


def request(path, body=None, token="valid"):
    headers = {"Accept": "application/json, text/event-stream"}
    if token:
        headers["Authorization"] = "Bearer " + (app["ADMIN_API_KEYS"] if token == "valid" else "invalid-p0-token")
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    req = urllib.request.Request("http://127.0.0.1:17300" + path, data=data, headers=headers)
    try:
        with opener.open(req, timeout=15) as response:
            return {"status": response.status, "body": json.load(response)}
    except urllib.error.HTTPError as error:
        return {"status": error.code, "body": json.loads(error.read())}


def rpc(method, params=None, token="valid"):
    return request("/api/mcp", {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}, token)


before = snapshot()
results = {}
for path in ["/api/v1/brands", "/api/v1/brands/tuc-p0-internal/opportunities"]:
    for token in [None, "invalid"]:
        result = request(path, token=token)
        assert result["status"] == 401, result
        results[f"{path} token={token}"] = result
results["opportunities"] = request("/api/v1/brands/tuc-p0-internal/opportunities")
assert results["opportunities"]["status"] == 200
pages = [request(f"/api/v1/prompts?brandId=tuc-p0-internal&limit=6&page={page}") for page in [1, 2]]
assert all(page["status"] == 200 for page in pages), pages
ids = [item["id"] for page in pages for item in page["body"]["data"]]
assert len(ids) == len(set(ids)) == 10, pages
results["prompt_pages"] = pages
results["mcp_initialize"] = rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "p0-local-audit", "version": "1"}})
assert results["mcp_initialize"]["status"] == 200
results["mcp_tools"] = rpc("tools/list")
tools = results["mcp_tools"]["body"]["result"]["tools"]
assert tools and all(tool["annotations"]["readOnlyHint"] for tool in tools)
for name, args in [("list_brands", {}), ("get_opportunities", {"brandId": "tuc-p0-internal"})]:
    result = rpc("tools/call", {"name": name, "arguments": args})
    assert result["status"] == 200 and not result["body"].get("error"), result
    assert not result["body"]["result"].get("isError"), result
    results[name] = result
for name, args in [
    ("create_prompts", {"brandId": "tuc-p0-internal", "prompts": [{"value": "Forbidden audit write"}]}),
    ("update_prompt", {"promptId": ids[0], "enabled": False}),
    ("delete_brand", {"brandId": "tuc-p0-internal"}),
    ("run_prompt", {"promptId": ids[0]}),
]:
    result = rpc("tools/call", {"name": name, "arguments": args})
    body = result["body"]
    assert "error" in body or body.get("result", {}).get("isError"), result
    results[name] = result
for token in [None, "invalid"]:
    result = rpc("tools/list", token=token)
    assert result["status"] == 401, result
    results[f"mcp_auth_{token}"] = result
after = snapshot()
for key in ["runs", "prompts", "opportunities", "schedules", "queued"]:
    assert before[key] == after[key], (key, before, after)
assert after["runs"] == 10 and after["schedules"] == 0 and not after["queued"], after
output = {"at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "before": before, "after": after, "results": results, "status": "PASS", "scope": "Local admin reads and disabled MCP write tools. Expired session and lower-role object access remain NOT_RUN."}
(run / "read-api-mcp-audit.json").write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps({"status": "PASS", "tools": [tool["name"] for tool in tools], "after": after}))
