# PROJECT_BRAIN_RUNTIME_BRIEF

As of: `2026-08-27`

## Mandatory refresh

Before substantive project work:

1. refresh GitHub `main` HEAD;
2. read `PROJECT_DIRECTION.md`;
3. read `CURRENT_STATE.md`;
4. read task-specific authority/evidence;
5. for spend/execution, additionally refresh exact executable authority and Owner decision;
6. never infer current project facts from chat or stale branches.

## Current headline

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_FAILCLOSED__SLOT_CLOSED`

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

`WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`

`PAPER_EXECUTION = DEFERRED` in current V0.1.

Pinned Harness:

- version `0.1.1-rc.2`;
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`;
- project fail-closed patch under `integrations/deepseek-harness/`;
- `maxRetries = 0`.

## Current V0.1 evidence

Offline preexecution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

`V0_1_OFFLINE_PREEXECUTION_GATES = PASS`

`FULL_EXACT_SLICE_MOCK_DRY_RUN = PASS`

Sealed V0.1:

- `cu / SHFE.cu2406`;
- 20 prior days;
- 2 burn-in + 20 measurement days;
- 1998 governed wakes;
- R1 verified;
- R2 `NOT_OBSERVED` permitted by frozen design;
- real provider calls at preexecution `0`; the 2026-08-27 real smoke consumed `1` (fail-closed).

## Current three-call smoke boundary

Owner decision:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

Owner payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`

Machine authority:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

Preparation is complete and CI-verified:

- first 3 governed wakes;
- 4 causal PNGs per call;
- one provider request per wake;
- zero retries;
- forced restart after successful call 2;
- call 4 impossible;
- execution code / prompt / context / renderer identities bound;
- full 1998-call replay unauthorized.

Real provider smoke STOPPED FAIL-CLOSED on 2026-08-27 (1 real call consumed; provider `numeric_claims` schema mismatch). Evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

Machine authority is terminal (slot consumed/closed):

`status = REVOKED`

`owner_payment_confirmation = true`

`max_spend_cny = 3.00`

`max_provider_calls = 3`

`max_retries = 0`

`authority_identity = 6622351c707538c0db881cf69e1dbd388ae2f1c339d478e67932c65d247b3ce9`

`REAL_DEEPSEEK_PROVIDER_CALLS = STOPPED__SLOT_CLOSED__NO_AUTHORITY_TO_RERUN`

`NEXT_EXPLICIT_PAID_SLOT = NEW_OWNER_AUTHORITY_REQUIRED`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

## Approved post-V0.1 roadmap

Authority:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

Architecture:

`docs/architecture/JIANGHE_EXECUTION_AND_PROMOTION_ARCHITECTURE_V0_1.md`

This roadmap applies **only after formal V0.1 closure** and must not alter current V0.1.

Headline:

```text
V0.1 closure
-> CU ~1 month historical capability replay
-> RB ~1 month historical capability replay
-> CU/RB comparative analysis
-> conditional RB regime supplementation
-> REAL-TIME PAPER
-> constrained RMB ~100k / RB / max-1-lot real-money candidate
-> evidence-governed later widening
```

Shadow is optional diagnostic mode, not mandatory promotion stage.

Paper exit is event/gate based, with ~10 effective trading days only as the earliest review reference.

RMB ~100k is a capital envelope, not a risk budget. RB is a candidate, not a profitability conclusion.

## Exact next task

`NEXT_TASK = OWNER_DECISION_REQUIRED_AFTER_FAILCLOSED_PROVIDER_SMOKE`

The three-call smoke slot is CLOSED (fail-closed after 1 real call). Do not add another offline research gate. Do not jump to post-V0.1 implementation before V0.1 closure.

## Current locks

- three-call provider smoke: CLOSED/REVOKED after fail-closed (evidence `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`); any re-run needs a new Owner paid authority;
- full V0.1 1998-call replay: locked;
- post-V0.1 CU/RB paid replays: locked;
- historical execution/PnL semantics: not yet approved;
- learning/policy promotion: locked;
- SHADOW: locked;
- PAPER/account connection: locked;
- broker/account actions: locked;
- permanent numeric risk rules: locked;
- real money/funding/orders: locked;
- automatic product/size/capital widening: locked.