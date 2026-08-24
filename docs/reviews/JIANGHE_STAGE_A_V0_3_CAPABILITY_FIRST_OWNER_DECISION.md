# JIANGHE STAGE-A V0.3 CAPABILITY-FIRST MODEL COMPARISON — OWNER DECISION

Status: `OWNER_APPROVED__CAPABILITY_FIRST__IMPLEMENTATION_AUTHORIZED__PAID_CALLS_PAUSED_UNTIL_OFFLINE_CLOSURE`
Date: 2026-08-24
Owner decision time: `2026-08-24T20:35:00+08:00`
Tool decision: `USE_EXISTING`

## 1. Binding Owner objective

The model-selection objective is no longer “which API most easily emits strict JSON under a uniform 1024-token ceiling.” The binding comparison order is:

```text
1=JIANGHE_CORRECTNESS_AND_CAPABILITY
2=ACTUAL_CNY_COST
3=ACTUAL_TIME_LATENCY
```

The test principle is:

```text
SAME_MATERIAL
SAME_QUESTION
DIFFERENT_MODEL_BRAIN
```

Capability is judged first. Cost and time are recorded and compared after answer quality is known; they are not automatic failure conditions merely because one model uses more reasoning tokens, takes longer, or costs more on a question.

## 2. Scope of the V0.3 correction

V0.3 supersedes V0.1/V0.2 **model-capability selection semantics**. It does not rewrite or delete historical attempts, spend, ledgers, evidence identities, or frozen historical plan identities.

The following equivalence is formally rejected for V0.3:

```text
NON_SCOREABLE_NORMALIZER != MODEL_CAPABILITY_FATAL_FAIL
OUTPUT_FORMAT_FAILURE != JIANGHE_CAPABILITY_FAIL
TRUNCATION != JIANGHE_CAPABILITY_FAIL
LONG_REASONING != JIANGHE_CAPABILITY_FAIL
```

JSON truncation, markdown wrapping, provider-specific final-answer formatting, an unclosed answer schema, or reasoning consuming much of an output budget are first classified as `OUTPUT_INTEGRATION_OPERATIONAL_COMPATIBILITY` problems. They do not by themselves establish poor Jianghe reasoning.

A Jianghe capability failure requires substantive evidence such as clear misunderstanding of Jianghe principles, unjustified trading where WAIT/NO_TRADE is required, invented rules/thresholds, materially wrong chart reading, forced conclusions despite unresolved visual/structured contradiction, sustained multi-question deviation from the Jianghe method, inability to consume required project inputs, or reliance on forbidden tools/search/future/outcome information.

## 3. MiniMax Attempt 002 — immutable history, corrected current meaning

Historical facts remain immutable:

```text
PROVIDER=MINIMAX
MODEL=MiniMax-M3
OLD_SLOT=1
HTTP_STATUS_CLASS=2xx
RESOLVED_MODEL=MiniMax-M3
FINISH_REASON=length
FINAL_CONTENT_STATE=TEXT_NONEMPTY
PROMPT_TOKENS=7999
COMPLETION_TOKENS=1024
REASONING_TOKEN_COUNT=914
LATENCY_MS=10364
ACCOUNTED_CNY=0.050799
TERMINAL_STATUS=NON_SCOREABLE_NORMALIZER
OLD_SLOT_RETRY=FORBIDDEN
```

The V0.2 frozen funnel did mechanically adjudicate this old attempt as an operational fatal stop. That historical statement remains true **inside V0.2**. It must no longer be promoted into a current Jianghe capability judgment.

```text
MINIMAX_V0_2_OPERATIONAL_FATAL_STOP=HISTORICAL_TRUE
MINIMAX_V0_3_JIANGHE_CAPABILITY_FAIL=NO_EVIDENCE
MINIMAX_CAPABILITY_STATUS=CANDIDATE__REQUIRES_FAIR_CAPABILITY_EVALUATION
```

Any future MiniMax test must use a new V0.3 research/slot identity. `MINIMAX:1` is never rerun.

## 4. DeepSeek Attempt 001 — immutable history

`DEEPSEEK:1` remains a real, accounted, non-retryable V0.1 attempt. V0.1 failed to preserve sufficient safe response-envelope evidence after receiving a 2xx provider JSON response. It was never valid evidence of a DeepSeek capability fatal fail.

V0.3 restarts the fair comparison **with DeepSeek first**, but only under a new V0.3 request/slot identity. It is not a rerun or replacement of `DEEPSEEK:1`.

## 5. Current candidate set

```text
DEEPSEEK=CAPABILITY_CANDIDATE__FAIR_V0_3_EVALUATION_REQUIRED
MINIMAX=CAPABILITY_CANDIDATE__FAIR_V0_3_EVALUATION_REQUIRED
KIMI=CAPABILITY_CANDIDATE__FAIR_V0_3_EVALUATION_REQUIRED
VERIFIED_PROVIDER=NONE
ADOPTED_PROVIDER=NONE
```

The prior current instruction `NEXT_EXPLICIT_SLOT=KIMI:1` is superseded. It must not be executed.

## 6. Fair-exam contract

For matched capability comparison, Kimi / DeepSeek / MiniMax receive the same governed research material:

- same Jianghe knowledge material and knowledge-pack identity;
- same context-selection principle;
- same question/task wording;
- same K-line visual bytes;
- same structured observation;
- same visible historical information and point-in-time boundary;
- same outcome/future-data prohibition;
- same no-tools/no-search requirement;
- same Jianghe trading-decision task.

Only provider-required wire syntax and provider-native/recommended reasoning controls may differ. Fairness does **not** require forcing three different reasoning models into an identical internal reasoning mechanism or an identical arbitrary completion-token ceiling.

## 7. Sufficient completion headroom

The common V0.2 `1024` completion-token ceiling is retired as a V0.3 capability gate.

Before V0.3 becomes executable, the offline builder must recheck current first-party provider documentation and set a provider-specific:

```text
SUFFICIENT_COMPLETION_HEADROOM
```

The objective is to allow normal reasoning plus a complete final answer, not intentionally create truncation. Provider ceilings may differ. Exact token ceilings become versioned inference configuration and must still have a calculable conservative cost bound within the project-wide CNY100 hard cap.

Reasoning-token count, output-token count, and latency are recorded measurements. High values are not capability failures by themselves.

## 8. Capability answer contract versus production schema

A capability test does not require direct production JSON as the admission ticket for scoring.

The requested final answer should make these semantics explicit and comparable:

```text
market_interpretation
setup_or_no_setup
action=WAIT|NO_TRADE|ENTER|MANAGE|EXIT
direction_if_applicable
evidence
invalidation_or_uncertainty
jianghe_principles_used
```

Acceptable final-answer surfaces may include valid JSON, markdown-wrapped JSON, provider-native structured output, or readable structured text, provided the **final answer semantics are complete and unambiguous**.

The project must preserve, behind the existing secret/reasoning boundary:

```text
MODEL_RAW_FINAL_ANSWER
NORMALIZED_EVALUATION_VIEW
```

The two identities must be cryptographically bound. Hidden chain-of-thought/reasoning text must not be persisted. A deterministic adapter may only transform representation; it must not add facts, repair substantive omissions, change a decision, or reinterpret model meaning.

## 9. Jianghe capability scoring

Capability scoring emphasizes:

1. Jianghe principle accuracy;
2. market-structure understanding;
3. K-line visual reading;
4. WAIT / NO_TRADE discipline;
5. absence of invented thresholds/rules;
6. honesty under uncertainty/UNKNOWN;
7. visual-versus-structured consistency;
8. hard-negative reasoning;
9. stability across matched questions/repeats when used;
10. whether the trading conclusion is actually explainable from governed Jianghe material.

After answer-quality scoring, the comparison view reports actual CNY cost and actual time/latency, plus token usage and integration convenience as diagnostic metadata. Final Owner-facing selection is based on correctness first, then cost, then time.

## 10. Failure semantics

One formatting/truncation event does not permanently eliminate a normally functioning model.

A capability candidate may be hard-stopped before further capability calls only for a clearly relevant hard failure, including unavailable model/route after verified configuration, inability to accept required project input, forbidden outcome/future/tool/search dependence, inability to stay inside the project-wide hard spend ceiling, or sufficient repeated semantic evidence that Jianghe capability is materially inadequate.

Operational/integration defects remain separately recorded and must not be relabeled as semantic capability failure.

## 11. Budget semantics

The binding project-wide API hard ceiling remains:

```text
TOTAL_API_HARD_CAP_CNY=100.00
```

The V0.1/V0.2 `STAGE_A_CNY18`, `CNY6_PER_PROVIDER`, and fixed `5_CALLS_PER_PROVIDER` limits are historical experiment-design limits and are **not V0.3 capability-comparison gates**. V0.3 may allocate fewer or more matched calls per provider as required for a fair, decisive comparison, subject to the CNY100 total hard ceiling.

Cost is measured, not optimized blindly. Unused budget remains unspent. There is no automatic recharge; any recharge remains a separate Owner cash action.

## 12. Engineering retained

V0.3 deliberately keeps the useful existing machinery:

- Jianghe knowledge pack and content identities;
- same-question / same-material identity binding;
- visual and structured input machinery;
- point-in-time/outcome firewall;
- paid-call ledger and conservative accounting;
- durable start/terminal evidence;
- duplicate-attempt prevention;
- secret protection and no-reasoning-text evidence boundary;
- request/evidence identity;
- provider adapters;
- cost/usage/latency recording.

V0.3 does not authorize a new large infrastructure program. The next implementation package is the smallest change that separates capability scoring from output-format compatibility and allows complete final answers.

## 13. Execution order and pause

Paid calls are paused until an offline V0.3 closure proves the new request/evidence/adapter path and a new V0.3 executable slot identity exists.

```text
OLD_KIMI_1=SUPERSEDED__DO_NOT_EXECUTE
OLD_DEEPSEEK_1=HISTORICAL__DO_NOT_RERUN
OLD_MINIMAX_1=HISTORICAL__DO_NOT_RERUN
NEXT_PAID_SLOT=CURRENTLY_NONE
FIRST_FUTURE_V0_3_PROVIDER=DEEPSEEK
FIRST_FUTURE_V0_3_SLOT=NEW_IDENTITY_REQUIRED
```

After the first complete DeepSeek V0.3 answer, obtain matched MiniMax and Kimi answers on the same capability fixture/material as quickly as the hard safety/accounting boundaries permit. Then compare answer quality/Jianghe fidelity, actual CNY, and actual latency together.

## 14. Locks preserved

```text
OUTCOME_ACCESS=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
AUTOMATIC_RECHARGE=FORBIDDEN
TOOL_DECISION=USE_EXISTING
```

This Owner decision is the current Stage-A model-comparison research-design authority. V0.1/V0.2 remain immutable historical experiment/evidence authorities and cannot override the V0.3 capability semantics above.