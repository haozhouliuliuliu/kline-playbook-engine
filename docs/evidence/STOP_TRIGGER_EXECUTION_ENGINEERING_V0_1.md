# 通用止损触发 工程证据（Stop Trigger Execution Engineering Evidence）

日期：2026-08-20
Lane：`parallel/stop-trigger-observation-v01`（GENERIC_STOP_TRIGGER_EXECUTION_ENGINEER）
基线：`origin/main` = `64771245acf5e445adc59eb5ef71afcb0ef00777`
范围隔离：仅实现通用、版本化的止损触发观察层；不实现候选策略逻辑、不设计移动止损、
不做回测、不检查候选结果、不计算 Holy Grail 特定止损、不发明跟踪规则、不改变冻结
Protocol、不使用候选结果数据；不修改 `CURRENT_STATE.md`。

## 结论

```text
STATUS=COMPLETE
STOP_TRIGGER_LAYER=IMPLEMENTED
BUY_STOP=PASS
SELL_STOP=PASS
GAP_THROUGH=PASS
POINT_IN_TIME_ACTIVATION=PASS
SAME_BAR_AMBIGUITY_FAIL_CLOSED=PASS
OCO_AMBIGUITY_FAIL_CLOSED=PASS
ONE_MINUTE_PATH_SUPPORTED=PASS
EXECUTION_OBSERVATION_BRIDGE=PASS
NO_DOUBLE_SLIPPAGE=PASS
NO_DOUBLE_COST=PASS
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

## 已实现（Implemented）

- 新增 `src/stop_order_execution.py`：
  - `StopSide`（`BUY_STOP` / `SELL_STOP`）；
  - `RestingStopOrder`（显式 resting 止损：`request_id`、`side`、`stop_price`、
    `active_at`、`trigger_model_version`、`instrument`、可选 `concrete_contract_id`、
    可选 `oco_group_id`）；
  - `StopTriggerResult`（确定性结果：outcome、sequence certainty、触发 bar 身份、
    参考执行价、确定性 `identity_id`）；
  - `evaluate_stop_order(...)`：单笔 resting 止损对有序已完成 bar 求值，首个合格
    触发胜出；
  - `evaluate_stop_group(...)`：一组止损求值，同一 OCO/bracket 组内同一最小分辨率
    bar 双双触发时 FAIL CLOSED 返回 `AMBIGUOUS_INTRABAR_SEQUENCE`；
  - `stop_trigger_result_to_execution_observation(...)`：无歧义触发桥接到既有
    `ExecutionObservation`。
- 新增 `tests/test_stop_order_execution.py`：27 个合成测试，全部通过。
- 新增 `docs/architecture/STOP_TRIGGER_EXECUTION_SEMANTICS_V0_1.md`（架构说明）。

## 触发规则（ENGINEERING EXECUTION ASSUMPTION）

```text
STOP_MARKET_TRIGGER_MODEL_V0_1   # 机器/工程约定，非人类来源语义
BUY_STOP : trigger if eligible bar.high >= stop_price
SELL_STOP: trigger if eligible bar.low  <= stop_price

BUY_STOP reference price:
  - if bar.open >= stop_price: reference = bar.open
  - elif bar.high >= stop_price: reference = stop_price
  - else: no trigger
SELL_STOP reference price:
  - if bar.open <= stop_price: reference = bar.open
  - elif bar.low <= stop_price: reference = stop_price
  - else: no trigger
```

- 参考价进入既有执行/滑点层；本模块绝不再加一次合成滑点。
- 不构造 tick 序列；不发明精确的分钟内时间戳；证据保留 bar start / end /
  `available_at`、触发侧、止损位、参考执行价、序列确定度。

## 关键语义（Key semantics）

### 时点激活（Point-in-time activation）

```text
bar.end <= active_at            -> 激活前已结束/已知 -> 不可触发（跳过）
active_at < bar.start           -> 严格早于 bar 触发区间 -> 合格
active_at == bar.start          -> 边界：open 与激活同刻
                                    open 已穿越阈值 -> AMBIGUOUS_INTRABAR_SEQUENCE
                                    否则后续穿越严格晚于激活 -> 真实触发
bar.start < active_at < bar.end -> 激活落在 bar 内部
                                    阈值在 bar 内被穿越 -> AMBIGUOUS_INTRABAR_SEQUENCE
                                    阈值从未穿越 -> 无歧义，继续后续 bar
```

- 首个合格触发胜出；同一决策不访问未来 bar；`cutoff_at` 限制为已可用 bar。
- 不假设有利顺序：穿越与激活无法由 OHLC 排序时一律 fail closed。

### OCO / bracket 组歧义

同一 `oco_group_id` 内，两个方向相反的 resting 止损在同一最小分辨率 bar 内都被
触及且无更细路径时，不任意选择其一，返回 `AMBIGUOUS_INTRABAR_SEQUENCE`（冲突 bar
起的所有触发均视为不可知）。本层只做同 bar 歧义检测，不实现 one-cancels-other
取消语义（那是下游策略/持仓逻辑）。无 `oco_group_id` 的止损按独立求值处理。

### 高时间框架

项目拥有 1 分钟 bar。未来 30m/60m 策略应在其可用时使用底层 1 分钟路径触发止损。
本层消费通用有序 `NormalizedHistoricalBar` 输入，独立可用，不依赖聚合实现。

### 保护性止损

入场止损与保护性出场止损共用同一通用触发机制（多头保护 `SELL_STOP` 与空头保护
`BUY_STOP` 走同一 `evaluate_stop_order` 与同一桥接）。本 lane 不决定 swing low 如何
寻找、移动止损如何移动、或止盈逻辑；只对已提供的止损位求值。

## 回归覆盖（tests/test_stop_order_execution.py，27 项）

- buy stop no trigger / normal trigger / gap-through
- sell stop no trigger / normal trigger / gap-through
- off-tick stop rejected when contract metadata supplied（含合约绑定不一致拒绝）
- pre-activation bar cannot trigger
- future bar not visible/eligible too early（`cutoff_at`）
- first eligible trigger wins
- exact same evidence gives deterministic identity/result
- same-bar activation ambiguity fails closed
- boundary open-crossing does not assume favorable ordering
- boundary open-not-crossed is unambiguous
- straddling bar without crossing is not ambiguous
- opposing OCO stops both touched in one 1m bar -> ambiguity
- OCO single-side touch has no ambiguity
- OCO both touch in different bars has no same-bar ambiguity
- group rejects mixed oco identities
- higher-timeframe use consumes underlying ordered 1m bars
- bridge rejects non-triggered result
- bridged observation flows through existing execution pipeline（FILLED，fill=参考价+滑点）
- no duplicate slippage（桥接价=参考价；滑点由 runner 恰好一次）
- no duplicate cost authority（OPEN 成本=synthetic_fee；CLOSE 成本=synthetic_fee+offset fee，单一权威）
- long protective sell-stop and short protective buy-stop share generic path
- contract-bound stop bridges concrete contract identity

## 测试

```text
python -m unittest tests.test_stop_order_execution -v        # 27 项，全部通过
python -m unittest discover -s tests -v                      # 全量回归（见提交时最终结果）
```

## 残留限制（residual limitation）

- 本层只做触发与同 bar 歧义检测，不实现 OCO 的 one-cancels-other 实际成交语义。
- 边界激活（`active_at == bar.start`）仅在 open 穿越阈值时 fail closed；这是为保持
  “不假设有利顺序” 的最小 fail-closed 约定，并允许真实边界放置可用。
- 不修改 `CURRENT_STATE.md`；本证据仅记录已完成的通用止损触发层。
