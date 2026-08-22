# PROJECT_HANDOFF_CURRENT

> Snapshot date: 2026-08-20
> Project: `kline-playbook-engine`
> Canonical repository: `haozhouliuliuliu/kline-playbook-engine`
> Status: `CURRENT_DERIVED_HANDOFF / READ_ONLY_TAKEOVER_REQUIRED`
>
> **This file is a derived continuity snapshot, not an independent source of truth.** If it conflicts with current Git, `CURRENT_STATE.md`, frozen protocols, Owner decisions, code/tests, or newer accepted evidence, the newer real repository authority wins.

## 1. Fresh-conversation takeover mode

The first turn in a fresh project-brain conversation is **read-only takeover verification only**.

```text
MODE=READ_ONLY_TAKEOVER_VERIFICATION
PROJECT_EXECUTION=PROHIBITED
REPO_WRITES=PROHIBITED
NEXT_WORK_PACKAGE_EXECUTION=PROHIBITED
CODEX_OR_DEEPSEEK_WORKER_PROMPTS=PROHIBITED
TOOL_ADOPTION=PROHIBITED
CANDIDATE_OUTCOME_RESEARCH=PROHIBITED
VALIDATION_UNLOCK=PROHIBITED
FINAL_HOLDOUT_UNLOCK=PROHIBITED
```

The new conversation must first fetch/read the real repository, reconstruct authority/state, identify contradictions or missing facts, report its understanding, and **stop for Owner acceptance**. It must not infer missing project facts from this handoff or from chat memory.

## 2. Exact repository identity

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

For GitHub operations, copy that exact value or obtain it from fetched repository metadata. Do not reconstruct the owner slug from memory.

## 3. Mandatory authority reconstruction

Read in this order before reporting takeover readiness:

1. `OWNER_COLLABORATION_CONTRACT.md`
2. `ARCHITECTURE_BASELINE.md`
3. `CURRENT_STATE.md`
4. `00_READ_FIRST.md`
5. `RESEARCH_DIRECTION.md`
6. `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
7. `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
8. `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
9. `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
10. `docs/reviews/FULL_PROJECT_SECOND_PASS_REPAIR_CLOSURE_AUDIT_2026-08-20.md`
11. `docs/reviews/SECOND_PASS_REPAIR_FINAL_CLOSURE_RECORD_2026-08-20.md`
12. `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`
13. `CROSS_PROJECT_OPERATING_CONTRACT.md`
14. `TOOL_REGISTRY.md`
15. this handoff last.

Also inspect current `main`/HEAD and any authority file named by `CURRENT_STATE.md` that is newer or more specific than this snapshot.

## 4. Current project state at handoff

The second-pass repair program is formally closed.

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
ARCHITECTURE_STATUS=ACCEPTED
SECOND_PASS_REPAIR_MODE=EXITED
SECOND_PASS_REPAIR_CLOSURE_AUDIT=COMPLETE
ORIGINAL_FINDINGS_DISPOSITIONED=62_OF_62
UNRESOLVED_CRITICAL_SILENT_BYPASS=0
UNRESOLVED_HIGH_STRUCTURAL_REPAIR_DEFECT=0
NEXT_NORMAL_PHASE=JIANGHE_AI_FIDELITY_AND_SOURCE_ONLY_EVIDENCE_WITHOUT_CANDIDATE_OUTCOMES
STRATEGY_SOURCE_EXPANSION=PAUSED_FOR_V1
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
JIANGHE_SOURCE_DISTILLATION=V1_1_EXHAUSTIVE_SECOND_PASS_COMPLETE
JIANGHE_SOURCE_ONLY_VERIFIED=NO
JIANGHE_PRIMARY_ELIGIBLE=NO
```

Repair closure means the repair program may end. It does **not** mean candidate-performance research is ready or authorized.

Two mandatory post-repair retrospectives were completed. Retrospective 1 found one additional HIGH completeness-laundering path; it was corrected and merged through PR #14. Retrospective 2 found no new CRITICAL or HIGH repair finding. The final 62-finding audit then gave every original finding an explicit closure disposition.

## 5. Binding research direction — do not regress

```text
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
STATUS=OWNER_APPROVED
```

Binding route:

```text
traceable human trading experience
-> source-faithful AI extraction / structuring
-> versioned Playbook Contract
-> deterministic / versioned machine operationalization
-> governed historical validation
-> strict validation / protected-holdout governance
-> accepted or rejected playbook
```

The current project is **not** authorized to do this as its default discovery route:

```text
mine K-line/chart patterns / indicators / arbitrary rules / parameter grids
-> rank historical PnL / Sharpe / survivors
-> retrofit a human source or narrative afterward
```

Generic architecture wording that AI may “find candidate ideas” does not override the later Owner-approved Human Playbook First direction. Any material return to data-first automatic strategy/pattern mining requires a new Owner-gated research-direction decision and formal authority update before execution.

## 6. Frozen protocol and chronology

Research Protocol v1.0 is FROZEN / BINDING.

Frozen chronology:

```text
DEVELOPMENT=2024-01-01..2024-12-31
VALIDATION=2025-01-01..2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT=2025-07-01..2025-12-31
```

Important frozen safeguards include:

- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`;
- claim status is `EXPLICIT / INFERRED / UNKNOWN`; unknown stays unknown;
- each source-faithful claim requires exactly one source-justified PRIMARY before candidate outcome testing;
- alternatives cannot rescue a failed PRIMARY;
- ambiguity fails closed instead of becoming hidden search freedom;
- renaming does not reset lineage/exposure;
- immutable Research Wave denominator counts all outcome-inspected variants/points;
- SOURCE_ONLY technically denies protected project outcome retrieval through its governed API surface;
- historical final is protected historical evidence, not universal epistemic unseen proof;
- `INSUFFICIENT_EVIDENCE` is legitimate;
- Common Statistical Profile must be appropriately adopted/locked before candidate outcome access;
- final lifecycle exposure is irreversible under the protocol.

## 7. Access / outcome boundary — still locked

```text
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
```

No project-recorded real candidate outcome exposure has been established.

A fresh conversation must not interpret “repair complete” as permission to inspect development/validation/final candidate performance.

## 8. Canonical data facts and qualification

Recorded canonical corpus facts remain:

```text
PRODUCTS=cu,al,ni,au,ag,rb
COVERAGE=2024-01-01..2025-12-31
GRANULARITY=1-minute
CONCRETE_CONTRACTS=212
NORMALIZED_ROWS=15280452
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
CROSS_SOURCE_RESULT=32841_MATCH/0_MISMATCH/0_NOT_COMPARABLE/139_NOT_AVAILABLE
```

Second-pass qualification:

```text
CANONICAL_PRICE_VALUES_REVOKED=NO
CANONICAL_CORPUS_REBUILT_DURING_SECOND_PASS=NO
CANONICAL_CORPUS_REVALIDATED_UNDER_REPAIRED_D01_D02=NO
PRE_CANDIDATE_CANONICAL_REVALIDATION_REQUIRED=YES
```

The accepted historical values were not proven numerically wrong, but old PASS status must not be promoted into a repaired-completeness proof. Candidate-enablement work must explicitly revalidate the corpus under the repaired completeness rules.

## 9. Key accepted second-pass foundation

The repaired/accepted foundation now includes, at a high level:

- authoritative confirmatory candidate execution choke point through `ResearchFirewall`;
- actual-date cohort derivation and actual input data-version binding;
- artifact-bound outcome-test registration and durable governance state;
- lineage continuity and exact wave-denominator semantics;
- claim-level PRIMARY and deterministic Playbook->Strategy equivalence;
- canonical completeness/provenance production rules with content-derived SessionMetadata identity and PASS-only storage admission;
- prospective material-bound SOURCE_ONLY evidence with honest historical `NOT_RECORDED` limits;
- execution/capital/forced-liquidation/round-trip corrections;
- explicit close-bucket child orders where a generic close spans today/previous buckets;
- per-member/per-resolved-contract capital assumptions;
- `AVAILABLE_CAPITAL_ONLY` opening/addition admission;
- point-in-time feature aggregation, full dependency-prefix feature identity, actual implementation-byte binding, stop evaluated-sequence identity, OCO cancellation, and same-bar ambiguity preservation;
- normal-caller aggregation completeness laundering closed before EMA/ADX.

Do not infer stronger threat-model claims than the formal evidence supports.

## 10. Package E / execution prerequisites

Owner-approved semantics:

```text
E04=EXPLICIT_BUCKET_CHILD_ORDERS
E05=PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS
E07=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
E08=AVAILABLE_CAPITAL_ONLY
```

E-06 is no longer an open-ended repair loop:

```text
E06_FINAL_JUDGMENT=PARTIALLY_BUILDABLE_WITH_GAPS
E06_EXCHANGE_LEVEL_SCHEDULE=INSUFFICIENT_EVIDENCE
E06_CURRENT_RATE_BACKFILL=FORBIDDEN
E06_FURTHER_REPEAT_ACQUISITION_DEFAULT=NO
E06_REOPEN_TRIGGER=NEW_OFFICIAL_SOURCE_OR_ACCESS_CHANGE_OR_OWNER_POLICY_CHANGE
```

E-07 is fail-closed:

```text
E07_TQSDK_HISTORY_ACCESS=LOGIN_REQUIRED
E07_MAPPING_COMPLETENESS=COMPLETE_FOR_2024_2025_WINDOW
E07_RUNTIME_MAPPING_STATUS=WIRED_FAIL_CLOSED_VERIFIED
E07_PROJECT_AUTHORED_OI_VOLUME_CALENDAR_PNL_SUBSTITUTE=FORBIDDEN
E07_PSEUDO_MAIN_PRICE_BARS=FORBIDDEN
```

The generic `ContractMappingSchedule` type is structural/synthetic machinery and is **not** proof that source-governed candidate mapping exists.

## 11. F/G/H / Holy Grail current state

The old F/G/H branches were not directly trusted/merged as-is. Their deterministic concepts were rebuilt against the repaired foundation.

Current state:

```text
FGH_GENERIC_FEATURE_CORE=INTEGRATED_ACCEPTED
FGH_GENERIC_STOP_OCO_CORE=INTEGRATED_ACCEPTED
FGH_COMBINED_SYNTHETIC_CAUSAL_CHAIN=INTEGRATED_ACCEPTED
FGH_NORMAL_CALLER_COMPLETENESS_LAUNDERING=CLOSED
HOLY_GRAIL_OWNER_DECISIONS=RECORDED_BINDING
HOLY_GRAIL_MACHINE_READY=YES
PRIMARY_FREEZE_READY=YES
```

Owner-approved Holy Grail semantics include:

- EMA touch uses a prior-completed-bar available close-based EMA reference; current-bar close look-ahead is forbidden;
- ADX `>30 and rising` is pre-pullback context, not a mandatory touch-bar rising condition;
- explicit SMA-seeded EMA / Wilder ADX / Decimal / 6dp ROUND_HALF_UP engineering convention;
- same-bar touch→entry and fill→protective-stop ordering uncertainty fails closed as intrabar ambiguity;
- completed-bar conservative chronology is used and must not be described as exchange-resting intrabar chronology;
- BASE is the first source-primary timeframe branch; 30/60/120-minute alternatives remain source-supported variants;
- swing low/high uses a confirmed pivot/fractal concept with right-side confirmation;
- no machine trailing-stop algorithm is adopted from vague “trail as profits grow” wording;
- exit on push to new highs is an optional versioned variant, not PRIMARY replacement.

Still-open normal operationalization prerequisites:

```text
HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL=OPEN
HOLY_GRAIL_ADX_RISING_WINDOW=OPEN_VERSIONED_NON_OUTCOME_CHOICE
HOLY_GRAIL_SWING_CONFIRMATION_COUNTS=OPEN_VERSIONED_NON_OUTCOME_CHOICE
HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION=NOT_ADOPTED
```

These are normal next-phase research prerequisites, not second-pass repair defects. They must be resolved without candidate-outcome tuning.

## 12. Statistical-profile status

Current project policy still has no adopted real positive-PASS Common Statistical Profile.

```text
REAL_COMMON_STATISTICAL_PROFILE=NOT_ADOPTED
POSITIVE_PASS_PATH=NOT_AVAILABLE
CANDIDATE_OUTCOME_ACCESS=NOT_AUTHORIZED
```

Historical profile work may exist in the repository, but a fresh conversation must use `CURRENT_STATE.md` and current policy/evidence rather than revive stale “profile revision is the current bottleneck” wording from old handoffs.

## 13. Persisted limitations / prerequisites

`KNOWN_LIMITATIONS_AND_TECH_DEBT.md` is the index. Important items include:

```text
LIMIT-001=HISTORICAL_PRICE_LIMIT_METADATA
LIMIT-002=PRE_CANDIDATE_CANONICAL_REVALIDATION
LIMIT-003=E06_HISTORICAL_EXCHANGE_FEE_MARGIN_SCHEDULE
LIMIT-004=E07_SOURCE_GOVERNED_TQSDK_MAPPING
LIMIT-005=HOLY_GRAIL_MACHINE_OPERATIONALIZATION
LIMIT-006=REAL_COMMON_STATISTICAL_PROFILE_NOT_ADOPTED
LIMIT-007=PORTFOLIO_CANDIDATE_OUTCOME_AUTHORITY_NOT_IMPLEMENTED
LIMIT-008=SOURCE_ONLY_AND_LOCAL_STATE_THREAT_MODEL_LIMIT
DECISION-001=LIVE_AI_MARKET_READING_FUTURE_OWNER_GATE
```

Do not silently turn a limitation into a solved fact merely because a generic engine type or synthetic fixture exists.

## 14. Threat-model / evidence boundaries

```text
SOURCE_ONLY_OS_PROCESS_SANDBOX=NOT_PROVEN_NOT_CLAIMED
LOCAL_PRIVATE_STATE_TAMPER_PROOFING=NOT_PROVEN_NOT_CLAIMED
VALIDATION_ROW_TO_CANONICAL_ARTIFACT_BYTE_PROVENANCE=NOT_FULL_END_TO_END_ATTESTATION
HISTORICAL_SOURCE_BYTES_RETROACTIVE_PROOF=IMPOSSIBLE_WHERE_NOT_RECORDED
```

Prospective source evidence has been hardened, but historical bytes that were never recorded cannot be manufactured after the fact.

## 15. Test / verification qualification

Recorded foundation evidence includes:

```text
R2_FOUNDATION_FULL_TESTS=478_OK_BEFORE_FINAL_FGH_CLOSURE_CORRECTION
R2_FOUNDATION_COMPILEALL=OK
R2_FOUNDATION_DIFF_CHECK=OK
FINAL_CLOSURE_CORRECTION_PROJECT_BRAIN_CODE_REVIEW=COMPLETE
FINAL_CLOSURE_CORRECTION_REGRESSION_ARTIFACTS=COMMITTED
INDEPENDENT_PROJECT_BRAIN_FINAL_FULL_SUITE_RERUN=NOT_AVAILABLE_IN_CONNECTOR_ENVIRONMENT
TEMPORARY_GITHUB_ACTIONS_APPROACH=ABANDONED_NOT_ADOPTED
```

Do not upgrade worker-reported test execution into a claim that project brain independently reran the final private-repository suite.

## 16. Tool / worker workflow

Current tool decision:

```text
TOOL_DECISION=USE_EXISTING
NEW_TOOL_REQUIRED=NO
MAIN=SOLE_FINAL_INTEGRATION_AUTHORITY
```

Stable collaboration rules already live in `OWNER_COLLABORATION_CONTRACT.md`; do not duplicate them into new task prompts.

Important operating preferences:

- Owner-facing communication defaults to Chinese, conclusion first, plain language;
- Owner is not expected to perform routine technical operations;
- safe bounded adjacent work should normally be completed as one coherent package;
- ordinary already-authorized technical continuation should not create repeated permission gates;
- safe independent work may run in 2–3 isolated branches/worktrees with exactly one integration lane owning `main`/shared authority;
- when several independent worker tasks are ready, provide all ready prompts together rather than consuming one Owner round-trip per lane;
- when GPT can safely complete repo-only docs/state/review integration through connected GitHub tools, do it directly;
- when Codex/DeepSeek is genuinely needed, give one complete copy-paste prompt and separately specify exact current model recommendation, reasoning intensity, and current-vs-new conversation recommendation;
- paid API/service commitments remain Owner-gated;
- current manual local-agent relay is preferred over inventing brittle paid/UI relay infrastructure when existing capability is adequate.

## 17. Handoff cleanup already performed

Only one active derived handoff entry should remain at repository root: this file.

The superseded 2026-08-19 root handoff chain (`KLINE_PLAYBOOK_ENGINE_HANDOFF_CURRENT_2026-08-19*.md`) is intentionally removed during handoff preparation. Git history retains it if historical reconstruction is ever needed. It must not be used to restore stale status such as “Common Statistical Profile revision is the current bottleneck” or the pre-second-pass firewall overclaims.

Historical reviews/evidence are retained because they are evidence, not active handoff clutter.

## 18. What the new conversation must report before doing any work

The first response after repository inspection should be a concise **takeover verification report**, not a work plan.

At minimum report:

1. exact canonical repository identity and current `main`/HEAD observed;
2. architecture baseline and project phase;
3. binding research direction and anti-regression interpretation;
4. frozen protocol/chronology;
5. exact outcome-access locks;
6. second-pass repair closure status and whether the 62-finding closure artifacts are present;
7. canonical corpus facts plus the repaired-completeness revalidation qualification;
8. E-06/E-07 governed prerequisite status;
9. Holy Grail `MACHINE_READY` status and its remaining operationalization prerequisites;
10. real Common Statistical Profile status;
11. active limitations from `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`;
12. tool decision and whether any supposedly adopted capability lacks repository/runtime evidence;
13. any contradiction, stale pointer, missing authority file, ambiguous status, or repository fact that differs from this handoff.

Then explicitly state:

```text
TAKEOVER_VERIFICATION_COMPLETE=YES_OR_NO
REPOSITORY_WRITES_PERFORMED=NO
PROJECT_EXECUTION_STARTED=NO
WAITING_FOR_OWNER_ACCEPTANCE=YES
```

If anything is unclear, report the ambiguity instead of guessing. Do not choose the next package until the Owner accepts takeover.

## 19. After takeover acceptance — not before

The current normal phase is:

```text
PRE_OUTCOME_HUMAN_PLAYBOOK_OPERATIONALIZATION
```

After the Owner accepts takeover, the new project brain should re-read `CURRENT_STATE.md`, inspect the exact current authorities/prerequisites, and decide the safest next bounded package. It should not automatically resume an old handoff's historical “next action”.

This file intentionally does not pre-authorize candidate outcomes, validation, final holdout, Shadow/Forward, broker actions, real money, paid source access, or a new research direction.
