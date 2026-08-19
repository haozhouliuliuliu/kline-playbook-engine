# PACKAGE_F_SOURCE_EVIDENCE_HARDENING_PREFLIGHT_V0_1

> Date: 2026-08-20
> Task: `PACKAGE_F_PREFLIGHT_SOURCE_EVIDENCE_HARDENING_AUDIT_V0_1`
> Type: **PREFLIGHT AUDIT ONLY** — this is the precise repair map for a future
>   Package F repair. No production code, historical extraction artifact, or
>   integration-review wording was changed by this task.
> Findings authority: `docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md`
>   — S-01, S-02, S-04
> Repair plan authority: `docs/reviews/FULL_PROJECT_SECOND_PASS_REPAIR_PLAN_V0_1.md`
>   — Package F targets S-01, S-02, S-04 (S-03 handled by R-PB-01 durable refs)
> Canonical repo: `haozhouliuliuliu/kline-playbook-engine`
> Baseline: `c13ec0412986234616d648983897ce3015df2671` (origin/main)
> Branch: `prep/package-f-source-evidence-preflight-v01`

## 0. Bottom line

```text
S01=REPRODUCED
S02=REPRODUCED
S04=REPRODUCED
HISTORICAL_SOURCE_BYTES_RETROACTIVELY_PROVABLE=NO
HISTORICAL_VERIFICATION_OVERCLAIM_CORRECTABLE_BY_WORDING=YES
PRODUCTION_FIX_PERFORMED=NO
HISTORICAL_ARTIFACT_REWRITTEN=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

- **S-01**: every accepted source bundle (Wave 1 Grimes, Wave 2 Steenbarger,
  Raschke screen, Raschke Holy Grail, Raschke NR7) binds **metadata only**.
  The `canonical_bundle_hash` recomputes exactly from
  `bundle_id + retrieval_mode + materials[material_id,url,canonical_title,date|publication_date] + selection_criteria`.
  No bundle records a fetched-HTML/PDF byte SHA256. Therefore the exact bytes
  seen by any historical extraction session are **not** retroactively provable.
  `HISTORICAL_EXACT_BYTES_PROVABLE=NO` is the correct answer for all bundles.
- **S-02**: the bounded SOURCE_ONLY output requires
  `draft.source_id == source_bundle.source_bundle_id` (schema-mismatch chain is
  reproduced exactly below). The richer extraction separately records
  `material_id` outside the structural output surface.
- **S-04**: `SOURCE_ONLY_VERIFIED=YES` / "project-issued verified" wording is
  inventoried per document and classified A / B below. The overclaim is
  correctable by prospective wording qualification; the historical fact that
  verification was a deterministic, source-reconstructable API token (F-10) is
  not retroactively upgradeable.

## 1. Scope performed / not performed

Performed (read-only):

- Read `CURRENT_STATE.md`, the second-pass adversarial audit, and the second-pass
  repair plan (Package F ordering).
- Read accepted evidence refs `evidence/wave1-accepted-raw-20260819`
  (`b68da256bbc493ac6e1de0fe02b7fde5a0396ddf`) and
  `evidence/wave2-accepted-raw-20260819`
  (`c0fef50bb3b0f5a97c7bdf472d5a9e2d9339273a`).
- Read the formal Holy Grail / NR7 source-bundle, session, and semantic-completion
  artifacts on main, and the accepted Raschke screen artifacts.
- Read `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`,
  `src/research_firewall.py`, and the real Wave 1 / Wave 2 / screen / Holy Grail
  / NR7 extraction drivers.
- Recomputed every `canonical_bundle_hash` from metadata-only fields and confirmed
  exact match (see `tools/audit_package_f_source_evidence.py`).
- Inventoried every `SOURCE_ONLY_VERIFIED` / "project-issued" / "unforgeable" /
  "technically verified" wording in the official review/evidence corpus.

Not performed (frozen boundaries, do not violate):

- No `src/` production code change.
- No historical bundle/session JSON rewrite, no re-generated hash.
- No source re-fetch, no download, no OCR, no attempt to reconstruct historical
  byte hashes.
- No integration-review modification and no deletion of `SOURCE_ONLY_VERIFIED`
  wording.
- No research-protocol change and no candidate-outcome data access.

## 2. S-01 — source bundle exact byte binding (exact inventory)

### 2.1 Which fields actually compose each bundle identity

All five accepted bundles use the identical canonical scheme (canonical JSON,
`sort_keys`, `ensure_ascii=False`, sha256) over **metadata only**:

```text
canonical_bundle_hash = sha256( canonical_json({
    "bundle_id": ...,
    "retrieval_mode": ...,
    "materials": [ { "material_id", "url", "canonical_title", "date"|"publication_date" } ... ],
    "selection_criteria": [ ... ],
}))
```

Verified by recomputation (all `MATCH`):

| BUNDLE | BUNDLE_ID | HASH |
|---|---|---|
| Wave 1 Grimes | `SB-W1-PUBLIC-GRIMES-V1` | `e9c60ca1169ff4cb23f2d599e4b74ebf49d6ce04942045b49f271de7eba52170` |
| Wave 2 Steenbarger | `SB-W2-PUBLIC-STEENBARGER-V1` | `39b46e341d05c212597c5703590ac71443dc9dc9eeca1de15cefc88b7a9db30b` |
| Raschke screen | `SB-RASCHKE-PUBLIC-SCREEN-V1` | `7b11a8f1516696e2e54f9dc0ee4d7785f8f1cd9dad06d52abe15378edd2633bd` |
| Raschke Holy Grail | `SB-RASCHKE-HOLY-GRAIL-SEMANTIC-V1` | `7e6cd5cf02eefa7ba7483eeda9a036433e5a07320455c0594971fc2e37bf882c` |
| Raschke NR7 | `SB-RASCHKE-NR7-SEMANTIC-V1` | `6304a630430871cdfd197ea38a2a22556d7854bff05fd5a7fad20a934bd06f11` |

The only other hash field present in any manifest is the per-material
`content_note_hash`, which is the sha256 of a **worker-authored** `content_note`
paraphrase (not of fetched bytes) and is **not** part of the canonical bundle
hash. The Holy Grail / NR7 manifests additionally carry a
`base_bundle_reference.base_bundle_hash` pointing at the accepted screen bundle.

Raw-retention boundaries confirm no bytes were retained:

- Wave 1 manifest: `raw_material_retention_boundary = "Raw HTML of the source
  pages was not retained. Only attributable short excerpts and concise
  paraphrases ... are recorded."`
- Holy Grail manifest `access_state.note`: PDFs "re-verified via direct HTTP
  fetch on 2026-08-20 (HTTP 200, application/pdf) ... Raw content was not
  committed." This is a URL-reachability re-check, **not** a byte hash of what
  an earlier session saw.
- `tools/acquire_raschke_official_articles.py` records only `bytes = len(resp.content)`
  (a length), `content_type`, `http_status`, `pdf_pages`, `extracted_chars`,
  `detected_years`; it writes raw PDFs to a temp dir **outside** the repository
  and computes no SHA256 of fetched bytes.

### 2.2 S-01 table

```text
BUNDLE                  BUNDLE_IDENTITY_INPUTS                                             URL_BOUND  CONTENT_NOTE_BOUND                  FETCHED_BYTE_SHA_BOUND  HISTORICAL_EXACT_BYTES_PROVABLE
Wave 1 Grimes           bundle_id,retrieval_mode,materials[material_id,url,title,date],      YES        NO (worker-authored note only;      NO                      NO
                        selection_criteria                                                  (url in   separate content_note_hash, not
                                                                                             hash)     in canonical_bundle_hash)
Wave 2 Steenbarger     bundle_id,retrieval_mode,materials[material_id,url,title,date],      YES        NO (same)                           NO                      NO
                        selection_criteria
Raschke screen         bundle_id,retrieval_mode,materials[material_id,url,title,             YES        NO (same)                           NO                      NO
                        publication_date],selection_criteria
Raschke Holy Grail     bundle_id,retrieval_mode,materials[material_id,url,title,             YES        NO (same)                           NO                      NO
                        publication_date],selection_criteria
                        + base_bundle_reference (screen hash)
Raschke NR7            bundle_id,retrieval_mode,materials[material_id,url,title,             YES        NO (same)                           NO                      NO
                        publication_date],selection_criteria
                        + base_bundle_reference (screen hash)
```

Consequences:

- A source can change at the same URL without changing the bundle identity.
- The bundle identity proves only the *worker-declared metadata* (URL, title,
  date, selection) and the worker-authored content note — not the bytes of the
  page/PDF the extraction session actually read.
- No historical exact byte SHA exists anywhere in the accepted artifacts, so
  `HISTORICAL_SOURCE_BYTES_RETROACTIVELY_PROVABLE=NO`. This is the correct
  answer, not a defect in this audit. Future hardening can bind byte hashes only
  for newly / re-fetched material and must not be presented as proof of bytes
  seen in an earlier session.

### 2.3 Evidence file map for S-01

| Artifact | Location |
|---|---|
| Wave 1 manifest + session | `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_1_MANIFEST.json`, `HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1.json` — ref `evidence/wave1-accepted-raw-20260819` |
| Wave 2 manifest + session | `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_WAVE_2_STEENBARGER_MANIFEST.json`, `HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_2_STEENBARGER.json` — ref `evidence/wave2-accepted-raw-20260819` |
| Raschke screen bundle | `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_SCREEN_V0_1.json` — branch `parallel/raschke-public-current-data-screen-v01` |
| Holy Grail bundle + session | `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json`, `HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json` — main |
| NR7 bundle + session | `docs/evidence/HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_NR7_SEMANTIC_V0_1.json`, `HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json` — main |

## 3. S-02 — `ClaimRecordDraft.source_id` schema mismatch (exact chain)

### 3.1 Canonical schema semantics

`docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md` §3 (Required claim
record) lists **both** `source_id` and `material_id` as distinct required fields,
and §4 requires the session to carry a "source-bundle identity/hash". The schema
therefore distinguishes:

- `source_id` — the source the claim came from (identifiable at claim level);
- `material_id` — the specific material within that source (e.g. `SB-W1-M1`).

### 3.2 What the bounded output actually enforces

`src/research_firewall.py`:

- `ClaimRecordDraft` (dataclass) fields: `claim_id`, `source_id`, `source_anchor`,
  `claim_status`, `source_excerpt_short_or_paraphrase`, `source_only_session_id`,
  `created_at` — **no `material_id` field** ("minimal ... Claim Schema v1.0
  structural subset").
- `SourceOnlyClaimExtractionContext.record_claim()`:

  ```python
  if draft.source_id != self._source_bundle.source_bundle_id:
      raise ValueError("claim record is bound to a different source bundle")
  ```

Real Wave 1 driver `tools/run_claim_extraction_wave1_source_only.py`:

```python
runner.record_claim(
    ClaimRecordDraft(
        claim_id=claim["claim_id"],
        source_id=bundle.source_bundle_id,   # bundle id, not material id
        ...
    )
)
```

The Wave 2 driver (`..._wave2_steenbarger_source_only.py`) and the Raschke
screen / Holy Grail / NR7 drivers use the same pattern (`source_id=BUNDLE_ID`).

The richer `CLAIMS` dictionaries in the same drivers separately carry a
`material_id` per claim (e.g. `SB-W1-M1`), and the durable session JSON embeds
that richer dict under `"claims"` — so `material_id` survives only **outside** the
bounded `ClaimRecordDraft` structural surface. The bounded surface's
`recorded_claim_ids` records only claim ids.

### 3.3 Chain (exact file / function / field)

```text
1. docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md §3
   -> source_id AND material_id are distinct required claim fields.
2. src/research_firewall.py
   -> ClaimRecordDraft.source_id (line ~278); no material_id field.
3. src/research_firewall.py
   -> SourceOnlyClaimExtractionContext.record_claim()
      requires draft.source_id == self._source_bundle.source_bundle_id
      (line ~371; ValueError otherwise).
4. tools/run_claim_extraction_wave1_source_only.py
   -> runner.record_claim(ClaimRecordDraft(source_id=bundle.source_bundle_id, ...))
      i.e. draft.source_id = "SB-W1-PUBLIC-GRIMES-V1" (bundle id).
   -> richer CLAIMS dict carries material_id="SB-W1-M1" separately.
5. docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_WAVE_1.json
   -> "claims" = richer dict with material_id; recorded_claim_ids from bounded
      ClaimRecordDraft records (no material_id).
6. tests/test_research_firewall.py (lines ~1166, ~1200)
   -> source_id=bundle.source_bundle_id; test suite enshrines the conflation.
```

Verdict: `S02=REPRODUCED`. The supposed structural SOURCE_ONLY output does not
faithfully enforce the canonical claim-schema meaning of `source_id` — it conflates
`source_id` with `source_bundle_id` while the richer extraction keeps `material_id`
out-of-band. **Schema is not changed by this preflight.**

## 4. S-04 — historical `SOURCE_ONLY_VERIFIED` wording inventory

Classification definitions:

- **A (accurate)** — wording is mechanism-descriptive: the session passed the
  project SOURCE_ONLY `open_verified_session` path and the protected-outcome
  retrieval API denied. This remains true (the denial path is real and verified).
- **B (overclaim)** — wording reads as if the project-issued token proves
  absolute unforgeability / worker-environment isolation. Under F-10 the
  verification token is deterministic and reconstructable from public source
  code, so B is too strong.

### 4.1 Wave 1 review — `docs/reviews/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_1_INTEGRATION_REVIEW_V0_1.md`

| Loc | Wording | Class |
|---|---|---|
| §1 verdict (line 20) | `SOURCE_ONLY_VERIFIED=YES` | B (unqualified project-level flag) |
| §4 (line 78) | `SOURCE_ONLY_IS_VERIFIED=YES`, `PROTECTED_MARKET_ACCESS_MODE=TECHNICALLY_DENIED`, `DENIAL_TEST_OUTCOME=DENIED` | A (mechanism) |
| §4 narrative | "The worker used the project-owned implementation in `src/research_firewall.py`"; "session evidence discloses the residual latent-model-knowledge risk and exposes no project protected-period market-outcome retrieval surface" | A |

### 4.2 Wave 2 review — `docs/reviews/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_2_INTEGRATION_REVIEW_V0_1.md`

| Loc | Wording | Class |
|---|---|---|
| §1 verdict (line 19) | `SOURCE_ONLY_VERIFIED=YES` | B (unqualified project-level flag) |
| §4 (line 79) | `SOURCE_ONLY_IS_VERIFIED=YES`, `PROTECTED_MARKET_ACCESS_MODE=TECHNICALLY_DENIED`, `DENIAL_TEST_OUTCOME=DENIED` | A (mechanism) |

### 4.3 Steenbarger semantic completion review — `docs/reviews/STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_SEMANTIC_COMPLETION_INTEGRATION_REVIEW_V0_1.md`

| Loc | Wording | Class |
|---|---|---|
| §1 verdict (line 20) | `SOURCE_ONLY_VERIFIED=YES` | B (unqualified project-level flag) |
| body | mechanism-descriptive denial / bounded-context text | A |

### 4.4 Raschke screen review — `docs/reviews/HUMAN_PLAYBOOK_RASCHKE_FREE_PUBLIC_CURRENT_DATA_SCREEN_INTEGRATION_REVIEW_V0_1.md`

| Loc | Wording | Class |
|---|---|---|
| §1 verdict (line 21) | `SOURCE_ONLY_VERIFIED=YES`, `PROTECTED_OUTCOME_DENIAL=PASS` | B flag / A denial |
| project-brain decision (line 64) | `SOURCE_ONLY_VERIFIED=YES` | B (unqualified project-level flag) |

### 4.5 Raschke NR7 semantic completion — `docs/research/semantic_completion/RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_SEMANTIC_COMPLETION_V0_1.md`

| Loc | Wording | Class |
|---|---|---|
| §1 verdict (line 43) | `SOURCE_ONLY_VERIFIED=YES` | B (unqualified project-level flag) |
| §13 (line 609) | "A new **project-issued verified** SOURCE_ONLY session was created using the actual project implementation" | B (overclaim phrasing) |
| §13 (line 622) | `SOURCE_ONLY_IS_VERIFIED=YES`, `PROTECTED_MARKET_ACCESS_MODE=TECHNICALLY_DENIED`, `DENIAL_TEST_OUTCOME=DENIED` | A (mechanism) |
| §13 exposure note | latent-model-knowledge not provable absent; protected windows technically unavailable; any request DENIED+audited | A |
| §14+ (line 691) | `SOURCE_ONLY_VERIFIED=YES` | B (unqualified project-level flag) |

### 4.6 Raschke Holy Grail semantic completion — `docs/research/semantic_completion/RASCHKE_HOLY_GRAIL_SEMANTIC_COMPLETION_V0_1.md`

| Loc | Wording | Class |
|---|---|---|
| §1 verdict (line 44) | `SOURCE_ONLY_VERIFIED=YES` | B (unqualified project-level flag) |
| §13 (line 609) | "A new **project-issued verified** SOURCE_ONLY session was created using the actual project implementation" | B (overclaim phrasing) |
| §13 (line 622) | `SOURCE_ONLY_IS_VERIFIED=YES`, `PROTECTED_MARKET_ACCESS_MODE=TECHNICALLY_DENIED`, `DENIAL_TEST_OUTCOME=DENIED` | A (mechanism) |
| §13 exposure note | latent-model-knowledge not provable absent; protected windows technically unavailable; any request DENIED+audited | A |
| §14+ (line 703) | `SOURCE_ONLY_VERIFIED=YES` | B (unqualified project-level flag) |

### 4.7 Worker artifacts (retained on the evidence refs)

| Loc | Wording | Class |
|---|---|---|
| Wave 1 worker doc (`.../HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_1_V0_1.md`, line 91) | "`is_verified == True` (project-issued verification evidence)" | B (overclaim phrasing) |
| Wave 2 worker doc (`.../HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_2_STEENBARGER_V0_1.md`, line 142) | "`is_verified == True` (project-issued verification evidence)" | B (overclaim phrasing) |

### 4.8 Firewall implementation / acceptance docs (project's own controls)

| Loc | Wording | Class |
|---|---|---|
| `HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md` §5.1 (lines 111, 117) | "Verification is **project-issued**: only `SourceOnlyPolicy.open_verified_session()` stamps ... forged evidence ... rejected" | B (overclaim phrasing) — **but explicitly self-qualified** |
| same doc (lines 324-325) | "... it is a technical-deny-verification mechanism, **not a claim of cryptographic unforgeability**" | A (explicit qualifier) |
| `HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_ACCEPTANCE_REVIEW_V1_1.md` (line 12) | "project-issued SOURCE_ONLY verification" listed as resolved gap | B phrasing, qualified by line 66 |
| same doc (line 66) | "This review does not require cryptographic attestation or sandboxing beyond the project-owned execution boundary" | A |
| `HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md` (line 52) | "SOURCE_ONLY verification is a project-owned application control, **not a cryptographic sandbox** and not a claim that model latent historical knowledge is absent" | A (explicit qualifier) |

### 4.9 Summary and correctability

- The A-class mechanism facts (verified SOURCE_ONLY path + protected-outcome API
  denied) remain accurate today.
- The B-class overclaim is the unqualified `SOURCE_ONLY_VERIFIED=YES` project-level
  flag and the "project-issued verified" phrasing, which under F-10 overstate what
  the deterministic API token proves.
- `HISTORICAL_VERIFICATION_OVERCLAIM_CORRECTABLE_BY_WORDING=YES`: the repair can add
  a standing qualifier — e.g. `SOURCE_ONLY_VERIFIED=YES` means "passed the
  project-owned SOURCE_ONLY technical-denial verification path; deterministic and
  source-reconstructable per F-10; not a cryptographic unforgeability attestation
  and not proof of absolute worker-environment isolation". It must **not** delete
  the wording or rewrite historical review text.
- Even after a future F-10 fix, historical records cannot be made to say the past
  was unforgeable. `HISTORICAL_ARTIFACT_REWRITTEN=NO`.
- Package B's worker branch addresses the API fixed-nonce forge defect but is not
  yet integrated to main; this preflight does **not** rely on it being merged.

## 5. Forward-looking Package F repair map (NOT executed here)

1. **S-01 (future repair)**: record fetched-content byte SHA256 for newly /
   re-fetched source material as an additional identity input (e.g. per-material
   `fetched_byte_sha256` + include in bundle identity), while keeping the raw
   bytes outside the repo (copyright boundary). Do not backfill or claim
   historical byte proof. Package F should define when "fetched" is authoritative
   (extraction-time fetch, pinned bytes) and keep `content_note_hash` semantics
   separate from fetched-byte binding.
2. **S-02 (future repair)**: make `ClaimRecordDraft` / `record_claim` carry the
   canonical schema `material_id` (and distinguish it from `source_id`/bundle id);
   do not require `draft.source_id == bundle_id` when a distinct material is
   intended. Add a regression test asserting schema fidelity. Do not change the
   frozen schema; change the implementation to conform to it.
3. **S-04 (future repair)**: add a standing wording qualifier in integration
   reviews / acceptance docs (as in §4.9). Optionally re-run the firewall docs
   consistency pass once F-10 is fixed, keeping the historical-timeline wording
   honest.

## 6. Verification performed

- `python -m tools.audit_package_f_source_evidence` — all five accepted bundles:
  `META_ONLY_MATCH=MATCH`, `BYTE_SHA=NO` (reproducible S-01 inventory).
- Full canonical suite: `python -m unittest discover -s tests -v`.
- `git diff --check`.
- No candidate-outcome data accessed; no source re-fetch; no historical artifact
  rewrite.

## 7. Conclusion flags

```text
HISTORICAL_SOURCE_BYTES_RETROACTIVELY_PROVABLE=NO
HISTORICAL_VERIFICATION_OVERCLAIM_CORRECTABLE_BY_WORDING=YES
PRODUCTION_FIX_PERFORMED=NO
HISTORICAL_ARTIFACT_REWRITTEN=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```
