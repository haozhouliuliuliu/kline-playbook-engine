import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

from tools.bilibili_corpus_acquisition import (
    assert_preserved_source_manifest,
    build_download_command,
    conservative_corpus_estimate,
    deduplicate_bvids,
    disk_capacity_safe,
    follow_bilibili_login_redirect,
    highest_dash_video,
    is_bilibili_hostname,
    media_backoff_seconds,
    part_identity,
    qr_status_name,
    qr_poll_status_code,
    redact_sensitive_text,
    remove_temporary_cookie_file,
    sanitize_windows_filename,
    signed_wbi_query,
    source_manifest_is_complete,
    quality_verification,
    download_output_template,
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

    def test_qr_status_handling(self):
        self.assertEqual(qr_status_name(86101), 'WAITING_FOR_SCAN')
        self.assertEqual(qr_status_name(86090), 'WAITING_FOR_CONFIRMATION')
        self.assertEqual(qr_status_name(86038), 'EXPIRED')
        self.assertEqual(qr_status_name(0), 'SUCCESS')

    def test_qr_status_comes_from_nested_data_code(self):
        self.assertEqual(qr_poll_status_code({'code': 0, 'data': {'code': 86101}}), 86101)
        with self.assertRaises(RuntimeError):
            qr_poll_status_code({'code': -400, 'data': {}})

    def test_media_412_backoff_is_conservative(self):
        self.assertEqual(media_backoff_seconds(1), 600)
        self.assertEqual(media_backoff_seconds(2), 1200)
        self.assertEqual(media_backoff_seconds(9), 3600)

    def test_temporary_cookie_cleanup(self):
        with TemporaryDirectory() as temporary_dir:
            cookie_path = Path(temporary_dir) / 'bilibili-session.cookies.txt'
            cookie_path.write_text('temporary-only', encoding='utf-8')
            remove_temporary_cookie_file(cookie_path)
            self.assertFalse(cookie_path.exists())

    def test_support_label_above_actual_dash_does_not_cause_false_fail(self):
        info = {
            'support_formats': [{'height': 1080, 'new_description': '1080P'}],
            'formats': [{'height': 720, 'width': 1280, 'fps': 30, 'vcodec': 'avc1', 'acodec': 'none'}],
        }
        self.assertEqual(quality_verification(info)['quality_verification'], 'PASS')

    def test_dash_selection_prefers_highest_quality_id(self):
        dash = {'video': [{'id': 64, 'bandwidth': 4}, {'id': 80, 'bandwidth': 2}]}
        self.assertEqual(highest_dash_video(dash)['id'], 80)

    def test_existing_99_row_manifest_is_preserved(self):
        with TemporaryDirectory() as temporary_dir:
            manifest_dir = Path(temporary_dir) / 'manifests'
            manifest_dir.mkdir()
            manifest = manifest_dir / 'source_manifest.jsonl'
            manifest.write_text(''.join('{"bvid":"BV1"}\n' for _ in range(99)), encoding='utf-8')
            assert_preserved_source_manifest(Path(temporary_dir))

    def test_qr_login_redirect_accepts_only_bilibili_https(self):
        opener = MagicMock()
        opener.open.return_value.__enter__.return_value = MagicMock()
        follow_bilibili_login_redirect(opener, 'https://www.bilibili.com/account/history')
        self.assertEqual(opener.open.call_count, 1)
        follow_bilibili_login_redirect(opener, '')
        self.assertEqual(opener.open.call_count, 1)
        with self.assertRaises(RuntimeError):
            follow_bilibili_login_redirect(opener, 'https://example.com/redirect')

    def test_bilibili_hostname_validation_ignores_port(self):
        self.assertTrue(is_bilibili_hostname('passport.bilibili.com'))
        self.assertFalse(is_bilibili_hostname('bilibili.com.example.com'))

    def test_duration_based_capacity_estimate(self):
        self.assertEqual(conservative_corpus_estimate([{'duration_seconds': 8}]), 10_000_000)

    def test_download_command_uses_source_best_without_reencoding(self):
        entry = {'ordinal': 2, 'upload_date': '20260101', 'bvid': 'BV1test', 'title': 'test',
                 'original_url': 'https://www.bilibili.com/video/BV1test'}
        command = build_download_command('yt-dlp', Path('auth.cookies'), Path('D:/corpus'), entry)
        self.assertIn('bestvideo*+bestaudio/best', command)
        self.assertIn('--merge-output-format', command)
        self.assertIn('--socket-timeout', command)
        normalized = [item.replace('\\', '/') for item in command]
        self.assertIn('home:D:/corpus/media', normalized)
        self.assertIn('subtitle:D:/corpus/subtitles', normalized)
        self.assertIn('infojson:D:/corpus/metadata', normalized)
        self.assertNotIn('--recode-video', command)
        self.assertEqual(download_output_template(entry), '000002__20260101__BV1test__test.%(ext)s')


if __name__ == '__main__':
    unittest.main()
