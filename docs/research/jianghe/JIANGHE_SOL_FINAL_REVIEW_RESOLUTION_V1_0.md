# 江河交易员 Sol 最终复核结论 V1.0（001–099）

> Date: 2026-08-22  
> Scope: final source-faithful semantic closure for the Jianghe 001–099 corpus  
> Boundary: source distillation only; **not** outcome validation, PRIMARY selection, or machine authorization.

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..099
SOURCE_TOTAL=99
MEDIA_AVAILABLE=98
SEMANTICALLY_REVIEWED_WITH_RELIABLE_LANGUAGE_OR_BURNED_TEXT=97
VISUAL_ONLY_NO_RELIABLE_LANGUAGE=065
PAID_GATE_EXCEPTION=022
CORPUS_MEDIA_RECOVERY=COMPLETE
FINAL_SOL_REVIEW=COMPLETE
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
```

## 1. Final-review source dispositions

| Source | Final disposition | Source-faithful effect |
|---|---|---|
| 007 | `SOL_FINAL_REVIEWED / NATIVE_SRT_VALID` | Repaired media now supports the explicit priority `势/趋势 > 位/位置 > 态/形态`; unresolved overlap/contest should be waited out; candlestick form alone is not entry permission. |
| 016 | `SOL_FINAL_REVIEWED / LOCAL_ASR_ACCEPTED_LIMITED` | Confirms the framework name “势位态动” and that an initial system is built from four dimensions; does **not** define the four dimensions completely. |
| 017 | `SOL_FINAL_REVIEWED / LOCAL_ASR_ACCEPTED` | Pins three exit approaches: fixed R/R, key-location/space exit, and dynamic market-structure exit; source personally prefers dynamic. Pins stage-dependent exit: early trend can use right-side exit/give room; non-early can use earlier/left-side protection. |
| 018 | `SOL_FINAL_REVIEWED / LOCAL_ASR_ACCEPTED + SAME_TIME_VISUAL` | Reconfirms location is not a trigger; same-timeframe internal structure can help judge weakness/context but is not an independent trade opportunity. Real lower-timeframe trigger requires switching to that timeframe and reading its own structure. |
| 048 | `SOL_FINAL_REVIEWED / BURNED_TEXT_VALID / RECOVERED_SRT_REJECTED_WRONG_VIDEO` | Burned text directly states travel/environment caused lack of focus, so he did not dare use large size; “trading must be focused.” P&L list is case content only, not validity evidence. |
| 065 | `VISUAL_ONLY / LOCAL_ASR_REJECTED_SEMANTIC_HALLUCINATION` | No native subtitle. Generated ASR is semantically incompatible with the video and is rejected. No spoken trading logic is inferred from order/chart outcomes. Semantic claim count remains 0. |
| 099 | `SOL_FINAL_REVIEWED / BURNED_SUBTITLE_VALID / RECOVERED_SRT_REJECTED_WRONG_VIDEO` | Small capital is handled through position/risk allocation rather than a special strategy: higher-quality orders receive more risk budget, lower-quality orders less; account funds may be physically capped/separated to control tail risk and behavior. Dollar amounts are examples only. |

## 2. Exact review-queue resolutions

### JH-REV-008 / V030 — score threshold
The same source passage says both:
- orders are opened only when score is “高于三分”; and
- at score 3 the source gives a non-zero 3000-dollar position example.

Therefore the exact boundary cannot be uniquely pinned. Final status:

`CLOSED_SOURCE_INTERNAL_BOUNDARY_UNRESOLVED`

Do not choose `>3` or `>=3` for the author. The full score formula and exact 3-point permission remain `UNKNOWN`.

### JH-REV-009 / V065 — missing language evidence
Native subtitle absence was confirmed, but the local ASR output failed semantic plausibility review: it contains repetitive unrelated English text inconsistent with the source video. Final status:

`CLOSED_RELIABLE_LANGUAGE_UNAVAILABLE_ASR_REJECTED`

The source remains visually reviewable but has no reliable language evidence for strategy semantics.

### JH-REV-010 / V069 — internal vs external structure
V069 explicitly states that same-timeframe internal structure only helps confirm external structure and does not itself provide a trading opportunity or trading logic. If a lower-timeframe opportunity is desired, the trader must switch to that lower timeframe and identify its **own external structure** there.

V018 and later evidence are compatible with this distinction: internal structure may affect context, weakening/reclassification, management or defense references, but is not standalone entry permission.

Final status:

`RESOLVED_ROLE_SCOPE_INTERNAL_CONFIRMATION_NOT_ENTRY`

The machine algorithm for separating internal/external structure remains `UNKNOWN`.

### JH-REV-011 / V079 — entry-candle close stop
The source language/slide says that when the recent high/low is the current entry candle, stop may be at that candle’s “close”; same-source diagrams/examples place stops beyond the corresponding low/high. This is a genuine text/visual inconsistency.

Final status:

`CLOSED_SOURCE_INTERNAL_TEXT_VISUAL_CONFLICT`

Stable structural/recent-high-low stop semantics remain usable. “Entry-candle close stop” is **not** machine-eligible unless the author later clarifies it.

### JH-REV-012 / V078 — exact 50/50 candle
The source defines:
- body share `>= 50%` → trend-type candle;
- wick share `>= 50%` → non-trend candle.

Exactly 50/50 satisfies both written definitions. Final status:

`CLOSED_SOURCE_DEFINITION_OVERLAP`

The tie remains `UNKNOWN`; no project-authored `>`/`>=` tie-break is allowed.

### JH-REV-013 / V048 — subtitle status
The recovered remote SRT does not match the actual video and is rejected. Reliable semantics come only from directly visible burned text. Final status:

`CLOSED_REMOTE_SRT_WRONG_VIDEO_BURNED_TEXT_USED`

### JH-REV-014 / V099 — subtitle status
The recovered remote SRT does not match the actual video and is rejected. The video itself has usable burned subtitles throughout. Final status:

`CLOSED_REMOTE_SRT_WRONG_VIDEO_BURNED_SUBTITLE_USED`

### JH-REV-015 / V096 — three dimensions
Full-video burned subtitles pin the three source dimensions as:
1. trading driven by account P&L/funds change rather than market facts;
2. simultaneously watching account P&L and real market, creating internal conflict and execution deformation;
3. trading from K-line/market rhythm rather than emotions or account-funds change.

Final status:

`CLOSED_SOL_VERIFIED_FULL_VIDEO_BURNED_SUBTITLE`

## 3. Contradiction updates

- `JH-CON-005` → `RESOLVED_STAGE_DEPENDENT`: V017 explicitly separates early-trend right-side exit from non-early earlier/left-side exit.
- `JH-CON-006` → `PARTIALLY_RESOLVED_QUALITY_RISK_HIERARCHY`: quality/score/state/context clearly modify size, and V099 adds quality-based risk allocation plus account-fund caps, but one universal mother sizing rule across all Families is not source-pinned.
- `JH-CON-007` → `RESOLVED_AS_SOURCE_INTERNAL_INCONSISTENCY / MACHINE_BOUNDARY_NOT_PINNED`.
- `JH-CON-016` → `RESOLVED_ROLE_SCOPE_INTERNAL_CONFIRMATION_NOT_ENTRY`.
- `JH-CON-019` → `RESOLVED_AS_SOURCE_INTERNAL_TEXT_VISUAL_CONFLICT / CLOSE_STOP_NOT_MACHINE_ELIGIBLE`.

## 4. ASR evidence-acceptance correction

The V065 failure establishes a project-level evidence rule:

```text
MODEL_IDENTITY_PASS
+ MODEL_LOAD_PASS
+ TIMESTAMP/COVERAGE_PASS
!=
SEMANTIC_LANGUAGE_EVIDENCE_PASS
```

Before local ASR may support a source claim, beginning/middle/end spot checks must confirm:
- expected source language;
- semantic plausibility relative to audible speech;
- no obvious repetitive hallucination or unrelated-language drift;
- rough audio/text agreement.

If these fail, the transcript is `REJECTED_AS_LANGUAGE_EVIDENCE`; no trading claim may be derived from it.

## 5. Final family decision

No new independent mechanism is justified. Core Families remain exactly A–D. Scalping remains a non-core execution mode. Moving averages remain auxiliary usage.

## 6. Research boundary

This V1.0 closes the **Jianghe source-distillation pass**, not project validation.

```text
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
REAL_MONEY=NOT_AUTHORIZED
```
