# HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_0

> Date: 2026-08-19
> Status: ENGINEERING_ACCEPTANCE_REVIEW / FIX_REQUIRED / RESEARCH_SEMANTICS_UNCHANGED
> Reviewed commit: `991e4916d0080df2acb5b819e917afe31ed1221f`
> Frozen authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Firewall requirements: `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`

## Verdict

`IMPLEMENTATION_ACCEPTANCE=PARTIAL_FIX_REQUIRED`

The implementation is directionally correct and preserves the frozen research semantics, but it is not yet safe to mark the pre-outcome firewall `COMPLETE_VERIFIED` for real candidate research. The main gap is identity binding: the gate verifies that some SOURCE_ONLY session/profile/wave are locked, but it does not yet prove that the exact experiment/hypothesis being granted is the one pre-registered inside those locked artifacts.

This is an ordinary engineering correction. Research Protocol v1.0, the frozen 12/6/6 chronology, and Owner freeze evidence remain unchanged.

## Critical engineering gaps before acceptance

### E-1 — caller-supplied lock booleans are not authoritative

`ResearchFirewall.request_candidate_outcome_access()` / `evaluate_gate()` accept:
- `multiplicity_counting_unit_locked: bool`
- `primary_scope_search_identities_locked: bool`

Those are security-relevant facts supplied directly by the caller. A caller can pass `True` without any immutable registry/evidence proving the lock.

Required fix: derive all gate-critical lock state from project-owned immutable artifacts/registries. The authoritative candidate-outcome API must not accept caller assertions for frozen prerequisites.

### E-2 — requested experiment/hypothesis is not bound to the locked RESEARCH_WAVE

The gate accepts an `ExperimentIdentity`, a `wave_id`, and a `profile_id`, but does not verify that:
- the experiment/strategy/family/claim identity belongs to the wave test set;
- the PRIMARY branch/scope/search identity for this exact experiment is the one pre-registered in the wave;
- the SOURCE_ONLY session/bundle used to derive the claim is the one bound to that hypothesis lineage.

Therefore an unrelated locked wave/session can currently satisfy the gate for another experiment.

Required fix: introduce one canonical immutable outcome-test registration/hypothesis identity (or equivalent) binding the experiment, family/claim, PRIMARY branch, scope/search identity, SOURCE_ONLY session/reference, wave, and profile. Candidate outcome access must resolve and verify that binding from registries.

### E-3 — manifest test set and permanent denominator can diverge

`ResearchWaveManifest.tested_family_claim_identities` is immutable, but `ResearchWaveRegistry` initializes a separate empty denominator and populates it via `add_tested_hypothesis()`.

The registry can therefore hold:
- manifest says set A;
- denominator says set B or empty.

`lock()` does not validate consistency.

Required fix: one canonical test-set/denominator source of truth. At minimum, wave lock must verify that the permanent denominator exactly matches the pre-registered tested-hypothesis set and is non-empty. Prefer representing pre-registered hypothesis identities directly in the immutable wave manifest and deriving the denominator from them rather than maintaining a second mutable pre-lock list.

### E-4 — wave/profile version binding is not enforced

The wave manifest records `statistical_profile_version`, but the gate independently accepts `profile_id` and only checks whether that profile is locked. It does not verify the selected profile is the profile/version declared by the wave.

Required fix: bind the exact statistical-profile identity/hash (not only free-text version) into the wave or outcome-test registration and verify equality at access time.

## SOURCE_ONLY readiness clarification

`SourceOnlyPolicy` correctly rejects `PROMPT_ONLY` and provides a deny-only protected-outcome entry point. However, a `SourceOnlySession` can currently be marked `TECHNICALLY_DENIED` by construction, and no real claim-extraction runner/environment has yet been demonstrated to be constrained to SOURCE_ONLY-only data surfaces.

Therefore current acceptance wording should be:

`SOURCE_ONLY_POLICY=IMPLEMENTED_AND_UNIT_VERIFIED`

not yet:

`REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED`

Before real claim extraction starts, the project needs a bounded claim-extraction runner/session path that is structurally given source materials and SOURCE_ONLY services only, with no canonical market-outcome retrieval surface, plus a deterministic test proving protected-period market retrieval is unavailable through that runner.

This does not require a new research-semantic decision.

## Additional hardening required

- On the first granted candidate outcome access, record/declare the wave's outcome-start event through the authoritative registry so the first-look boundary is durable.
- Outcome recording should be append-only/auditable; do not allow a prior hypothesis result to be silently overwritten in place.
- Preserve legacy `FinalUnseenFirewall` compatibility, but all candidate-outcome decisions must continue to delegate to the single `ResearchFirewall` owner.

## Tests required

Add deterministic regressions proving at least:
1. unrelated locked wave cannot authorize an experiment not in its registered test set;
2. unrelated SOURCE_ONLY session/source bundle cannot authorize a hypothesis lineage it did not produce/bind;
3. caller cannot assert multiplicity/PRIMARY locks with raw booleans;
4. mismatched wave/profile identity/version denies;
5. empty or divergent manifest/denominator cannot lock;
6. exact pre-registered hypothesis/experiment/PRIMARY/scope/profile/session binding can pass only with synthetic TEST_ONLY fixtures;
7. first granted outcome marks wave outcome-start durably;
8. recorded hypothesis outcomes cannot be silently overwritten;
9. real claim-extraction runner cannot retrieve protected-period project market outcomes;
10. full canonical suite remains green.

## Acceptance boundary

Until these fixes pass:

```text
PREOUTCOME_FIREWALL_ACCEPTANCE=NOT_COMPLETE
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
REAL_CLAIM_EXTRACTION=HOLD_FOR_SOURCE_ONLY_RUNNER_BINDING
RESEARCH_PROTOCOL_V1_0=FROZEN_UNCHANGED
```

After the ordinary engineering fixes and deterministic tests pass, project brain may accept the firewall package without a new Owner gate.