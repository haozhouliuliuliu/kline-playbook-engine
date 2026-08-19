"""RASCHKE_NR7_TARGETED_SEMANTIC_COMPLETION_V1 - SOURCE_ONLY driver.

Targeted source-semantic completion for the selected family
`RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT`. This is NOT a backtest,
NOT strategy mining, NOT parameter search, NOT statistical inference, and does
NOT create a Playbook Contract.

It uses the actual project SOURCE_ONLY implementation in
`src/research_firewall.py`:

- predeclares the approved public source bundle (reuses the accepted
  `SB-RASCHKE-PUBLIC-SCREEN-V1` materials that anchor the NR7 / trend-day /
  bracket family and computes this bundle's canonical hash);
- opens a project-verified SOURCE_ONLY session via
  `SourceOnlyPolicy.open_verified_session(...)`;
- verifies `source_only.is_verified(session_id) == True`;
- executes the protected-outcome denial path once (engineering proof) and
  expects `outcome=DENIED` / `reason=SOURCE_ONLY_TECHNICAL_DENIAL`;
- records each of the 23 targeted semantic resolutions through the bounded
  `SourceOnlyClaimExtractionContext` provenance output surface;
- writes durable JSON evidence artifacts:
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_NR7_SEMANTIC_V0_1.json
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json

HARD BOUNDARIES (frozen authority, do not violate):
- HUMAN_PLAYBOOK_FIRST remains binding. No data-first K-line mining, indicator
  discovery, parameter search, candidate backtests, candidate PnL/returns,
  expectancy, Sharpe, win/loss, equity/drawdown, Validation access,
  historical-final access, or canonical market-outcome calibration.
- No candidate outcome / PnL / backtest / indicator search / chart-pattern
  mining. No project protected-period market-outcome retrieval (the runner has
  no such surface; any request is technically DENIED and audited).
- Source claim != project/AI interpretation != machine operationalization.
  Claim statuses use the canonical EXPLICIT | INFERRED | UNKNOWN. The 6-class
  semantic classification (EXPLICITLY_PINNED / SOURCE_PERMITTED_MULTIPLE_
  VARIANTS / PARTIALLY_PINNED / NOT_PINNED / REQUIRES_UNAVAILABLE_INPUT /
  INFERRED_PROJECT_TRANSFER) is a separate research-classification layer.
- No invented thresholds; no fabricated OHLCV proxies for absent inputs
  (NYSE TICK / breadth is NOT owned by the current Chinese-futures corpus).
- No purchase/subscription/authentication; official free/public unauthenticated
  source material only. No additional official free/public pre-2024 Raschke
  article was added because the official Articles index enumerates exactly the
  materials already in the accepted bundle and none directly resolves the open
  order/stop semantics. Official videos are YouTube-hosted and blocked by 403
  in the recorded environment; they were NOT circumvented.
- The task does NOT draft a Playbook Contract; it returns exactly one decision
  `PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES|NO`.

All used source materials have effective content dates BEFORE 2024-01-01
(before the frozen corpus start), so under Protocol v1.0 section 4 no
source-example date audit is required for the protected windows.

Run:
    python -m tools.run_raschke_nr7_semantic_completion_source_only
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

SESSION_ID = "SOURCE_ONLY_RASCHKE_NR7_SEMANTIC_V1_20260819"
MODEL_IDENTITY = "deepseek-v4-flash"
PROMPT_SPEC_VERSION = "RASCHKE_NR7_TARGETED_SEMANTIC_COMPLETION_V1"
RETRIEVAL_MODE = "LOCAL_FREE_PUBLIC_RASCHKE_NR7_SEMANTIC_ONLY"
# Claim Schema v1.0 source identity (the actual source, distinct from the
# bundle id). Claims reference this source plus an approved material_id.
SOURCE_ID = "SRC-RASCHKE"
BUNDLE_ID = "SB-RASCHKE-NR7-SEMANTIC-V1"
BUNDLE_NAME = (
    "Official free/public Linda Bradford Raschke NR7 targeted semantic-completion "
    "bundle - reuses the accepted Raschke screen materials that anchor the "
    "NR7 / range-contraction -> trend-day breakout family (no new material added)"
)
CREATED_AT = "2026-08-19T00:00:00Z"

BASE_BUNDLE_REFERENCE = {
    "base_bundle_id": "SB-RASCHKE-PUBLIC-SCREEN-V1",
    "base_bundle_hash": "7b11a8f1516696e2e54f9dc0ee4d7785f8f1cd9dad06d52abe15378edd2633bd",
    "note": (
        "This semantic-completion bundle reuses the exact accepted source screen "
        "bundle materials. The official Articles index (lindaraschke.net/articles/) "
        "enumerates exactly the same free/public PDFs already in the accepted bundle; "
        "no additional official free/public pre-2024 Raschke article directly resolves "
        "the open order/stop semantics. Official videos/interviews are YouTube-hosted "
        "and blocked by 403 in the recorded environment (no circumvention). Therefore "
        "no new material is added."
    ),
}

EXPOSURE_NOTE = (
    "Model latent historical knowledge cannot be proven absent; this is a disclosed "
    "residual threat-model risk under the frozen protocol. Project protected-period "
    "outcomes (DEVELOPMENT 2024, VALIDATION 2025H1, FINAL_HOLDOUT 2025H2) are "
    "technically unavailable to this SOURCE_ONLY runner: it exposes no project "
    "protected-period market-outcome retrieval surface, and any such request is "
    "technically DENIED and audited. No canonical market data repository, validation "
    "surface, or historical-final surface was exposed to this session. All used source "
    "materials have effective content dates before 2024-01-01 (before the frozen corpus "
    "start), so no source-example date audit is required for the protected windows "
    "under Protocol v1.0 section 4. The bundled articles are official source "
    "teaching/interview material only; they are not accepted trading truth and were "
    "never selected by expected profitability. This session performs a targeted "
    "source-semantic completion only; it does not draft a Playbook Contract and does "
    "not select 45-minute vs 60-minute early-range based on outcomes."
)

RETENTION_BOUNDARY = (
    "Raw PDFs and full extracted article text were processed only in a local temp "
    "directory OUTSIDE the repository and were not committed. Only attributable short "
    "excerpts and concise paraphrases needed for claim traceability are recorded. "
    "Anchors point to the canonical official public URLs on lindaraschke.net."
)

SELECTION_CRITERIA = [
    "reuses the exact accepted Raschke screen bundle (SB-RASCHKE-PUBLIC-SCREEN-V1) materials that anchor the NR7 / range-contraction -> trend-day breakout family",
    "official lindaraschke.net free/public article archive / TRACEABLE_ORIGINAL",
    "free/public/unauthenticated access state (verified by direct fetch on 2026-08-19 in the accepted screen package)",
    "effective content date before 2024-01-01 (before the frozen corpus start)",
    "official Articles index checked on 2026-08-19: no additional official free/public pre-2024 article directly resolves the open order/stop semantics, so no new material is added",
    "official videos/interviews are YouTube-hosted and blocked by 403 in the recorded environment; no circumvention; official free article/text material used",
    "stable attributable official URL, title, and publication date",
    "material materially anchors a required semantic field of the selected family (NR7 day definition/lookback, day-after-NR7 bracket entry, trend-day definition/confirmation, management/exit, no-trade/failure, instrument/timeframe scope)",
    "not broadened into unrelated third-party summaries or paid material",
    "not selected by expected historical performance"
]

OPTIONAL_PAID_CANDIDATES = [
    {
        "source_identity": "Trading Sardines: Lessons in the Markets from a Lifelong Trader (Linda Bradford Raschke; 2015 book, ISBN 9781532395622)",
        "access_class": "PAID_BOOK (not purchased; listed for awareness only)",
        "evidence_gap_it_could_fill": "Potential additional explicit stop/invalidation/order-mechanics language for the NR7 early-morning-range bracket family.",
        "why_it_might_matter": "Raschke's own book may contain deeper trading-loop semantics than the short official free articles.",
    },
    {
        "source_identity": "Street Smarts: High Probability Short-Term Trading Strategies (Raschke & Connors; book)",
        "access_class": "PAID_BOOK (not purchased; listed for awareness only)",
        "evidence_gap_it_could_fill": "Deeper source-pinned semantics for the pattern-specific entry/stop/exit rules referenced in the 1997 AIQ interview.",
        "why_it_might_matter": "The 1997 AIQ interview references the Holy Grail / Three-Day Unfilled Gap Reversal patterns from this book with more detail than the free article.",
    },
    {
        "source_identity": "NYSE TICK / advance-decline breadth data (US market internals) referenced throughout the interviews",
        "access_class": "PAID_OR_SUBSCRIPTION_DATA (not purchased; listed for awareness only)",
        "evidence_gap_it_could_fill": "Breadth/TICK surface for the trend-day confirmation handicap.",
        "why_it_might_matter": "The source's trend-day confirmation uses NYSE breadth/TICK; these surfaces are not in the Chinese-futures corpus.",
    },
]

# ---------------------------------------------------------------------------
# Source bundle materials (reused from the accepted screen bundle; no new material)
# ---------------------------------------------------------------------------

MATERIALS = [
    {
        "material_id": "SR-V0-M01",
        "canonical_title": "Short Term Trading Strategies",
        "source_publication": "AIQ Opening Bell",
        "content_type": "official interview (Linda Bradford Raschke; patterns: Holy Grail, Three-Day Unfilled Gap Reversal, Wolfe Wave; timing; stops)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/august1997.pdf",
        "publication_date": "1997-08",
        "effective_content_date": "1997-08",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "no-trade (middle of range); stop process ('most often, I'll get out if the market fails to do what I thought it would do'); impulse/thrust/range-expansion cue list; failure example (Eaton Corp); source context for the selected family's no-trade and stop-process fields",
        "content_note": (
            "AIQ Opening Bell, Vol 6, Issue 8, August 1997. Interview by David Vomund. "
            "Used for NO_TRADE / FAILURE_OR_COUNTEREXAMPLE / stop-process context in the "
            "NR7 semantic completion. 'The worst thing you can do in terms of market "
            "timing is to buy in the middle of a trading range. Either buy new highs, or "
            "buy pullbacks...'; 'Most often, I'll get out if the market fails to do what "
            "I thought it would do'; 'If I try to guess a breakout, I'm wrong 90 percent "
            "of the time' (also stated in the 2004 article); failure example Eaton Corp."
        ),
    },
    {
        "material_id": "SR-V0-M02",
        "canonical_title": "The Discerning Trader: Linda Bradford Raschke",
        "source_publication": "Technical Analysis of Stocks & Commodities (V.11:9)",
        "content_type": "official interview (Thom Hartle; NR7 breakout; prior-day levels; breakout vs swing mode; contraction measure)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/Discerning-trader.pdf",
        "publication_date": "1993-09",
        "effective_content_date": "1993-09",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "NR7 definition + breakout entry (cocoa commodity-futures example); contraction-measure umbrella ('that tells me to switch to a breakout mode'); three-day trend structure (carry a good trend day overnight); end-of-day handling ('The last hour's action is very important to me')",
        "content_note": (
            "Stocks & Commodities V.11:9 (360-366), 1993, interview by Thom Hartle. "
            "KEY material for the NR7 family: Figure 2 'A narrow range seven-day (NR7) in "
            "today's trading range is the narrowest trading range in the last seven days. "
            "The low volatility leads to a trend' (September Cocoa); 'A good example might "
            "be buying the breakout of an NR7 day, which stands for a narrow range "
            "seven-day pattern... going with the volatility in that case'; 'I use different "
            "measurements for the amount of contraction in the market... that tells me to "
            "switch to a breakout mode'; 'if you ever get a middle, or a good trend day... "
            "you should always carry that trade overnight because the odds are that you "
            "will get follow through the next day'; 'The last hour's action is very "
            "important to me. I want to see how a market's going to perform at the end of "
            "the day, and if I like how it acts at the end of the day I will continue to "
            "carry the trade.'"
        ),
    },
    {
        "material_id": "SR-V0-M03",
        "canonical_title": "Trading Style and Daily Market Regimen",
        "source_publication": "Active Trader",
        "content_type": "official interview (Mark Etzkorn; trend days; NR7 bracket; wide-range bar; session windows)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/raschke0204.pdf",
        "publication_date": "2004-02",
        "effective_content_date": "2004-02",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "PRIMARY material: NR7 day definition; trend-day definition; trend-day precursors; trend-day confirmation (15-min bar, volume, leadership, trendiness 10-10:30/10:45, breadth); day-after-NR7 early-morning-range bracket (45-min vs 1-hour variants); hold-to-end-of-day / add / hold-part-overnight; no-trade (breakout guess 90% wrong; flags volatility failure)",
        "content_note": (
            "Active Trader, February 2004, interview by Mark Etzkorn (a day with Linda "
            "Raschke, Nov 2003). PRIMARY material for the selected family: 'A trend day "
            "opens on one end of its range and closes on the opposite end, has range "
            "expansion, and makes a steady pattern of higher highs and higher lows, or "
            "vice versa, throughout the day. In the index futures, there are two or three "
            "trend days a month'; trend-day precursors (significant range contraction "
            "'such as an NR7 day, which is a bar with the narrowest range of the past "
            "seven bars'; large opening gap; approaching new 20-day highs/lows); trend-day "
            "confirmation (large opening 15-min bar attributed to Toby Crabel, with 'you "
            "can determine the threshold of significance yourself'; 'a significant "
            "increase in volume in the first 15 minutes relative to the past two weeks'; "
            "leadership IBM/MSFT/INTC/GE; 'trendiness between say, 10 and 10:30 or 10:45 "
            "a.m.'; 'trend in the market breadth - the difference between advancing issues "
            "and declining issues'); 'Something I'll almost always do the day after an NR7 "
            "day is bracket stops around the early morning range. When I tested this out "
            "about five years ago, it didn't matter whether you bracketed the first 45 "
            "minutes range or the first hour's range. If there's going to be a trend day, "
            "you're going to catch it'; 'I'm looking to hold that position until the end "
            "of the day, or add to the position during the day, or maybe hold part of it "
            "overnight'; 'If I try to guess a breakout, I'm wrong 90 percent of the time.'"
        ),
    },
    {
        "material_id": "SR-V0-M04",
        "canonical_title": "The Rituals of Trading",
        "source_publication": "Active Trader",
        "content_type": "official interview (Mark Etzkorn; price-based trading; management; risk; execution)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/rituals.pdf",
        "publication_date": "2000-08",
        "effective_content_date": "2000-08",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "management/exit principles for held positions ('The minute the market gives back more than it should, you get out on the first reaction or pause'; 'you have to at least take half the position off'); three-pushes momentum; NYSE TICK used like a momentum oscillator (unavailable-input boundary); 'Ninety percent of what I do is price-based'",
        "content_note": (
            "Active Trader, August 2000, interview by Mark Etzkorn. Used for EXIT_OR_TARGET "
            "and management context: 'The minute the market gives back more than it should, "
            "you get out on the first reaction or pause'; 'I try to stay with a position as "
            "long as I can and take half off'; 'if the market reaches a price objective and "
            "you're really not sure if it's going to continue, you have to at least take "
            "half the position off'; 'Ninety percent of what I do is price-based. Indicators "
            "are just derivatives of price'; 'I use the TICKs like a momentum oscillator... "
            "The bottoms of sell-offs will be accompanied by negative TICK extremes, like "
            "-1,000' (NYSE TICK = NOT_OBSERVABLE_WITH_CURRENT_DATA)."
        ),
    },
    {
        "material_id": "SR-V0-M05",
        "canonical_title": "Traders Toolbox",
        "source_publication": "Active Trader",
        "content_type": "official interview part 2 (Mark Etzkorn; indicator checklist; Holy Grail across time frames; bar-close-position tendency)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/03/raschke_pt2_0304.pdf",
        "publication_date": "2004-03",
        "effective_content_date": "2004-03",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "indicator checklist context; closing breadth (10-period SMA of NYSE advancers minus decliners) as an unavailable-input boundary; Holy Grail across time frames (timeframe-context); TICK/TIKI highs and lows (unavailable-input boundary)",
        "content_note": (
            "Active Trader, March 2004, interview by Mark Etzkorn (follow-up). Used for "
            "context on the breadth/TICK unavailable-input boundary and multi-timeframe "
            "scope. Indicator checklist includes closing breadth (10-period SMA of NYSE "
            "advancers minus decliners) and TICK/TIKI highs and lows - both NOT owned by "
            "the Chinese-futures corpus."
        ),
    },
]

# ---------------------------------------------------------------------------
# 23 targeted semantic resolutions (source-only)
# ---------------------------------------------------------------------------

# claim_status uses the canonical EXPLICIT | INFERRED | UNKNOWN:
#   EXPLICIT  -> the source explicitly states the semantic content
#   INFERRED  -> project/AI interpretation or project transfer hypothesis
#   UNKNOWN   -> the source provides no defining semantics (NOT_PINNED)
SEMANTIC_RESOLUTIONS = [
    {
        "claim_id": "C-RAS-NR7-SEM-001",
        "semantic_field": "NR7_DAILY_BAR_DEFINITION",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "'...such as an NR7 day, which is a bar with the narrowest range of the past "
            "seven bars.' (Figure 2 caption, SR-V0-M02: 'A narrow range seven-day (NR7) "
            "in today's trading range is the narrowest trading range in the last seven "
            "days. The low volatility leads to a trend.')"
        ),
        "source_context_note": (
            "The NR7 is explicitly defined as a bar with the narrowest range of the past "
            "seven bars, on the daily bar (the source says 'day' / 'trading range in the "
            "last seven days'). The daily-bar boundary construction for Chinese futures "
            "(including night-session aggregation) is a governed-metadata project "
            "convention, not defined by the source."
        ),
        "classification_rationale": (
            "The daily-bar NR7 definition (narrowest range over a seven-bar window) is "
            "explicitly stated in two accepted materials. The exact governed daily-bar "
            "construction for Chinese futures is a separate project-convention matter "
            "(recorded in NEXT_SESSION_DEFINITION / CHINESE_FUTURES_TRANSFER_STATUS)."
        ),
        "ambiguity_notes": (
            "Daily-bar boundary (night session vs calendar day) for Chinese futures is not "
            "source-defined; any governed-metadata convention is INFERRED."
        ),
        "source_observation_surface": "daily bar ranges",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (bar ranges from owned OHLCV + governed session metadata)",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-002",
        "semantic_field": "NR7_LOOKBACK_SEMANTICS",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "'a bar with the narrowest range of the past seven bars' versus Figure 2 "
            "caption 'in today's trading range is the narrowest trading range in the last "
            "seven days.'"
        ),
        "source_context_note": (
            "The lookback length (seven) is explicit. The exact inclusive/exclusive window "
            "alignment is not unambiguously stated: the text reads 'narrowest range of the "
            "past seven bars' (a 7-bar window) while the figure reads 'in today's trading "
            "range is the narrowest trading range in the last seven days' (today compared "
            "with the last seven days). Both readings exist in the accepted bundle."
        ),
        "classification_rationale": (
            "Window length (7) is pinned; the exact 'previous/current seven-bar set' "
            "alignment is ambiguous between the two accepted source statements. Any project "
            "window convention is therefore an explicit labeled interpretation."
        ),
        "ambiguity_notes": "Inclusive vs exclusive seven-bar window alignment is ambiguous in the accepted source bundle.",
        "source_observation_surface": "daily bar ranges over a seven-bar window",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "window alignment needs an interpreted convention (INFERRED); no unavailable input",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-003",
        "semantic_field": "NEXT_SESSION_DEFINITION",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "MARKET_CONTEXT",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "source_excerpt_short_or_paraphrase": (
            "'Something I'll almost always do the day after an NR7 day is bracket stops "
            "around the early morning range...'"
        ),
        "source_context_note": (
            "The source pins the entry session as 'the day after an NR7 day' (next trading "
            "session). The exact session/bar construction for Chinese futures (which "
            "session 'early morning' maps to; night-session aggregation; calendar-day "
            "boundary) is not defined by the source."
        ),
        "classification_rationale": (
            "'The day after an NR7 day' is explicit for the concept; the exact session "
            "construction for Chinese futures is a governed-metadata project convention "
            "(INFERRED), so the field is PARTIALLY_PINNED."
        ),
        "ambiguity_notes": "Session boundary construction (Chinese futures night session / calendar day) is a project convention.",
        "source_observation_surface": "session/day sequence",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "session boundary construction for Chinese futures is INFERRED (governed metadata)",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-004",
        "semantic_field": "EARLY_MORNING_RANGE_WINDOW",
        "semantic_classification": "SOURCE_PERMITTED_MULTIPLE_VARIANTS",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "source_excerpt_short_or_paraphrase": (
            "'...it didn't matter whether you bracketed the first 45 minutes range or the "
            "first hour's range. If there's going to be a trend day, you're going to catch "
            "it.'"
        ),
        "source_context_note": (
            "The source explicitly states that both the first-45-minutes range and the "
            "first-hour range worked in her own test. Neither variant is uniquely primary "
            "in the source. Both identities are preserved explicitly."
        ),
        "classification_rationale": (
            "SOURCE_PERMITTED_MULTIPLE_VARIANTS: both variants are explicitly source-stated. "
            "No outcome-driven selection is permitted. Variants preserved: "
            "EARLY_RANGE_VARIANT_45MIN and EARLY_RANGE_VARIANT_60MIN."
        ),
        "ambiguity_notes": "Exact start time and intraday-bar aggregation for 'first 45 minutes' / 'first hour' is a governed-metadata project convention (INFERRED); the window identities are preserved as two explicit variants.",
        "source_observation_surface": "intraday range from session open (45-minute or 60-minute window)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (1-minute bars + session metadata)",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-005",
        "semantic_field": "BRACKET_ENTRY_LONG_LEVEL",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "source_excerpt_short_or_paraphrase": (
            "'...bracket stops around the early morning range...' (long side: buy stop "
            "above the early-morning-range high)"
        ),
        "source_context_note": (
            "A bracket of stops around the early morning range means a buy stop above the "
            "range high (long entry) and a sell stop below the range low (short entry). "
            "The long entry level is the early-morning-range high. The exact tick offset "
            "above the high is NOT_PINNED (separate field ENTRY_OFFSET_OR_TICK_CONVENTION)."
        ),
        "classification_rationale": (
            "The long bracket entry is a buy stop above the early-morning-range high; the "
            "level concept is explicit. Offset detail is a separate NOT_PINNED field."
        ),
        "ambiguity_notes": "Tick offset above the range high is not source-pinned (see ENTRY_OFFSET_OR_TICK_CONVENTION).",
        "source_observation_surface": "early-morning-range high (45-min or 60-min window)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (price + session metadata)",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-006",
        "semantic_field": "BRACKET_ENTRY_SHORT_LEVEL",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "source_excerpt_short_or_paraphrase": (
            "'...bracket stops around the early morning range...' (short side: sell stop "
            "below the early-morning-range low)"
        ),
        "source_context_note": (
            "The short bracket entry is a sell stop below the early-morning-range low. "
            "The level concept is explicit; the exact tick offset below the low is "
            "NOT_PINNED (separate field ENTRY_OFFSET_OR_TICK_CONVENTION)."
        ),
        "classification_rationale": (
            "The short bracket entry is a sell stop below the early-morning-range low; the "
            "level concept is explicit. Offset detail is a separate NOT_PINNED field."
        ),
        "ambiguity_notes": "Tick offset below the range low is not source-pinned (see ENTRY_OFFSET_OR_TICK_CONVENTION).",
        "source_observation_surface": "early-morning-range low (45-min or 60-min window)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (price + session metadata)",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-007",
        "semantic_field": "ENTRY_ORDER_TYPE",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "source_excerpt_short_or_paraphrase": (
            "'...bracket stops around the early morning range...' (the entries are stop "
            "orders)"
        ),
        "source_context_note": (
            "The source literally says 'bracket stops', which pins the entry order type as "
            "stop orders (buy stop above, sell stop below). The exact order subtype "
            "(stop-market vs stop-limit) and resting/OCO state machine are not stated by "
            "the source (see UNTRIGGERED_OPPOSITE_ORDER_CANCELLATION)."
        ),
        "classification_rationale": (
            "'Bracket stops' pins stop-entry orders. The subtype and resting-order state "
            "machine are operationalization details not defined by the source."
        ),
        "ambiguity_notes": "Stop-market vs stop-limit subtype and resting/OCO state machine are not source-pinned.",
        "source_observation_surface": "order semantics (stop entry)",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "exact order subtype is an INFERRED project convention",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-008",
        "semantic_field": "ENTRY_OFFSET_OR_TICK_CONVENTION",
        "semantic_classification": "NOT_PINNED",
        "claim_status": "UNKNOWN",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "source_excerpt_short_or_paraphrase": (
            "'bracket stops around the early morning range' - no offset/tick convention is "
            "stated for the NR7 bracket."
        ),
        "source_context_note": (
            "The source does not state any tick or price offset for placing the bracket "
            "stops relative to the early-morning-range high/low. (The 'one tick above the "
            "high' language appears only for the separate Three-Day Unfilled Gap Reversal "
            "pattern in SR-V0-M01, which is a different family.)"
        ),
        "classification_rationale": (
            "No offset/tick convention is pinned for this bracket family. Any offset is a "
            "clearly labeled project convention (INFERRED) at operationalization."
        ),
        "ambiguity_notes": "No source offset convention; the gap-reversal 'one tick' language does not transfer to this family.",
        "source_observation_surface": "order placement offset",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "offset is an INFERRED project convention (tick size available from governed metadata)",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-009",
        "semantic_field": "UNTRIGGERED_OPPOSITE_ORDER_CANCELLATION",
        "semantic_classification": "NOT_PINNED",
        "claim_status": "UNKNOWN",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "source_excerpt_short_or_paraphrase": (
            "No source statement about the untriggered opposite bracket order after one "
            "side fills."
        ),
        "source_context_note": (
            "The source describes bracketing stops around the early morning range but does "
            "not state what happens to the untriggered opposite order once one side fills. "
            "No OCO / cancel-on-fill semantics for this bracket are given. (The separate "
            "gap-reversal pattern states 'if not filled after three trading sessions, "
            "cancel the initial buy stop', but that belongs to a different family.)"
        ),
        "classification_rationale": (
            "Cancellation semantics for the untriggered opposite bracket order are not "
            "pinned by the source. Any OCO/cancel-on-fill handling is a clearly labeled "
            "project convention (INFERRED)."
        ),
        "ambiguity_notes": "Standard bracket mechanics (OCO cancel-on-fill) are a project convention, not a source claim.",
        "source_observation_surface": "order state machine",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "cancellation semantics are an INFERRED project convention",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-010",
        "semantic_field": "SIMULTANEOUS_OR_SAME_BAR_TRIGGER_HANDLING",
        "semantic_classification": "NOT_PINNED",
        "claim_status": "UNKNOWN",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "source_excerpt_short_or_paraphrase": (
            "No source statement about handling both bracket sides triggering on the same "
            "bar."
        ),
        "source_context_note": (
            "The source does not state how to handle a bar that trades through both the "
            "early-morning-range high and low (both bracket sides triggering on the same "
            "bar)."
        ),
        "classification_rationale": (
            "Same-bar/simultaneous trigger handling is not pinned by the source; any "
            "handling is a clearly labeled project convention (INFERRED)."
        ),
        "ambiguity_notes": "Same-bar double-trigger handling is a project convention, not a source claim.",
        "source_observation_surface": "intrabar trigger logic",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "same-bar handling is an INFERRED project convention",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-011",
        "semantic_field": "POST_ENTRY_INVALIDATION",
        "semantic_classification": "NOT_PINNED",
        "claim_status": "UNKNOWN",
        "claim_category": "INVALIDATION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY; SR-V0-M04:rituals:section:MANAGEMENT_EXIT",
        "source_excerpt_short_or_paraphrase": (
            "No source statement establishes a post-entry invalidation boundary for the "
            "NR7 early-morning-range bracket. (Generic: 'The minute the market gives back "
            "more than it should, you get out on the first reaction or pause.')"
        ),
        "source_context_note": (
            "Integration correction IC-1: the bracket statement defines ENTRY placement "
            "only. It does NOT prove that the opposite bracket side is the post-entry "
            "stop/invalidation for the selected family. The generic management statement "
            "is qualitative and does not define a unique numerical invalidation boundary."
        ),
        "classification_rationale": (
            "Per the integration review, INVALIDATION_REFERENCE=NOT_YET_SOURCE_PINNED_FOR_"
            "SELECTED_FAMILY. No source evidence establishes actual post-entry "
            "risk/invalidation for this bracket family. A NO/UNKNOWN here is acceptable."
        ),
        "ambiguity_notes": "Opposite bracket side must NOT be treated as an explicit source stop/invalidation without new source evidence.",
        "source_observation_surface": "post-entry price behavior (no source-defined boundary)",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "no source-defined invalidation boundary; a project boundary would be invented",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-012",
        "semantic_field": "INITIAL_STOP",
        "semantic_classification": "NOT_PINNED",
        "claim_status": "UNKNOWN",
        "claim_category": "RISK_PROCESS",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY; SR-V0-M01:august1997:section:STOP_PROCESS",
        "source_excerpt_short_or_paraphrase": (
            "No source-stated initial protective stop for the NR7 bracket entry. (Generic: "
            "'Most often, I'll get out if the market fails to do what I thought it would "
            "do.')"
        ),
        "source_context_note": (
            "The source does not state an initial stop for the day-after-NR7 early-morning-"
            "range bracket. The general discretionary stop process is not a pinned stop "
            "for this family."
        ),
        "classification_rationale": (
            "INITIAL_STOP=NOT_PINNED. No source-pinned initial protective stop exists for "
            "this bracket family; a numeric initial stop would be invented."
        ),
        "ambiguity_notes": "A source-faithful initial stop does not exist; inventing one is inventing critical trading-loop semantics.",
        "source_observation_surface": "protective stop placement (none source-defined)",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "no source-defined initial stop; a project stop would be invented",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-013",
        "semantic_field": "TREND_DAY_DEFINITION",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_DEFINITION",
        "source_excerpt_short_or_paraphrase": (
            "'A trend day opens on one end of its range and closes on the opposite end, "
            "has range expansion, and makes a steady pattern of higher highs and higher "
            "lows, or vice versa, throughout the day. In the index futures, there are two "
            "or three trend days a month.'"
        ),
        "source_context_note": (
            "Explicit, price-based trend-day definition. The defining semantics (open on "
            "one end, close on the opposite, range expansion, steady higher highs/higher "
            "lows) are stated. The numerical thresholds for 'range expansion' and 'steady "
            "pattern' are not quantified by the source (operationalization detail)."
        ),
        "classification_rationale": (
            "The trend-day definition semantics are explicit and price-based. Machine "
            "thresholding of 'range expansion' / 'steady pattern' would require an "
            "INFERRED project convention, but the definition itself is pinned."
        ),
        "ambiguity_notes": "'Range expansion' and 'steady pattern' are not numerically pinned (operationalization detail).",
        "source_observation_surface": "open/close/range/high-low sequence across the session",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (price from owned OHLCV); thresholds for 'expansion'/'steady' are INFERRED if operationalized",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-014",
        "semantic_field": "TREND_DAY_CONFIRMATION",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "CONFIRMATION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_CONFIRMATION",
        "source_excerpt_short_or_paraphrase": (
            "Trend-day confirmation: a very large 15-minute bar to open the session "
            "(Crabel) with 'you can determine the threshold of significance yourself'; "
            "'a significant increase in volume in the first 15 minutes relative to the "
            "past two weeks'; leadership (IBM/Microsoft/Intel/GE); 'trendiness between "
            "say, 10 and 10:30 or 10:45 a.m.'; and 'trend in the market breadth - the "
            "difference between advancing issues and declining issues.'"
        ),
        "source_context_note": (
            "Confirmation components are price/session/volume observable except breadth "
            "(NYSE TICK, unavailable). The source explicitly leaves the 'big bar' "
            "threshold to the trader ('compare it to the past five opening 15-minute bars "
            "or the past 20. You can quantify this type of thing a zillion different "
            "ways'). Confirmation is a handicap, not the NR7 bracket entry trigger itself."
        ),
        "classification_rationale": (
            "Confirmation components are partially pinned: volume/session components are "
            "observable and stated (qualitative), the 15-min-bar threshold is explicitly "
            "left to the trader (source-permitted multiple variants within the component), "
            "and the breadth component is REQUIRES_UNAVAILABLE_INPUT (separated in "
            "BREADTH_TICK_ROLE)."
        ),
        "ambiguity_notes": "'Very large' 15-min bar and 'significant increase' in volume are not numerically pinned; breadth input unavailable.",
        "source_observation_surface": "15-minute opening bar, volume, leadership names, intraday trendiness window, breadth",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "breadth/TICK component NOT_OBSERVABLE_WITH_CURRENT_DATA (see BREADTH_TICK_ROLE)",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-015",
        "semantic_field": "ORDINARY_VOLUME_ROLE",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "CONFIRMATION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_CONFIRMATION",
        "source_excerpt_short_or_paraphrase": (
            "'Which of those stocks have had a significant increase in volume in the first "
            "15 minutes relative to the past two weeks?' and 'The other things we look for "
            "in terms of a higher trending day include a volume increase.'"
        ),
        "source_context_note": (
            "Ordinary volume is used as a confirmation/enlargement component (not a gated "
            "entry condition): a volume increase supports a higher trending day and a "
            "big-target hold ('if I see volume, trend in the breadth and strong money "
            "flows, I'll play for a big target'). No numeric threshold or relative-volume "
            "baseline is pinned."
        ),
        "classification_rationale": (
            "Volume role is explicit but qualitative (confirmation/diagnostic), with no "
            "threshold or gating pinned. Ordinary volume is observable on the corpus."
        ),
        "ambiguity_notes": "'Significant increase' is not numerically pinned; volume is a non-gated confirmation component.",
        "source_observation_surface": "ordinary volume (first-15-minutes vs past two weeks comparison; intraday volume)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "no unavailable input; threshold is INFERRED if operationalized",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-016",
        "semantic_field": "BREADTH_TICK_ROLE",
        "semantic_classification": "REQUIRES_UNAVAILABLE_INPUT",
        "claim_status": "EXPLICIT",
        "claim_category": "CONFIRMATION",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_CONFIRMATION; SR-V0-M04:rituals:section:TICK_AS_MOMENTUM",
        "source_excerpt_short_or_paraphrase": (
            "'the last and most important thing is that I want to see trend in the market "
            "breadth - the difference between advancing issues and declining issues' "
            "(NYSE TICK); 'I use the TICKs like a momentum oscillator... The bottoms of "
            "sell-offs will be accompanied by negative TICK extremes, like -1,000.'"
        ),
        "source_context_note": (
            "The source's trend-day confirmation and momentum read use NYSE TICK/breadth "
            "(advancing minus declining) and TIKI. These are US-market internals NOT owned "
            "by the Chinese-futures 1-minute OHLCV corpus and are not ordinary volume. No "
            "OHLCV proxy is authorized. Breadth/TICK is a confirmation handicap, not the "
            "NR7 bracket entry trigger."
        ),
        "classification_rationale": (
            "REQUIRES_UNAVAILABLE_INPUT: the source's breadth/TICK confirmation surface is "
            "not owned by the project corpus; it is recorded as missing, not proxied."
        ),
        "ambiguity_notes": "No invented OHLCV proxy for breadth/TICK is authorized.",
        "source_observation_surface": "NYSE TICK / advancing-minus-declining breadth; TIKI",
        "observability_compatibility": "NOT_OBSERVABLE_WITH_CURRENT_DATA",
        "observability_missing_inputs": "NYSE TICK / breadth (US market internals) not owned; no proxy",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-017",
        "semantic_field": "EXIT_OR_TARGET",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "EXIT",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_CONFIRMATION; SR-V0-M04:rituals:section:MANAGEMENT_EXIT",
        "source_excerpt_short_or_paraphrase": (
            "'I'm looking to hold that position until the end of the day, or add to the "
            "position during the day, or maybe hold part of it overnight'; 'The minute the "
            "market gives back more than it should, you get out on the first reaction or "
            "pause'; 'if the market reaches a price objective and you're really not sure "
            "if it's going to continue, you have to at least take half the position off.'"
        ),
        "source_context_note": (
            "Exit/target semantics are 'ride the trend day': hold to end of day / add / "
            "hold part overnight on a confirmed trend day; exit on the first reaction/pause "
            "when price gives back more than it should; take at least half off at an "
            "uncertain price objective. These are qualitative management principles; no "
            "numeric target is pinned."
        ),
        "classification_rationale": (
            "The exit intent ('ride the trend day', give-back exit, take-half) is explicit "
            "but qualitative; no unique numeric target/convention is pinned. Any target "
            "level is an INFERRED project convention."
        ),
        "ambiguity_notes": "'Gives back more than it should', 'price objective', and 'big target' are not numerically pinned.",
        "source_observation_surface": "end-of-day hold / intraday give-back / price objective",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "no unique target level; exit convention is INFERRED if operationalized",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-018",
        "semantic_field": "END_OF_SESSION_HANDLING",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "EXIT",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_CONFIRMATION; SR-V0-M02:discerning-trader:section:THREE_DAY_STRUCTURE",
        "source_excerpt_short_or_paraphrase": (
            "'I'm looking to hold that position until the end of the day, or add to the "
            "position during the day, or maybe hold part of it overnight'; 'The last "
            "hour's action is very important to me... if I like how it acts at the end of "
            "the day I will continue to carry the trade'; 'if you ever get a middle, or a "
            "good trend day... you should always carry that trade overnight.'"
        ),
        "source_context_note": (
            "End-of-session handling is present: on a confirmed trend day, hold to the end "
            "of the day, add during the day, or hold part overnight; the last hour's "
            "behavior decides whether to carry the trade. Multiple allowed options are "
            "qualitative, not a deterministic rule."
        ),
        "classification_rationale": (
            "End-of-session semantics are explicit but qualitative with several allowed "
            "options; no deterministic end-of-session rule is pinned."
        ),
        "ambiguity_notes": "No deterministic end-of-session exit rule; options (hold all / add / hold part overnight) are qualitative.",
        "source_observation_surface": "end-of-day price behavior; overnight carry decision",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "no deterministic end-of-session rule; convention is INFERRED if operationalized",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-019",
        "semantic_field": "NO_TRADE",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "NO_TRADE",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:BREAKOUT_GUESS_FAILURE; SR-V0-M01:august1997:section:MARKET_TIMING",
        "source_excerpt_short_or_paraphrase": (
            "'If I try to guess a breakout, I'm wrong 90 percent of the time'; 'The worst "
            "thing you can do in terms of market timing is to buy in the middle of a "
            "trading range'; 'If there's no improvement in volume or breadth, the market "
            "is more likely to stay within a trading range.'"
        ),
        "source_context_note": (
            "Explicit no-trade constraints: do not guess breakout direction; do not buy in "
            "the middle of a trading range; without volume/breadth improvement the market "
            "is likely range-bound (scalp mode, not a big-target trend-day trade). These "
            "are qualitative constraints, not a deterministic no-trade gate."
        ),
        "classification_rationale": (
            "No-trade context is explicit but qualitative; no deterministic no-trade gate "
            "is pinned."
        ),
        "ambiguity_notes": "'Middle of a trading range', 'no improvement', and 'scalp mode' are not numerically pinned.",
        "source_observation_surface": "price position, volume/breadth improvement, breakout guessing",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "no deterministic gate; the breadth component is unavailable",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-020",
        "semantic_field": "FAILURE_OR_COUNTEREXAMPLE",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "FAILURE_OR_COUNTEREXAMPLE",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY; SR-V0-M03:raschke0204:section:FLAGS_VOLATILITY; SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "NR7 does not guarantee a trend day ('If there's going to be a trend day, "
            "you're going to catch it' - only if there is one); 'If I try to guess a "
            "breakout, I'm wrong 90 percent of the time'; flags 'will fail after a "
            "volatility extreme... and in contracting volatility... Statistical reliability "
            "only comes with a volatility filter'; Eaton Corp example ('no reason to be in "
            "the trade')."
        ),
        "source_context_note": (
            "Source-explicit failure/counterexample context: the bracket only catches a "
            "trend day if one develops; breakout guessing fails ~90%; continuation flags "
            "fail at volatility extremes and in contracting volatility; a no-trade failure "
            "example (Eaton Corp). No systematic loss ledger is provided (source-quality "
            "limitation, recorded not manufactured)."
        ),
        "classification_rationale": (
            "Failure/no-trade evidence is source-explicit and preserved, but qualitative; "
            "no quantitative failure rate is pinned for the NR7 family itself."
        ),
        "ambiguity_notes": "'Volatility extreme', 'V-spike', and 'significant degree' are not numerically pinned.",
        "source_observation_surface": "price/volume failure context; volatility extremes",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "no systematic loss ledger; qualitative only",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-021",
        "semantic_field": "TIMEFRAME_SCOPE",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "APPLICABILITY",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_SETUP; SR-V0-M04:rituals:section:MANAGEMENT_EXIT",
        "source_excerpt_short_or_paraphrase": (
            "NR7 defined on the daily bar; bracket entry intraday (first 45 minutes or "
            "first hour); confirmation on opening 15-minute bars; management on hourly "
            "charts ('continuation patterns on an hourly chart - little bull flags, "
            "triangles')."
        ),
        "source_context_note": (
            "The family spans daily (setup), intraday (entry), 15-minute (confirmation), "
            "and hourly (management) timeframes. No single operating timeframe is pinned "
            "for the whole loop."
        ),
        "classification_rationale": (
            "Multi-timeframe structure is explicit but no single operating timeframe is "
            "uniquely pinned for the full loop; PARTIALLY_PINNED."
        ),
        "ambiguity_notes": "No single operating timeframe is pinned for the whole trading loop.",
        "source_observation_surface": "daily bars, intraday bars, 15-minute bars, hourly bars",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (all timeframes derivable from owned data)",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-022",
        "semantic_field": "INSTRUMENT_SCOPE",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "APPLICABILITY",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_DEFINITION; SR-V0-M02:discerning-trader:section:NR7_BREAKOUT",
        "source_excerpt_short_or_paraphrase": (
            "'In the index futures, there are two or three trend days a month' (S&P index-"
            "futures bracket context); NR7 concept chart example is September Cocoa "
            "(commodity futures, 1993); 2004 context also covers US equities."
        ),
        "source_context_note": (
            "SOURCE_INSTRUMENT_SCOPE=US_EQUITY_INDEX_FUTURES_AND_US_EQUITIES_AND_"
            "COMMODITY_FUTURES. SOURCE_SUPPORTS_COMMODITY_FUTURES=YES (NR7/contraction-"
            "expansion concept explicitly shown on cocoa). SOURCE_SUPPORTS_CROSS_MARKET_"
            "TRANSFER=UNKNOWN (no explicit statement about transferring the exact bracket "
            "trade across asset classes)."
        ),
        "classification_rationale": (
            "The source instrument scope is explicitly pinned to US equity index futures + "
            "US equities + commodity futures (NR7 concept). The exact bracket practice is "
            "stated in an index-futures context."
        ),
        "ambiguity_notes": "SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN (no explicit statement about Chinese futures; see CHINESE_FUTURES_TRANSFER_STATUS).",
        "source_observation_surface": "instrument scope statement",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "the source universe is not the current corpus; transfer is a separate INFERRED field",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-NR7-SEM-023",
        "semantic_field": "CHINESE_FUTURES_TRANSFER_STATUS",
        "semantic_classification": "INFERRED_PROJECT_TRANSFER",
        "claim_status": "INFERRED",
        "claim_category": "APPLICABILITY",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "source_excerpt_short_or_paraphrase": (
            "Transfer of the exact day-after-NR7 early-morning-range bracket practice to "
            "cu/al/ni/au/ag/rb is NOT an explicit source claim."
        ),
        "source_context_note": (
            "The NR7 / contraction-expansion concept has a commodity-futures anchor "
            "(September Cocoa, 1993), but the exact bracket practice is stated in an "
            "index-futures (S&P) context. Transferring the exact bracket entry/management "
            "to Chinese futures is an INFERRED project hypothesis, not an explicit source "
            "claim."
        ),
        "classification_rationale": (
            "INFERRED_PROJECT_TRANSFER: any Chinese-futures operationalization is a "
            "separately labeled project hypothesis and does not inherit source authority "
            "automatically."
        ),
        "ambiguity_notes": "SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN; transfer is INFERRED, never presented as source fact.",
        "source_observation_surface": "instrument transfer hypothesis",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "transfer to Chinese futures is an INFERRED project hypothesis",
        "lineage_id": "L-RAS-NR7",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
]

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _canonical_hash(value: object) -> str:
    """Same canonical JSON+sha256 scheme used by src.research_firewall."""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _material_records() -> list[dict]:
    records = []
    for material in MATERIALS:
        note_hash = _canonical_hash(
            {
                "material_id": material["material_id"],
                "url": material["url"],
                "title": material["canonical_title"],
                "publication_date": material["publication_date"],
                "content_note": material["content_note"],
            }
        )
        record = dict(material)
        record["content_note_hash"] = note_hash
        records.append(record)
    return records


def _bundle_hash() -> str:
    return _canonical_hash(
        {
            "bundle_id": BUNDLE_ID,
            "retrieval_mode": RETRIEVAL_MODE,
            "materials": [
                {k: m[k] for k in ("material_id", "url", "canonical_title", "publication_date")}
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


def _claim_record_for(claim: dict, session_id: str) -> ClaimRecordDraft:
    return ClaimRecordDraft(
        claim_id=claim["claim_id"],
        source_id=SOURCE_ID,
        material_id=claim["material_id"],
        source_anchor=claim["source_anchor"],
        claim_status=claim["claim_status"],
        source_excerpt_short_or_paraphrase=claim["source_excerpt_short_or_paraphrase"],
        source_only_session_id=session_id,
        created_at=CREATED_AT,
    )


def _classification_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for resolution in SEMANTIC_RESOLUTIONS:
        key = resolution["semantic_classification"]
        counts[key] = counts.get(key, 0) + 1
    return counts


def main() -> None:
    _ = EvidenceLedger  # exercise import graph (no market data held here)

    bundle_hash = _bundle_hash()
    material_records = _material_records()

    # ---- Approved source bundle (provenance surface) --------------------
    # Built before the SOURCE_ONLY session so the session can bind the
    # deterministic material-derived session binding identity/hash (F-C01),
    # not the legacy recorded bundle id/hash.
    bundle = ApprovedSourceBundle.legacy_unbound(
        source_bundle_id=BUNDLE_ID,
        source_bundle_hash=bundle_hash,
        source_anchor_reference=(
            f"{BUNDLE_ID}: reuses the accepted Raschke screen bundle materials "
            "(SR-V0-M01 AIQ 1997-08; SR-V0-M02 S&C 1993-09; SR-V0-M03 Active Trader "
            "2004-02; SR-V0-M04 Active Trader 2000-08; SR-V0-M05 Active Trader 2004-03) "
            "that anchor the NR7 / range-contraction -> trend-day breakout family; see "
            "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_NR7_SEMANTIC_V0_1.json"
        ),
        material_records=tuple(
            {
                "source_id": SOURCE_ID,
                "material_id": material["material_id"],
                "source_anchor_reference": material["material_id"],
            }
            for material in MATERIALS
        ),
        content_note=RETENTION_BOUNDARY,
    )

    # ---- B: source bundle manifest (predeclared) --------------------------
    manifest = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_NR7_SEMANTIC",
        "manifest_version": "1.0",
        "bundle_id": BUNDLE_ID,
        "bundle_name": BUNDLE_NAME,
        "canonical_bundle_hash": bundle_hash,
        "selected_on": "2026-08-19",
        "retrieval_mode": RETRIEVAL_MODE,
        "package": "RASCHKE_NR7_TARGETED_SEMANTIC_COMPLETION_V0_1",
        "source": "SRC-RASCHKE",
        "source_admission_reference": (
            "docs/research/source_dossiers/SOURCE_DOSSIER_RASCHKE_V0_1.md; "
            "docs/reviews/HUMAN_PLAYBOOK_RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_"
            "INTEGRATION_REVIEW_V0_1.md"
        ),
        "base_bundle_reference": BASE_BUNDLE_REFERENCE,
        "selection_criteria": SELECTION_CRITERIA,
        "selection_basis_note": (
            "Reuses the accepted Raschke screen bundle materials that anchor the "
            "NR7 / range-contraction -> trend-day breakout family. Selection based on "
            "provenance + free/public access + source-anchor quality + direct relevance "
            "to the required semantic fields. NEVER based on expected trading performance."
        ),
        "no_additional_source_added": {
            "checked_on": "2026-08-19",
            "official_articles_index": "https://lindaraschke.net/articles/",
            "finding": (
                "The official Articles index enumerates exactly the same free/public PDFs "
                "already in the accepted screen bundle (Trade Trends, Trading Insights, "
                "Traders Toolbox, Multi-Market Traders Rule, The Rituals of Trading, Short "
                "Term Trading Strategies, Maintain your Mindset, Who are You?, Everything "
                "About Electronic Trading, The Discerning Trader, Trading Style and Daily "
                "Market Regimen). No additional official free/public pre-2024 Raschke "
                "article directly resolves the open order/stop semantics. Official "
                "videos/interviews are YouTube-hosted and blocked by 403 in the recorded "
                "environment (no circumvention). Therefore no new material is added."
            ),
        },
        "access_state": {
            "verified_at": "2026-08-19",
            "all_urls_accessible": True,
            "all_urls_free_public_unauthenticated": True,
            "all_effective_content_dates_before_2024_01_01": True,
            "note": (
                "URLs verified via direct HTTP fetch in the accepted screen package; PDFs "
                "are %PDF- with 200 status; no authentication/cookies used."
            ),
        },
        "video_surface": {
            "official_video_index": "https://lindaraschke.net/linda-videos/",
            "hosting": "YouTube channel @lindaraschke6565 only (no direct embeds/mp4)",
            "acquisition_state": "BLOCKED_BY_403_IN_RECORDED_ENV",
            "circumvention_attempted": "NO",
            "fallback": "official free article/text material used",
        },
        "materials": material_records,
        "raw_material_retention_boundary": RETENTION_BOUNDARY,
        "copyright_boundary": (
            "Store traceability, not a redistribution archive. Only short excerpts and "
            "concise paraphrases are recorded; full copyrighted articles are not stored "
            "in the repository."
        ),
        "optional_paid_candidates": OPTIONAL_PAID_CANDIDATES,
        "paid_candidates_note": (
            "Listed for awareness only. No purchase or subscription is authorized. "
            "PAID_SOURCE_PURCHASE_DEFAULT=NO. Free/public alternatives were sufficient "
            "for this semantic completion."
        ),
    }
    manifest_path = (
        REPO_ROOT / "docs" / "evidence" / "HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_NR7_SEMANTIC_V0_1.json"
    )
    _write_json(manifest_path, manifest)

    # ---- Verified SOURCE_ONLY session (actual project implementation) -----
    from src.research_firewall import SourceOnlyPolicy

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
    verified = policy.is_verified(session.session_id)
    if not verified:
        raise RuntimeError("SOURCE_ONLY session failed project verification")

    output = ClaimRecordOutput()
    runner = SourceOnlyClaimExtractionContext(
        source_bundle=bundle,
        source_only=policy,
        session_id=session.session_id,
        output_surface=output,
    )
    if not runner.verified:
        raise RuntimeError("SOURCE_ONLY semantic-completion runner is not verified")

    # ---- Protected-outcome technical denial (engineering proof, once) -----
    denial = runner.request_protected_market_outcome("ENGINEERING_PROOF_ONLY_NO_RETRIEVAL")
    if denial.outcome != "DENIED" or denial.reason != "SOURCE_ONLY_TECHNICAL_DENIAL":
        raise RuntimeError(f"Unexpected denial result: {denial}")

    # ---- Record the 23 semantic resolutions through the provenance surface -
    for resolution in SEMANTIC_RESOLUTIONS:
        runner.record_claim(_claim_record_for(resolution, session.session_id))

    # ---- C: SOURCE_ONLY session evidence + claim records ------------------
    session_record = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC",
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
        "session_purpose": (
            "RASCHKE_NR7_TARGETED_SEMANTIC_COMPLETION_V1. Targeted source-semantic "
            "completion for the selected family RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_"
            "BREAKOUT: resolve 23 semantic fields from the accepted source bundle and "
            "return exactly one decision PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES|NO. No "
            "Playbook Contract is drafted by this session."
        ),
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
        "claim_status_semantics": (
            "claim_status uses the canonical Claim Schema v1.0 statuses: "
            "EXPLICIT | INFERRED | UNKNOWN. EXPLICIT = source-stated semantics; "
            "INFERRED = project/AI interpretation or project transfer hypothesis; "
            "UNKNOWN = source provides no defining semantics (NOT_PINNED). The 6-class "
            "semantic_classification (EXPLICITLY_PINNED / SOURCE_PERMITTED_MULTIPLE_"
            "VARIANTS / PARTIALLY_PINNED / NOT_PINNED / REQUIRES_UNAVAILABLE_INPUT / "
            "INFERRED_PROJECT_TRANSFER) is a separate research-classification layer."
        ),
        "semantic_classification_legend": {
            "EXPLICITLY_PINNED": "the source gives an explicit, unambiguous semantic statement sufficient for faithful representation of the core meaning",
            "SOURCE_PERMITTED_MULTIPLE_VARIANTS": "the source explicitly permits more than one discrete variant; no unique PRIMARY is justified; all variants are preserved explicitly",
            "PARTIALLY_PINNED": "the source gives the concept/role but leaves a semantically meaningful boundary, measure, or detail undefined",
            "NOT_PINNED": "the source references the concept but provides no defining semantics",
            "REQUIRES_UNAVAILABLE_INPUT": "the source semantics require an information surface the project does not own",
            "INFERRED_PROJECT_TRANSFER": "project/AI transfer or interpretation hypothesis, not an explicit source claim",
        },
        "semantic_classification_counts": _classification_counts(),
        "recorded_claim_count": len(output.records),
        "recorded_claim_ids": [r.claim_id for r in output.records],
        "final_decision": {
            "family": "RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT",
            "PLAYBOOK_SEMANTICALLY_DRAFTABLE": "NO",
            "decision_rationale": (
                "The source pins the complete ENTRY mechanism (NR7 daily-bar definition; "
                "day-after-NR7 bracket stops around the early-morning range, with 45-min "
                "and 60-min as explicit source-permitted variants; buy stop above range "
                "high / sell stop below range low) and the price-based trend-day "
                "definition, but it does NOT pin the post-entry risk loop: INITIAL_STOP="
                "NOT_PINNED and POST_ENTRY_INVALIDATION=NOT_PINNED (integration correction "
                "IC-1). A full trading-loop Playbook Contract would still require invented "
                "critical invalidation/stop semantics, which is exactly the NO condition. "
                "The remaining entry/session order-mechanics gaps (tick offset, OCO "
                "cancellation, same-bar handling) are representable as clearly labeled "
                "project conventions, but the missing risk loop is not a source-permitted "
                "variant or a transfer; it is absent from the source."
            ),
            "primary_blocker": (
                "SOURCE_POST_ENTRY_RISK_SEMANTICS_NOT_PINNED "
                "(INITIAL_STOP=NOT_PINNED; POST_ENTRY_INVALIDATION=NOT_PINNED)"
            ),
            "early_range_variants": "EARLY_RANGE_VARIANT_45MIN, EARLY_RANGE_VARIANT_60MIN (both SOURCE_PERMITTED; no unique PRIMARY)",
            "source_supports_current_project_products": "UNKNOWN",
            "NO_CANDIDATE_OUTCOME_DATA_USED": "YES",
        },
        "claims": SEMANTIC_RESOLUTIONS,
    }
    session_path = (
        REPO_ROOT / "docs" / "evidence" / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json"
    )
    _write_json(session_path, session_record)

    # ---- Console summary ---------------------------------------------------
    print(f"SOURCE_ONLY_VERIFIED={verified}")
    print(f"DENIAL_OUTCOME={denial.outcome}")
    print(f"DENIAL_REASON={denial.reason}")
    print(f"RESOLUTIONS={len(SEMANTIC_RESOLUTIONS)}")
    print(f"CLASSIFICATION_COUNTS={_classification_counts()}")
    print(f"BUNDLE_HASH={bundle_hash}")
    print(f"MATERIALS={len(MATERIALS)}")
    print(f"MANIFEST={manifest_path.relative_to(REPO_ROOT).as_posix()}")
    print(f"SESSION={session_path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
