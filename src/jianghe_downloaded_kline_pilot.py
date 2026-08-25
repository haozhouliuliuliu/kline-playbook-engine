"""Deterministic strict-PIT downloaded-Kline pilot artifacts.

The builder reads the accepted local corpus only when freezing a plan.  The
portable verifier reconstructs every observation and PNG from the frozen,
visible bars, so CI never needs the 15M-row corpus.  No outcome or future field
is accepted by this module.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping

from src.data_substrate import BarQuality, CompletedBar
from src.historical_data import NormalizedHistoricalBar
from src.jianghe_ai_trader import JiangheObservation, ObservationBar, ObservationIdentity
from src.jianghe_prespend_runtime import CanonicalStructuredObservationArtifact, VisualInputArtifact
from src.jianghe_stage_a_frozen_stimulus import frozen_stage_a_renderer_config
from src.jianghe_visual_renderer import JiangheVisualRenderer, VisualObservationSpec, VisualPanel
from src.technical_features import TimeframeAggregator, TimeframeSpec


PILOT_ID = "JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_V0_1"
PLAN_VERSION = "JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_PLAN_V0_1"
CORPUS_IDENTITY = "1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8"
MANIFEST_IDENTITY = "7510a4a943e85c9be256e62971b5a64d64e9976c2b01c9f5d0fe07b1c6c8d324"
ELIGIBILITY_VIEW_IDENTITY = "fb30bfaf0433df02b4ee7d1e781b25473c7271495924859c1d781b87e036c822"
SAMPLE_COUNT = 5
TIMEZONE = "Asia/Shanghai"
WINDOW_COUNTS = {"1H": 3, "15m": 12, "5m": 36}
AGGREGATION_VERSION = "downloaded-kline-pilot-session-authority-v0.1"
_FORBIDDEN = frozenset({"future_return", "future_price", "pnl", "profit", "win_rate"})


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def identity(value: object) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _scan_forbidden(value: object, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in _FORBIDDEN:
                raise ValueError(f"{path} contains forbidden field {key}")
            _scan_forbidden(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _scan_forbidden(nested, f"{path}[{index}]")


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _bar_payload(bar: ObservationBar) -> dict[str, object]:
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


def _bar_from_payload(value: Mapping[str, object]) -> ObservationBar:
    return ObservationBar(
        timeframe=str(value["timeframe"]),
        open_time=datetime.fromisoformat(str(value["open_time"])),
        close_time=datetime.fromisoformat(str(value["close_time"])),
        available_at=datetime.fromisoformat(str(value["available_at"])),
        open_price=str(value["open_price"]), high_price=str(value["high_price"]),
        low_price=str(value["low_price"]), close_price=str(value["close_price"]),
        volume=str(value["volume"]), is_closed=value["is_closed"] is True,
    )


def _observation_from_sample(sample: Mapping[str, object]) -> JiangheObservation:
    bars = tuple(_bar_from_payload(item) for item in sample["visible_bars"])
    decision_time = datetime.fromisoformat(str(sample["decision_time"]))
    if any(bar.available_at > decision_time or bar.close_time > decision_time for bar in bars):
        raise ValueError("frozen sample contains post-decision data")
    return JiangheObservation(
        identity=ObservationIdentity(
            decision_time=decision_time, exchange_time=decision_time,
            product=str(sample["product"]), concrete_contract=str(sample["concrete_contract"]),
            mapping_identity=str(sample["mapping_identity"]),
            session_identity=str(sample["session_metadata_identity"]),
        ),
        bars=bars,
        visible_metadata=(("session", "UNKNOWN"),),
    )


def reconstruct_sample(sample: Mapping[str, object]) -> tuple[JiangheObservation, CanonicalStructuredObservationArtifact, VisualInputArtifact, dict[str, str]]:
    observation = _observation_from_sample(sample)
    structured = CanonicalStructuredObservationArtifact.from_observation(observation)
    panels = tuple(
        VisualPanel(timeframe, tuple(bar for bar in observation.bars if bar.timeframe == timeframe))
        for timeframe in ("1H", "15m", "5m")
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
    hashes = {
        "structured_observation_identity": structured.identity,
        "png_sha256": rendered.png_sha256,
        "renderer_config_identity": rendered.renderer_config_identity,
        "visual_artifact_identity": rendered.visual_artifact_identity,
    }
    return observation, structured, visual, hashes


def verify_plan(plan: Mapping[str, object]) -> str:
    _scan_forbidden(plan)
    if plan.get("pilot_id") != PILOT_ID or plan.get("schema_version") != PLAN_VERSION:
        raise ValueError("pilot plan identity/version mismatch")
    if plan.get("canonical_corpus_identity") != CORPUS_IDENTITY or plan.get("manifest_identity") != MANIFEST_IDENTITY:
        raise ValueError("pilot plan corpus binding mismatch")
    if plan.get("outcome_access") != "NO" or plan.get("future_access") != "NO":
        raise ValueError("pilot plan must deny outcome and future access")
    samples = plan.get("samples")
    if not isinstance(samples, list) or len(samples) != SAMPLE_COUNT:
        raise ValueError("pilot plan must contain exactly five samples")
    if len({item.get("sample_id") for item in samples if isinstance(item, Mapping)}) != SAMPLE_COUNT:
        raise ValueError("pilot sample identities must be unique")
    for sample in samples:
        if not isinstance(sample, Mapping):
            raise ValueError("pilot sample must be an object")
        if sample.get("outcome_access") != "NO" or sample.get("future_access") != "NO":
            raise ValueError("pilot sample must deny outcome and future access")
        bars = sample.get("visible_bars")
        if not isinstance(bars, list):
            raise ValueError("pilot sample visible bars are missing")
        counts = {tf: sum(1 for bar in bars if bar.get("timeframe") == tf) for tf in WINDOW_COUNTS}
        if counts != WINDOW_COUNTS:
            raise ValueError("pilot sample window counts drifted")
        observation, _, _, hashes = reconstruct_sample(sample)
        expected_timeframe_hashes = {
            tf: identity([_bar_payload(bar) for bar in observation.bars if bar.timeframe == tf])
            for tf in WINDOW_COUNTS
        }
        for name, expected in (*hashes.items(), ("observation_identity", observation.identity.identity)):
            if sample.get(name) != expected:
                raise ValueError(f"pilot sample {name} mismatch")
        if sample.get("timeframe_observation_hashes") != expected_timeframe_hashes:
            raise ValueError("pilot sample timeframe hashes mismatch")
        declared = sample.get("sample_identity")
        payload = dict(sample)
        payload.pop("sample_identity", None)
        if declared != identity(payload):
            raise ValueError("pilot sample identity mismatch")
    payload = dict(plan)
    declared_plan_identity = payload.pop("pilot_plan_identity", None)
    calculated = identity(payload)
    if declared_plan_identity != calculated:
        raise ValueError("pilot plan identity mismatch")
    return calculated


def _load_local_authority(project_root: Path) -> tuple[dict[str, object], set[str]]:
    view = json.loads((project_root / "docs/evidence/CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1.json").read_text(encoding="utf-8"))
    if view.get("qualified_eligibility_view_identity") != ELIGIBILITY_VIEW_IDENTITY:
        raise ValueError("qualified eligibility view identity mismatch")
    return view, {str(item["partition_identity"]) for item in view["excluded_partitions"]}


def _partition_identity(entry: Mapping[str, object]) -> str:
    from tools.revalidate_canonical_corpus import _partition_identity as governed_partition_identity
    return governed_partition_identity(entry)


def _select_partitions(data_root: Path, project_root: Path) -> list[dict[str, object]]:
    manifest = json.loads((data_root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("manifest_identity") != MANIFEST_IDENTITY:
        raise ValueError("local manifest identity mismatch")
    _, excluded = _load_local_authority(project_root)
    by_key = {f'{item["provider"]}|{item["contract"]}|{item["granularity_seconds"]}|{item["trading_day"]}': item for item in manifest["partitions"]}
    connection = sqlite3.connect(data_root / "catalog.sqlite")
    try:
        rows = connection.execute(
            "SELECT partition_key, contract, trading_day, row_count, coverage_start, coverage_end, quality_status, parquet_artifact_identity, parquet_logical_identity FROM partition_entries"
        ).fetchall()
    finally:
        connection.close()
    candidates: list[dict[str, object]] = []
    for row in rows:
        entry = by_key.get(row[0])
        if entry is None or _partition_identity(entry) in excluded or row[6] != "PASS" or row[3] < 225:
            continue
        product = str(row[1]).split(".", 1)[1].rstrip("0123456789")
        candidates.append({
            "partition_key": row[0], "contract": row[1], "product": product,
            "trading_day": row[2], "row_count": row[3], "coverage_start": row[4],
            "coverage_end": row[5], "parquet_artifact_identity": row[7],
            "parquet_logical_identity": row[8], "manifest_entry": entry,
        })
    products = sorted({str(item["product"]) for item in candidates}, key=lambda p: identity([CORPUS_IDENTITY, PILOT_ID, "product", p]))[:SAMPLE_COUNT]
    boundaries = ((date(2024, 1, 1), date(2024, 5, 31)), (date(2024, 6, 1), date(2024, 10, 31)), (date(2024, 11, 1), date(2025, 3, 31)), (date(2025, 4, 1), date(2025, 8, 31)), (date(2025, 9, 1), date(2025, 12, 31)))
    selected = []
    for index, product in enumerate(products):
        lower, upper = boundaries[index]
        pool = [item for item in candidates if item["product"] == product and lower <= date.fromisoformat(str(item["trading_day"])) <= upper]
        if not pool:
            raise ValueError(f"no eligible metadata-only pilot partition for {product}")
        selected.append(min(pool, key=lambda item: identity([CORPUS_IDENTITY, PILOT_ID, index, item["partition_key"]])))
    return selected


def _normalized_rows(table: object, *, contract: str) -> tuple[NormalizedHistoricalBar, ...]:
    rows = table.to_pylist()
    result = []
    for row in rows:
        completed = CompletedBar(
            instrument=contract, trading_day=row["trading_day"], start=row["bar_start"],
            end=row["bar_end"], available_at=row["historical_available_at"], quality=BarQuality(),
        )
        result.append(NormalizedHistoricalBar(
            exchange="SHFE", concrete_instrument=contract,
            source_event_at=row["bar_end"], source_retrieved_at=row["historical_available_at"],
            completed_bar=completed, open=row["open"], high=row["high"], low=row["low"], close=row["close"],
            volume=None if row["volume"] is None else Decimal(row["volume"]),
            open_interest_start=None if row["open_interest_start"] is None else Decimal(row["open_interest_start"]),
            open_interest_end=None if row["open_interest_end"] is None else Decimal(row["open_interest_end"]),
            raw_artifact_identity_id=row["raw_artifact_identity_id"], data_version_id=row["data_version_id"],
        ))
    return tuple(sorted(result, key=lambda item: item.completed_bar.start))


def _observation_bar(aggregate: object) -> ObservationBar:
    return ObservationBar(
        timeframe=aggregate.timeframe_spec.name, open_time=aggregate.start, close_time=aggregate.end,
        available_at=aggregate.available_at, open_price=_decimal_text(aggregate.open),
        high_price=_decimal_text(aggregate.high), low_price=_decimal_text(aggregate.low),
        close_price=_decimal_text(aggregate.close),
        volume="0" if aggregate.volume is None else _decimal_text(aggregate.volume), is_closed=True,
    )


def build_plan(data_root: Path, project_root: Path) -> dict[str, object]:
    import pyarrow.dataset as dataset
    from tools.build_canonical_dataset import build_contract_configs, load_calendar, load_schedules, load_specs, load_universe, load_universe_bounds

    from src.jianghe_prespend_runtime import SelectedJiangheContextArtifact
    from src.jianghe_v03_runtime import DEEPSEEK_V03_CONFIG, v03_capability_answer_contract_identity

    selected = _select_partitions(data_root, project_root)
    prompt_package = json.loads((project_root / "docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_3.json").read_text(encoding="utf-8"))
    context = SelectedJiangheContextArtifact.from_fixture_id("JH-FIX-C-001")
    prompt_binding = {
        "system_prompt_sha256": sha256(prompt_package["system_prompt"].encode("utf-8")).hexdigest(),
        "decision_prompt_sha256": sha256(prompt_package["decision_prompt"].encode("utf-8")).hexdigest(),
        "selected_context_identity": context.identity,
        "model_context_identity": context.model_payload()["model_context_identity"],
        "capability_answer_contract_identity": v03_capability_answer_contract_identity(),
    }
    configs = build_contract_configs(load_calendar(), load_universe(), load_universe_bounds(), load_specs(), load_schedules())
    parquet = dataset.dataset(data_root / "parquet", format="parquet", partitioning="hive")
    samples: list[dict[str, object]] = []
    for index, partition in enumerate(selected, 1):
        contract, day = str(partition["contract"]), date.fromisoformat(str(partition["trading_day"]))
        table = parquet.to_table(filter=(dataset.field("concrete_contract") == contract) & (dataset.field("trading_day") == day))
        rows = _normalized_rows(table, contract=contract)
        decision_time = min(datetime.fromisoformat(str(partition["coverage_end"])), rows[-1].completed_bar.available_at)
        visible_rows = tuple(row for row in rows if row.completed_bar.available_at <= decision_time)
        aggregator = TimeframeAggregator(configs[contract].sessions)
        observation_bars: list[ObservationBar] = []
        for name, seconds in (("5m", 300), ("15m", 900), ("1H", 3600)):
            result = aggregator.aggregate(
                visible_rows, spec=TimeframeSpec(name, "INTRADAY", seconds, AGGREGATION_VERSION),
                exchange="SHFE", concrete_instrument=contract,
                coverage_start=visible_rows[0].completed_bar.start, coverage_end=decision_time,
            )
            complete = tuple(item for item in result.aggregates if item.available_at <= decision_time)
            required = WINDOW_COUNTS[name]
            if len(complete) < required:
                raise ValueError(f"selected partition lacks {required} complete {name} bars")
            observation_bars.extend(_observation_bar(item) for item in complete[-required:])
        mapping_identity = identity({"rule": "EXPLICIT_CANONICAL_CONCRETE_CONTRACT_PARTITION", "partition_key": partition["partition_key"]})
        base: dict[str, object] = {
            "sample_id": f"DKL-DS-{index:03d}", "exchange": "SHFE", "product": partition["product"],
            "concrete_contract": contract, "trading_day": partition["trading_day"],
            "decision_time": decision_time.isoformat(), "timezone": TIMEZONE,
            "partition_key": partition["partition_key"], "partition_identity": _partition_identity(partition["manifest_entry"]),
            "parquet_artifact_identity": partition["parquet_artifact_identity"],
            "parquet_logical_identity": partition["parquet_logical_identity"],
            "source_1m_input_identity": identity([item.identity_id for item in visible_rows]),
            "source_1m_bar_count": len(visible_rows), "mapping_identity": mapping_identity,
            "session_metadata_identity": configs[contract].sessions.identity,
            "jianghe_prompt_context_binding": prompt_binding,
            "provider_inference_config_identity": DEEPSEEK_V03_CONFIG.identity,
            "visible_bars": [_bar_payload(bar) for bar in observation_bars],
            "timeframe_observation_hashes": {tf: identity([_bar_payload(bar) for bar in observation_bars if bar.timeframe == tf]) for tf in WINDOW_COUNTS},
            "outcome_access": "NO", "future_access": "NO",
        }
        observation, _, _, hashes = reconstruct_sample(base)
        base.update(hashes)
        base["observation_identity"] = observation.identity.identity
        base["sample_identity"] = identity(base)
        samples.append(base)
    plan: dict[str, object] = {
        "schema_version": PLAN_VERSION, "pilot_id": PILOT_ID,
        "canonical_corpus_identity": CORPUS_IDENTITY, "manifest_identity": MANIFEST_IDENTITY,
        "qualified_eligibility_view_identity": ELIGIBILITY_VIEW_IDENTITY,
        "selection_rule": "METADATA_ONLY_SHA256_SEED_FIVE_PRODUCTS_FIVE_FIXED_TIME_BANDS_V0_1",
        "selection_seed": identity([CORPUS_IDENTITY, PILOT_ID]), "sample_count": SAMPLE_COUNT,
        "timezone": TIMEZONE, "window_counts": WINDOW_COUNTS,
        "provider": "DEEPSEEK", "model_id": "deepseek-v4-flash-vision-exp",
        "provider_inference_config_identity": DEEPSEEK_V03_CONFIG.identity,
        "image_input_bound_tokens": 384,
        "jianghe_prompt_context_binding": prompt_binding,
        "outcome_access": "NO", "future_access": "NO", "validation_access": "LOCKED",
        "samples": samples,
    }
    plan["pilot_plan_identity"] = identity(plan)
    verify_plan(plan)
    return plan


def pretty_plan_bytes(plan: Mapping[str, object]) -> bytes:
    return (json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


__all__ = ["CORPUS_IDENTITY", "MANIFEST_IDENTITY", "PILOT_ID", "PLAN_VERSION", "build_plan", "identity", "pretty_plan_bytes", "reconstruct_sample", "verify_plan"]
