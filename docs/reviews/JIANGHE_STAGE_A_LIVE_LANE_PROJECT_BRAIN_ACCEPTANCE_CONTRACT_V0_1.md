# JIANGHE STAGE-A LIVE LANE — PROJECT-BRAIN ACCEPTANCE CONTRACT V0.1

Status: `PROJECT_BRAIN_REVIEW_CONTRACT__ENGINEERING_ONLY`
Date: 2026-08-24
Tool decision: `USE_EXISTING`

This document does not change frozen Stage-A research semantics, provider/model eligibility, the RMB100 funnel, the Owner paid-call authorization, or any outcome/shadow/broker/real-money lock. It records the engineering acceptance conditions the project brain will apply before a GitHub-hosted paid Stage-A lane can be merged or used.

## 1. Current gap

The integrated single-slot runner persists `NETWORK_ATTEMPT_STARTED` to local `.runtime/jianghe_stage_a` state and fsyncs before transport. That is sufficient for a persistent local machine but not for an ephemeral GitHub-hosted runner: a runner crash can destroy the only durable record that a paid slot started.

Therefore no GitHub-hosted paid Stage-A call is acceptable until a repository-native durable remote write-ahead boundary exists.

## 2. V1 execution mode

```text
LIVE_LANE_V1=SINGLE_SLOT_EXPLICIT_ONLY
RUN_ALL_REMAINING_STAGE_A=FORBIDDEN_IN_V1
AUTOMATIC_SEMANTIC_RETRY=FORBIDDEN
AUTOMATIC_BUDGET_EXTENSION=FORBIDDEN
```

Reason: the existing Stage-A funnel contains fatal stop conditions that depend on post-call evidence/evaluator judgment, including unscoreable responses, forbidden outcome/future references, invented hard-risk semantics, and unexplained dual-input contradiction. Until a governed automatic evaluator is separately authorized and proven to enforce every fatal stop, auto-running later slots could spend after an earlier fatal failure.

The project brain must review the durable evidence from each attempted slot before authorizing the next slot.

## 3. Exact pre-network order

A production GitHub live path must preserve this order:

```text
1. verify exact committed frozen-plan bytes against deterministic rebuild
2. prepare exact frozen provider/slot request and verify request/payload/stimulus/rate-card identities
3. verify current paid-call authorization, expiry, provider/model and hard caps
4. load and verify durable remote execution state
5. verify the slot is legally unattempted and the conservative cumulative budget permits it
6. verify the required provider credential is present, without serializing or printing it
7. construct the safe NETWORK_ATTEMPT_STARTED reservation
8. persist that start to durable remote state with compare-and-swap / non-fast-forward protection
9. re-read/verify the durable remote state proves that exact reservation is committed
10. only then permit the provider network request
11. materialize terminal/evidence using the existing secret-fail-closed evidence boundary
12. persist a safe terminal/evidence binding to durable remote state
```

Credential presence must be checked before durable reservation. A missing credential must make zero provider calls and must not permanently consume a frozen slot.

## 4. Durable remote state

Preferred design: a fixed dedicated repository runtime-state branch/ref, separate from `main`, containing only machine-readable secret-free Stage-A execution state and accepted safe evidence artifacts.

Required properties:

```text
REMOTE_STATE_BRANCH_NAME=FIXED_BY_CODE_OR_GOVERNED_CONFIG
CALLER_SELECTED_STATE_BRANCH=FORBIDDEN
FORCE_PUSH_FROM_LIVE_PATH=FORBIDDEN
CAS_OR_NON_FAST_FORWARD_UPDATE=REQUIRED
WORKFLOW_CONCURRENCY=SECONDARY_DEFENSE_ONLY
REMOTE_WRITE_FAILURE=ZERO_PROVIDER_NETWORK
REMOTE_VERIFICATION_FAILURE=ZERO_PROVIDER_NETWORK
STALE_HEAD_OR_CAS_CONFLICT=ZERO_PROVIDER_NETWORK
```

If two jobs race on the same remote head, at most one may successfully reserve a slot. A lost race must fail closed before provider network.

The remote execution ledger may contain frozen plan/request/payload identities, provider/model/slot, safe start identity, worst-case reservation, safe terminal/accounting status and durable evidence identities. It must not contain provider credentials, Authorization headers, GitHub tokens, raw secret-like values, or unchecked raw provider bodies.

## 5. Crash semantics

Once the durable remote `NETWORK_ATTEMPT_STARTED` exists, the slot is permanently `ATTEMPTED` for automatic execution purposes.

If any later step is missing because of process crash, hosted-runner loss, timeout, cancellation, transport interruption, terminal persistence failure, or evidence-export failure:

```text
AUTOMATIC_RETRY=FORBIDDEN
ACCOUNTING=FULL_FROZEN_WORST_CASE
NEXT_RESUME_SAME_SLOT=FORBIDDEN
```

Evidence-export failure must never be converted into permission to call the model again.

## 6. Existing local runner seam

The existing local fsync journal remains useful for deterministic attempt evidence and local/offline tests. The GitHub production live workflow, however, must not call a paid transport solely on the basis of local journal state.

A minimal acceptable implementation may:

- perform the remote reservation/verification first;
- then create the existing local start record;
- then invoke the existing audited transport;
- then materialize existing Stage-A attempt evidence;
- then bind the resulting safe terminal/evidence identity back into remote state.

A larger runner rewrite is not required if the remote gate is real and non-bypassable from the production workflow.

## 7. Workflow boundary

The paid live workflow must be:

```text
TRIGGER=workflow_dispatch_ONLY
ALLOWED_REF=main_ONLY
ENVIRONMENT=stage-a-readiness
INPUT_MODE=EXPLICIT_PROVIDER_AND_SLOT_ONLY
MODEL_INPUT=DERIVED_FROM_FROZEN_PLAN__NOT_CALLER_SELECTED
PERMISSIONS=MINIMUM_REQUIRED_FOR_CHECKOUT_AND_DURABLE_STATE_WRITE
AUTO_TRIGGER_ON_PUSH_OR_PR=FORBIDDEN
```

Provider secrets may come only from the existing protected environment. CI and PR tests must continue to run with provider credentials absent and must perform zero real provider calls.

## 8. Research/evaluation boundary

The live lane is an execution/durability mechanism only. It must not invent:

- new Stage-A slot ordering rules;
- new fatal-stop semantics;
- automatic provider ranking;
- evaluator-side fidelity judgments;
- new provider/model eligibility;
- any outcome/PnL rule.

The existing RMB100 funnel and current evaluator/scoring authorities remain authoritative.

## 9. Required adversarial acceptance

At minimum the implementation must prove, with injected/fake transport only:

1. remote state unavailable -> zero network;
2. remote write failure -> zero network;
3. remote verification failure -> zero network;
4. stale remote head/CAS conflict -> zero network;
5. concurrent reservation of one slot -> at most one success;
6. missing credential -> zero network and no durable slot consumption;
7. already-started slot -> retry forbidden;
8. started-without-terminal -> full worst-case accounting;
9. crash immediately after durable start -> resume never re-calls the slot;
10. crash/exception during network -> same;
11. terminal persistence failure -> same slot remains non-retryable;
12. evidence-export/secret-guard failure -> no retry;
13. remote state tamper/hash mismatch -> zero network;
14. wrong frozen plan/request/payload/provider/model -> zero network;
15. expired authorization -> zero network;
16. budget-cap breach -> zero network;
17. non-main workflow invocation -> no live job;
18. push/PR cannot auto-trigger paid workflow;
19. safe remote ledger contains no credential material or unchecked raw provider body;
20. durable evidence identity is bound to exact provider/slot/plan/start/terminal facts.

## 10. Merge/use gate

Before project-brain closure the candidate must pass:

```text
COMPILE=PASS
FROZEN_PLAN_CHECK=PASS
FOCUSED_STAGE_A_TESTS=PASS
NEW_LIVE_LANE_ADVERSARIAL_TESTS=PASS
CANONICAL_LINUX_FULL_SUITE=PASS
DIFF_HYGIENE=PASS
LIVE_CALLS_DURING_IMPLEMENTATION=0
PAID_MODEL_API_SPEND_DURING_IMPLEMENTATION=CNY_0
BSP_003=PRESERVED
RESEARCH_SEMANTICS_CHANGED=NO
```

Only after this contract is satisfied may the project brain consider the first explicit paid Stage-A slot. That later paid call remains governed by the already-committed Owner authorization and its expiry/caps.