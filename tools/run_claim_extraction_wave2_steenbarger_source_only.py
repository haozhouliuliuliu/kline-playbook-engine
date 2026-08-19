"""REAL_CLAIM_EXTRACTION_WAVE2_STEENBARGER_PUBLIC_V1 - SOURCE_ONLY driver.

This tool performs the second REAL source-faithful claim-extraction wave using
the actual project SOURCE_ONLY implementation in `src/research_firewall.py`:

- predeclares the approved public source bundle (Brett Steenbarger / TraderFeed
  free public pre-2024 posts) and computes its canonical bundle hash;
- opens a project-verified SOURCE_ONLY session via
  `SourceOnlyPolicy.open_verified_session(...)`;
- verifies `source_only.is_verified(session_id) == True`;
- executes the protected-outcome denial path once (engineering proof) and
  expects `outcome=DENIED` / `reason=SOURCE_ONLY_TECHNICAL_DENIAL`;
- records every claim through the bounded `SourceOnlyClaimExtractionContext`
  provenance output surface;
- writes durable JSON evidence artifacts:
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST.json
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_2_STEENBARGER.json

HARD BOUNDARIES (frozen authority, do not violate):
- No candidate outcome / PnL / backtest / indicator search / chart-pattern mining.
- No project protected-period market-outcome retrieval (the runner has no such
  surface; any request is technically DENIED and audited).
- No canonical market data repository, validation, or historical-final access.
- Source claim != project/AI interpretation != machine operationalization.
- No invented thresholds; no fabricated OHLCV proxies for absent inputs
  (NYSE TICK, Market Delta / bid-offer volume, US sector/index breadth and
  cross-market instruments are NOT owned by the current project corpus).
- No purchase/subscription/authentication; free public original pages only.

All source materials have effective content dates BEFORE 2024-01-01 (before the
frozen corpus start), so under Protocol v1.0 section 4 no source-example date
audit is required for the protected windows.

Run:
    python -m tools.run_claim_extraction_wave2_steenbarger_source_only
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

SESSION_ID = "SOURCE_ONLY_WAVE2_STEENBARGER_PUBLIC_V1_20260819"
MODEL_IDENTITY = "deepseek-v4-flash"
PROMPT_SPEC_VERSION = "REAL_CLAIM_EXTRACTION_WAVE2_STEENBARGER_PUBLIC_V1"
RETRIEVAL_MODE = "LOCAL_FREE_PUBLIC_ORIGINAL_SOURCE_BUNDLE_ONLY"
BUNDLE_ID = "SB-W2-PUBLIC-STEENBARGER-V1"
BUNDLE_NAME = "Real Claim Extraction Wave 2 - Public Brett Steenbarger TraderFeed source bundle"
CREATED_AT = "2026-08-19T00:00:00Z"

EXPOSURE_NOTE = (
    "Model latent historical knowledge cannot be proven absent; this is a disclosed "
    "residual threat-model risk under the frozen protocol. No project protected-period "
    "market-outcome retrieval was available through the SOURCE_ONLY runner; the runner "
    "technically denies any such request and audits it. No canonical market data "
    "repository, validation surface, or historical-final surface was exposed to this "
    "session. All selected source materials have effective content dates before "
    "2024-01-01 (before the frozen corpus start), so no source-example date audit is "
    "required for the protected windows under Protocol v1.0 section 4. The bundled "
    "posts are source-process/market-read teaching material only; they are not "
    "accepted trading truth and were never selected by expected profitability."
)

RETENTION_BOUNDARY = (
    "Raw HTML of the source pages was not retained. Only attributable short excerpts "
    "and concise paraphrases needed for claim traceability are recorded. Full "
    "copyrighted articles are not stored. Anchors point to the canonical public URLs "
    "on traderfeed.blogspot.com."
)

# ---------------------------------------------------------------------------
# Source bundle definition (materials only; no redistributed copyrighted content)
# ---------------------------------------------------------------------------

MATERIALS = [
    {
        "material_id": "SB-W2-M1",
        "canonical_title": "Walking Through a Trade Setup",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (step-by-step trade walk-through; ES futures)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2007/08/walking-through-trade-setup.html",
        "date": "2007-08-04",
        "effective_content_date": "2007-08-04",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "market context / observed cue / watching-no-trade / confirmation / invalidation / exit / target-limitation / applicability",
        "content_note": (
            "Walk-through of one ES futures trade across 10 numbered steps plus a "
            "closing multi-timeframe summary. Uses a Market Delta chart, NYSE TICK, "
            "3-minute bars and 1-minute ES volume. Covers: momentum low on expanded "
            "volume; no-trade rules ('I don't sell markets that make new highs and I "
            "don't chase highs on dwindling volume'; 'I don't chase sellers'); candidate "
            "highs; selling on positive TICK / green Market Delta that cannot make fresh "
            "price highs; stop above candidate highs (new highs invalidate); target of "
            "range lows; cover on volume pickup and very negative (-1000) TICK; explicit "
            "target limitation (play for highest-probability move, not a home run "
            "breakout); long waiting/observing behavior; multi-timeframe applicability "
            "focus list."
        ),
    },
    {
        "material_id": "SB-W2-M2",
        "canonical_title": "Three Basic Trade Setups",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (setup taxonomy: reversal / breakout / continuation)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2009/01/three-basic-trade-setups.html",
        "date": "2009-01-27",
        "effective_content_date": "2009-01-27",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "market context / observed cue / confirmation / applicability / exit-target conventions",
        "content_note": (
            "Classifies most trading patterns into three basic setups: 1) Reversal "
            "trades (market at/beyond a trading-range edge, cannot sustain buying/"
            "selling interest, falls back; initial target generally range midpoint or "
            "prior pivot; good volume + extreme NYSE TICK frequently tests the opposite "
            "end; especially watch reversals in weak relative volume - market-maker "
            "driven markets); 2) Breakout trades (range-bound market surges out on "
            "enhanced volume + very high/low NYSE TICK; usually a catalyst; cross-market "
            "repricing as confirmation; daily price targets R1/R2/R3 / S1/S2/S3); "
            "3) Continuation trades (trend in place, wait for pullback; volume expands "
            "with trend and contracts on pullbacks; trending cumulative NYSE TICK and "
            "Market Delta; TICK/Delta pullbacks as entries; e.g. hit R1, light-volume "
            "pullback -> reload long for R2)."
        ),
    },
    {
        "material_id": "SB-W2-M3",
        "canonical_title": "Making the Hard Trade",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (failed-breakout / range-day market read; ES futures + sector confirmation)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2009/05/making-hard-trade.html",
        "date": "2009-05-15",
        "effective_content_date": "2009-05-15",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "failure / non-confirmation / invalidation / exit-target (reversion to VWAP) / review-process",
        "content_note": (
            "Short post using a range-day read in ES futures. Covers: opening-range "
            "context and sensitivity to a range day; important sectors (XLE, XLF) not "
            "confirming the upside breakout while XLB and XLV looked sketchy at the "
            "highs; failure to take out the prior day's high; re-entering the morning "
            "range; recognizing the upmove was failing without needing to catch the "
            "exact top; playing a reversion back to VWAP as a first target; closing "
            "process claim 'Making the hard trade: It's all about preparation.'"
        ),
    },
]

SELECTION_CRITERIA = [
    "original / nearest-original provenance (author's own official TraderFeed archive)",
    "free/public/unauthenticated access state (verified by direct fetch on 2026-08-19)",
    "pre-2024 original posts (effective content date before the frozen corpus start)",
    "stable attributable URL, title, and post date",
    "substantive market-read / setup / process content with explicit watching, "
    "no-trade, invalidation or target-limitation context where available",
    "not selected by expected historical performance",
]

OPTIONAL_PAID_CANDIDATES = [
    {
        "source_identity": "Market Delta (marketdelta.com) - commercial order-flow / "
        "volume-at-bid-vs-offer software referenced by the source for the 'Market Delta' "
        "readings (green/red volume at offer vs bid)",
        "why_it_might_matter": "The source's entry/confirmation/exit logic in the "
        "walk-through depends on bid-vs-offer volume (Market Delta) which is not present "
        "in 1-minute OHLCV.",
        "evidence_gap_it_could_fill": "Bid/offer volume and delta readings used by the "
        "source for 'green Market Delta' and 'volume at offer vs bid' conditions.",
        "access_class": "PAID_SOFTWARE_SUBSCRIPTION (not purchased; listed for awareness only)",
    },
    {
        "source_identity": "Brett Steenbarger books (e.g. The Psychology of Trading, "
        "Enhancing Trader Performance, Trading Psychology 2.0)",
        "why_it_might_matter": "Book-length process/psychology synthesis referenced by "
        "the TraderFeed About Me profile; could expand the review/process layer.",
        "evidence_gap_it_could_fill": "More systematic process/review/error material, "
        "not market-data inputs.",
        "access_class": "PAID_BOOK (not purchased; listed for awareness only)",
    },
    {
        "source_identity": "Market Profile / auction value-area data and software "
        "(Steidlmayer/Dalton lineage) referenced via 'the value area from the prior day'",
        "why_it_might_matter": "The reversal-setup definition cites prior-day value area, "
        "a Market Profile construct not derivable directly from 1-minute OHLCV without "
        "additional interpretation.",
        "evidence_gap_it_could_fill": "Value-area / TPO distribution inputs for the "
        "reversal range-edge definition.",
        "access_class": "PAID_SOFTWARE_OR_DATA (not purchased; listed for awareness only)",
    },
]

# ---------------------------------------------------------------------------
# Claim records (full Claim Schema v1.0 structural subset)
# ---------------------------------------------------------------------------

CLAIMS = [
    # ---------------- Material 1: Walking Through a Trade Setup ----------------
    {
        "claim_id": "C-W2-001",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:step:1_MOMENTUM_LOW",
        "source_anchor_type": "blog_post_step",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "1) We make a momentum low in selling at the 13:30 bar, with expanded volume "
            "and very heavy volume hitting bids."
        ),
        "source_context_note": (
            "First numbered step of the ES futures walk-through. Identifies a momentum "
            "low on expanded volume with very heavy volume hitting bids (bid-side "
            "volume)."
        ),
        "claim_category": "OBSERVED_CUE",
        "source_timeframe_or_horizon_if_explicit": "intraday bars (13:30 bar; post uses "
        "3-minute and 1-minute bars)",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini), day "
        "session",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'Momentum low' and 'expanded volume' are the source's own qualitative "
            "descriptions; no numeric definition is given."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "A price low on expanded 1-minute volume is observable from the 1-minute "
            "OHLCV corpus. 'Very heavy volume hitting bids' requires Market Delta "
            "(bid-side volume), which the project does not own; no OHLCV proxy is "
            "invented."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-002",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:step:4_NO_TRADE_NEW_HIGHS",
        "source_anchor_type": "blog_post_step",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "I'm doing nothing, because I don't sell markets that make new highs and I "
            "don't chase highs on dwindling volume. The reduced volume and volume at "
            "offer suggests to me that the rally is running out of steam (buyers)."
        ),
        "source_context_note": (
            "Fourth numbered step: successive price highs are being made; the trader "
            "explicitly takes no action because he does not sell markets making new "
            "highs and does not chase highs on dwindling volume."
        ),
        "claim_category": "WATCHING_OR_NO_TRADE",
        "source_timeframe_or_horizon_if_explicit": "intraday (next two 3-minute bars)",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini), day "
        "session",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": (
            "Explicit no-trade rule: do not sell markets that make new highs; do not "
            "chase highs on dwindling volume."
        ),
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'New highs' and 'dwindling volume' are relative concepts the source does "
            "not numerically define."
        ),
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": (
            "The stated rule is price-and-volume based: 'new highs' and 'dwindling "
            "volume' are representable from 1-minute OHLCV. The illustrative rationale "
            "also cites 'volume at offer' (Market Delta), which is not owned; the rule "
            "itself does not require it. Interpreting 'new high' and 'dwindling volume' "
            "is an operationalization decision, not an observability gap."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-003",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:step:5_NO_TRADE_WAIT_RALLY",
        "source_anchor_type": "blog_post_step",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Sellers have re-entered the market. I don't chase sellers, so now I'm "
            "waiting for the next rally to see if we get a good entry in the direction "
            "of the general market trend."
        ),
        "source_context_note": (
            "Fifth numbered step: after a stiff drop below the prior two bars' lows, the "
            "trader does not chase the selloff but waits for a rally to seek an entry in "
            "the direction of the general market trend."
        ),
        "claim_category": "WATCHING_OR_NO_TRADE",
        "source_timeframe_or_horizon_if_explicit": "intraday",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini), day "
        "session",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": (
            "Explicit no-trade behavior: do not chase sellers; wait for a rally to seek "
            "an entry in the direction of the general market trend."
        ),
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'General market trend' is not numerically defined by the source; in the "
            "surrounding example it was assessed partly with net volume and TICK, which "
            "are not owned by the project."
        ),
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": (
            "The stated behavior is price-structure based (rally, trend direction) and "
            "representable from 1-minute OHLCV. The source's illustrative trend read "
            "also used net volume (Market Delta) and TICK; those inputs are missing but "
            "not required by the stated rule. Interpreting 'general market trend' is an "
            "operationalization decision."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-004",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:step:6_CANDIDATE_HIGHS",
        "source_anchor_type": "blog_post_step",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "The market bounces higher, but does not expand its TICK distribution and "
            "does not expand volume or volume traded at the offer. This is short-covering "
            "and I see we're having trouble making new highs relative to the 13:39 bar. "
            "I declare to myself that the highs of the 13:39 bar are my 'candidate highs' "
            "for this bounce and I now view the market as in a trading range defined by "
            "the 13:30 lows and the 13:39 highs."
        ),
        "source_context_note": (
            "Sixth numbered step: a bounce that fails to expand TICK distribution, "
            "volume, or offer-side volume is read as short-covering; failure to exceed "
            "the 13:39 bar's highs defines candidate highs and a short-term trading "
            "range."
        ),
        "claim_category": "CONFIRMATION",
        "source_timeframe_or_horizon_if_explicit": "intraday (13:39 bar candidate highs; "
        "13:30 lows; 3-minute bars)",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini), day "
        "session",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": (
            "The failed expansion of the bounce (short-covering read) is a "
            "non-confirmation of buying strength."
        ),
        "ambiguity_notes": (
            "'TICK distribution' is NYSE TICK, not owned by the project; 'candidate "
            "highs' and the range boundaries are the trader's discretionary labels."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "Price highs and volume are observable from 1-minute OHLCV; the 'trading "
            "range' and 'candidate highs' are derivable as an interpretation decision. "
            "TICK distribution and 'volume traded at the offer' (Market Delta) are not "
            "owned; no OHLCV proxy is invented."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-005",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:step:7_ENTRY_TRIGGER",
        "source_anchor_type": "blog_post_step",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "I sell when we make positive TICK readings and green Market Delta readings "
            "(more volume at offer than bid) that cannot make fresh price highs."
        ),
        "source_context_note": (
            "Seventh numbered step: the explicit entry trigger for the short is a "
            "combination of positive TICK readings and green Market Delta (more volume "
            "at offer than bid) that cannot make fresh price highs."
        ),
        "claim_category": "ACTION_PERMISSION",
        "source_timeframe_or_horizon_if_explicit": "intraday",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini), day "
        "session",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "The entry permission is explicitly conditioned on TICK and Market Delta "
            "inputs; only the 'cannot make fresh price highs' portion is price-based."
        ),
        "observability_compatibility": "NOT_OBSERVABLE_WITH_CURRENT_DATA",
        "observability_missing_inputs": (
            "NYSE TICK and Market Delta (volume at offer vs bid) are the stated entry "
            "triggers and are not owned by the current project corpus. The remaining "
            "price portion ('cannot make fresh price highs') alone is not a faithful "
            "representation of the stated trigger; no OHLCV proxy is invented."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_OBSERVABLE",
    },
    {
        "claim_id": "C-W2-006",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:step:7_STOP_AND_TARGET",
        "source_anchor_type": "blog_post_step",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "My trade idea is that we'll retest the lows of the range and resume "
            "movement in the market's longer-term (day session) direction. My stop is "
            "above the 13:39 highs--a move to new highs invalidates my idea. My profit "
            "target is the lows of the trading range."
        ),
        "source_context_note": (
            "Seventh numbered step (continuation): states the trade idea, the stop above "
            "the candidate highs, the invalidation condition (new highs), and the profit "
            "target of the range lows."
        ),
        "claim_category": "INVALIDATION",
        "source_timeframe_or_horizon_if_explicit": "intraday; day-session direction",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini), day "
        "session",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": (
            "A move to new highs (above the 13:39 candidate highs) invalidates the "
            "trade idea."
        ),
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": (
            "Profit target is the lows of the trading range; stop is placed above the "
            "candidate highs."
        ),
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'Candidate highs' and 'trading range' are the trader's discretionary "
            "labels; stop/target placement depends on their definition."
        ),
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": (
            "Stop above a candidate high, invalidation on new highs, and a target at "
            "range lows are price-structure statements representable from 1-minute "
            "OHLCV once candidate-high/range boundaries are interpreted (an "
            "operationalization decision, not an observability gap)."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-007",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:step:8_COVER",
        "source_anchor_type": "blog_post_step",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Eventually we get to the bottom of the trading range in the 13:48 and 13:51 "
            "bars. As one-minute ES volume picks up and we get very negative (-1000) "
            "TICK readings, I cover my position. I generally like buyers who can't push "
            "the market higher to get me into my short positions and sellers who are "
            "panicking out of the market to help me cover my positions."
        ),
        "source_context_note": (
            "Eighth numbered step: exit/management of the short. Covers when the target "
            "zone is reached, volume picks up, and very negative TICK readings appear; "
            "also states a general preference for fading buyers who cannot push the "
            "market higher and for covering into panicking sellers."
        ),
        "claim_category": "EXIT",
        "source_timeframe_or_horizon_if_explicit": "intraday (13:48 and 13:51 bars; "
        "1-minute volume)",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini), day "
        "session",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": (
            "Cover the position when the bottom of the range is reached, 1-minute volume "
            "picks up, and very negative (-1000) TICK readings occur. The numeric -1000 "
            "is the source's example reading, not a project threshold."
        ),
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'Volume picks up' is not numerically defined; the (-1000) TICK value is a "
            "specific historical example reading."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "Range bottom and 1-minute volume pickup are observable from 1-minute OHLCV. "
            "NYSE TICK readings are not owned; no OHLCV proxy is invented."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-008",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:step:9_TARGET_LIMITATION",
        "source_anchor_type": "blog_post_step",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "My goal is to enter the position after I identify a short-term candidate "
            "high, but as close to that high price as possible to keep losses small if "
            "I'm stopped out. ... My goal is also to simply play for the highest "
            "probability move. In this case, it's simply a return to the bottom of the "
            "range. I'm not playing for a home run breakout trade. If the market moves "
            "into breakout mode, I'll consider that a separate trade and setup."
        ),
        "source_context_note": (
            "Ninth numbered step: entry placement objective (close to the candidate high "
            "to keep losses small), favorable risk:reward, and an explicit target "
            "limitation (highest-probability move to the bottom of the range rather than "
            "a home run breakout; a breakout is treated as a separate trade/setup)."
        ),
        "claim_category": "ACTION_PERMISSION",
        "source_timeframe_or_horizon_if_explicit": "intraday",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini), day "
        "session",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": (
            "Explicit target limitation: play for the highest-probability move (a return "
            "to the bottom of the range), not a home run breakout; if the market moves "
            "into breakout mode, treat that as a separate trade and setup."
        ),
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'Candidate high', 'as close as possible', and 'highest probability move' "
            "are qualitative; no numeric tolerance is given."
        ),
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": (
            "Entry placement relative to a candidate high and a target at the range "
            "bottom are price-structure statements representable from 1-minute OHLCV "
            "once the candidate-high/range boundaries are interpreted."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-009",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:step:10_WAIT_FOR_SETUP",
        "source_anchor_type": "blog_post_step",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Note that I'm spending a lot of time sitting and doing nothing other than "
            "observing market dynamics and planning out the trade. There are times I'll "
            "sit for a very long time, just waiting for one great setup. The goal is not "
            "to put on trades; it's to wait for things to line up in your favor, giving "
            "you an edge."
        ),
        "source_context_note": (
            "Tenth numbered step: describes the trader's waiting/observing behavior and "
            "states that the goal is to wait for favorable conditions rather than to "
            "force trades."
        ),
        "claim_category": "REVIEW_PROCESS",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini), day "
        "session",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": (
            "Implicit no-trade posture: the goal is not to put on trades but to wait for "
            "conditions to line up in the trader's favor."
        ),
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": "UNKNOWN",
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Behavioral/process claim; no market-data input.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
    },
    {
        "claim_id": "C-W2-010",
        "material_id": "SB-W2-M1",
        "source_anchor": "SB-W2-M1:walking-through-trade-setup:closing:MULTI_TIMEFRAME",
        "source_anchor_type": "blog_post_closing",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "The type of pattern I'm illustrating above occurs on multiple time frames. "
            "A key to trading this way is being able to follow one market across many "
            "time frames ... and focusing on: 1) the market's general direction; 2) the "
            "presence of a trading range; 3) a candidate price high or low; 4) an entry "
            "that leans on this candidate high or low to follow the market's broader "
            "direction; and 5) a high probability price target."
        ),
        "source_context_note": (
            "Closing paragraph: states the pattern generalizes across time frames and "
            "lists five focus elements (general direction, trading range, candidate "
            "high/low, entry leaning on it, high-probability target)."
        ),
        "claim_category": "APPLICABILITY",
        "source_timeframe_or_horizon_if_explicit": "multiple time frames (source "
        "wording); the example uses intraday bars",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini) in the "
        "example; the source states the pattern occurs on multiple time frames",
        "source_applicability_if_explicit": (
            "Pattern stated to occur on multiple time frames; the five focus elements "
            "are the stated applicability framework."
        ),
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'Candidate price high or low' and 'high probability price target' are "
            "qualitative; the source's example read them with TICK/Delta aids that the "
            "project does not own."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "Market direction, trading range, and candidate high/low are price-structure "
            "concepts representable from 1-minute OHLCV (with interpretation). The "
            "illustrative example also used TICK and Market Delta, which are not owned; "
            "no proxy is invented."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    # ---------------- Material 2: Three Basic Trade Setups ----------------
    {
        "claim_id": "C-W2-011",
        "material_id": "SB-W2-M2",
        "source_anchor": "SB-W2-M2:three-basic-trade-setups:section:1_REVERSAL_TRADES",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Reversal Trades - The market moves to or just beyond the edges of a trading "
            "range (a consolidation area, the value area from the prior day), cannot "
            "sustain buying/selling interest, and falls back into that range."
        ),
        "source_context_note": (
            "First of three basic setups. Defines the reversal trade: price reaches or "
            "just exceeds a trading-range edge (including prior-day value area), fails to "
            "sustain buying/selling interest, and falls back into the range."
        ),
        "claim_category": "OBSERVED_CUE",
        "source_timeframe_or_horizon_if_explicit": "trading range; prior-day value area; "
        "timeframe not otherwise specified",
        "source_market_or_instrument_if_explicit": "stocks/indices (SPX context); "
        "market maker vs longer-timeframe participant context",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'Cannot sustain buying/selling interest' is qualitative; 'value area from "
            "the prior day' is a Market Profile construct not derivable directly from "
            "1-minute OHLCV without additional interpretation."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "Trading-range edges are price-observable from 1-minute OHLCV. 'Cannot "
            "sustain buying/selling interest' is volume/Delta based and prior-day value "
            "area requires Market Profile inputs; neither is owned, so no OHLCV proxy "
            "is invented."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-012",
        "material_id": "SB-W2-M2",
        "source_anchor": "SB-W2-M2:three-basic-trade-setups:section:1_REVERSAL_TARGETS",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "The initial target for such a trade will generally be the midpoint of that "
            "range (which may also be the pivot level from the previous day or week); a "
            "reversal on good volume and very weak/strong NYSE TICK will frequently test "
            "the opposite end of that range, as the breakout traders bail out of their "
            "positions."
        ),
        "source_context_note": (
            "Reversal-setup target statement: initial target generally the range "
            "midpoint (or prior pivot); a reversal on good volume and extreme NYSE TICK "
            "frequently extends to the opposite end of the range as breakout traders "
            "bail out."
        ),
        "claim_category": "EXIT",
        "source_timeframe_or_horizon_if_explicit": "trading range horizon; pivot from "
        "previous day or week",
        "source_market_or_instrument_if_explicit": "stocks/indices (SPX context)",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": (
            "Initial target generally the midpoint of the range (may also be the prior "
            "day/week pivot level); with good volume and very weak/strong NYSE TICK, "
            "frequently tests the opposite end of the range."
        ),
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'Midpoint of that range' vs 'pivot level' leaves two candidate target "
            "conventions; the source does not pin one unique rule."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "Range midpoint is price-observable once the range is interpreted. NYSE TICK "
            "is not owned; the pivot-level formula is not specified by the source."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-013",
        "material_id": "SB-W2-M2",
        "source_anchor": "SB-W2-M2:three-basic-trade-setups:section:1_REVERSAL_WEAK_RELATIVE_VOLUME",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "I like to be particularly on the lookout for reversal trades in "
            "environments in which relative volume is weak, as these tend to be markets "
            "that will be pushed around by market makers, not longer time frame "
            "participants."
        ),
        "source_context_note": (
            "Reversal-setup applicability note: prefers reversal trades in weak "
            "relative-volume environments because such markets are driven by market "
            "makers rather than longer-timeframe participants."
        ),
        "claim_category": "APPLICABILITY",
        "source_timeframe_or_horizon_if_explicit": "UNKNOWN",
        "source_market_or_instrument_if_explicit": "stocks/indices (SPX context)",
        "source_applicability_if_explicit": (
            "Reversal setups are especially sought in weak relative-volume environments."
        ),
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "'Relative volume' baseline/period is not defined by the source; "
            "'market makers vs longer time frame participants' is a structural "
            "inference, not a directly measured input."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "A relative-volume measure is derivable from 1-minute volume, but the "
            "source does not define its baseline; the participant-structure inference is "
            "not directly observable from the corpus."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-014",
        "material_id": "SB-W2-M2",
        "source_anchor": "SB-W2-M2:three-basic-trade-setups:section:2_BREAKOUT_TRADES",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Breakout Trades - Here we have a situation in which the market is range "
            "bound ... and surges out of the range, generally on enhanced volume and "
            "very high/low NYSE TICK levels. Very often, there will be a catalyst for "
            "the breakout (economic news; earnings) and the move will be reflected by "
            "other trading instruments and/or asset classes. ... if an economic report "
            "leads to repricing of other markets (interest rates; currencies), the "
            "chances are good that a simultaneous breakout in stock prices is real. The "
            "initial targets for breakout moves will be the daily price targets (R1, R2, "
            "R3; S1, S2, S3)."
        ),
        "source_context_note": (
            "Second of three basic setups: a range-bound market surges out of the range "
            "on enhanced volume and very high/low NYSE TICK, usually with a catalyst; "
            "cross-market repricing is treated as confirmation that the stock breakout "
            "is real; initial targets are the daily price targets R1/R2/R3, S1/S2/S3."
        ),
        "claim_category": "CONFIRMATION",
        "source_timeframe_or_horizon_if_explicit": "multi-day range noted (SPX example); "
        "daily price targets",
        "source_market_or_instrument_if_explicit": "stocks/indices (SPX); cross-market "
        "instruments (interest rates, currencies) as confirmation",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": (
            "Initial targets for breakout moves are the daily price targets R1/R2/R3 and "
            "S1/S2/S3 (formula not specified in this post)."
        ),
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "R1/R2/R3 and S1/S2/S3 target formulas are not defined in this post; "
            "'enhanced volume' and 'very high/low NYSE TICK' are qualitative."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "Range structure, breakout price, and volume are observable from 1-minute "
            "OHLCV. NYSE TICK and cross-market instruments (rates, currencies) are not "
            "owned by the current corpus; the catalyst (news/earnings) is not a market "
            "input. No proxy is invented."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-015",
        "material_id": "SB-W2-M2",
        "source_anchor": "SB-W2-M2:three-basic-trade-setups:section:3_CONTINUATION_TRADES",
        "source_anchor_type": "blog_post_section",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Continuation Trades - Here we have a trend already in place; the idea is to "
            "wait for a pull back to enter the trend. A good continuation trade will show "
            "volume expanding in the direction of the trend and contracting on pullbacks. "
            "There will also be a trending cumulative NYSE TICK and Market Delta; "
            "pullbacks in TICK and Delta will serve as potential entry points. For "
            "instance, if we hit R1 and then pull back on light volume and only modestly "
            "negative NYSE TICK and Delta, we could reload on the long side for a "
            "continuation move to R2."
        ),
        "source_context_note": (
            "Third of three basic setups: with a trend in place, wait for a pullback to "
            "enter; good continuations show volume expanding with the trend and "
            "contracting on pullbacks; trending cumulative NYSE TICK and Market Delta, "
            "with TICK/Delta pullbacks as potential entry points (R1-to-R2 example)."
        ),
        "claim_category": "CONFIRMATION",
        "source_timeframe_or_horizon_if_explicit": "trend context; R1/R2 daily price "
        "targets referenced",
        "source_market_or_instrument_if_explicit": "stocks/indices (SPX context)",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": (
            "Entry on pullbacks in TICK and Delta after a trend leg (e.g., hit R1, "
            "pull back on light volume and modestly negative TICK/Delta, reload long "
            "for a continuation move to R2)."
        ),
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "R1/R2 definitions are not specified in this post; 'volume expanding vs "
            "contracting' and 'modestly negative TICK and Delta' are qualitative."
        ),
        "observability_compatibility": "PARTIALLY_OBSERVABLE",
        "observability_missing_inputs": (
            "Trend direction and volume expansion/contraction are price/volume "
            "observable from 1-minute OHLCV (with interpretation). Trending cumulative "
            "NYSE TICK and Market Delta are not owned; no proxy is invented."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    # ---------------- Material 3: Making the Hard Trade ----------------
    {
        "claim_id": "C-W2-016",
        "material_id": "SB-W2-M3",
        "source_anchor": "SB-W2-M3:making-hard-trade:body:SECTOR_NON_CONFIRMATION",
        "source_anchor_type": "blog_post_body_paragraph",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "we came into the day sensitive to it being a range day and saw that the "
            "important XLE and XLF sectors were not confirming the upside breakout. Also "
            "looking sketchy at the highs were XLB and XLV."
        ),
        "source_context_note": (
            "Range-day read in ES futures: the upside breakout attempt is treated as "
            "suspect because key sectors (XLE, XLF) did not confirm, and XLB/XLV looked "
            "weak at the highs; the day was expected to be a range day."
        ),
        "claim_category": "CONFIRMATION",
        "source_timeframe_or_horizon_if_explicit": "day session (morning); prior-day "
        "high referenced",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini); sector "
        "ETFs XLE, XLF, XLB, XLV",
        "source_applicability_if_explicit": (
            "Upside breakout read is not applicable when key sectors do not confirm; the "
            "day is treated as a range day instead."
        ),
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": (
            "Non-confirmation of the breakout by key sectors is treated as counterevidence "
            "to the breakout read."
        ),
        "ambiguity_notes": (
            "'Sensitive to it being a range day' and 'not confirming' are qualitative "
            "judgments; the exact sector-confirmation rule is not specified."
        ),
        "observability_compatibility": "NOT_OBSERVABLE_WITH_CURRENT_DATA",
        "observability_missing_inputs": (
            "US sector ETF breadth (XLE/XLF/XLB/XLV) and the source index (ES) are not "
            "part of the current project corpus (Chinese futures 1-minute OHLCV); no "
            "proxy is invented."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_OBSERVABLE",
    },
    {
        "claim_id": "C-W2-017",
        "material_id": "SB-W2-M3",
        "source_anchor": "SB-W2-M3:making-hard-trade:body:FAILED_BREAKOUT_REVERSION",
        "source_anchor_type": "blog_post_body_paragraph",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Unable to take out yesterday's high, we moved back into the morning range ... "
            "Note how you didn't need to catch the exact top to recognize that the upmove "
            "was failing and play a reversion back to VWAP as a first target."
        ),
        "source_context_note": (
            "Failed-breakout read: price could not exceed the prior day's high and "
            "returned into the morning range; the trader recognized the upmove was "
            "failing without needing the exact top and played a reversion back to VWAP "
            "as a first target."
        ),
        "claim_category": "INVALIDATION",
        "source_timeframe_or_horizon_if_explicit": "day session (morning range); "
        "prior-day high",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini)",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": (
            "Failure to take out the prior day's high, followed by a return into the "
            "morning range, invalidates the upside breakout read."
        ),
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": (
            "Reversion back to VWAP is used as a first target; catching the exact top is "
            "explicitly stated as unnecessary."
        ),
        "source_failure_or_counterexample_anchor": (
            "The failed attempt on the prior day's high is a direct failure example of "
            "the upside breakout setup."
        ),
        "ambiguity_notes": (
            "'Morning range' boundaries and the VWAP reference period are not defined in "
            "this post; the source instrument (ES) differs from the project corpus."
        ),
        "observability_compatibility": "OBSERVABLE_NOW",
        "observability_missing_inputs": (
            "Prior-day high, morning range, and VWAP (a volume-weighted price) are all "
            "derivable from 1-minute OHLCV of an instrument. The source's example "
            "instrument (ES futures) is not in the current project corpus; instrument "
            "transfer/applicability is a separate interpretation step, not an "
            "observability gap."
        ),
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "INTERPRETATION_REQUIRED",
    },
    {
        "claim_id": "C-W2-018",
        "material_id": "SB-W2-M3",
        "source_anchor": "SB-W2-M3:making-hard-trade:closing:PREPARATION",
        "source_anchor_type": "blog_post_closing",
        "source_language": "EN",
        "claim_status": "EXPLICIT",
        "source_excerpt_short_or_paraphrase": (
            "Making the hard trade: It's all about preparation."
        ),
        "source_context_note": (
            "Closing sentence of the post: the 'hard trade' (shorting strength in a "
            "range day when sectors do not confirm) succeeds through preparation (the "
            "pre-market read of a range day and sector non-confirmation)."
        ),
        "claim_category": "REVIEW_PROCESS",
        "source_timeframe_or_horizon_if_explicit": "pre-market / day session",
        "source_market_or_instrument_if_explicit": "ES futures (S&P 500 E-mini); sector "
        "ETFs",
        "source_applicability_if_explicit": "UNKNOWN",
        "source_invalidation_if_explicit": "UNKNOWN",
        "source_no_trade_if_explicit": "UNKNOWN",
        "source_exit_or_management_if_explicit": "UNKNOWN",
        "source_failure_or_counterexample_anchor": "UNKNOWN",
        "ambiguity_notes": (
            "This is a process claim; it is not turned into a mechanical trading rule."
        ),
        "observability_compatibility": "NOT_APPLICABLE",
        "observability_missing_inputs": "Behavioral/process claim; no market-data input.",
        "primary_branch_status": "PRIMARY_NOT_YET_JUSTIFIED",
        "machine_operationalization_status": "NOT_STARTED",
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
    # EvidenceLedger import is intentional: it documents that the SOURCE_ONLY
    # policy is hosted by the project ResearchFirewall/evidence spine and keeps
    # the import graph exercised. The runner itself holds no market data.
    _ = EvidenceLedger

    bundle_hash = _bundle_hash()
    material_records = _material_records()

    # ---- B: source bundle manifest (predeclared) --------------------------
    manifest = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST",
        "manifest_version": "1.0",
        "bundle_id": BUNDLE_ID,
        "bundle_name": BUNDLE_NAME,
        "canonical_bundle_hash": bundle_hash,
        "selected_on": "2026-08-19",
        "retrieval_mode": RETRIEVAL_MODE,
        "source_admission_reference": (
            "docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md -> "
            "SRC-STEENBARGER / MAT-STEENBARGER-TRADERFEED (PRIORITY_DEEP_DIVE as "
            "process source) and docs/research/source_dossiers/SOURCE_DOSSIER_STEENBARGER_V0_1.md"
        ),
        "selection_criteria": SELECTION_CRITERIA,
        "selection_basis_note": (
            "Selection based on provenance + free/public access + anchor quality + "
            "failure/no-trade coverage + extraction suitability. NEVER based on "
            "expected trading performance, backtest quality, or ease of producing a "
            "strategy."
        ),
        "source_substitution": {
            "occurred": "NO",
            "note": (
                "All three preferred candidate posts were verified accessible "
                "(FREE_PUBLIC_UNAUTHENTICATED) with sufficient source-anchor quality, "
                "failure/no-trade coverage, and context; no substitution was required."
            ),
        },
        "access_state": {
            "verified_at": "2026-08-19",
            "all_urls_accessible": True,
            "all_urls_free_public_unauthenticated": True,
            "all_effective_content_dates_before_2024_01_01": True,
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
    manifest_path = (
        REPO_ROOT
        / "docs"
        / "evidence"
        / "HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST.json"
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
            f"{BUNDLE_ID}: 3 official free/public pre-2024 Brett Steenbarger "
            "TraderFeed posts (2007-08-04, 2009-01-27, 2009-05-15) on "
            "traderfeed.blogspot.com; see "
            "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST.json"
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
        "artifact": "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_2_STEENBARGER",
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
    session_path = (
        REPO_ROOT
        / "docs"
        / "evidence"
        / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_2_STEENBARGER.json"
    )
    _write_json(session_path, session_record)

    # ---- Console summary ---------------------------------------------------
    status_counts: dict[str, int] = {}
    obs_counts: dict[str, int] = {}
    primary_counts: dict[str, int] = {}
    for claim in CLAIMS:
        status_counts[claim["claim_status"]] = status_counts.get(claim["claim_status"], 0) + 1
        obs_counts[claim["observability_compatibility"]] = (
            obs_counts.get(claim["observability_compatibility"], 0) + 1
        )
        primary_counts[claim["primary_branch_status"]] = (
            primary_counts.get(claim["primary_branch_status"], 0) + 1
        )
    print(f"SOURCE_ONLY_VERIFIED={verified}")
    print(f"DENIAL_OUTCOME={denial.outcome}")
    print(f"DENIAL_REASON={denial.reason}")
    print(f"CLAIMS={len(CLAIMS)}")
    print(f"STATUS_COUNTS={status_counts}")
    print(f"OBSERVABILITY_COUNTS={obs_counts}")
    print(f"PRIMARY_COUNTS={primary_counts}")
    print(f"BUNDLE_HASH={bundle_hash}")
    print(f"MANIFEST={manifest_path.relative_to(REPO_ROOT).as_posix()}")
    print(f"SESSION={session_path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
