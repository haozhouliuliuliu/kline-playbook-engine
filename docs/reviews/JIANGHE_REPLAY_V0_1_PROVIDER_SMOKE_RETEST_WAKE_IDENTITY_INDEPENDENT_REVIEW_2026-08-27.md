# Jianghe Replay V0.1 Provider-smoke Retest — Wake Identity Independent Review

Status: `INDEPENDENT_REVIEW__ACCEPTABLE_WITH_NARROW_FORWARD_REPAIR`

Date: `2026-08-27`

Reviewer basis: current GitHub `main` commit `9a307929428e356ae27f6a381f84fb419512e53e`; no provider/network request was executed for this review.

## Scope and primary evidence

This review read the current ownership/state documents and the binding V0.1 Owner decision, original smoke authority/slot/fail-closed evidence, response-contract clarification, fresh retest authority/slot, and retest evidence. It also inspected the execution implementation at the retest-bound commit `4cf9600d834dd7df9e0526b2583a07e42a4b996e` and its unchanged relevant code on current `main`.

The question is limited to whether the V0.2 retest's changed *runtime* wake hashes invalidate its three-call provider-smoke evidence. It does not adjudicate trading quality or authorize any further call.

## Determination

`NOT A TRUE WAKE-SELECTION OR PROTOCOL VIOLATION.` The completed retest is acceptable for the narrow smoke claims: provider path, strict response-schema compatibility, restart continuity, one-request-per-admitted-wake accounting, and no-hidden-retry accounting. It is not evidence that the literal V0.1 runtime wake-hash strings were reused: they were not, and cannot be after the approved V0.2 prompt identity change under the implemented identity model.

The material defect is a wording/model-layer conflation in the fresh retest authority: it requires the “same exact first three governed wake identities”, while the sealed authority contains different runtime hash values. The broader phrase “same governed wakes” remains supported when interpreted as the stable logical selection: sealed slice, fixed-5m policy, ordered sequence 0/1/2, and close times. The literal “same exact … identities” is false for the current runtime-hash type.

## Recomputed causal chain from code

`src/jianghe_ai_trader.py` defines `JiangheAITraderIdentity.identity` as a canonical hash that includes both `system_prompt_identity` and `decision_prompt_identity`.

`src/fixed_5m_wake_ledger.py` defines a governed runtime `wake_identity` as a canonical hash of:

```text
wake_ledger_version + session_identity + sequence + close_time + trader_identity
```

The V0.2 Owner decision explicitly required a new decision-prompt contract/identity. The slots record the resulting trader identities:

| slot | prompt | trader identity | runtime wake hashes |
| --- | --- | --- | --- |
| original | V0.1 | `44039ae0…` | `edef4350…`, `dd9edac1…`, `c5d01898…` |
| retest | V0.2 | `bf233fb7…` | `4000fa69…`, `b4785ee8…`, `149e93dc…` |

Therefore the changed hashes follow necessarily from the approved prompt-contract change, rather than demonstrating a changed time selection. The smoke runner independently constructs `steps` from `preflight.wake_bars`, selects `steps[:3]`, and fails closed unless each generated runtime hash equals the fresh authority's sealed hash (`tools/run_replay_v0_1_provider_smoke.py`). It has no path for choosing a different timestamp because of a model response or market outcome.

## Answers to the audit questions

1. **No, not as a true experiment/protocol violation.** It is a literal-authority wording defect, not evidence of a changed logical wake selection. Calling the V0.2 strings the same exact V0.1 *runtime hashes* would be incorrect.
2. **Yes, this is identity-layer conflation.** The code's `wake_identity` is an execution-instance identity, not a stable logical wake-selection identity.
3. **No change found** in selection, replay close times (`13:05`, `13:10`, `13:15` UTC), fixed-5m policy, sealed slice, product/contract, causal context policy, renderer, or ordered first-three selection. The retest evidence also records the same fixed-5m preflight identity `e4d29a5f…` and the same slice/context/renderer identities. The changed prompt and trader/runtime identities are intentional retest variables authorized by the response-contract clarification.
4. **No outcome information was used to select or alter calls, on the available primary record.** The triggering old response was a schema rejection with no normalized decision or accepted state mutation; the clarification expressly forbids it entering model-visible context. The selection code is deterministic and pre-network. No audit can prove an unrecorded human mental state, but the authority, code, and evidence disclose no outcome-driven selection.
5. **Another paid V0.2 rerun would not resolve this discrepancy.** It would generate the same V0.2-derived runtime wake hashes again (assuming all bound inputs stay equal), not the V0.1 hashes. A rerun would add spend without deciding the identity-model issue.
6. **Yes.** The project should distinguish a stable `logical_wake_selection_identity` from the existing runtime/execution `wake_identity`.
7. **Yes.** The completed 3/3 evidence is acceptable for the stated provider-path/schema/restart/request-accounting adjudication without another paid rerun, subject to correcting the forward-facing authority vocabulary before any future slot is written.
8. **Other material contradiction found:** the retest authority's literal “same exact first three governed wake identities” conflicts with its own V0.2 resealed slot. No further material contradiction was found in the inspected chain for this narrow adjudication. The old slot is separately terminal and immutable; the fresh slot is separately terminal and records exactly three calls, zero retries, and the required restart.

## Narrow forward repair (no historical rewrite)

Do not change either historical slot, evidence file, prior authority, or `CURRENT_STATE.md`.

For a future authority/code change only:

1. Define and seal `logical_wake_selection_identity` from selection-invariant fields: protocol/wake-policy version, slice identity, session identity, fixed ordered sequence, and close time (optionally the causal observation identity if the protocol intends to bind it).
2. Retain the current `wake_identity` as `runtime_wake_identity`, explicitly including the trader/runtime identity for idempotency, persistence isolation, and one-request binding.
3. State future matched-retest requirements as “same logical wake-selection identities and close times”; require the runtime identities to be newly resealed and internally consistent whenever an approved runtime/prompt identity changes.
4. Add a deterministic test proving that a prompt/trader change preserves the logical identities while changing runtime identities, and a future-authority parser field for both identities.

This repair is prospective only. The historical evidence should retain the actual V0.1 and V0.2 runtime hash values exactly as recorded.

## Verification performed

No provider/API command was run.

```text
python -m unittest tests.test_fixed_5m_wake_ledger tests.test_jianghe_trading_only_prompt tests.test_replay_v0_1_provider_smoke tests.test_replay_v0_1_orchestrator tests.test_replay_restart_continuity -v
# 51 tests: PASS

python -m compileall -q src tools tests
git diff --check
# PASS
```
