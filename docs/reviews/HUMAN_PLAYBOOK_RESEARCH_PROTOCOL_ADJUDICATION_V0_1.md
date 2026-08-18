# HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADJUDICATION_V0_1

> Date: 2026-08-19
> Status: PROJECT_BRAIN_ADJUDICATION / NOT_FROZEN
> Reviewed evidence: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADVERSARIAL_REVIEW_V0_1.md`
> Input package under revision: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_1.md`
> Binding direction: `RESEARCH_DIRECTION.md`
>
> This adjudication accepts, modifies, or rejects reviewer recommendations. It does not freeze research semantics, select final split dates, authorize real claim extraction, backtesting, final-unseen access, or live trading.

## 1. Overall verdict

`ADVERSARIAL_REVIEW_ACCEPTED_WITH_PROJECT_BRAIN_MODIFICATIONS`

The review successfully identified protocol-level vulnerabilities without exposing a fatal flaw in Human Playbook First or Skeleton v1.0. The project should revise the input package before Owner freeze.

## 2. CRITICAL adjudication

### C-1 PRIMARY_BRANCH — ACCEPT, strengthened

Accept the core finding.

Required rule for the freeze candidate:

```text
SOURCE-FAITHFUL CLAIM
-> exactly one PRIMARY interpretation chosen from source evidence alone before any backtest
-> deterministic machine operationalization hash locked before any backtest
```

If the source alone cannot justify one primary interpretation without looking at outcomes, the claim is not eligible for source-faithful confirmatory validation yet. It remains `AMBIGUOUS / INSUFFICIENTLY_OPERATIONALIZED`.

Alternative interpretations may be registered as sensitivity/exploratory branches, but:
- they cannot rescue a failed primary branch and still be called validation of the original human claim;
- all pre-registered alternatives count as search freedom;
- a post-result interpretation is a new exposed descendant.

This is stricter and simpler than trying to decide whether small wording edits are material. Operationalization identity, not prose similarity, defines a branch.

### C-2 acceptance gates / metric shopping — PARTIALLY ACCEPT

Accept the metric-shopping criticism. Reject a universal one-size-fits-all trading metric/threshold as the sole solution.

Reason: trend-following, mean-reversion, sparse-event and high-frequency playbooks can have materially different event distributions and risk structures. Forcing all families to use one Sharpe/win-rate/etc. threshold would create false comparability.

Freeze candidate should instead use a **COMMON ACCEPTANCE CONTRACT**:

Mandatory global questions:
1. after pre-registered costs/slippage, is the primary branch's net economic edge positive with uncertainty treated explicitly?
2. is pre-registered evidence sufficiency met?
3. do pre-registered risk / failure constraints pass?
4. does the result survive the required chronology/exposure rules?

Family-specific metrics may be added only as extra constraints/diagnostics. They may not replace the common contract, and they may not be changed after validation exposure.

A family cannot choose a convenient metric as a substitute for the common primary evidence question.

### C-3 source-example leakage — ACCEPT WITH VERSION-DATE CORRECTION

Accept the executable exposure mechanism, with one correction: the relevant bound is the **effective content/version date**, not blindly the original publication date.

Examples:
- an unchanged 2011 book cannot contain 2025 examples;
- a 2011 book reissued/expanded in 2025 may contain new 2025 examples;
- a blog page may have an old publication date but later edits.

Freeze candidate:

```text
if effective content/version date < protected_window_start
-> source cannot contain examples from that future protected window
-> no example-date audit required for that protected window

otherwise
-> example-date exposure audit required
```

Exposure includes chart/date displays, textual examples, and verbal outcome descriptions. Derivative/repost material inherits original exposure plus added-content exposure.

Unknown example dates fail closed only for the affected material/family protected window, not the entire source corpus.

## 3. HIGH adjudication

### H-1 effective sample size / INSUFFICIENT_EVIDENCE — ACCEPT PRINCIPLE, REJECT UNVERIFIED 2-3 NUMBER

Accept that six products are not automatically six independent samples. Do not freeze the reviewer's estimate of `2-3` effective products; that number was not established by project evidence.

Freeze candidate:
- product count is never used as independence count by assumption;
- development-only correlation/regime diagnostics estimate dependence before confirmatory interpretation;
- evidence sufficiency uses pre-registered event counts, distinct trading days, and dependence-aware clustering/aggregation appropriate to the family;
- failure to meet sufficiency -> `INSUFFICIENT_EVIDENCE`, never threshold relaxation after seeing results.

Exact numeric minimum event requirements remain to be specified in the freeze package as a common procedure/rule, not guessed ad hoc for each winner.

### H-2 validation bug vs research revision — ACCEPT WITH STRONGER FAIL-SAFE

Adopt:
- `CAT1_IMPLEMENTATION_DEFECT`: objective mismatch against an already unambiguous pre-registered specification; repair restores the original specification. Same validation may be rerun once only if defect and repair are independently/deterministically demonstrated and logged.
- `CAT2_RESEARCH_LOGIC_CHANGE`: any change to intended logic/parameters/context/interpretation -> new descendant; validation remains exposed.
- `CAT3_SPECIFICATION_AMBIGUITY`: if seeing validation was needed to decide what the specification meant -> treat as CAT2.
- unknown/unproven classification defaults to CAT2.

CAT1 is not a license for iterative debugging on validation. Development remains the debugging arena.

### H-3 final-unseen state machine — ACCEPT

Freeze candidate states:

```text
FINAL_UNSEEN_LOCKED
-> FINAL_EXPOSED
-> FINAL_ACCEPTED | FINAL_REJECTED | FINAL_VOID_IMPLEMENTATION_DEFECT
```

`VOID` changes the conclusion, never restores unseen status. Any descendant inspired by final results inherits exposure and must wait for genuinely new unseen evidence (for example future Shadow/Forward data).

### H-4 lineage mechanism signature — ACCEPT WITH CAUTION

Accept the need for a mechanism-level identity stronger than names.

Do not pretend hidden teacher/student lineage can always be detected. Protocol should use available evidence:
- explicit citations/attribution;
- unusual shared vocabulary or mechanism structure;
- source chronology;
- shared operationalization components;
- direct parent/descendant derivation.

Family identity should bind a `mechanism_signature` over outcome-affecting logic/inputs/context, but similarity alone is evidence for review, not automatic proof of genealogy.

Renaming never resets exposure.

### H-5 surrogate rule — ACCEPT

A substitute feature must be justified from source semantics/measurement logic **before outcome testing**. A surrogate discovered because it backtests better is a new inferred branch and counts as search freedom; it cannot be labeled source-equivalent.

### H-6 enumeration/hash/search freedom — ACCEPT, simplify

Before any backtest, lock:
- primary operationalization hash;
- declared alternative branch hashes;
- instrument/timeframe/context scope;
- parameter/search ranges if any;
- prompt/specification version used to generate interpretations when AI contributes materially.

Post-lock additions are descendants with inherited exposure. Do not reduce the recorded search count by later merging failed branches.

## 4. Split adjudication

Independent review does not disqualify `12/6/6`; it correctly shows that split choice cannot cure low event counts or correlated products.

Project-brain recommendation for Owner decision remains:

`12 / 6 / 6` as the leading freeze candidate because it is the simplest to audit and preserves a full calendar year for development plus equal validation/final reserves.

But the interpretation changes:
- a window is an exam cohort, not a promise of statistical power;
- `INSUFFICIENT_EVIDENCE` is a normal outcome;
- no date boundary may be relaxed after seeing results;
- final is one protected exam, not proof of timeless validity;
- future Shadow/Forward evidence is the path for later fresh confirmation.

`10/8/6` remains a legitimate alternative if Owner prefers more validation history at the cost of development breadth.

Rolling validation is not recommended for the first frozen protocol because 24 months is too short and repeated looks create unnecessary tuning freedom.

## 5. Over-governance adjudication

Accept the reviewer's simplification direction.

Keep the safety-critical rules, reduce form burden:
- family-level exposure record + exception/example-date list; claim records reference it;
- fields may be `UNKNOWN` / not-applicable rather than fake precision;
- source anchor + short excerpt/paraphrase/context is sufficient; do not require redundant prose fields everywhere;
- group the protocol into five operational buckets:
  1. source/claim;
  2. interpretation/search;
  3. lineage/exposure;
  4. observability;
  5. validation/final acceptance.

Do not simplify away PRIMARY_BRANCH, common acceptance contract, exposure inheritance, chronology, or search enumeration.

## 6. Technical-debt timing

Agree with reviewer:
- TD-001, TD-002, LIMIT-001 do not block protocol freeze;
- they must activate before the relevant confirmatory/final-quality evidence claims depend on them.

## 7. Minimum revised package

Before Owner freeze decision, the revised package must include:
1. PRIMARY_BRANCH and ambiguity stop rule;
2. common acceptance contract (not family metric shopping);
3. effective-content-date source exposure mechanism;
4. operational `INSUFFICIENT_EVIDENCE` principle with dependence-aware sufficiency;
5. validation CAT1/CAT2/CAT3 rules;
6. final state machine / irreversible exposure;
7. mechanism signature / lineage rules;
8. surrogate pre-justification;
9. pre-backtest branch/scope/prompt hash lock;
10. a simple split recommendation with explicit limitations.

## 8. Freeze status

`NOT_FROZEN`

This adjudication makes the package ready for a revised v0.2 and a minimal Owner decision package. It does not itself authorize strategy research.