"""Deterministic fake PAPER activation rehearsal over the real startup surfaces.

OFFLINE ONLY. This module drives the exact same startup surfaces the future
PAPER path will use, but with deterministic fakes only: no account login, no
real TqApi session, no credentials, no DeepSeek/provider call, no order against
an external broker, no real money.

The rehearsal proves feature completion of the local single-owner PAPER startup
path:

    configuration -> persistence open -> assembly -> preflight -> fake connect
    -> broker truth -> market bootstrap -> trader ready -> new live 1m
    -> governed wake/context -> fake cognition -> fake deterministic risk/order
    plan -> journal -> fake broker -> reconciliation -> clean shutdown
    -> restart -> reopen durable state -> no duplicate old wake/order.

It reuses the existing project objects (``PaperRuntimeCoordinator`` via
``assemble_paper_runtime``, ``PaperLiveOneMinuteTransport``,
``LiveSessionCalendar`` / ``LiveCausalContextBuilder``, the durable wake/order
journals, the broker-truth mirror, the supervisor) and injects deterministic
fakes for the broker, live source, trader and risk planner.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping
from zoneinfo import ZoneInfo

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerOrderInstruction,
    BrokerOrderSnapshot,
    BrokerPositionSnapshot,
    OrderType,
)
from src.contract_semantics import OrderAction, PositionDirection
from src.paper_activation_profile import (
    PAPER_ACTIVATION_PROFILE_SCHEMA_VERSION,
    PaperActivationProfile,
    PaperActivationStatus,
)
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import (
    PAPER_EXECUTION_AUTHORITY_SCHEMA_VERSION,
    PaperAuthorityStatus,
    PaperExecutionAuthority,
)
from src.paper_live_causal_context import (
    LiveCausalContextBuilder,
    LiveSessionCalendar,
)
from src.paper_live_transport import PaperLiveOneMinuteTransport
from src.paper_offline_runtime_drill import PaperOfflineRuntimeDrill
from src.paper_order_journal import (
    BROKER_ORDER_ID_KNOWN,
    PaperOrderJournal,
)
from src.paper_runtime import (
    PaperOrderPlan,
    PaperRiskPlanner,
    PaperTrader,
    PaperTraderDecision,
)
from src.paper_runtime_assembly import PaperRuntimeAssemblyInputs, assemble_paper_runtime
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_runtime_controller import PaperRuntimeController
from src.paper_runtime_layout import PaperRuntimeLayout
from src.paper_wake_journal import DECISION_COMMITTED, PaperWakeJournal
from src.runtime_events import BrokerConnectionState

PAPER_OFFLINE_ACTIVATION_REHEARSAL_VERSION = "KPE_PAPER_OFFLINE_ACTIVATION_REHEARSAL_V0_1"

REPO_ROOT = Path(__file__).resolve().parents[1]

TZ = ZoneInfo("Asia/Shanghai")
EXCHANGE = "SHFE"
INSTRUMENT = "cu2406"
CONTRACT = "SHFE.cu2406"
PRODUCT = "cu"
TARGET_DAY = date(2024, 4, 10)
TRADER_IDENTITY = "OFFLINE_REHEARSAL_TRADER"
BROKER_ID = "OFFLINE_REHEARSAL_FAKE_BROKER"
RUNTIME_VERSION = "3.10.1"
_ONE_MINUTE = timedelta(minutes=1)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _at(hour: int, minute: int) -> datetime:
    return datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, hour, minute, tzinfo=TZ)


MORNING_UNTIL = _at(9, 15)
AT_0920 = _at(9, 20)


# --------------------------------------------------------------------------- fakes


def rehearsal_authority() -> PaperExecutionAuthority:
    """Deterministic OFFLINE_REHEARSAL-only fake authority (never project authority)."""
    return PaperExecutionAuthority(
        authority_id="OFFLINE_REHEARSAL_AUTHORITY_NOT_PROJECT_AUTHORITY",
        broker_kind="OFFLINE_REHEARSAL_FAKE",
        account_kind="OFFLINE_REHEARSAL_FAKE",
        status=PaperAuthorityStatus.ACTIVE,
        allow_connect=True,
        allow_order_submit=True,
        allow_order_cancel=True,
        allow_order_replace=True,
        allowed_contracts=(CONTRACT,),
    )


def rehearsal_profile() -> PaperActivationProfile:
    """Deterministic OFFLINE_REHEARSAL-only fake activation profile.

    All result-dependent policy bindings are present so the ACTIVE profile is
    complete; these are TEST_ONLY fakes, never a project PAPER policy.
    """
    return PaperActivationProfile(
        profile_id="OFFLINE_REHEARSAL_PROFILE_NOT_PROJECT_POLICY",
        status=PaperActivationStatus.ACTIVE,
        execution_mode="PAPER",
        tqsdk_runtime_version=RUNTIME_VERSION,
        live_data_policy_identity="OFFLINE_REHEARSAL_LIVE_POLICY",
        sizing_policy_identity="OFFLINE_REHEARSAL_SIZING_POLICY",
        execution_price_policy_identity="OFFLINE_REHEARSAL_PRICE_POLICY",
        close_offset_policy_identity="OFFLINE_REHEARSAL_OFFSET_POLICY",
        risk_policy_identity="OFFLINE_REHEARSAL_RISK_POLICY",
        broker_adapter_identity=BROKER_ID,
        allowed_contracts=(CONTRACT,),
    )


class RehearsalFakeBroker:
    """Deterministic journal-managed fake broker (offline rehearsal only)."""

    offline_test_only = True
    journal_managed_execution = True

    def __init__(self, journal: PaperOrderJournal) -> None:
        self.journal = journal
        self.state = BrokerConnectionState.DISCONNECTED
        self.at = MORNING_UNTIL
        self.orders: dict[str, BrokerOrderSnapshot] = {}
        self.submit_calls = 0
        self.cancel_calls = 0

    @property
    def broker_id(self) -> str:
        return BROKER_ID

    @property
    def order_journal(self) -> PaperOrderJournal:
        return self.journal

    @property
    def connection_state(self) -> BrokerConnectionState:
        return self.state

    def set_observed_at(self, at: datetime) -> None:
        self.at = at

    def connect(self) -> None:
        self.state = BrokerConnectionState.CONNECTED

    def disconnect(self) -> None:
        self.state = BrokerConnectionState.DISCONNECTED

    def _connected(self) -> None:
        if self.state is not BrokerConnectionState.CONNECTED:
            raise RuntimeError("OFFLINE_REHEARSAL_FAKE_BROKER_NOT_CONNECTED")

    def submit_order(self, instruction: BrokerOrderInstruction) -> str:
        self._connected()
        self.submit_calls += 1
        self.journal.mark_attempt_started(instruction.client_request_id, at=self.at)
        order_id = "broker:" + instruction.client_request_id
        self.journal.mark_broker_order_known(
            instruction.client_request_id, broker_order_id=order_id, at=self.at
        )
        self.orders[order_id] = BrokerOrderSnapshot(
            order_id=order_id,
            client_request_id=instruction.client_request_id,
            concrete_contract_id=instruction.concrete_contract_id,
            direction=instruction.direction,
            action=instruction.action,
            status="LIVE",
            requested_quantity=instruction.quantity,
            filled_quantity=Decimal("0"),
            snapshot_at=self.at,
            order_type=instruction.order_type,
            limit_price=instruction.limit_price,
            trigger_price=instruction.trigger_price,
            order_role=instruction.order_role,
            strategy_identity_id=instruction.strategy_identity_id,
            client_order_id=instruction.client_order_id or instruction.client_request_id,
            parent_order_id=instruction.parent_order_id,
            oco_group_id=instruction.oco_group_id,
            replace_generation=instruction.replace_generation,
            source_directive_identity=instruction.source_directive_identity,
        )
        return order_id

    def cancel_order(self, order_id: str) -> None:
        self._connected()
        self.cancel_calls += 1
        operation = self.journal.prepare_cancel_for_broker_order(order_id, at=self.at)
        self.journal.mark_cancel_attempt_started(operation.cancel_operation_id, at=self.at)
        current = self.orders[order_id]
        self.orders[order_id] = BrokerOrderSnapshot(
            order_id=current.order_id,
            client_request_id=current.client_request_id,
            concrete_contract_id=current.concrete_contract_id,
            direction=current.direction,
            action=current.action,
            status="CANCELLED",
            requested_quantity=current.requested_quantity,
            filled_quantity=current.filled_quantity,
            snapshot_at=self.at,
            order_type=current.order_type,
            limit_price=current.limit_price,
            trigger_price=current.trigger_price,
            order_role=current.order_role,
            strategy_identity_id=current.strategy_identity_id,
            client_order_id=current.client_order_id,
            parent_order_id=current.parent_order_id,
            oco_group_id=current.oco_group_id,
            replace_generation=current.replace_generation,
            source_directive_identity=current.source_directive_identity,
        )

    def fetch_account_snapshot(self) -> BrokerAccountSnapshot:
        self._connected()
        return BrokerAccountSnapshot(
            account_id="OFFLINE_REHEARSAL_FAKE_ACCOUNT",
            snapshot_at=self.at,
            cash_balance=Decimal("100000"),
            reserved_margin=Decimal("0"),
            charged_costs=Decimal("0"),
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
            currency="CNY",
        )

    def fetch_position_snapshot(self) -> tuple[BrokerPositionSnapshot, ...]:
        self._connected()
        return ()

    def fetch_order_snapshot(self) -> tuple[BrokerOrderSnapshot, ...]:
        self._connected()
        return tuple(sorted(self.orders.values(), key=lambda item: item.order_id))

    def capture_broker_truth(self) -> tuple[BrokerOrderSnapshot, ...]:
        """Independent fake-broker persistence; never derives from project state."""
        return tuple(sorted(self.orders.values(), key=lambda item: item.order_id))

    def restore_broker_truth(self, orders: tuple[BrokerOrderSnapshot, ...]) -> None:
        if any(not isinstance(item, BrokerOrderSnapshot) for item in orders):
            raise ValueError("fake broker truth requires broker snapshots")
        if len({item.order_id for item in orders}) != len(orders):
            raise ValueError("fake broker truth contains duplicate order ids")
        self.orders = {item.order_id: item for item in orders}


class RehearsalFakeTrader(PaperTrader):
    """Deterministic fake cognition: one committed decision per wake."""

    def __init__(self) -> None:
        self.calls = 0

    def decide(self, *, wake, context) -> PaperTraderDecision:
        self.calls += 1
        return PaperTraderDecision(decision_identity="rehearsal-decision:" + wake.wake_identity)


class RehearsalFakeRiskPlanner(PaperRiskPlanner):
    """Deterministic fake risk/order plan (TEST_ONLY fixed lot/price)."""

    def plan(self, *, wake, context, decision) -> PaperOrderPlan:
        request_id = "request:" + wake.bar.end.strftime("%Y%m%dT%H%M")
        return PaperOrderPlan(
            intent_identity="rehearsal-intent:" + request_id,
            risk_identity="rehearsal-risk:" + request_id,
            instruction=BrokerOrderInstruction(
                client_request_id=request_id,
                concrete_contract_id=CONTRACT,
                direction=PositionDirection.LONG,
                action=OrderAction.OPEN,
                order_type=OrderType.LIMIT,
                quantity=Decimal("1"),
                limit_price=Decimal("70000"),
                strategy_identity_id="OFFLINE_REHEARSAL_ONLY",
                source_directive_identity=wake.wake_identity,
            ),
        )


class RehearsalLiveSource:
    """Deterministic injected TqSdk-like live 1m source (offline rehearsal)."""

    def __init__(self, rows: tuple[Mapping[str, object], ...]) -> None:
        self._rows = list(rows)
        self.connected = True
        self.read_calls = 0

    def last_activity_at(self) -> datetime | None:
        return MORNING_UNTIL

    def read_recent_1m_rows(self, *, symbol: str, limit: int) -> tuple[Mapping[str, object], ...]:
        self.read_calls += 1
        return tuple(self._rows[-limit:])

    def extend(self, rows: tuple[Mapping[str, object], ...]) -> None:
        self._rows.extend(rows)


# ------------------------------------------------------------- canonical authority


def load_calendar_authority():
    """Load canonical trading-calendar + session-schedule authority (read-only)."""
    calendar_payload = json.loads(
        (REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json").read_text(encoding="utf-8")
    )
    session_payload = json.loads(
        (REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json").read_text(encoding="utf-8")
    )
    trading_calendar = tuple(
        date.fromisoformat(item)
        for year in sorted(calendar_payload["trading_days"])
        for item in calendar_payload["trading_days"][year]
    )
    night_closed = frozenset(
        date.fromisoformat(item)
        for values in calendar_payload["night_closed_trading_days"].values()
        for item in values
    )
    return trading_calendar, night_closed, session_payload["products"]


def build_rehearsal_calendar() -> LiveSessionCalendar:
    trading_calendar, night_closed, sessions = load_calendar_authority()
    return LiveSessionCalendar(
        product=PRODUCT,
        trading_calendar=trading_calendar,
        night_closed_days=night_closed,
        session_schedule=sessions,
    )


def _ns(value: datetime) -> int:
    return int(value.timestamp() * 1_000_000_000)


def _row_for_minute(start: datetime, *, symbol: str = INSTRUMENT) -> Mapping[str, object]:
    base = Decimal("70000") + Decimal(start.minute % 60)
    return {
        "datetime": _ns(start),
        "symbol": symbol,
        "open": str(base),
        "high": str(base + Decimal("2")),
        "low": str(base - Decimal("2")),
        "close": str(base + Decimal("1")),
        "volume": "3",
    }


def _prior_days(calendar: LiveSessionCalendar, count: int = 3) -> tuple[date, ...]:
    return tuple(day for day in calendar.trading_days if day < TARGET_DAY)[-count:]


def _rows_for_days(calendar: LiveSessionCalendar, days, *, until: datetime | None = None):
    rows: list[Mapping[str, object]] = []
    for day in days:
        for window in calendar.session_windows_for(day):
            cursor = window.start
            while cursor < window.end:
                if until is not None and cursor >= until:
                    break
                rows.append(_row_for_minute(cursor))
                cursor += _ONE_MINUTE
    return tuple(rows)


def _history_rows(calendar: LiveSessionCalendar, until: datetime | None = None):
    days = _prior_days(calendar, 3) + (TARGET_DAY,)
    return _rows_for_days(calendar, days, until=until)


# ------------------------------------------------------------------ rehearsal run


@dataclass(frozen=True)
class OfflineActivationRehearsalResult:
    passed: bool
    steps: tuple[tuple[str, str], ...]  # (step, PASS/FAIL)
    checks: tuple[str, ...]
    wake_count_after_restart: int
    order_count_after_restart: int
    identity: str

    def public_lines(self) -> tuple[str, ...]:
        return (
            f"PAPER_OFFLINE_REHEARSAL_SCHEMA={PAPER_OFFLINE_ACTIVATION_REHEARSAL_VERSION}",
            f"PAPER_OFFLINE_REHEARSAL_PASSED={'YES' if self.passed else 'NO'}",
            *(
                f"PAPER_OFFLINE_REHEARSAL_STEP_{step}={status}"
                for step, status in self.steps
            ),
            *self.checks,
            f"PAPER_OFFLINE_REHEARSAL_IDENTITY={self.identity}",
        )


def _step(name: str, ok: bool) -> tuple[str, str]:
    return (name, "PASS" if ok else "FAIL")


def run_offline_activation_rehearsal(
    *,
    state_root: str | Path,
    config: PaperRuntimeConfig | None = None,
) -> OfflineActivationRehearsalResult:
    """Run the deterministic fake activation rehearsal end-to-end (offline).

    Uses the same startup surfaces as the future PAPER path: configuration,
    persistence open, assembly, preflight, fake connect, broker truth, market
    bootstrap, trader ready, new live 1m, governed wake/context, fake
    cognition, fake deterministic risk/order plan, journal, fake broker,
    reconciliation, clean shutdown, restart, reopen durable state and no
    duplicate old wake/order. No real account, order, provider or credential
    action occurs.
    """
    steps: list[tuple[str, str]] = []
    checks: list[str] = []

    if config is None:
        config = PaperRuntimeConfig(
            config_id="OFFLINE_REHEARSAL_CONFIG",
            state_root=state_root,
            trader_identity=TRADER_IDENTITY,
            concrete_contract_id=CONTRACT,
            product=PRODUCT,
            exchange=EXCHANGE,
            tqsdk_runtime_version=RUNTIME_VERSION,
            broker_kind="OFFLINE_REHEARSAL_FAKE",
            account_kind="OFFLINE_REHEARSAL_FAKE",
            activation_profile=rehearsal_profile(),
            authority=rehearsal_authority(),
            symbol=INSTRUMENT,
        )

    layout = PaperRuntimeLayout(
        state_root=config.state_root,
        trader_identity=config.trader_identity,
        concrete_contract_id=config.concrete_contract_id,
        config_identity=config.stable_identity,
    )

    # 1. configuration
    steps.append(_step("CONFIGURATION", config.activation_profile is not None and config.authority is not None))

    # 2. persistence open
    try:
        layout.ensure_initialized()
        layout.reopen()
        steps.append(_step("PERSISTENCE_OPEN", True))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("PERSISTENCE_OPEN", False))
        checks.append("PERSISTENCE_OPEN_ERROR=" + type(error).__name__)

    order_journal = PaperOrderJournal(layout.order_journal_path)
    wake_journal = PaperWakeJournal(layout.wake_journal_path)
    mirror = PaperBrokerTruthMirror(broker_id=BROKER_ID)
    calendar = build_rehearsal_calendar()
    builder = LiveCausalContextBuilder(
        exchange=EXCHANGE, concrete_instrument=INSTRUMENT, product=PRODUCT, calendar=calendar
    )

    # 3. assembly
    broker = RehearsalFakeBroker(order_journal)
    source = RehearsalLiveSource(_history_rows(calendar, until=MORNING_UNTIL))
    trader = RehearsalFakeTrader()
    planner = RehearsalFakeRiskPlanner()
    try:
        assembly = assemble_paper_runtime(
            PaperRuntimeAssemblyInputs(
                trader_identity=config.trader_identity,
                concrete_contract_id=config.concrete_contract_id,
                exchange=EXCHANGE,
                product=PRODUCT,
                actual_tqsdk_runtime_version=RUNTIME_VERSION,
                authority=config.authority,
                activation_profile=config.activation_profile,
                sessions=calendar,
                context_builder=builder,
                wake_journal=wake_journal,
                order_journal=order_journal,
                broker_mirror=mirror,
                broker=broker,
                trader=trader,
                risk_planner=planner,
                source=source,
                symbol=INSTRUMENT,
            )
        )
        steps.append(_step("ASSEMBLY", True))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("ASSEMBLY", False))
        checks.append("ASSEMBLY_ERROR=" + type(error).__name__)
        _close_safe(order_journal, wake_journal)
        return _finish(steps, checks)

    controller = PaperRuntimeController(config=config, layout=layout, assembly=assembly)

    # 4. preflight (offline-rehearsal mode may pass with fakes)
    try:
        report = controller.preflight(mode="OFFLINE_REHEARSAL")
        steps.append(_step("PREFLIGHT", report.ready))
        checks.append(f"PREFLIGHT_OVERALL={report.overall}")
    except Exception as error:  # noqa: BLE001
        steps.append(_step("PREFLIGHT", False))
        checks.append("PREFLIGHT_ERROR=" + type(error).__name__)

    # 5. fake connect -> broker truth/reconciliation
    try:
        broker.set_observed_at(MORNING_UNTIL)
        assessment = controller.connect(at=MORNING_UNTIL)
        steps.append(_step("FAKE_CONNECT", assessment.can_connect))
        checks.append(f"CONNECT_BLOCKERS={','.join(assessment.connect_blockers) or 'NONE'}")
    except Exception as error:  # noqa: BLE001
        steps.append(_step("FAKE_CONNECT", False))
        checks.append("CONNECT_ERROR=" + type(error).__name__)

    # 6. market bootstrap
    try:
        controller.bootstrap(observed_at=MORNING_UNTIL)
        steps.append(_step("MARKET_BOOTSTRAP", controller.coordinator.market_bootstrapped))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("MARKET_BOOTSTRAP", False))
        checks.append("BOOTSTRAP_ERROR=" + type(error).__name__)

    # 7. trader ready
    controller.mark_trader_ready(True)
    steps.append(_step("TRADER_READY", controller.coordinator.trader_runtime_ready))

    # 8. new live 1m -> governed wake/context -> fake cognition -> fake risk/order
    #    plan -> journal -> fake broker -> reconciliation
    try:
        broker.set_observed_at(AT_0920)
        source.extend(_history_rows(calendar, until=AT_0920))
        result = controller.poll(observed_at=AT_0920)
        wake_results = tuple(result.consumer_result or ())
        steps.append(_step("NEW_LIVE_1M_WAKE", len(wake_results) == 1))
        checks.append(f"WAKE_RESULTS={len(wake_results)}")
        checks.append(f"TRADER_CALLS={trader.calls}")
        checks.append(f"BROKER_SUBMITS={broker.submit_calls}")
        checks.append(f"ORDER_KNOWN={1 if wake_results and wake_results[0].broker_order_id else 0}")
        steps.append(_step("JOURNAL_WAKE", bool(wake_journal.get(wake_results[0].wake_identity).status == DECISION_COMMITTED) if wake_results else False))
        steps.append(_step(
            "JOURNAL_ORDER",
            bool(order_journal.get(wake_results[0].client_request_id).status == BROKER_ORDER_ID_KNOWN)
            if wake_results and wake_results[0].client_request_id else False,
        ))
        steps.append(_step("RECONCILIATION", not order_journal.recovery_blockers()))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("NEW_LIVE_1M_WAKE", False))
        checks.append("WAKE_DRIVE_ERROR=" + type(error).__name__)

    # Preserve independently authoritative fake-broker truth before process
    # restart.  The project journal is deliberately not consulted.
    broker_truth_at_restart = broker.capture_broker_truth()

    # 9. clean shutdown
    try:
        controller.shutdown(at=AT_0920, persist_checkpoint=True)
        steps.append(_step("CLEAN_SHUTDOWN", controller.closed and layout.causal_checkpoint_path.exists()))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("CLEAN_SHUTDOWN", False))
        checks.append("SHUTDOWN_ERROR=" + type(error).__name__)

    # 10. restart -> reopen durable state (layout + journals + checkpoint)
    wake_before = _journal_wake_count(layout)
    order_before = _journal_order_count(layout)
    try:
        layout.reopen()
        steps.append(_step("RESTART_REOPEN_LAYOUT", True))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("RESTART_REOPEN_LAYOUT", False))
        checks.append("RESTART_REOPEN_ERROR=" + type(error).__name__)

    try:
        checkpoint = layout.read_causal_checkpoint()
        restored = LiveCausalContextBuilder.from_checkpoint(checkpoint, calendar=calendar)
        steps.append(_step("RESTORE_CHECKPOINT", restored.bootstrap_done))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("RESTORE_CHECKPOINT", False))
        checks.append("CHECKPOINT_RESTORE_ERROR=" + type(error).__name__)

    # 11. re-open journals (restart must reopen durable state, never wipe)
    try:
        order_journal2 = PaperOrderJournal(layout.order_journal_path)
        wake_journal2 = PaperWakeJournal(layout.wake_journal_path)
        steps.append(_step("RESTART_REOPEN_JOURNALS", True))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("RESTART_REOPEN_JOURNALS", False))
        checks.append("RESTART_JOURNAL_ERROR=" + type(error).__name__)
        _close_safe(order_journal, wake_journal)
        return _finish(steps, checks)

    # 12. re-assemble + re-activate after restart
    mirror2 = PaperBrokerTruthMirror(broker_id=BROKER_ID)
    broker2 = RehearsalFakeBroker(order_journal2)
    source2 = RehearsalLiveSource(_history_rows(calendar, until=MORNING_UNTIL))
    trader2 = RehearsalFakeTrader()
    planner2 = RehearsalFakeRiskPlanner()
    try:
        assembly2 = assemble_paper_runtime(
            PaperRuntimeAssemblyInputs(
                trader_identity=config.trader_identity,
                concrete_contract_id=config.concrete_contract_id,
                exchange=EXCHANGE,
                product=PRODUCT,
                actual_tqsdk_runtime_version=RUNTIME_VERSION,
                authority=config.authority,
                activation_profile=config.activation_profile,
                sessions=calendar,
                context_builder=restored,
                wake_journal=wake_journal2,
                order_journal=order_journal2,
                broker_mirror=mirror2,
                broker=broker2,
                trader=trader2,
                risk_planner=planner2,
                source=source2,
                symbol=INSTRUMENT,
            )
        )
        controller2 = PaperRuntimeController(config=config, layout=layout, assembly=assembly2)
        steps.append(_step("RESTART_ASSEMBLY", True))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("RESTART_ASSEMBLY", False))
        checks.append("RESTART_ASSEMBLY_ERROR=" + type(error).__name__)
        _close_safe(order_journal2, wake_journal2, order_journal, wake_journal)
        return _finish(steps, checks)

    broker2.set_observed_at(AT_0920)
    broker2.restore_broker_truth(broker_truth_at_restart)
    controller2.connect(at=AT_0920)
    controller2.bootstrap(observed_at=MORNING_UNTIL)
    controller2.mark_trader_ready(True)

    # 13. feed the SAME new minutes again after restart -> no duplicate old wake/order
    broker2.set_observed_at(AT_0920)
    source2.extend(_history_rows(calendar, until=AT_0920))
    try:
        result2 = controller2.poll(observed_at=AT_0920)
        wake_results2 = tuple(result2.consumer_result or ())
        checks.append(f"RESTART_WAKE_RESULTS={len(wake_results2)}")
        checks.append(f"RESTART_TRADER_CALLS={trader2.calls}")
        checks.append(f"RESTART_BROKER_SUBMITS={broker2.submit_calls}")
        no_dup = len(wake_results2) == 0 and trader2.calls == 0 and broker2.submit_calls == 0
        steps.append(_step("NO_DUPLICATE_WAKE_ORDER", no_dup))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("NO_DUPLICATE_WAKE_ORDER", False))
        checks.append("RESTART_DUPLICATE_ERROR=" + type(error).__name__)

    # 14. restart preserved durable state
    wake_after = _journal_wake_count(layout)
    order_after = _journal_order_count(layout)
    preserved = wake_after == wake_before and order_after == order_before and wake_after >= 1 and order_after >= 1
    steps.append(_step("RESTART_PRESERVES_STATE", preserved))
    checks.append(f"WAKE_COUNT_BEFORE={wake_before}")
    checks.append(f"WAKE_COUNT_AFTER={wake_after}")
    checks.append(f"ORDER_COUNT_BEFORE={order_before}")
    checks.append(f"ORDER_COUNT_AFTER={order_after}")

    # 15. graceful shutdown after restart
    try:
        controller2.shutdown(at=AT_0920, persist_checkpoint=True)
        steps.append(_step("RESTART_SHUTDOWN", controller2.closed))
    except Exception as error:  # noqa: BLE001
        steps.append(_step("RESTART_SHUTDOWN", False))
        checks.append("RESTART_SHUTDOWN_ERROR=" + type(error).__name__)

    _close_safe(order_journal2, wake_journal2, order_journal, wake_journal)

    passed = all(status == "PASS" for _, status in steps)
    return OfflineActivationRehearsalResult(
        passed=passed,
        steps=tuple(steps),
        checks=tuple(checks),
        wake_count_after_restart=wake_after,
        order_count_after_restart=order_after,
        identity=_hash({
            "schema_version": PAPER_OFFLINE_ACTIVATION_REHEARSAL_VERSION,
            "passed": passed,
            "steps": list(steps),
            "checks": list(checks),
        }),
    )


def _journal_wake_count(layout: PaperRuntimeLayout) -> int:
    journal = PaperWakeJournal(layout.wake_journal_path)
    try:
        return journal.total_count()
    finally:
        journal.close()


def _journal_order_count(layout: PaperRuntimeLayout) -> int:
    journal = PaperOrderJournal(layout.order_journal_path)
    try:
        return journal.total_count()
    finally:
        journal.close()


def _close_safe(*journals: object) -> None:
    for journal in journals:
        if journal is None:
            continue
        close = getattr(journal, "close", None)
        if callable(close):
            try:
                close()
            except Exception:  # noqa: BLE001
                pass


def _finish(steps: list[tuple[str, str]], checks: list[str]) -> OfflineActivationRehearsalResult:
    passed = all(status == "PASS" for _, status in steps)
    return OfflineActivationRehearsalResult(
        passed=passed,
        steps=tuple(steps),
        checks=tuple(checks),
        wake_count_after_restart=0,
        order_count_after_restart=0,
        identity=_hash({
            "schema_version": PAPER_OFFLINE_ACTIVATION_REHEARSAL_VERSION,
            "passed": passed,
            "steps": list(steps),
            "checks": list(checks),
        }),
    )


__all__ = [
    "AT_0920",
    "BROKER_ID",
    "CONTRACT",
    "EXCHANGE",
    "INSTRUMENT",
    "MORNING_UNTIL",
    "OfflineActivationRehearsalResult",
    "PAPER_OFFLINE_ACTIVATION_REHEARSAL_VERSION",
    "PRODUCT",
    "RehearsalFakeBroker",
    "RehearsalFakeRiskPlanner",
    "RehearsalFakeTrader",
    "RehearsalLiveSource",
    "TRADER_IDENTITY",
    "build_rehearsal_calendar",
    "load_calendar_authority",
    "rehearsal_authority",
    "rehearsal_profile",
    "run_offline_activation_rehearsal",
]
