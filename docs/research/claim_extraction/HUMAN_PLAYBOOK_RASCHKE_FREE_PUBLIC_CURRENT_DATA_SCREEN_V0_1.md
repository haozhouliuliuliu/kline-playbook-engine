# HUMAN_PLAYBOOK_RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V0_1

> Version: 0.1
> Date: 2026-08-19
> Status: REAL_SOURCE_SCREEN + BOUNDED_CLAIM_EXTRACTION / SOURCE_ONLY / NON_FROZEN
> Role: RASCHKE_FREE_PUBLIC_CURRENT_DATA_COMPATIBILITY_SCREEN_ENGINEER
> Prompt/spec: `RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V1`
> Retrieval mode: `LOCAL_FREE_PUBLIC_RASCHKE_SOURCE_SCREEN_ONLY`
> Source: `SRC-RASCHKE`
> Source dossier: `docs/research/source_dossiers/SOURCE_DOSSIER_RASCHKE_V0_1.md`
> Claim schema: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
> Protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Source bundle manifest: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json`
> SOURCE_ONLY session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_SCREEN_V0_1.json`
>
> `NO_CANDIDATE_OUTCOME_DATA_USED=YES`
> `CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED`
> `VALIDATION_ACCESS=LOCKED`
> `HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED`

---

## 1. Objective and scope

This is a **source screen + bounded claim extraction** package for Linda Bradford
Raschke's official free/public material. It is **not** a backtest, strategy
mining, parameter search, statistical inference, or a request to manufacture a
Playbook Contract.

The purpose is to determine whether Raschke's free/public original material
contains **at most ONE source-faithful trading family** that is sufficiently
compatible with the project's existing 1-minute OHLCV + governed session
metadata to justify a later targeted semantic-completion package.

Output target (per binding authority
`docs/research/HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_2.md`):

```text
RASCHKE_CURRENT_DATA_FAMILY_SELECTED=<ONE exact family | NONE>
```

At most ONE family may be selected. A `NONE` is a valid, successful result.

## 2. Authority read

Read before execution (from latest `origin/main` @ `6b548158dc9f60cd5bd5a3158733d16f7c0cb3f7`):

- `AGENTS.md`
- `OWNER_COLLABORATION_CONTRACT.md`
- `CURRENT_STATE.md`
- `RESEARCH_DIRECTION.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_2.md`
- `docs/research/source_dossiers/SOURCE_DOSSIER_RASCHKE_V0_1.md`
- `docs/reviews/STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_SEMANTIC_COMPLETION_INTEGRATION_REVIEW_V0_1.md`
- `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`
- `src/research_firewall.py`
- `tests/test_research_firewall.py`

All expected authorities were present at the exact paths. No missing-authority
substitution was required.

## 3. Hard research boundaries (HUMAN_PLAYBOOK_FIRST)

Forbidden and not performed:

- data-first K-line/chart mining
- indicator discovery
- pattern mining from canonical prices
- parameter search
- candidate backtests
- candidate PnL/returns, expectancy, Sharpe, win/loss, equity/drawdown
- DEVELOPMENT candidate outcome inspection
- Validation access
- historical-final access
- canonical market-outcome calibration

```text
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

The statistical positive-acceptance package remains parked. No protected-period
market outcomes were read, retrieved, or exposed.

## 4. Acquisition method and limitations

### 4.1 Video surface (NOT acquired — no circumvention)

The official video index (`https://lindaraschke.net/linda-videos/`) links its
videos only to the official YouTube channel (`@lindaraschke6565`); there are no
direct embeds, mp4, or m3u8 links on the official domain. The recorded
environment blocks YouTube public URL media download with a stable `403`
without cookies. Under the source-acquisition policy and tool-admission close-out
(`TOOL_DECISION=USE_EXISTING`), the video path was **not** circumvented.

```text
VIDEO_ACQUISITION=BLOCKED_BY_403_IN_RECORDED_ENV
CIRCUMVENTION_ATTEMPTED=NO
FALLBACK=OFFICIAL_FREE_ARTICLE_TEXT_MATERIAL (task-stated fallback)
```

One inaccessible video is not a project blocker.

### 4.2 Official free article/text material (acquired)

Eleven official free/public PDF articles hosted on the official domain
(`lindaraschke.net/wp-content/uploads/...`) were directly reachable without
authentication (HTTP 200, `application/pdf`, `%PDF-`). Eight contained an
embedded text layer and were used. Three (`Multi-Market Traders Rule`,
`Trade Trends`, `Trading Insights`) are image-only scans with no embedded text
layer; no OCR tool is installed (adding one would be a new framework), and they
are low-priority profile/interview pieces, so they were excluded and recorded in
the bundle manifest.

Tooling used (existing / minimal):
- `requests` (already present in the private probe venv) for download;
- `pypdf` (pure-Python text parser) installed **only** in the private isolated
  probe venv for text extraction of already-lawfully-acquired public documents.
  This is a parsing dependency, not a new acquisition framework.

Raw PDFs and full extracted text were written to a local **temp** directory
outside the repository and were **not** committed. Only attributable short
excerpts and concise paraphrases are recorded in project artifacts.

```text
ACQUISITION_TOOL_DECISION=USE_EXISTING
NEW_ACQUISITION_FRAMEWORK_INSTALLED=NO
PDF_PARSER=pypdf (private probe venv only)
RAW_OR_FULL_COPY_COMMITTED=NO
```

## 5. Source-bundle manifest

Bundle id: `SB-RASCHKE-PUBLIC-SCREEN-V1`
Canonical bundle hash: `7b11a8f1516696e2e54f9dc0ee4d7785f8f1cd9dad06d52abe15378edd2633bd`
Full manifest: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json`

| material_id | title | publication | effective date | role |
|---|---|---|---|---|
| SR-V0-M01 | Short Term Trading Strategies | AIQ Opening Bell | 1997-08 | market timing; no-trade; Holy Grail; gap reversal; Wolfe Wave; stops; failure example |
| SR-V0-M02 | The Discerning Trader | Stocks & Commodities V.11:9 | 1993-09 | NR7 breakout; prior-day levels; breakout vs swing mode; ADX rules; pullback to 20 EMA; 3-10 oscillator; contraction |
| SR-V0-M03 | Trading Style and Daily Market Regimen | Active Trader | 2004-02 | trend-day definition/setup/confirmation; NR7 + early-morning-range bracket; wide-range bar; two-period ROC; flags + volatility filter; session windows |
| SR-V0-M04 | The Rituals of Trading | Active Trader | 2000-08 | price-based emphasis; three pushes; management; risk; execution; bull/bear flags; TICK-as-momentum (boundary) |
| SR-V0-M05 | Traders Toolbox | Active Trader | 2004-03 | indicator checklist; Holy Grail across time frames; bar-close-position tendency; cross-market leading (boundary) |
| SR-V0-M09 | Maintain your Mindset | Stock Futures & Options | 2004-07 | psychology/process (record only) |
| SR-V0-M10 | Who are You? | Stock Futures & Options | 2003-08 | behavior/process (record only) |
| SR-V0-M11 | Everything about Electronic Trading | Stock Futures & Options | 2006-04 | execution/process (record only) |

All materials: `provenance=TRACEABLE_ORIGINAL`, `access=FREE_PUBLIC_UNAUTHENTICATED`,
`source_example_date_status=PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES`.

## 6. Source date / protected-window audit

All eight selected materials have **effective content dates before 2024-01-01**
(before the frozen corpus start). The WordPress `/2026/01/` and `/2026/03/`
upload paths are site-rebuild artifact folders, **not** content dates; the
content dates are the original magazine publication dates (1993, 1997, 2000,
2003, 2004, 2006) evidenced in-document.

Under Research Protocol v1.0 section 4:

```text
if effective_content_date < protected_window_start (2024-01-01)
-> no example-date audit is required for that protected window
```

The in-document example dates (e.g., 1997 stock examples CHV/CMZ/AXP/ETN; 2003
S&P index examples; 2000 S&P pullback example) are all pre-2024. No 2024/2025
market examples appear in any selected material.

```text
SOURCE_EXAMPLE_DATE_STATUS=PRE_2024_VERIFIED_NO_PROTECTED_WINDOW_EXAMPLES (all 8)
PROTECTED_WINDOW_EXAMPLE_EXPOSURE=NONE
```

## 7. SOURCE_ONLY session (verified)

Session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_SCREEN_V0_1.json`

Created through the actual project implementation
`SourceOnlyPolicy.open_verified_session(...)` in `src/research_firewall.py`:

- session id: `SOURCE_ONLY_RASCHKE_SCREEN_V1_20260819`
- model identity: `deepseek-v4-flash`
- prompt/spec version: `RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_V1`
- source bundle identity: `SB-RASCHKE-PUBLIC-SCREEN-V1`
- source bundle hash: `7b11a8f1516696e2e54f9dc0ee4d7785f8f1cd9dad06d52abe15378edd2633bd`
- retrieval mode: `LOCAL_FREE_PUBLIC_RASCHKE_SOURCE_SCREEN_ONLY`
- protected market access mode: `TECHNICALLY_DENIED`
- `is_verified == True` (project-issued verification evidence)

Engineering denial path (executed once, no actual retrieval attempted):

```text
outcome = DENIED
reason  = SOURCE_ONLY_TECHNICAL_DENIAL
```

All 24 claim records were appended through the bounded
`SourceOnlyClaimExtractionContext` provenance output surface, bound to this
verified session and to the approved source bundle.

### Exposure note (disclosed residual threat-model risk)

- Model latent historical knowledge cannot be proven absent; this is a disclosed
  residual threat-model risk under the frozen protocol.
- No project protected-period market-outcome retrieval was available through the
  SOURCE_ONLY runner; the runner technically denies any such request and audits it.
- No canonical market data repository, validation surface, or historical-final
  surface was exposed to this session.
- Any automatic transcript is not treated as exact quotation unless verified
  (no transcripts were used in this package; only official article text).

## 8. Claim extraction boundary and inventory

Only enough high-information claims to support the family screen were extracted
(24 claims, within the target 12-24; the count is not forced). Claims use the
canonical statuses `EXPLICIT | INFERRED | UNKNOWN`; `UNKNOWN` is preferred over
guessing. All 24 claims are `EXPLICIT` (each points to an attributable source
anchor with a short excerpt/paraphrase). No claim is a machine
operationalization.

Machine-readable claim records (full structural subset):
`docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_SCREEN_V0_1.json` -> `claims`.

Summary counts:

```text
CLAIMS = 24
EXPLICIT = 24
INFERRED = 0
UNKNOWN = 0

OBSERVABLE_NOW = 12
PARTIALLY_OBSERVABLE = 10
NOT_OBSERVABLE_WITH_CURRENT_DATA = 2
NOT_APPLICABLE = 0

PRIMARY_CANDIDATES = 0
PRIMARY_NOT_YET_JUSTIFIED = 24
AMBIGUOUS_STOP = 0
```

### Claim index

| claim_id | status | material | category | observability |
|---|---|---|---|---|
| C-RAS-001 | EXPLICIT | SR-V0-M01 | NO_TRADE | OBSERVABLE_NOW |
| C-RAS-002 | EXPLICIT | SR-V0-M01 | OBSERVED_CUE | PARTIALLY_OBSERVABLE |
| C-RAS-003 | EXPLICIT | SR-V0-M01 | ACTION_PERMISSION | OBSERVABLE_NOW |
| C-RAS-004 | EXPLICIT | SR-V0-M01 | ACTION_PERMISSION | OBSERVABLE_NOW |
| C-RAS-005 | EXPLICIT | SR-V0-M01 | OBSERVED_CUE | PARTIALLY_OBSERVABLE |
| C-RAS-007 | EXPLICIT | SR-V0-M02 | ACTION_PERMISSION | OBSERVABLE_NOW |
| C-RAS-008 | EXPLICIT | SR-V0-M02 | MARKET_CONTEXT | OBSERVABLE_NOW |
| C-RAS-009 | EXPLICIT | SR-V0-M02 | NO_TRADE | OBSERVABLE_NOW |
| C-RAS-010 | EXPLICIT | SR-V0-M02 | ACTION_PERMISSION | OBSERVABLE_NOW |
| C-RAS-011 | EXPLICIT | SR-V0-M02 | MARKET_CONTEXT | PARTIALLY_OBSERVABLE |
| C-RAS-012 | EXPLICIT | SR-V0-M03 | MARKET_CONTEXT | OBSERVABLE_NOW |
| C-RAS-013 | EXPLICIT | SR-V0-M03 | OBSERVED_CUE | OBSERVABLE_NOW |
| C-RAS-014 | EXPLICIT | SR-V0-M03 | CONFIRMATION | PARTIALLY_OBSERVABLE |
| C-RAS-015 | EXPLICIT | SR-V0-M03 | ACTION_PERMISSION | OBSERVABLE_NOW |
| C-RAS-016 | EXPLICIT | SR-V0-M03 | OBSERVED_CUE | OBSERVABLE_NOW |
| C-RAS-017 | EXPLICIT | SR-V0-M03 | NO_TRADE | PARTIALLY_OBSERVABLE |
| C-RAS-018 | EXPLICIT | SR-V0-M03 | OBSERVED_CUE | PARTIALLY_OBSERVABLE |
| C-RAS-019 | EXPLICIT | SR-V0-M03 | ACTION_PERMISSION | PARTIALLY_OBSERVABLE |
| C-RAS-020 | EXPLICIT | SR-V0-M03 | FAILURE_OR_COUNTEREXAMPLE | PARTIALLY_OBSERVABLE |
| C-RAS-021 | EXPLICIT | SR-V0-M04 | MANAGEMENT | PARTIALLY_OBSERVABLE |
| C-RAS-023 | EXPLICIT | SR-V0-M05 | OBSERVED_CUE | OBSERVABLE_NOW |
| C-RAS-024 | EXPLICIT | SR-V0-M02 | MARKET_CONTEXT | PARTIALLY_OBSERVABLE |
| C-RAS-025 | EXPLICIT | SR-V0-M04 | OBSERVED_CUE | NOT_OBSERVABLE_WITH_CURRENT_DATA |
| C-RAS-026 | EXPLICIT | SR-V0-M05 | OBSERVED_CUE | NOT_OBSERVABLE_WITH_CURRENT_DATA |

### Representative EXPLICIT claims (source layer only)

- `C-RAS-001` — "The worst thing you can do in terms of market timing is to buy in
  the middle of a trading range. Either buy new highs, or buy pullbacks, but
  don't put your capital to work in the middle of a trading range."
- `C-RAS-007` — NR7 day = "the narrowest trading range in the last seven days";
  "buying the breakout of an NR7 day ... going with the volatility" (cocoa
  commodity-futures chart example).
- `C-RAS-012` — trend day definition: "opens on one end of its range and closes
  on the opposite end, has range expansion, and makes a steady pattern of higher
  highs and higher lows, or vice versa."
- `C-RAS-013` — three trend-day precursors: (1) significant range contraction
  "such as an NR7 day, which is a bar with the narrowest range of the past seven
  bars"; (2) large opening gap; (3) approaching new 20-day highs/lows (magnets).
- `C-RAS-015` — "Something I'll almost always do the day after an NR7 day is
  bracket stops around the early morning range ... it didn't matter whether you
  bracketed the first 45 minutes range or the first hour's range. If there's
  going to be a trend day, you're going to catch it."
- `C-RAS-014` — trend-day confirmation: large opening 15-min bar (Crabel),
  volume increase, leadership, trendiness 10-10:30/10:45, and "the last and most
  important thing is ... trend in the market breadth" (advancing minus
  declining — NOT owned).
- `C-RAS-025` / `C-RAS-026` — observability boundaries: NYSE TICK used as a
  momentum oscillator; DAX/EuroStoxx cross-market leading. Both
  `NOT_OBSERVABLE_WITH_CURRENT_DATA`; no OHLCV proxy is authorized.

## 9. Source vs interpretation separation

- All 24 claims are **SOURCE CLAIMS** (`EXPLICIT`), each bound to an attributable
  anchor and short excerpt/paraphrase.
- No project/AI interpretation claim was required to be recorded as `INFERRED`
  in this screen; the screen's interpretive conclusions (family selection,
  instrument transfer, semantic-field classifications) are documented **in this
  dossier and the family handoff**, not as source claims.
- Machine operationalization was **not** performed. All claims remain
  `NOT_STARTED`; `PRIMARY_BRANCH_STATUS=PRIMARY_NOT_YET_JUSTIFIED` for all.

The mandatory separation is preserved:

```text
SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION
```

## 10. Observability matrix (selected family inputs)

For every required source input of the screened families, the classification is:

| Source input | Family use | Classification |
|---|---|---|
| raw bar open/high/low/close | all price-based families | OBSERVABLE_NOW |
| daily bar range (for NR7 = narrowest of past 7 bars) | NR7/trend-day | OBSERVABLE_NOW |
| session/time (early morning range 45-min or 1-hour; daily bar boundary) | NR7/trend-day bracket entry | OBSERVABLE_NOW |
| prior-day high/low | prior-day reference framework | OBSERVABLE_NOW |
| ordinary 1-min volume (breakout/expansion confirmation) | trend-day confirmation | OBSERVABLE_NOW (raw exists; "significant increase" is PARTIALLY_PINNED) |
| gap (open vs prior close) | trend-day precursor; gap rules | OBSERVABLE_NOW |
| 20-day high/low (magnet level) | trend-day precursor | OBSERVABLE_NOW |
| 20-period EMA / ADX / two-period ROC | Holy Grail / pullback / momentum | OBSERVABLE_NOW (derived from OHLC; indicator layer) |
| volatility (range/ATR) as filter | flags / contraction | OBSERVABLE_NOW (raw) |
| NYSE TICK / breadth (advancing minus declining) | trend-day confirmation handicap; TICK momentum | NOT_OBSERVABLE_WITH_CURRENT_DATA (no proxy) |
| DAX/EuroStoxx cross-market | context handicap | NOT_OBSERVABLE_WITH_CURRENT_DATA (no proxy) |
| bid/ask order flow, DOM | scalping execution | NOT_OBSERVABLE_WITH_CURRENT_DATA (no proxy) |
| visual discretionary pattern (flags, Wolfe Wave points, "three pushes") | flag/Wolfe/pushes families | PARTIALLY_OBSERVABLE (raw price observable; identification discretionary, not pinned) |

The rule from Protocol v1.0 / Claim Schema v1.0 is preserved: a missing input
does not authorize an invented OHLCV proxy. In particular, NYSE TICK/breadth and
Market-Profile-style inputs are **not** replaced by ordinary bar volume or
range-derived indicators.

## 11. Family candidates screened

### 11.1 NR7 / Range-Contraction → Trend-Day Breakout (SELECTED)

**SOURCE_FAMILY_NAME:** `RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT`
(contraction/expansion; going with the volatility after an NR7 day, including
the day-after-NR7 early-morning-range bracket and the NR7-day breakout).

**SOURCE_ORIGINALITY_OR_LINEAGE:** Multi-lineage. The NR7 measure is attributed by
Raschke to Toby Crabel (contraction/expansion; the 1993 S&C article lists
Crabel's "The principle of contraction/expansion" and "Opening range breakout").
Raschke's own tested practice statements ("Something I'll almost always do the
day after an NR7 day is bracket stops around the early morning range ... when I
tested this out about five years ago") and her NR7-breakout usage are Raschke's
own. The family is therefore a source-faithful Raschke-used family with a
documented lineage component; the lineage is disclosed, not hidden.

**INSTRUMENT_SCOPE:** S&P index futures (2004 Active Trader context); US equities
(2004 context); commodity futures — the 1993 S&C NR7 chart example is September
Cocoa (commodity futures). 

```text
SOURCE_INSTRUMENT_SCOPE=US_EQUITY_INDEX_FUTURES_AND_US_EQUITIES_AND_COMMODITY_FUTURES (NR7 concept shown on commodity futures)
SOURCE_SUPPORTS_COMMODITY_FUTURES=YES (NR7/contraction-expansion concept explicitly shown on commodity futures: cocoa)
SOURCE_SUPPORTS_CROSS_MARKET_TRANSFER=UNKNOWN (no explicit statement about transferring the exact bracket trade across asset classes)
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN (no explicit statement about Chinese futures; transfer is INFERRED, see section 14)
```

**TIMEFRAME_SCOPE:** NR7 is defined on the daily bar (narrowest range of the past
seven bars). The entry bracket is intraday (first 45 minutes or first hour of
the next session). The source states the underlying patterns occur across time
frames. Multi-timeframe applicability is explicit; no single operating
timeframe is uniquely pinned for the whole loop.

**MARKET_CONTEXT:** range contraction / low-volatility condition preceding an
expansion; the source's umbrella statement "you have to have some method of
measuring the amount of contraction in the market ... that tells me to switch to
a breakout mode"; trend-day precursors (contraction, large opening gap,
approaching new 20-day highs/lows).

**SETUP:** NR7 day — a bar with the narrowest range of the past seven bars.

**OBSERVED_CUE:** narrow-range price bars / low volatility; loss of oscillator
oscillation/extreme readings (discretionary alternate proxy).

**ENTRY_PERMISSION:** (1993) buy the breakout of the NR7 day high (going with the
volatility); (2004) the day after an NR7 day, bracket stops around the early
morning range (the source states either the first 45 minutes or the first hour
worked in her test).

**CONFIRMATION:** volume increase on the breakout/expansion (qualitative);
trend-day confirmation components (large opening 15-min bar; leadership;
trendiness 10-10:30/10:45; trend in breadth — the breadth component is
`NOT_OBSERVABLE_WITH_CURRENT_DATA` and is treated as a handicap, not the entry
trigger).

**INVALIDATION:** for the bracket entry, the opposite side of the bracketed range
being taken out invalidates the intended trend-day direction; "the minute the
market gives back more than it should, you get out on the first reaction or
pause."

**NO_TRADE:** no trade if the anticipated trend-day expansion does not develop;
flags/no-volatility failure conditions; "I'm wrong 90 percent of the time if I
try to guess a breakout" (use defined levels, not guesses).

**MANAGEMENT:** bracket stops; get out on first reaction/pause when the market
gives back more than it should; take at least half off at an uncertain price
objective.

**EXIT_OR_TARGET:** ride the trend day (the trend day by definition makes range
expansion and steady higher highs/higher lows); "if there's going to be a trend
day, you're going to catch it"; exit when the trend-day behavior fails.

**FAILURE_OR_COUNTEREXAMPLE:** NR7 does not guarantee a trend day; flags fail at
volatility extremes and in contracting volatility; the source's breakout-guess
failure statement; "statistical reliability only comes with a volatility filter."

**REQUIRED_INFORMATION_SURFACES:** raw bar OHLCV; daily bar ranges; session/time
metadata (early morning range, daily bar boundary); ordinary volume (confirmation);
gaps; 20-day highs/lows. Confirmation handicap additionally references NYSE
TICK/breadth (unavailable, not proxied).

**Semantic-field classification (important fields):**

```text
NR7_DEFINITION                        = EXPLICITLY_PINNED
EARLY_MORNING_RANGE_WINDOW            = PARTIALLY_PINNED (source: 45-min or 1-hour both worked in her test)
BRACKET_ENTRY_AFTER_NR7               = EXPLICITLY_PINNED (source practice statement)
NR7_BREAKOUT_ENTRY                     = EXPLICITLY_PINNED (1993)
TREND_DAY_DEFINITION                   = EXPLICITLY_PINNED (price-based)
TREND_DAY_PRECURSORS                   = EXPLICITLY_PINNED (3 conditions; unquantified sizes are PARTIALLY_PINNED)
TREND_DAY_CONFIRMATION                 = PARTIALLY_PINNED (volume/session observable; breadth REQUIRES_UNAVAILABLE_INPUT)
INVALIDATION_REFERENCE                 = EXPLICITLY_PINNED (opposite bracket side / fresh behavior failure)
EXIT_OR_TARGET_SEMANTICS               = PARTIALLY_PINNED ("ride the trend day"; "gives back more than it should")
VOLUME_ROLE                           = PARTIALLY_PINNED ("significant increase" qualitative)
TIMEFRAME_SCOPE                        = PARTIALLY_PINNED (NR7 daily; bracket intraday; multi-timeframe stated)
```

### 11.2 Holy Grail / pullback to 20-period EMA with ADX>30 (REJECTED as selected)

Two-article anchored (1997 AIQ rules; 2004 Active Trader part 2 setup detail
across time frames). Explicit 4-step buy rules. However it is primarily
**indicator-dependent** (14-period ADX, 20-period EMA), which is outside the
task's preferred price/volume/session family basis, and its examples are US
equities / S&P index with no commodity-futures anchor. It remains a useful
source claim set but is not the single best current-data-compatible family for a
full trading-loop semantic completion under the task preference.

### 11.3 Wide-range bar reversal (REJECTED as selected)

"Today has the widest range of the past four days ... the least-probable
scenario"; down-closing wide-range bar + high taken out within two days = buy
signal (~20% of the time). Purely price-based and `OBSERVABLE_NOW`, but it is a
single-article signal/tendency with no pinned stop/exit/target management loop,
so it is insufficient for a complete trading-loop semantic completion on its
own.

### 11.4 Two-period ROC momentum buy-day (REJECTED as selected)

Explicit two-period ROC cue and momentum buy-day setup, but indicator (ROC)
based with a rough "strong" reference window (3-4 weeks); partial trading loop;
not commodity-anchored.

### 11.5 Bull/bear flags continuation + volatility filter (REJECTED as selected)

The source describes flags as "the best risk-reward ratios of any technique"
and explicitly requires a volatility filter, but flag identification is
described as visual/discretionary ("a million ways to identify a continuation
pattern such as a flag"); no objective flag definition is pinned, so it is not
source-faithfully draftable without inventing a flag detector.

### 11.6 Scalping (S&P index futures) (REJECTED)

Depends on bid/ask order flow, execution platform skills, and NYSE TICK/breadth;
the 2004 article states scalping requires "really good execution skills," buying
on the bid and selling on the offer. These inputs are not in the OHLCV corpus and
no proxy is authorized.

### 11.7 Three-Day Unfilled Gap Reversal (REJECTED as selected)

Explicit and `OBSERVABLE_NOW`, but a single-article pattern with a narrow
structure and no commodity-futures anchor; less complete trading loop than the
NR7/trend-day family.

### 11.8 Wolfe Wave (REJECTED)

Construction rules are explicit but recognition is described as a trained-eye
skill ("magically trained eye"); point selection is discretionary; not
source-faithfully machine-draftable.

### 11.9 Taylor Trading / Trade Location (NOT SCREENED — video blocked)

The task-listed video "Day Type, Taylor Trading, Trade Location, More" is
YouTube-hosted and blocked; no official free article text on Taylor Trading was
found on the official domain. Recorded as not-screened due to the video
acquisition boundary, not as a rejected family.

## 12. Selection rule evaluation (selected family)

1. original/free source provenance is adequate — **YES** (official lindaraschke.net,
   TRACEABLE_ORIGINAL, two-article anchoring for NR7).
2. not primarily dependent on unavailable inputs — **YES** (core setup/entry is
   price/session/volume; breadth/TICK is a confirmatory handicap, recorded as
   unavailable, not proxied).
3. key trading-loop semantics are at least plausibly source-completable — **YES**
   (setup/entry explicit; invalidation and management present; exit/target
   partially pinned and flagged for the semantic-completion package).
4. current data surface materially covers required raw inputs — **YES** (bar
   OHLCV, daily ranges, session metadata, volume, gaps, 20-day levels).
5. instrument transfer is either source-supported or clearly separable as a
   later INFERRED hypothesis — **YES** (commodity-futures anchor for the NR7
   concept; exact bracket trade transfer to Chinese futures labeled INFERRED).
6. selection requires no outcome data and no invented thresholds — **YES** (NR7
   and bracket windows are source-pinned; no invented numeric thresholds).

Selection basis is provenance + current-data compatibility + semantic potential
only. It is **not** based on expected profitability.

## 13. Rejected-family reasons (summary)

See section 11.2-11.9. Common rejection themes: indicator-dependence outside the
price/volume/session preference (Holy Grail, two-period ROC); single-article
signal with incomplete management loop (wide-range bar, gap reversal);
visual/discretionary identification not source-mechanically pinned (flags, Wolfe
Wave, three-pushes); unavailable execution/order-flow inputs (scalping); and
video-blocked not-screened (Taylor Trading).

## 14. Instrument-transfer analysis (selected family)

```text
SOURCE_INSTRUMENT_SCOPE=US_EQUITY_INDEX_FUTURES_AND_US_EQUITIES_AND_COMMODITY_FUTURES
SOURCE_SUPPORTS_COMMODITY_FUTURES=YES
SOURCE_SUPPORTS_CROSS_MARKET_TRANSFER=UNKNOWN
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
```

- The NR7 / contraction-expansion **concept** is explicitly shown on a commodity
  futures chart (September Cocoa, 1993 S&C figure: "The low volatility leads to
  a trend"), which is positive evidence that the source applies the concept to
  commodity futures.
- The exact day-after-NR7 early-morning-range **bracket practice** is stated in
  an index-futures context (S&P), so transferring that exact entry/management to
  `cu/al/ni/au/ag/rb` is **not** an explicit source statement.
- Therefore any Chinese-futures operationalization is a separately labeled
  `INFERRED` project hypothesis and does not inherit source authority
  automatically (same discipline as the accepted Steenbarger integration review:
  `NO_AS_SOURCE_SUPPORT_STATEMENT`).

```text
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
NO in these fields means source support is absent, not that project evidence proves the setup cannot work.
```

## 15. Missing inputs (selected family)

- NYSE TICK / breadth (advancing minus declining) — used by the source for
  trend-day confirmation handicap; `NOT_OBSERVABLE_WITH_CURRENT_DATA`; **not**
  proxied with OHLCV.
- DAX/EuroStoxx cross-market leading — context handicap; `NOT_OBSERVABLE_WITH_CURRENT_DATA`; not proxied.
- Bid/ask order flow (scalping) — outside the selected family core; not proxied.
- A single pinned "early morning range" window — the source explicitly permits
  either 45-min or 1-hour (her test showed both worked); selecting one for the
  project is a source-permitted window choice (an `INFERRED` project convention),
  not an invented threshold.

## 16. Failure / no-trade evidence (selected family and source)

- NR7 does not guarantee a trend day (the bracket "catches" a trend day only if
  there is going to be one).
- Flags (continuation) fail at volatility extremes (V-spike) and in contracting
  volatility; "statistical reliability only comes with a volatility filter."
- "If I try to guess a breakout, I'm wrong 90 percent of the time" — no-trade
  against guessing; use defined levels.
- "The worst thing you can do ... is to buy in the middle of a trading range"
  — no-trade / entry-location rule.
- Eaton Corp Holy Grail example (1997): "no reason to be in this trade" — a
  source-acknowledged no-trade/failure case for the pullback pattern.
- Management counterexample language: "the minute the market gives back more
  than it should, you get out on the first reaction or pause."

## 17. Optional paid candidates (encountered; listed for awareness only)

- "Trading Sardines" (Raschke book, 2015) — paid book; potential deeper
  trading-loop semantics.
- "Street Smarts: High Probability Short-Term Trading Strategies" (Raschke &
  Connors) — paid book; source for the 1997-referenced patterns.
- NYSE TICK / TRIN / advance-decline breadth data — paid/subscription data;
  would fill the trend-day confirmation handicap surface.
- Keltner/ADX charting packages (e.g., TradeStation) — paid software; the
  indicators are computable from owned OHLCV, so this is a tool-awareness item,
  not a data gap.

No purchase, subscription, login, or credential use was performed or authorized.
`PAID_SOURCE_PURCHASE_DEFAULT=NO`.

## 18. Selection verdict

```text
RASCHKE_CURRENT_DATA_FAMILY_SELECTED=RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT
SELECTED_FAMILY_STATUS=SELECTED_FOR_TARGETED_SEMANTIC_COMPLETION
PLAYBOOK_CONTRACT_CREATED=NO
PRIMARY_LOCKED=NO
OPERATIONALIZED=NO
VALIDATED=NO
BACKTEST_AUTHORIZED=NO
```

This selection means: the family is sufficiently compatible with the current
1-minute OHLCV + governed session metadata, and its core semantics are
plausibly source-completable, to justify a **later targeted semantic-completion
package**. It does **not** authorize any Playbook Contract, operationalization,
or outcome testing in this package.

## 19. Exact next semantic-completion questions

If a targeted semantic-completion package is authorized for
`RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT`, it must resolve (source-only):

1. **NR7 day definition** — confirm the daily-bar NR7 (narrowest range of the
   past seven bars) applied to the governed Chinese-futures daily bar; is the
   daily bar boundary the governed session/calendar day?
2. **Early-morning-range window** — the source permits first-45-minutes or
   first-hour; which project convention (if either) is chosen, and is it
   recorded as an `INFERRED` project convention rather than a source claim?
3. **Bracket entry construction** — exact bracket stop placement above/below the
   early-morning-range high/low (the source does not pin tick offsets);
   invalidation = opposite bracket side.
4. **Trend-day definition operationalization** — open-on-one-end/close-opposite,
   range expansion, steady higher highs/higher lows: exact measurable
   formulation without inventing thresholds.
5. **Volume confirmation** — is "significant increase" source-completable or must
   it remain a qualitative, non-gated confirmation?
6. **Breadth/TICK handicap** — confirm the source's breadth/TICK trend-day
   confirmation is treated as unavailable (not proxied) and separated from the
   price/session entry.
7. **Exit/target** — whether "ride the trend day / get out when it gives back
   more than it should" can be pinned to a source-faithful project convention
   without invented targets.
8. **Instrument transfer** — record explicitly that transfer to
   `cu/al/ni/au/ag/rb` is an `INFERRED` hypothesis (commodity-futures concept
   support exists; exact bracket-trade transfer is not an explicit source claim).
9. **Failure/no-trade** — preserve the volatility-extreme/flag-failure and
   no-guessing no-trade evidence as explicit constraints.

## 20. Self-review

- Did I select a family because it looks profitable? **NO** — selected for
  provenance + price/session/volume compatibility + source-completable semantics.
- Did I use canonical market outcomes? **NO** — `NO_CANDIDATE_OUTCOME_DATA_USED=YES`.
- Did I invent an indicator or threshold? **NO** — NR7 and bracket windows are
  source-pinned; no numeric thresholds invented.
- Did I treat Market Profile/order flow as ordinary OHLCV? **NO** — TICK/breadth,
  order flow, and cross-market inputs are marked `NOT_OBSERVABLE_WITH_CURRENT_DATA`.
- Did I assume Chinese-futures transfer? **NO** — transfer is labeled `INFERRED`.
- Did I use a paid/login source? **NO** — official free/public unauthenticated only.
- Did I bypass a blocked video adapter? **NO** — video blocked by 403; official
  free article/text fallback used; no circumvention.
- Did I treat automatic speech recognition as exact quote? **NO** — no transcripts used.
- Did I choose multiple families instead of one? **NO** — exactly one family selected.
- Did I create a Playbook Contract prematurely? **NO** — status is
  `SELECTED_FOR_TARGETED_SEMANTIC_COMPLETION`.
- Did I rely on local memory instead of repository/source authority? **NO** —
  repository authority + actual official source evidence only.

```text
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```
