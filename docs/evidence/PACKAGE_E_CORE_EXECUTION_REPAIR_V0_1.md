# 执行证据：Package E 核心执行修复（PACKAGE_E_CORE_EXECUTION_REPAIR_V0_1）

日期：2026-08-20
任务：`PACKAGE_E_CORE_EXECUTION_REPAIR_V0_1`（production repair）
Lane：`repair/package-e-core-execution-v01`
基线：`origin/main` = `18a28c311a13dd531a6b62600838365f9090c7eb`
Preflight：`prep/package-e-execution-reproduction-v01` = `5f77f279181fe7fe9c385017ee92f93cf4ca204c`
Reproduction authority：`docs/evidence/PACKAGE_E_EXECUTION_DEFECT_REPRODUCTION_V0_1.md`
Repair-plan authority：`docs/reviews/FULL_PROJECT_SECOND_PASS_REPAIR_PLAN_V0_1.md`、`docs/reviews/CDF_CORRECTION_REVIEW_AND_NEXT_PARALLEL_PLAN_V0_1.md`

## 范围（Scope）

本包只处理以下 findings（修复语义已由现有行为/证据决定）：

```text
E-01  E-02  E-03  E-09  E-11  E-12  E-13
```

明确不处理（本包之外）：

```text
E-04 = NOT_TOUCHED
E-05 = NOT_TOUCHED
E-08 = NOT_TOUCHED
E-10 = WAIT_ACCEPTED_D05
```

原因（与 CDF 评审一致）：

- E-04 generic CLOSE 跨 today/previous 拆分分配与费用语义需要 authority 决策，未授权；
- E-05 异构合约乘数组合表示需要先规范，未授权；
- E-08 margin admission 资源语义（`available_capital` vs `available_resources`）未冻结，未授权；
- E-10 依赖 accepted D-05 session identity 进入 main 后，等待中；
- E-06 / E-07 是治理/研究 prerequisites，不在本包。

## 总体原则

- 未重构 execution engine；未新增 execution framework / position service / event bus /
  accounting subsystem / generic fee engine / repository abstraction。
- 未打开 Portfolio candidate outcome path；未使用任何 real candidate outcome 数据。
- `CURRENT_STATE.md` 未修改；未 push `main`；无 frozen protocol 变更。

```text
PRODUCTION_CODE_CHANGED=YES (scoped)
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CURRENT_STATE_CHANGED=NO
PORTFOLIO_CANDIDATE_PATH_REOPENED=NO
```

---

## E-01 — ADD 后正确重估 unrealized PnL

### Root cause

`ChronologicalValidationRunner._apply_capital_constraints` 的 OPEN/ADD 分支无条件构造
`CapitalSnapshot(..., unrealized_pnl=Decimal("0"), ...)`。当向已开仓位 ADD 时，旧 tranche
在本次明确可观察 fill price 下已存在 unrealized PnL；清零会在 equity path 引入虚假中间零，
并可能抹掉前序 mark/partial-close 携带的非零 unrealized（依赖 TD-002 重估）。

### Minimum fix

- 仅当 `current.position_quantity > 0`（即 ADD）时，以本次 fill price `P` 作为明确可观察
  fill mark，先计算 `next_quantity` 与 `next_average_open_price`，再：
  - LONG：`(P - next_average_open_price) * next_quantity * contract_multiplier`
  - SHORT：`(next_average_open_price - P) * next_quantity * contract_multiplier`
  该值精确等于“旧 tranche 在新 fill price 的 unrealized + 新 tranche 的 0”。
- `current.position_quantity == 0` 时新 OPEN 仍为 `unrealized_pnl=0`（行为不变）。
- 未直接复制 `current.unrealized_pnl`（可能对应旧 mark）；未创建新 `MarkObservation`；
  未修改“cannot add after mark-to-market”guard。

### New invariant

```text
ADD_AFTER_OPEN_REMARKS_AT_FILL_PRICE=YES
EQUITY_PATH_NO_SPURIOUS_INTERMEDIATE_ZERO_AFTER_ADD=YES
FRESH_OPEN_UNREALIZED_ZERO=YES
```

### Tests（`tests/test_validation_runner.py::PackageECoreExecutionRepairTests`）

- LONG：1 @100，ADD 1 @110 → avg 105 → unrealized = +10（multiplier 1）。
- SHORT 镜像：1 @100，ADD 1 @90 → avg 95 → unrealized = +10。
- 新 OPEN 仍为 0。
- 已 mark（carry +10、mark reference 未设）后 ADD @110 → 保持 +10，不被清零。

---

## E-02 — forced liquidation 可进入下一个 official trading day

### Root cause

`_evaluate_forced_liquidation` 检查 `trading_day != snapshot.position_trading_day` 即抛错。
session 尾部 breach 后，下一 trading day 第一个可交易 observation 会被拒绝；且该路径无
today/previous bucket aging。

### Minimum fix

- 用 `session_metadata.trading_day_at(...)` 得到 `observation_trading_day`。
- 规则：
  - `observation_trading_day is None` → fail；
  - `observation_trading_day < snapshot.position_trading_day` → fail；
  - 相等：正常；
  - 大于：允许，并把 snapshot 的 `today_quantity` 全部 age 到 `previous_quantity`
    （与普通 order-processing 跨 trading-day aging 语义一致）。
- 记录 `aged_quantity = 原 today_quantity`；不生成新的隐式 position；不做 civil-date 推断。

### New invariant

```text
FORCED_LIQUIDATION_CROSS_OFFICIAL_DAY=ALLOWED_WITH_ORDINARY_AGING
FORCED_LIQUIDATION_AGED_QUANTITY=RECORDED
FORCED_LIQUIDATION_NO_IMPLICIT_POSITION=YES
```

### Tests（`tests.test_contract_execution_semantics.ForcedLiquidationCrossDayOffsetRepairTests`）

- D1 breach → D2 下一可交易 observation → forced liquidation 成功；
- `aged_quantity` 正确（D1→D2 全 today → previous）。

---

## E-03 — forced liquidation offset fees

### Root cause

contract-bound forced liquidation 只收 synthetic execution fee，未应用
`OffsetCostAssumptions`，未解析 close-today/close-previous cost 语义；`resolved_close_offset`
与 `offset_cost_assumption_id` 均未设置，round-trip charged costs 不完整。

### Minimum fix

- contract-bound forced liquidation 必须接收 `OffsetCostAssumptions`；若
  `contract.offset_fee_metadata_identity != assumptions.identity_id` → fail closed。
- full liquidation 一定关闭全部 position；用 E-02 aging 后的 effective buckets：

  ```text
  offset_fee = today_quantity * close_today_fee_per_unit
             + previous_quantity * close_previous_fee_per_unit
  total_cost = execution_assumptions.synthetic_fee + offset_fee
  ```

- 解析：
  - today > 0, previous == 0 → `CLOSE_TODAY`；
  - today == 0, previous > 0 → `CLOSE_PREVIOUS`；
  - today > 0, previous > 0 → `CLOSE`（full forced liquidation 同时清两 bucket；
    不为它新增第三套 split object）。
- `ExecutionOutcome` 记录 `total_cost` / `resolved_close_offset` / `offset_cost_assumption_id`；
  `CapitalTransition` 记录 `required_cost=total_cost` / `aged_quantity` /
  `resolved_close_offset` / `offset_cost_assumption_id`；
  next flat snapshot `charged_costs += total_cost`（不只加 synthetic fee）。

### New invariant

```text
FORCED_LIQUIDATION_OFFSET_FEE=APPLIED_TO_EFFECTIVE_BUCKETS
FORCED_LIQUIDATION_OFFSET_ASSIGNMENT_FAIL_CLOSED=YES
FORCED_LIQUIDATION_TOTAL_COST_INCLUDES_OFFSET_FEE=YES
ROUND_TRIP_CHARGED_COSTS_COMPLETE_FOR_FORCED_LIQUIDATION=YES
```

### Tests（`tests.test_contract_execution_semantics.ForcedLiquidationCrossDayOffsetRepairTests`）

- today-only fee：同日清算 → `CLOSE_TODAY`，total_cost = 0.25 + 1×1。
- previous-only fee / D1→D2 aging 后全 previous：`CLOSE_PREVIOUS`，total_cost = 0.25 + 1×2。
- mixed full-position fee：today=1 且 previous=1 → `CLOSE`，total_cost = 0.25 + 1×1 + 1×2。
- offset assumption mismatch → fail closed（`offset-cost assumption identity is inconsistent`）。

---

## E-09 — duplicate ExecutionOutcome request_id fail closed

### Root cause

`RoundTripMaterializer.materialize` 用 dict comprehension 直接把 `execution_outcomes`
按 request_id 建 dict，重复 request_id 被静默 last-wins 覆盖，在 cost cross-check 前丢证据。

### Minimum fix

- 先 `tuple(execution_outcomes)`，逐个检查 request_id 唯一；只要重复即
  `raise ValueError("duplicate execution outcome request_id")`（即使两个 outcome 完全相同
  也直接 reject；不 last-wins、不 first-wins）。然后再构造 dict。

### New invariant

```text
DUPLICATE_EXECUTION_OUTCOME_REQUEST_ID=REJECTED
NO_LAST_WINS_NO_FIRST_WINS=YES
```

### Tests（`tests.test_round_trip_ledger.PackageECoreRepairTests`）

- 同 request_id 不同 total_cost → reject；
- 同 request_id 完全相同 outcome → 也 reject。

---

## E-11 — completed round trips 改成真实 chronology

### Root cause

`RoundTripLedger.__post_init__` 强制 lexical position_id 排序，`materialize` 也按
position_id 排序；这是确定性但不是交易时间顺序。

### Minimum fix

- 统一 canonical order（单一半径 helper `_completed_trip_order_key`，两边共用）：
  `(terminal_closed_at, opened_at, position_id)`。
- `RoundTripMaterializer.materialize` 与 `RoundTripLedger.__post_init__` 使用同一个
  helper/key，不复制两份不同排序规则。

### New invariant

```text
COMPLETED_ROUND_TRIP_ORDER=CHRONOLOGICAL_BY_TERMINAL_CLOSE_THEN_OPENED_THEN_ID
ORDERING_KEY_SHARED_BY_MATERIALIZER_AND_LEDGER=YES
TIE_CASE_DETERMINISTIC=YES
```

### Tests（`tests.test_round_trip_ledger.PackageECoreRepairTests`）

- z-position 10:00 完成、a-position 11:00 完成 → 顺序必须 z, a。
- tie case（同 terminal close）→ opened_at → position_id 确定性。
- `RoundTripLedger.__post_init__` 拒绝非 chronology 顺序。

---

## E-12 — open position identity 绑定实际 transition evidence

### Root cause

`RoundTripLedger.identity_id` 只绑定 `open_position_ids`（字符串）；open position 的数量/
均价/成本/状态变化不会改变 ledger identity，同一 position_id 的不同证据流得到相同 identity。

### Minimum fix

- 保留 `open_position_ids`；新增最小 immutable evidence 字段
  `open_position_evidence_identities: tuple[tuple[str, str], ...]`，每项
  `(position_id, evidence_identity)`，按 position_id 排序。
- `evidence_identity = hash({"position_id", "source_transition_references"})`（有序 source
  transition refs）。因 `CapitalTransition.reference_id` 已绑定 before/after
  `CapitalSnapshot`，quantity / average price / cost / state 变化都进入该 identity；
  不复制整份 CapitalSnapshot 进 ledger。
- `RoundTripLedger.identity_id` 绑定：completed trip identities + open position evidence
  identities（不只 open IDs）。
- 验证：`open_position_ids` 与 `open_position_evidence_identities` 中的 ids 完全一致。

### New invariant

```text
OPEN_POSITION_EVIDENCE_BOUND_IN_LEDGER_IDENTITY=YES
OPEN_POSITION_IDS_MATCH_EVIDENCE_IDS=ENFORCED
NO_FULL_CAPITAL_SNAPSHOT_COPY_INTO_LEDGER=YES
```

### Tests（`tests.test_round_trip_ledger.PackageECoreRepairTests`）

- 同一 open position id、不同 transition evidence（数量/均价不同）→ ledger identity 不同；
- evidence identities 存在且不同；
- `open_position_ids` 与 evidence ids 不一致 → fail closed。

---

## E-13 — bootstrap chronology barrier

注意：这只修复 `bootstrap_semantics.TradingState` 这一 feasibility fixture，不冒充
production Trading Loop。

### Root cause

`TradingState.ingest` / `_expected_sequence` 只按 trading_day 独立跟踪 sequence；新一天的
sequence 可在前一天仍有 buffered gap 时应用，且缺失的前一天事件可在未来一天状态已应用后
再 mutate 共享 position。

### Minimum fix

- 新增 `_latest_applied_trading_day` tracking；保留现有 same-day sequence logic。
- 规则：
  - A. `event.trading_day < latest_applied_trading_day` → reject late prior-day event；
  - B. `event.trading_day > latest_applied_trading_day` 且任意更早 trading day 仍有
    buffered sequence gap → 不允许应用 future day，fail closed；
  - C. 只有之前 day 无 buffered gap 才允许新 trading day 开始。
- 未做 global event bus；新增 `CrossTradingDayConflict(ValueError)`。

### New invariant

```text
D1_GAP_BLOCKS_D2=FAIL_CLOSED
LATE_D1_AFTER_D2=REJECTED
SAME_DAY_SEQUENCE_BEHAVIOR=PRESERVED
BOOTSTRAP_FIXTURE_ONLY=YES
```

### Tests（`tests.test_bootstrap_semantics.CrossTradingDayChronologyBarrierTests`）

- D1 seq1 applied、D1 seq3 buffered、D2 seq1 → 必须在 D2 处 fail closed；补上 D1 gap 后 D2 正常；
- D1 complete、D2 seq1 applied 后 D1 late event → reject；
- same-day sequence behavior（buffered then applied）保留。

---

## 保持不变（explicitly unchanged）

```text
E04_GENERIC_CLOSE_SPLIT=NOT_TOUCHED
E05_PORTFOLIO_HETEROGENEOUS_MULTIPLIERS=NOT_TOUCHED
E08_AVAILABLE_CAPITAL_VS_AVAILABLE_RESOURCES=NOT_TOUCHED
E10_ROUND_TRIP_SESSION_AUTHORITY_IDENTITY=WAIT_ACCEPTED_D05
PORTFOLIO_CANDIDATE_OUTCOME_PATH=NOT_IMPLEMENTED_FAIL_CLOSED
```

未修改 `src/portfolio_semantics.py`；`PortfolioCoordinator` candidate-outcome path 保持
`NOT_IMPLEMENTED` / fail closed。

## 变更文件（changed files）

```text
src/validation_runner.py          E-01 E-02 E-03
src/round_trip_ledger.py          E-09 E-11 E-12
src/bootstrap_semantics.py        E-13
tests/test_validation_runner.py   E-01 tests
tests/test_contract_execution_semantics.py  E-02 E-03 tests
tests/test_round_trip_ledger.py   E-09 E-11 E-12 tests
tests/test_bootstrap_semantics.py E-13 tests
```

## 验证（verification）

```text
FOCUSED_TESTS=119_PASS
FULL_TESTS=374_PASS
COMPILEALL=0
DIFF_CHECK=0
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CURRENT_STATE_CHANGED=NO
MAIN_PUSHED=NO
```

## 结论

```text
STATUS=COMPLETE
E01_ADD_UNREALIZED_REMARK=FIXED
E02_FORCED_LIQUIDATION_CROSS_DAY=FIXED
E03_FORCED_LIQUIDATION_OFFSET_FEES=FIXED
E09_DUPLICATE_OUTCOME_REJECTED=FIXED
E11_COMPLETED_ORDER_CHRONOLOGICAL=FIXED
E12_OPEN_EVIDENCE_BOUND_IN_LEDGER_ID=FIXED
E13_BOOTSTRAP_CROSS_DAY_BARRIER=FIXED
E04_CHANGED=NO
E05_CHANGED=NO
E08_CHANGED=NO
E10_CHANGED=NO
PORTFOLIO_CANDIDATE_PATH_REOPENED=NO
```
