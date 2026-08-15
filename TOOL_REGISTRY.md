# TOOL_REGISTRY.md

> **Date:** 2026-08-14  
> **Contract compatibility:** `CROSS_PROJECT_OPERATING_CONTRACT.md` Version 3.1  
> **Role:** Cross-project capability catalog and decision log.  
> **Authority boundary:** This registry does **not** define what any project actually runs. Project config/lockfiles/runtime are the authority for actual enabled versions.

---

# 0. Registry policy

Statuses:

```text
CANDIDATE
APPROVED
DEFERRED
REJECTED
RETIRED
```

Interpretation:

- **CANDIDATE:** plausible capability; not globally assumed safe/useful.
- **APPROVED:** admitted for its stated role/activation condition after sufficient evidence.
- **DEFERRED:** potentially useful, but no current need or unresolved prerequisite.
- **REJECTED:** should not be adopted for the stated foundation role.
- **RETIRED:** previously admitted, now replaced/unsafe/obsolete.

For each material tool, record only what matters:

- role;
- status;
- source/pin policy;
- activation condition;
- material risk;
- overlap;
- evidence/decision;
- revalidation trigger;
- removal notes.

No tool is constitutionally mandatory merely because it appears here.

---

# 1. Foundation / environment

## mise

**Role:** Runtime/tool version management, environment setup, and reusable project tasks.  
**Status:** `CANDIDATE`  
**Source/pin:** Official project; pin reviewed stable version before machine-level adoption.  
**Activate when:** Multiple projects benefit from reproducible tool/runtime versions or shared bootstrap/verify/run tasks.  
**Material risk:** Config/tasks/hooks can execute local commands; trust/review project config before execution.  
**Overlap:** `just` + separate runtime manager; language-native runtime managers.  
**Decision:** Preferred current environment candidate because one capability can cover runtime/tool versions plus tasks; do not force it where language-native tooling is simpler.  
**Revalidate when:** Windows behavior materially changes; trust model changes; maintenance declines; simpler native alternative becomes sufficient.  
**Remove:** Remove machine install and project config only after replacing required runtime/task entrypoints.

## just

**Role:** Project command runner.  
**Status:** `DEFERRED`  
**Source/pin:** Official project; pin stable release if adopted.  
**Activate when:** A project needs a small task interface but does not need mise-style runtime/environment management.  
**Material risk:** Executes project commands.  
**Overlap:** mise tasks.  
**Decision:** Good tool, but currently displaced as the default cross-project task-runner candidate by mise.  
**Revalidate when:** mise proves too complex/unreliable for the user’s Windows workflow.  
**Remove:** Delete task configuration after equivalent commands exist elsewhere.

---

# 2. Security / dependency integrity

## Trivy

**Role:** Local dependency vulnerability and secret scanning; optional broader repository security checks.  
**Status:** `CANDIDATE`  
**Source/pin:** Official project; pin reviewed stable release.  
**Activate when:** A project has third-party dependencies/secrets/external integrations and a deterministic scanner materially reduces risk.  
**Material risk:** Local scanning; may download/update vulnerability databases; can produce false positives/negatives.  
**Overlap:** Gitleaks + language-native dependency audits.  
**Decision:** Current first candidate for a lean combined security check. Default use should stay proportional; do not enable unrelated enterprise scanners merely because available.  
**Revalidate when:** Detection quality/maintenance changes; local fixture comparison shows material gaps.  
**Remove:** Remove scanner/config without changing project runtime behavior.

## Gitleaks

**Role:** Specialized secret scanning.  
**Status:** `DEFERRED`  
**Source/pin:** Official project; pin stable release if adopted.  
**Activate when:** Secret-scanning quality is insufficient in the chosen combined scanner or a project needs a dedicated secret detector.  
**Material risk:** False positives/negatives; repository-history scanning cost.  
**Overlap:** Trivy secret scanner.  
**Decision:** Keep as fallback specialist, not default foundation scanner.  
**Revalidate when:** Primary scanner misses relevant secret patterns or Gitleaks maintenance direction changes materially.  
**Remove:** Remove scanner/config only.

---

# 3. Tool / Skill admission

## OpenAI plugin-eval

**Role:** Static/local evaluation of Codex Skills/Plugins and optional live benchmark support.  
**Status:** `CANDIDATE`  
**Source/pin:** Official OpenAI plugins repository; use a reviewed pinned commit rather than tracking `main`.  
**Activate when:** Evaluating a non-trivial Skill/Plugin for admission or context/token cost.  
**Material risk:** Static modes are local; live benchmark mode consumes Codex usage and executes isolated Codex sessions. Fast-moving project/documentation may lag implementation.  
**Overlap:** Manual source review; custom evaluation harnesses.  
**Decision:** Prefer on-demand local CLI usage rather than installing it as an always-on Plugin. Static analysis should precede any live benchmark.  
**Revalidate when:** CLI/result schema or benchmark semantics change; official support status changes.  
**Remove:** Delete pinned checkout/local link and generated `.plugin-eval` artifacts when no longer needed.

---

# 4. Specialist engineering Skills

## mattpocock/skills — diagnosing-bugs

**Role:** Disciplined diagnosis loop for difficult bugs/performance regressions.  
**Status:** `CANDIDATE`  
**Source/pin:** Pin reviewed skill source/commit before use.  
**Activate when:** Cause is unclear, repeated fixes fail, or performance/debugging needs explicit hypothesis/instrumentation discipline.  
**Material risk:** Additional method/context; may over-process trivial bugs if activated too broadly.  
**Overlap:** Normal Codex debugging plus project autonomous-fix rules.  
**Decision:** Keep as on-demand specialist, not global/always-on.  
**Revalidate when:** Skill grows into broader workflow ownership or duplicates native Codex debugging sufficiently.  
**Remove:** Remove skill file/reference.

## mattpocock/skills — domain-modeling

**Role:** Clarify vocabulary/domain boundaries in complex professional domains.  
**Status:** `CANDIDATE`  
**Source/pin:** Pin reviewed skill source/commit.  
**Activate when:** `DOMAIN_COMPLEXITY` is material and terminology/state concepts are causing ambiguity.  
**Material risk:** Can create documentation overhead in simple projects.  
**Overlap:** `CONTEXT.md`, ADRs, normal architecture analysis.  
**Decision:** On-demand only.  
**Revalidate when:** Project already has a stable domain model or the skill becomes process-heavy.  
**Remove:** Remove skill while preserving any accepted domain facts in project authority.

## mattpocock/skills — codebase-design

**Role:** Module/interface design discipline for complex refactors/new boundaries.  
**Status:** `CANDIDATE`  
**Source/pin:** Pin reviewed skill source/commit.  
**Activate when:** Architectural seams/module depth are the actual problem.  
**Material risk:** Over-design on small changes.  
**Overlap:** Normal architecture review / ADR process.  
**Decision:** On-demand specialist only.  
**Revalidate when:** Native/project design rules cover the same behavior.  
**Remove:** Remove skill; accepted ADRs remain project authority.

---

# 5. Workflow frameworks / absorbed methods

## Ponytail

**Role:** Reduce over-engineering through reuse/native/minimum-solution ladder.  
**Status:** `CANDIDATE`  
**Source/pin:** Pin exact reviewed commit if tested/used.  
**Activate when:** Only after a minimal behavioral comparison shows the full Plugin provides material value beyond a short project/global rule.  
**Material risk:** Always-on behavior and lifecycle Hooks can affect every coding turn; model-dependent performance/cost effects.  
**Overlap:** Lean/YAGNI/reuse principles already absorbed by the contract; short `AGENTS.md` rules.  
**Decision:** Its core principles are absorbed. Whether the full Plugin deserves installation remains the main unresolved behavioral candidate. Do not globally install by default.  
**Revalidate when:** Codex/model behavior changes materially or Plugin Hooks change.  
**Remove:** Disable/remove Plugin, remove/revoke Hooks/trust/config, verify no residual connector/process remains.

## source-driven-development (Addy Osmani)

**Role:** Force framework/library decisions to be grounded in primary/official sources.  
**Status:** `REJECTED` **as a separate foundation Skill**  
**Source/pin:** N/A for foundation.  
**Activate when:** N/A by default; individual projects may still evaluate it independently.  
**Material risk:** Duplicate instruction/context.  
**Overlap:** Contract evidence/source rules and normal web/official documentation workflow.  
**Decision:** Principle absorbed; separate global Skill adds too much overlap.  
**Revalidate when:** A real project demonstrates repeated source-grounding failures that the existing rules do not solve.  
**Remove:** Remove installed copies if no project-specific reason remains.

## context-engineering (Addy Osmani)

**Role:** Manage agent context/rules/MCP inputs.  
**Status:** `REJECTED` **as a separate foundation Skill**  
**Material risk:** Duplicate meta-governance and context overhead.  
**Overlap:** Contract instruction architecture, bounded context, current state, handoff, conditional tools.  
**Decision:** Core principle absorbed.  
**Revalidate when:** Native/project context quality fails in a way the existing architecture cannot address.

## Addy Osmani full lifecycle pack

**Role:** End-to-end software-development workflow.  
**Status:** `REJECTED` as a foundation process owner.  
**Decision:** Too much overlap with the project’s single governance/process owner. Individual skills may be evaluated separately if they fill a demonstrated gap.

## Matt Pocock full skill pack

**Role:** Broad engineering/productivity Skill collection.  
**Status:** `REJECTED` as a whole-bundle default.  
**Decision:** Use curated specialists only.

## Superpowers full methodology

**Role:** Complete agent software-development methodology.  
**Status:** `REJECTED` as a foundation process owner.  
**Decision:** Conflicts with the “one process owner” architecture; individual techniques may be separately evaluated if needed.

## gstack full stack

**Role:** Multi-role virtual software company / full product workflow.  
**Status:** `REJECTED` as a foundation process owner.  
**Decision:** Too much workflow ownership, release/public-production emphasis, and overlap for default local single-user projects.

## Karpathy-style coding guideline packs

**Role:** Minimal/simple coding principles.  
**Status:** `REJECTED` as separate foundation tooling.  
**Decision:** Useful principles are already absorbed; no separate pack needed.

---

# 6. Large-repo / documentation / web acquisition

## CodeGraph

**Role:** Local code-relationship/graph retrieval for large or unfamiliar repositories.  
**Status:** `DEFERRED`  
**Source/pin:** Pin reviewed release/commit when a real trial is justified.  
**Activate when:** `LARGE_OR_UNFAMILIAR_REPO` and native grep/read/navigation produces material friction.  
**Material risk:** Context/tool-schema cost; large retrieval outputs can pollute main context; MCP/tool permissions as applicable.  
**Overlap:** Native search/read, subagent exploration.  
**Decision:** Do not benchmark speculatively. Trial on the first real large-repo problem; prefer explorer-subagent isolation if it reduces main-thread contamination.  
**Revalidate when:** Native Codex code intelligence materially improves or CodeGraph behavior/cost changes.  
**Remove:** Remove server/tool config and indexes.

## Context7

**Role:** On-demand library/API documentation acceleration.  
**Status:** `DEFERRED`  
**Source/pin:** Use reviewed official integration/client; external service remains non-authoritative.  
**Activate when:** Fast-changing library docs repeatedly cause version/API errors and official-source web lookup is materially inefficient.  
**Material risk:** External service/API key, data egress, community-contributed content may be inaccurate/incomplete.  
**Overlap:** Official documentation + native web search.  
**Decision:** Prefer official sources as truth. If enabled, prefer on-demand invocation rather than always-on MCP.  
**Revalidate when:** Service/source quality, privacy, API/pricing, or native web/docs capabilities change.  
**Remove:** Remove integration and revoke API key if unused.

## Firecrawl

**Role:** Large-scale web crawl/scrape/structured extraction.  
**Status:** `DEFERRED`  
**Source/pin:** Review/pin when a web-acquisition project actually needs it.  
**Activate when:** `WEB_ACQUISITION` involves many pages, JS-heavy sites, or structured crawl/extraction that native web access cannot efficiently provide.  
**Material risk:** Network/data egress, API/service cost, licensing/self-host complexity, target-site terms/robots/legal constraints.  
**Overlap:** Native web search/browser access.  
**Decision:** Not foundation infrastructure; project-specific acquisition engine.  
**Revalidate when:** A real crawling requirement appears.  
**Remove:** Remove service/API integration and credentials.

## AnySearch

**Role:** Alternative search layer.  
**Status:** `DEFERRED`  
**Decision:** No demonstrated cross-project advantage over existing web/search paths. Reconsider only if a real workload shows a concrete quality/cost gap.

---

# 7. AI runtime / evaluation

## Promptfoo

**Role:** LLM/agent behavior evaluation and red-team harness.  
**Status:** `CANDIDATE`  
**Source/pin:** Pin reviewed stable release/config when adopted.  
**Activate when:** `AI_RUNTIME` means product/runtime correctness materially depends on LLM behavior.  
**Material risk:** Can call paid models/tools; adversarial tests may trigger powerful actions if not isolated; generated eval artifacts/config need review.  
**Overlap:** Custom eval scripts; provider-specific tests.  
**Decision:** Strong current candidate for AI-runtime evaluation, not a deterministic-software default.  
**Revalidate when:** Provider integrations/eval semantics/licensing/support materially change.  
**Remove:** Remove eval config/tool after preserving any accepted Golden Set/evidence needed by project authority.

## DeepSeek Harness

**Role:** Provider-specific DeepSeek multi-turn/tool/reasoning protocol adapter and diagnostics.  
**Status:** `CANDIDATE`  
**Source/pin:** Pin exact reviewed release/commit; do not execute helper scripts directly from `main`.  
**Activate when:** A runtime directly uses DeepSeek multi-turn reasoning/tool calls/streaming and benefits from provider-specific protocol handling.  
**Material risk:** Third-party personal project, provider policy choices can be mixed with true protocol requirements, API credentials/cost.  
**Overlap:** Direct official DeepSeek API integration.  
**Decision:** Prefer runtime library first; CLI for diagnostics; MCP only when DeepSeek itself must be exposed as an agent tool; Skill default off.  
**Revalidate when:** Official DeepSeek API semantics or library implementation materially change.  
**Remove:** Remove library/CLI/MCP integration and confirm no residual credentials/processes.

---

# 8. UI quality / QA

## Taste family

**Role:** UI design-quality guidance.  
**Status:** `DEFERRED`  
**Source/pin:** Choose reviewed stable version/commit when a real UI project needs it; do not blindly follow experimental `main`.  
**Activate when:** `UI` work materially benefits from design-quality discipline.  
**Material risk:** Rapidly evolving/experimental variants; instruction/context overhead.  
**Overlap:** Native design reasoning, project design system.  
**Decision:** Approved source family for future evaluation, but no version frozen at foundation level.  
**Revalidate when:** First real UI project starts or a stable release supersedes experimental branches.  
**Remove:** Remove Skill/config.

## Playwright

**Role:** Deterministic browser/UI regression testing and trace-based debugging.  
**Status:** `CANDIDATE`  
**Source/pin:** Use project-appropriate stable release/lockfile.  
**Activate when:** A local web/UI project has repeatable user journeys worth regression testing.  
**Material risk:** Browser/runtime dependencies; test maintenance.  
**Overlap:** Manual/Computer Use exploratory QA.  
**Decision:** Use for deterministic repeatable UI flows; do not require a broad multi-browser matrix by default for private single-user projects.  
**Revalidate when:** Project UI/runtime changes materially.  
**Remove:** Remove test/runtime dependencies after preserving needed evidence.

## Codex Computer Use

**Role:** Exploratory UI QA.  
**Status:** `DEFERRED`  
**Source/pin:** Native product capability; availability may change.  
**Activate when:** Human-like exploratory interaction provides value beyond deterministic UI tests.  
**Material risk:** Can interact with UI and cause side effects; use appropriate sandbox/authorization.  
**Overlap:** Playwright/manual testing.  
**Decision:** Exploratory complement, not deterministic verification replacement.

---

# 9. Data durability

## Kopia

**Role:** Cross-machine/local backup and restore for valuable state.  
**Status:** `CANDIDATE`  
**Source/pin:** Pin reviewed stable release before adoption.  
**Activate when:** `VALUABLE_STATE` cannot be cheaply regenerated and a user-friendly scheduled snapshot/restore workflow is justified.  
**Material risk:** Backup credentials/encryption keys become critical secrets; storage targets incur capacity/cost; restore must be tested.  
**Overlap:** restic, storage-system-native backup.  
**Decision:** Current first general desktop-friendly candidate; project/storage-native consistent backup remains preferred when it is the correct state-level mechanism.  
**Revalidate when:** Reliability/maintenance/UI/support changes or a project-specific storage system has a better native recovery mechanism.  
**Remove:** Preserve repository encryption/recovery material and needed snapshots before uninstalling.

## restic

**Role:** CLI-oriented encrypted snapshot backup/restore.  
**Status:** `DEFERRED`  
**Source/pin:** Pin stable release when adopted.  
**Activate when:** CLI/automation simplicity is preferred over Kopia-style GUI/policy management.  
**Material risk:** Repository credentials/encryption keys, storage/cost, restore validation.  
**Overlap:** Kopia.  
**Decision:** Strong fallback, not current first desktop default.

---

# 10. Explicitly deferred / not-foundation capabilities

## Trinity-style persistent multi-agent task bus

**Role:** Persistent task IDs/task bus/review gates/cross-provider orchestration.  
**Status:** `DEFERRED`  
**Decision:** Do not build now. Native subagents/worktrees and a single project brain remain preferred until a real persistent cross-provider coordination failure demonstrates the need.

## OpenTelemetry as a default

**Role:** Distributed tracing/metrics/logging framework.  
**Status:** `REJECTED` as default foundation infrastructure.  
**Decision:** Local single-user projects normally need status/logs/ledger, not a distributed observability stack. Re-evaluate only for genuinely complex multi-process systems.

## Default cloud CI/CD stack

**Role:** Remote integration/deployment automation.  
**Status:** `REJECTED` as a universal foundation requirement.  
**Decision:** A Canonical Verification Path is the requirement. Remote CI/CD is optional when a project actually benefits from it.

## Warp as foundation

**Role:** Terminal/UX environment.  
**Status:** `REJECTED` as foundation requirement.  
**Decision:** Optional user preference, not project governance.

---

# 11. Current unresolved decisions

The registry intentionally leaves some items unresolved.

High-value future evidence gates:

1. **Ponytail full Plugin vs absorbed short rule:** only a minimal real behavioral comparison can decide whether always-on Plugin behavior is worth its context/Hook footprint.
2. **CodeGraph activation threshold:** defer until a real large/unfamiliar repository creates measurable native-navigation friction.
3. **Taste concrete version:** choose at first real UI activation, preferring stable/pinned releases.
4. **Security scanner final admission:** local deterministic fixture comparison should confirm the preferred scanner before promoting to `APPROVED`.
5. **mise final machine-level admission:** test on the owner’s real Windows environment before promoting to `APPROVED`.

No unresolved Tool Registry item blocks Contract Version 3.1 because the constitution defines capability governance, not product winners.
