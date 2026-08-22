"""有限并发、可恢复的 HTTP Range 下载器。

下载器只把经完整性校验的分块拼装为最终文件。临时状态不包含完整 URL，
从而避免把 CDN 的签名查询参数写入日志或仓库。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request


CONTENT_RANGE = re.compile(r"^bytes (\d+)-(\d+)/(\d+)$")


@dataclass(frozen=True)
class RangeChunk:
    index: int
    start: int
    end: int

    @property
    def size(self) -> int:
        return self.end - self.start + 1


@dataclass(frozen=True)
class DownloadReport:
    expected_bytes: int
    transferred_bytes: int
    elapsed_seconds: float
    concurrency: int
    resumed_chunks: int

    @property
    def megabytes_per_second(self) -> float:
        return self.transferred_bytes / max(self.elapsed_seconds, 0.001) / 1024 / 1024


def redact_download_reference(url: str) -> str:
    """保留协议、主机和路径，绝不返回查询参数或片段。"""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def build_range_chunks(total_bytes: int, chunk_bytes: int) -> list[RangeChunk]:
    if total_bytes <= 0:
        raise RuntimeError("远端文件总长度必须为正数")
    if chunk_bytes <= 0:
        raise RuntimeError("Range 分块大小必须为正数")
    return [
        RangeChunk(index=index, start=start, end=min(total_bytes - 1, start + chunk_bytes - 1))
        for index, start in enumerate(range(0, total_bytes, chunk_bytes))
    ]


def _response_status(response: Any) -> int:
    status = getattr(response, "status", None)
    if status is None and hasattr(response, "getcode"):
        status = response.getcode()
    try:
        return int(status)
    except (TypeError, ValueError) as error:
        raise RuntimeError("HTTP 响应缺少状态码") from error


def _content_range(response: Any) -> tuple[int, int, int]:
    raw = str(response.headers.get("Content-Range") or "")
    match = CONTENT_RANGE.fullmatch(raw)
    if not match:
        raise RuntimeError("服务端未返回严格 Content-Range")
    return tuple(int(value) for value in match.groups())


def probe_range_source(opener: Any, url: str, headers: dict[str, str], timeout: int = 45) -> int:
    """只接受严格的 206/0--0 应答，普通 200 必须失败关闭。"""
    request = Request(url, headers={**headers, "Range": "bytes=0-0"})
    with opener.open(request, timeout=timeout) as response:
        if _response_status(response) != 206:
            raise RuntimeError("服务端不支持 HTTP Range，拒绝生成不完整候选文件")
        start, end, total = _content_range(response)
        if (start, end) != (0, 0) or total <= 0:
            raise RuntimeError("服务端 Range 探测边界不匹配")
        first_byte = response.read(1)
        if len(first_byte) != 1:
            raise RuntimeError("服务端 Range 探测未返回首字节")
    return total


def _chunk_paths(work_dir: Path, chunk: RangeChunk) -> tuple[Path, Path, Path]:
    stem = f"chunk-{chunk.index:06d}"
    return work_dir / f"{stem}.part", work_dir / f"{stem}.json", work_dir / f"{stem}.tmp"


def _valid_completed_chunk(work_dir: Path, chunk: RangeChunk) -> bool:
    part_path, metadata_path, _ = _chunk_paths(work_dir, chunk)
    if not part_path.is_file() or not metadata_path.is_file() or part_path.stat().st_size != chunk.size:
        return False
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    digest = hashlib.sha256(part_path.read_bytes()).hexdigest()
    return metadata == {"start": chunk.start, "end": chunk.end, "size": chunk.size, "sha256": digest}


def assemble_completed_chunks(work_dir: Path, chunks: list[RangeChunk], destination: Path, expected_bytes: int) -> None:
    """所有分块均完整时才原子替换 destination。"""
    if not chunks:
        raise RuntimeError("没有可拼装的 Range 分块")
    if any(not _valid_completed_chunk(work_dir, chunk) for chunk in chunks):
        raise RuntimeError("存在缺失或损坏的 Range 分块，拒绝拼装")
    assembling = destination.with_name(destination.name + ".assembling")
    if assembling.exists():
        assembling.unlink()
    try:
        with assembling.open("wb") as target:
            for chunk in chunks:
                part_path, _, _ = _chunk_paths(work_dir, chunk)
                with part_path.open("rb") as source:
                    while data := source.read(1024 * 1024):
                        target.write(data)
            target.flush()
            os.fsync(target.fileno())
        if assembling.stat().st_size != expected_bytes:
            raise RuntimeError("拼装文件长度与远端总长度不一致")
        os.replace(assembling, destination)
    finally:
        if assembling.exists():
            assembling.unlink()


def download_with_ranges(
    opener: Any,
    url: str,
    destination: Path,
    work_dir: Path,
    *,
    headers: dict[str, str] | None = None,
    chunk_bytes: int = 16 * 1024 * 1024,
    concurrency: int = 4,
    max_chunk_attempts: int = 3,
    timeout: int = 45,
) -> DownloadReport:
    """下载单文件；只复用元数据和 SHA-256 均匹配的完整分块。"""
    if concurrency < 1 or concurrency > 8:
        raise RuntimeError("Range 并发数必须在 1--8")
    if max_chunk_attempts < 1:
        raise RuntimeError("每个 Range 分块至少尝试一次")
    safe_headers = dict(headers or {})
    expected_bytes = probe_range_source(opener, url, safe_headers, timeout)
    chunks = build_range_chunks(expected_bytes, chunk_bytes)
    work_dir.mkdir(parents=True, exist_ok=True)
    state_path = work_dir / "download_state.json"
    state = {"expected_bytes": expected_bytes, "chunk_bytes": chunk_bytes, "chunk_count": len(chunks)}
    if state_path.exists():
        try:
            prior = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior = None
        if prior != state:
            raise RuntimeError("已有下载分块与当前远端对象或分块配置不匹配")
    else:
        state_path.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")

    resumed = [chunk for chunk in chunks if _valid_completed_chunk(work_dir, chunk)]
    pending = [chunk for chunk in chunks if chunk not in resumed]
    transfer_lock = threading.Lock()
    transferred_bytes = 0

    def fetch_chunk(chunk: RangeChunk) -> None:
        nonlocal transferred_bytes
        part_path, metadata_path, temporary_path = _chunk_paths(work_dir, chunk)
        last_error: Exception | None = None
        for attempt in range(1, max_chunk_attempts + 1):
            if temporary_path.exists():
                temporary_path.unlink()
            request = Request(url, headers={**safe_headers, "Range": f"bytes={chunk.start}-{chunk.end}"})
            try:
                # 每个请求只读取同一登录态；响应体必须允许真正并发读取。
                response_context = opener.open(request, timeout=timeout)
                with response_context as response:
                    if _response_status(response) != 206:
                        raise RuntimeError(f"Range 分块返回 HTTP {_response_status(response)}")
                    start, end, total = _content_range(response)
                    if (start, end, total) != (chunk.start, chunk.end, expected_bytes):
                        raise RuntimeError("Range 分块边界或总长度不匹配")
                    digest = hashlib.sha256()
                    received = 0
                    with temporary_path.open("wb") as handle:
                        while data := response.read(1024 * 1024):
                            received += len(data)
                            if received > chunk.size:
                                raise RuntimeError("Range 分块返回超出声明边界的数据")
                            digest.update(data)
                            handle.write(data)
                        handle.flush()
                        os.fsync(handle.fileno())
                if received != chunk.size:
                    raise RuntimeError("Range 分块长度不完整")
                os.replace(temporary_path, part_path)
                metadata_path.write_text(
                    json.dumps({"start": chunk.start, "end": chunk.end, "size": chunk.size, "sha256": digest.hexdigest()}, sort_keys=True),
                    encoding="utf-8",
                )
                with transfer_lock:
                    transferred_bytes += received
                return
            except Exception as error:  # 保留已完成分块，当前未完成分块在有限重试后失败关闭。
                last_error = error
                if attempt < max_chunk_attempts:
                    time.sleep(min(attempt, 3))
        raise RuntimeError(f"Range 分块 {chunk.index} 下载失败：{last_error}")

    started = time.monotonic()
    if pending:
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(fetch_chunk, chunk) for chunk in pending]
            for future in as_completed(futures):
                future.result()
    assemble_completed_chunks(work_dir, chunks, destination, expected_bytes)
    return DownloadReport(expected_bytes, transferred_bytes, time.monotonic() - started, concurrency, len(resumed))
