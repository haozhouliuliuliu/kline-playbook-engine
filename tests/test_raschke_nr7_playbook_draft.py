"""Deterministic tests for the Raschke NR7 V0.1 Playbook Contract draft.

Covers the required fail-closed properties:

- all included source claims retain exact source/material IDs, anchors and
  status from the accepted SOURCE_ONLY evidence;
- UNKNOWN stays UNKNOWN (never rewritten EXPLICIT);
- unavailable NYSE TICK / breadth / leadership are recorded as
  NOT_OBSERVABLE_WITH_CURRENT_DATA and are never proxied;
- the 45-minute and 60-minute early-range variants are preserved explicitly and
  are not outcome-selected;
- no arbitrary PRIMARY is manufactured;
- no Holy Grail-specific stop semantics leak into the NR7 draft;
- unspecified offsets / order / fill / stop / exit values remain unresolved;
- readiness is fail-closed when required facts are missing;
- no ResearchFirewall candidate-outcome grant is requested;
- no strategy identity / outcome registration is produced from an unready draft;
- builder output is deterministic and matches the checked-in artifact.

Synthetic/deterministic fixtures only; no candidate outcome data is used.
"""

import inspect
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest import mock

from src.playbook_contract import (
    AmbiguityStatus,
    ClaimStatus,
    MachineOperationalization,
    MachineReadiness,
    ObservabilityStatus,
    TransferStatus,
    bridge_to_strategy_identity,
    validate_contract,
)
from src.strategy_evidence import LifecycleState
from tools import build_raschke_nr7_playbook_contract_draft as nr7_builder
from tools.build_raschke_nr7_playbook_contract_draft import (
    EARLY_RANGE_VARIANTS,
    FAMILY_ID,
    UNAVAILABLE_INPUTS,
    build_contract,
    build_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SESSION_EVIDENCE = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json"
)
OUTPUT_JSON = (
    REPO_ROOT
    / "docs"
    / "evidence"
    / "RASCHKE_NR7_PLAYBOOK_CONTRACT_DRAFT_V0_1.json"
)


def _session_evidence() -> dict:
    return json.loads(SESSION_EVIDENCE.read_text(encoding="utf-8"))


class Nr7SourceClaimsPreservationTests(unittest.TestCase):
    def test_all_source_claims_preserve_exact_ids_and_status(self):
        evidence = _session_evidence()
        contract = build_contract()

        self.assertEqual(evidence["recorded_claim_count"], len(contract.source_claims))
        by_id = {claim.claim_id: claim for claim in contract.source_claims}
        self.assertEqual(
            set(evidence["recorded_claim_ids"]),
            set(by_id.keys()),
        )
        for record in evidence["claims"]:
            claim = by_id[record["claim_id"]]
            self.assertEqual(record["material_id"], claim.source_id)
            self.assertEqual(record["source_anchor"], claim.source_anchor)
            self.assertEqual(record["claim_status"], claim.claim_status.value)
            self.assertEqual(record["lineage_id"], contract.research_lineage_id)

    def test_payload_claim_semantics_preserve_status_classification_and_observability(self):
        evidence = _session_evidence()
        payload = build_payload()
        semantics = {entry["claim_id"]: entry for entry in payload["claim_semantics"]}

        self.assertEqual(len(semantics), evidence["recorded_claim_count"])
        for record in evidence["claims"]:
            entry = semantics[record["claim_id"]]
            self.assertEqual(record["claim_status"], entry["claim_status"])
            self.assertEqual(record["semantic_field"], entry["semantic_field"])
            self.assertEqual(
                record["semantic_classification"], entry["semantic_classification"]
            )
            self.assertEqual(
                record["observability_compatibility"], entry["observability_compatibility"]
            )
            self.assertEqual(
                record["observability_missing_inputs"], entry["observability_missing_inputs"]
            )

    def test_unknown_remains_unknown(self):
        evidence = _session_evidence()
        payload = build_payload()
        source_by_id = {c["claim_id"]: c for c in payload["source_claims"]}
        semantics_by_id = {c["claim_id"]: c for c in payload["claim_semantics"]}

        expected_unknown = {
            record["claim_id"]
            for record in evidence["claims"]
            if record["claim_status"] == "UNKNOWN"
        }
        self.assertIn("C-RAS-NR7-SEM-008", expected_unknown)
        self.assertIn("C-RAS-NR7-SEM-012", expected_unknown)

        for claim_id in expected_unknown:
            self.assertEqual("UNKNOWN", source_by_id[claim_id]["claim_status"])
            self.assertEqual("UNKNOWN", semantics_by_id[claim_id]["claim_status"])

        # No source-UNKNOWN claim is silently upgraded anywhere in the payload.
        upgraded = {
            claim_id
            for claim_id in expected_unknown
            if source_by_id[claim_id]["claim_status"] != "UNKNOWN"
            or semantics_by_id[claim_id]["claim_status"] != "UNKNOWN"
        }
        self.assertEqual(set(), upgraded)


class Nr7ObservabilityTests(unittest.TestCase):
    def test_unavailable_tick_breadth_not_proxied(self):
        contract = build_contract()
        payload = build_payload()

        breadth_surfaces = [
            surface
            for surface in contract.observation_surfaces
            if surface.observability_status
            is ObservabilityStatus.NOT_OBSERVABLE_WITH_CURRENT_DATA
        ]
        self.assertTrue(breadth_surfaces)
        for surface in breadth_surfaces:
            self.assertFalse(surface.required)
            self.assertIn("NYSE_TICK", surface.missing_inputs)
            self.assertIn("ADVANCE_DECLINE_BREADTH", surface.missing_inputs)

        # No invented OHLCV/indicator proxy is recorded as the missing input.
        invented_proxies = {
            "ADX",
            "RSI",
            "MACD",
            "OPEN_INTEREST",
            "VOLUME_PROXY",
        }
        all_missing = {
            item for surface in contract.observation_surfaces for item in surface.missing_inputs
        }
        self.assertTrue(all_missing.isdisjoint(invented_proxies))
        self.assertEqual(UNAVAILABLE_INPUTS, contract.unavailable_inputs)
        payload_surfaces = {
            surface["surface_id"]: surface
            for surface in payload["observation_surfaces"]
        }
        self.assertEqual(
            ["ADVANCE_DECLINE_BREADTH", "NYSE_TICK", "TIKI"],
            payload_surfaces["BREADTH_TICK_HANDICAP"]["missing_inputs"],
        )

    def test_breadth_is_confirmation_handicap_not_required_entry_trigger(self):
        contract = build_contract()
        by_id = {surface.surface_id: surface for surface in contract.observation_surfaces}
        self.assertIn("BREADTH_TICK_HANDICAP", by_id)
        self.assertFalse(by_id["BREADTH_TICK_HANDICAP"].required)
        self.assertEqual(
            ObservabilityStatus.NOT_OBSERVABLE_WITH_CURRENT_DATA,
            by_id["BREADTH_TICK_HANDICAP"].observability_status,
        )


class Nr7EarlyRangeVariantTests(unittest.TestCase):
    def test_45min_and_60min_variants_preserved_explicitly(self):
        contract = build_contract()
        payload = build_payload()

        variant_branches = [
            branch
            for branch in contract.interpretations
            if branch.branch_id in (
                "SOURCE-PINNED-EARLY-RANGE-45MIN-VARIANT",
                "SOURCE-PINNED-EARLY-RANGE-60MIN-VARIANT",
            )
        ]
        self.assertEqual(2, len(variant_branches))
        self.assertEqual(
            {"EARLY_RANGE_VARIANT_45MIN", "EARLY_RANGE_VARIANT_60MIN"},
            {branch.interpretation_note for branch in variant_branches},
        )
        for branch in variant_branches:
            self.assertEqual(("C-RAS-NR7-SEM-004",), branch.source_claim_ids)
            self.assertEqual(TransferStatus.EXPLICIT, branch.transfer_status)
        self.assertEqual(list(EARLY_RANGE_VARIANTS), payload["early_range_variants"])

    def test_45min_60min_variants_not_outcome_selected(self):
        contract = build_contract()
        payload = build_payload()

        # Neither variant branch is PRIMARY, and the unresolved branch exists.
        self.assertFalse(
            any(
                branch.primary_selected
                for branch in contract.interpretations
                if branch.branch_id
                in ("SOURCE-PINNED-EARLY-RANGE-45MIN-VARIANT", "SOURCE-PINNED-EARLY-RANGE-60MIN-VARIANT")
            )
        )
        unresolved = [
            branch
            for branch in contract.interpretations
            if branch.branch_id == "UNRESOLVED-EARLY-RANGE-PRIMARY"
        ]
        self.assertEqual(1, len(unresolved))
        self.assertEqual(TransferStatus.UNKNOWN, unresolved[0].transfer_status)
        self.assertFalse(unresolved[0].primary_selected)
        self.assertEqual("NONE_SOURCE_JUSTIFIED", payload["early_range_primary_status"])
        self.assertEqual("NO", payload["final_decision"]["PRIMARY_FREEZE_READY"])


class Nr7PrimaryTests(unittest.TestCase):
    def test_no_arbitrary_primary_manufactured(self):
        contract = build_contract()
        self.assertFalse(any(branch.primary_selected for branch in contract.interpretations))
        result = validate_contract(contract)
        self.assertIn("CLAIM_PRIMARY_MISSING", result.blockers)

    def test_source_evidence_does_not_justify_any_primary(self):
        # The accepted SOURCE_ONLY session records no source-justified PRIMARY.
        evidence = _session_evidence()
        self.assertEqual("NO", evidence["final_decision"]["PLAYBOOK_SEMANTICALLY_DRAFTABLE"])
        for record in evidence["claims"]:
            self.assertEqual(
                "PRIMARY_NOT_YET_JUSTIFIED", record["primary_branch_status"]
            )


class Nr7HolyGrailIsolationTests(unittest.TestCase):
    def test_no_holy_grail_stop_semantics_leak(self):
        contract = build_contract()
        all_basis = " ".join(branch.source_basis for branch in contract.interpretations).lower()
        holy_grail_markers = (
            "swing low",
            "swing-low",
            "trailing stop",
            "14-period adx",
            "20-period ema",
            "newly formed swing",
        )
        for marker in holy_grail_markers:
            self.assertNotIn(marker, all_basis)

        # The NR7 risk-loop claims must stay unresolved (UNKNOWN), not EXPLICIT.
        for claim_id in ("C-RAS-NR7-SEM-011", "C-RAS-NR7-SEM-012"):
            referencing = [
                branch
                for branch in contract.interpretations
                if claim_id in branch.source_claim_ids
            ]
            self.assertTrue(referencing)
            for branch in referencing:
                self.assertEqual(TransferStatus.UNKNOWN, branch.transfer_status)

    def test_builder_does_not_import_holy_grail_tooling(self):
        source = inspect.getsource(nr7_builder)
        self.assertNotIn("build_raschke_holy_grail_playbook_contract_draft", source)
        self.assertNotIn("RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT", source)
        self.assertNotIn("C-RAS-HG-SEM", source)
        self.assertEqual("L-RAS-NR7", nr7_builder.RESEARCH_LINEAGE_ID)
        self.assertEqual("RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT", FAMILY_ID)


class Nr7UnresolvedMechanicsTests(unittest.TestCase):
    def test_unspecified_offsets_order_fill_stop_exit_remain_unresolved(self):
        contract = build_contract()
        unresolved_branches = {
            branch.branch_id: branch
            for branch in contract.interpretations
            if branch.branch_id.startswith("UNRESOLVED-")
        }
        expected_unresolved = {
            "UNRESOLVED-ENTRY-OFFSET-TICK",
            "UNRESOLVED-OPPOSITE-ORDER-CANCELLATION",
            "UNRESOLVED-SAME-BAR-TRIGGER-HANDLING",
            "UNRESOLVED-POST-ENTRY-INVALIDATION",
            "UNRESOLVED-INITIAL-STOP",
            "UNRESOLVED-EXIT-TARGET-CONVENTION",
            "UNRESOLVED-END-OF-SESSION-RULE",
        }
        for branch_id in expected_unresolved:
            self.assertIn(branch_id, unresolved_branches)
            self.assertEqual(
                TransferStatus.UNKNOWN, unresolved_branches[branch_id].transfer_status
            )

    def test_order_mechanics_surface_is_partially_observable(self):
        contract = build_contract()
        by_id = {surface.surface_id: surface for surface in contract.observation_surfaces}
        surface = by_id["BRACKET_ENTRY_ORDER_SEMANTICS"]
        self.assertTrue(surface.required)
        self.assertEqual(ObservabilityStatus.PARTIALLY_OBSERVABLE, surface.observability_status)
        for missing in (
            "entry_offset_or_tick_convention",
            "oco_cancellation_semantics",
            "order_subtype",
            "same_bar_trigger_ordering",
        ):
            self.assertIn(missing, surface.missing_inputs)


class Nr7FailClosedReadinessTests(unittest.TestCase):
    def test_draft_readiness_is_fail_closed(self):
        contract = build_contract()
        result = validate_contract(contract)
        self.assertEqual(MachineReadiness.NOT_MACHINE_READY, result.readiness)
        self.assertIsNone(contract.machine)
        for blocker in (
            "UNRESOLVED_CRITICAL_AMBIGUITY",
            "REQUIRED_INPUT_NOT_FULLY_OBSERVABLE",
            "CLAIM_PRIMARY_MISSING",
            "MACHINE_OPERATIONALIZATION_MISSING",
            "MULTIPLE_TIMEFRAMES_UNRESOLVED",
        ):
            self.assertIn(blocker, result.blockers)

    def test_adding_machine_labels_cannot_bypass_unresolved_semantic_gates(self):
        contract = build_contract()
        attempted_bypass = replace(
            contract,
            ambiguity_status=AmbiguityStatus.RESOLVED,
            machine=MachineOperationalization(
                operationalization_reference="TEST_ONLY_ATTEMPTED_BYPASS",
                code_hash="test-only-code",
                environment_hash="test-only-environment",
                required_feature_versions=(),
                parameter_identities=(),
            ),
        )
        result = validate_contract(attempted_bypass)
        self.assertEqual(MachineReadiness.NOT_MACHINE_READY, result.readiness)
        self.assertIn("CLAIM_PRIMARY_MISSING", result.blockers)
        self.assertIn("REQUIRED_INPUT_NOT_FULLY_OBSERVABLE", result.blockers)
        self.assertIn("MULTIPLE_TIMEFRAMES_UNRESOLVED", result.blockers)

    def test_no_strategy_identity_or_outcome_registration_from_unready_draft(self):
        contract = build_contract()
        with self.assertRaises(ValueError):
            bridge_to_strategy_identity(
                contract,
                parameters=(),
                code_hash="test-only-code",
                environment_hash="test-only-environment",
                required_feature_versions=(),
                data_exposure_history_reference="test-only-exposure",
                lifecycle_state=LifecycleState.DRAFT,
            )


class Nr7FirewallIsolationTests(unittest.TestCase):
    def test_no_research_firewall_candidate_outcome_grant_requested(self):
        source = inspect.getsource(nr7_builder)
        # The builder never imports the firewall, never instantiates it, and
        # never calls any outcome-registration method.
        self.assertNotIn("from src.research_firewall", source)
        self.assertNotIn("import research_firewall", source)
        self.assertNotIn("ResearchFirewall(", source)
        self.assertNotIn("register_outcome_test", source)
        payload = build_payload()
        self.assertEqual("NO", payload["final_decision"]["OUTCOME_TEST_REGISTERED"])
        self.assertEqual("NO", payload["final_decision"]["CANDIDATE_OUTCOME_DATA_USED"])

    def test_builder_only_reads_source_only_evidence(self):
        # The builder's only evidence input is the accepted SOURCE_ONLY session.
        self.assertEqual(
            "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json",
            nr7_builder.SESSION_EVIDENCE.name,
        )


class Nr7DeterministicOutputTests(unittest.TestCase):
    def test_checked_in_v0_1_artifact_is_deterministic(self):
        checked_in = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        payload = build_payload()
        self.assertEqual(payload, checked_in)
        self.assertEqual("NO", payload["final_decision"]["MACHINE_READY"])
        self.assertEqual("NO", payload["final_decision"]["PRIMARY_FREEZE_READY"])
        self.assertEqual("NO", payload["final_decision"]["STRATEGY_IDENTITY_CREATED"])
        self.assertEqual("NO", payload["final_decision"]["OUTCOME_TEST_REGISTERED"])
        self.assertEqual("NO", payload["final_decision"]["CANDIDATE_OUTCOME_DATA_USED"])
        self.assertEqual(23, payload["source_evidence_recorded_claim_count"])
        self.assertEqual("NOT_MACHINE_READY", payload["machine_readiness"])

    def test_builder_fails_closed_on_invalid_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad_evidence.json"
            bad.write_text("{not valid json", encoding="utf-8")
            with mock.patch.object(nr7_builder, "SESSION_EVIDENCE", bad):
                with self.assertRaises(ValueError):
                    nr7_builder._load_session_evidence()
        # Missing/incomplete session identity also fails closed.
        with tempfile.TemporaryDirectory() as tmp:
            empty = Path(tmp) / "empty_evidence.json"
            empty.write_text(
                json.dumps(
                    {
                        "claims": [
                            {
                                "claim_id": "C-RAS-NR7-SEM-001",
                                "claim_status": "EXPLICIT",
                                "material_id": "SR-V0-M03",
                                "source_anchor": "SR-V0-M03:sec",
                            }
                        ],
                        "recorded_claim_count": 1,
                        "session": {},
                    }
                ),
                encoding="utf-8",
            )
            with mock.patch.object(nr7_builder, "SESSION_EVIDENCE", empty):
                with self.assertRaises(ValueError):
                    nr7_builder.build_contract()


if __name__ == "__main__":
    unittest.main()
