# OFFLINE REAL PREBUILD CONSOLIDATED CODEX AUDIT — 2026-08-29

`AUDIT_MODE = FINDINGS_ONLY`

## Target and method

| Item | Value |
| --- | --- |
| Target branch | `integration/offline-real-prebuild-v01-20260829` |
| Target HEAD | `5ee1301fdbfdb01c110941f564f1b2a0022c1e8f` |
| Main observed at audit start | `c21e7ada2b4af40464f9110d16b036d2bfdc0a94` |
| Target PR | `#74` |
| Pre-audit CI evidence only | `#215` / `33235068477`: Linux and Windows SUCCESS; not acceptance |
| Audit branch base | target HEAD above |

The reviewer refreshed `origin/main`, verified that both the integration branch
and fetched PR #74 resolve exactly to the target HEAD, and read the current
governance, dynamic state, architecture, tool registry, direction, PAPER
feature-freeze/acceptance evidence, post-V0.1 roadmap, and the immutable
adopted Cross Project Operating Contract v3.1 at
`39757116c579a33affb1c58e058a43f1d3f4f6f5`.

The audit inspected `git diff origin/main...5ee1301…`, the complete target
modules and their focused tests, and their interfaces with the existing broker,
OMS, trading-state, recovery, reconciliation, safety and contract layers. It
also used minimal throwaway Python reproductions; no external call, credential
read, broker/provider connection, account mutation, or implementation change
was performed.

Verification run on the exact target:

- focused new-package test groups: PASS;
- `python -m compileall -q src tools tests`: PASS;
- `python tools/check_authority_consistency.py`: PASS;
- `git diff --check origin/main...HEAD`: PASS;
- broad `python -m unittest discover -s tests -v`: **INSUFFICIENT_EVIDENCE in
  this audit environment**. Two local child processes did not exit within the
  bounded audit command window and were stopped after identity verification;
  therefore it is not reported as a local PASS. CI #215 remains pre-audit
  configured-check evidence only.

Green tests/CI are verification evidence only. They do not resolve the findings
below because the reproductions exercise paths omitted by the tests.

## Findings summary

| ID | Severity | Concise claim | Scope |
| --- | --- | --- | --- |
| ORP-001 | HIGH | An explicitly supplied unknown/unresolved account durable state is discarded by controller preflight and can reach `READY_TEST`. | REAL controller/preflight |
| ORP-002 | HIGH | An unresolved external/manual mutation can be followed by `resume`/kill disarm and then receive `ALLOW` because the risk gate ignores the persistent safety-state mutation status. | REAL safety/risk |
| ORP-003 | HIGH | The realtime provider ledger accepts an attempt whose supplied authority identity differs from the authority to which the ledger is bound. | provider attempt control |
| ORP-004 | HIGH | CTP lifecycle events are not consumable by the existing trading-state contract; they omit required order facts and no production composition/restart bridge exists. | CTP ↔ runtime composition |
| ORP-005 | MEDIUM | `ContractFacts.identity_id` omits nested margin, fee and price-limit values; materially different facts retain the same identity and batch evidence echoes that lossy identity. | contract facts/capital evidence |

No BLOCKER or LOW finding was substantiated.

## Detailed findings

### ORP-001 — HIGH — account durable state is silently omitted

- **Location:** `src/real_runtime_controller.py:223-254`, especially
  `account_state` at line 229 and the `run_real_preflight` call at lines
  238-247; `src/real_preflight.py:159-169,381-387`.
- **Claim:** Controller preflight requires an `account_state` argument but
  never passes it onward. The lower preflight has no account-state parameter
  and its durable-state check covers only order, wake and reconciliation.
- **Reproduction:** With the bundled fully-bound TEST_ONLY fixture,
  `account_state=RealDurableState.UNKNOWN`, all other durable states `CLEAR`,
  produces `REPORT_OVERALL=READY`, no account durable check, and
  `activate_for_test()` returns `READY_TEST`.
- **Impact:** An account-truth gap can be represented as clear structural
  readiness. This contradicts the required fail-closed broker/account truth
  boundary and leaves scenario C unprotected at the controller boundary.
- **Violated invariant:** UNKNOWN/unresolved account state must prevent new
  risk/readiness; structural success must not silently erase a supplied safety
  fact.
- **Invalidates:** the controller's claimed durable-state composition; it does
  not alter accepted PAPER/V0.1 code.
- **Repair boundary:** the REAL preflight/controller durable-state schema and
  its tests; do not address it by weakening caller checks.

### ORP-002 — HIGH — persistent external mutation can be bypassed

- **Location:** `src/real_safety_state.py:199-203,245-283` and
  `src/real_risk_gate.py:424-444`.
- **Claim:** `record_external_mutation` latches
  `external_mutation_status=UNRESOLVED`, but `resume` and `disarm_kill` can
  set mode back to `NORMAL` without requiring resolution. The risk gate checks
  caller-supplied `facts.external_mutation_status`, not the persistent
  `safety_state.external_mutation_status`.
- **Reproduction:** `record_external_mutation`, `trip_kill`, then
  `disarm_kill` yields `SafetyMode.NORMAL` with persistent
  `ExternalMutationStatus.UNRESOLVED`. Supplying otherwise healthy facts with
  `external_mutation_status=RESOLVED` makes `RealRiskGate.evaluate` return
  `ALLOW` with reason `ALLOWED`.
- **Impact:** A manual/broker-side mutation that has not been reconciled can
  cease to block a risk-increasing action simply because the input bundle says
  resolved. This is an actual fail-open disagreement between the two safety
  owners.
- **Violated invariant:** unresolved external mutation must block new risk
  until coherent reconciliation restores truth; persistent safety state must
  outrank a contradictory transient input.
- **Invalidates:** REAL safety/risk composition only; accepted PAPER/V0.1
  behavior is unchanged.
- **Repair boundary:** the canonical REAL safety/risk composition boundary:
  make the persistent state authoritative and make resume/disarm preserve the
  unresolved-mutation block until an explicit coherent-resolution transition.

### ORP-003 — HIGH — provider attempt authority binding is not enforced

- **Location:** `src/realtime_provider_attempt_ledger.py:158-218` and
  `244-291`; `src/realtime_provider_control.py:154-215`.
- **Claim:** Ledger construction binds `self.authority_identity` to database
  metadata, but `record_attempt_started` never requires
  `identity.authority_identity == self.authority_identity`. Control therefore
  admits an attempt under a different authority into the ledger.
- **Reproduction:** A ledger initialized with
  `REALTIME_TEST_AUTHORITY` admitted a wake whose
  `RealtimeAttemptIdentity.authority_identity` was
  `REVOKED_OR_OTHER_AUTHORITY`. The durable attempt retained the latter value
  while the ledger metadata retained the former.
- **Impact:** The ledger's advertised authority identity no longer proves the
  authority that governed every admitted request. A future executor using this
  result could make a request under mismatched/revoked authority while still
  consuming the wrong ledger/budget namespace.
- **Violated invariant:** request identity, durable ledger and current exact
  authority must agree before an at-most-once provider attempt is admitted.
- **Invalidates:** provider-control authority evidence; it does not reopen the
  frozen V0.1 provider machinery, which is a separate module.
- **Repair boundary:** provider-attempt ledger admission validation and a
  targeted control/ledger mismatch test. Keep ceilings/authority caller-bound;
  do not invent a default authority.

### ORP-004 — HIGH — CTP adapter does not compose with the existing runtime state machine

- **Location:** `src/fangzheng_ctp_candidate.py:700-727`, in contrast with
  `src/trading_state.py:665-724`; additionally `capture_snapshot` and
  `restore_snapshot` deliberately reject at lines 587-591.
- **Claim:** The CTP `ORDER_ACKNOWLEDGED` event payload contains only
  `broker_order_id` and `lifecycle_status`; `TRADE_FILLED` contains only
  broker/trade IDs, price and quantity. Existing `TradingState` requires the
  submitted event to carry contract, direction, action and quantity, and a
  fill to carry contract, direction and action. No non-test production module
  imports/composes the new CTP, real reconciliation/recovery, REAL risk,
  contract-facts or provider-control surfaces.
- **Reproduction:** A scripted CTP acknowledgement emitted payload keys
  `broker_order_id,lifecycle_status`; a fill emitted
  `broker_order_id,broker_trade_id,price,quantity`. These cannot satisfy the
  cited `TradingState` handlers. The only out-of-order-fill test asserts that
  the adapter emits one fill event; it does not apply it to `TradingState` or
  an end-to-end recovery path.
- **Impact:** The package cannot prove safe submit/ack/fill/restart paths
  against the project's existing durable order state. In particular, scenarios
  A–F and the required callback-reordering claim are not established by a
  composed implementation; CTP's in-memory `_submitted` map also cannot
  persist the unknown-submit state across restart.
- **Violated invariant:** one canonical order identity/lifecycle must remain
  reconcilable across adapter, OMS, trading state, broker truth and recovery;
  UNKNOWN-after-submit must be persistent and fail closed.
- **Invalidates:** the combined REAL-prebuild composition claim, not the
  accepted PAPER or frozen V0.1 implementation (the target adds files only).
- **Repair boundary:** a single explicit REAL execution composition/recovery
  seam, including the lossless adapter-to-runtime event contract and durable
  project/broker identity mapping. Do not solve this by making `TradingState`
  accept incomplete events.

### ORP-005 — MEDIUM — material contract facts do not change the public facts identity

- **Location:** `src/contract_facts.py:347-373`; identity propagated by
  `src/capital_adequacy_batch.py:416,572`.
- **Claim:** `ContractFacts.identity_id` binds only `margin_basis` plus
  boolean presence flags for fee/price limits. It omits every nested margin
  amount/percentage, fee amount/percentage/currency and price-limit bound/basis
  value.
- **Reproduction:** Two otherwise identical current contract facts, one with
  initial margin `4500` and fee `5`, another with initial margin `9999` and fee
  `777`, return the identical `ContractFacts.identity_id`.
- **Impact:** Evidence that records only the facts identity (including the
  capital batch result) cannot distinguish materially different economic
  inputs. A snapshot's deeper hash currently masks this only when every caller
  carries a snapshot rather than the documented facts identity.
- **Violated invariant:** a semantic identity/hash must bind every field whose
  change alters the fact set and capital calculation.
- **Invalidates:** contract/capital evidence identity, locally; it does not
  affect accepted PAPER/V0.1 behavior.
- **Repair boundary:** `ContractFacts` canonical identity plus mutation tests
  for all nested margin, fee and price-limit fields. Preserve the separate
  contract-identity key used for store lookup.

## Primary adversarial-question record

| Questions | Result | Basis |
| --- | --- | --- |
| 1 | NO_FINDING | New modules are offline-only/injected; source inspection found no network/vendor SDK/credential value path. |
| 2 | NO_FINDING | Controller exposes `READY_TEST` only and external activation is always false. |
| 3 | NO_FINDING | Target diff is additive; no frozen PAPER/V0.1 files or tool status changed. |
| 4 | NO_FINDING | CTP SDK is not imported; transport is injected. Future vendor semantic evidence remains unavailable. |
| 5–12 | HIGH: ORP-004 | Identity/lifecycle fields are lost at the CTP-to-runtime boundary and unknown submit is not durably composed. |
| 13–15 | HIGH: ORP-002; INSUFFICIENT_EVIDENCE for live broker proof | Pure reconciliation detects typed differences, but its result is not wired to persistent safety/risk. |
| 16–19 | HIGH: ORP-002 | Gate classification is otherwise conservative, but its persistent external-mutation invariant is bypassable. |
| 20 | HIGH: ORP-001 | Unknown account state can reach structural `READY_TEST`; it still cannot authorize external activation. |
| 21–22 | NO_FINDING | Authority expiry/revocation and UNKNOWN health are fail-closed in the inspected pure paths. |
| 23–25 | NO_FINDING | Wake uniqueness and zero retry are enforced locally. |
| 26–27 | HIGH: ORP-003 | No numeric defaults were found, but authority binding of an admitted attempt is inconsistent. SQLite race behavior is INSUFFICIENT_EVIDENCE beyond the local single-process tests. |
| 28–29 | NO_FINDING | Source/freshness categories and replacement policy are explicit and fail closed. |
| 30 | MEDIUM: ORP-005 | Facts identity omits material nested values. |
| 31 | NO_FINDING | Store replacement keeps higher-quality current snapshots over lower/older input. |
| 32–36 | NO_FINDING | Decimal/unit separation and missing-value fail closure were substantiated; no RMB 100k default was found. |
| 37–38 | HIGH: ORP-004 | New abstractions are isolated rather than composed through one runtime state owner. |
| 39 | HIGH: ORP-001–004 | Focused tests miss the reproduced paths and do not exercise the CTP-to-state-machine integration. |
| 40 | INSUFFICIENT_EVIDENCE | Offline tests cover local SQLite reopening but not Windows locking/recovery under a real transport. |
| 41 | NO_FINDING | New modules reject/avoid secret values and report public non-secret identities only. |
| 42 | NO_FINDING | Inspected module docs consistently state OFFLINE/TEST_ONLY boundaries; no stronger supported readiness claim was found. |

## Required scenario record

| Scenario | Result |
| --- | --- |
| A–C | HIGH: ORP-004; persistent CTP submit truth and its bridge to complete broker reconciliation/recovery are absent. |
| D–E | HIGH: ORP-004; adapter-local duplicate handling exists, but no end-to-end CTP event → trading state proof exists. |
| F | HIGH: ORP-002; unresolved mutation can be bypassed in safety/risk composition. |
| G | NO_FINDING | Ledger keeps a durable started/unknown attempt and blocks duplicate wake locally. |
| H | HIGH: ORP-001 | Unknown account state does not block structural readiness. External authorization remains unavailable. |
| I | MEDIUM: ORP-005 | Nested economic facts can change without changing `ContractFacts.identity_id`. |
| J | NO_FINDING | One-lot calculator returns insufficient evidence for missing fee/margin. |

## Important independently checked areas with no finding

- The target's imports do not load an unadopted CTP SDK or perform a network,
  broker/provider, account, secret or real-money operation.
- REAL structural fixture status cannot become external execution authority.
- CTP callback duplicate IDs with different content, stale trading-day input,
  disconnects and incomplete scripted query paths fail closed within the adapter.
- Pure reconciliation distinguishes incomplete/stale/failed/unknown query
  statuses and does not promote them to complete broker truth.
- Risk policy defaults are unbound; missing margin/fee/slippage/constraints do
  not create a capital PASS, and the approximate RMB 100,000 envelope is not a
  code default.
- Provider wake uniqueness, fixed zero retry and crash-start persistence work
  for the tested single-ledger path.
- Contract snapshot replacement and snapshot deep-content identity correctly
  protect the tested snapshot store path.

## Verdict

`AUDIT_VERDICT = REPAIR_REQUIRED`

The bounded OFFLINE package contains four HIGH safety/composition defects and
one MEDIUM evidence-identity defect. This verdict is not a claim about PAPER,
external CTP readiness, real broker evidence, real-money readiness, or any
permission to perform an external action.
