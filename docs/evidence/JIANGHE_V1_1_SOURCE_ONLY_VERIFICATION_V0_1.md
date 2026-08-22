# 江河 V1.1 SOURCE_ONLY 验证 V0.1

> 日期：2026-08-23
> 范围：江河 V1.1 已完成来源知识的 material-bound SOURCE_ONLY 会话验证
> 不含：候选结果、Development 表现、Validation、Final、Shadow、Broker、真钱

## 结论

```text
JIANGHE_SOURCE_DISTILLATION=V1_1_EXHAUSTIVE_SECOND_PASS_COMPLETE
SOURCE_ONLY_VERIFIED=YES
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
FINAL=LOCKED
```

本次 `YES` 的含义严格限定为：项目 `SourceOnlyPolicy` 已创建并验证一个与江河 V1.1
知识包、来源物料清单、claim 清单和 case 清单绑定的 SOURCE_ONLY 会话；该会话的项目
能力面技术性拒绝受保护结果访问。它不等同于操作系统级隔离，也不宣称模型没有任何潜在
市场先验。

机器可读证据：`docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json`。

## 会话与物料绑定

```text
SESSION_ID=JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_GATE_V0_1_20260823
MODEL_IDENTITY=CODEX_GPT_5_DESKTOP_AGENT__MODEL_VERSION_NOT_EXPOSED
PROMPT_SPEC_IDENTITY=JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_GATE_V0_1
TOOL_RETRIEVAL_MODE=REPOSITORY_BOUND_JIANGHE_SOURCE_MANIFESTS_ONLY__NO_MARKET_OR_OUTCOME_TOOLS
PROTECTED_MARKET_ACCESS_MODE=TECHNICALLY_DENIED
KNOWLEDGE_PACK_VERSION=JIANGHE_V1_1
KNOWLEDGE_PACK_IDENTITY=7170f0d5e7d6cd5fc2de8faf27e50262e2ec65ce716527d24022531561b3fd43
```

| 绑定对象 | 检查结果 |
| --- | --- |
| 来源物料清单 | 22 个仓库工件逐字节 SHA-256 绑定；99 个唯一 BVID，98 个可访问来源，022 是唯一付费例外，时间轴缺口为 0。 |
| Claim 清单 | 16 个 JSONL 工件；352 条 claim ID 全部唯一；状态只为 `EXPLICIT`、`INFERRED`、`UNKNOWN`。 |
| Case 清单 | 11 个工件；80 个 case ID 全部唯一。 |
| 江河知识包 | V1.1、20 个内容哈希；会话身份内包含知识包、claim manifest 与 case manifest 身份。 |

原始视频并未被复制到仓库，也没有把未记录的历史媒体字节伪称为已证明。这里逐字节绑定
的是本仓库可审计的来源清单、来源发现、claim 和 case 研究物料；其来源媒体身份仍由 V1.1
coverage/source-index authority 记录。

## 技术拒绝结果

`SourceOnlyClaimExtractionContext` 只持有批准的来源 bundle、已验证会话和 claim 输出面。
它没有候选市场数据仓库、候选运行器、P&L、Validation、Final 或通用结果工件读取面。
以下请求逐项进入同一拒绝面，返回 `DENIED / SOURCE_ONLY_TECHNICAL_DENIAL` 并留下审计记录：

| 受保护能力 | 结果 |
| --- | --- |
| Candidate outcome runner | `DENIED` |
| Candidate PnL | `DENIED` |
| Validation | `DENIED` |
| Final | `DENIED` |
| Outcome artifact open | `DENIED`，`opened_artifact=NO` |

这不是“提示词要求不要看”。拒绝由 `SourceOnlyPolicy` 代码执行；手工构造的
`TECHNICALLY_DENIED` session 也不能被标记为 verified。

## V1.1 知识核验范围

本轮只核验已完成的 V1.1 知识链，不重新蒸馏 99 条视频：

- provenance/material binding：通过；来源、claim、case 三类 manifest 均内容绑定。
- claim identity completeness：通过；352 个 ID 唯一且拥有当前 V1.1 所需的身份、来源序号、状态和审核字段。
- UNKNOWN/矛盾保存：通过；未填补 `JH-UNK-*`，未为原本无法锁定的边界创造新语义；当前无须项目臆造解决的开放矛盾。
- 家族一致性：通过；仍严格为 `JH-FAMILY-A` 至 `JH-FAMILY-D`，没有 Family E。
- 新增内容：0 条 claim、0 个 case、0 个来源语义结论。

来源视频/claim/case 中的历史交易示例（包括 R、账户金额或盈亏展示）仍是**来源材料**，只可
用于理解来源语义、正反例和风险过程；它们不构成、也没有被转换为项目 candidate performance。

## PRIMARY 仍不具备资格

SOURCE_ONLY 通过不是 PRIMARY 或候选结果授权。江河 AI Trader 在 PRIMARY 前至少仍缺：

1. A/B/C/D 各 claim 的来源支持 PRIMARY branch 和相应的非结果机器化边界；
2. UNKNOWN、来源内部冲突及非机器化字段的失败闭合，不能用项目约定替代；
3. 真实模型/提供方版本、完整 `JiangheAITraderIdentity` 和合成忠实度证据；
4. 后续独立的预结果治理条件。当前统计/流程和候选结果授权均未改变。

因此以下锁保持不变：

```text
DEVELOPMENT_PERFORMANCE=NOT_AUTHORIZED
CANDIDATE_OUTCOME=NOT_AUTHORIZED
VALIDATION=LOCKED
FINAL=LOCKED
SHADOW=NOT_AUTHORIZED
BROKER=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

## 残余威胁模型边界

```text
SOURCE_ONLY_OS_PROCESS_SANDBOX=NOT_PROVEN_NOT_CLAIMED
LOCAL_PRIVATE_STATE_TAMPER_PROOFING=NOT_PROVEN_NOT_CLAIMED
LATENT_MODEL_MARKET_KNOWLEDGE=NOT_PROVABLE_ABSENT__DISCLOSED
```

这些是既有协议已披露的更强安全性质，不会被本次项目 API/session 级验证伪装成已解决；但它们
不改变本项目对 `SOURCE_ONLY_VERIFIED=YES` 的既定、受限含义。

## 可复核命令

```text
python tools/build_jianghe_source_only_verification_v0_1.py
python -m unittest tests.test_jianghe_source_only_verification tests.test_research_firewall tests.test_jianghe_ai_trader_foundation tests.test_jianghe_v1_1_acceptance -v
```
