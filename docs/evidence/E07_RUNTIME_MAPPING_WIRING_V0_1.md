# E07 Runtime Mapping Wiring V0.1

`src/e07_runtime_mapping.py` 固定执行顺序：研究符号 -> E07 PIT 日程 -> concrete contract
canonical membership -> QualifiedEligibilityView 分区。任一步缺失、过早可用、冲突、伪主连、
宇宙外合约、首交易日排除或身份不一致均拒绝；没有 volume/OI/日历/前后主连 fallback。

成功结果将 StrategyIdentity、E07 schedule、QualifiedEligibilityView、canonical parent、
session authority、machine implementation 和 partition identity 一起绑定。此 seam 不读取价格
或候选结果，也不改变 outcome access。
