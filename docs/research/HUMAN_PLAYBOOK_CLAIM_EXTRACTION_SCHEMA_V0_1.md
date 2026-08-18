# HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V0_1

> Date: 2026-08-19
> Status: ACTIVE_DRAFT / NON_FROZEN / NOT_APPLIED_TO_REAL_TRADING_LOGIC
> Research direction: `RESEARCH_DIRECTION.md`
> Source-layer input: `docs/research/HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT.md`
>
> This document defines how a future authorized claim-extraction stage may represent source claims. It is a schema only. It must not be used to extract real trading logic until project authority explicitly permits claim extraction under the later research protocol.

## 1. Purpose

Human Playbook First requires the project to preserve the difference between:

```text
WHAT THE SOURCE SAID
!=
WHAT THE PROJECT / AI THINKS IT MEANS
!=
HOW A MACHINE MAY LATER REPRESENT OR TEST IT
```

The schema exists to prevent those layers from collapsing.

## 2. Claim-status vocabulary

Candidate status vocabulary:

```text
EXPLICIT
INFERRED
UNKNOWN
```

Meaning:

- `EXPLICIT`: the source directly states the claim in attributable material.
- `INFERRED`: the project/AI derives an interpretation that is not directly stated by the source.
- `UNKNOWN`: the source evidence does not establish the field.

Rules:
- `UNKNOWN` is a valid result and should be preferred over filling a gap by guesswork.
- `INFERRED` must never be rewritten as if the source said it.
- A paraphrase of an explicit source statement remains a paraphrase, not a verbatim quote.

These labels remain non-frozen until the later research-protocol review.

## 3. Minimal claim record

A future claim record should support at least:

```text
claim_id:
source_id:
material_id:
source_anchor:
source_anchor_type: page | timestamp | section | paragraph | figure | other
source_language:
claim_status: EXPLICIT | INFERRED | UNKNOWN
source_excerpt_short:
source_paraphrase:
source_context_before_after:
claim_category:
source_observation_surface:
source_timeframe_or_horizon_if_explicit:
source_market_or_instrument_if_explicit:
source_applicability_if_explicit:
source_invalidation_if_explicit:
source_no_trade_if_explicit:
source_exit_or_management_if_explicit:
source_failure_or_counterexample_anchor:
ambiguity_notes:
lineage_id:
source_independence_notes:
observability_compatibility:
observability_missing_inputs:
interpretation_version:
interpretation_status:
interpretation_text:
interpretation_evidence_basis:
alternative_interpretation_ids:
search_freedom_branch_id:
data_exposure_state:
machine_operationalization_status:
review_status:
created_at:
updated_at:
```

No field should silently default to a concrete trading rule.

## 4. Source anchor requirement

Every `EXPLICIT` claim must point back to a source anchor.

Preferred anchors:
- book: edition + page / chapter / figure;
- video: source URL/id + timestamp;
- article/blog: canonical URL + section/paragraph context;
- interview: original/nearest-original page + question/answer position;
- image/chart: parent material + figure/frame identity.

If the source is derivative/reposted, preserve the provenance chain rather than pretending the derivative is original.

## 5. Copyright / retention boundary

The project needs traceability, not a redistribution archive.

Rules:
- store only short excerpts when useful;
- prefer page/timestamp/section anchors plus paraphrase;
- do not commit whole copyrighted books, course transcripts, videos or large copied passages;
- locally processed raw material must remain outside shareable project artifacts unless rights clearly permit retention.

## 6. Claim categories — structural slots only

A future claim may be tagged into one or more structural categories:

```text
MARKET_CONTEXT
OBSERVED_CUE
SOURCE_INTERPRETATION
WATCHING_OR_NO_TRADE
ACTION_PERMISSION
CONFIRMATION
INVALIDATION
MANAGEMENT
EXIT
APPLICABILITY
NON_APPLICABILITY
RISK_PROCESS
REVIEW_PROCESS
FAILURE_OR_COUNTEREXAMPLE
OTHER
```

These are structural containers, not machine rules.

Example with neutral placeholders only:

```text
source_excerpt_short: "<SOURCE PHRASE>"
claim_status: EXPLICIT
claim_category: OBSERVED_CUE
source_paraphrase: "<NEUTRAL PARAPHRASE>"
interpretation_status: NOT_STARTED
machine_operationalization_status: NOT_AUTHORIZED
```

Do not insert a real trading-source phrase into this schema during the current stage.

## 7. Source claim vs interpretation

Interpretation must be stored separately.

Example structure:

```text
SOURCE CLAIM v1
  anchor = <PAGE/TIMESTAMP>
  status = EXPLICIT

INTERPRETATION v1
  status = INFERRED
  text = <PROJECT INTERPRETATION>

INTERPRETATION v2
  status = INFERRED
  text = <ALTERNATIVE PROJECT INTERPRETATION>
```

Changing `INTERPRETATION v1` to `v2` must not alter the source claim record.

## 8. Ambiguity handling

Ambiguity is first-class evidence.

Use explicit notes for:
- unclear referent;
- context-dependent language;
- missing timeframe;
- missing market/instrument scope;
- unclear invalidation;
- unclear whether a phrase is descriptive or prescriptive;
- terminology that changes across a source's own materials;
- conflicting statements across time.

Do not force ambiguous claims into a single interpretation merely to make them testable.

## 9. Alternative interpretations and search freedom

If a claim has more than one plausible interpretation, preserve branches explicitly:

```text
claim_id = C1
interpretation_v1 -> branch B1
interpretation_v2 -> branch B2
interpretation_v3 -> branch B3
```

Future research protocol must decide how these branches count toward search freedom / multiple testing.

Current rule:

```text
multiple plausible interpretations exist
-> record them
-> do not choose historical winner in this stage
```

## 10. Observability gate

Every future claim should record what the source actually observed.

Candidate values:

```text
OBSERVABLE_NOW
PARTIALLY_OBSERVABLE
NOT_OBSERVABLE_WITH_CURRENT_DATA
UNKNOWN
NOT_APPLICABLE
```

Required questions:
1. What source input is required?
2. Does the project have that input point-in-time?
3. If only a substitute exists, does the substitute preserve meaning?
4. If meaning changes, should the claim remain untestable?

Never create a synthetic bar proxy solely to avoid an observability failure.

## 11. Failure / near-miss / negative evidence linkage

Claims should be able to link to:
- positive example;
- near-miss;
- negative/counterexample;
- same visible pattern in wrong context;
- same context with different outcome;
- ambiguous example;
- explicit source failure/invalidation.

The schema does not freeze a required count. The earlier `3 + 2 + 1` idea remains only a possible sampling heuristic for later review.

## 12. Lineage and independence

Every claim should link to a lineage where known.

Examples of lineage relationships:

```text
ORIGINATOR
DIRECT_DESCENDANT
TEACHER_STUDENT
RESTATEMENT
ADAPTATION
UNKNOWN_RELATION
```

A claim repeated inside one lineage is not automatically independent evidence.

The later protocol must decide how lineage dependence affects evidence aggregation.

## 13. Data exposure state

The schema must be compatible with future exposure tracking.

Candidate exposure fields may include:

```text
SOURCE_ONLY
NO_MARKET_DATA_EXPOSURE
DEVELOPMENT_EXPOSED
VALIDATION_EXPOSED
FINAL_UNSEEN_LOCKED
FINAL_UNSEEN_EXPOSED
```

These labels are placeholders only. The later chronological-split freeze must define their exact semantics.

Current source-level work should remain `NO_MARKET_DATA_EXPOSURE` for strategy claims because no real claim extraction/testing is authorized.

## 14. Machine operationalization boundary

Candidate statuses:

```text
NOT_AUTHORIZED
NOT_OBSERVABLE
INTERPRETATION_REQUIRED
READY_FOR_LATER_PROTOCOL_REVIEW
OPERATIONALIZED_VERSIONED
```

During the current stage:

`machine_operationalization_status=NOT_AUTHORIZED`

for every real trading claim.

## 15. Review requirements for future use

Before a claim can later progress toward machine operationalization, the research protocol should require review of:
- provenance;
- claim status (`EXPLICIT / INFERRED / UNKNOWN`);
- ambiguity;
- lineage;
- observability;
- failure/counterexamples;
- interpretation variants/search freedom;
- data exposure.

Material research-semantic decisions require the normal independent adversarial review before freeze/acceptance.

## 16. Forbidden transformations

Forbidden during claim extraction:

```text
source says "strong breakout"
-> silently define as > 1.5 ATR
```

```text
source says "selling pressure is weak"
-> invent one indicator
-> call it source-equivalent
```

```text
source does not state invalidation
-> infer a stop
-> mark it EXPLICIT
```

```text
try many interpretations
-> backtest all
-> retain best
-> describe winner as "what the source meant"
```

## 17. Schema validation criteria

The schema is considered structurally usable if a future record can answer:
- where did this claim come from?
- what did the source actually say?
- what is only our inference?
- what remains unknown?
- what information did the source observe?
- can current project data observe it?
- what lineage does it belong to?
- what alternative interpretations exist?
- has any interpretation seen development/validation/final data?
- where are failure/counterexamples linked?

## 18. Current status

`CLAIM_EXTRACTION_SCHEMA_RESULT=GO_AS_NON_FROZEN_DRAFT`

This means the schema is suitable as an input to the later research-protocol freeze review.

It does NOT authorize applying the schema to Brandt, Brooks, Raschke, Grimes, Steenbarger, Market Profile, Chinese sources, or any other real trading logic yet.

## 19. Next bounded action

Prepare a decision-ready **research-protocol input package** that combines:
- Human Playbook First binding direction;
- Source Dossier v0.2;
- first-wave source-layer findings;
- this Claim Extraction schema;
- skeptical/data-snooping guardrails;
- unresolved chronological split / exposure questions.

Do not execute/freeze the protocol until the proper Owner decision/review boundary is reached.
