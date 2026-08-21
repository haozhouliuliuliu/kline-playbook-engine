# 停止单与 OCO 运行时语义 V0.1

`STOP_MARKET` 与 `MARKET`/`LIMIT` 是订单类型；`ENTRY_STOP`、`PROTECTIVE_STOP`、`EXIT_STOP` 是独立角色。每笔订单确定性绑定策略、指令、客户订单、角色、类型、方向、数量、触发/限价、创建/可用时间、父订单、OCO、替换代次和机器 directive 身份。

纸面经纪商只基于已完成 1 分钟柱：停止单从 `RESTING` 到 `TRIGGERED` 再到填单；触发柱的开盘跳空按开盘价，否则按触发价。可用时刻位于柱内、激活时开盘已跨越、同 OCO 多订单同柱可触发，均产生 `AMBIGUOUS_INTRABAR_SEQUENCE`，不填单。

完整成交会在 Broker 产生 `ORDER_CANCELLED`，经 OMS、TradingState 和不可变 Ledger 处理其他活跃 OCO sibling。重复事件由既有事件身份幂等吸收；已取消/已成交后的迟到取消不覆盖成交事实。非原子 replace 以 cancel+submit 审计，替换代次递增，并显式暴露保护替换风险；不得据此宣称真实交易所队列、滑点或 gap 成交质量。
