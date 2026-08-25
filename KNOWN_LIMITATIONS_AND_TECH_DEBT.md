# KNOWN_LIMITATIONS_AND_TECH_DEBT

As of: `2026-08-26`

## 1. Persistent trader prototype is not implemented yet

Still required:

- durable project-owned `DS_WORKING_MEMORY`;
- `DS_JOURNAL` persistence;
- `DS_HYPOTHESIS_MEMORY` persistence;
- bounded Jianghe retrieval;
- project-owned K-line/market tools;
- complete request/retrieval/tool/memory audit;
- restart continuity in the actual project composition.

Status: `OPEN__NEXT_WORK_PACKAGE`

## 2. Harness patch is project-required

The admitted local Harness runtime is pinned to `0.1.1-rc.2` / `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` and requires the project fail-closed DeepSeek transport patch under `integrations/deepseek-harness/` plus `maxRetries: 0`.

Do not replace it with an unpatched upstream build without a new admission verification.

Status: `CONTROLLED_DEPENDENCY`

## 3. Persistent chronological replay is not implemented end-to-end

The accepted historical corpus exists, but broad life-like replay of one persistent trader must wait until the prototype identity and memory/runtime semantics are stable.

Status: `OPEN_AFTER_PROTOTYPE`

## 4. Experience-derived policy promotion pipeline is not implemented

Still required later:

- hypothesis identity;
- falsification/counterexample search;
- discovery-exposure lineage;
- independent validation;
- policy promotion/versioning.

Status: `OPEN_FUTURE_WORK`

## 5. Protected lanes are locked

- validation/holdout: locked;
- shadow: locked;
- broker/account: locked;
- real money: locked.

Status: `LOCKED_BY_CURRENT_AUTHORITY`

## 6. Long-run stability/profitability is not demonstrated

No current evidence establishes long-horizon runtime stability, production reliability or profitability. Those require later protected evidence after the persistent trader identity is stable.

Status: `OPEN_FUTURE_EVIDENCE`
