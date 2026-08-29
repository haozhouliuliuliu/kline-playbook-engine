"""Focused tests for the source-neutral contract-facts runtime store.

All numeric values in this file are synthetic FIXTURE-ONLY numbers for tests.
They are NOT production defaults and NOT permanent risk rules.
"""

import inspect
import re
import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.contract_facts import (
    FactCategory,
    FactFreshness,
    FactSourceType,
    FeeModel,
    MarginBasis,
    MarginFacts,
    SourceProvenance,
    ContractFacts,
    ContractIdentity,
    current_use_eligibility,
)
from src.contract_facts_runtime import (
    SnapshotRecordReasonCode,
    SnapshotRecordStatus,
    SnapshotReasonCode,
    SnapshotStatus,
    ContractFactsSnapshot,
    ContractFactsStore,
    make_snapshot,
)

FIXTURE_ONLY = True

_UNSET = object()

BEFORE = datetime(2026, 1, 14, 3, 30, 0, tzinfo=timezone.utc)
NOW = datetime(2026, 1, 15, 3, 30, 0, tzinfo=timezone.utc)
LATER = datetime(2026, 1, 15, 4, 30, 0, tzinfo=timezone.utc)
T_AFTER = datetime(2026, 1, 16, 3, 30, 0, tzinfo=timezone.utc)
EXPIRY = datetime(2026, 1, 15, 10, 0, 0, tzinfo=timezone.utc)


def _source(source_type=FactSourceType.EXCHANGE_OFFICIAL, retrieved_at=NOW):
    return SourceProvenance(
        source_identity="fixture-source-rb-v0",
        source_type=source_type,
        retrieved_at=retrieved_at,
        source_version="fixture-v0",
        notes="synthetic fixture source",
    )


def _identity(instrument_id="RB2605"):
    return ContractIdentity(exchange="SHFE", product_family="RB", instrument_id=instrument_id)


def _fixture_margin():
    return MarginFacts(basis=MarginBasis.PER_LOT_AMOUNT, initial_margin_per_lot=Decimal("4500"))


def _fixture_fee():
    return FeeModel(commission_per_lot=Decimal("5"))


def _complete_facts(
    *,
    instrument_id="RB2605",
    reference_price=Decimal("3000"),
    margin=_UNSET,
    fee=_UNSET,
    freshness=FactFreshness.CURRENT,
    is_historical_only=False,
    source_type=FactSourceType.EXCHANGE_OFFICIAL,
    observed_at=NOW,
):
    if margin is _UNSET:
        margin = _fixture_margin()
    if fee is _UNSET:
        fee = _fixture_fee()
    return ContractFacts(
        identity=_identity(instrument_id),
        multiplier=Decimal("10"),
        tick_size=Decimal("1"),
        tick_unit="yuan/ton",
        currency="CNY",
        observed_at=observed_at,
        source=_source(source_type, retrieved_at=observed_at),
        category=FactCategory.EXCHANGE_BROKER_FACT,
        freshness=freshness,
        reference_price=reference_price,
        margin=margin,
        fee=fee,
        is_historical_only=is_historical_only,
    )


class SnapshotIdentityTests(unittest.TestCase):
    def test_snapshot_id_is_deterministic_sha256(self):
        snap1 = make_snapshot(_complete_facts(), recorded_at=NOW)
        snap2 = make_snapshot(_complete_facts(), recorded_at=NOW)
        self.assertEqual(snap1.snapshot_id, snap2.snapshot_id)
        self.assertRegex(snap1.snapshot_id, r"^[0-9a-f]{64}$")

    def test_snapshot_id_changes_when_fact_value_changes(self):
        snap1 = make_snapshot(_complete_facts(), recorded_at=NOW)
        snap2 = make_snapshot(_complete_facts(reference_price=Decimal("3100")), recorded_at=NOW)
        self.assertNotEqual(snap1.snapshot_id, snap2.snapshot_id)

    def test_snapshot_id_changes_when_metadata_changes(self):
        snap1 = make_snapshot(_complete_facts(), recorded_at=NOW)
        snap2 = make_snapshot(_complete_facts(), recorded_at=LATER)
        self.assertNotEqual(snap1.snapshot_id, snap2.snapshot_id)

    def test_snapshot_id_changes_when_source_identity_changes(self):
        facts1 = _complete_facts()
        facts2 = ContractFacts(
            identity=facts1.identity,
            multiplier=facts1.multiplier,
            tick_size=facts1.tick_size,
            tick_unit=facts1.tick_unit,
            currency=facts1.currency,
            observed_at=facts1.observed_at,
            source=SourceProvenance(
                source_identity="fixture-source-rb-v1",
                source_type=FactSourceType.EXCHANGE_OFFICIAL,
                retrieved_at=NOW,
                source_version="fixture-v0",
                notes="synthetic fixture source",
            ),
            category=facts1.category,
            freshness=facts1.freshness,
            reference_price=facts1.reference_price,
            margin=facts1.margin,
            fee=facts1.fee,
        )
        self.assertNotEqual(
            make_snapshot(facts1, recorded_at=NOW).snapshot_id,
            make_snapshot(facts2, recorded_at=NOW).snapshot_id,
        )

    def test_completeness_derived_from_facts(self):
        complete = make_snapshot(_complete_facts(), recorded_at=NOW)
        self.assertTrue(complete.is_complete)
        self.assertEqual(complete.missing_facts, ())

        no_margin = make_snapshot(_complete_facts(margin=None), recorded_at=NOW)
        self.assertFalse(no_margin.is_complete)
        self.assertIn("margin", no_margin.missing_facts)

        no_fee = make_snapshot(_complete_facts(fee=None), recorded_at=NOW)
        self.assertFalse(no_fee.is_complete)
        self.assertIn("fee", no_fee.missing_facts)

    def test_completeness_tamper_guard_rejected(self):
        snap = make_snapshot(_complete_facts(), recorded_at=NOW)
        with self.assertRaises(ValueError):
            ContractFactsSnapshot(
                facts=snap.facts,
                recorded_at=NOW,
                expires_at=None,
                is_complete=True,
                missing_facts=("fee",),
                session_identity=None,
                trading_day=None,
                query_identity=None,
            )

    def test_snapshot_exposes_required_timestamps(self):
        snap = make_snapshot(_complete_facts(), recorded_at=NOW)
        self.assertEqual(snap.observed_at, NOW)
        self.assertEqual(snap.retrieved_at, NOW)
        self.assertEqual(snap.effective_at, None)


class StoreSelectionTests(unittest.TestCase):
    def test_complete_current_snapshot_is_eligible(self):
        store = ContractFactsStore()
        snap = make_snapshot(_complete_facts(), recorded_at=NOW)
        outcome = store.record(snap)
        self.assertEqual(outcome.status, SnapshotRecordStatus.STORED)
        result = store.query(_identity(), T_AFTER)
        self.assertEqual(result.status, SnapshotStatus.CURRENT)
        self.assertEqual(result.reason_code, SnapshotReasonCode.ELIGIBLE)
        self.assertIs(result.snapshot, snap)
        self.assertEqual(result.eligibility_reason, "CURRENT")
        ok, _ = current_use_eligibility(result.snapshot.facts)
        self.assertTrue(ok)

    def test_stale_snapshot_cannot_masquerade_current(self):
        store = ContractFactsStore()
        store.record(make_snapshot(_complete_facts(freshness=FactFreshness.STALE), recorded_at=NOW))
        result = store.query(_identity(), T_AFTER)
        self.assertEqual(result.status, SnapshotStatus.STALE)
        self.assertEqual(result.reason_code, SnapshotReasonCode.SNAPSHOT_STALE)
        self.assertIsNotNone(result.snapshot)

    def test_unknown_freshness_cannot_masquerade_current(self):
        store = ContractFactsStore()
        store.record(make_snapshot(_complete_facts(freshness=FactFreshness.UNKNOWN), recorded_at=NOW))
        result = store.query(_identity(), T_AFTER)
        self.assertEqual(result.status, SnapshotStatus.UNKNOWN)
        self.assertEqual(result.reason_code, SnapshotReasonCode.SNAPSHOT_FRESHNESS_UNKNOWN)

    def test_incomplete_cannot_masquerade_current(self):
        store = ContractFactsStore()
        store.record(make_snapshot(_complete_facts(margin=None), recorded_at=NOW))
        result = store.query(_identity(), T_AFTER)
        self.assertEqual(result.status, SnapshotStatus.INCOMPLETE)
        self.assertEqual(result.reason_code, SnapshotReasonCode.SNAPSHOT_INCOMPLETE)
        self.assertIn("margin", result.missing_facts)
        self.assertNotEqual(result.status, SnapshotStatus.CURRENT)

    def test_incomplete_missing_reference_price_reported(self):
        store = ContractFactsStore()
        store.record(make_snapshot(_complete_facts(reference_price=None), recorded_at=NOW))
        result = store.query(_identity(), T_AFTER)
        self.assertEqual(result.status, SnapshotStatus.INCOMPLETE)
        self.assertIn("reference_price", result.missing_facts)

    def test_expired_snapshot_is_stale(self):
        store = ContractFactsStore()
        store.record(make_snapshot(_complete_facts(), recorded_at=NOW, expires_at=EXPIRY))
        before = store.query(_identity(), EXPIRY - timedelta(minutes=1))
        self.assertEqual(before.status, SnapshotStatus.CURRENT)
        at = store.query(_identity(), EXPIRY)
        self.assertEqual(at.status, SnapshotStatus.STALE)
        self.assertEqual(at.reason_code, SnapshotReasonCode.SNAPSHOT_EXPIRED)

    def test_no_snapshot_for_contract_is_insufficient(self):
        store = ContractFactsStore()
        result = store.query(_identity("RB2610"), T_AFTER)
        self.assertEqual(result.status, SnapshotStatus.INSUFFICIENT)
        self.assertEqual(result.reason_code, SnapshotReasonCode.NO_SNAPSHOT_FOR_CONTRACT)
        self.assertIsNone(result.snapshot)

    def test_exact_contract_query_is_isolated(self):
        store = ContractFactsStore()
        store.record(make_snapshot(_complete_facts(instrument_id="RB2605"), recorded_at=NOW))
        store.record(
            make_snapshot(
                _complete_facts(instrument_id="RB2610", reference_price=Decimal("3200")),
                recorded_at=NOW,
            )
        )
        result_a = store.query(_identity("RB2605"), T_AFTER)
        result_b = store.query(_identity("RB2610"), T_AFTER)
        self.assertEqual(result_a.snapshot.contract_identity.instrument_id, "RB2605")
        self.assertEqual(result_b.snapshot.contract_identity.instrument_id, "RB2610")
        self.assertEqual(result_a.snapshot.facts.reference_price, Decimal("3000"))
        self.assertEqual(result_b.snapshot.facts.reference_price, Decimal("3200"))

    def test_historical_source_never_current_broker_truth(self):
        store = ContractFactsStore()
        hist = make_snapshot(
            _complete_facts(
                freshness=FactFreshness.STALE,
                is_historical_only=True,
                source_type=FactSourceType.HISTORICAL_CANONICAL_METADATA,
            ),
            recorded_at=NOW,
        )
        outcome = store.record(hist)
        self.assertEqual(outcome.status, SnapshotRecordStatus.STORED_HISTORICAL)
        self.assertIsNone(store.current_snapshot(_identity()))
        self.assertEqual(len(store.historical_snapshots(_identity())), 1)
        result = store.query(_identity(), T_AFTER)
        self.assertEqual(result.status, SnapshotStatus.INSUFFICIENT)
        self.assertEqual(result.reason_code, SnapshotReasonCode.NO_SNAPSHOT_FOR_CONTRACT)

    def test_provenance_retained_through_selection(self):
        store = ContractFactsStore()
        snap = make_snapshot(_complete_facts(), recorded_at=NOW)
        store.record(snap)
        result = store.query(_identity(), T_AFTER)
        self.assertIsNotNone(result.provenance)
        self.assertEqual(result.provenance.source_identity, "fixture-source-rb-v0")
        self.assertIs(result.snapshot.provenance, result.provenance)

    def test_no_sourceless_latest_wins(self):
        store = ContractFactsStore()
        store.record(make_snapshot(_complete_facts(), recorded_at=NOW))
        result = store.query(_identity(), T_AFTER)
        self.assertIsNotNone(result.provenance)
        self.assertIsNotNone(result.snapshot.provenance)


class ReplacementPolicyTests(unittest.TestCase):
    def test_older_complete_rejected_does_not_replace(self):
        store = ContractFactsStore()
        first = make_snapshot(_complete_facts(), recorded_at=NOW)
        store.record(first)
        older = make_snapshot(_complete_facts(), recorded_at=BEFORE)
        outcome = store.record(older)
        self.assertEqual(outcome.status, SnapshotRecordStatus.REJECTED)
        self.assertEqual(outcome.reason_code, SnapshotRecordReasonCode.REJECTED_OLDER)
        self.assertIs(store.current_snapshot(_identity()), first)

    def test_incomplete_never_replaces_complete_current(self):
        store = ContractFactsStore()
        first = make_snapshot(_complete_facts(), recorded_at=NOW)
        store.record(first)
        incomplete = make_snapshot(_complete_facts(margin=None), recorded_at=LATER)
        outcome = store.record(incomplete)
        self.assertEqual(outcome.status, SnapshotRecordStatus.REJECTED)
        self.assertEqual(
            outcome.reason_code, SnapshotRecordReasonCode.REJECTED_INCOMPLETE_REPLACING_COMPLETE
        )
        self.assertIs(store.current_snapshot(_identity()), first)

    def test_lower_quality_stale_never_replaces_complete_current(self):
        store = ContractFactsStore()
        first = make_snapshot(_complete_facts(), recorded_at=NOW)
        store.record(first)
        stale = make_snapshot(_complete_facts(freshness=FactFreshness.STALE), recorded_at=LATER)
        outcome = store.record(stale)
        self.assertEqual(outcome.status, SnapshotRecordStatus.REJECTED)
        self.assertEqual(outcome.reason_code, SnapshotRecordReasonCode.REJECTED_LOWER_QUALITY)
        self.assertIs(store.current_snapshot(_identity()), first)

    def test_newer_complete_replaces_and_preserves_superseded(self):
        store = ContractFactsStore()
        first = make_snapshot(_complete_facts(reference_price=Decimal("3000")), recorded_at=NOW)
        store.record(first)
        newer = make_snapshot(_complete_facts(reference_price=Decimal("3100")), recorded_at=LATER)
        outcome = store.record(newer)
        self.assertEqual(outcome.status, SnapshotRecordStatus.REPLACED)
        self.assertEqual(
            outcome.reason_code, SnapshotRecordReasonCode.REPLACED_NEWER_COMPLETE_CURRENT
        )
        self.assertIs(store.current_snapshot(_identity()), newer)
        superseded = store.superseded_snapshots(_identity())
        self.assertEqual(len(superseded), 1)
        self.assertEqual(superseded[0].snapshot_id, first.snapshot_id)
        result = store.query(_identity(), T_AFTER)
        self.assertEqual(result.snapshot.facts.reference_price, Decimal("3100"))

    def test_upgrade_from_stale_to_current_replaces(self):
        store = ContractFactsStore()
        stale = make_snapshot(_complete_facts(freshness=FactFreshness.STALE), recorded_at=NOW)
        store.record(stale)
        current = make_snapshot(_complete_facts(), recorded_at=LATER)
        outcome = store.record(current)
        self.assertEqual(outcome.status, SnapshotRecordStatus.REPLACED)
        self.assertEqual(outcome.reason_code, SnapshotRecordReasonCode.REPLACED_UPGRADE)
        self.assertEqual(store.query(_identity(), T_AFTER).status, SnapshotStatus.CURRENT)

    def test_rejected_record_is_atomic(self):
        store = ContractFactsStore()
        first = make_snapshot(_complete_facts(), recorded_at=NOW)
        store.record(first)
        store.record(make_snapshot(_complete_facts(margin=None), recorded_at=LATER))
        result = store.query(_identity(), T_AFTER)
        self.assertEqual(result.status, SnapshotStatus.CURRENT)
        self.assertIs(result.snapshot, first)


class ScopingTests(unittest.TestCase):
    def test_session_identity_scoping(self):
        store = ContractFactsStore()
        snap = make_snapshot(_complete_facts(), recorded_at=NOW, session_identity="session-A")
        store.record(snap)
        match = store.query(_identity(), T_AFTER, session_identity="session-A")
        self.assertEqual(match.status, SnapshotStatus.CURRENT)
        mismatch = store.query(_identity(), T_AFTER, session_identity="session-B")
        self.assertEqual(mismatch.status, SnapshotStatus.INSUFFICIENT)
        self.assertEqual(mismatch.reason_code, SnapshotReasonCode.SESSION_IDENTITY_MISMATCH)

    def test_trading_day_scoping(self):
        store = ContractFactsStore()
        snap = make_snapshot(_complete_facts(), recorded_at=NOW, trading_day="2026-01-15")
        store.record(snap)
        self.assertEqual(
            store.query(_identity(), T_AFTER, trading_day="2026-01-15").status,
            SnapshotStatus.CURRENT,
        )
        mismatch = store.query(_identity(), T_AFTER, trading_day="2026-01-16")
        self.assertEqual(mismatch.status, SnapshotStatus.INSUFFICIENT)
        self.assertEqual(mismatch.reason_code, SnapshotReasonCode.TRADING_DAY_MISMATCH)

    def test_query_identity_scoping(self):
        store = ContractFactsStore()
        snap = make_snapshot(_complete_facts(), recorded_at=NOW, query_identity="sealed-slice-v0")
        store.record(snap)
        self.assertEqual(
            store.query(_identity(), T_AFTER, query_identity="sealed-slice-v0").status,
            SnapshotStatus.CURRENT,
        )
        mismatch = store.query(_identity(), T_AFTER, query_identity="other-slice")
        self.assertEqual(mismatch.status, SnapshotStatus.INSUFFICIENT)
        self.assertEqual(mismatch.reason_code, SnapshotReasonCode.QUERY_IDENTITY_MISMATCH)


class ValidationTests(unittest.TestCase):
    def test_naive_recorded_at_rejected(self):
        snap = make_snapshot(_complete_facts(), recorded_at=NOW)
        with self.assertRaises(ValueError):
            ContractFactsSnapshot(
                facts=snap.facts,
                recorded_at=datetime(2026, 1, 1),
                expires_at=None,
                is_complete=snap.is_complete,
                missing_facts=snap.missing_facts,
                session_identity=None,
                trading_day=None,
                query_identity=None,
            )

    def test_naive_expiry_rejected(self):
        with self.assertRaises(ValueError):
            make_snapshot(_complete_facts(), recorded_at=NOW, expires_at=datetime(2026, 1, 1))

    def test_naive_query_as_of_rejected(self):
        store = ContractFactsStore()
        store.record(make_snapshot(_complete_facts(), recorded_at=NOW))
        with self.assertRaises(ValueError):
            store.query(_identity(), datetime(2026, 1, 1))

    def test_blank_session_identity_rejected(self):
        with self.assertRaises(ValueError):
            make_snapshot(_complete_facts(), recorded_at=NOW, session_identity="  ")


class NoProductionDefaultsTests(unittest.TestCase):
    def test_no_fixture_numbers_exported_as_production_defaults(self):
        import src.contract_facts_runtime as module

        defaults = [name for name in vars(module) if name.startswith("DEFAULT_")]
        self.assertEqual(defaults, [])
        source = inspect.getsource(module)
        self.assertNotIn("100000", source)
        self.assertNotIn("100_000", source)
        # No module-level numeric default assignments for slippage/fee/margin/capital/risk.
        self.assertIsNone(
            re.search(
                r"^\s*(?:SLIPPAGE|FEE|MARGIN|CAPITAL|RISK)[A-Z_]*\s*=\s*Decimal",
                source,
                re.MULTILINE,
            )
        )


if __name__ == "__main__":
    unittest.main()
