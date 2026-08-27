# Jianghe Replay V0.1 — Canonical Dataset Local Restoration Verification

Status: `ORIGINAL_ACCEPTED_DATASET_FOUND_AND_VERIFIED__NO_REBUILD__NO_DOWNLOAD__NO_PROVIDER_CALL`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

## Purpose

Close the `FINAL_PREFLIGHT_BLOCKER` (missing canonical dataset) by locating and
mechanically verifying the existing original accepted local canonical dataset,
then pointing preflight/runner at it via explicit `--manifest` and
`--parquet-root` paths. This is **restoration / path resolution**, not a new
dataset, not a research-design change, and not a new Owner decision.

## Dataset found (original, in place)

The accepted canonical dataset already exists locally in the project's own
ignored `data/canonical/` directory of the current repository worktree:

- manifest: `data/canonical/manifest.json`
- parquet root: `data/canonical/parquet/`
- catalog: `data/canonical/catalog.sqlite`

The dataset was NOT copied, moved, rebuilt, re-downloaded, or re-acquired.
No symlink/junction was created. The default relative paths are used, so the
earlier worktree had no manifest only because `data/canonical/` is git-ignored
and the fresh preflight was previously run from a path without the local data.

## Mechanical identity verification (project code, zero cost)

Using the project's own revalidated exact-slice seal verification
(`src/replay_v0_1_qualified_manifest.py::_verify_raw_accepted_manifest`) against
`docs/evidence/CANONICAL_CORPUS_IDENTITY.json`:

```
MANIFEST_IDENTITY_MATCH 7510a4a943e85c9be256e62971b5a64d64e9976c2b01c9f5d0fe07b1c6c8d324
PARTITION_COUNT 32980
CANONICAL_CORPUS_IDENTITY 1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
PARQUET_FILES 32980
VERIFICATION=PASS
```

- accepted manifest identity matches: `7510a4a943e85c9be256e62971b5a64d64e9976c2b01c9f5d0fe07b1c6c8d324` — PASS
- canonical corpus identity matches: `1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8` — PASS
- partition count `32,980` matches accepted corpus authority — PASS
- Parquet file count `32,980` matches accepted inventory — PASS
- `cu` product partitions: `5,820` (matches accepted `cu` inventory) — PASS
- exact frozen slice `cu` / `SHFE.cu2406` parquet present (`year=2024`, `108` files) — PASS
- `CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json` present — PASS
- `data/canonical/catalog.sqlite` present — PASS
- no partial/truncated-copy indicator found; partition identity set verifies against
  the accepted raw manifest identity — PASS

## Zero-cost preflight (explicit paths) — PASS

Run with the pinned canonical pyarrow environment (Python 3.12 + probe site-packages
`pyarrow 25.0.1` / `tzdata 2026.3`) and a new empty state directory:

```text
python tools/preflight_replay_v0_1_provider_smoke.py \
  --manifest data/canonical/manifest.json \
  --parquet-root data/canonical/parquet \
  --state-dir <new-empty-preflight-state>
```

Exit code `0`. Deterministic blueprint written to:

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_FINAL_PREFLIGHT_BLUEPRINT_2026-08-27.json`

Verified blueprint facts:

- product / contract: `cu` / `SHFE.cu2406`
- exact slice seal identity: `e9bbd232fd05d320a24c80ac5570a94abdf6d4c3a167cdd5c46f4426a6c84156`
- slice identity: `347291481968b1884635a11aa1da985d9aad1b3fb854a16087bbca662bd85a06`
- model: `deepseek-v4-flash-vision-exp`; provider: `deepseek`
- Harness: version `0.1.1-rc.2`, commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project transport patch: `integrations/deepseek-harness/`
- prompt contract: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`
- exactly 3 governed wakes (`call_1/call_2/call_3`) each carrying both
  `logical_wake_selection_identity` and `wake_identity`, exact close times, and
  exactly 4 causal PNG SHA-256 per call
- `real_provider_calls = 0`

## Evidence boundary

- No provider call, network request, credential read, or machine-authority
  reseal/activation occurred during restoration verification.
- The previous missing-data blocker is CLOSED by path resolution.
- The pinned pyarrow probe environment is the canonical `pyarrow 25.0.1` /
  `tzdata 2026.3` set already recorded in `requirements-canonical.txt` and
  `TOOL_REGISTRY.md` (PyArrow ADOPTED, role canonical normalized storage / replay
  read path).

## Source of truth

- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`
- `docs/evidence/CANONICAL_CORPUS_IDENTITY.json`
- `src/replay_v0_1_qualified_manifest.py`
- `tools/preflight_replay_v0_1_provider_smoke.py`
