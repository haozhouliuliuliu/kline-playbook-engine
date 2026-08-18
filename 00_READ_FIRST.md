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
- First firewall acceptance review: `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_0.md`
- **Current firewall acceptance delta:** `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_1.md`
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
- Common statistical profile must lock before first candidate outcome-bearing performance backtest
- c6eb082 hardening resolved major firewall identity-binding gaps, but final acceptance review v1.1 found one remaining E-5 cross-artifact binding gap
- **Current work package = HUMAN_PLAYBOOK_PREOUTCOME_RESEARCH_FIREWALL_IDENTITY_CROSS_BINDING_HARDENING**
- **Current status = FIX_REQUIRED**
- Current tool decision = USE_EXISTING

Frozen chronology:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

Current E-5 engineering gap:
- `OutcomeTestRegistration` has hypothesis-specific `primary_branch_identity`, `scope_identity`, and `parameter_search_identity`;
- `ResearchWaveManifest` separately declares PRIMARY/scope/search information;
- `ResearchWaveRegistry.lock()` currently verifies hypothesis/wave/profile/counting-unit binding but does not yet prove those PRIMARY/scope/search identities match the immutable wave declaration for each tested hypothesis;
- this must be fail-closed before the firewall package is finally accepted.

Until E-5 is fixed:
- real claim extraction remains on HOLD;
- candidate PnL/equity/expectancy/Sharpe/win-loss inspection remains NOT AUTHORIZED;
- validation remains locked;
- historical final-holdout remains locked;
- Shadow/live and real-money/broker actions remain NOT AUTHORIZED.

Next action:
`HARDEN_PRIMARY_SCOPE_SEARCH_CROSS_BINDING_THEN_REACCEPT`

Status authority: `CURRENT_STATE.md`.
Frozen protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`.

Canonical verification path:
`python -m unittest discover -s tests -v`
