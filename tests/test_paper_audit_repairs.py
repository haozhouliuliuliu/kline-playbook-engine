"""Focused regressions for the independent PAPER-readiness repair package."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerOrderInstruction,
    BrokerOrderSnapshot,
    OrderRole,
    OrderType,
)
from src.contract_semantics import OrderAction, PositionDirection
from src.jianghe_response_normalizer import JiangheResponseNormalizer
from src.jianghe_execution_bridge import JiangheExecutionBridge
from src.paper_activation_profile import PaperActivationProfile, PaperActivationStatus
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import (
    MutablePaperAuthoritySource,
    PaperAuthorityStatus,
    PaperExecutionAuthority,
)
from src.paper_order_journal import TERMINAL, PaperOrderJournal
from src.paper_execution_chain import PaperDeterministicExecutionChain
from src.paper_external_composition import (
    PaperExternalComponents,
    PaperExternalFactories,
    build_external_paper_controller,
)
from src.paper_runtime import PaperTraderDecision
from src.paper_runtime_bindings import (
    PaperExecutableBindings,
    PaperToolRoleBinding,
    PaperToolRoleStatus,
)
from src.paper_runtime_layout import PaperRuntimeLayoutError, PaperRuntimeLayout
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_wake_journal import SKIPPED, PaperWakeJournal
from src.risk_gate import RiskGate, RiskRuleSet
from src.tqsdk_paper_candidate import TqSdkPaperBrokerAdapter
from src.tqsdk_paper_driver import TqSdkPaperExecutionDriver
from src.tqsdk_live_source import TqSdkLiveOneMinuteSource
from tests.test_paper_live_causal_context import _CALENDAR
from tools.run_paper_runtime import _config_from_args, _run_external, build_parser


TZ = ZoneInfo("Asia/Shanghai")
CONTRACT = "SHFE.rb9999"
AT = datetime(2026, 8, 28, 9, 0, tzinfo=TZ)


def _authority(**changes: object) -> PaperExecutionAuthority:
    values = {
        "authority_id": "paper-authority",
        "broker_kind": "TQSDK_CANDIDATE",
        "account_kind": "TQSDK_PAPER",
        "status": PaperAuthorityStatus.ACTIVE,
        "allow_connect": True,
        "allow_order_submit": True,
        "allow_order_cancel": True,
        "allow_order_replace": True,
        "broker_identity": "broker-1",
        "account_identity": "account-1",
        "allowed_contracts": (CONTRACT,),
        "valid_from": AT - timedelta(minutes=1),
        "expires_at": AT + timedelta(minutes=1),
    }
    values.update(changes)
    return PaperExecutionAuthority(**values)


def _instruction(quantity: str = "1.0") -> BrokerOrderInstruction:
    return BrokerOrderInstruction(
        client_request_id="request-1",
        client_order_id="request-1",
        concrete_contract_id=CONTRACT,
        direction=PositionDirection.LONG,
        action=OrderAction.OPEN,
        order_type=OrderType.LIMIT,
        quantity=Decimal(quantity),
        limit_price=Decimal("3500.00"),
        order_role=OrderRole.GENERIC,
        strategy_identity_id="strategy-1",
        replace_generation=0,
        source_directive_identity="directive-1",
    )


class PaperAuthorityRepairTests(unittest.TestCase):
    def test_current_exact_authority_is_checked_for_each_permission(self) -> None:
        authority = _authority(allow_order_replace=False)
        authority.require_order_submit(
            CONTRACT, at=AT, broker_identity="broker-1", account_identity="account-1"
        )
        with self.assertRaisesRegex(PermissionError, "REPLACE_NOT_AUTHORIZED"):
            authority.require_order_replace(
                at=AT, broker_identity="broker-1", account_identity="account-1"
            )
        with self.assertRaisesRegex(PermissionError, "AUTHORITY_NOT_CURRENT"):
            authority.require_connect(
                at=AT + timedelta(minutes=2),
                broker_identity="broker-1",
                account_identity="account-1",
            )

    def test_mutable_source_revocation_is_observed(self) -> None:
        source = MutablePaperAuthoritySource(_authority(), source_identity="current-file")
        source.current().require_connect(
            at=AT, broker_identity="broker-1", account_identity="account-1"
        )
        source.replace(source.current().revoked())
        with self.assertRaises(PermissionError):
            source.current().require_connect(
                at=AT, broker_identity="broker-1", account_identity="account-1"
            )


class BrokerTruthRepairTests(unittest.TestCase):
    def test_account_identity_mismatch_invalidates_truth(self) -> None:
        mirror = PaperBrokerTruthMirror(
            broker_id="broker-1", expected_account_id="account-1"
        )
        account = BrokerAccountSnapshot(
            account_id="wrong-account",
            snapshot_at=AT,
            cash_balance=Decimal("1"),
            reserved_margin=Decimal("0"),
            charged_costs=Decimal("0"),
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
            currency="CNY",
        )
        with self.assertRaisesRegex(RuntimeError, "ACCOUNT_IDENTITY_MISMATCH"):
            mirror.refresh(account=account, positions=(), orders=(), observed_at=AT)
        self.assertIsNone(mirror.account)

    def test_terminal_order_remains_reconciled_after_broker_disappearance(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(
                Path(tmp) / "orders.sqlite3", require_full_envelope=True
            )
            instruction = _instruction("1.0")
            journal.prepare(
                client_request_id="request-1", trader_identity="trader",
                wake_identity="wake", decision_identity="decision",
                intent_identity="intent", risk_identity="risk",
                concrete_contract_id=CONTRACT, instruction=instruction, prepared_at=AT,
            )
            journal.mark_attempt_started("request-1", at=AT)
            snapshot = BrokerOrderSnapshot(
                order_id="broker-order", client_request_id="request-1",
                concrete_contract_id=CONTRACT, direction=PositionDirection.LONG,
                action=OrderAction.OPEN, status="FILLED",
                requested_quantity=Decimal("1"), filled_quantity=Decimal("1.0"),
                snapshot_at=AT, order_type=OrderType.LIMIT,
                limit_price=Decimal("3500"), order_role=OrderRole.GENERIC,
                strategy_identity_id="strategy-1", client_order_id="request-1",
                replace_generation=0, source_directive_identity="directive-1",
            )
            self.assertEqual((), journal.reconcile_broker_orders((snapshot,), observed_at=AT))
            self.assertEqual(TERMINAL, journal.get("request-1").status)
            self.assertEqual((), journal.reconcile_broker_orders((), observed_at=AT))
            journal.close()


class RecoveryAndOwnershipTests(unittest.TestCase):
    def test_wake_adjudication_never_redispatches(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperWakeJournal(Path(tmp) / "wakes.sqlite3")
            journal.observe(
                wake_identity="wake", trader_identity="trader",
                concrete_contract_id=CONTRACT, bar_identity="bar",
                bar_start=AT, bar_end=AT + timedelta(minutes=5),
                observed_at=AT + timedelta(minutes=5),
            )
            journal.mark_dispatch_started(
                "wake", request_id="request", at=AT + timedelta(minutes=5)
            )
            record = journal.adjudicate_unresolved_dispatch(
                "wake", outcome="REQUEST_OCCURRED_RESULT_UNRECOVERABLE",
                evidence_identity="evidence-1", at=AT + timedelta(minutes=6),
            )
            self.assertEqual(SKIPPED, record.status)
            with self.assertRaises(RuntimeError):
                journal.mark_dispatch_started(
                    "wake", request_id="request-2", at=AT + timedelta(minutes=7)
                )
            journal.close()

    def test_state_root_has_single_process_lease(self) -> None:
        with TemporaryDirectory() as tmp:
            layout = PaperRuntimeLayout(
                state_root=tmp, trader_identity="trader",
                concrete_contract_id=CONTRACT, config_identity="config",
            )
            first = layout.acquire_lease()
            try:
                with self.assertRaises(PaperRuntimeLayoutError):
                    layout.acquire_lease()
            finally:
                first.release()


class BindingAndSourceRepairTests(unittest.TestCase):
    def test_external_candidate_composition_is_complete_and_side_effect_free(self) -> None:
        ext_contract = "SHFE.cu2406"
        ext_at = datetime(2024, 4, 10, 9, 15, tzinfo=TZ)
        session_factory_calls: list[str] = []

        class IdentityPolicy:
            def __init__(self, identity_id: str) -> None:
                self.identity_id = identity_id

            def translate(self, *args, **kwargs):
                raise AssertionError("construction/preflight must not invoke sizing policy")

            def resolve(self, *args, **kwargs):
                raise AssertionError("construction/preflight must not invoke close policy")

            def resolve_limit_price(self, *args, **kwargs):
                raise AssertionError("construction/preflight must not invoke price policy")

        sizing = IdentityPolicy("fixture-sizing")
        price = IdentityPolicy("fixture-price")
        close = IdentityPolicy("fixture-close")
        authority = PaperExecutionAuthority(
            authority_id="fixture-external-authority",
            broker_kind="TQSDK_CANDIDATE",
            account_kind="TQSDK_PAPER",
            status=PaperAuthorityStatus.ACTIVE,
            allow_connect=True,
            allow_order_submit=True,
            allow_order_cancel=True,
            allow_order_replace=True,
            broker_identity="tqsdk-paper",
            account_identity="paper-account",
            allowed_contracts=(ext_contract,),
            valid_from=ext_at - timedelta(minutes=1),
            expires_at=ext_at + timedelta(minutes=1),
        )
        authority_source = MutablePaperAuthoritySource(
            authority, source_identity="fixture-current-authority"
        )
        risk = RiskGate(RiskRuleSet(
            ruleset_id="fixture-risk",
            version="fixture-only",
            max_order_quantity=Decimal("1"),
        ))
        role = PaperToolRoleBinding(
            tool_name="TqSdk",
            role="EXTERNAL_PAPER",
            status=PaperToolRoleStatus.CANDIDATE,
            runtime_version="3.10.1",
        )
        profile = PaperActivationProfile(
            profile_id="fixture-profile",
            status=PaperActivationStatus.ACTIVE,
            execution_mode="PAPER",
            tqsdk_runtime_version="3.10.1",
            live_data_policy_identity="placeholder",
            sizing_policy_identity=sizing.identity_id,
            execution_price_policy_identity=price.identity_id,
            close_offset_policy_identity=close.identity_id,
            risk_policy_identity=risk.identity_id,
            broker_adapter_identity="placeholder",
            allowed_contracts=(ext_contract,),
        )

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_holder: dict[str, object] = {}

            def create_components(order_journal, wake_journal, context_builder):
                driver = TqSdkPaperExecutionDriver(
                    broker_id="tqsdk-paper",
                    account_identity="paper-account",
                    session_factory=lambda: session_factory_calls.append("connect"),
                    order_journal=order_journal,
                    authority=authority,
                    authority_source=authority_source,
                    close_offset_policy=close,
                    execution_price_policy=price,
                    runtime_version_provider=lambda: "3.10.1",
                    require_authoritative_facts=True,
                )
                broker = TqSdkPaperBrokerAdapter(driver=driver, authority=authority)
                source = TqSdkLiveOneMinuteSource(
                    concrete_contract_id=ext_contract,
                    session_provider=driver.market_data_session,
                )
                chain = PaperDeterministicExecutionChain(
                    strategy_identity="fixture-strategy",
                    instrument="cu2406",
                    concrete_contract_id=ext_contract,
                    bridge=JiangheExecutionBridge(sizing),
                    risk_gate=risk,
                    max_market_age_seconds=30,
                )

                class Trader:
                    identity_id = "fixture-trader-implementation"

                    def decide(self, **kwargs):
                        raise AssertionError("construction/preflight must not call trader")

                bindings = PaperExecutableBindings(
                    live_data_policy=source,
                    sizing_policy=sizing,
                    execution_price_policy=price,
                    close_offset_policy=close,
                    risk_policy=risk,
                    broker_adapter=broker,
                )
                config_holder["profile"] = PaperActivationProfile(
                    profile_id=profile.profile_id,
                    status=profile.status,
                    execution_mode=profile.execution_mode,
                    tqsdk_runtime_version=profile.tqsdk_runtime_version,
                    live_data_policy_identity=source.identity_id,
                    sizing_policy_identity=sizing.identity_id,
                    execution_price_policy_identity=price.identity_id,
                    close_offset_policy_identity=close.identity_id,
                    risk_policy_identity=risk.identity_id,
                    broker_adapter_identity=broker.identity_id,
                    allowed_contracts=(ext_contract,),
                )
                return PaperExternalComponents(
                    broker=broker,
                    source=source,
                    trader=Trader(),
                    execution_chain=chain,
                    executable_bindings=bindings,
                )

            # Exact executable identities are only available after the pure
            # component factory runs, so build once with temporary journals,
            # then bind that mechanically derived profile to the real graph.
            probe_orders = PaperOrderJournal(root / "probe-orders.sqlite3", require_full_envelope=True)
            probe_wakes = PaperWakeJournal(root / "probe-wakes.sqlite3")
            try:
                from src.paper_live_causal_context import LiveCausalContextBuilder
                probe_builder = LiveCausalContextBuilder(
                    exchange="SHFE", concrete_instrument="cu2406",
                    product="cu", calendar=_CALENDAR,
                )
                create_components(probe_orders, probe_wakes, probe_builder)
            finally:
                probe_orders.close()
                probe_wakes.close()
            exact_profile = config_holder["profile"]
            self.assertIsInstance(exact_profile, PaperActivationProfile)
            config = PaperRuntimeConfig(
                config_id="fixture-external-config",
                state_root=root / "state",
                trader_identity="fixture-trader",
                concrete_contract_id=ext_contract,
                product="cu",
                exchange="SHFE",
                tqsdk_runtime_version="3.10.1",
                broker_kind="TQSDK_CANDIDATE",
                account_kind="TQSDK_PAPER",
                account_identity="paper-account",
                activation_profile=exact_profile,
                authority=authority,
                paper_tool_role=role,
                symbol=ext_contract,
                max_source_age_seconds=30,
            )
            layout = PaperRuntimeLayout(
                state_root=config.state_root,
                trader_identity=config.trader_identity,
                concrete_contract_id=config.concrete_contract_id,
                config_identity=config.stable_identity,
            )
            factories = PaperExternalFactories(
                authority_source=authority_source,
                activation_profile=exact_profile,
                paper_tool_role=role,
                sessions=_CALENDAR,
                create_components=create_components,
            )
            controller = build_external_paper_controller(
                config=config, layout=layout, factories=factories
            )
            try:
                self.assertEqual([], session_factory_calls)
                with self.assertRaisesRegex(
                    PaperRuntimeLayoutError, "STATE_ROOT_ALREADY_OWNED"
                ):
                    build_external_paper_controller(
                        config=config, layout=layout, factories=factories
                    )
                report = controller.preflight(assessed_at=ext_at)
                self.assertFalse(report.ready)
                self.assertEqual([], session_factory_calls)
            finally:
                controller.shutdown(at=ext_at, persist_checkpoint=False)

    def test_executable_binding_mismatch_is_rejected(self) -> None:
        class Bound:
            def __init__(self, identity: str) -> None:
                self.identity_id = identity

        from src.paper_activation_profile import PaperActivationProfile, PaperActivationStatus
        profile = PaperActivationProfile(
            profile_id="p", status=PaperActivationStatus.ACTIVE,
            execution_mode="PAPER", tqsdk_runtime_version="1",
            live_data_policy_identity="live", sizing_policy_identity="size",
            execution_price_policy_identity="price", close_offset_policy_identity="close",
            risk_policy_identity="risk", broker_adapter_identity="broker",
            allowed_contracts=(CONTRACT,),
        )
        bindings = PaperExecutableBindings(
            live_data_policy=Bound("wrong"), sizing_policy=Bound("size"),
            execution_price_policy=Bound("price"), close_offset_policy=Bound("close"),
            risk_policy=Bound("risk"), broker_adapter=Bound("broker"),
        )
        with self.assertRaisesRegex(ValueError, "live_data_policy_identity"):
            bindings.require_matches(profile)

    def test_candidate_tool_role_is_distinct_from_authority(self) -> None:
        role = PaperToolRoleBinding(
            tool_name="TqSdk", role="EXTERNAL_PAPER",
            status=PaperToolRoleStatus.CANDIDATE, runtime_version="1",
        )
        self.assertEqual(PaperToolRoleStatus.CANDIDATE, role.status)
        self.assertNotEqual(role.identity_id, _authority().identity_id)

    def test_tqsdk_live_source_is_exact_and_construction_is_pure(self) -> None:
        calls = []

        class Session:
            def authoritative_update_at(self):
                return AT
            def read_recent_1m_rows(self, *, symbol, limit):
                return ()

        source = TqSdkLiveOneMinuteSource(
            concrete_contract_id=CONTRACT,
            session_provider=lambda: calls.append("session") or Session(),
        )
        self.assertEqual([], calls)
        with self.assertRaisesRegex(ValueError, "CONTRACT_MISMATCH"):
            source.read_recent_1m_rows(symbol="SHFE.cu2406", limit=1)
        self.assertEqual([], calls)


class DecisionAndCliRepairTests(unittest.TestCase):
    def test_paper_decision_preserves_normalized_jianghe_semantics(self) -> None:
        payload = {
            "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_2",
            "family": "NONE", "action": "WAIT", "direction": "NONE",
            "attention_mode": "SCAN", "decision_state": "TRIGGER_NOT_READY",
            "rationale": "无来源支持的触发", "declared_unknown": [],
            "principle_references": [], "source_references": [], "numeric_claims": [],
            "current_market_hypothesis": None, "timeframe_trend_view": [],
            "key_location_hypotheses": [], "expected_trigger": None,
            "invalidation_hypothesis": None, "open_questions": [],
        }
        normalized = JiangheResponseNormalizer().normalize(
            json.dumps(payload, ensure_ascii=False)
        )
        decision = PaperTraderDecision(
            decision_identity=normalized.identity, normalized_decision=normalized
        )
        self.assertIs(decision.normalized_decision, normalized)

    def test_external_cli_has_no_historical_contract_default(self) -> None:
        args = build_parser().parse_args(["--state-root", "state"])
        with self.assertRaisesRegex(ValueError, "--concrete-contract"):
            _config_from_args(args)

    def test_external_cli_requires_explicit_contract_before_loading_bindings(self) -> None:
        args = build_parser().parse_args([
            "--state-root", "state", "--external-run",
            "--bindings-module", "module_that_must_not_be_imported",
        ])
        with self.assertRaisesRegex(ValueError, "--concrete-contract"):
            _run_external(args)


if __name__ == "__main__":
    unittest.main()
