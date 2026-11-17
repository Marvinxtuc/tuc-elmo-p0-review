#!/usr/bin/env python3
import datetime
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
run = Path(json.loads((root / "config/active-run.json").read_text())["path"])
app = dict(line.split("=", 1) for line in (root / "secrets/app.env").read_text().splitlines() if line)
needles = {name: app[name].encode() for name in ["BETTER_AUTH_SECRET", "ELMO_ENCRYPTION_KEY", "ADMIN_API_KEYS"]}
for path in (root / "secrets").iterdir():
    if path.suffix == ".json":
        data = json.loads(path.read_text())
        for name in ["value", "password"]:
            if name in data:
                needles[f"{path.name}.{name}"] = data[name].encode()
    elif path.name == "postgres.env":
        data = dict(line.split("=", 1) for line in path.read_text().splitlines() if line)
        needles["POSTGRES_PASSWORD"] = data["POSTGRES_PASSWORD"].encode()

excluded_directories = {"node_modules", ".git", ".turbo"}
excluded_names = {".env", "test-database.dump"}
scanned = 0
size = 0
findings = []


def files(directory):
    for path in directory.iterdir():
        if path.is_symlink():
            continue
        if path.is_dir():
            if path.name not in excluded_directories and path not in {root / "secrets", root / "runtime"}:
                yield from files(path)
        elif path.name not in excluded_names:
            yield path


for path in files(root):
    content = path.read_bytes()
    scanned += 1
    size += len(content)
    for name, value in needles.items():
        if value in content:
            findings.append({"path": str(path.relative_to(root)), "secret_field": name})
result = {
    "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "status": "FAIL" if findings else "PASS", "files_scanned": scanned, "bytes_scanned": size,
    "findings": findings, "secret_values_printed": False,
    "excluded_directories": sorted(excluded_directories) + ["<project>/secrets", "<project>/runtime"], "excluded_names": sorted(excluded_names),
    "scope": "Exact random synthetic credentials in ordinary reports, fixtures, prompts, logs, source, patch and build outputs. Runtime profiles, encrypted dump and env are private stores. General secret-pattern and forensic scans remain outside this exact-value result.",
}
(run / "secret-scan.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
raise SystemExit(1 if findings else 0)
