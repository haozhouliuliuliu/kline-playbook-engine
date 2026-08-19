# RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1

> Version: 0.1
> Date: 2026-08-20
> Status: PLAYBOOK_CONTRACT_DRAFT / SOURCE_AND_INTERPRETATION_LAYERS / PRE_OUTCOME / NOT_MACHINE_READY
> Lane: F (HOLY_GRAIL_PLAYBOOK_CONTRACT_INTERPRETATION_FREEZE_ENGINEER)
> Family: `RASCHKE_HOLY_GRAIL_PULLBACK`
> Contract schema: `src/playbook_contract.py` (generic Playbook Contract core, Lane B, merged)
> Semantic completion authority: `docs/research/semantic_completion/RASCHKE_HOLY_GRAIL_SEMANTIC_COMPLETION_V0_1.md`
> Playbook handoff: `docs/research/semantic_completion/RASCHKE_HOLY_GRAIL_PLAYBOOK_HANDOFF_V0_1.md`
> SOURCE_ONLY session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json`
> Source bundle evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json`
> Interpretation freeze: `docs/evidence/RASCHKE_HOLY_GRAIL_INTERPRETATION_FREEZE_V0_1.md`
> Deterministic JSON: `docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.json`
> Builder: `tools/build_raschke_holy_grail_playbook_contract_draft.py`

```text
PRIMARY_FREEZE_READY=NO
AMBIGUOUS_STOP=YES
CONTRACT_MACHINE_READY=NO
CONTRACT_VALIDATION_BLOCKERS=UNRESOLVED_CRITICAL_AMBIGUITY,PRIMARY_MISSING,MACHINE_OPERATIONALIZATION_MISSING
SOURCE_CLAIMS_BOUND=27
PROJECT_INTERPRETATIONS=8
SOURCE_EXPLICIT_FIELDS=0
PROJECT_INFERRED_FIELDS=7
UNRESOLVED_CRITICAL_FIELDS=5
TIMEFRAME_PRIMARY=UNRESOLVED
PROJECT_INSTRUMENT_SCOPE=cu,al,ni,au,ag,rb
PROJECT_TRANSFER_STATUS=INFERRED
REAL_STRATEGY_IDENTITY_CREATED=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

---

## 1. Purpose and boundary

This is a **real pre-outcome Playbook Contract specification task**. It converts
the accepted Raschke Holy Grail source semantics into a real versioned Playbook
Contract **DRAFT** using the actual generic contract schema
(`src/playbook_contract.py`), preserving the mandatory three-layer separation:

```text
SOURCE CLAIM
!=
PROJECT INTERPRETATION
!=
MACHINE OPERATIONALIZATION
```

This draft is **NOT** a backtest, NOT outcome inspection, NOT parameter tuning,
NOT strategy mining, and NOT statistical inference. No candidate market
outcome data was used. No real `StrategyIdentity` is created. Nothing is
registered in any `StrategyCatalog`. No `ResearchFirewall` outcome access is
requested.

The purpose is also to decide whether the PROJECT INTERPRETATION layer is
sufficiently frozen to support later machine operationalization. The decision
is **PRIMARY_FREEZE_READY=NO / AMBIGUOUS_STOP=YES**, which is a successful
research result: the source pins the trading-loop skeleton, but five
machine-facing fields remain genuinely ambiguous and must not be resolved by
guessing or outcome selection.

## 2. Accepted source skeleton

```text
CONTEXT:
14-period ADX initially >30 and rising

SETUP:
retracement to 20-period EMA

ENTRY LONG:
when price touches EMA, buy stop above previous-bar high

ENTRY SHORT:
source says sells reversed

INITIAL RISK:
protective stop at newly formed swing low/high

MANAGEMENT:
trail stops as profits grow

SOURCE-SPECIFIC EXIT CONTEXT:
later official material states look to exit on a push to new highs
for the long-side first-retracement setup.

CURRENT-PROJECT INSTRUMENT TRANSFER:
INFERRED (cu,al,ni,au,ag,rb)
```

## 3. Source claim binding

The draft binds the **exact accepted Holy Grail SOURCE_ONLY claim records**
(`C-RAS-HG-SEM-001`..`027`, all 27) from
`HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json`. No invented
source claims. Each `SourceClaimRef` carries:

- claim ID (`C-RAS-HG-SEM-###`);
- source ID (`SR-V0-M01`/`M02`/`M03`/`M04`/`M05`);
- source anchor (exact section anchors, e.g.
  `SR-V0-M01:august1997:section:HOLY_GRAIL_RULES`);
- claim status (`EXPLICIT` / `INFERRED` / `UNKNOWN`).

Contract-level source identity:

```text
SOURCE_BUNDLE_IDENTITY=SB-RASCHKE-HOLY-GRAIL-SEMANTIC-V1
SOURCE_BUNDLE_HASH=7e6cd5cf02eefa7ba7483eeda9a036433e5a07320455c0594971fc2e37bf882c
SOURCE_ONLY_SESSION_IDENTITY=SOURCE_ONLY_RASCHKE_HOLY_GRAIL_SEMANTIC_V1_20260820
SESSION_IDENTITY_HASH=618d1e429d08dbdfacb629e64b9b33c64957307ec341d8544cbcac464f08c376
RESEARCH_LINEAGE_ID=L-RAS-HOLYGRAIL
SOURCE_SCOPE=US_EQUITIES_AND_US_INDEX
```

## 4. Project interpretation layer (predeclared, versioned)

Eight `InterpretationBranch` objects are predeclared. **None** is selected as
PRIMARY (a PRIMARY cannot be source-justified while critical ambiguity
remains). Seven are clearly labeled `PROJECT_INFERRED_PREDECLARED` project
conventions; one (`INT-LONG-SHORT-MIRROR`) is the source-explicit mirror
concept with machine details that inherit unresolved fields.

| branch_id | interpretation | transfer | label |
|---|---|---|---|
| `INT-EMA-PRICE-INPUT-CLOSE` | EMA price input = close (source silent) | INFERRED | PROJECT_INFERRED_PREDECLARED |
| `INT-EMA-TOUCH-INTRABAR` | touch = `bar.low <= EMA <= bar.high` | INFERRED | PROJECT_INFERRED_PREDECLARED |
| `INT-ADX-RISING-1BAR` | rising = `ADX[current] > ADX[previous]` at context bar | INFERRED | PROJECT_INFERRED_PREDECLARED |
| `INT-ENTRY-OFFSET-1TICK` | entry = one tick above previous-bar high (tick metadata) | INFERRED | PROJECT_INFERRED_PREDECLARED |
| `INT-STOP-ACTIVATION-AFTER-FILL` | protective stop active from first eligible future bar after fill | INFERRED | PROJECT_INFERRED_PREDECLARED |
| `INT-SESSION-OFFICIAL-TRADING-DAY` | session boundary = official trading-day via SessionMetadata | INFERRED | PROJECT_INFERRED_PREDECLARED |
| `INT-INSTRUMENT-SCOPE-6PRODUCTS` | cu,al,ni,au,ag,rb fixed predeclared research scope | INFERRED | PROJECT_INFERRED_PREDECLARED |
| `INT-LONG-SHORT-MIRROR` | sells reversed (source-explicit mirror concept) | EXPLICIT | SOURCE_EXPLICIT (machine details inherit unresolved swing-high) |

These conventions are predeclared **before** any outcome access and are NOT
tuned on outcomes.

## 5. Observation surfaces

| surface_id | required | observability | missing inputs |
|---|---|---|---|
| `ADX_14_OHLC_DERIVED` | yes | OBSERVABLE_NOW | — |
| `EMA_20_PRICE_DERIVED` | yes | OBSERVABLE_NOW | — |
| `BAR_HIGH_LOW_ENTRY_STOP` | yes | OBSERVABLE_NOW | — |
| `PRICE_POSITION_RANGE_MOMENTUM_HIGHS` | yes | OBSERVABLE_NOW | range_boundary_inferred |
| `TIMEFRAME_30_60_120_DERIVABLE` | yes | OBSERVABLE_NOW | operating_timeframe_unresolved |
| `NYSE_TICK_BREADTH` | no | NOT_OBSERVABLE_WITH_CURRENT_DATA | NYSE_BREADTH, NYSE_TICK |

NYSE TICK/breadth is NOT part of the source-pinned 4-step Holy Grail rules; it
is recorded as unavailable context and not proxied. It is a non-required
surface, so it does not block readiness.

## 6. Unresolved critical ambiguity (AMBIGUOUS_STOP)

`ambiguity_status=UNRESOLVED_CRITICAL`. Five machine-facing fields have
multiple materially different equally-plausible interpretations that cannot be
justified from source/documentary evidence alone:

1. `NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION` — source pins the protective-stop
   reference concept ("newly formed swing low") but no software pivot algorithm;
   fractal/leg/zigzag pivot definitions remain equally plausible.
2. `NEWLY_FORMED_SWING_HIGH_MACHINE_DEFINITION` — mirror of the above.
3. `TRAILING_STOP_MACHINE_DEFINITION` — "trail stops as profits grow";
   swing/MA/distance-based trail mechanics equally plausible.
4. `EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION` — "look to exit on a push to
   new highs"; reference level and confirmation semantics not pinned.
5. `OPERATING_TIMEFRAME` — source explicitly multi-timeframe (base chart then
   30/60/120-minute); no single operating timeframe is source-justified and it
   is not hidden behind a tunable parameter. `TIMEFRAME_PRIMARY=UNRESOLVED`.

Preserved alternatives and the per-field classification are in
`docs/evidence/RASCHKE_HOLY_GRAIL_INTERPRETATION_FREEZE_V0_1.md`.

## 7. Contract validation (real `validate_contract`)

The real `validate_contract(...)` from `src/playbook_contract.py` returns:

```text
MACHINE_READINESS=NOT_MACHINE_READY
BLOCKERS=UNRESOLVED_CRITICAL_AMBIGUITY,PRIMARY_MISSING,MACHINE_OPERATIONALIZATION_MISSING
```

- `UNRESOLVED_CRITICAL_AMBIGUITY` — materially different from a hidden
  ambiguity; it is front-and-center because `PRIMARY_FREEZE_READY=NO`.
- `PRIMARY_MISSING` — a PRIMARY is required for machine readiness, but none can
  be source-justified while critical ambiguity remains.
- `MACHINE_OPERATIONALIZATION_MISSING` — `machine=None` intentionally; Lane G/H
  machine dependencies are not merged. This is an expected, acceptable blocker
  at this stage.

`CONTRACT_MACHINE_READY=NO` is the honest state. The contract is a real
SOURCE + INTERPRETATION representation, not a machine-ready strategy.

## 8. Instrument / timeframe / transfer scope

```text
INSTRUMENT_SCOPE=cu,al,ni,au,ag,rb
TIMEFRAME_SCOPE=BASE,30MIN,60MIN,120MIN (source-permitted multi-timeframe set)
PROJECT_TRANSFER_STATUS=INFERRED
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
CURRENT_PROJECT_PRODUCT_TRANSFER=INFERRED_PROJECT_TRANSFER
```

All six products are predeclared as the fixed project research scope **before**
any outcome access. This is not presented as Raschke's explicit instrument
scope.

## 9. Final decision

```text
PRIMARY_FREEZE_READY=NO
AMBIGUOUS_STOP=YES
CONTRACT_MACHINE_READY=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

`NO` is a successful result. The source + interpretation contract is real and
deterministic (`contract_identity=ed4af2cbff73a3eaf0420f003b7f4ef9b37f1dfd2d6d247195c1b2cc1c5619d0`),
but the PROJECT INTERPRETATION layer is not yet frozen enough for machine
operationalization because the swing-low/high machine definitions, the trailing
machine definition, the exit-on-push-to-new-highs machine definition, and the
operating timeframe remain critical unresolved ambiguity.
