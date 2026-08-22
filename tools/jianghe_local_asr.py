"""以 faster-whisper 在本机 CPU 上转写已确认无原生字幕的江河视频。

只输出带时间戳的原始转写和工程核验资料；绝不生成摘要、策略或交易解释。
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.jianghe_corpus_gap_audit import seconds_to_srt


LOW_CONFIDENCE_AVG_LOGPROB = -1.0
LOW_CONFIDENCE_NO_SPEECH = 0.60


def read_audit(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def srt_text(segments: list[dict[str, Any]]) -> str:
    blocks = []
    for number, segment in enumerate(segments, start=1):
        blocks.append(
            f"{number}\n{seconds_to_srt(float(segment['start']))} --> {seconds_to_srt(float(segment['end']))}\n{segment['text'].strip()}"
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def low_confidence(segment: dict[str, Any]) -> bool:
    return (
        float(segment.get("avg_logprob", 0)) < LOW_CONFIDENCE_AVG_LOGPROB
        or float(segment.get("no_speech_prob", 0)) >= LOW_CONFIDENCE_NO_SPEECH
    )


def validate_timeline(segments: list[dict[str, Any]], duration: float | None) -> dict[str, Any]:
    monotonic = all(
        float(current["start"]) >= float(previous["start"])
        and float(current["end"]) >= float(current["start"])
        and float(current["start"]) >= float(previous["end"])
        for previous, current in zip(segments, segments[1:])
    )
    first_start = float(segments[0]["start"]) if segments else None
    last_end = float(segments[-1]["end"]) if segments else None
    tail_gap = duration - last_end if duration is not None and last_end is not None else None
    thirds_covered = [False, False, False]
    if duration and duration > 0:
        for segment in segments:
            start, end = float(segment["start"]), float(segment["end"])
            for index in range(3):
                lower, upper = duration * index / 3, duration * (index + 1) / 3
                if start < upper and end > lower:
                    thirds_covered[index] = True
    return {
        "segment_count": len(segments),
        "timestamps_monotonic": monotonic,
        "first_speech_start_seconds": first_start,
        "last_speech_end_seconds": last_end,
        "media_duration_seconds": duration,
        "tail_gap_seconds": tail_gap,
        "start_middle_end_transcribed": all(thirds_covered) if duration and duration > 0 else bool(segments),
        "audio_decode_and_timeline_pass": bool(segments and monotonic and (tail_gap is None or tail_gap <= 30) and (all(thirds_covered) if duration and duration > 0 else True)),
        "alignment_sampling_seconds": [0, round((duration or 0) / 2, 3), round(max(0, (duration or 0) - 10), 3)],
        "alignment_note": "三个时间点仅作音频/画面回听复核索引；本工具不解释任何交易内容。",
    }


def write_package(record: dict[str, Any], asr_json_path: Path, low_confidence_rows: list[dict[str, Any]], validation: dict[str, Any], root: Path) -> Path:
    ordinal = int(record["source_ordinal"])
    bvid = str(record["bvid"])
    package = root / "sol_review_packages" / f"{ordinal:03}__{bvid}"
    package.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source_ordinal": ordinal,
        "bvid": bvid,
        "title": record.get("title"),
        "source_url": record.get("source_url"),
        "media_status": record.get("media_status"),
        "asr_engine": "faster-whisper",
        "asr_json_path": str(asr_json_path),
        "validation": validation,
    }
    (package / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (package / "original_video_path.txt").write_text(str(record["media_path"]) + "\n", encoding="utf-8")
    (package / "subtitle_or_asr_path.txt").write_text(str(asr_json_path.with_suffix(".srt")) + "\n" + str(asr_json_path) + "\n", encoding="utf-8")
    with (package / "low_confidence_segments.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["start", "end", "avg_logprob", "no_speech_prob"])
        writer.writeheader()
        writer.writerows(low_confidence_rows)
    with (package / "exact_range_requests_template.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["candidate_start", "candidate_end", "requested_sol_action", "status"])
        writer.writeheader()
        for second in validation["alignment_sampling_seconds"]:
            writer.writerow({"candidate_start": seconds_to_srt(second), "candidate_end": seconds_to_srt(second + 10), "requested_sol_action": "VERIFY_AUDIO_AND_SAME_TIME_VISUAL", "status": "PENDING"})
    (package / "README.txt").write_text(
        "工程证据包：包含原视频路径、逐字 ASR 路径、低置信时间段和时间范围复核模板。\n"
        "未包含交易策略、摘要或语义解释；请由 Sol 结合原视频同时间画面进行复核。\n",
        encoding="utf-8",
    )
    return package


def write_failed_package(record: dict[str, Any], reason: str, root: Path) -> Path:
    """ASR 引擎不可用时仍保留可供 Sol 直接回看原视频的最小证据包。"""
    ordinal = int(record["source_ordinal"])
    bvid = str(record["bvid"])
    package = root / "sol_review_packages" / f"{ordinal:03}__{bvid}"
    package.mkdir(parents=True, exist_ok=True)
    manifest = {
        "source_ordinal": ordinal, "bvid": bvid, "title": record.get("title"), "source_url": record.get("source_url"),
        "media_status": record.get("media_status"), "asr_engine": "faster-whisper", "asr_status": "FAILED", "failure_reason": reason,
    }
    (package / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (package / "original_video_path.txt").write_text(str(record["media_path"]) + "\n", encoding="utf-8")
    (package / "subtitle_or_asr_path.txt").write_text("ASR_FAILED_NO_TRANSCRIPT\n", encoding="utf-8")
    (package / "low_confidence_segments.csv").write_text("start,end,avg_logprob,no_speech_prob\n", encoding="utf-8")
    (package / "exact_range_requests_template.csv").write_text("candidate_start,candidate_end,requested_sol_action,status\n00:00:00,00:00:10,VERIFY_AUDIO_AND_SAME_TIME_VISUAL,PENDING\n", encoding="utf-8")
    (package / "README.txt").write_text(
        "工程证据包：本机 faster-whisper 模型下载未完成，未生成 ASR 文本。\n"
        "请由 Sol 直接回看原视频；本包不包含交易策略、摘要或语义解释。\n",
        encoding="utf-8",
    )
    return package


def transcribe_record(model: Any, record: dict[str, Any], root: Path) -> dict[str, Any]:
    media_path = Path(str(record["media_path"]))
    if not media_path.is_file():
        raise RuntimeError(f"媒体不存在：{media_path}")
    segments_iter, info = model.transcribe(
        str(media_path), language="zh", beam_size=5, vad_filter=True, condition_on_previous_text=False,
    )
    segments = [
        {
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
            "avg_logprob": segment.avg_logprob,
            "no_speech_prob": segment.no_speech_prob,
            "compression_ratio": segment.compression_ratio,
        }
        for segment in segments_iter
    ]
    validation = validate_timeline(segments, record.get("duration"))
    asr_dir = root / "asr"
    asr_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{int(record['source_ordinal']):03}__{record['bvid']}.local-asr"
    json_path = asr_dir / f"{stem}.json"
    srt_path = asr_dir / f"{stem}.srt"
    payload = {
        "source_ordinal": record["source_ordinal"], "bvid": record["bvid"], "language": getattr(info, "language", "zh"),
        "language_probability": getattr(info, "language_probability", None), "engine": "faster-whisper",
        "model": "small", "device": "cpu", "compute_type": "int8", "segments": segments, "validation": validation,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    srt_path.write_text(srt_text(segments), encoding="utf-8", newline="\n")
    low_rows = [{key: segment[key] for key in ("start", "end", "avg_logprob", "no_speech_prob")} for segment in segments if low_confidence(segment)]
    package = write_package(record, json_path, low_rows, validation, root)
    return {"bvid": record["bvid"], "status": "PASS" if validation["audio_decode_and_timeline_pass"] else "TIMELINE_VALIDATION_FAILED", "asr_json": str(json_path), "package": str(package), "validation": validation}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", default=r"D:\江河交易员")
    parser.add_argument("--ordinal", type=int, action="append", help="只转写指定 ordinal；默认全部需要 ASR 的条目")
    parser.add_argument("--record-failure", help="仅记录已验证的 ASR 引擎失败原因，并生成 Sol 证据包")
    parser.add_argument("--model-path", help="已完成校验的本地 faster-whisper 模型目录；不填才使用缓存模型名")
    args = parser.parse_args()
    try:
        from faster_whisper import WhisperModel
    except ImportError as error:
        raise RuntimeError("缺少 faster-whisper；请先安装唯一的 ASR 候选工具") from error
    root = Path(args.corpus_root).resolve()
    records = read_audit(root / "manifests" / "final_corpus_gap_audit.jsonl")
    selected = [record for record in records if record.get("needs_asr")]
    if args.ordinal:
        selected = [record for record in selected if int(record["source_ordinal"]) in set(args.ordinal)]
    if not selected:
        raise RuntimeError("没有符合条件的已确认无原生字幕媒体")
    if args.record_failure:
        results = [{"bvid": record["bvid"], "status": "ASR_FAILED", "package": str(write_failed_package(record, args.record_failure, root))} for record in selected]
        print(json.dumps({"STATUS": "ASR_FAILED_RECORDED", "results": results}, ensure_ascii=False))
        return 2
    model = WhisperModel(args.model_path or "small", device="cpu", compute_type="int8")
    results = [transcribe_record(model, record, root) for record in selected]
    print(json.dumps({"STATUS": "PASS", "results": results}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print("STATUS=FAILED_FAIL_CLOSED\nREASON=" + str(error), flush=True)
        raise SystemExit(1)
