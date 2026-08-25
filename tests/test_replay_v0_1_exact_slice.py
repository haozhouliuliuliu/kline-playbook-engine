from __future__ import annotations

from datetime import date, datetime, time, timedelta
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from src.historical_manifest import DatasetManifest, ManifestPartition, canonical_hash
from src.replay_v0_1_exact_slice import (
    _parse_calendar,
    _parse_e07,
    _parse_session_schedule,
    build_full_session_mapping_facts,
    select_and_seal_exact_v0_1_slice,
)
from src.replay_v0_1_selector import ReplayPartitionFact, select_v0_1_slice


REPO_ROOT = Path(__file__).resolve().parents[1]
_CN = ZoneInfo("Asia/Shanghai")


class ReplayV01ExactSliceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.calendar_payload = json.loads(
            (REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json").read_text(encoding="utf-8")
        )
        cls.session_payload = json.loads(
            (REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json").read_text(encoding="utf-8")
        )
        cls.e07_payload = json.loads(
            (REPO_ROOT / "docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json").read_text(encoding="utf-8")
        )
        cls.calendar, cls.night_closed, _ = _parse_calendar(cls.calendar_payload)
        cls.sessions, _ = _parse_session_schedule(cls.session_payload)
        cls.e07_records, cls.e07_identity = _parse_e07(cls.e07_payload)
        cls.mapping_facts = build_full_session_mapping_facts(
            trading_calendar=cls.calendar,
            night_closed_days=cls.night_closed,
            session_products=cls.sessions,
            e07_records=cls.e07_records,
            e07_schedule_identity=cls.e07_identity,
        )

    def test_frozen_e07_is_outcome_blind(self) -> None:
        self.assertEqual(self.e07_payload["price_data_used"], "NO")
        self.assertEqual(self.e07_payload["candidate_outcome_data_used"], "NO")
        self.assertEqual(self.e07_payload["semantics"]["derivation"], "SOURCE_GOVERNED")

    def test_cu_switch_day_is_rejected_when_night_and_day_map_to_different_contracts(self) -> None:
        # Frozen E07 switches cu2405 -> cu2406 at 2024-04-09 09:00.
        # CU has a governed night session and 2024-04-09 is not night-closed,
        # so the trading day begins on 2024-04-08 21:00 under the old contract.
        by_day = {
            item.trading_day: item
            for item in self.mapping_facts
            if item.product == "cu"
        }
        self.assertNotIn(date(2024, 4, 9), by_day)
        self.assertEqual(by_day[date(2024, 4, 8)].concrete_contract, "SHFE.cu2405")
        self.assertEqual(by_day[date(2024, 4, 10)].concrete_contract, "SHFE.cu2406")

    def test_night_closed_day_uses_day_session_start(self) -> None:
        # 2024-04-08 is an official night-closed trading day. It is therefore
        # legal to resolve its full trading-day mapping from 09:00 to 15:00.
        self.assertIn(date(2024, 4, 8), self.night_closed)
        cu_fact = next(
            item for item in self.mapping_facts
            if item.product == "cu" and item.trading_day == date(2024, 4, 8)
        )
        self.assertEqual(cu_fact.concrete_contract, "SHFE.cu2405")

    def test_first_cu_candidate_moves_to_april_10_after_full_session_guard(self) -> None:
        # This test intentionally supplies outcome-free synthetic partition
        # identities for the already-accepted cu2406 concrete contract. It
        # verifies only the calendar/E07 selection consequence; the real exact
        # seal must bind identities from the local accepted manifest.
        partitions = tuple(
            ReplayPartitionFact(
                product="cu",
                concrete_contract="SHFE.cu2406",
                trading_day=day,
                partition_identity=f"fixture-part-{day.isoformat()}",
                session_identity="fixture-session",
                eligible=True,
            )
            for day in self.calendar
        )
        selected = select_v0_1_slice(
            trading_calendar=self.calendar,
            mappings=self.mapping_facts,
            partitions=partitions,
        )
        self.assertEqual(selected.product, "cu")
        self.assertEqual(selected.concrete_contract, "SHFE.cu2406")
        self.assertEqual(selected.prior_history_days[0], date(2024, 3, 11))
        self.assertEqual(selected.prior_history_days[-1], date(2024, 4, 9))
        self.assertEqual(selected.burn_in_days, (date(2024, 4, 10), date(2024, 4, 11)))
        self.assertEqual(selected.measurement_days[0], date(2024, 4, 12))
        self.assertEqual(selected.measurement_days[-1], date(2024, 5, 14))
        self.assertEqual(len(selected.measurement_days), 20)

    def test_full_seal_path_binds_manifest_identity_and_real_authorities(self) -> None:
        selected_days = tuple(
            day for day in self.calendar
            if date(2024, 3, 11) <= day <= date(2024, 5, 14)
        )
        self.assertEqual(len(selected_days), 42)
        partitions = []
        for day in selected_days:
            start = datetime.combine(day, time(0, 0), tzinfo=_CN)
            end = start + timedelta(days=1)
            request_parameters = (
                ("duration_seconds", "60"),
                ("end_dt", end.isoformat()),
                ("start_dt", start.isoformat()),
                ("symbol", "SHFE.cu2406"),
            )
            partitions.append(
                ManifestPartition(
                    provider="TQSDK",
                    api_version="3.10.1",
                    contract="SHFE.cu2406",
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
                    normalized_batch_id=f"fixture-batch-{day.isoformat()}",
                    quality_status="PASS",
                )
            )
        manifest = DatasetManifest("fixture-manifest-v1", tuple(partitions))

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            corpus_path = root / "corpus.json"
            DatasetManifest.save(manifest, manifest_path)
            corpus_path.write_text(
                json.dumps(
                    {
                        "canonical_corpus_identity": "fixture-corpus-identity",
                        "raw_manifest_root_identity": manifest.identity(),
                        "partition_count": len(manifest.partitions),
                    }
                ),
                encoding="utf-8",
            )
            seal = select_and_seal_exact_v0_1_slice(
                manifest_path=manifest_path,
                trading_calendar_path=REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json",
                session_schedule_path=REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json",
                e07_path=REPO_ROOT / "docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json",
                corpus_identity_path=corpus_path,
            )

        self.assertEqual(seal.slice.product, "cu")
        self.assertEqual(seal.slice.concrete_contract, "SHFE.cu2406")
        self.assertEqual(seal.slice.burn_in_days[0], date(2024, 4, 10))
        self.assertEqual(seal.slice.measurement_days[-1], date(2024, 5, 14))
        self.assertEqual(seal.raw_manifest_root_identity, manifest.identity())
        self.assertEqual(len(seal.slice.partition_identities), 42)
        self.assertEqual(len(seal.identity), 64)

    def test_full_seal_rejects_manifest_identity_drift(self) -> None:
        day = date(2024, 4, 10)
        start = datetime.combine(day, time(0, 0), tzinfo=_CN)
        end = start + timedelta(days=1)
        request_parameters = (
            ("duration_seconds", "60"),
            ("end_dt", end.isoformat()),
            ("start_dt", start.isoformat()),
            ("symbol", "SHFE.cu2406"),
        )
        partition = ManifestPartition(
            provider="TQSDK",
            api_version="3.10.1",
            contract="SHFE.cu2406",
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
            normalized_batch_id="fixture-batch",
            quality_status="PASS",
        )
        manifest = DatasetManifest("fixture-manifest-v1", (partition,))
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            corpus_path = root / "corpus.json"
            DatasetManifest.save(manifest, manifest_path)
            corpus_path.write_text(
                json.dumps(
                    {
                        "canonical_corpus_identity": "fixture-corpus-identity",
                        "raw_manifest_root_identity": "wrong-manifest-identity",
                        "partition_count": 1,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "manifest identity"):
                select_and_seal_exact_v0_1_slice(
                    manifest_path=manifest_path,
                    trading_calendar_path=REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json",
                    session_schedule_path=REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json",
                    e07_path=REPO_ROOT / "docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json",
                    corpus_identity_path=corpus_path,
                )


if __name__ == "__main__":
    unittest.main()
