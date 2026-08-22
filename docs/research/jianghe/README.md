# 江河交易员正式研究证据包 — Current View V1.0 Final

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..099
SOURCE_TOTAL=99
MEDIA_AVAILABLE=98
SEMANTICALLY_REVIEWED_WITH_RELIABLE_LANGUAGE_OR_BURNED_TEXT=97
VISUAL_ONLY_NO_RELIABLE_LANGUAGE=065
BLOCKED_PAID_GATE=022
CORPUS_MEDIA_RECOVERY=COMPLETE
FINAL_SOL_REVIEW=COMPLETE
FINAL_SOURCE_DISTILLATION=COMPLETE
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
TOOL_DECISION=USE_EXISTING
```

先读 `JIANGHE_CURRENT_VIEW_V1_0.md`。

## V1.0 authority

最终来源蒸馏组合：

- `JIANGHE_TRADER_DOSSIER_V1_0.md`
- `JIANGHE_SOL_FINAL_REVIEW_RESOLUTION_V1_0.md`
- `JIANGHE_CLAIM_LEDGER_SUPPLEMENT_FINAL_V1_0.jsonl`
- `JIANGHE_CASE_LIBRARY_SUPPLEMENT_FINAL_V1_0.md`
- `JIANGHE_SOURCE_INDEX_SUPPLEMENT_FINAL_V1_0.csv`
- `JIANGHE_STRATEGY_FAMILIES_V1_0.md`
- `JIANGHE_SYSTEM_PROCESS_V1_0.md`
- `JIANGHE_UNKNOWN_REGISTER_V1_0.md`
- `JIANGHE_CONTRADICTION_REGISTER_V1_0.md`
- `JIANGHE_EVIDENCE_REVIEW_QUEUE_V1_0.csv`
- `JIANGHE_ASR_SEMANTIC_QA_RULE_V1_0.md`

旧V0.1–V0.9证据不删除，继续作为演进历史与底层claim/case来源。

## Final corpus disposition

- 007：损坏媒体已恢复并由Sol完整补审。
- 016/017/018：本地ASR经最终语义抽检可用并已补审。
- 048：所谓恢复远端SRT与视频内容不匹配，已拒绝；只使用视频直接烧录文字。
- 065：无原生字幕；本地ASR在最终语义QA中被判明显幻觉并拒绝。媒体可看，但不从订单/图表结果倒推口述策略；语义claim=0。
- 099：所谓恢复远端SRT与视频内容不匹配，已拒绝；视频自身完整烧录字幕可用并已补审。
- 022：付费门控合法不可达例外，不购买、不绕过。

## Final family state

仍只有：
- `JH-FAMILY-A` 趋势关键位回调延续
- `JH-FAMILY-B` 趋势衰弱反转 / 高周期回调
- `JH-FAMILY-C` 多周期确认突破
- `JH-FAMILY-D` 震荡边界反转

没有Family E。剥头皮保持非核心执行模式；均线/指标保持辅助角色。

## Research boundary

仓库不保存完整视频、完整字幕或ASR全文。SRT/ASR只作证据导航；图表claim回到原视频同时间画面。收益、RR、账户结果仅属source case content，不作为validity evidence。

`SOURCE_ONLY_VERIFIED=NO`、`PRIMARY_ELIGIBLE=NO`。V1.0是**江河001–099来源蒸馏收口**，不授权outcome testing、validation/final访问、PRIMARY冻结或真钱动作。
