import inspect
import unittest
from dataclasses import FrozenInstanceError

from src.strategy_evidence import (
    ArtifactBinding,
    DatasetClass,
    EvidenceLedger,
    EvidenceRecord,
    ExperimentIdentity,
    FinalUnseenFirewall,
    LifecycleState,
    StrategyCatalog,
    StrategyIdentity,
    TypedParameter,
)


def strategy(*, family_id="neutral-family", version="1.0", value=3, parent_identity_id=None):
    return StrategyIdentity(
        research_lineage_id="research-lineage-fixture",
        family_id=family_id,
        strategy_version=version,
        source="deterministic-fixture",
        applicable_instruments=("TEST",),
        timeframe="5m",
        parameters=(TypedParameter("window", "int", value),),
        code_hash="code-fixture-v1",
        environment_hash="environment-fixture-v1",
        required_feature_versions=("context-fixture-v1",),
        lifecycle_state=LifecycleState.DRAFT,
        data_exposure_history_reference="exposure-fixture-v1",
        parent_identity_id=parent_identity_id,
    )


class StrategyIdentityTests(unittest.TestCase):
    def test_identical_inputs_have_stable_identity_and_parameter_hash(self):
        self.assertEqual(strategy().identity_id, strategy().identity_id)
        self.assertEqual(strategy().parameter_hash, strategy().parameter_hash)

    def test_meaningful_parameter_change_requires_distinct_version_identity(self):
        first = strategy()
        changed = strategy(version="1.1", value=4)
        self.assertNotEqual(first.parameter_hash, changed.parameter_hash)
        self.assertNotEqual(first.identity_id, changed.identity_id)

    def test_historical_catalog_record_cannot_be_silently_mutated(self):
        catalog = StrategyCatalog()
        registered = catalog.register(strategy())
        with self.assertRaises(FrozenInstanceError):
            registered.family_id = "changed"
        self.assertEqual(catalog.records, (strategy(),))

    def test_catalog_rejects_reusing_a_version_for_changed_parameters(self):
        catalog = StrategyCatalog()
        catalog.register(strategy())
        with self.assertRaisesRegex(ValueError, "cannot be reused"):
            catalog.register(strategy(value=4))


class EvidenceAndFirewallTests(unittest.TestCase):
    def setUp(self):
        self.catalog = StrategyCatalog()
        self.parent = self.catalog.register(strategy())
        self.experiment = ExperimentIdentity.from_strategy(self.parent, "data-fixture-v1", "exposure-fixture-v1")
        self.ledger = EvidenceLedger()
        self.firewall = FinalUnseenFirewall(self.ledger)

    def test_experiment_binds_all_required_versions_deterministically(self):
        again = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        self.assertEqual(self.experiment.experiment_id, again.experiment_id)
        self.assertEqual(self.experiment.code_hash, "code-fixture-v1")
        self.assertEqual(self.experiment.parameter_hash, self.parent.parameter_hash)
        self.assertEqual(self.experiment.environment_hash, "environment-fixture-v1")
        self.assertEqual(self.experiment.feature_versions, ("context-fixture-v1",))

    def test_development_and_validation_accesses_are_granted_and_deterministic(self):
        development = self.firewall.request_access(self.experiment, DatasetClass.DEVELOPMENT)
        validation = self.firewall.request_access(self.experiment, DatasetClass.VALIDATION)
        repeated = FinalUnseenFirewall(EvidenceLedger()).request_access(self.experiment, DatasetClass.VALIDATION)
        self.assertTrue(development.allowed and validation.allowed)
        self.assertEqual(development.record.event_type, "DATASET_ACCESS_GRANTED")
        self.assertEqual(validation.record.record_id, repeated.record.record_id)
        self.assertEqual(len(self.ledger.records), 2)

    def test_final_unseen_is_denied_and_only_denial_fact_is_recorded(self):
        result = self.firewall.request_access(self.experiment, DatasetClass.FINAL_UNSEEN)
        self.assertFalse(result.allowed)
        self.assertEqual(result.record.event_type, "DATASET_ACCESS_DENIED")
        self.assertEqual(result.record.outcome, "DENIED")
        self.assertFalse(hasattr(result, "data"))
        self.assertNotIn(DatasetClass.FINAL_UNSEEN, self.ledger.exposures_for(self.parent.research_lineage_id))

    def test_descendant_and_renamed_family_retain_lineage_exposure(self):
        self.firewall.request_access(self.experiment, DatasetClass.VALIDATION)
        child = self.catalog.register(strategy(family_id="renamed-family", version="2.0", parent_identity_id=self.parent.identity_id))
        self.assertTrue(self.firewall.has_exposure(child, DatasetClass.VALIDATION))

    def test_ledger_is_append_only_factual_history_not_live_state(self):
        record = EvidenceRecord("LIFECYCLE_TRANSITION", self.experiment, DatasetClass.DEVELOPMENT, "RECORDED", LifecycleState.CANDIDATE)
        returned = self.ledger.append(record)
        with self.assertRaises(FrozenInstanceError):
            record.outcome = "CHANGED"
        # F-13: an exact duplicate append is idempotent - returns the already
        # stored canonical record and never inflates the factual history.
        again = self.ledger.append(record)
        self.assertIs(returned, again)
        self.assertEqual(self.ledger.records, (record,))

    # B28 (F-13): repeated identical evidence append is idempotent and never
    # inflates the canonical evidence ledger.
    def test_b28_repeated_identical_append_is_idempotent(self):
        record = EvidenceRecord("DATASET_ACCESS_GRANTED", self.experiment, DatasetClass.DEVELOPMENT, "GRANTED", LifecycleState.CANDIDATE, "synthetic-ok")
        first = self.ledger.append(record)
        for _ in range(5):
            returned = self.ledger.append(record)
            self.assertIs(returned, first)
        self.assertEqual(self.ledger.records, (record,))
        self.assertEqual(len(self.ledger.records), 1)


class ArtifactBindingHashTests(unittest.TestCase):
    """P-06: ArtifactBinding hashes are computed from the actual bytes."""

    # B08: identical bytes -> identical digest + identity.
    def test_b08_same_bytes_produce_same_identity(self):
        first = ArtifactBinding.from_bytes(
            artifact_kind="code", artifact_reference="ref-v1", content=b"same bytes", declared_version="v1"
        )
        second = ArtifactBinding.from_bytes(
            artifact_kind="code", artifact_reference="ref-v1", content=b"same bytes", declared_version="v1"
        )
        self.assertEqual(first.sha256, second.sha256)
        self.assertEqual(first.identity_id, second.identity_id)
        self.assertEqual(first.byte_size, len(b"same bytes"))

    # B09: a one-byte change changes the digest and the identity.
    def test_b09_one_byte_change_changes_digest(self):
        original = ArtifactBinding.from_bytes(
            artifact_kind="code", artifact_reference="ref-v1", content=b"synthetic code bytes", declared_version="v1"
        )
        tampered = ArtifactBinding.from_bytes(
            artifact_kind="code", artifact_reference="ref-v1", content=b"synthetic code byte!", declared_version="v1"
        )
        self.assertNotEqual(original.sha256, tampered.sha256)
        self.assertNotEqual(original.identity_id, tampered.identity_id)

    def test_constructor_never_accepts_caller_supplied_digest(self):
        # The public construction path is from_bytes/from_file only; a digest is
        # always recomputed from content and cannot be supplied directly.
        binding = ArtifactBinding.from_bytes(
            artifact_kind="environment", artifact_reference="env-v1", content=b"env", declared_version="v1"
        )
        self.assertEqual(len(binding.sha256), 64)
        self.assertEqual(binding.sha256, ArtifactBinding.from_bytes(
            artifact_kind="environment", artifact_reference="env-v1", content=b"env", declared_version="v1"
        ).sha256)


class PreIntegrationCorrectionArtifactBindingTests(unittest.TestCase):
    """B-C01: no callable ArtifactBinding path accepts a caller digest."""

    # BC01-A: the old private builder (and any renamed variant) must not exist,
    # and no constructor may accept digest/sha256 as caller input.
    def test_bc01_a_no_caller_digest_construction_path(self):
        for name in ("_build", "_from_digest", "from_digest"):
            self.assertFalse(hasattr(ArtifactBinding, name), f"caller-digest path {name!r} must not exist")
        for name in ("from_bytes", "from_file"):
            params = set(inspect.signature(getattr(ArtifactBinding, name)).parameters)
            self.assertNotIn("digest", params)
            self.assertNotIn("sha256", params)

    # BC01-B: from_bytes computes the digest from the actual bytes; same bytes
    # -> same digest, changed bytes -> changed digest (B08/B09 remain green).
    def test_bc01_b_from_bytes_digest_deterministic(self):
        same_a = ArtifactBinding.from_bytes(
            artifact_kind="code", artifact_reference="r", content=b"same bytes", declared_version="v1"
        )
        same_b = ArtifactBinding.from_bytes(
            artifact_kind="code", artifact_reference="r", content=b"same bytes", declared_version="v1"
        )
        changed = ArtifactBinding.from_bytes(
            artifact_kind="code", artifact_reference="r", content=b"changed bytes", declared_version="v1"
        )
        self.assertEqual(same_a.sha256, same_b.sha256)
        self.assertEqual(same_a.byte_size, len(b"same bytes"))
        self.assertNotEqual(same_a.sha256, changed.sha256)


if __name__ == "__main__":
    unittest.main()
