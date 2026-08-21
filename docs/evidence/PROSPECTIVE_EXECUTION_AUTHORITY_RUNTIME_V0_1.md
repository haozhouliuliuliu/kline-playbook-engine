# 前瞻执行 Authority 运行时 V0.1

`ProspectiveExecutionAuthorityStore` 是本地 append-only 摄入 seam：拒绝静默覆盖与同有效键冲突，保留审计记录，并仅按 `available_at <= decision_at` 查询。费用/保证金、逐日 concrete-contract 涨跌停、slippage policy 都有确定性身份；未来事实不可提前可见。

逐日涨跌停缺失或冲突拒绝，不能以 base rule 冒充当日事实。费用/保证金不补历史 E06。slippage 未解析的状态为 `UNRESOLVED_FAIL_CLOSED`，没有生产零滑点默认；`TEST_ONLY` policy 不能进入候选 Shadow。
