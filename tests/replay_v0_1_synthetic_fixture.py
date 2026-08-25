"""TEST_ONLY synthetic fixture for replay V0.1 lifecycle tests.

Synthetic only: no real broker, no network, no canonical market corpus, no
provider call, no outcome data.  Prices are arbitrary fixtures used only to
exercise the mechanical lifecycle; they carry no trading meaning.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path

from src.jianghe_ai_trader import (
    JiangheAITraderIdentity,
    ObservationBar,
    ReplayClock,
)
from src.jianghe_canon_retrieval import JiangheCanonRetriever
from src.jianghe_trading_only_prompt import TRADING_ONLY_PROMPT_CONTRACT
from src.persistent_deepseek_runtime import (
    CURRENT_MODEL,
    DeepSeekHarnessRuntimeContract,
    PersistentDeepSeekTraderPrototype,
    ProjectToolRegistry,
)
from src.persistent_trader_store import PersistentTraderStore
from src.replay_v0_1_orchestrator import GovernedWakeStep, RuntimeFactory
from src.replay_v0_1_runtime import ReplayV01Runtime
from src.replay_v0_1_selector import (
    ReplayMappingFact,
    ReplayPartitionFact,
    select_v0_1_slice,
)

TZ = timezone.utc
DURATIONS = {
    "4H": timedelta(hours=4),
    "1H": timedelta(hours=1),
    "15m": timedelta(minutes=15),
    "5m": timedelta(minutes=5),
}
ACTIVE_TIMEFRAMES = ("4H", "1H", "15m", "5m")
CANON_PATH = "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md"


def valid_response(
    *,
    action: str = "WAIT",
    direction: str = "NONE",
    attention_mode: str = "SCAN",
    family: str = "NONE",
    decision_state: str = "wait_for_better_location",
) -> str:
    return json.dumps(
        {
            "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_1",
            "family": family,
            "action": action,
            "direction": direction,
            "attention_mode": attention_mode,
            "decision_state": decision_state,
            "rationale": "Synthetic governed V0.1 decision.",
            "declared_unknown": [],
            "principle_references": [],
            "source_references": [],
            "numeric_claims": [],
        },
        ensure_ascii=False,
    )


def make_bar(
    timeframe: str,
    close_time: datetime,
    price: float,
    *,
    is_closed: bool = True,
) -> ObservationBar:
    duration = DURATIONS[timeframe]
    open_time = close_time - duration
    return ObservationBar(
        timeframe=timeframe,
        open_time=open_time,
        close_time=close_time,
        available_at=close_time,
        open_price=str(price),
        high_price=str(round(price + 2, 2)),
        low_price=str(round(price - 2, 2)),
        close_price=str(price),
        volume="1000",
        is_closed=is_closed,
    )


def _latest_grid_close(decision_time: datetime, minutes: int) -> datetime:
    aligned = decision_time.replace(minute=(decision_time.minute // minutes) * minutes, second=0, microsecond=0)
    if aligned > decision_time:
        aligned -= timedelta(minutes=minutes)
    return aligned


def build_session_steps(
    *,
    trading_day: date,
    session_identity: str,
    start: datetime,
    count: int = 8,
    base_price: float = 100.0,
) -> tuple[GovernedWakeStep, ...]:
    """Build a governed session of 5m wakes with causal 4H/1H/15m/5m context."""
    steps: list[GovernedWakeStep] = []
    session_5m_bars: list[ObservationBar] = []
    for index in range(count):
        close = start + timedelta(minutes=5 * (index + 1))
        wake_bar = make_bar("5m", close, base_price + index)
        session_5m_bars.append(wake_bar)
        context = list(session_5m_bars)
        context.append(make_bar("15m", _latest_grid_close(close, 15), base_price))
        context.append(make_bar("1H", _latest_grid_close(close, 60), base_price))
        context.append(make_bar("4H", _latest_grid_close(close, 240), base_price))
        steps.append(
            GovernedWakeStep(
                trading_day=trading_day,
                session_identity=session_identity,
                wake_bar=wake_bar,
                context_bars=tuple(context),
            )
        )
    return tuple(steps)


def build_slice() -> object:
    calendar = [date(2024, 1, 2) + timedelta(days=index) for index in range(70)]
    mappings = tuple(
        ReplayMappingFact("cu", calendar[index], "SHFE.cu2405", f"map-cu-{index}")
        for index in range(20, 42)
    )
    partitions = tuple(
        ReplayPartitionFact(
            "cu", "SHFE.cu2405", calendar[index], f"part-cu-{index}", f"session-{index}"
        )
        for index in range(70)
    )
    return select_v0_1_slice(trading_calendar=calendar, mappings=mappings, partitions=partitions)


def _identity() -> JiangheAITraderIdentity:
    return JiangheAITraderIdentity(
        knowledge_pack_identity="knowledge-v1",
        primary_branch_registry_identity="primary-v1",
        interpretation_set_identity="interpretation-v1",
        model_provider="deepseek",
        model_id_version=CURRENT_MODEL,
        system_prompt_identity=TRADING_ONLY_PROMPT_CONTRACT.system_prompt_sha256,
        decision_prompt_identity=TRADING_ONLY_PROMPT_CONTRACT.decision_prompt_sha256,
        context_selection_policy_identity="bounded-context-v1",
        memory_policy_identity="project-persistent-memory-v1",
        chart_renderer_identity="renderer-v1",
        observation_schema_version="JIANGHE_OBSERVATION_V0_1",
        wake_policy_version="wake-v1",
        decision_schema_version="JIANGHE_RUNTIME_RESPONSE_V0_1",
        runtime_normalizer_identity="normalizer-v1",
        hard_execution_envelope_identity="hard-envelope-v1",
        inference_configuration=(("max_retries", "0"),),
        tool_capability_set=(),
        source_family_scope=("A", "B", "C", "D"),
    )


class ReplayV01RuntimeFixture:
    """Builds reopenable ReplayV01Runtime instances bound to one state directory."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        canon_dir = self.root / "docs" / "research" / "jianghe"
        canon_dir.mkdir(parents=True, exist_ok=True)
        canon_file = canon_dir / "JIANGHE_CURRENT_VIEW_V1_1.md"
        canon_file.write_text(
            "# Jianghe fixture\n"
            "趋势中的关键位置应等待确认，不因单根K线猜测。\n"
            "UNKNOWN 必须保留为 UNKNOWN，不能强行猜测。\n",
            encoding="utf-8",
        )
        self.identity = _identity()
        self.db_path = self.root / "state" / "trader.sqlite3"
        self.contract = DeepSeekHarnessRuntimeContract.from_prompts(
            system_prompt=TRADING_ONLY_PROMPT_CONTRACT.system_prompt,
            decision_prompt=TRADING_ONLY_PROMPT_CONTRACT.decision_prompt,
        )

    def make_runtime_factory(self) -> RuntimeFactory:
        def factory(clock):
            store = PersistentTraderStore(self.db_path, trader_identity=self.identity.identity)
            retriever = JiangheCanonRetriever(
                self.root,
                allowed_paths=(CANON_PATH,),
                max_results=3,
                max_chars=1000,
                context_lines=0,
            )
            tools = ProjectToolRegistry(store, clock=clock)
            base = PersistentDeepSeekTraderPrototype(
                trader_identity=self.identity,
                store=store,
                retriever=retriever,
                tools=tools,
                runtime_contract=self.contract,
                clock=clock,
            )
            return ReplayV01Runtime(base)

        return factory
