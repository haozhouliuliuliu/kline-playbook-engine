# KNOWN_LIMITATIONS_AND_TECH_DEBT

Status: `CURRENT_DEBT_REGISTER`

This file owns unresolved capability limitations and technical debt only.

It must not copy the current work package, phase, locks, paid-slot state or next task. Read `CURRENT_STATE.md` for current project status.

## 1. Windows rejected-constructor SQLite cleanup

A deliberately rejected mismatched-trader `PersistentTraderStore` constructor can leave its SQLite connection open until Python cleanup/GC. On Windows, same-process immediate deletion of that temporary database may therefore receive `WinError 32`.

The identity mismatch itself remains fail-closed. This is cleanup/resource-lifetime technical debt, not a trader-state acceptance failure.

Status: `OPEN_TECH_DEBT__NON_ACCEPTANCE_BLOCKING`

## 2. Experience-derived policy promotion pipeline is incomplete

Later governed learning still requires a complete evidence/promotion path at production/replay scale, including as applicable:

- hypothesis identity and lineage;
- falsification/counterexample search;
- discovery-exposure lineage;
- independent validation;
- policy promotion/versioning.

`DS_HYPOTHESIS_MEMORY` remains non-executable until such a path is explicitly governed and accepted.

Status: `OPEN_FUTURE_CAPABILITY`

## 3. Long-run trading quality is not demonstrated

Existing engineering/replay evidence can establish runtime, lifecycle, causality, memory, audit and execution-path properties without establishing long-horizon profitability or robust cross-market generalization.

Long-term edge remains a separate evidence question.

Status: `OPEN_FUTURE_EVIDENCE`

## 4. Paper/real execution reliability remains future evidence

Future consequential execution requires real-time ingestion, OMS/order lifecycle, reconciliation, restart/reconnect safety, duplicate prevention, risk rejection, provider/data failure handling and account truth to be proven under the applicable future authority.

Architecture direction alone is not evidence that these future modes are ready.

Status: `OPEN_FUTURE_CAPABILITY_AND_EVIDENCE`

## 5. Governance anti-drift enforcement

The repository historically allowed duplicated volatile state and did not mechanically check authority ownership. The governance ownership repair introduces a canonical-owner model and repository consistency checker.

Until that checker is integrated and passing on `main`, governance drift prevention remains incomplete.

Status: `OPEN_UNTIL_GOVERNANCE_REPAIR_ACCEPTED`

## Maintenance rule

A debt item belongs here only while it is genuinely unresolved and useful for future work.

When resolved, remove it from the active file and rely on Git history/evidence for historical record.

Do not add current phase/authorization status here.
