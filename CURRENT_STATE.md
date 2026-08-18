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

## Binding research direction

RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
RESEARCH_DIRECTION_AUTHORITY=RESEARCH_DIRECTION.md

Primary research route:

```text
traceable human trading experience
-> AI-assisted extraction and structuring
-> versioned Playbook Contract
-> point-in-time market-scene representation / recognition
-> historical validation of applicability and failure conditions
-> strict validation / final-unseen governance
-> accepted or rejected playbook
```

The project is not primarily an unconstrained indicator/rule/parameter-mining engine.
Bounded parameterization and controlled search remain allowed when necessary to formalize or
test an already identified playbook, under the Selection Firewall and search-freedom rules.
Human sources create hypotheses, not accepted truth.

LIVE_AI_SCENE_RECOGNITION_MODE=UNDECIDED
LIVE_DISCRETIONARY_LLM_CRITICAL_PATH=NOT_AUTHORIZED
OWNER_GATE_REQUIRED_FOR_LIVE_AI_SEMANTICS=YES

The existing Skeleton v1.0 live-critical-path boundary remains unchanged. Any future live
market-reading implementation that would change that boundary requires a separate review and
Owner approval.

## Current objective

The Owner-approved canonical BALANCED research dataset is COMPLETE and ACCEPTED.
The next material stage is to design and freeze the research protocol and chronological split
**under `RESEARCH_DIRECTION.md`** before any genuine strategy research starts.

This next package must define how attributable human trading logic becomes versioned Playbook
artifacts, how qualitative concepts may be operationalized without unlimited search, how
family/lineage and exposure are tracked, and how development / validation / final-unseen data
are separated.

No specific playbook, source creator, split dates, validation cohort design, final-unseen
unlock, or live-AI semantics are frozen yet.

## Owner source/scope decision (final, recorded durably)

OWNER_APPROVAL=YES
OWNER_SOURCE_APPROVAL=TQSDK
TQSDK_STATUS=ADOPTED
TQSDK_ADOPTION_SCOPE=historical concrete-contract 1-minute research data only
TQSDK_VERIFIED_RUNTIME=3.10.1
OWNER_DATASET_SCOPE_APPROVAL=BALANCED
PAID_CONTINUITY_AUTHORIZED=NO
PAID_CONTINUITY_OWNER_GATE=REQUIRED_IF_NEEDED_LATER

Authority: `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`.

Adoption does NOT authorize broker connectivity, live/Shadow trading, order submission, or
future paid renewal. TqSdk runtime compatibility remains bound to verified `3.10.1` until
re-verified under a new compatible identity.

## Canonical BALANCED corpus (accepted)

CANONICAL_DATASET_BUILT=YES
CANONICAL_DATASET_ACCEPTED=YES
CANONICAL_DATASET_STATUS=ACCEPTED
SCALE_DECISION=APPROVED_FULL_BALANCED_CORPUS
CANONICAL_PRODUCTS=cu,al,ni,au,ag,rb
CANONICAL_COVERAGE=2024-01-01..2025-12-31
CANONICAL_GRANULARITY=1-minute
CONCRETE_CONTRACTS=212
PLAN_PARTITIONS=32980
ACQUIRED_PARTITIONS=32980
NORMALIZED_PARTITIONS=32980
NORMALIZED_ROWS=15280452
PARQUET_FILES=32980
HISTORICAL_METADATA_EFFECTIVE_PERIODS=PASS
NIGHT_CLOSED_DAY_AUTHORITY=PASS
GOVERNED_METADATA=PASS
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
CROSS_SOURCE_SUMMARY_IDENTITY=cee702ea6cd79e62ec49bf7f1f632f70e5b0a7a577ba455e09597cce9d16d4ae
CROSS_SOURCE_RESULT=32841_MATCH/0_MISMATCH/0_NOT_COMPARABLE/139_NOT_AVAILABLE

Current acceptance authority:
- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`
- `docs/evidence/CANONICAL_CORPUS_IDENTITY.json`
- `docs/evidence/CANONICAL_FULL_CROSS_SOURCE.json`

The canonical corpus build itself created no development/validation/final-unseen exposure for
any strategy lineage.

## Current boundaries

NOT_AUTHORIZED:
- concrete K-line strategy conclusions;
- large-scale strategy mining;
- unconstrained automated indicator/rule/parameter search as the default discovery route;
- automatic parameter optimization outside a future frozen protocol;
- final-unseen evaluation or unlock;
- Shadow automated trading;
- real-money trading;
- real broker order submission;
- discretionary LLM buy/sell decisions in the live critical path;
- new paid commitments;
- permanent RiskGate semantics without Owner approval;
- large multi-agent research orchestration;
- knowledge graph build-out;
- microservices/distributed architecture;
- importing strategy conclusions/results/parameters from `steel-radar-lite` or any other
  project.

## Current architecture

Top-level responsibility domains:
1. Data Substrate
2. Strategy Catalog
3. Backtest & Validation Engine
4. Research Loop
5. Trading Loop
6. Ledger
7. Observability & Control

See `ARCHITECTURE_BASELINE.md` for binding architecture details.
`RESEARCH_DIRECTION.md` specializes the Research Loop / Strategy Catalog discovery paradigm
without reopening Skeleton v1.0.

## Current tools and project capabilities

Current stage tool decision:

TOOL_DECISION=USE_EXISTING

No new tool is required to design the Human Playbook research protocol / chronological split.

Project-local adopted capabilities:
- TqSdk 3.10.1: ADOPTED for scoped historical concrete-contract 1-minute research data only.
- SHFE official annual raw: VERIFIED for official daily/statistical reference use only; not the
  canonical minute-data provider.
- PyArrow/Parquet 25.0.1: ADOPTED for normalized canonical bar storage.
- SQLite (`sqlite3`): ADOPTED as rebuildable canonical catalog/index; not the sole historical
  truth authority.
- Raw JSON + SHA256 provenance: retained as authoritative raw evidence mechanism.
- DuckDB: DEFERRED / optional; not installed.

All external components must progress through project-level:
CANDIDATE -> VERIFIED -> ADOPTED.

## Current local capability facts

These are environment facts, not project dependencies or research authority.

- VS Code is available on the Owner's Windows workstation and is used for repository work.
- A DeepSeek Flash-family model API is connected in the Owner's VS Code environment and may
  support ordinary engineering or justified independent review.
- DeepSeek/model availability does not authorize it to decide frozen research semantics.
- Do not use an external reviewer for routine small changes merely to obtain a second opinion;
  prefer deterministic tests/repository evidence first.
- Ponytail was found globally installed in Codex and was disabled/removed from active global
  discovery on 2026-08-15, with a reversible backup retained outside active discovery.

## Known limitations / technical debt

Authority/index: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.

Current non-blocking items that must survive handoff:
- TD-001: bootstrap `NormalizedSessionCalendar` overlaps session/trading-day responsibility
  with authoritative `SessionMetadata`; consolidate/isolate before it can become a second
  business-logic owner.
- TD-002: partial-close validation snapshot temporarily clears unrealized PnL until a later
  valid mark recomputes it; resolve before PnL-sensitive confirmatory evidence is treated as
  final quality.
- LIMIT-001: full governed historical price-limit metadata is deferred; bind it before claiming
  historical price-limit non-fill realism in confirmatory validation.
- DECISION-001: exact live AI market-reading / scene-recognition implementation remains an
  unresolved Owner-gated future decision; current discretionary LLM live critical path remains
  not authorized.

None of these invalidate the accepted canonical corpus.

## Current next action

CURRENT_NEXT_ACTION=RESEARCH_PROTOCOL_AND_CHRONOLOGICAL_SPLIT_FREEZE_REVIEW
CURRENT_NEXT_ACTION_MUST_CONFORM_TO=RESEARCH_DIRECTION.md

The review has NOT yet been executed or accepted.

It must not silently inherit an earlier generic-quant research assumption. In particular,
any prior draft such as a 12/6/6 split or generic candidate-mining workflow remains only a
proposal unless the new Human Playbook First protocol explicitly evaluates and freezes it.

The upcoming review should produce a single Owner decision package for genuinely frozen
research semantics rather than asking the Owner to decide routine implementation details.

## Current acceptance / durable evidence

- Architecture: `ARCHITECTURE_BASELINE.md` — Skeleton v1.0 ACCEPTED.
- Bootstrap: `docs/evidence/BOOTSTRAP_ACCEPTANCE.md`.
- Human Playbook First direction: `RESEARCH_DIRECTION.md` — OWNER_APPROVED.
- Canonical source/scope decision: `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`.
- Canonical corpus acceptance: `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`.
- Canonical corpus identity: `docs/evidence/CANONICAL_CORPUS_IDENTITY.json`.
- Full cross-source evidence: `docs/evidence/CANONICAL_FULL_CROSS_SOURCE.json`.
- Historical pre-acceptance canonical package: `docs/evidence/CANONICAL_DATASET_PACKAGE.md`
  (preserved for audit; superseded for current corpus status by final acceptance evidence).
- Known limitations/debt index: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.

## Current Owner action

OWNER_ACTION=NONE

The next Owner gate occurs after the project brain has designed a decision-ready Human
Playbook research protocol / chronological-split freeze package. No repeated approval is
needed for the already accepted canonical data/source decisions.

## Owner decision gates

Owner-level approval is required only for genuinely new product/research direction, frozen
experiment semantics, permanent risk rules, paid commitments, real-money/broker actions, or
irreversible external actions.
