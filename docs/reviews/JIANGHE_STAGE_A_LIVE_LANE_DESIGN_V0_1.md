# JIANGHE STAGE-A LIVE LANE DESIGN V0.1

> Status: `OFFLINE_IMPLEMENTATION_FOR_REVIEW__NO_LIVE_CALLS`

The first lane is deliberately explicit single-slot. It introduces no provider ordering, elimination, ranking, evaluator judgment or research-semantic rule.

```text
WORKFLOW_TRIGGER=workflow_dispatch_ONLY
WORKFLOW_REF=main_ONLY
WORKFLOW_ENVIRONMENT=stage-a-readiness
REMOTE_STATE_REF=refs/heads/stage-a-live-state-v0-1
REMOTE_STATE_FILE=stage-a-live-ledger-v0-1.json
REMOTE_START_BEFORE_PROVIDER_NETWORK=REQUIRED
CAS_PRIMITIVE=NORMAL_NON_FORCE_GIT_PUSH_FROM_EXACT_OBSERVED_PARENT
POST_WRITE_VERIFICATION=REMOTE_HEAD_AND_BYTES_EXACT_REREAD
WORKFLOW_CONCURRENCY=SECONDARY_GUARD_ONLY
INCOMPLETE_START=ATTEMPTED__FULL_WORST_CASE__AUTOMATIC_RETRY_FORBIDDEN
RAW_LOCAL_JOURNAL_REMOTE_COMMIT=FORBIDDEN
DURABLE_EVIDENCE=ONLY_AFTER_EXISTING_SECRET_FAIL_CLOSED_EXPORTER
```

The state ref contains only frozen slot/provider/model identities, request and payload identities, safe accounting/status, event hashes and a secret-guarded evidence artifact. It never receives the raw local journal, credentials, Authorization headers or GitHub token.

If remote state is unavailable, a CAS write fails, or the re-read differs, provider transport is unreachable. If a crash occurs after the durable start, the next run sees the slot in `attempted_slots` and refuses to invoke it again. A missing terminal conservatively accounts the complete frozen worst-case reservation.

All existing CNY100 / Stage-A CNY18 / per-provider CNY6 / 15 total / 5 per-provider limits and paid authorization checks remain in the existing runner preflight. BSP-003 and the frozen Stage-A plan/stimulus are unchanged.
