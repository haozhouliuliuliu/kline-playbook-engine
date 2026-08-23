# 江河真实模型探针前：冻结 Finding 复核与 Provider 第一方刷新 V0.1

> Status: `COMPLETE__OWNER_PROVIDER_SELECTION_REQUIRED`
> Date: 2026-08-24
> Verified main baseline: `0c223d6718eed3937a03f8f99a4f31b8f00426d2`
> Scope: finding-specific verification of frozen `BSP-001..005` / `RSP-001..002` plus first-party capability/pricing refresh for the remaining provider/model candidates.
> This review does **not** reopen a whole-repository audit and does **not** authorize paid calls.

## Executive result

```text
FROZEN_FINDING_VERIFICATION=COMPLETE
BSP_001=CONFIRMED_OPEN
BSP_002=CONFIRMED_OPEN
BSP_003=CONFIRMED_OPEN
BSP_004=CONFIRMED_OPEN
BSP_005=CONFIRMED_OPEN
RSP_001=CONFIRMED_OPEN
RSP_002=CONFIRMED_OPEN
NEW_BLOCKER_FOUND=NO
FROZEN_FINDING_SET_CHANGED=NO
TOOL_DECISION=USE_EXISTING

PROVIDER_REFRESH=COMPLETE_FOR_CURRENT_OWNER_CANDIDATES
RECOMMENDED_PROVIDER_SET=OPENAI_GPT_5_6_SOL__XAI_GROK_4_6__KIMI_K3
DEEPSEEK_V4_FLASH_VISION_EXP=NOT_FIRST_PARTY_VERIFIABLE_AS_CURRENT_VISUAL_API_MODEL
FINAL_APPROVED_PROVIDER_SET=NOT_DECIDED
PAID_CALL_AUTHORIZATION=NO
```

The frozen finding authority remains:
`docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md`.

This file records a fresh-current-main adjudication and time-sensitive provider reconnaissance only. It does not replace the frozen acceptance invariants.

---

## 1. Frozen finding verification against current main

### BSP-001 — CONFIRMED OPEN

Current `docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json` still carries only scope labels such as:

```text
knowledge_scope=CURRENT_ACTIVE_JIANGHE_V1_1_PLUS_PRIMARY_REGISTRY_V0_5
memory_scope=GOVERNED_WORKING_MEMORY_SNAPSHOT_ONLY
```

Current `JiangheModelRequest` still binds prompt package/context-policy identities, observation, visual and structured artifacts, but has no separate content-addressed selected Jianghe context artifact, no material selected-context payload, no current knowledge-pack/PRIMARY material binding, and no governed working-memory artifact binding. `build_transport_payload()` sends the compact prompts plus optional visual/structured artifacts, not a separately reproducible selected Jianghe context material.

**Adjudication:** original evidence remains true. No contrary current-main evidence found.

### BSP-002 — CONFIRMED OPEN

Current `StructuredInputArtifact` still accepts:

```python
payload: Mapping[str, Any]
```

and `from_payload()` still accepts caller-constructed mappings. The implementation binds/hash-checks the mapping and rejects explicit forbidden field names, but still does not require one strict versioned closed-world serializer generated from canonical `JiangheObservation`.

**Adjudication:** original evidence remains true. No contrary current-main evidence found.

### BSP-003 — CONFIRMED OPEN

Current runtime normalizer preserves model-declared `principle_references` as raw model evidence, which is correct. However `build_fidelity_response_payload()` still maps:

```text
runtime_evidence.principle_references
-> acknowledged_principles
```

while evaluator-side judgment supplies `violated_principles` and `invented_thresholds`. Therefore positive scorer-facing principle acknowledgment can still originate directly from model self-declaration.

**Adjudication:** original circular positive-evidence path remains. No contrary current-main evidence found.

### BSP-004 — CONFIRMED OPEN

Current provider contract remains intentionally offline-only. `InvocationConfig(live_calls_enabled=True)` is rejected and `CandidateProviderAdapter.invoke()` raises `LiveInvocationDisabledError`. No provider-specific real HTTP/SDK invocation path is present in the canonical provider contract.

**Adjudication:** original evidence remains true. This is unfinished pre-live work, not a regression.

### BSP-005 — CONFIRMED OPEN

Current provider contract can record generic usage metadata but has no executable cumulative CNY budget ledger, provider/model rate-card identity, pre-call worst-case reservation, FX authority, bounded image/token billing calculation, actual-cost reconciliation gate, or retry spend accounting. Repository search also found no current code path matching a budget/rate-card/worst-case-cost guard.

**Adjudication:** the RMB 100 limit remains governance-only and is not yet code-enforced.

### RSP-001 — CONFIRMED OPEN

Current `ShadowRuntime.drain_and_apply_events()` still performs:

```python
self._oms.apply_broker_event(event)
results.append(self._state.apply_broker_event(event))
```

so OMS side effects still occur before authoritative `TradingState` admission/deduplication.

**Adjudication:** original runtime correctness defect remains.

### RSP-002 — CONFIRMED OPEN

Current `StrategyIntent.identity_id` already hashes full semantic content, but `ConflictResolver.resolve()` deduplicates with a `seen` set keyed only by `intent_id` before comparing that full identity. Therefore same `intent_id` + different content can still be silently collapsed.

**Adjudication:** original identity-collision defect remains.

### Verification conclusion

No frozen finding is overturned. No new blocker is introduced. The next repair package must close the same five BSPs and should close both RSPs under the already-frozen acceptance invariants.

---

## 2. First-party provider/model refresh

Provider facts below are deliberately dated because API availability, pricing and model routing can drift. They must be rechecked again at implementation/spend authorization if the provider changes its published contract.

### 2.1 OpenAI — GPT-5.6 Sol

```text
MODEL_ID=gpt-5.6-sol
ALIAS=gpt-5.6 -> gpt-5.6-sol
DIRECT_API=YES
IMAGE_INPUT=YES
TEXT_OUTPUT=YES
STRUCTURED_OUTPUTS=YES
CONTEXT=1,050,000
MAX_OUTPUT=128,000
```

First-party model documentation confirms image input, Responses/Chat Completions support and Structured Outputs.

**Pricing authority issue:** current first-party OpenAI pages are not internally synchronized. The current model catalog/compare surface reports promotional Sol pricing around `$4 / 1M input` and `$20 / 1M output`, while the dedicated Sol model page still reports `$5 / 1M input` and `$30 / 1M output`. OpenAI's 2026-08-21 update explicitly says Sol API/credit pricing was reduced by more than 20% for three months, while older body text still shows the prior rate.

Therefore:

```text
OPENAI_CURRENT_PRICE_AUTHORITY=FIRST_PARTY_DOC_CONFLICT
BUDGET_GUARD_POLICY=DO_NOT_HARDCODE_THE_LOWER_RATE_UNTIL_CANONICAL_BILLING_AUTHORITY_IS_RESOLVED
CONSERVATIVE_PREFLIGHT_RATE=USE_HIGHER_PUBLISHED_BOUND_IF_UNRESOLVED
```

The model page describes snapshot semantics, but the current public Sol page does not expose a clearly dated immutable Sol snapshot distinct from `gpt-5.6-sol`. The transport must record requested selector and provider-returned model identity separately and treat unresolved drift as fail-closed/non-comparable evidence.

First-party sources:
- https://developers.openai.com/api/docs/models/gpt-5.6-sol
- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/compare
- https://openai.com/index/gpt-5-6/

### 2.2 xAI — Grok 4.6

```text
MODEL_ID=grok-4.6
DIRECT_API=YES
RESPONSES_API=YES
CHAT_COMPLETIONS=YES
IMAGE_INPUT=YES
TEXT_OUTPUT=YES
STRUCTURED_OUTPUTS=YES
CONTEXT=500,000
SHORT_CONTEXT_THRESHOLD=<200,000 prompt tokens
SHORT_INPUT_USD_PER_MTOK=2.00
SHORT_CACHED_USD_PER_MTOK=0.50
SHORT_OUTPUT_USD_PER_MTOK=6.00
LONG_INPUT_USD_PER_MTOK=4.00
LONG_CACHED_USD_PER_MTOK=1.00
LONG_OUTPUT_USD_PER_MTOK=12.00
```

xAI's `/v1/models` contract exposes model IDs, aliases, creation time and token prices. xAI also documents an exact per-request billed-cost field `usage.cost_in_usd_ticks`, which is unusually useful for BSP-005 reconciliation.

xAI explicitly documents alias semantics: unsuffixed model names generally track the latest stable release; date-suffixed releases are intended for consistency. The public Grok 4.6 page currently exposes `grok-4.6`, so the live transport must capture the response-resolved model string and reject/segregate drift rather than assuming the requested alias is an immutable research identity.

Server-side web/X search/code execution are available capabilities but are **not needed** for this Jianghe fidelity probe and should stay disabled.

First-party sources:
- https://docs.x.ai/developers/models/grok-4.6
- https://docs.x.ai/developers/pricing
- https://docs.x.ai/developers/models
- https://docs.x.ai/developers/model-capabilities/text/structured-outputs
- https://docs.x.ai/developers/cost-tracking
- https://docs.x.ai/developers/rest-api-reference/inference/models

### 2.3 Moonshot/Kimi — Kimi K3

```text
MODEL_ID=kimi-k3
DIRECT_API=YES
BASE_URL=https://api.moonshot.ai/v1
IMAGE_INPUT=YES
VIDEO_INPUT=YES
TEXT_OUTPUT=YES
STRICT_JSON_SCHEMA=YES
CONTEXT=1,000,000
CACHE_HIT_USD_PER_MTOK=0.30
INPUT_USD_PER_MTOK=3.00
OUTPUT_USD_PER_MTOK=15.00
MINIMUM_TOP_UP_TO_UNLOCK_USD=1
```

Kimi K3 is explicitly documented as natively visual. Its structured-output path supports `json_schema` with `strict: true` and `additionalProperties: false`.

Two cost-control details matter materially:

1. K3 always has thinking enabled; `reasoning_effort` supports low/high/max and defaults to max.
2. `max_completion_tokens` defaults to 131,072 and can be set much higher, so the project **must** set an explicit small bounded output ceiling before any spend-eligible call.

Kimi vision uses dynamic token accounting. The first-party vision guide exposes an estimate-tokens API for image/video requests, which can be used as part of conservative pre-call cost bounding. The platform lists only the current `kimi-k3` slug rather than a dated immutable K3 snapshot; model-drift handling therefore remains necessary.

First-party sources:
- https://platform.kimi.ai/docs/guide/kimi-k3-quickstart
- https://platform.kimi.ai/docs/models
- https://platform.kimi.ai/docs/guide/use-kimi-vision-model
- https://platform.kimi.ai/

### 2.4 DeepSeek — current official V4 API

Current first-party DeepSeek API documentation exposes only:

```text
deepseek-v4-flash
DeepSeek-V4-Flash

deepseek-v4-pro
DeepSeek-V4-Pro
```

The current official API model list does **not** expose `deepseek-v4-flash-vision-exp`. More importantly, DeepSeek's own current integration documentation explicitly states that DeepSeek V4 is text-only; image handling in some external integrations is proxied through another vision model before text is sent to DeepSeek.

Current V4 Flash pricing is extremely low — the Chinese first-party pricing page lists approximately `1 CNY / 1M cache-miss input tokens` and `2 CNY / 1M output tokens` — but price does not cure the hard capability mismatch. The project requires direct visual K-line fidelity for initial real-model comparison.

DeepSeek's direct response-format feature is JSON-object mode rather than the same strict JSON-schema response contract offered by the other three candidates, although strict function-call schema is available as a beta capability.

**Adjudication:**

```text
DEEPSEEK_V4_FLASH_VISION_EXP=NOT_VERIFIED_AS_A_CURRENT_FIRST_PARTY_API_MODEL
DEEPSEEK_CURRENT_V4=TEXT_ONLY
CURRENT_VISUAL_FIDELITY_PROBE_RECOMMENDATION=EXCLUDE_DEEPSEEK
```

This is a capability/scope conclusion, not a claim about DeepSeek model quality.

First-party sources:
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/api/list-models/
- https://api-docs.deepseek.com/quick_start/agent_integrations/github_copilot/
- https://api-docs.deepseek.com/guides/json_mode/

---

## 3. Project-brain provider recommendation

Under the current research objective — Jianghe fidelity first, mandatory visual K-line ability, strict/auditable outputs, and RMB 100 total hard cap — the recommended comparison set is:

```text
1. OpenAI GPT-5.6 Sol
2. xAI Grok 4.6
3. Kimi K3
```

Rationale:

- all three have current first-party direct API evidence for image input and structured output;
- they provide meaningfully different model/provider implementations, making a fidelity comparison more informative than testing only one vendor;
- Grok has strong per-request cost telemetry and comparatively low token prices;
- Kimi adds a current natively visual flagship from a separate provider and exposes pre-call multimodal token estimation;
- Sol remains the high-capability retained candidate and should stay in the comparison despite higher cost;
- the RMB 100 ceiling should be protected by bounded context selection, explicit output caps, no provider tools/search, no semantic retries, and pre-call worst-case reservation rather than by removing useful comparison candidates prematurely.

This recommendation is **not** adoption and is **not** paid-call authorization.

If the Owner chooses a lean two-provider implementation to minimize transport work, the engineering-first fallback recommendation is:

```text
OpenAI GPT-5.6 Sol + xAI Grok 4.6
```

because xAI currently exposes the strongest first-party model-resolution/pricing/cost-reconciliation surfaces. Kimi K3 remains the most useful third comparator if the Owner accepts the additional transport/rate-card path.

---

## 4. Owner decision now required

The next major decision remains Owner-gated:

1. choose the final provider/model set from the recommendation above;
2. choose whether the bounded fidelity probe is the recommended three-provider comparison or a leaner subset.

This choice authorizes only the **provider-specific implementation target** for BSP-004/BSP-005. It does **not** authorize a paid API call.

After the Owner chooses the provider set, the normal path is still:

```text
one batched repair for all still-valid BSP/RSP findings
-> finding-specific adversarial/focused tests
-> python -m unittest discover -s tests -v
-> finding-specific re-audit
-> formal closure evidence/state update
-> only then ask separately for paid-call authorization
```

All outcome, PRIMARY semantic-freeze, Validation, Final, Shadow/Forward, broker and real-money locks remain unchanged.
