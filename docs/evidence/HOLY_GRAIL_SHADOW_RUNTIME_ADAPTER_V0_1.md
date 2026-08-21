# Holy Grail 到 Shadow Runtime 适配器 V0.1

`src/holy_grail_shadow_adapter.py` 以真实 `HolyGrailMachineOperationalization.evaluate`
生成的事件序列作为唯一策略输入；它不是 TEST_ONLY 假策略。适配器仅在相同 completed-bar
`available_at` 产生 OPEN/CLOSE intent，并保留全部机器 directive：entry resting、保护止损
pending/activation、stop replace、触发、摆动确认和 OCO 关联身份。

本实现不声称纸面 MARKET fill 等同交易所 stop fill。现有 generic PaperBroker 只有 MARKET/
LIMIT 生命周期；因此 directive 被完整记录，未被悄悄降级或伪造成外部 resting-stop 成交。
针对真正 broker order 的 STOP/OCO 扩展仍是未来独立执行语义工作，当前合成链的成交事实只
来自 PaperBroker。该限制不影响 machine 的 completed-bar、L1/R1、pending、单调收紧和
同柱 ambiguity 语义。
