# ARCHITECTURE_BASELINE

Status: `CURRENT`

Product direction authority: `PROJECT_DIRECTION.md`

Execution/promotion detail: `docs/architecture/JIANGHE_EXECUTION_AND_PROMOTION_ARCHITECTURE_V0_1.md`

## Core runtime

```text
Market Data
-> Rolling Market State
-> Attention / Wake Policy
-> Causal 4H/1H/15m/5m Observation
-> Context Assembler
   -> Jianghe Canon
   -> Project-Validated Policy
   -> DeepSeek Working Memory
   -> Retrieved Analogues / Cases
-> DeepSeek Trader
-> Decision Normalizer + Mechanical Guards
-> constrained TradeIntent
-> deterministic RiskGate
-> OMS / Execution Adapter
-> Reconciliation / Safety / Immutable Ledger
```

DeepSeek interprets markets and proposes discretionary intent. Deterministic project code owns capital/risk limits, broker/account truth, order lifecycle, reconciliation, safety, request accounting and kill-switch behavior.

## Model/runtime boundary

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

Pinned shell:

- version `0.1.1-rc.2`;
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`;
- project fail-closed transport patch under `integrations/deepseek-harness/`;
- general retry `maxRetries: 0`.

Deployment baseline: `LOCAL_WORKSTATION_FIRST`.

Harness hosts sessions/tools/UI but does not own core trader semantics. The trader core remains project-owned and portable.

## Observation semantics

Active stack: `4H / 1H / 15m / 5m`.

4H role: `BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`.

All decision-time observations are causal. Historical replay uses governed completed data; real-time mode must preserve the same causal availability boundary.

## Persistent trader state

Project-owned persistent state includes attention/state, timeframe interpretations, hypotheses, key/watch/invalidation regions, family/setup candidate, expected trigger, open questions, meaningful prior decisions, journal, hypothesis memory and validated-policy references.

Every mutation is attributable and auditable. Restart preserves governed working state.

## Knowledge separation

- `JIANGHE_CANON` — read-only source truth.
- `PROJECT_VALIDATED_POLICY` — independently validated extensions.
- `DS_HYPOTHESIS_MEMORY` — candidate ideas only.
- `DS_WORKING_MEMORY` — current market state/hypotheses.
- `DS_JOURNAL` — reflection, never source truth.

## Execution-mode architecture direction

Future execution modes share the same cognition/risk/OMS contracts:

`EXECUTION_MODE = SHADOW / PAPER / REAL`

- `SHADOW`: no external order; diagnostics/fault isolation/safe degradation; not a mandatory promotion stage.
- `PAPER`: real-time end-to-end execution semantics through a paper/simulation account.
- `REAL`: real broker/account adapter under exact external-risk authority.

Normal promotion path after historical research:

`HISTORICAL REPLAY -> REAL-TIME PAPER -> CONSTRAINED REAL MONEY`

Switching PAPER -> REAL should primarily change account/execution authority and adapter configuration, not trader cognition.

## OMS/reconciliation boundary

Each order intent must be idempotently bound to trader/wake/decision/risk/order identities. Restart/reconnect must reconstruct account/order truth before new risk.

Truth hierarchy:

`BROKER/PAPER ACCOUNT -> PROJECT OMS LEDGER -> PROJECT POSITION STATE -> MODEL-VISIBLE POSITION SUMMARY`

Unknown order/position/account state means no new risk and fail-closed adjudication.

## Deterministic risk boundary

RiskGate has final veto. Required future controls include product whitelist, max position, add-on permission, per-trade/daily/cumulative risk, margin/headroom, duplicate prevention, reconciliation, data/provider/runtime health and kill-switch state.

Permanent numeric limits are not defined by architecture and require Owner authority before real-money use.

## Current work package boundary

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_FAILCLOSED__SLOT_CLOSED`

Current V0.1 remains intent-only with `PAPER_EXECUTION = DEFERRED`.

The post-V0.1 roadmap is approved as future direction only. Architecture grants no provider spend beyond the exact three-call smoke slot that was executed and closed on 2026-08-27 (fail-closed; see `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`), and no shadow, paper, broker/account or real-money permission.

Current next task:

`OWNER_DECISION_REQUIRED_AFTER_FAILCLOSED_PROVIDER_SMOKE`.