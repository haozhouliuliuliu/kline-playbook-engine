# 00_READ_FIRST

This repository is in `RESEARCH_FOUNDATION`.

Current authority/navigation:
- Owner collaboration: `OWNER_COLLABORATION_CONTRACT.md`
- Binding architecture: `ARCHITECTURE_BASELINE.md` — Skeleton v1.0
- Current state/next action: `CURRENT_STATE.md`
- Adopted governance: `CROSS_PROJECT_OPERATING_CONTRACT.md` Version 3.1, pinned by SHA256 in `CURRENT_STATE.md`
- Tool catalog only: `TOOL_REGISTRY.md`

Project state (accepted):
- PROJECT_PHASE=RESEARCH_FOUNDATION
- Skeleton v1.0 ACCEPTED
- TqSdk ADOPTED — historical concrete-contract 1-minute research data only
  (verified runtime compatibility = 3.10.1)
- PyArrow/Parquet ADOPTED — canonical normalized bar storage
- SQLite ADOPTED — rebuildable canonical catalog/index
- Canonical BALANCED corpus ACCEPTED (2024-01-01..2025-12-31)
- Next action = RESEARCH_PROTOCOL_AND_CHRONOLOGICAL_SPLIT_FREEZE_REVIEW

Status authority: `CURRENT_STATE.md`; corpus acceptance:
`docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`; corpus identity:
`docs/evidence/CANONICAL_CORPUS_IDENTITY.json`.

Canonical verification path:
`python -m unittest discover -s tests -v`
