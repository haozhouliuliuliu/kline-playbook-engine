# Jianghe Stage-A V0.3 Offline Closure V0.1

Status: `V0_3_OFFLINE_CLOSURE_COMPLETE__AWAITING_PROJECT_BRAIN_REVIEW`
Date: 2026-08-25
Tool decision: `USE_EXISTING`
Paid provider calls: `0` (none made by this closure)

## Purpose

This closure records the one-shot resolution of all confirmed Stage-A V0.3 offline
blockers (PF-003..PF-015, NF-001..NF-004) so a first DeepSeek
`V0_3:DEEPSEEK:CAPABILITY_MATCHED_001` matched capability call may be reviewed and
minted by the project brain. No real provider call, no secret read/print, no
outcome/future/broker/real-money activity occurred.

## Authority facts

```text
PF-001=RETRACTED_BY_OWNER_FIRST_PARTY_EVIDENCE
PF-002=RETRACTED_BY_OWNER_FIRST_PARTY_EVIDENCE
DEEPSEEK_NATIVE_VISION_MODEL_EXISTS=YES
MODEL_ID=deepseek-v4-flash-vision-exp
IMAGE_INPUT=YES
```
Reference: `docs/reviews/DEEPSEEK_V4_FLASH_VISION_EXP_FIRST_PARTY_CORRECTION_V0_1.md`.

## Finding disposition

| Finding | Status | Where closed |
|---|---|---|
| PF-001 | RETRACTED | Owner first-party evidence; vision guide verifies base64 `image_url` data URL |
| PF-002 | RETRACTED | First-party docs list `deepseek-v4-flash-vision-exp` as current |
| PF-003 | CLOSED | V0.3 capability pass uses one shared headed answer contract; `response_format_policy=NONE` for all three providers; production JSON never forced |
| PF-004 | CLOSED | New `V03Request`/`V03ProviderInferenceConfig`; no `max_output_tokens<=2000`, no `runtime_response_json_schema` binding; headroom 131072 |
| PF-005 | CLOSED | V0.3 removes CNY18/CNY6/5-call/15-call gates; only `TOTAL_API_HARD_CAP_CNY=100` remains (frozen plan `hard_project_cap_cny=100`) |
| PF-006 | CLOSED | `V03BudgetLedger` initializes at `HISTORICAL_PROJECT_ACCOUNTED_CNY=0.270021`; V0.3 plan carries 0.270021; theoretical remaining 99.729979 |
| PF-007 | CLOSED | `V03InvocationEvidence` preserves `MODEL_RAW_FINAL_ANSWER`; durable evidence never persists reasoning text / raw provider body (`hidden_reasoning_persisted=False`, `raw_provider_body_persisted=False`) |
| PF-008 | CLOSED | Three-tier identity: `V03CommonExamIdentity` (provider-neutral) + `V03ProviderInferenceConfig.identity` + `V03AttemptIdentity` |
| PF-009 | CLOSED | All three providers send the same canonical PNG bytes via base64 `image_url` data URL (first-party documented for DeepSeek and MiniMax) |
| PF-010 | CLOSED | Network timeout 900s per provider config; workflow timeout 30 min |
| PF-011 | CLOSED | `V03BudgetLedger` records PRECALL_CONSERVATIVE_RESERVATION_CNY / POSTCALL_CALCULATED_CNY / PROVIDER_REPORTED_BILLED_CNY / ACCOUNTED_CNY_FOR_HARD_CAP; calculated figure labeled conservative (cache discount not computed from committed authority) |
| PF-012 | CLOSED | V0.3 status taxonomy (INFRASTRUCTURE_FAILURE..CAPABILITY_NOT_SCOREABLE); only true infra/transport failures produce a red job |
| PF-013 | CLOSED | `actions/checkout@v7` + `actions/setup-python@v7` in offline CI, readiness and new V0.3 live workflow |
| PF-014 | CLOSED | V0.3 reuses repository-bound authorization/rate-card freshness checks; model id bound by frozen plan + `PROVIDER_MODEL_MISMATCH` fail-closed |
| PF-015 | CLOSED | `REQUESTED_MODEL_ID`/`RESOLVED_MODEL_ID` recorded; `V03ModelMismatchError` fail-closed before score |
| NF-001 | CLOSED | `tests/test_stage_a_live_workflow.py` rewritten to assert V0.2 retirement + V0.3 workflow properties |
| NF-002 | CLOSED | New V0.3 plan/slot/attempt identities, remote ref `stage-a-live-state-v0-3`, lane + runner exist |
| NF-003 | CLOSED | V0.3 uses brand-new identities (`V0_3:*:CAPABILITY_MATCHED_001`); old DEEPSEEK:1/MINIMAX:1/KIMI:1 never accepted (rejected by V0.3 ledger slot grammar) |
| NF-004 | CLOSED | `OUTPUT_EMPTY` terminal status preserves envelope/mechanical evidence; not an infra red job, not a capability fail |

## Implementation

New/updated files:
- `src/jianghe_v03_runtime.py` — V0.3 capability runtime (contracts, identities, adapter, budget, transport, evidence).
- `src/jianghe_v03_plan.py` + `tools/build_jianghe_stage_a_frozen_plan_v0_3.py` — deterministic V0.3 plan.
- `docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_3.json` — frozen V0.3 plan.
- `docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_3.json` — shared headed capability-answer prompt.
- `src/jianghe_v03_live_lane.py` + `tools/run_jianghe_v03_slot.py` — crash-safe single-slot lane on `stage-a-live-state-v0-3`.
- `.github/workflows/stage-a-v0-3-live-slot.yml` — manual main-only protected workflow (provider input only).
- `.github/workflows/stage-a-offline-ci.yml`, `stage-a-provider-readiness.yml` — Node24 action majors + V0.3 plan/test steps.
- `tests/test_jianghe_v03_runtime.py`, `test_jianghe_v03_adapter.py`, `test_jianghe_v03_plan.py`, `test_jianghe_v03_live_lane.py`, updated `test_stage_a_live_workflow.py`.

## Capability answer contract (shared verbatim by all three providers)

`MARKET_INTERPRETATION`, `FAMILY` (A|B|C|D|NONE|UNKNOWN), `SETUP_OR_NO_SETUP`,
`ACTION` (WAIT|NO_TRADE|ENTER|MANAGE|EXIT), `DIRECTION_IF_APPLICABLE`
(LONG|SHORT|NONE|UNKNOWN), `EVIDENCE`, `INVALIDATION_OR_UNCERTAINTY`,
`JIANGHE_PRINCIPLES_USED`, `VISUAL_OBSERVATIONS`, `STRUCTURED_OBSERVATIONS`,
`CONTRADICTIONS`, `DECLARED_UNKNOWN`. No production JSON forcing; no answer hints.
The adapter is format-only and cannot infer FAMILY from prose.

## Frozen identities

```text
V0_3_PLAN_IDENTITY=2a7897926fcf94ef58bd26b002a0cd3dbcd408c26af5a21ac6eb8a611f0887c3
COMMON_EXAM_IDENTITY=7521af411b5df17d27ced17c27a2db34e776ba85a97070f7634e3a197bf3c4e8
DEEPSEEK_SLOT_ID=V0_3:DEEPSEEK:CAPABILITY_MATCHED_001
MINIMAX_SLOT_ID=V0_3:MINIMAX:CAPABILITY_MATCHED_001
KIMI_SLOT_ID=V0_3:KIMI:CAPABILITY_MATCHED_001
REMOTE_REF=refs/heads/stage-a-live-state-v0-3
HISTORICAL_PROJECT_ACCOUNTED_CNY=0.270021
HARD_CAP_CNY=100
TOTAL_WORST_CASE_INCLUDING_HISTORICAL_CNY=18.668101
```

## Test evidence

Commands run (zero network; all provider responses mocked) from the V0.3 worktree:

- `python -m compileall -q src tools tests` — PASS
- `tools/build_jianghe_stage_a_frozen_plan_v0_3.py --check` — PASS (deterministic)
- `tools/build_jianghe_stage_a_frozen_plan_v0_2.py --check` — PASS (V0.2 history untouched)
- `git diff --check` — PASS
- Focused Stage-A + V0.3 suite (12 modules) — PASS (163 tests)
- Canonical full suite, LF authoritative checkout of this branch — PASS (1404 tests, 0 failures, 0 errors)

### Windows CRLF canonical result (environment-only)

```text
WINDOWS_CRLF_CANONICAL_RESULT=1404_TESTS__8_IDENTITY_FAILURES
ROOT_CAUSE=WORKTREE_CRLF_BYTES_DIFFER_FROM_AUTHORITATIVE_GIT_LF_BLOBS
MECHANISM=PATH_READ_BYTES_ON_CRLF_WORKTREE_DIFFERS_FROM_AUTHORITATIVE_LF_GIT_BLOBS
V0_3_CAUSED=NO
PROOF=
  - pristine afac050 relevant determinism tests pass;
  - `git diff afac050 HEAD` touches none of the affected identity inputs;
  - the same V0.3 HEAD in a `core.autocrlf=false` LF checkout passes all 1404 tests;
  - full canonical LF result = 1404 tests, OK.
CANONICAL_ACCEPTANCE_ENVIRONMENT=AUTHORITATIVE_LF_CHECKOUT
```
The 8 failures occur only in a Windows `core.autocrlf=true` working-tree checkout
where `Path.read_bytes()` reads CRLF bytes that differ from the authoritative LF
Git blobs. They are a pre-existing environment byte difference, not a V0.3
provider/runtime blocker, and they do not appear on the canonical LF CI.

## Go / no-go

```text
GO_FOR_DEEPSEEK_V0_3_FIRST_PAID_TEST=YES (code-layer offline closure complete)
PAID_PROVIDER_CALLS_MADE=0
SECRETS_READ_OR_PRINTED=NO
```
This worker executed no paid provider call. The new `V0_3:DEEPSEEK:CAPABILITY_MATCHED_001`
slot is ready to be executed by the project brain after remote review/merge of this branch.
`NEXT_ACTION=PROJECT_BRAIN_REMOTE_REVIEW_MERGE_THEN_EXECUTE_V0_3_DEEPSEEK_CAPABILITY_MATCHED_001`.
