# 江河交易员正式研究证据包 — Current View V0.2

## 状态

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..033
ANALYZED_AVAILABLE=31
BLOCKED_LOCAL_MEDIA=007
BLOCKED_PAID_GATE=022
SOURCE_ONLY_VERIFIED=NO
EVIDENCE_STAGE=PRELIMINARY_SOURCE_INTERPRETATION_EVIDENCE
PRIMARY_ELIGIBLE=NO
TOOL_DECISION=USE_EXISTING / NO_NEW_TOOL
```

007 的本地 MP4 已知损坏，保留 `PENDING_REPAIR`；022 为付费门控来源，不购买、不访问、不补猜。

## 如何读取当前证据

先读 `JIANGHE_CURRENT_VIEW_V0_2.md`。当前权威组合是：

- V0.1：001–028 的基础 claim ledger、case library、source index；
- `JIANGHE_SOL_REVIEW_RESOLUTION_V0_2.md`：解决 V0.1 的 7 条 Sol 待确认项，并在冲突时覆盖旧字段；
- V0.2：029–033 claim/case/source delta，以及累计 Dossier / Family / UNKNOWN / contradiction / review queue。

### V0.2 文件

- `JIANGHE_CURRENT_VIEW_V0_2.md`：当前阅读入口与优先级。
- `JIANGHE_TRADER_DOSSIER_V0_2.md`：001–033 的 14 部分累计 Dossier。
- `JIANGHE_STRATEGY_FAMILIES_V0_2.md`：累计 Family A–D 来源规格。
- `JIANGHE_SOL_REVIEW_RESOLUTION_V0_2.md`：V0.1 七项 Sol 原视频复核。
- `JIANGHE_CLAIM_LEDGER_DELTA_029_033_V0_2.jsonl`：029–033 的新增 claim。
- `JIANGHE_CASE_LIBRARY_DELTA_029_033_V0_2.md`：029–033 的新增案例。
- `JIANGHE_SOURCE_INDEX_DELTA_029_033_V0_2.csv`：029–033 来源索引。
- `JIANGHE_UNKNOWN_REGISTER_V0_2.md`：当前未解语义/机器边界。
- `JIANGHE_CONTRADICTION_REGISTER_V0_2.md`：已解决与仍开放的表面冲突。
- `JIANGHE_EVIDENCE_REVIEW_QUEUE_V0_2.csv`：当前只剩新的来源内部评分阈值冲突待后续证据解决。

## 重要 V0.2 变化

- Video 001：原视频确认是“应变交易理念”，不是 SRT 的“应变教育理念”。
- Video 024：ABC B 的两条明确放弃边界已钉死；A 的 4+ / 至少 2 根趋势 K 的方向与市场/周期适用语境也已复核。
- Video 020：1:1 是该案例空间预期，不是固定止盈或统一门槛。
- Video 021：该版本震荡交易明确为常规仓位的 0.5×。
- Video 017：固定 RR、固定空间和动态结构退出是替代性方法；江河偏好动态跟随。
- Videos 029–032：进一步补强多周期 N 结构、成功突破、强趋势弱化到震荡、宽幅震荡定义、左侧缩仓、分段利润和移动止损。
- Video 033：主要属于第三方学生案例。只记录江河明确说“进场逻辑基本一样”的归因；学生自己的快速退出/风险行为不迁移成江河规则。

## 证据与版权边界

仓库不含完整视频、完整字幕、批量帧或剪辑。SRT 只用于导航；图表相关 claim 必须能回到 BVID + timestamp 的原视频语言/画面。收益、账户曲线、R 倍数仅是 `SOURCE_CASE_CONTENT`，不是 validity evidence。

当前 `SOURCE_ONLY_VERIFIED=NO`，因此本证据包不能 PRIMARY-ready，也不授权 candidate outcome backtest、validation/final access、实盘或真钱动作。
