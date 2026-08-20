# HISTORICAL_PRICE_LIMIT_METADATA_AUTHORITY_PREP_V0_1

> Task: `HISTORICAL_PRICE_LIMIT_METADATA_AUTHORITY_PREP_V0_1`
> Goal: reduce `LIMIT-001=HISTORICAL_PRICE_LIMIT_METADATA` for `cu, al, ni, au, ag, rb`,
> `2024-01-01..2025-12-31`, SHFE.
> Date: 2026-08-21
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Branch: `preoutcome/historical-price-limit-prep-v01`
> Baseline: `origin/main` @ `e87315dd622689eb165dbe81f1728c868cc06a26`
> Companion artifact: `docs/evidence/HISTORICAL_PRICE_LIMIT_AUTHORITY_V0_1.json`
> Authority identity: `a283d4e611915b131d39b1cea135da7107689faa232e7a0226065f9e7dae7245`

```text
PRODUCTION_SRC_CHANGED=YES (new src/price_limit_authority.py; no existing module altered)
TESTS_CHANGED=YES (new tests/test_price_limit_authority.py)
CANDIDATE_BACKTEST_RUN=NO
CURRENT_RULE_BACKFILL_USED=NO
PAID_SOURCE_USED=NO
LOGIN_SOURCE_USED=NO
CAPTCHA_BYPASS_USED=NO
WAF_CHALLENGE_NOT_CIRCUMVENTED=YES
CURRENT_STATE_MODIFIED=NO
KNOWN_LIMITATIONS_MODIFIED=NO
```

This package prepares the governed authority for historical SHFE price-limit (涨跌停板)
metadata. It binds the **contract-text base daily price-limit rule** for the six products
with effective period, binding notice, source artifact, retrieval timestamp and exact
evidence classification; it records the **per-day exchange-adjustment layer** and
**special-day rule layer** as explicit `GAP` / `UNKNOWN` / `RETRIEVAL_BLOCKED`; and it
implements a **machine-readable authority schema with a fail-closed lookup interface** so
that execution simulation cannot claim a *real* price-limit fill for a 2024-2025 day while
the required operative fact is unbound.

---

## 1. Source policy applied

`FREE_PUBLIC_UNAUTHENTICATED_FIRST`. Only official SHFE sources or repository-verified
official references are used as facts. No paid, login, subscription, or captcha-bypass path
was used. **Current-rule backfill is forbidden and was not used.**

## 2. Retrieval environment (recorded honestly)

- On 2026-08-21 the live SHFE site (`www.shfe.com.cn`) served a **Safeline WAF
  bot-challenge (js-challenge)** for **all** HTML paths probed this pass, **including the
  `/products/` contract-specification pages** that the E06 pass had retrieved and hashed on
  2026-08-20. This is a change from the E06 retrieval environment and is recorded, not
  bypassed.
- `web.archive.org` returned **HTTP 429** for the whole pass (same as E06 recorded on
  2026-08-20). `archive.today` was not usable.
- The WAF challenge was **not** circumvented. Official rule HTML paths
  (`/regulation/`, `/publicnotice/notice/`, `/reports/...`) remain `RETRIEVAL_BLOCKED`.

Consequence: no fresh live retrieval of official SHFE text was possible this pass. The base
price-limit facts below are therefore bound from **already-committed repository official
evidence** — the E06 hashed contract-text pages (`S01`–`S06`, SHA256-bound) and the
repository-verified binding-notice chain in `docs/evidence/CANONICAL_CONTRACT_SPECS.json`
— not from a fresh snapshot.

## 3. What was bound this pass

### 3.1 Base contract-text daily price limit (normal-day default rule)

The SHFE contract text for each product fixes a **涨跌停板幅度** (daily price limit) as a
symmetric percentage of the previous settlement price. This is the *normal-day default
clause*. It is bound via the E06 hashed official contract pages plus the
repository-verified binding-notice / effective-period chain already committed in
`CANONICAL_CONTRACT_SPECS.json`:

| product | base limit (per bound contract text) | binding notice | effective period | E06 source / SHA256 |
| --- | --- | --- | --- | --- |
| cu | ±3% | [2023]2号公告 | 2023-01-17 .. 2025-12-31 | S01 `82e0ba93…3be3a` |
| al | ±3% | [2023]2号公告 (in-window [2024]105号 = delivery-grade only) | 2023-01-17 .. 2025-12-31 | S02 `a07a59ed…ec184` |
| ni | ±4% | [2023]2号公告 (2025-10-31 text update = delivery-grade only) | 2023-01-17 .. 2025-12-31 | S03 `140b5543…cbbf3` |
| au | ±3% | [2020]134号公告 | 2020-08-31 .. 2025-12-31 | S04 `7481ac53…71f1` |
| ag | ±3% | [2023]2号公告 | 2023-01-17 .. 2025-12-31 | S05 `b865ca53…a6cb9` |
| rb | ±3% | [2023]2号公告 (in-window [2024]116号 = delivery-grade only) | 2023-01-17 .. 2025-12-31 | S06 `615de796…a2063a` |

These values match the already-accepted `price_limit_pct` in `CANONICAL_CONTRACT_SPECS.json`
and the E06 contract-text notes. The in-window contract-text revisions recorded for
al/rb/ni are **delivery-grade-only** and did not change the price-limit value (repository
verified; recorded in `CANONICAL_CONTRACT_SPECS.json` as
`in_window_delivery_grade_revisions_only`).

**Honest boundary of this binding:** this establishes the *contract clause* (base limit)
with its effective period. It is **not** a per-day exchange schedule and it is **not**
evidence that every 2024-2025 trading day actually used exactly this limit.

### 3.2 What is explicitly UNKNOWN / GAP / BLOCKED (no fabrication)

| layer | status this pass | note |
| --- | --- | --- |
| Per-day exchange price-limit adjustment facts (2024-2025) | `HISTORICAL_GAP` | No bound official per-day schedule/notice for any of the six products. `per_day_facts` in the authority is empty. |
| New-listing first-day exception | `UNKNOWN` | Governed by SHFE risk-control rules (`S10`); rule text not bound this pass. No value asserted. |
| Resumption-after-suspension exception | `UNKNOWN` | Same source; not bound. |
| Consecutive same-direction limit handling | `UNKNOWN` | Same source; not bound. |
| Pre-holiday price-limit adjustments | `UNKNOWN` | No bound official notice for the window. |
| SHFE risk-control rule text (`风险控制管理办法`) | `RETRIEVAL_BLOCKED` | Live path WAF-blocked; Wayback 429; not bypassed. |

Nothing in this package asserts a historical per-day limit value from the current rule, from
a constant rule, or from prior knowledge. `UNKNOWN` remains `UNKNOWN`.

## 4. Machine-readable authority schema

`docs/evidence/HISTORICAL_PRICE_LIMIT_AUTHORITY_V0_1.json` (schema
`historical-price-limit-authority-v0_1`) is the committed, machine-readable authority. It
holds:

- header (repository, branch, baseline main, date, exchange, products, window);
- `source_policy` (free/public/unauthenticated, no paid/login/captcha-bypass, no
  current-rule backfill);
- `evidence_status_enum`;
- `sources` (bound artifacts with `source_id`, authority, URL, `retrieved_at`,
  `sha256`, retrieval/evidence status `EXACT_OFFICIAL_BOUND` /
  `REPOSITORY_VERIFIED_REFERENCE` / `RETRIEVAL_BLOCKED`);
- `product_rules` (base limit per product: `base_limit_pct`, `limit_unit`, `symmetric`,
  `basis`, `binding_notice`, `effective_start/end`, `effective_period_proof`,
  `in_window_delivery_grade_revisions_only`, `source_references`, classification
  `BASE_CONTRACT_TEXT_BOUND`);
- `special_day_rules` (each `UNKNOWN` this pass);
- `per_day_coverage` (each product `HISTORICAL_GAP`, `bound_days: 0`);
- `per_day_facts` (empty);
- `fail_closed_interface` policy;
- `identity` (canonical SHA256 of the whole authority, self-verified on load).

## 5. Fail-closed lookup interface

`src/price_limit_authority.py` implements the schema as frozen dataclasses and a
`PriceLimitAuthority` with a deterministic fail-closed interface:

- `base_rule(product, day)` — resolves the single effective **base** rule (raises when no
  effective period covers the day or conflicting rules overlap);
- `per_day_resolution(product, day)` — returns `BOUND` only when exactly one bound per-day
  fact exists, otherwise `UNKNOWN` / `CONFLICT`;
- `per_day_classification(product, day)` — exact evidence classification for the per-day
  layer;
- `require_per_day_fact(product, day)` — the **fail-closed gate**: raises unless exactly one
  bound per-day fact exists;
- `authority_identity()` and `from_evidence_json(...)` — canonical content identity and a
  loader that **rejects identity mismatches** (tamper guard).

**Enforced invariants (by construction and tests):**

1. `per_day_resolution` returns `BOUND` **only** from `per_day_facts`; no code path derives a
   per-day operative fact from a base rule.
2. `require_per_day_fact` raises whenever the operative fact is unbound → execution
   simulation **cannot** claim a real price-limit fill for any 2024-2025 day.
3. Identities are canonical content hashes; any change to a bound field changes the
   authority identity.

For the real 2024-2025 window, `per_day_facts` is empty, so the interface returns `UNKNOWN`
for every product/day — exactly the honest, anti-backfill behavior required by
`current rule ≠ historical rule`. A future governed step that binds official per-day
adjustment notices can populate `per_day_facts`; the interface then returns `BOUND` only for
those days, and the authority identity changes.

Note: absolute per-day lower/upper bounds (the execution-layer `PriceLimitFact`) additionally
require the official previous-settlement price per concrete contract per day, which is
outside this rule-metadata prep and remains unbound for a future governed step.

## 6. Relationship to existing execution semantics

The existing `ChronologicalValidationRunner._visible_limit_fact` already enforces
"exactly one price-limit fact point-in-time" and raises when missing (fail closed at the
execution layer). This prep supplies the **authority data layer** and the **fail-closed
lookup** that a governed data-preparation step must consume before any real limit-fill claim
is admissible. Synthetic price-limit facts (as in the existing execution-semantics tests)
remain fully supported; they are clearly labeled synthetic and are not historical authority.

## 7. Completeness matrix

Legend: `bound` = BASE_CONTRACT_TEXT_BOUND; `gap` = HISTORICAL_GAP; `unknown` = UNKNOWN;
`blocked` = RETRIEVAL_BLOCKED.

| product | base rule (2024-2025) | per-day operative (2024-2025) | special-day rules |
| --- | --- | --- | --- |
| cu | bound (±3%, [2023]2号) | gap | unknown |
| al | bound (±3%, [2023]2号) | gap | unknown |
| ni | bound (±4%, [2023]2号) | gap | unknown |
| au | bound (±3%, [2020]134号) | gap | unknown |
| ag | bound (±3%, [2023]2号) | gap | unknown |
| rb | bound (±3%, [2023]2号) | gap | unknown |

## 8. Final judgment

```text
LIMIT-001_REDUCTION=PREP_DONE_BASE_BOUND_PER_DAY_GAP
BASE_RULE_AUTHORITY=BOUND_MACHINE_READABLE
PER_DAY_OPERATIVE_LAYER=HISTORICAL_GAP
SPECIAL_DAY_RULES=UNKNOWN
REAL_PRICE_LIMIT_FILL_CLAIM_FOR_WINDOW=NOT_AUTHORIZED
CURRENT_RULE_BACKFILL=FORBIDDEN_AND_NOT_USED
```

Rationale:

- The **contract-text base daily price-limit rule** for all six products is now bound to
  official/repository-verified evidence with full provenance and a machine-readable schema.
  This is a real reduction of `LIMIT-001`: the rule authority is governed and reproducible.
- The **per-day exchange-adjustment layer** and **special-day rule layer** remain
  unbound for 2024-2025 (WAF `RETRIEVAL_BLOCKED` + Wayback 429 this pass; no archived
  official copy bound). They are recorded as explicit `HISTORICAL_GAP` / `UNKNOWN`, with no
  fabricated values.
- The **fail-closed interface** ensures that while any required per-day price-limit fact is
  missing, execution simulation rejects claims of *real* price-limit fills. The capability
  audit's LIMIT-001 verdict (blocking, not silently polluting) is preserved and now backed
  by a dedicated governed authority layer.

## 9. Verification

- New tests: `tests/test_price_limit_authority.py` (28 tests) — base-rule binding, per-day
  fail-closed across the whole window, synthetic bound-fact interface, conflict detection,
  schema validation, identity stability/integrity.
- Full suite: **602 tests OK** (baseline 574 + 28).
- `python -m compileall -q src tools tests` → OK.
- `CURRENT_STATE.md` and `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` are **not** modified on this
  branch (integration-owned); the integration lane should record
  `LIMIT-001_REDUCTION=PREP_DONE_BASE_BOUND_PER_DAY_GAP` in shared authority after review.

## 10. Explicit non-claims

- No per-day 2024-2025 price limit is asserted from the current rule or from a constant rule.
- No special-day exception is asserted.
- No official notice content that could not be retrieved was reconstructed.
- No candidate-outcome backtest was run; no main was written.
