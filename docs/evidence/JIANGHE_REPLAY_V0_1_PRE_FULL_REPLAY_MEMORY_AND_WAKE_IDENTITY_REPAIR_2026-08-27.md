# Jianghe Replay V0.1 — Pre-Full-Replay Memory & Wake-Identity Offline Repair

Status: `OFFLINE_VERIFIED__NO_PROVIDER_CALL`

Date: `2026-08-27`

Scope: bounded offline repair package implementing already-approved V0.1 semantics:

1. structured persistent trading-memory fidelity (A);
2. prospective logical-wake-selection identity vs runtime-wake identity separation (C);
3. deterministic regression coverage for the source-faithfulness finding exposed by the three-call smoke (B).

`PROVIDER_CALLS = 0` for this entire package. No provider/API/model network request, no paid call, no smoke rerun, no full V0.1 replay was executed. Historical smoke evidence and terminal machine authorities were not altered.

## Implementation commit

- Implementation + tests:
  - commit: `8e9f392478ae95f0327d18aa344bca0e04fda982`
- Evidence + current-state record (this file / `CURRENT_STATE.md`): recorded in the follow-up commit containing this artifact.

## Old → new response / prompt identities

| identity | old (historical, preserved) | new (active) |
| --- | --- | --- |
| response schema version | `JIANGHE_RUNTIME_RESPONSE_V0_1` | `JIANGHE_RUNTIME_RESPONSE_V0_2` |
| response schema identity | `60a008ff4e64a74a413f2f198f675dd3e3293ff7b891ed9e466b531d3bb32289` | `51a096ab36e827e4227ec9ee863d55fda8b66280d687416f243939cc19ca386d` |
| normalizer version | `JIANGHE_RUNTIME_RESPONSE_NORMALIZER_V0_1` | `JIANGHE_RUNTIME_RESPONSE_NORMALIZER_V0_2` |
| normalizer identity | `e0aa2c29da77786a496079fd2b5816206fd1381fd9ad0312a918cee450cca0fc` | `4fedeb27e7a738e1d9bf38d347eb97fe330ca6f1e7f3504b4314c6121ac2b92a` |
| prompt contract version | `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_2` | `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3` |
| prompt contract identity | `d5fd8384864bc4e0b2ff5198d21f0c4c522a33662babb1b13824c87d5420bac2` | `b7ded73fab8902c34bf54f6861c1ff00c9e05e0878ae01f0fc8742d08a0f74d4` |
| system prompt sha256 | preserved `SYSTEM_PROMPT` | `05d7a10beb4e8049d846a3ebf3df3ad62b815e28e0ea7962318698124752a531` |
| decision prompt sha256 | `181387fd77090ff829339680a57d0c48f665627297bd77772c6e8b7b600a7e1a` (V0_2) | `7be2c290d1c06e50a77d7aee5a0bc0b69c6d77cf3518780fcfde07451bac0efc` (V0_3) |

Historical prompt/schema constants (`RESPONSE_SCHEMA_VERSION_V0_1`, `RESPONSE_SCHEMA_IDENTITY_V0_1`, `NORMALIZER_IDENTITY_V0_1`, `DECISION_PROMPT_V0_1`, `DECISION_PROMPT_V0_2`, `SYSTEM_PROMPT`, `PROMPT_CONTRACT_VERSION_V0_1`, `PROMPT_CONTRACT_VERSION_V0_2`) remain frozen byte-identical; the historical V0_1/V0_2 decision-prompt hashes and both historical smoke slot hashes are unchanged.

## A. Structured trading memory

The strict model-visible response contract now exposes first-class model-supplied CURRENT STATE SNAPSHOT fields (no parsing of natural-language rationale by the deterministic layer):

- `current_market_hypothesis`: string or null
- `timeframe_trend_view`: array of `[timeframe, view]` string pairs over the active stack 4H/1H/15m/5m (each at most once, deterministically ordered)
- `key_location_hypotheses`: array of non-empty strings
- `expected_trigger`: string or null
- `invalidation_hypothesis`: string or null
- `open_questions`: array of non-empty strings

These are exactly model-supplied and are now persisted into `DS_WORKING_MEMORY` by the V0.1 projection/application path (`_project_to_jianghe_decision` + `_apply_working_memory`), survive restart, and are surfaced in the next model-visible `DS_WORKING_MEMORY` context. The prompt tells the trader to carry forward still-valid prior memory explicitly, revise on changed causal evidence, clear a field only when it no longer applies, and never invent missing trading evidence. Operational expiry/scheduling (watch-region expiry, `review_at`, `next_review`) remains project-owned and is not exposed to the model.

No future/outcome/PnL fields were introduced; the recursive outcome/self-evaluation rejection still applies.

## B. Jianghe source-fidelity regression

`JH-CLM-034-002` is canonically a MANAGEMENT claim ("盈利订单可随新发力/防守结构推进止损；二推不能突破前高是动能减弱退出线索。"). The known three-call smoke misuse used it as a PRE_ENTRY_REQUIREMENT. A deterministic evaluator-side fixture/adjudicator (`src/jianghe_source_fidelity_evaluation.py`) now classifies that known use as `SOURCE_FAITHFULNESS_FINDING`, grounded in the committed claim-level branch registry (verified by regression test). The active prompt (`SYSTEM_PROMPT_V0_3` / `DECISION_PROMPT_V0_3`) explicitly forbids extending a Jianghe claim beyond its supplied canonical meaning/category.

## C. Logical vs runtime wake identity

- `logical_wake_selection_identity`: stable logical wake-selection identity bound only to selection-invariant fields: logical identity/version (`KPE_FIXED_5M_LOGICAL_WAKE_SELECTION_V0_1`), frozen V0.1 wake-policy identity (`WAKE_POLICY_IDENTITY`), sealed slice identity, governed session identity, ordered sequence, and exact closed-5m close time. It excludes trader/prompt/runtime identity.
- `wake_identity` (now explicitly the runtime wake identity): continues to include the trader/runtime identity for idempotency, persistence isolation and one-request binding.

Invariant (proven by tests):

```text
same logical replay selection + changed approved prompt/trader identity
=> SAME logical wake-selection identity
=> DIFFERENT runtime wake identity
```

Both identities are first-class in `GovernedWake`, the wake-ledger store (`KPE_FIXED_5M_WAKE_LEDGER_STORE_V0_2`), wake exports, `ReplayStepBinding` and the future provider-smoke authority contract.

### Backward compatibility for historical terminal evidence

- Historical V0.1/V0.2 smoke wake hashes are not rewritten.
- Historical terminal authorities (runtime-only `wake_identity`, no logical identity, status `REVOKED`) remain readable.
- A runtime-only authority may never be PENDING/ACTIVE; it is terminal-only (a historical runtime-only authority cannot be silently upgraded into a new ACTIVE authority).
- Future ACTIVE/PENDING provider-smoke authorities (V0_2 authority version) require BOTH identities on every wake.

## D. Tests

Focused suites (all pass offline, zero provider calls):

- `tests.test_jianghe_structured_memory` — schema acceptance, fail-closed missing/unknown/wrong-type fields, exact model-supplied values, per-field persistence, carry-forward, deterministic clearing, restart preservation, next-request `DS_WORKING_MEMORY` presence, no outcome/PnL fields.
- `tests.test_jianghe_source_fidelity_regression` — JH-CLM-034-002 registry grounding, known misuse → source-faithfulness finding, compliant use OK, prompt claim-scope instruction.
- `tests.test_wake_identity_separation` — logical identity stable across trader change, runtime identity changes, sequence/time/slice/session alter logical identity, duplicate/missing/request-binding fail-closed, both identities first-class.
- Updated: `tests.test_jianghe_response_normalizer`, `tests.test_jianghe_trading_only_prompt`, `tests.test_fixed_5m_wake_ledger`, `tests.test_replay_v0_1_provider_smoke`, `tests.test_replay_integrity`, plus response builders in replay fixtures/mock/smoke-bridge/tools.

Broad regression:

```text
python -m unittest discover -s tests
590 tests: OK (1 expected pre-commit execution-code-bound guard error before the
implementation commit; passes after the commit; 8 skipped)

python -m compileall -q src tools tests  # PASS
git diff --check                         # PASS
python tools/check_authority_consistency.py  # AUTHORITY_CONSISTENCY = PASS
```

`test_execution_code_bound_passes_at_clean_head` verifies execution-critical paths match the committed HEAD; it passes on the committed tree by construction.

## Remaining limitations

- Structured-memory persistence is offline-verified with synthetic deterministic responses; it does not claim real-provider compatibility.
- A later exact paid smoke/revalidation after this prompt/schema contract change requires a new Owner paid authority plus a newly resealed two-identity machine authority before network execution.
- Watch-region operational expiry, `review_at` and `next_review` remain project-owned and are not yet projected from model state (intentionally out of scope).
- No real-provider call was made; nothing here grants provider, broker/account or real-money authority.
