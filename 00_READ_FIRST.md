# 00_READ_FIRST

This repository is in `RESEARCH_FOUNDATION`.

Current authority/navigation:
- Owner collaboration: `OWNER_COLLABORATION_CONTRACT.md`
- Binding architecture: `ARCHITECTURE_BASELINE.md` — Skeleton v1.0
- Binding research direction: `RESEARCH_DIRECTION.md` — Human Playbook First
- Current state/next action: `CURRENT_STATE.md`
- Research-protocol input package: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_1.md`
- Source Dossier schema: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
- Source Material Inventory: `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`
- First-wave source close-out: `docs/research/HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT.md`
- Non-frozen Claim Extraction schema: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V0_1.md`
- China-first discovery wave: `docs/research/CHINA_FIRST_SOURCE_DISCOVERY_WAVE_1.md`
- Completed acquisition-tool pilot: `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION.md`
- Tool-admission Windows evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION_WINDOWS_2026-08-18.md`
- Known non-blocking limitations/debt: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`
- Adopted governance: `CROSS_PROJECT_OPERATING_CONTRACT.md` Version 3.1, pinned by SHA256 in `CURRENT_STATE.md`
- Tool catalog only: `TOOL_REGISTRY.md`

Project state (accepted/current):
- PROJECT_PHASE=RESEARCH_FOUNDATION
- Skeleton v1.0 ACCEPTED
- RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST (Owner-approved)
- Canonical BALANCED corpus ACCEPTED (2024-01-01..2025-12-31)
- Source-acquisition tool-admission pilot COMPLETE
- First Human Playbook source-layer wave COMPLETE / GO at source-only level
- Source Dossier v0.2 is ACTIVE_DRAFT / NON_FROZEN
- Claim Extraction schema v0.1 is ACTIVE_DRAFT / NON_FROZEN and has NOT been applied to real trading logic
- Research-protocol input package v0.1 is READY_FOR_INDEPENDENT_ADVERSARIAL_REVIEW / NOT_FROZEN
- Research-protocol / chronological-split freeze remains required before genuine strategy research and is NOT EXECUTED
- Current work package = INDEPENDENT_ADVERSARIAL_REVIEW_OF_HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE
- Current reviewer role = advisory only; reviewer may attack assumptions and propose alternatives but may NOT freeze research semantics
- Concrete claim extraction, strategy research, machine thresholding, backtest, final-unseen access and live trading remain NOT AUTHORIZED
- Tool decision for current package = USE_EXISTING

Protocol-input package explicitly asks review of:
- whether 24 months can support the candidate chronological split;
- whether 12/6/6 is too weak/arbitrary;
- source-material/example leakage into validation/final-unseen;
- hidden search freedom from AI interpretation variants;
- lineage/exposure inheritance loopholes;
- observability substitutions that change source meaning;
- family-specific acceptance-gate gaming;
- validation/final revision policy;
- whether the design is too strict for qualitative human knowledge or too permissive against disguised data mining.

Status authority: `CURRENT_STATE.md`; research-direction authority: `RESEARCH_DIRECTION.md`.

Canonical verification path:
`python -m unittest discover -s tests -v`
