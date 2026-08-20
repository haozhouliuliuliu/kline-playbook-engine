# FGH Closure Correction Spec V0.1

> Date: 2026-08-20  
> Role: project-brain bounded engineering authority  
> Status: READY_FOR_SINGLE_CODEX_EXECUTION

## 1. Context

The deterministic F/G/H rebuild is integrated, but Retrospective 1 found one remaining normal-caller completeness-laundering gap in `src/technical_features.py`.

`AggregationResult` uses `@dataclass(frozen=True, init=False)`, but the class still exposes `AggregationResult._from_aggregation(...)`. A normal Python caller can call that classmethod directly, omit genuine `incomplete_buckets`, provide only the surviving aggregate bucket identities as `expected_bucket_identities`, and obtain a structurally valid result that `compute_ema` / `compute_adx` treat as complete.

This violates L-12's intended invariant: unresolved gap evidence must not be discardable before feature computation.

This is analogous in shape to the earlier Package-B caller-construction problem: a private-named constructor is still a callable API in Python.

## 2. Required bounded correction

Close normal-caller laundering without creating a framework, database, durable state, cryptographic service, or OS-sandbox claim.

Preferred minimum design:

- Keep `AggregationResult` non-publicly constructible via its normal dataclass constructor.
- `TimeframeAggregator.aggregate()` remains the sole normal producer accepted by feature computation.
- Feature computation must reject an `AggregationResult` created directly through `_from_aggregation(...)` or equivalent manual construction, even if the caller removed all incomplete buckets and made the remaining identity set internally consistent.
- A small process-local issued-object guard is acceptable. It must be explicit that this closes normal construction/API misuse only; it does not claim protection against a caller that deliberately mutates module-private Python state or process memory.
- Do not create persistent issued state.
- Do not introduce a new feature framework.

If Codex finds a smaller, cleaner implementation with the same bounded guarantee, it may use it, but it must not weaken the invariant or overclaim tamper-proofing.

## 3. Mandatory regressions

At minimum:

1. Build a genuine incomplete `AggregationResult` with the authoritative `TimeframeAggregator`.
2. Directly call the currently exposed `_from_aggregation(...)` (or whatever manual path remains after the implementation) to construct a forged clean envelope from only the surviving complete aggregates.
3. `compute_ema(...)` on the forged object must fail closed before feature computation.
4. Equivalent `compute_adx(...)` must also fail closed through the shared feature-input validator.
5. A genuine complete result issued by `TimeframeAggregator.aggregate()` must still compute.
6. A genuine incomplete result issued by the aggregator must still fail for unresolved continuity.
7. Existing future-bar append identity stability and feature implementation byte-binding tests must remain green.

## 4. Scope

Expected production file:

- `src/technical_features.py`

Expected tests:

- `tests/test_fgh_closure_guardrails.py` or equivalent small focused test file
- existing `tests/test_technical_features.py` only if a shared fixture must be reused/updated

Evidence:

- `docs/evidence/FGH_CLOSURE_GUARDRAILS_V0_1.md`

Do not modify unrelated foundation modules unless a concrete failing regression proves it necessary.

## 5. Required validation

Run:

```text
python -m unittest tests.test_technical_features tests.test_fgh_closure_guardrails tests.test_fgh_combined_causal_integration tests.test_stop_order_execution -v
python -m unittest discover -s tests -v
python -m compileall -q src tools tests
git diff --check
```

No candidate market outcome may be accessed.

## 6. Explicit non-goals

Do not:

- make Holy Grail `MACHINE_READY`;
- change FGH semantic Owner decisions;
- change E-06 or E-07 prerequisites;
- modify the frozen research protocol or 12/6/6 chronology;
- authorize candidate outcomes;
- add GitHub Actions/workflows;
- adopt a new tool/framework.

## 7. Closure authority

Codex completion is not project acceptance. Project brain will independently inspect the branch, perform Retrospective 2, map the original second-pass findings, and issue the final repair-closure decision.

```text
TOOL_DECISION=USE_EXISTING
NEW_TOOL_ADOPTION=NO
TEMPORARY_GITHUB_ACTIONS_APPROACH=ABANDONED_NOT_ADOPTED
CANDIDATE_OUTCOME_DATA_USED=NO
```
