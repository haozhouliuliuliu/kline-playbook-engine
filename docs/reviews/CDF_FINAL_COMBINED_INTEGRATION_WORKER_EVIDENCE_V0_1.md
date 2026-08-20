# CDF_FINAL_COMBINED_INTEGRATION_WORKER_EVIDENCE_V0_1

> Date: 2026-08-20
> Role: isolated integration worker for Package C / D / F final combined integration
> Branch: `integration/cdf-final-v01`
> Scope: merge three approved corrected branches, resolve C/F shared-file conflicts as a
> semantic union, run combined regression, push the integration branch. No `main`
> modification. No Package E start. No redesign of C/D/F. `CURRENT_STATE` / frozen
> protocols untouched.

## Main baseline

```text
MAIN_BASELINE=18a28c311a13dd531a6b62600838365f9090c7eb
MAIN_DESC=narrow E core lane to semantics already determined by authority
```

`git fetch origin` before any work; `origin/main == 18a28c3` matched the expected baseline.

## Source branch tips (exact)

```text
C_TIP=a9c7c6c6f69a574ab1b3a45b39db4fd07497cc59   repair/package-c-playbook-protocol-v01
D_TIP=8d23a2a49e7fdc63ecbdf5458e5a2f8e9ac4025b   repair/package-d-canonical-provenance-v01
F_TIP=78174c57eb62a2e93094340151e8415c6f2662e2   repair/package-f-source-evidence-hardening-v01
```

All three branches fork from `40f27b2` (merge-base with `origin/main`). Each branch is
individually accepted by the project-brain correction review
(`docs/reviews/CDF_CORRECTION_REVIEW_AND_NEXT_PARALLEL_PLAN_V0_1.md`).

## Merge order (fixed, no rebase, no squash, no force-push)

```text
1. git merge --no-ff origin/repair/package-d-canonical-provenance-v01  -> 3edd4744  (clean, 0 conflicts)
2. git merge --no-ff origin/repair/package-c-playbook-protocol-v01     -> 63f64716  (clean, 0 conflicts)
3. git merge --no-ff origin/repair/package-f-source-evidence-hardening-v01 -> 236a00d (2 conflicts, resolved)
```

Merge commits:

```text
D_MERGE=3edd474471d41753eb0794c764451df9bab18742  (parents: 18a28c3 main, 8d23a2a D)
C_MERGE=63f647161cc5f4adf10d523d7321f3fba3e4324c  (parents: 3edd4744, a9c7c6c C)
F_MERGE=236a00d3a761efe4e121b32f846afced6b2546c8  (parents: 63f64716, 78174c5 F)
```

As predicted by the review, D is production-file-disjoint from the C/F shared firewall
surface and merged with no conflicts. The only conflicts were the C/F shared files.

## Actual conflict files

```text
src/research_firewall.py
tests/test_research_firewall.py
```

(`tests/synthetic_fixture.py` was auto-merged cleanly by the ort strategy and verified
as a correct semantic union — see below.)

## Conflict resolution semantics (semantic union, never whole-file ours/theirs)

### `src/research_firewall.py`

Single conflict: the `src.playbook_contract` import block. Resolved as a union keeping
every symbol actually used by the combined file:

```python
from src.playbook_contract import (
    ClaimStatus,                       # Package F ClaimRecordDraft claim_status gate
    PlaybookContract,                  # shared
    validate_contract,                 # Package C readiness authority
    validate_strategy_against_playbook_contract,  # Package C bridge-equivalence authority
)
```

Verified the merged body retains BOTH packages' semantics:

- Package C: `derive_primary_branch_identity()` returns `contract.primary_selection_identity`;
  `register_outcome_test()` calls `validate_contract()` first and raises
  `PLAYBOOK_CONTRACT_NOT_MACHINE_READY` before any mutation; calls
  `validate_strategy_against_playbook_contract(contract, strategy)`; retains
  `experiment.validate_strategy(strategy)`; claim-level PRIMARY / duplicate source claim
  id / single-timeframe / PARTIALLY_OBSERVABLE / UNKNOWN-transfer blockers unchanged.
- Package F: `ApprovedSourceMaterialRef` (`from_bytes`, `historical_unbound` NOT_RECORDED,
  `material_identity`), `ByteBindingStatus`, `ApprovedSourceBundle` material refs with
  `session_binding_identity`/`session_binding_hash`; `SourceOnlyClaimExtractionContext.verified`
  compares `session.source_bundle_identity == bundle.session_binding_identity` and
  `session.source_bundle_hash == bundle.session_binding_hash` (no fallback to legacy
  `source_bundle_id`/`source_bundle_hash`); `ClaimRecordDraft` requires `source_id` +
  `material_id` and restricts `claim_status` to `EXPLICIT | INFERRED | UNKNOWN`.
- Package B: `SourceOnlyPolicy` issued-verified registry (only `open_verified_session`
  writes it; `record_session` can never self-verify), durable JSON state
  (`save_state`/`load_state`), family-claim lineage binding, artifact-derived
  registration, `alternatives == denominator`, B-C02/B-C04/B-C05 ordering preserved.
- Package A: caller cohort/synthetic bool removed (derived from `data_dates` and exact
  `TEST_ONLY_SYNTHETIC_DATA_VERSION` equality), validation default deny, authoritative
  `PRE_OUTCOME_GATE_GRANTED`, final holdout locked, Shadow/Forward denied.

### `tests/test_research_firewall.py`

Single conflict: the `tests.synthetic_fixture` import block. Resolved as a union keeping
both C's `SYNTHETIC_PARAMETER_IDENTITY` (used at the registration parameter test) and F's
`SYNTHETIC_MATERIAL_ANCHOR` / `SYNTHETIC_MATERIAL_ID` / `SYNTHETIC_SESSION_BINDING_HASH` /
`SYNTHETIC_SESSION_BINDING_IDENTITY` (used by the SOURCE_ONLY / claim tests). Both sets of
constants are genuinely used in the merged file, so the union is exact.

### `tests/synthetic_fixture.py` (auto-merged, verified)

Final fixture satisfies C + F + B simultaneously:

- SOURCE_ONLY side: `make_approved_material_ref(exact_bytes=...)` -> `ApprovedSourceMaterialRef.from_bytes`;
  `make_approved_bundle(materials=...)` -> material-bound `ApprovedSourceBundle`;
  `make_open_session` binds `source_bundle_identity=SYNTHETIC_SESSION_BINDING_IDENTITY` /
  `source_bundle_hash=SYNTHETIC_SESSION_BINDING_HASH` where those constants are derived from
  the actual bundle's `session_binding_identity`/`session_binding_hash` (never legacy id/hash).
- `make_contract` binds `source_bundle_identity` / `source_bundle_hash` to the material-bound
  facts and `source_only_session_identity` to the real issued session identity.
- `make_strategy` produces a bridge-equivalent StrategyIdentity; `build_synthetic_firewall`
  rebuilds the exact bound contract from the strategy's bridge facts and uses
  `derive_primary_branch_identity(contract)`.
- `ArtifactBinding` is created from real synthetic bytes (`from_bytes`), no fake code-hash
  strings.

## Package D completeness in the combined tree

Verified in the merged tree (D merged cleanly, all D corrections present):

```text
D-01 PASS requires full requested coverage            tests/test_package_d_canonical_repair.py (full requested coverage)
D-02 zero-bar session completeness enumeration        tests/test_package_d_canonical_repair.py (zero-bar window)
D-03 CanonicalRow.raw_artifact_identity_id            src/canonical_storage.py (from RawArtifact.identity_id)
D-04 volume=None preserved                            src/canonical_storage.py CanonicalRow nullable volume
D-05 SessionMetadata.version content-derived identity src/metadata_authority.py / canonical_storage.py
D-06 OFFICIAL_PARTIAL never re-promoted; VERIFIED_OFFICIAL requires exact source artifact hash
     src/metadata_authority.py + tests/test_package_d_canonical_repair.py (D-C01)
D-07 mixed partition pre-write rejection              src/canonical_storage.py write_partition_table
D-08 real runtime mismatch version diagnostic         src/historical_acquisition.py _check_runtime_version
normalize_and_store_partition accepts PASS only       tools/build_canonical_dataset.py (CANONICAL_STORAGE_REQUIRES_PASS_PARTITION)
legacy session identity mismatch                      SESSION_METADATA_IDENTITY_REVALIDATION_REQUIRED (no auto-migrate)
```

## Combined cross-package test (new)

```text
tests/test_cdf_combined_integration.py  (245 lines, minimal, reuses tests/synthetic_fixture helpers)
```

One closed chain proof: F exact-byte material ref -> material-bound bundle -> project-issued
verified session -> legal `(source_id, material_id)` claim record -> machine-ready
`PlaybookContract` bound to the same bundle/session -> real `bridge_to_strategy_identity`
-> TEST_ONLY profile locked -> wave registered -> `ResearchFirewall.register_outcome_test`
succeeds.

Two tamper proofs:

```text
T1 swap material bytes, keep old session  -> SOURCE_ONLY context no longer verified
T2 tamper StrategyIdentity timeframe or code hash -> outcome registration fails closed
```

No candidate market outcome data is used anywhere in the test.

## Test results

```text
COMBINED_CHAIN_TEST=1 OK
FOCUSED_TESTS=260 OK   (test_playbook_contract, test_research_firewall,
                        test_source_evidence_hardening, test_package_d_canonical_repair,
                        test_strategy_evidence, test_validation_runner,
                        test_portfolio_semantics, test_cdf_combined_integration)
FULL_TESTS=451 OK      (python -m unittest discover -s tests; pyarrow 25.0.1 present,
                        capability tests ran; 0 skipped)
COMPILEALL=OK          (python -m compileall -q src tools tests)
DIFF_CHECK=OK          (git diff --check clean)
CONFLICT_MARKERS=NONE  (git grep "<<<<<<<|=======|>>>>>>>" -> no matches)
```

## Ancestry validation

```text
C_IS_ANCESTOR=YES  git merge-base --is-ancestor origin/repair/package-c-playbook-protocol-v01 HEAD
D_IS_ANCESTOR=YES  git merge-base --is-ancestor origin/repair/package-d-canonical-provenance-v01 HEAD
F_IS_ANCESTOR=YES  git merge-base --is-ancestor origin/repair/package-f-source-evidence-hardening-v01 HEAD
MAIN_IS_ANCESTOR=YES  git merge-base --is-ancestor origin/main HEAD
```

## Remaining explicit limitations

- `CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED`; no candidate market outcome data was used.
- `VALIDATION_ACCESS=LOCKED`; `HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED`; `SHADOW_FORWARD=NOT_AUTHORIZED`.
- `CURRENT_STATE.md` was NOT modified by this worker; frozen Research Protocol / split /
  source-acquisition protocols were NOT modified.
- `main` was NOT modified; only `integration/cdf-final-v01` was advanced and pushed.
- Package E (execution repairs / governance research) was NOT started by this worker.
- No canonical corpus rebuild or acceptance rewrite occurred; D corrections are
  code/test-level and do not declare existing accepted OHLC values numerically wrong.
- Package F historical recorded bundle hashes remain historical metadata, not retroactive
  byte proof; historical accepted extraction artifacts were not refetched or rewritten.
- D-05 legacy session identity mismatch requires explicit revalidation/rebuild; no
  auto-migration was implemented.

## Acceptance authority

This worker records evidence only. Final acceptance of the integrated diff belongs to the
project brain / Owner; this document does not declare `main` accepted.
