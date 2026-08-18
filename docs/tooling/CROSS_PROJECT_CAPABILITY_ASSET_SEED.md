# CROSS_PROJECT_CAPABILITY_ASSET_SEED

> Date: 2026-08-18
> Status: PROJECT-LOCAL DURABLE SEED / NOT A CROSS-PROJECT AUTHORITY REPLACEMENT
> Purpose: Preserve the Owner-approved direction to treat reusable Skills, Plugins, MCP servers, frameworks, research tools, and capability patterns as a durable information asset across projects.
>
> Authority boundary: This file records durable project knowledge and candidate/tool-discovery design. It does not automatically install, approve, adopt, or activate any tool. `TOOL_REGISTRY.md`, project authority, actual config/lockfiles/runtime, and the normal CANDIDATE -> VERIFIED -> ADOPTED/APPROVED process remain authoritative.

## 1. Owner direction recorded

The Owner wants reusable capability knowledge to become a long-term cross-project asset rather than being repeatedly rediscovered in chat.

The intended asset is broader than a list of repository names. Preserve:

```text
DURABLE CAPABILITY PATTERN
-> candidate implementations
-> source / provenance
-> maintenance / release state
-> permissions / network / dependency risks
-> overlap with existing capabilities
-> verification evidence
-> adoption / defer / reject decision
-> replacement / supersession relation
-> revalidation trigger
```

Example:

```text
Capability: timestamped video evidence extraction
Today candidate: video-to-skill
Future candidate: <newer implementation>
Decision should compare the implementations rather than treating the first discovered repo as permanent.
```

This distinction is important because capability needs are relatively durable while concrete tools, model integrations, repositories, APIs, versions, and maintainers are volatile.

## 2. Canonical storage direction

Preferred long-term structure:

1. **Git repository = canonical versioned asset store.**
   - Markdown / JSON / YAML as appropriate.
   - Git history preserves decisions, source identities, replacement history, and review evidence.
   - Machine-readable records may later support automated discovery and filtering.

2. **Obsidian = optional human-facing knowledge interface.**
   - Useful for browsing local Markdown, links, tags, and relationships.
   - It should not become the sole authority or a proprietary database dependency.
   - A local clone of the canonical Git asset repository can be opened directly as an Obsidian vault.
   - Paid Obsidian Sync is optional and requires the normal paid-service Owner gate before adoption.

3. **Project repositories = project-local activation truth.**
   - A tool appearing in the cross-project catalog does not mean a project uses it.
   - Actual project config, lockfiles, installed components, and runtime remain the truth for enabled versions.

## 3. Discovery-to-adoption lifecycle

Recommended simple lifecycle for reusable tooling knowledge:

```text
DISCOVERED
-> CANDIDATE
-> VERIFIED
-> ADOPTED / APPROVED for a stated role
or
-> DEFERRED / REJECTED / RETIRED
```

The cross-project `TOOL_REGISTRY.md` status vocabulary remains binding where applicable. Discovery feeds the registry; it must not bypass it.

Popularity signals such as GitHub stars, stars/day, forks, downloads, mentions, or marketplace rank are **discovery signals only**, never quality or safety proof.

## 4. Weekly capability scout concept

Future bounded automation candidate: `CAPABILITY_SCOUT_WEEKLY`.

Goal: surface high-velocity reusable AI/software capabilities before they become widely known, then preserve only the useful subset.

Suggested weekly acquisition lanes:

- GitHub Trending (weekly/monthly);
- GitHub Search API and ecosystem-specific searches;
- OSS Insight trending / stars-velocity data;
- Agent Skills / skills.sh ecosystems;
- MCP registries / agent registries;
- official framework/plugin marketplaces;
- PyPI / npm / Hugging Face / model-tool ecosystems when relevant;
- Hacker News / technical blogs / release notes as secondary discovery signals;
- curated awesome lists only as discovery, never as evidence.

Suggested first-pass volume:

```text
collect top ~50-100 high-velocity candidates/week
-> deduplicate
-> classify by capability
-> discard obvious duplicates / abandoned / irrelevant / unsafe items
-> compare against existing registry capabilities
-> promote only a small useful subset to CANDIDATE records
```

Do not auto-install or auto-adopt from this pipeline.

## 5. Minimal candidate record

A future machine-readable record should be able to answer:

```text
NAME
CAPABILITY_CLASS
ROLE
STATUS
SOURCE_URL / REPOSITORY
SOURCE_IDENTITY / PIN_POLICY
LICENSE
LAST_CHECKED
MAINTENANCE_SIGNAL
ACTIVATE_WHEN
INPUT / OUTPUT SURFACES
NETWORK / AUTH / DATA_EGRESS
DEPENDENCIES
MATERIAL_RISKS
OVERLAP
REPLACES / REPLACED_BY
EVIDENCE
DECISION
REVALIDATE_WHEN
REMOVE
```

Avoid large speculative metadata schemas until real use proves the need.

## 6. Human Playbook acquisition capability gap

Current project-specific need that triggered this asset work:

```text
books + PDFs + EPUBs + websites + YouTube + Bilibili + local video + screenshots
-> preserve provenance
-> preserve transcript/page/timestamp anchors
-> preserve relevant visual evidence
-> structure content for Human Playbook research
-> keep source claim separate from AI interpretation
```

This is a demonstrated capability gap. Current stage decision is `ADD_TOOL`, but individual candidates below remain unverified unless explicitly stated otherwise.

## 7. Current candidate set discovered on 2026-08-18

### 7.1 `Lum1104/video-to-skill`

**Capability:** multimodal video/course evidence acquisition and structured skill generation.

**Status:** `CANDIDATE`.

**Why relevant:**
- supports video / playlist / course inputs;
- supports YouTube, Bilibili, and local media paths;
- aligns transcript, chapters, scene changes, OCR, and visual states;
- retains timestamped provenance/evidence;
- designed to keep raw media/evidence private rather than embedding it wholesale in generated Skills;
- explicitly treats captions/OCR/video text as untrusted content.

**Project fit:** Very high for future Human Playbook video claim extraction, especially where spoken explanation must remain linked to the chart visible at that time.

**Risks / checks before verification:**
- third-party dependencies and runtime downloads;
- ffmpeg / yt-dlp / local ASR/OCR paths;
- browser-cookie handling if authentication is enabled;
- copyright / platform terms;
- generated "Skill" semantics may be too strong for this project unless adapted into evidence dossiers rather than source-authority agents.

**Next evidence needed:** bounded Windows/local probe on one public YouTube video and one public Bilibili video.

### 7.2 `virgiliojr94/book-to-skill`

**Capability:** books/document collections -> structured on-demand Agent Skill.

**Status:** `CANDIDATE`.

**Why relevant:**
- PDF, EPUB, DOCX, HTML, RTF, MOBI/AZW and text-family support;
- chapter-oriented extraction;
- glossary/pattern/index outputs;
- explicitly designed to avoid repeatedly loading the whole book into model context;
- local document extraction paths.

**Project fit:** High as a reference design for chapter-level extraction and on-demand retrieval.

**Caution:** The project should not automatically turn a trader's book into a trader-authority Skill. Prefer adapting the extraction/indexing mechanics into provenance-preserving source evidence.

**Next evidence needed:** local probe using a document the Owner has rights to process; inspect page/chapter anchors and visual/table loss.

### 7.3 `docling-project/docling`

**Capability:** unified document parsing / conversion for complex documents.

**Status:** `CANDIDATE` for this project stage; externally mature enough to deserve priority evaluation, but not project-adopted by this record.

**Why relevant:** potential common ingest layer for PDF/EPUB/HTML/image/document sources, especially layout-heavy PDFs, tables, figures, reading order, and structured conversion.

**Overlap:** may serve as the extraction engine under book-oriented pipelines rather than requiring an entire book-to-skill workflow.

**Next evidence needed:** bounded real-document conversion quality test against the project's source-dossier requirements.

### 7.4 `XZXZZX-Ai/bilibili-mcp`

**Capability:** Bilibili discovery/transcript/search integration via MCP.

**Status:** `CANDIDATE`.

**Why relevant:** Chinese Human Playbook discovery will need Bilibili-native source handling and timestamp-oriented transcript search.

**Risks:** community project provenance/maintenance, platform/API behavior, authentication/data egress, MCP permission surface.

**Next evidence needed:** source review plus bounded public-video read-only probe.

### 7.5 `UKplus8HRS/video-transcribe-skill`

**Capability:** local/offline-oriented media transcription fallback.

**Status:** `CANDIDATE`.

**Why relevant:** videos without usable platform captions still need timestamped transcripts; local Whisper-style transcription can avoid an external transcription API.

**Risks:** model/runtime size, Chinese ASR accuracy, compute cost, ffmpeg dependencies, timestamps/segmentation quality.

**Next evidence needed:** short Chinese trading-video transcription benchmark with known manual spot-checks.

### 7.6 `firecrawl/skills` / Firecrawl

**Capability:** web search, scrape, crawl, structured extraction / acquisition Skills.

**Status:** `DEFERRED` in the existing cross-project registry; now has a real Human Playbook activation condition but should remain deferred until native/manual acquisition becomes a measurable bottleneck.

**Potential trigger:** large author/blog archives, JS-heavy sites, or repeated structured web acquisition that cannot be handled efficiently by existing web access.

### 7.7 `unclecode/Crawl4AI`

**Capability:** open-source web crawling and LLM-oriented Markdown extraction.

**Status:** `CANDIDATE` for future comparison against Firecrawl when large-scale web acquisition activates.

**Why relevant:** potentially more local/self-hosted path for blog/archive ingestion.

**Decision:** Do not add both Firecrawl and Crawl4AI now. Compare only when the real workload activates.

### 7.8 `lfnovo/open-notebook`

**Capability:** local-first multi-source research notebook / NotebookLM-like system.

**Status:** `CANDIDATE`, intentionally not activated now.

**Why relevant:** could become useful when the project has hundreds/thousands of books, pages, videos, transcripts, and source dossiers requiring persistent search and cross-source retrieval.

**Why deferred:** heavier application/database/UI stack than current evidence volume justifies.

### 7.9 `vercel-labs/skills` / `find-skills` / skills.sh ecosystem

**Capability:** discover/install Agent Skills across compatible agent hosts.

**Status:** `CANDIDATE` as a discovery aid, not as an always-on workflow owner.

**Why relevant:** reduces repeated manual searching for reusable Skills and may feed the future weekly capability scout.

**Boundary:** discovery results are untrusted candidates and must pass normal tool admission.

### 7.10 `thisis-romar/youtube-transcript-toolkit`

**Capability:** YouTube transcript cleaning + timestamped screenshots/PDF.

**Status:** `CANDIDATE`, lower priority than `video-to-skill` for current project.

**Why lower priority:** current access design may involve cookies, proxies, local token providers, remote EJS components, and a less stable repository/default-branch posture. Functionality is relevant, but the permission/maintenance surface is larger than needed for first admission trials.

### 7.11 `obra/Youtube2Webpage`

**Capability:** YouTube captions + timestamped screenshots into a browsable webpage.

**Status:** `CANDIDATE / REFERENCE`.

**Why relevant:** simple reference architecture for binding transcript text and screenshots by timestamp.

**Why not first choice:** narrow YouTube-focused pipeline and older/simpler architecture compared with newer multimodal candidates.

### 7.12 OSS Insight (`pingcap/ossinsight`)

**Capability:** GitHub ecosystem analytics / trending / star velocity / collections.

**Status:** `CANDIDATE` as a discovery-data source for the future cross-project capability scout.

**Why relevant:** provides trend/ranking APIs that can complement GitHub Trending/Search when selecting the weekly top candidate set.

**Boundary:** popularity is discovery evidence only, never adoption evidence.

### 7.13 Agent registry projects

Examples discovered:
- `agentoperations/agent-registry`
- `agentregistry-dev/agentregistry`

**Capability:** catalog metadata for agents, Skills, MCP servers, evaluations, lifecycle/promotion, dependency/supply-chain visibility.

**Status:** `CANDIDATE / REFERENCE`.

**Why relevant:** useful design references for the future machine-readable cross-project Tool/Capability Registry.

**Decision:** Do not adopt a full registry server now. First keep the canonical asset store in Git/Markdown and only introduce a registry service after real catalog scale/search/update pain exists.

## 8. Candidate trading/agent frameworks found but not recommended as project backbone

The following remain useful references but do not match the current Human Playbook First route as primary backbone:

- TradingAgents;
- Microsoft RD-Agent / Qlib;
- FinRobot;
- similar multi-agent trading or automated factor-mining systems.

Reason: current project authority does not use unconstrained automated strategy/factor discovery as the default research route, and does not authorize a discretionary LLM live buy/sell critical path.

They may be mined for component ideas after explicit fit review; presence/popularity does not authorize adoption.

## 9. Future replacement / supersession rule

The asset library should prefer capability-level competition rather than tool loyalty.

When a new candidate appears:

1. map it to an existing `CAPABILITY_CLASS`;
2. compare it against current candidates/adopted tool(s);
3. ask whether it materially improves quality, cost, privacy, reproducibility, maintenance, or capability coverage;
4. if yes, run a bounded replacement trial;
5. if it wins, record `REPLACED_BY` / migration evidence;
6. retire the old tool only after the dependent project paths are migrated safely.

This is the intended long-term information advantage: not merely remembering tools, but remembering **why they were considered, what they replaced, what evidence existed, and when a newer capability is actually better**.

## 10. Current bounded next action for kline-playbook-engine

Do not build the global weekly scout or Obsidian integration yet.

First perform a small Tool Admission Pilot on the demonstrated Human Playbook acquisition gap:

1. `video-to-skill` — public YouTube + public Bilibili evidence test;
2. `book-to-skill` + `Docling` — rights-cleared document extraction/index test;
3. `video-transcribe-skill` — Chinese no-caption transcription fallback test.

Only after deterministic/source/permission review and real local probes may any candidate move from `CANDIDATE` to `VERIFIED` or `ADOPTED`.

The broader cross-project weekly capability scout is a future separate bounded project/tooling package, not automatically activated by this seed document.
