# OFFLINE REAL PREBUILD — PROJECT-BRAIN FINAL ORP-004 REVALIDATION — 2026-08-30

`AUDIT_REVIEWER = PROJECT_BRAIN`

`AUDIT_MODE = INDEPENDENT_ADVERSARIAL_REVALIDATION__POST_SECOND_CODEX_REPAIR`

`AUDIT_VERDICT = REPAIR_REQUIRED`

## 1. Exact target and evidence boundary

| Item | Value |
| --- | --- |
| Canonical repository | `haozhouliuliuliu/kline-playbook-engine` |
| Main observed during final revalidation | `c21e7ada2b4af40464f9110d16b036d2bfdc0a94` |
| Integration branch | `integration/offline-real-prebuild-v01-20260829` |
| Pre-second-repair integration HEAD | `abe2618ec1134293a128548bbf3d3b3cbd551194` |
| Second Codex repair PR | `#78` |
| Exact second-repair HEAD | `2dab52d4d3fe0e3560a8cb08bf98c8f4d0db5ecd` |
| Repair-branch Repository CI | `#220` / `33259207901` = `SUCCESS` |
| Independent project-brain audit PR | `#79` |
| Audit branch | `project-brain/orp004-final-revalidation-20260830` |
| Audit reproductions | `tests/test_project_brain_orp004_final_revalidation.py`; `tests/test_project_brain_orp004_carried_position.py` |
| Audit CI first reproduction | Repository CI `#221` / `33263243043`: one intentional adversarial failure |
| Audit CI combined reproduction | Repository CI `#222` / `33263340171`: Linux `1181` tests, exactly two intentional adversarial failures, `12` skips; Windows prototype/PAPER/native offline regression `SUCCESS` |

This review remains inside the outcome-independent **OFFLINE REAL-prebuild** boundary. No broker/provider network action, credential use, account mutation, order action, paid provider call or real money was performed.

The current-main V0.1 paid execution lock and all external PAPER/REAL locks remain unchanged.

## 2. Prior-finding adjudication after the second repair

The second Codex repair at `2dab52d...` materially closes two of the three findings that remained after the previous project-brain review:

| Finding | Final revalidation status | Basis |
| --- | --- | --- |
| `PB-REAL-001` current reconciliation proof before new risk | `CLOSED` | Current-process proof is now instance/session/day/query-round bound, starts absent after restart, and is invalidated by truth-changing events. Independent code inspection and repair regressions support fail-closed behavior. |
| `PB-REAL-002` fill-fact / aggregate crash split brain | `CLOSED` | New fill-fact insertion and aggregate rebuild occur in one SQLite transaction, with legacy aggregate repair/blocking and crash/restart regressions. |
| `PB-REAL-003` exact TradingState restart reconciliation | `PARTIALLY_CLOSED` | Envelope/status/fill aggregate comparison was added, but independent audit found two material restart-state gaps below. |

Therefore original `ORP-004` remains **not closed**.

## 3. Confirmed residual findings

### PB2-REAL-001 — HIGH — aggregate-equal TradingState with different durable fill lineage is accepted as exact restart state

**Location**

`src/real_execution_composition.py`:

- `_rehydrate_trading_state`;
- `_trading_order_matches_durable`;
- `_validate_trading_position_projection`.

**Observed implementation behavior**

For a pre-existing runtime order, restart equivalence currently compares only:

- project order ID;
- client request ID;
- contract;
- direction/action;
- requested quantity;
- lifecycle/status;
- aggregate filled quantity;
- aggregate average fill price.

The position check separately compares only final quantity and average open price derived from current durable fill facts.

Neither comparison binds the **canonical fill-event lineage** — broker trade identities, exact fill event count, or equivalent deterministic economic-event identity — to the pre-existing `TradingState` history.

**Independent deterministic reproduction**

The project-brain audit constructs:

1. a durable REAL journal containing exactly one canonical broker fill of quantity `2` at price `3500` under one broker-trade identity;
2. a pre-existing `TradingState` with the same project order, same final FILLED status, same filled quantity `2`, same average fill price `3500`, and the same final long position quantity `2` / average `3500`;
3. however that `TradingState` reaches the aggregate through **two distinct fill events of quantity `1` + `1`** rather than the one canonical durable fill.

PR #79 / CI #221 and CI #222 both show that reopening the composition accepts this state with no `HARD_EXECUTION_INCONSISTENCY`.

CI #222 exact failure:

`AssertionError: 'HARD_EXECUTION_INCONSISTENCY' not found in () : restart accepted an aggregate-equal TradingState whose fill lineage differs from durable REAL facts`

**Why this is material**

Aggregate equality is weaker than execution-history equality. `TradingState` applies fill events into its ledger/accounting projection. Different fill-event identity/count can therefore imply different auditable/economic history even where terminal order quantity and weighted average happen to match.

The architecture requires one attributable, reconcilable order lifecycle across execution adapter, project OMS/state and immutable ledger. Restart may not declare an exact state merely because final aggregates collide.

**Required repair invariant**

A pre-existing `TradingState` may be accepted as exact only when its execution-event/economic lineage is provably the same as the canonical durable REAL execution facts, or when an equivalent canonical execution-projection/checkpoint identity proves that equality.

At minimum the repair must distinguish:

- one canonical fill `qty=2` from two different fills `qty=1 + qty=1` even when final quantity/average/position match;
- identical replay of the exact same durable fill identities from genuinely divergent fill history;
- duplicate idempotent replay from a distinct economic event.

Do not weaken this by comparing only terminal aggregates.

---

### PB2-REAL-002 — HIGH — current-journal position projection assumes a zero baseline and rejects legitimate carried positions on restart

**Location**

`src/real_execution_composition.py`:

- database metadata binds one `expected_trading_day` and `session_identity`;
- `_validate_trading_position_projection` initializes every contract/direction projection from `(quantity=0, average=0)` and derives absolute position using only fill facts present in the current REAL execution journal.

**Observed implementation behavior**

A valid position can exist before the current trading-day/session journal begins. The current validator has no explicit durable baseline position for that journal scope. For a current-day CLOSE of such a carried position, the first durable current-journal action is a close fill, but the validator starts from zero. It therefore concludes the close exceeds projected holdings and latches:

`TRADING_POSITION_PROJECTION_UNPROVABLE`

which becomes:

`HARD_EXECUTION_INCONSISTENCY`.

**Independent deterministic reproduction**

The project-brain audit constructs a legitimate existing long position quantity `2`, creates the current REAL composition journal, submits/fills a CLOSE quantity `1`, and confirms `TradingState` now correctly holds quantity `1`.

It then reopens the exact same journal with the exact same `TradingState` that the first composition produced.

CI #222 shows restart incorrectly hard-blocks that exact state:

`AssertionError: 'HARD_EXECUTION_INCONSISTENCY' unexpectedly found in ('HARD_EXECUTION_INCONSISTENCY',) : restart treated a legitimate carried-position baseline as zero and rejected the exact state it had produced`

**Why this is material**

China-futures positions may legitimately survive a process/session/trading-day boundary. The project has no binding rule that every REAL session must start flat. The architecture explicitly requires persistent project position state and restart/reconnect reconstruction.

A current-day/session execution journal cannot prove an absolute carried position by replaying only that scope's fill facts from zero. Treating missing historical opening fills as zero is an invented fact, not fail-closed truth.

**Required repair invariant**

Position validation for a bounded journal must use an explicit, durable, identity-bound **position baseline** or an equivalent canonical state boundary, then apply current-journal execution deltas over that baseline.

The baseline must:

- never be guessed as zero merely because the current journal contains no earlier OPEN fill;
- survive restart with deterministic identity;
- be tied to the composition/journal scope;
- remain subordinate to current broker/account truth for risk authorization;
- be verified by complete broker reconciliation before any `new_risk_allowed = True` proof;
- fail closed when missing/ambiguous rather than silently inventing holdings.

A legitimate carried-position CLOSE followed by restart with the exact resulting state must remain coherent, while stale/divergent carried-position state must still fail closed.

## 4. Audit CI interpretation

Repository CI #222 is intentionally red on Linux because the two project-brain adversarial assertions expose the target defects. This is expected audit evidence, not unrelated repository breakage.

The same run shows:

- authority consistency: PASS;
- compile: PASS;
- all ordinary repository tests around the repaired target continue to pass;
- existing second-repair ORP-004 tests pass;
- accepted PAPER regression tests pass;
- frozen V0.1 regression tests pass;
- Windows prototype/PAPER/native offline acceptance job: SUCCESS.

Linux summary:

`Ran 1181 tests in 102.391s`

`FAILED (failures=2, skipped=12)`

The only two failures are the project-brain adversarial reproductions named above.

## 5. PAPER and frozen V0.1 non-regression

`PAPER_NON_REGRESSION = PASS__OFFLINE_DETERMINISTIC_BOUNDARY`

`V0_1_NON_REGRESSION = PASS`

No accepted PAPER authority/evidence or frozen V0.1 semantics are implicated by these findings. The defects are isolated to the new OFFLINE REAL execution-composition restart-state boundary.

These PASS labels do not authorize external PAPER, REAL, broker or paid-provider action.

## 6. Verdict

`AUDIT_VERDICT = REPAIR_REQUIRED`

Final residual count after second Codex repair:

- `BLOCKER = 0`
- `HIGH = 2`
- `MEDIUM = 0`
- `LOW = 0`

Current closure:

- `PB-REAL-001 = CLOSED`
- `PB-REAL-002 = CLOSED`
- `PB-REAL-003 = PARTIALLY_CLOSED`
- `PB2-REAL-001 = OPEN__HIGH`
- `PB2-REAL-002 = OPEN__HIGH`
- `ORP-004 = NOT_CLOSED`

PR #78 must not be merged into the integration branch in its present form, and PR #74 must not be merged to `main`.

The next implementation should be one bounded high-assurance package because both findings concern the same canonical restart-state boundary:

`DURABLE EXECUTION EVENT LINEAGE + DURABLE POSITION BASELINE + EXACT TRADINGSTATE RESTART RECONCILIATION`

Codex may implement that repair. The project brain remains the independent acceptance reviewer and must re-run the two project-brain reproductions afterward.
