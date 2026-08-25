# MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_AUTOMATED_GATE_EVIDENCE_2026-08-26

Status: `AUTOMATED_GATE_PASS__LOCAL_WORKSTATION_ACCEPTANCE_PENDING`

Work package: `MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1`

Merged implementation: PR #42

Main merge commit: `361649965685282af0f04b854f14195c9ce66e65`

PR final head: `bb38a103457b9075f7f9a7d74715a054a8d166d4`

Provider calls made by this acceptance: `0`

## Final automated runs

Repository CI:

- run id: `32891952828`
- conclusion: `success`
- Python: `3.11.16`
- result: `437 tests`, `OK`, `12 skipped`, `0 failed`

DeepSeek Harness Dynamic Admission:

- run id: `32891952918`
- conclusion: `success`
- pinned Harness commit: `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- Node: `22.19.0`
- project fail-closed DeepSeek transport patch: applied
- `DEEPSEEK_API_KEY`: empty in project provider probes

The dynamic gate independently passed:

1. fail-closed DeepSeek vision transport with zero hidden stale-file second chat request;
2. exact project provider/model route plus project memory/tool context and tool audit integration using a no-network mock adapter;
3. the pinned Harness durable SQLite persistence contract `persists a live session driven through the store, surviving reload`;
4. unaffected DeepSeek image serialization and dynamic configuration behavior.

The persistence gate deliberately targets the admitted persistence property rather than the entire upstream SQLite backend implementation suite. The full upstream suite contains scheduler/timing mechanics tests unrelated to this project's required persistence property.

## Twelve prototype objective mapping

### 1. Exact DeepSeek model + admitted Harness composition

`PASS`

Evidence:

- `src/persistent_deepseek_runtime.py` binds `deepseek-v4-flash-vision-exp`, Harness `0.1.1-rc.2`, pinned commit `b150a551...`, mandatory project patch and `maxRetries = 0`.
- `integrations/deepseek-harness/project-dynamic.spec.ts` exercises the exact project provider/model route with a no-network adapter.
- dynamic admission run `32891952918` passed.

### 2. Causal 4H / 1H / 15m / 5m observation + chart path

`PASS`

Evidence:

- `tests/test_persistent_deepseek_trader_prototype.py::test_observation_exposes_exact_four_timeframe_stack_and_chart_provenance`
- `tests/test_persistent_deepseek_offline_probe.py`
- `tools/run_persistent_deepseek_trader_offline_probe.py` renders four deterministic PNG chart artifacts and verifies the active stack.

### 3. DS_WORKING_MEMORY survives restart

`PASS`

Evidence:

- project-owned SQLite store in `src/persistent_trader_store.py`
- `test_working_memory_survives_process_style_reopen_with_mutation_audit`
- offline probe closes and reopens the SQLite database before checking restored working memory.

### 4. Bounded attributable read-only JIANGHE_CANON retrieval

`PASS`

Evidence:

- `src/jianghe_canon_retrieval.py`
- `test_jianghe_retrieval_is_bounded_read_only_and_attributable`
- real-repository offline probe retrieves current Jianghe source artifacts with bounded result/excerpt limits.

### 5. Project K-line/market tools callable through Harness and audited

`PASS`

Evidence:

- `ProjectToolRegistry` records `TOOL_CALL`, `TOOL_RESULT` and `TOOL_ERROR` audit events.
- `integrations/deepseek-harness/project-dynamic.spec.ts` registers and calls project K-line tool `jianghe_kline_snapshot` through the Harness tool surface and verifies audit output.
- dynamic admission run `32891952918` passed.

### 6. DS_JOURNAL persists separately from source truth and policy

`PASS`

Evidence:

- separate `journal` table and semantic class `DS_JOURNAL_REFLECTION_NOT_FACT_OR_POLICY`.
- `test_journal_and_hypothesis_memory_are_separate_and_non_executable`.
- offline probe verifies journal survives persistent export/reopen.

### 7. DS_HYPOTHESIS_MEMORY persists and is non-executable

`PASS`

Evidence:

- separate `hypotheses` table.
- allowed states are `CANDIDATE`, `FALSIFIED`, `RETIRED`; no policy-promotion state exists.
- exported hypotheses explicitly carry `executable_policy = false`.
- relevant prototype tests passed.

### 8. Request/response/retrieval/tool/memory activity is reconstructable

`PASS`

Evidence:

- append-only project audit stores request ids, observation identities, payload hashes, retrieval identities, raw response hashes, normalized response identities, tool activity and memory mutation evidence.
- `test_model_request_is_fully_reconstructable_and_never_sent`
- `test_raw_response_and_strict_normalization_are_reconstructable`
- offline probe verifies the required audit event kinds after restart.

### 9. STRICT_OUTPUT_ENUM_ENFORCEMENT remains active

`PASS`

Evidence:

- strict `JiangheResponseNormalizer` rejects enum normalization/coercion and unknown fields.
- invalid output is recorded as `MODEL_RESPONSE_REJECTED`.
- existing normalizer tests and prototype regression tests passed.

### 10. NO_4H_EXACT_VOLUME_RECONCILIATION remains active

`PASS`

Evidence:

- existing `assert_no_4h_exact_volume_reconciliation` guard is called on context/tool arguments/results.
- prototype test verifies prohibited 4H reconciliation fails closed.
- offline probe explicitly exercises the rejection path.

### 11. No silent retry / hidden second request / model substitution / prompt mutation

`PASS`

Evidence:

- runtime contract requires `general_max_retries = 0`.
- provider execution is locked in the offline prototype contract.
- `stale-file-fail-closed.spec.ts` proves one failed request does not trigger a hidden second chat request.
- `PersistentDeepSeekTraderPrototype` rejects model mismatch.
- runtime identity binding tests reject system-prompt, decision-prompt and tool-capability drift.
- dynamic admission run `32891952918` passed.

### 12. Core trader state/knowledge is project-owned and portable

`PASS`

Evidence:

- project state is stored outside opaque Harness session internals.
- portable export explicitly excludes Harness opaque state.
- `test_portable_export_contains_project_state_not_harness_opaque_state`.
- regression test proves export includes records beyond bounded context-query limits (`101+` journal and `201+` hypotheses), preventing silent migration truncation.

## Automated gate conclusion

`PROTOTYPE_12_OBJECTIVE_AUTOMATED_GATE = PASS`

`REAL_DEEPSEEK_PROVIDER_CALL = NOT_PERFORMED`

`PAID_CALL_AUTHORIZATION = NOT_USED`

`REPLAY_OR_LEARNING = NOT_STARTED`

## Remaining work-package step

The project deployment boundary is `LOCAL_WORKSTATION_FIRST`. The implementation is merged and automated evidence is complete, but the dated handoff remains active until the Owner workstation executes the no-provider-call local acceptance probe and returns its evidence.

Required local artifact:

`~/.kline-playbook-engine/prototype-v0-1/offline-probe-summary.json`

or the platform-equivalent state directory chosen explicitly at runtime.

The local acceptance must show every `checks` value as `true` and `provider_call_made` as `false`.

Only after that local evidence is reviewed should current authority be finalized and the dated prototype handoff deleted. Do not enter replay/learning before that closure.
