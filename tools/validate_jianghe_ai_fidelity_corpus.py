#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""校验江河 AI 忠实度夹具语料 V0.1。

不做任何模型请求、不读取真实行情或收益。只验证：

1. 语料 JSON 的结构（corpus schema / rubric / 覆盖 / 硬负例 / 无污染）。
2. 语料引用的 source anchors（claim / case / unknown）确实存在于 V1.1 权威工件。

退出码：0 = 通过；1 = 任何错误。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_fidelity_scoring import CORPUS_ID, CORPUS_PATH, scan_outcome_contamination, validate_corpus

JH = ROOT / "docs" / "research" / "jianghe"
SALVAGE = JH / "second_pass_salvage"


def _load_claim_ids() -> set[str]:
    claim_ids: set[str] = set()
    paths = sorted(JH.glob("JIANGHE_CLAIM_LEDGER*.jsonl")) + sorted(
        SALVAGE.glob("JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part*.jsonl")
    )
    for path in paths:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                claim_ids.add(json.loads(line)["claim_id"])
    return claim_ids


def _load_case_ids() -> set[str]:
    case_ids: set[str] = set()
    paths = sorted(JH.glob("JIANGHE_CASE_LIBRARY*.md")) + [JH / "JIANGHE_SECOND_PASS_CASE_LIBRARY_DELTA_V1_1.md"]
    for path in paths:
        case_ids.update(re.findall(r"^## (JH-CASE-[A-Z0-9-]+)", path.read_text(encoding="utf-8"), flags=re.MULTILINE))
    return case_ids


def _load_unknown_ids() -> set[str]:
    text = (JH / "JIANGHE_UNKNOWN_REGISTER_V1_1.md").read_text(encoding="utf-8")
    return set(re.findall(r"\b(JH-UNK-\d{3})\b", text))


def _load_contradiction_ids() -> set[str]:
    text = (JH / "JIANGHE_CONTRADICTION_REGISTER_V1_1.md").read_text(encoding="utf-8")
    return set(re.findall(r"\b(JH-CON-\d{3})\b", text))


def _check_categorized_anchors(label: str, anchors: dict, registers: dict[str, set[str]], errors: list[str]) -> None:
    """按类别校验 source_anchors：claims/cases/unknowns/contradictions。"""
    category_keys = {
        "claims": "claim",
        "cases": "case",
        "unknowns": "unknown",
        "contradictions": "contradiction",
    }
    for category, known in registers.items():
        for anchor in anchors.get(category, []):
            if anchor not in known:
                errors.append(f"{label}: 引用不存在的 {category_keys[category]} 锚点 {anchor}")


def main() -> int:
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    if corpus.get("corpus_id") != CORPUS_ID:
        print("ERROR: corpus_id 不一致")
        return 1

    errors = validate_corpus(corpus)
    registers: dict[str, set[str]] = {
        "claims": _load_claim_ids(),
        "cases": _load_case_ids(),
        "unknowns": _load_unknown_ids(),
        "contradictions": _load_contradiction_ids(),
    }

    for fixture in corpus["fixtures"]:
        _check_categorized_anchors(fixture["fixture_id"], fixture.get("source_anchors", {}), registers, errors)
        for unknown in fixture["expected"].get("explicit_unknown", []):
            if unknown not in registers["unknowns"]:
                errors.append(f"{fixture['fixture_id']}: 引用不存在的 unknown 锚点 {unknown}")

    for hard_negative in corpus["hard_negatives"]:
        _check_categorized_anchors(hard_negative["id"], hard_negative.get("source_anchors", {}), registers, errors)
    for principle in corpus["principles"]:
        _check_categorized_anchors(principle["id"], principle.get("source_anchors", {}), registers, errors)

    contamination = scan_outcome_contamination(corpus)
    if contamination:
        errors.append(f"结果/未来价格污染命中 {len(contamination)} 处")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    fixture_count = len(corpus["fixtures"])
    print(f"OK: {CORPUS_ID} 校验通过（{fixture_count} 个夹具；无污染；全部锚点存在）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
