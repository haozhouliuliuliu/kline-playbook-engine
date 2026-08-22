"""江河逐条 PRIMARY 映射草案的回归测试。"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class JianghePrimaryClaimMappingDraftTests(unittest.TestCase):
    def run_command(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *arguments],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_draft_is_deterministically_rebuildable(self) -> None:
        result = self.run_command(
            "tools/build_jianghe_primary_claim_mapping_draft_v0_1.py", "--check"
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_draft_passes_independent_mechanical_validation(self) -> None:
        result = self.run_command("tools/validate_jianghe_primary_claim_mapping_draft_v0_1.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("PRIMARY_MAPPING_DRAFT_VALID=YES", result.stdout)


if __name__ == "__main__":
    unittest.main()
