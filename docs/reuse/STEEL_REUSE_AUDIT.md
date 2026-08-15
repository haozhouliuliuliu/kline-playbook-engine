# steel-radar-lite 清洁室复用审计

审计日期：2026-08-15
源仓库：`C:\Users\H\Documents\steel-radar-lite`（只读）
源提交：`84c7679445f49d86a66ab53581b99d039f385a4a`
源工作区：存在未跟踪文件 `exports/V6_HISTORICAL_36_IAR_REVIEW_PACKET.md`；未读取、未复制。

本审计只检查通用工程实现与测试。未读取或复制 RB 策略、Track A/B 语义、模型提示词、实验/盈亏结论、风险阈值、运行账本、凭据或项目状态。

| 已检查资产 | 分类 | 结论 |
| --- | --- | --- |
| `steel_radar_lite/tick_aggregator.py` | BORROW_TEST_OR_DESIGN | 可借鉴断线后标记 `partial`/`reconnect_gap`、只在切换窗口后结束 K 线的测试思路；代码硬编码 SimNow、5 分钟和旧项目文件格式，不复制。 |
| `tests/test_simnow_package1.py` | BORROW_TEST_OR_DESIGN | 可借鉴断线、部分 K 线、关闭竞争与恢复的回归类别；测试依赖 SimNow/CTP 模拟、RB 配置及旧项目运行协议，不复制。 |
| `steel_radar_lite/historical_replay/lane.py` | BORROW_TEST_OR_DESIGN | 可借鉴“完成时间不晚于可见时间”的因果边界与严格时序校验思路；实现包含 RB 合约、虚拟日期和 Track A/B 回放，不复制。 |
| `tests/test_historical_replay_lane.py` | BORROW_TEST_OR_DESIGN | 用作完成 K 线、夜盘归属、边界时刻可见性的回归类别来源；测试本身绑定钢铁项目模型与样本，不复制。 |
| `steel_radar_lite/ctp_gateway.py` | DEFER | 已检查其只读网关的断线恢复和健康状态模式；它直接绑定 CTP/SimNow 生命周期，当前项目未授权经纪商连接，延后而不复制。 |
| `steel_radar_lite/replay_runner.py` | DO_NOT_COPY | 是旧项目已审核事件/报告回放流程，含项目专属事实与输出语义。 |
| `tests/test_replay_runner.py` | DO_NOT_COPY | 覆盖旧项目审核事件和报告，不具备本项目中立性。 |
| `steel_radar_lite/latest_status.py` | DO_NOT_COPY | 虽有容错状态读取模式，但输出字段直接表达旧项目决策/行情状态。 |
| `tests/test_latest_status.py` | DO_NOT_COPY | 绑定旧项目运行状态与决策字段。 |
| `steel_radar_lite/decision_state_machine.py` | DO_NOT_COPY | 包含旧项目策略分数、阈值与操作结论。 |

## 按主题的检查结果

- Tick/K 线聚合：检查了 `tick_aggregator.py`；仅借鉴质量标记的测试类别。
- 完成 K 线时间与因果顺序：检查了 `historical_replay/lane.py` 与其测试；在本项目独立实现。
- 中国期货夜盘：检查了其夜盘测试；本项目仅保留显式、版本化时段元数据，不推断交易日。
- 合法缺席与异常缺口：旧项目未找到可直接复用的通用实现；本项目独立实现。
- `partial`/`reconnect_gap`：检查了聚合器；使用独立的不可变质量字段。
- 确定性回放：检查了回放器及其测试；均与旧项目事实/模型耦合，未复用。
- 不可变账本、幂等/去重、乱序、重启恢复：项目已有 `src/bootstrap_semantics.py` 与 9 项引导测试已经覆盖通用边界；旧项目检查资产不适合复制。
- 简单状态/可观测性：检查了 `latest_status.py`；因旧项目字段耦合而不复制。
- 密钥处理：本次未读取任何可能含凭据的文件或值。

## REUSE_NOW

无。当前最小数据底座使用 Python 标准库独立实现，避免引入旧项目的交易、存储或研究语义。
