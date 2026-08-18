# HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY

> Date: 2026-08-19
> Status: ACTIVE / SOURCE-LEVEL ONLY
> Schema: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
> Research direction: `RESEARCH_DIRECTION.md`
>
> This inventory tracks source materials and source-level evidence. It does not contain accepted trading rules, playbooks, backtest conclusions, or frozen research semantics.

## 1. Purpose

Provide one durable place to track what Human Playbook source material has been discovered, what has actually been checked, and what remains only a lead.

The project—not the Owner—is responsible for primary source discovery at scale. Owner-supplied material is supplemental and uses the same evidence standard.

## 2. Status vocabulary

Material processing status:

```text
DISCOVERED
PROVENANCE_CHECKED
SOURCE_DOSSIER_IN_PROGRESS
SOURCE_DOSSIER_COMPLETE
DEFERRED
REJECTED
```

Source-level admission classification:

```text
PRIORITY_DEEP_DIVE
KEEP_CANDIDATE
DISCOVERY_ONLY
DEFER
REJECT_SOURCE
```

Observation compatibility:

```text
OBSERVABLE_NOW
PARTIALLY_OBSERVABLE
NOT_OBSERVABLE_WITH_CURRENT_DATA
UNKNOWN
```

None of these statuses means a playbook is valid.

## 3. First-wave inventory — source-level only

Access/provenance checked on 2026-08-19. These rows intentionally stop before concrete trading-claim extraction.

| source_id | material_id | canonical source / series | material | type | language | provenance | processing status | source admission | observability | failure visibility | lineage / incentive note | current evidence / next source-level check |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SRC-BRANDT | MAT-BRANDT-DIARY | Peter L. Brandt | *Diary of a Professional Commodity Trader* | publisher book / longitudinal diary | EN | TRACEABLE_ORIGINAL | PROVENANCE_CHECKED | PRIORITY_DEEP_DIVE | OBSERVABLE_NOW | PRESENT | Wiley original; Brandt also operates commercial Factor services; publisher/author performance claims are not validity evidence | Wiley identifies the book as a 2009 trading diary with charts, analysis and play-by-play; deeper source-level check should sample dispersed periods + failures without extracting rules |
| SRC-BROOKS | MAT-BROOKS-PA | Al Brooks | Wiley *Trading Price Action* series + official Brooks Trading Course | books + long-form paid video course | EN | TRACEABLE_ORIGINAL | PROVENANCE_CHECKED | PRIORITY_DEEP_DIVE | OBSERVABLE_NOW | UNKNOWN | Official commercial education business; dense proprietary vocabulary creates high future AI-interpretation risk | Wiley confirms the book series; official site advertises 100+ hour / 52-module course. Next source-level check: material continuity, explicit failure/no-trade coverage, source glossary boundaries |
| SRC-RASCHKE | MAT-RASCHKE-VIDEOS | Linda Bradford Raschke | official video archive | long-form professional trading video archive | EN | TRACEABLE_ORIGINAL | PROVENANCE_CHECKED | PRIORITY_DEEP_DIVE | PARTIALLY_OBSERVABLE | UNKNOWN | Official site; mixed topics include price/volume plus Market Profile concepts; commercial subscription surface present | Official archive spans volume/price, day type, trade location, mean reversion, trend, breakouts, psychology and Market Profile. Next: identify which observation surfaces are reproducible with current data |
| SRC-GRIMES | MAT-GRIMES-MARKETLIFE | Adam H. Grimes / MarketLife | official blog + course platform | education/archive + commercial service | EN | TRACEABLE_ORIGINAL | PROVENANCE_CHECKED | KEEP_CANDIDATE | PARTIALLY_OBSERVABLE | UNKNOWN | Author explicitly spans quantitative and discretionary trading; MarketLife is commercial with subscriptions; marketing/testimonial claims are not validity evidence | Official blog links course migration to MarketLife; MarketLife states educational focus and paid tiers. Next: identify free/original long-form corpus suitable for source-level review before paid material is considered |
| SRC-STEENBARGER | MAT-STEENBARGER-TRADERFEED | Brett Steenbarger / TraderFeed | TraderFeed archive / resource center | longitudinal process, review and psychology archive | EN | TRACEABLE_ORIGINAL | PROVENANCE_CHECKED | PRIORITY_DEEP_DIVE | PARTIALLY_OBSERVABLE | PRESENT | Process/psychology source, not an independent vote for a specific technical setup; long archive reduces highlight-only bias | TraderFeed documents a multi-year archive with thousands of posts and curated failure/discipline/performance topics; next source-level check should focus on review/error/no-trade process evidence rather than trade-rule extraction |
| SRC-QINGZE | MAT-QINGZE-10Y | 青泽 | 《十年一梦：一个操盘手的自白》 | Chinese book / long-form trading memoir | ZH | VERIFIED_SOURCE_IDENTITY | PROVENANCE_CHECKED | KEEP_CANDIDATE | UNKNOWN | Chinese futures context is strategically relevant, but current check is bibliographic only; no assumption of validity or completeness | University library records confirm author 青泽, 企业管理出版社, 2006, 326 pages, and domestic stock/futures growth narrative. Next: obtain authorized text/sample and inspect failure density / hindsight risk / observation surfaces |
| SRC-QHRB-COMP | MAT-QHRB-COMPETITION | 期货日报全国期货实盘交易大赛 | official competition site / rankings | public-record discovery channel | ZH | TRACEABLE_ORIGINAL | PROVENANCE_CHECKED | DISCOVERY_ONLY | UNKNOWN | Official site explicitly says ranking data do not guarantee trading ability; use as discovery path, not playbook evidence | Use competition records to discover less-marketed Chinese traders, then separately verify identity, original long-form material and failure evidence |

## 4. Canonical provenance pointers for first wave

These are discovery/provenance anchors, not proof that any source/playbook is valid.

### Peter L. Brandt
- Wiley Online Books: `https://onlinelibrary.wiley.com/doi/book/10.1002/9781119202967`
- Wiley-VCH product page: `https://www.wiley-vch.de/en/areas-interest/finance-economics-law/diary-of-a-professional-commodity-trader-978-1-394-37796-1`
- Author/commercial site: `https://www.peterlbrandt.com/`

### Al Brooks
- Wiley companion/book identity: `https://books.wiley.com/titles/9781118066515/`
- Official course/site: `https://www.brookspriceaction.com/`

### Linda Bradford Raschke
- Official videos: `https://lindaraschke.net/linda-videos/`

### Adam H. Grimes
- Author blog: `https://adamhgrimes.com/`
- MarketLife: `https://www.marketlifetrading.com/`

### Brett Steenbarger
- TraderFeed: `https://traderfeed.blogspot.com/`

### 青泽
- University library bibliographic record: `https://opac.lib.uibe.edu.cn/opac/book/49b182740517669f88a4ed25a47f359d`
- Additional university library record: `https://jp.tfswufe.edu.cn/opac/book/f2386b9ba460e94891dbcbcf5b182482`

### 期货日报全国期货实盘交易大赛
- Official competition site: `https://ds.qhrb.com.cn/`

## 5. Required material record

For every material promoted beyond `DISCOVERED`, record or link the following:

```text
source_id:
material_id:
canonical_name:
person_or_series:
source_type:
language:
original_publisher_or_channel:
publication_or_upload_date:
canonical_url_or_bibliographic_id:
archive_or_version:
original_or_derivative:
parent_material_id_if_any:
identity_evidence:
provenance_evidence:
material_scale:
trading_loop_coverage_presence:
failure_visibility:
incentive_or_marketing_notes:
performance_claim_notes:
lineage_or_independence_notes:
observed_information_surface:
observability_compatibility:
access_checked_at:
processing_tool_if_any:
processing_tool_version_or_pin:
source_anchor_capability:
copyright_retention_boundary:
source_admission_classification:
open_source_level_questions:
```

Do not fill missing facts by inference. Use `UNKNOWN` when evidence is absent.

## 6. Source-level processing route

```text
DISCOVER
-> verify identity/provenance
-> register material
-> Source Dossier v0.2
-> classify source-level value / observability
-> preserve failure/counterexample leads
-> stop before concrete trading-claim extraction unless later authority allows it
```

## 7. Tool routing from completed admission pilot

Use the smallest verified capability needed:

- document/layout-heavy material: Docling is VERIFIED for the tested Windows extraction scope;
- Chinese no-caption local/offline media: video-transcribe-skill is VERIFIED as fallback, but transcripts require terminology/number spot-checks and are not exact quotations by default;
- local multimodal video evidence: video-to-skill local pipeline is a VERIFIED sub-capability, but the overall tool remains CANDIDATE because current anonymous public YouTube/Bilibili URL acquisition was blocked;
- book-to-skill remains DEFERRED / REFERENCE.

Tool status is separate from source status.

## 8. Current package boundary

Current work may populate this inventory and complete source-level dossiers.

Current work may **not**:
- extract concrete buy/sell rules as project claims;
- convert fuzzy language into thresholds;
- backtest source ideas;
- freeze protocol/split semantics;
- use final-unseen data;
- make live trading decisions.

## 9. Remaining representative lanes

The first population intentionally does not claim full coverage. Still missing or incomplete:
- auction/profile lineage sample with clearly traceable original/descendant boundaries;
- skeptical/counter-evidence source specifically for technical-analysis/data-snooping risk;
- additional China-first long-form trader sources discovered through public records rather than marketing prominence;
- explicit negative/near-miss material samples for several first-wave candidates.

These are the next source-level gaps. They remain source research, not strategy research.
