# ARCHITECTURE_BASELINE

Status: `CURRENT`

Product direction authority: `PROJECT_DIRECTION.md`

## 1. Core runtime

```text
Market Data
-> Rolling Market State
-> Attention / Wake Policy
-> Causal Multi-Timeframe Observation
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
-> Broker Reports
-> Reconciliation
-> Safety
-> Immutable Ledger
```

The AI interprets markets and proposes discretionary intent. Deterministic project code owns capital/risk limits, broker/account truth, order lifecycle, reconciliation, safety and kill-switch behavior.

## 2. Model/runtime boundary

`MODEL_SOURCE = DEEPSEEK_ONLY`

Current selected model line:

`deepseek-v4-flash-vision-exp`

Production-facing model integration is DeepSeek-specific. A runtime shell may host sessions, tools and UI, but trading knowledge, memory schema, validation semantics, evidence and hard-risk logic remain project-owned and portable.

## 3. Observation semantics

Current active view stack:

`4H / 1H / 15m / 5m`

4H role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

Decision-time observations are causal: no future bar/content enters before its governed `available_at`.

Historical replay baseline uses completed 1-minute bars and does not invent sub-minute paths from 1-minute OHLC.

## 4. Persistent trader state

Project-owned persistent state includes:

- instrument/session attention state;
- timeframe interpretations;
- active market hypotheses;
- key/watch/invalidation regions;
- family/setup candidate;
- expected trigger;
- open questions / UNKNOWNs;
- prior meaningful decisions still relevant;
- journal/reflection records;
- unvalidated DeepSeek hypotheses;
- validated project policy extensions.

Every mutation is attributable and auditable. Runtime restart must preserve governed working state.

## 5. Knowledge separation

- `JIANGHE_CANON` — source-grounded and read-only to the AI;
- `PROJECT_VALIDATED_POLICY` — independently validated project extensions;
- `DS_HYPOTHESIS_MEMORY` — candidate ideas, not executable policy;
- `DS_WORKING_MEMORY` — current market state/hypotheses;
- `DS_JOURNAL` — reflective notes, never source truth.

Retrieval assembles bounded relevant context. Context-selection policy is versioned as part of trader identity.

## 6. Trader identity

`JiangheAITraderIdentity` binds all outcome-affecting components, including:

- Jianghe knowledge identity;
- project-validated policy identity;
- DeepSeek model/version;
- prompts;
- context-selection policy;
- memory policy/schema;
- chart renderer;
- observation schema;
- wake policy;
- decision schema/normalizer;
- mechanical guards;
- inference configuration;
- tool capability set.

A material change creates a new trader version/descendant with preserved exposure lineage.

## 7. Mechanical guards

### `STRICT_OUTPUT_ENUM_ENFORCEMENT`

Machine fields such as action, direction and family use exact allowed enum values. Explanatory prose belongs in separate fields.

### `NO_4H_EXACT_VOLUME_RECONCILIATION`

The runtime does not sum or reconcile overlapping lower-timeframe volume into 4H volume or use that equality as a trading fact under the current 4H contract.

## 8. Learning architecture

Required promotion path:

```text
Observation
-> Falsifiable DS Hypothesis
-> Counterexample Search
-> Development Evidence
-> Independent Validation
-> Project-Validated Policy
```

Discovery exposure and redesign history remain recorded. Outcome and process correctness remain separate.

## 9. Chronological replay

Historical data is a simulated life for one persistent trader. Time advances forward; memory and prior decisions influence later decisions according to the frozen memory policy. Deterministic attention/wake logic controls model calls.

Conceptual attention states:

`SCAN -> WATCH -> CANDIDATE -> IN_POSITION`

## 10. DeepSeek Harness admission

`DEEPSEEK_HARNESS = CANDIDATE_FOR_PROJECT_ADMISSION`

A pinned build must prove:

- exact selected model route;
- K-line image/vision support;
- persistent session/state across restart;
- project-owned memory integration;
- project-owned K-line/retrieval tools;
- full request/response/memory audit;
- no silent retry/model/prompt mutation;
- portability of core trader logic.

## 11. UI target

Owner-facing UI should expose synchronized 4H/1H/15m/5m charts, current interpretation/action/family, key/watch/invalidation regions, what the trader is waiting for, retrieved Jianghe evidence, working memory, recent decisions, journal/hypothesis status and authorized deterministic system status.

## 12. Safety and authorization

Safety is fail-closed and overrides AI intent. Current authorization is defined by `CURRENT_STATE.md`; architecture alone grants no validation, shadow, broker/account or real-money permission.
