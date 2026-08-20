# HUMAN_PLAYBOOK_STATISTICAL_ACCEPTANCE_ROUTE_POLICY_V1_0

> Version: 1.0
> Date: 2026-08-21
> Status: ADOPTED / OWNER_RATIFIED / BINDING
> Owner approval: `docs/evidence/COMMON_STATISTICAL_PROFILE_ROUTE_A_D_OWNER_APPROVAL_2026-08-21.md`
> Decision package: `docs/reviews/COMMON_STATISTICAL_PROFILE_OWNER_DECISION_PACKAGE_V0_1.md`
> Machine-readable record: `src/statistical_acceptance_policy.py`
> Frozen authority unchanged: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`, `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
> Related policy: `docs/research/HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0.md`

## 1. Purpose

This is the adopted project policy for the statistical acceptance route after the
Owner ratified `ROUTE_A_NOW + ROUTE_D_FORWARD` on 2026-08-21. It clarifies the
roles of the historical split and the future prospective evidence path. It
supplements but does not amend Research Protocol v1.0 or the frozen 12/6/6
chronology.

## 2. Adopted route

```text
STATISTICAL_ACCEPTANCE_ROUTE=ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD
HISTORICAL_CHRONOLOGY=KEEP_FROZEN_12_6_6
STRONG_FWER=KEEP
ROUTE_E=FORBIDDEN
OUTCOME_CALIBRATED_THRESHOLDS=FORBIDDEN
PROTOCOL_VERSION_CHANGE_REQUIRED=NO
NEW_HISTORICAL_DATA_REQUIRED=NO
```

## 3. Historical-v1 role (Route A now)

The frozen 12/6/6 historical split remains the governed historical exam structure.
It does **not** promise a general-domain positive-PASS inference.

```text
HISTORICAL_GENERAL_DOMAIN_POSITIVE_PASS=NOT_REQUIRED_NOT_CLAIMED
HISTORICAL_ALLOWED_DISPOSITIONS=FAIL / INSUFFICIENT_EVIDENCE / GOVERNED_DIAGNOSTICS
HISTORICAL_V1_DEFAULT_UNRESOLVED_DISPOSITION=INSUFFICIENT_EVIDENCE
```

The historical cohorts keep these governed roles:

- **negative evidence** — conservative-bound failure discovery; a `FAIL` is a
  missed-opportunity result, never a false acceptance;
- **`INSUFFICIENT_EVIDENCE`** — the frozen legitimate sign-unresolved result;
- **governed diagnostics** — descriptive, non-outcome diagnostics;
- **procedural-integrity exam** — anti internal-tuning / process-integrity checks.

The historical split is **not** a general-domain acceptance gate and is never
allowed to fabricate a positive `PASS`.

## 4. Future positive-acceptance path (Route D forward)

The statistical positive-acceptance path is designated as future genuinely-unseen
prospective Shadow/Forward evidence.

```text
POSITIVE_ACCEPTANCE_PATH=FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD
```

A defensible strong-FWER PASS is only achievable on genuinely-unseen forward data.
Forward evidence naturally increases power and sufficiency without changing any
historical 12/6/6 semantics. Any playbook's statistical acceptance therefore
requires forward evidence accumulation **after** Shadow activation.

## 5. Strong-FWER is not lowered

```text
STRONG_FWER_ACCEPTANCE_TARGET=UNCHANGED
```

The project does not weaken the strong-FWER acceptance target, does not use
outcome-calibrated thresholds, and does not permit Route E, in order to obtain a
positive historical PASS.

## 6. Access state after adoption

This policy unlocks no outcome-bearing access.

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
```

Designating Shadow/Forward as the future acceptance path is **not** an
authorization of Shadow now.

## 7. Anti-regression

```text
SOURCE_CLAIM != PROJECT_AI_INTERPRETATION != MACHINE_OPERATIONALIZATION
HUMAN_PLAYBOOK_FIRST=REMAINS_BINDING
DATA_FIRST_KLINE_INDICATOR_PATTERN_PARAMETER_MINING=NOT_AUTHORIZED
STRONG_FWER=KEEP
```

No result from another project may be imported as project evidence.
