"""TEST_ONLY synthetic fixtures for the Shadow Runtime Foundation tests.

Synthetic only: no real broker, no network, no canonical market corpus, no
candidate strategy outcome, no real money. Fake strategies here are TEST_ONLY
and must never be used for candidate performance.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.contract_semantics import (
    ContractSpecification,
    PositionDirection,
)
from src.data_substrate import BarQuality, CompletedBar
from src.historical_data import NormalizedHistoricalBar
from src.intent import IntentAction, StrategyIntent
from src.market_context import MarketContext
from src.paper_broker import PaperFillPolicy
from src.risk_gate import RiskRuleSet
from src.shadow_runtime import RuntimeConfiguration
from src.trading_state import RuntimeAccountingAssumptions

TZ = ZoneInfo("Asia/Shanghai")

TEST_EXCHANGE = "TEST"
TEST_PRODUCT = "TST"
TEST_INSTRUMENT = "TEST.IF9999"
TEST_MULTIPLIER = Decimal("300")
TEST_TICK = Decimal("0.2")
TEST_STRATEGY_ID = "test-only-fake-strategy-v1"
TEST_TRADING_DAY = date(2024, 6, 17)

DEFAULT_STARTING_CAPITAL = Decimal("1000000")


def make_contract_spec(
    instrument: str = TEST_INSTRUMENT,
    *,
    multiplier: Decimal = TEST_MULTIPLIER,
    tick: Decimal = TEST_TICK,
) -> ContractSpecification:
    return ContractSpecification(
        exchange=TEST_EXCHANGE,
        product_family=TEST_PRODUCT,
        instrument_id=instrument,
        listed_at=datetime(2024, 1, 1, tzinfo=TZ),
        deactivated_at=datetime(2030, 1, 1, tzinfo=TZ),
        contract_multiplier=multiplier,
        minimum_price_tick=tick,
        currency="CNY",
        unit="lot",
        price_limit_rule_identity="price-limit-fixture-v1",
        offset_fee_metadata_identity="offset-fee-fixture-v1",
        metadata_version="v1",
    )


def make_bar(
    index: int,
    price: Decimal,
    *,
    session_start: datetime | None = None,
    interval: timedelta = timedelta(minutes=1),
) -> NormalizedHistoricalBar:
    """Deterministic completed bar starting at ``session_start + index*interval``."""
    start = session_start if session_start is not None else datetime(2024, 6, 17, 9, 0, tzinfo=TZ)
    bar_start = start + index * interval
    bar_end = bar_start + interval
    return NormalizedHistoricalBar(
        exchange=TEST_EXCHANGE,
        concrete_instrument=TEST_INSTRUMENT,
        source_event_at=bar_end,
        source_retrieved_at=bar_end,
        completed_bar=CompletedBar(
            instrument=TEST_INSTRUMENT,
            trading_day=bar_start.date(),
            start=bar_start,
            end=bar_end,
            available_at=bar_end,
            quality=BarQuality(partial=False, reconnect_gap=False),
        ),
        open=price,
        high=price + Decimal("2"),
        low=price - Decimal("2"),
        close=price,
        volume=Decimal("100"),
        open_interest_start=None,
        open_interest_end=None,
        raw_artifact_identity_id="raw-fixture-v1",
        data_version_id="data-fixture-v1",
    )


def make_accounting(
    *,
    initial_margin_rate: Decimal = Decimal("0.10"),
    maintenance_margin_rate: Decimal = Decimal("0.05"),
    additive_cost_per_fill: Decimal = Decimal("5"),
) -> RuntimeAccountingAssumptions:
    return RuntimeAccountingAssumptions(
        model_version="fixture-v1",
        initial_margin_rate=initial_margin_rate,
        maintenance_margin_rate=maintenance_margin_rate,
        additive_cost_per_fill=additive_cost_per_fill,
        currency="CNY",
    )


def make_ruleset(
    *,
    max_order_quantity: Decimal | None = Decimal("10"),
    max_position_quantity: Decimal | None = Decimal("10"),
    max_open_positions: int | None = 3,
    allow_opposite_direction_flip: bool = False,
    allow_open_when_disconnected: bool = False,
    allow_open_when_stale: bool = False,
) -> RiskRuleSet:
    return RiskRuleSet(
        ruleset_id="fixture-rules-v1",
        version="1",
        max_order_quantity=max_order_quantity,
        max_position_quantity=max_position_quantity,
        max_open_positions=max_open_positions,
        allow_opposite_direction_flip=allow_opposite_direction_flip,
        allow_open_when_disconnected=allow_open_when_disconnected,
        allow_open_when_stale=allow_open_when_stale,
    )


def make_config(
    *,
    runtime_id: str = "fixture-runtime",
    runtime_version: str = "v1",
    starting_capital: Decimal = DEFAULT_STARTING_CAPITAL,
    contract_specs: tuple[ContractSpecification, ...] = (make_contract_spec(),),
    accounting: RuntimeAccountingAssumptions | None = None,
    risk_ruleset: RiskRuleSet | None = None,
    staleness_threshold: timedelta = timedelta(minutes=5),
    fill_policy: PaperFillPolicy = PaperFillPolicy.IMMEDIATE_MARKET_AT_REFERENCE,
    broker_id: str = "paper-broker-fixture",
) -> RuntimeConfiguration:
    return RuntimeConfiguration(
        runtime_id=runtime_id,
        runtime_version=runtime_version,
        timezone="Asia/Shanghai",
        starting_capital=starting_capital,
        contract_specs=contract_specs,
        accounting=accounting if accounting is not None else make_accounting(),
        risk_ruleset=risk_ruleset if risk_ruleset is not None else make_ruleset(),
        staleness_threshold=staleness_threshold,
        broker_id=broker_id,
        fill_policy=fill_policy,
    )


def intent_from(
    context: MarketContext,
    *,
    action: IntentAction,
    direction: PositionDirection | None = None,
    quantity: Decimal | None = None,
    marker: str = "open-long",
) -> StrategyIntent:
    return StrategyIntent(
        intent_id=f"{marker}-{context.bar_identity}",
        strategy_identity_id=TEST_STRATEGY_ID,
        instrument=context.instrument,
        concrete_contract_id=context.concrete_contract_id,
        action=action,
        decision_at=context.observed_at,
        context_identity=context.identity_id,
        direction=direction,
        quantity=quantity,
        reason="TEST_ONLY fake strategy",
    )


class ScriptedStrategy:
    """TEST_ONLY: emits a deterministic script of intents per bar index."""

    def __init__(self, script: tuple[tuple[IntentAction, PositionDirection | None, Decimal | None], ...]):
        self._script = script
        self._seen = 0

    def intents(self, context: MarketContext) -> tuple[StrategyIntent, ...]:
        if self._seen >= len(self._script):
            self._seen += 1
            return ()
        action, direction, quantity = self._script[self._seen]
        self._seen += 1
        if action is IntentAction.HOLD:
            return (intent_from(context, action=action, marker=f"hold-{self._seen}"),)
        return (
            intent_from(
                context,
                action=action,
                direction=direction,
                quantity=quantity,
                marker=f"{action.value.lower()}-{self._seen}",
            ),
        )


class OpenLongStrategy:
    """TEST_ONLY: open LONG 1 on every bar."""

    def intents(self, context: MarketContext) -> tuple[StrategyIntent, ...]:
        return (
            intent_from(
                context,
                action=IntentAction.OPEN,
                direction=PositionDirection.LONG,
                quantity=Decimal("1"),
                marker="open-long",
            ),
        )


class OpenThenCloseStrategy:
    """TEST_ONLY: bar 0 opens LONG 1; bar 1 closes the whole LONG position.

    ``start_index`` lets a rebuilt runtime continue a script that already
    processed earlier bars (restart recovery).
    """

    def __init__(self, start_index: int = 0) -> None:
        self._bar_index = start_index

    def intents(self, context: MarketContext) -> tuple[StrategyIntent, ...]:
        if self._bar_index == 0:
            self._bar_index += 1
            return (
                intent_from(
                    context,
                    action=IntentAction.OPEN,
                    direction=PositionDirection.LONG,
                    quantity=Decimal("1"),
                    marker="open-0",
                ),
            )
        self._bar_index += 1
        return (
            intent_from(
                context,
                action=IntentAction.CLOSE,
                direction=PositionDirection.LONG,
                quantity=None,
                marker="close-1",
            ),
        )


class NoopStrategy:
    """TEST_ONLY: emits no intents."""

    def intents(self, context: MarketContext) -> tuple[StrategyIntent, ...]:
        return ()


class ConflictStrategy:
    """TEST_ONLY: emits two conflicting OPEN intents for the same contract."""

    def intents(self, context: MarketContext) -> tuple[StrategyIntent, ...]:
        return (
            intent_from(
                context,
                action=IntentAction.OPEN,
                direction=PositionDirection.LONG,
                quantity=Decimal("1"),
                marker="conflict-a",
            ),
            intent_from(
                context,
                action=IntentAction.OPEN,
                direction=PositionDirection.LONG,
                quantity=Decimal("2"),
                marker="conflict-b",
            ),
        )


def run_bars(runtime, bar_count: int, prices: list[Decimal]) -> list:
    """Run ``bar_count`` deterministic bars through a runtime; returns results."""
    results = []
    for index in range(bar_count):
        results.append(runtime.on_completed_bar(make_bar(index, prices[index])))
    return results
