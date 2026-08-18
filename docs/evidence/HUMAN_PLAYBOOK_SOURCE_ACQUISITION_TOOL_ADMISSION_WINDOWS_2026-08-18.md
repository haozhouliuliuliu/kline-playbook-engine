# HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION — Windows 2026-08-18 evidence

> Date: 2026-08-18
> Scope: bounded real-Windows tool admission pilot for Human Playbook source acquisition
> Status: COMPLETE (bounded close-out; negative platform results are valid evidence)
> PM review: 2026-08-19 — accept local-media verification; platform 403/412 are capability limitations, not project blockers
> Authority: `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION.md`,
>   `RESEARCH_DIRECTION.md` (HUMAN_PLAYBOOK_FIRST), `CURRENT_STATE.md`
> This pilot is engineering verification only; it is NOT a research-protocol
> freeze, NOT strategy research, and does NOT unlock or evaluate any final-unseen
> data or authorize any paid commitment.

## 0. Conclusion

- video-to-skill overall = **CANDIDATE**
  - `LOCAL_MULTIMODAL_PIPELINE` = **VERIFIED** (local legal media + sidecar SRT probe passed)
  - `YOUTUBE_PUBLIC_URL_ADAPTER` = **NOT_VERIFIED / BLOCKED_BY_403_IN_CURRENT_ENVIRONMENT**
  - `BILIBILI_PUBLIC_URL_ADAPTER` = **NOT_VERIFIED / BLOCKED_BY_412_IN_CURRENT_ENVIRONMENT**
- book-to-skill = **DEFERRED / REFERENCE** (Skill-generation layer is not a current project need; Docling already covers layout/figure/table extraction)
- Docling = **VERIFIED** (scope: Windows Human Playbook document/layout extraction capability; NOT ADOPTED)
- video-transcribe-skill = **VERIFIED** (scope: local/offline Chinese no-caption transcription fallback; non-exact transcript, spot-check required)
- Recommended minimal combination:
  - Document path: **Docling**
  - Chinese no-caption fallback: **video-transcribe-skill**
  - Multimodal video evidence: **video-to-skill** kept CANDIDATE (local pipeline is a verified sub-capability; public URL acquisition is not a reliable project capability on this network)
  - book-to-skill: NOT a required minimal-combination component
- This pilot created no research-protocol freeze, no strategy extraction, no backtest, no final-unseen access, and no paid commitment.

## 1. Host environment (real Windows probe)

- OS: Windows (PowerShell 5.1 host)
- Python: 3.12.10 (`C:\Users\H\AppData\Local\Programs\Python\Python312\python.exe`)
- git: 2.54.0.windows.1
- FFmpeg: 9.0.1-essentials_build (www.gyan.dev), staged inside the pilot sandbox
  (isolated; NOT a machine-level/system install). `ffmpeg.exe` + `ffprobe.exe`
  at `%LOCALAPPDATA%\Temp\kline-playbook-hp-pilot\ffmpeg\bin\`.
- Isolation: all third-party clones, venvs, runtimes, media, model weights, and
  outputs live under `%LOCALAPPDATA%\Temp\kline-playbook-hp-pilot\` (outside the
  project repo). Nothing was installed globally (no system packages, no
  Skill/MCP/Plugin installation, no generated-authority Skills).
- Package index: default PyPI (`https://pypi.org/simple`) used for installs; it
  was measurably faster than a CN mirror for large wheels from this network.

## 2. Candidate pins (verified by `git rev-parse` / GitHub API)

| Candidate | Upstream | Pin | License | Python |
|---|---|---|---|---|
| video-to-skill | Lum1104/video-to-skill | `5e9f97e89855a8a0ea998ba85e179fbc1765d4b7` | MIT | >=3.11,<3.14 |
| book-to-skill | virgiliojr94/book-to-skill | `ed84a9f9eb79a21953c38c2740773135eedc31ab` | MIT | >=3.9 |
| Docling | docling-project/docling | `v2.120.3` (`46a1103b8c4adc6bbde1e30ec48fd0f7142d5600`) | MIT | >=3.10,<4.0 |
| video-transcribe-skill | UKplus8HRS/video-transcribe-skill | `377ca33e2d2738c75e9a320ccfe80c1569f712e8` | MIT | (faster-whisper) |

- Docling pinned to the official current stable release `v2.120.3` (published
  2026-08-18), NOT tracking `main`.
- book-to-skill cloned from the OFFICIAL repository `virgiliojr94/book-to-skill`;
  the unrelated malicious re-upload `Leutenegger/book-to-skill` (documented in
  the upstream `SECURITY-NOTICE.md`) was NOT used.

## 3. Static review summary (before execution)

- video-to-skill: YouTube/Bilibili/local source adapters all via yt-dlp
  (bounded: `-f bv*[height<=720]+ba`, caption writing); cookies strictly opt-in
  (default none); subprocesses launched without a shell; robust
  untrusted-input/security model (frame/OCR/URL/size caps, sanitized tool logs,
  fail-closed validation); CLI: `doctor`, `inspect`, `extract`, `query`,
  `contact-sheet`, `context`, `annotate`, `gaps`, `run`, `validate`, `clean`,
  `evaluate`, `evidence-bundle`.
- book-to-skill: deterministic extractors (pypdf / pdfminer / pdftotext; Docling
  in `--mode technical`; ebooklib/bs4/docx/striprtf); chapter/ToC detection
  including CJK/Thai/Korean; outputs `full_text.txt` + `metadata.json`; also
  generates Agent Skills (we do NOT install any generated Skill).
- Docling: layout/reading-order/table/figure extraction with markdown/JSON/HTML
  export; the standard PDF pipeline downloads layout/table/OCR models on first
  use from HuggingFace.
- video-transcribe-skill: Bilibili via public `api.bilibili.com` view+playurl
  APIs (no yt-dlp for Bilibili); YouTube/generic via yt-dlp; ffmpeg converts to
  16 kHz mono wav; local faster-whisper (cpu/int8); outputs timestamped
  `transcript.txt` + `metadata.json`.

## 4. Runtime dependencies actually installed

- video-to-skill venv (`v2s`): `video-to-skill 0.1.0` (editable), `yt-dlp 2026.7.4`,
  `onnxruntime 1.29.0`, `rapidocr 3.9.2`, `opencv-python 5.0.0.93`,
  `numpy 2.5.2`, `pillow 12.3.0`, `pydantic 2.13.4`, `typer 0.27.1`,
  `httpx 0.28.1`, etc. The `asr` extra (faster-whisper) was intentionally NOT
  installed in this venv; ASR coverage is handled by the `video-transcribe-skill`
  venv, and platform captions cover the transcript route.
- book-to-skill venv (`b2s`): `book-to-skill 1.4.0` (editable) with `pypdf`,
  `pdfminer.six`, `python-docx`, `striprtf`, `ebooklib`, `beautifulsoup4`,
  plus `reportlab` (used only to generate the self-authored probe document).
- Docling venv: `docling 2.120.3`, `docling-slim 2.120.3` (editable),
  `docling-core 2.91.0`, `docling-parse 7.14.0`, `docling-ibm-models 3.14.0`,
  `torch 2.13.0`, `torchvision 0.28.0`, `transformers 5.15.0`, `rapidocr 3.9.2`.
  (`import docling` = 2.120.3; `docling_parse` + `DocumentConverter` import OK.)
- video-transcribe venv (`vts`): `faster-whisper 1.2.1`, `ctranslate2 4.8.1`,
  `socksio 1.0.0`, `yt-dlp 2026.7.4`.
- All third-party packages installed from PyPI (default index; the TUNA mirror
  also measured faster but connection hangs were index-independent).

## 5. video-to-skill runtime diagnostics (`doctor`)

```
OK       python: 3.12.10
OK       ffmpeg: <sandbox>\ffmpeg\bin\ffmpeg.exe
OK       ffprobe: <sandbox>\ffmpeg\bin\ffprobe.exe
OK       yt-dlp: <sandbox>\venvs\v2s\Scripts\yt-dlp.exe
OPTIONAL local ASR: install `video-to-skill[asr]`   (intentional; covered by vts)
OK       local OCR: module 'rapidocr' available
OPTIONAL vision: hosted vision disabled (native multimodal host inspects contact sheets)
OK       workspace storage: 18.2 GiB free
```
- CLI entry point on Windows: `python -m video_to_skill` (the module
  `video_to_skill.cli` has no `__main__` guard; `__main__.py` calls `run()`).

## 6. Probe A — video-to-skill on public YouTube sample

Sample: `https://www.youtube.com/watch?v=0L6Rcgp6j7Y` — "Four Price Action Secrets
(The Ultimate Guide To Price Action)" by TradingLab, ~490s, upload 2021-10-22,
public, captions available (yt-dlp metadata).

- `inspect` (metadata/captions): **PASS** — yt-dlp resolved metadata, captions,
  chapters; UTF-8 output required (`PYTHONIOENCODING=utf-8`; Windows console GBK
  otherwise fails on emoji).
- `extract` (media download): **BLOCKED** — `HTTP Error 403: Forbidden` on the
  video media stream. Consistent across 3 tested public videos (`0L6Rcgp6j7Y`,
  `cP6xvs2I02s`, `5Y7XCkXf7fk`): yt-dlp can fetch metadata/API JSON, but the
  `googlevideo.com` media stream returns 403 without browser cookies (YouTube
  bot detection). This is a network/IP + no-cookie constraint, not a bug.
- No cookies/auth used (project red line); no player-client or other
  anti-bot circumvention attempted.
- **Result: YOUTUBE_PUBLIC_URL_ADAPTER = NOT_VERIFIED / BLOCKED_BY_403_IN_CURRENT_ENVIRONMENT.**
  Transcript/timestamps/frames/OCR full pipeline could not be exercised on a
  YouTube URL in this environment.

## 7. Probe B — video-to-skill on public Bilibili sample

Sample: `https://www.bilibili.com/video/BV1ckHGeJEbv/` — "期货纯新手交易app怎么用？第一期
手把手教学" by 农夫量化, duration 487s, 2024-08-30, public (official view API).

- video-to-skill uses yt-dlp for Bilibili; **yt-dlp's Bilibili extractor is
  blocked**: `HTTP Error 412: Precondition Failed` on the video webpage, both via
  video-to-skill and via direct yt-dlp (even with Referer/User-Agent headers).
  Bilibili search (`bilisearch`) and the raw search API also return 412/-412
  (anti-bot).
- **Bilibili official public API path WORKS**: `api.bilibili.com/x/web-interface/view`
  and playurl returned valid data (code 0) with a browser User-Agent and no
  cookies. This is exactly the path `video-transcribe-skill` uses (see Probe D).
- No cookies/auth used (project red line); no anti-bot circumvention attempted.
- **Result: BILIBILI_PUBLIC_URL_ADAPTER = NOT_VERIFIED / BLOCKED_BY_412_IN_CURRENT_ENVIRONMENT**
  for video-to-skill (yt-dlp route). Bilibili content acquisition remains
  possible only via the direct public API path (video-transcribe-skill).

## 8. Probe C — book-to-skill + Docling comparison

Input: a self-authored probe document (reportlab PDF + HTML) containing 4 chapters,
one table (risk parameters), and one embedded candlestick-style figure — content the
project owns, so processing is authorized.

| Capability | Simple extraction (pypdf / html-parser via book-to-skill) | Docling 2.120.3 |
|---|---|---|
| Chapters / section | 4 detected (numeric) | 4 detected, ordered |
| Table | flattened to text (no structure) | structured TableItem (count=1), cells retained |
| Figure / image | **silently dropped** (no reference, no warning) | structured PictureItem (count=1); figure reference + alt present in markdown |
| Reading order | preserved as linear text | preserved (layout-aware) |
| Silent visual loss | **YES (figure)** | NO |

Notes:
- book-to-skill `--mode text`: PDF used `pypdf` (pdftotext unavailable), HTML used
  `html-parser`; chapter/ToC detection worked; the figure was silently omitted with
  no warning (`images_dropped` is only meaningful for EPUB).
- Docling: markdown export retains chapter headings, table cells (500000 / contract
  multiplier / etc.), and figure reference + alt caption; lossless JSON shows
  `label=picture count=1` and `label=table count=1`.
- Docling needed the standard pipeline (torch + layout/table/OCR models); OCR models
  came from ModelScope; the layout model from HuggingFace (direct endpoint).
- No generated "author persona Skill" was created or installed.
- **Result: Docling = VERIFIED for Windows Human Playbook document/layout extraction;
  simple extraction silently loses figures.**

## 9. Probe D — video-transcribe-skill Chinese no-caption fallback

Sample: the same public Bilibili video (BV1ckHGeJEbv).

- **Bilibili direct API acquisition: PASS** — `get_bilibili_audio` downloaded
  `audio.m4s` (4,671,841 B) via the official view/playurl API (no cookies), ffmpeg
  converted to 16 kHz mono `audio.wav` (15,554,848 B).
- **faster-whisper (base, zh): PASS** — 260 timestamped segments, detected
  language zh, probability 1.000. Output `[start-end] text` per line.
- **Non-exact status**: this transcript is ASR output, not exact quotation; it must
  be spot-checked before any quotation claim.

### ≥20-point manual spot check (transcript-level review)

Method caveat: reviewer performed a transcript-level manual review against the
video's stated subject (futures-trading APP tutorial: 同花顺期货通 app, 螺纹钢
2410 / 玉米 2409 contracts, margin, stops). The reviewer could not play audio, so
this is a human-assisted text review, not an audio-listening check. All Whisper
text is treated as non-exact.

Key findings (timestamp → Whisper → assessment):

Numbers / dates — mostly correct:
- [192-196] `罗文钢2410` / `24就是2024年的意思` — number 2410/2024 OK; product name WRONG
- [196-199] `10就是10月份到期` — OK
- [210-213] `9月30号` — OK
- [219-221] `玉米2409` — product name + number OK
- [311-313] `是3500多` — OK (margin amount)
- [374-376] `价格是3255` — OK
- [384] `325加10个点嘛` — OK

Product / proper names — MAJOR homophone errors:
- [054-059] `下载这个左笑` — should be 同花顺 (ISSUE: proper name)
- [062-064] `通话说你期货通` — garbled 同花顺 (ISSUE)
- [083-086] `通话说` — 同花顺 mis-heard (ISSUE)
- [166-168] `就这个罗文钢` — should be 螺纹钢 (ISSUE: product name)
- [158-160] `包括齐旋` — should be 期权 (ISSUE: product/derivative term)

Trading terms — homophone errors:
- [107-110] `新手指蓝` — should be 新手指南 (ISSUE)
- [145-147] `模拟上号` — should be 模拟账号 (ISSUE)
- [243-245] `组织的合约` — likely 主力合约 (ISSUE)
- [272-274] `对手架` — likely 对手价 (ISSUE)
- [293-297] `新手架` / `手术` / `医手` — 新手价 / 手数 / 一手 (ISSUE)
- [302-305] `最低就是医手` — 一手 (ISSUE); negation `不能做零点几手` OK
- [307-309] `占用的保证经` — should be 保证金 (ISSUE)
- [335-338] `刮单` — should be 挂单 (ISSUE)
- [359-363] `指引之损` — should be 止损 (ISSUE)

Negation — preserved where present:
- [208-210] `是不能等到10月的` — 不能 correct
- [302-304] `它不能做零点几手的` — 不能 correct

Ambiguous / possible hallucination:
- [042-046] `开户还是吃饶的` — meaning unclear (ISSUE)
- [116-120] `你也许我` — likely 私信我 (ISSUE)

Timestamps: present on every segment; mostly contiguous with small gaps
(e.g., 140.00→143.00 missing); 260 segments over 487s (~1.9s average), i.e.,
fine-grained but very fragmented.

**Verdict: engineering-usable for a no-caption fallback, but NOT reliable for
Chinese trading vocabulary.** Critical product/term homophone errors (螺纹钢→罗文钢,
期权→齐旋, 同花顺→左笑, 保证金→保证经, 止损→指引之损, 挂单→刮单, 手数→手术,
一手→医手) mean trading terms must always be spot-checked/human-reviewed before
any playbook extraction. Numbers and dates were largely correct.

- **Result: video-transcribe-skill = VERIFIED for local/offline Chinese no-caption
  transcription fallback**, with the above accuracy caveats recorded.

## 10. Minimal combination recommendation

Converge on (do NOT adopt all four merely for coverage):

- **Document path: Docling** (VERIFIED; preserves layout/reading order/tables/
  figures; simple extraction silently drops figures).
- **Chinese no-caption fallback: video-transcribe-skill** (VERIFIED; Bilibili
  direct-API acquisition works; Chinese ASR usable but must be spot-checked).
- **Multimodal video evidence: video-to-skill** stays CANDIDATE — its local
  pipeline is a verified sub-capability, but public YouTube/Bilibili URL
  acquisition is blocked (403/412) on this network without cookies and cannot be
  a reliable project capability yet.
- **book-to-skill: not required** in the minimal combination (DEFERRED/REFERENCE).
  The project needs provenance-preserving document extraction; Docling covers the
  layout/figure/table core directly.

## 11. Network / auth behavior observed

- **No cookies/credentials used anywhere.** All requests were unauthenticated
  public access (GitHub, PyPI, HuggingFace, ModelScope, Bilibili public API,
  YouTube/Bilibili via yt-dlp without cookies). No browser-cookie decryption,
  no login, no paid API, no DRM/paywall bypass, no anti-bot circumvention
  (e.g., no `player_client` spoofing).
- **PyPI large-wheel behavior**: connection-hang phenomenon observed (pip
  connected to a Fastly edge `151.101.192.223` and stalled at zero bytes;
  socket timeout did not fire). Measured throughput: PyPI official ~2.2 MB/s,
  TUNA ~3.3 MB/s, Aliyun ~1 MB/s. Killing the stuck pip process and retrying
  succeeded (torch 122MB then installed; verified import). Root cause: a stuck
  single connection, not a fundamental network failure.
- **HuggingFace**: `hf-mirror.com` snapshot resolution intermittently failed
  (`LocalEntryNotFoundError`); direct `huggingface.co` worked (200/1.36s).
  Switching to direct HF completed the docling layout model (171MB safetensors)
  and faster-whisper model downloads.
- **ModelScope** (RapidOCR models): downloaded successfully (PP-OCRv6 det/rec,
  cls).
- **YouTube**: metadata/captions accessible; media stream 403 (no-cookie bot
  check). **Bilibili**: yt-dlp webpage/search 412; official view/playurl API 200.
- Current IP is NOT a pure domestic network (huggingface.co and YouTube both
  reachable), consistent with the recommendation NOT to switch to a domestic IP
  (which would block YouTube and would not fix the 403/412).

## 12. Limits and caveats

- **YouTube media download (403) and Bilibili yt-dlp path (412)** are recorded as
  valid negative engineering evidence and as `KNOWN_LIMITATION` / capability
  limitations for this environment, NOT project blockers. Not attempting to
  circumvent platform access controls is a deliberate project safety boundary.
- video-to-skill `LOCAL_MULTIMODAL_PIPELINE` (VERIFIED) caveats:
  - OCR text quality is imperfect even on clean synthetic text
    (`BUY SIGNAL` exact at t=0, conf 0.99; `SELL SIGNAL`→`SELL SIGNACI`;
    `HOLD`→`LD`). OCR text must be treated as evidence, not exact.
  - Visual sampling coverage varies (default 30s periodic + scene changes; some
    time windows have no frame; denser 10s periodic improved but did not fully
    cover all windows).
  - Binding mechanism verified: at t=0 the caption "buy signal" and the frame OCR
    "BUY SIGNAL" align (source ID `local-6ba91aca…`, frames + visual-retention
    inventory + query/context retrieval).
- video-transcribe-skill: transcript is non-exact; Chinese trading terms need
  spot-check; Bilibili API / yt-dlp behavior can drift.
- Docling: requires the heavy standard stack (torch + models) even for a simple
  document; acceptable when figures/tables/layout matter, overkill for
  prose-only text. Not ADOPTED — only VERIFIED for the scoped capability.
- Bilibili official CC subtitles were unavailable for the sample video
  (subtitle list empty), so the vts spot check is transcript-level review rather
  than a CC-aligned cross-check.
- All clones/venvs/model weights/media live under the sandbox
  `%LOCALAPPDATA%\Temp\kline-playbook-hp-pilot`; nothing is committed to the repo.
- Cleanup: delete the sandbox directory after evidence is recorded; no raw media,
  venvs, model weights, cookies, credentials, or third-party clones are committed.

## 13. Cleanup path

- Sandbox root: `%LOCALAPPDATA%\Temp\kline-playbook-hp-pilot` (clones, venvs,
  media, model caches, logs, outputs). Remove this directory after the evidence
  is recorded; nothing in it is committed.
- Not committed: raw media, venvs, model weights, cookies, credentials,
  third-party repo clones, generated Skills, full transcripts of copyrighted
  sources. The evidence file records only sparse provenance anchors.
- Repository changes for this package are limited to the evidence file, the
  admission research doc, `CURRENT_STATE.md`, and `00_READ_FIRST.md` as needed.
