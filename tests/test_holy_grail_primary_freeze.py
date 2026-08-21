import json
import unittest
from pathlib import Path

from tools.build_holy_grail_primary_freeze_v0_1 import build_payload


class HolyGrailPrimaryFreezeTests(unittest.TestCase):
    def test_checked_in_freeze_is_deterministic_and_outcome_locked(self):
        path = Path("docs/evidence/HOLY_GRAIL_PRIMARY_FREEZE_V0_1.json")
        self.assertEqual(build_payload(), json.loads(path.read_text(encoding="utf-8")))
        payload = build_payload()
        self.assertEqual("ALL_CANONICAL_PRODUCTS_UNIFORM_SCOPE", payload["scope_rule"])
        self.assertEqual([], payload["outcome_tested_alternatives"])
        self.assertEqual("NO", payload["candidate_outcome_data_used"])
        self.assertEqual("NO", payload["outcome_test_registered"])
