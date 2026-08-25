from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
import json
from pathlib import Path
import unittest

from src.jianghe_downloaded_kline_pilot import PILOT_ID, identity, reconstruct_sample, verify_plan


class DownloadedKlinePilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.root = root
        cls.plan = json.loads((root / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_PLAN_V0_1.json").read_text(encoding="utf-8"))

    def test_frozen_plan_is_portably_verifiable(self) -> None:
        self.assertEqual(self.plan["pilot_plan_identity"], verify_plan(self.plan))
        self.assertEqual(PILOT_ID, self.plan["pilot_id"])

    def test_plan_has_five_unique_samples_and_products(self) -> None:
        samples = self.plan["samples"]
        self.assertEqual(5, len(samples))
        self.assertEqual(5, len({item["sample_id"] for item in samples}))
        self.assertEqual(5, len({item["product"] for item in samples}))

    def test_every_visible_bar_is_point_in_time(self) -> None:
        for sample in self.plan["samples"]:
            observation, _, _, _ = reconstruct_sample(sample)
            self.assertTrue(all(bar.available_at <= observation.identity.decision_time for bar in observation.bars))

    def test_post_decision_bar_fails_closed(self) -> None:
        sample = deepcopy(self.plan["samples"][0])
        decision = __import__("datetime").datetime.fromisoformat(sample["decision_time"])
        sample["visible_bars"][0]["available_at"] = (decision + timedelta(minutes=1)).isoformat()
        with self.assertRaisesRegex(ValueError, "post-decision"):
            reconstruct_sample(sample)

    def test_outcome_unlock_fails_closed(self) -> None:
        altered = deepcopy(self.plan)
        altered["outcome_access"] = "YES"
        with self.assertRaisesRegex(ValueError, "deny outcome"):
            verify_plan(altered)

    def test_materialized_summary_and_case_evidence_are_identity_bound_and_safe(self) -> None:
        summary = json.loads((self.root / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_SUMMARY_V0_1.json").read_text(encoding="utf-8"))
        declared = summary.pop("summary_evidence_identity")
        self.assertEqual(declared, identity(summary))
        self.assertEqual("REVIEW_BEFORE_EXPAND", summary["pilot_verdict"])
        self.assertEqual(5, summary["scoreable_count"])
        self.assertEqual(2, summary["total_factual_errors"])
        for case in summary["cases"]:
            filename = f"JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_{case['sample_id'].replace('-', '_')}_V0_1.json"
            text = (self.root / "docs/evidence" / filename).read_text(encoding="utf-8")
            self.assertNotIn('"reasoning_content"', text)
            self.assertNotIn('"reasoning_details"', text)
            payload = json.loads(text)
            declared_case = payload.pop("case_evidence_identity")
            self.assertEqual(declared_case, identity(payload))


if __name__ == "__main__":
    unittest.main()
