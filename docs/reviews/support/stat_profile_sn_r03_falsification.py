"""Synthetic-only falsification for the revision candidate-0.3 daily-score
self-normalized inference (SECOND INDEPENDENT REVIEW lane).

Purpose
-------
Reproducible, deterministic, candidate-outcome-free simulation used by
HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_SELF_NORMALIZATION_SECOND_REVIEW.md.

Scope
-----
* Part 0: pivotal-law calibration from scratch (signed T_infinity quantiles).
  Verifies whether the candidate smoke-test value q95(T_infinity)=5.335 is the
  correct ONE-SIDED 5% threshold or the TWO-SIDED 5% (one-sided 2.5%) threshold.
* Part 1: finite-sample size under H0: theta=0 at nominal one-sided 5%, for
  D = 117, 126, 242, 500 and processes A..J.
* Part 2: power at standardized mean shifts 0.1/0.2/0.3 sigma for a few
  representative processes.

No candidate outcomes, no canonical market returns, no real playbook data are
read or used. Only synthetic stochastic fixtures. numpy is used because it is
already present in the environment; no new runtime dependency is added.

Determinism: every process uses numpy.random.default_rng(seed) with fixed seeds.
"""

from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# Statistic definitions (exactly as in candidate-0.3 section 6)
# ---------------------------------------------------------------------------


def self_normalized_stat(z: np.ndarray, theta0: float = 0.0) -> float:
    """T_SN(theta0) = sqrt(D) * Z_bar / sqrt(V_D).

    z: 1-D array of daily scores Z_d (already the full authoritative day
       sequence including zero-event days). For the boundary null theta0=0 the
       caller passes Z_d = S_d; for general theta0 the caller passes
       Z_d = S_d - theta0 * C_d.
    """
    z = np.asarray(z, dtype=np.float64)
    d = z.shape[0]
    z_bar = z.mean()
    a_t = np.cumsum(z - z_bar)                 # A_t = sum_{j<=t}(Z_j - Z_bar)
    v_d = np.sum(a_t * a_t) / float(d * d)     # V_D = D^-2 sum A_t^2
    if not np.isfinite(v_d) or v_d <= 0.0:
        return np.nan
    return np.sqrt(d) * z_bar / np.sqrt(v_d)


# ---------------------------------------------------------------------------
# Part 0: Pivotal law calibration from scratch
# ---------------------------------------------------------------------------

def brownian_pivot_draws(n_paths: int, grid: int, seed: int = 20260819) -> np.ndarray:
    """Draw the signed pivot T_infinity = B(1)/sqrt(int_0^1 (B(r)-rB(1))^2 dr).

    B(r) - rB(1) is a standard Brownian bridge; the integral is the squared L2
    norm of the bridge. Returns n_paths i.i.d. draws of the signed pivot.
    """
    rng = np.random.default_rng(seed)
    increments = rng.standard_normal((n_paths, grid))
    b = np.cumsum(increments, axis=1) / np.sqrt(grid)      # B at grid points
    b1 = b[:, -1]                                          # B(1)
    r = (np.arange(1, grid + 1) / float(grid))[None, :]    # t/grid
    bridge = b - r * b1[:, None]                           # Brownian bridge
    norm2 = np.mean(bridge * bridge, axis=1)               # integral (1/grid sum)
    return b1 / np.sqrt(norm2)


def part0():
    print("=" * 78)
    print("PART 0: PIVOTAL-LAW CALIBRATION FROM SCRATCH (signed T_infinity)")
    print("=" * 78)
    grid = 500
    n_paths = 200_000
    draws = brownian_pivot_draws(n_paths, grid, seed=20260819)
    q = {}
    for p in (0.90, 0.95, 0.975, 0.99):
        q[p] = float(np.quantile(draws, p))
        print(f"  signed T_infinity quantile p={p:>5}: {q[p]:.4f}")
    p_ge_5336 = float(np.mean(draws >= 5.336))
    p_abs_ge_5336 = float(np.mean(np.abs(draws) >= 5.336))
    print(f"  P(T >= 5.336)        = {p_ge_5336:.4f}  (should be ~0.025 if 5.336 is the 97.5th pct)")
    print(f"  P(|T| >= 5.336)      = {p_abs_ge_5336:.4f}  (should be ~0.05 if 5.336 is the two-sided 5% value)")
    print(f"  MC SE for 0.05        = {np.sqrt(0.05*0.95/n_paths):.4f}")
    return q


# ---------------------------------------------------------------------------
# Process generators: return daily score series Z_d (theta0=0 => Z_d = S_d)
# ---------------------------------------------------------------------------

def p_iid(rng, d, sigma=1.0):
    return rng.normal(0.0, sigma, d)


def p_ar1(rng, d, rho, mu=0.0):
    eps = rng.normal(0.0, 1.0, d)
    z = np.empty(d)
    z[0] = mu + eps[0] / np.sqrt(1.0 - rho * rho)
    for t in range(1, d):
        z[t] = mu + rho * (z[t - 1] - mu) + eps[t]
    return z


def p_t(rng, d, df):
    # Student-t with df degrees of freedom (finite variance iff df>2).
    n = rng.normal(0.0, 1.0, d)
    chi = rng.chisquare(df, d)
    return n / np.sqrt(chi / df)


def p_arch(rng, d, omega=0.2, alpha=0.5):
    z = np.empty(d)
    z[0] = rng.normal(0.0, 1.0)
    for t in range(1, d):
        sigma2 = omega + alpha * z[t - 1] ** 2
        z[t] = rng.normal(0.0, np.sqrt(sigma2))
    return z


def p_sparse(rng, d, lam=0.5, mu=0.0, sigma=1.0):
    """Poisson daily counts; per-trade returns N(mu,sigma^2); Z_d = sum r_i."""
    counts = rng.poisson(lam, d)
    z = np.empty(d)
    for t in range(d):
        if counts[t] == 0:
            z[t] = 0.0
        else:
            z[t] = rng.normal(mu, sigma, counts[t]).sum()
    return z


def p_bursty(rng, d, lam_high=3.0, lam_low=0.05, p_active=0.3, mu=0.0, sigma=1.0):
    """Two-state Markov activity chain -> clustered (bursty) counts."""
    state = rng.random() < p_active
    counts = np.empty(d, dtype=np.int64)
    z = np.empty(d)
    for t in range(d):
        # flip state with prob p_active (stay probability high) -> clusters
        if rng.random() < 0.15:
            state = not state
        lam = lam_high if state else lam_low
        c = rng.poisson(lam)
        counts[t] = c
        z[t] = rng.normal(mu, sigma, c).sum() if c > 0 else 0.0
    return z


def p_count_return_corr(rng, d, lam=1.0, a=0.7, b=0.5, sigma=1.0):
    """Event count positively correlated with the return shock (hidden weight).

    Latent L_d ~ N(0,1); count C_d ~ Poisson(lam*exp(a*L_d)); each return
    r_i = b*L_d + eps_i. Then E[r_i]=0 but E[Z_d]=b*Cov(C_d,L_d) != 0, so the
    daily-score test targets a count-weighted quantity, not the per-trade mean.
    """
    latent = rng.normal(0.0, 1.0, d)
    mean_c = lam * np.exp(a * latent)
    counts = rng.poisson(mean_c)
    z = np.empty(d)
    for t in range(d):
        c = counts[t]
        if c == 0:
            z[t] = 0.0
        else:
            eps = rng.normal(0.0, sigma, c)
            z[t] = (b * latent[t] + eps).sum()
    return z


def p_variance_regime(rng, d, break_frac=0.5, sigma_lo=1.0, sigma_hi=3.0):
    """Zero-mean but variance jumps mid-series (nonstationary variance)."""
    b = int(d * break_frac)
    z = np.empty(d)
    z[:b] = rng.normal(0.0, sigma_lo, b)
    z[b:] = rng.normal(0.0, sigma_hi, d - b)
    return z


def p_extreme_shocks(rng, d, n_shocks=1, shock_size=12.0, sigma=1.0):
    """Null with a small number of huge signed shocks (random sign)."""
    z = rng.normal(0.0, sigma, d)
    idx = rng.choice(d, size=n_shocks, replace=False)
    signs = rng.choice([-1.0, 1.0], size=n_shocks)
    z[idx] += signs * shock_size
    return z


def p_week_cluster(rng, d, weeks_per=5, sigma_f=1.0, sigma_e=1.0):
    """Week-level common factor: profitable/loss days cluster within ISO weeks."""
    n_weeks = int(np.ceil(d / weeks_per))
    factors = rng.normal(0.0, sigma_f, n_weeks)
    z = rng.normal(0.0, sigma_e, d)
    for w in range(n_weeks):
        s = w * weeks_per
        e = min(d, (w + 1) * weeks_per)
        z[s:e] += factors[w]
    return z


# ---------------------------------------------------------------------------
# Part 1: finite-sample size
# ---------------------------------------------------------------------------

def run_size(q_one_sided: float, q_candidate_smoke: float):
    print()
    print("=" * 78)
    print("PART 1: FINITE-SAMPLE SIZE, H0: theta=0, one-sided nominal 5%")
    print("=" * 78)
    print("Correct one-sided 5% signed-pivot critical value q~4.30;")
    print("candidate smoke used q95=5.336 (two-sided 5% / one-sided 2.5%).")
    print(f"{'process':<28}{'D':>5}{'R':>7}{'rej@q4_30':>12}{'se':>7}{'rej@5_336':>12}")
    alpha = 0.05
    specs = [
        ("A iid gauss", p_iid, {}),
        ("B ar1 rho=0.20", p_ar1, {"rho": 0.2}),
        ("B ar1 rho=0.50", p_ar1, {"rho": 0.5}),
        ("B ar1 rho=0.80", p_ar1, {"rho": 0.8}),
        ("B ar1 rho=0.95", p_ar1, {"rho": 0.95}),
        ("C t_df=5", p_t, {"df": 5}),
        ("C t_df=3", p_t, {"df": 3}),
        ("C t_df=2 infvar", p_t, {"df": 2}),
        ("D arch(0.5)", p_arch, {}),
        ("E sparse pois lam=0.5", p_sparse, {"lam": 0.5}),
        ("E sparse pois lam=0.2", p_sparse, {"lam": 0.2}),
        ("F bursty counts", p_bursty, {}),
        ("G count-return corr", p_count_return_corr, {}),
        ("H variance regime", p_variance_regime, {}),
        ("I 1 extreme shock 12", p_extreme_shocks, {}),
        ("J week-cluster", p_week_cluster, {}),
    ]
    for name, fn, kw in specs:
        for d in (117, 126, 242, 500):
            rng = np.random.default_rng(20260819)
            rej_correct = 0
            rej_smoke = 0
            r = 5000
            for rep in range(r):
                z = fn(rng, d, **kw)
                tsn = self_normalized_stat(z, 0.0)
                if np.isnan(tsn):
                    continue
                if tsn >= q_one_sided:
                    rej_correct += 1
                if tsn >= q_candidate_smoke:
                    rej_smoke += 1
            n_eff = r
            p_correct = rej_correct / n_eff
            p_smoke = rej_smoke / n_eff
            se = np.sqrt(p_correct * (1 - p_correct) / n_eff)
            print(f"{name:<28}{d:>5}{r:>7}{p_correct:>12.4f}{se:>7.4f}{p_smoke:>12.4f}")


# ---------------------------------------------------------------------------
# Part 2: power at standardized alternatives
# ---------------------------------------------------------------------------

def run_power(q_one_sided: float):
    print()
    print("=" * 78)
    print("PART 2: POWER AT STANDARDIZED MEAN SHIFTS (one-sided 5%)")
    print("=" * 78)
    print("mean shift in per-day-score sigma units for direct processes;")
    print("per-trade shift for sparse (total trades ~ lam*D).")
    print(f"{'process':<26}{'D':>5}{'mu':>6}{'R':>7}{'power':>9}")
    for d in (117, 126, 242):
        for mu in (0.1, 0.2, 0.3):
            rng = np.random.default_rng(20260819)
            r = 2000
            rej = 0
            for rep in range(r):
                z = p_ar1(rng, d, rho=0.0, mu=mu)  # IID with mean mu
                tsn = self_normalized_stat(z, 0.0)
                if not np.isnan(tsn) and tsn >= q_one_sided:
                    rej += 1
            print(f"{'IID mean shift':<26}{d:>5}{mu:>6}{r:>7}{rej / r:>9.4f}")
        for rho in (0.5, 0.9):
            for mu in (0.1, 0.2, 0.3):
                rng = np.random.default_rng(20260819)
                r = 2000
                rej = 0
                for rep in range(r):
                    z = p_ar1(rng, d, rho=rho, mu=mu)
                    tsn = self_normalized_stat(z, 0.0)
                    if not np.isnan(tsn) and tsn >= q_one_sided:
                        rej += 1
                print(f"{'AR1 rho=' + str(rho) + ' shift':<26}{d:>5}{mu:>6}{r:>7}{rej / r:>9.4f}")
        # Sparse: per-trade mean shift, lambda=0.5
        for mu in (0.1, 0.2, 0.3):
            rng = np.random.default_rng(20260819)
            r = 2000
            rej = 0
            for rep in range(r):
                z = p_sparse(rng, d, lam=0.5, mu=mu, sigma=1.0)
                tsn = self_normalized_stat(z, 0.0)
                if not np.isnan(tsn) and tsn >= q_one_sided:
                    rej += 1
            print(f"{'sparse pois lam=0.5 shift':<26}{d:>5}{mu:>6}{r:>7}{rej / r:>9.4f}")


# ---------------------------------------------------------------------------

def main() -> None:
    np.random.seed(20260819)
    print("REVIEW: stat_profile_sn_r03_falsification.py")
    print("NO_CANDIDATE_OUTCOME_DATA_USED=YES  (synthetic fixtures only)")
    q = part0()
    q_one_sided = q[0.95]      # correct one-sided 5% threshold (95th pct of signed pivot)
    q_smoke = 5.336            # candidate smoke-test threshold
    print(f"\nUsing q_one_sided(0.95) = {q_one_sided:.4f} ; candidate smoke q = {q_smoke}")
    run_size(q_one_sided, q_smoke)
    run_power(q_one_sided)


if __name__ == "__main__":
    main()
