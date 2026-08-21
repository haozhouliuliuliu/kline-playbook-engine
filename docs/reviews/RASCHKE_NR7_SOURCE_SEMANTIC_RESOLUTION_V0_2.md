# RASCHKE_NR7_SOURCE_SEMANTIC_RESOLUTION_V0_2

> 状态：`COMPLETE / SOURCE_SEMANTIC_RESOLUTION=INSUFFICIENT / PRE_OUTCOME`
>
> 日期：2026-08-21
>
> 范围：Raschke NR7 / 区间收缩 → 趋势日突破族的来源复核；不读取任何候选行情、结果或受保护样本。

## 结论

```text
FAMILY=RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT
SOURCE_SEMANTIC_RESOLUTION=INSUFFICIENT
MACHINE_READY=NO
PRIMARY_FREEZE_READY=NO
STRATEGY_IDENTITY_CREATED=NO
OUTCOME_TEST_REGISTERED=NO
NO_CANDIDATE_OUTCOME_USED=YES
BLOCKING_FIELD_COUNT=5
BLOCKING_FIELDS=NR7_LOOKBACK_ALIGNMENT,EARLY_MORNING_RANGE_PRIMARY,INITIAL_STOP,POST_ENTRY_INVALIDATION,DETERMINISTIC_EXIT_AND_TIME_EXIT
```

这是一份完成的负向来源结论，不是工程失败。V0.1 已固定入场方向与止损单性质，但本轮复核仍不能把缺失的交易语义伪装成普通工程细节，因此不创建 NR7 V0.2 machine-ready Contract、运行时适配器、PRIMARY Freeze 或 StrategyIdentity。

## 证据范围与停止条件

本轮按以下有限范围检索并停止：

1. V0.1 已绑定的 `SB-RASCHKE-NR7-SEMANTIC-V1` 及 23 条 SOURCE_ONLY 声明；
2. Linda Bradford Raschke 官方文章页及其中的原始/近原始访谈资料；
3. 直接相关的官方《Trading Style and Daily Market Regimen》NR7 资料；
4. 官方《Everything You Wanted to Know about Electronic Trading but were Afraid to Ask》对一般静态保护止损的说明。

第 4 项只说明一般执行习惯（静态保护单应远离噪声），并未提及 NR7 或把止损价位定义为当前家族规则。因此它**不得**转移为 `INITIAL_STOP` 或 `POST_ENTRY_INVALIDATION`。官方文章目录没有提供额外的 NR7 专属止损、失效、目标或时间退出规则；付费书籍、订阅数据、登录、WAF/CAPTCHA 绕过均未使用。

来源锚点：

- `SR-V0-M03`：官方 Active Trader 访谈，NR7 后一天以早盘区间两侧 stop bracket；45 分钟和一小时均被明确允许；未给出成交后保护规则。
- `SR-V0-M01/M02/M04/M05`：V0.1 bundle 中的官方/近原始资料；仅提供定性管理、不同家族的止损示例或不可用的 TICK/广度上下文。
- 官方文章目录：<https://lindaraschke.net/articles/>。
- 官方电子交易文章：<https://lindaraschke.net/wp-content/uploads/2013/10/Rashke_0406.pdf>（一般性止损，非 NR7 专属）。

## V0.1 完整字段复核矩阵

`SOURCE CLAIM`、`PROJECT INTERPRETATION` 与 `MACHINE OPERATIONALIZATION` 保持分层。矩阵中 `项目处理` 只说明本轮是否可作非结果工程决定；它不是新的来源声明。

| 字段 | V0.1 来源分类 | 本轮分类 | 项目处理 / 结论 |
|---|---|---|---|
| NR7 日线定义 | EXPLICIT | PINNED_SOURCE_EXPLICIT | 保留为日线七柱窄幅概念；中国期货日界另列。 |
| NR7 回看对齐 | PARTIALLY_PINNED | UNKNOWN_SOURCE_SEMANTIC | “past seven”与“last seven days”不能唯一确定含当前柱的窗口；阻塞 PRIMARY。 |
| 下一交易时段 | PARTIALLY_PINNED | PROJECT_INFERRED_VERSIONED_NON_OUTCOME | “NR7 后一天”明确；本地 SessionMetadata 可决定交易日映射，不添加策略过滤。 |
| 早盘区间 45/60 分钟 | SOURCE_PERMITTED_MULTIPLE_VARIANTS | UNKNOWN_SOURCE_SEMANTIC | 两个来源允许版本均保留，不能由结果或任意默认值选 PRIMARY。 |
| 多头入场位 | EXPLICIT | PINNED_SOURCE_EXPLICIT | 早盘区间高点上方的 buy stop。 |
| 空头入场位 | EXPLICIT | PINNED_SOURCE_EXPLICIT | 早盘区间低点下方的 sell stop。 |
| 入场订单类型 | EXPLICIT | PINNED_SOURCE_EXPLICIT | stop entry；stop-market/stop-limit 仍不可由来源决定。 |
| 入场偏移/tick | UNKNOWN | MACHINE_DETAIL_OPEN | 不能把其他 setup 的“一跳”借入；触发价舍入可在未来机器版本中显式记录。 |
| 对侧未成交单 | UNKNOWN | PROJECT_INFERRED_VERSIONED_NON_OUTCOME | 若未来已有完整策略，可用单次入场 OCO 管道；这不补足风险语义。 |
| 同柱双触发 | UNKNOWN | UNOBSERVABLE_WITH_CURRENT_DATA | 仅 OHLCV 不能确定盘中先后；必须保持因果失败闭合，不能猜成交顺序。 |
| 成交后失效 | UNKNOWN | UNKNOWN_SOURCE_SEMANTIC | 未找到 NR7 专属边界；一般“不给回撤太多”是定性语言。阻塞 PRIMARY。 |
| 初始保护止损 | UNKNOWN | UNKNOWN_SOURCE_SEMANTIC | 未找到 NR7 专属价位；一般“静态保护止损”不定义位置。阻塞 PRIMARY。 |
| 趋势日定义 | EXPLICIT | PINNED_SOURCE_EXPLICIT | 价格化定义保留；不是入场后确定性退出。 |
| 趋势日确认 | PARTIALLY_PINNED | UNKNOWN_SOURCE_SEMANTIC | 大柱/量/趋势性阈值未固定，且非 bracket 入场触发。 |
| 普通成交量角色 | PARTIALLY_PINNED | UNKNOWN_SOURCE_SEMANTIC | 仅为定性确认，不制造数值门槛。 |
| TICK/广度角色 | REQUIRES_UNAVAILABLE_INPUT | UNOBSERVABLE_WITH_CURRENT_DATA | 当前数据不拥有该输入，严禁 OHLCV 代理。 |
| 盈利退出/目标 | PARTIALLY_PINNED | UNKNOWN_SOURCE_SEMANTIC | “持有趋势日/回撤过多退出/减半”没有确定价位或规则。 |
| 收盘/隔夜处理 | PARTIALLY_PINNED | UNKNOWN_SOURCE_SEMANTIC | 持至收盘、加仓、部分隔夜均被提及，未形成唯一时间退出。与前项合并为一个最小阻塞。 |
| 不交易条件 | PARTIALLY_PINNED | UNKNOWN_SOURCE_SEMANTIC | 定性风险提示，不能变成确定性 gate。 |
| 失败/反例 | PARTIALLY_PINNED | UNKNOWN_SOURCE_SEMANTIC | 保留负向上下文，不制造损失规则。 |
| 时间框架范围 | PARTIALLY_PINNED | UNKNOWN_SOURCE_SEMANTIC | 日线设定、45/60 分钟入场、15 分钟确认、小时管理，未有单一操作框架。 |
| 来源工具范围 | EXPLICIT | PINNED_SOURCE_EXPLICIT | 明确为美国指数期货/股票及商品期货的来源语境。 |
| 中国期货转移 | INFERRED | PINNED_SOURCE_INFERRED | 是版本化项目假设，绝不表述为来源事实；不按产品结果选择范围。 |

机器细节的项目决定仅限一般性、不改变来源交易含义的项目，如现有 OCO 编码、可用时点、身份绑定和 tick 舍入。它们不会被当作对初始止损、失效、退出、早盘窗口或回看对齐的替代答案。

## 最小阻塞集说明

1. `NR7_LOOKBACK_ALIGNMENT`：改变某日是否为 NR7，属于信号本体，不能凭工程偏好裁决。
2. `EARLY_MORNING_RANGE_PRIMARY`：45 分钟和 60 分钟都由来源允许，但来源未给唯一 PRIMARY；两者不得合并或按结果选择。
3. `INITIAL_STOP`：决定风险边界；所见一般止损文字没有 NR7 特异性。
4. `POST_ENTRY_INVALIDATION`：决定何时承认读法错误；对侧 entry bracket 不能改写为 stop。
5. `DETERMINISTIC_EXIT_AND_TIME_EXIT`：目标、回撤、收盘与隔夜均为多种定性管理可能，不能形成一个可回放的退出循环。

其余开放项要么是明确的未来机器细节、要么在现有 OHLCV 下不可观测、要么是以上阻塞被解除后仍须版本化的解释。将第 17、18 项合并不掩盖语义：二者共同缺的是同一个完整、确定性的离场循环。

## 不执行的后续阶段

因为 `MACHINE_READY=NO`，本工作包明确不执行：NR7 machine 模块、NR7→Shadow synthetic wiring、STOP/OCO 生命周期测试扩展、PRIMARY Freeze、StrategyIdentity、Research Wave outcome manifest。现有通用合成执行链保持不变，不能用 TEST_ONLY fake strategy 冒充真实 NR7。

可留下的非结果登记结论为：未来若 NR7 与 Holy Grail 同波次，NR7 必须作为新增、独立可证伪假设计入 multiplicity denominator；本轮没有创建 locked wave 或读取任何 outcome。

## 可复核性

机器可读矩阵：`docs/reviews/RASCHKE_NR7_SOURCE_SEMANTIC_RESOLUTION_V0_2.json`。

`tests/test_raschke_nr7_source_semantic_resolution_v02.py` 对矩阵完整性、最小阻塞、来源未固定字段的失败闭合以及禁止伪 machine-ready 结论进行回归保护。
