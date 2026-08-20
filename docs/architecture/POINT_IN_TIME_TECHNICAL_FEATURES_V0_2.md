# POINT_IN_TIME_TECHNICAL_FEATURES_V0_2

> 状态：通用确定性工程语义 / 非 Holy Grail PRIMARY 语义

## 模块接口

`TimeframeAggregator.aggregate(...)` 接收：

- 当前 `SessionMetadata` 权威；
- 有序 `NormalizedHistoricalBar`；
- 显式基础周期、目标 `TimeframeSpec`、交易所、具体合约和覆盖区间。

它返回不可通过普通构造器伪造的 `AggregationResult` 完整性信封。EMA/ADX 只接受该信封，不接受裸聚合柱序列。

## 完整性与时长

- 预期起点来自 `expected_bar_starts` 和 `expected_bar_starts_between`；
- 官方交易日来自 `trading_day_at`；
- 不按星期或民用日期猜测会话；
- 完全缺失的会话仍生成 `IncompleteBucket`；
- 每个桶记录预期起点、实际起点、起止时间和目标时长；
- 会话边缘不足一个完整目标周期时标记 `boundary_shortened=True`，绝不按任意柱数判为完整；
- 每根来源柱时长必须等于显式基础周期，目标周期必须是基础周期的整数倍；
- 日线必须覆盖官方交易日的全部预期起点，否则不完整。

## 特征身份

每个 EMA/ADX 值绑定：

- 交易所、具体合约、时间框架及 `SessionMetadata.version`；
- 当前聚合身份；
- 从序列根开始的链式依赖前缀身份；
- 显式 `FeatureNumericPolicy`；
- `ArtifactBinding.from_file` 计算的实际 `src/technical_features.py` 字节身份；
- 显式周期、价格字段和特征版本。

因此，早期来源证据即使没有改变最终数值，也会改变后续特征身份；实现文件字节变化同样会改变身份。

## 数值政策

模块没有默认数值政策。调用方必须显式提供 EMA 种子、ADX 初始化、内部精度、输出量化和舍入方式。通用算法不硬编码 20 或 14；Holy Grail 是否采用某一政策仍由 `FGH-GATE-03` 决定。
