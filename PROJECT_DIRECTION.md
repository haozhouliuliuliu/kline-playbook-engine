# PROJECT_DIRECTION

Status: `CURRENT_PRODUCT_AND_RESEARCH_DIRECTION`

This file owns product/research direction only. It does **not** own the current work package, current phase, current locks, current paid slot or next task. Those live only in `CURRENT_STATE.md`.

## 1. Mission

Build one persistent, auditable China-futures AI trader whose active model source is DeepSeek, whose initial trading foundation is Jianghe's documented experience, and whose long-run improvement is governed rather than self-promoted.

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

Current selected model line:

`deepseek-v4-flash-vision-exp`

Changing the model/provider direction requires explicit Owner authority. Exact provider/runtime adoption and pins live in `TOOL_REGISTRY.md`.

## 2. Cognitive and system boundary

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

DeepSeek interprets the causal market, applies Jianghe evidence and permitted memory, identifies setup/state/levels/triggers/invalidation, and returns a normalized trading judgment.

Project-owned deterministic systems control data eligibility, wake timing, replay/real-time clock, charts, context assembly, persistence, provider routing, retries, schema normalization, risk, orders, broker/account truth, reconciliation, kill switches, audit and governance.

## 3. Knowledge hierarchy

- `JIANGHE_CANON`: read-only source-grounded truth;
- `PROJECT_VALIDATED_POLICY`: independently validated extensions;
- `DS_HYPOTHESIS_MEMORY`: non-executable candidate ideas;
- `DS_WORKING_MEMORY`: persistent current market state;
- `DS_JOURNAL`: auditable reflection, not source truth or active policy.

DeepSeek may generate hypotheses but may not promote them directly into active trading policy.

## 4. Learning lifecycle

New experience-derived trading ideas follow:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

Profit is not identical to reasoning correctness. Loss is not identical to reasoning error.

Source truth, DeepSeek hypotheses and project-validated extensions remain separately labeled.

## 5. Historical replay direction

Historical model evaluation should simulate one trader moving forward through time rather than a stack of independent retrospective prompt exams.

Required principles:

- chronological and causal data visibility;
- no future information in decision-time observations;
- persistent trader identity and project-owned memory;
- attributable retrieval and audit;
- bounded context;
- outcome-blind slice selection when required by protocol;
- no silent policy promotion from replay experience.

Exact replay semantics belong to the applicable frozen Owner decision/protocol, referenced by `CURRENT_STATE.md` when active.

## 6. Product-level research route

Normal high-level route is:

`HISTORICAL HIGH-SPEED REPLAY -> REAL-TIME PAPER -> MINIMAL-CONSTRAINED REAL-MONEY VALIDATION`

The currently approved post-V0.1 roadmap authority is:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

Its strategic headline is:

- CU chronological historical capability replay;
- RB chronological historical capability replay;
- focused CU/RB comparison;
- conditional RB regime supplementation only when evidence gaps justify it;
- real-time PAPER;
- later constrained real-money candidate under separate exact authority.

This direction does not itself authorize any paid call, paper account, broker action or real money.

## 7. Initial product scope

Default paid historical research priority after the current V0.1 closes remains:

`CU -> RB -> conditional RB supplemental regimes`

AU/AG/AL/NI are not default paid follow-up products. Adding them requires a material unanswered generalization question and appropriate authority.

RB is a possible first real-money candidate under an approximately RMB 100,000 capital envelope because of one-lot granularity considerations. This is not a finding that RB is the most profitable or most stable product.

## 8. Real-time execution direction

Target execution modes:

`SHADOW / PAPER / REAL`

Normal promotion path:

`HISTORICAL REPLAY -> REAL-TIME PAPER -> CONSTRAINED REAL MONEY`

`SHADOW` is optional diagnostic/fault-isolation/safe-degradation capability, not a mandatory promotion stage.

PAPER should reuse the future real execution chain as closely as practical:

`real-time data -> Jianghe cognition -> deterministic risk -> OMS/order adapter -> paper account -> acknowledgements/fills/cancels/rejects -> position/account reconciliation -> MANAGE/EXIT -> audit`

## 9. Paper exit principle

Approximately 10 effective trading days is only an earliest review reference, not a pass rule.

`TIME_COVERAGE != SUFFICIENT_EVIDENCE`

Promotion requires enough evidence across ingestion, session transitions, restart continuity, model/execution state consistency, lifecycle coverage, acknowledgement/fill/cancel/reject paths, reconciliation, duplicate prevention, risk rejection, fail-closed provider/data/execution errors and complete audit.

## 10. Constrained real-money direction

Future candidate only; not an authorization:

- capital envelope approximately RMB 100,000;
- RB candidate;
- maximum 1 lot candidate;
- no automatic add-on or product expansion;
- deterministic risk veto;
- mandatory broker/account reconciliation;
- explicit kill switch/fail-closed handling;
- formal capital-adequacy/minimum-viable-capital analysis before activation.

RMB 100,000 is not a risk budget. Permanent numeric risk rules remain an Owner decision.

## 11. Promotion evidence semantics

Always distinguish:

- `SYSTEM_READY`;
- `TRADER_BEHAVIOR_ACCEPTABLE`;
- `RISK_COMPATIBLE`;
- `EVIDENCE_SUFFICIENT`;
- `PROFITABILITY_EVIDENCE`;
- `LONG_TERM_EDGE_EVIDENCE`.

A short profitable period cannot by itself establish long-term edge or justify real-money expansion.

## 12. Cost direction

Paid work packages require:

- a sealed request-count ceiling;
- actual usage accounting;
- explicit CNY ceiling;
- stop-before-next-request enforcement;
- exact Owner/machine execution authority.

Pricing references and exact current permission live outside this direction file.

## 13. Current-state pointer

For current work package, phase, locks, provider-execution hold/permission and next task, read only:

`CURRENT_STATE.md`
