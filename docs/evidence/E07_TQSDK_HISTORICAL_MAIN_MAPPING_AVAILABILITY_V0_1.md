# E07 TqSdk Historical Main Mapping — Availability Assessment V0.1

> Task: `E07_TQSDK_HISTORICAL_MAIN_MAPPING_PROVENANCE_V0_1`
> Role: source / provenance availability assessment ONLY. NOT a strategy backtest.
> NOT mapping-rule research. NOT production implementation.
> Date: 2026-08-20
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Branch: `research/e07-tqsdk-main-mapping-provenance-v01`
> Baseline: `origin/main` @ `1cb7ff7`
> Owner rule authority: `docs/reviews/PACKAGE_E_OWNER_DECISION_APPROVAL_2026-08-20.md`

```text
E07_MAPPING=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
SOURCE_POLICY=FREE_PUBLIC_UNAUTHENTICATED_FIRST
PAID_SOURCE_USED=NO
LOGIN_SOURCE_USED=NO
ACCOUNT_CREATION_USED=NO
OWNER_ACCOUNT_USED=NO
CAPTCHA_BYPASS_USED=NO
ACCESS_CONTROL_BYPASS_USED=NO
PSEUDO_MAIN_PRICE_BARS_DOWNLOADED=NO
CANDIDATE_OUTCOME_DATA_USED=NO
PRODUCTION_CODE_CHANGED=NO
```

## 1. Result summary

```text
TQSDK_HISTORY_ACCESS=LOGIN_REQUIRED
E07_MAPPING_COMPLETENESS=INCOMPLETE
E07_RUNTIME_MAPPING_STATUS=FAIL_CLOSED_PREREQUISITE
E07_COMPLETE_MAPPING_ARTIFACT_CREATED=NO
E07_JSON_MAPPING_EMPTY_FABRICATED=NO
```

The source-governed TqSdk historical main-contract mapping for
`cu/al/ni/au/ag/rb` over `2024-01-01..2025-12-31` **cannot be obtained** under the
project's `FREE_PUBLIC_UNAUTHENTICATED_FIRST` source policy, because the only
TqSdk interface that returns the vendor's point-in-time historical main mapping
(`TqApi.query_his_cont_quotes`) requires an authenticated `TqApi` session bound to a
registered 快期账户 (TianQin/Shinny account) via `TqAuth(account, password)`.

Per the Owner-approved rule, the project must **FAIL CLOSED** and record this
prerequisite. It must **not** substitute a project-authored OI/volume/calendar/PnL
mapping rule.

```text
E07_FAIL_CLOSED_OWNER_RULE=NOT_SUBSTITUTED_WITH_PROJECT_AUTHORED_MAPPING
```

## 2. Binding Owner rule (already frozen; not re-selected here)

Authority: `docs/reviews/PACKAGE_E_OWNER_DECISION_APPROVAL_2026-08-20.md`.

```text
E07_STATUS=OWNER_APPROVED_BINDING
E07_MAPPING=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
E07_PSEUDO_MAIN_PRICE_BARS_IN_CANONICAL_CORPUS=FORBIDDEN
E07_OUTCOME_BASED_MAPPING_SELECTION=FORBIDDEN
```

The adopted research mapping direction is a **source-governed historical TqSdk
main-contract mapping / documented `KQ.m@` convention**, applied only to select the
project's canonical concrete-contract bars. Pseudo-main price bars must not enter the
canonical corpus. Mapping must be point-in-time and apply only at the source-defined
next-trading-day switch, and exact historical mapping provenance must be recorded.

If complete historical source-governed mapping cannot be obtained under the
free/public/no-login source policy or cannot be provenance-bound, the project must
**fail closed** and return to the Owner. It must not substitute a project-tuned
OI/volume rule and must not choose a rule using outcomes.

The following **forbidden substitutes** were NOT used:

```text
PREVIOUS_DAY_OI_MAX_SUBSTITUTE=FORBIDDEN_NOT_USED
PREVIOUS_DAY_VOLUME_MAX_SUBSTITUTE=FORBIDDEN_NOT_USED
SELF_WRITTEN_OI_PLUS_VOLUME_FORMULA_SUBSTITUTE=FORBIDDEN_NOT_USED
CALENDAR_ROLL_SUBSTITUTE=FORBIDDEN_NOT_USED
PNL_SELECTED_MAPPING_SUBSTITUTE=FORBIDDEN_NOT_USED
```

Even though the underlying volume/OI data are present in the canonical corpus, they
are **not** an acceptable substitute for the source-governed mapping artifact.

## 3. TqSdk vendor definition (official, recorded)

The existing formal research already confirmed that TqSdk `KQ.m@` is the vendor
main-contract convention and that mapping switches use the vendor's own
point-in-time historical mapping semantics. Confirmed against official TqSdk
documentation (retrieved 2026-08-20):

- `KQ.m@` 主连 (main) contracts are vendor-maintained continuous instruments under the
  vendor `KQ` exchange. Symbol form: `KQ.m@SHFE.cu` (product main). Reference:
  `doc.shinnytech.com/tqsdk/latest/usage/mddatas.html` (合约, 行情和历史数据).
- Vendor main-selection rule (official): "天勤主力的选定标准为该合约持仓量和成交量
  均为最大后，在下一个交易日开盘后进行切换" — main = the contract whose open interest
  **and** volume are both the largest, with the switch applied at the **next trading
  day's open**. Reference: `usage/mddatas.html` (天勤主力 selection).
- The historical main mapping is exposed by `TqApi.query_his_cont_quotes(symbol, n)`,
  which returns, per effective date, the 标的 (underlying concrete) contract for each
  主连 symbol. This is the vendor's source-governed point-in-time mapping. Reference:
  `doc.shinnytech.com/tqsdk/latest/reference/tqsdk.api.html`.

The project does **not** recompute a "close-enough KQ.m@" from volume/OI; the target is
the source-governed mapping artifact.

## 4. Source policy

Strict policy applied (unchanged from project authority):

```text
FREE_PUBLIC_UNAUTHENTICATED_FIRST
PAID_SOURCE_PURCHASE=FORBIDDEN
SUBSCRIPTION=FORBIDDEN
LOGIN=FORBIDDEN
PAID_ACCOUNT_CREATION=FORBIDDEN
OWNER_ACCOUNT_USE=FORBIDDEN
CAPTCHA_BYPASS=FORBIDDEN
ACCESS_CONTROL_BYPASS=FORBIDDEN
```

No login, no account creation, no paid account, no borrowed Owner account, no captcha
bypass, and no access-control bypass was performed for this package.

## 5. Availability determination

### 5.1 TqSdk access requires an authenticated 快期账户

Official TqSdk documentation (retrieved 2026-08-20) states unambiguously:

> "在使用 TqSdk 之前，用户需要先注册自己的 快期账户 ，传入快期账户是使用任何 TqSdk
> 程序的前提" — Before using TqSdk, users must first register their own 快期账户; passing
> the 快期账户 is a prerequisite for using **any** TqSdk program.
> Reference: `doc.shinnytech.com/tqsdk/latest/usage/shinny_account.html`.

Every documented data-access entry point, including `query_his_cont_quotes`, requires a
`TqApi` instance constructed with `auth=TqAuth("快期账户", "账户密码")`, where the `auth`
parameter is documented as **必填** (required). Reference:
`doc.shinnytech.com/tqsdk/latest/reference/tqsdk.api.html`.

### 5.2 The historical main mapping API is bound to that authenticated session

`TqApi.query_his_cont_quotes(symbol, n)` is a **method of the authenticated `TqApi`
object**. There is no documented free/public/unauthenticated endpoint or static artifact
that returns the complete vendor point-in-time historical main mapping for the target
products/window. The official docs describe the `KQ.m@` selection rule in prose but do
not publish a downloadable full historical mapping artifact.

### 5.3 Repository self-evidence (consistent)

The project's own `TqSdkSourceAdapter` (`src/historical_acquisition.py`) constructs
`TqAuth(account, password)` and opens `TqApi(auth=auth, ...)` for data access, reading
credentials at runtime only (hidden password input). No credential is stored in the repo.
This confirms that TqSdk data access in this project's own machinery already requires an
authenticated account; the same login requirement applies to the historical main-mapping
API.

### 5.4 Conclusion

Because the only source-governed historical mapping interface requires login
(authentication against a registered 快期账户), and login/account use is forbidden by the
project's strict policy and by this package's explicit instructions, the mapping was
**not retrieved**. Per the Owner rule, this is a **FAIL CLOSED** prerequisite.

```text
TQSDK_HISTORY_ACCESS=LOGIN_REQUIRED
E07_MAPPING_COMPLETENESS=INCOMPLETE
E07_RUNTIME_MAPPING_STATUS=FAIL_CLOSED_PREREQUISITE
```

No `E07_TQSDK_HISTORICAL_MAIN_MAPPING_V0_1.json` was created, because a complete
source-governed mapping was not obtained. No empty/placeholder mapping JSON is fabricated
to masquerade as COMPLETE.

## 6. Provenance and evidence quality

- Official TqSdk pages consulted (rendered content), retrieved 2026-08-20:
  - `https://doc.shinnytech.com/tqsdk/latest/usage/mddatas.html`
  - `https://doc.shinnytech.com/tqsdk/latest/usage/shinny_account.html`
  - `https://doc.shinnytech.com/tqsdk/latest/reference/tqsdk.api.html`
- Repository self-evidence: `src/historical_acquisition.py` `TqSdkSourceAdapter`
  (`TqApi(auth=TqAuth(account, password), ...)`).
- Because this package fetched rendered documentation (not exact raw response bytes), no
  fetched-byte `sha256` was recorded and no `EXACT_BYTES_BOUND` claim is made.

```text
DOC_FETCHED_BYTE_SHA256=NOT_RECORDED
EXACT_BYTES_BOUND=NO
PROVENANCE_LIMITATION=FETCHED_RENDERED_DOCS_NOT_RAW_RESPONSE_BYTES
```

No strategy/PnL/Sharpe/win-rate/entry-count output was read or produced. No candidate
outcome was consulted. No mapping comparison was performed.

## 7. Canonical universe cross-check

Because no source-governed mapping was retrieved, no
`MAPPING_CONTRACT_NOT_IN_CANONICAL_UNIVERSE` fact was produced and no contract was
silently substituted. The canonical universe facts are unchanged:

```text
CANONICAL_PRODUCTS=cu,al,ni,au,ag,rb
CANONICAL_COVERAGE=2024-01-01..2025-12-31
CANONICAL_CONCRETE_CONTRACTS=212
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
```

A future authenticated retrieval would need to cross-check each mapped concrete contract
against this canonical universe and record `MAPPING_CONTRACT_NOT_IN_CANONICAL_UNIVERSE`
rather than substituting another contract.

## 8. Switch timing

No mapping was retrieved, so no switch-timing decision was applied. The vendor's
source-defined `next-trading-day` switch (not the selection-criterion day) remains the
required timing if and when a complete source-governed mapping is obtained under an
authorized path. No civil-date guessing was performed.

## 9. What would be required to reach COMPLETE (Owner-gated, NOT performed)

Obtaining a complete source-governed mapping for the six products over the window
requires an authenticated `TqApi` session with a registered 快期账户 and the
`query_his_cont_quotes` interface (or an equivalent official vendor interface). This
requires account login / registration, which is **forbidden** by the project's
`FREE_PUBLIC_UNAUTHENTICATED_FIRST` policy and by this package's explicit instructions.
Any such acquisition would require explicit Owner authorization, would have to bind
exact response bytes / canonicalized hashes, and would have to preserve the
source-defined next-trading-day switch.

```text
E07_COMPLETE_REQUIRES=AUTHENTICATED_TQSDK_SESSION_OWNER_GATED
E07_ACQUISITION_PERFORMED=NO
```

## 10. Artifacts produced by this package

```text
E07_AVAILABILITY_ASSESSMENT=docs/evidence/E07_TQSDK_HISTORICAL_MAIN_MAPPING_AVAILABILITY_V0_1.md
E07_COMPLETE_MAPPING_JSON=NOT_CREATED
SRC_DIFF=0
```

This package modifies **no** `src/*.py`, no authority/state file, and no frozen
protocol. It does not implement any runtime `ContractMappingSchedule` adapter; that
remains a future package and is gated on a complete source-governed mapping under an
authorized path.
