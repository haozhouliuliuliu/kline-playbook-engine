# SECOND_PASS_REPAIR_RETROSPECTIVE_2_2026-08-20

> Date: 2026-08-20
> Role: project-brain independent post-correction retrospective
> Status: COMPLETE
> Baseline includes PR #14 / FGH closure guardrail
> Outcome access: NONE

## 1. Mandate

This second retrospective was intentionally performed **after** Retrospective 1's HIGH finding was corrected and merged. It did not merely re-read Retrospective 1. The review replayed the original second-pass failure chains from downstream backwards and asked whether a repaired fact could still be lost, caller-declared, re-promoted, or bypassed through a compatibility surface.

No candidate outcome, Validation outcome, historical-final outcome, Shadow/Forward outcome, PnL, Sharpe, win rate, or trade-count evidence was accessed.

## 2. Attack surfaces replayed

### 2.1 Candidate execution choke point

Reviewed `ChronologicalValidationRunner` and current `ResearchFirewall` integration.

Current confirmatory path:

```text
actual ValidationInput.data_version_id
-> exact ExperimentIdentity.data_version check
-> cohort derived from actual input trading dates
-> ResearchFirewall.request_candidate_outcome_access()
-> registered hypothesis / locked wave / locked profile / SOURCE_ONLY / PRIMARY-scope-search controls
-> execution only after grant
```

`Validation` remains default-denied; historical final and Shadow/Forward remain denied. `FAST` remains a reject-only/sanity path and cannot establish CONFIRMED validity. The portfolio confirmatory outcome path remains hard closed with `PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED` after structural validation, so the compatibility `FinalUnseenFirewall` coarse-access surface is not a portfolio candidate-outcome bypass.

Result:

```text
NEW_EXECUTION_GATE_BYPASS_FOUND=NO
```

### 2.2 Source / claim / Playbook / Strategy / experiment binding

Replayed the source-to-outcome identity chain.

Current chain includes:

- prospective source material exact bytes via `ApprovedSourceMaterialRef.from_bytes()`;
- historical missing bytes explicitly `NOT_RECORDED`, never upgraded to exact;
- material-bound `ApprovedSourceBundle.session_binding_identity/hash`;
- SOURCE_ONLY session must be project-issued in the internal issued registry;
- claim `(source_id, material_id)` and anchor are checked against approved material;
- Playbook must be `MACHINE_READY` before registration;
- Strategy must be deterministically equivalent to the Playbook bridge;
- Experiment validates the entire Strategy identity;
- code/environment/data/feature artifacts are actual byte-derived `ArtifactBinding`s;
- family-claim lineage binding survives cosmetic claim renames and duplicate source tuples;
- failed registration cannot mutate the family-claim lineage map.

Threat-model boundary remains explicit: SOURCE_ONLY is not an OS/process sandbox and local private state is not claimed tamper-proof.

Result:

```text
NEW_SOURCE_IDENTITY_LAUNDERING_FOUND=NO
NEW_CALLER_DIGEST_EXACT_BINDING_PATH_FOUND=NO
```

### 2.3 Firewall durability / multiplicity / repeated evidence

Replayed restart and repeat-operation cases.

Current firewall has a versioned JSON state schema and atomic save/load path that persists ledger exposures, SOURCE_ONLY sessions/issued identities/denials, outcome registrations, wave lock/first-look/outcomes, profile locks, final-holdout state/unlock authority, and family-claim lineage. Unknown state schema fails closed.

Research-wave declared alternatives must equal the tested denominator at lock. EvidenceLedger exact repeats are idempotent; same ID with unequal content is treated as corruption.

Local disk tamper-proofing is explicitly not claimed.

Result:

```text
NEW_RESTART_RESET_BYPASS_FOUND=NO
NEW_DENOMINATOR_LAUNDERING_FOUND=NO
```

### 2.4 Playbook readiness and semantic self-attestation

Rechecked current Playbook/Strategy enforcement against the frozen Protocol:

- PRIMARY is resolved per source claim, not once per entire contract;
- duplicate source claim IDs fail readiness and PRIMARY identity generation;
- caller `ambiguity_status=NONE/RESOLVED` cannot hide incomplete PRIMARY facts;
- `UNRESOLVED_CRITICAL` remains a blocker;
- required `PARTIALLY_OBSERVABLE` input blocks machine readiness;
- `project_transfer_status=UNKNOWN` blocks machine readiness;
- machine-ready contracts require one timeframe;
- registration re-runs Playbook readiness and bridge-equivalence checks before mutation.

Result:

```text
NEW_PLAYBOOK_SELF_ATTESTATION_BYPASS_FOUND=NO
```

### 2.5 Canonical completeness / provenance propagation

Replayed the old observed-only-completeness chain into F/G technical features.

Current production pipeline now enforces:

- PASS requires full requested returned coverage;
- expected starts come from SessionMetadata authority, including zero-bar sessions;
- canonical raw-artifact link uses `RawArtifact.identity_id` semantics;
- missing volume remains nullable rather than becoming known zero;
- SessionMetadata version is content/authority derived;
- `OFFICIAL_PARTIAL` cannot be silently promoted to `VERIFIED_OFFICIAL`;
- mixed logical partitions fail before write;
- canonical storage accepts only PASS partitions;
- old session identity mismatch requires explicit revalidation, not auto-migration;
- feature aggregation uses SessionMetadata expected starts and preserves incomplete buckets.

The historical accepted 15,280,452-row corpus was **not rebuilt or re-certified** under these repaired D-01/D-02 rules. This is intentionally preserved as a pre-candidate data revalidation prerequisite; it is not evidence that the existing OHLC rows are numerically wrong.

Result:

```text
NEW_COMPLETENESS_SILENT_PASS_FOUND=NO
ACCEPTED_CORPUS_REVALIDATION_REQUIRED_BEFORE_CANDIDATE_USE=YES
```

### 2.6 Execution / capital / portfolio / round-trip propagation

Replayed E-01..E-13 against current code and Owner-approved semantics.

The repaired engine now includes ADD re-marking, cross-trading-day forced liquidation aging, forced-liquidation offset fees, explicit bucket-child requirement for a generic close that cannot fit one bucket, per-member/per-resolved-contract capital assumptions, available-capital-only admission, duplicate outcome rejection, chronological completed-round-trip ordering, open-position evidence in ledger identity, SessionMetadata authority in round-trip identity, and the bootstrap cross-day chronology barrier.

Portfolio outcome access remains unimplemented/fail-closed.

No new structural execution defect was found in the reviewed repaired surfaces.

Result:

```text
NEW_EXECUTION_STRUCTURAL_DEFECT_FOUND=NO
```

### 2.7 F/G/H deterministic rebuild after closure correction

Replayed L-06..L-18 and the first-retrospective L-12 variant.

Current generic feature/stop machinery now binds:

- expected/actual bucket constituents and authoritative session identity;
- full feature dependency prefix;
- actual feature implementation bytes;
- one exchange/concrete-contract stream;
- process-issued aggregation completeness envelope before EMA/ADX;
- one-shot bar iterable materialization;
- stop result evaluated-prefix/source identities;
- actual trigger implementation/version;
- completed-bar chronology without exchange-resting overclaim;
- OCO cancellation and same-bar ambiguity;
- combined synthetic causal chain.

The manual `AggregationResult._from_aggregation()` clean-envelope laundering route found in Retrospective 1 is now rejected by the shared feature-input validator unless the object was actually issued by `TimeframeAggregator.aggregate()` in the current process.

Result:

```text
NEW_FGH_CAUSAL_OR_COMPLETENESS_BYPASS_FOUND=NO
```

## 3. Explicit unresolved prerequisites — not repair defects

Second retrospective deliberately distinguishes “repair is closed” from “candidate research is ready.” The following remain open and must continue to block claims they do not support.

### 3.1 E-06 historical exchange fee/margin schedule

Final bounded official-source pass concludes:

```text
E06_FINAL_JUDGMENT=PARTIALLY_BUILDABLE_WITH_GAPS
E06_EXCHANGE_LEVEL_SCHEDULE_JUDGMENT=INSUFFICIENT_EVIDENCE
E06_REMAINING_GAPS=LONG_LIVED_GOVERNED_PREREQUISITE
E06_FURTHER_REPEAT_ACQUISITION_DEFAULT=NO
```

No current-rate backfill is allowed.

### 3.2 E-07 source-governed TqSdk historical main mapping

Current evidence concludes:

```text
TQSDK_HISTORY_ACCESS=LOGIN_REQUIRED
E07_MAPPING_COMPLETENESS=INCOMPLETE
E07_RUNTIME_MAPPING_STATUS=FAIL_CLOSED_PREREQUISITE
```

The generic `ContractMappingSchedule` remains a structural/synthetic engine type; it is **not** evidence that the Owner-approved source-governed TqSdk mapping prerequisite is satisfied. No candidate-quality runtime mapping adapter exists yet. Project-authored OI/volume/calendar substitutes remain forbidden.

This is a research/data prerequisite, not an unresolved implementation bug. Candidate performance access remains locked independently and this mapping prerequisite must be satisfied in any future candidate-enablement package.

### 3.3 Holy Grail machine operationalization

Owner-approved F/G/H decisions exist, but the current Holy Grail V0.2 draft remains intentionally `NOT_MACHINE_READY`. In particular:

- trailing-stop machine definition remains not adopted until source evidence or a new Owner decision;
- base-timeframe-to-concrete-machine-interval must still be explicitly operationalized;
- ADX rising window and swing confirmation counts must be explicit/versioned/non-outcome choices when the next Playbook version is built.

The approval artifact does not retroactively rewrite the historical V0.2 draft. A later normal research package must create a new version.

### 3.4 Historical source bytes / threat model

Historical source bytes that were never hashed remain unprovable. SOURCE_ONLY remains an API/session technical-denial boundary, not an OS/process sandbox. Local state/file tamper-proofing is not claimed.

## 4. Evidence-quality note

Project brain performed code-level and artifact-level review through the GitHub connector. The connector environment does not expose a local private-repository execution surface, so project brain could not independently rerun the full Python suite after the final Codex closure correction. The bounded correction's code and regression tests were reviewed and merged; the absence of an independent project-brain rerun is recorded rather than converted into a false CI claim.

This limitation affects the strength of test-execution attestation, not the status of candidate outcome access, which remains locked.

## 5. Retrospective 2 verdict

```text
RETROSPECTIVE_2=COMPLETE
NEW_CRITICAL_FINDINGS=0
NEW_HIGH_REPAIR_FINDINGS=0
UNRESOLVED_CRITICAL_SILENT_BYPASS=0
UNRESOLVED_STRUCTURAL_IMPLEMENTATION_DEFECT_FOUND_BY_RETRO_2=0
E06_GOVERNED_PREREQUISITE=OPEN_FAIL_CLOSED
E07_GOVERNED_PREREQUISITE=OPEN_FAIL_CLOSED
CANONICAL_REVALIDATION_PREREQUISITE=OPEN_FAIL_CLOSED
HOLY_GRAIL_MACHINE_READY=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
CANDIDATE_OUTCOME_DATA_USED=NO
```

The project can proceed to the formal 62-finding closure audit. Repair-mode exit does not imply candidate-performance readiness.