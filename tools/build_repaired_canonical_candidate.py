"""Pre-built FAIL-CLOSED repaired canonical candidate corpus application.

This tool is prepared in advance so that, the moment all 116 D01/D02
replacement partitions are qualification-verified (116/116 REPAIRED_PASS with
zero residual D01/D02/drift/authority-mismatch), a fully independent repaired
canonical candidate corpus can be assembled without writing ad-hoc tooling.

Flow:
1. Validate root disjointness (never write to the historical accepted root).
2. Load the e98 qualification evidence
   (``CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.json``).
3. Evaluate the materialization gate; HARD STOP unless ALL hold:
       TARGET=116  REPAIRED_PASS=116  STILL_D01=0  STILL_D02=0
       DRIFT=0  AUTHORITY_MISMATCH=0
   plus structural evidence flags and evidence-totals consistency.
4. Read the accepted manifest (as raw JSON: the accepted corpus legally
   contains truncated-PASS records that ``ManifestPartition`` refuses to load,
   exactly the 116 D01/D02 targets) and build the plan:
   - 32,864 already-PASS partitions are INHERITED as-is (byte-faithful parquet
     copy; accepted manifest facts preserved; catalog row facts carried over
     and byte-faithfulness verified by artifact-identity recomputation);
   - the 116 targets use ONLY qualified replacement raw, re-verified
     fail-closed (D01 exact coverage, D02 full expected sessions, no out-of-
     session bars, evidence-vs-disk consistency) and re-normalized under the
     current session authority, recorded as PASS.
5. Materialize ONLY after every gate/plan/re-qualification check passes.
   Output goes ONLY to the independent output root (default
   ``data/repaired_candidate_v01/``): manifest, parquet, catalog, quality
   summary, lineage, deterministic identities, and a build report.
6. The assembled corpus gets a NEW deterministic identity (never the accepted
   ``1d03fd...`` identity) and preserves the parent/historical lineage.

Boundaries (binding):
- No real materialization is run by this pre-built package's defaults.
- No candidate outcome is created here; no validation split is created here.
- The old ``CANONICAL_DATASET_ACCEPTANCE`` is never modified.
- The historical accepted root is never written.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from hashlib import sha256
import json
import shutil
import sqlite3
import sys
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from src.canonical_identity import canonical_hash, governed_metadata_root_identity
from src.canonical_repair_identity import (
    CROSS_SOURCE_CANDIDATE_NOT_REVERIFIED,
    PARENT_CANONICAL_CORPUS_IDENTITY,
    PARENT_RAW_MANIFEST_ROOT_IDENTITY,
    RepairedCandidateCorpusIdentity,
    qualification_evidence_identity,
)
from src.canonical_storage import (
    CANONICAL_SCHEMA_VERSION,
    PARQUET_STORAGE_VERSION,
    CanonicalCatalog,
    CatalogPartitionEntry,
)
from src.historical_acquisition import AcquisitionRequest, build_request_parameters
from src.historical_data import (
    DataVersionIdentity,
    RawArtifact,
    SourceIdentity,
    normalize_tqsdk_historical_bars,
)
from src.historical_manifest import DatasetManifest, ManifestPartition
from tools.build_canonical_dataset import (
    COVERAGE_END,
    COVERAGE_START,
    INVENTORY_RULE_IDENTITY,
    PRODUCTS,
    SOURCE_SPEC,
    build_contract_configs,
    load_calendar,
    load_schedules,
    load_specs,
    load_universe,
    normalize_and_store_partition,
)
from tools.qualify_canonical_d01_d02_repair import EXPECTED_TARGET_COUNT
from tools.revalidate_canonical_corpus import (
    _parse_datetime,
    _partition_identity,
    _timestamp_from_tqsdk,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = PROJECT_ROOT / "docs" / "evidence"

QUALIFICATION_EVIDENCE_SCHEMA_VERSION = (
    "canonical-d01-d02-targeted-repair-qualification-v0.1"
)
DEFAULT_EVIDENCE = EVIDENCE / "CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.json"
DEFAULT_HISTORICAL_ROOT = PROJECT_ROOT / "data" / "canonical"
DEFAULT_REPAIR_RAW_ROOT = (
    PROJECT_ROOT / "data" / "revalidation_repair_v01" / "raw" / "historical"
)
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "data" / "repaired_candidate_v01"

REPAIRED_MANIFEST_SCHEMA_VERSION = "canonical-repaired-candidate-manifest-v1"
REPAIRED_CATALOG_SCHEMA_VERSION = "canonical-repaired-candidate-catalog-v1"
REPAIRED_IDENTITY_SCHEMA_VERSION = "canonical-repaired-candidate-identity-v1"
REPAIRED_QUALITY_SUMMARY_SCHEMA_VERSION = "canonical-repaired-candidate-quality-v1"
REPAIRED_LINEAGE_SCHEMA_VERSION = "canonical-repaired-candidate-lineage-v1"
REPAIRED_BUILD_REPORT_SCHEMA_VERSION = "canonical-repaired-candidate-build-report-v1"
GOVERNED_METADATA_SCHEMA_VERSION = "canonical-governed-metadata-v1"

# Deterministic placeholder for the replacement raw retrieval timestamp, used
# only when the qualification evidence does not record a real
# ``candidate_retrieved_at`` per diagnostic.  A real qualified run must record
# the actual acquisition timestamp; that value takes precedence.
REPAIRED_RETRIEVED_AT = datetime(2026, 8, 21, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
REPAIRED_PROVIDER_VERSION = "3.10.1"

_KNOWN_QUALIFICATION_STATUSES = frozenset(
    {
        "REPAIRED_PASS",
        "STILL_D01_TRUNCATED",
        "STILL_D02_MISSING",
        "RAW_INVALID",
        "ACQUISITION_FAILED",
        "NOT_ATTEMPTED",
    }
)


class RepairedCorpusBlocked(Exception):
    """Fail-closed stop: materialization is not permitted."""


# --------------------------------------------------------------------------- #
# Roots
# --------------------------------------------------------------------------- #
def validate_disjoint(left: Path, right: Path, left_name: str, right_name: str) -> None:
    left_resolved = Path(left).resolve()
    right_resolved = Path(right).resolve()
    if (
        left_resolved == right_resolved
        or left_resolved in right_resolved.parents
        or right_resolved in left_resolved.parents
    ):
        raise RepairedCorpusBlocked(
            f"{left_name} and {right_name} must be disjoint roots "
            f"({left_resolved} vs {right_resolved})"
        )


def validate_roots(
    historical_root: Path, repair_raw_root: Path, output_root: Path
) -> None:
    """The output root must be independent; the historical root must never be
    overwritten; the repair raw root must never collide with either."""
    validate_disjoint(
        historical_root, repair_raw_root, "historical accepted root", "repair raw root"
    )
    validate_disjoint(
        historical_root, output_root, "historical accepted root", "output root"
    )
    validate_disjoint(
        repair_raw_root, output_root, "repair raw root", "output root"
    )


# --------------------------------------------------------------------------- #
# Qualification gate
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class GateSummary:
    target: int
    repaired_pass: int
    still_d01: int
    still_d02: int
    drift: int
    authority_mismatch: int
    acquisition_failed: int
    raw_invalid: int
    not_attempted: int
    gate_open: bool
    reasons: tuple[str, ...]


def compute_gate(evidence: dict) -> GateSummary:
    """Compute the materialization gate from the qualification evidence.

    Pure computation; callers decide whether to raise.  The gate opens only
    when TARGET=116, REPAIRED_PASS=116, STILL_D01=0, STILL_D02=0, DRIFT=0,
    AUTHORITY_MISMATCH=0 AND the evidence is structurally consistent (correct
    schema, no outcome access, no historical modification, reacquisition
    actually attempted, evidence totals match per-diagnostic counts, every
    REPAIRED_PASS diagnostic carries a candidate raw path, no unknown status).
    """
    diagnostics = evidence.get("diagnostics")
    if not isinstance(diagnostics, list):
        raise RepairedCorpusBlocked("qualification evidence has no diagnostics list")
    status_counts: Counter[str] = Counter(
        str(item.get("qualification_status")) for item in diagnostics
    )
    repaired_pass = status_counts.get("REPAIRED_PASS", 0)
    still_d01 = status_counts.get("STILL_D01_TRUNCATED", 0)
    still_d02 = status_counts.get("STILL_D02_MISSING", 0)
    raw_invalid = status_counts.get("RAW_INVALID", 0)
    acquisition_failed = status_counts.get("ACQUISITION_FAILED", 0)
    not_attempted = status_counts.get("NOT_ATTEMPTED", 0)
    drift = sum(
        1 for item in diagnostics if item.get("historical_provider_value_drift") is True
    )
    authority_mismatch = sum(
        1 for item in diagnostics if item.get("authority_boundary_reasons")
    )
    target = evidence.get("target_partition_count")

    reasons: list[str] = []
    if evidence.get("schema_version") != QUALIFICATION_EVIDENCE_SCHEMA_VERSION:
        reasons.append(f"UNEXPECTED_EVIDENCE_SCHEMA:{evidence.get('schema_version')}")
    if evidence.get("outcome_access_used") is not False:
        reasons.append("OUTCOME_ACCESS_USED")
    if evidence.get("historical_accepted_corpus_modified") is not False:
        reasons.append("HISTORICAL_CORPUS_MODIFIED")
    if evidence.get("targeted_reacquisition_attempted") is not True:
        reasons.append("REACQUISITION_NOT_ATTEMPTED")
    if target != EXPECTED_TARGET_COUNT:
        reasons.append(f"TARGET_NE_{EXPECTED_TARGET_COUNT}:{target}")
    if len(diagnostics) != EXPECTED_TARGET_COUNT:
        reasons.append(f"DIAGNOSTICS_NE_{EXPECTED_TARGET_COUNT}:{len(diagnostics)}")
    if repaired_pass != EXPECTED_TARGET_COUNT:
        reasons.append(f"REPAIRED_PASS_NE_{EXPECTED_TARGET_COUNT}:{repaired_pass}")
    if still_d01 != 0:
        reasons.append(f"STILL_D01_NE_0:{still_d01}")
    if still_d02 != 0:
        reasons.append(f"STILL_D02_NE_0:{still_d02}")
    if drift != 0:
        reasons.append(f"DRIFT_NE_0:{drift}")
    if authority_mismatch != 0:
        reasons.append(f"AUTHORITY_MISMATCH_NE_0:{authority_mismatch}")
    if raw_invalid != 0:
        reasons.append(f"RAW_INVALID_PRESENT:{raw_invalid}")
    if acquisition_failed != 0:
        reasons.append(f"ACQUISITION_FAILED_PRESENT:{acquisition_failed}")
    if not_attempted != 0:
        reasons.append(f"NOT_ATTEMPTED_PRESENT:{not_attempted}")
    unknown = set(status_counts) - _KNOWN_QUALIFICATION_STATUSES
    if unknown:
        reasons.append(f"UNKNOWN_QUALIFICATION_STATUS:{sorted(unknown)}")

    totals_match = (
        evidence.get("repaired_pass_count") == repaired_pass
        and evidence.get("still_d01_truncated_count") == still_d01
        and evidence.get("still_d02_missing_count") == still_d02
        and evidence.get("historical_provider_value_drift_count") == drift
        and evidence.get("authority_mismatch_count") == authority_mismatch
        and evidence.get("acquisition_failed_count") == acquisition_failed
    )
    if not totals_match:
        reasons.append("EVIDENCE_TOTALS_INCONSISTENT")

    missing_raw = [
        item.get("partition_identity")
        for item in diagnostics
        if item.get("qualification_status") == "REPAIRED_PASS"
        and not item.get("candidate_raw_path")
    ]
    if missing_raw:
        reasons.append(f"REPAIRED_PASS_MISSING_RAW_PATH:{len(missing_raw)}")

    return GateSummary(
        target=target if isinstance(target, int) else -1,
        repaired_pass=repaired_pass,
        still_d01=still_d01,
        still_d02=still_d02,
        drift=drift,
        authority_mismatch=authority_mismatch,
        acquisition_failed=acquisition_failed,
        raw_invalid=raw_invalid,
        not_attempted=not_attempted,
        gate_open=not reasons,
        reasons=tuple(sorted(reasons)),
    )


def evaluate_gate(evidence: dict) -> GateSummary:
    """Evaluate the gate and HARD STOP when any condition is unmet."""
    summary = compute_gate(evidence)
    if not summary.gate_open:
        raise RepairedCorpusBlocked(
            "qualification gate closed: " + "; ".join(summary.reasons)
        )
    return summary


def load_evidence(path: Path) -> dict:
    data = json.loads(Path(path).read_bytes().decode("utf-8"))
    if not isinstance(data, dict):
        raise RepairedCorpusBlocked(f"{Path(path).name} is not a JSON object")
    return data


# --------------------------------------------------------------------------- #
# Accepted manifest / plan
# --------------------------------------------------------------------------- #
def load_accepted_manifest(historical_root: Path) -> dict:
    """Read the accepted manifest as raw JSON.

    The accepted corpus legally contains truncated-PASS records (the 116
    D01/D02 targets) that the repaired ``ManifestPartition`` refuses to load;
    the raw-JSON form is therefore required to inventory the accepted corpus.
    """
    manifest_path = Path(historical_root) / "manifest.json"
    if not manifest_path.is_file():
        raise RepairedCorpusBlocked(f"no accepted manifest at {manifest_path}")
    document = json.loads(manifest_path.read_bytes().decode("utf-8"))
    if not isinstance(document, dict) or not isinstance(document.get("partitions"), list):
        raise RepairedCorpusBlocked("accepted manifest must contain a partition list")
    partitions = document["partitions"]
    if any(not isinstance(item, dict) for item in partitions):
        raise RepairedCorpusBlocked("accepted manifest contains a non-object partition")
    return document


@dataclass(frozen=True)
class RepairTarget:
    partition_identity: str
    diagnostic: dict
    accepted_partition: dict
    candidate_raw_path: Path


@dataclass(frozen=True)
class BuildPlan:
    inherited: tuple[tuple[dict, ManifestPartition], ...]
    repaired: tuple[RepairTarget, ...]
    accepted_total: int

    @property
    def inherited_count(self) -> int:
        return len(self.inherited)

    @property
    def repaired_count(self) -> int:
        return len(self.repaired)


def _derived_candidate_raw(diagnostic: dict, repair_raw_root: Path) -> Path:
    contract = str(diagnostic["contract"])
    exchange = contract.split(".", 1)[0]
    request = AcquisitionRequest(
        exchange=exchange,
        concrete_instrument=contract,
        trading_day=date.fromisoformat(str(diagnostic["trading_day"])),
        granularity_seconds=int(diagnostic["granularity_seconds"]),
        requested_start=_parse_datetime(diagnostic["requested_start"], "requested_start"),
        requested_end=_parse_datetime(diagnostic["requested_end"], "requested_end"),
    )
    return Path(repair_raw_root) / request.raw_file_name("TQSDK")


def _resolve_candidate_raw(diagnostic: dict, repair_raw_root: Path) -> Path:
    """Locate the qualified replacement raw: prefer ``candidate_raw_path``
    (relative to the repair raw root when not absolute), else derive from the
    standard raw naming scheme.  Missing on disk => HARD STOP."""
    raw_path_text = diagnostic.get("candidate_raw_path")
    if raw_path_text:
        candidate = Path(str(raw_path_text))
        if not candidate.is_absolute():
            candidate = Path(repair_raw_root) / candidate
        if candidate.is_file():
            return candidate.resolve()
    derived = _derived_candidate_raw(diagnostic, repair_raw_root)
    if derived.is_file():
        return derived.resolve()
    raise RepairedCorpusBlocked(
        "replacement raw missing for "
        f"{diagnostic.get('partition_identity')}: candidate_raw_path not found "
        f"and no derived raw at {derived}"
    )


def build_plan(
    evidence: dict,
    accepted_document: dict,
    historical_root: Path,
    repair_raw_root: Path,
) -> BuildPlan:
    """Classify every accepted partition as INHERITED (PASS, kept as-is) or a
    REPAIRED target (replaced only by qualified raw).  Any inconsistency is a
    HARD STOP."""
    diagnostics = evidence["diagnostics"]
    target_ids = [str(item.get("partition_identity")) for item in diagnostics]
    if any(not identity for identity in target_ids):
        raise RepairedCorpusBlocked("qualification evidence has an empty partition identity")
    if len(set(target_ids)) != len(target_ids):
        raise RepairedCorpusBlocked("qualification evidence has duplicate partition identities")
    target_set = set(target_ids)

    by_identity: dict[str, dict] = {}
    for partition in accepted_document["partitions"]:
        identity = _partition_identity(partition)
        if identity in by_identity:
            raise RepairedCorpusBlocked("accepted manifest has duplicate partition identity")
        by_identity[identity] = partition

    missing_targets = sorted(identity for identity in target_ids if identity not in by_identity)
    if missing_targets:
        raise RepairedCorpusBlocked(
            f"{len(missing_targets)} target partition(s) missing from accepted manifest"
        )

    inherited_raw: list[dict] = []
    repaired_targets: list[RepairTarget] = []
    for identity, partition in by_identity.items():
        if identity in target_set:
            diagnostic = next(
                item for item in diagnostics if str(item.get("partition_identity")) == identity
            )
            repaired_targets.append(
                RepairTarget(
                    partition_identity=identity,
                    diagnostic=diagnostic,
                    accepted_partition=partition,
                    candidate_raw_path=_resolve_candidate_raw(diagnostic, repair_raw_root),
                )
            )
        else:
            inherited_raw.append(partition)

    repaired_targets.sort(key=lambda target: target.partition_identity)
    if len(repaired_targets) != EXPECTED_TARGET_COUNT:
        raise RepairedCorpusBlocked(
            f"repair plan has {len(repaired_targets)} targets, expected {EXPECTED_TARGET_COUNT}"
        )
    accepted_total = len(by_identity)
    if len(inherited_raw) != accepted_total - EXPECTED_TARGET_COUNT:
        raise RepairedCorpusBlocked(
            f"repair plan inheritance mismatch: {len(inherited_raw)} inherited + "
            f"{EXPECTED_TARGET_COUNT} targets != {accepted_total} accepted partitions"
        )

    inherited: list[tuple[dict, ManifestPartition]] = []
    for raw in sorted(inherited_raw, key=lambda item: str(_partition_identity(item))):
        try:
            partition = ManifestPartition.from_dict(raw)
        except Exception as error:  # noqa: BLE001 - surface the load failure
            raise RepairedCorpusBlocked(
                f"inherited partition failed to load as PASS: {error}"
            ) from error
        if partition.quality_status != "PASS":
            raise RepairedCorpusBlocked(
                f"inherited partition is not PASS: {partition.contract} "
                f"{partition.trading_day.isoformat()} ({partition.quality_status})"
            )
        inherited.append((raw, partition))

    return BuildPlan(tuple(inherited), tuple(repaired_targets), accepted_total)


# --------------------------------------------------------------------------- #
# Candidate raw re-qualification (fail-closed, read-only)
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class VerifiedRaw:
    payload: bytes
    returned_start: datetime
    returned_end: datetime
    raw_sha256: str


def verify_candidate_raw(target: RepairTarget, config) -> VerifiedRaw:
    """Re-qualify the on-disk replacement raw under D01/D02 semantics.

    A diagnostic marked REPAIRED_PASS whose raw is actually truncated, missing
    expected session bars, contains out-of-session bars, or contradicts the
    evidence's recorded returned coverage is a HARD STOP: the evidence is not
    trusted; the on-disk raw is authoritative for fail-closed admission.
    """
    diagnostic = target.diagnostic
    contract = str(diagnostic["contract"])
    exchange = contract.split(".", 1)[0]
    requested_start = _parse_datetime(diagnostic["requested_start"], "requested_start")
    requested_end = _parse_datetime(diagnostic["requested_end"], "requested_end")
    interval = timedelta(seconds=int(diagnostic["granularity_seconds"]))
    payload = target.candidate_raw_path.read_bytes()
    try:
        records = json.loads(payload.decode("utf-8"))
        if not isinstance(records, list) or not records:
            raise ValueError("raw payload must be a non-empty JSON list")
        by_start: dict[datetime, dict] = {}
        zone = ZoneInfo("Asia/Shanghai")
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("raw record must be a JSON object")
            if record.get("symbol") not in (None, contract):
                raise ValueError("raw record contract differs from target contract")
            start = _timestamp_from_tqsdk(record.get("datetime"), zone)
            if start in by_start:
                raise ValueError("raw records contain duplicate bar starts")
            by_start[start] = record
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
        raise RepairedCorpusBlocked(
            f"candidate raw invalid for {target.partition_identity}: {error}"
        ) from error

    starts = sorted(by_start)
    returned_start = starts[0]
    returned_end = starts[-1] + interval

    # Evidence-vs-disk consistency: the recorded returned coverage must match
    # what is actually on disk.
    recorded_start = diagnostic.get("candidate_returned_start")
    if recorded_start and _parse_datetime(recorded_start, "candidate_returned_start") != returned_start:
        raise RepairedCorpusBlocked(
            f"candidate returned start contradicts on-disk raw for {target.partition_identity}"
        )
    recorded_end = diagnostic.get("candidate_returned_end")
    if recorded_end and _parse_datetime(recorded_end, "candidate_returned_end") != returned_end:
        raise RepairedCorpusBlocked(
            f"candidate returned end contradicts on-disk raw for {target.partition_identity}"
        )

    # D01: exact full requested coverage.
    if returned_start != requested_start or returned_end != requested_end:
        raise RepairedCorpusBlocked(
            f"STILL_D01_TRUNCATED on disk for {target.partition_identity}: "
            f"returned {returned_start.isoformat()}..{returned_end.isoformat()} "
            f"requested {requested_start.isoformat()}..{requested_end.isoformat()}"
        )

    # D02: every expected session bar present; nothing outside the session.
    expected = set(
        config.sessions.expected_bar_starts_between(
            exchange, contract, requested_start, requested_end, interval
        )
    )
    observed = set(starts)
    missing = expected - observed
    if missing:
        raise RepairedCorpusBlocked(
            f"STILL_D02_MISSING on disk for {target.partition_identity}: "
            f"{len(missing)} missing expected bar(s)"
        )
    extra = observed - expected
    if extra:
        raise RepairedCorpusBlocked(
            f"RAW_INVALID on disk for {target.partition_identity}: "
            f"{len(extra)} bar(s) outside the expected session"
        )
    return VerifiedRaw(payload, returned_start, returned_end, sha256(payload).hexdigest())


def _retrieved_at_for(diagnostic: dict, override: datetime | None) -> datetime:
    if override is not None:
        return override
    candidate = diagnostic.get("candidate_retrieved_at")
    if candidate:
        return _parse_datetime(candidate, "candidate_retrieved_at")
    return REPAIRED_RETRIEVED_AT


# --------------------------------------------------------------------------- #
# Repaired partition construction (read-only)
# --------------------------------------------------------------------------- #
def build_repaired_partition(
    target: RepairTarget, verified: VerifiedRaw, config, retrieved_at: datetime
) -> ManifestPartition:
    """Construct the PASS ManifestPartition for a qualified replacement,
    replicating the accepted acquisition path (DatasetBuilder) so every
    provenance identity is correct and deterministic."""
    diagnostic = target.diagnostic
    contract = str(diagnostic["contract"])
    exchange = contract.split(".", 1)[0]
    request = AcquisitionRequest(
        exchange=exchange,
        concrete_instrument=contract,
        trading_day=date.fromisoformat(str(diagnostic["trading_day"])),
        granularity_seconds=int(diagnostic["granularity_seconds"]),
        requested_start=_parse_datetime(diagnostic["requested_start"], "requested_start"),
        requested_end=_parse_datetime(diagnostic["requested_end"], "requested_end"),
    )
    request_parameters = build_request_parameters(
        request, SOURCE_SPEC.request_parameter_names
    )
    source = SourceIdentity(
        provider=SOURCE_SPEC.provider,
        source_type=SOURCE_SPEC.source_type,
        endpoint_identity=SOURCE_SPEC.endpoint_identity,
        provider_dataset_version=SOURCE_SPEC.provider_dataset_version,
        retrieved_at=retrieved_at,
        request_parameters=request_parameters,
    )
    artifact = RawArtifact.from_bytes(
        payload=verified.payload,
        exchange=request.exchange,
        concrete_instrument=request.concrete_instrument,
        coverage_start=verified.returned_start,
        coverage_end=verified.returned_end,
        granularity_seconds=request.granularity_seconds,
        timezone=request.timezone,
        raw_schema_identity=SOURCE_SPEC.raw_schema_identity,
        source_identity_id=source.identity_id,
    )
    data_version = DataVersionIdentity(
        source_identities=(source,),
        raw_artifacts=(artifact,),
        normalizer=SOURCE_SPEC.normalizer,
        session_metadata_version=config.sessions.version,
        historical_availability_rule=SOURCE_SPEC.availability_rule,
        contract_metadata_identity=config.contract_metadata_identity,
    )
    batch = normalize_tqsdk_historical_bars(
        verified.payload,
        artifact=artifact,
        data_version=data_version,
        sessions=config.sessions,
        minimum_price_tick=config.minimum_price_tick,
    )
    if batch.missing_expected_starts:
        raise RepairedCorpusBlocked(
            f"STILL_D02_MISSING during normalization for {target.partition_identity}"
        )
    return ManifestPartition(
        provider=SOURCE_SPEC.provider,
        api_version=REPAIRED_PROVIDER_VERSION,
        contract=request.concrete_instrument,
        exchange=request.exchange,
        granularity_seconds=request.granularity_seconds,
        timezone=request.timezone,
        trading_day=request.trading_day,
        requested_start=request.requested_start,
        requested_end=request.requested_end,
        returned_start=verified.returned_start,
        returned_end=verified.returned_end,
        retrieved_at=retrieved_at,
        raw_bytes=len(verified.payload),
        raw_sha256=verified.raw_sha256,
        request_identity=source.request_identity,
        request_parameters=request_parameters,
        normalizer_identity=SOURCE_SPEC.normalizer.identity_id,
        session_metadata_version=config.sessions.version,
        contract_metadata_identity=config.contract_metadata_identity,
        data_version_id=data_version.identity_id,
        normalized_batch_id=batch.identity_id,
        quality_status="PASS",
    )


# --------------------------------------------------------------------------- #
# Inherited parquet copy + catalog facts
# --------------------------------------------------------------------------- #
def _partition_rel_dir(partition: ManifestPartition) -> Path:
    product = partition.contract.split(".")[1][:2].lower()
    return (
        Path(f"exchange={partition.exchange}")
        / f"product={product}"
        / f"concrete_contract={partition.contract}"
        / f"year={partition.trading_day.year}"
        / f"month={partition.trading_day.month}"
    )


def _assert_inherited_parquet_present(
    partition: ManifestPartition, historical_root: Path
) -> None:
    rel_dir = _partition_rel_dir(partition)
    src_dir = Path(historical_root) / "parquet" / rel_dir
    if not src_dir.is_dir() or not any(
        item.is_file() for item in src_dir.rglob("*.parquet")
    ):
        raise RepairedCorpusBlocked(
            f"accepted parquet missing for {partition.contract} "
            f"{partition.trading_day.isoformat()} at {src_dir}"
        )


def copy_inherited_parquet(
    partition: ManifestPartition, historical_parquet_root: Path, output_parquet_root: Path
) -> dict:
    """Byte-faithful copy of an inherited partition's parquet files into the
    independent output root; returns storage facts including the recomputed
    parquet artifact identity used to verify byte-faithfulness."""
    rel_dir = _partition_rel_dir(partition)
    src_dir = Path(historical_parquet_root) / rel_dir
    if not src_dir.is_dir():
        raise RepairedCorpusBlocked(f"accepted parquet directory missing: {src_dir}")
    files = sorted(item for item in src_dir.rglob("*.parquet") if item.is_file())
    if not files:
        raise RepairedCorpusBlocked(
            f"accepted parquet empty for {partition.contract} {partition.trading_day.isoformat()}"
        )
    dst_dir = Path(output_parquet_root) / rel_dir
    dst_dir.mkdir(parents=True, exist_ok=True)
    for source_file in files:
        relative = source_file.relative_to(src_dir)
        target_file = dst_dir / relative
        shutil.copy2(source_file, target_file)
    copied_files = sorted(
        item for item in dst_dir.rglob("*.parquet") if item.is_file()
    )
    inventory = [
        {
            "relative_path": str(item.relative_to(output_parquet_root)).replace("\\", "/"),
            "sha256": sha256(item.read_bytes()).hexdigest(),
            "bytes": item.stat().st_size,
        }
        for item in copied_files
    ]
    return {
        "file_count": len(inventory),
        "files": inventory,
        "artifact_identity": canonical_hash(
            {"storage_version": PARQUET_STORAGE_VERSION, "files": inventory}
        ),
    }


def _catalog_key(partition: ManifestPartition) -> str:
    return (
        f"{partition.provider}|{partition.contract}|"
        f"{partition.granularity_seconds}|{partition.trading_day.isoformat()}"
    )


def _read_accepted_catalog_entry(accepted_catalog_path: Path, partition_key: str) -> dict | None:
    """Read-only lookup of an inherited partition's accepted catalog facts
    (row_count, logical identity) used to rebuild the candidate catalog."""
    if not Path(accepted_catalog_path).is_file():
        raise RepairedCorpusBlocked(f"accepted catalog missing: {accepted_catalog_path}")
    connection = sqlite3.connect(
        f"{Path(accepted_catalog_path).resolve().as_uri()}?mode=ro&immutable=1", uri=True
    )
    try:
        columns = [
            item[0]
            for item in connection.execute("SELECT * FROM partition_entries").description
        ]
        row = connection.execute(
            "SELECT * FROM partition_entries WHERE partition_key = ?", (partition_key,)
        ).fetchone()
    finally:
        connection.close()
    return None if row is None else dict(zip(columns, row))


def inherited_catalog_entry(
    partition: ManifestPartition, copied: dict, accepted_entry: dict | None
) -> CatalogPartitionEntry:
    if accepted_entry is None:
        raise RepairedCorpusBlocked(
            f"accepted catalog has no entry for {partition.contract} "
            f"{partition.trading_day.isoformat()}"
        )
    # Byte-faithfulness proof: the recomputed artifact identity of the copied
    # files must equal the accepted catalog's recorded artifact identity.
    if accepted_entry["parquet_artifact_identity"] != copied["artifact_identity"]:
        raise RepairedCorpusBlocked(
            f"inherited parquet copy is not byte-faithful for {partition.contract} "
            f"{partition.trading_day.isoformat()}"
        )
    return CatalogPartitionEntry(
        provider=partition.provider,
        contract=partition.contract,
        exchange=partition.exchange,
        granularity_seconds=partition.granularity_seconds,
        trading_day=partition.trading_day,
        raw_sha256=partition.raw_sha256,
        request_identity=partition.request_identity,
        data_version_id=partition.data_version_id,
        normalized_batch_id=partition.normalized_batch_id,
        parquet_artifact_identity=copied["artifact_identity"],
        parquet_logical_identity=accepted_entry["parquet_logical_identity"],
        parquet_storage_version=accepted_entry["parquet_storage_version"],
        row_count=int(accepted_entry["row_count"]),
        coverage_start=accepted_entry["coverage_start"],
        coverage_end=accepted_entry["coverage_end"],
        quality_status=partition.quality_status,
    )


# --------------------------------------------------------------------------- #
# Quality summary / identity
# --------------------------------------------------------------------------- #
def build_quality_summary(
    partitions: Iterable[ManifestPartition], inherited_count: int, repaired_count: int
) -> dict:
    counts: Counter[str] = Counter(item.quality_status for item in partitions)
    return {
        "schema_version": REPAIRED_QUALITY_SUMMARY_SCHEMA_VERSION,
        "total_partitions": sum(counts.values()),
        "inherited_partition_count": inherited_count,
        "repaired_partition_count": repaired_count,
        "by_status": dict(sorted(counts.items())),
        "all_accepted": all(item.quality_status == "PASS" for item in partitions),
    }


def _source_identity_id() -> str:
    return canonical_hash(
        {
            "provider": SOURCE_SPEC.provider,
            "source_type": SOURCE_SPEC.source_type,
            "endpoint_identity": SOURCE_SPEC.endpoint_identity,
            "raw_schema_identity": SOURCE_SPEC.raw_schema_identity,
            "provider_dataset_version": SOURCE_SPEC.provider_dataset_version,
            "normalizer_identity": SOURCE_SPEC.normalizer.identity_id,
            "availability_rule": SOURCE_SPEC.availability_rule,
        }
    )


def _governed_metadata_root_identity() -> str:
    calendar = load_calendar()
    specs = load_specs()
    schedules = load_schedules()
    universe_data = json.loads(
        (EVIDENCE / "CANONICAL_CONTRACT_UNIVERSE.json").read_bytes().decode("utf-8")
    )
    universe_identities = sorted(canonical_hash(entry) for entry in universe_data["contracts"])
    return governed_metadata_root_identity(
        calendar_identity=calendar.identity(),
        spec_identities=[item.identity() for item in specs.values()],
        schedule_identities=[item.identity() for item in schedules.values()],
        universe_identities=universe_identities,
        metadata_schema_version=GOVERNED_METADATA_SCHEMA_VERSION,
    )


def _evidence_totals(evidence: dict) -> dict:
    return {
        "repaired_pass_count": evidence.get("repaired_pass_count"),
        "still_d01_truncated_count": evidence.get("still_d01_truncated_count"),
        "still_d02_missing_count": evidence.get("still_d02_missing_count"),
        "historical_provider_value_drift_count": evidence.get(
            "historical_provider_value_drift_count"
        ),
        "authority_mismatch_count": evidence.get("authority_mismatch_count"),
        "acquisition_failed_count": evidence.get("acquisition_failed_count"),
    }


def compute_candidate_identity(
    manifest: DatasetManifest,
    quality_summary_identity: str,
    evidence: dict,
    *,
    parent_identity: str,
    parent_manifest_identity: str,
    repaired_target_count: int,
    inherited_count: int,
) -> RepairedCandidateCorpusIdentity:
    evidence_identity = qualification_evidence_identity(
        schema_version=str(evidence.get("schema_version")),
        target_partition_count=int(evidence.get("target_partition_count")),
        totals=_evidence_totals(evidence),
        diagnostics=evidence["diagnostics"],
    )
    return RepairedCandidateCorpusIdentity(
        schema_version=REPAIRED_IDENTITY_SCHEMA_VERSION,
        source_provider=SOURCE_SPEC.provider,
        source_identity_id=_source_identity_id(),
        products=tuple(PRODUCTS),
        coverage_start=COVERAGE_START,
        coverage_end=COVERAGE_END,
        inventory_rule_identity=INVENTORY_RULE_IDENTITY,
        raw_manifest_root_identity=manifest.identity(),
        governed_metadata_root_identity=_governed_metadata_root_identity(),
        normalizer_identity=SOURCE_SPEC.normalizer.identity_id,
        parquet_schema_version=CANONICAL_SCHEMA_VERSION,
        parquet_storage_version=PARQUET_STORAGE_VERSION,
        partition_identities=tuple(item.identity() for item in manifest.partitions),
        quality_summary_identity=quality_summary_identity,
        cross_source_summary_identity=CROSS_SOURCE_CANDIDATE_NOT_REVERIFIED,
        parent_canonical_corpus_identity=parent_identity,
        parent_raw_manifest_root_identity=parent_manifest_identity,
        qualification_evidence_identity=evidence_identity,
        repaired_target_count=repaired_target_count,
        inherited_partition_count=inherited_count,
    )


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def build_report(
    gate: GateSummary,
    plan: BuildPlan,
    output_root: Path,
    *,
    dry_run: bool,
    identity_id: str | None = None,
    manifest_identity: str | None = None,
) -> dict:
    return {
        "schema_version": REPAIRED_BUILD_REPORT_SCHEMA_VERSION,
        "dry_run": dry_run,
        "gate": {
            "target": gate.target,
            "repaired_pass": gate.repaired_pass,
            "still_d01": gate.still_d01,
            "still_d02": gate.still_d02,
            "drift": gate.drift,
            "authority_mismatch": gate.authority_mismatch,
            "acquisition_failed": gate.acquisition_failed,
            "raw_invalid": gate.raw_invalid,
            "not_attempted": gate.not_attempted,
            "gate_open": gate.gate_open,
            "reasons": list(gate.reasons),
        },
        "target_partition_count": EXPECTED_TARGET_COUNT,
        "inherited_partition_count": plan.inherited_count,
        "repaired_partition_count": plan.repaired_count,
        "accepted_total_partitions": plan.accepted_total,
        "output_root": str(Path(output_root)).replace("\\", "/"),
        "materialization_run": not dry_run,
        "repaired_candidate_identity": identity_id,
        "manifest_identity": manifest_identity,
    }


def prepare_materialization(
    plan: BuildPlan,
    configs: dict,
    *,
    historical_root: Path,
    repair_raw_root: Path,
    retrieved_at: datetime | None,
) -> tuple[list[ManifestPartition], list[tuple[RepairTarget, VerifiedRaw, ManifestPartition]]]:
    """Read-only fail-closed preparation: verify every candidate raw and build
    every repaired partition BEFORE any output byte is written."""
    repaired: list[tuple[RepairTarget, VerifiedRaw, ManifestPartition]] = []
    for target in plan.repaired:
        config = configs[target.diagnostic["contract"]]
        verified = verify_candidate_raw(target, config)
        retrieved = _retrieved_at_for(target.diagnostic, retrieved_at)
        partition = build_repaired_partition(target, verified, config, retrieved)
        repaired.append((target, verified, partition))
    inherited: list[ManifestPartition] = []
    accepted_catalog_path = Path(historical_root) / "catalog.sqlite"
    for _raw, partition in plan.inherited:
        _assert_inherited_parquet_present(partition, historical_root)
        if _read_accepted_catalog_entry(accepted_catalog_path, _catalog_key(partition)) is None:
            raise RepairedCorpusBlocked(
                f"accepted catalog has no entry for {partition.contract} "
                f"{partition.trading_day.isoformat()}"
            )
        inherited.append(partition)
    return inherited, repaired


def materialize(
    plan: BuildPlan,
    inherited_partitions: list[ManifestPartition],
    repaired: list[tuple[RepairTarget, VerifiedRaw, ManifestPartition]],
    *,
    configs: dict,
    historical_root: Path,
    repair_raw_root: Path,
    output_root: Path,
    evidence: dict,
    parent_identity: str,
    parent_manifest_identity: str,
    gate: GateSummary,
) -> dict:
    """Write the independent repaired candidate corpus.  Called only after the
    gate, plan, and read-only preparation all passed (fail-closed)."""
    output_root.mkdir(parents=True, exist_ok=True)
    parquet_out = output_root / "parquet"
    accepted_catalog_path = Path(historical_root) / "catalog.sqlite"

    entries: list[CatalogPartitionEntry] = []
    for partition in inherited_partitions:
        copied = copy_inherited_parquet(
            partition, Path(historical_root) / "parquet", parquet_out
        )
        accepted_entry = _read_accepted_catalog_entry(
            accepted_catalog_path, _catalog_key(partition)
        )
        entries.append(inherited_catalog_entry(partition, copied, accepted_entry))

    for target, _verified, partition in repaired:
        config = configs[target.diagnostic["contract"]]
        stored = normalize_and_store_partition(
            partition,
            repair_raw_root,
            parquet_out,
            config.sessions,
            config.metadata_fact.identity_id(),
            config.minimum_price_tick,
        )
        entries.append(stored.entry)

    all_partitions = list(inherited_partitions) + [item[2] for item in repaired]
    manifest = DatasetManifest(REPAIRED_MANIFEST_SCHEMA_VERSION, tuple(all_partitions))
    DatasetManifest.save(manifest, output_root / "manifest.json")

    quality = build_quality_summary(
        all_partitions, plan.inherited_count, plan.repaired_count
    )
    quality_identity = canonical_hash(quality)
    quality["quality_summary_identity"] = quality_identity
    (output_root / "quality_summary.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    identity = compute_candidate_identity(
        manifest,
        quality_identity,
        evidence,
        parent_identity=parent_identity,
        parent_manifest_identity=parent_manifest_identity,
        repaired_target_count=plan.repaired_count,
        inherited_count=plan.inherited_count,
    )
    (output_root / "identity.json").write_text(
        json.dumps(identity.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    lineage = {
        "schema_version": REPAIRED_LINEAGE_SCHEMA_VERSION,
        "parent_canonical_corpus_identity": parent_identity,
        "parent_raw_manifest_root_identity": parent_manifest_identity,
        "parent_manifest_path": str(Path(historical_root) / "manifest.json").replace(
            "\\", "/"
        ),
        "repaired_candidate_identity": identity.identity_id(),
        "qualification_evidence_identity": identity.qualification_evidence_identity,
        "repaired_target_count": plan.repaired_count,
        "inherited_partition_count": plan.inherited_count,
        "historical_accepted_corpus_modified": False,
        "candidate_status": "CANDIDATE",
    }
    (output_root / "lineage.json").write_text(
        json.dumps(lineage, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    catalog = CanonicalCatalog(output_root / "catalog.sqlite")
    try:
        catalog.set_meta("schema_version", REPAIRED_CATALOG_SCHEMA_VERSION)
        catalog.set_meta("manifest_identity", manifest.identity())
        catalog.set_meta("repaired_candidate_identity", identity.identity_id())
        catalog.set_meta("parent_canonical_corpus_identity", parent_identity)
        catalog.set_meta("parent_raw_manifest_root_identity", parent_manifest_identity)
        catalog.set_meta("qualification_evidence_identity", identity.qualification_evidence_identity)
        catalog.set_meta("build_complete", "yes")
        for entry in sorted(entries, key=lambda item: (item.contract, item.trading_day.isoformat())):
            catalog.upsert_partition_no_commit(entry)
        catalog.commit()
    finally:
        catalog.close()

    report = build_report(
        gate,
        plan,
        output_root,
        dry_run=False,
        identity_id=identity.identity_id(),
        manifest_identity=manifest.identity(),
    )
    (output_root / "build_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def run_build(
    *,
    historical_root: Path,
    evidence_path: Path,
    repair_raw_root: Path,
    output_root: Path,
    dry_run: bool = False,
    retrieved_at: datetime | None = None,
    parent_identity: str = PARENT_CANONICAL_CORPUS_IDENTITY,
    parent_manifest_identity: str = PARENT_RAW_MANIFEST_ROOT_IDENTITY,
) -> dict:
    """Fail-closed orchestration: everything up to materialization is read-only
    and validated before any output byte is written."""
    validate_roots(historical_root, repair_raw_root, output_root)
    evidence = load_evidence(evidence_path)
    gate = evaluate_gate(evidence)  # HARD STOP when any gate condition is unmet
    accepted_document = load_accepted_manifest(historical_root)
    plan = build_plan(evidence, accepted_document, historical_root, repair_raw_root)
    configs = build_contract_configs(load_calendar(), load_universe(), load_specs(), load_schedules())
    inherited_partitions, repaired = prepare_materialization(
        plan,
        configs,
        historical_root=historical_root,
        repair_raw_root=repair_raw_root,
        retrieved_at=retrieved_at,
    )
    if dry_run:
        return build_report(
            gate, plan, output_root, dry_run=True, identity_id=None, manifest_identity=None
        )
    return materialize(
        plan,
        inherited_partitions,
        repaired,
        configs=configs,
        historical_root=historical_root,
        repair_raw_root=repair_raw_root,
        output_root=output_root,
        evidence=evidence,
        parent_identity=parent_identity,
        parent_manifest_identity=parent_manifest_identity,
        gate=gate,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "FAIL-CLOSED repaired canonical candidate corpus application. "
            "Materialization is permitted only when the 116/116 qualification "
            "gate is fully open; output goes only to an independent root."
        )
    )
    parser.add_argument("--historical-root", type=Path, default=DEFAULT_HISTORICAL_ROOT)
    parser.add_argument("--evidence", type=Path, default=DEFAULT_EVIDENCE)
    parser.add_argument("--repair-raw-root", type=Path, default=DEFAULT_REPAIR_RAW_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--dry-run", action="store_true", help="validate everything; write nothing")
    parser.add_argument(
        "--retrieved-at",
        type=str,
        default=None,
        help="ISO-8601 timestamp override for repaired partition retrieved_at",
    )
    parser.add_argument(
        "--parent-identity", type=str, default=PARENT_CANONICAL_CORPUS_IDENTITY
    )
    parser.add_argument(
        "--parent-manifest-identity", type=str, default=PARENT_RAW_MANIFEST_ROOT_IDENTITY
    )
    args = parser.parse_args()

    retrieved_at = (
        _parse_datetime(args.retrieved_at, "retrieved_at") if args.retrieved_at else None
    )
    try:
        report = run_build(
            historical_root=args.historical_root,
            evidence_path=args.evidence,
            repair_raw_root=args.repair_raw_root,
            output_root=args.output_root,
            dry_run=args.dry_run,
            retrieved_at=retrieved_at,
            parent_identity=args.parent_identity,
            parent_manifest_identity=args.parent_manifest_identity,
        )
    except RepairedCorpusBlocked as error:
        print(f"HARD_STOP: {error}")
        raise SystemExit(1) from error
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
