# CDF_CORRECTION_REVIEW_AND_NEXT_PARALLEL_PLAN_V0_1

> Date: 2026-08-20
> Role: project-brain post-correction review and orchestration authority
> Candidate outcome access: NOT_AUTHORIZED

## Verdict

```text
PACKAGE_C_CORRECTION_REVIEW=PASS_READY_FOR_COMBINED_INTEGRATION
PACKAGE_D_CORRECTION_REVIEW=PASS_READY_FOR_COMBINED_INTEGRATION
PACKAGE_F_CORRECTION_REVIEW=PASS_READY_FOR_COMBINED_INTEGRATION
CDF_MAIN_INTEGRATION=NOT_YET
CDF_COMBINED_REGRESSION=REQUIRED
```

The three corrected branches are individually acceptable after bounded pre-integration corrections. They must now be combined in one isolated integration branch before main advances.

## Package C accepted correction invariants

```text
OUTCOME_REGISTRATION_REQUIRES_MACHINE_READY_PLAYBOOK_CONTRACT=YES
SOURCE_CLAIM_IDS_UNIQUE_FOR_PRIMARY_RESOLUTION=YES
OUTCOME_REGISTRATION_REQUIRES_STRATEGY_EQUIVALENT_TO_PLAYBOOK_BRIDGE=YES
```

`validate_strategy_against_playbook_contract()` is the shared Playbook->Strategy equivalence authority. `ResearchFirewall.register_outcome_test()` calls Playbook readiness and the shared validator before registration/governance mutation.

## Package D accepted correction invariants

```text
OFFICIAL_PARTIAL_NEVER_REPROMOTED_TO_VERIFIED_OFFICIAL=YES
VERIFIED_OFFICIAL_REQUIRES_EXACT_SOURCE_ARTIFACT_HASH=YES
CANONICAL_STORAGE_ACCEPTS_PASS_PARTITIONS_ONLY=YES
LEGACY_SESSION_IDENTITY_MISMATCH=EXPLICIT_REVALIDATION_REQUIRED
```

No canonical corpus rebuild or acceptance rewrite has occurred. Existing accepted OHLC values are not declared numerically wrong.

## Package F accepted correction invariants

```text
SOURCE_ONLY_SESSION_BINDS_MATERIAL_BOUND_BUNDLE_IDENTITY_AND_HASH=YES
FUTURE_BUNDLE_SESSION_HASH_DERIVED_FROM_APPROVED_MATERIAL_REFS=YES
CLAIM_RECORD_DRAFT_STATUS_SCHEMA_ENFORCED=YES
```

Historical recorded bundle hashes remain historical metadata, not retroactive byte proof. Historical accepted extraction artifacts remain unchanged.

## Required C/D/F integration behavior

Use a new isolated integration branch from latest main. Merge D, then C, then F. D is production-file-disjoint from the C/F shared firewall surface. C and F both modify `src/research_firewall.py` and `tests/synthetic_fixture.py`; conflicts must be resolved as a union of the already accepted semantics, not by choosing one branch over the other.

The combined tree must simultaneously preserve:

- Package C claim-level PRIMARY/readiness and Playbook->Strategy registration equivalence;
- Package F material-bound SOURCE_ONLY bundle/session/claim semantics;
- Package B artifact/lineage/durable firewall invariants;
- Package A authoritative candidate gate protections;
- Package D canonical completeness/provenance/storage admission invariants.

After merge resolution run focused cross-package tests plus the entire test suite. No branch reaches main until this combined regression is green and the project brain reviews the integrated diff.

## Parallel work now allowed

While the C/D/F integration lane runs, two additional isolated lanes are allowed.

### Lane E-Core — only unambiguous execution repairs

Production repair is allowed only for findings whose repair semantics are already determined by existing behavior/evidence and do not depend on accepted D-05 session identity:

```text
E-01,E-02,E-03,E-09,E-11,E-12,E-13
```

Do NOT repair E-04 here: generic CLOSE split allocation/fee semantics require an explicit authority decision if no existing rule resolves the split. Do NOT repair E-05 here: heterogeneous portfolio capital-assumption representation must be specified before implementation. Do NOT repair E-08 here. Do NOT repair E-10 until accepted D-05 is on the main integration path. E-13 remains explicitly bootstrap/feasibility scope.

### Lane E-Governance — authority research only

Research/documentation lane for:

```text
E-04 generic CLOSE split allocation / fee semantics
E-05 heterogeneous portfolio capital-assumption representation
E-06 historical realistic fee/margin authority
E-07 concrete-contract/main-contract mapping authority
E-08 margin-admission resource semantics
```

This lane must not choose a new outcome-affecting rule when existing authority is absent. E-04/E-05/E-07/E-08 are Owner-gated if the repository/formal external authority does not already contain a binding answer. Source acquisition follows FREE_PUBLIC_UNAUTHENTICATED_FIRST; no paid purchase/login, no candidate outcomes.

## Current three-lane orchestration

```text
LANE_1=CDF_COMBINED_INTEGRATION_AND_REGRESSION
LANE_2=PACKAGE_E_UNAMBIGUOUS_EXECUTION_REPAIRS
LANE_3=PACKAGE_E_GOVERNANCE_AUTHORITY_RESEARCH
MAX_ACTIVE_LANES=3
MAIN=SOLE_FINAL_INTEGRATION_AUTHORITY
TOOL_DECISION=USE_EXISTING
```

## Still locked

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
E04_SPLIT_RULE_CHOICE=NOT_DELEGATED_TO_WORKER
E05_PORTFOLIO_REPRESENTATION_CHOICE=NOT_DELEGATED_TO_WORKER
E08_SEMANTIC_CHOICE=NOT_DELEGATED_TO_WORKER
E07_MAPPING_RULE_CHOICE=NOT_DELEGATED_TO_WORKER
```
