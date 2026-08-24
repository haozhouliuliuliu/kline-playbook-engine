# JIANGHE STAGE-A PRE-EXECUTION HANDOFF — 2026-08-24

> Status: `CURRENT_PREEXECUTION_CHECKPOINT`
> Purpose: durable handoff for a fresh project-brain conversation before the first paid Stage-A model call.
> Canonical authority remains current GitHub `main`; this file is a compact execution checkpoint, not a substitute for `CURRENT_STATE.md` or `PROJECT_BRAIN_RUNTIME_BRIEF.md`.

## 1. Current material checkpoint

```text
OWNER_PAID_CALL_DECISION=AUTHORIZED
PAID_CALL_AUTHORIZATION_ID=OWNER-PAID-JIANGHE-FIDELITY-20260824-V01
AUTHORIZED_PROVIDER_MODELS=KIMI:kimi-k3,DEEPSEEK:deepseek-v4-flash-vision-exp,MINIMAX:MiniMax-M3
TOTAL_HARD_API_SPEND_CAP_CNY=100.00
STAGE_A_MAX_SPEND_CNY=18.00
STAGE_A_MAX_CALLS=15
NEW_RECHARGE_OR_TOPUP=NOT_AUTHORIZED_WITHOUT_SPECIFIC_AMOUNT_OWNER_CONFIRMATION
LIVE_CALLS=0
PAID_SPEND_CNY=0
OUTCOME_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

The paid-call authorization is already recorded in:

- `docs/evidence/JIANGHE_OWNER_PAID_CALL_DECISION_20260824_V0_1.md`
- `docs/evidence/JIANGHE_PAID_CALL_AUTHORIZATION_CURRENT.json`

The current authorization expires at `2026-08-31T00:00:00+08:00` unless superseded.

No provider/model is project `VERIFIED` or `ADOPTED` yet. `LIMIT-012` remains active until real-model Jianghe fidelity evidence exists.

## 2. Owner-approved Stage-A research design

Owner approved the Stage-A input/modality and synthetic visual-stimulus protocol on 2026-08-24.

Binding authority:

- `docs/reviews/JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md`

The approval freezes:

```text
QUALIFICATION_FIXTURE=JH-FIX-C-001
TRACK_ISOLATION=YES
SYNTHETIC_OHLC_FROM_VISIBLE_INFORMATION_ONLY=YES
SAME_UNDERLYING_OBSERVATION_FOR_VISUAL_STRUCTURED_DUAL=YES
FREEZE_ALL_STIMULUS_IDENTITIES_BEFORE_FIRST_PAID_CALL=YES
```

Stage-A content-track semantics:

```text
SEMANTIC = fixture visible-information text only; no image; no structured market artifact
VISUAL = deterministic K-line image only; no answer-bearing fixture prose; no structured artifact
STRUCTURED = governed structured observation only; no image; no answer-bearing fixture prose
DUAL_INPUT = same-observation deterministic image + governed structured observation
OPERATIONAL_PROVIDER = minimum governed smoke request for exact model/API/schema/usage/evidence verification
```

All three providers must receive semantically identical governed content for a given track; provider-specific syntax changes are allowed only where required by the API contract.

## 3. Synthetic visual stimulus boundary

Stage-A uses the already-existing non-outcome fixture:

```text
FIXTURE_ID=JH-FIX-C-001
PATTERN=FALSE_BREAKOUT__WICK_POKE_RETURN_NO_FOLLOW
```

The exact numeric OHLC bars have **not yet been frozen** at this checkpoint. They must be generated mechanically from only the fixture's visible information and source-authorized Jianghe semantics.

Hard constraints before first network call:

1. normalized synthetic price scale around 100;
2. no real/canonical candidate market data;
3. no hidden-future information;
4. no outcome/PnL/result access;
5. encode only prior range + upper-boundary wick/poke + return/close into range + lack of follow-through;
6. no chart labels that reveal the answer/family/trade direction;
7. image and structured artifact must derive from the exact same synthetic bars;
8. use the existing deterministic Jianghe visual renderer;
9. freeze synthetic observation identity, structured identity, renderer/config identity and PNG SHA-256 before any paid call;
10. once the first provider response exists, the bars/stimulus/prompt/expected/scoring rules may not be silently changed.

Do not invent a different fixture or visually tune bars after seeing provider output.

## 4. Engineering work still required before first paid call

The current spend runtime was repaired for safe paid use but historically assumed visual + structured artifacts together. The approved Stage-A protocol requires a minimal closed-world generalization to explicit `input_track` semantics.

Required implementation:

```text
SEMANTIC -> require semantic fixture text; forbid visual/structured artifacts
VISUAL -> require visual artifact; forbid answer-bearing fixture text and structured artifact
STRUCTURED -> require structured artifact; forbid visual and answer-bearing fixture text
DUAL_INPUT -> require visual + structured bound to the same observation
OPERATIONAL_PROVIDER -> explicit frozen smoke-input contract
UNKNOWN/MISMATCHED_COMBINATION -> FAIL_CLOSED
```

This change must preserve all already-closed pre-spend guarantees:

- content-addressed Jianghe context;
- closed-world structured observation;
- evaluator-side scoring authority;
- exact provider/model authorization;
- CNY100 shared executable hard cap;
- no automatic semantic retry;
- raw response / usage / identity evidence;
- outcome firewall;
- credential secrecy.

## 5. Stage-A runner requirements

Build one deterministic, resumable runner; do not create a second semantic/evaluation stack.

Before the first paid request it must commit/freeze a machine-readable plan containing at least:

```text
3 provider/model identities
5 Stage-A call slots per provider
track for every slot
JH-FIX-C-001 for content slots
synthetic observation identity
visual artifact identity / PNG SHA-256 where applicable
structured artifact identity where applicable
prompt/context/schema identities
inference configuration identities
CNY6 per-provider Stage-A envelope
CNY18 total Stage-A envelope
CNY100 shared project hard cap
```

Operational requirements:

- one shared persistent budget ledger across all providers;
- evidence persisted after every call;
- safe restart without repeating a successfully billable request;
- no semantic retry;
- provider eliminated immediately on fixed severe-failure conditions;
- no Stage-B call until Stage-A evidence and ranking are committed.

## 6. Provider/cost state

Current conservative spend guards:

```text
KIMI_K3: input 20 CNY/MTok; output 100 CNY/MTok; 1024 input tokens/image
DEEPSEEK_V4_FLASH_VISION_EXP: peak cache-miss input 3 CNY/MTok; output 9 CNY/MTok; <=384 input tokens/image
MINIMAX_M3: conservative >512K tier input 4.2 CNY/MTok; output 16.8 CNY/MTok; image billed through input-token accounting
```

Owner pricing fallback rule is adopted:

- if exact price is unavailable, use same-provider same-family / sibling-tier public pricing conservatively;
- choose the more expensive applicable tier;
- do not assume cache, off-peak or promotional discounts;
- an unknown billing unit/semantics still fails closed rather than being guessed.

DeepSeek Vision Exp remains an approved direct-visual candidate. Its same-price/base-performance relationship to V4 Flash plus added multimodality is provider/Owner-level product information; it is not project fidelity `VERIFIED` evidence.

## 7. Existing verification baseline

Pre-spend repair is already closed and integrated:

```text
BSP-001..005=CLOSED
RSP-001..002=CLOSED
PRE_SPEND_REPAIR_REAUDIT=PASS
FOCUSED_ADVERSARIAL=PASS__162_TESTS
CANONICAL_FULL_SUITE=PASS__1226_TESTS__27_SKIPPED
```

Provider pricing refresh was subsequently integrated and offline-gated. Do not reopen those findings absent concrete current-repo correctness evidence.

## 8. Exact next sequence for a fresh conversation

```text
1. Fetch current main HEAD.
2. Read 00_READ_FIRST.md and PROJECT_BRAIN_RUNTIME_BRIEF.md.
3. Refresh CURRENT_STATE.md.
4. Read this handoff and JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md.
5. Implement the minimal input_track runtime generalization.
6. Mechanically generate and freeze the exact JH-FIX-C-001 synthetic OHLC stimulus + machine-readable Stage-A plan.
7. Run focused adversarial tests + canonical full suite + diff hygiene.
8. Check only credential presence and existing balance/credits without exposing secrets.
9. If any new recharge/top-up is required, return the exact amount to Owner; do not fund automatically.
10. If existing credentials/funds suffice, execute Stage A only: max 5 calls/provider, max CNY6/provider, max CNY18 Stage A, shared CNY100 total ledger.
11. Persist evidence after every call and commit Stage-A ranking before any Stage-B activity.
```

## 9. Tool decision

```text
TOOL_DECISION=USE_EXISTING
```

No new framework/tool is required for this work. Codex is optional only if the runtime generalization or integration becomes genuinely complex; it is not currently a blocker.

## 10. Safety checkpoint

At this handoff:

```text
LIVE_CALLS=0
PAID_SPEND_CNY=0
STAGE_A=AUTHORIZED__PROTOCOL_APPROVED__NOT_STARTED
OWNER_ACTION=NONE_NOW__RETURN_ONLY_FOR_SPECIFIC_NEW_RECHARGE_TOPUP_AMOUNT_OR_NEW_MAJOR_DECISION
```
