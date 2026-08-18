# HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_FINAL_PREFREEZE_GAP_REVIEW_V0_1

> Date: 2026-08-19
> Status: PROJECT_BRAIN_FINAL_PREFREEZE_REVIEW / NEW_MATERIAL_GAPS_FOUND / NOT_FROZEN
> Scope: final project-brain recap after independent adversarial review and adjudication
> Binding direction: `RESEARCH_DIRECTION.md`
> Architecture: `ARCHITECTURE_BASELINE.md` Skeleton v1.0
> Reviewed candidate: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_2.md`
> Existing independent review: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADVERSARIAL_REVIEW_V0_1.md`
> Existing adjudication: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADJUDICATION_V0_1.md`

This review was triggered by the Owner's request for one final omission/error/forgetfulness check before automatically accepting the project-brain recommended freeze. The result is **NOT SAME AS BEFORE**: three material research-semantics gaps remain. Therefore the automatic Owner authorization condition is not satisfied and no freeze is executed by this review.

## 1. Overall verdict

`FINAL_PREFREEZE_VERDICT=HOLD_FOR_TARGETED_DELTA_REVIEW`

The prior package remains directionally sound, but the following three gaps are material enough that they must be resolved before Research Protocol v1.0 is frozen.

## 2. GAP-A — historical holdout is not necessarily epistemically unseen to humans or AI models

### Problem

The current protocol governs:
- repository/data access to development/validation/final windows;
- source examples that display protected market dates;
- branch/prompt/specification identity.

It does **not** govern external prior knowledge held by the human researcher or AI model.

Because the project is being designed in 2026 against historical 2024-2025 data:
- humans may remember important 2025 market outcomes;
- current AI models may have training/pretraining/retrieval exposure to 2025 market history;
- a model can potentially use latent outcome knowledge while choosing a `PRIMARY_BRANCH`, surrogate, context interpretation or family priority even when the locked final dataset is never opened.

Therefore `FINAL_UNSEEN` cannot safely mean "nobody participating in research has any prior knowledge of these historical outcomes" unless that stronger condition is actually demonstrated.

### Required semantic correction

Freeze candidate should distinguish:

```text
PROJECT_GOVERNED_HISTORICAL_HOLDOUT
!=
PROSPECTIVE_GENUINELY_UNSEEN_DATA
```

Recommended semantics:
- the 2025H2 reserve may remain the architecture's locked historical final holdout, protected from direct project outcome access/tuning;
- do not claim it is epistemically unseen to all humans/models;
- only future Shadow/Forward data collected after a playbook/version is frozen can be called genuinely prospective unseen evidence;
- primary-claim interpretation/operationalization should run in a `SOURCE_ONLY` process: no protected-window market retrieval/browsing, no outcome-oriented external search, and all material AI prompt/model/tool context is logged;
- if a human/model explicitly retrieves or cites protected-period market outcomes during claim design, mark the family exposed;
- latent model memory cannot be proven absent, so historical holdout evidence must be described with this limitation rather than overstated.

### Related schema requirement

Future claim/interpretation records should be able to store at least:

```text
interpretation_agent_type:
model_provider_and_name_if_ai:
model_or_runtime_version_if_available:
prompt_spec_hash:
retrieval_or_tool_access_mode:
source_input_bundle_hash:
explicit_protected_market_outcome_access: YES | NO | UNKNOWN
exogenous_market_knowledge_risk: PRESENT | POSSIBLE | UNKNOWN | MITIGATED_BY_SOURCE_ONLY_PROCESS
```

Provider-reported model knowledge cutoffs may be recorded as context, but must not be treated as proof that parametric memory excludes protected outcomes.

## 3. GAP-B — family/claim-level multiplicity is not explicit enough

### Problem

Skeleton v1.0 requires total search freedom to account for strategy count as well as parameters/instruments/timeframes/context. `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_2.md` strongly governs branches inside a family, but does not explicitly freeze the fact that testing **many different human playbooks/claims/families** is itself multiple testing.

Failure mode:

```text
extract 100 source-faithful human playbooks
-> each has one honest PRIMARY branch
-> test all 100
-> report the 5 historical winners
```

No within-family branch mining occurred, but selection bias/multiple testing remains severe.

### Required semantic correction

Before any outcome-bearing backtest, create a pre-registered `RESEARCH_WAVE_ID` containing:
- all playbook families to be tested in that wave;
- claim/hypothesis count where claims are separately testable;
- primary and alternative branch counts;
- instrument/timeframe/context combinations;
- parameter/search ranges;
- excluded/deferred candidates and reasons.

Rules:
- total multiplicity/search-freedom accounting includes the full wave, not only branches inside the eventual winner;
- failed/rejected/insufficient families remain recorded and cannot disappear from the denominator;
- adding a new family/claim after outcome inspection creates a new wave/descendant search event and cannot be silently merged into the old wave;
- the project-wide statistical profile must define how wave-level multiplicity affects acceptance when search scale becomes material.

Source discovery itself may remain broad; **outcome-bearing testing** must be wave-registered.

## 4. GAP-C — common statistical profile is currently allowed to freeze too late

### Problem

The current v0.2 / Owner package says exact confidence/precision method, dependence handling and minimum-event rules must be fixed before validation opens.

That still permits this sequence:

```text
run development performance backtests
-> observe which candidates look strong/weak
-> choose project-wide event thresholds/confidence method
-> then open validation
```

Even if the profile is later applied project-wide, choosing it after seeing outcome-bearing development results can create protocol-level threshold/metric shopping.

### Required semantic correction

Freeze candidate should require:

```text
COMMON_STATISTICAL_PROFILE_V1
must be independently reviewed + versioned + locked
BEFORE THE FIRST OUTCOME-BEARING PERFORMANCE BACKTEST
```

Allowed before that profile is frozen:
- source discovery;
- provenance/claim extraction;
- `PRIMARY_BRANCH` selection from source evidence;
- observability review;
- deterministic operationalization implementation;
- non-outcome unit/integration tests;
- data-quality and execution-semantic tests that do not reveal candidate performance.

Not allowed before that profile is frozen:
- candidate PnL/expectancy/Sharpe/win-rate/equity-curve comparison;
- any outcome-bearing backtest used to decide whether a candidate is promising.

This does not require the exact statistical numbers to be decided in this gap-review document. It requires the **timing boundary** to be frozen so the future profile cannot be calibrated to already-seen candidate performance.

If the project later decides it needs development outcomes to design the profile, that must be a separately governed calibration exercise whose families/data cannot then be treated as untouched evidence under the same protocol version.

## 5. Chronological split implication

The previous project-brain recommendation `12/6/6` is not rejected by these findings.

However its semantics must be corrected:
- 2024 = development cohort;
- 2025H1 = validation cohort;
- 2025H2 = locked project-governed historical final holdout;
- future Shadow/Forward = genuinely prospective unseen evidence.

The split-selection rationale must remain calendar/audit simplicity, not observed performance/regime comparison. No candidate split may be chosen by looking for the historically easiest final window.

## 6. What remains unchanged

The following prior recommendations still survive this final recap:
- Human Playbook First direction;
- source claim != AI/project interpretation != machine operationalization;
- `EXPLICIT / INFERRED / UNKNOWN`;
- exactly one source-justified PRIMARY branch before outcome testing;
- ambiguity stop rule;
- observability/surrogate fail-safe;
- lineage/exposure inheritance;
- effective-content-date source-example exposure;
- common acceptance contract;
- `INSUFFICIENT_EVIDENCE` as legitimate outcome;
- validation CAT1/CAT2/CAT3 rule;
- final exposure irreversible;
- no same-final retuning;
- 12/6/6 remains the leading simple split candidate;
- no final unlock/live/Shadow/real-money authorization from the protocol freeze.

## 7. Required next action

Because these are new material research-semantics changes discovered **after** the first independent review, they require one targeted independent adversarial delta review before Owner freeze.

The targeted reviewer should attack only:
1. historical-holdout vs genuinely prospective-unseen semantics and AI/human prior-knowledge contamination;
2. family/claim/wave-level multiplicity accounting;
3. statistical-profile freeze timing before first outcome-bearing backtest.

Do not reopen already accepted Skeleton v1.0 or the entire Human Playbook First direction unless one of these three gaps reveals a fatal contradiction.

## 8. Freeze status

```text
OWNER_AUTO_APPROVAL_CONDITION=NOT_SATISFIED_NEW_MATERIAL_GAPS_FOUND
RESEARCH_PROTOCOL_FREEZE_STATUS=NOT_EXECUTED
STRATEGY_RESEARCH_STARTED=NO
NEXT_ACTION=TARGETED_INDEPENDENT_ADVERSARIAL_DELTA_REVIEW
```
