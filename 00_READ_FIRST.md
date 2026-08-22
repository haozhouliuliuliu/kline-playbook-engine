# 00_READ_FIRST

This repository is in `RESEARCH_FOUNDATION`.

Canonical repository:

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

## Read current authority in this order

1. `OWNER_COLLABORATION_CONTRACT.md` — stable Owner collaboration preferences.
2. `ARCHITECTURE_BASELINE.md` — Skeleton v1.0 plus current adopted amendment.
3. `docs/architecture/ADR_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1.md` — current Jianghe AI decision-layer boundary.
4. `CURRENT_STATE.md` — current status, locks, next action, current prerequisites.
5. `RESEARCH_DIRECTION.md` — Owner-approved Human Playbook First research route and anti-regression guard.
6. `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` — FROZEN / BINDING.
7. `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` — FROZEN 12/6/6 chronology.
8. `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`.
9. `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`.
10. `docs/reviews/FULL_PROJECT_SECOND_PASS_REPAIR_CLOSURE_AUDIT_2026-08-20.md` — final disposition of the original 62 second-pass findings.
11. `docs/reviews/SECOND_PASS_REPAIR_FINAL_CLOSURE_RECORD_2026-08-20.md` — formal repair-node closure record.
12. `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` — active/deferred prerequisites that must survive handoff.
13. `CROSS_PROJECT_OPERATING_CONTRACT.md` — adopted Version 3.1 governance constitution.
14. `TOOL_REGISTRY.md` — capability catalog; appearance here does not mean this project adopted the tool.
15. `docs/research/JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md` — AI Trader version/replay boundary.
16. `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md` — current Jianghe source authority and its stated read order.
17. `PROJECT_BRAIN_RUNTIME_BRIEF.md` — compact post-takeover live pointer; after takeover it must be refreshed before every substantive project reply.
18. `PROJECT_HANDOFF_CURRENT.md` — derived continuity snapshot only; read it last, never as a replacement for the authorities above.

`CURRENT_STATE.md` is the authority for mutable project state and the next action. A handoff or chat summary cannot override current Git, current code/tests, frozen protocols, Owner decisions, or accepted evidence.

After takeover acceptance, the project brain must fetch the current `main` HEAD and `PROJECT_BRAIN_RUNTIME_BRIEF.md` before every substantive project reply. If `main` moved or the answer depends on mutable project state, it must also refresh `CURRENT_STATE.md` and the relevant authority instead of relying on chat memory or prior-turn assumptions.

## Current phase summary

```text
SECOND_PASS_REPAIR_MODE=EXITED
SECOND_PASS_REPAIR_CLOSURE_AUDIT=COMPLETE
ORIGINAL_FINDINGS_DISPOSITIONED=62_OF_62
UNRESOLVED_CRITICAL_SILENT_BYPASS=0
UNRESOLVED_HIGH_STRUCTURAL_REPAIR_DEFECT=0
HOLY_GRAIL_PLAYBOOK_CURRENT_VERSION=V0_4
HOLY_GRAIL_MACHINE_READY=YES
HOLY_GRAIL_PRIMARY_FREEZE_READY=YES
RASCHKE_NR7_PLAYBOOK_CURRENT_VERSION=V0_1
RASCHKE_NR7_MACHINE_READY=NO
RASCHKE_NR7_SOURCE_SEMANTIC_RESOLUTION=INSUFFICIENT
CHINA_FIRST_PLAYBOOK_PROMOTION_WAVE_V0_1=COMPLETE_NEGATIVE
CHINA_FIRST_SELECTED_SOURCE=NONE
GRIMES_FREE_PUBLIC_PLAYBOOK_PROMOTION_V0_1=COMPLETE_NEGATIVE
GRIMES_SELECTED_FAMILY=GRIMES_FAILURE_TEST_FAILED_BREAKOUT_REVERSAL
GRIMES_SOURCE_SEMANTIC_RESOLUTION=INSUFFICIENT
GRIMES_MACHINE_READY=NO
CANONICAL_REPAIRED_D01_D02_REVALIDATION=COMPLETE_FAIL
CANONICAL_TARGETED_REPAIR_STATUS=SUPERSEDED_BY_QUALIFIED_ELIGIBILITY_VIEW_V1
CANONICAL_116_FAILURE_ROOT_CAUSE_REVIEW=MIXED_ROOT_CAUSES
CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1=ADOPTED
CANONICAL_ELIGIBLE_PARTITIONS=32768
CANONICAL_ELIGIBLE_D01_D02=32768_PASS_0_FAIL
PRE_CANDIDATE_CANONICAL_REVALIDATION_REQUIRED=SATISFIED_BY_QUALIFIED_ELIGIBILITY_VIEW_V1
CANDIDATE_USE_OF_CURRENT_CANONICAL_CORPUS=NOT_AUTHORIZED
NEXT_NORMAL_PHASE=JIANGHE_AI_FIDELITY_AND_SOURCE_JUSTIFIED_PRIMARY_EVIDENCE_WITHOUT_CANDIDATE_OUTCOMES
STRATEGY_SOURCE_EXPANSION=PAUSED_FOR_V1
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
JIANGHE_SOURCE_DISTILLATION=V1_1_EXHAUSTIVE_SECOND_PASS_COMPLETE
JIANGHE_SOURCE_ONLY_VERIFIED=YES
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_AI_REPLAY_SCOPE=SYNTHETIC_NON_OUTCOME_ONLY
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
```

Repair completion does **not** mean candidate-performance readiness. Holy Grail V0.4 has a
frozen StrategyIdentity but no outcome registration; NR7 V0.1 remains fail-closed. Historical
canonical revalidation remains 32864 PASS / 116 FAIL, while the separately governed Qualified
Eligibility View V1 supplies 32768 D01/D02-certified candidate-eligible partitions. Candidate
outcome use remains unauthorized.

Key integrated evidence (2026-08-21):
- `docs/evidence/RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_3.md` + `RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3.json` / `.md`
- `docs/evidence/RASCHKE_NR7_INTERPRETATION_STATUS_V0_1.md` + `RASCHKE_NR7_PLAYBOOK_CONTRACT_DRAFT_V0_1.json` / `.md`
- `docs/reviews/RASCHKE_NR7_SOURCE_SEMANTIC_RESOLUTION_V0_2.md` (+ `.json`；NR7 仍失败闭合，未创建机器实现)
- `docs/reviews/CHINA_FIRST_PLAYBOOK_PROMOTION_WAVE_V0_1.md` (+ `.json`；三个既有中国期货来源线索顺序审查完成，`SELECTED_SOURCE=NONE`，未创建假 dossier/claim corpus/机器策略)
- `docs/reviews/GRIMES_FREE_PUBLIC_PLAYBOOK_PROMOTION_WAVE_V0_1.md` (+ `.json`；Failure Test 来源语义完成后失败闭合，未创建机器策略)
- `docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.md` (+ `.json`)
- `docs/evidence/CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.md` (+ `.json`)
- `docs/reviews/CANONICAL_D01_D02_116_FAILURE_ROOT_CAUSE_REVIEW_V0_1.md` (+ `.json`)
- `docs/evidence/CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1.md` (+ `.json`)
- `docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_4.md` (+ `.json`)
- `docs/research/HUMAN_PLAYBOOK_STATISTICAL_ACCEPTANCE_ROUTE_POLICY_V1_0.md`
- `docs/evidence/SHADOW_RUNTIME_FOUNDATION_V0_1.md`
- `docs/evidence/HOLY_GRAIL_PRIMARY_FREEZE_V0_1.md` (+ `.json`)
- `docs/evidence/E07_TQSDK_MAPPING_SCHEMA_AND_CAPTURE_V0_1.md` (+ source-bound `.json`)
- `docs/reviews/PROSPECTIVE_SHADOW_STATISTICAL_PROFILE_RESEARCH_V0_1.md`
- `docs/reviews/PROSPECTIVE_SHADOW_STATISTICAL_PROFILE_RESOLUTION_V0_2.md`
- `docs/evidence/HOLY_GRAIL_SHADOW_RUNTIME_ADAPTER_V0_1.md`
- `docs/evidence/E07_RUNTIME_MAPPING_WIRING_V0_1.md`
- `docs/evidence/PRE_SHADOW_GATE_V0_1.md`
- `docs/evidence/STOP_OCO_RUNTIME_EXECUTION_SEMANTICS_V0_1.md`
- `docs/evidence/HOLY_GRAIL_FULL_SHADOW_RUNTIME_WIRING_V0_2.md`
- `docs/evidence/PROSPECTIVE_EXECUTION_AUTHORITY_RUNTIME_V0_1.md`
- `docs/evidence/PRE_SHADOW_GATE_V0_2.md`
- `docs/reviews/PRE_SHADOW_READINESS_CONVERGENCE_V0_3.md`
- `docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.md` (+ `.json`；V1.1 knowledge pack、来源/claim/case 清单绑定，受保护结果能力技术拒绝；不提升 PRIMARY 或 outcome 权限)

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
PRE_CANDIDATE_CANONICAL_REVALIDATION_REQUIRED=SATISFIED_BY_QUALIFIED_ELIGIBILITY_VIEW_V1 (HISTORICAL_REVALIDATION=32864_PASS_116_FAIL_UNCHANGED)
CANDIDATE_USE_OF_CURRENT_CANONICAL_CORPUS=NOT_AUTHORIZED
E06_CONTINUOUS_HISTORICAL_EXCHANGE_FEE_MARGIN_SCHEDULE=INSUFFICIENT_EVIDENCE
E07_SOURCE_GOVERNED_TQSDK_HISTORICAL_MAIN_MAPPING=COMPLETE_FOR_2024_2025_WINDOW_WIRED_FAIL_CLOSED_VERIFIED
HOLY_GRAIL_MACHINE_READY=YES
HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION=SWING_BASED_TRAILING_PROJECT_INFERRED
RASCHKE_NR7_MACHINE_READY=NO
RASCHKE_NR7_SOURCE_SEMANTIC_RESOLUTION=INSUFFICIENT (five substantive source-semantic blockers remain; no NR7 machine/PRIMARY)
GRIMES_MACHINE_READY=NO
GRIMES_SOURCE_SEMANTIC_RESOLUTION=INSUFFICIENT (four substantive source-semantic blockers remain; no Grimes machine/PRIMARY)
STATISTICAL_ACCEPTANCE_ROUTE=ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD
PROSPECTIVE_SHADOW_STATISTICAL_PROFILE=NOT_LOCKABLE_UNDER_CURRENT_ASSUMPTION_AUTHORITY
PROSPECTIVE_PROCESS_ASSUMPTION_DESIGN=NO_GOVERNABLE_A_B_ASSUMPTION_FOUND
HOLY_GRAIL_STOP_OCO_OMS_EXECUTION=IMPLEMENTED_SYNTHETIC_COMPLETED_BAR_VERIFIED
PORTFOLIO_CANDIDATE_OUTCOME_AUTHORITY=NOT_IMPLEMENTED
JIANGHE_SOURCE_ONLY_VERIFIED=YES (PROJECT_API_SESSION_MECHANISM__MATERIAL_BOUND; OS/process sandbox 不声明)
JIANGHE_PRIMARY_ELIGIBLE=NO (仍需 source-justified PRIMARY branches、UNKNOWN fail-closed 和 AI fidelity evidence)
SOURCE_ONLY_OS_PROCESS_SANDBOX=NOT_PROVEN_NOT_CLAIMED
LOCAL_PRIVATE_STATE_TAMPER_PROOFING=NOT_PROVEN_NOT_CLAIMED
```

Canonical historical price values were not revoked, and explicit revalidation remains an immutable historical fact (32980 revalidated, 116 FAIL, 13008 missing expected bars). Qualified Eligibility View V1 uniformly excludes governed first trading-day partitions and is the separately identity-bound candidate-eligibility authority; candidate outcome access remains locked by other gates.

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
