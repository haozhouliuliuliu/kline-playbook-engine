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

The AI interprets markets and proposes discretionary intent.

Deterministic project code owns capital/risk limits, broker/account truth, order lifecycle, reconciliation, safety and kill-switch behavior.

## 2. Model/runtime boundary

DeepSeek is the sole active model source.

Current selected model line:

`deepseek-v4-flash-vision-exp`

Do not maintain a multi-provider runtime for removed providers.

A runtime shell such as DeepSeek Harness may host sessions/tools/UI, but it must not own the project's trading knowledge, memory schema, validation semantics, evidence or hard-risk logic. Those remain project-owned so the shell can be replaced without losing the trader.

## 3. Observation semantics

Current active view stack:

`4H / 1H / 15m / 5m`

4H current role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

4H is not an automatic trigger and must not be used for exact cross-timeframe volume reconciliation.

Decision-time observations must be causal: no future bar/content may enter before its governed `available_at`.

Historical replay baseline remains completed 1-minute bars; do not invent sub-minute paths from 1m OHLC.

## 4. Persistent trader state

The product is not a sequence of independent prompts.

Project-owned persistent state includes at least:

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

Every mutation must be attributable and auditable.

Restarting the UI/runtime must not erase the trader's governed working state.

## 5. Knowledge separation

The runtime must preserve the hierarchy defined in `PROJECT_DIRECTION.md`:

- `JIANGHE_CANON` — source-grounded and read-only to the AI;
- `PROJECT_VALIDATED_POLICY` — independently validated project extensions;
- `DS_HYPOTHESIS_MEMORY` — candidate ideas, not executable policy;
- `DS_WORKING_MEMORY` — current market state/hypotheses;
- `DS_JOURNAL` — reflective notes, never source truth.

Retrieval must assemble bounded relevant context rather than append the entire corpus/chat history to every model call.

Context-selection policy is outcome-affecting and therefore versioned as part of trader identity.

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

A material change creates a new trader version/descendant. Historical exposure/evidence is not silently reassigned to the new identity.

## 7. Mechanical guards

Current mandatory guards:

### `STRICT_OUTPUT_ENUM_ENFORCEMENT`

Machine fields such as action/direction/family must use exact allowed enum values. Explanatory prose belongs in separate fields.

### `NO_4H_EXACT_VOLUME_RECONCILIATION`

The model/runtime must not sum/reconcile overlapping lower-timeframe volume into 4H volume or use that equality as a trading fact under the current 4H contract.

These guards constrain observed failure modes; they do not invent new Jianghe doctrine.

## 8. Learning architecture

DeepSeek may functionally improve through persistent external experience without directly rewriting source truth or live policy.

Required promotion path:

```text
Observation
-> Falsifiable DS Hypothesis
-> Counterexample Search
-> Development Evidence
-> Independent Validation
-> Project-Validated Policy
```

The hypothesis/research system must record discovery exposure and redesign history to avoid disguising repeated search as one clean test.

Outcome and process correctness remain separate. Profit alone cannot promote a rule.

## 9. Chronological replay

Historical data is a simulated life for one persistent trader.

Time advances forward; memory and prior decisions may influence later decisions according to the frozen memory policy. The model is awakened only when deterministic attention/wake logic says a meaningful re-evaluation is useful.

Conceptual attention states:

`SCAN -> WATCH -> CANDIDATE -> IN_POSITION`

Potential wake events include meaningful bar close, watch-region entry/exit, breakout/failure candidate, invalidation, state transition and session events.

Large replay must not be implemented as thousands of stateless independent API exams.

## 10. Harness/runtime shell admission

DeepSeek Harness is currently a candidate runtime shell, not adopted architecture.

A pinned build must prove:

- exact selected model route;
- K-line image/vision support;
- persistent session/state across restart;
- project-owned memory integration;
- project-owned K-line/retrieval tools;
- full request/response/memory audit;
- no silent retry/model/prompt mutation;
- portability of core trader logic.

If it fails, replace the shell, not the product direction.

## 11. UI target

Owner-facing UI should eventually expose only what improves operation/reasoning:

- synchronized 4H/1H/15m/5m charts;
- current interpretation/action/family;
- key/watch/invalidation regions;
- what the trader is waiting for;
- relevant Jianghe evidence retrieved;
- working memory and recent decisions;
- journal/hypothesis status;
- later, deterministic risk/safety/account status when authorized.

UI polish and packaging are secondary to correct persistent-trader behavior.

## 12. Safety and current locks

Safety is fail-closed and overrides AI intent.

Current authorization remains in `CURRENT_STATE.md`; this architecture grants no validation/holdout, shadow, broker/account or real-money permission by itself.
