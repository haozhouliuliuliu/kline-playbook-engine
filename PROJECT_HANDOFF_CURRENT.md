# PROJECT_HANDOFF_CURRENT

> Derived continuity handoff. **handoff != authority**.
> Fresh conversations must reconstruct truth from current GitHub `main` and formal authority first. This file exists to prevent loss of the current problem set and sequencing across conversation rollover.

## Mandatory fresh-conversation behavior

Do **not** start from this handoff alone.

1. fetch canonical repo `haozhouliuliuliu/kline-playbook-engine` current `main` HEAD;
2. read `00_READ_FIRST.md` and follow its read-only takeover order;
3. read `PROJECT_BRAIN_RUNTIME_BRIEF.md` and `CURRENT_STATE.md` from that same current `main`;
4. read the current formal pre-spend finding authority:
   `docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md`;
5. read the exact source/authority files named by that review as needed to independently verify the findings;
6. only after reconstructing current phase/locks/findings, read this file last as a continuity check;
7. first takeover turn is read-only: report understanding/contradictions and stop for Owner acceptance;
8. after Owner acceptance, every substantive reply follows `PROJECT_BRAIN_RUNTIME_BRIEF.md` refresh rules.

If this handoff conflicts with current `main`, `CURRENT_STATE.md` or formal authority, **current `main` wins**.

---

# Handoff state at conversation rollover

The previous project-brain conversation completed the Owner-requested double pre-spend assurance review and consolidated the results. The audit did **not** authorize live provider calls or spend.

The current durable result is:

```text
PRE_SPEND_DOUBLE_AUDIT=COMPLETE_FAIL_REPAIR_REQUIRED
CONSOLIDATED_FINDINGS=FROZEN
BLOCKER_BEFORE_SPEND=5
REPAIR_RECOMMENDED_BEFORE_SPEND=2
SPEND_GATE=CLOSED
LIVE_CALLS=0
PAID_SPEND=0
OUTCOME_ACCESS=NO
PRIMARY_FREEZE=NO
TOOL_DECISION=USE_EXISTING
```

The original PRIMARY fixed-rubric re-audit remains PASS. The original 27-item pre-live fidelity gate remains PASS. The new blockers below are a later Owner-requested pre-spend assurance layer and must not be confused with reopening old PRIMARY prose/template issues.

Formal detailed authority:

`docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md`

Active limitation pointer:

`LIMIT-015` in `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`

---

# Design handoff rule: freeze the problem and acceptance criteria, not the code design

The outgoing project brain deliberately chose **not** to prescribe exact classes/modules/implementation architecture for the repair.

What is frozen:

- the seven finding IDs below;
- their current evidence basis;
- the safety/evidence/cost invariants that a repair must prove;
- the rule that model self-report cannot grade itself;
- the rule that exact material sent to a provider must be auditable/content-addressed;
- the Owner's RMB 100 total hard cap;
- all existing outcome/broker/real-money/PRIMARY locks.

What is **not** frozen:

- exact new class names;
- exact module boundaries;
- whether a safe solution uses one artifact class or a small composition of artifacts;
- exact evaluator implementation method, provided it is evaluator-side and auditable;
- exact provider SDK/HTTP choice, which depends on the final Owner-selected provider(s).

Reason: the next fresh project brain should independently verify current `main` before editing and choose the simplest correct implementation. A handoff should not force a potentially suboptimal code design merely because the previous conversation is ending.

The next brain should **not restart an open-ended audit**. It should verify these frozen findings, reject a finding only with concrete contrary repository evidence, and then proceed toward one bounded repair package after the required Owner provider-selection decision.

---

# All current concrete findings

## BSP-001 — Real paid request does not yet bind and send a content-addressed Jianghe knowledge/context artifact

**Classification:** `BLOCKER_BEFORE_SPEND`

### What exists today

The checked-in prompt package correctly says the knowledge scope is:

`CURRENT_ACTIVE_JIANGHE_V1_1_PLUS_PRIMARY_REGISTRY_V0_5`

and the provider request correctly sends the actual compact system prompt / decision prompt text plus optional visual/structured artifacts.

### What is missing

The scope label is not the actual Jianghe knowledge material.

The current `JiangheModelRequest` / transport path does not separately bind and materially send a deterministic selected Jianghe context artifact that proves:

- which current V1.1 / PRIMARY V0.5 material the model saw;
- which knowledge-pack identity it came from;
- which PRIMARY registry/interpretation authority it came from;
- which context-selection policy produced it;
- the exact selected content hash/identity;
- which governed working-memory snapshot was included, if any.

### Why it matters

Without this, a future paid model could be tested mostly on generic prompt-following and chart reading while the evidence merely claims a V1.1/V0.5 scope label. That would make the paid Jianghe-fidelity result ambiguous and potentially misleading.

### Required outcome, without locking implementation

A spend-eligible request must be able to prove the exact material actually sent, content-address it, bind it into request/evidence identity, reject forbidden outcome/future/fixture material, and reproduce the same context deterministically.

Do **not** solve this by blindly sending all 352 claims every call. Minimal deterministic selection is preferred when sufficient; unnecessary full-context egress would waste tokens and money.

Full invariants/tests are in the consolidated findings authority.

---

## BSP-002 — Structured input is not yet a strict closed-world canonical observation artifact

**Classification:** `BLOCKER_BEFORE_SPEND`

### What exists today

`StructuredInputArtifact` hashes its payload, binds an observation identity, rejects explicitly forbidden field names and can reject forged declared hashes.

### What is missing

Its payload is still a generic `Mapping[str, Any]`. A caller can construct arbitrary extra fields as long as the names are not explicitly forbidden. The current generic scan does not convert this into a strict market-observation schema and does not provide a proof that only the canonical Jianghe observation left the process.

Current tests also manually construct small dictionaries instead of requiring one canonical serializer from `JiangheObservation`.

### Why it matters

A real provider call must have a closed, auditable data-egress surface. Arbitrary structured extensions create a route for stale data, free-form context or unauthorized information to be sent while still producing a valid-looking artifact hash.

### Required outcome

Spend-eligible structured input must use a strict versioned schema with unknown-field rejection, be generated from canonical observation authority, bind exact serialized content to the canonical observation identity, and leave no arbitrary free-form extension channel.

Full adversarial acceptance criteria are in the formal findings file.

---

## BSP-003 — Model-declared `principle_references` can currently become positive scoring evidence

**Classification:** `BLOCKER_BEFORE_SPEND`

This is one of the most important findings because it can directly bias model selection.

### Current path

The model is allowed to output `principle_references`.

The normalizer correctly records those as raw fields the model actually emitted.

But the current bridge maps model-declared `principle_references` into scorer-side `acknowledged_principles`.

The fidelity fixture scorer has many PASS paths that require `principle_acknowledged`.

### Resulting defect

A model can effectively say “I used JH-PRINC-002” and that self-declaration can become positive evidence that it actually satisfied JH-PRINC-002.

A poor model that emits many likely principle IDs can therefore inflate its apparent Jianghe fidelity.

### Important distinction

The normalizer itself is **not** the problem. Keeping raw model references is useful audit evidence.

The problem is allowing raw self-declared references to become scoring facts.

### Required outcome

Model-declared principle/source references must remain raw evidence only.

Positive `acknowledged_principles`, negative `violated_principles`, and `invented_thresholds` used for scoring must come from an evaluator-side grounded adjudication tied to the fixture/corpus, normalized decision and evaluator identity/evidence.

The exact evaluator implementation is deliberately left for the next project brain to choose after reviewing current main. It may be deterministic extraction, separately governed evaluator review, or another auditable method. The non-negotiable rule is:

**the model may not grade itself.**

A required adversarial test is that a response declaring every `JH-PRINC-*` cannot gain PASS merely from those declarations.

---

## BSP-004 — Real provider transport is intentionally not implemented

**Classification:** `BLOCKER_BEFORE_SPEND`

This is not a regression; it is unfinished pre-live work.

Current provider code explicitly has no real HTTP/SDK/secret-reading path, and live invocation remains disabled. Current state correctly says:

`JIANGHE_AI_REAL_MODEL_PROVIDER=LIVE_TRANSPORT_NOT_IMPLEMENTED_NOT_VERIFIED_NOT_ADOPTED`

### Required outcome

After the Owner chooses the final provider/model set, the project needs one audited canonical real-provider path that:

- is disabled by default and only enabled by explicit Owner authorization;
- never writes credentials to artifacts/logs;
- keeps requested alias separate from provider-resolved model/version;
- records timing, raw response and required usage/provider IDs;
- carries the canonical observation/context/visual/structured identities;
- disables web/search/tools/grounding/code execution unless separately approved;
- distinguishes transport failure from semantic/schema failure;
- does not automatically pay to retry semantic/schema failures;
- does not fork a provider-specific second Jianghe semantics/normalizer/evaluator stack.

Provider-specific implementation must wait for fresh first-party capability/pricing verification and final Owner provider selection.

---

## BSP-005 — RMB 100 hard budget exists in governance but not yet in executable spend control

**Classification:** `BLOCKER_BEFORE_SPEND`

Owner authority is fixed at:

```text
TOTAL_HARD_SPEND_CAP_CNY=100.00
NO_AUTOMATIC_BUDGET_EXTENSION=YES
NO_PROVIDER_SPECIFIC_OVERRUN=YES
```

### What is missing

There is not yet a code-level mechanism that proves, before each real call:

- the provider/model rate card and billing semantics are known/bound;
- maximum output/image/token settings are bounded;
- the worst-case charge fits inside remaining RMB authorization;
- cumulative spend across all selected providers remains below the same total cap;
- retries cannot bypass the cap;
- actual usage/cost is reconciled before the next call;
- unknown pricing, unknown FX, ambiguous image billing or rate-card drift causes fail-closed behavior.

### Required outcome

Budget enforcement must be executable, cumulative and pre-call. It must not rely on the Owner manually watching a dashboard.

Automatic semantic/schema retry should be zero. Any later permitted transport retry must be explicitly bounded and budgeted.

If a provider prices in USD/another currency, an auditable predeclared CNY conversion authority or conservative bound is required before the call. Do not invent an exchange-rate convention silently.

---

## RSP-001 — ShadowRuntime mutates OMS before authoritative TradingState event admission/deduplication

**Classification:** `REPAIR_RECOMMENDED_BEFORE_SPEND`

### Current behavior

`TradingState.apply_broker_event()` has the correct authoritative duplicate/out-of-order/sequence-gap logic.

But `ShadowRuntime.drain_and_apply_events()` currently invokes:

1. `OMS.apply_broker_event(event)`
2. `TradingState.apply_broker_event(event)`

in that order.

OMS fill handling adds fill quantity before TradingState has decided whether the event is a duplicate/rejected fact.

### Risk

A duplicate/replayed fill can mutate or error in the OMS mirror before the authoritative state returns its correct idempotent result.

This does not block the non-broker fidelity probe itself, but it is a real runtime correctness defect and should be included in the same repair package.

### Required outcome

Rejected/no-op broker events must not mutate OMS. Identical duplicate fills must be idempotent across both authorities/mirrors; different-content duplicates and out-of-order/gap events must fail closed without OMS side effects.

Implementation design is open; do not create two competing sequence authorities.

---

## RSP-002 — `ConflictResolver` silently collapses same intent ID without proving the payloads are identical

**Classification:** `REPAIR_RECOMMENDED_BEFORE_SPEND`

The code/documentation says identical duplicate intents may collapse.

The current implementation deduplicates by `intent_id` alone before comparing complete semantic/content identity.

Therefore same ID + different action/direction/quantity/context/reason can be silently reduced to the first occurrence instead of being treated as an identity collision.

### Required outcome

- same ID + same full content identity may collapse deterministically;
- same ID + different full content identity must fail closed;
- input ordering must not decide which conflicting payload silently wins.

---

## NBP-001 — limitations index contained resolved entries contrary to its own maintenance rule

**Classification:** `NONBLOCKING_CLEANUP`

At handoff preparation time, `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` still contained resolved LIMIT-013/LIMIT-014 even though the file says resolved items should leave the active unresolved index.

The handoff integration removes those resolved sections and adds active `LIMIT-015` for the current pre-spend blockers. Historical resolution evidence remains in the durable reviews/Git history.

This was documentation hygiene only and never a spend blocker.

---

# Rechecked suspicions that are NOT current findings

The next conversation should not repeatedly reopen these unless new concrete evidence appears.

## Observation identity

Current canonical observation identity is content-bound. `ObservationIdentity.content_identity` is populated from the visible observation content through `JiangheObservation`, including bars/positions/active orders/schema/visible metadata. The earlier suspicion that changed bars might preserve the same observation identity is not supported by current code.

## Visual provenance

The integrated visual path is strong enough for the current architecture: PNG content hash, renderer/config provenance, canonical observation binding and visual artifact identity are recomputed and forged identities/hashes are rejected. Do not build a second visual stack merely because of this handoff.

## Requested alias vs resolved provider model

Current contract separates requested model selector from provider-resolved model/version and tests exact-snapshot drift rejection. Preserve this.

## Runtime normalizer

Current normalizer has strict JSON/schema/type behavior and recursively rejects explicit forbidden outcome/self-evaluation fields. BSP-003 is a scoring-evidence provenance problem, not a reason to replace the normalizer wholesale.

## Evaluator outer fail-closed behavior

The existing harness already has useful fail-closed controls for malformed responses, duplicate records, corpus mismatch, failed calls, provenance gaps, metadata violations and detected outcome contamination. Preserve those controls while repairing semantic judgment provenance.

## Tools

No new general framework/MCP/large SDK is needed for the frozen repair set.

`TOOL_DECISION=USE_EXISTING`

A selected provider's SDK or direct HTTP layer is a provider-specific implementation choice, not permission to add unrelated infrastructure.

---

# Required sequencing after new-conversation takeover

Do not jump directly into coding on the first new-conversation turn.

### Fresh takeover

The new project brain first follows `00_READ_FIRST.md`, verifies current `main`, reads current formal state/finding authority, reports contradictions/missing authority if any, and waits for Owner acceptance.

### After takeover acceptance

1. Independently verify BSP-001..005 and RSP-001..002 against **current main**, without restarting a broad audit.
2. Recheck current first-party capability/pricing for the remaining provider candidates because provider facts are time-sensitive.
3. Produce the final provider/model cost-capability recommendation under the binding RMB 100 ceiling.
4. The **Owner selects the final provider/model set and bounded probe scope**. That is the next major Owner decision.
5. Then do one batched repair package for every still-valid finding, including selected-provider live transport and executable budget guard.
6. Run finding-specific adversarial/focused tests plus canonical full suite:
   `python -m unittest discover -s tests -v`.
7. Perform a finding-specific re-audit only; do not create another endless whole-project audit loop.
8. Write closure evidence into formal GitHub authority and update `CURRENT_STATE.md` / runtime brief.
9. Only after all five BSP blockers close may the project ask the Owner for a separate explicit authorization to actually spend/call the provider.

No candidate outcome, PRIMARY semantic freeze, broker, account, or real-money authority is implied by any of the above.

---

# Provider/Owner facts that must survive the handoff

Current Owner scope, subject to current-main refresh:

```text
ANTHROPIC_CLAUDE=EXCLUDED_BY_OWNER
GOOGLE_GEMINI=EXCLUDED_BY_OWNER
OPENAI_GPT_5_6_SOL=CANDIDATE_RETAINED
XAI_GROK_4_6=CANDIDATE_UNDER_OWNER_CONSIDERATION
KIMI_K3=CANDIDATE_UNDER_OWNER_CONSIDERATION
DEEPSEEK_V4_FLASH_VISION_EXP=CANDIDATE_UNDER_OWNER_CONSIDERATION__EXPERIMENTAL
FINAL_APPROVED_PROVIDER_SET=NOT_DECIDED
TOTAL_HARD_SPEND_CAP_CNY_IF_LATER_APPROVED=100.00
LIVE_CALLS=0
PAID_SPEND=0
```

Do not reuse old USD-100 / Anthropic / Gemini execution scope. That proposal is superseded.

Because pricing/capability facts change, the next project brain must use fresh first-party sources immediately before final recommendation/implementation. Access in WorkBuddy or another UI does not itself prove programmatic API capability or pricing.

---

# Core product/architecture facts that must not regress

```text
AI_ROLE=JIANGHE_STYLE_MARKET_READING_AND_TRADE_DECISION
MECHANICAL_ROLE=HARD_RISK_ORDER_EXECUTION_RECONCILIATION_SAFETY
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
UNKNOWN_OR_UNFAMILIAR=WAIT_OR_NO_TRADE
INITIAL_MODEL_SELECTION_TARGET=JIANGHE_FIDELITY_NOT_PROFIT
REAL_MODEL_SELECTION_MUST_INCLUDE_VISUAL_KLINE_EYES=YES
HISTORICAL_REPLAY_BASELINE=COMPLETED_1_MINUTE_BAR
SUB_MINUTE_LIVE_IF_ADDED=SEPARATE_VERSION_NOT_1M_EQUIVALENT
PRIMARY_ELIGIBLE=NO
PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
OUTCOME_ACCESS=NO
```

Current knowledge/PRIMARY identities/counts must always be refreshed from current authority rather than copied from this handoff.

---

# Worker/integration discipline for the next conversation

- exactly one integration lane may update `main` and shared authority;
- parallel workers must use different worktrees;
- DS Flash is appropriate for ordinary mechanical repair/review/integration;
- reserve Codex for genuinely high-value architecture/research/complex cross-module work;
- WorkBuddy is treated as local/no-GitHub; before assigning WorkBuddy, tell the Owner the exact local repo/worktree folder and current model, then provide one complete copyable prompt;
- no worker may inspect candidate outcomes or make paid calls under the current locks;
- do not add new tools unless current capability is genuinely insufficient; current decision is `USE_EXISTING`.

---

# Final continuity check

The next conversation is successful if, after read-only takeover, it understands all of the following without relying on old chat:

1. old PRIMARY/pre-live gates are PASS;
2. a later Owner-requested pre-spend assurance review found five real spend blockers and two additional repair-recommended runtime defects;
3. the complete finding authority is the consolidated review file, not this handoff;
4. exact repair implementation is intentionally open, but acceptance/safety/evidence/cost invariants are frozen;
5. current next Owner decision is final provider/model selection after fresh cost/capability review;
6. no live provider call or spend is authorized;
7. once provider scope is selected, the project should do one batched repair, targeted re-audit and full suite — not another rolling audit/fix loop.
