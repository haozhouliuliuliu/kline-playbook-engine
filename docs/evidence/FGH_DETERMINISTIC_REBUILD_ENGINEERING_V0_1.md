# FGH_DETERMINISTIC_REBUILD_ENGINEERING_V0_1

> 范围：纯合成、确定性 F/G/H 重建
> 候选结果访问：未授权且未使用

## L-01..L-05 状态

通用工程能力已经能表达显式数值政策、完成柱观察、同柱歧义和版本化身份，但没有替 Holy Grail 选择任何语义：

| Finding | 当前工程状态 | 剩余语义门 |
|---|---|---|
| L-01 | 草案保留 EMA/触碰概念并显式暴露未解决项 | FGH-GATE-01 |
| L-02 | 通用 ADX 可参数化；未定义上升窗口/时序 | FGH-GATE-02 |
| L-03 | `FeatureNumericPolicy` 必须显式提供；无默认 | FGH-GATE-03 |
| L-04 | 通用止损层能表示同柱顺序未知 | FGH-GATE-04 |
| L-05 | 不继承“成交后下一柱激活”默认；同柱顺序可失败关闭 | FGH-GATE-05 |

## L-06..L-18 映射

| Finding | 实现 | 回归证据 | 剩余门 |
|---|---|---|---|
| L-06 | 日线比较官方交易日全部预期起点 | `test_daily_partial_day_is_incomplete` | 无 |
| L-07 | 按权威预期起点枚举零柱会话 | `test_missing_whole_expected_session_is_explicit_incomplete_evidence` | 无 |
| L-08 | 每桶记录预期/实际起点、边界和时长；校验基础周期整数倍 | `test_complete_bucket_proves_constituents_bounds_and_duration`、`test_session_shortened_bucket_never_becomes_complete_by_bar_count` | 无 |
| L-09 | 链式依赖前缀身份绑定全部历史证据 | `test_earlier_source_evidence_changes_dependency_identity_even_when_value_is_same` | 无 |
| L-10 | 聚合与特征序列绑定单一交易所和具体合约 | `test_mixed_concrete_contract_stream_fails_closed` | 无 |
| L-11 | 特征身份绑定实际实现文件字节 | `test_feature_identity_binds_actual_implementation_bytes` | 无 |
| L-12 | EMA/ADX 只接受保留缺口证据的 `AggregationResult` | `test_gap_evidence_cannot_be_dropped_or_computed_as_continuous` | 无 |
| L-13 | 组入口仅物化一次生成器 | `test_one_shot_generator_and_tuple_produce_identical_group_result` | 无 |
| L-14 | 结果绑定触发柱和实际评估前缀 | `test_not_triggered_identity_binds_changed_earlier_evaluated_bar` | 无 |
| L-15 | 只接受受支持模型常量并绑定实际实现字节 | `test_trigger_model_version_mismatch_is_rejected` | 无 |
| L-16 | 明示完成柱保守观察，不声称交易所驻留时序 | `test_completed_bar_observation_never_claims_exchange_resting_chronology` | FGH-GATE-05（Holy Grail 选择） |
| L-17 | 首触发取消兄弟单；同柱双触发保持歧义 | `test_first_unambiguous_trigger_cancels_sibling_before_later_touch`、`test_same_bar_both_touch_is_ambiguous_not_arbitrarily_ordered` | 无 |
| L-18 | Session→聚合→EMA/ADX→草案→OCO→ExecutionObservation→Firewall 合成链 | `test_full_synthetic_chain_preserves_identity_chronology_and_firewall_locks` | FGH-GATE-01..06（PRIMARY 专属部分） |

## 因果链安全结论

- `SessionMetadata.version` 传播到聚合与特征身份；
- 缺失预期柱/窗口阻断特征连续性；
- 特征与止损结果均绑定完整材料依赖；
- Holy Grail 草案保持 `NOT_MACHINE_READY`；
- 未创建 `StrategyIdentity`；
- 未注册或请求 OutcomeTest；
- Validation 请求仍由当前防火墙拒绝；
- 历史最终留出集保持 `FINAL_HISTORICAL_HOLDOUT_LOCKED`。

```text
HOLY_GRAIL_MACHINE_READY=NO
PRIMARY_FREEZE_READY=NO
CANDIDATE_OUTCOME_DATA_USED=NO
```
