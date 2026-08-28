# PAPER EXECUTION ASSET AND READINESS AUDIT

Status: `OFFLINE_ENGINEERING_READINESS_FOUNDATION_IMPLEMENTED__EXTERNAL_ACCOUNT_ACTION_NOT_EXECUTED`

Date: `2026-08-27`

Scope: project asset verification and offline downstream engineering requested by the Owner while the full frozen V0.1 paid replay is deferred. This audit does **not** authorize or record any broker/paper-account login, network order, provider call, credential read or real-money action.

## 1. Headline

The repository already contained most broker-neutral execution primitives needed for PAPER, but current `main` had a material capability-layer gap: the project-owned runtime orchestrator `src/shadow_runtime.py` had been removed by historical cleanup while its dependent execution components and `tests/runtime_synthetic_fixture.py` remained.

This package restores that orchestration capability seam without reviving stale product state, and adds current fail-closed boundaries for future Jianghe PAPER integration.

Current readiness classification after this package:

- deterministic local synthetic paper execution chain: `READY / TESTED`;
- OMS/order lifecycle: `READY / EXISTING`;
- broker/account/position reconciliation: `READY / EXISTING`;
- safety, disconnect and fail-closed recovery primitives: `READY / EXISTING`;
- external PAPER connect/order machine gate: `IMPLEMENTED OFFLINE`;
- Jianghe normalized decision -> executable order semantics: `FAIL_CLOSED SEAM IMPLEMENTED`, final execution policy not frozen;
- TqSdk as external PAPER/live role: `CANDIDATE ONLY`, not project-verified/adopted for this role;
- actual TqKq/TqSim account login/network order smoke: `NOT EXECUTED / OWNER BROKER-ACCOUNT GATE`;
- real-time TqSdk market-data ingestion into Jianghe wake/context path: `NOT YET VERIFIED`;
- real broker/real money: `LOCKED`.

## 2. Existing assets verified

### Broker-neutral order surface

`src/broker_adapter.py` already defines project-owned generic order instructions, account/position/order snapshots and the `BrokerAdapter` interface. Core logic therefore does not need to bind directly to TqSdk/CTP private structures.

### Deterministic local paper broker

`src/paper_broker.py` already supports deterministic local paper account truth, order submission/cancel/replace, acknowledgement/fill/reject events, completed-bar fills, stop/ambiguity handling, snapshots and restart restoration. It is synthetic/local only, not an external brokerage simulation account.

### OMS

`src/order_management.py` already owns deterministic client/order identity, duplicate prevention, create/cancel/replace lifecycle and broker-event application.

### Reconciliation and safety

`src/reconciliation.py`, `src/safety.py`, `src/runtime_recovery.py`, `src/runtime_events.py`, `src/runtime_ledger.py` and `src/trading_state.py` already provide the broker-truth-first reconciliation, disconnect/staleness/mismatch fail-closed handling, event identity/idempotency, restart reconstruction and immutable audit primitives required by the current architecture.

### RiskGate

`src/risk_gate.py` already provides the deterministic veto surface. Its current numeric rule values are fixture/test rules, not permanent PAPER/REAL Jianghe risk semantics.

## 3. Capability-layer deletion found and repaired

Git history proves `src/shadow_runtime.py` existed before cleanup and was deleted in commit `3fe687e0834d079f856b407fe865c27d44b26d7c` (`chore: consolidate current fact surface`). The execution primitives listed above survived, and `tests/runtime_synthetic_fixture.py` continued to import `src.shadow_runtime.RuntimeConfiguration`.

The package restores the exact previously implemented project-owned orchestration module from its immutable Git blob (`6315af8b87807fd2069986aa709ebb301d527e21`) as a capability seam. This is not restoration of deleted dynamic project state or stale architecture authority. Current architecture remains owned by `ARCHITECTURE_BASELINE.md` and the current Jianghe execution architecture.

New regression coverage proves the restored runtime can execute a synthetic completed bar through:

`MarketContext -> intent -> RiskGate -> OMS -> PaperBroker -> broker events -> TradingState -> reconciliation/safety`.

## 4. New external PAPER authority boundary

`src/paper_execution_authority.py` adds a machine-verifiable generic PAPER execution authority form with separate permissions:

- `allow_connect`;
- `allow_order_submit`.

No action is allowed merely because a credential exists. `PENDING`/`REVOKED` are fail-closed. Order permission implies connection permission. Optional exact-contract scope can be bound. Authority objects store credential environment-variable names only, never secret values.

Disconnect remains a safety action and is always permitted by the adapter.

## 5. TqSdk PAPER candidate seam

`src/tqsdk_paper_candidate.py` adds `TqSdkPaperBrokerAdapter` behind the existing project-owned `BrokerAdapter` surface.

The adapter itself imports no TqSdk package, reads no credential and opens no network connection. An injected TqSdk driver must translate third-party objects into project-owned `BrokerEvent` and snapshot types. Connect and order paths are mechanically blocked unless an ACTIVE PAPER authority permits them.

Official TqSdk documentation was checked during this audit and confirms current TqSdk provides:

- `TqSim` local simulated trading;
- `TqKq` persistent 快期 simulated account behavior;
- `insert_order()` / `cancel_order()`;
- account, position and order queries;
- real-time quote/K-line update surfaces.

That upstream capability does **not** make the role project VERIFIED/ADOPTED. The current adopted TqSdk role remains historical concrete-contract 1m acquisition only until separate PAPER/live verification is completed.

## 6. Jianghe execution-semantic boundary

The active `JIANGHE_RUNTIME_RESPONSE_V0_2` expresses trading judgment (`WAIT/WATCH/CANDIDATE/ENTER/MANAGE/EXIT`, direction, hypothesis, locations, trigger, invalidation) but does not freeze broker order quantity, order type, exact entry pricing or permanent sizing/risk policy.

`src/jianghe_execution_bridge.py` therefore implements the safe forward seam:

- `WAIT / NO_TRADE / WATCH / CANDIDATE` -> deterministic `HOLD`, zero external order;
- `ENTER / MANAGE / EXIT` -> fail closed with `ExecutionSemanticsRequired` unless an explicit project-owned `JiangheExecutionPolicy` is supplied;
- the bridge never parses quantity/order facts from free-text rationale.

This lets the infrastructure be completed now without silently freezing Jianghe execution semantics that still require an Owner decision before live PAPER order creation.

## 7. Offline regression coverage

`tests/test_paper_execution_readiness.py` covers:

- restored local paper runtime end-to-end order/fill/reconciliation;
- external PAPER connect blocked without authority;
- connect-only authority cannot submit orders;
- ACTIVE connect+order authority can reach the injected fake driver;
- cancel path through the gated adapter;
- Jianghe non-executable actions produce no order;
- Jianghe ENTER fails closed without explicit execution semantics;
- malformed authority cannot allow order without connect;
- secret values cannot be embedded in credential-name authority fields.

No test performs a provider request or network broker/account action.

## 8. What is still required before real PAPER operation

The following are deliberately not claimed complete by this package:

1. implement and independently verify a concrete TqSdk driver that maps TqApi/TqKq order, fill, cancel, reject, account and position updates into project-owned generic events/snapshots;
2. implement/verify the real-time market-data ingestion/wake path for closed 5m bars and causal 4H/1H/15m/5m Jianghe observations;
3. freeze the PAPER execution semantics needed to turn Jianghe `ENTER/MANAGE/EXIT` into exact quantity/order instructions without giving DeepSeek project-operator responsibility;
4. create a future exact Owner + machine PAPER authority with credential-location seams and exact account/contract scope;
5. only then perform a bounded external TqKq connectivity/order/cancel/reconciliation smoke.

These remaining items are separable: items 1-3 can continue offline; item 4-5 cross the broker/account consequential-action gate.

## 9. Full V0.1 relationship

This work does not modify or complete the frozen V0.1 research experiment. Full V0.1 remains technically ready but its paid execution is deferred by current Owner sequencing. No post-V0.1 historical research result is assumed.

The purpose of this package is to reduce the engineering gap after historical validation so later PAPER promotion can reuse the same project-owned execution chain instead of starting from a new implementation.
