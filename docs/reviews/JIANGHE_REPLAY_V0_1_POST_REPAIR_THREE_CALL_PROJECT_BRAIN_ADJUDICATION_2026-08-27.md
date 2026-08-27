# Jianghe Replay V0.1 — Post-repair Three-call Project-brain Adjudication

Status: `ADJUDICATED_PASS__FULL_V0_1_TECHNICALLY_READY__EXACT_PAID_EXECUTION_AUTHORITY_STILL_REQUIRED`

Date: `2026-08-27`

Canonical adjudication basis:

- `docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`
- `docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION_OWNER_DECISION_2026-08-27.md`
- `docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_EXECUTION_2026-08-27.md`
- `docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_RUN_2026-08-27.json`
- `docs/reviews/JIANGHE_REPLAY_V0_1_THREE_CALL_TRADING_QUALITY_REVIEW_2026-08-27.md`
- current Jianghe claim authority, including `JH-CLM-034-002`, `JH-CLM-034-003`, and the source-fidelity machinery.

No additional provider call was used for this adjudication.

## 1. Headline decision

The post-repair real-provider revalidation is accepted as a technical/model-contract PASS and closes the pre-full-V0.1 revalidation gate.

`FULL_V0_1_TECHNICAL_READINESS = PASS`

This does **not** itself authorize the paid full V0.1 replay. The full replay remains a new consequential paid execution and therefore still requires its own exact Owner execution authority and fresh machine-readable slot before any provider request.

## 2. System / provider integrity

`SYSTEM_READY_FOR_FROZEN_V0_1_LIFECYCLE_REPLAY = YES`

Observed real-path evidence:

- exactly `3` real provider attempts;
- exactly `3` provider results received;
- exactly `3` accepted normalized decisions;
- `0` retries;
- `0` hidden/auxiliary requests;
- no call 4;
- exactly `4` governed causal PNGs per call;
- both logical wake-selection identity and runtime wake identity matched the sealed authority for all three calls;
- provider/model/Harness identities matched the sealed execution contract;
- all attempt accounting was durable (`3 RESULT_RECEIVED`, `0 UNKNOWN_AFTER_ATTEMPT_START`, `0 unresolved`);
- the slot was terminalized to `REVOKED` and cannot be reused.

No replay-integrity invalidator from the frozen Owner protocol was observed in the three-call revalidation.

## 3. Persistent memory / restart objective

`STRUCTURED_TRADING_MEMORY_LIVE_REVALIDATION = PASS`

This is the most important result of the rerun because the previous three-call review exposed material gap `MEM-01`.

The real provider path now demonstrates first-class model-supplied persistence for:

- `current_market_hypothesis`;
- `timeframe_trend_view`;
- `key_location_hypotheses`;
- `expected_trigger`;
- `invalidation_hypothesis`;
- `open_questions`;
- plus directional/attention/last-decision state.

Causal continuity was directly evidenced:

- call 1 began from the expected empty baseline;
- call 2 received the accepted structured state from call 1;
- the project forced a restart after call 2;
- call 3 received the accepted full structured state from call 2 after reopen;
- restart continuity was `VERIFIED`.

Therefore the prior MEM-01 blocker is closed on the actual provider path, not merely by an offline unit test.

## 4. Trading-behavior adjudication

`TRADER_BEHAVIOR_ACCEPTABLE_FOR_PROCEEDING_TO_V0_1 = PRELIMINARY_YES`

All three post-repair calls remained `WAIT/WATCH` during the same early-session impulse/pullback sequence. That is not, by itself, a defect. The earlier read of the same three logical market opportunities found the restraint coherent: DeepSeek did not chase the first impulse, preserved directional context, and adapted conditionally as the pullback developed.

The post-repair execution summary shows canonical Jianghe references including `JH-CLM-034-003` and `JH-CLM-042-002`. The earlier material source-category misuse concerned `JH-CLM-034-002` (a MANAGEMENT claim incorrectly used as a pre-entry requirement). The current committed summary does not demonstrate recurrence of that specific misuse.

However, the new post-repair commit does not contain a separate full normalized-decision/raw-response extraction comparable to the historical retest decision package. Therefore this adjudication does **not** claim that every sentence, numeric description, or source attribution in all three new rationales has been independently re-read and certified.

That evidence-packaging limitation is not a V0.1 lifecycle-integrity blocker. It should be corrected prospectively for the full V0.1 run: complete per-wake normalized decision/state/source-reference evidence must be preserved so trading-quality review does not depend on retained local runtime state.

The prior TQ findings remain useful monitoring dimensions:

- exact Jianghe claim-category fidelity;
- precise OHLC wording;
- whether repeated WATCH behavior reflects appropriate selectivity or excessive reluctance.

These are trading-quality findings, not frozen V0.1 replay-integrity invalidators.

## 5. What this result does and does not establish

- `SYSTEM_READY`: **YES**, for the frozen V0.1 lifecycle/provider path.
- `STRUCTURED_MEMORY_CONTINUITY`: **YES**, live-provider verified.
- `RESTART_CONTINUITY`: **YES**.
- `TRADER_BEHAVIOR_ACCEPTABLE`: **PRELIMINARY YES / no current blocker demonstrated**.
- `RISK_COMPATIBLE`: **NOT TESTED**.
- `EVIDENCE_SUFFICIENT_FOR_FULL_TRADER_QUALITY_CONCLUSION`: **NO**; three calls are intentionally too small.
- `PROFITABILITY_EVIDENCE`: **NONE**.
- `LONG_TERM_EDGE_EVIDENCE`: **NONE**.

This is consistent with the frozen protocol: V0.1 is a lifecycle/memory/audit experiment, not a profitability backtest, and bad or missed trades are trading-quality evidence rather than lifecycle invalidators.

## 6. Promotion decision

The correct next project boundary is the **full frozen V0.1 chronological lifecycle replay**, not PAPER and not post-V0.1 CU/RB yet.

`PROMOTION_TO_FULL_V0_1_PREPARATION = APPROVED_BY_PROJECT_BRAIN`

Before any real full-V0.1 provider request:

1. create a new exact Owner paid/provider execution authority for the full frozen replay;
2. create and validate a fresh machine-readable authority bound to the exact current execution commit, sealed slice, provider/model/Harness/prompt/schema/runtime identities, wake policy and zero-retry policy;
3. preserve complete per-wake normalized trading decision/state/source-reference evidence during the full run;
4. preserve the existing fail-closed provider-attempt accounting and terminalization guarantees;
5. do not change the frozen V0.1 research semantics merely to improve apparent trading results.

Until the Owner grants that exact paid execution authority, `FULL_V0_1_1998_CALL_REPLAY` remains locked.

## 7. Post-V0.1 boundary

Only after the full frozen V0.1 lifecycle replay is completed and adjudicated should the project proceed to the already approved post-V0.1 sequence:

`CU chronological historical replay -> RB chronological historical replay -> focused CU/RB comparison -> conditional RB supplementation -> PAPER`.

This adjudication does not authorize those later paid/provider or execution stages.
