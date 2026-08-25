"""Downloaded-Kline V0.2 的显式、可审计模型输入契约。

V0.1 的 observation 与历史请求身份保持不变。本模块只为后续新请求生成
provider-neutral 的说明层：它不新增行情、不会读取 future/outcome，也不写入
任何样本特定的答案提示。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal, InvalidOperation
import json
from typing import Any, Mapping

from src.jianghe_ai_trader import JiangheObservation, ObservationBar
from src.jianghe_downloaded_kline_pilot import identity
from src.jianghe_prespend_runtime import CanonicalStructuredObservationArtifact


INPUT_CONTRACT_VERSION = "DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2"
_FORBIDDEN_FIELDS = frozenset({"future_return", "future_price", "pnl", "profit", "win_rate"})
INPUT_CONTRACT_SCHEMA_IDENTITY = identity({
    "input_contract_version": INPUT_CONTRACT_VERSION,
    "timeframe_contract_fields": (
        "bar_order", "index_basis", "eligible_bar_rule", "visible_bar_count",
        "latest_closed_bar", "penultimate_bar",
    ),
    "latest_bar_fields": ("index", "open_time", "close_time", "available_at", "ohlcv", "is_closed"),
    "volume_comparison_rule": "EXACT_INTERVAL_COVERAGE_AND_CLOSED_AVAILABLE_COMPONENTS_ONLY",
    "not_comparable_rule": "NOT_COMPARABLE_IS_NOT_MISMATCH",
    "scope": "PROVIDER_NEUTRAL__CASE_NEUTRAL__NO_FUTURE_OR_OUTCOME",
})


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _decimal(value: str, field_name: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except (InvalidOperation, TypeError) as error:
        raise ValueError(f"{field_name} 必须是有限 Decimal 字符串") from error
    if not parsed.is_finite() or parsed < 0:
        raise ValueError(f"{field_name} 必须是非负有限 Decimal 字符串")
    return parsed


def _scan_forbidden(value: object) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key).lower().replace("-", "_") in _FORBIDDEN_FIELDS:
                raise ValueError(f"input contract contains forbidden field {key}")
            _scan_forbidden(nested)
    elif isinstance(value, list):
        for nested in value:
            _scan_forbidden(nested)


def _bar_payload(bar: ObservationBar, index: int) -> dict[str, object]:
    return {
        "index_basis": "ZERO_BASED_WITHIN_TIMEFRAME",
        "index": index,
        "open_time": bar.open_time.isoformat(),
        "close_time": bar.close_time.isoformat(),
        "available_at": bar.available_at.isoformat(),
        "ohlcv": {
            "open": bar.open_price,
            "high": bar.high_price,
            "low": bar.low_price,
            "close": bar.close_price,
            "volume": bar.volume,
        },
        "is_closed": bar.is_closed,
    }


def _ordered_timeframes(observation: JiangheObservation) -> tuple[str, ...]:
    # Preserve the canonical observation's timeframe group order instead of making
    # a naming-based assumption about arbitrary future timeframe labels.
    return tuple(dict.fromkeys(bar.timeframe for bar in observation.bars))


def _volume_comparisons(
    *, observation: JiangheObservation, bars_by_timeframe: Mapping[str, tuple[ObservationBar, ...]],
) -> list[dict[str, object]]:
    """Only declare a volume comparison after exact interval membership is proven."""
    results: list[dict[str, object]] = []
    decision_time = observation.identity.decision_time
    for target_timeframe, targets in bars_by_timeframe.items():
        for component_timeframe, components in bars_by_timeframe.items():
            if target_timeframe == component_timeframe:
                continue
            if not targets or not components:
                continue
            target_span = targets[0].close_time - targets[0].open_time
            component_span = components[0].close_time - components[0].open_time
            if component_span <= timedelta(0) or target_span <= component_span:
                continue
            quotient, remainder = divmod(target_span, component_span)
            if remainder != timedelta(0) or quotient <= 1:
                continue
            for target_index, target in enumerate(targets):
                members = tuple(
                    bar for bar in components
                    if bar.open_time >= target.open_time and bar.close_time <= target.close_time
                )
                exact = (
                    len(members) == quotient
                    and bool(members)
                    and members[0].open_time == target.open_time
                    and members[-1].close_time == target.close_time
                    and all(members[index - 1].close_time == member.open_time for index, member in enumerate(members) if index)
                    and all(member.is_closed and member.available_at <= decision_time for member in members)
                )
                bucket = {
                    "source_observation_identity": observation.identity.identity,
                    "target_timeframe": target_timeframe,
                    "target_open_time": target.open_time.isoformat(),
                    "target_close_time": target.close_time.isoformat(),
                    "component_timeframe": component_timeframe,
                }
                base = {
                    "constituent_bucket_identity": identity(bucket),
                    "target_timeframe": target_timeframe,
                    "target_bar_index": target_index,
                    "component_timeframe": component_timeframe,
                    "comparison_rule": "EXACT_INTERVAL_COVERAGE_AND_CLOSED_AVAILABLE_COMPONENTS_ONLY",
                }
                if not exact:
                    results.append({
                        **base,
                        "comparison_status": "NOT_COMPARABLE__MISSING_OR_NON_CONTIGUOUS_VISIBLE_CONSTITUENTS",
                        "comparison_permitted": False,
                    })
                    continue
                member_indexes = [components.index(member) for member in members]
                component_volume = sum((_decimal(member.volume, "component volume") for member in members), Decimal("0"))
                target_volume = _decimal(target.volume, "target volume")
                results.append({
                    **base,
                    "comparison_status": "MATCH" if component_volume == target_volume else "MISMATCH",
                    "comparison_permitted": True,
                    "target_volume": format(target_volume, "f"),
                    "component_bar_indexes": member_indexes,
                    "component_volumes": [member.volume for member in members],
                    "component_volume_sum": format(component_volume, "f"),
                })
    return results


@dataclass(frozen=True)
class DownloadedKlineInputContractV02:
    """V0.2 请求附加层；原 canonical structured artifact 仍保持独立、不可变。"""

    source_observation_identity: str
    structured_observation_identity: str
    payload_json: str
    identity: str

    @classmethod
    def from_observation(
        cls,
        observation: JiangheObservation,
        structured_observation: CanonicalStructuredObservationArtifact,
    ) -> "DownloadedKlineInputContractV02":
        if not isinstance(observation, JiangheObservation):
            raise TypeError("observation 必须是 JiangheObservation")
        if not isinstance(structured_observation, CanonicalStructuredObservationArtifact):
            raise TypeError("structured_observation 必须是 canonical artifact")
        if structured_observation.source_observation_identity != observation.identity.identity:
            raise ValueError("structured observation 必须绑定同一 observation")
        decision_time = observation.identity.decision_time
        bars_by_timeframe: dict[str, tuple[ObservationBar, ...]] = {}
        for timeframe in _ordered_timeframes(observation):
            bars = tuple(bar for bar in observation.bars if bar.timeframe == timeframe)
            if not bars:
                raise ValueError("timeframe 不能为空")
            if any(not bar.is_closed or bar.available_at > decision_time or bar.close_time > decision_time for bar in bars):
                raise ValueError("input contract 只接受 decision_time 前已闭合且可见的 K 线")
            if any(previous.open_time >= current.open_time for previous, current in zip(bars, bars[1:])):
                raise ValueError("同一 timeframe 的 K 线必须严格 oldest-to-newest")
            bars_by_timeframe[timeframe] = bars
        timeframe_contracts = []
        for timeframe in _ordered_timeframes(observation):
            bars = bars_by_timeframe[timeframe]
            timeframe_contracts.append({
                "timeframe": timeframe,
                "bar_order": "OLDEST_TO_NEWEST",
                "index_basis": "ZERO_BASED_WITHIN_TIMEFRAME",
                "eligible_bar_rule": "IS_CLOSED_AND_AVAILABLE_AT_LTE_DECISION_TIME",
                "visible_bar_count": len(bars),
                "latest_closed_bar": _bar_payload(bars[-1], len(bars) - 1),
                "penultimate_bar": _bar_payload(bars[-2], len(bars) - 2) if len(bars) > 1 else None,
            })
        payload = {
            "input_contract_version": INPUT_CONTRACT_VERSION,
            "input_contract_schema_identity": INPUT_CONTRACT_SCHEMA_IDENTITY,
            "source_observation_identity": observation.identity.identity,
            "structured_observation_identity": structured_observation.identity,
            "decision_time": decision_time.isoformat(),
            "scope": "PROVIDER_NEUTRAL__CASE_NEUTRAL__NO_FUTURE_OR_OUTCOME",
            "timeframe_contracts": timeframe_contracts,
            "cross_timeframe_volume_comparisons": _volume_comparisons(
                observation=observation, bars_by_timeframe=bars_by_timeframe,
            ),
            "cross_timeframe_volume_guard": (
                "Only compare volume when comparison_permitted is true; "
                "NOT_COMPARABLE is not a mismatch."
            ),
        }
        _scan_forbidden(payload)
        payload_json = _canonical_json(payload)
        return cls(
            source_observation_identity=observation.identity.identity,
            structured_observation_identity=structured_observation.identity,
            payload_json=payload_json,
            identity=identity({"input_contract_version": INPUT_CONTRACT_VERSION, "payload": payload}),
        )

    def payload(self) -> dict[str, Any]:
        return json.loads(self.payload_json)


__all__ = [
    "DownloadedKlineInputContractV02", "INPUT_CONTRACT_SCHEMA_IDENTITY",
    "INPUT_CONTRACT_VERSION",
]
