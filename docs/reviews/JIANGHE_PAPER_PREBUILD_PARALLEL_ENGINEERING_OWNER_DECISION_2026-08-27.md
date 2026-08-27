# JIANGHE PAPER PREBUILD PARALLEL ENGINEERING — OWNER DECISION

Status: `OWNER_APPROVED__OFFLINE_PREBUILD_ONLY__NO_ACCOUNT_OR_ORDER_AUTHORITY`

Date: `2026-08-27`

Product: `JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

## 1. Owner direction

The Owner explicitly approves accelerating engineering that is not dependent on the pending full frozen V0.1 / later CU-RB research outcomes, so that the project can approach a state where, after the required historical research closes, PAPER can begin with minimal remaining engineering.

Approved engineering mode:

```text
ONE INTEGRATION MAINLINE
+
PARALLEL ISOLATED WORKER BRANCHES/WORKTREES
+
FINAL SINGLE TARGETED PAPER-READINESS AUDIT/REPAIR PACKAGE
```

The project brain remains the single process/integration owner.

## 2. Scope allowed now

The following work is approved as ordinary offline engineering and may proceed before the full V0.1 / CU-RB research sequence is complete:

- broker-neutral real-time closed-bar ingestion;
- causal real-time 1m -> 5m / 15m / 1H / 4H aggregation infrastructure consistent with existing architecture principles;
- persistent 5m wake admission / duplicate prevention / restart recovery;
- real-time context assembly plumbing that does not alter frozen historical research semantics;
- PAPER runtime/supervisor startup-state machine;
- broker/account truth mirrors and reconciliation infrastructure;
- broker-neutral TqSdk PAPER candidate adapter/driver code using offline fakes only;
- project-owned order identity/idempotency journals;
- submit/cancel/replace attempt accounting and UNKNOWN fail-closed recovery infrastructure;
- activation profiles and machine-verifiable connect/order gates;
- fault injection, deterministic tests, CI, evidence, documentation;
- restoration/refactoring of still-required execution capability layers when current architecture clearly owns the behavior;
- independent high-assurance review where consequential execution infrastructure warrants it.

Ordinary defects discovered within this bounded engineering package should be repaired and retested without repeated Owner round-trips.

## 3. Explicitly NOT authorized by this decision

This decision does **not** authorize:

- logging into or connecting to a live PAPER/simulation broker/account;
- reading or using account credentials for external connectivity;
- submitting, cancelling, replacing, or otherwise mutating any external PAPER order/account state;
- any real broker/account action;
- any real-money action;
- any paid DeepSeek/provider call beyond separately authorized provider work;
- starting full frozen V0.1 provider replay;
- starting post-V0.1 CU/RB paid replay;
- changing frozen V0.1 research semantics;
- skipping the approved historical -> PAPER promotion route;
- freezing strategy-result-dependent sizing, pricing, close-offset, permanent risk, product, or other execution semantics before the relevant evidence/Owner decision exists.

`PAPER_CONNECT = NOT_AUTHORIZED`

`PAPER_ORDER_SUBMIT = NOT_AUTHORIZED`

`BROKER_ACCOUNT_ACTION = NOT_AUTHORIZED`

`REAL_MONEY = NOT_AUTHORIZED`

## 4. Result-dependent boundary

Infrastructure should be designed so that strategy/research-dependent settings can be bound later through an explicit activation profile rather than requiring core rewrites.

Until separately frozen/approved, the runtime must fail closed rather than invent:

- order quantity / sizing;
- execution price policy;
- SHFE/INE close-today vs close-yesterday mechanics when policy is not explicit;
- permanent numeric risk limits;
- final PAPER contract whitelist;
- any other outcome-affecting execution semantic not already owned by canonical authority.

## 5. Parallel worker rule

Parallelism is approved only with repository isolation:

- exactly one integration lane owns the shared PAPER-readiness integration branch and later `main` integration;
- Flash/Codex workers use separate branches/worktrees;
- workers do not edit `main`, `CURRENT_STATE.md`, shared Owner authority, or another worker's worktree;
- worker output is not canonical fact until reviewed/integrated by the project brain;
- no two workers may share a consequential external runtime/account state.

## 6. Final acceptance requirement

After all outcome-independent PAPER prebuild engineering is integrated, perform **one consolidated targeted adversarial PAPER-readiness audit and repair package** covering at least:

- real-time causal data construction;
- wake persistence/restart/duplicate prevention;
- cognition/context continuity plumbing;
- startup/reconnect sequencing;
- broker/account truth and reconciliation;
- submit/cancel/replace idempotency;
- UNKNOWN order-state handling;
- partial fill/cancel/reject paths;
- stale/missing/out-of-order data fail-closed behavior;
- account/order mismatch fail-closed behavior;
- execution authority boundaries;
- activation-profile completeness;
- secret handling;
- audit/evidence completeness;
- Linux/Windows CI and deterministic fault-injection coverage.

Repair ordinary findings inside that same audit package where canonical authority determines the correct behavior.

## 7. Promotion semantics unchanged

This decision is an engineering acceleration/sequencing authority only.

It does not change the approved product route in `PROJECT_DIRECTION.md` and `docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`.

Historical research remains a prerequisite to formally activating real-time PAPER. The purpose of this decision is to make the eventual PAPER transition operationally close to `login -> verify account/data -> bind final approved activation profile -> run`, rather than beginning infrastructure construction at that later point.
