# JIANGHE_TRADER_CORPUS_ACCEPTANCE_AND_ANALYSIS_PREP_V0_1

JiangHe Trader（交易员江河）Bilibili 语料验收与分析准备文档。

> 边界声明：本阶段为工程/证据整理执行者。严禁总结、解释或蒸馏任何交易策略；
> 不访问任何候选表现 / 回测数据；不修改冻结的 Research Protocol。

---

## 1. 来源与获取状态

| 项 | 值 |
|---|---|
| UP UID | 3546770449631285 |
| 公开枚举总数 (ENUMERATED) | 99 |
| 本地可达 (LOCAL_AVAILABLE) | 98 |
| 取得失败 / 付费门控 (UNAVAILABLE_PAID_GATED) | 1 |
| 损坏 (CORRUPT) | 0 |
| 重复 BVID (DUPLICATE) | 0 |
| 验收可用 (ACCEPTED_FOR_RESEARCH) | 98 |

唯一未取得视频：`BV19b2kBxEhi`「裸k交易方式演练与实盘讲解-充电直播回放」
（ordinal 22，upload_date 20251208）。状态记 `UNAVAILABLE_PAID_GATED`（付费/充电专属，需开通包月），
**不记为 DOWNLOAD_FAILURE**。原始枚举来源：`manifests/source_manifest.jsonl`（WBI_SPACE_API）。

下载 runner 已退出，进度文件 `manifests/download_progress.json` 标记 `state=COMPLETE`，
`downloaded=98 / failed=1 / remaining=0`。

---

## 2. 语料完整性验收 (B)

对 99 条枚举逐项机械检查（脚本：`tools/corpus_acceptance.py`），产出：

- `manifests/corpus_acceptance.jsonl`
- `manifests/corpus_acceptance.csv`

检查项（每条）：文件存在、非零大小、ffprobe 可读、video stream 存在、audio stream 存在、
duration 合理、width/height/fps/codec、SHA256、BVID 对应关系、重复 BVID/part、manifest 路径存在。

结论：98 本地视频全部通过（CORRUPT=0，DUPLICATE=0），均写入 SHA256 以便后续取证溯源。

---

## 3. 字幕盘点 (C)

判定规则（纯机械，不把弹幕当作者字幕）：

- `NATIVE`：存在 Bilibili 原生下载字幕 `subtitles/<...>.ai-zh.srt`
- `NONE_NEEDS_ASR`：无原生字幕轨；需后续本地 ASR 才有文本（不做 OCR，无法判定硬字幕）
- `BURNED_IN_ONLY`：未通过 OCR 确认，**本阶段计 0**（避免无证据臆断）
- `UNKNOWN`：付费门控视频（无本地文件）

| 统计 | 数量 |
|---|---|
| NATIVE_SUBTITLE_COUNT | 90 |
| BURNED_IN_ONLY_COUNT | 0 |
| NONE_NEEDS_ASR_COUNT | 8 |
| UNKNOWN (付费) | 1 |

---

## 4. 正式 analysis queue (D)

按 `upload_date` 从早到晚排序（`tools/corpus_acceptance.py` 一并生成）：

- `manifests/analysis_queue.jsonl`
- `manifests/analysis_queue.csv`

字段：`analysis_ordinal, bvid, title, upload_date, duration_seconds, local_video_path,
video_sha256, width, height, fps, subtitle_status, subtitle_path, source_status, analysis_status`。

- `source_status`：`AVAILABLE` / `UNAVAILABLE_PAID_GATED`（付费视频保留在索引中但不进入本地分析）
- `analysis_status` 初始：`PENDING`
- 付费视频排在队列末尾（analysis_ordinal=null），仅作来源索引。

---

## 5. 前 5 条 ANALYSIS PACKAGE PILOT (F)

对 `analysis_queue` 最早 5 个 AVAILABLE 视频生成 pilot 包（`tools/build_pilot_package.py`）：

```
D:\江河交易员\analysis_packages\<ordinal>__<BVID>\
  manifest.json
  source_metadata.json      (嵌入原始 yt-dlp info.json)
  transcript_or_subtitle.srt (若有原生字幕则复制)
  visual_index\             (固定时间覆盖帧 + index.json，机械采样，无 AI 挑选)
  README.txt
```

| # | BVID | 帧数 | 覆盖间隔 |
|---|---|---|---|
| 1 | BV1yxebzoERD | 32 | 15s |
| 2 | BV1qEamztEz1 | 40 | 15s |
| 3 | BV1q9WAzjEev | 40 | 15s |
| 4 | BV12tn2zGEgH | 35 | 15s |
| 5 | BV16fxYzGEA3 | 40 | 15s |

规则：原视频始终保留；任何重要结论后续必须通过 `exact_range` 工具回原视频高密度复查。
不加 ASR、不蒸馏交易语义。

---

## 6. exact-range 取证工具 (E)

`tools/exact_range.py` — 本地只读工具（不修改原视频、不做 AI 分析/OCR、不自动挑选片段）。

能力：
- 指定时间戳抽取原分辨率单帧 PNG（准确 seek）
- 指定时间范围按帧间隔连续抽帧，附时间戳清单
- 可选无损（stream-copy）短片段

测试 `tests/test_exact_range.py`：`exact timestamp`、`range extraction`、`Windows path`、`invalid BVID` 全部通过。

---

## 7. 本地 ASR 可行性评估 (G)

本机硬件：

| 资源 | 规格 |
|---|---|
| CPU | AMD Ryzen 5 550, 6 核 / 12 线程 |
| RAM | 15.3 GB |
| GPU | AMD Radeon(TM) Graphics，可用显存 0.5 GB（集成显卡，无独立大显存） |
| D 盘剩余 | ~219 GB |

候选方案（状态仅 CANDIDATE，未安装）：

- `whisper.cpp`：C++，CPU 推理，体积小，适合无 GPU 环境 — **CANDIDATE**
- `faster-whisper`：Python，CTranslate2，CPU 推理优于原版 whisper — **CANDIDATE**

现状：本机**未安装**任何 whisper/ASR 工具，`ffmpeg` 就绪。

决策（ASR_TOOL_DECISION）：**ADD_TOOL**
- 8 个 NONE_NEEDS_ASR 视频（短片，约 10 分钟级）可在本地 CPU 跑 `faster-whisper` small 模型完成；
- GPU 显存不足，须 CPU 推理，需评估耗时（非实时）；
- 严禁使用任何付费 API。
- 仅在 Owner 明确批准后安装，且只装到用户级/项目级隔离环境。

---

## 8. 交付物与边界

- 工具代码：`tools/corpus_acceptance.py`、`tools/exact_range.py`、`tools/build_pilot_package.py`
- 测试：`tests/test_exact_range.py`（ALL TESTS PASSED）
- 摘要 manifest/evidence：`manifests/corpus_acceptance.*`、`manifests/analysis_queue.*`
- 文档：本文件

**不提交 Git**：`D:\江河交易员\media\`、`subtitles\`、`analysis_packages\`（含帧）、`logs\` 等大型语料/帧/字幕包。
**不分析交易语义**：所有内容为机械覆盖与取证准备，无任何策略解读。
