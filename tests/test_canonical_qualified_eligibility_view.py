from __future__ import annotations

from dataclasses import replace
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.canonical_identity import canonical_hash
from src.candidate_eligibility import (
    CandidateCanonicalInputGateway,
    CandidateEligibilityError,
    CandidateEligibilityGate,
    CandidateQualityDataIdentity,
    ConcreteContractMappingResult,
    EXCLUSION_RULE,
    EligibilityPartition,
    QualifiedEligibilityView,
    UNRESOLVED_FAIL_CLOSED,
)
from src.research_firewall import ResearchFirewall
from src.strategy_evidence import EvidenceLedger
from tools.build_canonical_qualified_eligibility_view import (
    DEFAULT_PARENT_DATA_ROOT,
    EXPECTED_CLEAN_FIRST_DAYS,
    EXPECTED_ELIGIBLE_PARTITIONS,
    EXPECTED_EXCLUDED_PARTITIONS,
    EXPECTED_EXCLUDED_ROWS,
    EXPECTED_FAILURES,
    PARENT_CORPUS_IDENTITY,
    _adoption_payload,
    _implementation_identity,
    _load_object,
    build_view,
)


class CanonicalQualifiedEligibilityViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        cls.root = root
        cls.manifest = _load_object(DEFAULT_PARENT_DATA_ROOT / "canonical" / "manifest.json")
        cls.universe = _load_object(root / "docs" / "evidence" / "CANONICAL_CONTRACT_UNIVERSE.json")
        cls.revalidation = _load_object(root / "docs" / "evidence" / "CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json")
        cls.view, cls.certificate = build_view(
            manifest=cls.manifest,
            universe=cls.universe,
            revalidation=cls.revalidation,
            adoption=_adoption_payload(),
            raw_root=DEFAULT_PARENT_DATA_ROOT / "raw" / "historical",
            implementation_identity=_implementation_identity(),
            contract_universe_source_artifact_sha256=sha256((root / "docs" / "evidence" / "CANONICAL_CONTRACT_UNIVERSE.json").read_bytes()).hexdigest(),
        )

    def test_01_uniform_exclusion_has_exact_partition_count(self) -> None:
        self.assertEqual(EXPECTED_EXCLUDED_PARTITIONS, self.view.excluded_partition_count)

    def test_02_uniform_exclusion_has_exact_row_count(self) -> None:
        self.assertEqual(EXPECTED_EXCLUDED_ROWS, self.view.excluded_row_count)

    def test_03_remaining_eligible_count_is_exact(self) -> None:
        self.assertEqual(EXPECTED_ELIGIBLE_PARTITIONS, self.view.eligible_partition_count)

    def test_04_failures_are_a_strict_subset_of_uniform_exclusion(self) -> None:
        failed = {item["partition_identity"] for item in self.revalidation["failure_partitions"]}
        self.assertEqual(EXPECTED_FAILURES, len(failed))
        self.assertTrue(failed <= set(self.view.excluded_partition_identities))

    def test_05_clean_first_days_are_not_selected_from_failure_labels(self) -> None:
        failed = {item["partition_identity"] for item in self.revalidation["failure_partitions"]}
        self.assertEqual(EXPECTED_CLEAN_FIRST_DAYS, len(set(self.view.excluded_partition_identities) - failed))

    def test_06_mutating_failure_list_cannot_change_or_justify_exclusion(self) -> None:
        altered = dict(self.revalidation)
        altered["failure_partitions"] = altered["failure_partitions"][:-1]
        with self.assertRaisesRegex(ValueError, "first-day subset"):
            build_view(
                manifest=self.manifest, universe=self.universe, revalidation=altered,
                adoption=_adoption_payload(), raw_root=DEFAULT_PARENT_DATA_ROOT / "raw" / "historical",
                implementation_identity=_implementation_identity(),
                contract_universe_source_artifact_sha256=sha256((self.root / "docs" / "evidence" / "CANONICAL_CONTRACT_UNIVERSE.json").read_bytes()).hexdigest(),
            )

    def test_07_all_remaining_partitions_are_d01_certified(self) -> None:
        self.assertEqual(EXPECTED_ELIGIBLE_PARTITIONS, self.certificate["d01_pass_count"])

    def test_08_all_remaining_partitions_are_d02_certified(self) -> None:
        self.assertEqual(EXPECTED_ELIGIBLE_PARTITIONS, self.certificate["d02_pass_count"])

    def test_09_no_uncertified_partition_remains(self) -> None:
        self.assertEqual(0, self.certificate["uncertified_partition_count"])

    def test_10_view_identity_is_deterministic(self) -> None:
        self.assertEqual(self.view.identity(), self.view.identity())

    def test_11_view_identity_changes_with_parent(self) -> None:
        self.assertNotEqual(self.view.identity(), replace(self.view, parent_corpus_identity="another-parent").identity())

    def test_12_view_identity_changes_with_universe(self) -> None:
        self.assertNotEqual(self.view.identity(), replace(self.view, contract_universe_identity="another-universe").identity())

    def test_13_view_identity_changes_with_implementation(self) -> None:
        self.assertNotEqual(self.view.identity(), replace(self.view, implementation_identity="another-implementation").identity())

    def _small_gate(self) -> tuple[CandidateEligibilityGate, EligibilityPartition, EligibilityPartition]:
        excluded = EligibilityPartition("excluded", "SHFE.cu2501", date(2025, 1, 2))
        eligible = EligibilityPartition("eligible", "SHFE.cu2501", date(2025, 1, 3))
        view = QualifiedEligibilityView(
            parent_corpus_identity=PARENT_CORPUS_IDENTITY,
            parent_manifest_identity="manifest", contract_universe_identity="universe",
            contract_universe_source_artifact_sha256="universe-source", revalidation_evidence_identity="revalidation",
            authority_decision_evidence_identity="decision", implementation_identity="implementation",
            excluded_partitions=(excluded,), included_partition_root_identity=canonical_hash(["eligible"]),
            excluded_partition_count=1, eligible_partition_count=1, excluded_row_count=1,
        )
        return CandidateEligibilityGate(view, (excluded, eligible)), excluded, eligible

    def test_14_eligible_gate_returns_identity_bound_reference(self) -> None:
        gate, _, eligible = self._small_gate()
        reference = gate.require_eligible(concrete_contract=eligible.concrete_contract, trading_day=eligible.trading_day, partition_identity=eligible.partition_identity, parent_corpus_identity=PARENT_CORPUS_IDENTITY)
        self.assertEqual(gate.view.identity(), reference.qualified_eligibility_view_identity)

    def test_15_excluded_gate_fails_closed(self) -> None:
        gate, excluded, _ = self._small_gate()
        with self.assertRaisesRegex(CandidateEligibilityError, "CANDIDATE_PARTITION_NOT_ELIGIBLE_FIRST_TRADING_DAY"):
            gate.require_eligible(concrete_contract=excluded.concrete_contract, trading_day=excluded.trading_day, partition_identity=excluded.partition_identity, parent_corpus_identity=PARENT_CORPUS_IDENTITY)

    def test_16_unknown_partition_fails_closed(self) -> None:
        gate, _, eligible = self._small_gate()
        with self.assertRaisesRegex(CandidateEligibilityError, "CANDIDATE_PARTITION_UNKNOWN_IDENTITY"):
            gate.require_eligible(concrete_contract=eligible.concrete_contract, trading_day=eligible.trading_day, partition_identity="unknown", parent_corpus_identity=PARENT_CORPUS_IDENTITY)

    def test_17_identity_mismatch_fails_closed(self) -> None:
        gate, _, eligible = self._small_gate()
        with self.assertRaisesRegex(CandidateEligibilityError, "CANDIDATE_PARTITION_IDENTITY_MISMATCH"):
            gate.require_eligible(concrete_contract="SHFE.cu2502", trading_day=eligible.trading_day, partition_identity=eligible.partition_identity, parent_corpus_identity=PARENT_CORPUS_IDENTITY)

    def test_18_firewall_gateway_cannot_bypass_eligibility(self) -> None:
        gate, excluded, _ = self._small_gate()
        gateway = CandidateCanonicalInputGateway(ResearchFirewall(EvidenceLedger()), gate)
        with self.assertRaisesRegex(CandidateEligibilityError, "NOT_ELIGIBLE"):
            gateway.request_partition(concrete_contract=excluded.concrete_contract, trading_day=excluded.trading_day, partition_identity=excluded.partition_identity, parent_corpus_identity=PARENT_CORPUS_IDENTITY)

    def test_19_mapping_seam_is_fail_closed_and_has_no_fallback(self) -> None:
        gate, excluded, _ = self._small_gate()
        unresolved = ConcreteContractMappingResult(UNRESOLVED_FAIL_CLOSED, excluded.concrete_contract, excluded.trading_day)
        with self.assertRaisesRegex(CandidateEligibilityError, "MAPPING_AUTHORITY_UNRESOLVED"):
            gate.require_mapping_eligible(unresolved, partition_identity=excluded.partition_identity, parent_corpus_identity=PARENT_CORPUS_IDENTITY)
        resolved = ConcreteContractMappingResult("E07_SOURCE_GOVERNED_MAPPING_V1", excluded.concrete_contract, excluded.trading_day)
        with self.assertRaisesRegex(CandidateEligibilityError, "NOT_ELIGIBLE"):
            gate.require_mapping_eligible(resolved, partition_identity=excluded.partition_identity, parent_corpus_identity=PARENT_CORPUS_IDENTITY)

    def test_20_candidate_data_identity_stays_not_outcome_ready(self) -> None:
        identity = CandidateQualityDataIdentity(PARENT_CORPUS_IDENTITY, self.view.identity(), UNRESOLVED_FAIL_CLOSED, UNRESOLVED_FAIL_CLOSED, ("session-authority",))
        self.assertFalse(identity.ready_for_candidate_outcome)

    def test_21_dry_run_writes_no_candidate_eligibility_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            output = temporary_root / "output"
            command = [sys.executable, "-m", "tools.build_canonical_qualified_eligibility_view", "--dry-run", "--local-output", str(output), "--view-json", str(temporary_root / "view.json"), "--view-markdown", str(temporary_root / "view.md"), "--adoption-json", str(temporary_root / "adoption.json"), "--adoption-markdown", str(temporary_root / "adoption.md")]
            completed = subprocess.run(command, cwd=self.root, capture_output=True, text=True, check=True)
            self.assertIn('"dry_run": true', completed.stdout)
            self.assertFalse(output.exists())
            self.assertFalse((temporary_root / "view.json").exists())

    def test_22_no_outcome_or_raw_data_dependencies_are_imported(self) -> None:
        content = (self.root / "src" / "candidate_eligibility.py").read_text(encoding="utf-8").lower()
        imports = "\n".join(line for line in content.splitlines() if line.startswith("from ") or line.startswith("import "))
        self.assertNotIn("outcome", imports)
        self.assertNotIn("historical_acquisition", imports)


if __name__ == "__main__":
    unittest.main()
