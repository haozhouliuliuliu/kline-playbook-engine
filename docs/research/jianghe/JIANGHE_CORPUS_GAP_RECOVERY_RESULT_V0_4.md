# 江河语料缺口恢复结果 V0.4

> 范围：只继续 V0.3 已保留的 007 媒体和 faster-whisper small 模型分块；没有重审 99 条来源，也没有解释交易语义。

## 本轮结果

```text
007_REDOWNLOAD=PASS_RESUMED_FROM_COMPLETE_RANGE_CHUNKS
007_FFPROBE=PASS
007_FULL_DECODE=PASS
007_FINAL_STATUS=MEDIA_OK
007_CODEC=hevc
007_RESOLUTION=1728x1080

ASR_TOOL=faster-whisper
ASR_TOOL_STATUS=CANDIDATE_NOT_VERIFIED_FINAL_MODEL_RANGE_BLOCKED
ASR_MODEL=small_CPU_int8
ASR_MODEL_SOURCE=HUGGING_FACE_OFFICIAL_SYSTRAN_FASTER_WHISPER_SMALL
ASR_MODEL_HASH_VERIFIED=NO
ASR_MODEL_LOAD_TEST=NOT_RUN
ASR_COMPLETED_BVIDS=NONE
NETWORK_ROUTE_BLOCKED=YES
```

007 使用现存完整分块恢复最高可用原始 DASH 视频与音频。视频 35,400,928 字节、音频 9,036,881 字节均完整校验后，以 `ffmpeg -c copy` 无损 mux。候选文件的 ffprobe 验证为视频和音频流齐全、1728x1080、HEVC、时长 858.721791 秒；严格完整解码通过。旧损坏媒体随后移入仓库外 quarantine，新文件才放回正式 media 路径。临时认证材料在完成后已删除。

官方模型的前 28 个 16 MiB Range 分块已从 V0.3 的已完成分块续传并校验。最后一个缺失分块先后尝试：官方 Hugging Face 地址、一个同对象镜像候选、`urllib`、`httpx` 和系统 `curl` 的严格 Range 传输。镜像和官方 `curl` 返回未满足严格 `206`/`Content-Range` 的响应；其他传输在限定窗口内未获得完整正文。下载器拒绝拼装不完整模型，因而没有运行 CTranslate2 加载或任何 ASR。

016、017、018、065 的现有 Sol review package 未写入伪造文本；`subtitle_or_asr_path.txt`、`low_confidence_segments.csv` 和 `exact_range_requests_template.csv` 保持原有无 ASR 状态。022 仍为 `SOURCE_UNAVAILABLE_PAID_GATED`，没有绕过或购买。

## 验证

```text
RANGE_DOWNLOADER_TESTS=PASS
EVIDENCE_VALIDATION=PASS
GIT_DIFF_CHECK=PASS
FULL_SUITE=RUN_WITH_2_PRE_EXISTING_HOLY_GRAIL_ARTIFACT_FAILURES
TEMPORARY_AUTH_MATERIAL_DELETED=YES
```
