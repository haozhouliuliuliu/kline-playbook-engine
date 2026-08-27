# Jianghe Replay V0.1 — Post-repair Revalidation Final Zero-Cost Preflight (PASS)

Status: `PASS__ZERO_COST__NO_PROVIDER_ATTEMPT__DATASET_VERIFIED`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

## Command

Run on canonical `main` with a new empty state directory and explicit dataset paths:

```text
python tools/preflight_replay_v0_1_provider_smoke.py \
  --manifest data/canonical/manifest.json \
  --parquet-root data/canonical/parquet \
  --state-dir <new-empty-preflight-state>
```

Pinned canonical pyarrow environment: Python `3.12` + `pyarrow 25.0.1` /
`tzdata 2026.3` (probe site-packages; matches `requirements-canonical.txt`).

Exit code `0`. `real_provider_calls = 0`. No network, no credential read, no
machine-authority creation/activation.

## Deterministic blueprint (persisted)

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_FINAL_PREFLIGHT_BLUEPRINT_2026-08-27.json`

| field | value |
| --- | --- |
| preflight_version | `KPE_REPLAY_V0_1_PROVIDER_SMOKE_PREFLIGHT_V0_1` |
| product / contract | `cu` / `SHFE.cu2406` |
| slice identity | `347291481968b1884635a11aa1da985d9aad1b3fb854a16087bbca662bd85a06` |
| exact slice seal identity | `e9bbd232fd05d320a24c80ac5570a94abdf6d4c3a167cdd5c46f4426a6c84156` |
| context policy identity | `98262c9ab0614b4145fe56cb8746a44d754d03a38a25584aba810991cd666371` |
| renderer identity | `JIANGHE_VISUAL_RENDERER_V0_1:2397764a0f3e2b453456fd8735caeb59881d19ea5a2399fc91fb7e7307525851` |
| canonical fixed-5m preflight identity | `e4d29a5f6001302811c78be76565ef3095325fd46d28811c88591b6e375750a8` |
| constructed bar counts | 4H=164, 1H=286, 15m=1270, 5m=3810 |
| provider / model | `deepseek` / `deepseek-v4-flash-vision-exp` |
| Harness | `0.1.1-rc.2` @ `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e` |
| prompt contract | `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3` |
| trader identity | `39ea5818636e94a4e707a6615d2017dee48dce2e79efcef8b6783015814653ba` |
| runtime contract identity | `4edae4cd9273ae2da633f2976825b10cb81e1a984155ac7b9588b6e8f642fa31` |
| real provider calls | `0` |

## Smoke wakes (both identities, exact close times, 4 PNGs each)

### call_1

- trading day: `2024-04-10`; session identity: `ce374c864bf10ba5bb2d6878579a9c12a5a1734aa9121a245c2eb7899952ee14`
- close time: `2024-04-09T13:05:00.000000+00:00`
- logical wake-selection identity: `1c3ef378cd2cd18569f331333667ac65711c98191291bdf33b729f497114d5b6`
- runtime wake identity: `1435a96a125f8d82eaefddd6a3969aa8dd8243268053bde7cafb3f1b9b220e57`
- observation identity: `bf3017885a8129beb95338e942478bb940dec5d18f22e5b6d2fa003d820cc63c`
- PNG hashes: `2d8879e3…219df`, `8274da4f…5f942`, `f9e5b22b…e2074`, `4ef00403…aad400e`

### call_2

- trading day: `2024-04-10`; session identity: `ce374c864bf10ba5bb2d6878579a9c12a5a1734aa9121a245c2eb7899952ee14`
- close time: `2024-04-09T13:10:00.000000+00:00`
- logical wake-selection identity: `a840d8825ced91397e9b262da891f5716a88036825edc7fd54a8441cd10b7d62`
- runtime wake identity: `61e12be115a82869e50df79c75f2abeac7796bf6195bc73169a97f2fa51a655e`
- observation identity: `4449e9dfc80cf2937db47ebb52ddbd05d0a267545d27d6c3905d0f1cb769c339`
- PNG hashes: `23063a98…e677bc`, `412c98e4…a69f1`, `7b88bff4…ce4cd9`, `7783f414…c606677`

### call_3

- trading day: `2024-04-10`; session identity: `ce374c864bf10ba5bb2d6878579a9c12a5a1734aa9121a245c2eb7899952ee14`
- close time: `2024-04-09T13:15:00.000000+00:00`
- logical wake-selection identity: `94221314c120c591a79489e26734e3436d62c21d9087629551a9f3cfcddb296b`
- runtime wake identity: `3f57e6107e6b80f2e0907b3d1db6e51b092a881aa93368d9006001183b1989ce`
- observation identity: `14c754ae4fd77ac515f27f986ff4d0837a8599599a9517f4039a966d9ba7d458`
- PNG hashes: `326d221c…dcb37`, `7e4dd2b3…cd770`, `f43d2f0d…998bd`, `ea1c8da5…f5a59dc`

## Verification scope

- exact frozen slice verified against accepted manifest identity and corpus identity;
- `cu` / `SHFE.cu2406` exact slice present;
- exactly first 3 governed wakes, exact close times;
- both logical and runtime identities present per wake;
- exactly 4 causal PNGs per call;
- deterministic preflight success;
- no future/outcome/PnL leakage by construction (causal context index built from
  prior/burn-in/measurement windows only).

## Evidence boundary

- Zero provider/network/credential activity.
- The prior missing-data blocker is CLOSED by local path restoration.
- A fresh forward V0_3 two-identity machine authority and the immediate
  consequential-action check remain required before any real execution.
