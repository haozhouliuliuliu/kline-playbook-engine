# 00_READ_FIRST

This repository is in `RESEARCH_FOUNDATION`.

Read current authority/navigation in this order:
1. `OWNER_COLLABORATION_CONTRACT.md`
2. `ARCHITECTURE_BASELINE.md` — Skeleton v1.0 ACCEPTED
3. `CURRENT_STATE.md` — current status / authorization / next action
4. `RESEARCH_DIRECTION.md` — Human Playbook First, Owner-approved, with anti-regression guard
5. `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` — FROZEN / BINDING
6. `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` — FROZEN 12/6/6
7. `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
8. `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
9. `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`
10. `docs/reviews/HANDOFF_THIRD_PASS_FAILURE_MODE_REVIEW_2026-08-19.md`
11. `KLINE_PLAYBOOK_ENGINE_HANDOFF_CURRENT_2026-08-19_V3.md` — derived continuity snapshot only

Important current evidence:
- Owner protocol freeze: `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- Pre-outcome firewall implementation: `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`
- Final firewall acceptance: `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md`
- Common Statistical Profile v1 first candidate (historical candidate; NOT_LOCKED): `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
- Statistical engine capability audit (integrated): `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`
- Engine compatibility crosswalk (integrated to main; original branch commit `05ad7f9a94c1a6b885402a4417a0d095dbfa7c56`; main integration `4b2c882331f855c730d125517e6b7fd563025055`): `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK.md`
- Independent adversarial statistical review (integrated to main; original branch commit `5e78605d312ee2e6c22e82dc4d91d651eacac4b2`; main integration `4650e5fe24e4ac50377a2e7440b81921c57c0a87`): `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md`
- Project-brain adjudication of both parallel lines: `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`
- Third-pass handoff/anti-regression review: `docs/reviews/HANDOFF_THIRD_PASS_FAILURE_MODE_REVIEW_2026-08-19.md`
- Known limitations/debt: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`
- Adopted governance: `CROSS_PROJECT_OPERATING_CONTRACT.md` Version 3.1, pinned by SHA256 in `CURRENT_STATE.md`

## Catastrophic anti-regression rule

Do **not** reinterpret the broad Skeleton statement that AI may "find candidate ideas" as permission to return to data-first K-line/chart-pattern/indicator/parameter mining.

Binding current route is:

```text
traceable human trading experience
-> source-faithful AI extraction/structuring
-> versioned Playbook Contract
-> machine operationalization
-> governed historical validation
```

The following is **not** the current authorized research route:

```text
mine K-line/chart patterns / indicators / rule grids / parameters
-> rank by historical PnL/Sharpe
-> retrofit a narrative or human source afterward
```

`RESEARCH_DIRECTION.md` now contains the formal anti-regression interpretation guard. Any future shift back toward data-first automatic strategy/pattern mining is an Owner-gated research-direction change.

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
- Paid ChatGPT↔DS API relay/orchestrator = NOT_ADOPTED_CURRENTLY; brittle VS Code UI relay automation = NOT_ADOPTED_CURRENTLY.
- Current local-agent relay = Owner manual relay only when a DS/local worker is genuinely needed; GPT should do safe repo-only GitHub work directly when capable.
- Conversation handoff = third-pass ready, waiting for Owner acceptance of the fresh conversation's read-only takeover report.
- Owner research/product semantic action = NONE.

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

Do **not** treat the adversarial reviewer's `RECOMMENDED_SIMPLIFIED_V1`, illustrative volatility assumptions, suggested thresholds, 2x cost stress, Holm choice, or block-length formula as adopted/frozen project facts. The adjudication accepted revision requirements, not the reviewer's exact replacement numbers/methods.

Parallel-work rule:
- isolated worktrees/branches for independent workers;
- one integration lane owns `main` and shared authority/state;
- parallel workers do not push `main` or edit shared authority unless assigned;
- normally use 2–3 high-value lanes, not many conflicting agents;
- when several independent lanes are ready, give all runnable prompts together;
- before creating/reusing a worktree, inspect `git worktree list` and branch/remote state.

Fresh-conversation takeover rule:
- first takeover turn is read-only verification only;
- do not modify GitHub, issue DS prompts, adopt tools, start profile revision, extract real claims, or otherwise advance project state;
- report reconstructed authority/state and wait for Owner confirmation.

Recorded next project action **after takeover acceptance**:
`REVISE_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE_FROM_ADJUDICATED_REVIEW`

Status authority: `CURRENT_STATE.md`.
Frozen protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`.

Canonical verification path:
`python -m unittest discover -s tests -v`
