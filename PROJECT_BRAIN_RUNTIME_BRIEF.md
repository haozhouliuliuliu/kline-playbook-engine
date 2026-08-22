# PROJECT_BRAIN_RUNTIME_BRIEF

> Purpose: compact live pointer for the project brain. This file reduces reliance on chat memory and avoids re-reading the full repository authority on every reply.
> Status: LIVE_POINTER / NOT_A_REPLACEMENT_FOR_FORMAL_AUTHORITY

## Mandatory runtime rule

For every **substantive project reply** after takeover:

1. fetch the current `main` HEAD;
2. fetch this file from current `main` **before answering**;
3. do not rely on chat memory, handoff text, or prior-turn assumptions for mutable project facts;
4. if `main` contains material project-state changes newer than `LAST_MATERIAL_STATE_COMMIT`, or the question concerns current state / architecture / locks / next work / worker prompts / model or tool adoption, also refresh `CURRENT_STATE.md` and the specific authority named there before answering;
5. narrow conceptual or explanatory replies may use this compact pointer plus already-fetched stable authority when no mutable fact is involved.

A fresh project-brain conversation still follows the full read-only takeover process in `00_READ_FIRST.md`. This file is the lightweight **post-takeover refresh surface**, not a shortcut around takeover verification.

## Update ownership

`main` integration lane owns this file.

Update it whenever a `main` change materially changes any of:
- current work package / next normal phase;
- architecture direction;
- authorization locks;
- Jianghe source / PRIMARY / fidelity status;
- adopted model/tool/provider;
- candidate outcome / Validation / Final / Shadow / Broker / real-money authority.

`LAST_MATERIAL_STATE_COMMIT` points to the latest substantive code/research/state commit this brief has incorporated. Later documentation-only commits that merely update this brief do not make the marker stale.

Keep this file short. Detailed evidence stays in `CURRENT_STATE.md`, ADRs, protocols, tests, and evidence artifacts.

## Current live pointer

```text
LAST_MATERIAL_STATE_COMMIT=4e17509e0c12c86d0966e6920d3fb0ddb2f6e7c2
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
JIANGHE_SOURCE_DISTILLATION=V1_1_EXHAUSTIVE_SECOND_PASS_COMPLETE
JIANGHE_SOURCE_ONLY_VERIFIED=YES
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1=INTEGRATED_NON_OUTCOME
JIANGHE_AI_OBSERVATION_REPLAY_V0_2=INTEGRATED_SYNTHETIC_NON_OUTCOME
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
JIANGHE_AI_REPLAY_SCOPE=SYNTHETIC_NON_OUTCOME_ONLY
STRATEGY_SOURCE_EXPANSION=PAUSED_FOR_V1
CURRENT_NORMAL_WORK=REAL_MODEL_FIDELITY_CANDIDATE_EVALUATION_PLUS_SOURCE_JUSTIFIED_PRIMARY_BRANCH_WORK_WITHOUT_CANDIDATE_OUTCOMES
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

Current integration inputs (2026-08-23):
- fidelity fixture/scoring corpus (`research/jianghe-ai-fidelity-fixtures-v01` @ `2cf678d`) — **integrated to `main`**;
- local WorkBuddy observation/replay implementation (four files, protection commit `2d885a5`) — **integrated to `main`**.

After those were safely integrated, this pointer was updated in the same integration task.
Next normal phase: real-model fidelity candidate evaluation + source-justified PRIMARY branch work, all WITHOUT candidate outcomes.
