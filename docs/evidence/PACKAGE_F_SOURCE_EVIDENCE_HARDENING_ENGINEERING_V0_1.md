# PACKAGE F — SOURCE EVIDENCE HARDENING — ENGINEERING EVIDENCE V0_1

Authoritative spec: `docs/reviews/PARALLEL_PACKAGE_C_D_F_ACTUAL_REPAIR_SPEC_V0_1.md`
Findings repaired: **S-01, S-02, S-04** (S-03 reachability already mitigated by
retained evidence refs)
Preflight: `prep/package-f-source-evidence-preflight-v01` @ `2bc9ea14...`
(S-01 / S-02 / S-04 reproduced)

## 1. Scope

One isolated branch, one coherent Package F commit series on
`repair/package-f-source-evidence-hardening-v01`, based on `origin/main`
(`e8ccab1`). Package F hardens the SOURCE_ONLY **source-evidence surface** in
`src/research_firewall.py` and its synthetic tests / future-facing tool drivers.

It does **not** touch Playbook Contract, canonical data, execution, historical
extraction JSON, frozen protocols, or `CURRENT_STATE.md`. No external source was
re-fetched, no OCR was performed, no full copyrighted source was stored, and no
candidate outcome data was viewed or used.

## 2. S-01 — forward-only byte provenance, no retroactive fiction

### Root cause (reproduced in preflight)

None of the accepted historical source bundles bind fetched bytes: canonical
bundle hashes are computed from recorded metadata (bundle id, retrieval mode,
material metadata, selection criteria), and the only per-material hash is the
worker-authored `content_note_hash` (a paraphrase, not fetched bytes). No
fetched-byte SHA256 exists anywhere in the accepted evidence. Therefore
`HISTORICAL_EXACT_BYTES_PROVABLE=NO`.

Re-downloading old URLs and hashing them now would only prove what bytes exist
today, not what an earlier worker saw. This package does **not** do that.

### Repair — forward-only material provenance

- Added `ByteBindingStatus` (exactly two states: `EXACT_BYTES_BOUND`,
  `NOT_RECORDED`; no complex enum hierarchy).
- Added `ApprovedSourceMaterialRef` — an immutable, forward-only source material
  provenance object with `source_id`, `material_id`, `source_anchor_reference`,
  `byte_binding_status`, `fetched_content_sha256`, `fetched_byte_size`.
- `ApprovedSourceMaterialRef.from_bytes(...)` computes `sha256(content)` and
  `len(content)` **internally** from the supplied bytes and marks
  `EXACT_BYTES_BOUND`. Direct construction is closed (raises `TypeError`), so a
  caller cannot fabricate an exact ref from an arbitrary digest/size. This
  deliberately avoids the Package B `ArtifactBinding._build` caller-digest
  defect.
- `ApprovedSourceMaterialRef.historical_unbound(...)` records no hash/size and
  explicitly marks `NOT_RECORDED` — the legitimate representation of historical
  material whose exact fetched bytes were never recorded.

### Repair — bundle knows its approved materials

- `ApprovedSourceBundle` gained `materials: tuple[ApprovedSourceMaterialRef,...]`
  (canonical sorted/unique by `(source_id, material_id)`).
- `bundle_identity` binds the canonical material refs (their identities/hashes),
  so changing an exact-byte-bound material's bytes changes the material identity
  and therefore the bundle identity.
- `ApprovedSourceBundle.legacy_unbound(...)` is the explicit legacy/unbound
  construction path: the recorded bundle reference/hash is preserved as a
  historical value, while every material ref stays `NOT_RECORDED`. A recorded
  historical hash can never upgrade materials to `EXACT_BYTES_BOUND`.
- `byte_binding_status` on the bundle is derived: `EXACT_BYTES_BOUND` only when
  every approved material ref is exact; otherwise `NOT_RECORDED`.

## 3. S-02 — source_id / material_id schema semantics

### Root cause (reproduced in preflight)

`ClaimRecordDraft` had no `material_id`; `SourceOnlyClaimExtractionContext.record_claim()`
required `draft.source_id == source_bundle.source_bundle_id` — conflating the
source bundle id with the Claim Schema v1.0 `source_id`. The Claim Schema
requires both `source_id` and `material_id` as distinct fields.

### Repair

- `ClaimRecordDraft` gained required `material_id` (Claim Schema v1.0 structural
  subset).
- `record_claim()` now verifies the `(source_id, material_id)` pair exists in the
  approved bundle's material refs via `ApprovedSourceBundle.approved_material(...)`.
  `source_id` is the actual source identity, never a bundle-id alias. The old
  rule `draft.source_id == source_bundle.source_bundle_id` is removed.
- `record_claim()` still verifies session/bundle binding (`runner.verified`) and
  session binding, and now also verifies the source anchor (below). SOURCE_ONLY
  protection is preserved.

### Source anchor association

`record_claim()` no longer checks only the source/material pair. `draft.source_anchor`
must be legitimately associated with the approved material's `source_anchor_reference`:
exact equality, or a strictly structural descendant anchor (`material_anchor + ":"`
prefix). No URL parser and no fuzzy matcher were added.

### Drivers/helpers updated

- Synthetic fixtures (`tests/synthetic_fixture.py`) gained a distinct synthetic
  source identity and approved material refs/bundle helpers.
- The NR7 and Holy Grail source-only semantic-completion tools now build the
  bundle via `legacy_unbound` (material refs `NOT_RECORDED`, `source_id=SRC-RASCHKE`,
  anchor = material id) and record claims with `material_id` from the claim
  dict. Historical extraction JSON is not rewritten; the tools were verified
  in-process without writing artifacts.

## 4. S-04 — verification wording clarification

The historical `SOURCE_ONLY_VERIFIED=YES` is a record that the then-current
project API/session mechanism reported verified. It is not proof of OS/process
isolation, not proof that a worker had no shell/file access, and not proof that
old deterministic verification tokens were cryptographically unforgeable.
Package B closed the fixed-nonce forge path prospectively. The SOURCE_ONLY
protected-market outcome API remained technically denied at all times, and no
evidence was found that any prior worker accessed candidate outcomes.

Canonical clarification: `docs/evidence/SOURCE_ONLY_VERIFICATION_SEMANTICS_CLARIFICATION_2026-08-20.md`.

Current code/docstrings are updated only where they still presented API-level
verification as a stronger guarantee (`SourceOnlyPolicy` docstring and the
issued-verified registry comment in `src/research_firewall.py`). No historical
wording was erased and no historical JSON was modified.

## 5. Focused acceptance tests (F01..F13)

`tests/test_source_evidence_hardening.py` (23 tests including FC01/F-C02/F-C03
regressions) plus the updated
`tests/test_research_firewall.py` runner tests:

- F01 `from_bytes` same bytes → same material identity.
- F02 changed bytes → changed material identity.
- F03 `historical_unbound` → `sha256=None`, `byte_size=None`,
  `byte_binding_status=NOT_RECORDED`.
- F04 no exact-byte construction path accepts a caller-supplied digest.
- F05 exact material bytes change → bundle identity changes; legacy-unbound
  bundle stays explicitly `NOT_RECORDED` with the recorded hash preserved.
- F06 `ClaimRecordDraft` missing `material_id` fails.
- F07 approved `(source_id, material_id)` pair records successfully.
- F08 bundle-id-as-source-id fails unless the bundle id is truly also an
  approved source id.
- F09 unknown material pair fails closed.
- F10 anchor mismatch fails; structural descendant anchor accepted.
- F11 protected market-outcome request remains `DENIED` /
  `SOURCE_ONLY_TECHNICAL_DENIAL`.
- F12 Package B `open_verified_session` / `is_verified` stay green.
- F13 manual `record_session` still cannot self-verify.

## 6. Validation

- Focused: `python -m unittest tests.test_source_evidence_hardening tests.test_research_firewall -v` — green.
- Full suite: `python -m unittest discover -s tests -v` — green (see commit note).
- `git diff --check` — clean.
- Tool dry-run (in-process, no artifact writes): NR7 (5 material refs, 23
  claims, denial `DENIED`) and Holy Grail (5 material refs, 27 claims, denial
  `DENIED`) both record through the hardened `record_claim` path.

## 7. Non-changes

```text
HISTORICAL_ARTIFACT_REWRITTEN=NO
EXTERNAL_SOURCE_REFETCHED=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CURRENT_STATE_CHANGED=NO
PLAYBOOK_CONTRACT_CHANGED=NO
CANONICAL_DATA_CHANGED=NO
EXECUTION_CHANGED=NO
```

## 8. Pre-integration correction (F-C01 / F-C02 / F-C03)

Authoritative review: `docs/reviews/PARALLEL_PACKAGE_C_D_F_PREINTEGRATION_REVIEW_V0_1.md`
(baseline `40f27b24...` merged into this branch; one new correction commit, no
amend of the original Package F commit).

### F-C01 — SOURCE_ONLY sessions bind material-derived bundle identity/hash

`ApprovedSourceBundle` now exposes deterministic material-derived session
binding facts:

- `session_binding_identity` — equal to the material-bound `bundle_identity`;
- `session_binding_hash` — derived from `bundle_identity` + `byte_binding_status`.

`bundle_identity` now also binds the recorded historical `source_bundle_hash`, so
the same bundle id + materials with a different recorded hash is a different
bundle evidence identity.

`SourceOnlyClaimExtractionContext.verified` now compares the session against
`session_binding_identity` / `session_binding_hash` (not the legacy bundle id /
caller-supplied recorded hash). Therefore changing exact source bytes changes
both session binding identity and hash, invalidating a previously verified
SOURCE_ONLY session context (FC01-A/B/C regressions).

`source_bundle_id` / `source_bundle_hash` are retained as historical recorded
values (`historical_recorded_bundle_hash`), never upgraded to byte proof.
Historical-unbound legacy bundles remain `NOT_RECORDED` and still have
deterministic session binding facts for future re-runs.

All future `open_verified_session` call sites (synthetic fixtures, NR7 and Holy
Grail tools, Package B helpers) now bind `source_bundle_identity` /
`source_bundle_hash` to the material-derived session binding identity/hash.
Committed historical session JSON is unchanged.

### F-C02 — future session binding hash is not caller-controlled

`session_binding_identity` / `session_binding_hash` are read-only derived
properties, not constructor fields. There is no `session_binding_hash=`,
`bundle_binding_hash=`, or `material_digest=` caller path. Exact binding still
originates only from `ApprovedSourceMaterialRef.from_bytes()` and is derived
upward. An `inspect.signature` regression proves this (FC02).

### F-C03 — ClaimRecordDraft claim_status conforms to Claim Schema v1.0

`ClaimRecordDraft.claim_status` is now restricted to `EXPLICIT | INFERRED |
UNKNOWN` (authority: `src/playbook_contract.ClaimStatus`). Values such as
`READY`, `explicit`, `NOT_APPLICABLE` fail closed (FC03 regressions).
