# JIANGHE REPLAY V0.1 — POST-REPAIR THREE-CALL PROVIDER REVALIDATION OWNER DECISION

Status: `OWNER_REVALIDATION_APPROVED__CALL_BOUNDED__CNY_CEILING_WAIVED__F05_FRESH_REVIEW_WAIVED_FOR_THIS_EXACT_SLOT__PROCEED_TO_RESEAL_AND_EXECUTE`

Date: `2026-08-27`

## 1. Current Owner decision

The Owner requires one fresh three-call real-provider revalidation after the structured-memory and logical/runtime wake-identity repair.

`POST_REPAIR_REAL_PROVIDER_REVALIDATION = REQUIRED`

The exact hard execution envelope is:

`MAX_PROVIDER_CALLS = 3`

`MAX_RETRIES = 0`

`NO_CALL_4 = TRUE`

`OWNER_PAYMENT_CONFIRMATION = APPROVED_FOR_THIS_EXACT_THREE_CALL_REVALIDATION`

### Scoped cost amendment

The Owner explicitly supersedes the earlier `MAX_SPEND_CNY = 3.00` requirement for this exact three-call revalidation.

For this exact slot:

- no fixed CNY ceiling is required;
- no per-request CNY spend estimator / stop-before-next-request budget guard is required;
- the machine authority must not invent a numeric CNY ceiling merely to satisfy an old schema;
- actual provider token/usage accounting must still be preserved after execution;
- the hard mechanical controls remain the three-call ceiling, zero retries, no replacement wake and no call 4.

This is a **scoped exception for this exact post-repair three-call revalidation only**. It does not amend the project's general cost direction for future paid packages.

Under the authority precedence in `PROJECT_GOVERNANCE.md`, this exact Owner decision governs this slot even though `PROJECT_DIRECTION.md` retains the project's default cost doctrine.

### Scoped F-05 independent-review waiver

After F-05 was repaired offline with zero provider attempts, the Owner explicitly directed on `2026-08-27`:

`F05_FRESH_INDEPENDENT_REVIEW = WAIVED_FOR_THIS_EXACT_THREE_CALL_REVALIDATION`

The Owner accepts the residual risk of proceeding without another independent review of the narrow F-05 execution-critical delta. This waiver is deliberate and is limited to **this exact post-repair three-call revalidation**. It does not remove the project's general independent-review doctrine for future consequential-action boundaries, research semantics, fragile infrastructure, or later paid packages.

This scoped Owner amendment supersedes the prior F-05-specific review hold for this slot. It does **not** waive any of the following mechanical gates:

- fresh deterministic preflight against the exact execution commit;
- fresh exact V0_3 machine-authority reseal against the executable commit;
- exact active prompt/schema/model/Harness/data bindings;
- `MAX_PROVIDER_CALLS = 3`;
- `MAX_RETRIES = 0`;
- no replacement wake;
- no call 4;
- durable attempt accounting;
- fail-closed terminalization after any real-attempt failure or ambiguity;
- full V0.1 remaining locked after this three-call slot.

## 2. Scientific purpose

The new three-call run is an execution-path / model-contract revalidation, not a profitability test.

It must verify:

- active response schema: `JIANGHE_RUNTIME_RESPONSE_V0_2`;
- active trading-only prompt: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`;
- model-supplied structured current-state fields normalize successfully;
- accepted structured trading state persists into `DS_WORKING_MEMORY`;
- call 2 receives call-1 persisted state causally;
- forced project-owned restart after call 2 preserves exact state into call 3;
- both stable logical wake-selection identity and runtime wake identity are enforced and evidenced;
- exactly one governed provider request is admitted per wake, with zero retries and no hidden request.

This revalidation does not establish profitability, execution quality or long-term edge.

## 3. Isolation requirements

Preserve:

- the same frozen V0.1 sealed slice;
- product / contract: `cu` / `SHFE.cu2406`;
- the same context-selection policy;
- the same renderer;
- the adopted DeepSeek provider/model line and pinned Harness path;
- the same ordered first three logical governed wakes and exact close times;
- forced project-owned restart after successful call 2 before call 3;
- exactly four governed causal PNGs per call;
- max provider calls = `3`;
- max retries = `0`;
- no call 4, replacement wake or outcome-driven re-asking;
- full 1998-call replay remains unauthorized.

The new runtime wake identities may differ because approved prompt/schema/trader identity changed. Stable logical wake-selection identities must remain equal for the same logical opportunities.

## 4. Required pre-execution assurance

F-01 and F-02 have been independently closed.

The fresh independent review at:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_PROVIDER_REVALIDATION_F02_CLOSURE_INDEPENDENT_REVIEW_2026-08-27.md`

found material blocker `F-03`: a child bridge may have reached the provider-attempt boundary but the parent can time out or lose the result file, causing existing accounting to incorrectly report zero provider/network calls.

F-03 and subsequent F-04 were repaired and independently accepted before the final preflight. F-05 was then found at the final pre-execution gate and repaired offline with zero provider attempts. The Owner now explicitly waives a **new F-05-only independent review** for this exact slot.

Before a new machine slot may become ACTIVE:

1. retain the accepted F-01/F-02/F-03/F-04 closure evidence and accepted independent review;
2. retain F-05 offline closure evidence showing zero provider attempts;
3. run deterministic final preflight against the exact current execution commit and the verified original canonical dataset;
4. reseal a new forward V0_3 two-identity machine authority against that exact current execution commit; never reuse/reactivate either historical terminal slot;
5. bind exact current prompt/schema/trader/runtime identities and exactly three logical+runtime wake pairs;
6. bind call ceiling = 3, retries = 0, images = 4, restart after call 2;
7. encode the Owner's scoped CNY-ceiling waiver explicitly rather than fabricating a numeric spend cap;
8. verify the exact current machine authority, dataset, provider/model, pinned Harness and credential-location seam immediately before activation;
9. only then activate the slot immediately before execution.

Any mismatch fails closed before provider execution.

A new independent F-05 review is **not** a precondition for this exact slot by current Owner decision.

## 5. Revalidation acceptance scope

Technical PASS requires:

- `3` real provider requests and `3` accepted normalized decisions;
- `0` retries and `0` hidden/auxiliary provider requests;
- no call 4;
- exactly 4 governed PNG inputs per call;
- both logical and runtime wake identities match the fresh machine authority;
- all decision-time observations remain causal with no future/outcome/PnL leakage;
- every required V0.2 structured-memory field is present with strict allowed type;
- persisted structured state is exactly model-supplied, not parsed from rationale;
- call 2 sees accepted call-1 state;
- after forced restart, call 3 sees exact accepted call-2 state;
- provider metadata/request accounting is durable before normalization failure when available;
- any child-bridge timeout/no-result after attempt start is represented as an unknown attempted call and terminates the slot rather than being treated as zero calls.

Any schema/normalization/request/restart/identity/state-continuity or unknown-attempt failure stops immediately with zero retry. The slot is then terminal and cannot be automatically rerun.

Trading-quality findings remain separate from technical integrity unless they expose a contract/causality/memory-integrity violation.

## 6. Historical evidence preservation

Do not rewrite:

- original failed smoke evidence;
- historical successful retest evidence;
- either historical terminal machine authority;
- historical runtime wake hashes.

The new run must produce new authority/evidence under new identities.

## 7. Full V0.1 boundary

`FULL_V0_1_1998_CALL_REPLAY = STILL_LOCKED`

Completion of the new three-call revalidation must be adjudicated before any full-V0.1 paid authority decision.
