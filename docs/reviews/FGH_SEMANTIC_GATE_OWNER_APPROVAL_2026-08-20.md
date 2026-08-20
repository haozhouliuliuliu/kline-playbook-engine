# FGH_SEMANTIC_GATE_OWNER_APPROVAL_2026-08-20

> Date: 2026-08-20
> Status: OWNER_APPROVED_BINDING
> Proposal authority: `docs/reviews/FGH_SEMANTIC_GATE_OWNER_DECISION_PROPOSAL_V0_1.md`
> Decision basis: Owner explicitly pre-authorized the project brain to continue through the repair-complete node without pausing for additional individual approvals; the project brain therefore applies the proposal's stated safe recommendations as the binding project choices below.
> Outcome basis: NO candidate outcome / PnL / Sharpe / trade-count evidence was used to choose any option.

These decisions freeze only the named machine/research semantics. They do not authorize candidate outcome access, Validation, historical final holdout, Shadow/Forward, real-money trading, broker access, paid data, or source-policy bypass.

```text
APPROVE_FGH_GATE_01=OPTION_B
APPROVE_FGH_GATE_02=OPTION_B
APPROVE_FGH_GATE_03=OPTION_A
APPROVE_FGH_GATE_04=OPTION_A
APPROVE_FGH_GATE_05=OPTION_A
APPROVE_FGH_GATE_06=OPTION_A_BASE
APPROVE_SWING_LOW=OPTION_A
APPROVE_TRAILING_STOP=OPTION_A_NO_MACHINE_TRAILING_UNTIL_SOURCE_PINNED
APPROVE_EXIT_NEW_HIGHS=OPTION_A_OPTIONAL_VARIANT_NOT_PRIMARY
```

## FGH-GATE-01 — EMA touch

Use a prior-available EMA reference. The EMA price basis is the standard close-based EMA, explicitly labeled a project `INFERRED` machine convention rather than a source claim. A bar may test `low <= EMA_prior <= high` only against an EMA value already available from prior completed bars. Current-bar close must not be used to judge the same bar's touch.

```text
EMA_PRICE_BASIS=PROJECT_INFERRED_CLOSE
EMA_REFERENCE=PRIOR_COMPLETED_BAR_AVAILABLE
TOUCH_RULE=BAR_LOW_LE_EMA_PRIOR_LE_BAR_HIGH
CURRENT_BAR_CLOSE_LOOKAHEAD=FORBIDDEN
```

## FGH-GATE-02 — ADX rising sequence

ADX `>30 and rising` is an initial/context condition before the pullback. The touch bar does not need to remain rising. The machine must use an explicit deterministic lookback/window for the rising test, labeled `INFERRED`; the old rule `ADX[t] > ADX[t-1]` on the touch bar is not source authority.

```text
ADX_CONTEXT=INITIAL_PRE_PULLBACK
TOUCH_BAR_RISING_REQUIRED=NO
ADX_RISING_WINDOW=EXPLICIT_VERSIONED_INFERRED
OLD_TOUCH_BAR_ONE_STEP_RULE=NOT_AUTHORITY
```

## FGH-GATE-03 — EMA/ADX numeric convention

Adopt the proposal's documented standard engineering convention: SMA-seeded EMA; Wilder ADX initialization; Decimal arithmetic; explicit 6-decimal `ROUND_HALF_UP` quantization policy. This is an ENGINEERING machine convention, not a source fact. The exact numeric policy must be versioned and identity-bound.

```text
EMA_SEED=SMA
ADX_INITIALIZATION=WILDER_SMA_DX
ARITHMETIC=DECIMAL
QUANTIZATION=6DP_ROUND_HALF_UP
NUMERIC_POLICY=VERSIONED_IDENTITY_BOUND
```

## FGH-GATE-04 — same-bar touch -> entry

At 1-minute resolution, if EMA touch and the entry-stop threshold are both reached inside the same bar and their ordering is not observable, fail closed as `AMBIGUOUS_INTRABAR_SEQUENCE`. Do not invent an order and do not silently defer in a way that changes the source event without an explicit future version.

```text
SAME_BAR_TOUCH_ENTRY=AMBIGUOUS_INTRABAR_SEQUENCE
FAIL_CLOSED=YES
```

## FGH-GATE-05 — fill -> protective stop / chronology

Use the completed-bar conservative chronology model. It must never be described as exchange-resting intrabar chronology. If entry fill and protective-stop interaction occur in the same 1-minute bar and ordering is not observable, preserve `AMBIGUOUS_INTRABAR_SEQUENCE`. The old next-bar-only protective-stop activation convention is not adopted because it silently erases same-bar risk.

```text
CHRONOLOGY=COMPLETED_BAR_AVAILABILITY_CONSERVATIVE
EXCHANGE_RESTING_CLAIM=NO
SAME_BAR_FILL_STOP=AMBIGUOUS_INTRABAR_SEQUENCE
NEXT_BAR_ONLY_STOP_ACTIVATION_DEFAULT=REJECTED
INTRABAR_ORDERING=NOT_OBSERVABLE_AT_1M
```

## FGH-GATE-06 — operating timeframe

Adopt the source's base chart as the PRIMARY timeframe branch for the first machine interpretation. This is a non-outcome project choice made to minimize extra transfer assumptions. It does not make 30/60/120-minute source variants disappear; they remain source-supported alternatives/variants. Mapping `BASE` to a concrete machine interval remains a separate operationalization fact and must be explicit before `MACHINE_READY`.

```text
PRIMARY_TIMEFRAME_BRANCH=BASE
SOURCE_ALTERNATIVES=30MIN,60MIN,120MIN
BASE_TO_MACHINE_INTERVAL=EXPLICIT_BEFORE_MACHINE_READY
```

## Newly formed swing low/high

Adopt a deterministic fractal/pivot definition with explicit left/right confirmation bars. A swing is not available until its required right-side confirmation has completed. Same-bar availability is forbidden. The short side mirrors the rule with swing high. Exact confirmation counts remain explicit versioned machine parameters; they must not be chosen by outcome.

```text
SWING_DEFINITION=FRACTAL_PIVOT_EXPLICIT_CONFIRMATION
SAME_BAR_AVAILABILITY=NO
RIGHT_SIDE_CONFIRMATION_REQUIRED=YES
SHORT_SIDE=MIRROR_SWING_HIGH
CONFIRMATION_COUNTS=EXPLICIT_VERSIONED_NON_OUTCOME
```

## Trailing stop

Do not invent a trailing algorithm while the source only says to trail stops as profits grow. No Holy Grail PRIMARY machine trailing rule is adopted yet. This is an explicit research prerequisite, not a repair defect and not permission to backtest alternative trailing rules.

```text
TRAILING_STOP_MACHINE_DEFINITION=NOT_ADOPTED_UNTIL_SOURCE_PINNED_OR_NEW_OWNER_DECISION
MACHINE_READY_BLOCKER=PRESERVE
OUTCOME_TUNING_FOR_TRAILING=FORBIDDEN
```

## Exit on push to new highs

Treat the later source wording about exit on a push to new highs as an optional versioned exit variant, not the Holy Grail PRIMARY exit. It cannot rescue or modify the PRIMARY after seeing outcomes.

```text
EXIT_ON_PUSH_TO_NEW_HIGHS=OPTIONAL_VARIANT
PRIMARY_EXIT_REPLACED=NO
OUTCOME_RESCUE=FORBIDDEN
```

## Authorization boundary

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
PAID_SOURCE=NOT_AUTHORIZED
```

Any later change to these frozen semantics requires a new explicit Owner decision and a new versioned project artifact. The remaining `TRAILING_STOP_MACHINE_DEFINITION` prerequisite intentionally keeps the Holy Grail PRIMARY `NOT_MACHINE_READY` until source evidence or a new Owner decision supplies a deterministic rule.