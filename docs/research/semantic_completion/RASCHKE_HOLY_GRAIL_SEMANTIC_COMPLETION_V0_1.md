# RASCHKE_HOLY_GRAIL_SEMANTIC_COMPLETION_V0_1

> Version: 0.1
> Date: 2026-08-20
> Status: SOURCE_SEMANTIC_COMPLETION / SOURCE_ONLY / NON_FROZEN / PRE_OUTCOME
> Role: RASCHKE_HOLY_GRAIL_TARGETED_SEMANTIC_COMPLETION_ENGINEER
> Prompt/spec: `RASCHKE_HOLY_GRAIL_TARGETED_SEMANTIC_COMPLETION_V1`
> Retrieval mode: `LOCAL_FREE_PUBLIC_RASCHKE_HOLY_GRAIL_SEMANTIC_ONLY`
> Source bundle: `SB-RASCHKE-HOLY-GRAIL-SEMANTIC-V1`
> Source bundle hash: `7e6cd5cf02eefa7ba7483eeda9a036433e5a07320455c0594971fc2e37bf882c`
> SOURCE_ONLY session: `SOURCE_ONLY_RASCHKE_HOLY_GRAIL_SEMANTIC_V1_20260820`
> Session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json`
> Bundle manifest: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json`
> Base bundle: `SB-RASCHKE-PUBLIC-SCREEN-V1` / `7b11a8f1516696e2e54f9dc0ee4d7785f8f1cd9dad06d52abe15378edd2633bd`
> Schema/authority: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`, `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`

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
FAMILY=RASCHKE_HOLY_GRAIL_PULLBACK
PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES
SEMANTICS_EXPLICITLY_PINNED=12
SEMANTICS_SOURCE_PERMITTED_MULTIPLE_VARIANTS=0
SEMANTICS_PARTIALLY_PINNED=10
SEMANTICS_NOT_PINNED=4
SEMANTICS_REQUIRES_UNAVAILABLE_INPUT=0
SEMANTICS_INFERRED_PROJECT_TRANSFER=1
INITIAL_STOP=EXPLICITLY_PINNED
POST_ENTRY_INVALIDATION=EXPLICITLY_PINNED
EXIT_TRIGGER=PARTIALLY_PINNED
SOURCE_SUPPORTS_COMMODITY_FUTURES=UNKNOWN
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
OPTIONAL_PAID_CANDIDATES=3
SOURCE_ONLY_VERIFIED=YES
PROTECTED_OUTCOME_DENIAL=PASS
NO_CANDIDATE_OUTCOME_DATA_USED=YES
PLAYBOOK_HANDOFF_CREATED=YES
PRIMARY_BLOCKER=NONE
```

This package is a **successful source-research result**: it resolves all 27
targeted semantic fields for `RASCHKE_HOLY_GRAIL_PULLBACK` from the accepted
official free/public Raschke source bundle and returns
`PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES`.

The source pins the complete trading loop:

- **CONTEXT** — 14-period ADX > 30 and rising (explicit); extended-range
  breakout + new momentum highs (qualitative, SR-V0-M05).
- **SETUP** — retracement/pullback of price to the 20-period exponential
  moving average (explicit target; EMA price input NOT_PINNED).
- **ENTRY** — buy stop above the high of the previous bar when price touches
  the 20-period EMA (explicit); sells reversed for the short.
- **INITIAL_RISK / INVALIDATION** — protective sell stop at the newly formed
  swing low (explicit). This is the key contrast with the accepted NR7 negative
  result (`INITIAL_STOP=NOT_PINNED`, `POST_ENTRY_INVALIDATION=NOT_PINNED`):
  the Holy Grail family has a source-stated post-entry risk boundary.
- **EXIT** — trail stops as profits grow (explicit); take at least half off at
  a price objective (qualitative, SR-V0-M04); exit on first reaction/pause when
  giving back more than it should (qualitative, SR-V0-M04).
- **NO_TRADE / APPLICABILITY** — do not buy in the middle of a trading range;
  avoid ADX < 20 declining; do not fade ADX > 32 rising; do not guess breakouts.
- **TIMEFRAME / INSTRUMENT SCOPE** — multi-timeframe explicit (base chart then
  30/60/120-minute); US equities / US index examples; commodity-futures and
  Chinese-futures support UNKNOWN (transfer is INFERRED).

The remaining gaps are representable as **clearly labeled INFERRED project
conventions**, not invented critical rules:

- `MOVING_AVERAGE_PRICE_INPUT=NOT_PINNED` (the source never states the EMA price
  basis; any project choice, e.g. standard close-based EMA, is INFERRED);
- `TIME_EXIT_IF_ANY=NOT_PINNED` and `REENTRY_RULE_IF_ANY=NOT_PINNED` (the source
  has no such rules; they remain unrepresented rather than guessed);
- swing-low identification, trailing mechanics, and the qualitative exit
  triggers are `PARTIALLY_PINNED` (concept present; exact mechanics require a
  labeled INFERRED convention).

Because a full trading-loop Playbook Contract can be drafted from
source-faithful semantics **without inventing critical rules**, the honest
decision is `YES`. A HANDOFF document is created
(`docs/research/semantic_completion/RASCHKE_HOLY_GRAIL_PLAYBOOK_HANDOFF_V0_1.md`)
for the later operationalization lane. No Playbook Contract code is
instantiated by this package (Lane B2 is integrated separately).

---

## 1. Authority read

Per the task, the following authorities were read from latest `origin/main`
(`2b197f9b1a72471cbd338e6392d920bf48b58cd1`):

- `AGENTS.md`
- `OWNER_COLLABORATION_CONTRACT.md`
- `CURRENT_STATE.md`
- `docs/research/PARALLEL_WORK_PACKAGE_2026-08-20_V0_2.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`
- `src/research_firewall.py`
- `tests/test_research_firewall.py` (SOURCE_ONLY tests)

Accepted Raschke screen worker evidence was read at its exact commit
`bd09f9acc4647f9a2240a2f20bf9c919c4d8bb23` on
`parallel/raschke-public-current-data-screen-v01`:

- `docs/research/claim_extraction/HUMAN_PLAYBOOK_RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V0_1.md`
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json`
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_SCREEN_V0_1.json`

The screen identified Holy Grail material in the official free/public Raschke
articles (SR-V0-M01 1997 4-step rules; SR-V0-M05 2004 cross-timeframe setup;
SR-V0-M02 1993 pullback-to-EMA framework). This package reconstructs the family
from those exact accepted artifacts, not from a summary.

All expected authority files were present at the exact baseline. No authority
was reported missing or substituted.

---

## 2. Scope and core question

The task is a **targeted source-semantic completion**, not a backtest, not a
parameter search, not outcome inspection, and not a Playbook implementation.
The family under test is:

```text
RASCHKE_HOLY_GRAIL_PULLBACK
```

Core question (single final decision):

```text
Does the accepted official free/public Raschke source bundle supply enough
source-faithful semantics for the Holy Grail / pullback family (strong-trend /
ADX context + pullback to a 20-period EMA) that a later full trading-loop
Playbook Contract can be drafted WITHOUT inventing critical trading-loop
semantics?
```

- `YES` requires the remaining unresolved items to be representable explicitly
  as source-permitted variants / clearly labeled project transfer **without**
  inventing critical trading-loop semantics.
- `NO` means a full trading-loop Playbook would still require invented critical
  entry, invalidation, exit, or other semantics.
- The task explicitly instructs **not to force a YES**.

---

## 3. Source bundle

Bundle: `SB-RASCHKE-HOLY-GRAIL-SEMANTIC-V1` — **reuses the exact accepted
Raschke screen bundle materials** that anchor the Holy Grail / pullback family
(all `TRACEABLE_ORIGINAL`, `FREE_PUBLIC_UNAUTHENTICATED`, effective content date
before 2024-01-01).

| material_id | title | date | role in this package |
|---|---|---|---|
| `SR-V0-M01` | Short Term Trading Strategies (AIQ) | 1997-08 | PRIMARY: Holy Grail 4-step buy rules (sells reversed); no-trade middle of range; impulse/thrust cue; stop process; Eaton Corp failure example; lineage reference to Street Smarts (Raschke & Connors) |
| `SR-V0-M05` | Traders Toolbox (Active Trader) | 2004-03 | PRIMARY: Holy Grail setup across time frames (20-bar EMA pullback; 30/60/120-minute retracements; 14-bar ADX>30 on each timeframe); indicator checklist (14-period ADX, 20-period EMA; breadth/TICK/put-call boundaries) |
| `SR-V0-M02` | The Discerning Trader (S&C) | 1993-09 | Raschke's own pullback framework: 'If there is a trend... buying a pullback to a moving average... 20-period exponential moving average on all my markets'; ADX no-trade/fade rules (ADX<20 declining; ADX>32 rising) |
| `SR-V0-M04` | The Rituals of Trading (Active Trader) | 2000-08 | management/exit principles: give-back exit on first reaction/pause; take at least half off at a price objective; price-based emphasis |
| `SR-V0-M03` | Trading Style and Daily Market Regimen (Active Trader) | 2004-02 | no-trade / failure context: breakout-guess failure (~90%); down-trending gap-up short rule (context only) |

### 3.1 No additional source was added

The task permits adding another official free/public pre-2024 Raschke source
**only if** it directly resolves one of the open semantic questions. On
2026-08-20 the official Articles index (`https://lindaraschke.net/articles/`)
was re-verified with HTTP 200 and enumerates **exactly the same** free/public
PDFs already in the accepted screen bundle (Trade Trends, Trading Insights,
Traders Toolbox, Multi-Market Traders Rule, The Rituals of Trading, Short Term
Trading Strategies, Maintain your Mindset, Who are You?, Everything About
Electronic Trading, The Discerning Trader, Trading Style and Daily Market
Regimen). No additional official free/public pre-2024 article directly resolves
the open semantics (notably the EMA price input, which is NOT_PINNED).

Official videos/interviews are YouTube-hosted (blocked by 403 in the recorded
environment; no circumvention under
`HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`). Paid books (`Trading
Sardines`, `Street Smarts`) and NYSE TICK/breadth data are listed as
awareness-only candidates, not purchased.

```text
NO_ADDITIONAL_SOURCE_ADDED=YES
CHECKED_ON=2026-08-20
OFFICIAL_ARTICLES_INDEX=https://lindaraschke.net/articles/ (HTTP 200 re-verified)
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
| 1 | TREND_CONTEXT_DEFINITION | PARTIALLY_PINNED | M05 HOLY_GRAIL_SETUP; M01 HOLY_GRAIL_RULES |
| 2 | ADX_PERIOD | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES; M05 HOLY_GRAIL_SETUP |
| 3 | ADX_THRESHOLD | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES; M05 HOLY_GRAIL_SETUP |
| 4 | ADX_RISING_OR_LEVEL_REQUIREMENT | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES |
| 5 | MOVING_AVERAGE_TYPE | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES; M02 PULLBACK_TO_MA; M05 HOLY_GRAIL_SETUP |
| 6 | MOVING_AVERAGE_PERIOD | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES; M02 PULLBACK_TO_MA; M05 HOLY_GRAIL_SETUP |
| 7 | MOVING_AVERAGE_PRICE_INPUT | NOT_PINNED | M01 HOLY_GRAIL_RULES; M02 PULLBACK_TO_MA; M05 HOLY_GRAIL_SETUP |
| 8 | PULLBACK_DEFINITION | PARTIALLY_PINNED | M01 HOLY_GRAIL_RULES; M02 PULLBACK_TO_MA |
| 9 | PULLBACK_TOUCH_OR_PENETRATION_RULE | PARTIALLY_PINNED | M01 HOLY_GRAIL_RULES |
| 10 | ENTRY_TRIGGER | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES |
| 11 | ENTRY_ORDER_TYPE | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES |
| 12 | ENTRY_OFFSET | PARTIALLY_PINNED | M01 HOLY_GRAIL_RULES |
| 13 | LONG_RULE | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES |
| 14 | SHORT_RULE | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES |
| 15 | INITIAL_STOP | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES |
| 16 | POST_ENTRY_INVALIDATION | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES; M04 MANAGEMENT_EXIT |
| 17 | STOP_ADJUSTMENT_IF_ANY | PARTIALLY_PINNED | M01 HOLY_GRAIL_RULES |
| 18 | PROFIT_TARGET | PARTIALLY_PINNED | M04 MANAGEMENT_EXIT; M05 HOLY_GRAIL_SETUP |
| 19 | EXIT_TRIGGER | PARTIALLY_PINNED | M01 HOLY_GRAIL_RULES; M04 MANAGEMENT_EXIT |
| 20 | TIME_EXIT_IF_ANY | NOT_PINNED | M01 HOLY_GRAIL_RULES |
| 21 | REENTRY_RULE_IF_ANY | NOT_PINNED | M05 HOLY_GRAIL_SETUP |
| 22 | NO_TRADE | PARTIALLY_PINNED | M01 MARKET_TIMING; M02 ADX_RULES; M03 BREAKOUT_GUESS_FAILURE |
| 23 | FAILURE_OR_COUNTEREXAMPLE | PARTIALLY_PINNED | M01 HOLY_GRAIL_RULES (Eaton Corp); M03 BREAKOUT_GUESS_FAILURE |
| 24 | TIMEFRAME_SCOPE | PARTIALLY_PINNED | M05 HOLY_GRAIL_SETUP |
| 25 | INSTRUMENT_SCOPE | EXPLICITLY_PINNED | M01 HOLY_GRAIL_RULES; M02 PULLBACK_TO_MA |
| 26 | COMMODITY_FUTURES_SCOPE | NOT_PINNED (UNKNOWN) | M01 HOLY_GRAIL_RULES |
| 27 | CURRENT_PROJECT_PRODUCT_TRANSFER | INFERRED_PROJECT_TRANSFER | M01 HOLY_GRAIL_RULES |

Counts:

```text
SEMANTICS_EXPLICITLY_PINNED=12
SEMANTICS_SOURCE_PERMITTED_MULTIPLE_VARIANTS=0
SEMANTICS_PARTIALLY_PINNED=10
SEMANTICS_NOT_PINNED=4
SEMANTICS_REQUIRES_UNAVAILABLE_INPUT=0
SEMANTICS_INFERRED_PROJECT_TRANSFER=1
TOTAL=27
```

### 4.1 EXPLICITLY_PINNED (12)

1. **ADX_PERIOD** — 14 in two accepted materials (M01 "14-period ADX"; M05
   "14-bar ADX reading above 30").
2. **ADX_THRESHOLD** — > 30 (M01 "greater than 30"; M05 "above 30"). The M02
   20/32 values are separate no-trade/fade rules recorded under NO_TRADE, not
   the Holy Grail entry filter.
3. **ADX_RISING_OR_LEVEL_REQUIREMENT** — "must initially be greater than 30 AND
   rising" (M01 step 1). The level+rising conjunction is explicit; the "rising"
   slope measurement window is a representable INFERRED convention, and M01
   step 2's "usually accompanied by a turndown in ADX" is a qualitative
   descriptive nuance of the pullback phase.
4. **MOVING_AVERAGE_TYPE** — exponential ("20-period exponential moving
   average" in M01/M02; "20-bar EMA" in M05), consistent across all three.
5. **MOVING_AVERAGE_PERIOD** — 20, consistent across all three.
6. **ENTRY_TRIGGER** — price touches the 20-period EMA → place a buy stop above
   the high of the previous bar; entry occurs on its fill (M01 step 3).
7. **ENTRY_ORDER_TYPE** — stop order (buy stop for the long; sell stop for the
   short). The stop-market vs stop-limit subtype is an operational detail.
8. **LONG_RULE** — the complete explicit 4-step buy rules (M01 steps 1-4).
9. **SHORT_RULE** — "sells reversed" (M01 header): the short side is the mirror
   of the 4-step buy rules; the mirror construction is the source's own
   reversal statement.
10. **INITIAL_STOP** — "Once filled, enter a protective sell stop at the newly
    formed swing low" (M01 step 4). The initial stop is source-pinned. The
    mechanical identification of a "swing low" is not defined (INFERRED pivot
    convention). This is the key contrast with the NR7 negative result.
11. **POST_ENTRY_INVALIDATION** — the protective stop at the newly formed swing
    low is the explicit post-entry invalidation boundary (M01 step 4); the M04
    "gives back more than it should → first reaction/pause" rule is qualitative
    management context, not a conflicting rule.
12. **INSTRUMENT_SCOPE** — `SOURCE_INSTRUMENT_SCOPE=US_EQUITIES_AND_US_INDEX`
    (1997 examples: Eaton Corp; CHV/CMZ/AXP/ETN; M05 S&P context). The M02 "on
    all my markets" statement is broad lineage context, NOT counted as explicit
    commodity-futures support.

### 4.2 SOURCE_PERMITTED_MULTIPLE_VARIANTS (0)

No field is source-permitted as multiple discrete variants. The 14-period
ADX>30 and the 20-period EMA are stated consistently across the accepted
materials; the 1993 ADX 20/32 values are no-trade/fade rules for a different
purpose, not a competing entry-filter variant.

### 4.3 PARTIALLY_PINNED (10)

1. **TREND_CONTEXT_DEFINITION** — the ADX>30-and-rising filter is explicit; the
   "extended trading range breakout / new momentum highs" market structure
   (M05) is qualitative and not numerically pinned.
2. **PULLBACK_DEFINITION** — the pullback target (20-period EMA) is explicit;
   the pullback leg count/depth/duration that qualifies as "a
   retracement/pullback" is not defined.
3. **PULLBACK_TOUCH_OR_PENETRATION_RULE** — "when price touches the 20-period
   MA" is explicit; the bar-level definition of "touches" (intrabar low/high vs
   close vs penetration) is not pinned.
4. **ENTRY_OFFSET** — "above the high of the previous bar" pins the reference
   level; the exact tick offset above that high is not stated (the gap-reversal
   "one tick above" language does not transfer).
5. **STOP_ADJUSTMENT_IF_ANY** — "Trail stops as profits grow" is explicit; the
   trailing mechanics (swing/MA/distance-based) are not pinned.
6. **PROFIT_TARGET** — "take at least half off at a price objective when
   continuation is uncertain" (M04) is explicit but qualitative; M05 "looking
   for a top" is multi-timeframe context; no numeric target pinned.
7. **EXIT_TRIGGER** — trail as profits grow (M01); exit on first reaction/pause
   when giving back more than it should (M04); "get out if the market fails to
   do what I thought it would do" (M01 stop process). Present and
   source-attributed, but qualitative; the exit is NOT missing.
8. **NO_TRADE** — explicit constraints (middle-of-range; ADX<20 declining avoid;
   do not fade ADX>32 rising; no guess-breakouts) but the operational boundaries
   (range definition, ADX slope, "middle") are not numerically pinned.
9. **FAILURE_OR_COUNTEREXAMPLE** — Eaton Corp "no reason to be in this trade" is
   a source-acknowledged no-trade/failure case for the pullback pattern;
   guess-breakout failure (~90%). Limited detail; no systematic loss ledger
   (source-quality limitation).
10. **TIMEFRAME_SCOPE** — multi-timeframe explicit (base chart then 30/60/120-
    minute, each preceded by 14-bar ADX>30 on that timeframe); no single
    operating timeframe uniquely pinned for the whole loop.

### 4.4 NOT_PINNED (4)

1. **MOVING_AVERAGE_PRICE_INPUT** — the source never states the price basis of
   the 20-period EMA (close vs typical vs high/low). Any project choice (e.g.,
   standard close-based EMA) is a clearly labeled INFERRED project convention.
2. **TIME_EXIT_IF_ANY** — no source time-based exit exists for this family; any
   such rule would be an invented critical rule and is therefore not
   represented.
3. **REENTRY_RULE_IF_ANY** — no source re-entry rule; the M05 multi-timeframe
   sequence is a context observation, not a re-entry rule.
4. **COMMODITY_FUTURES_SCOPE** — `SOURCE_SUPPORTS_COMMODITY_FUTURES=UNKNOWN`: no
   explicit commodity-futures example or statement applies the Holy Grail
   pullback rules to commodity futures (unlike the NR7 family's cocoa anchor);
   the M02 "on all my markets" statement is ambiguous and not counted as
   explicit support.

### 4.5 REQUIRES_UNAVAILABLE_INPUT (0)

No required semantic field depends on an information surface the project does
not own. The M05 30/60/120-minute charts are derivable from owned 1-minute
OHLCV. NYSE TICK/breadth is referenced by the source as a general pullback-
buying context (M04: "If the TICKs are making new highs, I'll look to buy the
pullbacks") and as a confirmation boundary, but it is NOT part of the
source-pinned 4-step Holy Grail rules; it is recorded as unavailable context,
not proxied, and not a required input for this family.

### 4.6 INFERRED_PROJECT_TRANSFER (1)

**CURRENT_PROJECT_PRODUCT_TRANSFER** —
`SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN`. Transferring the Holy Grail
pullback rules to `cu/al/ni/au/ag/rb` is an INFERRED project hypothesis, not an
explicit source claim. "Works across timeframes" is NOT interpreted as
"explicitly applies to Chinese cu/al/ni/au/ag/rb".

---

## 5. Lineage analysis (source evidence only)

Per the task, lineage is recorded explicitly and overlap is not counted as
independent confirmation.

- **Raschke's own stated practice** — the 1993 S&C statement "If there is a
  trend, I'll try to always look for buying a pullback to a moving average...
  I personally use a 20-period exponential moving average on all my markets"
  (SR-V0-M02) is Raschke's own stated personal practice. The 2004 Active Trader
  "Holy Grail across time frames" setup (SR-V0-M05) is presented in Raschke's
  own words in the Etzkorn interview.
- **Shared lineage (Raschke & Connors)** — the 1997 AIQ interview (SR-V0-M01)
  presents the "Holy Grail" 4-step rules and references the Raschke & Connors
  book *Street Smarts*, from which the pattern is drawn with more detail than
  the free article. The "Holy Grail" name/rule lineage is therefore shared with
  Larry Connors.
- **Not independent confirmation** — the Raschke free articles and the
  Raschke & Connors book are the same lineage (co-authored). The book is not an
  independent confirmation of the articles, and the articles are not
  independent confirmation of the book. The lineage overlap is disclosed, not
  counted as independent source support.
- **Consequence for this package** — all Holy Grail semantics in this package
  are anchored to the accepted official free/public Raschke articles
  (SR-V0-M01, SR-V0-M02, SR-V0-M04, SR-V0-M05). The shared Connors lineage is
  recorded as lineage context, and *Street Smarts* remains an awareness-only
  optional paid candidate (not purchased).

---

## 6. Stop / invalidation rule (the key positive result vs NR7)

The accepted NR7 negative result was driven by
`INITIAL_STOP=NOT_PINNED` / `POST_ENTRY_INVALIDATION=NOT_PINNED`. The Holy
Grail family is different:

```text
INITIAL_STOP=EXPLICITLY_PINNED
POST_ENTRY_INVALIDATION=EXPLICITLY_PINNED
```

- The 1997 4-step rules (SR-V0-M01 step 4) explicitly state: "Once filled,
  enter a protective sell stop at the newly formed swing low."
- This is a source-stated post-entry risk boundary: if price trades back below
  the newly formed swing low, the pullback-in-trend thesis is invalidated.
- The M04 management language ("the minute the market gives back more than it
  should, you get out on the first reaction or pause") is qualitative
  management context, not a conflicting rule; it does not replace the hard
  swing-low stop.
- The mechanical identification of a "swing low" is not defined by the source
  (an INFERRED pivot convention at operationalization) — this is a
  representable convention, not an absent critical rule.

---

## 7. Instrument-transfer analysis

```text
SOURCE_INSTRUMENT_SCOPE=US_EQUITIES_AND_US_INDEX
SOURCE_SUPPORTS_COMMODITY_FUTURES=UNKNOWN
SOURCE_SUPPORTS_CROSS_MARKET_TRANSFER=UNKNOWN
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
CURRENT_PROJECT_PRODUCT_TRANSFER=INFERRED_PROJECT_TRANSFER
```

- The Holy Grail examples are US equities (Eaton Corp; CHV/CMZ/AXP/ETN) and an
  S&P index context (M05). There is **no** commodity-futures chart anchor for
  the Holy Grail rules (unlike the NR7 family's September Cocoa example).
- The M02 statement "I personally use a 20-period exponential moving average on
  all my markets" is a broad usage statement. It is recorded as lineage context
  and is **not** counted as explicit commodity-futures support for the Holy
  Grail pullback.
- Any Chinese-futures operationalization is a separately labeled `INFERRED`
  project hypothesis and does not inherit source authority automatically.
  `UNKNOWN` means source support is absent, not that project evidence proves
  the setup cannot work.

---

## 8. Observability matrix

Raw observability does **not** settle source semantics. The table separates
(a) source surface, (b) current project-observable portion, (c) missing
portion, and the resulting semantic classification.

| semantic field | observable on current corpus (1-min OHLCV + governed metadata) | missing / unowned | classification |
|---|---|---|---|
| TREND_CONTEXT_DEFINITION | ADX (OHLC-derived), price bars | range/momentum-highs boundary (INFERRED) | PARTIALLY_PINNED |
| ADX_PERIOD | ADX (OHLC-derived) | — | EXPLICITLY_PINNED |
| ADX_THRESHOLD | ADX (OHLC-derived) | — | EXPLICITLY_PINNED |
| ADX_RISING_OR_LEVEL_REQUIREMENT | ADX level/slope (OHLC-derived) | slope window (INFERRED) | EXPLICITLY_PINNED |
| MOVING_AVERAGE_TYPE | EMA (price-derived) | — | EXPLICITLY_PINNED |
| MOVING_AVERAGE_PERIOD | EMA (price-derived) | — | EXPLICITLY_PINNED |
| MOVING_AVERAGE_PRICE_INPUT | all candidate price inputs owned | price basis (INFERRED) | NOT_PINNED |
| PULLBACK_DEFINITION | price/EMA (OHLC-derived) | pullback structure (INFERRED) | PARTIALLY_PINNED |
| PULLBACK_TOUCH_OR_PENETRATION_RULE | price/EMA (OHLC-derived) | touch definition (INFERRED) | PARTIALLY_PINNED |
| ENTRY_TRIGGER | price/EMA, previous-bar high | — | EXPLICITLY_PINNED |
| ENTRY_ORDER_TYPE | order semantics | subtype (INFERRED) | EXPLICITLY_PINNED |
| ENTRY_OFFSET | previous-bar high | tick offset (INFERRED) | PARTIALLY_PINNED |
| LONG_RULE | ADX/EMA/bars/swings | swing-low ID, EMA basis (INFERRED) | EXPLICITLY_PINNED |
| SHORT_RULE | ADX/EMA/bars/swings | mirror construction (INFERRED) | EXPLICITLY_PINNED |
| INITIAL_STOP | swing lows (price) | swing-low ID (INFERRED) | EXPLICITLY_PINNED |
| POST_ENTRY_INVALIDATION | swing lows (price) | swing-low ID (INFERRED) | EXPLICITLY_PINNED |
| STOP_ADJUSTMENT_IF_ANY | price progress | trail mechanics (INFERRED) | PARTIALLY_PINNED |
| PROFIT_TARGET | price objectives | numeric target (INFERRED) | PARTIALLY_PINNED |
| EXIT_TRIGGER | price behavior | numeric trigger (INFERRED) | PARTIALLY_PINNED |
| TIME_EXIT_IF_ANY | — | no source semantics | NOT_PINNED |
| REENTRY_RULE_IF_ANY | — | no source semantics | NOT_PINNED |
| NO_TRADE | price position, ADX | range/slope boundaries (INFERRED) | PARTIALLY_PINNED |
| FAILURE_OR_COUNTEREXAMPLE | price/context | limited detail (source-quality) | PARTIALLY_PINNED |
| TIMEFRAME_SCOPE | all timeframes derivable | unique operating timeframe (INFERRED) | PARTIALLY_PINNED |
| INSTRUMENT_SCOPE | not the source universe | transfer (INFERRED) | EXPLICITLY_PINNED |
| COMMODITY_FUTURES_SCOPE | — | no source statement | NOT_PINNED (UNKNOWN) |
| CURRENT_PROJECT_PRODUCT_TRANSFER | current products | transfer is INFERRED | INFERRED_PROJECT_TRANSFER |

No OHLCV proxy is authorized for the unavailable TICK/breadth context (which is
not a required input for the 4-step rules).

---

## 9. Missing inputs / open representable conventions

- `MOVING_AVERAGE_PRICE_INPUT` (NOT_PINNED) — the EMA price basis is a critical
  setup input left open by the source. The standard convention (close-based
  EMA) would be an INFERRED project convention, never a source claim.
- Swing-low identification for the initial stop — INFERRED pivot definition.
- Trailing mechanics ("trail stops as profits grow") — INFERRED trail rule.
- Numeric profit target / exit trigger — INFERRED conventions; the qualitative
  source exits (trail, take-half at objective, first-reaction exit) are
  preserved as source semantics.
- NYSE TICK/breadth and DAX/EuroStoxx cross-market (source context, outside the
  4-step rules) — NOT owned, not proxied, not required.

Optional paid candidates (awareness only, per
`HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`): `Trading Sardines` (2015
book), `Street Smarts` (Raschke & Connors book — shared lineage, not
independent), NYSE TICK/breadth feeds. None are purchased and none are required
for this decision.

---

## 10. Contradictions / tensions between source statements

There are no direct logical contradictions, but there are **unresolved
tensions** that matter for operationalization:

1. **EMA price input tension.** The source repeatedly states "20-period
   exponential moving average" / "20-bar EMA" without the price input. This is
   recorded as NOT_PINNED rather than resolved by guessing.
2. **ADX rising vs turndown tension.** M01 step 1 requires ADX "rising"
   (initially), while step 2 observes the retracement is "usually accompanied
   by a turndown in ADX." This is a descriptive nuance of the pullback phase,
   not a conflicting rule; it is recorded in ADX_RISING_OR_LEVEL_REQUIREMENT.
3. **Entry-filter ADX vs no-trade ADX tension.** M01/M05 use ADX>30 as the
   entry filter; M02 uses ADX<20 declining (avoid) and ADX>32 rising (do not
   fade) as no-trade constraints. These serve different roles and are not in
   conflict, but they must not be collapsed into one threshold.
4. **"all my markets" instrument tension.** M02 "20-period EMA on all my
   markets" is broad; the Holy Grail examples are US equities/S&P. This is why
   `SOURCE_SUPPORTS_COMMODITY_FUTURES=UNKNOWN` and the transfer to Chinese
   futures is `INFERRED`.

None of these tensions is resolved by outcome data; they are recorded as source
semantics that remain open.

---

## 11. Source-negative / failure / invalidation context

The bundle preserves failure/no-trade/invalidation context (source-level, no
outcomes):

- Eaton Corp Holy Grail example (1997): "no reason to be in this trade" — a
  source-acknowledged no-trade/failure case for the pullback pattern.
- "If I try to guess a breakout, I'm wrong 90 percent of the time" — no-trade
  against guessing; use defined levels.
- "The worst thing you can do... is to buy in the middle of a trading range" —
  no-trade / entry-location rule (buy new highs or pullbacks).
- "I avoid the markets where the ADX falls below 20 and is declining" and
  "I will not fade a market... where the ADX is above 32 and rising" — ADX-based
  no-trade/fade constraints.
- Management counterexample language: "the minute the market gives back more
  than it should, you get out on the first reaction or pause."

The bundle contains positive examples, no-trade rules, and explicit failure
context. It does not contain a systematic loss ledger or quantified failure
rates (source-quality limitation, recorded rather than manufactured).

---

## 12. Final decision

```text
PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES
PRIMARY_BLOCKER=NONE
```

Rationale:

- The source pins the complete trading loop for the Holy Grail pullback:
  CONTEXT (14-period ADX > 30 and rising; extended-range breakout + new
  momentum highs), SETUP (pullback/retracement to the 20-period EMA), ENTRY
  (buy stop above the high of the previous bar when price touches the 20-period
  EMA; sells reversed for shorts), INITIAL_RISK/INVALIDATION (protective sell
  stop at the newly formed swing low — source-pinned), EXIT (trail stops as
  profits grow; take at least half off at a price objective; exit on first
  reaction/pause when giving back too much), NO_TRADE (middle-of-range; ADX<20
  declining avoid; do not fade ADX>32 rising; no guess-breakouts), TIMEFRAME
  (multi-timeframe explicit: base chart then 30/60/120-minute), INSTRUMENT
  scope (US equities/S&P examples; commodity-futures support UNKNOWN).
- None of the task's NO conditions applies:
  - initial stop IS pinned (`INITIAL_STOP=EXPLICITLY_PINNED`);
  - exit is NOT missing (`EXIT_TRIGGER=PARTIALLY_PINNED`, present and
    source-attributed);
  - trigger is NOT discretionary (`ENTRY_TRIGGER=EXPLICITLY_PINNED`);
  - no source formula conflict with a missing variant identity (14-period
    ADX>30 and 20-period EMA are consistent across all accepted materials);
  - no critical unavailable information surface (the 30/60/120-minute charts are
    derivable from owned 1-minute OHLCV; NYSE TICK/breadth is NOT part of the
    4-step rules).
- The remaining gaps (EMA price basis NOT_PINNED; swing-low identification;
  trailing mechanics; qualitative exits) are representable as **clearly labeled
  INFERRED project conventions** — exactly the same class of representable
  conventions the accepted NR7 completion acknowledged for order-mechanics
  gaps. They are not absent critical rules.

A HANDOFF document is created for the later operationalization lane. No
Playbook Contract code is instantiated here (Lane B2 is integrated separately).

`NO_CANDIDATE_OUTCOME_DATA_USED=YES`

---

## 13. SOURCE_ONLY session evidence

A new project-issued verified SOURCE_ONLY session was created using the actual
project implementation (`SourceOnlyPolicy.open_verified_session`,
`ApprovedSourceBundle`, `ClaimRecordOutput`, `ClaimRecordDraft`,
`SourceOnlyClaimExtractionContext` in `src/research_firewall.py`):

```text
SESSION_ID=SOURCE_ONLY_RASCHKE_HOLY_GRAIL_SEMANTIC_V1_20260820
MODEL_IDENTITY=deepseek-v4-flash
PROMPT_SPEC=RASCHKE_HOLY_GRAIL_TARGETED_SEMANTIC_COMPLETION_V1
SOURCE_BUNDLE_IDENTITY=SB-RASCHKE-HOLY-GRAIL-SEMANTIC-V1
SOURCE_BUNDLE_HASH=7e6cd5cf02eefa7ba7483eeda9a036433e5a07320455c0594971fc2e37bf882c
RETRIEVAL_MODE=LOCAL_FREE_PUBLIC_RASCHKE_HOLY_GRAIL_SEMANTIC_ONLY
PROTECTED_MARKET_ACCESS_MODE=TECHNICALLY_DENIED
SOURCE_ONLY_IS_VERIFIED=YES
DENIAL_TEST_OUTCOME=DENIED
DENIAL_TEST_REASON=SOURCE_ONLY_TECHNICAL_DENIAL
RECORDED_RESOLUTIONS=27
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
- No parameter/indicator variant was selected from outcomes; the exact source
  values (14-period ADX>30, 20-period EMA) were recorded as stated.

---

## 14. Self-review

- Did I invent an ADX formula or threshold? **No** — 14-period ADX and >30 are
  recorded exactly as stated (M01/M05); the M02 20/32 values are recorded as
  separate no-trade rules.
- Did I invent an EMA price input? **No** — `MOVING_AVERAGE_PRICE_INPUT=
  NOT_PINNED`; any project choice is labeled INFERRED, never source fact.
- Did I invent a stop? **No** — the initial stop is source-pinned
  (`INITIAL_STOP=EXPLICITLY_PINNED`: protective sell stop at the newly formed
  swing low, M01 step 4).
- Did I invent an exit? **No** — exit triggers are source-attributed (trail as
  profits grow; take half at a price objective; first-reaction exit); mechanics
  are recorded PARTIALLY_PINNED / INFERRED.
- Did I silently collapse a source variant? **No** — there is no
  SOURCE_PERMITTED_MULTIPLE_VARIANTS in this family; the 14-period ADX>30 and
  20-period EMA are consistent across all accepted materials.
- Did I silently promote a Chinese-futures transfer to EXPLICIT? **No** —
  `CURRENT_PROJECT_PRODUCT_TRANSFER=INFERRED_PROJECT_TRANSFER`;
  `SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN`.
- Did I use a paid source? **No** — official free/public unauthenticated only;
  paid items (Trading Sardines, Street Smarts, NYSE TICK/breadth) are
  awareness-only candidates; none purchased.
- Did I touch candidate outcomes? **No** — `NO_CANDIDATE_OUTCOME_DATA_USED=YES`;
  the protected-outcome denial path was exercised once (DENIED /
  SOURCE_ONLY_TECHNICAL_DENIAL); no canonical outcome surface touched.
- Did I mistake a marketing statement for validation? **No** — no performance/
  testimonial claim is treated as validity evidence; the decision rests on
  source-pinned semantics only.
- Did I force a YES? **No** — the YES is driven by source-pinned context,
  setup, entry, initial-risk/invalidation, exit, no-trade, and scope semantics;
  the NR7 NO was specifically due to missing post-entry risk semantics, which
  are source-pinned here.
- Did I rely on local memory instead of repo/source authority? **No** — all
  authority from repo files at the exact baseline; all semantics from the
  accepted official source bundle/claim records (re-verified at the exact
  screen commit; official Articles index re-verified HTTP 200 on 2026-08-20;
  raw content not committed).

---

## 15. Final output

```text
STATUS=COMPLETE
FAMILY=RASCHKE_HOLY_GRAIL_PULLBACK
PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES
SEMANTICS_EXPLICITLY_PINNED=12
SEMANTICS_SOURCE_PERMITTED_MULTIPLE_VARIANTS=0
SEMANTICS_PARTIALLY_PINNED=10
SEMANTICS_NOT_PINNED=4
SEMANTICS_REQUIRES_UNAVAILABLE_INPUT=0
SEMANTICS_INFERRED_PROJECT_TRANSFER=1
INITIAL_STOP=EXPLICITLY_PINNED
POST_ENTRY_INVALIDATION=EXPLICITLY_PINNED
EXIT_TRIGGER=PARTIALLY_PINNED
SOURCE_SUPPORTS_COMMODITY_FUTURES=UNKNOWN
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
OPTIONAL_PAID_CANDIDATES=3
SOURCE_ONLY_VERIFIED=YES
PROTECTED_OUTCOME_DENIAL=PASS
NO_CANDIDATE_OUTCOME_DATA_USED=YES
PLAYBOOK_HANDOFF_CREATED=YES
PRIMARY_BLOCKER=NONE
```
