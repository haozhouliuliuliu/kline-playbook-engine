# 江河 001–099 二次覆盖审计 V1.1

> Status: ACTIVE / CORRECTIVE AUDIT
> Scope: corpus-wide source-coverage completeness, not outcome validation

## 结论

V1.0 的“FINAL_SOURCE_DISTILLATION=COMPLETE”结论被撤回。

原因不是已发现某条具体策略结论必然错误，而是**证据覆盖证明不足**：早期 001–028 的 Claim Ledger 与后续批次相比存在明显稀疏/不对称，且若干长视频被标记为 `SOL_ANALYZED`，但仓库中 `claim_count=0` 或仅 1–2 条 claim。仅凭高层 Dossier 无法证明这些视频已经被完整逐段复核而不是被压缩、跳过或只提取代表性内容。

因此当前必须 fail closed：

```text
FINAL_SOURCE_DISTILLATION=REVOKED_PENDING_EXHAUSTIVE_SECOND_PASS
SECOND_PASS_SOURCE_COVERAGE_AUDIT=OPEN
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

## 已确认的结构性风险

### A. 001–028 明显低覆盖

基础 source index 记录以下**可访问且已标记 ANALYZED，但 claim_count=0** 的来源：

`001,003,004,009,010,011,013,014,019,025,026`

其中多条标题/时长本身表明它们是系统构建、交易逻辑、强弱、复盘、情绪、实盘教学或底层逻辑材料；在没有逐段 `NO_NEW_CLAIM` 证据的情况下，不能把 0 claim 解释为“完整看完但没有可记录内容”。

V1.0 已补审的 `007,016,017,018` 不在上述剩余零-claim集合中。

### B. 001–028 还存在长视频低 claim 密度

即便 claim_count 非零，以下早期材料仍明显需要完整二次检查，而不能只看现有 claim：

- 002: 973.986s / 2 claims
- 005: 763.752s / 2 claims
- 006: 1163.345s / 2 claims
- 008: 966.3s / 1 claim
- 012: 492.078s / 1 claim
- 015: 902.909s / 1 claim
- 020: 847.716s / 2 claims
- 021: 2125.814s / 3 claims
- 023: 1061.2s / 1 claim
- 024: 2154.212s / 2 claims
- 027: 1399.608s / 2 claims
- 028: 583.913s / 1 claim

低 claim 数本身不是错误，但**没有逐段覆盖记录时，它不能证明没有被压缩**。

### C. 后续批次覆盖结构更一致

029–098 的 source indexes 普遍给每条来源留下多个 claim，且 case / notes / review queue 更系统；037 有“仅结果展示、无新增策略语义”的明确 no-claim 理由；065 有“可靠语言不可用、禁止视觉倒推”的明确 no-claim 理由；022 是付费门控例外。

这进一步说明 001–028 与后续批次的证据粒度不一致，必须统一重审标准。

## 二次核验标准

这轮不允许用“已经在 Dossier 里出现过”作为跳过理由。

对每个可访问来源必须建立 `SECOND_PASS_SOURCE_COVERAGE_RECORD`，至少包含：

- source ordinal / BVID / duration;
- language basis;
- 全时长分段清单；
- 每段是否实际复核语言；
- 图表依赖段是否复核 same-time visual；
- 每段结果：`NEW_CLAIM / DUPLICATE_SUPPORT / CASE_ONLY / PROCESS_ONLY / NO_TRADING_SEMANTIC / UNRELIABLE_LANGUAGE / NEEDS_SOL_REVIEW`；
- 新增 claim/case 或明确的 no-new-claim 理由；
- 任何与既有结论冲突/收窄/扩张的地方。

必须满足：

```text
AVAILABLE_SOURCE_DURATION_COVERAGE=100%
UNACCOUNTED_TIMELINE_GAP=0
CHART_DEPENDENT_CLAIM_WITHOUT_SAME_TIME_VISUAL=0
UNEXPLAINED_ZERO_CLAIM_AVAILABLE_SOURCE=0
```

## 优先级

### Priority 1 — 全量重审 001–028

除 022 付费不可达外，001–028 全部重新逐段复核；007/016/017/018 虽已在 V1.0 补审，也纳入覆盖记录，防止只复核了候选片段。

### Priority 2 — 抽掉“代表性压缩”风险

029–099 也必须建立完整 timeline coverage record；不能只验证现有 claim 是否正确，而要确认**有没有没被提取的独立交易语义**。

### Priority 3 — 全局再综合

只有 98 条可访问来源全部完成 100% coverage record 后，才能重新：

- 合并 claim ledger；
- 更新 case library；
- 重新判断 Family A–D 是否完整；
- 重建 Unknown / Contradiction；
- 重写 14 项 Dossier；
- 再次决定是否可称 `FINAL_SOURCE_DISTILLATION=COMPLETE`。

## 已知合法例外

- 022: `SOURCE_UNAVAILABLE_PAID_GATED` — 不购买、不绕过。
- 065: 媒体可用但现有 local ASR 已因语义幻觉被拒绝。若没有新的可靠语言证据，保持 `VISUAL_ONLY_NO_RELIABLE_LANGUAGE`，不得根据订单结果倒推口述逻辑。

## 工具判断

```text
TOOL_DECISION=USE_EXISTING
```

不新增语义模型。Codex只可做机械分段、字幕/ASR运输、时间轴覆盖清单和证据打包；最终语义判定继续由 GPT-5.6 Sol 完成。
