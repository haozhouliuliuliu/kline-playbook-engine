# 江河来源本地 ASR 语义验收规则 V1.0

> Scope: Jianghe source-evidence transport only  
> Tool: project-approved `faster-whisper` local CPU/int8 path  
> Status: BINDING_FOR_JIANGHE_SOURCE_REVIEW

## Why this rule exists

Corpus recovery verified model identity, hash, CTranslate2 loading and time-axis coverage. Final Sol review then found that V065's transcript was semantically unrelated to the actual video despite those mechanical checks.

Therefore:

```text
DOWNLOAD/MODEL_INTEGRITY
+ MODEL_LOAD
+ TIMESTAMP_MONOTONICITY
+ DURATION_COVERAGE
!=
SEMANTIC_LANGUAGE_EVIDENCE_ACCEPTANCE
```

## Acceptance gate

A local ASR transcript may support Jianghe source claims only when all are true:

1. native subtitle absence was already confirmed;
2. model identity/load checks pass;
3. complete time-axis/coverage checks pass;
4. beginning, middle and end audio/text spot checks show the expected source language;
5. transcript is semantically plausible relative to audible speech;
6. no obvious repetitive hallucination, unrelated-language drift or long fabricated repetition is present;
7. low-confidence regions remain disclosed.

If any semantic check fails:

```text
TRANSCRIPT_STATUS=REJECTED_AS_LANGUAGE_EVIDENCE
SOURCE_CLAIM_FROM_ASR=FORBIDDEN
VISUAL_ORDER_OUTCOME_INFERENCE=FORBIDDEN
```

The media may still be reviewed visually, but trading reasons may not be inferred from chart/order outcomes.

## V065 precedent

V065 is the binding negative example:
- native subtitle: unavailable;
- faster-whisper mechanical validation: passed in corpus-recovery workflow;
- final semantic QA: failed;
- disposition: `LOCAL_ASR_REJECTED_SEMANTIC_HALLUCINATION`;
- semantic claim count: 0.

This does not revoke the project's scoped approval of faster-whisper as an evidence-transport tool. It narrows acceptance of **individual transcript outputs** fail-closed.
