# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK

> Version: 1.0
> Date: 2026-08-19
> Status: CROSSWALK_COMPLETE / READ_ONLY / NO_STATISTICAL_DECISION / NO_CANDIDATE_OUTCOME
> Work package: `COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK` (parallel worker)
> Branch: `parallel/stat-engine-audit`
> Candidate read: `git show origin/main:docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
> (origin/main @ `6ef668fd7214fcef2f12b71cb3e9ea2a36bfcaf7` — "design Common Statistical Profile v1 candidate")
> Capability baseline: `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md` (this branch)
> Frozen authority unchanged: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Frozen chronology unchanged: `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`

This is a **compatibility / falsification crosswalk only**. It does not adjudicate the candidate's
numeric or method choices, does not modify the candidate, does not modify frozen protocol, and does
not implement a statistics framework. It answers one question for each candidate requirement:
**can the current engine actually and precisely produce the input that requirement needs?**

---

## CROSSWALK_VERDICT

The candidate is **broadly engine-compatible in data terms and mostly in SEMANTIC terms**, with three
kinds of gaps:

1. **Missing materialization (SMALL_DELTA, no framework needed):** the round-trip ledger, day/week
   helpers, holding-horizon derivation, and aggregation functions do not exist. The engine already
   records every fact they need (`position_id`, per-fill/transition PnL and cost, timestamps,
   `position_trading_day`, contract identity). The engine's `position_id` lifecycle is a natural,
   already-deterministic round-trip key that matches the candidate's "one completed round trip =
   one position, one concrete contract" definition.
2. **Design ambiguities the candidate must adjudicate (DESIGN_AMBIGUITY), not the engine:** the
   exact round-trip counting rule for multi-leg entries / multi-leg partial closes; the holding-
   horizon `H` counting convention; the `open_ratio` denominator and cohort-boundary convention; the
   exact meaning of "parameter branch" under Holm versus the firewall's `parameter_search_identity`;
   and whether "2× cost/friction stress" is fee-only (candidate's formula) or must also stress
   slippage (which lives inside gross PnL, not the cost term).
3. **Tech-debt blockers (UNSAFE_UNTIL_TECH_DEBT_FIXED / DATA BLOCKER):** TD-002 pollutes only
   equity-path-derived artifacts (not the primary estimand, not sufficiency counts, not realized
   PnL); TD-001 is a discipline requirement on any new day/week helper; LIMIT-001 is a **data
   blocker** for producing the real-corpus VALIDATION/FINAL round-trip ledger (the engine fails
   closed, it does not silently fill).

No `SEMANTIC_CONFLICT` with frozen research semantics was found in the candidate's requirements as
read. `INSUFFICIENT_EVIDENCE`, the permanent wave denominator, cohort immutability, and the
pre-outcome lock are all consistent with the firewall and Protocol v1.0.

---

## A. PRIMARY estimand compatibility (completed round-trip net return / entry notional)

Candidate: `r_t = (gross realized PnL_t − total cost_t) / entry notional_t` over completed round
trips; a completed round trip = position opened and fully closed inside the cohort, attributed to
**one concrete contract**, realized PnL settled.

Engine facts that map directly:

- `CapitalSnapshot.position_id` is created at first open, **preserved across adds and partial
  closes**, and regenerated only after a full close. It is a deterministic, unambiguous
  round-trip key. The ledger delta groups `CapitalTransition` records by `position_id`.
- `entry notional` per leg = `fill_price × capital_assumptions.contract_multiplier × quantity`
  on each OPEN transition (all available); the engine already implements a weighted
  `average_open_price`, and multiple entry legs before the first mark are supported.
- `gross realized PnL_t` = sum of `realized_pnl_change` across that position's closing
  transitions (full/partial close, forced liquidation) — engine records `realized_pnl_change`
  exactly and deterministically.
- One concrete contract per position is **enforced by the engine** ("a mapping roll cannot
  silently change the concrete contract of an open position"). This matches the candidate's
  "one concrete contract" trade definition — but it also means **a roll cannot be represented
  as one trade**: opening on contract A and rolling to B produces two separate round trips
  (one on A, one on B). The candidate's definition is consistent with that, so this is
  ENGINE_READY; it is a constraint the profile may rely on but must state.
- Forced liquidation produces a closing transition with realized PnL and is a valid way to
  "fully close" a position; it would be a completed round trip (and independently triggers the
  R1 breach check). Engine-supported.

**Trade identity ambiguity (partial close → how many observations):** the candidate defines
`gross` as the sum across "the round trip's closing transitions (including partial closes)" and
`entry notional` as the sum over "the legs that opened the position", which strongly implies
**one position = one observation regardless of entry-leg count or partial-close count**. This is
exactly what the engine's `position_id` can deliver. **However, the candidate has not explicitly
pinned the counting rule "one `position_id` = one round-trip observation, and partial-close legs
are merged into that one observation."** Until pinned, three failure modes remain open:
multiple partial closes inflated into multiple observations (N inflation, item B); multiple entry
legs mis-split into separate trades; and same-strategy successive flat→open→flat cycles on the
same instrument/day being ambiguous. → **DESIGN_AMBIGUITY (adjudicate the counting rule; the
engine provides `position_id` as the ready-made key).**

**Add-to-position:** engine supports adds only **before the first mark-to-market** ("cannot add
to a position after mark-to-market in the minimum lifecycle"). Entry legs are therefore
contiguous in time. Consistent with the candidate's "legs that opened the position"; the profile
may rely on this constraint.

**All-in cost / normalized net return:** all-in cost per round trip = sum of `required_cost` /
`charged_costs` deltas across the position's transitions (synthetic fee + close-today/previous
offset fees; forced liquidation charges the synthetic fee). The ledger must take cost from
**one** source to avoid double counting (see §G). Net return is a pure ratio; the engine data is
sufficient.

**Cohort classification:** `FrozenResearchProtocol` dates + `classify_cohort` (firewall) exist;
entry/exit timestamps per round trip can be classified against DEVEL/VALIDATION/FINAL boundaries.

Classification: **SMALL_DELTA** (ledger) + **DESIGN_AMBIGUITY** (round-trip counting rule to pin).

---

## B. Equal-weight per-trade aggregation — risks only

The engine data supports notional-normalized per-trade returns (quantities, fill prices,
multiplier per leg are all recorded). Equal-weight-per-trade aggregation is a pure downstream
choice the engine can serve. Reported risks (no decision made):

- **Small- vs large-notional trades compared fairly:** only if every observation is
  normalized by its own entry notional. The engine has all leg prices/quantities, so this is
  achievable; the ledger must not compare raw PnL.
- **Multiple partial closes double-weighted:** avoidable **only** if the ledger groups by
  `position_id` (one observation per round trip). If each partial-close leg becomes its own
  observation, N inflates and the mean is double-weighted. → depends on adjudicating §A.
- **A long position split into many close legs artificially raising N:** same dependency; the
  engine can prevent it via `position_id` grouping.
- **A frequent strategy naturally getting more statistical weight:** under equal weight per
  trade, a higher-frequency family has larger N in its own hypothesis sample — that is
  expected per-hypothesis behavior and does not cross hypotheses (Holm handles cross-
  hypothesis multiplicity by M). The risk would only arise if trade sets from different
  hypotheses/families were pooled into one sample, which the candidate does **not** do. Low
  residual risk; report only.

Classification: **SMALL_DELTA** (ledger normalizes by entry notional; group by `position_id`),
with the §A **DESIGN_AMBIGUITY** as a prerequisite.

---

## C. Holding horizon (H_median, ESS = N / max(1, 2H − 1))

The candidate pinned H as **trading days** ("median holding horizon of the cohort's completed
trades, in trading days"; ESS factor `2H−1`). The engine can deterministically produce both ends
of the horizon:

- entry trading day: `position_trading_day` on the first OPEN snapshot;
- exit trading day: `SessionMetadata.trading_day_at(exchange, instrument, close_fill.evaluated_at)`
  (authoritative path) — for full close, partial-close-final, and forced liquidation.

**H counting convention is NOT pinned by the candidate (DESIGN_AMBIGUITY):**
- Is same-day (intraday) H = 1 or H = 0? (`H=1 → ESS=N`; `H=0` also → `ESS=N` under
  `max(1,2H−1)`, so the effect only appears once H ≥ 2.)
- Is the count inclusive of the entry day, exclusive, or elapsed trading days between
  entry and exit dates (a position opened day D and closed day D+1 → H=1 or H=2)?
- Night-session semantics: a position opened in the night session of day D and closed in the
  day session of D+1 spans how many trading days? The engine's `position_trading_day` is a
  single date per snapshot and `SessionMetadata` is the night-session authority — the data is
  unambiguous, but the **convention** for counting elapsed trading days must be pinned by the
  designer before ESS and `L_weeks` are computable.
- `H_median` is computed over **completed** round trips only (the candidate says "cohort's
  completed trades"); the engine can identify completed vs still-open via `position_id`
  close status.

Classification: **SMALL_DELTA** (derivable) + **DESIGN_AMBIGUITY** (H counting convention).
TD-001 matters here only if the wrong trading-day authority is used (must use `SessionMetadata`).

---

## D. Weekly block bootstrap — data requirements

Candidate block key: each trade's block = ISO calendar week of its **exit trading day**
(`exit_week`), pinned by the candidate; only weeks with ≥1 completed trade are active weeks.

Engine/data mapping:

- **trade → trading day:** derivable — `position_trading_day` / `SessionMetadata` (see §C).
- **trading day → ISO/calendar week:** pure helper `date.isocalendar()`; **not present in the
  engine today** — SMALL_DELTA (a helper, no semantics). Note ISO week boundaries differ from
  the cohort cut-offs (2024-12-30 is ISO week 1 of 2025, etc.); the ledger must be explicit
  that "week" = ISO week, as the candidate says.
- **cross-instrument same-week grouping:** per-trade instrument identity + exit week exist; the
  bootstrap resamples whole weeks, so contemporaneous cross-product dependence is preserved by
  construction. SMALL_DELTA (ledger emits `(hypothesis, trade, exit_week, product, r_t)` rows).
- **overlapping position information:** the engine has **no overlapping-exposure index**
  (capability audit §7). The candidate does **not** need a per-pair overlap index — it handles
  overlap by whole-week resampling + ESS (H). So the missing overlap index is **not a blocker**
  for this candidate; only per-trade `exit_week` and `H` are needed. State this explicitly so
  the profile does not assume an overlap index exists.
- **"One trade → one unique week assignment":** the candidate assigns each trade to exactly one
  week (`exit_week`). This is **required and already pinned**. A multi-week position (open in
  week 1, close in week 3) is wholly assigned to its exit week — a modeling choice the
  candidate made; the engine can produce it, but the profile must be aware the trade's return is
  a multi-week return collapsed into one block. This is a design choice already made (not
  ENGINE ambiguity), but worth flagging as a known property.

Classification: **SMALL_DELTA** (week helper + ledger rows; deterministic seed wrapper is
stdlib-only per candidate §6.7). No ENGINE_AMBIGUITY — exit-week assignment is pinned.

---

## E. Concentration metrics (day ≤ 50%, week ≤ 75%)

The candidate **has pinned the concentration basis: trade counts** ("Concentration is measured
on trade counts (non-outcome structure), not PnL"; `max trades in a day / N`, `max trades in a
week / N`). It is not ambiguous.

- Engine support: per-trade day and exit-week are derivable (§C/§D); count concentration is a
  pure aggregation. SMALL_DELTA.
- Distinct from **R2** (single-trade concentration ≤ 40% of absolute net PnL, i.e.,
  `max |r_t| / Σ|r_t|`), which is PnL-based and needs per-trade `r_t` (ledger). The candidate is
  explicit about both; no ambiguity, but the two must not be confused in implementation.
- No-trade days contribute nothing to S5 (they have zero trades); consistent with candidate §4.2
  (zero-trading days not imputed).

Classification: **SMALL_DELTA** (S5/S6 and R2 all computable from ledger; basis already pinned).

---

## F. open_ratio ≤ 25% — denominator ambiguity

Candidate S8: "positions still open at cohort end / total positions".

**The denominator is not pinned (DESIGN_AMBIGUITY):**
- Is "total positions" = all `position_id`s opened inside the cohort (including those still
  open at cohort end), or only completed round trips, or also positions that began **before**
  the cohort boundary and are still open at cohort end?
- The primary sample (§A) contains only **completed** round trips (opened AND closed inside the
  cohort). "Positions still open at cohort end" are therefore **not in the primary sample** —
  so S8's denominator must be a broader set than the primary sample. The candidate does not
  state what that broader set is, nor whether a position opened pre-cohort counts.
- The engine **can** safely generate the underlying facts: per `position_id`, open timestamp and
  close-or-still-open status (close status = whether a full-close/liquidation transition exists
  by cohort end). So the data is safe; only the counting convention needs adjudication.

Classification: **SMALL_DELTA** (facts available) + **DESIGN_AMBIGUITY** (denominator and
cohort-boundary convention). Not affected by TD-002 (open/closed is a position state, not an
unrealized value).

---

## G. Cost-stress (2×) compatibility

Candidate formula: `r_t^stress = (gross_t − 2 × cost_t) / entry notional_t` — a **post-hoc,
additive** recompute on the ledger, not a re-run of the engine.

Engine support for the *additive* interpretation:

- The cost term is additive per round trip: `required_cost` / `charged_costs` deltas
  (synthetic fee per fill + close-today/previous offset fee; forced liquidation charges the
  synthetic fee). Doubling the summed cost term is deterministic and engine-supported. The
  engine already separates `realized_pnl_change` (gross) from `charged_costs` (fees), so the
  ledger can emit `gross`, `cost`, and `gross − 2×cost` from one pass. **ENGINE_READY for the
  post-hoc fee-doubling interpretation.**
- Contract-specific assumptions: each position binds `execution_assumption_id`,
  `capital_assumption_id`, `offset_cost_assumption_id`. A uniform 2× multiplier on the cost
  term preserves the relative fee structure across contracts — consistent.

Two hazards the profile must adjudicate (DESIGN_AMBIGUITY / semantics):

1. **Slippage lives in GROSS, not in the cost term.** The engine computes
   `fill_price = observation.price ± synthetic_slippage`, so slippage changes `gross realized
   PnL`; the separate cost term (`total_cost`/`charged_costs`) is **fees only**. The candidate's
   `2× cost` therefore stresses **fees only**, not slippage. If the intent of "2× cost/friction
   stress" is to stress *all* friction including slippage, that requires a **re-run stress**
   with `2 × synthetic_slippage`, which changes fill prices, may change fills, and thereby
   changes N / sufficiency — a materially different procedure than the candidate's formula. The
   designer must pin: **slippage is gross, stress doubles fees only** (candidate's formula), or
   adopt a re-run slippage stress. → **DESIGN_AMBIGUITY.**
2. **Double-charge hazard in the ledger.** Costs can be sourced from either
   `ExecutionOutcome.total_cost` (per fill) or `CapitalSnapshot.charged_costs` deltas (per
   transition). Summing **both** double-counts. The ledger must consume exactly one source for
   `total cost_t`. This is a ledger-construction guardrail, not an engine bug.

Forced liquidation: its fee is part of `charged_costs`; if a liquidated round trip is in the
sample it is stressed consistently (and independently fails R1).

Classification: **ENGINE_READY** (post-hoc fee-doubling) + **DESIGN_AMBIGUITY** (slippage-in-gross
vs fee-only stress; confirm cost source to avoid double counting).

---

## H. Holm denominator (M) compatibility

Candidate: Holm step-down FWER over the wave's **permanent tested denominator M**, with
`hypothesis_test_id` as the machine counting unit; PRIMARY = 1, each outcome-tested alternative =
1, each outcome-tested instrument/timeframe/context/parameter branch = 1; FAIL / INSUFFICIENT
remain in M.

Firewall/engine machine facts:

- `ResearchWaveManifest.tested_hypothesis_test_ids` is the **single permanent denominator**;
  `ResearchWaveRegistry.denominator(wave_id)` returns exactly `len(tested_hypothesis_test_ids)`.
- `OutcomeTestRegistration` binds exactly one `hypothesis_test_id` to one
  `primary_branch_identity`, one `scope_identity`, one `parameter_search_identity`, one wave, one
  profile, one counting-unit identity. Adding a hypothesis after outcome-test start requires a
  new wave/search event (frozen). FAIL/INSUFFICIENT remain in the denominator.
- So the engine can deterministically supply **M = |tested_hypothesis_test_ids|** of the locked
  wave manifest, and the candidate's "one hypothesis = one hypothesis_test_id" is machine-
  consistent. The candidate's own §14 pins the counting-unit identity (e.g.,
  `HYPOTHESIS_TEST_ID_V1`) — **ENGINE_READY** for M itself.

**Counting-language ambiguity to reconcile (DESIGN_AMBIGUITY):**
- The candidate says "every ... **parameter branch** that is outcome-tested = 1". The firewall's
  model holds parameter **search** *inside* one hypothesis via `parameter_search_identity`
  (a parameter grid is one hypothesis = one `hypothesis_test_id`, with the search identity
  binding the grid). A literal reading of the candidate ("each parameter branch = 1") would
  multiply M where the firewall intends one search event. The designer must pin the rule so
  that the **statistical denominator M equals the firewall's `len(tested_hypothesis_test_ids)`**
  machine-identically — i.e., decide explicitly whether a parameter-grid sweep counts as one
  hypothesis (firewall default) or as many (candidate-literal), and likewise for
  instrument/timeframe/context variants: each distinct outcome-tested variant is a separate
  `hypothesis_test_id` (own registration, own PRIMARY/scope/search binding).
- The candidate and firewall agree on: PRIMARY = 1; outcome-tested alternatives = separate
  counted hypotheses; deterministic non-outcome work not in M. Only the "parameter branch"
  phrasing needs reconciliation.

Classification: **ENGINE_READY** (M available) + **DESIGN_AMBIGUITY** (parameter-branch counting
language; must be reconciled to firewall M).

---

## I. TD-001 / TD-002 / LIMIT-001 → candidate rule matrix

| Candidate rule | TD-001 (calendar authority) | TD-002 (partial-close unrealized zeroing) | LIMIT-001 (missing price-limit facts) |
|---|---|---|---|
| **PRIMARY estimand `r_t`** (realized, per round trip) | Unaffected if entry/exit trading days come from `SessionMetadata` (authoritative) | **Unaffected** — uses realized deltas + position state, not unrealized/equity | **DATA BLOCKER** for real-corpus generation (fails closed → no trade produced); no silent pollution |
| **S1 N_trades** | Unaffected | Unaffected (position count) | Blocked by trade-set generation (above) |
| **S2 D_days** | Affected **only if** wrong calendar used (bootstrap vs SessionMetadata) — must consume SessionMetadata | Unaffected | Blocked (above) |
| **S3 W_active** | Same as S2 (must use SessionMetadata) | Unaffected | Blocked (above) |
| **S4 W_active ≥ 4L** | Same as S2 | Unaffected | Blocked (above) |
| **S5/S6 day/week count concentration** | Same as S2 (trading-day/week basis) | Unaffected (counts, not values) | Blocked (above) |
| **S7 ESS (H)** | Same as S2 (H in trading days) | Unaffected (H from open/close trading days) | Blocked (above) |
| **S8 open_ratio** | Unaffected (position state; but day basis if used) | **Unaffected** — open/closed is position state, not unrealized value | Blocked (above) |
| **Week-block bootstrap (exit_week)** | Same as S2 (exit trading day → ISO week) | Unaffected (exit week from close event) | Blocked (above) |
| **R1 forced-liquidation/breach > 0** | Unaffected | **AFFECTED IF** breach is re-derived from a reconstructed equity path that includes the partial-close snapshot (equity artificially dips to cash when unrealized is zeroed). The engine's own breach detection runs on marks (post-recompute) and is unaffected. → use engine mark-transition breach facts, not a reconstructed path | Blocked (above) |
| **R2 single-trade concentration (PnL)** | Unaffected | Unaffected (per-trade realized `r_t`) | Blocked (above) |
| **Economic floor 2 bp** | Unaffected | Unaffected (per-trade realized) | Blocked (above) |
| **Cost stress (2×)** | Unaffected | Unaffected (realized + fee cost term) | Blocked (above) |
| **Equity/drawdown diagnostics** (family-specific only, not common) | Unaffected | **AFFECTED** at partial-close snapshots — any equity-path/drawdown diagnostic must either avoid partial-close snapshots or wait for the TD-002 fix | Blocked (above) |

Precise TD-002 conclusion for this candidate: the **primary estimand, sufficiency S1–S8,
concentration, ESS, open_ratio, R2, economic floor, and cost stress are NOT polluted by TD-002**
because they consume realized PnL / position state / trading-day facts only. TD-002 only pollutes
**equity-path-derived artifacts** (drawdown diagnostics; and R1 only if breach is reconstructed
from a partial-close-including equity path instead of the engine's mark-transition facts).
Recommended: consume the engine's `MarkToMarketTransition.breached` and `ForcedLiquidationRequirement`
facts directly for R1, and keep any drawdown diagnostic off partial-close snapshots until the
mark-preservation semantic (TD-002) is implemented.

Precise TD-001 conclusion: TD-001 is a **discipline requirement**, not an active polluter. Every
new day/week helper must consume `SessionMetadata.trading_day_at` (the authoritative path), never
`bootstrap_semantics.NormalizedSessionCalendar`. If honored, S2/S3/S5/S6/S7/H/exit_week are safe.

Precise LIMIT-001 conclusion: LIMIT-001 is a **data blocker**, not a code bug. Contract-bound
confirmatory execution fails closed when a required PIT price-limit fact is missing, so the
real-corpus VALIDATION/FINAL round-trip ledger cannot be produced until governed facts are bound by
effective period. With synthetic facts (tests) the whole pipeline is buildable now.

---

## Candidate item → classification

| Candidate item | Classification |
|---|---|
| PRIMARY_ESTIMAND (round-trip net return / entry notional) | **SMALL_DELTA** (round-trip ledger; `position_id` key) + **DESIGN_AMBIGUITY** (counting rule: one `position_id` = one observation) |
| Equal-weight per-trade aggregation | **SMALL_DELTA** + **DESIGN_AMBIGUITY** (dependent on §A grouping; partial-close N-inflation risk) |
| H_median (trading days) / ESS | **SMALL_DELTA** + **DESIGN_AMBIGUITY** (H counting convention) |
| Week-block bootstrap (circular, exit-week, B=10k, seeded) | **SMALL_DELTA** (ISO-week helper + ledger rows + stdlib RNG wrapper) |
| S1–S6 (N, D_days, W_active, W≥4L, day/week count concentration) | **SMALL_DELTA** (pure aggregation; basis already pinned to trade counts) |
| S7 ESS | **SMALL_DELTA** + **DESIGN_AMBIGUITY** (H convention) |
| S8 open_ratio | **SMALL_DELTA** (facts available) + **DESIGN_AMBIGUITY** (denominator / boundary convention) |
| R1 forced-liquidation/breach | **ENGINE_READY** if consuming engine mark-transition/liquidation facts; **UNSAFE_UNTIL_TECH_DEBT_FIXED** only if re-derived from a reconstructed equity path (TD-002) |
| R2 single-trade concentration | **SMALL_DELTA** (per-trade `r_t` from ledger) |
| Economic floor 2 bp | **SMALL_DELTA** (per-trade `r_t`) |
| COST_STRESS 2× | **ENGINE_READY** for post-hoc fee-doubling + **DESIGN_AMBIGUITY** (slippage-in-gross; cost-source double-count guard) |
| Holm denominator M | **ENGINE_READY** (M = len(`tested_hypothesis_test_ids`)) + **DESIGN_AMBIGUITY** (parameter-branch counting language vs `parameter_search_identity`) |
| Decision table / cohort immutability / INSUFFICIENT_EVIDENCE | **ENGINE_READY** (firewall gate + frozen wave semantics already support these) |

No **MEDIUM_DELTA** item is introduced by this candidate itself: the only medium delta in the
engine (multi-day portfolio/equity series for drawdown) is needed **only for family-specific
drawdown diagnostics**, which the candidate explicitly makes non-common. The common pipeline is
all small deltas.

---

## Minimum implementation order (engineering dependencies only; NOT a statistical decision)

1. **Round-trip ledger** — group `CapitalTransition` by `position_id`; emit per round trip:
   entry legs → entry notional; closing transitions → gross realized; all-in cost from **one**
   source (`required_cost`/`charged_costs` deltas, never both); entry/exit timestamps and
   trading days; exit ISO week; open/closed-at-cohort-end status; cohort classification. This is
   the prerequisite for every rule.
2. **Day/week helpers** — trading-day authority = `SessionMetadata` only (TD-001 guardrail);
   ISO week via `date.isocalendar()`. Prerequisite for S2/S3/S5/S6/S8, `exit_week`, H.
3. **H derivation + convention pin** — entry/exit trading day per round trip; the designer pins
   the H counting convention before ESS/S4/L_weeks are meaningful.
4. **Sufficiency gate S1–S8** — pure evaluator over the ledger + day/week helpers.
5. **Per-trade `r_t` + R2 + economic floor** — normalized returns, single-trade concentration,
   floor check.
6. **Week-block bootstrap** — circular blocks over active weeks, `L_weeks` rule, deterministic
   seed (stdlib `random.Random`), one-sided p / α-quantile lower bound.
7. **Holm step-down** — read M from the locked wave manifest's `tested_hypothesis_test_ids`
   (bind to `multiplicity_counting_unit_identity`); reconcile the parameter-branch counting
   language first.
8. **Decision table + cost-stress recompute** — fixed order (integrity → sufficiency → risk →
   edge → stress); post-hoc fee-doubling on the ledger (confirm slippage-in-gross semantics).
9. **TD-002 mark-preservation semantic** — before any equity-path/drawdown diagnostic or a
   reconstructed-path R1 is used as evidence (parallel to 1–8; must precede final-quality
   equity-path claims).
10. **TD-001 consolidation** — isolate/retire bootstrap `NormalizedSessionCalendar` before any
    day-level helper is trusted (parallel to 2).
11. **LIMIT-001 governed price-limit facts** — bind by effective period before producing the
    real-corpus VALIDATION/FINAL ledger (data dependency, parallel to 1–8 in design time).
12. **Canonical numeric profile doc + counting-unit identity + RNG wrapper + profile-identity
    binding** — encode the numeric spec into `CommonStatisticalProfile` fields so
    `profile_identity` locks the numbers.

---

## Things the engine can already guarantee (for the candidate's use)

- Deterministic, replay-stable per-fill and per-transition PnL/cost accounting (`Decimal`,
  identity-bound, chronological, fail-closed on reorder).
- `position_id` as a stable round-trip key preserved across adds and partial closes.
- Realized PnL of the closed portion is exact even under partial close (TD-002 does not touch it).
- One concrete contract per position (roll = separate round trips) — matches the candidate's
  trade definition.
- Authoritative trading-day identity via `SessionMetadata`; entry/exit trading days derivable.
- Versioned execution/capital/offset-cost assumption identities for cost attribution.
- Firewall: permanent wave denominator M, profile/identity locks, pre-outcome gate, cohort
  classification — all gate-tested.
- Fail-closed execution: missing price-limit facts raise, never silently fill (LIMIT-001).

## Things the profile must NOT assume

- No round-trip ledger, day/week helpers, H, ESS, concentration, open_ratio, bootstrap, or Holm
  implementation exists today — all are SMALL_DELTA work.
- Must not assume a multi-day portfolio/equity series or drawdown path exists (only a
  single-decision-point portfolio; family drawdown diagnostics need the medium delta).
- Must not assume partial-close snapshots are safe for equity-path/drawdown use (TD-002).
- Must not assume `position_id` grouping is automatically adopted — the counting rule must be
  explicitly pinned or N can inflate via partial-close legs.
- Must not assume slippage is inside the cost term — it is inside gross (fill price); "2× cost"
  stresses fees only unless a re-run slippage stress is adopted.
- Must not assume any overlapping-exposure index exists (not needed by this candidate, but not
  present).
- Must not use the bootstrap `NormalizedSessionCalendar` for any day/week fact (TD-001).
- Must not assume real-corpus VALIDATION/FINAL round trips can be produced until LIMIT-001
  governed price-limit facts are bound.
- Must not assume execution events are directly keyed by `hypothesis_test_id`/`wave_id` — the
  ledger must join via experiment → `OutcomeTestRegistration`.

---

## Design ambiguities requiring adjudication (by the profile designer, not this worker)

1. **Round-trip counting rule:** one `position_id` = one observation (engine-ready key) vs
   partial-close-leg-as-observation. Must pin to prevent N inflation (§A/B).
2. **H holding-horizon convention:** trading days, inclusive/exclusive of entry day, same-day
   H=1 vs H=0, night-session spanning (§C).
3. **open_ratio denominator:** "total positions" = all positions opened in cohort (incl. still
   open), vs also pre-cohort positions; and the cohort-boundary rule (§F).
4. **Cost-stress scope:** fee-only post-hoc doubling (candidate formula) vs re-run slippage
   stress; and the single cost source to avoid double counting (§G).
5. **Holm "parameter branch" counting:** grid-as-one-search-event (firewall
   `parameter_search_identity`) vs each parameter set = 1 hypothesis; must make statistical M
   machine-identical to firewall M (§H).
6. **Exit-week assignment property:** multi-week returns collapsed to exit week (candidate
   already pins exit week; confirm the property is intended).

---

## Tests / evidence

- This crosswalk is **evidence-only**: no production code, no tests, and no candidate were
  modified. Full suite re-run: `python -m unittest discover -s tests -v`.
- Baseline referenced: `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`
  (this branch) — engine capability map used throughout.
- Candidate read at: `git show origin/main:docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
  (origin/main @ `6ef668fd7214fcef2f12b71cb3e9ea2a36bfcaf7`).
- No frozen protocol, candidate, or CURRENT_STATE/00_READ_FIRST file was modified.
