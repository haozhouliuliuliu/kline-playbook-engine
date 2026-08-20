# COMMON_STATISTICAL_PROFILE_ROUTE_A_D_OWNER_APPROVAL_2026-08-21

> Date: 2026-08-21
> Status: OWNER_RATIFIED / ADOPTED / BINDING
> Work package: `COMMON_STATISTICAL_PROFILE_ROUTE_A_D_OWNER_RATIFICATION_V0_1`
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Official main base: `e87315dd622689eb165dbe81f1728c868cc06a26`
> Decision package: `preoutcome/stat-profile-owner-decision-v01` @ `768bb8c` (`docs/reviews/COMMON_STATISTICAL_PROFILE_OWNER_DECISION_PACKAGE_V0_1.md`)
> Owner decision: explicit approval of the recommended route on 2026-08-21 (binding)
> Adopted policy artifact: `docs/research/HUMAN_PLAYBOOK_STATISTICAL_ACCEPTANCE_ROUTE_POLICY_V1_0.md`
> Machine-readable policy: `src/statistical_acceptance_policy.py`

The Owner explicitly approved the project-brain recommendation `ROUTE_A_NOW +
ROUTE_D_FORWARD` on 2026-08-21. This is the formal adoption record of the Common
Statistical Profile acceptance route. This approval is **binding** for subsequent
implementation: workers may implement this route but may not substitute an
alternative statistical acceptance route without a new Owner decision.

## Adopted decision

```text
STATISTICAL_ACCEPTANCE_ROUTE=ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD
HISTORICAL_CHRONOLOGY=KEEP_FROZEN_12_6_6
STRONG_FWER=KEEP
HISTORICAL_GENERAL_DOMAIN_POSITIVE_PASS=NOT_REQUIRED_NOT_CLAIMED
HISTORICAL_ALLOWED_DISPOSITIONS=FAIL / INSUFFICIENT_EVIDENCE / GOVERNED_DIAGNOSTICS
POSITIVE_ACCEPTANCE_PATH=FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD
ROUTE_E=FORBIDDEN
OUTCOME_CALIBRATED_THRESHOLDS=FORBIDDEN
PROTOCOL_VERSION_CHANGE_REQUIRED=NO
NEW_HISTORICAL_DATA_REQUIRED=NO
```

## Binding effect

- Research Protocol v1.0 and the frozen 12/6/6 chronology remain **unchanged**.
- Historical v1 no longer promises a general-domain positive-PASS inference; the
  honest unresolved disposition on the historical path remains
  `INSUFFICIENT_EVIDENCE`.
- The historical 12/6/6 split keeps its governed roles: negative evidence,
  `FAIL`, `INSUFFICIENT_EVIDENCE`, governed diagnostics, and the
  procedural-integrity exam. It is **not** a general-domain acceptance gate.
- The statistical positive-acceptance path is designated as future genuinely-unseen
  prospective Shadow/Forward evidence. A defensible strong-FWER PASS is only
  achievable on such forward evidence.
- The strong-FWER acceptance target is **not** lowered.
- Route E (weakening strong-FWER) and outcome-calibrated thresholds are forbidden.
- No protocol version bump and no new historical data are required for this route.

## What this approval does NOT mean

This approval does **not** authorize:

```text
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
REAL_MONEY=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
```

In particular, "positive acceptance moved to future Shadow/Forward" is **not** an
authorization of Shadow now. Shadow remains a later, separately authorized gate.
This approval is not a candidate-outcome backtest authorization, unlocks no
validation, unlocks no historical final holdout, and does not permit any outcome
tuning. It is not a lock of any real (non-TEST_ONLY) statistical profile as a
positive-PASS basis.

## Relationship to prior evidence

- This approval **does not** rewrite or re-flag the old rejected `PROFILE_0_4`
  candidate. That candidate remains rejected / not lockable as a positive-PASS
  basis.
- This approval **supersedes the parking language only in scope**: the
  `STATISTICAL_POSITIVE_ACCEPTANCE_PACKAGE=PARKED` state is replaced by the
  designated Route D forward path. Frozen Protocol v1.0, the 12/6/6 chronology,
  the IE-only evidence policy, and all access locks remain intact.

## Non-decisions / unchanged access state

```text
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
STRONG_FWER_ACCEPTANCE_TARGET=UNCHANGED
```
