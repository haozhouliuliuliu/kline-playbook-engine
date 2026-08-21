"""可恢复地获取 Bilibili UP 主公开视频语料。

本工具只保存视频、字幕、元数据和完整性证据；不读取或解释交易内容。Chrome
登录态只会由 yt-dlp 在运行时读取，绝不导出、打印或持久化 Cookie。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen


UP_UID = "3546770449631285"
UP_URL = f"https://space.bilibili.com/{UP_UID}/video"
LOG_SECRET_PATTERN = re.compile(r"(?i)(sessdata|cookie|token|authorization)\s*[=:]\s*[^\s;,&]+")
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL", *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
WBI_MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35,
    27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13,
    37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4,
    22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52,
]
HTTP_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Referer": UP_URL,
}


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_output_dir() -> Path:
    user_profile = Path(os.environ.get("USERPROFILE", Path.home()))
    return user_profile / "Videos" / "kline-playbook-engine" / "bilibili" / UP_UID


def sanitize_windows_filename(value: str, fallback: str = "untitled") -> str:
    """返回稳定、Windows 安全的单个文件名片段。"""
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", value).strip(" .")
    cleaned = re.sub(r"\s+", " ", cleaned)
    if not cleaned:
        cleaned = fallback
    if cleaned.upper() in WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned[:120].rstrip(" .") or fallback


def redact_sensitive_text(value: str) -> str:
    return LOG_SECRET_PATTERN.sub(lambda match: f"{match.group(1)}=[REDACTED]", value)


def bvid_from_entry(entry: dict[str, Any]) -> str | None:
    for candidate in (entry.get("bvid"), entry.get("id"), entry.get("url")):
        if isinstance(candidate, str):
            match = re.search(r"BV[0-9A-Za-z]+", candidate)
            if match:
                return match.group(0)
    return None


def normalize_entry(entry: dict[str, Any], ordinal: int, enumerated_at: str) -> dict[str, Any] | None:
    bvid = bvid_from_entry(entry)
    if not bvid:
        return None
    timestamp = entry.get("timestamp")
    upload_date = entry.get("upload_date")
    if not upload_date and isinstance(timestamp, (int, float)):
        upload_date = datetime.fromtimestamp(timestamp, UTC).strftime("%Y%m%d")
    part_count = entry.get("part_count") or entry.get("n_entries") or 1
    return {
        "ordinal": ordinal,
        "bvid": bvid,
        "aid_if_available": entry.get("aid") or entry.get("display_id"),
        "cid_if_available": entry.get("cid"),
        "title": entry.get("title") or "UNKNOWN",
        "description_if_available": entry.get("description"),
        "upload_date": upload_date,
        "timestamp": timestamp,
        "duration_seconds": entry.get("duration"),
        "original_url": entry.get("webpage_url") or f"https://www.bilibili.com/video/{bvid}",
        "uploader": entry.get("uploader") or entry.get("channel"),
        "uploader_id": str(entry.get("uploader_id") or entry.get("channel_id") or UP_UID),
        "playlist_index_if_available": entry.get("playlist_index"),
        "availability": entry.get("availability") or "public",
        "is_multi_part": bool(part_count and int(part_count) > 1),
        "part_count": part_count,
        "enumeration_source": entry.get("enumeration_source") or "yt-dlp:BilibiliSpaceVideo",
        "enumerated_at": enumerated_at,
        "estimated_bytes": best_known_size(entry),
    }


def best_known_size(info: dict[str, Any]) -> int | None:
    sizes = [
        item.get("filesize") or item.get("filesize_approx")
        for item in info.get("formats", []) if isinstance(item, dict)
    ]
    sizes = [int(size) for size in sizes if isinstance(size, (int, float)) and size > 0]
    return max(sizes) if sizes else None


def deduplicate_bvids(entries: Iterable[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    duplicates = 0
    for entry in entries:
        bvid = str(entry["bvid"])
        if bvid in seen:
            duplicates += 1
            continue
        seen.add(bvid)
        unique.append(entry)
    unique.sort(key=lambda item: (item.get("timestamp") is None, item.get("timestamp") or 0, item["bvid"]))
    for ordinal, item in enumerate(unique, start=1):
        item["ordinal"] = ordinal
    return unique, duplicates


def source_manifest_is_complete(reported_total: int | None, entries: list[dict[str, Any]]) -> bool:
    return reported_total is not None and reported_total >= 0 and len(entries) == reported_total


def part_identity(bvid: str, part: int | None) -> str:
    return f"{bvid}__p{part or 1:02d}"


def disk_capacity_safe(estimated_bytes: int | None, free_bytes: int) -> bool:
    return estimated_bytes is not None and estimated_bytes >= 0 and estimated_bytes <= free_bytes * 0.70


def ensure_output_layout(output_dir: Path) -> None:
    for name in ("media", "metadata", "subtitles", "manifests", "logs"):
        (output_dir / name).mkdir(parents=True, exist_ok=True)


def write_jsonl_csv(path_base: Path, records: list[dict[str, Any]], fields: list[str]) -> None:
    with path_base.with_suffix(".jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    with path_base.with_suffix(".csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def run_command(command: list[str], log_path: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(command, text=True, capture_output=True, encoding="utf-8", errors="replace")
    log_path.write_text(
        redact_sensitive_text(process.stdout + "\n" + process.stderr), encoding="utf-8"
    )
    if check and process.returncode != 0:
        raise RuntimeError(f"命令失败，详情见：{log_path}")
    return process


def yt_dlp_json(yt_dlp: str, url: str, log_path: Path, *, flat: bool = False) -> dict[str, Any]:
    command = [yt_dlp, "--cookies-from-browser", "chrome", "--skip-download", "--dump-single-json", "--no-warnings"]
    if flat:
        command.append("--flat-playlist")
    command.append(url)
    result = run_command(command, log_path)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"yt-dlp 未返回可解析元数据，详情见：{log_path}") from error


def fetch_json(url: str) -> dict[str, Any]:
    request = Request(url, headers=HTTP_HEADERS)
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def wbi_mixin_key(image_url: str, sub_url: str) -> str:
    source = Path(urlparse(image_url).path).stem + Path(urlparse(sub_url).path).stem
    if len(source) < max(WBI_MIXIN_KEY_ENC_TAB) + 1:
        raise RuntimeError("Bilibili WBI 密钥格式无效")
    return "".join(source[index] for index in WBI_MIXIN_KEY_ENC_TAB)[:32]


def signed_wbi_query(parameters: dict[str, Any], mixin_key: str) -> str:
    filtered = {
        key: re.sub(r"[!'()*]", "", str(value))
        for key, value in parameters.items()
        if value is not None
    }
    filtered["wts"] = str(int(time.time()))
    query = urlencode(sorted(filtered.items()))
    return f"{query}&w_rid={hashlib.md5((query + mixin_key).encode()).hexdigest()}"


def parse_duration(value: str | None) -> int | None:
    if not value:
        return None
    try:
        parts = [int(part) for part in value.split(":")]
    except ValueError:
        return None
    seconds = 0
    for part in parts:
        seconds = seconds * 60 + part
    return seconds


def enumerate_wbi_space() -> tuple[list[dict[str, Any]], int | None, int, bool]:
    """WBI Space API 备用枚举；只读取公开视频元数据，不读取浏览器凭据。"""
    nav = fetch_json("https://api.bilibili.com/x/web-interface/nav")
    wbi_img = nav.get("data", {}).get("wbi_img", {})
    mixin_key = wbi_mixin_key(wbi_img.get("img_url", ""), wbi_img.get("sub_url", ""))
    raw_entries: list[dict[str, Any]] = []
    reported_total: int | None = None
    page_number = 1
    while True:
        query = signed_wbi_query({
            "mid": UP_UID, "pn": page_number, "ps": 50, "order": "pubdate",
            "platform": "web", "web_location": "1550101",
        }, mixin_key)
        payload = fetch_json(f"https://api.bilibili.com/x/space/wbi/arc/search?{query}")
        if payload.get("code") != 0:
            raise RuntimeError(f"WBI Space API 返回 code={payload.get('code')}")
        data = payload.get("data", {})
        page = data.get("page", {})
        count = page.get("count")
        if isinstance(count, int):
            reported_total = count
        page_entries = data.get("list", {}).get("vlist", [])
        if not page_entries:
            break
        raw_entries.extend(item for item in page_entries if isinstance(item, dict))
        if reported_total is not None and len(raw_entries) >= reported_total:
            break
        page_number += 1
    enumerated_at = utc_now()
    normalized = []
    for index, entry in enumerate(raw_entries, start=1):
        entry = dict(entry)
        entry.update({
            "id": entry.get("bvid"), "timestamp": entry.get("created"),
            "duration": parse_duration(entry.get("length")), "uploader": entry.get("author"),
            "uploader_id": entry.get("mid"), "webpage_url": f"https://www.bilibili.com/video/{entry.get('bvid')}",
            "enumeration_source": "Bilibili:WBI_SPACE_API",
        })
        record = normalize_entry(entry, index, enumerated_at)
        if record:
            normalized.append(record)
    unique, duplicates = deduplicate_bvids(normalized)
    return unique, reported_total, duplicates, source_manifest_is_complete(reported_total, unique)


def enumerate_source(yt_dlp: str, output_dir: Path) -> tuple[list[dict[str, Any]], int | None, int, bool]:
    try:
        discovered = yt_dlp_json(yt_dlp, UP_URL, output_dir / "logs" / "enumerate-space.log", flat=True)
    except RuntimeError:
        entries, reported_total, duplicates, complete = enumerate_wbi_space()
        source_fields = list(entries[0].keys()) if entries else []
        write_jsonl_csv(output_dir / "manifests" / "source_manifest", entries, source_fields)
        (output_dir / "manifests" / "enumeration_summary.json").write_text(json.dumps({
            "UPLOADER_REPORTED_TOTAL": reported_total, "ENUMERATED_UNIQUE_BVIDS": len(entries),
            "DUPLICATES_REMOVED": duplicates, "ENUMERATION_COMPLETE": "YES" if complete else "NO",
            "enumeration_method": "Bilibili:WBI_SPACE_API", "enumerated_at": utc_now(),
        }, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        return entries, reported_total, duplicates, complete
    raw_entries = [item for item in discovered.get("entries", []) if isinstance(item, dict)]
    reported_total_raw = discovered.get("playlist_count") or discovered.get("n_entries")
    reported_total = int(reported_total_raw) if isinstance(reported_total_raw, (int, float, str)) and str(reported_total_raw).isdigit() else None
    enriched: list[dict[str, Any]] = []
    enumerated_at = utc_now()
    for index, raw_entry in enumerate(raw_entries, start=1):
        bvid = bvid_from_entry(raw_entry)
        if not bvid:
            continue
        details = yt_dlp_json(yt_dlp, f"https://www.bilibili.com/video/{bvid}", output_dir / "logs" / f"metadata-{bvid}.log")
        details["enumeration_source"] = "yt-dlp:BilibiliSpaceVideo+video-metadata"
        normalized = normalize_entry(details, index, enumerated_at)
        if normalized:
            enriched.append(normalized)
            (output_dir / "metadata" / f"{bvid}.info.json").write_text(
                json.dumps(details, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
            )
    unique, duplicates = deduplicate_bvids(enriched)
    complete = source_manifest_is_complete(reported_total, unique)
    source_fields = list(unique[0].keys()) if unique else [
        "ordinal", "bvid", "aid_if_available", "cid_if_available", "title", "description_if_available",
        "upload_date", "timestamp", "duration_seconds", "original_url", "uploader", "uploader_id",
        "playlist_index_if_available", "availability", "is_multi_part", "part_count", "enumeration_source",
        "enumerated_at", "estimated_bytes",
    ]
    write_jsonl_csv(output_dir / "manifests" / "source_manifest", unique, source_fields)
    summary = {
        "UPLOADER_REPORTED_TOTAL": reported_total,
        "ENUMERATED_UNIQUE_BVIDS": len(unique),
        "DUPLICATES_REMOVED": duplicates,
        "ENUMERATION_COMPLETE": "YES" if complete else "NO",
        "enumeration_method": "yt-dlp:BilibiliSpaceVideo",
        "enumerated_at": enumerated_at,
    }
    (output_dir / "manifests" / "enumeration_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    return unique, reported_total, duplicates, complete


def select_best_video_format(info: dict[str, Any]) -> dict[str, Any] | None:
    video_formats = [
        item for item in info.get("formats", [])
        if isinstance(item, dict) and item.get("vcodec") not in (None, "none")
    ]
    if not video_formats:
        return None
    return max(video_formats, key=lambda item: (item.get("height") or 0, item.get("fps") or 0, item.get("tbr") or 0))


def resolution_label(format_info: dict[str, Any] | None) -> str:
    if not format_info:
        return "UNKNOWN"
    width, height = format_info.get("width"), format_info.get("height")
    return f"{width}x{height}" if width and height else str(format_info.get("format_note") or "UNKNOWN")


def quality_verification(info: dict[str, Any]) -> dict[str, Any]:
    selected = select_best_video_format(info)
    support_formats = info.get("support_formats") or []
    advertised_heights = [
        item.get("new_description") or item.get("display_desc") or item.get("height")
        for item in support_formats if isinstance(item, dict)
    ]
    advertised_numeric = [item.get("height") for item in support_formats if isinstance(item, dict) and isinstance(item.get("height"), int)]
    actual_height = selected.get("height") if selected else None
    supported_height = max(advertised_numeric) if advertised_numeric else actual_height
    result = "PASS" if selected and (not advertised_numeric or actual_height >= supported_height) else "FAIL"
    return {
        "quality_verification": result,
        "highest_supported_resolution": max(advertised_heights, key=str) if advertised_heights else resolution_label(selected),
        "highest_actual_downloadable_resolution": resolution_label(selected),
        "selected_resolution": resolution_label(selected),
        "selected_fps": selected.get("fps") if selected else None,
        "selected_video_codec": selected.get("vcodec") if selected else None,
        "selected_audio_codec": next((item.get("acodec") for item in info.get("formats", []) if isinstance(item, dict) and item.get("acodec") not in (None, "none")), None),
        "selected_video_bitrate": selected.get("tbr") if selected else None,
        "selected_video_filesize": selected.get("filesize") or selected.get("filesize_approx") if selected else None,
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def ffprobe_streams(ffprobe: str, video_path: Path, log_path: Path) -> dict[str, Any]:
    result = run_command([ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(video_path)], log_path)
    details = json.loads(result.stdout)
    streams = details.get("streams", [])
    video = next((item for item in streams if item.get("codec_type") == "video"), {})
    audio = next((item for item in streams if item.get("codec_type") == "audio"), {})
    duration = float(details.get("format", {}).get("duration") or 0)
    if not video or not audio or duration <= 0:
        raise RuntimeError(f"ffprobe 完整性验证失败，详情见：{log_path}")
    return {"container": details.get("format", {}).get("format_name"), "duration_seconds": duration,
            "width": video.get("width"), "height": video.get("height"), "fps": video.get("r_frame_rate"),
            "video_codec": video.get("codec_name"), "audio_codec": audio.get("codec_name")}


def corpus_estimate(entries: list[dict[str, Any]]) -> int | None:
    sizes = [entry.get("estimated_bytes") for entry in entries]
    return sum(int(size) for size in sizes if isinstance(size, (int, float)) and size > 0) if any(sizes) else None


def run_workflow(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).expanduser().resolve()
    ensure_output_layout(output_dir)
    entries, reported_total, duplicates, complete = enumerate_source(args.yt_dlp, output_dir)
    if not complete:
        print("STATUS=ENUMERATION_INCOMPLETE_FAIL_CLOSED")
        return 2
    if not entries:
        print("STATUS=NO_PUBLIC_VIDEOS")
        return 2
    pilot = entries[0]
    pilot_info = yt_dlp_json(args.yt_dlp, pilot["original_url"], output_dir / "logs" / f"pilot-{pilot['bvid']}-formats.log")
    quality = quality_verification(pilot_info)
    (output_dir / "manifests" / "pilot_quality.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")
    if quality["quality_verification"] != "PASS":
        print("STATUS=QUALITY_VERIFICATION_FAIL")
        return 3
    estimate = corpus_estimate(entries)
    free_bytes = shutil.disk_usage(output_dir).free
    disk_report = {"estimated_bytes": estimate, "free_bytes": free_bytes, "safe": disk_capacity_safe(estimate, free_bytes)}
    (output_dir / "manifests" / "disk_capacity.json").write_text(json.dumps(disk_report, indent=2), encoding="utf-8")
    if not disk_report["safe"]:
        print("STATUS=DISK_CAPACITY_BLOCKED")
        return 4
    print(json.dumps({"STATUS": "READY_FOR_PILOT_AND_RESUMABLE_DOWNLOAD", "PILOT_BVID": pilot["bvid"],
                      "UPLOADER_REPORTED_TOTAL": reported_total, "ENUMERATED_UNIQUE_BVIDS": len(entries),
                      "DUPLICATES_REMOVED": duplicates, "CORPUS_ESTIMATED_SIZE": estimate,
                      "FREE_DISK_BEFORE": free_bytes}, ensure_ascii=False))
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yt-dlp", required=True, help="独立工具环境中的 yt-dlp 可执行文件")
    parser.add_argument("--output-dir", default=str(default_output_dir()))
    return parser.parse_args()


if __name__ == "__main__":
    try:
        raise SystemExit(run_workflow(parse_args()))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"STATUS=FAILED_FAIL_CLOSED\nREASON={redact_sensitive_text(str(error))}", file=sys.stderr)
        raise SystemExit(1)
