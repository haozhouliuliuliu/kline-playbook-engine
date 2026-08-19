# PACKAGE_C_PLAYBOOK_PROTOCOL_DEFECT_REPRODUCTION_V0_1

> Task: `PACKAGE_C_PREFLIGHT_PLAYBOOK_PROTOCOL_REPRODUCTION_V0_1`
> Role: defect reproduction only. NOT a repair task.
> Date: 2026-08-20
> Findings authority: `docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md` (Part B)
> Reproduction script: `tools/reproduce_package_c_findings.py`
> Baseline: `origin/main` `c13ec0412986234616d648983897ce3015df2671`

```text
STATUS=PREFLIGHT_DEFECT_REPRODUCTION_COMPLETE
PRODUCTION_CODE_CHANGED=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
P01=REPRODUCED
P02=REPRODUCED
P03=REPRODUCED
P04=REPRODUCED
P05=REPRODUCED
```

Every finding below was reproduced on the real `origin/main` code with a
synthetic `PlaybookContract` lowest-level trigger. No `src/*.py` file was
modified. No frozen Protocol (`HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`), no
CURRENT_STATE, and no Holy Grail draft were modified. No Raschke outcome data
was used and no market data was read.

## Interpretation boundary (mandatory)

- **P-01 / P-02 are protocol enforcement gaps.** They prove that the current
  validator does not mechanically enforce a frozen Protocol v1.0 requirement.
  Proving an enforcement gap is **not** an authorization for any worker to
  modify the frozen Protocol, to weaken it, or to redesign the claim/ambiguity
  model on this branch. Any future repair must be a separate, authority-backed
  repair task that binds the validator to the frozen requirement (or follows an
  explicit Owner/authority decision), never a silent protocol edit in a
  reproduction lane.
- Reproducing a gap is not proof that any protected outcome was accessed. No
  candidate outcome path was exercised.
- This document records findings only; it creates no repair design.

## Reproduction method

All scenarios are synthetic and generic (no candidate family). Each finding was
reproduced by calling the most direct authoritative function on a constructed
`src.playbook_contract.PlaybookContract`:

- `validate_contract(contract)` — the fail-closed readiness authority;
- `bridge_to_strategy_identity(contract, ...)` — the StrategyIdentity bridge
  (P-05 only, and only after the contract validates machine-ready).

---

## P-01 — CRITICAL / PROTOCOL_MISMATCH — one PRIMARY per contract, not one PRIMARY per source-faithful claim

- **STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `src.playbook_contract._collect_blockers`, check 6:
  `primary_count = sum(1 for branch in contract.interpretations if branch.primary_selected)`
  with `MULTIPLE_PRIMARY_SELECTED` (>1) and `PRIMARY_MISSING` (==0, when
  `primary_required`). The count is global over the whole contract, not per
  source claim / per critical interpretation.
- **MINIMAL_TRIGGER**: synthetic contract with two source claims `c1`, `c2`;
  two interpretation branches — `b1` references `c1` with
  `primary_selected=True`; `b2` references `c2` with `primary_selected=False`;
  every other readiness fact filled (source bundle/session, machine layer,
  observability, scope) and `ambiguity_status=NONE` (non-blocking value).
- **ACTUAL_BEHAVIOR**: `validate_contract` returns `MACHINE_READY` with no
  blockers. Claim `c2` has **no** PRIMARY interpretation of its own, and this
  does not block. The validator requires exactly one PRIMARY for the *entire
  contract*, not one PRIMARY for every source-faithful claim / critical
  interpretation that needs machine interpretation.
- **FROZEN_PROTOCOL_EXPECTATION**: Protocol v1.0 §2 — *"Before any candidate
  outcome-bearing performance test, every source-faithful claim must have
  exactly one source-justified `PRIMARY_BRANCH`."* A multi-claim contract that
  leaves one claim without a PRIMARY violates this.
- **FUTURE_FIX_BOUNDARY**: a repair would need to enforce PRIMARY coverage per
  source-faithful claim (or per critical interpretation requiring machine
  interpretation), e.g. bind `primary_selected` coverage to `source_claim_ids`.
  This must be designed in a separate authority-backed repair task; no protocol
  change is authorized here.

## P-02 — CRITICAL / SELF_ATTESTATION_GAP — ambiguity_status is caller self-attestation

- **STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `src.playbook_contract._collect_blockers`, check 3:
  `if contract.ambiguity_status is AmbiguityStatus.UNRESOLVED_CRITICAL:`
  appends `UNRESOLVED_CRITICAL_AMBIGUITY`. The single contract-level enum is
  supplied by the caller and is trusted directly; no field-level
  critical-semantic inventory is consulted or required.
- **MINIMAL_TRIGGER**: two contracts identical in **every** field except
  `ambiguity_status`. Contract A: `UNRESOLVED_CRITICAL`. Contract B: `NONE`
  (obtained with `dataclasses.replace(A, ambiguity_status=NONE)`). The probe
  prints the differing fields, which is exactly `['ambiguity_status']`.
- **ACTUAL_BEHAVIOR**: A is `NOT_MACHINE_READY` with
  `UNRESOLVED_CRITICAL_AMBIGUITY`; B is `MACHINE_READY`. Flipping only the
  caller-set enum removes the blocker. The system has no field-level ambiguity
  inventory that must prove the underlying ambiguity was actually resolved;
  `ambiguity_notes` is optional and unvalidated.
- **FROZEN_PROTOCOL_EXPECTATION**: Protocol v1.0 §2 *"If source evidence alone
  cannot justify one primary interpretation: AMBIGUOUS /
  INSUFFICIENTLY_OPERATIONALIZED -> STOP"* and the fail-closed
  `AMBIGUITY_FAIL_CLOSED` claim. An unresolved critical semantic choice must
  not be clearable by an unverified caller enum.
- **FUTURE_FIX_BOUNDARY**: a repair would bind the blocker to a mandatory,
  derived field-level critical-semantic inventory rather than trusting a
  contract-level enum. This document deliberately does **not** design that
  field model ("do not design the field model here"); it only proves the
  self-attestation gap.

## P-03 — HIGH / OBSERVABILITY_GAP — PARTIALLY_OBSERVABLE required inputs do not block MACHINE_READY

- **STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `src.playbook_contract._collect_blockers`, check 4:
  required surfaces block only when `observability_status` is
  `NOT_OBSERVABLE_WITH_CURRENT_DATA` or `UNKNOWN`, or when the surface id is in
  `contract.unavailable_inputs`. `PARTIALLY_OBSERVABLE` is not in the blocking
  set.
- **MINIMAL_TRIGGER**: synthetic contract with a required observation surface
  `price` set to `observability_status=PARTIALLY_OBSERVABLE` with explicit
  `missing_inputs=("order-flow",)`. Per the mandate, the surface id is **not**
  also placed into `contract.unavailable_inputs` (which would trip the separate,
  existing `REQUIRED_INPUT_NOT_OBSERVABLE` blocker and would not isolate this
  finding). All other facts machine-ready.
- **ACTUAL_BEHAVIOR**: `validate_contract` returns `MACHINE_READY` with no
  blockers. A `PARTIALLY_OBSERVABLE` required surface alone never blocks, and no
  machine-resolution record proving the observable subset is sufficient is
  required.
- **FROZEN_PROTOCOL_EXPECTATION**: Protocol v1.0 §5 — before machine
  operationalization the project must answer whether the observed input is
  available point-in-time, and a missing input must not be silently accepted;
  `PARTIALLY_OBSERVABLE` implies some required input is missing and must be
  justified before outcome testing.
- **FUTURE_FIX_BOUNDARY**: a repair would require a justified machine-resolution
  record (or fail closed) whenever a required surface is `PARTIALLY_OBSERVABLE`
  with non-empty `missing_inputs`. Repair design is out of scope here.

## P-04 — HIGH / TRANSFER_GAP — UNKNOWN project transfer status does not block MACHINE_READY

- **STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `src.playbook_contract._collect_blockers`, check 9:
  the only transfer-specific blocker is
  `INFERRED_TRANSFER_MISLABELED_EXPLICIT` — an overall `EXPLICIT` project
  transfer containing an `INFERRED`/`UNKNOWN` branch. `project_transfer_status
  = UNKNOWN` is never a blocker.
- **MINIMAL_TRIGGER**: synthetic contract with
  `project_transfer_status=TransferStatus.UNKNOWN`, branches
  `transfer_status=EXPLICIT`, and every other fact satisfying the current
  validator.
- **ACTUAL_BEHAVIOR**: `validate_contract` returns `MACHINE_READY` with no
  blockers. A playbook can be machine-ready while the applicability transfer
  from source claim to project interpretation remains `UNKNOWN`.
- **FROZEN_PROTOCOL_EXPECTATION**: Protocol v1.0 §1–§2 — transfer semantics must
  be preserved; an `UNKNOWN` transfer is a degraded provenance state that must
  not silently present as machine-operationalized readiness.
- **FUTURE_FIX_BOUNDARY**: a repair would make `UNKNOWN` project transfer a
  readiness blocker (or require an explicit resolution record) before
  `MACHINE_READY`. Repair design is out of scope here.

## P-05 — HIGH / SCOPE_GAP — multiple timeframes silently represented as one StrategyIdentity timeframe string

- **STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `src.playbook_contract._collect_blockers`, check 8
  (`SCOPE_MISSING` only when `timeframe_scope` is empty) and
  `bridge_to_strategy_identity`:
  `timeframe=",".join(sorted(contract.timeframe_scope))`.
- **MINIMAL_TRIGGER**: synthetic contract with
  `timeframe_scope=("15m", "60m")` (sorted, unique — accepted by the canonical
  tuple rule) and all other facts machine-ready; then
  `bridge_to_strategy_identity(...)` called with matching machine inputs.
- **ACTUAL_BEHAVIOR**: `validate_contract` returns `MACHINE_READY` (no unique
  PRIMARY timeframe requirement), and the bridge produces
  `StrategyIdentity.timeframe == "15m,60m"` — the two timeframes are silently
  joined into one comma-separated string.
- **FROZEN_PROTOCOL_EXPECTATION**: Protocol v1.0 §2 — before outcome testing the
  instrument/timeframe/context scope must be locked; a multi-timeframe scope
  with an unresolved operating timeframe (directly relevant to Holy Grail) must
  not be silently collapsed into a single timeframe label.
- **FUTURE_FIX_BOUNDARY**: a repair would require a unique PRIMARY timeframe (or
  explicit source-permitted variant treatment) before bridging to a single
  `StrategyIdentity.timeframe`. Repair design is out of scope here.

---

## Scope and boundaries

- No production `src/*.py` file was modified on this branch.
- No `CURRENT_STATE.md`, frozen Protocol, or Holy Grail draft was modified.
- No tests were added or changed; the diagnostic script is the deliverable and
  is not part of the default unittest suite (it exits 0 by design).
- No candidate outcome data, no Raschke outcome data, and no market data were
  read or used.
- P-06 (artifact binding gap) was not in this preflight's scope; only P-01..P-05
  were reproduced.
