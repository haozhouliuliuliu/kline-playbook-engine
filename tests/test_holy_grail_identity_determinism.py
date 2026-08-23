"""Anti-regression tests for Holy Grail V0.4 identity determinism and the
Primary Freeze -> contract -> machine -> feature identity chain.

Regression context (repair/holy-grail-identity-determinism-v01):

- Commit ``35295bd`` hand-edited the identity fields inside
  ``HOLY_GRAIL_PRIMARY_FREEZE_V0_1.json`` and
  ``RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_4.json`` to values that the
  deterministic builders do NOT produce, and also let
  ``PRE_SHADOW_GATE_V0_2.json`` carry a stale ``gate_module_sha256``.  There was
  no Holy Grail semantic change (builders, source claims, machine code and all
  inputs stayed byte-identical).  The artifacts were re-generated from their
  authoritative builders; this file locks that determinism and the identity
  chain so the drift class cannot silently return.

These tests are intentionally redundant with the generic
``test_playbook_contract`` determinism tests: they pin the actual Holy Grail
V0.4 chain (freeze / contract / machine / feature / PreShadow gate) against
builder output, cwd independence, temp/worktree-path independence, ordering
independence, byte-identical rerun, and cross-artifact consistency.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.playbook_contract import (
    MachineOperationalization,
    PlaybookContract,
    bridge_to_strategy_identity,
)
from src.pre_shadow_gate import PreShadowGateV02Inputs, PreShadowTechnicalGateV02
from tools.build_holy_grail_primary_freeze_v0_1 import build_payload as freeze_payload
from tools.build_pre_shadow_gate_v0_1 import build_payload as gate_v01_payload
from tools.build_pre_shadow_gate_v0_2 import build_payload as gate_v02_payload
from tools.build_raschke_holy_grail_playbook_contract_draft_v0_4 import (
    build_contract,
    build_payload as contract_payload,
    strategy_parameters,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "docs" / "evidence"

V0_4_JSON = EVIDENCE_DIR / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_4.json"
FREEZE_JSON = EVIDENCE_DIR / "HOLY_GRAIL_PRIMARY_FREEZE_V0_1.json"
GATE_V01_JSON = EVIDENCE_DIR / "PRE_SHADOW_GATE_V0_1.json"
GATE_V02_JSON = EVIDENCE_DIR / "PRE_SHADOW_GATE_V0_2.json"
PRE_SHADOW_GATE_MODULE = REPO_ROOT / "src" / "pre_shadow_gate.py"
SESSION_EVIDENCE = (
    EVIDENCE_DIR / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json"
)

# Authoritative identity set computed by the current builders (2026-08-21).
# These values are the source of truth until a genuine, reviewed semantic change
# deliberately re-generates every derived artifact from the builders.
AUTHORITATIVE = {
    "contract_identity": "549e730b4c3b78b7367b253fc665f651d7486f053fab6dde101ca9d73a4b2a61",
    "machine_identity": "22886cfa770ba7dd1f266133f950e99ec6770ca0332eca40657d57943155b6c9",
    "feature_identity": "3c3dfff55831482b6ee44e746d9976b8b5a3a7a7b986c21b9f799868761b0309",
    "strategy_identity": "64ff2a4fd4df6a89047fe2042a1120f67037f5179b908b29922996908daa3040",
    "strategy_version": "pc-0.4.0-549e730b4c3b78b7367b253fc665f651d7486f053fab6dde101ca9d73a4b2a61",
    "parameter_hash": "aa41f53232f44255e9a012b93e1890d889bf4a0a986dc5e4f754dbb1c46d1659",
}

PRE_SHADOW_GATE_SHA256 = hashlib.sha256(PRE_SHADOW_GATE_MODULE.read_bytes()).hexdigest()


def _cwd_independent_key() -> tuple:
    c = contract_payload()
    f = freeze_payload()
    return (
        c["contract_identity"],
        c["machine_operationalization"]["machine_identity"],
        tuple(c["machine_operationalization"]["required_feature_versions"]),
        f["strategy_identity"],
        f["primary_contract_identity"],
        tuple(f["feature_versions"]),
        f["strategy_version"],
    )


class HolyGrailIdentityDeterminismTests(unittest.TestCase):
    """Task 4: same semantic inputs -> same identity; rerun -> byte-identical."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.contract_payload = contract_payload()
        cls.contract = build_contract()
        cls.freeze = freeze_payload()
        cls.v0_4_checked_in = json.loads(V0_4_JSON.read_text(encoding="utf-8"))
        cls.freeze_checked_in = json.loads(FREEZE_JSON.read_text(encoding="utf-8"))

    def test_same_semantic_inputs_yield_identical_identity(self):
        first = contract_payload()
        second = contract_payload()
        self.assertEqual(first["contract_identity"], second["contract_identity"])
        self.assertEqual(
            first["machine_operationalization"]["machine_identity"],
            second["machine_operationalization"]["machine_identity"],
        )
        self.assertEqual(freeze_payload()["strategy_identity"], self.freeze["strategy_identity"])

    def test_rerun_builder_is_byte_identical_to_checked_in_artifacts(self):
        # Deterministic builders must reproduce the checked-in JSON byte-for-byte.
        self.assertEqual(
            self.contract_payload,
            self.v0_4_checked_in,
        )
        self.assertEqual(self.freeze, self.freeze_checked_in)
        self.assertEqual(
            gate_v01_payload(),
            json.loads(GATE_V01_JSON.read_text(encoding="utf-8")),
        )
        self.assertEqual(
            gate_v02_payload(),
            json.loads(GATE_V02_JSON.read_text(encoding="utf-8")),
        )

    def test_authoritative_identity_set_is_pinned(self):
        # Lock the current authoritative set; ANY drift (like the 35295bd
        # hand-edit) fails here even if two artifacts were edited consistently.
        self.assertEqual(
            AUTHORITATIVE["contract_identity"], self.contract_payload["contract_identity"]
        )
        self.assertEqual(
            AUTHORITATIVE["machine_identity"],
            self.contract_payload["machine_operationalization"]["machine_identity"],
        )
        self.assertEqual(
            AUTHORITATIVE["feature_identity"],
            self.contract_payload["machine_operationalization"]["required_feature_versions"][0],
        )
        self.assertEqual(AUTHORITATIVE["strategy_identity"], self.freeze["strategy_identity"])
        self.assertEqual(AUTHORITATIVE["strategy_version"], self.freeze["strategy_version"])
        self.assertEqual(AUTHORITATIVE["parameter_hash"], self.freeze["parameter_hash"])
        self.assertEqual(self.freeze["primary_contract_identity"], self.freeze_checked_in["primary_contract_identity"])

    def test_semantic_input_change_changes_identity(self):
        # Changing machine code bytes (a semantic input) must change the chain.
        contract = self.contract
        altered_machine = MachineOperationalization(
            operationalization_reference=contract.machine.operationalization_reference,
            code_hash="0" * 64,
            environment_hash=contract.machine.environment_hash,
            required_feature_versions=contract.machine.required_feature_versions,
            parameter_identities=contract.machine.parameter_identities,
        )
        altered = PlaybookContract(
            schema_version=contract.schema_version,
            contract_version=contract.contract_version,
            contract_id=contract.contract_id,
            research_lineage_id=contract.research_lineage_id,
            family_id=contract.family_id,
            source_claims=contract.source_claims,
            source_bundle_identity=contract.source_bundle_identity,
            source_bundle_hash=contract.source_bundle_hash,
            source_only_session_identity=contract.source_only_session_identity,
            source_scope=contract.source_scope,
            interpretations=contract.interpretations,
            ambiguity_status=contract.ambiguity_status,
            ambiguity_notes=contract.ambiguity_notes,
            primary_required=contract.primary_required,
            source_variant_count=contract.source_variant_count,
            observation_surfaces=contract.observation_surfaces,
            unavailable_inputs=contract.unavailable_inputs,
            instrument_scope=contract.instrument_scope,
            timeframe_scope=contract.timeframe_scope,
            project_transfer_status=contract.project_transfer_status,
            machine=altered_machine,
            data_exposure_history_reference=contract.data_exposure_history_reference,
            parent_contract_id=contract.parent_contract_id,
            created_at=contract.created_at,
        )
        self.assertNotEqual(contract.contract_identity, altered.contract_identity)
        self.assertNotEqual(contract.machine.machine_identity, altered.machine.machine_identity)

    def test_semantic_parameter_change_changes_strategy_identity(self):
        # A genuinely different approved parameter must change the parameter
        # identity that feeds the StrategyIdentity chain.
        from src.playbook_contract import canonical_hash
        from src.strategy_evidence import TypedParameter

        base_params = strategy_parameters()
        changed = tuple(
            TypedParameter(
                parameter.name,
                parameter.type_name,
                999 if parameter.name == "ema_period" and parameter.type_name == "int" else parameter.value,
            )
            for parameter in base_params
        )
        base_hash = canonical_hash([p.as_dict() for p in base_params])
        changed_hash = canonical_hash([p.as_dict() for p in changed])
        self.assertNotEqual(base_hash, changed_hash)
        self.assertEqual(
            self.freeze["parameter_hash"],
            base_hash,
        )

    def test_collection_ordering_does_not_change_identity(self):
        # Reversing claim/branch/surface enumeration order must not change the
        # Holy Grail contract identity (identity sorts every collection).
        contract = self.contract
        reordered = PlaybookContract(
            schema_version=contract.schema_version,
            contract_version=contract.contract_version,
            contract_id=contract.contract_id,
            research_lineage_id=contract.research_lineage_id,
            family_id=contract.family_id,
            source_claims=tuple(reversed(contract.source_claims)),
            source_bundle_identity=contract.source_bundle_identity,
            source_bundle_hash=contract.source_bundle_hash,
            source_only_session_identity=contract.source_only_session_identity,
            source_scope=contract.source_scope,
            interpretations=tuple(reversed(contract.interpretations)),
            ambiguity_status=contract.ambiguity_status,
            ambiguity_notes=contract.ambiguity_notes,
            primary_required=contract.primary_required,
            source_variant_count=contract.source_variant_count,
            observation_surfaces=tuple(reversed(contract.observation_surfaces)),
            unavailable_inputs=contract.unavailable_inputs,
            instrument_scope=contract.instrument_scope,
            timeframe_scope=contract.timeframe_scope,
            project_transfer_status=contract.project_transfer_status,
            machine=contract.machine,
            data_exposure_history_reference=contract.data_exposure_history_reference,
            parent_contract_id=contract.parent_contract_id,
            created_at=contract.created_at,
        )
        self.assertEqual(contract.contract_identity, reordered.contract_identity)

    def test_irrelevant_cwd_change_is_unchanged(self):
        saved = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            try:
                moved = _cwd_independent_key()
            finally:
                os.chdir(saved)
        self.assertEqual(_cwd_independent_key(), moved)

    def test_temp_worktree_path_change_is_unchanged(self):
        # Copy a minimal tree (src + tools + the single builder input) to a
        # different absolute temp path and confirm the identity chain is
        # identical: identities must not bind to the worktree path.
        with tempfile.TemporaryDirectory() as tmp:
            copy_root = Path(tmp) / "kline-identity-copy"
            (copy_root / "src").mkdir(parents=True)
            (copy_root / "tools").mkdir()
            (copy_root / "docs" / "evidence").mkdir(parents=True)
            shutil.copytree(REPO_ROOT / "src", copy_root / "src", dirs_exist_ok=True)
            shutil.copytree(REPO_ROOT / "tools", copy_root / "tools", dirs_exist_ok=True)
            shutil.copy2(SESSION_EVIDENCE, copy_root / "docs" / "evidence" / SESSION_EVIDENCE.name)
            code = (
                "import sys; sys.path.insert(0, %r); "
                "from tools.build_raschke_holy_grail_playbook_contract_draft_v0_4 import build_payload as c; "
                "from tools.build_holy_grail_primary_freeze_v0_1 import build_payload as f; "
                "print('K=' + c()['contract_identity'] + '|' + f()['strategy_identity'])"
            ) % str(copy_root)
            result = subprocess.run(
                [sys.executable, "-c", code],
                cwd=str(copy_root),
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            moved_key = result.stdout.strip().split("=", 1)[1]
            expected = (
                f"{AUTHORITATIVE['contract_identity']}|{AUTHORITATIVE['strategy_identity']}"
            )
            self.assertEqual(expected, moved_key)


class HolyGrailIdentityChainConsistencyTests(unittest.TestCase):
    """Task 4: Primary Freeze <-> contract <-> machine/feature chain + PreShadow."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.contract_payload = contract_payload()
        cls.contract = build_contract()
        cls.freeze = freeze_payload()

    def test_primary_freeze_references_current_contract_identity(self):
        self.assertEqual(
            self.freeze["primary_contract_identity"],
            self.contract_payload["contract_identity"],
        )
        self.assertEqual(
            self.freeze["strategy_version"],
            f"pc-{self.contract.contract_version}-{self.contract.contract_identity}",
        )
        self.assertEqual(
            self.freeze["feature_versions"],
            self.contract_payload["machine_operationalization"]["required_feature_versions"],
        )
        # The freeze's parameter_hash must equal the bridge StrategyIdentity hash.
        machine = self.contract.machine
        strategy = bridge_to_strategy_identity(
            self.contract,
            parameters=strategy_parameters(),
            code_hash=machine.code_hash,
            environment_hash=machine.environment_hash,
            required_feature_versions=machine.required_feature_versions,
            data_exposure_history_reference=self.contract.data_exposure_history_reference,
        )
        self.assertEqual(self.freeze["parameter_hash"], strategy.parameter_hash)

    def test_strategy_identity_references_current_machine_and_contract_identity(self):
        machine = self.contract.machine
        strategy = bridge_to_strategy_identity(
            self.contract,
            parameters=strategy_parameters(),
            code_hash=machine.code_hash,
            environment_hash=machine.environment_hash,
            required_feature_versions=machine.required_feature_versions,
            data_exposure_history_reference=self.contract.data_exposure_history_reference,
        )
        self.assertEqual(self.freeze["strategy_identity"], strategy.identity_id)
        self.assertEqual(strategy.playbook_contract_identity, self.contract.contract_identity)
        self.assertEqual(strategy.code_hash, machine.code_hash)
        self.assertEqual(strategy.environment_hash, machine.environment_hash)
        self.assertEqual(
            tuple(sorted(strategy.required_feature_versions)),
            tuple(sorted(machine.required_feature_versions)),
        )
        self.assertEqual(strategy.strategy_version, self.freeze["strategy_version"])

    def test_current_state_declared_identity_matches_formal_freeze(self):
        # CURRENT_STATE is not a required mirror of the historical Holy Grail
        # formal-freeze identity (active-context consolidation keeps it current-
        # truth only; the formal freeze remains in evidence/reviews/Git history).
        # If CURRENT_STATE ever declares the field, the declared value must match
        # the formal freeze and the authoritative set; absence is legal.
        state_text = (REPO_ROOT / "CURRENT_STATE.md").read_text(encoding="utf-8")
        declared = None
        for line in state_text.splitlines():
            if line.startswith("HOLY_GRAIL_PRIMARY_STRATEGY_IDENTITY="):
                declared = line.split("=", 1)[1].strip()
                break
        if declared is not None:
            self.assertEqual(self.freeze["strategy_identity"], declared)
            self.assertEqual(AUTHORITATIVE["strategy_identity"], declared)

    def test_pre_shadow_gate_references_consistent_identity(self):
        # Gate V0_2 module hash must match the actual pre_shadow_gate.py bytes.
        gate_v02 = gate_v02_payload()
        self.assertEqual(PRE_SHADOW_GATE_SHA256, gate_v02["gate_module_sha256"])
        # The checked-in gate must be exactly what the builder produces.
        self.assertEqual(
            gate_v02,
            json.loads(GATE_V02_JSON.read_text(encoding="utf-8")),
        )
        # Gate V0_1 must reference the same module bytes and match its builder.
        gate_v01 = gate_v01_payload()
        self.assertEqual(PRE_SHADOW_GATE_SHA256, gate_v01["gate_module_sha256"])
        self.assertEqual(
            gate_v01,
            json.loads(GATE_V01_JSON.read_text(encoding="utf-8")),
        )
        # The V0_2 gate evaluation must be stable and outcome-locked.
        decision = PreShadowTechnicalGateV02().evaluate(PreShadowGateV02Inputs(
            strategy_identity_frozen=True, machine_ready=True,
            e07_runtime_mapping_wired=True, candidate_eligibility_active=True,
            stop_oco_execution_verified=True, runtime_recovery_verified=True,
            safety_verified=True, authority_ingestion_ready=True,
            ledger_reconciliation_verified=True, statistical_profile_locked=False,
            research_wave_locked=False, shadow_authorized=False,
            fee_margin_fact_configured=False, price_limit_fact_configured=False,
            slippage_policy_configured=False, source_only_verified=True,
            outcome_exposure_clean=True,
        ))
        self.assertEqual(gate_v02["identity"], decision.identity_id)
        self.assertFalse(decision.authorized_to_start)


if __name__ == "__main__":
    unittest.main()
