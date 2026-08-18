# HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_1

> Date: 2026-08-19
> Status: DECISION_INPUT_READY / NOT_FROZEN / REQUIRES_ADVERSARIAL_REVIEW
> Binding direction: `RESEARCH_DIRECTION.md`
> Architecture: `ARCHITECTURE_BASELINE.md` Skeleton v1.0
> Source-layer close-out: `docs/research/HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT.md`
> Claim schema: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V0_1.md`
> Current state: `CURRENT_STATE.md`
>
> This document is a decision-ready INPUT package. It does not execute the research-protocol or chronological-split freeze. All recommendations below remain proposals until the required adversarial review and Owner decision gate are completed.

## 1. What is already binding and should NOT be reopened

Already binding:
- `HUMAN_PLAYBOOK_FIRST` is the primary research paradigm.
- Human sources create hypotheses, not accepted truth.
- Strategy Catalog / Playbook Contract remains the strategy owner.
- AI operates mainly in the offline Research Loop.
- No discretionary LLM buy/sell decisions in the live critical path.
- Selection Firewall / development-validation-final separation / lineage-aware exposure remain architectural requirements.
- Large unconstrained indicator/rule/parameter mining is not the default discovery route.
- Same strategy artifact/code hash must cross relevant validation modes.

This package specializes research semantics under those constraints; it does not reopen Skeleton v1.0.

## 2. Strongest counterarguments / failure risks FIRST

### RISK-1 — The accepted corpus is only 24 months

Current canonical corpus:
- 2024-01-01 through 2025-12-31;
- six products: cu/al/ni/au/ag/rb;
- 1-minute concrete-contract data.

Any chronological split leaves relatively little genuinely unseen history. Rare playbooks may have too few independent examples for strong inference.

Implication:
- a clean split can still be statistically weak;
- the protocol must prefer honest `INSUFFICIENT_EVIDENCE` over relaxing the split after seeing results;
- future Shadow/Forward data will be important for continuing unseen evidence.

### RISK-2 — Human source material itself can leak future market data

A source published during/after the canonical period may show charts or describe events from a validation/final-unseen window.

Example failure mode:

```text
final-unseen dates are technically locked in the dataset
but
researcher watches a later video that shows those same dates and outcomes
```

That is still exposure.

The protocol therefore needs source-example exposure accounting, not only database-access accounting.

### RISK-3 — AI interpretation creates hidden multiple testing

A fuzzy phrase can generate many plausible operational meanings.

If AI tries many definitions and keeps the best backtest, Human Playbook First degenerates into disguised rule mining.

Interpretation branches therefore need immutable IDs and search-freedom accounting.

### RISK-4 — Lineage can create false independent confirmation

Teacher/student, originator/descendant, repost and same-school sources can repeat one idea while appearing to be many sources.

Market Profile already demonstrated this risk.

Lineage must affect both evidence aggregation and data-exposure inheritance.

### RISK-5 — Observability substitution can silently change meaning

A source may rely on volume-at-price, DOM/order flow, fundamentals, news, research trips or human-process information that the current corpus does not contain.

Inventing a bar proxy solely to make a concept testable can invalidate source fidelity.

### RISK-6 — Validation feedback can contaminate a family

If validation results are observed and then logic is changed, the revised artifact is no longer independent of that validation set.

Renaming a strategy/version cannot restore unseen status.

### RISK-7 — Source selection itself has survivorship/marketing bias

Public books, successful traders, interviews and competition winners are not a random sample of trading ideas.

The protocol must preserve failed/negative/counter-evidence and avoid treating source fame or historical PnL claims as prior validity.

### RISK-8 — Execution realism is not yet final-quality complete

Known project prerequisites:
- TD-002 must be resolved before PnL-sensitive confirmatory evidence is treated as final quality.
- LIMIT-001 historical price-limit metadata must be bound before claiming realistic price-limit non-fill behavior.
- TD-001 session/trading-day duplicate responsibility must be consolidated/isolated before it can become a second business-logic owner in production/backtest/live paths.

These do not block protocol design, but they constrain what later evidence may claim.

## 3. Decision block A — admissible source / provenance semantics

### Project-brain provisional recommendation

For future claim extraction:

```text
TRACEABLE_ORIGINAL / nearest-original attributable material
-> eligible for EXPLICIT source claims

DERIVATIVE / repost
-> discovery or supporting context by default
-> may not silently become original authority

DISCOVERY_ONLY sources (for example competition rankings)
-> cannot generate playbook claims by themselves
```

If only a derivative survives, preserve the provenance chain and require explicit review before treating any statement as an attributable claim.

Performance claims/testimonials remain separate fields, never admission proof.

### Strongest counterargument

This may exclude useful Chinese historical material whose originals disappeared or are difficult to access.

### Proposed compromise

Allow derivative material only under explicit degraded-provenance status, never disguised as original, and require corroborating identity/context evidence before claim-level use.

### Freeze status

`PROPOSED / NOT_FROZEN`

## 4. Decision block B — claim status and source/interpretation separation

### Project-brain provisional recommendation

Freeze the three-way claim vocabulary:

```text
EXPLICIT
INFERRED
UNKNOWN
```

and durable separation:

```text
SOURCE CLAIM
!= PROJECT / AI INTERPRETATION
!= MACHINE OPERATIONALIZATION
```

Rules:
- `UNKNOWN` is acceptable and preferred over guesswork.
- interpretation versions never overwrite the source record.
- meaningful interpretation changes create new immutable interpretation/version identity.

### Strongest counterargument

Some human trading language is inherently contextual; forcing categorical labels could create false precision.

### Proposed mitigation

Keep ambiguity notes and multiple interpretation branches first-class. The three labels describe provenance of meaning, not confidence level.

### Freeze status

`PROPOSED / NOT_FROZEN`

## 5. Decision block C — interpretation branches / search-freedom accounting

### Project-brain provisional recommendation

Every materially distinct branch counts as research freedom, including as applicable:
- interpretation variants;
- parameters/thresholds;
- instrument subsets;
- timeframe variants;
- context/regime definitions;
- feature substitutions;
- materially changed entry/exit/invalidation logic.

Rule:

```text
if a change could materially change historical outcomes
-> new version/branch
-> search freedom recorded
```

Do not allow AI to generate many hidden definitions and retain only the winner.

### Strongest counterargument

Over-counting minor interpretation differences can make legitimate qualitative translation practically impossible.

### Proposed mitigation

Later protocol may distinguish `MATERIAL` vs `NON_MATERIAL` edits, but outcome-affecting ambiguity must default to material until proven otherwise.

### Freeze status

`PROPOSED / NOT_FROZEN`

## 6. Decision block D — lineage and exposure inheritance

### Project-brain provisional recommendation

Lineage should inherit both conceptual dependence and data exposure.

Rules proposed:
- renaming family/version does not reset exposure;
- descendants inherit parent development/validation/final exposure;
- teacher/student or originator/descendant sources are not independent confirmations by default;
- source material with identifiable historical example dates should record those dates as source-example exposure;
- if a claim's source visibly exposes a market date, that date cannot later be called unseen for that claim/family merely because the dataset API was locked.

If example dates are unknown but material plausibly covers the reserved final window, the family should fail closed until exposure is resolved.

### Strongest counterargument

Source-example exposure can be hard to reconstruct, especially for videos/articles with mixed examples.

### Proposed mitigation

Track exposure at the finest practical level; unknown exposure becomes an explicit limitation rather than assumed clean.

### Freeze status

`PROPOSED / NOT_FROZEN`

## 7. Decision block E — observability gate

### Project-brain provisional recommendation

Before machine operationalization, every claim must answer:
1. what did the source actually observe?
2. does the project own that input point-in-time?
3. is a proposed substitute meaning-preserving?
4. if not, should the claim remain untestable?

Candidate outcomes:

```text
OBSERVABLE_NOW
PARTIALLY_OBSERVABLE
NOT_OBSERVABLE_WITH_CURRENT_DATA
UNKNOWN
NOT_APPLICABLE
```

Rule:

```text
missing source input
!= permission to invent a bar proxy
```

### Strongest counterargument

Strict fidelity can exclude concepts where a reasonable statistical surrogate exists.

### Proposed mitigation

A surrogate may be proposed later as a new `INFERRED` interpretation/version with explicit semantic-change risk; it must never be labeled source-equivalent without evidence.

### Freeze status

`PROPOSED / NOT_FROZEN`

## 8. Decision block F — negative examples / counter-evidence / no-trade

### Project-brain provisional recommendation

Before operationalization, a playbook-family evidence bundle should contain more than positive examples.

Required classes should include as available:
- positive examples;
- near-miss;
- negative/counterexample;
- wrong-context lookalike;
- ambiguous case;
- source-explicit failure/invalidation/no-trade where available.

Do NOT freeze `3 + 2 + 1` as a universal count. Retain it only as a sampling heuristic.

### Strongest counterargument

Some sources do not publish enough failure material; hard counts could unfairly reject potentially useful ideas.

### Proposed mitigation

Freeze the requirement for explicit negative/counterexample review, not a universal number. Missing negative material itself becomes a source-quality limitation.

### Freeze status

`PROPOSED / NOT_FROZEN`

## 9. Decision block G — chronological split

No split is active yet.

Canonical history: 2024-01-01 through 2025-12-31.

### Candidate G1 — 12 / 6 / 6

```text
Development: 2024-01-01 .. 2024-12-31
Validation:  2025-01-01 .. 2025-06-30
Final-unseen:2025-07-01 .. 2025-12-31
```

Pros:
- simple and auditable;
- full first year for development;
- equal six-month validation and final reserve;
- easy exposure bookkeeping.

Risks:
- six-month validation/final periods may be underpowered for sparse playbooks;
- half-year seasonality/regime concentration;
- any source showing H2-2025 examples could contaminate final-unseen for that family.

### Candidate G2 — 10 / 8 / 6

```text
Development: first 10 months
Validation: next 8 months
Final-unseen: last 6 months
```

Pros:
- more validation history;
- preserves six-month final reserve.

Risks:
- less development history for contextual playbooks;
- calendar boundaries become less intuitive;
- still limited sample size.

### Candidate G3 — 12-month development + rolling/blocked validation inside next 6 months + 6-month final reserve

Pros:
- may provide richer stability diagnostics inside validation.

Risks:
- substantially more complex;
- repeated validation looks can become another source of tuning/search freedom;
- easier to accidentally convert validation into development.

### Project-brain provisional recommendation before adversarial review

`G1 (12/6/6)` is the leading simplicity candidate, but **not yet recommended for freeze** until adversarial review specifically addresses sparse-event power, seasonality and source-example leakage.

The protocol should prefer `INSUFFICIENT_EVIDENCE` over changing dates after seeing results.

### Freeze status

`UNDECIDED / OWNER-GATED`

## 10. Decision block H — validation feedback / revision policy

### Project-brain provisional recommendation

Before validation opens:
- playbook artifact/version and planned metrics/gates are pre-registered.

After validation results are observed:
- validation may accept/reject/diagnose;
- any outcome-affecting revision creates a descendant with inherited exposure;
- the same observed validation set cannot become fresh confirmation for that descendant;
- if no untouched confirmation cohort remains, the descendant waits for new Shadow/Forward data or another pre-governed unseen source.

### Strongest counterargument

This is expensive in a 24-month dataset and may reject promising ideas after one correctable defect.

### Proposed mitigation

Use development data aggressively for debugging and robustness before opening validation. Validation is an exam, not a design workshop.

### Freeze status

`PROPOSED / NOT_FROZEN`

## 11. Decision block I — final-unseen unlock

### Project-brain provisional recommendation

Final-unseen remains technically locked until all pre-final gates pass.

Minimum structural gates before unlock should include:
- provenance/claim/interpretation review complete;
- observability resolved;
- lineage/exposure record complete;
- deterministic artifact/code/parameter/environment identity frozen;
- development + validation evidence complete;
- search freedom recorded and overfitting controls applied as required;
- execution realism prerequisites relevant to the playbook satisfied;
- independent adversarial review passed;
- family-specific acceptance metrics/thresholds were pre-registered before validation/final access.

Final result policy:
- final pass may support acceptance;
- final fail rejects/defers the tested family/version;
- final results may not be used to tune and re-present the same lineage as unseen.

### Strongest counterargument

A single final window can be noisy and create false rejection.

### Proposed mitigation

Final-unseen is not the only evidence forever; future Shadow/Forward data provides continuing unseen evidence. The cost of false rejection is preferable to laundering final data into development.

### Freeze status

`PROPOSED / OWNER-GATED`

## 12. Decision block J — acceptance criteria architecture

### Project-brain provisional recommendation

Freeze **global structural gates**, but do not force one universal numeric Sharpe/PnL/sample threshold across every playbook family.

For each family, before validation exposure, require a versioned family test plan that pre-registers:
- primary metric(s);
- minimum sample/event requirement;
- cost/slippage assumptions;
- drawdown/risk constraints;
- stability/robustness checks;
- relevant instrument/context scope;
- rejection criteria.

This preserves pre-registration while avoiding arbitrary one-size-fits-all thresholds.

### Strongest counterargument

Family-specific gates can be manipulated to favor each candidate.

### Proposed mitigation

Family test plans must be approved before validation, use bounded templates, and count unusual/custom criteria as additional research freedom requiring justification.

### Freeze status

`PROPOSED / NOT_FROZEN`

## 13. Skeptical / statistical guardrail options

The protocol should freeze the principle that multiple testing/search freedom must be controlled, but it need not automatically mandate one method for every research scale.

Candidate references:
- White Reality Check;
- Sullivan/Timmermann/White data-snooping application;
- Bailey et al. probability of backtest overfitting.

Possible future policy:

```text
small bounded family / few pre-registered variants
-> transparent search accounting + robustness + chronological validation may be sufficient

larger interpretation/parameter universe
-> stronger multiple-testing / overfitting control required
```

Exact statistical method/threshold remains unresolved and should be selected based on the actual search space before confirmatory validation.

## 14. AI role in the frozen protocol — candidate boundary

AI may:
- discover/organize sources;
- extract anchored source claims;
- propose interpretations;
- enumerate ambiguities/alternatives;
- implement deterministic artifacts/tests;
- find counterexamples;
- red-team source fidelity and overfitting.

AI may not:
- silently convert inferred meanings to source claims;
- hide interpretation branches;
- inspect locked final data;
- tune the same lineage after final exposure and call it unseen;
- approve its own final research evidence.

This is consistent with existing `RESEARCH_DIRECTION.md` and Skeleton v1.0.

## 15. Implementation prerequisites before final-quality evidence

Not protocol blockers today, but must be activated at the correct stage:

- `TD-002`: resolve partial-close unrealized-PnL semantics before PnL-sensitive confirmatory evidence is final quality.
- `LIMIT-001`: bind governed historical price-limit metadata before claiming realistic price-limit non-fill behavior.
- `TD-001`: consolidate/isolate duplicate session/trading-day responsibility before it can become a second authority in backtest/production/live paths.

## 16. Owner-level decisions this package is preparing

The Owner should not be asked to decide routine fields or implementation details.

Material freeze decisions can be compressed to:

1. **Claim/interpretation governance** — approve or change `EXPLICIT / INFERRED / UNKNOWN`, immutable interpretation branching and search-freedom treatment.
2. **Exposure/lineage/observability governance** — approve source-example exposure inheritance, lineage inheritance and fail-closed observability rules.
3. **Chronological split** — choose/freeze the date partition (G1/G2/other) and final-unseen reserve.
4. **Validation/final revision policy** — decide whether observed validation/final data permanently contaminates descendants as proposed.
5. **Acceptance architecture** — approve global structural gates + family-specific pre-registered numeric test plans.

Everything else should be implemented by the project brain under those decisions.

## 17. Required adversarial review before Owner freeze

Before any of the above becomes binding, an independent reviewer should attack at least:
- whether the 24-month corpus can support the proposed split;
- whether 12/6/6 is too weak or too arbitrary;
- source-example leakage rules;
- hidden search freedom in AI interpretation;
- lineage/exposure inheritance loopholes;
- whether family-specific acceptance gates can be gamed;
- whether the proposed revision policy is too strict or not strict enough;
- whether the protocol accidentally blocks useful qualitative human knowledge or allows disguised data mining.

Reviewer output is advisory. It may not freeze project semantics.

## 18. Current package result

`PROTOCOL_INPUT_PACKAGE_STATUS=READY_FOR_INDEPENDENT_ADVERSARIAL_REVIEW`

No protocol or chronological split is frozen by this file.
No real playbook claim extraction is authorized by this file.
