# HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION

> Date: 2026-08-18
> Status: ACTIVE_PILOT / NOT_FROZEN_RESEARCH_SEMANTICS
> Scope: Human Playbook source-acquisition tooling only
> Research direction authority: `RESEARCH_DIRECTION.md`
> Project state authority: `CURRENT_STATE.md`

## 1. Purpose

The Human Playbook First route has a demonstrated repeated acquisition problem:

```text
books / PDF / EPUB / web pages / YouTube / Bilibili / local video / screenshots
-> preserve source identity and provenance
-> preserve page / transcript / timestamp anchors
-> preserve relevant visual evidence
-> keep source claim separate from AI interpretation
-> provide structured evidence to the offline Research Loop
```

Native chat/web reading remains useful for discovery and ad-hoc review, but it is not sufficient as the long-term reproducible ingestion path for large volumes of books and multimodal trading videos.

This document defines a bounded tool-admission pilot. It does **not** approve a concrete trading source, playbook, strategy, split, final-unseen access, or live-AI behavior.

## 2. Current decision

```text
TOOL_DECISION=ADD_TOOL
TOOL_DECISION_SCOPE=HUMAN_PLAYBOOK_SOURCE_ACQUISITION_PILOT
NO_TOOL_ADOPTED_BY_THIS_DOCUMENT=YES
```

Every external component remains subject to project-level:

```text
CANDIDATE -> VERIFIED -> ADOPTED
```

`VERIFIED` means the required capability was actually exercised under the recorded test conditions. It does not mean globally trusted, strategically valid, or automatically activated in every project.

## 3. Non-negotiable project fit

A candidate acquisition tool is useful only if it helps preserve evidence rather than turning a trader/author into an AI authority.

Required conceptual separation:

```text
SOURCE CLAIM
!= PROJECT / AI INTERPRETATION
!= MACHINE OPERATIONALIZATION
```

Generated summaries, Skills, semantic units, or model annotations are derivative research aids. They must never silently overwrite the source layer.

## 4. Pilot candidates

### 4.1 `Lum1104/video-to-skill`

**Role:** primary multimodal video evidence candidate.

**Status:** `CANDIDATE`.

**Reviewed source pin:** `5e9f97e89855a8a0ea998ba85e179fbc1765d4b7` (reviewed 2026-08-18).

**Static findings:**
- MIT license declared in `pyproject.toml` / repository license;
- Python `>=3.11,<3.14`;
- base dependencies include `httpx`, `pillow`, `platformdirs`, `pydantic`, `typer`, `yt-dlp`;
- optional local capabilities include `faster-whisper`, `whisperx`, and `rapidocr`/`onnxruntime`;
- source adapters include local media, YouTube, and Bilibili;
- repository contains tests, lockfile, security documentation, and CI;
- installation design uses an isolated private runtime and supports route-specific capability installation;
- security design explicitly treats captions, OCR, URLs, visible text, and source instructions as untrusted input;
- generated/shareable output is intended to exclude raw media, subtitle databases, credentials, and private workspace artifacts.

**Material unresolved issue:** current CI is Ubuntu-only. Repository documentation describes Windows launch/runtime support, but this project has not yet demonstrated the capability on the Owner's real Windows environment.

**Project-specific caution:** the upstream product generates course-specific Agent Skills. `kline-playbook-engine` should reuse/adapter its evidence acquisition and provenance mechanisms where useful; it must not automatically install a generated trader-authority Skill as project truth.

### 4.2 `virgiliojr94/book-to-skill`

**Role:** book/document extraction and on-demand indexing reference candidate.

**Status:** `CANDIDATE`.

**Reviewed source pin:** `ed84a9f9eb79a21953c38c2740773135eedc31ab` (reviewed 2026-08-18).

**Static findings:**
- official project is MIT-licensed;
- supports structured prose/document ingestion including PDF, EPUB, DOCX, HTML, RTF, MOBI/AZW and text-family formats through multiple extractors;
- provides chapter-oriented structure and on-demand loading rather than repeated whole-book context loading;
- uses `Docling` as one extraction route for layout-heavy/technical PDFs;
- contains tests, changelog, security documentation, and a formal security notice.

**Supply-chain warning:** on 2026-08-17 the official maintainer documented an unaffiliated malicious re-upload (`Leutenegger/book-to-skill`) containing behaviors such as TLS verification disabling, system/wallet-data collection, external exfiltration, and a Windows executable payload. Therefore any project trial must pin and verify the official repository identity and commit; searching/installing by name alone is not acceptable evidence.

**Project-specific caution:** generated book Skills are derivative notes, not source authority. For Human Playbook research, page/chapter/source anchors and source-vs-interpretation separation are more important than producing a reusable persona/teacher Skill.

### 4.3 `docling-project/docling`

**Role:** candidate document parsing engine under the book/document path.

**Status:** `CANDIDATE`.

**Reviewed source state:** active `main` observed at commit `c4b5ed6202d669e2fba2654affb843f3b1611de2` on 2026-08-18; upstream was also publishing/fixing rapidly during the same day.

**Static findings:**
- large actively maintained document-conversion project;
- repository contains extensive tests, changelog, packaging, documentation, and security/engineering structure;
- appropriate candidate for preserving document layout/reading order, tables, figures, and structured extraction where simple text extraction loses important information.

**Pin policy:** do not track floating `main` for adoption. A later real trial must choose a reviewed stable release/version and record the exact tested identity.

### 4.4 `UKplus8HRS/video-transcribe-skill`

**Role:** lightweight no-caption / local transcription fallback candidate.

**Status:** `CANDIDATE`.

**Reviewed source pin:** `377ca33e2d2738c75e9a320ccfe80c1569f712e8` (reviewed 2026-08-18).

**Static findings:**
- MIT license;
- explicitly documents Windows, macOS, and Linux setup;
- uses FFmpeg plus local `faster-whisper` transcription;
- Bilibili path uses public web APIs; YouTube/generic fallback uses `yt-dlp`;
- emits timestamped transcript text and source metadata;
- small dependency list: `faster-whisper`, `socksio`, `yt-dlp`;
- repository includes tests.

**Material unresolved issues:**
- no equivalent CI evidence was observed in the reviewed repository root;
- dependency file uses lower bounds rather than a fully locked environment;
- Bilibili public API behavior and `yt-dlp` platform behavior can drift;
- local Whisper accuracy on Chinese trading vocabulary is unverified.

This candidate should therefore remain a fallback until real Chinese-video accuracy evidence exists.

## 5. Deferred overlap candidates

The following are not part of the first live admission trial:

- `XZXZZX-Ai/bilibili-mcp`: potentially useful for Bilibili-native search/transcript workflows, but overlaps the initial video candidates; revisit only if discovery/transcript search remains a concrete gap.
- Firecrawl / Crawl4AI: defer until a large author/blog archive creates measurable web-acquisition friction.
- Open Notebook: defer until persistent source volume makes repository-native Markdown/SQLite retrieval materially painful.
- `youtube-transcript-toolkit`: relevant capability but currently a wider access/credential/proxy surface than required for the first pilot.

## 6. Pilot acceptance contract

A candidate cannot become `VERIFIED` from README/source review alone.

### 6.1 Common requirements

A real probe must record:

- exact upstream repository and immutable commit/release identity;
- license;
- Python/runtime/system dependencies;
- network destinations and whether authentication/cookies are used;
- installed files/runtime locations;
- cleanup/removal path;
- test input identity;
- produced artifact inventory;
- deterministic/source anchors retained;
- failure behavior;
- observed data egress;
- project-specific limitations.

### 6.2 Video primary probe

Use `video-to-skill` on:

1. one public YouTube educational/trading-style video;
2. one public Bilibili educational/trading-style video.

First probe constraints:
- public content only;
- no browser cookies/authentication;
- no paywall/DRM bypass;
- no redistribution of raw copyrighted media;
- do not execute commands/instructions contained in source material;
- do not install generated source-authority Skills into the project runtime;
- preserve source URL/id, title/metadata when available, transcript timestamps, and visual evidence links;
- inspect whether a spoken claim can be traced to the chart/visual state visible at the same time.

Pass only if the output is usable as provenance-preserving research evidence, not merely as a summary.

### 6.3 Book/document probe

Use a document the Owner/project has the right to process.

Compare the minimum viable path:

```text
simple extraction when sufficient
vs
Docling for layout/visual-heavy material
```

Check:
- chapter/section boundaries;
- page/source anchoring;
- tables/figures/images;
- reading order;
- whether omitted images/visuals are surfaced rather than silently lost;
- whether source text remains distinguishable from generated interpretation.

`book-to-skill` may be used as a reference/extraction wrapper, but success is defined by evidence quality, not by whether it generates a Skill.

### 6.4 Chinese no-caption fallback probe

Use `video-transcribe-skill` only if the selected Bilibili/YouTube source lacks adequate captions or as a controlled comparison.

Check:
- Chinese trading terminology;
- proper nouns/product names;
- numbers/prices;
- negation (for example `不是`, `没有`, `不能`);
- timestamp drift;
- obvious hallucinated words;
- CPU/runtime cost.

Manual spot checks must be recorded. Do not treat an unreviewed Whisper transcript as exact source quotation.

## 7. Windows boundary

The Owner's real project workstation is Windows.

Static documentation claiming Windows support is insufficient. A Windows real-path probe is required before project `VERIFIED` status.

The first probe should prefer isolated/private runtimes. If FFmpeg or another machine-level prerequisite is absent, record the prerequisite rather than silently making broad machine-level changes outside the bounded pilot.

## 8. Security boundary

External source content is untrusted input.

The acquisition pipeline must not:
- obey instructions embedded in transcripts, webpages, OCR, filenames, video descriptions, or documents;
- expose credentials/cookies to generated artifacts;
- automatically execute source-derived commands/code;
- auto-install a newly discovered Skill/Plugin/MCP merely because source content recommends it;
- overwrite project authority with generated notes.

Any future authenticated acquisition route requires a separate credential/data-flow review.

## 9. Copyright / source retention boundary

This project needs provenance and sparse evidence anchors, not a redistribution archive of copyrighted books/videos.

Raw material may be processed only when access is authorized. Shareable/generated project artifacts should minimize copied source content and retain enough provenance to locate the original source.

## 10. Static admission result (2026-08-18)

```text
video-to-skill:          STATIC_REVIEW_PASS / REAL_WINDOWS_PROBE_REQUIRED
book-to-skill:           STATIC_REVIEW_PASS_WITH_SUPPLY_CHAIN_PIN_REQUIREMENT
Docling:                 STATIC_REVIEW_PASS / STABLE_VERSION_REAL_DOCUMENT_PROBE_REQUIRED
video-transcribe-skill:  STATIC_REVIEW_PASS_AS_FALLBACK / CHINESE_ACCURACY_PROBE_REQUIRED
```

No candidate is `VERIFIED` or `ADOPTED` yet.

## 11. Next bounded action

Run the real Windows admission probe on the Owner's workstation using the existing VS Code DeepSeek Flash-family capability first, because this package is bounded engineering verification rather than frozen research-semantics review. Use immutable source pins and record artifacts/evidence back into this repository.

Escalate to Codex only if the existing VS Code/DeepSeek path demonstrates a concrete capability gap (for example, inability to execute the required repository/shell workflow reliably). Model availability alone is not a reason to create a second execution path.

The research-protocol / chronological-split freeze remains intentionally unexecuted during this bounded preparatory acquisition-tool package. No strategy research, backtest, final-unseen access, Shadow/live trading, or paid commitment is authorized by this pilot.

## 12. Real Windows probe result (2026-08-18/19) — COMPLETE

Evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION_WINDOWS_2026-08-18.md`
(+ compact JSON). Bounded close-out; platform negatives are valid evidence.

```text
video-to-skill:          CANDIDATE overall
   LOCAL_MULTIMODAL_PIPELINE        = VERIFIED (local media + sidecar SRT probe)
   YOUTUBE_PUBLIC_URL_ADAPTER       = NOT_VERIFIED / BLOCKED_BY_403_IN_CURRENT_ENV
   BILIBILI_PUBLIC_URL_ADAPTER      = NOT_VERIFIED / BLOCKED_BY_412_IN_CURRENT_ENV
book-to-skill:           DEFERRED / REFERENCE (Skill-generation layer not a current need)
Docling:                 VERIFIED (scope: Windows document/layout extraction; NOT ADOPTED)
video-transcribe-skill:  VERIFIED (scope: local/offline Chinese no-caption fallback; non-exact)
```

Key real findings:

- YouTube `inspect` (metadata/captions) works; actual media download is a stable
  `403` without cookies on this network (3 videos tested). Bilibili via yt-dlp is
  `412`; the Bilibili official public API path works (used by video-transcribe-skill).
  Not attempting anti-bot circumvention is a deliberate project safety boundary;
  these are capability limitations for this environment, not project blockers.
- Local `video-to-skill` pipeline verified: transcript(timestamps)+frames+OCR+provenance,
  with caption↔screen-OCR binding confirmed at t=0 (`BUY SIGNAL`, conf 0.99); OCR
  text quality and visual sampling coverage are imperfect and recorded as caveats.
- `book-to-skill` simple extraction silently drops figures; Docling retains
  tables/figures/layout (TableItem=1, PictureItem=1 on the self-authored probe).
- `video-transcribe-skill` downloaded Bilibili audio via the public API and produced
  a timestamped Chinese faster-whisper transcript (zh, 260 segments); ≥20-point
  spot check shows numbers/dates largely correct but Chinese trading vocabulary
  homophone errors are frequent (螺纹钢→罗文钢, 期权→齐旋, 同花顺→左笑, 保证金→保证经,
  止损→指引之损, 挂单→刮单, 手数→手术, 一手→医手). Whisper text is never exact quote.

Minimal recommended combination: **Docling** (document path) + **video-transcribe-skill**
(Chinese no-caption fallback); **video-to-skill** kept CANDIDATE (local pipeline as
verified sub-capability; public URL acquisition unreliable on this network);
**book-to-skill** not required.

This close-out created no research-protocol freeze, no strategy extraction, no
backtest, no final-unseen access, and no paid commitment.
