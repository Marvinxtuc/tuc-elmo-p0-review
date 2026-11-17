#!/usr/bin/env python3
import hashlib
import html
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
run = Path(json.loads((root / "config/active-run.json").read_text())["path"])
observations = [json.loads(line) for line in (run / "observations.jsonl").read_text().splitlines()]
assert len(observations) == 10
assert all(item["observation_mode"] == item["judge_mode"] == "UPSTREAM_STUB" for item in observations)
assert all(item["answer"].strip() == item["prompt"].strip() for item in observations)

groups = {}
for group in ["non_brand", "brand_control"]:
    selected = [item for item in observations if item["prompt_group"] == group]
    groups[group] = {"answers": len(selected), "stub_mentions": sum(item["brand_mentioned"] for item in selected)}
metrics = {
    "mode": "UPSTREAM_STUB", "planned": 10, "stored": 10,
    "stub_processed": sum(item["assessments"] is not None for item in observations),
    "qualified_live_judgements": 0, "groups": groups,
    "live_visibility": None, "live_citation_rate": None, "semantic_quality": None,
}
(run / "metrics-recompute.json").write_text(json.dumps(metrics, indent=2) + "\n")
window = sorted(item["sampled_at"] for item in observations)
lines = [
    "# TechUnity Connect — Internal Pipeline Pilot", "",
    "**UPSTREAM_STUB / UPSTREAM_STUB · SYNTHETIC TEST DATA**", "",
    "## Method and Scope", "",
    f"Collection window runs from {window[0]} through {window[-1]}. The provider is stub and the judge version is stub+request-1.", "",
    "The upstream stub echoes each input question. This report verifies storage, extraction, grouping and evidence export. Consumer-interface visibility, real API behavior, semantic quality and commercial delivery remain unverified.", "",
    "## Pipeline Completeness", "",
    "| Item | Result |", "|---|---|",
    "| Planned / stored observations | 10 / 10 |",
    "| Stub-processed / stored answers | 10 / 10 |",
    "| Qualified live judgements | N/A |",
    "| Live API requests | 0 |",
    "| Live account billing verification | NOT_RUN |",
    "| Consumer-interface visibility | N/A |", "",
    "## Fixture Metrics", "",
    "| Cohort | Stub matches | Stub answers |", "|---|---|---|",
    f"| Non-brand | {groups['non_brand']['stub_mentions']} | {groups['non_brand']['answers']} |",
    f"| Brand control | {groups['brand_control']['stub_mentions']} | {groups['brand_control']['answers']} |", "",
    "The two branded questions contain the brand name, which the echo preserves. All ten observation IDs below support the echo finding. These counts describe fixture processing. Live mention, recommendation, sentiment and official citation rates remain N/A.", "",
    "## Evidence Index", "",
]
for item in sorted(observations, key=lambda item: item["observation_id"]):
    raw = run / "raw" / f"upstream-{item['observation_id']}.json"
    assert raw.exists()
    lines.extend([
        f"### {item['observation_id']}", "",
        f"Group `{item['prompt_group']}`. Prompt `{item['prompt_id']}`.", "",
        "> " + item["answer"].replace("\n", "\n> "), "",
        f"Raw evidence `../raw/{raw.name}` has SHA-256 `{hashlib.sha256(raw.read_bytes()).hexdigest()}`.", "",
    ])
lines.extend([
    "## Next Steps", "",
    "Confirm one answer-provider and judge combination with valid free quota and enforceable spending controls. Review the candidate judgement labels. Complete the remaining P0 cases before deciding on an internal live API pilot.", "",
])
markdown = "\n".join(lines)
(run / "reports/SAMPLE_REPORT_EN.md").write_text(markdown)
document = "<!doctype html><html lang=en><meta charset=utf-8>"
document += '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">'
document += "<title>TUC Internal Pipeline Pilot</title><style>body{max-width:960px;margin:40px auto;padding:0 24px;color:#1c2634;background:#fff;font:16px/1.6 system-ui}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}h1{font-size:30px}aside{padding:16px;border:1px solid #bd8b17;background:#fff6d8}</style>"
document += "<h1>TechUnity Connect</h1><aside><strong>UPSTREAM_STUB · SYNTHETIC TEST DATA</strong></aside><pre>"
document += html.escape(markdown) + "</pre></html>"
(run / "reports/SAMPLE_REPORT_EN.html").write_text(document)
print(json.dumps({"markdown_sha256": hashlib.sha256(markdown.encode()).hexdigest(), "html_sha256": hashlib.sha256(document.encode()).hexdigest(), "groups": groups}))
