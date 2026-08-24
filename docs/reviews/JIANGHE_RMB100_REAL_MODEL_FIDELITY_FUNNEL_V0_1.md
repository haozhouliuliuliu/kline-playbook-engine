# JIANGHE RMB100 REAL-MODEL FIDELITY FUNNEL V0.1

Status: `READY_FOR_OWNER_PAID_CALL_DECISION__NOT_AUTHORIZED`
Date: 2026-08-24
Purpose: bounded non-outcome real-model Jianghe fidelity qualification and stability comparison.
Tool decision: `USE_EXISTING`

## Hard boundaries

```text
TOTAL_API_SPEND_CAP_CNY=100.00
PAID_MODEL_SPEND=NOT_AUTHORIZED
LIVE_CALLS=0
OUTCOME_ACCESS=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
AUTOMATIC_SEMANTIC_RETRY=FORBIDDEN
PROVIDER_TOOLS_OR_SEARCH=DISABLED
```

This plan does not authorize a call. A separate committed Owner paid-call authorization remains mandatory before network access.

The CNY100 executable ledger is the API-consumption ceiling. Any account top-up/recharge is a separate external cash action and must also remain within the Owner-approved cash exposure; the project must check each provider's current minimum recharge and existing account balance before asking the Owner to fund anything.

## Eligible implementation set

```text
KIMI_K3=SPEND_GUARD_READY__CANDIDATE
DEEPSEEK_V4_FLASH_VISION_EXP=SPEND_GUARD_READY__EXPERIMENTAL__CANDIDATE
MINIMAX_M3=SPEND_GUARD_READY__CANDIDATE
```

None is project-`VERIFIED` or `ADOPTED`.

Current conservative rate-card authority: `docs/evidence/JIANGHE_PROVIDER_PRICING_AUTHORITY_V0_1.json`.
Current fallback policy: `docs/reviews/PROVIDER_PRICING_FALLBACK_POLICY_V0_1.md`.

## One paid call

Every paid fidelity call uses the same governed production-like boundary: content-addressed Jianghe context, closed-world structured observation, canonical K-line visual input, strict output normalization, requested/resolved model identity capture, tools/search disabled, exact pre-network budget reservation, and no automatic retry.

Required evaluation tracks remain:

```text
SEMANTIC
VISUAL
STRUCTURED
DUAL_INPUT
OPERATIONAL_PROVIDER
```

A track is an evaluator focus, not permission to create a weaker side protocol. A production-like call may contribute evidence to more than one track.

Default probe output ceiling: `MAX_COMPLETION_TOKENS=1024`.

## Stage A — tiny qualification funnel

```text
PROVIDERS=3
MAX_CALLS_PER_PROVIDER=5
MAX_STAGE_A_CALLS=15
MAX_CNY_PER_PROVIDER=6.00
STAGE_A_TOTAL_ENVELOPE_CNY=18.00
```

Five focused calls per provider at most:

1. `OPERATIONAL_PROVIDER_SMOKE` — route/model identity, multimodal acceptance, schema/usage evidence.
2. `SEMANTIC_HARD_NEGATIVE` — Jianghe hard-negative reasoning; WAIT/NO_TRADE must remain legitimate.
3. `VISUAL_KLINE_READ` — chart interpretation where wick/location/structure detail matters.
4. `STRUCTURED_OBSERVATION` — canonical structured state without invented fields/thresholds.
5. `DUAL_INPUT_CONSISTENCY` — visual and structured evidence must not produce an unexplained contradiction.

Fatal stop conditions include: wrong/unusable route after configuration is verified, inability to accept canonical visual input, unscoreable normalized response, missing required identity evidence, dependence on tools/search, forbidden outcome/future reference, invented hard risk/UNKNOWN-as-permission, or inability to fit the deterministic stage budget.

Advance rule:

```text
OPERATIONAL_PROVIDER=PASS
FATAL_FAIL=0
CONTENT_FOCUS_PASS_COUNT>=3_OF_4
DUAL_INPUT_UNEXPLAINED_CONTRADICTION=0
```

An eliminated provider receives no Stage-B budget.

## Stage B — only top one or two

Qualifiers are ranked only on Jianghe fidelity and operational validity, with no PnL/outcome evidence. Ranking order is lexicographic: fatal-fail count; hard-negative/semantic pass count; visual fidelity; structured fidelity; dual-input consistency; repeat stability; and only if fidelity is effectively tied, cost/latency as an operational tie-breaker.

At most two advance.

### Top-1 stability lane

```text
ENVELOPE_CNY=42.00
MAX_CALLS=12
```

Use the governed fixture corpus across A/B/C/D plus NONE/hard-negative behavior, preferring paired positive/negative cases and repeats on the highest-disagreement fixtures.

### Top-2 comparison lane

```text
ENVELOPE_CNY=28.00
MAX_CALLS=8
```

Use the same core fixture subset as the top-1 lane for like-for-like comparison.

### Tie/disagreement reserve

```text
ENVELOPE_CNY=12.00
MAX_CALLS=4
```

Use only if the top two remain materially unresolved. Calls must be paired on the same disputed fixtures. Otherwise this reserve remains unspent.

## Total funnel ceiling

```text
STAGE_A=18.00
TOP1_STABILITY=42.00
TOP2_COMPARISON=28.00
TIE_RESERVE=12.00
TOTAL=100.00
MAX_TOTAL_CALLS=39
```

These are ceilings, not spending targets. Unused budget remains unspent. No eliminated provider receives recycled budget. No extension above CNY100 is automatic.

## Per-call budget enforcement

Immediately before every request: reload current repository pricing authority; verify freshness; build the exact payload; compute the canonical conservative input/image/output bound; reserve worst-case CNY cost in the single shared ledger; check the global and stage/provider envelope; only then allow the HTTP seam.

If provider usage is unavailable or cannot be reconciled, the full reservation is charged against the ledger before any later call.

## Result semantics

```text
NO_MODEL_QUALIFIES
ONE_MODEL_QUALIFIES
TOP_MODEL_CLEAR
TOP_TWO_UNRESOLVED
```

`TOP_MODEL_CLEAR` means only the best Jianghe-fidelity candidate under this bounded probe. It does not mean profitable, production-adopted, broker-authorized, or real-money-ready.

## Owner gate

The next Owner decision is narrowly scoped: authorize or decline this bounded paid-call funnel, hard-capped at CNY100 API consumption with no outcome/PnL access.

If authorized, the project must commit the closed-world paid-call authorization artifact before the first provider request. Credentials/funding remain separate and must never be pasted into repository evidence or logs.
