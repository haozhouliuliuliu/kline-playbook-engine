# STOP_TRIGGER_EXECUTION_SEMANTICS_V0_2

> 状态：通用确定性工程模型 / 非完整 OMS（订单管理系统）

## 执行模型

唯一受支持的公开模型版本是 `COMPLETED_BAR_STOP_TRIGGER_V0_2`。调用方声明其他版本会直接失败。订单、单笔结果和组结果都绑定由 `ArtifactBinding.from_file` 计算的实际 `src/stop_order_execution.py` 字节身份。

观察模型固定标记为：

```text
COMPLETED_BAR_AVAILABILITY_CONSERVATIVE
EXCHANGE_RESTING_CHRONOLOGY_CLAIMED=NO
```

它只在完成柱可用时观察触发证据，不声称重建交易所内的逐笔先后。将该通用模型用于 Holy Grail PRIMARY 仍受 `FGH-GATE-05` 阻塞。

## 序列证据

- 组评估只物化并校验输入柱迭代器一次；
- 所有成员读取同一不可变有序元组；
- 每个结果保存实际评估的柱身份及链式前缀身份；
- `TRIGGERED` 和歧义结果额外绑定对应柱的 `NormalizedHistoricalBar.identity_id`；
- `NOT_TRIGGERED` 绑定完整实际评估序列，早期柱变化会改变结果身份。

## 最小 OCO 生命周期

- 同一最小分辨率柱内多个成员触发：`AMBIGUOUS_INTRABAR_SEQUENCE`；
- 首个无歧义成员触发：兄弟单变为 `CANCELLED`；
- 取消证据绑定触发结果、取消时间、双方订单身份和已评估前缀；
- 组结果身份包含全部取消证据；
- 已取消兄弟单不会在后续柱再次触发。

该模块不拥有持仓、资金、费用、滑点、价格限制或完整 OMS 生命周期。
