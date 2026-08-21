#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build the first-5 AVAILABLE analysis packages (pilot) for the JiangHe trader corpus.

For each of the first 5 AVAILABLE videos (sorted by upload_date), create:
  analysis_packages/<analysis_ordinal>__<bvid>/
    manifest.json
    source_metadata.json
    transcript_or_subtitle.srt        (copied if native subtitle exists)
    visual_index/                    (fixed-time-coverage frames + index.json)
    README.txt

Mechanical only: fixed-time coverage frames; NO AI selection, NO content analysis.
Original videos are never modified.
"""
import glob
import json
import os
import shutil
import sys

import exact_range  # local module (same tools/ dir)

ROOT = "D:/江河交易员"
MANIFESTS = os.path.join(ROOT, "manifests")
PKG_ROOT = os.path.join(ROOT, "analysis_packages")
SUBTITLES = os.path.join(ROOT, "subtitles")
METADATA = os.path.join(ROOT, "metadata")
FFMPEG = exact_range.FFMPEG


def load_jsonl(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def extract_coverage(video, dur, interval, out_dir):
    """Fixed-time coverage. Resilient: one failed frame does not abort the run."""
    os.makedirs(out_dir, exist_ok=True)
    frames = []
    t = 0.0
    idx = 1
    while t < dur - 1e-6:
        out_png = os.path.join(out_dir, "frame_%05d_t%.3f.png" % (idx, t))
        try:
            exact_range.extract_single_frame(video, t, out_png, FFMPEG, accurate=False)
            ok = os.path.exists(out_png) and os.path.getsize(out_png) > 0
        except Exception as e:
            ok = False
            sys.stderr.write("frame fail @%.3f: %s\n" % (t, e))
        if ok:
            frames.append({"timestamp": round(t, 3), "path": out_png})
        t += interval
        idx += 1
    return frames


def main():
    queue = load_jsonl(os.path.join(MANIFESTS, "analysis_queue.jsonl"))
    avail = [q for q in queue if q["source_status"] == "AVAILABLE"]
    top5 = avail[:5]
    print("building %d packages" % len(top5), flush=True)

    summary = []
    for q in top5:
        bvid = q["bvid"]
        ordinal = q["analysis_ordinal"]
        pkg_dir = os.path.join(PKG_ROOT, "%03d__%s" % (ordinal, bvid))
        os.makedirs(pkg_dir, exist_ok=True)
        os.makedirs(os.path.join(pkg_dir, "visual_index"), exist_ok=True)

        info_src = None
        hit = glob.glob(os.path.join(METADATA, "*%s*.info.json" % bvid))
        if hit:
            with open(hit[0], encoding="utf-8") as f:
                info_src = json.load(f)
        source_meta = {
            "bvid": bvid,
            "title": q["title"],
            "upload_date": q["upload_date"],
            "duration_seconds": q["duration_seconds"],
            "width": q["width"],
            "height": q["height"],
            "fps": q["fps"],
            "video_sha256": q["video_sha256"],
            "source_status": q["source_status"],
            "raw_info_json_present": info_src is not None,
        }
        if info_src:
            source_meta["raw"] = info_src
        with open(os.path.join(pkg_dir, "source_metadata.json"), "w", encoding="utf-8") as f:
            json.dump(source_meta, f, ensure_ascii=False, indent=2)

        sub_src = q.get("subtitle_path")
        sub_copied = None
        if sub_src and os.path.exists(sub_src):
            dst = os.path.join(pkg_dir, "transcript_or_subtitle.srt")
            shutil.copy2(sub_src, dst)
            sub_copied = "transcript_or_subtitle.srt"

        dur = q["duration_seconds"] or 0
        interval = max(15.0, dur / 40.0)
        idx = extract_coverage(q["local_video_path"], dur, interval,
                              os.path.join(pkg_dir, "visual_index"))
        index = {
            "bvid": bvid,
            "coverage": "fixed_time_interval",
            "interval_seconds": round(interval, 3),
            "frame_count": len(idx),
            "frames": idx,
        }
        with open(os.path.join(pkg_dir, "visual_index", "index.json"), "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

        manifest = {
            "analysis_ordinal": ordinal,
            "bvid": bvid,
            "title": q["title"],
            "upload_date": q["upload_date"],
            "duration_seconds": q["duration_seconds"],
            "width": q["width"],
            "height": q["height"],
            "fps": q["fps"],
            "video_sha256": q["video_sha256"],
            "subtitle_status": q["subtitle_status"],
            "local_video_path": q["local_video_path"],
            "items": [
                "manifest.json",
                "source_metadata.json",
                sub_copied or "(no native subtitle)",
                "visual_index/",
            ],
            "visual_index_frames": len(idx),
        }
        with open(os.path.join(pkg_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        readme = (
            "Analysis Package (PILOT)\n"
            "======================\n\n"
            "BVID: %s\n"
            "Title: %s\n"
            "Upload date: %s\n"
            "Duration: %.1f s | Resolution: %sx%s | FPS: %s\n"
            "Subtitle status: %s\n\n"
            "Contents:\n"
            "  manifest.json               - package manifest\n"
            "  source_metadata.json        - source metadata (raw yt-dlp info embedded)\n"
            "  transcript_or_subtitle.srt  - native Bilibili subtitle copy (if available)\n"
            "  visual_index/               - mechanically sampled frames + index.json\n"
            "                              (fixed-time coverage, NO AI selection)\n\n"
            "RULES / BOUNDARY:\n"
            "- Original video is never modified; verify any conclusion by re-extracting\n"
            "  exact ranges with the exact_range tool against the source video.\n"
            "- No transaction-strategy analysis is performed here; this is mechanical coverage only.\n"
            "- Frames are sampled at a fixed time interval so no long span is skipped.\n"
        ) % (bvid, q["title"], q["upload_date"], q["duration_seconds"],
              q["width"], q["height"], q["fps"], q["subtitle_status"])
        with open(os.path.join(pkg_dir, "README.txt"), "w", encoding="utf-8") as f:
            f.write(readme)

        print("done %s (%d frames)" % (bvid, len(idx)), flush=True)
        summary.append({"ordinal": ordinal, "bvid": bvid, "frames": len(idx), "pkg": pkg_dir})

    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
