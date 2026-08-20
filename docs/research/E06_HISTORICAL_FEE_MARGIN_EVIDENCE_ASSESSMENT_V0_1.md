# E06_HISTORICAL_FEE_MARGIN_EVIDENCE_ASSESSMENT_V0_1

> Task: `E06_OFFICIAL_HISTORICAL_FEE_MARGIN_EVIDENCE_COLLECTION_V0_1`
> Role: source/evidence collection. NOT production code repair.
> Date: 2026-08-20
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Branch: `research/e06-official-fee-margin-evidence-v01`
> Baseline: `origin/main` @ `c32c5bf2b76afd290cc0e44839aacf778d423863`
> Companion artifact: `docs/evidence/E06_HISTORICAL_FEE_MARGIN_SOURCE_INVENTORY_V0_1.json`

```text
PRODUCTION_SRC_CHANGED=NO
TESTS_CHANGED=NO
CANDIDATE_BACKTEST_RUN=NO
CURRENT_RATE_BACKFILL_USED=NO
PAID_SOURCE_USED=NO
LOGIN_SOURCE_USED=NO
CAPTCHA_BYPASS_USED=NO
WAF_CHALLENGE_NOT_CIRCUMVENTED=YES
```

This package collects point-in-time official SHFE evidence for transaction margin and
transaction fee facts for `cu`, `al`, `ni`, `au`, `ag`, `rb` over
`2024-01-01..2025-12-31`. It does not implement a runtime fee schedule, does not run any
backtest, and does not decide E-07 mapping or E-08 resource semantics.

---

## 1. Source policy applied

`FREE_PUBLIC_UNAUTHENTICATED_FIRST`. Only SHFE official public sources or repository
verified official references were used. No paid, login, subscription, or captcha-bypass
path was used.

## 2. Retrieval environment (recorded honestly)

- Live SHFE `www.shfe.com.cn` serves a **Safeline WAF bot-challenge page** for all HTML
  paths except the `/products/` contract-specification pages and direct static-file
  downloads (`W0xxx.*` attachments, `P0xxx.zip` annual archives). This was verified for
  `/publicnotice/notice/`, `/reports/businessdata/feeandcharges/`,
  `/regulation/`, `/sitemap/`, `/api/`, `/pub/`, `/data/` and for a specific notice page.
- The WAF challenge was **not** bypassed; it was recorded as `RETRIEVAL_BLOCKED` for those
  paths.
- Static file downloads from the official domain **do** succeed without the HTML
  challenge. This is how the official fee attachment bytes below were bound.
- `web.archive.org` CDX/availability/web interfaces returned HTTP 429 for the whole pass;
  `archive.today` returned 429; `DuckDuckGo` (html + lite) returned an anomaly page after
  a few queries; `Baidu` returned a captcha; `Bing`/`Yandex`/`Mojeek`/`SearXNG` were
  unusable or captcha-gated. These are retrieval limitations, not evidence of
  non-existence.

Consequence: **official notice HTML pages and the official monthly fee/margin schedule
pages could not be read in this pass.** The evidence below is therefore partial and is
labelled per the `evidence_status` enum. This package does **not** claim a complete
point-in-time fee/margin schedule.

## 3. What was bound this pass

### 3.1 Six official SHFE contract-specification pages (live, hashed)

Retrieved live from `https://www.shfe.com.cn/products/futures/metal/...` on 2026-08-20.
Each page is the current contract text with its binding notice. The values relevant to
E-06 are the **contract-text minimum transaction margin** (最低交易保证金, i.e. the
margin written into the contract text) and the delivery/limit facts. These are distinct
from the exchange trading-margin rate set by notices (see §5).

| product | contract-text minimum margin | basis | price limit | binding notice (repo-verified) | effective window (repo-verified) |
| --- | --- | --- | --- | --- | --- |
| cu | 5% of contract value | percentage_of_contract_value | ±3% | [2023]2号 | 2023-01-17..2025-12-31 |
| al | 5% of contract value | percentage_of_contract_value | ±3% | [2023]2号; in-window [2024]105号 (delivery grade only) | 2023-01-17..2025-12-31 |
| ni | 5% of contract value | percentage_of_contract_value | ±4% | [2023]2号; 2025-10-31 text update (delivery grade only) | 2023-01-17..2025-12-31 |
| au | 4% of contract value | percentage_of_contract_value | ±3% | [2020]134号 | 2020-08-31..2025-12-31 |
| ag | 4% of contract value | percentage_of_contract_value | ±3% | [2023]2号 | 2023-01-17..2025-12-31 |
| rb | 5% of contract value | percentage_of_contract_value | ±3% | [2023]2号; in-window [2024]116号 (delivery grade only) | 2023-01-17..2025-12-31 |

The binding-notice references and effective windows are taken from the already committed,
repository-verified `docs/evidence/CANONICAL_CONTRACT_SPECS.json` (itself built from
official SHFE product pages). The six live pages confirm the contract-text minimum margin
values shown above.

**Caveat recorded:** the six pages are current snapshots (2026-08-20). They establish the
contract-text minimum margin in force for the window only via the binding-notice /
effective-period chain already verified in `CANONICAL_CONTRACT_SPECS.json`; they are not
per-day exchange margin schedules.

### 3.2 One official fee attachment (gold, bound and extracted)

- Resource: `W020250423567339313503.doc`
- URL: `https://www.shfe.com.cn/publicnotice/notice/202504/W020250423567339313503.doc`
- content_type: `application/msword`; byte_size: 34816; `Last-Modified: 2025-04-23`
- sha256: `8599ef055c98975776e1879fe501ca74b96392d996a501413fef32bdb3b22bd5`
- Content: official attachment "调整后相关合约交易手续费一览表" (adjusted transaction fee
  schedule for relevant contracts), columns: transaction fee (元/手), hedging transaction
  fee (元/手), intraday close-today transaction fee (元/手), intraday close-today hedging
  transaction fee (元/手).

Bound point-in-time fact (contract AU2506, as published 2025-04-23):

| contract | transaction fee | hedging fee | close-today fee | hedging close-today fee | basis |
| --- | --- | --- | --- | --- | --- |
| AU2506 | 20 元/手 | 10 元/手 | 20 元/手 | 10 元/手 | per_lot (元/手) |

This binds a **gold fee basis of fixed-per-lot** (元/手) and one point-in-time value set
for gold, effective around 2025-04-23. It does **not** establish the gold fee before that
date, nor the gold margin, nor any other product's fees.

### 3.3 Repository verified official references (not re-fetched this pass)

- `docs/evidence/CANONICAL_CONTRACT_SPECS.json` (product spec provenance, binding notices,
  effective periods).
- `docs/evidence/SHFE_OFFICIAL_RAW_RECHECK_MANIFEST.json` (official annual daily-quotation
  archives 2023/2024/2025, HTTP 200, sha256-bound; these contain OHLC/volume/OI, not
  fee/margin schedules).

## 4. What was NOT retrievable this pass

- Official notice HTML pages for 2024-2025 margin/fee adjustments (`RETRIEVAL_BLOCKED`,
  WAF).
- Official monthly fee schedule pages
  (`/reports/businessdata/feeandcharges/YYYYMM/...`) (`RETRIEVAL_BLOCKED`, WAF).
- Historical exchange trading-margin schedules (`交易所保证金率`) for the window
  (`HISTORICAL_SCHEDULE_GAP` — no bound official value).
- Transaction/close-today/close-previous fee schedules for the window for
  `cu, al, ni, ag, rb` and for `au` outside the 2025-04-23 point (`HISTORICAL_SCHEDULE_GAP`).

### 4.1 Known official notice URLs not yet read (`OFFICIAL_REFERENCE_ONLY`)

The following official SHFE URLs were discovered (search-engine URL discovery only; the
live HTML is WAF-blocked and archives were rate-limited this pass). They are recorded so a
future pass can bind their content:

| official URL | period | status this pass |
| --- | --- | --- |
| `https://www.shfe.com.cn/publicnotice/notice/202407/t20240715_801992.html` | 2024-07 | OFFICIAL_REFERENCE_ONLY / RETRIEVAL_BLOCKED |
| `https://www.shfe.com.cn/publicnotice/notice/202405/t20240529_801782.html` | 2024-05 | OFFICIAL_REFERENCE_ONLY / RETRIEVAL_BLOCKED |
| `https://www.shfe.com.cn/publicnotice/notice/202512/t20251222_829864.html` | 2025-12 | OFFICIAL_REFERENCE_ONLY / RETRIEVAL_BLOCKED |
| `https://www.shfe.com.cn/reports/businessdata/feeandcharges/202501/t20250102_824218.html` | 2025-01 | OFFICIAL_REFERENCE_ONLY / RETRIEVAL_BLOCKED |
| `https://www.shfe.com.cn/publicnotice/notice/202601/t20260120_830161.html` | 2026-01 (outside window) | reference only |

No value from any of these URLs is asserted. They are candidate targets for a future
official-retrieval pass.

## 5. Margin distinction (per task §7)

This package distinguishes:

- **Contract-text minimum transaction margin** (最低交易保证金 written into the contract
  text): bound above for all six products (`EXACT_OFFICIAL_BOUND`).
- **Exchange trading margin** (交易所交易保证金率 applied to actual positions, adjustable
  by notices): **not bound** this pass; no current rate was backfilled.

Broker-added margin is explicitly out of scope; no assumption is made about future
broker surcharges.

## 6. Close-today vs close-previous (per task §8)

- The bound gold attachment defines an explicit **intraday close-today fee** distinct from
  the general transaction fee (`CLOSE_TODAY_FEE` recorded; 20 元/手 for AU2506 as
  published 2025-04-23). No separate close-previous fee was present in that attachment,
  so `CLOSE_PREVIOUS_FEE` for au is recorded as `NOT_SEPARATELY_SPECIFIED_BY_BOUND_SOURCE`
  for that point.
- For `cu, al, ni, ag, rb`, no official close-today/close-previous distinction could be
  bound this pass; recorded as `HISTORICAL_SCHEDULE_GAP` / not separately specified by any
  bound source. No fabricated second value was created.

## 7. Completeness matrix

Legend: `covered` = EXACT_OFFICIAL_BOUND; `gap` = HISTORICAL_SCHEDULE_GAP (no bound value
for the period); `blocked` = RETRIEVAL_BLOCKED (official source known/exists but could not
be retrieved this pass); `reference` = OFFICIAL_REFERENCE_ONLY (official URL known, value
not bound).

Fact types: `CTX_MARGIN` = contract-text minimum transaction margin; `EX_MARGIN` =
exchange trading margin; `TX_FEE` = transaction fee; `CT_FEE` = close-today fee;
`CP_FEE` = close-previous fee; `BASIS` = fee basis.

| product | CTX_MARGIN (2024-2025) | EX_MARGIN (2024-2025) | TX_FEE (2024-2025) | CT_FEE (2024-2025) | CP_FEE (2024-2025) | BASIS (2024-2025) |
| --- | --- | --- | --- | --- | --- | --- |
| cu | covered (5%, [2023]2号) | blocked | blocked | blocked | blocked | blocked |
| al | covered (5%, [2023]2号) | blocked | blocked | blocked | blocked | blocked |
| ni | covered (5%, [2023]2号) | blocked | blocked | blocked | blocked | blocked |
| au | covered (4%, [2020]134号) | blocked | partial (20元/手 @2025-04-23 only) | partial (20元/手 @2025-04-23 only) | gap | covered for the bound point (per_lot) |
| ag | covered (4%, [2023]2号) | blocked | blocked | blocked | blocked | blocked |
| rb | covered (5%, [2023]2号) | blocked | blocked | blocked | blocked | blocked |

Overall the matrix is dominated by `blocked`/`gap` for the exchange-level facts that a
realistic execution schedule requires.

## 8. Final judgment

```text
E06_FINAL_JUDGMENT=PARTIALLY_BUILDABLE_WITH_GAPS
E06_EXCHANGE_LEVEL_SCHEDULE_JUDGMENT=INSUFFICIENT_EVIDENCE
```

Rationale:

- Contract-text minimum transaction margins for all six products are bound to official
  SHFE pages with hashes and repo-verified binding notices
  (`EXACT_OFFICIAL_BOUND`).
- One point-in-time gold fee schedule (AU2506, 2025-04-23) is bound
  (`EXACT_OFFICIAL_BOUND`), which also fixes gold fee basis as fixed-per-lot for that
  point.
- The exchange trading-margin schedule and the transaction/close-today/close-previous fee
  schedules over 2024-01-01..2025-12-31 are **not** established: notice HTML pages were
  WAF-blocked and archives were rate-limited this pass. They are recorded as
  `RETRIEVAL_BLOCKED` / `HISTORICAL_SCHEDULE_GAP`.
- **No current rate was backfilled. No value was invented.**
- Because key time ranges (all of 2024, most of 2025, and all products except the one au
  point) lack a bound official exchange-level fee/margin value, this package does **not**
  claim a candidate-quality historical schedule complete for any product, and the overall
  schedule is not `COMPLETE_BUILDABLE`.

Interpretation: the package is "partially buildable with gaps" only at the level of
contract-text minimum margins (plus one gold fee point). For the specific E-06 goal of a
realistic **exchange-level** point-in-time fee/margin schedule, the evidence is
`INSUFFICIENT_EVIDENCE`: the bound contract-text margins alone do not constitute an
exchange trading-margin schedule, and no exchange-level fee schedule exists for the
window. A future pass with different retrieval conditions (SHFE WAF policy change, archive
availability) is required before any exchange-level schedule may be considered buildable.

## 9. Constraints honored

- No `src/*` change, no `tests/*` change.
- No runtime fee schedule code.
- No candidate backtest, no return comparison.
- No E-07 mapping decision, no E-08 resource-semantics decision.
- Gap and blocked records are explicit, not silently filled.
