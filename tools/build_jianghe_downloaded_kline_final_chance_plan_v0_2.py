#!/usr/bin/env python3
"""Build/verify the four-case Jianghe downloaded-Kline V0.2 final-chance plan.

Materialization requires the accepted local canonical corpus. The emitted plan
is deliberately non-executable (`MATERIALIZED__AWAITING_PRESEND_REVIEW`):
this tool cannot call a provider or create a paid slot.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys
from typing import Mapping

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_substrate import BarQuality, CompletedBar
from src.historical_data import NormalizedHistoricalBar
from src.jianghe_ai_trader import JiangheObservation, ObservationBar, ObservationIdentity
from src.jianghe_downloaded_kline_final_chance import (
    CONTEXT_FIXTURE_ID,
    DECISION_PROMPT_ADDENDUM,
    FOUR_HOUR_AGGREGATION_VERSION,
    HIGHER_TIMEFRAME_DESCRIPTOR_VERSION,
    HIGHER_WINDOW_COUNTS,
    LOWER_AGGREGATION_VERSION,
    LOWER_WINDOW_COUNTS,
    PANEL_ORDER,
    PILOT_ID,
    PLAN_VERSION,
    PROVIDER_ORDER,
    SAMPLE_COUNT,
    SampleNotEligible,
    bar_payload,
    build_four_hour_context,
    build_plan_spec,
    identity,
    pretty_json_bytes,
    verify_plan_spec,
)
from src.jianghe_downloaded_kline_input_contract import (
    DownloadedKlineInputContractV02,
    INPUT_CONTRACT_SCHEMA_IDENTITY,
    INPUT_CONTRACT_VERSION,
)
from src.jianghe_downloaded_kline_pilot import (
    CORPUS_IDENTITY,
    ELIGIBILITY_VIEW_IDENTITY,
    MANIFEST_IDENTITY,
)
from src.jianghe_prespend_runtime import (
    CanonicalStructuredObservationArtifact,
    SelectedJiangheContextArtifact,
    VisualInputArtifact,
)
from src.jianghe_stage_a_frozen_stimulus import frozen_stage_a_renderer_config
from src.jianghe_visual_renderer import JiangheVisualRenderer, VisualObservationSpec, VisualPanel
from src.technical_features import TimeframeAggregator, TimeframeSpec


DEFAULT_DATA_ROOT = Path(r"C:\Users\H\Documents\kline-playbook-engine\data\canonical")
DEFAULT_SPEC = ROOT / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_SPEC_V0_2.json"
DEFAULT_PLAN = ROOT / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_V0_2.json"
HISTORICAL_V01_PLAN = ROOT / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_PLAN_V0_1.json"
PROMPT_PACKAGE = ROOT / "docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_3.json"


def _bar_from_payload(value: Mapping[str, object]) -> ObservationBar:
    return ObservationBar(
        timeframe=str(value["timeframe"]),
        open_time=datetime.fromisoformat(str(value["open_time"])),
        close_time=datetime.fromisoformat(str(value["close_time"])),
        available_at=datetime.fromisoformat(str(value["available_at"])),
        open_price=str(value["open_price"]),
        high_price=str(value["high_price"]),
        low_price=str(value["low_price"]),
        close_price=str(value["close_price"]),
        volume=str(value["volume"]),
        is_closed=value["is_closed"] is True,
    )


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _partition_identity(entry: Mapping[str, object]) -> str:
    from tools.revalidate_canonical_corpus import _partition_identity as governed_partition_identity
    return governed_partition_identity(entry)


def _historical_partition_keys() -> set[str]:
    if not HISTORICAL_V01_PLAN.exists():
        return set()
    plan = json.loads(HISTORICAL_V01_PLAN.read_text(encoding="utf-8"))
    return {str(item["partition_key"]) for item in plan.get("samples", [])}


def _candidate_metadata(data_root: Path) -> list[dict[str, object]]:
    manifest = json.loads((data_root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("manifest_identity") != MANIFEST_IDENTITY:
        raise ValueError("local manifest identity mismatch")
    view = json.loads(
        (ROOT / "docs/evidence/CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1.json").read_text(
            encoding="utf-8"
        )
    )
    if view.get("qualified_eligibility_view_identity") != ELIGIBILITY_VIEW_IDENTITY:
        raise ValueError("qualified eligibility view identity mismatch")
    excluded = {str(item["partition_identity"]) for item in view["excluded_partitions"]}
    historical_keys = _historical_partition_keys()
    by_key = {
        f'{item["provider"]}|{item["contract"]}|{item["granularity_seconds"]}|{item["trading_day"]}': item
        for item in manifest["partitions"]
    }
    connection = sqlite3.connect(data_root / "catalog.sqlite")
    try:
        rows = connection.execute(
            "SELECT partition_key, contract, trading_day, row_count, coverage_start, coverage_end, "
            "quality_status, parquet_artifact_identity, parquet_logical_identity FROM partition_entries"
        ).fetchall()
    finally:
        connection.close()
    candidates = []
    for row in rows:
        entry = by_key.get(row[0])
        if (
            entry is None
            or row[0] in historical_keys
            or _partition_identity(entry) in excluded
            or row[6] != "PASS"
            or row[3] < 225
        ):
            continue
        candidates.append(
            {
                "partition_key": row[0],
                "contract": row[1],
                "product": str(row[1]).split(".", 1)[1].rstrip("0123456789"),
                "trading_day": row[2],
                "coverage_end": row[5],
                "parquet_artifact_identity": row[7],
                "parquet_logical_identity": row[8],
                "manifest_entry": entry,
            }
        )
    return candidates


def _normalized_rows(table: object, *, contract: str) -> tuple[NormalizedHistoricalBar, ...]:
    result = []
    for row in table.to_pylist():
        completed = CompletedBar(
            instrument=contract,
            trading_day=row["trading_day"],
            start=row["bar_start"],
            end=row["bar_end"],
            available_at=row["historical_available_at"],
            quality=BarQuality(),
        )
        result.append(
            NormalizedHistoricalBar(
                exchange="SHFE",
                concrete_instrument=contract,
                source_event_at=row["bar_end"],
                source_retrieved_at=row["historical_available_at"],
                completed_bar=completed,
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=None if row["volume"] is None else Decimal(row["volume"]),
                open_interest_start=None
                if row["open_interest_start"] is None
                else Decimal(row["open_interest_start"]),
                open_interest_end=None
                if row["open_interest_end"] is None
                else Decimal(row["open_interest_end"]),
                raw_artifact_identity_id=row["raw_artifact_identity_id"],
                data_version_id=row["data_version_id"],
            )
        )
    return tuple(sorted(result, key=lambda item: item.completed_bar.start))


def _lower_stack(rows, *, sessions, contract: str, decision_time: datetime) -> tuple[ObservationBar, ...]:
    aggregator = TimeframeAggregator(sessions)
    bars = []
    for name, seconds in (("1H", 3600), ("15m", 900), ("5m", 300)):
        result = aggregator.aggregate(
            rows,
            spec=TimeframeSpec(name, "INTRADAY", seconds, LOWER_AGGREGATION_VERSION),
            exchange="SHFE",
            concrete_instrument=contract,
            coverage_start=rows[0].completed_bar.start,
            coverage_end=decision_time,
        )
        complete = tuple(item for item in result.aggregates if item.available_at <= decision_time)
        required = LOWER_WINDOW_COUNTS[name]
        if len(complete) < required:
            raise SampleNotEligible(f"candidate lacks {required} complete {name} bars")
        for item in complete[-required:]:
            bars.append(
                ObservationBar(
                    timeframe=name,
                    open_time=item.start,
                    close_time=item.end,
                    available_at=item.available_at,
                    open_price=_decimal_text(item.open),
                    high_price=_decimal_text(item.high),
                    low_price=_decimal_text(item.low),
                    close_price=_decimal_text(item.close),
                    volume="0" if item.volume is None else _decimal_text(item.volume),
                    is_closed=True,
                )
            )
    return tuple(bars)


def _observation(sample: Mapping[str, object]) -> JiangheObservation:
    decision_time = datetime.fromisoformat(str(sample["decision_time"]))
    return JiangheObservation(
        identity=ObservationIdentity(
            decision_time=decision_time,
            exchange_time=decision_time,
            product=str(sample["product"]),
            concrete_contract=str(sample["concrete_contract"]),
            mapping_identity=str(sample["mapping_identity"]),
            session_identity=str(sample["session_metadata_identity"]),
        ),
        bars=tuple(_bar_from_payload(item) for item in sample["visible_bars"]),
        visible_metadata=(("session", "UNKNOWN"),),
    )


def _reconstruct(sample: Mapping[str, object]) -> tuple[JiangheObservation, dict[str, str]]:
    observation = _observation(sample)
    counts = {tf: sum(bar.timeframe == tf for bar in observation.bars) for tf in PANEL_ORDER}
    if counts != {**HIGHER_WINDOW_COUNTS, **LOWER_WINDOW_COUNTS}:
        raise ValueError("timeframe counts drifted")
    descriptors = sample.get("higher_timeframe_bar_descriptors")
    four_hour_bars = tuple(bar for bar in observation.bars if bar.timeframe == "4H")
    if not isinstance(descriptors, list) or len(descriptors) != len(four_hour_bars):
        raise ValueError("4H descriptors missing")
    for bar, descriptor in zip(four_hour_bars, descriptors):
        if descriptor.get("aggregation_version") != FOUR_HOUR_AGGREGATION_VERSION:
            raise ValueError("4H descriptor version mismatch")
        if descriptor.get("official_trading_day") != sample.get("trading_day"):
            raise ValueError("4H trading-day binding mismatch")
        if descriptor.get("observation_bar_identity") != identity(bar_payload(bar)):
            raise ValueError("4H descriptor visible-bar binding mismatch")
        if descriptor.get("volume_comparison_eligible") is not False:
            raise ValueError("4H volume comparison must remain disabled")
        grid_start = datetime.fromisoformat(str(descriptor["grid_start"]))
        grid_end = datetime.fromisoformat(str(descriptor["grid_end"]))
        if not (grid_start <= bar.open_time < bar.close_time <= grid_end):
            raise ValueError("4H bar outside civil grid")

    structured = CanonicalStructuredObservationArtifact.from_observation(observation)
    lower = JiangheObservation(
        identity=ObservationIdentity(
            decision_time=observation.identity.decision_time,
            exchange_time=observation.identity.exchange_time,
            product=observation.identity.product,
            concrete_contract=observation.identity.concrete_contract,
            mapping_identity=str(sample["lower_projection_mapping_identity"]),
            session_identity=observation.identity.session_identity,
        ),
        bars=tuple(bar for bar in observation.bars if bar.timeframe != "4H"),
        visible_metadata=observation.visible_metadata,
    )
    lower_structured = CanonicalStructuredObservationArtifact.from_observation(lower)
    lower_contract = DownloadedKlineInputContractV02.from_observation(lower, lower_structured)
    higher_payload = {
        "version": HIGHER_TIMEFRAME_DESCRIPTOR_VERSION,
        "source_observation_identity": observation.identity.identity,
        "timeframe": "4H",
        "role": "BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY",
        "aggregation_version": FOUR_HOUR_AGGREGATION_VERSION,
        "cross_timeframe_volume_comparison_eligible": False,
        "bars": descriptors,
    }
    panels = tuple(
        VisualPanel(tf, tuple(bar for bar in observation.bars if bar.timeframe == tf))
        for tf in PANEL_ORDER
    )
    rendered = JiangheVisualRenderer(frozen_stage_a_renderer_config()).render(
        VisualObservationSpec(
            product=observation.identity.product,
            concrete_contract=observation.identity.concrete_contract,
            as_of=observation.identity.decision_time,
            panels=panels,
        )
    )
    visual = VisualInputArtifact(
        source_observation_identity=observation.identity.identity,
        renderer_identity=rendered.renderer_config_identity,
        png_bytes=rendered.png_bytes,
    )
    return observation, {
        "full_structured_observation_identity": structured.identity,
        "lower_input_contract_identity": lower_contract.identity,
        "higher_timeframe_descriptor_identity": identity(higher_payload),
        "png_sha256": rendered.png_sha256,
        "renderer_config_identity": rendered.renderer_config_identity,
        "visual_artifact_identity": rendered.visual_artifact_identity,
        "visual_input_identity": visual.identity,
    }


def _build_sample(partition, *, index: int, parquet, configs) -> dict[str, object]:
    import pyarrow.dataset as dataset

    contract = str(partition["contract"])
    day = date.fromisoformat(str(partition["trading_day"]))
    table = parquet.to_table(
        filter=(dataset.field("concrete_contract") == contract)
        & (dataset.field("trading_day") == day)
    )
    rows = _normalized_rows(table, contract=contract)
    if not rows:
        raise SampleNotEligible("candidate has no rows")
    decision_time = min(
        datetime.fromisoformat(str(partition["coverage_end"])),
        rows[-1].completed_bar.available_at,
    )
    visible = tuple(row for row in rows if row.completed_bar.available_at <= decision_time)
    sessions = configs[contract].sessions
    higher, descriptors = build_four_hour_context(
        visible,
        sessions=sessions,
        exchange="SHFE",
        concrete_instrument=contract,
        trading_day=day,
        decision_time=decision_time,
    )
    lower = _lower_stack(visible, sessions=sessions, contract=contract, decision_time=decision_time)
    mapping_identity = identity(
        {
            "rule": "FINAL_CHANCE_EXPLICIT_CANONICAL_PARTITION_PLUS_4H_CONTEXT",
            "partition_key": partition["partition_key"],
            "4h": FOUR_HOUR_AGGREGATION_VERSION,
            "lower": LOWER_AGGREGATION_VERSION,
        }
    )
    base = {
        "sample_id": f"DKL-FC-{index:03d}",
        "exchange": "SHFE",
        "product": partition["product"],
        "concrete_contract": contract,
        "trading_day": partition["trading_day"],
        "decision_time": decision_time.isoformat(),
        "partition_key": partition["partition_key"],
        "partition_identity": _partition_identity(partition["manifest_entry"]),
        "parquet_artifact_identity": partition["parquet_artifact_identity"],
        "parquet_logical_identity": partition["parquet_logical_identity"],
        "source_1m_input_identity": identity([row.identity_id for row in visible]),
        "source_1m_bar_count": len(visible),
        "mapping_identity": mapping_identity,
        "lower_projection_mapping_identity": identity(
            {"rule": "LOWER_STACK_PROJECTION_FOR_INPUT_CONTRACT_V0_2", "source": mapping_identity}
        ),
        "session_metadata_identity": sessions.identity,
        "visible_bars": [bar_payload(bar) for bar in (*higher, *lower)],
        "higher_timeframe_bar_descriptors": [item.payload() for item in descriptors],
        "outcome_access": "NO",
        "future_access": "NO",
    }
    observation, hashes = _reconstruct(base)
    base.update(hashes)
    base["observation_identity"] = observation.identity.identity
    base["sample_identity"] = identity(base)
    return base


def build_materialized_plan(data_root: Path) -> dict[str, object]:
    import pyarrow.dataset as dataset
    from tools.build_canonical_dataset import (
        build_contract_configs, load_calendar, load_schedules, load_specs,
        load_universe, load_universe_bounds,
    )
    from src.jianghe_v03_runtime import V03_PROVIDER_CONFIGS

    configs = build_contract_configs(
        load_calendar(), load_universe(), load_universe_bounds(), load_specs(), load_schedules()
    )
    parquet = dataset.dataset(data_root / "parquet", format="parquet", partitioning="hive")
    candidates = _candidate_metadata(data_root)
    bands = (
        (date(2024, 1, 1), date(2024, 6, 30)),
        (date(2024, 7, 1), date(2024, 12, 31)),
        (date(2025, 1, 1), date(2025, 6, 30)),
        (date(2025, 7, 1), date(2025, 12, 31)),
    )
    samples = []
    used_products = set()
    for index, (start, end) in enumerate(bands, 1):
        pool = [
            item for item in candidates
            if start <= date.fromisoformat(str(item["trading_day"])) <= end
            and item["product"] not in used_products
            and item["contract"] in configs
        ]
        pool.sort(key=lambda item: identity([CORPUS_IDENTITY, PILOT_ID, index, item["partition_key"]]))
        chosen = None
        for item in pool:
            try:
                chosen = _build_sample(item, index=index, parquet=parquet, configs=configs)
            except SampleNotEligible:
                continue
            break
        if chosen is None:
            raise ValueError(f"no fresh eligible final-chance sample in band {index}")
        samples.append(chosen)
        used_products.add(chosen["product"])

    prompt = json.loads(PROMPT_PACKAGE.read_text(encoding="utf-8"))
    system_hash = sha256(prompt["system_prompt"].encode("utf-8")).hexdigest()
    decision_hash = sha256(prompt["decision_prompt"].encode("utf-8")).hexdigest()
    addendum_hash = sha256(DECISION_PROMPT_ADDENDUM.encode("utf-8")).hexdigest()
    context = SelectedJiangheContextArtifact.from_fixture_id(CONTEXT_FIXTURE_ID)
    context_binding = {
        "fixture_id": CONTEXT_FIXTURE_ID,
        "selected_context_identity": context.identity,
        "model_context_identity": context.model_payload()["model_context_identity"],
    }
    common = []
    for sample in samples:
        payload = {
            "version": "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_COMMON_CASE_V0_1",
            "sample_identity": sample["sample_identity"],
            "full_structured_observation_identity": sample["full_structured_observation_identity"],
            "lower_input_contract_identity": sample["lower_input_contract_identity"],
            "higher_timeframe_descriptor_identity": sample["higher_timeframe_descriptor_identity"],
            "png_sha256": sample["png_sha256"],
            "system_prompt_sha256": system_hash,
            "decision_prompt_sha256": decision_hash,
            "decision_prompt_addendum_sha256": addendum_hash,
            **context_binding,
        }
        common.append(
            {"sample_id": sample["sample_id"], "common_case_identity": identity(payload), "payload": payload}
        )
    slots = [
        {
            "slot_identity": f"DKL_FC_V0_2:{provider}:{case['sample_id']}",
            "provider_id": provider,
            "sample_id": case["sample_id"],
            "common_case_identity": case["common_case_identity"],
            "execution_eligible": False,
        }
        for case in common for provider in PROVIDER_ORDER
    ]
    provider_configs = [
        {
            "provider_id": config.provider_id,
            "model_id": config.model_id,
            "provider_inference_config_identity": config.identity,
        }
        for config in V03_PROVIDER_CONFIGS
        if config.provider_id in PROVIDER_ORDER
    ]
    provider_configs.sort(key=lambda item: PROVIDER_ORDER.index(item["provider_id"]))
    plan = {
        "schema_version": PLAN_VERSION,
        "pilot_id": PILOT_ID,
        "status": "MATERIALIZED__AWAITING_PRESEND_REVIEW",
        "plan_spec_identity": build_plan_spec()["plan_spec_identity"],
        "canonical_corpus_identity": CORPUS_IDENTITY,
        "manifest_identity": MANIFEST_IDENTITY,
        "qualified_eligibility_view_identity": ELIGIBILITY_VIEW_IDENTITY,
        "provider_order": list(PROVIDER_ORDER),
        "provider_configs": provider_configs,
        "jianghe_context_binding": context_binding,
        "system_prompt_sha256": system_hash,
        "decision_prompt_sha256": decision_hash,
        "decision_prompt_addendum": DECISION_PROMPT_ADDENDUM,
        "decision_prompt_addendum_sha256": addendum_hash,
        "input_contract_version": INPUT_CONTRACT_VERSION,
        "input_contract_schema_identity": INPUT_CONTRACT_SCHEMA_IDENTITY,
        "four_hour_aggregation_version": FOUR_HOUR_AGGREGATION_VERSION,
        "lower_aggregation_version": LOWER_AGGREGATION_VERSION,
        "timeframe_stack": list(PANEL_ORDER),
        "automatic_retry": "FORBIDDEN",
        "automatic_next_slot": "FORBIDDEN",
        "next_explicit_paid_slot": None,
        "outcome_access": "NO",
        "future_access": "NO",
        "validation_access": "LOCKED",
        "common_case_bindings": common,
        "provider_slots": slots,
        "samples": samples,
    }
    plan["pilot_plan_identity"] = identity(plan)
    verify_materialized_plan(plan)
    return plan


def verify_materialized_plan(plan: Mapping[str, object]) -> str:
    if plan.get("schema_version") != PLAN_VERSION:
        raise ValueError("plan version mismatch")
    if plan.get("status") != "MATERIALIZED__AWAITING_PRESEND_REVIEW":
        raise ValueError("materialized plan must remain fail-closed")
    if plan.get("next_explicit_paid_slot") is not None:
        raise ValueError("materialization cannot create a paid slot")
    samples = plan.get("samples")
    slots = plan.get("provider_slots")
    if not isinstance(samples, list) or len(samples) != SAMPLE_COUNT:
        raise ValueError("materialized plan requires four samples")
    if not isinstance(slots, list) or len(slots) != SAMPLE_COUNT * len(PROVIDER_ORDER):
        raise ValueError("materialized plan requires 12 non-executable slots")
    if any(slot.get("execution_eligible") is not False for slot in slots):
        raise ValueError("materialized slots must remain non-executable")
    for sample in samples:
        observation, hashes = _reconstruct(sample)
        if sample.get("observation_identity") != observation.identity.identity:
            raise ValueError("sample observation identity mismatch")
        for key, value in hashes.items():
            if sample.get(key) != value:
                raise ValueError(f"sample {key} mismatch")
        payload = dict(sample)
        declared = payload.pop("sample_identity", None)
        if declared != identity(payload):
            raise ValueError("sample identity mismatch")
    payload = dict(plan)
    declared = payload.pop("pilot_plan_identity", None)
    calculated = identity(payload)
    if declared != calculated:
        raise ValueError("plan identity mismatch")
    return calculated


def main() -> None:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-spec", action="store_true")
    mode.add_argument("--check-spec", action="store_true")
    mode.add_argument("--materialize", action="store_true")
    mode.add_argument("--check-plan", action="store_true")
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--spec", type=Path, default=DEFAULT_SPEC)
    parser.add_argument("--output", type=Path, default=DEFAULT_PLAN)
    args = parser.parse_args()

    if args.write_spec:
        value = build_plan_spec()
        args.spec.parent.mkdir(parents=True, exist_ok=True)
        args.spec.write_bytes(pretty_json_bytes(value))
        print(json.dumps({"status": value["status"], "plan_spec_identity": value["plan_spec_identity"]}))
    elif args.check_spec:
        value = json.loads(args.spec.read_text(encoding="utf-8"))
        print(json.dumps({"check": "PASS", "plan_spec_identity": verify_plan_spec(value)}))
    elif args.materialize:
        value = build_materialized_plan(args.data_root)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(pretty_json_bytes(value))
        print(json.dumps({"status": value["status"], "pilot_plan_identity": value["pilot_plan_identity"]}))
    else:
        value = json.loads(args.output.read_text(encoding="utf-8"))
        print(json.dumps({"check": "PASS", "pilot_plan_identity": verify_materialized_plan(value)}))


if __name__ == "__main__":
    main()
