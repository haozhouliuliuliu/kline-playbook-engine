# CURRENT_STATE

As of: `2026-08-27`

## Mission

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

## Active work package

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_FAILCLOSED__SLOT_CLOSED`

`NEXT_TASK = OWNER_DECISION_REQUIRED_AFTER_FAILCLOSED_PROVIDER_SMOKE`

Current replay authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Current smoke authority:

- Owner decision: `docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`
- Owner payment/execution authority: `docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`
- machine authority: `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`
- fail-closed evidence: `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

## Frozen current V0.1

- product: `cu`;
- concrete contract: `SHFE.cu2406`;
- prior history: 20 eligible trading days;
- burn-in: 2 trading days;
- measurement: 20 trading days through `2024-05-14`;
- replay days: 22;
- governed wakes: `1998`;
- wake policy: `EVERY_NEW_CLOSED_5M_BAR`;
- observation stack: `4H / 1H / 15m / 5m`;
- one persistent trader;
- intent-only lifecycle;
- `PAPER_EXECUTION = DEFERRED`;
- no outcome-driven rerun;
- no model-visible PnL/outcome feedback;
- no learning/policy promotion.

The Owner-approved post-V0.1 CU/RB roadmap does not modify these semantics.

## Offline preexecution result

Formal evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

`V0_1_OFFLINE_PREEXECUTION_GATES = PASS`

`FULL_EXACT_SLICE_MOCK_DRY_RUN = PASS`

Real-corpus mock accounting:

`step = wake = request = mock-call = 1998`

R1 = `VERIFIED`.

R2 = `NOT_OBSERVED` as permitted by the frozen rule.

Real provider calls at preexecution = `0` (the later 2026-08-27 real smoke consumed exactly `1`; see fail-closed evidence).

## Provider smoke preparation

`PROVIDER_SMOKE_PREPARATION = READY`

CI-verified properties:

- first 3 governed wakes only;
- `max_provider_calls = 3`;
- `max_retries = 0`;
- exactly 4 deterministic causal PNGs per call;
- one governed wake -> exactly one Harness request;
- no hidden second request;
- forced project-owned restart after successful call 2 before call 3;
- exact provider/model/image/request assertions;
- execution-critical source bound to full execution commit;
- prompt/context/renderer/API-key identities bound pre-network;
- production paid endpoint cannot be overridden;
- ACTIVE spend field must be positive and finite;
- call 4 impossible;
- full 1998-call replay explicitly unauthorized.

Real three-call provider smoke executed on `2026-08-27` and STOPPED FAIL-CLOSED:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

- real provider calls attempted: `1`
- real provider calls normalized: `0`
- retries: `0`
- hidden second requests: `0`
- root cause: provider `numeric_claims` emitted as an object vs the frozen array schema
- call 4: `NO`
- full 1998-call replay: `NO`

Machine authority is now terminal (slot consumed/closed):

`status = REVOKED`

`owner_payment_confirmation = true`

`max_spend_cny = 3.00`

`max_provider_calls = 3`

`max_retries = 0`

`full_replay_1998_calls_authorized = false`

`authority_identity = 6622351c707538c0db881cf69e1dbd388ae2f1c339d478e67932c65d247b3ce9`

Therefore:

`REAL_DEEPSEEK_PROVIDER_CALLS = STOPPED__SLOT_CLOSED__NO_AUTHORITY_TO_RERUN`

`NEXT_EXPLICIT_PAID_SLOT = NEW_OWNER_AUTHORITY_REQUIRED`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

## Approved future roadmap after V0.1 closure

Authority:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

Execution architecture:

`docs/architecture/JIANGHE_EXECUTION_AND_PROMOTION_ARCHITECTURE_V0_1.md`

Future normal path:

```text
V0.1 closure
-> CU ~1 trading month chronological historical capability replay
-> RB ~1 trading month chronological historical capability replay
-> CU/RB comparative analysis
-> conditional RB regime supplementation only if evidence gaps remain
-> REAL-TIME PAPER
-> constrained RMB ~100,000 capital envelope / RB / max 1 lot real-money candidate
-> later widening only by evidence + new Owner authority
```

Initial CU/RB historical selection is deterministic/outcome-blind from a fixed post-V0.1 anchor. RB first attempts calendar alignment to the CU block and otherwise takes first mechanically eligible block.

AU/AG/AL/NI are not default paid follow-up products.

## Paper and shadow direction

Target future execution modes:

`SHADOW / PAPER / REAL`

Normal promotion path:

`HISTORICAL REPLAY -> REAL-TIME PAPER -> CONSTRAINED REAL MONEY`

Shadow is optional diagnostic/fault-isolation/safe-degradation capability, not a mandatory stage.

Paper exit is not “10 days without errors”. Approximately 10 effective trading days is only the earliest review reference; event coverage and engineering gates must also be sufficient. Twenty days with insufficient events is not an automatic pass.

## Constrained real-money direction

Future candidate only:

- capital envelope approximately RMB 100,000;
- RB only;
- maximum 1 lot;
- no automatic add-on;
- deterministic risk veto;
- mandatory broker/account reconciliation;
- explicit kill switch/fail-closed handling;
- formal capital-adequacy/minimum-viable-capital analysis before activation.

RMB 100,000 is not a risk budget. RB is not currently proven most profitable or most stable.

Permanent numeric per-trade/daily/drawdown limits are not frozen and require later Owner authority.

## Cost direction

Pricing reference:

`docs/evidence/DEEPSEEK_PROVIDER_PRICING_REFERENCE_2026-08-27.md`

Future paid packages require exact request-count ceiling, usage ledger, explicit CNY ceiling and stop-before-next-request logic. The public `deepseek-v4-flash` price is not treated as verified exact pricing for `deepseek-v4-flash-vision-exp`.

## Current locks

- current three-call smoke: pending Owner payment confirmation;
- full 1998-call V0.1 provider replay: locked;
- post-V0.1 CU/RB provider replay: locked;
- historical execution/PnL semantics: not yet approved;
- learning/policy promotion: locked;
- SHADOW: locked;
- PAPER/account connection: locked;
- broker/account actions/writes: locked;
- permanent numeric risk rules: locked;
- real money/capital funding/real orders: locked;
- automatic product, position-size or capital expansion: locked.