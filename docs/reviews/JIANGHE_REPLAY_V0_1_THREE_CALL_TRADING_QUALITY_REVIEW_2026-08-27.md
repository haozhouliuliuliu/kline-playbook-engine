# Jianghe Replay V0.1 — Three-Call DeepSeek Trading-Quality Review

Status: `PRELIMINARY_TRADER_BEHAVIOR_ACCEPTABLE_WITH_MATERIAL_MEMORY_FIDELITY_GAP`

Date: `2026-08-27`

Scope: read-only adjudication of the three successful V0.2 provider-smoke decisions already extracted from retained local evidence. No provider request, future bar, post-decision outcome, PnL, win/loss label, or profitability evidence is used.

Primary evidence:

- `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_DECISIONS_2026-08-27.md`
- `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_DECISIONS_2026-08-27.json`
- `docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`
- `docs/research/jianghe/JIANGHE_CLAIM_LEDGER_DELTA_034_039_V0_3.jsonl`
- `docs/research/jianghe/JIANGHE_CLAIM_LEDGER_DELTA_040_043_V0_3.jsonl`
- `src/replay_v0_1_orchestrator.py`

## 1. Headline adjudication

The three-call trader behavior is **preliminarily acceptable** for a smoke-level trading-quality read: DeepSeek did not chase the first bullish impulse, did not invent an entry after the second bar, remained directionally coherent through the forced restart, and tightened its conditional interpretation as the pullback deepened.

However, the completed smoke also exposes one material implementation gap for the intended full V0.1 lifecycle experiment: important model-owned trading state such as key locations, expected trigger, invalidation, current market hypothesis and watch regions is expressed in free-text rationale but is not preserved as first-class structured working memory by the current projection/persistence path. Because V0.1 explicitly tests one persistent trader and its causal memory, this gap should be repaired offline before asking the Owner to authorize the full paid replay.

No full V0.1 provider execution is authorized by this review.

## 2. Decision sequence

### Call 1 — 13:05 UTC

Observed behavior:

- `ACTION = WATCH`
- `DIRECTION = LONG`
- `FAMILY = NONE`
- recognized a strong first night-session 5m bullish impulse;
- explicitly refused to enter on direction/momentum alone;
- waited for pullback/retest or secondary confirmation.

Assessment: **good restraint / coherent**. The model did not equate a large breakout bar with an automatic entry.

### Call 2 — 13:10 UTC

Observed behavior:

- remained `WATCH / LONG / NONE`;
- recognized the second 5m bar made a higher high (`76830`) but closed back at `76750`;
- required a pullback hold and another push rather than chasing;
- explicitly watched `76620` and `76830` as near-term conditions.

Assessment: **coherent continuation**, with one factual wording error noted below.

### Call 3 — 13:15 UTC, after forced project-owned restart

Observed behavior:

- remained `WATCH / LONG / NONE` after restart;
- noticed the 15m/5m pullback to `76590` and close at `76640`;
- explicitly acknowledged that the prior `76620` watch level had been breached intrabar;
- shifted attention to the older `76560` prior swing high;
- stated a conditional interpretation: hold/reversal at `76560` keeps a long candidate alive; break of `76560` invalidates the long idea.

Assessment: **restart continuity and adaptive reasoning are good**. This is not an unacknowledged goalpost move: call 2 did not declare `76620` as a hard stop; call 3 explicitly records that it failed and downgrades the thesis to the next structurally older level.

## 3. Positive findings

### A. No impulse chasing

Across all three calls, DeepSeek kept `ACTION = WATCH`. It did not convert the first large bullish bar into an immediate `ENTER` simply because price and momentum were strong.

### B. Stable directional state

The sequence is internally coherent:

`SCAN/NONE -> WATCH/LONG -> WATCH/LONG -> WATCH/LONG`

The forced restart after call 2 did not reset the prior trading stance. Call 3 had the prior `WATCH / LONG` state available and reasoned from it.

### C. Explicit uncertainty

The model repeatedly declared missing confirmation and did not claim unavailable higher-timeframe evidence. This is aligned with the frozen V0.1 requirement to state uncertainty rather than invent missing facts.

### D. Numeric level reading is mostly grounded

The key values cited by the model are present in the causal observation:

- first 5m close `76780`;
- first 5m high `76810`;
- second-step high `76830`;
- first night-session low `76620`;
- third-step pullback low `76590`;
- 15m close `76640`;
- prior 1H/4H high `76560`.

No future level was required to support the three judgments.

## 4. Trading-quality findings / problems

### Finding TQ-01 — one source-faithfulness error

DeepSeek repeatedly cites `JH-CLM-034-002` to support the statement that a real entry typically appears after a new launch point from a push-pull-push.

That is not what the canonical claim primarily says.

`JH-CLM-034-002` is a **management** claim: after a profitable order, a newly formed launch/defensive structure can be used to advance the stop, and failure of a second push to break the prior high is an exit/momentum-weakening clue.

Therefore the model converted a post-entry management observation into a pre-entry requirement. This did not cause an unsafe entry in the three-call sample — in fact it made the model more conservative — but it is a real Jianghe attribution/fidelity defect and should be tracked in later evaluation.

By contrast, `JH-CLM-042-002` is applied appropriately: direction/momentum/location alone do not automatically trigger a trade; a defined location plus an explicit rejection/entry signal is still required.

Adjudication: `TRADING_REASONING_FIDELITY_FINDING`, not a replay-integrity failure.

### Finding TQ-02 — factual wording imprecision in call 2

Call 2 says the night-session **open** gapped up to `76780/76810`.

The causal bar actually opened at `76720`, reached `76810`, and closed at `76780`.

The broader conclusion — a large upward opening gap/impulse relative to the prior session — remains directionally correct, but the wording conflates open, high and close.

Adjudication: `MINOR_MARKET_FACT_PRECISION_ERROR`; no observed decision-state consequence in this sample.

### Finding TQ-03 — evidence is too small to infer style quality

Three consecutive early-session wakes all produced `WATCH / LONG / NONE`. This is compatible with disciplined patience, but the sample is far too small to determine whether the trader is appropriately selective or pathologically reluctant to enter.

Adjudication: `NOT_ENOUGH_EVIDENCE`.

## 5. Material lifecycle implementation gap

### Finding MEM-01 — model trading state is richer than persisted structured memory

The frozen Owner authority assigns DeepSeek the trading task of determining, when warranted:

- current market state;
- important locations;
- active setup/family;
- direction/bias;
- expected trigger;
- invalidation;
- permitted working-memory updates.

The three real responses actually do state important locations, trigger conditions and invalidation in their rationale, especially call 2 and call 3.

But the current runtime projection deliberately constructs:

- `watch_regions = ()`;
- `invalidation = None`;
- `next_review = None`.

And `_apply_working_memory()` persists only:

- `attention_mode`;
- `last_meaningful_decision`;
- `transition_reason`;
- `directional_bias`;
- `active_family_hypothesis`.

Consequently fields already present in `DS_WORKING_MEMORY` — including `current_market_hypothesis`, `timeframe_trend_view`, `watch_regions`, `key_location_hypotheses`, `expected_trigger`, `invalidation_hypothesis`, `open_questions` and `review_at` — are not populated from the model's accepted trading judgment in this path.

The full rationale is retained in `transition_reason`, so the smoke does have continuity, but this is a lossy, unstructured substitute for the first-class memory model that V0.1 is intended to exercise.

Adjudication: `MATERIAL_RESEARCH_QUALITY_GAP_BEFORE_FULL_V0_1`.

This is not a reason to rewrite the three historical smoke decisions and does not invalidate the 3/3 provider-path/restart/schema result. It is a forward implementation issue.

## 6. Promotion semantics

- `SYSTEM_READY` for the narrow three-call provider path/schema/request-accounting/restart smoke: **YES**.
- `TRADER_BEHAVIOR_ACCEPTABLE` from these three calls: **PRELIMINARY YES, WITH TQ-01/TQ-02 FINDINGS**.
- `RISK_COMPATIBLE`: **NOT TESTED HERE**.
- `EVIDENCE_SUFFICIENT` for full trader-quality conclusions: **NO**.
- `PROFITABILITY_EVIDENCE`: **NONE**.
- `LONG_TERM_EDGE_EVIDENCE`: **NONE**.

## 7. Required forward work before asking for full V0.1 spend authority

1. Preserve historical smoke authority/evidence exactly as recorded.
2. Complete the already-required prospective logical-wake-selection identity vs runtime-wake identity separation before any future provider slot is resealed.
3. Repair the decision-response / project-memory contract so material trader-owned state — at minimum current market hypothesis, important locations/watch state, expected trigger and invalidation when supplied — can survive as explicit structured project-owned memory rather than only free-text transition rationale.
4. Add deterministic tests proving those fields persist causally and survive restart without semantic invention.
5. Keep Jianghe source attribution exact; add evaluator coverage for a claim being used outside its canonical category/meaning.
6. Re-adjudicate offline. Do not spend provider budget merely to verify deterministic persistence machinery.
7. If the repair changes the model-visible response/prompt contract, a later exact paid smoke/revalidation decision must be made under a new Owner/machine authority before full V0.1.

Until these steps are resolved, `FULL_V0_1_1998_CALL_REPLAY` remains locked.
