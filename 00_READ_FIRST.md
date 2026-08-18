# 00_READ_FIRST

This repository is in `RESEARCH_FOUNDATION`.

Current authority/navigation:
- Owner collaboration: `OWNER_COLLABORATION_CONTRACT.md`
- Binding architecture: `ARCHITECTURE_BASELINE.md` — Skeleton v1.0
- Binding research direction: `RESEARCH_DIRECTION.md` — Human Playbook First
- **Binding Human Playbook research protocol:** `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- **Binding 12/6/6 chronology:** `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- **Binding Selection Firewall requirements:** `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- **Active Claim Extraction schema:** `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
- Owner freeze evidence: `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- Pre-outcome firewall implementation evidence: `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`
- Common Statistical Profile v1 candidate (NOT_LOCKED): `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
- Statistical engine capability audit (COMPLETE): `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`
- Firewall acceptance history:
  - `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_0.md`
  - `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_1.md`
  - **final acceptance:** `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md`
- Current state/next action: `CURRENT_STATE.md`
- Source Dossier schema: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
- Source Material Inventory: `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`
- First-wave source close-out: `docs/research/HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT.md`
- Known limitations/debt: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`
- Adopted governance: `CROSS_PROJECT_OPERATING_CONTRACT.md` Version 3.1, pinned by SHA256 in `CURRENT_STATE.md`

Project state:
- Skeleton v1.0 ACCEPTED
- RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST (Owner-approved)
- Canonical BALANCED corpus ACCEPTED (2024-01-01..2025-12-31)
- First Human Playbook source-layer wave COMPLETE / GO at source-only level
- **Research Protocol v1.0 = FROZEN / BINDING**
- **Chronology = FROZEN 12/6/6**
- `INSUFFICIENT_EVIDENCE` = frozen legitimate result
- Historical final cohort = project-governed historical holdout, not universal epistemic unseen proof
- RESEARCH_WAVE whole-wave multiplicity governance = frozen
- **Pre-outcome firewall = ACCEPTED / COMPLETE_VERIFIED** at commit `046d3e7b386c50d936285741226c3b0b26d1a6e9`
- Real claim extraction environment = VERIFIED / NOT_STARTED
- Candidate outcome-bearing performance backtest = NOT_AUTHORIZED
- **Common Statistical Profile v1 = CANDIDATE / NOT_LOCKED** (design commit `6ef668f`; engine capability audit `c34cebde` integrated)
- **Current work package = COMMON_STATISTICAL_PROFILE_V1_DESIGN_AND_INDEPENDENT_REVIEW**
- Current tool decision = USE_EXISTING

Frozen chronology:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

Current firewall reality:
- `WaveHypothesisBinding` is the immutable per-hypothesis PRIMARY/scope/parameter-search identity authority;
- wave lock and authoritative access both cross-check the exact binding;
- SOURCE_ONLY policy + bounded claim-extraction runner are verified;
- TEST_ONLY profiles can authorize only synthetic DEVELOPMENT fixtures;
- real candidate PnL/equity/expectancy/Sharpe/win-loss inspection remains denied until a real independently reviewed `COMMON_STATISTICAL_PROFILE_V1` is locked and bound into a real research wave;
- validation, historical final holdout, Shadow/live and real-money/broker actions remain locked/not authorized.

Next action:
`INDEPENDENT_ADVERSARIAL_REVIEW_OF_COMMON_STATISTICAL_PROFILE_V1`

Status authority: `CURRENT_STATE.md`.
Frozen protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`.

Canonical verification path:
`python -m unittest discover -s tests -v`
