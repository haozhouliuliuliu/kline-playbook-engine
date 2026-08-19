# RASCHKE_SELECTED_FAMILY_HANDOFF_V0_1

> Version: 0.1
> Date: 2026-08-19
> Status: SELECTED_FOR_TARGETED_SEMANTIC_COMPLETION / HANDOFF ONLY / NON_FROZEN
> Source: `SRC-RASCHKE`
> Screen package: `docs/research/claim_extraction/HUMAN_PLAYBOOK_RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V0_1.md`
> SOURCE_ONLY session: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_SCREEN_V0_1.json`
> Source bundle: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json`
>
> `PLAYBOOK_CONTRACT_CREATED=NO`
> `PRIMARY_LOCKED=NO`
> `OPERATIONALIZED=NO`
> `VALIDATED=NO`
> `BACKTEST_AUTHORIZED=NO`
> `NO_CANDIDATE_OUTCOME_DATA_USED=YES`

---

## 1. Handoff intent

This handoff documents the **single** source-faithful Raschke family selected by
the screen package for a later **targeted semantic-completion package**. It is a
handoff, not a Playbook Contract. The family must go through a separate targeted
semantic-completion package before any Playbook Contract, non-outcome
operationalization, or outcome testing can be considered.

## 2. Selected family

```text
RASCHKE_CURRENT_DATA_FAMILY_SELECTED=RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT
SELECTED_FAMILY_STATUS=SELECTED_FOR_TARGETED_SEMANTIC_COMPLETION
```

Concept: **range contraction -> expansion / breakout** (the source's "you have to
have some method of measuring the amount of contraction in the market ... that
tells me to switch to a breakout mode"). The pinned contraction measure is the
**NR7 day** (a bar with the narrowest range of the past seven bars). The family
trades the expansion (trend day / breakout) that follows contraction, either by
buying the NR7-day breakout (1993 source) or by bracketing stops around the next
day's early morning range (2004 source).

## 3. Core source anchors (short; full records in the screen dossier)

- NR7 definition: `SR-V0-M02:discerning-trader:section:NR7_BREAKOUT` ("the
  narrowest trading range in the last seven days. The low volatility leads to a
  trend"; "buying the breakout of an NR7 day ... going with the volatility").
- Trend-day definition: `SR-V0-M03:raschke0204:section:TREND_DAY_DEFINITION`
  ("opens on one end of its range and closes on the opposite end, has range
  expansion, and makes a steady pattern of higher highs and higher lows, or vice
  versa").
- Trend-day precursors: `SR-V0-M03:raschke0204:section:TREND_DAY_SETUP`
  (contraction/NR7; large opening gap; approaching new 20-day highs/lows).
- Day-after-NR7 bracket entry: `SR-V0-M03:raschke0204:section:NR7_BRACKET_ENTRY`
  ("bracket stops around the early morning range ... it didn't matter whether
  you bracketed the first 45 minutes range or the first hour's range. If there's
  going to be a trend day, you're going to catch it").
- Contraction-measure umbrella: `SR-V0-M02:discerning-trader:section:CONTRACTION_MEASURE`.

## 4. Family readiness summary (screen package)

| Semantic field | Source classification |
|---|---|
| NR7_DEFINITION | EXPLICITLY_PINNED |
| EARLY_MORNING_RANGE_WINDOW | PARTIALLY_PINNED (45-min or 1-hour both source-stated) |
| BRACKET_ENTRY_AFTER_NR7 | EXPLICITLY_PINNED |
| NR7_BREAKOUT_ENTRY | EXPLICITLY_PINNED |
| TREND_DAY_DEFINITION | EXPLICITLY_PINNED |
| TREND_DAY_PRECURSORS | EXPLICITLY_PINNED (sizes unquantified -> PARTIALLY_PINNED) |
| TREND_DAY_CONFIRMATION | PARTIALLY_PINNED (volume/session observable; breadth = REQUIRES_UNAVAILABLE_INPUT) |
| INVALIDATION_REFERENCE | EXPLICITLY_PINNED (opposite bracket side / fresh behavior failure) |
| EXIT_OR_TARGET_SEMANTICS | PARTIALLY_PINNED ("ride the trend day"; "gives back more than it should") |
| VOLUME_ROLE | PARTIALLY_PINNED ("significant increase" qualitative) |
| TIMEFRAME_SCOPE | PARTIALLY_PINNED (NR7 daily; bracket intraday; multi-timeframe stated) |

## 5. Instrument transfer

```text
SOURCE_INSTRUMENT_SCOPE=US_EQUITY_INDEX_FUTURES_AND_US_EQUITIES_AND_COMMODITY_FUTURES
SOURCE_SUPPORTS_COMMODITY_FUTURES=YES
SOURCE_SUPPORTS_CROSS_MARKET_TRANSFER=UNKNOWN
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
```

- The NR7 / contraction-expansion concept is explicitly shown on a commodity
  futures chart (September Cocoa, 1993 S&C).
- The exact day-after-NR7 bracket practice is stated in an index-futures context
  (S&P); transferring it to `cu/al/ni/au/ag/rb` is **INFERRED**, not an explicit
  source claim.
- Any future Chinese-futures operationalization must be labeled `INFERRED` and
  must not be presented as the same EXPLICIT source claim.

## 6. Required information surfaces and observability

| Required source input | Classification |
|---|---|
| raw bar open/high/low/close | OBSERVABLE_NOW |
| daily bar range (NR7) | OBSERVABLE_NOW |
| session/time (early morning range; daily bar boundary) | OBSERVABLE_NOW (governed metadata) |
| ordinary volume (confirmation) | OBSERVABLE_NOW (raw; "significant" PARTIALLY_PINNED) |
| gaps | OBSERVABLE_NOW |
| 20-day high/low | OBSERVABLE_NOW |
| NYSE TICK / breadth | NOT_OBSERVABLE_WITH_CURRENT_DATA (no proxy) |
| cross-market (DAX/EuroStoxx) | NOT_OBSERVABLE_WITH_CURRENT_DATA (no proxy) |
| bid/ask order flow (scalping, outside family) | NOT_OBSERVABLE_WITH_CURRENT_DATA (no proxy) |

## 7. Bounded next package (targeted semantic-completion)

The next package must be a **targeted semantic-completion package** in a
verified SOURCE_ONLY environment (schema:
`docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`). It must resolve
the exact questions in the screen dossier section 19, including:

1. daily-bar NR7 applied to governed Chinese-futures daily bars;
2. early-morning-range window convention (45-min or 1-hour; record as INFERRED);
3. bracket entry construction and tick-offset convention (INFERRED);
4. measurable trend-day definition without invented thresholds;
5. volume confirmation gating (or keep non-gated qualitative);
6. breadth/TICK handicap separated as unavailable (not proxied);
7. exit/target convention ("ride the trend day / get out when giving back too
   much");
8. instrument transfer recorded as INFERRED;
9. failure/no-trade constraints (volatility-extreme flag failure; no guessing).

It must **not** create a Playbook Contract unless separately authorized, and it
must **not** perform any outcome-bearing testing.

## 8. Boundaries preserved

```text
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PLAYBOOK_CONTRACT_CREATED=NO
```

This handoff is a research-navigation artifact only and does not change any
frozen authority or `CURRENT_STATE.md`.
