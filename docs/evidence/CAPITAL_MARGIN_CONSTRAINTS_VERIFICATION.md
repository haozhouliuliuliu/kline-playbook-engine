# 资本与保证金执行约束验证记录

日期：2026-08-15

工具结论：`USE_EXISTING`。仅使用 Python 标准库和既有项目模块；未接入实际账户、经纪商、费率或交易框架。

复用的既有原语：

- `ChronologicalValidationRunner` 的 PIT、时序、执行观察和填充/未填充路径。
- `ExecutionAssumptions` 的固定合成费用；`StrategyIdentity`、`ExperimentIdentity`、既有账本与最终未见防火墙。

新增的合成夹具合同：

- 显式 `OrderSpecification(request_id, quantity)`，数量为正 `Decimal` 并按顺序绑定原有执行请求。
- `CapitalMarginAssumptions`：版本、合成合约乘数、初始保证金率和货币单位，全部构成稳定身份；示例仅用 `capital-v1`、乘数 `1`、保证金率 `0.1`、`SYNTH`。
- `CapitalSnapshot` 与 `CapitalTransition` 为不可变离线验证快照，不接管实时 `TradingState`。
- 可填充订单在可用资本覆盖 `填充价 × 数量 × 乘数 × 保证金率 + 既有合成费用` 时才填充；否则记录 `NOT_FILLED/INSUFFICIENT_MARGIN`，资本快照不变。
- 执行与确认事实仍写入现有 `EvidenceLedger`，并同时引用执行假设和资本/保证金假设身份。

明确未证明：真实交易所/经纪商费用或保证金、维护保证金、盯市盈亏、净额、强平、组合/风险预算、真实订单或任何金融有效性。
