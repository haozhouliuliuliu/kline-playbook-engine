# KNOWN_LIMITATIONS_AND_TECH_DEBT

As of: `2026-08-25`

Current limitations only. Closed provider-selection/Stage-A issues belong in Git history, not here.

## 1. DeepSeek output guard not fully hardened

Observed failure mode: an enum field can contain a valid value plus explanatory prose, making the response mechanically unscoreable even when reasoning is coherent.

Required fix:

`STRICT_OUTPUT_ENUM_ENFORCEMENT`

Status: `OPEN`

## 2. 4H volume reasoning guard not fully hardened

Observed failure mode: DeepSeek once attempted invalid exact reconciliation between 4H volume and overlapping lower-timeframe volume.

Required fix:

`NO_4H_EXACT_VOLUME_RECONCILIATION`

Status: `OPEN`

## 3. Persistent trader memory is not implemented yet

The current codebase has foundational AI-trader types, replay/data/chart machinery and audit concepts, but does not yet provide the final project-owned persistent memory system spanning calls/restarts.

Needed capabilities include:

- working-memory persistence;
- journal persistence;
- hypothesis-memory persistence;
- relevant-case retrieval;
- mutation audit;
- explicit separation of Jianghe canon / DS hypotheses / validated project policy.

Status: `OPEN`

## 4. DeepSeek Harness is not yet verified

Harness is only a project admission candidate.

Still unverified for this project:

- pinned compatible version/commit;
- exact `deepseek-v4-flash-vision-exp` route;
- image/K-line input on that route;
- restart persistence;
- integration with project-owned memory/tools;
- audit fidelity;
- absence of silent retry/model/prompt changes;
- portability if Harness is removed.

Status: `OPEN`

## 5. Persistent chronological replay is not implemented end-to-end

The accepted historical corpus exists, but the project has not yet run the intended life-like replay of one persistent trader through time with governed memory and deterministic wake policy.

Do not substitute stateless independent API calls and call that equivalent evidence.

Status: `OPEN`

## 6. Experience-derived policy promotion pipeline is not implemented

The required conceptual path exists in `PROJECT_DIRECTION.md`, but tooling/storage for:

- hypothesis identity;
- falsification/counterexample search;
- discovery-exposure lineage;
- independent validation;
- policy promotion/versioning;

still needs implementation before DeepSeek is allowed to improve active trading policy from its own experience.

Status: `OPEN`

## 7. No protected validation / shadow / broker / real-money lane is open

This is an authorization boundary, not an implementation bug.

Current state:

- validation/holdout locked;
- shadow locked;
- broker/account locked;
- real money locked.

Status: `LOCKED_BY_CURRENT_AUTHORITY`

## 8. Long-run model stability is not yet demonstrated

DeepSeek is the sole active model source, but that does not prove long-horizon stability, production reliability or profitability of the future persistent trader identity.

Those require later evidence after the memory/runtime identity is stable.

Status: `OPEN_FUTURE_EVIDENCE`
