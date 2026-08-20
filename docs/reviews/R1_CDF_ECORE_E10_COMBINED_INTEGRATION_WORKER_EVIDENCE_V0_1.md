# R1_CDF_ECORE_E10_COMBINED_INTEGRATION_WORKER_EVIDENCE_V0_1

> Date: 2026-08-20
> Role: isolated integration worker for the R1 C/D/F + E-Core + E-10 combined integration
> Branch: `integration/r1-cdf-ecore-e10-v01`
> Scope: merge accepted C/D/F combined integration + accepted Package E-Core + E-Governance
> research artifact onto ONE latest tree, implement the sole new production fix E-10 using
> accepted D-05 SessionMetadata content identity, run the combined regression, push the
> integration branch. No `main` modification. No E-04/E-05/E-06/E-07/E-08 implementation.
> No old F/G/H start. No candidate outcome data.

## Main baseline

```text
MAIN_BASELINE=c32c5bf2b76afd290cc0e44839aacf778d423863
MAIN_DESC=record Package E owner decision proposal without adopting semantics
```

`git fetch origin` before work; `origin/main == c32c5bf` matched the expected baseline and
is the pure authority/doc descendant of the expected baseline `c32c5bf` (identical).

## Source branch tips (exact, recorded before merge)

```text
CDF_TIP=b32a42241706153a2f9b14f99989090a3900270f   integration/cdf-final-v01
E_CORE_TIP=004881258514f7d1480309da70e69b0fa844a5c6   repair/package-e-core-execution-v01
GOVERNANCE_TIP=0cd6833ec35397c7f481f142958ef44bd8cbbbdd   research/package-e-governance-authority-v01
```

All three branches fork from `18a28c311a13dd531a6b62600838365f9090c7eb` (merge-base with
`origin/main`). Each is independently accepted by the project-brain review
(`docs/reviews/POST_CDF_E_CORE_GOVERNANCE_REVIEW_AND_REPAIR_EXIT_PLAN_V0_1.md`).

## Merge order (fixed, no rebase, no squash, no force-push)

```text
1. git merge --no-ff origin/integration/cdf-final-v01                  -> 54dd450  (clean, 0 conflicts)
2. git merge --no-ff origin/repair/package-e-core-execution-v01        -> 8147f48  (clean, 0 conflicts)
3. git merge --no-ff origin/research/package-e-governance-authority-v01 -> 49ecf7e  (clean, 0 conflicts)
```

Merge commits:

```text
CDF_MERGE=54dd45099aad8a114537e07c5189d8f895cfa83f   (parents: c32c5bf main, b32a422 CDF)
ECORE_MERGE=8147f48b53d7cc5b4dfa20c11606659b3c679b32 (parents: 54dd450, 0048812 E-Core)
GOVERNANCE_MERGE=49ecf7ef7cf03570c2aa560a4d2264d773d84808 (parents: 8147f48, 0cd6833 Governance)
```

No branch modified `main`; only `integration/r1-cdf-ecore-e10-v01` was advanced locally and
will be pushed.

## Actual conflict files

```text
NONE
```

All three merges completed cleanly (`0 conflicts`). C/D/F are already a combined tree on
`integration/cdf-final-v01`; E-Core is production-file-disjoint from the CDF shared
firewall surface; the E-Governance branch is a documentation/research-only branch. No
manual conflict resolution was required, therefore no whole-file `--ours`/`--theirs`
override of any production file was performed.

## E-10 implementation (the sole new production fix)

Problem (from the exit plan): CompletedRoundTrip.ledger_identity did not bind
`SessionMetadata.version` (D-05 content-derived identity) nor the derived entry/exit
official day/week and active-official-day facts. Changing the session authority could
leave the ledger identity unchanged even when the derived facts changed.

### `src/round_trip_ledger.py`

- `CompletedRoundTrip` gains `session_metadata_version: str | None = None`.
  - When `RoundTripMaterializer` has a `SessionMetadata`, this equals
    `self._session_metadata.version` (the D-05 content-derived identity).
  - When no `SessionMetadata` is supplied, it is `None` (generic/synthetic no-session path
    preserved; no fake `"unknown-session-v1"` authority is invented).
  - The caller cannot pass a separate session-version string to the materializer; the value
    always comes from the actual `SessionMetadata` object.
- `_finalize` computes `session_metadata_version` from the materializer's session metadata
  and adds to the `ledger_identity` hash payload, in addition to the pre-existing facts:
  - `position_id`
  - `terminal_reason`
  - `forced_liquidation`
  - `ordered_transition_references`
  - `ordered_outcome_references`
  - NEW: `session_metadata_version`
  - NEW: `entry_official_trading_day` / `exit_official_trading_day`
  - NEW: `entry_official_trading_week` / `exit_official_trading_week`
  - NEW: `active_official_trading_days`
- The no-session path keeps `session_metadata_version=None` and still binds the actually
  produced entry/exit day/week and active days into the identity.
- E-02 alignment: `_official_day_week` now accepts a FORCED_LIQUIDATION terminal whose
  session-mapped observation day is LATER than the snapshot's position day (the E-02
  cross-trading-day aging case). An earlier day, or any mismatch on a normal transition,
  still fails closed. This is required so a D1->D2 forced liquidation can materialize as a
  completed round trip whose exit day is the session authority's day.

No new session registry; no new ledger framework; no change to E-04/E-05/E-08.

### E-10 regression tests (`tests/test_round_trip_ledger.py::PackageE10SessionAuthorityIdentityTests`)

- E10-A: two SessionMetadata with identical civil transition timestamps but different
  authoritative windows/trading-day mapping -> different version, at least one
  entry/exit day/week differs, ledger_identity differs.
- E10-B: two SessionMetadata with identical authority facts + same transition stream ->
  identical ledger_identity.
- E10-C: changed SessionMetadata window that coincidentally yields the same entry/exit day
  still changes ledger_identity because the D-05 content version changed (identity binds
  authority, not only derived results).
- E10-D: no-session generic path stays deterministic and does not crash.

### D-05 combined regression proof

E-10 reads `SessionMetadata.version`, which is the D-05 content-derived identity computed
from `authority_reference` + exact session windows (`src/data_substrate.py`,
`src/metadata_authority.py`). No legacy caller schedule label is copied into the round
trip; E10-C and integration test D prove identity change with the same label but different
content.

## E-Core × CDF combined regression (`tests/test_r1_cdf_ecore_integration.py`)

New minimal cross-package integration test reusing `tests.synthetic_fixture` helpers (does
not duplicate the fixture framework):

- A. CDF synthetic Playbook / firewall chain still completes outcome registration.
- B. One SessionMetadata is used simultaneously as canonical/session authority (D-05),
  E-Core official trading-day authority in the runner, and RoundTripMaterializer authority.
- C. Forced liquidation D1 -> D2: E-02 aging + E-03 offset fees correct; completed round
  trip carries correct `session_metadata_version` and a recomputable ledger identity.
- D. Changing the SessionMetadata authority (D-05 version) changes round-trip identity even
  when derived days coincide.
- E. Candidate outcome authorization stays closed: only the TEST_ONLY synthetic profile /
  governed data version registers; validation and historical-final-holdout candidate access
  remain denied.

## Test results

```text
FOCUSED_TESTS=318 OK
  (test_cdf_combined_integration, test_playbook_contract, test_research_firewall,
   test_source_evidence_hardening, test_package_d_canonical_repair,
   test_validation_runner, test_contract_execution_semantics, test_round_trip_ledger,
   test_bootstrap_semantics, test_r1_cdf_ecore_integration)
FULL_TESTS=478 OK  (python -m unittest discover -s tests; 0 failures, 0 errors)
COMPILEALL=OK      (python -m compileall -q src tools tests)
DIFF_CHECK=OK      (git diff --check clean)
CONFLICT_MARKERS=NONE  (git grep "^<<<<<<<|^=======|^>>>>>>>" -> no real markers)
```

## Invariants preserved (verified in the merged tree)

- Package C: claim-level PRIMARY (`derive_primary_branch_identity`), Playbook MACHINE_READY
  required before outcome registration, StrategyIdentity equivalence via the shared
  `validate_strategy_against_playbook_contract` bridge, duplicate source claim id fail
  closed, PARTIALLY_OBSERVABLE / UNKNOWN transfer blocks, one machine timeframe.
- Package D: full requested coverage for PASS, zero-bar session missing detection,
  RawArtifact.identity_id provenance, nullable volume, content-derived
  SessionMetadata.version, OFFICIAL_PARTIAL never re-promoted, VERIFIED_OFFICIAL requires
  exact source artifact SHA, mixed partition pre-write reject, PASS-only canonical storage,
  legacy session identity mismatch requires explicit revalidation.
- Package F: ApprovedSourceMaterialRef.from_bytes, historical_unbound NOT_RECORDED,
  material-bound bundle/session identity + hash, source_id/material_id enforcement,
  claim_status only EXPLICIT/INFERRED/UNKNOWN.
- Package A/B firewall protections retained (authoritative candidate gate, TEST_ONLY
  synthetic gate, final holdout locked, Shadow/Forward denied).
- E-Core: E-01 ADD re-mark at fill price, E-02 forced liquidation cross-day aging, E-03
  offset fees into outcome/transition/charged_costs, E-09 duplicate request_id reject,
  E-11 chronological ordering, E-12 open evidence in ledger identity, E-13 bootstrap
  cross-trading-day barrier. E-04/E-05/E-08 remain untouched.

## Ancestry validation

```text
CDF_IS_ANCESTOR=YES        git merge-base --is-ancestor origin/integration/cdf-final-v01 HEAD
E_CORE_IS_ANCESTOR=YES     git merge-base --is-ancestor origin/repair/package-e-core-execution-v01 HEAD
GOVERNANCE_IS_ANCESTOR=YES git merge-base --is-ancestor origin/research/package-e-governance-authority-v01 HEAD
MAIN_IS_ANCESTOR=YES       git merge-base --is-ancestor origin/main HEAD
```

## Remaining governed blockers

```text
E04_SPLIT_RULE_CHOICE=OWNER_DECISION_REQUIRED   (proposal OPTION_C, NOT adopted)
E05_PORTFOLIO_REPRESENTATION_CHOICE=OWNER_DECISION_REQUIRED
E07_MAPPING_RULE_CHOICE=OWNER_DECISION_REQUIRED
E08_RESOURCE_CHOICE=OWNER_DECISION_REQUIRED
E06_STATUS=INSUFFICIENT_EVIDENCE  (official historical fee/margin schedule gap)
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
```

`docs/reviews/PACKAGE_E_OWNER_DECISION_PROPOSAL_V0_1.md` is `PROPOSAL_ONLY_NOT_ADOPTED`;
none of its E-04/E-05/E-07/E-08 semantics were implemented.

## Explicit limitations

- No `main` was modified; `CURRENT_STATE.md`, `00_READ_FIRST.md`, frozen Research Protocol
  / 12-6-6 / canonical corpus / canonical acceptance were NOT modified.
- No candidate market outcome data was read or used.
- E-06 / E-07 / old F/G/H remain governed prerequisites, not implemented here.
- This document records evidence only; it does not declare `main` accepted.
