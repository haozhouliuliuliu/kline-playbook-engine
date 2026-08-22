# AGENTS

Canonical repository identity:

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

## Bootstrap

1. Read `OWNER_COLLABORATION_CONTRACT.md`.
2. Read `00_READ_FIRST.md` and follow its current authority order.
3. Use the exact canonical repository identity above for GitHub operations; do not reconstruct it from memory.

If a GitHub operation unexpectedly returns `404`, first compare the requested repository slug character-for-character with the canonical identity before retrying.

## Mandatory project rules

- This is a clean-room project. Other projects and project-external chat are not project fact sources.
- Follow the current consolidated architecture in `ARCHITECTURE_BASELINE.md` + the Jianghe AI ADR. Do not revert to historical “LLM offline only” wording from old Git history.
- Follow `CURRENT_STATE.md` authorization locks.
- Jianghe is the sole current V1 trading knowledge source while `STRATEGY_SOURCE_EXPANSION=PAUSED_FOR_V1`.
- UNKNOWN / contradiction / unsupported or unfamiliar market state must allow WAIT / NO_TRADE; do not invent source semantics to force a trade.
- External tools/frameworks/models remain CANDIDATE until project evidence verifies/adopts them.
- No candidate outcome, Validation, Final, real Shadow, broker order or real-money action without current authority.
- Protect Git/worktree/user files; no destructive cleanup merely to make a command succeed.

## Parallel / worktree rules

- Use isolated branches/worktrees for parallel workers.
- **Never point two active workers at the same worktree.**
- Exactly one integration lane may advance `main` and shared authority/state files.
- Before creating/reusing a worktree, inspect `git worktree list`, target branch and current remote state.
- Parallel workers must not edit `CURRENT_STATE.md`, `00_READ_FIRST.md`, `PROJECT_BRAIN_RUNTIME_BRIEF.md`, frozen protocols, Owner evidence or other integration-owned authority unless explicitly assigned.
- If WorkBuddy/local worker cannot access GitHub, its work remains local; a GitHub-capable lane must protect/commit/integrate it.
- Do not parallelize tasks whose meaning depends on an unresolved frozen research-semantic decision or Owner gate.

## Verification

Canonical full-suite command:

```text
python -m unittest discover -s tests -v
```

Also use relevant focused tests, `python -m compileall -q src tools tests`, and `git diff --check` for integration work when applicable.
