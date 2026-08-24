# JIANGHE STAGE-A INPUT AND VISUAL STIMULUS PROTOCOL — OWNER DECISION V0.1

Status: `OWNER_APPROVED__FROZEN_FOR_STAGE_A`
Date: 2026-08-24
Owner approval time: `2026-08-24T09:03:00+08:00`
Scope: Stage-A real-model Jianghe fidelity qualification only.
Paid-call authorization: already granted separately under `OWNER-PAID-JIANGHE-FIDELITY-20260824-V01`.
Live calls before this decision: 0
Paid spend before this decision: CNY 0
Outcome/PnL access: NO

## Owner decision

The Owner explicitly approved this protocol in project chat on 2026-08-24 at 09:03 +08:00:

```text
APPROVE_JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_V0_1=YES
TRACK_ISOLATION=YES
QUALIFICATION_FIXTURE=JH-FIX-C-001
SYNTHETIC_OHLC_FROM_VISIBLE_INFORMATION_ONLY=YES
SAME_UNDERLYING_OBSERVATION_FOR_VISUAL_STRUCTURED_DUAL=YES
FREEZE_ALL_STIMULUS_IDENTITIES_BEFORE_FIRST_PAID_CALL=YES
```

This is a research-design approval. It freezes the Stage-A modality-isolation and visual-stimulus semantics below. It does not expand the separate paid-call authorization.

## Why this decision was required

The repository already freezes:

- the Jianghe fidelity fixture semantics;
- the non-outcome firewall;
- the deterministic visual renderer;
- the structured observation schema;
- the provider transports and CNY100 hard budget guard.

However, the fixture corpus expresses each synthetic market situation mainly as `visible_information` prose. It did not previously freeze the exact OHLC bar recipe used to turn that prose into a K-line image. Different valid-looking OHLC realizations can change what a vision model sees and therefore change its fidelity score.

There was a second related issue: the historical fidelity design distinguishes `SEMANTIC`, `VISUAL`, `STRUCTURED`, and `DUAL_INPUT` as separate tracks, while the repaired spend runtime required both a visual artifact and a structured observation on every spend-eligible request. Using that runtime unchanged would make the track labels less interpretable because a nominal VISUAL or STRUCTURED test would still receive both modalities.

The Owner approval freezes these questions once for Stage A.

## Frozen Stage-A protocol

### 1. Track isolation

Each content track tests one input condition while keeping the Jianghe system prompt, governed minimal PRIMARY context, response schema, inference configuration, and scoring rules fixed.

```text
SEMANTIC:
  fixture visible_information text only
  no K-line image
  no structured market-state artifact

VISUAL:
  deterministic K-line image only
  no fixture situation prose describing the answer-relevant pattern
  no structured market-state artifact

STRUCTURED:
  governed structured observation only
  no K-line image
  no fixture situation prose describing the answer-relevant pattern

DUAL_INPUT:
  deterministic K-line image + governed structured observation
  both generated from the exact same underlying synthetic observation identity
  no fixture situation prose describing the answer-relevant pattern

OPERATIONAL_PROVIDER:
  minimum governed smoke request sufficient to verify exact provider/model identity,
  multimodal transport/schema/usage/evidence capture; not used as a substitute for
  content-track fidelity scoring.
```

Extra answer-bearing modality is forbidden for the isolated track. This makes visual-vs-structured-vs-dual differences interpretable instead of merely relabeling the same request.

### 2. One shared synthetic situation for cross-modal qualification

For the four content tracks in Stage A, use the same predeclared non-outcome fixture situation so the only intended experimental difference is the input modality.

```text
FIXTURE_ID=JH-FIX-C-001
NAME=FALSE_BREAKOUT__WICK_POKE_RETURN_NO_FOLLOW
RATIONALE=visually legible; hard-negative; requires no-trade discipline;
          tests whether a model distinguishes a wick/poke from a genuine breakout
```

The exact fixture ID is frozen before the first provider call and may not change after seeing any model response.

Stage B, if later reached, may broaden family coverage under its already approved funnel envelope, but only after Stage-A evidence/ranking is committed.

### 3. Deterministic synthetic OHLC construction

The exact bar recipe is implemented mechanically under all of these frozen constraints:

1. use only the chosen fixture's `visible_information` and source-authorized Jianghe semantics;
2. never read or encode `hidden_future_information`, outcome/PnL, later price path, or candidate result;
3. use a normalized synthetic price scale around 100 rather than real-market prices;
4. use no historical/canonical candidate market data;
5. encode only what the visible fixture states — for C-001: a prior range, an upper-boundary wick/poke, close/return into the prior range, and lack of follow-through;
6. do not add labels such as `false breakout`, `buy`, `sell`, `expected`, family code, or any answer hint to the image;
7. generate structured input from the exact same bars used for the image;
8. render with the already integrated deterministic Jianghe visual renderer;
9. freeze the synthetic observation identity, structured-artifact identity, renderer/config identity, PNG SHA-256, and request identities before any paid call;
10. any change to the frozen bars after the first provider response invalidates comparability and requires a new explicit research-design version rather than silent repair.

The exact numeric bar recipe is an implementation detail inside this approved protocol, but it must pass an offline semantic inspection proving that the chart expresses the visible fixture and nothing from hidden/rubric/expected sections.

### 4. Fairness across providers

For a given track, all three providers receive semantically identical governed content:

- same fixture identity;
- same selected Jianghe context;
- same underlying synthetic observation where applicable;
- same PNG bytes where applicable;
- same structured JSON bytes where applicable;
- same response schema semantics;
- provider-specific syntax only where required by the API contract.

No provider-specific prompt improvement is allowed after observing another provider's answer.

### 5. Offline freeze before first paid call

Before the first network request, commit a machine-readable Stage-A plan containing at least:

```text
provider/model set
five call slots per provider
track per slot
fixture id per content slot
synthetic observation identity
visual artifact identity / PNG hash where applicable
structured artifact identity where applicable
prompt/context/schema identities
inference configuration identities
per-provider Stage-A CNY6 envelope
Stage-A total CNY18 envelope
shared project CNY100 cap
```

The plan must be validated entirely offline. The provider response cannot influence fixture choice, bars, prompts, expected answers, or scoring rules.

### 6. Runtime engineering implication

The spend request/runtime is minimally generalized from “visual + structured always required” to a closed-world `input_track` contract:

- SEMANTIC requires semantic fixture text and forbids visual/structured artifacts;
- VISUAL requires visual and forbids answer-bearing semantic fixture text/structured artifact;
- STRUCTURED requires structured and forbids answer-bearing semantic fixture text/visual artifact;
- DUAL_INPUT requires visual + structured bound to the same observation;
- OPERATIONAL_PROVIDER uses its explicitly frozen smoke-input contract.

This change must not weaken existing content-addressing, provider authorization, budget, no-retry, outcome firewall, or evidence requirements. Unknown or mismatched combinations fail closed.

## What this approval does not authorize

This protocol does not change the existing CNY100 authorization and does not authorize:

- new providers/models;
- more than five Stage-A calls per provider;
- more than CNY6 Stage-A spend per provider or CNY18 total Stage-A spend;
- any new recharge/top-up without a specific amount returned to the Owner;
- outcome/PnL, Validation, Final, Shadow/Forward, Broker, or real-money access;
- PRIMARY semantic freeze;
- model/provider VERIFIED or ADOPTED status before evidence exists.

## Execution status at approval

```text
LIVE_CALLS=0
PAID_SPEND_CNY=0
STAGE_A=AUTHORIZED__INPUT_PROTOCOL_APPROVED__NOT_STARTED
NEXT=RUNTIME_GENERALIZATION__DETERMINISTIC_STIMULUS_FREEZE__OFFLINE_TESTS__CREDENTIAL_FUNDING_READINESS__STAGE_A
```
