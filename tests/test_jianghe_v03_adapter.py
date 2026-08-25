"""Format-only V0.3 capability adapter adversarial tests.

The adapter may only change representation. It must never make the model smarter:
no WAIT->ENTER, no guessing direction/family/action, no principle completion, no
truncation repair, no contradiction resolution, no invented-value invention.
"""

from __future__ import annotations

import unittest

from src.jianghe_v03_runtime import (
    V03CapabilityAdapter,
    unwrap_markdown_json,
)

ADAPTER = V03CapabilityAdapter()

FULL_ANSWER = """MARKET_INTERPRETATION:
Range-bound with an upper-boundary poke.

FAMILY:
NONE

SETUP_OR_NO_SETUP:
No setup.

ACTION:
WAIT

DIRECTION_IF_APPLICABLE:
NONE

EVIDENCE:
Close back inside the prior range.

INVALIDATION_OR_UNCERTAINTY:
A sustained close above 102 invalidates.

JIANGHE_PRINCIPLES_USED:
UNKNOWN register; no-trade guard.

VISUAL_OBSERVATIONS:
Poke wick at upper boundary.

STRUCTURED_OBSERVATIONS:
No follow-through.

CONTRADICTIONS:
NONE

DECLARED_UNKNOWN:
NONE
"""


class AdapterAdversarialTests(unittest.TestCase):
    def test_wait_never_becomes_enter(self) -> None:
        answer = ADAPTER.adapt(FULL_ANSWER)
        self.assertEqual("WAIT", answer.action)
        self.assertNotEqual("ENTER", answer.action)

    def test_unknown_direction_never_guesses_long_short(self) -> None:
        raw = FULL_ANSWER.replace("DIRECTION_IF_APPLICABLE:\nNONE", "DIRECTION_IF_APPLICABLE:\nUNKNOWN")
        answer = ADAPTER.adapt(raw)
        self.assertEqual("UNKNOWN", answer.direction)
        self.assertNotIn("LONG", (answer.direction,))
        self.assertNotIn("SHORT", (answer.direction,))

    def test_missing_family_never_inferred_from_prose(self) -> None:
        raw = FULL_ANSWER.replace("FAMILY:\nNONE\n\n", "")
        answer = ADAPTER.adapt(raw)
        self.assertIsNone(answer.family)
        self.assertIn("FAMILY", answer.missing_headings)

    def test_missing_principle_never_completed(self) -> None:
        raw = FULL_ANSWER.replace("JIANGHE_PRINCIPLES_USED:\nUNKNOWN register; no-trade guard.\n\n", "")
        answer = ADAPTER.adapt(raw)
        self.assertIn("JIANGHE_PRINCIPLES_USED", answer.missing_headings)
        self.assertNotIn("no-trade guard", str(answer.headings.values()))

    def test_markdown_wrapped_json_only_unwrapped(self) -> None:
        inner = '{"market_interpretation": "range", "action": "WAIT"}'
        wrapped = f"```json\n{inner}\n```"
        self.assertEqual(inner, unwrap_markdown_json(wrapped))
        answer = ADAPTER.adapt(wrapped)
        # Unwrapping is representation-only: headed extraction finds no headings.
        self.assertIn("MARKET_INTERPRETATION", answer.missing_headings)

    def test_headed_plain_text_extracts_exact_headings(self) -> None:
        answer = ADAPTER.adapt(FULL_ANSWER)
        self.assertEqual("Range-bound with an upper-boundary poke.", answer.headings["MARKET_INTERPRETATION"])
        self.assertEqual("NONE", answer.family)
        self.assertEqual("WAIT", answer.action)
        self.assertEqual((), answer.missing_headings)

    def test_contradiction_never_resolved_by_adapter(self) -> None:
        raw = FULL_ANSWER.replace(
            "MARKET_INTERPRETATION:\nRange-bound with an upper-boundary poke.",
            "MARKET_INTERPRETATION:\nStrong bullish breakout with follow-through.",
        )
        answer = ADAPTER.adapt(raw)
        self.assertEqual("WAIT", answer.action)
        self.assertIn("Strong bullish breakout", answer.headings["MARKET_INTERPRETATION"])

    def test_truncated_answer_never_completed(self) -> None:
        raw = "MARKET_INTERPRETATION:\nRange-bound.\n\nFAMILY:\nNONE\n\nACTION:\n"
        answer = ADAPTER.adapt(raw, truncated=True)
        self.assertTrue(answer.truncated)
        self.assertFalse(answer.scoreable)
        self.assertIsNone(answer.action)

    def test_invented_threshold_preserved_verbatim(self) -> None:
        raw = FULL_ANSWER.replace(
            "EVIDENCE:\nClose back inside the prior range.",
            "EVIDENCE:\n突破 103.5 则买入；跌破 99.0 则离场。",
        )
        answer = ADAPTER.adapt(raw)
        self.assertIn("突破 103.5 则买入；跌破 99.0 则离场。", answer.headings["EVIDENCE"])

    def test_cannot_judge_not_forced_to_family_or_action(self) -> None:
        raw = FULL_ANSWER.replace("FAMILY:\nNONE", "FAMILY:\n无法判断")
        raw = raw.replace("ACTION:\nWAIT", "ACTION:\n无法判断")
        answer = ADAPTER.adapt(raw)
        self.assertIsNone(answer.family)
        self.assertIsNone(answer.action)
        self.assertFalse(answer.scoreable)

    def test_duplicate_headings_marked_duplicate(self) -> None:
        raw = FULL_ANSWER.replace(
            "FAMILY:\nNONE",
            "FAMILY:\nNONE\nFAMILY:\nA",
        )
        answer = ADAPTER.adapt(raw)
        self.assertIn("FAMILY", answer.duplicate_headings)

    def test_missing_headings_marked_missing(self) -> None:
        raw = "MARKET_INTERPRETATION:\nOnly this heading.\n"
        answer = ADAPTER.adapt(raw)
        self.assertNotIn("MARKET_INTERPRETATION", answer.missing_headings)
        self.assertIn("FAMILY", answer.missing_headings)
        self.assertIn("ACTION", answer.missing_headings)
        self.assertIn("EVIDENCE", answer.missing_headings)

    def test_scoreable_requires_complete_core_semantics(self) -> None:
        self.assertTrue(ADAPTER.adapt(FULL_ANSWER).scoreable)
        invalid = FULL_ANSWER.replace("ACTION:\nWAIT", "ACTION:\nBUY_NOW")
        self.assertFalse(ADAPTER.adapt(invalid).scoreable)
        missing = FULL_ANSWER.replace("EVIDENCE:\nClose back inside the prior range.\n\n", "")
        self.assertFalse(ADAPTER.adapt(missing).scoreable)


if __name__ == "__main__":
    unittest.main()
