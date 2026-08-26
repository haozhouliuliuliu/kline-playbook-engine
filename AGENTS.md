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

## Worker routing / utilization

- The project brain remains the single process/orchestration owner.
- VS Code DeepSeek Flash is the default implementation worker for non-high-end work.
- Codex is reserved for high-end / high-assurance work.
- Ordinary local-machine, repository, test, documentation, bug-fix and parallelizable implementation work should normally be delegated to Flash when useful.
- Do not leave useful safe worker capacity idle when a task can be cleanly parallelized.
- The project brain + Flash may work concurrently on independent scopes.
- For genuinely high-end work, Codex may also be used concurrently when independent work/review adds value.
- Parallel workers MUST use separate worktrees/branches.
- Exactly one integration lane may modify `main`/shared authority.
- Never parallelize workers against the same consequential paid runtime state, machine authority, broker/account state, or other intrinsically single-owner external action.
- When a task is intrinsically serial/single-agent, use only the most appropriate worker.
- The project brain may work alone only when delegation/coordination overhead would exceed the benefit or a single coherent agent is clearly safer/faster.
- Codex must not be consumed merely to avoid idleness on routine work.

Worker-prompt discipline:

- default implementation-worker prompt language: English;
- prompts should be bounded and reference canonical GitHub authority rather than paste stable project history;
- separately state recommended worker/model family, reasoning level, and conversation mode when giving the Owner a worker task;
- detailed evidence belongs in GitHub;
- when the project brain can inspect GitHub directly, successful workers should not spend tokens reproducing long final reports;
- normal successful completion may output only `DONE`, or stop without additional prose when the interface permits;
- blockers/true Owner gates may be reported compactly.

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
