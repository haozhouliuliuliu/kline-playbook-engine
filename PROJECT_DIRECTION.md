# PROJECT_DIRECTION

As of: `2026-08-27`

This file is the binding current product/research direction for `kline-playbook-engine`.

## 1. Mission

Build one persistent, auditable China-futures AI trader whose active model source is DeepSeek, whose initial trading foundation is Jianghe's documented experience, and whose long-run improvement is governed rather than self-promoted.

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

## 2. Cognitive and system boundary

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

DeepSeek interprets the causal market, applies Jianghe evidence and permitted memory, identifies setup/state/levels/triggers/invalidation, and returns the normalized trading judgment.

Project-owned deterministic systems control data eligibility, wake timing, replay/real-time clock, charts, context assembly, persistence, provider routing, retries, schema normalization, risk, orders, broker/account truth, reconciliation, kill switches, audit and governance.

## 3. Knowledge hierarchy

- `JIANGHE_CANON`: read-only source-grounded truth.
- `PROJECT_VALIDATED_POLICY`: independently validated extensions.
- `DS_HYPOTHESIS_MEMORY`: non-executable candidate ideas.
- `DS_WORKING_MEMORY`: persistent current market state.
- `DS_JOURNAL`: auditable reflection, not source truth or active policy.

Promotion path remains:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

## 4. Current active V0.1

Current authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Current smoke decision:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_ACTIVE__THREE_CALL_SLOT`

Frozen V0.1:

- sealed product `cu`, contract `SHFE.cu2406`;
- 20 prior-history days;
- 2 burn-in + 20 measurement days;
- 1998 governed closed-5m wakes;
- `WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`;
- causal `4H / 1H / 15m / 5m` observation;
- one persistent trader;
- intent-only lifecycle;
- `PAPER_EXECUTION = DEFERRED`;
- no amount PnL/win-rate/outcome feedback in decision context;
- no outcome-driven rerun;
- no learning/policy promotion.

The post-V0.1 roadmap must not alter these semantics.

## 5. Current evidence and paid boundary

`V0_1_OFFLINE_PREEXECUTION_GATES = PASS`

`FULL_EXACT_SLICE_MOCK_DRY_RUN = PASS`

Three-call provider-smoke preparation is `READY` and CI-verified.

Owner payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`

Current machine authority is ACTIVE for this exact sealed slot:

`status = ACTIVE`

`owner_payment_confirmation = true`

`max_spend_cny = 3.00`

`max_provider_calls = 3`

`max_retries = 0`

`REAL_DEEPSEEK_PROVIDER_CALLS = AUTHORIZED_FOR_THIS_EXACT_THREE_CALL_SLOT_ONLY`

`NEXT_EXPLICIT_PAID_SLOT = THREE_CALL_PROVIDER_SMOKE__EXECUTION`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

Full V0.1 1998-call replay remains unauthorized.

## 6. Post-V0.1 staged direction

Owner-approved roadmap authority:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

Execution architecture:

`docs/architecture/JIANGHE_EXECUTION_AND_PROMOTION_ARCHITECTURE_V0_1.md`

After formal V0.1 closure, normal route is:

```text
CU ~1 trading month chronological historical capability replay
-> RB ~1 trading month chronological historical capability replay
-> CU/RB focused comparative analysis
-> conditional RB regime supplementation only when evidence gaps justify it
-> REAL-TIME PAPER
-> constrained real-money candidate: RMB ~100,000 capital envelope / RB / max 1 lot
-> evidence-governed later widening only by new authority
```

Product-level strategy:

`HISTORICAL HIGH-SPEED REPLAY + REAL-TIME PAPER EXECUTION + MINIMAL-CONSTRAINED REAL-MONEY VALIDATION`

## 7. Initial historical research rules

CU and RB initial windows must be chronological, causal and outcome-blind.

Adopted roadmap selector:

`POST_V0_1_FORWARD_FIRST_ELIGIBLE_ALIGNED_WINDOW_V0_1`

- fixed scan anchor is strictly after current V0.1 measurement end `2024-05-14`;
- CU takes first eligible metadata-only 2+20 block with one unchanged governed contract;
- RB first attempts those same trading dates if mechanically eligible; otherwise takes the first eligible 2+20 block from the same anchor;
- selection never inspects Jianghe performance or market attractiveness;
- exact slices must be separately sealed before any paid calls.

Post-V0.1 historical execution/PnL evaluation is allowed only after a separate authority freezes causal fill/slippage/fee semantics; execution outcomes remain outside same-wake model cognition.

## 8. Product scope

Default paid research priority after V0.1:

`CU -> RB -> conditional RB supplemental regimes`

AU/AG/AL/NI are not default paid work. They may be proposed later only for a material unanswered generalization question.

RB is the likely first real-money candidate under the Owner's approximately RMB 100,000 capital envelope because of one-lot granularity considerations. This is not a finding that RB is most profitable or most stable.

## 9. Real-time execution direction

Target execution modes:

`SHADOW / PAPER / REAL`

Normal promotion path:

`HISTORICAL REPLAY -> REAL-TIME PAPER -> CONSTRAINED REAL MONEY`

`SHADOW` is optional diagnostic/fault-isolation/safe-degradation capability, not a mandatory stage.

Paper should reuse the future real execution chain: real-time data -> Jianghe cognition -> deterministic risk -> OMS/order adapter -> paper account -> acknowledgement/fill/cancel/reject -> position/account reconciliation -> MANAGE/EXIT -> audit.

## 10. Paper exit principle

Approximately 10 **effective** trading days is the earliest review point, not a pass rule.

`TIME_COVERAGE != SUFFICIENT_EVIDENCE`

Paper exit requires sufficient evidence across causal ingestion, session transitions, restart continuity, model/execution state consistency, lifecycle coverage, order acknowledgement/fill/cancel/reject paths, reconciliation, duplicate prevention, risk rejection, fail-closed provider/data/execution errors and complete audit.

If 20+ days still provide insufficient decision/trade/event coverage, paper is not automatically promoted.

## 11. Constrained real-money direction

Future candidate only; not currently authorized:

`CAPITAL_ENVELOPE ~= RMB 100,000`

`PRODUCT = RB`

`MAX_POSITION = 1 LOT`

RMB 100,000 is the account/capital envelope, not a risk allowance. No automatic add-on or product expansion is allowed. Deterministic risk and reconciliation have final authority.

Before REAL, a formal capital-adequacy/minimum-viable-capital analysis must evaluate actual Jianghe invalidation distances, one-lot risk, margin/headroom, fees/slippage, stress/gap exposure and drawdown behavior. If one lot violates approved risk constraints, the correct result is no trade/capital inadequate.

Permanent numeric risk rules remain an Owner decision.

## 12. Promotion evidence semantics

Always distinguish:

- `SYSTEM_READY`;
- `TRADER_BEHAVIOR_ACCEPTABLE`;
- `RISK_COMPATIBLE`;
- `EVIDENCE_SUFFICIENT`;
- `PROFITABILITY_EVIDENCE`;
- `LONG_TERM_EDGE_EVIDENCE`.

Paper profit or 10 no-loss days is not sufficient for real money. A short window also cannot be required to prove long-term statistical edge before a minimal constrained real-money validation may ever be considered.

## 13. Provider/cost direction

Pricing reference:

`docs/evidence/DEEPSEEK_PROVIDER_PRICING_REFERENCE_2026-08-27.md`

Cost is controlled per paid work package by sealed wake/request count, actual usage ledger, explicit Owner CNY ceiling and a stop-before-next-request guard. The public `deepseek-v4-flash` tariff is not assumed to be the exact tariff of the active `deepseek-v4-flash-vision-exp` model unless verified.

“CU + RB about CNY 400” remains a planning hypothesis, not a fact or blanket spend authority.

## 14. Current authorization boundary

Current next task:

`NEXT_TASK = EXECUTE_THREE_CALL_PROVIDER_SMOKE`

Authorized for this exact sealed slot only:

- three-call provider smoke: ACTIVE (owner_payment_confirmation=true, max_spend_cny=3.00, max 3 calls, 0 retries, execution authority `docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`);

Still locked:

- full 1998-call V0.1 replay;
- post-V0.1 paid CU/RB replays;
- historical execution/PnL semantics until separately approved;
- SHADOW;
- PAPER/account connection;
- broker/account writes;
- permanent numeric risk rules;
- real money / funding / real orders;
- product/position/capital widening.