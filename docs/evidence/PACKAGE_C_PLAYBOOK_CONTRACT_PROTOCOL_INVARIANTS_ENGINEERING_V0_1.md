# PACKAGE C — PLAYBOOK CONTRACT PROTOCOL INVARIANTS — ENGINEERING EVIDENCE V0_1

Authoritative spec: `docs/reviews/PARALLEL_PACKAGE_C_D_F_ACTUAL_REPAIR_SPEC_V0_1.md`
Findings repaired: **P-01, P-02, P-03, P-04, P-05**
Preflight reproduction: `prep/package-c-playbook-protocol-reproduction-v01` @
`f76aed58c4fe43b92dc2e798d74159365562b28b` (P-01..P-05 all `REPRODUCED`).

## 1. Scope

One isolated branch `repair/package-c-playbook-protocol-v01`, based on
`origin/main` `e8ccab103a43c464aef6cc02f9566083e7acd922` (which carries the
bounded parallel Package C/D/F repair spec). Package C makes Playbook Contract
machine readiness derive from claim-level PRIMARY, ambiguity, observability,
transfer and timeframe facts instead of caller self-attestation.

It does **not** repair Package D/E/F, does not modify frozen Protocol v1.0, does
not touch the canonical pipeline, source historical artifacts,
execution/capital, the Holy Grail worker branch, or old F/G/H lanes, and does
not edit `CURRENT_STATE.md`. Only synthetic `PlaybookContract` fixtures are used
and no candidate outcome data is read.

## 2. Root causes and minimum repairs

### P-01 — one PRIMARY per contract, not per source-faithful claim

- **Old behavior:** `_collect_blockers` counted `primary_selected` across all
  `InterpretationBranch` objects and required exactly one total PRIMARY for the
  whole contract (`PRIMARY_MISSING` when zero, `MULTIPLE_PRIMARY_SELECTED` when
  >1). A multi-component playbook could select one interpretation as PRIMARY
  while other claim-level interpretation choices stayed unselected and still be
  `MACHINE_READY`.
- **Minimum repair:** machine readiness now derives PRIMARY **per source
  claim**. For every `SourceClaimRef.claim_id`:
  1. at least one `InterpretationBranch` must reference it;
  2. among its referencing branches exactly one must have
     `primary_selected=True`.
  Zero PRIMARY for a claim → `CLAIM_PRIMARY_MISSING` (blocker). More than one
  PRIMARY for a claim → `CLAIM_PRIMARY_MULTIPLE` (blocker). One branch may be the
  PRIMARY for several claims it explicitly references.
- **New invariant:**
  ```text
  FOR_EACH claim IN contract.source_claims:
      referencing = branches referencing claim
      referencing != empty                    else CLAIM_PRIMARY_MISSING
      count(b.primary_selected) == 1          else CLAIM_PRIMARY_MISSING / CLAIM_PRIMARY_MULTIPLE
  ```
  The old contract-wide `PRIMARY_MISSING` / `MULTIPLE_PRIMARY_SELECTED` blockers
  are gone. `primary_required` remains descriptive schema metadata and no longer
  gates this derivation.

### P-02 — ambiguity_status is caller self-attestation, never a safety authority

- **Old behavior:** `contract.ambiguity_status` is one caller-supplied enum.
  `UNRESOLVED_CRITICAL` blocked readiness, but flipping the enum to `NONE` /
  `RESOLVED` removed the blocker with no field-level proof.
- **Minimum repair:** `ambiguity_status` stays as descriptive / compatibility
  metadata but can never waive derived ambiguity:
  - claim-level PRIMARY incomplete + `ambiguity_status=NONE` → still
    `NOT_MACHINE_READY`;
  - claim-level PRIMARY incomplete + `ambiguity_status=RESOLVED` → still
    `NOT_MACHINE_READY`;
  - `ambiguity_status=UNRESOLVED_CRITICAL` → always a blocker
    (`UNRESOLVED_CRITICAL_AMBIGUITY`), even when claim PRIMARYs look complete.
- **New invariant:** a caller may declare "there is still a problem"
  (`UNRESOLVED_CRITICAL` blocks) but cannot declare "there is no problem"
  (`NONE`/`RESOLVED`) to remove a derived blocker.

### P-03 — PARTIALLY_OBSERVABLE required inputs block MACHINE_READY

- **Old behavior:** required `ObservationSurface` blocked readiness only for
  `NOT_OBSERVABLE_WITH_CURRENT_DATA` / `UNKNOWN`; `PARTIALLY_OBSERVABLE` was
  accepted as machine-ready with no required machine-resolution record.
- **Minimum repair:** any required surface with
  `observability_status=PARTIALLY_OBSERVABLE` now adds
  `REQUIRED_INPUT_NOT_FULLY_OBSERVABLE` (blocker). No surrogate approval object,
  partial-resolution framework, or proxy model is introduced. A future
  explicitly governed inferred surrogate must be a separate interpretation /
  contract version.
- **New invariant:** required surface observability must be
  `OBSERVABLE_NOW` (or `NOT_APPLICABLE` on a required surface with an explicit
  non-applicability) for machine readiness in this package.

### P-04 — UNKNOWN project transfer blocks MACHINE_READY

- **Old behavior:** `project_transfer_status=UNKNOWN` was not a readiness
  blocker; only an EXPLICIT project transfer containing inferred/unknown
  interpretation branches was blocked.
- **Minimum repair:** `project_transfer_status=UNKNOWN` adds
  `PROJECT_TRANSFER_UNKNOWN` (blocker). `INFERRED` remains allowed, but only as
  explicitly labeled inferred project transfer — it is never treated as
  source-explicit. The existing `INFERRED_TRANSFER_MISLABELED_EXPLICIT` guard
  stays.
- **New invariant:** UNKNOWN applicability transfer is never machine-ready;
  INFERRED transfer is not blanket-banned.

### P-05 — exactly one timeframe for machine-ready / no comma-joined bridge

- **Old behavior:** Playbook scope required only a non-empty `timeframe_scope`;
  the bridge joined all values into one comma-separated
  `StrategyIdentity.timeframe` string (e.g. `("15m","60m")` → `"15m,60m"`).
- **Minimum repair:** a machine-ready contract must have
  `len(timeframe_scope) == 1`. Zero values keep the existing `SCOPE_MISSING`
  blocker; more than one value adds `MULTIPLE_TIMEFRAMES_UNRESOLVED` (blocker).
  `bridge_to_strategy_identity()` fails closed unless the contract is
  machine-ready and `timeframe_scope` has exactly one value, and it uses that
  value verbatim: `StrategyIdentity.timeframe = timeframe_scope[0]`.
- **New invariant:** `("15m","60m")` can never bridge into
  `StrategyIdentity.timeframe="15m,60m"`. Multiple source-permitted timeframes
  may remain in drafts/variants only.

## 3. Deterministic `primary_selection_identity`

`PlaybookContract.primary_selection_identity` is a deterministic canonical hash
(`canonical_hash`) of the **sorted** `(claim_id,
selected_primary_branch.branch_identity)` pairs, one entry per unique source
claim. It raises `ValueError` while any source claim's PRIMARY is unresolved or
the contract has no source claims — it never fabricates an identity for
incomplete PRIMARY resolution.

`ResearchFirewall.derive_primary_branch_identity(contract)` now returns
`contract.primary_selection_identity` (it no longer assumes the whole contract
has exactly one selected branch). The existing `primary_branch_identity` field
name on `WaveHypothesisBinding` / `OutcomeTestRegistration` is retained for
compatibility, but its machine meaning is now the whole-contract canonical
PRIMARY selection identity. No second PRIMARY authority was added.

## 4. Tests

Focused: `python -m unittest tests.test_playbook_contract tests.test_research_firewall -v` → **140 OK**.
Full: `python -m unittest discover -s tests -v` → **372 OK** (baseline 356 OK, +16).
`git diff --check` → clean.

Package C regressions (C01..C14):

| Test | Proves |
|------|--------|
| C01 | C1/C2 claims, only C1 PRIMARY → `NOT_MACHINE_READY` (`CLAIM_PRIMARY_MISSING`) |
| C02 | C1/C2 each exactly one PRIMARY → PRIMARY check passes (machine-ready) |
| C03 | same claim two PRIMARY → `CLAIM_PRIMARY_MULTIPLE` (blocker) |
| C04 | PRIMARY missing + `ambiguity_status=NONE` → still blocks |
| C05 | PRIMARY missing + `ambiguity_status=RESOLVED` → still blocks |
| C06 | PRIMARY complete + `UNRESOLVED_CRITICAL` → still blocks |
| C07 | required `PARTIALLY_OBSERVABLE` → `REQUIRED_INPUT_NOT_FULLY_OBSERVABLE` |
| C08 | `UNKNOWN` transfer → `PROJECT_TRANSFER_UNKNOWN`; INFERRED still allowed |
| C09 | `timeframe_scope=("15m","60m")` → `MULTIPLE_TIMEFRAMES_UNRESOLVED` |
| C10 | bridge multi-timeframe → fails closed |
| C11 | single timeframe → bridge uses exact value (`StrategyIdentity.timeframe`) |
| C12 | `primary_selection_identity` deterministic |
| C13 | changing a claim's PRIMARY changes `primary_selection_identity` |
| C14 | Package B registration binds `primary_selection_identity`; correct match registers, old single-branch identity cannot impersonate |

Stale old-expectation updates (the old contract-wide PRIMARY bypass was not
preserved to keep old tests green):

- `test_missing_primary_blocks_when_required` now expects `CLAIM_PRIMARY_MISSING`.
- `test_multiple_primary_selected_blocks` was replaced by
  `test_each_claim_with_exactly_one_primary_is_machine_ready` (two claims, each
  with its own PRIMARY, is now machine-ready) and
  `test_duplicate_primary_for_one_claim_blocks` (two PRIMARY branches for the
  same claim is a blocker).

## 5. Remaining limitations

- `PARTIALLY_OBSERVABLE` required inputs block machine readiness in this
  package; a future explicitly governed inferred surrogate must be introduced as
  a separate interpretation / contract version (not done here).
- `ambiguity_status` remains descriptive; deriving ambiguity from a mandatory
  field-level critical-semantic inventory is out of scope for this package.
- Multi-timeframe contracts stay valid as drafts/variants but cannot bridge;
  resolving a PRIMARY timeframe from source-permitted variants is a separate
  research decision.
- `primary_selected` is still the branch-level flag a contract author sets; this
  package enforces the claim-level derivation invariant on that flag but does
  not itself justify *which* branch a source would select (that remains
  Protocol v1.0 §2 source-justification responsibility).

## 6. Status

```text
STATUS=PACKAGE_C_REPAIR_COMPLETE
BASELINE=e8ccab103a43c464aef6cc02f9566083e7acd922
BRANCH=repair/package-c-playbook-protocol-v01
P01_CLAIM_LEVEL_PRIMARY=FIXED
P02_AMBIGUITY_SELF_ATTESTATION_CLOSED=FIXED
P03_PARTIAL_REQUIRED_INPUT_BLOCKS=FIXED
P04_UNKNOWN_TRANSFER_BLOCKS=FIXED
P05_SINGLE_TIMEFRAME_REQUIRED=FIXED
PRIMARY_SELECTION_IDENTITY=ADDED
FIREWALL_PRIMARY_BINDING_UPDATED=YES
PACKAGE_B_REGRESSIONS_GREEN=YES
CURRENT_STATE_CHANGED=NO
FROZEN_PROTOCOL_CHANGED=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

## Pre-integration correction

Review authority: `docs/reviews/PARALLEL_PACKAGE_C_D_F_PREINTEGRATION_REVIEW_V0_1.md`
(verdict `PACKAGE_C_INTEGRATION=BLOCKED_PENDING_BOUNDED_CORRECTION`). This is the
single bounded pre-integration correction; the original P-01..P-05 direction is
preserved. Branch merged `origin/main` (`40f27b24...`) with `git merge
origin/main --no-edit` (merge commit `620029b1...`); the new main content was
review + CURRENT_STATE and merged without conflicts. No rebase / force-push /
main modification.

### C-C01 — outcome registration requires a MACHINE_READY PlaybookContract

- **Root defect:** `ResearchFirewall.register_outcome_test()` did not require
  `validate_contract(contract).ready`. A caller could hand-build a
  `StrategyIdentity` carrying `playbook_contract_identity=contract.contract_identity`
  (bypassing `bridge_to_strategy_identity`) and register a contract that Package
  C itself marks `NOT_MACHINE_READY`.
- **Minimum fix:** `register_outcome_test()` calls the single existing authority
  `validate_contract(contract)` first and raises fail-closed
  `PLAYBOOK_CONTRACT_NOT_MACHINE_READY: <blockers>` (e.g.
  `PLAYBOOK_CONTRACT_NOT_MACHINE_READY: PROJECT_TRANSFER_UNKNOWN`) before any
  registration / lineage mapping / wave first-look mutation. No second readiness
  implementation was added.
- **Regressions:** CC01-A (required PARTIALLY_OBSERVABLE → `REQUIRED_INPUT_NOT_FULLY_OBSERVABLE`),
  CC01-B (`project_transfer_status=UNKNOWN` → `PROJECT_TRANSFER_UNKNOWN`),
  CC01-C (`timeframe_scope=("15m","60m")` → `MULTIPLE_TIMEFRAMES_UNRESOLVED`),
  CC01-D (incomplete claim PRIMARY → `CLAIM_PRIMARY_MISSING`). Each also proves
  no registry registration, no `family_claim_lineage` mutation, and no wave
  first-look / lock after the failure.
- **Result:** `OUTCOME_REGISTRATION_REQUIRES_MACHINE_READY_PLAYBOOK_CONTRACT=YES`.

### C-C02 — duplicate source claim ids fail closed

- **Root defect:** `PlaybookContract` permitted two `SourceClaimRef` records with
  the same `claim_id` but different source anchors. Claim-level PRIMARY resolved
  by `claim_id` and `primary_selection_identity` collapsed the ids with a set, so
  two real source records could be covered by one branch / one PRIMARY.
- **Minimum fix:** draft construction stays permissive; `validate_contract()`
  adds the explicit blocker `DUPLICATE_SOURCE_CLAIM_ID` (NOT_MACHINE_READY), and
  `primary_selection_identity` raises `ValueError("duplicate source claim ids ...")`
  instead of hashing a collapsed set. No fuzzy source-claim equivalence invented.
- **Regressions:** CC02-A (duplicate claim id → `DUPLICATE_SOURCE_CLAIM_ID`),
  CC02-B (`primary_selection_identity` raises), CC02-C (one branch referencing
  `("C1",)` with `primary_selected=True` still cannot make it machine-ready).
- **Result:** `SOURCE_CLAIM_IDS_UNIQUE_FOR_PRIMARY_RESOLUTION=YES`.

### C-C03 — StrategyIdentity must equal the Playbook bridge output

- **Root defect:** `strategy.playbook_contract_identity == contract.contract_identity`
  is a caller-assertable field; it does not prove the StrategyIdentity is the
  deterministic bridge output.
- **Minimum fix:** one small shared validator
  `validate_strategy_against_playbook_contract(contract, strategy)` in
  `src/playbook_contract.py` is the single semantic authority. It first requires
  `validate_contract(contract).ready`, then compares the exact deterministic
  bridge facts A..L (research lineage, family, `playbook_contract_identity`,
  applicable instruments == canonical contract instrument scope, single
  timeframe == `timeframe_scope[0]`, machine code/environment hashes, required
  feature versions, typed parameter identities via `parameter_identity`,
  data exposure reference, source == `source_scope or family_id`, and the
  deterministic version `f"pc-{contract_version}-{contract_identity}"`).
  `bridge_to_strategy_identity()` constructs the identity and then calls the same
  validator; `ResearchFirewall.register_outcome_test()` calls the same validator
  (replacing the previous caller-assertable `playbook_contract_identity`-only
  check). No StrategyIdentity dataclass freeze, no token, no registry, no
  signature system, no new lifecycle/parent rules.
- **Regressions:** a valid bridge strategy registers normally; CC03-A..J each
  tamper exactly one field (applicable_instruments, timeframe, code_hash,
  environment_hash, required_feature_versions, typed parameter,
  data_exposure_history_reference, source, strategy_version,
  playbook_contract_identity) and prove `register_outcome_test` fails closed.
  The wave binding is derived from the valid strategy, so it can never be
  recomputed to match a tampered strategy.
- **Result:** `OUTCOME_REGISTRATION_REQUIRES_STRATEGY_EQUIVALENT_TO_PLAYBOOK_BRIDGE=YES`.

### Test fixture consequence

The shared synthetic fixture (`tests/synthetic_fixture.py`) now produces
strategies that are exactly bridge-equivalent: `make_strategy()` uses the bridge
version string and builds a consistent contract from bridge-relevant overrides,
and `build_synthetic_firewall()` reverse-rebuilds the exact bound contract from
the strategy's facts. B-C03 lineage-reuse uses a single claim (a duplicate
claim_id contract is now invalid for PRIMARY resolution), and B-C04 declares the
two features on the contract machine. All Package B invariants remain green.

### Correction status

```text
STATUS=PACKAGE_C_PREINTEGRATION_CORRECTION_COMPLETE
BRANCH=repair/package-c-playbook-protocol-v01
PRE_CORRECTION_TIP=1ca8cef5eb0f019d1f39ad687a2ce5b1c097d890
MAIN_MERGE_COMMIT=620029b1b32d63315e5204e44d019edd3d77793a
CC01_MACHINE_READY_REQUIRED_AT_REGISTRATION=YES
CC02_DUPLICATE_CLAIM_IDS_FAIL_CLOSED=YES
CC03_STRATEGY_EQUALS_PLAYBOOK_BRIDGE_SEMANTICS=YES
INVALID_CONTRACT_NO_REGISTRY_MUTATION=YES
INVALID_CONTRACT_NO_LINEAGE_MUTATION=YES
INVALID_CONTRACT_NO_FIRST_LOOK=YES
PRIMARY_SELECTION_DUPLICATE_ID_REJECTED=YES
MANUAL_STRATEGY_SCOPE_TAMPER_REJECTED=YES
MANUAL_STRATEGY_MACHINE_TAMPER_REJECTED=YES
VALID_BRIDGE_STRATEGY_REGISTRATION_PASSES=YES
PACKAGE_B_INVARIANTS_GREEN=YES
FOCUSED_TESTS=158 OK
FULL_TESTS=390 OK
DIFF_CHECK=CLEAN
CURRENT_STATE_CHANGED=NO
FROZEN_PROTOCOL_CHANGED=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```
