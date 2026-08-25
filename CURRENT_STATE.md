# CURRENT_STATE

As of: `2026-08-26`

## Mission

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

Target:

`A PERSISTENT, AUDITABLE, JIANGHE-TRAINED, EVIDENCE-IMPROVING DEEPSEEK FUTURES TRADER`

The project is building one persistent DeepSeek-based China-futures trader. Jianghe is its initial source-grounded trading foundation. The trader may accumulate working memory, journal records and falsifiable hypotheses, but source truth and active policy remain governed project assets.

## Knowledge and learning boundary

The runtime keeps these layers separate:

- `JIANGHE_CANON`: source-grounded, read-only to the trader;
- `PROJECT_VALIDATED_POLICY`: independently validated project extensions;
- `DS_HYPOTHESIS_MEMORY`: DeepSeek-generated candidate ideas;
- `DS_WORKING_MEMORY`: current market state and active hypotheses;
- `DS_JOURNAL`: reflection and self-critique.

Experience-derived policy follows:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

PnL and process correctness remain separate evidence dimensions.

## Current architecture

`Market Data -> Rolling Market State -> Attention/Wake Policy -> Causal Multi-Timeframe Observation -> Context Assembler -> DeepSeek Trader -> Decision Normalizer + Mechanical Guards -> constrained TradeIntent -> deterministic RiskGate -> OMS/Execution -> Reconciliation/Safety/Ledger`

AI owns market interpretation and proposed discretionary intent.

Deterministic project systems own hard risk, broker/account truth, order lifecycle, reconciliation and safety.

Current active observation stack:

`4H / 1H / 15m / 5m`

4H role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

Mandatory guards:

- `STRICT_OUTPUT_ENUM_ENFORCEMENT = IMPLEMENTED_AND_REGRESSION_TESTED`
- `NO_4H_EXACT_VOLUME_RECONCILIATION = IMPLEMENTED_AND_REGRESSION_TESTED`

The guard implementation and broad repository regression passed the cleanup integration CI before authority synchronization.

## Historical data foundation

Accepted canonical historical corpus:

- source scope: TqSdk historical concrete-contract 1-minute data
- coverage: `2024-01-01..2025-12-31`
- products: `cu, al, ni, au, ag, rb`
- partitions: `32,980`
- contracts: `212`
- normalized rows: `15,280,452`
- corpus identity: `1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`

Authority:

`docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`

The corpus is reserved for causal chronological replay of a persistent trader.

## Repository hygiene

The active tree is intentionally reduced to current product authority, current Jianghe source evidence, accepted canonical-data evidence, DeepSeek trader/runtime components, and deterministic execution/safety infrastructure.

Superseded provider-selection, stateless evaluation, pilot/final-chance and obsolete generic research runtime surfaces are historical Git material rather than active takeover dependencies.

Fresh takeover is governed by the four-file active core listed in `00_READ_FIRST.md`.

## Current work package

`CURRENT_WORK_PACKAGE = JIANGHE_PERSISTENT_DEEPSEEK_TRADER_FOUNDATION_V0_1`

`DEEPSEEK_HARNESS = CANDIDATE_FOR_PROJECT_ADMISSION`

`TOOL_DECISION = ADD_TOOL__VERIFY_DEEPSEEK_HARNESS`

Exact next sequence:

1. verify a pinned DeepSeek Harness version/commit against exact model + vision + persistence + project-owned memory/tool/audit requirements;
2. if the pinned build passes, mark it VERIFIED and decide whether to ADOPT it only as the runtime shell; if it fails, use the thinnest project-owned equivalent without changing product direction;
3. build the smallest persistent trader proving exact DeepSeek model path, chart/vision input, persistent working memory, Jianghe retrieval, K-line tools, structured journal/hypothesis memory and complete audit;
4. run a small chronological lifecycle replay to debug memory/runtime semantics;
5. only after that trader identity is stable, design broader historical replay and governed experience-learning research.

## Current execution and research locks

- paid provider calls: `PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- protected future/outcome research access: locked unless a current protocol authorizes it
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked

No current implementation step requires a paid provider call.

## Historical paid-research accounting

`PROJECT_ACCOUNTED_CNY = 20.9075330`

Historical hard cap record: `100.00 CNY`.

This is accounting history, not current spend authorization.
