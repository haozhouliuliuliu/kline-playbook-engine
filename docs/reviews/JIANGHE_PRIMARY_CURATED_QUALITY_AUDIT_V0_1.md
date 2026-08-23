# 江河 PRIMARY curated quality 对抗审计 V0.1

```text
AUDIT_STATUS=FAIL_CLOSED_MATERIAL_FINDINGS
AUDIT_DATE=2026-08-23
AUDIT_MODE=READ_ONLY_ADVERSARIAL
REGISTRY_MODIFIED=NO
PRIMARY_FREEZE=NO
OUTCOME_ACCESS=NO
TOTAL_RECORDS=352
READY_POPULATION=340
READY_REVIEWED=74
STOP_POPULATION=12
STOP_REVIEWED=12
TOTAL_REVIEWED=86
```

## 1. 审计对象与方法

只读审计对象：

`docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_CURATED_REVIEW_V0_3_IDENTITY_BOUND.jsonl`

方法分三层：

1. 运行既有独立 validator 与 deterministic build check，确认 352 条身份、来源绑定、
   UNKNOWN/contradiction 链接和机械生成一致性；
2. 100% 阅读全部 12 条 STOP，核对停止原因、authority link、observability 与
   machineability 是否一致；
3. 从按 `claim_id` 排序的 340 条 READY 中等距系统抽取 60 条，再并入所有抽到范围外
   的 READY UNKNOWN-linked、`SOL_REVIEW_REQUIRED`、各 family、各 machineability 与
   observability 代表项，去重后形成 74 条 READY 对抗样本。

最终样本覆盖 63 个 source ordinal；family 出现次数为 A=27、B=18、C=10、D=24，
另有无 family 的记录 27 条。machineability 覆盖
`DIRECTLY_PROGRAMMABLE=16`、`MULTI_CASE_INFERABLE=38`、
`HUMAN_DISCRETION_REQUIRED=13`、`NOT_YET_UNDERSTOOD=7`；
observability 覆盖 `SUPPORTED_BY_GOVERNED_INPUTS=64` 与
`NOT_APPLICABLE_AUDIT_ONLY=10`。READY 样本包含全部 10 条 READY UNKNOWN-linked；
contradiction-linked 记录全部位于 STOP，已由 STOP 全检覆盖。

## 2. 74 条 READY 样本

```text
JH-CLM-001-001, JH-CLM-001-SP01, JH-CLM-001-SP02, JH-CLM-002-001,
JH-CLM-003-SP02, JH-CLM-004-SP03, JH-CLM-005-001, JH-CLM-006-002,
JH-CLM-007-F03, JH-CLM-009-SP02, JH-CLM-011-SP02, JH-CLM-014-SP01,
JH-CLM-016-F01, JH-CLM-017-F03, JH-CLM-018-F02, JH-CLM-019-SP04,
JH-CLM-020-002, JH-CLM-020-SP02, JH-CLM-021-003, JH-CLM-021-SP02,
JH-CLM-024-001, JH-CLM-024-002, JH-CLM-024-SP03, JH-CLM-026-SP02,
JH-CLM-028-001, JH-CLM-029-004, JH-CLM-030-003, JH-CLM-031-001,
JH-CLM-032-004, JH-CLM-034-004, JH-CLM-036-004, JH-CLM-039-003,
JH-CLM-042-001, JH-CLM-043-003, JH-CLM-045-003, JH-CLM-047-001,
JH-CLM-049-002, JH-CLM-050-002, JH-CLM-051-002, JH-CLM-052-003,
JH-CLM-054-002, JH-CLM-055-004, JH-CLM-057-002, JH-CLM-058-003,
JH-CLM-060-001, JH-CLM-061-004, JH-CLM-063-001, JH-CLM-066-002,
JH-CLM-068-001, JH-CLM-069-FINAL, JH-CLM-072-002, JH-CLM-074-002,
JH-CLM-076-002, JH-CLM-078-002, JH-CLM-078-008, JH-CLM-079-003,
JH-CLM-081-002, JH-CLM-083-001, JH-CLM-084-004, JH-CLM-085-004,
JH-CLM-086-002, JH-CLM-087-001, JH-CLM-088-004, JH-CLM-090-002,
JH-CLM-091-003, JH-CLM-093-003, JH-CLM-093-005, JH-CLM-094-002,
JH-CLM-094-003, JH-CLM-096-001, JH-CLM-097-003, JH-CLM-099-F01,
JH-CLM-099-F02, JH-CLM-099-F03
```

## 3. 全部 12 条 STOP

```text
STOP_SOURCE_AMBIGUOUS=JH-CLM-006-SP03,JH-CLM-078-FINAL
STOP_SOURCE_CONFLICT=JH-CLM-026-SP04,JH-CLM-030-001,JH-CLM-030-FINAL,JH-CLM-079-006,JH-CLM-079-FINAL
STOP_OBSERVABILITY_GAP=JH-CLM-038-003,JH-CLM-048-001,JH-CLM-048-F01,JH-CLM-090-004,JH-CLM-096-002
```

这 12 条均保留了真实停止原因：50/50 分类无唯一 tie-break；评分 `>3` 与 `>=3`
冲突；止损文字—视觉冲突；或缺少个人专注/精神状态等当前受治理输入。相关
UNKNOWN/contradiction 链接未被静默消解，observability 与 disposition 一致。

## 4. 实质发现

### Q-01：5 条 READY 仍声明 `SOL_REVIEW_REQUIRED`

以下记录把来源审查状态保留为 `SOL_REVIEW_REQUIRED`，却同时给出
`READY_FOR_PRIMARY_FREEZE`：

```text
JH-CLM-005-001
JH-CLM-020-002
JH-CLM-021-003
JH-CLM-024-001
JH-CLM-024-002
```

其中包含 `DIRECTLY_PROGRAMMABLE` 的来源数字、待固定的适用范围/比例/边界，不能在
状态语义未澄清前视为可冻结。现有 validator 只校验
`semantic_readiness -> pre_freeze_disposition`，没有阻止这一交叉字段冲突。

### Q-02：现有“逐条 review”证据可被模板机械生成

对全部 352 条做结构归一后：

- `review_rationale` 的 352/352 条都精确等于字段插值模板；
- READY 的 `semantic_interpretation.interpretation` 340/340 条都只是
  `source_meaning` 外包一层 claim-id 引用；
- 删除 claim id 后，352 条 operationalization 只剩 7 个固定句型；
- 因此“352 条 rationale 均唯一”主要可由 claim id 和字段值插入产生，不能作为
  独立逐条审查已经发生的充分证据。

样本中的 `source_meaning` 和 ambiguity 内容本身是多样的，且抽检未发现把 UNKNOWN
阈值静默补成数字、把案例数字升级成全局规则、或用 outcome 选择分支；所以本发现
不是断言 340 条语义必然错误，而是指出当前 artifact 无法排除“模板化伪逐条 review”。

## 5. 正向结果与边界

- 既有 validator 输出 `PRIMARY_MAPPING_IDENTITY_BOUND_VALID=YES`；build `--check`
  通过；352 条唯一、排序、来源/claim manifest/knowledge pack identity 绑定一致；
- 12 条 STOP 均正确失败闭合；74 条 READY 样本覆盖任务要求的语义与可操作性层次；
- registry 仍明确 `primary_semantics_frozen=false`、`primary_eligible=false`；
- 本审计未修改 curated JSONL、branch registry 或任何 PRIMARY authority。

由于 Q-01 是确定的状态冲突，Q-02 又使“显式逐条审查完成”缺少独立证据，本轮质量
审计必须 `FAIL_CLOSED`。修复应由拥有 PRIMARY registry 的 integration lane 完成；
本 lane 不越权改写语义或冻结 PRIMARY。
