# Backtest & Validation 执行语义验证记录

日期：2026-08-15

工具结论：`USE_EXISTING`。实现仅使用 Python 标准库和现有项目模块；未安装、验证或采纳第三方回测、交易、研究或存储框架。

复用的既有原语：

- `CompletedBar.available_at` 与 `is_visible_at()`：决定市场输入何时可见。
- `StrategyIdentity` 与 `ExperimentIdentity`：绑定策略制品、代码、参数、环境、数据、特征与暴露版本。
- `EvidenceLedger`：唯一的访问/验证结果事实账本。
- `FinalUnseenFirewall`：所有 runner 数据集访问的唯一入口。

本包证明的连接语义：

- 输入必须按 `(decision_at, request_id)` 严格递增；不符合时失败而不重排。
- 事件按 `VISIBLE_MARKET_INPUT -> STRATEGY_INTENT -> ORDER_CREATED -> FILL_ELIGIBLE` 排序；同一时间戳使用固定优先级。
- 不可见的已完成 K 线不能生成意图。
- FAST 只能记录拒绝，不能产生确认结果；CONFIRMATORY 才能记录确认结果。
- FINAL_UNSEEN 经实际 runner 路径仍默认拒绝，且不会执行事件链。

借鉴的清洁室测试/设计类别：`docs/reuse/STEEL_REUSE_AUDIT.md` 中
`historical_replay/lane.py` 的严格因果/时间边界测试思路；未复制旧项目代码或语义。

明确未证明：成本、滑点、费率、保证金、价格限制、组合交互、展期、真实订单/成交、最终未见评估与任何金融有效性。
