# Source and Scope Owner Approval (canonical research dataset)

OWNER_APPROVAL=YES
OWNER_SOURCE_APPROVAL=TQSDK
TQSDK_STATUS=ADOPTED
TQSDK_ADOPTION_SCOPE=historical concrete-contract 1-minute research data only
TQSDK_VERIFIED_RUNTIME=3.10.1

OWNER_DATASET_SCOPE_APPROVAL=BALANCED

PAID_CONTINUITY_AUTHORIZED=NO
PAID_CONTINUITY_OWNER_GATE=REQUIRED_IF_NEEDED_LATER

CANONICAL_DATASET_BUILT=NO
CANONICAL_DATASET_ACCEPTED=NO
STRATEGY_RESEARCH_STARTED=NO

Recorded: `2026-08-16`
Branch: `main`
Authority: Owner decision (final for this package), recorded durably here so it
does not live only in chat. See also
`docs/evidence/CANONICAL_DATASET_SOURCE_AND_SCOPE_READINESS.md` (technical
dossier) and `CURRENT_STATE.md` / `TOOL_REGISTRY.md`.

## 1. Owner decision (final, no further Owner re-ask in this package)

- **SOURCE**: Approve TqSdk as the canonical minute-data source for the
  research dataset (`OWNER_SOURCE_APPROVAL=TQSDK`).
- **SCOPE**: Approve the **BALANCED** engineering/research-foundation scale
  (`OWNER_DATASET_SCOPE_APPROVAL=BALANCED`).
- **PAID CONTINUITY**: NOT authorized now (`PAID_CONTINUITY_AUTHORIZED=NO`).
  If it later becomes actually required, it is an Owner gate
  (`PAID_CONTINUITY_OWNER_GATE=REQUIRED_IF_NEEDED_LATER`). Nothing was
  purchased, upgraded, recharged, or renewed.

## 2. Adoption scope and explicit non-authorizations

`TQSDK_ADOPTION_SCOPE=historical concrete-contract 1-minute research data only`

Adoption is **narrow and scoped**. It authorizes:

- acquisition of historical, concrete-contract, 1-minute research bar data via
  the verified TqSdk runtime (`3.10.1`) for the approved canonical corpus;

It **does NOT authorize**:

- broker connectivity or any broker API;
- live or Shadow automated trading;
- order submission of any kind;
- any paid renewal, subscription, recharge, or purchase of TqSdk or any other
  service;
- the use of pseudo MAIN/CONTINUOUS symbols (concrete contracts only);
- any strategy research, optimization, or evaluation (unchanged NOT_AUTHORIZED
  boundaries remain in force).

## 3. Runtime identity freeze

- The currently verified TqSdk runtime compatibility identity is
  **`3.10.1`** (`TQSDK_VERIFIED_RUNTIME=3.10.1`).
- `TqSdkSourceAdapter` is runtime-version bound: it declares
  `verified_runtime_version="3.10.1"` and fails closed on a different imported
  runtime version (never retried, never silently continued under the
  `tqsdk-3.10.1...` source/normalizer identity).
- A different runtime version requires fresh re-verification and a new source
  identity; it is not silently assumed compatible.

## 4. Source identity binding (as implemented)

The adopted source identity for normalized data is produced by
`TqSdkSourceAdapter.source_specification`:

- provider: `TQSDK`
- source_type: `PROFESSIONAL_HISTORICAL_API`
- endpoint_identity: `TqApi.get_kline_data_series`
- raw_schema_identity: `tqsdk-kline-records-json-v1`
- normalizer adapter: `tqsdk-3.10.1-fixed-bar-adapter-v1`
- normalized schema: `completed-historical-bar-v1`
- availability rule: `bar-start-plus-duration-v1`

SHFE official annual/statistical raw remains a `VERIFIED` daily cross-check
reference only; it is not the canonical minute source and is not adopted as a
canonical dataset source.

## 5. Status

- `FOUNDATION_MERGED=PASS` (main fast-forwarded to the accepted readiness HEAD
  `238c230207250b3a02cd22dea658898a9a982e53` in this package, then pushed).
- The canonical research dataset is **NOT yet built** and **NOT yet accepted**
  (`CANONICAL_DATASET_BUILT=NO`). This document records the Owner source/scope
  decision only.
- Next governed step: build the BALANCED corpus on the dedicated
  `ds/canonical-dataset-build` branch, then accept it as evidence.
