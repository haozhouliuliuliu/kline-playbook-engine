# CURRENT_STATE

## Project phase
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
ADOPTED_CONTRACT_SHA256=3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e
LAST_KNOWN_GOOD=b6d1961dca5b4c879bc7deb6406f3c63723b04d4
BOOTSTRAP_ACCEPTANCE=GO
BOOTSTRAP_ACCEPTANCE_EVIDENCE=docs/evidence/BOOTSTRAP_ACCEPTANCE.md
CURRENT_BLOCKER=NONE

## Current objective
Establish the first real, provenance-bound, point-in-time historical China-futures data path and canonical research dataset before substantive strategy research.

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
CURRENT_NEXT_ACTION=REAL_HISTORICAL_DATA_SUBSTRATE_FEASIBILITY_PACKAGE

## Current acceptance

PROJECT_BOOTSTRAP is formally accepted at
`b6d1961dca5b4c879bc7deb6406f3c63723b04d4`. The acceptance record is
`docs/evidence/BOOTSTRAP_ACCEPTANCE.md`.

## Current tool decision

TOOL_DECISION=USE_EXISTING

No data provider, external trading framework, broker connector, strategy, or
live-money capability is verified or adopted. The next bounded package must
perform the new-stage source/tool applicability review before any adoption.

## Owner decision gates
Owner-level approval is required only for genuinely new product/research direction, frozen experiment semantics, permanent risk rules, paid commitments, real-money/broker actions, or irreversible external actions.
