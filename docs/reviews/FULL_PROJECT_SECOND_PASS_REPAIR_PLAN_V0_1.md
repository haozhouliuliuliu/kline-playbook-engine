# FULL_PROJECT_SECOND_PASS_REPAIR_PLAN_V0_1

> Date: 2026-08-20
> Status: ACTIVE / PROJECT_BRAIN_REPAIR_ORCHESTRATION
> Findings authority: `docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md`
> Research direction: HUMAN_PLAYBOOK_FIRST
> Candidate outcomes: NOT_AUTHORIZED
> Tool decision: USE_EXISTING

## 1. Purpose

Turn the second-pass audit into a dependency-ordered repair program without allowing a worker to redesign unrelated parts of the project.

This plan is intentionally narrow and sequential. Foundational trust-boundary repairs are not parallelized because later packages depend on their exact semantics.

```text
REPAIR_EXECUTION_MODE=SINGLE_INTEGRATION_LANE_SEQUENTIAL_FOUNDATION_FIRST
PARALLEL_FOUNDATION_REPAIR=NO
MAIN=SOLE_INTEGRATION_AUTHORITY
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
```

## 2. Repairs already completed directly by project brain

### R-PB-01 — durable accepted-wave evidence refs

Created repository refs:

```text
evidence/wave1-accepted-raw-20260819 -> b68da256bbc493ac6e1de0fe02b7fde5a0396ddf
evidence/wave2-accepted-raw-20260819 -> c0fef50bb3b0f5a97c7bdf472d5a9e2d9339273a
```

Purpose: preserve exact accepted worker evidence commits independently of ordinary worker-branch cleanup. Integration reviews on main remain the semantic authority and continue to override rejected worker statements.

This closes the immediate branch-reachability part of audit S-03. It does not retroactively byte-bind external source pages and does not upgrade SOURCE_ONLY attestation strength.

## 3. Repair order

### Package A — candidate execution trust boundary

Target findings:

```text
F-01 F-02 F-03 F-04 F-05 F-11
```

Goal: there must be no production-like runner/portfolio path that can execute candidate/validation outcome logic from a legacy coarse grant, caller-declared cohort, unbound bars, or arbitrary real-profile object.

Package A is the first DS package. No Playbook redesign, canonical rebuild, feature work, execution realism, or F/G/H integration belongs here.

### Package B — artifact / lineage / source / durable governance binding

Target findings:

```text
F-06 F-07 F-08 F-09 F-10 F-12 F-13 P-06
```

Goal: replace internally-consistent opaque labels with bindings to actual project artifacts where required; make exposure/locks reconstructable and prevent lineage/profile/session laundering.

Do not start until Package A is integrated and re-audited.

### Package C — Playbook Contract protocol invariants

Target findings:

```text
P-01 P-02 P-03 P-04 P-05
```

Goal: make machine readiness derive from claim/field-level PRIMARY, ambiguity, observability, transfer and timeframe semantics instead of caller self-attestation.

No Holy Grail-specific outcome logic in this package.

### Package D — canonical completeness / provenance

Target findings:

```text
D-01 D-02 D-03 D-04 D-05 D-06 D-07 D-08
```

Goal: make canonical acceptance prove requested-session completeness and bind the intended provenance/session identities. Re-audit the already accepted corpus without silently replacing it or claiming corruption before evidence exists.

No candidate outcomes.

### Package E — execution / capital / portfolio / round-trip

Target findings:

```text
E-01 E-02 E-03 E-04 E-05 E-08 E-09 E-10 E-11 E-12 E-13
```

`E-06` historical realistic fees/margins and `E-07` concrete-contract research mapping are separate research/evidence design prerequisites, not ordinary bug fixes; they remain fail-closed blockers until their own governed package is approved/defined from source/data authority.

### Package F — source-evidence hardening

Target findings:

```text
S-01 S-02 S-04
```

S-03 immediate ref-durability is already handled by R-PB-01. Source byte hashes can only bind newly/re-fetched material; they must not be misrepresented as proof of bytes seen in an earlier session if no historical byte hash exists.

### Package G — latest F/G/H correction and combined regression

Only after Packages A-E have established the lower-level contracts, return to:

```text
L-01 .. L-18
```

Do not patch the three old lanes in isolation against obsolete lower-level assumptions. Rebase/reconstruct only the necessary parts on the repaired foundation, then run one combined integration regression.

## 4. Anti-overengineering rule for all workers

For every finding:

```text
1. reproduce the exact defect with the smallest failing test;
2. make the smallest change that makes the invariant true;
3. add a regression test for the exact bypass/defect;
4. do not introduce a framework, service, database, crypto protocol, generalized event bus, or abstraction layer unless the existing project contract strictly cannot express the invariant;
5. do not broaden scope because a more general design is aesthetically attractive;
6. if a required semantic is not already authorized, fail closed and report it instead of inventing it.
```

A worker must not convert a simple equality/binding fix into a new subsystem.

## 5. Acceptance discipline

Each package must provide:
- exact baseline and branch/commit;
- changed-file list;
- defect-reproducing tests that fail before the fix and pass after;
- focused tests plus full canonical suite;
- `git diff --check`;
- explicit statement that no candidate outcome data was accessed;
- no frozen protocol change;
- no `CURRENT_STATE.md` edit by worker unless the worker is explicitly assigned main integration ownership.

Project brain performs integration review after each package. A green worker suite is necessary but not sufficient.

## 6. Current next action

```text
CURRENT_REPAIR_PACKAGE=PACKAGE_A_CANDIDATE_EXECUTION_TRUST_BOUNDARY
CURRENT_REPAIR_PACKAGE_STATUS=READY_FOR_SINGLE_DS_WORKER
OWNER_ACTION=RELAY_ONE_BOUNDED_DS_PROMPT
TOOL_DECISION=USE_EXISTING
```
