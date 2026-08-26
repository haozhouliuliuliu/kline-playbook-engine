"""Replay-only qualification of the accepted legacy manifest by formal D01/D02 revalidation.

The accepted canonical manifest predates the strict D01 constructor guard that now
rejects a historical PASS record when returned coverage is truncated. Formal
post-acceptance revalidation already identified exactly those bad partitions.

This module does not weaken the current ManifestPartition guard and does not
reclassify any failed partition as usable. It verifies the accepted raw manifest
identity without constructing known-failed legacy records, binds the formal
revalidation evidence, marks every revalidation failure ineligible, and still
constructs every remaining partition through the current strict ManifestPartition
contract before it may enter replay selection.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping

from src.historical_manifest import ManifestPartition, canonical_hash
from src.replay_v0_1_exact_slice import (
    EXACT_SLICE_ADAPTER_VERSION,
    ExactReplaySliceSeal,
    _load_json,
    _parse_calendar,
    _parse_e07,
    _parse_session_schedule,
    _require_text,
    build_full_session_mapping_facts,
)
from src.replay_v0_1_selector import PRODUCT_ORDER, ReplayPartitionFact, select_v0_1_slice

QUALIFIED_MANIFEST_ADAPTER_VERSION = "KPE_REPLAY_V0_1_QUALIFIED_MANIFEST_V0_1"
REVALIDATION_SCHEMA_VERSION = "canonical-corpus-revalidation-d01-d02-v0.1"
REVALIDATION_RESULT = "FAIL_REPAIRED_COMPLETENESS"
_REQUIRED_REASONS = frozenset({"D01_RETURNED_COVERAGE_TRUNCATED", "D02_MISSING_EXPECTED_BARS"})
_CONTRACT = re.compile(r"^SHFE\.([a-z]+)\d{4}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _whole_number(value: object, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative whole number")
    return value


def _raw_partition_key(item: Mapping[str, Any]) -> tuple[object, ...]:
    return (
        item.get("provider"), item.get("contract"), item.get("granularity_seconds"),
        item.get("timezone"), item.get("trading_day"), item.get("requested_coverage_start"),
        item.get("requested_coverage_end"),
    )


def raw_partition_identity(item: Mapping[str, Any]) -> str:
    if not isinstance(item, Mapping):
        raise ValueError("raw manifest partition must be an object")
    request_parameters = item.get("request_parameters")
    if not isinstance(request_parameters, list):
        raise ValueError("raw manifest partition request_parameters must be a list")
    normalized_parameters: tuple[tuple[object, object], ...] = tuple(
        tuple(pair) for pair in request_parameters if isinstance(pair, list) and len(pair) == 2
    )
    if len(normalized_parameters) != len(request_parameters):
        raise ValueError("raw manifest request parameter entry must contain exactly two values")
    required = (
        "provider", "api_version", "contract", "exchange", "granularity_seconds", "timezone",
        "trading_day", "requested_coverage_start", "requested_coverage_end", "returned_coverage_start",
        "returned_coverage_end", "retrieved_at", "raw_bytes", "raw_sha256", "request_identity",
        "normalizer_identity", "session_metadata_version", "contract_metadata_identity", "data_version_id",
        "normalized_batch_id", "quality_status",
    )
    missing = tuple(name for name in required if name not in item)
    if missing:
        raise ValueError(f"raw manifest partition is missing required fields: {missing}")
    return canonical_hash({
        "provider": item["provider"], "api_version": item["api_version"], "contract": item["contract"],
        "exchange": item["exchange"], "granularity_seconds": item["granularity_seconds"],
        "timezone": item["timezone"], "trading_day": item["trading_day"],
        "requested_coverage_start": item["requested_coverage_start"],
        "requested_coverage_end": item["requested_coverage_end"],
        "returned_coverage_start": item["returned_coverage_start"],
        "returned_coverage_end": item["returned_coverage_end"], "retrieved_at": item["retrieved_at"],
        "raw_bytes": item["raw_bytes"], "raw_sha256": item["raw_sha256"],
        "request_identity": item["request_identity"], "request_parameters": normalized_parameters,
        "normalizer_identity": item["normalizer_identity"],
        "session_metadata_version": item["session_metadata_version"],
        "contract_metadata_identity": item["contract_metadata_identity"], "data_version_id": item["data_version_id"],
        "normalized_batch_id": item["normalized_batch_id"], "quality_status": item["quality_status"],
    })


def _verify_raw_accepted_manifest(payload: Mapping[str, Any], *, expected_identity: str, expected_count: int) -> tuple[tuple[Mapping[str, Any], str], ...]:
    schema_version = _require_text(payload.get("schema_version"), "raw manifest schema version")
    raw_partitions = payload.get("partitions")
    if not isinstance(raw_partitions, list) or not raw_partitions:
        raise ValueError("raw accepted manifest has no partitions")
    if len(raw_partitions) != expected_count:
        raise ValueError("raw accepted manifest partition count disagrees with corpus authority")
    rows: list[tuple[tuple[object, ...], Mapping[str, Any], str]] = []
    seen_keys: set[tuple[object, ...]] = set()
    seen_ids: set[str] = set()
    for raw in raw_partitions:
        if not isinstance(raw, Mapping):
            raise ValueError("raw accepted manifest partition must be an object")
        key = _raw_partition_key(raw)
        if key in seen_keys:
            raise ValueError("raw accepted manifest contains duplicate partition key")
        seen_keys.add(key)
        partition_identity = raw_partition_identity(raw)
        if partition_identity in seen_ids:
            raise ValueError("raw accepted manifest contains duplicate partition identity")
        seen_ids.add(partition_identity)
        rows.append((key, raw, partition_identity))
    ordered = tuple(sorted(rows, key=lambda item: item[0]))
    recomputed_identity = canonical_hash({"schema_version": schema_version, "partitions": [item[2] for item in ordered]})
    recorded_identity = _require_text(payload.get("manifest_identity"), "raw manifest recorded identity")
    if recorded_identity != recomputed_identity:
        raise ValueError("raw accepted manifest recorded identity does not match recomputation")
    if recomputed_identity != expected_identity:
        raise ValueError("raw canonical manifest identity does not match accepted corpus authority")
    return tuple((raw, partition_identity) for _, raw, partition_identity in ordered)


@dataclass(frozen=True)
class RevalidationQualification:
    revalidation_identity: str
    failure_partition_identities: frozenset[str]
    qualified_partition_count: int
    excluded_partition_count: int
    schema_version: str = REVALIDATION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not _SHA256.fullmatch(self.revalidation_identity):
            raise ValueError("revalidation identity must be lowercase SHA-256")
        if self.excluded_partition_count != len(self.failure_partition_identities):
            raise ValueError("excluded partition count disagrees with formal failure identity set")
        if self.qualified_partition_count <= 0 or self.excluded_partition_count <= 0:
            raise ValueError("formal revalidation qualification counts must be positive")


def verify_revalidation_qualification(payload: Mapping[str, Any], *, raw_by_identity: Mapping[str, Mapping[str, Any]], expected_manifest_identity: str, expected_partition_count: int) -> RevalidationQualification:
    if payload.get("schema_version") != REVALIDATION_SCHEMA_VERSION:
        raise ValueError("unexpected canonical D01/D02 revalidation schema")
    if payload.get("revalidation_result") != REVALIDATION_RESULT:
        raise ValueError("unexpected canonical D01/D02 revalidation result")
    for field_name in ("recomputed_manifest_identity", "recorded_manifest_identity"):
        if payload.get(field_name) != expected_manifest_identity:
            raise ValueError(f"revalidation {field_name} disagrees with accepted raw manifest")
    partition_count = _whole_number(payload.get("partition_count"), "revalidation partition_count")
    pass_count = _whole_number(payload.get("pass_count"), "revalidation pass_count")
    fail_count = _whole_number(payload.get("fail_count"), "revalidation fail_count")
    d01_count = _whole_number(payload.get("d01_failure_count"), "revalidation d01_failure_count")
    d02_count = _whole_number(payload.get("d02_failure_count"), "revalidation d02_failure_count")
    truncated_count = _whole_number(payload.get("truncated_partition_count"), "revalidation truncated_partition_count")
    if partition_count != expected_partition_count or pass_count + fail_count != partition_count:
        raise ValueError("revalidation PASS/FAIL counts do not cover accepted manifest exactly")
    if not (fail_count == d01_count == d02_count == truncated_count):
        raise ValueError("revalidation D01/D02/truncation failure counts disagree")
    catalog_summary = payload.get("catalog_summary")
    if not isinstance(catalog_summary, Mapping) or catalog_summary.get("catalog_partitions") != partition_count:
        raise ValueError("revalidation catalog partition count disagrees with accepted manifest")
    reason_counts = payload.get("reason_counts")
    if not isinstance(reason_counts, Mapping) or any(reason_counts.get(reason) != fail_count for reason in _REQUIRED_REASONS):
        raise ValueError("revalidation reason counts do not cover every formal failure")
    failures = payload.get("failure_partitions")
    if not isinstance(failures, list) or len(failures) != fail_count:
        raise ValueError("revalidation failure partition list disagrees with fail_count")
    failure_ids: set[str] = set()
    for failure in failures:
        if not isinstance(failure, Mapping):
            raise ValueError("revalidation failure entry must be an object")
        partition_identity = _require_text(failure.get("partition_identity"), "revalidation failure partition identity")
        if partition_identity in failure_ids:
            raise ValueError("revalidation failure partition identities must be unique")
        failure_ids.add(partition_identity)
        raw = raw_by_identity.get(partition_identity)
        if raw is None:
            raise ValueError("revalidation failure identity does not exist in accepted raw manifest")
        match = _CONTRACT.fullmatch(str(raw.get("contract", "")))
        raw_product = match.group(1) if match is not None else None
        if failure.get("contract") != raw.get("contract") or failure.get("trading_day") != raw.get("trading_day") or failure.get("product") != raw_product or failure.get("historical_quality_status") != raw.get("quality_status"):
            raise ValueError("revalidation failure metadata disagrees with accepted raw partition")
        reasons = failure.get("reasons")
        if not isinstance(reasons, list) or not _REQUIRED_REASONS.issubset(set(reasons)):
            raise ValueError("revalidation failure entry does not carry both D01 and D02 reasons")
    return RevalidationQualification(
        revalidation_identity=_require_text(payload.get("revalidation_identity"), "revalidation identity"),
        failure_partition_identities=frozenset(failure_ids),
        qualified_partition_count=pass_count,
        excluded_partition_count=fail_count,
    )


def build_revalidated_partition_facts(*, manifest_payload: Mapping[str, Any], revalidation_payload: Mapping[str, Any], expected_manifest_identity: str, expected_partition_count: int) -> tuple[tuple[ReplayPartitionFact, ...], RevalidationQualification]:
    raw_rows = _verify_raw_accepted_manifest(manifest_payload, expected_identity=expected_manifest_identity, expected_count=expected_partition_count)
    raw_by_identity = {partition_identity: raw for raw, partition_identity in raw_rows}
    qualification = verify_revalidation_qualification(
        revalidation_payload,
        raw_by_identity=raw_by_identity,
        expected_manifest_identity=expected_manifest_identity,
        expected_partition_count=expected_partition_count,
    )
    facts: list[ReplayPartitionFact] = []
    strict_qualified_count = 0
    for raw, partition_identity in raw_rows:
        contract = _require_text(raw.get("contract"), "raw partition contract")
        match = _CONTRACT.fullmatch(contract)
        if match is None:
            continue
        product = match.group(1)
        if product not in PRODUCT_ORDER or raw.get("granularity_seconds") != 60 or raw.get("exchange") != "SHFE":
            continue
        failed = partition_identity in qualification.failure_partition_identities
        if failed:
            facts.append(ReplayPartitionFact(
                product=product, concrete_contract=contract,
                trading_day=date.fromisoformat(_require_text(raw.get("trading_day"), "raw trading day")),
                partition_identity=partition_identity,
                session_identity=_require_text(raw.get("session_metadata_version"), "raw session identity"),
                eligible=False,
            ))
            continue
        partition = ManifestPartition.from_dict(dict(raw))
        if partition.identity() != partition_identity:
            raise ValueError("strict qualified partition identity drifted from accepted raw manifest")
        eligible = partition.quality_status == "PASS"
        if eligible:
            strict_qualified_count += 1
        facts.append(ReplayPartitionFact(
            product=product, concrete_contract=partition.contract, trading_day=partition.trading_day,
            partition_identity=partition_identity, session_identity=partition.session_metadata_version,
            eligible=eligible,
        ))
    if strict_qualified_count != qualification.qualified_partition_count:
        raise ValueError("strict replay-qualified partition count disagrees with formal D01/D02 revalidation")
    return tuple(facts), qualification


@dataclass(frozen=True)
class RevalidatedExactReplaySliceSeal:
    base_seal: ExactReplaySliceSeal
    revalidation_identity: str
    qualified_partition_count: int
    excluded_partition_count: int
    qualification_adapter_version: str = QUALIFIED_MANIFEST_ADAPTER_VERSION
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.base_seal, ExactReplaySliceSeal):
            raise TypeError("base_seal must be ExactReplaySliceSeal")
        if not _SHA256.fullmatch(self.revalidation_identity):
            raise ValueError("revalidation identity must be lowercase SHA-256")
        if self.qualified_partition_count <= 0 or self.excluded_partition_count <= 0:
            raise ValueError("qualification counts must be positive")
        object.__setattr__(self, "identity", _hash({
            "qualification_adapter_version": self.qualification_adapter_version,
            "base_exact_slice_seal_identity": self.base_seal.identity,
            "revalidation_identity": self.revalidation_identity,
            "qualified_partition_count": self.qualified_partition_count,
            "excluded_partition_count": self.excluded_partition_count,
        }))

    @property
    def slice(self):
        return self.base_seal.slice

    @property
    def canonical_corpus_identity(self) -> str:
        return self.base_seal.canonical_corpus_identity

    @property
    def raw_manifest_root_identity(self) -> str:
        return self.base_seal.raw_manifest_root_identity

    @property
    def trading_calendar_identity(self) -> str:
        return self.base_seal.trading_calendar_identity

    @property
    def session_authority_root_identity(self) -> str:
        return self.base_seal.session_authority_root_identity

    @property
    def e07_schedule_identity(self) -> str:
        return self.base_seal.e07_schedule_identity

    def to_dict(self) -> dict[str, Any]:
        payload = self.base_seal.to_dict()
        payload["base_exact_slice_seal_identity"] = payload["exact_slice_seal_identity"]
        payload["exact_slice_seal_identity"] = self.identity
        payload.update({
            "qualification_adapter_version": self.qualification_adapter_version,
            "revalidation_identity": self.revalidation_identity,
            "qualified_partition_count": self.qualified_partition_count,
            "excluded_partition_count": self.excluded_partition_count,
        })
        return payload


def select_and_seal_revalidated_exact_v0_1_slice(*, manifest_path: Path, revalidation_path: Path, trading_calendar_path: Path, session_schedule_path: Path, e07_path: Path, corpus_identity_path: Path) -> RevalidatedExactReplaySliceSeal:
    manifest_payload = _load_json(manifest_path)
    corpus = _load_json(corpus_identity_path)
    expected_manifest_identity = _require_text(corpus.get("raw_manifest_root_identity"), "accepted raw manifest root identity")
    expected_count = corpus.get("partition_count")
    if type(expected_count) is not int or expected_count <= 0:
        raise ValueError("accepted corpus authority has invalid partition_count")
    partitions, qualification = build_revalidated_partition_facts(
        manifest_payload=manifest_payload,
        revalidation_payload=_load_json(revalidation_path),
        expected_manifest_identity=expected_manifest_identity,
        expected_partition_count=expected_count,
    )
    calendar_payload = _load_json(trading_calendar_path)
    session_payload = _load_json(session_schedule_path)
    e07_payload = _load_json(e07_path)
    calendar, night_closed, calendar_identity = _parse_calendar(calendar_payload)
    sessions, session_root_identity = _parse_session_schedule(session_payload)
    e07_records, e07_schedule_identity = _parse_e07(e07_payload)
    mappings = build_full_session_mapping_facts(
        trading_calendar=calendar, night_closed_days=night_closed,
        session_products=sessions, e07_records=e07_records,
        e07_schedule_identity=e07_schedule_identity,
    )
    selected = select_v0_1_slice(trading_calendar=calendar, mappings=mappings, partitions=partitions)
    base = ExactReplaySliceSeal(
        slice=selected,
        canonical_corpus_identity=_require_text(corpus.get("canonical_corpus_identity"), "canonical corpus identity"),
        raw_manifest_root_identity=expected_manifest_identity,
        trading_calendar_identity=calendar_identity,
        session_authority_root_identity=session_root_identity,
        e07_schedule_identity=e07_schedule_identity,
        adapter_version=EXACT_SLICE_ADAPTER_VERSION,
    )
    return RevalidatedExactReplaySliceSeal(
        base_seal=base,
        revalidation_identity=qualification.revalidation_identity,
        qualified_partition_count=qualification.qualified_partition_count,
        excluded_partition_count=qualification.excluded_partition_count,
    )


__all__ = [
    "QUALIFIED_MANIFEST_ADAPTER_VERSION", "REVALIDATION_RESULT", "REVALIDATION_SCHEMA_VERSION",
    "RevalidatedExactReplaySliceSeal", "RevalidationQualification", "build_revalidated_partition_facts",
    "raw_partition_identity", "select_and_seal_revalidated_exact_v0_1_slice",
    "verify_revalidation_qualification",
]
