import unittest

from tools.bilibili_corpus_acquisition import (
    deduplicate_bvids,
    disk_capacity_safe,
    part_identity,
    redact_sensitive_text,
    sanitize_windows_filename,
    signed_wbi_query,
    source_manifest_is_complete,
)


class BilibiliCorpusAcquisitionTests(unittest.TestCase):
    def test_windows_filename_sanitization(self):
        self.assertEqual(sanitize_windows_filename('CON'), '_CON')
        self.assertEqual(sanitize_windows_filename('a<>:"/\\|?*b.'), 'a_________b')
        self.assertEqual(sanitize_windows_filename('   '), 'untitled')

    def test_bvid_deduplication_and_deterministic_ordering(self):
        records = [
            {'bvid': 'BV2', 'timestamp': 2}, {'bvid': 'BV1', 'timestamp': 1}, {'bvid': 'BV2', 'timestamp': 3},
        ]
        unique, duplicates = deduplicate_bvids(records)
        self.assertEqual(duplicates, 1)
        self.assertEqual([record['bvid'] for record in unique], ['BV1', 'BV2'])
        self.assertEqual([record['ordinal'] for record in unique], [1, 2])

    def test_multi_part_identity(self):
        self.assertEqual(part_identity('BV1abc', 2), 'BV1abc__p02')
        self.assertEqual(part_identity('BV1abc', None), 'BV1abc__p01')

    def test_incomplete_enumeration_fails_closed(self):
        self.assertFalse(source_manifest_is_complete(None, []))
        self.assertFalse(source_manifest_is_complete(2, [{'bvid': 'BV1'}]))
        self.assertTrue(source_manifest_is_complete(1, [{'bvid': 'BV1'}]))

    def test_disk_space_guard(self):
        self.assertTrue(disk_capacity_safe(70, 100))
        self.assertFalse(disk_capacity_safe(71, 100))
        self.assertFalse(disk_capacity_safe(None, 100))

    def test_log_redaction_never_keeps_cookie_value(self):
        value = redact_sensitive_text('Cookie: SESSDATA=private-value; token=another-secret')
        self.assertNotIn('private-value', value)
        self.assertNotIn('another-secret', value)

    def test_wbi_query_is_deterministic_except_timestamp(self):
        query = signed_wbi_query({'mid': '123', 'order': 'pubdate'}, 'a' * 32)
        self.assertIn('mid=123', query)
        self.assertIn('order=pubdate', query)
        self.assertRegex(query, r'w_rid=[0-9a-f]{32}$')


if __name__ == '__main__':
    unittest.main()
