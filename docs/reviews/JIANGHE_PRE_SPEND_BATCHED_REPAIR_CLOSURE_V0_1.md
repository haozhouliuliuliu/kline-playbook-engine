# 江河真实模型探针前批量修复关闭证据 V0.1

> Status: `PASS__FROZEN_FINDINGS_REPAIRED`
> Date: 2026-08-24
> Frozen authority: `docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md`
> Repair PR: `#21` (`repair/prespend-batched-domestic-v02`)
> Final implementation head reviewed: `e51772f16a9312a2a79943b214f0070bc92b9dc5`
> Tool decision: `USE_EXISTING`

## Executive result

```text
BSP-001=CLOSED
BSP-002=CLOSED
BSP-003=CLOSED
BSP-004=CLOSED
BSP-005=CLOSED
RSP-001=CLOSED
RSP-002=CLOSED
PRE_SPEND_REPAIR_REAUDIT=PASS
LIVE_CALLS=0
PAID_SPEND=0
OUTCOME_ACCESS=NO
PROVIDER_VERIFIED=NO
PROVIDER_ADOPTED=NO
PAID_CALL_AUTHORIZED=NO
```

This closure is limited to the frozen pre-spend engineering findings. It does **not** authorize a paid provider call, does not verify or adopt any provider/model, does not promote PRIMARY, and does not unlock outcome, Validation, historical Final, Shadow/Forward, broker access, or real money.

## Verification evidence

Final materialized repair verification:

```text
WORKFLOW_RUN_ID=32673455814
JOB_ID=97277715870
FOCUSED_ADVERSARIAL=PASS__162_TESTS
CANONICAL_FULL_SUITE=PASS__1226_TESTS__27_SKIPPED
DIFF_HYGIENE=PASS
MATERIALIZE=PASS
```

The run used no real provider call. Provider transport tests used injected fake HTTP seams only.

## Finding closure

### BSP-001 — CLOSED

The spend-eligible request now carries deterministic, content-addressed Jianghe material derived from current repository authority.

- The governed fidelity fixture is used only to select `source_anchors.claims`.
- Selected source records are resolved from current PRIMARY V0.5 exact committed Git blob bytes and bind the corrected claim-manifest identity `f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36` and active knowledge-pack identity.
- The model receives only a closed safe semantic projection of selected PRIMARY claims; fixture ID, fixture expected/rubric/hidden-future material and PRIMARY review/audit baggage are not transmitted.
- Selection provenance and the exact model-context payload each have deterministic identities; both are bound into the request identity.
- A manually selected unrelated context artifact cannot become spend-eligible.
- Changing governed fixture/source selection changes selected context and request identity.

Primary implementation: `src/jianghe_prespend_runtime.py`.
Focused evidence: `tests/test_jianghe_prespend_repair.py`.

### BSP-002 — CLOSED

Spend-eligible structured input is now a strict canonical observation artifact.

- `CanonicalStructuredObservationArtifact` is `init=False` and can only be built through `from_observation(JiangheObservation)`.
- Only `JIANGHE_OBSERVATION_V0_1` is accepted.
- Unknown visible metadata and free-form position `entry_facts` are rejected.
- The serializer uses a fixed closed-world field set and deterministic canonical JSON.
- Artifact identity binds schema identity, source observation identity, and exact serialized content hash.
- Caller-supplied arbitrary schema/artifact identity construction is rejected.

Primary implementation: `src/jianghe_prespend_runtime.py`.
Focused evidence: `tests/test_jianghe_prespend_repair.py`.

### BSP-003 — CLOSED

Model-declared principle references no longer grade the model.

- Raw `principle_references` remain retained only as model evidence.
- Scoring `acknowledged_principles`, `violated_principles`, and invented-threshold judgments come from evaluator-side adjudication.
- `EvaluatorSideJudgment.from_fixture()` binds normalized decision identity, corpus identity, fixture identity, evaluator/extractor identity, explicit per-principle adjudications, and evaluator evidence.
- Every fixture principle constraint must be explicitly adjudicated; incomplete or ungrounded judgment fails closed.
- The scorer bridge uses evaluator acknowledgements rather than model self-declarations.

Primary implementation: `src/jianghe_response_normalizer.py`.
Focused evidence: `tests/test_jianghe_response_normalizer.py`, `tests/test_jianghe_model_provider.py`.

### BSP-004 — CLOSED

A single spend-eligible live transport seam now exists for the Owner-confirmed implementation target set:

```text
KIMI_K3
DEEPSEEK_V4_FLASH_VISION_EXP
MINIMAX_M3
```

- The older provider adapter remains offline/live-disabled; no second Jianghe semantics/normalizer/evaluator stack was created.
- Production invocation requires an exact committed Owner paid-call authorization artifact. That artifact is intentionally absent while paid calls are unauthorized; caller-fabricated authorization cannot substitute for it.
- Credentials are read from environment only at invocation and are not serialized into evidence.
- Provider tools/search capabilities are disabled.
- No automatic retry is implemented.
- Requested model and provider-resolved model are separately recorded.
- Raw provider response body, model response text, provider response ID, timing and usage are preserved.
- Evidence binds request, observation, selected context, context policy, knowledge pack, PRIMARY manifest, structured artifact, visual artifacts, provider identity, rate card and budget reservation.
- Transport failures and malformed/provider-response failures fail closed separately.

Primary implementation: `src/jianghe_prespend_runtime.py`.

`BSP-004=CLOSED` means the audited transport implementation/gating exists. It does **not** mean any provider/model is live-verified.

### BSP-005 — CLOSED

The RMB 100 limit is now executable code rather than governance-only prose.

- `CnyBudgetLedger` is one shared ledger across providers and cannot be configured above CNY 100.
- A new request cannot reserve while a prior reservation is unreconciled.
- Exact serialized HTTP request bytes are built before reservation; a conservative text-input bound is derived from the actual payload and must match the call bounds exactly.
- Output and image bounds are explicit. Kimi's repository rate authority uses a fixed image-token rule.
- Provider/model/rate-card mismatch, stale/unknown pricing, ambiguous image billing, caller-supplied production FX, and missing usage fail closed.
- Actual usage is reconciled before a next call; unknown post-network usage consumes the full reservation conservatively.
- Automatic retries are disabled.
- The repository pricing authority explicitly leaves DeepSeek Vision Exp and MiniMax M3 provider-specific spend eligibility blocked until exact image-billing authority is established.

Primary implementation: `src/jianghe_prespend_runtime.py`.
Pricing authority: `docs/evidence/JIANGHE_PROVIDER_PRICING_AUTHORITY_V0_1.json`.

`BSP-005=CLOSED` means the hard-cap enforcement framework is complete. It does **not** assert that all three provider/model pairs currently have spend-eligible rate cards.

### RSP-001 — CLOSED

`ShadowRuntime.drain_and_apply_events()` now sends each broker event through authoritative `TradingState.apply_broker_event()` first. OMS mutation occurs only when `result.applied` is true. Rejected duplicate/different-content/out-of-order/gap events therefore cannot mutate OMS first.

Primary implementation: `src/shadow_runtime.py`.
Focused evidence: `tests/test_prespend_missing_repairs.py`.

### RSP-002 — CLOSED

`StrategyIntent.identity_id` binds intent ID, strategy, instrument/contract, action, decision time, market-context identity, direction, quantity, limit price and reason. `ConflictResolver` now permits same-ID collapse only when this full canonical identity is identical; same ID with different content raises fail-closed.

Primary implementation: `src/intent.py`.
Focused evidence: `tests/test_prespend_missing_repairs.py`.

## Provider-specific residual gates

These are not reopened BSP findings:

```text
KIMI_K3=TRANSPORT_IMPLEMENTED__RATE_GUARD_CURRENT__NOT_LIVE_VERIFIED__NOT_ADOPTED
DEEPSEEK_V4_FLASH_VISION_EXP=TRANSPORT_IMPLEMENTED__EXACT_VISION_IMAGE_BILLING_AUTHORITY_UNRESOLVED__SPEND_FAIL_CLOSED__NOT_LIVE_VERIFIED__NOT_ADOPTED
MINIMAX_M3=TRANSPORT_IMPLEMENTED__EXACT_M3_IMAGE_BILLING_AUTHORITY_UNRESOLVED__SPEND_FAIL_CLOSED__NOT_LIVE_VERIFIED__NOT_ADOPTED
```

Before any paid call, the project still requires a separate explicit Owner authorization artifact and current provider-specific pricing/billing authority. The total future paid-probe ceiling remains CNY 100 unless the Owner explicitly changes that authority.

## Locks preserved

```text
PAID_MODEL_SPEND=NOT_AUTHORIZED
LIVE_CALLS=0
PAID_SPEND=0
OUTCOME_ACCESS=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
```
