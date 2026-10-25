"""The suite has to pass in more than one environment.

The agent works inside a container where the repo sits at an absolute path.
Verification may run somewhere else, where that path does not exist. A test
that embeds the container's path passes for the agent and fails for everyone
else, so this check makes that failure visible where the work happens.
"""

import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SELF = Path(__file__).name


class SuitePortabilityTest(unittest.TestCase):
    def test_no_test_embeds_an_absolute_filesystem_path(self):
        # This file is skipped: its own pattern would match itself.
        offenders = []
        for path in sorted(HERE.glob("test_*.py")):
            if path.name == SELF:
                continue
            for match in re.finditer(r"[\"'](/[A-Za-z0-9._-]+/[^\"'\n]*)[\"']", path.read_text()):
                offenders.append(f"{path.name}: {match.group(1)}")
        self.assertEqual(
            offenders,
            [],
            "resolve paths from Path(__file__) instead, so the suite runs anywhere",
        )


if __name__ == "__main__":
    unittest.main()
