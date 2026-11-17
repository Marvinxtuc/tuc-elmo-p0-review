#!/usr/bin/env python3
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
run = Path(json.loads((root / "config/active-run.json").read_text())["path"])
g0 = Path("<G0_AUDIT_ROOT>")
website = Path("<USER_HOME>/Desktop/TechUnityConnect")
source = root / "upstream/elmo"


def command(args, cwd=None, env=None):
    return subprocess.check_output(args, cwd=cwd, env=env, text=True).strip()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, data):
    (run / name).write_text(json.dumps(data, indent=2) + "\n")


before = json.loads((g0 / "evidence/website-tracked-hashes-before.json").read_text())
files = command(["git", "ls-files"], website).splitlines()
after = {name: {"bytes": (website / name).stat().st_size, "sha256": digest(website / name)} for name in files}
differences = [name for name in set(before) | set(after) if before.get(name) != after.get(name)]
website_state = {
    "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "head": command(["git", "rev-parse", "HEAD"], website),
    "branch": command(["git", "branch", "--show-current"], website),
    "status": command(["git", "status", "--porcelain"], website),
    "tracked_file_count": len(after), "differences": sorted(differences),
    "production_sha": None, "production_changes_performed": False,
}
assert not differences, website_state
assert website_state["head"] == "aa697643422270b8ba478e6a3a39fd15bd3547d6"
write("website-after.json", website_state)
write("website-tracked-hashes-after.json", after)
assert command(["git", "status", "--porcelain"], g0 / "upstream/elmo") == ""
write("g0-frozen-verification.json", {
    "source_worktree_clean": True,
    "evidence_manifest_sha256": digest(g0 / "evidence/evidence-manifest.json"),
    "evidence_checksums_sha256": digest(g0 / "evidence/SHA256SUMS"),
})

patch = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=source)
untracked = command(["git", "ls-files", "--others", "--exclude-standard"], source).splitlines()
assert untracked == ["packages/lib/src/p0-policy.test.ts"], untracked
for name in untracked:
    result = subprocess.run(["git", "diff", "--no-index", "--binary", "--", "/dev/null", name], cwd=source, capture_output=True)
    assert result.returncode == 1
    patch += result.stdout
patch_path = root / "patches/p0-offline.patch"
patch_path.write_bytes(patch)
changed = command(["git", "diff", "--name-only", "HEAD"], source).splitlines() + untracked
write("patch-files-final.json", {name: {"bytes": (source / name).stat().st_size, "sha256": digest(source / name)} for name in changed})

environment = dict(os.environ)
environment.update({"DOCKER_HOST": f"unix://{root}/runtime/colima/tuc-p0/docker.sock", "DOCKER_CONFIG": str(root / "runtime/docker-client")})
container = json.loads(command(["docker", "inspect", "tuc-elmo-p0-postgres"], env=environment))[0]
db = command(["docker", "exec", "tuc-elmo-p0-postgres", "psql", "-U", "tuc_p0", "-d", "tuc_elmo_p0_test", "-At", "-c",
              "SELECT jsonb_build_object('database',current_database(),'role',current_user,'version',version(),'migration_count',(SELECT count(*) FROM drizzle.__drizzle_migrations),'last_migration_created_at',(SELECT max(created_at) FROM drizzle.__drizzle_migrations));"], env=environment)
app = dict(line.split("=", 1) for line in (root / "secrets/app.env").read_text().splitlines() if line)
redacted = {name: value if name in {"DEPLOYMENT_MODE", "APP_URL", "VITE_APP_URL", "DISABLE_TELEMETRY", "SCRAPE_TARGETS", "ONBOARDING_LLM_TARGET", "RUNS_PER_PROMPT", "TUC_P0_OFFLINE", "VITE_TUC_P0_MODE", "NODE_ENV", "HOST", "PORT"} else "[PRIVATE_TEST_VALUE]" for name, value in app.items()}
state = {
    "at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "app_environment": redacted,
    "env_copies_equal": digest(root / "secrets/app.env") == digest(source / ".env") == digest(source / "apps/web/.env"),
    "secret_file_permissions": {str(path.relative_to(root)): oct(path.stat().st_mode & 0o777) for path in (root / "secrets").iterdir() if path.is_file()},
    "command_home": str(root / "runtime/home"),
    "container": {"name": container["Name"], "image_id": container["Image"], "memory_bytes": container["HostConfig"]["Memory"], "nano_cpus": container["HostConfig"]["NanoCpus"], "ports": container["HostConfig"]["PortBindings"], "network_mode": container["HostConfig"]["NetworkMode"], "mount_destinations": [mount["Destination"] for mount in container["Mounts"]]},
    "database": json.loads(db),
    "global_node": command(["/opt/homebrew/bin/node", "--version"]),
    "global_pnpm": command(["/opt/homebrew/bin/pnpm", "--version"]),
}
write("environment.redacted.json", state)
lock = {
    "schema_version": "p0-A0-1", "upstream_origin": command(["git", "remote", "get-url", "origin"], source),
    "upstream_commit": command(["git", "rev-parse", "HEAD"], source),
    "upstream_tree": command(["git", "rev-parse", "HEAD^{tree}"], source),
    "lockfile_sha256": digest(source / "pnpm-lock.yaml"),
    "supply_chain_policy_sha256": digest(source / "pnpm-workspace.yaml"),
    "instructions_sha256": digest(source / "AGENTS.md"),
    "patch": "patches/p0-offline.patch", "patch_sha256": digest(patch_path),
    "patch_file_count": len(changed),
    "node": "24.22.3", "pnpm": "12.18.0", "postgres": "18.7",
    "postgres_image": "postgres@sha256:b6972e1115a4ff8eba5d7f7d19184926d1e16d7d1136ae1e1a7ebf286da0f015",
    "database_schema": json.loads(db),
    "config_hashes": {str(path.relative_to(root)): digest(path) for path in sorted((root / "config").iterdir()) if path.is_file()},
    "fixture_hashes": {str(path.relative_to(root)): digest(path) for path in sorted((root / "fixtures").iterdir()) if path.is_file()},
    "website_head": website_state["head"], "website_files_unchanged": len(after),
    "plan_sha256": "d31a54c561a2d218e16c68dbbba7fb49333f5150aaf9f8ec7e9dc93d2a1fbc73",
}
assert lock["upstream_commit"] == "15c2d5f1b56682ce98e6c6ed76e254eec124e15e"
assert lock["lockfile_sha256"] == "743919e30a100aa0b8386b3b60b9ac8bf0a64de702c0cc6b4ffa9180d66c5151"
write("source-lock.json", lock)
(root / "SOURCE_LOCK.json").write_text(json.dumps(lock, indent=2) + "\n")
print(json.dumps({"website_unchanged_files": len(after), "changed_source_files": len(changed), "patch_sha256": lock["patch_sha256"], "database": state["database"]}))
