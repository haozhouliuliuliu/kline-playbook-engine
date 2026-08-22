# 江河语料缺口恢复结果 V0.2

> 范围：仅处理 V0.1 遗留的 007 媒体修复和 016/017/018/065 本地 ASR。
> 边界：不解释任何交易语义，不提交媒体、字幕、转写或凭据。

## 恢复结论

```text
CORPUS_RECOVERY_STATUS=INCOMPLETE_RETRYABLE_NETWORK_BLOCKERS
007_SOURCE_ACCESS=ACCOUNT_LOGIN_VERIFIED_AND_ACCESSIBLE
007_REDOWNLOAD=FAILED_RETRYABLE
007_FFPROBE=CURRENT_LOCAL_FILE_FAIL
007_FULL_DECODE_CHECK=CURRENT_LOCAL_FILE_FAIL
007_FINAL_STATUS=LOCAL_MEDIA_CORRUPT_PENDING_REPAIR

ASR_TOOL=faster-whisper / whisper.cpp
ASR_TOOL_STATUS=NO_TOOL_VERIFIED_FOR_LOCAL_ASR
ASR_MODEL=small / CPU / int8
ASR_PILOT_065=NOT_STARTED_NO_MODEL_FILE
ASR_COMPLETED_BVIDS=NONE
```

022 没有重新尝试绕过付费，仍为 `SOURCE_UNAVAILABLE_PAID_GATED`。

## 007 无损修复尝试

二维码登录通过，临时会话在当前账号下通过 `ACCOUNT_LOGIN_VERIFIED`。在此会话下，007 的 WBI 媒体清单仍可访问。

按既有安全路径先后尝试：

1. `yt-dlp` 认证的 `bestvideo*+bestaudio/best` 无损下载：在第一个媒体字节前持续停滞，未生成候选 MP4。
2. WBI/DASH 最高视频与音频流：增加有界断点续传和备用流轮换后，约数分钟只写入 8 MiB 视频分片，速度不足以在合理窗口完成完整媒体；没有开始音频、mux 或替换。

所有不完整数据仍位于 `D:\江河交易员\repair\007__BV1Da4xz6E8y\`。正式媒体文件和 `D:\江河交易员\quarantine\` 均未被修改，因为没有任何候选文件通过 ffprobe 与完整解码验收。

## 本地免费 ASR 诊断

`faster-whisper 1.2.1` 已存在。官方 Hugging Face 模型 API 和 `model.bin` 的首字节请求均可达（HTTP 200/206），磁盘空间充足；但默认下载留下 0 字节 `.incomplete`，确认残缺后已仅删除该 0 字节文件。禁用 Xet 后，配置、词表等小文件可完成，唯独 `model.bin` 仍不写入。

随后仅评估一个备用候选 `whisper.cpp`：官方 Windows x64 发布包和 GGML small 模型端点均可达，但发布包实测下载约 8--20 KB/s，无法在合理窗口取得二进制和模型。因此 `whisper.cpp` 保持 `CANDIDATE`，没有标记为 VERIFIED，也没有与 faster-whisper 并行作为生产工具。

016、017、018、065 继续为已确认无原生字幕、待本地转写状态。现有 Sol review packages 保持，不包含伪造的 ASR 文本。

## 安全与验证

```text
TEMPORARY_AUTH_MATERIAL_DELETED=YES
REPO_SECRET_SCAN=PASS
TARGETED_TESTS=23_PASS
FULL_SUITE=846_RUN_2_PRE_EXISTING_HOLY_GRAIL_ARTIFACT_FAILURES
GIT_DIFF_CHECK=PASS
```
