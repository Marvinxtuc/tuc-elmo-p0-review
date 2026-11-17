#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "REVIEW_MANIFEST.json").read_text())
failures = []
for item in manifest["files"]:
    relative = Path(item["path"])
    target = root / relative
    if relative.is_absolute() or ".." in relative.parts or target.is_symlink() or not target.resolve().is_relative_to(root):
        failures.append({"path": item["path"], "error": "UNSAFE_PATH"})
        continue
    if not target.is_file():
        failures.append({"path": item["path"], "error": "MISSING"})
        continue
    data = target.read_bytes()
    if len(data) != item["bytes"] or hashlib.sha256(data).hexdigest() != item["sha256"]:
        failures.append({"path": item["path"], "error": "CONTENT_CHANGED"})
print(json.dumps({"checked": len(manifest["files"]), "failures": failures, "status": "FAIL" if failures else "PASS"}, indent=2))
raise SystemExit(1 if failures else 0)
