# 江河交易员正式研究证据包 V0.1

## 状态与边界

本包将来源时间线 001–028 的既有本地语料和 Sol 已确认的交易语义整理为可复查的研究证据；它不是新的策略研究，也不是机器策略、回测或表现证据。

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..028
CURRENT_ANALYZABLE=26
BLOCKED_LOCAL_MEDIA=001 (source ordinal 007)
BLOCKED_PAID_GATE=001 (source ordinal 022)
SOURCE_ONLY_VERIFIED=NO
EVIDENCE_STAGE=PRELIMINARY_SOURCE_INTERPRETATION_EVIDENCE
PRIMARY_ELIGIBLE=NO
TOOL_DECISION=USE_EXISTING / NO_NEW_TOOL
```

`007` 的原始媒体经本地 `ffprobe` 复查出现 MP4 样本表错误，故不解释、不猜测，保留为 `PENDING_REPAIR`。`022` 是付费门控来源，未购买、未访问、未补猜。

## 文件说明

- `JIANGHE_TRADER_DOSSIER_V0_1.md`：14 部分的累积研究摘要。
- `JIANGHE_CLAIM_LEDGER_V0_1.jsonl`：每行一条可追溯主张。
- `JIANGHE_CASE_LIBRARY_V0_1.md`：来源案例，仅说明语义，不是盈利能力证据。
- `JIANGHE_STRATEGY_FAMILIES_V0_1.md`：仅 A–D 四个来源家族。
- `JIANGHE_UNKNOWN_REGISTER_V0_1.md`、`JIANGHE_CONTRADICTION_REGISTER_V0_1.md`：未解问题与表面冲突。
- `JIANGHE_SOURCE_INDEX_V0_1.csv`、`JIANGHE_EVIDENCE_REVIEW_QUEUE_V0_1.csv`：完整来源索引与待 Sol 复核项。

## 版权与复查

仓库不含视频、完整字幕、批量帧或剪辑。每条重要主张只保存 BVID、短摘录/概述、精确时间和同时间画面复查说明。需要复查时，在本地语料根目录用 `tools/exact_range.py` 按 BVID 与记录时间抽取原视频帧；抽取结果只留在本地，不提交 Git。

字幕只用于导航。图表依赖的结论以“原视频同时间画面”为准；若字幕与原视频语言冲突，进入复核队列而不依字幕猜测。
