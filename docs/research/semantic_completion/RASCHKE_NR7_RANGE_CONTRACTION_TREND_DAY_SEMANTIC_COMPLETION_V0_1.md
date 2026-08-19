# RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_SEMANTIC_COMPLETION_V0_1

> Version: 0.1
> Date: 2026-08-19
> Status: SOURCE_SEMANTIC_COMPLETION / SOURCE_ONLY / NON_FROZEN / PRE_OUTCOME
> Role: RASCHKE_NR7_TARGETED_SEMANTIC_COMPLETION_ENGINEER
> Prompt/spec: `RASCHKE_NR7_TARGETED_SEMANTIC_COMPLETION_V1`
> Retrieval mode: `LOCAL_FREE_PUBLIC_RASCHKE_NR7_SEMANTIC_ONLY`
> Source bundle: `SB-RASCHKE-NR7-SEMANTIC-V1`
> Source bundle hash: `6304a630430871cdfd197ea38a2a22556d7854bff05fd5a7fad20a934bd06f11`
> SOURCE_ONLY session: `SOURCE_ONLY_RASCHKE_NR7_SEMANTIC_V1_20260819`
> Session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json`
> Bundle manifest: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_NR7_SEMANTIC_V0_1.json`
> Base bundle: `SB-RASCHKE-PUBLIC-SCREEN-V1` / `7b11a8f1516696e2e54f9dc0ee4d7785f8f1cd9dad06d52abe15378edd2633bd`
> Schema/authority: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`, `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Integration authority: `docs/reviews/HUMAN_PLAYBOOK_RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_INTEGRATION_REVIEW_V0_1.md`

```text
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PLAYBOOK_CONTRACT_CREATED=NO
```

---

## 0. Decision summary

```text
FAMILY=RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT
PLAYBOOK_SEMANTICALLY_DRAFTABLE=NO
SEMANTICS_EXPLICITLY_PINNED=6
SEMANTICS_SOURCE_PERMITTED_MULTIPLE_VARIANTS=1
SEMANTICS_PARTIALLY_PINNED=9
SEMANTICS_NOT_PINNED=5
SEMANTICS_REQUIRES_UNAVAILABLE_INPUT=1
SEMANTICS_INFERRED_PROJECT_TRANSFER=1
POST_ENTRY_INVALIDATION=NOT_PINNED
INITIAL_STOP=NOT_PINNED
EARLY_RANGE_VARIANTS=EARLY_RANGE_VARIANT_45MIN, EARLY_RANGE_VARIANT_60MIN (both SOURCE_PERMITTED; no unique PRIMARY)
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
SOURCE_ONLY_VERIFIED=YES
PROTECTED_OUTCOME_DENIAL=PASS
PRIMARY_BLOCKER=SOURCE_POST_ENTRY_RISK_SEMANTICS_NOT_PINNED (INITIAL_STOP=NOT_PINNED; POST_ENTRY_INVALIDATION=NOT_PINNED)
```

This package is a **successful source-research result**: it resolves 23
targeted semantic fields for the selected family from the accepted official
free/public Raschke source bundle, and it returns `PLAYBOOK_SEMANTICALLY_DRAFTABLE=NO`.

The source pins the complete **entry** mechanism and the price-based
**trend-day definition**, and it explicitly permits two **early-morning-range
variants** (first-45-minutes and first-hour). It does **not** pin the
**post-entry risk loop**: there is no source-stated `INITIAL_STOP` and no
source-stated `POST_ENTRY_INVALIDATION` for the day-after-NR7
early-morning-range bracket family. Per the integration correction IC-1, the
opposite bracket side is an **entry placement**, not an established source
stop/invalidation. Because a full trading-loop Playbook Contract would still
require invented critical invalidation/stop semantics, the honest decision is
`NO`. A `NO` here is a legitimate, useful result (same discipline as the
accepted Steenbarger negative semantic completion).

No Playbook Contract candidate was created, because doing so would require
inventing the post-entry stop/invalidation boundary.

---

## 1. Authority read

Per the task, the following authorities were read from latest `origin/main`
(`03ae64e950f288854aa9450301d1bdc9ab538f97`):

- `AGENTS.md`
- `OWNER_COLLABORATION_CONTRACT.md`
- `CURRENT_STATE.md`
- `CROSS_PROJECT_OPERATING_CONTRACT.md`
- `TOOL_REGISTRY.md`
- `RESEARCH_DIRECTION.md`
- `docs/research/PARALLEL_WORK_PACKAGE_2026-08-19_V0_1.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`
- `src/research_firewall.py`
- `tests/test_research_firewall.py` (SOURCE_ONLY tests)
- `docs/reviews/HUMAN_PLAYBOOK_RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_INTEGRATION_REVIEW_V0_1.md`

Accepted Raschke screen worker evidence was read at its exact commit
`bd09f9acc4647f9a2240a2f20bf9c919c4d8bb23` on
`parallel/raschke-public-current-data-screen-v01`:

- `docs/research/claim_extraction/HUMAN_PLAYBOOK_RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V0_1.md`
- `docs/research/semantic_completion/RASCHKE_SELECTED_FAMILY_HANDOFF_V0_1.md`
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json`
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_SCREEN_V0_1.json`

All expected authority files were present at the exact baseline. No authority
was reported missing or substituted.

---

## 2. Scope and core question

The task is a **targeted source-semantic completion**, not a backtest, not a
parameter search, not outcome inspection, and not a Playbook implementation.
The family is already selected:

```text
RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT
```

Core question (single final decision):

```text
Does the accepted official free/public Raschke source bundle supply enough
source-faithful semantics for the selected NR7 / range-contraction ->
trend-day breakout family that a later full trading-loop Playbook Contract can
be drafted WITHOUT inventing critical trading-loop semantics?
```

- `YES` requires the remaining unresolved items to be representable explicitly
  as source-permitted variants / clearly labeled project transfer **without**
  inventing critical trading-loop semantics.
- `NO` means a full trading-loop Playbook would still require invented critical
  entry, invalidation, exit, session, or other semantics.
- A `NO` is a successful research result. The task explicitly instructs
  **not to force a YES**.

---

## 3. Source bundle

Bundle: `SB-RASCHKE-NR7-SEMANTIC-V1` — **reuses the exact accepted Raschke
screen bundle materials** that anchor the NR7 / range-contraction ->
trend-day breakout family (all `TRACEABLE_ORIGINAL`,
`FREE_PUBLIC_UNAUTHENTICATED`, effective content date before 2024-01-01).

| material_id | title | date | role in this package |
|---|---|---|---|
| `SR-V0-M02` | The Discerning Trader (S&C) | 1993-09 | NR7 definition + breakout entry (cocoa commodity-futures figure); contraction-measure umbrella; three-day trend structure / carry-overnight; end-of-day handling |
| `SR-V0-M03` | Trading Style and Daily Market Regimen (Active Trader) | 2004-02 | PRIMARY material: NR7 day definition; trend-day definition/precursors/confirmation; day-after-NR7 early-morning-range bracket (45-min vs 1-hour); hold-to-end-of-day / add / hold-part-overnight; no-trade |
| `SR-V0-M04` | The Rituals of Trading (Active Trader) | 2000-08 | management/exit principles (give-back exit, take-half); price-based emphasis; NYSE TICK-as-momentum boundary (unavailable input) |
| `SR-V0-M01` | Short Term Trading Strategies (AIQ) | 1997-08 | no-trade (middle of range); generic stop process; failure example; impulse/thrust cue context |
| `SR-V0-M05` | Traders Toolbox (Active Trader) | 2004-03 | indicator-checklist context; closing breadth / TICK/TIKI unavailable-input boundary; multi-timeframe context |

### 3.1 No additional source was added

The task permits adding another official free/public pre-2024 Raschke source
**only if** it directly resolves one of the open semantic questions. A check of
the official Articles index (`https://lindaraschke.net/articles/`) on
2026-08-19 shows it enumerates **exactly the same** free/public PDFs already in
the accepted screen bundle (Trade Trends, Trading Insights, Traders Toolbox,
Multi-Market Traders Rule, The Rituals of Trading, Short Term Trading
Strategies, Maintain your Mindset, Who are You?, Everything About Electronic
Trading, The Discerning Trader, Trading Style and Daily Market Regimen). No
additional official free/public pre-2024 article directly resolves the open
order/stop semantics.

Official videos/interviews are YouTube-hosted (blocked by 403 in the recorded
environment; no circumvention under `HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`).
Paid books (`Trading Sardines`, `Street Smarts`) and NYSE TICK/breadth data are
listed as awareness-only candidates, not purchased.

```text
NO_ADDITIONAL_SOURCE_ADDED=YES
CHECKED_ON=2026-08-19
OFFICIAL_ARTICLES_INDEX=https://lindaraschke.net/articles/
```

---

## 4. Field-by-field semantic matrix

Classification legend (source evidence only; never filled with a preferred
trading definition):

- `EXPLICITLY_PINNED`: the source gives an explicit, unambiguous semantic
  statement sufficient for faithful representation of the core meaning.
- `SOURCE_PERMITTED_MULTIPLE_VARIANTS`: the source explicitly permits more than
  one discrete variant; no unique PRIMARY is justified; all variants are
  preserved explicitly (never collapsed into a hidden parameter).
- `PARTIALLY_PINNED`: the source gives the concept/role but leaves a
  semantically meaningful boundary, measure, or detail undefined.
- `NOT_PINNED`: the source references the concept but provides no defining
  semantics.
- `REQUIRES_UNAVAILABLE_INPUT`: the source semantics require an information
  surface the project does not own.
- `INFERRED_PROJECT_TRANSFER`: project/AI transfer or interpretation
  hypothesis, not an explicit source claim.

| # | semantic field | classification | primary source anchor(s) |
|---|---|---|---|
| 1 | NR7_DAILY_BAR_DEFINITION | EXPLICITLY_PINNED | M03 TREND_DAY_SETUP; M02 NR7_BREAKOUT (Figure 2) |
| 2 | NR7_LOOKBACK_SEMANTICS | PARTIALLY_PINNED | M03 TREND_DAY_SETUP; M02 Figure 2 caption |
| 3 | NEXT_SESSION_DEFINITION | PARTIALLY_PINNED | M03 NR7_BRACKET_ENTRY |
| 4 | EARLY_MORNING_RANGE_WINDOW | SOURCE_PERMITTED_MULTIPLE_VARIANTS | M03 NR7_BRACKET_ENTRY |
| 5 | BRACKET_ENTRY_LONG_LEVEL | EXPLICITLY_PINNED | M03 NR7_BRACKET_ENTRY |
| 6 | BRACKET_ENTRY_SHORT_LEVEL | EXPLICITLY_PINNED | M03 NR7_BRACKET_ENTRY |
| 7 | ENTRY_ORDER_TYPE | EXPLICITLY_PINNED | M03 NR7_BRACKET_ENTRY |
| 8 | ENTRY_OFFSET_OR_TICK_CONVENTION | NOT_PINNED | M03 NR7_BRACKET_ENTRY |
| 9 | UNTRIGGERED_OPPOSITE_ORDER_CANCELLATION | NOT_PINNED | M03 NR7_BRACKET_ENTRY |
| 10 | SIMULTANEOUS_OR_SAME_BAR_TRIGGER_HANDLING | NOT_PINNED | M03 NR7_BRACKET_ENTRY |
| 11 | POST_ENTRY_INVALIDATION | NOT_PINNED | M03 NR7_BRACKET_ENTRY; M04 MANAGEMENT_EXIT |
| 12 | INITIAL_STOP | NOT_PINNED | M03 NR7_BRACKET_ENTRY; M01 STOP_PROCESS |
| 13 | TREND_DAY_DEFINITION | EXPLICITLY_PINNED | M03 TREND_DAY_DEFINITION |
| 14 | TREND_DAY_CONFIRMATION | PARTIALLY_PINNED | M03 TREND_DAY_CONFIRMATION |
| 15 | ORDINARY_VOLUME_ROLE | PARTIALLY_PINNED | M03 TREND_DAY_CONFIRMATION |
| 16 | BREADTH_TICK_ROLE | REQUIRES_UNAVAILABLE_INPUT | M03 TREND_DAY_CONFIRMATION; M04 TICK_AS_MOMENTUM |
| 17 | EXIT_OR_TARGET | PARTIALLY_PINNED | M03 TREND_DAY_CONFIRMATION; M04 MANAGEMENT_EXIT |
| 18 | END_OF_SESSION_HANDLING | PARTIALLY_PINNED | M03 TREND_DAY_CONFIRMATION; M02 THREE_DAY_STRUCTURE |
| 19 | NO_TRADE | PARTIALLY_PINNED | M03 BREAKOUT_GUESS_FAILURE; M01 MARKET_TIMING |
| 20 | FAILURE_OR_COUNTEREXAMPLE | PARTIALLY_PINNED | M03 NR7_BRACKET_ENTRY / FLAGS_VOLATILITY; M01 HOLY_GRAIL_RULES |
| 21 | TIMEFRAME_SCOPE | PARTIALLY_PINNED | M03 TREND_DAY_SETUP; M04 MANAGEMENT_EXIT |
| 22 | INSTRUMENT_SCOPE | EXPLICITLY_PINNED | M03 TREND_DAY_DEFINITION; M02 NR7_BREAKOUT |
| 23 | CHINESE_FUTURES_TRANSFER_STATUS | INFERRED_PROJECT_TRANSFER | M03 NR7_BRACKET_ENTRY |

Counts:

```text
SEMANTICS_EXPLICITLY_PINNED=6
SEMANTICS_SOURCE_PERMITTED_MULTIPLE_VARIANTS=1
SEMANTICS_PARTIALLY_PINNED=9
SEMANTICS_NOT_PINNED=5
SEMANTICS_REQUIRES_UNAVAILABLE_INPUT=1
SEMANTICS_INFERRED_PROJECT_TRANSFER=1
TOTAL=23
```

### 4.1 EXPLICITLY_PINNED (6)

1. **NR7_DAILY_BAR_DEFINITION** — "such as an NR7 day, which is a bar with the
   narrowest range of the past seven bars" (M03); Figure 2 (M02): "A narrow
   range seven-day (NR7) in today's trading range is the narrowest trading
   range in the last seven days. The low volatility leads to a trend." The NR7
   is a **daily-bar** concept. The daily-bar boundary construction for Chinese
   futures (night-session aggregation / calendar day) is a governed-metadata
   project convention, not defined by the source (recorded separately).
2. **BRACKET_ENTRY_LONG_LEVEL** — "bracket stops around the early morning
   range": the long entry is a **buy stop above the early-morning-range high**.
   (The exact tick offset above the high is NOT_PINNED; separate field.)
3. **BRACKET_ENTRY_SHORT_LEVEL** — the short entry is a **sell stop below the
   early-morning-range low**. (Tick offset below the low is NOT_PINNED.)
4. **ENTRY_ORDER_TYPE** — the source literally says "bracket **stops**", which
   pins the entry order type as **stop orders** (buy stop / sell stop). The
   exact subtype (stop-market vs stop-limit) and resting/OCO state machine are
   operationalization details not defined by the source (see
   UNTRIGGERED_OPPOSITE_ORDER_CANCELLATION = NOT_PINNED).
5. **TREND_DAY_DEFINITION** — "A trend day opens on one end of its range and
   closes on the opposite end, has range expansion, and makes a steady pattern
   of higher highs and higher lows, or vice versa, throughout the day. In the
   index futures, there are two or three trend days a month." The definition is
   explicit and price-based. The numerical thresholds for "range expansion" and
   "steady pattern" are not quantified (operationalization detail).
6. **INSTRUMENT_SCOPE** — `SOURCE_INSTRUMENT_SCOPE=US_EQUITY_INDEX_FUTURES_AND_US_EQUITIES_AND_COMMODITY_FUTURES`.
   The bracket practice is stated in an index-futures (S&P) context ("In the
   index futures, there are two or three trend days a month"); the 2004 context
   also covers US equities; the NR7 / contraction-expansion **concept** is
   explicitly shown on a commodity-futures chart (September Cocoa, 1993).
   `SOURCE_SUPPORTS_COMMODITY_FUTURES=YES`;
   `SOURCE_SUPPORTS_CROSS_MARKET_TRANSFER=UNKNOWN`.

### 4.2 SOURCE_PERMITTED_MULTIPLE_VARIANTS (1)

**EARLY_MORNING_RANGE_WINDOW** — "it didn't matter whether you bracketed the
first 45 minutes range or the first hour's range. If there's going to be a
trend day, you're going to catch it." The source explicitly states that **both**
the first-45-minutes range and the first-hour range worked in her own test.
Neither variant is uniquely primary in the source. **Both identities are
preserved explicitly** as `EARLY_RANGE_VARIANT_45MIN` and
`EARLY_RANGE_VARIANT_60MIN`. No outcome-driven selection between 45m and 60m
was performed or is permitted. The variants are **not** collapsed into a hidden
parameter.

### 4.3 PARTIALLY_PINNED (9)

1. **NR7_LOOKBACK_SEMANTICS** — the lookback length (seven) is explicit, but the
   exact inclusive/exclusive window alignment is ambiguous between the accepted
   source statements: "narrowest range of the past seven bars" (a 7-bar window)
   vs "in today's trading range is the narrowest trading range in the last seven
   days" (today compared with the last seven days). Any project window
   convention is an explicit labeled interpretation.
2. **NEXT_SESSION_DEFINITION** — "the day after an NR7 day" pins the entry
   session as the next trading session; the exact session/bar construction for
   Chinese futures (which session "early morning" maps to; night-session
   aggregation; calendar-day boundary) is a governed-metadata project
   convention (INFERRED).
3. **TREND_DAY_CONFIRMATION** — components are stated: a very large opening
   15-minute bar (Crabel) with the threshold explicitly left to the trader
   ("you can determine the threshold of significance yourself... compare it to
   the past five opening 15-minute bars or the past 20. You can quantify this
   type of thing a zillion different ways"); "a significant increase in volume
   in the first 15 minutes relative to the past two weeks"; leadership
   (IBM/MSFT/INTC/GE); "trendiness between say, 10 and 10:30 or 10:45 a.m.";
   and breadth (advancing minus declining — unavailable, see BREADTH_TICK_ROLE).
   Confirmation is a **handicap**, not the NR7 bracket entry trigger.
4. **ORDINARY_VOLUME_ROLE** — volume is an explicit confirmation/enlargement
   component ("a volume increase" on a higher trending day; "a significant
   increase in volume in the first 15 minutes relative to the past two weeks";
   "if I see volume, trend in the breadth and strong money flows, I'll play for
   a big target"). No numeric threshold or gating is pinned; it is a non-gated
   confirmation component.
5. **EXIT_OR_TARGET** — "ride the trend day": hold to end of day / add / hold
   part overnight on a confirmed trend day; "The minute the market gives back
   more than it should, you get out on the first reaction or pause"; "if the
   market reaches a price objective and you're really not sure if it's going to
   continue, you have to at least take half the position off." Qualitative
   management principles; no numeric target pinned.
6. **END_OF_SESSION_HANDLING** — "I'm looking to hold that position until the
   end of the day, or add to the position during the day, or maybe hold part of
   it overnight"; "The last hour's action is very important to me... if I like
   how it acts at the end of the day I will continue to carry the trade"; "if
   you ever get a middle, or a good trend day... you should always carry that
   trade overnight." Present but qualitative with several allowed options; no
   deterministic end-of-session rule.
7. **NO_TRADE** — "If I try to guess a breakout, I'm wrong 90 percent of the
   time"; "The worst thing you can do in terms of market timing is to buy in the
   middle of a trading range"; "If there's no improvement in volume or breadth,
   the market is more likely to stay within a trading range." Explicit
   constraints but qualitative; no deterministic no-trade gate.
8. **FAILURE_OR_COUNTEREXAMPLE** — NR7 does not guarantee a trend day (the
   bracket catches a trend day only if there is going to be one); breakout-guess
   failure (~90%); flags fail at volatility extremes and in contracting
   volatility ("statistical reliability only comes with a volatility filter");
   Eaton Corp no-trade example. Source-explicit failure context preserved; no
   systematic loss ledger (source-quality limitation, recorded not manufactured).
9. **TIMEFRAME_SCOPE** — NR7 on the daily bar; bracket entry intraday (first
   45-min/hour); confirmation on opening 15-minute bars; management on hourly
   charts. No single operating timeframe is pinned for the whole loop.

### 4.4 NOT_PINNED (5)

1. **ENTRY_OFFSET_OR_TICK_CONVENTION** — the source does not state any tick or
   price offset for placing the bracket stops relative to the early-morning-range
   high/low. (The "one tick above the high" language appears only for the
   separate Three-Day Unfilled Gap Reversal pattern in SR-V0-M01, which is a
   different family and does not transfer.)
2. **UNTRIGGERED_OPPOSITE_ORDER_CANCELLATION** — the source does not state what
   happens to the untriggered opposite bracket order once one side fills. No
   OCO / cancel-on-fill semantics for this bracket are given. (The separate
   gap-reversal "cancel after three sessions" statement belongs to a different
   family.)
3. **SIMULTANEOUS_OR_SAME_BAR_TRIGGER_HANDLING** — the source does not state how
   to handle a bar that trades through both the early-morning-range high and low
   (both bracket sides triggering on the same bar).
4. **POST_ENTRY_INVALIDATION** — see section 6. `NOT_PINNED`.
5. **INITIAL_STOP** — see section 6. `NOT_PINNED`.

### 4.5 REQUIRES_UNAVAILABLE_INPUT (1)

**BREADTH_TICK_ROLE** — "the last and most important thing is that I want to see
trend in the market breadth - the difference between advancing issues and
declining issues" (NYSE TICK); "I use the TICKs like a momentum oscillator...
The bottoms of sell-offs will be accompanied by negative TICK extremes, like
-1,000"; TIKI. These are US-market internals **not owned** by the Chinese-futures
1-minute OHLCV corpus and are not ordinary volume. **No OHLCV proxy is
authorized.** Breadth/TICK is a confirmation handicap, not the NR7 bracket entry
trigger.

### 4.6 INFERRED_PROJECT_TRANSFER (1)

**CHINESE_FUTURES_TRANSFER_STATUS** — transferring the exact day-after-NR7
early-morning-range bracket practice to `cu/al/ni/au/ag/rb` is an **INFERRED
project hypothesis**, not an explicit source claim. The NR7 /
contraction-expansion **concept** has a commodity-futures anchor (cocoa), but
the exact bracket practice is stated in an index-futures (S&P) context. Any
Chinese-futures operationalization must be labeled `INFERRED` and must not
inherit source authority automatically.

---

## 5. 45-minute vs 60-minute rule (SOURCE_PERMITTED_MULTIPLE_VARIANTS)

The 45m/60m decision is **not** made by picking the one that seems better.

```text
EARLY_RANGE_VARIANTS=EARLY_RANGE_VARIANT_45MIN, EARLY_RANGE_VARIANT_60MIN
EARLY_RANGE_VARIANT_STATUS=SOURCE_PERMITTED_MULTIPLE_VARIANTS
UNIQUE_PRIMARY_EARLY_RANGE=NO (no source-justified PRIMARY)
```

The source explicitly states both worked in her own test ("it didn't matter
whether you bracketed the first 45 minutes range or the first hour's range").
No stronger source evidence makes one uniquely primary. Therefore both
identities are preserved explicitly and recorded as
`SOURCE_PERMITTED_MULTIPLE_VARIANTS`. They are **not** collapsed into a hidden
parameter. If a future source-justified PRIMARY emerges, that is a separate
finding; it cannot be selected from outcomes.

---

## 6. Stop / invalidation rule (critical correction)

The bracket statement defines **entry placement** only. It does **not**
automatically prove "after long entry, short bracket = stop" or "after short
entry, long bracket = stop".

Per the integration review IC-1:

```text
INVALIDATION_REFERENCE=NOT_YET_SOURCE_PINNED_FOR_SELECTED_FAMILY
```

A specific search of the source evidence for actual post-entry risk/invalidation
was performed:

- The bracket entry statement (M03) describes entry placement, not a post-entry
  stop.
- The generic management statement "The minute the market gives back more than
  it should, you get out on the first reaction or pause" (M04) is qualitative
  and does not define a unique numerical invalidation boundary.
- The generic stop process "Most often, I'll get out if the market fails to do
  what I thought it would do" (M01) is a discretionary stop process, not a
  pinned stop for this family.
- No source statement establishes that the opposite bracket side is the
  post-entry stop/invalidation for the selected family.

Result:

```text
POST_ENTRY_INVALIDATION=NOT_PINNED
INITIAL_STOP=NOT_PINNED
```

A `NO`/`UNKNOWN` here is an acceptable and deliberate result. Treating the
opposite bracket side as an explicit source invalidation would silently promote
a plausible project inference into source fact, which is forbidden.

---

## 7. Instrument-transfer analysis

```text
SOURCE_INSTRUMENT_SCOPE=US_EQUITY_INDEX_FUTURES_AND_US_EQUITIES_AND_COMMODITY_FUTURES
SOURCE_SUPPORTS_COMMODITY_FUTURES=YES
SOURCE_SUPPORTS_CROSS_MARKET_TRANSFER=UNKNOWN
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
CHINESE_FUTURES_TRANSFER_STATUS=INFERRED_PROJECT_TRANSFER
```

- The NR7 / contraction-expansion **concept** is explicitly shown on a commodity
  futures chart (September Cocoa, 1993 S&C), positive evidence the source
  applies the concept to commodity futures.
- The exact day-after-NR7 early-morning-range **bracket practice** is stated in
  an index-futures (S&P) context; transferring that exact entry/management to
  `cu/al/ni/au/ag/rb` is **not** an explicit source statement.
- Therefore any Chinese-futures operationalization is a separately labeled
  `INFERRED` project hypothesis and does not inherit source authority
  automatically. `UNKNOWN` in the support fields means source support is
  absent, not that project evidence proves the setup cannot work.

---

## 8. Observability matrix

Raw observability does **not** settle source semantics. The table separates
(a) source surface, (b) current project-observable portion, (c) missing
portion, and the resulting semantic classification.

| semantic field | observable on current corpus (1-min OHLCV + governed metadata) | missing / unowned | classification |
|---|---|---|---|
| NR7_DAILY_BAR_DEFINITION | daily bar ranges | daily-bar boundary for Chinese futures (INFERRED convention) | EXPLICITLY_PINNED |
| NR7_LOOKBACK_SEMANTICS | daily bar ranges | window alignment (INFERRED convention) | PARTIALLY_PINNED |
| NEXT_SESSION_DEFINITION | session/day sequence | session boundary construction (INFERRED) | PARTIALLY_PINNED |
| EARLY_MORNING_RANGE_WINDOW | 1-min bars + session metadata | exact start/aggregation (INFERRED); both variants preserved | SOURCE_PERMITTED_MULTIPLE_VARIANTS |
| BRACKET_ENTRY_LONG_LEVEL | range high | tick offset (NOT_PINNED) | EXPLICITLY_PINNED |
| BRACKET_ENTRY_SHORT_LEVEL | range low | tick offset (NOT_PINNED) | EXPLICITLY_PINNED |
| ENTRY_ORDER_TYPE | order semantics | exact subtype / resting state (INFERRED) | EXPLICITLY_PINNED |
| ENTRY_OFFSET_OR_TICK_CONVENTION | tick size from metadata | no source offset | NOT_PINNED |
| UNTRIGGERED_OPPOSITE_ORDER_CANCELLATION | can be modeled | no source cancellation semantics | NOT_PINNED |
| SIMULTANEOUS_OR_SAME_BAR_TRIGGER_HANDLING | intrabar triggers | no source handling | NOT_PINNED |
| POST_ENTRY_INVALIDATION | price behavior | no source boundary (IC-1) | NOT_PINNED |
| INITIAL_STOP | price levels | no source stop | NOT_PINNED |
| TREND_DAY_DEFINITION | OHLCV | thresholds for expansion/steady (INFERRED) | EXPLICITLY_PINNED |
| TREND_DAY_CONFIRMATION | 15-min bar, volume, session window | breadth/TICK (unavailable) | PARTIALLY_PINNED |
| ORDINARY_VOLUME_ROLE | ordinary volume | thresholds / baseline (INFERRED) | PARTIALLY_PINNED |
| BREADTH_TICK_ROLE | — | NYSE TICK / advance-decline | REQUIRES_UNAVAILABLE_INPUT |
| EXIT_OR_TARGET | price/volume | unique target (INFERRED) | PARTIALLY_PINNED |
| END_OF_SESSION_HANDLING | end-of-day price behavior | deterministic rule (INFERRED) | PARTIALLY_PINNED |
| NO_TRADE | price position | deterministic gate (INFERRED) | PARTIALLY_PINNED |
| FAILURE_OR_COUNTEREXAMPLE | price/volume context | systematic loss ledger (not in source) | PARTIALLY_PINNED |
| TIMEFRAME_SCOPE | all timeframes derivable | — | PARTIALLY_PINNED |
| INSTRUMENT_SCOPE | not the source universe | exact bracket-trade transfer (INFERRED) | EXPLICITLY_PINNED |
| CHINESE_FUTURES_TRANSFER_STATUS | current products | transfer is INFERRED | INFERRED_PROJECT_TRANSFER |

No OHLCV proxy is authorized for the `REQUIRES_UNAVAILABLE_INPUT` row.

---

## 9. Missing inputs

- NYSE TICK / breadth (advancing minus declining) — used by the source for
  trend-day confirmation handicap and momentum read; `NOT_OBSERVABLE_WITH_CURRENT_DATA`; not proxied.
- A source-pinned post-entry stop/invalidation boundary — absent from the
  source; `NOT_PINNED`.
- A unique 45m-vs-60m PRIMARY — the source permits both; preserved as two
  explicit variants.
- A pinned entry tick-offset / OCO / same-bar handling convention — absent from
  the source; `NOT_PINNED`, representable only as clearly labeled project
  conventions.
- DAX/EuroStoxx cross-market (context handicap, outside family core) — not
  owned; not proxied.

Optional paid candidates (awareness only, per
`HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`): `Trading Sardines` (2015
book), `Street Smarts` (book), NYSE TICK/breadth feeds. None are purchased and
none are required for this decision; they cannot be required merely to make
this playbook work.

---

## 10. Contradictions / tensions between source statements

There are no direct logical contradictions, but there are **unresolved
tensions** that matter for operationalization:

1. **NR7 window alignment tension.** "narrowest range of the past seven bars"
   (text) vs "in today's trading range is the narrowest trading range in the
   last seven days" (figure caption) differ on whether the current day counts
   within the seven. This is recorded as PARTIALLY_PINNED, not resolved by
   guessing.
2. **Early-range variant tension.** The source explicitly permits both 45-min
   and 1-hour windows; no PRIMARY exists. Both are preserved.
3. **Confirmation component tension.** The source calls breadth "the last and
   most important thing" for trend-day confirmation, yet the NR7 bracket entry
   itself requires no breadth/TICK. This is why breadth is recorded as an
   unavailable confirmation handicap, not an entry gate.
4. **Entry-vs-risk tension.** The bracket statement fully defines entry but not
   the post-entry risk loop. This is the core reason the family is NOT
   semantically draftable as a full trading loop.

None of these tensions is resolved by outcome data; they are recorded as source
semantics that remain open.

---

## 11. Source-negative / failure / invalidation context

The bundle preserves failure/no-trade/invalidation context (source-level, no
outcomes):

- NR7 does not guarantee a trend day (the bracket "catches" a trend day only if
  there is going to be one).
- "If I try to guess a breakout, I'm wrong 90 percent of the time" — no-trade
  against guessing; use defined levels.
- "The worst thing you can do... is to buy in the middle of a trading range" —
  no-trade / entry-location rule.
- "If there's no improvement in volume or breadth, the market is more likely to
  stay within a trading range" — range-day context (scalp mode, not big-target
  trend-day).
- Flags fail at volatility extremes (V-spike) and in contracting volatility;
  "statistical reliability only comes with a volatility filter."
- Eaton Corp example (1997): "no reason to be in this trade" — source-
  acknowledged no-trade/failure case.
- Management counterexample language: "the minute the market gives back more
  than it should, you get out on the first reaction or pause."

The bundle contains positive examples, no-trade rules, and explicit failure
context. It does not contain a systematic loss ledger or quantified failure
rates (source-quality limitation, recorded rather than manufactured).

---

## 12. Final decision

```text
PLAYBOOK_SEMANTICALLY_DRAFTABLE=NO
PRIMARY_BLOCKER=SOURCE_POST_ENTRY_RISK_SEMANTICS_NOT_PINNED
  (INITIAL_STOP=NOT_PINNED; POST_ENTRY_INVALIDATION=NOT_PINNED)
```

Rationale:

- The source pins the complete **entry** mechanism: NR7 daily-bar definition,
  day-after-NR7 bracket stops around the early-morning range, with 45-min and
  60-min as explicit source-permitted variants, buy stop above range high /
  sell stop below range low, stop-order type. It also pins the price-based
  **trend-day definition** and supplies qualitative exit/no-trade/failure
  context.
- The source does **not** pin the **post-entry risk loop**: `INITIAL_STOP=
  NOT_PINNED` and `POST_ENTRY_INVALIDATION=NOT_PINNED` (integration correction
  IC-1; the opposite bracket side is entry placement, not an established stop).
- A full trading-loop Playbook Contract would still require **invented critical
  invalidation/stop semantics**. That is exactly the NO condition in the task:
  "a full trading-loop Playbook would still require invented critical entry,
  invalidation, exit, session or other semantics."
- The remaining entry/session order-mechanics gaps (tick offset, OCO
  cancellation, same-bar handling) are representable as clearly labeled project
  conventions, but the missing risk loop is **not** a source-permitted variant
  and **not** a transfer; it is simply absent from the source.

Supporting blocker classes, all present:

```text
INITIAL_STOP_NOT_PINNED
POST_ENTRY_INVALIDATION_NOT_PINNED
```

This is a **successful negative source-semantic result** (same discipline as
the accepted Steenbarger negative completion). It does not mean the family is
unusable; it means a full source-faithful trading-loop Playbook cannot be
drafted without inventing the post-entry risk control.

`NO_CANDIDATE_OUTCOME_DATA_USED=YES`

---

## 13. SOURCE_ONLY session evidence

A new project-issued verified SOURCE_ONLY session was created using the actual
project implementation (`SourceOnlyPolicy.open_verified_session`,
`ApprovedSourceBundle`, `ClaimRecordOutput`, `ClaimRecordDraft`,
`SourceOnlyClaimExtractionContext` in `src/research_firewall.py`):

```text
SESSION_ID=SOURCE_ONLY_RASCHKE_NR7_SEMANTIC_V1_20260819
MODEL_IDENTITY=deepseek-v4-flash
PROMPT_SPEC=RASCHKE_NR7_TARGETED_SEMANTIC_COMPLETION_V1
SOURCE_BUNDLE_IDENTITY=SB-RASCHKE-NR7-SEMANTIC-V1
SOURCE_BUNDLE_HASH=6304a630430871cdfd197ea38a2a22556d7854bff05fd5a7fad20a934bd06f11
RETRIEVAL_MODE=LOCAL_FREE_PUBLIC_RASCHKE_NR7_SEMANTIC_ONLY
PROTECTED_MARKET_ACCESS_MODE=TECHNICALLY_DENIED
SOURCE_ONLY_IS_VERIFIED=YES
DENIAL_TEST_OUTCOME=DENIED
DENIAL_TEST_REASON=SOURCE_ONLY_TECHNICAL_DENIAL
RECORDED_RESOLUTIONS=23
```

Exposure note (disclosed, not certified away):

- Model latent historical knowledge cannot be proven absent (residual
  threat-model risk under Protocol v1.0 §3).
- Project protected-period outcomes (DEVELOPMENT 2024, VALIDATION 2025H1,
  FINAL_HOLDOUT 2025H2) are technically unavailable to this SOURCE_ONLY runner;
  the runner exposes no project protected-period market-outcome retrieval
  surface, and any such request is technically DENIED and audited.
- No canonical market data repository, validation surface, or historical-final
  surface was exposed to this session.
- All source materials predate 2024-01-01; no source-example date audit is
  required for the protected windows (Protocol v1.0 §4).
- The 45m vs 60m early-range decision was NOT made from outcomes; both
  variants are preserved explicitly.

---

## 14. Self-review

- Did I pick 45m or 60m because one seems better? **No** — recorded
  `SOURCE_PERMITTED_MULTIPLE_VARIANTS`; both identities preserved explicitly.
- Did I treat the opposite bracket side as the source stop? **No** —
  `POST_ENTRY_INVALIDATION=NOT_PINNED`, `INITIAL_STOP=NOT_PINNED` (IC-1).
- Did I invent an initial stop or invalidation boundary? **No** — both remain
  NOT_PINNED; inventing them is exactly why the answer is NO.
- Did I invent a tick offset / OCO / same-bar convention and call it source
  fact? **No** — recorded NOT_PINNED; any project convention is clearly labeled
  INFERRED at operationalization (which does not rescue the missing risk loop).
- Did I invent an OHLCV proxy for breadth/TICK? **No** — `BREADTH_TICK_ROLE=
  REQUIRES_UNAVAILABLE_INPUT`; not proxied.
- Did I invent an NR7 window alignment? **No** — `NR7_LOOKBACK_SEMANTICS=
  PARTIALLY_PINNED`; ambiguity recorded.
- Did I assume Chinese-futures transfer? **No** — `CHINESE_FUTURES_TRANSFER_STATUS=
  INFERRED_PROJECT_TRANSFER`; `SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN`.
- Did I use outcomes to resolve any semantic? **No** — `NO_CANDIDATE_OUTCOME_DATA_USED=YES`;
  denial path exercised once; no canonical outcome surface touched.
- Did I use paid/authenticated material? **No** — free/public/unauthenticated
  only; paid items are awareness-only candidates; no new source added.
- Did I force a YES? **No** — the honest decision is `PLAYBOOK_SEMANTICALLY_DRAFTABLE=NO`.
- Did I rely on local memory instead of repo/source authority? **No** — all
  authority from repo files at the exact baseline; all semantics from the
  accepted official source bundle text (re-verified against the worker's
  official-article extraction in a temp dir outside the repo; raw content not
  committed).

---

## 15. Final output

```text
STATUS=COMPLETE
FAMILY=RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT
PLAYBOOK_SEMANTICALLY_DRAFTABLE=NO
SEMANTICS_EXPLICITLY_PINNED=6
SEMANTICS_SOURCE_PERMITTED_MULTIPLE_VARIANTS=1
SEMANTICS_PARTIALLY_PINNED=9
SEMANTICS_NOT_PINNED=5
SEMANTICS_REQUIRES_UNAVAILABLE_INPUT=1
SEMANTICS_INFERRED_PROJECT_TRANSFER=1
POST_ENTRY_INVALIDATION=NOT_PINNED
INITIAL_STOP=NOT_PINNED
EARLY_RANGE_VARIANTS=EARLY_RANGE_VARIANT_45MIN, EARLY_RANGE_VARIANT_60MIN (SOURCE_PERMITTED_MULTIPLE_VARIANTS; no unique PRIMARY)
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
SOURCE_ONLY_VERIFIED=YES
PROTECTED_OUTCOME_DENIAL=PASS
NO_CANDIDATE_OUTCOME_DATA_USED=YES
PRIMARY_BLOCKER=SOURCE_POST_ENTRY_RISK_SEMANTICS_NOT_PINNED (INITIAL_STOP=NOT_PINNED; POST_ENTRY_INVALIDATION=NOT_PINNED)
```
