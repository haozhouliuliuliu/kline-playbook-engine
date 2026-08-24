"""江河 V1.1 的 material-bound SOURCE_ONLY 验证会话构建器。

本模块只读取已提交的江河来源研究工件，并把它们绑定到
``SourceOnlyClaimExtractionContext``。它不读取候选行情、收益、Validation、
Final 或任何结果工件。
"""

from __future__ import annotations

import csv
import io
import json
import re
import shutil
import subprocess
from hashlib import sha256
from pathlib import Path
from typing import Iterable

from src.research_firewall import (
    ApprovedSourceBundle,
    ApprovedSourceMaterialRef,
    ClaimRecordOutput,
    ProtectedProjectSurface,
    SourceOnlyClaimExtractionContext,
    SourceOnlyPolicy,
)


ROOT = Path(__file__).resolve().parents[1]
JIANGHE_ROOT = ROOT / "docs" / "research" / "jianghe"
SALVAGE_ROOT = JIANGHE_ROOT / "second_pass_salvage"
FOUNDATION_PATH = ROOT / "docs" / "evidence" / "JIANGHE_AI_TRADER_FOUNDATION_V0_1.json"

SESSION_ID = "JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_GATE_V0_1_20260823"
MODEL_IDENTITY = "CODEX_GPT_5_DESKTOP_AGENT__MODEL_VERSION_NOT_EXPOSED"
PROMPT_SPEC_IDENTITY = "JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_GATE_V0_1"
TOOL_RETRIEVAL_MODE = "REPOSITORY_BOUND_JIANGHE_SOURCE_MANIFESTS_ONLY__NO_MARKET_OR_OUTCOME_TOOLS"
_GIT_EXECUTABLE = shutil.which("git") or "git"


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def _normalize_worktree_text_bytes(content: bytes) -> bytes:
    """Normalize only the CRLF transform Git may apply to checked-out text files."""
    return content.replace(b"\r\n", b"\n")


def _repository_blob_bytes(path: Path) -> bytes:
    """Return exact committed Git blob bytes and fail closed on real worktree drift.

    SOURCE_ONLY claims exact *repository* artifact bytes. Git blobs are the repository
    authority; OS checkout newline transforms are not. A working tree may differ only
    by CRLF<->LF checkout normalization. Any other difference is an uncommitted material
    change and must not be silently laundered into a verified session.
    """
    if not path.is_file():
        raise ValueError(f"repository material missing: {_relative(path)}")
    relative = _relative(path)
    process = subprocess.run(
        [_GIT_EXECUTABLE, "show", f"HEAD:{relative}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise ValueError(f"cannot resolve committed repository blob: {relative}")
    blob = bytes(process.stdout)
    worktree = path.read_bytes()
    if worktree != blob and _normalize_worktree_text_bytes(worktree) != blob:
        raise ValueError(f"working tree differs from committed repository material: {relative}")
    return blob


def _repository_text(path: Path) -> str:
    try:
        return _repository_blob_bytes(path).decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError(f"repository material is not UTF-8 text: {_relative(path)}") from error


def _source_paths() -> tuple[Path, ...]:
    coverage = tuple(sorted(SALVAGE_ROOT.glob("JIANGHE_SECOND_PASS_SOURCE_COVERAGE_RECORD_V1_1.part*.csv")))
    findings = tuple(sorted(SALVAGE_ROOT.glob("JIANGHE_SECOND_PASS_SOURCE_FINDINGS_V1_1.part*.md")))
    indexes = (
        JIANGHE_ROOT / "JIANGHE_SOURCE_INDEX_V0_1.csv",
        *tuple(sorted(JIANGHE_ROOT.glob("JIANGHE_SOURCE_INDEX_DELTA_*.csv"))),
        JIANGHE_ROOT / "JIANGHE_SOURCE_INDEX_SUPPLEMENT_FINAL_V1_0.csv",
    )
    manifests = (
        SALVAGE_ROOT / "SECOND_PASS_SALVAGE_MANIFEST_V1_1.md",
        SALVAGE_ROOT / "JIANGHE_SECOND_PASS_SOURCE_FINDINGS_MANIFEST_V1_1.md",
        SALVAGE_ROOT / "JIANGHE_SECOND_PASS_INTEGRITY_CHECK_V1_1.md",
    )
    return coverage + findings + indexes + manifests


def _claim_paths() -> tuple[Path, ...]:
    return tuple(sorted(JIANGHE_ROOT.glob("JIANGHE_CLAIM_LEDGER*.jsonl"))) + tuple(
        sorted(SALVAGE_ROOT.glob("JIANGHE_SECOND_PASS_CLAIM_LEDGER*.jsonl"))
    )


def _case_paths() -> tuple[Path, ...]:
    return tuple(sorted(JIANGHE_ROOT.glob("JIANGHE_CASE_LIBRARY*.md"))) + (
        JIANGHE_ROOT / "JIANGHE_SECOND_PASS_CASE_LIBRARY_DELTA_V1_1.md",
    )


def _assert_paths_exist(paths: Iterable[Path]) -> tuple[Path, ...]:
    normalized = tuple(paths)
    if not normalized or any(not path.is_file() for path in normalized):
        raise ValueError("江河 SOURCE_ONLY 物料清单不完整")
    if len(set(normalized)) != len(normalized):
        raise ValueError("江河 SOURCE_ONLY 物料清单存在重复文件")
    return normalized


def _manifest(label: str, paths: Iterable[Path]) -> dict[str, object]:
    resolved = _assert_paths_exist(paths)
    materials = []
    for index, path in enumerate(resolved, start=1):
        blob = _repository_blob_bytes(path)
        materials.append(
            {
                "logical_material_id": f"{label}:{index:03d}",
                "repository_artifact": _relative(path),
                "content_sha256": sha256(blob).hexdigest(),
                "byte_size": len(blob),
            }
        )
    return {
        "manifest_id": label,
        "material_count": len(materials),
        "materials": materials,
        "manifest_identity": _canonical_hash(materials),
        "binding_status": "EXACT_REPOSITORY_ARTIFACT_BYTES_BOUND",
    }


def _claim_summary(paths: Iterable[Path]) -> dict[str, object]:
    claims: list[dict[str, object]] = []
    for path in _assert_paths_exist(paths):
        for line_number, line in enumerate(_repository_text(path).splitlines(), start=1):
            if line.strip():
                try:
                    claims.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"江河 claim 清单 JSONL 无法解析：{_relative(path)}:{line_number}") from error

    required_fields = ("claim_id", "source_ordinal", "claim_status", "review_status")
    missing = {
        field: [str(claim.get("claim_id", "<missing>")) for claim in claims if not claim.get(field)]
        for field in required_fields
    }
    if any(missing.values()):
        raise ValueError("江河 claim 身份字段不完整")
    claim_ids = [str(claim["claim_id"]) for claim in claims]
    if len(set(claim_ids)) != len(claim_ids):
        raise ValueError("江河 claim_id 不唯一")
    statuses = sorted({str(claim["claim_status"]) for claim in claims})
    if set(statuses) - {"EXPLICIT", "INFERRED", "UNKNOWN"}:
        raise ValueError("江河 claim status 不符合冻结 schema")
    return {
        "claim_record_count": len(claims),
        "unique_claim_id_count": len(set(claim_ids)),
        "claim_statuses": statuses,
        "claim_identity_completeness": "PASS",
        "claim_manifest_identity": _manifest("JIANGHE_V1_1_CLAIM_MANIFEST", paths)["manifest_identity"],
    }


def _case_summary(paths: Iterable[Path]) -> dict[str, object]:
    case_ids: list[str] = []
    for path in _assert_paths_exist(paths):
        case_ids.extend(
            re.findall(r"^## (JH-CASE-[A-Z0-9-]+)", _repository_text(path), flags=re.MULTILINE)
        )
    if not case_ids or len(set(case_ids)) != len(case_ids):
        raise ValueError("江河 case_id 缺失或不唯一")
    return {
        "case_record_count": len(case_ids),
        "unique_case_id_count": len(set(case_ids)),
        "case_identity_completeness": "PASS",
        "case_manifest_identity": _manifest("JIANGHE_V1_1_CASE_MANIFEST", paths)["manifest_identity"],
    }


def _coverage_summary() -> dict[str, object]:
    paths = tuple(sorted(SALVAGE_ROOT.glob("JIANGHE_SECOND_PASS_SOURCE_COVERAGE_RECORD_V1_1.part*.csv")))
    text = "".join(_repository_text(path) for path in _assert_paths_exist(paths))
    rows = list(csv.DictReader(io.StringIO(text)))
    if len(rows) != 99 or len({row["source_ordinal"] for row in rows}) != 99:
        raise ValueError("江河 source coverage 不是完整 001..099")
    if [row["source_ordinal"] for row in rows] != [f"{number:03d}" for number in range(1, 100)]:
        raise ValueError("江河 source coverage 序号不是连续 001..099")
    if len({row["bvid"] for row in rows}) != 99:
        raise ValueError("江河 source coverage BVID 不唯一")
    paid = [row for row in rows if row["source_ordinal"] == "022"]
    accessible = [row for row in rows if row["source_ordinal"] != "022"]
    if len(paid) != 1 or "PAID" not in paid[0]["access_status"]:
        raise ValueError("江河付费门控例外不符合 V1.1 authority")
    if len(accessible) != 98 or any(
        row["timeline_coverage"] != "FULL_TIMELINE_REVIEWED_0_TO_END"
        or float(row["unaccounted_timeline_gap_seconds"]) != 0
        for row in accessible
    ):
        raise ValueError("江河可访问 source coverage 未完整闭合")
    return {
        "source_total": len(rows),
        "unique_bvid_count": len({row["bvid"] for row in rows}),
        "accessible_source_count": len(accessible),
        "paid_gate_exception": "022",
        "unaccounted_timeline_gap": 0,
        "source_coverage_completeness": "PASS",
    }


def _knowledge_pack() -> dict[str, object]:
    if not FOUNDATION_PATH.is_file():
        raise ValueError("江河知识包基础工件缺失")
    payload = json.loads(_repository_text(FOUNDATION_PATH))
    if payload.get("knowledge_pack_version") != "JIANGHE_V1_1" or not payload.get("knowledge_pack_identity"):
        raise ValueError("江河 V1.1 知识包身份缺失")
    return {
        "knowledge_pack_version": payload["knowledge_pack_version"],
        "knowledge_pack_identity": payload["knowledge_pack_identity"],
        "document_hash_count": len(payload.get("document_hashes", ())),
    }


def build_verification_payload() -> dict[str, object]:
    """建立一次真实 project-API SOURCE_ONLY 会话并返回可持久化证据。

    会话只传入仓库中已批准的来源/claim/case 工件。所有受保护项目结果
    请求都经过同一拒绝面，因而既不会获得结果，也不会打开结果工件。
    """

    source_manifest = _manifest("JIANGHE_V1_1_SOURCE_MATERIAL_MANIFEST", _source_paths())
    claim_manifest = _manifest("JIANGHE_V1_1_CLAIM_MANIFEST", _claim_paths())
    case_manifest = _manifest("JIANGHE_V1_1_CASE_MANIFEST", _case_paths())
    knowledge_pack = _knowledge_pack()

    all_materials = (
        ("SOURCE", _source_paths()),
        ("CLAIM", _claim_paths()),
        ("CASE", _case_paths()),
    )
    material_refs: list[ApprovedSourceMaterialRef] = []
    for category, paths in all_materials:
        for index, path in enumerate(_assert_paths_exist(paths), start=1):
            material_refs.append(
                ApprovedSourceMaterialRef.from_bytes(
                    source_id="JIANGHE_TRADER_V1_1",
                    material_id=f"{category}:{index:03d}",
                    source_anchor_reference=f"JIANGHE_V1_1:{category}:{index:03d}",
                    content=_repository_blob_bytes(path),
                )
            )
    source_bundle = ApprovedSourceBundle(
        source_bundle_id="JIANGHE_V1_1_SOURCE_ONLY_MATERIAL_BUNDLE_V0_1",
        source_bundle_hash=_canonical_hash(
            {
                "source_material_manifest": source_manifest["manifest_identity"],
                "claim_manifest": claim_manifest["manifest_identity"],
                "case_manifest": case_manifest["manifest_identity"],
            }
        ),
        source_anchor_reference="JIANGHE_V1_1_SOURCE_AUTHORITY_CHAIN",
        materials=tuple(material_refs),
        content_note="只绑定仓库中的来源研究工件；不复制或读取原始受版权保护视频。",
    )
    policy = SourceOnlyPolicy()
    session = policy.open_verified_session(
        session_id=SESSION_ID,
        model_identity=MODEL_IDENTITY,
        prompt_spec_version=PROMPT_SPEC_IDENTITY,
        source_bundle_identity=source_bundle.session_binding_identity,
        source_bundle_hash=source_bundle.session_binding_hash,
        tool_retrieval_mode=TOOL_RETRIEVAL_MODE,
        researcher_model_exposure_note=(
            "模型的潜在/参数化市场先验无法被证明不存在；本会话未提供任何项目候选结果、"
            "P&L、Validation、Final 或结果工件。"
        ),
        knowledge_pack_identity=str(knowledge_pack["knowledge_pack_identity"]),
        claim_manifest_identity=str(claim_manifest["manifest_identity"]),
        case_manifest_identity=str(case_manifest["manifest_identity"]),
    )
    context = SourceOnlyClaimExtractionContext(
        source_bundle=source_bundle,
        source_only=policy,
        session_id=session.session_id,
        output_surface=ClaimRecordOutput(),
    )
    if not context.verified:
        raise ValueError("江河 SOURCE_ONLY 会话未被项目机制验证")

    protected_surfaces = (
        ProtectedProjectSurface.CANDIDATE_OUTCOME_RUNNER,
        ProtectedProjectSurface.CANDIDATE_PNL,
        ProtectedProjectSurface.VALIDATION,
        ProtectedProjectSurface.FINAL,
    )
    denials = [context.request_protected_project_surface(surface) for surface in protected_surfaces]
    denials.append(context.attempt_open_protected_outcome_artifact())
    if any(denial.outcome != "DENIED" or denial.reason != "SOURCE_ONLY_TECHNICAL_DENIAL" for denial in denials):
        raise ValueError("江河 SOURCE_ONLY 保护面未失败闭合")

    unknown_register = _repository_text(JIANGHE_ROOT / "JIANGHE_UNKNOWN_REGISTER_V1_1.md")
    contradiction_register = _repository_text(JIANGHE_ROOT / "JIANGHE_CONTRADICTION_REGISTER_V1_1.md")
    family_document = _repository_text(JIANGHE_ROOT / "JIANGHE_STRATEGY_FAMILIES_V1_1.md")
    family_ids = re.findall(r"^## (JH-FAMILY-[A-Z])", family_document, flags=re.MULTILINE)
    if family_ids != ["JH-FAMILY-A", "JH-FAMILY-B", "JH-FAMILY-C", "JH-FAMILY-D"]:
        raise ValueError("江河策略家族不再是唯一 A/B/C/D")
    if "JH-UNK-047" not in unknown_register or "FAIL-CLOSED / NOT USED" not in unknown_register:
        raise ValueError("江河 UNKNOWN fail-closed 记录缺失")
    if "Open contradiction count" not in contradiction_register or "`0`" not in contradiction_register:
        raise ValueError("江河 contradiction 记录不完整")

    return {
        "artifact": "JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1",
        "source_only_verified": "YES",
        "primary_eligible": "NO",
        "candidate_outcome_backtest": "NOT_AUTHORIZED",
        "verification_scope": "PROJECT_API_SESSION_MECHANISM__MATERIAL_BOUND_SOURCE_ONLY",
        "knowledge_pack": knowledge_pack,
        "source_material_manifest": source_manifest,
        "claim_manifest": {
            **claim_manifest,
            **_claim_summary(_claim_paths()),
        },
        "case_manifest": {
            **case_manifest,
            **_case_summary(_case_paths()),
        },
        "source_coverage": _coverage_summary(),
        "session": {
            "session_id": session.session_id,
            "session_identity": session.session_identity,
            "model_identity": session.model_identity,
            "prompt_spec_version": session.prompt_spec_version,
            "tool_retrieval_mode": session.tool_retrieval_mode,
            "protected_market_access_mode": session.protected_market_access_mode.value,
            "source_bundle_identity": session.source_bundle_identity,
            "source_bundle_hash": session.source_bundle_hash,
            "knowledge_pack_identity": session.knowledge_pack_identity,
            "claim_manifest_identity": session.claim_manifest_identity,
            "case_manifest_identity": session.case_manifest_identity,
            "verification_evidence": session.verification_evidence,
            "is_project_issued_verified": policy.is_verified(session.session_id),
        },
        "technical_denials": [
            {
                "requested_surface": denial.requested_surface.value,
                "outcome": denial.outcome,
                "reason": denial.reason,
                "opened_artifact": "NO",
            }
            for denial in denials
        ],
        "semantic_verification": {
            "verification_mode": "MANIFEST_AND_EXISTING_V1_1_SEMANTIC_PRESERVATION__NO_REDISTILLATION",
            "new_claims_created": 0,
            "new_cases_created": 0,
            "unknown_preservation": "PASS__UNKNOWN_REMAINS_UNKNOWN__NO_PROJECT_SEMANTIC_RESOLUTION",
            "contradiction_preservation": "PASS__NO_OPEN_CONTRADICTION_REQUIRES_INVENTED_RESOLUTION",
            "family_consistency": "PASS__JH_FAMILY_A_B_C_D_ONLY",
            "source_provided_case_outcomes": "SOURCE_MATERIAL_ONLY__NOT_PROJECT_CANDIDATE_PERFORMANCE",
        },
        "residual_threat_model": {
            "latent_model_market_knowledge": "NOT_PROVABLE_ABSENT__DISCLOSED",
            "source_only_os_process_sandbox": "NOT_PROVEN_NOT_CLAIMED",
            "meaning_of_verified": "PROJECT_API_SESSION_MECHANISM_REPORTED_VERIFIED",
        },
        "primary_remaining_requirements": [
            "Jianghe A/B/C/D claims still require source-justified PRIMARY branches before any outcome-bearing route.",
            "UNKNOWN and source-internal conflicts remain non-machine-eligible; this session does not resolve them.",
            "A real provider/model version, its JiangheAITraderIdentity, and synthetic fidelity evidence remain unimplemented/unverified.",
            "Candidate outcomes, Development performance, Validation, Final, Shadow, Broker, and real money remain unauthorized.",
        ],
    }
