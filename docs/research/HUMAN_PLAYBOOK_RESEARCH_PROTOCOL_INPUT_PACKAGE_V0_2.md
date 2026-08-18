# HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_2

> Date: 2026-08-19
> Status: REVISED_AFTER_ADVERSARIAL_REVIEW / OWNER_DECISION_CANDIDATE / NOT_FROZEN
> Supersedes as freeze candidate: `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_1.md`
> Independent review: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADVERSARIAL_REVIEW_V0_1.md`
> Project-brain adjudication: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADJUDICATION_V0_1.md`
> Binding direction: `RESEARCH_DIRECTION.md`
> Architecture: `ARCHITECTURE_BASELINE.md` Skeleton v1.0

This document is the revised decision candidate. It is still NOT frozen and does not authorize concrete playbook extraction, backtesting, final-unseen access, Shadow/live trading, or real-money actions.

## 1. Five-bucket protocol structure

The freeze candidate is intentionally reduced to five operational buckets:

1. source / claim;
2. interpretation / search freedom;
3. lineage / exposure;
4. observability;
5. validation / final acceptance.

## 2. Source / claim governance

Candidate freeze rules:

- source claim, project/AI interpretation, and machine operationalization are separate immutable layers;
- claim status vocabulary: `EXPLICIT / INFERRED / UNKNOWN`;
- original/nearest-original attributable material is preferred for `EXPLICIT` claims;
- derivative/repost material may be used with degraded provenance but cannot masquerade as original authority;
- discovery-only records such as rankings cannot create playbook claims by themselves;
- performance/testimonial claims remain separate from validity evidence;
- missing source meaning remains `UNKNOWN` rather than guessed.

## 3. Interpretation / search-freedom governance

### 3.1 PRIMARY_BRANCH rule

Before any backtest, every source-faithful claim must have exactly one `PRIMARY_BRANCH` selected from source evidence alone.

If a unique primary interpretation cannot be justified before seeing outcomes:

`AMBIGUOUS / INSUFFICIENTLY_OPERATIONALIZED -> STOP`

The project may preserve alternatives as research notes, but the claim is not yet eligible for source-faithful confirmatory validation.

### 3.2 Operationalization identity

Every tested branch has a deterministic operationalization identity/hash covering outcome-affecting logic, features, parameters, scope and context.

```text
same operationalization hash -> same branch
changed operationalization hash -> new branch/search freedom
```

Alternative branches cannot rescue a failed primary and still be reported as validation of the original source claim.

### 3.3 Pre-backtest lock

Before testing, lock:
- primary branch hash;
- declared alternative branch hashes;
- instrument scope;
- timeframe scope;
- context/regime scope;
- parameter/search ranges;
- materially relevant AI prompt/specification version.

Post-lock additions are descendants and inherit exposure. Failed branches cannot later be removed from search-freedom accounting.

## 4. Lineage / exposure governance

### 4.1 Lineage

Renaming does not reset lineage or exposure.

Family identity binds a mechanism-level signature over outcome-affecting logic/inputs/context plus available provenance evidence.

Lineage review uses, where available:
- explicit attribution;
- source chronology;
- unusual shared vocabulary/mechanism structure;
- parent/descendant derivation;
- shared operationalization components.

Similarity alone is not proof of hidden genealogy, but unresolved dependence is not counted as independent confirmation.

### 4.2 Source-example exposure

The exposure bound uses the **effective content/version date**.

```text
if effective_content_date < protected_window_start
-> material cannot contain future examples from that protected window
-> no example-date audit needed for that window

else
-> example-date exposure audit required
```

Exposure includes:
- charts/visuals showing dates/outcomes;
- written dated examples;
- verbal descriptions of dated outcomes;
- derivative/repost inherited exposure plus new-content exposure.

Unknown dates fail closed only for the affected material/family protected window, not unrelated source content.

Family exposure is irreversible once protected outcomes are observed.

## 5. Observability governance

Before operationalization ask:
1. what did the human source actually observe?
2. is that input available point-in-time in project data?
3. is a substitute justified from source semantics/measurement logic before outcome testing?
4. if not, should the claim remain untestable?

Allowed states:
`OBSERVABLE_NOW / PARTIALLY_OBSERVABLE / NOT_OBSERVABLE_WITH_CURRENT_DATA / UNKNOWN / NOT_APPLICABLE`.

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

## 7. Common acceptance contract

Family-specific metric shopping is not allowed.

All families face the same core questions:

1. **Economic edge:** after pre-registered costs/slippage, does the PRIMARY branch show positive net economic edge with uncertainty treated explicitly?
2. **Evidence sufficiency:** does it meet the pre-registered common sufficiency procedure (events, distinct trading days, dependence-aware aggregation/cluster treatment)?
3. **Risk/failure constraints:** do required pre-registered risk/failure checks pass?
4. **Chronology/exposure integrity:** was the evidence obtained without violating split/exposure/search rules?

Family-specific metrics may be added only as extra constraints/diagnostics. They cannot replace these common questions and cannot be changed after validation exposure.

The protocol must not assume six products equal six independent samples. Dependence is measured using development-only diagnostics; no unverified fixed effective-product count is frozen.

Failure to meet evidence sufficiency produces:

`INSUFFICIENT_EVIDENCE`

not a relaxed threshold or changed split.

Exact numeric implementation of confidence/precision and minimum-event rules remains part of the freeze implementation specification and must be pre-registered before any family opens validation.

## 8. Chronological split candidate

Canonical corpus: 2024-01-01 .. 2025-12-31.

### Leading candidate: 12 / 6 / 6

- Development: 2024-01-01 .. 2024-12-31
- Validation: 2025-01-01 .. 2025-06-30
- Final-unseen: 2025-07-01 .. 2025-12-31

Why it remains preferred:
- simplest auditable calendar split;
- full first year for development/debugging;
- equal validation/final reserves;
- easiest source-example exposure bookkeeping.

Known limitations:
- sparse playbooks may be underpowered;
- half-year regime/seasonality concentration;
- correlated products reduce effective independence;
- final is one exam cohort, not timeless proof.

Policy consequence: honest `INSUFFICIENT_EVIDENCE` is expected and acceptable.

### Alternative: 10 / 8 / 6

Keeps the same final reserve but moves two months from development to validation. This may help moderate-frequency families but reduces contextual development history and creates less intuitive boundaries.

### Rolling validation

Not recommended for the first freeze. With only 24 months it creates repeated looks/search freedom without enough independent blocks to justify the complexity.

No split is frozen until Owner approval.

## 9. Validation revision policy

Before validation: artifact/specification/metrics/scope are locked.

After validation exposure:

### CAT1_IMPLEMENTATION_DEFECT
Objective mismatch against an already unambiguous pre-registered specification. Repair restores the original specification and changes no intended research logic.

- deterministic/independent evidence of defect and repair required;
- at most one same-validation rerun per family/epoch;
- full audit record required.

### CAT2_RESEARCH_LOGIC_CHANGE
Any intended logic/parameter/context/interpretation change.

- new descendant;
- inherits validation exposure;
- same validation cannot be fresh confirmation.

### CAT3_SPECIFICATION_AMBIGUITY
If validation results were needed to decide what the specification meant, treat as CAT2.

Unknown classification defaults to CAT2.

## 10. Final-unseen state machine

```text
FINAL_UNSEEN_LOCKED
-> FINAL_EXPOSED
-> FINAL_ACCEPTED | FINAL_REJECTED | FINAL_VOID_IMPLEMENTATION_DEFECT
```

Rules:
- exposure is irreversible;
- `VOID` means result is inconclusive because implementation violated the pre-registered specification; it does not restore unseen status;
- final-inspired descendants inherit exposure and must wait for genuinely new unseen evidence;
- no tuning and rerunning the same final window;
- future Shadow/Forward data is the intended fresh-evidence path.

Final pass supports acceptance for that tested cohort; it is not proof of permanent validity.

## 11. Final unlock structural gates

Before final access:
- provenance / claim / PRIMARY interpretation review complete;
- observability resolved;
- lineage/mechanism signature/exposure record complete;
- deterministic artifact/code/parameter/environment identity frozen;
- development + validation evidence complete;
- search freedom locked/accounted;
- common acceptance contract passes;
- relevant execution realism prerequisites satisfied;
- required independent review passed.

## 12. Technical-debt activation

Not blockers for protocol freeze itself:
- TD-001;
- TD-002;
- LIMIT-001.

They become blockers before the corresponding confirmatory/final-quality evidence relies on their affected semantics.

## 13. What remains Owner-gated

Material freeze decisions now reduce to:

1. approve the five-bucket governance above, including PRIMARY_BRANCH, exposure inheritance, observability/surrogate rules, common acceptance contract and validation/final state rules;
2. choose the initial chronological split: recommended `12/6/6`, alternative `10/8/6`;
3. approve that `INSUFFICIENT_EVIDENCE` is a valid non-failure outcome when the 24-month corpus cannot support a family cleanly.

## 14. Freeze status

`OWNER_DECISION_REQUIRED / NOT_FROZEN`

Until Owner approval, strategy research remains not authorized.