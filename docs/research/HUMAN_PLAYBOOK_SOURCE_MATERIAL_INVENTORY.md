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

## 3. Inventory table

| source_id | material_id | canonical source / series | material | type | language | provenance | processing status | source admission | observability | failure visibility | lineage note | current evidence / next source-level check |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD | TBD | DISCOVERED | KEEP_CANDIDATE | UNKNOWN | UNKNOWN | UNKNOWN | Populate through project-led discovery; no strategy extraction |

## 4. Required material record

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

## 5. Source-level processing route

```text
DISCOVER
-> verify identity/provenance
-> register material
-> Source Dossier v0.2
-> classify source-level value / observability
-> preserve failure/counterexample leads
-> stop before concrete trading-claim extraction unless later authority allows it
```

## 6. Tool routing from completed admission pilot

Use the smallest verified capability needed:

- document/layout-heavy material: Docling is VERIFIED for the tested Windows extraction scope;
- Chinese no-caption local/offline media: video-transcribe-skill is VERIFIED as fallback, but transcripts require terminology/number spot-checks and are not exact quotations by default;
- local multimodal video evidence: video-to-skill local pipeline is a VERIFIED sub-capability, but the overall tool remains CANDIDATE because current anonymous public YouTube/Bilibili URL acquisition was blocked;
- book-to-skill remains DEFERRED / REFERENCE.

Tool status is separate from source status.

## 7. Current package boundary

Current work may populate this inventory and complete source-level dossiers.

Current work may **not**:
- extract concrete buy/sell rules as project claims;
- convert fuzzy language into thresholds;
- backtest source ideas;
- freeze protocol/split semantics;
- use final-unseen data;
- make live trading decisions.

## 8. Next source-level target

Populate a small representative first wave across materially different source forms and observation surfaces, enough to test whether Source Dossier v0.2 works in practice without creating strategy-research exposure.

Selection should favor diversity of evidence form rather than fame or popularity:
- longitudinal diary/archive;
- dense price-action/context teaching;
- professional short-term trading material;
- auction/profile lineage material;
- process/review/error documentation;
- Chinese futures long-form source;
- Chinese competition/public-record discovery path;
- skeptical/counter-evidence source.

Specific people/materials remain candidates until provenance is checked and recorded here.
