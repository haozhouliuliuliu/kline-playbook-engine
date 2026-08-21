# Holy Grail 全 Shadow Runtime 接线 V0.2

真实 `HolyGrailMachineOperationalization` 的 completed-bar directive 现经 `HolyGrailShadowAdapter` 进入 generic OMS/PaperBroker：入场停止单挂单、触发、填单；保护停止 pending/activation；摆动 trailing 的取消/重建；保护触发与平仓均为可审计 broker 事件。适配器不再把 machine 的 stop 事件降级为 MARKET intent。

`PROTECTIVE_STOP_PENDING` 在尚无确认 pivot 时显式存在；它及 `PROTECTIVE_STOP_REPLACEMENT_IN_PROGRESS` 会阻断后续普通开仓，直到保护状态被解析。PaperBroker snapshot 包含 resting stop 身份，现有重建与 reconciliation 继续以 broker snapshot 和链式 Ledger fail closed。

这是 `SYNTHETIC_EXECUTION_SEMANTICS`，不是 `REAL_EXCHANGE_EXECUTION_CLAIM`；真实滑点、排队、涨跌停和成交质量仍由前瞻 authority 及未来资料治理。
