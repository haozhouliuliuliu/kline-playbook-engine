# KNOWN_LIMITATIONS_AND_TECH_DEBT

## Purpose

This file is the current index of known non-blocking implementation debt and deferred
research/runtime prerequisites that should survive handoff.

It is not a bug graveyard and does not override accepted evidence. Items belong here only
when forgetting them could cause later work to make a false assumption.

## Status legend

```text
OPEN      = known gap/debt remains
DEFERRED  = intentionally postponed until its activation condition
RESOLVED  = fixed; preserve the resolution reference, then move to history when appropriate
```

---

## TD-001 — Duplicate session/trading-day responsibility in bootstrap fixture

```text
STATUS=RESOLVED
RESOLVED_BY=docs/evidence/EXECUTION_EVIDENCE_TD001_TD002_REPAIR_V0_1.md
PRIORITY=MEDIUM
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=production/backtest session-authority consolidation or live trading path
```

`src/bootstrap_semantics.py` previously carried an early feasibility
`NormalizedSessionCalendar.trading_day_at()` implementation.

The accepted historical/canonical data path uses the explicit/versioned
`SessionMetadata` authority in `src/data_substrate.py` and governed metadata. The bootstrap
calendar is deliberately a feasibility fixture, but a second independent trading-day
implementation created future drift risk.

Resolution (see `docs/evidence/EXECUTION_EVIDENCE_TD001_TD002_REPAIR_V0_1.md`):

- `NormalizedSessionCalendar` now delegates `trading_day_at()` / `trading_week_at()` to a
  single authoritative `SessionMetadata`, so no competing trading-day algorithm remains;
- `SessionMetadata.trading_week_at()` makes weekly attribution use the same official
  trading-day identity;
- regression tests prove one timestamp cannot silently map to conflicting trading days,
  including night-session/cross-midnight and week-boundary cases.

This debt did not invalidate the accepted canonical corpus.

---

## TD-002 — Partial-close snapshot temporarily clears unrealized PnL

```text
STATUS=RESOLVED
RESOLVED_BY=docs/evidence/EXECUTION_EVIDENCE_TD001_TD002_REPAIR_V0_1.md
PRIORITY=MEDIUM
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=PnL-sensitive confirmatory validation is treated as final-quality evidence
```

Previously, in the offline validation lifecycle, a partial close created the remaining-position
snapshot with `unrealized_pnl=0` and updated the position request identity; a later valid mark
observation recomputed unrealized PnL for the remaining quantity.

This was acceptable for the bootstrap/semantics package and was not a canonical-data issue,
but it was a modeling simplification that could create a misleading intermediate equity state.

Resolution (see `docs/evidence/EXECUTION_EVIDENCE_TD001_TD002_REPAIR_V0_1.md`):

- after a partial close the remaining position is re-marked deterministically at the close
  fill price (the explicit mark price of the transition), so unrealized PnL / equity /
  drawdown path stay correct;
- realized PnL totals and transaction-cost semantics are unchanged;
- full close still ends with a flat snapshot and zero remaining unrealized.

---

## LIMIT-001 — Historical price-limit metadata is not yet fully governed for the corpus

```text
STATUS=DEFERRED
PRIORITY=HIGH_WHEN_ACTIVATED
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=confirmatory validation claims historical price-limit non-fill realism
REDUCTION=PREP_DONE_BASE_BOUND_PER_DAY_GAP
AUTHORITY=docs/research/HISTORICAL_PRICE_LIMIT_METADATA_AUTHORITY_PREP_V0_1.md
```

The canonical dataset acceptance did not require full historical price-limit rule/fact
coverage. The accepted dataset package explicitly deferred price-limit history while
preserving tick/session/contract metadata needed for normalization and data quality.

Before a confirmatory backtest claims realistic Chinese-futures price-limit execution over
2024-2025, the project must bind the relevant historical limit metadata by effective period
and ensure execution semantics fail closed when the required fact is missing.

Do not infer historical limits from a current webpage or use a constant rule without evidence.
The six-product base-rule authority is now machine-readable, but the per-day operative layer remains a historical gap and special-day rules remain unknown; this limitation is not resolved.

---

## LIMIT-002 — Accepted canonical corpus requires explicit revalidation under repaired completeness rules

```text
STATUS=RESOLVED
RESOLVED_BY=docs/evidence/CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1_ADOPTION.md
PRIORITY=CRITICAL_BEFORE_CANDIDATE_USE
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=none; candidate outcome gate remains separately locked
```

Second-pass Package D repaired the production completeness/provenance path: full requested
coverage is required for PASS, zero-bar expected sessions/windows are represented, canonical
storage is PASS-only, and session authority is content-derived. The historical accepted
15,280,452-row corpus was **not** rebuilt or re-certified under those repaired D-01/D-02 rules.

This does not revoke the recorded OHLC values or the existing cross-source comparison. It
means the old acceptance cannot be promoted into a new claim that repaired completeness has
already been re-proven.

Historical revalidation remains an unchanged fact: 32864 PASS / 116 FAIL. The resolution does not rewrite it; Qualified Eligibility View V1 uniformly excludes every governed first trading-day partition, producing 32768 D01/D02-certified eligible partitions with a separate identity. Candidate outcome access remains locked by other gates.

---

## LIMIT-003 — Continuous 2024-2025 historical exchange fee/margin schedule remains incomplete

```text
STATUS=DEFERRED
PRIORITY=CRITICAL_BEFORE_CANDIDATE_QUALITY_EXECUTION
CURRENT_BLOCKER=NO_FOR_REPAIR_CLOSURE
ACTIVATE_BEFORE=historical candidate validation claims realistic China-futures fees/margins
AUTHORITY=docs/research/E06_HISTORICAL_FEE_MARGIN_EVIDENCE_ASSESSMENT_V0_2.md
REOPEN_TRIGGER=NEW_OFFICIAL_SOURCE_OR_ACCESS_CHANGE_OR_OWNER_POLICY_CHANGE
```

The final bounded official-source pass materially improved point-in-time SHFE evidence but did
not establish a continuous exchange-level fee/margin schedule over 2024-01-01..2025-12-31 for
cu/al/ni/au/ag/rb.

Binding current status:

```text
E06_FINAL_JUDGMENT=PARTIALLY_BUILDABLE_WITH_GAPS
E06_EXCHANGE_LEVEL_SCHEDULE_JUDGMENT=INSUFFICIENT_EVIDENCE
E06_FURTHER_REPEAT_ACQUISITION_DEFAULT=NO
```

Current-rate backfill, third-party substitution, and inferred historical values remain
forbidden. This is a long-lived governed prerequisite, not a reason to reopen the completed
second-pass repair loop.

---

## LIMIT-004 — Source-governed TqSdk historical main-contract mapping

```text
STATUS=RESOLVED
PRIORITY=CRITICAL_BEFORE_CANDIDATE_CONTRACT_MAPPING
CURRENT_BLOCKER=NO_FOR_REPAIR_CLOSURE
ACTIVATE_BEFORE=research-symbol candidate execution maps to canonical concrete contracts
RESOLVED_BY=docs/evidence/E07_TQSDK_MAPPING_SCHEMA_AND_CAPTURE_V0_1.md
SCHEDULE=docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json
WINDOW=2024-01-01..2025-12-31
RUNTIME_WIRING=WIRED_FAIL_CLOSED_VERIFIED
```

Owner-authorized authenticated capture pins TqSdk 3.10.1's daily `KQ.m@` mapping response.
The resulting 105-change, six-product schedule binds only canonical concrete contracts for
the 2024-2025 window. It is mapping evidence only, not price or outcome evidence. Runtime
wiring is implemented and verified as a fail-closed runtime/candidate-input seam; it remains
separate from outcome authorization.

The generic `ContractMappingSchedule` type is structural/synthetic machinery and is **not** a
candidate mapping authority. Do not substitute a project-authored OI/volume/calendar formula,
do not use pseudo-main price bars, and do not select a mapping by outcomes.

---

## LIMIT-005 — Holy Grail Primary identity and pre-outcome gate

```text
STATUS=RESOLVED
PRIORITY=HIGH_BEFORE_CANDIDATE_OUTCOME_ACCESS
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=first candidate outcome-bearing test
RESOLVED_BY=docs/evidence/HOLY_GRAIL_PRIMARY_FREEZE_V0_1.md
```

Holy Grail V0.4 has one frozen PRIMARY and StrategyIdentity, constructed without candidate
outcomes. Its 1-minute base, one-step ADX rising window, L1/R1 swing confirmation and
swing-based trailing stop remain versioned project-inferred conventions, not source claims.
The later “exit on push to new highs” wording remains an optional versioned variant, not the
PRIMARY exit and cannot rescue the PRIMARY after outcomes.

---

## LIMIT-006 — Prospective Shadow statistical profile is not yet locked

```text
STATUS=DEFERRED_RESEARCH_POLICY
PRIORITY=CRITICAL_BEFORE_PROSPECTIVE_CANDIDATE_OUTCOME_ACCESS
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=prospective Shadow forward candidate evidence
AUTHORITY=docs/research/HUMAN_PLAYBOOK_STATISTICAL_ACCEPTANCE_ROUTE_POLICY_V1_0.md
HISTORICAL_POSITIVE_PASS_PROFILE_BLOCKER=DISPOSITIONED_BY_ROUTE_A_D
PROSPECTIVE_SHADOW_STATISTICAL_PROFILE=NOT_LOCKABLE_UNDER_CURRENT_ASSUMPTION_AUTHORITY
PROSPECTIVE_PROCESS_ASSUMPTION_DESIGN=NO_GOVERNABLE_A_B_ASSUMPTION_FOUND
STATISTICAL_BLOCKER_CLASS=RESEARCH_DESIGN_LIMIT_NOT_ENGINEERING_DEFECT
```

Route A+D is binding: historical general-domain positive PASS is not required or claimed,
and future genuinely unseen prospective Shadow/Forward is the positive path. Formal research
now identifies the exact mathematical missing authority: a pre-governed process class linking
conditional mean/tail/dependence assumptions to the frozen unconditional event-weighted null.
Production code still permits locking only explicitly `TEST_ONLY` profiles for synthetic engine fixtures.

The bounded V0.3 project-control/prospective-design pass found no A/B assumption that
both preserves the frozen population estimand and governs the required market process.
This is a research-design limit, not an execution-engineering defect; do not reopen it
without a new governed design, strong independent theory, or formal protocol decision.
Do not create a real-looking profile by filling descriptive strings, and do not treat test
profile success as permission to inspect candidate outcomes.

---

## LIMIT-007 — Portfolio candidate-outcome authority is not implemented

```text
STATUS=DEFERRED_ARCHITECTURE
PRIORITY=HIGH_WHEN_ACTIVATED
CURRENT_BLOCKER=NO_FOR_REPAIR_CLOSURE
ACTIVATE_BEFORE=multi-strategy portfolio candidate-performance evaluation
```

Package E fixed heterogeneous per-member/per-resolved-contract capital assumptions, but the
portfolio confirmatory outcome path remains intentionally hard closed after structural
validation with:

```text
PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED
```

Do not remove this fail-closed boundary as an incidental implementation change. A future
portfolio candidate authority requires a dedicated identity/access design and appropriate
project approval.

---

## LIMIT-008 — SOURCE_ONLY and local project state do not prove hostile-process tamper resistance

```text
STATUS=DEFERRED_THREAT_MODEL_LIMIT
PRIORITY=MEDIUM_UNLESS_THREAT_MODEL_CHANGES
CURRENT_BLOCKER=NO
```

SOURCE_ONLY now has material-bound evidence, project-issued session verification, a protected
outcome API that always denies, and durable governance state. These controls are normal
project API/session boundaries.

They do not prove:

- OS/process sandbox isolation from shell/repository/files;
- malicious Python introspection resistance;
- local state-file tamper resistance;
- cryptographic protection against a hostile actor who already controls the process/filesystem.

Historical source bytes that were never recorded also cannot be retroactively proven. Do not
upgrade these boundaries in future status language without a new threat-model package.

---

## DECISION-001 — Live AI market-reading implementation remains unresolved

```text
STATUS=DEFERRED_OWNER_GATE
CURRENT_BLOCKER=NO
AUTHORITY=RESEARCH_DIRECTION.md
```

The Human Playbook First direction includes the long-term concept of a machine market-reading
brain, but does not authorize a discretionary LLM in the live trading critical path.

The exact live scene-recognition implementation is a future architecture/research decision
and must not be silently chosen by an implementation agent.

See `RESEARCH_DIRECTION.md` for the binding boundary.

---

## Maintenance rule

When a listed item becomes relevant to the current bounded package, `CURRENT_STATE.md` should
reference it explicitly. Do not keep stale solved items here indefinitely; preserve accepted
resolution evidence and then retire the item cleanly.
