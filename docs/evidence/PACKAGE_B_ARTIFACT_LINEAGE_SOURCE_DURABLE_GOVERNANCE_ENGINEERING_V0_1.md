# PACKAGE B — ARTIFACT LINEAGE / SOURCE DURABLE GOVERNANCE — ENGINEERING EVIDENCE V0_1

Authoritative spec: `docs/reviews/PACKAGE_B_ARTIFACT_LINEAGE_SOURCE_DURABLE_GOVERNANCE_SPEC_V0_1.md`
Findings repaired: **F-06, F-07, F-08, F-09, F-10, F-12, F-13, P-06**

## 1. Scope

One isolated branch, one coherent Package B commit series on
`repair/package-b-artifact-governance-v01`, based on
`07b84958c96db85f7a984a1e7712be5ba37d65d0` (origin/main, which already merged
Package A). Package B repairs the artifact-lineage and SOURCE_ONLY durable
governance layer. It does **not** redesign Packages C/D/E/F, does not reopen the
portfolio confirmatory path, does not modify `CURRENT_STATE.md`, frozen
protocols, or integration-owned authority, and uses only synthetic fixtures (no
canonical candidate data, no real broker/trading).

## 2. Root causes and minimum repairs

### F-06 — wave identities were caller-supplied, not derived from actual artifacts

- **Root cause:** PRIMARY/scope/parameter-search identity values were caller
  strings in the registration path; a caller could self-declare them without any
  binding to the actual `PlaybookContract` / `StrategyIdentity` /
  `ResearchWaveManifest` facts.
- **Repair:** `register_outcome_test` now derives all three identities from the
  actual artifacts and requires an exact match with the pre-registered wave
  binding:
  - `derive_primary_branch_identity(contract)` — exactly one `primary_selected`
    branch required;
  - `derive_scope_identity(contract, strategy)` — contract identity / family /
    instruments / timeframes / transfer status;
  - `derive_parameter_search_identity(parameter_search_ranges, strategy)` — wave
    declaration plus the exact typed strategy parameters.
  The caller never supplies these values (caller PRIMARY/scope/search identity
  authority removed).

### F-07 — SOURCE_ONLY / Playbook / Strategy were not explicitly bound

- **Root cause:** a strategy was not required to be bound to the Playbook
  contract that claims it, and a session/contract bundle cross-check was absent.
- **Repair:**
  - `StrategyIdentity` gained `playbook_contract_identity` (included in the
    identity hash); `bridge_to_strategy_identity()` sets it to
    `contract.contract_identity`; ordinary legacy construction may leave it
    `None` but `register_outcome_test` rejects `None`/mismatch.
  - `register_outcome_test` verifies contract↔strategy research lineage/family,
    contract↔session source bundle identity/hash, contract↔session
    `source_only_session_identity`, and
    `strategy.playbook_contract_identity == contract.contract_identity`.
  - Registration requires a verified SOURCE_ONLY session; an unverified manual
    session fails closed at registration time.

### F-08 — easy lineage laundering via family rename / renumbering

- **Root cause:** family-claim identity could be laundered by renaming a family
  or renumbering claims.
- **Repair:** `derive_family_claim_identity(contract)` hashes the sorted
  `(source_id, source_anchor, claim_status)` tuples only (claim_id/family_id
  deliberately excluded). `register_outcome_test` maintains a
  family-claim → research-lineage mapping; reusing the same family-claim
  evidence under a renamed family + new lineage is rejected.

### F-09 — durable restart reconstruction

- **Root cause:** research governance state (sessions, waves, profiles,
  registrations, final-holdout) was in-memory only.
- **Repair:** versioned JSON state file.
  - `STATE_SCHEMA_VERSION = "v1"`;
  - `ResearchFirewall.to_state_dict() / from_state_dict() / save_state(path) /
    load_state(path)`;
  - atomic write (temp file + `os.replace`);
  - unknown schema version fails closed;
  - round-trips ledger records/exposures, SOURCE_ONLY sessions + issued-verified
    set + denial records, registrations, wave manifests/locks/outcome-start/
    terminal outcomes, profile locks, final-holdout state + unlock authority,
    and the family-claim → lineage mapping.
  - After reload irreversible facts remain irreversible (verified sessions,
    locked waves/profiles, started first-looks, recorded outcomes, exposures,
    final-holdout terminal state).

### F-10 — SOURCE_ONLY verification must not be reproducible from source

- **Root cause:** verification used a fixed deterministic issuer nonce derivable
  from public source.
- **Repair:** `open_verified_session()` is the only normal verified-creation
  path; it stamps an opaque `secrets.token_hex(32)` diagnostic token and records
  the session in an internal issued-verified set (`session_id → issued identity`).
  `record_session()` records compatibility sessions as-is but can never promote
  to verified. `is_verified()` requires `TECHNICALLY_DENIED` mode + issued-set
  membership + exact stored session identity. A manual session carrying the old
  deterministic token is not verified (B14).

### F-12 — alternatives must equal the tested denominator

- **Root cause:** declared outcome-tested alternatives were not machine-bound to
  the tested denominator.
- **Repair:** `ResearchWaveManifest.declared_outcome_tested_alternatives` is a
  canonical sorted/unique tuple of the exact `hypothesis_test_id` values. Wave
  lock requires
  `set(declared_outcome_tested_alternatives) == set(tested_hypothesis_test_ids)`.
  Missing or extra declared points fail the lock; empty alternatives are valid
  only when the denominator is empty (lock still requires a non-empty
  denominator).

### F-13 — repeated identical evidence operations are idempotent

- **Root cause:** repeated identical grant/deny/audit could inflate evidence.
- **Repair:** `EvidenceLedger.append(record)` appends on first occurrence,
  returns the already-stored canonical record on an exact duplicate (no crash,
  no inflation), and still rejects impossible internal corruption (same record
  id → non-equal content).

### P-06 — actual artifact bindings without a framework

- **Root cause:** arbitrary raw hash strings were treated as sufficient artifact
  attestation.
- **Repair:**
  - `ArtifactBinding` (frozen, `init=False`): only `from_bytes`/`from_file`
    compute `sha256` internally from actual content; there is no public
    constructor accepting a caller digest. `identity_id` hashes
    kind/reference/sha256/byte_size/declared_version.
  - `OutcomeArtifactBindings` (frozen) holds exactly code/environment/data/
    feature artifacts with kind checks; feature versions sorted/unique (empty
    legal).
  - `register_outcome_test` verifies: code sha256 == `code_hash`,
    environment sha256 == `environment_hash`, data declared_version ==
    `data_version`, feature declared versions exactly cover
    `required_feature_versions`; the registration stores the artifact
    identities.
  - The runner's obsolete `artifact_identity_id` / `artifact_code_hash` caller
    equality check was removed (no redundant caller-label attestation).

## 3. State schema (v1)

`ResearchFirewall.STATE_SCHEMA_VERSION == "v1"`. `to_state_dict()` emits:

```text
state_schema_version, ledger, source_only_sessions, source_only_issued_verified,
source_only_denials, outcome_registrations, wave_manifests, wave_locked,
wave_outcome_started, wave_outcomes, statistical_profiles,
statistical_profile_locked, final_holdout_state, final_holdout_unlock_authority,
family_claim_lineage
```

Unknown `state_schema_version` → `ValueError` (fail closed). This is project
state durability, not tamper-proof storage.

## 4. Invariants enforced

- PRIMARY/scope/search identities are derived from actual artifacts and must
  match the wave binding exactly.
- The strategy must be explicitly bound to the Playbook contract.
- The SOURCE_ONLY session must be verified and bundle/session-identity matched.
- The family-claim identity binds a single research lineage.
- Wave lock requires declared alternatives == tested denominator.
- Evidence append is idempotent by canonical record id.
- All artifact attestation is byte-derived; no caller-supplied digests.
- Only TEST_ONLY profiles can lock; only the governed synthetic data version
  grants a candidate pre-outcome access; VALIDATION/final-holdout/shadow remain
  denied.

## 5. Tests

Regression suite added as `PackageBArtifactLineageGovernanceTests` in
`tests/test_research_firewall.py` plus artifact-hash tests in
`tests/test_strategy_evidence.py` and a bridge test in
`tests/test_playbook_contract.py`:

| Test | Proves |
| --- | --- |
| B01/B02/B03 | bogus caller PRIMARY/scope/search strings rejected at registration (derived identity authority removed) |
| B04 | a SOURCE_ONLY session from a different bundle cannot authorize |
| B05 | strategy with `playbook_contract_identity=None` cannot register |
| B06 | strategy bound to contract A cannot register under contract B |
| B07 | family rename reusing the same family-claim evidence cannot reset lineage |
| B08/B09 | `ArtifactBinding` hash is computed from bytes; a one-byte change changes digest/identity |
| B10/B11/B12/B13 | code/environment/data/feature artifact mismatch prevents registration |
| B14 | old deterministic fixed-nonce token on a manual session is NOT verified |
| B15 | `record_session()` cannot promote a session to verified |
| B16 | `open_verified_session()` is verified |
| B17..B23 | save → fresh-load preserves verified sessions, manual sessions stay unverified, wave locks, first-look/terminal outcomes, profile locks, ledger exposure, final-holdout terminal state |
| B24 | unknown state schema version fails closed |
| B25/B26/B27 | declared alternatives missing/extra fail wave lock; exact set locks |
| B28/B29 | repeated identical evidence append / grant+deny are idempotent (no inflation) |
| B30 | Package A protections intact (no caller cohort/synthetic booleans, VALIDATION denied, non-test profile lock denied, portfolio confirmatory path closed) |
| bridge | `bridge_to_strategy_identity()` sets `playbook_contract_identity == contract.contract_identity` |

- **Focused tests** (Package B affected set, 10 modules): `Ran 237 tests ... OK`
- **Full canonical suite**: `Ran 350 tests ... OK`
- **`git diff --check`**: exit 0 (LF→CRLF warnings only)

## 6. Remaining limitations (explicit)

- `verification_evidence` is an opaque diagnostic token; process/shell sandboxing
  limitation remains unresolved (documented API-level forgery fixed only).
- State durability is not tamper-proof: an actor who can edit the local state
  file can edit anything on disk.
- Package B proves byte-derived artifact hashing, not canonical
  data-to-row provenance/completeness (Package D owns that).
- Claim-level PRIMARY/critical ambiguity model (Package C), execution/capital/
  portfolio reopening (Package E), and historical source byte claims
  (Package F) are untouched.
- `ArtifactBinding.from_file` reads bytes then hashes; it does not bind a
  filesystem path over time.
- No real broker order submission / real-money trading; no canonical candidate
  outcome data used anywhere.

## 7. Status

```text
STATUS=COMPLETE
BASELINE=07b84958c96db85f7a984a1e7712be5ba37d65d0
BRANCH=repair/package-b-artifact-governance-v01
COMMITS=3ca4052 (production), 11fd5fb (tests), plus docs evidence (tip of branch)
F06_ARTIFACT_DERIVED_PRIMARY_SCOPE_SEARCH=YES
F07_SOURCE_PLAYBOOK_STRATEGY_BINDING=YES
F08_FAMILY_CLAIM_LINEAGE_BINDING=YES
F09_DURABLE_STATE_RESTART=YES
F10_SOURCE_ONLY_FORGE_PATH_CLOSED=YES
F12_ALTERNATIVES_DENOMINATOR_BOUND=YES
F13_EVIDENCE_IDEMPOTENT=YES
P06_ACTUAL_ARTIFACT_BINDINGS=YES
PLAYBOOK_CONTRACT_IDENTITY_ON_STRATEGY=YES
CALLER_PRIMARY_IDENTITY_AUTHORITY_REMOVED=YES
CALLER_SCOPE_IDENTITY_AUTHORITY_REMOVED=YES
CALLER_SEARCH_IDENTITY_AUTHORITY_REMOVED=YES
CALLER_FAMILY_CLAIM_IDENTITY_AUTHORITY_REMOVED=YES
OLD_FIXED_NONCE_FORGE_TEST=YES
STATE_SCHEMA_VERSION=v1
UNKNOWN_STATE_SCHEMA_FAIL_CLOSED=YES
RESTART_IRREVERSIBLE_FACTS_PRESERVED=YES
PORTFOLIO_PATH_STILL_CLOSED=YES
FILES=14 (4 src, 10 tests)
FOCUSED_TESTS=237 OK
FULL_TESTS=350 OK
DIFF_CHECK=clean
NO_CANDIDATE_OUTCOME_DATA_USED=YES
FROZEN_PROTOCOL_CHANGED=NO
CURRENT_STATE_CHANGED=NO
REMAINING_LIMITATIONS=see section 6
BLOCKER=NONE
```
