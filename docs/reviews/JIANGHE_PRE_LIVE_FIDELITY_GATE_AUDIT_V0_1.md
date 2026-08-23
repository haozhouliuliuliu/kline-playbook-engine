# JIANGHE PRE-LIVE FIDELITY GATE AUDIT V0.1

> 状态：已确认的 fail-closed 审计结论。
> 本文件是当前 pre-live fidelity gate 的正式裁决；后续修复完成并重新运行 gate audit 之前，任何 live provider probe 均被阻止。

## Audit status（正式裁决）

```text
PRE_LIVE_FIDELITY_GATE_AUDIT=NOT_READY_REPAIR_REQUIRED
LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_AUDIT_REPAIR
PAID_MODEL_SPEND=NOT_AUTHORIZED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
OUTCOME_ACCESS=NO
```

## 裁决理由

原因不是 live provider 失败，而是在 live probe 之前发现证据链缺口：当前 harness
尚不能证明“被评价的 fidelity 证据确实来自同一个 governed observation / visual /
structured input / provider invocation / normalized response”。在证据链闭环之前，
任何真实模型 live fidelity probe 的结论都无法被 project brain 采纳为可复核事实。

## GLOBAL — 全局证据链缺口

```text
G-01 ObservationIdentity 没绑定实际 bars/positions/orders/charts 内容。
G-02 JiangheAITraderIdentity 尚未绑定 governed normalizer + 当前 PRIMARY registry。
G-03 fidelity track label 尚无真实输入 provenance 证明。
```

## FIDELITY — fidelity evaluator 证据完整性缺口

```text
H-01 outcome contamination 目前不会强制 evaluator ERROR。
H-02 unknown response fields 未严格拒绝。
H-03 corpus_id 未和实际 corpus 强绑定。
H-04 call_success=False 仍可能评分。
H-05 arbitrary metadata/input reference 不足以证明 provenance。
H-06 evidence parser 存在 bool/str/int 宽松 coercion。
H-07 无 deterministic full report_identity。
H-08 technical OK 与 evidence completeness/fidelity eligibility 混淆。
```

## PROVIDER — provider 证据缺口

```text
H-09 request artifacts 没严格证明属于同一 observation。
H-10 requested model identity 与 provider-resolved model/version/snapshot 混淆。
H-11 capability identity 未完全绑定 API surface。
H-12 structured input capability 与 JSON output capability 混淆。
H-13 无完整 deterministic provider response evidence identity。
```

## OBSERVATION — 观察证据缺口

```text
O-01 replay decision 未强制绑定 accepted/current observation。
O-02 canonical ObservationBar validation 弱于 visual path。
O-03 old ChartRender 与新 visual artifact 需要 canonical bridge。
```

## NORMALIZER/PROMPT — normalizer 与 prompt 缺口

```text
N-01 无 governed raw-response normalizer。
N-02 live fidelity exact prompt package identity 尚未冻结。
N-03 real-model-specific firewall tests 不完整。
N-04 runtime response normalizer 与 fidelity evaluation evidence extractor 必须分离，
     不允许模型自己提供 self-scoring labels 后直接当评价事实。
```

## PROCESS — 过程缺口

```text
P-01 原来 visual+provider -> live probe 的路线过于乐观。
P-02 PRIMARY 结构完整，但 final freeze 前仍需 actual curated JSONL adversarial sampling。
P-03 WorkBuddy visual branch old-base + manual loose-ref 恢复，需要按文件/hash搬运。
P-04 combined latest-main full suite 尚未完成。
```

## 修复范围（后续 repair 包）

修复必须 fail-closed，且不引入：

- candidate outcome / P&L 访问；
- Validation / Final / Shadow；
- broker / real money；
- 真实模型 API call / paid spend；
- PRIMARY semantic freeze；
- Jianghe source semantics 修改；
- force rewrite main history。

修复目标见 `CURRENT_STATE.md` / `PROJECT_BRAIN_RUNTIME_BRIEF.md` 中的
`CURRENT_WORK_PACKAGE` 与 `NEXT_NORMAL_PHASE`。

## Reaudit gate

本审计的 `NOT_READY_REPAIR_REQUIRED` 状态在以下条件全部满足前不得翻转：

1. fidelity evaluator 证据完整性修复通过（outcome contamination fail-closed、
   strict schema、corpus binding、failed-call non-scoreable、strict types、
   typed provenance、metadata allowlist+scan、deterministic report_identity、
   三态分离）；
2. WorkBuddy visual renderer 按文件/hash 独立搬运并 review 通过；
3. real-model firewall tests 通过；
4. combined latest-main full suite 0 failures / 0 errors；
5. 重新运行本 gate audit 并确认无剩余缺口；
6. Owner 明确请求 live probe approval。

在此之前：`LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_AUDIT_REPAIR`，
`OWNER_ACTION=NONE_UNTIL_REAUDIT_PASSES_AND_LIVE_PROBE_APPROVAL_IS_REQUESTED`。
