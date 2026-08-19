# PLAYBOOK_CONTRACT_CORE_ENGINEERING_V0_1

> Version: 0.1 (final engineering state)
> Date: 2026-08-19
> Status: IMPLEMENTED_AND_TESTED / ENGINEERING_VERIFIED / GENERIC
> Work package: Lane B of the 2026-08-19 parallel work package — `PLAYBOOK_CONTRACT_CORE`
> Architecture addendum: `docs/architecture/PLAYBOOK_CONTRACT_CORE_V0_1.md`
> Tool decision: `USE_EXISTING` (no new tool adopted)

## 1. Frozen authority references (do not modify)

- `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `ARCHITECTURE_BASELINE.md` (Skeleton v1.0)

Frozen facts preserved unchanged: `SOURCE CLAIM != PROJECT INTERPRETATION !=
MACHINE OPERATIONALIZATION`; `EXPLICIT / INFERRED / UNKNOWN`; exactly one
source-justified PRIMARY before outcome testing; ambiguity stops instead of
mining alternatives; observability states; the 12/6/6 split; RESEARCH_WAVE
semantics; the historical-final state machine; `INSUFFICIENT_EVIDENCE`;
CAT1/CAT2/CAT3.

This is ordinary engineering implementation under Protocol v1.0 §16. It modifies
no frozen research semantics, no existing source module, and no Lane C
execution/equity logic.

## 2. Implementation owner / module

Single owner of the generic Playbook Contract core: `src/playbook_contract.py`.

Reused (not replaced) existing machinery: `StrategyIdentity`, `StrategyCatalog`,
`ExperimentIdentity`, `EvidenceLedger`, `ResearchFirewall`,
`SourceOnlySession`/`SourceOnlyPolicy`, and the canonical JSON+sha256 identity
patterns from `src/strategy_evidence.py` / `src/canonical_identity.py`.

New surface:

```text
PlaybookContract            generic contract (three mandatory layers)
SourceClaimRef              SOURCE layer claim reference (claim_identity)
InterpretationBranch        PROJECT INTERPRETATION layer (branch_identity)
ObservationSurface          required observation surface + observability
MachineOperationalization   MACHINE layer reference (machine_identity)
ClaimStatus / TransferStatus / AmbiguityStatus / ObservabilityStatus / MachineReadiness
validate_contract           fail-closed -> ContractValidationResult
bridge_to_strategy_identity explicit, fail-closed bridge to StrategyIdentity
parameter_identity          canonical identity of a TypedParameter
```

The module does not import `src.research_firewall.py`. No function grants
candidate outcome access; `ResearchFirewall` remains the sole outcome-access
owner.

## 3. Design decisions

### 3.1 Structural construction vs. semantic readiness

`PlaybookContract` construction is permissive for draft content (an empty source
claim set, an absent machine layer, empty scope, and empty code hashes are all
constructible). `validate_contract` is the single fail-closed authority that
marks `NOT_MACHINE_READY`. This mirrors the protocol: a draft is representable,
but it cannot bridge to a machine strategy until machine-ready.

### 3.2 Deterministic canonical identity

`contract_identity` uses the project's canonical JSON+sha256 scheme. Collection
fields whose ordering is not semantically meaningful (`source_claims`,
`interpretations`, `observation_surfaces`, `instrument_scope`, `timeframe_scope`,
`unavailable_inputs`) are canonicalized by sorting in the identity, so identical
semantic content in a different input order yields the same identity. PRIMARY and
variant facts are carried as explicit fields on each branch (never by position),
so order does not silently change meaning.

### 3.3 Bridge never registers / never authorizes

`bridge_to_strategy_identity` returns a `StrategyIdentity` but never calls
`StrategyCatalog.register` and never touches outcome access. Registration into a
catalog is an explicit caller action. `strategy_version` is derived from the
contract version plus the contract identity, so any semantic content change
yields a distinct version; the existing append-only `StrategyCatalog` guard then
rejects any attempt to reuse a family/version with different evidence.

## 4. Test evidence

`tests/test_playbook_contract.py` — 23 deterministic tests, synthetic generic
fixtures only (no candidate family, no candidate outcomes). Coverage:

- deterministic identity independent of input ordering;
- immutable version identity (frozen, stable hash);
- SOURCE/INTERPRETATION/MACHINE layer separation;
- missing source provenance fails closed;
- missing interpretation provenance / unresolvable source basis fails closed;
- unresolved critical ambiguity blocks readiness;
- required input NOT_OBSERVABLE / unavailable input blocks readiness;
- non-required missing surface does not block;
- multiple source-permitted variants cannot silently collapse (and invented
  variants fail closed);
- missing PRIMARY / multiple PRIMARY block;
- missing machine identities / machine operationalization block;
- missing scope blocks;
- INFERRED transfer distinguishable from EXPLICIT (mislabel fails closed);
- bridge preserves lineage/version/parameters/features;
- bridge is deterministic;
- changing contract content changes bridged strategy identity;
- bridge refuses drafts and mismatched machine inputs;
- duplicate family/version mutation rejected by existing `StrategyCatalog`;
- module cannot authorize `ResearchFirewall` access (no import, no outcome API,
  bridge performs no registration).

## 5. Verification

```text
git diff --check        -> clean
python -m unittest discover -s tests -v
  -> existing suite + 23 new playbook-contract tests all OK
```

No candidate outcome data was used; no backtest was run; no PnL was inspected;
no statistical gate was invented; no real candidate `StrategyIdentity` was
created from a live human playbook.
