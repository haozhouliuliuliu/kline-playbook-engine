# CANONICAL_COMPLETENESS_AUTHORITY_RESOLUTION_V0_1

> Date: 2026-08-21  
> Branch: `preoutcome/canonical-revalidation-v01`  
> Scope: authority/design resolution only; no market download, no TqSdk login,
> no 116 or 32,980 re-run, no repaired corpus materialization, and no outcome access.

## Decision status

```text
RESOLUTION_STATUS=OWNER_SEMANTIC_GATE_REQUIRED
PROJECT_BRAIN_RECOMMENDED_PATH=QUALIFIED_ELIGIBILITY_VIEW_WITH_UNIFORM_FIRST_TRADING_DAY_EXCLUSION
HISTORICAL_ACCEPTED_CORPUS_MODIFIED=NO
CANDIDATE_SCOPE_SEMANTICS_ADOPTED=NO
```

The recommended path is not adopted by this document. It changes the
candidate-quality input scope and therefore requires one Owner decision.

## 1. Terms that must not be conflated

| Term | Meaning | What it does not prove |
|---|---|---|
| `SESSION_IS_OPEN` | The governed schedule says a market session is open. | That a specific concrete contract traded in every minute. |
| `TRADE_OR_BAR_EXISTS` | A trade produced a bar for a concrete contract/minute. | That every scheduled minute must have one. |
| `PROVIDER_STORES_BAR` | TqSdk has a bar in its historical series. | That absence is an exchange outage or a provider loss. |
| `PROJECT_RECEIVED_BAR` | The project saved a returned provider bar. | That the provider stored every possible bar. |
| `CERTIFIED_PARTITION` | A partition satisfies the currently frozen D01/D02 rules. | That excluded historical data is deleted or false. |
| `CANDIDATE_ELIGIBLE_VIEW` | A separate, identity-bound subset permitted as research input. | Historical canonical acceptance or source semantics have changed. |

TqSdk first-party semantics state that a request range filters existing series
data, does not guarantee one K-line per session minute, and can skip times
with no data. They do not provide an independent, contract/minute-specific
authority for the first available bar.

## 2. Re-evaluation of D01 and D02

`D01` (`returned_start == requested_start` and `returned_end == requested_end`)
is a strict transport/coverage contract. It is suitable when the requested
range is independently known to contain bars at both boundaries. It is not a
general proof of completeness for a sparse-bar API, because a valid provider
series may begin after an open-session request start.

`D02` (every scheduled complete minute minus observed bars) is a strict
session-population contract. It incorrectly assumes that every open session
minute necessarily contains a bar when used directly against TqSdk sparse
K-lines. It remains valuable as an anti-laundering check: provider observations
must not silently redefine the expected set.

Therefore neither rule may be relaxed by setting `expected_start` to the first
observed/returned bar. That would make observed data define the completeness
authority it is supposed to be checked against.

## 3. Evidence used

| Evidence | Bound fact |
|---|---|
| `CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1` | 32,980 checked; 32,864 pass; 116 fail. |
| `CANONICAL_FIRST_DAY_PROVIDER_PROBE_V0_1` | Six deterministic representatives: all six original requests repeat truncation; three severe day-only requests still truncate; 11,496 overlapping OHLC comparisons, zero mismatch. |
| `CANONICAL_FIRST_DAY_SCOPE_ADJUDICATION_V0_1` | Full 116 reacquisition and repaired-corpus materialization are not permitted under existing authority. |
| Provider-semantics addendum `4250d…fa8d` | TqSdk returns existing bars in range; no bar-per-minute guarantee; no-data times can be skipped. |
| `CANONICAL_CONTRACT_UNIVERSE.json` + accepted manifest/raw | Deterministic first-trading-day inventory and row-impact calculation below. |

No candidate outcome, validation, final-holdout, Shadow, broker, payment, or
new source access was used.

## 4. Candidate paths considered

| Path | Decision | Reason |
|---|---|---|
| A. `PROVIDER_SPARSE_BAR_COMPLETENESS` | REJECT | Saving all returned bars is valid provenance, but cannot independently prove TqSdk did not omit a stored bar. Treating returned sparsity as completeness is circular. |
| B. `UNIFORM_FIRST_TRADING_DAY_EXCLUSION` | VIABLE, OWNER-GATED | A rule fixed from governed contract bounds excludes every contract's first trading day, not the observed failures only. It avoids selection on performance or provider outcome. |
| C. `FIRST_AVAILABLE_BAR_BOUNDARY` | REJECT | The proposed boundary comes from the same observed provider data. It violates D02 non-laundering unless a separate versioned source proves it. |
| D. `SECOND_SOURCE_OR_TICK_AUTHORITY` | VIABLE FUTURE SOURCE PATH | Requires an independently governed source that can establish contract/minute trade or bar existence. The repository has no such minute/tick authority; acquisition, entitlement, cost, and source verification are separate gates. |
| E. `QUALIFIED_ELIGIBILITY_VIEW` | RECOMMENDED IMPLEMENTATION FORM | Preserve the historical accepted corpus; define a separate deterministic candidate-eligible view that uses B's uniform exclusion and fails closed for excluded input. |

## 5. Deterministic impact of B + E

The calculation reads only the accepted manifest and the 212 governed
first-trading-day raw artifacts; it does not revalidate the 32,980 corpus.

| Product | First-day partitions | Excluded rows |
|---|---:|---:|
| ag | 36 | 15,840 |
| al | 36 | 10,958 |
| au | 32 | 14,850 |
| cu | 36 | 11,606 |
| ni | 36 | 7,045 |
| rb | 36 | 10,393 |
| **Total** | **212** | **70,692** |

```text
TOTAL_ACCEPTED_ROWS=15280452
UNIFORM_FIRST_DAY_EXCLUDED_ROWS=70692
EXCLUDED_ROW_PERCENT=0.46263029
REMAINING_ELIGIBLE_PARTITIONS=32768
REMAINING_ELIGIBLE_REPAIRED_D01_D02_PASS=32768
```

The rule creates 212 contract/date holes, distributed over 25 first-trading
dates for each product (2024-01-02 through 2025-12-16). It does not create a
whole-product/day absence: other concrete contracts can remain present on those
dates. It also excludes 96 clean first-day partitions along with the 116
uncertified ones, so it does not select on the observed failure label.

## 6. E07 and candidate-runtime consequence

E07 historical main-contract mapping is already an incomplete, fail-closed
prerequisite. A future source-governed mapping must resolve a concrete contract
before candidate input access. If that resolved contract/date is excluded by
the candidate-eligible view, runtime access must deny the request before any
feature, candidate, validation, or execution computation. It must not select a
different contract, synthesize bars, or fall back to the accepted raw corpus.

This is an additional eligibility check, not an E07 substitute and not a
project-authored main-contract mapping rule.

## 7. Recommended Owner decision

```text
QUESTION=Should candidate-quality research use a new deterministic qualified eligibility view that uniformly excludes every concrete contract's governed first trading day, while retaining the historical accepted corpus unchanged?

OPTION_A=Approve qualified eligibility view v1: exclude all 212 first-day partitions (70,692 rows; 0.46263029%); candidate access to them fails closed; retained eligible set is 32,768/32,768 repaired-D01/D02 certified partitions.
OPTION_B=Do not adopt exclusion: keep candidate-quality research blocked until an independently governed minute/tick or provider-availability authority defines exact expected coverage.

RECOMMENDED_OPTION=OPTION_A
ALTERNATIVE=OPTION_B
```

Option A is recommended because it is deterministic from pre-existing
governed listing dates, applies equally to all first days (including clean
ones), preserves all accepted source artifacts, avoids observed-data laundering,
and removes only 0.46263029% of rows. It is still a new research-input scope
semantic and must not be adopted by implementation alone.

Option B retains maximal potential information but leaves candidate-quality
research blocked for an unknown time and requires a new independently governed
source/availability authority.

## 8. Engineering preparation permitted only after Option A

After explicit Owner approval, a separate bounded package may implement an
identity-bound `QUALIFIED_ELIGIBILITY_VIEW_V1` with lineage to the historical
corpus and assertions that excluded partition access fails closed. It must not
rewrite historical raw, Parquet, manifest, catalog, acceptance evidence, or
the frozen D01/D02 evidence. Its identity must bind at least the parent corpus
identity, contract-universe identity, exclusion rule version, exact excluded
partition identities, and implementation bytes.
