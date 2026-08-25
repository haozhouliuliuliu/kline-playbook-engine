# ARCHITECTURE_BASELINE

Status: `CURRENT`

Product direction authority: `PROJECT_DIRECTION.md`

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

AI interprets markets and proposes discretionary intent. Deterministic project code owns capital/risk limits, broker/account truth, order lifecycle, reconciliation, safety and kill-switch behavior.

## Model/runtime boundary

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

Runtime shell:

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

Pinned shell:

- version `0.1.1-rc.2`
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project fail-closed transport patch under `integrations/deepseek-harness/`
- general retry `maxRetries: 0`

Deployment baseline:

`LOCAL_WORKSTATION_FIRST`

The local Harness process may expose a localhost browser UI. Project-owned memory, K-line data/tools, Jianghe knowledge and trader state stay local/project-controlled. Public/cloud hosting is outside the adopted local product boundary unless later authority changes it.

Harness hosts sessions/tools/UI but does not own core trader semantics. The trader core must remain portable behind another thin shell.

## Observation semantics

Active stack: `4H / 1H / 15m / 5m`.

4H role: `BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`.

Decision-time observations are causal. Historical replay, when explicitly opened, uses completed 1-minute data and does not invent sub-minute paths.

## Persistent trader state

Project-owned persistent state includes:

- instrument/session attention state;
- timeframe interpretations;
- active market hypotheses;
- key/watch/invalidation regions;
- family/setup candidate;
- expected trigger;
- open questions/UNKNOWNs;
- prior meaningful decisions still relevant;
- `DS_JOURNAL`;
- `DS_HYPOTHESIS_MEMORY`;
- project-validated policy references.

Every mutation is attributable and auditable. Restart preserves governed working state; this was proven by the completed minimal persistent trader prototype and Owner-workstation acceptance.

## Knowledge separation

- `JIANGHE_CANON` — read-only source truth.
- `PROJECT_VALIDATED_POLICY` — independently validated extensions.
- `DS_HYPOTHESIS_MEMORY` — candidate ideas only.
- `DS_WORKING_MEMORY` — current market state/hypotheses.
- `DS_JOURNAL` — reflection, never source truth.

## Mechanical guards

- `STRICT_OUTPUT_ENUM_ENFORCEMENT`
- `NO_4H_EXACT_VOLUME_RECONCILIATION`

Both are implemented and CI verified.

## Learning architecture

`Observation -> Falsifiable DS Hypothesis -> Counterexample Search -> Development Evidence -> Independent Validation -> Project-Validated Policy`

Discovery exposure and redesign history remain recorded. Outcome and process correctness remain separate.

## Current implementation boundary

`MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1 = COMPLETE`.

The accepted local composition proves persistent project-owned memory, bounded Jianghe retrieval, causal multi-timeframe observation/charts, audited tools, journal/hypothesis separation, reconstructable request/response state, portability and fail-closed provider/runtime guards.

`CURRENT_WORK_PACKAGE = NONE__AWAITING_EXPLICIT_NEXT_WORK_PACKAGE`.

Persistent chronological replay is a future work package, not an automatic consequence of prototype completion. Architecture alone grants no replay/learning, provider-call, validation, shadow, broker/account or real-money permission.
