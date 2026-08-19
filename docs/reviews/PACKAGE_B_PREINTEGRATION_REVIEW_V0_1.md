# PACKAGE_B_PREINTEGRATION_REVIEW_V0_1

> Date: 2026-08-20
> Role: project-brain integration review
> Worker branch: `repair/package-b-artifact-governance-v01`
> Baseline: `07b84958c96db85f7a984a1e7712be5ba37d65d0`
> Candidate outcomes: NOT_AUTHORIZED

## Verdict

```text
PACKAGE_B_DIRECTION=ACCEPTED
PACKAGE_B_INTEGRATION=BLOCKED_PENDING_ONE_BOUNDED_CORRECTION
WORKER_BRANCH_AHEAD_BY=3
WORKER_BRANCH_BEHIND_BY=0
FROZEN_PROTOCOL_CHANGED=NO
CURRENT_STATE_CHANGED_BY_WORKER=NO
```

The worker implemented the intended Package B direction and the broad regression set is useful. However, project-brain review found four concrete defects/gaps that must be corrected on the same branch before integration. These are bounded corrections, not a redesign.

## B-C01 — ArtifactBinding private-builder bypass

`ArtifactBinding` is `init=False`, but exposes classmethod `_build(artifact_kind, artifact_reference, digest, byte_size, declared_version)`. Python callers can directly call this method with an arbitrary 64-character digest, creating an `ArtifactBinding` without hashing supplied bytes. This violates the Package B invariant that the artifact digest is not caller authority.

Required invariant:

```text
NO_CALLABLE_ARTIFACTBINDING_PATH_ACCEPTS_CALLER_DIGEST=YES
```

The implementation should compute the digest only inside `from_bytes`/`from_file`. Do not replace this with a crypto/service framework.

## B-C02 — Outcome registration does not fully validate ExperimentIdentity against StrategyIdentity

`register_outcome_test()` currently checks only:

```text
experiment.strategy_identity_id == strategy.identity_id
```

but `ExperimentIdentity` contains additional strategy-derived facts (research lineage, family, strategy version, code hash, parameter hash, environment hash, feature versions). The existing `ExperimentIdentity.validate_strategy(strategy)` already performs the exact full comparison and should be used.

Without this correction, an internally inconsistent `ExperimentIdentity` can be registered and can reach the firewall grant path even though the runner later rejects it. That can still create incorrect first-look/exposure governance facts.

Required invariant:

```text
OUTCOME_REGISTRATION_REQUIRES_EXPERIMENT_VALIDATE_STRATEGY=YES
```

## B-C03 — family-claim lineage identity is sensitive to duplicate identical claims

`derive_family_claim_identity()` hashes a sorted tuple of claim evidence tuples but does not de-duplicate exact duplicates. Repeating an identical source claim changes the family-claim hash and therefore can create a new lineage root without changing the underlying source evidence.

For F-08, exact duplicate evidence must be idempotent. Derive the identity from the sorted unique set of `(source_id, source_anchor, claim_status)` tuples.

Required invariant:

```text
EXACT_DUPLICATE_SOURCE_CLAIMS_DO_NOT_CHANGE_FAMILY_CLAIM_IDENTITY=YES
```

This does not claim semantic-equivalence detection across different source evidence.

## B-C04 — feature artifact identity ordering can reject valid multi-feature bindings

`OutcomeArtifactBindings` requires feature artifacts to be ordered by unique declared version. `OutcomeTestRegistration` separately requires `feature_artifact_identities` to be lexically sorted, while `register_outcome_test()` stores identities in feature-version order. Hash lexical order is not guaranteed to equal version order, so a valid two-feature binding can fail nondeterministically based on hash ordering.

Store registration feature artifact identities in canonical lexical identity order (or remove the conflicting identity-order invariant while preserving canonical deterministic storage). Keep feature-version coverage exact.

Required invariant:

```text
VALID_MULTI_FEATURE_BINDING_NOT_DEPENDENT_ON_HASH_LEXICAL_LUCK=YES
```

## Mutation ordering note

When correcting B-C03, also ensure the `family_claim_identity -> lineage` mapping is not permanently mutated by a registration that later fails (for example duplicate hypothesis id or registration construction failure). Establish a new lineage mapping only after the registration object is valid and the outcome-test registry accepts it, or otherwise make the operation rollback-safe with the smallest implementation.

## Accepted parts pending correction

Subject to the corrections above, review accepts the direction of:

- artifact-derived PRIMARY/scope/search checks;
- Playbook ↔ Strategy contract binding;
- verified SOURCE_ONLY bundle/session binding;
- versioned JSON governance-state persistence;
- removal of fixed deterministic SOURCE_ONLY verification formula;
- alternatives == tested denominator at wave lock;
- idempotent EvidenceLedger append;
- removal of runner caller artifact self-attestation.

Package B must not broaden into Package C/D/E/F while correcting these items.

## Parallel preflight evidence

The two reproduction-only branches are accepted as preflight evidence, not production fixes:

```text
PACKAGE_D_PREFLIGHT_BRANCH=prep/package-d-canonical-reproduction-v01
PACKAGE_D_PREFLIGHT_COMMIT=8ffea4472cdd24257b612c5a9050bff9f567ec8a
PACKAGE_D_PREFLIGHT=D01_D08_REPRODUCED_PRODUCTION_UNCHANGED
PACKAGE_E_PREFLIGHT_BRANCH=prep/package-e-execution-reproduction-v01
PACKAGE_E_PREFLIGHT_COMMIT=5f77f279181fe7fe9c385017ee92f93cf4ca204c
PACKAGE_E_PREFLIGHT=E01_E05_E08_E13_REPRODUCED_PRODUCTION_UNCHANGED
```

These branches remain evidence/preparation only. Their production fixes must wait for the dependency-ordered Package D/E stages.
