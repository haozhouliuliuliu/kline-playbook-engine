# PARALLEL_PACKAGE_C_D_F_ACTUAL_REPAIR_SPEC_V0_1

> Date: 2026-08-20
> Status: ACTIVE / BOUNDED IMPLEMENTATION SPEC
> Parent: `docs/reviews/FULL_PROJECT_SECOND_PASS_REPAIR_PLAN_V0_1.md`
> Preflights: Package C `f76aed58...`, Package D `8ffea447...`, Package F `2bc9ea14...`
> Candidate outcomes: NOT_AUTHORIZED

## 1. Parallel rule

C, D and F may run concurrently in isolated worktrees because Package B is integrated and their principal production ownership is disjoint. Main is the sole integration lane. Each worker must use the latest `origin/main`, must not modify `CURRENT_STATE.md`, and must not merge/push main.

No worker may inspect candidate PnL/return/Sharpe/win-rate/drawdown or access real candidate outcome data.

---

# Package C — Playbook Contract Protocol invariants

Findings: P-01..P-05.

## C-01 / C-02 — claim-level PRIMARY and derived ambiguity

Do not add a large decision framework. Reuse `InterpretationBranch.source_claim_ids` and `primary_selected`.

For machine readiness, derive PRIMARY per source claim:

- every `SourceClaimRef.claim_id` must be referenced by at least one interpretation branch;
- for each source claim, exactly one referencing branch must have `primary_selected=True`;
- zero selected for a claim -> blocker;
- more than one selected for a claim -> blocker;
- one branch may legitimately be the selected PRIMARY for multiple claims when it explicitly references those claims.

Add a deterministic contract-level `primary_selection_identity`: canonical hash of sorted `(claim_id, selected_branch_identity)` pairs. This replaces the old assumption that the whole contract has only one selected branch.

`ambiguity_status` may remain as descriptive/backward-compatible metadata, but it can never waive derived ambiguity. If claim-level PRIMARY derivation is unresolved, readiness must block even when caller sets `NONE`/`RESOLVED`. If caller explicitly sets `UNRESOLVED_CRITICAL`, it also blocks.

Update `ResearchFirewall.derive_primary_branch_identity()` to use the contract's `primary_selection_identity` (the existing field name may remain for compatibility, but its machine meaning becomes the canonical whole-contract PRIMARY selection identity). Do not add a second PRIMARY authority.

## C-03 — PARTIALLY_OBSERVABLE required inputs

A required `ObservationSurface` with `PARTIALLY_OBSERVABLE` must block `MACHINE_READY` in this package. Do not invent a surrogate/subset-resolution object. A future explicitly governed inferred surrogate can be a separate interpretation/contract version.

## C-04 — UNKNOWN transfer

`project_transfer_status=UNKNOWN` must block machine readiness. `INFERRED` remains allowed only as explicitly labeled inferred project transfer; it must never be treated as source-explicit.

## C-05 — timeframe

A machine-ready contract must have exactly one `timeframe_scope` value. Multiple source-permitted timeframes may remain in drafts/variants, but they may not bridge into one `StrategyIdentity.timeframe` comma-joined string.

`bridge_to_strategy_identity()` must fail closed unless the contract is machine-ready and the timeframe scope contains exactly one value; it must use that value verbatim.

## C acceptance tests

At minimum prove:

1. two source claims with PRIMARY only for C1 -> NOT_MACHINE_READY;
2. each claim exactly one PRIMARY -> passes PRIMARY check;
3. duplicate PRIMARY for one claim -> blocker;
4. caller `ambiguity_status=NONE` cannot waive unresolved claim PRIMARY;
5. `UNRESOLVED_CRITICAL` still blocks even when claim primaries are otherwise complete;
6. required PARTIALLY_OBSERVABLE -> blocker;
7. UNKNOWN transfer -> blocker;
8. two timeframes -> blocker and bridge refusal;
9. one timeframe -> bridge uses exact value;
10. Package B outcome registration still derives/compares the new canonical PRIMARY selection identity.

Do not modify frozen Protocol v1.0.

---

# Package D — Canonical completeness / provenance

Findings: D-01..D-08. No canonical corpus rebuild in this package; use synthetic/temp fixtures only.

## D-01 — truncated coverage cannot be PASS

A `ManifestPartition` may still record a partial returned response, but `quality_status == "PASS"` is legal only when:

`returned_start == requested_start` and `returned_end == requested_end`.

If coverage is truncated, quality must be non-PASS/fail-closed. Do not silently stretch returned coverage.

The acquisition/build path must compute a non-PASS quality for truncated coverage rather than constructing an invalid PASS manifest.

## D-02 — expected completeness from session authority, not observed days

Add the smallest SessionMetadata helper needed to enumerate expected bar starts over a declared coverage range directly from authoritative session windows. Normalization must compare observed starts against all expected starts within the claimed coverage, not only `observed_by_day` keys.

This must catch an entirely absent session window when the artifact claims coverage over it. A fully empty raw payload remains invalid and therefore can never PASS.

Do not synthesize bars.

## D-03 — raw artifact identity

`CanonicalRow.raw_artifact_identity_id` must come from `NormalizedHistoricalBar.raw_artifact_identity_id` / `RawArtifact.identity_id`, never `partition.raw_sha256`.

Raw SHA remains a different provenance fact.

## D-04 — missing volume is not zero

Change canonical volume semantics to nullable integer:

- `CanonicalRow.volume: int | None`;
- `None` is valid and preserved into Parquet;
- non-None volume must be non-negative integer;
- canonical schema documentation must explicitly say `int64 nullable`;
- conversion from normalized bars must preserve `None`, never replace it with zero.

Do not claim accepted corpus rows were affected.

## D-05 — SessionMetadata identity binds real authority

Keep construction simple but remove caller-string identity authority.

`SessionMetadata(authority_reference, windows)` must compute its public identity/version deterministically from:

- the supplied authority reference; and
- the exact canonical session windows `(exchange, instrument, trading_day, start, end, kind)`.

`build_session_metadata()` must supply an authority reference that binds at least:

- `TradingCalendar.identity()`;
- `ProductSessionSchedule.identity()`;
- concrete contract;
- the explicit night-closed override if one was supplied.

Thus same caller label + different windows/calendar facts cannot yield the same `SessionMetadata.version`.

Migrate downstream tests/builders to the computed identity. Do not create a metadata registry.

## D-06 — metadata byte provenance

Do not fetch new external material in this package.

Enhance `GovernedSource` minimally so a governed source can bind either one or multiple exact artifact SHA256 values. Exact hashes must be canonical/sorted/unique and included in source identity.

Rules:

- `OFFICIAL_AVAILABLE` / `ARCHIVED_OFFICIAL` may only claim byte-bound status when at least one exact artifact hash is present;
- sources whose exact bytes are not presently recorded must be explicitly `OFFICIAL_PARTIAL` or `PENDING_OFFICIAL_BINDING`, not silently treated as exact-byte-bound;
- loaders should use hashes already present in committed evidence where available (e.g. calendar/universe per-year hashes);
- schedule/spec sources with no historical byte hash stay explicitly partial; do not invent hashes and do not re-download.

The code may change future canonical identities if/when a corpus is rebuilt. This package does not rewrite accepted corpus evidence.

## D-07 — mixed partition write

`write_partition_table()` must reject input rows spanning more than one logical `PARTITION_COLUMNS` tuple before writing any files. Do not scan the entire dataset root to recover inventory.

## D-08 — version mismatch diagnostics

Capture the actual TqSdk runtime version in a local variable and include it in the mismatch error before clearing/resetting adapter state. Regression must assert the real observed wrong version appears in the message.

## D acceptance tests

At minimum reproduce then close D-01..D-08 with synthetic/temp fixtures. Keep PyArrow tests capability-gated. Full default suite must remain green without reading the real canonical corpus.

No canonical corpus rebuild, no acceptance-document rewrite, no claim that existing OHLC prices are wrong.

---

# Package F — Source-evidence hardening

Findings: S-01, S-02, S-04. S-03 reachability is already mitigated by retained evidence refs.

## F-01 — future byte provenance, no retroactive fiction

Historical exact fetched bytes cannot be reconstructed where no historical byte hash was recorded. Do not rewrite old source bundle/session JSON and do not re-fetch old URLs to pretend the newly fetched bytes are what an earlier worker saw.

Add the smallest forward-only material provenance object to the SOURCE_ONLY bundle surface, for example `ApprovedSourceMaterialRef`, with:

- `source_id`;
- `material_id`;
- `source_anchor_reference`;
- explicit byte-binding status;
- optional fetched byte SHA256 and byte size.

Provide two explicit construction modes only:

1. `from_bytes(...)`: computes SHA256/size internally from supplied bytes and marks exact byte binding;
2. `historical_unbound(...)`: records no hash and explicitly marks byte binding `NOT_RECORDED`.

Do not expose a constructor/helper that accepts an arbitrary caller digest while claiming exact byte binding.

`ApprovedSourceBundle` must include the canonical material refs in its identity/hash so future exact-byte-bound material changes change the bundle identity. Historical-unbound materials remain explicitly unbound rather than silently strong.

Do not store copyrighted full bytes in the repository.

## F-02 — source_id / material_id schema semantics

Bring the bounded `ClaimRecordDraft` structural subset into alignment with Claim Schema v1.0:

- add required `material_id`;
- `source_id` remains the actual source identity, not the bundle id;
- `SourceOnlyClaimExtractionContext.record_claim()` must verify the `(source_id, material_id)` pair exists in the approved bundle material refs;
- it must still verify session/bundle binding and source anchors;
- remove the incorrect rule `draft.source_id == source_bundle.source_bundle_id`.

Update synthetic tests and future-facing drivers/helpers. Do not rewrite accepted historical claim artifacts; document their legacy schema mismatch.

## F-04 — verification wording

Do not rewrite historical evidence JSON. Create/update a single canonical clarification document explaining:

- historical `SOURCE_ONLY_VERIFIED=YES` means the project API/session path reported verified under the controls then implemented;
- it is not proof of OS/process isolation;
- it is not retroactive proof that old deterministic verification tokens were unforgeable;
- Package B closed the fixed-nonce API forgery path prospectively;
- protected-market retrieval through the SOURCE_ONLY API remained technically denied; no evidence was found that prior workers accessed candidate outcomes.

Update current code/docstrings only where they still imply cryptographic/process-level guarantees. Do not erase historical wording.

## F acceptance tests

At minimum prove:

1. `from_bytes` same bytes -> same material identity/hash;
2. changed bytes -> changed identity/hash;
3. historical-unbound material has no byte hash and is explicitly `NOT_RECORDED`;
4. no exact-byte construction path accepts a caller-supplied digest;
5. bundle identity changes when exact-byte-bound material changes;
6. ClaimRecordDraft requires material_id;
7. valid `(source_id, material_id)` records;
8. bundle-id-as-source-id no longer passes unless it is truly an approved source_id;
9. unknown material pair fails closed;
10. SOURCE_ONLY protected-outcome request remains DENIED;
11. Package B `is_verified()` behavior remains green.

No external refetch, no candidate outcome data, no historical artifact rewriting.

---

## Integration

C/D/F workers push isolated branches only. Project brain reviews each diff and runs a post-parallel cross-package audit before any branch reaches main. If two packages unexpectedly touch the same production authority, stop and report rather than inventing conflict resolution.