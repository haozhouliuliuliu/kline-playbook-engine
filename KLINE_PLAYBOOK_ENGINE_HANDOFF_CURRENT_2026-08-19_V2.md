# kline-playbook-engine — Current Project Handoff V2

> Snapshot date: 2026-08-19
> Purpose: continuity for a fresh ChatGPT/project-brain conversation after a second-pass omission review.
> **Derived snapshot only.** If this conflicts with current Git, `CURRENT_STATE.md`, frozen protocol, code/tests, or newer evidence, the real repository wins.

## 1. Repository / mandatory first action

Repository:
`haozhouliuliuliu/kline-playbook-engine`

Before making any project-state, architecture, research, tooling, or next-step claim, fetch/read the real repository.

Read first:
1. `OWNER_COLLABORATION_CONTRACT.md`
2. `ARCHITECTURE_BASELINE.md`
3. `CURRENT_STATE.md`
4. `RESEARCH_DIRECTION.md`
5. `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
6. `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
7. `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`
8. `00_READ_FIRST.md`

Do not reconstruct project status from old chat or this handoff when repo facts are available.

## 2. Stable Owner collaboration facts

Owner is not a programmer. Default communication:
- Chinese;
- conclusion first;
- plain language;
- translate relevant English UI text immediately;
- do ordinary technical work without sending routine operations back to Owner;
- one complete copy-paste DS/Codex prompt per worker when an implementation agent is needed;
- after prompts, separately state exact recommended model, reasoning intensity, and continue/new conversation.

Owner-level gates are reserved for genuine product/direction changes, frozen research semantics, permanent risk rules, real-money/broker actions, paid commitments, irreversible external actions, and other authority-defined consequential actions.

Owner explicitly prefers:
- finish safe bounded work in one package instead of artificial small rounds;
- use safe parallelism when work is genuinely independent;
- isolated Git worktrees/branches for parallel workers;
- exactly one integration lane owns `main` and shared authority/state;
- parallel workers do not push `main` or independently edit shared authority unless assigned;
- normally 2–3 high-value lanes, not many conflict-heavy agents;
- if several independent lanes are ready, provide all runnable worker prompts in the same response instead of one prompt per Owner round-trip;
- if GPT can safely do repository-only docs/state/review integration through connected GitHub tools, GPT should do it directly instead of consuming a DS worker.

Authority: `OWNER_COLLABORATION_CONTRACT.md` + `AGENTS.md`.

## 3. Cost / local-agent workflow decision from this conversation

Current workflow decision:

```text
PAID_CHAT_RELAY_ORCHESTRATOR=NOT_ADOPTED_CURRENTLY
BRITTLE_VSCODE_UI_CHAT_AUTOMATION=NOT_ADOPTED_CURRENTLY
CURRENT_DS_RELAY_MODE=OWNER_MANUAL_RELAY_WHEN_LOCAL_AGENT_IS_NEEDED
```

Reason:
- Owner does not want to add a new paid OpenAI API merely to automate ChatGPT↔DeepSeek message relay when ChatGPT subscription + existing DeepSeek capacity are already available;
- UI/clipboard automation between chat windows was rejected as the default because it is brittle and had already caused wasted effort previously;
- future new paid API/service remains an Owner gate.

Current local capability snapshot reported by Owner:
- VS Code Chat can use `DeepSeek V4 Flash`;
- Owner reports ample DeepSeek API quota for bounded engineering/review work;
- this is a runtime/current-capability fact, not a project-adopted product dependency and may change later.

Do not resurrect a paid relay-agent project unless Owner explicitly revisits it or existing capability becomes inadequate.

## 4. Safe parallel-worktree operating rule

Parallel pattern has been proven usable:
- main integration lane: original `kline-playbook-engine` / `main`;
- engine/audit lane: `parallel/stat-engine-audit`;
- independent statistical review lane: `parallel/stat-profile-review`.

Both statistical branch outputs are now integrated to `main` as durable evidence.

Local worktrees may still exist on the Owner machine. A future agent must run/inspect `git worktree list`, branch state, and remote state before creating/reusing worktrees. Do not blindly recreate an existing branch/worktree or destructively delete retained worktrees just to make setup commands succeed.

## 5. Project isolation / governance

This is a clean-room independent project. Do not import strategy conclusions, experimental results, parameters, failure history, or route judgments from other projects.

Adopted cross-project constitution:
- `CROSS_PROJECT_OPERATING_CONTRACT.md`
- Version `3.1`
- SHA256 `3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e`

Tool taxonomy distinction is important:
- project-level capability lifecycle: `CANDIDATE / VERIFIED / ADOPTED`;
- cross-project `TOOL_REGISTRY.md` catalog taxonomy: `CANDIDATE / APPROVED / DEFERRED / REJECTED / RETIRED`;
- do not conflate these two vocabularies;
- project repo/runtime/CURRENT_STATE decide what this project actually uses.

Current project tool decision: `USE_EXISTING`.

## 6. Accepted architecture

`ARCHITECTURE_BASELINE.md`:
- Skeleton v1.0
- ACCEPTED

Top-level domains remain:
1. Data Substrate
2. Strategy Catalog
3. Backtest & Validation Engine
4. Research Loop
5. Trading Loop
6. Ledger
7. Observability & Control

AI remains primarily offline research support. Discretionary LLM decisions are not authorized in the live critical path. Do not reopen the full architecture without a concrete fatal flaw.

## 7. Binding research direction

`RESEARCH_DIRECTION.md`:

```text
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
STATUS=OWNER_APPROVED
```

Binding route:

```text
traceable human trading experience
-> AI-assisted extraction and structuring
-> versioned Playbook Contract
-> point-in-time market-scene representation / recognition
-> historical validation of applicability and failure conditions
-> strict validation / protected-holdout governance
-> accepted or rejected playbook
```

Human sources create hypotheses, not authority. Fame/performance claims do not validate a playbook.

Three layers must remain distinct:
1. SOURCE / RAW CLAIM
2. PROJECT / AI INTERPRETATION
3. MACHINE OPERATIONALIZATION

`原话 != AI理解 != 机器定义`.

Project-led source discovery is primary. Owner-supplied material is supplemental. Owner is not the manual data collector.

## 8. Research Protocol v1.0 — FROZEN / BINDING

Owner approval on 2026-08-19:
`按 v0.3 推荐冻结`

Authorities:
- `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

Frozen chronology:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

Important frozen semantics include:
- one source-justified PRIMARY branch before outcome testing;
- alternatives cannot rescue a failed PRIMARY as validation of the source claim;
- lineage/exposure survives renaming;
- immutable Research Wave denominator / whole-wave multiplicity;
- SOURCE_ONLY interpretation with technical denial of protected-period project market-outcome retrieval;
- historical holdout is project-governed historical evidence, not universal epistemic unseen proof;
- common statistical profile must lock before first candidate outcome-bearing backtest;
- `INSUFFICIENT_EVIDENCE` is legitimate;
- validation/final exposure is irreversible under protocol rules;
- future Shadow/Forward is the stronger genuinely prospective unseen path under later authority.

No candidate performance research has started.

## 9. Canonical historical data — ACCEPTED

Canonical BALANCED corpus:
- products: `cu, al, ni, au, ag, rb`
- coverage: `2024-01-01..2025-12-31`
- granularity: 1 minute
- concrete contracts: 212
- partitions: 32,980
- normalized rows: 15,280,452
- Parquet files: 32,980
- canonical corpus identity: `1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`
- cross-source identity: `cee702ea6cd79e62ec49bf7f1f632f70e5b0a7a577ba455e09597cce9d16d4ae`
- cross-source result: `32841_MATCH / 0_MISMATCH / 0_NOT_COMPARABLE / 139_NOT_AVAILABLE`

Project-local adopted data capabilities:
- TqSdk 3.10.1 — historical concrete-contract 1-minute research acquisition only
- PyArrow/Parquet 25.0.1 — normalized canonical storage
- SQLite — rebuildable catalog/index
- Raw JSON + SHA256 provenance — authoritative raw evidence mechanism

Corpus construction itself created no recorded strategy-family development/validation/final exposure.

## 10. Human Playbook source layer

First source-layer wave result: `GO` at source-only level.

Completed source dossiers include:
- Peter Brandt
- Al Brooks
- Linda Raschke
- Adam Grimes
- Brett Steenbarger
- Steidlmayer -> Dalton Market Profile lineage
- skeptical/counter-evidence methods: White, Sullivan/Timmermann/White, Bailey et al.

China-first:
- 青泽: identity/bibliography verified; no full dossier without authorized text/sample
- 期货日报实盘大赛: DISCOVERY_ONLY
- 付爱民 / 王少多 / 张亚楠: discovery leads only; provenance pinning incomplete

Source-acquisition tool pilot is closed/accepted as evidence; no new tool is needed for the current statistical-profile package. Do not promote a VERIFIED source tool to ADOPTED merely because it was tested.

## 11. Pre-outcome firewall — ACCEPTED

Final acceptance:
`docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md`

State:

```text
PREOUTCOME_FIREWALL_IMPLEMENTATION=COMPLETE_VERIFIED_ACCEPTED
IDENTITY_BINDING=VERIFIED
PRIMARY_SCOPE_SEARCH_CROSS_BINDING=VERIFIED
SOURCE_ONLY_POLICY=VERIFIED
SOURCE_ONLY_CLAIM_EXTRACTION_RUNNER=VERIFIED
REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED
RESEARCH_WAVE_IDENTITY_BINDING=VERIFIED
STATISTICAL_PROFILE_INTERFACE=VERIFIED
PRE_OUTCOME_GATE_STATUS=VERIFIED_FAIL_CLOSED
HISTORICAL_FINAL_HOLDOUT_LOCK=ENFORCED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

Key engineering facts:
- `src/research_firewall.py` is the single owner of new pre-outcome access rules;
- candidate access is identity-bound to the exact hypothesis/wave/profile/source session/PRIMARY/scope/search registration;
- callers cannot self-assert frozen lock booleans;
- one `WaveHypothesisBinding` per tested hypothesis pins PRIMARY/scope/parameter-search identity;
- terminal outcome records are non-overwritable;
- validation, historical final, Shadow/Forward remain denied.

SOURCE_ONLY is an application-level control, not a cryptographic sandbox. Model latent memory is a disclosed residual risk.

## 12. Common Statistical Profile v1 — CURRENT BOTTLENECK

First candidate:
- `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
- commit `6ef668fd7214fcef2f12b71cb3e9ea2a36bfcaf7`
- status: `CANDIDATE_REVISION_REQUIRED_NOT_LOCKED`
- no candidate outcome data used

Statistical-engine capability audit:
- original branch commit `c34cebde4307eb2d532886ed8da94e2985323ede`
- main cherry-pick `4946b0db2692a06ff6965efedb242156ab52e886`
- `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`

Engine compatibility crosswalk:
- original branch `parallel/stat-engine-audit`
- original commit `05ad7f9a94c1a6b885402a4417a0d095dbfa7c56`
- integrated to main by `4b2c882331f855c730d125517e6b7fd563025055`
- `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK.md`

Independent adversarial statistical review:
- original branch `parallel/stat-profile-review`
- original commit `5e78605d312ee2e6c22e82dc4d91d651eacac4b2`
- integrated to main by `4650e5fe24e4ac50377a2e7440b81921c57c0a87`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md`
- verdict `GO_WITH_REQUIRED_CHANGES`
- 3 CRITICAL / 6 HIGH

Project-brain adjudication:
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`
- status `ADJUDICATION_COMPLETE / PROFILE_NOT_LOCKABLE_YET`

Accepted revision requirements:
1. Separate economic materiality from statistical detectability/power interpretation. Do not imply insufficient power means no edge.
2. Remove `ESS=N/max(1,2H-1)` as a deterministic hard sufficiency gate.
3. Pin one engine `position_id` = one completed round-trip observation; aggregate opening legs/adds/partial-close legs; forced liquidation is terminal; concrete-contract roll creates separate round trips.
4. Explicitly define holding-horizon and multi-week dependence/block attribution before lock.
5. Current fixed sufficiency thresholds remain candidate heuristics and must be justified/simplified before lock.
6. Distinguish fee stress from slippage/friction stress.
7. Add a simple predeclared robustness guard against one event/narrow time window carrying the apparent edge.
8. Add explicit `DATA_BLOCKED` (or equivalent) distinct from FAIL and INSUFFICIENT_EVIDENCE.
9. Make multiplicity counting machine-consistent with frozen Research Wave/search identities. Holm remains a leading simple candidate, not locked.
10. Correct Romano-Wolf description; correction does not require adopting it.

### Critical non-adoption warning

The independent reviewer also proposed a `RECOMMENDED_SIMPLIFIED_V1` and used illustrative arithmetic/power examples. **Those reviewer suggestions are advisory evidence, not accepted project semantics.** In particular, do NOT infer that the project has accepted or frozen:
- `N>=60`, specific day/week minima, or any other reviewer threshold;
- a specific `2x` cost gate;
- Holm as the final multiplicity method;
- the review's block-length formula;
- the review's illustrative volatility/sigma values or power examples as project facts;
- any exact replacement for the removed ESS gate.

The adjudication accepted the defects/revision requirements, not the reviewer's proposed numeric replacement. Exact methods/numbers remain a pre-outcome design task.

Current candidate is **not lockable**. No outcome-bearing backtest is authorized.

## 13. Statistical-engine facts relevant to revision

Safe/available primitives include:
- realized PnL
- cash balance
- execution/transaction costs
- instrument and concrete-contract identity
- timestamps / authoritative trading-day identity
- per-order realized PnL contribution
- deterministic `position_id` lifecycle

Missing/small deltas:
- round-trip ledger materialization
- holding duration
- day/week aggregation
- active/no-trade day counts
- per-hypothesis/per-wave execution join

Medium delta:
- multi-day portfolio/equity series

Known technical debt impact:
- TD-001: duplicate calendar responsibility; future trusted day/week statistics must use `SessionMetadata`
- TD-002: partial-close snapshot zeroes unrealized PnL; corrupts intermediate equity/drawdown path, not final realized round-trip total
- LIMIT-001: governed historical price-limit facts incomplete; affected confirmatory PnL generation fails closed until bound

## 14. Current authorization boundaries

AUTHORIZED NOW:
- source discovery/provenance
- controlled real claim extraction inside verified SOURCE_ONLY environment under Claim Schema v1.0
- deterministic non-outcome operationalization/tests
- Common Statistical Profile revision/review/implementation without candidate outcomes
- synthetic/non-candidate engine tests
- safe isolated parallel engineering/review work

NOT AUTHORIZED:
- candidate performance inspection (PnL/equity/expectancy/Sharpe/win-loss or equivalent) before revised profile lock + real wave + firewall pass
- validation access
- historical final-holdout unlock
- changing frozen 12/6/6 without new protocol/Owner gate
- changing frozen research semantics without new protocol/Owner gate
- unconstrained strategy/indicator/rule/parameter mining
- Shadow automated trading
- real-money/broker orders
- discretionary live LLM critical path
- new paid commitments
- permanent RiskGate semantics without Owner approval
- large multi-agent orchestration / knowledge graph / microservices expansion
- cross-project strategy-result import
- paywall/DRM/platform bypass
- authenticated browser-cookie acquisition without separate review
- redistribution of copyrighted raw source material

## 15. Tests / current verification

Last reported canonical verification on all statistical lanes:

```text
python -m unittest discover -s tests -v
235 tests OK
3 skipped
exit 0
```

All main changes after that code-bearing verification, including adjudication, handoff/state sync, collaboration-rule changes, and integration of the two review evidence documents, are documentation/state/authority-only; no production/test code changed.

## 16. Current next safe action

From `CURRENT_STATE.md`:

```text
CURRENT_NEXT_ACTION=REVISE_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE_FROM_ADJUDICATED_REVIEW
PROFILE_STATUS=CANDIDATE_REVISION_REQUIRED_NOT_LOCKED
TOOL_DECISION=USE_EXISTING
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED
OWNER_ACTION=NONE
```

The next package should revise the profile candidate + design evidence in one coherent pass, without candidate outcomes. Then run a **targeted delta independent review** over only materially changed statistical definitions. Do not repeat the whole project review.

Do not implement the full statistical evaluator before the revised statistical design survives targeted review, except for purely non-semantic helpers that cannot bias the profile choice.

## 17. Progress estimates

Engineering estimates only:
- Architecture / Bootstrap: 100%
- Data Substrate: ~90%
- Strategy Catalog: ~58%
- Backtest & Validation: ~64%
- Human Playbook Research Loop: ~43%
- Trading Loop: ~15%
- Ledger / Observability: ~25%
- Overall project: ~45%

Do not inflate progress from test counts or tooling scaffolding.

## 18. Owner gates still reserved

Owner approval remains required for:
- changes to frozen research semantics or chronology
- historical final-holdout unlock
- new paid commitments
- irreversible external actions
- authenticated acquisition with material new data-flow risk
- permanent risk rules
- real-money/broker actions
- live critical-path changes

Current Owner action: `NONE`.
