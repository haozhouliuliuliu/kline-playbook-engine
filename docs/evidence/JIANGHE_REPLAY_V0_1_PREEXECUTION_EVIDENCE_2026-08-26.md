# JIANGHE REPLAY V0.1 PREEXECUTION EVIDENCE — 2026-08-26

Status: `PASS`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

Execution mode: `OWNER_WORKSTATION_REAL_CANONICAL_CORPUS__MOCK_NO_PROVIDER`

Execution repository HEAD: `42c83537b2c19f0e47460937662f58679245989d`

Real DeepSeek/provider calls: `0`

`provider_call_authorized = false`

## Evidence provenance

This evidence seals the Owner-workstation dry-run result reported after executing the repository's merged exact-slice no-provider driver against the real local canonical Parquet corpus.

The raw output artifact remains on the Owner workstation at the reported temporary output path. Its reported SHA-256 is:

`DB17C17D197CCF7212192D03DEC1F9A78EFE8D0770E9D4B849009B3DD3816151`

The project does not reconstruct or replace that raw local artifact in GitHub. This file records the reported identities, counts and PASS result needed to establish the pre-provider boundary.

## Exact execution

Python: `3.12.10`

PyArrow: `25.0.1`

Command:

```powershell
& "C:/Users/H/AppData/Local/Programs/Python/Python312/python.exe" tools/run_replay_v0_1_exact_slice_mock_dry_run.py --manifest C:/Users/H/Documents/kline-playbook-engine/data/canonical/manifest.json --parquet-root C:/Users/H/Documents/kline-playbook-engine/data/canonical/parquet --state-dir C:/Users/H/AppData/Local/Temp/replay_v0_1_mock_dry_run_20260826_083356 --output C:/Users/H/AppData/Local/Temp/replay_v0_1_mock_dry_run_output_20260826_083356.json
```

Exit code: `0`

Repository status before and after remained unchanged except for the pre-existing untracked `.workbuddy/` directory. No code, data, research design, sample, commit or push was changed by the workstation run.

## Exact sealed historical slice

- product: `cu`
- concrete contract: `SHFE.cu2406`
- slice identity: `347291481968b1884635a11aa1da985d9aad1b3fb854a16087bbca662bd85a06`
- exact slice seal identity: `e9bbd232fd05d320a24c80ac5570a94abdf6d4c3a167cdd5c46f4426a6c84156`
- base exact slice seal identity: `8b7f86eb4bcb6bd9c3ed8e69eb43d67135a9b3deaa88967dcb6a9aaa35816fc9`
- prior-history days: `20`, from `2024-03-11` through `2024-04-09`
- burn-in days: `2024-04-10`, `2024-04-11`
- measurement days: `20`, from `2024-04-12` through `2024-05-14`

The selector remained outcome-blind and used the accepted product ordering and governed point-in-time mapping rules.

## Canonical corpus / eligibility identities

- canonical corpus identity: `1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`
- raw manifest root identity: `7510a4a943e85c9be256e62971b5a64d64e9976c2b01c9f5d0fe07b1c6c8d324`
- revalidation identity: `42e0de64e47c91156f82bbd09b53e404e93a69eebd2bc2e950c8b58c8753af32`
- qualified partitions: `32864`
- excluded partitions: `116`
- trading calendar identity: `5892a946e0b6258cb2745d46ca58b636fd60a57e43ca2b116105f3b4747130be`
- session authority root identity: `7b9f366ac2beec16eb3083578955f37b35626586d6a4d3697279aae0e43f7237`
- E07 schedule identity: `d52e92a66c0096741217ee4d0a881d1668a07a7ddc38aba6dca19efa6ccb161e`
- canonical row session-metadata identity across the bound days: `2a1168ed755460a0011ed7e9531d4e37fa7b67e7f50e71dbe2e7daab2a02dfac`

## Causal observation preflight

- fixed-5m preflight identity: `e4d29a5f6001302811c78be76565ef3095325fd46d28811c88591b6e375750a8`
- context policy identity: `98262c9ab0614b4145fe56cb8746a44d754d03a38a25584aba810991cd666371`
- context index identity: `2f26be68155766a99b3d18c8922b3d498719e80c1f4c3607630473874d3e25a3`
- constructed 4H bars: `164`
- constructed 1H bars: `286`
- constructed 15m bars: `1270`
- constructed 5m bars: `3810`

## Persistent trader / lifecycle result

- trader identity: `44039ae0212235b451ecae788901741cffce95c2436eb2f4a10e8d01422a34e9`
- runtime contract identity: `c94e20fabddbdfd51c6741914874f591589c07149b940450bed6e9932b0d35ac`
- mock transport identity: `NO_PROVIDER_DETERMINISTIC_WAIT_MOCK_V0_1`
- replay days: `22`
- governed sessions: `87`
- steps: `1998`
- wakes: `1998`
- prepared requests: `1998`
- mock transport calls: `1998`
- exact accounting: `step = wake = request = mock-call = 1998`
- R1 phase-boundary restart: `VERIFIED`
- R2 active-state restart occurred: `false`
- R2 coverage: `NOT_OBSERVED`
- final state identity: `e26a8fda696ab7d69e86de06f5403228cc627dd1051de9e04fd14fde9813793e`
- full mock dry-run identity: `4e7827c8e32348dbba43c431b52c7c5f1f95bafa62ff01c7d39675e1d64930c7`
- result: `PASS`

`R2 = NOT_OBSERVED` is not a failure. The approved Owner design explicitly requires `NOT_OBSERVED` when no persisted WATCH/CANDIDATE/IN_POSITION state occurs after the R2 arming point; the sample must not be changed to force coverage. The deterministic mock returned WAIT/SCAN throughout, so no active state was expected.

## Audit result

Total audit events: `18160`

- `DS_JOURNAL_APPEND`: `87`
- `DS_WORKING_MEMORY_MUTATION`: `9990`
- `MODEL_REQUEST_PREPARED_OFFLINE`: `1998`
- `MODEL_RESPONSE_RAW`: `1998`
- `MODEL_RESPONSE_NORMALIZED`: `1998`
- `REPLAY_INTENT_POSITION`: `1998`
- `REPLAY_SESSION_END`: `87`
- `REPLAY_RESTART_VERIFIED`: `1`
- `REPLAY_ACTIVE_STATE_RESTART_COVERAGE`: `1`
- `REPLAY_STATE_SEALED`: `1`
- `REPLAY_FINALIZED`: `1`

Hypothesis revision export: `[]`.

An empty hypothesis-revision export is valid for this deterministic WAIT/SCAN mechanical rehearsal; the append-only revision mechanism is already implemented and tested as a prerequisite, while this mock did not create or revise hypotheses.

## Pre-execution gate adjudication

The full offline/pre-provider sequence required by the Owner-approved V0.1 design is satisfied:

1. trading-only prompt/context contract — complete;
2. append-only/versioned hypothesis revision history — complete and tested;
3. deterministic outcome-blind slice selector — complete;
4. fixed-5m wake ledger/orchestrator — complete;
5. causal 4H/1H/15m/5m runtime context wiring — complete;
6. intent-only lifecycle state — complete;
7. restart gates — complete;
8. leakage/request-count/audit invariants — complete;
9. exact-slice real-corpus mock/no-provider dry run — `PASS`;
10. pre-execution evidence seal — `PASS`.

Therefore:

`V0_1_OFFLINE_PREEXECUTION_GATES = PASS`

`FULL_EXACT_SLICE_MOCK_DRY_RUN = PASS`

`REAL_DEEPSEEK_PROVIDER_CALLS = 0`

`FIRST_REAL_PROVIDER_CALL_BOUNDARY = REACHED`

## Authorization boundary

This evidence does **not** authorize paid/provider execution.

Current provider state remains:

`REAL_DEEPSEEK_PROVIDER_CALLS = PAUSED`

The separate three-call smoke authority and Owner decision govern the next possible paid action. Full `1998`-request replay remains unauthorized.
