# E07 Source-Governed TqSdk Main Mapping — Prep V0.1

> Task: `E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_PREP_V0_1`
> Role: API-independent engineering preparation ONLY. NOT a mapping acquisition,
> NOT a strategy backtest, NOT a runtime wiring, NOT an outcome study.
> Date: 2026-08-21
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Branch: `preoutcome/e07-mapping-prep-v01`
> Baseline: `e87315dd622689eb165dbe81f1728c868cc06a26` (`origin/main`)

```text
E07_MAPPING=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
SOURCE_POLICY=FREE_PUBLIC_UNAUTHENTICATED_FIRST
LOGIN_USED=NO
NETWORK_USED=NO
OUTCOME_DATA_USED=NO
TQSDK_IMPORT_USED=NO
DECODE_ADAPTER_IMPLEMENTED=NO
PROJECT_AUTHORED_MAPPING_SUBSTITUTE=FORBIDDEN_NOT_USED
PSEUDO_MAIN_PRICE_BARS=FORBIDDEN_NOT_USED
```

## 1. Result summary

```text
TQSDK_HISTORY_ACCESS=LOGIN_REQUIRED
E07_MAPPING_COMPLETENESS=INCOMPLETE
E07_RUNTIME_MAPPING_STATUS=FAIL_CLOSED_PREREQUISITE
BLOCKED_API_CONTRACT_NOT_PINNED=YES
COMPLETE_MAPPING_ARTIFACT_CREATED=NO
```

This package implements the **API-independent engineering preparation** for the
source-governed TqSdk historical main-contract mapping. It does **not** obtain,
decode, or apply any real mapping. Because the exact TqSdk
`query_his_cont_quotes` response contract is not pinned by evidence, no TqSdk
decode adapter is written and `BLOCKED_API_CONTRACT_NOT_PINNED` is recorded.

## 2. Binding Owner rule (frozen; not re-selected here)

Authority: `docs/reviews/PACKAGE_E_OWNER_DECISION_APPROVAL_2026-08-20.md` and
`docs/evidence/E07_TQSDK_HISTORICAL_MAIN_MAPPING_AVAILABILITY_V0_1.md`.

```text
E07_STATUS=OWNER_APPROVED_BINDING
E07_MAPPING=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
E07_PSEUDO_MAIN_PRICE_BARS_IN_CANONICAL_CORPUS=FORBIDDEN
E07_OUTCOME_BASED_MAPPING_SELECTION=FORBIDDEN
```

## 3. Pinned vs not pinned (why `BLOCKED_API_CONTRACT_NOT_PINNED`)

The availability evidence pins the interface **name** and **documented
behaviour**:

- `TqApi.query_his_cont_quotes(symbol, n)` returns, per effective date, the
  标的 (underlying concrete) contract for each 主连 (main) symbol;
- it requires an authenticated `TqApi` session bound to `TqAuth(account, password)`;
- vendor main symbols use the `KQ.m@` form;
- the source-defined switch applies at the next trading day's open.

The evidence does **not** pin the exact wire/response schema (field names,
effective-date representation, record structure) of that interface. Per the
project's `UNKNOWN_OVER_GUESSING=REQUIRED` rule, this package does **not** guess
or implement any TqSdk response decoding. It records:

```text
BLOCKED_API_CONTRACT_NOT_PINNED=YES
TQSDK_DECODE_NOT_IMPLEMENTED="TqSdk query_his_cont_quotes response schema is not pinned"
```

A decode adapter may only be written after the exact response contract is pinned
by evidence and under explicit Owner authorization for the authenticated path.

## 4. Implemented machinery (API-independent)

Module: `src/source_governed_mapping.py`.

```text
SOURCE_GOVERNED_MAPPING_RECORD_SCHEMA=SourceGovernedMappingRecord
PROVENANCE=MappingProvenance (exact-bytes-bound consistency enforced)
EFFECTIVE_TIMESTAMP_DATE=effective_trading_date + effective_at (source-defined next-trading-day switch)
DETERMINISTIC_NORMALIZATION=canonical ordering / dedup / conflict detection
MAPPING_IDENTITY=content sha256 over normalized fields (deterministic)
FAIL_CLOSED_MISSING=MappingUnavailableError
FAIL_CLOSED_CONFLICT=MappingConflictError
CANONICAL_MEMBERSHIP_VALIDATION=MAPPING_CONTRACT_NOT_IN_CANONICAL_UNIVERSE
TERMINAL_ONLY_AUTH_CAPTURE_INTERFACE=TerminalOnlyAuthCapture / TerminalAuthCapture
NO_PSEUDO_MAIN_PRICE_BARS=PseudoMainBarForbidden
NO_PROJECT_AUTHORED_SUBSTITUTE=MappingSubstitutionForbidden
```

Key properties:

- **Record schema** — a source-governed mapping record binds
  `research_symbol`, the vendor `source_symbol` (`KQ.m@` form), the concrete
  canonical target, the effective trading date and the exact switch moment,
  availability (no lookahead), provenance, and the `SOURCE_GOVERNED` derivation
  marker.
- **Provenance** — `MappingProvenance` carries provider/interface identity,
  retrieval session, retrieval timestamp, a source-artifact identity hash when
  exact bytes are bound, and the `exact_bytes_bound` flag. `exact_bytes_bound`
  must be consistent with the hash (fail closed otherwise). The availability
  doc's `DOC_FETCHED_BYTE_SHA256=NOT_RECORDED` limitation is preserved.
- **Effective timestamp/date** — the source-defined next-trading-day switch is
  modelled as `effective_trading_date` plus the tz-aware `effective_at` (which
  must fall on that date). No civil-date guessing is performed.
- **Deterministic normalization** — schedules normalize to a canonical ordering
  and reject duplicate/conflicting records at construction, so identity is
  order-independent and reproducible.
- **Mapping identity** — content `sha256` over the normalized record and
  schedule fields; any semantic change changes the identity.
- **Fail-closed missing/conflict** — PIT resolution raises
  `MappingUnavailableError` when no record applies and `MappingConflictError`
  when the same effective day maps to more than one concrete contract.
- **Canonical-contract membership validation** — every mapped concrete target is
  checked against the canonical concrete-contract universe; a target outside the
  universe produces a `MAPPING_CONTRACT_NOT_IN_CANONICAL_UNIVERSE` fact and is
  never silently substituted.
- **Terminal-only auth capture interface** — a boundary (and a concrete
  terminal-hidden-input implementation) that reads credentials at the terminal
  only, holds them in memory only, never persists/logs/commits them, and fails
  closed on an empty credential or a non-interactive terminal. It performs no
  login.
- **No pseudo-main price bars** — the target must be a concrete contract id; any
  synthesized/main/pseudo symbol (`KQ.m@`, `.main`, 主连) target is rejected.
- **No project-authored mapping substitution** — the only accepted derivation
  marker is `SOURCE_GOVERNED`; OI/volume/calendar/PnL-derived records are
  rejected at construction.

## 5. What was deliberately NOT implemented

```text
TQSDK_DECODE_ADAPTER=NOT_IMPLEMENTED (BLOCKED_API_CONTRACT_NOT_PINNED)
RUNTIME_CONTRACT_MAPPING_SCHEDULE_WIRING=NOT_DONE (future Owner-gated package)
AUTHENTICATED_RETRIEVAL=NOT_PERFORMED (login forbidden)
COMPLETE_MAPPING_JSON=NOT_CREATED (no real mapping obtained)
```

The generic structural `ContractMappingSchedule` in `src/contract_semantics.py`
was **not modified** and remains structural/synthetic machinery, not candidate
mapping authority.

## 6. Verification

Executed on branch `preoutcome/e07-mapping-prep-v01` at baseline
`e87315dd622689eb165dbe81f1728c868cc06a26`.

```text
FULL_TESTS=606_OK (baseline 574 + 32 new E07 prep tests)
NEW_TEST_FILE=tests/test_source_governed_mapping.py
COMPILEALL=OK
DIFF_CHECK=OK (4 new files, 0 modified tracked files)
MAIN_UNTOUCHED=YES
```

Companion JSON (deterministic, reproducible via
`python -m tools.verify_e07_mapping_machinery`):
`docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_PREP_V0_1.json`.

## 7. Artifacts produced by this package

```text
SRC_MODULE=src/source_governed_mapping.py
TEST_MODULE=tests/test_source_governed_mapping.py
VERIFY_TOOL=tools/verify_e07_mapping_machinery.py
EVIDENCE_MD=docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_PREP_V0_1.md
EVIDENCE_JSON=docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_PREP_V0_1.json
```

This package modifies **no** existing `src/*.py`, no authority/state file, and no
frozen protocol. It does not implement any runtime adapter and does not create a
complete mapping artifact. A real source-governed mapping remains an
Owner-gated authenticated TqSdk retrieval whose exact response contract must
first be pinned by evidence.
