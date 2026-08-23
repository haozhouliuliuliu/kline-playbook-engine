# 江河 PRIMARY curated-quality 固定验收标准 V0.1

> Status: `LOCKED_FOR_CURRENT_PRE_FREEZE_REPAIR_GATE`  
> Scope: current Jianghe PRIMARY curated-quality repair and its independent re-audit.  
> This document fixes the acceptance criteria for the current gate so that implementation and independent review use the same standard. It does not freeze PRIMARY semantics, authorize a live model probe, access outcomes, or change source authority.

## 1. Why this rubric exists

The prior V0.3/V0.4 repair cycle exposed a process problem: prose-template diagnostics were allowed to drift into de facto semantic acceptance criteria. That can create a moving goalpost where one worker removes one textual pattern and another worker rejects the replacement for a different stylistic pattern.

For this gate, acceptance is therefore based on **source correctness, traceability, disposition integrity, preserved uncertainty, operational boundaries, deterministic identity, and firewall/test evidence** — not on literary uniqueness.

The governing PRIMARY preparation contract remains:

- `docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1.md`
- `docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_SCHEMA_V0_1.json`

This rubric narrows how curated-quality repair is judged; it does not replace source authority or the preparation contract.

## 2. The eight hard acceptance criteria

A repaired PRIMARY curated artifact passes this gate only if all eight criteria pass.

### R1 — Complete claim coverage and real evidence traceability

Required:

```text
TOTAL_CLAIMS=352
UNMAPPED=0
DUPLICATES=0
```

Every repository path or formal authority reference used to justify a curated adjudication must resolve to a real repository artifact / authority. A phantom path or invented review authority is a blocking defect.

Source-bound fields must remain traceable to the active claim/source authority and current knowledge-pack / claim-manifest identities.

### R2 — READY / STOP disposition integrity

`READY_FOR_PRIMARY_FREEZE` is allowed only when the **minimal proposition selected for that claim** is source-justified and has no unresolved blocker that is required to decide that proposition.

A READY claim may not retain an unresolved:

- required source review that is necessary to establish the selected proposition;
- source conflict that affects the selected proposition;
- source ambiguity that prevents a unique selected proposition;
- governed-observation gap required to apply the selected proposition.

A later formal review resolution may clear an older source-review flag only when the resolution authority actually exists and substantively resolves the relevant issue. A downstream curated artifact may not clear a blocker merely by writing `COMPLETE`.

STOP is a valid first-class result and must not be removed to improve readiness counts.

### R3 — UNKNOWN and contradiction preservation

Required:

```text
GUESSED_UNKNOWN=0
SILENT_CONFLICT_RESOLUTION=0
```

Relevant UNKNOWN / contradiction authority must be linked or explicitly adjudicated as not applicable to the particular claim. Reverse-coverage checks are used to detect plausible omissions, but sharing a source ordinal alone does **not** force every claim from that source to link every UNKNOWN or contradiction.

No project-authored numeric proxy, tie-break, classifier, or convenience rule may fill source uncertainty.

### R4 — Authentic alternative review

Only a **source-plausible competing interpretation** counts as a material alternative.

Forbidden:

- manufacturing an alternative solely by saying “ignore the ambiguity and invent a fixed project rule”;
- creating strawman alternatives only to make the review field look populated;
- using a blanket alternative solely because the schema has a field for alternatives.

If no material source-plausible alternative exists, `NO_MATERIAL_SOURCE_ALTERNATIVE` is acceptable with a claim-relevant reason.

### R5 — Source fidelity and no semantic overreach

The curated artifact must not:

- rewrite source truth;
- generalize a source/case-local number into a universal threshold;
- convert vague source language into invented precision;
- convert correlation into causation;
- convert optional/contextual behavior into a universal mandatory rule;
- convert source UNKNOWN into a project answer;
- use candidate outcomes, later market movement, P&L, win rate, Sharpe, expectancy, Validation, Final, Shadow, or future data to select a branch.

A `semantic_interpretation` may be identical or nearly identical to `source_meaning` when the source wording itself is already the correct minimal proposition. **Source echo is not a defect by itself.**

### R6 — Operational boundary correctness

The artifact must preserve the boundary between:

```text
SOURCE SEMANTIC
AI DISCRETION
DETERMINISTIC MACHINE OPERATIONALIZATION
```

`HUMAN_DISCRETION_REQUIRED` / discretionary concepts may not be silently converted to hard thresholds or deterministic classifiers.

`NOT_YET_UNDERSTOOD` may be READY only when a narrower known proposition is source-justified, the unknown portion is explicitly excluded, and the unknown portion does not block that narrower proposition.

Observability claims must match the governed causal observation surface.

### R7 — Mechanical builder, deterministic identities, no hidden semantic generator

The builder / validator may:

- load curated data;
- validate schema and real evidence paths;
- verify source equality / bindings;
- validate cross-references;
- serialize deterministically;
- count records;
- compute deterministic identities.

It may not choose or generate claim semantics, alternatives, UNKNOWN resolution, contradiction resolution, semantic mode, operationalization meaning, or disposition from keywords, categories, machineability, source ordinal, family ID, or other heuristics.

Required:

```text
BRANCH_IDENTITIES_DETERMINISTIC=YES
PRIMARY_FREEZE=NO
PRIMARY_ELIGIBLE=NO
```

### R8 — Reproducible validation, firewall, and full test health

The repaired artifact must pass its focused validators/tests and the canonical full suite in a valid project test environment with:

```text
FAILURES=0
ERRORS=0
OUTCOME_ACCESS=NO
LIVE_MODEL_CALLS=0
PAID_SPEND=0
```

An environment failure such as missing local timezone data is not automatically attributed to the repair, but it also cannot be counted as a formal full-suite PASS. Integration must obtain a clean full-suite run in a valid environment before this gate closes.

## 3. What is explicitly NOT a blocking criterion

The following may be useful diagnostics, but **cannot independently fail the gate**:

- prose uniqueness;
- high or low `difflib` similarity;
- repeated sentence frames;
- repeated standard operational wording;
- `semantic_interpretation == source_meaning`;
- many claims legitimately using the same semantic or operationalization mode;
- claim IDs making strings unique or non-unique;
- a diagnostic reporting a template cluster without demonstrating a violation of R1–R8;
- stylistic awkwardness that does not change semantic or audit meaning;
- ordinary maintainability issues that do not affect R1–R8.

A reviewer may record these as NOTE / technical debt, but may not reopen the gate solely for them.

## 4. Rule for any newly discovered finding

After this rubric is locked, a new finding may block the current gate only when the reviewer provides:

```text
FINDING_ID
AFFECTED_CLAIM_IDS_OR_ARTIFACT
HARD_CRITERION=R1|R2|R3|R4|R5|R6|R7|R8
CONCRETE_REPOSITORY_EVIDENCE
WHY_THE_CRITERION_IS_VIOLATED
MINIMUM_REQUIRED_FIX
```

If a finding cannot be mapped to R1–R8 with concrete evidence, it is non-blocking for the current gate and must be recorded separately as NOTE / technical debt.

This rule exists specifically to prevent moving-goalpost review.

## 5. Fixed independent re-audit method

The next independent re-audit uses the following fixed method.

### 5.1 Machine checks — 352/352

Run across all 352 claims:

- coverage / uniqueness;
- current knowledge-pack and claim-manifest identity binding;
- evidence-path existence;
- branch identity recomputation;
- READY + unresolved-review/conflict/ambiguity/observability contradictions;
- UNKNOWN / contradiction forward and reverse coverage diagnostics;
- source-bound field equality;
- deterministic rebuild;
- firewall / outcome denial.

### 5.2 Semantic review — 100% of exception population

Review every claim in any of these sets:

- all STOP claims;
- all UNKNOWN-linked claims;
- all contradiction-linked claims;
- all claims with original or later source-review resolution requirements;
- all claims carrying material ambiguity relevant to disposition;
- all source-scoped numeric rules / thresholds / ratios;
- all observability-boundary claims;
- every claim whose semantic/disposition/alternative/evidence adjudication is materially changed by the repair;
- every claim identified by the prior independent V0.4 re-audit findings.

### 5.3 Straight-through claims — stratified audit sample

Claims outside the exception population do **not** require another free-form 352/352 prose rewrite or reviewer essay.

The independent reviewer will inspect a fixed minimum sample of **60 straight-through claims**, spread across source ordinals, A/B/C/D/NONE scope, semantic modes, operationalization modes, and machineability classes.

A sampled straight-through claim passes when R1–R8 hold. Textual originality is irrelevant.

If the sample uncovers a genuine R1–R8 systemic defect, the reviewer may expand the affected class as needed. Expansion must be tied to that specific hard criterion, not to a new style standard.

## 6. Disposition counts are not a target

No acceptance decision may optimize for retaining `340 READY / 12 STOP`.

Counts may remain the same or change. The only question is whether each resulting disposition satisfies R1–R8.

## 7. Current V0.4 re-audit findings under this rubric

The independent V0.4 re-audit is reclassified as follows for the next repair:

```text
F-01 prose/template similarity alone = NON_BLOCKING
      (only underlying R1-R8 defects, if any, remain relevant)

F-02 phantom evidence paths = BLOCKING / R1

F-03 fabricated strawman alternatives = BLOCKING where present / R4

F-04 stale Q01 wording = repair if it creates current adjudication contradiction;
      otherwise non-blocking wording cleanup

F-05 JH-CLM-021-002 unresolved visual-reference review = BLOCKING / R2 unless real authority resolves it

F-06 UNKNOWN reverse-coverage candidates = targeted R3 adjudication;
      source co-location alone does not require a link

F-07 awkward NO_TRADE wording = NON_BLOCKING unless it changes R5/R6 meaning

F-08 stale historical ambiguity wording = NON_BLOCKING unless it changes current R2/R5 truth

F-09 schema layering note = NON_BLOCKING for this gate when a real formal resolution authority exists;
      downstream self-declaration alone remains forbidden by R2

F-10 local tzdata error = environment issue under R8; clean full-suite run still required before integration
```

## 8. Gate outcome vocabulary

The independent reviewer must end with exactly one of:

```text
PRIMARY_CURATED_QUALITY_REAUDIT=PASS
```

or

```text
PRIMARY_CURATED_QUALITY_REAUDIT=FAIL
```

A FAIL must list at least one unresolved R1–R8 violation with concrete evidence.

A PASS means only that the current pre-freeze curated-quality gate is satisfied. It does **not** mean:

- PRIMARY semantics are frozen;
- PRIMARY is eligible for candidate outcomes;
- a model/provider is VERIFIED or ADOPTED;
- a live-model probe is authorized;
- paid spend is authorized;
- Broker or real-money activity is authorized.

Those remain separate gates under existing project authority.
