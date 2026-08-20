"""RASCHKE_HOLY_GRAIL_TARGETED_SEMANTIC_COMPLETION_V1 - SOURCE_ONLY driver.

Targeted source-semantic completion for the family
`RASCHKE_HOLY_GRAIL_PULLBACK` (strong-trend / ADX context + pullback to a
20-period exponential moving average). This is NOT a backtest, NOT strategy
mining, NOT parameter search, NOT statistical inference, and does NOT create a
Playbook Contract.

It uses the actual project SOURCE_ONLY implementation in
`src/research_firewall.py`:

- predeclares the approved public source bundle (reuses the exact accepted
  `SB-RASCHKE-PUBLIC-SCREEN-V1` materials that anchor the Holy Grail / pullback
  family and computes this bundle's canonical hash);
- opens a project-verified SOURCE_ONLY session via
  `SourceOnlyPolicy.open_verified_session(...)`;
- verifies `source_only.is_verified(session_id) == True`;
- executes the protected-outcome denial path once (engineering proof) and
  expects `outcome=DENIED` / `reason=SOURCE_ONLY_TECHNICAL_DENIAL`;
- records each of the 27 targeted semantic resolutions through the bounded
  `SourceOnlyClaimExtractionContext` provenance output surface;
- writes durable JSON evidence artifacts:
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json

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
  (NYSE TICK / breadth is NOT owned by the current Chinese-futures corpus and
  is NOT part of the source-pinned 4-step Holy Grail rules).
- No purchase/subscription/authentication; official free/public unauthenticated
  source material only. The official Articles index (lindaraschke.net/articles/),
  re-verified with HTTP 200 on 2026-08-20, enumerates exactly the same free/public
  PDFs already in the accepted screen bundle; no additional official free/public
  pre-2024 Raschke article directly resolves an open semantic field. Official
  videos are YouTube-hosted and blocked by 403 in the recorded environment; they
  were NOT circumvented.
- The task does NOT draft a Playbook Contract; it returns exactly one decision
  `PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES|NO` and, if YES, a HANDOFF document only
  (no Playbook Contract code is instantiated; Lane B2 is integrated separately).

All used source materials have effective content dates BEFORE 2024-01-01
(before the frozen corpus start), so under Protocol v1.0 section 4 no
source-example date audit is required for the protected windows.

Run:
    python -m tools.run_raschke_holy_grail_semantic_completion_source_only
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

SESSION_ID = "SOURCE_ONLY_RASCHKE_HOLY_GRAIL_SEMANTIC_V1_20260820"
MODEL_IDENTITY = "deepseek-v4-flash"
PROMPT_SPEC_VERSION = "RASCHKE_HOLY_GRAIL_TARGETED_SEMANTIC_COMPLETION_V1"
RETRIEVAL_MODE = "LOCAL_FREE_PUBLIC_RASCHKE_HOLY_GRAIL_SEMANTIC_ONLY"
# Claim Schema v1.0 source identity (the actual source, distinct from the
# bundle id). Claims reference this source plus an approved material_id.
SOURCE_ID = "SRC-RASCHKE"
BUNDLE_ID = "SB-RASCHKE-HOLY-GRAIL-SEMANTIC-V1"
BUNDLE_NAME = (
    "Official free/public Linda Bradford Raschke Holy Grail targeted "
    "semantic-completion bundle - reuses the accepted Raschke screen materials "
    "that anchor the RASCHKE_HOLY_GRAIL_PULLBACK family (strong-trend / ADX "
    "context + pullback to 20-period EMA); no new material added"
)
CREATED_AT = "2026-08-20T00:00:00Z"

BASE_BUNDLE_REFERENCE = {
    "base_bundle_id": "SB-RASCHKE-PUBLIC-SCREEN-V1",
    "base_bundle_hash": "7b11a8f1516696e2e54f9dc0ee4d7785f8f1cd9dad06d52abe15378edd2633bd",
    "note": (
        "This semantic-completion bundle reuses the exact accepted source screen "
        "bundle materials that anchor the Holy Grail / pullback family. The official "
        "Articles index (lindaraschke.net/articles/), re-verified with HTTP 200 on "
        "2026-08-20, enumerates exactly the same free/public PDFs already in the "
        "accepted bundle (Trade Trends, Trading Insights, Traders Toolbox, "
        "Multi-Market Traders Rule, The Rituals of Trading, Short Term Trading "
        "Strategies, Maintain your Mindset, Who are You?, Everything About Electronic "
        "Trading, The Discerning Trader, Trading Style and Daily Market Regimen); no "
        "additional official free/public pre-2024 Raschke article directly resolves an "
        "open semantic field (notably the EMA price input, which is NOT_PINNED). "
        "Official videos/interviews are YouTube-hosted and blocked by 403 in the "
        "recorded environment (no circumvention). Therefore no new material is added."
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
    "not use outcomes to select any formula/parameter variant."
)

RETENTION_BOUNDARY = (
    "Raw PDFs and full extracted article text were processed only in a local temp "
    "directory OUTSIDE the repository and were not committed. Only attributable short "
    "excerpts and concise paraphrases needed for claim traceability are recorded. "
    "Anchors point to the canonical official public URLs on lindaraschke.net. "
    "On 2026-08-20 the official Articles index and the Holy Grail article URLs were "
    "re-verified as free/public unauthenticated (HTTP 200); no raw content was "
    "committed."
)

SELECTION_CRITERIA = [
    "reuses the exact accepted Raschke screen bundle (SB-RASCHKE-PUBLIC-SCREEN-V1) materials that anchor the RASCHKE_HOLY_GRAIL_PULLBACK family",
    "official lindaraschke.net free/public article archive / TRACEABLE_ORIGINAL",
    "free/public/unauthenticated access state (re-verified by direct HTTP 200 fetch on 2026-08-20)",
    "effective content date before 2024-01-01 (before the frozen corpus start)",
    "official Articles index re-checked on 2026-08-20 (HTTP 200): enumerates exactly the same free/public PDFs already in the accepted bundle; no additional official free/public pre-2024 article directly resolves an open semantic field, so no new material is added",
    "official videos/interviews are YouTube-hosted and blocked by 403 in the recorded environment; no circumvention; official free article/text material used",
    "stable attributable official URL, title, and publication date",
    "material materially anchors a required semantic field of the Holy Grail / pullback family (trend/ADX context, 20-period EMA, pullback touch, entry trigger, initial stop at swing low, trail/exit, no-trade/failure, timeframe/instrument scope)",
    "not broadened into unrelated third-party summaries or paid material",
    "not selected by expected historical performance"
]

OPTIONAL_PAID_CANDIDATES = [
    {
        "source_identity": "Trading Sardines: Lessons in the Markets from a Lifelong Trader (Linda Bradford Raschke; 2015 book, ISBN 9781532395622)",
        "access_class": "PAID_BOOK (not purchased; listed for awareness only)",
        "evidence_gap_it_could_fill": "Potential additional explicit EMA price-input / trailing-mechanics / exit language for the Holy Grail pullback family.",
        "why_it_might_matter": "Raschke's own book may contain deeper trading-loop semantics than the short official free articles.",
    },
    {
        "source_identity": "Street Smarts: High Probability Short-Term Trading Strategies (Raschke & Connors; book)",
        "access_class": "PAID_BOOK (not purchased; listed for awareness only)",
        "evidence_gap_it_could_fill": "Deeper source-pinned semantics for the Holy Grail pattern referenced in the 1997 AIQ interview (lineage shared with Larry Connors; not independent confirmation).",
        "why_it_might_matter": "The 1997 AIQ interview references the Holy Grail pattern from this book with more detail than the free article.",
    },
    {
        "source_identity": "NYSE TICK / advance-decline breadth data (US market internals) referenced throughout the interviews",
        "access_class": "PAID_OR_SUBSCRIPTION_DATA (not purchased; listed for awareness only)",
        "evidence_gap_it_could_fill": "TICK-based pullback-buying context ('If the TICKs are making new highs, I'll look to buy the pullbacks'); NOT part of the source-pinned 4-step Holy Grail rules.",
        "why_it_might_matter": "The source's TICK/breadth momentum read is not in the Chinese-futures corpus; it is not an OHLCV proxy and is not required by the 4-step rules.",
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
        "diversity_role": "PRIMARY material for the Holy Grail 4-step buy rules; no-trade (middle of range); impulse/thrust cue list; stop process; failure example (Eaton Corp); lineage reference to the Raschke & Connors 'Street Smarts' book",
        "content_note": (
            "AIQ Opening Bell, Vol 6, Issue 8, August 1997. Interview by David Vomund. "
            "Holy Grail buy rules (sells reversed): 1. The 14-period ADX must initially "
            "be greater than 30 and rising. 2. Look for a retracement in price to the "
            "20-period exponential moving average, usually accompanied by a turndown in "
            "ADX. 3. When price touches the 20-period moving average, put a buy stop "
            "above the high of the previous bar. 4. Once filled, enter a protective sell "
            "stop at the newly formed swing low. Trail stops as profits grow. Also: "
            "'The worst thing you can do in terms of market timing is to buy in the "
            "middle of a trading range. Either buy new highs, or buy pullbacks...'; "
            "'Moves often start in either direction with an impulse and a thrust. It may "
            "be a range expansion, an increase in standard deviation, a breakaway gap, "
            "or even a failure to make a lower low'; stop process ('Most often, I'll get "
            "out if the market fails to do what I thought it would do'); failure example "
            "Eaton Corp ('no reason to be in this trade'). The interview references the "
            "Holy Grail pattern from the Raschke & Connors book 'Street Smarts'; the "
            "pattern lineage is shared with Larry Connors, not independent confirmation."
        ),
    },
    {
        "material_id": "SR-V0-M02",
        "canonical_title": "The Discerning Trader: Linda Bradford Raschke",
        "source_publication": "Technical Analysis of Stocks & Commodities (V.11:9)",
        "content_type": "official interview (Thom Hartle; pullback to 20-period EMA; ADX no-trade rules; prior-day levels)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/Discerning-trader.pdf",
        "publication_date": "1993-09",
        "effective_content_date": "1993-09",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "Raschke's own stated pullback-in-trend framework: 'If there is a trend, I'll try to always look for buying a pullback to a moving average... I personally use a 20-period exponential moving average on all my markets'; ADX no-trade/fade rules (ADX<20 declining avoid; ADX>32 rising do not fade)",
        "content_note": (
            "Stocks & Commodities V.11:9 (360-366), 1993, interview by Thom Hartle. "
            "Raschke's own stated pullback framework: 'If there is a trend, I'll try to "
            "always look for buying a pullback to a moving average... I personally use a "
            "20-period exponential moving average on all my markets.' ADX no-trade/fade "
            "rules: 'I avoid the markets where the ADX falls below 20 and is declining... "
            "I will not fade a market... where the ADX is above 32 and rising.' Prior-day "
            "high/low as reference points. This material supplies the 20-period EMA "
            "usage statement and the ADX-based no-trade constraints for the Holy Grail "
            "family."
        ),
    },
    {
        "material_id": "SR-V0-M03",
        "canonical_title": "Trading Style and Daily Market Regimen",
        "source_publication": "Active Trader",
        "content_type": "official interview (Mark Etzkorn; trend days; no-trade; failure context)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/raschke0204.pdf",
        "publication_date": "2004-02",
        "effective_content_date": "2004-02",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "no-trade / failure context for the Holy Grail family: 'If I try to guess a breakout, I'm wrong 90 percent of the time' (guess-breakout failure, low-ADX warning)",
        "content_note": (
            "Active Trader, February 2004, interview by Mark Etzkorn (a day with Linda "
            "Raschke, Nov 2003). Used for NO_TRADE / FAILURE_OR_COUNTEREXAMPLE context "
            "for the Holy Grail family: 'If I try to guess a breakout, I'm wrong 90 "
            "percent of the time. I'm a perfect contrary indicator. ... I just know if "
            "it's a low ADX, I'm going to be wrong if I try to guess.' Also: 'In a "
            "down-trending market, an early gap up is a short 95 percent of the time.' "
            "These are no-trade / failure constraints, not entry rules for the Holy "
            "Grail pullback."
        ),
    },
    {
        "material_id": "SR-V0-M04",
        "canonical_title": "The Rituals of Trading",
        "source_publication": "Active Trader",
        "content_type": "official interview (Mark Etzkorn; management/exit; price-based emphasis)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/rituals.pdf",
        "publication_date": "2000-08",
        "effective_content_date": "2000-08",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "management/exit principles for held positions: give-back exit on first reaction/pause; take at least half off at a price objective when continuation uncertain; price-based emphasis ('Ninety percent of what I do is price-based')",
        "content_note": (
            "Active Trader, August 2000, interview by Mark Etzkorn. Used for "
            "EXIT_TRIGGER / PROFIT_TARGET / POST_ENTRY_INVALIDATION management context "
            "for the Holy Grail family: 'The minute the market gives back more than it "
            "should, you get out on the first reaction or pause'; 'If the market reaches "
            "a price objective, and you're really not sure if it's going to continue, "
            "you have to at least take half the position off'; 'Ninety percent of what I "
            "do is price-based. Indicators are just derivatives of price.' These are "
            "qualitative management principles; no numeric exit is pinned."
        ),
    },
    {
        "material_id": "SR-V0-M05",
        "canonical_title": "Traders Toolbox",
        "source_publication": "Active Trader",
        "content_type": "official interview part 2 (Mark Etzkorn; Holy Grail setup across time frames; indicator checklist)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/03/raschke_pt2_0304.pdf",
        "publication_date": "2004-03",
        "effective_content_date": "2004-03",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "PRIMARY material for the Holy Grail setup across time frames: 'When the market breaks out of an extended trading range and makes new momentum highs, there is a sequence that typically unfolds. Price first pulls back to the 20-bar EMA... then the same retracement will occur on the 30-minute chart, then the 60-minute chart, then the 120-minute time frame. By then you should be looking for a top. But each retracement has to be preceded by a 14-bar ADX reading above 30 on that time frame'; indicator checklist (14-period ADX; 20-period EMA; closing breadth / TICK / put-call as unavailable-input boundaries)",
        "content_note": (
            "Active Trader, March 2004, interview by Mark Etzkorn (follow-up). PRIMARY "
            "material for the Holy Grail setup across time frames: 'When the market "
            "breaks out of an extended trading range and makes new momentum highs, there "
            "is a sequence that typically unfolds. Price first pulls back to the 20-bar "
            "EMA... then the same retracement will occur on the 30-minute chart, then "
            "the 60-minute chart, then the 120-minute time frame. By then you should be "
            "looking for a top. But each retracement has to be preceded by a 14-bar ADX "
            "reading above 30 on that time frame.' Indicator checklist includes 14-period "
            "ADX and 20-period EMA; closing breadth (10-period SMA of NYSE advancers "
            "minus decliners), TICK/TIKI, and put-call ratio are US internals NOT owned "
            "by the Chinese-futures corpus (unavailable-input boundary, not proxied)."
        ),
    },
]

# ---------------------------------------------------------------------------
# 27 targeted semantic resolutions (source-only)
# ---------------------------------------------------------------------------

# claim_status uses the canonical EXPLICIT | INFERRED | UNKNOWN:
#   EXPLICIT  -> the source explicitly states the semantic content
#   INFERRED  -> project/AI interpretation or project transfer hypothesis
#   UNKNOWN   -> the source provides no defining semantics (NOT_PINNED)
SEMANTIC_RESOLUTIONS = [
    {
        "claim_id": "C-RAS-HG-SEM-001",
        "semantic_field": "TREND_CONTEXT_DEFINITION",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "MARKET_CONTEXT",
        "material_id": "SR-V0-M05",
        "source_anchor": "SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP; SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "'When the market breaks out of an extended trading range and makes new "
            "momentum highs, there is a sequence that typically unfolds. Price first "
            "pulls back to the 20-bar EMA...' (SR-V0-M05); Holy Grail buy step 1: 'The "
            "14-period ADX must initially be greater than 30 and rising' (SR-V0-M01)."
        ),
        "source_context_note": (
            "The trend context for the pullback has two explicit components: (a) an "
            "ADX>30-and-rising filter (explicit numeric, SR-V0-M01 step 1 and SR-V0-M05 "
            "'14-bar ADX reading above 30 on that time frame'), and (b) a qualitative "
            "market-structure context ('breaks out of an extended trading range and "
            "makes new momentum highs', SR-V0-M05). The ADX filter is explicit; the "
            "extended-range/momentum-highs structure is qualitative and not numerically "
            "defined."
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: the ADX>30-and-rising filter is explicit, but the "
            "'extended trading range breakout / new momentum highs' market-structure "
            "definition is qualitative and not numerically pinned."
        ),
        "ambiguity_notes": "No numeric definition of 'extended trading range' or 'new momentum highs' in the source.",
        "source_observation_surface": "14-period ADX (OHLC-derived), price position relative to a trading range / momentum highs",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "ADX and price bars derivable from owned OHLCV; range/momentum-highs boundary needs an interpreted convention (INFERRED)",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-002",
        "semantic_field": "ADX_PERIOD",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "'The 14-period ADX must initially be greater than 30 and rising' "
            "(SR-V0-M01 step 1); 'each retracement has to be preceded by a 14-bar ADX "
            "reading above 30 on that time frame' (SR-V0-M05)."
        ),
        "source_context_note": (
            "The ADX period is 14 in both accepted source statements (SR-V0-M01 '14-"
            "period ADX' and SR-V0-M05 '14-bar ADX')."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: the ADX period is explicitly stated as 14 in two "
            "accepted source materials."
        ),
        "ambiguity_notes": "none for the period value; the exact ADX smoothing formula (standard Wilder) is the conventional indicator definition, not re-stated by the source",
        "source_observation_surface": "14-period ADX (OHLC-derived)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "ADX derivable from owned OHLCV",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-003",
        "semantic_field": "ADX_THRESHOLD",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "'The 14-period ADX must initially be greater than 30 and rising' "
            "(SR-V0-M01 step 1); 'each retracement has to be preceded by a 14-bar ADX "
            "reading above 30 on that time frame' (SR-V0-M05)."
        ),
        "source_context_note": (
            "The Holy Grail entry ADX threshold is > 30 in both accepted source "
            "statements. The separate SR-V0-M02 no-trade/fade values (avoid ADX below 20 "
            "and declining; do not fade ADX above 32 and rising) are NO_TRADE "
            "constraints recorded under NO_TRADE, not the Holy Grail entry filter."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: the entry-filter ADX threshold is explicitly stated as "
            "greater than 30 / above 30 in two accepted source materials; no source "
            "conflict for the entry threshold."
        ),
        "ambiguity_notes": "'greater than 30' vs 'above 30' are the same threshold; strict inequality semantics are conventional",
        "source_observation_surface": "14-period ADX level (OHLC-derived)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "ADX derivable from owned OHLCV",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-004",
        "semantic_field": "ADX_RISING_OR_LEVEL_REQUIREMENT",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "'The 14-period ADX must initially be greater than 30 and rising' "
            "(SR-V0-M01 step 1). Holy Grail buy step 2 adds: the retracement to the "
            "20-period EMA is 'usually accompanied by a turndown in ADX.'"
        ),
        "source_context_note": (
            "The source requires the ADX to be BOTH greater than 30 AND rising "
            "(conjunction) at the trend-initiation stage ('initially'). Step 2 notes the "
            "retracement is 'usually accompanied by a turndown in ADX', which describes "
            "the pullback phase. The level+rising requirement is explicit; the 'rising' "
            "slope measurement window is not numerically defined."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: the requirement (level > 30 AND rising) is an explicit "
            "source statement. The exact 'rising' slope measurement window is a "
            "representable INFERRED project convention, and the step-2 'turndown in ADX "
            "during the retracement' is a qualitative descriptive nuance."
        ),
        "ambiguity_notes": "'rising' slope measurement window is not numerically defined (INFERRED convention); step-2 'usually accompanied by a turndown in ADX' is qualitative",
        "source_observation_surface": "14-period ADX level and slope (OHLC-derived)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "ADX derivable from owned OHLCV; slope window is an INFERRED convention",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-005",
        "semantic_field": "MOVING_AVERAGE_TYPE",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M02:discerning-trader:section:PULLBACK_TO_MA; SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "'...retracement in price to the 20-period exponential moving average' "
            "(SR-V0-M01 step 2); 'I personally use a 20-period exponential moving "
            "average on all my markets' (SR-V0-M02); 'Price first pulls back to the "
            "20-bar EMA' (SR-V0-M05)."
        ),
        "source_context_note": (
            "The moving average is an EXPONENTIAL moving average (EMA) in all three "
            "accepted source statements ('20-period exponential moving average' in "
            "SR-V0-M01 and SR-V0-M02; '20-bar EMA' in SR-V0-M05)."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: the moving-average type (exponential) is explicitly and "
            "consistently stated across three accepted source materials."
        ),
        "ambiguity_notes": "none for type; the EMA smoothing formula is the conventional indicator definition",
        "source_observation_surface": "20-period exponential moving average (price-derived)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "EMA derivable from owned OHLCV",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-006",
        "semantic_field": "MOVING_AVERAGE_PERIOD",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M02:discerning-trader:section:PULLBACK_TO_MA; SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "'20-period exponential moving average' (SR-V0-M01 step 2, SR-V0-M02); "
            "'20-bar EMA' (SR-V0-M05)."
        ),
        "source_context_note": (
            "The EMA period is 20 in all three accepted source statements."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: the EMA period is explicitly stated as 20 across three "
            "accepted source materials; no source conflict."
        ),
        "ambiguity_notes": "none for the period value",
        "source_observation_surface": "20-period exponential moving average (price-derived)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "EMA derivable from owned OHLCV",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-007",
        "semantic_field": "MOVING_AVERAGE_PRICE_INPUT",
        "semantic_classification": "NOT_PINNED",
        "claim_status": "UNKNOWN",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M02:discerning-trader:section:PULLBACK_TO_MA; SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "The source states '20-period exponential moving average' (SR-V0-M01, "
            "SR-V0-M02) and '20-bar EMA' (SR-V0-M05) WITHOUT specifying the price input "
            "(close vs typical price vs high/low)."
        ),
        "source_context_note": (
            "None of the accepted source materials states the price basis of the "
            "20-period EMA. The conventional indicator default is closing price, but "
            "that is a project convention, not a source statement."
        ),
        "classification_rationale": (
            "NOT_PINNED: the source does not state the EMA price input. Any project "
            "choice (e.g., standard close-based EMA) is a clearly labeled INFERRED "
            "project convention, never presented as a source claim."
        ),
        "ambiguity_notes": "EMA price basis is a critical setup input left open by the source; must be recorded as INFERRED at operationalization",
        "source_observation_surface": "price series used to compute the 20-period EMA",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "price basis is an INFERRED project convention (all candidate price inputs are owned in OHLCV)",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-008",
        "semantic_field": "PULLBACK_DEFINITION",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M02:discerning-trader:section:PULLBACK_TO_MA",
        "source_excerpt_short_or_paraphrase": (
            "'Look for a retracement in price to the 20-period exponential moving "
            "average' (SR-V0-M01 step 2); 'If there is a trend, I'll try to always look "
            "for buying a pullback to a moving average' (SR-V0-M02)."
        ),
        "source_context_note": (
            "The pullback target (the 20-period EMA) is explicit. The pullback "
            "structure/magnitude (leg count, depth, duration) that qualifies as 'a "
            "retracement/pullback' is not defined by the source."
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: the pullback target (20-period EMA) is explicit, but the "
            "definition of what qualifies as a pullback (structure/depth/duration) is "
            "not numerically pinned."
        ),
        "ambiguity_notes": "No source definition of pullback leg count, depth, or duration; only the EMA-touch target is explicit",
        "source_observation_surface": "price retracement toward the 20-period EMA",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "pullback structure is an interpreted convention (INFERRED); price/EMA derivable from OHLCV",
        "lineage_id": "L-RAS-PULLBACK",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-009",
        "semantic_field": "PULLBACK_TOUCH_OR_PENETRATION_RULE",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "'When price touches the 20-period moving average, put a buy stop above the "
            "high of the previous bar' (SR-V0-M01 step 3)."
        ),
        "source_context_note": (
            "The trigger condition is price TOUCHING the 20-period EMA. The source does "
            "not define whether 'touches' means an intrabar low/high touch, a close "
            "touch, or whether penetration through the EMA also counts."
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: the touch condition (price touches the 20-period EMA) is "
            "explicit, but the bar-level definition of 'touches' (intrabar vs close vs "
            "penetration) is not pinned."
        ),
        "ambiguity_notes": "Bar-level 'touch' semantics (intrabar low/high vs close vs penetration) not defined by the source",
        "source_observation_surface": "price proximity to the 20-period EMA",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "touch definition is an interpreted convention (INFERRED); price/EMA derivable from OHLCV",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-010",
        "semantic_field": "ENTRY_TRIGGER",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "'When price touches the 20-period moving average, put a buy stop above the "
            "high of the previous bar' (SR-V0-M01 step 3)."
        ),
        "source_context_note": (
            "The entry trigger is explicit: when price touches the 20-period EMA, place "
            "a buy stop above the high of the previous bar; the entry occurs when that "
            "buy stop is filled."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: both the touch condition and the stop-fill trigger are "
            "explicit source statements."
        ),
        "ambiguity_notes": "'the previous bar' is the bar preceding the touch bar; whether the stop level updates on subsequent bars is not stated",
        "source_observation_surface": "price touch of 20-period EMA; high of the previous bar",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (price + EMA derivable from owned OHLCV)",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-011",
        "semantic_field": "ENTRY_ORDER_TYPE",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "'...put a buy stop above the high of the previous bar' (SR-V0-M01 step 3)."
        ),
        "source_context_note": (
            "The entry order type is a STOP order (buy stop for the long; sell stop for "
            "the short side). The exact subtype (stop-market vs stop-limit) is an "
            "operational detail not stated by the source."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: 'buy stop' / 'sell stop' pins the entry order type as "
            "stop orders. The stop-market vs stop-limit subtype is a representable "
            "operationalization detail."
        ),
        "ambiguity_notes": "stop-market vs stop-limit subtype not source-pinned",
        "source_observation_surface": "order semantics (stop entry)",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "exact order subtype is an INFERRED project convention",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-012",
        "semantic_field": "ENTRY_OFFSET",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "'...put a buy stop above the high of the previous bar' (SR-V0-M01 step 3)."
        ),
        "source_context_note": (
            "The reference level is explicit: above the high of the previous bar. The "
            "exact tick/price offset above that high is not stated by the source. (The "
            "separate Three-Day Unfilled Gap Reversal's 'one tick above' language in "
            "SR-V0-M01 belongs to a different family and does not transfer.)"
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: the reference level (above the previous bar's high) is "
            "explicit; the exact offset above it is not pinned."
        ),
        "ambiguity_notes": "tick offset above the previous-bar high is not source-pinned",
        "source_observation_surface": "previous-bar high (price)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "offset is an INFERRED project convention (tick size available from governed metadata)",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-013",
        "semantic_field": "LONG_RULE",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "Holy Grail buy rules: 1. 'The 14-period ADX must initially be greater than "
            "30 and rising.' 2. 'Look for a retracement in price to the 20-period "
            "exponential moving average, usually accompanied by a turndown in ADX.' 3. "
            "'When price touches the 20-period moving average, put a buy stop above the "
            "high of the previous bar.' 4. 'Once filled, enter a protective sell stop at "
            "the newly formed swing low. Trail stops as profits grow.' (SR-V0-M01)"
        ),
        "source_context_note": (
            "The long side is a complete explicit 4-step rule set: trend/ADX context, "
            "pullback to the 20-period EMA, buy-stop entry above the previous bar's "
            "high, protective sell stop at the newly formed swing low, trail as profits "
            "grow."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: the 4-step long rules are explicit source statements in "
            "the accepted material."
        ),
        "ambiguity_notes": "swing-low identification and trail mechanics are not mechanically defined (INFERRED at operationalization); EMA price input NOT_PINNED",
        "source_observation_surface": "ADX, 20-period EMA, bar highs, swing lows (all price/OHLC-derived)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "swing-low identification and EMA price basis are INFERRED conventions; no unavailable input",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-014",
        "semantic_field": "SHORT_RULE",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "Holy Grail buy rules are stated with the header '(sells reversed)' "
            "(SR-V0-M01): the short side is the mirror image of the 4-step buy rules."
        ),
        "source_context_note": (
            "The source explicitly states the short side reverses the buy rules "
            "('sells reversed'). The mirror operationalization (sell stop below the "
            "previous bar's low; protective buy stop at the newly formed swing high) is "
            "the source's own reversal statement."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: 'sells reversed' is an explicit source statement that "
            "the short side mirrors the long rules. The exact mirror construction is a "
            "direct reading of that statement."
        ),
        "ambiguity_notes": "'reversed' mirror construction is the source's own statement but the step-by-step short wording is not separately spelled out",
        "source_observation_surface": "ADX, 20-period EMA, bar lows, swing highs (all price/OHLC-derived)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none beyond the same INFERRED conventions as the long side",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-015",
        "semantic_field": "INITIAL_STOP",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "RISK_PROCESS",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "'Once filled, enter a protective sell stop at the newly formed swing low' "
            "(SR-V0-M01 step 4)."
        ),
        "source_context_note": (
            "The initial stop is source-pinned: a protective sell stop placed at the "
            "newly formed swing low immediately after the long entry fill (mirror: "
            "protective buy stop at the newly formed swing high for the short). The "
            "mechanical identification of a 'swing low/high' is not defined by the "
            "source (INFERRED pivot convention at operationalization)."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: the initial stop rule (protective sell stop at the "
            "newly formed swing low) is an explicit source statement. This is the key "
            "contrast with the NR7 family, whose initial stop was NOT_PINNED. Swing-low "
            "identification is a representable INFERRED operationalization."
        ),
        "ambiguity_notes": "'newly formed swing low' mechanical identification is not source-pinned (INFERRED pivot definition)",
        "source_observation_surface": "newly formed swing low (price)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "swing-low identification is an INFERRED convention; prices owned",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-016",
        "semantic_field": "POST_ENTRY_INVALIDATION",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "INVALIDATION",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M04:rituals:section:MANAGEMENT_EXIT",
        "source_excerpt_short_or_paraphrase": (
            "'Once filled, enter a protective sell stop at the newly formed swing low' "
            "(SR-V0-M01 step 4); 'The minute the market gives back more than it should, "
            "you get out on the first reaction or pause' (SR-V0-M04)."
        ),
        "source_context_note": (
            "The hard post-entry invalidation is the protective stop at the newly formed "
            "swing low (source-stated): price trading back below the swing low "
            "invalidates the pullback-in-trend thesis. The SR-V0-M04 give-back rule adds "
            "a qualitative management-based invalidation layer ('gives back more than it "
            "should')."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: the protective stop at the newly formed swing low is an "
            "explicit source-stated post-entry invalidation boundary. The SR-V0-M04 "
            "give-back rule is qualitative management context (PARTIALLY_PINNED "
            "nuance), not a conflicting rule. This is the key contrast with the NR7 "
            "family, whose post-entry invalidation was NOT_PINNED."
        ),
        "ambiguity_notes": "'gives back more than it should' (SR-V0-M04) is qualitative; the hard swing-low stop is the pinned invalidation",
        "source_observation_surface": "newly formed swing low; price give-back behavior",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "swing-low identification is an INFERRED convention; prices owned",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-017",
        "semantic_field": "STOP_ADJUSTMENT_IF_ANY",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "MANAGEMENT",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "'Trail stops as profits grow' (SR-V0-M01 step 4)."
        ),
        "source_context_note": (
            "The trailing concept is explicit: the stop is adjusted to trail as profits "
            "grow. The trailing mechanism (how the stop is moved - swing-based, "
            "MA-based, fixed-distance, etc.) is not pinned by the source."
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: the trailing concept is explicit ('Trail stops as "
            "profits grow'), but the trailing mechanics are not defined and require a "
            "clearly labeled INFERRED project convention."
        ),
        "ambiguity_notes": "trailing mechanics (swing/MA/distance-based) not source-pinned",
        "source_observation_surface": "profit progress vs current stop level",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "trail mechanics are an INFERRED project convention",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-018",
        "semantic_field": "PROFIT_TARGET",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "EXIT",
        "material_id": "SR-V0-M04",
        "source_anchor": "SR-V0-M04:rituals:section:MANAGEMENT_EXIT; SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "'If the market reaches a price objective, and you're really not sure if "
            "it's going to continue, you have to at least take half the position off' "
            "(SR-V0-M04); 'By then you should be looking for a top' (SR-V0-M05, after "
            "the multi-timeframe retracement sequence)."
        ),
        "source_context_note": (
            "No numeric price target is pinned. The source gives a qualitative "
            "management principle (take at least half off at a price objective when "
            "continuation is uncertain) and a multi-timeframe context (looking for a "
            "top after the retracement sequence)."
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: the take-half-at-a-price-objective principle is an "
            "explicit source statement, but no numeric profit target is pinned; any "
            "target convention is an INFERRED project convention."
        ),
        "ambiguity_notes": "'price objective' is not numerically defined in the source",
        "source_observation_surface": "price objective / continuation behavior",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "price-objective definition is an INFERRED project convention",
        "lineage_id": "L-RAS-PROCESS",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-019",
        "semantic_field": "EXIT_TRIGGER",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "EXIT",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M04:rituals:section:MANAGEMENT_EXIT",
        "source_excerpt_short_or_paraphrase": (
            "'Trail stops as profits grow' (SR-V0-M01 step 4); 'The minute the market "
            "gives back more than it should, you get out on the first reaction or "
            "pause' (SR-V0-M04); 'Most often, I'll get out if the market fails to do "
            "what I thought it would do' (SR-V0-M01 stop process)."
        ),
        "source_context_note": (
            "The source supplies multiple qualitative exit triggers: trailing stops as "
            "profits grow (SR-V0-M01), exit on the first reaction/pause when price "
            "gives back more than it should (SR-V0-M04), and a discretionary stop "
            "process ('get out if the market fails to do what I thought it would do', "
            "SR-V0-M01). None is numerically pinned."
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: exit triggers are present and source-attributed but "
            "qualitative; no deterministic numeric exit trigger is pinned. The exit is "
            "NOT missing - it is present with source-faithful qualitative semantics."
        ),
        "ambiguity_notes": "all exit triggers are qualitative; no deterministic numeric trigger pinned",
        "source_observation_surface": "profit trail, price give-back, position behavior vs expectation",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "exit mechanics are INFERRED project conventions",
        "lineage_id": "L-RAS-PROCESS",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-020",
        "semantic_field": "TIME_EXIT_IF_ANY",
        "semantic_classification": "NOT_PINNED",
        "claim_status": "UNKNOWN",
        "claim_category": "EXIT",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "No time-based exit is stated for the Holy Grail pullback family in the "
            "accepted source material."
        ),
        "source_context_note": (
            "The accepted source bundle contains no time-based exit (e.g., end-of-"
            "session, N-bars-hold, end-of-day) for the Holy Grail pullback rules. "
            "Time-based exits appear for other families (e.g., the gap-reversal "
            "three-session cancellation), which do not transfer."
        ),
        "classification_rationale": (
            "NOT_PINNED: the source provides no time-based exit semantics for this "
            "family; any such rule would be an invented critical rule and is therefore "
            "not represented."
        ),
        "ambiguity_notes": "no source time-exit semantics; must remain NOT_PINNED rather than guessed",
        "source_observation_surface": "not applicable (no source statement)",
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "not applicable - no source time-exit semantics",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-021",
        "semantic_field": "REENTRY_RULE_IF_ANY",
        "semantic_classification": "NOT_PINNED",
        "claim_status": "UNKNOWN",
        "claim_category": "MANAGEMENT",
        "material_id": "SR-V0-M05",
        "source_anchor": "SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "No explicit re-entry rule is stated. SR-V0-M05 describes a multi-timeframe "
            "sequence: 'Price first pulls back to the 20-bar EMA... then the same "
            "retracement will occur on the 30-minute chart, then the 60-minute chart, "
            "then the 120-minute time frame.'"
        ),
        "source_context_note": (
            "The SR-V0-M05 multi-timeframe sequence describes the same setup re-"
            "appearing on higher timeframes (a context observation), not a re-entry "
            "rule for a single position after an exit. No source re-entry rule is given."
        ),
        "classification_rationale": (
            "NOT_PINNED: no explicit re-entry rule exists in the source. The "
            "multi-timeframe sequence is recorded as context, not as a re-entry rule."
        ),
        "ambiguity_notes": "multi-timeframe retracement sequence is context, not a re-entry rule; any re-entry rule would be an invented critical rule",
        "source_observation_surface": "not applicable (no source re-entry statement)",
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "not applicable - no source re-entry semantics",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-022",
        "semantic_field": "NO_TRADE",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "NO_TRADE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:MARKET_TIMING; SR-V0-M02:discerning-trader:section:ADX_RULES; SR-V0-M03:raschke0204:section:BREAKOUT_GUESS_FAILURE",
        "source_excerpt_short_or_paraphrase": (
            "'The worst thing you can do in terms of market timing is to buy in the "
            "middle of a trading range. Either buy new highs, or buy pullbacks...' "
            "(SR-V0-M01); 'I avoid the markets where the ADX falls below 20 and is "
            "declining... I will not fade a market... where the ADX is above 32 and "
            "rising' (SR-V0-M02); 'If I try to guess a breakout, I'm wrong 90 percent "
            "of the time' (SR-V0-M03)."
        ),
        "source_context_note": (
            "Explicit no-trade constraints are present: do not buy in the middle of a "
            "trading range (buy new highs or pullbacks); avoid markets with ADX below "
            "20 and declining; do not fade a market with ADX above 32 and rising; do "
            "not guess a breakout. The operational boundaries (range definition, ADX "
            "slope, 'middle') are not numerically defined."
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: the no-trade statements are explicit but their "
            "operational boundaries (trading-range definition, ADX rising/declining "
            "measure, 'middle of range') are not numerically pinned."
        ),
        "ambiguity_notes": "'middle of a trading range' boundary and ADX slope measurement are not numerically defined",
        "source_observation_surface": "price position relative to a trading range; ADX level/slope",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "range/slope definitions are INFERRED conventions",
        "lineage_id": "L-RAS-TIMING",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-023",
        "semantic_field": "FAILURE_OR_COUNTEREXAMPLE",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "FAILURE_OR_COUNTEREXAMPLE",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M03:raschke0204:section:BREAKOUT_GUESS_FAILURE",
        "source_excerpt_short_or_paraphrase": (
            "Eaton Corp Holy Grail example (SR-V0-M01): 'no reason to be in this trade' "
            "- a source-acknowledged no-trade/failure case for the pullback pattern; "
            "'If I try to guess a breakout, I'm wrong 90 percent of the time' "
            "(SR-V0-M03)."
        ),
        "source_context_note": (
            "The source acknowledges a failure/no-trade case for the pullback pattern "
            "(Eaton Corp: 'no reason to be in this trade') and a guess-breakout failure "
            "statement. The detail is limited; no systematic loss ledger is in the "
            "source (source-quality limitation, recorded not manufactured)."
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: a source-attributed failure/no-trade example is present "
            "(Eaton Corp), but the detail is limited and no systematic failure ledger "
            "exists in the source."
        ),
        "ambiguity_notes": "limited failure detail; no systematic loss ledger in the source",
        "source_observation_surface": "Eaton Corp price/context example; breakout-guess failure",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "none; failure detail is a source-quality limitation, not an unavailable input",
        "lineage_id": "L-RAS-FAILURE",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-024",
        "semantic_field": "TIMEFRAME_SCOPE",
        "semantic_classification": "PARTIALLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "APPLICABILITY",
        "material_id": "SR-V0-M05",
        "source_anchor": "SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP",
        "source_excerpt_short_or_paraphrase": (
            "'Price first pulls back to the 20-bar EMA... then the same retracement "
            "will occur on the 30-minute chart, then the 60-minute chart, then the "
            "120-minute time frame... each retracement has to be preceded by a 14-bar "
            "ADX reading above 30 on that time frame' (SR-V0-M05)."
        ),
        "source_context_note": (
            "The Holy Grail setup is explicitly stated to apply across time frames: the "
            "pullback-to-EMA sequence repeats on the base chart and then on 30-, 60-, "
            "and 120-minute charts, each retracement preceded by a 14-bar ADX>30 on "
            "that timeframe. The SR-V0-M01 rules are period-based (14-period ADX, "
            "20-period EMA) and therefore bar-timeframe-agnostic. No single operating "
            "timeframe is uniquely pinned for the whole loop."
        ),
        "classification_rationale": (
            "PARTIALLY_PINNED: multi-timeframe applicability is explicit, but no single "
            "operating timeframe is uniquely pinned for the full trading loop."
        ),
        "ambiguity_notes": "no single operating timeframe is pinned for the whole loop; multi-timeframe sequence is explicit",
        "source_observation_surface": "base chart plus 30/60/120-minute charts (all derivable from 1-minute OHLCV)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (all timeframes derivable from owned 1-minute OHLCV)",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-025",
        "semantic_field": "INSTRUMENT_SCOPE",
        "semantic_classification": "EXPLICITLY_PINNED",
        "claim_status": "EXPLICIT",
        "claim_category": "APPLICABILITY",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES; SR-V0-M02:discerning-trader:section:PULLBACK_TO_MA",
        "source_excerpt_short_or_paraphrase": (
            "1997 Holy Grail examples are US equities (Eaton Corp; CHV/CMZ/AXP/ETN); "
            "SR-V0-M05 is an S&P index context; SR-V0-M02 states 'I personally use a "
            "20-period exponential moving average on all my markets.'"
        ),
        "source_context_note": (
            "SOURCE_INSTRUMENT_SCOPE=US_EQUITIES_AND_US_INDEX (the Holy Grail examples "
            "are US equities and S&P index context). The SR-V0-M02 'on all my markets' "
            "statement is a broad usage statement recorded as lineage context, NOT "
            "counted as explicit commodity-futures support (see COMMODITY_FUTURES_"
            "SCOPE)."
        ),
        "classification_rationale": (
            "EXPLICITLY_PINNED: the source examples are explicitly US equities and US "
            "index context. Commodity-futures support is recorded separately as "
            "UNKNOWN."
        ),
        "ambiguity_notes": "'on all my markets' (SR-V0-M02) is broad and ambiguous; not counted as explicit commodity-futures support",
        "source_observation_surface": "instrument scope statement",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "the source universe is not the current corpus; transfer is a separate INFERRED field",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-026",
        "semantic_field": "COMMODITY_FUTURES_SCOPE",
        "semantic_classification": "NOT_PINNED",
        "claim_status": "UNKNOWN",
        "claim_category": "APPLICABILITY",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "SOURCE_SUPPORTS_COMMODITY_FUTURES=UNKNOWN: no explicit commodity-futures "
            "example or statement applies the Holy Grail pullback rules to commodity "
            "futures in the accepted source material."
        ),
        "source_context_note": (
            "Unlike the NR7 family (which had a September Cocoa commodity-futures "
            "chart), the Holy Grail pullback rules have no commodity-futures anchor in "
            "the accepted material. The SR-V0-M02 'on all my markets' statement is "
            "ambiguous and is not counted as explicit commodity-futures support."
        ),
        "classification_rationale": (
            "NOT_PINNED (UNKNOWN): the source provides no explicit commodity-futures "
            "support statement for the Holy Grail family. Absence of support is not "
            "evidence of failure; it is an unaddressed scope."
        ),
        "ambiguity_notes": "'on all my markets' (SR-V0-M02) is recorded as ambiguous lineage context, not explicit support",
        "source_observation_surface": "not applicable (no explicit commodity-futures statement)",
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "not applicable - no source statement",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "machine_operationalization_status": "NOT_STARTED",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
    },
    {
        "claim_id": "C-RAS-HG-SEM-027",
        "semantic_field": "CURRENT_PROJECT_PRODUCT_TRANSFER",
        "semantic_classification": "INFERRED_PROJECT_TRANSFER",
        "claim_status": "INFERRED",
        "claim_category": "APPLICABILITY",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "source_excerpt_short_or_paraphrase": (
            "Transfer of the Holy Grail pullback rules to cu/al/ni/au/ag/rb is NOT an "
            "explicit source claim."
        ),
        "source_context_note": (
            "SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN. The source scope is US "
            "equities / US index; no explicit statement addresses Chinese futures. Any "
            "Chinese-futures operationalization of the Holy Grail pullback is an "
            "INFERRED project hypothesis and does not inherit source authority "
            "automatically."
        ),
        "classification_rationale": (
            "INFERRED_PROJECT_TRANSFER: any Chinese-futures operationalization is a "
            "separately labeled project hypothesis. 'Works across timeframes' is NOT "
            "interpreted as 'explicitly applies to Chinese cu/al/ni/au/ag/rb'."
        ),
        "ambiguity_notes": "SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN; transfer is INFERRED, never presented as source fact",
        "source_observation_surface": "instrument transfer hypothesis",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "transfer to Chinese futures is an INFERRED project hypothesis",
        "lineage_id": "L-RAS-HOLYGRAIL",
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
            "that anchor the RASCHKE_HOLY_GRAIL_PULLBACK family; see "
            "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json"
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
        "artifact": "HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL",
        "manifest_version": "1.0",
        "bundle_id": BUNDLE_ID,
        "bundle_name": BUNDLE_NAME,
        "canonical_bundle_hash": bundle_hash,
        "selected_on": "2026-08-20",
        "retrieval_mode": RETRIEVAL_MODE,
        "package": "RASCHKE_HOLY_GRAIL_TARGETED_SEMANTIC_COMPLETION_V0_1",
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
            "RASCHKE_HOLY_GRAIL_PULLBACK family (strong-trend / ADX context + pullback "
            "to a 20-period EMA). Selection based on provenance + free/public access + "
            "source-anchor quality + direct relevance to the required semantic fields. "
            "NEVER based on expected trading performance."
        ),
        "no_additional_source_added": {
            "checked_on": "2026-08-20",
            "official_articles_index": "https://lindaraschke.net/articles/",
            "finding": (
                "The official Articles index (re-verified with HTTP 200 on 2026-08-20) "
                "enumerates exactly the same free/public PDFs already in the accepted "
                "screen bundle (Trade Trends, Trading Insights, Traders Toolbox, "
                "Multi-Market Traders Rule, The Rituals of Trading, Short Term Trading "
                "Strategies, Maintain your Mindset, Who are You?, Everything About "
                "Electronic Trading, The Discerning Trader, Trading Style and Daily "
                "Market Regimen). No additional official free/public pre-2024 Raschke "
                "article directly resolves an open semantic field (notably the EMA "
                "price input, which is NOT_PINNED). Official videos/interviews are "
                "YouTube-hosted and blocked by 403 in the recorded environment (no "
                "circumvention). Therefore no new material is added."
            ),
        },
        "access_state": {
            "verified_at": "2026-08-20",
            "all_urls_accessible": True,
            "all_urls_free_public_unauthenticated": True,
            "all_effective_content_dates_before_2024_01_01": True,
            "note": (
                "Official Articles index and Holy Grail article URLs (august1997.pdf, "
                "raschke_pt2_0304.pdf) re-verified via direct HTTP fetch on 2026-08-20 "
                "(HTTP 200, application/pdf); no authentication/cookies used. Raw "
                "content was not committed."
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
        REPO_ROOT / "docs" / "evidence" / "HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json"
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

    # ---- Record the 27 semantic resolutions through the provenance surface -
    for resolution in SEMANTIC_RESOLUTIONS:
        runner.record_claim(_claim_record_for(resolution, session.session_id))

    # ---- C: SOURCE_ONLY session evidence + claim records ------------------
    session_record = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL",
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
            "RASCHKE_HOLY_GRAIL_TARGETED_SEMANTIC_COMPLETION_V1. Targeted source-"
            "semantic completion for the family RASCHKE_HOLY_GRAIL_PULLBACK: resolve "
            "27 semantic fields from the accepted source bundle and return exactly one "
            "decision PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES|NO. No Playbook Contract is "
            "drafted by this session (Lane B2 is integrated separately)."
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
            "family": "RASCHKE_HOLY_GRAIL_PULLBACK",
            "PLAYBOOK_SEMANTICALLY_DRAFTABLE": "YES",
            "decision_rationale": (
                "The source pins the complete trading loop for the Holy Grail pullback: "
                "CONTEXT (14-period ADX > 30 and rising; extended-range breakout + new "
                "momentum highs from SR-V0-M05), SETUP (pullback/retracement to the "
                "20-period exponential moving average), ENTRY (buy stop above the high "
                "of the previous bar when price touches the 20-period EMA), "
                "INITIAL_RISK/INVALIDATION (protective sell stop at the newly formed "
                "swing low - source-pinned, the key contrast with the NR7 negative "
                "result), EXIT (trail stops as profits grow; take at least half off at "
                "a price objective; exit on first reaction/pause when giving back too "
                "much), NO_TRADE (middle-of-range; ADX<20 declining avoid; do not fade "
                "ADX>32 rising; do not guess breakouts), TIMEFRAME (multi-timeframe "
                "explicit: base chart then 30/60/120-minute), INSTRUMENT scope (US "
                "equities/S&P examples; commodity-futures support UNKNOWN). The "
                "remaining gaps (EMA price input NOT_PINNED; swing-low identification; "
                "trailing mechanics; qualitative exits) are representable as clearly "
                "labeled INFERRED project conventions. None of the NO conditions "
                "applies: the initial stop IS pinned, the exit is present (not "
                "missing), the trigger is explicit (not discretionary), there is no "
                "source formula conflict for the entry parameters (14-period ADX>30 and "
                "20-period EMA are consistent across all accepted materials), and no "
                "critical information surface is unavailable (the 30/60/120-minute "
                "charts are derivable from owned 1-minute OHLCV; NYSE TICK/breadth is "
                "NOT part of the 4-step rules)."
            ),
            "primary_blocker": "NONE",
            "initial_stop": "EXPLICITLY_PINNED",
            "post_entry_invalidation": "EXPLICITLY_PINNED",
            "exit_trigger": "PARTIALLY_PINNED",
            "source_supports_commodity_futures": "UNKNOWN",
            "source_supports_current_project_products": "UNKNOWN",
            "NO_CANDIDATE_OUTCOME_DATA_USED": "YES",
        },
        "claims": SEMANTIC_RESOLUTIONS,
    }
    session_path = (
        REPO_ROOT / "docs" / "evidence" / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json"
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
