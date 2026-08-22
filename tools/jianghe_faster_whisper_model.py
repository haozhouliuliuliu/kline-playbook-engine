"""下载并校验官方 faster-whisper small 模型，不使用付费或云端 ASR。"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
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


def prepare_model(concurrency: int) -> dict[str, Any]:
    expected_hash, expected_size = official_lfs_metadata()
    snapshot = cached_snapshot()
    model_path = snapshot / MODEL_FILE
    hash_verified = model_path.is_file() and model_path.stat().st_size == expected_size and sha256_file(model_path) == expected_hash
    report = None
    if not hash_verified:
        url = f"https://huggingface.co/{MODEL_REPOSITORY}/resolve/main/{MODEL_FILE}"
        report = download_with_ranges(
            build_opener(), url, model_path, snapshot / ".range-model-bin", headers=HTTP_HEADERS,
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
    args = parser.parse_args()
    if not 1 <= args.concurrency <= 8:
        raise RuntimeError("Range 并发数必须在 1--8")
    print(json.dumps(prepare_model(args.concurrency), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print("STATUS=FAILED_FAIL_CLOSED", file=sys.stderr)
        print("REASON=" + str(error).split("?")[0][:500], file=sys.stderr)
        raise SystemExit(1)
