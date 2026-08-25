# AGENTS

Canonical repository:

`haozhouliuliuliu/kline-playbook-engine`

This file contains stable operating rules for people and AI working on this repository. Current product/state live in `PROJECT_DIRECTION.md` and `CURRENT_STATE.md`.

## Start here

1. Refresh GitHub `main`.
2. Read `00_READ_FIRST.md`.
3. Follow its active-core takeover order.
4. Treat current GitHub `main` as the only dynamic fact source.
5. Load only the current task-specific authority/evidence after the active core.

## Product boundary

- This is a single-purpose China-futures trading project.
- `MODEL_SOURCE = DEEPSEEK_ONLY` unless the Owner explicitly changes model direction.
- Jianghe source truth, DeepSeek working hypotheses and project-validated extensions remain separately labeled.
- UNKNOWN, contradiction or insufficient confirmation must allow `WAIT` / `NO_TRADE`.
- Persistent memory is project-owned, bounded and auditable.
- DeepSeek may generate hypotheses but may not self-promote them into active trading policy.
- Hard risk, broker/account truth, order lifecycle, reconciliation and safety remain deterministic project systems.

## Owner collaboration

The Owner is not expected to perform ordinary engineering work.

Project brain should:

- default to Chinese and plain language for Owner-facing explanations;
- make ordinary engineering, test, documentation and integration decisions autonomously;
- challenge technically weaker proposals when a better approach exists;
- ask the Owner only for material product/research direction, semantic freezes, permanent risk rules, real-money/broker/account actions, paid spend without current authority, or irreversible external decisions.

Do not create artificial authorization loops for already-approved work.

## Workers and Git

- Exactly one integration lane may modify `main` and shared authority at a time.
- Parallel workers use separate worktrees/branches.
- Do not point two active workers at one worktree.
- Strong reasoning workers are reserved for architecture, research design and difficult cross-module work when useful.
- Ordinary mechanical work may use cheaper reliable workers.
- WorkBuddy is treated as local/no-GitHub unless current tool evidence proves otherwise.
- Worker reports are not authority. Accepted facts are written to GitHub by the integration lane.
- Protect user files/worktrees; never use destructive local cleanup merely to make a command pass.

## Tool/runtime admission

For material external frameworks, tools and models use:

- `CANDIDATE` — plausible, not verified for this project;
- `VERIFIED` — actually tested against project requirements;
- `ADOPTED` — formally selected for a defined role.

Current DeepSeek Harness status is governed by `PROJECT_DIRECTION.md` / `CURRENT_STATE.md`.

## Research and evidence

- Future information must not enter a decision-time observation.
- Discovery/tuning evidence remains separate from independent validation/holdout evidence.
- Profit is not identical to process correctness; loss is not identical to process error.
- New DeepSeek-derived trading ideas follow the learning lifecycle in `PROJECT_DIRECTION.md`.
- Source/evidence records remain immutable factual lineage.

## Verification

For code changes use the smallest sufficient focused checks plus normal repository CI.

Default broad regression command:

`python -m unittest discover -s tests`

Also use when applicable:

- `python -m compileall -q src tools tests`
- deterministic artifact checks
- `git diff --check`
