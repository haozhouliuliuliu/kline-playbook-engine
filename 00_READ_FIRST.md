# 00_READ_FIRST

Canonical repository:

`haozhouliuliuliu/kline-playbook-engine`

GitHub current `main` is the only dynamic project fact source.

This file owns **navigation only**. It must not duplicate current work-package, phase, lock, paid-slot or next-task values.

## Fresh-conversation takeover

Read in this stable order:

1. `00_READ_FIRST.md`
2. `PROJECT_GOVERNANCE.md`
3. `AGENTS.md`
4. `ARCHITECTURE_BASELINE.md`
5. `TOOL_REGISTRY.md`
6. `PROJECT_DIRECTION.md`
7. `PROJECT_BRAIN_RUNTIME_BRIEF.md`
8. `CURRENT_STATE.md`
9. the exact current task-specific Owner decisions / machine authorities / evidence referenced by `CURRENT_STATE.md`

Only load additional architecture/research/evidence files when the current task actually needs them.

## What each file owns

- `PROJECT_GOVERNANCE.md` — stable governance, authority precedence and one-concern/one-owner map;
- `AGENTS.md` — worker/worktree/repository operating procedure;
- `ARCHITECTURE_BASELINE.md` — long-lived system architecture;
- `TOOL_REGISTRY.md` — project tool/provider status, pins, credential-location seams and revalidation triggers;
- `PROJECT_DIRECTION.md` — product/research direction;
- `PROJECT_BRAIN_RUNTIME_BRIEF.md` — refresh procedure;
- `CURRENT_STATE.md` — **sole volatile owner** for current activity, work package, phase, locks and next task;
- exact Owner/machine authority — exact paid/consequential execution permission;
- evidence — what actually happened.

Do not use README, chat, stale branches, deleted handoffs or old state snapshots to override these owners.

## Takeover discipline

A fresh project brain must not infer current state from the stable files.

Read `CURRENT_STATE.md`, then follow its exact current authority/evidence pointers.

If a stable file contains a copied volatile current-state value, treat it as an authority-drift defect rather than a second source of truth.

## First takeover report

The first report should state only:

- current `main` HEAD;
- whether canonical owners are internally consistent;
- current product direction;
- relevant `CANDIDATE / VERIFIED / ADOPTED` tool/runtime status and credential seam;
- current activity/work package/phase from `CURRENT_STATE.md`;
- exact current execution/paid boundary from the task-specific authority;
- current locks and next task from `CURRENT_STATE.md`;
- any contradiction or broken authority reference.

First takeover is read-only unless the Owner explicitly directs otherwise.
