# MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_HANDOFF_2026-08-26

Status: `CURRENT_TASK_HANDOFF`

Delete this file when this work package is completed. Do not append a superseding history section.

## Starting point

Canonical repo: `haozhouliuliuliu/kline-playbook-engine`

Starting main after Harness admission merge:

`16021908b3226c6e9598f8030ddc5f2805825b1a`

Product:

`JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

Model:

`deepseek-v4-flash-vision-exp`

Current work package:

`MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1`

## Runtime shell already decided

Do not redo Harness selection.

Use local DeepSeek Harness only:

- version `0.1.1-rc.2`
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project patch under `integrations/deepseek-harness/`
- retry policy `maxRetries: 0`

Harness dynamic admission is complete. PR #41 passed `project-dynamic-admission` and repository `test`, then merged.

The project patch is mandatory because the unpatched DeepSeek adapter has a stale image-file recovery path capable of issuing a hidden second chat request.

## Deployment boundary

Build the first prototype on the Owner's local workstation.

A localhost Web UI/browser surface is acceptable. Do not build public hosting, cloud deployment, authentication, multi-user infrastructure, mobile packaging or polished product UI in this work package.

Project market data, trader memory, Jianghe knowledge, K-line tools and audit state remain local/project-owned.

## Prototype objective

Prove that one DeepSeek trader can persist as the same governed trader across calls and process restart.

Minimum proof:

1. exact `deepseek-v4-flash-vision-exp` integration path with the admitted Harness composition;
2. existing causal `4H / 1H / 15m / 5m` observation and chart path can be exposed to the trader;
3. `DS_WORKING_MEMORY` persists locally and survives restart;
4. relevant `JIANGHE_CANON` can be retrieved read-only in a bounded, attributable way;
5. project-owned K-line/market tools are callable through Harness and tool activity is audited;
6. `DS_JOURNAL` persists separately from source truth and policy;
7. `DS_HYPOTHESIS_MEMORY` persists separately and is explicitly non-executable policy;
8. every model request/response, retrieved knowledge identity, tool use and memory mutation is reconstructable;
9. `STRICT_OUTPUT_ENUM_ENFORCEMENT` remains active;
10. `NO_4H_EXACT_VOLUME_RECONCILIATION` remains active;
11. no silent retry, hidden second model request, model substitution or prompt mutation;
12. core trader state/knowledge is project-owned and portable if Harness is replaced later.

## Knowledge semantics that must not drift

- `JIANGHE_CANON` is read-only source truth.
- `PROJECT_VALIDATED_POLICY` contains only independently validated project extensions.
- `DS_HYPOTHESIS_MEMORY` is candidate research material, not trading policy.
- `DS_WORKING_MEMORY` is current persistent market state/hypotheses.
- `DS_JOURNAL` is reflection, not fact or policy.

Do not create a mechanism where DeepSeek can directly rewrite Jianghe canon or promote its own hypothesis to active policy.

## Scope exclusions

Do not in this work package:

- run broad historical replay;
- design a new trading research protocol;
- alter Jianghe semantics;
- alter 4H role;
- expose validation/holdout;
- open shadow/broker/real-money lanes;
- make paid provider calls without fresh executable authority;
- optimize profitability;
- create public/cloud deployment;
- spend time on polished generic UI.

## Preferred implementation approach

Keep the prototype small and testable.

Project-owned storage/schema code should sit outside opaque Harness internals. Harness should supply the local agent/session/tool/UI shell; project code should supply trader memory schemas, Jianghe retrieval, K-line tools, context assembly, guards and audit semantics.

Offline/no-network tests should prove persistence, retrieval, tool/audit behavior and fail-closed transport wherever possible before any real API call is considered.

## Acceptance gate

The work package is complete only when automated evidence proves the twelve prototype objectives above and current authority is synchronized.

After completion:

1. update `CURRENT_STATE.md`, `PROJECT_BRAIN_RUNTIME_BRIEF.md`, `00_READ_FIRST.md`, architecture/limitations as needed;
2. delete this dated handoff file rather than marking it obsolete;
3. stop before broad chronological replay unless the next work package has been explicitly defined.
