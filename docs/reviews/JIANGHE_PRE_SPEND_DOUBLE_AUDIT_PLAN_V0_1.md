# 江河真实模型探针前双重复核计划 V0.1

> Status: `OWNER_REQUESTED__READ_ONLY_AUDITS_REQUIRED_BEFORE_ANY_SPEND`
> Date: 2026-08-23
> Scope: two independent, read-only reviews of the same frozen main lineage before any live model/provider request.

## Why

The Owner explicitly requested two additional reviews because repeated historical repair cycles may have introduced redundant layers, stale compatibility paths, unnecessary artifacts, or regressions in areas that were previously sound. The purpose is not to invent new gates; it is to verify that the integrated system is coherent, minimal enough, and cost-safe before any paid API usage.

No real API call or paid spend is authorized by this plan.

## Fixed audit baseline

Both rounds must start from the exact same `main` commit chosen at dispatch time. If main moves between dispatches, the second round must either rebase its read-only baseline to the same commit or both audits must be restarted on the new frozen baseline.

Workers must not modify repo files while auditing.

## Round 1 — Whole-system architecture / redundancy audit

Primary questions:

1. Does the current Jianghe AI Trader architecture still have one clear authority per concern?
2. Did historical repair cycles leave duplicated provenance, identity, normalization, visual, provider, evaluator, PRIMARY, or replay layers?
3. Are there stale V0.1/V0.3/V0.4 compatibility branches still influencing current behavior unnecessarily?
4. Did any repair weaken or bypass a previously correct invariant?
5. Are current runtime/state/ADR/protocol authorities mutually consistent?
6. Is the path from observation -> model request -> response -> normalizer -> evaluator -> TradeIntent still minimal and auditable?
7. Is there any code/artifact that should be deleted, demoted to historical evidence, or made non-current before paid testing?
8. Are there hidden coupling or identity cycles that could make the live probe evidence misleading?
9. Are tests proving actual invariants or merely mirroring implementation details?
10. Does the current architecture create avoidable token/data egress or cost amplification?

Output must classify findings as:

```text
BLOCKER_BEFORE_SPEND
REPAIR_RECOMMENDED_BEFORE_SPEND
NONBLOCKING_CLEANUP
NO_FINDING
```

Every blocking/recommended finding requires concrete repository evidence and a minimum fix.

## Round 2 — Fine-grained regression / dead-code / hygiene / cost-path audit

Primary checks:

- dead/unreachable code and unused adapters/classes;
- stale version constants and old identity references;
- duplicate schema/enum/validation logic;
- unused compatibility shims;
- tests referencing superseded artifacts;
- code paths where malformed provider output could bypass fail-closed behavior;
- evidence fields written but never validated, or validated but never consumed;
- incorrect default values, bool/int coercion, optional-field leakage;
- timestamp/timezone edge cases;
- deterministic hash instability / platform dependence;
- file/path assumptions and Windows/Linux differences;
- credential/logging leakage surfaces;
- retry logic that could accidentally retry semantic failures and waste money;
- token/output limits that permit unnecessary spend;
- repeated full-context sends where caching/minimal context should be used;
- visual payload duplication or unnecessary high-resolution egress;
- provider-specific features accidentally enabled (web/search/tools/grounding);
- stale docs/state contradicting runtime behavior;
- unnecessary test/support artifacts created by prior repair cycles;
- full-suite regressions and targeted adversarial cases.

Round 2 may not fail merely for style or prose similarity. Any spend blocker must identify a concrete correctness, evidence-integrity, security, or cost-control failure.

## Consolidation rule

After both read-only audits:

1. project brain compares findings and removes false positives / duplicates;
2. no code is changed until the combined finding set is frozen;
3. if repair is necessary, produce one batched repair package;
4. after that repair, run focused regression + canonical full suite + only the specific audit checks affected by the repair;
5. do not restart open-ended review cycles unless a new concrete invariant is broken.

## Spend gate

```text
ROUND_1_STATUS=PENDING
ROUND_2_STATUS=PENDING
CONSOLIDATED_FINDINGS=NOT_AVAILABLE
LIVE_CALLS=0
PAID_SPEND=0
TOTAL_HARD_SPEND_CAP_CNY=100.00
FINAL_PROVIDER_SET=NOT_DECIDED
```
