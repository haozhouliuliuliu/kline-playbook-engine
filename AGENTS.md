# AGENTS

Canonical repository:

`haozhouliuliuliu/kline-playbook-engine`

This file contains only stable operating rules for people/AI working on this repository. Current product/state live in `PROJECT_DIRECTION.md` and `CURRENT_STATE.md`.

## Start here

1. Refresh GitHub `main`.
2. Read `00_READ_FIRST.md`.
3. Follow its small active-core takeover order.
4. Treat current GitHub `main` as the only dynamic fact source.
5. Do not load obsolete Git history, old chats or deleted plans unless a specific forensic task requires them.

## Product boundary

- This is a single-purpose futures-trading project.
- DeepSeek is the only active model source unless the Owner explicitly changes that decision.
- Jianghe source truth, DeepSeek working hypotheses and project-validated extensions must remain separately labeled.
- UNKNOWN / contradiction / insufficient confirmation must allow `WAIT` / `NO_TRADE`.
- Persistent memory is project-owned and auditable; it is not an unbounded chat transcript.
- DeepSeek may generate hypotheses but may not self-promote them into active trading policy.
- Hard risk, broker/account truth, order lifecycle, reconciliation and safety remain deterministic/project-owned.

## Owner collaboration

The Owner is not expected to perform ordinary engineering work.

Project brain should:

- default to Chinese and plain language for Owner-facing explanations;
- make ordinary engineering/test/documentation/integration decisions autonomously;
- independently challenge technically weaker proposals rather than merely agree;
- ask the Owner only for material product/research direction, semantic freezes, permanent risk rules, real-money/broker/account actions, paid spend that lacks authority, or other irreversible external decisions.

Do not create artificial authorization loops for already-approved work.

## Workers and Git

- Exactly one integration lane may modify `main` and shared authority at a time.
- Parallel workers use different worktrees/branches.
- Do not point two active workers at one worktree.
- Codex/strong reasoning workers are reserved for architecture, research design and difficult cross-module work when useful.
- Ordinary mechanical work may use cheaper reliable workers.
- WorkBuddy is treated as local/no-GitHub unless current tool evidence proves otherwise; never assign it mandatory remote GitHub steps.
- Worker reports are not authority. Accepted facts are written to GitHub by the integration lane.
- Protect user files/worktrees; never use destructive cleanup merely to make a command pass.

## Tool/runtime admission

For material external frameworks/tools/models use:

- `CANDIDATE` — plausible, not verified for this project;
- `VERIFIED` — actually tested against project requirements;
- `ADOPTED` — formally selected for a defined role.

DeepSeek Harness is currently governed by `PROJECT_DIRECTION.md` / `CURRENT_STATE.md`; do not infer adoption from its presence in external docs.

## Research and evidence

- Future information must not enter a decision-time observation.
- Discovery/tuning evidence must remain separate from independent validation/holdout evidence.
- Profit is not identical to process correctness; loss is not identical to process error.
- New DeepSeek-derived trading ideas must follow the learning lifecycle defined in `PROJECT_DIRECTION.md`.
- Historical source/evidence must never be rewritten to make the current theory look cleaner.

## Verification

For code changes use the smallest sufficient focused checks plus normal repository CI.

Default full local regression command when a broad change justifies it:

`python -m unittest discover -s tests`

Also use, when applicable:

- `python -m compileall -q src tools tests`
- deterministic artifact checks
- `git diff --check`

Do not repeatedly run expensive full suites for documentation-only edits when no executable path changed.
