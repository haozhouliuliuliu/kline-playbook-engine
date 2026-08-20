"""Tests for the pre-built FAIL-CLOSED repaired canonical candidate corpus
application (``tools/build_repaired_canonical_candidate.py``).

The tests use minimal legal synthetic fixtures built on the REAL governed
session authority (calendar/specs/schedules/universe evidence), so the
fail-closed D01/D02 re-qualification is exercised against the same session
semantics the tool runs in production:

- 116 synthetic target partitions recorded as truncated-PASS in the accepted
  manifest (the exact record shape ``ManifestPartition`` refuses to load),
- qualified replacement raw (full requested coverage) for each target,
- a small number of genuinely PASS inherited partitions with real parquet and
  a rebuildable accepted catalog.

TEST_ONLY / synthetic only: no real corpus, no candidate outcome, and no
materialization of the real 15M-row historical corpus is ever performed here.
"""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from zoneinfo import ZoneInfo

from src.canonical_identity import canonical_hash
from src.canonical_storage import CanonicalCatalog
from src.historical_acquisition import AcquisitionRequest, build_request_parameters
from src.historical_manifest import DatasetManifest
from src.metadata_authority import (
    ContractSpec,
    GovernedSource,
    ProductSessionSchedule,
    TradingCalendar,
)
import tools.build_repaired_canonical_candidate as app
from tools.build_repaired_canonical_candidate import (
    EXPECTED_TARGET_COUNT,
    RepairTarget,
    RepairedCorpusBlocked,
    VerifiedRaw,
    build_repaired_partition,
    run_build,
    validate_roots,
)
from tools.build_canonical_dataset import (
    SOURCE_SPEC,
    build_contract_configs,
    normalize_and_store_partition,
)
from tools.revalidate_canonical_corpus import _partition_identity

CN = ZoneInfo("Asia/Shanghai")
UTC = ZoneInfo("UTC")
INTERVAL = timedelta(seconds=60)
QUALIFICATION_SCHEMA = "canonical-d01-d02-targeted-repair-qualification-v0.1"
ACCEPTED_MANIFEST_SCHEMA = "canonical-balanced-manifest-v1"
ACCEPTED_CATALOG_SCHEMA = "canonical-catalog-v1"
PARENT_IDENTITY = (
    "1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8"
)
INHERITED_COUNT = 2

# --------------------------------------------------------------------------- #
# Shared synthetic fixture
# --------------------------------------------------------------------------- #
_FIXTURE_CONFIGS: dict | None = None
_FIXTURE_PRODUCTS = ("cu", "al", "ni", "au", "ag", "rb")
_FIXTURE_DAY = date(2024, 6, 17)


def _synthetic_contracts() -> list[str]:
    return sorted(
        f"SHFE.{product}24{number:02d}"
        for product in _FIXTURE_PRODUCTS
        for number in range(1, 21)
    )


def _fixture_configs() -> dict:
    """A compact synthetic contract config set on the REAL session machinery.

    Uses a tiny trading calendar (five days) and a short day window so
    ``expected_bar_starts_between`` scans are cheap, while still exercising
    the real ``build_session_metadata`` / ``SessionMetadata`` authority and the
    same fail-closed D01/D02 semantics the tool runs in production.
    """
    global _FIXTURE_CONFIGS
    if _FIXTURE_CONFIGS is None:
        source = GovernedSource(
            resource_identity="fixture-source",
            url="https://example.com/official",
            retrieved_at=datetime(2026, 8, 16, tzinfo=CN),
            artifact_sha256="a" * 64,
            schema_version="v1",
            classification="OFFICIAL_AVAILABLE",
            effective_period_start=date(2024, 1, 1),
            effective_period_end=date(2024, 12, 31),
        )
        days = [
            date(2024, 6, 17),
            date(2024, 6, 18),
            date(2024, 6, 19),
            date(2024, 6, 20),
            date(2024, 6, 21),
        ]
        calendar = TradingCalendar("fixture-calendar-v1", days, source)
        schedules = {
            product: ProductSessionSchedule(
                "SHFE",
                product,
                date(2024, 1, 1),
                date(2024, 12, 31),
                ((time(9, 0), time(10, 0)),),
                None,
                timezone="Asia/Shanghai",
                source=source,
            )
            for product in _FIXTURE_PRODUCTS
        }
        specs = {
            product: ContractSpec(
                "SHFE",
                product,
                product.upper(),
                Decimal("10"),
                "yuan/ton",
                Decimal("5"),
                "ton/lot",
                "yuan/ton",
                "1-12",
                "3",
                binding_notice="fixture",
                effective_start=date(2024, 1, 1),
                effective_end=date(2024, 12, 31),
                source=source,
            )
            for product in _FIXTURE_PRODUCTS
        }
        universe = {
            product: [f"SHFE.{product}24{number:02d}" for number in range(1, 21)]
            for product in _FIXTURE_PRODUCTS
        }
        _FIXTURE_CONFIGS = build_contract_configs(calendar, universe, specs, schedules)
    return _FIXTURE_CONFIGS


def _record(start: datetime, contract: str) -> dict:
    """A synthetic TqSdk-style raw record with prices that are exact multiples
    of the contract's minimum tick (string-encoded for exact Decimal parsing)."""
    tick = _fixture_configs()[contract].minimum_price_tick
    return {
        "datetime": int(start.timestamp() * 1_000_000_000),
        "symbol": contract,
        "open": str(Decimal(100) * tick),
        "high": str(Decimal(101) * tick),
        "low": str(Decimal(99) * tick),
        "close": str(Decimal(100) * tick),
        "volume": "100",
        "open_oi": "1000",
        "close_oi": "1001",
    }


def _payload(starts: list[datetime], contract: str) -> bytes:
    return json.dumps(
        [_record(start, contract) for start in starts],
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _window(contract: str, day: date):
    """A 2-minute day-session window guaranteed to align with the real session
    authority; returns (requested_start, requested_end, expected_starts)."""
    requested_start = datetime.combine(day, time(9, 0), tzinfo=CN)
    requested_end = requested_start + timedelta(minutes=2)
    expected = _fixture_configs()[contract].sessions.expected_bar_starts_between(
        contract.split(".")[0], contract, requested_start, requested_end, INTERVAL
    )
    assert len(expected) == 2, (contract, day, expected)
    return requested_start, requested_end, expected


def _request_parameters(contract: str, day: date, requested_start: datetime, requested_end: datetime):
    request = AcquisitionRequest(
        exchange=contract.split(".")[0],
        concrete_instrument=contract,
        trading_day=day,
        granularity_seconds=60,
        requested_start=requested_start,
        requested_end=requested_end,
    )
    return build_request_parameters(request, SOURCE_SPEC.request_parameter_names)


def _accepted_target_record(
    contract: str, day: date, requested_start: datetime, requested_end: datetime, expected: list
) -> dict:
    """An accepted truncated-PASS record (missing the first expected bar), the
    exact shape the repaired ``ManifestPartition`` refuses to load."""
    config = _fixture_configs()[contract]
    truncated = expected[1:]
    payload = _payload(truncated, contract)
    returned_start = truncated[0]
    returned_end = truncated[-1] + INTERVAL
    request_parameters = _request_parameters(contract, day, requested_start, requested_end)
    return {
        "provider": "TQSDK",
        "api_version": "3.10.1",
        "contract": contract,
        "exchange": "SHFE",
        "granularity_seconds": 60,
        "timezone": "Asia/Shanghai",
        "trading_day": day.isoformat(),
        "requested_coverage_start": requested_start.isoformat(),
        "requested_coverage_end": requested_end.isoformat(),
        "returned_coverage_start": returned_start.isoformat(),
        "returned_coverage_end": returned_end.isoformat(),
        "retrieved_at": "2026-08-19T02:00:00+00:00",
        "raw_bytes": len(payload),
        "raw_sha256": hashlib.sha256(payload).hexdigest(),
        "request_identity": canonical_hash(request_parameters),
        "request_parameters": [[name, value] for name, value in request_parameters],
        "normalizer_identity": SOURCE_SPEC.normalizer.identity_id,
        "session_metadata_version": config.sessions.version,
        "contract_metadata_identity": config.metadata_fact.identity_id(),
        "data_version_id": "accepted-dv-v1",
        "normalized_batch_id": "accepted-nb-v1",
        "quality_status": "PASS",
    }


def _make_fixture_target(
    contract: str, day: date, requested_start: datetime, requested_end: datetime, raw_path: Path
) -> RepairTarget:
    diagnostic = {
        "contract": contract,
        "trading_day": day.isoformat(),
        "granularity_seconds": 60,
        "requested_start": requested_start.isoformat(),
        "requested_end": requested_end.isoformat(),
    }
    return RepairTarget(
        partition_identity="fixture",
        diagnostic=diagnostic,
        accepted_partition={},
        candidate_raw_path=Path(raw_path),
    )


def _write_inherited(partition, payload: bytes, raw_scratch_dir: Path, parquet_dir: Path, config):
    request = AcquisitionRequest(
        exchange=partition.exchange,
        concrete_instrument=partition.contract,
        trading_day=partition.trading_day,
        granularity_seconds=partition.granularity_seconds,
        requested_start=partition.requested_start,
        requested_end=partition.requested_end,
    )
    raw_path = raw_scratch_dir / request.raw_file_name("TQSDK")
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_bytes(payload)
    return normalize_and_store_partition(
        partition,
        raw_scratch_dir,
        parquet_dir,
        config.sessions,
        config.metadata_fact.identity_id(),
        config.minimum_price_tick,
    )


def _build_evidence(diagnostics: list[dict]) -> dict:
    return {
        "schema_version": QUALIFICATION_SCHEMA,
        "source_failure_evidence_commit": "a9e306550c5dc47695e4c27c1812de4c3cad5641",
        "source_failure_evidence_path": (
            "docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json"
        ),
        "target_partition_count": len(diagnostics),
        "target_selection_rule": "exact failure_partitions from committed revalidation evidence only",
        "outcome_access_used": False,
        "historical_accepted_corpus_modified": False,
        "targeted_reacquisition_attempted": True,
        "targeted_reacquisition_success_count": len(diagnostics),
        "repaired_pass_count": sum(
            1 for item in diagnostics if item["qualification_status"] == "REPAIRED_PASS"
        ),
        "still_d01_truncated_count": sum(
            1 for item in diagnostics if item["qualification_status"] == "STILL_D01_TRUNCATED"
        ),
        "still_d02_missing_count": sum(
            1 for item in diagnostics if item["qualification_status"] == "STILL_D02_MISSING"
        ),
        "acquisition_failed_count": sum(
            1 for item in diagnostics if item["qualification_status"] == "ACQUISITION_FAILED"
        ),
        "authority_mismatch_count": sum(
            1 for item in diagnostics if item["authority_boundary_reasons"]
        ),
        "historical_provider_value_drift_count": sum(
            1 for item in diagnostics if item.get("historical_provider_value_drift")
        ),
        "overlapping_ohlc_values_compared": 0,
        "overlapping_ohlc_mismatch_count": 0,
        "result": "ALL_116_REPLACEMENTS_QUALIFIED",
        "blocker": None,
        "diagnostics": diagnostics,
        "summaries": {},
        "systematic_pattern_observations": {},
    }


def _build_synthetic_corpus(tmp: Path) -> SimpleNamespace:
    """Build a minimal legal synthetic accepted root, repair raws, and a fully
    qualified (116/116 REPAIRED_PASS) qualification evidence document."""
    configs = _fixture_configs()
    day = _FIXTURE_DAY
    all_contracts = _synthetic_contracts()
    target_contracts = all_contracts[:EXPECTED_TARGET_COUNT]
    target_set = set(target_contracts)
    inherited_contracts = [
        contract for contract in all_contracts if contract not in target_set
    ][:INHERITED_COUNT]

    accepted_root = tmp / "accepted"
    repair_root = tmp / "repair_raw"
    scratch_raw = tmp / "scratch_raw"
    output_root = tmp / "output"
    evidence_path = tmp / "evidence.json"
    (accepted_root / "parquet").mkdir(parents=True, exist_ok=True)

    accepted_target_records: list[dict] = []
    diagnostics: list[dict] = []
    targets: list[dict] = []

    for contract in target_contracts:
        config = configs[contract]
        requested_start, requested_end, expected = _window(contract, day)
        record = _accepted_target_record(
            contract, day, requested_start, requested_end, expected
        )
        accepted_target_records.append(record)
        payload = _payload(expected, contract)
        request = AcquisitionRequest(
            exchange=contract.split(".")[0],
            concrete_instrument=contract,
            trading_day=day,
            granularity_seconds=60,
            requested_start=requested_start,
            requested_end=requested_end,
        )
        raw_path = repair_root / request.raw_file_name("TQSDK")
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(payload)
        targets.append(
            {
                "contract": contract,
                "day": day,
                "requested_start": requested_start,
                "requested_end": requested_end,
                "expected": expected,
                "raw_path": raw_path,
                "payload": payload,
            }
        )
        diagnostics.append(
            {
                "partition_identity": _partition_identity(record),
                "product": contract.split(".")[1][:2].lower(),
                "contract": contract,
                "trading_day": day.isoformat(),
                "calendar_month": day.strftime("%Y-%m"),
                "provider": "TQSDK",
                "granularity_seconds": 60,
                "requested_start": requested_start.isoformat(),
                "requested_end": requested_end.isoformat(),
                "returned_start": record["returned_coverage_start"],
                "returned_end": record["returned_coverage_end"],
                "missing_expected_bar_count": 1,
                "truncation_shape": "START_ONLY",
                "missing_region_shape": "PREFIX_ONLY",
                "missing_regions": [],
                "current_session_windows": [],
                "session_class": "DAY_ONLY",
                "missing_session_class": "DAY_ONLY",
                "missing_starts_at_requested_boundary": True,
                "listing_effective_coverage": "WITHIN_GOVERNED_LISTING_COVERAGE",
                "listing_first_trading_day": "2024-01-02",
                "listing_last_trading_day": "2025-12-31",
                "authority_boundary_reasons": [],
                "qualification_status": "REPAIRED_PASS",
                "candidate_raw_path": str(raw_path).replace("\\", "/"),
                "candidate_returned_start": requested_start.isoformat(),
                "candidate_returned_end": requested_end.isoformat(),
                "candidate_retrieved_at": "2026-08-21T00:00:00+00:00",
            }
        )

    accepted_inherited_records: list[dict] = []
    inherited_stored: list = []
    for contract in inherited_contracts:
        config = configs[contract]
        requested_start, requested_end, expected = _window(contract, day)
        payload = _payload(expected, contract)
        retrieved_at = datetime(2026, 8, 19, 2, 0, tzinfo=UTC)
        target = _make_fixture_target(
            contract, day, requested_start, requested_end, Path("unused")
        )
        verified = VerifiedRaw(
            payload,
            expected[0],
            expected[-1] + INTERVAL,
            hashlib.sha256(payload).hexdigest(),
        )
        partition = build_repaired_partition(target, verified, config, retrieved_at)
        stored = _write_inherited(
            partition, payload, scratch_raw, accepted_root / "parquet", config
        )
        accepted_inherited_records.append(partition.to_dict())
        inherited_stored.append(stored)

    accepted_partitions = sorted(
        accepted_target_records + accepted_inherited_records,
        key=lambda item: _partition_identity(item),
    )
    accepted_manifest = {
        "schema_version": ACCEPTED_MANIFEST_SCHEMA,
        "manifest_identity": canonical_hash(
            {
                "schema_version": ACCEPTED_MANIFEST_SCHEMA,
                "partitions": [_partition_identity(item) for item in accepted_partitions],
            }
        ),
        "partitions": accepted_partitions,
    }
    (accepted_root / "manifest.json").write_text(
        json.dumps(accepted_manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    catalog = CanonicalCatalog(accepted_root / "catalog.sqlite")
    try:
        catalog.set_meta("schema_version", ACCEPTED_CATALOG_SCHEMA)
        for stored in inherited_stored:
            catalog.upsert_partition(stored.entry)
    finally:
        catalog.close()

    evidence = _build_evidence(diagnostics)
    evidence_path.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )

    return SimpleNamespace(
        accepted_root=accepted_root,
        repair_root=repair_root,
        output_root=output_root,
        evidence=evidence,
        evidence_path=evidence_path,
        targets=targets,
        accepted_inherited_records=accepted_inherited_records,
        day=day,
    )


def _mutate_status(corpus, index: int, status: str) -> None:
    diagnostics = list(corpus.evidence["diagnostics"])
    diagnostic = dict(diagnostics[index])
    diagnostic["qualification_status"] = status
    diagnostics[index] = diagnostic
    corpus.evidence = _build_evidence(diagnostics)
    corpus.evidence_path.write_text(
        json.dumps(corpus.evidence, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _mutate_drift(corpus, index: int) -> None:
    diagnostics = list(corpus.evidence["diagnostics"])
    diagnostic = dict(diagnostics[index])
    diagnostic["historical_provider_value_drift"] = True
    diagnostics[index] = diagnostic
    corpus.evidence = _build_evidence(diagnostics)
    corpus.evidence_path.write_text(
        json.dumps(corpus.evidence, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _mutate_repair_raw_truncated(corpus, index: int) -> None:
    """Replace one on-disk replacement raw with a truncated payload AND align
    the diagnostic's candidate returned coverage, so the pure on-disk D01
    check (not the evidence-vs-disk check) must fire."""
    spec = corpus.targets[index]
    truncated = spec["expected"][1:]
    payload = _payload(truncated, spec["contract"])
    spec["raw_path"].write_bytes(payload)
    diagnostics = list(corpus.evidence["diagnostics"])
    diagnostic = dict(diagnostics[index])
    diagnostic["candidate_returned_start"] = truncated[0].isoformat()
    diagnostic["candidate_returned_end"] = (truncated[-1] + INTERVAL).isoformat()
    diagnostics[index] = diagnostic
    corpus.evidence = _build_evidence(diagnostics)
    corpus.evidence_path.write_text(
        json.dumps(corpus.evidence, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _write_evidence(corpus) -> None:
    corpus.evidence_path.write_text(
        json.dumps(corpus.evidence, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


# --------------------------------------------------------------------------- #
# Root / gate boundary tests
# --------------------------------------------------------------------------- #
class RootAndGateBoundaryTests(unittest.TestCase):
    def test_historical_root_overwrite_rejected(self) -> None:
        historical = Path("C:/accepted/canonical")
        repair = Path("C:/repair/raw")
        with self.assertRaises(RepairedCorpusBlocked):
            validate_roots(historical, repair, historical)
        with self.assertRaises(RepairedCorpusBlocked):
            validate_roots(historical, repair, historical / "child")
        with self.assertRaises(RepairedCorpusBlocked):
            validate_roots(historical, historical, Path("C:/out"))
        # A genuinely independent output root is allowed.
        validate_roots(historical, repair, Path("C:/out"))

    def test_committed_not_attempted_evidence_hard_stops(self) -> None:
        """The real committed qualification evidence is BLOCKED/NOT_ATTEMPTED:
        the application must refuse to materialize today, before touching any
        corpus root."""
        evidence = app.DEFAULT_EVIDENCE
        with self.assertRaises(RepairedCorpusBlocked) as caught:
            run_build(
                historical_root=Path("C:/unused/historical"),
                evidence_path=evidence,
                repair_raw_root=Path("C:/unused/repair"),
                output_root=Path("C:/unused/output"),
            )
        self.assertIn("qualification gate closed", str(caught.exception))


# --------------------------------------------------------------------------- #
# Application tests
# --------------------------------------------------------------------------- #
class RepairedCorpusApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original = app.build_contract_configs
        app.build_contract_configs = lambda *args, **kwargs: _fixture_configs()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(setattr, app, "build_contract_configs", self._original)

    def test_116_of_116_qualified_materializes(self) -> None:
        corpus = _build_synthetic_corpus(Path(self._tmp.name))
        report = run_build(
            historical_root=corpus.accepted_root,
            evidence_path=corpus.evidence_path,
            repair_raw_root=corpus.repair_root,
            output_root=corpus.output_root,
        )
        self.assertEqual(116, report["repaired_partition_count"])
        self.assertEqual(INHERITED_COUNT, report["inherited_partition_count"])
        self.assertTrue(report["materialization_run"])
        identity = report["repaired_candidate_identity"]
        self.assertIsNotNone(identity)
        self.assertNotEqual(PARENT_IDENTITY, identity)

        # New manifest: all partitions PASS; inherited preserved; repaired new.
        manifest = DatasetManifest.load(corpus.output_root / "manifest.json")
        self.assertEqual(116 + INHERITED_COUNT, len(manifest.partitions))
        self.assertTrue(all(p.quality_status == "PASS" for p in manifest.partitions))

        inherited_ids = {
            _partition_identity(item) for item in corpus.accepted_inherited_records
        }
        repaired_ids = {
            item["partition_identity"] for item in corpus.evidence["diagnostics"]
        }
        for partition in manifest.partitions:
            if _partition_identity(partition.to_dict()) in inherited_ids:
                # inherited partition identity is byte-identical to accepted
                self.assertIn(_partition_identity(partition.to_dict()), inherited_ids)
                self.assertNotIn(_partition_identity(partition.to_dict()), repaired_ids)
        # every repaired partition replaced the accepted target identity
        manifest_ids = {p.identity() for p in manifest.partitions}
        self.assertFalse(repaired_ids & manifest_ids)
        self.assertTrue(inherited_ids <= manifest_ids)

        # Deterministic artifacts present.
        for name in (
            "manifest.json",
            "quality_summary.json",
            "identity.json",
            "lineage.json",
            "build_report.json",
        ):
            self.assertTrue((corpus.output_root / name).is_file(), name)
        self.assertTrue((corpus.output_root / "catalog.sqlite").is_file())
        self.assertTrue((corpus.output_root / "parquet").is_dir())

        quality = json.loads(
            (corpus.output_root / "quality_summary.json").read_text(encoding="utf-8")
        )
        self.assertTrue(quality["all_accepted"])
        self.assertEqual({"PASS": 116 + INHERITED_COUNT}, quality["by_status"])

        lineage = json.loads(
            (corpus.output_root / "lineage.json").read_text(encoding="utf-8")
        )
        self.assertEqual(PARENT_IDENTITY, lineage["parent_canonical_corpus_identity"])
        self.assertFalse(lineage["historical_accepted_corpus_modified"])

        catalog = CanonicalCatalog(corpus.output_root / "catalog.sqlite")
        try:
            self.assertEqual(116 + INHERITED_COUNT, catalog.partition_count())
        finally:
            catalog.close()

    def test_115_of_116_rejected_no_output(self) -> None:
        corpus = _build_synthetic_corpus(Path(self._tmp.name))
        _mutate_status(corpus, 0, "STILL_D01_TRUNCATED")
        with self.assertRaises(RepairedCorpusBlocked) as caught:
            run_build(
                historical_root=corpus.accepted_root,
                evidence_path=corpus.evidence_path,
                repair_raw_root=corpus.repair_root,
                output_root=corpus.output_root,
            )
        self.assertIn("REPAIRED_PASS_NE_116", str(caught.exception))
        self.assertFalse(corpus.output_root.exists())

    def test_one_d02_fail_rejected_no_output(self) -> None:
        corpus = _build_synthetic_corpus(Path(self._tmp.name))
        _mutate_status(corpus, 7, "STILL_D02_MISSING")
        with self.assertRaises(RepairedCorpusBlocked) as caught:
            run_build(
                historical_root=corpus.accepted_root,
                evidence_path=corpus.evidence_path,
                repair_raw_root=corpus.repair_root,
                output_root=corpus.output_root,
            )
        self.assertIn("STILL_D02_NE_0", str(caught.exception))
        self.assertFalse(corpus.output_root.exists())

    def test_one_drift_rejected_no_output(self) -> None:
        corpus = _build_synthetic_corpus(Path(self._tmp.name))
        _mutate_drift(corpus, 3)
        with self.assertRaises(RepairedCorpusBlocked) as caught:
            run_build(
                historical_root=corpus.accepted_root,
                evidence_path=corpus.evidence_path,
                repair_raw_root=corpus.repair_root,
                output_root=corpus.output_root,
            )
        self.assertIn("DRIFT_NE_0", str(caught.exception))
        self.assertFalse(corpus.output_root.exists())

    def test_defective_replacement_raw_blocks_even_if_evidence_says_pass(self) -> None:
        """PASS-only storage: a replacement raw that is defective on disk is a
        HARD STOP even when the evidence claims REPAIRED_PASS."""
        corpus = _build_synthetic_corpus(Path(self._tmp.name))
        _mutate_repair_raw_truncated(corpus, 5)
        with self.assertRaises(RepairedCorpusBlocked) as caught:
            run_build(
                historical_root=corpus.accepted_root,
                evidence_path=corpus.evidence_path,
                repair_raw_root=corpus.repair_root,
                output_root=corpus.output_root,
            )
        self.assertIn("STILL_D01_TRUNCATED on disk", str(caught.exception))
        self.assertFalse(corpus.output_root.exists())

    def test_dry_run_writes_nothing(self) -> None:
        corpus = _build_synthetic_corpus(Path(self._tmp.name))
        report = run_build(
            historical_root=corpus.accepted_root,
            evidence_path=corpus.evidence_path,
            repair_raw_root=corpus.repair_root,
            output_root=corpus.output_root,
            dry_run=True,
        )
        self.assertTrue(report["dry_run"])
        self.assertFalse(report["materialization_run"])
        self.assertTrue(report["gate"]["gate_open"])
        self.assertFalse(corpus.output_root.exists())

    def test_deterministic_identity(self) -> None:
        corpus = _build_synthetic_corpus(Path(self._tmp.name))
        first = run_build(
            historical_root=corpus.accepted_root,
            evidence_path=corpus.evidence_path,
            repair_raw_root=corpus.repair_root,
            output_root=corpus.output_root / "out1",
        )
        second = run_build(
            historical_root=corpus.accepted_root,
            evidence_path=corpus.evidence_path,
            repair_raw_root=corpus.repair_root,
            output_root=corpus.output_root / "out2",
        )
        self.assertEqual(first["repaired_candidate_identity"], second["repaired_candidate_identity"])
        self.assertNotEqual(PARENT_IDENTITY, first["repaired_candidate_identity"])
        first_manifest = DatasetManifest.load(corpus.output_root / "out1" / "manifest.json")
        second_manifest = DatasetManifest.load(corpus.output_root / "out2" / "manifest.json")
        self.assertEqual(first_manifest.identity(), second_manifest.identity())


class ToolBoundaryTests(unittest.TestCase):
    def test_no_outcome_dependency(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (root / "tools/build_repaired_canonical_candidate.py").read_text(encoding="utf-8")
        imports = "\n".join(
            line for line in source.splitlines()
            if line.startswith("from ") or line.startswith("import ")
        ).lower()
        self.assertNotIn("outcome", imports)
        self.assertNotIn("validation", imports)

    def test_never_writes_acceptance_or_historical_acceptance(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (root / "tools/build_repaired_canonical_candidate.py").read_text(encoding="utf-8")
        # The tool may document the old acceptance as a boundary, but it must
        # never write to it, and the only write roots it owns are the
        # independent output root.
        for line in source.splitlines():
            if any(
                marker in line
                for marker in ("write_text", ".save(", "write_bytes", "copy2")
            ):
                self.assertNotIn("CANONICAL_DATASET_ACCEPTANCE", line)
                self.assertNotIn("historical_accepted_corpus_modified': True", line)
        self.assertIn("data/repaired_candidate_v01", source)


if __name__ == "__main__":
    unittest.main()
