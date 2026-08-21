# RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_4

> 状态：MACHINE_READY / PRIMARY_FREEZE_READY / 非语义冻结
>
> 决定依据：`docs/evidence/HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_APPROVAL_2026-08-21.md`
> （OWNER_APPROVED_BINDING，2026-08-21）
>
> 父版本（历史不可变）：`RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_3.md` 保持不变。

## 当前结论

Holy Grail V0.4 已把 V0.3 遗留的 4 个操作化前提全部关闭，并安装了机器实现层
（`src/holy_grail_machine.py`），`validate_contract` 通过，`MACHINE_READY=YES`。
这是**机器就绪**（确定性、来源忠实、可版本化的机器约定已齐备），**不是**语义冻结本身，也
**不是**任何候选结果就绪。PRIMARY_FREEZE_READY=YES 仅表示"可冻结"，冻结是未来显式动作。

## 分层：来源事实 与 项目解释

来源固定的指标周期、阈值、EMA/回撤/止损/跟踪/多时间框架概念保留在 SOURCE CLAIM 层（27 条来源声明与
V0.2 / V0.3 / SOURCE_ONLY 证据逐字一致）。以下 Owner 批准的机器约定记录在 PROJECT INTERPRETATION 层
并显式标记为 INFERRED，而非来源声明：

- BASE=1 分钟（`PROJECT_INFERRED`）：零聚合假设、原生 1m 底稿；30/60/120 分钟保持来源备选、非 PRIMARY；
- ADX 上升窗口=1 步（`PROJECT_INFERRED_VERSIONED_NON_OUTCOME`）：初始回撤前背景柱 `ADX[t]>ADX[t-1]`；
  触碰柱不要求上升；旧"触碰柱上一步上升"规则 `NOT_AUTHORITY`；
- 摆动确认计数=L1_R1（`PROJECT_INFERRED_VERSIONED_NON_OUTCOME`）：3 柱分形，右侧确认柱完成前枢轴不可用，
  同柱可用=NO，空头镜像摆动高点，相等边界不构成枢轴；
- 跟踪止损=SWING_BASED_TRAILING（`PROJECT_INFERRED`）：多头只上移、空头只下移（`MONOTONIC_TIGHTEN_ONLY=YES`），
  无新增距离参数；是来源两个独立陈述（初始摆动低点停损 + "trail stops as profits grow"）拼接成的项目推断，
  绝不是来源声明；
- EMA 触碰/数值政策/同柱时序/完成柱保守时序沿用 FGH-GATE-01..05。

## 机器化语义要点（MACHINE OPERATIONALIZATION）

- 1 分钟 BASE 特征路径：会话权威 1 分钟聚合（零聚合）+ EMA20(close) + Wilder ADX14 + Decimal/6dp
  `ROUND_HALF_UP` 数值政策；
- 完成柱保守时序：仅在完成柱可得时观察证据；禁止当前柱收盘前视；同柱触碰->入场与同柱成交->保护停损
  失败关闭为 `AMBIGUOUS_INTRABAR_SEQUENCE`；
- 初始保护停损绑定：成交后绑定"新形成"的已确认摆动低点/高点；若成交时无已确认枢轴，则如实记录
  `PROTECTIVE_STOP_PENDING`（停损生效延迟，不伪造"成交即有停损"）；
- 摆动跟踪：只用已确认枢轴，单调收紧，更差枢轴忽略，同一枢轴不重复处理，停损替换/OCO 交互确定化；
- 确定性事件排序与全链路身份绑定：参数身份、实现字节身份、特征身份、聚合流身份均进入序列身份。

## 结果边界

```text
MACHINE_READY=YES
PRIMARY_FREEZE_READY=YES
STRATEGY_IDENTITY_CREATED=NO
OUTCOME_TEST_REGISTERED=NO
CANDIDATE_OUTCOME_DATA_USED=NO
RESEARCH_FIREWALL_UNLOCKED=NO
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
```

StrategyIdentity 是否允许创建，须严格按现有 protocol / authority 判断；在 Research Wave / 统计画像 /
canonical 等前置未满足前，StrategyIdentity / outcome registration 保持未开放。
