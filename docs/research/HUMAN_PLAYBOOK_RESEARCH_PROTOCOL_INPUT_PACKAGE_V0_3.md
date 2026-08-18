# HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_3

> Date: 2026-08-19
> Status: FINAL_OWNER_DECISION_CANDIDATE / NOT_FROZEN
> Supersedes as freeze candidate: `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_2.md`
> Prior review: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADVERSARIAL_REVIEW_V0_1.md`
> Prior adjudication: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADJUDICATION_V0_1.md`
> Final gap review: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_FINAL_PREFREEZE_GAP_REVIEW_V0_1.md`
> Delta review: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_DELTA_ADVERSARIAL_REVIEW_V0_1.md`
> Delta adjudication: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_DELTA_ADJUDICATION_V0_1.md`
> Binding direction: `RESEARCH_DIRECTION.md`
> Architecture: `ARCHITECTURE_BASELINE.md` Skeleton v1.0

This is the final pre-freeze research-protocol candidate. It remains NOT FROZEN until the Owner explicitly approves the material research semantics.

## 1. Five operational buckets

1. source / claim;
2. interpretation / search freedom;
3. lineage / exposure;
4. observability;
5. validation / final acceptance.

A sixth cross-cutting control, `RESEARCH_WAVE`, governs multiplicity across families/claims before outcome-bearing testing.

## 2. Source / claim governance

Freeze candidate:
- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`;
- claim status: `EXPLICIT / INFERRED / UNKNOWN`;
- original/nearest-original attributable material preferred for `EXPLICIT`;
- derivative material must preserve degraded provenance and lineage;
- discovery-only records such as rankings cannot create playbook claims by themselves;
- performance/testimonial claims are never validity evidence;
- unknown meaning stays `UNKNOWN` rather than guessed.

## 3. PRIMARY interpretation / search freedom

Before any outcome-bearing backtest, every source-faithful claim must have exactly one source-justified `PRIMARY_BRANCH`.

If source evidence alone cannot justify one primary interpretation:

```text
AMBIGUOUS / INSUFFICIENTLY_OPERATIONALIZED -> STOP
```

Alternative branches:
- may be preserved as explicit sensitivity/exploratory branches;
- cannot rescue a failed primary and still be reported as validation of the source claim;
- count as search freedom if outcome-tested.

Every tested branch has a deterministic operationalization identity/hash over outcome-affecting logic, inputs, parameters, scope and context.

Before outcome testing, lock:
- PRIMARY hash;
- declared outcome-tested alternative hashes;
- instrument/timeframe/context scope;
- parameter/search ranges;
- materially relevant AI prompt/spec version.

Post-lock additions are new descendants/search events and inherit exposure.

## 4. SOURCE_ONLY interpretation environment / historical knowledge threat model

Historical research cannot honestly guarantee that every human researcher or AI model is epistemically unaware of 2024-2025 market outcomes.

Therefore distinguish:

```text
PROJECT_GOVERNED_HISTORICAL_HOLDOUT
!=
PROSPECTIVE_GENUINELY_UNSEEN_DATA
```

During source claim extraction and interpretation:
- use a `SOURCE_ONLY` environment;
- technically deny retrieval/query of protected-period market outcomes, rather than relying only on prompt instructions;
- record model identity/version, prompt/spec version, tool/retrieval mode and source-bundle identity;
- explicit protected-period outcome references by a researcher/model create exposure for the affected family;
- latent/parametric prior market knowledge that cannot be proven absent is disclosed as a residual threat-model limitation, not falsely certified away.

Historical holdout therefore tests project-procedural integrity against internal tuning. Stronger genuinely unseen claims require future prospective Shadow/Forward evidence under later authority.

## 5. Lineage / exposure

Renaming never resets exposure.

Family identity binds a mechanism-level signature over outcome-affecting logic/inputs/context plus available provenance evidence.

Lineage review may use:
- explicit attribution;
- source chronology;
- unusual shared vocabulary/mechanism structure;
- parent/descendant derivation;
- shared operationalization components.

Similarity is evidence for review, not automatic proof of genealogy; unresolved dependence cannot be counted as independent confirmation.

### Source-example exposure

Use effective content/version date, not blindly original publication date.

```text
if effective_content_date < protected_window_start
-> material cannot contain future examples from that protected window
-> no example-date audit required for that window
else
-> example-date exposure audit required
```

Exposure includes charts/visuals, written dated examples and verbal outcome descriptions. Derivatives inherit original exposure plus added-content exposure. Unknown dates fail closed only for the affected material/family protected window.

Exposure is irreversible once protected outcomes are observed.

## 6. Observability / surrogate rule

Before operationalization ask:
1. what did the source actually observe?
2. is that input available point-in-time in project data?
3. is a substitute justified from source semantics/measurement logic before outcome testing?
4. if not, should the claim remain untestable?

States:
`OBSERVABLE_NOW / PARTIALLY_OBSERVABLE / NOT_OBSERVABLE_WITH_CURRENT_DATA / UNKNOWN / NOT_APPLICABLE`.

Missing DOM/order flow/fundamentals/news/etc. does not authorize inventing a K-line proxy.

A surrogate may exist only as a clearly `INFERRED` branch justified before outcome testing. A surrogate chosen because it backtests better is a new search branch and cannot be called source-equivalent.

## 7. Negative evidence

Before confirmatory testing, preserve as available:
- positive examples;
- near-miss;
- negative/counterexample;
- wrong-context lookalike;
- ambiguous/no-trade;
- source-explicit invalidation/failure.

No universal `3+2+1` count is frozen. Missing negative material is itself a limitation.

## 8. RESEARCH_WAVE multiplicity control

Source discovery can remain open. Outcome-bearing performance testing must occur inside a pre-registered immutable research wave.

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
- once any outcome-bearing test runs, adding a new family/claim/branch creates a new wave/search event;
- all outcome-tested hypotheses remain permanently in the denominator, including FAIL and `INSUFFICIENT_EVIDENCE`;
- reporting/promoting winners must disclose the full tested denominator;
- multiplicity correction/decision rules must be monotonic with search freedom: more testing can never make acceptance easier.

Exact statistical correction method is implemented in the project-wide statistical profile, not selected family-by-family.

## 9. Common statistical profile / freeze timing

The common project-wide statistical profile must be locked before the first candidate outcome-bearing performance backtest.

### Allowed before profile lock
- source discovery/provenance;
- source-only claim extraction/interpretation;
- deterministic operationalization/specification;
- unit/integration/data-quality tests;
- engine-sanity tests using dummy/random/non-candidate fixtures that cannot inform candidate quality;
- non-outcome signal/event-frequency measurement used only to design sufficiency procedures.

### Forbidden before profile lock
Candidate performance outputs including PnL, equity curve, expectancy, Sharpe/risk-adjusted return, win/loss performance or equivalent candidate-quality outcomes.

The locked profile includes:
- common acceptance questions;
- counting units/multiplicity semantics;
- uncertainty/precision method;
- evidence-sufficiency procedure;
- dependence handling;
- numerical thresholds/procedure for the wave.

If candidate PnL/outcomes are intentionally used to calibrate a profile, that calibration cohort is permanently burned/exposed and cannot later serve as clean evidence under the same protocol lineage.

Changing the profile after outcome exposure creates a new profile/protocol version and does not restore prior unseen status.

## 10. Common acceptance contract

All families answer the same core questions:

1. **Economic edge:** after pre-registered costs/slippage, does the PRIMARY branch show positive net economic edge with uncertainty treated explicitly?
2. **Evidence sufficiency:** does it meet the locked project-wide sufficiency procedure using event counts, distinct trading days and dependence-aware aggregation/cluster treatment as appropriate?
3. **Risk/failure constraints:** do the required pre-registered risk/failure checks pass?
4. **Integrity:** were chronology/exposure/search/wave rules preserved?

Family-specific metrics may add constraints/diagnostics but may not replace the common contract or change after outcome exposure.

Six products are not assumed to equal six independent samples. Dependence is measured; no guessed fixed effective-product number is frozen.

If sufficiency is unmet:

`INSUFFICIENT_EVIDENCE`

not relaxed thresholds, changed dates or added post-result hypotheses.

## 11. Initial historical chronology candidate

Recommended freeze:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

This is the `12/6/6` split.

Why:
- simplest audit trail;
- full first calendar year for development/debugging;
- equal validation/final reserves;
- easiest exposure bookkeeping;
- avoids repeated rolling validation looks.

Limitations:
- sparse families may be underpowered;
- half-year regime/seasonality concentration;
- correlated products reduce effective independence;
- historical final pass is a one-shot project-governed historical exam, not proof of epistemically unseen evidence or timeless validity.

`10/8/6` remains a legitimate alternative; rolling validation is not recommended for the first protocol.

## 12. Validation revision policy

Before validation: artifact/specification/metrics/scope are locked.

After validation exposure:

### CAT1_IMPLEMENTATION_DEFECT
Objective mismatch against an unambiguous pre-registered specification. Repair restores the same intended specification.
- deterministic/independent evidence required;
- at most one same-validation rerun per family/epoch;
- full audit record.

### CAT2_RESEARCH_LOGIC_CHANGE
Any intended logic/parameter/context/interpretation change.
- new descendant;
- inherits validation exposure;
- same validation is not fresh confirmation.

### CAT3_SPECIFICATION_AMBIGUITY
If validation results were needed to decide what the specification meant, treat as CAT2.

Unknown classification defaults to CAT2.

## 13. Historical final-holdout state machine

```text
FINAL_HISTORICAL_HOLDOUT_LOCKED
-> FINAL_HISTORICAL_HOLDOUT_EXPOSED
-> FINAL_ACCEPTED | FINAL_REJECTED | FINAL_VOID_IMPLEMENTATION_DEFECT
```

Rules:
- exposure irreversible;
- `VOID` changes conclusion, never restores holdout status;
- final-inspired descendants inherit exposure;
- no tuning and rerunning the same final cohort as clean evidence;
- future genuinely prospective Shadow/Forward data is the route to stronger fresh evidence.

## 14. Single pre-outcome gate

Before the first outcome-bearing performance backtest for a wave, all must be true:

```text
SOURCE_ONLY controls active
COMMON_STATISTICAL_PROFILE locked
multiplicity counting unit locked
RESEARCH_WAVE test set + denominator locked
PRIMARY/scope/search identities locked
```

This is the main anti-overfitting gate before development performance begins.

## 15. Final-holdout unlock structural gates

Before historical final-holdout access:
- provenance/claim/PRIMARY review complete;
- observability resolved;
- lineage/mechanism/exposure record complete;
- deterministic artifact/code/parameter/environment identity frozen;
- development + validation evidence complete;
- search freedom/wave denominator accounted;
- common acceptance contract passes;
- relevant execution-realism prerequisites satisfied;
- required independent review passed.

## 16. Technical debt activation

Not blockers for semantic protocol freeze:
- TD-001;
- TD-002;
- LIMIT-001.

They become blockers before affected confirmatory/final-quality claims rely on those semantics.

## 17. Implementation details after semantic freeze

The following do not need separate Owner semantic approval once this protocol is frozen, but must be versioned and independently reviewed where required before first outcome-bearing testing:
- exact confidence/precision method;
- exact minimum-event thresholds;
- dependence/multiplicity implementation;
- wave-manifest schema;
- SOURCE_ONLY engineering enforcement/tests;
- model/researcher exposure-log field format;
- Selection Firewall implementation.

## 18. What remains unauthorized even after this protocol freeze

This protocol does not authorize:
- final-holdout unlock by itself;
- Shadow/live automated trading;
- real-money/broker orders;
- discretionary LLM live critical path;
- paid commitments;
- permanent RiskGate changes.

## 19. Freeze candidate decision

Project-brain recommendation remains:

```text
APPROVE GOVERNANCE = YES
INITIAL SPLIT = 12/6/6
ALLOW INSUFFICIENT_EVIDENCE = YES
APPROVE HISTORICAL-HOLDOUT / PROSPECTIVE-UNSEEN DISTINCTION = YES
APPROVE RESEARCH_WAVE MULTIPLICITY GOVERNANCE = YES
APPROVE PRE-OUTCOME STATISTICAL-PROFILE LOCK = YES
```

`OWNER_DECISION_REQUIRED / NOT_FROZEN`