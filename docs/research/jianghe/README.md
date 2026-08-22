# 江河交易员正式研究证据包 — Current View V0.6

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..073
ANALYZED_AVAILABLE=70
PENDING_SEMANTIC_REVIEW=065
BLOCKED_LOCAL_MEDIA=007
BLOCKED_PAID_GATE=022
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
TOOL_DECISION=USE_EXISTING / NO_NEW_TOOL
```

先读 `JIANGHE_CURRENT_VIEW_V0_6.md`。

当前累计结构：001–028 为 V0.1 基础 evidence；V0.2 为 Sol review resolution + 029–033 delta；V0.3 为 034–043 delta；V0.4 为 044–053 delta；V0.5 为 054–063 delta；V0.6 为 064–073 delta + 001–073 累计 Dossier / Family / System Process / UNKNOWN / contradiction / review queue。

V0.6 仍只有四个核心 Family A–D。剥头皮保持 `SCALPING_EXECUTION_MODE / NON_CORE`；均线保持 `AUXILIARY_TOOL_USAGE`，均不创建 Family E。

V065 没有 SRT，且抽样视频画面没有稳定可读取的烧录语义字幕。当前仅确认MP4可读和交易画面存在，不根据纯视觉订单结果推断其交易原因；状态为 `PENDING_SEMANTIC_REVIEW`，等待本地免费ASR或直接音频复核。

V069 新增重要治理边界：同周期内部结构只用于帮助确认外部结构，不得直接当作该周期波段交易机会，也不得冒充下一小周期外部结构。

仓库不含完整视频、完整字幕或批量帧。SRT仅导航；图表 claim 必须能回到 BVID + timestamp 的原视频语言/画面。收益、R倍数和账户结果仅为 `SOURCE_CASE_CONTENT`，不是 validity evidence。

`SOURCE_ONLY_VERIFIED=NO`，因此当前证据仍为 preliminary，不是 PRIMARY-ready，不授权 outcome backtest、validation/final access、真钱或实盘动作。
