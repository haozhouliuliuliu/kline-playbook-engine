# Jianghe Replay V0.1 — Post-repair Revalidation Final Preflight Blocker

Status: `FAILCLOSED_BEFORE_PROVIDER_CAPABILITY__NO_PROVIDER_ATTEMPT`

Date: `2026-08-27`

## Exact failed zero-cost check

On canonical `main` commit `8bd64338966bdbb555dbe7bf5bcef1ba99fac6ac`, the required final command was run with a new empty state directory:

```text
python tools/preflight_replay_v0_1_provider_smoke.py --state-dir <new-empty-state-dir>
```

It failed before any provider, Harness, network, or credential path while loading the required frozen manifest:

```text
FileNotFoundError: data/canonical/manifest.json
```

## Evidence boundary

- `data/canonical/manifest.json` is absent in the fresh current-main integration worktree.
- It is also absent in the existing repository worktree.
- `git ls-files` has no tracked manifest or canonical Parquet content; `.gitignore` excludes `/data/canonical/`.
- No substitute dataset was selected and no external acquisition/rebuild was performed.
- `POST_REPAIR_REVALIDATION_PROVIDER_CALLS = 0`; `POST_REPAIR_REVALIDATION_PROVIDER_ATTEMPTS = 0`.
- No V0.3 authority was created, resealed, activated, or revoked because the preflight could not establish exact wake identities and causal image hashes.

The missing local, ignored dataset prevents preservation of the authority/evidence chain required for any real call. Owner direction is required either to restore the exact verifiable frozen artifact or to grant a governed rebuild/acquisition authority. Full V0.1 remains locked.
