"""Build the identity-only qualified candidate eligibility view v1.

The builder reads accepted metadata and the 212 already-accepted first-day raw
files solely to count their rows.  It never alters accepted raw, Parquet,
manifest, catalog, or historical acceptance evidence.
"""

from __future__ import annotations

import argparse
from datetime import date
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from src.canonical_identity import canonical_hash
from src.candidate_eligibility import (
    EXCLUSION_RULE,
    EligibilityPartition,
    QualifiedEligibilityView,
)
from tools.revalidate_canonical_corpus import _partition_identity, _raw_filename


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARENT_DATA_ROOT = Path(r"C:\Users\H\Documents\kline-playbook-engine\data")
DEFAULT_UNIVERSE = PROJECT_ROOT / "docs" / "evidence" / "CANONICAL_CONTRACT_UNIVERSE.json"
DEFAULT_REVALIDATION = PROJECT_ROOT / "docs" / "evidence" / "CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json"
DEFAULT_ADOPTION_JSON = PROJECT_ROOT / "docs" / "evidence" / "CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1_ADOPTION.json"
DEFAULT_ADOPTION_MD = PROJECT_ROOT / "docs" / "evidence" / "CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1_ADOPTION.md"
DEFAULT_VIEW_JSON = PROJECT_ROOT / "docs" / "evidence" / "CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1.json"
DEFAULT_VIEW_MD = PROJECT_ROOT / "docs" / "evidence" / "CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1.md"
DEFAULT_LOCAL_OUTPUT = PROJECT_ROOT / "data" / "candidate_eligibility_v01"

PARENT_CORPUS_IDENTITY = "1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8"
PARENT_MANIFEST_IDENTITY = "7510a4a943e85c9be256e62971b5a64d64e9976c2b01c9f5d0fe07b1c6c8d324"
EXPECTED_TOTAL_PARTITIONS = 32980
EXPECTED_EXCLUDED_PARTITIONS = 212
EXPECTED_ELIGIBLE_PARTITIONS = 32768
EXPECTED_EXCLUDED_ROWS = 70692
EXPECTED_TOTAL_ROWS = 15280452
EXPECTED_FAILURES = 116
EXPECTED_CLEAN_FIRST_DAYS = 96


def _load_object(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load JSON object: {path}") from error
    if not isinstance(data, dict):
        raise ValueError(f"JSON document must be an object: {path}")
    return data


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _adoption_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema_version": "canonical-qualified-eligibility-adoption-v1",
        "view_version": "QUALIFIED_ELIGIBILITY_VIEW_V1",
        "owner_direction_date": "2026-08-21",
        "owner_direction": (
            "Owner directed the project brain to directly decide and proceed for clear evidence "
            "and recommended ordinary research semantics, without redundant approval gates."
        ),
        "project_brain_decision": "ADOPT_RECOMMENDED_OPTION_A",
        "adopted_semantics": "QUALIFIED_ELIGIBILITY_VIEW_WITH_UNIFORM_FIRST_TRADING_DAY_EXCLUSION",
        "historical_acceptance_changed": False,
        "candidate_quality_input_eligibility_changed": True,
        "no_candidate_outcome_used": True,
        "validation_used": False,
        "historical_final_holdout_used": False,
        "shadow_used": False,
        "excluded_partition_count": EXPECTED_EXCLUDED_PARTITIONS,
        "excluded_row_count": EXPECTED_EXCLUDED_ROWS,
        "excluded_row_percent": "0.46263029",
        "eligible_partition_count": EXPECTED_ELIGIBLE_PARTITIONS,
        "authority_basis": "docs/reviews/CANONICAL_COMPLETENESS_AUTHORITY_RESOLUTION_V0_1.md#recommended-option-a",
    }
    payload["adoption_evidence_identity"] = canonical_hash(payload)
    return payload


def write_adoption_evidence(json_output: Path, markdown_output: Path) -> dict[str, Any]:
    payload = _adoption_payload()
    _write_json(json_output, payload)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.write_text("\n".join([
        "# Canonical qualified eligibility view v1 — adoption",
        "",
        "```text",
        "VIEW_VERSION=QUALIFIED_ELIGIBILITY_VIEW_V1",
        "ADOPTED_SEMANTICS=QUALIFIED_ELIGIBILITY_VIEW_WITH_UNIFORM_FIRST_TRADING_DAY_EXCLUSION",
        "HISTORICAL_ACCEPTANCE_CHANGED=NO",
        "CANDIDATE_QUALITY_INPUT_ELIGIBILITY_CHANGED=YES",
        "NO_CANDIDATE_OUTCOME_USED=YES",
        "VALIDATION_USED=NO",
        "HISTORICAL_FINAL_HOLDOUT_USED=NO",
        "SHADOW_USED=NO",
        f"EXCLUDED_PARTITIONS={EXPECTED_EXCLUDED_PARTITIONS}",
        f"EXCLUDED_ROWS={EXPECTED_EXCLUDED_ROWS}",
        "EXCLUDED_ROW_PERCENT=0.46263029",
        f"ELIGIBLE_PARTITIONS={EXPECTED_ELIGIBLE_PARTITIONS}",
        f"ADOPTION_EVIDENCE_IDENTITY={payload['adoption_evidence_identity']}",
        "```",
        "",
        "2026-08-21，Owner 指示项目脑对已有清晰证据和普通研究语义直接决定并推进，不再设置重复批准关口。项目脑据此前完整性权威裁决所推荐的 OPTION_A，采纳首个受治理交易日统一排除。",
        "",
        "这只改变候选质量研究可使用的输入资格：所有具体合约的受治理首个交易日均不可用。它不删除、不重写、也不重新验收历史已接受语料；116 个 D01/D02 失败仍是历史重新验证中的失败，绝不会被改写为通过。",
    ]) + "\n", encoding="utf-8")
    return payload


def _implementation_identity() -> str:
    module = PROJECT_ROOT / "src" / "candidate_eligibility.py"
    tool = Path(__file__)
    return canonical_hash({
        "implementation_version": "canonical-qualified-eligibility-implementation-v1",
        "module_sha256": sha256(module.read_bytes()).hexdigest(),
        "builder_sha256": sha256(tool.read_bytes()).hexdigest(),
    })


def _partitions(manifest: dict[str, Any]) -> tuple[EligibilityPartition, ...]:
    entries = manifest.get("partitions")
    if not isinstance(entries, list):
        raise ValueError("accepted manifest must contain partitions")
    out = []
    for item in entries:
        if not isinstance(item, dict):
            raise ValueError("accepted manifest has a non-object partition")
        try:
            out.append(EligibilityPartition(
                partition_identity=_partition_identity(item),
                concrete_contract=str(item["contract"]),
                trading_day=date.fromisoformat(str(item["trading_day"])),
            ))
        except (KeyError, ValueError) as error:
            raise ValueError("accepted manifest has an invalid partition identity") from error
    ordered = tuple(sorted(out))
    if len({item.partition_identity for item in ordered}) != len(ordered):
        raise ValueError("accepted manifest has duplicate partition identities")
    return ordered


def _first_day_keys(universe: dict[str, Any]) -> set[tuple[str, str]]:
    contracts = universe.get("contracts")
    if not isinstance(contracts, list):
        raise ValueError("contract universe must contain contracts")
    out: set[tuple[str, str]] = set()
    for item in contracts:
        if not isinstance(item, dict) or not isinstance(item.get("concrete_contract"), str) or not isinstance(item.get("first_trading_day"), str):
            raise ValueError("contract universe contains invalid first-trading-day bounds")
        key = (item["concrete_contract"], item["first_trading_day"])
        if key in out:
            raise ValueError("contract universe repeats a concrete contract first day")
        out.add(key)
    return out


def _count_excluded_rows(manifest_entries: list[dict[str, Any]], excluded: tuple[EligibilityPartition, ...], raw_root: Path) -> int:
    by_identity = {_partition_identity(item): item for item in manifest_entries}
    total = 0
    for partition in excluded:
        entry = by_identity.get(partition.partition_identity)
        if entry is None:
            raise ValueError("excluded partition is absent from accepted manifest")
        path = raw_root / _raw_filename(entry)
        try:
            records = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise ValueError(f"cannot count accepted excluded raw rows: {path}") from error
        if not isinstance(records, list):
            raise ValueError("accepted excluded raw payload must be a list")
        total += len(records)
    return total


def build_view(
    *,
    manifest: dict[str, Any],
    universe: dict[str, Any],
    revalidation: dict[str, Any],
    adoption: dict[str, Any],
    raw_root: Path,
    implementation_identity: str,
    contract_universe_source_artifact_sha256: str,
) -> tuple[QualifiedEligibilityView, dict[str, Any]]:
    if manifest.get("manifest_identity") != PARENT_MANIFEST_IDENTITY:
        raise ValueError("accepted manifest identity does not match the governed parent")
    partitions = _partitions(manifest)
    if len(partitions) != EXPECTED_TOTAL_PARTITIONS:
        raise ValueError("accepted partition count does not match the governed parent")
    first_day_keys = _first_day_keys(universe)
    excluded = tuple(item for item in partitions if (item.concrete_contract, item.trading_day.isoformat()) in first_day_keys)
    if len(excluded) != EXPECTED_EXCLUDED_PARTITIONS or len(first_day_keys) != EXPECTED_EXCLUDED_PARTITIONS:
        raise ValueError("uniform first-trading-day exclusion count is not 212")
    failure_entries = revalidation.get("failure_partitions")
    if revalidation.get("revalidation_identity") != "42e0de64e47c91156f82bbd09b53e404e93a69eebd2bc2e950c8b58c8753af32" or not isinstance(failure_entries, list):
        raise ValueError("revalidation evidence identity is not the governed D01/D02 result")
    failure_ids = {str(item.get("partition_identity")) for item in failure_entries if isinstance(item, dict)}
    excluded_ids = {item.partition_identity for item in excluded}
    if len(failure_ids) != EXPECTED_FAILURES or not failure_ids <= excluded_ids:
        raise ValueError("revalidation failures must be exactly the excluded first-day subset")
    if len(excluded_ids - failure_ids) != EXPECTED_CLEAN_FIRST_DAYS:
        raise ValueError("uniform exclusion must retain 96 clean first-day partitions")
    eligible_ids = tuple(sorted(item.partition_identity for item in partitions if item.partition_identity not in excluded_ids))
    if len(eligible_ids) != EXPECTED_ELIGIBLE_PARTITIONS:
        raise ValueError("eligible partition count is not 32768")
    if revalidation.get("pass_count") != 32864 or revalidation.get("fail_count") != EXPECTED_FAILURES:
        raise ValueError("revalidation summary counts are not governed")
    excluded_rows = _count_excluded_rows(manifest["partitions"], excluded, raw_root)
    if excluded_rows != EXPECTED_EXCLUDED_ROWS:
        raise ValueError("uniform excluded row count is not 70692")
    if adoption.get("adoption_evidence_identity") != canonical_hash({key: value for key, value in adoption.items() if key != "adoption_evidence_identity"}):
        raise ValueError("adoption evidence identity is invalid")
    if adoption.get("adopted_semantics") != "QUALIFIED_ELIGIBILITY_VIEW_WITH_UNIFORM_FIRST_TRADING_DAY_EXCLUSION":
        raise ValueError("adoption evidence does not authorize the qualified view")
    universe_identity = canonical_hash(universe)
    view = QualifiedEligibilityView(
        parent_corpus_identity=PARENT_CORPUS_IDENTITY,
        parent_manifest_identity=PARENT_MANIFEST_IDENTITY,
        contract_universe_identity=universe_identity,
        contract_universe_source_artifact_sha256=contract_universe_source_artifact_sha256,
        revalidation_evidence_identity=str(revalidation["revalidation_identity"]),
        authority_decision_evidence_identity=str(adoption["adoption_evidence_identity"]),
        implementation_identity=implementation_identity,
        excluded_partitions=excluded,
        included_partition_root_identity=canonical_hash(list(eligible_ids)),
        excluded_partition_count=len(excluded),
        eligible_partition_count=len(eligible_ids),
        excluded_row_count=excluded_rows,
    )
    certificate = {
        "revalidation_evidence_identity": revalidation["revalidation_identity"],
        "d01_pass_count": len(eligible_ids),
        "d02_pass_count": len(eligible_ids),
        "uncertified_partition_count": 0,
        "failure_partition_count": len(failure_ids),
        "clean_first_day_exclusion_count": len(excluded_ids - failure_ids),
        "total_accepted_row_count": EXPECTED_TOTAL_ROWS,
        "historical_accepted_corpus_modified": False,
        "no_candidate_outcome_used": True,
    }
    return view, certificate


def _view_markdown(view: QualifiedEligibilityView, certificate: dict[str, Any]) -> str:
    return "\n".join([
        "# Canonical qualified eligibility view v1",
        "",
        "```text",
        f"VIEW_IDENTITY={view.identity()}",
        f"PARENT_CORPUS_IDENTITY={view.parent_corpus_identity}",
        f"PARENT_MANIFEST_IDENTITY={view.parent_manifest_identity}",
        f"EXCLUSION_RULE={EXCLUSION_RULE}",
        f"EXCLUDED_PARTITIONS={view.excluded_partition_count}",
        f"EXCLUDED_ROWS={view.excluded_row_count}",
        "EXCLUDED_ROW_PERCENT=0.46263029",
        f"ELIGIBLE_PARTITIONS={view.eligible_partition_count}",
        f"D01_CERTIFIED_ELIGIBLE={certificate['d01_pass_count']}",
        f"D02_CERTIFIED_ELIGIBLE={certificate['d02_pass_count']}",
        "UNCERTIFIED_PARTITIONS=0",
        "HISTORICAL_ACCEPTED_CORPUS_MODIFIED=NO",
        "NO_CANDIDATE_OUTCOME_USED=YES",
        "MAPPING_AUTHORITY=UNRESOLVED_FAIL_CLOSED",
        "PRICE_LIMIT_AUTHORITY=UNRESOLVED_FAIL_CLOSED",
        "LIMIT_002_CANDIDATE_QUALITY_CANONICAL_ELIGIBILITY=READY_TO_CLOSE_ON_INTEGRATION",
        "```",
        "",
        "该视图是候选质量研究输入的确定性资格层，不是历史语料删除、重抓、重写或重新验收。它由合约宇宙的首个受治理交易日统一导出；116 个失败和 96 个已通过的首日分区均被排除。其余 32,768 个分区由完整 D01/D02 重新验证证据认证。",
    ]) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the canonical qualified candidate eligibility view v1")
    parser.add_argument("--parent-data-root", type=Path, default=DEFAULT_PARENT_DATA_ROOT)
    parser.add_argument("--universe", type=Path, default=DEFAULT_UNIVERSE)
    parser.add_argument("--revalidation", type=Path, default=DEFAULT_REVALIDATION)
    parser.add_argument("--adoption-json", type=Path, default=DEFAULT_ADOPTION_JSON)
    parser.add_argument("--adoption-markdown", type=Path, default=DEFAULT_ADOPTION_MD)
    parser.add_argument("--view-json", type=Path, default=DEFAULT_VIEW_JSON)
    parser.add_argument("--view-markdown", type=Path, default=DEFAULT_VIEW_MD)
    parser.add_argument("--local-output", type=Path, default=DEFAULT_LOCAL_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    adoption = _adoption_payload()
    manifest = _load_object(args.parent_data_root / "canonical" / "manifest.json")
    view, certificate = build_view(
        manifest=manifest,
        universe=_load_object(args.universe),
        revalidation=_load_object(args.revalidation),
        adoption=adoption,
        raw_root=args.parent_data_root / "raw" / "historical",
        implementation_identity=_implementation_identity(),
        contract_universe_source_artifact_sha256=sha256(args.universe.read_bytes()).hexdigest(),
    )
    evidence = view.to_dict()
    evidence["all_remaining_certificate"] = certificate
    evidence["excluded_row_percent"] = "0.46263029"
    evidence["historical_revalidation_status"] = "32864_PASS_116_FAIL"
    evidence["historical_accepted_corpus_modified"] = False
    evidence["candidate_quality_data_identity_template"] = {
        "parent_corpus_identity": view.parent_corpus_identity,
        "qualified_eligibility_view_identity": view.identity(),
        "mapping_authority_identity": "UNRESOLVED_FAIL_CLOSED",
        "price_limit_authority_identity": "UNRESOLVED_FAIL_CLOSED",
        "other_required_governed_inputs": "REQUIRED_AT_FUTURE_CANDIDATE_INTEGRATION",
        "candidate_outcome_ready": False,
    }
    if not args.dry_run:
        write_adoption_evidence(args.adoption_json, args.adoption_markdown)
        _write_json(args.view_json, evidence)
        args.view_markdown.parent.mkdir(parents=True, exist_ok=True)
        args.view_markdown.write_text(_view_markdown(view, certificate), encoding="utf-8")
        _write_json(args.local_output / "eligibility_manifest.json", evidence)
    print(json.dumps({
        "dry_run": args.dry_run,
        "qualified_eligibility_view_identity": view.identity(),
        "excluded_partition_count": view.excluded_partition_count,
        "eligible_partition_count": view.eligible_partition_count,
        "excluded_row_count": view.excluded_row_count,
        "uncertified_partition_count": certificate["uncertified_partition_count"],
    }, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
