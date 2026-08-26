# kline-playbook-engine

A single-purpose China-futures AI-trader project.

## Start here

For current project facts, do **not** infer status from this README.

Read:

1. `00_READ_FIRST.md`
2. follow its canonical takeover order

The current work package, phase, locks and next task live only in:

`CURRENT_STATE.md`

## Project shape

The project builds a persistent, auditable DeepSeek-based futures trader grounded initially in Jianghe's documented trading knowledge.

Core principles include:

- chronological/causal market observation;
- project-owned persistent memory and audit;
- source truth separated from model hypotheses and validated policy;
- deterministic risk/OMS/reconciliation/safety outside model discretion;
- governed evidence before promotion;
- exact Owner authority for paid or consequential external actions.

## Canonical owners

- governance: `PROJECT_GOVERNANCE.md`
- worker/repository procedure: `AGENTS.md`
- architecture: `ARCHITECTURE_BASELINE.md`
- tools/providers/pins/credential seams: `TOOL_REGISTRY.md`
- product/research direction: `PROJECT_DIRECTION.md`
- current dynamic state: `CURRENT_STATE.md`
- known limitations/tech debt: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`

## Historical data authority

`docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`

## Verification

Typical broad regression command:

`python -m unittest discover -s tests`

See `AGENTS.md` and repository workflows for current verification procedure.
