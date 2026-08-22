# 00_READ_FIRST

Canonical repository:

```text
REPOSITORY_FULL_NAME=haozhouliuliuliu/kline-playbook-engine
```

This file owns the **active read order**. Do not reconstruct current project state from chat memory, old handoffs, old branches, or historical review files.

## Fresh-conversation takeover

A fresh project-brain conversation starts with **read-only takeover verification**.

Read in this order:

1. `OWNER_COLLABORATION_CONTRACT.md` — stable Owner collaboration rules.
2. `PROJECT_BRAIN_RUNTIME_BRIEF.md` — compact live pointer.
3. `CURRENT_STATE.md` — mutable current project authority.
4. `ARCHITECTURE_BASELINE.md` — consolidated current architecture.
5. `docs/architecture/ADR_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1.md` — binding AI decision-layer details.
6. `RESEARCH_DIRECTION.md` — current Human Playbook First direction.
7. `docs/research/JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md` — Jianghe AI identity / replay / fidelity governance.
8. `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` and `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` — frozen source/outcome governance.
9. `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` — current unresolved limits only.
10. `CROSS_PROJECT_OPERATING_CONTRACT.md` and `TOOL_REGISTRY.md` — governance/tool catalog.
11. `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md` — current Jianghe source authority; follow its internal read order only as deeply as the task requires.
12. `PROJECT_HANDOFF_CURRENT.md` — pointer-only derived handoff; read last.

During the takeover turn:
- fetch current `main` and the files above;
- reconstruct current phase, architecture, locks, Jianghe status, active limitations and next normal phase;
- report contradictions/missing authority if any;
- distinguish repository facts from the derived handoff;
- then stop for Owner acceptance.

Do **not** modify the repository, start a work package, generate worker prompts, adopt tools, inspect candidate outcomes, or change research/product direction during that first takeover turn.

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
-> non-outcome fidelity evaluation
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
- `CURRENT_STATE.md` — detailed current authority.

Historical repair programs, rejected/deferred playbooks, superseded progress estimates and old integration logs are intentionally excluded from the active takeover path. They remain preserved in Git history and their durable evidence/review artifacts.

## Verification path

Canonical full-suite command:

```text
python -m unittest discover -s tests -v
```

A historical test count is not current project authority.
