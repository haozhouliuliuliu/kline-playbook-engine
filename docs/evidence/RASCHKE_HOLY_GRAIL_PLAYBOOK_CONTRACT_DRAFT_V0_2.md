# RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_2

> 状态：有效草案 / NOT_MACHINE_READY
>
> 构建器：`tools/build_raschke_holy_grail_playbook_contract_draft.py`
>
> 机器可读证据：`docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_2.json`

## 分层边界

```text
SOURCE CLAIM
!=
PROJECT INTERPRETATION
!=
MACHINE OPERATIONALIZATION
```

V0.2 绑定现有 SOURCE_ONLY 证据中的 27 条来源声明。下列内容只在来源实际固定的范围内保留为来源事实：14 周期 ADX、ADX 初始大于 30 且上升的概念、20 周期 EMA 概念、回撤/触碰概念、前一柱高点上方买入止损单、成交后以新形成摆动低点为保护止损、盈利增长时跟踪止损，以及多时间框架性质。

V0.2 没有把旧项目解释提升为来源事实，没有建立机器实现层，也没有选定任何 PRIMARY（唯一主解释）。

## 明确未解决项

- `FGH-GATE-01`：EMA 价格基准及精确触碰语义；
- `FGH-GATE-02`：ADX 上升窗口及其相对回撤的时序；
- `FGH-GATE-03`：EMA/ADX 数值实现政策；
- `FGH-GATE-04`：同柱触碰 EMA 与入场触发的先后；
- `FGH-GATE-05`：同柱成交与保护止损的先后及执行时序模型；
- `FGH-GATE-06`：Holy Grail 的单一 PRIMARY 时间框架；
- `NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION`；
- `TRAILING_STOP_MACHINE_DEFINITION`；
- `EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION`。

## 确定性验证结果

当前验证器必须返回以下阻塞族：

- `UNRESOLVED_CRITICAL_AMBIGUITY`；
- `CLAIM_PRIMARY_MISSING`；
- `REQUIRED_INPUT_NOT_FULLY_OBSERVABLE`；
- `MACHINE_OPERATIONALIZATION_MISSING`；
- `MULTIPLE_TIMEFRAMES_UNRESOLVED`。

```text
HOLY_GRAIL_MACHINE_READY=NO
PRIMARY_FREEZE_READY=NO
STRATEGY_IDENTITY_CREATED=NO
OUTCOME_TEST_REGISTERED=NO
CANDIDATE_OUTCOME_DATA_USED=NO
```
