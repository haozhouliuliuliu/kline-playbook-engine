# AGENTS

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

Canonical bootstrap verification path:
`python -m unittest discover -s tests -v`
