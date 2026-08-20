# STAT_PROFILE_ROUTE_A_D_ADOPTION_STATE_SYNC_RECOMMENDATION_V0_1

> Date: 2026-08-21
> Status: RECOMMENDATION_ONLY / NOT_APPLIED
> Branch: `preoutcome/stat-profile-route-adoption-v01`
> Formal main base: `e87315dd622689eb165dbe81f1728c868cc06a26`
> Authority: `docs/evidence/COMMON_STATISTICAL_PROFILE_ROUTE_A_D_OWNER_APPROVAL_2026-08-21.md`, `docs/research/HUMAN_PLAYBOOK_STATISTICAL_ACCEPTANCE_ROUTE_POLICY_V1_0.md`

## Purpose

This document records the recommended `CURRENT_STATE.md` synchronization for the
integration lane. This package does **not** modify `CURRENT_STATE.md` or `main`.
The integration lane applies this state-sync recommendation later under its own
integration authority.

## Recommended additions to `CURRENT_STATE.md` (integration lane scope)

```text
STATISTICAL_ACCEPTANCE_ROUTE=ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD
STATISTICAL_ACCEPTANCE_ROUTE_STATUS=OWNER_RATIFIED_BINDING
STATISTICAL_ACCEPTANCE_ROUTE_AUTHORITY=docs/evidence/COMMON_STATISTICAL_PROFILE_ROUTE_A_D_OWNER_APPROVAL_2026-08-21.md
STATISTICAL_ACCEPTANCE_ROUTE_POLICY=docs/research/HUMAN_PLAYBOOK_STATISTICAL_ACCEPTANCE_ROUTE_POLICY_V1_0.md
HISTORICAL_GENERAL_DOMAIN_POSITIVE_PASS=NOT_REQUIRED_NOT_CLAIMED
HISTORICAL_ALLOWED_DISPOSITIONS=FAIL / INSUFFICIENT_EVIDENCE / GOVERNED_DIAGNOSTICS
POSITIVE_ACCEPTANCE_PATH=FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD
ROUTE_E=FORBIDDEN
OUTCOME_CALIBRATED_THRESHOLDS=FORBIDDEN
STATISTICAL_POSITIVE_ACCEPTANCE_PACKAGE=DESIGNATED_FORWARD_NOT_PARKED
```

## Fields that must remain unchanged in `CURRENT_STATE.md`

The following existing binding lines must **not** be weakened by the sync:

```text
RESEARCH_PROTOCOL_VERSION=1.0
RESEARCH_PROTOCOL_STATUS=FROZEN_BINDING
CHRONOLOGICAL_SPLIT_STATUS=FROZEN_12_6_6
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
```

## Note for the integration lane

- The old `STATISTICAL_POSITIVE_ACCEPTANCE_PACKAGE=PARKED` line, if present, may
  be superseded by `DESIGNATED_FORWARD_NOT_PARKED` **only** in the sense that the
  forward path is now designated. It does **not** unlock Validation, historical
  final holdout, Shadow/Forward, or candidate-outcome backtest.
- No protocol version bump is required; do not change `RESEARCH_PROTOCOL_VERSION`.
- No new historical data is required; do not change the canonical corpus boundary.
- Do not back-port these lines onto `main` from this feature branch; apply them
  only as part of a normal integration-lane sync under integration authority.
