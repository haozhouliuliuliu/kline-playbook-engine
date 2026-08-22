# 江河 001–099 二次复核抢救快照 V1.1

> Status: DURABLE INTERMEDIATE SNAPSHOT
> Purpose: preserve current second-pass findings immediately; this is not a final dossier and must not be used to claim corpus completion.

## 1. Why this snapshot exists

Owner requested a full second-pass audit to eliminate the risk that earlier work only watched representative fragments, skipped sections, or compressed long videos too aggressively. The second pass confirmed that this risk was real, especially in the early corpus.

Therefore the previous V1.0 claim `FINAL_SOURCE_DISTILLATION=COMPLETE` remains revoked.

```text
SECOND_PASS_SOURCE_COVERAGE_AUDIT=OPEN
FINAL_SOURCE_DISTILLATION=REVOKED_PENDING_EXHAUSTIVE_SECOND_PASS
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
```

## 2. Confirmed under-extraction problem

The early `001–028` package was materially sparser than later batches. Multiple accessible long-form videos had `claim_count=0`, and several 8–36 minute videos had only 1–3 claims without full-timeline coverage records.

Second-pass review has already confirmed that at least some of those sparse records were under-extracted, not truly empty.

Examples already recovered during second pass:

- `003`: system-construction workflow was materially richer than the old zero-claim record: source materials -> first system draft -> historical feedback/classification refinement -> execution.
- `010`: contains a complete review loop: record -> decompose conditions -> classify -> identify successful/failed conditions -> intervene -> act again -> repeat.
- `019`: contains core semantics around N-structure, multi-timeframe structure, conditional reasoning, risk, fixed loss cost, dynamic holding and system execution; old zero-claim state was not an adequate representation.
- `025`: contains material live-trading/process evidence beyond the previous near-empty formal record.
- `026`: contains system construction, quality-based sizing/risk logic and execution material beyond the previous zero-claim representation.
- `021` and `024`: contain more detailed sizing split/addition/management/exit semantics than the old low-count summaries preserved.

These are evidence-completeness corrections. They do not automatically invalidate Family A–D, but they invalidate the claim that the first pass was exhaustive.

## 3. Subtitle identity contamination discovered

The corpus-recovery workflow mechanically recovered remote subtitle files for `009, 014, 048, 099`.

Final Sol review later proved `048` and `099` were wrong-video subtitle matches and rejected them. Therefore `009` and `014` cannot inherit semantic trust merely because remote retrieval, BVID/CID mapping and file naming succeeded. They require actual video-subtitle identity QA.

```text
REMOTE_DOWNLOAD_SUCCESS != SEMANTIC_IDENTITY_PASS
```

At minimum, beginning/middle/end must be checked against the actual video. Any mismatch must fail closed.

## 4. Current second-pass progress preserved from the active Sol session

The active review has re-opened the corpus from the beginning rather than only checking old claims. Work has already performed direct same-time visual inspection on multiple chart-dependent sources, including generated contact sheets/keyframes for `002`, `005`, `006`, `009`, `013`, `014`, `017`, plus later-batch visual material currently available in the active session.

The review must not be considered complete merely because a source has an old `SOL_ANALYZED` label.

For every accessible source, completion now requires a timeline coverage record with one of:

```text
NEW_CLAIM
DUPLICATE_SUPPORT
CASE_ONLY
PROCESS_ONLY
NO_TRADING_SEMANTIC
UNRELIABLE_LANGUAGE
NEEDS_SOL_REVIEW
```

## 5. Binding completion criteria

The exhaustive pass is complete only when all 98 accessible sources prove:

```text
AVAILABLE_SOURCE_DURATION_COVERAGE=100%
UNACCOUNTED_TIMELINE_GAP=0
CHART_DEPENDENT_CLAIM_WITHOUT_SAME_TIME_VISUAL=0
UNEXPLAINED_ZERO_CLAIM_AVAILABLE_SOURCE=0
SUBTITLE_VIDEO_IDENTITY_QA_REQUIRED=YES
UNRESOLVED_RECOVERED_SUBTITLE_IDENTITY=0
```

`022` remains the paid-gated legal exception. `065` remains visual-only unless reliable language evidence is obtained; its rejected hallucinated ASR cannot support semantic claims.

## 6. Preservation rule from this point forward

Do not wait until the entire second pass is complete before writing results. Every meaningful recovered batch must be written to durable repository artifacts and committed immediately in small batches. Interim artifacts must be explicitly labeled provisional/second-pass so partial work is not confused with final authority.

Full videos, complete subtitle corpora and large generated frame dumps remain outside Git unless later authority changes that storage boundary. Durable repository evidence should preserve conclusions, coverage records, hashes/paths and selected necessary visual evidence rather than duplicating the entire local corpus.
