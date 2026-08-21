# Holy Grail Identity Determinism Audit V0.1

**Status:** REPAIRED / CONSISTENT

**Date:** 2026-08-21

**Repository:** `haozhouliuliuliu/kline-playbook-engine`

**Branch:** `repair/holy-grail-identity-determinism-v01` (created from current main
`35295bda297fd8794d6a961a7808d96bc2d963b0`)

---

## Result summary

```text
ROOT_CAUSE=STALE_NON_AUTHORITATIVE_IDENTITY_VALUES_EDIT_WITHOUT_BUILDER_REGENERATION
AUTHORITATIVE_FINAL_IDENTITY_SET=be8872baf56983385636a4480889ba2e006578912c565bf824694aafb861c67b|14fbde5279f43e8dfa96241f35ca84c806f6b4e434a1784bafe6f66d1f8c1fce|333ca10c58adabe6c5348cd95d3ef5d19b2450fdf0ff51b0339993129f69b6b4|d2093ca202c465b5bedc77ad6cf46b6a5776077be29bbfe67ce093669b7738e8
SEMANTIC_CHANGE_OCCURRED=NO
IDENTITY_DRIFT_BUG=YES
REPAIRED=YES
```

The drift is **Category C/D** (Task 1 taxonomy): the identity-bearing artifacts at
current main had been overwritten with values that no builder produces, without any
semantic change, and the artifact dependency graph was not regenerated. The builders
and all semantic inputs are byte-identical across the whole range; the builders are
deterministic and produce one canonical identity set. The repair re-generated every
derived artifact from its authoritative builder and pinned the chain with
anti-regression tests.

---

## 1. What was asked

- `HOLY_GRAIL_IDENTITY_DETERMINISM_AND_REGRESSION_REPAIR_V0_1`
- Determine why Holy Grail identities changed across three main commits
  (`3f95b80`, `e87d899`, `35295bd`) with no Holy Grail strategy semantic change.
- Recompute the authoritative identities from current-main authority
  (source claims, Playbook V0.4, machine code, approved parameters, feature
  implementation, protocol, scope), never by restoring an old SHA.
- Fix the builder / identity construction and all derived artifacts if a bug
  exists; otherwise only add regression tests and formal evidence.
- Add anti-regression tests and record evidence.
- Commit and push to `repair/holy-grail-identity-determinism-v01`; never touch main.

No strategy research, no candidate-outcome access, no research-semantic change, and no
network access were performed. No real money / broker / candidate outcome access.

---

## 2. Commit topology and changed surface

The three compared commits are strictly linear ancestors:

```text
3f95b80d8240fc44ffc4ac7c917ce00615bde91a   integrate: close pre-shadow execution semantics v0.3
        |
        v
e87d899998bcafe6442e19e2eee5b8db962a0005   research: record NR7 V0.2 source resolution
        |
        v
35295bda297fd8794d6a961a7808d96bc2d963b0   research: complete China-first playbook promotion wave  (current main)
```

Across the whole range `3f95b80..35295bd`:

- **No `src/` change** and **no `tools/` change** (verified with
  `git diff --name-only` over `tools/` and `src/`).
- **No builder-input change**: the Holy Grail SOURCE_ONLY session evidence and source
  bundle files are unchanged.
- The only identity-affecting changes are in commit `35295bd`, which edited two
  evidence JSON files (identity fields only) plus docs and one test:

  - `docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_4.json` (6 lines:
    `contract_identity`, `machine_identity`, `required_feature_versions[0]`)
  - `docs/evidence/HOLY_GRAIL_PRIMARY_FREEZE_V0_1.json` (8 lines:
    `strategy_identity`, `strategy_version`, `primary_contract_identity`,
    `feature_versions[0]`)
  - `CURRENT_STATE.md` carries the same drifted `HOLY_GRAIL_PRIMARY_STRATEGY_IDENTITY`.

Also present at main (pre-existing staleness, unrelated to `35295bd` but part of the
PreShadow dependency chain):

- `docs/evidence/PRE_SHADOW_GATE_V0_2.json` — `gate_module_sha256` stale
  (`45e0807…`) vs. actual `src/pre_shadow_gate.py` sha256 (`3e073ed…`).
  `PRE_SHADOW_GATE_V0_1.json` is consistent and was correctly regenerated.

---

## 3. Evidence that no semantic change occurred

| Input | `3f95b80` | `e87d899` | `35295bd` |
| --- | --- | --- | --- |
| `src/holy_grail_machine.py` blob | `45b1603362…` | `45b1603362…` | `45b1603362…` |
| `src/technical_features.py` blob | `bef369e0a8…` | `bef369e0a8…` | `bef369e0a8…` |
| `src/pre_shadow_gate.py` blob | `d2a7c7997d…` | `d2a7c7997d…` | `d2a7c7997d…` |
| `tools/build_raschke_holy_grail_playbook_contract_draft_v0_4.py` | unchanged | unchanged | unchanged |
| `tools/build_holy_grail_primary_freeze_v0_1.py` | unchanged | unchanged | unchanged |
| SOURCE_ONLY session evidence | unchanged | unchanged | unchanged |
| machine `code_hash` in contract JSON | `250034797e…` | `250034797e…` | `250034797e…` |
| machine `environment_hash` in contract JSON | `9b4f429566…` | `9b4f429566…` | `9b4f429566…` |
| `parameter_hash` in freeze JSON | `aa41f53232…` | `aa41f53232…` | `aa41f53232…` |

The machine `code_hash`, `environment_hash` and `parameter_hash` — the fields that
would move if code or parameters changed — are **unchanged** at current main. The
drifted fields are exactly the *derived* identities (`contract_identity`,
`machine_identity`, feature identity, `strategy_identity`), which are recomputed
compositions, not independent inputs.

---

## 4. Root cause

**Classification:** Category C (stale artifact overwritten with non-authoritative
values) + Category D (artifact dependency graph not regenerated); the same effect as
Category B in that the drift is non-semantic.

**Mechanism:** commit `35295bd` replaced the derived identity fields in the Primary
Freeze and V0.4 Contract JSON with values that the builders do not compute, and let
the PreShadow gate V0.2 carry a stale module hash. The builders were not re-run, so
the checked-in artifacts stopped matching the deterministic builder output. The
pre-existing determinism tests
(`test_holy_grail_primary_freeze.test_checked_in_freeze_is_deterministic_and_outcome_locked`
and
`test_raschke_holy_grail_v04_machine_ready.test_checked_in_v0_4_artifact_is_deterministic`)
**fail on current main**, which independently proves the drift.

The e87d899 identity set (which the current builders reproduce exactly) is the
authoritative set; it was never semantically invalidated.

---

## 5. Authoritative identity set (recomputed from authority, not restored)

Computed by running the current-main builders (not by copying any old SHA):

```text
feature_identity           = 333ca10c58adabe6c5348cd95d3ef5d19b2450fdf0ff51b0339993129f69b6b4
contract_identity          = be8872baf56983385636a4480889ba2e006578912c565bf824694aafb861c67b
machine_identity           = 14fbde5279f43e8dfa96241f35ca84c806f6b4e434a1784bafe6f66d1f8c1fce
strategy_identity          = d2093ca202c465b5bedc77ad6cf46b6a5776077be29bbfe67ce093669b7738e8
strategy_version           = pc-0.4.0-be8872baf56983385636a4480889ba2e006578912c565bf824694aafb861c67b
parameter_hash             = aa41f53232f44255e9a012b93e1890d889bf4a0a986dc5e4f754dbb1c46d1659
pre_shadow_gate.py sha256   = 3e073ed3e38cdefc3765d04a82738d493f2c41761e2298a1b2f1036a4dd82b04
PRE_SHADOW_GATE_V0_1 identity = cbcc6801820e6d0009ff4d051cd3ec025aa5f9a22b986ad9902d1aa34b310340
PRE_SHADOW_GATE_V0_2 identity = 9aa97528bfc3dfa14a5035db7347c5464f88142b785efeb6940754ef88767703
```

### 5.1 Determinism verification (Task 2)

Executed with a probe that runs the actual builders:

| Check | Result |
| --- | --- |
| Same inputs, 10 consecutive in-process runs | identical |
| Different cwd (unrelated directory) | unchanged |
| Different temp/worktree absolute path (copied `src` + `tools` + evidence) | unchanged |
| `PYTHONHASHSEED=0` (subprocess) | unchanged |

Why the identities are path/order/mtime-independent by construction:

- `ArtifactBinding.identity_id` (feature / machine bindings) is a canonical hash of
  `{artifact_kind, artifact_reference, sha256(content bytes), byte_size,
  declared_version}` — no absolute path, no mtime, no environment value.
- `contract_identity` / `machine_identity` / `primary_selection_identity` /
  `claim_identity` / `branch_identity` / `surface_identity` hash canonical
  `sort_keys=True` JSON over `sorted()` tuple collections.
- `required_feature_versions` and `parameter_identities` are enforced sorted+unique
  by `_canonical_tuple`.
- No identity binds an absolute local path, mtime, temp worktree path, unordered
  dict/set, or machine-specific environment value. No self-referential hash on the
  generated artifact.

---

## 6. Fix applied (Task 3)

No builder code defect was found — the builders are correct and deterministic. The
defect was that the checked-in artifacts did not match the builders. Repair = re-run
the authoritative builders (no hand-editing of JSON):

1. `tools/build_raschke_holy_grail_playbook_contract_draft_v0_4.py`
   → regenerated `docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_4.json`
   (contract/machine/feature identities restored to the authoritative set).
2. `tools/build_holy_grail_primary_freeze_v0_1.py`
   → regenerated `docs/evidence/HOLY_GRAIL_PRIMARY_FREEZE_V0_1.json`
   (strategy/contract/feature identities + `strategy_version` restored).
3. `tools/build_pre_shadow_gate_v0_2.py`
   → regenerated `docs/evidence/PRE_SHADOW_GATE_V0_2.json`
   (`gate_module_sha256` corrected to the actual module hash).
4. `CURRENT_STATE.md` → `HOLY_GRAIL_PRIMARY_STRATEGY_IDENTITY` corrected from the
   drifted `fba1aec…` to the authoritative `d2093ca…`.

The regenerated files are byte-identical to the builder output (verified by the
determinism tests). The historical drifted values remain in the immutable commit
history (`35295bd`); this audit does not rewrite history.

---

## 7. Anti-regression tests (Task 4)

Added `tests/test_holy_grail_identity_determinism.py` (12 tests, all passing):

| Requirement | Test |
| --- | --- |
| same semantic inputs -> same identity | `test_same_semantic_inputs_yield_identical_identity` |
| semantic input change -> identity changes | `test_semantic_input_change_changes_identity`, `test_semantic_parameter_change_changes_strategy_identity` |
| irrelevant cwd change -> unchanged | `test_irrelevant_cwd_change_is_unchanged` |
| temp/worktree path change -> unchanged | `test_temp_worktree_path_change_is_unchanged` |
| artifact generation/collection order -> unchanged | `test_collection_ordering_does_not_change_identity` |
| rerun builder -> byte-identical output | `test_rerun_builder_is_byte_identical_to_checked_in_artifacts` |
| Primary Freeze references current contract identity | `test_primary_freeze_references_current_contract_identity` |
| StrategyIdentity references current machine/contract identity | `test_strategy_identity_references_current_machine_and_contract_identity` |
| CURRENT_STATE identity == formal freeze artifact identity | `test_current_state_matches_formal_freeze_identity` |
| PreShadow gate references consistent identity | `test_pre_shadow_gate_references_consistent_identity` |
| pinned authoritative identity set | `test_authoritative_identity_set_is_pinned` |

`test_authoritative_identity_set_is_pinned` additionally locks the exact current
hashes so that a consistent two-file hand-edit (the drift pattern) is also caught.

---

## 8. Verification

```text
Focused: python -m unittest tests.test_holy_grail_identity_determinism tests.test_holy_grail_primary_freeze tests.test_raschke_holy_grail_v04_machine_ready  -> OK (32 tests)
Full:    python -m unittest discover -s tests -v                                  -> PASS
Compile: python -m compileall -q src tools tests                                  -> PASS
git diff --check                                                                  -> clean
```

No candidate outcome, credentials, or raw market data are included in this repair.

---

## 9. Honest boundaries

- The exact provenance of the drifted `fba1aec / 76825d1 / 3c3dfff / 7129969`
  values (which environment/editor produced them) is not reconstructed; the
  authoritative determination is what matters and is fully evidenced: they do not
  match any builder output and are therefore not authoritative.
- The PreShadow V0.2 `gate_module_sha256` staleness predates `35295bd`; it was fixed
  as part of the "PreShadow dependencies" requirement.
- Historical evidence is preserved as committed; only current-main artifacts were
  regenerated from their builders.
