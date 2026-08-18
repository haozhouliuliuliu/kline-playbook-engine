# Canonical Dataset — BALANCED Corpus Acceptance (Phase 11)

Status: ACCEPTED.  The Owner/project-lead-approved BALANCED canonical research
dataset is fully built, normalized, cross-source verified, and sealed under an
immutable canonical corpus identity.

## Acceptance facts

```
OWNER_APPROVAL=YES
OWNER_SOURCE_APPROVAL=TQSDK
TQSDK_ADOPTION_SCOPE=historical concrete-contract 1-minute research data only
TQSDK_VERIFIED_RUNTIME=3.10.1
OWNER_DATASET_SCOPE_APPROVAL=BALANCED
SCALE_DECISION=APPROVED_FULL_BALANCED_CORPUS
COVERAGE=2024-01-01..2025-12-31
PAID_CONTINUITY_AUTHORIZED=NO
CANONICAL_DATASET_STATUS=ACCEPTED
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
```

## Corpus inventory

| Product | Partitions | Contracts |
|---------|-----------:|----------:|
| cu  | 5,820 | 36 |
| al  | 5,820 | 36 |
| ni  | 5,820 | 36 |
| au  | 3,880 | 32 |
| ag  | 5,820 | 36 |
| rb  | 5,820 | 36 |
| **Total** | **32,980** | **212** |

- Normalized rows: 15,280,452
- Parquet files: 32,980 (exactly one file per partition; no duplicates)
- Raw artifacts: 32,980 TqSdk 60-second JSON partitions (ignored `data/raw/historical/`)
- Manifest: `data/canonical/manifest.json`, identity `7510a4a943e85c9be256e62971b5a64d64e9976c2b01c9f5d0fe07b1c6c8d324`
- Catalog: `data/canonical/catalog.sqlite` (rebuildable SQLite index, 32,980 partitions)
- Parquet layout: `data/canonical/parquet/exchange=SHFE/product=<p>/concrete_contract=<c>/year=<y>/month=<m>`

## Quality gates

- Acquisition: 32,980/32,980 partitions PASS (fail-closed resumable build;
  resilient unattended reconnect/resume; zero data loss).
- Cross-source (vs SHFE official annual raw): 32,841 MATCH / 0 MISMATCH /
  0 NOT_COMPARABLE / 139 NOT_AVAILABLE (no official row for that contract/day;
  benign).  `docs/evidence/CANONICAL_FULL_CROSS_SOURCE.json`
  summary_identity `cee702ea6cd79e62ec49bf7f1f632f70e5b0a7a577ba455e09597cce9d16d4ae`.
- Normalization: Parquet write/read logical equality preserved (Decimal OHLC,
  Asia/Shanghai timezone, nullable open-interest) per canonical schema
  `canonical-normalized-bar-v1`, storage `parquet-partitioned-v1`.
- Tests: 181/181 pass (pyarrow venv), compileall clean, 12/12 evidence JSON
  valid, secret scan 0, `git diff --check` clean.

## Governed metadata (correction recorded)

The HISTORICAL_METADATA_EFFECTIVE_PERIOD_BINDING is PASS: contract-spec
effective periods and official night-closed days are bound to SHFE notices
(`CANONICAL_CONTRACT_SPECS.json` v2, `CANONICAL_TRADING_CALENDAR.json` v2 with
`night_closed_trading_days`); the acquisition planner is fail-closed on missing
or conflicting metadata coverage.  See `CANONICAL_DATASET_PACKAGE.md` for the
correction notice.

## Identity inputs (deterministic, reproducible)

`CANONICAL_CORPUS_IDENTITY.json` binds: source provider/identity, product
universe (cu,al,ni,au,ag,rb), coverage, inventory rule
`pit-complete-listed-concrete-contract-universe-v1`, raw manifest root identity,
governed metadata root identity, normalizer identity, Parquet schema/storage
versions, 32,980 unique partition identities, quality summary identity, and
cross-source summary identity.

## Boundaries preserved

- No strategy lineage, research/main-contract rule, or chronological split is
  created here.
- No broker connectivity, live/Shadow trading, order submission, or paid
  renewal is authorized.
- Next review (NOT executed): research-protocol and chronological-split freeze.
