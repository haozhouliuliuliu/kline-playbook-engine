# 江河 PRIMARY curated quality repair V0.1

```text
ARTIFACT_STATUS=CURATED_REPAIR_COMPLETE_AWAITING_INDEPENDENT_REAUDIT
TOTAL_REVIEWED=352
Q01_REVIEWED=5/5
Q01_REMAINING_CONFLICT_COUNT=0

OLD_DECLARED_READY=340
NEW_READY=340
NEW_STOP_SOURCE_AMBIGUOUS=2
NEW_STOP_SOURCE_CONFLICT=5
NEW_STOP_OBSERVABILITY_GAP=5
NEW_STOP_IDENTITY_INCOMPLETE=0

GUESSED_UNKNOWN=0
SILENT_CONFLICT_RESOLUTION=0
SOURCE_TEXT_REWRITTEN=0
OUTCOME_ACCESS=NO
PRIMARY_FREEZE=NO
PRIMARY_ELIGIBLE=NO

KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940

PROMPT_PACKAGE_PRIMARY_REBIND_REQUIRED_AFTER_V04_INTEGRATION=YES
INDEPENDENT_REAUDIT=NOT_RUN_BY_THIS_WORKER
```

## 修复范围与结论

本轮重新核对 active 352-claim manifest、对应 source finding、source anchor、案例、
UNKNOWN register、contradiction register 与 Sol 复核证据。340 条 READY 与 12 条 STOP
是本轮逐条复核后的结果，不是沿用旧计数作为目标。12 条 STOP 仍作为完整 branch object
保留，其中 2 条为来源歧义、5 条为来源冲突、5 条为当前观察面缺口。

V0.3 保留为历史失败证据，没有覆盖或删除。V0.4 新建 claim-level curated review、
branch registry JSONL 与说明文件，并重新计算 352 个确定性 branch identity。

## Q-01 逐条裁定

| claim | 原始状态 | 复核证据与结论 | V0.4 disposition |
|---|---|---|---|
| `JH-CLM-005-001` | `SOL_REVIEW_REQUIRED` | 同时间画面与语言足以确认：价格进入上方黄色关键区域后向下排斥，进入下方区域后向上排斥。只确认存在、位置和方向；区域边界与排斥强弱阈值仍属人工判断。 | `READY_FOR_PRIMARY_FREEZE` |
| `JH-CLM-020-002` | `SOL_REVIEW_REQUIRED` | 来源先说明未预设止盈，随后“至少 1:1”只描述该案例当时的空间预期。它不是固定止盈、自动平仓条件或跨案例规则。原始错误管理元数据在 source binding 中保留，V0.4 另列有证据的有效修正。 | `READY_FOR_PRIMARY_FREEZE` |
| `JH-CLM-021-003` | `SOL_REVIEW_REQUIRED` | 当前来源所述系统版本明确使用 `RANGE_POSITION_SIZE = 0.5 × REGULAR_POSITION_SIZE`。常规仓位绝对值及未来版本是否沿用均未定义。 | `READY_FOR_PRIMARY_FREEZE` |
| `JH-CLM-024-001` | `SOL_REVIEW_REQUIRED` | 多空方向均适用；A 段至少四根连续同向 K 线，其中至少两根为趋势型 K 线；范围覆盖来源所述流动市场与多个时间框架。巨大单根 K 线替代条件仍为未知。 | `READY_FOR_PRIMARY_FREEZE` |
| `JH-CLM-024-002` | `SOL_REVIEW_REQUIRED` | 两条独立放弃条件得到确认：至少三根连续同向回调 K 线；或 B 在三根以内快速回到、触及或突破 A 起点。不能反推 B 总长度最多两根，混合方向 B 可以更久。 | `READY_FOR_PRIMARY_FREEZE` |

上述五条均绑定
`docs/research/jianghe/JIANGHE_SOL_REVIEW_RESOLUTION_V0_2.md`。source manifest 中的历史
`review_status=SOL_REVIEW_REQUIRED` 不被改写；V0.4 使用独立的
`required_source_review.original_status` 与 `effective_status` 保存历史状态和本轮实际裁定。
另一条 `JH-CLM-030-001` 虽已完成所需复核，但来源冲突仍未解决，因此有效状态为
`REVIEW_COMPLETE_UNRESOLVED_SOURCE_CONFLICT` 并保持 `STOP_SOURCE_CONFLICT`。

## Q-02 根因与结构修复

V0.3 的 material finding 来自三个结构问题：`review_rationale` 可由状态字段插值复现；
READY 语义大多只是 `source_meaning` 外包 claim id；操作化解释集中在少数固定句型。
这使记录看似逐条存在，实际却没有清楚表达每条声明能支持和不能支持什么。

V0.4 把以下内容变成 curated data 的必填机器可读字段：

- `review_basis`：来源、锚点、案例和追加复核证据；
- `claim_specific_reasoning`：来源说了什么、没说什么、支持什么、不支持什么；
- `semantic_boundary`：来源语义、AI 解释约束及为何无需追加解释；
- `operational_boundary`：可机械检查部分、AI discretion（自主判断）边界、受治理观察输入、主观/未知项和未来观察能力；
- `authority_links` 与 `alternative_analysis`：显式 UNKNOWN、矛盾、替代解释及来源理由；
- `required_source_review`、`q01_adjudication` 与 `disposition_reason`：复核状态、证据和最终 disposition 的分离记录。

正式 builder 不产生以上语义字段，不按 claim category、关键词、machineability 或旧计数选择
semantic mode、替代解释或 disposition。它只验证 curated 数据与正式来源逐字段绑定，机械拼装
branch object、计数、稳定序列化和计算 SHA-256 identity。独立 validator 再从正式来源和登记表
交叉核对。

透明诊断工具只报告风险，不自动裁决语义。当前结果：

```text
OLD_TEMPLATE_MARKER_RECORDS=0
SOURCE_WRAPPER_ECHOES=0
BLANKET_ALTERNATIVE_DEFAULTS=0
UNRESOLVED_REVIEW_PLUS_READY=0
IDENTICAL_OPERATIONALIZATION_CLUSTERS=0
MAX_IDENTICAL_OPERATIONALIZATION_CLUSTER=1
MECHANICAL_BUILDER_SEMANTIC_DECIDERS=0
```

这些数字用于发现旧模式残留，不把文字唯一性当作语义质量证明；最终仍需独立 worker
重审 source-based reasoning。

## Source、firewall 与非最终边界

branch registry 中的 `source_meaning`、`source_anchor`、`source_status` 及完整
`source_record_binding` 均从 active claim manifest 原样机械绑定。来源自身出现 P&L、收益或结果
等普通语言时不做关键词清洗。项目没有访问 candidate outcome、未来价格、真实模型 API、
broker 或真钱 surface。

所有 branch object 保持：

```text
identity_binding_scope=PRE_FREEZE_NON_FINAL
primary_semantics_frozen=false
primary_eligible=false
```

`READY_FOR_PRIMARY_FREEZE` 仅表示可交给独立重审，不表示 PRIMARY 已冻结或已 eligible。

## Prompt package 后续机械重绑定

当前 `docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json` 仍含：

```text
context_selection.knowledge_scope=CURRENT_ACTIVE_JIANGHE_V1_1_PLUS_PRIMARY_REGISTRY_V0_3
identities.context_selection_identity=646f8f96335227a08d7560a8e0cc30ec3ad64b18eea390ce9d19957fe025c912
identities.prompt_package_identity=beedb7e8189d0c649b39683d57fec6e8e937c0ac8f3a1b793cf4929df2e88b3b
```

V0.4 集成后需要由 integration lane 更新 `context_selection.knowledge_scope`，随后按既有规范
重算 `identities.context_selection_identity` 和 `identities.prompt_package_identity`。本修复分支
不修改 provider、normalizer、visual renderer、fidelity evaluator 或 prompt package 语义。

## 可复核命令

```powershell
python tools/build_jianghe_primary_claim_mapping_draft_v0_1.py --check
python tools/validate_jianghe_primary_claim_mapping_draft_v0_1.py
python tools/diagnose_jianghe_primary_curated_quality_v0_4.py
python -m unittest tests.test_jianghe_primary_curated_quality_v0_4 -v
python -m unittest tests.test_jianghe_primary_claim_mapping_draft_v0_1 -v
```
