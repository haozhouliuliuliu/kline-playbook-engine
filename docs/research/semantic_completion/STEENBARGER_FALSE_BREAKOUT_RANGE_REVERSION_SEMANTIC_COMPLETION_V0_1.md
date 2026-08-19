# STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_SEMANTIC_COMPLETION_V0_1

> Version: 0.1
> Date: 2026-08-19
> Status: SOURCE_SEMANTIC_COMPLETION / SOURCE_ONLY / NON_FROZEN / PRE_OUTCOME
> Role: STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_SEMANTIC_COMPLETION_ENGINEER
> Prompt/spec: `STEENBARGER_FALSE_BREAKOUT_SEMANTIC_COMPLETION_V1`
> Retrieval mode: `LOCAL_FREE_PUBLIC_ORIGINAL_SOURCE_SEMANTIC_COMPLETION_ONLY`
> Source bundle: `SB-SC-STEENBARGER-FALSE-BREAKOUT-V1`
> Source bundle hash: `82240a24e3e8aa04084198f25a5660f55d702f620f612aac13ca0b7813a6a80e`
> SOURCE_ONLY session: `SOURCE_ONLY_SEMANTIC_COMPLETION_STEENBARGER_FALSE_BREAKOUT_V1_20260819`
> Session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_STEENBARGER_FALSE_BREAKOUT_SEMANTIC_V0_1.json`
> Bundle manifest: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_STEENBARGER_FALSE_BREAKOUT_SEMANTIC_V0_1.json`
> Schema/authority: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`, `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`

```text
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
```

---

## 0. Decision summary

```text
SOURCE_FAITHFUL_PRICE_VOLUME_PLAYBOOK_DRAFTABLE=NO
PRICE_VOLUME_ONLY_FORMULATION_EXPLICITLY_SUPPORTED_BY_SOURCE=NO
SOURCE_SUPPORTS_CHINESE_FUTURES_TRANSFER=NO
SOURCE_ONLY_VERIFIED=YES
PROTECTED_OUTCOME_DENIAL=PASS
NO_CANDIDATE_OUTCOME_DATA_USED=YES
PLAYBOOK_CONTRACT_CREATED=NO
```

This package is a **successful negative research result**. The official
free/public pre-2024 Steenbarger (TraderFeed) source material supplies enough
*conceptual* semantics to describe a false-breakout / range-reversion playbook,
but it does **not** supply a source-faithful, current-data-compatible,
price/volume-only operational formulation. The source's own entry permission and
its genuine-vs-false-breakout identification are bound to NYSE TICK, Market
Delta (bid/offer volume), participation/breadth, and sector/cross-market
confirmation inputs that the project does not own; and the price/volume
components that remain (trading-range boundary, candidate high/low, morning
range, entry permission in price/volume form) are not pinned by the source.
Silently deleting the unavailable inputs and calling the remaining price shell a
"Steenbarger playbook" is forbidden and was not done.

No Playbook Contract candidate was created, because doing so would require
invented thresholds and invented entry semantics.

---

## 1. Authority read

Per the task, the following authorities were read from latest `origin/main`
(`eecc5cb3fe50c9c7aa438156e5e300027ebd9597`):

- `AGENTS.md`
- `OWNER_COLLABORATION_CONTRACT.md`
- `CURRENT_STATE.md`
- `RESEARCH_DIRECTION.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_1.md`
- `docs/reviews/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_1_INTEGRATION_REVIEW_V0_1.md`
- `docs/reviews/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_2_INTEGRATION_REVIEW_V0_1.md`
- `docs/research/source_dossiers/SOURCE_DOSSIER_STEENBARGER_V0_1.md`
- `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`
- `src/research_firewall.py`
- `tests/test_research_firewall.py` (SOURCE_ONLY tests)

Wave 2 worker evidence was read at its exact commit
`c0fef50bb3b0f5a97c7bdf472d5a9e2d9339273a` on
`parallel/claim-extraction-wave2-steenbarger-public`:

- `docs/research/claim_extraction/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_2_STEENBARGER_V0_1.md`
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST.json`
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_2_STEENBARGER.json`

All expected authority files were present at the exact baseline. No authority
was reported missing or substituted.

## 2. Scope and core question

The task is a **targeted source-semantic completion**, not a third broad
extraction wave, not a backtest, and not strategy mining. The Steenbarger
false-breakout / range-reversion family is already selected
(`CURRENT_STATE.md` / `HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_1.md`):

- Target claims: `C-W2-006`, `C-W2-008`, `C-W2-017`
- Supporting context: `C-W2-002`, `C-W2-003`, `C-W2-009`

Core question (single final decision):

```text
Does official Steenbarger source material itself supply enough semantics to
define a coherent false-breakout / range-reversion Playbook using only
information surfaces the project currently owns, without silently deleting
source-critical TICK / Market Delta / sector / cross-market conditions?
```

- `YES` requires the official source to separately provide a faithful
  price/volume-only formulation.
- `NO` means a faithful formulation still materially depends on unavailable
  information, undefined source semantics, unsupported instrument transfer, or
  arbitrary project invention. A `NO` is a successful research result.

## 3. Source bundle

Bundle: `SB-SC-STEENBARGER-FALSE-BREAKOUT-V1` (11 official free/public
pre-2024 TraderFeed posts; all `TRACEABLE_ORIGINAL`,
`FREE_PUBLIC_UNAUTHENTICATED`, effective content date before 2024-01-01).

| material_id | title | date | role in this package |
|---|---|---|---|
| `SB-SC-M1` | Walking Through a Trade Setup | 2007-08-04 | candidate highs, trading range, invalidation (new highs), range-lows target, TICK+Market-Delta entry trigger, breakout-as-separate-setup, multi-timeframe focus list |
| `SB-SC-M2` | Three Basic Trade Setups | 2009-01-27 | reversal/breakout/continuation separation; range-edge/value-area; midpoint-or-pivot target; TICK/volume roles |
| `SB-SC-M3` | Making the Hard Trade | 2009-05-15 | failed prior-day-high breakout; morning range; reversion-to-VWAP first target; sector non-confirmation |
| `SB-SC-M4` | Catching False Breakouts | 2009-07-14 | false-breakout definition; return-to-range; reversion-to-VWAP; cross-index non-confirmation tell |
| `SB-SC-M5` | Trading Patterns: Failed Opening Range Breakout | 2007-06-06 | opening/preopening range; genuine-vs-failed breakout condition; midpoint target; TICK+volume integration |
| `SB-SC-M6` | The Relevance of VWAP in a Range Market | 2010-03-29 | VWAP definition; return-to-VWAP; range-breakout handicap via TICK/Cumulative Delta/intermarket |
| `SB-SC-M7` | Notes on Trading a Range Market | 2010-04-09 | range-day fade-away-from-VWAP; VWAP-amplitude rough rule (example-specific) |
| `SB-SC-M8` | A Simple Trading Template | 2009-02-14 | range-day template; fade-away-from-VWAP; pivot/overnight/prior-day-high levels; breadth+TICK conditions |
| `SB-SC-M9` | Breakouts From Trading Ranges: Making the Identification | 2009-02-11 | genuine-vs-false breakout identification; enhanced volume; sector participation; breadth plurality; VWAP; cross-asset revaluation |
| `SB-SC-M10` | The Trading Process: Day Structure | 2009-12-30 | seven day structures; range/false-breakout trading toward VWAP; breakout trading away from VWAP |
| `SB-SC-M11` | Anatomy of a False Breakout in the Stock Market | 2007-08-19 | false-breakout anatomy; TICK-thrust failure; return to range midpoint; enhanced-volume breakout |

The first three materials are the accepted Wave 2 bundle posts
(`SB-W2-M1/M2/M3`); the remaining eight are task-scoped semantic-completion
posts fetched directly from the official archive on 2026-08-19.

## 4. Field-by-field semantic matrix

Classification legend (source evidence only; never filled with a preferred
trading definition):

- `EXPLICITLY_PINNED`: the source gives an explicit, unambiguous semantic
  statement sufficient for faithful representation.
- `PARTIALLY_PINNED`: the source gives the concept/role but leaves a
  semantically meaningful boundary, measure, or selection undefined, or gives
  only example-specific instances.
- `NOT_PINNED`: the source references the concept but provides no defining
  semantics.
- `REQUIRES_UNAVAILABLE_INPUT`: the source semantics require an information
  surface the project does not own.

| # | semantic field | classification | primary source anchor(s) |
|---|---|---|---|
| 1 | GENERAL_MARKET_DIRECTION | PARTIALLY_PINNED | M1 closing (element 1); M1 step 5; M1 step 7 |
| 2 | TRADING_RANGE_BOUNDARY | PARTIALLY_PINNED | M1 step 6; M2 reversal; M5 preopening range; M4 definition |
| 3 | CANDIDATE_HIGH_OR_LOW | PARTIALLY_PINNED | M1 step 6; M1 closing (element 3/4) |
| 4 | MORNING_RANGE_BOUNDARY | NOT_PINNED | M3 failed-breakout reversion; M5 preopening/opening ranges |
| 5 | FALSE_BREAKOUT_DEFINITION | PARTIALLY_PINNED | M4 definition; M10 items 6/7 |
| 6 | FAILED_BREAKOUT_CONDITION | PARTIALLY_PINNED | M1 step 6; M5 failed opening range; M11 TICK-thrust failure |
| 7 | RETURN_TO_RANGE_CONDITION | PARTIALLY_PINNED | M4 definition; M3 reversion; M10 item 6 |
| 8 | NEW_HIGH_OR_LOW_INVALIDATION_REFERENCE | EXPLICITLY_PINNED | M1 step 7 (stop/target); M3 failed-breakout reversion |
| 9 | VWAP_DEFINITION_OR_SESSION_REFERENCE | PARTIALLY_PINNED | M6 VWAP definition; M8 range-market fade; M10 toward/away |
| 10 | ENTRY_PERMISSION | REQUIRES_UNAVAILABLE_INPUT | M1 step 7 entry trigger; M8 range-market fade |
| 11 | TARGET_BOUNDARY | PARTIALLY_PINNED | M1 step 7/9; M3 reversion-to-VWAP; M2 reversal targets; M4 return-to-VWAP; M5 midpoint |
| 12 | BREAKOUT_VS_RANGE_REVERSION_SEPARATION | EXPLICITLY_PINNED | M1 step 9; M2 three setups; M10 seven day structures |
| 13 | VOLUME_ROLE | PARTIALLY_PINNED | M1 step 4/8; M10 item 6; M9 enhanced volume / genuine-vs-false |
| 14 | PARTICIPATION_ROLE | REQUIRES_UNAVAILABLE_INPUT | M10 item 6; M9 genuine features; M8 item 1 |
| 15 | TICK_ROLE | REQUIRES_UNAVAILABLE_INPUT | M1 step 7/8; M2 reversal/breakout; M5 TICK failure; M11 TICK thrust |
| 16 | MARKET_DELTA_ROLE | REQUIRES_UNAVAILABLE_INPUT | M1 step 7; M1 step 6; M2 continuation |
| 17 | SECTOR_OR_CROSS_MARKET_CONFIRMATION_ROLE | REQUIRES_UNAVAILABLE_INPUT | M3 sector non-confirmation; M9 genuine features; M4 cross-index tell; M2 breakout |
| 18 | INSTRUMENT_SCOPE | EXPLICITLY_PINNED | M1 (ES); M5 (ER2); M11 (ER2); M9 (ES 30-min); M2 (SPX) |
| 19 | TIMEFRAME_SCOPE | PARTIALLY_PINNED | M1 closing; M4 definition; M10 day structure |

Counts:

```text
SEMANTICS_EXPLICITLY_PINNED=3
SEMANTICS_PARTIALLY_PINNED=10
SEMANTICS_NOT_PINNED=1
SEMANTICS_REQUIRES_UNAVAILABLE_INPUT=5
```

### 4.1 EXPLICITLY_PINNED (3)

**NEW_HIGH_OR_LOW_INVALIDATION_REFERENCE** — `M1 step 7`: "My stop is above the
13:39 highs--a move to new highs invalidates my idea." `M3`: "Unable to take out
yesterday's high, we moved back into the morning range." The invalidation
reference (a fresh new high/low beyond the candidate or prior-day level
invalidates the reversion read) is explicit and price-representable.

**BREAKOUT_VS_RANGE_REVERSION_SEPARATION** — `M1 step 9`: "I'm not playing for a
home run breakout trade. If the market moves into breakout mode, I'll consider
that a separate trade and setup." `M2`: Reversal/Breakout/Continuation
taxonomy. `M10`: seven day structures with trading toward VWAP in range/false-
breakout conditions and away from VWAP in breakout/trend conditions. The
separation is explicit and consistent.

**INSTRUMENT_SCOPE** — the source's tradeable scope in these examples is
explicitly US equity-index futures (ES, ER2) in an SPX/NYSE/NASDAQ/Russell
context with US sectors and breadth. `SOURCE_INSTRUMENT_SCOPE_EXPLICIT =
US_EQUITY_INDEX_FUTURES (ES, ER2) + US_INDEX_AND_SECTOR_BREADTH`. This field is
pinned to a universe the project does **not** own; see §6 for transfer.

### 4.2 PARTIALLY_PINNED (10)

Each of these has an explicit source concept but a semantically meaningful part
left open:

1. **GENERAL_MARKET_DIRECTION** — "the market's general direction", "direction
   of the general market trend", "the market's longer-term (day session)
   direction" are referenced as directional context; no operational measure is
   given (in the example it was assessed partly with Market Delta/TICK).
2. **TRADING_RANGE_BOUNDARY** — range concept explicit; the walk-through range
   is a discretionary bar example (13:30 lows / 13:39 highs); the prior-day
   value-area variant is unavailable; no general boundary rule.
3. **CANDIDATE_HIGH_OR_LOW** — concept explicit ("candidate highs"); the
   selection rule is the trader's real-time discretionary declaration, not a
   defined procedure (and was supported by TICK/volume/offer-volume
   non-expansion).
4. **FALSE_BREAKOUT_DEFINITION** — explicit definition "new highs or lows
   following an extended trading range, only to see trade return to that
   range" and "opens within a range and moves above the range, usually with
   limited participation and volume that wanes with higher prices, only to fall
   back into the range and return toward VWAP"; but "extended", "return", and
   "limited participation" are not quantified.
5. **FAILED_BREAKOUT_CONDITION** — part is price/volume observable (failure to
   make new highs; waning volume), but the source's full real-time
   identification integrates TICK distribution, TICK thrusts, and offer-side
   volume (unavailable). The source presents the integrated read as the
   identification method.
6. **RETURN_TO_RANGE_CONDITION** — explicit and price-based ("only to see trade
   return to that range"; "moved back into the morning range"); the extent /
   touch criterion is not defined.
7. **VWAP_DEFINITION_OR_SESSION_REFERENCE** — VWAP explicitly defined as the
   volume-weighted average price and referenced as the day session's VWAP;
   the exact computation window (session start) is not pinned, so any project
   computation needs an INFERRED session window.
8. **TARGET_BOUNDARY** — multiple explicit conventions (range lows; VWAP as a
   first target; range midpoint; prior pivot; opposite extreme on sustained
   strength); no unique PRIMARY target; pivot/value-area variants undefined or
   unavailable.
9. **VOLUME_ROLE** — role explicit (waning/enhanced/expanded/pickup), no
   numeric thresholds or relative-volume baseline pinned.
10. **TIMEFRAME_SCOPE** — "occurs at every time frame" / "follow one market
    across many time frames"; no single operating timeframe pinned (examples
    use 1-min, 3-min, 30-min).

### 4.3 NOT_PINNED (1)

**MORNING_RANGE_BOUNDARY** — "moved back into the morning range" and
"opening range"/"preopening range" are referenced (locating "the market's
estimate of value") but no start/end definition is given. Observable prices
exist, but the source semantics of the morning-range boundary are
`NOT_PINNED`; any morning-range definition would be invented.

### 4.4 REQUIRES_UNAVAILABLE_INPUT (5)

- **ENTRY_PERMISSION** — the source's only concrete entry trigger is TICK +
  Market Delta: "I sell when we make positive TICK readings and green Market
  Delta readings (more volume at offer than bid) that cannot make fresh price
  highs." The price/volume alternative ("fade moves away from VWAP that cannot
  sustain upside/downside price targets") is mentioned but not operationalized
  ("cannot sustain" is undefined). See §5.
- **PARTICIPATION_ROLE** — "limited participation", "fail to attract
  volume/participation", "vast majority of sectors should participate,
  expanding the plurality of advancing or declining stocks", "narrow breadth"
  are explicit distinguishing inputs; breadth/advance-decline is not in the
  corpus.
- **TICK_ROLE** — NYSE TICK is integral to entry, exit, reversal/breakout
  character, and genuine-vs-false identification; not owned, not OHLCV.
- **MARKET_DELTA_ROLE** — Market Delta (volume at offer vs bid) is integral to
  the entry/confirmation logic; not owned, not ordinary volume.
- **SECTOR_OR_CROSS_MARKET_CONFIRMATION_ROLE** — sector non-confirmation,
  sector participation, cross-index non-confirmation, and cross-asset
  revaluation are explicit confirmation/counterevidence inputs; not in the
  Chinese-futures corpus.

## 5. Price-volume-only stripping test (VERY IMPORTANT)

Forbidden transformation being tested:

```text
Steenbarger method: price + volume + TICK + Market Delta + sector/cross-market confirmation
-> delete TICK
-> delete Market Delta
-> delete confirmation
-> call the remaining price pattern "Steenbarger playbook"
```

The project may not do this unless Steenbarger separately provides a
source-supported price/volume-only formulation that makes TICK / Delta / sector
**optional** rather than integral.

### 5.1 What the source DOES supply at price/volume/VWAP level

The source supplies price/volume-based **descriptions**:

- False-breakout definition (`M4`): "A false breakout occurs when we get new
  highs or lows following an extended trading range, only to see trade return
  to that range."
- False-breakout-day structure (`M10` items 6/7): opens within a range, moves
  above/below the range with "volume that wanes with higher prices", falls back
  into the range "and return toward VWAP"; "an extension of range trading
  conditions."
- Trading direction (`M10`): "In range markets and on false breakouts, you'll
  be trading for moves toward VWAP and often the prior day's pivot level... you
  will be fading price strength and weakness in range and false breakout
  markets."
- Range-market fade (`M8`): "If you are playing a range market, you should fade
  moves away from VWAP that cannot sustain upside/downside price targets."
- Return to VWAP (`M6`): moves away from value "will tend to return back to
  (and usually through) VWAP."

VWAP itself is defined as the volume-weighted average price and is computable
from 1-minute OHLCV under an explicitly defined project calculation.

### 5.2 Why that is NOT an explicitly supported price/volume-only formulation

1. **The source's explicit entry permission requires unavailable inputs.**
   The only concrete entry trigger for this family is TICK + Market Delta
   (`M1 step 7`, claim `C-W2-005`, classified
   `NOT_OBSERVABLE_WITH_CURRENT_DATA`). No separate price/volume-only entry
   trigger is defined. The VWAP-fade sentence (`M8`) describes intent, not an
   operational entry rule ("cannot sustain ... targets" is undefined).

2. **Genuine-vs-false breakout identification requires unavailable inputs.**
   `M9` makes the identification explicit: "The key, then, is recognizing when
   a breakout is a genuine one and when it is false. Markets can move out of
   their ranges, only to fail to attract volume/**participation** and fall back
   toward their volume-weighted averages." Its genuine-breakout features
   include leading-sector confirmation, "the vast majority of sectors should
   participate ... expanding the plurality of advancing or declining stocks",
   and "similar revaluations among related asset classes." `M4` uses a
   cross-index non-confirmation "tell" (NASDAQ/Russell) and a Market Delta
   chart. `M5` and `M11` integrate TICK explicitly. These are identification
   inputs, not optional extras.

3. **The price/volume false-breakout definition is effectively ex-post.** "Only
   to see trade return to that range" is a characterization confirmed by the
   return; it does not, by itself, tell a machine when a breakout at the margin
   is false versus genuine. The source's own real-time distinction is bound to
   the unavailable identification inputs.

4. **No source anchor makes TICK/Delta/sector optional.** No post states "this
   can be traded with price and volume alone" or otherwise downgrades TICK /
   Delta / participation / sector / cross-market from integral to optional for
   this family.

### 5.3 Verdict

```text
PRICE_VOLUME_ONLY_FORMULATION_EXPLICITLY_SUPPORTED_BY_SOURCE=NO
```

There is no source-supported price/volume-only formulation that makes
TICK/Delta/sector optional. The price/volume description exists but is
insufficiently pinned (range boundary, candidate high, entry permission, target
uniqueness, morning range) and its real-time identification depends on inputs
the project does not own. A price/volume-only "Steenbarger playbook" on the
current corpus would be a project invention, not a source-faithful claim.

## 6. Instrument-transfer analysis

`SOURCE_INSTRUMENT_SCOPE_EXPLICIT` =
`US_EQUITY_INDEX_FUTURES (ES, ER2) + US_INDEX_AND_SECTOR_BREADTH` (SPX/NYSE/
NASDAQ/Russell context; XLE/XLF/XLB/XLV; advance-decline).

```text
SOURCE_SUPPORTS_CHINESE_FUTURES_TRANSFER=NO
```

- The source's "occurs on multiple time frames" / "occurs at every time frame"
  is **time-frame** language, and `M1` explicitly frames it as "follow **one**
  market across many time frames (which is different from following multiple
  markets in a single time frame)." It does not authorize transfer across
  unrelated markets/instruments.
- No source statement mentions Chinese futures or commodity futures as
  tradeable instruments for this method.
- The project corpus is Chinese futures (`cu, al, ni, au, ag, rb`). Transfer to
  those instruments would be an **INFERRED project hypothesis**, not an
  EXPLICIT Steenbarger claim, and could not become the same PRIMARY under the
  Claim Schema / Research Protocol v1.0.
- The source scope is not silently rewritten. The family stays scoped to the
  US equity-index futures / US breadth universe in source terms; the project's
  corpus is not a source-supported substitute universe for this method.

## 7. Observability matrix

Raw observability does **not** settle source semantics. The table separates
(a) source surface, (b) current project-observable portion, (c) missing
portion, and the resulting semantic classification.

| semantic field | observable on current corpus (1-min OHLCV + governed metadata) | missing / unowned | classification |
|---|---|---|---|
| GENERAL_MARKET_DIRECTION | possible via an interpreted trend proxy | no source-defined measure | PARTIALLY_PINNED |
| TRADING_RANGE_BOUNDARY | prices/highs/lows observable; boundary rule not | value-area variant (Market Profile) | PARTIALLY_PINNED |
| CANDIDATE_HIGH_OR_LOW | prices observable; selection rule not pinned | example used TICK/offer-volume | PARTIALLY_PINNED |
| MORNING_RANGE_BOUNDARY | prices observable | source never defines the boundary | NOT_PINNED |
| FALSE_BREAKOUT_DEFINITION | price + ordinary volume + VWAP observable | "participation"; unquantified extent | PARTIALLY_PINNED |
| FAILED_BREAKOUT_CONDITION | new-high failure, waning volume observable | TICK distribution/thrusts, offer-side volume | PARTIALLY_PINNED |
| RETURN_TO_RANGE_CONDITION | price observable | touch extent undefined | PARTIALLY_PINNED |
| NEW_HIGH_OR_LOW_INVALIDATION_REFERENCE | price observable | reference level needs interpreted definition | EXPLICITLY_PINNED |
| VWAP_DEFINITION_OR_SESSION_REFERENCE | computable from price+volume | exact session window (INFERRED needed) | PARTIALLY_PINNED |
| ENTRY_PERMISSION | "cannot make fresh price highs" portion observable | TICK + Market Delta trigger | REQUIRES_UNAVAILABLE_INPUT |
| TARGET_BOUNDARY | range lows / VWAP / midpoint observable | pivot formula, value area; uniqueness | PARTIALLY_PINNED |
| BREAKOUT_VS_RANGE_REVERSION_SEPARATION | representable | — | EXPLICITLY_PINNED |
| VOLUME_ROLE | ordinary volume observable | thresholds / relative-volume baseline | PARTIALLY_PINNED |
| PARTICIPATION_ROLE | — | breadth / advance-decline | REQUIRES_UNAVAILABLE_INPUT |
| TICK_ROLE | — | NYSE TICK | REQUIRES_UNAVAILABLE_INPUT |
| MARKET_DELTA_ROLE | — | bid/offer volume | REQUIRES_UNAVAILABLE_INPUT |
| SECTOR_OR_CROSS_MARKET_CONFIRMATION_ROLE | — | US sectors / indices / cross-asset | REQUIRES_UNAVAILABLE_INPUT |
| INSTRUMENT_SCOPE | cu/al/ni/au/ag/rb (not source scope) | ES/ER2 + US breadth | EXPLICITLY_PINNED (to non-owned universe) |
| TIMEFRAME_SCOPE | 1-min bars available | no pinned operating timeframe | PARTIALLY_PINNED |

No OHLCV proxy is authorized for any `REQUIRES_UNAVAILABLE_INPUT` row.

## 8. Missing inputs

The following source inputs are **not owned** by the current corpus and remain
missing (recorded, never substituted):

- NYSE TICK (distribution, extremes, thrusts) — integral to entry/exit and
  genuine-vs-false identification.
- Market Delta / bid-vs-offer volume ("green Market Delta", "volume at offer vs
  bid") — integral to the explicit entry trigger and candidate-high
  non-confirmation.
- Participation / breadth (advance-decline plurality, sector participation,
  "narrow breadth") — integral to genuine-vs-false identification and the
  range-day template.
- US sector / index / cross-market confirmation (XLE/XLF/XLB/XLV, SPX, NASDAQ,
  Russell, Treasury/currency repricing) — explicit confirmation/counterevidence
  surfaces.
- Prior-day value area (Market Profile) and pivot-level formulas
  (R1/R2/R3, S1/S2/S3) — referenced but not derivable/defined in the bundle.

Optional paid candidates (awareness only, per
`HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`): Market Delta software,
NYSE TICK/breadth feeds, US sector/index breadth feeds, Market Profile
value-area data. None are purchased or required for this decision; they cannot
be required merely to make this playbook work.

## 9. Contradictions / tensions between source posts

There are no direct logical contradictions, but there are **unresolved
tensions** that matter for operationalization:

1. **Target convention tension.** `M1` targets range lows for the short;
   `M3` targets VWAP as a "first target"; `M2` reversal targets the range
   midpoint "or the prior pivot"; `M4` targets a fade back into the day's range
   "for a move back to the VWAP", with "on sustained strength ... complete
   rotation through the range to the opposite extreme"; `M5` targets the
   midpoint of the opening range. The source does not pin one unique PRIMARY
   target for the family.

2. **Entry-permission tension (explicit vs sketch).** `M1` gives a precise
   TICK+Market-Delta entry trigger; `M8`/`M10` describe a VWAP-fade intent that
   is not operationalized. The explicit trigger is unavailable; the sketch is
   unpinned.

3. **False-breakout identification emphasis.** `M4` treats the price-based
   definition as primary and cross-index non-confirmation as a "tell"; `M9`
   treats participation/breadth/sector/cross-asset as genuine-breakout
   features; `M5`/`M11` make TICK thrusts central. These are complementary
   surfaces but none is optional in the source's own examples.

4. **"Participation" ambiguity.** `M10` uses "limited participation" in the
   false-breakout-day definition; `M9` uses "fail to attract
   volume/participation" and sector plurality. "Participation" is never defined
   as a single measurable quantity; it spans volume, breadth, and sectors.

None of these tensions is resolved by outcome data; they are recorded as source
semantics that remain open.

## 10. Source-negative / failure / invalidation context

The bundle preserves failure/no-trade/invalidation context (source-level, no
outcomes):

- `C-W2-002`: do not sell markets making new highs; do not chase highs on
  dwindling volume.
- `C-W2-003`: do not chase sellers; wait for a rally in the direction of the
  general trend.
- `C-W2-006`: a move to new highs invalidates the idea; target the range lows.
- `C-W2-008`: play for the highest-probability move (return to the range
  bottom), not a home run breakout; a breakout is a separate setup.
- `C-W2-016` (context): sector non-confirmation is counterevidence to an upside
  breakout in the example (not a universal rule — Wave 2 integration correction
  IC-2).
- `C-W2-017`: unable to take out the prior day's high; reverted into the
  morning range; reversion to VWAP as a first target.
- `M5`: if a revaluation is genuine, "we should not return to the prior trading
  range"; a failed opening-range breakout anticipates a return to the midpoint.
- `M9`: markets that "fail to attract volume/participation" fall back toward
  their volume-weighted averages (false-breakout failure mode).
- `M11`: TICK thrusts that no longer generate higher prices mark a stalling
  rally and a return to the range midpoint.

The bundle contains positive examples, near-miss/non-confirmation cases,
no-trade rules, and explicit invalidation statements. It does not contain a
systematic loss ledger or quantified failure rates (source-quality limitation,
recorded rather than manufactured).

## 11. Final decision

```text
SOURCE_FAITHFUL_PRICE_VOLUME_PLAYBOOK_DRAFTABLE=NO
PRICE_VOLUME_ONLY_FORMULATION_EXPLICITLY_SUPPORTED_BY_SOURCE=NO
SOURCE_SUPPORTS_CHINESE_FUTURES_TRANSFER=NO
PLAYBOOK_CONTRACT_CREATED=NO
```

Rationale (blocker classes):

```text
PRIMARY_BLOCKER=SOURCE_REQUIRES_TICK_AND_MARKET_DELTA_AND_SECTOR_OR_CROSS_MARKET_CONFIRMATION
```

Supporting blocker classes, all present:

- `SOURCE_REQUIRES_TICK` — entry permission, genuine-vs-false identification,
  exit timing (TICK distribution, thrusts, -1000 readings).
- `SOURCE_REQUIRES_MARKET_DELTA` — the explicit entry trigger ("green Market
  Delta"; volume at offer vs bid).
- `SOURCE_REQUIRES_SECTOR_OR_CROSS_MARKET_CONFIRMATION` — sector
  participation/non-confirmation, cross-index non-confirmation, cross-asset
  revaluation.
- `RANGE_DEFINITION_NOT_PINNED` — trading range / candidate high / morning
  range boundaries are not source-defined.
- `ENTRY_PERMISSION_NOT_PINNED` — the only price/volume entry sketch
  ("fade moves away from VWAP that cannot sustain targets") is not
  operationalized.
- `SOURCE_INSTRUMENT_TRANSFER_NOT_JUSTIFIED` — US equity-index futures scope is
  not source-authorized for Chinese futures.

Because even the price/volume core has unpinned range/candidate/entry/target
semantics, and the source's own entry and identification are bound to
unavailable inputs, no faithful non-outcome Playbook Contract can be drafted
without arbitrary project invention. The candidate family therefore remains
`SOURCE_SEMANTIC_COMPLETION_REQUIRED` / partially observable under the current
data budget.

## 12. SOURCE_ONLY session evidence

A new project-issued verified SOURCE_ONLY session was created using the actual
project implementation (`SourceOnlyPolicy.open_verified_session`,
`ApprovedSourceBundle`, `ClaimRecordOutput`, `ClaimRecordDraft`,
`SourceOnlyClaimExtractionContext` in `src/research_firewall.py`):

```text
SESSION_ID=SOURCE_ONLY_SEMANTIC_COMPLETION_STEENBARGER_FALSE_BREAKOUT_V1_20260819
MODEL_IDENTITY=deepseek-v4-flash
PROMPT_SPEC=STEENBARGER_FALSE_BREAKOUT_SEMANTIC_COMPLETION_V1
SOURCE_BUNDLE_IDENTITY=SB-SC-STEENBARGER-FALSE-BREAKOUT-V1
SOURCE_BUNDLE_HASH=82240a24e3e8aa04084198f25a5660f55d702f620f612aac13ca0b7813a6a80e
RETRIEVAL_MODE=LOCAL_FREE_PUBLIC_ORIGINAL_SOURCE_SEMANTIC_COMPLETION_ONLY
PROTECTED_MARKET_ACCESS_MODE=TECHNICALLY_DENIED
SOURCE_ONLY_IS_VERIFIED=YES
DENIAL_TEST_OUTCOME=DENIED
DENIAL_TEST_REASON=SOURCE_ONLY_TECHNICAL_DENIAL
RECORDED_RESOLUTIONS=19
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

## 13. Self-review

- Did I strip away an inconvenient source input? **No** — TICK / Market Delta /
  participation / sector / cross-market are all recorded as
  `REQUIRES_UNAVAILABLE_INPUT`; the price-only stripping test answered NO.
- Did I invent a range boundary? **No** — `TRADING_RANGE_BOUNDARY` and
  `MORNING_RANGE_BOUNDARY` remain PARTIALLY/NOT_PINNED; no boundary invented.
- Did I invent a VWAP session? **No** — VWAP's exact session window is left
  PARTIALLY_PINNED with an explicit INFERRED note.
- Did I invent a volume threshold? **No** — `VOLUME_ROLE` is PARTIALLY_PINNED;
  no numeric threshold added.
- Did I assume Chinese-futures transfer? **No** — `SOURCE_SUPPORTS_CHINESE_FUTURES_TRANSFER=NO`;
  any transfer would be an INFERRED hypothesis.
- Did I convert example-specific language into universal applicability? **No** —
  the "two points" VWAP-amplitude rule is recorded as example-specific; sector
  non-confirmation stays example-specific (IC-2).
- Did I promote source context into EXPLICIT claim? **No** — all EXPLICITLY_PINNED
  fields trace to direct source anchors; everything else is classified
  PARTIALLY/NOT_PINNED or REQUIRES_UNAVAILABLE_INPUT.
- Did I use outcomes? **No** — `NO_CANDIDATE_OUTCOME_DATA_USED=YES`; denial path
  exercised once; no canonical outcome surface touched.
- Did I use paid/authenticated material? **No** — free/public/unauthenticated
  only; paid items are awareness-only candidates.
- Did I rely on local memory instead of repo/source authority? **No** — all
  authority from repo files at the exact baseline; all semantics from the
  fetched official source pages.

## 14. Smallest safe next source action

The smallest safe next action is **not** to buy data by default. Consistent
with `HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md` and the triage:

1. Record this family as `SOURCE_FAITHFUL_PRICE_VOLUME_PLAYBOOK_DRAFTABLE=NO`
   and keep it as partially observable; do not proxy TICK/Delta/sector.
2. The source semantics that would be needed for a faithful operationalization
   (a defined trading-range/morning-range boundary, a defined candidate high/
   low, a defined price/volume entry permission, and a unique target
   convention) are **not present in the official pre-2024 TraderFeed material
   used**, and additional TraderFeed posts are unlikely to change the entry-
   permission binding (TICK+Market Delta) without a materially different
   source formulation.
3. The next bounded source action should be **source re-selection**: triage
   toward a different admitted source family whose method is expressed on
   surfaces the project owns (price/volume on the traded instrument), rather
   than purchasing the missing US equity surfaces.
4. Do not draft an incomplete Playbook Contract merely to show progress.

`NO_CANDIDATE_OUTCOME_DATA_USED=YES`
