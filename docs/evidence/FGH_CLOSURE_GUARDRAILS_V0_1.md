# FGH Closure Guardrails V0.1

> 范围：仅关闭 `AggregationResult` 的正常调用方完整性证据洗白路径
> 候选结果访问：未授权且未使用

## 旧绕过路径

正常 Python 调用方可以直接调用 `AggregationResult._from_aggregation(...)`，从真实的不完整结果中丢弃 `incomplete_buckets`，并把 `expected_bucket_identities` 缩减为剩余完整聚合柱的身份。该伪造对象内部结构自洽，旧共享校验会把它当成完整连续输入交给 EMA/ADX。

## 新不变量

`TimeframeAggregator.aggregate()` 是正常 API 中唯一会登记 `AggregationResult` 的签发方。登记表使用进程内弱引用，以 `id(result)` 定位后仍要求取回值与输入满足 `is` 对象身份相同。

EMA 与 ADX 继续共用 `_validated_feature_input()`。该入口在检查 `incomplete_buckets` 前先验证签发身份：

- 手工调用 `_from_aggregation(...)` 得到的对象未登记，失败关闭；
- 聚合器签发的完整对象可正常计算；
- 聚合器签发的不完整对象仍由连续性检查阻断；
- 调用期间函数参数强持有输入对象，不会因弱登记导致正在校验的对象被回收；
- 对象回收后弱登记自动移除；即使运行时以后复用整数 `id`，`is` 检查也不会把不同对象当成已签发对象。

## 回归测试

`tests/test_fgh_closure_guardrails.py` 覆盖：

1. 真实聚合器产生带缺失预期柱的不完整结果；
2. 手工丢弃不完整证据并构造表面完整的 envelope；
3. EMA 拒绝该伪造对象；
4. ADX 通过同一共享校验拒绝该伪造对象；
5. 真实签发的完整结果可计算 EMA；
6. 真实签发的完整结果可计算 ADX；
7. 真实签发的不完整结果仍因连续性失败关闭。

## 边界声明

```text
NORMAL_CALLER_COMPLETENESS_LAUNDERING=CLOSED
OS_PROCESS_TAMPER_PROOFING=NOT_CLAIMED
LOCAL_PRIVATE_STATE_TAMPER_PROOFING=NOT_CLAIMED
PERSISTENT_ISSUED_STATE=NO
CANDIDATE_OUTCOME_DATA_USED=NO
```

本修复不声称抵抗恶意 Python 内省、直接修改模块私有登记状态或进程内存篡改，也不创建持久登记、数据库、密码服务或新框架。
