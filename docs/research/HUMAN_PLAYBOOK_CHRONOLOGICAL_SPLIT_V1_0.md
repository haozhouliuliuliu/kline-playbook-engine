# HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0

> Version: 1.0
> Date: 2026-08-19
> Status: FROZEN / BINDING_CHRONOLOGY
> Owner approval: `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
> Protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Canonical corpus: 2024-01-01 .. 2025-12-31

## 1. Frozen 12 / 6 / 6 split

```text
DEVELOPMENT
2024-01-01 .. 2024-12-31

VALIDATION
2025-01-01 .. 2025-06-30

PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT
2025-07-01 .. 2025-12-31
```

The boundaries are fixed for Research Protocol v1.0.

## 2. Meaning of each cohort

### DEVELOPMENT
Permitted only after the protocol's pre-outcome gate is satisfied for candidate performance testing. Used for implementation debugging, development analysis and pre-registered exploratory work within the frozen wave/profile rules.

### VALIDATION
A protected exam cohort. Before opening validation for a family/version, the artifact/specification/metrics/scope must already be locked. Validation feedback follows CAT1/CAT2/CAT3 rules in Research Protocol v1.0.

### PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT
A one-shot project-governed historical exam cohort. It is technically protected and must remain locked until a separate final-holdout unlock authority exists.

A pass means the tested version survived a procedurally protected historical exam. It does **not** prove every human/AI was epistemically unaware of that market period, and it is not proof of timeless validity.

## 3. Prospective evidence distinction

```text
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT
!=
PROSPECTIVE_GENUINELY_UNSEEN_DATA
```

Future Shadow/Forward cohorts are the stronger genuinely prospective unseen path. They remain outside this split and require later authority before activation.

## 4. No boundary rescue

If a family has too few independent events or insufficient evidence:

```text
INSUFFICIENT_EVIDENCE
```

is the correct outcome.

Do not change these dates after viewing outcomes. Any future protocol that changes chronology requires a new research-protocol version and the normal Owner semantic gate.

## 5. Exposure rules

- protected-period source examples can create exposure independently of database access;
- family/lineage exposure is irreversible once protected outcomes are observed;
- renaming or changing version labels does not restore unseen status;
- descendants inherit relevant exposure;
- historical-final exposure never becomes unseen again, including `FINAL_VOID_IMPLEMENTATION_DEFECT` cases.

## 6. Current access state

At freeze time:

```text
DEVELOPMENT candidate outcome access = NOT_YET_AUTHORIZED until pre-outcome gate implementation/lock passes
VALIDATION access = LOCKED
HISTORICAL_FINAL_HOLDOUT access = LOCKED
PROSPECTIVE_SHADOW_FORWARD = NOT_AUTHORIZED
```
