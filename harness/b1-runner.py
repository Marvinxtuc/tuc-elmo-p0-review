#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import threading
from urllib.parse import urlparse

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--label", required=True)
parser.add_argument("--cwd", default=str(root / "upstream/elmo"))
parser.add_argument("--timeout", type=int, default=600)
parser.add_argument("--stage", choices=["runtime", "quality", "mock"], default="runtime")
parser.add_argument("--database", choices=["tuc_elmo_p0_test", "tuc_elmo_p0_restore"], default="tuc_elmo_p0_test")
parser.add_argument("--app-env", action="store_true")
parser.add_argument("--background", action="store_true")
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
command = args.command[1:] if args.command[:1] == ["--"] else args.command
if not command or not re.fullmatch(r"[a-zA-Z0-9_-]+", args.label):
    parser.error("A command and a simple unique label are required")
if not Path(args.cwd).resolve().is_relative_to(root):
    raise SystemExit("Working directory escapes the B1 worktree")
run = root / Path(json.loads((root / "config/active-run.json").read_text())["path"])
if not run.resolve().is_relative_to(root / "runs") or run.name.endswith("-A0"):
    raise SystemExit("Only the new B1 evidence directory may be written")
configuration = json.loads((root / "config/local-runtime.json").read_text())
approval = json.loads(Path(configuration["source_approval"]).read_text())
runtime = Path(configuration["runtime_root"])
if approval.get("approval_id") != "A0-user-20261117" or runtime.parent != Path(approval["runtime_root"]):
    raise SystemExit("Existing A0 runtime identity does not match")

environment = {name: value for name, value in os.environ.items()
               if name in {"USER", "LOGNAME", "TMPDIR", "LANG", "LC_ALL", "TERM"}}
environment.update({
    "HOME": str(root / "runtime/home"),
    "PATH": f"{runtime}/node-v24.22.3-darwin-arm64/bin:{root}/runtime/pnpm-recovered:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
    "COLIMA_HOME": str(runtime / "colima"), "LIMA_HOME": str(runtime / "lima"),
    "DOCKER_CONFIG": str(runtime / "docker-client"),
    "DOCKER_HOST": f"unix://{runtime}/colima/tuc-p0/docker.sock",
    "XDG_CONFIG_HOME": str(root / "runtime/xdg-config"),
    "XDG_CACHE_HOME": str(root / "runtime/xdg-cache"),
    "XDG_DATA_HOME": str(root / "runtime/xdg-data"),
    "npm_config_userconfig": str(root / "config/package-manager-empty.npmrc"),
    "npm_config_globalconfig": str(root / "config/package-manager-empty.npmrc"),
    "npm_config_store_dir": str(runtime / "pnpm-store"),
    "npm_config_verify_deps_before_run": "false",
    "CI": "true", "DO_NOT_TRACK": "1", "DISABLE_TELEMETRY": "1",
    "TURBO_TELEMETRY_DISABLED": "1", "COREPACK_ENABLE_NETWORK": "0",
    "TUC_P0_OFFLINE": "1", "TUC_P0_STAGE": args.stage, "TUC_P0_BATCH_ID": run.name,
})
redactions = []
if args.stage == "runtime":
    values = dict(line.split("=", 1) for line in (root / "secrets/app.env").read_text().splitlines()
                  if line and not line.startswith("#"))
    expected = {"SCRAPE_TARGETS": "stub:stub", "ONBOARDING_LLM_TARGET": "stub:stub",
                "TYPESAFE_API_KEY": "stub", "TUC_P0_OFFLINE": "1", "RUNS_PER_PROMPT": "1",
                "DEPLOYMENT_MODE": "local", "HOST": "127.0.0.1"}
    if any(values.get(key) != value for key, value in expected.items()):
        raise SystemExit("Runtime configuration conflicts with the offline policy")
    if any(key.endswith("_API_KEY") and value != "stub" for key, value in values.items()):
        raise SystemExit("Non-stub API credentials are outside the runtime scope")
    database = urlparse(values["DATABASE_URL"])
    if database.hostname != "127.0.0.1" or database.port != 17332 or args.database not in approval["new_test_databases"]:
        raise SystemExit("Database target is outside A0")
    values["DATABASE_URL"] = database._replace(path="/" + args.database).geturl()
    environment.update(values)
    redactions = [value for key, value in values.items()
                  if key in {"DATABASE_URL", "BETTER_AUTH_SECRET", "ELMO_ENCRYPTION_KEY", "ADMIN_API_KEYS"}]
    if database.password:
        redactions.append(database.password)
elif args.stage == "quality":
    allowed = {"lint", "test", "test:scripts", "build", "check-types", "biome", "vitest"}
    if not any(item in allowed for item in command):
        raise SystemExit("Quality stage requires a declared quality command")
    environment.update({"TUC_P0_OFFLINE": "0", "NODE_ENV": "test" if any(item in {"test", "vitest"} for item in command) else "production",
                        "SCRAPE_TARGETS": "stub:stub", "ONBOARDING_LLM_TARGET": "stub:stub",
                        "TYPESAFE_API_KEY": "stub", "APP_URL": "http://127.0.0.1:17300",
                        "VITE_APP_URL": "http://127.0.0.1:17300",
                        "BETTER_AUTH_SECRET": "local-schema-snapshot", "ELMO_ENCRYPTION_KEY": ""})
    environment["TUC_P0_SCHEMA_SHA256"] = json.loads((root / "config/schema-snapshot.json").read_text())["sha256"]

environment["TUC_P0_STAGE"] = args.stage
environment["TUC_P0_BATCH_ID"] = run.name
policy = root / "config" / ("runtime.sb" if args.stage == "runtime" else args.stage + ".sb")
environment["TUC_P0_POLICY_SHA256"] = hashlib.sha256(policy.read_bytes()).hexdigest()
environment["TUC_P0_EGRESS_LOG"] = str(run / "egress.jsonl")
environment["TUC_P0_LEDGER"] = str(root / "runtime/budget.sqlite")
environment["NODE_OPTIONS"] = f"--require={root}/harness/offline-preload.cjs"
for directory in [root / "runtime/home", root / "runtime/xdg-config", root / "runtime/xdg-cache", root / "runtime/xdg-data"]:
    directory.mkdir(parents=True, exist_ok=True)
if "migrate" in command and args.stage != "runtime":
    raise SystemExit("Migrations require the approved runtime database context")
if Path(command[0]).name == "pnpm":
    command.insert(1, "--config.verifyDepsBeforeRun=false")
command = ["/usr/bin/sandbox-exec", "-f", str(policy), *command]
log = run / "logs" / f"{args.label}.log"
if log.exists():
    raise SystemExit("Evidence labels are append-only and must be unique")
record = {"label": args.label, "command": command, "cwd": args.cwd, "stage": args.stage,
          "started_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "policy_sha256": environment["TUC_P0_POLICY_SHA256"],
          "offline": environment["TUC_P0_OFFLINE"], "output": str(log.relative_to(run))}


def execute():
    with log.open("x") as output:
        process = subprocess.Popen(command, cwd=args.cwd, env=environment, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, start_new_session=True)
        record["pid"] = process.pid
        if args.background:
            path = run / "processes.json"
            records = json.loads(path.read_text()) if path.exists() else []
            records.append(dict(record))
            path.write_text(json.dumps(records, indent=2) + "\n")

        def timeout():
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)

        timer = threading.Timer(args.timeout, timeout)
        timer.start()
        try:
            for line in process.stdout:
                for value in sorted(redactions, key=len, reverse=True):
                    line = line.replace(value, "[REDACTED_TEST_SECRET]")
                line = re.sub(r"(secretKey:\s*)\d+", r"\1[REDACTED_PROTOCOL_TOKEN]", line)
                output.write(line)
                output.flush()
            record["exit_code"] = process.wait()
        finally:
            timer.cancel()
    record["ended_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (run / "commands.jsonl").open("a") as output:
        output.write(json.dumps(record) + "\n")
    return record["exit_code"]


if args.background:
    pid = os.fork()
    if pid:
        print(json.dumps({"supervisor_pid": pid, "label": args.label, "stage": args.stage}))
        raise SystemExit(0)
    os.setsid()
    with open(os.devnull, "r+") as null:
        for descriptor in [0, 1, 2]:
            os.dup2(null.fileno(), descriptor)
    os._exit(execute())
exit_code = execute()
print(json.dumps(record, indent=2))
print(log.read_text(errors="replace")[-2500:])
raise SystemExit(exit_code)
