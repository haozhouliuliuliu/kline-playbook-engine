# Jianghe Second-Pass Integrity Check V1.1

> Status: PASS
> Scope: mechanical integrity of the rescued exhaustive second-pass artifacts. This check does not independently validate trading performance.

## Coverage record

Validated against the canonical local second-pass CSV before rescue:

```text
records = 99
unique_source_ordinals = 99
missing_ordinals = NONE
duplicate_ordinals = NONE
accessible_sources = 98
paid_gate_exception = 022
visual_only_no_reliable_language = 065
all_98_accessible_timeline_coverage = FULL_TIMELINE_REVIEWED_0_TO_END
nonzero_unaccounted_timeline_gaps = NONE
```

Canonical reconstructed artifact:

```text
filename = JIANGHE_SECOND_PASS_SOURCE_COVERAGE_RECORD_V1_1.csv
bytes = 35142
newline_count = 100
sha256 = 1133f089caec2906668241c901a0034e8c5d0d0fa6efcefa9ba61f3994f65877
```

The four committed coverage parts were locally concatenated byte-for-byte and matched this canonical artifact exactly.

## Recovered claim delta

Validated against the canonical local JSONL before rescue:

```text
records = 64
valid_json_records = 64
unique_claim_ids = 64
duplicate_claim_ids = NONE
source_ordinals_outside_001_099 = NONE
```

Canonical reconstructed artifact:

```text
filename = JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.jsonl
bytes = 63941
jsonl_records = 64
sha256 = 5330d703a16ccebf86ae9e984658d95a0423ad96736ed4ed0f0441a910d312a1
```

The four committed claim parts were locally concatenated byte-for-byte and matched this canonical artifact exactly.

## Dossier/reconciliation hashes

```text
JIANGHE_TRADER_DOSSIER_V1_1.md
sha256 = cb43d643a096d674b48d07101f2e211aa6e939c1c3a5e72282041c54836fdad0

JIANGHE_SECOND_PASS_RECONCILIATION_V1_1.md
sha256 = 052c59b2e33ce86fcd63aa4fa3d1dd768fcf8c39175e305962d1ef09696152a6
```

## Provenance/fail-closed checks

The rescued state preserves:

```text
022 = SOURCE_UNAVAILABLE_PAID_GATED
065 = VISUAL_ONLY_NO_RELIABLE_LANGUAGE / semantic claim count 0
048_RECOVERED_REMOTE_SRT = REJECTED_WRONG_VIDEO
099_RECOVERED_REMOTE_SRT = REJECTED_WRONG_VIDEO
009_RECOVERED_REMOTE_SRT = NOT_USED_UNREVALIDATED_AFTER_CONTAMINATION_DISCOVERY
014_RECOVERED_REMOTE_SRT = NOT_USED_UNREVALIDATED_AFTER_CONTAMINATION_DISCOVERY
```

No source outcome/R/P&L value is promoted to strategy-validity evidence by this integrity check.

## Result

```text
SECOND_PASS_ARTIFACT_INTEGRITY = PASS
SECOND_PASS_TIMELINE_COVERAGE_RECORD = COMPLETE_FOR_98_ACCESSIBLE_SOURCES
UNACCOUNTED_TIMELINE_GAP = 0
CLAIM_DELTA_PARSE = PASS
CLAIM_ID_UNIQUENESS = PASS
```

Research boundary remains:

```text
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
REAL_MONEY=NOT_AUTHORIZED
```
