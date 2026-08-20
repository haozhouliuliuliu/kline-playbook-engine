# Canonical Repaired Corpus Application — Pre-Build Prep v0.1

- STATUS: `PRE_BUILT_READY` / `MATERIALIZATION_NOT_RUN`
- BASE_COMMIT: `e98df52a427a23c85fac70125a1f20dbd5f2a353`
- BASE_COMMIT_SUBJECT: `evidence: qualify targeted canonical repair`
- BRANCH: `preoutcome/canonical-repair-application-v01`
- QUALIFICATION_EVIDENCE: `docs/evidence/CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.json`
  (currently `RESULT=BLOCKED`, `TARGETED_REACQUISITION_ATTEMPTED=False`,
  `qualification_status=NOT_ATTEMPTED` for all 116 diagnostics)
- APPLICATION: `tools/build_repaired_canonical_candidate.py`
- IDENTITY_MODULE: `src/canonical_repair_identity.py`
- TESTS: `tests/test_build_repaired_canonical_candidate.py`
- MATERIALIZATION_RUN: `NO`

## 1. Purpose

Once all 116 D01/D02 replacement partitions are qualification-verified, the
project must be able to construct a new, fully independent repaired canonical
candidate corpus immediately — without writing ad-hoc tooling at that moment.
This package pre-builds that application now, fail-closed, and does not modify
or materialize any real historical data today.

The accepted canonical corpus (identity
`1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`,
32,980 partitions, 15,280,452 rows) contains 116 partitions that, under the
corrected D01/D02 session-authority semantics, are truncated (returned coverage
missing the session head) and/or missing expected session bars. The repair path
re-acquires only those 116 partitions. 32,864 partitions are genuinely PASS and
are inherited unchanged.

## 2. Scope and boundaries (binding)

- NO real materialization is performed by this package. The tool refuses to
  materialize unless the full qualification gate opens.
- The historical accepted root is NEVER written (parquet/manifest/catalog/raw
  all preserved).
- Output goes ONLY to an independent root: `data/repaired_candidate_v01/`.
- The repaired corpus is a CANDIDATE with a NEW identity. It never claims to be
  the accepted `1d03fd...` corpus.
- Parent/historical lineage is preserved and bound into the new identity.
- No candidate outcome is created; no chronological/validation split is created.
- The old `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md` is never modified.

## 3. Inputs

| Input | Default | Role |
|---|---|---|
| historical accepted data root | `data/canonical/` | accepted `manifest.json`, `parquet/`, `catalog.sqlite` |
| e98 qualification evidence | `docs/evidence/CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.json` | 116 target diagnostics + gate facts |
| repair raw root | `data/revalidation_repair_v01/raw/historical/` | qualified replacement raw (per-target) |

## 4. Materialization gate (HARD STOP when any condition is unmet)

```text
TARGET=116
REPAIRED_PASS=116
STILL_D01=0
STILL_D02=0
DRIFT=0
AUTHORITY_MISMATCH=0
```

`STILL_D01` = diagnostics with `qualification_status == "STILL_D01_TRUNCATED"`;
`STILL_D02` = `"STILL_D02_MISSING"`; `DRIFT` = diagnostics with
`historical_provider_value_drift == true`; `AUTHORITY_MISMATCH` = diagnostics
with non-empty `authority_boundary_reasons`.

The gate also requires, structurally:

- evidence `schema_version == canonical-d01-d02-targeted-repair-qualification-v0.1`;
- `outcome_access_used == False`;
- `historical_accepted_corpus_modified == False`;
- `targeted_reacquisition_attempted == True` (all 116 actually re-acquired);
- evidence totals equal the per-diagnostic counts (no inconsistent evidence);
- every `REPAIRED_PASS` diagnostic carries a `candidate_raw_path`;
- no unknown qualification status.

Any unmet condition raises a fail-closed `HARD_STOP` and nothing is written to
the output root.

## 5. Fail-closed application flow

1. **Root disjointness**: historical root, repair raw root, and output root must
   be pairwise disjoint (equal/ancestor/descendant is rejected).
2. **Gate** (read-only): evaluated before any corpus access.
3. **Plan** (read-only): the accepted manifest is read as raw JSON (the accepted
   corpus legally contains truncated-PASS records that the repaired
   `ManifestPartition` refuses to load — exactly the 116 targets). Every
   accepted partition is classified as inherited or target by recomputed
   partition identity; every target must exist in the accepted manifest; every
   inherited partition must load as a valid PASS `ManifestPartition`.
4. **Re-qualification** (read-only, fail-closed): each on-disk replacement raw
   is re-verified under D01/D02 semantics — exact full requested coverage, all
   expected session bars present, no out-of-session bars, and the recorded
   candidate returned coverage must match the on-disk raw. A defective raw is a
   HARD STOP even when the evidence claims `REPAIRED_PASS`.
5. **Assembly** (write, only after 1-4 pass):
   - inherited partitions: byte-faithful parquet copy; the recomputed parquet
     artifact identity must equal the accepted catalog's recorded artifact
     identity (byte-faithfulness proof); catalog row facts carried over;
   - repaired partitions: re-normalized under current session authority via the
     accepted acquisition path; recorded as PASS with new raw/identity facts;
   - outputs written under the independent output root: `manifest.json`,
     `parquet/`, `catalog.sqlite`, `quality_summary.json`, `identity.json`,
     `lineage.json`, `build_report.json`.

## 6. Outputs (new)

```text
data/repaired_candidate_v01/
  manifest.json          # canonical-repaired-candidate-manifest-v1
  parquet/               # inherited byte-copy + new repaired partitions
  catalog.sqlite         # canonical-repaired-candidate-catalog-v1
  quality_summary.json   # canonical-repaired-candidate-quality-v1
  identity.json          # canonical-repaired-candidate-identity-v1
  lineage.json           # canonical-repaired-candidate-lineage-v1
  build_report.json      # canonical-repaired-candidate-build-report-v1
```

## 7. New identity and lineage

The repaired candidate gets a NEW deterministic identity
(`src/canonical_repair_identity.py`) that binds: source, products, coverage,
inventory rule, new raw-manifest root, governed metadata root, normalizer,
parquet schema/storage versions, all partition identities (32,864 inherited +
116 repaired), quality-summary identity, the explicit
`cross_source_summary_identity=CANDIDATE_NOT_REVERIFIED` sentinel (the repaired
candidate has NOT been cross-source verified), the parent corpus identity
(`1d03fd...`), the parent raw-manifest root identity (`7510a4a9...`), the
qualification evidence identity (normalized to exclude machine-dependent raw
paths), and the inherited/repaired counts.

The new identity value is guaranteed to differ from `1d03fd...` and is
reproducible: identical inputs yield the identical identity.

## 8. Dry-run mode

`python -m tools.build_repaired_canonical_candidate --dry-run` validates roots,
evidence, gate, plan, and re-qualifies every replacement raw, then prints the
build report — writing nothing.

## 9. Test matrix (synthetic fixtures)

`tests/test_build_repaired_canonical_candidate.py` builds minimal legal
synthetic fixtures on the real session machinery (compact calendar + day
window) and verifies:

| Requirement | Test |
|---|---|
| 116/116 qualified → materializes | `test_116_of_116_qualified_materializes` |
| 115/116 must be rejected | `test_115_of_116_rejected_no_output` |
| one D01/D02 fail must be rejected | `test_one_d02_fail_rejected_no_output` |
| one drift must be rejected | `test_one_drift_rejected_no_output` |
| historical root overwrite must be rejected | `test_historical_root_overwrite_rejected` |
| deterministic identity | `test_deterministic_identity` |
| PASS-only storage (defective raw blocks) | `test_defective_replacement_raw_blocks_even_if_evidence_says_pass` |
| dry-run writes nothing | `test_dry_run_writes_nothing` |
| no outcome dependency | `test_no_outcome_dependency` |
| acceptance never rewritten | `test_never_writes_acceptance_or_historical_acceptance` |
| current BLOCKED evidence hard-stops | `test_committed_not_attempted_evidence_hard_stops` |

## 10. Status

```text
STATUS=PRE_BUILT_READY
MATERIALIZATION_RUN=NO
FAIL_CLOSED_GATE_TESTED=YES
FOCUSED_TESTS=11_OK
FULL_TESTS=547_OK
COMPILEALL=OK
DIFF_CHECK=OK
PUSH=YES
BLOCKER=NONE
```

Verified on `preoutcome/canonical-repair-application-v01` at base
`e98df52a427a23c85fac70125a1f20dbd5f2a353`:
