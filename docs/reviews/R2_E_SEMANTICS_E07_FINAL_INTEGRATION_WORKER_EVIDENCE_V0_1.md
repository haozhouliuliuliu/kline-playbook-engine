# R2_E_SEMANTICS_E07_FINAL_INTEGRATION_WORKER_EVIDENCE_V0_1

> Task: `R2_E_SEMANTICS_E07_FINAL_INTEGRATION_V0_1`
> Role: integration + regression ONLY. NOT a re-implementation of E-04/E-05/E-08, NOT a re-research of E-07.
> Date: 2026-08-20
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Branch: `integration/r2-e-semantics-e07-final-v01`
> Base authority: `docs/reviews/R2_FOUR_LANE_EXECUTION_PLAN_V0_1.md`, `docs/reviews/PACKAGE_E_OWNER_DECISION_APPROVAL_2026-08-20.md`, `CURRENT_STATE.md`

## 1. Baseline

Created strictly from the latest `origin/main` after `git fetch origin`. No old-main SHA was guessed.

```text
BASELINE=origin/main
BASELINE_SHA=e0cf182475fb9c39bd2b40447e49cba9909ae4cb
```

The latest `main` already includes R2 foundation (A/B/C/D/F, E-Core, E-10, E-06 assessment, F/G/H preparation authority).

## 2. Source branch tips (fetched origin)

```text
SOURCE_1=origin/repair/package-e-owner-approved-semantics-v01
SOURCE_1_SHA=17c7c232e881c04745a479b3022c06d6e1c1b5d2
SOURCE_2=origin/research/e07-tqsdk-main-mapping-provenance-v01
SOURCE_2_SHA=b72a0634b69e5d01b998cf703eaeeb155fec3469
```

## 3. Merge order (strict no-ff; no rebase, no squash, no force-push)

Merge 1 first, then Merge 2:

```text
MERGE_1=git merge --no-ff origin/repair/package-e-owner-approved-semantics-v01
MERGE_1_COMMIT=d8dd581
MERGE_2=git merge --no-ff origin/research/e07-tqsdk-main-mapping-provenance-v01
MERGE_2_COMMIT=cf45b82
HEAD=cf45b82
```

## 4. Conflicts

None. Both merges completed cleanly via the `ort` strategy. No conflict resolution was required. No merge markers remain.

```text
CONFLICTS=0
MERGE_MARKERS=0
AUTHORITY_FILES_UNCHANGED=YES
```

`CURRENT_STATE.md`, `00_READ_FIRST.md`, and frozen research protocol files were verified unchanged versus `origin/main` (authority preserved; no stale-branch state restored).

## 5. E-04 / E-05 / E-08 / E-07 preservation (Owner authority)

Owner authority enforced in the merged tree, verified in source:

- **E-04** `OPTION_C_EXPLICIT_BUCKET_CHILD_ORDERS`: `src/validation_runner.py` resolves a generic `CLOSE` to `CLOSE_TODAY` only when the today bucket alone satisfies quantity, and to `CLOSE_PREVIOUS` only when the previous bucket alone satisfies it; otherwise fails closed with `GENERIC_CLOSE_REQUIRES_EXPLICIT_BUCKET_CHILD_ORDERS`. No today-first/previous-first/proportional auto split and no hidden child-order creation.
- **E-05** `PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS`: `PortfolioCapitalBinding` binds `strategy_identity_id`, `concrete_contract_id`, `capital_assumptions`. `PortfolioRequest` carries `capital_bindings` (no single global `capital_assumptions`). Each candidate resolves its concrete contract first, then the unique `(strategy, concrete contract)` binding; resolved `ContractSpecification.contract_multiplier` must equal the binding `capital_assumptions.contract_multiplier`. No global fallback.
- **E-08** `AVAILABLE_CAPITAL_ONLY`: `CapitalMarginAssumptions.margin_admission_resource = "AVAILABLE_CAPITAL_ONLY"` and it is bound into `identity_id`. Open/add admission uses `current.available_capital`; not `available_resources`, `equity`, or positive floating PnL.
- **E-07**: evidence only. `docs/evidence/E07_TQSDK_HISTORICAL_MAIN_MAPPING_AVAILABILITY_V0_1.md` merged. No login, no account creation, no Owner-account use, no OI/volume substitute, no self-written `KQ.m@` rule, no pseudo-main price bars, and no runtime mapping implementation.

```text
E04_STATUS=PRESERVED
E05_STATUS=PRESERVED
E08_STATUS=PRESERVED
E07_STATUS=FAIL_CLOSED_PRESERVED
E07_COMPLETE_MAPPING=NO
E07_FAIL_CLOSED=YES
PORTFOLIO_CANDIDATE_PATH=STILL_CLOSED
```

The portfolio candidate-outcome path remains fail-closed at `PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED` even though the E-05 portfolio representation is structurally correct.

## 6. Combined regression

Focused modules all green, then full suite:

```text
FOCUSED=tests.test_validation_runner tests.test_contract_execution_semantics tests.test_capital_margin_constraints tests.test_portfolio_semantics tests.test_round_trip_ledger tests.test_r1_cdf_ecore_integration tests.test_cdf_combined_integration tests.test_research_firewall
FOCUSED_RESULT=OK

FULL=python -m unittest discover -s tests -v
FULL_TESTS=489
FULL_RESULT=OK
BASELINE_478_SUITE_NOT_DEGRADED=YES
```

489 = R2 foundation baseline 478 + 11 new E-04/E-05/E-08 tests.

Specific Owner-authority regressions verified green by name:

```text
E04_generic_close_across_buckets_fails_closed_and_explicit_bucket_orders_flat=OK
E05_heterogeneous_multiplier_bindings_resolve_structurally=OK
E05_outcome_path_remains_closed=OK
E08_positive_unrealized_pnl_cannot_finance_new_admission=OK
E08_negative_unrealized_pnl_does_not_reduce_admission_capacity=OK
```

Cross-cutting regressions (R2 foundation, E-10 RoundTrip SessionMetadata binding, ResearchFirewall candidate restrictions) covered by the full 489-suite pass.

## 7. Static checks

```text
COMPILEALL=python -m compileall -q src tools tests
COMPILEALL_RESULT=OK
DIFF_CHECK=git diff --check
DIFF_CHECK_RESULT=CLEAN
MERGE_MARKER_GREP=git grep -n "^<<<<<<<\|^=======\|^>>>>>>>"
MERGE_MARKER_GREP_RESULT=NONE
```

## 8. E-07 final state

```text
TQSDK_HISTORY_ACCESS=LOGIN_REQUIRED
E07_MAPPING_COMPLETENESS=INCOMPLETE
E07_RUNTIME_MAPPING_STATUS=FAIL_CLOSED_PREREQUISITE
E07_COMPLETE_MAPPING=NO
E07_FAIL_CLOSED=YES
```

This integration merges the E-07 availability evidence only. It does not implement runtime mapping and does not announce `main` accepted.

## 9. Push

```text
PUSHED=integration/r2-e-semantics-e07-final-v01
MAIN_PUSHED=NO
```

This branch is offered for review. `main` was not pushed by this lane.
