# HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0

> Version: 1.0
> Date: 2026-08-19
> Status: FROZEN / BINDING_RESEARCH_PROTOCOL
> Owner approval: `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
> Binding direction: `RESEARCH_DIRECTION.md`
> Binding architecture: `ARCHITECTURE_BASELINE.md` Skeleton v1.0
> Frozen chronology: `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
> Selection-Firewall requirements: `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`

This protocol freezes the research semantics for Human Playbook First. It does not itself authorize validation/final access, Shadow/live trading, broker actions, paid commitments, or permanent RiskGate changes.

## 1. Research object and source separation

The project preserves three separate layers:

```text
SOURCE CLAIM
!=
PROJECT / AI INTERPRETATION
!=
MACHINE OPERATIONALIZATION
```

Claim provenance-of-meaning labels are:

```text
EXPLICIT
INFERRED
UNKNOWN
```

Rules:
- original/nearest-original attributable material is preferred for EXPLICIT claims;
- derivative/repost material must preserve degraded provenance and lineage;
- discovery-only records such as rankings cannot create playbook claims by themselves;
- performance/testimonial claims are not validity evidence;
- missing meaning stays UNKNOWN rather than guessed.

## 2. PRIMARY interpretation and branch identity

Before any candidate outcome-bearing performance test, every source-faithful claim must have exactly one source-justified `PRIMARY_BRANCH`.

If source evidence alone cannot justify one primary interpretation:

```text
AMBIGUOUS / INSUFFICIENTLY_OPERATIONALIZED -> STOP
```

Alternative interpretations may be preserved, but:
- an outcome-tested alternative counts as search freedom;
- an alternative cannot rescue a failed PRIMARY and still be called validation of the source claim;
- post-result additions are new descendants/search events and inherit exposure.

Every tested branch has a deterministic operationalization identity/hash over outcome-affecting logic, inputs, parameters, scope and context.

Before outcome testing, lock:
- PRIMARY branch hash;
- declared outcome-tested alternative hashes;
- instrument/timeframe/context scope;
- parameter/search ranges;
- materially relevant AI prompt/specification version.

## 3. SOURCE_ONLY interpretation environment

Historical research cannot prove that every human researcher or AI model is epistemically unaware of 2024-2025 market outcomes.

Therefore:

```text
PROJECT_GOVERNED_HISTORICAL_HOLDOUT
!=
PROSPECTIVE_GENUINELY_UNSEEN_DATA
```

During source claim extraction and interpretation:
- use a `SOURCE_ONLY` environment;
- technically deny retrieval/query of protected-period market outcomes;
- record model identity/version, prompt/spec version, tool/retrieval mode and source-bundle identity;
- explicit protected-period outcome references by a researcher/model create exposure for the affected family;
- latent/parametric prior market knowledge that cannot be proven absent is disclosed as residual threat-model risk, not certified away.

The historical holdout tests project-procedural integrity against internal tuning. Stronger genuinely prospective unseen claims require future Shadow/Forward evidence under later authority.

## 4. Lineage and exposure

Renaming never resets lineage or exposure.

Family identity binds a mechanism-level signature over outcome-affecting logic/inputs/context plus available provenance evidence.

Lineage review may use:
- explicit attribution;
- source chronology;
- unusual shared vocabulary/mechanism structure;
- parent/descendant derivation;
- shared operationalization components.

Similarity alone is not automatic proof of genealogy, but unresolved dependence cannot be counted as independent confirmation.

### Source-example exposure

Use effective content/version date, not blindly original publication date.

```text
if effective_content_date < protected_window_start
-> no example-date audit is required for that protected window
else
-> example-date exposure audit is required
```

Exposure includes chart/visual dates and outcomes, written dated examples, verbal dated outcome descriptions, and inherited derivative/repost exposure plus added-content exposure.

Unknown dates fail closed only for the affected material/family protected window. Exposure is irreversible once protected outcomes are observed.

## 5. Observability and surrogate rule

Before machine operationalization, answer:
1. what did the source actually observe?
2. is that input available point-in-time in project data?
3. is a substitute justified from source semantics/measurement logic before outcome testing?
4. if not, should the claim remain untestable?

Allowed states:

```text
OBSERVABLE_NOW
PARTIALLY_OBSERVABLE
NOT_OBSERVABLE_WITH_CURRENT_DATA
UNKNOWN
NOT_APPLICABLE
```

Missing DOM/order flow/fundamentals/news/etc. does not authorize inventing a K-line proxy.

A surrogate is allowed only as a clearly `INFERRED` branch justified before outcome testing. A surrogate selected because it backtests better is a new search branch and cannot be called source-equivalent.

## 6. Negative evidence

Before confirmatory testing, preserve source-level evidence as available across:
- positive examples;
- near-miss;
- negative/counterexample;
- wrong-context lookalike;
- ambiguous/no-trade;
- source-explicit invalidation/failure.

No universal `3+2+1` count is frozen. Missing negative material is itself a source-quality limitation.

## 7. RESEARCH_WAVE multiplicity control

Source discovery can remain open. Candidate outcome-bearing performance testing must occur inside a pre-registered immutable research wave.

Before the first outcome-bearing test in a wave, lock a `RESEARCH_WAVE_ID` manifest containing at minimum:
- protocol/statistical-profile version;
- tested playbook-family list;
- independently testable claim count semantics;
- PRIMARY branch hashes;
- declared alternative branches scheduled for outcome testing;
- instrument/timeframe/context scopes;
- parameter/search ranges;
- multiplicity denominator semantics.

Counting rules:
- claim count is based on independently falsifiable operationalized hypotheses, not sentence count;
- after any outcome-bearing test runs, adding a family/claim/branch creates a new wave/search event;
- every outcome-tested hypothesis remains permanently in the denominator, including FAIL and `INSUFFICIENT_EVIDENCE`;
- reporting/promoting winners must disclose the full tested denominator;
- multiplicity correction/decision rules must be monotonic with search freedom: more testing can never make acceptance easier.

## 8. Common statistical profile and freeze timing

The common project-wide statistical profile must be versioned, independently reviewed where required, and locked before the first candidate outcome-bearing performance backtest.

Before profile lock, allowed work includes:
- source discovery/provenance;
- SOURCE_ONLY claim extraction/interpretation;
- deterministic operationalization/specification;
- unit/integration/data-quality tests;
- engine-sanity tests using dummy/random/non-candidate fixtures that cannot inform candidate quality;
- non-outcome signal/event-frequency measurement used only to design sufficiency procedures.

Before profile lock, candidate performance outputs are forbidden, including PnL, equity curve, expectancy, Sharpe/risk-adjusted return, win/loss performance or equivalent candidate-quality outcomes.

The locked profile must define:
- common acceptance questions;
- counting units/multiplicity semantics;
- uncertainty/precision method;
- evidence-sufficiency procedure;
- dependence handling;
- numerical thresholds/procedure for the wave.

If candidate outcomes are intentionally used to calibrate the profile, that calibration cohort is permanently burned/exposed and cannot later serve as clean evidence under the same protocol lineage.

Changing the profile after outcome exposure creates a new profile/protocol version and does not restore prior unseen status.

## 9. Common acceptance contract

All families answer the same core questions:
1. **Economic edge:** after pre-registered costs/slippage, does the PRIMARY branch show positive net economic edge with uncertainty treated explicitly?
2. **Evidence sufficiency:** does it meet the locked project-wide sufficiency procedure using event counts, distinct trading days and dependence-aware aggregation/cluster treatment as appropriate?
3. **Risk/failure constraints:** do the required pre-registered risk/failure checks pass?
4. **Integrity:** were chronology/exposure/search/wave rules preserved?

Family-specific metrics may add constraints/diagnostics but may not replace the common contract or change after outcome exposure.

Six products are not assumed to equal six independent samples. Dependence is measured; no guessed fixed effective-product number is frozen.

If evidence sufficiency is unmet:

```text
INSUFFICIENT_EVIDENCE
```

not relaxed thresholds, changed dates or added post-result hypotheses.

## 10. Frozen historical chronology

Authority: `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`.

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

This is the frozen `12/6/6` split.

It is a governance choice for simplicity/auditability, not a guarantee of statistical power. Sparse families may return `INSUFFICIENT_EVIDENCE`.

## 11. Validation revision policy

Before validation: artifact/specification/metrics/scope are locked.

After validation exposure:

### CAT1_IMPLEMENTATION_DEFECT
Objective mismatch against an unambiguous pre-registered specification; repair restores the same intended specification.
- deterministic/independent evidence required;
- at most one same-validation rerun per family/epoch;
- full audit record required.

### CAT2_RESEARCH_LOGIC_CHANGE
Any intended logic/parameter/context/interpretation change.
- new descendant;
- inherits validation exposure;
- same validation is not fresh confirmation.

### CAT3_SPECIFICATION_AMBIGUITY
If validation results were needed to decide what the specification meant, treat as CAT2.

Unknown classification defaults to CAT2.

## 12. Historical final-holdout state machine

```text
FINAL_HISTORICAL_HOLDOUT_LOCKED
-> FINAL_HISTORICAL_HOLDOUT_EXPOSED
-> FINAL_ACCEPTED | FINAL_REJECTED | FINAL_VOID_IMPLEMENTATION_DEFECT
```

Rules:
- exposure is irreversible;
- `VOID` changes conclusion, never restores holdout status;
- final-inspired descendants inherit exposure;
- no tuning and rerunning the same final cohort as clean evidence;
- future genuinely prospective Shadow/Forward data is the route to stronger fresh evidence.

## 13. Single pre-outcome gate

Before the first candidate outcome-bearing performance backtest for a wave, all must be true:

```text
SOURCE_ONLY controls active and verified
COMMON_STATISTICAL_PROFILE locked
multiplicity counting unit locked
RESEARCH_WAVE test set + denominator locked
PRIMARY/scope/search identities locked
```

Until that gate is technically enforced, candidate outcome-bearing performance backtests remain prohibited.

## 14. Historical final-holdout unlock gates

Before historical final-holdout access:
- provenance/claim/PRIMARY review complete;
- observability resolved;
- lineage/mechanism/exposure record complete;
- deterministic artifact/code/parameter/environment identity frozen;
- development + validation evidence complete;
- search freedom/wave denominator accounted;
- common acceptance contract passes;
- relevant execution-realism prerequisites satisfied;
- required independent review passed;
- separate final-holdout unlock authority exists.

This protocol freeze does not itself unlock the historical final holdout.

## 15. Technical-debt activation

The following do not block semantic protocol freeze but become blockers before affected confirmatory/final-quality evidence relies on their semantics:
- TD-001 duplicate session/trading-day responsibility;
- TD-002 partial-close unrealized-PnL semantics;
- LIMIT-001 historical price-limit metadata.

## 16. Implementation requirements after freeze

The following are ordinary implementation work under this frozen semantic authority and do not need another Owner research-semantic gate, but must be versioned/tested/reviewed before the first outcome-bearing candidate test:
- exact common statistical profile;
- exact minimum-event thresholds;
- dependence/multiplicity implementation;
- research-wave manifest schema;
- SOURCE_ONLY technical enforcement/tests;
- model/researcher exposure-log field formats;
- Selection Firewall implementation consistent with `HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`.

## 17. What this protocol authorizes now

Once this file is binding, the project may proceed with the **pre-outcome research phase** only:
- implement/verify SOURCE_ONLY controls;
- perform source-faithful claim extraction after SOURCE_ONLY controls are verified;
- perform non-outcome deterministic operationalization and tests;
- implement the statistical-profile/wave/firewall machinery.

No candidate outcome-bearing performance backtest is authorized until the single pre-outcome gate is satisfied.

## 18. Still unauthorized

- historical final-holdout unlock;
- Shadow/live automated trading;
- real-money/broker actions;
- discretionary LLM live critical path;
- new paid commitments;
- permanent RiskGate changes.

## 19. Change control

Any future change to these frozen research semantics requires a new version, independent adversarial review when material, and the normal Owner research-semantic gate.
