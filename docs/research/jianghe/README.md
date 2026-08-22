# 江河交易员正式研究证据包 — Current View V0.9

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..099
ANALYZED_AVAILABLE=95
PENDING_SEMANTIC_REVIEW=065,099
PARTIAL_NO_NATIVE_SRT_REVIEW=048
BLOCKED_LOCAL_MEDIA=007
BLOCKED_PAID_GATE=022
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
TOOL_DECISION=USE_EXISTING_FOR_AUDIT / ADD_TOOL_IF_TRUE_NO_SUBTITLE_CONFIRMED
```

先读 `JIANGHE_CURRENT_VIEW_V0_9.md`。

当前累计结构：001–028为V0.1基础evidence；V0.2为Sol review resolution+029–033；V0.3为034–043；V0.4为044–053；V0.5为054–063；V0.6为064–073；V0.7为074–083；V0.8为084–093；V0.9加入094–098，并把099明确置为待本地语料审计/语义复核。

V0.9仍只有四个核心Family A–D。V094/V096/V097主要补风险、纪律和交易者状态；V095/V098继续补宽幅震荡、多周期位置→低周期确认及案例证据，不创建Family E。

本轮Sol会话只收到094–098 MP4，未收到099 MP4。Owner说明065和099没有SRT；历史上048也曾无独立SRT且只做过烧录文字有限复核。因此下一步不是直接假定“真的没有字幕”，而是对001–099进行BVID级全量媒体/字幕机械审计，解释历史90 vs 89字幕计数差异。

审计阶段使用现有工具；只有真实确认`NO_NATIVE_SUBTITLE_CONFIRMED_NEEDS_ASR`后才`ADD_TOOL`，首选本地免费CPU `faster-whisper`单一pilot，不使用OpenAI API或其他付费API。Codex只负责获取/转写/证据打包，不解释交易语义。

仓库不含完整视频、完整字幕或批量帧。SRT只作导航；图表claim必须回到BVID+timestamp原视频语言+同时间画面。收益、RR、账户结果只属于source case content，不作为validity evidence。

`SOURCE_ONLY_VERIFIED=NO`，当前仍为preliminary，不授权outcome testing、validation/final访问或真钱动作。
