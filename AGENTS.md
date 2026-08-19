# AGENTS

Canonical repository identity:

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

Repository-identity operating rule:
- For GitHub connector/API operations, copy the exact canonical `REPOSITORY_FULL_NAME` above or obtain the repository identity from already-fetched repository metadata. Do not reconstruct or retype the owner/repository slug from memory.
- If an expected repository operation returns `404 Not Found`, first compare the requested slug character-for-character against the canonical identity above. Correct that identity before any retry; do not probe guessed spelling variants.
- A repository-name typo is an operational defect. Do not narrate repeated typo/retry cycles to the Owner when the canonical identity can decide the issue deterministically.

Read first, in this order:
1. `OWNER_COLLABORATION_CONTRACT.md`
2. `ARCHITECTURE_BASELINE.md`
3. `CURRENT_STATE.md`
4. `CROSS_PROJECT_OPERATING_CONTRACT.md`
5. `TOOL_REGISTRY.md`

Project-specific mandatory rules:
- This is a clean-room project. Other projects and project-external chat are not project fact sources.
- Preserve Skeleton v1.0 unless a concrete fatal flaw is established through project authority.
- Follow `CURRENT_STATE.md` authorization boundaries.
- External tools/frameworks remain candidates until this project explicitly verifies and adopts them.
- No real broker order submission or real-money trading without explicit Owner authorization.
- Protect existing Git/worktree/user files; no destructive cleanup.
- For parallel work, use isolated worktrees/branches. Exactly one integration lane owns `main` and shared authority/state files.
- Before creating or reusing a parallel worktree, inspect `git worktree list`, the target branch, and current remote state. Do not blindly recreate an existing branch/worktree or delete a retained review worktree just to make a command succeed.
- Parallel workers must not push `main` or independently edit `CURRENT_STATE.md`, `00_READ_FIRST.md`, frozen protocols, Owner evidence, or other integration-owned authority unless explicitly assigned that ownership.
- Do not parallelize work whose meaning depends on an unresolved frozen research-semantic decision or Owner gate.

Canonical bootstrap verification path:
`python -m unittest discover -s tests -v`
