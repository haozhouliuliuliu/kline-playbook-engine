# POST_CDF_E_CORE_GOVERNANCE_REVIEW_AND_REPAIR_EXIT_PLAN_V0_1

> Date: 2026-08-20
> Role: project-brain review / repair-exit orchestration authority
> Candidate outcome access: NOT_AUTHORIZED

## Current review verdict

```text
CDF_COMBINED_INTEGRATION_WORKER_REVIEW=PASS_READY_FOR_MAIN_INTEGRATION
PACKAGE_E_CORE_REVIEW=PASS_READY_FOR_COMBINED_E_INTEGRATION
PACKAGE_E_GOVERNANCE_RESEARCH_REVIEW=ACCEPTED_AS_DECISION_INPUT
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

CDF integration branch `integration/cdf-final-v01` combines accepted Package C/D/F semantics from main baseline `18a28c311a13dd531a6b62600838365f9090c7eb`. Worker evidence records 260 focused tests, 451 full tests, compileall clean, diff-check clean, no conflict markers, and ancestry for C/D/F/main. Project-brain code review confirms the C/F shared `research_firewall.py` semantics are a union rather than one branch overwriting the other.

Package E-Core branch `repair/package-e-core-execution-v01` is accepted for its scoped semantics: E-01, E-02, E-03, E-09, E-11, E-12, E-13. E-04/E-05/E-08/E-10 remain untouched as commanded; Portfolio candidate outcome remains closed. E-13 remains bootstrap-feasibility scope only.

E-Governance branch `research/package-e-governance-authority-v01` is accepted as decision input, not adopted semantics. It concludes:

```text
E04_STATUS=OWNER_DECISION_REQUIRED
E05_STATUS=OWNER_DECISION_REQUIRED
E06_STATUS=INSUFFICIENT_EVIDENCE
E07_STATUS=OWNER_DECISION_REQUIRED
E08_STATUS=OWNER_DECISION_REQUIRED
```

E-06 remains a source-evidence collection problem. No current rate may be backfilled into 2024-2025. E-07/E-08 and the project-specific E-04/E-05 representation semantics are not delegated to workers.

## Repair exit definition

The project does NOT need every future Trading Loop component finished before leaving repair mode. Second-pass repair mode ends when all second-pass findings are either:

1. fixed and regression-tested; or
2. converted into an explicit governed prerequisite / Owner-gated unresolved semantic that cannot be silently bypassed.

Candidate outcome access remains locked until all outcome-affecting prerequisites are satisfied.

## Remaining substantive repair work

Expected path, assuming no new CRITICAL/HIGH integration defect is discovered:

```text
ROUND_R1_NOW=
  integrate CDF + E-Core on one tree
  + implement E-10 using accepted D-05 SessionMetadata identity
  + collect E-06 official historical fee/margin evidence as far as free/public sources allow
  + obtain Owner decisions for E-04/E-05/E-07/E-08

ROUND_R2=
  implement approved E-04/E-05/E-07/E-08 semantics
  + rebuild/correct old Holy-Grail/feature/stop F-G-H package against repaired foundation
  + combined causal-timing regression

FINAL_CLOSURE=
  one full second-pass closure audit on the integrated tree
  + only bounded corrections if concrete new blockers are found
```

Planning estimate: two substantive repair rounds plus one final closure audit. This is not a guarantee that the closure audit finds zero small defects, but another long open-ended audit/repair loop is not the planned default.

## Codex allocation

Do not idle waiting for Codex quota. Deterministic integration/E-10 and official-source evidence collection can proceed now with the current worker lane.

Reserve Codex, when available, for the hardest remaining implementation package:

```text
CODEX_PRIORITY=OLD_F_G_H_REBUILD_AND_COMBINED_CAUSAL_TIMING_INTEGRATION
```

Reason: this package spans Playbook semantics, feature resampling/EMA/ADX causal computation, stop-trigger observation timing, identity/provenance, and combined regression. It is the highest cross-module reasoning/code-integration load remaining. Codex must still obey project-brain-frozen semantics; it is an executor, not the authority for unresolved research design.

## Current lane plan

```text
LANE_1=INTEGRATE_CDF_E_CORE_AND_IMPLEMENT_E10
LANE_2=E06_OFFICIAL_HISTORICAL_FEE_MARGIN_EVIDENCE_COLLECTION
LANE_3=PREPARE_FGH_REBUILD_AUTHORITY_AND_USE_CODEX_WHEN_QUOTA_REFRESHES
TOOL_DECISION=USE_EXISTING
NEW_TOOL_REQUIRED=NO
```

## Locked boundaries

```text
NO_CANDIDATE_OUTCOME_DATA_USED=REQUIRED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
E04_OWNER_DECISION_REQUIRED=YES
E05_OWNER_DECISION_REQUIRED=YES
E07_OWNER_DECISION_REQUIRED=YES
E08_OWNER_DECISION_REQUIRED=YES
```
