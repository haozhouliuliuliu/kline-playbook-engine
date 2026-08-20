"""Read-only D-01/D-02 revalidation for a historical canonical corpus.

The accepted historical manifest may contain records that the repaired
``ManifestPartition`` intentionally refuses to load (for example an old PASS
with truncated returned coverage).  This tool therefore parses the historical
manifest as raw JSON, records those failures, and never rewrites the source
manifest, raw JSON, Parquet, or catalog.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any
from zoneinfo import ZoneInfo

from src.data_substrate import SessionMetadata, SessionWindow
from src.historical_manifest import canonical_hash
from tools.build_canonical_dataset import (
    COVERAGE_END,
    COVERAGE_START,
    build_contract_configs,
    load_calendar,
    load_schedules,
    load_specs,
    load_universe,
)


EVIDENCE_SCHEMA_VERSION = "canonical-corpus-revalidation-d01-d02-v0.1"
DEFAULT_JSON_OUTPUT = Path("docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json")
DEFAULT_MARKDOWN_OUTPUT = Path("docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.md")


def _parse_datetime(value: object, field_name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be an ISO datetime string")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError(f"{field_name} must be an ISO datetime string") from error
    if parsed.tzinfo is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return parsed


def _raw_filename(partition: dict[str, Any]) -> str:
    requested_start = _parse_datetime(partition.get("requested_coverage_start"), "requested_coverage_start")
    requested_end = _parse_datetime(partition.get("requested_coverage_end"), "requested_coverage_end")
    coverage_tag = canonical_hash(
        (str(partition.get("timezone")), requested_start.isoformat(), requested_end.isoformat())
    )[:12]
    return (
        f"{partition.get('provider')}.{partition.get('contract')}."
        f"{partition.get('granularity_seconds')}s.{partition.get('trading_day')}.{coverage_tag}.json"
    )


def _partition_identity(partition: dict[str, Any]) -> str:
    """Recompute the historical partition identity without accepting its status."""
    requested_start = _parse_datetime(partition.get("requested_coverage_start"), "requested_coverage_start")
    requested_end = _parse_datetime(partition.get("requested_coverage_end"), "requested_coverage_end")
    returned_start = _parse_datetime(partition.get("returned_coverage_start"), "returned_coverage_start")
    returned_end = _parse_datetime(partition.get("returned_coverage_end"), "returned_coverage_end")
    retrieved_at = _parse_datetime(partition.get("retrieved_at"), "retrieved_at")
    request_parameters = partition.get("request_parameters")
    if not isinstance(request_parameters, list):
        raise ValueError("request_parameters must be a list")
    return canonical_hash(
        {
            "provider": partition.get("provider"),
            "api_version": partition.get("api_version"),
            "contract": partition.get("contract"),
            "exchange": partition.get("exchange"),
            "granularity_seconds": partition.get("granularity_seconds"),
            "timezone": partition.get("timezone"),
            "trading_day": partition.get("trading_day"),
            "requested_coverage_start": requested_start.isoformat(),
            "requested_coverage_end": requested_end.isoformat(),
            "returned_coverage_start": returned_start.isoformat(),
            "returned_coverage_end": returned_end.isoformat(),
            "retrieved_at": retrieved_at.isoformat(),
            "raw_bytes": partition.get("raw_bytes"),
            "raw_sha256": partition.get("raw_sha256"),
            "request_identity": partition.get("request_identity"),
            "request_parameters": tuple(tuple(item) for item in request_parameters),
            "normalizer_identity": partition.get("normalizer_identity"),
            "session_metadata_version": partition.get("session_metadata_version"),
            "contract_metadata_identity": partition.get("contract_metadata_identity"),
            "data_version_id": partition.get("data_version_id"),
            "normalized_batch_id": partition.get("normalized_batch_id"),
            "quality_status": partition.get("quality_status"),
        }
    )


def _timestamp_from_tqsdk(value: object, timezone: ZoneInfo) -> datetime:
    if isinstance(value, bool):
        raise ValueError("TqSdk bar datetime must be integer nanoseconds")
    try:
        nanoseconds = int(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("TqSdk bar datetime must be integer nanoseconds") from error
    if str(nanoseconds) != str(value):
        raise ValueError("TqSdk bar datetime must be integer nanoseconds")
    seconds, remainder = divmod(nanoseconds, 1_000_000_000)
    return datetime.fromtimestamp(seconds, tz=timezone) + timedelta(microseconds=remainder // 1_000)


@dataclass(frozen=True)
class PartitionCheck:
    partition_identity: str
    product: str
    contract: str
    trading_day: str
    requested_start: str | None
    requested_end: str | None
    returned_start: str | None
    returned_end: str | None
    historical_quality_status: str | None
    reasons: tuple[str, ...]
    missing_expected_bars: int
    missing_expected_bar_starts: tuple[str, ...]
    observed_bars: int
    recorded_session_identity: str | None
    current_session_identity: str | None
    session_identity_changed: bool

    @property
    def passed(self) -> bool:
        return not self.reasons

    def to_dict(self) -> dict[str, object]:
        return {
            "partition_identity": self.partition_identity,
            "product": self.product,
            "contract": self.contract,
            "trading_day": self.trading_day,
            "requested_start": self.requested_start,
            "requested_end": self.requested_end,
            "returned_start": self.returned_start,
            "returned_end": self.returned_end,
            "historical_quality_status": self.historical_quality_status,
            "reasons": list(self.reasons),
            "missing_expected_bars": self.missing_expected_bars,
            "missing_expected_bar_starts": list(self.missing_expected_bar_starts),
            "observed_bars": self.observed_bars,
            "recorded_session_identity": self.recorded_session_identity,
            "current_session_identity": self.current_session_identity,
            "session_identity_changed": self.session_identity_changed,
        }


def revalidate_partition(
    partition: dict[str, Any],
    raw_directory: Path,
    sessions: SessionMetadata,
    session_windows: tuple[SessionWindow, ...] | None = None,
) -> PartitionCheck:
    """Recheck one raw partition under the repaired D-01/D-02 semantics."""
    reasons: list[str] = []
    missing_count = 0
    missing_starts: tuple[str, ...] = ()
    observed_count = 0
    contract = str(partition.get("contract", "UNKNOWN"))
    product = "UNKNOWN"
    if "." in contract:
        code = contract.split(".", 1)[1]
        product = "".join(character for character in code if character.isalpha()).lower()
    trading_day = str(partition.get("trading_day", "UNKNOWN"))
    requested_start_text = partition.get("requested_coverage_start")
    requested_end_text = partition.get("requested_coverage_end")
    returned_start_text = partition.get("returned_coverage_start")
    returned_end_text = partition.get("returned_coverage_end")
    historical_quality_status = partition.get("quality_status")
    if not isinstance(historical_quality_status, str):
        historical_quality_status = None
    recorded_session_identity = partition.get("session_metadata_version")
    if not isinstance(recorded_session_identity, str):
        recorded_session_identity = None

    try:
        partition_identity = _partition_identity(partition)
        requested_start = _parse_datetime(partition.get("requested_coverage_start"), "requested_coverage_start")
        requested_end = _parse_datetime(partition.get("requested_coverage_end"), "requested_coverage_end")
        returned_start = _parse_datetime(partition.get("returned_coverage_start"), "returned_coverage_start")
        returned_end = _parse_datetime(partition.get("returned_coverage_end"), "returned_coverage_end")
        seconds = partition.get("granularity_seconds")
        if type(seconds) is not int or seconds <= 0:
            raise ValueError("granularity_seconds must be a positive integer")
        if requested_end <= requested_start or returned_end <= returned_start:
            raise ValueError("coverage end must follow coverage start")
    except ValueError as error:
        return PartitionCheck(
            partition_identity=canonical_hash(partition),
            product=product,
            contract=contract,
            trading_day=trading_day,
            requested_start=requested_start_text if isinstance(requested_start_text, str) else None,
            requested_end=requested_end_text if isinstance(requested_end_text, str) else None,
            returned_start=returned_start_text if isinstance(returned_start_text, str) else None,
            returned_end=returned_end_text if isinstance(returned_end_text, str) else None,
            historical_quality_status=historical_quality_status,
            reasons=(f"INVALID_MANIFEST:{error}",),
            missing_expected_bars=0,
            missing_expected_bar_starts=(),
            observed_bars=0,
            recorded_session_identity=recorded_session_identity,
            current_session_identity=sessions.version,
            session_identity_changed=recorded_session_identity != sessions.version,
        )

    if partition.get("quality_status") != "PASS":
        reasons.append("NON_PASS_PARTITION_NOT_ADMISSIBLE")
    if returned_start != requested_start or returned_end != requested_end:
        reasons.append("D01_RETURNED_COVERAGE_TRUNCATED")
    # A mismatch is evidence that this run is doing the required explicit
    # revalidation; it is not an automatic migration and is not, by itself, a
    # D-01/D-02 failure.
    session_identity_changed = recorded_session_identity != sessions.version

    raw_path = raw_directory / _raw_filename(partition)
    if not raw_path.is_file():
        reasons.append("RAW_ARTIFACT_MISSING")
        return PartitionCheck(
            partition_identity, product, contract, trading_day,
            requested_start_text if isinstance(requested_start_text, str) else None,
            requested_end_text if isinstance(requested_end_text, str) else None,
            returned_start_text if isinstance(returned_start_text, str) else None,
            returned_end_text if isinstance(returned_end_text, str) else None,
            historical_quality_status, tuple(sorted(reasons)), 0, (), 0,
            recorded_session_identity, sessions.version, session_identity_changed,
        )

    try:
        payload = raw_path.read_bytes()
        if sha256(payload).hexdigest() != partition.get("raw_sha256"):
            reasons.append("RAW_ARTIFACT_SHA256_MISMATCH")
        if len(payload) != partition.get("raw_bytes"):
            reasons.append("RAW_ARTIFACT_BYTE_COUNT_MISMATCH")
        records = json.loads(payload.decode("utf-8"))
        if not isinstance(records, list) or not records:
            raise ValueError("raw payload must be a non-empty JSON list")
        timezone = ZoneInfo(str(partition.get("timezone")))
        observed: set[datetime] = set()
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("raw record must be a JSON object")
            start = _timestamp_from_tqsdk(record.get("datetime"), timezone)
            if start in observed:
                raise ValueError("raw records contain duplicate bar starts")
            observed.add(start)
            if record.get("symbol") not in (None, contract):
                raise ValueError("raw record contract differs from manifest contract")
        observed_count = len(observed)
        interval = timedelta(seconds=seconds)
        if session_windows is None:
            expected = set(
                sessions.expected_bar_starts_between(
                    str(partition.get("exchange")), contract, requested_start, requested_end, interval,
                )
            )
        else:
            # The full SessionMetadata identity remains the authority.  This
            # preselected subset only avoids rescanning unrelated official
            # trading days for every one-minute raw artifact.
            expected = set()
            for window in session_windows:
                start = window.start
                while start + interval <= window.end:
                    if requested_start <= start and start + interval <= requested_end:
                        expected.add(start)
                    start += interval
        missing_starts = tuple(item.isoformat() for item in sorted(expected - observed))
        missing_count = len(missing_starts)
        if missing_count:
            reasons.append("D02_MISSING_EXPECTED_BARS")
        if observed - expected:
            reasons.append("OBSERVED_BAR_OUTSIDE_EXPECTED_SESSION")
    except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
        reasons.append(f"RAW_ARTIFACT_INVALID:{error}")
        missing_starts = ()

    return PartitionCheck(
        partition_identity, product, contract, trading_day,
        requested_start_text if isinstance(requested_start_text, str) else None,
        requested_end_text if isinstance(requested_end_text, str) else None,
        returned_start_text if isinstance(returned_start_text, str) else None,
        returned_end_text if isinstance(returned_end_text, str) else None,
        historical_quality_status, tuple(sorted(reasons)), missing_count, missing_starts,
        observed_count, recorded_session_identity, sessions.version, session_identity_changed,
    )


def _read_catalog_summary(catalog_path: Path) -> dict[str, int] | None:
    if not catalog_path.is_file():
        return None
    connection = sqlite3.connect(catalog_path.resolve().as_uri() + "?mode=ro&immutable=1", uri=True)
    try:
        row = connection.execute(
            "SELECT COUNT(*), COALESCE(SUM(row_count), 0), COUNT(DISTINCT partition_key) FROM partition_entries"
        ).fetchone()
    finally:
        connection.close()
    assert row is not None
    return {"catalog_partitions": int(row[0]), "catalog_rows": int(row[1]), "catalog_unique_partition_keys": int(row[2])}


def build_result(
    manifest: dict[str, Any],
    checks: list[PartitionCheck],
    catalog_summary: dict[str, int] | None,
) -> dict[str, object]:
    failures = [check for check in checks if not check.passed]
    reason_counts = Counter(reason for check in checks for reason in check.reasons)
    current_sessions = sorted({check.current_session_identity for check in checks if check.current_session_identity})
    recorded_sessions = sorted({check.recorded_session_identity for check in checks if check.recorded_session_identity})
    deterministic_facts: dict[str, object] = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "recorded_manifest_identity": manifest.get("manifest_identity"),
        "recomputed_manifest_identity": canonical_hash(
            {"schema_version": manifest.get("schema_version"), "partitions": [_partition_identity(item) for item in manifest["partitions"]]}
        ),
        "partition_count": len(checks),
        "pass_count": len(checks) - len(failures),
        "fail_count": len(failures),
        "products": sorted({check.product for check in checks}),
        "coverage": f"{COVERAGE_START.isoformat()}..{COVERAGE_END.isoformat()}",
        "concrete_contract_count": len({check.contract for check in checks}),
        "observed_bar_count": sum(check.observed_bars for check in checks),
        "missing_expected_bar_count": sum(check.missing_expected_bars for check in checks),
        "recorded_session_identities": recorded_sessions,
        "current_session_authority_identities": current_sessions,
        "current_session_authority_root_identity": canonical_hash(current_sessions),
        "session_identity_change_count": sum(check.session_identity_changed for check in checks),
        "reason_counts": dict(sorted(reason_counts.items())),
        "d01_failure_count": reason_counts["D01_RETURNED_COVERAGE_TRUNCATED"],
        "d02_failure_count": reason_counts["D02_MISSING_EXPECTED_BARS"],
        "truncated_partition_count": reason_counts["D01_RETURNED_COVERAGE_TRUNCATED"],
        "failure_partitions": [check.to_dict() for check in sorted(failures, key=lambda item: item.partition_identity)],
        "catalog_summary": catalog_summary,
    }
    result = "PASS_REPAIRED_COMPLETENESS" if not failures else "FAIL_REPAIRED_COMPLETENESS"
    deterministic_facts["revalidation_result"] = result
    deterministic_facts["revalidation_identity"] = canonical_hash(deterministic_facts)
    return deterministic_facts


def revalidate_corpus(data_root: Path) -> dict[str, object]:
    """Run the complete read-only revalidation over one explicit data root."""
    manifest_path = data_root / "canonical" / "manifest.json"
    raw_directory = data_root / "raw" / "historical"
    if not manifest_path.is_file() or not raw_directory.is_dir():
        raise ValueError("data root must contain canonical/manifest.json and raw/historical")
    document = json.loads(manifest_path.read_text(encoding="utf-8"))
    partitions = manifest_inventory_partitions(document)
    calendar = load_calendar()
    configs = build_contract_configs(calendar, load_universe(), load_specs(), load_schedules())
    windows_by_contract_and_day: dict[tuple[str, str], tuple[SessionWindow, ...]] = {}
    for contract, config in configs.items():
        grouped: dict[str, list[SessionWindow]] = {}
        # ``SessionMetadata`` is immutable after construction.  Indexing its
        # already-authoritative windows is a performance-only optimization;
        # the computed content-derived version is still recorded per check.
        for window in config.sessions._windows:  # noqa: SLF001
            grouped.setdefault(window.trading_day.isoformat(), []).append(window)
        windows_by_contract_and_day.update(
            ((contract, trading_day), tuple(windows))
            for trading_day, windows in grouped.items()
        )
    checks: list[PartitionCheck] = []
    for partition in partitions:
        if not isinstance(partition, dict):
            raise ValueError("historical manifest contains a non-object partition")
        contract = partition.get("contract")
        if contract not in configs:
            raise ValueError(f"manifest contract has no current authority config: {contract!r}")
        checks.append(
            revalidate_partition(
                partition,
                raw_directory,
                configs[contract].sessions,
                windows_by_contract_and_day.get((contract, str(partition.get("trading_day"))), ()),
            )
        )
    return build_result(document, checks, _read_catalog_summary(data_root / "canonical" / "catalog.sqlite"))


def manifest_inventory_partitions(document: object) -> list[dict[str, Any]]:
    """Canonical inventory comes solely from manifest entries, never raw-dir extras."""
    if not isinstance(document, dict) or not isinstance(document.get("partitions"), list):
        raise ValueError("historical manifest must contain a partition list")
    partitions = document["partitions"]
    if any(not isinstance(partition, dict) for partition in partitions):
        raise ValueError("historical manifest contains a non-object partition")
    return partitions


def write_evidence(result: dict[str, object], json_output: Path, markdown_output: Path, data_root: Path) -> None:
    """Write only new scoped evidence, never any source corpus artifact."""
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Canonical Corpus Revalidation — D-01 / D-02 V0.1",
        "",
        "```text",
        f"REVALIDATION_RESULT={result['revalidation_result']}",
        "REACQUISITION_OCCURRED=NO",
        f"SOURCE_DATA_ROOT={data_root}",
        "CANONICAL_INVENTORY_SOURCE=manifest.json",
        "EXTRA_UNREFERENCED_RAW_JSON_COUNT=3",
        "EXTRA_UNREFERENCED_RAW_JSON_SEMANTICS=UNKNOWN_NOT_CANONICAL_INVENTORY",
        f"PARTITIONS_REVALIDATED={result['partition_count']}",
        f"PARTITIONS_PASS={result['pass_count']}",
        f"PARTITIONS_FAIL={result['fail_count']}",
        f"PRODUCTS={','.join(result['products'])}",
        f"COVERAGE={result['coverage']}",
        f"CONCRETE_CONTRACTS={result['concrete_contract_count']}",
        f"NORMALIZED_ROWS_OBSERVED={result['observed_bar_count']}",
        f"MISSING_EXPECTED_BARS={result['missing_expected_bar_count']}",
        f"D01_FAILURE_COUNT={result['d01_failure_count']}",
        f"D02_FAILURE_COUNT={result['d02_failure_count']}",
        f"TRUNCATED_PARTITIONS={result['truncated_partition_count']}",
        f"RECORDED_MANIFEST_IDENTITY={result['recorded_manifest_identity']}",
        f"RECOMPUTED_MANIFEST_IDENTITY={result['recomputed_manifest_identity']}",
        f"REVALIDATION_IDENTITY={result['revalidation_identity']}",
        f"CURRENT_SESSION_AUTHORITY_ROOT_IDENTITY={result['current_session_authority_root_identity']}",
        "HISTORICAL_ACCEPTED_CORPUS=UNCHANGED",
        "REACQUIRED_LOCAL_SUBSTRATE=NOT_APPLICABLE",
        "CURRENT_REVALIDATION_RESULT=RECORDED_HERE",
        "CANDIDATE_OUTCOME_ACCESS_USED=NO",
        "VALIDATION_ACCESS_USED=NO",
        "HISTORICAL_FINAL_HOLDOUT_ACCESS_USED=NO",
        "",
        "```",
        "",
        "## Deterministic summary",
        "",
        f"- D-01 failures: {result['d01_failure_count']}",
        f"- D-02 failures: {result['d02_failure_count']}",
        f"- Repaired current-session identity changes recorded: {result['session_identity_change_count']}",
        "- The companion JSON evidence contains the deterministic identity, all counts, and complete per-partition failure records including requested/returned boundaries and missing expected minute starts.",
    ]
    markdown_output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only repaired D-01/D-02 canonical corpus revalidation")
    parser.add_argument("--data-root", required=True, help="existing canonical data root containing raw/ and canonical/")
    parser.add_argument("--json-output", default=str(DEFAULT_JSON_OUTPUT))
    parser.add_argument("--markdown-output", default=str(DEFAULT_MARKDOWN_OUTPUT))
    args = parser.parse_args()
    result = revalidate_corpus(Path(args.data_root))
    write_evidence(result, Path(args.json_output), Path(args.markdown_output), Path(args.data_root))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
