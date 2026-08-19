# 已完成往返持仓账本 工程证据（Completed Round-Trip Ledger Engineering Evidence）

日期：2026-08-20
Lane：`parallel/completed-round-trip-ledger-v01`（COMPLETED_ROUND_TRIP_LEDGER_ENGINEER）
基线：`origin/main` = `2b197f9b1a72471cbd338e6392d920bf48b58cd1`
范围隔离：仅实现通用已完成往返持仓账本基础设施；不实现策略研究、候选回测、统计推断、
Playbook 语义、排名逻辑；不耦合 Raschke/Grimes 或任何候选族；不锁定统计阈值；
不使用候选结果数据；不修改 `CURRENT_STATE.md`。

## 结论

```text
ROUND_TRIP_LEDGER=IMPLEMENTED
ONE_POSITION_ID_ONE_ROUND_TRIP=PASS
ADDS_AGGREGATED=PASS
PARTIAL_CLOSES_AGGREGATED=PASS
FORCED_LIQUIDATION_TERMINAL=PASS
PARTIAL_CLOSE_N_INFLATION_PREVENTED=PASS
REALIZED_PNL_AGGREGATION=PASS
COST_SINGLE_AUTHORITY=PASS
SESSION_METADATA_DAY_WEEK=PASS
INCOMPLETE_POSITION_NOT_COMPLETED=PASS
DETERMINISTIC_IDENTITY=PASS
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

## 已实现（Implemented）

- 新增 `src/round_trip_ledger.py`：
  - `CompletedRoundTrip`（不可变已完成往返记录）；
  - `RoundTripLedger`（不可变容器：已完成往返 + 仍未完成持仓 id 集合）；
  - `RoundTripMaterializer`（按 `position_id` 分组既有权威转换流并聚合）。
- 新增 `tests/test_round_trip_ledger.py`：25 个合成测试，全部通过。
- 新增 `docs/architecture/COMPLETED_ROUND_TRIP_LEDGER_V0_1.md`（架构说明）。

## 绑定身份规则（Binding identity rule）

```text
ONE position_id == ONE completed round trip
```

ADD 与部分平仓属于同一往返；部分平仓绝不单独计为一次交易。这是避免下游 N 膨胀的核心不变量。

## 权威路径（Authoritative paths）

```text
gross_realized_pnl = Σ CapitalTransition.realized_pnl_change   # 平仓/强平转换
charged_costs      = Σ CapitalTransition.required_cost         # 唯一加性成本权威
official day       = SessionMetadata.trading_day_at(...)        # TD-001 单一交易日权威
official week      = SessionMetadata.trading_week_at(...)       # 周度归属源自官方交易日身份
ledger_identity    = sha256(ordered transition/outcome refs)    # 确定性身份
```

- 成本单一权威：`CapitalTransition.required_cost`；`ExecutionOutcome.total_cost`
  仅作为交叉校验，出现不一致即失败关闭，绝不作为第二求和路径。
- 滑点已内嵌于成交价 / 毛已实现盈亏，不再作为费用重复计入。
- 周度归属使用官方交易日身份而非原始 civil 时间戳；夜盘跨 civil 午夜正确映射。

## 要求的合成测试覆盖（Required synthetic test coverage）

| # | 要求 | 测试 | 结果 |
| --- | --- | --- | --- |
| 1 | OPEN → FULL CLOSE = 恰好 1 个往返 | `test_open_full_close_is_exactly_one_round_trip` | PASS |
| 2 | OPEN → ADD → FULL CLOSE = 恰好 1 个往返 | `test_open_add_full_close_is_exactly_one_round_trip` | PASS |
| 3 | OPEN → PARTIAL CLOSE → FULL CLOSE = 恰好 1 个往返 | `test_open_partial_close_full_close_is_exactly_one_round_trip` | PASS |
| 4 | OPEN → ADD → 多次 PARTIAL CLOSE → FULL CLOSE = 恰好 1 个往返 | `test_open_add_multiple_partial_closes_full_close_is_exactly_one_round_trip` | PASS |
| 5 | 强平 = 终局已完成往返且带强平标记 | `test_forced_liquidation_is_terminal_completed_round_trip` | PASS |
| 6 | 多空 | `test_long_and_short_round_trips` | PASS |
| 7 | 部分平仓不膨胀交易计数 | `test_partial_closes_do_not_inflate_trade_count` | PASS |
| 8 | 毛已实现盈亏等于权威已实现转换之和 | `test_gross_realized_pnl_equals_aggregation_of_authoritative_realized_transitions` | PASS |
| 9 | 成本恰好计一次 | `test_cost_charged_exactly_once` | PASS |
| 10 | 全平数量身份平衡 | `test_full_close_total_quantity_identity_is_balanced` | PASS |
| 11 | 进出场交易日使用 SessionMetadata | `test_entry_and_exit_trading_day_use_session_metadata` | PASS |
| 12 | 夜盘时间戳正确映射官方交易日/周 | `test_night_session_timestamp_maps_to_official_trading_day_and_week` | PASS |
| 13 | 不同 position_id 保持不同往返 | `test_distinct_position_ids_remain_distinct_round_trips` | PASS |
| 14 | 未完成持仓不物化为已完成 | `test_incomplete_open_position_is_not_materialized_as_completed` / `test_incomplete_position_is_reported_but_not_completed` | PASS |
| 15 | 等价有序证据下确定性身份稳定 | `test_deterministic_identity_is_stable_for_equivalent_ordered_evidence` | PASS |
| 16 | 证据实质变化改变身份 | `test_material_change_to_evidence_changes_identity` | PASS |

附加失败关闭守卫（Guard tests）：

- 已完成 position_id 复用失败关闭（`test_reopening_completed_position_id_fails_closed`）；
- 无关合约持仓静默合并失败关闭（`test_merging_unrelated_contract_positions_fails_closed`）；
- 乱序转换失败关闭（`test_out_of_order_transitions_fail_closed`）；
- 执行结果成本与权威成本不一致失败关闭（`test_outcome_cost_mismatch_fails_closed`）；
- 时间戳超出发布会话窗口失败关闭而非猜测（`test_session_day_outside_published_windows_fails_closed`）；
- 会话交易日与快照交易日不一致失败关闭（`test_session_day_inconsistent_with_snapshot_fails_closed`）；
- 平面无操作转换不得携带成本/盈亏（`test_flat_noop_transition_cannot_carry_cost_or_pnl`）；
- 运行器输出经 SessionMetadata 映射官方交易日（`test_session_metadata_with_runner_output_uses_official_day`）。

## 验证（Verification）

- 聚焦命令：`python -m unittest tests.test_round_trip_ledger -v` → 25 tests OK。
- 静态差异检查：`git diff --check`（提交前执行）。
- 完整命令：`python -m unittest discover -s tests -v`（提交前执行）。

## 残留限制（Residual limitation）

- 周度归属沿用官方交易日的 ISO `(year, week)`；若未来需要交易所特定周/结算周定义，
  必须在正式 authority 中以版本化事实显式提供，本 lane 不做猜测。
- `active_official_trading_days` 仅含存在生命周期活动（转换）的官方交易日；不含
  无事件持有日的“完整持有区间日数”——后者需要事件/mark 流依赖，本 lane 失败关闭而非猜测。
- 本账本当前没有消费方（Playbook 证据、统计画像、观测报表均未在本 lane 实现）；
  账本接口保持通用，不锁定任何候选族或统计阈值。
