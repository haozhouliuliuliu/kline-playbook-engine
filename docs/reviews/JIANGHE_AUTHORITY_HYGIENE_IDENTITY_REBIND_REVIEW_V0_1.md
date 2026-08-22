# 江河 authority hygiene → identity rebind 审查 V0.1

> Date: 2026-08-23  
> Status: `REBIND_REQUIRED_FAIL_CLOSED`  
> Scope: consequences of removing mutable readiness fields from Jianghe source-distillation documents.  
> No candidate outcome, Validation, Final, Shadow, Broker or real-money access occurred.

## Conclusion

The authority-hygiene cleanup was semantically correct: Jianghe source-distillation documents must not own mutable SOURCE_ONLY / PRIMARY / authorization state. However, the existing V1.1 knowledge-pack builder and SOURCE_ONLY verification bind **raw repository bytes** for several of those documents.

Therefore the hygiene edits changed the active repository bytes without changing Jianghe trading semantics. Under the existing identity design this still changes the research-object byte identity. The old active identity cannot continue to be claimed as the current bundle identity until the existing builders are re-run and all dependent evidence is synchronized.

Fail-closed consequence:

```text
HISTORICAL_PRE_HYGIENE_KNOWLEDGE_PACK_IDENTITY=3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5
HISTORICAL_PRE_HYGIENE_SOURCE_ONLY_VERIFICATION_EVENT=PASS
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=REBIND_REQUIRED
CURRENT_ACTIVE_SOURCE_ONLY_VERIFICATION=REVERIFY_REQUIRED
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

This is an identity/evidence repair requirement, not a source-semantic regression.

## Why the old identity is no longer current

`tools/build_jianghe_knowledge_pack_v0_1.py` constructs `KnowledgePackIdentity` from raw contents of documents including:

- `JIANGHE_CURRENT_VIEW_V1_1.md`
- `JIANGHE_SECOND_PASS_VERIFICATION_REPORT_V1_1.md`
- `JIANGHE_TRADER_DOSSIER_V1_1.md`
- `JIANGHE_SECOND_PASS_RECONCILIATION_V1_1.md`
- `SECOND_PASS_SALVAGE_MANIFEST_V1_1.md`
- `JIANGHE_SECOND_PASS_SOURCE_FINDINGS_MANIFEST_V1_1.md`
- `JIANGHE_SECOND_PASS_SOURCE_FINDINGS_V1_1.part04.md`

The hygiene package changed these bytes to remove or historicalize mutable readiness fields while preserving source claims/cases/UNKNOWN/contradiction semantics.

The checked-in foundation artifact still contains hashes for the pre-hygiene bytes and the identity `3f2ddbf9...`; it is therefore a historical pre-hygiene identity until rebuilt.

## SOURCE_ONLY consequence

`src/jianghe_source_only_verification.py` builds exact repository-artifact manifests and reports:

```text
binding_status=EXACT_REPOSITORY_ARTIFACT_BYTES_BOUND
```

Its source-material set includes second-pass findings and salvage/integrity manifests whose bytes changed in the hygiene package. Consequently the old SOURCE_ONLY evidence remains valid evidence that the **pre-hygiene exact bundle** passed the project API/session gate, but it cannot be used as proof that the **current active-byte bundle** has the same identity.

The claim files and case files were not semantically edited by the hygiene package. Their previously recorded claim/case counts remain research facts, but the complete active SOURCE_ONLY session identity must still be regenerated because the bound source-material bundle changed.

## Required bounded repair under existing semantics

Do **not** redesign identity semantics in this repair. Keep the existing content/hash rules and perform a deterministic rebuild:

1. run `python tools/build_jianghe_knowledge_pack_v0_1.py` on current `main`;
2. record the newly generated current knowledge-pack identity and document hashes;
3. run `python tools/build_jianghe_source_only_verification_v0_1.py` on that same tree;
4. verify exact source/claim/case manifests and technical denials;
5. update all non-historical active references that still bind `3f2ddbf9...` as the current identity, including fidelity fixture metadata and PRIMARY-preparation bindings;
6. preserve `3f2ddbf9...` only where explicitly labeled historical/pre-hygiene provenance;
7. run targeted tests plus the canonical full suite;
8. only after deterministic evidence matches current bytes may `JIANGHE_SOURCE_ONLY_VERIFIED=YES` be restored for the active bundle.

Changing what the knowledge-pack identity *means* or excluding documents from the existing identity would be a separate research-governance decision and is explicitly outside this repair.

## Current boundary

Until the rebuild is complete:

```text
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=REBIND_REQUIRED
CURRENT_ACTIVE_SOURCE_ONLY_VERIFICATION=REVERIFY_REQUIRED
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=BLOCKED_ON_CURRENT_IDENTITY_REBIND_FOR_FINAL_BRANCH_IDENTITIES
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
```

Claim-level semantic review may be prepared without outcomes, but no final claim-level branch identity may be asserted against the stale pre-hygiene knowledge-pack identity.
