# FGH_CODEX_REBUILD_PREPARATION_V0_1

> Version: 0.1
> Date: 2026-08-20
> Role: FGH rebuild construction authority (preparation for `OLD_F_G_H_REBUILD_AND_COMBINED_CAUSAL_TIMING_INTEGRATION`)
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Preparation branch: `prep/fgh-codex-rebuild-v01`
> Execution target branch (Codex): `prep/fgh-codex-rebuild-v01` -> R1 foundation tree
> Candidate outcome access: NOT_AUTHORIZED
> Scope: remap the second-pass audit findings `L-01..L-18` onto the repaired A/B/C/D/F/E foundation; define the exact Codex construction graph. NOT production implementation. NOT a merge. NOT a semantic freeze.

```text
FGH_PREPARATION_STATUS=COMPLETE_PREPARATION_ONLY
SRC_PRODUCTION_DIFF=0
OLD_F_MERGED=NO
OLD_G_MERGED=NO
OLD_H_MERGED=NO
RESEARCH_SEMANTICS_DECIDED_BY_THIS_DOC=NO
OWNER_DECISIONS_TAKEN_BY_THIS_DOC=NO
CANDIDATE_OUTCOME_DATA_USED=NO
```

---

## 0. Baseline and study method

### 0.1 Source tree for Codex execution

The FGH rebuild must be constructed on the **post-R1 integrated tree**, not on
`origin/main` alone. Current state:

```text
MAIN=c32c5bf2b76afd290cc0e44839aacf778d423863   (Package A/B integrated only)
CDF=integration/cdf-final-v01                   (Package C/D/F repairs, READY_FOR_MAIN_INTEGRATION)
E_CORE=repair/package-e-core-execution-v01      (Package E repairs, READY_FOR_COMBINED_INTEGRATION)
R1=integration/r1-cdf-ecore-e10-v01@49ecf7e     (CDF + E-Core + E-Governance merged on one tree)
```

`integration/r1-cdf-ecore-e10-v01` is the single tree that already contains
the repaired foundation the FGH rebuild depends on:

- **Package C** — claim-level PRIMARY (`resolve_claim_primary`,
  `primary_selection_identity`, `CLAIM_PRIMARY_MISSING`,
  `CLAIM_PRIMARY_MULTIPLE`), `PARTIALLY_OBSERVABLE` required inputs block
  machine-ready, `MULTIPLE_TIMEFRAMES_UNRESOLVED` (single-timeframe bridge),
  `PROJECT_TRANSFER_UNKNOWN` blocks, `validate_strategy_against_playbook_contract`
  single shared bridge validator.
- **Package D** — `SessionMetadata(authority_reference, windows)` with
  deterministic content version (D-05); `expected_bar_starts` /
  `expected_bar_starts_between` / `missing_bar_starts` (D-02); zero-bar /
  entirely-absent window enumeration; `CanonicalRow.raw_artifact_identity_id`
  from `NormalizedHistoricalBar.raw_artifact_identity_id` (D-03); nullable
  volume (D-04); `GovernedSource` byte provenance (D-06).
- **Package F** — material-bound SOURCE_ONLY (`ApprovedSourceMaterialRef`
  forward-only byte binding, `historical_unbound` for NOT_RECORDED,
  `open_verified_session`), verification-wording corrections.
- **Package E (core)** — E-01 ADD PnL re-mark, E-02 forced-liquidation
  cross-trading-day, E-03 offset-fee resolution, E-09/E-11/E-12/E-13.
- **Package A/B (on main)** — `ArtifactBinding.from_bytes` (only trusted
  code-hash construction path), `OutcomeArtifactBindings`, firewall hardening.

If R1 has not been integrated to `main` by execution time, Codex must create a
fresh worktree from `origin/main` and merge the accepted R1 components in the
exact order the R1 integration lane documents, or reuse the existing
`integration/r1-cdf-ecore-e10-v01` head. Codex must not silently re-derive any
C/D/F/E semantics.

### 0.2 Old branches studied (git show / git diff / git log only; never merged)

```text
OLD_F=parallel/holy-grail-playbook-contract-draft-v01
OLD_F_COMMIT=9fe53a2104e78e51f09f56c3bc73d2f6c930e536
OLD_G=parallel/pit-feature-timeframe-core-v01
OLD_G_COMMIT=ae16f7cd0b38aadc783bd8957c7b03a7ac123d37
OLD_H=parallel/stop-trigger-observation-v01
OLD_H_COMMIT=8244935ed3be32394910a6fb745017b31e194b6a
OLD_BASELINE=64771245acf5e445adc59eb5ef71afcb0ef00777
```

All three branches are exactly one commit on top of `6477124` (the pre-CDF
baseline). Findings studied:

- `FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md` Part F (the
  `L-01..L-18` findings), Part G chains 1/5/6.
- `PARALLEL_WORK_PACKAGE_2026-08-20_V0_3_ADVERSARIAL_AUDIT.md` (F-1/F-2,
  G-1..G-4, H-1..H-3, X-1..X-3).
- Frozen `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` (SOURCE CLAIM != PROJECT
  INTERPRETATION != MACHINE OPERATIONALIZATION; PRIMARY rule; INFERRED
  conventions must be frozen before outcome tests; no worker may pick among
  equally plausible research meanings).
- Holy Grail source-semantic evidence
  (`RASCHKE_HOLY_GRAIL_SEMANTIC_COMPLETION_V0_1.md`,
  `RASCHKE_HOLY_GRAIL_PLAYBOOK_HANDOFF_V0_1.md`).
- Holy Grail existing Playbook draft evidence (old F branch:
  `RASCHKE_HOLY_GRAIL_INTERPRETATION_FREEZE_V0_1.md`,
  `RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.md`,
  `RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.json`,
  `tools/build_raschke_holy_grail_playbook_contract_draft.py`).

### 0.3 Locked boundaries (unchanged)

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
PRIMARY_FREEZE=NOT_AUTHORIZED_UNTIL_OWNER_GATES
F_G_H=NOT_MERGED
```

---

## 1. Goal and classification legend

Every `L-01..L-18` finding is remapped onto the repaired foundation. Each item
is assigned exactly one headline class:

```text
RESOLVED_BY_CURRENT_FOUNDATION         foundation now provides the governing helper/semantics;
                                       old branch must reuse it (no new model, no re-derivation)
UNAMBIGUOUS_IMPLEMENTATION_FIX         deterministic engineering fix; no research-semantic choice
SOURCE_SEMANTIC_AUTHORITY_REQUIRED     source does not pin a unique answer; cannot be chosen here
OWNER_DECISION_REQUIRED                outcome-affecting choice; worker must not freeze
OBSOLETE_AFTER_FOUNDATION_CHANGE       old branch construct is superseded and must not be ported
```

Headline classes per finding (full detail in sections 2-9):

| id | class |
|---|---|
| L-01 | SOURCE_SEMANTIC_AUTHORITY_REQUIRED |
| L-02 | SOURCE_SEMANTIC_AUTHORITY_REQUIRED |
| L-03 | OWNER_DECISION_REQUIRED |
| L-04 | OWNER_DECISION_REQUIRED |
| L-05 | OWNER_DECISION_REQUIRED (+ `INT-STOP-ACTIVATION-AFTER-FILL` OBSOLETE) |
| L-06 | UNAMBIGUOUS_IMPLEMENTATION_FIX (reuse D-02/D-05) |
| L-07 | UNAMBIGUOUS_IMPLEMENTATION_FIX (reuse D-02/D-05) |
| L-08 | UNAMBIGUOUS_IMPLEMENTATION_FIX |
| L-09 | UNAMBIGUOUS_IMPLEMENTATION_FIX |
| L-10 | UNAMBIGUOUS_IMPLEMENTATION_FIX |
| L-11 | UNAMBIGUOUS_IMPLEMENTATION_FIX (reuse ArtifactBinding) |
| L-12 | UNAMBIGUOUS_IMPLEMENTATION_FIX |
| L-13 | UNAMBIGUOUS_IMPLEMENTATION_FIX |
| L-14 | UNAMBIGUOUS_IMPLEMENTATION_FIX |
| L-15 | UNAMBIGUOUS_IMPLEMENTATION_FIX (label binding) |
| L-16 | OWNER_DECISION_REQUIRED (machine chronology model) |
| L-17 | UNAMBIGUOUS_IMPLEMENTATION_FIX (lifecycle) |
| L-18 | UNAMBIGUOUS_IMPLEMENTATION_FIX (mandatory combined synthetic regression) |

Counts:

```text
RESOLVED_BY_CURRENT_FOUNDATION=0
UNAMBIGUOUS_IMPLEMENTATION_FIX=12
SOURCE_SEMANTIC_AUTHORITY_REQUIRED=2
OWNER_DECISION_REQUIRED=4
OBSOLETE_AFTER_FOUNDATION_CHANGE=0 (headline) / 2 (sub-constructs: L-05 activation convention, old G window_at)
```

The two `SOURCE_SEMANTIC_AUTHORITY_REQUIRED` items block the Holy Grail
`PRIMARY`; the four `OWNER_DECISION_REQUIRED` items are the FGH causal-timing
gates (section 12). Every `UNAMBIGUOUS_IMPLEMENTATION_FIX` must still respect
those gates where the fix touches timing/chronology.

---

## 2. L-01 — Holy Grail EMA touch: which price/reference (Lane F)

### 2.1 What old F actually implemented

Old F predeclared (never PRIMARY, `PROJECT_INFERRED_PREDECLARED`):

```text
INT-EMA-PRICE-INPUT-CLOSE   EMA_PRICE_INPUT = close
INT-EMA-TOUCH-INTRABAR      touch = bar.low <= EMA <= bar.high  (long side)
```

So old F's touch judgment uses a **close-based EMA** compared against the same
bar's `[low, high]` range. That is a project machine interpretation of "when
price touches the 20-period MA", explicitly labeled INFERRED and not a source
claim.

### 2.2 What the accepted source evidence pins

Semantic completion (source-only, accepted):

```text
MOVING_AVERAGE_PRICE_INPUT        = NOT_PINNED  (source never states the EMA price basis)
PULLBACK_TOUCH_OR_PENETRATION_RULE = PARTIALLY_PINNED
   ("touch" explicit; bar-level definition of touches —
    intrabar low/high vs close vs penetration — NOT pinned)
```

The source therefore does **not** uniquely state:

- whether the EMA is computed on close / typical / high-low;
- whether a touch means `low <= EMA`, `close <= EMA`, or any-price intrabar
  penetration.

### 2.3 Judgment

```text
CLASS=SOURCE_SEMANTIC_AUTHORITY_REQUIRED
```

The source has no unique answer for the touch price/reference. Per Protocol
v1.0, a worker must not pick among equally plausible research meanings. Old F's
close-based intrabar touch may remain a **predeclared labeled INFERRED branch**,
but it must not be treated as source-exact, and it must not be frozen as the
Holy Grail PRIMARY before Owner adoption (section 12 `FGH-GATE-01`).

Note the causality hazard already recorded in the audit (L-01): a close-based
EMA is not available during the same bar; using it to decide the same bar's
touch is look-ahead unless the interpretation explicitly defines the
prior-available EMA reference. That is part of the same Owner gate.

---

## 3. L-02 — ADX sequence (Lane F)

### 3.1 Source evidence decomposed

```text
ADX_PERIOD                        = EXPLICITLY_PINNED (14)
ADX_THRESHOLD                     = EXPLICITLY_PINNED (>30)
ADX_RISING_OR_LEVEL_REQUIREMENT   = EXPLICITLY_PINNED
   ("must initially be greater than 30 AND rising"; slope measurement window INFERRED)
M01 step 2                        = "usually accompanied by a turndown in ADX"  (pullback-phase nuance, qualitative)
M05                                = each retracement preceded by 14-bar ADX>30 on that timeframe (multi-timeframe)
```

### 3.2 Decomposition

| sub-item | source status |
|---|---|
| ADX > 30 | pinned (threshold) |
| ADX rising (concept) | pinned ("rising"); slope window not pinned |
| pullback timing relative to ADX | **not pinned** — source says pullback is "usually accompanied by a turndown in ADX", i.e. the rising filter is an *initial* context, not a condition that must still hold on the touch bar |
| EMA interaction | multi-timeframe per M05; per-timeframe ADX>30 is context, not a same-touch condition |

### 3.3 Source-vs-project gap

Old F added `INT-ADX-RISING-1BAR = ADX[current] > ADX[previous]` evaluated at
the context/touch bar. Requiring ADX to still be rising **at the touch bar** is
a project-added sequence requirement the source does not state. The audit
(L-02) records this conflict.

### 3.4 Judgment

```text
CLASS=SOURCE_SEMANTIC_AUTHORITY_REQUIRED
```

The gap is real: old F added a one-bar "rising at current bar" requirement that
is not source-pinned. The source-pinned core (ADX>30 and rising as an initial
context, pullback usually accompanied by an ADX turndown) must be represented
faithfully; where the machine must evaluate "rising" (which window, relative to
which bar), that is a labeled INFERRED convention needing Owner adoption
(section 12 `FGH-GATE-02`). Do not silently keep old F's one-bar convention as
if it were source semantics.

---

## 4. L-03 — EMA / ADX seed, warmup, initialization, rounding, precision (Lane F -> G)

### 4.1 What old G chose (and old F did not freeze)

Old F froze no algorithm semantics. Old G independently chose:

```text
EMA      SMA-seeded (first EMA = SMA of first `period` observations);
         alpha = 2/(period+1); INSUFFICIENT_HISTORY before `period` bars
ADX      Welles Wilder; first smoothed = sum of first `period` raw;
         first ADX = simple average of first `period` DX; recursive update;
         first ADX at index 2*period - 1
OUTPUT   Decimal, 6 decimal places, ROUND_HALF_UP (per-step quantization)
```

All labeled "ENGINEERING FEATURE SEMANTICS" in old G, i.e. machine
conventions, not human-source facts.

### 4.2 Current project authority

There is **no** project authority on the R1 tree freezing these numeric
conventions for the Holy Grail family (or generically). The foundation provides
`ArtifactBinding`/version identity scaffolding but no numeric policy.

### 4.3 Judgment

```text
CLASS=OWNER_DECISION_REQUIRED
```

The source cannot decide numerical implementation (source is silent on EMA
seed, ADX warmup, quantization). These are project machine-operationalization
choices. They **do** affect outcome: EMA-touch classification and ADX>30
classification change with seed/warmup/rounding. Per the task rule, do not
freeze them here; do not let Codex freeze them. Provide as a gate
(section 12 `FGH-GATE-03`), with the safe default being the documented standard
conventions (SMA-seeded EMA, Wilder init, exact Decimal, explicit single
output quantization policy) adopted by Owner.

---

## 5. L-04 — Same 1-minute bar: EMA touch + entry trigger cannot be ordered (Lane F -> H)

### 5.1 Existing authority check

The source pins the concept (touch EMA -> buy stop above previous-bar high) but
not intra-bar ordering. Old F did **not** promote touch-vs-entry-stop same-bar
ordering to a critical ambiguity. Old H only models same-bar ambiguity for
*stop activation* (`AMBIGUOUS_INTRABAR_SEQUENCE`), not for the EMA-touch ->
entry-stop step.

There is currently **no** conservative same-bar policy governing
"EMA touch and entry stop threshold both reached inside one 1-minute bar".

### 5.2 Judgment

```text
CLASS=OWNER_DECISION_REQUIRED
```

Minimal candidate policies (listed only; not selected):

- **A.** Treat the touch/entry same-bar event as `AMBIGUOUS_INTRABAR_SEQUENCE`
  (fail closed; no entry until ordering is decidable at the minimum resolution).
- **B.** Evaluate EMA touch on the prior completed bar; place/trigger the entry
  stop only from the next bar (deferral; removes same-bar ambiguity but changes
  entry prices).
- **C.** Adopt a separate, explicitly justified finer chronology model
  (requires project-owned intrabar evidence, which does not exist at 1-minute).

Gate: section 12 `FGH-GATE-04`.

---

## 6. L-05 — Entry fill + protective stop inside the same bar (Lane F -> H)

### 6.1 Can the current execution/stop model know intrabar ordering?

No. At 1-minute resolution the project owns only completed-bar OHLC;
`ExecutionObservation` and the stop model cannot distinguish fill-then-stop
from stop-then-fill inside one bar. The bridge in old H observes only at
`bar_available_at`.

Old F predeclared `INT-STOP-ACTIVATION-AFTER-FILL` = protective stop active
from the first eligible future bar after the entry fill, i.e. **no same-bar
post-fill stop exposure**. The audit (L-05) flags this as silent risk
suppression: the source says "Once filled, enter a protective stop", and a
same-bar post-fill stop loss path must not be assumed away.

### 6.2 Judgment

```text
CLASS=OWNER_DECISION_REQUIRED
SUB_CONSTRUCT_OBSOLETE=INT-STOP-ACTIVATION-AFTER-FILL (must not be preserved as-is)
INTRA_BAR_ORDERING=NOT_OBSERVABLE_AT_1M
```

Required: the rebuilt contract/stop chain must encode the same-bar
fill+protective-stop event as fail-closed (reuse old H's
`AMBIGUOUS_INTRABAR_SEQUENCE` semantics) or an explicitly adopted conservative
policy. The "next-bar stop" convenience is not a valid stand-in for "no
same-bar risk". Gate: section 12 `FGH-GATE-05` (merged with the L-16 chronology
question).

---

## 7. L-06 .. L-12 — G (feature engine) re-verification

Foundation facts reused throughout (Package D / B):

```text
SessionMetadata(authority_reference, windows)   deterministic content version (D-05)
expected_bar_starts / expected_bar_starts_between / missing_bar_starts   authoritative enumeration (D-02)
zero-bar / entirely-absent session windows   enumerable from authoritative windows (D-02)
NormalizedHistoricalBar.exchange / concrete_instrument / identity_id / data_version_id
ArtifactBinding.from_bytes   only trusted artifact-hash construction path (B / P-06)
```

### L-06 — Daily completeness

```text
OLD_G_BEHAVIOR   _aggregate_daily() groups whatever bars were supplied for a trading day;
                 never compares against all expected starts -> partial day can emit a complete daily bar.
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX
REUSE=SessionMetadata.expected_bar_starts / missing_bar_starts (D-02, D-05) — do NOT build a second model.
REQUIREMENT=Daily aggregation must verify the complete expected constituent set (all published session
            windows of the official trading day) or emit an IncompleteBucket / reject; never emit a
            complete daily bar from a partial day.
```

### L-07 — Absent session visibility

```text
OLD_G_BEHAVIOR   _aggregate_intraday() groups only windows that have >=1 supplied bar;
                 a completely missing session window disappears without an incomplete record.
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX
REUSE=D-02 authoritative window enumeration (zero-bar windows), SessionMetadata.window list.
REQUIREMENT=Iterate authoritative windows for represented official trading days, including zero-bar
            windows; emit IncompleteBucket for missing windows. Do not rebuild a second session model.
```

### L-08 — Interval / constituent duration

```text
OLD_G_BEHAVIOR   accepts arbitrary interval_seconds; proves neither that the interval is an exact
                 integral multiple of the base nor that each constituent bar duration == base interval.
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX
REUSE=expected_bar_starts(base interval) alignment; CompletedBar.start/end.
REQUIREMENT=Require each NormalizedHistoricalBar duration to equal the declared base interval; require a
            supported exact base/interval relationship (or reject the spec); validate every constituent.
            Supported interval set is a documented machine convention (not a source claim).
```

### L-09 — Feature dependency prefix

```text
OLD_G_BEHAVIOR   feature identity binds current source aggregate identity + computed value + spec,
                 not the full historical dependency prefix (EMA/ADX depend on the whole prefix).
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX
REUSE=pattern from ArtifactBinding (hash over actual evidence) and the audit "opaque identity strings" chain.
REQUIREMENT=Bind an explicit dependency-chain/prefix identity (or prior-feature identity chain) so any
            material source-evidence change changes the feature identity even when the final numeric
            value coincidentally does not.
```

### L-10 — Mixed exchange / instrument stream

```text
OLD_G_BEHAVIOR   _validated_aggregate_series checks chronology/overlap/timeframe/session version but NOT
                 exchange / concrete_instrument homogeneity.
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX
REUSE=NormalizedHistoricalBar.exchange / concrete_instrument.
REQUIREMENT=Require all aggregates in one feature series to share one exchange + one concrete instrument.
```

### L-11 — Feature actual code hash

```text
OLD_G_BEHAVIOR   feature identity binds caller algorithm/version strings, not actual implementation code.
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX
REUSE=ArtifactBinding.from_bytes (only trusted digest construction path; P-06/B).
REQUIREMENT=Bind the actual feature implementation bytes hash into feature identity; a code change without
            a manual version bump must change the identity. No caller-supplied digest.
```

### L-12 — Incomplete bucket evidence discard

```text
OLD_G_BEHAVIOR   compute_ema / compute_adx accept arbitrary AggregatedBar iterables; a caller can pass
                 only the complete aggregates and discard incomplete_buckets, compressing the series.
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX
REUSE=AggregationResult completeness state (already present in old G; keep it in the rebuild).
REQUIREMENT=Require continuity/completeness evidence for feature computation (e.g. pass AggregationResult
            and fail closed on unresolved missing buckets), or explicitly reject a series with gaps.
```

---

## 8. L-13 .. L-17 — H (trigger / stop) re-verification

### L-13 — Generator consumption in group evaluation

```text
OLD_H_BEHAVIOR   evaluate_stop_group() passes the same `bars` iterable into evaluate_stop_order()
                 per order; a one-shot generator is consumed by the first order.
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX  (pure implementation bug; no research semantics)
REQUIREMENT=Materialize/validate the ordered bar sequence exactly once at group entry; reuse the
            immutable tuple for all member orders; add a generator regression test.
```

### L-14 — Exact bars / evaluated-sequence identity

```text
OLD_H_BEHAVIOR   StopTriggerResult.identity_id records timestamps/prices/trigger fields but NOT the
                 NormalizedHistoricalBar.identity_id of the triggering bar, nor the evaluated prefix
                 (NOT_TRIGGERED evidence is even more sequence-dependent).
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX  (provenance fix; no research semantics)
REQUIREMENT=Bind the triggering bar identity_id for triggered/ambiguous results and a deterministic
            evaluated-sequence/dependency identity for non-triggered/group results.
```

### L-15 — trigger_model_version caller label

```text
OLD_H_BEHAVIOR   RestingStopOrder.trigger_model_version accepts any non-empty string while the code
                 always executes STOP_MARKET_TRIGGER_MODEL_V0_1.
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX  (label binding)
NOTE=The underlying trigger model semantics (buy-stop high>=stop / sell-stop low<=stop; gap-through
      reference; active_at eligibility; AMBIGUOUS_INTRABAR_SEQUENCE) remain ENGINEERING assumptions,
      not human-source semantics. Fixing the label binding is an implementation fix; the model semantics
      are NOT thereby research-frozen ("code can change" != "research semantics frozen").
REQUIREMENT=Derive/verify the executed model version from the actual implementation (e.g. ArtifactBinding
            over the trigger code + explicit model constant); reject caller-declared versions that do not
            match the executed algorithm.
```

### L-16 — Completed-bar availability vs exchange-resting chronology

```text
OLD_H_BEHAVIOR   bridge emits ExecutionObservation(observed_at=available_at=bar_available_at); a stop
                 economically triggering inside the minute is observed only after bar completion.
CLASS=OWNER_DECISION_REQUIRED  (machine chronology model; NOT a pure code bug)
DETAIL=The completed-bar availability model is conservative and honest (fail-closed), but it is NOT the
       same chronology as an exchange-resting stop. It materially interacts with gap-through,
       protective-stop and same-bar OCO behavior (L-04/L-05).
REQUIREMENT=The rebuilt bridge must explicitly declare its model as "completed-bar availability,
            conservative" and never present it as exchange-resting chronology. Choosing between
            completed-bar observation (conservative) and a separately justified intrabar/gap-through
            model is an Owner gate (section 12 FGH-GATE-05).
```

### L-17 — OCO cancellation lifecycle

```text
OLD_H_BEHAVIOR   evaluate_stop_group() detects same-bar both-touch ambiguity but does NOT cancel a
                 sibling after an earlier unambiguous OCO trigger; a later bar can trigger the sibling.
CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX  (lifecycle scope completion)
NOTE=Trigger model semantics (same-bar both-touch -> AMBIGUOUS) remain labeled ENGINEERING assumptions.
REQUIREMENT=Implement the OCO lifecycle: cancel the sibling at the first unambiguous trigger, preserve
            AMBIGUOUS_INTRABAR_SEQUENCE for same-bar conflicts, and never represent detection-only as a
            complete OCO/bracket lifecycle executor.
```

---

## 9. L-18 — Combined regression (future Codex must-complete)

The branch-local suites (303 / 338 / 330 on old F/G/H) are not a combined
regression. The rebuild must produce one combined synthetic chain:

```text
F contract semantics (PlaybookContract draft, SOURCE layer + interpretation layer)
+ G feature computation (session-aware aggregation -> EMA/ADX, all L-06..L-12 fixes)
+ H trigger observation (stop-trigger, all L-13..L-17 fixes)
+ current Playbook Contract (R1 tree, Package C claim-level PRIMARY / bridge)
+ current SessionMetadata (R1 tree, Package D authority identity)
+ current ResearchFirewall (R1 tree, material-bound SOURCE_ONLY; firewall pre-outcome gate)
```

Mandatory constraints:

```text
SYNTHETIC_ONLY=YES
NO_CANDIDATE_OUTCOME=YES
NO_VALIDATION/HOLDOUT_ACCESS=YES
NO_REAL_STRATEGY_IDENTITY_REGISTRATION=YES
NO_FIREWALL_OUTCOME_ACCESS=YES
```

The chain must prove at least:

1. one synthetic 1m bar stream -> `SessionMetadata` (authority identity) ->
   `TimeframeAggregator` (L-06/07/08 fixed, zero incomplete buckets on a
   complete synthetic day) -> EMA/ADX (L-09/10/11/12 fixed) with verified
   feature identities;
2. the Playbook Contract draft validates to the expected `NOT_MACHINE_READY`
   blockers (no silent machine-ready while Owner gates are open);
3. stop orders evaluate the identical materialized bar tuple (L-13), bind
   source bar identities (L-14), execute the version they declare (L-15), and
   follow the conservative chronology + OCO lifecycle (L-16/L-17);
4. firewall SOURCE_ONLY denial and pre-outcome gate behavior still hold in the
   combined tree;
5. `python -m unittest discover -s tests -v` green, `git diff --check` clean.

`CLASS=UNAMBIGUOUS_IMPLEMENTATION_FIX` (deliverable definition; execution
blocks on the gates in section 12 for the Holy Grail PRIMARY-specific parts,
not for the generic machinery).

---

## 10. Foundation conflict graph

For each old branch, the authoritative mapping. `CURRENT_MAIN_REPLACEMENT`
points at the R1 tree unless stated.

### 10.1 PlaybookContract

```text
OLD_FILE=src/playbook_contract.py  (baseline 6477124 schema consumed by old F builder)
OLD_SYMBOL=PlaybookContract / InterpretationBranch / ObservationSurface / MachineOperationalization / validate_contract
CURRENT_MAIN_REPLACEMENT=src/playbook_contract.py on integration/r1-cdf-ecore-e10-v01
   (Package C: claim-level PRIMARY, primary_selection_identity,
    validate_strategy_against_playbook_contract, single-timeframe bridge,
    PARTIALLY_OBSERVABLE/UNKNOWN-transfer/multi-timeframe blockers)
PORT_DIRECTLY=InterpretationBranch / ObservationSurface / SourceClaimRef concepts and identities
REWRITE_REQUIRED=contract construction to new schema; claim-level PRIMARY selection; machine layer
   (operationalization_reference/code_hash/environment_hash/required_feature_versions/parameter_identities)
DO_NOT_PORT=old contract_identity hash and old JSON; old single-contract PRIMARY gating (P-01);
   old `primary_required`-only semantics (now claim-level and unconditional)
```

### 10.2 StrategyIdentity

```text
OLD_FILE=src/strategy_evidence.py  (baseline; none of F/G/H created a real identity)
OLD_SYMBOL=StrategyIdentity / StrategyCatalog
CURRENT_MAIN_REPLACEMENT=src/strategy_evidence.py on R1 tree (playbook_contract_identity binding)
   + bridge_to_strategy_identity + validate_strategy_against_playbook_contract (single shared validator)
PORT_DIRECTLY=nothing from old branches (they created no identities)
REWRITE_REQUIRED=any future identity creation must go through bridge_to_strategy_identity on a
   MACHINE_READY single-timeframe contract
DO_NOT_PORT=manual StrategyIdentity construction outside the bridge; ","-joined multi-timeframe strings
```

### 10.3 ResearchFirewall

```text
OLD_FILE=src/research_firewall.py  (baseline read by old F/G/H; none modified it)
OLD_SYMBOL=ResearchFirewall / SourceOnlySession / ApprovedSourceBundle / WaveHypothesisBinding
CURRENT_MAIN_REPLACEMENT=src/research_firewall.py on R1 tree (Package F: ApprovedSourceMaterialRef
   forward-only byte binding, historical_unbound, open_verified_session material-bound)
PORT_DIRECTLY=SOURCE_ONLY claim binding pattern used by old F (claims loaded from session evidence)
REWRITE_REQUIRED=old F draft's session/bundle identity + verification_evidence handling must be
   re-validated against material-bound verification (EXACT_BYTES_BOUND vs NOT_RECORDED)
DO_NOT_PORT=self-attested "verification_evidence" strings as unforgeable proof; caller-declared
   primary/scope/search identities (F-06..F-08); any pre-outcome gate bypass (F-01..F-03)
```

### 10.4 SessionMetadata

```text
OLD_FILE=src/data_substrate.py  (old G added `window_at` accessor, +19 lines on baseline)
OLD_SYMBOL=SessionMetadata / SessionWindow / window_at (G-added)
CURRENT_MAIN_REPLACEMENT=src/data_substrate.py on R1 tree (D-05 authority_reference version,
   D-02 expected_bar_starts / expected_bar_starts_between / missing_bar_starts)
PORT_DIRECTLY=SessionWindow fields; expected_bar_starts / missing_bar_starts; trading_day_at
REWRITE_REQUIRED=old G aggregation to call the D-repaired API; replace window_at with the
   authoritative window/expected enumeration (no second session model)
DO_NOT_PORT=caller-string version identity; window_at accessor; observed-window-only grouping
   (L-06/L-07); weekday/civil-date inference
```

### 10.5 ArtifactBinding

```text
OLD_FILE=did not exist at baseline 6477124 (Package A/B added it after)
OLD_SYMBOL=n/a
CURRENT_MAIN_REPLACEMENT=src/strategy_evidence.py ArtifactBinding.from_bytes / from_file (P-06/B;
   digest computed only from actual bytes; no caller-supplied digest)
PORT_DIRECTLY=use ArtifactBinding.from_bytes for: feature code hash (L-11), MachineOperationalization
   code_hash, trigger model version verification (L-15)
REWRITE_REQUIRED=n/a in old branches (they predate it)
DO_NOT_PORT=any caller-supplied digest / version-label-only identity for code/feature artifacts
```

### 10.6 Old F files

```text
tools/build_raschke_holy_grail_playbook_contract_draft.py  -> REWRITE_REQUIRED (new schema; claims binding kept)
docs/evidence/RASCHKE_HOLY_GRAIL_INTERPRETATION_FREEZE_V0_1.md -> REWRITE_REQUIRED (keep INFERRED predeclarations;
   reclassify L-01..L-05 items per sections 2-6; keep PRIMARY_FREEZE_READY=NO)
docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.json -> REWRITE_REQUIRED (regenerate under R1 schema)
docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.md -> REWRITE_REQUIRED
```

### 10.7 Old G files

```text
src/technical_features.py  -> REWRITE_REQUIRED (L-06..L-12; keep TimeframeSpec/AggregatedBar/IncompleteBucket/
   AggregationResult/FeatureValue/ADXValue shape; fix identity/completeness/stream binding)
src/data_substrate.py window_at delta  -> DO_NOT_PORT (D-05 replaces)
docs/architecture/POINT_IN_TIME_TECHNICAL_FEATURES_V0_1.md -> REWRITE (V0_2) for the fixes
tests/test_technical_features.py -> REBUILD with the completeness/identity regressions
```

### 10.8 Old H files

```text
src/stop_order_execution.py  -> REWRITE_REQUIRED (L-13..L-17; keep RestingStopOrder/StopTriggerResult/
   evaluate_stop_order/evaluate_stop_group; fix identity/version/chronology/lifecycle)
docs/architecture/STOP_TRIGGER_EXECUTION_SEMANTICS_V0_1.md -> REWRITE (V0_2) for L-13..L-17 + conservative chronology
tests/test_stop_order_execution.py -> REBUILD with generator/identity/version/OCO regressions
```

---

## 11. Exact Codex work graph

Recommended construction order. Every phase lists allowed files, forbidden
decisions, and exit tests. `SCOPE` = files Codex may touch; anything else on
the R1 tree is read-only.

### PHASE_1 — source/semantic freeze prerequisites

```text
PURPOSE=freeze the INFERRED/labeled conventions that are SOURCE_SEMANTIC_AUTHORITY_REQUIRED or
        OWNER_DECISION_REQUIRED, and record them as gates; no code.
ALLOWED=docs/reviews/FGH_CODEX_REBUILD_PREPARATION_V0_1.md (this authority),
        docs/research/semantic_completion/* (non-frozen annotations only),
        docs/evidence/*FREEZE* / *INTERPRETATION* (label-only updates)
FORBIDDEN=choosing EMA touch reference/price input (L-01); ADX rising window/timing (L-02);
        EMA/ADX numeric conventions (L-03); same-bar touch->entry policy (L-04); fill->stop
        chronology (L-05/L-16); operating timeframe; swing-low/high; trailing; exit-on-new-highs;
        any candidate outcome data; any src change
EXIT=all section-12 gates documented with DECISION_ID/QUESTION/OPTIONS/OUTCOME_EFFECT/
     RECOMMENDED_SAFE_DEFAULT; no resolution silently adopted; PRIMARY_FREEZE_READY remains NO
```

### PHASE_2 — Playbook draft port (old F -> R1 schema)

```text
ALLOWED=tools/build_raschke_holy_grail_playbook_contract_draft.py (rewrite),
        docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_1.{md,json} (regenerate),
        docs/evidence/RASCHKE_HOLY_GRAIL_INTERPRETATION_FREEZE_V0_1.md (reclassify),
        tests for the builder (draft validation expectations)
FORBIDDEN=resolving critical ambiguity; selecting PRIMARY; choosing a single operating timeframe;
        inventing source claims; modifying src/playbook_contract.py; creating StrategyIdentity
EXIT=builder runs against R1 playbook_contract.py; validate_contract returns NOT_MACHINE_READY with the
     exact expected blockers (UNRESOLVED_CRITICAL_AMBIGUITY, CLAIM_PRIMARY_MISSING,
     MULTIPLE_TIMEFRAMES_UNRESOLVED, REQUIRED_INPUT_NOT_FULLY_OBSERVABLE where applicable,
     MACHINE_OPERATIONALIZATION_MISSING); JSON regenerated deterministically; no identity registered
```

### PHASE_3 — feature engine rebuild (old G)

```text
ALLOWED=src/technical_features.py (new owner file), tests/test_technical_features.py,
        docs/architecture/POINT_IN_TIME_TECHNICAL_FEATURES_V0_2.md
        (src/data_substrate.py ONLY if a minimal additive accessor is strictly required; prefer reuse)
FORBIDDEN=choosing Holy Grail EMA price input/period/ADX semantics (contract inputs, not engine
        decisions); deciding numeric quantization policy (FGH-GATE-03); hard-coding 14/20;
        reading the real canonical corpus
EXIT=L-06/07/08 closed via expected_bar_starts/missing_bar_starts; L-09 prefix identity; L-10 stream
     binding; L-11 ArtifactBinding code hash; L-12 continuity fail-closed; all synthetic tests green
```

### PHASE_4 — trigger/stop rebuild (old H)

```text
ALLOWED=src/stop_order_execution.py (new owner file), tests/test_stop_order_execution.py,
        docs/architecture/STOP_TRIGGER_EXECUTION_SEMANTICS_V0_2.md
FORBIDDEN=changing conservative same-bar semantics without Owner (FGH-GATE-04/05); caller-declared
        trigger_model_version; claiming exchange-resting chronology; reading the real corpus
EXIT=L-13 materialize-once; L-14 bar-identity/evaluated-sequence binding; L-15 executed-version
     verification; L-16 explicit conservative completed-bar model label; L-17 OCO sibling
     cancellation; AMBIGUOUS_INTRABAR_SEQUENCE preserved
```

### PHASE_5 — combined synthetic chain

```text
ALLOWED=src/technical_features.py + src/stop_order_execution.py (integration-only fixes),
        new synthetic combined regression tests in tests/, a synthetic chain runner in tools/,
        docs/evidence/*COMBINED* engineering evidence
FORBIDDEN=real corpus; candidate outcomes; validation/holdout access; real StrategyIdentity
        registration; firewall outcome access
EXIT=one synthetic 1m stream -> SessionMetadata (D-05) -> aggregator -> EMA/ADX -> Playbook draft
     (F) -> stop orders (H) -> ExecutionObservation -> synthetic validation path; identities
     verified end-to-end; combined regression green
```

### PHASE_6 — full regression

```text
ALLOWED=fixes confined to the new feature/stop modules and their tests
FORBIDDEN=schema/authority changes; changing semantics merely to pass tests
EXIT=python -m unittest discover -s tests -v green on the combined tree; git diff --check clean;
     src production diff for pre-existing modules = 0; combined regression documented
```

---

## 12. Owner gates

`RECOMMENDED_SAFE_DEFAULT != ADOPTED`. Nothing here is frozen. These are the
gates the FGH rebuild cannot silently resolve.

### FGH-GATE-01 — EMA touch reference / price basis (L-01)

```text
DECISION_ID=FGH-GATE-01
QUESTION=Which EMA touch reference and price basis does the Holy Grail PRIMARY adopt?
OPTION_A=close-based EMA, intrabar touch `low <= EMA <= high` (old F predeclared INFERRED branch)
OPTION_B=prior-available EMA reference (no current-bar-close EMA); touch defined on the bar where
        the prior EMA is already observable
OPTION_C=other EMA price input (typical/high-low) with an explicitly defined touch rule
OUTCOME_EFFECT=defines which bars emit EMA-touch signals and the entry stop placement; materially
        changes entry bars/prices; a close-based same-bar comparison is look-ahead unless redefined
RECOMMENDED_SAFE_DEFAULT=A as a labeled INFERRED branch ONLY with same-bar causality resolved
        (combined with FGH-GATE-04); never treated as source-exact
```

### FGH-GATE-02 — ADX rising sequence (L-02)

```text
DECISION_ID=FGH-GATE-02
QUESTION=At which bar/window is "ADX rising" evaluated relative to the pullback/touch, given the
        source says "initially >30 AND rising" and the pullback is "usually accompanied by a turndown"?
OPTION_A=old F one-bar `ADX[t]>ADX[t-1]` at the context/touch bar (project-added requirement)
OPTION_B=ADX>30 and rising measured over an explicit lookback window, evaluated before the pullback
        (source-faithful "initial" context; touch bar does not need rising)
OPTION_C=explicit pullback-phase model (rising window + ADX turndown during pullback)
OUTCOME_EFFECT=changes which bars qualify as Holy Grail contexts; trade count and entry timing
RECOMMENDED_SAFE_DEFAULT=B (closest to source "initially >30 and rising") as a labeled INFERRED
        convention; old F one-bar convention must not silently stand
```

### FGH-GATE-03 — EMA/ADX numeric machine conventions (L-03)

```text
DECISION_ID=FGH-GATE-03
QUESTION=Which numeric implementation (seed/warmup/init/rounding/precision) is the project machine
        convention for EMA and Wilder ADX?
OPTION_A=adopt documented standard conventions (SMA-seeded EMA; Wilder init; exact Decimal; single
        explicit output quantization, e.g. 6dp ROUND_HALF_UP) as ENGINEERING feature semantics
OPTION_B=exact Decimal with NO intermediate quantization (quantize only at output boundaries)
OPTION_C=another explicit policy
OUTCOME_EFFECT=EMA-touch and ADX>30 classification change with seed/warmup/rounding; outcome-affecting
RECOMMENDED_SAFE_DEFAULT=A (matches old G's documented convention) adopted by Owner; not worker-frozen
```

### FGH-GATE-04 — same-bar EMA touch -> entry stop ordering (L-04)

```text
DECISION_ID=FGH-GATE-04
QUESTION=When EMA touch and entry-stop threshold are both reached inside one 1-minute bar, what is the
        machine policy?
OPTION_A=AMBIGUOUS_INTRABAR_SEQUENCE (fail closed; no entry on that bar)
OPTION_B=defer entry decision to the next bar (touch evaluated on completed prior bar)
OPTION_C=separate explicitly justified finer chronology (not available at 1-minute)
OUTCOME_EFFECT=determines whether ambiguous same-bar bars produce entries; direct entry/trade-count
        effect
RECOMMENDED_SAFE_DEFAULT=A (consistent with old H's existing fail-closed semantics)
```

### FGH-GATE-05 — same-bar fill -> protective stop + chronology model (L-05 + L-16)

```text
DECISION_ID=FGH-GATE-05
QUESTION=Which conservative policy covers same-bar fill+protective-stop ordering, and which execution
        chronology does the stop bridge claim?
OPTION_A=completed-bar availability + AMBIGUOUS_INTRABAR_SEQUENCE for same-bar fill/stop (conservative;
        old H model, explicitly labeled, never called exchange-resting)
OPTION_B=next-bar-only protective-stop activation (old F INT-STOP-ACTIVATION-AFTER-FILL) — REJECTED as
        silent same-bar risk suppression unless Owner explicitly overrides
OPTION_C=separately justified intrabar/gap-through model (requires project-owned intrabar evidence)
OUTCOME_EFFECT=defines the protective-stop loss path and any same-bar ambiguity handling; interacts
        with entry fill, gap-through, OCO
RECOMMENDED_SAFE_DEFAULT=A
INTRA_BAR_ORDERING=NOT_OBSERVABLE_AT_1M
```

### FGH-GATE-06 — operating timeframe PRIMARY (pre-existing unresolved critical ambiguity)

```text
DECISION_ID=FGH-GATE-06
QUESTION=Which single operating timeframe is the Holy Grail PRIMARY (source is explicitly
        multi-timeframe: base then 30/60/120-minute)?
OPTION_A=BASE (base chart)
OPTION_B=30MIN / OPTION_C=60MIN / 120MIN
OUTCOME_EFFECT=the bridge requires exactly one timeframe_scope value (Package C P-05); no PRIMARY /
        MACHINE_READY Holy Grail strategy is possible until resolved; machinery must not hard-code it
RECOMMENDED_SAFE_DEFAULT=no default; remains TIMEFRAME_PRIMARY=UNRESOLVED until Owner selects with a
        non-outcome justification (as already required by old F's AMBIGUOUS_STOP)
```

Note: `NEWLY_FORMED_SWING_LOW/HIGH_MACHINE_DEFINITION`, `TRAILING_STOP_MACHINE_DEFINITION`, and
`EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION` remain pre-existing unresolved critical ambiguity
(from old F's AMBIGUOUS_STOP), outside the L-01..L-18 remap scope but prerequisites for any future
Holy Grail PRIMARY freeze. They are referenced here, not re-derived.

---

## 13. Artifacts

```text
docs/reviews/FGH_CODEX_REBUILD_PREPARATION_V0_1.md        (this document)
docs/reviews/FGH_CODEX_REBUILD_FINDING_MATRIX_V0_1.json   (machine-readable matrix)
```

No production code added. No default tests added. No merge of old branches.

---

## 14. Validation

```text
SRC_PRODUCTION_DIFF=0            (only docs/reviews/ changed on this branch)
python -m unittest discover -s tests -v   (baseline must remain green)
git diff --check                 (clean)
```

---

## 15. Push

```text
BRANCH=prep/fgh-codex-rebuild-v01
PUSH=origin
```

---

## Appendix A — Source evidence anchors (Holy Grail)

```text
ADX_PERIOD=14 / ADX_THRESHOLD>30 / ADX_RISING>30-and-rising   SR-V0-M01 HOLY_GRAIL_RULES; SR-V0-M05
20-period EMA / pullback-to-EMA                                SR-V0-M01; SR-V0-M02 PULLBACK_TO_MA; SR-V0-M05
buy stop above previous-bar high / touch 20 EMA                SR-V0-M01 step 3
protective sell stop at newly formed swing low "once filled"   SR-V0-M01 step 4
"usually accompanied by a turndown in ADX" (pullback nuance)   SR-V0-M01 step 2
trail stops as profits grow                                    SR-V0-M01
30/60/120-minute sequence, each with 14-bar ADX>30             SR-V0-M05
multi-timeframe explicit; no single operating timeframe        SR-V0-M05 (PARTIALLY_PINNED)
```

The machine conventions in old G/H (`INT-EMA-TOUCH-INTRABAR`, `INT-ADX-RISING-1BAR`,
`INT-STOP-ACTIVATION-AFTER-FILL`, `STOP_MARKET_TRIGGER_MODEL_V0_1`, SMA-seeded EMA, Wilder init,
6dp ROUND_HALF_UP) are all ENGINEERING/INFERRED project conventions, not human-source facts.
