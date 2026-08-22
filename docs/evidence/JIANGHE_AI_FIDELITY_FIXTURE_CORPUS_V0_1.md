# 江河 AI 忠实度夹具语料 V0.1 — Evidence / Review

```text
ARTIFACT_ID=JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1
TRADER_ID=JIANGHE_TRADER
KNOWLEDGE_PACK_REFERENCE=JIANGHE_V1_1
BASELINE=ebc9da72c989086f97ff77f9840dcb124c3c5935
BRANCH=research/jianghe-ai-fidelity-fixtures-v01
STATUS=READY_FOR_MODEL_EVALUATION
FIXTURE_COUNT=20
COVERAGE=A/B/C/D/NONE
REQUIRED_HARD_NEGATIVES=9
```

## 目的

本语料只回答一个问题：**模型是否像江河地理解市场**（fidelity），而不是
**模型是否赚钱**（performance）。它实现 `JIANGHE_AI_FIDELITY_BENCHMARK_V0_1`
的夹具部分，并为其评分提供确定性的语义约束核心。

被禁止的内容（语料与评分中都不存在）：

```text
REAL_CANDIDATE_PNL=EXCLUDED
FUTURE_PRICE_PERFORMANCE_AS_ANSWER=EXCLUDED
WIN_LOSS_LABELS=EXCLUDED
OUTCOME_BASED_MODEL_SELECTION=EXCLUDED
"LATER_WENT_UP_THEREFORE_BUY"=EXCLUDED
SOURCE_CASE_LATER_RETURNS_AS_GRADING_TARGETS=EXCLUDED
```

来源案例的图示/行为语义可以用于夹具叙事，但来源案例的后续收益**永远不是评分目标**。

## 交付物

| 路径 | 内容 |
|---|---|
| `docs/evidence/JIANGHE_AI_FIDELITY_FIXTURES_V0_1.json` | machine-readable 夹具语料（20 个夹具、9 条硬负例、18 条原则、注册表） |
| `src/jianghe_fidelity_scoring.py` | 确定性评分核心（约束求值、PASS/FAIL、语料校验、污染扫描） |
| `tests/test_jianghe_ai_fidelity_scoring.py` | 测试（结构、覆盖、锚点、无污染、评分语义、决策互操作） |
| `tools/validate_jianghe_ai_fidelity_corpus.py` | 语料校验 CLI（结构 + 锚点存在性 + 无污染） |

## 评分语义

一个 case 允许多个合理语言答案，**不强制模型复述固定文字**。评分以语义约束为主：

- PASS 示例 1：识别为 A 并等待确认。
- PASS 示例 2：A 候选但 NO_TRADE，因为触发未完成。
- FAIL 示例：仅看到吞没就直接 LONG。

判定规则（`evaluate_fixture`）：

```text
PASS 当且仅当：至少一个 pass_path 全部成立，且没有任何 fail_condition 全部成立
否则：FAIL
```

约束类型（`semantic_constraint_types`）：

| 类型 | 语义 |
|---|---|
| `family_in` / `family_not_in` | 策略家族 A/B/C/D/NONE 许可 |
| `action_in` / `action_not_in` | WAIT/NO_TRADE/WATCH/CANDIDATE/ENTER/MANAGE/EXIT |
| `direction_in` / `direction_not_in` | LONG/SHORT/NONE 许可 |
| `principle_acknowledged` | 回复显式满足某条江河原则（任意命中） |
| `principle_violated` | 回复显式违反某条江河原则（任意命中，FAIL 用） |
| `no_invented_threshold` | 没有发明来源未钉死的阈值 |
| `invented_threshold` | 发明了任意来源未钉死的阈值（FAIL 用） |
| `declares_unknown` | 把给定的 UNKNOWN 概念标记为未知 |
| `no_outcome_reference` | 没有引用未来价格/结果/盈亏 |
| `outcome_referenced` | 引用了未来价格/结果/盈亏（FAIL 用） |

`FidelityResponse` 承载被规范化后的回复（family/action/direction +
acknowledged/violated principles + declared_unknown + invented_thresholds +
outcome_reference + raw_text）。可从 `JiangheDecision`（`src/jianghe_ai_trader.py`）
构造；每个评测样本仍按基准保存原始回复、规范化决策与评审理由。

## 覆盖

### 策略家族

| 覆盖 | 夹具 | 主题 |
|---|---|---|
| A | `JH-FIX-A-001/002/003`, `JH-FIX-C-003` | 趋势关键位回调延续（到位等待 / 确认入场 / 回调过深不做 / 突破后切换 A） |
| B | `JH-FIX-B-001/002/003` | 趋势衰弱反转（弱化不等于反转 / 接管后入场 / 趋势完整不做逆势） |
| C | `JH-FIX-C-001/002/003`, `JH-FIX-D-004` | 确认突破（假突破不做 / 真突破入场 / 真突破切机制） |
| D | `JH-FIX-D-001/002/003/004` | 震荡边界反转（中部不做 / 二推失败做 / 到位等待 / 真突破切 C） |
| NONE | `JH-FIX-NONE-001..007` | NO_TRADE / WAIT（对抗未决、无反应、同周期内部结构、LONG_INVALID≠SHORT_VALID、UNKNOWN 不虚构、止损后新设置、偏向非触发） |

### 硬负例（9 条全部覆盖）

| 硬负例 | 主夹具 |
|---|---|
| HN-001 形态≠入场许可 | A-001, B-003, D-003, NONE-003, NONE-006 |
| HN-002 位置≠触发 | A-001, D-003, NONE-002, NONE-004, NONE-007 |
| HN-003 弱化≠反转 | B-001, B-003, NONE-004 |
| HN-004 震荡中部不做 | D-001 |
| HN-005 对抗未决→等待 | NONE-001, B-001 |
| HN-006 假突破≠真突破 | C-001, D-004 |
| HN-007 同周期内部≠低周期设置 | NONE-003 |
| HN-008 LONG_INVALID≠SHORT_VALID | NONE-004, B-001 |
| HN-009 UNKNOWN/矛盾→不虚构 | NONE-005, A-001, A-003 |

## 无结果保证（non_outcome_guarantee）

- 夹具观察全部为**合成的、非结果**的当前状态描述（`synthetic_observations`）。
- `hidden_future_information` 声明哪些信息绝不提供给模型（后续价格路径、结果等）；
  它是“排除保证”，不是被评分的夹具内容。污染扫描跳过这两个元数据区，但会严格扫描
  `visible_information`、`expected`、`rubric`、`title` 等全部被评分内容。
- `tools/validate_jianghe_ai_fidelity_corpus.py` 与测试都会对**被评分内容**执行
  结果/未来价格词污染扫描；任何命中即判语料不合格。

## 来源锚定

每个夹具的 `source_anchors` 按类别引用 V1.1 权威工件，且校验器保证存在：

- `claims` → `JIANGHE_CLAIM_LEDGER*.jsonl` + `second_pass_salvage/*DELTA_V1_1.part*.jsonl`
- `cases` → `JIANGHE_CASE_LIBRARY*.md` + `JIANGHE_SECOND_PASS_CASE_LIBRARY_DELTA_V1_1.md`
- `unknowns` → `JIANGHE_UNKNOWN_REGISTER_V1_1.md`
- `contradictions` → `JIANGHE_CONTRADICTION_REGISTER_V1_1.md`

`explicit_unknown` 只引用 UNKNOWN 注册表真实条目（如 JH-UNK-002/003/004/005/006/008/016/030/031/032/033/039/043/044）。

## 运行

```text
python tools/validate_jianghe_ai_fidelity_corpus.py
python -m unittest tests.test_jianghe_ai_fidelity_scoring -v
```

全量项目测试（bootstrap）不受影响：

```text
python -m unittest discover -s tests -v
```

## 边界

本语料完成的是**忠实度基准的夹具与评分核心**，不是策略有效性验证，也不解锁任何
结果相关授权。

```text
SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION
UNKNOWN > GUESSING
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
REAL_MONEY=NOT_AUTHORIZED
MODEL_PROVIDERS=CANDIDATE
```
