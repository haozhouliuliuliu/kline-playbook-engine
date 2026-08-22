# 江河语料缺口恢复结果 V0.5

> 范围：在既有 28 个完整模型分块基础上，完成最后分块、模型校验、本地 ASR 与 Sol review package 更新。
> 边界：未重新审计语料；未修改 007；未生成交易策略、摘要或交易语义解释；媒体、模型和转写均未进入 Git。

## 最终结果

```text
CORPUS_RECOVERY_STATUS=COMPLETE_WITH_PAID_GATE_EXCEPTION

007_FINAL_STATUS=MEDIA_OK

ASR_TOOL=faster-whisper
ASR_TOOL_STATUS=VERIFIED_FOR_LOCAL_ASR
ASR_MODEL=small_CPU_int8
ASR_MODEL_SOURCE=HUGGING_FACE_OFFICIAL_SYSTRAN_FASTER_WHISPER_SMALL
ASR_MODEL_HASH_VERIFIED=YES
ASR_MODEL_LOAD_TEST=PASS
ASR_COMPLETED_BVIDS=BV1DgCCB2E1g,BV1NBy5BfEYF,BV1K5ywBoEKz,BV1GSozBrE9e

065_ASR=PASS
016_ASR=PASS
017_ASR=PASS
018_ASR=PASS

PAID_GATE_EXCEPTION=022_SOURCE_UNAVAILABLE_PAID_GATED
```

最后一个 16 MiB `model.bin` Range 分块在新稳定节点下以单连接完成；此前 28 个完整分块被直接复用。完整模型的官方 LFS SHA-256 校验通过，随后通过 CTranslate2 CPU/int8 本地加载。

065 使用完整音频转写作为 pilot。默认 VAD 会漏掉低置信音频，因此最终统一配置为：CPU、int8、small、关闭 VAD、临时单声道响度归一化、保留模型产生的低置信段。该配置不人工补写文本；低置信段已写入各自的 CSV。065、016、017、018 均通过时间戳单调、首/中/尾覆盖和尾部覆盖检查。

四个 Sol review package 已更新：`subtitle_or_asr_path.txt` 指向本地 SRT 与 JSON，且均包含 `low_confidence_segments.csv` 与 `exact_range_requests_template.csv`。没有复制完整视频。

## 验证

```text
LAST_RANGE_RESUMED_CHUNKS=28
LAST_RANGE_TRANSFERRED_BYTES=16777216
LAST_RANGE_THROUGHPUT_MBPS=0.2924
TEMPORARY_AUTH_MATERIAL_DELETED=YES
```
