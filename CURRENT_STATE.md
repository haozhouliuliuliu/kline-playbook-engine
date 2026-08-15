# CURRENT_STATE

## Project phase
PROJECT_PHASE=PROJECT_BOOTSTRAP
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
ADOPTED_CONTRACT_SHA256=3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e

## Current objective
Establish the clean repository/governance structure and verify the cheapest technical prerequisites needed to implement Skeleton v1.0.

## Current boundaries
NOT_AUTHORIZED:
- concrete K-line strategy conclusions;
- large-scale strategy mining;
- automatic parameter optimization;
- final-unseen evaluation;
- Shadow automated trading;
- real-money trading;
- real broker order submission;
- large multi-agent research orchestration;
- knowledge graph build-out;
- microservices/distributed architecture.

## Current architecture
Top-level responsibility domains:
1. Data Substrate
2. Strategy Catalog
3. Backtest & Validation Engine
4. Research Loop
5. Trading Loop
6. Ledger
7. Observability & Control

See ARCHITECTURE_BASELINE.md for binding architecture details.

## Tool/open-source status
No candidate is automatically adopted.

Known categories:
- execution backbone candidate: VeighNa / vn.py
- fast screening candidate: vectorbt
- data/simulation candidates: TqSdk, openctp, SimNow
- storage baseline candidates: SQLite, Parquet; DuckDB optional
- later/reference only: NautilusTrader, STUMPY, RD-Agent, Qlib, TradingAgents, MiroFish, Freqtrade, Jesse, LEAN

All external components must progress through:
CANDIDATE → VERIFIED → ADOPTED

## Current next action
CURRENT_NEXT_ACTION=BOOTSTRAP_REPOSITORY_AND_RUN_MINIMUM_TECHNICAL_FEASIBILITY_CHECKS

The first implementation-stage work should:
1. create the repository and formal authority files;
2. preserve Skeleton v1.0 without expanding it;
3. define minimal tests for data/session semantics and state/ledger boundaries;
4. perform a stage-level tool/open-source applicability review;
5. verify only the cheapest fatal prerequisites before broad implementation;
6. keep all broker/live-money actions disabled unless explicitly authorized later.

## Owner decision gates
Owner-level approval is required only for genuinely new product/research direction, frozen experiment semantics, permanent risk rules, paid commitments, real-money/broker actions, or irreversible external actions.
