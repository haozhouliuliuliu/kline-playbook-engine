from __future__ import annotations

from datetime import date, datetime, time, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from src.historical_manifest import ManifestPartition, canonical_hash
from src.replay_v0_1_qualified_manifest import (
    build_revalidated_partition_facts,
    raw_partition_identity,
    select_and_seal_revalidated_exact_v0_1_slice,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
_CN = ZoneInfo("Asia/Shanghai")


def _good_partition(day: date, contract: str = "SHFE.cu2406") -> dict:
    start = datetime.combine(day, time(0, 0), tzinfo=_CN)
    end = start + timedelta(days=1)
    request_parameters = (
        ("duration_seconds", "60"),
        ("end_dt", end.isoformat()),
        ("start_dt", start.isoformat()),
        ("symbol", contract),
    )
    partition = ManifestPartition(
        provider="TQSDK",
        api_version="3.10.1",
        contract=contract,
        exchange="SHFE",
        granularity_seconds=60,
        timezone="Asia/Shanghai",
        trading_day=day,
        requested_start=start,
        requested_end=end,
        returned_start=start,
        returned_end=end,
        retrieved_at=end,
        raw_bytes=1,
        raw_sha256="0" * 64,
        request_identity=canonical_hash(request_parameters),
        request_parameters=request_parameters,
        normalizer_identity="fixture-normalizer",
        session_metadata_version="fixture-session",
        contract_metadata_identity="fixture-contract-metadata",
        data_version_id="fixture-data-version",
        normalized_batch_id=f"fixture-batch-{contract}-{day.isoformat()}",
        quality_status="PASS",
    )
    return partition.to_dict()


def _legacy_bad_partition(day: date, contract: str = "SHFE.cu2501") -> dict:
    raw = _good_partition(day, contract)
    raw["returned_coverage_start"] = (
        datetime.fromisoformat(raw["requested_coverage_start"]) + timedelta(minutes=1)
    ).isoformat()
    return raw


def _manifest(raw_partitions: list[dict]) -> dict:
    ordered = sorted(
        raw_partitions,
        key=lambda item: (
            item["provider"], item["contract"], item["granularity_seconds"], item["timezone"],
            item["trading_day"], item["requested_coverage_start"], item["requested_coverage_end"],
        ),
    )
    identity = canonical_hash(
        {
            "schema_version": "fixture-manifest-v1",
            "partitions": [raw_partition_identity(item) for item in ordered],
        }
    )
    return {
        "schema_version": "fixture-manifest-v1",
        "manifest_identity": identity,
        "partitions": ordered,
    }


def _revalidation(manifest: dict, failures: list[dict]) -> dict:
    failure_entries = []
    for raw in failures:
        contract = raw["contract"]
        product = contract.split(".", 1)[1].rstrip("0123456789")
        failure_entries.append(
            {
                "contract": contract,
                "historical_quality_status": raw["quality_status"],
                "partition_identity": raw_partition_identity(raw),
                "product": product,
                "reasons": ["D01_RETURNED_COVERAGE_TRUNCATED", "D02_MISSING_EXPECTED_BARS"],
                "trading_day": raw["trading_day"],
            }
        )
    count = len(manifest["partitions"])
    fail = len(failure_entries)
    return {
        "schema_version": "canonical-corpus-revalidation-d01-d02-v0.1",
        "revalidation_result": "FAIL_REPAIRED_COMPLETENESS",
        "revalidation_identity": "1" * 64,
        "recomputed_manifest_identity": manifest["manifest_identity"],
        "recorded_manifest_identity": manifest["manifest_identity"],
        "partition_count": count,
        "pass_count": count - fail,
        "fail_count": fail,
        "d01_failure_count": fail,
        "d02_failure_count": fail,
        "truncated_partition_count": fail,
        "catalog_summary": {"catalog_partitions": count},
        "reason_counts": {
            "D01_RETURNED_COVERAGE_TRUNCATED": fail,
            "D02_MISSING_EXPECTED_BARS": fail,
        },
        "failure_partitions": failure_entries,
    }


class ReplayV01QualifiedManifestTests(unittest.TestCase):
    def test_formal_failure_is_excluded_without_weakening_strict_manifest_guard(self) -> None:
        good = _good_partition(date(2024, 4, 10))
        bad = _legacy_bad_partition(date(2024, 1, 16))
        with self.assertRaisesRegex(ValueError, "PASS requires full requested coverage"):
            ManifestPartition.from_dict(bad)
        manifest = _manifest([good, bad])
        facts, qualification = build_revalidated_partition_facts(
            manifest_payload=manifest,
            revalidation_payload=_revalidation(manifest, [bad]),
            expected_manifest_identity=manifest["manifest_identity"],
            expected_partition_count=2,
        )
        by_identity = {item.partition_identity: item for item in facts}
        self.assertTrue(by_identity[raw_partition_identity(good)].eligible)
        self.assertFalse(by_identity[raw_partition_identity(bad)].eligible)
        self.assertEqual(qualification.qualified_partition_count, 1)
        self.assertEqual(qualification.excluded_partition_count, 1)

    def test_revalidation_failure_identity_must_exist_in_exact_accepted_manifest(self) -> None:
        good = _good_partition(date(2024, 4, 10))
        bad = _legacy_bad_partition(date(2024, 1, 16))
        manifest = _manifest([good])
        report = _revalidation(manifest, [])
        report["fail_count"] = 1
        report["d01_failure_count"] = 1
        report["d02_failure_count"] = 1
        report["truncated_partition_count"] = 1
        report["pass_count"] = 0
        report["reason_counts"] = {
            "D01_RETURNED_COVERAGE_TRUNCATED": 1,
            "D02_MISSING_EXPECTED_BARS": 1,
        }
        report["failure_partitions"] = _revalidation(_manifest([bad]), [bad])["failure_partitions"]
        with self.assertRaisesRegex(ValueError, "does not exist in accepted raw manifest"):
            build_revalidated_partition_facts(
                manifest_payload=manifest,
                revalidation_payload=report,
                expected_manifest_identity=manifest["manifest_identity"],
                expected_partition_count=1,
            )

    def test_unrelated_legacy_failure_no_longer_blocks_first_cu2406_slice(self) -> None:
        calendar_payload = json.loads(
            (REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json").read_text(encoding="utf-8")
        )
        calendar = tuple(
            date.fromisoformat(item)
            for year in sorted(calendar_payload["trading_days"])
            for item in calendar_payload["trading_days"][year]
        )
        selected_days = [day for day in calendar if date(2024, 3, 11) <= day <= date(2024, 5, 14)]
        self.assertEqual(len(selected_days), 42)
        good = [_good_partition(day) for day in selected_days]
        unrelated_bad = _legacy_bad_partition(date(2024, 1, 16))
        manifest = _manifest(good + [unrelated_bad])
        report = _revalidation(manifest, [unrelated_bad])
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            corpus_path = root / "corpus.json"
            report_path = root / "revalidation.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report_path.write_text(json.dumps(report), encoding="utf-8")
            corpus_path.write_text(
                json.dumps(
                    {
                        "canonical_corpus_identity": "fixture-corpus",
                        "raw_manifest_root_identity": manifest["manifest_identity"],
                        "partition_count": len(manifest["partitions"]),
                    }
                ),
                encoding="utf-8",
            )
            seal = select_and_seal_revalidated_exact_v0_1_slice(
                manifest_path=manifest_path,
                revalidation_path=report_path,
                trading_calendar_path=REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json",
                session_schedule_path=REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json",
                e07_path=REPO_ROOT / "docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json",
                corpus_identity_path=corpus_path,
            )
        self.assertEqual(seal.slice.product, "cu")
        self.assertEqual(seal.slice.concrete_contract, "SHFE.cu2406")
        self.assertEqual(seal.slice.burn_in_days, (date(2024, 4, 10), date(2024, 4, 11)))
        self.assertEqual(seal.slice.measurement_days[-1], date(2024, 5, 14))
        self.assertEqual(seal.revalidation_identity, "1" * 64)
        self.assertEqual(seal.excluded_partition_count, 1)
        self.assertNotEqual(seal.identity, seal.base_seal.identity)

    def test_repository_revalidation_excludes_116_and_not_cu2406(self) -> None:
        report = json.loads(
            (REPO_ROOT / "docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["partition_count"], 32980)
        self.assertEqual(report["pass_count"], 32864)
        self.assertEqual(report["fail_count"], 116)
        self.assertEqual(report["revalidation_identity"], "42e0de64e47c91156f82bbd09b53e404e93a69eebd2bc2e950c8b58c8753af32")
        self.assertEqual(len(report["failure_partitions"]), 116)
        self.assertFalse(any(item["contract"] == "SHFE.cu2406" for item in report["failure_partitions"]))


if __name__ == "__main__":
    unittest.main()
