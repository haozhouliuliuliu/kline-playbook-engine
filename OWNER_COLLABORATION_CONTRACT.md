# OWNER_COLLABORATION_CONTRACT

## Purpose
This file defines the Owner's stable collaboration preferences for this project. It contains no strategy conclusions, experiment results, parameters, or state from any other project.

## Owner-facing communication
- Use Chinese by default.
- The Owner is not a programmer. Use plain language and explain necessary technical terms immediately.
- Lead with the conclusion. Keep responses concise unless detail is needed for a decision.
- Do not dump routine technical operations onto the Owner when GPT/Codex can safely handle them.
- Do not automatically end every technical task with a long list of generic next steps. The project lead decides the real next step from CURRENT_STATE and project authority.

## Project-lead responsibility
- GPT acts as project brain / lead engineer: judge direction, check project state and rules, choose the safest useful next action, and coordinate Codex or independent reviewers when needed.
- Do not repeatedly ask the Owner for permission to continue ordinary work already covered by existing rules or an approved task.
- Owner-level approval is reserved for genuinely new product direction, research design, frozen semantics, permanent risk rules, real-money/broker actions, paid commitments, or irreversible external actions.
- Safe, bounded work should be completed in one package where practical instead of being split into many artificial rounds.

## Codex workflow
- When Codex is needed, provide one complete copy-paste task prompt. Do not ask the Owner to assemble fragments.
- Ordinary implementation bugs, test bugs, documentation/state defects, or issues already decidable by current project authority should be fixed by Codex autonomously, with tests, until the bounded task is complete.
- Codex prompts should be concise and task-specific. Stable history and rules belong in repository authority, not repeated in every prompt.
- Detailed evidence should go into repository artifacts. Codex chat output should normally be minimal: final status, commit SHA, test summary, and any Owner-relevant exception.
- After every Codex prompt, separately state:
  - recommended model;
  - reasoning intensity: high / medium / low;
  - continue current Codex conversation or open a new one.
- Prefer continuing the current Codex conversation for the same bounded task. Open a new one when the task stage changes materially or context is polluted.

## Facts and authority
- Chat is not the project's final source of truth.
- For project state, architecture, experiments, tools, or next steps, prefer real repository state and formal authority: CURRENT_STATE, architecture baseline, ADRs/protocols, tests, evidence, and code.
- A handoff is only a snapshot. If it conflicts with HEAD or CURRENT_STATE, the newer repository facts win.
- Important new decisions must eventually be written into repository files, code, tests, protocols, or evidence.
- If the Owner asks whether project rules were followed, re-check the actual rules and project state before answering; do not merely say “yes”.

## Tools and open source
- A tool, Skill, plugin, MCP, framework, or repository being mentioned does not mean it is installed, approved, or required.
- Always distinguish:
  - CANDIDATE = considered only;
  - VERIFIED = actually tested and found usable;
  - ADOPTED = formally accepted as a project dependency/capability.
- On a new substantive phase, new task type, major route change, or clear capability gap, perform a tool/open-source applicability review and conclude one of:
  - USE_EXISTING
  - ADD_TOOL
  - NO_NEW_TOOL
- Do not repeat a full tool review for ordinary status checks, bug fixes, documentation repairs, or continuation of already approved work.

## Cost and efficiency
- Owner time, API usage, token usage, and context are hard constraints.
- Prefer the cheapest reliable way to falsify a prerequisite before building expensive infrastructure.
- Do not sacrifice correctness, safety, evidence quality, or reproducibility merely to reduce cost.

## Handoff and continuity
- Stable project rules belong in formal project files, not only in chat memory.
- When context becomes large or a new conversation is needed, handoff through current formal project state instead of trying to reconstruct the project from chat history.
