"""STEENBARGER_FALSE_BREAKOUT_SEMANTIC_COMPLETION_V1 - SOURCE_ONLY driver.

Targeted source-semantic completion for the already-selected Steenbarger
false-breakout / range-reversion playbook family. This is NOT a third broad
claim-extraction wave, NOT a backtest, and NOT strategy mining.

It uses the actual project SOURCE_ONLY implementation in
`src/research_firewall.py`:

- predeclares the approved public semantic-completion source bundle (Brett
  Steenbarger / TraderFeed free public pre-2024 posts) and computes its
  canonical bundle hash;
- opens a project-verified SOURCE_ONLY session via
  `SourceOnlyPolicy.open_verified_session(...)`;
- verifies `source_only.is_verified(session_id) == True`;
- executes the protected-outcome denial path once (engineering proof) and
  expects `outcome=DENIED` / `reason=SOURCE_ONLY_TECHNICAL_DENIAL`;
- records each semantic-field resolution through the bounded
  `SourceOnlyClaimExtractionContext` provenance output surface;
- writes durable JSON evidence artifacts:
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_STEENBARGER_FALSE_BREAKOUT_SEMANTIC_V0_1.json
    docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_STEENBARGER_FALSE_BREAKOUT_SEMANTIC_V0_1.json

HARD BOUNDARIES (frozen authority, do not violate):
- HUMAN_PLAYBOOK_FIRST remains binding. No data-first K-line mining, indicator
  discovery, parameter search, candidate backtests, candidate PnL/returns,
  expectancy, Sharpe, win/loss, equity/drawdown, Validation access,
  historical-final access, or canonical market-outcome calibration.
- No candidate outcome / PnL / backtest / indicator search / chart-pattern
  mining. No project protected-period market-outcome retrieval (the runner has
  no such surface; any request is technically DENIED and audited).
- Source claim != project/AI interpretation != machine operationalization.
- No invented thresholds; no fabricated OHLCV proxies for absent inputs
  (NYSE TICK, Market Delta / bid-offer volume, US sector/index breadth,
  advance-decline, cross-market instruments are NOT owned by the current
  Chinese-futures corpus).
- No purchase/subscription/authentication; free public original pages only.
- The task does NOT draft a Playbook Contract; it records a source-semantic
  decision. This package's separate markdown dossier decides
  SOURCE_FAITHFUL_PRICE_VOLUME_PLAYBOOK_DRAFTABLE.

All source materials have effective content dates BEFORE 2024-01-01 (before the
frozen corpus start), so under Protocol v1.0 section 4 no source-example date
audit is required for the protected windows.

Run:
    python -m tools.run_steenbarger_false_breakout_semantic_completion_source_only
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

SESSION_ID = "SOURCE_ONLY_SEMANTIC_COMPLETION_STEENBARGER_FALSE_BREAKOUT_V1_20260819"
MODEL_IDENTITY = "deepseek-v4-flash"
PROMPT_SPEC_VERSION = "STEENBARGER_FALSE_BREAKOUT_SEMANTIC_COMPLETION_V1"
RETRIEVAL_MODE = "LOCAL_FREE_PUBLIC_ORIGINAL_SOURCE_SEMANTIC_COMPLETION_ONLY"
BUNDLE_ID = "SB-SC-STEENBARGER-FALSE-BREAKOUT-V1"
BUNDLE_NAME = (
    "Targeted source-semantic completion - public Brett Steenbarger TraderFeed "
    "false-breakout / range-reversion source bundle"
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
    "protected windows under Protocol v1.0 section 4. The bundled posts are "
    "source-process/market-read teaching material only; they are not accepted "
    "trading truth and were never selected by expected profitability. This session "
    "resolves source semantics only; it does not draft a Playbook Contract."
)

RETENTION_BOUNDARY = (
    "Raw HTML of the source pages was not retained. Only attributable short excerpts "
    "and concise paraphrases needed for semantic traceability are recorded. Full "
    "copyrighted articles are not stored. Anchors point to the canonical public URLs "
    "on traderfeed.blogspot.com."
)

# ---------------------------------------------------------------------------
# Source bundle definition (materials only; no redistributed copyrighted content)
# ---------------------------------------------------------------------------

# The first three materials are the accepted Wave 2 bundle posts; the remaining
# eight are the task-scoped official pre-2024 TraderFeed semantic-completion
# posts that directly resolve the required semantics.
MATERIALS = [
    {
        "material_id": "SB-SC-M1",
        "wave2_material_ref": "SB-W2-M1",
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
        "diversity_role": "candidate highs / trading range / invalidation / target / entry trigger / no-trade / applicability",
        "content_note": (
            "Walk-through of one ES futures trade across 10 numbered steps plus a "
            "closing multi-timeframe summary. Key semantics for the false-breakout/"
            "range-reversion family: (step 6) the market bounces but does not expand "
            "TICK distribution, volume, or volume at the offer; the 13:39 bar highs "
            "are declared 'candidate highs' and the market is viewed as in a trading "
            "range defined by the 13:30 lows and the 13:39 highs; (step 7) 'I sell "
            "when we make positive TICK readings and green Market Delta readings (more "
            "volume at offer than bid) that cannot make fresh price highs... My stop "
            "is above the 13:39 highs--a move to new highs invalidates my idea. My "
            "profit target is the lows of the trading range.'; (step 9) enter after a "
            "short-term candidate high as close to that high as possible, play for the "
            "highest-probability move (return to the bottom of the range), not a home "
            "run breakout; 'If the market moves into breakout mode, I'll consider that "
            "a separate trade and setup.'; closing: the pattern occurs on multiple "
            "time frames; focus on 1) market's general direction, 2) presence of a "
            "trading range, 3) a candidate price high or low, 4) an entry leaning on "
            "that candidate, 5) a high probability price target. Uses NYSE TICK and "
            "Market Delta (bid/offer volume)."
        ),
    },
    {
        "material_id": "SB-SC-M2",
        "wave2_material_ref": "SB-W2-M2",
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
        "diversity_role": "reversal/breakout/continuation separation; range-edge / value-area; target conventions; confirmation",
        "content_note": (
            "Classifies most trading patterns into three basic setups: 1) Reversal "
            "trades ('The market moves to or just beyond the edges of a trading range "
            "(a consolidation area, the value area from the prior day), cannot sustain "
            "buying/selling interest, and falls back into that range. The initial "
            "target... will generally be the midpoint of that range (which may also be "
            "the pivot level from the previous day or week); a reversal on good volume "
            "and very weak/strong NYSE TICK will frequently test the opposite end of "
            "that range'); 2) Breakout trades (range-bound market surges out on "
            "enhanced volume + very high/low NYSE TICK; usually a catalyst; cross-market "
            "repricing as confirmation; initial targets R1/R2/R3, S1/S2/S3); "
            "3) Continuation trades (trend in place, wait for pullback; volume expands "
            "with trend and contracts on pullbacks; trending cumulative NYSE TICK and "
            "Market Delta; TICK/Delta pullbacks as entries)."
        ),
    },
    {
        "material_id": "SB-SC-M3",
        "wave2_material_ref": "SB-W2-M3",
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
        "diversity_role": "failed prior-day-high breakout; morning range; reversion to VWAP; sector non-confirmation; invalidation",
        "content_note": (
            "Short post using a range-day read in ES futures. Covers: 'we came into "
            "the day sensitive to it being a range day and saw that the important XLE "
            "and XLF sectors were not confirming the upside breakout. Also looking "
            "sketchy at the highs were XLB and XLV.' Then: 'Unable to take out "
            "yesterday's high, we moved back into the morning range (bottom chart). "
            "Note how you didn't need to catch the exact top to recognize that the "
            "upmove was failing and play a reversion back to VWAP as a first target.' "
            "Closing process claim: 'Making the hard trade: It's all about "
            "preparation.' Key semantics: prior-day high, morning range, range-day "
            "call, sector non-confirmation, reversion-to-VWAP target, no need to "
            "catch the exact top."
        ),
    },
    {
        "material_id": "SB-SC-M4",
        "canonical_title": "Catching False Breakouts",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (false-breakout definition and trade; ES + Market Delta + cross-index tell)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2009/07/catching-false-breakouts.html",
        "date": "2009-07-14",
        "effective_content_date": "2009-07-14",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "false-breakout definition; return-to-range; reversion-to-VWAP; cross-index non-confirmation",
        "content_note": (
            "Defines a false breakout: 'A false breakout occurs when we get new highs "
            "or lows following an extended trading range, only to see trade return to "
            "that range. These occur at every time frame.' The example short-term "
            "false break to the downside in ES was 'not confirmed by fresh lows for "
            "the NASDAQ or Russell averages--often a nice tell for false breaks.' "
            "Trading consequence: 'a fade back into the day's range is generally a "
            "great play for a move back to the VWAP. On sustained strength, those "
            "false breaks lead to a complete rotation through the range to the "
            "opposite extreme.' Uses a Market Delta chart."
        ),
    },
    {
        "material_id": "SB-SC-M5",
        "canonical_title": "Trading Patterns: Failed Opening Range Breakout",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (failed opening-range breakout; Russell 2000 ER2 futures + NYSE TICK + volume)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2007/06/trading-patterns-failed-opening-range.html",
        "date": "2007-06-06",
        "effective_content_date": "2007-06-06",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "opening-range boundary; genuine-breakout condition; failed-breakout condition; midpoint target; TICK/volume integration",
        "content_note": (
            "Annotated chart of Russell 2000 (ER2) futures with NYSE TICK and volume "
            "for the morning of 2007-06-01. 'The preopening and opening ranges are "
            "extremely important, because they locate the market's estimate of value.' "
            "'If we get a breakout from the preopening range on expanded volume and "
            "strong NYSE TICK, it means that the market is undergoing a new valuation "
            "... The key principle... is that, if this revaluation is genuine, we "
            "should not return to the prior trading range.' A momentum (volume) peak, "
            "subsequent price peak on reduced upside momentum but very strong TICK, "
            "then failure of positive TICK readings to achieve new highs => 'failed "
            "opening range breakout in the making. Knowing that, we can anticipate a "
            "move back to the midpoint of that opening range; i.e., a return to the "
            "prior level of valuation.' 'Notice how the chart above integrates a "
            "number of market dynamics over time: valuation levels, volume, TICK, and "
            "price.'"
        ),
    },
    {
        "material_id": "SB-SC-M6",
        "canonical_title": "The Relevance of VWAP in a Range Market",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (VWAP reference point in range markets; ES)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2010/03/relevance-of-vwap-in-range-market.html",
        "date": "2010-03-29",
        "effective_content_date": "2010-03-29",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "VWAP definition; return-to-VWAP; range-breakout handicap via TICK/Cumulative Delta/intermarket",
        "content_note": (
            "'The volume-weighted average price (VWAP; red line above) is an excellent "
            "reference point in range bound markets. In a good range trade, we'll tend "
            "to see a narrow value area (volume will be transacted within a narrow "
            "price band) and moves away from value will tend to return back to (and "
            "usually through) VWAP. In a true range trade, we'll also see little slope "
            "to VWAP, as we transact volume relatively evenly above and below that "
            "average price.' 'If you're playing for a range breakout, it often makes "
            "sense to track the distribution of NYSE TICK, Cumulative Delta, and "
            "intermarket themes. Often we'll see buying or selling unable to pierce "
            "VWAP prior to a breakout to the downside or upside. It's the inability of "
            "price to trade through VWAP that shows buying or selling drying up.'"
        ),
    },
    {
        "material_id": "SB-SC-M7",
        "canonical_title": "Notes on Trading a Range Market",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (range-day fade rule; rough VWAP-amplitude symmetry rule; ES)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2010/04/notes-on-trading-range-market.html",
        "date": "2010-04-09",
        "effective_content_date": "2010-04-09",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "range-day call; fade-away-from-VWAP; VWAP-amplitude rough rule; breakout handicap",
        "content_note": (
            "'By making the call of range day, we are prepared to fade moves away from "
            "the day's volume-weighted average price. We can also then focus on how "
            "markets trade above and below VWAP to handicap the odds of a breakout "
            "from the trading range.' 'As a rough rule, I look for the amplitudes of "
            "moves above and below VWAP in a range market to be similar: If we trade "
            "two points above VWAP before retreating, I'll look for a reversal move to "
            "travel two points below VWAP. Focusing on that rule can be helpful in "
            "identifying range extensions that become range breakouts.' Note: the "
            "'two points' amplitude is an example-specific rough rule, not a pinned "
            "universal threshold."
        ),
    },
    {
        "material_id": "SB-SC-M8",
        "canonical_title": "A Simple Trading Template",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (intraday trading template; pivot/overnight/VWAP price levels; breadth + TICK)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2009/02/simple-trading-template.html",
        "date": "2009-02-14",
        "effective_content_date": "2009-02-14",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "range-day template; fade-away-from-VWAP; pivot/overnight/prior-day-high reference levels; TICK+breadth",
        "content_note": (
            "Very simple real-time template: '1) Market opens above or below the "
            "previous day's pivot on low volume and relatively narrow breadth and "
            "TICK: Play for a move back to pivot and consider a range day, with moves "
            "oscillating around VWAP; 2) Market makes a good move on strong/weak TICK "
            "and average or above volume early in the AM and holds above/below pivot "
            "on next pullback: Play for a move to the overnight high/low and/or the "
            "previous day's high/low; 3) ... on strong/weak TICK and average or better "
            "volume: Play for a move to previous day's high/low and R1/S1; 4) ... Play "
            "for a move to R2/S2.' 'If you are playing a range market, you should fade "
            "moves away from VWAP that cannot sustain upside/downside price targets.' "
            "'If you are playing for a directional move up/down, price should stay "
            "above/below the day's VWAP.' Note: template mixes price levels with "
            "breadth and TICK conditions."
        ),
    },
    {
        "material_id": "SB-SC-M9",
        "canonical_title": "Breakouts From Trading Ranges: Making the Identification",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (genuine vs false breakout identification; volume + sector + breadth + VWAP + cross-asset)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2009/02/breakouts-from-trading-ranges-making.html",
        "date": "2009-02-11",
        "effective_content_date": "2009-02-11",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "genuine-vs-false breakout identification; enhanced volume; sector participation; VWAP; cross-asset revaluation",
        "content_note": (
            "Identifies genuine range breakouts: legit breakout => traders jump aboard "
            "+ counter-positioned bail out => 'creates enhanced volume on the breakout "
            "move.' 'The key, then, is recognizing when a breakout is a genuine one "
            "and when it is false. Markets can move out of their ranges, only to fail "
            "to attract volume/participation and fall back toward their "
            "volume-weighted averages (i.e., their previous estimates of value).' "
            "Other than volume expansion, features of range breakouts: '1) Sectors "
            "that have been leading the market should lead the market in the "
            "direction of the break; 2) The vast majority of sectors should "
            "participate in the break, expanding the plurality of advancing or "
            "declining stocks; 3) The market should stay below its volume-weighted "
            "average price ... as it searches for new, lower levels of value; 4) ... "
            "similar revaluations among related asset classes, such as Treasury "
            "instruments, commodities, and currencies.'"
        ),
    },
    {
        "material_id": "SB-SC-M10",
        "canonical_title": "The Trading Process: Day Structure",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (seven day-structure types; range/false-breakout trading toward VWAP)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2009/12/trading-process-day-structure.html",
        "date": "2009-12-30",
        "effective_content_date": "2009-12-30",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "day-structure taxonomy; range day; false upside/downside breakout day; trading toward vs away from VWAP",
        "content_note": (
            "'Day structure, for me as an intraday trader, trumps longer timeframe "
            "trend considerations.' Seven day-structure possibilities: 1) Range Day "
            "(oscillate around an average price value, relatively low volatility, "
            "likely ending not far from its opening price level and/or VWAP); "
            "2) Upside Trend Day; 3) Downside Trend Day; 4) Upside Breakout Day (opens "
            "within a range, builds volume and participation at the upper end, price "
            "breaks above the range, further acceptance with solid volume); "
            "5) Downside Breakout Day; 6) False Upside Breakout Day ('The market opens "
            "within a range and moves above the range, usually with limited "
            "participation and volume that wanes with higher prices, only to fall back "
            "into the range and return toward VWAP. A false upside breakout represents "
            "an extension of range trading conditions.'); 7) False Downside Breakout "
            "Day. 'In range markets and on false breakouts, you'll be trading for "
            "moves toward VWAP and often the prior day's pivot level. In trending and "
            "breakout markets, you'll be trading for moves away from VWAP and toward "
            "the R1/R2/R3 or S1/S2/S3 price levels. In other words, you'll be fading "
            "price strength and weakness in range and false breakout markets and "
            "trading with strength and weakness during trending and breakout "
            "conditions.'"
        ),
    },
    {
        "material_id": "SB-SC-M11",
        "canonical_title": "Anatomy of a False Breakout in the Stock Market",
        "author": "Brett N. Steenbarger, Ph.D.",
        "publisher_channel": "TraderFeed (traderfeed.blogspot.com), official archive",
        "content_type": "official blog post (false breakout anatomy; Russell 2000 ER2 futures + NYSE TICK + volume)",
        "language": "EN",
        "url": "https://traderfeed.blogspot.com/2007/08/anatomy-of-false-breakout-in-stock.html",
        "date": "2007-08-19",
        "effective_content_date": "2007-08-19",
        "provenance": "TRACEABLE_ORIGINAL",
        "access": "FREE_PUBLIC_UNAUTHENTICATED",
        "diversity_role": "false-breakout anatomy; TICK thrust failure; return to range midpoint; enhanced-volume breakout",
        "content_note": (
            "Annotated chart of the Russell 2000 (ER2) futures afternoon trade. 'For "
            "the better part of an hour, we're trading in a range, but the "
            "distribution of the NYSE TICK during that range was positive. We then "
            "break out of the range on enhanced volume, as buyers lift offers.' The "
            "time-trend pattern triggered on 14 of the last 16 bars closing higher; "
            "'From that point forward, thrusts in the NYSE TICK above 1000 are no "
            "longer able to generate higher prices; there is a stalling out of the "
            "rally. This emboldens the sellers, who proceed to take the market back "
            "to the midpoint of the prior trading range.' Opposite time-trend pattern "
            "on enhanced volume (16 of prior 19 bars closing lower). 'Much of the "
            "market's short-term swings consists of counter-movement once markets "
            "become too one-sided.'"
        ),
    },
]

SELECTION_CRITERIA = [
    "official author's own TraderFeed archive (traderfeed.blogspot.com) / TRACEABLE_ORIGINAL",
    "free/public/unauthenticated access state (verified by direct fetch on 2026-08-19)",
    "pre-2024 original posts (effective content date before the frozen corpus start)",
    "stable attributable URL, title, and post date",
    "post directly resolves one or more of the required false-breakout / range-reversion "
    "semantic fields (definition, range boundary, candidate high/low, morning range, "
    "failed-breakout condition, return-to-range, invalidation, VWAP, entry permission, "
    "target, breakout-vs-reversion separation, volume/participation/TICK/Delta/sector "
    "roles, instrument/timeframe scope)",
    "not broadened into unrelated psychology/process material beyond the required semantics",
    "not selected by expected historical performance",
]

OPTIONAL_PAID_CANDIDATES = [
    {
        "source_identity": "Market Delta (marketdelta.com) - commercial order-flow / "
        "volume-at-bid-vs-offer software referenced by the source for 'Market Delta' "
        "readings (green/red volume at offer vs bid)",
        "why_it_might_matter": "The source's explicit entry trigger for the range "
        "reversion short requires green Market Delta (more volume at offer than bid); "
        "this surface is not present in 1-minute OHLCV.",
        "evidence_gap_it_could_fill": "Bid/offer volume and delta readings used by the "
        "source for the entry/confirmation/exit conditions.",
        "access_class": "PAID_SOFTWARE_SUBSCRIPTION (not purchased; listed for awareness only)",
    },
    {
        "source_identity": "NYSE TICK feed (or equivalent breadth/TICK data product)",
        "why_it_might_matter": "The source's genuine-vs-false breakout identification and "
        "entry/exit timing rely on NYSE TICK (distribution, extremes, thrusts); not in "
        "the Chinese-futures corpus.",
        "evidence_gap_it_could_fill": "Breadth/TICK distribution and thrust surfaces for "
        "breakout identification.",
        "access_class": "PAID_OR_SUBSCRIPTION_DATA (not purchased; listed for awareness only)",
    },
    {
        "source_identity": "US sector/index breadth (XLE/XLF/XLB/XLV, SPX, NASDAQ, "
        "Russell, advance-decline) data feeds",
        "why_it_might_matter": "Sector participation / non-confirmation and cross-index "
        "non-confirmation are used by the source as counterevidence and genuine-breakout "
        "features; the project corpus is Chinese futures (cu/al/ni/au/ag/rb).",
        "evidence_gap_it_could_fill": "US equity breadth and sector confirmation surfaces.",
        "access_class": "PAID_OR_SUBSCRIPTION_DATA (not purchased; listed for awareness only)",
    },
    {
        "source_identity": "Market Profile / auction value-area data and software "
        "(Steidlmayer/Dalton lineage) referenced via 'the value area from the prior day'",
        "why_it_might_matter": "The reversal-setup range-edge definition cites prior-day "
        "value area, a Market Profile construct not derivable directly from 1-minute "
        "OHLCV without additional interpretation.",
        "evidence_gap_it_could_fill": "Value-area / TPO distribution inputs for the "
        "reversal range-edge definition.",
        "access_class": "PAID_SOFTWARE_OR_DATA (not purchased; listed for awareness only)",
    },
]

# ---------------------------------------------------------------------------
# Semantic-field resolutions (19 required fields, source evidence only)
# ---------------------------------------------------------------------------
# Each record binds one required semantic field to the source evidence that
# resolves (or fails to resolve) it. `classification` is one of:
#   EXPLICITLY_PINNED | PARTIALLY_PINNED | NOT_PINNED | REQUIRES_UNAVAILABLE_INPUT
# No field is filled with a preferred trading definition.

SEMANTIC_FIELDS = [
    {
        "semantic_field": "GENERAL_MARKET_DIRECTION",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:closing:MULTI_TIMEFRAME; "
            "SB-SC-M1:walking-through-trade-setup:step:5_NO_TRADE_WAIT_RALLY; "
            "SB-SC-M1:walking-through-trade-setup:step:7_STOP_AND_TARGET"
        ),
        "source_evidence": (
            "The source lists 'the market's general direction' as focus element 1 and "
            "refers to 'the direction of the general market trend' and 'the market's "
            "longer-term (day session) direction' as the direction in which the "
            "reversion trade intends to resume movement."
        ),
        "source_context_note": (
            "General direction is used as directional context, not a defined trigger. "
            "In the example it was assessed partly with net volume (Market Delta) and "
            "TICK, which the project does not own; no operational measure is given by "
            "the source."
        ),
        "source_vs_project": (
            "SOURCE: qualitative 'general direction' of the market. PROJECT: any "
            "measure (e.g., a moving average or higher-timeframe trend proxy) would be "
            "an INFERRED interpretation, not an EXPLICIT source semantic."
        ),
    },
    {
        "semantic_field": "TRADING_RANGE_BOUNDARY",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:6_CANDIDATE_HIGHS; "
            "SB-SC-M2:three-basic-trade-setups:section:1_REVERSAL_TRADES; "
            "SB-SC-M5:failed-opening-range:body:PREOPENING_RANGE; "
            "SB-SC-M4:catching-false-breakouts:body:FALSE_BREAKOUT_DEFINITION"
        ),
        "source_evidence": (
            "'I now view the market as in a trading range defined by the 13:30 lows "
            "and the 13:39 highs' (example-specific); reversal trades occur at 'the "
            "edges of a trading range (a consolidation area, the value area from the "
            "prior day)'; false breakout is 'new highs or lows following an extended "
            "trading range'; preopening/opening ranges 'locate the market's estimate "
            "of value'."
        ),
        "source_context_note": (
            "The concept of a trading range is explicit, but the source gives no "
            "general rule for fixing range boundaries; the walk-through boundary is a "
            "discretionary bar-level example. The prior-day value-area variant is a "
            "Market Profile construct not derivable from 1-minute OHLCV."
        ),
        "source_vs_project": (
            "SOURCE: range boundaries left to trader discretion / example-specific "
            "bars, or value area. PROJECT: any fixed boundary rule would be an "
            "INFERRED interpretation; no arbitrary boundary may be promoted to source "
            "semantics."
        ),
    },
    {
        "semantic_field": "CANDIDATE_HIGH_OR_LOW",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:6_CANDIDATE_HIGHS; "
            "SB-SC-M1:walking-through-trade-setup:closing:MULTI_TIMEFRAME"
        ),
        "source_evidence": (
            "'I declare to myself that the highs of the 13:39 bar are my 'candidate "
            "highs' for this bounce'; closing lists 'a candidate price high or low' as "
            "focus element 3 and 'an entry that leans on this candidate high or low' "
            "as element 4."
        ),
        "source_context_note": (
            "The concept is explicit, but what makes a bar a 'candidate' high/low "
            "(selection rule) is the trader's real-time discretionary declaration, not "
            "a defined procedure. In the example it was supported by TICK/volume/offer-"
            "volume non-expansion, which the project does not own."
        ),
        "source_vs_project": (
            "SOURCE: candidate high/low is a discretionary label. PROJECT: any rule "
            "for identifying candidate highs/lows would be an INFERRED "
            "operationalization, not an EXPLICIT source semantic."
        ),
    },
    {
        "semantic_field": "MORNING_RANGE_BOUNDARY",
        "classification": "NOT_PINNED",
        "source_anchor": (
            "SB-SC-M3:making-hard-trade:body:FAILED_BREAKOUT_REVERSION; "
            "SB-SC-M5:failed-opening-range:body:PREOPENING_AND_OPENING_RANGES"
        ),
        "source_evidence": (
            "'Unable to take out yesterday's high, we moved back into the morning "
            "range'; the opening range is described as locating 'the market's estimate "
            "of value'. No start/end definition of 'morning range' / 'opening range' "
            "is given."
        ),
        "source_context_note": (
            "The morning/opening range is referenced but never defined by exact "
            "boundaries (e.g., first N minutes, high/low of a named interval). "
            "Observable prices exist, but the source semantics of the boundary are "
            "NOT_PINNED."
        ),
        "source_vs_project": (
            "SOURCE: morning range referenced without a definition. PROJECT: any "
            "morning-range boundary (e.g., first 30/60 minutes) would be invented, "
            "not source-pinned."
        ),
    },
    {
        "semantic_field": "FALSE_BREAKOUT_DEFINITION",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M4:catching-false-breakouts:body:FALSE_BREAKOUT_DEFINITION; "
            "SB-SC-M10:day-structure:item:6_FALSE_UPSIDE_BREAKOUT_DAY; "
            "SB-SC-M10:day-structure:item:7_FALSE_DOWNSIDE_BREAKOUT_DAY"
        ),
        "source_evidence": (
            "'A false breakout occurs when we get new highs or lows following an "
            "extended trading range, only to see trade return to that range.' "
            "False Upside/Downside Breakout Day: 'The market opens within a range and "
            "moves above the range, usually with limited participation and volume "
            "that wanes with higher prices, only to fall back into the range and "
            "return toward VWAP.'"
        ),
        "source_context_note": (
            "The definition is explicit and largely price/volume-based (new high/low "
            "after a range, return to the range; waning volume on the breakout leg). "
            "However 'extended trading range' and 'return to that range' are not "
            "quantified, and 'limited participation' invokes breadth/participation "
            "that is not in the corpus."
        ),
        "source_vs_project": (
            "SOURCE: false breakout = new high/low after a range that reverts into the "
            "range; false breakout day = range-open move beyond range with waning "
            "volume/participation, reverting toward VWAP. PROJECT: the unquantified "
            "'extended', 'return', and 'limited participation' components would need "
            "INFERRED definitions."
        ),
    },
    {
        "semantic_field": "FAILED_BREAKOUT_CONDITION",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:6_CANDIDATE_HIGHS; "
            "SB-SC-M5:failed-opening-range:body:FAILED_OPENING_RANGE_BREAKOUT; "
            "SB-SC-M11:anatomy-of-false-breakout:body:TICK_THRUST_FAILURE"
        ),
        "source_evidence": (
            "The source's failed-breakout condition integrates several signals: the "
            "bounce 'does not expand its TICK distribution and does not expand volume "
            "or volume traded at the offer', and price has 'trouble making new highs "
            "relative to the 13:39 bar'; a failed opening range breakout is recognized "
            "from a momentum/volume peak, a price peak on reduced upside momentum but "
            "very strong TICK, then failure of positive TICK to achieve new highs; "
            "thrusts in NYSE TICK above 1000 'are no longer able to generate higher "
            "prices; there is a stalling out of the rally.'"
        ),
        "source_context_note": (
            "Part of the condition is price/volume observable (failure to make new "
            "highs; waning volume). The TICK-distribution, TICK-thrust, and offer-side "
            "volume components are unavailable inputs. The source presents the "
            "integrated read (valuation levels + volume + TICK + price) as the "
            "identification method."
        ),
        "source_vs_project": (
            "SOURCE: failed-breakout identification integrates price + volume + TICK + "
            "offer-side volume. PROJECT: the TICK/offer-side components are not owned; "
            "a price/volume-only subset (new-high failure + waning volume) is "
            "observable but is not the source's full condition and is not threshold-"
            "pinned."
        ),
    },
    {
        "semantic_field": "RETURN_TO_RANGE_CONDITION",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M4:catching-false-breakouts:body:FALSE_BREAKOUT_DEFINITION; "
            "SB-SC-M3:making-hard-trade:body:FAILED_BREAKOUT_REVERSION; "
            "SB-SC-M10:day-structure:item:6_FALSE_UPSIDE_BREAKOUT_DAY"
        ),
        "source_evidence": (
            "'Only to see trade return to that range'; 'moved back into the morning "
            "range'; 'only to fall back into the range and return toward VWAP.'"
        ),
        "source_context_note": (
            "Return to the range is explicit and price-based, but how far back into "
            "the range (extent/touch criterion) is not defined."
        ),
        "source_vs_project": (
            "SOURCE: return into the range / toward VWAP. PROJECT: any exact "
            "'returned-to-range' touch threshold would be INFERRED."
        ),
    },
    {
        "semantic_field": "NEW_HIGH_OR_LOW_INVALIDATION_REFERENCE",
        "classification": "EXPLICITLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:7_STOP_AND_TARGET; "
            "SB-SC-M3:making-hard-trade:body:FAILED_BREAKOUT_REVERSION"
        ),
        "source_evidence": (
            "'My stop is above the 13:39 highs--a move to new highs invalidates my "
            "idea.' 'Unable to take out yesterday's high, we moved back into the "
            "morning range.'"
        ),
        "source_context_note": (
            "The invalidation reference is explicit: a fresh new high/low beyond the "
            "candidate level (or prior day's high) invalidates the reversion read. "
            "Exact stop distance above the level is operational detail, not semantic."
        ),
        "source_vs_project": (
            "SOURCE: new highs/lows beyond the reference invalidate. PROJECT: the "
            "invalidation is directly representable from price; only the reference "
            "level (candidate high / prior-day high) needs an interpreted definition."
        ),
    },
    {
        "semantic_field": "VWAP_DEFINITION_OR_SESSION_REFERENCE",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M6:vwap-in-range-market:body:VWAP_DEFINITION; "
            "SB-SC-M8:simple-trading-template:body:RANGE_MARKET_FADE; "
            "SB-SC-M10:day-structure:body:TOWARD_VS_AWAY_FROM_VWAP"
        ),
        "source_evidence": (
            "'The volume-weighted average price (VWAP) is an excellent reference point "
            "in range bound markets'; 'the day's volume-weighted average price'; "
            "'trading for moves toward VWAP... in range markets and on false "
            "breakouts'; 'fade moves away from VWAP that cannot sustain upside/"
            "downside price targets.'"
        ),
        "source_context_note": (
            "VWAP is explicitly defined as the volume-weighted average price and is "
            "computable from bar price/volume. The session reference is 'the day's "
            "VWAP' / 'day session', but the exact computation window (session start) "
            "is not pinned by the source; the project would need an explicitly defined "
            "project calculation (INFERRED)."
        ),
        "source_vs_project": (
            "SOURCE: VWAP = volume-weighted average price; referenced as the day "
            "session's VWAP. PROJECT: computing VWAP from 1-minute OHLCV under an "
            "explicitly defined session window is a project calculation (INFERRED "
            "window), not an EXPLICIT source window."
        ),
    },
    {
        "semantic_field": "ENTRY_PERMISSION",
        "classification": "REQUIRES_UNAVAILABLE_INPUT",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:7_ENTRY_TRIGGER; "
            "SB-SC-M8:simple-trading-template:body:RANGE_MARKET_FADE"
        ),
        "source_evidence": (
            "Explicit entry permission: 'I sell when we make positive TICK readings "
            "and green Market Delta readings (more volume at offer than bid) that "
            "cannot make fresh price highs.' Price/volume alternative in the template: "
            "'If you are playing a range market, you should fade moves away from VWAP "
            "that cannot sustain upside/downside price targets.'"
        ),
        "source_context_note": (
            "The source's only concrete entry trigger for this family is TICK + "
            "Market Delta based and is NOT_OBSERVABLE with current data. The "
            "price/volume fade alternative ('fade moves away from VWAP that cannot "
            "sustain targets') is not operationally pinned ('cannot sustain' is "
            "undefined) and is not a defined entry trigger."
        ),
        "source_vs_project": (
            "SOURCE: entry requires TICK + Market Delta (explicit); a VWAP fade is "
            "mentioned but not operationalized. PROJECT: cannot reproduce the explicit "
            "trigger without TICK/Delta; any price/volume-only entry rule would be an "
            "INFERRED, not a source-pinned, permission."
        ),
    },
    {
        "semantic_field": "TARGET_BOUNDARY",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:7_STOP_AND_TARGET; "
            "SB-SC-M1:walking-through-trade-setup:step:9_TARGET_LIMITATION; "
            "SB-SC-M3:making-hard-trade:body:FAILED_BREAKOUT_REVERSION; "
            "SB-SC-M2:three-basic-trade-setups:section:1_REVERSAL_TARGETS; "
            "SB-SC-M4:catching-false-breakouts:body:RETURN_TO_VWAP; "
            "SB-SC-M5:failed-opening-range:body:MIDPOINT_TARGET"
        ),
        "source_evidence": (
            "'My profit target is the lows of the trading range'; 'play a reversion "
            "back to VWAP as a first target'; reversal 'initial target will generally "
            "be the midpoint of that range (which may also be the pivot level from the "
            "previous day or week)'; 'a fade back into the day's range is generally a "
            "great play for a move back to the VWAP. On sustained strength, those "
            "false breaks lead to a complete rotation through the range to the "
            "opposite extreme'; 'anticipate a move back to the midpoint of that "
            "opening range.'"
        ),
        "source_context_note": (
            "Multiple explicit target conventions exist (range lows, VWAP, range "
            "midpoint, prior pivot, opposite extreme on sustained strength). The "
            "source does not pin one unique primary target for the family; the pivot/"
            "value-area variants are undefined or unavailable."
        ),
        "source_vs_project": (
            "SOURCE: several target conventions, none uniquely pinned as PRIMARY. "
            "PROJECT: choosing one as THE target would be an INFERRED selection, not "
            "an EXPLICIT source semantic."
        ),
    },
    {
        "semantic_field": "BREAKOUT_VS_RANGE_REVERSION_SEPARATION",
        "classification": "EXPLICITLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:9_TARGET_LIMITATION; "
            "SB-SC-M2:three-basic-trade-setups:body:THREE_SETUPS; "
            "SB-SC-M10:day-structure:body:SEVEN_DAY_STRUCTURES"
        ),
        "source_evidence": (
            "'I'm not playing for a home run breakout trade. If the market moves into "
            "breakout mode, I'll consider that a separate trade and setup.' The "
            "three-basic-setups taxonomy separates Reversal / Breakout / Continuation; "
            "the day-structure taxonomy separates Range Day, Trend Days, Breakout "
            "Days, and False Breakout Days, with trading toward VWAP in range/false-"
            "breakout conditions and away from VWAP in breakout/trend conditions."
        ),
        "source_context_note": (
            "The range-reversion (fade) trade is explicitly separated from a breakout "
            "trade; a breakout is a different setup. This separation is explicit and "
            "consistent across posts."
        ),
        "source_vs_project": (
            "SOURCE: separation explicit. PROJECT: honoring the separation is "
            "source-faithful; merging them would violate source semantics."
        ),
    },
    {
        "semantic_field": "VOLUME_ROLE",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:4_NO_TRADE_NEW_HIGHS; "
            "SB-SC-M1:walking-through-trade-setup:step:8_COVER; "
            "SB-SC-M10:day-structure:item:6_FALSE_UPSIDE_BREAKOUT_DAY; "
            "SB-SC-M9:breakouts-from-ranges:body:ENHANCED_VOLUME; "
            "SB-SC-M9:breakouts-from-ranges:body:GENUINE_VS_FALSE"
        ),
        "source_evidence": (
            "Volume roles are explicit: don't chase highs 'on dwindling volume'; "
            "cover when 'one-minute ES volume picks up'; false breakout day has "
            "'volume that wanes with higher prices'; a genuine breakout 'creates "
            "enhanced volume on the breakout move'; 'Markets can move out of their "
            "ranges, only to fail to attract volume/participation and fall back "
            "toward their volume-weighted averages.'"
        ),
        "source_context_note": (
            "Volume's role (confirms/rejects a breakout; wanes on false breakouts; "
            "picks up at cover) is explicit, but no numeric thresholds are given for "
            "'dwindling', 'wanes', 'enhanced', or 'picks up'."
        ),
        "source_vs_project": (
            "SOURCE: qualitative volume role. PROJECT: any numeric volume threshold or "
            "relative-volume baseline would be INFERRED; ordinary 1-minute volume is "
            "observable but the source does not pin how it is compared."
        ),
    },
    {
        "semantic_field": "PARTICIPATION_ROLE",
        "classification": "REQUIRES_UNAVAILABLE_INPUT",
        "source_anchor": (
            "SB-SC-M10:day-structure:item:6_FALSE_UPSIDE_BREAKOUT_DAY; "
            "SB-SC-M9:breakouts-from-ranges:body:GENUINE_FEATURES; "
            "SB-SC-M8:simple-trading-template:body:ITEM_1"
        ),
        "source_evidence": (
            "False breakout days occur 'usually with limited participation'; genuine "
            "breakouts require 'the vast majority of sectors should participate in "
            "the break, expanding the plurality of advancing or declining stocks'; "
            "the range-day template conditions on 'relatively narrow breadth'."
        ),
        "source_context_note": (
            "Participation/breadth (advance-decline plurality, sector participation, "
            "breadth) is explicitly used to distinguish genuine vs false breakouts "
            "and to identify range days. This surface is NOT in the Chinese-futures "
            "1-minute OHLCV corpus."
        ),
        "source_vs_project": (
            "SOURCE: participation/breadth is a required distinguishing input. "
            "PROJECT: not owned; no OHLCV proxy is authorized."
        ),
    },
    {
        "semantic_field": "TICK_ROLE",
        "classification": "REQUIRES_UNAVAILABLE_INPUT",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:7_ENTRY_TRIGGER; "
            "SB-SC-M1:walking-through-trade-setup:step:8_COVER; "
            "SB-SC-M2:three-basic-trade-setups:section:1_REVERSAL_TARGETS; "
            "SB-SC-M2:three-basic-trade-setups:section:2_BREAKOUT_TRADES; "
            "SB-SC-M5:failed-opening-range:body:TICK_FAILURE; "
            "SB-SC-M11:anatomy-of-false-breakout:body:TICK_THRUST_FAILURE"
        ),
        "source_evidence": (
            "NYSE TICK is integral: entry requires 'positive TICK readings'; cover "
            "uses 'very negative (-1000) TICK readings'; reversals on 'very weak/"
            "strong NYSE TICK'; breakouts on 'very high/low NYSE TICK levels'; "
            "failed opening range breakout from 'failure of positive TICK readings to "
            "achieve new highs'; 'thrusts in the NYSE TICK above 1000 are no longer "
            "able to generate higher prices.'"
        ),
        "source_context_note": (
            "TICK is explicitly integral to entry, exit, genuine-vs-false breakout "
            "identification, and reversal/breakout character. NYSE TICK is NOT owned "
            "by the current corpus and is not OHLCV."
        ),
        "source_vs_project": (
            "SOURCE: TICK is an integral input. PROJECT: not owned; treating it as "
            "optional or proxying it with OHLCV is forbidden."
        ),
    },
    {
        "semantic_field": "MARKET_DELTA_ROLE",
        "classification": "REQUIRES_UNAVAILABLE_INPUT",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:step:7_ENTRY_TRIGGER; "
            "SB-SC-M1:walking-through-trade-setup:step:6_CANDIDATE_HIGHS; "
            "SB-SC-M2:three-basic-trade-setups:section:3_CONTINUATION_TRADES"
        ),
        "source_evidence": (
            "Market Delta (volume at offer vs bid) is integral: entry requires 'green "
            "Market Delta readings (more volume at offer than bid)'; candidate-high "
            "non-confirmation includes 'does not expand volume or volume traded at "
            "the offer'; continuation trades use 'trending cumulative... Market "
            "Delta' with 'pullbacks in TICK and Delta' as entries."
        ),
        "source_context_note": (
            "Market Delta / bid-vs-offer volume is explicitly integral to the "
            "entry/confirmation logic of the flagship walk-through. It is NOT present "
            "in 1-minute OHLCV and is not ordinary volume."
        ),
        "source_vs_project": (
            "SOURCE: Market Delta is an integral input. PROJECT: not owned; ordinary "
            "1-minute volume is not a faithful substitute."
        ),
    },
    {
        "semantic_field": "SECTOR_OR_CROSS_MARKET_CONFIRMATION_ROLE",
        "classification": "REQUIRES_UNAVAILABLE_INPUT",
        "source_anchor": (
            "SB-SC-M3:making-hard-trade:body:SECTOR_NON_CONFIRMATION; "
            "SB-SC-M9:breakouts-from-ranges:body:GENUINE_FEATURES; "
            "SB-SC-M4:catching-false-breakouts:body:CROSS_INDEX_TELL; "
            "SB-SC-M2:three-basic-trade-setups:section:2_BREAKOUT_TRADES"
        ),
        "source_evidence": (
            "Sector non-confirmation is used as counterevidence to an upside breakout "
            "(XLE/XLF not confirming; XLB/XLV sketchy at highs); genuine breakouts "
            "require leading sectors to lead and 'similar revaluations among related "
            "asset classes, such as Treasury instruments, commodities, and "
            "currencies'; false breaks can be telegraphed by cross-index non-"
            "confirmation ('not confirmed by fresh lows for the NASDAQ or Russell "
            "averages'); breakout confirmation includes cross-market repricing."
        ),
        "source_context_note": (
            "Sector/index breadth and cross-market confirmation are explicit and "
            "integral to the family's identification/confirmation. These surfaces are "
            "not in the Chinese-futures corpus."
        ),
        "source_vs_project": (
            "SOURCE: sector/cross-market confirmation is an integral input. PROJECT: "
            "not owned; no proxy is authorized."
        ),
    },
    {
        "semantic_field": "INSTRUMENT_SCOPE",
        "classification": "EXPLICITLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:body:ES_FUTURES; "
            "SB-SC-M5:failed-opening-range:body:ER2_FUTURES; "
            "SB-SC-M11:anatomy-of-false-breakout:body:ER2_FUTURES; "
            "SB-SC-M9:breakouts-from-ranges:body:ES_30MIN; "
            "SB-SC-M2:three-basic-trade-setups:section:2_BREAKOUT_TRADES"
        ),
        "source_evidence": (
            "The source's tradeable instruments in the false-breakout / range-"
            "reversion examples are US equity-index futures: ES (S&P 500 E-mini) and "
            "ER2 (Russell 2000 futures), in an SPX/NYSE/NASDAQ/Russell context, with "
            "US sectors (XLE/XLF/XLB/XLV) and US index breadth."
        ),
        "source_context_note": (
            "SOURCE_INSTRUMENT_SCOPE_EXPLICIT = US_EQUITY_INDEX_FUTURES (ES, ER2) + "
            "US_INDEX_AND_SECTOR_BREADTH. No source statement mentions Chinese futures "
            "or commodity futures as tradeable instruments for this method."
        ),
        "source_vs_project": (
            "SOURCE: scope explicitly US equity-index futures / US index breadth. "
            "PROJECT: corpus is Chinese futures (cu/al/ni/au/ag/rb); transfer is NOT "
            "source-supported (see instrument-transfer analysis in the dossier)."
        ),
    },
    {
        "semantic_field": "TIMEFRAME_SCOPE",
        "classification": "PARTIALLY_PINNED",
        "source_anchor": (
            "SB-SC-M1:walking-through-trade-setup:closing:MULTI_TIMEFRAME; "
            "SB-SC-M4:catching-false-breakouts:body:FALSE_BREAKOUT_DEFINITION; "
            "SB-SC-M10:day-structure:body:DAY_STRUCTURE_TRUMPS"
        ),
        "source_evidence": (
            "'The type of pattern I'm illustrating above occurs on multiple time "
            "frames. A key to trading this way is being able to follow one market "
            "across many time frames (which is different from following multiple "
            "markets in a single time frame)'; 'These [false breakouts] occur at "
            "every time frame'; day structure 'trumps longer timeframe trend "
            "considerations' for the intraday trader."
        ),
        "source_context_note": (
            "Multi-timeframe applicability is explicit, but the source emphasizes "
            "'follow ONE market across many time frames' (same-market multi-"
            "timeframe), not multiple markets. No single operating timeframe is "
            "pinned (examples use 1-min, 3-min, 30-min bars)."
        ),
        "source_vs_project": (
            "SOURCE: pattern occurs across time frames of the same market. PROJECT: "
            "choosing a specific operating bar-timeframe for the Chinese-futures "
            "corpus would be an INFERRED choice; the source does not pin one."
        ),
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
    # EvidenceLedger import documents that the SOURCE_ONLY policy is hosted by
    # the project ResearchFirewall/evidence spine and keeps the import graph
    # exercised. The runner itself holds no market data.
    _ = EvidenceLedger

    bundle_hash = _bundle_hash()
    material_records = _material_records()

    # ---- B: source bundle manifest (predeclared) --------------------------
    manifest = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_BUNDLE_STEENBARGER_FALSE_BREAKOUT_SEMANTIC",
        "manifest_version": "1.0",
        "bundle_id": BUNDLE_ID,
        "bundle_name": BUNDLE_NAME,
        "canonical_bundle_hash": bundle_hash,
        "selected_on": "2026-08-19",
        "retrieval_mode": RETRIEVAL_MODE,
        "package": (
            "TARGETED_SOURCE_SEMANTIC_COMPLETION_STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_V0_1"
        ),
        "wave2_bundle_reference": (
            "SB-W2-PUBLIC-STEENBARGER-V1 (docs/evidence/"
            "HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST.json); the first "
            "three materials are the accepted Wave 2 bundle posts."
        ),
        "source_admission_reference": (
            "docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md -> "
            "SRC-STEENBARGER / MAT-STEENBARGER-TRADERFEED and "
            "docs/research/source_dossiers/SOURCE_DOSSIER_STEENBARGER_V0_1.md"
        ),
        "selection_criteria": SELECTION_CRITERIA,
        "selection_basis_note": (
            "Selection based on provenance + free/public access + anchor quality + "
            "direct relevance to the required false-breakout / range-reversion "
            "semantics. NEVER based on expected trading performance, backtest quality, "
            "or ease of producing a strategy."
        ),
        "source_substitution": {
            "occurred": "NO",
            "note": (
                "All eleven posts were verified accessible (FREE_PUBLIC_UNAUTHENTICATED) "
                "with sufficient source-anchor quality and directly resolve required "
                "semantics; no substitution was required."
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
        / "HUMAN_PLAYBOOK_SOURCE_BUNDLE_STEENBARGER_FALSE_BREAKOUT_SEMANTIC_V0_1.json"
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
            f"{BUNDLE_ID}: 11 official free/public pre-2024 Brett Steenbarger "
            "TraderFeed posts (2007-08-04, 2009-01-27, 2009-05-15, 2009-07-14, "
            "2007-06-06, 2010-03-29, 2010-04-09, 2009-02-14, 2009-02-11, "
            "2009-12-30, 2007-08-19) on traderfeed.blogspot.com; see "
            "docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_STEENBARGER_FALSE_BREAKOUT_SEMANTIC_V0_1.json"
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
        raise RuntimeError("SOURCE_ONLY semantic-completion runner is not verified")

    # ---- Protected-outcome technical denial (engineering proof, once) -----
    denial = runner.request_protected_market_outcome("ENGINEERING_PROOF_ONLY_NO_RETRIEVAL")
    if denial.outcome != "DENIED" or denial.reason != "SOURCE_ONLY_TECHNICAL_DENIAL":
        raise RuntimeError(f"Unexpected denial result: {denial}")

    # ---- Record semantic-field resolutions through the provenance surface --
    # claim_status carries the source-resolution classification for this
    # semantic-completion artifact type (EXPLICITLY_PINNED / PARTIALLY_PINNED /
    # NOT_PINNED / REQUIRES_UNAVAILABLE_INPUT), not the claim-extraction
    # EXPLICIT/INFERRED/UNKNOWN status; this is documented in the session JSON.
    for idx, field in enumerate(SEMANTIC_FIELDS, start=1):
        runner.record_claim(
            ClaimRecordDraft(
                claim_id=f"S-SC-{idx:02d}-{field['semantic_field']}",
                source_id=bundle.source_bundle_id,
                source_anchor=field["source_anchor"],
                claim_status=field["classification"],
                source_excerpt_short_or_paraphrase=field["source_evidence"],
                source_only_session_id=session.session_id,
                created_at=CREATED_AT,
            )
        )

    # ---- C: SOURCE_ONLY session evidence + semantic resolutions -----------
    session_record = {
        "artifact": "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_STEENBARGER_FALSE_BREAKOUT_SEMANTIC",
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
            "TARGETED_SOURCE_SEMANTIC_COMPLETION_STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_V0_1. "
            "Resolves source semantics only; no Playbook Contract is drafted by this "
            "session."
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
            "For these semantic-completion records, claim_status carries the source "
            "resolution classification (EXPLICITLY_PINNED / PARTIALLY_PINNED / "
            "NOT_PINNED / REQUIRES_UNAVAILABLE_INPUT). This is a semantic-completion "
            "artifact type distinct from the claim-extraction EXPLICIT/INFERRED/"
            "UNKNOWN status of the Claim Schema v1.0."
        ),
        "recorded_resolution_count": len(output.records),
        "recorded_resolution_ids": [r.claim_id for r in output.records],
        "semantic_fields": SEMANTIC_FIELDS,
    }
    session_path = (
        REPO_ROOT
        / "docs"
        / "evidence"
        / "HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_STEENBARGER_FALSE_BREAKOUT_SEMANTIC_V0_1.json"
    )
    _write_json(session_path, session_record)

    # ---- Console summary ---------------------------------------------------
    classification_counts: dict[str, int] = {}
    for field in SEMANTIC_FIELDS:
        classification_counts[field["classification"]] = (
            classification_counts.get(field["classification"], 0) + 1
        )
    print(f"SOURCE_ONLY_VERIFIED={verified}")
    print(f"DENIAL_OUTCOME={denial.outcome}")
    print(f"DENIAL_REASON={denial.reason}")
    print(f"SEMANTIC_FIELDS={len(SEMANTIC_FIELDS)}")
    print(f"CLASSIFICATION_COUNTS={classification_counts}")
    print(f"BUNDLE_HASH={bundle_hash}")
    print(f"MATERIALS={len(MATERIALS)}")
    print(f"MANIFEST={manifest_path.relative_to(REPO_ROOT).as_posix()}")
    print(f"SESSION={session_path.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
