# PLAYBOOK_CONTRACT_CORE_V0_1

> Version: 0.1
> Date: 2026-08-19
> Status: ARCHITECTURE_ADDENDUM / GENERIC_ENGINEERING (Lane B of the 2026-08-19 parallel work package)
> Scope: deterministic generic Playbook Contract representation + fail-closed validation + StrategyCatalog bridge
> Parent: `ARCHITECTURE_BASELINE.md` (Skeleton v1.0 — not redesigned)

## 1. Purpose

The Architecture Baseline requires a strategy to follow a **Playbook Contract**
rather than a custom programming language. The frozen Research Protocol v1.0
requires the transition:

```text
SOURCE CLAIM
!=
PROJECT / AI INTERPRETATION
!=
MACHINE OPERATIONALIZATION
```

This addendum defines the smallest deterministic **generic** Playbook Contract
core needed for that transition. It is deliberately independent of any specific
human-source playbook (for example the Raschke NR7 family) and of whether that
family ever passes semantic completion.

## 2. Three mandatory layers

A `PlaybookContract` always keeps the three layers separate:

| Layer | Representation | Authority |
| --- | --- | --- |
| SOURCE CLAIM | `SourceClaimRef` collection + contract-level source bundle / SOURCE_ONLY session | Claim Schema v1.0 |
| PROJECT INTERPRETATION | `InterpretationBranch` collection with per-branch source basis and transfer status | Protocol v1.0 §1–§2 |
| MACHINE OPERATIONALIZATION | `MachineOperationalization` reference (code hash, environment hash, feature versions, parameter identities) | Strategy Identity requirements |

The canonical contract identity composes all three layers. A change in any layer
changes the contract identity (immutable version identity).

## 3. Contract capabilities

The representation supports, at minimum:

- contract version (`schema_version`, `contract_version`);
- research lineage identity (`research_lineage_id`);
- family identity (`family_id`);
- source IDs / claim IDs (`source_claims[*].source_id`, `.claim_id`);
- source bundle identity/hash and SOURCE_ONLY session identity (contract level);
- source claim status (`claim_status` = EXPLICIT / INFERRED / UNKNOWN);
- explicit interpretation branch identity (`branch_id`, `branch_identity`);
- source basis for each interpretation (`source_claim_ids`, `source_basis`);
- unresolved ambiguity (`ambiguity_status`, `ambiguity_notes`);
- required observation surfaces (`ObservationSurface.required`);
- observability status (`ObservabilityStatus` per surface);
- unavailable inputs (`unavailable_inputs`);
- instrument/source scope (`instrument_scope`, `source_scope`);
- project transfer status (`project_transfer_status` = EXPLICIT / INFERRED / UNKNOWN);
- timeframe/session scope (`timeframe_scope`);
- machine operationalization reference (`machine.operationalization_reference`);
- implementation/code hash (`machine.code_hash`);
- required feature versions (`machine.required_feature_versions`);
- parameter identities (`machine.parameter_identities`);
- data exposure history reference (`data_exposure_history_reference`);
- parent/version lineage (`parent_contract_id`);
- deterministic canonical identity/hash (`contract_identity`).

## 4. Fail-closed validation

`validate_contract` marks a contract `NOT_MACHINE_READY` (with a deterministic
blocker list) when any of the following hold. Validation enforces existing
frozen authority mechanically; it makes no research decisions:

```text
SOURCE_REFERENCES_MISSING                  source claims / bundle / session missing
INTERPRETATION_PROVENANCE_MISSING          no interpretations or no source basis
INTERPRETATION_REFERENCES_UNKNOWN_SOURCE_CLAIM   branch cites a claim not in source_claims
UNRESOLVED_CRITICAL_AMBIGUITY              ambiguity stops instead of mining alternatives
REQUIRED_INPUT_NOT_OBSERVABLE              required surface NOT_OBSERVABLE/UNKNOWN, or listed unavailable
SOURCE_VARIANTS_SILENTLY_COLLAPSED         source-permitted variants not all represented
SOURCE_VARIANTS_INVENTED                   variant not permitted by the source
MULTIPLE_PRIMARY_SELECTED                  > 1 PRIMARY selected
PRIMARY_MISSING                            PRIMARY required but none selected
MACHINE_OPERATIONALIZATION_MISSING         no machine layer
MACHINE_IDENTITIES_MISSING                 code/feature/environment/parameter identities absent
SCOPE_MISSING                              instrument or timeframe scope empty
INFERRED_TRANSFER_MISLABELED_EXPLICIT      overall EXPLICIT but a branch is INFERRED/UNKNOWN
```

Only when no blocker exists is the contract `MACHINE_READY`.

## 5. Strategy Catalog bridge

`bridge_to_strategy_identity` maps a machine-ready contract onto the existing
`StrategyIdentity` model (`src/strategy_evidence.py`):

- it requires explicit machine-ready inputs (`code_hash`, `environment_hash`,
  `parameters`, `required_feature_versions`, `data_exposure_history_reference`);
- every supplied input must match the contract's machine layer;
- `strategy_version` is derived from the contract version and the contract's
  canonical identity, so any semantic content change produces a new strategy
  version/identity;
- the bridge **never registers** into a `StrategyCatalog` and **never grants**
  candidate outcome access. Registration is an explicit caller action and
  `ResearchFirewall` remains the sole outcome-access owner.

## 6. Boundaries

- Generic by design; no candidate-specific data or semantics.
- No replacement for `StrategyIdentity`, `StrategyCatalog`, `ExperimentIdentity`,
  `EvidenceLedger`, `ResearchFirewall`, or the canonical/hash identity patterns.
- The module does not import `src.research_firewall.py`.
- No candidate market outcomes, backtests, PnL inspection, or statistical gates.
