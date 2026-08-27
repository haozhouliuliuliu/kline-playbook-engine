# JIANGHE REPLAY V0.1 — POST-REPAIR THREE-CALL PROVIDER REVALIDATION OWNER DECISION

Status: `OWNER_REQUIRED_REVALIDATION__EXECUTION_NOT_YET_AUTHORIZED`

Date: `2026-08-27`

## 1. Owner decision

The Owner explicitly requires a fresh three-call real-provider revalidation after the structured-memory and logical/runtime wake-identity offline repair.

`POST_REPAIR_REAL_PROVIDER_REVALIDATION = REQUIRED`

This resolves the prior question of whether real-provider revalidation is needed: **yes**.

This decision does not itself activate a provider slot because the project requires a separate exact numerical CNY spend ceiling plus a freshly resealed machine-readable authority immediately before paid execution.

`OWNER_NUMERICAL_SPEND_CEILING = NOT_YET_BOUND`

`PROVIDER_EXECUTION = LOCKED_PENDING_EXACT_SPEND_AND_MACHINE_AUTHORITY`

## 2. Scientific purpose

The new three-call run is not a repeat for reassurance and is not a profitability test.

Its purpose is to verify the changed real-provider contract introduced by the offline repair:

- active response schema: `JIANGHE_RUNTIME_RESPONSE_V0_2`;
- active trading-only prompt contract: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`;
- model-supplied structured current-state snapshot fields normalize successfully;
- accepted structured trading state persists into `DS_WORKING_MEMORY`;
- the next model request receives that persisted state causally;
- restart after call 2 preserves the exact structured state into call 3;
- future provider authority binds both stable logical wake-selection identity and runtime wake identity;
- request accounting remains exactly one request per admitted wake with zero retries and no hidden request.

This revalidation does not establish profitability, execution quality, or long-term edge.

## 3. Isolation requirements

To isolate the changed prompt/schema/memory contract, the revalidation should preserve the same logical market opportunities as the previous successful smoke:

- same frozen V0.1 sealed slice;
- same product / concrete contract;
- same context-selection policy;
- same renderer;
- same provider/model line and pinned Harness/runtime path unless a current canonical tool authority requires revalidation first;
- same ordered first three logical governed wakes and exact close times;
- same forced project-owned restart after call 2;
- max provider calls = `3`;
- max retries = `0`;
- no call 4, replacement wake, or outcome-driven re-asking;
- full 1998-call replay remains unauthorized.

The new runtime wake identities are expected to differ because the approved prompt/schema/trader identity changed. The stable logical wake-selection identities must remain equal for the same logical wakes.

## 4. Required pre-execution assurance

Before a new machine slot may become ACTIVE:

1. refresh current `main`;
2. independently review the offline repair and new two-identity provider-smoke path for material correctness;
3. run deterministic preflight against the exact current execution commit;
4. reseal a **new** V0_2 two-identity machine authority; never reuse or reactivate either historical terminal slot;
5. bind the exact current prompt/schema/trader/runtime identities;
6. bind exactly three logical + runtime wake pairs and their close times;
7. bind exact request ceiling = 3, retries = 0, images per call = 4, restart after call 2;
8. bind an explicit positive numerical `MAX_SPEND_CNY` approved by the Owner;
9. only then set `owner_payment_confirmation=true` and slot status `ACTIVE`.

Any mismatch fails closed before provider credential use or network construction.

## 5. Revalidation acceptance scope

System/provider revalidation passes only if all three admitted calls satisfy the active strict response contract and all of the following are evidenced:

- `3` real provider requests, `3` accepted normalized decisions;
- `0` retries and `0` hidden/auxiliary provider requests;
- no call 4;
- exactly 4 governed PNG inputs per call;
- both logical and runtime wake identities match the fresh machine authority;
- the logical wake-selection identities match the intended same logical first-three opportunities;
- all decision-time observations remain causal with no future/outcome/PnL leakage;
- every required V0_2 structured-memory field is present with the strict allowed type;
- persisted structured state is exactly model-supplied, not parsed from rationale;
- call 2 sees the accepted state persisted from call 1;
- after the forced restart, call 3 sees the exact accepted state persisted from call 2;
- provider metadata/request accounting is durably retained before normalization failure if a failure occurs.

Any schema/normalization/request/restart/identity/state-continuity failure stops immediately with zero retry; the fresh slot is consumed/closed according to its exact authority.

Trading-quality findings (including a cautious/no-trade sequence, bad trade judgment, or imperfect Jianghe interpretation) are recorded separately and do not by themselves convert a technically valid provider-smoke run into a system-integrity PASS or FAIL unless they expose a contract/causality/memory-integrity violation.

## 6. Historical evidence preservation

Do not rewrite:

- the original failed smoke evidence;
- the successful V0_2-prompt historical retest evidence;
- either historical terminal machine authority;
- historical runtime wake hashes.

The new run must produce new authority/evidence under new identities.

## 7. Full V0.1 boundary

`FULL_V0_1_1998_CALL_REPLAY = STILL_LOCKED`

Completion of the new three-call revalidation will be adjudicated separately before any request for full V0.1 paid authority.
