# PROJECT GOVERNANCE OWNERSHIP REPAIR — OWNER DECISION

Status: `OWNER_APPROVED`

Date: `2026-08-27`

Scope: `GOVERNANCE / CONTEXT CONTINUITY / AUTHORITY OWNERSHIP ONLY`

## Trigger

The Owner observed repeated fresh-conversation loss and authority drift, including a concrete local-runtime continuity failure where a new conversation did not know the already-established DeepSeek credential location contract.

The Owner explicitly directed the project to stop provider-smoke execution for now and repair the governance/context structure instead of delegating the smoke to another fresh conversation.

## Owner decision

The project adopts the operating principle:

`ONE_CONCERN__ONE_CANONICAL_OWNER`

Dynamic facts must not be copied across many active files merely for convenience.

The following ownership split is approved:

| Concern | Canonical owner |
| --- | --- |
| stable project governance / authority ownership | `PROJECT_GOVERNANCE.md` |
| scoped worker / repository operating procedure | `AGENTS.md` |
| long-lived architecture | `ARCHITECTURE_BASELINE.md` |
| tool/provider/framework status, pins, credential seam, revalidation rules | `TOOL_REGISTRY.md` |
| product / research direction | `PROJECT_DIRECTION.md` |
| current phase / work package / locks / next task | `CURRENT_STATE.md` |
| refresh procedure for project brain | `PROJECT_BRAIN_RUNTIME_BRIEF.md` |
| fresh-conversation navigation | `00_READ_FIRST.md` |
| project landing page | `README.md` |
| unresolved capability limitations / technical debt | `KNOWN_LIMITATIONS_AND_TECH_DEBT.md` |
| exact paid/external execution permission | exact Owner execution authority + machine-readable authority |

## DeepSeek credential continuity

The repository must record only the credential **location contract**, never the secret value.

For the current adopted DeepSeek provider path:

`CREDENTIAL_ENV = DEEPSEEK_API_KEY`

`CREDENTIAL_LOCATION = OWNER_WINDOWS_USER_ENVIRONMENT`

The secret value must never be committed, printed, logged, copied into project authority, or requested for storage in chat. Runtime checks may report only `SET / UNSET` or equivalent non-secret availability state.

The canonical owner for this credential seam is `TOOL_REGISTRY.md`.

## Provider-smoke hold

The previously approved exact three-call provider-smoke authority remains an immutable record of the approved sealed slot, but the Owner now directs:

`PROVIDER_SMOKE_EXECUTION = OWNER_HOLD_BEFORE_FIRST_CALL`

`PROVIDER_CALLS_DURING_GOVERNANCE_REPAIR = 0`

Do not delegate or resume the provider smoke in a fresh conversation while this hold is current.

The hold does not consume or widen the prior paid slot. It does not authorize a fourth call, full 1998-call replay, post-V0.1 paid replay, broker/account action, paper execution, or real money.

A later explicit Owner instruction is required to resume the held three-call smoke.

## Migration boundary

This repair does **not** change:

- Jianghe trading semantics;
- current V0.1 frozen replay design;
- sealed `cu / SHFE.cu2406` slice;
- 1998 governed-wake identity;
- DeepSeek model selection;
- Harness pin;
- the already-approved post-V0.1 CU/RB roadmap;
- historical evidence;
- permanent risk rules.

It repairs only governance ownership, takeover continuity and anti-drift enforcement.

## Legacy Contract 3.1

The project previously explicitly adopted `CROSS_PROJECT_OPERATING_CONTRACT.md` Version `3.1` with:

`ADOPTED_CONTRACT_SHA256 = 3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e`

The 2026-08-25 cleanup deleted that file without an explicit replacement/adoption migration. This decision restores the adoption record at the project-governance layer rather than silently inventing a new cross-project constitution.

The exact historical Version 3.1 source remains immutable in Git history at commit `39757116c579a33affb1c58e058a43f1d3f4f6f5`, path `CROSS_PROJECT_OPERATING_CONTRACT.md`.
