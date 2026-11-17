#!/usr/bin/env python3
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

root = Path(__file__).resolve().parents[1]
run = Path(json.loads((root / "config/active-run.json").read_text())["path"])
environment = dict(os.environ)
environment["DOCKER_HOST"] = "unix://" + str(root / "runtime/colima/tuc-p0/docker.sock")
environment["DOCKER_CONFIG"] = str(root / "runtime/docker-client")
container = "tuc-elmo-p0-postgres"


def query(database, sql):
    result = subprocess.run(
        ["docker", "exec", container, "psql", "-U", "tuc_p0", "-d", database, "-At", "-c", sql],
        env=environment, capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def table_hashes(database):
    tables = query(database, "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;").splitlines()
    hashes = {}
    for name in tables:
        quoted = '"' + name.replace('"', '""') + '"'
        data = json.loads(query(database, f"SELECT coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text),'[]'::jsonb) FROM public.{quoted} t;"))
        canonical = json.dumps(data, sort_keys=True, separators=(",", ":")).encode()
        hashes[name] = {"count": len(data), "sha256": hashlib.sha256(canonical).hexdigest()}
    return hashes


assert query("tuc_elmo_p0_restore", "SELECT count(*) FROM pg_tables WHERE schemaname='public';") == "0", "Restore target contains existing tables"
before = table_hashes("tuc_elmo_p0_test")
assert before["prompt_runs"]["count"] == 10
assert before["organization"]["count"] == 1
backup = run / "test-database.dump"
with backup.open("xb") as output:
    subprocess.run(
        ["docker", "exec", container, "pg_dump", "-U", "tuc_p0", "-d", "tuc_elmo_p0_test", "-Fc", "--no-owner", "--no-acl"],
        env=environment, stdout=output, check=True,
    )
backup.chmod(0o600)
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
timer = time.monotonic()
with backup.open("rb") as source:
    subprocess.run(
        ["docker", "exec", "-i", container, "pg_restore", "-U", "tuc_p0", "-d", "tuc_elmo_p0_restore", "--no-owner", "--no-acl"],
        env=environment, stdin=source, check=True,
    )
elapsed = time.monotonic() - timer
after = table_hashes("tuc_elmo_p0_restore")
assert before == after, "Restored table contents differ"
result = {
    "started_at_utc": started, "restore_seconds": round(elapsed, 3),
    "source_database": "tuc_elmo_p0_test", "restore_database": "tuc_elmo_p0_restore",
    "target_empty_before_restore": True, "public_table_hashes_match": True,
    "tables": before, "backup_file": "test-database.dump",
    "backup_sha256": hashlib.sha256(backup.read_bytes()).hexdigest(),
    "secret_material_location": "Project-private secrets directory, excluded from ordinary evidence manifests",
    "production_rpo_rto_claimed": False,
}
(run / "restore-verification.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"restored_tables": len(before), "prompt_runs": before["prompt_runs"]["count"], "organizations": before["organization"]["count"], "table_hashes_match": True, "restore_seconds": result["restore_seconds"]}))
