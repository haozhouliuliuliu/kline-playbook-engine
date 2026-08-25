# KNOWN_LIMITATIONS_AND_TECH_DEBT

As of: `2026-08-26`

## 1. DeepSeek output guard not fully hardened

A machine enum field can contain a valid value plus explanatory prose, making the response mechanically invalid.

Required fix:

`STRICT_OUTPUT_ENUM_ENFORCEMENT`

Status: `OPEN`

## 2. 4H volume reasoning guard not fully hardened

DeepSeek must not perform exact reconciliation between 4H volume and overlapping lower-timeframe volume.

Required fix:

`NO_4H_EXACT_VOLUME_RECONCILIATION`

Status: `OPEN`

## 3. Persistent trader memory is not implemented yet

Needed capabilities include:

- working-memory persistence;
- journal persistence;
- hypothesis-memory persistence;
- relevant-case retrieval;
- mutation audit;
- explicit separation of Jianghe canon, DeepSeek hypotheses and validated project policy.

Status: `OPEN`

## 4. DeepSeek Harness is not yet verified

Still unverified for this project:

- pinned compatible version/commit;
- exact `deepseek-v4-flash-vision-exp` route;
- image/K-line input on that route;
- restart persistence;
- integration with project-owned memory/tools;
- audit fidelity;
- absence of silent retry/model/prompt changes;
- portability if the runtime shell changes.

Status: `OPEN`

## 5. Persistent chronological replay is not implemented end-to-end

The accepted historical corpus exists, but the project has not yet run the intended life-like replay of one persistent trader through time with governed memory and deterministic wake policy.

Status: `OPEN`

## 6. Experience-derived policy promotion pipeline is not implemented

Tooling/storage is still required for:

- hypothesis identity;
- falsification/counterexample search;
- discovery-exposure lineage;
- independent validation;
- policy promotion/versioning.

Status: `OPEN`

## 7. Protected execution/research lanes are locked

Current state:

- validation/holdout locked;
- shadow locked;
- broker/account locked;
- real money locked.

Status: `LOCKED_BY_CURRENT_AUTHORITY`

## 8. Long-run model stability is not yet demonstrated

The current trader identity has not yet established long-horizon stability, production reliability or profitability. Those require later protected evidence after memory/runtime identity is stable.

Status: `OPEN_FUTURE_EVIDENCE`
