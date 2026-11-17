#!/usr/bin/env python3
import argparse
import datetime
import json
import os
from pathlib import Path
import signal
import subprocess
import time

root = Path(__file__).resolve().parents[1]
run = Path(json.loads((root / "config/active-run.json").read_text())["path"])
parser = argparse.ArgumentParser()
parser.add_argument("--name")
args = parser.parse_args()
path = run / "processes.json"
records = json.loads(path.read_text())
ordered = sorted(records, key=lambda record: "tunnel" in record["name"])
for record in ordered:
    if args.name and record["name"] != args.name:
        continue
    pid = record["pid"]
    command = subprocess.run(
        ["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True,
    )
    if command.returncode != 0:
        record["stop_status"] = "ALREADY_STOPPED"
        continue
    cwd = subprocess.run(
        ["lsof", "-a", "-p", str(pid), "-d", "cwd", "-Fn"],
        capture_output=True, text=True,
    )
    if str(root) not in command.stdout and str(root) not in cwd.stdout:
        record["stop_status"] = "SKIPPED_SCOPE_MISMATCH"
        continue
    if os.getpgid(pid) != pid:
        record["stop_status"] = "SKIPPED_PROCESS_GROUP_MISMATCH"
        continue
    os.killpg(pid, signal.SIGTERM)
    record["stop_status"] = "STOP_REQUESTED"
    record["stop_requested_at_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    for _ in range(150):
        state = subprocess.run(["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True)
        if state.returncode != 0 or state.stdout.strip().startswith("Z"):
            record["stop_status"] = "STOPPED"
            break
        time.sleep(0.2)
    else:
        record["stop_status"] = "STOP_TIMEOUT"
        path.write_text(json.dumps(records, indent=2) + "\n")
        raise SystemExit("A project process did not stop before its dependency shutdown")
path.write_text(json.dumps(records, indent=2) + "\n")
print(json.dumps([{"name": r["name"], "stop_status": r.get("stop_status")} for r in records if not args.name or r["name"] == args.name]))
