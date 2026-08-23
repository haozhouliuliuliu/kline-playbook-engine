# 国产 Provider 候选范围与 Pre-Spend 正确执行顺序 V0.1

> Status: `COMPLETE__ZERO_COST_ELIGIBILITY_REQUIRED_BEFORE_BATCHED_REPAIR`
> Date: 2026-08-24
> Baseline main: `a3ac72deccd5381a100d48ae2347412b500c65e6`
> Scope: Owner payment/access constraint, domestic candidate hard eligibility, and sequencing before the frozen pre-spend repair package.
> This document does **not** authorize paid calls and does **not** change the frozen BSP/RSP finding set.

## 1. Owner payment/access constraint

The Owner reports that direct recharge/payment is not available for OpenAI/ChatGPT and xAI/Grok for this project. Therefore they are no longer practical spend candidates for the current RMB 100 probe even if technically capable.

Current practical domestic candidate pool proposed by Owner:

```text
KIMI_K3
DEEPSEEK_V4_FLASH_VISION_EXP
MINIMAX_M3
GLM_5_3_WITH_REASONING_EFFORT_MAX
```

`GLM-5.3 Max` is not a separate model ID. First-party Z.ai material identifies the model as `glm-5.3` and `max` as the `reasoning_effort` level.

## 2. Zero-cost hard eligibility result

The current product/research requirement remains:

```text
REAL_MODEL_SELECTION_MUST_INCLUDE_VISUAL_KLINE_EYES=YES
```

The candidate used for Jianghe visual fidelity must itself receive the canonical K-line image input. A separate vision MCP/tool that converts the image before a text-only decision model is **not** equivalent under the current research design and would require a separate Owner-approved research-design change.

### Kimi K3 — HARD-ELIGIBLE

First-party Kimi API documentation currently confirms:
- model id `kimi-k3`;
- direct API at `https://api.moonshot.ai/v1`;
- native visual understanding and direct image/video input;
- 1M context;
- strict `json_schema` structured output with `strict: true` and `additionalProperties: false`;
- minimum successful top-up requirement of USD 1;
- current public rate: cache hit USD 0.30/MTok, input USD 3/MTok, output USD 15/MTok.

First-party authority:
- https://platform.kimi.ai/docs/guide/kimi-k3-quickstart
- https://platform.kimi.ai/

### DeepSeek V4 Flash Vision Exp — HARD-ELIGIBLE, EXPERIMENTAL

The previous exclusion was already formally corrected. DeepSeek's official `deepseek-ai/deepseek-harness` 2026-08-21 release includes `deepseek-v4-flash-vision-exp` in its default catalog with `inputModalities: [text, image]` and direct DeepSeek API handling.

Candidate-specific risks remain experimental model drift and aggressive provider-side image compression. These are fidelity risks to test, not pre-test disqualifiers.

Authority:
- `docs/reviews/DEEPSEEK_V4_FLASH_VISION_EXP_FIRST_PARTY_CORRECTION_V0_1.md`
- https://github.com/deepseek-ai/deepseek-harness

### MiniMax M3 — HARD-ELIGIBLE FOR VISUAL INPUT; STRUCTURED-OUTPUT CONTRACT TO VERIFY IN TRANSPORT IMPLEMENTATION

First-party MiniMax material currently confirms:
- model id `MiniMax-M3`;
- direct MiniMax API;
- native multimodal model with image/video input;
- API context up to 1M tokens;
- current public API pricing page lists M3 at permanently discounted rates around USD 0.30/MTok input and USD 1.20/MTok output for context <=512K, with higher long-context tier above 512K.

The currently indexed generic MiniMax API reference still contains stale structured-output wording from older model generations. Therefore exact native `json_schema` enforcement for M3 should be verified against the live/current model contract during BSP-004 implementation; this is not a visual-eligibility blocker because the project runtime normalizer already fails closed on malformed output.

First-party authority:
- https://www.minimax.cn/models/text/m3
- https://platform.minimax.io/subscribe/token-plan

### GLM-5.3 + reasoning_effort=max — NOT HARD-ELIGIBLE FOR CURRENT DIRECT-VISUAL PROBE

First-party Z.ai material confirms:
- model id is `glm-5.3`;
- `reasoning_effort` supports `low`, `high`, `max`, default `max`;
- the model is a language/coding model with 1M-context evaluation use;
- current Zhipu model-family documentation separates language models from vision models, and the immediately preceding same-base GLM-5.2 is explicitly `text -> text`;
- current Z.ai Coding Plan exposes Vision Analysis through MCP/tooling, but that is not evidence that `glm-5.3` itself receives image input.

Therefore under the current direct-visual Jianghe fidelity protocol, GLM-5.3(max) should not receive paid visual-probe budget unless new first-party evidence establishes native image input or the Owner explicitly authorizes a different research design using a vision sidecar.

First-party authority:
- https://z.ai/blog/glm-5.3
- https://docs.bigmodel.cn/cn/guide/models/text/glm-5.2
- https://docs.bigmodel.cn/cn/guide/start/model-overview

## 3. Correct sequencing: repair before any spend, but only after zero-cost eligibility scope

The project should **not** spend first and repair later. All five BSP blockers must close before a paid call.

However, a small zero-cost eligibility decision must precede the batched repair because:
- BSP-004 requires real provider-specific transports;
- BSP-005 requires provider/model-specific rate-card, image/token billing and actual-usage reconciliation rules;
- implementing transports for candidates that cannot satisfy direct visual input would create avoidable work and broaden the spend surface.

Correct sequence:

```text
0. ZERO-COST HARD ELIGIBILITY
   -> no model calls, no spend
   -> establish which domestic APIs satisfy direct visual + usable transport requirements

1. OWNER CONFIRMS IMPLEMENTATION TARGET SET
   -> this selects which provider transports/rate cards to implement
   -> does NOT authorize paid calls

2. ONE BATCHED PRE-SPEND REPAIR
   BSP-001 content-addressed Jianghe selected context
   BSP-002 strict closed-world canonical structured observation
   BSP-003 evaluator-grounded positive/negative principle evidence
   BSP-004 real transports for selected providers, live disabled by default
   BSP-005 executable shared RMB 100 cumulative hard budget guard
   RSP-001 authoritative TradingState admission before OMS side effects
   RSP-002 same intent_id + different semantic content fails closed

3. VERIFICATION
   -> finding-specific focused/adversarial tests
   -> canonical full suite: python -m unittest discover -s tests -v
   -> finding-specific re-audit only
   -> write CLOSED/PASS evidence and refresh state

4. SEPARATE OWNER PAID-CALL AUTHORIZATION
   -> only after all BSP-001..005 are CLOSED

5. RMB 100 FUNNEL PROBE
   Stage A: tiny qualification spend per eligible candidate
      - 1 smoke
      - small SEMANTIC set
      - small VISUAL set
      - small DUAL_INPUT set
      - schema / identity / usage / latency evidence
      - clearly weak candidate stops immediately
   Stage B: remaining budget goes only to top 1–2 for repeat/stability evidence
```

This preserves the previous funnel idea while preventing money from being spent before the safety/evidence/cost infrastructure exists.

## 4. Current project-brain recommendation

Without changing the frozen direct-visual research requirement, the current likely implementation target set is:

```text
KIMI_K3
DEEPSEEK_V4_FLASH_VISION_EXP
MINIMAX_M3
```

`GLM-5.3(max)` remains a high-capability domestic language/agent model but is not currently a like-for-like direct visual Jianghe candidate on available first-party evidence.

No provider/model is project-VERIFIED or ADOPTED. No live call or paid spend is authorized.

```text
TOOL_DECISION=USE_EXISTING
FROZEN_FINDING_SET_CHANGED=NO
SPEND_GATE=CLOSED
PAID_CALL_AUTHORIZATION=NO
```
