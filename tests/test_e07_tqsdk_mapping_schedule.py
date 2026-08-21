"""Regression checks for the authenticated E07 mapping capture transformation."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.build_e07_tqsdk_mapping_schedule import build_payload


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "docs" / "evidence" / "E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json"


class E07TqSdkMappingScheduleTests(unittest.TestCase):
    def test_checked_in_schedule_is_deterministic_and_mapping_only(self):
        payload = build_payload()
        self.assertEqual(payload, json.loads(ARTIFACT.read_text(encoding="utf-8")))
        self.assertEqual(105, payload["record_count"])
        self.assertEqual([], payload["canonical_membership_violations"])
        self.assertEqual("NO", payload["price_data_used"])
        self.assertEqual("NO", payload["candidate_outcome_data_used"])
        self.assertEqual(
            "331ba31e2a03695160aff28f7c7c58888dcc9bc091515e176c8d5c6b66edcb5c",
            payload["schedule_identity"],
        )


if __name__ == "__main__":
    unittest.main()
