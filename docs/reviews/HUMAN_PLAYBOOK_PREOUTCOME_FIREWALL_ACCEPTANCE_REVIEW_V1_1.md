# HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_1

> Date: 2026-08-19
> Status: PROJECT_BRAIN_ACCEPTANCE_DELTA / FIX_REQUIRED
> Reviewed implementation commit: `c6eb082b36b63c19850366a14640aa9b63a5e18a`
> Frozen authority unchanged: Research Protocol v1.0 / 12-6-6 chronology

## Verdict

`ACCEPTANCE_VERDICT=PARTIAL_FIX_REQUIRED`

The c6eb082 hardening resolves the prior acceptance gaps around caller-supplied security booleans, cross-session/profile/experiment binding, wave-denominator split-brain, project-issued SOURCE_ONLY verification, bounded SOURCE_ONLY claim-extraction context, first-look audit, and immutable terminal outcomes.

One remaining identity-binding gap blocks final engineering acceptance.

## E-5 — PRIMARY / scope / parameter-search cross-artifact binding is incomplete

`OutcomeTestRegistration` binds:
- `primary_branch_identity`;
- `scope_identity`;
- `parameter_search_identity`.

`ResearchWaveManifest` separately binds:
- `primary_branch_identities`;
- `instrument_timeframe_context_scope`;
- `parameter_search_ranges`.

However, `ResearchWaveRegistry.lock()` currently validates only:
- hypothesis registration exists;
- registration points to the same wave;
- statistical profile id/identity match;
- multiplicity counting-unit identity matches.

It does **not** validate that each registered hypothesis's PRIMARY/scope/search identity is the one frozen by the wave manifest.

`ResearchFirewall._resolve_binding()` later sets `primary_scope_search_identities_locked=True` after checking the immutable registration and wave existence/profile/counting-unit, but without a cross-artifact PRIMARY/scope/search consistency proof.

Therefore a malformed/adversarial registration may still be locked into a wave even when its PRIMARY/scope/search identity disagrees with the manifest declaration.

## Required correction

Keep one canonical immutable identity representation. Preferred minimal fix:

1. Replace the wave manifest's free-form scope/search declarations with explicit identity sets/maps that can be compared exactly to each `OutcomeTestRegistration`, or add exact identity fields alongside the human-readable descriptions.
2. At `lock_wave()` validate for every tested `hypothesis_test_id`:
   - `registration.primary_branch_identity` belongs to / exactly matches the PRIMARY identity frozen for that hypothesis;
   - `registration.scope_identity` exactly matches the frozen scope identity for that hypothesis;
   - `registration.parameter_search_identity` exactly matches the frozen search/parameter identity for that hypothesis.
3. Fail closed on extra/missing/mismatched PRIMARY/scope/search identities.
4. `_resolve_binding()` may only report `PRIMARY_SCOPE_SEARCH_IDENTITIES_LOCKED=True` after those validations are represented by a locked immutable wave/registration relationship.

Do not compare semantic meaning using fragile free-form string parsing. Bind deterministic identity/hash values.

## Required regression tests

At minimum:
- PRIMARY identity mismatch -> wave lock fails;
- scope identity mismatch -> wave lock fails;
- parameter/search identity mismatch -> wave lock fails;
- extra PRIMARY identity in manifest not represented by the tested set -> fail closed or deterministic validation rule;
- exact hypothesis-specific PRIMARY/scope/search binding -> lock succeeds;
- authoritative access remains DENIED when cross-binding is not valid.

## SOURCE_ONLY note

The bounded `SourceOnlyClaimExtractionContext` is acceptable for the current project-owned engineering boundary: it structurally exposes approved source provenance + claim output and no canonical market outcome service, while protected-outcome requests deny and audit. This review does not require cryptographic attestation or sandboxing beyond the project-owned execution boundary.

## Test evidence boundary

The implementation report states `227 OK / 3 skipped` with 46 firewall tests. Repository inspection confirms the corresponding test code exists, but this project-brain connector review did not independently execute the local Windows test suite. Final acceptance should rely on the next DS Flash run plus committed deterministic regression coverage.

## Boundaries

No frozen research semantic is changed.
No real claim extraction or candidate outcome backtest is authorized by this review.
Candidate outcome performance remains `NOT_AUTHORIZED`.

## Next action

`NEXT_ACTION=HARDEN_PRIMARY_SCOPE_SEARCH_CROSS_BINDING_THEN_REACCEPT`
