# PROJECT_BRAIN_RUNTIME_BRIEF

Status: `CURRENT_REFRESH_PROCEDURE`

This file owns the project-brain refresh procedure only. It must not duplicate current work-package, phase, locks, paid-slot status or `NEXT_TASK`.

## Mandatory refresh before substantive project work

1. Refresh current GitHub `main` HEAD.
2. Read `PROJECT_GOVERNANCE.md` when governance/authority interpretation is relevant or when the conversation is fresh.
3. Read `PROJECT_DIRECTION.md` for product/research direction.
4. Read `ARCHITECTURE_BASELINE.md` when architecture is relevant.
5. Read `TOOL_REGISTRY.md` when provider/tool/runtime/credential/pin capability matters.
6. Read `CURRENT_STATE.md` for the sole current dynamic state.
7. Read only the task-specific Owner decisions/evidence/code referenced by `CURRENT_STATE.md` and required for the task.
8. For any spend or consequential external execution, additionally refresh the exact Owner execution authority and machine-readable authority immediately before execution.
9. Never infer current project state, permissions, locks, model/tool status or next task from chat memory or stale branches.

## Mandatory minimum pre-answer refresh

Before every substantive project status, plan, recommendation, worker prompt,
review, or execution decision, the project brain must complete, at minimum:

1. refresh current GitHub `main`;
2. read `PROJECT_BRAIN_RUNTIME_BRIEF.md` from that current `main`;
3. read `PROJECT_GOVERNANCE.md`;
4. read `PROJECT_DIRECTION.md`;
5. read `CURRENT_STATE.md`;
6. read the task-relevant canonical owner(s);
7. read the exact Owner authority / machine authority / evidence referenced by
   `CURRENT_STATE.md` when material to the current task.

## Binding-parent dereference rule

If a current canonical owner references or adopts another still-binding
authority, the project brain must not stop at the pointer file when the
referenced rules are material to the current task.

In particular, for worker delegation, model/reasoning selection, parallelism,
prompt construction, cost/context/output discipline, or Owner-gate
interpretation, read the relevant sections of the adopted
`CROSS_PROJECT_OPERATING_CONTRACT` v3.1 from the immutable source identified by
`PROJECT_GOVERNANCE.md`.

## Fresh-conversation rule

A fresh conversation starts with `00_READ_FIRST.md` and follows its takeover order.

The first takeover report is read-only unless the Owner explicitly directs otherwise.

## Authority ownership rule

Use canonical owners instead of synchronizing the same fact everywhere:

- governance/authority ownership: `PROJECT_GOVERNANCE.md`;
- worker/repository procedure: `AGENTS.md`;
- architecture: `ARCHITECTURE_BASELINE.md`;
- tools/providers/pins/credential seams: `TOOL_REGISTRY.md`;
- product/research direction: `PROJECT_DIRECTION.md`;
- volatile current state: `CURRENT_STATE.md`;
- exact spend/execution permission: applicable Owner execution authority + machine authority.

If two active authorities appear to own the same current fact, treat that as an authority defect and reconcile it before consequential execution.

## Secrets

Repository authority may record secret **location contracts** and environment-variable names, never secret values.

Provider availability checks must not print secret values.

## Consequential-action rule

Before a paid provider call, broker/account action, paper/real execution or irreversible external action:

- refresh `main`;
- re-read `CURRENT_STATE.md`;
- re-read the exact execution authority;
- verify the machine authority against the current executable path;
- fail closed on mismatch or ambiguity.

A local API key being present does not itself grant execution permission.
