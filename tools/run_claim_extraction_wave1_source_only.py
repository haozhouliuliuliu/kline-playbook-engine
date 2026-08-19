"""REAL_CLAIM_EXTRACTION_WAVE1_PUBLIC_V1 — SOURCE_ONLY driver.

This tool performs the first REAL source-faithful claim-extraction wave using the
actual project SOURCE_ONLY implementation in `src/research_firewall.py`:

- predeclares the approved public source bundle (Adam Grimes / MarketLife free
  public pages) and computes its canonical bundle hash;
- opens a project-verified SOURCE_ONLY session via
  `SourceOnlyPolicy.open_verified_session(...)`;
- verifies `source_only.is_verified(session_id) == True`;
- executes the protected-outcome denial path once (engineering proof) and
  expects `outcome=DENIED` / `reason=SOURCE_ONLY_TECHNICAL_DENIAL`;
- records every claim through the bounded `SourceOnlyClaimExtractionContext`
  provenance output surface;
- writes durable JSON evidence artifacts:
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_1_MANIFEST.json
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1.json

HARD BOUNDARIES (frozen authority, do not violate):
- No candidate outcome / PnL / backtest / indicator search / chart-pattern mining.
- No project protected-period market-outcome retrieval (the runner has no such
  surface; any request is technically DENIED and audited).
- No canonical market data repository, validation, or historical-final access.
- Source claim != project/AI interpretation != machine operationalization.
- No invented thresholds; no fabricated OHLCV proxies for absent inputs.
- No purchase/subscription/authentication; free public original pages only.

All source materials have effective content dates BEFORE 2024-01-01 (before the
frozen corpus start), so under Protocol v1.0 section 4 no source-example date
audit is required for the protected windows.

Run:
    python -m tools.run_claim_extraction_wave1_source_only
"""

from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path

from src.research_firewall import (
    ApprovedSourceBundle,
    ClaimRecordDraft,
    ClaimRecordOutput,
    SourceOnlyClaimExtractionContext,
)
from src.strategy_evidence import EvidenceLedger

REPO_ROOT = Path(__file__).resolve().parents[1]

# ---------------------------------------------------------------------------
# Identity constants
# ---------------------------------------------------------------------------

SESSION_ID = "SOURCE_ONLY_WAVE1_PUBLIC_V1_20260819"
MODEL_IDENTITY = "deepseek-v4-flash"
PROMPT_SPEC_VERSION = "REAL_CLAIM_EXTRACTION_WAVE1_PUBLIC_V1"
RETRIEVAL_MODE = "LOCAL_FREE_PUBLIC_ORIGINAL_SOURCE_BUNDLE_ONLY"
BUNDLE_ID = "SB-W1-PUBLIC-GRIMES-V1"
BUNDLE_NAME = "Real Claim Extraction Wave 1 - Public Adam Grimes free public source bundle"
CREATED_AT = "2026-08-19T00:00:00Z"

EXPOSURE_NOTE = (
    "Model latent historical knowledge cannot be proven absent; this is a disclosed "
    "residual threat-model risk under the frozen protocol. No project protected-period "
    "market-outcome retrieval was available through the SOURCE_ONLY runner; the runner "
    "technically denies any such request and audits it. No canonical market data "
    "repository, validation surface, or historical-final surface was exposed to this "
    "session. All selected source materials have effective content dates before "
    "2024-01-01 (before the frozen corpus start), so no source-example date audit is "
    "required for the protected windows under Protocol v1.0 section 4."
)

RETENTION_BOUNDARY = (
    "Raw HTML of the source pages was not retained. Only attributable short excerpts "
    "and concise paraphrases needed for claim traceability are recorded. Full "
    "copyrighted articles/courses are not stored. Anchors point to the canonical "
    "public URLs."
)


def _canonical_hash(value: object) -> str:
    """Same canonical JSON+sha256 scheme used by src.research_firewall."""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Source bundle definition (materials only; no redistributed copyrighted content)
# ---------------------------------------------------------------------------

MATERIALS = [
    {
        "material_id": "SB-W1-M1",
        "canonical_title": "How I Trade (Part 1 of 2)",
        "author": "Adam H. Grimes",
        "publisher_channel": "The Blog of Adam H Grimes (adamhgrimes.com)",
        "content_type": "official blog post (trading process / market-reading method)",
        "language": "EN",
        "url": "https://www.adamhgrimes.com/how-i-trade-part-1-of-2/",
        "date": "2023-10-31",
        "effective_content_date": "2023-10-31",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "market context / observed cue / review process",
        "content_note": (
            "Sections: Discretionary vs Systematic; Fundamental and Macro; Technicals; "
            "Importance of doing your own work; Can the whole be more than the sum of the "
            "parts? Includes: macro/fundamental signals are not timing signals; pattern "
            "occurrence identification via discretion vs rule set; '100% reliable' pattern "
            "claims impossible; context must be quantified; baseline-relative edge analysis."
        ),
    },
    {
        "material_id": "SB-W1-M2",
        "canonical_title": "Reader question: what's wrong with Fibonacci?",
        "author": "Adam H. Grimes",
        "publisher_channel": "The Blog of Adam H Grimes (adamhgrimes.com)",
        "content_type": "official blog post (methodological critique / counterexample)",
        "language": "EN",
        "url": "https://www.adamhgrimes.com/whats-wrong-fibonacci/",
        "date": "2016-03-23",
        "effective_content_date": "2016-03-23",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "limitation / failure / counterexample",
        "content_note": (
            "Reply to a reader question. Covers: inability to predict which Fibonacci "
            "level will hold; confluence as possible luck; random-data perception study; "
            "price-memory reliance on chart adjustment; absence of quantitative proof for "
            "Fibonacci; data-supported replacement of ~50% retracement of prior swing with "
            "a very large margin of error."
        ),
    },
    {
        "material_id": "SB-W1-M3",
        "canonical_title": "Marketlifetrading.com and the free trading course",
        "author": "Adam H. Grimes",
        "publisher_channel": "The Blog of Adam H Grimes (adamhgrimes.com)",
        "content_type": "official blog post (education approach / risk / process)",
        "language": "EN",
        "url": "https://www.adamhgrimes.com/marketlife-free-trading-course/",
        "date": "2017-09-06",
        "effective_content_date": "2017-09-06",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "action/no-trade / applicability / risk-process",
        "content_note": (
            "Announcement/relaunch of the free trading course. Covers: trading is not a "
            "get-rich-quick scheme; cannot learn to trade with a few candlestick patterns; "
            "becoming a trader requires changing how you think and handle risk; the "
            "author's acknowledged process mistake of making everything free (not "
            "sustainable); commitment to free public material plus paid tiers."
        ),
    },
]

SELECTION_CRITERIA = [
    "original / nearest-original provenance (author's own official blog)",
    "stable attributable URL and title",
    "substantive trading / process / market-observation content",
    "useful context on applicability, limitation, invalidation or failure where available",
    "not selected by expected historical performance",
]

OPTIONAL_PAID_CANDIDATES = [
    {
        "source_identity": "Adam Grimes / MarketLife paid education platform "
        "(marketlifetrading.com subscriptions, premium courses, daily market insight)",
        "why_it_might_matter": "Deeper long-form course material and live market context "
        "could later clarify context factors, full trading-loop examples and invalidation "
        "examples at scale.",
        "evidence_gap_it_could_fill": "More systematic failure/invalidation examples and "
        "defined context factors for pattern claims.",
        "access_class": "PAID_SUBSCRIPTION (not purchased; listed for awareness only)",
    },
    {
        "source_identity": "Adam Grimes, The Art and Science of Technical Analysis (book)",
        "why_it_might_matter": "Book-length synthesis of the discretionary + quantitative "
        "method the free blog material is based on.",
        "evidence_gap_it_could_fill": "Structured definitions of market-structure and "
        "momentum concepts that may be referenced implicitly in free material.",
        "access_class": "PAID_BOOK (not purchased; listed for awareness only)",
    },
]

# ---------------------------------------------------------------------------
# Claim records (full Claim Schema v1.0 structural subset)
# ---------------------------------------------------------------------------

CLAIMS = [
    {
        "claim_id": "C-W1-001",
        "material_id": "SB-W1-M1",
        "source_anchor": "SB-W1-M1:how-i-trade-part-1-of-2:section:FUNDAMENTAL_AND_MACRO",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Fundamental and macro factors matter, but they are not timing signals. ... "
            "there's a tremendous amount of variability in the signals. There's enough "
            "variability that we should often ignore the week-to-week or even "
            "month-to-month numbers. (Of course, it's important to know when this is not "
            "true.)"
        ),
        "source_context_note": (
            "Section 'Fundamental and Macro'. Grimes: fundamental and macro factors matter "
            "but are not timing signals; the data is volatile; week-to-week or "
            "month-to-month numbers should often be ignored (with an explicit but "
            "undefined exception). Public commentary is misaligned with the trader's "
            "interests."
        ),
        "claim_category": "SOURCE_INTERPRETATION",
        "source_timeframe_or_horizon_if_explicit": "week-to-week / month-to-month (as a "
        "reading cadence, stated by source)",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": (
            "'it's important to know when this is not true' (source states exceptions exist "
            "but does not define them)."
        ),
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'signals that work' is not enumerated; source does not specify which macro "
            "factors, how to measure timing implications, or when the reading-cadence "
            "exception applies."
        ),
        "observability_compatibility": "NOT_OBSERVABLE_WITH_CURRENT_DATA",
        "observability_missing_inputs": (
            "Fundamental/macro data series are absent from the project's 1-minute OHLCV "
            "canonical corpus; no faithful OHLCV proxy exists."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-002",
        "material_id": "SB-W1-M1",
        "source_anchor": "SB-W1-M1:how-i-trade-part-1-of-2:section:IMPORTANCE_OF_DOING_YOUR_OWN_WORK",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "either we can go through charts and mark the patterns based on discretion, or "
            "we can do it with a rule set and probably let a computer mark them. The first "
            "of those choices is subject to a massive amount of error and influence from "
            "the researcher."
        ),
        "source_context_note": (
            "Section 'Importance of doing your own work'. Describes two approaches to "
            "identifying pattern occurrences when answering 'what has happened when this "
            "pattern has occurred in the past?'."
        ),
        "claim_category": "REVIEW_PROCESS",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": "UNKNOWN",
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Methodological claim; no market-data input required.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-003",
        "material_id": "SB-W1-M1",
        "source_anchor": "SB-W1-M1:how-i-trade-part-1-of-2:section:IMPORTANCE_OF_DOING_YOUR_OWN_WORK",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Even some of the best-known 'encyclopedias' of technical patterns show "
            "patterns that have never failed, that are 100% reliable. This, of course, is "
            "impossible - markets do not work like that. ... work done like this is "
            "potentially highly misleading."
        ),
        "source_context_note": (
            "Same section. Claims of perfect reliability imply discretionary selection of "
            "'valid' patterns, which the source flags as misleading for developing traders."
        ),
        "claim_category": "FAILURE_OR_COUNTEREXAMPLE",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": (
            "Counterexample to pattern encyclopedias that claim 100% reliability."
        ),
        "ambiguity_notes": "UNKNOWN",
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Methodological/counterexample claim.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-004",
        "material_id": "SB-W1-M1",
        "source_anchor": "SB-W1-M1:how-i-trade-part-1-of-2:section:IMPORTANCE_OF_DOING_YOUR_OWN_WORK",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Some patterns may depend on complex factors such as time of day, action (or "
            "volatility) in related markets, and other aspects of context. ... some patterns "
            "can't be explained in a simple rule set."
        ),
        "source_context_note": (
            "Same section. Acknowledges that some patterns are context-dependent and "
            "resist simple quantification while still being real to a discretionary trader."
        ),
        "claim_category": "APPLICABILITY",
        "source_timeframe_or_horizon_if_explicit": "time of day (stated as an example factor)",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": (
            "Applicability boundary: simple rule sets may fail for context-dependent "
            "patterns; quantification may not catch everything."
        ),
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "The specific 'other aspects of context' are not enumerated by the source."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "Time-of-day is derivable from 1-minute OHLCV; related-market action/volatility "
            "is only partially observable with the current single-market corpus and the "
            "other context factors are unspecified."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-005",
        "material_id": "SB-W1-M1",
        "source_anchor": "SB-W1-M1:how-i-trade-part-1-of-2:section:IMPORTANCE_OF_DOING_YOUR_OWN_WORK",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "you need to compare to a baseline drawn from the asset itself. Your comparison "
            "is not zero. ... if you have an active trading system that is long-only stocks "
            "and ... returns about 6% a year over a long slice of data. Great, but the buy "
            "and hold return might have been 7% or 8%. Does your approach even have an edge? "
            "(Probably not.)"
        ),
        "source_context_note": (
            "Same section. Illustrative numbers (6% / 7-8%) are the source's example, not "
            "project evidence. The claim is the methodological requirement to benchmark "
            "against the asset baseline, not zero."
        ),
        "claim_category": "REVIEW_PROCESS",
        "source_timeframe_or_horizon_if_explicit": "long slice of data (source wording)",
        "source_market_or_instrument_if_explicit": "stocks (example only)",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": (
            "Implied: do not actively trade an approach that does not beat the asset "
            "baseline after risk considerations."
        ),
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "Illustrative numbers must not be read as project findings or as thresholds."
        ),
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Methodological claim (benchmarking practice).",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-006",
        "material_id": "SB-W1-M1",
        "source_anchor": "SB-W1-M1:how-i-trade-part-1-of-2:section:CAN_THE_WHOLE_BE_MORE_THAN_THE_SUM_OF_THE_PARTS",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Technical traders are guilty of saying 'context' and dismissing everything ... "
            "'You have to put it in context, of course. Of course a statistical test will "
            "show it doesn't work, because you must have context.' If this is true, "
            "quantifying aspects of this context isn't just crucial - it's non-negotiable. "
            "... 'context' can be the refuge of a trader that doesn't want to do the work to "
            "quantify an edge."
        ),
        "source_context_note": (
            "Section 'Can the whole be more than the sum of the parts?'. Source argues "
            "context must be quantified rather than used to dismiss statistical results."
        ),
        "claim_category": "REVIEW_PROCESS",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "The source does not define which context factors to quantify; that remains an "
            "open interpretation/operationalization question."
        ),
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Methodological claim (quantification discipline).",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-007",
        "material_id": "SB-W1-M2",
        "source_anchor": "SB-W1-M2:whats-wrong-fibonacci:bullet:WHICH_LEVEL_WILL_HOLD",
        "source_anchor_type": "blog_post_bullet",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "You couldn't be sure which level would work, but some level always worked after "
            "the fact. I began to realize that levels would be violated in live trades; I "
            "had dutifully placed my stop a few ticks beyond, but then another level clearly "
            "held at the end of the day. There was no way, and no way in the literature, to "
            "predict which level would hold. ... we were drawing so many levels on charts "
            "that it might just be luck that they seemed to work."
        ),
        "source_context_note": (
            "One of the author's bullets explaining why he abandoned Fibonacci levels. "
            "Combines live-trade observation with a confluence critique."
        ),
        "claim_category": "FAILURE_OR_COUNTEREXAMPLE",
        "source_timeframe_or_horizon_if_explicit": "intraday ('at the end of the day') as "
        "the example context",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": (
            "Levels being violated in live trades and the inability to predict which level "
            "holds are stated as the invalidation of using such levels for stops."
        ),
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": (
            "Example: stops placed a few ticks beyond a level were violated; another level "
            "held instead."
        ),
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "The exact 'levels' and how they were drawn are trader-discretionary and not "
            "defined; confluence is described qualitatively."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "OHLCV is observable, but the specific discretionary levels and their "
            "confluence are not defined by the source, so a faithful representation is not "
            "determined."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-008",
        "material_id": "SB-W1-M2",
        "source_anchor": "SB-W1-M2:whats-wrong-fibonacci:bullet:NO_QUANTITATIVE_PROOF",
        "source_anchor_type": "blog_post_bullet",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "No one will ever provide you with a quantitative proof of Fibonacci levels "
            "working. ... I have yet to receive a single shred of actual work done on these "
            "ratios. ... I place no emphasis at all on Fibonacci levels. Here's the real "
            "key: you do not need them."
        ),
        "source_context_note": (
            "Concluding bullets and closing statement. The source reports absence of "
            "quantitative support and states he does not use Fibonacci levels in his "
            "trading in any capacity."
        ),
        "claim_category": "NON_APPLICABILITY",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": (
            "Non-applicability for the source's own trading process; the claim that 'you do "
            "not need them' is a stated stance."
        ),
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": (
            "Absence of quantitative proof is treated as the counterevidence to Fibonacci "
            "usage."
        ),
        "ambiguity_notes": (
            "'No quantitative proof' is the source's report of his search; absence of "
            "evidence is not proof of absence, which the source himself acknowledges as a "
            "possibility ('It's possible my thinking on this subject is wrong')."
        ),
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Methodological/non-use stance claim.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-009",
        "material_id": "SB-W1-M2",
        "source_anchor": "SB-W1-M2:whats-wrong-fibonacci:closing:RETRACEMENT_REPLACEMENT",
        "source_anchor_type": "blog_post_closing",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "No, this is not, nor is it intended to be, a disproof of the theory, but it "
            "does offer a simple replacement that is supported by the data: look for "
            "retracements to end at about 50% of the previous swing, with a very large "
            "margin of error. We might wish for more precision, but that is all I have been "
            "able to find in the data. Good news, though: it's enough."
        ),
        "source_context_note": (
            "Closing paragraph referencing the author's quantitative posts on Fibonacci. "
            "'about 50% with a very large margin of error' is the source's own qualitative "
            "description and must not be sharpened into a precise threshold."
        ),
        "claim_category": "OBSERVED_CUE",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": (
            "Stated as a simple data-supported replacement for Fibonacci retracement levels."
        ),
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'About 50%' and 'very large margin of error' are intentionally imprecise; the "
            "swing definition and measurement method are not specified by the source."
        ),
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": (
            "Retracement depth relative to a prior swing is representable from 1-minute "
            "OHLCV. Swing definition is an interpretation/operationalization decision, not "
            "an observability gap."
        ),
        "primary_branch_status": "PRELIMINARY_SOURCE_JUSTIFIED_PRIMARY_CANDIDATE",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W1-010",
        "material_id": "SB-W1-M2",
        "source_anchor": "SB-W1-M2:whats-wrong-fibonacci:bullet:RANDOM_DATA_PERCEPTION",
        "source_anchor_type": "blog_post_bullet",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "I generated many charts of random market data according to various techniques "
            "and spent a lot of time looking at them. ... when you see how easily your "
            "perception is swayed and how easily you find patterns in random data, you start "
            "to think deeply. Does it invalidate the idea of patterns in real market data? "
            "Of course not, but it certainly challenges the claims of 'just look at a "
            "chart! You can see it works!'"
        ),
        "source_context_note": (
            "Bullet on randomness. The source describes experiential learning about "
            "perception and pattern-finding in random data."
        ),
        "claim_category": "FAILURE_OR_COUNTEREXAMPLE",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": (
            "Challenges visual 'just look at a chart' evidence claims, without invalidating "
            "patterns in real data."
        ),
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": "UNKNOWN",
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Methodological/cognitive-bias claim.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-011",
        "material_id": "SB-W1-M2",
        "source_anchor": "SB-W1-M2:whats-wrong-fibonacci:bullet:PRICE_MEMORY_ADJUSTMENT",
        "source_anchor_type": "blog_post_bullet",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Much of the discipline of technical analysis rests on the idea that people "
            "have a memory around specific prices. ... there are different ways that "
            "historical charts must be adjusted. With futures, there are at least three "
            "common methods (difference, ratio, or unadjusted), and the question of when to "
            "roll to new contracts. ... The answer I got from asking many people was either "
            "confusion or 'it doesn't matter.'"
        ),
        "source_context_note": (
            "Bullet on adjusted price charts. Flags chart-adjustment and roll decisions as "
            "material to any 'price memory' / level approach."
        ),
        "claim_category": "RISK_PROCESS",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "futures and stocks (examples)",
        "source_applicability_if_explicit": (
            "Applies to any approach relying on remembered price levels or chart "
            "structures across adjusted historical data."
        ),
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": "UNKNOWN",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "The project corpus adjustment method/roll semantics determine whether "
            "'price-memory' levels are faithfully preserved; adjustment metadata is only "
            "partially documented (see LIMIT-001 class of limitations)."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-012",
        "material_id": "SB-W1-M3",
        "source_anchor": "SB-W1-M3:marketlife-free-trading-course:body:NOT_GET_RICH_QUICK",
        "source_anchor_type": "blog_post_paragraph",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "of course trading isn't a get rich quick scheme, of course you probably can't "
            "turn your 1,000 into 1,000,000 this year, of course you can't learn to trade "
            "with just a few candlestick patterns. ... before you can change your life, you "
            "have to change the way you think and the way you handle risk. It's not just "
            "about learning some patterns or trading techniques - it's about becoming a "
            "trader and that's a long and difficult path."
        ),
        "source_context_note": (
            "Body paragraph from the free-course relaunch announcement. Positions trading "
            "as a risk/process skill, not pattern memorization."
        ),
        "claim_category": "RISK_PROCESS",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": "UNKNOWN",
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Process/risk statement; no market-data input.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-013",
        "material_id": "SB-W1-M3",
        "source_anchor": "SB-W1-M3:marketlife-free-trading-course:body:ACKNOWLEDGED_PROCESS_MISTAKE",
        "source_anchor_type": "blog_post_paragraph",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "One of the mistakes I made with the old course was making everything free. It "
            "was a labor of love and a fun hobby, but I wasn't able to maintain the "
            "production schedule or the community forum for an unpaid project."
        ),
        "source_context_note": (
            "Body paragraph. An explicit, attributable acknowledgement of a process/"
            "sustainability failure by the source about his own prior offering."
        ),
        "claim_category": "FAILURE_OR_COUNTEREXAMPLE",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": (
            "Source-attributed failure about sustainability of an all-free offering."
        ),
        "ambiguity_notes": "UNKNOWN",
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Business/process claim; no market-data input.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-014",
        "material_id": "SB-W1-M1",
        "source_anchor": "SB-W1-M1:how-i-trade-part-1-of-2:synthesis:IMPORTANCE_OF_DOING_YOUR_OWN_WORK",
        "source_anchor_type": "project_synthesis_across_sections",
        "source_language": "EN",
        "claim_status": "INFERRED",
        "source_excerpt_short_or_paraphrase": (
            "Project/AI synthesis (not a direct source quote): the source's explicit "
            "methodological requirements - systematic occurrence identification, a "
            "consistent assumed entry, baseline-relative outcome analysis, and quantified "
            "context - together imply a coherent pre-adoption validation standard for any "
            "pattern claim."
        ),
        "source_context_note": (
            "Synthesized from the explicit steps in 'Importance of doing your own work' "
            "(find every occurrence, assume a consistent entry, see what happened, analyze, "
            "compare to an asset baseline) and 'Can the whole be more than the sum of the "
            "parts?' (quantify context)."
        ),
        "claim_category": "REVIEW_PROCESS",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "This is project/AI interpretation, clearly labeled INFERRED; it must never be "
            "presented as a direct source statement."
        ),
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Methodological synthesis claim.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W1-015",
        "material_id": "SB-W1-M2",
        "source_anchor": "SB-W1-M2:whats-wrong-fibonacci:synthesis:RETRACEMENT_PREFERENCE",
        "source_anchor_type": "project_synthesis_across_sections",
        "source_language": "EN",
        "claim_status": "INFERRED",
        "source_excerpt_short_or_paraphrase": (
            "Project/AI synthesis (not a direct source quote): the source's explicit "
            "rejection of precise Fibonacci ratios combined with his stated 'about 50% of "
            "the previous swing with a very large margin of error' replacement implies a "
            "preference for simpler, coarser retracement anchors over precise ratio levels."
        ),
        "source_context_note": (
            "Synthesized from the 'you cannot predict which level will hold' bullet, the "
            "'no quantitative proof' bullet, and the closing replacement statement."
        ),
        "claim_category": "SOURCE_INTERPRETATION",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "UNKNOWN",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "This is project/AI interpretation, clearly labeled INFERRED; the source never "
            "explicitly states a preference for 'simpler anchors' in those words."
        ),
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Methodological synthesis claim.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
]

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _material_records() -> list[dict]:
    """Materials enriched with deterministic per-material content-note hashes."""
    records = []
    for material in MATERIALS:
        note_hash = _canonical_hash(
            {
                "material_id": material["material_id"],
                "url": material["url"],
                "title": material["canonical_title"],
                "date": material["date"],
                "content_note": material["content_note"],
            }
        )
        record = dict(material)
        record["content_note_hash"] = note_hash
        records.append(record)
    return records


def _bundle_hash() -> str:
    """Canonical hash over the full source-bundle identity (materials + criteria)."""
    return _canonical_hash(
        {
            "bundle_id": BUNDLE_ID,
            "retrieval_mode": RETRIEVAL_MODE,
            "materials": [
                {k: m[k] for k in ("material_id", "url", "canonical_title", "date")}
                for m in MATERIALS
            ],
            "selection_criteria": SELECTION_CRITERIA,
        }
    )


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    bundle_hash = _bundle_hash()
    material_records = _material_records()

    # ---- B: source bundle manifest (predeclared) --------------------------
    manifest = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_1_MANIFEST",
        "manifest_version": "1.0",
        "bundle_id": BUNDLE_ID,
        "bundle_name": BUNDLE_NAME,
        "canonical_bundle_hash": bundle_hash,
        "selected_on": "2026-08-19",
        "retrieval_mode": RETRIEVAL_MODE,
        "source_admission_reference": (
            "docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md -> "
            "SRC-GRIMES / MAT-GRIMES-MARKETLIFE (KEEP_CANDIDATE) and "
            "docs/research/source_dossiers/SOURCE_DOSSIER_GRIMES_V0_1.md"
        ),
        "selection_criteria": SELECTION_CRITERIA,
        "selection_basis_note": (
            "Selection based on provenance + anchor quality + extraction suitability. "
            "NEVER based on expected trading performance, backtest quality, or ease of "
            "producing a strategy."
        ),
        "source_substitution": {
            "occurred": "NO",
            "note": (
                "SRC-GRIMES free/public bundle was formed successfully from 3 official "
                "Adam Grimes blog pages; no substitution was required."
            ),
        },
        "materials": material_records,
        "raw_material_retention_boundary": RETENTION_BOUNDARY,
        "copyright_boundary": (
            "Store traceability, not a redistribution archive. Only short excerpts and "
            "concise paraphrases are recorded; full copyrighted material is not stored."
        ),
        "optional_paid_candidates": OPTIONAL_PAID_CANDIDATES,
        "paid_candidates_note": (
            "Listed for awareness only. No purchase or subscription is authorized. "
            "PAID_SOURCE_PURCHASE_DEFAULT=NO. Free/public alternatives were sufficient."
        ),
    }
    manifest_path = REPO_ROOT / "docs" / "evidence" / "HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_1_MANIFEST.json"
    _write_json(manifest_path, manifest)

    # ---- Verified SOURCE_ONLY session (actual project implementation) -----
    from src.research_firewall import SourceOnlyPolicy

    policy = SourceOnlyPolicy()
    session = policy.open_verified_session(
        session_id=SESSION_ID,
        model_identity=MODEL_IDENTITY,
        prompt_spec_version=PROMPT_SPEC_VERSION,
        source_bundle_identity=BUNDLE_ID,
        source_bundle_hash=bundle_hash,
        tool_retrieval_mode=RETRIEVAL_MODE,
        researcher_model_exposure_note=EXPOSURE_NOTE,
    )
    verified = policy.is_verified(session.session_id)
    if not verified:
        raise RuntimeError("SOURCE_ONLY session failed project verification")

    bundle = ApprovedSourceBundle(
        source_bundle_id=BUNDLE_ID,
        source_bundle_hash=bundle_hash,
        source_anchor_reference=(
            f"{BUNDLE_ID}: 3 official free/public Adam Grimes blog pages "
            "(2023-10-31, 2016-03-23, 2017-09-06) on adamhgrimes.com; see "
            "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_1_MANIFEST.json"
        ),
        content_note=RETENTION_BOUNDARY,
    )
    output = ClaimRecordOutput()
    runner = SourceOnlyClaimExtractionContext(
        source_bundle=bundle,
        source_only=policy,
        session_id=session.session_id,
        output_surface=output,
    )
    if not runner.verified:
        raise RuntimeError("SOURCE_ONLY claim-extraction runner is not verified")

    # ---- Protected-outcome technical denial (engineering proof, once) -----
    denial = runner.request_protected_market_outcome("ENGINEERING_PROOF_ONLY_NO_RETRIEVAL")
    if denial.outcome != "DENIED" or denial.reason != "SOURCE_ONLY_TECHNICAL_DENIAL":
        raise RuntimeError(f"Unexpected denial result: {denial}")

    # ---- Record claims through the provenance surface ---------------------
    for claim in CLAIMS:
        runner.record_claim(
            ClaimRecordDraft(
                claim_id=claim["claim_id"],
                source_id=bundle.source_bundle_id,
                source_anchor=claim["source_anchor"],
                claim_status=claim["claim_status"],
                source_excerpt_short_or_paraphrase=claim["source_excerpt_short_or_paraphrase"],
                source_only_session_id=session.session_id,
                created_at=CREATED_AT,
            )
        )

    # ---- C: SOURCE_ONLY session evidence + claim records ------------------
    session_record = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1",
        "session": {
            "session_id": session.session_id,
            "session_identity": session.session_identity,
            "model_identity": session.model_identity,
            "prompt_spec_version": session.prompt_spec_version,
            "source_bundle_identity": session.source_bundle_identity,
            "source_bundle_hash": session.source_bundle_hash,
            "tool_retrieval_mode": session.tool_retrieval_mode,
            "protected_market_access_mode": session.protected_market_access_mode.value,
            "researcher_model_exposure_note": session.researcher_model_exposure_note,
            "verification_evidence": session.verification_evidence,
        },
        "technical_denial_state": {
            "protected_market_access_mode": "TECHNICALLY_DENIED",
            "note": (
                "The SOURCE_ONLY runner exposes no project protected-period market-outcome "
                "retrieval surface; the only market-outcome-related entry point always "
                "DENIES and audits."
            ),
        },
        "is_verified": verified,
        "denial_path_result": {
            "outcome": denial.outcome,
            "reason": denial.reason,
            "request_reference": "ENGINEERING_PROOF_ONLY_NO_RETRIEVAL",
            "run_once": True,
        },
        "exposure_note": EXPOSURE_NOTE,
        "recorded_claim_count": len(output.records),
        "recorded_claim_ids": [r.claim_id for r in output.records],
        "claims": CLAIMS,
    }
    session_path = REPO_ROOT / "docs" / "evidence" / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1.json"
    _write_json(session_path, session_record)

    # ---- Console summary ---------------------------------------------------
    status_counts: dict[str, int] = {}
    for claim in CLAIMS:
        status_counts[claim["claim_status"]] = status_counts.get(claim["claim_status"], 0) + 1
    print(f"SOURCE_ONLY_VERIFIED={verified}")
    print(f"DENIAL_OUTCOME={denial.outcome}")
    print(f"DENIAL_REASON={denial.reason}")
    print(f"CLAIMS={len(CLAIMS)}")
    print(f"STATUS_COUNTS={status_counts}")
    print(f"BUNDLE_HASH={bundle_hash}")
    print(f"MANIFEST={manifest_path.relative_to(REPO_ROOT).as_posix()}")
    print(f"SESSION={session_path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
