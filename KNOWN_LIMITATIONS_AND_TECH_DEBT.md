# KNOWN_LIMITATIONS_AND_TECH_DEBT

As of: `2026-08-26`

## 1. Persistent chronological replay is not implemented end-to-end

The minimal persistent DeepSeek trader prototype is complete and locally accepted, but one life-like chronological replay of the persistent trader has not yet been implemented or executed end-to-end.

A future replay package must preserve causal availability, persistent memory, trader identity, bounded context/retrieval, auditable wake decisions and the existing mechanical guards. It must not be confused with mass independent stateless prompt exams.

Status: `OPEN_FUTURE_WORK_PACKAGE`

## 2. Harness patch is project-required

The admitted local Harness runtime is pinned to `0.1.1-rc.2` / `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` and requires the project fail-closed DeepSeek transport patch under `integrations/deepseek-harness/` plus `maxRetries: 0`.

Do not replace it with an unpatched upstream build without a new admission verification.

Status: `CONTROLLED_DEPENDENCY`

## 3. Windows rejected-constructor SQLite cleanup remains imperfect

A deliberately rejected mismatched-trader `PersistentTraderStore` constructor can leave its SQLite connection open until Python cleanup/GC. On Windows, same-process immediate deletion of that temporary database may therefore receive `WinError 32`.

The identity mismatch itself remains fail-closed. Native Windows prototype acceptance and the real offline CLI probe both pass. This is cleanup/resource-lifetime technical debt, not a failed prototype objective.

Status: `OPEN_TECH_DEBT__NON_ACCEPTANCE_BLOCKING`

## 4. Experience-derived policy promotion pipeline is not implemented

Still required later:

- governed hypothesis identity/lineage at replay scale;
- falsification/counterexample search workflow;
- discovery-exposure lineage;
- independent validation;
- policy promotion/versioning.

`DS_HYPOTHESIS_MEMORY` remains non-executable and may not self-promote into active policy.

Status: `OPEN_FUTURE_WORK`

## 5. Protected lanes are locked

- paid provider calls: `PAUSED`;
- `NEXT_EXPLICIT_PAID_SLOT = NONE`;
- validation/holdout: locked;
- shadow: locked;
- broker/account: locked;
- real money: locked.

Status: `LOCKED_BY_CURRENT_AUTHORITY`

## 6. Long-run stability and profitability are not demonstrated

Prototype completion proves the governed local runtime/memory/retrieval/tool/audit composition, not long-horizon trading quality, production reliability or profitability.

No current evidence establishes profitable historical performance, robust generalization, live/shadow performance, or production readiness. Those require later explicitly governed research/protected evidence.

Status: `OPEN_FUTURE_EVIDENCE`
