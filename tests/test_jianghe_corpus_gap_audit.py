import unittest

from tools.jianghe_corpus_gap_audit import bili_json_to_srt, preferred_track, seconds_to_srt, validate_sources
from tools.jianghe_local_asr import validate_timeline


class JiangheCorpusGapAuditTests(unittest.TestCase):
    def test_timestamp_conversion(self):
        self.assertEqual(seconds_to_srt(3661.234), "01:01:01,234")

    def test_bilibili_subtitle_json_conversion(self):
        result = bili_json_to_srt({"body": [{"from": 0, "to": 1.25, "content": "测试"}]})
        self.assertIn("00:00:00,000 --> 00:00:01,250", result)
        self.assertIn("测试", result)

    def test_preferred_track_prefers_chinese(self):
        track = preferred_track([{"lan": "en"}, {"lan": "ai-zh"}])
        self.assertEqual(track["lan"], "ai-zh")

    def test_source_validation_rejects_duplicate_bvid(self):
        rows = [{"ordinal": number, "bvid": "BV1same" if number < 3 else f"BV{number}"} for number in range(1, 100)]
        with self.assertRaises(RuntimeError):
            validate_sources(rows)

    def test_timeline_validation_rejects_non_monotonic_segments(self):
        result = validate_timeline([
            {"start": 0, "end": 2}, {"start": 1, "end": 3},
        ], 3)
        self.assertFalse(result["timestamps_monotonic"])


if __name__ == "__main__":
    unittest.main()
