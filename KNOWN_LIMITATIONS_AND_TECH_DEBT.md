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
STATUS=OPEN
PRIORITY=MEDIUM
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=production/backtest session-authority consolidation or live trading path
```

`src/bootstrap_semantics.py` still contains the early feasibility
`NormalizedSessionCalendar.trading_day_at()` implementation.

The accepted historical/canonical data path uses the later explicit/versioned
`SessionMetadata` authority in `src/data_substrate.py` and governed metadata. The bootstrap
calendar is deliberately a feasibility fixture, but keeping two implementations with
similar trading-day responsibility creates future drift risk.

Required later action:

- preserve `SessionMetadata` / governed session facts as the authoritative semantics;
- retire, adapt, or clearly isolate the bootstrap calendar before it could become a second
  business-logic owner;
- add/retain regression tests proving one timestamp cannot silently map to conflicting
  trading days.

This debt does not invalidate the accepted canonical corpus.

---

## TD-002 — Partial-close snapshot temporarily clears unrealized PnL

```text
STATUS=OPEN
PRIORITY=MEDIUM
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=PnL-sensitive confirmatory validation is treated as final-quality evidence
```

In the current offline validation lifecycle, a partial close creates the remaining-position
snapshot with `unrealized_pnl=0` and updates the position request identity; a later valid mark
observation recomputes unrealized PnL for the remaining quantity.

This was acceptable for the bootstrap/semantics package and is not a canonical-data issue,
but it is a modeling simplification. Before confirmatory PnL evidence is relied on for final
strategy acceptance, the project should decide and implement a coherent mark-preservation /
re-mark semantic so a partial close cannot create a misleading intermediate equity state.

Do not silently change historical accepted evidence when fixing this. Add a new explicit
semantic/version if outcome-affecting behavior changes.

---

## LIMIT-001 — Historical price-limit metadata is not yet fully governed for the corpus

```text
STATUS=DEFERRED
PRIORITY=HIGH_WHEN_ACTIVATED
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=confirmatory validation claims historical price-limit non-fill realism
```

The canonical dataset acceptance did not require full historical price-limit rule/fact
coverage. The accepted dataset package explicitly deferred price-limit history while
preserving tick/session/contract metadata needed for normalization and data quality.

Before a confirmatory backtest claims realistic Chinese-futures price-limit execution over
2024-2025, the project must bind the relevant historical limit metadata by effective period
and ensure execution semantics fail closed when the required fact is missing.

Do not infer historical limits from a current webpage or use a constant rule without evidence.

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
