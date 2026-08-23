# 江河 PRIMARY 逐条语义审查草案 V0.2

```text
ARTIFACT_STATUS=PRE_FREEZE_NON_FINAL
CURATION_MODEL=EXPLICIT_CLAIM_BY_CLAIM_REVIEW
GENERATOR_ROLE=MECHANICAL_VALIDATION_AND_SERIALIZATION_ONLY
IDENTITY_BINDING_STATUS=PENDING_REBIND
PRIMARY_FREEZE=NO
OUTCOME_ACCESS=NO
TOTAL_CLAIMS=352
SEMANTICALLY_READY_PRE_IDENTITY=340
STOP_SOURCE_AMBIGUOUS=2
STOP_SOURCE_CONFLICT=5
STOP_OBSERVABILITY_GAP=5
IDENTITY_PENDING_COUNT=352
STOP_IDENTITY_INCOMPLETE=340
UNMAPPED=0
GUESSED_UNKNOWN=0
SILENT_CONFLICT_RESOLUTION=0
SOURCE_TEXT_REWRITTEN=0
```

该草案由 352 条显式策展审查记录机械生成。生成器不使用类别词、机器化标签、
歧义备注关键词或其他启发式来决定语义；它只绑定来源与策展字段，并进行稳定序列化和哈希。
独立校验器负责检查逐字段一致、覆盖完整、权威链接存在以及身份仍待重绑定。

来源含义、来源锚点和来源状态按绑定清单原样保存。来源原文即使包含结果相关词语也不改写；
禁止的是项目新增结果字段、结果数据依赖或按结果选择解释。

语义就绪状态与身份就绪状态彼此独立。语义已就绪的记录在身份重绑定前，正式处置仍为
`STOP_IDENTITY_INCOMPLETE`；来源歧义、来源冲突和可观察性缺口则按各自原因失败闭合。

可复核命令：

```powershell
python tools/build_jianghe_primary_claim_mapping_draft_v0_1.py --check
python tools/validate_jianghe_primary_claim_mapping_draft_v0_1.py
```
