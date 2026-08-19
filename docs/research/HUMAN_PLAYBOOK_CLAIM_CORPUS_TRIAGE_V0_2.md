# HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_2

> Date: 2026-08-19
> Status: ACTIVE / NON_FROZEN / PRE_OUTCOME
> Supersedes current-action portion of: `docs/research/HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_1.md`
> Authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Source acquisition policy: `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`

## 1. Purpose

Record the result of the first semantic-completion attempt and select the smallest next source action without using outcomes or buying new data.

```text
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
```

## 2. First semantic-completion result

Target:
`STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION`

Integration review:
`docs/reviews/STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_SEMANTIC_COMPLETION_INTEGRATION_REVIEW_V0_1.md`

Result:

```text
SOURCE_FAITHFUL_PRICE_VOLUME_PLAYBOOK_DRAFTABLE=NO
PRICE_VOLUME_ONLY_FORMULATION_EXPLICITLY_SUPPORTED_BY_SOURCE=NO
PLAYBOOK_CONTRACT_CREATED=NO
```

The family remains useful source/process knowledge but is stopped as the current-data Playbook candidate because its reviewed real-time identification/entry logic materially uses NYSE TICK, Market Delta, breadth/participation and US sector/cross-market confirmation, while key price-side semantics remain under-specified.

No additional paid data is justified.

## 3. Source-reselection principle

The next candidate should maximize:
1. original/nearest-original free public provenance;
2. raw information-surface compatibility with current 1-minute OHLCV + governed session metadata;
3. explicit setup/context/invalidation/exit language;
4. failure/no-trade visibility;
5. enough source semantics to plausibly define one non-outcome Playbook Contract without parameter invention;
6. instrument/timeframe transfer must remain explicit or separately labeled INFERRED.

Selection must not use expected profitability or ease of producing a backtest.

## 4. Candidate comparison

### Brandt

Strengths:
- source-envelope is strongly price-chart/futures compatible;
- failure/risk visibility is good;
- longitudinal diary is attractive.

Current limitation:
- primary diary/book material is paid/publisher material.

Under `FREE_PUBLIC_UNAUTHENTICATED_FIRST`, Brandt remains a strong future candidate but is not the next default source package unless a sufficiently rich official free public bundle is found.

### Brooks

Strengths:
- bar/high/low/failed-breakout language is highly compatible with OHLCV;
- extensive source vocabulary and failure-aware concepts.

Current limitation:
- core books/course are paid and current official site states many articles/full functionality require registration/login;
- free public glossary/examples may be useful later but do not yet establish a sufficiently bounded source bundle for the next package.

Brooks remains a candidate, not next default.

### Raschke — selected next

Repository dossier:
`docs/research/source_dossiers/SOURCE_DOSSIER_RASCHKE_V0_1.md`

Existing classification:
`SOURCE_ADMISSION_CLASSIFICATION=PRIORITY_DEEP_DIVE`

Why selected:
- official site exposes a current free-resource library;
- free official material includes price/volume, day type/trade location, short-term pattern, mean-reversion/trend/breakout and related market-strategy content;
- dossier already identifies price bars/charts, volume and session context as a materially compatible information surface;
- mixed observability is known in advance, so Market Profile/richer inputs can be marked rather than proxied;
- this provides a genuinely different source lineage after Grimes/Steenbarger.

Selection is based on provenance + current-data compatibility + semantic potential, not performance expectation.

## 5. Tool decision for next package

The next source type includes video/multimodal material, so the project rechecks existing acquisition capability.

Authority:
`docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION.md`

Recorded capability:
- local `video-to-skill` multimodal sub-pipeline: VERIFIED for local media + sidecar transcript/frames/OCR/provenance;
- public YouTube URL acquisition: NOT_VERIFIED / blocked by 403 in the recorded environment;
- `video-transcribe-skill`: VERIFIED for local/offline Chinese no-caption fallback, with known non-exact transcript limitations;
- Docling: VERIFIED for document/layout extraction, not needed by default here.

Decision:

```text
TOOL_DECISION=USE_EXISTING
NO_NEW_TOOL_REQUIRED=YES
```

The Raschke package must not bypass anti-bot/cookie/auth restrictions. If an official free video cannot be lawfully/technically acquired into the verified local pipeline, use official free text/article material or another accessible official Raschke resource instead. Acquisition failure of one video is not permission to bypass access controls and is not a project-wide blocker.

## 6. Next bounded package

```text
NEXT_PACKAGE=RASCHKE_FREE_PUBLIC_CURRENT_DATA_COMPATIBILITY_SCREEN_AND_CLAIM_EXTRACTION_V0_1
SOURCE=SRC-RASCHKE
SOURCE_ACCESS=FREE_PUBLIC_UNAUTHENTICATED_ONLY
PRIMARY_GOAL=SELECT_AT_MOST_ONE_SOURCE_FAITHFUL_PRICE_VOLUME_SESSION_FAMILY_FOR_SEMANTIC_COMPLETION
OUTCOME_ACCESS=FORBIDDEN
```

Preferred official free material to screen first:
- `Volume and Price`;
- `Day Type, Taylor Trading, Trade Location, More`;
- `Mean Reversion, Trend Trading, and Breakouts`;
- `Short Term Scalping Patterns with Candlesticks`;
- official free articles when they provide stronger exact anchors or video acquisition is technically blocked.

Do not assume every listed item is technically downloadable. Verify access state first and stay within project safety policy.

## 7. Success condition

This package is not required to create a Playbook Contract.

Success means one of:

```text
A. RASCHKE_CURRENT_DATA_FAMILY_SELECTED=<one source-justified family>
   -> targeted semantic completion becomes next package

B. RASCHKE_CURRENT_DATA_FAMILY_SELECTED=NONE
   -> record why and reselect another public source
```

A `NONE` is valid evidence. No source is forced to fit current data.
