# JIANGHE PRE-LIVE FIDELITY GATE RE-AUDIT V0.1

> 本文件对 `docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_AUDIT_V0_1.md` 的
> 全部原 finding（G-01..G-03、H-01..H-13、O-01..O-03、N-01..N-04、P-01..P-04）
> 在 **integration tree 当前 repo** 逐项重新检查 code/artifact/test，并给出裁决。
> 不引用任何“之前 worker 说 PASS”作为依据。

## Re-audit 裁决

```text
PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS
```

前提：

```text
ALL_ORIGINAL_FINDINGS_CLOSED=27/27
FULL_SUITE=1195_PASS_0_FAILURES_0_ERRORS
FIREWALLS=PASS
OUTCOME_ACCESS=NO
LIVE_MODEL_CALLS=0
PAID_SPEND=0
```

---

## GLOBAL — 全局证据链

### G-01

```text
ID=G-01
ORIGINAL_FINDING=ObservationIdentity 没绑定实际 bars/positions/orders/charts 内容。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  src/jianghe_ai_trader.py 的 ObservationIdentity.bind_content() 把 bars
  （OHLCV/timeframe/三时间戳/is_closed）、positions、active_order_ids、
  visible_metadata 全部序列化为 content_identity=_canonical_hash(content)，
  并 replace 进 identity；JiangheObservation.identity 使用该绑定。
  observation.identity.identity 参与 visual/structured/replay/provider 链路。
TEST_EVIDENCE=
  tests/test_jianghe_ai_trader_foundation.py:
  test_observation_identity_changes_when_one_ohlc_field_changes、
  test_all_material_bar_fields_are_identity_bound、
  test_position_and_order_facts_change_observation_identity。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### G-02

```text
ID=G-02
ORIGINAL_FINDING=JiangheAITraderIdentity 尚未绑定 governed normalizer + 当前 PRIMARY registry。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  src/jianghe_ai_trader.py 的 JiangheAITraderIdentity 字段包括
  primary_branch_registry_identity、interpretation_set_identity、
  system_prompt_identity、decision_prompt_identity、
  context_selection_policy_identity、runtime_normalizer_identity、
  chart_renderer_identity、observation/wake/decision schema、
  hard_execution_envelope_identity、inference/tool/family scope，
  全部在 __post_init__ 中要求非空并参与 _canonical_hash 计算 identity。
  即研究对象身份可绑定 governed normalizer、prompt 与当前 PRIMARY registry。
TEST_EVIDENCE=
  tests/test_jianghe_ai_trader_foundation.py:
  test_ai_identity_binds_primary_registry_normalizer_and_execution_envelope
  （逐个字段替换验证 identity 变化，含 primary_branch_registry_identity 与
  runtime_normalizer_identity）、test_provider_and_inference_configuration_are_identity_bound。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### G-03

```text
ID=G-03
ORIGINAL_FINDING=fidelity track label 尚无真实输入 provenance 证明。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  src/jianghe_fidelity_evaluation.py 的 InputEvidence 是 typed provenance
  （12 个字段，全部必须为 lowercase 64 位 sha256 hex）；
  TRACK_REQUIRED_EVIDENCE 对 SEMANTIC/VISUAL/STRUCTURED/DUAL_INPUT/
  OPERATIONAL_PROVIDER 各自严格要求最小 identity 集合；
  parse_input_evidence 拒绝未知字段；track 必须是精确 ALLOWED_TRACKS 枚举。
  因此 caller 无法在缺少 typed provenance 时把某 track 重贴为另一 track。
TEST_EVIDENCE=
  tests/test_jianghe_real_model_firewall.py：VISUAL 无 visual provenance ->
  rejected；STRUCTURED 无 structured provenance -> rejected；
  DUAL 少任一输入 -> rejected；OPERATIONAL_PROVIDER 无 provider evidence -> rejected。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

---

## FIDELITY — fidelity evaluator 证据完整性

### H-01

```text
ID=H-01
ORIGINAL_FINDING=outcome contamination 目前不会强制 evaluator ERROR。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  src/jianghe_fidelity_evaluation.py evaluate_response_records()：
  response.outcome_reference=True、raw_text 命中污染模式、metadata 命中污染
  模式都会使该 record 不被 admit，进入 outcome_violations 并追加 errors；
  non_scoreable_total>0 时 evidence_eligibility=INELIGIBLE，
  errors 非空时 processing_status=ERROR。
TEST_EVIDENCE=
  tests/test_jianghe_real_model_firewall.py：unknown outcome 字段、
  raw_text contamination、metadata contamination 均被拒绝且 admitted=0。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-02

```text
ID=H-02
ORIGINAL_FINDING=unknown response fields 未严格拒绝。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  _CANONICAL_RESPONSE_FIELDS allowlist；parse_fidelity_response 对任何未知
  字段抛 ValueError -> malformed_response_records，不评分。
TEST_EVIDENCE=
  tests/test_jianghe_real_model_firewall.py：
  test_unknown_outcome_field_rejected（future_price -> rejected）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-03

```text
ID=H-03
ORIGINAL_FINDING=corpus_id 未和实际 corpus 强绑定。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  evaluate_response_records() 对每条 record 校验
  record.corpus_id == 当前 corpus_id，不一致进入 corpus_mismatch_records
  且不 admit。
TEST_EVIDENCE=
  tests/test_jianghe_real_model_firewall.py：corpus mismatch -> rejected。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-04

```text
ID=H-04
ORIGINAL_FINDING=call_success=False 仍可能评分。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  call_success 必须为真正 bool（parse_record 拒绝非 bool）；
  call_success=False 时 record 进入 failed_call_records 且不 admit、不评分。
TEST_EVIDENCE=
  tests/test_jianghe_real_model_firewall.py：call_success=False ->
  NON_SCOREABLE。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-05

```text
ID=H-05
ORIGINAL_FINDING=arbitrary metadata/input reference 不足以证明 provenance。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  parse_metadata 只允许 _ALLOWED_METADATA_KEYS={probe_session_id,
  engine_version}，值必须是 JSON-safe scalar，未知键拒绝；
  重要 provenance 一律走 InputEvidence typed 字段；metadata 还做污染扫描。
TEST_EVIDENCE=
  tests/test_jianghe_real_model_firewall.py：metadata contamination -> rejected。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-06

```text
ID=H-06
ORIGINAL_FINDING=evidence parser 存在 bool/str/int 宽松 coercion。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  _strict_latency 拒绝 bool/float/负数；_to_string_tuple 元素必须为 str；
  parse_fidelity_response 对 family/action/direction/raw_text 拒绝非字符串；
  outcome_reference 必须真正 bool；parse_record 的 call_success 必须真正 bool。
TEST_EVIDENCE=
  tests/test_jianghe_fidelity_evaluation.py + tests/test_jianghe_real_model_firewall.py。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-07

```text
ID=H-07
ORIGINAL_FINDING=无 deterministic full report_identity。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  _compute_report_identity 对排除 report_identity 字段后的报告做 canonical
  JSON（ensure_ascii=False、sort_keys、separators=(",",":")）后 SHA-256；
  _finalize_report 追加 report_identity。
TEST_EVIDENCE=
  tests/test_jianghe_fidelity_evaluation.py（report identity 确定性断言）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-08

```text
ID=H-08
ORIGINAL_FINDING=technical OK 与 evidence completeness/fidelity eligibility 混淆。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  报告三态分离：processing_status（OK/ERROR）、evidence_completeness
  （COMPLETE/INCOMPLETE）、evidence_eligibility（ELIGIBLE/INELIGIBLE）
  各自独立计算，不再用一个 technical OK 掩盖证据缺口。
TEST_EVIDENCE=
  tests/test_jianghe_fidelity_evaluation.py（三态各自断言）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

---

## PROVIDER — provider 证据

### H-09

```text
ID=H-09
ORIGINAL_FINDING=request artifacts 没严格证明属于同一 observation。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  src/jianghe_model_provider.py JiangheModelRequest.__post_init__：
  visual/structured artifact 的 observation_identity 必须等于 request 的
  observation_identity，否则 ValueError；
  to_input_evidence 要求 response_evidence.request_identity == request.identity
  且 provider/capability 一致。
TEST_EVIDENCE=
  tests/test_jianghe_model_provider.py（request/response 绑定断言）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-10

```text
ID=H-10
ORIGINAL_FINDING=requested model identity 与 provider-resolved model/version/snapshot 混淆。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  RequestedModelSelectorIdentity（requested：selector/version_binding/
  drift policy/exact_snapshot）与 ResolvedProviderModelIdentity（resolved：
  resolved_model_id/resolved_version_or_snapshot，reported_by=PROVIDER_RESPONSE）
  是两个独立 dataclass；parse_mocked_response 校验 exact pinned selector 与
  provider resolved model 一致。
TEST_EVIDENCE=
  tests/test_jianghe_model_provider.py（requested vs resolved 分离断言）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-11

```text
ID=H-11
ORIGINAL_FINDING=capability identity 未完全绑定 API surface。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  ProviderIdentity 绑定 provider_id/api_surface/api_version/
  endpoint_semantics_identity 并生成 identity；CapabilityDeclaration 绑定
  provider_identity + supported_tracks + 全部 capability bool + 漂移策略。
TEST_EVIDENCE=
  tests/test_jianghe_model_provider.py（capability identity 断言）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-12

```text
ID=H-12
ORIGINAL_FINDING=structured input capability 与 JSON output capability 混淆。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  CapabilityDeclaration 分开声明 supports_structured_input（输入）与
  supports_structured_output（输出），各为严格 bool 字段，均参与 identity。
TEST_EVIDENCE=
  tests/test_jianghe_model_provider.py（input/output 能力分离断言）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### H-13

```text
ID=H-13
ORIGINAL_FINDING=无完整 deterministic provider response evidence identity。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  JiangheModelResponseEvidence 计算 raw_response_sha256 与 identity
  （request_identity/provider/capability/requested selector/resolved model/
  response_id/timing/latency/raw hash/normalized identity/usage identity）。
TEST_EVIDENCE=
  tests/test_jianghe_model_provider.py（response evidence identity 断言）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

---

## OBSERVATION — 观察证据

### O-01

```text
ID=O-01
ORIGINAL_FINDING=replay decision 未强制绑定 accepted/current observation。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  src/jianghe_ai_trader.py JiangheMarketReplay.accept_observation 设置
  accepted_observation_identity；record_decision 要求
  record.observation_identity == accepted_observation_identity，否则
  ValueError；accept 之前 record_decision 也拒绝。
TEST_EVIDENCE=
  tests/test_jianghe_market_replay_v0_2.py（decision 必须绑定 accepted
  observation identity）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### O-02

```text
ID=O-02
ORIGINAL_FINDING=canonical ObservationBar validation 弱于 visual path。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  视觉路径消费同一 canonical ObservationBar：VisualPanel 校验
  isinstance(ObservationBar) 与 timeframe 一致；JiangheVisualRenderer
  _validate_spec 集中统一审计有限性、OHLC 关系、volume>=0 与
  available_at<=as_of（未来数据拒绝），与观察路径共享同一类型。
TEST_EVIDENCE=
  tests/test_jianghe_visual_renderer.py + tests/test_jianghe_visual_renderer_adversarial.py
  （OHLC 攻击、未来泄露、极端数值全部拒绝）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### O-03

```text
ID=O-03
ORIGINAL_FINDING=old ChartRender 与新 visual artifact 需要 canonical bridge。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  canonical_visual_artifact_identity()（src/jianghe_ai_trader.py）统一旧
  ChartRender 与新 PNG renderer 的 visual provenance identity；ChartRender 用
  其计算并校验 visual_artifact_identity；VisualArtifact.from_canonical_observation
  走 integrated renderer 生成统一受支持路径。
TEST_EVIDENCE=
  tests/test_jianghe_ai_trader_foundation.py + tests/test_jianghe_visual_renderer.py。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

---

## NORMALIZER/PROMPT — normalizer 与 prompt

### N-01

```text
ID=N-01
ORIGINAL_FINDING=无 governed raw-response normalizer。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  src/jianghe_response_normalizer.py：NORMALIZER_VERSION=
  JIANGHE_RUNTIME_RESPONSE_NORMALIZER_V0_1、NORMALIZER_IDENTITY 版本化；
  JiangheResponseNormalizer.normalize 严格解析，未知/缺失字段、非严格 schema、
  自评字段全部拒绝。
TEST_EVIDENCE=
  tests/test_jianghe_response_normalizer.py。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### N-02

```text
ID=N-02
ORIGINAL_FINDING=live fidelity exact prompt package identity 尚未冻结。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json 为
  CANDIDATE_PRE_LIVE_NON_OUTCOME 候选 prompt package，记录全部 identity；
  本轮已把 context_selection.knowledge_scope 从
  CURRENT_ACTIVE_JIANGHE_V1_1_PLUS_PRIMARY_REGISTRY_V0_3 机械 rebind 为
  ..._V0_5，并按既有 canonical serialization/hash 语义重算
  context_selection_identity=5fc4c18008cfbdff739d1f4e243c24cdb408053b60eb9cab55548b6eb86823c7、
  prompt_package_identity=4f1597a994fe375f52e8bc225decf15d0f85694e688467b53c19acc0a2c322d9。
TEST_EVIDENCE=
  tests/test_jianghe_prompt_package.py：
  test_prompt_package_identities_match_exact_checked_in_content +
  test_primary_scope_rebound_to_v0_5_not_v0_3。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### N-03

```text
ID=N-03
ORIGINAL_FINDING=real-model-specific firewall tests 不完整。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  tests/test_jianghe_real_model_firewall.py 覆盖当前路径：未知 outcome 字段、
  raw_text/metadata 污染、call_success=False、corpus mismatch、VISUAL/
  STRUCTURED/DUAL/OPERATIONAL_PROVIDER 缺 provenance、不读取 protected
  artifact、evaluator/renderer 无 network、无 paid/live call。
TEST_EVIDENCE=
  tests/test_jianghe_real_model_firewall.py 全部通过。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### N-04

```text
ID=N-04
ORIGINAL_FINDING=runtime normalizer 与 fidelity evidence extractor 必须分离，
     不允许模型自评 labels 后直接当评价事实。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  _FORBIDDEN_SELF_EVALUATION_FIELDS 拒绝模型输出的
  violated_principles/invented_thresholds/fidelity_score 等自评字段；
  EvaluatorSideJudgment（evaluator-side）是这些字段唯一来源，且必须匹配
  EVALUATION_EXTRACTOR_IDENTITY；build_fidelity_response_payload 只从
  evaluator_judgment 取 violated/invented，runtime evidence 只贡献客观字段。
TEST_EVIDENCE=
  tests/test_jianghe_response_normalizer.py（自评拒绝与 extractor 分离断言）。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

---

## PROCESS — 过程

### P-01

```text
ID=P-01
ORIGINAL_FINDING=原来 visual+provider -> live probe 的路线过于乐观。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  原审计的 reaudit gate 条件 1-5 已在本 integration tree 满足：fidelity 证据
  完整性修复、WorkBuddy visual renderer 按文件/hash 独立搬运并 review、
  real-model firewall 通过、combined latest-main full suite 0/0、本 gate
  re-audit 逐项复核。条件 6（Owner 请求 live probe approval）是 PASS 之后的
  Owner 动作，已记录为 NEXT_NORMAL_PHASE，不在本 gate 内。
TEST_EVIDENCE=
  本文件 + 本 integration full suite（1195 tests OK）。
REMAINING_RISK=OWNER_LIVE_PROBE_APPROVAL_IS_A_FUTURE_GATE_NOT_THIS_REAUDIT
```

### P-02

```text
ID=P-02
ORIGINAL_FINDING=PRIMARY 结构完整，但 final freeze 前仍需 actual curated JSONL
     adversarial sampling。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT_V0_1.md
  记录独立 WorkBuddy read-only audit：AUDITOR_ROLE=
  INDEPENDENT_LOCAL_WORKBUDDY_READ_ONLY，CANDIDATE_COMMIT=
  08dc196e1a889c9d17070a767a24a41aab2f17d6，R1-R8 全 PASS，
  PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT=PASS；对应 V0.5 gate artifact
  （docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_GATE_V0_5.json）与
  repair review（JIANGHE_PRIMARY_CURATED_QUALITY_REPAIR_V0_2.md）。
  固定 rubric 明确禁止以 prose uniqueness / difflib / sentence-template 作为
  gate（本 re-audit 未使用这些作 gate）。
TEST_EVIDENCE=
  tests/test_jianghe_primary_curated_quality_v0_5.py 全部通过。
REMAINING_RISK=NONE_FOR_THIS_GATE（PRIMARY freeze 仍为 Owner 决策）
```

### P-03

```text
ID=P-03
ORIGINAL_FINDING=WorkBuddy visual branch old-base + manual loose-ref 恢复，
     需要按文件/hash 搬运。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  独立对抗审计 docs/reviews/JIANGHE_VISUAL_RENDERER_LOCAL_ADVERSARIAL_AUDIT_V0_1.md
  以 blob/hash 验证（png_sha256/config/input/artifact 四层哈希独立重算、
  跨进程确定性 PASS）并发现 F-ADV-01/02/03；当前 tree 已修复：
  render() 用 localcontext(_fixed_decimal_context())（F-ADV-01）、
  CLI 原子 (PNG, manifest) pair 写入（F-ADV-02）、极端 Decimal
  |adjusted|<=100 / format 长度<=256 fail closed（F-ADV-03）；
  WorkBuddy 本地实现按保护 commit 2d885a5 搬运并在
  JIANGHE_AI_FIDELITY_AND_REPLAY_INTEGRATION_REVIEW_V0_1.md 审查。
TEST_EVIDENCE=
  tests/test_jianghe_visual_renderer_adversarial.py（含三 finding 回归测试），
  与 tests/test_jianghe_visual_renderer.py 合计 111 tests OK。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

### P-04

```text
ID=P-04
ORIGINAL_FINDING=combined latest-main full suite 尚未完成。
CURRENT_STATUS=CLOSED
CLOSING_EVIDENCE=
  本 integration tree 已合并 PRIMARY V0.5 + prompt rebind + visual + provider
  + normalizer + evaluator + identity/replay 于同一 latest-main descendant；
  python -m compileall -q src tools tests 通过；full suite 1195 tests
  0 failures / 0 errors；git diff --check 通过。
TEST_EVIDENCE=
  本 integration 的 full suite 与 diff check 输出。
REMAINING_RISK=NONE_FOR_THIS_GATE
```

---

## 安全边界

```text
OUTCOME_ACCESS=NO
LIVE_MODEL_CALLS=0
PAID_SPEND=0
PRIMARY_FREEZE=NO
PRIMARY_ELIGIBLE=NO
```

## 裁决含义

`PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS` 只意味着原 pre-live audit 的全部 finding
在当前 integrated tree 已闭环。它不授权真实 provider/model 调用、付费、candidate
outcome、Validation/Final/Shadow、Broker 或 real-money。真实 model fidelity probe
仍需 Owner 明确授权（credentials/data egress/paid spend），且不解锁 candidate
outcomes。
