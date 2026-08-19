# PACKAGE_B_ARTIFACT_LINEAGE_SOURCE_DURABLE_GOVERNANCE_SPEC_V0_1

> Date: 2026-08-20
> Status: ACTIVE / BOUNDED IMPLEMENTATION SPEC
> Parent repair plan: `docs/reviews/FULL_PROJECT_SECOND_PASS_REPAIR_PLAN_V0_1.md`
> Findings: `F-06 F-07 F-08 F-09 F-10 F-12 F-13 P-06`
> Candidate outcomes: NOT_AUTHORIZED

## 1. Scope rule

Package B fixes the artifact/governance binding layer only. It must not redesign Playbook claim-level PRIMARY semantics (Package C), canonical completeness (Package D), execution/capital (Package E), source-byte historical provenance (Package F), or old F/G/H lanes (Package G).

For every finding: reproduce -> minimum repair -> regression test. If the repository lacks an authorized semantic truth, fail closed instead of inventing one.

## 2. F-06 — derive wave identities from actual artifacts

`WaveHypothesisBinding` may remain a value object, but an outcome registration must recompute and verify its values from the actual artifacts. Caller-provided matching strings are not authority.

For Package B use these deterministic derivations:

- `primary_branch_identity`: derive from the actual `PlaybookContract.interpretations` branch currently marked `primary_selected=True`. Package B does not change the current one-contract-primary model; if the current contract does not have exactly one selected branch, registration fails closed. Package C later replaces this with Protocol-complete claim/field-level PRIMARY semantics.
- `scope_identity`: canonical hash of the actual contract/strategy scope facts: contract identity, family id, sorted StrategyIdentity applicable instruments, StrategyIdentity timeframe, contract instrument scope, contract timeframe scope and project transfer status.
- `parameter_search_identity`: canonical hash of the exact `ResearchWaveManifest.parameter_search_ranges` declaration plus the actual StrategyIdentity typed parameters. Do not accept a separately invented identity string as authority.

At `register_outcome_test`, recompute the three values and require the existing wave binding for that hypothesis to match exactly.

## 3. F-07 — bind SOURCE_ONLY / claims / Playbook / Strategy

Outcome registration must receive the actual `PlaybookContract`; remove caller authority over `family_claim_identity`.

Derive `family_claim_identity` from source evidence, independent of a cosmetic family rename: canonical hash of sorted tuples `(source_id, source_anchor, claim_status)` from the contract source claims. Do not include `claim_id` or `family_id` in this derived family-claim identity.

Registration must verify:

- contract research lineage == strategy research lineage;
- contract family id == strategy family id;
- contract source bundle identity/hash == the referenced verified SOURCE_ONLY session bundle identity/hash;
- contract SOURCE_ONLY session identity == actual session identity;
- strategy is explicitly bound to this Playbook contract.

For the last item add one optional generic field to `StrategyIdentity`:

```text
playbook_contract_identity: str | None = None
```

Include it in StrategyIdentity identity hashing. `bridge_to_strategy_identity()` must set it to `contract.contract_identity`. Ordinary legacy/synthetic StrategyIdentity construction may leave it `None`, but `register_outcome_test` must reject `None` or mismatch.

Do not parse a contract identity out of a version string.

## 4. F-08 — prevent easy lineage laundering

Do not attempt semantic AI similarity detection.

Use the derived `family_claim_identity` as the enforceable root key. `ResearchFirewall` must maintain a mapping:

```text
family_claim_identity -> research_lineage_id
```

The first valid artifact-bound registration establishes the mapping. Every later registration with the same derived family-claim identity must use the same lineage, regardless of strategy/family display rename.

If the Playbook contract declares a parent contract or the strategy declares a parent identity, existing parent lineage equality rules remain mandatory.

Persist this family-claim/lineage mapping in Package B state (F-09).

This closes deterministic laundering for the same source-claim family. Do not claim it detects arbitrary semantic equivalence across completely different source evidence; that would require a new research authority and remains fail closed/not proven.

## 5. P-06 — actual artifact bindings, without a framework

Add one small generic immutable artifact value object, preferably in `src/strategy_evidence.py`:

```text
ArtifactBinding
- artifact_kind
- artifact_reference
- sha256
- byte_size
- declared_version: str | None
```

Provide constructors that compute sha256 internally from actual bytes and, optionally, a local file path. The constructor must not accept a caller-supplied sha256 without recomputing it from the supplied content.

Canonical artifact identity must hash kind/reference/sha256/size/declared_version.

Add one immutable `OutcomeArtifactBindings` container holding exactly:

```text
code_artifact
environment_artifact
data_artifact
feature_artifacts
```

At `register_outcome_test` verify:

- code artifact sha256 == `StrategyIdentity.code_hash`;
- environment artifact sha256 == `StrategyIdentity.environment_hash`;
- data artifact declared_version == `ExperimentIdentity.data_version`;
- feature artifact declared versions exactly cover `StrategyIdentity.required_feature_versions` (empty is legal);
- stored OutcomeTestRegistration records the artifact identities, not only labels.

Do not claim this proves the supplied ValidationInput bars were read from the data artifact bytes; Package D owns canonical data-to-row provenance/completeness. Package A's TEST_ONLY synthetic data label therefore remains a label-level fixture boundary. Package B only removes the false claim that arbitrary raw hash strings are sufficient artifact attestation.

The runner's existing `artifact_identity_id` / `artifact_code_hash` caller equality check must not be treated as attestation. If these parameters serve no remaining safe purpose after firewall artifact registration, remove them rather than preserving a redundant caller-label check. Do not build an execution plugin system.

## 6. F-10 — SOURCE_ONLY verification must not be reproducible from source code

Remove the fixed deterministic issuer nonce as the verification authority.

Keep the implementation simple:

- `open_verified_session()` is the only normal API that marks a session verified;
- `record_session()` may record supplied compatibility/unverified sessions but must never make them verified regardless of a copied/recomputed `verification_evidence` string;
- maintain an internal verified-session set/registry populated only by `open_verified_session()` and trusted state restore;
- `is_verified()` requires TECHNICALLY_DENIED mode plus membership in that internal issued set and exact stored session identity;
- `verification_evidence` may remain an opaque diagnostic token generated with `secrets.token_hex()` or equivalent; verification must not be reproducible from a public fixed formula.

Do not create PKI, HSM, signing services or an OS sandbox. This fixes the documented API-level forgery defect only. The process/shell sandbox limitation remains explicitly unresolved.

## 7. F-09 — durable restart reconstruction

Use one versioned JSON state file; no database.

Implement the smallest explicit serialization/reload path for research governance state. It must round-trip:

- EvidenceLedger records/exposure facts;
- SOURCE_ONLY sessions and which sessions were project-issued verified;
- SOURCE_ONLY denial records if currently treated as audit evidence;
- OutcomeTestRegistry registrations;
- ResearchWaveRegistry manifests, locked-wave set, outcome-start set and terminal outcomes;
- StatisticalProfileRegistry profiles and locked set;
- HistoricalFinalHoldout state and registered unlock authority if any;
- family-claim -> research-lineage mapping introduced for F-08.

Preferred API shape:

```text
ResearchFirewall.save_state(path)
ResearchFirewall.load_state(path) -> ResearchFirewall
```

or an equally small `to_state_dict/from_state_dict` plus two JSON helpers.

Use a state schema version. Unknown schema version -> fail closed.

Write atomically with temp file + replace if trivial; do not create a persistence abstraction/framework.

After reload, irreversible facts must remain irreversible: a started wave is still started, recorded outcomes remain, final-holdout exposure/terminal state remains, exposure records remain, locked profiles/waves remain locked, and verified SOURCE_ONLY sessions remain the sessions that were originally issued.

This persistence is project state durability, not protection against an attacker who can arbitrarily edit local files. Do not claim tamper-proof storage.

## 8. F-12 — alternatives must equal the tested denominator

For machine enforcement, `ResearchWaveManifest.declared_outcome_tested_alternatives` must be a canonical sorted/unique tuple of the exact `hypothesis_test_id` values declared as outcome-tested alternatives.

At wave lock require:

```text
set(declared_outcome_tested_alternatives)
==
set(tested_hypothesis_test_ids)
```

No missing tested point and no extra undeclared point. Empty alternatives are therefore valid only when the tested denominator is empty; a lock still separately requires a non-empty denominator.

Human descriptions belong in other manifest description fields; do not overload the machine alternatives field with prose.

Update TEST_ONLY fixtures accordingly.

## 9. F-13 — repeated identical evidence operations are idempotent

Choose the minimal idempotent behavior; do not add timestamps/event buses.

`EvidenceLedger.append(record)` must:

- append and return the record on first occurrence;
- if the exact same `record_id` is already present, return the already stored canonical record without adding a duplicate and without raising;
- still reject impossible internal corruption where the same record id maps to non-equal record content.

Tests must show repeated identical grant/deny/audit calls do not crash and do not inflate the canonical evidence ledger.

## 10. Required cross-binding tests

At minimum prove:

1. bogus caller PRIMARY/scope/search strings cannot authorize when they differ from actual Playbook/Strategy/manifest derivation;
2. a SOURCE_ONLY session from a different bundle cannot authorize the Playbook;
3. a strategy bound to another/no Playbook contract cannot register;
4. renaming family id while reusing the same derived family-claim evidence cannot reset lineage;
5. ArtifactBinding hash is computed from bytes and changes when bytes change;
6. code/environment/data/feature artifact mismatch prevents registration;
7. a manually constructed SOURCE_ONLY session carrying the old deterministic expected token does not verify;
8. `record_session()` cannot promote a session to verified;
9. save -> fresh-process-style load preserves wave locks, first-look/outcomes, profile locks, SOURCE_ONLY issued verification, evidence exposure and final-holdout state;
10. unknown state schema fails closed;
11. declared alternatives missing/extra vs tested denominator fails wave lock;
12. repeated identical evidence append/access is idempotent;
13. current Package A invariants remain green: caller cohort/synthetic booleans absent, VALIDATION denied, non-test profile lock denied, portfolio confirmatory path closed.

All fixtures synthetic. No canonical candidate data.

## 11. Explicit non-goals

Do not modify:

- Protocol v1.0 or 12/6/6;
- Common Statistical Profile numeric design;
- claim-level PRIMARY/critical ambiguity model (Package C);
- canonical completeness/provenance (Package D);
- execution/capital/portfolio reopening (Package E);
- historical source byte claims (Package F);
- F/G/H branches;
- CURRENT_STATE.md.

No candidate PnL/return/win-rate/Sharpe/drawdown inspection.

## 12. Acceptance

One isolated branch, one coherent Package B commit series, full tests, `git diff --check`, and explicit remaining limitations. Project brain performs integration review; worker does not merge main.
