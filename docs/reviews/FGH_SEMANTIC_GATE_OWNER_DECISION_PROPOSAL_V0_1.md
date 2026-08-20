# FGH_SEMANTIC_GATE_OWNER_DECISION_PROPOSAL_V0_1

> Version: 0.1
> Date: 2026-08-20
> Role: FGH semantic-gate decision preparation (research / decision-preparation ONLY, NOT implementation)
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Branch: `research/fgh-semantic-gate-decision-package-v01`
> Status: `PROPOSAL_ONLY_NOT_ADOPTED`
> Authority chain: `CURRENT_STATE.md`, `docs/reviews/R2_FOUR_LANE_EXECUTION_PLAN_V0_1.md` (Lane 3), `docs/reviews/FGH_CODEX_REBUILD_PREPARATION_V0_1.md`, `docs/reviews/FGH_CODEX_REBUILD_FINDING_MATRIX_V0_1.json`, frozen `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`, accepted `RASCHKE_HOLY_GRAIL_SEMANTIC_COMPLETION_V0_1.md` / `RASCHKE_HOLY_GRAIL_PLAYBOOK_HANDOFF_V0_1.md`, Holy Grail source bundle (`SB-RASCHKE-HOLY-GRAIL-SEMANTIC-V1`), old F interpretation draft (`RASCHKE_HOLY_GRAIL_INTERPRETATION_FREEZE_V0_1.md`, `git show` on old F branch only).

```text
PURPOSE=prepare ALL remaining Holy Grail machine-semantic decisions for Owner in one pass
DECISION_STATUS=PROPOSAL_ONLY_NOT_ADOPTED
SRC_PRODUCTION_DIFF=0
CANDIDATE_OUTCOME_DATA_USED=NO
VALIDATION/HOLDOUT_ACCESS=NOT_AUTHORIZED
RECOMMENDED_SAFE_DEFAULT != ADOPTED
NOTHING_HERE_IS_FROZEN
COVERAGE=FGH-GATE-01..06 + NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION
       + TRAILING_STOP_MACHINE_DEFINITION + EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION
```

This document is a single, complete Owner-decision-preparation package. Its
purpose is to surface every remaining Holy Grail machine-semantic decision at
once so that no single unresolved semantic gate re-surfaces one-by-one later
(per the repair-exit criterion in `CURRENT_STATE.md`). It makes **no**
production change and adopts **nothing**.

## 0. Baseline and study method

### 0.1 Tree

Created fresh from latest `origin/main` as
`research/fgh-semantic-gate-decision-package-v01`.

```text
MAIN_HEAD=e0cf182475fb9c39bd2b40447e49cba9909ae4cb
BRANCH=research/fgh-semantic-gate-decision-package-v01
```

### 0.2 Decision-preparation inputs read (never candidate outcome)

- `CURRENT_STATE.md`
- `docs/reviews/R2_FOUR_LANE_EXECUTION_PLAN_V0_1.md`
- `docs/reviews/FGH_CODEX_REBUILD_PREPARATION_V0_1.md`
- `docs/reviews/FGH_CODEX_REBUILD_FINDING_MATRIX_V0_1.json`
- frozen `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- accepted `RASCHKE_HOLY_GRAIL_SEMANTIC_COMPLETION_V0_1.md`
- accepted `RASCHKE_HOLY_GRAIL_PLAYBOOK_HANDOFF_V0_1.md`
- Holy Grail source bundle `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json`
- Holy Grail SOURCE_ONLY session `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json`
- old F interpretation draft `RASCHKE_HOLY_GRAIL_INTERPRETATION_FREEZE_V0_1.md`
  (read via `git show` on `parallel/holy-grail-playbook-contract-draft-v01`; not merged)

The candidate outcome backtest is **not** read and remains `NOT_AUTHORIZED`.

### 0.3 Mandatory decision basis

Per frozen Protocol v1.0 and the Lane-3 boundary, every recommendation in this
package is justified **only** by:

```text
FAIL_CLOSED
SOURCE_FAITHFUL
CAUSAL
REPRODUCIBLE
MINIMUM_HIDDEN_DEGREES_OF_FREEDOM
```

and is **never** justified by PnL / Sharpe / trade count. No option below is
selected "because it backtests better".

---

## 1. GATE-01 — EMA touch: price input and touch definition

### 1.1 Source re-check

The accepted source bundle re-verified the official free/public Raschke index
(`https://lindaraschke.net/articles/`, HTTP 200 on 2026-08-20) and found **no
additional** official free/public pre-2024 article that distinguishes either
(a) the EMA price input or (b) the bar-level touch definition.

```text
MOVING_AVERAGE_TYPE        = EXPLICITLY_PINNED (exponential)
MOVING_AVERAGE_PERIOD      = EXPLICITLY_PINNED (20)
MOVING_AVERAGE_PRICE_INPUT = SOURCE_NOT_PINNED  (source never states the price basis)
PULLBACK_TOUCH_OR_PENETRATION_RULE = PARTIALLY_PINNED
   (concept "when price touches the 20-period MA" pinned; the bar-level definition of
    "touches" — intrabar low/high vs close vs penetration — is NOT pinned)
```

Both the EMA price input and the touch definition therefore remain
`SOURCE_NOT_PINNED`. The source cannot further separate them beyond this
package's existing classification. Old F's `INT-EMA-PRICE-INPUT-CLOSE`
(close-based EMA) and `INT-EMA-TOUCH-INTRABAR` (`bar.low <= EMA <= bar.high`)
are **labeled INFERRED branches**, not source facts.

### 1.2 Decision block

```text
DECISION_ID=FGH-GATE-01
SOURCE_STATUS=SOURCE_NOT_PINNED (both EMA price input and touch definition)
QUESTION=Which EMA price input (close / typical / high-low) AND which bar-level
         touch definition does the Holy Grail PRIMARY adopt?
OPTION_A=close-based EMA + intrabar touch low<=EMA<=high (old F predeclared INFERRED
         branch); REQUIRES the same-bar causality of the close-based EMA reference to
         be resolved first, else it is look-ahead
OPTION_B=prior-available EMA reference: EMA is computed only from bars strictly before
         the current bar (no current-bar-close EMA); touch is defined on the bar where
         that prior-available EMA is already observable (e.g. bar.low <= EMA_prior <= bar.high).
         Causal, no look-ahead.
OPTION_C=other EMA price input (typical / high-low) with an explicitly defined touch rule
PROJECT_BRAIN_RECOMMENDATION=OPTION_B (prior-available EMA reference) combined with a
         standard close-based EMA evaluated only on prior completed bars. This is the only
         option that is causal (a close-based EMA is not available during the same bar it
         would judge). The price-input sub-choice remains an explicitly labeled INFERRED
         project convention (standard close-based), never a source claim.
RECOMMENDATION_REASON=FAIL_CLOSED + CAUSAL: an EMA computed on the current bar's close
         cannot legitimately judge the same bar's touch (look-ahead). Using a
         prior-available reference is causal, source-faithful to "price touches the MA",
         reproducible, and adds the minimum hidden degrees of freedom. SOURCE_NOT_PINNED
         is retained for the price basis.
OUTCOME_EFFECT=defines which bars emit EMA-touch signals and the entry-stop placement;
         materially changes entry bars/prices. A close-based same-bar comparison is
         look-ahead unless redefined (audit L-01).
CAN_CODEX_IMPLEMENT_GENERIC_MACHINERY_BEFORE_DECISION=YES (generic, parameterized EMA
         computation + touch-signal layer can be built without freezing which variant is
         PRIMARY; the prior-available causality constraint should be encoded as an
         invariant)
BLOCKS_HOLY_GRAIL_MACHINE_READY=YES
```

---

## 2. GATE-02 — ADX rising: sequence and timing

### 2.1 Source re-check of the timing

```text
ADX_PERIOD                 = EXPLICITLY_PINNED (14)
ADX_THRESHOLD              = EXPLICITLY_PINNED (>30)
ADX_RISING_OR_LEVEL_REQUIREMENT = EXPLICITLY_PINNED ("must initially be greater than 30
                                 AND rising"; slope measurement window NOT pinned / INFERRED)
M01 step 2                 = "retracement ... usually accompanied by a turndown in ADX"
```

Source timing decomposition:

- **Step 1** (M01) is an **initial/context** filter: "The 14-period ADX must
  initially be greater than 30 and rising." This is the state of the market
  that justifies entering the pullback setup — a pre-setup context.
- **Step 2** (M01) describes the **pullback phase**: price retraces to the
  20-EMA and this retracement is "usually accompanied by a turndown in ADX."

Therefore the source does **not** require ADX to still be rising **at the
touch bar**. On the contrary, the source's own qualitative wording associates
the pullback phase with an ADX turndown. Old F's `INT-ADX-RISING-1BAR`
(`ADX[current] > ADX[previous]` at the context/touch bar) is a **project-added
requirement**, not a source fact, and would contradict the "turndown during
pullback" nuance if evaluated at the touch bar.

### 2.2 Decision block

```text
DECISION_ID=FGH-GATE-02
SOURCE_STATUS=ADX>30 AND "rising" pinned as an initial context; slope window NOT pinned;
         pullback usually accompanied by an ADX turndown (qualitative). The source does NOT
         uniquely pin the relative-to-which-bar timing of "rising".
QUESTION=At which bar/window is "ADX rising" evaluated relative to the pullback/touch?
OPTION_A=old F one-bar ADX[t]>ADX[t-1] at the context/touch bar (project-added; NOT a
         source fact; conflicts with the "turndown during pullback" nuance)
OPTION_B=ADX>30 and rising measured over an explicit lookback window, evaluated as the
         INITIAL context before the setup/pullback (the touch bar does not need to be
         rising). Source-faithful "initially >30 and rising".
OPTION_C=explicit pullback-phase model (rising context window + explicit ADX turndown
         during the pullback)
PROJECT_BRAIN_RECOMMENDATION=OPTION_B, kept as a clearly labeled INFERRED project
         convention: "rising" is evaluated over an explicit deterministic window at the
         context/setup bar before entry, and the touch bar is NOT required to be rising.
         This is the closest source-faithful reading of "initially >30 and rising".
RECOMMENDATION_REASON=SOURCE_FAITHFUL + FAIL_CLOSED: OPTION_A is not source-supported and
         would silently contradict the source's own pullback-turndown wording; OPTION_B
         preserves the source's initial-context meaning with a single explicit slope-window
         convention (minimum hidden DOF) and no look-ahead. Old F's one-bar convention must
         not silently stand as if it were source semantics.
OUTCOME_EFFECT=defines which bars qualify as Holy Grail contexts; changes entry timing and
         trade count.
CAN_CODEX_IMPLEMENT_GENERIC_MACHINERY_BEFORE_DECISION=YES (deterministic ADX computation is
         generic; the "rising" evaluation window can be parameterized and bound later)
BLOCKS_HOLY_GRAIL_MACHINE_READY=YES
```

---

## 3. GATE-03 — EMA / ADX numeric feature semantics

### 3.1 Scope

This gate compares **machine conventions only**: EMA seed/warmup, Wilder ADX
initialization, decimal precision, rounding/quantization. It is forbidden to
choose these by strategy outcome. The source is silent on every one of these;
they are engineering feature semantics, not source facts.

```text
SOURCE_STATUS=SOURCE_SILENT (source cannot decide numerical implementation)
```

### 3.2 Decision block

```text
DECISION_ID=FGH-GATE-03
SOURCE_STATUS=SOURCE_SILENT (all numeric conventions are project machine-operationalization)
QUESTION=Which numeric implementation (seed / warmup / init / rounding / precision) is the
         project machine convention for EMA and Wilder ADX?
OPTION_A=documented standard conventions: SMA-seeded EMA (first EMA = SMA of first `period`
         closes; alpha=2/(period+1); INSUFFICIENT_HISTORY before `period` bars); Wilder ADX
         init (first smoothed = sum of first `period` raw; first ADX = simple average of
         first `period` DX; recursive update; first ADX at index 2*period-1); exact Decimal
         arithmetic; single explicit output quantization (6dp ROUND_HALF_UP per-step).
         (Matches old G's documented ENGINEERING convention.)
OPTION_B=exact Decimal with NO intermediate quantization; quantize only at output boundaries
OPTION_C=another explicit policy
PROJECT_BRAIN_RECOMMENDATION=OPTION_A (adopt the documented standard conventions as
         ENGINEERING feature semantics, explicitly labeled ENGINEERING, NOT research-frozen
         merely by adoption). Selection is based on STANDARDNESS, REPRODUCIBILITY,
         CAUSALITY, and IMPLEMENTATION STABILITY — never on outcome.
RECOMMENDATION_REASON=STANDARD + REPRODUCIBLE + IMPLEMENTATION_STABLE: SMA-seeded EMA and
         Wilder initialization are the widely documented standard conventions, give a
         deterministic warmup, and are the most stable to re-implement and audit. A single
         explicit quantization policy (6dp ROUND_HALF_UP per-step) makes every intermediate
         reproducible. No outcome-based selection is used.
OUTCOME_EFFECT=EMA-touch and ADX>30 classification change with seed/warmup/rounding;
         outcome-affecting.
CAN_CODEX_IMPLEMENT_GENERIC_MACHINERY_BEFORE_DECISION=YES (a parameterized numeric engine can
         be built; the specific convention BINDING is this gate and must not be frozen by
         Codex)
BLOCKS_HOLY_GRAIL_MACHINE_READY=YES
```

---

## 4. GATE-04 — Same-bar EMA touch -> entry trigger

### 4.1 Context

At 1-minute resolution the project owns only completed-bar OHLC and cannot see
intrabar ordering between an EMA touch and the entry-stop threshold being
reached inside one bar. The source pins the concept (touch EMA -> buy stop above
previous-bar high) but not the intra-bar ordering.

### 4.2 Decision block

```text
DECISION_ID=FGH-GATE-04
SOURCE_STATUS=entry-trigger concept EXPLICITLY_PINNED; intra-bar ordering NOT observable at 1m
QUESTION=When EMA touch and the entry-stop threshold are both reached inside one 1-minute
         bar, what is the machine policy?
OPTION_A=FAIL_CLOSED same-bar ambiguous (AMBIGUOUS_INTRABAR_SEQUENCE): no entry on that bar
OPTION_B=defer to next bar (touch evaluated on the prior completed bar; entry-stop placed /
         triggered only from the next bar)
OPTION_C=require finer data (a finer intrabar-ordered chronology; NOT available at 1m)
PROJECT_BRAIN_RECOMMENDATION=OPTION_A (fail-closed same-bar ambiguous), consistent with old
         H's existing AMBIGUOUS_INTRABAR_SEQUENCE semantics.
RECOMMENDATION_REASON=FAIL_CLOSED + MINIMUM_HIDDEN_DEGREES_OF_FREEDOM: with ordering
         unobservable at 1m, OPTION_A declines to invent an ordering, whereas OPTION_B
         silently imposes an ordering that changes entry prices. OPTION_C is not available
         with current data. No outcome-based selection.
OUTCOME_EFFECT=determines whether ambiguous same-bar bars produce entries; direct
         entry/trade-count effect.
CAN_CODEX_IMPLEMENT_GENERIC_MACHINERY_BEFORE_DECISION=YES (same-bar ambiguity detection
         machinery already exists in old H and can be reused; the policy binding is this
         gate)
BLOCKS_HOLY_GRAIL_MACHINE_READY=YES
```

---

## 5. GATE-05 — Entry fill -> protective stop (and chronology model)

### 5.1 Context

The source pins "Once filled, enter a protective sell stop at the newly formed
swing low" (M01 step 4). At 1-minute resolution the project cannot distinguish
fill-then-stop from stop-then-fill inside one bar:

```text
INTRABAR_ORDERING=NOT_OBSERVABLE_AT_1M
```

Old F's `INT-STOP-ACTIVATION-AFTER-FILL` (protective stop active only from the
first eligible future bar, i.e. no same-bar post-fill stop) **silently erases
the same-bar risk**. It is flagged by audit L-05 and must not be the default
recommendation.

### 5.2 Decision block

```text
DECISION_ID=FGH-GATE-05
SOURCE_STATUS="Once filled, enter a protective stop" EXPLICITLY_PINNED; intra-bar ordering
         NOT_OBSERVABLE_AT_1M; old F next-bar activation is an OBSOLETE sub-construct
QUESTION=Which conservative policy covers same-bar fill + protective-stop ordering, and
         which execution chronology does the stop bridge claim?
OPTION_A=completed-bar conservative + AMBIGUOUS_INTRABAR_SEQUENCE for the same-bar
         fill/stop event (fail-closed; explicitly labeled; NEVER called exchange-resting)
OPTION_B=next-bar-only protective-stop activation (old F INT-STOP-ACTIVATION-AFTER-FILL);
         REJECTED as a silent same-bar risk suppression unless the Owner explicitly
         overrides
OPTION_C=finer intrabar evidence (a separately justified intrabar/gap-through chronology;
         requires project-owned intrabar evidence not available at 1m)
PROJECT_BRAIN_RECOMMENDATION=OPTION_A (completed-bar conservative + ambiguity), with the
         bridge explicitly declaring its model as "completed-bar availability,
         conservative" and never presenting it as exchange-resting chronology.
RECOMMENDATION_REASON=FAIL_CLOSED + SOURCE_FAITHFUL: the source says the protective stop
         exists after fill; OPTION_A does not pretend to know same-bar ordering and does
         not erase same-bar risk. OPTION_B silently suppresses risk and OPTION_C is not
         available with current data. Old F's next-bar convenience is not a valid stand-in
         for "no same-bar risk".
OUTCOME_EFFECT=defines the protective-stop loss path and any same-bar ambiguity handling;
         interacts with entry fill, gap-through, and OCO (audit L-16 / L-17).
CAN_CODEX_IMPLEMENT_GENERIC_MACHINERY_BEFORE_DECISION=YES (reuse old H's
         AMBIGUOUS_INTRABAR_SEQUENCE; the chronology claim must be explicit and honest)
BLOCKS_HOLY_GRAIL_MACHINE_READY=YES
```

---

## 6. GATE-06 — Operating timeframe PRIMARY

### 6.1 Context

The source is explicitly multi-timeframe: the setup first on the base chart, then
the same retracement on the 30-minute, 60-minute, and 120-minute timeframes,
each retracement preceded by a 14-bar ADX>30 on that timeframe (M05). The Owner's
final machine PRIMARY must be **single** timeframe (Package C P-05 bridge
requires one `timeframe_scope`). The choice is **not** made by backtest.

### 6.2 Non-outcome justification matrix

`BASE` denotes the base chart on which the source's core 4-step rules are
described; `30m/60m/120m` are the higher-timeframe confirmations.

| criterion | BASE | 30m | 60m | 120m |
|---|---|---|---|---|
| SOURCE_PROMINENCE | Highest — the M01 core 4-step entry/setup rules anchor on the base chart; M05 lists BASE first, then 30/60/120 as the unfolding sequence | Medium — first HTF confirmation in M05 | Medium — second HTF confirmation | Lowest — final HTF in M05 ("by then you should be looking for a top") |
| DATA_OBSERVABILITY | OBSERVABLE_NOW (owned 1m base; full canonical granularity) | OBSERVABLE_NOW (derivable by aggregation from 1m; D-02 window authority) | OBSERVABLE_NOW (derivable) | OBSERVABLE_NOW (derivable; least bars per trading day) |
| WARMUP_REQUIREMENTS | Lowest absolute calendar history for EMA(20)/ADX(14) at the base; most bars per day | Moderate warmup (needs enough 30m bars) | Higher warmup | Highest warmup (needs enough 120m bars; fewest bars per session) |
| SEMANTIC_FIDELITY | Highest — the source's explicit entry/setup/stop/exit rules (M01) are described at the base-chart level | Confirmatory role (M05) | Confirmatory role | Confirmatory role |

No PnL is compared. The matrix is purely about source prominence, observability,
warmup, and semantic fidelity.

### 6.3 Decision block

```text
DECISION_ID=FGH-GATE-06
SOURCE_STATUS=multi-timeframe EXPLICIT (base then 30/60/120-minute); no single operating
         timeframe pinned by the source
QUESTION=Which single operating timeframe is the Holy Grail PRIMARY?
OPTION_A=BASE
OPTION_B=30MIN
OPTION_C=60MIN / 120MIN
PROJECT_BRAIN_RECOMMENDATION=OPTION_A (BASE) as the source-faithful PRIMARY proposal,
         retained as a PROPOSAL ONLY. The source's explicit entry/setup/stop/exit rules are
         anchored at the base chart; 30/60/120 are higher-timeframe confirmations, not the
         PRIMARY entry anchor. No default is adopted; TIMEFRAME_PRIMARY remains UNRESOLVED
         until the Owner selects with a non-outcome justification.
RECOMMENDATION_REASON=SOURCE_PROMINENCE + SEMANTIC_FIDELITY + DATA_OBSERVABILITY: the
         source's 4-step core rules describe the base chart; BASE has the highest source
         prominence and semantic fidelity for the PRIMARY entry loop, and full observability
         on the owned corpus. Not chosen by PnL.
OUTCOME_EFFECT=the bridge requires exactly one timeframe_scope (Package C P-05); no PRIMARY
         / MACHINE_READY Holy Grail strategy is possible until resolved; machinery must not
         hard-code it.
CAN_CODEX_IMPLEMENT_GENERIC_MACHINERY_BEFORE_DECISION=YES (30/60/120 aggregation is generic
         machinery per L-08; the PRIMARY timeframe binding is this gate and must not be
         hard-coded)
BLOCKS_HOLY_GRAIL_MACHINE_READY=YES
```

---

## 7. NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION

### 7.1 Context

The source pins the protective-stop reference concept ("protective sell stop at
the newly formed swing low", M01 step 4) but no software pivot algorithm. Old F
records `UNRESOLVED_CRITICAL_AMBIGUITY`. The short side is the mirror (newly
formed swing high). The machine definition must be split into its required
components so future Codex does not silently pick a pivot algorithm.

```text
SOURCE_STATUS=concept EXPLICITLY_PINNED; pivot algorithm SOURCE_NOT_PINNED
```

Required sub-components (each option must fix all of these):

```text
PIVOT_CONFIRMATION         how a swing low is identified (fractal / leg-zigzag / rolling-min)
LEFT/RIGHT_CONFIRMATION    how many bars each side confirm the pivot
AVAILABILITY_TIME          the point-in-time at which the pivot becomes observable
SAME_BAR_AVAILABILITY      whether the pivot can be known on the same bar as the entry fill
STOP_ACTIVATION_TIMING     when the protective stop activates relative to confirmation and fill
```

### 7.2 Decision block

```text
DECISION_ID=NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION
SOURCE_STATUS=SOURCE_NOT_PINNED (concept pinned; pivot algorithm not pinned)
QUESTION=Which deterministic swing-low definition does the Holy Grail PRIMARY adopt for the
         protective stop reference?
OPTION_A=FRACTAL PIVOT: a bar whose low is lower than both its left and right neighbors
         (explicit N confirmation bars each side); availability = once the right-side
         confirmation is complete (point-in-time); SAME_BAR_AVAILABILITY=NO (needs future
         confirmation bars); stop activation after confirmation, with the same-bar
         fill/stop ambiguity resolved per GATE-05. Short side mirrors with swing high.
OPTION_B=LEG/ZIGZAG PIVOT: a swing low confirmed by a subsequent move up by an explicit
         threshold (e.g. R-multiple or ATR); availability after threshold confirmation;
         SAME_BAR_AVAILABILITY=NO.
OPTION_C=ROLLING-MINIMUM over a fixed lookback window (lowest low of the trailing N bars);
         availability at the end of the window; SAME_BAR_AVAILABILITY=NO (window needs bars
         after the fill to be a post-fill "newly formed" low reference).
PROJECT_BRAIN_RECOMMENDATION=OPTION_A (fractal pivot) as the most standard, deterministic,
         reproducible option, with explicit left/right confirmation-bar counts and a
         fail-closed SAME_BAR_AVAILABILITY=NO (a newly formed swing low cannot be known on
         the same bar as the fill because it requires future confirmation bars).
RECOMMENDATION_REASON=FAIL_CLOSED + REPRODUCIBLE + MINIMUM_HIDDEN_DEGREES_OF_FREEDOM:
         fractal pivot is a well-defined, widely used, deterministic pivot with explicit
         confirmation semantics; it makes availability and stop-activation timing explicit
         and never claims same-bar availability. Not chosen by outcome.
OUTCOME_EFFECT=defines the protective-stop reference level and its availability/activation
         timing; directly determines the stop-loss path.
CAN_CODEX_IMPLEMENT_GENERIC_MACHINERY_BEFORE_DECISION=YES (generic, parameterized pivot
         detection can be built; the definition BINDING is this gate — Codex must NOT pick
         a pivot algorithm itself)
BLOCKS_HOLY_GRAIL_MACHINE_READY=YES
```

---

## 8. TRAILING_STOP_MACHINE_DEFINITION

### 8.1 Context

The source says only "Trail stops as profits grow" (M01 step 4). It does not give
a precise trailing algorithm. Therefore the trailing mechanics remain
`SOURCE_NOT_PINNED`. This gate is not decided by profitability.

### 8.2 Decision block

```text
DECISION_ID=TRAILING_STOP_MACHINE_DEFINITION
SOURCE_STATUS=SOURCE_NOT_PINNED (concept pinned; no precise algorithm)
QUESTION=Which deterministic trailing convention does the Holy Grail PRIMARY adopt, given
         the source gives no exact algorithm?
OPTION_A=NO_MACHINE_TRAILING_UNTIL_SOURCE_PINNED: do not machine-trail; the trailing
         component stays NOT machine-ready / optional until a source-pinned or
         Owner-adopted convention exists (fail-closed)
OPTION_B=explicit deterministic trailing convention: trail the protective stop below the
         most recent swing low (reusing the adopted swing-low definition from GATE above)
         as profits grow
OPTION_C=fixed-distance or ATR-based trailing
PROJECT_BRAIN_RECOMMENDATION=OPTION_A (NO_MACHINE_TRAILING_UNTIL_SOURCE_PINNED) as the
         fail-closed default for PRIMARY. If the Owner wants a deterministic trailing,
         OPTION_B (trail below the most recent swing low) is the most source-faithful and
         deterministic alternative because it reuses the swing-low concept already present
         in the source's protective-stop language.
RECOMMENDATION_REASON=FAIL_CLOSED + SOURCE_FAITHFUL + MINIMUM_HIDDEN_DEGREES_OF_FREEDOM:
         the source gives no algorithm, so the honest default is not to machine-trail until
         a convention is adopted; no profitability-based justification is used.
OUTCOME_EFFECT=defines the exit/trailing path for held positions; changes which bars close
         positions after entry.
CAN_CODEX_IMPLEMENT_GENERIC_MACHINERY_BEFORE_DECISION=YES (generic trailing-stop machinery
         can be parameterized; the convention BINDING is this gate)
BLOCKS_HOLY_GRAIL_MACHINE_READY=YES
```

---

## 9. EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION

### 9.1 Distinguish source 2004 later exit wording from the original core rule

The accepted Holy Grail source evidence does **not** contain a source claim
"exit on a push to new highs". The nearest source statements are:

```text
ORIGINAL CORE RULE (SR-V0-M01, 1997, step 4) : "Trail stops as profits grow."
   -> PRIMARY exit anchor for the Holy Grail core rules (trailing stop).
2004 LATER EXIT WORDING (SR-V0-M05, 2004)     : "By then you should be looking for a top."
   -> qualitative multi-timeframe top context after the 30/60/120 retracement sequence
      (PARTIALLY_PINNED). Not a deterministic exit.
NO-TRADE ENTRY-LOCATION RULE (SR-V0-M01)      : "Either buy new highs, or buy pullbacks."
   -> entry location, NOT an exit.
```

"Exit on a push to new highs" appears only in old F's interpretation draft as a
candidate exit (`EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION`, "long-side
first-retracement exit context"). It is **not** a source-pinned claim in the
accepted bundle. The 2004 wording ("looking for a top") is qualitative context,
not a PRIMARY exit rule.

### 9.2 Decision block

```text
DECISION_ID=EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION
SOURCE_STATUS=SOURCE_NOT_PINNED (not a source claim in the accepted bundle; 2004 wording is
         qualitative top context; original core exit is "trail as profits grow")
QUESTION=Is "exit on a push to new highs" a PRIMARY exit, an alternative variant, or an
         unfrozen optional exit?
OPTION_A=UNFROZEN OPTIONAL EXIT VARIANT: not part of PRIMARY; the PRIMARY exit stays the
         source-pinned "trail as profits grow" (with the trailing convention from GATE-08)
OPTION_B=ALTERNATIVE VARIANT: adopted as a labeled INFERRED alternative exit, non-PRIMARY
OPTION_C=PRIMARY EXIT: adopted as the PRIMARY exit (requires a non-outcome Owner
         justification the source does not provide)
PROJECT_BRAIN_RECOMMENDATION=OPTION_A (unfrozen optional exit variant). The 2004 "looking
         for a top" wording is qualitative and is NOT a source-pinned "exit on push to new
         highs" rule; the original core exit is "trail as profits grow". "Exit on push to
         new highs" is an old-F candidate, not a source claim, so it must not be promoted to
         PRIMARY without a non-outcome Owner justification.
RECOMMENDATION_REASON=SOURCE_FAITHFUL + FAIL_CLOSED: promoting an old-F candidate that the
         accepted source does not state to PRIMARY would be a source-unfaithful choice;
         keeping it as an unfrozen optional variant adds no hidden degrees of freedom to the
         PRIMARY loop.
OUTCOME_EFFECT=determines which exit path is the PRIMARY Holy Grail exit and whether the
         old-F "push to new highs" candidate participates as an alternative/optional exit.
CAN_CODEX_IMPLEMENT_GENERIC_MACHINERY_BEFORE_DECISION=YES (generic exit machinery can be
         parameterized; the PRIMARY/optional binding is this gate)
BLOCKS_HOLY_GRAIL_MACHINE_READY=YES
```

---

## 10. Recommendation-principle summary

Every decision above is a `PROPOSAL_ONLY_NOT_ADOPTED`. Each was justified only
by:

```text
FAIL_CLOSED
SOURCE_FAITHFUL
CAUSAL
REPRODUCIBLE
MINIMUM_HIDDEN_DEGREES_OF_FREEDOM
```

and **never** by PnL / Sharpe / trade count. `CAN_CODEX_IMPLEMENT_GENERIC_
MACHINERY_BEFORE_DECISION=YES` everywhere means Codex may build **parameterized**
generic machinery and port the draft while remaining NOT_MACHINE_READY; Codex
must not freeze any of these gates (per `FGH_CODEX_REBUILD_PREPARATION_V0_1.md`
and `CURRENT_STATE.md`).

---

## 11. Final Owner approval block (PROPOSAL ONLY — NOT adopted)

The Owner may copy the block below verbatim. It is **not** approved by this
document. Each line is prefixed `PROPOSAL_ONLY_NOT_ADOPTED` and records the
recommended option; the Owner must decide each line before any PRIMARY freeze.

```text
PROPOSAL_ONLY_NOT_ADOPTED=YES

# FGH semantic gates (recommended proposals only)
APPROVE_FGH_GATE_01=OPTION_B (prior-available EMA reference; close-based EMA on prior
  completed bars; touch=bar.low<=EMA_prior<=bar.high; price-input labeled INFERRED)
APPROVE_FGH_GATE_02=OPTION_B (ADX>30 and rising over an explicit lookback window,
  evaluated as initial context before the pullback; touch bar need not be rising;
  INFERRED slope window)
APPROVE_FGH_GATE_03=OPTION_A (documented standard conventions: SMA-seeded EMA, Wilder
  init, exact Decimal, single explicit 6dp ROUND_HALF_UP output quantization; ENGINEERING
  feature semantics)
APPROVE_FGH_GATE_04=OPTION_A (fail-closed AMBIGUOUS_INTRABAR_SEQUENCE for same-bar
  EMA-touch + entry-stop)
APPROVE_FGH_GATE_05=OPTION_A (completed-bar conservative + AMBIGUOUS_INTRABAR_SEQUENCE
  for same-bar fill/protective-stop; INTRABAR_ORDERING=NOT_OBSERVABLE_AT_1M; never
  presented as exchange-resting)
APPROVE_FGH_GATE_06=OPTION_A (BASE) as PRIMARY timeframe proposal (non-outcome
  justification; otherwise remains TIMEFRAME_PRIMARY=UNRESOLVED)

# Pre-existing Holy Grail machine-definition ambiguities (recommended proposals only)
APPROVE_SWING_LOW=OPTION_A (fractal pivot with explicit left/right confirmation bars;
  SAME_BAR_AVAILABILITY=NO; stop activation after confirmation, same-bar fill/stop per
  GATE-05; short side mirrors with swing high)
APPROVE_TRAILING_STOP=OPTION_A (NO_MACHINE_TRAILING_UNTIL_SOURCE_PINNED) [or OPTION_B:
  trail below the most recent swing low] — Owner must pick one
APPROVE_EXIT_NEW_HIGHS=OPTION_A (unfrozen optional exit variant; PRIMARY exit remains
  source-pinned "trail as profits grow")
```

Any line the Owner declines to set keeps that gate open and continues to block
Holy Grail `MACHINE_READY` / `PRIMARY` (see `BLOCKS_HOLY_GRAIL_MACHINE_READY=YES`
above). Nothing in this document freezes a decision; the Owner is the only
authority that may turn a proposal into an adoption.

---

## Appendix A — Source evidence anchors used (Holy Grail)

```text
M01 (1997 AIQ, SHORT_TERM_TRADING_STRATEGIES):
  step1 "The 14-period ADX must initially be greater than 30 and rising."
  step2 "Look for a retracement in price to the 20-period exponential moving average,
         usually accompanied by a turndown in ADX."
  step3 "When price touches the 20-period moving average, put a buy stop above the high
         of the previous bar."
  step4 "Once filled, enter a protective sell stop at the newly formed swing low.
         Trail stops as profits grow."
  no-trade: "Either buy new highs, or buy pullbacks."  stop process: "get out if the
         market fails to do what I thought it would do."  failure: Eaton Corp.
M02 (1993 S&C, THE_DISCERNING_TRADER):
  "I personally use a 20-period exponential moving average on all my markets."
  ADX no-trade/fade: ADX<20 declining avoid; ADX>32 rising do not fade.
M04 (2000 Active Trader, THE_RITUALS_OF_TRADING):
  "the minute the market gives back more than it should, you get out on the first
   reaction or pause"; "take at least half off at a price objective when continuation
   is uncertain."
M05 (2004 Active Trader, TRADERS_TOOLBOX):
  "...price first pulls back to the 20-bar EMA... then the same retracement will occur
   on the 30-minute chart, then the 60-minute chart, then the 120-minute time frame.
   By then you should be looking for a top. But each retracement has to be preceded by
   a 14-bar ADX reading above 30 on that time frame."
```

```text
SOURCE_STATUS_VERDICT=SOURCE_NOT_PINNED for: EMA price input, touch bar definition,
  ADX rising slope window, operating timeframe PRIMARY, swing-low pivot algorithm,
  trailing mechanics, "exit on push to new highs"
SOURCE_STATUS_PINNED for: ADX period 14, ADX threshold >30, ADX "rising" initial context,
  EMA type exponential, EMA period 20, entry trigger/order type, initial stop concept,
  post-entry invalidation concept
```
