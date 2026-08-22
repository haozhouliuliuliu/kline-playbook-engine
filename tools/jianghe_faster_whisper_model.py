"""下载并校验官方 faster-whisper small 模型，不使用付费或云端 ASR。"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.request import Request, build_opener

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.parallel_range_downloader import download_with_ranges


MODEL_REPOSITORY = "Systran/faster-whisper-small"
MODEL_FILE = "model.bin"
HTTP_HEADERS = {"User-Agent": "kline-playbook-engine-local-asr/0.1"}


class _HttpxResponse:
    def __init__(self, response: Any):
        self.status = response.status_code
        self.headers = response.headers
        self._body = io.BytesIO(response.content)

    def read(self, size: int = -1) -> bytes:
        return self._body.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *_: object) -> None:
        return None


class HttpxRangeOpener:
    """仅用于无认证模型文件；严格连接与读取超时，避免 urllib 正文读无限挂起。"""
    def open(self, request: Request, timeout: int) -> _HttpxResponse:
        try:
            import httpx
        except ImportError as error:
            raise RuntimeError("已安装的 httpx 不可用，不能启用模型 HTTP fallback") from error
        response = httpx.get(
            request.full_url, headers=dict(request.header_items()), follow_redirects=True,
            timeout=httpx.Timeout(timeout, connect=timeout),
        )
        return _HttpxResponse(response)


class CurlRangeOpener:
    """仅在 Python HTTP 后端卡死时使用；仍交给同一 Range 校验器组装。"""
    def open(self, request: Request, timeout: int) -> _HttpxResponse:
        with tempfile.TemporaryDirectory(prefix="jianghe-range-") as temporary:
            root = Path(temporary)
            headers_path, body_path = root / "headers.txt", root / "body.bin"
            command = ["curl.exe", "--fail", "--silent", "--show-error", "--location", "--connect-timeout", str(timeout), "--max-time", str(timeout + 5)]
            range_value = None
            for name, value in request.header_items():
                if name.lower() == "range":
                    range_value = value
                    continue
                command.extend(["--header", f"{name}: {value}"])
            if not range_value or not range_value.startswith("bytes="):
                raise RuntimeError("curl Range 请求缺少有效区间")
            command.extend(["--range", range_value.removeprefix("bytes=")])
            command.extend(["--dump-header", str(headers_path), "--output", str(body_path), request.full_url])
            completed = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)
            if completed.returncode != 0:
                raise RuntimeError("curl Range 传输失败")
            raw_headers = headers_path.read_text(encoding="iso-8859-1")
            blocks = [block for block in raw_headers.split("\r\n\r\n") if "Content-Range:" in block or "content-range:" in block]
            if not blocks:
                raise RuntimeError("curl Range 响应缺少 Content-Range")
            lines = blocks[-1].splitlines()
            status_line = next((line for line in lines if line.startswith("HTTP/")), "")
            try:
                status = int(status_line.split()[1])
            except (IndexError, ValueError) as error:
                raise RuntimeError("curl Range 响应状态无效") from error
            headers = {}
            for line in lines[1:]:
                if ":" in line:
                    name, value = line.split(":", 1)
                    headers[name] = value.strip()
            return _HttpxResponse(type("CurlResult", (), {"status_code": status, "headers": headers, "content": body_path.read_bytes()})())


def official_lfs_metadata() -> tuple[str, int]:
    request = Request(f"https://huggingface.co/api/models/{MODEL_REPOSITORY}?blobs=true", headers=HTTP_HEADERS)
    with build_opener().open(request, timeout=45) as response:
        if response.status != 200:
            raise RuntimeError("Hugging Face 官方模型元数据不可访问")
        payload = json.loads(response.read().decode("utf-8"))
    siblings = payload.get("siblings") if isinstance(payload, dict) else None
    if not isinstance(siblings, list):
        raise RuntimeError("Hugging Face 官方模型元数据格式异常")
    for item in siblings:
        if not isinstance(item, dict) or item.get("rfilename") != MODEL_FILE:
            continue
        lfs = item.get("lfs") if isinstance(item.get("lfs"), dict) else {}
        sha256, size = str(lfs.get("sha256") or ""), lfs.get("size")
        if len(sha256) == 64 and isinstance(size, int) and size > 0:
            return sha256, size
    raise RuntimeError("官方模型元数据未提供 model.bin 的 LFS SHA-256 与长度")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while data := handle.read(1024 * 1024):
            digest.update(data)
    return digest.hexdigest()


def cached_snapshot() -> Path:
    from huggingface_hub import snapshot_download

    # 只交给官方缓存机制准备小文件；model.bin 由严格 Range 下载器单独处理。
    location = snapshot_download(MODEL_REPOSITORY, ignore_patterns=[MODEL_FILE])
    path = Path(location)
    if not path.is_dir():
        raise RuntimeError("Hugging Face 缓存未返回可用模型目录")
    return path


def prepare_model(concurrency: int, model_url: str | None = None, use_httpx: bool = False, use_curl: bool = False) -> dict[str, Any]:
    expected_hash, expected_size = official_lfs_metadata()
    snapshot = cached_snapshot()
    model_path = snapshot / MODEL_FILE
    hash_verified = model_path.is_file() and model_path.stat().st_size == expected_size and sha256_file(model_path) == expected_hash
    report = None
    if not hash_verified:
        url = model_url or f"https://huggingface.co/{MODEL_REPOSITORY}/resolve/main/{MODEL_FILE}"
        if not url.startswith("https://hf-mirror.com/") and not url.startswith("https://huggingface.co/"):
            raise RuntimeError("模型下载地址必须是 Hugging Face 官方或单一已声明镜像 HTTPS 地址")
        report = download_with_ranges(
            CurlRangeOpener() if use_curl else HttpxRangeOpener() if use_httpx else build_opener(), url, model_path, snapshot / ".range-model-bin", headers=HTTP_HEADERS,
            concurrency=concurrency,
        )
        if model_path.stat().st_size != expected_size or sha256_file(model_path) != expected_hash:
            raise RuntimeError("官方 model.bin 下载后 SHA-256 或长度校验失败")
        hash_verified = True
    from faster_whisper import WhisperModel

    # 构造器会加载 CTranslate2 模型；未通过不得把工具标为已验证。
    WhisperModel(str(snapshot), device="cpu", compute_type="int8")
    return {
        "status": "VERIFIED_FOR_LOCAL_ASR",
        "model_repository": MODEL_REPOSITORY,
        "model_path": str(snapshot),
        "model_hash_verified": hash_verified,
        "model_hash": expected_hash,
        "model_size": expected_size,
        "model_load_test": "PASS",
        "download": None if report is None else {
            "expected_bytes": report.expected_bytes,
            "transferred_bytes": report.transferred_bytes,
            "elapsed_seconds": round(report.elapsed_seconds, 3),
            "megabytes_per_second": round(report.megabytes_per_second, 4),
            "concurrency": report.concurrency,
            "resumed_chunks": report.resumed_chunks,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--concurrency", type=int, default=4, help="Range 并发数（1--8）")
    parser.add_argument("--model-url", help="仅在官方路线明确失败后使用的同一模型镜像地址")
    parser.add_argument("--use-single-hash-verified-mirror", action="store_true", help="使用唯一镜像候选，仍须官方 LFS SHA-256 通过")
    parser.add_argument("--httpx-range-fallback", action="store_true", help="无认证模型下载使用已安装 httpx 的严格超时后端")
    parser.add_argument("--curl-range-fallback", action="store_true", help="仅在 Python HTTP 后端卡死时使用系统 curl 的严格超时传输")
    args = parser.parse_args()
    if not 1 <= args.concurrency <= 8:
        raise RuntimeError("Range 并发数必须在 1--8")
    if args.model_url and args.use_single_hash_verified_mirror:
        raise RuntimeError("模型镜像地址只能选择一种指定方式")
    model_url = args.model_url
    if args.use_single_hash_verified_mirror:
        model_url = f"https://hf-mirror.com/{MODEL_REPOSITORY}/resolve/main/{MODEL_FILE}"
    if args.httpx_range_fallback and args.curl_range_fallback:
        raise RuntimeError("HTTP fallback 后端只能选择一种")
    print(json.dumps(prepare_model(args.concurrency, model_url, args.httpx_range_fallback, args.curl_range_fallback), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print("STATUS=FAILED_FAIL_CLOSED", file=sys.stderr)
        print("REASON=" + str(error).split("?")[0][:500], file=sys.stderr)
        raise SystemExit(1)
