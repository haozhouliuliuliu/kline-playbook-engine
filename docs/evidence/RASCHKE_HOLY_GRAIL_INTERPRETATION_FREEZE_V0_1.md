# RASCHKE_HOLY_GRAIL_INTERPRETATION_FREEZE_V0_1

> Version: 0.1
> Date: 2026-08-20
> Status: INTERPRETATION_FREEZE_DECISION / PRE_OUTCOME / NON_FROZEN_AS_MACHINE_READY
> Lane: F (HOLY_GRAIL_PLAYBOOK_CONTRACT_INTERPRETATION_FREEZE_ENGINEER)
> Family: `RASCHKE_HOLY_GRAIL_PULLBACK`
> Contract draft: `docs/research/playbook_candidates/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.md`
> Contract JSON: `docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.json`
> Semantic completion authority: `docs/research/semantic_completion/RASCHKE_HOLY_GRAIL_SEMANTIC_COMPLETION_V0_1.md`
> Playbook handoff: `docs/research/semantic_completion/RASCHKE_HOLY_GRAIL_PLAYBOOK_HANDOFF_V0_1.md`

```text
PRIMARY_FREEZE_READY=NO
AMBIGUOUS_STOP=YES
SOURCE_EXPLICIT_FIELDS=0
SOURCE_PARTIAL_PROJECT_INTERPRETATION_REQUIRED=1
PROJECT_INFERRED_PREDECLARED=7
UNRESOLVED_CRITICAL_AMBIGUITY=5
NOT_APPLICABLE=0
TIMEFRAME_PRIMARY=UNRESOLVED
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

---

## 1. Purpose

This document records the per-field interpretation-freeze decision for the
machine-facing meaning of the accepted Raschke Holy Grail source skeleton. It
applies the mandated non-outcome interpretation hierarchy:

```text
1. exact source statement;
2. literal deterministic interpretation requiring no additional market thesis;
3. already-governed project facts (minimum tick / session metadata);
4. stable mathematical or software convention, genuinely unambiguous and
   clearly labeled PROJECT_INFERRED;
5. otherwise STOP.
```

It never chooses between equally plausible research meanings arbitrarily, and
it never uses candidate results, chart performance, trade count, apparent
convenience, or "this usually works better".

## 2. Field classification legend

```text
SOURCE_EXPLICIT                              source pins the machine meaning exactly
SOURCE_PARTIAL_PROJECT_INTERPRETATION_REQUIRED  source pins concept; machine meaning needs project interpretation
PROJECT_INFERRED_PREDECLARED                 project predeclares a labeled INFERRED convention (never a source claim)
UNRESOLVED_CRITICAL_AMBIGUITY                multiple materially different equally-plausible definitions; STOP
NOT_APPLICABLE                               not relevant for this family
```

## 3. Field-by-field classification (13 fields)

| # | field | classification | basis / reason |
|---|---|---|---|
| 1 | `EMA_PRICE_INPUT` | `PROJECT_INFERRED_PREDECLARED` | Source never states the EMA price basis (`MOVING_AVERAGE_PRICE_INPUT=NOT_PINNED`). A close-based EMA is adopted as the genuinely unambiguous standard software/math convention; clearly labeled INFERRED (branch `INT-EMA-PRICE-INPUT-CLOSE`). Not a source claim. |
| 2 | `EMA_TOUCH_BAR_SEMANTICS` | `PROJECT_INFERRED_PREDECLARED` | Source says "when price touches the 20-period MA"; bar-level touch not pinned. Adopted machine interpretation: `bar.low <= EMA <= bar.high` (long side) (branch `INT-EMA-TOUCH-INTRABAR`). Not silently equated with close crossing. |
| 3 | `ADX_RISING_MACHINE_SEMANTICS` | `PROJECT_INFERRED_PREDECLARED` | Source requires "initially greater than 30 AND rising"; slope measurement window not pinned. Minimal literal deterministic reading: `ADX[current] > ADX[previous]` at the context bar (branch `INT-ADX-RISING-1BAR`), clearly labeled INFERRED. |
| 4 | `ENTRY_ABOVE_PREVIOUS_HIGH_TICK_OFFSET` | `PROJECT_INFERRED_PREDECLARED` | Source pins the reference level ("above the high of the previous bar") but not the tick offset. Governed contract tick metadata makes the minimal legal price one tick above; recorded as a project operational convention (branch `INT-ENTRY-OFFSET-1TICK`), NOT source-exact ("one tick"). |
| 5 | `NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION` | `UNRESOLVED_CRITICAL_AMBIGUITY` | Source pins the protective-stop reference concept ("newly formed swing low") but no software pivot algorithm. Fractal / leg / zigzag pivot definitions remain materially different and equally plausible. STOP; not labeled SOURCE_EXPLICIT. |
| 6 | `NEWLY_FORMED_SWING_HIGH_MACHINE_DEFINITION` | `UNRESOLVED_CRITICAL_AMBIGUITY` | Mirror of the swing-low definition for the short side; same unresolved pivot-algorithm gap. STOP. |
| 7 | `PROTECTIVE_STOP_ACTIVATION_TIME` | `PROJECT_INFERRED_PREDECLARED` | Source says "Once filled, enter a protective sell stop"; activation timing after fill is not separately pinned. Adopted deterministic convention: protective stop active from the first eligible future bar after the entry fill, no same-bar-before-fill activation (branch `INT-STOP-ACTIVATION-AFTER-FILL`), consistent with the generic stop-trigger "first eligible future bar" convention. |
| 8 | `TRAILING_STOP_MACHINE_DEFINITION` | `UNRESOLVED_CRITICAL_AMBIGUITY` | "Trail stops as profits grow" pins the concept but not the mechanics; swing/MA/distance-based trail definitions remain materially different and equally plausible. STOP. |
| 9 | `EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION` | `UNRESOLVED_CRITICAL_AMBIGUITY` | "Look to exit on a push to new highs" (long-side first-retracement exit context) pins the concept but not the reference level or confirmation semantics. STOP. |
| 10 | `LONG_SHORT_MIRROR_DETAILS` | `SOURCE_PARTIAL_PROJECT_INTERPRETATION_REQUIRED` | Source explicitly says "sells reversed" (mirror concept is source-explicit; branch `INT-LONG-SHORT-MIRROR`). The machine mirror details (sell stop below previous-bar low; protective stop at newly formed swing high) are the literal reversal but inherit the unresolved swing-high machine definition. |
| 11 | `OPERATING_TIMEFRAME` | `UNRESOLVED_CRITICAL_AMBIGUITY` | Source is explicitly multi-timeframe (base chart then 30/60/120-minute). No single project PRIMARY timeframe can be justified from source/documentary evidence alone. `TIMEFRAME_PRIMARY=UNRESOLVED`; several timeframes are NOT hidden behind a tunable parameter. |
| 12 | `SESSION_BOUNDARY` | `PROJECT_INFERRED_PREDECLARED` | Source silent on session boundary. Already-governed project fact: official trading-day identity via `SessionMetadata` (branch `INT-SESSION-OFFICIAL-TRADING-DAY`), not civil-date inference. |
| 13 | `CURRENT_PROJECT_INSTRUMENT_SCOPE` | `PROJECT_INFERRED_PREDECLARED` | Source scope is US equities/US index; Chinese-futures support UNKNOWN. All six products (cu,al,ni,au,ag,rb) are predeclared as the fixed project research scope BEFORE any outcome access (branch `INT-INSTRUMENT-SCOPE-6PRODUCTS`); transfer is `INFERRED_PROJECT_TRANSFER`, never presented as Raschke's explicit scope. |

### Counts

```text
SOURCE_EXPLICIT_FIELDS=0
SOURCE_PARTIAL_PROJECT_INTERPRETATION_REQUIRED=1  (LONG_SHORT_MIRROR_DETAILS)
PROJECT_INFERRED_PREDECLARED=7  (1,2,3,4,7,12,13)
UNRESOLVED_CRITICAL_AMBIGUITY=5  (5,6,8,9,11)
NOT_APPLICABLE=0
TOTAL=13
```

## 4. Why PRIMARY_FREEZE_READY=NO

`YES` would require exactly one explicit project interpretation package with no
remaining CRITICAL interpretation ambiguity, no hidden variants, and no
outcome-selected meaning. That is not the case:

- `NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION` and
  `NEWLY_FORMED_SWING_HIGH_MACHINE_DEFINITION` are critical: the source pins
  the protective-stop reference concept but not a software pivot algorithm, and
  multiple materially different pivot definitions remain equally plausible. Per
  the task rule, these are `UNRESOLVED_CRITICAL_AMBIGUITY`, which forces
  `PRIMARY_FREEZE_READY=NO`.
- `TRAILING_STOP_MACHINE_DEFINITION`,
  `EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION`, and `OPERATING_TIMEFRAME`
  are also critical unresolved machine semantics.

Therefore:

```text
PRIMARY_FREEZE_READY=NO
AMBIGUOUS_STOP=YES
```

This is a successful result. Alternatives are preserved (section 5). The
machine-facing meaning is NOT frozen enough for operationalization yet.

## 5. Preserved alternatives (AMBIGUOUS_STOP)

### 5.1 NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION (and swing-high mirror)

The source pins the protective-stop reference concept only. Equally plausible
and materially different machine definitions that remain preserved (none
selected):

- fractal pivot: a bar whose low is lower than both neighbors (lookback N);
- leg/zigzag pivot: a swing low confirmed by a subsequent move up by a
  threshold amount;
- rolling-minimum low over a fixed lookback window;
- other software pivot conventions.

None is chosen here; choosing any of them would require outcome-free
justification that the source does not provide. The short-side mirror uses the
same definition for swing highs.

### 5.2 TRAILING_STOP_MACHINE_DEFINITION

"Trail stops as profits grow" is preserved as a source concept. Equally
plausible machine mechanics (not selected): trailing below the most recent
swing low; trailing below a moving average; trailing by a fixed distance;
trailing by an ATR-based distance.

### 5.3 EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION

"Look to exit on a push to new highs" (long-side first-retracement setup) is
preserved as a source concept. Equally plausible machine definitions (not
selected): exit on the first close at a new high; exit on the first bar whose
high exceeds the reference high; exit when price pushes to a new high relative
to a pre-entry swing high; with or without tick-offset/confirmation semantics.

### 5.4 OPERATING_TIMEFRAME

The source-permitted timeframe set is preserved explicitly:
`BASE, 30MIN, 60MIN, 120MIN`. No single operating timeframe is source-justified
and no tunable parameter hides the choice. A primary timeframe may be adopted
in a later lane only with a non-outcome justification; otherwise the family
remains `TIMEFRAME_PRIMARY=UNRESOLVED`.

## 6. Anti-outcome safeguards

- No candidate market outcome, PnL, return, expectancy, win rate, Sharpe,
  equity/drawdown, validation, or historical final-holdout access was used or
  requested.
- No real `StrategyIdentity` was created; nothing was registered in any
  `StrategyCatalog`; no `ResearchFirewall` outcome access was requested.
- No source claim was invented; all 27 claims are bound from the accepted
  SOURCE_ONLY evidence.
- Inferred conventions are predeclared and versioned before any outcome access
  and are never tuned on outcomes.

```text
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```
