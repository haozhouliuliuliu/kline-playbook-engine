# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1

> Date: 2026-08-19
> Role: project-brain adjudication after independent parallel review
> Status: `ADJUDICATION_COMPLETE / PROFILE_NOT_LOCKABLE_YET / NO_OUTCOME_DATA_USED`
> Frozen authority unchanged: Research Protocol v1.0 + 12/6/6 chronology

## 1. Evidence reviewed

Primary candidate:
- `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
- design commit: `6ef668fd7214fcef2f12b71cb3e9ea2a36bfcaf7`

Integrated engine capability audit:
- `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`
- original parallel commit: `c34cebde4307eb2d532886ed8da94e2985323ede`
- cherry-picked main commit: `4946b0db2692a06ff6965efedb242156ab52e886`

Independent engine-compatibility crosswalk (parallel branch evidence):
- branch: `parallel/stat-engine-audit`
- commit: `05ad7f9a94c1a6b885402a4417a0d095dbfa7c56`
- document: `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK.md`

Independent adversarial statistical review (parallel branch evidence):
- branch: `parallel/stat-profile-review`
- commit: `5e78605d312ee2e6c22e82dc4d91d651eacac4b2`
- document: `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md`
- verdict: `GO_WITH_REQUIRED_CHANGES`
- findings: 3 CRITICAL, 6 HIGH

No real Human Playbook candidate outcome, candidate PnL, validation outcome, or historical-final outcome was used by the design, crosswalk, review, or this adjudication.

## 2. Overall adjudication

```text
PROFILE_V1_CANDIDATE_DIRECTION=KEEP
CURRENT_CANDIDATE_LOCKABLE=NO
FROZEN_PROTOCOL_CONFLICT=NO
OWNER_GATE_REQUIRED_NOW=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
```

The candidate's core governance direction remains useful: one common profile, pre-outcome lock, dependence-aware inference, whole-wave multiplicity, deterministic rules, and `INSUFFICIENT_EVIDENCE` as a legitimate result. The current numerical/method draft must not be locked because the independent review identified real defects and the engine crosswalk identified unresolved definitions.

All required corrections can be made inside the not-yet-frozen Common Statistical Profile without changing Research Protocol v1.0 or the frozen chronology. Therefore this is a normal project-brain adjudication/revision path, not a new Owner research-semantics gate at this time.

## 3. CRITICAL findings — adjudication

### C-1 — power / detectability and false precision

**Decision: ACCEPT.**

The current draft mixes an economic edge floor with significance/sufficiency rules without first showing what effect sizes the frozen 6-month validation cohort can realistically distinguish. A profile that mostly returns `INSUFFICIENT_EVIDENCE` may still be valid, but it must not imply that insufficient power means no edge.

Required revision:
- publish a predeclared no-outcome-data power/precision capacity interpretation;
- explicitly separate `economic materiality` from `statistical detectability`;
- define `INSUFFICIENT_EVIDENCE` as inability of the available cohort/profile to resolve the required claim, not evidence of no edge;
- do not tune thresholds after candidate outcomes are seen.

This does **not** create a requirement that sparse playbooks must pass. Sparse playbooks may legitimately remain `INSUFFICIENT_EVIDENCE` under Protocol v1.0.

### C-2 — `ESS = N / max(1, 2H-1)` as a hard gate

**Decision: ACCEPT. Remove from the lock candidate as a deterministic hard sufficiency formula.**

The formula embeds an unstated dependence model and creates false precision. Holding horizon remains useful structural information, but `2H-1` must not determine PASS/FAIL/INSUFFICIENT as if it were an exact effective sample size.

Required revision:
- remove the current `2H-1` ESS hard gate;
- retain holding-horizon/overlap information as a dependence diagnostic/input;
- choose one predeclared dependence-aware inference/sufficiency procedure that does not claim a model-dependent ESS heuristic is exact.

The exact replacement is still a design task; this adjudication does not silently choose one.

### C-3 — incomplete round-trip / holding / block semantics

**Decision: ACCEPT, with the engine crosswalk supplying the implementation-compatible identity.**

The revised candidate must explicitly define:
- one engine `position_id` = one completed round-trip observation;
- multiple opening legs/adds remain inside that one observation;
- partial-close legs are aggregated into that one observation and do not increase `N`;
- full close ends the observation;
- forced liquidation is a terminal close for the observation and separately triggers the applicable failure/risk fact;
- a contract roll cannot silently continue one observation across concrete contracts; each concrete-contract position remains its own round trip;
- holding horizon convention must be explicit and use `SessionMetadata` as the trading-day authority;
- cross-week/multi-week position attribution for dependence inference must be explicitly defined before profile lock.

The engine can support these identities with a small round-trip-ledger materialization; no new framework is required.

## 4. HIGH findings — adjudication

### H-1 — current fixed sufficiency numbers

**Decision: ACCEPT AS A REVISION REQUIREMENT, not as proof that every current number is wrong.**

`N>=60`, distinct-day/week minima, concentration thresholds, and `open_ratio` are currently candidate heuristics, not accepted truths. The revised profile must either justify each surviving hard threshold in relation to the intended evidence claim or simplify/remove redundant knobs. No threshold may be calibrated from candidate outcomes.

### H-2 — fixed `2x cost/friction` rule

**Decision: ACCEPT.**

The engine crosswalk confirms that additive fees and slippage are different objects. A post-hoc `2x cost` formula can deterministically stress additive fees, but it does not automatically stress slippage or all execution friction.

Required revision:
- stop describing fee doubling as universal friction doubling;
- define exactly what is stressed;
- preserve pre-registered base execution assumptions;
- if sensitivity bands are reported, label them diagnostics unless a hard gate is separately justified before outcomes.

### H-3 — time-window concentration / extreme-winner dependence

**Decision: ACCEPT IN PRINCIPLE.**

The common profile needs a simple deterministic guard against an apparent edge being carried by one event or one narrow time window. The final exact statistic/threshold remains part of candidate revision; do not invent it from outcomes.

### H-4 — governed data gap state

**Decision: ACCEPT.**

Add an explicit `DATA_BLOCKED` or equivalently unambiguous data-governance disposition distinct from:
- `FAIL` (evidence against the hypothesis), and
- `INSUFFICIENT_EVIDENCE` (available governed sample cannot resolve the claim).

`LIMIT-001` is the current concrete example: missing required governed price-limit facts block affected confirmatory evidence generation; they are not permission to fill through the limit and not evidence that a strategy failed.

### H-5 — multiplicity counting taxonomy

**Decision: ACCEPT.**

The final profile must make the statistical hypothesis count machine-consistent with the frozen Research Wave/search identities. It must prevent both:
- over-counting purely nuisance implementation detail as independent hypotheses; and
- laundering real search freedom by collapsing materially distinct branches/parameter searches into one count.

Holm FWER remains the leading simple v1 default because it is deterministic and conservative, but it is **not yet locked**. The revised candidate must state the exact error-rate target and counting taxonomy.

### H-6 — Romano-Wolf description

**Decision: ACCEPT editorial/methodological correction.**

The revised candidate must accurately describe Romano-Wolf stepdown. This correction does not itself require adopting Romano-Wolf for v1.

## 5. Engine crosswalk findings — accepted facts

The following are accepted engineering facts for the next profile revision/implementation package:

- existing engine records realized PnL, costs, instrument/contract identities, timestamps, trading-day identity, and deterministic `position_id` lifecycle sufficient to materialize the proposed round-trip ledger;
- round-trip ledger/day-week aggregation/holding-horizon helpers are missing but are small deltas;
- `open_ratio` denominator/cohort-boundary semantics are not yet pinned;
- holding-horizon counting convention is not yet pinned;
- fee stress and slippage stress are not the same operation;
- Research Wave denominator/profile identities are already machine-bound, but the final statistical counting taxonomy must align with them;
- TD-001 requires all new day/week statistics to use `SessionMetadata`, not the bootstrap calendar;
- TD-002 does not corrupt final realized round-trip PnL but does corrupt partial-close equity/unrealized/drawdown paths until fixed;
- LIMIT-001 is fail-closed data/governance debt for affected real confirmatory PnL, not silent PnL corruption;
- multi-day portfolio/equity series is a medium engineering delta and is **not** required merely to revise the common trade-level primary estimand; it becomes required before evidence claims depend on portfolio-day/equity-path diagnostics.

## 6. What is deliberately NOT decided here

This adjudication does not lock:
- the final primary-estimand formula beyond the round-trip identity boundary above;
- final minimum trade/day/week counts;
- final block/bootstrap procedure or block-length rule;
- final cost-stress multiplier;
- final concentration thresholds;
- final Holm/other multiplicity method;
- final numeric acceptance thresholds.

Those belong in the revised Common Statistical Profile candidate, still before any candidate outcome inspection.

## 7. Next bounded package

```text
CURRENT_NEXT_ACTION=REVISE_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE_FROM_ADJUDICATED_REVIEW
PROFILE_STATUS=CANDIDATE_REVISION_REQUIRED_NOT_LOCKED
TOOL_DECISION=USE_EXISTING
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
OWNER_ACTION=NONE
```

The next package should revise the candidate and design evidence in one coherent pass, then run a **targeted delta independent review** only over materially changed statistical definitions. Do not repeat the entire project review. Implementation of the round-trip ledger/statistical evaluator should wait until the revised profile survives that targeted review, except for purely non-semantic helpers that are independently useful and cannot bias the profile decision.
