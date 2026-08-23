# 江河真实模型探针前双重复核 — 合并发现 V0.1

> Status: `FROZEN__REPAIR_REQUIRED_BEFORE_SPEND`
> Audit baseline: `7d85b41044181ee35ac482ea158898956727f23b`
> Date: 2026-08-24
> Scope: Owner-requested pre-spend assurance review before any real provider request.
> Authority role: this file is the durable consolidated finding authority for the current pre-spend repair gate.

## Executive result

```text
ROUND_1_ARCHITECTURE_AUDIT=FAIL
ROUND_2_FINE_GRAINED_AUDIT=FAIL
CONSOLIDATED_FINDINGS=FROZEN
BLOCKER_BEFORE_SPEND=5
REPAIR_RECOMMENDED_BEFORE_SPEND=2
NONBLOCKING_CLEANUP=1
LIVE_CALLS=0
PAID_SPEND=0
SPEND_GATE=CLOSED
TOOL_DECISION=USE_EXISTING
```

The original PRIMARY fixed-rubric re-audit and the original 27-item pre-live fidelity gate remain PASS. These findings are a later Owner-requested pre-spend assurance layer; they do not reopen PRIMARY prose/template questions and do not invalidate the prior gate evidence outside the concrete issues listed here.

No provider/model becomes VERIFIED or ADOPTED by this review. No outcome access, PRIMARY freeze, broker access, real money, or paid call is authorized.

## How the next project brain must use this document

The **finding set and non-negotiable acceptance invariants are frozen**. The **implementation design is intentionally not frozen**.

Reason: the current project brain has enough evidence to define what is wrong and what a repair must prove, but the next fresh conversation should independently refresh current `main`, re-read the relevant source files, and choose the simplest correct implementation. Locking exact class names/module layout here would risk forcing a suboptimal design after context handoff.

Therefore:

1. do not restart an open-ended architecture audit unless new concrete evidence appears;
2. independently verify each frozen finding against current `main` before editing;
3. preserve every acceptance invariant below;
4. implementation details may change if the alternative is simpler/safer and still closes the finding;
5. if a frozen finding is proven false by concrete repository evidence, record that adjudication formally rather than silently dropping it;
6. if a genuinely new blocker is found during repair, it must be concrete correctness, evidence-integrity, security, or cost-control evidence — not style/prose preference;
7. after repair, re-run focused adversarial tests, the canonical full suite, and only the audit checks affected by these findings.

## BSP-001 — Paid probe request does not yet carry a content-addressed Jianghe knowledge/context artifact

```text
CLASSIFICATION=BLOCKER_BEFORE_SPEND
AREA=knowledge_context_provenance
AFFECTED=
  docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json
  src/jianghe_model_provider.py
  tests/test_jianghe_prompt_package.py
  tests/test_jianghe_model_provider.py
```

### Concrete repository evidence

The prompt package declares:

```text
knowledge_scope=CURRENT_ACTIVE_JIANGHE_V1_1_PLUS_PRIMARY_REGISTRY_V0_5
market_scope=CURRENT_CANONICAL_OBSERVATION_ONLY
memory_scope=GOVERNED_WORKING_MEMORY_SNAPSHOT_ONLY
```

but the current prompt package contains only the compact system/decision prompts plus scope labels and identities. The scope string itself is not the Jianghe V1.1 / PRIMARY V0.5 material.

`JiangheModelRequest` currently binds provider/model, prompt package, context-selection policy, response schema, normalizer, evaluator extractor, observation, timing and visual/structured artifacts. Its transport payload sends actual system/decision prompt text and optional visual/structured inputs, but it does **not** carry a separate content-addressed selected Jianghe context artifact, current knowledge-pack identity, current PRIMARY registry identity, selected-context content hash, or working-memory snapshot artifact.

The prompt package rebind from V0.3 to V0.5 correctly changed the `knowledge_scope` string and context/package identities, but that does not by itself prove what source material a future provider actually receives.

### Why this blocks spend

A paid fidelity probe could otherwise measure generic prompt-following plus chart reading rather than execution of the repository-governed Jianghe V1.1 + PRIMARY V0.5 knowledge boundary. The resulting evidence would be ambiguous: the repository could prove which scope label was intended without proving which exact Jianghe material the model actually saw.

This also creates avoidable cost pressure if a later implementation reacts by repeatedly sending the entire knowledge pack without a governed minimal-selection policy.

### Non-negotiable repair invariants

A spend-eligible request path must prove all of the following:

1. the exact Jianghe context actually sent is material content, not merely a scope label or hash;
2. selected context is derived only from current repository authority allowed for the probe;
3. selected context is content-addressed and deterministically reproducible from its inputs/policy;
4. request identity changes if the selected Jianghe context changes;
5. evidence binds at minimum the current knowledge-pack identity, current PRIMARY registry/interpretation authority as applicable, context-selection policy identity, selected-context identity/content hash, and the request identity;
6. provider transport actually sends the same selected context whose identity is recorded;
7. no outcome/future/fixture-answer authority can enter the selected context;
8. full 352-claim transmission is **not** required. A minimal deterministic subset is preferred when semantically sufficient; the repair must not manufacture cost by sending irrelevant material;
9. governed working memory, if used by the probe, must be separately bound rather than implied by the phrase `GOVERNED_WORKING_MEMORY_SNAPSHOT_ONLY`.

### Minimum acceptance evidence

At least adversarial tests proving:

- identical selection inputs -> identical selected-context identity and bytes/text;
- a material context change -> different identity and request identity;
- transport payload contains the actual selected material;
- recorded identity cannot be forged to match different material;
- forbidden outcome/future/fixture material is rejected;
- empty/missing required selected context fails closed for tracks that require Jianghe knowledge;
- a request cannot claim V1.1/V0.5 scope while sending unrelated context.

---

## BSP-002 — Structured model input is not yet a strict closed-world canonical observation artifact

```text
CLASSIFICATION=BLOCKER_BEFORE_SPEND
AREA=structured_input_data_egress_and_provenance
AFFECTED=
  src/jianghe_model_provider.py
  src/jianghe_ai_trader.py
  tests/test_jianghe_model_provider.py
```

### Concrete repository evidence

`StructuredInputArtifact` currently accepts a generic `Mapping[str, Any]` payload, verifies that `payload.observation_identity` matches the declared observation identity, checks JSON compatibility/forbidden field **names**, hashes the payload, and binds the hash into an artifact identity.

This is good content-addressing, but it is not a closed-world observation schema. Callers can still construct arbitrary extra fields so long as field names are not on the forbidden-name list. The generic forbidden scan does not make arbitrary textual values a governed market-data schema.

Existing provider tests intentionally construct structured input manually from a small dictionary rather than requiring a single canonical constructor from `JiangheObservation`.

### Why this blocks spend

For a real API request, the project must be able to prove exactly what structured market/context information left the process. A generic mapping leaves room for accidental extra context, stale fields, hidden free-form text, or data that should not be present under `OUTCOME_ACCESS=NO`.

The visual path is materially stronger: integrated visual artifacts bind canonical observation, renderer provenance, PNG bytes and canonical visual artifact identity. Structured input should reach the same audit quality.

### Non-negotiable repair invariants

1. spend-eligible structured input must have one strict versioned schema;
2. unknown fields fail closed;
3. canonical structured input must be derived from the canonical `JiangheObservation` or another formally equivalent governed observation authority, not an arbitrary caller dictionary;
4. the structured artifact must bind the canonical observation identity and exact serialized structured content;
5. no arbitrary free-form extension channel may silently carry extra market/outcome/context data;
6. schema identity must correspond to an actual schema/serializer contract, not a caller-supplied opaque 64-hex value with no enforced meaning;
7. serialization must be deterministic across supported platforms;
8. outcome/future/fixture-answer content remains impossible by construction or explicitly rejected fail-closed.

### Minimum acceptance evidence

Adversarial tests must include:

- extra unknown key rejected;
- forged schema/artifact identity rejected;
- same canonical observation -> deterministic structured bytes/payload identity;
- changed canonical observation -> changed structured identity;
- observation identity mismatch rejected;
- nested or disguised unauthorized free-form data cannot pass through an otherwise harmless key;
- provider transport receives the exact artifact whose identity is recorded.

---

## BSP-003 — Fidelity scoring currently trusts model-declared `principle_references` as positive scoring evidence

```text
CLASSIFICATION=BLOCKER_BEFORE_SPEND
AREA=fidelity_evidence_integrity
AFFECTED=
  src/jianghe_response_normalizer.py
  src/jianghe_fidelity_scoring.py
  src/jianghe_fidelity_evaluation.py
  docs/evidence/JIANGHE_AI_FIDELITY_FIXTURES_V0_1.json
  tests/test_jianghe_fidelity_evaluation.py
  tests/test_jianghe_model_provider.py
```

### Concrete repository evidence

The runtime response schema allows the model to output `principle_references`. The normalizer correctly treats these as objective fields the model actually emitted.

However, `build_fidelity_response_payload()` currently maps:

```text
runtime_evidence.principle_references
    -> acknowledged_principles
```

The scorer's `principle_acknowledged` constraints then use `acknowledged_principles` as positive PASS-path evidence. Multiple current fixtures require one or more acknowledged Jianghe principles for PASS.

This creates a circular evidence path: the model can declare that it referenced a principle, and the scorer may treat that declaration as evidence that the principle was actually satisfied.

The existing evaluator-side separation is stronger for `violated_principles` and `invented_thresholds`, but the current `EvaluatorSideJudgment` object mainly validates identity/type/sortedness of caller-supplied judgments; the durable chain still needs to prove how positive/negative semantic judgments are grounded in fixture constraints and the model's actual rationale/decision.

### Why this blocks spend

A provider that simply emits many plausible principle IDs could receive artificially favorable fidelity scores without demonstrating Jianghe-consistent reasoning. That would directly contaminate model selection, which is the purpose of the paid probe.

### Non-negotiable repair invariants

1. model-declared principle/source references remain raw model evidence only;
2. a model's self-declared principle ID may not directly become a positive scoring fact;
3. `acknowledged_principles`, `violated_principles`, and `invented_thresholds` used for scoring must come from an evaluator-side grounded adjudication path tied to the fixture and normalized response;
4. evaluator judgment must bind the normalized decision identity, fixture identity/corpus identity, evaluator/extractor version/identity, and the evidence used to make the judgment;
5. missing evaluator judgment must fail closed/non-scoreable where semantic judgment is required;
6. the repair must preserve multiple-reasonable-answer semantics and must not turn the corpus into fixed-text recitation;
7. no model self-score or self-reported `no_violations` / `no_inventions` may become scoring authority.

### Minimum acceptance evidence

Adversarial tests must prove:

- a response that blindly declares every `JH-PRINC-*` cannot gain PASS merely from those declarations;
- unsupported declared principle IDs do not become acknowledged facts;
- evaluator judgment for a different fixture/decision identity is rejected;
- empty caller-supplied judgment cannot silently neutralize concrete fixture violations;
- the same normalized response + same fixture + same evaluator evidence produces deterministic adjudication identity/result where the chosen evaluator path is intended to be deterministic;
- model raw references survive for audit even when evaluator-side scoring rejects them.

Implementation choice is intentionally open: deterministic rule extraction, separately governed evaluator review, or another auditable mechanism may be chosen after fresh-main review. The invariant is that model self-report cannot grade itself.

---

## BSP-004 — Real provider transport is not implemented

```text
CLASSIFICATION=BLOCKER_BEFORE_SPEND
AREA=live_provider_transport
AFFECTED=
  src/jianghe_model_provider.py
  provider-specific implementation not yet present
```

### Concrete repository evidence

The current provider contract explicitly states that it contains no HTTP/SDK/secret-reading/real invocation implementation. `InvocationConfig.live_calls_enabled=True` is rejected and `CandidateProviderAdapter.invoke()` is intentionally disabled.

Current state correctly records:

```text
JIANGHE_AI_REAL_MODEL_PROVIDER=LIVE_TRANSPORT_NOT_IMPLEMENTED_NOT_VERIFIED_NOT_ADOPTED
```

This is not a historical regression; it is an intentionally unfinished pre-live boundary. It is nevertheless a hard spend blocker because there is no audited canonical path that could legally make the real request.

### Non-negotiable repair invariants

Once the Owner selects the final provider/model set, the live transport must:

1. remain behind explicit Owner authorization and a disabled-by-default gate;
2. use environment/secret handling that never serializes credentials into request/evidence/log artifacts;
3. bind requested selector separately from provider-resolved model/version/snapshot;
4. record raw response evidence, provider response ID if available, timing and usage metadata required for audit;
5. preserve the canonical request/observation/context/visual/structured identities established by the offline contract;
6. disable provider web/search/tools/grounding/code-execution or other extra capabilities unless explicitly required and separately approved;
7. distinguish transport failures from semantic/schema failures;
8. semantic/schema failures must not trigger automatic paid retries;
9. retry behavior, if any transport retry is later permitted, must be bounded, idempotency-aware where the provider supports it, and budget-accounted;
10. malformed/partial provider responses remain non-scoreable and fail closed;
11. provider-specific code must not fork a second Jianghe semantics/normalizer/evaluator stack.

The exact provider SDK/HTTP implementation is not frozen here. Provider-specific work should wait for final Owner provider selection and a fresh first-party capability/pricing check.

---

## BSP-005 — RMB 100 hard cap is governance-only; no code-level spend guard exists yet

```text
CLASSIFICATION=BLOCKER_BEFORE_SPEND
AREA=cost_control
OWNER_HARD_CAP_CNY=100.00
AFFECTED=
  docs/reviews/JIANGHE_LIVE_PROBE_OWNER_SCOPE_REVISION_V0_2.md
  src/jianghe_model_provider.py
  future live transport/budget evidence
```

### Concrete repository evidence

The Owner authority fixes:

```text
TOTAL_HARD_SPEND_CAP_CNY=100.00
NO_AUTOMATIC_BUDGET_EXTENSION=YES
NO_PROVIDER_SPECIFIC_OVERRUN=YES
```

The current provider contract can record provider usage metadata but contains no cumulative CNY budget ledger, provider rate-card identity, pre-call worst-case cost check, canonical output-token ceiling, remaining-budget check, retry spend accounting, or unknown-price fail-closed policy.

Because real transport is intentionally disabled, no money has been spent. This finding concerns the missing enforcement required before that transport is enabled.

### Non-negotiable repair invariants

1. total authorized spend across all finally selected providers is hard-capped at RMB 100 unless the Owner later explicitly changes the authority;
2. the system must fail **before** a call if the conservative worst-case charge permitted by that request could exceed remaining authorized budget;
3. every spend-eligible call must bind a provider/model pricing authority/rate-card identity and billing semantics sufficient to compute/upper-bound cost;
4. USD or other non-CNY pricing must use a predeclared auditable FX/conversion authority or conservative bound before the call; unknown conversion semantics => no call;
5. request-level maximum output/token/image settings relevant to cost must be explicit, versioned and bounded;
6. automatic semantic/schema retries are forbidden;
7. any transport retry later permitted must have an explicit maximum count, cost upper bound and cumulative-budget accounting;
8. actual usage/cost evidence must be reconciled after each call before another call can be authorized;
9. unknown provider price, ambiguous image billing, missing usage needed for accounting, or rate-card drift => fail closed;
10. no provider can borrow beyond the total hard cap through separate local counters.

### Minimum acceptance evidence

Tests must cover:

- pre-call rejection when worst-case request cost exceeds remaining CNY budget;
- exact boundary behavior at remaining budget;
- cumulative spend across multiple providers/calls;
- rate-card/model mismatch rejection;
- unknown price/FX/image billing rejection;
- output-token cap included in request identity/cost estimate where relevant;
- semantic failure causes zero automatic retry;
- transport retry, if implemented, cannot exceed configured count or budget;
- actual usage update reduces remaining budget before the next authorization.

---

## RSP-001 — `ShadowRuntime` applies broker events to OMS before authoritative TradingState admission/deduplication

```text
CLASSIFICATION=REPAIR_RECOMMENDED_BEFORE_SPEND
AREA=runtime_idempotency
AFFECTED=
  src/shadow_runtime.py
  src/order_management.py
  src/trading_state.py
  tests/test_shadow_runtime.py
```

### Concrete repository evidence

`TradingState.apply_broker_event()` has explicit duplicate-event, different-content duplicate, out-of-order and sequence-gap handling. Existing tests demonstrate identical duplicate events become `APPLIED_ALREADY_NOOP` without changing authoritative state.

But `ShadowRuntime.drain_and_apply_events()` currently does the side effects in this order:

```text
OMS.apply_broker_event(event)
TradingState.apply_broker_event(event)
```

OMS fill handling adds the event fill quantity to the current order fill before the authoritative TradingState has decided whether the event is a duplicate/out-of-order/rejected fact.

### Risk

A replayed duplicate fill can mutate or error in the OMS mirror before TradingState returns the correct idempotent result. This is not a spend-path blocker because the bounded fidelity probe must not execute broker orders, but it is a concrete runtime correctness defect and should be included in the same repair package rather than left behind.

### Non-negotiable repair invariants

1. a broker event rejected/no-op by the authoritative state-admission policy must not mutate OMS or other mirrors;
2. identical duplicate fill is idempotent across both TradingState and OMS;
3. same event ID with different content fails closed without mirror mutation;
4. out-of-order/sequence-gap rejected events do not mutate OMS;
5. accepted broker facts still override local inference.

Implementation may either admit through TradingState before mirror mutation or make the OMS itself consume an authoritative admission result. Do not create two competing sequence authorities.

---

## RSP-002 — `ConflictResolver` collapses same `intent_id` without proving content identity

```text
CLASSIFICATION=REPAIR_RECOMMENDED_BEFORE_SPEND
AREA=intent_identity_integrity
AFFECTED=
  src/intent.py
  related runtime tests
```

### Concrete repository evidence

The resolver documentation says identical duplicate intents collapse. The implementation deduplicates by `intent_id` alone: the first occurrence is kept and later occurrences with the same ID are dropped before comparing full content identity.

Therefore:

- same ID + same content can safely collapse;
- same ID + different content can currently be silently collapsed as if identical.

### Non-negotiable repair invariants

1. same intent ID + same full semantic/content identity may collapse deterministically;
2. same intent ID + different content identity must fail closed as an identity collision/conflict;
3. no ordering artifact may silently choose one conflicting payload;
4. tests cover changed action, direction, quantity, context identity and reason under the same intent ID.

This is execution correctness, not a paid-fidelity-call blocker, but should be repaired in the same bounded package.

---

## NBP-001 — Active limitations index retained resolved LIMIT-013/LIMIT-014 despite its own maintenance rule

```text
CLASSIFICATION=NONBLOCKING_CLEANUP
AREA=authority_hygiene
AFFECTED=KNOWN_LIMITATIONS_AND_TECH_DEBT.md
```

The file says resolved items should be removed from the active unresolved index, yet it still contains resolved LIMIT-013 and LIMIT-014 sections. This does not affect runtime correctness or spend safety. During this handoff/state update, the active index should remove those resolved sections and retain their resolution in current state/review history.

---

## Important suspected problems that were rechecked and are NOT findings

The next conversation should not waste time reopening these without new evidence.

### NF-001 — Observation identity is content-bound

`ObservationIdentity` includes `content_identity`, and `JiangheObservation` binds visible bars, positions, active orders, schema and visible metadata into that content identity. The earlier suspicion that same time/contract with changed bars could retain the same canonical observation identity is not supported by current code.

### NF-002 — Integrated visual provenance is materially strong

The current visual path recomputes PNG hash, renderer/config provenance, canonical observation binding and visual artifact identity; forged identities/hashes are rejected. No second visual stack is required by this audit.

### NF-003 — Requested model selector and provider-resolved model identity are separated

Current provider tests distinguish mutable requested alias from actual provider-resolved model/version and reject drift under exact-snapshot binding.

### NF-004 — Runtime normalizer strictness is not the current blocker

The normalizer requires strict JSON shape/types, rejects unknown fields, recursively rejects explicit forbidden outcome/self-evaluation field names, validates Decimal numeric claims, and keeps raw model text. BSP-003 is a scorer/evidence-grounding problem, not a reason to replace the normalizer wholesale.

### NF-005 — Evaluator outer fail-closed controls remain useful

Current evaluation harness already rejects/marks non-scoreable duplicate candidate-fixture-track records, malformed responses, corpus mismatch, failed calls, insufficient provenance, metadata violations and detected outcome contamination. BSP-003 targets the semantic source of positive/negative scoring judgments; do not discard the surrounding harness without concrete cause.

### NF-006 — No new framework/tool is required

```text
TOOL_DECISION=USE_EXISTING
```

The repairs are ordinary repository engineering/research-evidence work. Do not add a new framework/MCP/large SDK merely because the handoff changed conversations. A provider SDK, if later selected, is provider-specific implementation and must still be justified after Owner provider selection.

## Repair sequencing / Owner gates

The audit plan required consolidation before code changes. Consolidation is now complete and frozen by this document.

Because BSP-004 and part of BSP-005 are provider-specific, the clean route is:

1. fresh project-brain read-only takeover and Owner acceptance;
2. verify the frozen findings against current `main` without restarting an open-ended audit;
3. refresh current first-party provider capability/pricing facts and make the final cost/capability recommendation;
4. **Owner selects the final provider/model set and bounded probe scope** — this remains an Owner decision because it determines paid external access and spend;
5. perform one batched repair package covering all still-valid BSP/RSP findings, including the selected provider transport and hard budget enforcement;
6. focused adversarial tests + canonical full suite + finding-specific re-audit;
7. only after all five BSP items are CLOSED may a separate Owner authorization enable bounded paid calls under the already-defined or newly approved hard cap.

Ordinary engineering choices inside the repair package do not require repeated Owner authorization. New product direction, new research design, semantic freeze, permanent real-money risk rules, broker/account actions, or increased paid spend remain Owner-gated.

## Closure rule

The pre-spend assurance gate may be marked PASS only when all five `BLOCKER_BEFORE_SPEND` findings are formally CLOSED with code/artifact/test evidence.

The two `REPAIR_RECOMMENDED_BEFORE_SPEND` findings should be closed in the same package unless the next project brain produces concrete evidence that one is false or safely out of scope. `NBP-001` is cleanup only and cannot independently keep the spend gate closed.

Do not confuse closure of this gate with:

- model/provider VERIFIED or ADOPTED;
- PRIMARY semantic freeze;
- candidate outcome access;
- historical backtest authorization;
- broker access;
- real money authorization.
