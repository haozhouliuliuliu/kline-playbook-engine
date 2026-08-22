# Jianghe V1.1 Project-Brain Acceptance — 2026-08-23

## Decision

```text
PROJECT_BRAIN_REPOSITORY_ACCEPTANCE=PASS
SOURCE_DISTILLATION_COMPLETENESS_ACCEPTED=YES
SECOND_PASS_SOURCE_COVERAGE_AUDIT=COMPLETE
FINAL_SOURCE_DISTILLATION=COMPLETE_V1_1_AFTER_CORRECTIVE_SECOND_PASS
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
REAL_MONEY=NOT_AUTHORIZED
MAIN_INTEGRATION_METHOD=FAST_FORWARD_ELIGIBLE_IF_BRANCH_REMAINS_0_BEHIND
TOOL_DECISION=USE_EXISTING
```

This acceptance is limited to durable repository integration of the Jianghe source-research line. It is not performance validation, PRIMARY promotion, candidate-outcome authority, broker authorization, or trading authorization.

## Reviewed repository state

Repository: `haozhouliuliuliu/kline-playbook-engine`  
Branch: `research/jianghe-evidence-001-099-v1-0-final`  
Main base at review start: `42e6ee8e42804ad27f4fe63fd20fad040bd1054d`  
Reviewed branch head before this acceptance record: `b32f4ea218d1f0e4efd22617daedec8ff8f33125`

The branch was directly compared with `main` after the governance repairs and remained `behind_by=0`; it therefore contained all current main history plus the Jianghe line.

## Evidence accepted

The durable V1.1 package establishes, at repository/source-distillation level:

```text
SOURCE_TOTAL=99
UNIQUE_BVID=99
MEDIA_AVAILABLE=98
PAID_GATE_EXCEPTION=022
FULL_TIMELINE_SECOND_PASS_AVAILABLE_MEDIA=98
UNACCOUNTED_TIMELINE_GAP=0
SECOND_PASS_UNDEREXTRACTION_SOURCES=22
SECOND_PASS_RECOVERED_CLAIMS=64
SECOND_PASS_RECOVERED_CASES=9
VISUAL_ONLY_NO_RELIABLE_LANGUAGE=065
RECOVERED_REMOTE_SRT_USED_WITHOUT_IDENTITY_QA=0
DOSSIER_SECTIONS=14
CORE_STRATEGY_FAMILIES=A,B,C,D
FAMILY_E=NOT_JUSTIFIED
```

The accepted authority chain is:

1. `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md`
2. `docs/research/jianghe/JIANGHE_SECOND_PASS_VERIFICATION_REPORT_V1_1.md`
3. `docs/research/jianghe/JIANGHE_TRADER_DOSSIER_V1_1.md`
4. `docs/research/jianghe/JIANGHE_SECOND_PASS_RECONCILIATION_V1_1.md`
5. `docs/research/jianghe/JIANGHE_SECOND_PASS_CASE_LIBRARY_DELTA_V1_1.md`
6. `docs/research/jianghe/JIANGHE_STRATEGY_FAMILIES_V1_1.md`
7. `docs/research/jianghe/JIANGHE_UNKNOWN_REGISTER_V1_1.md`
8. `docs/research/jianghe/JIANGHE_CONTRADICTION_REGISTER_V1_1.md`
9. `docs/research/jianghe/second_pass_salvage/SECOND_PASS_SALVAGE_MANIFEST_V1_1.md`
10. `docs/research/jianghe/second_pass_salvage/JIANGHE_SECOND_PASS_INTEGRITY_CHECK_V1_1.md`
11. the four coverage fragments, four 64-claim fragments and five source-findings fragments under `second_pass_salvage/`.

The Dossier has exactly 14 numbered sections. The V1.1 Strategy Families file preserves exactly A–D. The UNKNOWN register keeps unpinned machine semantics open rather than filling them by project convention. The Contradiction Register records zero items requiring invented semantic reconciliation.

## Fail-closed language/evidence dispositions

Accepted dispositions:

```text
022=SOURCE_UNAVAILABLE_PAID_GATED
065=VISUAL_ONLY_NO_RELIABLE_LANGUAGE__SEMANTIC_CLAIM_COUNT_0
048_REMOTE_SRT=REJECTED_WRONG_VIDEO
099_REMOTE_SRT=REJECTED_WRONG_VIDEO
009_REMOTE_SRT=FAIL_CLOSED_NOT_USED_IN_SECOND_PASS
014_REMOTE_SRT=FAIL_CLOSED_NOT_USED_IN_SECOND_PASS
065_LOCAL_ASR=REJECTED_SEMANTIC_HALLUCINATION
```

The remote-subtitle contamination engineering root cause remains `ENGINEERING OPEN, NOT A SEMANTIC BLOCKER`. That acquisition path must not again be treated as automatically trusted language evidence until its identity failure is repaired and revalidated.

## Governance corrections made during acceptance

The project-brain acceptance pass made the following bounded repairs before integration:

- `bf4c8e0e44c23a9468dbbd6c0a29c6afce0d9620` — closed the historical V1.1 coverage audit and preserved its original opening rationale/criteria.
- `abbac09f3fee007f3735ab9fdf4e4f8684ff08ff` — corrected the salvage manifest so GitHub LF-normalized coverage fragments are not falsely claimed raw-byte-identical to the historical local CRLF artifact.
- `0b27a4735925ba6a52bf26435b5e6996275039a6` — aligned the integrity report with that newline-normalization qualification.
- `690b4aad5a0403f297e48aa0eee355296d1b38e9` and `189a0f1febe488f6aef59715cfcf06ed33ab917d` — removed two write-probe files from the integration tip while preserving their historical commits.
- `24b9e6f5c6299e1a85d79daf2ffbbffd1b72bcbf` — made the exact-range local integration test portable and skip-safe when local corpus/ffmpeg evidence is absent.
- `b32f4ea218d1f0e4efd22617daedec8ff8f33125` — added repository-only V1.1 acceptance checks for 99/98 coverage, 64 claims, 9 cases, 14 dossier sections, Families A–D, UNKNOWN/Contradiction handling, audit closure, byte-integrity honesty, and locked outcome boundaries.

## Coverage byte-integrity qualification

The historical local coverage CSV is identified as:

```text
LOCAL_BYTES=35142
LOCAL_NEWLINES=100
LOCAL_SHA256=1133f089caec2906668241c901a0034e8c5d0d0fa6efcefa9ba61f3994f65877
```

GitHub text writes normalized CRLF to LF. The four remote coverage fragments total 35042 bytes, exactly 100 bytes smaller, consistent with the 100 newline delimiters.

Therefore:

```text
REMOTE_GITHUB_RAW_BYTE_IDENTITY_TO_LOCAL=NOT_CLAIMED
REMOTE_GITHUB_TEXT_ROW_CONTENT=PRESERVED_WITH_LF_NORMALIZATION
```

This does not invalidate the 99-row semantic/mechanical coverage record. It only prevents an unsupported raw-byte equality claim.

The four claim JSONL fragments retain the recorded remote byte sizes and the durable package records 64 valid unique claim IDs.

## Visual/media storage boundary

The existing Jianghe corpus preparation authority explicitly excludes large media, subtitles, analysis packages, frames and logs from Git tracking. Therefore bulk JPG/PNG/contact-sheet upload is **not** a prerequisite for main integration and should not be used to turn Git into a media archive.

Important visual conclusions remain linked to source ordinal/BVID/timestamp and same-time visual review semantics. Source media/frame material belongs in the non-Git evidence layer and can be regenerated with the read-only extraction tooling where the accepted source corpus remains available.

## Test/execution status

A repository-only `unittest` acceptance file was added and statically reviewed. Existing Jianghe unit-test imports were also inspected for top-level third-party dependency hazards; the reviewed acquisition/audit/downloader paths use Python standard-library imports at discovery time.

However, the current assistant container has neither GitHub network/DNS access nor repository credentials, and this repository has no available GitHub Actions workflow surface exposed here. Therefore the full canonical command was **not independently re-executed in this acceptance session**:

```text
python -m unittest discover -s tests -v
```

Record this honestly as:

```text
CURRENT_SESSION_CANONICAL_TEST_EXECUTION=NOT_AVAILABLE_IN_CURRENT_TOOL_SURFACE
CURRENT_SESSION_TEST_PASS_NOT_CLAIMED
STATIC_IMPORT_AND_REPOSITORY_EVIDENCE_REVIEW=PASS
```

This execution limitation is non-semantic and does not reopen the already durable source-distillation evidence. It remains ordinary engineering follow-up when a repository execution environment is next available.

## Integration-risk assessment

The Jianghe branch adds/modifies research documents, research acquisition/audit tooling, tests, and `TOOL_REGISTRY.md`. It does not modify the production/live runtime critical path, StrategyIdentity, ResearchFirewall, RiskGate, broker access, outcome-test authority, validation locks, or frozen chronology.

No new tool is required for integration:

```text
CAPABILITY_DECISION=USE_EXISTING
```

## Final boundary

```text
SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION
UNKNOWN > GUESSING
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
REAL_MONEY=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
```
