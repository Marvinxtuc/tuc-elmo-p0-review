#!/usr/bin/env python3
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
active = json.loads((root / "config/active-run.json").read_text())
run = Path(active["path"])
parser = argparse.ArgumentParser()
parser.add_argument("--label", required=True)
parser.add_argument("--cwd", default=str(root / "upstream/elmo"))
parser.add_argument("--timeout", type=int, default=1200)
parser.add_argument("--app-env", action="store_true")
parser.add_argument("--background", action="store_true")
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
command = args.command
if command and command[0] == "--":
    command = command[1:]
if not command:
    parser.error("A command is required")

node_bin = root / "runtime/node-v24.22.3-darwin-arm64/bin"
pnpm_bin = root / "runtime/pnpm-native/package"
environment = {
    name: value
    for name, value in os.environ.items()
    if name in {"HOME", "USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL", "TERM"}
}
environment.update({
    "HOME": str(root / "runtime/home"),
    "PATH": f"{node_bin}:{pnpm_bin}:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
    "COLIMA_HOME": str(root / "runtime/colima"),
    "LIMA_HOME": str(root / "runtime/lima"),
    "DOCKER_CONFIG": str(root / "runtime/docker-client"),
    "DOCKER_HOST": f"unix://{root}/runtime/colima/tuc-p0/docker.sock",
    "PNPM_HOME": str(pnpm_bin),
    "XDG_CONFIG_HOME": str(root / "runtime/xdg-config"),
    "XDG_CACHE_HOME": str(root / "runtime/xdg-cache"),
    "XDG_DATA_HOME": str(root / "runtime/xdg-data"),
    "npm_config_userconfig": str(root / "config/package-manager-empty.npmrc"),
    "npm_config_globalconfig": str(root / "config/package-manager-empty.npmrc"),
    "CI": "true",
    "DO_NOT_TRACK": "1",
    "DISABLE_TELEMETRY": "1",
    "TURBO_TELEMETRY_DISABLED": "1",
    "COREPACK_ENABLE_NETWORK": "0",
    "TUC_P0_OFFLINE": "0",
})
redactions = []
if args.app_env:
    app_environment = dict(
        line.split("=", 1)
        for line in (root / "secrets/app.env").read_text().splitlines()
        if line and not line.startswith("#")
    )
    if app_environment.get("SCRAPE_TARGETS") != "stub:stub":
        raise SystemExit("Only the approved stub targets are enabled by this runner")
    environment.update(app_environment)
    for name in ["DATABASE_URL", "BETTER_AUTH_SECRET", "ELMO_ENCRYPTION_KEY", "ADMIN_API_KEYS"]:
        if app_environment.get(name):
            redactions.append(app_environment[name])
    password = urlparse(app_environment["DATABASE_URL"]).password
    if password:
        redactions.append(password)
if "migrate" in command:
    approval = json.loads((root / "approvals/A0.json").read_text())
    database = urlparse(environment.get("DATABASE_URL", ""))
    if (
        approval.get("approval_id") != "A0-user-20261117"
        or database.hostname != "127.0.0.1"
        or database.port != 17332
        or database.path.lstrip("/") not in approval["new_test_databases"]
    ):
        raise SystemExit("Migration is outside the approved new test database scope")
started = datetime.datetime.now(datetime.timezone.utc).isoformat()
log = run / "logs" / f"{args.label}.log"
if args.background:
    with log.open("x") as output:
        process = subprocess.Popen(
            command, cwd=args.cwd, env=environment, stdout=output,
            stderr=subprocess.STDOUT, start_new_session=True,
        )
    path = run / "processes.json"
    records = json.loads(path.read_text()) if path.exists() else []
    record = {
        "name": args.label, "pid": process.pid, "command": command,
        "started_at_utc": started, "output": str(log.relative_to(run)),
    }
    records.append(record)
    path.write_text(json.dumps(records, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    raise SystemExit(0)
with log.open("x") as output:
    try:
        result = subprocess.run(
            command, cwd=args.cwd, env=environment, stdout=output,
            stderr=subprocess.STDOUT, timeout=args.timeout,
        )
        exit_code = result.returncode
    except subprocess.TimeoutExpired:
        exit_code = 124

sanitized = log.read_text(errors="replace")
for value in sorted(redactions, key=len, reverse=True):
    sanitized = sanitized.replace(value, "[REDACTED_TEST_SECRET]")
log.write_text(sanitized)

record = {
    "command": command,
    "cwd": args.cwd,
    "started_at_utc": started,
    "ended_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "exit_code": exit_code,
    "output": str(log.relative_to(run)),
    "environment": "Allowlisted host fields and project-local tool/runtime paths",
}
with (run / "commands.jsonl").open("a") as output:
    output.write(json.dumps(record) + "\n")
print(json.dumps(record, indent=2))
print(log.read_text(errors="replace")[-3500:])
raise SystemExit(exit_code)
