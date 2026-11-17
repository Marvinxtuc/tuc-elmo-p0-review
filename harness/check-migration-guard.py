#!/usr/bin/env python3
import contextlib
import io
import json
from pathlib import Path
import runpy
import sys
from unittest.mock import patch

root = Path(__file__).resolve().parents[1]
read_text = Path.read_text
outcomes = []
for case in ["missing-A0", "outside-test-database"]:
    def intercepted(path, *args, **kwargs):
        data = read_text(path, *args, **kwargs)
        if case == "missing-A0" and path == root / "approvals/A0.json":
            return "{}"
        if case == "outside-test-database" and path == root / "secrets/app.env":
            return data.replace("/tuc_elmo_p0_test", "/outside_approved_scope")
        return data

    with patch.object(Path, "read_text", intercepted), patch("subprocess.run") as transport:
        sys.argv = [str(root / "harness/run-command.py"), "--label", "must-not-launch-" + case, "--app-env", "--", "migrate"]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(root / "harness/run-command.py"), run_name="__main__")
        except SystemExit as error:
            assert str(error) == "Migration is outside the approved new test database scope", str(error)
        else:
            raise AssertionError("Migration guard accepted a forbidden target")
        transport.assert_not_called()
    outcomes.append({"case": case, "status": "PASS", "subprocess_calls": 0})
print(json.dumps(outcomes))
