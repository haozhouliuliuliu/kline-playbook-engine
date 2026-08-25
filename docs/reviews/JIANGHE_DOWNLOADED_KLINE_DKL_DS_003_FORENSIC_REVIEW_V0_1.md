# DKL-DS-003 离线取证复核 V0.1

```text
CASE=DKL-DS-003
HISTORICAL_ATTEMPT_IMMUTABLE=YES
ATTEMPT=DOWNLOADED_KLINE_V0_1:DEEPSEEK:DKL-DS-003:001
CONTRACT=SHFE.al2509
DECISION_TIME=2025-03-25T15:00:00+08:00
PILOT_PLAN_IDENTITY=e4dd70c8938995ec57715abc28bcf1784d9a1e4d2c6bd7e61add83a224d8582a
SOURCE_1M_INPUT_IDENTITY=da5377c96d5b8744bec9b62c92ec4ef7f19531754b85a5e5d8084536e1b08e8e
SOURCE_1M_BAR_COUNT=465
STRUCTURED_OBSERVATION_IDENTITY=3b1ad4131df6aa9c90c39277943218f53666f69a5221944f9c90aa34eb078c2e
PNG_SHA256=2517f76e51bb530e989020465327ef226ca6a4b71c6f63af417bf8290e6a154e
MECHANICAL_REVIEW_IDENTITY=8d81c7fbb8bea20e2705a23783eacffd9cabaa9fa21082a2ea0207ef5766425b
OUTCOME_ACCESS=NO
FUTURE_ACCESS=NO
PAID_CALLS_MADE=0
```

## 机械重建

`tools/review_jianghe_downloaded_kline_dkl_ds_003.py` 只读取 canonical 1m
row 的 `historical_available_at <= decision_time`，并复用当前 session/calendar
authority 的 `TimeframeAggregator`。三组重算结果逐 bar 等于冻结 V0.1
observation；structured identity 与 PNG SHA256 也逐项一致。

| 周期 | 最后一根（同周期零基索引） | 倒数第二根（同周期零基索引） |
| --- | --- | --- |
| 5m | `35`; 14:55–15:00; O20710/H20710/L20700/C20710/V20 | `34`; 14:50–14:55; O20695/H20710/L20690/C20710/V29 |
| 15m | `11`; 14:45–15:00; O20695/H20710/L20690/C20710/V54 | `10`; 14:30–14:45; O20700/H20705/L20690/C20695/V31 |
| 1H | `2`; 13:30–14:30; O20680/H20700/L20670/C20700/V470 | `1`; 10:30–11:30; O20690/H20690/L20660/C20670/V453 |

上表每根均 `is_closed=true`，`close_time <= decision_time` 且
`available_at <= decision_time`。这是交易时段对齐聚合（1H 不是普通自然时钟
resample），没有读取 decision time 后的任何 source row。

## 15m/5m 成交量机械验证

模型声称的对象是最后一根 15m，即 14:45–15:00（V54）。它的唯一合法 5m
constituent bucket 是：14:45–14:50（V5）、14:50–14:55（V29）、
14:55–15:00（V20）。区间连续、完整、均已关闭且可见，机械和为 `5+29+20=54`。

```text
COMPARISON_LEGALITY=LEGAL__EXACT_CONTIGUOUS_INTERVAL_COVERAGE
COMPONENT_VOLUME_SUM=54
TARGET_15M_VOLUME=54
AGGREGATION_RESULT=MATCH
```

因此不存在 session boundary、partial aggregation、availability 或不同 bucket
导致的不可比情形；模型写出的 `5+5+29=39` 不是合法 constituent 映射。

## 当时模型输入与 PNG

V0.1 structured artifact 的 bars 是按 `5m`、`15m`、`1H` 分组，且各组内按
open time 从旧到新排列；它携带 `decision_time`、`close_time`、`available_at`、
`is_closed` 与 timestamp。但是它未把该数组顺序写成语义字段，未显式标出每个
timeframe 的 latest closed bar/index，也未声明跨周期 volume 只能按 exact
constituent bucket 比较。因此数据本身正确，但接口存在通用、可消除的表达歧义。

使用同一 observation 重建的 PNG 已人工检查：每个 panel 的 `BARS` 与
`CLOSED` 数量匹配；5m 最新 bar 位于右侧边界、未被裁切或覆盖；x-axis 可见
`03-25 14:55`；无 off-by-one rendering。PNG 与 structured artifact 的
`source_observation_identity=6c55d51e2cf807e49a591fa84a8ed18b4492ff84d304fa6cd301eb7565cd5e0b`
相同。

## 原始 final answer 的两个事实错误

历史 safe evidence 中的 `MODEL_RAW_FINAL_ANSWER`（未读取或保存 hidden reasoning）包含：

```text
ERROR_1_EXACT_TEXT=“5m 最后一根：O 20695 / H 20710 / L 20690 / C 20710”
ERROR_2_EXACT_TEXT=“三根 5m volume 为 5+5+29=39，两者无法对上”
```

第一句把索引 34 当成索引 35；第二句漏掉 V20 的最后 constituent，并把不存在的
第二个 V5 放入 bucket。safe evidence 的 evaluator 正确标为两项 factual error，
其结论与本次机械复核一致。

```text
ERROR_1=将倒数第二根 5m 当成最后闭合 5m
ERROR_1_ROOT_CAUSE=MULTI_CAUSAL
ERROR_2=把最后 15m 的合法 constituent 错算为 5+5+29，并声称 mismatch
ERROR_2_ROOT_CAUSE=MULTI_CAUSAL
CANONICAL_DATA_CORRECT=YES
AGGREGATION_CORRECT=YES
RENDERING_CORRECT=YES
STRUCTURED_INPUT_CORRECT=YES__SEMANTICS_NOT_EXPLICIT_ENOUGH
INPUT_AMBIGUITY=YES__ORDER_LATEST_AND_BUCKET_RELATION_NOT_EXPLICIT
MODEL_FACTUAL_ERROR=YES
EVALUATOR_ERROR=NO
GENERIC_REPAIR_REQUIRED=YES
GENERIC_REPAIR_DESCRIPTION=DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2 adds explicit per-timeframe oldest-to-newest order, latest/penultimate closed bars, zero-based indexes, PIT eligibility and exact-bucket-only volume comparison semantics.
NEW_INPUT_CONTRACT_SCHEMA_IDENTITY=0057b11939c71f10fa7094db119f5b280e74edd13cb2bb7d40cc29a418c4c68a
HISTORICAL_PILOT_VERDICT_UNCHANGED=YES
```

V0.2 is provider-neutral and case-neutral. It is not injected into the immutable
V0.1 request, does not say any particular bar value is “the answer”, and does not
authorize a rerun of this attempt or a large batch.

## Offline regression and closure

Focused regressions cover latest/penultimate distinction, explicit chronological
order, decision boundary, closed/available-only input, session-break or missing
bucket non-comparability, exact 5m→15m mapping, volume sum, structured/PNG common
source, and future-bar rejection. See
`tests/test_jianghe_downloaded_kline_input_contract.py`,
`tests/test_jianghe_downloaded_kline_pilot.py`, and the targeted mechanical tool.

```text
FORENSIC_VERDICT=MULTI_CAUSAL_DEFECTS_FIXED
PILOT_REVIEW_RESOLUTION=READY_FOR_FRESH_PILOT_V0_2
LARGE_BATCH_AUTHORIZED=NO
```
