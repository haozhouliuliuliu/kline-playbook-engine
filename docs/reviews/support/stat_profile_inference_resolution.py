#!/usr/bin/env python
"""
STAT_PROFILE_INFERENCE_RESOLUTION — synthetic-only falsification
================================================================
Lane: COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_REVIEWER
Project: haozhouliuliuliu/kline-playbook-engine
Branch: parallel/stat-profile-inference-resolution-r04

PURPOSE
-------
Pre-outcome, candidate-outcome-free, synthetic-only evaluation of candidate
inference procedures for the Common Statistical Profile v1 daily-score test:

    C_d = number of eligible completed round trips exiting on trading day d
    S_d = sum of their normalized per-round-trip returns
    theta = E[S_d] / E[C_d]   (event-weighted per-trade mean)
    Z_d(theta0) = S_d - theta0 * C_d
    H0: theta <= 0  -> boundary test Z_d(0) = S_d
    T_SN = sqrt(D) * Zbar / sqrt(V_D),  V_D = D^-2 * sum_t A_t^2,
           A_t = sum_{j<=t}(Z_j - Zbar)

Methods compared:
  sn_asy     : candidate 0.3 asymptotic signed-pivotal calibration
               (T_inf = B(1)/sqrt(int_0^1 (B(r)-rB(1))^2 dr), symmetric)
  sn_wild_r  : fixed-b wild bootstrap (Rademacher +/-1 multipliers) of T_SN,
               null-imposed (restricted) resampling
  sn_wild_g  : fixed-b wild bootstrap (Gaussian N(0,1) multipliers)
  block_bt   : circular block bootstrap of the null-imposed mean (L days)
  week_t     : weekly aggregation + t-test on ~27 weekly scores (df=G-1)
  week_wc    : weekly aggregation + wild cluster bootstrap (Rademacher, clusters=weeks)

ALL WORK IS SYNTHETIC. NO candidate outcome, PnL, equity, Sharpe, win/loss,
VALIDATION or historical-final data is used. No threshold is tuned on any
result. Deterministic seeds only.

DEPENDENCY: numpy only.
"""

import json
import os
from datetime import date

import numpy as np

MASTER_SEED = 20260819


# ---------------------------------------------------------------------------
# Calendar metadata (non-outcome). Week grouping for the weekly methods uses the
# real authoritative trading calendar so weeks match the frozen cohorts.
# ---------------------------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_CAL_PATH = os.path.normpath(
    os.path.join(_HERE, "..", "..", "evidence", "CANONICAL_TRADING_CALENDAR.json")
)


def _cohort_days(start: str, end: str):
    with open(_CAL_PATH, "r", encoding="utf-8") as fh:
        cal = json.load(fh)
    days = set()
    for year, lst in cal["trading_days"].items():
        for s in lst:
            days.add(date.fromisoformat(s))
    a = date.fromisoformat(start)
    b = date.fromisoformat(end)
    return sorted(dd for dd in days if a <= dd <= b)


_COHORTS = {
    "DEV": _cohort_days("2024-01-01", "2024-12-31"),
    "VAL": _cohort_days("2025-01-01", "2025-06-30"),
    "FIN": _cohort_days("2025-07-01", "2025-12-31"),
}
_WEEK_IDX = {}  # cohort -> array of ISO-week index per trading day (0-based)
for _name, _ds in _COHORTS.items():
    _weeks = {}
    for _dd in _ds:
        _iso = (_dd.isocalendar()[0], _dd.isocalendar()[1])
        if _iso not in _weeks:
            _weeks[_iso] = len(_weeks)
    _WEEK_IDX[_name] = np.array([_weeks[(dd.isocalendar()[0], dd.isocalendar()[1])] for dd in _ds])


# ---------------------------------------------------------------------------
# Pivot calibration for sn_asy (Brownian-motion functional)
#   T_inf = B(1) / sqrt( int_0^1 [B(r) - r B(1)]^2 dr )
# ---------------------------------------------------------------------------
def calibrate_signed_pivot(n_paths=200_000, grid=1000, seed=MASTER_SEED):
    rng = np.random.default_rng(seed)
    dW = rng.standard_normal((n_paths, grid)) / np.sqrt(grid)
    B = np.cumsum(dW, axis=1)  # Brownian motion on the grid
    tgrid = np.arange(1, grid + 1) / grid
    denom = np.mean((B - B[:, -1:] * tgrid[None, :]) ** 2, axis=1)
    T = B[:, -1] / np.sqrt(denom)
    T = np.sort(T)
    return T


# Module-level locked calibration sample (computed once; used by sn_asy).
# 200k paths x 1000-step grid, deterministic seed -> reproducible pivot CDF.
PIVOT_SORTED = calibrate_signed_pivot(n_paths=200_000, grid=1000, seed=MASTER_SEED)


def signed_p_asy(Tobs, T_sorted):
    """one-sided p = P(T_inf >= Tobs) from the sorted calibration sample."""
    n = T_sorted.size
    idx = np.searchsorted(T_sorted, Tobs, side="right")
    return (n - idx) / n


def signed_q(T_sorted, alpha):
    n = T_sorted.size
    idx = int(np.ceil((1 - alpha) * n)) - 1
    idx = max(0, min(n - 1, idx))
    return T_sorted[idx]


# ---------------------------------------------------------------------------
# Self-normalized statistic (vectorized over leading axes)
# ---------------------------------------------------------------------------
def sn_stat(z):
    """T_SN = sqrt(D) * zbar / sqrt(V_D),  V_D = D^-2 * sum_t A_t^2.
    Equivalently T_SN = D * zbar / sqrt(mean_t A_t^2), since mean(A^2)=D*V_D.
    z: (..., D). Returns (...,)."""
    D = z.shape[-1]
    zbar = z.mean(axis=-1)
    A = np.cumsum(z - zbar[..., None], axis=-1)
    V = np.mean(A * A, axis=-1)  # = D^-1 sum A_t^2 = D * V_D
    V = np.maximum(V, 1e-300)
    return D * zbar / np.sqrt(V)


def _rademacher(rng, shape):
    return (rng.random(shape) < 0.5).astype(np.float64) * 2.0 - 1.0


def sn_wild_p(z, B, rng, gaussian=False):
    """Wild-bootstrap (restricted/null-imposed) p-value for T_SN.
    Z*_d = w_d * Z_d ;  p = (1 + #{T* >= T}) / (B+1)."""
    D = z.shape[-1]
    T = sn_stat(z[None, :])[0]
    if gaussian:
        W = rng.standard_normal((B, D))
    else:
        W = _rademacher(rng, (B, D))
    ZW = W * z[None, :]
    Tstar = sn_stat(ZW)
    p = (1.0 + np.count_nonzero(Tstar >= T)) / (B + 1.0)
    return p, T


def block_bt_p(z, L, B, rng):
    """Circular block bootstrap of the null-imposed mean (restricted).
    Recentre the data at the null mean 0 (u = z - zbar), resample length-L
    circular blocks of u, recompute the mean; p = (1 + #{mean* >= zbar})/(B+1).
    Block length is a knob; block captures dependence only up to length L."""
    D = z.shape[-1]
    zbar = z.mean()
    u = z - zbar  # null-centred scores (mean exactly 0)
    m = int(np.ceil(D / L))
    s = rng.integers(0, D, size=(B, m))                       # (B, m) starts
    pos = (s[:, :, None] + np.arange(L)[None, None, :]) % D   # (B, m, L)
    idx = pos.reshape(B, m * L)[:, :D]
    blocks = u[idx]                                           # (B, D)
    means = blocks.mean(axis=1)
    p = (1.0 + np.count_nonzero(means >= zbar)) / (B + 1.0)
    return p


def week_scores(z, cohort):
    """Aggregate daily scores to ISO-week sums using the real calendar."""
    wi = _WEEK_IDX[cohort]
    G = wi.max() + 1
    zw = np.zeros(G, dtype=np.float64)
    np.add.at(zw, wi, z)
    return zw, G


def _betacf(a, b, x, itmax=200, eps=3e-12):
    """Lentz continued fraction for the incomplete beta (Numerical Recipes)."""
    import math
    qab = a + b
    qap = a + 1.0
    qam = a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < 1e-30:
        d = 1e-30
    d = 1.0 / d
    h = d
    for _m in range(1, itmax + 1):
        m2 = 2 * _m
        aa = _m * (b - _m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        h *= d * c
        aa = -(a + _m) * (qab + _m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < 1e-30:
            d = 1e-30
        c = 1.0 + aa / c
        if abs(c) < 1e-30:
            c = 1e-30
        d = 1.0 / d
        dele = d * c
        h *= dele
        if abs(dele - 1.0) < eps:
            break
    return h


def _betai(a, b, x):
    """Regularized incomplete beta I_x(a,b), numpy-only."""
    import math
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(1.0 - x)
    )
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def _t_cdf_one_sided(t, df):
    """one-sided upper-tail p of Student-t, via I_x(df/2, 1/2), numpy-only."""
    x = df / (df + t * t)
    return 0.5 * _betai(df / 2.0, 0.5, x)


def week_t_p(z, cohort):
    zw, G = week_scores(z, cohort)
    zbar = zw.mean()
    if G <= 2:
        return 0.5
    s = zw.std(ddof=1)
    if s <= 0:
        return 0.5
    t = zbar / (s / np.sqrt(G))
    return _t_cdf_one_sided(t, G - 1)


def week_wild_p(z, cohort, B, rng):
    """Wild cluster bootstrap at the weekly level (clusters = ISO weeks),
    null-imposed (restricted): Z*_w = w_w * Z_w, Rademacher at the week level."""
    zw, G = week_scores(z, cohort)
    zbar = zw.mean()
    if G <= 2 or zw.std(ddof=1) <= 0:
        return 0.5
    se = zw.std(ddof=1) / np.sqrt(G)
    T = zbar / se
    W = (rng.random((B, G)) < 0.5).astype(np.float64) * 2.0 - 1.0
    ZW = W * zw[None, :]  # (B, G)
    means = ZW.mean(axis=1)
    sds = np.sqrt(((ZW - means[:, None]) ** 2).sum(axis=1) / (G - 1))
    ses = sds / np.sqrt(G)
    Tstar = np.zeros(B)
    ok = ses > 0
    Tstar[ok] = means[ok] / ses[ok]
    p = (1.0 + np.count_nonzero(Tstar >= T)) / (B + 1.0)
    return p


# ---------------------------------------------------------------------------
# Null process generators. All have E[S_d] = 0 (the adjudicated null for the
# event-weighted estimand theta = E[S]/E[C]).
# ---------------------------------------------------------------------------
def gen_null(name, D, rng):
    if name == "iid_gauss":
        return rng.standard_normal(D)
    if name.startswith("ar1"):
        rho = float(name.split("_")[1])
        eps = rng.standard_normal(D)
        z = np.empty(D)
        z[0] = eps[0]
        for t in range(1, D):
            z[t] = rho * z[t - 1] + eps[t]
        return z * np.sqrt(1 - rho * rho)  # unit marginal variance
    if name == "left_skew_sev":  # 5% at -19, 95% at +1 ; E=0
        u = rng.random(D)
        return np.where(u < 0.05, -19.0, 1.0)
    if name == "left_skew_mild":  # 10% at -1, 90% at +1/9 ; E=0
        u = rng.random(D)
        return np.where(u < 0.10, -1.0, 1.0 / 9.0)
    if name == "right_skew":  # 5% at +19, 95% at -1 ; E=0
        u = rng.random(D)
        return np.where(u < 0.05, 19.0, -1.0)
    if name == "t3":
        return rng.standard_t(3, size=D)
    if name == "t2":
        return rng.standard_t(2, size=D)
    if name == "garch":  # GARCH(1,1)-ish heteroskedastic, mean 0
        sigma = np.empty(D)
        z = np.empty(D)
        s0 = 1.0
        for t in range(D):
            s0 = np.sqrt(0.05 + 0.85 * s0 * s0 + 0.10 * (z[t - 1] ** 2 if t > 0 else 1.0))
            sigma[t] = s0
            z[t] = rng.standard_normal() * s0
        return z
    if name == "sparse_pois":  # compound Poisson daily score, C ~ Pois(0.5)
        C = rng.poisson(0.5, size=D)
        z = np.zeros(D)
        for t in range(D):
            if C[t] > 0:
                z[t] = rng.standard_normal(C[t]).sum()
        return z
    if name == "bursty":  # 2-state Markov count (bursty events)
        z = np.zeros(D)
        state = 0
        for t in range(D):
            if rng.random() < 0.05:
                state = 1 - state
            if state == 1:
                z[t] = rng.standard_normal()
            # state 0: zero-trade day
        return z
    if name == "week_cluster":  # within-week common factor
        wi = np.zeros(D, dtype=int)
        # group into weeks of ~5
        for t in range(D):
            wi[t] = t // 5
        fac = rng.standard_normal(wi.max() + 1)
        return fac[wi] + rng.standard_normal(D) * 0.5
    if name == "var_change":  # structural variance change 3x in second half
        half = D // 2
        z = np.empty(D)
        z[:half] = rng.standard_normal(half)
        z[half:] = rng.standard_normal(D - half) * 3.0
        return z
    if name == "rare_loss":  # rare extreme losses (1% of days, -20; E=0)
        u = rng.random(D)
        return np.where(u < 0.01, -20.0, 20.0 * 0.01 / 0.99)  # E = 0.01*(-20)+0.99*x = 0
    if name == "persist_leftskew":  # AR(1) rho=0.8 on left-skewed innovations
        rho = 0.8
        eps = gen_null("left_skew_sev", D, rng) / np.sqrt(1 - rho * rho)
        z = np.empty(D)
        z[0] = eps[0]
        for t in range(1, D):
            z[t] = rho * z[t - 1] + eps[t]
        return z
    if name == "persist_sparse":  # AR(1) on sparse compound scores
        base = gen_null("sparse_pois", D, rng)
        rho = 0.8
        z = np.empty(D)
        z[0] = base[0]
        for t in range(1, D):
            z[t] = rho * z[t - 1] + base[t]
        return z
    raise ValueError(f"unknown null {name}")


NULLS = [
    "iid_gauss", "ar1_0.30", "ar1_0.60", "ar1_0.80", "ar1_0.95",
    "left_skew_sev", "left_skew_mild", "right_skew", "t3", "t2",
    "garch", "sparse_pois", "bursty", "week_cluster", "var_change",
    "rare_loss", "persist_leftskew", "persist_sparse",
]

ALPHAS = [0.05, 0.025, 0.01, 0.005, 0.0025]


def empirical_rejection(pvals, alpha):
    return float(np.mean(np.asarray(pvals) <= alpha))


# ---------------------------------------------------------------------------
# Main size experiment
# ---------------------------------------------------------------------------
def run_size(methods, nulls, Dlist, R, B, seed=MASTER_SEED):
    """Returns results[method][null][D] = dict(alpha->rejection)."""
    rng = np.random.default_rng(seed)
    results = {m: {} for m in methods}
    for null in nulls:
        for D in Dlist:
            cols = {}
            for m in methods:
                cols[m] = {a: [] for a in ALPHAS}
            for r in range(R):
                z = gen_null(null, D, rng)
                for m in methods:
                    if m == "sn_asy":
                        p, _ = sn_asy_p(z, PIVOT_SORTED)
                    elif m == "sn_wild_r":
                        p, _ = sn_wild_p(z, B, rng, gaussian=False)
                    elif m == "sn_wild_g":
                        p, _ = sn_wild_p(z, B, rng, gaussian=True)
                    elif m == "block_bt_5":
                        p = block_bt_p(z, 5, B, rng)
                    elif m == "block_bt_10":
                        p = block_bt_p(z, 10, B, rng)
                    elif m == "block_bt_15":
                        p = block_bt_p(z, 15, B, rng)
                    else:
                        raise ValueError(m)
                    for a in ALPHAS:
                        cols[m][a].append(p)
            for m in methods:
                results[m].setdefault(null, {})[D] = {
                    a: empirical_rejection(cols[m][a], a) for a in ALPHAS
                }
    return results


def sn_asy_p(z, pivot_sorted):
    T = sn_stat(z[None, :])[0]
    return signed_p_asy(T, pivot_sorted), T


# ---------------------------------------------------------------------------
# Power (synthetic standardized alternatives) for the leading methods
# ---------------------------------------------------------------------------
def run_power(methods, Dlist, effect_levels, R, B, seed=MASTER_SEED + 1):
    """Effect added to an IID-Gaussian daily score: mean = eff * sigma_expected.
    effect_levels in standardized units (multiplier of per-day sigma=1)."""
    rng = np.random.default_rng(seed)
    out = {}
    for D in Dlist:
        for eff in effect_levels:
            rej = {m: [] for m in methods}
            for r in range(R):
                z = rng.standard_normal(D) + eff
                for m in methods:
                    if m == "sn_asy":
                        p, _ = sn_asy_p(z, PIVOT_SORTED)
                    elif m == "sn_wild_r":
                        p, _ = sn_wild_p(z, B, rng, gaussian=False)
                    elif m == "sn_wild_g":
                        p, _ = sn_wild_p(z, B, rng, gaussian=True)
                    rej[m].append(p)
            for m in methods:
                out[(D, eff, m)] = empirical_rejection(rej[m], 0.05)
    return out


# ---------------------------------------------------------------------------
# Weekly methods (reference)
# ---------------------------------------------------------------------------
def run_week(methods, nulls, cohorts, R, B, seed=MASTER_SEED + 2):
    rng = np.random.default_rng(seed)
    results = {m: {} for m in methods}
    for null in nulls:
        for cohort in cohorts:
            D = len(_COHORTS[cohort])
            cols = {m: {a: [] for a in ALPHAS} for m in methods}
            for r in range(R):
                z = gen_null(null, D, rng)
                for m in methods:
                    if m == "week_t":
                        p = week_t_p(z, cohort)
                    elif m == "week_wild":
                        p = week_wild_p(z, cohort, B, rng)
                    else:
                        raise ValueError(m)
                    for a in ALPHAS:
                        cols[m][a].append(p)
            for m in methods:
                results[m].setdefault(null, {})[cohort] = {
                    a: empirical_rejection(cols[m][a], a) for a in ALPHAS
                }
    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def fmt_cell(res):
    return " ".join(f"{a}:{res[a]:.3f}" for a in ALPHAS)


if __name__ == "__main__":
    import time

    t0 = time.time()
    q = {a: signed_q(PIVOT_SORTED, a) for a in ALPHAS}
    print("pivot quantiles:", {a: round(float(q[a]), 3) for a in ALPHAS})

    # ---- (1) MAIN SIZE table: sn_asy vs sn_wild_r vs sn_wild_g ----
    # R lowered to keep the whole run tractable; tail-level rows are repeated
    # at higher R in (2).
    R_MAIN = 1200
    B = 999
    methods_main = ["sn_asy", "sn_wild_r", "sn_wild_g"]
    main_nulls = [
        "iid_gauss", "ar1_0.30", "ar1_0.60", "ar1_0.80", "ar1_0.95",
        "left_skew_sev", "left_skew_mild", "right_skew", "t3", "t2",
        "garch", "sparse_pois", "bursty", "week_cluster", "var_change",
        "rare_loss", "persist_leftskew", "persist_sparse",
    ]
    print(f"\n[1] MAIN SIZE R={R_MAIN} B={B}")
    res_main = run_size(methods_main, main_nulls, [117, 126], R_MAIN, B, seed=MASTER_SEED)
    for m in methods_main:
        print(f"\n== {m} ==")
        for null in main_nulls:
            for D in [117, 126]:
                print(f"  {null:16s} D{D} " + fmt_cell(res_main[m][null][D]))

    # D=242 convergence subset
    conv_nulls = ["iid_gauss", "ar1_0.80", "ar1_0.95", "left_skew_sev", "left_skew_mild"]
    print(f"\n[1b] D=242 CONVERGENCE R={R_MAIN} B={B}")
    res242 = run_size(methods_main, conv_nulls, [242], R_MAIN, B, seed=MASTER_SEED + 6)
    for m in methods_main:
        print(f"\n== {m} (D=242) ==")
        for null in conv_nulls:
            print(f"  {null:16s} D242 " + fmt_cell(res242[m][null][242]))

    # ---- (2) TAIL FOCUS: danger processes at higher R ----
    R_TAIL = 5000
    tail_nulls = ["ar1_0.80", "ar1_0.95", "left_skew_sev", "left_skew_mild", "persist_leftskew"]
    print(f"\n[2] TAIL FOCUS R={R_TAIL} B={B}")
    res_tail = run_size(methods_main, tail_nulls, [117, 126], R_TAIL, B, seed=MASTER_SEED + 7)
    for m in methods_main:
        print(f"\n== {m} (tail) ==")
        for null in tail_nulls:
            for D in [117, 126]:
                print(f"  {null:16s} D{D} " + fmt_cell(res_tail[m][null][D]))

    # ---- (3) BLOCK BOOTSTRAP reference ----
    R_BLK = 1200
    blk_nulls = ["iid_gauss", "ar1_0.80", "ar1_0.95", "left_skew_sev", "sparse_pois"]
    print(f"\n[3] BLOCK BOOTSTRAP REFERENCE R={R_BLK} B={B}")
    res_blk = run_size(["block_bt_5", "block_bt_10", "block_bt_15"],
                       blk_nulls, [117, 126], R_BLK, B, seed=MASTER_SEED + 3)
    for m in ["block_bt_5", "block_bt_10", "block_bt_15"]:
        print(f"\n== {m} ==")
        for null in blk_nulls:
            for D in [117, 126]:
                print(f"  {null:16s} D{D} " + fmt_cell(res_blk[m][null][D]))

    # ---- (4) WEEKLY methods reference ----
    R_WK = 2000
    wk_nulls = ["iid_gauss", "ar1_0.60", "ar1_0.80", "ar1_0.95",
                "left_skew_sev", "left_skew_mild", "sparse_pois", "week_cluster"]
    print(f"\n[4] WEEKLY METHODS REFERENCE R={R_WK} B={B}")
    res_wk = run_week(["week_t", "week_wild"], wk_nulls, ["VAL", "FIN"], R_WK, B, seed=MASTER_SEED + 4)
    for m in ["week_t", "week_wild"]:
        print(f"\n== {m} ==")
        for null in wk_nulls:
            for cohort in ["VAL", "FIN"]:
                print(f"  {null:16s} {cohort} " + fmt_cell(res_wk[m][null][cohort]))

    # ---- (5) POWER ----
    R_POW = 1200
    print(f"\n[5] POWER (IID alternatives, one-sided 5%) R={R_POW} B={B}")
    pow_out = run_power(["sn_asy", "sn_wild_r", "sn_wild_g"], [117, 126], [0.1, 0.2, 0.3],
                        R_POW, B, seed=MASTER_SEED + 5)
    for D in [117, 126]:
        for eff in [0.1, 0.2, 0.3]:
            row = " ".join(f"{m}={pow_out[(D, eff, m)]:.3f}" for m in ["sn_asy", "sn_wild_r", "sn_wild_g"])
            print(f"  D={D} eff={eff}: {row}")

    print(f"\nELAPSED {time.time() - t0:.1f}s")
