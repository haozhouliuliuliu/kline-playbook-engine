#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
exact_range.py — read-only frame / clip extraction tool for the JiangHe trader corpus.

Given a BVID (resolved against D:/江河交易员/media), extract:
  * a single original-resolution PNG at an exact timestamp
  * a sequence of frames across a [start, end] range at a given interval
  * an optional lossless (stream-copy) short clip

Hard rules (enforced):
  - Never modifies the source video.
  - No AI image analysis, no OCR, no "important-segment" auto-selection.
  - Outputs are written to a caller-specified directory (never the source tree).
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys

FFMPEG = "C:/Users/H/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.1-full_build-shared/bin/ffmpeg.exe"
MEDIA_ROOT = "D:/江河交易员/media"

FRAGMENT_RE = re.compile(r"\.f\d+\.mp4$", re.IGNORECASE)


def resolve_media(bvid, media_root=MEDIA_ROOT):
    """Resolve a BVID to its final local mp4 (excluding merge/intermediate fragments)."""
    hits = [h for h in glob.glob(os.path.join(media_root, "*%s*.mp4" % bvid))
            if not FRAGMENT_RE.search(os.path.basename(h))]
    if not hits:
        raise ValueError("BVID_NOT_FOUND: %s" % bvid)
    # prefer the shortest matching name (final merged file is the base name)
    hits.sort(key=lambda p: len(os.path.basename(p)))
    return hits[0]


def extract_single_frame(video_path, timestamp, out_png, ffmpeg=FFMPEG, accurate=True):
    """Extract one frame at `timestamp` (seconds) into out_png at original resolution.

    accurate=True places -ss after -i for frame-exact seek (slower, precise).
    """
    if accurate:
        cmd = [ffmpeg, "-i", video_path, "-ss", "%.6f" % timestamp, "-frames:v", "1", "-y", out_png]
    else:
        cmd = [ffmpeg, "-ss", "%.6f" % timestamp, "-i", video_path, "-frames:v", "1", "-y", out_png]
    _run(cmd)


def extract_range(video_path, start, end, interval, out_dir, ffmpeg=FFMPEG, accurate=True):
    """Extract one frame every `interval` seconds between start and end.

    Returns list of {"timestamp": float, "path": str}.
    """
    os.makedirs(out_dir, exist_ok=True)
    frames = []
    t = float(start)
    idx = 1
    while t < float(end) - 1e-6:
        out_png = os.path.join(out_dir, "frame_%05d_t%.3f.png" % (idx, t))
        extract_single_frame(video_path, t, out_png, ffmpeg, accurate)
        frames.append({"timestamp": round(t, 3), "path": out_png})
        t += float(interval)
        idx += 1
    return frames


def make_clip(video_path, start, end, out_path, ffmpeg=FFMPEG, lossless=True):
    """Produce a short clip spanning [start, end]. lossless=True uses stream copy (no re-encode)."""
    if lossless:
        cmd = [ffmpeg, "-ss", "%.6f" % start, "-to", "%.6f" % end, "-i", video_path,
               "-c", "copy", "-y", out_path]
    else:
        cmd = [ffmpeg, "-ss", "%.6f" % start, "-to", "%.6f" % end, "-i", video_path,
               "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-y", out_path]
    _run(cmd)


def _run(cmd):
    try:
        # ffmpeg may emit non-ASCII text from Chinese file paths.  Preserve the
        # process result even when the active Windows code page cannot decode it.
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=300,
        )
    except Exception as e:
        raise RuntimeError("FFMPEG_INVOKE_FAILED: %s" % e)
    if r.returncode != 0:
        raise RuntimeError("FFMPEG_FAILED rc=%s: %s" % (r.returncode, r.stderr[-500:]))


def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only frame/clip extraction for JiangHe corpus.")
    p.add_argument("--bvid", required=True, help="Bilibili BVID, e.g. BV1yxebzoERD")
    p.add_argument("--start", type=float, default=0.0, help="start timestamp (seconds)")
    p.add_argument("--end", type=float, default=None, help="end timestamp (seconds); required for range")
    p.add_argument("--interval", type=float, default=None, help="frame interval in seconds (range mode)")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--clip", action="store_true", help="also produce a lossless short clip")
    p.add_argument("--no-lossless-clip", dest="lossless", action="store_false", default=True,
                   help="re-encode clip instead of stream-copy")
    p.add_argument("--single", action="store_true", help="single-frame mode (ignore interval/end)")
    p.add_argument("--ffmpeg", default=FFMPEG, help="ffmpeg binary path")
    args = p.parse_args(argv)

    try:
        video = resolve_media(args.bvid)
    except ValueError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 2

    os.makedirs(args.out, exist_ok=True)
    result = {"bvid": args.bvid, "video_path": video, "frames": [], "clip": None}
    if args.single:
        out_png = os.path.join(args.out, "frame_t%.3f.png" % args.start)
        extract_single_frame(video, args.start, out_png, args.ffmpeg)
        result["frames"] = [{"timestamp": round(args.start, 3), "path": out_png}]
    else:
        if args.end is None or args.interval is None:
            print("ERROR: range mode requires --end and --interval", file=sys.stderr)
            return 2
        result["frames"] = extract_range(video, args.start, args.end, args.interval,
                                         args.out, args.ffmpeg)
        if args.clip:
            clip_path = os.path.join(args.out, "clip_%s_%.3f-%.3f.mp4" % (args.bvid, args.start, args.end))
            make_clip(video, args.start, args.end, clip_path, args.ffmpeg, lossless=args.lossless)
            result["clip"] = clip_path

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
