# FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20

> Date: 2026-08-20
> Role: project-brain / full-project second-pass adversarial audit
> Status: COMPLETE_FINDINGS_ONLY / NO_REPAIR_PACKAGE_AUTHORIZED_BY_THIS_DOCUMENT
> Scope: repository foundations through latest parallel lanes F/G/H
> Outcome access: NONE

## 1. Audit mandate

This audit was initiated after repeated parallel work exposed cross-lane defects that were not visible in isolated branch tests. The audit deliberately continued after finding the first defects and traced project authority and code from the data/metadata substrate through strategy identity, Playbook Contract, firewall, validation/execution, source research, round-trip evidence, and the unmerged F/G/H branches.

This document records findings only. It does not create a repair design, worker prompt, new research direction, new statistical method, candidate outcome authorization, validation unlock, or final-holdout unlock.

Important interpretation boundary:

```text
ENFORCEMENT_GAP_FOUND != PROOF_THAT_PROTECTED_OUTCOME_WAS_ACCESSED
DATA_COMPLETENESS_PROOF_GAP_FOUND != PROOF_THAT_ACCEPTED_PRICE_ROWS_ARE_WRONG
EXECUTION_DEFECT_FOUND != PROOF_THAT_A_CANDIDATE_RESULT_WAS_ALREADY_CORRUPTED
```

Project-recorded candidate performance research remains not started.

## 2. Severity / finding classes

- `CRITICAL`: invalidates or materially weakens a claimed pre-outcome safety invariant, cohort isolation, identity binding, or candidate-quality execution prerequisite.
- `HIGH`: material reproducibility, provenance, execution, completeness, or research-freedom gap that must not be relied on for candidate evidence.
- `MEDIUM`: real defect/limitation with narrower blast radius or currently synthetic-only impact.
- `CONFIRMED_DEFECT`: behavior follows directly from current code/tests.
- `ENFORCEMENT_GAP`: policy exists but is not technically bound to the real artifact/path it claims to govern.
- `PROVENANCE_GAP`: identity does not uniquely/cryptographically bind the factual source or dependency chain.
- `SCOPE_LIMITATION`: current implementation cannot faithfully support the broader use implied by project status language.

## 3. Executive verdict

```text
SECOND_PASS_AUDIT=COMPLETE_FINDINGS_ONLY
PREVIOUS_PREOUTCOME_FIREWALL_COMPLETE_VERIFIED_CLAIM=OVERSTATED
PREVIOUS_SOURCE_ONLY_PROJECT_ISSUED_UNFORGEABLE_CLAIM=FALSE_AS_IMPLEMENTED
VALIDATION_RUNNER_PREOUTCOME_GATE_CONNECTION=ABSENT
VALIDATION_DEFAULT_LOCK_AT_REAL_RUNNER=FALSE
CANONICAL_INTRADAY_COMPLETENESS_PROOF=INCOMPLETE
PLAYBOOK_CONTRACT_PROTOCOL_EQUIVALENCE=INCOMPLETE
REAL_CANDIDATE_MACHINE_READY_PLAYBOOK=NO
F_G_H_INTEGRATION=REMAINS_BLOCKED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY_DESPITE_LEGACY_RUNNER_BYPASS
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
NO_PROJECT_RECORDED_CANDIDATE_OUTCOME_EXPOSURE_FOUND=YES
```

The dominant finding is not one isolated bug. Several earlier modules were locally self-consistent but were never strongly cross-bound to the next module. The recurring failure mode is:

```text
identity/status label exists
-> local tests prove internal consistency
-> downstream accepts the label/string
-> no proof binds the label to the actual source/data/code/cohort/artifact
```

This pattern propagated into later F/G/H work.

---

# Part A — Research firewall / cohort / exposure

## F-01 — CRITICAL / CONFIRMED_DEFECT
### Validation runner bypasses the authoritative candidate pre-outcome gate

`ChronologicalValidationRunner` still consumes `FinalUnseenFirewall` coarse access records (`DATASET_ACCESS_GRANTED`) and, when no explicit access record is supplied, directly calls the legacy access path. It does not call `ResearchFirewall.request_candidate_outcome_access()` and does not accept its `PRE_OUTCOME_GATE_GRANTED` record as the authoritative candidate grant.

The current test suite explicitly asserts that `DatasetClass.VALIDATION` can produce `VALIDATION_CONFIRMED` through this legacy path without validation authority.

Therefore the repository statement that the single pre-outcome gate is technically enforced at candidate execution is false for the real validation-runner entry point.

Propagation:

```text
legacy coarse grant
-> ChronologicalValidationRunner
-> VALIDATION_CONFIRMED / execution outcomes
-> capital transitions / portfolio path
```

No evidence was found that this bypass has been used on a real candidate. It is nevertheless a critical dormant path.

## F-02 — CRITICAL / ENFORCEMENT_GAP
### PortfolioCoordinator repeats the same legacy-grant bypass

`PortfolioCoordinator.evaluate()` requests coarse dataset access through `FinalUnseenFirewall`, then passes that grant to `ChronologicalValidationRunner`. The portfolio path therefore inherits F-01 and can confirm VALIDATION-style execution without the identity-bound candidate gate.

## F-03 — CRITICAL / ENFORCEMENT_GAP
### Candidate firewall and validation runner are separate ResearchFirewall instances

`FinalUnseenFirewall.__init__()` constructs its own new `ResearchFirewall(ledger)`. A separately configured `ResearchFirewall` that owns SOURCE_ONLY sessions, wave locks, outcome-test registrations and profile locks is not the object owned by the runner compatibility firewall.

Thus even a perfectly configured candidate gate has no current object-level connection to the runner/portfolio compatibility path.

## F-04 — CRITICAL / ENFORCEMENT_GAP
### Cohort is caller-declared, not derived from actual accessed data

`ResearchFirewall.request_candidate_outcome_access()` accepts `cohort` as a caller-supplied enum. It does not bind cohort to actual partition dates, bar dates, canonical data identity, or a dataset slice identity.

The repository contains `classify_cohort(date)`, but the authoritative access API does not require cohort to be derived through it.

A future caller could therefore present data from one chronological cohort while asking the gate to evaluate another unless a separate data-binding layer prevents it.

## F-05 — CRITICAL / ENFORCEMENT_GAP
### ValidationInput is not bound to Experiment.data_version or canonical provenance

`ValidationInput` contains a minimal `CompletedBar`; it does not carry/verify `NormalizedHistoricalBar.data_version_id`, raw/source identity, canonical corpus identity, partition identity, or cohort slice identity.

`ExperimentIdentity.data_version` is an opaque non-empty string. The runner checks strategy/experiment labels but not that the actual bars supplied belong to the experiment's declared data version.

This breaks the intended chain:

```text
actual data artifact -> ExperimentIdentity.data_version -> execution input
```

## F-06 — CRITICAL / ENFORCEMENT_GAP
### Wave PRIMARY/scope/search identities are opaque caller strings, not derived from actual Playbook/Strategy artifacts

`WaveHypothesisBinding` and `OutcomeTestRegistration` cross-check `primary_branch_identity`, `scope_identity`, and `parameter_search_identity` against each other, but no registry proves those strings are derived from:
- the actual selected Playbook interpretation;
- actual StrategyIdentity instrument/timeframe/context scope;
- actual parameters/search ranges.

The hardening solved cross-document mismatch but not semantic artifact binding. Internally consistent bogus identity strings can still lock.

## F-07 — CRITICAL / ENFORCEMENT_GAP
### SOURCE_ONLY session/bundle is not bound to the tested Playbook/claim artifact

Outcome-test registration verifies that a SOURCE_ONLY session exists and that its bundle identity/hash matches the registration. It does not verify that:
- the bundle is the bundle referenced by the tested PlaybookContract;
- `family_claim_identity` resolves to an actual claim/family artifact;
- the tested strategy descends from that claim/bundle.

Any verified session can be internally bound to a registration unless another layer enforces the missing relationship.

## F-08 — CRITICAL / ENFORCEMENT_GAP
### Lineage/exposure inheritance can be laundered by caller-supplied lineage

The protocol says renaming never resets exposure. Code exposure tracking uses caller-supplied `research_lineage_id`. `StrategyCatalog` only checks lineage inheritance when a `parent_identity_id` is explicitly declared.

A related descendant can be constructed with a fresh lineage ID and no parent; no mechanism-signature/lineage authority technically rejects this. Exposure inheritance is therefore policy-level, not enforced against lineage omission/renaming.

## F-09 — CRITICAL / DURABILITY_GAP
### Firewall locks, exposure, wave first-look and final-holdout state are in-memory

`EvidenceLedger`, SOURCE_ONLY session registry, outcome-test registry, wave lock/outcome-start state, statistical-profile lock state and historical-final state machine are process-memory objects in the current implementation.

No durable reload/reconstruction path was found that restores these states after restart. A fresh process begins with fresh registries/LOCKED initial state.

Repository documentation uses language such as `durably declares` and irreversible exposure. That durability is not currently implemented by these classes.

## F-10 — CRITICAL / CONFIRMED_DEFECT
### SOURCE_ONLY verification evidence is reproducible/forgeable from public deterministic inputs

`SourceOnlyPolicy` uses a deterministic module-visible `_issuer_nonce` derived from a fixed string and computes verification evidence from that nonce plus the session identity. `record_session()` accepts caller-constructed sessions.

The test named “forged verification evidence” only tests the literal string `forged-evidence`; it does not construct the actual deterministic expected token.

Therefore the documented statement “only open_verified_session() can stamp evidence that is_verified accepts; forged evidence is rejected” is false as implemented. A caller with the source code can reconstruct the expected evidence for a manually constructed TECHNICALLY_DENIED session.

Additionally, the SOURCE_ONLY object boundary denies project outcome requests through that API, but it is not an OS/process sandbox around a worker that also possesses shell/repository/file access. This second point is a threat-model limitation, not evidence that any prior worker accessed protected data.

## F-11 — CRITICAL / ENFORCEMENT_GAP
### A non-TEST_ONLY arbitrary statistical profile can be treated as a real locked profile

`CommonStatisticalProfile.is_test_only` is true only for the exact marker `TEST_ONLY`. Any profile with non-empty descriptive strings and no marker is treated as non-test-only; `StatisticalProfileRegistry.lock()` only checks that it is registered.

There is no technical binding to an Owner-approved/adopted numeric profile artifact.

This is especially material because current Owner-approved policy explicitly states that no lockable positive-PASS Common Statistical Profile exists and the positive-acceptance package is parked.

## F-12 — HIGH / MULTIPLICITY_GAP
### Declared alternatives are not structurally bound to the tested denominator

`ResearchWaveManifest.declared_outcome_tested_alternatives` participates in the manifest identity but is not cross-checked against tested hypotheses/bindings. The code therefore does not prove that every declared outcome-tested alternative is represented in the permanent denominator, nor that an opaque tested hypothesis corresponds to a declared alternative.

## F-13 — HIGH / AUDIT_GAP
### Repeated identical EvidenceRecord operations are neither appendable nor idempotent

`EvidenceLedger.append()` rejects duplicate `record_id`. `EvidenceRecord` identity has no event occurrence/time/sequence nonce. Repeating the same coarse decision or same gate denial/grant with identical evidence fields can raise `duplicate evidence record` rather than producing an idempotent access result or a second auditable event.

---

# Part B — Playbook Contract / Strategy identity

## P-01 — CRITICAL / PROTOCOL_MISMATCH
### Playbook Contract enforces one PRIMARY per contract, not one PRIMARY per source-faithful claim / critical interpretation

Frozen Protocol v1.0 requires each source-faithful claim to have exactly one source-justified PRIMARY before outcome testing.

`validate_contract()` instead counts `primary_selected` across all `InterpretationBranch` objects and requires exactly one total PRIMARY for the whole contract.

A multi-component playbook can therefore theoretically select one interpretation as PRIMARY while other claim-level interpretation choices remain unselected, then pass this specific check if the caller sets contract-level ambiguity to a non-blocking state.

## P-02 — CRITICAL / SELF_ATTESTATION_GAP
### Critical ambiguity status is caller-set, not derived from field-level ambiguity

`PlaybookContract.ambiguity_status` is one contract-level enum supplied by the caller. The contract model has no mandatory field-level critical-semantic inventory from which unresolved ambiguity is derived.

`validate_contract()` trusts the enum. This weakens the claimed `AMBIGUITY_FAIL_CLOSED` guarantee.

## P-03 — HIGH / OBSERVABILITY_GAP
### PARTIALLY_OBSERVABLE required inputs do not block MACHINE_READY

Required observation surfaces block readiness only when status is `NOT_OBSERVABLE_WITH_CURRENT_DATA` or `UNKNOWN`. `PARTIALLY_OBSERVABLE` is accepted as machine-ready without a required machine-resolution record proving the observable subset is sufficient.

## P-04 — HIGH / TRANSFER_GAP
### UNKNOWN project transfer status does not block MACHINE_READY

`project_transfer_status=UNKNOWN` is not a readiness blocker. The only transfer-specific blocker is an EXPLICIT project transfer containing inferred/unknown interpretation branches.

A playbook can therefore be machine-ready while applicability transfer remains UNKNOWN.

## P-05 — HIGH / SCOPE_GAP
### Multiple timeframes can be silently represented as one StrategyIdentity timeframe string

Playbook scope only requires a non-empty `timeframe_scope`. The bridge joins all values into a comma-separated StrategyIdentity `timeframe` string. It does not require a unique PRIMARY timeframe or explicit source-permitted variant treatment.

This directly matters for Holy Grail, where operating timeframe remains unresolved.

## P-06 — HIGH / ARTIFACT_BINDING_GAP
### code_hash / environment_hash / feature versions are labels, not verified actual artifacts

`StrategyIdentity` requires non-empty strings; it does not validate cryptographic format or derive them from actual code/environment artifacts. The runner receives `artifact_identity_id` and `artifact_code_hash` from its caller and checks them against the same declared StrategyIdentity values.

Therefore the current implementation proves label consistency, not that the executed strategy code/environment is the artifact represented by those labels.

`ExperimentIdentity.data_version` has the same opaque-string problem, compounded by F-05.

---

# Part C — Canonical data / metadata / storage

## D-01 — HIGH / COMPLETENESS_PROOF_GAP
### Acquisition may mark a truncated returned coverage as PASS

`ManifestPartition` requires returned coverage to lie inside requested coverage, not to cover the full requested interval.

Normalization computes missing expected starts only for trading days represented in observed bars. DatasetBuilder quality is PASS when that missing list is empty.

Therefore a provider response containing a complete-looking subset of the requested session can be accepted as PASS without proving the full requested session/day was returned.

The accepted corpus may still be complete in fact; this finding means full intraday completeness was not fully enforced by the acceptance code.

## D-02 — HIGH / COMPLETENESS_PROOF_GAP
### Entirely absent trading days/session windows can disappear from missing-bar evidence

`normalize_tqsdk_historical_bars()` builds expected/missing checks from `observed_by_day`. If an expected day/window has no observed bar at all, it need not appear in `missing_expected_starts`.

This is the same root failure mode later reproduced in Lane G's daily/session aggregation completeness defects.

Propagation:

```text
canonical normalization completeness blind spot
-> canonical acceptance all-PASS can overstate proof
-> Lane G aggregation inherited the same observed-only pattern
```

## D-03 — HIGH / PROVENANCE_GAP
### Canonical stored raw_artifact_identity_id is populated with raw SHA, not RawArtifact.identity_id

`NormalizedHistoricalBar.raw_artifact_identity_id` refers to the `RawArtifact.identity_id`. In canonical storage construction, `CanonicalRow.raw_artifact_identity_id` is populated with `partition.raw_sha256` instead.

This is a provenance-semantic mismatch. It does not alter OHLC values but breaks the meaning of that identity link.

## D-04 — MEDIUM/HIGH / SEMANTIC_LOSS
### Missing normalized volume is silently stored as zero

Canonical storage conversion uses `0` when normalized `bar.volume is None`. That collapses “unknown/missing volume” into “known zero volume”.

The accepted TqSdk corpus likely supplies volume; no evidence was found that accepted rows were affected. The generic canonical path is nonetheless unsafe.

## D-05 — HIGH / METADATA_IDENTITY_GAP
### SessionMetadata.version does not uniquely bind actual session windows/calendar facts

`SessionMetadata` accepts a caller-provided `version` string and does not compute an identity from its actual windows.

The canonical builder sets this version to `ProductSessionSchedule.identity()`, which binds product session times/source but does not bind the concrete contract's generated windows, TradingCalendar identity, or night-closed-day set.

Downstream code frequently treats `session_metadata_version` as the session identity. This is weaker than the actual authority surface.

## D-06 — HIGH / SOURCE_PROVENANCE_GAP
### Governed metadata sources are often value-bound but not byte-bound

The metadata model supports `artifact_sha256` / `content_hash`, but canonical loaders build calendar/session/spec sources with these hashes unset (`None`). Values and URLs are committed and corpus root identity binds the modeled values, but exact retrieved official source bytes are not cryptographically pinned.

## D-07 — MEDIUM / STORAGE_API_DEFECT
### write_partition_table does not reject mixed logical partitions

The function can write rows spanning multiple hive partitions, but its returned file inventory is built only from the directory implied by the first row. Current canonical build calls it one manifest partition at a time, so accepted-build impact was not established.

## D-08 — MEDIUM / DIAGNOSTIC_DEFECT
### TqSdk runtime-version mismatch diagnostic loses the actual runtime version

The adapter resets the captured version to `None` before formatting the mismatch error. This affects diagnostics/auditability, not market values.

---

# Part D — Source research / SOURCE_ONLY evidence

## S-01 — HIGH / PROVENANCE_GAP
### Source bundle hash does not bind exact fetched source bytes

Wave 1, Wave 2 and Holy Grail manifests bind URL/title/date/selection metadata and content-note hashes, but raw HTML/PDF bytes are intentionally not retained and no fetched-content SHA256 is recorded.

A source can change at the same URL while the project's canonical source-bundle identity remains unchanged.

Copyright boundaries do not require storing full copyrighted content, but the current identity therefore does not prove the exact bytes seen by the extraction session.

Holy Grail is especially audit-sensitive because old 1993/1997/2004 material is currently hosted under 2026 site paths. No claim is made that content was altered; exact fetched edition is simply not byte-bound.

## S-02 — HIGH / SCHEMA_MISMATCH
### SOURCE_ONLY ClaimRecordDraft conflates source_id with source_bundle_id

Binding claim schema distinguishes `source_id` and `material_id`. `SourceOnlyClaimExtractionContext.record_claim()` requires `draft.source_id == source_bundle.source_bundle_id`.

The real Wave 1 driver therefore writes `source_id=bundle.source_bundle_id` to the bounded output surface, while its richer claim dictionary separately records material IDs.

The supposedly structural SOURCE_ONLY output does not faithfully enforce the canonical claim-schema meaning of `source_id`.

## S-03 — HIGH / DURABILITY_GAP
### Accepted Wave 1/Wave 2 raw evidence exists only on worker branches, not main

Main contains integration reviews that point to exact worker branches/commits. The source-bundle/session/extraction artifacts themselves are not present on main.

As long as the branches/commits remain reachable, evidence is retrievable. The main branch alone is not a self-contained durable evidence set, and branch deletion/GC would break the review's evidence path.

## S-04 — HIGH / VERIFICATION_OVERSTATEMENT
### Prior integration reviews inherited the SOURCE_ONLY verification overclaim

Wave 1/Wave 2 reviews accepted `SOURCE_ONLY_VERIFIED=YES` based on the project API/session mechanism. F-10 means this is not an unforgeable project-issued attestation. This does not show workers accessed market outcomes; it downgrades what “verified” proves.

---

# Part E — Execution / capital / portfolio / round-trip

## E-01 — HIGH / CONFIRMED_DEFECT
### ADD resets unrealized PnL to zero

When adding to an already open position, the new `CapitalSnapshot` is constructed with `unrealized_pnl=0` regardless of the existing position's mark relative to the new fill.

At the second fill price, the earlier tranche can already have unrealized gain/loss. Resetting it to zero creates another intermediate equity-path distortion distinct from TD-002.

## E-02 — HIGH / CONFIRMED_DEFECT
### Forced liquidation cannot cleanly cross to the next official trading day

Forced-liquidation execution checks the execution observation trading day against the existing snapshot `position_trading_day`. The declared liquidation rule is “next tradable observation”; a breach near session end can legitimately liquidate on the next official trading day, which this binding can reject.

The liquidation path does not perform the same today/previous bucket aging used by ordinary order processing.

## E-03 — HIGH / COST_DEFECT
### Forced liquidation omits close-today/close-previous offset fees

Forced liquidation charges the synthetic execution fee but does not apply `OffsetCostAssumptions` or resolve close-today/close-previous cost semantics. Round-trip charged costs for forced liquidation are therefore incomplete relative to the project's existing China-futures close-offset model.

## E-04 — HIGH / SCOPE_LIMITATION
### Generic CLOSE cannot split one close across today + previous buckets

If a requested generic close quantity exceeds each individual bucket but is less than/equal to their combined quantity, the runner fails rather than deterministically splitting the close across both buckets.

This is a material China-futures execution limitation not represented in the prior tech-debt register.

## E-05 — HIGH / SCOPE_LIMITATION
### Current portfolio capital assumptions cannot support heterogeneous product multipliers in one evaluation

`PortfolioRequest` uses one `CapitalMarginAssumptions.contract_multiplier`, and every resolved contract is required to match it. A single portfolio evaluation therefore cannot simultaneously represent products with different multipliers (for example ni vs au/rb/cu).

## E-06 — HIGH / REALISM_GAP
### Historical margin/fee schedule is not yet a governed candidate-quality execution authority

Canonical contract-spec evidence binds tick/multiplier/base price-limit text but the current validation model uses synthetic `initial_margin_rate`, `maintenance_margin_rate`, `synthetic_fee`, `synthetic_slippage`, and synthetic offset-fee assumptions.

This is acceptable for engine fixtures but not equivalent to historical China-futures candidate execution realism.

## E-07 — CRITICAL PRE-OUTCOME RESEARCH GAP
### Concrete-contract trading/mapping rule is not frozen

The canonical corpus intentionally stores all concrete contracts and explicitly deferred the research/main-contract selection rule. The repository has a generic `ContractMappingSchedule` type but no adopted main authority was found that freezes, for cu/al/ni/au/ag/rb, which concrete contract is traded at each point in time and exactly when rolls occur.

This is outcome-affecting search freedom and must be considered unresolved before any candidate performance access. It also affects multi-timeframe features, transaction costs, gaps and round-trip identity.

## E-08 — MEDIUM/HIGH / RESOURCE_SEMANTICS_GAP
### Add-position margin check uses available_capital rather than equity-aware resources

The add/open capacity check uses `current.available_capital` (cash minus reserved margin), which excludes unrealized PnL. This may be intentionally conservative in some states, but after TD-002 re-marking it can diverge from the project's `available_resources` equity-based property. No explicit authority was found establishing which is intended for margin admission.

## E-09 — HIGH / ROUND_TRIP_EVIDENCE_GAP
### RoundTripMaterializer silently overwrites duplicate execution outcomes by request_id

`execution_outcomes` is converted to a dictionary keyed by request ID without duplicate rejection. Multiple outcomes with the same request ID silently overwrite one another before cost cross-checking.

## E-10 — HIGH / ROUND_TRIP_IDENTITY_GAP
### Round-trip identity omits derived session-authority semantics

Round-trip `ledger_identity` binds transition/outcome references and terminal reason but not SessionMetadata identity/version or derived entry/exit day/week/active-day values. A change in session attribution authority can alter derived round-trip fields without necessarily altering the round-trip identity.

## E-11 — MEDIUM / ORDERING_GAP
### Completed round trips are ordered by position_id, not chronology

`RoundTripLedger` requires lexical position-id ordering. This is deterministic but is not trade chronology. Downstream consumers that assume ledger order is time order would be wrong.

## E-12 — MEDIUM/HIGH / OPEN-EVIDENCE_IDENTITY_GAP
### Open positions contribute only IDs to RoundTripLedger identity

For still-open positions, ledger identity contains only `open_position_ids`, not their current transition/state evidence. Material changes to an incomplete open position can leave ledger identity unchanged.

## E-13 — MEDIUM/HIGH / LIVE-STATE_FIXTURE_GAP
### Bootstrap TradingState has no cross-trading-day chronology barrier

The feasibility `TradingState` tracks sequence independently per trading day. A new day's sequence can apply while a prior day's sequence gap remains buffered; the missing prior-day event can later mutate position after future-day state has already applied.

The module is explicitly a feasibility fixture, not production. It must not be mistaken for a production-safe TradingState implementation.

---

# Part F — Latest Lane F/G/H findings and propagation

## L-01 — HIGH / CAUSALITY_GAP (Lane F)
### EMA touch interpretation does not freeze which causally available EMA is used

Lane F predeclares `bar.low <= EMA <= bar.high` but does not specify whether EMA is known before that bar begins or is computed from that bar's close.

Using a current-bar close-derived EMA to decide whether the same bar touched the EMA is a look-ahead error.

## L-02 — HIGH / CAUSALITY_GAP (Lane F)
### Holy Grail source chronology is not fully represented by “ADX rising on current context bar”

The source sequence states ADX is initially >30 and rising before the pullback, and says the pullback is usually accompanied by an ADX turndown. Lane F's one-bar rising convention can conflict with this sequence if evaluated at the touch bar.

## L-03 — HIGH / MACHINE_SEMANTICS_GAP (Lane F -> G)
### EMA and ADX algorithm semantics were not part of the interpretation freeze

Lane F does not freeze EMA seed/warmup/rounding or Wilder ADX initialization/smoothing/output rounding. Lane G independently chooses SMA-seeded EMA and 6-decimal per-step ROUND_HALF_UP, plus one exact Wilder ADX implementation.

Those choices can change EMA-touch and ADX>30 classification and are outcome-affecting machine semantics.

## L-04 — HIGH / INTRABAR_SEQUENCE_GAP (Lane F -> H)
### Touch -> entry-stop ordering can be unknowable inside the same 1-minute bar

The source says when price touches EMA, put a stop above the previous bar high. If touch and stop threshold are both reached within one minimum-resolution bar, OHLC does not identify which occurred first. Lane F did not promote this to a critical semantic/causal ambiguity.

## L-05 — HIGH / INTRABAR_RISK_GAP (Lane F -> H)
### Protective stop may trigger after fill inside the same bar

Lane F predeclares protective stop activation only on the first eligible future bar. The source says “Once filled, enter a protective stop.” If fill and protective-stop price both occur inside the same minimum-resolution bar, sequence can be unknowable. Deferring activation to the next bar silently removes a possible loss path.

## L-06 — HIGH / COMPLETENESS_DEFECT (Lane G)
### Daily aggregate can be emitted without proving all expected minute bars exist

Lane G daily aggregation groups whatever bars were supplied for a trading day and emits a daily bar. It does not compare against all expected starts/windows for that day.

## L-07 — HIGH / COMPLETENESS_DEFECT (Lane G)
### Entire absent session windows can disappear from intraday incompleteness evidence

Lane G builds intraday window groups only from windows represented by supplied bars. A session window with zero supplied bars can therefore vanish rather than produce an incomplete bucket.

This repeats D-02's earlier observed-only completeness pattern.

## L-08 — HIGH / VALIDATION_GAP (Lane G)
### Base interval and constituent durations are insufficiently cross-validated

The aggregator accepts an arbitrary base interval and timeframe interval without fully proving each `NormalizedHistoricalBar` duration matches the base interval and that requested higher timeframe is an integral compatible aggregation of the base bars/session window.

## L-09 — HIGH / PROVENANCE_GAP (Lane G)
### EMA/ADX feature identity does not bind full historical dependency chain

EMA/ADX values depend on a prefix of prior aggregate bars, but emitted feature identity binds the current source aggregate identity plus computed value and high-level spec identity, not a hash of the full dependency prefix.

If earlier evidence changes but the final numeric feature value happens to remain identical, the feature identity can remain unchanged.

## L-10 — HIGH / STREAM_BINDING_GAP (Lane G)
### Feature computation does not require one exchange/instrument stream

`_validated_aggregate_series` checks chronology, overlap, timeframe identity and session version, but not that all aggregates belong to the same exchange/concrete instrument. A chronological sequence can mix contracts and still enter EMA/ADX computation.

## L-11 — HIGH / IMPLEMENTATION_IDENTITY_GAP (Lane G)
### Feature identities do not bind actual implementation code hash

Feature identity relies on caller/version strings such as algorithm/version labels. A code change without a corresponding manual version bump can preserve the same feature identity.

## L-12 — HIGH / FAIL-CLOSED_GAP (Lane G)
### Feature functions can be called on aggregates while incomplete-bucket evidence is discarded

`compute_ema` / `compute_adx` accept only aggregate sequences, not `AggregationResult` completeness state. A downstream caller can discard `incomplete_buckets` and compute apparently valid features on the remaining aggregates.

## L-13 — HIGH / CONFIRMED_DEFECT (Lane H)
### evaluate_stop_group consumes one-shot bar iterables repeatedly

The same `bars` iterable is passed into `evaluate_stop_order()` once per order. If `bars` is a generator, the first order consumes it and later orders evaluate an empty stream.

## L-14 — HIGH / PROVENANCE_GAP (Lane H)
### Stop-trigger result identity does not bind exact source bar identities / evaluated sequence

Result identity records bar timestamps/prices and order semantics but not the `NormalizedHistoricalBar.identity_id` of the triggering bar nor the complete evaluated evidence prefix. Equivalent-looking bars from different source/data versions can produce the same trigger identity.

## L-15 — HIGH / MODEL_VERSION_GAP (Lane H)
### trigger_model_version is caller-declared but implementation is fixed

`RestingStopOrder.trigger_model_version` accepts any non-empty string while the code always executes the V0_1 algorithm. Evidence can therefore claim a model version that was not actually executed.

## L-16 — HIGH / EXECUTION_TIME_GAP (Lane H)
### Trigger bridge models intrabar stop as observed only at completed-bar availability

The bridge emits `ExecutionObservation.observed_at=available_at=bar.available_at`. A resting stop that economically triggers inside the minute is therefore represented as observed/fill-eligible only after the bar completes.

This is conservative in one sense but is not the same execution chronology as an exchange-resting stop, and it materially interacts with gap-through, protective-stop and same-bar OCO behavior.

## L-17 — HIGH / OCO_LIFECYCLE_GAP (Lane H)
### Same-bar ambiguity detection is not a complete OCO cancellation lifecycle

Lane H detects when both opposing stops trigger in the same bar. It does not cancel the sibling after an earlier unambiguous trigger. A later bar can therefore trigger the sibling too if a downstream caller treats group results as actual OCO lifecycle execution.

## L-18 — HIGH / INTEGRATION_EVIDENCE_GAP
### F/G/H branch-local green suites are not a combined regression

The reported 303 / 338 / 330 test suites were run independently on branches from the same baseline. They do not prove the combined F+G+H code behaves correctly after merge. The first adversarial audit already identified this; the second audit confirms that multiple defects exist only at cross-lane boundaries.

---

# Part G — Cross-generation propagation chains

## Chain 1 — observed-only completeness

```text
historical normalizer only checks observed days
-> canonical all-PASS completeness proof can miss completely absent coverage
-> Lane G reuses observed-window grouping
-> absent session/day can again disappear
-> EMA/ADX can be computed on a sparse but apparently complete series
```

## Chain 2 — opaque identity strings

```text
StrategyIdentity code/environment/feature labels
+ Experiment data_version label
-> Playbook machine identity labels
-> Wave PRIMARY/scope/search labels
-> Firewall checks label equality
-> validation inputs/code/data are not proven to be those labeled artifacts
```

## Chain 3 — firewall local consistency without execution-path integration

```text
ResearchFirewall internal tests green
-> documentation marks PREOUTCOME_FIREWALL complete
-> legacy FinalUnseenFirewall retained for compatibility
-> validation_runner / portfolio remain on compatibility path
-> candidate gate never becomes the real execution choke point
```

## Chain 4 — source provenance / interpretation

```text
source bundle metadata hash does not bind exact fetched bytes
+ SOURCE_ONLY verification is reproducible
+ bounded output conflates source_id/bundle_id
-> integration review accepts SOURCE_ONLY_VERIFIED
-> PlaybookContract accepts nonempty source/session labels
-> outcome registration accepts those labels without resolving to actual Playbook source artifact
```

## Chain 5 — Holy Grail causal machine semantics

```text
source says ADX initially rising -> pullback/touch EMA -> stop entry -> once filled protective stop
-> Lane F chooses partial project conventions but leaves time order underdefined
-> Lane G defines current-bar/prefix feature calculation conventions
-> Lane H defines completed-bar stop trigger conventions
-> cross-lane composition creates same-bar look-ahead / sequence / risk-suppression ambiguity
```

## Chain 6 — China-futures execution realism

```text
canonical corpus contains all concrete contracts
-> concrete-contract selection/roll intentionally deferred
+ synthetic fee/margin assumptions
+ LIMIT-001 price-limit facts incomplete
+ ordinary close/forced-liquidation bucket gaps
-> generic engine tests pass
-> candidate-quality China-futures execution still not frozen/complete
```

---

# Part H — Status corrections implied by this audit

The following prior status language must be treated as overstated until a later repair/reacceptance package exists:

```text
PREOUTCOME_FIREWALL_IMPLEMENTATION=COMPLETE_VERIFIED_ACCEPTED
SOURCE_ONLY_POLICY=VERIFIED_AS_PROJECT_ISSUED_UNFORGEABLE
PRE_OUTCOME_GATE_STATUS=VERIFIED_FAIL_CLOSED_AT_REAL_EXECUTION_PATH
PRIMARY_SCOPE_SEARCH_IDENTITIES=FULLY_ARTIFACT_BOUND
VALIDATION_ACCESS=TECHNICALLY_LOCKED_AT_VALIDATION_RUNNER
CANONICAL_INTRADAY_COMPLETENESS=FULLY_PROVEN_BY_PASS_STATUS
PLAYBOOK_CONTRACT_AMBIGUITY_FAIL_CLOSED=PROTOCOL_COMPLETE
```

Safer second-pass status is:

```text
PREOUTCOME_FIREWALL_CORE_LOGIC=IMPLEMENTED_BUT_NOT_EXECUTION_PATH_ENFORCED
SOURCE_ONLY_API_DENIAL=IMPLEMENTED
SOURCE_ONLY_PROJECT_ISSUED_ATTESTATION=NOT_SECURELY_ENFORCED
VALIDATION_POLICY=LOCKED
VALIDATION_RUNNER_TECHNICAL_LOCK=NOT_ENFORCED
CANONICAL_CORPUS_ACCEPTED_DATA_VALUES=NOT_REVOKED
CANONICAL_INTRADAY_COMPLETENESS_PROOF=REQUIRES_REAUDIT
PLAYBOOK_CONTRACT_CORE=IMPLEMENTED_BUT_PROTOCOL_BINDING_GAPS_FOUND
ROUND_TRIP_LEDGER=IMPLEMENTED_WITH_IDENTITY_AND_INPUT_VALIDATION_GAPS
F_G_H=NOT_MERGED
```

No finding in this audit authorizes inspection of candidate outcomes to diagnose these issues.

## 4. What was NOT found / not claimed

This audit did NOT find evidence that:
- a real candidate PnL/backtest was already run;
- validation/final candidate market outcomes were actually inspected by Wave 1/2/Raschke workers;
- the 15,280,452 accepted canonical OHLC rows are numerically wrong;
- cross-source comparison contains a known mismatch (recorded comparison remains 32,841 MATCH / 0 MISMATCH / 139 NOT_AVAILABLE);
- the frozen 12/6/6 chronology itself was altered;
- HUMAN_PLAYBOOK_FIRST was violated by an outcome-driven strategy-mining run.

The audit instead finds that several technical controls and completeness/provenance claims were stronger on paper than their actual cross-module enforcement.

## 5. Audit stop condition

The second-pass audit covered the current repository chain through the latest F/G/H branches and deliberately continued after defects were found. At this point the dominant unresolved classes have repeated across all major layers:

- data completeness / provenance;
- semantic identity binding;
- source attestation / lineage;
- cohort/firewall execution choke point;
- execution realism / capital lifecycle;
- latest feature/stop/playbook causal composition.

No repair design is included by mandate.

```text
SECOND_PASS_FINDINGS_RECORDED=YES
REPAIR_PROMPTS_INCLUDED=NO
OUTCOME_ACCESS_USED=NO
F_G_H_MERGED=NO
```
