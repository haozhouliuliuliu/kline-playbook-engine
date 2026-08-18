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
- Pre-outcome firewall acceptance review: `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_0.md`
- Current state/next action: `CURRENT_STATE.md`
- Final v0.3 candidate (historical input to frozen protocol): `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_INPUT_PACKAGE_V0_3.md`
- Final Owner decision package: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_DECISION_PACKAGE_V0_2.md`
- Targeted delta review: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_DELTA_ADVERSARIAL_REVIEW_V0_1.md`
- Delta adjudication: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_DELTA_ADJUDICATION_V0_1.md`
- Prior independent review: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADVERSARIAL_REVIEW_V0_1.md`
- Prior adjudication: `docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_ADJUDICATION_V0_1.md`
- Source Dossier schema: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
- Source Material Inventory: `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`
- First-wave source close-out: `docs/research/HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT.md`
- China-first discovery wave: `docs/research/CHINA_FIRST_SOURCE_DISCOVERY_WAVE_1.md`
- Known non-blocking limitations/debt: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`
- Adopted governance: `CROSS_PROJECT_OPERATING_CONTRACT.md` Version 3.1, pinned by SHA256 in `CURRENT_STATE.md`

Project state (accepted/current):
- PROJECT_PHASE=RESEARCH_FOUNDATION
- Skeleton v1.0 ACCEPTED
- RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST (Owner-approved)
- Canonical BALANCED corpus ACCEPTED (2024-01-01..2025-12-31)
- First Human Playbook source-layer wave COMPLETE / GO at source-only level
- Independent protocol review + final delta review COMPLETE
- Owner approved: `按 v0.3 推荐冻结`
- **Research Protocol v1.0 = FROZEN / BINDING**
- **Chronology = FROZEN 12/6/6**
- `INSUFFICIENT_EVIDENCE` = frozen legitimate result
- Historical final cohort = project-governed historical holdout, not a claim of universal epistemic unseen-ness
- RESEARCH_WAVE whole-wave multiplicity governance = frozen
- Common statistical profile must lock before first candidate outcome-bearing performance backtest
- Pre-outcome research firewall = IMPLEMENTED_AND_VERIFIED / IDENTITY_BOUND (single owner: `src/research_firewall.py`)
- Current work package = `HUMAN_PLAYBOOK_PREOUTCOME_RESEARCH_FIREWALL_IMPLEMENTATION` (COMPLETE)
- Next package = `COMMON_STATISTICAL_PROFILE_V1_DESIGN_AND_INDEPENDENT_REVIEW`
- Current tool decision = USE_EXISTING

Frozen chronology:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

Important implementation reality:
- `src/research_firewall.py` is the single owner: identity-bound `OutcomeTestRegistration`, project-issued SOURCE_ONLY verification, a bounded SOURCE_ONLY claim-extraction runner, immutable RESEARCH_WAVE manifests (single canonical denominator), common-statistical-profile identity/lock, the fail-closed pre-outcome gate, and the historical-final state machine;
- candidate outcome access is keyed by one registered hypothesis identity; callers cannot assert frozen lock booleans;
- the legacy `FinalUnseenFirewall` in `src/strategy_evidence.py` delegates to it (compatibility preserved);
- only TEST_ONLY statistical profiles exist, so candidate outcome-bearing performance backtests remain NOT AUTHORIZED until the real `COMMON_STATISTICAL_PROFILE_V1` is designed, reviewed, and locked.

Immediate allowed work:
- implement/test the frozen pre-outcome firewall requirements;
- source discovery/provenance;
- non-outcome operationalization/tests;
- after SOURCE_ONLY controls are verified, controlled real claim extraction under Claim Schema v1.0.

Still NOT AUTHORIZED:
- candidate PnL/equity/expectancy/Sharpe/win-loss or equivalent performance inspection before the pre-outcome gate passes;
- validation access before prerequisites;
- historical final-holdout unlock;
- Shadow/live trading;
- real-money/broker actions;
- discretionary LLM live critical path;
- paid commitments;
- permanent RiskGate changes.

Status authority: `CURRENT_STATE.md`; frozen research-protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`.

Canonical verification path:
`python -m unittest discover -s tests -v`
