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

## Current local capability facts
These are environment facts, not project dependencies or adoption decisions.

- VS Code is available on the Owner's Windows workstation and is used for repository work.
- A DeepSeek Flash-family model API is connected in the Owner's VS Code environment and may be considered as an independent reviewer when an actual review need justifies it.
- Do not use the DeepSeek reviewer for routine small code changes merely to obtain a second opinion; prefer deterministic tests and repository evidence first.
- Ponytail was found globally installed in Codex and was disabled/removed from active global discovery on 2026-08-15, with a reversible backup retained outside active discovery. A fresh Codex process/restart is required before relying on absence from runtime context.

## Current next action
CURRENT_NEXT_ACTION=MINIMUM_POSITION_MARK_TO_MARKET_AND_FORCED_LIQUIDATION_FEASIBILITY_PACKAGE

The first implementation-stage work should:
1. create the repository and formal authority files;
2. preserve Skeleton v1.0 without expanding it;
3. define minimal tests for data/session semantics and state/ledger boundaries;
4. perform a stage-level tool/open-source applicability review;
5. verify only the cheapest fatal prerequisites before broad implementation;
6. keep all broker/live-money actions disabled unless explicitly authorized later.

## Completed bootstrap evidence
- Restored bootstrap history has been verified from the exported bundle at
  `2f840bb84939eee5c6b0948a817641e79cf7af1d`.
- The minimum Data Substrate contract is implemented in
  `src/data_substrate.py` and covered by deterministic unit tests.
- The clean-room reuse audit is recorded in `docs/reuse/STEEL_REUSE_AUDIT.md`.
- Strategy Identity + Evidence Spine feasibility is implemented in
  `src/strategy_evidence.py` with deterministic firewall tests and evidence in
  `docs/evidence/STRATEGY_EVIDENCE_SPINE_VERIFICATION.md`.
- Backtest & Validation chronological connection semantics are implemented in
  `src/validation_runner.py` with evidence in
  `docs/evidence/VALIDATION_EXECUTION_SEMANTICS_VERIFICATION.md`.
- Confirmatory synthetic fill/non-fill and versioned execution-assumption
  semantics are implemented through the existing runner and ledger, with
  evidence in `docs/evidence/CONFIRMATORY_EXECUTION_REALISM_VERIFICATION.md`.
- Synthetic order-size, capital/margin affordability, and sequential capital
  snapshot semantics are implemented through the existing runner and ledger,
  with evidence in `docs/evidence/CAPITAL_MARGIN_CONSTRAINTS_VERIFICATION.md`.
- No external trading framework, broker connector, strategy, or live-money
  capability has been verified or adopted.

## Owner decision gates
Owner-level approval is required only for genuinely new product/research direction, frozen experiment semantics, permanent risk rules, paid commitments, real-money/broker actions, or irreversible external actions.
