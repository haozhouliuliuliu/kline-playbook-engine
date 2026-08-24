# JIANGHE STAGE-A SECURE CREDENTIAL READINESS INTEGRATION V0.1

Status: `INTEGRATED__OWNER_SECRET_CONFIGURATION_PENDING`
Date: 2026-08-24
Implementation merge: `c3ec8fda6331106b3916ea14875e26fc0a0ec640` (PR #25)
Tool decision: `USE_EXISTING`

## Result

The repository now has a manual-only, non-billable credential/existing-balance readiness boundary:

- `.github/workflows/stage-a-provider-readiness.yml`
- `src/jianghe_provider_readiness.py`
- `tools/check_jianghe_provider_readiness.py`
- `tests/test_stage_a_readiness_workflow.py`

The workflow is `workflow_dispatch` only, accepts `main` only, uses read-only repository permission, references the GitHub environment `stage-a-readiness`, and does not contain or invoke `tools/run_jianghe_stage_a_slot.py` or any direct model endpoint.

Provider credentials are referenced only through named GitHub Actions secrets:

```text
MOONSHOT_API_KEY
DEEPSEEK_API_KEY
MINIMAX_API_KEY
```

Secret values must never be pasted into chat, committed to Git, printed to logs, or materialized in evidence.

## Non-billable balance behavior

```text
KIMI=GET_/v1/users/me/balance_ONLY
DEEPSEEK=GET_/user/balance_ONLY
MINIMAX_PAYGO=NO_VERIFIED_READ_ONLY_BALANCE_API__UNKNOWN_WITH_ZERO_NETWORK
MODEL_ENDPOINT_AS_BALANCE_PROBE=FORBIDDEN
BALANCE_REQUEST_RETRY=FORBIDDEN
FUNDING_ACTION=NONE
```

Frozen five-slot Stage-A worst-case ceilings:

```text
KIMI=5.57772_CNY
DEEPSEEK=0.775968_CNY
MINIMAX=1.0885308_CNY
```

These ceilings are not recharge requests. New recharge/top-up remains undecided until existing balances are verified. If funding is required, the project brain must return provider + exact shortfall + freshly verified official funding URL + reason to Owner before any payment action.

## Verification

PR #25 offline verification:

```text
STAGE_A_FOCUSED_TESTS=PASS__49_TESTS
CANONICAL_FULL_SUITE=PASS__1278_TESTS__27_SKIPPED
DIFF_HYGIENE=PASS
FROZEN_PLAN_CHECK=PASS
FROZEN_PLAN_INDEPENDENT_REBUILD=PASS
LIVE_CALLS=0
PAID_SPEND_CNY=0
```

## Current gate

```text
STAGE_A_STATUS=AUTHORIZED__NOT_STARTED
READINESS_WORKFLOW=INTEGRATED__NOT_RUN
GITHUB_ENVIRONMENT=stage-a-readiness__OWNER_CONFIGURATION_PENDING
PROVIDER_SECRETS=NOT_CONFIGURED
EXISTING_PROVIDER_BALANCE=NOT_VERIFIED
NEW_RECHARGE_REQUIRED=NOT_DETERMINED
LIVE_CALLS=0
PAID_SPEND_CNY=0
```

Next: Owner securely configures provider secrets; then run the manual non-billable readiness workflow. No Stage-A model call is permitted as part of this readiness step.
