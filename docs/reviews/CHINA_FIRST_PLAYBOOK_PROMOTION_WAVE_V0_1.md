# China-first Playbook Promotion Wave V0.1

> 状态：`COMPLETE / SELECTED_SOURCE=NONE / PRE_OUTCOME`
>
> 日期：2026-08-21
>
> 范围：对既有 China-first discovery leads A（付爱民）、B（王少多）、C（张亚楠）执行顺序、公开来源、非结果审查。

## 结论

```text
SELECTED_SOURCE=NONE
SOURCE_RESELECTION_STATUS=COMPLETE_NEGATIVE
NO_CANDIDATE_OUTCOME_USED=YES
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
PAID_OR_AUTHENTICATED_ACCESS=NOT_USED
TOOL_DECISION=USE_EXISTING
```

这是一项完整的负向来源选择结论，不是工程失败。三名候选均未同时满足：公开原始/最近原始来源足以支撑可追溯语义，且存在一个可由当前 `1-minute OHLCV + governed sessions + E07 + Qualified Eligibility View V1` 忠实表达的完整、确定性 Playbook family。

没有创建假装“已选来源”的 Source Dossier、正式 source bundle、claim corpus、Playbook Contract、机器实现、synthetic adapter、Primary Freeze、StrategyIdentity 或 locked Research Wave。

## 顺序停止记录

| 次序 | 候选 | Source Dossier 可准入 | 当前数据兼容 family | 结论 |
|---|---|---|---|---|
| A | 付爱民 | `YES_SOURCE_LEVEL_ONLY` | `NO` | A 未达到双重条件，继续 B。 |
| B | 王少多 | `NO` | `NO` | B 未达到条件，继续 C。 |
| C | 张亚楠 | `NO` | `NO` | 已穷尽预先限定集合，停止。 |

比赛身份只保留为 `DISCOVERY_SIGNAL`，不是 `SKILL_EVIDENCE` 或 `PLAYBOOK_VALIDITY_EVIDENCE`；未使用排名、收益、胜率或候选 outcome 进行选择。

## A — 付爱民

- 身份/来源：七禾网/期货中国页面将付爱民作为受访者，三次长访谈均标注“来源：期货中国”；按 `NEAREST_ORIGINAL` 处理，而非独立有效性证据。
- 访问/证据：均免费、无需登录。2026-08-21 直接 HTTP 获取，仅记录定位与响应 SHA-256，不保存全文。
- 失败可见性：`PRESENT`，包含多次大起大落、重仓损失与止损/风险线讨论。

| material | 发布日 | URL | 响应 SHA-256 |
|---|---|---|---|
| `MAT-FUAIMIN-2010-INTERVIEW` | 2010-11-15 | <https://www.7hcn.com/article/54612-1.html> | `e3e7e6f0ea6959570ff7ff3e51487faa59d48b781157e8fd17a1e5f4b3ce3f90` |
| `MAT-FUAIMIN-2012-INTERVIEW` | 2012-09-09 | <https://www.7hcn.com/article/115390-1.html> | `4b18c993c981d63d01ae5fd0094d4cff167aa02aece53f9974811f311cfb2c62` |
| `MAT-FUAIMIN-2013-INTERVIEW` | 2013-12-15 | <https://www.7hcn.com/article/148597-1.html> | `9236efffef5d6a7d28c4cb712e66127cbbf8d6fb4406675805701aafa94d6e42` |

来源明确称其个人指标没有完全量化；中长线判断结合 K 线形态、基本面与产业新闻，且没有固定 setup、确认、入场、初始止损、失效和退出闭环。任何 OHLCV 代理或机器阈值都会是未经授权的语义发明。

```text
SOURCE_DOSSIER_ADMISSIBLE=YES_SOURCE_LEVEL_ONLY
CURRENT_DATA_COMPATIBLE_PLAYBOOK_FAMILY_CANDIDATE=NO
SOURCE_ADMISSION_CLASSIFICATION=DEFER
```

已记录但不推进的相邻家族：`UNQUANTIFIED_PERSONAL_SYSTEM`、`FUNDAMENTAL_AND_KLINE_MEDIUM_TERM_SWING`、`RISK_PROCESS_ONLY`。

## B — 王少多

- 身份/来源：七禾网页面将王少多列为受访者，并明确归因期货日报网；有界公开检索未能固定原始个人采访 URL/页面身份，因此只能是 `DERIVATIVE`。
- 访问/证据：免费、无需登录；2026-08-21 响应 SHA-256 为 `c04b6b2c6e7ed4a59d73f2c3058a5f75fb9c75401427f01485a70ac51373e7e5`。

| material | 发布日 | URL | 分类 |
|---|---|---|---|
| `MAT-WANGSHAODUO-DERIVATIVE` | 2024-01-02 | <https://www.7hcn.com/article/453531-1.html> | `DERIVATIVE` |

失败可见性为 `PRESENT`，但不是完整交易循环的反例记录。核心观察面是现货行情、熟悉品种、信息整理与“开仓逻辑变化”，不是当前数据面可观测的事实；入场、时间框架、初始止损、失效、退出和不交易边界都未固定。

```text
SOURCE_DOSSIER_ADMISSIBLE=NO
CURRENT_DATA_COMPATIBLE_PLAYBOOK_FAMILY_CANDIDATE=NO
SOURCE_ADMISSION_CLASSIFICATION=REJECT_SOURCE_FOR_CURRENT_PROMOTION
```

已记录但不推进：`SPOT_VALUE_AND_FAMILIAR_PRODUCT_DISCRETION`、`OPENING_LOGIC_CHANGE_EXIT_PROCESS`。

## C — 张亚楠

- 身份/来源：七禾网采访合集将张亚楠列为受访者，并说明“期货日报采访内容、七禾网编辑整理”；原始个人采访未被固定，因此只能是 `DERIVATIVE`。
- 访问/证据：免费、无需登录；2026-08-21 响应 SHA-256 为 `b2d657f4ff8736f920dc7f9314524f8b32f8695688e94e536b55066a4d5da65f`。

| material | 发布日 | URL | 分类 |
|---|---|---|---|
| `MAT-ZHANGYANAN-DERIVATIVE` | 2022-12-23 | <https://www.7hcn.com/article/435463-1.html> | `DERIVATIVE` |

失败可见性为 `PRESENT`，但没有完整订单/交易循环反例。核心输入明确包含实地调研、基本面供需判断、未来预期/现货事实的时点，当前没有这些数据，不能用一分钟 OHLCV 伪造；“倒金字塔建仓、设置止盈止损”也没有固定入场、加仓、初始止损、失效、退出或时间框架。

```text
SOURCE_DOSSIER_ADMISSIBLE=NO
CURRENT_DATA_COMPATIBLE_PLAYBOOK_FAMILY_CANDIDATE=NO
SOURCE_ADMISSION_CLASSIFICATION=REJECT_SOURCE_FOR_CURRENT_PROMOTION
```

已记录但不推进：`FUNDAMENTAL_RESEARCH_TIMING`、`INVERTED_PYRAMID_POSITION_MANAGEMENT`。

## 中国期货转移、语义完成与重开条件

没有来源被选中，故不存在可推进的 `SOURCE_EXPLICIT_INSTRUMENT_SCOPE -> PROJECT_INFERRED_TRANSFER_SCOPE`。不能将“交易中国期货”误写成其基本面、调研、盘感或持仓管理能由本项目六个品种的一分钟 OHLCV 自动复现。

本波次不得扩大到其他交易者，也不得重复深挖 A/B/C。仅当出现新的、公开可访问且可归因的原始/最近原始材料，并直接改变已记录最小 blocker，才能在新的有界来源重选包中审查；收益、结果或事后吸引力绝不是重开理由。

机器可读记录：`docs/reviews/CHINA_FIRST_PLAYBOOK_PROMOTION_WAVE_V0_1.json`。
