# HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_1

> Date: 2026-08-19
> Status: ACTIVE / NON_FROZEN / PRE_OUTCOME
> Authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Claim schema: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
> Wave 1 review: `docs/reviews/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_1_INTEGRATION_REVIEW_V0_1.md`
> Wave 2 review: `docs/reviews/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_2_INTEGRATION_REVIEW_V0_1.md`

## 1. Purpose

After two accepted real SOURCE_ONLY extraction waves, stop broadening the claim inventory temporarily and identify the smallest source-semantic completion target that can plausibly become a versioned non-outcome Playbook Contract using the project's existing data boundary.

This triage uses no candidate outcomes and does not authorize any backtest.

```text
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
```

## 2. Cross-wave inventory

Accepted post-integration totals:

```text
REAL_CLAIM_EXTRACTION_WAVES_ACCEPTED=2
TOTAL_CLAIMS=33
TOTAL_EXPLICIT=31
TOTAL_INFERRED=2
TOTAL_UNKNOWN=0
TOTAL_OBSERVABLE_NOW=6
TOTAL_PARTIALLY_OBSERVABLE=12
TOTAL_NOT_OBSERVABLE_WITH_CURRENT_DATA=3
TOTAL_NOT_APPLICABLE=12
TOTAL_PRIMARY_CANDIDATES=0
TOTAL_PRIMARY_NOT_YET_JUSTIFIED=33
```

The absence of PRIMARY candidates is treated as useful evidence: source meaning is still under-specified for machine operationalization, and the project must not fill that gap using outcome-driven definitions.

## 3. Triage buckets

### A. PROCESS_LAYER_ONLY_OR_PRIMARILY_PROCESS

The 12 `NOT_APPLICABLE` records belong primarily to research/review/risk/process knowledge rather than market-scene detection. Preserve them in the Human Playbook process layer; do not force them into price features.

Examples include:
- researcher-bias warnings;
- pattern-validation discipline;
- preparation/waiting/process statements;
- risk and learning process claims.

### B. CURRENTLY_NOT_OBSERVABLE

The 3 `NOT_OBSERVABLE_WITH_CURRENT_DATA` records remain source-valid but cannot currently become faithful machine market-scene inputs.

Examples:
- fundamental/macro inputs absent from the project corpus;
- NYSE TICK + Market Delta entry trigger;
- US sector/index confirmation.

No OHLCV proxy is authorized.

### C. PARTIALLY_OBSERVABLE / SOURCE-SURFACE GAP

The 12 `PARTIALLY_OBSERVABLE` records are retained as possible future components, but their missing information surfaces or unresolved source semantics block current PRIMARY selection.

Typical gaps:
- TICK / Market Delta;
- related-market or sector confirmation;
- prior-day value-area semantics;
- relative-volume baseline;
- proprietary/undefined pivot formulas;
- mixed observable and non-observable context.

### D. OBSERVABLE-NOW SEMANTIC-COMPLETION CANDIDATES

Six records have the required data surface available in the existing project substrate, but still lack a unique source-justified operational interpretation:

- Wave 1 `C-W1-009`: coarse retracement observation around prior swing;
- Wave 2 `C-W2-002`: do not sell new highs / do not chase highs on dwindling volume;
- Wave 2 `C-W2-003`: do not chase sellers; wait for rally in broader direction;
- Wave 2 `C-W2-006`: new-high invalidation / range-low target after candidate highs;
- Wave 2 `C-W2-008`: entry near candidate high + bounded range target / separate breakout setup;
- Wave 2 `C-W2-017`: failed prior-day-high breakout, return into morning range, VWAP reversion target.

`OBSERVABLE_NOW` means the necessary raw information surface exists; it does not mean the operational definition is already pinned.

## 4. First semantic-completion target selection

```text
FIRST_PLAYBOOK_CONTRACT_CANDIDATE_FAMILY=STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION
CANDIDATE_FAMILY_STATUS=SOURCE_SEMANTIC_COMPLETION_REQUIRED / NOT_PRIMARY / NOT_OPERATIONALIZED
SELECTION_BASIS=SOURCE_COMPLETENESS_PLUS_EXISTING_DATA_COMPATIBILITY_NOT_EXPECTED_PERFORMANCE
```

Target source claims:
- `C-W2-006`
- `C-W2-008`
- `C-W2-017`

Supporting context:
- `C-W2-002`
- `C-W2-003`
- `C-W2-009`

Why this family is selected first:
1. the existing bundle contains an actual step-by-step trade narrative with explicit waiting, candidate-high logic, invalidation and target limitation;
2. the failed-breakout example contains prior-day high, morning range and VWAP surfaces that are representable from the existing 1-minute OHLCV + governed session metadata;
3. the source explicitly separates range-reversion from a breakout trade, reducing hidden interpretation freedom;
4. missing TICK/Market Delta/sector inputs can be kept out of the first price/volume semantic-completion question rather than silently proxied;
5. the selection is based on traceability and observability, not expected profitability.

## 5. Why other observable candidate is not first

Wave 1 `C-W1-009` (approximately 50% retracement with a very large margin of error) is retained but not selected first because:
- the source does not define swing identification;
- the source deliberately leaves a large tolerance undefined;
- turning it into a numerical retracement rule would immediately require invented semantics.

This is not a negative judgment about the claim's trading merit.

## 6. Exact unresolved semantics for selected family

Before any PRIMARY or machine operationalization, source evidence must resolve or explicitly leave unresolved:

```text
GENERAL_MARKET_DIRECTION
TRADING_RANGE_BOUNDARY
CANDIDATE_HIGH_OR_LOW
MORNING_RANGE_BOUNDARY
FAILED_BREAKOUT_CONDITION
NEW_HIGH_INVALIDATION_REFERENCE
VWAP_SESSION_REFERENCE
ENTRY_PERMISSION_WITHOUT_NON_OWNED_TICK_OR_MARKET_DELTA
TARGET_BOUNDARY
BREAKOUT_VS_RANGE_REVERSION_SEPARATION
```

If official source evidence does not pin one of these, record `UNKNOWN` / `NOT_SOURCE_JUSTIFIED`; do not manufacture a formula.

Most importantly, the project may not simply delete TICK/Market Delta/sector confirmation from the human playbook and call the remaining price-only shell source-equivalent. The next package must determine whether Steenbarger provides a separate source-supported price/volume false-breakout/range-reversion formulation that is faithful with current data. If not, this candidate family stops as partially observable.

## 7. Next bounded package

```text
NEXT_PACKAGE=TARGETED_SOURCE_SEMANTIC_COMPLETION_STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_V0_1
TOOL_DECISION=USE_EXISTING
SOURCE_ACQUISITION=FREE_PUBLIC_UNAUTHENTICATED_ONLY
OUTCOME_ACCESS=FORBIDDEN
```

The package should search only the official free/public pre-2024 TraderFeed archive for source passages that define the selected family and its boundaries. It should not broaden to a third trader yet and should not produce backtests.

Likely source anchors to examine include TraderFeed material on:
- false breakouts / reversals;
- day structure;
- VWAP and range markets;
- candidate highs/lows;
- trade exits / targets;
- range vs breakout regime distinctions.

The output is a source-semantic completion dossier and a decision:

```text
SOURCE_FAITHFUL_PRICE_VOLUME_PLAYBOOK_DRAFTABLE=YES|NO
```

A `NO` is a legitimate result and means this family remains partially observable under the current data budget.
