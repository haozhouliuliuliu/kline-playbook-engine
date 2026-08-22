# 江河交易员正式研究证据包 — Second-Pass Coverage Audit Open

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..099
SOURCE_TOTAL=99
MEDIA_AVAILABLE=98
BLOCKED_PAID_GATE=022
VISUAL_ONLY_NO_RELIABLE_LANGUAGE=065
CORPUS_MEDIA_RECOVERY=COMPLETE
V1_0_SOL_TARGETED_REVIEW=COMPLETE
FINAL_SOURCE_DISTILLATION=REVOKED_PENDING_EXHAUSTIVE_SECOND_PASS
SECOND_PASS_SOURCE_COVERAGE_AUDIT=OPEN
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
TOOL_DECISION=USE_EXISTING
```

先读：

1. `JIANGHE_SECOND_PASS_COVERAGE_AUDIT_V1_1.md`
2. `JIANGHE_SECOND_PASS_SALVAGE_SNAPSHOT_V1_1.md`
3. `JIANGHE_SECOND_PASS_RECOVERED_FINDINGS_001_043_V1_1.md`
4. `JIANGHE_SECOND_PASS_WORKING_INVENTORY_044_099_V1_1.md`
5. `JIANGHE_CURRENT_VIEW_V1_0.md`
6. `JIANGHE_SOL_FINAL_REVIEW_RESOLUTION_V1_0.md`（保留为 V1.0 targeted-review 历史，不再代表全语料最终完成）

## 为什么撤回 V1.0 的 final-complete 状态

二次 repo 审计发现，001–028 的证据粒度和后续批次明显不一致。以下可访问来源被标记为 `ANALYZED/SOL_ANALYZED`，但仓库中 `claim_count=0`：

`001,003,004,009,010,011,013,014,019,025,026`

同时，多条 8–36 分钟早期视频只有 1–3 个 claim。低 claim 数本身不证明错误，但当前没有逐段 timeline coverage record，无法证明这些材料是完整逐段复核后“没有更多独立语义”，还是被代表性压缩/跳过。

二次复核已确认，至少 `003、010、019、025、026` 等旧低/零-claim记录存在实质性压缩，已经建立 durable salvage artifacts，后续继续按小批次写入、commit、push，不再等整个二次复核完成后一次性落盘。

因此 fail closed：**V1.0 的具体已核验结论继续保留，但“001–099 已完成最终来源蒸馏”这一全局状态撤回。**

## 当前 authority

- `JIANGHE_SECOND_PASS_COVERAGE_AUDIT_V1_1.md`：当前最高优先级，定义二次核验缺口与验收标准。
- `JIANGHE_SECOND_PASS_SALVAGE_SNAPSHOT_V1_1.md`：当前会话抢救快照，防止二次复核中间成果只留在聊天。
- `JIANGHE_SECOND_PASS_RECOVERED_FINDINGS_001_043_V1_1.md`：已经发现的早期低覆盖/遗漏结论，明确标为中间态。
- `JIANGHE_SECOND_PASS_WORKING_INVENTORY_044_099_V1_1.md`：后半段现有证据与待全时长证明清单。
- `JIANGHE_TRADER_DOSSIER_V1_0.md`：历史综合快照，不再视为最终完整 Dossier。
- `JIANGHE_SOL_FINAL_REVIEW_RESOLUTION_V1_0.md`：007/016/017/018/048/065/099 及 030/069/078/079/096 的 targeted review 结论继续有效，除非二次全量复核出现直接反证。
- 既有 V0.1–V0.9 claim/case/source artifacts：继续作为底层来源记录。

## 二次核验必须证明什么

对 98 条可访问来源逐条建立完整时间轴覆盖记录，最终要求：

```text
AVAILABLE_SOURCE_DURATION_COVERAGE=100%
UNACCOUNTED_TIMELINE_GAP=0
CHART_DEPENDENT_CLAIM_WITHOUT_SAME_TIME_VISUAL=0
UNEXPLAINED_ZERO_CLAIM_AVAILABLE_SOURCE=0
SUBTITLE_VIDEO_IDENTITY_QA_REQUIRED=YES
UNRESOLVED_RECOVERED_SUBTITLE_IDENTITY=0
```

不能因为某条内容“和已有结论重复”就跳过；必须记录为 `DUPLICATE_SUPPORT`。没有交易语义也必须记录明确原因。

## Corpus exceptions

- `022`：`SOURCE_UNAVAILABLE_PAID_GATED`，合法不可达例外，不购买、不绕过。
- `065`：现有 local ASR 因语义幻觉已被拒绝；如果没有新的可靠语言证据，继续保持视觉可用但禁止从订单/图表结果倒推口述策略。

## Research boundary

`SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`。

收益、RR、账户结果只属于 source case content，不是 validity evidence。

`SOURCE_ONLY_VERIFIED=NO`、`PRIMARY_ELIGIBLE=NO`，不授权 outcome testing、validation/final 访问、PRIMARY 冻结或真钱动作。
