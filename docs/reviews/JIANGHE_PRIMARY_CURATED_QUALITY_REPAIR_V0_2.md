# 江河 PRIMARY curated-quality TARGETED CONVERGENCE REPAIR V0.2

> Status: `AWAITING_INDEPENDENT_REAUDIT`
> Acceptance authority: `docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_ACCEPTANCE_RUBRIC_V0_1.md`
> Candidate artifact: `docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_CURATED_REVIEW_V0_5.jsonl`

## 1. 修复边界

本轮仅按冻结的 R1–R8 修复 V0.4 已复现的具体缺陷。未把 prose uniqueness、difflib similarity、标准句式复用或 source echo 当作 gate 条件，也未为降低文本相似度重写 352 条语义。

V0.4 仅作为 candidate input。V0.5 重新绑定最终内容并生成新 identity；V0.3 历史文件保持不变。构建器只执行加载、校验、绑定、交叉引用、路径存在性检查、确定性序列化与哈希，不选择或生成语义、alternative、authority link、operationalization 或 disposition。

## 2. R1–R8 自检结果

| 标准 | 状态 | 证据摘要 |
| --- | --- | --- |
| R1 | PASS | 352 条唯一覆盖，UNMAPPED=0、DUPLICATES=0；用于裁决的 repository evidence path 全部存在，phantom 路径 fail closed。 |
| R2 | PASS | READY=340；12 条真实 STOP 保留；READY 不携带影响最小命题的未解决 required review、冲突、歧义或观测缺口。 |
| R3 | PASS | GUESSED_UNKNOWN=0、SILENT_CONFLICT_RESOLUTION=0；UNKNOWN 与 contradiction 完成反向候选逐项 LINK / NOT_APPLICABLE 裁决。 |
| R4 | PASS | 171 条伪造的 `ALT-PROJECT-PRECISION` 稻草人全部移除；7 条真实 source-plausible material alternative 保留。 |
| R5 | PASS | source-bound 文本逐字保持；未把案例数字、UNKNOWN、相关性或 contextual 行为升级为统一项目规则。 |
| R6 | PASS | SOURCE SEMANTIC、AI DISCRETION、DETERMINISTIC MACHINE OPERATIONALIZATION 边界保持；human discretion 未硬编码。 |
| R7 | PASS | builder 为 mechanical-only；branch identity 可确定性重建；PRIMARY_FREEZE=NO、PRIMARY_ELIGIBLE=NO。 |
| R8 | PASS | compile、focused tests、research firewall 与 canonical full suite 全绿；full suite 1194 tests、0 failures、0 errors；无 outcome access、live model call 或 paid spend。 |

Machine-readable gate：`docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_GATE_V0_5.json`。该 gate 只包含 R1–R8，不包含 prose/difflib/句式唯一性标准。

## 3. Targeted blocker 收口

```text
PHANTOM_PATH_RECORD_COUNT_BEFORE=346
PHANTOM_PATH_RECORD_COUNT_AFTER=0

FABRICATED_ALTERNATIVES_BEFORE=171
FABRICATED_ALTERNATIVES_AFTER=0
REAL_MATERIAL_ALTERNATIVES=7
```

V0.4 中 346 条记录引用了 102 个不存在的 `docs/research/jianghe/source_findings/JIANGHE_SOURCE_*_FINDINGS_V0_1.md` 路径。V0.5 将每条 `review_basis.source_finding` 精确绑定到 claim manifest 实际列出的材料，并对全部裁决证据执行 repository path existence 校验。

V0.4 中 171 条 `MATERIAL_ALTERNATIVES_REVIEWED` 仅用“忽略歧义并发明固定项目规则”构造 alternative，不是 source-plausible competing interpretation。V0.5 将其改为 claim-specific `NO_MATERIAL_SOURCE_ALTERNATIVE`，保留 7 条真实 material alternative。

## 4. JH-CLM-021-002

```text
JH_CLM_021_002_RESULT=READY_FOR_PRIMARY_FREEZE
```

正式 V1.1 second-pass authority 已复核 source 021 的完整视频/画面，并把止损边界收窄为震荡外部边界/结构外。V0.5 仅保留这个较窄命题；精确价格点、统一 buffer 与统一画点算法仍明确排除，并由 human discretion 保持未固定。

Resolution authority：

- `docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part02.jsonl`
- `docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_SOURCE_FINDINGS_V1_1.part00.md`
- `docs/research/jianghe/JIANGHE_SECOND_PASS_CASE_LIBRARY_DELTA_V1_1.md`

## 5. Authority reverse coverage

反向诊断文件：`docs/reviews/JIANGHE_PRIMARY_AUTHORITY_REVERSE_COVERAGE_V0_5.json`。

```text
UNKNOWN_REVERSE_COVERAGE_CANDIDATES=1741
UNKNOWN_LINKS_BEFORE=17
UNKNOWN_LINKS_AFTER=129
UNKNOWN_LINKS_ADDED=112
UNKNOWN_NOT_APPLICABLE_ADJUDICATIONS=1612

CONTRADICTION_REVERSE_COVERAGE_CANDIDATES=224
CONTRADICTION_LINKS=61
CONTRADICTION_NOT_APPLICABLE_ADJUDICATIONS=163
```

每个候选均明确为 `LINK` 或 `NOT_APPLICABLE_TO_THIS_CLAIM`；source ordinal 共址只产生候选，不机械强制链接。报告例 `JH-UNK-036 -> JH-CLM-078-004` 裁定为 `LINK`，而 `JH-UNK-036 -> JH-CLM-078-002` 裁定为 `NOT_APPLICABLE_TO_THIS_CLAIM`。

## 6. Q01 五条一致性

`JH-CLM-005-001`、`JH-CLM-020-002`、`JH-CLM-021-003`、`JH-CLM-024-001`、`JH-CLM-024-002` 均绑定实际存在的 `docs/research/jianghe/JIANGHE_SOL_REVIEW_RESOLUTION_V0_2.md`，并分别记录 resolution effect 与 remaining unresolved scope。原始 source review status 保持未改，current adjudication 不再声称仍待 Sol 复核。

## 7. 安全边界与验证

```text
SOURCE_TEXT_REWRITTEN=0
SOURCE_OVERREACH=0
OPERATIONAL_HARDCODE=0
MECHANICAL_SEMANTIC_GENERATOR=0
OUTCOME_ACCESS=NO
LIVE_MODEL_CALLS=0
PAID_SPEND=0
PRIMARY_FREEZE=NO
PRIMARY_ELIGIBLE=NO
```

本文件只记录 repair lane 的自检结果。当前状态为 `AWAITING_INDEPENDENT_REAUDIT`，不声称 independent re-audit 已通过，也不授权 PRIMARY freeze、candidate outcome、live model、paid spend、Broker 或 real-money 行为。
