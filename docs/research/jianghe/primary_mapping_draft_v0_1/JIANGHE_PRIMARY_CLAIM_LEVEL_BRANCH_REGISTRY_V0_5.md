# 江河 PRIMARY identity-bound pre-freeze branch registry V0.5

```text
ARTIFACT_STATUS=PRE_FREEZE_NON_FINAL
CURATION_MODEL=EXPLICIT_CLAIM_BY_CLAIM_REVIEW
GENERATOR_ROLE=MECHANICAL_VALIDATION_AND_SERIALIZATION_ONLY
KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
IDENTITY_BINDING_STATUS=BOUND_CURRENT_ACTIVE_IDENTITY
BRANCH_IDENTITIES_DETERMINISTIC=YES
PRIMARY_FREEZE=NO
JIANGHE_PRIMARY_ELIGIBLE=NO
OUTCOME_ACCESS=NO
TOTAL_CLAIMS=352
CLAIM_LEVEL_RECORDS_REVIEWED=352
READY_FOR_PRIMARY_FREEZE=340
STOP_SOURCE_AMBIGUOUS=2
STOP_SOURCE_CONFLICT=5
STOP_OBSERVABILITY_GAP=5
STOP_IDENTITY_INCOMPLETE=0
UNMAPPED_CLAIMS=0
DUPLICATE_CLAIM_ASSIGNMENTS=0
HIDDEN_ALTERNATIVES=0
OUTCOME_REFERENCES_USED_FOR_BRANCH_SELECTION=0
UNKNOWN_FILLED_BY_PROJECT_GUESS=0
SOURCE_CONFLICTS_SILENTLY_RESOLVED=0
SOURCE_TEXT_REWRITTEN=0
```

该 registry 由 352 条 identity-bound 策展审查记录机械生成。生成器不根据类别词、
machineability（机器化标记）或歧义关键词裁决语义，只绑定正式 schema、当前 active
knowledge pack、claim manifest 与已审查字段，并生成稳定 branch identity。

`primary_branch_identity` 是对每条 branch object 去除自身 identity 字段后的规范 JSON
执行 SHA-256 得到。它证明对象内容可确定重算，不代表 PRIMARY 已冻结，也不代表 AI
市场决策必须是固定输出。

所有真实 STOP 保持为一等记录；数量由逐条 source review 得出，不以 V0.3 的 340/12
为目标。UNKNOWN、来源冲突和观察面缺口均未被填平。来源文本及锚点仍逐字绑定，
不因包含收益或结果等普通来源语言而改写。

可复核命令：

```powershell
python tools/build_jianghe_primary_claim_mapping_draft_v0_1.py --check
python tools/validate_jianghe_primary_claim_mapping_draft_v0_1.py
```
