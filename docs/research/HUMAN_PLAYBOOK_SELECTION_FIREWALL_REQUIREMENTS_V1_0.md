# HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0

> Version: 1.0
> Date: 2026-08-19
> Status: FROZEN_SEMANTICS / IMPLEMENTATION_PENDING
> Owner approval: `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
> Protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`

## 1. Purpose

Translate the frozen Human Playbook research semantics into enforceable research-access requirements without pretending the existing code already implements them.

Current repository reality at freeze time:
- `src/strategy_evidence.py` contains an append-only evidence ledger and a `FinalUnseenFirewall` that denies `DatasetClass.FINAL_UNSEEN`;
- that existing implementation does **not** yet represent SOURCE_ONLY enforcement, research-wave locks, common-statistical-profile locks, or the new historical-holdout state semantics;
- therefore candidate outcome-bearing performance testing remains prohibited until the requirements below are implemented and verified.

## 2. Required pre-outcome gate

Before the first candidate outcome-bearing performance backtest for any wave, the system must verify all of:

```text
SOURCE_ONLY_CONTROLS = ACTIVE_AND_VERIFIED
COMMON_STATISTICAL_PROFILE = LOCKED
MULTIPLICITY_COUNTING_UNIT = LOCKED
RESEARCH_WAVE = LOCKED
PRIMARY_SCOPE_SEARCH_IDENTITIES = LOCKED
```

If any prerequisite is false/missing/unknown, access to candidate outcome-bearing performance execution must fail closed.

## 3. SOURCE_ONLY technical denial

During source claim extraction/interpretation, the implementation must prevent project retrieval/query of protected-period market outcomes.

Minimum evidence record:
- model identity/version;
- prompt/specification version;
- source-bundle identity/hash;
- tool/retrieval mode;
- protected-market access mode;
- researcher/model explicit exposure note where applicable.

A prompt instruction such as “do not look at final data” is insufficient by itself. The environment must enforce the denial or the claim-extraction session is not SOURCE_ONLY verified.

## 4. Research-wave lock

Before candidate performance testing starts, persist an immutable wave manifest binding:
- `research_wave_id`;
- protocol version;
- statistical-profile version;
- family/claim test set;
- PRIMARY branch identities;
- declared outcome-tested alternatives;
- instruments/timeframes/contexts;
- parameter/search ranges;
- multiplicity denominator/counting semantics.

After the first outcome-bearing test in that wave:
- append of new tested hypotheses to the same wave is forbidden;
- new hypotheses require a new wave/search event;
- FAIL and `INSUFFICIENT_EVIDENCE` entries remain in the permanent tested denominator.

## 5. Statistical-profile lock

Before candidate outcome-bearing performance execution, the implementation must bind an immutable statistical-profile identity that includes:
- uncertainty/precision method;
- event/evidence sufficiency procedure;
- dependence handling;
- multiplicity decision rule;
- common acceptance thresholds/procedure.

Changing an outcome-relevant profile after candidate outcome exposure creates a new profile/protocol lineage and cannot restore prior unseen status.

## 6. Historical chronology enforcement

The frozen cohorts are:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

Required behavior:
- candidate development outcome access remains denied until the single pre-outcome gate passes;
- validation is denied until family/version validation prerequisites are satisfied;
- historical final-holdout is denied until a separate explicit final-holdout unlock authority exists;
- future Shadow/Forward remains not authorized.

## 7. Exposure inheritance

The firewall/evidence layer must preserve:
- research lineage identity;
- family/mechanism identity;
- dataset/source-example exposure;
- descendant exposure inheritance;
- irreversible historical-final exposure.

Renaming family/version/strategy must not reset exposure.

## 8. Validation change classification

When validation is exposed, outcome-affecting changes must be recorded under:
- `CAT1_IMPLEMENTATION_DEFECT`;
- `CAT2_RESEARCH_LOGIC_CHANGE`;
- `CAT3_SPECIFICATION_AMBIGUITY`.

Unknown/unproven classification defaults to CAT2.

CAT1 same-validation rerun is limited to one per family/epoch and requires deterministic/independent defect-and-repair evidence.

## 9. Historical-final state machine

Implementation must support the semantic state machine:

```text
FINAL_HISTORICAL_HOLDOUT_LOCKED
-> FINAL_HISTORICAL_HOLDOUT_EXPOSED
-> FINAL_ACCEPTED | FINAL_REJECTED | FINAL_VOID_IMPLEMENTATION_DEFECT
```

`VOID` never restores holdout status.

## 10. Current implementation status

```text
SEMANTICS = FROZEN
SOURCE_ONLY_ENFORCEMENT = NOT_IMPLEMENTED
RESEARCH_WAVE_LOCK = NOT_IMPLEMENTED
STATISTICAL_PROFILE_LOCK = NOT_IMPLEMENTED
HISTORICAL_HOLDOUT_STATE_MODEL = NOT_IMPLEMENTED
PRE_OUTCOME_GATE = NOT_IMPLEMENTED
CANDIDATE_OUTCOME_BACKTEST = NOT_AUTHORIZED
```

The next engineering package must implement and test these controls before any candidate outcome-bearing performance backtest.
