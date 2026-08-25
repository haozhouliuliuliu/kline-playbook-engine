"""Owner-approved Jianghe downloaded-Kline V0.2 final-chance protocol primitives.

Offline only: this module defines the fail-closed plan spec, the deterministic
session-aware 4H context representation, and the pre-frozen correctness
domination rule. It performs no provider call and creates no paid slot.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from typing import Mapping, Sequence

from src.data_substrate import SessionMetadata
from src.historical_data import NormalizedHistoricalBar
from src.jianghe_ai_trader import ObservationBar
from src.jianghe_downloaded_kline_input_contract import (
    INPUT_CONTRACT_SCHEMA_IDENTITY,
    INPUT_CONTRACT_VERSION,
)
from src.jianghe_downloaded_kline_pilot import (
    CORPUS_IDENTITY,
    ELIGIBILITY_VIEW_IDENTITY,
    MANIFEST_IDENTITY,
)


PILOT_ID = "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PILOT_V0_2"
PLAN_VERSION = "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_V0_2"
PLAN_SPEC_VERSION = "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_SPEC_V0_2"
HIGHER_TIMEFRAME_DESCRIPTOR_VERSION = "JIANGHE_HIGHER_TIMEFRAME_DESCRIPTOR_V0_1"
FOUR_HOUR_AGGREGATION_VERSION = "SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1"
LOWER_AGGREGATION_VERSION = "downloaded-kline-final-chance-lower-stack-v0.2"
SAMPLE_COUNT = 4
TIMEZONE = "Asia/Shanghai"
PANEL_ORDER = ("4H", "1H", "15m", "5m")
LOWER_WINDOW_COUNTS = {"1H": 3, "15m": 12, "5m": 36}
HIGHER_WINDOW_COUNTS = {"4H": 2}
PROVIDER_ORDER = ("DEEPSEEK", "MINIMAX", "KIMI")
CONTEXT_FIXTURE_ID = "JH-FIX-C-001"
DECISION_PROMPT_ADDENDUM = (
    "本轮测试额外提供 4H 背景表示。4H 只用于市场状态、关键区域、背景位置和剩余空间；"
    "不得把 4H 本身当成自动方向、入场或触发规则。4H 使用官方交易时段内的 civil 4-hour grid；"
    "休市时段不是缺失数据。4H 不参与 V0.2 exact cross-timeframe volume reconciliation。"
)
SEVERITY_ORDER = {"NONE": 0, "MINOR": 1, "MATERIAL": 2, "CRITICAL": 3}
EVALUATION_DIMENSIONS = (
    "MARKET_FACTUAL_CORRECTNESS",
    "LATEST_CLOSED_BAR_CORRECTNESS",
    "CROSS_TIMEFRAME_RELATION_CORRECTNESS",
    "FOUR_HOUR_CONTEXT_ROLE_CORRECTNESS",
    "JIANGHE_SOURCE_FIDELITY",
    "FAMILY_AND_SETUP_INTERPRETATION",
    "BREAKOUT_AND_INVALIDATION_LOGIC",
    "INVENTED_FIXED_RULES_OR_UNSUPPORTED_JIANGHE_CLAIMS",
    "UNCERTAINTY_WAIT_NO_TRADE_DISCIPLINE",
)
_FORBIDDEN = frozenset(
    {"pnl", "profit", "win_rate", "future_price", "future_return", "sharpe", "expectancy"}
)


class SampleNotEligible(ValueError):
    """A valid metadata candidate cannot satisfy the frozen sample recipe."""


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def identity(value: object) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _scan_forbidden(value: object, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).lower().replace("-", "_").replace(" ", "_")
            if normalized in _FORBIDDEN:
                raise ValueError(f"{path} contains forbidden outcome/future field {key}")
            _scan_forbidden(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _scan_forbidden(nested, f"{path}[{index}]")


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def bar_payload(bar: ObservationBar) -> dict[str, object]:
    return {
        "timeframe": bar.timeframe,
        "open_time": bar.open_time.isoformat(),
        "close_time": bar.close_time.isoformat(),
        "available_at": bar.available_at.isoformat(),
        "open_price": bar.open_price,
        "high_price": bar.high_price,
        "low_price": bar.low_price,
        "close_price": bar.close_price,
        "volume": bar.volume,
        "is_closed": bar.is_closed,
    }


def plan_spec_payload() -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": PLAN_SPEC_VERSION,
        "pilot_id": PILOT_ID,
        "plan_version": PLAN_VERSION,
        "status": "PLAN_NOT_MATERIALIZED",
        "canonical_corpus_identity": CORPUS_IDENTITY,
        "manifest_identity": MANIFEST_IDENTITY,
        "qualified_eligibility_view_identity": ELIGIBILITY_VIEW_IDENTITY,
        "sample_count": SAMPLE_COUNT,
        "provider_order": list(PROVIDER_ORDER),
        "total_calls_if_fully_executed": SAMPLE_COUNT * len(PROVIDER_ORDER),
        "matched_case_rule": "SAME_CASE_BYTES_AND_QUESTION_ACROSS_ALL_THREE_PROVIDERS",
        "timeframe_stack": list(PANEL_ORDER),
        "lower_window_counts": LOWER_WINDOW_COUNTS,
        "higher_window_counts": HIGHER_WINDOW_COUNTS,
        "input_contract_version": INPUT_CONTRACT_VERSION,
        "input_contract_schema_identity": INPUT_CONTRACT_SCHEMA_IDENTITY,
        "jianghe_context_selection": "CURRENT_SPEND_ELIGIBLE_PRIMARY_V0_5_SAFE_PROJECTION_VIA_JH_FIX_C_001",
        "four_hour_representation": {
            "version": FOUR_HOUR_AGGREGATION_VERSION,
            "role": "BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY",
            "civil_grid_hours": 4,
            "official_session_minutes_only": True,
            "non_trading_breaks_are_gaps": False,
            "cross_official_trading_day": False,
            "complete_visible_bucket_only": True,
            "cross_timeframe_volume_comparison_eligible": False,
            "jianghe_permanent_doctrine": False,
        },
        "daily_weekly_monthly_in_this_round": "EXCLUDED__INSUFFICIENT_BOUNDED_SOURCE_BACKED_ROLE_EVIDENCE",
        "selection_rule": "FRESH_METADATA_ONLY_SHA256__FOUR_TIME_BANDS__DISTINCT_PRODUCTS__EXCLUDE_V01_PARTITIONS",
        "historical_attempt_reuse": "FORBIDDEN",
        "historical_partition_reuse": "FORBIDDEN_WHEN_V01_PLAN_IS_AVAILABLE",
        "decision_prompt_addendum": DECISION_PROMPT_ADDENDUM,
        "evaluation": {
            "severity_order": list(SEVERITY_ORDER),
            "dimensions": list(EVALUATION_DIMENSIONS),
            "automatic_elimination_rule": (
                "CANDIDATE_AUTO_ELIMINATED_ONLY_IF_DOMINATED_BY_DEEPSEEK:"
                "NO_DIMENSION_BETTER_AND_EITHER_WORSE_WORST_SEVERITY_OR_MORE_MATERIAL_CRITICAL_ERRORS"
            ),
            "mixed_or_parity_policy": "NO_AUTOMATIC_ELIMINATION__REVIEW_REQUIRED",
            "selection_priority": "JIANGHE_CORRECTNESS_AND_CAPABILITY__THEN_ACTUAL_CNY__THEN_ACTUAL_TIME",
        },
        "provider_tools": "DISABLED",
        "automatic_retry": "FORBIDDEN",
        "automatic_next_slot": "FORBIDDEN",
        "outcome_access": "NO",
        "future_access": "NO",
        "validation_access": "LOCKED",
        "next_explicit_paid_slot": None,
        "materialization_requirement": "ACCEPTED_LOCAL_CANONICAL_CORPUS_REQUIRED",
        "budget_rule": "REPRICE_AT_MATERIALIZATION_AND_PRESEND_REVIEW_AGAINST_CURRENT_SHARED_CNY_LEDGER",
    }
    _scan_forbidden(payload)
    return payload


def build_plan_spec() -> dict[str, object]:
    payload = plan_spec_payload()
    return {**payload, "plan_spec_identity": identity(payload)}


def verify_plan_spec(spec: Mapping[str, object]) -> str:
    expected = build_plan_spec()
    if dict(spec) != expected:
        raise ValueError("final-chance plan spec drifted")
    return str(expected["plan_spec_identity"])


def _civil_grid_bounds(start: datetime) -> tuple[datetime, datetime]:
    if start.tzinfo is None or start.utcoffset() is None:
        raise ValueError("4H grid input must be timezone-aware")
    grid_start = start.replace(hour=(start.hour // 4) * 4, minute=0, second=0, microsecond=0)
    return grid_start, grid_start + timedelta(hours=4)


@dataclass(frozen=True)
class HigherTimeframeBarDescriptor:
    timeframe: str
    aggregation_version: str
    official_trading_day: str
    grid_start: str
    grid_end: str
    first_market_minute: str
    last_market_minute_end: str
    expected_constituent_count: int
    expected_constituent_starts_identity: str
    source_constituent_identity: str
    observation_bar_identity: str
    volume_comparison_eligible: bool = False

    def __post_init__(self) -> None:
        if self.timeframe != "4H" or self.aggregation_version != FOUR_HOUR_AGGREGATION_VERSION:
            raise ValueError("unexpected higher-timeframe descriptor semantics")
        if self.expected_constituent_count <= 0:
            raise ValueError("4H descriptor requires expected official minutes")
        if self.volume_comparison_eligible is not False:
            raise ValueError("4H descriptor must be excluded from exact volume reconciliation")

    def payload(self) -> dict[str, object]:
        return {
            "timeframe": self.timeframe,
            "aggregation_version": self.aggregation_version,
            "official_trading_day": self.official_trading_day,
            "grid_start": self.grid_start,
            "grid_end": self.grid_end,
            "first_market_minute": self.first_market_minute,
            "last_market_minute_end": self.last_market_minute_end,
            "expected_constituent_count": self.expected_constituent_count,
            "expected_constituent_starts_identity": self.expected_constituent_starts_identity,
            "source_constituent_identity": self.source_constituent_identity,
            "observation_bar_identity": self.observation_bar_identity,
            "volume_comparison_eligible": False,
        }


def build_four_hour_context(
    rows: Sequence[NormalizedHistoricalBar],
    *,
    sessions: SessionMetadata,
    exchange: str,
    concrete_instrument: str,
    trading_day: date,
    decision_time: datetime,
) -> tuple[tuple[ObservationBar, ...], tuple[HigherTimeframeBarDescriptor, ...]]:
    """Group all official expected 1m minutes by civil 4h grid; breaks are not gaps."""
    expected_day = sessions.expected_bar_starts(
        exchange, concrete_instrument, trading_day, timedelta(minutes=1)
    )
    if not expected_day:
        raise SampleNotEligible("trading day has no authoritative 1m starts")
    groups: dict[tuple[str, str], list[datetime]] = {}
    for start in expected_day:
        grid_start, grid_end = _civil_grid_bounds(start)
        groups.setdefault((grid_start.isoformat(), grid_end.isoformat()), []).append(start)
    by_start = {row.completed_bar.start: row for row in rows}
    bars: list[ObservationBar] = []
    descriptors: list[HigherTimeframeBarDescriptor] = []
    for (grid_start, grid_end), raw_starts in sorted(groups.items()):
        expected = tuple(sorted(raw_starts))
        if expected[-1] + timedelta(minutes=1) > decision_time:
            continue
        if any(start not in by_start for start in expected):
            continue
        constituents = tuple(by_start[start] for start in expected)
        if any(row.completed_bar.available_at > decision_time for row in constituents):
            continue
        if any(row.volume is None for row in constituents):
            continue
        volume = sum((row.volume for row in constituents if row.volume is not None), Decimal(0))
        bar = ObservationBar(
            timeframe="4H",
            open_time=expected[0],
            close_time=expected[-1] + timedelta(minutes=1),
            available_at=max(row.completed_bar.available_at for row in constituents),
            open_price=_decimal_text(constituents[0].open),
            high_price=_decimal_text(max(row.high for row in constituents)),
            low_price=_decimal_text(min(row.low for row in constituents)),
            close_price=_decimal_text(constituents[-1].close),
            volume=_decimal_text(volume),
            is_closed=True,
        )
        descriptors.append(
            HigherTimeframeBarDescriptor(
                timeframe="4H",
                aggregation_version=FOUR_HOUR_AGGREGATION_VERSION,
                official_trading_day=trading_day.isoformat(),
                grid_start=grid_start,
                grid_end=grid_end,
                first_market_minute=bar.open_time.isoformat(),
                last_market_minute_end=bar.close_time.isoformat(),
                expected_constituent_count=len(expected),
                expected_constituent_starts_identity=identity([item.isoformat() for item in expected]),
                source_constituent_identity=identity([row.identity_id for row in constituents]),
                observation_bar_identity=identity(bar_payload(bar)),
            )
        )
        bars.append(bar)
    required = HIGHER_WINDOW_COUNTS["4H"]
    if len(bars) < required:
        raise SampleNotEligible("candidate lacks two complete visible 4H context buckets")
    return tuple(bars[-required:]), tuple(descriptors[-required:])


def adjudicate_candidate_against_deepseek(
    deepseek: Mapping[str, str], candidate: Mapping[str, str]
) -> dict[str, object]:
    """Correctness-only rule frozen before new model outputs exist."""
    if set(deepseek) != set(EVALUATION_DIMENSIONS) or set(candidate) != set(EVALUATION_DIMENSIONS):
        raise ValueError("adjudication requires every frozen dimension exactly once")
    if any(value not in SEVERITY_ORDER for value in (*deepseek.values(), *candidate.values())):
        raise ValueError("unknown correctness severity")
    better = [
        d for d in EVALUATION_DIMENSIONS if SEVERITY_ORDER[candidate[d]] < SEVERITY_ORDER[deepseek[d]]
    ]
    worse = [
        d for d in EVALUATION_DIMENSIONS if SEVERITY_ORDER[candidate[d]] > SEVERITY_ORDER[deepseek[d]]
    ]
    benchmark_worst = max(SEVERITY_ORDER[v] for v in deepseek.values())
    candidate_worst = max(SEVERITY_ORDER[v] for v in candidate.values())
    benchmark_material = sum(SEVERITY_ORDER[v] >= 2 for v in deepseek.values())
    candidate_material = sum(SEVERITY_ORDER[v] >= 2 for v in candidate.values())
    dominated = (
        not better
        and bool(worse)
        and (candidate_worst > benchmark_worst or candidate_material > benchmark_material)
    )
    return {
        "verdict": (
            "DOMINATED_BY_DEEPSEEK"
            if dominated
            else "MIXED_OR_CANDIDATE_ADVANTAGE"
            if better
            else "PARITY_OR_NONDOMINATED"
        ),
        "automatic_elimination": dominated,
        "candidate_better_dimensions": better,
        "candidate_worse_dimensions": worse,
        "deepseek_worst_severity": tuple(SEVERITY_ORDER)[benchmark_worst],
        "candidate_worst_severity": tuple(SEVERITY_ORDER)[candidate_worst],
        "deepseek_material_or_critical_count": benchmark_material,
        "candidate_material_or_critical_count": candidate_material,
    }


def pretty_json_bytes(value: Mapping[str, object]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
