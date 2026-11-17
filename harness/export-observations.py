#!/usr/bin/env python3
import datetime
import hashlib
import json
from pathlib import Path
import urllib.error
import urllib.request
import urllib.parse

root = Path(__file__).resolve().parents[1]
run = Path(json.loads((root / "config/active-run.json").read_text())["path"])
environment = dict(
    line.split("=", 1) for line in (root / "secrets/app.env").read_text().splitlines() if line
)
headers = {"Authorization": "Bearer " + environment["ADMIN_API_KEYS"]}


def read(path, authenticated=True):
    request = urllib.request.Request(
        "http://127.0.0.1:17300" + path,
        headers=headers if authenticated else {},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


prompts = read("/api/v1/prompts?brandId=tuc-p0-internal&limit=100")
(run / "prompts-api.json").write_text(json.dumps(prompts, indent=2) + "\n")
observations = []
started = datetime.datetime.fromisoformat(json.loads((run / "run-manifest.json").read_text())["started_at_utc"])
window = urllib.parse.urlencode({
    "start": started.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
    "end": (started + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
    "limit": 100,
})
for prompt in prompts["data"]:
    runs = read(f"/api/v1/prompts/{prompt['id']}/runs?{window}")
    assert len(runs["data"]) == 1, runs
    for item in runs["data"]:
        detail = read(f"/api/v1/prompts/{prompt['id']}/runs/{item['id']}")
        assert detail["provider"] == "stub", detail
        (run / "raw" / f"api-{item['id']}.json").write_text(json.dumps(detail, indent=2) + "\n")
        observations.append({
            "schema_version": "p0-api-export-1",
            "observation_id": item["id"],
            "prompt_id": prompt["id"],
            "prompt": prompt["value"],
            "prompt_group": "brand_control" if "brand_control" in prompt["tags"] else "non_brand",
            "observation_mode": "UPSTREAM_STUB",
            "judge_mode": "UPSTREAM_STUB",
            "judge_version": "stub+request-1",
            "provider": detail["provider"],
            "model": detail["model"],
            "sampled_at": detail["createdAt"],
            "answer": detail["answer"]["text"],
            "assessments": detail["assessments"],
            "brand_mentioned": detail["brandMentioned"],
            "citations": detail["citations"],
            "raw_api_ref": f"raw/api-{item['id']}.json",
            "usage": None,
            "cost_status": "NOT_APPLICABLE_STUB",
            "upstream_commit": "15c2d5f1b56682ce98e6c6ed76e254eec124e15e",
        })

assert len(observations) == 10, len(observations)
assert all(item["answer"] for item in observations)
path = run / "observations.jsonl"
path.write_text("".join(json.dumps(item) + "\n" for item in observations))

try:
    read("/api/v1/brands", authenticated=False)
    raise AssertionError("Unauthenticated API request was accepted")
except urllib.error.HTTPError as error:
    assert error.code == 401, error.code

opportunities = read("/api/v1/brands/tuc-p0-internal/opportunities")
(run / "opportunities-read.json").write_text(json.dumps(opportunities, indent=2) + "\n")
summary = {
    "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "observation_count": len(observations),
    "non_brand": sum(item["prompt_group"] == "non_brand" for item in observations),
    "brand_control": sum(item["prompt_group"] == "brand_control" for item in observations),
    "observation_mode": "UPSTREAM_STUB",
    "judge_mode": "UPSTREAM_STUB",
    "unauthenticated_api_status": 401,
    "observations_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "limitations": ["API output is normalized. Full upstream payloads are exported separately from the new test database.",
                    "Judge mode is stub. Semantic quality and live-provider behavior remain NOT_RUN."],
}
(run / "api-export-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
