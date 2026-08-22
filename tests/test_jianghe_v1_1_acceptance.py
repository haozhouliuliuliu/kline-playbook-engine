#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Repository-only acceptance checks for Jianghe exhaustive second pass V1.1.

No media, network, ASR engine, ffmpeg, outcome data, or private local paths are
required. These checks only verify the durable text/evidence package and its
fail-closed research boundaries.
"""
from __future__ import annotations

import csv
import io
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JH = ROOT / "docs" / "research" / "jianghe"
SALVAGE = JH / "second_pass_salvage"


def _concat_text(paths: list[Path]) -> str:
    return "".join(path.read_text(encoding="utf-8") for path in paths)


def _seconds(value: str) -> int:
    hours, minutes, seconds = [int(part) for part in value.split(":" )]
    return hours * 3600 + minutes * 60 + seconds


class JiangheV11AcceptanceTests(unittest.TestCase):
    def test_coverage_record_is_complete_and_fail_closed(self):
        parts = sorted(SALVAGE.glob("JIANGHE_SECOND_PASS_SOURCE_COVERAGE_RECORD_V1_1.part*.csv"))
        self.assertEqual(len(parts), 4)
        rows = list(csv.DictReader(io.StringIO(_concat_text(parts))))
        self.assertEqual(len(rows), 99)
        self.assertEqual([row["source_ordinal"] for row in rows], [f"{number:03d}" for number in range(1, 100)])
        self.assertEqual(len({row["bvid"] for row in rows}), 99)

        by_ordinal = {row["source_ordinal"]: row for row in rows}
        self.assertIn("PAID", by_ordinal["022"]["access_status"])
        accessible = [row for row in rows if row["source_ordinal"] != "022"]
        self.assertEqual(len(accessible), 98)
        self.assertTrue(all(row["timeline_coverage"] == "FULL_TIMELINE_REVIEWED_0_TO_END" for row in accessible))
        self.assertTrue(all(float(row["unaccounted_timeline_gap_seconds"]) == 0 for row in accessible))
        self.assertTrue(all(row["tool_decision"] == "USE_EXISTING" for row in rows))

    def test_second_pass_claim_delta_has_64_unique_bounded_claims(self):
        parts = sorted(SALVAGE.glob("JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part*.jsonl"))
        self.assertEqual(len(parts), 4)
        claims = [json.loads(line) for line in _concat_text(parts).splitlines() if line.strip()]
        self.assertEqual(len(claims), 64)
        self.assertEqual(len({claim["claim_id"] for claim in claims}), 64)

        allowed_ordinals = {f"{number:03d}" for number in range(1, 100)}
        for claim in claims:
            self.assertIn(claim["source_ordinal"], allowed_ordinals)
            self.assertFalse(claim["source_only_verified"])
            self.assertFalse(claim["primary_eligible"])
            self.assertLessEqual(_seconds(claim["source_timestamp_start"]), _seconds(claim["source_timestamp_end"]))
            self.assertNotEqual(claim["review_status"], "UNREVIEWED")

    def test_case_delta_contains_exactly_nine_recovered_or_expanded_cases(self):
        text = (JH / "JIANGHE_SECOND_PASS_CASE_LIBRARY_DELTA_V1_1.md").read_text(encoding="utf-8")
        case_ids = re.findall(r"^## (JH-CASE-[A-Z0-9-]+)", text, flags=re.MULTILINE)
        self.assertEqual(len(case_ids), 9)
        self.assertEqual(len(set(case_ids)), 9)

    def test_dossier_keeps_exact_fourteen_sections(self):
        text = (JH / "JIANGHE_TRADER_DOSSIER_V1_1.md").read_text(encoding="utf-8")
        sections = re.findall(r"^## (\d+)\.", text, flags=re.MULTILINE)
        self.assertEqual(sections, [str(number) for number in range(1, 15)])

    def test_family_state_is_a_through_d_only(self):
        text = (JH / "JIANGHE_STRATEGY_FAMILIES_V1_1.md").read_text(encoding="utf-8")
        family_ids = re.findall(r"^## (JH-FAMILY-[A-Z])", text, flags=re.MULTILINE)
        self.assertEqual(family_ids, ["JH-FAMILY-A", "JH-FAMILY-B", "JH-FAMILY-C", "JH-FAMILY-D"])
        self.assertNotIn("JH-FAMILY-E", text)

    def test_unknown_and_contradiction_registers_remain_fail_closed(self):
        unknown = (JH / "JIANGHE_UNKNOWN_REGISTER_V1_1.md").read_text(encoding="utf-8")
        contradiction = (JH / "JIANGHE_CONTRADICTION_REGISTER_V1_1.md").read_text(encoding="utf-8")
        self.assertIn("JH-UNK-047", unknown)
        self.assertIn("FAIL-CLOSED / NOT USED", unknown)
        self.assertIn("JH-UNK-048", unknown)
        self.assertIn("ENGINEERING OPEN, NOT A SEMANTIC BLOCKER", unknown)
        self.assertRegex(contradiction, r"Open contradiction count\s*\n\n`0`")

    def test_current_view_and_verification_do_not_unlock_outcomes(self):
        current_view = (JH / "JIANGHE_CURRENT_VIEW_V1_1.md").read_text(encoding="utf-8")
        verification = (JH / "JIANGHE_SECOND_PASS_VERIFICATION_REPORT_V1_1.md").read_text(encoding="utf-8")
        combined = current_view + "\n" + verification
        required = (
            "FULL_TIMELINE_SECOND_PASS_AVAILABLE_MEDIA=98",
            "UNACCOUNTED_TIMELINE_GAP=0",
            "SECOND_PASS_UNDEREXTRACTION_SOURCES=22",
            "SECOND_PASS_RECOVERED_CLAIMS=64",
            "SECOND_PASS_RECOVERED_CASES=9",
            "SOURCE_ONLY_VERIFIED=NO",
            "PRIMARY_ELIGIBLE=NO",
            "CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED",
            "REAL_MONEY=NOT_AUTHORIZED",
        )
        for value in required:
            self.assertIn(value, combined)

    def test_audit_is_closed_and_manifest_is_byte-honest(self):
        audit = (JH / "JIANGHE_SECOND_PASS_COVERAGE_AUDIT_V1_1.md").read_text(encoding="utf-8")
        manifest = (SALVAGE / "SECOND_PASS_SALVAGE_MANIFEST_V1_1.md").read_text(encoding="utf-8")
        integrity = (SALVAGE / "JIANGHE_SECOND_PASS_INTEGRITY_CHECK_V1_1.md").read_text(encoding="utf-8")
        self.assertIn("Status: CLOSED / SUPERSEDED BY EXHAUSTIVE SECOND-PASS COMPLETION", audit)
        self.assertIn("SECOND_PASS_SOURCE_COVERAGE_AUDIT=COMPLETE", audit)
        self.assertIn("REMOTE_GITHUB_RAW_BYTE_IDENTITY_TO_LOCAL = NOT_CLAIMED", manifest)
        self.assertIn("PASS_WITH_NEWLINE_NORMALIZATION_QUALIFICATION", integrity)


if __name__ == "__main__":
    unittest.main()
