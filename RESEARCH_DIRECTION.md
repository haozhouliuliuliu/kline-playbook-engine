# RESEARCH_DIRECTION

## Status

STATUS=OWNER_APPROVED
EFFECTIVE_DATE=2026-08-18
PROJECT_RESEARCH_PARADIGM=HUMAN_PLAYBOOK_FIRST

This file defines the binding research-direction boundary for `kline-playbook-engine`.
It does not define any concrete profitable strategy, parameter set, chronological
split, final-unseen unlock, or live trading rule.

## 1. Product/research direction

The project's primary strategy-research route is:

```text
traceable human trading experience
-> AI-assisted extraction and structuring
-> versioned Playbook Contract
-> point-in-time market-scene representation / recognition
-> historical validation of applicability and failure conditions
-> strict validation / final-unseen governance
-> accepted or rejected playbook
```

In plain language, the intended product is a **trader playbook library + market-reading brain**:
the project should learn from mature, attributable human trading logic, make that logic
explicit and testable, and determine when a playbook does or does not fit the market.

The primary research engine is therefore **not** an unconstrained search over indicators,
rule combinations, or parameter grids whose objective is to discover the best historical
equity curve.

## 2. Candidate knowledge sources

Candidate playbooks may originate from traceable human sources such as:

- books;
- public teaching material;
- trader interviews or explanations;
- videos or other attributable educational material;
- other documented human trading experience admitted by the research protocol.

Every admitted playbook must preserve provenance/source identity sufficient to answer:

- where the idea came from;
- what the source actually claimed;
- what interpretation/translation was performed by AI or researchers;
- what later changes created a new playbook version or lineage.

A source being famous, experienced, persuasive, or profitable is **not** evidence that its
playbook is valid for this project.

## 3. What AI is for

AI may be used mainly in the offline Research Loop to:

- find and organize candidate human trading ideas;
- extract natural-language trading logic into structured playbook fields;
- distinguish market background, observation, confirmation, invalidation, exit logic,
  and stated non-applicable environments;
- propose testable representations of qualitative concepts;
- locate historical analogues and counterexamples without violating dataset exposure rules;
- analyze failures and regime/applicability boundaries;
- help implement deterministic strategy artifacts and tests;
- red-team whether a playbook has been mistranslated, overfit, or given excessive search freedom.

AI output is a research hypothesis or implementation aid, not accepted trading truth.

## 4. Playbook-first research object

The Strategy Catalog's existing Playbook Contract remains the strategy owner.
The research protocol should make a human-derived playbook explicit enough to preserve,
as applicable:

- provenance/source;
- market background/context;
- observed price/volume/volatility/session structure;
- qualitative pattern or setup;
- confirmation logic;
- entry intent;
- invalidation / "what would prove this read wrong";
- exit logic;
- known non-applicable environments;
- applicable instruments/timeframes if supported;
- implementation/feature interpretation version;
- family lineage and data-exposure history.

A meaningful change in interpretation or outcome-affecting logic creates a new version or
lineage under the existing identity/evidence rules.

## 5. Human source is hypothesis, not authority

`HUMAN_PLAYBOOK_FIRST` does **not** weaken statistical or evidence standards.

Every candidate remains subject to the existing architecture and evidence controls,
including as applicable:

- point-in-time / `available_at` semantics;
- chronological validation;
- execution realism;
- Selection Firewall;
- development / validation / final-unseen separation;
- lineage-aware exposure inheritance;
- search-freedom and multiple-testing controls;
- correlation / false-diversification checks;
- independent acceptance where required.

The project must be able to reject a human trading idea cleanly when evidence does not
support it.

## 6. Prohibited default research route

The following is **not** the project's default strategy-discovery route:

```text
large indicator/rule/parameter universe
-> brute-force or automated search
-> rank by historical PnL/Sharpe/etc.
-> report the best survivor as the strategy
```

Bounded parameterization, robustness checks, feature interpretation, and controlled search
may be used when they are necessary to formalize or test an already identified playbook.
They must remain evidence-governed, recorded as search freedom, and must not silently turn
back into unrestricted strategy mining.

## 7. Relationship to Skeleton v1.0

This direction does **not** reopen or replace `ARCHITECTURE_BASELINE.md` Skeleton v1.0.
It specializes the previously intentionally-open Research Loop / Strategy Catalog route:

- Strategy Catalog already uses a Playbook Contract and requires provenance/source.
- Research Loop already permits AI to find candidate ideas, organize knowledge, implement
  drafts, analyze experiments, and red-team hypotheses.
- Backtest & Validation / Selection Firewall remain the examination system that determines
  whether a playbook survives evidence.

The architecture's current live-critical-path boundary also remains binding:
**no discretionary LLM buy/sell decision in the live trading critical path is authorized by
this research-direction decision.**

## 8. Live market-reading brain is intentionally unresolved

The long-term product concept includes machine assistance for recognizing which accepted
playbook/market scene best matches the current market, faster and more consistently than a
human trader.

However the exact live implementation mode is **not frozen here**.

```text
LIVE_AI_SCENE_RECOGNITION_MODE=UNDECIDED
LIVE_DISCRETIONARY_LLM_CRITICAL_PATH=NOT_AUTHORIZED
OWNER_GATE_REQUIRED_FOR_LIVE_AI_SEMANTICS=YES
```

Possible future implementations may differ materially (for example deterministic features,
a frozen classifier/model, or a more flexible AI component). Any design that changes the
current Skeleton v1.0 live-critical-path boundary requires a separate architecture/research
review and Owner approval before activation.

## 9. Implication for the next research-protocol freeze

`CURRENT_NEXT_ACTION=RESEARCH_PROTOCOL_AND_CHRONOLOGICAL_SPLIT_FREEZE_REVIEW`
must be designed **under this Human Playbook First direction**.

Before strategy research begins, that review should determine at minimum:

- admissible source/provenance rules;
- how natural-language playbooks become versioned testable artifacts;
- how ambiguous qualitative concepts may be operationalized without unlimited search;
- playbook family / lineage semantics;
- search-budget accounting for reinterpretations, parameters, instruments, timeframes,
  and market-context variants;
- development / validation / final-unseen chronology and access rules;
- what validation feedback may or may not be used to revise a playbook;
- how rejected ideas and negative evidence are preserved;
- acceptance criteria before any final-unseen unlock.

## 10. What is not frozen by this file

This decision does **not** yet freeze:

- specific books, creators, videos, traders, or playbooks;
- any concrete K-line strategy conclusion;
- exact development/validation/final-unseen dates;
- any 12/6/6 or other split proposal;
- parameter ranges;
- strategy ranking metrics;
- final-unseen unlock rules beyond existing authority;
- live scene-recognition implementation;
- broker/execution framework;
- permanent RiskGate rules.

Those remain future protocol/architecture decisions under the normal Owner-gate process.
