#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for tools/exact_range.py — read-only frame/clip extraction."""
import json
import os
import subprocess
import sys
import tempfile

TOOL = os.path.join(os.path.dirname(__file__), "..", "tools", "exact_range.py")
PY = "C:/Users/H/.workbuddy/binaries/python/versions/3.13.12/python.exe"

# First available video from the acceptance output (known to exist locally).
KNOWN_BVID = "BV1yxebzoERD"
KNOWN_DURATION = 474.756


def _run(args):
    return subprocess.run([PY, TOOL] + args, capture_output=True, text=True)


def test_exact_timestamp():
    with tempfile.TemporaryDirectory() as td:
        out_dir = td
        r = _run(["--bvid", KNOWN_BVID, "--start", "5.0", "--out", out_dir, "--single"])
        assert r.returncode == 0, r.stderr
        res = json.loads(r.stdout)
        p = res["frames"][0]["path"]
        assert os.path.exists(p) and os.path.getsize(p) > 0, "frame png not created"


def test_range_extraction():
    with tempfile.TemporaryDirectory() as td:
        r = _run(["--bvid", KNOWN_BVID, "--start", "5.0", "--end", "7.0",
                  "--interval", "0.5", "--out", td])
        assert r.returncode == 0, r.stderr
        res = json.loads(r.stdout)
        # 5.0,  ](5.5, 6.0, 6.5 -> 4 frames; 7.0 excluded
        assert len(res["frames"]) == 4, "expected 4 frames, got %d" % len(res["frames"])
        for fr in res["frames"]:
            assert os.path.getsize(fr["path"]) > 0


def test_windows_path():
    # output dir given in Windows-style backslash form must work
    with tempfile.TemporaryDirectory() as td:
        win_out = td.replace("/", "\\")
        r = _run(["--bvid", KNOWN_BVID, "--start", "3.0", "--out", win_out, "--single"])
        assert r.returncode == 0, r.stderr
        assert os.path.exists(os.path.join(td, "frame_t3.000.png"))


def test_invalid_bvid():
    with tempfile.TemporaryDirectory() as td:
        r = _run(["--bvid", "BV_INVALID_XYZ", "--start", "0", "--out", td, "--single"])
        assert r.returncode == 2, "invalid BVID must exit 2"
        assert "BVID_NOT_FOUND" in r.stderr
        # ensure no stray output file created
        assert not any(f.endswith(".png") for f in os.listdir(td))


if __name__ == "__main__":
    test_exact_timestamp()
    test_range_extraction()
    test_windows_path()
    test_invalid_bvid()
    print("ALL TESTS PASSED")
