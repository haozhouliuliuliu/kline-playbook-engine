#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Corpus acceptance + subtitle inventory + analysis queue builder for
kline-playbook-engine JiangHe trader corpus.

Pure mechanical verification. Does NOT analyze content.
Outputs (written into D:/江河交易员/manifests):
  corpus_acceptance.jsonl
  corpus_acceptance.csv
  analysis_queue.jsonl
  analysis_queue.csv
"""
import csv
import glob
import hashlib
import json
import os
import re
import subprocess

FFPROBE = "C:/Users/H/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg.Shared_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.1-full_build-shared/bin/ffprobe.exe"
MEDIUM_ROOT = "D:/江河交易员"
MANIFESTS = os.path.join(MEDIUM_ROOT, "manifests")
MEDIA = os.path.join(MEDIUM_ROOT, "media")
SUBTITLES = os.path.join(MEDIUM_ROOT, "subtitles")

SOURCE_MANIFEST = os.path.join(MANIFESTS, "source_manifest.jsonl")
CORPUS_MANIFEST = os.path.join(MANIFESTS, "corpus_manifest.jsonl")

FRAGMENT_RE = re.compile(r"\.f\d+\.mp4$", re.IGNORECASE)


def load_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe(path):
    cmd = [
        FFPROBE, "-v", "error",
        "-show_entries", "stream=index:stream=codec_type:stream=codec_name:stream=width:stream=height:stream=avg_frame_rate:stream=r_frame_rate",
        "-show_entries", "format=duration",
        "-of", "json", path,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def parse_fps(v):
    try:
        a, b = v.split("/")
        a, b = float(a), float(b)
        return round(a / b, 4) if b else None
    except Exception:
        return None


def find_media_for_bvid(bvid):
    hits = [h for h in glob.glob(os.path.join(MEDIA, "*%s*.mp4" % bvid)) if not FRAGMENT_RE.search(os.path.basename(h))]
    return hits[0] if hits else None


def find_subtitle_for_bvid(bvid):
    hits = glob.glob(os.path.join(SUBTITLES, "*%s*.srt" % bvid))
    return hits[0] if hits else None


def main():
    sources = load_jsonl(SOURCE_MANIFEST)
    corpus_records = {r["bvid"]: r for r in load_jsonl(CORPUS_MANIFEST)}

    seen = {}
    duplicates = set()
    for s in sources:
        b = s.get("bvid")
        if b in seen:
            duplicates.add(b)
        else:
            seen[b] = s.get("ordinal")

    enumerated = len(sources)
    acceptance = []
    sub_counter = {"NATIVE": 0, "BURNED_IN_ONLY": 0, "NONE_NEEDS_ASR": 0, "UNKNOWN": 0}
    local_available = 0
    corrupt = 0
    unavailable_paid = 0
    accepted = 0

    for s in sources:
        bvid = s.get("bvid")
        ordinal = s.get("ordinal")
        title = s.get("title", "")
        upload_date = s.get("upload_date", "")
        media_path = find_media_for_bvid(bvid)
        sub_path = find_subtitle_for_bvid(bvid)
        meta_path = corpus_records.get(bvid, {}).get("metadata_path")

        rec = {
            "ordinal": ordinal,
            "bvid": bvid,
            "title": title,
            "upload_date": upload_date,
            "local_video_path": media_path,
            "subtitle_path": sub_path,
            "metadata_path": meta_path,
            "source_status": "AVAILABLE",
            "subtitle_status": "UNKNOWN",
            "corrupt": False,
            "duplicate_bvid": bvid in duplicates,
            "checks": {},
        }

        if not media_path:
            rec["source_status"] = "UNAVAILABLE_PAID_GATED"
            rec["subtitle_status"] = "UNKNOWN"
            unavailable_paid += 1
            sub_counter["UNKNOWN"] += 1
            acceptance.append(rec)
            continue

        if not os.path.exists(media_path) or os.path.getsize(media_path) == 0:
            rec["corrupt"] = True
            rec["checks"] = {"exists": os.path.exists(media_path), "nonzero": os.path.exists(media_path) and os.path.getsize(media_path) > 0}
            corrupt += 1
            acceptance.append(rec)
            continue

        info = ffprobe(media_path)
        if info is None:
            rec["corrupt"] = True
            rec["checks"] = {"exists": True, "nonzero": True, "ffprobe_readable": False}
            corrupt += 1
            acceptance.append(rec)
            continue

        vstream = None
        astream = None
        for st in info.get("streams", []):
            ct = st.get("codec_type")
            if ct == "video" and vstream is None:
                vstream = st
            elif ct == "audio" and astream is None:
                astream = st
        duration = None
        if info.get("format", {}).get("duration"):
            try:
                duration = float(info["format"]["duration"])
            except Exception:
                duration = None

        checks = {
            "exists": True,
            "nonzero": True,
            "ffprobe_readable": True,
            "video_stream": vstream is not None,
            "audio_stream": astream is not None,
            "duration_ok": duration is not None and duration > 0,
        }
        if not (vstream and astream and duration):
            rec["corrupt"] = True
            rec["checks"] = checks
            corrupt += 1
            acceptance.append(rec)
            continue

        rec.update({
            "video_sha256": sha256_of(media_path),
            "width": vstream.get("width"),
            "height": vstream.get("height"),
            "fps": parse_fps(vstream.get("avg_frame_rate") or vstream.get("r_frame_rate") or "0/1"),
            "video_codec": vstream.get("codec_name"),
            "audio_codec": astream.get("codec_name"),
            "duration_seconds": round(duration, 3),
            "checks": checks,
        })

        if sub_path and os.path.exists(sub_path):
            rec["subtitle_status"] = "NATIVE"
            sub_counter["NATIVE"] += 1
        else:
            rec["subtitle_status"] = "NONE_NEEDS_ASR"
            sub_counter["NONE_NEEDS_ASR"] += 1

        rec["checks"]["metadata_path_exists"] = bool(meta_path) and os.path.exists(meta_path)

        local_available += 1
        if not rec["corrupt"]:
            accepted += 1
        acceptance.append(rec)

    with open(os.path.join(MANIFESTS, "corpus_acceptance.jsonl"), "w", encoding="utf-8") as f:
        for rec in acceptance:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    cols = ["ordinal", "bvid", "title", "upload_date", "source_status", "subtitle_status",
            "local_video_path", "subtitle_path", "metadata_path", "video_sha256",
            "width", "height", "fps", "video_codec", "audio_codec", "duration_seconds",
            "corrupt", "duplicate_bvid"]
    with open(os.path.join(MANIFESTS, "corpus_acceptance.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for rec in acceptance:
            w.writerow({k: rec.get(k) for k in cols})

    avail = [r for r in acceptance if r["source_status"] == "AVAILABLE" and not r["corrupt"]]
    avail.sort(key=lambda r: (r.get("upload_date") or ""))
    queue = []
    for i, r in enumerate(avail, 1):
        queue.append({
            "analysis_ordinal": i,
            "bvid": r["bvid"],
            "title": r["title"],
            "upload_date": r["upload_date"],
            "duration_seconds": r["duration_seconds"],
            "local_video_path": r["local_video_path"],
            "video_sha256": r["video_sha256"],
            "width": r["width"],
            "height": r["height"],
            "fps": r["fps"],
            "subtitle_status": r["subtitle_status"],
            "subtitle_path": r["subtitle_path"],
            "source_status": r["source_status"],
            "analysis_status": "PENDING",
        })
    for r in [x for x in acceptance if x["source_status"] == "UNAVAILABLE_PAID_GATED"]:
        queue.append({
            "analysis_ordinal": None,
            "bvid": r["bvid"],
            "title": r["title"],
            "upload_date": r["upload_date"],
            "duration_seconds": None,
            "local_video_path": None,
            "video_sha256": None,
            "width": None,
            "height": None,
            "fps": None,
            "subtitle_status": r["subtitle_status"],
            "subtitle_path": r["subtitle_path"],
            "source_status": "UNAVAILABLE_PAID_GATED",
            "analysis_status": "PENDING",
        })

    with open(os.path.join(MANIFESTS, "analysis_queue.jsonl"), "w", encoding="utf-8") as f:
        for q in queue:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    qcols = ["analysis_ordinal", "bvid", "title", "upload_date", "duration_seconds",
             "local_video_path", "video_sha256", "width", "height", "fps",
             "subtitle_status", "subtitle_path", "source_status", "analysis_status"]
    with open(os.path.join(MANIFESTS, "analysis_queue.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=qcols)
        w.writeheader()
        for q in queue:
            w.writerow(q)

    print(json.dumps({
        "ENUMERATED": enumerated,
        "LOCAL_AVAILABLE": local_available,
        "UNAVAILABLE_PAID_GATED": unavailable_paid,
        "CORRUPT": corrupt,
        "DUPLICATE_BVID": len(duplicates),
        "ACCEPTED_FOR_RESEARCH": accepted,
        "NATIVE_SUBTITLE_COUNT": sub_counter["NATIVE"],
        "BURNED_IN_ONLY_COUNT": sub_counter["BURNED_IN_ONLY"],
        "NONE_NEEDS_ASR_COUNT": sub_counter["NONE_NEEDS_ASR"],
        "UNKNOWN_SUBTITLE_COUNT": sub_counter["UNKNOWN"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
