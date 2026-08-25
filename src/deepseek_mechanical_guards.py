"""Mechanical guards for the current DeepSeek-only Jianghe trader.

These guards enforce project-owned transport/context boundaries. They do not create
new Jianghe trading doctrine and they do not infer market outcomes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


NO_4H_EXACT_VOLUME_RECONCILIATION = "NO_4H_EXACT_VOLUME_RECONCILIATION"

# Raw per-timeframe OHLCV remains legal. What is forbidden is a derived exact
# reconciliation/equality payload that invites the model to treat 4H volume as
# arithmetically identical to overlapping lower-timeframe volume.
_FORBIDDEN_4H_RECONCILIATION_KEYS = frozenset(
    {
        "component_volume_sum",
        "constituent_volume_sum",
        "cross_timeframe_volume_comparison",
        "cross_timeframe_volume_comparisons",
        "exact_volume_match",
        "reconciled_volume",
        "volume_equality",
        "volume_match",
        "volume_reconciliation",
    }
)


def _normalized_key(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _is_4h(value: object) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower().replace(" ", "")
    return normalized in {"4h", "4hour", "4hours", "240m", "240min"}


def _mapping_declares_4h(mapping: Mapping[object, object]) -> bool:
    for raw_key, raw_value in mapping.items():
        key = _normalized_key(raw_key)
        if key in {"timeframe", "target_timeframe", "higher_timeframe", "htf"} and _is_4h(raw_value):
            return True
    return False


def assert_no_4h_exact_volume_reconciliation(value: Any) -> None:
    """Fail closed if a model-context payload contains derived exact 4H volume reconciliation.

    Raw 4H and lower-timeframe volume fields are allowed. The forbidden shape is
    derived comparison/reconciliation data scoped to 4H, including nested records.
    """

    def walk(node: Any, inherited_4h_scope: bool = False) -> None:
        if isinstance(node, Mapping):
            local_4h_scope = inherited_4h_scope or _mapping_declares_4h(node)
            normalized_keys = {_normalized_key(key) for key in node.keys()}
            if local_4h_scope and normalized_keys & _FORBIDDEN_4H_RECONCILIATION_KEYS:
                offending = sorted(normalized_keys & _FORBIDDEN_4H_RECONCILIATION_KEYS)
                raise ValueError(
                    f"{NO_4H_EXACT_VOLUME_RECONCILIATION}: forbidden derived 4H volume fields {offending}"
                )
            for raw_key, child in node.items():
                key = _normalized_key(raw_key)
                child_4h_scope = local_4h_scope or (
                    key in {"4h", "four_hour", "four_hours", "240m", "240min"}
                )
                walk(child, child_4h_scope)
            return
        if isinstance(node, Sequence) and not isinstance(node, (str, bytes, bytearray)):
            for child in node:
                walk(child, inherited_4h_scope)

    walk(value)


__all__ = [
    "NO_4H_EXACT_VOLUME_RECONCILIATION",
    "assert_no_4h_exact_volume_reconciliation",
]
