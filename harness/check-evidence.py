#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
run = Path(json.loads((root / "config/active-run.json").read_text())["path"])
probe = run / "integrity-probe"
probe.mkdir(exist_ok=True)
data = probe / "synthetic.txt"
data.write_text("synthetic integrity fixture\n")
manifest = probe / "manifest.json"
manifest.write_text(json.dumps({"files": [{"path": str(data.relative_to(root)), "bytes": data.stat().st_size, "sha256": hashlib.sha256(data.read_bytes()).hexdigest()}]}))


def verify(path):
    result = subprocess.run([sys.executable, str(root / "p0ctl"), "verify", "--manifest", str(path.relative_to(root))], capture_output=True, text=True)
    return {"exit_code": result.returncode, "result": json.loads(result.stdout)}


valid = verify(manifest)
assert valid["exit_code"] == 0, valid
data.write_text("synthetic integrity Fixture\n")
tampered = verify(manifest)
assert tampered["exit_code"] == 1 and tampered["result"]["failures"][0]["error"] == "CONTENT_CHANGED", tampered
escape = probe / "escape-manifest.json"
escape.write_text(json.dumps({"files": [{"path": "../outside", "bytes": 0, "sha256": "0" * 64}]}))
unsafe = verify(escape)
assert unsafe["exit_code"] == 1 and unsafe["result"]["failures"][0]["error"] == "UNSAFE_PATH", unsafe
outcome = {"valid": valid, "one_character_changed": tampered, "path_escape": unsafe, "status": "PASS", "scope": "Disposable synthetic evidence copy. Original observations and reports retained."}
(run / "integrity-verification.json").write_text(json.dumps(outcome, indent=2) + "\n")
print(json.dumps(outcome))
