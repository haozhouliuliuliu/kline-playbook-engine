# 00_READ_FIRST

Canonical repository:

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

This file owns the active read order. Current GitHub `main` is the only dynamic project fact source. Do not reconstruct current state from chat memory, Project uploads, personal memory, old branches, stale handoffs, or historical review snapshots.

## Fresh-conversation takeover

A fresh project-brain conversation starts with read-only takeover verification. **This file must be the first repository file read.** After it, fetch current `main` HEAD and read the active core below in order.

### Active core — read in this order

1. `OWNER_COLLABORATION_CONTRACT.md` — stable Owner collaboration rules.
2. `PROJECT_BRAIN_RUNTIME_BRIEF.md` — compact current live pointer.
3. `CURRENT_STATE.md` — detailed mutable current authority.
4. `ARCHITECTURE_BASELINE.md` — current architecture/product boundary.
5. `RESEARCH_DIRECTION.md` — Human Playbook First / Jianghe direction.
6. `docs/research/JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md` — AI Trader identity/replay/fidelity governance.
7. `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md` — Jianghe source authority.
8. `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` — unresolved limitations; LIMIT-012 is active.
9. `docs/reviews/JIANGHE_STAGE_A_V0_3_CAPABILITY_FIRST_OWNER_DECISION.md` — **current Stage-A model-comparison research-design authority**.
10. `docs/evidence/JIANGHE_STAGE_A_CAPABILITY_COMPARISON_PLAN_V0_3.json` — current non-executable V0.3 matched-comparison plan; executable identities remain pending offline closure.
11. `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md` — immutable first paid attempt.
12. `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_002_MINIMAX_ADJUDICATION_V0_1.md` — immutable second paid attempt and historical V0.2 adjudication.
13. `docs/reviews/JIANGHE_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_OWNER_DECISION.md` — historical V0.2 experiment-design authority; does not override V0.3 capability semantics.
14. `docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_2.json` — historical V0.2 plan/carry-forward identity and accounting authority.
15. refresh `refs/heads/stage-a-live-state-v0-2` when verifying historical attempt/accounting state.
16. `docs/reviews/JIANGHE_STAGE_A_V0_3_OFFLINE_CLOSURE_V0_1.md` — V0.3 offline closure record (finding dispositions, frozen plan/identities, GO/NO-GO).
17. `PROJECT_HANDOFF_CURRENT.md` — derived continuity pointer; **read last**.

### Takeover-turn report

During the first takeover turn remain read-only and report: current `main` HEAD, phase/work package/architecture, Jianghe/PRIMARY/LIMIT-012, V0.3 capability-first objective and paid-call pause, immutable Attempt 001/002 facts, why V0.2 MiniMax operational elimination is not V0.3 Jianghe capability failure, all three current capability candidates, historical accounting/CNY100 hard cap, exact next work/executable-slot status, all downstream locks, and any authority contradiction. Then stop for Owner acceptance; do not make a provider call.

## Current Stage-A V0.3 anti-regression rules

```text
MODEL_SELECTION_PRIORITY=JIANGHE_CORRECTNESS_AND_CAPABILITY__THEN_ACTUAL_CNY__THEN_ACTUAL_TIME
FAIRNESS=SAME_MATERIAL__SAME_QUESTION__DIFFERENT_MODEL_BRAIN
NON_SCOREABLE_NORMALIZER_IS_CAPABILITY_FATAL=NO
TRUNCATION_IS_CAPABILITY_FATAL=NO
LONG_REASONING_IS_CAPABILITY_FATAL=NO
PROVIDER_FORMAT_DIFFERENCE_IS_CAPABILITY_FATAL=NO
UNIFORM_1024_CAPABILITY_GATE=RETIRED
PRODUCTION_JSON_REQUIRED_FOR_CAPABILITY_SCORE=NO
PROVIDER_SPECIFIC_SUFFICIENT_COMPLETION_HEADROOM=REQUIRED
RAW_FINAL_ANSWER_EVIDENCE=REQUIRED__SECRET_SAFE__NO_CHAIN_OF_THOUGHT
NORMALIZED_EVALUATION_VIEW=REQUIRED__IDENTITY_BOUND__FORMAT_ONLY
DEEPSEEK_NATIVE_VISION_MODEL_EXISTS=YES
DEEPSEEK_CURRENT_FIRST_PARTY_NATIVE_VISUAL_ROUTE=VERIFIED__VISION_EXP_DIRECT_IMAGE_INPUT
PAID_CALLS_CURRENTLY_PAUSED=YES__AWAITING_PROJECT_BRAIN_REVIEW
NEXT_EXPLICIT_PAID_SLOT=NONE_UNTIL_REVIEW
FIRST_FUTURE_V0_3_PROVIDER=DEEPSEEK
FIRST_FUTURE_V0_3_SLOT=V0_3:DEEPSEEK:CAPABILITY_MATCHED_001
V0_3_REMOTE_REF=refs/heads/stage-a-live-state-v0-3
OLD_KIMI_1=SUPERSEDED__DO_NOT_EXECUTE
OLD_DEEPSEEK_1=HISTORICAL__DO_NOT_RERUN
OLD_MINIMAX_1=HISTORICAL__DO_NOT_RERUN
AUTOMATIC_RETRY=FORBIDDEN
AUTOMATIC_NEXT_SLOT=FORBIDDEN
TOTAL_API_HARD_CAP_CNY=100
AUTOMATIC_RECHARGE=FORBIDDEN
OUTCOME_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

The old V0.2 live workflow is retired fail-closed before credentials/provider transport. Do not use it to run `KIMI:1` or any other V0.2 slot.

## Historical attempt compatibility

Old attempts remain immutable and are never rerun. DeepSeek old slot 1 is V0.1 history and not capability-fatal evidence.

MiniMax old slot 1 is immutable V0.2 history. Its old funnel `ELIMINATED` status is historical V0.2 operational semantics only:

```text
MINIMAX_V0_2_OPERATIONAL_FATAL_STOP=HISTORICAL_TRUE
MINIMAX_V0_3_JIANGHE_CAPABILITY_FAIL=NO_EVIDENCE
MINIMAX_V0_3_CAPABILITY_STATUS=CANDIDATE__FAIR_EVALUATION_REQUIRED
```

Any future DeepSeek/MiniMax/Kimi test must use new V0.3 identities after offline closure.

## Current research / product route

```text
traceable Jianghe human trading experience
-> source-faithful V1.1 knowledge pack
-> versioned Jianghe AI Trader identity
-> causal multi-timeframe observation + working memory
-> capability-first non-outcome real-model comparison
-> source-justified PRIMARY preparation
-> governed historical outcome research only after explicit gates
-> genuinely unseen Shadow/Forward evidence when later authorized
```

The AI is the market-reading decision brain. Deterministic infrastructure owns hard risk, orders, execution truth, reconciliation and Safety. UNKNOWN, contradiction, unfamiliar state or unsupported interpretation must allow WAIT/NO_TRADE rather than invention.

## After takeover: mandatory refresh rule

Before every substantive project reply:
1. fetch current `main` HEAD;
2. fetch `PROJECT_BRAIN_RUNTIME_BRIEF.md`;
3. refresh `CURRENT_STATE.md` and the specific named authority for state/architecture/locks/next work/provider/model/tool answers;
4. refresh V0.2 remote state when stating historical attempt/accounting facts;
5. once a V0.3 executable plan/ref exists, refresh it before stating executable slots or V0.3 accounting;
6. never use conversation memory as mutable authority.

## Conditional authority

- `docs/reviews/JIANGHE_RMB100_REAL_MODEL_FIDELITY_FUNNEL_V0_1.md` — historical V0.1/V0.2 funnel semantics; formatting-related fatal-stop logic does not govern V0.3 capability elimination.
- `docs/reviews/JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md` — input/stimulus baseline unless V0.3 versions an affected identity.
- `docs/reviews/JIANGHE_STAGE_A_LIVE_LANE_PROJECT_BRAIN_ACCEPTANCE_CONTRACT_V0_1.md` — durability/CAS/secret boundary.
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` and selection-firewall authority — read before PRIMARY/outcome changes.
- `CROSS_PROJECT_OPERATING_CONTRACT.md` — cross-project governance.
- `TOOL_REGISTRY.md` — tool admission.
- closed pre-spend repair reviews — read only for dispute/audit; do not reopen rolling whole-repo audit by default.

## Verification path

```text
python -m unittest discover -s tests -v
```

Historical test counts are not current authority.