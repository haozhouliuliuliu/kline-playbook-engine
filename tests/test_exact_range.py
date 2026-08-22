#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Portable local-corpus integration tests for tools/exact_range.py.

These tests require the Jianghe media corpus and ffmpeg. They skip cleanly when
that local evidence environment is unavailable, so repository-wide unittest
discovery remains portable.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

from tools import exact_range

TOOL = os.path.join(os.path.dirname(__file__), "..", "tools", "exact_range.py")
PY = sys.executable
KNOWN_BVID = "BV1yxebzoERD"


def _local_evidence_available():
    if not os.path.isfile(exact_range.FFMPEG):
        return False
    try:
        exact_range.resolve_media(KNOWN_BVID)
    except ValueError:
        return False
    return True


def _run(args):
    return subprocess.run([PY, TOOL] + args, capture_output=True, text=True)


@unittest.skipUnless(
    _local_evidence_available(),
    "requires local Jianghe corpus and configured ffmpeg evidence environment",
)
class ExactRangeLocalIntegrationTests(unittest.TestCase):
    def test_exact_timestamp(self):
        with tempfile.TemporaryDirectory() as td:
            r = _run(["--bvid", KNOWN_BVID, "--start", "5.0", "--out", td, "--single"])
            self.assertEqual(r.returncode, 0, r.stderr)
            res = json.loads(r.stdout)
            p = res["frames"][0]["path"]
            self.assertTrue(os.path.exists(p) and os.path.getsize(p) > 0, "frame png not created")

    def test_range_extraction(self):
        with tempfile.TemporaryDirectory() as td:
            r = _run([
                "--bvid", KNOWN_BVID,
                "--start", "5.0",
                "--end", "7.0",
                "--interval", "0.5",
                "--out", td,
            ])
            self.assertEqual(r.returncode, 0, r.stderr)
            res = json.loads(r.stdout)
            self.assertEqual(len(res["frames"]), 4)
            for frame in res["frames"]:
                self.assertGreater(os.path.getsize(frame["path"]), 0)

    def test_windows_path(self):
        with tempfile.TemporaryDirectory() as td:
            win_out = td.replace("/", "\\") if os.name == "nt" else td
            r = _run(["--bvid", KNOWN_BVID, "--start", "3.0", "--out", win_out, "--single"])
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(td, "frame_t3.000.png")))

    def test_creates_missing_output_directory(self):
        with tempfile.TemporaryDirectory() as td:
            out_dir = os.path.join(td, "new", "nested", "frames")
            r = _run(["--bvid", KNOWN_BVID, "--start", "4.0", "--out", out_dir, "--single"])
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertTrue(os.path.exists(os.path.join(out_dir, "frame_t4.000.png")))


class ExactRangePortableBehaviorTests(unittest.TestCase):
    def test_invalid_bvid_fails_closed_without_output(self):
        with tempfile.TemporaryDirectory() as td:
            r = _run(["--bvid", "BV_INVALID_XYZ", "--start", "0", "--out", td, "--single"])
            self.assertEqual(r.returncode, 2)
            self.assertIn("BVID_NOT_FOUND", r.stderr)
            self.assertFalse(any(name.endswith(".png") for name in os.listdir(td)))


if __name__ == "__main__":
    unittest.main()
