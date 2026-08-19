# PARALLEL_WORK_PACKAGE_2026-08-20_V0_3_ADVERSARIAL_AUDIT

> Date: 2026-08-20
> Status: FORMAL PROJECT-BRAIN ADVERSARIAL AUDIT
> Scope: Lane F / Lane G / Lane H from baseline `64771245acf5e445adc59eb5ef71afcb0ef00777`
> Outcome data: NOT USED

## Executive verdict

The three-lane package produced useful work, but none of F/G/H should be integrated into `main` unchanged.

```text
LANE_F=RESEARCH_RESULT_VALID_DIRECTION / REVISION_REQUIRED_BEFORE_FREEZE_AUTHORITY
LANE_G=INTEGRATION_BLOCKED_CORRECTIONS_REQUIRED
LANE_H=INTEGRATION_BLOCKED_CORRECTIONS_REQUIRED
COMBINED_F_G_H_REGRESSION=NOT_YET_RUN
CANDIDATE_OUTCOME_ACCESS=NOT_AUTHORIZED
```

This is not a rollback of the parallel-execution strategy. The audit found defects precisely because independent lanes were reviewed together before integration.

## Lane F — Holy Grail Playbook Contract draft

Worker branch/commit:

```text
parallel/holy-grail-playbook-contract-draft-v01
9fe53a2104e78e51f09f56c3bc73d2f6c930e536
```

Accepted:
- real `PlaybookContract` schema is reused;
- 27 accepted SOURCE_ONLY claims are bound;
- `PRIMARY_FREEZE_READY=NO` and `AMBIGUOUS_STOP=YES` are honest outcomes;
- no StrategyIdentity / catalog registration / outcome access occurred.

Correction required before the interpretation-freeze artifact can become authority:

### F-1 Causal EMA-touch semantics are not resolved

The draft predeclares `bar.low <= EMA <= bar.high`, but does not pin which point-in-time EMA value is being compared to the same bar. A close-based EMA computed using the current bar close is not available during that bar. Using it to decide whether the same bar touched the EMA would introduce look-ahead.

Required correction: explicitly distinguish a prior-available EMA reference, a continuously-updated/intrabar model (if separately defined and justified), or keep the field critical/unresolved. No candidate outcome may choose among them.

### F-2 Protective-stop activation cannot silently discard same-bar risk

The draft predeclares the protective stop as active only from the first eligible future bar after entry fill. The source says protection is entered once filled, while Lane H intentionally models same-bar activation/trigger sequence as potentially ambiguous at 1-minute resolution. The interpretation layer may not silently exclude same-bar post-fill stop risk merely for convenience.

Required correction: align with the generic stop-trigger chronology. Where the 1-minute bar cannot determine post-fill ordering, preserve `AMBIGUOUS_INTRABAR_SEQUENCE` or another explicit fail-closed semantic rather than assuming no same-bar stop exposure.

Other already-recognized critical ambiguity remains:
- swing-low/high software definition;
- trailing-stop mechanics;
- exit-on-new-highs mechanics;
- operating timeframe.

Therefore PRIMARY remains not frozen.

## Lane G — PIT timeframe aggregation / EMA / Wilder ADX

Worker branch/commit:

```text
parallel/pit-feature-timeframe-core-v01
ae16f7cd0b38aadc783bd8957c7b03a7ac123d37
```

Direction accepted, but integration is blocked by correctness/provenance defects.

### G-1 Daily aggregation does not fail closed on missing constituent minutes

`_aggregate_daily()` aggregates whatever bars were supplied for an official trading day. It does not prove that all expected 1-minute starts from all published session windows are present. A partially missing day can therefore become an apparently complete daily bar.

Required: daily aggregation must verify the complete expected constituent set or explicitly return an incomplete result; never emit a complete daily bar from a partial day.

### G-2 Entirely absent session windows and invalid interval/base relationships are not adequately guarded

Intraday aggregation iterates only session windows that have at least one supplied bar. A completely missing session window can disappear without an incomplete-window record. Also arbitrary interval seconds are accepted without proving that the requested interval is representable as an exact integer number of base bars; e.g. a non-multiple of the 60-second base can leave uncovered time while still appearing complete.

Required:
- derive/iterate the authoritative windows for represented official trading days, including zero-bar windows where relevant;
- require a supported exact base-interval relationship or explicitly reject unsupported aggregation specs;
- validate each constituent bar duration against the declared base interval.

### G-3 Feature identities do not bind the complete dependency provenance

EMA/ADX values depend on historical prefixes, but the current feature identity binds only the current aggregate identity plus the resulting value. If upstream evidence changes while the final numeric value happens to remain equal, the feature identity can remain unchanged.

Required: bind an explicit dependency-chain/prefix identity (or prior feature identity chain) so any material source-evidence change changes the feature identity even when the numeric output coincidentally does not.

### G-4 Feature computation can silently ignore reported incomplete buckets

`compute_ema()` / `compute_adx()` accept arbitrary `AggregatedBar` iterables. A caller can pass only the complete aggregates from an `AggregationResult` that also contains incomplete buckets, causing the feature series to compress over missing data.

Required: provide/require continuity/completeness evidence for feature computation and fail closed when the dependency history contains unresolved missing aggregate buckets.

Wilder formulas themselves appear structurally consistent with the documented standard engineering convention; the main blockers are aggregation completeness, causality/provenance, and continuity.

## Lane H — generic stop-trigger observation layer

Worker branch/commit:

```text
parallel/stop-trigger-observation-v01
8244935ed3be32394910a6fb745017b31e194b6a
```

Direction accepted, but integration is blocked by one definite iterable bug and evidence-provenance hardening.

### H-1 Generator-consumption bug in group evaluation

`evaluate_stop_group()` passes the same `bars` iterable independently into `evaluate_stop_order()` for each order. If `bars` is a one-shot generator, the first order consumes it and later orders evaluate an empty sequence.

Required: materialize/validate the ordered bar sequence exactly once at group entry and reuse the immutable tuple for all member orders. Add a generator regression test.

### H-2 Trigger-result identity does not bind source-bar / evaluated-sequence evidence strongly enough

`StopTriggerResult.identity_id` records timestamps, prices and trigger fields but not the normalized source-bar identity. Different underlying OHLC evidence can therefore produce the same trigger identity when the reference result happens to match. `NOT_TRIGGERED` evidence is even more dependent on the evaluated sequence.

Required: bind the exact triggering bar identity for triggered/ambiguous results and a deterministic evaluated-sequence/dependency identity for non-triggered/group results.

### H-3 OCO cancellation is deliberately not implemented

This is not a defect against Lane H's narrow prompt, but it is an integration limitation. `evaluate_stop_group()` detects same-bar ambiguity; it does not cancel later opposing stops after an earlier unambiguous OCO trigger. Therefore this module must not yet be represented as a complete OCO/bracket lifecycle executor.

The existing same-bar activation rule is conservative and can remain a versioned engineering assumption after explicit integration review; it must be reconciled with Lane F's protective-stop activation interpretation.

## Cross-lane integration findings

### X-1 No combined regression exists yet

Lane F reports 303 tests, Lane G 338, Lane H 330, but each branch was tested independently from the same baseline. There is no single branch containing corrected F+G+H with one full regression run.

Required before main integration:
1. correct G and H in their own lanes;
2. revise F's causal interpretation artifact;
3. merge all corrected heads into one isolated integration worktree;
4. run full combined tests and `git diff --check`;
5. only then integrate reviewed artifacts/code to main.

### X-2 F/G EMA chronology must be one semantic chain

The Playbook interpretation must state exactly which PIT EMA value is observable at each decision/trigger point, and Lane G must provide that exact causal feature. The research layer may not refer vaguely to an EMA while the machine layer chooses a different timing convention.

### X-3 F/H protective-stop chronology must be one semantic chain

Lane F may not assume away a same-bar post-entry protective-stop event if Lane H's minimum-resolution evidence cannot determine ordering. The contract must either encode the fail-closed ambiguity or provide separately justified finer chronology.

## Parallelism verdict

```text
PARALLEL_EXECUTION_STRATEGY=KEEP
MAX_ACTIVE_LANES=3
MAIN=SOLE_INTEGRATION_LANE
MANDATORY_POST_PARALLEL_ADVERSARIAL_AUDIT=YES
MANDATORY_COMBINED_REGRESSION_BEFORE_MAIN=YES
```

The error pattern does not justify returning to serial execution. The optimization is to keep independent construction parallel while making cross-lane adversarial audit and a combined integration regression mandatory before acceptance.

## Progress estimate (planning estimate, not acceptance evidence)

Using accepted `main` capabilities only, the project is approximately:

```text
FULL_PROJECT_ENGINEERING_PROGRESS_ESTIMATE=~63_PERCENT
PRE_OUTCOME_RESEARCH_AND_VALIDATION_FOUNDATION=~75_PERCENT
```

Raw F/G/H implementation would move apparent implementation volume higher, but unaccepted branches with known correctness defects are not counted as completed engineering.

The full-project estimate remains materially lower than the pre-outcome-foundation estimate because major live Trading Loop / RiskGate / OMS / broker adapter / reconciliation / safety / owner-facing observability work is still largely unimplemented, and no real Playbook has yet reached a frozen machine-ready StrategyIdentity.

## Authorization state

```text
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
OWNER_ACTION=NONE
```
