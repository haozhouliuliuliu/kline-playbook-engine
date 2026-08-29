# OFFLINE REAL PREBUILD — PROJECT-BRAIN POST-REPAIR AUDIT — 2026-08-29

`AUDIT_REVIEWER = PROJECT_BRAIN`

`AUDIT_MODE = INDEPENDENT_FINDINGS_ONLY__POST_CODEX_REPAIR`

`AUDIT_VERDICT = REPAIR_REQUIRED`

## 1. Exact target and authority boundary

| Item | Value |
| --- | --- |
| Canonical repository | `haozhouliuliuliu/kline-playbook-engine` |
| Main observed at audit refresh | `c21e7ada2b4af40464f9110d16b036d2bfdc0a94` |
| Target integration branch | `integration/offline-real-prebuild-v01-20260829` |
| Exact target HEAD | `abe2618ec1134293a128548bbf3d3b3cbd551194` |
| Integration PR | `#74` |
| Original findings-only audit | PR `#75`, commit `20ec57ce22c9c90e0bbd53a0e4359e74f3273dd9` |
| Codex bounded repair | PR `#76`, commit `f7d4ac494444097e005c76cee6f88f6f9be6b64a` |
| Repair-branch CI evidence | Repository CI `#217` = SUCCESS |
| Post-repair integration CI evidence | Repository CI `#218`, run `33244098685` = SUCCESS |

This review is limited to the outcome-independent **OFFLINE REAL-prebuild** code boundary. It does not authorize or establish Fangzheng/CTP live connectivity, PAPER login/order action, broker/account mutation, paid provider execution, real money, permanent numeric risk policy, or frozen V0.1 execution.

Current-main locks and the frozen V0.1 research route remain unchanged.

## 2. Method

The project brain independently re-read current-main governance/direction/state/architecture/tool ownership and the original Codex consolidated audit. The review then inspected the actual post-repair implementation and its interfaces rather than accepting worker completion claims.

Primary code paths inspected include:

- `src/real_preflight.py` / `src/real_runtime_controller.py`;
- `src/real_safety_state.py` / `src/real_risk_gate.py`;
- `src/realtime_provider_attempt_ledger.py` / `src/realtime_provider_control.py`;
- `src/contract_facts.py` / capital-facts propagation;
- `src/fangzheng_ctp_candidate.py`;
- `src/real_execution_composition.py`;
- `src/real_reconciliation.py` / `src/real_runtime_recovery.py`;
- `src/trading_state.py`;
- the relevant focused, cross-finding, restart and PAPER regression tests.

Repository CI #218 was also inspected as verification evidence. Its Linux job ran `1167` tests with `OK (skipped=12)`, and authority consistency / compile passed. The Windows prototype job, including PAPER offline-readiness and native offline acceptance probes, also passed. Green CI is verification evidence, not acceptance by itself.

No broker/provider connection, credential read, account mutation, order, paid call or real-money action was performed by this audit.

## 3. Original-finding closure table

| Finding | Re-audit result | Project-brain evidence |
| --- | --- | --- |
| ORP-001 | `CLOSED` | `account_state` is now a first-class preflight input, the controller forwards it, UNKNOWN/UNRESOLVED/NOT_SUPPLIED fail closed, and focused/controller regressions pass. |
| ORP-002 | `CLOSED` | Persistent external-mutation state now outranks contradictory transient facts; kill disarm/resume cannot bypass an unresolved mutation; explicit resolution is required. |
| ORP-003 | `CLOSED` | Provider ledger and control both enforce exact authority-identity equality before durable admission; mismatch consumes no attempt and ledger binding survives reopen. |
| ORP-004 | `PARTIALLY_CLOSED` | A real CTP→durable project-state composition seam now exists and closes many original scenarios, but three material restart/readiness invariants below remain open. |
| ORP-005 | `CLOSED` | `ContractFacts.identity_id` now binds nested margin, fee and price-limit economic values through deterministic canonical serialization; propagation tests pass. |

## 4. What ORP-004 repair successfully established

The repair materially improved the original CTP composition gap. The current target now has one explicit project-owned `RealExecutionComposition` seam with SQLite persistence and project/broker identity separation.

The inspected implementation/tests substantiate, within the offline fake boundary:

- durable project order identity before crossing the submit transport seam;
- UNKNOWN submit surviving process-style restart;
- disconnect-before-ack followed by complete broker query resolving OPEN;
- complete broker query resolving FILLED and applying economic effect once;
- incomplete broker query preserving UNKNOWN and blocking new risk in that recovery result;
- fill-before-ack callback reordering while retaining complete project semantic order facts;
- identical fill replay deduplication;
- conflicting external trade identity becoming a hard inconsistency;
- external/unmapped broker order becoming an external-mutation latch;
- stale trading-day callback fail-closed behavior;
- no silent second submit when the durable project order already exists.

These are genuine closures of a substantial part of original ORP-004. They do not close the three findings below.

## 5. New / remaining material findings

### PB-REAL-001 — HIGH — composition readiness can be TRUE before any current broker reconciliation truth exists

**Location**

`src/real_execution_composition.py` — `RealExecutionComposition.new_risk_allowed`.

**Observed behavior**

The property returns `False` only when:

- there is an unresolved durable order;
- an active composition blocker exists; or
- an optional safety controller itself blocks risk increase.

Otherwise it returns `True`.

It does **not** require a current complete broker/account/position/order/trade reconciliation result, a current broker-truth generation, a matching current trading day/session proof, or even an adapter currently holding known broker truth.

**Deterministic reproduction from the code path**

Construct a fresh composition with:

- an empty REAL execution journal;
- no active blocker;
- no orders;
- a fresh `TradingState`;
- an adapter whose session/broker truth is still DISCONNECTED/UNKNOWN;
- no safety controller.

Then:

- `unresolved_order_count == 0`;
- `active_blockers() == ()`;
- there is no safety-controller denial;
- therefore `new_risk_allowed == True` despite zero established broker/account truth.

The same design has no durable/current reconciliation token that must be reacquired after reconnect or other broker-truth invalidation.

**Impact**

A future REAL runtime consuming this explicit readiness property can observe a fail-open `True` before the architecture-required broker/account reconstruction has occurred. This directly conflicts with the project truth hierarchy and the rule that unknown broker/order/position/account state means no new risk.

**Required invariant for repair**

`new_risk_allowed` must remain false until a **current, complete, appropriately bound reconciliation proof** exists. That proof must be invalidated by any event that makes broker truth uncertain, including disconnect/reconnect/trading-day or session invalidation and other state changes that require fresh broker truth. Merely being connected/READY is not sufficient.

Do not solve this by inventing live broker facts or weakening fail-closed semantics.

---

### PB-REAL-002 — HIGH — fill fact and order aggregate are committed in separate transactions, allowing crash-created durable split brain

**Location**

`src/real_execution_composition.py` — `_record_fill`, `_record_fact`, `real_execution_facts`, `real_execution_orders`, and restart rehydration.

**Observed persistence sequence**

For a new fill, `_record_fill` currently:

1. calls `_record_fact(...)`, which opens and commits its own SQLite transaction inserting the external fill fact;
2. later opens a different SQLite transaction to update `real_execution_orders` with broker ID, lifecycle, filled quantity and average fill price;
3. later applies the derived fill to `TradingState`.

**Crash reproduction / invariant failure**

If the process terminates after step 1 commits but before step 2 commits:

- the canonical external fill fact exists durably;
- `real_execution_orders` still has its earlier aggregate state, e.g. OPEN / filled `0`;
- restart rehydration can replay the fill fact into `TradingState`, so `TradingState` can show PARTIALLY_FILLED/FILLED while `real_execution_orders` remains stale;
- a later duplicate broker trade fact is already present, so `_record_fact` returns the dedupe path instead of repairing the stale aggregate;
- subsequent reconciliation can then classify the divergence as incomplete/inconsistent rather than deterministically rebuilding the already-known durable fill.

Combined with PB-REAL-001, an OPEN/stale aggregate is also not inherently counted as unresolved.

**Impact**

A process crash can create two durable project representations of the same order with different economic state. This defeats the restart/reconciliation guarantee that the repair was intended to establish.

**Required invariant for repair**

Choose one coherent durable authority:

- either insert the external fill fact and update its derived order aggregate atomically in one transaction; or
- make one durable representation canonical and deterministically rebuild/validate the other from it before any readiness claim.

Crash at every persistence boundary must reconstruct one coherent order/fill state. An already-recorded fill fact must not prevent deterministic recovery of a missing derived aggregate update.

Do not delete or rewrite historical economic facts to conceal the inconsistency.

---

### PB-REAL-003 — HIGH — restart rehydration skips consistency checking when `TradingState` already contains the same order ID

**Location**

`src/real_execution_composition.py` — `_rehydrate_trading_state`.

**Observed behavior**

For every durable REAL order, the method currently performs the equivalent of:

```text
if TradingState already has project_order_id:
    continue
```

The skip condition verifies only order-ID existence. It does not prove equality of:

- client-request identity;
- concrete contract;
- direction/action;
- requested quantity;
- lifecycle/status;
- filled quantity / average fill;
- derived position/economic projection;
- durable fill-fact history.

**Deterministic reproduction from the code path**

Supply a restored/stale `TradingState` that already contains `project-order-1`, while the REAL execution SQLite journal contains the same project order with a later partial/full fill. Constructor rehydration sees the order ID and skips replay/validation. The journal and `TradingState` can therefore remain split-brain without a hard inconsistency being latched.

**Impact**

Restart correctness depends on the caller accidentally supplying an exactly synchronized `TradingState`. The composition seam does not establish that requirement itself, yet it exposes readiness from its own journal/blocker state. A stale model/project position projection can therefore coexist with a nominally resolved durable execution journal.

**Required invariant for repair**

On restart, a pre-existing `TradingState` order must be explicitly reconciled with the durable REAL execution facts. If it is exactly coherent, accept it. If deterministic missing-event replay can safely bring it forward, do so. Otherwise latch a hard inconsistency and fail closed. Never skip solely because the project order ID exists.

Regression coverage must include both:

- an exact-consistent pre-existing `TradingState`; and
- a stale/divergent pre-existing `TradingState` sharing the same order ID.

## 6. Cross-package adjudication

The three findings above are one coherent remaining ORP-004 closure problem:

```text
CURRENT BROKER TRUTH PROOF
+ ATOMIC / REBUILDABLE DURABLE ORDER ECONOMICS
+ EXACT RESTART STATE RECONCILIATION
= SAFE REAL EXECUTION COMPOSITION READINESS
```

They should be repaired together as one bounded package. Splitting them among parallel workers would increase the chance of creating competing lifecycle/readiness owners.

No new finding was substantiated in ORP-001, ORP-002, ORP-003 or ORP-005 after the Codex repair.

## 7. PAPER semantic non-regression

`PAPER_NON_REGRESSION = PASS__OFFLINE_DETERMINISTIC_BOUNDARY`

The only bounded change to a pre-existing shared runtime implementation inspected here is the duplicate `ORDER_SUBMITTED` handling in `src/trading_state.py`.

Relative to main, the new path:

- preserves the first-submit behavior;
- requires an existing order acknowledgement to match client request, contract, direction, action and requested quantity;
- preserves an already PARTIALLY_FILLED/FILLED state when a later acknowledgement arrives instead of resetting the economic state;
- does not relax TradingState's complete-field requirements for submitted/fill events.

Repository CI #218 also runs the existing PAPER regression surface and Windows PAPER/native offline probes successfully. No accepted PAPER authority/evidence was modified by the target.

This PASS is limited to the deterministic offline code boundary; it is not external PAPER authorization.

## 8. Frozen V0.1 semantic non-regression

`V0_1_NON_REGRESSION = PASS`

The target does not alter the frozen V0.1 Owner decision, sealed 1998-wake replay semantics, wake policy, outcome-blind selection, causal timeframe semantics or V0.1 provider authority. The full V0.1 regression surface in Repository CI #218 remains green.

This audit does not authorize the 1998 paid replay.

## 9. Important no-finding areas

No material finding was substantiated in the following inspected boundaries:

- no vendor CTP SDK/runtime was silently adopted;
- no network/broker/provider action is performed merely by importing/constructing the offline candidate surfaces;
- no secret value or credential-bearing field was added to the audited durable records;
- REAL authority fixtures remain TEST_ONLY/offline and cannot themselves authorize external execution;
- permanent numeric REAL risk limits remain unbound rather than inferred from the approximately RMB 100,000 capital envelope;
- provider attempt retry remains zero and duplicate wake/UNKNOWN persistence remains fail closed;
- historical contract facts do not masquerade as current broker truth;
- contract-capital calculations still return insufficient evidence rather than fabricating missing margin/fee inputs.

## 10. Verdict and next repair boundary

`AUDIT_VERDICT = REPAIR_REQUIRED`

Counts for this post-repair project-brain audit:

- `BLOCKER = 0`
- `HIGH = 3`
- `MEDIUM = 0`
- `LOW = 0`

Original finding status:

- `ORP-001 = CLOSED`
- `ORP-002 = CLOSED`
- `ORP-003 = CLOSED`
- `ORP-004 = PARTIALLY_CLOSED`
- `ORP-005 = CLOSED`

Codex may perform one bounded repair package for `PB-REAL-001..003` against exact target `abe2618ec1134293a128548bbf3d3b3cbd551194`.

The project brain remains the acceptance reviewer after that repair. Codex must not self-accept the repaired package.
