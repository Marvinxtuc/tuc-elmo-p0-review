#!/usr/bin/env python3
import datetime
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
run = Path(json.loads((root / "config/active-run.json").read_text())["path"])
rows = [json.loads(line) for line in (run / "test-results.jsonl").read_text().splitlines()]
assert len(rows) == 64 and len({row["test_id"] for row in rows}) == 64
for row in rows:
    if row["status"] == "PASS":
        assert row["evidence_refs"], row["test_id"]
        for reference in row["evidence_refs"]:
            assert (run / reference).is_file(), (row["test_id"], reference)
assert json.loads((run / "shutdown-verification.json").read_text())["status"] == "PASS"
assert json.loads((run / "secret-scan.json").read_text())["status"] == "PASS"

website = Path("<USER_HOME>/Desktop/TechUnityConnect")
before = json.loads(Path("<G0_AUDIT_ROOT>/evidence/website-tracked-hashes-before.json").read_text())
for name, expected in before.items():
    data = (website / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected["sha256"], name

paths = {path for path in root.iterdir() if path.is_file() and (path.suffix in {".md", ".html"} or path.name in {"SOURCE_LOCK.json", "test-results.jsonl", "p0ctl"})}
for directory in [root / "harness", root / "config", root / "approvals", root / "fixtures", root / "patches", run]:
    paths.update(path for path in directory.rglob("*") if path.is_file() and path.name != "test-database.dump")
source = root / "upstream/elmo"
tracked = subprocess.check_output(["git", "ls-files"], cwd=source, text=True).splitlines()
paths.update(source / name for name in tracked)
paths.add(source / "packages/lib/src/p0-policy.test.ts")
files = []
for path in sorted(paths, key=lambda item: str(item.relative_to(root))):
    relative = path.relative_to(root)
    assert path.resolve().is_relative_to(root) and not path.is_symlink(), str(relative)
    assert relative.parts[0] not in {"secrets", "runtime"}, str(relative)
    assert not any(part in {"node_modules", ".git"} for part in relative.parts), str(relative)
    assert path.name != ".env", str(relative)
    data = path.read_bytes()
    files.append({"path": relative.as_posix(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "classification": "INTERNAL_SYNTHETIC_AUDIT"})
manifest = {
    "schema_version": "1.0", "created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "root": str(root), "files": files,
    "excluded": ["secrets/**", "runtime/**", "**/.env", "**/node_modules/**", "**/.git/**", "test-database.dump", "evidence-manifest.json", "SHA256SUMS"],
    "integrity_boundary": "Local reproducibility checks. Owner must retain this manifest digest independently.",
}
path = root / "evidence-manifest.json"
path.write_text(json.dumps(manifest, indent=2) + "\n")
checksums = {item["path"]: item["sha256"] for item in files}
checksums[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
(root / "SHA256SUMS").write_text("".join(f"{checksums[name]}  {name}\n" for name in sorted(checksums)))
print(json.dumps({"files": len(files), "manifest_sha256": checksums[path.name], "sha256sums_sha256": hashlib.sha256((root / "SHA256SUMS").read_bytes()).hexdigest()}))
