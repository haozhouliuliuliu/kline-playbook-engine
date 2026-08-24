# 00_READ_FIRST

Canonical repository:

```text
REPOSITORY_FULL_NAME=haozhouliuliu/kline-playbook-engine
```

This file owns the **active read order**. Current GitHub `main` is the only dynamic project fact source. Do not reconstruct current state from chat memory, Project uploads, personal memory, old branches, stale handoffs, or historical review snapshots.

## Fresh-conversation takeover

A fresh project-brain conversation starts with **read-only takeover verification**.

**This file must be the first repository file read.** After reading it, fetch current `main` HEAD and read the active core below in order.

### Active core — read in this order

1. `OWNER_COLLABORATION_CONTRACT.md` — stable Owner collaboration rules.
2. `PROJECT_BRAIN_RUNTIME_BRIEF.md` — compact current live pointer; refresh surface before substantive replies.
3. `CURRENT_STATE.md` — detailed mutable current project authority.
4. `ARCHITECTURE_BASELINE.md` — consolidated current architecture and product boundary.
5. `RESEARCH_DIRECTION.md` — current Jianghe / Human Playbook First direction.
6. `docs/research/JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md` — AI Trader identity / replay / PRIMARY-compatibility / fidelity governance.
7. `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md` — current Jianghe source authority; follow its internal read order only as deeply as the task needs.
8. `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` — unresolved limitations only; LIMIT-012 is the active real-model fidelity limitation.
9. `docs/reviews/JIANGHE_RMB100_REAL_MODEL_FIDELITY_FUNNEL_V0_1.md` — current bounded Stage-A fatal-stop / advancement / budget semantics.
10. `docs/reviews/JIANGHE_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_OWNER_DECISION.md` — Owner-approved current Stage-A provider-response experiment design.
11. `docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_2.json` — current machine-readable V0.2 plan, carry-forward accounting and executable-slot authority.
12. `docs/reviews/JIANGHE_STAGE_A_V0_2_INTEGRATION_AND_REMOTE_BOOTSTRAP_CLOSURE_V0_1.md` — V0.2 integration/bootstrap closure; historical bootstrap head may be superseded by later attempt commits, so use `CURRENT_STATE.md` for the current remote head.
13. `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md` — immutable first paid-attempt evidence/adjudication.
14. `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_002_MINIMAX_ADJUDICATION_V0_1.md` — immutable second paid-attempt evidence and MiniMax fatal-stop adjudication.
15. `PROJECT_HANDOFF_CURRENT.md` — derived continuity pointer; **read last** and use only to cross-check current authority.

### Takeover-turn report

During the first takeover turn, remain read-only and report at least:

1. current `main` HEAD;
2. current phase / work package / next normal phase;
3. architecture and product boundary;
4. Jianghe / PRIMARY / pre-live gate status;
5. Stage-A V0.2 plan identity, fixed remote ref and current remote execution state;
6. paid authorization/caps/expiry and current conservative Stage-A accounting;
7. Attempt 001 DeepSeek status and why it is non-retryable but not a provider fatal-fail adjudication;
8. Attempt 002 MiniMax status and why the pre-existing funnel eliminates MiniMax;
9. current remaining provider candidates and the exact next explicit slot, if current authority still names one;
10. outcome / Validation / Final / Shadow / broker / real-money locks;
11. unresolved LIMIT-012 status;
12. any authority contradiction, missing artifact, stale handoff, or main-vs-handoff mismatch.

Then stop and wait for Owner takeover acceptance. Do not start another paid call during the takeover turn.

### Read-only takeover prohibitions

Do **not** during the first takeover turn:

- modify repository files or refs;
- create worker prompts or work packages;
- dispatch/rerun a provider workflow;
- make a provider/model call or spend money;
- mutate `stage-a-live-state-v0-1` or `stage-a-live-state-v0-2`;
- inspect candidate outcome/PnL/future data;
- unlock Validation / Final / Shadow;
- change Jianghe/PRIMARY semantics;
- change provider/model set, frozen Stage-A V0.2 research semantics, or product direction;
- introduce/adopt a new tool.

## Current Stage-A anti-regression rules

While the current RMB100 Stage-A funnel is active:

```text
AUTOMATIC_RETRY=FORBIDDEN
AUTOMATIC_NEXT_SLOT=FORBIDDEN
CALLER_SELECTED_REMOTE_REF=FORBIDDEN
OUTCOME_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

A paid slot is durable-attempted as soon as the governed remote `NETWORK_ATTEMPT_STARTED` exists. Never rerun an attempted slot. A provider eliminated by the frozen funnel receives no further Stage-A calls and no recycled Stage-B budget.

The current V0.2 plan carries Attempt 001 forward rather than resetting calls/spend. Do not treat an empty V0.2 `events` list at bootstrap as zero global attempts; always use plan-bound carry-forward accounting plus V0.2 events.

## Conditional authority — read only when the task needs it

- `docs/reviews/JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md` — V0.1 input/stimulus authority inherited unchanged by V0.2; read for stimulus/track-isolation disputes or implementation detail.
- `docs/reviews/JIANGHE_STAGE_A_PREEXECUTION_HANDOFF_2026-08-24.md` — historical pre-first-call checkpoint; **not current execution state**.
- `docs/reviews/JIANGHE_STAGE_A_LIVE_LANE_PROJECT_BRAIN_ACCEPTANCE_CONTRACT_V0_1.md` — live-lane durability/CAS/secret-boundary engineering contract.
- `docs/architecture/ADR_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1.md` — architecture-boundary detail.
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` — read before PRIMARY branch design, exposure/multiplicity decisions, or outcome-bearing research design.
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` — read before outcome chronology/access work.
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md` — read when protected outcome access or firewall behavior is in scope.
- `CROSS_PROJECT_OPERATING_CONTRACT.md` — cross-project governance questions.
- `TOOL_REGISTRY.md` — only when a tool/plugin/framework admission decision is needed.
- `docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md` — frozen historical findings; read only for repair audit/dispute. BSP-001..005 and RSP-001..002 are closed and LIMIT-015 is resolved in current mutable state.
- `docs/reviews/JIANGHE_PRE_SPEND_BATCHED_REPAIR_CLOSURE_V0_1.md` — accepted repair closure evidence.
- `docs/reviews/JIANGHE_LIVE_PROBE_OWNER_SCOPE_REVISION_V0_2.md` — binding Owner provider exclusions/budget scope when a current authority requires it.
- Historical reviews/evidence — read only when a current authority points to them or a dispute/audit requires them.

Important compatibility rule: the frozen Human Playbook protocol predates the Jianghe AI decision-layer migration. For Jianghe AI Trader, its `deterministic operationalization identity/hash` language is specialized by `JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md`: deterministic **identity binding** is required; deterministic fixed-rule market decisions are not.

## After takeover: mandatory refresh rule

Before every **substantive project reply**:

1. fetch current `main` HEAD;
2. fetch `PROJECT_BRAIN_RUNTIME_BRIEF.md` from current `main`;
3. if the answer concerns current state / architecture / locks / next work / worker prompts / model/provider/tool or there is newer material state, refresh `CURRENT_STATE.md` and the specific formal authority it names;
4. for live Stage-A questions, additionally refresh the fixed V0.2 remote ref/ledger before stating attempted slots, current remote head, or accounting;
5. do not rely on conversation memory for mutable project facts.

Narrow conceptual explanations may use already-fetched stable authority when no mutable project fact is involved.

## Current research / product anti-regression rule

The active route remains:

```text
traceable Jianghe human trading experience
-> source-faithful V1.1 knowledge pack
-> versioned Jianghe AI Trader identity
-> causal multi-timeframe observation + working memory
-> non-outcome semantic + visual + structured real-model fidelity evaluation
-> source-justified PRIMARY preparation
-> governed historical outcome research only after explicit gates
-> genuinely unseen Shadow/Forward evidence when later authorized
```

The AI is the market-reading decision brain. Deterministic infrastructure owns hard risk, orders, execution truth, reconciliation and Safety.

The project is **not** authorized to mine indicators/patterns/parameter grids by historical PnL and then retrofit a human explanation. Jianghe remains the sole V1 trading knowledge source. UNKNOWN, contradiction, unfamiliar state, or unsupported interpretation must allow `WAIT` / `NO_TRADE` rather than invention.

## Mutable-state location

Do not duplicate detailed mutable status here. Current values live in:

- `PROJECT_BRAIN_RUNTIME_BRIEF.md` — compact live refresh surface;
- `CURRENT_STATE.md` — detailed current authority;
- active Stage-A plan / attempt adjudications named above;
- fixed V0.2 remote ledger for durable attempted-slot/accounting evidence.

`PROJECT_HANDOFF_CURRENT.md` is only a derived continuity aid. It never overrides current formal authority.

## Verification path

Canonical full-suite command:

```text
python -m unittest discover -s tests -v
```

Historical test counts are not current project authority.
