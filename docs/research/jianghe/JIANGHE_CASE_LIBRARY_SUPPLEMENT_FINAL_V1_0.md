# 江河 Case Library Supplement — Final V1.0

这些case只用于来源语义组织，不构成策略有效性证据。

## JH-CASE-007-F01 — 对抗/重叠等待与势位态优先

- source: 007 / `BV1Da4xz6E8y`
- type: `TEACHING_HARD_NEGATIVE_AND_CONTEXT`
- context: K线重叠、多空仍在争夺时，不应只见局部形态就下注。
- source action logic: 等价格真正离开空间、赢家明确，再顺着胜方；更高层判断先看趋势，再看位置，最后才看形态。
- hard negative: N字、吞没、影线测试等若脱离趋势和位置，不构成完整交易理由。
- machine gap: “离开空间/赢家明确”的统一阈值仍UNKNOWN。

## JH-CASE-017-F01 — 三类离场与趋势阶段

- source: 017 / `BV1NBy5BfEYF`
- type: `MANAGEMENT_PROCESS_CASE`
- exit alternatives: fixed R/R; key-location/space; dynamic market-structure.
- source preference: dynamic structure.
- invalidation examples: 原趋势不能继续创新；最后N结构防守位被破。
- stage modifier: 趋势初期可更右侧持有，非初期可更早/左侧退出。
- hard negative: 不能因为账户利润大小临时切换离场逻辑。

## JH-CASE-018-F01 — 高周期位置不是入场

- source: 018 / `BV1K5ywBoEKz`
- type: `MULTI_TIMEFRAME_PERMISSION_CASE`
- high-TF: 先定位关键区域与弱趋势/可能平衡背景。
- low-TF: 切到5m主战场，等待真实转向/反转，而不是到位就买。
- hard negative: 高周期“标准位置”若处在同周期内部结构中，也不自动可交易。
- resolution effect: 与V069共同支持内部结构只作确认/语境，而非独立入口。

## JH-CASE-048-F01 — 专注状态导致缩仓

- source: 048 / `BV1Ybckz4EKX`
- type: `RISK_STATE_CASE`
- evidence: video burned text only; recovered remote SRT rejected as wrong-video mismatch.
- source condition: 外出/环境导致不专注。
- source response: 不敢开太大仓位；强调交易要专注。
- hard negative: 后续P&L列表不得反推出策略有效性或入场规则。

## JH-CASE-099-F01 — 小资金的质量分层与账户资金隔离

- source: 099 / `BV1Yu8p68EYJ`
- type: `RISK_ALLOCATION_PROCESS_CASE`
- evidence: burned subtitles; recovered remote SRT rejected as wrong-video mismatch.
- source logic: 小资金不需要一套特殊策略；把筹码/风险按订单质量分配，高质量多一些、低质量少一些。
- account layer: 可对交易账户设置物理资金上限/隔离多余资金，减少黑天鹅暴露和余额对行为的刺激。
- hard negative: 片中美元金额只是示例，不是统一参数；盈利金额不是有效性证据。

## V065 — no semantic case

- source: 065 / `BV1GSozBrE9e`
- native subtitle: none.
- local ASR: rejected for semantic hallucination.
- visual media: readable.
- disposition: `NO_SEMANTIC_CASE_CREATED`.
- rule: do not infer spoken entry/stop/management logic from order outcomes.
