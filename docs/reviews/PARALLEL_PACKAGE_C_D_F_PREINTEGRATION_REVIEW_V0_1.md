# PARALLEL_PACKAGE_C_D_F_PREINTEGRATION_REVIEW_V0_1

> Date: 2026-08-20
> Role: project-brain integration review
> Baseline: `e8ccab103a43c464aef6cc02f9566083e7acd922`
> Candidate outcomes: NOT_AUTHORIZED

## Verdict

```text
PACKAGE_C_DIRECTION=ACCEPTED
PACKAGE_C_INTEGRATION=BLOCKED_PENDING_BOUNDED_CORRECTION
PACKAGE_D_DIRECTION=ACCEPTED
PACKAGE_D_INTEGRATION=BLOCKED_PENDING_BOUNDED_CORRECTION
PACKAGE_F_DIRECTION=ACCEPTED
PACKAGE_F_INTEGRATION=BLOCKED_PENDING_BOUNDED_CORRECTION
POST_PARALLEL_COMBINED_REGRESSION=NOT_YET_RUN
```

All three workers stayed on isolated branches from the same baseline and each branch is ahead by one / behind by zero. The broad repair direction is correct, but cross-layer review found additional concrete integration gaps. These are bounded corrections, not redesigns.

## Package C blockers

### C-C01 — ResearchFirewall can register a NOT_MACHINE_READY contract

Package C correctly hardens `validate_contract()` for claim-level PRIMARY, partial observability, UNKNOWN project transfer, and multiple timeframes. However `ResearchFirewall.register_outcome_test()` does not require `validate_contract(contract).ready` before registration. A caller can manually construct a `StrategyIdentity` carrying `playbook_contract_identity=contract.contract_identity` and bypass the bridge, allowing a contract that Package C itself marks `NOT_MACHINE_READY` to be registered.

Required invariant:

```text
OUTCOME_REGISTRATION_REQUIRES_MACHINE_READY_PLAYBOOK_CONTRACT=YES
```

The check must occur before any registration/governance mutation.

### C-C02 — duplicate source claim IDs undermine claim-level PRIMARY

Package C resolves PRIMARY by `claim_id`, but `PlaybookContract` does not reject duplicate `SourceClaimRef.claim_id` values. Two distinct source records sharing one claim id can collapse onto one branch/PRIMARY and `primary_selection_identity` de-duplicates ids with a set.

Required invariant:

```text
SOURCE_CLAIM_IDS_UNIQUE_FOR_PRIMARY_RESOLUTION=YES
```

Fail closed on duplicate claim ids; do not invent fuzzy source-claim equivalence.

### C-C03 — manually constructed StrategyIdentity can still self-attest contract bridge semantics

`strategy.playbook_contract_identity == contract.contract_identity` alone does not prove the StrategyIdentity is the deterministic bridge output. Before outcome registration, exact machine/scope facts must match the actual machine-ready contract:

- applicable instruments == canonical contract instrument scope;
- timeframe == the single contract timeframe;
- code hash == contract machine code hash;
- environment hash == contract machine environment hash;
- required feature versions == contract machine feature versions;
- typed parameter identities == contract machine parameter identities;
- data exposure history reference == contract data exposure history reference;
- strategy source == contract source scope (or existing deterministic bridge fallback);
- strategy version == the deterministic bridge version currently produced by `bridge_to_strategy_identity`.

Use one small shared validator/helper rather than duplicating a second bridge implementation.

Required invariant:

```text
OUTCOME_REGISTRATION_REQUIRES_STRATEGY_EQUIVALENT_TO_PLAYBOOK_BRIDGE=YES
```

## Package D blockers

### D-C01 — OFFICIAL_PARTIAL source is re-promoted to VERIFIED_OFFICIAL downstream

Package D correctly classifies session schedules / contract specs lacking historical byte hashes as `OFFICIAL_PARTIAL`, but `tools/build_canonical_dataset.py::build_contract_configs()` still creates `ContractMetadataFact(... evidence_classification="VERIFIED_OFFICIAL")`. `ContractMetadataFact` currently only permits `VERIFIED_OFFICIAL` or `PILOT_FIXTURE` and does not require an artifact hash for the verified-official state.

This recreates the provenance overclaim one layer downstream.

Required invariants:

```text
OFFICIAL_PARTIAL_NEVER_REPROMOTED_TO_VERIFIED_OFFICIAL=YES
VERIFIED_OFFICIAL_REQUIRES_EXACT_SOURCE_ARTIFACT_HASH=YES
```

Extend the existing small classification surface; do not create a new metadata framework.

### D-C02 — ANOMALY partitions can still enter canonical storage

Package D now marks truncated/missing coverage as non-PASS `ANOMALY:*`, but the canonical normalize path iterates all manifest partitions and `normalize_and_store_partition()` itself does not require `quality_status == "PASS"` before Parquet/catalog materialization.

Thus detection and storage admission are not yet connected.

Required invariant:

```text
CANONICAL_STORAGE_ACCEPTS_PASS_PARTITIONS_ONLY=YES
```

Enforce at the reusable storage boundary (`normalize_and_store_partition`) so an alternate caller cannot bypass it; CLI filtering may be added only as an ergonomic secondary check.

### D-C03 — legacy accepted manifest compatibility must fail clearly, not ambiguously

The new content-derived SessionMetadata identity intentionally changes future data-version/session identities. Existing accepted historical manifests were produced under the old schedule-label identity and are not silently compatible. Do not rewrite them. Add a clear fail-closed diagnostic/regression establishing that a legacy partition/session identity mismatch requires explicit revalidation/rebuild, rather than being interpreted as data corruption or automatically migrated.

Required invariant:

```text
LEGACY_SESSION_IDENTITY_MISMATCH=EXPLICIT_REVALIDATION_REQUIRED
```

No corpus rebuild in this correction.

## Package F blockers

### F-C01 — material-bound bundle identity is not connected to SOURCE_ONLY session binding

Package F adds material-bound `ApprovedSourceBundle.bundle_identity`, but `SourceOnlyClaimExtractionContext.verified` still compares the session against `source_bundle.source_bundle_id` and caller-supplied `source_bundle_hash`. Therefore changing exact source bytes changes `bundle_identity` but does not necessarily invalidate the verified SOURCE_ONLY session binding.

Required invariant:

```text
SOURCE_ONLY_SESSION_BINDS_MATERIAL_BOUND_BUNDLE_IDENTITY_AND_HASH=YES
```

Future session binding must use material-derived bundle binding facts. Historical recorded id/hash remain historical metadata only and must not be upgraded into byte proof.

### F-C02 — source_bundle_hash remains caller authority for future exact bundles

The ordinary bundle object still accepts an arbitrary `source_bundle_hash`; the material-bound `bundle_identity` is separate. Add the smallest deterministic material-bound bundle hash/binding hash derived from canonical material refs (and stable bundle metadata). Exact material byte changes must change both the identity used for session binding and the hash used for session binding.

Do not remove the historical recorded bundle hash; rename/separate its semantics if needed so legacy evidence remains representable without pretending it is a byte-bound hash.

Required invariant:

```text
FUTURE_BUNDLE_SESSION_HASH_DERIVED_FROM_APPROVED_MATERIAL_REFS=YES
```

### F-C03 — ClaimRecordDraft claim_status remains unconstrained

The bounded draft now includes `material_id`, but `claim_status` accepts any non-empty string even though Claim Schema v1.0 explicitly limits it to `EXPLICIT | INFERRED | UNKNOWN`.

Required invariant:

```text
CLAIM_RECORD_DRAFT_STATUS_SCHEMA_ENFORCED=YES
```

Keep the change small; an enum is optional, a direct value check is sufficient.

## Accepted direction pending corrections

Package C:
- claim-level PRIMARY derivation;
- canonical PRIMARY selection identity;
- PARTIALLY_OBSERVABLE required input blocking;
- UNKNOWN transfer blocking;
- single-timeframe machine readiness.

Package D:
- full returned coverage required for PASS;
- zero-bar session completeness detection;
- RawArtifact identity propagation;
- nullable volume preservation;
- content-derived SessionMetadata identity;
- explicit byte provenance classification;
- mixed-partition rejection;
- runtime-version diagnostic.

Package F:
- forward-only exact-byte material refs;
- explicit historical unbound state;
- source_id/material_id separation;
- historical verification clarification;
- no historical refetch/rewriting.

## Integration rule

The three correction branches may continue in parallel. Do not merge any of them to `main` yet. After all corrections return:

1. project-brain reviews each corrected branch;
2. integrate C, D, F through the sole main integration lane;
3. because C and F both modify `src/research_firewall.py`, run a post-merge cross-package audit of SOURCE_ONLY + outcome-registration interfaces;
4. run one combined full regression after all accepted C/D/F changes are present together;
5. only then advance to Package E / later lanes.
