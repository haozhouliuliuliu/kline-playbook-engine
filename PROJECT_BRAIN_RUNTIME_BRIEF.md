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
