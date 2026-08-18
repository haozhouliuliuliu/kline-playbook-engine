# HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2

> Date: 2026-08-19
> Status: ACTIVE_DRAFT / NON_FROZEN
> Scope: source-level evidence only
> Binding research direction: `RESEARCH_DIRECTION.md`
> Current state authority: `CURRENT_STATE.md`
>
> This document does **not** freeze research protocol, chronological split, concrete playbooks, source rankings, strategy semantics, parameterization, final-unseen access, or live-AI behavior.

## 1. Purpose

Human Playbook First requires a durable source layer before any trading claim is operationalized.

The source layer answers:

```text
Who is this source?
What is the original material?
Can we trace it?
What kind of evidence does it contain?
Does it expose failure / invalidation / no-trade cases?
What incentives or marketing conflicts exist?
Is it independent evidence or part of a lineage/repost chain?
Can the project's available data actually observe what this trader observes?
```

It does **not** answer whether a playbook is profitable or valid.

Source quality != playbook validity.

## 2. Acquisition ownership

Default acquisition model:

```text
PROJECT-LED DISCOVERY = PRIMARY
OWNER-SUPPLIED MATERIAL = SUPPLEMENTAL
```

The Owner is not the project's manual source collector and should not be expected to watch/select large volumes of books, videos, interviews, blogs, or courses.

Project-led discovery may use public books/catalogs, publisher pages, interviews, articles, blogs, videos, images, public teaching material, competition/public-account records, skeptical research, and other traceable sources.

Owner-supplied material and project-discovered material use the same evidence standard.

```text
Owner supplied != trusted
AI discovered != trusted
```

## 3. Non-negotiable separation

The project must preserve three layers:

```text
SOURCE / RAW CLAIM
!=
PROJECT / AI INTERPRETATION
!=
MACHINE OPERATIONALIZATION
```

This dossier is only the first layer's source-level envelope. It must not silently turn an author's language into a machine rule.

Examples of forbidden collapse:

```text
source phrase: "strong breakout"
-> AI tries 50 definitions
-> keeps the best backtest
```

That would be hidden search freedom, not faithful source extraction.

## 4. Source Dossier v0.2 — required blocks

Every serious source candidate should be able to answer these eight blocks.

### 4.1 Identity

Record:
- canonical person / series / institution name;
- aliases/translations where material;
- source type;
- market/domain background where traceable;
- language;
- whether identity itself is verified or uncertain.

### 4.2 Original provenance

Record:
- original publisher/channel/platform;
- publication/upload date when available;
- canonical URL / bibliographic identifier;
- archive/version if used;
- original vs repost vs excerpt vs transcript vs commentary;
- parent source when the material is derivative.

Original material is preferred. Reposts may be discovery aids but should not silently become canonical evidence.

### 4.3 Material scale and continuity

Record whether the candidate provides:
- one isolated clip/page/chart;
- a full book/course/interview;
- a multi-year archive/diary;
- repeated real-time or near-real-time observations;
- only hindsight-selected examples.

Longitudinal material is usually more informative than isolated highlight examples because it exposes consistency, changes, failures, and missing periods.

### 4.4 Trading-loop completeness

At the source level, record whether material appears to contain some or all of:
- market/background context;
- setup / observation;
- confirmation / decision condition;
- invalidation / stop / error condition;
- exit / management;
- no-trade / stand-aside condition;
- applicability limits.

This is a coverage inventory only. Do not extract concrete strategy logic in this dossier stage.

### 4.5 Failure visibility

Record whether the material visibly includes:
- losing trades;
- failed patterns;
- mistakes;
- drawdowns;
- abandoned ideas;
- no-trade cases;
- changed interpretations;
- counterexamples.

A source showing only winners is lower-value research evidence even when the author is famous.

### 4.6 Incentives / conflicts / marketing

Record:
- paid courses/services/newsletters;
- brokerage/referral relationships when traceable;
- return/PnL claims;
- testimonials/marketing claims;
- whether performance claims have independent supporting evidence;
- conflicts between educational claims and commercial incentives.

Performance claims must remain isolated from playbook validity.

### 4.7 Lineage / independence

Record:
- teacher/student lineage;
- copied/reposted material;
- shared school/framework;
- direct citations/dependencies;
- whether multiple sources are genuinely independent or merely repeat the same ancestor.

Agreement among related sources must not be counted as independent corroboration.

### 4.8 Observability compatibility

For each source, ask:

1. What does the trader actually observe?
2. Does the current project data contain those observations?
3. If only a substitute exists, does the substitute change the meaning?
4. Can the project honestly test the source's idea with available data?

Example observation surfaces:
- bars / OHLC;
- volume;
- multi-timeframe structure;
- DOM / order book;
- tape / prints;
- market profile / auction-derived structure;
- news;
- fundamentals;
- cross-market relationships;
- discretionary visual context.

Allowed compatibility labels:

```text
OBSERVABLE_NOW
PARTIALLY_OBSERVABLE
NOT_OBSERVABLE_WITH_CURRENT_DATA
UNKNOWN
```

Critical rule:

If a trader relies on DOM/order-flow absorption and the project currently has 1-minute bars, do **not** invent an arbitrary wick/bar proxy and call it the same concept.

`NOT_OBSERVABLE_WITH_CURRENT_DATA` is an acceptable and important research result.

## 5. Source-level evidence confidence

Use plain evidence labels rather than false precision.

```text
VERIFIED_SOURCE_IDENTITY
TRACEABLE_ORIGINAL
TRACEABLE_DERIVATIVE
UNVERIFIED_CLAIM
UNKNOWN
```

Do not create an automatic numeric admission score that pretends weak dimensions can be precisely traded off against one another.

A numeric rubric may later be used as a screening aid, but it cannot by itself admit a source or validate a playbook.

## 6. Source admission classification

Use conclusion-style classifications:

```text
PRIORITY_DEEP_DIVE
KEEP_CANDIDATE
DISCOVERY_ONLY
DEFER
REJECT_SOURCE
```

Interpretation:

- `PRIORITY_DEEP_DIVE`: source form/provenance/failure visibility make deeper source review worthwhile.
- `KEEP_CANDIDATE`: potentially useful, but evidence or original material is incomplete.
- `DISCOVERY_ONLY`: useful for finding people/materials, not itself playbook evidence.
- `DEFER`: potentially useful but blocked by observability, access, duplication, or low current relevance.
- `REJECT_SOURCE`: material is too untraceable, misleading, unsafe, or unusable for the project source layer.

These are source-level workflow labels, not judgments of trading skill.

## 7. Sampling heuristic for large archives

For very large longitudinal sources, a cheap default screening heuristic may use:

```text
3 + 2 + 1
```

Meaning:
- 3 dispersed time points;
- 2 failure / losing / invalidation examples where available;
- 1 complete source-level example.

This is a **heuristic**, not a frozen protocol requirement. It may be adjusted when source structure makes it inappropriate.

## 8. Future claim extraction status vocabulary

When the project later has authority to extract actual trading claims, every extracted statement must distinguish:

```text
EXPLICIT = the source explicitly states it
INFERRED = project/AI interpretation
UNKNOWN = source does not specify it
```

This vocabulary is defined now so the source layer is compatible with later research, but this document does not authorize concrete claim extraction yet.

## 9. Material-level provenance minimum

Each material item should eventually record at least:

```text
source_id
material_id
canonical_name
person_or_series
source_type
original_publisher_or_channel
publication_or_upload_date
canonical_url_or_bibliographic_id
archive_or_version
language
original_or_derivative
parent_material_id_if_any
access_checked_at
local_processing_status
source_anchor_capability
copyright_retention_boundary
notes
```

Do not preserve entire copyrighted books/videos in the repository merely for convenience. Keep provenance and sparse evidence anchors sufficient to relocate the original source.

## 10. Tool usage boundary

The completed Windows tool-admission pilot established:

- Docling = VERIFIED for Windows document/layout extraction;
- video-transcribe-skill = VERIFIED for local/offline Chinese no-caption fallback, with terminology spot-check requirements;
- video-to-skill local multimodal pipeline = VERIFIED sub-capability, while public YouTube/Bilibili URL adapters remain unverified on the current network;
- book-to-skill = DEFERRED / REFERENCE.

These statuses do not automatically make a tool ADOPTED.

Use the smallest verified capability needed for a source-material task. Do not install or activate all candidates by default.

## 11. Current prohibited work

This source-dossier stage does not authorize:
- concrete buy/sell rule extraction;
- strategy conclusions;
- machine thresholds for fuzzy trader language;
- parameter search;
- backtesting playbooks;
- research-protocol / chronological-split freeze;
- final-unseen access;
- live/Shadow trading;
- discretionary live LLM decisions;
- paid/credential-bearing acquisition without the required gate;
- knowledge-graph build-out.

## 12. Acceptance / freeze boundary

This v0.2 dossier is an operational draft for source-level work.

It is not frozen research semantics.

Before any later research protocol or claim-extraction semantics become binding, they require the project's normal decision/review process, including independent adversarial review where required by project authority.
