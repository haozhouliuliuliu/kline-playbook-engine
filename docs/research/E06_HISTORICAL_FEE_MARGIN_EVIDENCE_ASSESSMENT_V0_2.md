# E06_HISTORICAL_FEE_MARGIN_EVIDENCE_ASSESSMENT_V0_2

> Task: `E06_FINAL_BOUNDED_STATIC_OFFICIAL_EVIDENCE_PASS_V0_1`
> Role: source/evidence collection (final bounded pass). NOT production code repair. NOT an open-ended search task.
> Date: 2026-08-20
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Branch: `research/e06-final-static-official-pass-v01`
> Baseline: `origin/main` @ `e0cf182475fb9c39bd2b40447e49cba9909ae4cb`
> Companion artifact: `docs/evidence/E06_HISTORICAL_FEE_MARGIN_SOURCE_INVENTORY_V0_2.json`
> V0_1 preserved: `docs/research/E06_HISTORICAL_FEE_MARGIN_EVIDENCE_ASSESSMENT_V0_1.md` and
> `docs/evidence/E06_HISTORICAL_FEE_MARGIN_SOURCE_INVENTORY_V0_1.json`

```text
PRODUCTION_SRC_CHANGED=NO
TESTS_CHANGED=NO
CANDIDATE_BACKTEST_RUN=NO
CURRENT_RATE_BACKFILL_USED=NO
PAID_SOURCE_USED=NO
LOGIN_SOURCE_USED=NO
CAPTCHA_BYPASS_USED=NO
WAF_CHALLENGE_NOT_CIRCUMVENTED=YES
THIRD_PARTY_VALUE_SUBSTITUTION_USED=NO
PRICE_VOLATILITY_MARGIN_INFERENCE_USED=NO
COPYRIGHTED_DOCUMENTS_COMMITTED=NO
```

This is the final bounded static-official evidence pass for E-06 (R2 Lane 2). It attempts one
last time to bind SHFE official static attachments for 2024-2025 fee / exchange-margin
evidence. After this pass, remaining gaps are formally preserved as long-lived governed
prerequisites and are not re-acquired through repeated crawling.

---

## 1. Scope and constraints honored

- Search engines were used **only** to discover official static attachment URLs and official
  notice references (DuckDuckGo lite). No numeric value from any search snippet was asserted
  as a binding value.
- All bound values were extracted from **SHFE official artifact bytes** downloaded directly
  from `www.shfe.com.cn`.
- No WAF bypass, no captcha bypass, no login, no paid source, no current-rate backfill, no
  third-party value substitution (新浪/东方财富/券商/论坛/blog), no price/volatility-derived
  margin inference.
- No `src/*` change, no `tests/*` change, no runtime fee schedule, no candidate outcome.

## 2. Retrieval environment (recorded honestly)

Re-verified this pass:

- Live SHFE `www.shfe.com.cn` still serves a **Safeline WAF bot-challenge page** for HTML
  notice paths. Example re-check: `GET /publicnotice/notice/202405/t20240529_801782.html`
  returns HTTP 200 but the body is the WAF challenge page (`WEB应用防火墙`).
- **Direct static-file downloads of W-prefixed notice attachments succeed** without the HTML
  challenge. This is the access path used to bind the artifacts below.
- `web.archive.org` CDX and `archive.org/wayback/available` still return HTTP 429;
  `archive.today` 429. Browser DNS resolution for `shfe.com.cn` failed in the integrated
  browser, but OS-level DNS/TCP succeeded; direct downloads were performed via the local
  terminal.
- DuckDuckGo lite (browser) worked this pass for URL discovery (unlike V0_1's rate-limits).

## 3. What was newly bound this pass (official static artifact bytes)

Each row is an official `W*.doc` / `W*.docx` notice attachment downloaded directly from the
SHFE official domain. Values are extracted from the artifact bytes; the raw copyrighted
documents are **not** committed (only reference, SHA256, and structured extracted facts).

### 3.1 Gold transaction-fee schedule (2025-05-14)

- Resource: `W020250514571606151665.doc`
- URL: `https://www.shfe.com.cn/publicnotice/notice/202505/W020250514571606151665.doc`
- sha256: `c006eaed477a1fa5382bbb99bf1bc53b937b2cdcfa2ed3ccd8d1a20922a4fd36`; byte_size 48128
- Notice reference: 关于调整黄金期货品种相关合约交易手续费的通知 (2025-05-14)
- Values (transaction / hedging / close-today / hedging close-today, 元/手):

| contract | tx fee | hedge | close-today | hedge close-today |
| --- | --- | --- | --- | --- |
| AU2506 | 20 | 10 | 20 | 10 |
| AU2507 | 20 | 10 | 0 | 0 |
| AU2508 | 20 | 10 | 20 | 10 |
| AU2510 | 10 | 5 | 0 | 0 |
| AU2512 | 20 | 10 | 0 | 0 |
| AU2602 | 10 | 5 | 0 | 0 |
| AU2604 | 10 | 5 | 0 | 0 |
| AU2606 | 20 | 10 | 0 | 0 |

Fee basis for this schedule is fixed-per-lot (元/手). This extends the V0_1 AU2506 2025-04-23
point to a fuller gold contract set.

### 3.2 Silver transaction-fee schedule (2025-12-22, effective 2025-12-24)

- Resource: `W020251222666756741466.doc`
- URL: `https://www.shfe.com.cn/publicnotice/notice/202512/W020251222666756741466.doc`
- sha256: `4cddc94f46de4ae4281aad605160cb3d2553f68d07cf2fae96f679bd72747822`; byte_size 33792
- Notice reference: 上期发〔2025〕377号 (2025-12-22), effective 2025-12-24 trading
- Values (transaction / hedging / close-today / hedging close-today, ‰):

| contract | tx rate | hedge | close-today | hedge close-today |
| --- | --- | --- | --- | --- |
| AG2602 | 0.05 | 0.025 | 0.25 | 0.125 |
| AG2604 | 0.01 | 0.005 | 0.05 | 0.025 |

This establishes that **silver fees are on a per-turnover (‰) basis** at this point, and binds
silver close-today fees for AG2602/AG2604.

### 3.3 Gold & silver exchange trading-margin / price-limit (2024-05-21, effective 2024-05-23)

- Resource: `W020240521646446918541.docx`
- URL: `https://www.shfe.com.cn/publicnotice/notice/202405/W020240521646446918541.docx`
- sha256: `e7aead59cbdfed2a790e52b4e93ad3cf3a43d5640e38269069b77eea2a7617a9`; byte_size 20280
- Notice reference: 关于调整黄金等期货交易保证金比例和涨跌停板幅度的通知 (SHFE 2024-05-21),
  effective 2024-05-23
- Exchange-level values (both gold and silver):

| standard | 涨跌停板 | 交易保证金 套保 | 交易保证金 投机 |
| --- | --- | --- | --- |
| 现行 | 8% | 9% | 10% |
| 调整后 | 10% | 11% | 12% |

Note: broker-posted copies (e.g. 国联期货) state 套保16%/投机17% — those are broker
surcharges on top of the exchange margin and are **not** used. The exchange-level values are
11%/12% from the official SHFE attachment.

### 3.4 Silver exchange margin / price-limit, AG2602 (2025-12-10)

- Resource: `W020251210612760043490.docx`
- URL: `https://www.shfe.com.cn/publicnotice/notice/202512/W020251210612760043490.docx`
- sha256: `ec0c4640b433dae74d2f7e0dcbd52cd7378711e38306acd104e23525721a22bf`; byte_size 19444
- Values (AG2602): 现行 涨跌停板14%, 套保15%, 一般16%; 调整后 涨跌停板15%, 套保16%, 一般17%.

### 3.5 Special-contract hedging-fee schedule (2024-07-15)

- Resource: `W020240715643641663357.doc`
- URL: `https://www.shfe.com.cn/publicnotice/notice/202407/W020240715643641663357.doc`
- sha256: `63da302fabecbf0e50ca89db8222545f23dbe050c508b5787bc18fe4b8729e60`; byte_size 87552
- Notice reference: SHFE fee schedule notice, publication 2024-07-15
- Relevant values (hedging / 套保):

| item | value |
| --- | --- |
| NI2408/NI2409 套保 / 套保平今 | 1.5 / 4.5 元/手 |
| AU2408 套保 / 套保平今 | 5 / 3 元/手 |
| RB2501 套保 / 套保平今 | 0.15‰ / 0.15‰ |
| 黄金套保: 6/12月合约 | 5 元/手 (平今 0) |
| 黄金套保: 其他月 上市起 / 交割月前第二月起 | 1 / 5 元/手 (平今 0) |
| 白银套保: 6/12月合约 | 0.025‰ / 0.025‰ |
| 白银套保: 其他月 上市起 / 交割月前第二月起 | 0.005‰ / 0.025‰ |

This binds hedging-specific fee values for `ni`, `au`, `rb` at a 2024 point-in-time.

## 4. Official references discovered but NOT byte-bound this pass (OFFICIAL_REFERENCE_ONLY)

The following official notice URLs / text were discovered via search (URL discovery only);
the live HTML is WAF-blocked and was not downloaded, so no value from them is asserted as a
binding value:

| reference | period | note |
| --- | --- | --- |
| `t20240529_801782.html` | 2024-05 | 螺纹钢/黄金/白银/燃料油 fee adjustment notice (rebar fee text present in index) |
| `t20240418_801607.html` (上期发〔2024〕123号) | 2024-04 | gold/silver fee adjustment (AU2406 30元/手 close-today, AU2408 6元/手, AG2408 万分之零点三) |
| `t20251017_829279.html` | 2025-10 | gold/silver margin/price-limit (涨跌停板14%, 套保15%, 一般16%) |
| nickel NI2409 fee notice (2024-07-02) | 2024-07 | NI2409 transaction fee 3元/手 effective 2024-07-02 (tsite notice 911404829.html) |
| `t20250102_824218.html` (2025-01 fee schedule page) | 2025-01 | official monthly fee schedule page (HTML) |
| `W020240715641204649505.doc` (second 2024-07-15 attachment) | 2024-07 | not downloaded this pass |

These are recorded for a future pass under changed access conditions; they are not asserted as
values.

## 5. Completeness matrix (V0_2)

Legend: `covered` = EXACT_OFFICIAL_BOUND (full window); `point` = EXACT_OFFICIAL_BOUND at
specific point(s); `ref` = OFFICIAL_REFERENCE_ONLY; `gap` = HISTORICAL_SCHEDULE_GAP.

Fact types: `CTX_MARGIN` = contract-text minimum transaction margin; `EX_MARGIN` = exchange
trading margin; `TX_FEE` = transaction fee; `CT_FEE` = close-today fee; `CP_FEE` =
close-previous fee; `BASIS` = fee basis.

| product | CTX_MARGIN | EX_MARGIN (2024-25) | TX_FEE (2024-25) | CT_FEE | CP_FEE | BASIS |
| --- | --- | --- | --- | --- | --- | --- |
| cu | covered (5%) | gap | gap | gap | gap | gap |
| al | covered (5%) | gap | gap | gap | gap | gap |
| ni | covered (5%) | gap | point (hedge NI2408/09 2024-07) | gap | gap | point (per-lot hedge) |
| au | covered (4%) | point (2024-05-23 套保11/投机12) | point (2025-04-23, 2025-05-14) | point (2025-04/05) | gap | point (per-lot) |
| ag | covered (4%) | point (2024-05-23; AG2602 2025-12-10) | point (2025-12-24) | point (AG2602/04 2025-12-24) | gap | point (per-turnover) |
| rb | covered (5%) | gap | point (hedge RB2501 2024-07) | gap | gap | point (hedge per-turnover) |

Compared to V0_1 (which was dominated by `blocked`/`gap` for all exchange-level facts), V0_2
now has `point` bindings for au/ag exchange margins, au/ag fees, and ni/au/rb hedging fees.
However, **no product has a continuous point-in-time exchange-level fee/margin schedule over
the window**, and cu/al/ni/rb exchange margins plus general fee schedules remain unbound.

## 6. Final judgment

```text
E06_FINAL_JUDGMENT=PARTIALLY_BUILDABLE_WITH_GAPS
E06_EXCHANGE_LEVEL_SCHEDULE_JUDGMENT=INSUFFICIENT_EVIDENCE
E06_FURTHER_REPEAT_ACQUISITION_DEFAULT=NO
E06_REMAINING_GAPS=LONG_LIVED_GOVERNED_PREREQUISITE
E06_REOPEN_TRIGGER=NEW_OFFICIAL_SOURCE_OR_ACCESS_CHANGE_OR_OWNER_POLICY_CHANGE
```

Rationale:

- Contract-text minimum transaction margins remain bound for all six products (`EXACT_OFFICIAL_BOUND`).
- This pass materially expanded point-in-time exchange-level evidence: gold fee schedule
  (2025-05-14), silver fee schedule with per-turnover basis (2025-12-24), gold/silver exchange
  trading margin (2024-05-23), AG2602 exchange margin (2025-12-10), and special-contract
  hedging fees for ni/au/rb (2024-07-15) — all byte-bound to official SHFE artifacts.
- The outcome is **not** upgraded to `COMPLETE_BUILDABLE` merely because much was found:
  there is still no continuous point-in-time exchange-level fee/margin schedule for any
  product over `2024-01-01..2025-12-31`; exchange margins for cu/al/ni/rb and general
  transaction-fee schedules for cu/al/ni/rb (and silver) are unbound; the reversal dates of
  elevated gold/silver margin periods are unbound; and many notice effective dates are
  reference-only.
- Therefore the exchange-level schedule remains `INSUFFICIENT_EVIDENCE`, and the overall
  outcome is `PARTIALLY_BUILDABLE_WITH_GAPS`.
- Remaining gaps are preserved as `LONG_LIVED_GOVERNED_PREREQUISITE` with
  `E06_FURTHER_REPEAT_ACQUISITION_DEFAULT=NO`. This is not an abandonment of accuracy: it
  prevents the project from stalling on repeated scraping. It is not re-opened unless an
  official access condition changes, a new formal source appears, or the Owner changes the
  source policy.
- No value was invented; `UNKNOWN`/`NOT_SPECIFIED` is preserved.

## 7. Constraints honored (final)

- No `src/*` change, no `tests/*` change.
- No runtime fee schedule code, no candidate outcome.
- No E-07 mapping decision, no E-08 resource-semantics decision.
- No current-rate backfill; no third-party numeric authority; no WAF/captcha/login bypass.
- Downloaded copyrighted `.doc`/`.docx` artifacts were hashed and extracted but are **not**
  committed; only reference, hash, and structured extracted facts are recorded.
- V0_1 evidence documents are preserved and not overwritten.
