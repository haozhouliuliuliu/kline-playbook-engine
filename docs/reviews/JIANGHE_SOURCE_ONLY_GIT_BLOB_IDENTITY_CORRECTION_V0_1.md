# Jianghe SOURCE_ONLY Git-blob identity correction V0.1

## Decision

```text
CORRECTION_TYPE=EVIDENCE_IDENTITY_CORRECTNESS_ONLY
ROOT_CAUSE=WINDOWS_CRLF_WORKTREE_BYTES_HASHED_WHILE_GIT_STORED_LF_BLOBS
OLD_CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
CORRECTED_CLAIM_MANIFEST_IDENTITY=f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36
CLAIM_RECORDS=352
CLAIM_SEMANTIC_CHANGE_COUNT=0
PRIMARY_CURATED_SEMANTIC_CHANGE_COUNT=0
PRIMARY_V0_5_REBOUND_RECORDS=352
PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
OUTCOME_ACCESS=NO
PAID_SPEND=0
LIVE_CALLS=0
```

The original SOURCE_ONLY machine evidence claimed exact repository-artifact byte binding but
used `Path.read_bytes()` from a Windows checkout. Git line-ending normalization stored LF blobs,
so CRLF working-tree sizes/hashes were not identities of the committed repository bytes.
All 16 claim files showed the exact CRLF signature: `formal_size - git_blob_size == LF_count`.

A claim-by-claim JSON comparison against the SOURCE_ONLY creation commit found zero changed
claims and zero changes in fields consumed by PRIMARY (`source_reference`, anchors, status,
source meaning, ambiguity and family scope). This correction therefore changes byte/content
identities and derived branch identities only. It does not reopen Jianghe semantics.

The corrected builder binds exact `git show HEAD:<path>` blob bytes and permits a checkout to
differ only by CRLF-to-LF text normalization; any other uncommitted material drift fails closed.
Historical V0.3 PRIMARY artifacts and the historical hygiene/rebind execution record are retained
unchanged. Current V0.5 curated records change only `claim_manifest_identity`; the current V0.5
registry is deterministically rebuilt and may change only `claim_manifest_identity` and derived
`primary_branch_identity`.

Corrected SOURCE_ONLY identities:

```text
SOURCE_MATERIAL_MANIFEST_IDENTITY=8124b0ef9f9063e775d4f924c28b031321fd47b0f85b4cf9b4a6646b77b5b1ff
CLAIM_MANIFEST_IDENTITY=f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36
CASE_MANIFEST_IDENTITY=a985e3bec039ea04e6fa417b336d48c9a8a89164214d7c7864b13d6758c3cd1f
SOURCE_ONLY_SESSION_IDENTITY=c9492e4375ef748c6f616aa32bd2a1052a765aa62b52b98a1d6fa58a6a01f698
```

No candidate outcome, Validation, Final, Shadow, broker, real-money or provider call authorization
is changed by this correction.
