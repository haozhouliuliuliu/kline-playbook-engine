# 00_READ_FIRST

Canonical repository:

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

This file owns the **active read order**. Do not reconstruct current project state from chat memory, uploaded snapshots, old handoffs, old branches, or historical review files.

## Fresh-conversation takeover

A fresh project-brain conversation starts with **read-only takeover verification**.

Read only this active core first, in order:

1. `OWNER_COLLABORATION_CONTRACT.md` — stable Owner collaboration rules.
2. `PROJECT_BRAIN_RUNTIME_BRIEF.md` — compact live pointer.
3. `CURRENT_STATE.md` — mutable current project authority.
4. `ARCHITECTURE_BASELINE.md` — consolidated current architecture.
5. `RESEARCH_DIRECTION.md` — current Jianghe / Human Playbook First direction.
6. `docs/research/JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md` — AI Trader identity / replay / PRIMARY-compatibility / fidelity governance.
7. `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md` — current Jianghe source authority; follow its internal read order only as deeply as needed.
8. `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` — current unresolved limits only.
9. `docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md` — current frozen pre-spend blocker/evidence/acceptance authority while `LIMIT-015` is active.
10. `PROJECT_HANDOFF_CURRENT.md` — derived continuity handoff; read last and use only as a cross-check, never as authority over current `main`.

During the takeover turn:
- fetch current `main` and the active core above;
- reconstruct current phase, architecture, locks, Jianghe status, active limitations, frozen pre-spend findings and next normal phase;
- report contradictions/missing authority if any;
- distinguish repository facts from the derived handoff;
- then stop for Owner acceptance.

Do **not** modify the repository, start a work package, generate worker prompts, adopt tools, inspect candidate outcomes, make provider calls, or change research/product direction during that first takeover turn.

## Conditional authority — read when the task needs it

Do not preload these on every fresh conversation merely because they exist:

- `docs/architecture/ADR_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1.md` — read for architecture-boundary detail.
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` — read before PRIMARY branch design, exposure/multiplicity decisions, or any outcome-bearing research design.
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` — read before outcome chronology/access work.
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md` — read when protected outcome access or firewall behavior is in scope.
- `CROSS_PROJECT_OPERATING_CONTRACT.md` — read for cross-project governance questions.
- `TOOL_REGISTRY.md` — read only when a tool/plugin/framework admission decision is actually needed.
- `docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_PLAN_V0_1.md` — historical plan/method for the current consolidated findings; its original `PENDING` footer is not current mutable status.
- `docs/reviews/JIANGHE_LIVE_PROBE_OWNER_SCOPE_REVISION_V0_2.md` — read for binding Owner provider exclusions/budget scope before provider recommendation/implementation.
- Historical reviews/evidence — read only when current authority points to them or a dispute/audit requires them.

Important compatibility rule: the frozen Human Playbook protocol predates the Jianghe AI decision-layer migration. For Jianghe AI Trader, its `deterministic operationalization identity/hash` language is specialized by `JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md`: deterministic **identity binding** is required; deterministic fixed-rule market decisions are not.

## After takeover: mandatory refresh rule

Before every **substantive project reply**:

1. fetch current `main` HEAD;
2. fetch `PROJECT_BRAIN_RUNTIME_BRIEF.md` from current `main`;
3. if `main` contains material state newer than the brief marker, or the answer concerns current state / architecture / locks / next work / worker prompts / tool or model adoption, refresh `CURRENT_STATE.md` and the specific authority it points to;
4. do not rely on local conversation memory for mutable project facts.

Narrow conceptual explanations may use already-fetched stable authority when no mutable project fact is involved.

## Current research / product anti-regression rule

The active route is:

```text
traceable Jianghe human trading experience
-> source-faithful V1.1 knowledge pack
-> versioned Jianghe AI Trader identity
-> causal multi-timeframe observation + working memory
-> non-outcome semantic + visual + structured fidelity evaluation
-> source-justified PRIMARY preparation
-> governed historical outcome research only after explicit gates
-> genuinely unseen Shadow/Forward evidence when later authorized
```

The AI is the market-reading decision brain. Deterministic infrastructure owns hard risk, orders, execution truth, reconciliation and Safety.

The project is **not** currently authorized to:

```text
mine indicators / chart patterns / parameter grids by historical PnL
-> select winners
-> retrofit a human explanation
```

Jianghe is the sole current trading knowledge source for V1. Strategy-source expansion is paused. UNKNOWN, contradiction, unfamiliar market state, or unsupported interpretation must allow `WAIT` / `NO_TRADE` rather than invention.

## Mutable-state location

Do not duplicate mutable project status in this file. Current values live in:

- `PROJECT_BRAIN_RUNTIME_BRIEF.md` — compact refresh surface;
- `CURRENT_STATE.md` — detailed current authority;
- currently active formal review/evidence named by `CURRENT_STATE.md` — for detailed blocker/evidence/acceptance semantics.

`PROJECT_HANDOFF_CURRENT.md` is a derived continuity aid only. It may summarize the active problem set for conversation rollover, but it never overrides current formal authority.

Historical repair programs, rejected/deferred playbooks, superseded progress estimates and old integration logs are intentionally excluded from the active takeover path. They remain preserved in Git history and durable evidence/review artifacts.

## Verification path

Canonical full-suite command:

```text
python -m unittest discover -s tests -v
```

A historical test count is not current project authority.
