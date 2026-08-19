# RASCHKE_HOLY_GRAIL_PLAYBOOK_HANDOFF_V0_1

> Version: 0.1
> Date: 2026-08-20
> Status: HANDOFF ONLY / NON_FROZEN / PRE_OUTCOME / SOURCE_ONLY
> Family: `RASCHKE_HOLY_GRAIL_PULLBACK`
> Semantic completion: `docs/research/semantic_completion/RASCHKE_HOLY_GRAIL_SEMANTIC_COMPLETION_V0_1.md`
> SOURCE_ONLY session: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json`
> Source bundle: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json`
>
> `PLAYBOOK_CONTRACT_CREATED=NO`
> `PRIMARY_LOCKED=NO`
> `OPERATIONALIZED=NO`
> `VALIDATED=NO`
> `BACKTEST_AUTHORIZED=NO`
> `PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES`
> `NO_CANDIDATE_OUTCOME_DATA_USED=YES`

---

## 1. Handoff intent

This handoff documents the source-faithful semantic completion of the
`RASCHKE_HOLY_GRAIL_PULLBACK` family (strong-trend / ADX context + pullback to a
20-period exponential moving average). The semantic-completion package returned
`PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES`.

This is a **handoff, not a Playbook Contract**. It defines what a later
operationalization lane must honor so that a full trading-loop Playbook Contract
can be drafted **without inventing critical trading-loop semantics**. No
Playbook Contract code is instantiated here: Lane B2 (the generic Playbook
Contract bridge) is still being integrated independently. No outcome testing,
parameter search, or validation access is authorized by this handoff.

## 2. Family

```text
RASCHKE_HOLY_GRAIL_PULLBACK
```

Concept: in a strong trend (14-period ADX > 30 and rising; market broke out of
an extended trading range and makes new momentum highs), buy the pullback to the
20-period exponential moving average, entering on a buy stop above the high of
the previous bar, with a protective sell stop at the newly formed swing low, and
trail as profits grow. Sells are the mirror ("sells reversed").

The Holy Grail name/rule lineage is shared with Larry Connors (`Street Smarts`,
Raschke & Connors). The 1993 pullback-to-20-EMA practice and the 2004
cross-timeframe setup are Raschke's own words in the official interviews. The
lineage overlap is disclosed and is **not** counted as independent confirmation.

## 3. Core source anchors (short; full records in the session evidence)

- 4-step Holy Grail buy rules: `SR-V0-M01:august1997:section:HOLY_GRAIL_RULES`
  (1997 AIQ): 14-period ADX > 30 and rising; retracement to the 20-period
  exponential moving average (usually accompanied by a turndown in ADX); when
  price touches the 20-period MA, put a buy stop above the high of the previous
  bar; once filled, enter a protective sell stop at the newly formed swing low;
  trail stops as profits grow.
- Pullback-to-EMA framework: `SR-V0-M02:discerning-trader:section:PULLBACK_TO_MA`
  (1993 S&C): "If there is a trend, I'll try to always look for buying a
  pullback to a moving average... I personally use a 20-period exponential moving
  average on all my markets."
- ADX no-trade rules: `SR-V0-M02:discerning-trader:section:ADX_RULES` (avoid
  ADX<20 declining; do not fade ADX>32 rising).
- Holy Grail across time frames: `SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP`
  (2004 Active Trader): "When the market breaks out of an extended trading range
  and makes new momentum highs, there is a sequence that typically unfolds.
  Price first pulls back to the 20-bar EMA... then the same retracement will
  occur on the 30-minute chart, then the 60-minute chart, then the 120-minute
  time frame... each retracement has to be preceded by a 14-bar ADX reading
  above 30 on that time frame."
- Management/exit: `SR-V0-M04:rituals:section:MANAGEMENT_EXIT` (exit on first
  reaction/pause when giving back more than it should; take at least half off at
  a price objective when continuation is uncertain).
- No-trade: `SR-V0-M01:august1997:section:MARKET_TIMING` (do not buy in the
  middle of a trading range); `SR-V0-M03:raschke0204:section:BREAKOUT_GUESS_FAILURE`
  (do not guess breakouts).
- Failure/counterexample: `SR-V0-M01:august1997:section:HOLY_GRAIL_RULES`
  (Eaton Corp: "no reason to be in this trade").

## 4. Family readiness summary (27 fields)

| # | semantic field | source classification |
|---|---|---|
| 1 | TREND_CONTEXT_DEFINITION | PARTIALLY_PINNED (ADX>30&rising explicit; extended-range/momentum-highs qualitative) |
| 2 | ADX_PERIOD | EXPLICITLY_PINNED (14) |
| 3 | ADX_THRESHOLD | EXPLICITLY_PINNED (>30) |
| 4 | ADX_RISING_OR_LEVEL_REQUIREMENT | EXPLICITLY_PINNED (>30 AND rising; slope measurement INFERRED) |
| 5 | MOVING_AVERAGE_TYPE | EXPLICITLY_PINNED (exponential) |
| 6 | MOVING_AVERAGE_PERIOD | EXPLICITLY_PINNED (20) |
| 7 | MOVING_AVERAGE_PRICE_INPUT | NOT_PINNED (source silent; project convention INFERRED) |
| 8 | PULLBACK_DEFINITION | PARTIALLY_PINNED (target = 20 EMA explicit; structure not defined) |
| 9 | PULLBACK_TOUCH_OR_PENETRATION_RULE | PARTIALLY_PINNED (touch explicit; bar-level touch definition INFERRED) |
| 10 | ENTRY_TRIGGER | EXPLICITLY_PINNED (price touches 20 EMA -> buy stop above previous-bar high) |
| 11 | ENTRY_ORDER_TYPE | EXPLICITLY_PINNED (buy stop / sell stop) |
| 12 | ENTRY_OFFSET | PARTIALLY_PINNED (above previous-bar high; tick offset INFERRED) |
| 13 | LONG_RULE | EXPLICITLY_PINNED (4-step buy rules) |
| 14 | SHORT_RULE | EXPLICITLY_PINNED ("sells reversed") |
| 15 | INITIAL_STOP | EXPLICITLY_PINNED (protective sell stop at newly formed swing low) |
| 16 | POST_ENTRY_INVALIDATION | EXPLICITLY_PINNED (swing-low protective stop) |
| 17 | STOP_ADJUSTMENT_IF_ANY | PARTIALLY_PINNED ("trail stops as profits grow"; mechanics INFERRED) |
| 18 | PROFIT_TARGET | PARTIALLY_PINNED (take half at a price objective; no numeric target) |
| 19 | EXIT_TRIGGER | PARTIALLY_PINNED (trail / first-reaction give-back exit / stop process) |
| 20 | TIME_EXIT_IF_ANY | NOT_PINNED (no source time-exit) |
| 21 | REENTRY_RULE_IF_ANY | NOT_PINNED (no source re-entry rule) |
| 22 | NO_TRADE | PARTIALLY_PINNED (middle-of-range; ADX<20 declining; don't fade ADX>32 rising; no guessing) |
| 23 | FAILURE_OR_COUNTEREXAMPLE | PARTIALLY_PINNED (Eaton Corp failure example; no systematic ledger) |
| 24 | TIMEFRAME_SCOPE | PARTIALLY_PINNED (multi-timeframe explicit; no unique operating timeframe) |
| 25 | INSTRUMENT_SCOPE | EXPLICITLY_PINNED (US equities / US index examples) |
| 26 | COMMODITY_FUTURES_SCOPE | NOT_PINNED (SOURCE_SUPPORTS_COMMODITY_FUTURES=UNKNOWN) |
| 27 | CURRENT_PROJECT_PRODUCT_TRANSFER | INFERRED_PROJECT_TRANSFER (SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN) |

Counts:

```text
SEMANTICS_EXPLICITLY_PINNED=12
SEMANTICS_SOURCE_PERMITTED_MULTIPLE_VARIANTS=0
SEMANTICS_PARTIALLY_PINNED=10
SEMANTICS_NOT_PINNED=4
SEMANTICS_REQUIRES_UNAVAILABLE_INPUT=0
SEMANTICS_INFERRED_PROJECT_TRANSFER=1
```

## 5. Source-pinned trading loop (what is already pinned)

```text
CONTEXT        : 14-period ADX > 30 and rising; extended-range breakout + new momentum highs
SETUP          : retracement/pullback of price to the 20-period exponential moving average
ENTRY          : when price touches the 20-period EMA, buy stop above the high of the previous bar
                 (sells reversed: sell stop below the low of the previous bar)
INITIAL_RISK   : protective sell stop at the newly formed swing low (source-pinned)
INVALIDATION   : price trading back through the swing low invalidates; plus qualitative
                 "gives back more than it should -> first reaction/pause" (M04)
EXIT           : trail stops as profits grow; take at least half off at a price objective;
                 exit on first reaction/pause when giving back too much
NO_TRADE       : do not buy in the middle of a trading range; avoid ADX<20 declining;
                 do not fade ADX>32 rising; do not guess breakouts
TIMEFRAME      : multi-timeframe explicit (base chart then 30/60/120-minute)
INSTRUMENT     : US equities / US index examples; commodity-futures UNKNOWN; transfer INFERRED
```

## 6. INFERRED conventions the operationalization lane must label (not source facts)

The following are NOT source claims; they are project conventions that the
operationalization lane must choose, document, and label `INFERRED`:

1. `MOVING_AVERAGE_PRICE_INPUT` — the EMA price basis. The source never states
   it. The standard convention is a close-based EMA; if adopted, record it as
   `INFERRED`, never as source fact.
2. "Newly formed swing low" identification — a pivot/leg definition for the
   initial stop must be chosen (`INFERRED`).
3. Trailing mechanics for "trail stops as profits grow" — a deterministic trail
   rule (e.g., swing-based or fixed-distance) must be chosen (`INFERRED`).
4. A numeric profit target / exit trigger convention consistent with the
   qualitative source exits (take-half-at-objective; first-reaction give-back
   exit) (`INFERRED`).
5. ADX "rising" slope measurement window (`INFERRED`).
6. The operating timeframe choice among the explicitly multi-timeframe setup
   (`INFERRED`; the source permits the pattern across timeframes but pins no
   single operating timeframe).
7. Entry offset above the previous-bar high (tick convention) (`INFERRED`).
8. Bar-level "touch" definition for the 20-period EMA (`INFERRED`).

These conventions must be frozen as clearly labeled `INFERRED` project
conventions BEFORE any outcome-bearing test, under Protocol v1.0. They must NOT
be tuned on outcomes.

## 7. Instrument transfer

```text
SOURCE_INSTRUMENT_SCOPE=US_EQUITIES_AND_US_INDEX
SOURCE_SUPPORTS_COMMODITY_FUTURES=UNKNOWN
SOURCE_SUPPORTS_CROSS_MARKET_TRANSFER=UNKNOWN
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
CURRENT_PROJECT_PRODUCT_TRANSFER=INFERRED_PROJECT_TRANSFER
```

- The Holy Grail examples are US equities (Eaton Corp; CHV/CMZ/AXP/ETN) and an
  S&P index context. There is no commodity-futures chart anchor for the Holy
  Grail rules (unlike the NR7 family's cocoa example).
- The M02 "on all my markets" statement is ambiguous and is recorded as lineage
  context, not explicit commodity-futures support.
- Any Chinese-futures (`cu/al/ni/au/ag/rb`) operationalization is an `INFERRED`
  project hypothesis and must not be presented as an explicit source claim.
  `UNKNOWN` means source support is absent, not that project evidence proves the
  setup cannot work.

## 8. Required information surfaces and observability

| Required source input | Classification |
|---|---|
| 14-period ADX (OHLC-derived) | OBSERVABLE_NOW |
| 20-period EMA (price-derived) | OBSERVABLE_NOW (price basis INFERRED) |
| bar highs/lows (entry stop level, swing lows) | OBSERVABLE_NOW |
| price position relative to range / momentum highs | OBSERVABLE_NOW (range/momentum-highs boundary INFERRED) |
| 30/60/120-minute charts (multi-timeframe setup) | OBSERVABLE_NOW (derivable from 1-minute OHLCV) |
| NYSE TICK / breadth / cross-market (context, NOT part of the 4-step rules) | NOT_OBSERVABLE_WITH_CURRENT_DATA (no proxy; not required) |

No OHLCV proxy is authorized for TICK/breadth; they are not part of the
source-pinned 4-step Holy Grail rules.

## 9. Bounded next package (operationalization handoff)

The next lane (after Lane B2 integration) must:

1. Draft the full trading-loop Playbook Contract for
   `RASCHKE_HOLY_GRAIL_PULLBACK` from the source-pinned semantics in section 5,
   labeling every convention in section 6 as `INFERRED`.
2. Choose and freeze the `INFERRED` conventions BEFORE any outcome-bearing test
   (Protocol v1.0 pre-outcome gate).
3. Record `SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN` and label the
   Chinese-futures transfer `INFERRED_PROJECT_TRANSFER` in the Contract.
4. Preserve the no-trade and failure semantics (section 4 fields 22-23) as
   explicit constraints.
5. NOT use outcomes to select any formula/parameter; NOT collapse the shared
   Connors lineage into independent confirmation; NOT use paid material (only
   the awareness-only candidates are recorded).

This handoff does NOT authorize Playbook Contract instantiation, outcome
testing, validation access, or historical-final access.

`NO_CANDIDATE_OUTCOME_DATA_USED=YES`
