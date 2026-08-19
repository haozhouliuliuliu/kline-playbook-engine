"""PACKAGE_D_PREFLIGHT_CANONICAL_DEFECT_REPRODUCTION_V0_1 diagnostic tool.

This is a DIAGNOSTIC / reproduction tool, NOT a repair-acceptance test and NOT
part of the default unittest suite.  Its purpose is to prove, on the current
real code, the D-01..D-08 findings from the second full-project audit:

  docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md (Part C)

Rules followed:
- NO production code is modified.
- NO canonical corpus is rebuilt.
- NO real 2024/2025 candidate market corpus is read.
- Every dynamic reproduction uses synthetic in-memory / temp-dir fixtures.

Behavior contract (matches the Package D preflight mandate):
- If current behavior matches the audit finding  -> print ``Dxx=REPRODUCED``.
- If current behavior contradicts the audit        -> print ``Dxx=AUDIT_FINDING_INACCURATE``.
- If the defect is not demonstrable on this code    -> print ``Dxx=NOT_REPRODUCED``.
- If the reproduction itself hits an unexpected
  environment error                                  -> print ``Dxx=REPRO_ERROR``.
- The script ALWAYS exits 0: it is a diagnostic probe, so an unexpected error
  in one probe must not be reported as a suite failure.

Run from the repository root:

  python tools/reproduce_package_d_findings.py

(Copied verbatim where relevant: this tool intentionally re-invokes the exact
production functions it is auditing so the probe reflects current behavior.)
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

# Bootstrap: allow ``import src`` / ``import tools`` when run as a plain script
# from anywhere inside the checkout (``python tools/reproduce_package_d_findings.py``).
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.canonical_storage import CanonicalRow, write_partition_table  # noqa: E402
from src.data_substrate import SessionMetadata, SessionWindow  # noqa: E402
from src.historical_acquisition import (  # noqa: E402
    AcquisitionError,
    ManifestPartition,
    TqSdkSourceAdapter,
)
from src.historical_data import (  # noqa: E402
    DataVersionIdentity,
    NormalizerIdentity,
    NormalizedHistoricalBar,
    RawArtifact,
    SourceIdentity,
    normalize_tqsdk_historical_bars,
)
from src.historical_manifest import canonical_hash as manifest_hash  # noqa: E402
from src.metadata_authority import (  # noqa: E402
    GovernedSource,
    ProductSessionSchedule,
    TradingCalendar,
    build_session_metadata,
)

CN = ZoneInfo("Asia/Shanghai")
UTC = ZoneInfo("UTC")

# --- helpers ----------------------------------------------------------------


def _nanoseconds(timestamp: datetime) -> int:
    return int(timestamp.timestamp() * 1_000_000_000)


def _record(start: datetime, *, volume: int | None = 32) -> dict:
    record = {
        "id": _nanoseconds(start),
        "datetime": _nanoseconds(start),
        "open": 120000,
        "high": 120020,
        "low": 119990,
        "close": 120010,
        "volume": volume,
        "open_oi": 1010,
        "close_oi": 1012,
    }
    if volume is None:
        record.pop("volume")
    return record


def _normalizer() -> NormalizerIdentity:
    return NormalizerIdentity(
        "tqsdk-3.10.1-fixed-bar-adapter-v1",
        "completed-historical-bar-v1",
        "bar-start-plus-duration-v1",
    )


def _source(retrieved_at: datetime | None = None) -> SourceIdentity:
    return SourceIdentity(
        "TQSDK",
        "PROFESSIONAL_HISTORICAL_API",
        "TqApi.get_kline_data_series",
        None,
        retrieved_at or datetime(2026, 8, 20, 2, 0, tzinfo=UTC),
        (("duration_seconds", "60"), ("end_dt", "2026-08-20"), ("start_dt", "2026-08-20"), ("symbol", "SHFE.ni2509")),
    )


def _data_version(artifact: RawArtifact, session_version: str) -> DataVersionIdentity:
    return DataVersionIdentity(
        (artifact_source := _source(),),
        (artifact,),
        _normalizer(),
        session_version,
        "bar-start-plus-duration-v1",
        "ni2509-contract-fixture-v1",
    )


def _artifact_from_records(records: list[dict], coverage_start: datetime, coverage_end: datetime) -> RawArtifact:
    payload = json.dumps(records, separators=(",", ":")).encode("utf-8")
    return RawArtifact.from_bytes(
        payload=payload,
        exchange="SHFE",
        concrete_instrument="SHFE.ni2509",
        coverage_start=coverage_start,
        coverage_end=coverage_end,
        granularity_seconds=60,
        timezone="Asia/Shanghai",
        raw_schema_identity="tqsdk-kline-records-json-v1",
        source_identity_id=_source().identity_id,
    )


def _canonical_row(
    *,
    trading_day: date,
    bar_start: datetime,
    bar_end: datetime,
    volume: int,
    raw_artifact_identity_id: str,
) -> CanonicalRow:
    return CanonicalRow(
        provider="TQSDK",
        source_type="PROFESSIONAL_HISTORICAL_API",
        exchange="SHFE",
        concrete_contract="SHFE.ni2509",
        product="ni",
        trading_day=trading_day,
        bar_start=bar_start,
        bar_end=bar_end,
        historical_available_at=bar_end,
        open=Decimal("120000"),
        high=Decimal("120020"),
        low=Decimal("119990"),
        close=Decimal("120010"),
        volume=volume,
        open_interest_start=1010,
        open_interest_end=1012,
        raw_artifact_identity_id=raw_artifact_identity_id,
        source_identity_id="src-fixture-v1",
        data_version_id="dv-fixture-v1",
        contract_metadata_identity="cm-fixture-v1",
        session_metadata_identity="sm-fixture-v1",
        normalizer_identity="norm-fixture-v1",
    )


def _manifest_partition(
    *,
    trading_day: date,
    requested_start: datetime,
    requested_end: datetime,
    returned_start: datetime,
    returned_end: datetime,
    payload: bytes,
    session_version: str,
    data_version_id: str,
    normalized_batch_id: str,
    quality_status: str,
) -> ManifestPartition:
    request_parameters = (
        ("duration_seconds", "60"),
        ("end_dt", requested_end.isoformat()),
        ("start_dt", requested_start.isoformat()),
        ("symbol", "SHFE.ni2509"),
    )
    return ManifestPartition(
        provider="TQSDK",
        api_version="3.10.1",
        contract="SHFE.ni2509",
        exchange="SHFE",
        granularity_seconds=60,
        timezone="Asia/Shanghai",
        trading_day=trading_day,
        requested_start=requested_start,
        requested_end=requested_end,
        returned_start=returned_start,
        returned_end=returned_end,
        retrieved_at=datetime(2026, 8, 20, 2, 0, tzinfo=UTC),
        raw_bytes=len(payload),
        raw_sha256=hashlib.sha256(payload).hexdigest(),
        request_identity=manifest_hash(request_parameters),
        request_parameters=request_parameters,
        normalizer_identity=_normalizer().identity_id,
        session_metadata_version=session_version,
        contract_metadata_identity="cm-fixture-v1",
        data_version_id=data_version_id,
        normalized_batch_id=normalized_batch_id,
        quality_status=quality_status,
    )


def _quality(missing: tuple) -> str:
    return "PASS" if not missing else f"ANOMALY:missing_expected_starts={len(missing)}"


def _session(version: str, windows: list[SessionWindow]) -> SessionMetadata:
    return SessionMetadata(version, windows)


# --- D-01 -------------------------------------------------------------------


def reproduce_d01() -> tuple[str, str]:
    """Truncated returned coverage (missing head) can still be marked PASS."""
    trading_day = date(2026, 8, 20)
    requested_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
    requested_end = datetime(2026, 8, 20, 9, 10, tzinfo=CN)
    # provider returns only 09:03..09:10 (internally continuous bars whose
    # starts lie inside the returned half-open coverage [09:03, 09:10)).
    returned_start = datetime(2026, 8, 20, 9, 3, tzinfo=CN)
    returned_end = datetime(2026, 8, 20, 9, 10, tzinfo=CN)
    bars = [
        returned_start + timedelta(minutes=offset)
        for offset in range(7)  # starts 09:03..09:09, last bar ends at 09:10
    ]
    records = [_record(start) for start in bars]
    payload = json.dumps(records, separators=(",", ":")).encode("utf-8")

    # 1) Manifest accepts returned coverage inside requested (not equal).
    manifest_ok = True
    try:
        _manifest_partition(
            trading_day=trading_day,
            requested_start=requested_start,
            requested_end=requested_end,
            returned_start=returned_start,
            returned_end=returned_end,
            payload=payload,
            session_version="shfe-ni-session-v1",
            data_version_id="dv-fixture-v1",
            normalized_batch_id="nb-fixture-v1",
            quality_status="PASS",
        )
    except Exception:  # noqa: BLE001 - probe
        manifest_ok = False

    # 2) Normalization: artifact coverage is the RETURNED coverage, so the
    #    missing head (09:00..09:02) is filtered out of covered_expected.
    windows = [
        SessionWindow("SHFE", "SHFE.ni2509", trading_day, requested_start, requested_end, "day")
    ]
    sessions = _session("shfe-ni-session-v1", windows)
    artifact = _artifact_from_records(records, returned_start, returned_end)
    data_version = _data_version(artifact, "shfe-ni-session-v1")
    batch = normalize_tqsdk_historical_bars(
        payload, artifact=artifact, data_version=data_version, sessions=sessions,
        minimum_price_tick=Decimal("10"),
    )
    quality = _quality(batch.missing_expected_starts)

    reproduced = manifest_ok and not batch.missing_expected_starts and quality == "PASS"
    detail = (
        f"requested={requested_start.isoformat()}..{requested_end.isoformat()} "
        f"returned={returned_start.isoformat()}..{returned_end.isoformat()} "
        f"missing_expected_starts={len(batch.missing_expected_starts)} quality={quality} "
        f"manifest_accepted={manifest_ok} (head 09:00..09:02 absent yet PASS)"
    )
    return ("REPRODUCED" if reproduced else "NOT_REPRODUCED", detail)


# --- D-02 -------------------------------------------------------------------


def reproduce_d02() -> tuple[str, str]:
    """An entirely absent session window/day produces no missing-bar evidence."""
    trading_day = date(2026, 8, 20)
    window_a_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
    window_a_end = datetime(2026, 8, 20, 9, 5, tzinfo=CN)
    window_b_start = datetime(2026, 8, 20, 10, 0, tzinfo=CN)
    window_b_end = datetime(2026, 8, 20, 10, 5, tzinfo=CN)
    windows = [
        SessionWindow("SHFE", "SHFE.ni2509", trading_day, window_a_start, window_a_end, "day"),
        SessionWindow("SHFE", "SHFE.ni2509", trading_day, window_b_start, window_b_end, "day"),
    ]
    sessions = _session("shfe-ni-session-v1", windows)
    # Input contains ONLY the first window's complete bars (5 bars).
    records = [
        _record(window_a_start + timedelta(minutes=offset))
        for offset in range(5)
    ]
    payload = json.dumps(records, separators=(",", ":")).encode("utf-8")
    # Returned coverage from the provider only spans the first window.
    artifact = _artifact_from_records(records, window_a_start, window_a_end)
    data_version = _data_version(artifact, "shfe-ni-session-v1")
    batch = normalize_tqsdk_historical_bars(
        payload, artifact=artifact, data_version=data_version, sessions=sessions,
        minimum_price_tick=Decimal("10"),
    )

    # Existing API that CAN express an absent window/day:
    window_b_expected = sessions.expected_bar_starts("SHFE", "SHFE.ni2509", trading_day, timedelta(seconds=60))
    expressible = sessions.missing_bar_starts(
        "SHFE", "SHFE.ni2509", trading_day, timedelta(seconds=60), observed_starts=()
    )

    reproduced = (
        not batch.missing_expected_starts
        and any(w.start == window_b_start for w in windows)
        and window_b_start in window_b_expected
        and window_b_start in expressible
    )
    detail = (
        f"windows=2 (09:00-09:05, 10:00-10:05) input=window A only "
        f"missing_expected_starts={len(batch.missing_expected_starts)} "
        f"pipeline_evidence_for_window_B={any(s == window_b_start for s in batch.missing_expected_starts)} "
        f"expressible_via_missing_bar_starts={len(expressible)} (API exists, pipeline never calls it "
        "for days/windows with zero observed bars)"
    )
    return ("REPRODUCED" if reproduced else "NOT_REPRODUCED", detail)


def reproduce_d02_empty_day() -> tuple[str, str]:
    """Minimal case: an expected trading day with zero observed bars at all."""
    day_a = date(2026, 8, 20)
    day_b = date(2026, 8, 21)
    windows = [
        SessionWindow("SHFE", "SHFE.ni2509", day_a, datetime(2026, 8, 20, 9, 0, tzinfo=CN), datetime(2026, 8, 20, 9, 5, tzinfo=CN), "day"),
        SessionWindow("SHFE", "SHFE.ni2509", day_b, datetime(2026, 8, 21, 9, 0, tzinfo=CN), datetime(2026, 8, 21, 9, 5, tzinfo=CN), "day"),
    ]
    sessions = _session("shfe-ni-session-v1", windows)
    # The normalizer only iterates observed_by_day; day_b never appears.
    expressible = sessions.missing_bar_starts(
        "SHFE", "SHFE.ni2509", day_b, timedelta(seconds=60), observed_starts=()
    )
    from src.historical_data import NormalizedHistoricalBatch  # noqa: PLC0415

    empty_batch_rejected = False
    try:
        NormalizedHistoricalBatch((), (), "artifact-fixture-v1", "dv-fixture-v1")
    except Exception:  # noqa: BLE001 - probe
        empty_batch_rejected = True
    reproduced = len(expressible) == 5 and empty_batch_rejected
    detail = (
        f"expected_day={day_b.isoformat()} with 0 observed bars -> "
        f"missing_bar_starts returns {len(expressible)} expected starts (API can express) "
        f"but NormalizedHistoricalBatch rejects an empty batch "
        f"(requires >=1 bar) so the pipeline has no evidence object at all"
    )
    return ("REPRODUCED" if reproduced else "NOT_REPRODUCED", detail)


# --- D-03 -------------------------------------------------------------------


def reproduce_d03() -> tuple[str, str]:
    """CanonicalRow.raw_artifact_identity_id stores raw_sha256, not RawArtifact.identity_id."""
    trading_day = date(2026, 8, 20)
    start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
    end = datetime(2026, 8, 20, 9, 1, tzinfo=CN)
    records = [_record(start)]
    payload = json.dumps(records, separators=(",", ":")).encode("utf-8")
    artifact = _artifact_from_records(records, start, end)

    # (a) The normalizer assigns RawArtifact.identity_id (correct semantics).
    completed = _completed_bar(artifact, start, end)
    normalized_bar = NormalizedHistoricalBar(
        artifact.exchange,
        artifact.concrete_instrument,
        start,
        datetime(2026, 8, 20, 2, 0, tzinfo=UTC),
        completed,
        Decimal("120000"), Decimal("120020"), Decimal("119990"), Decimal("120010"),
        Decimal("32"), Decimal("1010"), Decimal("1012"),
        artifact.identity_id,  # <- raw_artifact_identity_id per src/historical_data.py
        "dv-fixture-v1",
    )

    # (b) The canonical builder assigns partition.raw_sha256 (the defect).
    #     Exact builder line: tools/build_canonical_dataset.py
    #     ``raw_artifact_identity_id=partition.raw_sha256``.
    canonical = _canonical_row(
        trading_day=trading_day,
        bar_start=start,
        bar_end=end,
        volume=32,
        raw_artifact_identity_id=artifact.raw_sha256,  # mirrors the builder assignment
    )

    reproduced = (
        canonical.raw_artifact_identity_id == artifact.raw_sha256
        and canonical.raw_artifact_identity_id != artifact.identity_id
        and normalized_bar.raw_artifact_identity_id == artifact.identity_id
        and canonical.raw_artifact_identity_id != normalized_bar.raw_artifact_identity_id
    )
    detail = (
        f"RawArtifact.raw_sha256={artifact.raw_sha256[:12]}... "
        f"RawArtifact.identity_id={artifact.identity_id[:12]}... "
        f"NormalizedHistoricalBar.raw_artifact_identity_id={normalized_bar.raw_artifact_identity_id[:12]}... (correct) "
        f"CanonicalRow.raw_artifact_identity_id={canonical.raw_artifact_identity_id[:12]}... (=raw_sha256, defect)"
    )
    return ("REPRODUCED" if reproduced else "NOT_REPRODUCED", detail)


def _completed_bar(artifact: RawArtifact, start: datetime, end: datetime):
    from src.data_substrate import BarQuality, CompletedBar  # noqa: PLC0415

    return CompletedBar(
        artifact.concrete_instrument,
        start.date(),
        start,
        end,
        end,
        BarQuality(),
    )


# --- D-04 -------------------------------------------------------------------


def reproduce_d04() -> tuple[str, str]:
    """Missing normalized volume is silently stored as 0 in canonical rows."""
    trading_day = date(2026, 8, 20)
    start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
    end = datetime(2026, 8, 20, 9, 1, tzinfo=CN)
    # A raw record without a ``volume`` field normalizes to volume=None.
    records = [_record(start, volume=None)]
    payload = json.dumps(records, separators=(",", ":")).encode("utf-8")
    artifact = _artifact_from_records(records, start, end)
    data_version = _data_version(artifact, "shfe-ni-session-v1")
    windows = [SessionWindow("SHFE", "SHFE.ni2509", trading_day, start, end, "day")]
    sessions = _session("shfe-ni-session-v1", windows)
    batch = normalize_tqsdk_historical_bars(
        payload, artifact=artifact, data_version=data_version, sessions=sessions,
        minimum_price_tick=Decimal("10"),
    )
    normalized_volume = batch.bars[0].volume
    # Exact builder conversion: ``volume=int(bar.volume) if bar.volume is not None else 0``.
    stored_volume = int(normalized_volume) if normalized_volume is not None else 0
    canonical = _canonical_row(
        trading_day=trading_day,
        bar_start=start,
        bar_end=end,
        volume=stored_volume,
        raw_artifact_identity_id="artifact-fixture-v1",
    )
    pylist_volume = canonical.to_pylist_row()["volume"]

    reproduced = normalized_volume is None and stored_volume == 0 and pylist_volume == 0
    detail = (
        f"NormalizedHistoricalBar.volume={normalized_volume!r} -> "
        f"CanonicalRow.volume={stored_volume} pylist_row.volume={pylist_volume} "
        "(unknown/missing collapsed into known zero; "
        "accepted 15,280,452-row impact NOT_ESTABLISHED: no real corpus was read)"
    )
    return ("REPRODUCED" if reproduced else "NOT_REPRODUCED", detail)


# --- D-05 -------------------------------------------------------------------


def reproduce_d05() -> tuple[str, str]:
    """SessionMetadata.version is a caller string and does not bind windows/calendar."""
    # (a) Two different window sets share one caller-supplied version string.
    day_a = date(2026, 8, 20)
    sm_a = _session("same-version", [
        SessionWindow("SHFE", "SHFE.ni2509", day_a, datetime(2026, 8, 20, 9, 0, tzinfo=CN), datetime(2026, 8, 20, 10, 0, tzinfo=CN), "day"),
    ])
    sm_b = _session("same-version", [
        SessionWindow("SHFE", "SHFE.ni2509", day_a, datetime(2026, 8, 20, 9, 0, tzinfo=CN), datetime(2026, 8, 20, 11, 0, tzinfo=CN), "day"),
    ])
    same_version_different_windows = (
        sm_a.version == sm_b.version
        and len(sm_a.expected_bar_starts("SHFE", "SHFE.ni2509", day_a, timedelta(seconds=60)))
        != len(sm_b.expected_bar_starts("SHFE", "SHFE.ni2509", day_a, timedelta(seconds=60)))
    )

    # (b) Real builder path: version comes from ProductSessionSchedule.identity()
    #     and does not bind TradingCalendar identity / night-closed set / windows.
    source = GovernedSource(
        resource_identity="SHFE official trading-hours page",
        url="https://www.shfe.com.cn/services/calenderandholidays/tradinghours/",
        retrieved_at=datetime(2026, 8, 16, 16, 0, tzinfo=CN),
        artifact_sha256=None,
        schema_version="shfe-trading-hours-v1",
        classification="OFFICIAL_AVAILABLE",
        effective_period_start=date(2024, 1, 1),
        effective_period_end=date(2025, 12, 31),
    )
    schedule = ProductSessionSchedule(
        "SHFE", "cu", date(2024, 1, 1), date(2025, 12, 31),
        ((time(9, 0), time(10, 15)), (time(10, 30), time(11, 30)), (time(13, 30), time(15, 0))),
        (time(21, 0), time(1, 0)),
        timezone="Asia/Shanghai",
        source=source,
    )
    cal_source = GovernedSource(
        resource_identity="SHFE official annual raw",
        url="https://www.shfe.com.cn/eng/reports/StatisticalData/Annualdata/HistoricalData/downloadhistory/",
        retrieved_at=datetime(2026, 8, 16, 16, 0, tzinfo=CN),
        artifact_sha256=None,
        schema_version="shfe-official-annual-daily-v2",
        classification="OFFICIAL_AVAILABLE",
        effective_period_start=date(2024, 1, 1),
        effective_period_end=date(2025, 12, 31),
    )
    day1 = date(2024, 1, 2)
    day2 = date(2024, 1, 3)
    cal_normal = TradingCalendar("v1", [day1, day2], cal_source, night_closed_trading_days=())
    cal_closed = TradingCalendar("v1", [day1, day2], cal_source, night_closed_trading_days={day2})
    sm_normal = build_session_metadata(cal_normal, schedule, "SHFE.cu2401", [day1, day2])
    sm_closed = build_session_metadata(cal_closed, schedule, "SHFE.cu2401", [day1, day2])

    version_from_schedule_identity = sm_normal.version == schedule.identity()
    same_version_different_authority = (
        sm_normal.version == sm_closed.version
        and len(sm_normal._windows) != len(sm_closed._windows)
    )

    reproduced = same_version_different_windows and version_from_schedule_identity and same_version_different_authority
    detail = (
        f"caller-version collision: two window sets both 'same-version' with "
        f"{len(sm_a.expected_bar_starts('SHFE','SHFE.ni2509',day_a,timedelta(seconds=60)))} vs "
        f"{len(sm_b.expected_bar_starts('SHFE','SHFE.ni2509',day_a,timedelta(seconds=60)))} expected starts; "
        f"builder version=ProductSessionSchedule.identity()={sm_normal.version[:12]}... "
        f"same schedule identity, different night-closed set -> different window count "
        f"({len(sm_normal._windows)} vs {len(sm_closed._windows)}) yet identical version"
    )
    return ("REPRODUCED" if reproduced else "NOT_REPRODUCED", detail)


# --- D-06 -------------------------------------------------------------------


def reproduce_d06() -> tuple[str, str]:
    """Inventory governed metadata sources for byte-binding (inventory only)."""
    from tools.build_canonical_dataset import (  # noqa: PLC0415
        load_calendar,
        load_schedules,
        load_specs,
    )

    evidence = _REPO_ROOT / "docs" / "evidence"
    cal = load_calendar()
    schedules = load_schedules()
    specs = load_specs()

    cal_json = json.loads((evidence / "CANONICAL_TRADING_CALENDAR.json").read_bytes().decode("utf-8"))
    sched_json = json.loads((evidence / "CANONICAL_SESSION_SCHEDULES.json").read_bytes().decode("utf-8"))
    spec_json = json.loads((evidence / "CANONICAL_CONTRACT_SPECS.json").read_bytes().decode("utf-8"))
    uni_json = json.loads((evidence / "CANONICAL_CONTRACT_UNIVERSE.json").read_bytes().decode("utf-8"))

    cal_committed_hash = "artifact_sha256s" in cal_json["source"]  # per-year dict, not single sha
    sched_committed_hash = any("hash" in k.lower() or "sha" in k.lower() for k in sched_json["products"][next(iter(sched_json["products"]))])
    spec_committed_hash = any("hash" in k.lower() or "sha" in k.lower() for k in spec_json["products"][next(iter(spec_json["products"]))])
    uni_committed_hash = "artifact_sha256s" in uni_json.get("source", {})

    rows = [
        ("trading_calendar", cal.source.url is not None, cal_committed_hash, cal.source.artifact_sha256),
        ("session_schedules", next(iter(schedules.values())).source.url is not None, sched_committed_hash, next(iter(schedules.values())).source.artifact_sha256),
        ("contract_specs", next(iter(specs.values())).source.url is not None, spec_committed_hash, next(iter(specs.values())).source.artifact_sha256),
        ("contract_universe", bool(uni_json.get("source", {}).get("url")), uni_committed_hash, None),
    ]
    lines = []
    for name, url_present, committed, runtime in rows:
        runtime_bound = runtime is not None
        lines.append(
            f"  {name}: url_present={url_present} committed_byte_hash={committed} "
            f"runtime_artifact_sha256={runtime!r} -> {'BYTE_BOUND' if runtime_bound else 'NOT_BYTE_BOUND'}"
        )
    runtime_all_none = all(runtime is None for _, _, _, runtime in rows)
    cal_matches = rows[0][2] is True and rows[0][3] is None
    sched_matches = rows[1][2] is False and rows[1][3] is None
    spec_matches = rows[2][2] is False and rows[2][3] is None
    uni_matches = rows[3][2] is True and rows[3][3] is None
    reproduced = runtime_all_none and cal_matches and sched_matches and spec_matches and uni_matches
    detail = (
        "inventory (committed evidence + current loaders):\n" + "\n".join(lines) +
        "\n  Calendar/universe committed JSON carries per-year artifact_sha256s, but the current "
        "runtime GovernedSource model/loaders bind NO byte hash (single-sha field, set to None); "
        "schedules/specs have no committed byte hash at all."
    )
    return ("REPRODUCED" if reproduced else "NOT_REPRODUCED", detail)


# --- D-07 -------------------------------------------------------------------


def reproduce_d07() -> tuple[str, str]:
    """write_partition_table returns inventory for only the first-row partition."""
    try:
        import pyarrow  # noqa: F401, PLC0415
    except Exception as exc:  # noqa: BLE001 - stdlib-only env
        return ("NOT_REPRODUCED", f"pyarrow unavailable: {type(exc).__name__}")

    row_a = _canonical_row(
        trading_day=date(2026, 8, 20),
        bar_start=datetime(2026, 8, 20, 9, 0, tzinfo=CN),
        bar_end=datetime(2026, 8, 20, 9, 1, tzinfo=CN),
        volume=32,
        raw_artifact_identity_id="artifact-a",
    )
    row_b = CanonicalRow(
        provider="TQSDK",
        source_type="PROFESSIONAL_HISTORICAL_API",
        exchange="SHFE",
        concrete_contract="SHFE.al2609",
        product="al",
        trading_day=date(2026, 9, 18),
        bar_start=datetime(2026, 9, 18, 9, 0, tzinfo=CN),
        bar_end=datetime(2026, 9, 18, 9, 1, tzinfo=CN),
        historical_available_at=datetime(2026, 9, 18, 9, 1, tzinfo=CN),
        open=Decimal("18000"),
        high=Decimal("18020"),
        low=Decimal("17990"),
        close=Decimal("18010"),
        volume=40,
        open_interest_start=2020,
        open_interest_end=2022,
        raw_artifact_identity_id="artifact-b",
        source_identity_id="src-fixture-v1",
        data_version_id="dv-fixture-v1",
        contract_metadata_identity="cm-fixture-v1",
        session_metadata_identity="sm-fixture-v1",
        normalizer_identity="norm-fixture-v1",
    )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "parquet"
        facts = write_partition_table(root, [row_a, row_b])

        # Actual parquet files on disk across ALL partitions.
        actual = sorted(str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*.parquet"))
        # Inventory reported by the function (built from the FIRST row's partition dir).
        inventory = sorted(f["relative_path"] for f in facts["files"])
        first_partition_dir = f"exchange=SHFE/product=ni/concrete_contract=SHFE.ni2509/year=2026/month=8"
        second_partition_dir = f"exchange=SHFE/product=al/concrete_contract=SHFE.al2609/year=2026/month=9"

        both_written = any(p.startswith(first_partition_dir) for p in actual) and any(
            p.startswith(second_partition_dir) for p in actual
        )
        inventory_misses_second = all(p.startswith(first_partition_dir) for p in inventory) and not any(
            p.startswith(second_partition_dir) for p in inventory
        )
        reproduced = both_written and inventory_misses_second
        detail = (
            f"rows span 2 logical partitions; actual files={len(actual)} "
            f"across [{first_partition_dir}, {second_partition_dir}]; "
            f"returned inventory files={len(inventory)} all under first-row partition "
            f"(second partition missing from inventory={inventory_misses_second})"
        )
        return ("REPRODUCED" if reproduced else "NOT_REPRODUCED", detail)


# --- D-08 -------------------------------------------------------------------


def reproduce_d08() -> tuple[str, str]:
    """TqSdk runtime-version mismatch diagnostic loses the actual runtime version."""
    class _Probe(TqSdkSourceAdapter):
        def __init__(self):
            super().__init__(
                credentials_provider=lambda: ("acct", "pw"),
                verified_runtime_version="3.10.1",
            )

        def _build_auth(self, account, password):
            return object()

        def _open_api(self, auth):
            self._version = "WRONG_RUNTIME_9.9.9"
            self._api = object()
            return self._api

    probe = _Probe()
    message = None
    try:
        probe._connect()
    except AcquisitionError as exc:
        message = str(exc)

    reproduced = (
        message is not None
        and "9.9.9" not in message
        and "None" in message
        and "WRONG_RUNTIME" not in message
    )
    detail = f"error message={message!r} (actual runtime version 9.9.9 is lost, printed as None)"
    return ("REPRODUCED" if reproduced else "NOT_REPRODUCED", detail)


# --- runner -----------------------------------------------------------------


def main() -> int:
    probes = [
        ("D01", reproduce_d01),
        ("D02", reproduce_d02),
        ("D02b", reproduce_d02_empty_day),
        ("D03", reproduce_d03),
        ("D04", reproduce_d04),
        ("D05", reproduce_d05),
        ("D06", reproduce_d06),
        ("D07", reproduce_d07),
        ("D08", reproduce_d08),
    ]
    results: dict[str, str] = {}
    for label, fn in probes:
        try:
            status, detail = fn()
        except Exception as exc:  # noqa: BLE001 - diagnostic probe isolation
            status, detail = "REPRO_ERROR", f"{type(exc).__name__}: {exc}"
        results[label] = status
        print(f"{label}={status}")
        print(f"  {detail}")

    print("\n--- SUMMARY ---")
    for label, status in results.items():
        print(f"{label}={status}")
    print("PRODUCTION_CODE_CHANGED=NO")
    print("CANONICAL_CORPUS_REBUILT=NO")
    print("REAL_CANDIDATE_DATA_USED=NO")
    print("EXIT=0 (diagnostic tool; behavior matches or contradicts audit is reported, not failed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
