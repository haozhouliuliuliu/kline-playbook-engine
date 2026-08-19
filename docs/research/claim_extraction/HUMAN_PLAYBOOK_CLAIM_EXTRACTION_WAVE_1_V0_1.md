# HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_1_V0_1

> Version: 0.1
> Date: 2026-08-19
> Status: REAL_SOURCE_FAITHFUL_CLAIM_EXTRACTION / SOURCE_ONLY / NON_FROZEN
> Role: SOURCE_ONLY_CLAIM_EXTRACTION_WAVE_1_ENGINEER
> Prompt/spec: `REAL_CLAIM_EXTRACTION_WAVE1_PUBLIC_V1`
> Retrieval mode: `LOCAL_FREE_PUBLIC_ORIGINAL_SOURCE_BUNDLE_ONLY`
> Claim schema: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
> Protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Source bundle manifest: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_1_MANIFEST.json`
> SOURCE_ONLY session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1.json`
>
> `NO_CANDIDATE_OUTCOME_DATA_USED=YES`

---

## 1. Objective and scope

This is the first REAL source-faithful claim-extraction wave. It is **not** a
backtest, strategy-discovery, statistical-inference, or market-data expansion
task. Its only deliverable is a durable, source-faithful claim library produced
inside the verified project SOURCE_ONLY environment.

The wave extracts **source claims** only, under the three-layer separation:

```text
SOURCE CLAIM != PROJECT / AI INTERPRETATION != MACHINE OPERATIONALIZATION
```

No candidate outcome / PnL / expectancy / Sharpe / win-loss / equity / drawdown
was produced or consulted. No candidate backtest was run. No validation or
historical-final access was used. No canonical market outcomes were read for this
task.

## 2. Selected source and source substitution

- Primary selected source: `SRC-GRIMES` / `MAT-GRIMES-MARKETLIFE` (Adam H. Grimes /
  MarketLife), per the binding authority ordering.
- Source substitution: **NO**. A sufficient free/public Grimes bundle was formed
  directly from three official `adamhgrimes.com` blog pages; no substitution was
  required.
- Selection basis: provenance + anchor quality + extraction suitability only.
  Selection **never** depended on expected profitability, backtest quality, or
  ease of producing a strategy.

## 3. Source bundle (predeclared)

Bundle id: `SB-W1-PUBLIC-GRIMES-V1`
Canonical bundle hash: `e9c60ca1169ff4cb23f2d599e4b74ebf49d6ce04942045b49f271de7eba52170`

| material_id | title | date | URL | role in bundle |
|---|---|---|---|---|
| `SB-W1-M1` | How I Trade (Part 1 of 2) | 2023-10-31 | https://www.adamhgrimes.com/how-i-trade-part-1-of-2/ | market context / review process |
| `SB-W1-M2` | Reader question: what's wrong with Fibonacci? | 2016-03-23 | https://www.adamhgrimes.com/whats-wrong-fibonacci/ | limitation / failure / counterexample |
| `SB-W1-M3` | Marketlifetrading.com and the free trading course | 2017-09-06 | https://www.adamhgrimes.com/marketlife-free-trading-course/ | risk / process / applicability |

All three are official author blog pages: provenance `TRACEABLE_ORIGINAL`,
access `FREE_PUBLIC_UNAUTHENTICATED`.

All three have effective content dates **before 2024-01-01** (before the frozen
corpus start). Under Research Protocol v1.0 section 4, no source-example date
audit is required for the protected windows for this bundle.

## 4. Extraction boundary

- Only official free/public unauthenticated pages were used.
- No paywall bypass, DRM bypass, purchase, subscription, login, credential use,
  or authenticated scraping.
- No invented OHLCV proxy for absent inputs (DOM / order flow / fundamentals /
  news / premium data). Missing inputs are recorded as
  `NOT_OBSERVABLE_WITH_CURRENT_DATA` or `PARTIALLY_OBSERVABLE`.
- No fuzzy language converted into invented numbers (e.g., no silent conversion
  of "strong breakout" into an ATR threshold).
- No candidate outcome or protected-period market retrieval was performed.

## 5. SOURCE_ONLY session (verified)

Session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1.json`

Created through the actual project implementation
`SourceOnlyPolicy.open_verified_session(...)` in `src/research_firewall.py`:

- session id: `SOURCE_ONLY_WAVE1_PUBLIC_V1_20260819`
- model identity: `deepseek-v4-flash`
- prompt/spec version: `REAL_CLAIM_EXTRACTION_WAVE1_PUBLIC_V1`
- source bundle identity: `SB-W1-PUBLIC-GRIMES-V1`
- source bundle hash: `e9c60ca1169ff4cb23f2d599e4b74ebf49d6ce04942045b49f271de7eba52170`
- retrieval mode: `LOCAL_FREE_PUBLIC_ORIGINAL_SOURCE_BUNDLE_ONLY`
- protected market access mode: `TECHNICALLY_DENIED`
- `is_verified == True` (project-issued verification evidence)

Engineering denial path (executed once, no actual retrieval attempted):

```text
outcome = DENIED
reason  = SOURCE_ONLY_TECHNICAL_DENIAL
```

All 15 claim records were appended through the bounded
`SourceOnlyClaimExtractionContext` provenance output surface, bound to this
verified session and to the approved source bundle.

### Exposure note

- Model latent historical knowledge cannot be proven absent; this is a disclosed
  residual threat-model risk under the frozen protocol.
- No project protected-period market-outcome retrieval was available through the
  SOURCE_ONLY runner; the runner technically denies any such request and audits it.
- No canonical market data repository, validation surface, or historical-final
  surface was exposed to this session.

## 6. Claim records (15 claims)

Machine-readable claim records (full Claim Schema v1.0 structural subset):
`docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1.json` -> `claims`.

Summary counts:

```text
CLAIMS = 15
EXPLICIT = 13
INFERRED = 2
UNKNOWN = 0

OBSERVABLE_NOW = 1
PARTIALLY_OBSERVABLE = 3
NOT_OBSERVABLE_WITH_CURRENT_DATA = 1
NOT_APPLICABLE = 10 (process/method claims; observability not a market-data input)

PRIMARY_CANDIDATES = 1  (PRELIMINARY_SOURCE_JUSTIFIED_PRIMARY_CANDIDATE)
PRIMARY_NOT_YET_JUSTIFIED = 14
AMBIGUOUS_STOP = 0
```

### Claim index

| claim_id | status | material | category | observability | primary |
|---|---|---|---|---|---|
| C-W1-001 | EXPLICIT | SB-W1-M1 | SOURCE_INTERPRETATION | NOT_OBSERVABLE_WITH_CURRENT_DATA | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-002 | EXPLICIT | SB-W1-M1 | REVIEW_PROCESS | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-003 | EXPLICIT | SB-W1-M1 | FAILURE_OR_COUNTEREXAMPLE | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-004 | EXPLICIT | SB-W1-M1 | APPLICABILITY | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-005 | EXPLICIT | SB-W1-M1 | REVIEW_PROCESS | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-006 | EXPLICIT | SB-W1-M1 | REVIEW_PROCESS | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-007 | EXPLICIT | SB-W1-M2 | FAILURE_OR_COUNTEREXAMPLE | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-008 | EXPLICIT | SB-W1-M2 | NON_APPLICABILITY | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-009 | EXPLICIT | SB-W1-M2 | OBSERVED_CUE | OBSERVABLE_NOW | PRELIMINARY_SOURCE_JUSTIFIED_PRIMARY_CANDIDATE |
| C-W1-010 | EXPLICIT | SB-W1-M2 | FAILURE_OR_COUNTEREXAMPLE | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-011 | EXPLICIT | SB-W1-M2 | RISK_PROCESS | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-012 | EXPLICIT | SB-W1-M3 | RISK_PROCESS | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-013 | EXPLICIT | SB-W1-M3 | FAILURE_OR_COUNTEREXAMPLE | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-014 | INFERRED | SB-W1-M1 | REVIEW_PROCESS | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W1-015 | INFERRED | SB-W1-M2 | SOURCE_INTERPRETATION | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |

### 6.1 EXPLICIT claims (13) — attributable anchors

Every EXPLICIT claim points to a source anchor (`material_id:url:section/bullet`).
Representative anchors:

- `C-W1-001` — macro/fundamental factors matter but are **not timing signals**;
  data is highly variable; week-to-week / month-to-month numbers should often be
  ignored (with an explicit but undefined exception). Anchor:
  `SB-W1-M1:how-i-trade-part-1-of-2:section:FUNDAMENTAL_AND_MACRO`.
- `C-W1-002` — two ways to identify pattern occurrences: discretionary chart
  marking (subject to a **massive amount of error and influence from the
  researcher**) vs rule-set / computer marking. Anchor:
  `...:section:IMPORTANCE_OF_DOING_YOUR_OWN_WORK`.
- `C-W1-003` — claims that patterns are **100% reliable are impossible**; such
  "encyclopedia" work is **potentially highly misleading**. Anchor: same section.
- `C-W1-004` — some patterns depend on **complex context** (time of day, action/
  volatility in related markets, other unspecified context) and **cannot be
  explained in a simple rule set**. Anchor: same section.
- `C-W1-005` — edge must be compared to a **baseline drawn from the asset
  itself**, not zero (illustrative 6% vs 7-8% buy-and-hold example). Anchor: same
  section.
- `C-W1-006` — **context must be quantified**; "context" is too often the refuge
  of a trader who does not want to do the work to quantify an edge. Anchor:
  `...:section:CAN_THE_WHOLE_BE_MORE_THAN_THE_SUM_OF_THE_PARTS`.
- `C-W1-007` — with Fibonacci levels, **no way to predict which level will hold**;
  levels were violated in live trades; drawing many levels (confluence) may be
  **luck**. Anchor: `SB-W1-M2:whats-wrong-fibonacci:bullet:WHICH_LEVEL_WILL_HOLD`.
- `C-W1-008` — **no quantitative proof** for Fibonacci levels; source places no
  emphasis on them; "**you do not need them**". Anchor:
  `...:bullet:NO_QUANTITATIVE_PROOF`.
- `C-W1-009` — data-supported replacement: **retracements tend to end at about
  50% of the previous swing, with a very large margin of error** (source's own
  qualitative wording; must not be sharpened). Anchor:
  `...:closing:RETRACEMENT_REPLACEMENT`.
- `C-W1-010` — random-data chart study: **patterns appear in random data**;
  challenges "just look at a chart" claims without invalidating real-data
  patterns. Anchor: `...:bullet:RANDOM_DATA_PERCEPTION`.
- `C-W1-011` — price-memory / level use must account for **chart adjustment**
  (futures roll methods, dividends, splits); practitioners often do not. Anchor:
  `...:bullet:PRICE_MEMORY_ADJUSTMENT`.
- `C-W1-012` — trading is **not a get-rich-quick scheme**; you cannot learn with a
  few candlestick patterns; it requires **changing how you think and handle
  risk**. Anchor: `SB-W1-M3:marketlife-free-trading-course:body:NOT_GET_RICH_QUICK`.
- `C-W1-013` — source-acknowledged **process mistake**: making the old course
  entirely free was not sustainable. Anchor:
  `...:body:ACKNOWLEDGED_PROCESS_MISTAKE`.

### 6.2 INFERRED claims (2) — clearly labeled project/AI interpretation

- `C-W1-014` — project/AI synthesis: the source's explicit methodological steps
  (systematic occurrence identification, consistent assumed entry,
  baseline-relative analysis, quantified context) together imply a **coherent
  pre-adoption validation standard** for pattern claims.
- `C-W1-015` — project/AI synthesis: the source's rejection of precise Fibonacci
  ratios combined with his "~50% of previous swing, very large margin of error"
  replacement implies a **preference for simpler, coarser retracement anchors**
  over precise ratio levels.

Both are marked `INFERRED` and are never presented as direct source statements.
They are interpretation records, not source quotes.

## 7. Source vs interpretation separation

- The 13 EXPLICIT claims are direct short excerpts / close paraphrases with
  attributable anchors.
- The 2 INFERRED claims are the only project/AI interpretations and are explicitly
  labeled as such.
- Machine operationalization was **not** performed. All claims remain
  `NOT_STARTED` except `C-W1-009`, which is `INTERPRETATION_REQUIRED` because the
  source's "about 50% ... very large margin of error" needs a source-faithful
  interpretation before any non-outcome operationalization could be considered.

## 8. Observability / make-do rule

For each claim we asked: what did the human observe, do we have it point-in-time,
and can it be represented faithfully with current data?

- `OBSERVABLE_NOW` (1): `C-W1-009` — retracement depth relative to a prior swing
  is representable from the 1-minute OHLCV corpus. Swing definition is an
  interpretation decision, not an observability gap.
- `PARTIALLY_OBSERVABLE` (3): `C-W1-004` (time-of-day is derivable; related-market
  context only partially available; other context factors unspecified),
  `C-W1-007` (OHLCV is observable, but the specific discretionary levels and their
  confluence are not defined by the source, so a faithful representation is not
  determined), and `C-W1-011` (project corpus adjustment/roll semantics determine
  whether price-memory levels are preserved; adjustment metadata only partially
  documented — see the LIMIT-001 class of limitations).
- `NOT_OBSERVABLE_WITH_CURRENT_DATA` (1): `C-W1-001` — fundamental/macro data
  series are absent; **no faithful OHLCV proxy was invented**.
- `NOT_APPLICABLE` (10): process/method/counterexample claims that do not rely on
  a market-data input.

One non-observable claim did **not** block the wave; the remaining useful claims
were extracted normally.

## 9. Ambiguity

- `AMBIGUOUS_STOP = 0`: no claim required a stop because the source meaning was
  unambiguous at the claim level.
- Genuine ambiguity is preserved in `ambiguity_notes` and `UNKNOWN` fields
  (e.g., `C-W1-009`'s "very large margin of error" precision, `C-W1-004`'s
  unspecified "other aspects of context", `C-W1-001`'s undefined exception).
- No outcome data was used to resolve any ambiguity.

## 10. Negative / failure evidence

Negative / failure context is present in the bundle and preserved:

- `C-W1-003` — counterexample: "100% reliable" pattern encyclopedias impossible.
- `C-W1-007` — invalidation: Fibonacci levels violated in live trades; cannot
  predict which level holds.
- `C-W1-008` — failure: no quantitative proof found for Fibonacci levels.
- `C-W1-010` — counterexample: patterns appear in random data; challenges visual
  chart evidence.
- `C-W1-011` — data-integrity caution: chart adjustment / price-memory.
- `C-W1-013` — source-acknowledged process failure (unsustainable all-free model).

Recorded absence / limitation: the bundle contains no explicit
no-trade-example inventory or systematic loss-example ledger; that is a
source-quality limitation of this bundle and is recorded rather than
manufactured.

## 11. PRIMARY readiness

- Only `C-W1-009` carries `PRELIMINARY_SOURCE_JUSTIFIED_PRIMARY_CANDIDATE` because
  the source states a single clear behavioral replacement (retracements ~50% of
  prior swing with a very large margin of error) from which a unique
  source-justified preliminary primary can be identified.
- All other claims are `PRIMARY_NOT_YET_JUSTIFIED`. PRIMARY branch selection for
  outcome testing is a later Protocol v1.0 step and is **not** performed in this
  extraction wave.
- No outcome data was used to form or test any primary candidate.

## 12. Copyright boundary

- Store traceability, not a redistribution archive.
- Only attributable short excerpts and concise paraphrases are recorded in the
  JSON/markdown artifacts; full copyrighted articles/courses are not stored.
- Raw HTML was not retained (retention boundary recorded in the manifest).

## 13. Optional paid candidates (awareness only)

Encountered and recorded for awareness only (no purchase / subscription):

1. MarketLife paid education platform (subscriptions, premium courses, daily
   market insight) — could later clarify defined context factors and systematic
   failure/invalidation examples.
2. Adam Grimes, *The Art and Science of Technical Analysis* (book) — book-length
   synthesis of the free material's method.

`PAID_SOURCE_PURCHASE_DEFAULT=NO`; free/public alternatives were sufficient, so
the wave continued without any paid access.

## 14. Anti-regression / self-review checklist

- No EXPLICIT claim contains AI inference (the two synthesis records are
  INFERRED and labeled).
- No invented threshold: "about 50% ... very large margin of error" is recorded
  as the source's own qualitative wording, not sharpened.
- No fake OHLCV proxy for DOM / order flow / fundamentals / news.
- Limitation/failure context preserved and absence recorded.
- No source chosen for apparent profitability.
- No paid/authenticated material used.
- No public alternative ignored because a paid source looked better.
- EXPLICIT anchors are traceable to official URLs + section/bullet.
- SOURCE_ONLY identities internally consistent across session / bundle / claims.
- No candidate outcome / protected-period market data touched.

`NO_CANDIDATE_OUTCOME_DATA_USED=YES`

## 15. Durable artifacts produced

- `docs/research/claim_extraction/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_1_V0_1.md` (this file)
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_1_MANIFEST.json`
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1.json`
- `tools/run_claim_extraction_wave1_source_only.py` (reproducible SOURCE_ONLY driver)
