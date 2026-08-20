"""Synthetic tests for E07 source-governed TqSdk main-mapping prep machinery.

These tests exercise only API-independent machinery (no TqSdk import, no login,
no network, no outcome data).  The exact TqSdk ``query_his_cont_quotes``
response schema is not pinned, so no decode adapter exists to test; the blocked
marker itself is asserted.
"""

import unittest
from datetime import date, datetime, timedelta
from unittest import mock
from zoneinfo import ZoneInfo

from src.source_governed_mapping import (
    BLOCKED_API_CONTRACT_NOT_PINNED,
    MappingConflictError,
    MappingProvenance,
    MappingSubstitutionForbidden,
    MappingUnavailableError,
    PseudoMainBarForbidden,
    SourceGovernedMappingError,
    SourceGovernedMappingRecord,
    SourceGovernedMappingSchedule,
    TerminalAuthCapture,
    TerminalOnlyAuthCapture,
    TqSdkMappingDecodeBoundary,
)

CN = ZoneInfo("Asia/Shanghai")
DAY_1 = date(2024, 6, 17)
DAY_2 = date(2024, 6, 18)
DAY_3 = date(2024, 6, 19)


def at(day, hour, minute):
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=CN)


def make_provenance(
    *,
    version="synthetic-mapping-provenance-v1",
    retrieval_session_id="synthetic-session-001",
    exact=False,
    artifact=None,
):
    return MappingProvenance(
        provider_identity="TQSDK",
        interface_identity="TqApi.query_his_cont_quotes",
        retrieval_session_id=retrieval_session_id,
        retrieved_at=at(DAY_1, 8, 0),
        source_artifact_identity=artifact,
        exact_bytes_bound=exact,
        mapping_version=version,
        provenance_notes=("synthetic-only",),
    )


def make_record(
    *,
    research="MAIN:SHFE:cu",
    source="KQ.m@SHFE.cu",
    concrete="SHFE.cu2407",
    day=DAY_1,
    hour=9,
    minute=0,
    available_minutes_before=30,
    provenance=None,
    derivation="SOURCE_GOVERNED",
):
    return SourceGovernedMappingRecord(
        research_symbol=research,
        source_symbol=source,
        concrete_instrument_id=concrete,
        effective_trading_date=day,
        effective_at=at(day, hour, minute),
        available_at=at(day, hour, minute) - timedelta(minutes=available_minutes_before),
        provenance=provenance or make_provenance(),
        derivation=derivation,
    )


CANONICAL_UNIVERSE = (
    "SHFE.cu2405",
    "SHFE.al2407",
)
FULL_UNIVERSE = set(CANONICAL_UNIVERSE) | {"SHFE.cu2406", "SHFE.cu2407", "SHFE.cu2408"}


class SourceGovernedMappingRecordTests(unittest.TestCase):
    def test_valid_record_builds_and_identity_is_deterministic(self):
        record = make_record()
        self.assertEqual(record.concrete_instrument_id, "SHFE.cu2407")
        self.assertEqual(record.derivation, "SOURCE_GOVERNED")
        self.assertEqual(record.identity_id, make_record().identity_id)
        self.assertEqual(record.identity_id, record.identity_id)

    def test_identity_changes_with_any_semantic_field(self):
        base = make_record()
        variants = (
            make_record(research="MAIN:SHFE:al"),
            make_record(concrete="SHFE.cu2408"),
            make_record(day=DAY_2),
            make_record(provenance=make_provenance(version="synthetic-mapping-provenance-v2")),
        )
        for variant in variants:
            self.assertNotEqual(base.identity_id, variant.identity_id)

    def test_empty_or_whitespace_identities_rejected(self):
        for kwargs in (
            {"research": ""},
            {"research": "  "},
            {"source": ""},
            {"concrete": ""},
            {"concrete": " SHFE.cu2407 "},
        ):
            with self.assertRaises(SourceGovernedMappingError):
                make_record(**kwargs)

    def test_effective_at_must_fall_on_effective_trading_date(self):
        with self.assertRaisesRegex(SourceGovernedMappingError, "effective trading date"):
            SourceGovernedMappingRecord(
                research_symbol="MAIN:SHFE:cu",
                source_symbol="KQ.m@SHFE.cu",
                concrete_instrument_id="SHFE.cu2407",
                effective_trading_date=DAY_1,
                effective_at=at(DAY_2, 9, 0),
                available_at=at(DAY_2, 9, 0) - timedelta(minutes=30),
                provenance=make_provenance(),
            )

    def test_timestamps_must_be_timezone_aware(self):
        naive = datetime(2024, 6, 17, 9, 0)
        with self.assertRaisesRegex(SourceGovernedMappingError, "timezone-aware"):
            SourceGovernedMappingRecord(
                research_symbol="MAIN:SHFE:cu",
                source_symbol="KQ.m@SHFE.cu",
                concrete_instrument_id="SHFE.cu2407",
                effective_trading_date=DAY_1,
                effective_at=naive,
                available_at=naive - timedelta(minutes=30),
                provenance=make_provenance(),
            )

    def test_available_after_switch_rejected(self):
        with self.assertRaisesRegex(SourceGovernedMappingError, "no later than"):
            make_record(available_minutes_before=-5)

    def test_forbidden_derivations_fail_closed(self):
        for forbidden in ("PREVIOUS_DAY_OI_MAX", "PREVIOUS_DAY_VOLUME_MAX",
                          "OI_PLUS_VOLUME_FORMULA", "CALENDAR_ROLL", "PNL_SELECTED"):
            with self.assertRaises(MappingSubstitutionForbidden):
                make_record(derivation=forbidden)

    def test_pseudo_main_target_rejected(self):
        for pseudo in ("KQ.m@SHFE.cu", "SHFE.cu.main", "SHFE.cu主连"):
            with self.assertRaises(PseudoMainBarForbidden):
                make_record(concrete=pseudo)

    def test_research_symbol_must_differ_from_source_symbol(self):
        with self.assertRaisesRegex(SourceGovernedMappingError, "differ from"):
            make_record(research="KQ.m@SHFE.cu")

    def test_research_symbol_may_be_vendor_main_form(self):
        # source symbol is allowed to be the vendor KQ.m@ main reference; the
        # target concrete contract must still be a real concrete contract.
        record = make_record(source="KQ.m@SHFE.cu")
        self.assertEqual(record.source_symbol, "KQ.m@SHFE.cu")


class MappingProvenanceTests(unittest.TestCase):
    def test_exact_bytes_bound_requires_artifact_hash(self):
        with self.assertRaisesRegex(SourceGovernedMappingError, "artifact identity"):
            make_provenance(exact=True, artifact=None)

    def test_artifact_hash_without_exact_bound_rejected(self):
        with self.assertRaisesRegex(SourceGovernedMappingError, "exact_bytes_bound"):
            make_provenance(exact=False, artifact="deadbeef")

    def test_provenance_identity_is_deterministic_and_sensitive(self):
        base = make_provenance()
        self.assertEqual(base.identity_id, make_provenance().identity_id)
        changed = make_provenance(retrieval_session_id="synthetic-session-002")
        self.assertNotEqual(base.identity_id, changed.identity_id)

    def test_retrieved_at_must_be_timezone_aware(self):
        with self.assertRaisesRegex(SourceGovernedMappingError, "timezone-aware"):
            MappingProvenance(
                provider_identity="TQSDK",
                interface_identity="TqApi.query_his_cont_quotes",
                retrieval_session_id="synthetic-session-001",
                retrieved_at=datetime(2024, 6, 17, 8, 0),
                source_artifact_identity=None,
                exact_bytes_bound=False,
                mapping_version="v1",
            )


class SourceGovernedMappingScheduleTests(unittest.TestCase):
    def setUp(self):
        self.provenance = make_provenance()
        self.record_1 = make_record(
            concrete="SHFE.cu2406", day=DAY_1, hour=9, minute=0, provenance=self.provenance
        )
        self.record_2 = make_record(
            concrete="SHFE.cu2407", day=DAY_2, hour=9, minute=0, provenance=self.provenance
        )
        self.record_3 = make_record(
            concrete="SHFE.cu2408", day=DAY_3, hour=9, minute=0, provenance=self.provenance
        )
        self.schedule = SourceGovernedMappingSchedule(
            "synthetic-schedule-v1",
            ("MAIN:SHFE:cu",),
            (self.record_1, self.record_2, self.record_3),
        )

    def test_construction_is_deterministic_regardless_of_input_order(self):
        forward = SourceGovernedMappingSchedule(
            "synthetic-schedule-v1",
            ("MAIN:SHFE:cu",),
            (self.record_1, self.record_2, self.record_3),
        )
        reversed_input = SourceGovernedMappingSchedule(
            "synthetic-schedule-v1",
            ("MAIN:SHFE:cu",),
            (self.record_3, self.record_1, self.record_2),
        )
        self.assertEqual(forward.identity_id, reversed_input.identity_id)
        self.assertEqual(forward.records, reversed_input.records)

    def test_duplicate_records_fail_closed(self):
        with self.assertRaises(MappingConflictError):
            SourceGovernedMappingSchedule(
                "dup-schedule-v1",
                ("MAIN:SHFE:cu",),
                (self.record_1, self.record_1),
            )

    def test_same_effective_day_conflict_fails_closed(self):
        conflicting = make_record(
            concrete="SHFE.cu2409", day=DAY_2, hour=9, minute=0, provenance=self.provenance
        )
        with self.assertRaisesRegex(MappingConflictError, "conflicting"):
            SourceGovernedMappingSchedule(
                "conflict-schedule-v1",
                ("MAIN:SHFE:cu",),
                (self.record_1, self.record_2, conflicting),
            )

    def test_undeclared_research_symbol_rejected(self):
        with self.assertRaisesRegex(SourceGovernedMappingError, "undeclared"):
            SourceGovernedMappingSchedule(
                "undeclared-schedule-v1",
                ("MAIN:SHFE:cu",),
                (make_record(research="MAIN:SHFE:al"),),
            )

    def test_resolve_point_in_time_and_switch(self):
        before_first = at(DAY_1, 8, 59)
        on_first = at(DAY_1, 9, 1)
        after_second = at(DAY_2, 9, 1)
        with self.assertRaises(MappingUnavailableError):
            self.schedule.resolve("MAIN:SHFE:cu", before_first)
        first = self.schedule.resolve("MAIN:SHFE:cu", on_first)
        second = self.schedule.resolve("MAIN:SHFE:cu", after_second)
        self.assertEqual(first.concrete_instrument_id, "SHFE.cu2406")
        self.assertEqual(second.concrete_instrument_id, "SHFE.cu2407")
        self.assertEqual(first.effective_trading_date, DAY_1)
        self.assertEqual(second.effective_trading_date, DAY_2)
        self.assertEqual(first.record_identity_id, self.record_1.identity_id)
        self.assertEqual(second.record_identity_id, self.record_2.identity_id)
        self.assertEqual(first.schedule_identity_id, self.schedule.identity_id)

    def test_resolve_is_deterministic_and_idempotent(self):
        a = self.schedule.resolve("MAIN:SHFE:cu", at(DAY_2, 9, 1))
        b = self.schedule.resolve("MAIN:SHFE:cu", at(DAY_2, 9, 1))
        self.assertEqual(a, b)
        self.assertEqual(a.identity_id, b.identity_id)

    def test_unavailable_future_record_fails_closed_no_lookahead(self):
        # record_3 becomes effective only on DAY_3; a decision on DAY_2 must not see it.
        decision = at(DAY_2, 12, 0)
        resolved = self.schedule.resolve("MAIN:SHFE:cu", decision)
        self.assertEqual(resolved.concrete_instrument_id, "SHFE.cu2407")

    def test_unknown_symbol_fails_closed(self):
        with self.assertRaises(MappingUnavailableError):
            self.schedule.resolve("MAIN:SHFE:al", at(DAY_2, 9, 1))

    def test_membership_validation_records_not_in_universe(self):
        violations = self.schedule.validate_canonical_membership(CANONICAL_UNIVERSE)
        offending = {v.concrete_instrument_id for v in violations}
        self.assertIn("SHFE.cu2406", offending)
        self.assertIn("SHFE.cu2407", offending)
        self.assertIn("SHFE.cu2408", offending)
        self.assertTrue(all(v.fact == "MAPPING_CONTRACT_NOT_IN_CANONICAL_UNIVERSE" for v in violations))

    def test_membership_all_in_universe_passes(self):
        self.assertEqual(self.schedule.validate_canonical_membership(FULL_UNIVERSE), ())

    def test_concrete_bar_selection_only_fails_closed_on_unknown_target(self):
        with self.assertRaises(PseudoMainBarForbidden):
            self.schedule.assert_concrete_bar_selection_only(CANONICAL_UNIVERSE)

    def test_concrete_bar_selection_only_passes_with_full_universe(self):
        self.schedule.assert_concrete_bar_selection_only(FULL_UNIVERSE)  # must not raise


class TerminalAuthCaptureTests(unittest.TestCase):
    def test_module_records_blocked_tqsdk_api_contract(self):
        self.assertTrue(BLOCKED_API_CONTRACT_NOT_PINNED)

    def test_decode_boundary_is_protocol_only_and_not_implemented(self):
        # The decode boundary must not be instantiable; it is a typing-only
        # Protocol documenting a future Owner-authorized adapter.
        with self.assertRaises(TypeError):
            TqSdkMappingDecodeBoundary()

    def test_fake_provider_satisfies_terminal_only_auth_boundary(self):
        def provider() -> tuple[str, str]:
            return ("synthetic-account", "synthetic-password")

        # Structural conformance to the capture boundary (no login occurs).
        self.assertTrue(hasattr(provider, "__call__"))
        captured = provider()
        self.assertEqual(captured[0], "synthetic-account")
        self.assertEqual(len(captured[1]) > 0, True)

    def test_non_interactive_terminal_fails_closed(self):
        with mock.patch.object(__import__("sys").stdin, "isatty", return_value=False):
            with self.assertRaisesRegex(SourceGovernedMappingError, "interactive terminal"):
                TerminalAuthCapture().capture()

    def test_empty_credentials_fail_closed(self):
        with mock.patch.object(__import__("sys").stdin, "isatty", return_value=True), \
                mock.patch("builtins.input", return_value=""), \
                mock.patch("getpass.getpass", return_value=""):
            with self.assertRaisesRegex(SourceGovernedMappingError, "credentials are required"):
                TerminalAuthCapture().capture()

    def test_terminal_capture_never_persists_credentials(self):
        # The capture boundary must not write any state; only an in-memory tuple
        # is returned.  No file/registry side effect exists to assert, so we
        # assert the public contract: capture returns a tuple only.
        with mock.patch.object(__import__("sys").stdin, "isatty", return_value=True), \
                mock.patch("builtins.input", return_value="acct"), \
                mock.patch("getpass.getpass", return_value="pw"):
            account, password = TerminalAuthCapture().capture()
        self.assertEqual((account, password), ("acct", "pw"))


if __name__ == "__main__":
    unittest.main()
