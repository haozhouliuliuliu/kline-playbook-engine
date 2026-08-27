# JIANGHE PAPER FEATURE FREEZE AND INDEPENDENT AUDIT — OWNER DECISION

Status: `OWNER_APPROVED__FEATURE_FREEZE__PROJECT_BRAIN_FINDINGS_ONLY_AUDIT__CODEX_REPAIR_LATER`

Date: `2026-08-28`

Product: `JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

## 1. Owner decision

After the last outcome-independent PAPER login-ready engineering package passes the integration gate, the PAPER prebuild implementation is feature-frozen before the final consolidated acceptance review.

The final review must be independently performed by the project brain rather than delegated to Codex, because a material portion of the implementation has already been authored or repaired by Codex and the Owner requires an independent reviewer.

The review pass is intentionally separated from the later repair pass.

## 2. Feature-freeze rule

Once the exact frozen integration identity is recorded in the feature-freeze evidence:

- do not add new ordinary PAPER features;
- do not expand product scope, broker scope, account scope, strategy scope, OMS scope, deployment scope or platform scope;
- do not perform opportunistic refactors merely to improve style;
- implementation changes after freeze require either a concrete finding from the independent audit or an explicit Owner reopening of feature scope;
- the freeze does not prevent minimal tests/instrumentation required to prove or reproduce an audit finding.

The exact frozen code identity and CI evidence are owned by the corresponding feature-freeze evidence document, not by this stable process decision.

## 3. Independent audit owner and output contract

`AUDIT_REVIEWER_ROLE = PROJECT_BRAIN`

The project brain will inspect the complete feature-frozen PAPER prebuild as one consolidated system.

During that audit pass the project brain must:

- find and substantiate defects, gaps, contradictions, unsafe assumptions or missing evidence;
- list findings clearly enough that a repair worker can independently reproduce and understand them;
- include location/evidence and material impact when useful;
- not implement repairs during the findings-only audit pass;
- not prescribe repair mechanics or code changes by default.

Repair advice is allowed only where the correct constraint depends on project-specific or Owner-specific context that a repair worker cannot reliably infer from the repository itself. In that case, provide only the minimum semantic constraint/direction needed to avoid an incorrect repair.

## 4. Later repair ownership

After the independent project-brain findings are complete, Codex may be assigned a bounded repair package against those findings.

Codex is not the independent final-audit reviewer for the frozen package. Its later role is repair/implementation after findings exist.

The project brain remains the process/integration owner and will decide whether repairs actually close the findings.

## 5. Relationship to the earlier PAPER prebuild decision

This decision refines the execution of the final acceptance requirement in:

`docs/reviews/JIANGHE_PAPER_PREBUILD_PARALLEL_ENGINEERING_OWNER_DECISION_2026-08-27.md`

The earlier requirement for one consolidated targeted PAPER-readiness audit and repair package is not waived. It is now deliberately partitioned into:

```text
FEATURE FREEZE
-> PROJECT-BRAIN INDEPENDENT FINDINGS-ONLY AUDIT
-> CODEX REPAIR PACKAGE
-> PROJECT-BRAIN CLOSURE / REVALIDATION
```

No final readiness or acceptance may be claimed merely because feature implementation is frozen.

## 6. Safety and research boundaries unchanged

This decision does not authorize:

- PAPER account login/connect;
- external PAPER submit/cancel/replace/account mutation;
- broker/account action;
- real money;
- paid provider execution;
- full frozen V0.1 execution;
- post-V0.1 CU/RB paid replay;
- changes to frozen V0.1 research semantics;
- freezing result-dependent sizing, execution-price, close-offset, permanent numeric risk or final contract-whitelist settings.

The approved historical-research -> PAPER promotion route remains unchanged.
