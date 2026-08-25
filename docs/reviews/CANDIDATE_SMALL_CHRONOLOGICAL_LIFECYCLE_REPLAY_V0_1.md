# CANDIDATE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1

Status: `CANDIDATE__NOT_AUTHORITY__NO_EXECUTION_PERMISSION`

Prepared from main: `83b97f90e62783911eaf23c08ac3d287b5e320b2`

Candidate branch: `research/candidate-small-chronological-lifecycle-replay-v0-1`

## 1. Why this candidate exists

The minimal persistent DeepSeek trader prototype is complete and locally accepted. The next scientifically useful step is not a profitability backtest and not learning. It is a small chronological lifecycle replay that asks whether the same governed trader can walk forward through real historical market time with stable identity, persistent memory, causal observations, attributable retrieval, deterministic state transitions and reconstructable model/tool activity.

This document is deliberately a candidate. It does not open replay, paid provider execution, learning, validation, shadow, broker/account or real-money lanes.

## 2. Primary research question

Can one fixed `JiangheAITraderIdentity` move forward through a bounded real historical segment as one persistent trader without future leakage, memory reset, hidden extra model requests, policy self-promotion or audit gaps?

This first replay is a lifecycle/runtime study. It is not designed to establish profitability, generalization or final wake-policy efficiency.

## 3. Key design principle: remove call scarcity as a confound

Owner direction for research quality: there is no artificial model-call ceiling when additional calls are genuinely useful to obtain the best test result. This is not permission to waste money.

Therefore the first lifecycle replay should not optimize for minimum DeepSeek calls. Sparse/event-optimized wake policy would create a second confound: if the trader misses an important transition, we could not tell whether the trader reasoning failed or the wake policy simply failed to call it.

Candidate baseline wake policy for this lifecycle study:

- one model wake on every newly available closed `5m` bar during governed trading sessions;
- `15m` / `1H` / `4H` context refresh occurs causally when those bars become available, without creating duplicate model requests at the same timestamp;
- explicit session, accepted paper-position/order, watch-region and invalidation events may cause an additional wake only when they occur at a distinct causal time;
- exactly one admitted model request per logged wake decision;
- no retries, hidden second requests or silent model substitution.

A later work package may study attention/wake compression. This first replay should not simultaneously optimize call efficiency and judge trader reasoning.

## 4. Historical slice: outcome-blind deterministic selection

Use only the accepted canonical corpus and governed point-in-time mapping.

Candidate selection rule:

1. product = `cu`, chosen mechanically as the first product in the canonical frozen product ordering, not after looking at replay outcomes;
2. resolve the research symbol through the existing E07 source-governed PIT mapping seam to a concrete contract;
3. scan forward from the beginning of the accepted 2024 corpus until there are at least 20 prior eligible trading days available for chart/context warm history;
4. choose the first subsequent contiguous window containing 2 burn-in trading days plus 20 measurement trading days for which the E07 mapped concrete contract does not change and required canonical partitions/session metadata are complete;
5. selection code may inspect only eligibility/mapping/calendar/data-completeness facts, never prices, returns or candidate outcome.

The fixed slice identity, mapping identity, concrete contract, partition identities and trading days must be written before any real DeepSeek replay request.

Why avoid a roll in V0.1: contract-roll lifecycle is valuable but is a separate confound. First prove one persistent trader on one governed concrete-contract segment; later explicitly test roll continuity.

## 5. Burn-in and measurement

### Burn-in: 2 trading days

- real causal DeepSeek observation/reasoning is allowed if/when provider execution is separately authorized;
- working memory, journal and candidate hypotheses may persist;
- ENTER execution is disabled during burn-in;
- no profitability/result judgment;
- purpose: avoid measuring a totally blank-memory cold start as if it were normal trading behavior.

### Measurement: 20 trading days

- continue with the exact same trader identity and persistent state;
- no reset between burn-in and measurement;
- constrained decisions may progress through `SCAN / WATCH / CANDIDATE / IN_POSITION / COOLDOWN` according to existing transition rules;
- deterministic paper execution may be used only if its exact historical semantics are admitted for this package;
- model must not receive future prices or amount PnL as decision input;
- all replay state is local/project-owned.

The 20-day length is a lifecycle-debug window, not a statistical claim of edge.

## 6. Observation and causality

At each wake:

- world clock moves only forward;
- baseline historical evidence comes from completed canonical `1m` bars;
- visible K-line stack remains `4H / 1H / 15m / 5m`;
- 4H remains `BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`;
- no observation bar may have `available_at` after decision time;
- no visual artifact may contain future bars;
- no invented sub-minute path;
- the exact observation identity and rendered artifact identities are bound to the request.

The existing `ReplayClock` / `JiangheMarketReplay` safety semantics should be reused rather than replaced.

## 7. Knowledge and memory rules

Allowed context layers:

- read-only `JIANGHE_CANON`;
- `PROJECT_VALIDATED_POLICY` only if already independently validated and active;
- persistent `DS_WORKING_MEMORY`;
- persistent `DS_JOURNAL`;
- persistent `DS_HYPOTHESIS_MEMORY` as non-executable candidate material.

Forbidden:

- DeepSeek rewriting Jianghe canon;
- a hypothesis self-promoting into active policy;
- replay outcome automatically changing validated policy;
- post-hoc human edits to memory during a run;
- restarting with a cleaned memory state after an inconvenient decision.

Journal/reflection may use only information causally available at that replay time.

## 8. Real provider execution seam required before paid replay

Current prototype runtime intentionally has no provider transport and hard-locks `provider_call_authorized = false`.

Before any real replay request, a separate explicit execution seam must be added/reviewed that preserves:

- sole active model `deepseek-v4-flash-vision-exp`;
- pinned Harness `0.1.1-rc.2` / `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`;
- mandatory project fail-closed patch;
- `maxRetries = 0`;
- no hidden second request;
- prompt/model identity binding;
- append-only request/response audit;
- local workstation execution.

Provider authorization must be explicit for the adopted replay package. Candidate design work itself makes zero provider calls.

## 9. Spend policy candidate

Research-quality rule:

`NO_ARTIFICIAL_CALL_CAP__NO_WASTEFUL_CALLS`

Interpretation:

- do not truncate or distort the scientifically preferred wake design merely to reduce API count;
- every paid call must correspond to a governed wake and create unique replay information;
- no duplicate retries, repeated 'just to see' calls on the same state, parallel model variants, or outcome-driven re-asking unless separately designed as an experiment;
- record request count and provider cost as evidence, but do not use a budget ceiling as an acceptance criterion.

## 10. V0.1 acceptance criteria

The lifecycle replay passes as an engineering/research-lifecycle proof only if all of the following hold:

1. fixed trader identity remains unchanged for the run;
2. fixed historical-slice identity is declared before real model execution;
3. replay clock never moves backward;
4. zero future-data/visual leakage;
5. wake log is complete and deterministic from admitted events;
6. provider request count exactly matches authorized model wakes; no hidden extras;
7. every request/response is reconstructable;
8. every Jianghe retrieval is bounded and attributable;
9. every tool call/result is audited;
10. working memory continuity survives the full run and at least one deliberate process restart checkpoint;
11. journal remains separate from fact/policy;
12. hypothesis memory remains non-executable and cannot self-promote;
13. strict output enum remains active;
14. no 4H exact volume reconciliation remains active;
15. all attention/decision transitions satisfy existing transition rules;
16. no manual state reset or post-hoc prompt/model mutation during the run;
17. if provider execution fails, fail closed; do not silently retry or substitute;
18. final portable export can reconstruct project-owned core state without Harness opaque session dependence.

Profit, hit rate and return are descriptive only in V0.1 and are explicitly NOT pass/fail criteria.

## 11. Failure taxonomy

A failed decision is not automatically a failed replay.

Classify failures separately:

- `CAUSALITY_FAILURE` — future information leaked;
- `IDENTITY_FAILURE` — model/prompt/context policy/trader identity drifted;
- `WAKE_FAILURE` — governed wake missing/duplicated;
- `TRANSPORT_FAILURE` — hidden retry/extra request/substitution/provider inconsistency;
- `MEMORY_FAILURE` — state reset/corruption/non-causal mutation;
- `RETRIEVAL_FAILURE` — non-attributable/unbounded/forbidden knowledge access;
- `STATE_MACHINE_FAILURE` — illegal attention/decision transition;
- `EXECUTION_SIMULATION_FAILURE` — deterministic paper semantics disagree with admitted rules;
- `AUDIT_FAILURE` — cannot reconstruct an outcome-affecting step;
- `TRADER_REASONING_ERROR` — runtime is valid but the model made a poor/contradictory judgment.

Only the last category is primarily 'the trader thought badly'; the others are system/research-integrity defects.

## 12. What V0.1 must not conclude

Even a perfect lifecycle run does not prove:

- profitable edge;
- generalization across six products;
- robustness across regimes;
- optimal wake policy;
- safe live trading;
- validated learning;
- production readiness.

## 13. Proposed sequence after design adoption

1. freeze replay design and deterministic slice selector;
2. implement offline selector + replay orchestrator + audit invariants with mock provider;
3. run no-provider dry rehearsal over the exact selected slice;
4. independently verify zero leakage and request-count semantics;
5. open one explicit local paid DeepSeek replay execution authority;
6. run 2-day burn-in + 20-day measurement without resets;
7. seal evidence before interpreting trading quality;
8. perform lifecycle audit first, trading-reasoning review second;
9. stop and decide whether a second replay design is warranted.

No learning/policy promotion is part of this candidate.

## 14. Open design questions for independent review

External reviewer should challenge especially:

- dense every-5m wake versus alternative baseline;
- 2-day burn-in adequacy;
- 20-day measurement length for lifecycle debugging;
- outcome-blind slice selection rule;
- whether deterministic paper execution should be included in V0.1 or deferred;
- whether the first replay should allow `DS_JOURNAL` and `DS_HYPOTHESIS_MEMORY` mutation, and under what causal information boundary;
- restart checkpoint placement;
- failure taxonomy and acceptance criteria;
- any leakage path not covered above.
