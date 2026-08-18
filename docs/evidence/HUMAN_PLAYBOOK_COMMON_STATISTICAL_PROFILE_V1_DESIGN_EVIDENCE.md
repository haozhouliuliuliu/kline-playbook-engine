# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_DESIGN_EVIDENCE

> Work package: `COMMON_STATISTICAL_PROFILE_V1_DESIGN_AND_INDEPENDENT_REVIEW` — Phase 1
> Phase: `DESIGN_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE`
> Role: statistical design engineer
> Date: 2026-08-19
> Evidence file for: `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`

## 1. Outcome-data integrity statement

This phase used **no candidate outcome data** and **no protected-period outcome access**:

```text
REAL_HUMAN_PLAYBOOK_RUN         = NO
CANDIDATE_PNL_INSPECTION        = NO
EQUITY_CURVE_INSPECTION         = NO
EXPECTANCY_INSPECTION           = NO
SHARPE_INSPECTION               = NO
WIN_LOSS_INSPECTION             = NO
DEVELOPMENT_CALIBRATION_USED    = NO
VALIDATION_ACCESS               = NO (remains LOCKED)
HISTORICAL_FINAL_HOLDOUT_ACCESS = NO (remains LOCKED)
THRESHOLD_TUNING_ON_OUTCOMES    = NO
SYNTHETIC_CALCULATIONS          = YES (arithmetic only; see §4)
```

The only market-related facts read were **non-outcome metadata**: the canonical trading
calendar (trading-day and ISO-week counts per frozen cohort) and code interfaces/field
definitions. No strategy PnL, returns, equity, or any candidate-quality output was computed
or inspected.

## 2. Code / interface inspection record

Files read (interfaces, fields, and behavior — no candidate runs):

- `src/research_firewall.py` — `FrozenResearchProtocol`, `Cohort`, `classify_cohort`,
  `CommonStatisticalProfile` (identity/lock interface + `profile_identity` hash),
  `StatisticalProfileRegistry`, `ResearchWaveManifest` (permanent denominator, counting-unit
  identity, hypothesis bindings), `OutcomeTestRegistration`, `ResearchWaveRegistry`,
  `PreOutcomeGate` (five controls, TEST_ONLY path, VALIDATION/FINAL always denied),
  `ResearchFirewall.request_candidate_outcome_access()` / `evaluate_gate()` /
  `_resolve_binding()`.
- `src/strategy_evidence.py` — `EvidenceLedger`, `DatasetClass`
  (incl. `PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT`, legacy `FINAL_UNSEEN`), `AccessResult`,
  `ExperimentIdentity`, `StrategyIdentity` (via imports from `research_firewall.py`).
- `src/validation_runner.py` — `CapitalSnapshot` (`realized_pnl`, `unrealized_pnl`,
  `equity`, `charged_costs`, `starting_capital`, `state_at`, `position_trading_day`,
  `concrete_contract_id`), `CapitalTransition` (`realized_pnl_change`, `required_cost`,
  `before`/`after`), `ExecutionAssumptions` (`synthetic_fee`, `synthetic_slippage`),
  `ExecutionOutcome` (`fill_price`, `total_cost`), `MarkToMarketTransition`,
  `ValidationRunResult`, `ChronologicalValidationRunner`, `CapitalMarginAssumptions`.
- `src/portfolio_semantics.py` — `PortfolioRequest`, `PortfolioCandidate`,
  `CandidateOutcome`, `AttributedPosition`, `StrategySleeve`, `SharedCapitalState`,
  `PortfolioReconciliation`, `PortfolioEvaluationResult`, `PortfolioCoordinator`.
- `tests/test_research_firewall.py` — how `TEST_ONLY` profiles and identity-bound waves are
  constructed (used to confirm the profile/wave interface can express a real profile without
  schema change).

Key finding recorded in the candidate: the engine can generate per-fill/per-transition
realized PnL, costs, positions, timestamps, contract identity, and trading-day attribution,
but has **no round-trip ledger / per-trade net-return aggregation layer** — hence the
`ENGINEERING_DELTA` requirement (candidate §4.3, §15).

## 3. Authority documents inspected

- `AGENTS.md`, `00_READ_FIRST.md`, `OWNER_COLLABORATION_CONTRACT.md`,
  `CROSS_PROJECT_OPERATING_CONTRACT.md` (v3.1), `ARCHITECTURE_BASELINE.md` (Skeleton v1.0),
  `RESEARCH_DIRECTION.md` (HUMAN_PLAYBOOK_FIRST), `CURRENT_STATE.md`,
  `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` (FROZEN_BINDING)
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` (FROZEN_12_6_6)
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md` (ACCEPTED)
- `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`
- `docs/evidence/CANONICAL_TRADING_CALENDAR.json` (metadata only)

No frozen semantics were modified. No `SEMANTIC_CONFLICT` was identified.

## 4. Synthetic calculations (arithmetic only — no candidate returns)

Computed with a temporary script (created outside the repository in `%TEMP%`, run with the
system Python, then deleted; no repository code changed):

- **Trading-day / ISO-week counts per frozen cohort** (from `CANONICAL_TRADING_CALENDAR.json`):
  - DEVELOPMENT (2024): 242 trading days, 52 distinct ISO weeks;
  - VALIDATION (2025-01-01..06-30): 117 trading days, 27 distinct ISO weeks;
  - PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT (2025-07-01..12-31): 126 trading days,
    27 distinct ISO weeks.
  Used to ground the sufficiency thresholds (§7 of the candidate) and the 6-month sparse
  strategy analysis (§18 item 7).
- **ESS = N / max(1, 2H − 1)** illustrative table (e.g., H=1 → ESS=N; H=3, N=150 → ESS=30
  → exactly meets S7; H=5, N=200 → ESS≈22.2 → S7 fails). Confirms the holding-horizon
  adjustment behavior.
- **Holm step-down thresholds at α=0.05** for M=5/10/20/40 (e.g., M=10 smallest threshold
  0.005 → largest 0.05; M=20 → 0.0025…0.05). Confirms multiplicity behavior.
- **Circular week-block bootstrap size m = ceil(W_active / L_weeks)** for W=12/26/52,
  L=1/2/4 (e.g., VALIDATION-scale W=26, L=4 → m=7). Confirms stability conditions.
- **Block-length rule L_weeks = min(max(1, ceil(H_median/5)), 4)**: H=1..5 → L=1; H=6..10 →
  L=2; H=15 → L=3; H=16 → L=4 (cap). Confirms deterministic behavior.

These are pure arithmetic on pre-registered formulas and calendar metadata; no candidate
outcome was involved.

## 5. Primary literature inspection record

Verified directly during this phase:

- **Künsch (1989)**, "The Jackknife and the Bootstrap for General Stationary Observations",
  Ann. Statist. 17(3):1217–1241 — abstract and bibliographic identity verified on the
  journal's Project Euclid page (primary publisher-hosted page).
- **Romano & Wolf (2005)**, "Stepwise Multiple Testing as Formalized Data Snooping",
  Econometrica 73(4):1237–1282 — bibliographic identity verified on Michael Wolf's official
  University of Zurich publications page (author's page).
- **Politis & Romano (1992)**, "A Circular Block-Resampling Procedure for Stationary Data",
  in Exploring the Limits of Bootstrap, Wiley, 263–270 — verified on Dimitris Politis's
  official UCSD publication page.
- **Politis & Romano (1994)**, "The Stationary Bootstrap", JASA 89(428):1303–1313 —
  verified on Politis's official UCSD publication page.
- **Politis & White (2004)**, "Automatic Block-Length Selection for the Dependent
  Bootstrap", Econometric Reviews 23(1):53–70 — verified on Politis's official UCSD
  publication page (incl. the 2009 Patton/Politis/White correction, which the candidate
  cites as a reason not to use ABL in v1).
- **Politis, Romano & Wolf (1999)**, *Subsampling*, Springer — verified on both authors'
  official pages.

Cited from established bibliographic knowledge (full-text retrieval blocked by
paywalls/CAPTCHA or PDF-extraction limits; no blog/secondary trading source used):

- Holm (1979), Scand. J. Statist. 6(2):65–70.
- White (2000), Econometrica 68(5):1097–1126.
- Sullivan, Timmermann & White (1999), J. Finance 54(5):1647–1691.
- Benjamini & Hochberg (1995), JRSS-B 57(1):289–300.
- Lo (2002), Fin. Anal. J. 58(4):36–52.
- Newey & West (1987), Econometrica 55(3):703–708.
- Cameron, Gelbach & Miller (2008), Rev. Econ. Statist. 90(3):414–427.
- Bailey, Borwein, López de Prado & Zhu (2014), Notices Amer. Math. Soc. 61(5):458–471.

The role each reference plays, and what it does not prove, is recorded in candidate §16.

## 6. Tests

```text
BASELINE (before design): python -m unittest discover -s tests -v
  235 tests OK, 3 skipped (matches the documented accepted state)

AFTER DESIGN (no production code changed; document-only phase):
  python -m unittest discover -s tests -v
  235 tests OK, 3 skipped (expected: identical)
```

No production or test code was modified in this phase. The candidate intentionally records
its required engineering deltas rather than implementing them before independent review
(candidate §15), consistent with the task instruction "不要为了'做了事'强行改代码".

## 7. Phase output

```text
DESIGN_VERDICT                 = DESIGNED_CANDIDATE
PRIMARY_ESTIMAND               = mean per-trade net return on entry notional (completed round trips)
UNCERTAINTY_METHOD             = circular week-block bootstrap, one-sided alpha=0.05, B=10000, fixed seed
SUFFICIENCY_RULE               = N>=60, D_days>=30, W_active>=8, W>=4*L, day conc<=0.50, week conc<=0.75, ESS>=30, open_ratio<=0.25
MULTIPLICITY_METHOD            = Holm step-down FWER alpha=0.05 over the wave's permanent denominator M
SEMANTIC_CONFLICT              = NONE
ENGINEERING_DELTA              = REQUIRED (round-trip ledger, statistical evaluator, canonical profile doc, counting-unit identity, RNG wrapper, tests)
COMMON_STATISTICAL_PROFILE_V1_STATUS = CANDIDATE_NOT_LOCKED
NEXT_STAGE                     = INDEPENDENT_ADVERSARIAL_REVIEW_OF_COMMON_STATISTICAL_PROFILE_V1
```
