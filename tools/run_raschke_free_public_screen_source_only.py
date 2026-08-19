"""RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V1 - SOURCE_ONLY driver.

Bounded source screen + claim extraction for Linda Bradford Raschke official
free/public material. This is NOT a backtest, NOT strategy mining, NOT parameter
search, NOT statistical inference, and does NOT create a Playbook Contract.

It uses the actual project SOURCE_ONLY implementation in
`src/research_firewall.py`:

- predeclares the approved public source bundle (official lindaraschke.net free
  article/text material) and computes its canonical bundle hash;
- opens a project-verified SOURCE_ONLY session via
  `SourceOnlyPolicy.open_verified_session(...)`;
- verifies `source_only.is_verified(session_id) == True`;
- executes the protected-outcome denial path once (engineering proof) and
  expects `outcome=DENIED` / `reason=SOURCE_ONLY_TECHNICAL_DENIAL`;
- records each source claim through the bounded
  `SourceOnlyClaimExtractionContext` provenance output surface;
- writes durable JSON evidence artifacts:
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_SCREEN_V0_1.json

HARD BOUNDARIES (frozen authority, do not violate):
- HUMAN_PLAYBOOK_FIRST remains binding. No data-first K-line mining, indicator
  discovery, parameter search, candidate backtests, candidate PnL/returns,
  expectancy, Sharpe, win/loss, equity/drawdown, Validation access,
  historical-final access, or canonical market-outcome calibration.
- No candidate outcome / PnL / backtest / indicator search / chart-pattern
  mining. No project protected-period market-outcome retrieval (the runner has
  no such surface; any request is technically DENIED and audited).
- Source claim != project/AI interpretation != machine operationalization.
  Claim statuses use the canonical EXPLICIT | INFERRED | UNKNOWN.
- No invented thresholds; no fabricated OHLCV proxies for absent inputs
  (NYSE TICK / breadth, put-call ratio, bid-ask order flow, DAX/EuroStoxx
  cross-market are NOT owned by the current Chinese-futures corpus).
- No purchase/subscription/authentication; official free/public unauthenticated
  source material only. Official videos are YouTube-hosted and are blocked by
  403 in the recorded environment; they were NOT circumvented.
- The task does NOT draft a Playbook Contract; it selects at most ONE family for
  a later targeted semantic-completion package.

All selected source materials have effective content dates BEFORE 2024-01-01
(before the frozen corpus start), so under Protocol v1.0 section 4 no
source-example date audit is required for the protected windows.

Run:
    python -m tools.run_raschke_free_public_screen_source_only
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

SESSION_ID = "SOURCE_ONLY_RASCHKE_SCREEN_V1_20260819"
MODEL_IDENTITY = "deepseek-v4-flash"
PROMPT_SPEC_VERSION = "RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V1"
RETRIEVAL_MODE = "LOCAL_FREE_PUBLIC_RASCHKE_SOURCE_SCREEN_ONLY"
BUNDLE_ID = "SB-RASCHKE-PUBLIC-SCREEN-V1"
BUNDLE_NAME = (
    "Official free/public Linda Bradford Raschke source screen bundle - "
    "official lindaraschke.net free article/text material (price/volume/session "
    "compatibility screen)"
)
CREATED_AT = "2026-08-19T00:00:00Z"

EXPOSURE_NOTE = (
    "Model latent historical knowledge cannot be proven absent; this is a disclosed "
    "residual threat-model risk under the frozen protocol. Project protected-period "
    "outcomes (DEVELOPMENT 2024, VALIDATION 2025H1, FINAL_HOLDOUT 2025H2) are "
    "technically unavailable to this SOURCE_ONLY runner: it exposes no project "
    "protected-period market-outcome retrieval surface, and any such request is "
    "technically DENIED and audited. No canonical market data repository, validation "
    "surface, or historical-final surface was exposed to this session. All selected "
    "source materials have effective content dates before 2024-01-01 (before the "
    "frozen corpus start), so no source-example date audit is required for the "
    "protected windows under Protocol v1.0 section 4. The bundled articles are "
    "official source teaching/interview material only; they are not accepted trading "
    "truth and were never selected by expected profitability. Official videos are "
    "YouTube-hosted and were not acquired (recorded environment blocks YouTube media "
    "with 403; no circumvention was attempted). This session performs a bounded "
    "source screen and claim extraction only; it does not draft a Playbook Contract."
)

RETENTION_BOUNDARY = (
    "Raw PDFs and full extracted article text were processed only in a local temp "
    "directory OUTSIDE the repository and were not committed. Only attributable short "
    "excerpts and concise paraphrases needed for claim traceability are recorded. "
    "Anchors point to the canonical official public URLs on lindaraschke.net."
)

# ---------------------------------------------------------------------------
# Source bundle definition (materials only; no redistributed copyrighted content)
# ---------------------------------------------------------------------------

# Eight official free/public articles with an embedded text layer were acquired.
# Three additional official PDFs (SR-V0-M06 ftrader, SR-V0-M07 upstairs,
# SR-V0-M08 Omega) are image-only scans with no embedded text layer; no OCR tool
# is installed (adding one would be a new framework) and they are low-priority
# profile/interview pieces, so they are excluded and recorded in the manifest.
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
        "diversity_role": "market timing rules; no-trade (middle of range); Holy Grail; gap reversal; Wolfe Wave; stop process; failure/counterexample (Eaton Corp)",
        "content_note": (
            "AIQ Opening Bell, Vol 6, Issue 8, August 1997. Interview by David Vomund. "
            "Covers: 'the worst thing you can do in terms of market timing is to buy in "
            "the middle of a trading range. Either buy new highs, or buy pullbacks, but "
            "don't put your capital to work in the middle of a trading range'; moves "
            "often start 'with an impulse and a thrust ... range expansion, an increase "
            "in standard deviation, a breakaway gap, or even a failure to make a lower "
            "low'; Holy Grail buy rules (14-period ADX > 30 and rising; retracement to "
            "20-period EMA; buy stop above high of previous bar; protective sell stop at "
            "newly formed swing low; trail); Three-Day Unfilled Gap Reversal rules; "
            "Wolfe Wave construction rules; stop strategy ('most often, I'll get out if "
            "the market fails to do what I thought it would do'); failure example Eaton "
            "Corp (no reason to be in the trade)."
        ),
    },
    {
        "material_id": "SR-V0-M02",
        "canonical_title": "The Discerning Trader: Linda Bradford Raschke",
        "source_publication": "Technical Analysis of Stocks & Commodities (V.11:9)",
        "content_type": "official interview (Thom Hartle; NR7 breakout; prior-day levels; breakout vs swing mode; ADX rules; 3-10 oscillator; contraction)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/Discerning-trader.pdf",
        "publication_date": "1993-09",
        "effective_content_date": "1993-09",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "NR7/contraction->trend; prior-day high/low reference points; breakout vs swing mode; ADX no-trade rules; pullback to 20 EMA; 3-10 oscillator; trend-day 3-day structure; failure/no-trade visibility",
        "content_note": (
            "Stocks & Commodities V.11:9 (360-366), 1993, interview by Thom Hartle. "
            "Covers: prior day's high and low as 'the most important reference points "
            "when I'm entering a position the next day'; determining the day before "
            "whether in breakout mode or swing-trading mode; NR7 day definition and "
            "'buying the breakout of an NR7 day ... going with the volatility' (cocoa "
            "example figure: 'The low volatility leads to a trend'); 'you have to have "
            "some method of measuring the amount of contraction in the market ... that "
            "tells me to switch to a breakout mode'; ADX rules (avoid ADX below 20 and "
            "declining; do not fade a market with ADX above 32 and rising); 'if there "
            "is a trend, buying the pullback to a moving average ... 20-period "
            "exponential moving average on all my markets'; 3-10 oscillator; short-term "
            "momentum precedes long-term momentum; three-day trade structure (test of "
            "prior low, middle trend day, third day peters out; carry overnight after a "
            "good trend day); failure/risk visibility (worst-case scenarios, fat tails)."
        ),
    },
    {
        "material_id": "SR-V0-M03",
        "canonical_title": "Trading Style and Daily Market Regimen",
        "source_publication": "Active Trader",
        "content_type": "official interview (Mark Etzkorn; trend days; NR7 bracket; wide-range bar; two-period ROC; flags + volatility filter; scalping vs position)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/raschke0204.pdf",
        "publication_date": "2004-02",
        "effective_content_date": "2004-02",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "trend-day definition/setup/confirmation; NR7 + early-morning-range bracket; wide-range bar reversal; two-period ROC; flags + volatility filter; session windows; no-trade; invalidation; instrument/timeframe scope",
        "content_note": (
            "Active Trader, February 2004, interview by Mark Etzkorn (a day with Linda "
            "Raschke, Nov 2003). Key material for the selected family: NR7 day (a bar "
            "with the narrowest range of the past seven bars) as a trend-day precursor; "
            "trend day definition ('opens on one end of its range and closes on the "
            "opposite end, has range expansion, and makes a steady pattern of higher "
            "highs and higher lows'); 'Something I'll almost always do the day after an "
            "NR7 day is bracket stops around the early morning range ... it didn't "
            "matter whether you bracketed the first 45 minutes range or the first "
            "hour's range. If there's going to be a trend day, you're going to catch "
            "it'; trend-day confirmation (large opening 15-min bar attributed to Toby "
            "Crabel; volume increase; leadership; trendiness 10-10:30/10:45; trend in "
            "breadth = advancing minus declining); wide-range bar reversal ('If today "
            "has the widest range of the past four days and an up close, the odds the "
            "low of the bar will be taken out in the next two days is the least-"
            "probable scenario'; down-closing wide-range bar + high taken out within "
            "two days = buy signal); two-period ROC momentum; flags + volatility filter;"
            " 'In a down-trending market, an early gap up is a short 95 percent of the "
            "time'; 'If I try to guess a breakout, I'm wrong 90 percent of the time'; "
            "session windows 10-11:30am and 2-3pm for flags; scalping execution."
        ),
    },
    {
        "material_id": "SR-V0-M04",
        "canonical_title": "The Rituals of Trading",
        "source_publication": "Active Trader",
        "content_type": "official interview (Mark Etzkorn; price-based trading; flags; three pushes; management; risk; execution; money management; psychology)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/rituals.pdf",
        "publication_date": "2000-08",
        "effective_content_date": "2000-08",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "price-based emphasis; three pushes; continuation patterns; management (take half, get out when giving back too much); risk framing; execution; bull/bear flags as best risk-reward; 30/60/120-min road map",
        "content_note": (
            "Active Trader, August 2000, interview by Mark Etzkorn. Covers: 'Ninety "
            "percent of what I do is price-based. Indicators are just derivatives of "
            "price'; 'When a market breaks out and there's some momentum, there are "
            "usually three pushes up'; 'The minute the market gives back more than it "
            "should, you get out on the first reaction or pause'; 'If the market "
            "reaches a price objective, and you're really not sure if it's going to "
            "continue, you have to at least take half the position off'; trading in two "
            "pieces; no averaging (bad habit); bull/bear flags as 'the best risk-reward "
            "ratios of any technique out there'; 30-, 60- and 120-minute charts as "
            "intraday road map; TICK used like a momentum oscillator; execution accounts "
            "for at least 50 percent of the bottom line; initial risk point ($500/contract "
            "general rule; S&P scalp risk 3 points, position risk up to 10 points); four "
            "areas (trade methodology, execution, money management, psychology)."
        ),
    },
    {
        "material_id": "SR-V0-M05",
        "canonical_title": "Traders Toolbox",
        "source_publication": "Active Trader",
        "content_type": "official interview part 2 (Mark Etzkorn; 3-10 oscillator; 14-period ADX; Keltner channels; two-period ROC; Holy Grail across time frames; bar-close-position tendency)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/03/raschke_pt2_0304.pdf",
        "publication_date": "2004-03",
        "effective_content_date": "2004-03",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "indicator checklist (3-10 oscillator, 14 ADX, Keltner, 2p ROC, TICK/TIKI, closing breadth, put-call); Holy Grail setup across time frames; daily close-in-upper-20% tendency; cross-market leading (DAX/EuroStoxx) as unavailable-input boundary",
        "content_note": (
            "Active Trader, March 2004, interview by Mark Etzkorn (follow-up). Indicator "
            "checklist: 3-10 oscillator (3-day minus 10-day SMA plus 16-period SMA), "
            "14-period ADX, Keltner Channels (2.5 ATR around 20-period EMA), two-period "
            "ROC on daily charts, TICK/TIKI highs and lows, closing breadth (10-period "
            "SMA of NYSE advancers minus decliners), put-call ratio (5-period SMA). "
            "Holy Grail setup detail: 'When the market breaks out of an extended trading "
            "range and makes new momentum highs, there is a sequence that typically "
            "unfolds. Price first pulls back to the 20-bar EMA ... then the same "
            "retracement will occur on the 30-minute chart, then the 60-minute chart, "
            "then the 120-minute time frame. By then you should be looking for a top. "
            "But each retracement has to be preceded by a 14-bar ADX reading above 30 "
            "on that time frame'; tendency: a daily S&P bar closing in the upper 20% of "
            "its range has approximately 75% odds the next bar trades above the high but "
            "only 50% odds it closes above it. Cross-market: DAX/EuroStoxx leading the "
            "US (unavailable cross-market surface for this project)."
        ),
    },
    {
        "material_id": "SR-V0-M09",
        "canonical_title": "Maintain your Mindset Using the Three R's of Positive Thinking",
        "source_publication": "Stock Futures & Options",
        "content_type": "official article (mindset/psychology; process)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/SFO_July04.pdf",
        "publication_date": "2004-07",
        "effective_content_date": "2004-07",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "psychology/process boundary (not a market-scene observable)",
        "content_note": (
            "SFO Magazine, July 2004. Mindset/psychology article (Three R's of positive "
            "thinking). Process material only; not a market-scene strategy input. Retained "
            "for the record; no market-scene claims extracted from it."
        ),
    },
    {
        "material_id": "SR-V0-M10",
        "canonical_title": "Who are You? Zoom in on Personal Trading Behavior and Profit from it!",
        "source_publication": "Stock Futures & Options",
        "content_type": "official article (behavior/psychology; process)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/SFO_raschke_0803.pdf",
        "publication_date": "2003-08",
        "effective_content_date": "2003-08",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "behavioral/process claims; unforced errors; game plan; resting stop; add to winners (GREEN LIGHT GO)",
        "content_note": (
            "SFO Magazine, August/September 2003, article by Linda Bradford Raschke. "
            "Behavioral process: bottom lines suffer from marginal trades, game plans not "
            "followed, unforced errors; identify personal behavioral patterns; have a "
            "trading plan each day as insurance against marginal spontaneous trades; "
            "always have a resting stop in the market until able to recognize personal "
            "signs of being in a bad trade; GREEN LIGHT GO - add to a winning position "
            "when the trade feels in sync. Process layer, not a market-scene observable."
        ),
    },
    {
        "material_id": "SR-V0-M11",
        "canonical_title": "Everything You Wanted to Know about Electronic Trading but were Afraid to Ask",
        "source_publication": "Stock Futures & Options",
        "content_type": "official article (execution/process; order routing; execution skills)",
        "language": "EN",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/Rashke_0406.pdf",
        "publication_date": "2006-04",
        "effective_content_date": "2006-04",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "source_example_date_status": "PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES",
        "diversity_role": "execution/process boundary (order routing, resting stops, working bids/offers)",
        "content_note": (
            "SFO Magazine, April 2006, article by Linda Bradford Raschke. Execution/"
            "process: electronic order routing, execution platforms, resting stops at "
            "exchange level, working a bid first and executing at market if not filled, "
            "avoid being reactive, place initial stop well outside the noise. Execution "
            "layer; not a market-scene strategy input for this screen."
        ),
    },
]

# Excluded image-only official PDFs (acquired but no embedded text layer; no OCR
# tool installed; adding one would be a new acquisition/processing framework).
IMAGE_ONLY_EXCLUDED = [
    {
        "material_id": "SR-V0-M06",
        "canonical_title": "Multi-Market Traders Rule",
        "source_publication": "Financial Trader",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/ftrader.pdf",
        "reason_excluded": "image-only scan; no embedded text layer; no OCR tool installed; profile/interview piece not needed for the family screen",
    },
    {
        "material_id": "SR-V0-M07",
        "canonical_title": "Trade Trends (interview/profile)",
        "source_publication": "Futures",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/upstairs.pdf",
        "reason_excluded": "image-only scan; no embedded text layer; no OCR tool installed; profile/interview piece not needed for the family screen",
    },
    {
        "material_id": "SR-V0-M08",
        "canonical_title": "Trading Insights (interview/profile)",
        "source_publication": "Omega Research",
        "url": "https://lindaraschke.net/wp-content/uploads/2026/01/Omega.pdf",
        "reason_excluded": "image-only scan; no embedded text layer; no OCR tool installed; profile/interview piece not needed for the family screen",
    },
]

SELECTION_CRITERIA = [
    "official lindaraschke.net free/public article archive / TRACEABLE_ORIGINAL",
    "free/public/unauthenticated access state (verified by direct fetch on 2026-08-19)",
    "effective content date before 2024-01-01 (before the frozen corpus start)",
    "official video surface is YouTube-hosted and blocked by 403 in the recorded "
    "environment; no circumvention; official free article/text material used instead",
    "stable attributable official URL, title, and publication date",
    "material materially improves exact anchors for a price/volume/session trading "
    "family (trend day / NR7 / contraction-expansion / range-breakout / pullback / "
    "session context)",
    "not broadened into unrelated third-party summaries or paid material",
    "not selected by expected historical performance",
]

OPTIONAL_PAID_CANDIDATES = [
    {
        "source_identity": "Trading Sardines: Lessons in the Markets from a Lifelong Trader "
        "(Linda Bradford Raschke; 2015 book, ISBN 9781532395622)",
        "why_it_might_matter": "Raschke's own book may contain deeper, more complete "
        "trading-loop semantics than the short official free articles.",
        "evidence_gap_it_could_fill": "Potential additional explicit setup/entry/"
        "invalidation/exit language for the selected family.",
        "access_class": "PAID_BOOK (not purchased; listed for awareness only)",
    },
    {
        "source_identity": "Street Smarts: High Probability Short-Term Trading Strategies "
        "(Raschke & Connors; book)",
        "why_it_might_matter": "The 1997 AIQ interview references the Holy Grail / "
        "Three-Day Unfilled Gap Reversal / Wolfe Wave patterns from this book with more "
        "detail than the free article.",
        "evidence_gap_it_could_fill": "Deeper source-pinned semantics for the pattern-"
        "specific claims.",
        "access_class": "PAID_BOOK (not purchased; listed for awareness only)",
    },
    {
        "source_identity": "NYSE TICK / TRIN / advance-decline breadth data (US market "
        "internals) referenced throughout the interviews",
        "why_it_might_matter": "The source's trend-day confirmation and TICK-momentum "
        "read use NYSE breadth/TICK; these surfaces are not in the Chinese-futures corpus.",
        "evidence_gap_it_could_fill": "Breadth/TICK surfaces for the trend-day "
        "confirmation handicap.",
        "access_class": "PAID_OR_SUBSCRIPTION_DATA (not purchased; listed for awareness only)",
    },
    {
        "source_identity": "Keltner Channel / ADX / 3-10 oscillator charting packages "
        "(e.g., TradeStation) referenced for the indicator checklist",
        "why_it_might_matter": "The Holy Grail setup uses ADX and 20-period EMA; these "
        "are computable from OHLC but the source's own charting tools are commercial.",
        "evidence_gap_it_could_fill": "Not a data gap; the indicators are computable "
        "from owned OHLCV. Listed only for source-tool awareness.",
        "access_class": "PAID_SOFTWARE (not purchased; listed for awareness only)",
    },
]

# ---------------------------------------------------------------------------
# Source claims (SOURCE CLAIM layer only; canonical EXPLICIT | INFERRED | UNKNOWN)
# ---------------------------------------------------------------------------
# Each claim is a source claim with an attributable anchor. claim_status is the
# canonical Claim Schema v1.0 EXPLICIT / INFERRED / UNKNOWN. INFERRED claims are
# labeled project/AI interpretation and are never presented as direct source
# statements. No machine operationalization is performed here.

CLAIMS = [
    {
        "claim_id": "C-RAS-001",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:MARKET_TIMING",
        "claim_status": "EXPLICIT",
        "claim_category": "NO_TRADE",
        "source_excerpt_short_or_paraphrase": (
            "'The worst thing you can do in terms of market timing is to buy in the "
            "middle of a trading range. Either buy new highs, or buy pullbacks, but "
            "don't put your capital to work in the middle of a trading range.'"
        ),
        "source_context_note": "Explicit no-trade/entry-location rule: do not put "
        "capital to work in the middle of a trading range; buy new highs or pullbacks.",
        "source_observation_surface": "price position relative to a trading range",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none; 'middle of a trading range' requires an "
        "interpreted range boundary (INFERRED), not an unavailable input",
        "lineage_id": "L-RAS-TIMING",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Range boundary definition is not pinned by the source.",
    },
    {
        "claim_id": "C-RAS-002",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:LISTEN_TO_MARKETS",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "source_excerpt_short_or_paraphrase": (
            "'Moves often start in either direction with an impulse and a thrust. It "
            "may be a range expansion, an increase in standard deviation, a breakaway "
            "gap, or even a failure to make a lower low.'"
        ),
        "source_context_note": "Explicit cue list for move initiation; several "
        "components are price-based (range expansion, breakaway gap, failure to make a "
        "lower low); 'increase in standard deviation' is not defined by the source.",
        "source_observation_surface": "price bars / range / gaps / lower-low failure",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "'increase in standard deviation' is not "
        "pinned (measure/window undefined); the other cues are price-observable",
        "lineage_id": "L-RAS-TIMING",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "No numeric definition of 'impulse', 'thrust', or the "
        "standard-deviation measure.",
    },
    {
        "claim_id": "C-RAS-003",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "source_excerpt_short_or_paraphrase": (
            "Holy Grail buy rules (sells reversed): 1. The 14-period ADX must initially "
            "be greater than 30 and rising. 2. Look for a retracement in price to the "
            "20-period exponential moving average, usually accompanied by a turndown in "
            "ADX. 3. When price touches the 20-period moving average, put a buy stop "
            "above the high of the previous bar. 4. Once filled, enter a protective "
            "sell stop at the newly formed swing low. Trail stops as profits grow."
        ),
        "source_context_note": "Explicit, structured pullback-in-trend rules. "
        "Indicator-based (ADX, EMA); both are computable from OHLC but are indicators, "
        "not raw price/volume/session.",
        "source_observation_surface": "ADX (OHLC-derived), 20-period EMA, bar highs, "
        "swing lows",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "indicators are derivable from owned OHLCV; "
        "'newly formed swing low' requires an interpreted swing definition (INFERRED)",
        "lineage_id": "L-RAS-HOLYGRAIL",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Swing-low identification is not pinned; ADX parameters are "
        "explicit (14-period).",
    },
    {
        "claim_id": "C-RAS-004",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:GAP_REVERSAL_RULES",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "source_excerpt_short_or_paraphrase": (
            "Three-Day Unfilled Gap Reversals: 1. Today the security gaps lower and "
            "does not fill the gap. 2. Over the next three trading sessions, have in "
            "place a buy stop one tick above the high of the gap-down day. 3. If filled, "
            "place a protective sell stop at the low of the gap-down day. 4. Protect any "
            "accrued profits with a trailing stop. 5. If not filled after three trading "
            "sessions, cancel the initial buy stop."
        ),
        "source_context_note": "Explicit gap-reversal rules; fully price/bar-based "
        "(gaps from OHLC). Single-article mention; no commodity-futures anchor.",
        "source_observation_surface": "gaps, bar highs/lows, session days",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none for raw bars; gap 'unfilled' semantics "
        "are explicit",
        "lineage_id": "L-RAS-GAPREVERSAL",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "'does not fill the gap' is explicit but tick-level fill "
        "semantics need a defined project convention.",
    },
    {
        "claim_id": "C-RAS-005",
        "material_id": "SR-V0-M01",
        "source_anchor": "SR-V0-M01:august1997:section:WOLFE_WAVE_RULES",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "source_excerpt_short_or_paraphrase": (
            "Wolfe Wave construction: wave 2 is the top of a bar chart; wave 3 is the "
            "bottom of the first decline after wave 2; wave 1 is the bottom prior to "
            "the wave 2 top (point 3 lower than point 1); wave 4 is the top of wave 3; "
            "a trend line from point 1 to point 3 projects to the anticipated reversal "
            "point (wave 5), the entry point; price objective from a trendline from "
            "points 1 to 4; initial stop just beneath point 5, then moved to break-even."
        ),
        "source_context_note": "Explicit construction rules but the source describes "
        "recognition as a trained-eye skill ('you will automatically get a magically "
        "trained eye'). Discretionary pattern identification.",
        "source_observation_surface": "bar swing points, trendlines",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "swing point identification and trendline "
        "drawing are discretionary; no objective selection rule is pinned",
        "lineage_id": "L-RAS-WOLFEWAVE",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Point selection (what counts as a swing top/bottom) is "
        "not mechanically defined.",
    },
    {
        "claim_id": "C-RAS-007",
        "material_id": "SR-V0-M02",
        "source_anchor": "SR-V0-M02:discerning-trader:section:NR7_BREAKOUT",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "source_excerpt_short_or_paraphrase": (
            "'A good example might be buying the breakout of an NR7 day, which stands "
            "for a narrow range seven-day pattern ... That trade would be going with "
            "the volatility in that case.' (Figure: 'A narrow range seven-day (NR7) in "
            "today's trading range is the narrowest trading range in the last seven "
            "days. The low volatility leads to a trend.')"
        ),
        "source_context_note": "Explicit NR7 definition (narrowest range of the last "
        "seven days) and an explicit entry: buy the breakout of the NR7 day, going "
        "with the volatility. Chart example is September Cocoa (commodity futures). "
        "KEY claim for the selected family.",
        "source_observation_surface": "daily bar ranges, breakout of NR7 day high/low",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (bar ranges and breakout levels from "
        "OHLCV); instrument transfer to Chinese futures is INFERRED, not explicit",
        "lineage_id": "L-RAS-NR7",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "NR7 is attributed lineage (Toby Crabel contraction/"
        "expansion); breakout entry 'with the volatility' has no explicit volume "
        "threshold.",
    },
    {
        "claim_id": "C-RAS-008",
        "material_id": "SR-V0-M02",
        "source_anchor": "SR-V0-M02:discerning-trader:section:GAME_PLAN",
        "claim_status": "EXPLICIT",
        "claim_category": "MARKET_CONTEXT",
        "source_excerpt_short_or_paraphrase": (
            "'I write down the previous day's high and low, because to me those are the "
            "most important reference points when I'm entering a position the next "
            "day; I like to know where the price today is relative to the previous "
            "day's high/low ... I program myself to either being in a breakout or "
            "countertrend mode.'"
        ),
        "source_context_note": "Explicit prior-day-level reference framework: previous "
        "day's high/low are the most important reference points; the trader decides "
        "the day before whether to trade that market in breakout mode or swing/"
        "countertrend mode.",
        "source_observation_surface": "prior-day high/low, current price relative to "
        "them",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (prior-day high/low from OHLCV; session/"
        "calendar metadata governs day boundaries)",
        "lineage_id": "L-RAS-PRIORDAY",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "'breakout mode' vs 'swing mode' selection is discretionary; "
        "no objective classifier is given.",
    },
    {
        "claim_id": "C-RAS-009",
        "material_id": "SR-V0-M02",
        "source_anchor": "SR-V0-M02:discerning-trader:section:ADX_RULES",
        "claim_status": "EXPLICIT",
        "claim_category": "NO_TRADE",
        "source_excerpt_short_or_paraphrase": (
            "'I avoid the markets where the ADX falls below 20 and is declining, "
            "because there's just not enough movement between the swings for me. "
            "Likewise, I have something of a golden rule: I will not fade a market. I "
            "will not try to trade against a market where the ADX is above 32 and "
            "rising.'"
        ),
        "source_context_note": "Explicit no-trade/filter rules keyed to ADX. "
        "Indicator-based (ADX computable from OHLC) but an indicator, and 'declining'/"
        "'rising' are not numerically defined.",
        "source_observation_surface": "ADX (OHLC-derived)",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "ADX is computable from owned OHLCV; 'declining'/"
        "'rising' slope semantics not pinned",
        "lineage_id": "L-RAS-ADX",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Slope ('declining'/'rising') definition is not pinned.",
    },
    {
        "claim_id": "C-RAS-010",
        "material_id": "SR-V0-M02",
        "source_anchor": "SR-V0-M02:discerning-trader:section:PULLBACK_TO_MA",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "source_excerpt_short_or_paraphrase": (
            "'If there is a trend, I'll try to always look for buying a pullback to a "
            "moving average ... I personally use a 20-period exponential moving average "
            "on all my markets.'"
        ),
        "source_context_note": "Explicit pullback-in-trend entry framework using a "
        "20-period EMA. Indicator-based but EMA is computable from owned OHLC.",
        "source_observation_surface": "20-period EMA, price pullback",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "EMA computable from OHLCV; 'trend' and "
        "'pullback' semantics not pinned",
        "lineage_id": "L-RAS-PULLBACK",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "'if there is a trend' is not objectively defined here.",
    },
    {
        "claim_id": "C-RAS-011",
        "material_id": "SR-V0-M02",
        "source_anchor": "SR-V0-M02:discerning-trader:section:THREE_DAY_STRUCTURE",
        "claim_status": "EXPLICIT",
        "claim_category": "MARKET_CONTEXT",
        "source_excerpt_short_or_paraphrase": (
            "'Most likely what'll happen is that the first day the market makes a test "
            "of the previous day's low. Then the middle day is when it'll have a trend "
            "day, and then the third day it peters out. Usually the middle day tends to "
            "be the big day, so if you ever get a middle, or a good trend day, or a "
            "good movement that day you should always carry that trade overnight "
            "because the odds are that you will get follow through the next day.'"
        ),
        "source_context_note": "Explicit multi-day structure claim (test of prior low, "
        "trend day, peter out) with an explicit management implication (carry a good "
        "trend day overnight for follow-through).",
        "source_observation_surface": "daily price structure relative to prior day's "
        "low; trend-day character",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "'trend day' needs the source's trend-day "
        "definition (see C-RAS-012); otherwise daily bars are observable",
        "lineage_id": "L-RAS-TRENDDAY",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "'peters out' and 'big day' are qualitative.",
    },
    {
        "claim_id": "C-RAS-012",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_DEFINITION",
        "claim_status": "EXPLICIT",
        "claim_category": "MARKET_CONTEXT",
        "source_excerpt_short_or_paraphrase": (
            "'A trend day opens on one end of its range and closes on the opposite "
            "end, has range expansion, and makes a steady pattern of higher highs and "
            "higher lows, or vice versa, throughout the day. In the index futures, "
            "there are two or three trend days a month.'"
        ),
        "source_context_note": "Explicit trend-day definition. Purely price-based "
        "(open/close/range/sequence of highs and lows). KEY claim for the selected "
        "family. Note: 'in the index futures' indicates the base instrument scope.",
        "source_observation_surface": "daily open/close/range, sequence of intraday "
        "highs/lows",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (open/close/high/low from 1-min OHLCV; "
        "session metadata governs day boundaries)",
        "lineage_id": "L-RAS-TRENDDAY",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "'range expansion' and 'steady pattern' are not numerically "
        "pinned.",
    },
    {
        "claim_id": "C-RAS-013",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_SETUP",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "source_excerpt_short_or_paraphrase": (
            "Three different types of conditions tend to precede a trend day: first, a "
            "significant degree of range contraction, 'such as an NR7 day, which is a "
            "bar with the narrowest range of the past seven bars'; second, a trend day "
            "after a large opening gap; finally, if the market is approaching new "
            "20-day highs or lows, 'these points tend to be magnets or key chart levels "
            "that will accelerate price action.'"
        ),
        "source_context_note": "Explicit trend-day precursor conditions. NR7 (narrowest "
        "range of past seven bars) is explicitly defined here and in the 1993 article. "
        "All price/session based. KEY claim for the selected family.",
        "source_observation_surface": "daily bar ranges (NR7), opening gaps, 20-day "
        "highs/lows",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (all from OHLCV + session metadata)",
        "lineage_id": "L-RAS-NR7",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "'significant degree' and 'large opening gap' are not "
        "numerically pinned.",
    },
    {
        "claim_id": "C-RAS-014",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TREND_DAY_CONFIRMATION",
        "claim_status": "EXPLICIT",
        "claim_category": "CONFIRMATION",
        "source_excerpt_short_or_paraphrase": (
            "Trend-day confirmation: 'a very large 15-minute bar to open the trading "
            "session' (attributed to Toby Crabel); volume increase ('Which of those "
            "stocks have had a significant increase in volume in the first 15 minutes "
            "relative to the past two weeks?'); leadership (IBM/Microsoft/Intel/GE); "
            "trendiness 10-10:30/10:45; and 'the last and most important thing is that "
            "I want to see trend in the market breadth - the difference between "
            "advancing issues and declining issues.'"
        ),
        "source_context_note": "Explicit trend-day confirmation mix. Volume and "
        "session components are observable; breadth (advancing minus declining) is a "
        "US equity-market surface NOT owned by the Chinese-futures corpus. The "
        "confirmation is a handicap, not the NR7 bracket entry trigger itself.",
        "source_observation_surface": "opening 15-min bar, volume, session time, "
        "breadth (advancing minus declining)",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "breadth (NYSE advancing/declining) is "
        "NOT_OBSERVABLE_WITH_CURRENT_DATA; no OHLCV proxy is authorized",
        "lineage_id": "L-RAS-TRENDDAY",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "'very large' 15-min bar and 'significant increase' in "
        "volume are not numerically pinned; breadth input unavailable.",
    },
    {
        "claim_id": "C-RAS-015",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "source_excerpt_short_or_paraphrase": (
            "'Something I'll almost always do the day after an NR7 day is bracket stops "
            "around the early morning range. When I tested this out about five years "
            "ago, it didn't matter whether you bracketed the first 45 minutes range or "
            "the first hour's range. If there's going to be a trend day, you're going "
            "to catch it.'"
        ),
        "source_context_note": "Explicit self-contained entry/management practice: the "
        "day after an NR7 day, bracket stops around the early morning range (either "
        "the first 45 minutes or the first hour - the source states both worked in her "
        "own test). Price/session based; no breadth/TICK required for the entry. KEY "
        "claim for the selected family. Base instrument in context is index futures.",
        "source_observation_surface": "NR7 day, next-day early morning range (45-min "
        "or 1-hour), bracket stop levels",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (session range from governed session "
        "metadata + 1-min OHLCV); choosing 45-min vs 1-hour is a source-permitted "
        "window choice, not an invented threshold",
        "lineage_id": "L-RAS-NR7",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "The bracket entry is explicit; instrument transfer to "
        "Chinese futures is INFERRED (the practice statement is in an index-futures "
        "context).",
    },
    {
        "claim_id": "C-RAS-016",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:WIDE_RANGE_BAR",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "source_excerpt_short_or_paraphrase": (
            "'If today has the widest range of the past four days and an up close, the "
            "odds the low of the bar will be taken out in the next two days is the "
            "least-probable scenario ... If there was a down-closing wide-range bar and "
            "the market takes out the high of that bar within two days, it's a buy "
            "signal, because that's the least-probable scenario - it occurs maybe 20 "
            "percent of the time.'"
        ),
        "source_context_note": "Explicit wide-range-bar tendency/signal. Purely "
        "price-based (bar ranges and closes). Single-article mention; no explicit "
        "stop/exit/target structure is given in the article.",
        "source_observation_surface": "daily bar ranges, closes, two-day takeout of "
        "high/low",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (bar ranges/closes from OHLCV)",
        "lineage_id": "L-RAS-WIDERANGE",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Signal/tendency only; management/exit/target not pinned in "
        "the article; 'widest range of the past four days' is explicit.",
    },
    {
        "claim_id": "C-RAS-017",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:FLAGS_VOLATILITY",
        "claim_status": "EXPLICIT",
        "claim_category": "NO_TRADE",
        "source_excerpt_short_or_paraphrase": (
            "'Bull and bear flags ... work in normal market conditions. But a bear "
            "flag, for example, will fail after a volatility extreme like a V-spike "
            "reversal because the market will likely make a spike and ledge instead of "
            "making a good retest back down. So, shorting the reaction after a V-spike "
            "reversal is a sucker's play. Flags will also fail when there's no "
            "volatility ... Statistical reliability only comes with a volatility "
            "filter.'"
        ),
        "source_context_note": "Explicit no-trade/failure condition: continuation "
        "flags (bull/bear) are unreliable at volatility extremes and in contracting "
        "volatility; a volatility filter is required. Also: 'If I simply [stop trading "
        "the pattern] after we've had a big move, it will eliminate the system's "
        "drawdown periods.'",
        "source_observation_surface": "volatility condition, flag patterns (visual)",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "volatility is computable from OHLCV; flag "
        "pattern identification is visual/discretionary and not mechanically pinned",
        "lineage_id": "L-RAS-FLAGS",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "'volatility extreme' and 'V-spike reversal' are not "
        "numerically pinned.",
    },
    {
        "claim_id": "C-RAS-018",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:TWO_PERIOD_ROC",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "source_excerpt_short_or_paraphrase": (
            "On the two-period rate of change (ROC) momentum: 'Typically, after two "
            "strong readings in an uptrend, [a pullback will occur].' A strong reading "
            "is 'one that's greater than the readings over the previous three to four "
            "weeks. It sort of depends on the individual market and environment, but "
            "three to four weeks is a rough way to quantify it.'"
        ),
        "source_context_note": "Explicit momentum pullback cue using a two-period ROC "
        "(difference between current close and close two bars ago); 'strong' is "
        "roughly quantified as greater than readings over the previous three to four "
        "weeks. Indicator (ROC) is a price derivative computable from owned closes.",
        "source_observation_surface": "two-period ROC (closes)",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "ROC computable from OHLCV; the 'strong' "
        "comparison window (3-4 weeks) is a rough source quantification, not a pinned "
        "threshold",
        "lineage_id": "L-RAS-ROC",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "'strong reading' threshold is deliberately rough in source.",
    },
    {
        "claim_id": "C-RAS-019",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:GAP_SHORT_RULE",
        "claim_status": "EXPLICIT",
        "claim_category": "ACTION_PERMISSION",
        "source_excerpt_short_or_paraphrase": (
            "'In a down-trending market, an early gap up is a short 95 percent of the "
            "time.'"
        ),
        "source_context_note": "Explicit conditional entry rule (early gap up in a "
        "down-trending market -> short). 'Down-trending market' is not objectively "
        "defined; 'early gap up' needs a session-time definition.",
        "source_observation_surface": "gap, session time, market trend context",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "gaps/session observable; 'down-trending "
        "market' definition not pinned",
        "lineage_id": "L-RAS-GAP",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Trend-context and 'early' definitions not pinned.",
    },
    {
        "claim_id": "C-RAS-020",
        "material_id": "SR-V0-M03",
        "source_anchor": "SR-V0-M03:raschke0204:section:BREAKOUT_GUESS_FAILURE",
        "claim_status": "EXPLICIT",
        "claim_category": "FAILURE_OR_COUNTEREXAMPLE",
        "source_excerpt_short_or_paraphrase": (
            "'If I try to guess a breakout, I'm wrong 90 percent of the time. I'm a "
            "perfect contrary indicator. ... I just know if it's a low ADX, I'm going "
            "to be wrong if I try to guess.'"
        ),
        "source_context_note": "Explicit failure/counterexample: guessing a breakout "
        "direction is unreliable; the source uses this as an argument for defined "
        "statistics/strategies and a low-ADX warning against guessing. Useful failure/"
        "no-trade evidence.",
        "source_observation_surface": "breakout guessing / low-ADX context",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "ADX computable; 'guessing' is a process "
        "failure mode, not a market-scene input",
        "lineage_id": "L-RAS-FAILURE",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Counterexample/process claim.",
    },
    {
        "claim_id": "C-RAS-021",
        "material_id": "SR-V0-M04",
        "source_anchor": "SR-V0-M04:rituals:section:MANAGEMENT_EXIT",
        "claim_status": "EXPLICIT",
        "claim_category": "MANAGEMENT",
        "source_excerpt_short_or_paraphrase": (
            "'The minute the market gives back more than it should, you get out on the "
            "first reaction or pause.' Also: 'If the market reaches a price objective, "
            "and you're really not sure if it's going to continue, you have to at least "
            "take half the position off.'"
        ),
        "source_context_note": "Explicit management/exit principles for held "
        "positions: exit on the first reaction/pause when price gives back more than "
        "it should; take at least half off at a price objective when continuation is "
        "uncertain. Qualitative; not numerically pinned.",
        "source_observation_surface": "price behavior vs objective/expectation",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "price observable; 'gives back more than it "
        "should' and 'price objective' are not numerically pinned",
        "lineage_id": "L-RAS-PROCESS",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Qualitative management; relevant to the selected family's "
        "exit semantics.",
    },
    {
        "claim_id": "C-RAS-023",
        "material_id": "SR-V0-M05",
        "source_anchor": "SR-V0-M05:toolbox:section:BAR_CLOSE_TENDENCY",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "source_excerpt_short_or_paraphrase": (
            "'Let's take the example of a daily S&P bar that closes in the upper 20 "
            "percent of its range. The odds are approximately 75 percent that the next "
            "bar will trade above the high of this bar, but there's only a 50-percent "
            "chance it will close above it. In other words, the pattern forecasts the "
            "market should trade above the most recent day's high, but it has no "
            "forecasting value regarding the close.'"
        ),
        "source_context_note": "Explicit, quantified bar-close-position tendency. "
        "Purely price-based (bar close position in range, next-bar high/close). "
        "Illustrates the source's tendency-modeling style; no entry/exit rules are "
        "attached here.",
        "source_observation_surface": "daily bar close position, next-bar high/close",
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": "none (bar ranges/closes from OHLCV)",
        "lineage_id": "L-RAS-TENDENCY",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Specific percentages are the source's own stated tendency; "
        "not a trading rule by itself.",
    },
    {
        "claim_id": "C-RAS-024",
        "material_id": "SR-V0-M02",
        "source_anchor": "SR-V0-M02:discerning-trader:section:CONTRACTION_MEASURE",
        "claim_status": "EXPLICIT",
        "claim_category": "MARKET_CONTEXT",
        "source_excerpt_short_or_paraphrase": (
            "'I use different measurements for the amount of contraction in the "
            "market. There's a number of different proxies you can use, but everybody "
            "should have some method of measuring the amount of contraction in the "
            "market. Many times, oscillators or momentum indicators will lose their "
            "oscillations or extreme readings. This is what I like to measure, and "
            "that tells me to switch to a breakout mode.'"
        ),
        "source_context_note": "Explicit framework claim: measuring market contraction "
        "tells the trader to switch to a breakout mode. This is the conceptual "
        "umbrella for the NR7 / range-contraction -> trend-day breakout family. The "
        "specific method is discretionary observation.",
        "source_observation_surface": "contraction (bar ranges / oscillator "
        "extreme-loss)",
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": "contraction is measurable from OHLCV but the "
        "source gives no single pinned method ('a number of different proxies you can "
        "use')",
        "lineage_id": "L-RAS-NR7",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "The source explicitly allows multiple contraction proxies; "
        "NR7 is one pinned example.",
    },
    {
        "claim_id": "C-RAS-025",
        "material_id": "SR-V0-M04",
        "source_anchor": "SR-V0-M04:rituals:section:TICK_AS_MOMENTUM",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "source_excerpt_short_or_paraphrase": (
            "'I use the TICKs like a momentum oscillator: If the TICKs are making new "
            "highs, I'll look to buy the pullbacks. ... The bottoms of sell-offs will "
            "be accompanied by negative TICK extremes, like -1,000, for example. Tops "
            "are characterized much more by complacency, with a lack of TICK readings.'"
        ),
        "source_context_note": "Explicit observability boundary: the source uses NYSE "
        "TICK (up-ticking minus down-ticking NYSE stocks) as a momentum oscillator and "
        "for trend confirmation. NYSE TICK is NOT owned by the Chinese-futures 1-minute "
        "OHLCV corpus and is not ordinary volume; no OHLCV proxy is authorized.",
        "source_observation_surface": "NYSE TICK / breadth (up-ticking minus "
        "down-ticking NYSE stocks)",
        "observability_compatibility": "NOT_OBSERVABLE_WITH_CURRENT_DATA",
        "observability_missing_inputs": "NYSE TICK / TRIN breadth surface; not owned "
        "by the corpus; no OHLCV proxy is authorized",
        "lineage_id": "L-RAS-TICK",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Confirmation/handicap input; not part of the NR7 bracket "
        "entry itself.",
    },
    {
        "claim_id": "C-RAS-026",
        "material_id": "SR-V0-M05",
        "source_anchor": "SR-V0-M05:toolbox:section:CROSS_MARKET_LEADING",
        "claim_status": "EXPLICIT",
        "claim_category": "OBSERVED_CUE",
        "source_excerpt_short_or_paraphrase": (
            "'What you'll find is, if you pull up a 15-minute EuroStoxx chart in the "
            "morning, and let's say the chart looked like this (she points to a strongly "
            "uptrending chart), I could just buy the S&P futures right then and have "
            "[very high odds of a] winning trade because the two markets are so highly "
            "correlated.' (DAX/EuroStoxx leading the US markets.)"
        ),
        "source_context_note": "Explicit observability boundary: the source uses "
        "cross-market leading relationships (DAX/EuroStoxx vs US). Cross-market data is "
        "NOT owned by the current Chinese-futures corpus; no proxy is authorized. This "
        "is a secondary context input, not part of the NR7/trend-day core entry.",
        "source_observation_surface": "cross-market index relationships (DAX / "
        "EuroStoxx vs US)",
        "observability_compatibility": "NOT_OBSERVABLE_WITH_CURRENT_DATA",
        "observability_missing_inputs": "European index data (DAX/EuroStoxx) and US "
        "corpus cross-market surface; not owned",
        "lineage_id": "L-RAS-CROSSMARKET",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
        "ambiguity_notes": "Context/handicap input for the index-futures context; not "
        "required for the selected family's core price/session inputs.",
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
        source_id=BUNDLE_ID,
        source_anchor=claim["source_anchor"],
        claim_status=claim["claim_status"],
        source_excerpt_short_or_paraphrase=claim["source_excerpt_short_or_paraphrase"],
        source_only_session_id=session_id,
        created_at=CREATED_AT,
    )


def main() -> None:
    _ = EvidenceLedger  # exercise import graph (no market data held here)

    bundle_hash = _bundle_hash()
    material_records = _material_records()

    # ---- B: source bundle manifest (predeclared) --------------------------
    manifest = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN",
        "manifest_version": "1.0",
        "bundle_id": BUNDLE_ID,
        "bundle_name": BUNDLE_NAME,
        "canonical_bundle_hash": bundle_hash,
        "selected_on": "2026-08-19",
        "retrieval_mode": RETRIEVAL_MODE,
        "package": "RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_AND_CLAIM_EXTRACTION_V0_1",
        "source": "SRC-RASCHKE",
        "source_admission_reference": (
            "docs/research/source_dossiers/SOURCE_DOSSIER_RASCHKE_V0_1.md; "
            "docs/research/HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_2.md"
        ),
        "selection_criteria": SELECTION_CRITERIA,
        "selection_basis_note": (
            "Selection based on provenance + free/public access + source-anchor "
            "quality + direct relevance to a price/volume/session trading family. "
            "NEVER based on expected trading performance, backtest quality, or ease "
            "of producing a strategy."
        ),
        "source_substitution": {
            "occurred": "PARTIAL_SURFACE_SUBSTITUTION",
            "note": (
                "Official videos are YouTube-hosted and blocked by 403 in the recorded "
                "environment; no circumvention was attempted. Per source-acquisition "
                "policy, the screen switched to official free article/text material "
                "(the task's stated fallback). All bundled materials are official "
                "lindaraschke.net free/public PDFs; no paid or third-party-substitute "
                "material was used."
            ),
        },
        "access_state": {
            "verified_at": "2026-08-19",
            "all_urls_accessible": True,
            "all_urls_free_public_unauthenticated": True,
            "all_effective_content_dates_before_2024_01_01": True,
            "note": "URLs verified via direct HTTP fetch; PDFs are %PDF- with 200 "
            "status; no authentication/cookies used.",
        },
        "video_surface": {
            "official_video_index": "https://lindaraschke.net/linda-videos/",
            "hosting": "YouTube channel @lindaraschke6565 only (no direct embeds/mp4)",
            "acquisition_state": "BLOCKED_BY_403_IN_RECORDED_ENV",
            "circumvention_attempted": "NO",
            "fallback": "official free article/text material used",
        },
        "image_only_excluded": IMAGE_ONLY_EXCLUDED,
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
            "for this screen."
        ),
    }
    manifest_path = (
        REPO_ROOT / "docs" / "evidence" / "HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json"
    )
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
            f"{BUNDLE_ID}: 8 official free/public pre-2024 Linda Bradford Raschke "
            "articles on lindaraschke.net (AIQ Opening Bell 1997-08; Stocks & "
            "Commodities 1993-09; Active Trader 2004-02, 2000-08, 2004-03; SFO "
            "2004-07, 2003-08, 2006-04); see "
            "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json"
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
        raise RuntimeError("SOURCE_ONLY screen runner is not verified")

    # ---- Protected-outcome technical denial (engineering proof, once) -----
    denial = runner.request_protected_market_outcome("ENGINEERING_PROOF_ONLY_NO_RETRIEVAL")
    if denial.outcome != "DENIED" or denial.reason != "SOURCE_ONLY_TECHNICAL_DENIAL":
        raise RuntimeError(f"Unexpected denial result: {denial}")

    # ---- Record source claims through the provenance surface --------------
    for claim in CLAIMS:
        runner.record_claim(_claim_record_for(claim, session.session_id))

    # ---- C: SOURCE_ONLY session evidence + claim records ------------------
    session_record = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_SCREEN",
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
            "RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V1. Bounded source screen + claim "
            "extraction to select at most one current-data-compatible source-faithful "
            "family. No Playbook Contract is drafted by this session."
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
            "EXPLICIT | INFERRED | UNKNOWN. INFERRED claims are project/AI "
            "interpretation, never presented as direct source statements."
        ),
        "recorded_claim_count": len(output.records),
        "recorded_claim_ids": [r.claim_id for r in output.records],
        "claims": CLAIMS,
    }
    session_path = (
        REPO_ROOT / "docs" / "evidence" / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_SCREEN_V0_1.json"
    )
    _write_json(session_path, session_record)

    # ---- Console summary ---------------------------------------------------
    status_counts: dict[str, int] = {}
    obs_counts: dict[str, int] = {}
    for claim in CLAIMS:
        status_counts[claim["claim_status"]] = status_counts.get(claim["claim_status"], 0) + 1
        obs_counts[claim["observability_compatibility"]] = (
            obs_counts.get(claim["observability_compatibility"], 0) + 1
        )
    print(f"SOURCE_ONLY_VERIFIED={verified}")
    print(f"DENIAL_OUTCOME={denial.outcome}")
    print(f"DENIAL_REASON={denial.reason}")
    print(f"CLAIMS={len(CLAIMS)}")
    print(f"STATUS_COUNTS={status_counts}")
    print(f"OBSERVABILITY_COUNTS={obs_counts}")
    print(f"BUNDLE_HASH={bundle_hash}")
    print(f"MATERIALS={len(MATERIALS)}")
    print(f"IMAGE_ONLY_EXCLUDED={len(IMAGE_ONLY_EXCLUDED)}")
    print(f"MANIFEST={manifest_path.relative_to(REPO_ROOT).as_posix()}")
    print(f"SESSION={session_path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
