# SECOND_PASS_REPAIR_RETROSPECTIVE_1_ADVERSARIAL_INTEGRATION_2026-08-20

> Date: 2026-08-20
> Role: project-brain first mandatory retrospective before second-pass repair closure
> Status: CORRECTION_REQUIRED_BEFORE_CLOSURE
> Candidate outcome access: NOT_AUTHORIZED / NOT_USED

## 1. Scope reviewed

This retrospective re-opened the most recent four-lane outputs against the real integrated repository rather than accepting worker chat summaries:

- R2 E-04/E-05/E-08 engineering + E-07 fail-closed integration;
- final bounded E-06 official-static evidence pass;
- all-at-once F/G/H semantic decision proposal;
- Codex deterministic F/G/H rebuild and combined synthetic causal chain.

The R2 foundation was already accepted and integrated before these four lanes. The review preserved the frozen Human Playbook First direction, Protocol v1.0, 12/6/6 chronology, and all candidate/Validation/final-holdout/Shadow locks.

## 2. Accepted integration facts

### Package E

E-04 implements the Owner-approved explicit bucket-child-order rule; generic cross-bucket CLOSE cannot silently auto-split.

E-05 binds capital assumptions per strategy member and resolved concrete contract; the portfolio candidate outcome path remains fail-closed.

E-08 binds `AVAILABLE_CAPITAL_ONLY` into the capital-assumption identity and open/add admission path.

E-07 correctly records `LOGIN_REQUIRED`, `INCOMPLETE`, and `FAIL_CLOSED_PREREQUISITE`; no project-authored OI/volume/calendar/PnL substitute was introduced.

### E-06

The final bounded SHFE static-official pass added additional byte-bound official evidence but did not overclaim completeness. Remaining exchange-level fee/margin gaps are now a long-lived governed prerequisite. Default repeated acquisition is closed until an official-source/access/policy trigger changes.

### F/G/H

The Codex rebuild correctly avoided merging the obsolete old F/G/H branches. It rebuilt generic feature/trigger machinery on the repaired foundation, added source-faithful Holy Grail V0.2 draft artifacts, and kept the draft `NOT_MACHINE_READY`. The implementation does not create a Holy Grail StrategyIdentity, register an OutcomeTest, or access candidate outcomes.

The separate semantic package enumerated all remaining Holy Grail decisions at once. Project-brain recommendations were subsequently frozen by Owner authority in `FGH_SEMANTIC_GATE_OWNER_APPROVAL_2026-08-20.md`; the trailing-stop machine definition intentionally remains not adopted until source-pinned or separately re-approved.

## 3. HIGH correction found: AggregationResult normal-construction laundering

### Finding

`src/technical_features.py` defines `AggregationResult` with `init=False`, which blocks the ordinary dataclass constructor. However it also exposes the classmethod:

```text
AggregationResult._from_aggregation(...)
```

A normal caller can therefore take a real incomplete aggregation result, drop its `incomplete_buckets`, replace `expected_bucket_identities` with only the retained complete buckets, and call `_from_aggregation` directly. The resulting object satisfies its own structural `__post_init__` checks and can be passed to `compute_ema` / `compute_adx` as if the gap never existed.

This re-opens the exact L-12 failure mode the rebuild was intended to close: caller-side discarding of incomplete bucket evidence and time compression.

### Severity

```text
SEVERITY=HIGH
CLASS=IMPLEMENTATION_TRUST_BOUNDARY_BYPASS
CANDIDATE_OUTCOME_EXPOSURE=NO
MUST_FIX_BEFORE_REPAIR_CLOSURE=YES
```

It is analogous to the earlier Package B caller-accessible `_build()` defect: a leading underscore is not sufficient authority in Python when the method itself constructs trusted evidence.

### Required bounded correction

Feature computation must accept only an `AggregationResult` actually issued by `TimeframeAggregator.aggregate()` in the current process. A private in-memory issued-object registry is sufficient for the project's current boundary; OS/process/local-state tamper-proofing remains explicitly unproven and must not be claimed.

Required regression:

1. produce an incomplete result using the real aggregator;
2. call `_from_aggregation` manually with incomplete evidence removed;
3. verify feature computation rejects it as not aggregator-issued;
4. verify a real aggregator-issued complete result still computes normally.

No new framework or durable registry is needed.

## 4. Navigation/handoff defect found

`00_READ_FIRST.md` still contains a stale current-state summary from the earlier statistical-profile/takeover phase. It correctly says `CURRENT_STATE.md` is status authority, but its duplicated current-work summary and recorded next action are stale and can mislead a fresh conversation.

```text
SEVERITY=MEDIUM
CLASS=AUTHORITY_NAVIGATION_STALENESS
MUST_FIX_BEFORE_HANDOFF=YES
```

Closure must replace stale current-work prose with the repair-closure state and keep the fresh-conversation first-turn read-only verification rule.

## 5. Stop/OCO recheck

The completed-bar stop model and OCO lifecycle were re-read. The implementation materializes generators once, binds evaluated bar prefixes, binds implementation bytes, cancels siblings after an unambiguous first trigger, and preserves same-bar ambiguity.

When multiple OCO members have non-orderable events in one completed bar, the group returns ambiguity rather than inventing an ordering. This is conservative and consistent with the frozen fail-closed direction. No new implementation correction is authorized from this retrospective without a concrete contradictory invariant.

## 6. Explicit residual boundaries that are not repair defects

The following are not to be silently “fixed” with invented facts:

- E-06 complete 2024-2025 exchange-level fee/margin schedule: evidence incomplete;
- E-07 historical TqSdk vendor mapping: login required under current source policy;
- Holy Grail trailing-stop machine algorithm: source not pinned, remains a research prerequisite;
- `BASE` timeframe still needs an explicit concrete interval before a machine-ready contract;
- project product transfer remains `INFERRED` unless later governed research upgrades it;
- SOURCE_ONLY OS/process sandbox and local state tamper-proofing are not proven;
- end-to-end proof that execution consumed exact artifact bytes remains stronger than current binding guarantees.

These residuals must remain explicit and fail closed where relevant. They do not justify reopening candidate outcomes.

## 7. Retrospective-1 decision

```text
RETROSPECTIVE_1=CORRECTION_REQUIRED
CORRECTION=AGGREGATION_RESULT_ISSUANCE_GUARD
HANDOFF_FIX=00_READ_FIRST_REFRESH
OPEN_ENDED_REPAIR_LOOP=NO
NEXT=APPLY_BOUNDED_GUARDRAIL_THEN_RUN_RETROSPECTIVE_2_AND_FINAL_62_FINDING_CLOSURE_AUDIT
```
