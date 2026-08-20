# SHADOW_RUNTIME_FOUNDATION_V0_1

> Version: 0.1 (final engineering state)
> Date: 2026-08-21
> Status: IMPLEMENTED_AND_TESTED / ENGINEERING_VERIFIED / GENERIC
> Work package: `SHADOW_RUNTIME_FOUNDATION_V0_1` — 模拟盘运行基础（确定性 paper trading runtime）
> Architecture addendum: `docs/architecture/SHADOW_RUNTIME_FOUNDATION_V0_1.md`
> Tool decision: `USE_EXISTING`（未新增外部框架，全部使用现有 Python 标准库）
> Branch: `preoutcome/shadow-runtime-foundation-v01`；base `main` `e87315dd622689eb165dbe81f1728c868cc06a26`
> 未触碰 `main`；未连接真实 broker；未使用真钱；未使用任何 candidate strategy outcome。

## 1. Authority and scope

依据：`ARCHITECTURE_BASELINE.md`（Skeleton v1.0）第 5 节 Trading Loop 与第 6 节
Ledger 的既有规定。本包只做“架构基线已明确、且不需要新 research semantics”的普通工程实现；
不改动任何冻结研究语义，不改动现有 src 模块的既有行为，不推进任何候选结果。

硬边界（未实现、未触碰）：

```text
REAL_TQSDK_TRADING         = NOT_IMPLEMENTED
SIMNOW_LOGIN               = NOT_IMPLEMENTED
CTP_LOGIN                  = NOT_IMPLEMENTED
REAL_BROKER_CREDENTIALS    = NOT_IMPLEMENTED
REAL_MONEY_SIZING          = NOT_IMPLEMENTED
PERMANENT_RISKGATE_NUMBERS = NOT_IMPLEMENTED
SHADOW_AUTO_START          = NOT_IMPLEMENTED
LIVE_LLM_DECISION          = NOT_IMPLEMENTED
CANDIDATE_OUTCOME_USAGE    = FORBIDDEN
```

## 2. PHASE A — component gap audit

对现有组件按本包口径分类（仅用于决定本包实现范围，不代表任何 production-ready 判断）。

```text
PRODUCTION_READY            —— 既有语义被直接复用：
                              ContractSpecification / ContractMaster / OrderAction /
                              PositionDirection / CloseOffset / OffsetCostAssumptions
                              (src/contract_semantics.py)
                              CompletedBar / SessionMetadata (src/data_substrate.py)
                              NormalizedHistoricalBar (src/historical_data.py)

STRUCTURAL_CORE_ONLY         —— 结构存在，但本包补充了运行时链绑定：
                              StrategyIdentity / playbook contract (src/playbook_contract.py,
                              src/strategy_evidence.py) —— 仅作为 strategy_identity_id 载体

SYNTHETIC_ONLY               —— 仅用于合成/纸面：
                              (新) src/paper_broker.py（确定性纸面券商）
                              (新) src/runtime_synthetic_fixture.py（TEST_ONLY 假策略，tests/）

PARTIAL                      —— 已有部分、本包补齐为运行时完整语义：
                              stop/OCO (src/stop_order_execution.py) —— 保留，运行时链独立
                              portfolio semantics (src/portfolio_semantics.py) —— 保留，真钱组合仲裁域

MISSING                      —— 基线已规定、此前缺失、本包实现：
                              TradingState、broker event identity/dedup/out-of-order、
                              OMS、BrokerAdapter 接口、PaperBrokerAdapter、
                              reconciliation、Safety、RuntimeLedger、crash/restart recovery

OWNER_GATED                  —— 需要 Owner 新决策，未实现：
                              永久真钱 RiskGate 数值、live LLM 决策、Shadow 自动启动、
                              candidate round-trip 统计接入 runtime 链

EXTERNAL_BROKER_GATED        —— 需要真实券商/接入，未实现：
                              真实 TqSdk trading、SimNow/CTP 登录、真实凭证、真钱下单
```

## 3. PHASE B — implemented (ordinary engineering gaps)

新增 13 个 src 模块（见架构 addendum §2）。关键语义：

1. **TradingState**（`src/trading_state.py`）— 唯一实时可变状态权威。持有账户
   `AccountState`、仓位 `PositionState`、券商已确认订单 `RuntimeOrderState`、
   已应用事件日志与每 stream 序号水位、连接状态。所有 broker 事实经
   `apply_broker_event` 幂等、去重、严格有序地应用。
2. **Broker event identity**（`src/runtime_events.py`）— `BrokerEvent` 带
   `event_id`/`stream_id`/`sequence`；去重（同 id 同内容=幂等 no-op，同 id 异内容=
   violation）、乱序/缺口/非法内容全部 fail closed 记录为 violation 并交给 Safety。
3. **OMS**（`src/order_management.py`）— submit/cancel/replace 生命周期，
   broker 事实覆盖本地推断；重复 client_request_id fail closed。
4. **BrokerAdapter 接口**（`src/broker_adapter.py`）— 项目自有薄接口 + 快照词汇
   （账户/仓位/订单），核心逻辑不绑定任何第三方私有结构。
5. **Deterministic PaperBrokerAdapter**（`src/paper_broker.py`）— 纯合成、不连外网、
   不模仿任何真实券商私有 API；确定性事件流、券商侧镜像账本、快照 fixture。
6. **Reconciliation**（`src/reconciliation.py`）— 本地状态 vs 券商快照，
   账户/仓位/订单逐项比对，任一 mismatch 即 fail closed。
7. **Safety**（`src/safety.py`）— 覆盖 stale market data、broker disconnect、
   duplicate/inconsistent order、account/position/order mismatch、clock/session anomaly、
   kill switch（永久 latch，手动 disarm）。未冻结任何真钱风险限额。
8. **Ledger integration**（`src/runtime_ledger.py`）— intent/order/cancel/fill/
   position transition/safety/reconciliation/broker event/recovery/runtime start/
   kill switch 全部入链；链式哈希 + `verify_chain()` 可审计、可重放。
9. **crash/restart recovery**（`src/runtime_recovery.py`）— 从持久化事实 + 券商快照
   重建 TradingState；ledger tail 不一致即 fail closed；PaperBroker 使用确定性快照 fixture。

## 4. PHASE C — end-to-end synthetic runtime

`src/shadow_runtime.py` 将整链串联为确定性 `ShadowRuntime`，并覆盖：

- completed bar → TEST_ONLY 假策略 intent → 冲突解决 → RiskGate → OMS →
  PaperBroker → broker events → TradingState → Safety → RuntimeLedger → reconciliation；
- duplicate fill（幂等 no-op）、out-of-order event（violation+blocking）、
  disconnect（Safety flag + RiskGate 拒绝新开仓）、stale data（Safety/RiskGate 拒绝）、
  position mismatch（reconciliation fail closed）、kill switch（阻断交易，可 disarm 恢复）、
  restart recovery（持久化重建后对账通过并可继续交易）。

禁止使用 Holy Grail/NR7 或任何候选表现；仅允许 TEST_ONLY fake strategy
（`tests/runtime_synthetic_fixture.py`）。

## 5. WHAT_IS_NOW_IMPLEMENTED

```text
DETERMINISTIC_PAPER_TRADING_RUNTIME_CHAIN = IMPLEMENTED
TRADING_STATE_SOLE_MUTABLE_OWNER         = IMPLEMENTED
BROKER_EVENT_IDENTITY_DEDUP_IDEMPOTENT   = IMPLEMENTED
BROKER_EVENT_OUT_OF_ORDER_HANDLING       = IMPLEMENTED
OMS_SUBMIT_CANCEL_REPLACE_LIFECYCLE      = IMPLEMENTED
PROJECT_OWNED_BROKER_ADAPTER_INTERFACE   = IMPLEMENTED
DETERMINISTIC_PAPER_BROKER_ADAPTER       = IMPLEMENTED
RECONCILIATION_FAIL_CLOSED               = IMPLEMENTED
SAFETY_STALE_DISCONNECT_DUP_MISMATCH_CLOCK_KILL = IMPLEMENTED
RUNTIME_LEDGER_REPLAYABLE_AUDITABLE      = IMPLEMENTED
CRASH_RESTART_RECOVERY                   = IMPLEMENTED
END_TO_END_SYNTHETIC_SCENARIOS           = IMPLEMENTED (58 focused tests)
```

## 6. WHAT_REMAINS_EXTERNAL_BROKER_GATED

```text
REAL_TQSDK_TRADING            = REMAINS_EXTERNAL_BROKER_GATED
SIMNOW_LOGIN                  = REMAINS_EXTERNAL_BROKER_GATED
CTP_LOGIN                     = REMAINS_EXTERNAL_BROKER_GATED
REAL_BROKER_CREDENTIALS       = REMAINS_EXTERNAL_BROKER_GATED
REAL_BROKER_RECONCILIATION    = REMAINS_EXTERNAL_BROKER_GATED
REAL_ACCOUNT_POSITION_SOURCE  = REMAINS_EXTERNAL_BROKER_GATED
```

## 7. WHAT_REMAINS_OWNER_GATED

```text
PERMANENT_RISKGATE_NUMBERS      = REMAINS_OWNER_GATED
PERMANENT_FEE_MARGIN_SCHEDULES  = REMAINS_OWNER_GATED
SHADOW_AUTO_START               = REMAINS_OWNER_GATED
LIVE_LLM_DECISION               = REMAINS_OWNER_GATED
RUNTIME_TO_ROUND_TRIP_CANDIDATE_PIPELINE = REMAINS_OWNER_GATED
```

## 8. WHAT_REMAINS_STRATEGY_GATED

```text
ANY_CANDIDATE_FAMILY_STRATEGY_IN_RUNTIME   = REMAINS_STRATEGY_GATED (禁止使用候选表现)
CANDIDATE_OUTCOME_BACKTEST                 = NOT_AUTHORIZED
VALIDATION_ACCESS                          = LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS            = LOCKED
PROSPECTIVE_SHADOW_FORWARD                 = NOT_AUTHORIZED
```

## 9. Verification

```text
python -m unittest discover -s tests -v   -> 632 tests OK (58 new focused)
python -m compileall -q src tools tests   -> clean
git diff --check                          -> clean
NO_NETWORK / NO_BROKER / NO_REAL_MONEY    -> guaranteed (synthetic only)
```

## 10. Tool decision

```text
TOOL_DECISION=USE_EXISTING
NEW_TOOL_REQUIRED=NO
```

未新增任何外部框架。若未来需要真实券商接入才可能引入外部依赖，届时按
`TOOL_REGISTRY.md` 走 CANDIDATE → VERIFIED → ADOPTED 流程并记录
`ADD_TOOL_REQUIRED`。
