# HUMAN_TRADER_DISTILLATION_DOSSIER_SCHEMA_V1_0

> Version: 1.0
> Date: 2026-08-21
> Status: ACTIVE / OWNER-APPROVED OPERATIONAL RESEARCH TEMPLATE
> Governing authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Claim-level authority: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

## 1. Purpose and boundary

This schema defines the **trader-level, long-horizon distillation dossier** used to accumulate evidence across many source materials from the same trader.

It is an aggregation/organization layer above claim records. It does **not** replace or loosen the binding claim-extraction schema or research protocol.

The three layers remain strictly separate:

```text
SOURCE CLAIM
!=
PROJECT / AI INTERPRETATION
!=
MACHINE OPERATIONALIZATION
```

Missing source meaning must remain `UNKNOWN`. Inference must remain labeled `INFERRED` and may never be rewritten as an `EXPLICIT` source rule.

This schema does not authorize candidate outcome-bearing backtests, validation access, final-holdout access, Shadow/live trading, broker access, paid commitments, or real-money actions.

## 2. Longitudinal update rule

A trader dossier is **cumulative**, not one-summary-per-video.

Each new approved source may:
- add evidence to an existing field;
- fill a prior `UNKNOWN`;
- weaken or overturn an earlier interpretation when better source evidence appears;
- add a positive case, negative case, near-miss, lookalike or ambiguity;
- reveal a new strategy family;
- merge apparently separate families when evidence shows they are the same mechanism.

Do not delete contradictory source evidence merely to make the dossier cleaner. Preserve the conflict and its anchors until resolved.

Repeated presentation of the same mechanism in different videos is evidence reinforcement, not a new strategy family by default.

## 3. Mandatory 14-part trader dossier

Every trader dossier uses the same fourteen sections.

### 1. Market classification system

Document how the trader classifies market state in their own terms, for example trend, range, breakout, failed breakout, reversal, acceleration, exhaustion, or other source-specific categories.

Record the trader's actual taxonomy where available; do not silently replace it with a project taxonomy.

### 2. Preconditions for each market class

For every class above, record the conditions under which the trader considers that class active.

This must include context before the entry candle where the source provides it. Do not reduce a regime definition to one local bar unless the source itself does so.

### 3. Key locations and how they are formed

Record which locations matter and how the trader constructs them, including as applicable:
- prior highs/lows;
- range boundaries;
- support/resistance;
- trend lines/channels;
- consolidation or dense-trading areas;
- round numbers;
- source-specific zones or reference levels.

A location label without formation semantics remains incomplete.

### 4. Price/K-line behavior observed at key locations

Record what the trader watches after price reaches a key location, including as applicable:
- strength/weakness;
- failed break;
- engulfing behavior;
- consecutive bars;
- wicks;
- close location;
- tempo/rhythm change;
- other explicitly observed behavior.

For video material, the verbal statement and corresponding chart behavior must be jointly anchored when the meaning depends on the picture.

### 5. Entry timing and trigger

Record the exact source-supported entry semantics:
- anticipatory vs confirmation entry;
- breakout vs pullback;
- close-confirmed vs intrabar;
- trigger event;
- sequence of required conditions;
- timeframe used for execution.

If timing is not pinned, write `UNKNOWN`.

### 6. Explicit no-trade conditions

Record when the trader explicitly does not trade or withdraws permission, including as applicable:
- poor location;
- insufficient space;
- noisy/choppy market;
- conflicting signals;
- bad risk/reward;
- wrong regime;
- source-specific disqualifiers.

Negative/no-trade evidence is first-class evidence, not an optional note.

### 7. How the trader admits being wrong

Record source-supported invalidation semantics:
- initial stop;
- structural invalidation;
- time invalidation;
- behavior that proves the original thesis wrong;
- conditions requiring immediate abandonment.

Do not invent a stop when the source does not provide one.

### 8. Management after the trade works

Record:
- profit taking;
- scaling out;
- trailing/moving stop;
- conditions for holding;
- conditions for letting profits run;
- exit sequencing;
- discretionary vs rule-like management.

### 9. Position sizing and risk process

Record explicit source statements about:
- position size;
- risk per trade;
- stop-distance adjustment;
- quality-based sizing;
- response to losing streaks;
- portfolio or concurrent-position rules.

If not stated, record `UNKNOWN`; never backfill from project convention.

### 10. Multi-timeframe coordination

Record exactly what each timeframe is used for:
- higher timeframe role;
- execution timeframe role;
- when the trader changes timeframe;
- which observations belong to which timeframe;
- any rule against mixing timeframe logics.

Do not merge statements from different timeframes into one machine rule unless the source supports that linkage.

### 11. Representative successful and failed cases

Preserve concrete cases, not only abstract rules.

Each case should explain why it belongs to the claimed pattern and link to the relevant claims.

Where available, include both:
- successful/positive examples;
- failed or invalidated examples.

A successful outcome is an illustration of source semantics, not evidence that the strategy has economic edge.

### 12. Lookalike counterexamples / hard negatives

Preserve cases that look similar but should not be traded.

This section is especially important for later machine recognition because it defines the boundary between:
- true pattern;
- near-miss;
- wrong-context lookalike;
- explicit no-trade case.

### 13. Explicit rules versus discretionary judgment

Every meaningful element must be classified into one of:

```text
DIRECTLY_PROGRAMMABLE
MULTI_CASE_INFERABLE
HUMAN_DISCRETION_REQUIRED
NOT_YET_UNDERSTOOD
```

This classification is separate from source provenance:

```text
EXPLICIT | INFERRED | UNKNOWN
```

For example, an `EXPLICIT` concept can still be `HUMAN_DISCRETION_REQUIRED` if the source uses an unformalized visual judgment.

### 14. Independent strategy families

Identify the trader's distinct strategy families by mechanism, not by video count or naming variation.

For each family, maintain:

```text
applicable_market
-> location
-> trigger
-> no_trade
-> stop_or_invalidation
-> management
-> exit
-> counterexamples
```

Repeated appearances of the same mechanism across videos strengthen one family. They do not create multiple families unless the outcome-affecting mechanism is materially different.

Family merges/splits must preserve lineage and prior evidence anchors.

## 4. Evidence preservation requirements

Do not retain only the final prose summary.

Every material conclusion must remain traceable to its source evidence.

For video, preserve at minimum:

```text
trader_id:
material_id:
source_id_or_url:
source_timestamp_start:
source_timestamp_end:
language_anchor:
visual_anchor:
timeframe_visible_or_stated:
instrument_if_explicit:
case_type:
linked_claim_ids:
interpretation_status:
ambiguity_notes:
```

Preferred `case_type` values:

```text
POSITIVE_EXAMPLE
FAILED_EXAMPLE
INVALIDATION
NEAR_MISS
WRONG_CONTEXT_LOOKALIKE
NO_TRADE
AMBIGUOUS
OTHER
```

For chart-dependent video statements, a language-only anchor is insufficient when the referent depends on what is being pointed to, drawn, circled, moved, zoomed, or compared on screen.

Use:

```text
LANGUAGE EVIDENCE
+
SAME-TIME VISUAL EVIDENCE
+
BEFORE/AFTER VISUAL CHANGE WHEN MATERIAL
```

Important rule candidates must support exact reinspection of the source time range.

## 5. Source wording and copyright handling

Preserve source meaning and traceability, not a redistribution archive.

Use short excerpts only when useful; otherwise prefer concise paraphrase plus exact source/time anchors.

Do not commit full copyrighted videos, courses, books or transcripts into shareable repository artifacts unless rights clearly allow it.

## 6. UNKNOWN and contradiction policy

A dossier is allowed to remain incomplete indefinitely.

Use `UNKNOWN` when the source corpus has not pinned an answer.

When two source materials conflict:
- preserve both anchors;
- record chronology/context/timeframe differences where known;
- do not force reconciliation;
- downgrade the affected interpretation to ambiguous if a unique source-faithful meaning cannot be justified.

## 7. Machine-readiness boundary

The trader dossier is not itself a machine strategy.

A field being well understood does not automatically make it programmable.

Machine operationalization remains governed by the claim schema and protocol. The dossier may only describe machine-readiness using the classification in Section 3.13 and existing machine-operationalization statuses.

No inferred numeric threshold may be silently introduced to make a visual/discretionary concept executable.

## 8. Cross-trader merge preparation

When multiple traders are later compared, preserve two identities:

```text
TRADER-SPECIFIC SOURCE SEMANTICS
MECHANISM-LEVEL FAMILY SIGNATURE
```

Cross-trader deduplication may group mechanisms only after source-specific meanings, context and differences are preserved.

Similarity of vocabulary or chart appearance alone is insufficient to declare two strategy families equivalent.

## 9. Minimum working artifact shape

A trader-level dossier should contain:

```text
TRADER_IDENTITY
SOURCE_MATERIAL_INDEX
14-PART DOSSIER
CLAIM LINKS
CASE LIBRARY
STRATEGY FAMILY INDEX
UNRESOLVED / UNKNOWN REGISTER
CONTRADICTION REGISTER
MACHINEABILITY CLASSIFICATION
UPDATE HISTORY
```

This structure is cumulative across videos and other approved source material.
