"""Deterministic offline tests for the REAL risk/safety primitives.

Covers the additive production-oriented REAL risk policy, safety state and gate:
BOUND/UNBOUND bindings, HEALTHY/UNHEALTHY/UNKNOWN health, kill/no-new-risk modes,
action classification, fail-closed reason-coded decisions and the safety-state
transition controller.

All numeric values are explicit FIXTURE-ONLY values; none are permanent
real-money risk limits and none are derived from any capital envelope. No
broker, provider, account or real-money action is performed.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from src.contract_semantics import PositionDirection
from src.real_risk_policy import BindingStatus, PolicyBinding, RealRiskPolicy
from src.real_risk_gate import (
    ActionRiskClassification,
    ProposedAction,
    RealRiskDecision,
    RealRiskGate,
    RealRiskRuntimeFacts,
    ReasonCode,
    RiskDecision,
    classify_action,
)
from src.real_safety_state import (
    ExternalMutationStatus,
    HealthState,
    RealSafetyController,
    RealSafetyState,
    SafetyMode,
    mode_allows_risk_increase,
)

PRODUCT = "RB"
CONTRACT = "SHFE.rb2510"

# FIXTURE-ONLY money/quantity values; NOT permanent risk limits and NOT derived
# from any capital envelope (including any ~RMB 100,000 reference).
FIXTURE_MAX_POSITION = Decimal("10")
FIXTURE_PER_TRADE_RISK = Decimal("5000")
FIXTURE_DAILY_LOSS = Decimal("20000")
FIXTURE_DAILY_RISK = Decimal("10000")
FIXTURE_CUMULATIVE_LOSS = Decimal("50000")
FIXTURE_DRAWDOWN = Decimal("30000")
FIXTURE_MIN_MARGIN = Decimal("20000")
FIXTURE_RESERVE = Decimal("10000")
FIXTURE_ACCOUNT_CASH = Decimal("250000")
FIXTURE_ACCOUNT_MARGIN = Decimal("50000")
FIXTURE_ACCOUNT_HEADROOM = Decimal("150000")
FIXTURE_STOP_RISK = Decimal("2000")


def _now() -> datetime:
    return datetime(2026, 8, 29, 9, 30, tzinfo=timezone.utc)


def _empty_policy(**overrides: object) -> RealRiskPolicy:
    """Explicitly UNBOUND policy (no binding values)."""
    defaults: dict[str, object] = {
        "policy_id": "FIXTURE_UNBOUND_POLICY",
        "version": "test-v0.1",
    }
    defaults.update(overrides)
    return RealRiskPolicy(**defaults)  # type: ignore[arg-type]


def _bound_policy(**overrides: object) -> RealRiskPolicy:
    """Synthetic fully-bound FIXTURE policy (all required bindings BOUND)."""
    defaults: dict[str, object] = {
        "policy_id": "FIXTURE_REAL_RISK_POLICY",
        "version": "test-v0.1",
        "product_whitelist": frozenset({PRODUCT}),
        "contract_authorization": frozenset({CONTRACT}),
        "max_position_quantity": FIXTURE_MAX_POSITION,
        "allow_add_on": True,
        "per_trade_risk_ceiling": FIXTURE_PER_TRADE_RISK,
        "daily_loss_ceiling": FIXTURE_DAILY_LOSS,
        "daily_risk_ceiling": FIXTURE_DAILY_RISK,
        "cumulative_loss_ceiling": FIXTURE_CUMULATIVE_LOSS,
        "drawdown_ceiling": FIXTURE_DRAWDOWN,
        "minimum_margin_headroom": FIXTURE_MIN_MARGIN,
        "operational_reserve_headroom": FIXTURE_RESERVE,
    }
    defaults.update(overrides)
    return RealRiskPolicy(**defaults)  # type: ignore[arg-type]


def _facts(**overrides: object) -> RealRiskRuntimeFacts:
    """One healthy OPEN fact bundle; override fields for each scenario."""
    defaults: dict[str, object] = {
        "proposed_action": ProposedAction.OPEN,
        "reconciliation_health": HealthState.HEALTHY,
        "market_data_health": HealthState.HEALTHY,
        "provider_runtime_health": HealthState.HEALTHY,
        "broker_session_health": HealthState.HEALTHY,
        "external_mutation_status": ExternalMutationStatus.RESOLVED,
        "concrete_contract_id": CONTRACT,
        "product_family": PRODUCT,
        "proposed_direction": PositionDirection.LONG,
        "proposed_quantity": Decimal("1"),
        "current_position_direction": None,
        "current_position_quantity": Decimal("0"),
        "account_cash": FIXTURE_ACCOUNT_CASH,
        "account_margin": FIXTURE_ACCOUNT_MARGIN,
        "account_headroom": FIXTURE_ACCOUNT_HEADROOM,
        "proposed_stop_risk": FIXTURE_STOP_RISK,
        "realized_pnl": Decimal("0"),
        "unrealized_pnl": Decimal("0"),
        "daily_loss": Decimal("0"),
        "daily_risk_used": Decimal("0"),
        "drawdown": Decimal("0"),
        "cumulative_loss": Decimal("0"),
        "unresolved_order_count": 0,
        "kill_switch_tripped": False,
        "no_new_risk_requested": False,
    }
    defaults.update(overrides)
    return RealRiskRuntimeFacts(**defaults)  # type: ignore[arg-type]


def _normal_safety() -> RealSafetyState:
    return RealSafetyState(
        mode=SafetyMode.NORMAL,
        mode_reason="FIXTURE normal",
        mode_changed_at=_now(),
        external_mutation_status=ExternalMutationStatus.RESOLVED,
        external_mutation_since=None,
        hard_inconsistency_latched=False,
        hard_inconsistency_reason=None,
        hard_inconsistency_since=None,
    )


class RealRiskPolicyTests(unittest.TestCase):
    def test_all_bindings_unbound_by_default(self) -> None:
        """No production defaults: every binding is UNBOUND until supplied."""
        policy = _empty_policy()
        for binding in PolicyBinding:
            self.assertIs(
                policy.binding_status(binding),
                BindingStatus.UNBOUND,
                f"{binding.value} must default to UNBOUND",
            )
        self.assertFalse(policy.is_fully_bound())
        self.assertEqual(len(policy.required_unbound_bindings()), len(RealRiskPolicy.required_unbound_bindings(policy)))
        self.assertIn(PolicyBinding.PRODUCT_WHITELIST, policy.required_unbound_bindings())

    def test_no_field_has_a_fixture_default(self) -> None:
        """The policy dataclass carries no hidden numeric/whitelist defaults."""
        policy = _empty_policy()
        for field in (
            "product_whitelist",
            "contract_authorization",
            "max_position_quantity",
            "allow_add_on",
            "per_trade_risk_ceiling",
            "daily_loss_ceiling",
            "daily_risk_ceiling",
            "cumulative_loss_ceiling",
            "drawdown_ceiling",
            "minimum_margin_headroom",
            "operational_reserve_headroom",
        ):
            self.assertIsNone(getattr(policy, field), f"{field} must default to None")

    def test_explicit_bound_status(self) -> None:
        policy = _bound_policy()
        for binding in PolicyBinding:
            self.assertIs(policy.binding_status(binding), BindingStatus.BOUND)
        self.assertTrue(policy.is_fully_bound())
        self.assertEqual(policy.required_unbound_bindings(), ())

    def test_empty_whitelist_is_unbound(self) -> None:
        """An empty whitelist/authorization is not an established binding."""
        policy = _bound_policy(product_whitelist=frozenset())
        self.assertIs(policy.binding_status(PolicyBinding.PRODUCT_WHITELIST), BindingStatus.UNBOUND)
        self.assertFalse(policy.is_fully_bound())

    def test_identity_is_canonical_and_stable(self) -> None:
        left = _bound_policy()
        right = _bound_policy()
        self.assertEqual(left.identity_id, right.identity_id)
        changed = _bound_policy(max_position_quantity=Decimal("9"))
        self.assertNotEqual(left.identity_id, changed.identity_id)

    def test_validation_rejects_bad_bindings(self) -> None:
        with self.assertRaises(ValueError):
            _bound_policy(max_position_quantity=Decimal("0"))
        with self.assertRaises(ValueError):
            _bound_policy(per_trade_risk_ceiling=Decimal("-1"))
        with self.assertRaises(ValueError):
            _bound_policy(allow_add_on="yes")  # type: ignore[arg-type]


class RealSafetyControllerTests(unittest.TestCase):
    def test_starts_normal_and_allows_risk_increase(self) -> None:
        controller = RealSafetyController(_now())
        self.assertIs(controller.state.mode, SafetyMode.NORMAL)
        self.assertTrue(controller.state.allows_risk_increase())
        self.assertTrue(mode_allows_risk_increase(SafetyMode.NORMAL))

    def test_only_normal_allows_risk_increase(self) -> None:
        for mode in (SafetyMode.NO_NEW_RISK, SafetyMode.KILL, SafetyMode.UNKNOWN):
            self.assertFalse(mode_allows_risk_increase(mode))

    def test_trip_and_disarm_kill_require_explicit_actions(self) -> None:
        controller = RealSafetyController(_now())
        state = controller.trip_kill("FIXTURE hard stop", _now())
        self.assertIs(state.mode, SafetyMode.KILL)
        self.assertFalse(state.allows_risk_increase())
        with self.assertRaises(ValueError):
            controller.trip_kill("", _now())
        disarmed = controller.disarm_kill("FIXTURE manual disarm after review", _now())
        self.assertIs(disarmed.mode, SafetyMode.NORMAL)
        with self.assertRaises(ValueError):
            controller.disarm_kill("cannot disarm when not tripped", _now())

    def test_pause_resume_are_explicit(self) -> None:
        controller = RealSafetyController(_now())
        with self.assertRaises(ValueError):
            controller.resume("cannot resume from normal", _now())
        paused = controller.pause("FIXTURE pause new risk", _now())
        self.assertIs(paused.mode, SafetyMode.NO_NEW_RISK)
        resumed = controller.resume("FIXTURE resume", _now())
        self.assertIs(resumed.mode, SafetyMode.NORMAL)

    def test_hard_inconsistency_persists_until_manual_clear(self) -> None:
        """One healthy sample must not auto-clear a hard inconsistency."""
        controller = RealSafetyController(_now())
        controller.latch_hard_inconsistency("FIXTURE reconciliation mismatch", _now())
        self.assertTrue(controller.state.hard_inconsistency_latched)
        self.assertFalse(controller.state.allows_risk_increase())
        # No auto-clear exists; only an explicit manual clear unlatches.
        self.assertTrue(controller.state.hard_inconsistency_latched)
        with self.assertRaises(ValueError):
            controller.clear_hard_inconsistency("", _now())
        controller.clear_hard_inconsistency("FIXTURE manual reset after reconciliation", _now())
        self.assertFalse(controller.state.hard_inconsistency_latched)
        self.assertTrue(controller.state.allows_risk_increase())

    def test_external_mutation_forces_no_new_risk_until_reconciliation(self) -> None:
        controller = RealSafetyController(_now())
        controller.record_external_mutation("FIXTURE manual position edit", _now())
        self.assertIs(controller.state.mode, SafetyMode.NO_NEW_RISK)
        self.assertIs(controller.state.external_mutation_status, ExternalMutationStatus.UNRESOLVED)
        self.assertFalse(controller.state.allows_risk_increase())
        # Resolution alone does not resume trading; an explicit resume is required.
        controller.resolve_external_mutation("FIXTURE reconciled", _now())
        self.assertIs(controller.state.external_mutation_status, ExternalMutationStatus.RESOLVED)
        self.assertIs(controller.state.mode, SafetyMode.NO_NEW_RISK)
        with self.assertRaises(ValueError):
            controller.resolve_external_mutation("not unresolved", _now())
        controller.resume("FIXTURE resume after reconciliation", _now())
        self.assertIs(controller.state.mode, SafetyMode.NORMAL)
        self.assertTrue(controller.state.allows_risk_increase())

    def test_kill_disarm_and_resume_cannot_bypass_unresolved_external_mutation(self) -> None:
        controller = RealSafetyController(_now())
        controller.record_external_mutation("FIXTURE manual position edit", _now())
        controller.trip_kill("FIXTURE kill", _now())

        disarmed = controller.disarm_kill("FIXTURE manual disarm", _now())
        self.assertIs(disarmed.mode, SafetyMode.NO_NEW_RISK)
        self.assertIs(disarmed.external_mutation_status, ExternalMutationStatus.UNRESOLVED)
        with self.assertRaisesRegex(ValueError, "unresolved external mutation"):
            controller.resume("must remain blocked", _now())

        controller.resolve_external_mutation("FIXTURE complete reconciliation", _now())
        resumed = controller.resume("FIXTURE resume after resolution", _now())
        self.assertIs(resumed.mode, SafetyMode.NORMAL)
        self.assertTrue(resumed.allows_risk_increase())


class ClassifyActionTests(unittest.TestCase):
    def test_unknown_action_classifies_unknown(self) -> None:
        facts = _facts(proposed_action=ProposedAction.UNKNOWN)
        self.assertIs(classify_action(facts), ActionRiskClassification.UNKNOWN)

    def test_hold_classifies_neutral(self) -> None:
        facts = _facts(proposed_action=ProposedAction.HOLD)
        self.assertIs(classify_action(facts), ActionRiskClassification.NEUTRAL)

    def test_open_classifies_increasing(self) -> None:
        facts = _facts(proposed_action=ProposedAction.OPEN)
        self.assertIs(classify_action(facts), ActionRiskClassification.RISK_INCREASING)

    def test_close_with_full_truth_classifies_reducing(self) -> None:
        facts = _facts(
            proposed_action=ProposedAction.CLOSE,
            current_position_direction=PositionDirection.LONG,
            current_position_quantity=Decimal("5"),
            proposed_direction=PositionDirection.SHORT,
            proposed_quantity=Decimal("3"),
        )
        self.assertIs(classify_action(facts), ActionRiskClassification.RISK_REDUCING)

    def test_close_with_unknown_position_truth_not_reducing(self) -> None:
        facts = _facts(
            proposed_action=ProposedAction.CLOSE,
            current_position_quantity=None,
            proposed_direction=PositionDirection.SHORT,
            proposed_quantity=Decimal("3"),
        )
        self.assertIs(classify_action(facts), ActionRiskClassification.UNKNOWN)

    def test_close_wrong_direction_not_reducing(self) -> None:
        facts = _facts(
            proposed_action=ProposedAction.CLOSE,
            current_position_direction=PositionDirection.LONG,
            current_position_quantity=Decimal("5"),
            proposed_direction=PositionDirection.LONG,
            proposed_quantity=Decimal("3"),
        )
        self.assertIs(classify_action(facts), ActionRiskClassification.UNKNOWN)

    def test_close_oversized_proposal_still_reduces_to_zero(self) -> None:
        facts = _facts(
            proposed_action=ProposedAction.CLOSE,
            current_position_direction=PositionDirection.LONG,
            current_position_quantity=Decimal("5"),
            proposed_direction=PositionDirection.SHORT,
            proposed_quantity=Decimal("9"),
        )
        self.assertIs(classify_action(facts), ActionRiskClassification.RISK_REDUCING)


class RealRiskGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.gate = RealRiskGate()

    def test_unbound_policy_denies_risk_increase(self) -> None:
        """Case: any required binding UNBOUND => DENY, never ALLOW."""
        decision = self.gate.evaluate(_empty_policy(), _normal_safety(), _facts(), _now())
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.PRODUCT_WHITELIST_UNBOUND, decision.reason_codes)
        self.assertFalse(decision.allowed())

    def test_product_not_whitelisted_denied(self) -> None:
        """Case: product outside the bound whitelist => DENY."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(product_family="CU"), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.PRODUCT_NOT_WHITELISTED, decision.reason_codes)

    def test_max_position_exceeded_denied(self) -> None:
        """Case: resulting position above the bound max => DENY."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(proposed_quantity=Decimal("11")), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.MAX_POSITION_EXCEEDED, decision.reason_codes)

    def test_add_on_not_explicitly_allowed_denied(self) -> None:
        """Case: pyramiding without explicit add-on permission => DENY."""
        add_facts = dict(
            current_position_direction=PositionDirection.LONG,
            current_position_quantity=Decimal("5"),
            proposed_direction=PositionDirection.LONG,
            proposed_quantity=Decimal("1"),
        )
        decision = self.gate.evaluate(
            _bound_policy(allow_add_on=None), _normal_safety(), _facts(**add_facts), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.ADD_ON_UNBOUND, decision.reason_codes)

        decision = self.gate.evaluate(
            _bound_policy(allow_add_on=False), _normal_safety(), _facts(**add_facts), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.ADD_ON_NOT_ALLOWED, decision.reason_codes)

    def test_unknown_margin_fails_closed(self) -> None:
        """Case: margin/headroom unproven => INSUFFICIENT_OR_UNKNOWN, not ALLOW."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(account_headroom=None), _now()
        )
        self.assertIs(decision.decision, RiskDecision.INSUFFICIENT_OR_UNKNOWN)
        self.assertIn(ReasonCode.MARGIN_HEADROOM_UNPROVEN, decision.reason_codes)
        self.assertFalse(decision.allowed())

    def test_unproven_risk_limits_fail_closed(self) -> None:
        """Case: per-trade risk unprovable => INSUFFICIENT_OR_UNKNOWN."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(proposed_stop_risk=None), _now()
        )
        self.assertIs(decision.decision, RiskDecision.INSUFFICIENT_OR_UNKNOWN)
        self.assertIn(ReasonCode.PER_TRADE_RISK_UNKNOWN, decision.reason_codes)
        self.assertFalse(decision.allowed())

    def test_unresolved_order_denied(self) -> None:
        """Case: duplicate/unresolved order => DENY; unknown count => fail closed."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(unresolved_order_count=2), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.UNRESOLVED_ORDER, decision.reason_codes)

        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(unresolved_order_count=None), _now()
        )
        self.assertIs(decision.decision, RiskDecision.INSUFFICIENT_OR_UNKNOWN)
        self.assertIn(ReasonCode.UNRESOLVED_ORDER_UNKNOWN, decision.reason_codes)

    def test_reconciliation_unknown_fails_closed(self) -> None:
        """Case: reconciliation health UNKNOWN => INSUFFICIENT_OR_UNKNOWN."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(reconciliation_health=HealthState.UNKNOWN), _now()
        )
        self.assertIs(decision.decision, RiskDecision.INSUFFICIENT_OR_UNKNOWN)
        self.assertIn(ReasonCode.RECONCILIATION_UNKNOWN, decision.reason_codes)

    def test_market_provider_broker_health_fail_closed(self) -> None:
        """Case: market/provider/broker UNHEALTHY or UNKNOWN fail closed."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(market_data_health=HealthState.UNHEALTHY), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.MARKET_DATA_UNHEALTHY, decision.reason_codes)

        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(provider_runtime_health=HealthState.UNKNOWN), _now()
        )
        self.assertIs(decision.decision, RiskDecision.INSUFFICIENT_OR_UNKNOWN)
        self.assertIn(ReasonCode.PROVIDER_RUNTIME_UNKNOWN, decision.reason_codes)

        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(broker_session_health=HealthState.UNHEALTHY), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.BROKER_SESSION_UNHEALTHY, decision.reason_codes)

    def test_external_mutation_unresolved_denied(self) -> None:
        """Case: unresolved external/manual mutation => DENY."""
        decision = self.gate.evaluate(
            _bound_policy(),
            _normal_safety(),
            _facts(external_mutation_status=ExternalMutationStatus.UNRESOLVED),
            _now(),
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.EXTERNAL_MUTATION_UNRESOLVED, decision.reason_codes)

    def test_persistent_external_mutation_outranks_contradictory_transient_facts(self) -> None:
        controller = RealSafetyController(_now())
        controller.record_external_mutation("FIXTURE manual broker mutation", _now())
        controller.trip_kill("FIXTURE kill", _now())
        persistent = controller.disarm_kill("FIXTURE disarm", _now())

        decision = self.gate.evaluate(
            _bound_policy(),
            persistent,
            _facts(external_mutation_status=ExternalMutationStatus.RESOLVED),
            _now(),
        )

        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.EXTERNAL_MUTATION_UNRESOLVED, decision.reason_codes)

    def test_kill_switch_tripped_denies(self) -> None:
        """Case: KILL mode or kill input => DENY, never risk increase."""
        killed = RealSafetyState(
            mode=SafetyMode.KILL,
            mode_reason="FIXTURE kill",
            mode_changed_at=_now(),
            external_mutation_status=ExternalMutationStatus.RESOLVED,
            external_mutation_since=None,
            hard_inconsistency_latched=False,
            hard_inconsistency_reason=None,
            hard_inconsistency_since=None,
        )
        decision = self.gate.evaluate(_bound_policy(), killed, _facts(), _now())
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.KILL_SWITCH_TRIPPED, decision.reason_codes)

        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(kill_switch_tripped=True), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.KILL_SWITCH_TRIPPED, decision.reason_codes)

    def test_no_new_risk_denies_increase_but_allows_proven_reduction(self) -> None:
        """Case: no-new-risk blocks increase; proven reduction stays allowed."""
        paused = RealSafetyState(
            mode=SafetyMode.NO_NEW_RISK,
            mode_reason="FIXTURE paused",
            mode_changed_at=_now(),
            external_mutation_status=ExternalMutationStatus.RESOLVED,
            external_mutation_since=None,
            hard_inconsistency_latched=False,
            hard_inconsistency_reason=None,
            hard_inconsistency_since=None,
        )
        decision = self.gate.evaluate(_bound_policy(), paused, _facts(), _now())
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.NO_NEW_RISK_ACTIVE, decision.reason_codes)

        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(no_new_risk_requested=True), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.NO_NEW_RISK_ACTIVE, decision.reason_codes)

        reduce_facts = _facts(
            proposed_action=ProposedAction.CLOSE,
            current_position_direction=PositionDirection.LONG,
            current_position_quantity=Decimal("5"),
            proposed_direction=PositionDirection.SHORT,
            proposed_quantity=Decimal("3"),
        )
        decision = self.gate.evaluate(_bound_policy(), paused, reduce_facts, _now())
        self.assertIs(decision.decision, RiskDecision.ALLOW)
        self.assertIs(decision.action_classification, ActionRiskClassification.RISK_REDUCING)

    def test_synthetic_fully_bound_allow(self) -> None:
        """Case: synthetic fully-bound policy + healthy facts => ALLOW."""
        decision = self.gate.evaluate(_bound_policy(), _normal_safety(), _facts(), _now())
        self.assertIs(decision.decision, RiskDecision.ALLOW)
        self.assertIs(decision.action_classification, ActionRiskClassification.RISK_INCREASING)
        self.assertIn(ReasonCode.ALLOWED, decision.reason_codes)
        self.assertTrue(decision.allowed())

    def test_claimed_reduction_with_unknown_truth_not_allow(self) -> None:
        """Case: claimed reduction with unknown position truth => not ALLOW."""
        decision = self.gate.evaluate(
            _bound_policy(),
            _normal_safety(),
            _facts(
                proposed_action=ProposedAction.CLOSE,
                current_position_quantity=None,
                proposed_direction=PositionDirection.SHORT,
                proposed_quantity=Decimal("3"),
            ),
            _now(),
        )
        self.assertIs(decision.decision, RiskDecision.INSUFFICIENT_OR_UNKNOWN)
        self.assertIn(ReasonCode.ACTION_CLASSIFICATION_UNKNOWN, decision.reason_codes)
        self.assertFalse(decision.allowed())

    def test_proven_reduction_deterministic_allow(self) -> None:
        """Case: proven reduction with full truth and healthy session => ALLOW."""
        decision = self.gate.evaluate(
            _bound_policy(),
            _normal_safety(),
            _facts(
                proposed_action=ProposedAction.CLOSE,
                current_position_direction=PositionDirection.LONG,
                current_position_quantity=Decimal("5"),
                proposed_direction=PositionDirection.SHORT,
                proposed_quantity=Decimal("3"),
            ),
            _now(),
        )
        self.assertIs(decision.decision, RiskDecision.ALLOW)
        self.assertIs(decision.action_classification, ActionRiskClassification.RISK_REDUCING)
        self.assertIn(ReasonCode.ALLOWED, decision.reason_codes)

    def test_reduction_denied_when_reconciliation_unhealthy(self) -> None:
        """No blanket close: unhealthy reconciliation blocks a close."""
        decision = self.gate.evaluate(
            _bound_policy(),
            _normal_safety(),
            _facts(
                proposed_action=ProposedAction.CLOSE,
                current_position_direction=PositionDirection.LONG,
                current_position_quantity=Decimal("5"),
                proposed_direction=PositionDirection.SHORT,
                proposed_quantity=Decimal("3"),
                reconciliation_health=HealthState.UNHEALTHY,
            ),
            _now(),
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.RECONCILIATION_UNHEALTHY, decision.reason_codes)
        self.assertFalse(decision.allowed())

    def test_hold_neutral_allowed(self) -> None:
        """Case: HOLD/no-order is NEUTRAL and ALLOWED under NORMAL safety."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(proposed_action=ProposedAction.HOLD), _now()
        )
        self.assertIs(decision.decision, RiskDecision.ALLOW)
        self.assertIs(decision.action_classification, ActionRiskClassification.NEUTRAL)
        self.assertIn(ReasonCode.NEUTRAL_NO_RISK, decision.reason_codes)

    def test_daily_loss_ceiling_exceeded_denied(self) -> None:
        """Case: daily realized loss above the bound ceiling => DENY."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(daily_loss=Decimal("21000")), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.DAILY_LOSS_CEILING_EXCEEDED, decision.reason_codes)

    def test_daily_risk_ceiling_exceeded_denied(self) -> None:
        """Case: used + proposed daily risk above the bound ceiling => DENY."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(daily_risk_used=Decimal("9000")), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.DAILY_RISK_CEILING_EXCEEDED, decision.reason_codes)

    def test_drawdown_ceiling_exceeded_denied(self) -> None:
        """Case: drawdown above the bound ceiling => DENY."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(drawdown=Decimal("31000")), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.DRAWDOWN_CEILING_EXCEEDED, decision.reason_codes)

    def test_margin_headroom_insufficient_denied(self) -> None:
        """Case: proven headroom below the bound minimum margin => DENY."""
        decision = self.gate.evaluate(
            _bound_policy(), _normal_safety(), _facts(account_headroom=Decimal("15000")), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.MARGIN_HEADROOM_INSUFFICIENT, decision.reason_codes)

    def test_reserve_headroom_enforced_only_when_bound(self) -> None:
        """Case: operational reserve enforced when supplied; skipped when absent.

        Uses a reserve above the minimum-margin binding so the reserve check is
        the deciding constraint (min margin still passes).
        """
        reserve_policy = _bound_policy(operational_reserve_headroom=Decimal("25000"))
        decision = self.gate.evaluate(
            reserve_policy, _normal_safety(), _facts(account_headroom=Decimal("22000")), _now()
        )
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.RESERVE_HEADROOM_INSUFFICIENT, decision.reason_codes)

        no_reserve_policy = _bound_policy(operational_reserve_headroom=None)
        decision = self.gate.evaluate(
            no_reserve_policy, _normal_safety(), _facts(account_headroom=Decimal("22000")), _now()
        )
        self.assertIs(decision.decision, RiskDecision.ALLOW)

    def test_hard_inconsistency_latch_denies(self) -> None:
        """Case: persistent hard inconsistency latched => DENY even on healthy facts."""
        latched = RealSafetyState(
            mode=SafetyMode.NORMAL,
            mode_reason="FIXTURE normal",
            mode_changed_at=_now(),
            external_mutation_status=ExternalMutationStatus.RESOLVED,
            external_mutation_since=None,
            hard_inconsistency_latched=True,
            hard_inconsistency_reason="FIXTURE hard inconsistency",
            hard_inconsistency_since=_now(),
        )
        decision = self.gate.evaluate(_bound_policy(), latched, _facts(), _now())
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.HARD_INCONSISTENCY_LATCHED, decision.reason_codes)

    def test_unknown_safety_mode_denies(self) -> None:
        """Case: UNKNOWN safety mode => DENY (never allows risk increase)."""
        unknown = RealSafetyState(
            mode=SafetyMode.UNKNOWN,
            mode_reason="FIXTURE state unknown",
            mode_changed_at=_now(),
            external_mutation_status=ExternalMutationStatus.RESOLVED,
            external_mutation_since=None,
            hard_inconsistency_latched=False,
            hard_inconsistency_reason=None,
            hard_inconsistency_since=None,
        )
        decision = self.gate.evaluate(_bound_policy(), unknown, _facts(), _now())
        self.assertIs(decision.decision, RiskDecision.DENY)
        self.assertIn(ReasonCode.SAFETY_MODE_UNKNOWN, decision.reason_codes)

    def test_decision_is_deterministic_and_identity_stable(self) -> None:
        left = self.gate.evaluate(_bound_policy(), _normal_safety(), _facts(), _now())
        right = self.gate.evaluate(_bound_policy(), _normal_safety(), _facts(), _now())
        self.assertEqual(left.identity_id, right.identity_id)
        self.assertIsInstance(left, RealRiskDecision)

    def test_facts_validation_rejects_bad_values(self) -> None:
        with self.assertRaises(ValueError):
            _facts(proposed_quantity=Decimal("0"))
        with self.assertRaises(ValueError):
            _facts(current_position_quantity=Decimal("-1"))
        with self.assertRaises(ValueError):
            _facts(unresolved_order_count=-1)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
