# PROJECT_DIRECTION

As of: `2026-08-25`

This file is the single current product/research direction for `kline-playbook-engine`.

If another active document conflicts with this file on product direction, model scope, memory/learning philosophy, or long-term target, this file wins unless the Owner explicitly changes it later.

Do not preserve superseded product plans in active takeover text. Git history is sufficient for obsolete plans.

---

# 1. One-sentence mission

Build one persistent, single-purpose China-futures AI trader whose only active model is DeepSeek, whose initial trading foundation is Jianghe's documented experience, and whose long-run goal is to become a more mature evidence-driven trader through governed memory, replay, reflection, hypothesis generation, falsification and validation without silently rewriting Jianghe source truth.

Canonical short name:

`JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

---

# 2. Non-negotiable product definition

The product is NOT a generic chatbot, generic coding agent, multi-provider model router, general research assistant, multi-agent company, or broad finance copilot.

It is a dedicated futures-trading workstation/runtime with one job:

`observe market -> recall relevant Jianghe + own experience -> reason -> decide -> record -> learn under governance`

The intended end-state is closer to a persistent professional trader than to repeated stateless API question answering.

The trader should be able to:

- continuously follow futures markets through time;
- view causal multi-timeframe market data and standardized K-line charts;
- retain current market hypotheses and prior decisions across restarts;
- retrieve only the Jianghe knowledge relevant to the present situation;
- use tools to inspect data, render charts, search prior cases and write structured notes;
- keep an auditable trading journal;
- remember prior mistakes and prior state transitions;
- propose new trading hypotheses from accumulated experience;
- actively search for counterexamples to its own hypotheses;
- promote only independently validated extensions into active project trading policy;
- remain able to say `WAIT` / `NO_TRADE` when evidence is incomplete or contradictory.

The product does NOT receive authority to control hard risk, broker/account truth, order lifecycle truth, safety overrides or real-money execution merely because the AI trader becomes more capable.

---

# 3. Model scope is closed

Current model/runtime policy:

- DeepSeek is the only active AI model source for Jianghe trading research and product development.
- Current selected model line: `deepseek-v4-flash-vision-exp` until an explicit later Owner decision changes the DeepSeek model generation.
- MiniMax is not a reserve, fallback, shadow comparator or future automatic candidate.
- Kimi is not a reserve, fallback, shadow comparator or future automatic candidate.
- Do not spend engineering or paid-evaluation budget maintaining MiniMax/Kimi adapters for this project.
- Do not design a multi-provider abstraction merely to preserve removed providers.
- Test doubles/mocks may exist for deterministic tests, but production-facing model code should be DeepSeek-specific where that is simpler and clearer.

If a materially new DeepSeek model generation appears, it may be evaluated as a DeepSeek upgrade. Reopening other providers is a new Owner model-selection decision, not a default engineering option.

---

# 4. Jianghe remains the origin, not the ceiling

Jianghe source material is the trader's initial expert foundation.

The project must distinguish three different things:

1. what Jianghe actually said or demonstrated;
2. what DeepSeek currently believes about a market;
3. what the project later validates as a useful extension beyond the Jianghe source.

These must never be merged into one unlabeled knowledge pool.

The long-run goal is NOT to freeze DeepSeek forever as a perfect Jianghe impersonator.

The long-run goal is:

`JIANGHE-TRAINED -> EXPERIENCE-ACCUMULATING -> EVIDENCE-IMPROVING AI TRADER`

DeepSeek may eventually outperform the original Jianghe source application by accumulating more cases, remembering more consistently, testing hypotheses systematically and learning from verified experience.

However, "self-improvement" must mean evidence-governed improvement, not unrestricted self-editing.

---

# 5. Knowledge hierarchy

The runtime must preserve a strict hierarchy.

## 5.1 `JIANGHE_CANON`

Contains source-grounded Jianghe claims, cases, contradictions, unknowns and accepted source interpretation.

Rules:

- read-only to the trading agent;
- DeepSeek cannot rewrite it;
- DeepSeek cannot relabel its own idea as Jianghe's idea;
- source provenance must remain traceable;
- uncertainty in the source remains uncertainty rather than being filled with invented certainty.

The source record may remain in Git/evidence even if later active project policy goes beyond it. "Beyond Jianghe" must not falsify the historical source record.

## 5.2 `PROJECT_VALIDATED_POLICY`

Contains trading extensions or operationalizations that the project has independently validated.

These may be stronger, narrower or more specific than Jianghe's documented source when evidence justifies it.

They must be labeled as project-validated extensions, not Jianghe quotes.

A project-validated policy may eventually change how the AI acts even when Jianghe was silent or less specific. A direct contradiction with a source-backed Jianghe principle requires an explicit Owner research decision before becoming active policy.

## 5.3 `DS_HYPOTHESIS_MEMORY`

Contains DeepSeek-generated candidate ideas that are not yet validated.

Examples:

- a suspected extra condition for a breakout family;
- a possible context where a Jianghe setup degrades;
- a recurring failure mode observed in a product or session;
- a possible interaction between higher-timeframe state and lower-timeframe confirmation.

These hypotheses are allowed to guide research and attention, but may not silently become executable trading rules.

## 5.4 `DS_WORKING_MEMORY`

Contains the trader's current market state:

- active hypotheses;
- timeframe-specific interpretation;
- key/watch/invalidation regions;
- current family candidate;
- expected trigger;
- open questions;
- current attention state;
- prior meaningful decisions that remain relevant.

This memory is persistent across calls and restarts, but it is mutable and auditable.

## 5.5 `DS_JOURNAL`

Contains reflective notes and self-critique.

It may say things such as:

- "I over-weighted a 4H background condition";
- "I treated a wick poke as stronger than the evidence allowed";
- "I failed output-contract discipline";
- "I should search for failed analogues before promoting this pattern."

Journal text is not market fact, not Jianghe canon and not validated policy.

---

# 6. What "memory" means

The project must not simulate memory by endlessly appending the entire chat history to every API call.

Persistent memory is an external, project-owned system.

Each DeepSeek call should receive a deliberately selected context assembled from:

1. stable system / trading contract;
2. relevant Jianghe canon;
3. relevant validated project policy;
4. current working memory for the instrument/session;
5. retrieved analogous historical decisions/cases when useful;
6. current causal market observation and charts;
7. task-specific tool results.

The context selector is part of `JiangheAITraderIdentity` and must be versioned/audited because changing retrieval changes the trader.

The agent must not assume that "more context is always better". Relevance, provenance and bounded context are required.

---

# 7. Learning is allowed, but direct self-rewriting is forbidden

DeepSeek is allowed to learn in the functional sense:

- remember;
- reflect;
- compare current situations to past situations;
- identify repeated mistakes;
- propose new hypotheses;
- design searches for confirming and disconfirming cases;
- revise or abandon its own hypotheses;
- accumulate a reusable skill/case library;
- improve its future reasoning through retrieved experience.

DeepSeek is NOT allowed to:

- directly edit `JIANGHE_CANON`;
- directly promote its own hypothesis into active policy;
- change its risk limits;
- change validation/holdout boundaries;
- rewrite historical decisions or evidence;
- treat recent profit as proof of correctness;
- treat recent loss as proof of incorrectness;
- optimize against protected future/validation data outside an authorized research protocol;
- silently change the product's objective or trading philosophy.

---

# 8. Required learning lifecycle

Any new experience-derived trading idea must move through this exact conceptual path:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

No stage may be skipped because DeepSeek is confident.

## 8.1 Observation

The agent notices a repeated pattern, mistake, market condition or apparent opportunity.

This creates a traceable note, not a rule.

## 8.2 Hypothesis

The agent must state the proposed relationship precisely enough to be falsifiable.

A hypothesis record must include at least:

- hypothesis identity;
- statement;
- market/setup scope;
- source status (`DS_DERIVED`, not Jianghe unless genuinely source-backed);
- examples that motivated it;
- known counterexamples;
- what evidence would falsify it;
- discovery data exposure lineage.

## 8.3 Counterexample search

Before trying to prove itself right, the system must actively search for similar cases where the hypothesis fails.

The project should prefer adversarial falsification over self-confirmation.

## 8.4 Development evidence

The hypothesis may be explored on authorized development data with multiplicity/search history recorded.

Repeated redesign after seeing results counts as additional search exposure; it must not be disguised as one clean test.

## 8.5 Independent validation

A candidate extension only becomes trusted when tested on data not used to invent/tune it, under a protocol frozen before looking at the validation result.

## 8.6 Promotion

Only after the required evidence passes may the project promote the idea into `PROJECT_VALIDATED_POLICY`.

Promotion changes the effective AI Trader version.

If the promoted idea materially changes the trading philosophy or contradicts Jianghe canon, Owner approval is required.

---

# 9. Process correctness and trading outcome must stay separate

The system must never learn using the shortcut:

`profit = correct reasoning`

or

`loss = incorrect reasoning`.

Every replay/decision should preserve separate concepts:

- `PROCESS_CORRECTNESS`: whether the decision followed available facts, Jianghe/active policy and causal evidence correctly at decision time;
- `OUTCOME`: what happened later;
- `RISK/EXECUTION_RESULT`: what a simulated or real position would have produced under a defined execution model.

A good process can lose. A bad process can win.

Outcome can generate research questions, but outcome alone cannot promote a rule.

---

# 10. Historical replay must simulate a life, not a stack of independent exam questions

Large-scale K-line use should eventually run as chronological replay.

The core semantics are:

- time moves forward;
- future information is unavailable until it becomes available;
- working memory persists forward in time;
- decisions and notes become part of later accessible experience according to the memory policy;
- the agent is not called on every 1-minute bar by default;
- deterministic state/attention logic decides when an AI wake-up is useful.

Expected attention states remain conceptually:

`SCAN -> WATCH -> CANDIDATE -> IN_POSITION`

Potential wake events include:

- meaningful bar close;
- entry/exit from a watch region;
- breakout/failed-breakout candidate;
- invalidation touch;
- state/family transition;
- session event;
- later, when authorized, order/position/safety events.

The goal is to test one persistent trader moving through market history, not thousands of stateless prompt calls.

---

# 11. DeepSeek Harness direction

DeepSeek Harness is the preferred external runtime substrate to evaluate for the persistent trader because it may provide session, tool, workspace, persistence and UI infrastructure.

Project status at this direction decision:

`DEEPSEEK_HARNESS = CANDIDATE_FOR_PROJECT_ADMISSION`

It is not automatically trusted or adopted merely because it is DeepSeek-associated.

Before adoption, the project must verify a pinned version/commit against these mandatory capabilities:

- exact selected DeepSeek API/model path can be used;
- vision/K-line image input works correctly for the selected model path;
- persistent session/state survives restart;
- project-owned memory can be integrated without being trapped inside the framework;
- project-owned tool interfaces can render/retrieve K-line information;
- raw model requests/responses and memory mutations remain auditable;
- no framework behavior silently retries, changes model, changes prompt or bypasses project governance;
- core trading logic remains project-owned and portable if Harness is later replaced.

If Harness fails these gates, do not change the product direction. Replace only the runtime substrate with the thinnest project-owned equivalent.

---

# 12. UI/workstation target

The Owner-facing product should eventually feel like a dedicated trading workstation, not an engineering console.

Minimum useful surfaces are:

- synchronized 4H / 1H / 15m / 5m K-line views;
- current DeepSeek interpretation;
- active Jianghe family / state / action;
- key/watch/invalidation regions;
- what DeepSeek is waiting for;
- relevant Jianghe evidence/cases it retrieved;
- current working memory;
- recent decisions and journal entries;
- later, validated hypothesis/research status;
- system/risk/safety status when those lanes are authorized.

Drawing/annotation tools may be added when they improve Jianghe reasoning, but UI polish is secondary to correct persistent-trader behavior.

A local-first web UI is acceptable. A desktop wrapper is optional. Do not let packaging choice become the architecture.

---

# 13. Deterministic systems remain outside AI discretion

Even after the trader becomes more mature:

- market/account/broker facts remain deterministic/project-owned;
- hard risk remains deterministic;
- order lifecycle remains deterministic;
- safety/kill switch remains deterministic;
- audit ledger remains immutable factual history;
- AI hypotheses remain labeled hypotheses until evidence promotes them.

The AI may propose a `TradeIntent`; it does not get unrestricted authority over money.

---

# 14. Known DeepSeek hardening requirements

Before broader replay, preserve the two known mechanical protections from the final-chance study:

1. `STRICT_OUTPUT_ENUM_ENFORCEMENT`
   - action/direction/family machine fields must use exact allowed values;
   - explanations belong in separate text fields.

2. `NO_4H_EXACT_VOLUME_RECONCILIATION`
   - 4H volume must not be exactly reconciled against overlapping lower-timeframe volume;
   - 4H remains background/state/location context under the current Jianghe interpretation unless later research explicitly changes that policy.

These are engineering guards, not new Jianghe doctrine.

---

# 15. Current implementation order

The next implementation sequence is fixed unless the Owner changes direction:

1. finish the two narrow DeepSeek hardening items;
2. perform project-level DeepSeek Harness admission review on a pinned version/commit;
3. build the smallest persistent trader prototype that proves exact model + vision + memory + Jianghe retrieval + K-line tools + journal + audit;
4. run a small chronological lifecycle replay to find architecture/memory errors, not to optimize trading performance;
5. only after the persistent-trader identity is stable, design and authorize broader historical replay/research;
6. use large historical data to accumulate experience and test hypotheses under strict discovery/validation separation;
7. keep shadow/broker/real-money locked until later explicit authorities.

Do not skip directly to massive API replay with a stateless trader.

Do not spend time building a polished full website before the persistent memory/reasoning loop is proven.

---

# 16. What future project brains must not do

Do not:

- reopen MiniMax/Kimi selection;
- add generic multi-provider routing;
- convert the product into a general assistant;
- allow DeepSeek's journal to become Jianghe canon;
- allow DeepSeek to promote its own strategy changes without evidence gates;
- optimize against future/holdout data because "the AI is learning";
- equate PnL with reasoning correctness;
- make memory an unbounded chat transcript;
- make Harness the owner of core trading knowledge/business logic;
- replace chronological replay with independent random prompt exams when studying persistent learning;
- let historical/outdated project plans remain in the active takeover path.

When an active plan is replaced, update the current authority to only state the new truth and remove obsolete active documents/references from the current tree when they no longer serve a live purpose. Git history is the historical record.

---

# 17. Success definition

The project succeeds if it produces a DeepSeek-based futures trader that:

- begins with high-fidelity Jianghe reasoning;
- remembers what it was watching and why;
- learns from its own audited experience without corrupting source truth;
- becomes more stable through tools, validators and memory;
- can generate new falsifiable trading hypotheses;
- can reject its own weak ideas using counterexamples;
- can promote only independently validated improvements;
- remains causally honest and auditable;
- can eventually demonstrate, on protected evidence, that its matured policy is better than the initial Jianghe-only baseline;
- still remains under deterministic risk/safety/execution control.

The desired identity is not "a DeepSeek chat session with Jianghe pasted into it".

It is:

`A PERSISTENT, AUDITABLE, JIANGHE-TRAINED, EVIDENCE-IMPROVING DEEPSEEK FUTURES TRADER`.
