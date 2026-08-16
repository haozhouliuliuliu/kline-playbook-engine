# Canonical Dataset — BALANCED Corpus Definition (Phase 4)

OWNER_DATASET_SCOPE_APPROVAL=BALANCED
COVERAGE=2024-01-01..2025-12-31
PRODUCT_COUNT=6
GRANULARITY=1-minute concrete-contract bars
SOURCE=TQSDK (ADOPTED, scoped)

Status: this document defines the approved BALANCED engineering/research-
foundation corpus. It does NOT mark the canonical dataset built or accepted,
and it does NOT expose any strategy lineage. The research/main-contract
selection rule and the chronological split belong to the later research-
protocol freeze and are NOT created here.

Machine-readable companion: `docs/evidence/CANONICAL_BALANCED_UNIVERSE.json`.

## 1. Coverage

`2024-01-01` through `2025-12-31` (two complete consecutive calendar years).

Rationale:
- complete calendar-year boundaries;
- existing verified SHFE official 2024/2025 annual raw supports per-day
  cross-checking (see `SHFE_OFFICIAL_RAW_RECHECK_MANIFEST.json`);
- official trading-day counts read from the official raw: 242 (2024), 243
  (2025).

No adjacent two-year interval was materially better on official metadata or
source coverage, so the preferred interval is used.

## 2. Six-product selection (evidence-based, no strategy criteria)

Selection used ONLY:
1. official metadata completeness;
2. continuous data availability;
3. differing session structures;
4. contract lifecycle coverage;
5. engineering diversity;
6. cross-source reference availability.

NOT used: prior steel strategy results, PnL, parameter performance, known
profitable/unprofitable periods, strategy relevance.

### Final universe: `cu`, `al`, `ni`, `au`, `ag`, `rb`

| Product | Tick | Multiplier | Contract months | Night session | Spec source (official) |
| --- | --- | --- | --- | --- | --- |
| cu (铜 Copper) | 10 元/吨 | 5 t/lot | 1–12月 | 21:00–01:00 | shfe.com.cn .../nonferrousmetal/cu_f/ (text 2023-03-29, [2023]2号) |
| al (铝 Aluminum) | 5 元/吨 | 5 t/lot | 1–12月 | 21:00–01:00 | shfe.com.cn .../nonferrousmetal/al_f/ (text 2024-07-12, [2024]105号) |
| ni (镍 Nickel) | 10 元/吨 | 1 t/lot | 1–12月 | 21:00–01:00 | shfe.com.cn .../nonferrousmetal/ni_f/ (text 2025-10-31, [2023]2号) |
| au (黄金 Gold) | 0.02 元/克 | 1000 g/lot | nearest 3 consecutive + even months ≤13m | 21:00–02:30 | shfe.com.cn .../ferrousandpreciousmetal/au_f/ (text 2020-08-31, [2020]134号) |
| ag (白银 Silver) | 1 元/千克 | 15 kg/lot | 1–12月 | 21:00–02:30 | shfe.com.cn .../ferrousandpreciousmetal/ag_f/ (text 2023-03-29, [2023]2号) |
| rb (螺纹钢 Rebar) | 1 元/吨 | 10 t/lot | 1–12月 | 21:00–23:00 | shfe.com.cn .../ferrousandpreciousmetal/rb_f/ (text 2024-09-24, [2024]116号) |

Selection evidence:

- **Continuous data availability:** all six appear in every month file of the
  verified SHFE official 2024 and 2025 annual raw, 12/12 months each year,
  with official trading-day counts 242 (2024) / 243 (2025) per product.
- **Differing session structures:** the set spans all three official night
  bands — 21:00–23:00 (rb), 21:00–01:00 (cu/al/ni), 21:00–02:30 (au/ag) —
  per the official SHFE trading-hours page. Day session is common
  (09:00–10:15, 10:30–11:30, 13:30–15:00).
- **Contract lifecycle coverage:** five products list all 12 contract months;
  gold lists nearest-3-consecutive + even months within 13 months (a
  materially different lifecycle). Nickel's price-limit structure (±4%) also
  differs from the ±3% common band.
- **Engineering diversity:** tick sizes 0.02 / 1 / 5 / 10; multipliers 1 t, 5 t,
  10 t, 15 kg, 1000 g; base metals, precious metals, ferrous.
- **Cross-source reference availability:** all six are present in the verified
  SHFE official 2024/2025 annual raw (concrete-contract daily OHLC/volume/OI),
  enabling per-day cross-source MATCH/MISMATCH checks.
- **Official metadata completeness:** each product has a current official SHFE
  contract-text page binding tick, multiplier, quote unit, contract months,
  last-trading-day rule, and margin, plus the official trading-hours page for
  session schedule.

All tick/multiplier/session facts for the selected products are stable across
the 2024–2025 window (last contract-text revisions predate or cover the
window; no mid-window spec change applies to these six).

## 3. Concrete-contract inventory rule

Rule: **PIT-complete listed concrete-contract universe, data-driven.**

- For each selected product and each official trading day in the window, every
  listed concrete contract that actually returned data is acquired.
- No post-hoc "most active / profitable contract" preselection.
- Pseudo MAIN/CONTINUOUS symbols are rejected (existing acquisition boundary).
- The research/main-contract selection rule and any per-product continuous
  series are a later research-protocol freeze decision, not made here.

This avoids future-information selection bias: the raw corpus is complete with
respect to what officially traded, per trading day, so a later research rule
can be applied without missing concrete-contract data.

## 4. Scale projection and guardrail result

Exact universe read from the verified SHFE official annual raw:

- Trading days: 242 (2024), 243 (2025).
- Listed concrete-contract × trading-day partitions: **32,980**.
- Partitions with actual daily volume > 0: **32,841**.

Real bounded scale probe (24 partitions, one TqSdk session, 2026-08-16):

- TqSdk returns the full session bar skeleton even for ultra-thin far-month
  contracts (e.g., 465 rows for 21:00–01:00 products, 555 for 21:00–02:30,
  345 for 21:00–23:00), with volume=0 on empty minutes.
- Raw partition size is ~75–96 KB regardless of contract activity.
- Measured average: **≈ 79.6 KB/partition**.

Refined projected scale for the full bias-free corpus:

- Raw storage: **≈ 2.615 GB** (32,841 partitions × ≈79.6 KB).
- Guardrail (Owner-approved): absolute cap ≈ 5 GB — NOT exceeded;
  ≈ 3× readiness BALANCED estimate (≈ 1.32 GB) — **EXCEEDED ≈ 1.98×**.

Per the Owner instruction: when avoiding preselection pushes raw storage above
≈ 3× the readiness estimate, STOP before the large acquisition and report the
exact projected scale to GPT/project lead. The large acquisition is therefore
**GATED** in this package. All definition/metadata/storage/engine work is
preserved on `ds/canonical-dataset-build` so the build can proceed immediately
once the project lead resolves the scale decision (accept the ≈2.6 GB corpus,
approve a bounded bias-controlled subset, or adjust scope). No paid continuity
is authorized.

`SCALE_GUARDRAIL=STOP_AND_REPORT_PROJECTED`
`SCALE_ACTION=REPORT_TO_PROJECT_LEAD_BEFORE_LARGE_ACQUISITION`
`PROJECTED_RAW_GB=2.615`

## 5. What this definition does and does not do

Does:
- freezes the approved BALANCED corpus definition (products, coverage,
  granularity, inventory rule) for the canonical build;

Does NOT:
- mark the canonical dataset built or accepted (`CANONICAL_DATASET_BUILT=NO`);
- create a development/validation/final-unseen split;
- expose the corpus to any strategy lineage;
- authorize broker/order/live/Shadow behavior or paid continuity.
