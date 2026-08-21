# 前瞻过程假设设计闭合 V0.1

```text
PROSPECTIVE_PROCESS_ASSUMPTION_DESIGN=NO_GOVERNABLE_A_B_ASSUMPTION_FOUND
STATISTICAL_BLOCKER_CLASS=RESEARCH_DESIGN_LIMIT_NOT_ENGINEERING_DEFECT
FROZEN_ESTIMAND=theta=E[S_d]/E[C_d]
FROZEN_NULL=E[S_d]<=0
CANDIDATE_OUTCOME_DATA_USED=NO
```

本次只审查项目可以预先执行的采集/部署设计；不重跑旧统计方法、不修改冻结协议。

| 设计 | 能否保证所需过程假设 | 是否保持总体目标 | 结论 |
|---|---|---|---|
| 随机观察/部署 | 只随机“是否看见或参与”，不能随机市场的 `S_d` 条件均值、尾部或时间依赖 | 加权后仍需市场过程假设 | REJECT |
| 预排稀疏抽样 | 不能令不同时点市场结果独立；只改变被观测子序列 | 若按有限已实现时点推断则已改为 finite-population target | REJECT |
| 随机信号参与 | 随机化的是执行选择，不是同一策略在市场中的潜在收益生成过程 | 产生的是参与/不参与比较的因果问题，不是冻结 `E[S_d]` | REJECT |
| 有限期随机化检验 | 精确性依赖可归因的 sharp null 和固定潜在结果 | 检验随机化分配/有限总体，不给出冻结随机总体均值的顺序保证 | REJECT |
| 确定性批次 | 只是分组，既不提供独立簇也不提供已知依赖界 | 仍需未治理的市场依赖假设 | REJECT |
| 强制风险界/有界分数 | 可限制仓位或损失暴露，但不能在不改动 `S_d` 定义时限制市场 score 的支撑/尾部 | 截断/裁剪会改 score 或 estimand | REJECT |

随机化推断的精确结论以 sharp null（能补全所有未观察潜在结果）为基础；弱平均零假设并不自动得到相同有效性，见 [Cohen 与 Fogarty](https://academic.oup.com/jrsssb/article-abstract/84/2/295/7056119) 及 [Ding 等的随机化推断讨论](https://pmc.ncbi.nlm.nih.gov/articles/PMC6027661/)。e-process 仍要求预先给出可用的条件过程类，见 [Wang 等](https://academic.oup.com/biomet/article/112/1/asae049/7796539)。

因此后续只有新的可治理过程设计、独立强外部理论依据，或正式协议变更才可重开；不得把此研究设计边界误写为工程缺陷。
