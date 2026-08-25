# 江河输入时间周期范围证据复核 V0.1

```text
CURRENT_TEST_TIMEFRAMES=1H__15M__5M
CURRENT_STACK_SCOPE=STAGE_A_CAPABILITY_TEST_PROTOCOL__NOT_JIANGHE_PERMANENT_DOCTRINE
CURRENT_1H_15M_5M_IS_TEST_PROTOCOL=YES
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
JIANGHE_HIGHER_TIMEFRAME_EVIDENCE_STATUS=UNRESOLVED_IN_CURRENT_PRIMARY_EVIDENCE
CAN_WE_CONCLUDE_JIANGHE_ONLY_USES_1H_AND_BELOW=NO
CAN_WE_CONCLUDE_HIGHER_TIMEFRAME_IS_REQUIRED=UNRESOLVED
NEXT_INPUT_PROTOCOL_RECOMMENDATION=OWNER_RESEARCH_DECISION_REQUIRED_AFTER_EVIDENCE_REVIEW
```

## 问题 A：为何当前使用 1H / 15m / 5m

当前 downloaded-Kline pilot 的 `window_counts` 和 Stage-A frozen stimulus 采用
`1H / 15m / 5m`，用于在同一受控、point-in-time K 线输入上比较模型能力。这是
当前测试协议的输入选择；现有 mutable authority 没有把它冻结为江河交易方法的
永久周期组合。特别是 `CURRENT_STATE.md` 与 `PROJECT_BRAIN_RUNTIME_BRIEF.md` 均记载
`JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED`，不能把 pilot 输入设计提升为
project 的江河语义规则。

## 问题 B：是否有高于 1H 的证据

当前 PRIMARY 冻结尚未请求，所以严格回答只能是
`UNRESOLVED_IN_CURRENT_PRIMARY_EVIDENCE`。但 source-backed、经复核的材料明确否定
“江河只看 1H 及以下”的结论：它们可为下一个 input-protocol research decision
提供证据，不可在本轮直接把 4H/日线加入 paid input。

| 层级 | IDs / source | 有限原意 | 本轮可得结论 |
| --- | --- | --- | --- |
| source-backed claim | `JH-CLM-039-001`; case `JH-CASE-039-001`; source `039 / BV1xGcxzPECD` | 明示常用搭配含 `4H+15m`、`1H+5m`、`15m+1m`，并提醒级别差过大或过小都会削弱执行质量。 | 支持江河来源材料使用过高于 1H 的背景组合。 |
| source-backed claim | `JH-CLM-012-SP01`, `JH-CLM-012-SP02`; source `012 / BV1Gv1fBYEp9` | 4H 关键区附近先观察；15m 的变化可对应 4H 回调，且不把单根反向 K 线夸大为大周期反转。 | 支持多周期、分阶段解读。 |
| source-backed claim | `JH-CLM-095-001`, `JH-CLM-095-003`; case `JH-CASE-095-001`; source `095 / BV1LCG36dEsR` | 4H 从强转弱、不能创新高；按 4H→1H→5m 逐级读取，接近关键区等待新信号。 | 支持该案例使用 4H 背景，但不推出每次交易都必须使用。 |

以上在 current primary mapping 中均仍为 `primary_eligible=false` 或尚未纳入已冻结
PRIMARY；这正是本 review 不使用 `SUPPORTED_BY_PRIMARY_EVIDENCE` 的原因。它们也没有
提供“日线或更大周期在全部场景必需”的证据。

本结论不创建任何新交易规则、不改动当前 paid-call input，且不授权 large batch。
