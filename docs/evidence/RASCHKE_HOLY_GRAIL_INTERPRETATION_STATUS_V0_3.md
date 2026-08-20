# RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_3

> 状态：OWNER_DECIDED_FGH / 非语义冻结 / NOT_MACHINE_READY
>
> 决定依据：`docs/reviews/FGH_SEMANTIC_GATE_OWNER_APPROVAL_2026-08-20.md`（OWNER_APPROVED_BINDING，2026-08-20）
>
> 父版本（历史不可变）：`RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_2.md` 保持不变。

## 当前结论

Holy Grail 具备来源忠实、可版本化的 Playbook 草案，且 F/G/H 语义门已由 Owner 批准决定。V0.3 是**当前澄清草案**，
不是正向就绪提升。机器实现层仍未建立，故尚不具备机器就绪条件；若干正常的结果前操作化前提仍显式开放并失败关闭。

## 来源事实与项目解释

来源固定的指标周期、阈值、EMA/回撤/止损/跟踪/多时间框架概念保留在 SOURCE CLAIM 层（27 条来源声明与 V0.2 / SOURCE_ONLY
证据一致）。以下 Owner 批准的工程约定记录在 PROJECT INTERPRETATION 层并显式标记为 INFERRED 机器约定，而非来源声明：

- prior-completed-bar 可得的 close 基准 EMA 触碰约定（当前柱收盘前视禁止）；
- ADX 作为回撤前初始背景条件（`>30 且上升`），触碰柱不必上升；
- SMA 种子 EMA、Wilder ADX 初始化、Decimal 算术、6 位 `ROUND_HALF_UP` 量化、版本化身份绑定数值政策；
- 同柱触碰->入场 与 同柱成交->保护止损 均失败关闭为 `AMBIGUOUS_INTRABAR_SEQUENCE`；
- 完成柱保守时序模型，交易所驻留柱内时序不声称，下柱才激活保护止损的旧约定被拒绝；
- BASE 为来源主分支，30/60/120 分钟仍为来源备选；
- 摆动低点/高点采用分形枢轴显式右确认定义（同柱可用禁止、空头镜像）；
- 跟踪止损未采纳（不发明任何跟踪算法，结果调优禁止）；
- 推至新高退出仅作可选版本化变体，非 PRIMARY（结果救场禁止）。

## 仍开放的操作化前提

```text
HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL=OPEN
HOLY_GRAIL_ADX_RISING_WINDOW=OPEN_VERSIONED_NON_OUTCOME_CHOICE
HOLY_GRAIL_SWING_CONFIRMATION_COUNTS=OPEN_VERSIONED_NON_OUTCOME_CHOICE
HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION=NOT_ADOPTED
```

这些前提必须由未来显式版本化的非结果决定满足；不得由候选结果调优选择，也不得在本工件中解决。

## 未继承为默认真值的旧工程解释

- 当前柱收盘参与同柱触碰判定（禁止）；
- 触碰柱上一根 ADX 必须上升（非来源权威）；
- 成交后的下一柱才激活保护止损（被拒绝）；
- 任一固定跟踪算法（未采纳）；
- 任一具体 BASE 机器周期映射（未选择）。

```text
MACHINE_READY=NO
PRIMARY_FREEZE_READY=NO
STRATEGY_IDENTITY_CREATED=NO
OUTCOME_TEST_REGISTERED=NO
CANDIDATE_OUTCOME_DATA_USED=NO
```
