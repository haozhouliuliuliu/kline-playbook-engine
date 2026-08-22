# PROJECT_HANDOFF_CURRENT

> Snapshot date: 2026-08-23
> Project: `kline-playbook-engine`
> Canonical repository: `haozhouliuliuliu/kline-playbook-engine`
> Status: `CURRENT_DERIVED_HANDOFF / READ_ONLY_TAKEOVER_REQUIRED`
>
> **handoff != authority.** This file is a derived continuity snapshot, not an independent
> source of truth. If it conflicts with current Git, `CURRENT_STATE.md`, `00_READ_FIRST.md`,
> frozen protocols, Owner decisions, code/tests, or newer accepted evidence, the newer real
> repository authority wins.

## 1. Formal authority location

Read in order (per `00_READ_FIRST.md`): `OWNER_COLLABORATION_CONTRACT.md`,
`ARCHITECTURE_BASELINE.md`, `CURRENT_STATE.md`, `00_READ_FIRST.md`, `RESEARCH_DIRECTION.md`,
frozen protocol/chronology files, `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`,
`CROSS_PROJECT_OPERATING_CONTRACT.md`, `TOOL_REGISTRY.md`, `PROJECT_BRAIN_RUNTIME_BRIEF.md`,
then this handoff last. A fresh project-brain conversation starts with read-only takeover
verification and stops for Owner acceptance.

## 2. Current main

```text
MAIN=<integration lane head pushed to origin/main>
LAST_MATERIAL_STATE_COMMIT=4e17509e0c12c86d0966e6920d3fb0ddb2f6e7c2
```

Integration lane `integration/jianghe-ai-fidelity-replay-v01` is the source of the current
`main` head; the state-sync commit is the top commit.

## 3. Jianghe current identity

```text
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
JIANGHE_SOURCE_DISTILLATION=V1_1_EXHAUSTIVE_SECOND_PASS_COMPLETE
JIANGHE_SOURCE_ONLY_VERIFIED=YES
JIANGHE_PRIMARY_ELIGIBLE=NO
KNOWLEDGE_PACK_VERSION=JIANGHE_V1_1
KNOWLEDGE_PACK_IDENTITY=3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5
```

## 4. Completed integration (2026-08-23)

```text
JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1=INTEGRATED_NON_OUTCOME
JIANGHE_AI_OBSERVATION_REPLAY_V0_2=INTEGRATED_SYNTHETIC_NON_OUTCOME
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
```

Fidelity fixtures + semantic scoring core (`docs/evidence/JIANGHE_AI_FIDELITY_*`,
`src/jianghe_fidelity_scoring.py`, `tools/validate_jianghe_ai_fidelity_corpus.py`) and the
local observation/replay V0.2 (`src/jianghe_market_replay.py`, `src/jianghe_chart_renderer.py`,
V0.2 tests) are integrated into `main` as one non-outcome system over the V0.1 foundation.
Review record: `docs/reviews/JIANGHE_AI_FIDELITY_AND_REPLAY_INTEGRATION_REVIEW_V0_1.md`.
Real-model fidelity evaluation has **not** started.

## 5. Outcome locks (unchanged, all locked)

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
PERFORMANCE_RESEARCH_STARTED=NO
```

No real candidate outcome exposure has been established.

## 6. Next normal phase

```text
NEXT_NORMAL_PHASE=REAL_MODEL_FIDELITY_CANDIDATE_EVALUATION_PLUS_SOURCE_JUSTIFIED_PRIMARY_BRANCH_WORK_WITHOUT_CANDIDATE_OUTCOMES
```

All of it remains WITHOUT candidate outcomes. `PRIMARY_ELIGIBLE=NO` stays until source-justified
PRIMARY branches, UNKNOWN/source-conflict fail-closed treatment, and real-model fidelity
evidence are separately satisfied.

## 7. What the new conversation must do

First turn = read-only takeover verification report: canonical identity and current `main`/HEAD,
architecture/phase, binding research direction, frozen protocol/chronology, exact outcome locks,
current Jianghe identity (above), integrated fidelity/replay status, active limitations from
`KNOWN_LIMITATIONS_AND_TECH_DEBT.md`, and any contradiction/stale pointer found. Then stop for
Owner acceptance; do not start the next package before acceptance.

This file does not pre-authorize candidate outcomes, validation, final holdout, Shadow/Forward,
broker, real money, paid source access, or a new research direction.
