# 00_READ_FIRST

Canonical repository:

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

This file owns the active read order. Current GitHub `main` is the only dynamic
project fact source. Do not reconstruct current state from chat memory, Project
uploads, personal memory, old branches, stale handoffs, or historical review
snapshots.

## Fresh-conversation takeover

A fresh project-brain conversation starts with read-only takeover verification.
**This file must be the first repository file read.** After it, fetch current
`main` HEAD and read the active core below in order.

### Active core — read in this order

1. `OWNER_COLLABORATION_CONTRACT.md` — stable Owner collaboration rules.
2. `PROJECT_BRAIN_RUNTIME_BRIEF.md` — compact current live pointer.
3. `CURRENT_STATE.md` — detailed mutable current authority.
4. `ARCHITECTURE_BASELINE.md` — current architecture/product boundary.
5. `RESEARCH_DIRECTION.md` — Human Playbook First / Jianghe direction.
6. `docs/research/JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md` — AI Trader identity/replay/fidelity governance.
7. `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md` — Jianghe source authority.
8. `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` — current unresolved limits; `LIMIT-012` is resolved and `LIMIT-013` is the current downloaded-Kline input-scope gate.
9. `docs/reviews/JIANGHE_STAGE_A_V0_3_THREE_PROVIDER_MATCHED_CAPABILITY_COMPARISON_V0_1.md` — completed three-provider matched comparison.
10. `docs/reviews/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_V0_1.md` — immutable first real downloaded-Kline DeepSeek pilot.
11. `docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_SUMMARY_V0_1.json` — machine-readable pilot summary.
12. `docs/reviews/JIANGHE_DOWNLOADED_KLINE_DKL_DS_003_FORENSIC_REVIEW_V0_1.md` — completed DKL-DS-003 forensic closure.
13. `docs/reviews/JIANGHE_TIMEFRAME_INPUT_SCOPE_EVIDENCE_REVIEW_V0_1.md` — current timeframe-scope evidence review.
14. `docs/reviews/JIANGHE_STAGE_A_V0_3_CAPABILITY_FIRST_OWNER_DECISION.md` — historical/current Stage-A research-design authority where still applicable.
15. `docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_3.json` — immutable V0.3 matched-comparison executable identity authority.
16. `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md` and `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_002_MINIMAX_ADJUDICATION_V0_1.md` — immutable early paid attempts when historical accounting is relevant.
17. refresh `refs/heads/stage-a-live-state-v0-2`, `refs/heads/stage-a-live-state-v0-3`, or `refs/heads/downloaded-kline-pilot-state-v0-1` only when the specific historical/current ledger fact is required.
18. `PROJECT_HANDOFF_CURRENT.md` — derived continuity pointer; **read last**.

### Takeover-turn report

During the first takeover turn remain read-only and report:

- current `main` HEAD;
- phase, current work package, architecture and Human Playbook First/Jianghe state;
- three-provider matched-comparison result and DeepSeek's current leading-provider status, explicitly noting no permanent adoption;
- downloaded-Kline V0.1 pilot result and immutable `REVIEW_BEFORE_EXPAND` historical verdict;
- DKL-DS-003 forensic closure and `DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2` identity;
- timeframe evidence status: `1H/15m/5m` is the current test protocol, not permanent Jianghe doctrine; source-backed 4H evidence exists but higher-timeframe requirements remain unresolved in current PRIMARY;
- `LIMIT-012=RESOLVED__THREE_PROVIDER_MATCHED_EVIDENCE_COMPLETE` and current `LIMIT-013` input-scope gate;
- current project accounted CNY, CNY100 hard cap, paid-call pause and absence of a current executable paid slot;
- exact next work and all outcome/validation/holdout/shadow/broker/real-money locks;
- any authority contradiction.

Then stop for Owner acceptance. Do not make a provider call on the takeover turn.

## Current live execution state

```text
CURRENT_WORK_PACKAGE=JIANGHE_DOWNLOADED_KLINE_PILOT_DEFECT_REVIEW_COMPLETE
NEXT_NORMAL_PHASE=DOWNLOADED_KLINE_INPUT_PROTOCOL_DECISION
OWNER_ACTION=DECIDE_V0_2_INPUT_SCOPE_THEN_AUTHORIZE_OR_DECLINE_FRESH_SMALL_PILOT
THREE_PROVIDER_MATCHED_COMPARISON=COMPLETE
STAGE_A_CURRENT_LEADING_PROVIDER=DEEPSEEK
ADOPTED_PROVIDER=NONE__NO_PERMANENT_ADOPTION
DOWNLOADED_KLINE_PILOT=COMPLETE__HISTORICAL_VERDICT_REVIEW_BEFORE_EXPAND
PILOT_REVIEW_RESOLUTION=READY_FOR_FRESH_PILOT_V0_2
NEW_INPUT_CONTRACT_VERSION=DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2
NEW_INPUT_CONTRACT_SCHEMA_IDENTITY=0057b11939c71f10fa7094db119f5b280e74edd13cb2bb7d40cc29a418c4c68a
CURRENT_TEST_TIMEFRAMES=1H__15M__5M
CURRENT_1H_15M_5M_IS_TEST_PROTOCOL=YES
JIANGHE_HIGHER_TIMEFRAME_EVIDENCE_STATUS=UNRESOLVED_IN_CURRENT_PRIMARY_EVIDENCE
SOURCE_BACKED_HIGHER_TIMEFRAME_SUPPORT=YES__4H_EXAMPLES_EXIST
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
LIMIT_012=RESOLVED__THREE_PROVIDER_MATCHED_EVIDENCE_COMPLETE
LIMIT_013=OPEN__OWNER_DECISION_REQUIRED
PAID_CALLS_CURRENTLY_PAUSED=YES__DOWNLOADED_KLINE_INPUT_PROTOCOL_DECISION
NEXT_EXPLICIT_PAID_SLOT=NONE
TOOL_DECISION=USE_EXISTING
CURRENT_PROJECT_ACCOUNTED_CNY=3.1609662
TOTAL_API_HARD_CAP_CNY=100
AUTOMATIC_RECHARGE=FORBIDDEN
LARGE_BATCH_AUTHORIZED=NO
OUTCOME_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

The existing source-backed Jianghe material includes examples such as `4H+15m`,
`1H+5m`, `15m+1m`, and `4H→1H→5m`. This disproves any current claim that Jianghe
only uses 1H and below, but it does **not** establish a frozen rule that every input
must contain 4H or daily bars. Adding higher-timeframe paid input is a separate
Owner research/input-protocol decision.

## Capability and evidence anti-regression rules

```text
MODEL_SELECTION_PRIORITY=JIANGHE_CORRECTNESS_AND_CAPABILITY__THEN_ACTUAL_CNY__THEN_ACTUAL_TIME
FAIRNESS=SAME_MATERIAL__SAME_QUESTION__DIFFERENT_MODEL_BRAIN
NON_SCOREABLE_NORMALIZER_IS_CAPABILITY_FATAL=NO
TRUNCATION_IS_CAPABILITY_FATAL=NO
LONG_REASONING_IS_CAPABILITY_FATAL=NO
PROVIDER_FORMAT_DIFFERENCE_IS_CAPABILITY_FATAL=NO
PRODUCTION_JSON_REQUIRED_FOR_CAPABILITY_SCORE=NO
RAW_FINAL_ANSWER_EVIDENCE=REQUIRED__SECRET_SAFE__NO_CHAIN_OF_THOUGHT
NORMALIZED_EVALUATION_VIEW=REQUIRED__IDENTITY_BOUND__FORMAT_ONLY
HISTORICAL_ATTEMPTS=IMMUTABLE__NEVER_RERUN
AUTOMATIC_RETRY=FORBIDDEN
AUTOMATIC_NEXT_SLOT=FORBIDDEN
```

The first downloaded-Kline pilot's five attempts are immutable. DKL-DS-003's
historical model answer remains wrong on two factual details; the V0.2 input
contract repairs only generic order/latest-closed-bar/exact-bucket semantics and
has not yet been sent to a provider.

## Current research / product route

```text
traceable Jianghe human trading experience
-> source-faithful V1.1 knowledge pack
-> versioned Jianghe AI Trader identity
-> causal multi-timeframe observation + working memory
-> capability-first provider qualification
-> downloaded-Kline point-in-time pilot
-> input-protocol scope decision
-> fresh independent small V0.2 pilot if Owner authorizes
-> larger historical evaluation only after evidence supports expansion
-> governed outcome research only after explicit gates
-> genuinely unseen Shadow/Forward evidence when later authorized
```

The AI is the market-reading decision brain. Deterministic infrastructure owns hard
risk, orders, execution truth, reconciliation and Safety. UNKNOWN, contradiction,
unfamiliar state or unsupported interpretation must allow WAIT/NO_TRADE rather than
invention.

## After takeover: mandatory refresh rule

Before every substantive project reply:
1. fetch current `main` HEAD;
2. fetch `PROJECT_BRAIN_RUNTIME_BRIEF.md`;
3. refresh `CURRENT_STATE.md` and the specific named authority for state/architecture/locks/next work/provider/model/tool answers;
4. refresh the relevant ledger ref only when stating a ledger/attempt/accounting fact;
5. never use conversation memory as mutable authority.

## Conditional historical authority

- `docs/reviews/JIANGHE_STAGE_A_V0_3_OFFLINE_CLOSURE_V0_1.md` — V0.3 offline closure and executable identity history.
- `docs/reviews/JIANGHE_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_OWNER_DECISION.md` and `docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_2.json` — historical V0.2 semantics/accounting only.
- `docs/reviews/JIANGHE_RMB100_REAL_MODEL_FIDELITY_FUNNEL_V0_1.md` — historical V0.1/V0.2 funnel semantics; formatting fatal-stop logic does not govern later capability conclusions.
- `docs/reviews/JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md` — Stage-A stimulus baseline unless explicitly versioned.
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` and selection-firewall authority — read before PRIMARY/outcome changes.
- `CROSS_PROJECT_OPERATING_CONTRACT.md` — cross-project governance.
- `TOOL_REGISTRY.md` — tool admission.

Do not reopen a closed whole-repository audit by default.