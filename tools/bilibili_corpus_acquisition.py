"""可恢复地获取 Bilibili UP 主公开视频语料。

本工具只保存视频、字幕、元数据和完整性证据；不读取或解释交易内容。登录使用
Bilibili 网页二维码流程，绝不读取 Chrome 数据，也不输出或提交 Cookie。
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from http.cookiejar import CookieJar, MozillaCookieJar
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPCookieProcessor, Request, build_opener, urlopen


UP_UID = "3546770449631285"
UP_URL = f"https://space.bilibili.com/{UP_UID}/video"
PILOT_BVID = "BV1yxebzoERD"
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
                  "(KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36 Edg/147.0.0.0",
    "Referer": "https://www.bilibili.com/",
}


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_output_dir() -> Path:
    user_profile = Path(os.environ.get("USERPROFILE", Path.home()))
    return user_profile / "Videos" / "kline-playbook-engine" / "bilibili" / UP_UID


def default_auth_dir() -> Path:
    local_app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    return local_app_data / "kline-playbook-engine" / "bilibili-auth"


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


def is_bilibili_cookie_domain(domain: str) -> bool:
    return domain.lstrip(".").lower().endswith("bilibili.com")


def is_bilibili_hostname(hostname: str | None) -> bool:
    return bool(hostname) and (hostname.lower() == "bilibili.com" or hostname.lower().endswith(".bilibili.com"))


def qr_status_name(code: int | None) -> str:
    return {
        86101: "WAITING_FOR_SCAN",
        86090: "WAITING_FOR_CONFIRMATION",
        86038: "EXPIRED",
        0: "SUCCESS",
    }.get(code, "UNEXPECTED")


def qr_poll_status_code(payload: dict[str, Any]) -> int:
    if payload.get("code") != 0:
        raise RuntimeError(f"二维码轮询接口返回外层 code={payload.get('code')}")
    code = (payload.get("data") or {}).get("code")
    if not isinstance(code, int):
        raise RuntimeError("二维码轮询接口未返回 data.code")
    return code


def media_backoff_seconds(attempt: int) -> int:
    """媒体请求第一次至少等待十分钟，之后指数退避，最高一小时。"""
    return min(600 * (2 ** max(0, attempt - 1)), 3600)


def auth_status_path(auth_dir: Path) -> Path:
    return auth_dir / "session_status.json"


def write_auth_status(auth_dir: Path, state: str, **extra: Any) -> None:
    auth_dir.mkdir(parents=True, exist_ok=True)
    record = {"state": state, "updated_at": utc_now(), **extra}
    auth_status_path(auth_dir).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")


def assert_preserved_source_manifest(output_dir: Path, expected_count: int = 99) -> None:
    manifest = output_dir / "manifests" / "source_manifest.jsonl"
    if not manifest.is_file():
        raise RuntimeError("既有 source_manifest.jsonl 缺失，拒绝继续")
    with manifest.open(encoding="utf-8") as handle:
        rows = sum(1 for line in handle if line.strip())
    if rows != expected_count:
        raise RuntimeError(f"既有 source_manifest 数量为 {rows}，预期为 {expected_count}，拒绝继续")


def remove_temporary_cookie_file(cookie_path: Path) -> None:
    try:
        cookie_path.unlink()
    except FileNotFoundError:
        pass


def save_bilibili_cookies(cookie_jar: CookieJar, cookie_path: Path) -> int:
    """仅保存 Bilibili 域 Cookie，供下一步 yt-dlp 临时读取；不记录其值。"""
    filtered = MozillaCookieJar(str(cookie_path))
    source_jar = getattr(cookie_jar, "jar", cookie_jar)
    for cookie in source_jar:
        if is_bilibili_cookie_domain(cookie.domain):
            retained = copy.copy(cookie)
            retained.discard = False
            filtered.set_cookie(retained)
    if not list(filtered):
        raise RuntimeError("二维码登录未产生可用的 Bilibili 域会话 Cookie")
    cookie_path.parent.mkdir(parents=True, exist_ok=True)
    filtered.save(ignore_discard=True, ignore_expires=True)
    return len(list(filtered))


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
    # Chrome 路线已在当前环境停用；匿名元数据失败时由 WBI 备用枚举失败闭合。
    command = [yt_dlp, "--skip-download", "--dump-single-json", "--no-warnings"]
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


def opener_json(opener: Any, url: str) -> dict[str, Any]:
    request = Request(url, headers=HTTP_HEADERS)
    with opener.open(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def show_qr_code(login_url: str, png_path: Path) -> None:
    """将 Bilibili 返回的登录 URL 制成二维码并在本机显示。"""
    parsed = urlparse(login_url)
    if parsed.scheme != "https" or not is_bilibili_hostname(parsed.hostname):
        raise RuntimeError("二维码登录地址不是预期的 Bilibili HTTPS 地址")
    try:
        import qrcode
    except ImportError as error:
        raise RuntimeError("缺少二维码生成依赖，请在独立工具环境安装 qrcode[pil]") from error
    png_path.parent.mkdir(parents=True, exist_ok=True)
    qrcode.make(login_url).save(png_path)
    os.startfile(str(png_path))  # type: ignore[attr-defined]  # Windows only


def follow_bilibili_login_redirect(opener: Any, redirect_url: str) -> None:
    """消费二维码成功响应中的 Bilibili 登录跳转，以便 CookieJar 接收会话。"""
    parsed = urlparse(redirect_url)
    if not parsed.scheme and not parsed.netloc:
        return
    if parsed.scheme != "https" or not is_bilibili_hostname(parsed.hostname):
        raise RuntimeError(
            "二维码登录回调地址不是预期的 Bilibili HTTPS 地址"
            f"（scheme={parsed.scheme or 'NONE'}; hostname={parsed.hostname or 'NONE'}）"
        )
    request = Request(redirect_url, headers=HTTP_HEADERS)
    with opener.open(request, timeout=30):
        pass


def session_json(session: Any, url: str) -> dict[str, Any]:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def create_bilibili_web_session() -> Any:
    """复用 Bili23 v2.11.0 的最小网页会话初始化，不包含其 GUI 或下载器。"""
    try:
        import httpx
    except ImportError as error:
        raise RuntimeError("缺少独立工具环境依赖 httpx") from error
    session = httpx.Client(follow_redirects=True, timeout=30, headers=HTTP_HEADERS)
    fingerprint = session_json(session, "https://api.bilibili.com/x/frontend/finger/spi")
    data = fingerprint.get("data") or {}
    buvid3, buvid4 = data.get("b_3"), data.get("b_4")
    if not isinstance(buvid3, str) or not isinstance(buvid4, str):
        session.close()
        raise RuntimeError("Bilibili 指纹初始化未返回 buvid3/buvid4")
    for name, value in {
        "buvid3": buvid3,
        "buvid4": buvid4,
        "CURRENT_FNVAL": "4048",
        "CURRENT_QUALITY": "0",
    }.items():
        session.cookies.set(name, value, domain=".bilibili.com", path="/")
    return session


def load_bilibili_auth_session(cookie_path: Path) -> Any:
    """从临时 Netscape 文件恢复当前 Bilibili 会话；不读取或输出 Cookie 值。"""
    if not cookie_path.is_file():
        raise RuntimeError("临时 Bilibili 会话文件不存在")
    try:
        import httpx
    except ImportError as error:
        raise RuntimeError("缺少独立工具环境依赖 httpx") from error
    stored = MozillaCookieJar(str(cookie_path))
    stored.load(ignore_discard=True, ignore_expires=True)
    session = httpx.Client(follow_redirects=True, timeout=30, headers=HTTP_HEADERS)
    count = 0
    for cookie in stored:
        if is_bilibili_cookie_domain(cookie.domain):
            session.cookies.set(cookie.name, cookie.value, domain=cookie.domain, path=cookie.path)
            count += 1
    if not count:
        session.close()
        raise RuntimeError("临时会话文件不含 Bilibili 域 Cookie")
    return session


def wbi_json(session: Any, endpoint: str, parameters: dict[str, Any]) -> dict[str, Any]:
    nav = session_json(session, "https://api.bilibili.com/x/web-interface/nav")
    wbi_img = nav.get("data", {}).get("wbi_img", {})
    mixin_key = wbi_mixin_key(wbi_img.get("img_url", ""), wbi_img.get("sub_url", ""))
    payload = session_json(session, f"https://api.bilibili.com{endpoint}?{signed_wbi_query(parameters, mixin_key)}")
    if payload.get("code") != 0:
        raise RuntimeError(f"Bilibili WBI 媒体接口返回 code={payload.get('code')}")
    return payload


def highest_dash_video(dash: dict[str, Any]) -> dict[str, Any] | None:
    videos = [entry for entry in dash.get("video", []) if isinstance(entry, dict)]
    if not videos:
        return None
    return max(videos, key=lambda entry: (entry.get("id") or 0, entry.get("bandwidth") or 0))


def verify_pilot_wbi_quality(cookie_path: Path, bvid: str = PILOT_BVID) -> dict[str, Any]:
    """以已验证会话读取 support_formats 与 DASH 清单；不下载媒体。"""
    session = load_bilibili_auth_session(cookie_path)
    try:
        view = wbi_json(session, "/x/web-interface/wbi/view", {"bvid": bvid})
        pages = view.get("data", {}).get("pages") or []
        if not pages or not isinstance(pages[0], dict) or not pages[0].get("cid"):
            raise RuntimeError("pilot 视频未返回可用 CID")
        playurl = wbi_json(session, "/x/player/wbi/playurl", {
            "bvid": bvid, "cid": pages[0]["cid"], "qn": 127, "fnver": 0, "fnval": 4048, "fourk": 1,
        })
        data = playurl.get("data") or {}
        support_formats = [item for item in data.get("support_formats", []) if isinstance(item, dict)]
        dash = data.get("dash") or {}
        actual_video = highest_dash_video(dash)
        audio_streams = [entry for entry in dash.get("audio", []) if isinstance(entry, dict)]
        supported = max(support_formats, key=lambda entry: entry.get("quality") or 0, default=None)
        supported_id = supported.get("quality") if supported else None
        actual_id = actual_video.get("id") if actual_video else None
        passed = bool(actual_video and audio_streams)
        return {
            "bvid": bvid,
            "cid": pages[0]["cid"],
            "highest_supported_resolution": (supported or {}).get("new_description") or (supported or {}).get("display_desc") or "UNKNOWN",
            "highest_downloadable_resolution": resolution_label(actual_video),
            "highest_supported_quality_id": supported_id,
            "highest_downloadable_quality_id": actual_id,
            "fps": (actual_video or {}).get("frame_rate") or (actual_video or {}).get("frame_rate"),
            "video_codec": (actual_video or {}).get("codecs"),
            "audio_codec": audio_streams[0].get("codecs") if audio_streams else None,
            "quality_verification": "PASS" if passed else "FAIL",
            "quality_policy": "SOURCE_BEST_PLUS_VISUAL_ADEQUACY",
        }
    finally:
        session.close()


def follow_bilibili_session_redirect(session: Any, redirect_url: str) -> None:
    parsed = urlparse(redirect_url)
    if not parsed.scheme and not parsed.netloc:
        return
    if parsed.scheme != "https" or not is_bilibili_hostname(parsed.hostname):
        raise RuntimeError("二维码登录回调地址不是预期的 Bilibili HTTPS 地址")
    response = session.get(redirect_url, timeout=30)
    response.raise_for_status()


def run_qr_login(auth_dir: Path, output_dir: Path) -> int:
    """运行 Bilibili 网页二维码登录；只在本机临时保留 Bilibili 域 Cookie。"""
    assert_preserved_source_manifest(output_dir)
    session = create_bilibili_web_session()
    cookie_path = auth_dir / "bilibili-session.cookies.txt"
    remove_temporary_cookie_file(cookie_path)
    write_auth_status(auth_dir, "QR_GENERATING")
    while True:
        generated = session_json(session, "https://passport.bilibili.com/x/passport-login/web/qrcode/generate?" + urlencode({
            "source": "main-fe-header",
            "go_url": "https://www.bilibili.com/",
            "web_location": "333.1007",
        }))
        if generated.get("code") != 0:
            raise RuntimeError(f"二维码生成接口返回 code={generated.get('code')}")
        data = generated.get("data") or {}
        login_url, qrcode_key = data.get("url"), data.get("qrcode_key")
        if not isinstance(login_url, str) or not isinstance(qrcode_key, str) or not qrcode_key:
            raise RuntimeError("二维码生成接口未返回完整登录参数")
        show_qr_code(login_url, auth_dir / "bilibili-login-qr.png")
        write_auth_status(auth_dir, "QR_READY")
        while True:
            time.sleep(3)
            poll_url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll?" + urlencode({"qrcode_key": qrcode_key})
            polled = session_json(session, poll_url)
            code = qr_poll_status_code(polled)
            state = qr_status_name(code)
            if state == "WAITING_FOR_SCAN":
                write_auth_status(auth_dir, state)
                continue
            if state == "WAITING_FOR_CONFIRMATION":
                write_auth_status(auth_dir, state)
                continue
            if state == "EXPIRED":
                write_auth_status(auth_dir, "QR_EXPIRED_REGENERATING")
                break
            if state != "SUCCESS":
                raise RuntimeError(f"二维码轮询接口返回未预期 code={code}")
            nav = session_json(session, "https://api.bilibili.com/x/web-interface/nav")
            is_logged_in = bool(nav.get("data", {}).get("isLogin"))
            if not is_logged_in:
                write_auth_status(auth_dir, "LOGIN_VERIFICATION_FAILED")
                return 2
            save_bilibili_cookies(session.cookies.jar, cookie_path)
            write_auth_status(auth_dir, "ACCOUNT_LOGIN_VERIFIED", qr_login="PASS", account_login_verified="YES")
            print("QR_LOGIN=PASS\nACCOUNT_LOGIN_VERIFIED=YES")
            return 0


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
    result = "PASS" if selected else "FAIL"
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


def conservative_corpus_estimate(entries: list[dict[str, Any]]) -> int | None:
    """优先使用已知大小；否则按 10 Mbps 与已枚举总时长保守估算。"""
    known_size = corpus_estimate(entries)
    if known_size is not None:
        return known_size
    durations = [entry.get("duration_seconds") for entry in entries]
    total_seconds = sum(float(value) for value in durations if isinstance(value, (int, float)) and value > 0)
    return int(total_seconds * 10_000_000 / 8) if total_seconds else None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        if isinstance(item, dict):
            records.append(item)
    return records


def download_output_template(entry: dict[str, Any]) -> str:
    ordinal = int(entry.get("ordinal") or 0)
    upload_date = sanitize_windows_filename(str(entry.get("upload_date") or "UNKNOWN"))
    bvid = sanitize_windows_filename(str(entry["bvid"]))
    title = sanitize_windows_filename(str(entry.get("title") or "untitled"))
    return f"{ordinal:06d}__{upload_date}__{bvid}__{title}.%(ext)s"


def find_downloaded_video(media_dir: Path, bvid: str) -> Path | None:
    candidates = [
        path for path in media_dir.glob(f"*__{bvid}__*.*")
        if path.is_file() and path.suffix.lower() in {".mp4", ".mkv", ".webm"}
    ]
    return max(candidates, key=lambda path: path.stat().st_size, default=None)


def find_sidecar(directory: Path, bvid: str, suffix: str) -> Path | None:
    candidates = [path for path in directory.glob(f"*{bvid}*{suffix}") if path.is_file()]
    return max(candidates, key=lambda path: path.stat().st_mtime, default=None)


def build_download_command(yt_dlp: str, cookie_path: Path, output_dir: Path, entry: dict[str, Any]) -> list[str]:
    return [
        yt_dlp, "--cookies", str(cookie_path), "--continue", "--no-overwrites",
        "--format", "bestvideo*+bestaudio/best", "--merge-output-format", "mp4",
        "--write-info-json", "--write-subs", "--write-auto-subs",
        "--sub-langs", "zh.*,zh-Hans,zh-CN,ai-zh", "--windows-filenames",
        "--retries", "1", "--fragment-retries", "1", "--sleep-requests", "2", "--socket-timeout", "30",
        "--paths", f"home={output_dir / 'media'}",
        "--paths", f"subtitle={output_dir / 'subtitles'}",
        "--paths", f"infojson={output_dir / 'metadata'}",
        "--output", download_output_template(entry), str(entry["original_url"]),
    ]


def manifest_record_for_video(entry: dict[str, Any], video_path: Path, metadata_path: Path | None,
                              subtitle_path: Path | None, ffprobe: str, output_dir: Path) -> dict[str, Any]:
    probe = ffprobe_streams(ffprobe, video_path, output_dir / "logs" / f"ffprobe-{entry['bvid']}.log")
    return {
        "ordinal": entry["ordinal"], "bvid": entry["bvid"], "local_video_path": str(video_path),
        "metadata_path": str(metadata_path) if metadata_path else None,
        "subtitle_path": str(subtitle_path) if subtitle_path else None,
        "video_sha256": sha256_file(video_path), "container": probe["container"],
        "width": probe["width"], "height": probe["height"], "fps": probe["fps"],
        "video_codec": probe["video_codec"], "audio_codec": probe["audio_codec"],
        "duration_seconds": probe["duration_seconds"],
        "quality_policy": "SOURCE_BEST_PLUS_VISUAL_ADEQUACY", "quality_verification": "PASS",
        "download_status": "COMPLETE", "failure_reason": None, "downloaded_at": utc_now(),
    }


def manifest_fields() -> list[str]:
    return [
        "ordinal", "bvid", "local_video_path", "metadata_path", "subtitle_path", "video_sha256",
        "container", "width", "height", "fps", "video_codec", "audio_codec", "duration_seconds",
        "quality_policy", "quality_verification", "download_status", "failure_reason", "downloaded_at",
    ]


def write_download_progress(output_dir: Path, records: list[dict[str, Any]], total: int, state: str) -> None:
    records.sort(key=lambda item: int(item.get("ordinal") or 0))
    write_jsonl_csv(output_dir / "manifests" / "corpus_manifest", records, manifest_fields())
    completed = [item for item in records if item.get("download_status") in {"COMPLETE", "PILOT_COMPLETE"}]
    failed = [item for item in records if item.get("download_status") == "FAILED"]
    queue = [
        {
            "ordinal": item.get("ordinal"), "bvid": item.get("bvid"),
            "local_video_path": item.get("local_video_path"), "subtitle_path": item.get("subtitle_path"),
            "status": item.get("download_status"),
        }
        for item in records
    ]
    write_jsonl_csv(output_dir / "analysis_queue", queue, ["ordinal", "bvid", "local_video_path", "subtitle_path", "status"])
    progress = {
        "state": state, "updated_at": utc_now(), "total": total, "downloaded": len(completed),
        "failed": len(failed), "remaining": total - len(completed) - len(failed),
    }
    (output_dir / "manifests" / "download_progress.json").write_text(
        json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def record_by_bvid(records: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(record["bvid"]): record for record in records if record.get("bvid")}


def is_verified_record(record: dict[str, Any] | None) -> bool:
    if not record or record.get("download_status") not in {"COMPLETE", "PILOT_COMPLETE"}:
        return False
    video_path = Path(str(record.get("local_video_path") or ""))
    expected_hash = record.get("video_sha256")
    return video_path.is_file() and isinstance(expected_hash, str) and sha256_file(video_path) == expected_hash


def is_http_412(value: str) -> bool:
    return "412" in value and ("HTTP" in value.upper() or "PRECONDITION" in value.upper())


def run_download_all(args: argparse.Namespace) -> int:
    output_dir = Path(args.output_dir).expanduser().resolve()
    ensure_output_layout(output_dir)
    assert_preserved_source_manifest(output_dir)
    entries = read_jsonl(output_dir / "manifests" / "source_manifest.jsonl")
    unique_bvids = {str(entry.get("bvid")) for entry in entries if entry.get("bvid")}
    if len(entries) != 99 or len(unique_bvids) != 99:
        raise RuntimeError("source_manifest 未保持 99 个唯一 BVID，拒绝下载")
    estimate = conservative_corpus_estimate(entries)
    free_bytes = shutil.disk_usage(output_dir).free
    if not disk_capacity_safe(estimate, free_bytes):
        (output_dir / "manifests" / "disk_capacity.json").write_text(json.dumps({
            "estimated_bytes": estimate, "free_bytes": free_bytes, "safe": False,
        }, indent=2), encoding="utf-8")
        print("STATUS=DISK_CAPACITY_BLOCKED")
        return 4
    cookie_path = Path(args.auth_dir).expanduser().resolve() / "bilibili-session.cookies.txt"
    if not cookie_path.is_file():
        raise RuntimeError("没有有效的临时二维码登录会话；请先运行 --qr-login")
    records = read_jsonl(output_dir / "manifests" / "corpus_manifest.jsonl")
    known = record_by_bvid(records)
    for entry in entries:
        current = known.get(str(entry["bvid"]))
        if not current:
            current = {"ordinal": entry["ordinal"], "bvid": entry["bvid"], "download_status": "PENDING"}
            records.append(current)
            known[str(entry["bvid"])] = current
    write_download_progress(output_dir, records, len(entries), "RUNNING")
    try:
        for entry in entries:
            bvid = str(entry["bvid"])
            current = known[bvid]
            if is_verified_record(current):
                continue
            log_path = output_dir / "logs" / f"download-{bvid}.log"
            last_error = ""
            for attempt in range(1, 4):
                result = run_command(build_download_command(args.yt_dlp, cookie_path, output_dir, entry), log_path, check=False)
                if result.returncode == 0:
                    video_path = find_downloaded_video(output_dir / "media", bvid)
                    if video_path:
                        metadata_path = find_sidecar(output_dir / "metadata", bvid, ".info.json")
                        subtitle_path = find_sidecar(output_dir / "subtitles", bvid, ".srt")
                        current.clear()
                        current.update(manifest_record_for_video(entry, video_path, metadata_path, subtitle_path, args.ffprobe, output_dir))
                        write_download_progress(output_dir, records, len(entries), "RUNNING")
                        break
                    last_error = "yt-dlp 成功但未找到媒体文件"
                else:
                    last_error = redact_sensitive_text(result.stdout + "\n" + result.stderr)[-500:]
                if attempt < 3:
                    delay = media_backoff_seconds(attempt) if is_http_412(last_error) else 60 * attempt
                    current.update({"download_status": "RETRYING", "failure_reason": f"attempt={attempt}; backoff_seconds={delay}"})
                    write_download_progress(output_dir, records, len(entries), "RUNNING")
                    time.sleep(delay)
            else:
                current.update({"download_status": "FAILED", "failure_reason": redact_sensitive_text(last_error)})
                write_download_progress(output_dir, records, len(entries), "RUNNING")
        write_download_progress(output_dir, records, len(entries), "COMPLETE")
        print("STATUS=DOWNLOAD_COMPLETE")
        return 0
    finally:
        remove_temporary_cookie_file(cookie_path)


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
    parser.add_argument("--yt-dlp", help="独立工具环境中的 yt-dlp 可执行文件")
    parser.add_argument("--output-dir", default=str(default_output_dir()))
    parser.add_argument("--auth-dir", default=str(default_auth_dir()))
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--qr-login", action="store_true", help="显示二维码并安全完成本机网页登录")
    parser.add_argument("--download-all", action="store_true", help="从既有 99 项 source manifest 断点续传下载")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        cli_args = parse_args()
        if cli_args.qr_login:
            raise SystemExit(run_qr_login(Path(cli_args.auth_dir).expanduser().resolve(), Path(cli_args.output_dir).expanduser().resolve()))
        if cli_args.download_all:
            if not cli_args.yt_dlp:
                raise RuntimeError("全量下载必须提供 --yt-dlp")
            raise SystemExit(run_download_all(cli_args))
        if not cli_args.yt_dlp:
            raise RuntimeError("非二维码模式必须提供 --yt-dlp")
        raise SystemExit(run_workflow(cli_args))
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"STATUS=FAILED_FAIL_CLOSED\nREASON={redact_sensitive_text(str(error))}", file=sys.stderr)
        raise SystemExit(1)
