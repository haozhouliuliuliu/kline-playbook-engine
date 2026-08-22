# 江河语料媒体与字幕缺口审计结果 V0.1

> 范围：source manifest 中的 001--099（唯一 join key 为 BVID）
> 执行边界：只做媒体、字幕、转写和证据运输；不包含任何交易语义解释。

## 最终计数

```text
SOURCE_COUNT=99
UNIQUE_BVID_COUNT=99
MEDIA_OK=97
MEDIA_CORRUPT=1
MEDIA_MISSING=0
SOURCE_PAID_GATED=1

NATIVE_SUBTITLE_VERIFIED_LOCAL=94
REMOTE_SUBTITLE_RECOVERED=4
NO_NATIVE_SUBTITLE_CONFIRMED_NEEDS_ASR=4
SOURCE_UNAVAILABLE_PAID_GATED=1
SUBTITLE_FETCH_FAILED_RETRYABLE=0
```

完整逐 BVID 审计输出（不在 Git 中提交媒体或字幕）：

```text
D:\江河交易员\manifests\final_corpus_gap_audit.jsonl
D:\江河交易员\manifests\final_corpus_gap_audit.csv
```

所有 99 条都有明确媒体和最终字幕状态；没有把网络失败写成“无字幕”。所有本地最终 MP4 都被 ffprobe 检查；97 个通过，007 被严格错误输出判为损坏，022 没有本地媒体且为付费门控。

## 远端字幕恢复与真实无原生字幕

对审计开始时本地缺字幕的 BVID 使用当前登录态查询 CID 和字幕轨道。远端存在但本地缺失的 4 条已原样下载为 SRT：009、014、048、099。

```text
009=BV1qXWvzTETj
014=BV1xX1SBFE3s
048=BV1Ybckz4EKX
099=BV1Yu8p68EYJ
```

远端成功返回零字幕轨道、媒体又可用的 4 条为 016、017、018、065；它们是唯一进入本地 ASR 队列的条目。048 的旧“仅烧录字幕”状态被当前可取得的远端 AI 字幕替代，最终状态为 `NATIVE_SUBTITLE_VERIFIED_LOCAL`。

## 007、022、048、065、099

```text
007_SOURCE_ACCESS=ACCESSIBLE
007_LOCAL_MEDIA=MEDIA_CORRUPT
007_REDOWNLOAD=FAILED_RETRYABLE_NO_VALID_CANDIDATE
007_FFPROBE=VIDEO_AND_AUDIO_STREAMS_PRESENT_BUT_STRICT_ERROR_OUTPUT
007_FINAL_STATUS=LOCAL_MEDIA_CORRUPT_PENDING_REPAIR

022_SOURCE_ACCESS=PAID_GATED (WBI code 87008)
022_FINAL_STATUS=SOURCE_UNAVAILABLE_PAID_GATED

048_FINAL_STATUS=NATIVE_SUBTITLE_VERIFIED_LOCAL (remote AI subtitle recovered)
065_FINAL_STATUS=NO_NATIVE_SUBTITLE_CONFIRMED_NEEDS_ASR

099_BVID=BV1Yu8p68EYJ
099_TITLE=小资金如何做大？
099_MEDIA_STATUS=MEDIA_OK (video + audio ffprobe PASS)
099_FINAL_STATUS=NATIVE_SUBTITLE_VERIFIED_LOCAL (remote AI subtitle recovered)
```

007 的源端媒体清单在当前登录态下可访问。旧本地 MP4 与旧 manifest 哈希一致，却在严格 ffprobe/完整解码中出现 AV1 解析错误，所以不能继续标为正常文件。直接 DASH 下载和项目已验证的 yt-dlp 无损下载均在尚未形成候选 MP4 时停滞；没有隔离或覆盖旧文件。临时下载残留保留在 `D:\江河交易员\repair\007__BV1Da4xz6E8y\`，原文件仍在原路径，尚无可放入 `quarantine` 的已替换旧件。

## 历史“90 vs 89”差异

```text
OLD_REPORTED_SUBTITLE_COUNT=90
OLD_FOLDER_SUBTITLE_COUNT=89 (历史人工/Windows 观察值)
FRESH_PRE_RECOVERY_PHYSICAL_SRT_COUNT=90
FRESH_PRE_RECOVERY_MANIFEST_REFERENCED_SRT_COUNT=90
FRESH_PRE_RECOVERY_BVID_JOIN_MATCH=90_OF_90
NEW_BVID_VERIFIED_SUBTITLE_COUNT=94
DISCREPANCY_ROOT_CAUSE=历史 89 项目录观察无法复现；实际磁盘与 corpus manifest 在补救前均为 90，且按 BVID 一对一匹配，无删除、重命名、重复 BVID 或 part 映射差异证据。故差异属于当时的陈旧/筛选式 Windows 视图计数，而非语料落盘差异。
```

## ASR 决策与 Sol 证据包

机械审计阶段的工具决策为 `USE_EXISTING`。确认 4 条真实无原生字幕后，按规定只新增一个本地免费候选：

```text
ASR_TOOL_DECISION=ADD_TOOL
ASR_TOOL=faster-whisper 1.2.1
ASR_MODE=small / CPU / int8
ASR_PILOT=FAILED_MODEL_DOWNLOAD_STALLED
ASR_COMPLETED_BVIDS=NONE
```

065 被选作试点。软件包已安装，但公开 `small` 模型下载持续无进度，未进入音频转写；本机也没有 `whisper.cpp` 命令，因此没有混用或安装第二个 ASR 工具。没有生成任何伪造的 SRT/JSON。016、017、018、065 各自的包明确记录为 `ASR_FAILED`，供 Sol 直接回看原视频；048、065、099 的包均已建立。

```text
D:\江河交易员\sol_review_packages\016__BV1DgCCB2E1g
D:\江河交易员\sol_review_packages\017__BV1NBy5BfEYF
D:\江河交易员\sol_review_packages\018__BV1K5ywBoEKz
D:\江河交易员\sol_review_packages\048__BV1Ybckz4EKX
D:\江河交易员\sol_review_packages\065__BV1GSozBrE9e
D:\江河交易员\sol_review_packages\099__BV1Yu8p68EYJ
```

每个包只包含原视频路径、字幕或 ASR 路径、低置信段表、精确时间范围模板及工程 README；不复制视频，不写交易策略解释。

## 验证与安全

```text
UNIT_TESTS=23_PASS
GIT_DIFF_CHECK=PASS
COOKIE_TOKEN_PASSWORD_IN_REPO=NO
```

登录 Cookie 只从仓库外的临时 Bilibili 会话文件读取，未写入仓库、审计清单、测试夹具或日志；本任务使用的会话文件及测试副本已删除。未完成的 007 repair 临时目录保留为下载失败证据；后续需要重新登录后，再跑 007 的无损修复和 065 的 ASR 试点。
