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
rule combinations, chart/K-line patterns, or parameter grids whose objective is to discover
the best historical equity curve.

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
large indicator/rule/K-line-pattern/parameter universe
-> brute-force or automated search
-> rank by historical PnL/Sharpe/etc.
-> report the best survivor as the strategy
```

Bounded parameterization, robustness checks, feature interpretation, and controlled search
may be used when they are necessary to formalize or test an already identified playbook.
They must remain evidence-governed, recorded as search freedom, and must not silently turn
back into unrestricted strategy mining.

### Anti-regression interpretation guard

This section is a binding interpretation guard for later conversations and implementation work:

- Generic language in `ARCHITECTURE_BASELINE.md` such as "AI may find candidate ideas" does **not** re-authorize data-first automatic K-line/chart-pattern/indicator discovery. This Owner-approved Human Playbook First direction specializes that broader architecture language.
- The existence of normalized OHLCV/bar data does not create authority to mine shapes, indicators, rules, or parameter combinations first and then retrofit a human narrative afterward.
- `MVP does not require automatic pattern discovery` in the architecture baseline must not be interpreted as "automatic pattern discovery is an equally authorized current route". It is not the current research route.
- Tool availability, model capability, API quota, implementation convenience, or a promising backtest cannot silently change the research paradigm.
- Results, parameters, strategies, failure histories, or route judgments from other projects cannot be imported as evidence for changing this route.
- Any future move from Human Playbook First back toward data-first automatic strategy/pattern mining is a material research-direction change and requires explicit Owner approval plus formal authority updates before execution.

## 7. Relationship to Skeleton v1.0

This direction does **not** reopen or replace `ARCHITECTURE_BASELINE.md` Skeleton v1.0.
It specializes the previously intentionally-open Research Loop / Strategy Catalog route:

- Strategy Catalog already uses a Playbook Contract and requires provenance/source.
- Research Loop already permits AI to find candidate ideas, organize knowledge, implement
  drafts, analyze experiments, and red-team hypotheses.
- Backtest & Validation / Selection Firewall remain the examination system that determines
  whether a playbook survives evidence.

The original live-critical-path boundary is historical Skeleton v1.0 context. It is now
amended by the Owner decision recorded in
`docs/architecture/ADR_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1.md`: the Jianghe AI Trader may
propose a versioned, constrained trade intent from a causal observation. Deterministic RiskGate,
OMS, TradingState, broker reconciliation and Safety retain all execution and hard-risk truth.

## 8. Jianghe AI market-reading boundary

The long-term product concept includes machine assistance for recognizing which accepted
playbook/market scene best matches the current market, faster and more consistently than a
human trader.

The product decision-layer direction is now frozen, but real external operation is not authorized.

```text
JIANGHE_AI_DECISION_LAYER=ADOPTED_ARCHITECTURE_V0_1
AI_OUTPUT=CONSTRAINED_TRADE_INTENT_ONLY
DETERMINISTIC_RISK_EXECUTION_SAFETY=RETAINED
REAL_SHADOW_BROKER_REAL_MONEY=NOT_AUTHORIZED
MODEL_PROVIDER=ALL_CANDIDATE_UNTIL_FIDELITY_EVIDENCE
```

The current implementation provides only synthetic, non-outcome replay foundation. Any real
model provider, sub-minute capability, Shadow, broker or real-money activation remains a
separate future gate and cannot be inferred from this architecture amendment.

## 9. Relationship to the now-frozen Research Protocol

The protocol-design work that was the next step when this direction was first approved has since been completed.

Current binding authorities are:
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` — FROZEN / BINDING;
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` — FROZEN 12/6/6;
- `CURRENT_STATE.md` — the only authority for the project's **current** work package / next action.

Do **not** infer a current next action from historical wording in this research-direction document. This file defines direction, not mutable project state.

The frozen protocol now governs at minimum:
- admissible source/provenance rules;
- natural-language claim separation and PRIMARY interpretation rules;
- lineage/exposure inheritance;
- search-freedom / whole-wave multiplicity;
- SOURCE_ONLY interpretation controls;
- development / validation / historical-final chronology;
- validation revision categories;
- common statistical-profile freeze before candidate outcomes;
- historical-final access governance.

## 10. What is not frozen by this file

This research-direction decision itself does **not** freeze:

- specific books, creators, videos, traders, or playbooks;
- any concrete K-line strategy conclusion;
- parameter ranges;
- strategy ranking metrics;
- live scene-recognition implementation;
- broker/execution framework;
- permanent RiskGate rules.

Some research semantics that were intentionally left open when this file was first approved were later frozen by separate binding authority. In particular, Research Protocol v1.0 and the 12/6/6 chronology are now frozen elsewhere. This section must not be used to undo those later authorities.
