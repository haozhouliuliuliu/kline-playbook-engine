# HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_2_STEENBARGER_V0_1

> Version: 0.1
> Date: 2026-08-19
> Status: REAL_SOURCE_FAITHFUL_CLAIM_EXTRACTION / SOURCE_ONLY / NON_FROZEN
> Role: SOURCE_ONLY_CLAIM_EXTRACTION_WAVE_2_ENGINEER
> Prompt/spec: `REAL_CLAIM_EXTRACTION_WAVE2_STEENBARGER_PUBLIC_V1`
> Retrieval mode: `LOCAL_FREE_PUBLIC_ORIGINAL_SOURCE_BUNDLE_ONLY`
> Claim schema: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
> Protocol authority: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Source bundle manifest: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST.json`
> SOURCE_ONLY session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_2_STEENBARGER.json`
>
> `NO_CANDIDATE_OUTCOME_DATA_USED=YES`

---

## 0. Authority files actually used

Per the Wave 2 prompt, the following authorities were read from latest `origin/main`
(`04f5ecbd956c09e59b892270c73afd613c3c771c`):

- `AGENTS.md`
- `OWNER_COLLABORATION_CONTRACT.md`
- `CURRENT_STATE.md`
- `RESEARCH_DIRECTION.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`
- `docs/research/source_dossiers/SOURCE_DOSSIER_STEENBARGER_V0_1.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION.md`
- `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`
- `src/research_firewall.py`
- `tests/test_research_firewall.py` (SOURCE_ONLY tests)

Two files named in the prompt were **not found** in `origin/main` or in the Wave 1
worktree, and this absence is recorded rather than guessed:

- `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md` — does not exist
  in `origin/main`; the closest binding authority actually used is
  `docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_TOOL_ADMISSION.md` plus the
  `FREE_PUBLIC_UNAUTHENTICATED_FIRST` policy recorded in the Wave 1 source bundle
  manifest (`docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_1_MANIFEST.json`).
- `docs/reviews/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_1_INTEGRATION_REVIEW_V0_1.md` —
  does not exist in `origin/main` or in the `parallel/claim-extraction-wave1-public`
  worktree. The closest available Wave 1 material actually used for the format and
  the PRIMARY lesson is:
  - `docs/research/claim_extraction/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_1_V0_1.md`
    (Wave 1 extraction document, in the Wave 1 worktree);
  - `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1.json` (Wave 1 session
    evidence, in the Wave 1 worktree).

The Wave 1 PRIMARY correction lesson from the prompt ("about 50% of the previous
swing" was **not** enough to justify a PRIMARY because the swing definition and
tolerance were open) is applied throughout Section 11: no claim in Wave 2 is
marked a PRIMARY candidate unless the source pins one unique interpretation.

The statistical-inference package referenced in other worktrees was **not**
reopened.

## 1. Objective and scope

This is the second REAL source-faithful claim-extraction wave. It is **not** a
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

- Primary selected source: `SRC-STEENBARGER` / `MAT-STEENBARGER-TRADERFEED`
  (Brett N. Steenbarger, Ph.D., TraderFeed official public archive), per the
  dossier classification `PRIORITY_DEEP_DIVE_AS_PROCESS_SOURCE`.
- Source substitution: **NO**. All three preferred candidate posts were verified
  directly (fetched on 2026-08-19), are `FREE_PUBLIC_UNAUTHENTICATED`, are
  original pre-2024 TraderFeed posts, and together provide rich source-anchor
  quality plus explicit watching/no-trade, invalidation, failure and
  target-limitation context. No substitute post was required.
- Selection basis: provenance + free/public access + anchor quality +
  failure/no-trade coverage + extraction suitability only. Selection **never**
  depended on expected profitability, backtest quality, or ease of producing a
  strategy.

## 3. Source bundle (predeclared BEFORE claim extraction)

Bundle id: `SB-W2-PUBLIC-STEENBARGER-V1`
Canonical bundle hash: `39b46e341d05c212597c5703590ac71443dc9dc9eeca1de15cefc88b7a9db30b`

| material_id | title | date | URL | role in bundle |
|---|---|---|---|---|
| `SB-W2-M1` | Walking Through a Trade Setup | 2007-08-04 | https://traderfeed.blogspot.com/2007/08/walking-through-trade-setup.html | full trade walk-through: market context / observed cue / watching-no-trade / confirmation / invalidation / exit / target-limitation / applicability |
| `SB-W2-M2` | Three Basic Trade Setups | 2009-01-27 | https://traderfeed.blogspot.com/2009/01/three-basic-trade-setups.html | setup taxonomy: reversal / breakout / continuation; confirmation and target conventions |
| `SB-W2-M3` | Making the Hard Trade | 2009-05-15 | https://traderfeed.blogspot.com/2009/05/making-hard-trade.html | failure / non-confirmation / invalidation / reversion target / review-process |

All three are official author (TraderFeed) pages: provenance `TRACEABLE_ORIGINAL`,
access `FREE_PUBLIC_UNAUTHENTICATED`, verified by direct fetch on 2026-08-19.

All three have effective content dates **before 2024-01-01** (before the frozen
corpus start). Under Research Protocol v1.0 section 4, no source-example date
audit is required for the protected windows for this bundle.

## 4. Extraction boundary

- Only official free/public unauthenticated pages were used.
- No paywall bypass, DRM bypass, purchase, subscription, login, credential use,
  or authenticated scraping.
- No invented OHLCV proxy for absent inputs. The source references NYSE TICK,
  Market Delta (bid/offer volume), US sector/index breadth (XLE/XLF/XLB/XLV),
  prior-day value area, relative volume, pivot levels (R1/R2/R3, S1/S2/S3) and
  cross-market instruments (rates, currencies). None of these are treated as
  equivalent to 1-minute OHLCV, and none are silently substituted.
- No fuzzy language converted into invented numbers (e.g., "very heavy volume",
  "dwindling volume", "enhanced volume", "candidate highs", "high probability
  price target" are recorded as the source's own qualitative wording).
- No candidate outcome or protected-period market retrieval was performed.

## 5. SOURCE_ONLY session (verified)

Session evidence: `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_2_STEENBARGER.json`

Created through the actual project implementation
`SourceOnlyPolicy.open_verified_session(...)` in `src/research_firewall.py`:

- session id: `SOURCE_ONLY_WAVE2_STEENBARGER_PUBLIC_V1_20260819`
- model identity: `deepseek-v4-flash`
- prompt/spec version: `REAL_CLAIM_EXTRACTION_WAVE2_STEENBARGER_PUBLIC_V1`
- source bundle identity: `SB-W2-PUBLIC-STEENBARGER-V1`
- source bundle hash: `39b46e341d05c212597c5703590ac71443dc9dc9eeca1de15cefc88b7a9db30b`
- retrieval mode: `LOCAL_FREE_PUBLIC_ORIGINAL_SOURCE_BUNDLE_ONLY`
- protected market access mode: `TECHNICALLY_DENIED`
- `is_verified == True` (project-issued verification evidence)

Engineering denial path (executed once, no actual retrieval attempted):

```text
outcome = DENIED
reason  = SOURCE_ONLY_TECHNICAL_DENIAL
```

All 18 claim records were appended through the bounded
`SourceOnlyClaimExtractionContext` provenance output surface, bound to this
verified session and to the approved source bundle.

### Exposure note

- Model latent historical knowledge cannot be proven absent; this is a disclosed
  residual threat-model risk under the frozen protocol.
- No project protected-period market-outcome retrieval was available through the
  SOURCE_ONLY runner; the runner technically denies any such request and audits it.
- No canonical market data repository, validation surface, or historical-final
  surface was exposed to this session.

## 6. Claim records (18 claims)

Machine-readable claim records (full Claim Schema v1.0 structural subset):
`docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_2_STEENBARGER.json` -> `claims`.

Summary counts:

```text
CLAIMS = 18
EXPLICIT = 18
INFERRED = 0
UNKNOWN = 0

OBSERVABLE_NOW = 5
PARTIALLY_OBSERVABLE = 9
NOT_OBSERVABLE_WITH_CURRENT_DATA = 2
NOT_APPLICABLE = 2

PRIMARY_CANDIDATES = 0
PRIMARY_NOT_YET_JUSTIFIED = 18
AMBIGUOUS_STOP = 0
```

### Claim index

| claim_id | status | material | category | observability | primary |
|---|---|---|---|---|---|
| C-W2-001 | EXPLICIT | SB-W2-M1 | OBSERVED_CUE | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-002 | EXPLICIT | SB-W2-M1 | WATCHING_OR_NO_TRADE | OBSERVABLE_NOW | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-003 | EXPLICIT | SB-W2-M1 | WATCHING_OR_NO_TRADE | OBSERVABLE_NOW | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-004 | EXPLICIT | SB-W2-M1 | CONFIRMATION | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-005 | EXPLICIT | SB-W2-M1 | ACTION_PERMISSION | NOT_OBSERVABLE_WITH_CURRENT_DATA | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-006 | EXPLICIT | SB-W2-M1 | INVALIDATION | OBSERVABLE_NOW | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-007 | EXPLICIT | SB-W2-M1 | EXIT | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-008 | EXPLICIT | SB-W2-M1 | ACTION_PERMISSION | OBSERVABLE_NOW | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-009 | EXPLICIT | SB-W2-M1 | REVIEW_PROCESS | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-010 | EXPLICIT | SB-W2-M1 | APPLICABILITY | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-011 | EXPLICIT | SB-W2-M2 | OBSERVED_CUE | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-012 | EXPLICIT | SB-W2-M2 | EXIT | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-013 | EXPLICIT | SB-W2-M2 | APPLICABILITY | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-014 | EXPLICIT | SB-W2-M2 | CONFIRMATION | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-015 | EXPLICIT | SB-W2-M2 | CONFIRMATION | PARTIALLY_OBSERVABLE | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-016 | EXPLICIT | SB-W2-M3 | CONFIRMATION | NOT_OBSERVABLE_WITH_CURRENT_DATA | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-017 | EXPLICIT | SB-W2-M3 | INVALIDATION | OBSERVABLE_NOW | PRIMARY_NOT_YET_JUSTIFIED |
| C-W2-018 | EXPLICIT | SB-W2-M3 | REVIEW_PROCESS | NOT_APPLICABLE | PRIMARY_NOT_YET_JUSTIFIED |

### 6.1 EXPLICIT claims — attributable anchors

Every EXPLICIT claim points to a source anchor
(`material_id:post-slug:step|section|body|closing:NAME`).

- `C-W2-001` — momentum low in selling at the 13:30 bar with expanded volume and
  very heavy volume hitting bids. Anchor:
  `SB-W2-M1:walking-through-trade-setup:step:1_MOMENTUM_LOW`.
- `C-W2-002` — no-trade rule: "I don't sell markets that make new highs and I
  don't chase highs on dwindling volume." Anchor:
  `...:step:4_NO_TRADE_NEW_HIGHS`.
- `C-W2-003` — no-trade behavior: "I don't chase sellers, so now I'm waiting for
  the next rally to see if we get a good entry in the direction of the general
  market trend." Anchor: `...:step:5_NO_TRADE_WAIT_RALLY`.
- `C-W2-004` — a bounce that fails to expand TICK distribution, volume, or
  offer-side volume is short-covering; failure to make new highs relative to the
  13:39 bar defines "candidate highs" and a short-term trading range. Anchor:
  `...:step:6_CANDIDATE_HIGHS`.
- `C-W2-005` — entry permission: "I sell when we make positive TICK readings and
  green Market Delta readings (more volume at offer than bid) that cannot make
  fresh price highs." Anchor: `...:step:7_ENTRY_TRIGGER`.
- `C-W2-006` — invalidation/exit: stop above the candidate highs ("a move to new
  highs invalidates my idea"); profit target is the lows of the trading range.
  Anchor: `...:step:7_STOP_AND_TARGET`.
- `C-W2-007` — exit/management: cover when the bottom of the range is reached,
  1-minute volume picks up, and very negative (-1000) TICK readings appear; likes
  buyers who can't push the market higher (entries into shorts) and sellers
  panicking out (cover). Anchor: `...:step:8_COVER`.
- `C-W2-008` — entry placement + explicit target limitation: enter after a
  candidate high but as close to that high as possible to keep losses small; play
  for the highest-probability move (a return to the bottom of the range), not a
  home run breakout; a breakout is a separate trade and setup. Anchor:
  `...:step:9_TARGET_LIMITATION`.
- `C-W2-009` — waiting/observing behavior: "The goal is not to put on trades; it's
  to wait for things to line up in your favor, giving you an edge." Anchor:
  `...:step:10_WAIT_FOR_SETUP`.
- `C-W2-010` — applicability: the pattern occurs on multiple time frames; follow
  one market across many time frames focusing on (1) market general direction,
  (2) presence of a trading range, (3) candidate price high or low, (4) an entry
  leaning on that candidate, (5) a high-probability price target. Anchor:
  `...:closing:MULTI_TIMEFRAME`.
- `C-W2-011` — reversal trade definition: market moves to or just beyond the
  edges of a trading range (a consolidation area, the prior-day value area),
  cannot sustain buying/selling interest, and falls back into that range. Anchor:
  `SB-W2-M2:three-basic-trade-setups:section:1_REVERSAL_TRADES`.
- `C-W2-012` — reversal target: initial target generally the midpoint of the range
  (may also be the prior day/week pivot); on good volume and very weak/strong NYSE
  TICK, frequently tests the opposite end as breakout traders bail out. Anchor:
  `...:section:1_REVERSAL_TARGETS`.
- `C-W2-013` — reversal applicability: especially look for reversals in weak
  relative-volume environments, which tend to be markets pushed around by market
  makers, not longer-timeframe participants. Anchor:
  `...:section:1_REVERSAL_WEAK_RELATIVE_VOLUME`.
- `C-W2-014` — breakout trade: range-bound market surges out on enhanced volume
  and very high/low NYSE TICK, usually with a catalyst; cross-market repricing
  (rates, currencies) makes a simultaneous stock breakout more likely real; initial
  targets are daily price targets R1/R2/R3, S1/S2/S3. Anchor:
  `...:section:2_BREAKOUT_TRADES`.
- `C-W2-015` — continuation trade: with a trend in place wait for a pullback;
  volume expands with the trend and contracts on pullbacks; trending cumulative
  NYSE TICK and Market Delta; TICK/Delta pullbacks are potential entries (hit R1,
  pull back on light volume and modestly negative TICK/Delta, reload long for R2).
  Anchor: `...:section:3_CONTINUATION_TRADES`.
- `C-W2-016` — failure/non-confirmation: key sectors XLE and XLF did not confirm
  the upside breakout; XLB and XLV looked sketchy at the highs; the day was
  treated as a range day. Anchor:
  `SB-W2-M3:making-hard-trade:body:SECTOR_NON_CONFIRMATION`.
- `C-W2-017` — invalidation/exit: unable to take out yesterday's high, moved back
  into the morning range; "you didn't need to catch the exact top to recognize
  that the upmove was failing and play a reversion back to VWAP as a first
  target." Anchor: `...:body:FAILED_BREAKOUT_REVERSION`.
- `C-W2-018` — review process: "Making the hard trade: It's all about
  preparation." Anchor: `...:closing:PREPARATION`.

### 6.2 INFERRED / UNKNOWN claims

None. `INFERRED = 0`, `UNKNOWN = 0`. No project/AI synthesis claim was forced;
all 18 records are direct short excerpts / close paraphrases with attributable
anchors. This is a count-quality choice, not a claim of completeness.

## 7. Source vs interpretation separation

- All 18 claims are EXPLICIT source statements with attributable anchors.
- No INFERRED project/AI synthesis records were produced (unlike Wave 1); the
  source's own wording was sufficient for this bundle, and no interpretation was
  silently promoted.
- Machine operationalization was **not** performed. Claims that need a
  source-faithful interpretation before any non-outcome operationalization are
  marked `INTERPRETATION_REQUIRED`; claims whose core inputs are not owned are
  marked `NOT_OBSERVABLE`; process claims are `NOT_STARTED`.

## 8. Observability / make-do rule (source surface A vs project surface B vs missing C)

Per the Wave 2 observability rule, each claim separates:

- **A. source information surface** — what the source actually observed;
- **B. current project-observable portion** — what the 1-minute OHLCV corpus +
  governed existing metadata can represent point-in-time;
- **C. missing portion** — inputs the project does **not** own (no proxy invented).

Key non-owned inputs in this bundle (recorded, never substituted):

- **NYSE TICK** — NOT owned. Never treated as equivalent to 1-minute OHLCV.
- **Market Delta** (volume at offer vs bid / green-red delta) — NOT owned.
- **US sector/index breadth** (XLE/XLF/XLB/XLV, ES) — NOT owned; the project
  corpus is Chinese futures (cu/al/ni/au/ag/rb) 1-minute OHLCV.
- **Cross-market instruments** (interest rates, currencies) — NOT owned.
- **Prior-day value area** (Market Profile) — not derivable directly from
  OHLCV without additional interpretation.
- **Pivot levels / daily price targets** (R1/R2/R3, S1/S2/S3) — formulas not
  specified by the source in this bundle.

Per-claim assignments (details in the session JSON `observability_missing_inputs`):

- `OBSERVABLE_NOW` (5): `C-W2-002`, `C-W2-003`, `C-W2-006`, `C-W2-008`,
  `C-W2-017` — stated conditions are price/volume (new highs, dwindling volume,
  rally/trend, stop above candidate highs, range-lows target, prior-day high,
  morning range, VWAP). VWAP is a volume-weighted price derivable from 1-minute
  OHLCV. Interpretation of constructs such as "candidate high" or "trend" is an
  operationalization decision, not an observability gap.
- `PARTIALLY_OBSERVABLE` (9): `C-W2-001`, `C-W2-004`, `C-W2-007`, `C-W2-010`,
  `C-W2-011`, `C-W2-012`, `C-W2-013`, `C-W2-014`, `C-W2-015` — part is
  OHLCV-representable (price/volume) and part requires non-owned inputs
  (TICK, Market Delta, value area, relative-volume baseline, pivot formulas).
- `NOT_OBSERVABLE_WITH_CURRENT_DATA` (2): `C-W2-005` (entry trigger is NYSE TICK +
  Market Delta) and `C-W2-016` (US sector/index breadth). No proxy is invented.
- `NOT_APPLICABLE` (2): `C-W2-009`, `C-W2-018` — behavioral/process claims.

Missing inputs never blocked the other useful claims; each claim's observable
portion was still extracted and recorded.

## 9. Ambiguity

- `AMBIGUOUS_STOP = 0`: no claim required a stop because the source meaning was
  unambiguous at the claim level.
- Genuine open interpretation is preserved in `ambiguity_notes` and the
  `INTERPRETATION_REQUIRED` machine-operationalization status rather than resolved
  by invention (e.g., `C-W2-012` midpoint-vs-pivot target convention, `C-W2-005`
  TICK/Delta trigger, `C-W2-013` relative-volume baseline, `C-W2-014`/`C-W2-015`
  R1/R2/R3 formulas).
- No outcome data was used to resolve any ambiguity.

## 10. Negative / failure / no-trade evidence

Failure / no-trade context is present in the bundle and preserved:

- `C-W2-002` — no-trade rule: do not sell markets making new highs; do not chase
  highs on dwindling volume.
- `C-W2-003` — no-trade behavior: do not chase sellers; wait for a rally to seek
  an entry in the direction of the general market trend.
- `C-W2-004` — non-confirmation: a bounce failing to expand TICK/volume/offer-side
  volume is read as short-covering.
- `C-W2-005` — action permission only on a specific TICK/Delta trigger; the rule
  is a discipline against premature shorting.
- `C-W2-006` — invalidation: a move to new highs invalidates the idea.
- `C-W2-008` — explicit target limitation: play for the highest-probability move
  (return to range bottom), not a home run breakout; a breakout is a separate
  trade/setup.
- `C-W2-009` — waiting behavior: goal is to wait for conditions to line up, not to
  force trades.
- `C-W2-016` — failure/counterexample: key sectors did not confirm the upside
  breakout; day treated as a range day.
- `C-W2-017` — failure: unable to take out the prior day's high; reverted into the
  morning range and played a reversion to VWAP.

Recorded absence / limitation: the bundle does not contain a systematic loss
ledger or a quantified failure rate; that is a source-quality limitation of this
bundle and is recorded rather than manufactured.

## 11. PRIMARY readiness (Wave 1 lesson applied)

- **`PRIMARY_CANDIDATES = 0`.** Per the Wave 1 correction, source meaning that is
  clear at claim level can still lack a unique operational interpretation.
  `PRELIMINARY_SOURCE_JUSTIFIED_PRIMARY_CANDIDATE` is used only when the source
  pins one unique interpretation without invented numeric/operational semantics.
- In this bundle every candidate primary would require an invented or
  under-specified construct: "candidate highs", "trading range", "midpoint",
  "relative volume" baseline, R1/R2/R3 pivot formulas, or non-owned TICK/Delta/
  sector inputs. The source does not pin any of these uniquely, so **all 18
  claims are `PRIMARY_NOT_YET_JUSTIFIED`**.
- `AMBIGUOUS_STOP = 0` — no claim has genuinely conflicting source meanings.
- PRIMARY branch selection for outcome testing is a later Protocol v1.0 step and
  is **not** performed in this extraction wave.
- No outcome data was used to form or test any primary candidate.

## 12. Copyright boundary

- Store traceability, not a redistribution archive.
- Only attributable short excerpts and concise paraphrases are recorded in the
  JSON/markdown artifacts; full copyrighted articles are not stored.
- Raw HTML was not retained (retention boundary recorded in the manifest).

## 13. Optional paid candidates (awareness only)

Encountered and recorded for awareness only (no purchase / subscription):

1. Market Delta (marketdelta.com) — commercial order-flow / volume-at-bid-vs-offer
   software referenced by the source for "Market Delta" readings. Could later fill
   the bid/offer-volume gap behind the entry/confirmation/exit conditions.
2. Brett Steenbarger books (e.g., *The Psychology of Trading*, *Enhancing Trader
   Performance*, *Trading Psychology 2.0*) — book-length process material; would
   expand the review/process layer, not market-data inputs.
3. Market Profile / auction value-area data and software (Steidlmayer/Dalton
   lineage) referenced via "the value area from the prior day".

`PAID_SOURCE_PURCHASE_DEFAULT=NO`; free/public alternatives were sufficient, so
the wave continued without any paid access.

## 14. Anti-regression / self-review checklist

- Did EXPLICIT contain AI inference? **No** — all 18 are source excerpts/close
  paraphrases; INFERRED = 0.
- Did you invent thresholds? **No** — qualitative wording is preserved; no "very
  heavy volume" -> numeric, no "dwindling volume" -> threshold, no "candidate
  high" -> rule.
- Did you treat TICK / Market Delta as OHLCV? **No** — both are recorded as
  missing; `C-W2-005` is `NOT_OBSERVABLE_WITH_CURRENT_DATA`.
- Did you silently substitute unavailable breadth data? **No** — sector/index
  breadth (`C-W2-016`) is `NOT_OBSERVABLE_WITH_CURRENT_DATA`; no proxy.
- Did you prematurely mark PRIMARY? **No** — `PRIMARY_CANDIDATES = 0`, all
  `PRIMARY_NOT_YET_JUSTIFIED` (Wave 1 lesson applied).
- Did you select only winner examples? **No** — failure/non-confirmation,
  invalidation, no-trade and target-limitation claims are preserved (Section 10).
- Did you omit explicit waiting/no-trade/failure context? **No** — `C-W2-002`,
  `C-W2-003`, `C-W2-009` (waiting/no-trade), `C-W2-016`, `C-W2-017` (failure).
- Did any candidate outcome or protected data get touched? **No** — the SOURCE_ONLY
  runner has no such surface; denial path verified once (`DENIED` /
  `SOURCE_ONLY_TECHNICAL_DENIAL`).
- Did any paid/authenticated source get used? **No** — free/public/unauthenticated
  only; paid items are awareness-only candidates.

`NO_CANDIDATE_OUTCOME_DATA_USED=YES`

## 15. Durable artifacts produced

- `docs/research/claim_extraction/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_2_STEENBARGER_V0_1.md` (this file)
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST.json`
- `docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_2_STEENBARGER.json`
- `tools/run_claim_extraction_wave2_steenbarger_source_only.py` (reproducible SOURCE_ONLY driver)

Wave 1 was **not** modified. No frozen authority and no `CURRENT_STATE.md` was
modified by this wave.
