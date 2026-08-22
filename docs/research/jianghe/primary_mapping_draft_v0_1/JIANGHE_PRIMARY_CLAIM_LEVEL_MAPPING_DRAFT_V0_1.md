# 江河 PRIMARY 逐条映射草案 V0.1

```text
ARTIFACT_STATUS=PRE_FREEZE_NON_FINAL
IDENTITY_BINDING_STATUS=PENDING_REBIND
PRIMARY_FREEZE=NO
RESULT_SURFACE_ACCESS=NOT_USED
TOTAL_CLAIMS=352
REVIEWED=352
READY_FOR_PRIMARY_FREEZE_DRAFT_COUNT=0
STOP_SOURCE_AMBIGUOUS_COUNT=66
STOP_SOURCE_CONFLICT_COUNT=3
STOP_OBSERVABILITY_GAP_COUNT=0
STOP_IDENTITY_INCOMPLETE_COUNT=283
UNMAPPED=0
GUESSED_UNKNOWN=0
```

此目录是对绑定的 352 条来源声明逐条生成的非最终映射草案。它不重用历史身份，
也不生成任何最终 PRIMARY 分支身份。待主线完成当前知识包重绑定后，集成线必须重新
运行生成器与校验器，再决定是否进入任何后续冻结审查。

映射规则：每条记录保留来源含义、家族范围、已知 UNKNOWN/矛盾、可观察性和一个
失败闭合处置。来源未唯一说明的语义保持 UNKNOWN；来源冲突不由本草案和解；当前
观察面未提供的人类状态输入保持为可观察性缺口。

正式 preparation schema 中的 `knowledge_pack_identity` 与 `primary_branch_identity`
在本草案均为 null：当前 root authority 要求 rebind，且本分支没有冻结权限。

## 与正式 schema 的字段对应

| 正式字段 | 草案字段 | 重绑定前的处理 |
| --- | --- | --- |
| `selected_interpretation_text` | `source_meaning` | 保留绑定声明的来源含义 |
| `interpretation_evidence_basis` | `source`、`review_evidence` | 保留来源锚点与审查权威 |
| `ambiguity_preserved`、`unknown_ids`、`contradiction_ids` | `known_ambiguity`、`unknown_preservation` | 保留，不做项目和解 |
| `observability_status`、`observability_missing_inputs` | `observability` | 保留当前观察面判断 |
| `primary_branch_version` | `primary_branch_version` | 标为 `DRAFT_V0_1_NON_FINAL` |
| `knowledge_pack_identity`、`primary_branch_identity` | 同名字段 | 均为 null，等待主线重绑定后才能合法填入 |

可复核命令：

```powershell
python tools/build_jianghe_primary_claim_mapping_draft_v0_1.py --check
python tools/validate_jianghe_primary_claim_mapping_draft_v0_1.py
```
