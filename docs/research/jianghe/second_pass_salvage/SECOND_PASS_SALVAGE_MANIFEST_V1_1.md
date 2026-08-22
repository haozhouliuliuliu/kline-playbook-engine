# Jianghe Second-Pass Salvage Manifest V1.1

> Status: DURABLE INTEGRITY MANIFEST
> Branch: `research/jianghe-evidence-001-099-v1-0-final`
> Purpose: make the rescued second-pass artifacts reconstructable and integrity-checkable even if the active chat/runtime disappears.

## 1. Canonical local artifacts rescued

| Artifact | Local byte size | SHA-256 |
|---|---:|---|
| `JIANGHE_SECOND_PASS_SOURCE_COVERAGE_RECORD_V1_1.csv` | 35142 | `1133f089caec2906668241c901a0034e8c5d0d0fa6efcefa9ba61f3994f65877` |
| `JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.jsonl` | 63941 | `5330d703a16ccebf86ae9e984658d95a0423ad96736ed4ed0f0441a910d312a1` |
| `JIANGHE_TRADER_DOSSIER_V1_1.md` | 13347 | `cb43d643a096d674b48d07101f2e211aa6e939c1c3a5e72282041c54836fdad0` |
| `JIANGHE_SECOND_PASS_RECONCILIATION_V1_1.md` | 7338 | `052c59b2e33ce86fcd63aa4fa3d1dd768fcf8c39175e305962d1ef09696152a6` |

The dossier and reconciliation are committed directly under `docs/research/jianghe/`.

The larger CSV/JSONL artifacts were intentionally committed in four ordered parts each so the rescue could be pushed in small commits rather than held until one large final write.

### GitHub text newline normalization qualification

The canonical local coverage CSV used CRLF line endings. GitHub's text-content write path normalized the committed coverage fragments to LF. The repository API therefore reports the following remote sizes:

```text
coverage part00 = 9121 bytes
coverage part01 = 8769 bytes
coverage part02 = 8435 bytes
coverage part03 = 8717 bytes
remote LF total = 35042 bytes
```

Each remote coverage fragment is exactly 25 bytes smaller than the corresponding local fragment, matching its 25 newline delimiters. Across four fragments the 100-byte difference matches the 100 recorded newlines in the canonical local CSV.

Therefore:

```text
CANONICAL_LOCAL_COVERAGE_SHA256 = 1133f089caec2906668241c901a0034e8c5d0d0fa6efcefa9ba61f3994f65877
REMOTE_GITHUB_RAW_BYTE_IDENTITY_TO_LOCAL = NOT_CLAIMED
REMOTE_GITHUB_TEXT_ROW_CONTENT = PRESERVED_WITH_LF_NORMALIZATION
```

The local canonical SHA-256 remains a provenance identifier for the pre-rescue artifact. Do not claim that raw concatenation of the LF-normalized GitHub fragments reproduces that local byte hash. Semantic/mechanical reconstruction remains governed by the 99-row coverage checks below. If exact original-byte reconstruction is required later, newline restoration must be independently rechecked before claiming hash equality.

The claim JSONL fragments did not exhibit this byte-size discrepancy; their remote GitHub sizes match the recorded fragment sizes.

## 2. Coverage record parts

Reconstruct the repository text view in order:

```text
part00 + part01 + part02 + part03
-> JIANGHE_SECOND_PASS_SOURCE_COVERAGE_RECORD_V1_1.csv
```

The resulting GitHub reconstruction is LF-normalized. The historical local fragment metadata is preserved below for provenance.

| Part | Local bytes | Lines/newlines | Local SHA-256 | Commit |
|---|---:|---:|---|---|
| `JIANGHE_SECOND_PASS_SOURCE_COVERAGE_RECORD_V1_1.part00.csv` | 9146 | 25 | `7f73443bd9234c367cacd18a50e2e2bcaf9e810d60a0537a6ca0eb25060ca976` | `ae5866d9935b545cac8f6f3191e789ee14dcd49e` |
| `...part01.csv` | 8794 | 25 | `072435183d0167eb34e56a4ba241b5090b9bbd8a8a81bfa5c597aad8d0cc4172` | `2b190b59a1ec6c1c7c93daeadd779cc5015102a3` |
| `...part02.csv` | 8460 | 25 | `2315215e5fafe7bf4bd655fadaf0a1f4ec7a44ddabe1d67c6b71f9973825812b` | `a8cdd090be21d3c8fb416229a8f1155fef8c7f65` |
| `...part03.csv` | 8742 | 25 | `d651c96d6ef3ab313097b9c9c8991ec8fa535f6aa7b49047c02e5fdacbe098ce` | `417bc4451c695d287c6db7d42d9ed37fdc0f73fe` |

Historical canonical local artifact:

```text
bytes = 35142
newline_count = 100
sha256 = 1133f089caec2906668241c901a0034e8c5d0d0fa6efcefa9ba61f3994f65877
```

Semantic/mechanical audit of the coverage CSV content:

```text
data_rows = 99
unique_source_ordinals = 99
missing_ordinals = NONE
duplicate_ordinals = NONE
accessible_sources = 98
all_accessible_timeline_coverage = FULL_TIMELINE_REVIEWED_0_TO_END
nonzero_unaccounted_timeline_gaps = NONE
paid_gate_exception = 022
visual_only_no_reliable_language = 065
```

## 3. Second-pass recovered claim delta parts

Reconstruct in order with raw byte concatenation:

```text
part00 + part01 + part02 + part03
-> JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.jsonl
```

| Part | Bytes | JSONL records | SHA-256 | Commit |
|---|---:|---:|---|---|
| `JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part00.jsonl` | 15843 | 16 | `6b49092f390c901dec13d2d89a1d8f3224ba49ef040792a5a5608a63facbbde2` | `67da180d271cc2707b3365298f296ee882c57973` |
| `...part01.jsonl` | 15473 | 16 | `68db5dd7cc61dad7d30c836b6c0be1fa5530571c018f4d77213ab36873ed7ba2` | `fe1c77ce1a756cd39420cad98983b24f10003e56` |
| `...part02.jsonl` | 16195 | 16 | `4a2833d3ca0a042329d1f9e4089644a0f9d57e1b28957fbfde132f79c04e8843` | `3fadf20db2a546b268eb98cb5f2dc840bfc78f20` |
| `...part03.jsonl` | 16430 | 16 | `2005e0972b76257551801a4644ae84de0cc0f21ad4d203df7c73c6c5c59d7f38` | `a1c215d8e83cd8b9ab7797e090181ec17e58a0a5` |

Integrity check after concatenation:

```text
bytes = 63941
jsonl_records = 64
valid_json_records = 64
unique_claim_ids = 64
sha256 = 5330d703a16ccebf86ae9e984658d95a0423ad96736ed4ed0f0441a910d312a1
```

The 64 claims are a **recovery delta**, concentrated on material semantics that the earlier sparse 001–028 package compressed or omitted. They do not replace unchanged V0.x/V1.0 claims; final cumulative reading must merge them with prior evidence while honoring later contradiction resolutions.

## 4. Other rescue commits

| Commit | Durable artifact |
|---|---|
| `1cc5451530ef9fd6090955f79ac48c4aa9cc2ce4` | `JIANGHE_SECOND_PASS_SALVAGE_SNAPSHOT_V1_1.md` |
| `2edd8f203d1573aeec2a588b14d1260cd24c1756` | `JIANGHE_SECOND_PASS_RECOVERED_FINDINGS_001_043_V1_1.md` |
| `f896d5b129fd891f707527cde17adc775bd65f5f` | `JIANGHE_SECOND_PASS_WORKING_INVENTORY_044_099_V1_1.md` |
| `f9f8aaac3a3f21d12561bb17c53808395282e35d` | README links/authority rescue update |
| `7ff5c8b87917b4a3d0440a6e85fa5117c41adffe` | exact `JIANGHE_SECOND_PASS_RECONCILIATION_V1_1.md` |
| `4a27dea60aed020d20c3d97a394fa9a90408fc09` | exact `JIANGHE_TRADER_DOSSIER_V1_1.md` |

## 5. Research boundary

These artifacts preserve the exhaustive second-pass research state. They do **not** authorize outcome testing, validation/final holdout access, PRIMARY promotion, broker access, paid actions or real-money trading.

```text
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
REAL_MONEY=NOT_AUTHORIZED
```
