# JIANGHE PAPER PREBUILD ENGINEERING STATUS — 2026-08-27

Status: `CURRENT_HANDOFF_EVIDENCE__OFFLINE_ENGINEERING_IN_PROGRESS`

This file records evidence/status for the offline PAPER prebuild package. `CURRENT_STATE.md` remains the sole dynamic-state owner and wins if this snapshot later becomes stale.

## 1. Canonical parent / authority

Canonical main when this status was prepared:

`54aefc9a2a8841415308a8e5a49c1a14a7ff859a`

Current offline-prebuild Owner authority:

`docs/reviews/JIANGHE_PAPER_PREBUILD_PARALLEL_ENGINEERING_OWNER_DECISION_2026-08-27.md`

That authority permits outcome-independent offline PAPER infrastructure engineering and parallel isolated workers. It does not authorize account login/connect, PAPER order actions, provider spend, full V0.1 execution, post-V0.1 paid replay, or real money.

## 2. Integration mainline

Open integration PR:

`#56 Paper execution readiness foundation V0.1`

Integration branch:

`integration/paper-readiness-v01-20260827`

Observed integration head when recorded:

`61f47c87d89035f856021ef1e7235f2815f34076`

Latest observed CI for that head:

- GitHub Actions `Repository CI` run `#151` / run id `33059066123`;
- conclusion: `success`.

The integration branch is the only PAPER-readiness integration lane. It must not be treated as canonical main until project-brain review/integration.

## 3. Offline capability already implemented on PR #56

Observed changed capability surface includes:

- restored project-owned runtime orchestration seam: `src/shadow_runtime.py`;
- broker-neutral Jianghe decision-to-execution bridge: `src/jianghe_execution_bridge.py`;
- broker-neutral live closed-bar normalization/tracker: `src/live_market_data.py`;
- live-capable market-context work: `src/market_context.py`;
- separate PAPER connection/order machine gate: `src/paper_execution_authority.py`;
- result-dependent activation bindings: `src/paper_activation_profile.py`;
- broker/account truth mirror: `src/paper_broker_mirror.py`;
- durable external order submission attempt journal: `src/paper_order_journal.py`;
- durable real-time wake journal: `src/paper_wake_journal.py`;
- fail-closed startup/readiness supervisor: `src/paper_supervisor.py`;
- broker-neutral TqSdk candidate adapter: `src/tqsdk_paper_candidate.py`;
- offline-testable TqSdk object/order driver: `src/tqsdk_paper_driver.py`;
- deterministic PAPER-readiness/foundation/supervisor tests.

Key implemented invariants already present on the integration branch include:

- account connect permission and external order permission are separate;
- import/construction of PAPER candidate code performs no login/network/credential action;
- missing sizing/price/close-offset/risk/adapter activation bindings cannot silently become ACTIVE;
- strategy decisions that lack frozen executable order semantics fail closed rather than invent quantity/order details;
- broker/account truth is mirrored from external snapshots rather than inferred from synthetic local accounting;
- external order submission is durably journaled before broker submit is attempted;
- an exception after submit-attempt start becomes an unresolved/unknown submission rather than `not sent`;
- real-time wake dispatch is durably recorded so restart cannot silently dispatch the same admitted wake twice;
- unresolved wake dispatches and unresolved order attempts block readiness;
- broker/account snapshot, unknown external orders, market bootstrap/sequence health, trader readiness and execution authority are composed by the PAPER supervisor;
- no external PAPER action was performed by this engineering package.

## 4. Important capability gaps still open

The package is not yet complete. Known outcome-independent work still required includes at least:

### A. Real-time causal context path

The current live tracker normalizes closed bars and enforces bootstrap/watermark/sequence checks, but the final PAPER path still needs a project-owned streaming causal context builder from live 1m substrate to the architecture-required:

`5m wake + 15m / 1H / 4H context`

It must preserve governed session boundaries, causal availability and restart/duplicate invariants without pretending live bars are historical dataset rows.

### B. External order lifecycle recovery

The existing `PaperOrderJournal` strongly covers submit-attempt ambiguity, but cancel/replace/reconnect/restart/UNKNOWN lifecycle handling still needs a consolidated high-assurance implementation/review. External account truth must resolve project ledger state before new risk is admitted.

### C. Runtime composition

`PaperRuntimeSupervisor` is currently a pure readiness composition layer; the final login-time startup sequence and fake end-to-end runtime drill still need to prove the intended state transition:

`authority -> connect eligibility -> account snapshot/reconciliation -> market bootstrap -> market sequence clean -> trader observation ready -> order gate separately ready`

without allowing order submission before all required bindings are explicit.

### D. Result-dependent activation settings remain intentionally unbound

Do not freeze or invent before the applicable evidence/Owner decision:

- sizing/lot policy;
- execution price policy;
- SHFE/INE close-offset policy when trade-day inventory matters;
- permanent numeric risk limits;
- final PAPER contract whitelist.

Interfaces/profile bindings may be completed now; values remain fail-closed.

### E. TqSdk PAPER role status

`TOOL_REGISTRY.md` currently adopts TqSdk only for historical concrete-contract 1m research acquisition at version `3.10.1`. That adoption must not be silently stretched into PAPER connectivity/order submission. A later targeted verification/adoption step is required before actual account connection.

## 5. Pre-created isolated worker branches

The project brain pre-created two isolated branches for the next parallel step:

- `flash/paper-live-context-v01-20260827`
- `codex/paper-order-recovery-v01-20260827`

They are worker branches only. Workers must not edit `main`, `CURRENT_STATE.md`, Owner authority, PR #56 integration branch directly, or each other's worktree.

Because the integration branch continued after branch creation, each worker must first inspect divergence. If its assigned branch contains no worker-specific commits and is merely behind, fast-forward it to the latest `origin/integration/paper-readiness-v01-20260827` before editing. Never overwrite unknown existing work.

## 6. Assigned next parallel scopes

### Flash — live causal context branch

Own only:

- live 1m substrate aggregation to 5m/15m/1H/4H;
- session-aware causal completeness;
- 5m wake/context emission;
- restart/reconnect continuity at the market/context layer;
- deterministic tests/fault cases.

Do not touch external order lifecycle, broker authority, credentials, provider calls, `CURRENT_STATE.md`, or main/integration branches.

### Codex — external order/recovery branch

Own only:

- submit/cancel/replace attempt accounting;
- restart/reconnect resolution against broker truth;
- unresolved/UNKNOWN state fail-closed behavior;
- duplicate prevention;
- partial fill/cancel/reject/order-state mapping and adversarial tests;
- high-assurance review/repair of this scoped execution boundary.

Do not touch live market aggregation/trader cognition semantics, credentials, real account connectivity, `CURRENT_STATE.md`, or main/integration branches.

## 7. Integration sequence after workers finish

The project brain / next integration lane should:

1. refresh canonical main and this status through `CURRENT_STATE.md`;
2. inspect each worker branch by diff/tests, not worker prose;
3. integrate Flash scope into `integration/paper-readiness-v01-20260827`;
4. integrate Codex scope into the same integration branch;
5. resolve overlap only in the integration lane;
6. run focused tests + full repository CI on Linux/Windows;
7. complete the remaining PAPER supervisor/fake end-to-end runtime composition;
8. update `docs/evidence/PAPER_EXECUTION_ASSET_AND_READINESS_AUDIT_2026-08-27.md` or successor current evidence with accepted facts;
9. run one consolidated targeted PAPER-readiness adversarial audit/repair package required by the Owner decision;
10. only after that package is accepted should PR #56 be considered for merge to main.

## 8. Consequential actions remain locked

At this handoff:

- PAPER account login/connect: `NOT_AUTHORIZED`;
- PAPER order submit/cancel/replace: `NOT_AUTHORIZED`;
- broker/account mutation: `NOT_AUTHORIZED`;
- real money: `NOT_AUTHORIZED`;
- new provider paid calls: only under separate exact authority;
- full V0.1 paid replay: still requires separate exact Owner/machine authority.

No secret value is required or permitted in repository evidence.
