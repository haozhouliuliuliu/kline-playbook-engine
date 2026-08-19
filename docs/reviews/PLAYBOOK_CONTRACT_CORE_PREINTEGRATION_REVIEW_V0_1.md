# PLAYBOOK_CONTRACT_CORE_PREINTEGRATION_REVIEW_V0_1

> Date: 2026-08-20
> Status: ACCEPT_DIRECTION / BOUNDED_CORRECTION_REQUIRED_BEFORE_INTEGRATION
> Worker branch: `parallel/playbook-contract-core-v01`
> Worker commit: `aa3a2812ebbd6c91306763de8410d09fbac57a52`

## Verdict

The generic Playbook Contract direction is accepted: source/interpetation/machine separation, fail-closed provenance/ambiguity/observability checks, deterministic bridge to existing `StrategyIdentity`, and no outcome-access ownership in this module are all appropriate.

Two related over-constraints must be corrected before merge:

```text
ZERO_PARAMETER_STRATEGY_MUST_BE_SUPPORTED=YES
ZERO_REQUIRED_FEATURE_VERSION_STRATEGY_MUST_BE_SUPPORTED=YES
```

Reason: existing `src/strategy_evidence.py::StrategyIdentity` does not require either `parameters` or `required_feature_versions` to be non-empty. A valid fixed-rule strategy may have no tunable parameters; a strategy using only raw governed inputs may have no separately versioned derived features. The generic Playbook Contract layer must not narrow the existing Strategy Catalog domain without research/architecture authority.

Required behavior:
- `MachineOperationalization.parameter_identities=()` is valid when the bridge receives `parameters=()` exactly;
- non-empty/empty parameter identity mismatch remains fail-closed;
- `MachineOperationalization.required_feature_versions=()` is valid when the bridge receives `required_feature_versions=()` exactly;
- non-empty/empty feature-version mismatch remains fail-closed;
- `operationalization_reference`, `code_hash`, `environment_hash`, source provenance, scope, ambiguity/observability rules and data-exposure identity remain mandatory as already designed;
- no candidate outcome access is introduced.

Add synthetic regression tests for both legitimate empty-set cases and mismatch cases. Bring latest `origin/main` into the worker branch and rerun the combined suite before integration.