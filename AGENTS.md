# AGENTS

Canonical repository identity:

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

## Bootstrap

1. Read `00_READ_FIRST.md` **first**.
2. Fetch current `main` HEAD.
3. Follow the active takeover order declared by `00_READ_FIRST.md`; that order begins with `OWNER_COLLABORATION_CONTRACT.md` after the bootstrap file itself.
4. Use the exact canonical repository identity above for GitHub operations; do not reconstruct it from memory.

If a GitHub operation unexpectedly returns `404`, first compare the requested repository slug character-for-character with the canonical identity before retrying. A connector 404 by itself is not evidence that the private repository, branch, PR or artifact was deleted.

## Mandatory project rules

- This is a clean-room project. Other projects and project-external chat are not project fact sources.
- Current GitHub `main` is the sole dynamic project fact source. Chat, Project uploads and handoff prose never override current authority.
- Follow the current consolidated architecture in `ARCHITECTURE_BASELINE.md` + the Jianghe AI ADR. Do not revert to historical “LLM offline only” wording from old Git history.
- Follow `CURRENT_STATE.md` authorization locks and the current active Stage-A plan/attempt authorities named by `00_READ_FIRST.md`.
- Jianghe is the sole current V1 trading knowledge source while `STRATEGY_SOURCE_EXPANSION=PAUSED_FOR_V1`.
- UNKNOWN / contradiction / unsupported or unfamiliar market state must allow WAIT / NO_TRADE; do not invent source semantics to force a trade.
- External tools/frameworks/models remain CANDIDATE until project evidence verifies/adopts them.
- No candidate outcome, Validation, Final, real Shadow, broker order or real-money action without current authority.
- Protect Git/worktree/user files; no destructive cleanup merely to make a command succeed.

## Live Stage-A safety rules

When the current Stage-A live fidelity funnel is active:

- Refresh the fixed live remote ledger before stating current attempted slots or accounting.
- A durable `NETWORK_ATTEMPT_STARTED` makes that slot attempted; **never rerun it**, even after crash/cancel/terminal persistence failure.
- `AUTOMATIC_RETRY=FORBIDDEN` and `AUTOMATIC_NEXT_SLOT=FORBIDDEN`.
- Production live state ref is fixed by current authority; caller-selected live refs are forbidden.
- Do not mutate historical Stage-A state refs after they are superseded/declared immutable.
- Provider elimination/fatal-stop decisions come from the frozen funnel/evaluator authority, not workflow convenience.
- An eliminated provider receives no further Stage-A calls and no recycled Stage-B budget.
- Paid wallet funding is not the same as model API consumption accounting.
- No live call may be used merely as a balance probe.

## Parallel / worktree rules

- Use isolated branches/worktrees for parallel workers.
- **Never point two active workers at the same worktree.**
- Exactly one integration lane may advance `main` and shared authority/state files.
- Before creating/reusing a worktree, inspect `git worktree list`, target branch and current remote state.
- Parallel workers must not edit `CURRENT_STATE.md`, `00_READ_FIRST.md`, `PROJECT_BRAIN_RUNTIME_BRIEF.md`, `PROJECT_HANDOFF_CURRENT.md`, frozen protocols, Owner evidence or other integration-owned authority unless explicitly assigned.
- If WorkBuddy/local worker cannot access GitHub, its work remains local; a GitHub-capable lane must protect/commit/integrate it.
- Do not parallelize tasks whose meaning depends on an unresolved frozen research-semantic decision or Owner gate.

## Worker use

- Codex/Sol is appropriate for high-value architecture, research-design implementation and complex cross-module integration in an isolated worktree.
- Ordinary mechanical engineering/testing/review may use cheaper reliable workers when available.
- WorkBuddy remains local/no-GitHub unless current tool evidence proves otherwise.
- Workers do not become project authority merely by reporting success; project brain reviews and the integration lane writes accepted facts to GitHub.

## Verification

Canonical full-suite command:

```text
python -m unittest discover -s tests -v
```

Also use relevant focused tests, `python -m compileall -q src tools tests`, deterministic artifact rebuild/checks and `git diff --check` for integration work when applicable.
