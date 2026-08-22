# 江河交易员当前研究视图 V1.1 — Exhaustive Second-Pass Source Distillation

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..099
SOURCE_TOTAL=99
MEDIA_AVAILABLE=98
PAID_GATE_EXCEPTION=022
FULL_TIMELINE_SECOND_PASS_AVAILABLE_MEDIA=98
SECOND_PASS_AVAILABLE_SOURCE_DURATION_COVERAGE=100%
SECOND_PASS_UNACCOUNTED_TIMELINE_GAP=0
UNEXPLAINED_ZERO_CLAIM_AVAILABLE_SOURCE=0
VISUAL_ONLY_NO_RELIABLE_LANGUAGE=065
RECOVERED_REMOTE_SRT_USED_WITHOUT_IDENTITY_QA=0
SECOND_PASS_SOURCE_COVERAGE_AUDIT=COMPLETE
FINAL_SOURCE_DISTILLATION=COMPLETE_V1_1_AFTER_CORRECTIVE_SECOND_PASS
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
TOOL_DECISION=USE_EXISTING
```

## Why V1.1 exists

V1.0 was reopened because the old 001–028 evidence package was too sparse to prove exhaustive coverage. The second pass confirmed real under-extraction: several long/meaningful early sources had zero or very few formal claims despite containing system construction, review process, structure, risk, entry/management and other material semantics.

V1.1 therefore does **not** simply restore the old V1.0 completion flag. It completes a corrective full-timeline pass across all 98 accessible sources and records the recovered semantics separately.

## Current authority order

1. `JIANGHE_CURRENT_VIEW_V1_1.md`
2. `JIANGHE_TRADER_DOSSIER_V1_1.md`
3. `JIANGHE_SECOND_PASS_RECONCILIATION_V1_1.md`
4. `second_pass_salvage/SECOND_PASS_SALVAGE_MANIFEST_V1_1.md`
5. `second_pass_salvage/JIANGHE_SECOND_PASS_SOURCE_COVERAGE_RECORD_V1_1.part00..03.csv` — reconstruct to the canonical 99-source coverage record using the manifest hashes.
6. `second_pass_salvage/JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part00..03.jsonl` — reconstruct to the canonical 64-claim recovery delta using the manifest hashes.
7. `JIANGHE_SOL_FINAL_REVIEW_RESOLUTION_V1_0.md` — targeted-review decisions retained unless superseded by V1.1.
8. Existing V0.1–V0.9 claim/case/source artifacts — prior evidence history remains part of the cumulative evidence base.

## Corrective audit result

The second-pass coverage record proves:

```text
DATA_ROWS=99
UNIQUE_SOURCE_ORDINALS=99
MISSING_ORDINALS=NONE
DUPLICATE_ORDINALS=NONE
ACCESSIBLE_SOURCES=98
ALL_ACCESSIBLE_TIMELINES=FULL_TIMELINE_REVIEWED_0_TO_END
NONZERO_UNACCOUNTED_TIMELINE_GAPS=NONE
PAID_GATE_EXCEPTION=022
VISUAL_ONLY_NO_RELIABLE_LANGUAGE=065
```

The second-pass recovered-claim delta contains:

```text
JSONL_RECORDS=64
VALID_JSON_RECORDS=64
UNIQUE_CLAIM_IDS=64
```

Exact checksums and reconstruction instructions are frozen in `SECOND_PASS_SALVAGE_MANIFEST_V1_1.md`.

## Material corrections from the second pass

- Early under-extraction was real. `003`, `010`, `019`, `025`, `026` and several other long sources contained material semantics not adequately represented by their old zero/low-claim records.
- The complete system-building/review loop is now first-class evidence rather than background prose.
- Risk evidence is richer: tolerated loss, stop distance, quality/score/context-based risk, planned staged entries and account-level caps/separation coexist; no universal account-risk percentage is source-pinned.
- Trend quality/stage and regime-specific method selection are better supported.
- Breakout and range mechanisms gained materially more positive/negative-case detail.
- No independent fifth strategy mechanism emerged. Families remain A–D.

## Language/provenance fail-closed decisions

- `009` / `014`: remote-recovered SRTs were not trusted after the recovered-subtitle contamination issue; second-pass semantics use burned text/visual evidence rather than those un-revalidated tracks.
- `048` / `099`: recovered remote SRTs are confirmed wrong-video and rejected.
- `065`: local ASR is rejected for semantic hallucination; the video remains visual-only and semantic claim count remains 0.

## Family state

Exactly four core mechanisms remain:

- `JH-FAMILY-A` — trend key-location pullback continuation
- `JH-FAMILY-B` — trend weakening reversal / higher-timeframe pullback
- `JH-FAMILY-C` — confirmed breakout
- `JH-FAMILY-D` — range-boundary reversal

`SCALPING_EXECUTION_MODE` remains non-core. MA/EMA remains optional auxiliary evidence, not a core strategy family.

## What remains intentionally UNKNOWN

The second pass closes coverage gaps; it does not invent missing author semantics. Important remaining non-lockable items include:

- V030 exact score=3 entry boundary;
- V078 exact 50/50 candle tie;
- V079 entry-candle-close stop text/visual conflict;
- exact algorithms for key zones, strength, second-push quality, trend stage and vacuum areas;
- one universal cross-Family risk mother formula/account percentage;
- reliable spoken strategy language for 065.

## Research boundary

V1.1 completes the **source-distillation coverage pass** only.

```text
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
REAL_MONEY=NOT_AUTHORIZED
```

`SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION` and `UNKNOWN > GUESSING` remain binding.
