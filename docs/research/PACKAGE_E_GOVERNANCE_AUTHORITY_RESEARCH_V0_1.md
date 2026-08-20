# PACKAGE_E_GOVERNANCE_AUTHORITY_RESEARCH_V0_1

> Task: `PACKAGE_E_GOVERNANCE_AUTHORITY_RESEARCH_V0_1`
> Role: research / authority package ONLY. NOT a production repair package.
> Date: 2026-08-20
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Branch: `research/package-e-governance-authority-v01`
> Baseline: `origin/main` @ `18a28c3`
> Findings authority: `docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md`
> Lane authority: `docs/reviews/CDF_CORRECTION_REVIEW_AND_NEXT_PARALLEL_PLAN_V0_1.md`

```text
STATUS=RESEARCH_COMPLETE
PRODUCTION_CODE_CHANGED=NO
CURRENT_STATE_CHANGED=NO
NO_OUTCOME_RULE_SELECTED=YES
SOURCE_POLICY=FREE_PUBLIC_UNAUTHENTICATED_FIRST
PAID_SOURCE_USED=NO
LOGIN_SOURCE_USED=NO
CANDIDATE_OUTCOME_DATA_USED=NO
```

This package answers, for E-04/E-05/E-06/E-07/E-08, whether an **existing authority**
already decides the open question, or whether an **Owner decision** is required. It does
not choose any new outcome-affecting rule. No `src/*.py` file and no authority/state file
was modified.

---

## Executive conclusion

| Item | Open question | Repository authority found | External formal authority resolves | Verdict |
| --- | --- | --- | --- | --- |
| E-04 | generic `CLOSE` split allocation / fee semantics across today+previous buckets | Partial synthetic field exists (`generic_close_rule="TODAY_FIRST"`) but split case raises; not Owner-frozen | No exchange auto-split rule; TqSdk requires explicit offset for SHFE | `OWNER_DECISION_REQUIRED` |
| E-05 | heterogeneous per-member multiplier/capital representation in one portfolio evaluation | Multiplier facts already bound per-contract in `ContractMaster`; portfolio representation not frozen | (facts only; representation is project-internal) | `OWNER_DECISION_REQUIRED` |
| E-06 | historical realistic fee/margin point-in-time schedule for cu/al/ni/au/ag/rb 2024-01-01..2025-12-31 | `NOT_IMPLEMENTED_FOR_CANDIDATE_QUALITY`; synthetic assumptions only; no fee/margin schedule committed | Official SHFE sources free/public but not bound at this pass; retrieval blocked at research time | `INSUFFICIENT_EVIDENCE` |
| E-07 | concrete-contract / main-contract research mapping rule | `NOT_FROZEN` (corpus = all concrete contracts; `ContractMappingSchedule` has no selection algorithm) | Exchanges define no single research main-contract rule; TqSdk `KQ.m@` is a vendor convention | `OWNER_DECISION_REQUIRED` |
| E-08 | margin-admission resource definition (`available_capital` vs `available_resources`) | No frozen authority; admission uses `available_capital` | CTP/TqSdk account model is equity-aware (maps to `available_resources`) but does not force the project model | `OWNER_DECISION_REQUIRED` |

**Summary:** Four of the five items (`E-04`, `E-05`, `E-07`, `E-08`) require an Owner
decision because no existing repository authority and no binding external formal rule
determines the outcome-affecting semantics. `E-06` is an evidence gap, not an authority
question: the exact historical fee/margin schedule is not yet established from verified
official evidence and must not be backfilled from current rates.

No `ADOPTED=` / `FROZEN=` / `SELECTED=` claim is made anywhere in this document for any
new rule. Where a repository field or an external convention exists, it is reported as
**existing material** and its authority status is stated explicitly.

---

## E-04 — generic CLOSE across today + previous buckets

### Problem restated

`today < close_qty`, `previous < close_qty`, `today + previous >= close_qty`. The close
must be split across both buckets, but the project has no frozen rule for the allocation
order (nor for splitting at all).

### A. Repository close-offset authority

- `src/contract_semantics.py` defines `CloseOffset` = `CLOSE_TODAY | CLOSE_PREVIOUS | CLOSE`.
- `src/contract_semantics.py` `OffsetCostAssumptions` carries
  `generic_close_rule: str = "TODAY_FIRST"`; `__post_init__` rejects any value other than
  `"TODAY_FIRST"`, and the field is inside `identity_id`. This is a **versioned synthetic
  field**.
- `src/validation_runner.py` `_apply_capital_constraints` generic-close resolution:
  ```text
  if today_quantity >= q:            -> CLOSE_TODAY
  elif previous_quantity >= q:       -> CLOSE_PREVIOUS
  else: raise "generic close cannot deterministically resolve across position buckets"
  ```
  The split shape (`today < q AND previous < q AND today+previous >= q`) **raises**. The
  resolution code does not read `generic_close_rule` at all; `TODAY_FIRST` is only a
  defaulted field of `OffsetCostAssumptions` that single-bucket resolution happens to be
  consistent with.
- `docs/evidence/CHINA_FUTURES_CONTRACT_EXECUTION_SEMANTICS_VERIFICATION.md` states:
  "通用 `CLOSE` 只按版本化的合成规则确定性解析" — a generic CLOSE is resolved
  deterministically by the versioned synthetic rule. It does **not** name a frozen
  allocation order for a **split** across buckets, and it does not record an Owner freeze
  of `TODAY_FIRST`.
- No document in the repository explicitly freezes `TODAY_FIRST` (or any other order) as
  an Owner-approved project semantic for the cross-bucket split. `CURRENT_STATE.md` and the
  CDF plan record `E04_SPLIT_RULE_CHOICE=NOT_DELEGATED_TO_WORKER`.

**Repo conclusion:** A **partial, synthetic, code-level** field (`TODAY_FIRST`) exists for
single-bucket priority, but there is **no binding project authority** for the cross-bucket
split allocation and its fee splitting. The split case fails closed today.

### B. External formal rule (SHFE / TqSdk / adopted execution abstraction)

- **TqSdk official docs** (the project's adopted scoped data/execution abstraction;
  `doc.shinnytech.com/tqsdk/latest/usage/trade.html` and
  `reference/tqsdk.api.html`, retrieved 2026-08-20) define the order `offset`:
  ```text
  offset: "OPEN", "CLOSE" 或 "CLOSETODAY"
  (上期所和上期能源分平今/平昨, 平今用"CLOSETODAY", 平昨用"CLOSE";
   其他交易所直接用"CLOSE" 按照交易所的规则平仓)
  ```
  i.e., for SHFE the caller **must explicitly choose** 平今 (`CLOSETODAY`) or 平昨
  (`CLOSE`). TqSdk/CTP does not provide an automatic proportional split of a generic
  close across today and previous buckets.
- **Exchange semantics vs broker/API behavior:** SHFE requires the 平今/平昨 distinction
  on order entry (fees differ), and there is **no official exchange rule that
  automatically allocates a generic close across the two buckets**. Any "default order"
  (e.g., some terminals closing 昨仓 first) is a broker/API convention, not an exchange
  rule, and is therefore not binding for the project's synthetic model.

**External conclusion:** No binding external formal authority resolves the cross-bucket
split. The external material is consistent with "the caller/upper layer must specify the
bucket" (`OPTION_C` shape below) but does not force the project's synthetic model.

### C. Minimum Owner decision (do NOT select here)

| Option | Allocation rule | Impact on fee calculation | Impact on evidence identity | Determinism |
| --- | --- | --- | --- | --- |
| `OPTION_A` | today-first, then previous (consume today fully, remainder from previous) | Each bucket pays its own per-bucket fee (`close_today_fee_per_unit` / `close_previous_fee_per_unit`) on its consumed quantity | The resolved per-leg offsets and per-bucket fee identities must be recorded in the execution outcome / capital transition / round-trip identity (new split legs become distinct evidence) | Deterministic given bucket quantities; must define tie/remainder handling |
| `OPTION_B` | previous-first, then today (consume previous fully, remainder from today) | Same per-bucket fee mechanics, different fee mix when the two fees differ | Same evidence-identity requirement; different recorded leg split | Deterministic given bucket quantities; must define tie/remainder handling |
| `OPTION_C` | forbid automatic allocation across buckets for generic `CLOSE`; upper layer must explicitly emit `CLOSE_TODAY` + `CLOSE_PREVIOUS` child orders | Fees charged exactly per explicit bucket order (no implicit split) | Evidence identity stays per explicit order; no synthetic split legs | Fully deterministic; closest to TqSdk/SHFE explicit-offset semantics |

This package does not discuss returns and does not choose among `OPTION_A/B/C`.

---

## E-05 — heterogeneous multipliers in one portfolio evaluation

### Who is the multiplier factual authority?

- `src/contract_semantics.py` `ContractSpecification.contract_multiplier` (per concrete
  contract) inside `ContractMaster` is the **factual authority**. It is bound to official
  SHFE contract text in `docs/evidence/CANONICAL_CONTRACT_SPECS.json`:
  cu=5 t/lot, al=5 t/lot, ni=1 t/lot, au=1000 g/lot, ag=15 kg/lot, rb=10 t/lot (each with
  `source_url`, `binding_notice`, `effective_period`, `retrieved_at`, `identity`).
- `src/portfolio_semantics.py` `PortfolioRequest.capital_assumptions` is a **single**
  `CapitalMarginAssumptions` with one `contract_multiplier`; `_resolve_candidates` requires
  `contract.contract_multiplier == request.capital_assumptions.contract_multiplier` for
  every resolved member, else raises `"portfolio contract multiplier is inconsistent with
  capital assumptions"`. One evaluation therefore cannot represent products whose resolved
  multipliers genuinely differ.

### Answer

**Yes** — multipliers are already factually bound per contract by `ContractMaster`
(`ContractSpecification.contract_multiplier`), sourced from official SHFE material. The
open part is **only the portfolio representation**: how one evaluation carries
heterogeneous per-member capital semantics.

### Repository/architecture determines the representation uniquely?

- `ARCHITECTURE_BASELINE.md` §1 gives the data substrate ownership of "contract
  multiplier/tick/limit metadata" and "contract mapping, main/continuous/roll metadata"
  — consistent with per-contract authority — but it does **not** specify the portfolio
  capital-assumption representation for heterogeneous members.
- Multiple outcome-affecting representations exist (per-member
  `CapitalMarginAssumptions`; per-member multiplier derived from the resolved contract;
  whether margin/offset/execution assumptions also become per-member; how identity hashes
  change). The architecture does not uniquely decide among them.
- `CURRENT_STATE.md`: `E05_PORTFOLIO_REPRESENTATION=NOT_DELEGATED_TO_WORKER`; the CDF plan:
  "E-05 heterogeneous portfolio capital-assumption representation must be specified before
  implementation".

**Verdict: `OWNER_DECISION_REQUIRED`.** The minimal representation direction — each member
uses the **resolved contract's** capital assumption/multiplier rather than a global
multiplier-map framework — is recorded as the candidate minimum, but it is not adopted
here and the Owner must confirm the representation before any implementation. No code was
modified.

---

## E-06 — historical realistic fee/margin authority (2024-01-01..2025-12-31)

### Repository state

- `CURRENT_STATE.md`:
  `HISTORICAL_REALISTIC_MARGIN_FEE_AUTHORITY=NOT_IMPLEMENTED_FOR_CANDIDATE_QUALITY`.
- The validation model uses **synthetic** `initial_margin_rate`, `maintenance_margin_rate`,
  `synthetic_fee`, `synthetic_slippage`, and synthetic `OffsetCostAssumptions` (per E-06
  audit finding). These are acceptable engine fixtures but are not historical
  China-futures candidate-execution realism.
- `docs/evidence/CANONICAL_DATASET_SOURCE_AND_SCOPE_READINESS.md` marks
  multiplier/tick/listing/price-limit as `OFFICIAL_PARTIAL` ("current; historical changes
  need verification"); no committed historical margin/fee schedule exists.
- `docs/evidence/SHFE_OFFICIAL_RAW_RECHECK_MANIFEST.json` proves SHFE **official annual
  daily-quotation archives** were retrievable free/public with recorded `sha256`
  (2023/2024/2025 zips, HTTP 200). Those archives are daily OHLC/volume/OI, **not**
  fee/margin schedules.

### External research (this pass)

- SHFE official product-spec pages and margin/fee adjustment notices are the natural
  free/public official sources. The project has already committed product-spec provenance
  (`CANONICAL_CONTRACT_SPECS.json`).
- At research time (2026-08-20) the SHFE site (`www.shfe.com.cn` and `eng.shfe.com.cn`)
  returned a bot-verification challenge, so no new official notice bytes were fetched this
  session. This is a **retrieval limitation**, not a conclusion that the sources are
  unavailable to a human or to the earlier verified acquisition path.
- TqSdk quote objects expose **current** `commission` / `margin` per contract (example in
  official docs) but do not provide a governed historical point-in-time fee/margin
  schedule for 2024–2025.

### Per-product inventory

`FACT_TYPE` values: INITIAL_MARGIN, MAINTENANCE/EXCHANGE_MARGIN, TRANSACTION_FEE,
CLOSE_TODAY_FEE, CLOSE_PREVIOUS_FEE, BASIS (percentage vs fixed-per-lot), EFFECTIVE_DATES.

```text
PRODUCT=cu|al|ni|au|ag|rb   (each of the six)
FACT_TYPE=INITIAL_MARGIN | MAINTENANCE/EXCHANGE_MARGIN | TRANSACTION_FEE |
          CLOSE_TODAY_FEE | CLOSE_PREVIOUS_FEE | BASIS | EFFECTIVE_DATES
OFFICIAL_SOURCE=SHFE contract-spec page / SHFE margin-fee notice (free public official)
NOTICE/RULE_ID=not bound at this pass (SHFE notice numbers to be collected per effective period)
EFFECTIVE_START=NOT_ESTABLISHED
EFFECTIVE_END=NOT_ESTABLISHED
PUBLIC_FREE=YES (official SHFE sources are free/public)
EXACT_HISTORICAL_VALUE_VISIBLE=NOT_ESTABLISHED (no committed official fee/margin value for 2024-2025)
BYTE_HASH_RECORDED_NOW=NO
STATUS=HISTORICAL_SCHEDULE_GAP
```

### Conclusion

**Verdict: `INSUFFICIENT_EVIDENCE`.** A complete, exact point-in-time fee/margin schedule
for the six products over 2024-01-01..2025-12-31 is **not established** from verified
committed official evidence at this pass. Official SHFE sources are free/public in
principle (and were proven retrievable for the daily archives), but the fee/margin notice
values for the window are not yet collected and byte-bound, and automated retrieval was
blocked at research time.

Rules applied:
- `HISTORICAL_SCHEDULE_GAP` is recorded for the missing periods.
- **No current rate is backfilled into the past**; no synthetic-to-historical upgrade claim
  is made.
- A future bounded collection package may attempt to build the schedule by binding each
  official notice (URL, title, publication date, retrieved_at, sha256 of fetched bytes) and
  recording `HISTORICAL_SCHEDULE_GAP` where values cannot be fully recovered.

---

## E-07 — concrete-contract / main-contract research mapping rule

### Repository fact verification (confirmed)

- Canonical corpus stores **all** concrete contracts (`CANONICAL_DATASET_BALANCED_DEFINITION.md`:
  "PIT-complete listed concrete-contract universe, data-driven"; pseudo
  MAIN/CONTINUOUS rejected).
- `src/contract_semantics.py` `ContractMappingSchedule` is explicitly documented:
  "Explicit PIT schedule; it contains no contract-selection algorithm."
- `CURRENT_STATE.md`:
  `CONCRETE_CONTRACT_RESEARCH_MAPPING_RULE=NOT_FROZEN`,
  `E07_CONCRETE_CONTRACT_MAPPING_RULE=NOT_FROZEN_OWNER_GATED`.

**Confirmed:** the research mapping rule is **not frozen** in the repository.

### External formal authority

- **Exchanges do not define a single official "research main contract" rule.** SHFE (and
  the other Chinese futures exchanges) publish per-contract volume/open interest and
  settlement data and maintain margin/fee per contract, but none of them publishes an
  official unique main-contract mapping intended for research backtests. This was verified
  against the exchange's role as data publisher; no official rule was found. (Expected
  result confirmed, not assumed.)
- **TqSdk vendor convention** (official docs, `usage/mddatas.html`, retrieved 2026-08-20)
  defines its 主连 (`KQ.m@`):
  ```text
  天勤主力的选定标准为该合约持仓量和成交量均为最大后，在下一个交易日开盘后进行切换
  ```
  i.e., main = the contract whose **open interest AND volume are both the largest**, with
  the switch applied at the **next trading day's open**. This is a **vendor definition**
  (快期/TianQin), not an exchange rule, and it is only relevant to this project if the
  Owner adopts a source-governed vendor main-contract definition as the mapping rule.

### Verdict

**Verdict: `OWNER_DECISION_REQUIRED`.** No external formal authority defines the research
mapping rule for cu/al/ni/au/ag/rb. Owner options may only be **pre-outcome deterministic
rules**. Candidates (researched but NOT approved here) and their properties:

| Candidate rule | Required inputs | Point-in-time availability | Lookahead risk | Roll timing | Tie handling requirement | Current canonical observability |
| --- | --- | --- | --- | --- | --- | --- |
| Previous official trading day open-interest max | Per-concrete-contract daily open interest | Daily OI in SHFE official annual archives (verified) | None if prior-day only | Next tradable observation after the criterion day | Must define tie rule (e.g., nearest-to-expiry) | Available (per-contract daily OI present) |
| Previous official trading day volume max | Per-concrete-contract daily volume | Daily volume in SHFE official archives (verified) | None if prior-day only | Next tradable observation | Must define tie rule | Available |
| Predefined calendar roll | Fixed calendar rule + contract listing/expiry | Listing/expiry from official schedules (OFFICIAL_PARTIAL) | None if fully predefined | Per calendar rule | Defined by rule | Partially available (historical schedules need binding) |
| Volume/open-interest combination | Both series | As above | Depends on formula and window | Per rule | Must define | Available |
| Explicit vendor main-contract definition (source-governed) | Vendor `KQ.m@` rule or published mapping | Vendor publishes current 主连 and historical query (`query_his_cont_quotes`) | Vendor rule is PIT by construction; confirm no future data used | Vendor-defined (next-day-open switch) | Vendor-defined | Requires explicit adoption + governance of the vendor rule as project source |

No candidate was run over full data; no PnL-based selection was performed.

---

## E-08 — `available_capital` vs `available_resources` (margin admission)

### Repository state (confirmed)

- `src/validation_runner.py` `CapitalSnapshot`:
  ```text
  cash_balance         = starting_capital + realized_pnl - charged_costs
  equity               = cash_balance + unrealized_pnl
  available_capital    = cash_balance - reserved_margin          (excludes unrealized PnL)
  available_resources  = equity - reserved_margin                (includes unrealized PnL)
  ```
- The add/open margin admission check uses `current.available_capital`:
  `if current.available_capital < required_margin + required_cost: -> INSUFFICIENT_MARGIN`.
- The portfolio shared-capital policy is `SEQUENTIAL_AVAILABLE_CAPITAL`
  (`docs/evidence/MULTI_STRATEGY_PORTFOLIO_CONFLICT_SEMANTICS_VERIFICATION.md`), i.e., the
  portfolio sleeve path also consumes "available capital".
- **No repository document freezes** whether unrealized PnL may participate in margin
  admission. `CURRENT_STATE.md`:
  `E08_MARGIN_ADMISSION_RESOURCE_SEMANTICS=UNRESOLVED_FORMAL_AUTHORITY_REQUIRED`.

### A. Formal project authority

None found. The current code default (`available_capital`) is described as conservative in
the E-08 audit note, but no authority states it is the intended margin-admission resource.

### B. External formal futures margin / account-equity rules

- The China-futures account model (CTP convention, mirrored by TqSdk official docs
  `reference/tqsdk.objs.html`, retrieved 2026-08-20) defines:
  ```text
  balance   (账户权益/动态权益) = 静态权益 + 平仓盈亏 + 持仓盈亏 - 手续费 + 权利金 + 期权市值
  available (可用资金)         = 账户权益 - 冻结保证金 - 保证金 - 冻结权利金 - 冻结手续费 - 期权市值
  ```
  i.e., the real model's available funds are **equity-aware**: unrealized/floating PnL
  (`持仓盈亏`) is part of 账户权益, and available funds are equity minus occupied/frozen
  margin. This maps to the project's `available_resources` (`equity - reserved_margin`),
  not `available_capital`.
- **Important boundary:** exchange/clearing conventions describe the real account model;
  they do **not** automatically decide the project's **synthetic backtest account model**.
  The external rule is informative and maps cleanly to `available_resources`, but the
  project's own model choice is a project decision, not an external mandate.

### Verdict

**Verdict: `OWNER_DECISION_REQUIRED`.** The minimal Owner choice is:

```text
AVAILABLE_CAPITAL_ONLY              (cash - reserved_margin; unrealized PnL does NOT
                                     participate in margin admission; current code default)
EQUITY_AWARE_AVAILABLE_RESOURCES    (equity - reserved_margin; unrealized PnL participates;
                                     maps to the real CTP/TqSdk available-funds convention)
```

This choice **affects margin admission** (which opens/adds fill) and is therefore an
**outcome-affecting semantic**. The Owner decides; this package does not select.

---

## Source inventory

See `docs/evidence/PACKAGE_E_GOVERNANCE_SOURCE_INVENTORY_V0_1.json` for the
provenance/URL/hash inventory. Highlights:

- **TqSdk official documentation** (adopted scoped data/execution abstraction; free
  public, no login): `doc.shinnytech.com/tqsdk/latest/usage/trade.html`,
  `reference/tqsdk.api.html` (order `offset` semantics), `reference/tqsdk.objs.html`
  (Account equity/available formula, Position 今仓/昨仓 fields), `usage/mddatas.html`
  (主连 `KQ.m@` rule). Retrieved 2026-08-20; fetched-byte sha256 `NOT_RECORDED` this
  session (no full page bytes committed).
- **SHFE official product-spec pages** (free public): the six product pages referenced in
  `docs/evidence/CANONICAL_CONTRACT_SPECS.json` (with binding notices, effective periods,
  recorded `identity`). SHFE live site was bot-challenged at research time; existing
  recorded provenance reused.
- **SHFE official annual daily archives** (free public; proven retrievable):
  `docs/evidence/SHFE_OFFICIAL_RAW_RECHECK_MANIFEST.json` (URL + sha256 recorded) — daily
  OHLC/volume/OI reference only, not fee/margin.
- **SHFE official notice/regulation pages**: reference-only at this pass (blocked;
  fee/margin values not bound).

No third-party forum answer is used as binding authority. Third-party material was not
used to decide any finding.

---

## Owner decisions required

```text
E04_SPLIT_RULE_CHOICE   = OPTION_A | OPTION_B | OPTION_C   (Owner selects)
E05_PORTFOLIO_REPRESENTATION_CHOICE = per-member resolved-contract capital semantics vs
                                      other representations (Owner selects)
E07_MAPPING_RULE_CHOICE = one pre-outcome deterministic rule (Owner selects)
E08_RESOURCE_CHOICE     = AVAILABLE_CAPITAL_ONLY | EQUITY_AWARE_AVAILABLE_RESOURCES
                          (Owner selects)
```

Each is a new outcome-affecting semantic. None is selected by this package.

---

## Known gaps

- E-06: exact historical fee/margin values for 2024–2025 not bound; `HISTORICAL_SCHEDULE_GAP`
  recorded; no backfill; a dedicated collection package is required and its full recovery
  is not yet proven.
- E-04: the existing `generic_close_rule="TODAY_FIRST"` field is a code-level synthetic
  default, not an Owner-frozen semantic; the cross-bucket split is unimplemented and
  unresolved.
- E-07: historical listing/expiry schedules for the window are `OFFICIAL_PARTIAL` (would be
  needed by several candidate mapping rules).
- E-08: the real-world equity-aware convention maps to `available_resources` but the
  project synthetic account model choice is un-frozen.
- Retrieval limitation: SHFE live site bot-challenge at research time (2026-08-20); no new
  official notice bytes fetched this session.

---

## Machine block

```text
E04_STATUS=OWNER_DECISION_REQUIRED
E05_STATUS=OWNER_DECISION_REQUIRED
E06_STATUS=INSUFFICIENT_EVIDENCE
E07_STATUS=OWNER_DECISION_REQUIRED
E08_STATUS=OWNER_DECISION_REQUIRED

E06_HISTORICAL_FEE_MARGIN_SCHEDULE_BUILDABLE=NO
E07_MAPPING_RULE_ALREADY_FROZEN=NO
E08_RESOURCE_RULE_ALREADY_FROZEN=NO

OWNER_GATE_E04=YES
OWNER_GATE_E05=YES
OWNER_GATE_E07=YES
OWNER_GATE_E08=YES

PAID_SOURCE_USED=NO
LOGIN_SOURCE_USED=NO
CANDIDATE_OUTCOME_DATA_USED=NO
PRODUCTION_CODE_CHANGED=NO
```
