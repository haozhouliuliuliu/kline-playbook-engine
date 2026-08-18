# HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0

> Version: 1.0
> Date: 2026-08-19
> Status: IMPLEMENTED_AND_TESTED / ENGINEERING_VERIFIED
> Work package: `HUMAN_PLAYBOOK_PREOUTCOME_RESEARCH_FIREWALL_IMPLEMENTATION`
> Tool decision: `USE_EXISTING` (no new tool adopted)

## 1. Frozen authority references (do not modify)

- `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

Frozen facts preserved unchanged:

```text
RESEARCH_PROTOCOL_VERSION=1.0
RESEARCH_PROTOCOL_STATUS=FROZEN_BINDING

DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31

PROJECT_GOVERNED_HISTORICAL_HOLDOUT != PROSPECTIVE_GENUINELY_UNSEEN_DATA
```

This is ordinary engineering implementation under Protocol v1.0 §16. It does not
modify any frozen research semantics, the frozen 12/6/6 split, the Owner freeze
evidence, PRIMARY_BRANCH semantics, RESEARCH_WAVE semantics,
`INSUFFICIENT_EVIDENCE`, CAT1/CAT2/CAT3, live AI semantics, or the
historical-final state machine.

## 2. Implementation owner / module

Single owner of the pre-outcome research access rules:
`src/research_firewall.py` — `ResearchFirewall`, `PreOutcomeGate`,
`SourceOnlyPolicy`, `SourceOnlySession`, `ResearchWaveRegistry`,
`ResearchWaveManifest`, `StatisticalProfileRegistry`,
`CommonStatisticalProfile`, `HistoricalFinalHoldoutStateMachine`,
`classify_cohort`, frozen constants.

Legacy compatibility:
`src/strategy_evidence.py` — `DatasetClass` gained the canonical
`PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT` and `SHADOW_FORWARD` members;
`FINAL_UNSEEN` is kept as a legacy name. `FinalUnseenFirewall` is now a thin
compatibility adapter that **delegates every decision** to `ResearchFirewall`.
There is exactly one owner of the access rules; there is no second parallel
firewall rule set in the project.

## 3. Implemented controls

| Control | Status | Where |
| --- | --- | --- |
| SOURCE_ONLY_CONTROLS | ACTIVE_AND_VERIFIED (engineering) | `SourceOnlyPolicy` / `SourceOnlySession` |
| COMMON_STATISTICAL_PROFILE | interface + lock implemented; real numeric profile NOT designed | `CommonStatisticalProfile` / `StatisticalProfileRegistry` |
| MULTIPLICITY_COUNTING_UNIT | LOCKED control enforced by the gate | `PreOutcomeGate` |
| RESEARCH_WAVE | LOCKED (immutable manifest) | `ResearchWaveRegistry` / `ResearchWaveManifest` |
| PRIMARY_SCOPE_SEARCH_IDENTITIES | LOCKED control enforced by the gate | `PreOutcomeGate` |

### 3.1 SOURCE_ONLY

`SourceOnlySession` records at least:
- model identity/version;
- prompt/spec version;
- source bundle identity/hash;
- tool/retrieval mode;
- protected market access mode;
- explicit researcher/model exposure note.

`SourceOnlyPolicy.is_verified()` requires `protected_market_access_mode ==
TECHNICALLY_DENIED`. A `PROMPT_ONLY` mode ("the prompt said do not look") is
**not** technical denial and is not verified. The policy exposes **no**
protected-period market outcome retrieval surface; the only market-outcome-related
entry point (`request_protected_market_outcome`) always returns `DENIED` and
records the denial.

This does **not** claim to eliminate external model latent memory. Latent/parametric
prior market knowledge that cannot be proven absent remains a disclosed residual
threat-model risk under the frozen protocol.

### 3.2 RESEARCH_WAVE

`ResearchWaveManifest` is immutable (frozen dataclass) and binds:
- research_wave_id;
- protocol version;
- statistical profile version;
- tested family/claim identities;
- PRIMARY branch identities;
- declared outcome-tested alternatives;
- instrument/timeframe/context scope;
- parameter/search ranges;
- denominator/counting semantics.

`ResearchWaveRegistry` enforces:
- waves are buildable before outcome testing starts;
- once locked, a wave's test set cannot be modified (`add_tested_hypothesis`
  raises after lock);
- after the first outcome-bearing test, new hypotheses require a new wave /
  new search event;
- FAIL and `INSUFFICIENT_EVIDENCE` entries remain permanently in the denominator
  (no deletion path exists).

### 3.3 Common statistical profile interface

`CommonStatisticalProfile` implements fields, identity hash, version, lock state,
and a `TEST_ONLY` marker for fixtures. This package deliberately does **not**
decide the final confidence method, minimum-event numbers, multiplicity-correction
numbers, or dependence thresholds. The real `COMMON_STATISTICAL_PROFILE_V1` numeric
standard must be designed and independently reviewed separately under Protocol v1.0
before any candidate outcome.

### 3.4 Pre-outcome gate

`PreOutcomeGate` is a single fail-closed gate. Before any candidate outcome-bearing
performance access, all five controls must be satisfied:

```text
SOURCE_ONLY_CONTROLS            = ACTIVE_AND_VERIFIED
COMMON_STATISTICAL_PROFILE      = LOCKED
MULTIPLICITY_COUNTING_UNIT      = LOCKED
RESEARCH_WAVE                   = LOCKED
PRIMARY_SCOPE_SEARCH_IDENTITIES = LOCKED
```

Any missing/unknown prerequisite -> `DENIED`. Because only `TEST_ONLY` profiles
exist in this package, the only reachable grant is
`SYNTHETIC_DEVELOPMENT_OUTCOME_ONLY` (synthetic dummy fixtures). A `TEST_ONLY`
profile refuses a non-synthetic fixture
(`TEST_ONLY_PROFILE_REQUIRES_SYNTHETIC_FIXTURE`).

## 4. Denied paths

- missing SOURCE_ONLY -> DENY;
- SOURCE_ONLY unverified (including PROMPT_ONLY) -> DENY;
- statistical profile missing / draft / unlocked -> DENY;
- multiplicity counting unit unlocked -> DENY;
- research wave missing / unlocked -> DENY;
- PRIMARY/scope/search identities unlocked -> DENY;
- VALIDATION -> default DENY (no explicit validation authority in this package);
- PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT -> always DENY
  (`FINAL_HISTORICAL_HOLDOUT_ALWAYS_LOCKED`);
- Shadow/Forward -> DENY (`SHADOW_FORWARD_NOT_AUTHORIZED`);
- out-of-scope dates -> DENY;
- locked wave cannot append hypothesis -> DENY/raise;
- final-holdout unlock is never automatic; exposure requires a separate,
  explicitly registered unlock authority and no such authority is registered by
  default.

## 5. Historical final naming and state machine

Compatibility migration: `DatasetClass.FINAL_UNSEEN` is preserved (old code/tests
keep working). The canonical semantic name
`DatasetClass.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT` was added, plus
`DatasetClass.SHADOW_FORWARD`. Both final names and Shadow/Forward are always
denied by the single owner.

State machine (`HistoricalFinalHoldoutStateMachine`):

```text
FINAL_HISTORICAL_HOLDOUT_LOCKED
-> FINAL_HISTORICAL_HOLDOUT_EXPOSED
-> FINAL_ACCEPTED | FINAL_REJECTED | FINAL_VOID_IMPLEMENTATION_DEFECT
```

This package implements **no** automatic final-holdout unlock. `VOID` changes a
conclusion and never restores holdout status.

## 6. Compatibility approach

- `FinalUnseenFirewall` keeps its legacy constructor and interface
  (`request_access(experiment, dataset_class)`, `has_exposure(...)`) and now
  delegates to `ResearchFirewall.legacy_request_access`.
- `validation_runner.py` and `portfolio_semantics.py` continue to use
  `FinalUnseenFirewall` unchanged; their existing behavior (final-cohort deny,
  deterministic records) is preserved and covered by the existing test suite.
- Coarse DEVELOPMENT/VALIDATION grants through the legacy path are **not**
  candidate-outcome authorization. The authoritative candidate-outcome path is
  `ResearchFirewall.request_candidate_outcome_access` / `evaluate_gate`, which is
  fail-closed. This is documented in `tests/test_research_firewall.py`
  (`test_legacy_coarse_grants_are_not_candidate_outcome_authorization`).

## 7. Tests

New: `tests/test_research_firewall.py` (38 tests) covering:
- frozen 12/6/6 chronology classification and constants;
- SOURCE_ONLY session/policy (verification, PROMPT_ONLY not technical denial,
  technical denial of market-outcome requests, exposure note, identity
  determinism);
- research wave immutability, lock, append-after-lock denial, append-after-test
  requires new wave, permanent denominator with FAIL / INSUFFICIENT_EVIDENCE;
- statistical profile registry lock/identity and TEST_ONLY marker;
- historical final-holdout state machine (no auto-unlock, authority required,
  VOID never restores);
- the 14 minimum pre-outcome gate checks;
- firewall integration (default deny, final always denied even when controls
  satisfied, legacy coarse grants are not candidate-outcome authorization).

Canonical suite: `python -m unittest discover -s tests -v`
Result: 219 tests OK (3 skipped), including the pre-existing 181 tests unchanged
(no regression).

## 8. Known limitations

- `CommonStatisticalProfile` is an identity/lock interface only; the real numeric
  standard is not designed here (by design).
- The legacy runner/portfolio paths can still execute non-outcome engine-sanity /
  dummy-fixture runs on DEVELOPMENT/VALIDATION; those are not candidate-outcome
  authorization and cannot inform candidate quality.
- External model latent memory is a disclosed residual threat-model risk and is
  not claimed to be eliminated by SOURCE_ONLY technical controls.

## 9. Still NOT implemented

- Real `COMMON_STATISTICAL_PROFILE_V1` numeric standard (confidence method,
  minimum-event numbers, multiplicity correction, dependence thresholds);
- a separate explicit validation authority;
- a separate final-holdout unlock authority (deliberately absent);
- Shadow/Forward activation;
- wiring of the authoritative gate into every historical legacy runner call path
  (the authoritative path exists and is fail-closed; legacy coarse grants are
  explicitly non-authorizing);
- real Human Playbook claim extraction / candidate PnL.

## 10. Candidate performance backtest status

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

Exact reason it remains locked/unlocked: the single pre-outcome gate is
implemented and fail-closed, but the real `COMMON_STATISTICAL_PROFILE_V1` is not
yet designed or locked. Only `TEST_ONLY` profiles exist, so no real-candidate
outcome-bearing access can pass the gate
(`TEST_ONLY_PROFILE_REQUIRES_SYNTHETIC_FIXTURE`), and no candidate PnL / equity /
expectancy / Sharpe / win-loss inspection is possible through the authoritative
path. VALIDATION and the historical final holdout remain locked.

Next step (unchanged by this package):

```text
COMMON_STATISTICAL_PROFILE_V1_DESIGN_AND_INDEPENDENT_REVIEW
```

SOURCE_ONLY controls are implemented and verified; the project may proceed to
controlled real claim extraction under Claim Schema v1.0. This package performed
no real claim extraction and no real candidate outcome backtest.
