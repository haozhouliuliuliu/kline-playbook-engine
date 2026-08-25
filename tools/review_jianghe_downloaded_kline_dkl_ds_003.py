"""离线复核 DKL-DS-003 的 canonical 1m→多周期链路，绝不访问模型或 outcome。"""

from __future__ import annotations

import argparse
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_downloaded_kline_pilot import (
    AGGREGATION_VERSION,
    WINDOW_COUNTS,
    _bar_payload,
    _normalized_rows,
    _observation_bar,
    identity,
    reconstruct_sample,
)
from src.technical_features import TimeframeAggregator, TimeframeSpec


CASE_ID = "DKL-DS-003"


def _bar_summary(bar: dict[str, object], index: int) -> dict[str, object]:
    return {
        "index_basis": "ZERO_BASED_WITHIN_TIMEFRAME",
        "index": index,
        "open_time": bar["open_time"],
        "close_time": bar["close_time"],
        "available_at": bar["available_at"],
        "is_closed": bar["is_closed"],
        "ohlcv": {
            "open": bar["open_price"], "high": bar["high_price"],
            "low": bar["low_price"], "close": bar["close_price"], "volume": bar["volume"],
        },
    }


def review(project_root: Path, canonical_root: Path) -> tuple[dict[str, Any], bytes]:
    import pyarrow.dataset as dataset
    from tools.build_canonical_dataset import (
        build_contract_configs, load_calendar, load_schedules, load_specs,
        load_universe, load_universe_bounds,
    )

    plan = json.loads((project_root / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_PLAN_V0_1.json").read_text(encoding="utf-8"))
    sample = next(item for item in plan["samples"] if item["sample_id"] == CASE_ID)
    decision_time = datetime.fromisoformat(sample["decision_time"])
    contract = str(sample["concrete_contract"])
    trading_day = date.fromisoformat(str(sample["trading_day"]))
    parquet = dataset.dataset(canonical_root / "parquet", format="parquet", partitioning="hive")
    table = parquet.to_table(filter=(dataset.field("concrete_contract") == contract) & (dataset.field("trading_day") == trading_day))
    rows = _normalized_rows(table, contract=contract)
    visible_rows = tuple(row for row in rows if row.completed_bar.available_at <= decision_time)
    if any(row.completed_bar.available_at > decision_time for row in visible_rows):
        raise AssertionError("post-decision source row entered visible input")
    configs = build_contract_configs(load_calendar(), load_universe(), load_universe_bounds(), load_specs(), load_schedules())
    aggregator = TimeframeAggregator(configs[contract].sessions)
    rebuilt: dict[str, list[dict[str, object]]] = {}
    for name, seconds in (("5m", 300), ("15m", 900), ("1H", 3600)):
        aggregates = aggregator.aggregate(
            visible_rows,
            spec=TimeframeSpec(name, "INTRADAY", seconds, AGGREGATION_VERSION),
            exchange="SHFE", concrete_instrument=contract,
            coverage_start=visible_rows[0].completed_bar.start, coverage_end=decision_time,
        ).aggregates
        complete = tuple(item for item in aggregates if item.available_at <= decision_time)
        rebuilt[name] = [_bar_payload(_observation_bar(item)) for item in complete[-WINDOW_COUNTS[name]:]]
    frozen = {name: [bar for bar in sample["visible_bars"] if bar["timeframe"] == name] for name in rebuilt}
    if rebuilt != frozen:
        raise AssertionError("canonical aggregation does not match frozen V0.1 visible bars")
    observation, structured, visual, hashes = reconstruct_sample(sample)
    if structured.identity != sample["structured_observation_identity"] or hashes["png_sha256"] != sample["png_sha256"]:
        raise AssertionError("bound structured or visual artifact identity drifted")
    final_15m = rebuilt["15m"][-1]
    components = [
        bar for bar in rebuilt["5m"]
        if bar["open_time"] >= final_15m["open_time"] and bar["close_time"] <= final_15m["close_time"]
    ]
    component_volume = sum((Decimal(str(bar["volume"])) for bar in components), Decimal("0"))
    target_volume = Decimal(str(final_15m["volume"]))
    report = {
        "review_schema_version": "JIANGHE_DOWNLOADED_KLINE_DKL_DS_003_MECHANICAL_REVIEW_V0_1",
        "case": CASE_ID,
        "contract": contract,
        "decision_time": decision_time.isoformat(),
        "source_1m_input_identity": identity([row.identity_id for row in visible_rows]),
        "source_1m_bar_count": len(visible_rows),
        "source_rows_only_available_at_lte_decision_time": True,
        "canonical_aggregation_matches_frozen_v0_1": True,
        "structured_observation_identity": structured.identity,
        "png_sha256": hashes["png_sha256"],
        "visual_source_observation_identity": visual.source_observation_identity,
        "timeframes": {
            timeframe: {
                "last_visible_bar": _bar_summary(bars[-1], len(bars) - 1),
                "penultimate_bar": _bar_summary(bars[-2], len(bars) - 2),
            }
            for timeframe, bars in rebuilt.items()
        },
        "last_15m_to_5m_volume": {
            "target_15m_bar": _bar_summary(final_15m, len(rebuilt["15m"]) - 1),
            "constituent_5m_bars": [_bar_summary(bar, rebuilt["5m"].index(bar)) for bar in components],
            "component_volume_sum": format(component_volume, "f"),
            "target_15m_volume": format(target_volume, "f"),
            "aggregation_result": "MATCH" if component_volume == target_volume else "MISMATCH",
            "comparison_legality": "LEGAL__EXACT_CONTIGUOUS_INTERVAL_COVERAGE",
        },
        "outcome_access": "NO",
        "future_access": "NO",
    }
    report["review_identity"] = identity(report)
    return report, visual.png_bytes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=ROOT)
    parser.add_argument("--canonical-root", type=Path, required=True)
    parser.add_argument("--png-output", type=Path)
    args = parser.parse_args()
    report, png_bytes = review(args.project_root.resolve(), args.canonical_root.resolve())
    if args.png_output is not None:
        output = args.png_output.resolve()
        if output.exists():
            raise ValueError("png output 已存在，拒绝覆盖")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(png_bytes)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
