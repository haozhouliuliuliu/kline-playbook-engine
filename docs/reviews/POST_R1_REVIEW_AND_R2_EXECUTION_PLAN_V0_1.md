# POST_R1_REVIEW_AND_R2_EXECUTION_PLAN_V0_1

> Date: 2026-08-20
> Role: project-brain R1 acceptance / R2 orchestration authority
> Candidate outcome access: NOT_AUTHORIZED

## R1 review verdict

```text
R1_CDF_ECORE_E10_BRANCH=integration/r1-cdf-ecore-e10-v01
R1_PROJECT_BRAIN_REVIEW=PASS_READY_FOR_FINAL_MAIN_SYNC
R1_WORKER_FULL_TESTS=478_OK
R1_COMPILEALL=OK
R1_DIFF_CHECK=OK
R1_PRODUCTION_REPAIR_REOPEN_REQUIRED=NO
```

The R1 branch contains the accepted C/D/F semantic union, accepted E-Core repairs, and E-10 session-authority binding. It was built from `c32c5bf...`; current main later added Owner-approved E-04/E-05/E-07/E-08 authority/state commits. Therefore R1 needs only a latest-main authority sync plus regression before final integration. This is integration work, not a new repair round.

## E-06 evidence verdict

```text
E06_BRANCH=research/e06-official-fee-margin-evidence-v01
E06_PROJECT_BRAIN_REVIEW=ACCEPTED_EVIDENCE_WITH_GAPS
E06_FINAL_JUDGMENT=PARTIALLY_BUILDABLE_WITH_GAPS
E06_EXCHANGE_LEVEL_SCHEDULE=INSUFFICIENT_EVIDENCE
CURRENT_RATE_BACKFILL=FORBIDDEN
```

Bound evidence includes official contract-text minimum transaction margins for all six products and one exact official AU2506 fee point (2025-04-23). A complete 2024-2025 exchange-level fee/margin point-in-time schedule is not established. The remaining gap is a governed evidence prerequisite for future candidate-quality realism, not a reason for an open-ended repair loop.

## F/G/H preparation verdict

```text
FGH_PREP_BRANCH=prep/fgh-codex-rebuild-v01
FGH_PREP_PROJECT_BRAIN_REVIEW=ACCEPTED_CONSTRUCTION_AUTHORITY
FGH_UNAMBIGUOUS_IMPLEMENTATION_FIXES=12
FGH_SOURCE_SEMANTIC_PREREQUISITES=2
FGH_OWNER_GATED_CAUSAL_CHOICES=4
OLD_FGH_DIRECT_MERGE=FORBIDDEN
CODEX_PRIORITY=FGH_REBUILD_AND_COMBINED_CAUSAL_TIMING_INTEGRATION
```

The old F/G/H branches must be rebuilt against the repaired R1/R2 foundation. Unresolved Holy Grail semantic choices remain explicit governed prerequisites and must not be silently frozen by workers. Generic feature/trigger infrastructure can be rebuilt and tested while the Holy Grail contract remains NOT_MACHINE_READY.

## Binding Owner-approved Package E semantics

Authority: `docs/reviews/PACKAGE_E_OWNER_DECISION_APPROVAL_2026-08-20.md`.

```text
E04=OPTION_C_EXPLICIT_BUCKET_CHILD_ORDERS
E05=PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS
E07=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
E08=AVAILABLE_CAPITAL_ONLY
```

Workers may implement these exact semantics but may not substitute alternatives.

## R2 current three lanes

```text
LANE_1=R1_FINAL_MAIN_AUTHORITY_SYNC_PLUS_E06_FGH_PREP_ARTIFACT_INTEGRATION
LANE_2=IMPLEMENT_OWNER_APPROVED_E04_E05_E08
LANE_3=E07_TQSDK_HISTORICAL_MAIN_MAPPING_PROVENANCE_ACQUISITION
MAX_ACTIVE_DS_LANES=3
```

Lane 1 is integration only. Lane 2 is bounded production implementation. Lane 3 is source/provenance acquisition and may only implement a mapping artifact if the approved TqSdk source-governed historical mapping can be obtained under the free/public/no-login policy. If not, it must fail closed and record the prerequisite; it must never substitute a project-authored OI/volume rule.

## Codex timing

```text
WAIT_IDLE_FOR_CODEX=NO
CODEX_START_CONDITION=R2_FOUNDATION_BRANCH_AVAILABLE
CODEX_TASK=OLD_F_G_H_REBUILD_AND_COMBINED_CAUSAL_TIMING_INTEGRATION
```

Do not idle waiting for Codex quota. DS should complete the three R2 lanes now. When Codex quota is available, use Codex for the F/G/H rebuild on the latest accepted R2 foundation. If the R2 branches are still under review at that moment, Codex may study the accepted preparation authority but must not implement on a stale foundation.

## Repair-exit definition

Repair mode ends after:

```text
1. R1 main-sync/integration accepted;
2. E04/E05/E08 owner-approved semantics implemented/tested;
3. E07 either source-governed mapping provenance established OR explicit fail-closed prerequisite recorded;
4. E06 remains explicit evidence prerequisite without fabricated backfill;
5. F/G/H generic rebuild + combined synthetic causal regression accepted;
6. one final second-pass closure audit finds no new critical structural blocker.
```

Holy Grail may remain NOT_MACHINE_READY because unresolved source/Owner semantic choices are normal research prerequisites, not repair defects, provided they are explicit and impossible to bypass.

## Locked boundaries

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
PAID_SOURCE_PURCHASE=NO
```
