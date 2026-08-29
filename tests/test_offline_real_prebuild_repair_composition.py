"""Bounded cross-finding regression for the consolidated REAL repair."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.contract_facts import FeeModel, MarginBasis, MarginFacts
from src.fangzheng_ctp_candidate import (
    CtpCallbackType,
    CtpOrderRecord,
    FangzhengCtpBrokerAdapter,
)
from src.fangzheng_ctp_fake import FakeCtpOperation, FakeCtpStep, ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition, RealOrderLifecycle
from src.real_preflight import RealDurableState
from src.real_risk_gate import RealRiskGate, RiskDecision
from src.real_runtime_controller import RealRuntimeController
from src.real_safety_state import ExternalMutationStatus, RealSafetyController
from src.realtime_provider_attempt_ledger import (
    RealtimeProviderAttemptLedger,
    realtime_provider_attempt_ledger_path_for,
)
from src.realtime_provider_control import RealtimeBudgetInput, RealtimeProviderControl
from tests.real_synthetic_fixture import ASSESSED_AT, synthetic_config
from tests.test_contract_facts import _contract
from tests.test_fangzheng_ctp_candidate import CONTRACT, instruction, profile
from tests.test_fangzheng_ctp_fake import callback, establish_ready, ready_steps
from tests.test_real_execution_composition import (
    NOW,
    TRADING_DAY,
    _ready_query_steps,
    _trading_state,
)
from tests.test_real_risk_safety import _bound_policy, _facts
from tests.test_realtime_provider_control import AUTHORITY_IDENTITY, _identity


class OfflineRealPrebuildRepairCompositionTests(unittest.TestCase):
    def test_all_five_repaired_invariants_hold_together_offline(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)

            controller = RealRuntimeController(config=synthetic_config(state_root=root))
            preflight = controller.preflight(
                assessed_at=ASSESSED_AT,
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                account_state=RealDurableState.UNKNOWN,
                reconciliation_state=RealDurableState.CLEAR,
            )
            self.assertFalse(preflight.ready)

            safety = RealSafetyController(ASSESSED_AT)
            safety.record_external_mutation("fixture external mutation", ASSESSED_AT)
            safety.trip_kill("fixture kill", ASSESSED_AT)
            persistent = safety.disarm_kill("fixture disarm", ASSESSED_AT)
            decision = RealRiskGate().evaluate(
                _bound_policy(),
                persistent,
                _facts(external_mutation_status=ExternalMutationStatus.RESOLVED),
                ASSESSED_AT,
            )
            self.assertIs(decision.decision, RiskDecision.DENY)

            provider_control = RealtimeProviderControl(ledger=RealtimeProviderAttemptLedger(
                realtime_provider_attempt_ledger_path_for(root),
                authority_identity=AUTHORITY_IDENTITY,
            ))
            admission = provider_control.admit(
                identity=_identity(authority_identity="OTHER_AUTHORITY"),
                budget=RealtimeBudgetInput(),
            )
            self.assertFalse(admission.admitted)
            self.assertEqual(provider_control.admitted_attempt_count(), 0)

            execution_path = root / "real-execution.sqlite3"
            first_transport = ScriptedCtpTransport(ready_steps() + (
                FakeCtpStep(
                    FakeCtpOperation.SUBMIT,
                    (callback("disconnect", CtpCallbackType.DISCONNECTED),),
                    expected_project_order_id="project-order-1",
                ),
            ))
            first_adapter = FangzhengCtpBrokerAdapter(first_transport, profile())
            establish_ready(first_adapter)
            first = RealExecutionComposition(
                path=execution_path, adapter=first_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            first.submit_order(instruction(), submitted_at=NOW)
            first.consume_adapter_events()

            incomplete_steps = list(_ready_query_steps())
            incomplete_steps[4] = FakeCtpStep(FakeCtpOperation.QUERY_POSITIONS)
            incomplete_transport = ScriptedCtpTransport(tuple(incomplete_steps))
            incomplete_adapter = FangzhengCtpBrokerAdapter(incomplete_transport, profile())
            establish_ready(incomplete_adapter)
            incomplete = RealExecutionComposition(
                path=execution_path, adapter=incomplete_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            incomplete_report = incomplete.reconcile_adapter_truth(
                round_id="incomplete", requested_at=NOW, observed_at=NOW,
                expected_account=incomplete_adapter.fetch_account_snapshot(), expected_positions=(),
            )
            self.assertFalse(incomplete_report.new_risk_allowed)
            self.assertIs(
                incomplete.order_for("project-order-1").lifecycle,
                RealOrderLifecycle.UNKNOWN,
            )

            open_record = CtpOrderRecord(
                "project-order-1", "request-1", "broker-order-1", CONTRACT,
                instruction().direction, instruction().action, "LIVE",
                Decimal("2"), Decimal("0"), NOW,
            )
            complete_transport = ScriptedCtpTransport(_ready_query_steps(orders=(open_record,)))
            complete_adapter = FangzhengCtpBrokerAdapter(complete_transport, profile())
            establish_ready(complete_adapter)
            complete = RealExecutionComposition(
                path=execution_path, adapter=complete_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            complete.reconcile_adapter_truth(
                round_id="complete", requested_at=NOW, observed_at=NOW,
                expected_account=complete_adapter.fetch_account_snapshot(), expected_positions=(),
            )
            self.assertIs(
                complete.order_for("project-order-1").lifecycle,
                RealOrderLifecycle.OPEN,
            )

            original_facts = _contract(
                margin=MarginFacts(
                    basis=MarginBasis.PER_LOT_AMOUNT,
                    initial_margin_per_lot=Decimal("4500"),
                ),
                fee=FeeModel(commission_per_lot=Decimal("5")),
            )
            changed_facts = _contract(
                margin=MarginFacts(
                    basis=MarginBasis.PER_LOT_AMOUNT,
                    initial_margin_per_lot=Decimal("4500"),
                ),
                fee=FeeModel(commission_per_lot=Decimal("6")),
            )
            self.assertNotEqual(original_facts.identity_id, changed_facts.identity_id)


if __name__ == "__main__":
    unittest.main()
