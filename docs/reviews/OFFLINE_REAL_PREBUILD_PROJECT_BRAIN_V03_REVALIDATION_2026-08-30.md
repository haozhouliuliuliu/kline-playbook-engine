# OFFLINE REAL PREBUILD — PROJECT-BRAIN V03 REVALIDATION — 2026-08-30

`AUDIT_REVIEWER = PROJECT_BRAIN`

`AUDIT_MODE = INDEPENDENT_ADVERSARIAL_REVALIDATION__POST_THIRD_CODEX_REPAIR`

`AUDIT_VERDICT = REPAIR_REQUIRED`

## 1. Exact target and evidence boundary

| Item | Value |
| --- | --- |
| Canonical repository | `haozhouliuliuliu/kline-playbook-engine` |
| Main observed during revalidation | `c21e7ada2b4af40464f9110d16b036d2bfdc0a94` |
| Integration branch | `integration/offline-real-prebuild-v01-20260829` |
| Integration PR | `#74` — blocked from `main` |
| Third Codex repair PR | `#80` |
| Exact third-repair HEAD | `b8e479ee68f9fa97149f8684549fa92050ddb8a7` |
| Repair parent | `2dab52d4d3fe0e3560a8cb08bf98c8f4d0db5ecd` |
| Repair-branch Repository CI | `#224` / `33277680146` = `SUCCESS` |
| Repair-branch Linux suite | `1193` tests, `12` skips, PASS |
| Independent project-brain audit PR | `#81` |
| Audit branch | `project-brain/orp004-v03-independent-revalidation-20260830` |
| Audit test commit with final adversarial set | `1fb38f129e6ed157fdebc0bfd2cdb2f2359d5a22` |
| Final adversarial Repository CI | `#227` / `33279957018` |
| CI #227 Linux | `1199` tests; exactly `4` project-brain adversarial failures; `12` skips |
| CI #227 Windows prototype/PAPER/native offline | `SUCCESS` |

The worker completion report said `1193_TESTS_PASS_8_SKIPPED`. GitHub CI is the operative evidence and records `1193` tests with `12` skips on the repair branch. This bookkeeping mismatch is not the acceptance blocker; the independent findings below are.

This review remains inside the outcome-independent **OFFLINE REAL-prebuild** boundary. No broker/provider network action, credential use, account mutation, order action, paid provider call or real money was performed.

Current-main V0.1 paid execution and all external PAPER/REAL locks remain unchanged.

## 2. Prior residual findings after PR #80

PR #80 materially fixes both findings carried from the preceding project-brain review.

| Finding | Independent v03 status | Basis |
| --- | --- | --- |
| `PB2-REAL-001` exact execution-event lineage | `CLOSED` | The prior independent one-fill-vs-two-fill aggregate-collision reproduction now hard-fails as required. Durable fill lineage includes the material external/event identities and exact ordered fact set rather than only terminal quantity/average. |
| `PB2-REAL-002` carried-position journal baseline | `CLOSED` | The prior independent legitimate carried LONG position -> current-journal CLOSE -> exact restart reproduction now remains coherent and does not self-latch `HARD_EXECUTION_INCONSISTENCY`. |

These are real closures. The v03 rejection is caused by newly exposed adjacent restart-integrity gaps, not failure to fix the two prior reproductions.

## 3. Confirmed residual findings

### PB3-REAL-001 — HIGH — a nonempty journal can silently re-bootstrap schema/baseline after durable metadata loss

**Primary location**

`src/real_execution_composition.py` initialization / schema / position-baseline path.

**Observed behavior**

PR #80 correctly treats a known legacy `V0_1` journal as baseline-initializable only when the legacy journal is empty. However the `schema_version metadata absent` path can establish the current schema and allow baseline initialization without first proving that the durable REAL journal is empty.

The independent audit constructs a valid current journal with a durable current-session order and an originally captured position baseline. It then removes:

- `real_position_baseline`; and
- the `schema_version` metadata row,

while leaving the durable execution journal nonempty. The supplied caller `TradingState` position is then made divergent from the originally captured baseline.

On reopen, the implementation silently captures the caller's divergent position as a new baseline and reports no `HARD_EXECUTION_INCONSISTENCY`.

CI #227 exact failure:

`restart accepted: nonempty journal silently recaptured a divergent caller position after schema+baseline loss`

**Why this is material**

A damaged or partially lost durable journal must not be reclassified as a fresh journal merely because one metadata row disappeared. That converts missing durable authority into caller-provided state and permits history to be silently rewritten at the journal boundary.

**Required invariant**

Baseline/schema initialization is permitted only when the database can positively prove a genuinely fresh/empty execution journal under an explicit initialization contract.

If any consequential durable journal state exists — orders, fills/facts, lifecycle facts, baseline/checkpoint remnants, or other state establishing prior use — missing/inconsistent schema/baseline metadata must fail closed. It must not guess zero, capture current caller state as replacement history, delete facts, or silently migrate an ambiguous nonempty journal.

---

### PB3-REAL-002 — HIGH — restart exactness does not bind the full TradingState economic + immutable-audit state

**Primary locations**

- `src/real_execution_composition.py` restart validation;
- `src/trading_state.py` mutable state / restore surfaces;
- `src/runtime_ledger.py` immutable factual ledger.

PR #80 now proves exact current-journal fill-event lineage and validates terminal position quantity/average over a durable carried-position baseline. That is necessary but still weaker than exact `TradingState` continuity.

`TradingState` is explicitly the sole authoritative mutable local real-time state owner. Its position and account projections contain economic fields beyond quantity/average, and its injected `RuntimeLedger` is the immutable chained record of what happened.

The independent audit proves three subcases in which the execution lineage and visible terminal quantity/average remain correct but restart still accepts a split-brain state:

#### A. Position economics divergence is accepted

The exact state produced by a carried-position partial CLOSE is retained, including the exact current-journal applied BrokerEvents. Only the resulting `PositionState.realized_pnl` is changed by `+1` while quantity and average-open price remain exact.

Restart reports no `HARD_EXECUTION_INCONSISTENCY`.

CI #227:

`restart accepted exact fill lineage and terminal qty/average despite divergent position economics`

#### B. Account economics divergence is accepted

The exact execution lineage and position projection are retained. Only `AccountState.charged_costs` is changed by `+1`.

Restart reports no `HARD_EXECUTION_INCONSISTENCY`.

CI #227:

`restart accepted exact execution lineage/position aggregates despite divergent account economics`

#### C. Immutable RuntimeLedger loss is accepted

The exact orders, positions, account projection and applied BrokerEvent history produced by the composition are retained, but the state's `RuntimeLedger` is replaced with a fresh empty ledger.

Restart reports no `HARD_EXECUTION_INCONSISTENCY`.

CI #227:

`restart accepted exact applied events with a replaced empty immutable RuntimeLedger`

**Why this is material**

A restart boundary cannot claim exact project-state continuity when the same execution facts correspond to different realized PnL, costs, margin/economic state, or a missing immutable audit chain. The architecture requires project position state, OMS/execution journal, reconciliation and immutable ledger to remain attributable and auditable before consequential operation.

Broker reconciliation does not cure a corrupted local restart identity by itself. Current broker truth is still required before new risk, but local durable state must first be internally coherent rather than silently accepting conflicting economic/audit projections.

**Required invariant**

The REAL journal must bind a deterministic journal-start state boundary/checkpoint sufficient to prove the full relevant project-state continuity across restart, then validate current-journal execution effects against it.

At minimum the restart proof must cover, as applicable:

- full relevant `PositionState` economic identity, not only quantity and average-open price;
- full relevant `AccountState` economic identity;
- accounting-assumption / contract-semantic identity needed to reproduce those economics;
- exact current-journal execution-event lineage already fixed by PR #80;
- immutable `RuntimeLedger` chain validity and deterministic correspondence/ancestry for the composition-owned economic/broker events;
- journal trading-day/session identity.

Do not require byte identity of unrelated ledger history merely for convenience, but the journal-start checkpoint and current-journal events must be provably anchored in one intact ledger chain. An empty/replaced/tampered ledger with otherwise copied applied-event state must fail closed.

Do not silently overwrite supplied economic history to make it match. Safe deterministic rehydration/replay is allowed only when idempotency and economic exactly-once behavior are proven.

The durable checkpoint remains continuity evidence, **not current broker truth**. A fresh current-process complete broker reconciliation is still mandatory before `new_risk_allowed = True`.

## 4. Independent CI interpretation

The project-brain audit intentionally adds negative assertions that should pass only when the safety invariants are enforced.

### CI #225

The two prior PB2 reproductions passed after PR #80, while two newly added adjacent probes failed exactly as predicted:

- missing schema + missing baseline on nonempty journal;
- divergent position economics with exact fill lineage/quantity/average.

### CI #226

Added the account-economic continuity probe. Linux had exactly three project-brain failures:

- nonempty-journal baseline recapture;
- position economics divergence;
- account economics divergence.

Windows/PAPER/native offline path remained successful.

### CI #227

Added the RuntimeLedger coherence probe.

Linux result:

`Ran 1199 tests in 104.233s`

`FAILED (failures=4, skipped=12)`

Exactly the following independent project-brain tests fail:

1. nonempty journal schema/baseline loss is silently recaptured;
2. position economic divergence is accepted;
3. account economic divergence is accepted;
4. exact applied-event state with an empty replacement RuntimeLedger is accepted.

The two prior PB2 reproductions pass in the same run.

Repository authority consistency and compile pass before the suite. All ordinary PR #80 regression tests around REAL restart state pass. Accepted PAPER regressions and frozen V0.1 regressions continue to pass. Windows prototype/PAPER/native offline job is `SUCCESS`.

This red Linux result is intentional audit evidence exposing the four target gaps, not unrelated repository failure.

## 5. PAPER and frozen V0.1 non-regression

`PAPER_NON_REGRESSION = PASS__OFFLINE_DETERMINISTIC_BOUNDARY`

`V0_1_NON_REGRESSION = PASS`

No accepted PAPER authority/evidence or frozen V0.1 research semantics are changed by these findings. They remain isolated to the new OFFLINE REAL execution-composition restart-integrity boundary.

These labels grant no external PAPER/REAL/broker/provider/paid permission.

## 6. Verdict

`AUDIT_VERDICT = REPAIR_REQUIRED`

Prior residual closure:

- `PB2-REAL-001 = CLOSED`
- `PB2-REAL-002 = CLOSED`

New residual count:

- `BLOCKER = 0`
- `HIGH = 2`
- `MEDIUM = 0`
- `LOW = 0`

Current residuals:

- `PB3-REAL-001 = OPEN__HIGH__NONEMPTY_JOURNAL_INITIALIZATION_INTEGRITY`
- `PB3-REAL-002 = OPEN__HIGH__FULL_TRADINGSTATE_ECONOMIC_AND_LEDGER_CONTINUITY`
- `ORP-004 = NOT_CLOSED`

PR #80 must not be merged into the integration branch in its present form. PR #74 remains blocked from `main`.

The next repair should remain one bounded high-assurance package because both findings belong to the same journal/restart ownership boundary:

`FAIL-CLOSED JOURNAL INITIALIZATION + DURABLE FULL-ECONOMIC CHECKPOINT + RUNTIMELEDGER ANCHOR/COHERENCE + EXACT CURRENT-JOURNAL REPLAY + FRESH BROKER TRUTH BEFORE NEW RISK`

Preserve PR #80's successfully repaired exact fill lineage and carried-position behavior. Do not broaden into external broker activation, permanent risk numbers, execution-policy binding, PAPER changes, or V0.1 semantic changes.

The project brain remains the independent acceptance reviewer and must re-run all PR #81 adversarial cases after the next implementation.