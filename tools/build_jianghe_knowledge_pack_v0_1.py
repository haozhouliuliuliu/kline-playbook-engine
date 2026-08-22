"""构建江河 V1.1 知识包身份；只绑定内容，不绑定 cwd、路径或 mtime。"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_ai_trader import KnowledgePackIdentity


OUTPUT = ROOT / "docs" / "evidence" / "JIANGHE_AI_TRADER_FOUNDATION_V0_1.json"

# 左侧为永久逻辑名称；实际 Git 路径只用于读取，永不参与 identity 哈希。
KNOWLEDGE_DOCUMENTS = {
    "CURRENT_VIEW": "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md",
    "SECOND_PASS_VERIFICATION_REPORT": "docs/research/jianghe/JIANGHE_SECOND_PASS_VERIFICATION_REPORT_V1_1.md",
    "DOSSIER": "docs/research/jianghe/JIANGHE_TRADER_DOSSIER_V1_1.md",
    "SECOND_PASS_RECONCILIATION": "docs/research/jianghe/JIANGHE_SECOND_PASS_RECONCILIATION_V1_1.md",
    "STRATEGY_FAMILIES": "docs/research/jianghe/JIANGHE_STRATEGY_FAMILIES_V1_1.md",
    "UNKNOWN_REGISTER": "docs/research/jianghe/JIANGHE_UNKNOWN_REGISTER_V1_1.md",
    "CONTRADICTION_REGISTER": "docs/research/jianghe/JIANGHE_CONTRADICTION_REGISTER_V1_1.md",
    "CASE_LIBRARY_DELTA": "docs/research/jianghe/JIANGHE_SECOND_PASS_CASE_LIBRARY_DELTA_V1_1.md",
    "CLAIM_SALVAGE_MANIFEST": "docs/research/jianghe/second_pass_salvage/SECOND_PASS_SALVAGE_MANIFEST_V1_1.md",
    "SOURCE_FINDINGS_MANIFEST": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_SOURCE_FINDINGS_MANIFEST_V1_1.md",
    "CLAIM_LEDGER_BASE": "docs/research/jianghe/JIANGHE_CLAIM_LEDGER_SUPPLEMENT_FINAL_V1_0.jsonl",
    "CLAIM_DELTA_PART_00": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part00.jsonl",
    "CLAIM_DELTA_PART_01": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part01.jsonl",
    "CLAIM_DELTA_PART_02": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part02.jsonl",
    "CLAIM_DELTA_PART_03": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part03.jsonl",
    "SOURCE_FINDINGS_PART_00": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_SOURCE_FINDINGS_V1_1.part00.md",
    "SOURCE_FINDINGS_PART_01": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_SOURCE_FINDINGS_V1_1.part01.md",
    "SOURCE_FINDINGS_PART_02": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_SOURCE_FINDINGS_V1_1.part02.md",
    "SOURCE_FINDINGS_PART_03": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_SOURCE_FINDINGS_V1_1.part03.md",
    "SOURCE_FINDINGS_PART_04": "docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_SOURCE_FINDINGS_V1_1.part04.md",
}


def build_payload() -> dict[str, object]:
    documents = {
        logical_name: (ROOT / relative_path).read_text(encoding="utf-8")
        for logical_name, relative_path in KNOWLEDGE_DOCUMENTS.items()
    }
    knowledge_pack = KnowledgePackIdentity.from_documents("JIANGHE_V1_1", documents)
    return {
        "artifact": "JIANGHE_AI_TRADER_FOUNDATION_V0_1",
        "knowledge_pack_version": knowledge_pack.pack_version,
        "knowledge_pack_identity": knowledge_pack.identity,
        "document_hashes": [
            {"logical_document_id": name, "content_sha256": digest}
            for name, digest in knowledge_pack.document_hashes
        ],
        "identity_semantics": "CONTENT_AND_LOGICAL_DOCUMENT_ID_ONLY__NO_GIT_PATH_CWD_OR_MTIME",
        "source_only_verified": "NO",
        "primary_eligible": "NO",
        "candidate_outcome_backtest": "NOT_AUTHORIZED",
        "real_model_provider": "NOT_IMPLEMENTED",
        "replay_fixture_scope": "SYNTHETIC_NON_OUTCOME_ONLY",
    }


def main() -> None:
    OUTPUT.write_text(json.dumps(build_payload(), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
