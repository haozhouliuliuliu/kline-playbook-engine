# 江河语料缺口重新验证计划 V0.9

## 目标

在不改变交易语义解释权、不使用付费API、不购买付费视频的前提下，机械验证当前所谓“缺视频/缺字幕”到底是：

1. 来源本身没有；
2. 本地下载失败/命名遗漏；
3. Bilibili字幕接口当时未返回但现在可取；
4. 只有烧录字幕；
5. 确实需要本地免费ASR。

Codex/脚本只能做获取、校验、转写和证据打包，不得自行解释交易策略。

## 已知缺口

### 007

当前状态：`LOCAL_MEDIA_BROKEN / PENDING_REPAIR`。

需要重新验证：
- source manifest中的BVID/URL仍可访问；
- 当前Bilibili登录态下是否可重新获取媒体；
- 是原文件损坏、下载中间文件混淆，还是来源不可达；
- 若重新下载成功，ffprobe验证视频+音频并替换为新的本地final media；旧损坏文件先隔离，不静默覆盖证据。

### 022

当前状态：`UNAVAILABLE_PAID_GATED`。

只重新确认门控状态，不购买、不绕过。若仍是充电/付费专属，则维持blocked。

### 048

历史状态：无独立SRT；V0.4只采用可直接读取的烧录文字做有限语义。

需要验证：
- 本地是否其实存在字幕但命名/索引遗漏；
- Bilibili字幕接口当前是否提供AI字幕/CC字幕；
- 若确实无字幕，列入本地免费ASR队列，用于补全完整语音，随后交给Sol复核。

### 065

Owner确认无SRT。当前为`PENDING_SEMANTIC_REVIEW`。

按与048相同步骤验证；若来源确实无字幕，则本地ASR。

### 099

Owner确认无SRT；本轮Sol会话未收到099 MP4。

首先在本地source_manifest和media中确认：
- 099的BVID、标题、URL；
- final MP4是否存在；
- ffprobe是否有video+audio；
- 是否存在任何本地SRT/VTT/ASS/JSON字幕；
- Bilibili字幕接口是否有可取字幕。

若媒体完整且确实无字幕，则本地ASR后形成Sol evidence package。

## 全量审计要求

不能只检查上述已知编号。必须对001–099按BVID做全量交叉表：

- source manifest枚举状态；
- final media存在/缺失/损坏；
- video stream；
- audio stream；
- duration；
- native subtitle / AI subtitle / burned-in-only / none；
- 本地subtitle文件匹配；
- 远端subtitle API结果；
- 是否需要ASR；
- 当前Sol semantic status。

必须解释历史上`90个字幕`与Windows目录看到`89个文件`的差异，不能只给新计数。

## 字幕状态枚举

每个BVID最终只能落入明确状态：

- `NATIVE_SUBTITLE_VERIFIED_LOCAL`
- `NATIVE_SUBTITLE_AVAILABLE_REMOTE_LOCAL_MISSING`
- `BURNED_IN_ONLY_VERIFIED`
- `NO_NATIVE_SUBTITLE_CONFIRMED_NEEDS_ASR`
- `SUBTITLE_FETCH_FAILED_RETRYABLE`
- `SOURCE_UNAVAILABLE_PAID_GATED`
- `MEDIA_BROKEN_REPAIR_REQUIRED`

## 远端字幕重新验证

使用现有Bilibili认证获取能力，优先：

1. 当前已验证的项目Bilibili/WBI/yt-dlp能力；
2. 使用运行时登录态，不把cookie/token写入repo；
3. 对每个疑似缺字幕BVID查询CID/字幕轨道；
4. 若有字幕，下载到`D:\江河交易员\subtitles`并更新manifest；
5. 不因单次HTTP失败就认定“没有字幕”；区分`NONE`与`FETCH_FAILED`。

## ASR工具决策

阶段1机械审计使用：`USE_EXISTING`。

只有当真实确认存在`NO_NATIVE_SUBTITLE_CONFIRMED_NEEDS_ASR`后：

```text
TOOL_DECISION=ADD_TOOL
CANDIDATE=faster-whisper (CPU, local, free)
```

采用前必须做一个真实无字幕视频pilot：
- 不使用OpenAI API或任何付费API；
- CPU-only；
- 输出带时间戳SRT/JSON；
- 不做摘要；
- 不做交易语义判断；
- 对几个随机时间点人工/机械对齐音频与视频，确认时间轴没有漂移。

若`faster-whisper`在该机器不稳定，再评估`whisper.cpp`；不要同时安装一堆候选。

## Sol evidence package

对每个最终需要ASR的视频，Codex只生成：

```text
BVID
原MP4路径
ASR SRT路径
ASR JSON路径
语言
时间轴
低置信片段列表
可按时间精确抽帧的索引
```

禁止Codex总结交易逻辑。

随后由GPT-5.6 Sol：
- 读转写；
- 回原视频对应画面；
- 修正ASR关键错字；
- 建立/更新claim与case；
- 处理与旧Dossier的冲突。

## 结束条件

只有在下列条件满足后，江河source corpus才能进入最终收口：

- 001–099每条来源状态明确；
- 007已修复或确认无法修复且原因明确；
- 022门控状态明确；
- 所有缺字幕BVID都被区分为远端遗漏/真实无字幕/获取失败；
- 所有真实无字幕且媒体可用的视频均完成本地免费ASR；
- 048/065/099的完整语义由Sol复核；
- 历史字幕计数差异得到解释；
- 所有开放review/contradiction重新审查；
- 不使用任何outcome validity数据。
