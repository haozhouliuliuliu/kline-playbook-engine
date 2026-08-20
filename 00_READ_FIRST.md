# 00_READ_FIRST

This repository is in `RESEARCH_FOUNDATION`.

Canonical repository:

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

## Read current authority in this order

1. `OWNER_COLLABORATION_CONTRACT.md` — stable Owner collaboration preferences.
2. `ARCHITECTURE_BASELINE.md` — Skeleton v1.0, ACCEPTED.
3. `CURRENT_STATE.md` — current status, locks, next action, current prerequisites.
4. `RESEARCH_DIRECTION.md` — Owner-approved Human Playbook First research route and anti-regression guard.
5. `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` — FROZEN / BINDING.
6. `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` — FROZEN 12/6/6 chronology.
7. `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`.
8. `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`.
9. `docs/reviews/FULL_PROJECT_SECOND_PASS_REPAIR_CLOSURE_AUDIT_2026-08-20.md` — final disposition of the original 62 second-pass findings.
10. `docs/reviews/SECOND_PASS_REPAIR_FINAL_CLOSURE_RECORD_2026-08-20.md` — formal repair-node closure record.
11. `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` — active/deferred prerequisites that must survive handoff.
12. `CROSS_PROJECT_OPERATING_CONTRACT.md` — adopted Version 3.1 governance constitution.
13. `TOOL_REGISTRY.md` — capability catalog; appearance here does not mean this project adopted the tool.
14. `PROJECT_HANDOFF_CURRENT.md` — derived continuity snapshot only; read it last, never as a replacement for the authorities above.

`CURRENT_STATE.md` is the authority for mutable project state and the next action. A handoff or chat summary cannot override current Git, current code/tests, frozen protocols, Owner decisions, or accepted evidence.

## Current phase summary

```text
SECOND_PASS_REPAIR_MODE=EXITED
SECOND_PASS_REPAIR_CLOSURE_AUDIT=COMPLETE
ORIGINAL_FINDINGS_DISPOSITIONED=62_OF_62
UNRESOLVED_CRITICAL_SILENT_BYPASS=0
UNRESOLVED_HIGH_STRUCTURAL_REPAIR_DEFECT=0
NEXT_NORMAL_PHASE=PRE_OUTCOME_HUMAN_PLAYBOOK_OPERATIONALIZATION
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
```

Repair completion does **not** mean candidate-performance readiness. The project has returned from repair mode to normal pre-outcome research/foundation work while important prerequisites remain fail-closed.

## Catastrophic anti-regression rule

Do **not** reinterpret broad architecture language such as AI may “find candidate ideas” as permission to return to data-first K-line/chart-pattern/indicator/parameter mining.

Binding route:

```text
traceable human trading experience
-> source-faithful AI extraction / structuring
-> versioned Playbook Contract
-> deterministic / versioned machine operationalization
-> governed historical validation
-> strict validation / protected holdout governance
-> accepted or rejected playbook
```

The following is not the current authorized strategy-discovery route:

```text
mine K-line/chart patterns / indicators / rule grids / parameters
-> rank by historical PnL / Sharpe / trade outcomes
-> retrofit a human source or narrative afterward
```

Any material return to data-first strategy/pattern mining is an Owner-gated research-direction change.

## Important current prerequisites

Do not silently promote any of these into solved facts:

```text
PRE_CANDIDATE_CANONICAL_REVALIDATION_REQUIRED=YES
E06_CONTINUOUS_HISTORICAL_EXCHANGE_FEE_MARGIN_SCHEDULE=INSUFFICIENT_EVIDENCE
E07_SOURCE_GOVERNED_TQSDK_HISTORICAL_MAIN_MAPPING=INCOMPLETE_FAIL_CLOSED
HOLY_GRAIL_MACHINE_READY=NO
HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION=NOT_ADOPTED
REAL_COMMON_STATISTICAL_PROFILE=NOT_ADOPTED
PORTFOLIO_CANDIDATE_OUTCOME_AUTHORITY=NOT_IMPLEMENTED
SOURCE_ONLY_OS_PROCESS_SANDBOX=NOT_PROVEN_NOT_CLAIMED
LOCAL_PRIVATE_STATE_TAMPER_PROOFING=NOT_PROVEN_NOT_CLAIMED
```

Canonical historical price values were not revoked, but the accepted corpus has not yet been re-certified under the repaired D-01/D-02 completeness rules.

## Fresh-conversation takeover rule

A fresh project-brain conversation starts with **read-only takeover verification only**.

During the first takeover turn it must:

- fetch the real repository using the exact canonical repository identity above;
- read the authority set in the order above;
- reconstruct current state, locks, active prerequisites, research direction, and next normal phase;
- report any contradiction, stale reference, missing file, or ambiguity it finds;
- explicitly distinguish repository facts from the derived handoff snapshot;
- stop and wait for Owner acceptance.

During that first turn it must **not**:

```text
REPO_WRITE
START_NEXT_WORK_PACKAGE
GENERATE_CODEX_OR_DEEPSEEK_WORKER_PROMPTS
ADOPT_NEW_TOOLS
RUN_CANDIDATE_OUTCOME_RESEARCH
UNLOCK_VALIDATION_OR_FINAL_HOLDOUT
MAKE_NEW_PRODUCT_OR_RESEARCH_DIRECTION_DECISIONS
```

Only after the Owner accepts the takeover report may the new conversation choose and execute the next normal bounded package from current authority.

## Handoff hygiene

Only one active derived handoff entry should exist at the repository root: `PROJECT_HANDOFF_CURRENT.md`.

Old superseded derived handoff snapshots/pointer chains should not be used for takeover. Git history preserves them if historical reconstruction is ever needed. Historical evidence, frozen protocols, accepted reviews, and Owner decisions are not handoff clutter and must not be deleted merely to reduce context.

## Verification path

Canonical bootstrap verification command:

```text
python -m unittest discover -s tests -v
```

Test counts are evidence about a particular executed suite, not a substitute for repository authority or project readiness.