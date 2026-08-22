# 江河交易员正式研究证据包 — V1.1 Exhaustive Second Pass Complete

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..099
SOURCE_TOTAL=99
MEDIA_AVAILABLE=98
PAID_GATE_EXCEPTION=022
FULL_TIMELINE_SECOND_PASS_AVAILABLE_MEDIA=98
AVAILABLE_SOURCE_DURATION_COVERAGE=100%
UNACCOUNTED_TIMELINE_GAP=0
UNEXPLAINED_ZERO_CLAIM_AVAILABLE_SOURCE=0
VISUAL_ONLY_NO_RELIABLE_LANGUAGE=065
RECOVERED_REMOTE_SRT_USED_WITHOUT_IDENTITY_QA=0
SECOND_PASS_SOURCE_COVERAGE_AUDIT=COMPLETE
FINAL_SOURCE_DISTILLATION=COMPLETE_V1_1_AFTER_CORRECTIVE_SECOND_PASS
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
TOOL_DECISION=USE_EXISTING
```

先读：

1. `JIANGHE_CURRENT_VIEW_V1_1.md`
2. `JIANGHE_TRADER_DOSSIER_V1_1.md`
3. `JIANGHE_SECOND_PASS_RECONCILIATION_V1_1.md`
4. `second_pass_salvage/SECOND_PASS_SALVAGE_MANIFEST_V1_1.md`
5. `JIANGHE_SECOND_PASS_COVERAGE_AUDIT_V1_1.md` — 记录为什么V1.0被撤回和二次核验标准
6. `JIANGHE_SOL_FINAL_REVIEW_RESOLUTION_V1_0.md` — targeted-review历史结论
7. 既有V0.1–V0.9 claim/case/source artifacts

## V1.1为什么存在

V1.0曾过早写入`FINAL_SOURCE_DISTILLATION=COMPLETE`。Owner要求重新检查是否存在“只看部分、跳过部分、压缩过头”的情况；二次审计确认这种风险**确实发生过**，主要集中在001–028。

因此V1.0的完成状态先被撤回，随后对98条可访问来源重新做全时间轴二次覆盖，并把遗漏/压缩内容重新提取。

二次覆盖记录现证明：

```text
99条source唯一且完整登记
98条可访问视频全部 FULL_TIMELINE_REVIEWED_0_TO_END
022 = 唯一付费门控合法例外
UNACCOUNTED_TIMELINE_GAP = 0
065 = 全视频视觉复核，但无可靠语言证据，语义claim保持0
```

## 二次复核抢救结果

- 新恢复的second-pass Claim Delta：**64条**，均有唯一claim ID并通过JSON解析。
- 早期最明显的低覆盖问题出现在`003、010、019、025、026`等旧零/低-claim来源；021/024等长视频也补出了明显更多风险、管理、入场和条件细节。
- `009/014`：因远端恢复字幕链路已证明可能错视频，本轮不使用未重新验证的远端SRT；只用实际视频烧录文字/视觉证据。
- `048/099`：恢复远端SRT确认错视频，继续作废。
- `065`：faster-whisper输出虽然机械验收通过，但语义幻觉，继续作废。

完整可重建的coverage和claim delta被拆成小文件逐批commit；字节数、行数、SHA-256及重建方式见：

`second_pass_salvage/SECOND_PASS_SALVAGE_MANIFEST_V1_1.md`

## 当前策略家族

二次复核没有发现独立Family E。仍只有：

- `JH-FAMILY-A` 趋势关键位回调延续
- `JH-FAMILY-B` 趋势衰弱反转 / 高周期回调
- `JH-FAMILY-C` 确认突破
- `JH-FAMILY-D` 震荡边界反转

剥头皮继续是`NON_CORE_EXECUTION_MODE`；MA/EMA继续是`AUXILIARY_TOOL_USAGE`。

## 仍然不允许猜的内容

- V030精确3分开仓边界；
- V078严格50/50 K线归类；
- V079“进场K收盘价止损”文字/视觉冲突；
- 关键区、强弱、二推、趋势阶段、真空区域等统一机器阈值；
- 一个跨所有Family统一账户风险比例/母公式；
- V065可靠口述交易语义。

## Research boundary

V1.1完成的是**来源蒸馏覆盖修复**，不是策略有效性验证。

```text
SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION
UNKNOWN > GUESSING
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
REAL_MONEY=NOT_AUTHORIZED
```

收益、R、账户金额只属于source case content，不是validity evidence。
