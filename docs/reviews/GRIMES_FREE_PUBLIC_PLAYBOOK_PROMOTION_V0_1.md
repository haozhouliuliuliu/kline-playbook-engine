# Grimes 免费公开 Playbook 推进审查 V0.1

> 状态：`COMPLETE / ONE_FAMILY_SOURCE_SEMANTIC_INSUFFICIENT / PRE_OUTCOME`
>
> 日期：2026-08-21
>
> 机器可读记录：`GRIMES_FREE_PUBLIC_PLAYBOOK_PROMOTION_V0_1.json`

## 结论

```text
SELECTED_FAMILY=GRIMES_FAILURE_TEST_FAILED_BREAKOUT_REVERSAL
FINAL_RESULT=ONE_FAMILY_SOURCE_SEMANTIC_INSUFFICIENT
PLAYBOOK_SEMANTICALLY_DRAFTABLE=NO
MACHINE_READY=NO
PRIMARY_FREEZE_READY=NO
NO_CANDIDATE_OUTCOME_USED=YES
PAID_OR_AUTHENTICATED_ACCESS=NOT_USED
SOURCE_ONLY_VERIFIED=YES
```

Adam H. Grimes 的作者原始公开博客中，`Failure Test（失败测试/失败突破反转）`
是本次有限材料内最接近完整循环的单一家族：它明确给出价格结构、双向收盘进场、
初始止损概念，并展示了失败/跳空风险。它仍不能成为机器策略：来源没有固定参考
支撑/阻力或枢轴如何构成、何为“立即”反转、持仓后失效、余仓退出和时间退出。

这是一项成功的负向来源语义结论；没有创建 Playbook Contract、机器实现、E07 接线、
Primary Freeze、StrategyIdentity 或真实/模拟候选结果登记。

## 有界公开材料清单与停止

只检查以下三个信息面后停止：作者原始博客、MarketLife 的公开访问/商业面、以及被
作者博客直接链接或用于解释选中家族的原始公开文章。所有获取均为直接 HTTP 200、
无需账号；每项字节哈希和大小已绑定在 source bundle 中，原始 HTML 未提交。

| 材料 | 用途 | 结果 |
|---|---|---|
| `Marketlifetrading.com and the free trading course` | 课程来源与迁移关系 | 作者原始公开帖；课程内容本身不作为免登录材料。 |
| `The Completely New and Revised Trading Course…` | 访问状态 | 作者明确课程需要注册，排除。 |
| `Fundamental Trading Patterns` | 家族筛选 | 失败测试是以价格结构为核心的反转类。 |
| `Trading Pattern: the Failure Test` | 核心 setup / entry / stop | 选中 bundle。 |
| `The Failure Test` | 语境、风险、失败可见性 | 选中 bundle。 |
| `Managing the Failure Test in AAPL` | 1R 部分止盈、跟踪止损示例 | 选中 bundle。 |
| `Current Technical Situation: S&P 500` | 1R 部分止盈、余仓跟踪示例 | 选中 bundle。 |
| `Reader question: How to handle exits?` | 退出的负向语义证据 | 选中 bundle。 |

MarketLife 的公开 `pullbacks` 页面是付费课程销售页，未购买。作者的免费课程虽称免费，
但要求注册，按本包 `FREE_PUBLIC_UNAUTHENTICATED` 锁定规则未进入内容提取。

停止条件已满足：作者原始材料已覆盖 setup、entry、stop、管理与退出缺口；继续无边界
搜索不能合法填补来源没有固定的语义。付费书籍、课程、订阅、账号均未使用。

## 家族筛选

| 家族 | 处置 | 仅来源维度理由 |
|---|---|---|
| Pullback | 未选 | 多个进场/管理选择仍由交易者裁量；相关 MarketLife 大课为付费。 |
| Breakout | 未选 | 多种进场样式并存，且作者明确反对简单的“回到突破位就退出”规则。 |
| Failure Test | 进入语义完成 | 价格结构、双向收盘进场、初始止损、失败可见性最完整，无外部数据依赖。 |
| Anti / Snap Pullback | 未选 | 原文允许多种基于指标和多时间框架动量的定义，不能形成唯一当前数据闭环。 |

排序没有使用收益、胜率、PnL、Sharpe、回测、验证或任何候选结果。

## 来源声明、项目解释与可观测性

完整 13 条 claim corpus 与已验证的 `SOURCE_ONLY` 会话在：

- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_GRIMES_FAILURE_TEST_SEMANTIC_V0_1.json`
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_GRIMES_FAILURE_TEST_SEMANTIC_V0_1.json`

| 交易循环字段 | 语义分类 | 当前数据可观测性 | 结论 |
|---|---|---|---|
| 失败测试定义 | `PINNED_SOURCE_EXPLICIT` | `OBSERVABLE_NOW` | 价格越过水平后反转的概念明确。 |
| 参考水平 | `UNKNOWN_SOURCE_SEMANTIC` | `PARTIALLY_OBSERVABLE` | 原文说 support/resistance/pivot，未定义如何构造或选择。 |
| 反转速度 | `UNKNOWN_SOURCE_SEMANTIC` | `PARTIALLY_OBSERVABLE` | “immediately/quickly”没有时间或柱数边界。 |
| 双向进场 | `PINNED_SOURCE_EXPLICIT` | `OBSERVABLE_NOW` | 失败柱收盘进场，方向对称。 |
| 初始止损 | `PINNED_SOURCE_EXPLICIT` | `OBSERVABLE_NOW` | 放在新极值处或略外；最小跳动和订单子类型是机器细节。 |
| 首次止盈 | `PINNED_SOURCE_EXPLICIT` | `OBSERVABLE_NOW` | 1R 时部分止盈，但 25%–50% 不是唯一 PRIMARY。 |
| 持仓后失效 | `UNKNOWN_SOURCE_SEMANTIC` | `UNKNOWN` | 原文明确说管理没有唯一答案。 |
| 余仓退出 | `UNKNOWN_SOURCE_SEMANTIC` | `UNKNOWN` | 仅称跟踪/收紧止损，未定义触发、基准、更新和全平条件。 |
| 时间退出 | `UNKNOWN_SOURCE_SEMANTIC` | `NOT_APPLICABLE` | 没有持仓时长或收盘退出规则。 |
| 失败/不交易 | `PINNED_SOURCE_INFERRED` | `PARTIALLY_OBSERVABLE` | 有亏损与跳空风险材料，但没有确定性不交易清单。 |
| 时间框架/品种 | `UNKNOWN_SOURCE_SEMANTIC` | `PARTIALLY_OBSERVABLE` | 泛称全时间框架，不等于明确的一分钟中国期货范围。 |

项目拥有的一分钟 OHLCV、受治理交易时段、E07 映射和 Qualified Eligibility View 只能说明
部分价格输入可见；它们不能补造参考水平、反转窗口或退出语义，更不能代替 DOM、新闻、
宏观或 MarketLife 专有工具。

## 最小阻塞集与禁止的后续动作

```text
BLOCKING_FIELDS=
  REFERENCE_LEVEL_SEMANTICS
  REVERSAL_TIMING_WINDOW
  POST_ENTRY_INVALIDATION
  REMAINDER_EXIT_AND_TIME_EXIT
```

“一跳止损偏移”“Stop/OCO 的订单细节”等属于可版本化的普通机器约定；上表四项却定义
了策略本身。当前来源没有把它们钉死，不能由项目擅自补写。

Grimes 的宽泛时间框架表述和其股票、外汇、商品例子，不构成对 `cu/al/ni/au/ag/rb` 的
来源明确授权。由于完整循环已经失败关闭，本包没有尝试 `PROJECT_CHINESE_FUTURES_TRANSFER`；
不存在任何微观结构假设或 K 线代理。

只有出现新的、免费、公开、无需认证、可归因于作者或最近原始来源的材料，且能直接固定
一个以上述最小阻塞字段，才可以创建新的有界重开包。历史表现、回测结果或事后吸引力
永远不是重开条件。

## 研究波与统计边界

本包没有机器就绪家族，故没有新增未来 outcome-bearing Research Wave 的分母、没有注册
候选假设，也没有改变项目的 prospective statistical research-design blocker。若未来
来源改变此结论，最多先进入新的 `PRE_WAVE_DRAFT`；在新治理的统计前提存在前，仍不得
产生候选结果。
