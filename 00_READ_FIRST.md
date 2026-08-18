# 00_READ_FIRST

This repository is in `RESEARCH_FOUNDATION`.

Current authority/navigation:
- Owner collaboration: `OWNER_COLLABORATION_CONTRACT.md`
- Binding architecture: `ARCHITECTURE_BASELINE.md` — Skeleton v1.0
- Binding research direction: `RESEARCH_DIRECTION.md` — Human Playbook First
- Current state/next action: `CURRENT_STATE.md`
- Current Source Dossier draft: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
- Current Source Material Inventory: `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`
- Completed acquisition-tool pilot: `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION.md`
- Tool-admission Windows evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION_WINDOWS_2026-08-18.md`
- Known non-blocking limitations/debt: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`
- Adopted governance: `CROSS_PROJECT_OPERATING_CONTRACT.md` Version 3.1, pinned by SHA256 in `CURRENT_STATE.md`
- Tool catalog only: `TOOL_REGISTRY.md`

Project state (accepted):
- PROJECT_PHASE=RESEARCH_FOUNDATION
- Skeleton v1.0 ACCEPTED
- RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST (Owner-approved)
- Primary research route = traceable human trading experience -> AI-assisted structured Playbook -> point-in-time scene representation/recognition -> strict historical validation
- Unconstrained indicator/rule/parameter mining for the best historical curve is NOT the default strategy-discovery route
- Live discretionary LLM decisions remain NOT AUTHORIZED; exact future live scene-recognition semantics remain an Owner-gated decision
- TqSdk ADOPTED — historical concrete-contract 1-minute research data only (verified runtime compatibility = 3.10.1)
- PyArrow/Parquet ADOPTED — canonical normalized bar storage
- SQLite ADOPTED — rebuildable canonical catalog/index
- Canonical BALANCED corpus ACCEPTED (2024-01-01..2025-12-31)
- Human Playbook source-acquisition tool-admission pilot COMPLETE; Docling and video-transcribe-skill are VERIFIED for their recorded bounded scopes, not ADOPTED
- Research-protocol / chronological-split freeze review remains required before genuine strategy research and stays unexecuted
- Current work package = HUMAN_PLAYBOOK_SOURCE_DOSSIER_AND_INVENTORY_PILOT
- Current source-level route = project-led discovery -> provenance/identity check -> Source Dossier v0.2 -> Source Material Inventory -> source-level observability/admission classification
- Concrete trading-claim extraction, strategy research, backtest, and machine thresholding are NOT authorized in the current package

Status authority: `CURRENT_STATE.md`; research-direction authority: `RESEARCH_DIRECTION.md`;
source-dossier draft: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`;
source inventory: `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`;
corpus acceptance: `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`;
corpus identity: `docs/evidence/CANONICAL_CORPUS_IDENTITY.json`.

Canonical verification path:
`python -m unittest discover -s tests -v`
