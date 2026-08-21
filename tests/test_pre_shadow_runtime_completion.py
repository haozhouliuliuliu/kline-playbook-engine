"""Synthetic-only tests for prospective facts, E07 wiring, gate and HG adapter."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
import unittest
from zoneinfo import ZoneInfo

from src.candidate_eligibility import CandidateEligibilityGate, EligibilityPartition, QualifiedEligibilityView
from src.e07_runtime_mapping import E07RuntimeMappingWiring
from src.holy_grail_shadow_adapter import HolyGrailShadowAdapter
from src.pre_shadow_gate import PreShadowGate, PreShadowGateInputs
from src.prospective_execution_authority import ProspectiveExecutionAuthority, ProspectiveExecutionAuthorityError, ProspectiveFeeMarginFact, ProspectivePriceLimitFact, ProspectiveSlippageAuthority
from src.source_governed_mapping import MappingProvenance, SourceGovernedMappingRecord, SourceGovernedMappingSchedule
from src.contract_semantics import PositionDirection
from tools.build_pre_shadow_gate_v0_1 import build_payload


CN = ZoneInfo("Asia/Shanghai")
AT = datetime(2025, 1, 6, 9, 0, tzinfo=CN)


def _view(partition: EligibilityPartition) -> QualifiedEligibilityView:
    from src.canonical_identity import canonical_hash
    return QualifiedEligibilityView("parent", "manifest", "universe", "a" * 64, "revalidation", "decision", "implementation", (), canonical_hash([partition.partition_identity]), 0, 1, 0)


class PreShadowGateTests(unittest.TestCase):
    def test_not_authorized_is_distinct_from_technical_ready(self):
        inputs = PreShadowGateInputs(*([True] * 12), shadow_authorized=False)
        decision = PreShadowGate().evaluate(inputs)
        self.assertTrue(decision.technically_ready)
        self.assertFalse(decision.authorized_to_start)

    def test_missing_profile_denies(self):
        values = [True] * 12
        values[2] = False
        decision = PreShadowGate().evaluate(PreShadowGateInputs(*values, shadow_authorized=False))
        self.assertFalse(decision.technically_ready)
        self.assertIn("statistical_profile_locked", decision.missing_controls)

    def test_checked_in_gate_evidence_is_deterministic_and_denies(self):
        from pathlib import Path
        import json
        path = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "PRE_SHADOW_GATE_V0_1.json"
        self.assertEqual(build_payload(), json.loads(path.read_text(encoding="utf-8")))
        self.assertFalse(build_payload()["decision"]["authorized_to_start"])


class ProspectiveAuthorityTests(unittest.TestCase):
    def test_missing_facts_and_slippage_fail_closed(self):
        authority = ProspectiveExecutionAuthority()
        with self.assertRaises(ProspectiveExecutionAuthorityError):
            authority.require_fee_margin("SHFE.cu2502", AT)
        with self.assertRaises(ProspectiveExecutionAuthorityError):
            authority.require_price_limit("SHFE.cu2502", date(2025, 1, 6), AT)
        with self.assertRaises(ProspectiveExecutionAuthorityError):
            authority.require_slippage()

    def test_pit_facts_are_source_bound_and_resolve_only_after_availability(self):
        authority = ProspectiveExecutionAuthority(
            fee_margin_facts=(ProspectiveFeeMarginFact("SHFE.cu2502", AT, AT, "fee-source", Decimal("1"), Decimal("0.1")),),
            price_limit_facts=(ProspectivePriceLimitFact("SHFE.cu2502", date(2025, 1, 6), AT, AT, "limit-source", Decimal("90"), Decimal("110")),),
            slippage_authority=ProspectiveSlippageAuthority("slippage-source", True, "FIXED_SOURCE_BOUND_MODEL"),
        )
        self.assertEqual("fee-source", authority.require_fee_margin("SHFE.cu2502", AT).source_identity)
        self.assertEqual("limit-source", authority.require_price_limit("SHFE.cu2502", date(2025, 1, 6), AT).source_identity)
        self.assertTrue(authority.require_slippage().configured)


class E07RuntimeWiringTests(unittest.TestCase):
    def _wiring(self) -> tuple[E07RuntimeMappingWiring, str]:
        partition = EligibilityPartition("partition", "SHFE.cu2502", date(2025, 1, 6))
        gate = CandidateEligibilityGate(_view(partition), (partition,))
        provenance = MappingProvenance("TqSdk", "query", "session", AT, "a" * 64, True, "e07")
        record = SourceGovernedMappingRecord("MAIN:SHFE:cu", "KQ.m@SHFE.cu", "SHFE.cu2502", date(2025, 1, 6), AT, AT, provenance)
        schedule = SourceGovernedMappingSchedule("e07", ("MAIN:SHFE:cu",), (record,))
        return E07RuntimeMappingWiring(schedule, gate, frozenset({"SHFE.cu2502"}), strategy_identity="strategy", session_authority_identity="session", machine_implementation_identity="machine"), partition.partition_identity

    def test_pit_resolution_binds_every_identity(self):
        wiring, partition = self._wiring()
        resolved = wiring.resolve(research_symbol="MAIN:SHFE:cu", decision_at=AT + timedelta(minutes=1), partition_identity=partition)
        self.assertEqual("SHFE.cu2502", resolved.partition.concrete_contract)
        self.assertEqual("strategy", resolved.identity.strategy_identity)

    def test_first_day_or_lookahead_is_rejected(self):
        wiring, partition = self._wiring()
        with self.assertRaises(Exception):
            wiring.resolve(research_symbol="MAIN:SHFE:cu", decision_at=AT - timedelta(seconds=1), partition_identity=partition)
        with self.assertRaises(Exception):
            wiring.resolve(research_symbol="MAIN:SHFE:cu", decision_at=AT + timedelta(minutes=1), partition_identity="wrong")


class HolyGrailAdapterTests(unittest.TestCase):
    def test_real_machine_sequence_projects_open_close_and_directives(self):
        # Reuse only a deterministic non-candidate OHLC fixture to exercise the real machine.
        from tests.test_holy_grail_machine_operationalization import _HG_BASE_OHLC, aggregate, bars_from_ohlc, POLICY, TICK
        from src.holy_grail_machine import HolyGrailMachineOperationalization, HolyGrailMachineParameters, HolyGrailEventType
        machine = HolyGrailMachineOperationalization(HolyGrailMachineParameters(), POLICY, exchange="SHFE", concrete_instrument="cu2502", tick_size=TICK)
        bars = bars_from_ohlc(_HG_BASE_OHLC)
        adapter = HolyGrailShadowAdapter.from_machine(machine=machine, aggregation=aggregate(bars), strategy_identity_id="strategy", instrument="cu2502", quantity=Decimal("1"))
        self.assertTrue(any(item.event_type == HolyGrailEventType.ENTRY_ORDER_RESTING for item in adapter.directives))
        self.assertTrue(any(item.event_type == HolyGrailEventType.PROTECTIVE_STOP_ACTIVE for item in adapter.directives))
        self.assertEqual("HOLY_GRAIL_MACHINE_POSITION_OPENED", adapter.intents(type("Context", (), {"concrete_contract_id": "cu2502", "instrument": "cu2502", "available_at": bars[35].completed_bar.available_at, "identity_id": "context"})())[0].reason)
        from src.shadow_runtime import ShadowRuntime
        from tests.runtime_synthetic_fixture import make_config, make_contract_spec
        runtime = ShadowRuntime(make_config(contract_specs=(make_contract_spec("cu2502"),)), adapter, created_at=bars[0].completed_bar.available_at)
        for bar in bars:
            runtime.on_completed_bar(bar)
        self.assertIsNotNone(runtime.state.position_for("cu2502", PositionDirection.LONG))
        self.assertTrue(runtime.ledger.verify_chain())


if __name__ == "__main__":
    unittest.main()
