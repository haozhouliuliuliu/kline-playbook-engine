# 执行证据：TD-001 / TD-002 修复（Execution Evidence TD-001 / TD-002 Repair）

日期：2026-08-19
Lane：`parallel/execution-evidence-td001-td002-v01`（EXECUTION_EVIDENCE_TECH_DEBT_ENGINEER）
基线：`origin/main` = `03ae64e950f288854aa9450301d1bdc9ab538f97`
范围隔离：仅修复已记录的 TD-001 / TD-002 类缺陷；不实现 Playbook Contract（Lane B）、不做策略研究、不引入统计推断、不检查候选结果、不修改研究协议与防火墙权威、不重构无关组合架构。

## 结论

```text
TD001 = FIXED
TD002 = FIXED
SESSION_METADATA_SINGLE_TRADING_DAY_AUTHORITY = YES
NIGHT_SESSION_CROSS_MIDNIGHT_TEST = PASS
WEEK_ATTRIBUTION_TEST = PASS
PARTIAL_CLOSE_REMAINING_UNREALIZED = PASS
REALIZED_PNL_INVARIANCE = PASS
EQUITY_PATH_REGRESSION = PASS
FULL_CLOSE_TERMINAL_STATE = PASS
NO_CANDIDATE_OUTCOME_DATA_USED = YES
```

## TD-001 — 交易日判定必须只有单一权威

### 根因（root cause）

- `src/bootstrap_semantics.py` 中的可行性夹具 `NormalizedSessionCalendar.trading_day_at()`
  自行遍历 `TradingSession` 实现了一套与权威 `SessionMetadata.trading_day_at()`
  （`src/data_substrate.py`）平行但独立的交易日判定算法。
- 可信路径（`historical_data.py`、`portfolio_semantics.py`、`validation_runner.py`）
  当前都已调用 `SessionMetadata.trading_day_at()`，但 bootstrap 夹具保留第二个算法，
  形成“一个时间戳可能出现第二套交易日真相”的漂移风险（TD-001 记录原文）。
- 当时不存在基于官方交易日身份的周度归属能力；周度若被任何消费方按原始 civil
  时间戳自行推导，会与交易日身份产生系统性不一致（夜盘跨午夜时尤其明显）。

### 修复（files/functions changed）

- `src/data_substrate.py`
  - 新增 `SessionMetadata.trading_week_at(exchange, instrument, timestamp)`：
    先调用 `trading_day_at()` 得到官方交易日，再取该交易日的 ISO `(year, week)`。
    周度归属与交易日身份完全同源，绝不使用原始 civil 时间戳推导周。
- `src/bootstrap_semantics.py`
  - `NormalizedSessionCalendar.__init__` 现在把 `TradingSession` 显式转换为
    `SessionWindow` 并构造 `SessionMetadata`；`trading_day_at()` 与新增的
    `trading_week_at()` 全部委托给该 `SessionMetadata`。
  - 夹具不再包含任何独立的交易日/周判定算法；同一时间戳在夹具与权威路径得到
    完全相同的交易日与周。
  - `SessionConflict` 类保留仅为 API 兼容；冲突现在在 `SessionMetadata` 构造期
    （重叠窗口拒绝）即 fail closed，查询期不再可能到达冲突状态。

### 权威路径（TD-001 authoritative path）

```text
timestamp
  -> SessionMetadata.trading_day_at(exchange, instrument, timestamp)   # 唯一权威
       -> SessionWindow.contains(timestamp) -> window.trading_day
  -> SessionMetadata.trading_week_at(...)                              # 唯一权威
       -> trading_day_at(...) -> trading_day.isocalendar() -> (year, week)
```

- 夜盘跨 civil 午夜：21:00 前一工作日开市到次日凌晨的窗口显式绑定到其“为之开盘”的
  官方交易日（SHFE 规则）；`contains` 使用 `start <= ts < end` 的确定性边界。
- 周度归属：夜盘时间戳归属到官方交易日的 ISO 周，而不是 civil 日期所在的周
  （例如 2025-06-13（周五，civil week 24）21:30 属于交易日 2025-06-16（周一，week 25））。

### 回归覆盖（新增）

- `tests/test_bootstrap_semantics.py::TradingDayAuthorityTests`
  - 正常日盘时段；
  - 夜盘跨 civil 午夜（21:30 与 00:30 两个 civil 时刻都映射到 2025-06-16）；
  - 进入官方下一交易日的确定性边界（23:59 仍属夜盘，01:00 端点不属任何窗口）；
  - 周边界情形（周度归属跟随官方交易日身份）；
  - 同一事件在夹具与权威 `SessionMetadata` 得到相同交易日与周。
- `tests/test_data_substrate.py::test_trading_week_uses_official_trading_day_identity`

## TD-002 — 部分平仓后剩余持仓估值

### 根因（root cause）

- `src/validation_runner.py` 的 `ChronologicalValidationRunner._apply_capital_constraints()`
  CLOSE 分支中，部分平仓（`remaining_quantity > 0`）时用
  `unrealized_pnl=Decimal("0")` 构造剩余持仓快照（并更新 `position_request_id`）。
- 结果：部分平仓之后的中间 equity / unrealized PnL / drawdown/路径状态失真，
  直到下一次有效 mark 观测才重新估值。记录于 TD-002 原文。
- 已实现的 realized PnL 合计不是本缺陷（realized_pnl_change 始终由平仓成交价正确驱动）。

### 修复（files/functions changed）

- `src/validation_runner.py`
  - CLOSE 分支部分平仓路径：以本次平仓成交价 `outcome.fill_price` 作为该 transition
    的显式 mark price，计算剩余持仓的确定性未实现盈亏：
    `remaining_unrealized_pnl = (outcome.fill_price - average_open_price) * remaining_quantity * contract_multiplier * pnl_sign`
    并用该值替换原来的 `unrealized_pnl=Decimal("0")`。
  - 该值不是复制旧 mark 的陈旧数字：它是 transition 发生时真实成交价下的确定估值。
  - 无需新增 API 参数：CLOSE 成交价即显式 mark price，已是该路径既有输入。

### 部分平仓估值语义（TD-002 partial-close valuation semantics）

```text
OPEN (qty=Q0, avg=A, fill=P_open)
  -> PARTIAL CLOSE (qty=C, fill=Pc)
       realized_change  = (Pc - A) * C  * mult * sign
       remaining_unrealized = (Pc - A) * (Q0-C) * mult * sign   # 关键修复
       equity_after = cash_after + remaining_unrealized
  -> FULL CLOSE (remaining, fill=Pf)
       剩余 unrealized -> 0（flat snapshot，全部 realized）
```

- 在相同 mark price 下，“一次全平”与“部分平仓再全平”得到相同 equity
  （无因部分平仓这一事件本身产生的伪跳变）。
- `equity = cash/realized + 当前开仓估值`（沿用既有 `CapitalSnapshot.equity` 语义）。

### 保持的不变量（invariants preserved）

- `realized_pnl` 完全不受未实现修复影响（仅由平仓成交价驱动）。
- 交易成本语义不变：`total_cost = synthetic_fee + 每单位 close offset fee`。
- 全平（`remaining_quantity == 0`）仍产出 flat `CapitalSnapshot`：
  `position_quantity=0`、`unrealized_pnl=0`、`reserved_margin=0`、`average_open_price=0`、
  无持仓绑定。
- 剩余数量与 today/previous bucket 正确保留；`position_request_id` 按既有语义更新为
  平仓订单 id。
- 最小生命周期中“mark 之后不可再经 `_apply_capital_constraints` 追加订单”的既有规则
  未改变；部分平仓本身不写入 `latest_mark_reference`。
- 部分平仓后的后续 mark 对剩余数量（而非平仓前总量）重估值（新增测试覆盖）。

### 回归覆盖（新增，`tests/test_position_capital_lifecycle.py`）

- `test_partial_close_preserves_remaining_quantity_and_revalues_remaining`（LONG，OPEN→PARTIAL→FULL）
- `test_optional_add_then_partial_close_preserves_correct_remaining_quantity`（OPEN→ADD→PARTIAL→FULL）
- `test_short_partial_close_favorable_mark_is_consistent`（SHORT 有利 mark）
- `test_adverse_partial_close_leaves_negative_remaining_unrealized`（不利 mark，未实现为负）
- `test_partial_close_does_not_create_artificial_equity_jump`（零成本下 equity 无伪跳变）
- `test_realized_pnl_and_transaction_costs_unaffected_by_unrealized_fix`
- `test_later_mark_after_partial_close_revalues_remaining_quantity`

## 测试

```text
python -m unittest discover -s tests -v
```

- 本 lane 修改/新增相关测试均通过。
- 全量回归保持 green（见提交时的最终结果）。

## 残留限制（residual limitation）

- 周度归属采用官方交易日的 ISO `(year, week)`。若未来需要交易所特定“周/结算周”
  定义，必须在正式 authority 中以版本化事实显式提供；本 lane 不做猜测。
- 最小生命周期对“已 mark 持仓不可再经普通订单路径追加/平仓”的既有限制保持不变；
  本 lane 只修复部分平仓瞬时未实现盈亏清零，不扩展生命周期能力。
- 不修改 `CURRENT_STATE.md`；本证据仅记录已完成的 TD-001/TD-002 修复。
