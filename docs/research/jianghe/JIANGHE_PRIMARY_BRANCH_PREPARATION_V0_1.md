# 江河 PRIMARY Branch Preparation V0.1

> Status: `INTEGRATED_PRE_FREEZE_NON_OUTCOME_PREPARATION`  
> Scope: define the source-justified claim-level PRIMARY preparation contract for Jianghe AI Trader.  
> Does not freeze PRIMARY semantics, promote PRIMARY eligibility, inspect candidate outcomes, or adopt a model/provider.

## 1. Why this preparation exists

The frozen Human Playbook protocol requires every source-faithful claim to have exactly one source-justified PRIMARY branch before any outcome-bearing research. The Jianghe AI Trader protocol specializes that requirement: PRIMARY is a stable **interpretation branch + AI Trader identity**, not a deterministic fixed-rule market-decision machine.

The current Jianghe V1.1 source bundle is already material-bound by SOURCE_ONLY evidence:

```text
KNOWLEDGE_PACK_VERSION=JIANGHE_V1_1
KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
CLAIM_RECORD_COUNT=352
CASE_MANIFEST_IDENTITY=06dc398086ada39da0214230dcff015561592ea55f041b31fdf0f58258638ac1
CASE_RECORD_COUNT=80
```

Binding authorities:
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
- `docs/research/JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md`
- `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md`
- `docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json`

Mutable readiness remains owned by repository-root `CURRENT_STATE.md` / `PROJECT_BRAIN_RUNTIME_BRIEF.md`.

## 2. Design decision: claim-level PRIMARY identity

Do **not** define only four giant PRIMARY branches for Families A/B/C/D.

The 352 claims include market context, observed cues, no-trade constraints, action permission, confirmation, invalidation, management, exit, applicability, risk process, review process, hard negatives and UNKNOWN/source-conflicted concepts. Collapsing all of these into four family-level branches would silently erase source scope and ambiguity.

Instead, every claim receives its own versioned PRIMARY branch object:

```text
claim_id
-> one selected source-justified interpretation
-> explicit scope / applicability / negative constraints
-> explicit UNKNOWN / contradiction preservation
-> observability disposition
-> operationalization mode
-> deterministic branch identity/hash
```

Family A/B/C/D/NONE remains a scope dimension, not a substitute for claim-level mapping.

## 3. Required disposition for every one of the 352 claims

Each claim must end in exactly one pre-freeze disposition:

```text
READY_FOR_PRIMARY_FREEZE
or
STOP_SOURCE_AMBIGUOUS
or
STOP_SOURCE_CONFLICT
or
STOP_OBSERVABILITY_GAP
or
STOP_IDENTITY_INCOMPLETE
```

`STOP_*` is not failure to do research. It is the required fail-closed result when the source cannot justify a unique interpretation or the current observation surface cannot support it.

A claim with `claim_status=UNKNOWN` is never converted into a guessed threshold. Its source-justified branch may preserve UNKNOWN explicitly when that is the only faithful interpretation; if a trade decision would require invented precision, the operational consequence is WAIT / NO_TRADE or a STOP disposition.

## 4. Primary branch record

Each claim-level branch must bind at least:

```text
claim_id
claim_manifest_identity
knowledge_pack_identity
source_ordinal / source anchor
claim_status
claim_category
selected_interpretation_text
interpretation_evidence_basis
family_scope
case_references
applicability_scope
no_trade_guard
invalidation_scope
management_or_exit_scope
ambiguity_preserved
unknown_ids
contradiction_ids
observability_status
observability_missing_inputs
semantic_mode
operationalization_mode
alternative_interpretation_ids_predeclared
primary_branch_version
primary_branch_identity
pre_freeze_disposition
review_evidence
```

The branch identity is deterministic over canonicalized branch content. Deterministic identity does **not** imply deterministic market decisions by the AI.

## 5. Semantic modes

A claim is classified by what the source can actually support, not by what would be convenient to backtest.

### `DIRECT_SOURCE_RELATION`
For genuinely source-pinned relations that can be represented without invented thresholds. Examples include timeframe binding, `location/bias != trigger`, `LONG_INVALID != SHORT_VALID`, and source-scoped position arithmetic where all inputs are explicit.

### `AI_CONTEXTUAL_INTERPRETATION`
For source-supported but discretionary concepts such as relative strength, key location quality, trend stage, second-push quality, breakout quality or active management. The branch freezes the interpretation boundary and inputs, not a fabricated numeric cutoff.

### `NO_TRADE_GUARD`
For source-supported negative permission: unresolved contest, range middle for main-TF swing logic, location without reaction, weakening without takeover, false breakout, unfamiliar/unsupported state, or other hard negative.

### `SOURCE_SCOPED_CASE_RULE`
For a rule or number that is valid only in a named source/case/era and must not be generalized, e.g. source-local 0.5x range sizing or a source-era 1:1 habit.

### `PRESERVE_UNKNOWN`
For unpinned or internally inconsistent semantics. No project-authored tie-break, threshold, risk percentage or proxy is allowed.

### `PROCESS_OR_AUDIT_ONLY`
For review/system-building/evidence-process claims that constrain research or audit behavior but do not directly create market permission.

## 6. Operationalization modes

```text
DETERMINISTIC_RELATION
AI_INTERPRETATION_WITH_SOURCE_GUARDS
NO_TRADE_OR_WAIT_GUARD
AUDIT_ONLY
NOT_OPERATIONALIZABLE_STOP
```

A deterministic relation may support the AI Trader without turning the entire trader into a deterministic strategy.

## 7. Family-level non-negotiable interpretation boundaries

These are aggregation constraints derived from the V1.1 dossier/family/UNKNOWN/contradiction authority. They guide claim mapping but do not replace it.

### Family A — trend key-location pullback continuation
- bind trend to a timeframe;
- pullback/context/location alone is not entry permission;
- require actual trend-direction recovery/confirmation;
- deep/accelerating counter movement or broken trend premise blocks the branch;
- no universal pullback-depth or key-zone threshold is invented.

### Family B — weakening reversal / higher-timeframe pullback
- weakening/damage of the old direction is necessary context, not sufficient entry;
- actual new-direction takeover/follow-through is required;
- intact strong trend countertrend attempts remain NO_TRADE;
- no universal acceleration/reversal threshold is invented.

### Family C — confirmed breakout
- genuine departure from old space plus follow-through/confirmation is the source boundary;
- wick-only test, rapid return or weak/no follow-through is not promoted to a true breakout;
- quantitative breakout/follow thresholds remain source-unpinned unless an individual claim explicitly pins one.

### Family D — range-boundary reversal
- confirmed range + outer boundary + failed continuation/strength conversion + counter confirmation;
- range middle is not main-TF swing permission;
- genuine breakout invalidates D and requires reclassification;
- source-era light/0.5x sizing is not generalized into a permanent D constant.

### NONE / WAIT / NO_TRADE
- `NO_TRADE` is a first-class decision;
- UNKNOWN, contradiction, unfamiliar market state, location without trigger, unresolved contest and insufficient source support may end in WAIT/NO_TRADE rather than forced LONG/SHORT.

## 8. Cross-cutting source boundaries

### Multi-timeframe
Higher/main timeframe supplies context/location; lower/execution timeframe supplies actual execution behavior where used. Same-timeframe internal structure may inform context/management but is not silently relabeled as an independent lower-timeframe setup.

### Risk
The source supports tolerated-loss/stop-distance position arithmetic in specific contexts and quality/context-based risk adjustment. It does **not** pin one universal account-risk percentage, one cross-family mother formula, one permanent range multiplier, or one exact score threshold.

### Management
Fixed R/R, key-location/space exit and dynamic structure exit are contextual alternatives. Historical/source-local preferences are not universalized. Order mode and market structure constrain management; P&L hindsight does not choose the branch.

### Evidence quality
Wrong-video subtitles, semantically failed ASR and unvalidated recovered language tracks cannot support a PRIMARY interpretation. Historical displayed P&L/R is source case content only, not project validity evidence.

## 9. Claim assignment workflow

For each claim in the exact 352-record manifest:

1. bind the original claim record and source anchor;
2. preserve EXPLICIT / INFERRED / UNKNOWN status;
3. identify applicable V1.1 family/cross-cutting authority and linked cases;
4. record all relevant UNKNOWN / contradiction constraints;
5. choose one source-justified interpretation **without outcome access**;
6. record any alternatives before outcome access;
7. determine observability from the current causal Jianghe observation surface;
8. choose semantic and operationalization modes;
9. generate deterministic branch identity;
10. mark `READY_FOR_PRIMARY_FREEZE` only if the branch is unique, source-justified, identity-complete and does not invent missing semantics; otherwise STOP.

No mapping may be chosen solely from `strategy_family_ids`, `machineability`, a title, a case outcome, or later market movement.

## 10. Pre-freeze completeness gate

Before asking the Owner to freeze PRIMARY semantics, the project must prove at minimum:

```text
CLAIM_MANIFEST_RECORDS=352
CLAIM_LEVEL_RECORDS_REVIEWED=352
UNMAPPED_CLAIMS=0
DUPLICATE_CLAIM_ASSIGNMENTS=0
HIDDEN_ALTERNATIVES=0
OUTCOME_REFERENCES_USED_FOR_BRANCH_SELECTION=0
UNKNOWN_FILLED_BY_PROJECT_GUESS=0
SOURCE_CONFLICTS_SILENTLY_RESOLVED=0
BRANCH_IDENTITIES_DETERMINISTIC=YES
KNOWLEDGE_PACK_IDENTITY_BOUND=YES
CLAIM_MANIFEST_IDENTITY_BOUND=YES
```

Any `STOP_*` claim remains visible. The project must not obtain `PRIMARY_ELIGIBLE=YES` by deleting or ignoring hard claims.

## 11. Relationship to real-model fidelity

Claim-level PRIMARY preparation and real-model fidelity are parallel prerequisites. A source-faithful branch registry does not prove that any real model can execute it faithfully. Conversely, a model that performs well on fidelity fixtures cannot repair a source-ambiguous PRIMARY branch.

The full pre-outcome research object later binds:

```text
frozen claim-level PRIMARY branches
+ knowledge pack identity
+ verified/adopted model-provider version
+ prompts/context/memory/renderer/observation/wake/normalizer/inference/tool identities
+ deterministic hard-risk/execution envelope
= versioned JiangheAITraderIdentity
```

## 12. Current boundary of this artifact

This artifact is **pre-freeze preparation only**. It creates no PRIMARY promotion and grants no candidate-outcome, Validation, Final, Shadow, Broker or real-money permission. Final PRIMARY semantic freeze remains an Owner-gated action under the collaboration contract.

Machine-readable companion: `JIANGHE_PRIMARY_BRANCH_PREPARATION_SCHEMA_V0_1.json`.
