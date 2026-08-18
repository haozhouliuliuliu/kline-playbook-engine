# 00_READ_FIRST

This repository is in `RESEARCH_FOUNDATION`.

Read current authority/navigation in this order:
1. `OWNER_COLLABORATION_CONTRACT.md`
2. `ARCHITECTURE_BASELINE.md` — Skeleton v1.0 ACCEPTED
3. `CURRENT_STATE.md` — current status / authorization / next action
4. `RESEARCH_DIRECTION.md` — Human Playbook First, Owner-approved
5. `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` — FROZEN / BINDING
6. `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` — FROZEN 12/6/6
7. `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
8. `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
9. `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`

Important current evidence:
- Owner protocol freeze: `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- Pre-outcome firewall implementation: `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`
- Final firewall acceptance: `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md`
- Common Statistical Profile v1 first candidate (historical candidate; NOT_LOCKED): `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
- Statistical engine capability audit (integrated): `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`
- Parallel engine compatibility crosswalk: branch `parallel/stat-engine-audit`, commit `05ad7f9a94c1a6b885402a4417a0d095dbfa7c56`
- Parallel independent adversarial statistical review: branch `parallel/stat-profile-review`, commit `5e78605d312ee2e6c22e82dc4d91d651eacac4b2`
- Project-brain adjudication of both parallel lines: `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`
- Known limitations/debt: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`
- Adopted governance: `CROSS_PROJECT_OPERATING_CONTRACT.md` Version 3.1, pinned by SHA256 in `CURRENT_STATE.md`

Current state summary:
- Canonical BALANCED corpus ACCEPTED: cu/al/ni/au/ag/rb, 2024-01-01..2025-12-31, 1-minute, 212 contracts, 15,280,452 rows.
- Human Playbook First = binding research direction.
- Research Protocol v1.0 = FROZEN / BINDING.
- Chronology = FROZEN 12/6/6.
- `INSUFFICIENT_EVIDENCE` = frozen legitimate result.
- Pre-outcome firewall = ACCEPTED / COMPLETE_VERIFIED.
- SOURCE_ONLY real claim-extraction environment = VERIFIED / NOT_STARTED.
- Candidate outcome-bearing performance backtest = NOT_AUTHORIZED.
- Common Statistical Profile v1 first candidate = `CANDIDATE_REVISION_REQUIRED_NOT_LOCKED` after independent review/adjudication.
- Current work package = `COMMON_STATISTICAL_PROFILE_V1_REVISION_AFTER_PARALLEL_REVIEW`.
- Current tool decision = `USE_EXISTING`.
- Owner action = NONE.

Frozen chronology:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

Current statistical-profile revision facts:
- keep the common-profile direction;
- current draft must not be locked;
- remove `ESS=N/max(1,2H-1)` as a deterministic hard gate;
- pin one `position_id` as one round-trip observation and aggregate add/partial-close legs;
- define holding/multi-week dependence semantics explicitly;
- separate economic materiality from detectability/power interpretation;
- distinguish fee stress from slippage/friction stress;
- make data-governance blocking explicit (`DATA_BLOCKED` or equivalent);
- make multiplicity counting machine-consistent with Research Wave/search identities;
- no candidate outcomes may be used to tune the revised profile.

Parallel-work rule:
- isolated worktrees/branches for independent workers;
- one integration lane owns `main` and shared authority/state;
- parallel workers do not push `main` or edit shared authority unless assigned;
- normally use 2–3 high-value lanes, not many conflicting agents.

Next action:
`REVISE_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE_FROM_ADJUDICATED_REVIEW`

Status authority: `CURRENT_STATE.md`.
Frozen protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`.

Canonical verification path:
`python -m unittest discover -s tests -v`
