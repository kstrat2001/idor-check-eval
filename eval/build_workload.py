"""Regenerate the suite command in workloads/idor-check.json from hidden/.

The grader runs the suite command inside a copy of the result, where this
folder does not exist, so the hidden tests travel inside the command itself.
Edit hidden/*.py, then run: python3 eval/build_workload.py
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
runner = (HERE / "hidden" / "run_junit.py").read_text()
hidden = (HERE / "hidden" / "test_hidden_sharing.py").read_text()
REPO = HERE.parent
originals = {
    f.relative_to(REPO).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest()
    for f in sorted((REPO / "tests").glob("*.py"))
}
hidden = hidden.replace('"__ORIGINAL_TEST_FILES__"', repr(originals))
script = runner.replace('"__HIDDEN_TESTS__"', repr(hidden))
assert "DARKMUX_GRADE" not in script
command = "python3 - ${REPORT} <<'DARKMUX_GRADE'\n" + script + "DARKMUX_GRADE\n"

path = HERE / "workloads" / "idor-check.json"
doc = json.loads(path.read_text())
doc["workload"]["verify"]["grade"]["suite"]["command"] = command
path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")
print(f"updated {path.name}: suite command is {len(command)} bytes")
