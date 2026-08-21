"""Build the pre-outcome Holy Grail V0.4 PRIMARY freeze evidence."""

from __future__ import annotations

import json
from pathlib import Path

from src.playbook_contract import bridge_to_strategy_identity
from tools.build_raschke_holy_grail_playbook_contract_draft_v0_4 import (
    build_contract,
    strategy_parameters,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "evidence" / "HOLY_GRAIL_PRIMARY_FREEZE_V0_1.json"


def build_payload() -> dict[str, object]:
    contract = build_contract()
    machine = contract.machine
    if machine is None:
        raise ValueError("Holy Grail V0.4 machine layer is required")
    strategy = bridge_to_strategy_identity(
        contract,
        parameters=strategy_parameters(),
        code_hash=machine.code_hash,
        environment_hash=machine.environment_hash,
        required_feature_versions=machine.required_feature_versions,
        data_exposure_history_reference=contract.data_exposure_history_reference,
    )
    return {
        "artifact": "HOLY_GRAIL_PRIMARY_FREEZE_V0_1",
        "protocol_version": "1.0",
        "primary_playbook": "RASCHKE_HOLY_GRAIL_V0_4",
        "primary_contract_identity": contract.contract_identity,
        "primary_selection_identity": contract.primary_selection_identity,
        "strategy_identity": strategy.identity_id,
        "strategy_version": strategy.strategy_version,
        "parameter_hash": strategy.parameter_hash,
        "machine_code_hash": strategy.code_hash,
        "machine_environment_hash": strategy.environment_hash,
        "feature_versions": list(strategy.required_feature_versions),
        "product_scope": ["cu", "al", "ni", "au", "ag", "rb"],
        "scope_rule": "ALL_CANONICAL_PRODUCTS_UNIFORM_SCOPE",
        "primary_timeframe": "BASE_1_MINUTE",
        "outcome_tested_higher_timeframe_alternatives": [],
        "outcome_tested_alternatives": [],
        "parameter_search_ranges": "FIXED_BY_V0_4_MACHINE_PARAMETERS",
        "lineage": contract.research_lineage_id,
        "candidate_eligibility_view_identity": "fb30bfaf0433df02b4ee7d1e781b25473c7271495924859c1d781b87e036c822",
        "source_governed_mapping_required": "E07_SOURCE_GOVERNED_TQSDK_MAPPING_V0_1",
        "candidate_outcome_data_used": "NO",
        "outcome_test_registered": "NO",
        "research_wave_locked": "NO",
        "status": "PRIMARY_FROZEN_PRE_OUTCOME",
    }


def main() -> None:
    OUT.write_text(json.dumps(build_payload(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
