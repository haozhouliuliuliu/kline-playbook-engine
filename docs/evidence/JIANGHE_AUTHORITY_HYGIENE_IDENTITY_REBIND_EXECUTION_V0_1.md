# 江河 authority hygiene → identity rebind 执行证据 V0.1

> 日期：2026-08-23
> 范围：authority hygiene 后当前 active bundle 的确定性 identity rebind 执行
> 不含：候选结果、Development 表现、Validation、Final、Shadow、Broker、真钱

## 结论

```text
REBIND_STATUS=COMPLETE
SOURCE_SEMANTICS_CHANGED=NO
BUILDER_DOUBLE_RUN_DETERMINISTIC=YES
SOURCE_ONLY_TECHNICAL_DENIAL=PASS
OUTCOME_ACCESS=NO
PRIMARY_FREEZE=NO
CURRENT_ACTIVE_SOURCE_ONLY_VERIFICATION=YES
```

本次执行确认：江河 V1.1 来源语义未改变；当前 active 知识包与 SOURCE_ONLY 证据由
canonical builder 在最新 `main` 上确定性重建；所有受保护结果访问面技术性拒绝
（`DENIED / SOURCE_ONLY_TECHNICAL_DENIAL`）；PRIMARY 未冻结，`JIANGHE_PRIMARY_ELIGIBLE=NO`。

机器可读证据：
- `docs/evidence/JIANGHE_AI_TRADER_FOUNDATION_V0_1.json`
- `docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json`

## 权威 identity（canonical builder 实际输出）

```text
KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
CLAIM_MANIFEST_RECORDS=352
CASE_MANIFEST_IDENTITY=06dc398086ada39da0214230dcff015561592ea55f041b31fdf0f58258638ac1
CASE_MANIFEST_RECORDS=80
SOURCE_MATERIAL_MANIFEST_IDENTITY=b883fe2aaeda1aedb1317b5ac39840ab18425016293515931d3ed64d8a206e6c
SOURCE_MATERIAL_MATERIAL_COUNT=22
SOURCE_BUNDLE_HASH=87983a6f8376baa8419ca92118d325c5f5a224165bbe056fe82337fa7eef6037
SOURCE_BUNDLE_IDENTITY=1619b05272aaaad4a25ce9f35fdde764506ed70a9118e33b9bd42b16bbfa1e3b
SESSION_IDENTITY=da7c00ffa0b90035e9bec10ad829e180f085c29cfbd05875797ad2db3b589552
SESSION_BINDING_HASH=NOT_A_DISTINCT_OUTPUT_FIELD__SESSION_EXPOSES_SOURCE_BUNDLE_HASH_ONLY
```

注：`SESSION_BINDING_HASH` 不是 builder 输出的独立字段；会话暴露的绑定哈希是
`source_bundle_hash`。`verification_evidence` 为每次运行重新生成的 issuance token，
不在此固化。

## 确定性验证

`build_jianghe_knowledge_pack_v0_1.py` 与 `build_jianghe_source_only_verification_v0_1.py`
各运行两次：

```text
FIRST_SECOND_RUN_DETERMINISTIC_MATCH=YES
KNOWLEDGE_PACK_DOUBLE_RUN_BYTE_IDENTICAL=YES
SOURCE_ONLY_PAYLOAD_IDENTICAL_EXCEPT_RANDOM_ISSUANCE_TOKEN=YES
SELF_REFERENCE_CHECK=PASS
```

知识包产物两次运行逐字节一致；SOURCE_ONLY 负载除随机 `verification_evidence` issuance
token 外全部一致。自引用一致性验证通过：会话内引用的知识包、claim manifest、case
manifest 身份分别与对应 artifact 的清单身份一致。

## 技术拒绝结果

`SourceOnlyClaimExtractionContext` 未持有候选结果读取面。以下请求逐项进入同一拒绝面：

| 受保护能力 | 结果 |
| --- | --- |
| Candidate outcome runner | `DENIED` |
| Candidate PnL | `DENIED` |
| Validation | `DENIED` |
| Final | `DENIED` |
| Outcome artifact open | `DENIED`，`opened_artifact=NO` |

`SOURCE_ONLY_TECHNICAL_DENIAL=PASS`。

## 与 project brain 早期手工预测的关系

Project brain 在本次执行前给出的 4 个离线手工预测值（source material manifest、
source bundle hash、source bundle identity、session identity）与 canonical builder
实际输出不一致。这些预测值从未出现在任何可达提交历史中，属于 **historical
pre-execution expectation**，不代表任何已存在证据。**canonical builder 输出为最终
authority**；本文件记录的全部确定性 identity 均为 builder 实际输出。

## 历史 pre-hygiene 身份

```text
HISTORICAL_PRE_HYGIENE_KNOWLEDGE_PACK_IDENTITY=3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5
HISTORICAL_PRE_HYGIENE_SOURCE_ONLY_VERIFICATION=PASS
```

旧身份与旧 SOURCE_ONLY PASS 保留为历史 pre-hygiene 证据，不再作为当前 active bundle
身份。审查 authority：`docs/reviews/JIANGHE_AUTHORITY_HYGIENE_IDENTITY_REBIND_REVIEW_V0_1.md`。

## 边界

```text
SOURCE_SEMANTICS_CHANGED=NO
OUTCOME_ACCESS=NO
PRIMARY_FREEZE=NO
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```
