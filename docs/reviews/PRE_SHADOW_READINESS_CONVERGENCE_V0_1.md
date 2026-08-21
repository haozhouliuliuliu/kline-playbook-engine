# Pre-Shadow 准备度收敛 V0.1

本矩阵只登记工程和治理状态，不读取候选结果，也不授权实际行情、券商或真实资金。

| 项目 | 状态 | 依据 / 说明 |
|---|---|---|
| Holy Grail V0.4 机器 | READY | 已完成确定性、已完成柱驱动的机器化。 |
| PRIMARY 与 StrategyIdentity | READY | `HOLY_GRAIL_PRIMARY_FREEZE_V0_1` 固定单一策略、六品种、1 分钟和参数身份。 |
| Qualified Eligibility View V1 | READY | 身份 `fb30…c822`，32768 个 D01/D02 合格分区；不解锁结果。 |
| E07 来源主连映射 | READY_FOR_WINDOW | 认证 TqSdk 3.10.1 捕获生成 105 条、六品种的 2024-2025 日程。 |
| 前瞻 Shadow 统计档案 | BLOCKED | 方法不足，尚未固定事件估计量、依赖/聚类、顺序阈值与强 FWER。 |
| 研究波次 | DRAFT_ONLY | 只有无结果草案；不得锁定 manifest。 |
| Holy Grail 到 Shadow Runtime 适配 | BLOCKED_FAIL_CLOSED | 现有 Runtime 的 intent 只有市场开/平仓，尚无对机器入场止损、保护止损/OCO 替换与完成柱时序的已验证适配。不得用测试假策略冒充。 |
| 实时行情接入 | DEFERRED | 未采纳、未授权；不属于本次映射捕获。 |
| E06 费用/保证金 | BLOCKED_FOR_CANDIDATE_EXECUTION | 连续 2024-2025 官方逐期表仍无充分证据。 |
| 历史涨跌停 | BLOCKED_FOR_REALISM_CLAIM | 基础规则已绑定，逐日生效值和特殊日仍缺。 |
| 风控常量 | FIXTURE_ONLY | Shadow foundation 数值不是永久实盘限额。 |
| 券商依赖 | DEFERRED | Paper runtime 只用于合成基础验证；真实券商仍未授权。 |
| 候选结果访问 | LOCKED | 本次未访问、未注册、未解锁。 |

## 最短合法路径

先由项目 authority 采纳一份方法充分的前瞻统计档案；随后实现并以合成、无结果证据验证
Holy Grail 机器事件到 Runtime intent / 止损 OCO 的完整适配；再在独立授权下完成实时行情、
E06、逐日价格限制及 Shadow 运行授权。任何一步都不得反向解锁历史候选收益。
