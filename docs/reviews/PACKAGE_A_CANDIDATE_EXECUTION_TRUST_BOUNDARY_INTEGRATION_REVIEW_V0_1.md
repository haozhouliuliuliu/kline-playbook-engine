# PACKAGE_A_CANDIDATE_EXECUTION_TRUST_BOUNDARY_INTEGRATION_REVIEW_V0_1

> Date: 2026-08-20
> Status: ACCEPTED_WITH_EXPLICIT_RESIDUAL_BOUNDARY
> Baseline: `ffaecde1ca24facc871a5be66e1cdb6b8c619819`
> Integrated commits: `6704b4b03eed07a72bc847b58c7dec375320e960`, `79d0d057cb694b639724ebf84bcf222edb0e5337`
> Candidate outcomes: NOT_AUTHORIZED

## Verdict

Package A is accepted and integrated. The repair is a monotonic tightening of the candidate execution trust boundary and does not authorize real candidate outcomes.

Closed in this package:

```text
F-01=ACCEPTED_FIXED
F-02=ACCEPTED_FIXED_BY_FAIL_CLOSED_PORTFOLIO_PATH
F-03=ACCEPTED_FIXED
F-04=ACCEPTED_FIXED_AT_DATE_TO_COHORT_LAYER
F-05=ACCEPTED_FIXED_AT_VALIDATION_INPUT_TO_EXPERIMENT_LABEL_LAYER
F-11=ACCEPTED_FIXED_UNDER_CURRENT_NO_REAL_PROFILE_POLICY
CALLER_SYNTHETIC_BOOLEAN_BYPASS=ACCEPTED_FIXED
```

Key accepted invariants:

- `ChronologicalValidationRunner` receives the externally configured `ResearchFirewall`; confirmatory execution no longer accepts legacy `DATASET_ACCESS_GRANTED` as candidate authorization.
- Candidate cohort is derived from actual input trading dates through the existing frozen chronology classifier; a caller does not declare the security cohort.
- `ValidationInput.data_version_id` must equal `ExperimentIdentity.data_version` before confirmatory execution.
- Non-`TEST_ONLY` statistical profiles cannot currently be locked; this implements the present project fact that no real positive-PASS profile is adopted.
- Portfolio confirmatory candidate execution is intentionally closed with `PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED` instead of inventing a new portfolio authorization design.
- Caller-supplied `synthetic_fixture` was removed from the authoritative firewall and runner APIs. TEST-only synthetic status is derived by exact equality to one production `TEST_ONLY_SYNTHETIC_DATA_VERSION` identity.

Worker evidence reports 166 focused tests and 318 full tests passing with 3 existing skips after the correction, plus `git diff --check` clean. The project-brain review independently inspected the remote commit history and production diffs before integration.

## Explicit residual boundary

Package A does **not** prove that a `data_version`, `code_hash`, environment hash, feature version, Playbook binding, lineage or SOURCE_ONLY verification label is cryptographically/structurally bound to the real artifact bytes or durable process-independent state.

In particular:

```text
REAL_DATA_BYTES_TO_DATA_VERSION_ATTESTATION=NOT_YET_ENFORCED
REAL_CODE_BYTES_TO_CODE_HASH_ATTESTATION=NOT_YET_ENFORCED
PRIMARY_SCOPE_SEARCH_TO_ACTUAL_PLAYBOOK_STRATEGY_ARTIFACT=NOT_YET_ENFORCED
SOURCE_ONLY_SESSION_TO_TESTED_PLAYBOOK_CLAIM=NOT_YET_ENFORCED
LINEAGE_RENAMING_TECHNICALLY_PREVENTED=NO
FIREWALL_STATE_DURABLE_ACROSS_RESTART=NO
SOURCE_ONLY_PROJECT_ISSUED_ATTESTATION=NOT_SECURELY_ENFORCED
```

Therefore `TEST_ONLY_SYNTHETIC_DATA_VERSION` is a governed label, not proof that supplied bars are truly synthetic. That deeper artifact-binding issue moves to Package B/P-06 and keeps real candidate outcome access unauthorized.

## Next authority

Proceed to Package B from `docs/reviews/FULL_PROJECT_SECOND_PASS_REPAIR_PLAN_V0_1.md`, targeting:

```text
F-06 F-07 F-08 F-09 F-10 F-12 F-13 P-06
```

Package B must remain bounded, fail closed on semantics that do not yet have authority, and must not change frozen Protocol v1.0 or inspect candidate outcomes.
