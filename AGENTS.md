# AGENTS

Canonical repository:

`haozhouliuliuliu/kline-playbook-engine`

This file owns scoped worker/repository operating procedure only.

Stable governance and authority ownership:

`PROJECT_GOVERNANCE.md`

Current dynamic project state:

`CURRENT_STATE.md`

## Start here

1. Refresh GitHub `main`.
2. Read `00_READ_FIRST.md`.
3. Follow its active takeover order.
4. Treat current GitHub `main` as the only dynamic fact source.
5. Read task-specific authority/evidence pointed to by `CURRENT_STATE.md`.

Do not reconstruct current state from chat, stale branches or old handoffs.

## Workers and Git

- Exactly one integration lane may modify `main` and shared authority at a time.
- Parallel workers use separate worktrees/branches.
- Do not point two active workers at one worktree.
- Before integration, refresh current `main` and reconcile shared-authority changes from the actual current parent.
- Worker reports are not authority. Accepted facts are written to canonical GitHub authority/evidence by the integration lane.
- Protect user files/worktrees; never use destructive local cleanup merely to make a command pass.

## Owner interaction

Follow `PROJECT_GOVERNANCE.md` for Owner gates and authority precedence.

For ordinary engineering/tests/docs/integration under existing authority, proceed autonomously.

Do not ask the Owner to perform routine technical work that the project brain or worker can safely perform.

## Tool/runtime use

Project tool/provider/framework status, pins, credential-location seams and revalidation triggers live only in:

`TOOL_REGISTRY.md`

Do not infer tool adoption from local installation, environment variables, worker availability or chat history.

Secret values must never be printed, logged, committed or copied into authority.

## Research and evidence

- Future information must not enter decision-time observations.
- Discovery/tuning evidence remains separate from independent validation/holdout evidence.
- Profit is not identical to process correctness; loss is not identical to process error.
- Source truth, model hypotheses and project-validated policy remain separately labeled.
- Source/evidence records remain immutable factual lineage.
- Frozen research semantics may be changed only by appropriate Owner authority.

## Verification

For code changes use the smallest sufficient focused checks plus normal repository CI.

Default broad regression command:

`python -m unittest discover -s tests`

Also use when applicable:

- `python -m compileall -q src tools tests`;
- deterministic artifact checks;
- authority-consistency checks;
- `git diff --check`.

Verification passing does not itself grant paid/provider, paper, broker/account or real-money authority.
