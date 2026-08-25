# DEEPSEEK_HARNESS_ADMISSION_V0_1

As of: `2026-08-26`

Status: `ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

This authority applies only to DeepSeek Harness as the local runtime/workbench shell for `JIANGHE_PERSISTENT_DEEPSEEK_TRADER`.

It does not authorize provider spend, protected validation data, shadow trading, broker/account access or real-money execution.

## Admitted build

Upstream repository: `deepseek-ai/deepseek-harness`

Pinned commit: `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`

Pinned version: `0.1.1-rc.2`

Required project composition:

- project fail-closed DeepSeek transport patch under `integrations/deepseek-harness/`;
- retry policy `mode: normal`, `maxRetries: 0`;
- exact selected model route `deepseek-v4-flash-vision-exp`;
- project-owned memory/tools/audit semantics.

No floating `main`, `latest` or unpinned Harness build is admitted.

## Dynamic admission result

PR #41 final tested head:

`e4b0e3ef972ed3c8685ab71318f4c1a885a7ccd4`

Checks:

- `project-dynamic-admission = success`
- repository `test = success`

GitHub Actions success marker:

`KPE_HARNESS_DYNAMIC_ADMISSION_PASS head=e4b0e3ef972ed3c8685ab71318f4c1a885a7ccd4 run=32885625244 attempt=1 pinned=b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`

PR #41 merged to `main` as:

`16021908b3226c6e9598f8030ddc5f2805825b1a`

The project-specific dynamic gate proved:

- the pinned Harness composition supports the selected DeepSeek vision/model path used by the project;
- general model retry is explicitly zero;
- stale image-file failure is fail-closed under the project patch and does not silently issue a second chat-completions request;
- project-owned working-memory/tool context can be injected through the Harness agent seam and remains audit-visible;
- SQLite session persistence restores session state across restart;
- DeepSeek image serialization and dynamic config behavior remain intact after the project patch;
- no provider credential or paid provider call was required for admission verification.

## Deployment boundary

`DEPLOYMENT = LOCAL_WORKSTATION_FIRST`

Harness is to be installed/run locally for the first persistent-trader prototype. A Web UI may bind to localhost and be opened in the Owner's browser. This authority does not adopt public/cloud deployment.

Project-owned market data, persistent trader memory, Jianghe source data, K-line tools and audit records remain local/project-controlled unless a later authority explicitly changes that boundary.

## Runtime ownership boundary

Harness owns only runtime-shell concerns such as sessions, tool plumbing, persistence seams and UI infrastructure.

The project continues to own:

- Jianghe canon and provenance;
- memory schemas and promotion rules;
- context-selection semantics;
- trader identity;
- K-line observation/rendering semantics;
- evidence and replay semantics;
- deterministic risk/safety/execution authority.

The trader core must not become dependent on opaque Harness-only state that prevents later migration to another thin shell.

## Current conclusion

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

`TOOL_DECISION = USE_EXISTING__PINNED_DEEPSEEK_HARNESS`

`NEXT_WORK_PACKAGE = MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1`

The next conversation should implement the prototype, not repeat Harness selection/admission work.
