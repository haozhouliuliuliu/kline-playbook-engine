"""Bounded SOURCE_ONLY semantic completion for Adam H. Grimes's Failure Test.

This tool records source provenance and semantic limits only.  It never opens a
market-data surface and its one protected-outcome request must be denied.

Run with:
    python -m tools.run_grimes_failure_test_semantic_completion_source_only
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.request import Request, urlopen

from src.research_firewall import (
    ApprovedSourceBundle,
    ApprovedSourceMaterialRef,
    ClaimRecordDraft,
    ClaimRecordOutput,
    SourceOnlyClaimExtractionContext,
    SourceOnlyPolicy,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID = "SRC-GRIMES"
BUNDLE_ID = "SB-GRIMES-FAILURE-TEST-SEMANTIC-V1"
SESSION_ID = "SOURCE_ONLY_GRIMES_FAILURE_TEST_SEMANTIC_V1_20260821"
MODEL_IDENTITY = "gpt-5"
PROMPT_SPEC_VERSION = "GRIMES_FREE_PUBLIC_PLAYBOOK_PROMOTION_AND_SEMANTIC_COMPLETION_V0_1"
RETRIEVAL_MODE = "DIRECT_FREE_PUBLIC_AUTHOR_BLOG_ONLY"
CREATED_AT = "2026-08-21T00:00:00Z"

RETENTION_BOUNDARY = (
    "Fetched HTML was used in memory only and is not committed. The repository retains "
    "canonical URLs, exact fetched-byte digests/sizes, short attributable paraphrases, "
    "and semantic findings; it does not redistribute full third-party articles."
)
EXPOSURE_NOTE = (
    "Model latent market knowledge cannot be proven absent. The project SOURCE_ONLY "
    "runner exposes no project market-outcome retrieval surface: the only related call is "
    "technically denied and audited. No canonical bars, candidate outcomes, validation, "
    "or historical-final material was supplied to this session. All selected source "
    "articles predate 2024-01-01, so Protocol v1.0 section 4 requires no protected-window "
    "source-example audit."
)

# The first two records establish the bounded free-public inventory. The remaining
# six records are the selected Failure Test semantic bundle.
INVENTORY = [
    {
        "material_id": "GR-INV-01",
        "title": "Marketlifetrading.com and the free trading course",
        "url": "https://www.adamhgrimes.com/marketlife-free-trading-course/",
        "publication_date": "2017-09-06",
        "role": "author-original course migration/provenance anchor",
        "screen_result": "FREE_PUBLIC_AUTHOR_POST; course content itself is not treated as unauthenticated because the author says registration is required",
    },
    {
        "material_id": "GR-INV-02",
        "title": "The Completely New and Revised Trading Course is Nearing Completion",
        "url": "https://www.adamhgrimes.com/completely-new-revised-trading-course-nearing-completion/",
        "publication_date": "2018-02-20",
        "role": "author-original access-status anchor",
        "screen_result": "AUTHOR STATES COURSE IS FREE BUT REGISTRATION_REQUIRED; excluded under this package's FREE_PUBLIC_UNAUTHENTICATED lock",
    },
    {
        "material_id": "GR-FT-01",
        "title": "Fundamental Trading Patterns",
        "url": "https://www.adamhgrimes.com/fundamental-trading-patterns/",
        "publication_date": "2014-01-10",
        "role": "family screen: Failure Test is a price-structure counter-trend pattern",
    },
    {
        "material_id": "GR-FT-02",
        "title": "Trading Pattern: the Failure Test",
        "url": "https://www.adamhgrimes.com/trading-pattern-the-failure-test/",
        "publication_date": "2012-07-24",
        "role": "primary source: setup, both directions, close entry and initial stop",
    },
    {
        "material_id": "GR-FT-03",
        "title": "The Failure Test",
        "url": "https://www.adamhgrimes.com/failure-test-2/",
        "publication_date": "2014-11-11",
        "role": "primary restatement: context, risk and failed-pattern visibility",
    },
    {
        "material_id": "GR-FT-04",
        "title": "Chart of the Day: Managing the Failure Test in AAPL",
        "url": "https://www.adamhgrimes.com/chart-of-the-day-managing-the-failure-test-in-aapl/",
        "publication_date": "2012-12-18",
        "role": "management example: partial profit at 1R and discretionary trailing",
    },
    {
        "material_id": "GR-FT-05",
        "title": "Current Technical Situation: S&P 500",
        "url": "https://www.adamhgrimes.com/current-technical-situation-sp-500/",
        "publication_date": "2011-10-18",
        "role": "management example: 1R partial exit then trailing remainder",
    },
    {
        "material_id": "GR-FT-06",
        "title": "Reader question: How to handle exits?",
        "url": "https://www.adamhgrimes.com/reader-question-handle-exits/",
        "publication_date": "2016-08-11",
        "role": "negative semantic evidence: author explicitly declines one universal management answer",
    },
]

SELECTED_MATERIAL_IDS = {"GR-FT-01", "GR-FT-02", "GR-FT-03", "GR-FT-04", "GR-FT-05", "GR-FT-06"}

# Every record keeps the three layers separate.  UNKNOWN records document an
# absence in the complete selected bundle, never a project-made trading rule.
CLAIMS = [
    {
        "claim_id": "C-GR-FT-001", "semantic_field": "FAMILY_DEFINITION", "semantic_classification": "PINNED_SOURCE_EXPLICIT", "claim_status": "EXPLICIT", "claim_category": "OBSERVED_CUE", "material_id": "GR-FT-02", "anchor": "GR-FT-02:entry-definition", "paraphrase": "A failure test probes beyond support or resistance and promptly reverses back through that level.", "context": "Price-structure pattern, not an indicator rule.", "observability": "OBSERVABLE_NOW", "missing": "None for raw OHLC price extremes; reference-level selection remains separately unresolved.",
    },
    {
        "claim_id": "C-GR-FT-002", "semantic_field": "REFERENCE_LEVEL_SEMANTICS", "semantic_classification": "UNKNOWN_SOURCE_SEMANTIC", "claim_status": "UNKNOWN", "claim_category": "MARKET_CONTEXT", "material_id": "GR-FT-02", "anchor": "GR-FT-02:entry-definition", "paraphrase": "The source names resistance, support and prior pivots but does not define a deterministic construction or significance test.", "context": "The source presents a chart-reading concept rather than a unique level algorithm.", "observability": "PARTIALLY_OBSERVABLE", "missing": "A source-pinned rule for forming/selecting the reference level from 1-minute OHLCV.",
    },
    {
        "claim_id": "C-GR-FT-003", "semantic_field": "REVERSAL_TIMING_WINDOW", "semantic_classification": "UNKNOWN_SOURCE_SEMANTIC", "claim_status": "UNKNOWN", "claim_category": "CONFIRMATION", "material_id": "GR-FT-03", "anchor": "GR-FT-03:pattern-description", "paraphrase": "The author uses 'immediately' and 'quickly reverses' without fixing a bar count, clock duration, or equivalent boundary.", "context": "No threshold or proxy is introduced by the project.", "observability": "PARTIALLY_OBSERVABLE", "missing": "A source-pinned timing window for the failed probe.",
    },
    {
        "claim_id": "C-GR-FT-004", "semantic_field": "ENTRY_LONG_SHORT", "semantic_classification": "PINNED_SOURCE_EXPLICIT", "claim_status": "EXPLICIT", "claim_category": "ACTION_PERMISSION", "material_id": "GR-FT-02", "anchor": "GR-FT-02:entry-rule", "paraphrase": "After an upside probe fails back below resistance, enter short on the bar close; reverse the construction for a downside support test.", "context": "Both directions are explicitly described.", "observability": "OBSERVABLE_NOW", "missing": "Order execution details are separate machine conventions.",
    },
    {
        "claim_id": "C-GR-FT-005", "semantic_field": "INITIAL_STOP", "semantic_classification": "PINNED_SOURCE_EXPLICIT", "claim_status": "EXPLICIT", "claim_category": "INVALIDATION", "material_id": "GR-FT-02", "anchor": "GR-FT-02:entry-rule", "paraphrase": "The protective stop goes at or just beyond the new extreme of the failed movement.", "context": "This pins the risk-point concept; a one-tick offset/order subtype is not source stated.", "observability": "OBSERVABLE_NOW", "missing": "Tick offset and stop order mechanics are MACHINE_DETAIL_OPEN, not source semantics.",
    },
    {
        "claim_id": "C-GR-FT-006", "semantic_field": "RISK_CONTEXT", "semantic_classification": "PINNED_SOURCE_EXPLICIT", "claim_status": "EXPLICIT", "claim_category": "RISK_PROCESS", "material_id": "GR-FT-03", "anchor": "GR-FT-03:risk-management", "paraphrase": "Range and counter-trend uses can gap adversely; the author advises smaller risk and action after an adverse opening.", "context": "This is risk guidance, not a deterministic sizing or gap-handling algorithm.", "observability": "PARTIALLY_OBSERVABLE", "missing": "Gap policy/sizing formula and China-futures session transfer.",
    },
    {
        "claim_id": "C-GR-FT-007", "semantic_field": "FIRST_PROFIT_ACTION", "semantic_classification": "PINNED_SOURCE_EXPLICIT", "claim_status": "EXPLICIT", "claim_category": "MANAGEMENT", "material_id": "GR-FT-05", "anchor": "GR-FT-05:trade-management", "paraphrase": "In the illustrated management plan, take 25% to 50% profit when open profit equals initial risk (1R).", "context": "The source explicitly permits a range, so it does not select one unique PRIMARY fraction.", "observability": "OBSERVABLE_NOW", "missing": "A source-justified unique partial-exit fraction.",
    },
    {
        "claim_id": "C-GR-FT-008", "semantic_field": "POST_ENTRY_INVALIDATION", "semantic_classification": "UNKNOWN_SOURCE_SEMANTIC", "claim_status": "UNKNOWN", "claim_category": "INVALIDATION", "material_id": "GR-FT-06", "anchor": "GR-FT-06:management-answer", "paraphrase": "The author says there is no single answer for discretionary trade management and that decisions depend on the trader.", "context": "This rules out treating a blog-level management discussion as a complete deterministic post-entry rule.", "observability": "UNKNOWN", "missing": "A unique stop-movement/invalidation rule for the remaining position.",
    },
    {
        "claim_id": "C-GR-FT-009", "semantic_field": "REMAINDER_EXIT", "semantic_classification": "UNKNOWN_SOURCE_SEMANTIC", "claim_status": "UNKNOWN", "claim_category": "EXIT", "material_id": "GR-FT-04", "anchor": "GR-FT-04:management-example", "paraphrase": "The example says to tighten and trail the stop after partial profit, but it gives no deterministic trailing method or final exit trigger.", "context": "A trailing stop label alone is not a machine rule.", "observability": "UNKNOWN", "missing": "Trailing reference, activation, update cadence and full-exit condition.",
    },
    {
        "claim_id": "C-GR-FT-010", "semantic_field": "TIME_EXIT", "semantic_classification": "UNKNOWN_SOURCE_SEMANTIC", "claim_status": "UNKNOWN", "claim_category": "EXIT", "material_id": "GR-FT-06", "anchor": "GR-FT-06:management-answer", "paraphrase": "No selected free-public material fixes a holding duration, session close rule, or time-based exit for the family.", "context": "No substitute time rule is invented.", "observability": "NOT_APPLICABLE", "missing": "Source semantic for a time exit.",
    },
    {
        "claim_id": "C-GR-FT-011", "semantic_field": "FAILURE_AND_NO_TRADE", "semantic_classification": "PINNED_SOURCE_INFERRED", "claim_status": "INFERRED", "claim_category": "FAILURE_OR_COUNTEREXAMPLE", "material_id": "GR-FT-03", "anchor": "GR-FT-03:risk-management", "paraphrase": "The source explicitly discusses losing patterns, gap-and-go continuation, and the need for a planned stop; project interpretation preserves these as failure visibility rather than a no-trade filter.", "context": "There is no explicit deterministic no-trade checklist.", "observability": "PARTIALLY_OBSERVABLE", "missing": "A source-pinned no-trade filter.",
    },
    {
        "claim_id": "C-GR-FT-012", "semantic_field": "TIMEFRAME_AND_INSTRUMENT_SCOPE", "semantic_classification": "UNKNOWN_SOURCE_SEMANTIC", "claim_status": "EXPLICIT", "claim_category": "APPLICABILITY", "material_id": "GR-FT-03", "anchor": "GR-FT-03:scope", "paraphrase": "The author says the pattern can be used across timeframes, but the selected examples do not define a 1-minute base interval or Chinese-futures session scope.", "context": "Broad source language does not become an explicit cu/al/ni/au/ag/rb authorization.", "observability": "PARTIALLY_OBSERVABLE", "missing": "Source-pinned 1-minute timeframe and project Chinese-futures transfer.",
    },
    {
        "claim_id": "C-GR-FT-013", "semantic_field": "CHINESE_FUTURES_TRANSFER", "semantic_classification": "PINNED_SOURCE_INFERRED", "claim_status": "INFERRED", "claim_category": "APPLICABILITY", "material_id": "GR-FT-03", "anchor": "GR-FT-03:scope", "paraphrase": "Any transfer to the project’s six Chinese futures products would be a project inference, not a source claim.", "context": "Transfer is deliberately not attempted because the source loop is already insufficient.", "observability": "UNKNOWN", "missing": "Project-specific transfer authority and complete source semantics.",
    },
]


def fetch_material(material: dict[str, str]) -> tuple[ApprovedSourceMaterialRef, dict[str, object]]:
    request = Request(material["url"], headers={"User-Agent": "KlinePlaybookResearch/0.1 (+source-only)"})
    with urlopen(request, timeout=30) as response:
        content = response.read()
        status = response.status
    if status != 200 or not content:
        raise RuntimeError(f"source fetch failed for {material['material_id']}: HTTP {status}")
    reference = ApprovedSourceMaterialRef.from_bytes(
        source_id=SOURCE_ID,
        material_id=material["material_id"],
        source_anchor_reference=material["material_id"],
        content=content,
    )
    record = dict(material)
    record.update(
        {
            "provenance": "TRACEABLE_ORIGINAL",
            "access": "FREE_PUBLIC_UNAUTHENTICATED",
            "effective_content_date_before_2024_01_01": True,
            "http_status": status,
            "byte_binding_status": reference.byte_binding_status.value,
            "fetched_content_sha256": reference.fetched_content_sha256,
            "fetched_byte_size": reference.fetched_byte_size,
        }
    )
    return reference, record


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    fetched = [fetch_material(material) for material in INVENTORY]
    refs = [reference for reference, _ in fetched if reference.material_id in SELECTED_MATERIAL_IDS]
    records = [record for _, record in fetched]
    bundle = ApprovedSourceBundle(
        source_bundle_id=BUNDLE_ID,
        source_bundle_hash="SOURCE_BYTES_BOUND_AT_RUN_TIME",
        source_anchor_reference=f"{BUNDLE_ID}: author-original free-public blog material",
        materials=tuple(refs),
        content_note=RETENTION_BOUNDARY,
    )

    manifest = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_BUNDLE_GRIMES_FAILURE_TEST_SEMANTIC",
        "manifest_version": "1.0",
        "bundle_id": BUNDLE_ID,
        "source": SOURCE_ID,
        "package": PROMPT_SPEC_VERSION,
        "selected_family": "GRIMES_FAILURE_TEST_FAILED_BREAKOUT_REVERSAL",
        "selected_on": "2026-08-21",
        "selection_basis": "SOURCE_SEMANTIC_COMPLETENESS_AND_CURRENT_OHLCV_COMPATIBILITY_ONLY; NEVER_CANDIDATE_OUTCOM",
        "retrieval_mode": RETRIEVAL_MODE,
        "bundle_identity": bundle.bundle_identity,
        "session_binding_identity": bundle.session_binding_identity,
        "session_binding_hash": bundle.session_binding_hash,
        "byte_binding_status": bundle.byte_binding_status.value,
        "inventory": records,
        "selected_material_ids": sorted(SELECTED_MATERIAL_IDS),
        "stopping_condition": {
            "author_original_blog_material": "REVIEWED",
            "official_marketlife_public_surface": "REVIEWED_ONLY_AS_ACCESS/COMMERCIAL_CONTEXT; no paid course content used",
            "explicitly_referenced_original_public_material": "NOT_NEEDED_AFTER_SELECTED_BUNDLE_COVERED_SETUP_ENTRY_STOP_MANAGEMENT_AND_EXIT_GAP",
            "result": "MET_STOP_BOUNDED_SEARCH",
        },
        "excluded_surfaces": [
            "MarketLife course lessons: author states registration is required; excluded by FREE_PUBLIC_UNAUTHENTICATED_ONLY.",
            "MarketLife pullback masterclass: public sales page advertises a paid $1997 product; not purchased or used.",
            "Books, subscriptions, courses, accounts, and authenticated material: not purchased, logged into, or bypassed.",
        ],
        "raw_material_retention_boundary": RETENTION_BOUNDARY,
    }
    write_json(REPO_ROOT / "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_GRIMES_FAILURE_TEST_SEMANTIC_V0_1.json", manifest)

    policy = SourceOnlyPolicy()
    session = policy.open_verified_session(
        session_id=SESSION_ID,
        model_identity=MODEL_IDENTITY,
        prompt_spec_version=PROMPT_SPEC_VERSION,
        source_bundle_identity=bundle.session_binding_identity,
        source_bundle_hash=bundle.session_binding_hash,
        tool_retrieval_mode=RETRIEVAL_MODE,
        researcher_model_exposure_note=EXPOSURE_NOTE,
    )
    runner = SourceOnlyClaimExtractionContext(
        source_bundle=bundle,
        source_only=policy,
        session_id=session.session_id,
        output_surface=ClaimRecordOutput(),
    )
    if not runner.verified:
        raise RuntimeError("SOURCE_ONLY session is not verified")
    denial = runner.request_protected_market_outcome("ENGINEERING_PROOF_ONLY_NO_RETRIEVAL")
    if denial.outcome != "DENIED" or denial.reason != "SOURCE_ONLY_TECHNICAL_DENIAL":
        raise RuntimeError("protected market outcome was not denied")

    for claim in CLAIMS:
        runner.record_claim(
            ClaimRecordDraft(
                claim_id=claim["claim_id"], source_id=SOURCE_ID, material_id=claim["material_id"],
                source_anchor=claim["anchor"], claim_status=claim["claim_status"],
                source_excerpt_short_or_paraphrase=claim["paraphrase"],
                source_only_session_id=session.session_id, created_at=CREATED_AT,
            )
        )

    session_record = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_GRIMES_FAILURE_TEST_SEMANTIC",
        "session": {
            "session_id": session.session_id, "session_identity": session.session_identity,
            "model_identity": session.model_identity, "prompt_spec_version": session.prompt_spec_version,
            "source_bundle_identity": session.source_bundle_identity, "source_bundle_hash": session.source_bundle_hash,
            "tool_retrieval_mode": session.tool_retrieval_mode,
            "protected_market_access_mode": session.protected_market_access_mode.value,
            "verification_evidence": session.verification_evidence,
        },
        "is_verified": True,
        "technical_denial": {"outcome": denial.outcome, "reason": denial.reason, "run_once": True},
        "exposure_note": EXPOSURE_NOTE,
        "claim_status_semantics": "EXPLICIT=source stated; INFERRED=project interpretation; UNKNOWN=source does not pin the field.",
        "recorded_claim_count": len(CLAIMS),
        "claims": CLAIMS,
        "final_decision": {
            "PLAYBOOK_SEMANTICALLY_DRAFTABLE": "NO",
            "machine_ready": "NO",
            "reason": "Entry and initial-stop concepts are explicit, but reference-level construction, reversal timing, post-entry invalidation, remainder exit and time exit are not source-pinned.",
            "no_candidate_outcome_used": "YES",
        },
    }
    write_json(REPO_ROOT / "docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_GRIMES_FAILURE_TEST_SEMANTIC_V0_1.json", session_record)
    print("SOURCE_ONLY_VERIFIED=True")
    print(f"DENIAL_REASON={denial.reason}")
    print(f"CLAIMS={len(CLAIMS)}")
    print(f"BUNDLE_IDENTITY={bundle.bundle_identity}")


if __name__ == "__main__":
    main()
