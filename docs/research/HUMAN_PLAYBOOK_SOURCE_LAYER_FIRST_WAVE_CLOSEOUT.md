# HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT

> Date: 2026-08-19
> Status: FIRST_WAVE_SOURCE_LAYER_COMPLETE / NON_FROZEN
> Research direction: `RESEARCH_DIRECTION.md`
> Source schema: `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
> Inventory: `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`
>
> This close-out records what the first source-layer wave established. It does not freeze research protocol, split dates, claim semantics, statistical procedures, playbooks, final-unseen access, or live-AI behavior.

## 1. What is complete

The project now has a durable source layer that can represent materially different evidence forms without turning them into trading rules.

Representative completed source dossiers:
- Peter Brandt longitudinal diary;
- Al Brooks dense price-action books/course source;
- Linda Raschke multi-method professional video archive;
- Adam Grimes discretionary + quantitative education source;
- Brett Steenbarger process/review/error archive;
- Steidlmayer -> Dalton Market Profile lineage cluster;
- skeptical methodological counter-evidence cluster (White / Sullivan-Timmermann-White / Bailey et al.).

China-first source layer:
- 青泽 book identity/provenance is verified at bibliographic level only; no authorized text/sample means no complete dossier yet.
- 期货日报全国期货（期权）实盘交易大赛 is explicitly `DISCOVERY_ONLY`.
- first China discovery leads are recorded separately and remain `DISCOVERED` until original/nearest-original provenance is pinned.

## 2. Durable findings from the first wave

### 2.1 Source quality is not playbook validity

A source can have excellent provenance, long history and visible failures while its trading ideas still fail historical validation.

The source layer therefore admits material for research value, not for truth status.

### 2.2 Lineage agreement is not independent confirmation

Market Profile established the clearest example:

```text
Steidlmayer origin/codification
-> Hawkins collaboration/application
-> Dalton expansion/popularization
-> later educators
```

Multiple books in one lineage cannot be counted as independent evidence merely because different authors repeat related concepts.

The same rule must later apply to classical charting, candlestick, price-action and teacher/student chains.

### 2.3 Observability must be checked before operationalization

A trader may observe:
- OHLC bars;
- volume;
- multi-timeframe structure;
- Market Profile / volume-at-price;
- order flow / DOM;
- fundamentals/news/research trips;
- psychology/process variables.

The project currently owns a point-in-time 1-minute OHLCV corpus, not every possible source input.

Rule:

```text
source concept requires unavailable input
-> mark not/partially observable
-> do not invent a convenient bar proxy
```

A substitute that changes meaning is not faithful operationalization.

### 2.4 Failure visibility is a first-class source property

The project should prefer materials that expose:
- losses;
- invalidations;
- abandoned views;
- no-trade decisions;
- drawdowns;
- mistakes;
- ambiguous cases.

Winner-only examples are structurally weaker evidence even when the author is famous.

### 2.5 Commercial incentives must remain visible

Brooks, Raschke, Grimes, Brandt and Market Profile descendants all have some commercial/education surface.

Commercial activity does not automatically disqualify a source, but:
- testimonials are marketing;
- return claims are claims;
- publisher copy is not validation;
- paid access cannot become an implicit Owner commitment.

### 2.6 Process sources are not market-scene sources

Steenbarger demonstrates a separate category: review, discipline, deliberate practice and trader development can be highly valuable without being market-scene inputs.

Future Playbook architecture must avoid forcing human-process concepts into market-data features.

### 2.7 Skeptical evidence belongs inside the research loop

White, Sullivan/Timmermann/White and Bailey et al. establish a durable methodological warning:

```text
try enough interpretations / models / rules on the same history
-> some will look strong by chance
```

This is directly relevant to Human Playbook First because fuzzy source language can create hidden search freedom if AI generates many operational meanings and selects the best backtest.

No specific statistical procedure is frozen by this conclusion.

### 2.8 China-first provenance has a different practical shape

Chinese futures material is often distributed through:
- books;
- interviews;
- competition reports;
- repost/aggregation sites;
- video platforms.

The project must not lower its evidence bar because original pages are harder to pin.

If only a derivative interview is available, preserve the derivative chain explicitly and keep the candidate below `TRACEABLE_ORIGINAL` until the original/nearest-original source is located.

## 3. Questions that the later research protocol MUST decide

These are decision inputs, not frozen answers.

### 3.1 Claim extraction status

Candidate vocabulary:

```text
EXPLICIT = source states it directly
INFERRED = project/AI interpretation
UNKNOWN = source does not establish it
```

The later protocol must decide how these statuses are stored, reviewed and promoted.

### 3.2 Source claim vs AI interpretation vs machine definition

The later protocol must enforce durable separation:

```text
SOURCE / RAW CLAIM
!=
PROJECT / AI INTERPRETATION
!=
MACHINE OPERATIONALIZATION
```

Each interpretation revision must be versioned rather than silently replacing the source.

### 3.3 Interpretation branches count as search freedom

If one source phrase yields multiple plausible operational meanings, those branches must later count toward research freedom / multiple testing.

Forbidden pattern:

```text
source says "strong breakout"
-> generate many definitions
-> keep historical winner
```

### 3.4 Failure / negative / near-miss preservation

The later protocol must require enough negative and ambiguous examples that a concept cannot be learned only from selected successes.

The prior `3 + 2 + 1` sampling idea may remain a heuristic, not a frozen universal rule:
- 3 dispersed material/time points;
- 2 failure/negative cases;
- 1 complete-loop sample.

### 3.5 Lineage and exposure accounting

The protocol must determine how source families and downstream descendants are grouped so repeated lineage material is not treated as independent confirmation.

It must also record which source/material/interpretation has been exposed to which research data windows.

### 3.6 Observability gate

Before a source claim becomes machine-operationalizable, the protocol must ask:
1. what information did the trader actually observe?
2. does the project have it point-in-time?
3. if a substitute is proposed, does it preserve meaning?
4. if not, should the claim remain currently untestable?

### 3.7 Chronological split / validation / final-unseen governance

The source layer does not decide split dates.

The later freeze must decide:
- development vs validation windows;
- how interpretation revisions affect exposure;
- confirmatory evidence rules;
- final-unseen lock/unlock semantics;
- what happens when a playbook family is modified after seeing validation results.

### 3.8 Counter-evidence integration

The later protocol should explicitly require skeptical/counter-evidence review before acceptance of a playbook family, rather than only collecting supportive trader narratives.

## 4. Explicit non-decisions

This close-out does NOT decide:
- any concrete source ranking beyond source-level admission;
- any playbook;
- any setup/entry/exit/invalidation rule;
- any threshold or parameter;
- any statistical correction method;
- split dates;
- final-unseen access;
- live scene-recognition implementation;
- paid source acquisition.

## 5. Tool decision

`TOOL_DECISION=USE_EXISTING`

The current source layer does not justify another tool addition.

Verified components remain available only when the material requires them:
- Docling for layout-heavy documents;
- video-transcribe-skill for local/offline Chinese no-caption fallback;
- video-to-skill local multimodal pipeline as a verified sub-capability while its public URL adapters remain unverified in the current network.

## 6. First-wave acceptance

`FIRST_WAVE_SOURCE_LAYER_RESULT=GO`

Meaning:
- Source Dossier v0.2 is workable across trader, lineage, process and skeptical-source classes.
- Provenance, failure visibility, incentives, lineage and observability can be kept separate from playbook validity.
- The project has enough source-layer evidence to prepare a non-frozen Claim Extraction schema and a later decision-ready research-protocol package.

It does NOT mean strategy research may start.

## 7. Next bounded action

Prepare a **non-frozen Claim Extraction Schema** using neutral placeholders only.

The schema may define fields, provenance anchors, `EXPLICIT / INFERRED / UNKNOWN`, interpretation versioning, ambiguity handling, lineage/exposure references and observability checks.

It must NOT be applied to real trading logic until later authority allows claim extraction.
