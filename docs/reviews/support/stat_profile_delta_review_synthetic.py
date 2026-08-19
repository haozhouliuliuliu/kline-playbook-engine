"""Synthetic finite-sample falsification for COMMON_STATISTICAL_PROFILE_V1 revision candidate 0.3.

Independent targeted delta review -- reproducibility script (docs/reviews/support/).
Author: independent statistical reviewer, 2026-08-19.
Dependencies: numpy only (documented). No production code, no runtime dependency, no
candidate outcome data, no canonical market data. Synthetic fixtures only.

What it tests (falsification, NOT tuning):
  A. The signed Brownian pivotal quantiles used by candidate-0.3 (one-sided p / Holm
     p-values) and the Monte-Carlo error of those quantiles.
  B. Null size of the scalar self-normalized test T_SN = sqrt(D)*Z_bar/sqrt(V_D) on daily
     score series of lengths 117 / 126 / 242 under:
       - IID Gaussian;
       - AR(1) rho in {0.3, 0.6, 0.85};
       - GARCH-like volatility clustering;
       - heavy-tailed (t_3) and skewed heavy-tailed innovations;
       - sparse Poisson event counts with zero-trade days (with and without the N>=20 floor);
       - clustered/bursty event counts;
       - event counts correlated with return shocks;
       - structural variance change (nonstationarity);
       - a small number of extreme daily events;
       - strongly clustered profitable weeks (alternative/power pathology).
  C. Power sanity for small positive means under IID Gaussian.

All random draws use a single deterministic seed (default_rng(20260819)).
"""
from __future__ import annotations

import numpy as np

SEED = 20260819
ALPHA = 0.05
LENGTHS = (117, 126, 242)
R = 5000  # replications per (case, length) for null size
CAL_M = 200_000  # Brownian paths for pivotal calibration
CAL_GRID = 1000  # grid steps for Brownian discretization


def self_norm_stat(z: np.ndarray) -> float:
    """Shao(2010) scalar self-normalized statistic for the mean of series z (len D)."""
    z = np.asarray(z, dtype=float)
    D = z.shape[0]
    zbar = z.mean()
    A = np.cumsum(z - zbar)
    V_D = float(np.sum(A * A) / (D * D))
    if not (np.isfinite(V_D) and V_D > 0):
        return float("inf")  # degenerate normalizer => candidate returns INSUFFICIENT_EVIDENCE
    return float(np.sqrt(D) * zbar / np.sqrt(V_D))


def pivotal_calibration(rng, M: int = CAL_M, m: int = CAL_GRID) -> np.ndarray:
    """Simulate the limiting signed pivotal T = B(1)/sqrt(int_0^1 (B(r)-rB(1))^2 dr)."""
    inc = rng.standard_normal((M, m)) / np.sqrt(m)
    B = np.cumsum(inc, axis=1)
    B1 = B[:, -1]
    r = np.arange(1, m + 1) / m
    bridge = B - np.outer(B1, r)
    V = np.mean(bridge * bridge, axis=1)
    T = B1 / np.sqrt(V)
    return T


def q_and_mc_error(rng, level: float) -> tuple[float, float]:
    """Quantile at `level` and its Monte-Carlo standard error via 5 independent runs."""
    qs = []
    for _ in range(5):
        T = pivotal_calibration(rng)
        qs.append(float(np.quantile(T, level)))
    qs = np.array(qs)
    return float(np.mean(qs)), float(np.std(qs, ddof=1))


# ---------------------------------------------------------------------------
# data generators (all return a daily score series of length n; null mean zero)
# ---------------------------------------------------------------------------

def gen_iid(rng, n):
    return rng.standard_normal(n)


def gen_ar1(rng, n, rho):
    e = rng.standard_normal(n)
    z = np.empty(n)
    z[0] = e[0]
    for d in range(1, n):
        z[d] = rho * z[d - 1] + e[d]
    return z


def gen_garch(rng, n, omega=0.05, alpha=0.10, beta=0.85):
    z = np.empty(n)
    sig2 = 1.0
    for d in range(n):
        sig2 = omega + alpha * (z[d - 1] ** 2 if d > 0 else 0.0) + beta * sig2
        z[d] = np.sqrt(sig2) * rng.standard_normal()
    return z


def gen_heavy(rng, n, df=3.0):
    return rng.standard_t(df, n)


def gen_skewed_heavy(rng, n):
    # 90% t_3, 10% large negative => left-skewed heavy tail; mean approx 0
    z = rng.standard_t(3.0, n)
    mask = rng.random(n) < 0.10
    z[mask] = -8.0 - np.abs(rng.standard_t(3.0, mask.sum()))
    return z


def gen_sparse_compound(rng, n, lam, rho, scale=1.0, enforce_n_ge_20=False):
    """Poisson daily counts; per-trade return = day shock + idio (null mean zero)."""
    while True:
        e = rng.standard_normal(n)
        day = np.empty(n)
        day[0] = e[0]
        for d in range(1, n):
            day[d] = rho * day[d - 1] + e[d]
        C = rng.poisson(lam, n).astype(float)
        if enforce_n_ge_20 and C.sum() < 20:
            continue
        # S_d = C_d * day_d + sqrt(C_d)*idio_d  (exact in distribution)
        S = C * day + np.sqrt(np.maximum(C, 0.0)) * scale * rng.standard_normal(n)
        return S


def gen_bursty(rng, n, p=0.05, burst_mean=10.0):
    # zero most days, Poisson bursts on 5% of days
    C = np.where(rng.random(n) < p, rng.poisson(burst_mean, n), 0.0)
    S = C * rng.standard_normal(n)
    return S


def gen_count_return_correlated(rng, n, lam0=0.5, k=2.0):
    # daily shock eps; count increases with |eps| (count-return dependence), null E[S]=0
    while True:
        eps = rng.standard_normal(n)
        C = rng.poisson(lam0 + k * np.abs(eps)).astype(float)
        if C.sum() >= 20:
            break
    S = C * eps
    return S


def gen_structural_variance(rng, n, ratio=3.0):
    half = n // 2
    z = np.empty(n)
    z[:half] = rng.standard_normal(half)
    z[half:] = ratio * rng.standard_normal(n - half)
    return z


def gen_skew_two_point(rng, n, win_val, win_prob, loss_val):
    """Two-point skew: rare large opposite-tail value + common small value.
    win_val/loss_val chosen so mean is (approx) set by caller."""
    z = np.full(n, loss_val, dtype=float)
    mask = rng.random(n) < win_prob
    z[mask] = win_val
    return z


def gen_extreme_events(rng, n, p=0.03, sigma=30.0):
    # rare large daily events; null mean zero
    z = np.zeros(n)
    mask = rng.random(n) < p
    z[mask] = sigma * rng.standard_normal(mask.sum())
    return z


def gen_clustered_profitable_weeks(rng, n, pos_weeks=(5, 12, 19), lam=2.0, mu=1.0):
    """Alternative: positive per-trade mean concentrated in a few 5-day weeks; rest no trades."""
    z = np.zeros(n)
    week_of_day = np.arange(n) // 5
    for w in pos_weeks:
        days = np.where(week_of_day == w)[0]
        for d in days:
            c = rng.poisson(lam)
            z[d] = c * (mu + rng.standard_normal())
    return z


# ---------------------------------------------------------------------------
# size / power machinery
# ---------------------------------------------------------------------------

def rejection_fraction(gen, rng, n, q95, R):
    rej = 0
    deg = 0
    for _ in range(R):
        z = gen(rng, n)
        T = self_norm_stat(z)
        if not np.isfinite(T):
            deg += 1
            continue
        if T > q95:
            rej += 1
    return rej / R, deg / R


def tail_rejection(gen, rng, n, q99, R=5000):
    """Holm-relevant tail: fraction of T > q99 (one-sided 1% level)."""
    rej = 0
    for _ in range(R):
        z = gen(rng, n)
        T = self_norm_stat(z)
        if np.isfinite(T) and T > q99:
            rej += 1
    return rej / R


def run_case(name, gen, rng, q95, lengths=LENGTHS, R=R):
    row = []
    for n in lengths:
        rej, deg = rejection_fraction(gen, rng, n, q95, R)
        row.append((n, rej, deg))
    print(f"{name}: " + "; ".join(f"n={n} rej={rej:.4f} deg={deg:.4f}" for n, rej, deg in row))


def main():
    rng = np.random.default_rng(SEED)
    print("=== A. Signed pivotal calibration (deterministic seed) ===")
    for level, name in ((0.95, "q95(one-sided 5%)"), (0.975, "q97.5"), (0.99, "q99"), (0.9975, "q99.75")):
        q, err = q_and_mc_error(rng, level)
        print(f"{name}: mean={q:.4f}  mc_sd={err:.4f}")

    # single high-fidelity calibration used for all size tests
    T = pivotal_calibration(rng)
    q95 = float(np.quantile(T, 0.95))
    print(f"Using q95 = {q95:.4f} for size tests (M={CAL_M}, grid={CAL_GRID})")

    print()
    print("=== B. Null size (target 0.0500) ===")
    run_case("IID Gaussian", gen_iid, rng, q95)
    for rho in (0.30, 0.60, 0.85):
        run_case(f"AR(1) rho={rho}", (lambda rng, n, r=rho: gen_ar1(rng, n, r)), rng, q95)
    run_case("GARCH-like (a=0.10,b=0.85)", gen_garch, rng, q95)
    run_case("Heavy tail t_3", gen_heavy, rng, q95)
    run_case("Skewed heavy (10% -8)", gen_skewed_heavy, rng, q95)
    for lam in (0.2, 0.5, 1.0):
        run_case(f"Sparse Poisson lam={lam} unfiltered", (lambda rng, n, l=lam: gen_sparse_compound(rng, n, l, 0.0, enforce_n_ge_20=False)), rng, q95)
        run_case(f"Sparse Poisson lam={lam} N>=20 filtered", (lambda rng, n, l=lam: gen_sparse_compound(rng, n, l, 0.0, enforce_n_ge_20=True)), rng, q95)
    run_case("Bursty counts (5% Poisson10)", gen_bursty, rng, q95)
    run_case("Count-return correlated", gen_count_return_correlated, rng, q95)
    run_case("Structural variance change 3x (hi in 2nd half)", gen_structural_variance, rng, q95)
    run_case(
        "Structural variance change 1/3x (hi in 1st half)",
        (lambda rng, n: gen_structural_variance(rng, n, ratio=1.0 / 3.0)),
        rng,
        q95,
    )
    run_case("Extreme rare events (p=0.03, s=30)", gen_extreme_events, rng, q95)

    # clean two-point skew cases: rare large opposite-tail value
    # left-skew mean zero: 5% at -19, 95% at +1  (E=0)
    run_case("Left-skew mean-zero (5% -19 / 95% +1)", (lambda rng, n: gen_skew_two_point(rng, n, 1.0, 0.95, -19.0)), rng, q95)
    # left-skew positive mean: 5% at -19, 95% at +2  (E=0.95)
    run_case("Left-skew POSITIVE mean (5% -19 / 95% +2)", (lambda rng, n: gen_skew_two_point(rng, n, 2.0, 0.95, -19.0)), rng, q95)
    # right-skew mean zero: 5% at +19, 95% at -1  (E=0)
    run_case("Right-skew mean-zero (5% +19 / 95% -1)", (lambda rng, n: gen_skew_two_point(rng, n, 19.0, 0.05, -1.0)), rng, q95)
    # right-skew positive mean: 5% at +19, 95% at -0.5 (E=0.475)
    run_case("Right-skew POSITIVE mean (5% +19 / 95% -0.5)", (lambda rng, n: gen_skew_two_point(rng, n, 19.0, 0.05, -0.5)), rng, q95)
    # mild left-skew mean-zero: 10% at -3, 90% at +1/3 (E=0)
    run_case("Left-skew MILD mean-zero (10% -3 / 90% +0.333)", (lambda rng, n: gen_skew_two_point(rng, n, 1.0 / 3.0, 0.90, -3.0)), rng, q95)

    print()
    print("=== B2. Holm-relevant tail size at one-sided 1% (q99) ===")
    q99 = float(np.quantile(T, 0.99))
    for name, gen in (
        ("IID Gaussian", gen_iid),
        ("AR(1) rho=0.85", (lambda rng, n: gen_ar1(rng, n, 0.85))),
        ("Left-skew mean-zero (5% -19 / 95% +1)", (lambda rng, n: gen_skew_two_point(rng, n, 1.0, 0.95, -19.0))),
        ("Structural variance change 3x", gen_structural_variance),
    ):
        row = " ".join(f"n={n} tail_rej={tail_rejection(gen, rng, n, q99):.4f}" for n in LENGTHS)
        print(f"{name}: {row}")

    print()
    print("=== C. Power sanity (IID Gaussian, positive mean), one-sided 5% ===")
    for mu, name in ((0.2, "mu=0.2"), (0.5, "mu=0.5"), (1.0, "mu=1.0")):
        gen = (lambda rng, n, m=mu: gen_iid(rng, n) + m)
        run_case(f"IID+const {name}", gen, rng, q95)

    print()
    print("=== D. Alternative pathology: clustered profitable weeks (power) ===")
    run_case("Profitable weeks 5/12/19 (lam=2,mu=1)", gen_clustered_profitable_weeks, rng, q95, lengths=(126,))

    print()
    print("done")


if __name__ == "__main__":
    main()
