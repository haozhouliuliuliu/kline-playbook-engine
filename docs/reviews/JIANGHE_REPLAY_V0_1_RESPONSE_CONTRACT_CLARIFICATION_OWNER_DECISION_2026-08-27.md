# JIANGHE REPLAY V0.1 RESPONSE CONTRACT CLARIFICATION — OWNER DECISION

Status: `OWNER_APPROVED__IMPLEMENT_BEFORE_PROVIDER_RETEST`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

## Trigger

The first real provider-smoke request reached the adopted DeepSeek path and returned valid JSON, but the provider emitted `numeric_claims` as a JSON object rather than the strict array required by `JIANGHE_RUNTIME_RESPONSE_V0_1`. The project normalizer correctly rejected the response and the original paid slot stopped fail-closed.

Canonical evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

## Owner decision

The response schema itself remains correct and stays frozen:

`RESPONSE_SCHEMA_VERSION = JIANGHE_RUNTIME_RESPONSE_V0_1`

The project must **not** add a permissive object-to-array compatibility coercion in the normalizer. Such coercion could silently discard or invent `unit` / `source_reference` provenance and would weaken the existing fail-closed contract.

Instead, the trading-only prompt contract must be clarified so the provider receives the exact serialization requirements that the normalizer already enforces.

This is a serialization-contract clarification, not a change to Jianghe trading semantics, market interpretation, action semantics, causal data, wake policy, sample, product, model, memory policy, or V0.1 research purpose.

## Required prompt-contract change

Create a new prompt-contract identity/version, expected naming:

`KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_2`

The system prompt's trading scope remains materially unchanged. The decision prompt must explicitly state the exact JSON shapes, including at minimum:

- top level remains the exact existing field set;
- `declared_unknown` is a JSON array of strings;
- `principle_references` is a JSON array of strings;
- `source_references` is a JSON array of strings;
- `numeric_claims` **must be a JSON array**;
- zero numeric claims must be represented as `[]`;
- each `numeric_claims` item must contain exactly:
  - `claim` — non-empty string;
  - `value` — finite decimal encoded as a string;
  - `unit` — string or `null`;
  - `source_reference` — string or `null`;
- a label->value JSON object/map is forbidden for `numeric_claims`;
- no markdown or prose may surround the JSON object;
- no extra top-level or nested claim keys may be introduced.

The implementation should use an explicit structural template or equivalent unambiguous serialization instruction without inserting fabricated market values.

## What must remain unchanged

Do not change:

- `JIANGHE_RUNTIME_RESPONSE_V0_1` accepted semantic fields;
- `JiangheResponseNormalizer` strict rejection of unknown fields;
- `numeric_claims` canonical normalized representation;
- forbidden outcome/PnL/self-evaluation fields;
- product `cu` / contract `SHFE.cu2406`;
- sealed slice and governed wakes;
- `EVERY_NEW_CLOSED_5M_BAR`;
- causal `4H / 1H / 15m / 5m` observation;
- model `deepseek-v4-flash-vision-exp`;
- DeepSeek Harness pin;
- zero-retry rule;
- one-wake/one-provider-request rule;
- no learning/policy promotion;
- full V0.1 replay lock.

## Fail-closed observability repair

Ordinary engineering is also authorized to ensure provider usage/request metadata survives a schema-rejection path.

After a provider response is received but before/while normalization is attempted, the project must durably retain, when supplied by the provider/bridge:

- request id;
- usage/token fields;
- model identity;
- response raw hash / raw-response audit lineage;
- rejection reason.

A normalizer rejection must still stop execution immediately, but it must not cause already-received billing/usage metadata to be lost merely because evidence serialization happens after normalization.

No secret value may be persisted.

## Verification before any new paid call

Before a new provider retest may become executable:

1. focused prompt/normalizer tests must pass;
2. the normalizer must still reject object-shaped `numeric_claims`;
3. a conforming array-shaped response must normalize successfully;
4. provider-smoke mock/loopback rehearsal must pass with the new prompt identity;
5. fail-closed usage/evidence persistence must be tested;
6. full repository regression and authority-consistency checks must pass;
7. the exact execution-critical code and new prompt/context/renderer identities must be resealed into a new machine authority.

## Prior failed call and retest semantics

The prior rejected provider response produced no normalized trading decision and no accepted trading-state mutation. It remains immutable diagnostic evidence and must not be supplied to the model as trading context.

A separately authorized fresh provider-smoke retest may therefore start again from the same first sealed governed wake using a clean pre-smoke state. This is an explicit protocol-repair retest, not an outcome-driven attempt to obtain a nicer trading answer.

The new paid authority is separate from the consumed original slot.
