import io
import tempfile
import unittest
from pathlib import Path

from tools.parallel_range_downloader import (
    assemble_completed_chunks,
    build_range_chunks,
    download_with_ranges,
    redact_download_reference,
)


class FakeResponse:
    def __init__(self, status, headers, data):
        self.status = status
        self.headers = headers
        self._body = io.BytesIO(data)

    def read(self, size=-1):
        return self._body.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class FakeRangeOpener:
    def __init__(self, data, support_ranges=True, wrong_total=None):
        self.data = data
        self.support_ranges = support_ranges
        self.wrong_total = wrong_total
        self.calls = []

    def open(self, request, timeout):
        range_header = request.headers.get("Range")
        self.calls.append(range_header)
        if not self.support_ranges:
            return FakeResponse(200, {}, self.data)
        start, end = [int(value) for value in range_header.removeprefix("bytes=").split("-")]
        end = len(self.data) - 1 if not str(end) else end
        total = self.wrong_total if self.wrong_total is not None else len(self.data)
        return FakeResponse(206, {"Content-Range": f"bytes {start}-{end}/{total}"}, self.data[start:end + 1])


class ParallelRangeDownloaderTests(unittest.TestCase):
    def test_build_range_chunks_includes_exact_boundaries(self):
        chunks = build_range_chunks(17, 8)
        self.assertEqual([(item.start, item.end) for item in chunks], [(0, 7), (8, 15), (16, 16)])

    def test_resume_reuses_completed_chunks(self):
        data = b"0123456789abcdefghi"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "candidate.bin"
            work_dir = root / "chunks"
            first = FakeRangeOpener(data)
            download_with_ranges(first, "https://safe.example/item?signature=hidden", destination, work_dir, chunk_bytes=8, concurrency=2)
            destination.unlink()
            second = FakeRangeOpener(data)
            report = download_with_ranges(second, "https://safe.example/item?signature=changed", destination, work_dir, chunk_bytes=8, concurrency=2)
            self.assertEqual(destination.read_bytes(), data)
            self.assertEqual(report.resumed_chunks, 3)
            self.assertEqual(second.calls, ["bytes=0-0"])

    def test_tampered_completed_chunk_is_downloaded_again(self):
        data = b"0123456789abcdef"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            destination = root / "candidate.bin"
            work_dir = root / "chunks"
            download_with_ranges(FakeRangeOpener(data), "https://safe.example/item", destination, work_dir, chunk_bytes=8, concurrency=2)
            (work_dir / "chunk-000001.part").write_bytes(b"tampered")
            destination.unlink()
            opener = FakeRangeOpener(data)
            report = download_with_ranges(opener, "https://safe.example/item", destination, work_dir, chunk_bytes=8, concurrency=2)
            self.assertEqual(report.resumed_chunks, 1)
            self.assertIn("bytes=8-15", opener.calls)
            self.assertEqual(destination.read_bytes(), data)

    def test_missing_chunk_rejects_assembly(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(RuntimeError, "缺失或损坏"):
                assemble_completed_chunks(root, build_range_chunks(8, 4), root / "candidate.bin", 8)

    def test_total_size_mismatch_rejects_download(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(RuntimeError, "长度不完整"):
                download_with_ranges(FakeRangeOpener(b"01234567", wrong_total=9), "https://safe.example/item", root / "candidate.bin", root / "chunks", chunk_bytes=4)

    def test_no_range_support_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(RuntimeError, "不支持 HTTP Range"):
                download_with_ranges(FakeRangeOpener(b"01234567", support_ranges=False), "https://safe.example/item", root / "candidate.bin", root / "chunks")

    def test_redaction_strips_signature_query(self):
        safe = redact_download_reference("https://safe.example/video.m4s?signature=super-secret-value#fragment")
        self.assertEqual(safe, "https://safe.example/video.m4s")
        self.assertNotIn("secret", safe)


if __name__ == "__main__":
    unittest.main()
