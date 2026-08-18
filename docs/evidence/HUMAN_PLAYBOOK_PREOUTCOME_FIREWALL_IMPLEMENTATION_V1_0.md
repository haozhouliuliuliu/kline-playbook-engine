# HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0

> Version: 1.0 (final engineering state)
> Date: 2026-08-19
> Status: IMPLEMENTED_AND_TESTED / ENGINEERING_VERIFIED / IDENTITY_BOUND
> Work package: `HUMAN_PLAYBOOK_PREOUTCOME_RESEARCH_FIREWALL_IDENTITY_CROSS_BINDING_HARDENING`
> Tool decision: `USE_EXISTING` (no new tool adopted)
> Acceptance review: `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_0.md`
> Final acceptance delta: `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_1.md`
> Review verdict: v1.0 `PARTIAL_FIX_REQUIRED` and v1.1 `PARTIAL_FIX_REQUIRED` (E-5) -> resolved by this engineering package
> Acceptance boundary: `PREOUTCOME_FIREWALL_ACCEPTANCE=COMPLETE_VERIFIED` (engineering)

## 1. Frozen authority references (do not modify)

- `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

Frozen facts preserved unchanged:

```text
RESEARCH_PROTOCOL_VERSION=1.0
RESEARCH_PROTOCOL_STATUS=FROZEN_BINDING

DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31

PROJECT_GOVERNED_HISTORICAL_HOLDOUT != PROSPECTIVE_GENUINELY_UNSEEN_DATA
```

This is ordinary engineering implementation under Protocol v1.0 §16. It does not
modify any frozen research semantics, the frozen 12/6/6 split, the Owner freeze
evidence, PRIMARY_BRANCH semantics, RESEARCH_WAVE semantics,
`INSUFFICIENT_EVIDENCE`, CAT1/CAT2/CAT3, live AI semantics, or the
historical-final state machine.

## 2. Implementation owner / module

Single owner of the pre-outcome research access rules:
`src/research_firewall.py`:
- `ResearchFirewall` (single owner), `PreOutcomeGate` (low-level pure gate),
  `PreOutcomeGateDecision`, `GateControl`;
- `OutcomeTestRegistration` + `OutcomeTestRegistry` — canonical identity-bound
  hypothesis/outcome-test registration;
- `WaveHypothesisBinding` — immutable per-hypothesis PRIMARY/scope/parameter-search
  identity frozen by the wave (machine-comparable identity authority);
- `SourceOnlyPolicy`, `SourceOnlySession` (project-issued verification),
  `SourceOnlyClaimExtractionContext`, `ApprovedSourceBundle`,
  `ClaimRecordOutput`, `ClaimRecordDraft`;
- `ResearchWaveRegistry`, `ResearchWaveManifest` (single canonical denominator);
- `StatisticalProfileRegistry`, `CommonStatisticalProfile` (identity/lock only);
- `HistoricalFinalHoldoutStateMachine` (never auto-unlocks);
- `classify_cohort` and frozen constants.

Legacy compatibility:
`src/strategy_evidence.py` — `DatasetClass` gained the canonical
`PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT` and `SHADOW_FORWARD` members;
`FINAL_UNSEEN` is kept as a legacy name. `FinalUnseenFirewall` is a thin
compatibility adapter that **delegates every decision** to `ResearchFirewall`.
There is exactly one owner of the access rules; there is no second parallel
firewall rule set in the project.

## 3. Identity-bound outcome-test registration (acceptance gaps E-1, E-2)

Every candidate outcome access is keyed by a single registered
`hypothesis_test_id`. `OutcomeTestRegistration` is immutable and binds:
- hypothesis/test identity;
- `experiment_identity_id` + `strategy_identity_id` (ExperimentIdentity /
  strategy identity);
- research lineage;
- family / claim identity;
- PRIMARY branch identity;
- instrument/timeframe/context scope identity;
- parameter/search identity;
- SOURCE_ONLY session id + session identity hash;
- source bundle identity/hash;
- `research_wave_id`;
- exact statistical profile id + profile identity hash;
- multiplicity / counting-unit identity;
- protocol version.

`ResearchFirewall.request_candidate_outcome_access()` accepts only
`cohort`, `experiment`, `hypothesis_test_id`, and `synthetic_fixture`. All other
facts are resolved from the registries and verified at access time. It is
impossible to combine an unrelated locked wave + session + experiment + profile
just because each is individually locked (`IDENTITY_BINDING:*` denies).

## 4. No caller-supplied frozen lock booleans (acceptance gap E-1)

The authoritative production paths
`ResearchFirewall.request_candidate_outcome_access()` and
`ResearchFirewall.evaluate_gate()` no longer accept
`multiplicity_counting_unit_locked` or `primary_scope_search_identities_locked`.
All gate-critical lock state is derived from project-owned immutable
registries/artifacts. The low-level pure `PreOutcomeGate.evaluate()` still accepts
booleans and is covered by direct unit tests only.

## 5. Implemented controls

| Control | Status | Where |
| --- | --- | --- |
| SOURCE_ONLY_CONTROLS | ACTIVE_AND_VERIFIED (project-issued) | `SourceOnlyPolicy` / `SourceOnlySession` |
| COMMON_STATISTICAL_PROFILE | interface + lock implemented; real numeric profile NOT designed | `CommonStatisticalProfile` / `StatisticalProfileRegistry` |
| MULTIPLICITY_COUNTING_UNIT | LOCKED (derived from locked wave + manifest counting-unit identity) | `ResearchWaveManifest` / gate |
| RESEARCH_WAVE | LOCKED (immutable manifest; single canonical denominator) | `ResearchWaveRegistry` / `ResearchWaveManifest` |
| PRIMARY_SCOPE_SEARCH_IDENTITIES | LOCKED (bound in the outcome-test registration) | `OutcomeTestRegistration` / gate |

### 5.1 SOURCE_ONLY (project-issued verification)

`SourceOnlySession` records model identity/version, prompt/spec version, source
bundle identity/hash, tool/retrieval mode, protected market access mode, and an
explicit researcher/model exposure note.

Verification is **project-issued**: only `SourceOnlyPolicy.open_verified_session()`
stamps `verification_evidence` that `is_verified()` accepts. A manually constructed
`TECHNICALLY_DENIED` session (or one with forged evidence) is **not** verified.
`PROMPT_ONLY` ("the prompt said do not look") is not technical denial. The policy
exposes no protected-period market outcome retrieval surface; the only
market-outcome-related entry point always returns `DENIED` and records the denial.

A bounded `SourceOnlyClaimExtractionContext` runner structurally holds only an
approved source bundle (provenance), SOURCE_ONLY services/session, and a
provenance/claim-record output surface. It has no canonical market-data
repository, historical outcome API, validation/final data surface, or generic
market-outcome retrieval service; any protected-period project market-outcome
request through it is `DENIED` + audited.

This does **not** claim to eliminate external model latent memory. Latent/parametric
prior market knowledge that cannot be proven absent remains a disclosed residual
threat-model risk under the frozen protocol.

### 5.2 RESEARCH_WAVE (single canonical denominator; acceptance gaps E-3, E-5)

`ResearchWaveManifest` is immutable and directly binds the complete tested
hypothesis identity set (`tested_hypothesis_test_ids`), plus the exact
statistical profile id/hash, the multiplicity counting-unit identity, and a
`hypothesis_bindings: tuple[WaveHypothesisBinding, ...]` — the deterministic
per-hypothesis PRIMARY/scope/parameter-search identity authority. The permanent
denominator is **derived from the manifest** — there is no second mutable
pre-lock list, so manifest and denominator cannot diverge. The human-readable
`instrument_timeframe_context_scope` / `parameter_search_ranges` are retained as
informational only; they never carry security identity authority.

Manifest construction fails closed when:
- a tested hypothesis has no binding (missing);
- a binding exists for a hypothesis not in the tested set (extra);
- a binding id is duplicated.

`ResearchWaveRegistry.lock()` fails closed and verifies:
- the tested set is non-empty;
- every tested hypothesis identity has a registration;
- each registration points to this wave;
- each registration binds the same profile id/identity and counting-unit identity
  as the manifest;
- **each registration's `primary_branch_identity`, `scope_identity`, and
  `parameter_search_identity` exactly match the wave-frozen `WaveHypothesisBinding`
  for that hypothesis (E-5 cross-artifact binding).**

Once locked, the test set is permanently immutable. A new family/claim/branch
requires a new wave / new search event. `FAIL` and `INSUFFICIENT_EVIDENCE`
remain permanently in the tested denominator.

### 5.3 Common statistical profile interface

`CommonStatisticalProfile` implements fields, identity hash, version, lock state,
and a `TEST_ONLY` marker for fixtures. This package deliberately does **not**
decide the final confidence method, minimum-event numbers, multiplicity-correction
numbers, or dependence thresholds. The real `COMMON_STATISTICAL_PROFILE_V1` numeric
standard must be designed and independently reviewed separately under Protocol v1.0
before any candidate outcome.

### 5.4 Pre-outcome gate (acceptance gap E-4)

The gate requires all five controls satisfied:

```text
SOURCE_ONLY_CONTROLS            = ACTIVE_AND_VERIFIED
COMMON_STATISTICAL_PROFILE      = LOCKED
MULTIPLICITY_COUNTING_UNIT      = LOCKED
RESEARCH_WAVE                   = LOCKED
PRIMARY_SCOPE_SEARCH_IDENTITIES = LOCKED
```

The profile used at access must equal the exact profile id/hash bound in the wave
manifest and the hypothesis registration (`WAVE_PROFILE_ID_MISMATCH`,
`PROFILE_IDENTITY_MISMATCH` -> DENY). `PRIMARY_SCOPE_SEARCH_IDENTITIES=LOCKED` is
reported only after `ResearchFirewall._resolve_binding()` confirms the locked wave
holds an exact `WaveHypothesisBinding` for the hypothesis and the registration's
PRIMARY/scope/parameter-search identities still match it
(`PRIMARY_BRANCH_IDENTITY_MISMATCH`, `SCOPE_IDENTITY_MISMATCH`,
`PARAMETER_SEARCH_IDENTITY_MISMATCH` -> DENY). Because only `TEST_ONLY` profiles
exist in this package, the only reachable grant is
`SYNTHETIC_DEVELOPMENT_OUTCOME_ONLY` (synthetic dummy fixtures); a `TEST_ONLY`
profile refuses a non-synthetic fixture
(`TEST_ONLY_PROFILE_REQUIRES_SYNTHETIC_FIXTURE`).

## 6. Durable first-look and append-only outcome audit

- On the first authoritative outcome grant, `ResearchWaveRegistry` durably
  declares the wave outcome-test-start (`WAVE_OUTCOME_TEST_STARTED` evidence
  record), and the grant record carries an explicit
  `SYNTHETIC_TEST_ONLY_FIRST_LOOK` audit note for TEST_ONLY synthetic grants so
  they can never be confused with a future real candidate wave.
- `record_terminal_outcome()` is append-only: the first terminal outcome is
  immutable; re-recording the same fact is idempotent; a different outcome is
  rejected (`cannot overwrite`). `FAIL` / `INSUFFICIENT_EVIDENCE` stay in the
  permanent denominator. Future CAT1 revisions must use explicit
  evidence/revision events (not implemented in this package, by design).

## 7. Denied paths

- missing / unverified SOURCE_ONLY session (including PROMPT_ONLY and
  manually-forged sessions) -> DENY;
- statistical profile missing / draft / unlocked -> DENY;
- research wave missing / unlocked -> DENY;
- unregistered hypothesis/test -> DENY (`UNREGISTERED_HYPOTHESIS_TEST`);
- experiment/strategy identity mismatch vs registration -> DENY
  (`EXPERIMENT_IDENTITY_MISMATCH`, `STRATEGY_IDENTITY_MISMATCH`);
- hypothesis not in the wave tested set -> DENY;
- wave/profile id/hash mismatch -> DENY / lock fail;
- counting-unit identity mismatch -> DENY / lock fail;
- hypothesis PRIMARY/scope/parameter-search identity mismatch vs wave-frozen
  binding -> DENY / lock fail (`PRIMARY_BRANCH_IDENTITY_MISMATCH`,
  `SCOPE_IDENTITY_MISMATCH`, `PARAMETER_SEARCH_IDENTITY_MISMATCH`,
  `PRIMARY_SCOPE_SEARCH_BINDING_MISSING`);
- source bundle / session identity mismatch -> DENY;
- VALIDATION -> default DENY (no validation authority in this package);
- PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT -> always DENY
  (`FINAL_HISTORICAL_HOLDOUT_ALWAYS_LOCKED`);
- Shadow/Forward -> DENY (`SHADOW_FORWARD_NOT_AUTHORIZED`);
- out-of-scope dates -> DENY;
- locked wave cannot gain new hypotheses; a new hypothesis requires a new wave;
- final-holdout unlock is never automatic; exposure requires a separate,
  explicitly registered unlock authority and no such authority is registered by
  default.

## 8. Historical final naming and state machine

Compatibility migration: `DatasetClass.FINAL_UNSEEN` is preserved (old code/tests
keep working). The canonical semantic name
`DatasetClass.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT` was added, plus
`DatasetClass.SHADOW_FORWARD`. Both final names and Shadow/Forward are always
denied by the single owner.

State machine (`HistoricalFinalHoldoutStateMachine`):

```text
FINAL_HISTORICAL_HOLDOUT_LOCKED
-> FINAL_HISTORICAL_HOLDOUT_EXPOSED
-> FINAL_ACCEPTED | FINAL_REJECTED | FINAL_VOID_IMPLEMENTATION_DEFECT
```

This package implements **no** automatic final-holdout unlock. `VOID` changes a
conclusion and never restores holdout status.

## 9. Compatibility approach

- `FinalUnseenFirewall` keeps its legacy constructor and interface
  (`request_access(experiment, dataset_class)`, `has_exposure(...)`) and now
  delegates to `ResearchFirewall.legacy_request_access`.
- `validation_runner.py` and `portfolio_semantics.py` continue to use
  `FinalUnseenFirewall` unchanged; their existing behavior (final-cohort deny,
  deterministic records) is preserved and covered by the existing test suite.
- Coarse DEVELOPMENT/VALIDATION grants through the legacy path are **not**
  candidate-outcome authorization. The authoritative candidate-outcome path is
  `ResearchFirewall.request_candidate_outcome_access()` / `evaluate_gate()`,
  which is identity-bound and fail-closed.

## 10. Tests

New: `tests/test_research_firewall.py` (54 tests) covering the 15 identity-binding
regressions plus the E-5 PRIMARY/scope/parameter-search cross-binding regressions:
1. unrelated locked wave cannot authorize an experiment/hypothesis outside its
   registered test set;
2. unrelated verified SOURCE_ONLY session cannot authorize another lineage;
3. manually constructed `TECHNICALLY_DENIED` session is NOT verified without
   project-issued evidence (forged evidence also rejected);
4. authoritative API has no caller-controlled multiplicity/PRIMARY lock booleans
   (`inspect.signature` assertion);
5. wave/profile identity mismatch -> DENY / lock fail;
6. manifest tested set != registry/binding set -> wave cannot lock;
7. empty tested denominator -> wave cannot lock;
8. exact registered binding (experiment + family/claim + PRIMARY + scope/search +
   source session/bundle + wave + TEST_ONLY profile) -> only synthetic
   DEVELOPMENT passes;
9. first granted outcome marks the wave outcome-start durably (with explicit
   TEST_ONLY first-look audit);
10. a second different outcome cannot overwrite the first;
11. the synthetic SOURCE_ONLY claim runner cannot access protected-period project
    market outcomes (DENY + audit) and holds no market/outcome surfaces;
12. legacy `FinalUnseenFirewall` compatibility remains green;
13. VALIDATION remains DENIED;
14. historical final remains DENIED;
15. Shadow/Forward remains DENIED.

E-5 cross-binding regressions (E-5 tests 1-8):
- PRIMARY identity mismatch -> wave lock fails;
- scope identity mismatch -> wave lock fails;
- parameter/search identity mismatch -> wave lock fails;
- binding set missing a tested hypothesis -> manifest construction fails;
- manifest with an extra hypothesis binding -> construction fails;
- duplicate hypothesis binding -> construction fails;
- exact PRIMARY + scope + search binding -> lock succeeds and
  `PRIMARY_SCOPE_SEARCH_IDENTITIES` is locked;
- malformed/adversarial direct registration (wave/profile/counting-unit match but
  PRIMARY mismatch) -> cannot lock, and candidate outcome access is impossible.

Canonical suite: `python -m unittest discover -s tests -v`
Result: 235 tests OK (3 skipped), including the pre-existing suite unchanged
(no regression).

## 11. Known limitations

- `CommonStatisticalProfile` is an identity/lock interface only; the real numeric
  standard is not designed here (by design).
- The legacy runner/portfolio paths can still execute non-outcome engine-sanity /
  dummy-fixture runs on DEVELOPMENT/VALIDATION; those are not candidate-outcome
  authorization and cannot inform candidate quality.
- External model latent memory is a disclosed residual threat-model risk and is
  not claimed to be eliminated by SOURCE_ONLY technical controls.
- `open_verified_session`'s evidence is project-issued by construction; it is a
  technical-deny-verification mechanism, not a claim of cryptographic unforgeability.

## 12. Still NOT implemented

- Real `COMMON_STATISTICAL_PROFILE_V1` numeric standard (confidence method,
  minimum-event numbers, multiplicity correction, dependence thresholds);
- a separate explicit validation authority;
- a separate final-holdout unlock authority (deliberately absent);
- Shadow/Forward activation;
- full validation CAT1/CAT2/CAT3 revision event flow (explicit evidence/revision
  events only, by design);
- real Human Playbook claim extraction / candidate PnL.

## 13. Candidate performance backtest status

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

Exact reason it remains locked: the pre-outcome firewall is implemented,
identity-bound, and fail-closed, but the real `COMMON_STATISTICAL_PROFILE_V1` is
not yet designed, independently reviewed, or locked. Only `TEST_ONLY` profiles
exist, so no real-candidate outcome-bearing access can pass the gate
(`TEST_ONLY_PROFILE_REQUIRES_SYNTHETIC_FIXTURE`), and no candidate PnL / equity /
expectancy / Sharpe / win-loss inspection is possible through the authoritative
path. VALIDATION and the historical final holdout remain locked.

Next step:

```text
COMMON_STATISTICAL_PROFILE_V1_DESIGN_AND_INDEPENDENT_REVIEW
```

`REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED` may be recorded in `CURRENT_STATE.md`
only after the bounded SOURCE_ONLY claim-extraction runner/context is demonstrated
and accepted. This package implemented and unit-verified that runner with
synthetic fixtures only; it performed no real claim extraction and no real
candidate outcome backtest.
