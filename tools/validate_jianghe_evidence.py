#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Validate the Jianghe V0.1 formal evidence package without reading market data."""
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "research" / "jianghe"
FAMILIES = {"JH-FAMILY-A", "JH-FAMILY-B", "JH-FAMILY-C", "JH-FAMILY-D"}
BLOCKED = {
    "007": ("LOCAL_MEDIA_BROKEN", "PENDING_REPAIR"),
    "022": ("UNAVAILABLE_PAID_GATED", "BLOCKED_SOURCE_UNAVAILABLE"),
}


def fail(message):
    raise AssertionError(message)


def load_index():
    with (EVIDENCE / "JIANGHE_SOURCE_INDEX_V0_1.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_claims():
    path = EVIDENCE / "JIANGHE_CLAIM_LEDGER_V0_1.jsonl"
    claims = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            try:
                claims.append(json.loads(line))
            except json.JSONDecodeError as error:
                fail("claim ledger line %d is not JSON: %s" % (number, error))
    return claims


def validate():
    index = load_index()
    ordinals = [row["source_ordinal"] for row in index]
    if ordinals != ["%03d" % number for number in range(1, 29)]:
        fail("source chronology must contain every ordinal 001..028 once")
    by_ordinal = {row["source_ordinal"]: row for row in index}
    for ordinal, expected in BLOCKED.items():
        row = by_ordinal[ordinal]
        if (row["source_status"], row["research_status"]) != expected:
            fail("blocked source %s has incorrect status" % ordinal)
    if any(row["research_status"] == "ANALYZED" for row in (by_ordinal["007"], by_ordinal["022"])):
        fail("blocked sources must not enter executable analysis")
    if sum(row["research_status"] == "ANALYZED" for row in index) != 26:
        fail("available analyzed source count must remain 26")
    for row in index:
        links = {value for value in row["family_links"].split("|") if value}
        if not links.issubset(FAMILIES):
            fail("source %s links an invalid family" % row["source_ordinal"])

    claims = load_claims()
    bvids = {row["bvid"] for row in index}
    claim_ids = set()
    required = {
        "claim_id", "trader_id", "source_ordinal", "bvid", "material_title",
        "source_timestamp_start", "source_timestamp_end", "source_anchor_type",
        "language_anchor_short", "visual_anchor_description", "before_after_visual_change",
        "timeframe_visible_or_stated", "instrument_if_explicit", "claim_category",
        "claim_status", "interpretation_status", "interpretation_text", "dossier_section_ids",
        "strategy_family_ids", "case_ids", "source_no_trade_if_explicit",
        "source_invalidation_if_explicit", "source_exit_or_management_if_explicit",
        "ambiguity_notes", "machineability", "review_status",
    }
    for claim in claims:
        if not required.issubset(claim):
            fail("claim %s misses required fields" % claim.get("claim_id", "UNKNOWN"))
        if claim["claim_id"] in claim_ids:
            fail("duplicate claim ID %s" % claim["claim_id"])
        claim_ids.add(claim["claim_id"])
        if claim["bvid"] not in bvids:
            fail("claim %s has BVID absent from source index" % claim["claim_id"])
        if claim["source_ordinal"] in BLOCKED:
            fail("blocked source has an executable claim: %s" % claim["claim_id"])
        if claim["claim_status"] == "EXPLICIT":
            anchored = all(claim[field] not in ("", "UNKNOWN") for field in (
                "source_timestamp_start", "source_timestamp_end", "language_anchor_short",
            ))
            if not anchored and claim["review_status"] != "SOL_REVIEW_REQUIRED":
                fail("explicit claim %s lacks an anchor/review state" % claim["claim_id"])
        links = {value for value in claim["strategy_family_ids"].split("|") if value}
        if not links.issubset(FAMILIES):
            fail("claim %s links an invalid family" % claim["claim_id"])
    for row in index:
        actual = sum(claim["source_ordinal"] == row["source_ordinal"] for claim in claims)
        if actual != int(row["claim_count"]):
            fail("source %s claim count disagrees with ledger" % row["source_ordinal"])

    case_text = (EVIDENCE / "JIANGHE_CASE_LIBRARY_V0_1.md").read_text(encoding="utf-8")
    case_ids = set(re.findall(r"^## (JH-CASE-[A-Z0-9-]+)$", case_text, flags=re.MULTILINE))
    if not case_ids:
        fail("case library contains no cases")
    for claim in claims:
        for case_id in filter(None, claim["case_ids"].split("|")):
            if case_id not in case_ids:
                fail("claim %s links missing case %s" % (claim["claim_id"], case_id))

    tracked = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).splitlines()
    banned_suffixes = {".mp4", ".mkv", ".mov", ".avi", ".srt", ".vtt", ".png", ".jpg", ".jpeg"}
    media = [path for path in tracked if Path(path).suffix.lower() in banned_suffixes]
    if media:
        fail("copyright/media artifacts tracked: %s" % media)
    secret_pattern = re.compile(r"(?i)(cookie|api[_-]?key|access[_-]?token|secret)\s*[:=]\s*[^\s]{8,}")
    checked_files = [path for path in EVIDENCE.rglob("*") if path.is_file()]
    secrets = [str(path.relative_to(ROOT)) for path in checked_files if secret_pattern.search(path.read_text(encoding="utf-8", errors="ignore"))]
    if secrets:
        fail("potential secret material tracked: %s" % secrets)
    print("JIANGHE_EVIDENCE_VALIDATION=OK claims=%d cases=%d" % (len(claims), len(case_ids)))


if __name__ == "__main__":
    try:
        validate()
    except AssertionError as error:
        print("JIANGHE_EVIDENCE_VALIDATION=FAIL: %s" % error, file=sys.stderr)
        sys.exit(1)
