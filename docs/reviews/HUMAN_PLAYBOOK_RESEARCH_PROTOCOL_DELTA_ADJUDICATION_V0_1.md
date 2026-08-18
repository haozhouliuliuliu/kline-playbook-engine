# HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_DELTA_ADJUDICATION_V0_1

> Date: 2026-08-19
> Status: PROJECT_BRAIN_DELTA_ADJUDICATION / NOT_FROZEN
> Delta review: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_DELTA_ADVERSARIAL_REVIEW_V0_1.md`
> Prior candidate: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_2.md`
> Binding direction: `RESEARCH_DIRECTION.md`

## 1. Overall verdict

`DELTA_REVIEW_ACCEPTED_WITH_PROJECT_BRAIN_CLARIFICATIONS`

The targeted review confirms all three final pre-freeze gaps are material and mutually compatible. It found no new CRITICAL architecture/research-paradigm flaw and does not disqualify the 12/6/6 historical split candidate or `INSUFFICIENT_EVIDENCE`.

The review does, however, introduce new material research-semantics that were not present in the earlier Owner decision package. They must therefore be added to the final Owner freeze package before protocol freeze.

## 2. GAP A — historical holdout vs prospective genuinely unseen evidence

### Decision: ACCEPT

Freeze candidate must distinguish:

```text
PROJECT_GOVERNED_HISTORICAL_HOLDOUT
!=
PROSPECTIVE_GENUINELY_UNSEEN_DATA
```

The 2025 H2 historical final cohort remains valuable because it prevents project-internal iterative tuning and creates a one-shot governed historical exam. It must not be described as proof that every human researcher or AI model was epistemically unaware of those market outcomes.

Required semantics:
- historical holdout protects against project-controlled access/tuning, not unknowable latent/model memory;
- AI/source interpretation sessions must use a `SOURCE_ONLY` environment that technically denies retrieval/query of protected-period market outcomes;
- model identity/version, tool/retrieval mode, prompt/spec version and source-bundle identity are recorded as research context;
- explicit researcher/model references to protected-period outcomes create exposure for the affected family;
- unverifiable latent/parametric prior knowledge is disclosed as a background threat-model limitation, not falsely certified away;
- strongest unseen claims and any later real-deployment promotion require genuinely future Shadow/Forward evidence under later authority.

Clarification: this does not require the project to prove an AI model has no historical market memory. The rule is to control what the project can control, disclose the residual risk, and narrow the claim strength accordingly.

## 3. GAP B — research-wave multiplicity

### Decision: ACCEPT

The protocol must explicitly govern multiplicity across Human Playbook families/claims, not only interpretation branches inside one family.

Before the first outcome-bearing performance backtest in a research wave, lock an immutable `RESEARCH_WAVE_ID` manifest containing at minimum:
- protocol/statistical-profile version;
- tested family list;
- independently testable claim count semantics;
- PRIMARY branch hashes;
- declared alternative branches actually scheduled for outcome testing;
- instrument/timeframe/context scope;
- parameter/search ranges;
- multiplicity denominator semantics.

Rules:
- source discovery can remain open, but outcome-bearing performance testing is wave-registered;
- a claim is counted by independently falsifiable operationalized hypothesis identity, not by sentence count;
- once any outcome-bearing test in the wave runs, adding a new family/claim/branch for performance testing creates a new wave/search event;
- all outcome-tested hypotheses remain permanently in the denominator; failures and `INSUFFICIENT_EVIDENCE` cannot be deleted from the search history;
- reporting or promoting winners must disclose the full tested denominator;
- the correction/decision rule must be monotonic with search freedom: testing more hypotheses must never make acceptance easier.

The exact multiple-testing formula remains a versioned statistical-profile implementation detail, but the counting/denominator semantics are frozen research rules.

## 4. GAP C — statistical-profile freeze timing

### Decision: ACCEPT

The common project-wide statistical profile must be locked before the first candidate outcome-bearing performance backtest, not merely before validation.

Freeze candidate must distinguish:

### Allowed before profile lock
- source discovery/provenance;
- claim extraction and source-only interpretation;
- deterministic operationalization/specification;
- unit/integration/data-quality tests;
- engine-sanity tests using dummy/random/non-candidate fixtures that cannot inform candidate performance;
- non-outcome signal/event-frequency measurement used only to design sufficiency rules.

### Not allowed before profile lock
Any candidate test revealing performance outcomes such as:
- PnL/equity curve;
- expectancy;
- Sharpe/risk-adjusted return;
- win/loss performance;
- any outcome metric used to judge candidate quality.

The profile must lock both:
1. semantic principles/counting units/common acceptance contract; and
2. numerical procedure used for the first wave.

If PnL/outcome data is intentionally used to calibrate the profile, that calibration cohort is permanently burned/exposed and cannot later serve as clean evidence under the same protocol lineage.

Changing the locked profile after outcome exposure creates a new protocol/profile version and cannot retroactively preserve prior unseen status.

## 5. Cross-gap gate

The minimum safe lifecycle has one decisive gate:

```text
BEFORE FIRST OUTCOME-BEARING PERFORMANCE BACKTEST:
- SOURCE_ONLY interpretation controls active;
- common statistical profile locked;
- multiplicity counting unit locked;
- research wave test set + denominator locked.
```

This makes the three gaps compatible rather than contradictory.

## 6. Historical split adjudication

`12/6/6` remains the project-brain recommended initial historical chronology:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

The semantic correction is in the claim attached to the final cohort:
- historical final pass = pass of a one-shot project-governed historical exam;
- it is not proof of epistemically unseen evidence for all humans/models;
- genuinely prospective unseen evidence comes later from future Shadow/Forward cohorts under separate authority.

The split still does not guarantee statistical sufficiency. `INSUFFICIENT_EVIDENCE` remains the safe result when pre-registered sufficiency is unmet.

## 7. Owner-gated vs implementation detail

### Must be Owner-frozen
- historical-holdout vs prospective-unseen distinction;
- SOURCE_ONLY technical-denial principle and residual prior-knowledge threat model;
- research-wave pre-registration / denominator permanence / post-lock new-wave rule;
- statistical-profile lock before first outcome-bearing candidate backtest;
- burned calibration cohort rule;
- 12/6/6 historical split;
- `INSUFFICIENT_EVIDENCE` as valid outcome;
- existing v0.2 PRIMARY/lineage/observability/validation/final rules.

### Ordinary implementation after semantic freeze
- exact statistical confidence/dependence/multiplicity method;
- exact numerical minimum-event thresholds;
- wave-manifest schema fields;
- SOURCE_ONLY engineering configuration and tests;
- model/researcher exposure log field format;
- concrete Selection Firewall enforcement code.

These implementation artifacts still must be completed and independently reviewed where required before the first outcome-bearing performance backtest.

## 8. Freeze status

`NOT_FROZEN`

The next action is to publish protocol candidate v0.3 and a final Owner decision package containing the new semantics. No strategy research is authorized by this adjudication.