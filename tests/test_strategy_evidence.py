import unittest
from dataclasses import FrozenInstanceError

from src.strategy_evidence import (
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
        self.ledger.append(record)
        with self.assertRaises(FrozenInstanceError):
            record.outcome = "CHANGED"
        with self.assertRaises(ValueError):
            self.ledger.append(record)
        self.assertEqual(self.ledger.records, (record,))


if __name__ == "__main__":
    unittest.main()
