# Main baseline test debt + Jianghe Git-blob identity repair V0.1

> Date: 2026-08-24
> Integration PR: #20
> Integrated commit: `ef6862cadb495f543d4d6fcc659701c7ccea7dd0`

## Conclusion

```text
MAIN_BASELINE_REPAIR=PASS
CANONICAL_FULL_SUITE=PASS_IN_ISOLATED_MATERIALIZATION_GATE
TARGETED_REGRESSION=PASS_IN_ISOLATED_MATERIALIZATION_GATE
SOURCE_ONLY_REPOSITORY_BYTE_AUTHORITY=EXACT_COMMITTED_GIT_BLOB_BYTES
OLD_CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
CORRECTED_CLAIM_MANIFEST_IDENTITY=f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36
CLAIM_RECORDS=352
CLAIM_SEMANTIC_CHANGE_COUNT=0
PRIMARY_V0_5_CURATED_SEMANTIC_CHANGE_COUNT=0
PRIMARY_V0_5_IDENTITY_REBIND=COMPLETE
HISTORICAL_V0_3_PRIMARY_ARTIFACTS=UNCHANGED
OUTCOME_ACCESS=NO
PAID_SPEND=0
LIVE_CALLS=0
```

## Why the green result is mechanically established

The isolated branch workflow was fail-closed for materialization: it first applied the deterministic repair, then ran focused/targeted regression, then ran the canonical full suite `python -m unittest discover -s tests -v`. Only if all stages exited zero did it delete its temporary repair script, diagnostic file and temporary workflow, create the final materialized commit, and push that commit.

The final branch head used by PR #20 (`3eeee366b3f11c7a36fcd6ceee7b052c257a8538`) contains the repaired artifacts and tests while the temporary repair script, diagnostic and branch workflow are absent. Therefore the guarded materialization path completed successfully; a failing targeted or full-suite run could not have produced that final head.

## Repairs integrated

1. Portable Bilibili path assertion no longer hard-codes Windows separators.
2. Canonical eligibility tests that truly require the external governed local corpus skip only those integration cases when that corpus is absent; fail-closed/unit behavior remains testable in clean CI.
3. Existing deterministic evidence/builders were regenerated where repository code and generated artifacts had drifted, retaining explicit identity pins rather than weakening assertions.
4. Jianghe SOURCE_ONLY exact-byte binding now hashes and sizes the committed Git blob, not OS-specific checkout bytes.
5. The CRLF/LF discrepancy was proven to be line-ending normalization: all 16 claim materials matched the exact byte-count signature and 352 claim JSON records had zero semantic-field changes.
6. Current PRIMARY V0.5 was mechanically rebound to the corrected claim-manifest identity; only identity fields and derived branch identities were permitted to move. Historical V0.3 artifacts remain unchanged.

Detailed Jianghe identity authority: `docs/reviews/JIANGHE_SOURCE_ONLY_GIT_BLOB_IDENTITY_CORRECTION_V0_1.md`.

## Non-effects

This repair does not close or modify the frozen pre-spend finding set by itself. BSP-001..005 and RSP-001..002 retain their existing status until their dedicated repair and finding-specific re-audit complete. It does not authorize provider calls, paid spend, candidate outcomes, PRIMARY semantic freeze, Validation, Final, Shadow/Forward, broker access or real money.
