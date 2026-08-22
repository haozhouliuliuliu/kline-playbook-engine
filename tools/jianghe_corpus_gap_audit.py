"""江河 001--099 媒体与字幕的机械审计工具。

本工具只读取来源清单、检查本地文件、查询 Bilibili 字幕轨道，并保存原样字幕。
它不读取、更不解释任何交易内容。Cookie 只从调用方指定的仓库外临时文件读取，
不会写入日志或审计产物。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
import shutil
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from http.cookiejar import CookieJar, MozillaCookieJar
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import HTTPCookieProcessor, Request, build_opener

# 支持从仓库根目录及 ``python tools/...py`` 两种方式启动。
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.bilibili_corpus_acquisition import (
    HTTP_HEADERS,
    redact_sensitive_text,
    signed_wbi_query,
    wbi_mixin_key,
)


SOURCE_COUNT = 99
SUBTITLE_EXTENSIONS = {".srt", ".vtt", ".ass", ".json"}
KNOWN_BURNED_IN_ORDINALS = {48}
SECRET_PATTERN = re.compile(r"(?i)(sessdata|bili_jct|cookie|token|authorization|password)\s*[=:]\s*[^\s;,&]+")


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise RuntimeError(f"缺少清单文件：{path}")
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"清单第 {number} 行不是有效 JSON") from error
        if not isinstance(value, dict):
            raise RuntimeError(f"清单第 {number} 行不是对象")
        rows.append(value)
    return rows


def validate_sources(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bvids = [row.get("bvid") for row in rows]
    ordinals = [row.get("ordinal") for row in rows]
    if len(rows) != SOURCE_COUNT:
        raise RuntimeError(f"source manifest 条数为 {len(rows)}，预期 {SOURCE_COUNT}")
    if len(set(bvids)) != SOURCE_COUNT or any(not isinstance(item, str) or not item for item in bvids):
        raise RuntimeError("source manifest BVID 不唯一或为空")
    if set(ordinals) != set(range(1, SOURCE_COUNT + 1)):
        raise RuntimeError("source manifest ordinal 不是完整的 001--099")
    return sorted(rows, key=lambda row: int(row["ordinal"]))


def bvid_from_name(path: Path) -> str | None:
    match = re.search(r"(BV[0-9A-Za-z]+)", path.name)
    return match.group(1) if match else None


def local_file_index(directory: Path, extensions: set[str] | None = None) -> dict[str, list[Path]]:
    result: dict[str, list[Path]] = {}
    if not directory.is_dir():
        return result
    for path in directory.iterdir():
        if not path.is_file() or (extensions is not None and path.suffix.lower() not in extensions):
            continue
        bvid = bvid_from_name(path)
        if bvid:
            result.setdefault(bvid, []).append(path)
    return result


def ffprobe_media(ffprobe: str, path: Path) -> dict[str, Any]:
    command = [ffprobe, "-v", "error", "-show_entries", "format=duration", "-show_streams", "-of", "json", str(path)]
    try:
        completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    except OSError as error:
        return {"ffprobe_ok": False, "error": f"ffprobe 无法启动：{error}"}
    if completed.returncode != 0:
        return {"ffprobe_ok": False, "error": redact_sensitive_text(completed.stderr[-300:])}
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"ffprobe_ok": False, "error": "ffprobe 输出不是 JSON"}
    streams = payload.get("streams") if isinstance(payload.get("streams"), list) else []
    video = next((item for item in streams if isinstance(item, dict) and item.get("codec_type") == "video"), None)
    audio = next((item for item in streams if isinstance(item, dict) and item.get("codec_type") == "audio"), None)
    duration_raw = (payload.get("format") or {}).get("duration") if isinstance(payload.get("format"), dict) else None
    try:
        duration = float(duration_raw) if duration_raw is not None else None
    except (TypeError, ValueError):
        duration = None
    return {
        "ffprobe_ok": bool(video and audio and duration and duration > 0 and not completed.stderr.strip()),
        "video_stream": bool(video),
        "audio_stream": bool(audio),
        "duration": duration,
        "width": video.get("width") if video else None,
        "height": video.get("height") if video else None,
        "codec": video.get("codec_name") if video else None,
        "error": redact_sensitive_text(completed.stderr[-300:]) if completed.stderr.strip() else None,
    }


def download_binary(opener: Any, urls: list[str], output_path: Path, max_attempts: int = 6) -> None:
    """以有界断点续传下载单一 DASH 流；失败不能产生可替换成品。"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    expected_size: int | None = None
    last_error = ""
    for attempt in range(1, max_attempts + 1):
        url = urls[(attempt - 1) % len(urls)]
        existing_size = output_path.stat().st_size if output_path.exists() else 0
        headers = {**HTTP_HEADERS, "Range": f"bytes={existing_size}-"}
        try:
            with opener.open(Request(url, headers=headers), timeout=45) as response:
                content_range = response.headers.get("Content-Range") or ""
                match = re.search(r"/(\d+)$", content_range)
                if match:
                    expected_size = int(match.group(1))
                if response.status not in {200, 206}:
                    raise RuntimeError(f"DASH 返回 HTTP {response.status}")
                with output_path.open("ab" if existing_size else "wb") as handle:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
            current_size = output_path.stat().st_size
            if expected_size is not None and current_size == expected_size:
                return
            if expected_size is None and current_size > existing_size:
                return
            last_error = f"attempt={attempt}; downloaded={current_size}; expected={expected_size}"
        except Exception as error:
            current_size = output_path.stat().st_size if output_path.exists() else 0
            last_error = f"attempt={attempt}; downloaded={current_size}; error={redact_sensitive_text(str(error))}"
        if attempt < max_attempts:
            time.sleep(min(5 * attempt, 20))
    raise RuntimeError("DASH 断点续传未完成：" + last_error)


def best_dash_item(items: Any) -> dict[str, Any] | None:
    if not isinstance(items, list):
        return None
    candidates = [item for item in items if isinstance(item, dict) and (item.get("base_url") or item.get("baseUrl"))]
    return max(candidates, key=lambda item: (int(item.get("id") or 0), int(item.get("bandwidth") or 0)), default=None)


def stream_url(item: dict[str, Any]) -> str:
    value = str(item.get("base_url") or item.get("baseUrl") or "")
    if not value.startswith("https://"):
        raise RuntimeError("DASH 流没有安全的 HTTPS 地址")
    return value


def repair_media_from_dash(opener: Any, source: dict[str, Any], root: Path, ffprobe: str, cookie_path: Path) -> dict[str, Any]:
    """用已验证的 yt-dlp 路线无损下载最佳 DASH 流，再进行替换。"""
    bvid = str(source["bvid"])
    view = wbi_json(opener, "/x/web-interface/wbi/view", {"bvid": bvid})
    pages = (view.get("data") or {}).get("pages") or []
    if not pages or not isinstance(pages[0], dict) or not pages[0].get("cid"):
        raise RuntimeError("修复时来源未返回可用 CID")
    cid = int(pages[0]["cid"])
    repair_dir = root / "repair" / f"{int(source['ordinal']):03}__{bvid}"
    repair_dir.mkdir(parents=True, exist_ok=True)
    candidate = repair_dir / "candidate.mp4"
    if candidate.exists():
        raise RuntimeError("修复目录已有 candidate.mp4，拒绝覆盖")
    command = [
        sys.executable, "-m", "yt_dlp", "--cookies", str(cookie_path), "--format", "bestvideo*+bestaudio/best",
        "--merge-output-format", "mp4", "--no-warnings", "--no-continue", "--socket-timeout", "60",
        "--output", str(repair_dir / "candidate.%(ext)s"), str(source["original_url"]),
    ]
    download = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if download.returncode != 0:
        raise RuntimeError("yt-dlp 无损下载失败：" + redact_sensitive_text(download.stderr[-500:]))
    if not candidate.is_file():
        raise RuntimeError("yt-dlp 成功但未生成 candidate.mp4")
    probe = ffprobe_media(ffprobe, candidate)
    if not probe.get("ffprobe_ok"):
        raise RuntimeError("新媒体 ffprobe 未通过：" + str(probe.get("error") or "缺少音视频流"))
    current_media = local_file_index(root / "media").get(bvid, [])
    if len(current_media) != 1:
        raise RuntimeError("修复替换前本地媒体文件数量异常")
    old_path = current_media[0]
    quarantine = root / "quarantine"
    quarantine.mkdir(parents=True, exist_ok=True)
    quarantined = quarantine / f"{old_path.stem}.pre-repair{old_path.suffix}"
    if quarantined.exists():
        raise RuntimeError("隔离目录已存在同名旧文件，拒绝覆盖")
    shutil.move(str(old_path), str(quarantined))
    try:
        shutil.move(str(candidate), str(old_path))
    except Exception:
        shutil.move(str(quarantined), str(old_path))
        raise
    return {"bvid": bvid, "cid": cid, "final_media_path": str(old_path), "quarantine_path": str(quarantined), "ffprobe": probe}


def repair_media_direct_from_dash(opener: Any, source: dict[str, Any], root: Path, ffprobe: str) -> dict[str, Any]:
    """WBI 返回的最佳 DASH 视频和音频分开断点续传，再无损 mux。"""
    bvid = str(source["bvid"])
    view = wbi_json(opener, "/x/web-interface/wbi/view", {"bvid": bvid})
    pages = (view.get("data") or {}).get("pages") or []
    if not pages or not isinstance(pages[0], dict) or not pages[0].get("cid"):
        raise RuntimeError("直接修复时来源未返回可用 CID")
    cid = int(pages[0]["cid"])
    payload = wbi_json(opener, "/x/player/wbi/playurl", {"bvid": bvid, "cid": cid, "qn": 127, "fnver": 0, "fnval": 4048, "fourk": 1})
    dash = (payload.get("data") or {}).get("dash") or {}
    video, audio = best_dash_item(dash.get("video")), best_dash_item(dash.get("audio"))
    if not video or not audio:
        raise RuntimeError("当前登录态下来源未提供完整视频与音频 DASH 流")
    repair_dir = root / "repair" / f"{int(source['ordinal']):03}__{bvid}" / "direct_retry"
    video_path, audio_path, candidate = repair_dir / "source-video.m4s", repair_dir / "source-audio.m4s", repair_dir / "candidate.mp4"
    if candidate.exists():
        raise RuntimeError("直接修复目录已有 candidate.mp4，拒绝覆盖")
    video_urls = [stream_url(video)] + [str(item) for item in video.get("backup_url", video.get("backupUrl", [])) if str(item).startswith("https://")]
    audio_urls = [stream_url(audio)] + [str(item) for item in audio.get("backup_url", audio.get("backupUrl", [])) if str(item).startswith("https://")]
    download_binary(opener, video_urls, video_path)
    download_binary(opener, audio_urls, audio_path)
    mux = subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video_path), "-i", str(audio_path), "-c", "copy", "-movflags", "+faststart", str(candidate)], capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
    if mux.returncode != 0 or mux.stderr.strip():
        raise RuntimeError("直接 DASH 无损 mux 失败：" + redact_sensitive_text(mux.stderr[-300:]))
    probe = ffprobe_media(ffprobe, candidate)
    if not probe.get("ffprobe_ok"):
        raise RuntimeError("直接 DASH 新媒体 ffprobe 未通过：" + str(probe.get("error") or "缺少音视频流"))
    current_media = local_file_index(root / "media").get(bvid, [])
    if len(current_media) != 1:
        raise RuntimeError("直接修复替换前本地媒体文件数量异常")
    old_path = current_media[0]
    quarantine = root / "quarantine"
    quarantine.mkdir(parents=True, exist_ok=True)
    quarantined = quarantine / f"{old_path.stem}.pre-repair{old_path.suffix}"
    if quarantined.exists():
        raise RuntimeError("隔离目录已存在同名旧文件，拒绝覆盖")
    shutil.move(str(old_path), str(quarantined))
    try:
        shutil.move(str(candidate), str(old_path))
    except Exception:
        shutil.move(str(quarantined), str(old_path))
        raise
    return {"bvid": bvid, "cid": cid, "final_media_path": str(old_path), "quarantine_path": str(quarantined), "ffprobe": probe}


def load_cookie_opener(cookie_path: Path):
    if not cookie_path.is_file():
        raise RuntimeError("未找到指定的临时 Bilibili 会话文件")
    jar = MozillaCookieJar(str(cookie_path))
    jar.load(ignore_discard=True, ignore_expires=True)
    if not any(cookie.domain.lstrip(".").lower().endswith("bilibili.com") for cookie in jar):
        raise RuntimeError("临时会话文件不含 Bilibili 域 Cookie")
    return build_opener(HTTPCookieProcessor(jar))


def opener_json(opener: Any, url: str) -> dict[str, Any]:
    request = Request(url, headers=HTTP_HEADERS)
    with opener.open(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Bilibili 接口未返回对象")
    return payload


def wbi_json(opener: Any, endpoint: str, parameters: dict[str, Any]) -> dict[str, Any]:
    nav = opener_json(opener, "https://api.bilibili.com/x/web-interface/nav")
    image_data = ((nav.get("data") or {}).get("wbi_img") or {})
    mixin_key = wbi_mixin_key(str(image_data.get("img_url") or ""), str(image_data.get("sub_url") or ""))
    payload = opener_json(opener, "https://api.bilibili.com" + endpoint + "?" + signed_wbi_query(parameters, mixin_key))
    if payload.get("code") != 0:
        raise RuntimeError(f"Bilibili WBI 返回 code={payload.get('code')}")
    return payload


def subtitle_tracks(opener: Any, bvid: str) -> tuple[int, list[dict[str, Any]]]:
    view = wbi_json(opener, "/x/web-interface/wbi/view", {"bvid": bvid})
    pages = (view.get("data") or {}).get("pages") or []
    if not pages or not isinstance(pages[0], dict) or not pages[0].get("cid"):
        raise RuntimeError("来源未返回可用 CID")
    cid = int(pages[0]["cid"])
    payload = opener_json(opener, "https://api.bilibili.com/x/player/v2?" + urlencode({"bvid": bvid, "cid": cid}))
    if payload.get("code") != 0:
        raise RuntimeError(f"字幕接口返回 code={payload.get('code')}")
    tracks = (((payload.get("data") or {}).get("subtitle") or {}).get("subtitles") or [])
    if not isinstance(tracks, list):
        raise RuntimeError("字幕接口 tracks 格式异常")
    return cid, [item for item in tracks if isinstance(item, dict)]


def source_access_check(opener: Any, bvid: str) -> dict[str, Any]:
    """只验证当前会话是否能读取媒体清单，不下载媒体。"""
    try:
        view = wbi_json(opener, "/x/web-interface/wbi/view", {"bvid": bvid})
        pages = (view.get("data") or {}).get("pages") or []
        if not pages or not isinstance(pages[0], dict) or not pages[0].get("cid"):
            return {"bvid": bvid, "source_access": "UNAVAILABLE_OTHER", "reason": "CID_MISSING"}
        cid = int(pages[0]["cid"])
        playurl = wbi_json(opener, "/x/player/wbi/playurl", {
            "bvid": bvid, "cid": cid, "qn": 127, "fnver": 0, "fnval": 4048, "fourk": 1,
        })
        dash = (playurl.get("data") or {}).get("dash") or {}
        has_video = bool(dash.get("video")) if isinstance(dash, dict) else False
        has_audio = bool(dash.get("audio")) if isinstance(dash, dict) else False
        return {
            "bvid": bvid,
            "source_access": "ACCESSIBLE" if has_video and has_audio else "UNAVAILABLE_OTHER",
            "cid": cid,
            "video_stream": has_video,
            "audio_stream": has_audio,
        }
    except Exception as error:
        message = redact_sensitive_text(str(error))
        status = "PAID_GATED" if "87008" in message or "supporter" in message.lower() else "FETCH_FAILED"
        return {"bvid": bvid, "source_access": status, "reason": message[:500]}


def preferred_track(tracks: list[dict[str, Any]]) -> dict[str, Any] | None:
    preferred = ("zh-CN", "ai-zh", "zh", "zh-Hans")
    for language in preferred:
        for track in tracks:
            if track.get("lan") == language:
                return track
    return tracks[0] if tracks else None


def seconds_to_srt(value: float) -> str:
    milliseconds = max(0, round(value * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def bili_json_to_srt(payload: dict[str, Any]) -> str:
    body = payload.get("body")
    if not isinstance(body, list):
        raise RuntimeError("字幕 JSON 缺少 body")
    blocks: list[str] = []
    for number, item in enumerate(body, start=1):
        if not isinstance(item, dict):
            continue
        try:
            start, end = float(item["from"]), float(item["to"])
        except (KeyError, TypeError, ValueError):
            continue
        content = str(item.get("content") or "").strip()
        if end <= start or not content:
            continue
        blocks.append(f"{number}\n{seconds_to_srt(start)} --> {seconds_to_srt(end)}\n{content}")
    if not blocks:
        raise RuntimeError("字幕 JSON 没有可用时间轴")
    return "\n\n".join(blocks) + "\n"


def fetch_track_to_srt(opener: Any, track: dict[str, Any], output_path: Path) -> None:
    url = str(track.get("subtitle_url") or "")
    if url.startswith("//"):
        url = "https:" + url
    if not url.startswith("https://"):
        raise RuntimeError("字幕轨道没有安全的 HTTPS 地址")
    payload = opener_json(opener, url)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(bili_json_to_srt(payload), encoding="utf-8", newline="\n")


@dataclass
class RemoteResult:
    status: str
    track_count: int | None
    cid: int | None
    recovered_path: str | None
    error: str | None


def remote_subtitle_check(opener: Any, source: dict[str, Any], subtitles_dir: Path, download: bool) -> RemoteResult:
    try:
        cid, tracks = subtitle_tracks(opener, str(source["bvid"]))
        if not tracks:
            return RemoteResult("NONE_CONFIRMED", 0, cid, None, None)
        selected = preferred_track(tracks)
        recovered_path = None
        if download and selected:
            language = re.sub(r"[^0-9A-Za-z.-]+", "_", str(selected.get("lan") or "unknown"))
            output = subtitles_dir / f"{int(source['ordinal']):06}__{source['bvid']}.remote-{language}.srt"
            fetch_track_to_srt(opener, selected, output)
            recovered_path = str(output)
        return RemoteResult("AVAILABLE", len(tracks), cid, recovered_path, None)
    except Exception as error:  # 网络或门控异常必须保留为失败，不能伪装成无字幕。
        message = redact_sensitive_text(str(error))
        lowered = message.lower()
        status = "PAID_GATED" if any(marker in lowered for marker in ("87008", "supporter", "充电", "付费")) else "FETCH_FAILED"
        return RemoteResult(status, None, None, None, message[:500])


def semantic_status_for(ordinal: int) -> str:
    if ordinal in {65, 99}:
        return "PENDING_SOL_REVIEW"
    if ordinal == 48:
        return "PARTIAL_BURNED_IN_ONLY_PREVIOUS_REVIEW"
    return "EXISTING_OR_NOT_APPLICABLE"


def audit(args: argparse.Namespace) -> list[dict[str, Any]]:
    root = Path(args.corpus_root).resolve()
    manifests = root / "manifests"
    subtitles_dir = root / "subtitles"
    sources = validate_sources(read_jsonl(manifests / "source_manifest.jsonl"))
    media_index = local_file_index(root / "media")
    subtitle_index = local_file_index(subtitles_dir, SUBTITLE_EXTENSIONS)
    corpus_rows = {str(row.get("bvid")): row for row in read_jsonl(manifests / "corpus_manifest.jsonl")}
    prior_path = manifests / "final_corpus_gap_audit.jsonl"
    prior_rows = {str(row.get("bvid")): row for row in read_jsonl(prior_path)} if prior_path.is_file() else {}
    remote_candidates = {str(source["bvid"]) for source in sources if not subtitle_index.get(str(source["bvid"]))}
    opener = load_cookie_opener(Path(args.auth_cookie).resolve()) if args.remote_check else None
    records: list[dict[str, Any]] = []
    for source in sources:
        bvid = str(source["bvid"])
        ordinal = int(source["ordinal"])
        media_files = media_index.get(bvid, [])
        subtitle_files = subtitle_index.get(bvid, [])
        corpus = corpus_rows.get(bvid, {})
        if len(media_files) > 1:
            raise RuntimeError(f"BVID {bvid} 有多个本地媒体文件，拒绝猜测")
        media_path = media_files[0] if media_files else None
        probe = ffprobe_media(args.ffprobe, media_path) if media_path else {}
        if media_path is None:
            media_status = "SOURCE_PAID_GATED" if "supporter-only" in str(corpus.get("failure_reason", "")).lower() else "MEDIA_MISSING"
        elif probe.get("ffprobe_ok"):
            media_status = "MEDIA_OK"
        else:
            media_status = "MEDIA_CORRUPT"
        remote = RemoteResult("NOT_REQUIRED", None, None, None, None)
        if bvid in remote_candidates and opener is not None:
            remote = remote_subtitle_check(opener, source, subtitles_dir, args.download_remote_subtitles)
        elif bvid in remote_candidates and prior_rows.get(bvid):
            prior = prior_rows[bvid]
            remote = RemoteResult(
                str(prior.get("remote_subtitle_status") or "NOT_REQUIRED"),
                prior.get("remote_subtitle_track_count"), prior.get("remote_cid"), None, prior.get("remote_error"),
            )
        elif prior_rows.get(bvid) and str(prior_rows[bvid].get("remote_subtitle_status") or "").startswith("AVAILABLE"):
            prior = prior_rows[bvid]
            remote = RemoteResult(str(prior["remote_subtitle_status"]), prior.get("remote_subtitle_track_count"), prior.get("remote_cid"), None, None)
        elif any(".remote-" in path.name for path in subtitle_files):
            remote = RemoteResult("AVAILABLE_RECOVERED", 1, None, None, None)
        local_status = "LOCAL_PRESENT" if subtitle_files else "LOCAL_MISSING"
        if subtitle_files:
            final_subtitle_status = "NATIVE_SUBTITLE_VERIFIED_LOCAL"
            needs_asr = False
        elif media_status == "SOURCE_PAID_GATED" or remote.status == "PAID_GATED":
            final_subtitle_status = "SOURCE_UNAVAILABLE_PAID_GATED"
            needs_asr = False
        elif remote.status == "AVAILABLE":
            final_subtitle_status = "NATIVE_SUBTITLE_AVAILABLE_REMOTE_LOCAL_MISSING" if not remote.recovered_path else "NATIVE_SUBTITLE_VERIFIED_LOCAL"
            needs_asr = False
        elif remote.status == "NONE_CONFIRMED":
            final_subtitle_status = "BURNED_IN_ONLY_VERIFIED" if ordinal in KNOWN_BURNED_IN_ORDINALS else "NO_NATIVE_SUBTITLE_CONFIRMED_NEEDS_ASR"
            needs_asr = media_status == "MEDIA_OK"
        elif remote.status == "FETCH_FAILED":
            final_subtitle_status = "SUBTITLE_FETCH_FAILED_RETRYABLE"
            needs_asr = False
        elif not subtitle_files:
            final_subtitle_status = "SUBTITLE_FETCH_FAILED_RETRYABLE"
            needs_asr = False
        else:
            raise RuntimeError(f"BVID {bvid} 无法归类")
        record = {
            "source_ordinal": ordinal,
            "bvid": bvid,
            "title": source.get("title"),
            "source_url": source.get("original_url"),
            "upload_date": source.get("upload_date"),
            "media_status": media_status,
            "media_path": str(media_path) if media_path else None,
            "file_size": media_path.stat().st_size if media_path else None,
            "ffprobe_ok": probe.get("ffprobe_ok", False) if media_path else False,
            "video_stream": probe.get("video_stream", False) if media_path else False,
            "audio_stream": probe.get("audio_stream", False) if media_path else False,
            "duration": probe.get("duration") if media_path else None,
            "width": probe.get("width") if media_path else None,
            "height": probe.get("height") if media_path else None,
            "codec": probe.get("codec") if media_path else None,
            "local_subtitle_files": [str(path) for path in subtitle_files] + ([remote.recovered_path] if remote.recovered_path else []),
            "local_subtitle_status": local_status,
            "remote_subtitle_status": remote.status,
            "remote_subtitle_track_count": remote.track_count,
            "remote_cid": remote.cid,
            "remote_error": remote.error,
            "final_subtitle_status": final_subtitle_status,
            "needs_asr": needs_asr,
            "semantic_status": semantic_status_for(ordinal),
            "source_access_status": prior_rows.get(bvid, {}).get("source_access_status"),
            "source_access_reason": prior_rows.get(bvid, {}).get("source_access_reason"),
            "audited_at": utc_now(),
        }
        records.append(record)
    return records


def write_audit(root: Path, records: list[dict[str, Any]]) -> None:
    output_base = root / "manifests" / "final_corpus_gap_audit"
    output_base.with_suffix(".jsonl").write_text(
        "".join(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in records), encoding="utf-8", newline="\n"
    )
    fields = list(dict.fromkeys(field for record in records for field in record))
    with output_base.with_suffix(".csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            row = record.copy()
            row["local_subtitle_files"] = json.dumps(row["local_subtitle_files"], ensure_ascii=False)
            writer.writerow(row)


def write_sol_review_package(record: dict[str, Any], root: Path) -> Path:
    ordinal = int(record["source_ordinal"])
    bvid = str(record["bvid"])
    package = root / "sol_review_packages" / f"{ordinal:03}__{bvid}"
    package.mkdir(parents=True, exist_ok=True)
    subtitle_paths = record.get("local_subtitle_files") or []
    manifest = {
        "source_ordinal": ordinal, "bvid": bvid, "title": record.get("title"), "source_url": record.get("source_url"),
        "media_status": record.get("media_status"), "final_subtitle_status": record.get("final_subtitle_status"),
        "subtitle_paths": subtitle_paths,
    }
    (package / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (package / "original_video_path.txt").write_text(str(record.get("media_path") or "MEDIA_UNAVAILABLE") + "\n", encoding="utf-8")
    (package / "subtitle_or_asr_path.txt").write_text("\n".join(str(path) for path in subtitle_paths) + "\n", encoding="utf-8")
    (package / "low_confidence_segments.csv").write_text("start,end,avg_logprob,no_speech_prob\n", encoding="utf-8")
    (package / "exact_range_requests_template.csv").write_text("candidate_start,candidate_end,requested_sol_action,status\n00:00:00,00:00:10,VERIFY_AUDIO_AND_SAME_TIME_VISUAL,PENDING\n", encoding="utf-8")
    (package / "README.txt").write_text("工程证据包：包含原视频路径、字幕路径和精确时间范围复核模板。\n不包含交易策略、摘要或语义解释。\n", encoding="utf-8")
    return package


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", default=r"D:\江河交易员")
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--remote-check", action="store_true", help="仅对本地缺字幕 BVID 远端复核")
    parser.add_argument("--auth-cookie", help="仓库外的临时 Bilibili 会话文件；仅 --remote-check 时必填")
    parser.add_argument("--download-remote-subtitles", action="store_true", help="原样下载远端可用字幕")
    parser.add_argument("--source-access-bvid", action="append", default=[], help="仅验证指定 BVID 当前媒体访问状态")
    parser.add_argument("--repair-bvid", help="从当前登录态无损修复一个已确认损坏的本地媒体")
    parser.add_argument("--repair-direct-bvid", help="使用 WBI/DASH 断点续传无损修复一个媒体")
    parser.add_argument("--create-sol-package-ordinal", type=int, action="append", default=[], help="为指定来源生成 Sol 工程证据包")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if (args.remote_check or args.source_access_bvid or args.repair_bvid or args.repair_direct_bvid) and not args.auth_cookie:
        raise RuntimeError("远端复核必须通过 --auth-cookie 显式提供仓库外临时会话文件")
    if args.download_remote_subtitles and not args.remote_check:
        raise RuntimeError("下载远端字幕必须同时启用 --remote-check")
    sources = validate_sources(read_jsonl(Path(args.corpus_root).resolve() / "manifests" / "source_manifest.jsonl"))
    repair_result = None
    repair_bvid = args.repair_bvid or args.repair_direct_bvid
    if repair_bvid:
        selected = [source for source in sources if source["bvid"] == repair_bvid]
        if len(selected) != 1:
            raise RuntimeError("修复 BVID 不在唯一 source manifest 中")
        cookie_path = Path(args.auth_cookie).resolve()
        opener = load_cookie_opener(cookie_path)
        repair_result = repair_media_direct_from_dash(opener, selected[0], Path(args.corpus_root).resolve(), args.ffprobe) if args.repair_direct_bvid else repair_media_from_dash(opener, selected[0], Path(args.corpus_root).resolve(), args.ffprobe, cookie_path)
    records = audit(args)
    access_results: list[dict[str, Any]] = []
    if args.source_access_bvid:
        opener = load_cookie_opener(Path(args.auth_cookie).resolve())
        access_results = [source_access_check(opener, bvid) for bvid in args.source_access_bvid]
        by_bvid = {str(item["bvid"]): item for item in access_results}
        for record in records:
            access = by_bvid.get(str(record["bvid"]))
            if access:
                record["source_access_status"] = access.get("source_access")
                record["source_access_reason"] = access.get("reason")
    write_audit(Path(args.corpus_root).resolve(), records)
    packages = []
    if args.create_sol_package_ordinal:
        selected_ordinals = set(args.create_sol_package_ordinal)
        packages = [str(write_sol_review_package(record, Path(args.corpus_root).resolve())) for record in records if int(record["source_ordinal"]) in selected_ordinals]
        if len(packages) != len(selected_ordinals):
            raise RuntimeError("存在不在 source manifest 中的 Sol package ordinal")
    print(json.dumps({"STATUS": "PASS", "SOURCE_COUNT": len(records), "source_access": access_results, "repair": repair_result, "packages": packages}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print("STATUS=FAILED_FAIL_CLOSED", file=sys.stderr)
        print("REASON=" + redact_sensitive_text(SECRET_PATTERN.sub("[REDACTED]", str(error))), file=sys.stderr)
        raise SystemExit(1)
