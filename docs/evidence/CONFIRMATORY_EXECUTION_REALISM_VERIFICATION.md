# 确认性执行真实性验证记录

日期：2026-08-15

工具结论：`USE_EXISTING`。只使用 Python 标准库和已有项目模块；未安装、验证或采纳外部回测、交易、经纪商或数据框架。

复用的既有原语：

- `CompletedBar` 的点时可见性，以及 `ChronologicalValidationRunner` 的可见输入到填充资格事件链。
- `StrategyIdentity`、`ExperimentIdentity`、`EvidenceLedger` 与 `FinalUnseenFirewall`。

新增且已验证的最小语义：

- `ExecutionObservation` 记录中性合成执行观察的观测/可见时间、价格和可交易状态；观察必须在订单获得资格后才可独立使用。
- `ExecutionAssumptions` 是不可变、版本化的合成模型身份：`synthetic-v1`、固定滑点 `1.5`、固定费用 `0.25`、`NEXT_TRADABLE_OBSERVATION` 规则。它们不是实际市场估计。
- 后续可见且可交易的观察得到 `FILLED`；无观察、观察晚于截止时间或不可交易得到 `NOT_FILLED`。
- 执行结果及 `VALIDATION_CONFIRMED` 均通过现有 `EvidenceLedger` 写入，并引用执行假设身份；没有第二个账本。
- 没有执行假设和评估时，不能发出 `VALIDATION_CONFIRMED`；FAST 语义未改变，最终未见数据仍经既有防火墙拒绝。

未证明：真实费用/滑点校准、交易所撮合与价格限制细节、资金/保证金、组合交互、真实订单或成交、最终未见评估，以及任何金融有效性。
