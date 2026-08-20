# R2_FOUR_LANE_EXECUTION_PLAN_V0_1

> Date: 2026-08-20
> Status: ACTIVE_EXECUTION_AUTHORITY
> Base authority: `CURRENT_STATE.md`, `docs/reviews/PACKAGE_E_OWNER_DECISION_APPROVAL_2026-08-20.md`, `docs/reviews/FGH_CODEX_REBUILD_PREPARATION_V0_1.md`

## Current accepted baseline

`integration/r2-foundation-final-v01` passed project-brain review and full combined regression (478 tests) and was fast-forwarded to `main` at `0c775ee9939778bbde38c2132fe65f120c075a61`.

The following isolated branches are reviewed as useful inputs but are not yet on `main`:

- `repair/package-e-owner-approved-semantics-v01` — implements Owner-approved E-04/E-05/E-08.
- `research/e07-tqsdk-main-mapping-provenance-v01` — establishes that complete TqSdk historical main mapping requires authenticated access and therefore remains fail-closed under current source policy.

## Four concurrent lanes

```text
LANE_1=DS_E_SEMANTICS_E07_FINAL_INTEGRATION
LANE_2=DS_E06_FINAL_STATIC_OFFICIAL_EVIDENCE_PASS
LANE_3=DS_FGH_SEMANTIC_GATE_DECISION_PACKAGE
LANE_4=CODEX_FGH_DETERMINISTIC_REBUILD
MAX_ACTIVE_LANES=4
```

### Lane 1 — E semantics + E07 integration

Merge the reviewed E-04/E-05/E-08 implementation and E07 availability evidence onto latest `main`, run combined regression, and produce one main-ready branch. E07 must remain fail-closed; no login or substitute mapping rule is allowed.

### Lane 2 — E06 final bounded evidence pass

One final bounded attempt to discover and bind official SHFE static attachments for 2024-2025 fee/margin adjustments. No WAF/captcha/login bypass, no current-rate backfill, no third-party value substitution. After this pass, any remaining gaps become explicit long-lived prerequisites rather than triggering open-ended repeated acquisition work.

### Lane 3 — FGH semantic gate decision package

Do not implement production. Re-check source evidence for FGH-GATE-01/02 and prepare a compact Owner-decision package for FGH-GATE-01..06 plus the pre-existing swing/trailing/exit machine-definition ambiguities. Recommendations remain proposals until Owner approval.

### Lane 4 — Codex deterministic F/G/H rebuild

Codex may implement only deterministic engineering work classified as `UNAMBIGUOUS_IMPLEMENTATION_FIX` in `FGH_CODEX_REBUILD_PREPARATION_V0_1.md`, plus port the Holy Grail draft to the current schema while deliberately remaining NOT_MACHINE_READY where semantic gates are unresolved. Codex may not decide or freeze FGH-GATE-01..06 or any swing/trailing/exit semantic.

## Cross-lane boundaries

Lane 1 may modify execution/portfolio integration files and tests. Lane 4 should confine production changes to the Holy Grail draft builder, `src/technical_features.py`, `src/stop_order_execution.py`, their tests/docs, and narrowly necessary synthetic integration files. Lane 2 and Lane 3 are evidence/research only. This separation is intentional so all four lanes can run concurrently.

## Repair-exit criterion

Second-pass repair mode ends after:

1. Lane 1 is accepted and integrated;
2. Lane 4 deterministic F/G/H rebuild is accepted with combined synthetic causal regression;
3. Lane 2 remaining E06 gaps and E07 authenticated-access limitation are encoded as explicit governed prerequisites and cannot be silently bypassed;
4. FGH semantic gates remain either Owner-approved/frozen or explicitly block Holy Grail MACHINE_READY/PRIMARY;
5. one final second-pass closure audit finds no unresolved silent bypass/critical implementation defect.

Candidate outcome access does not need to be unlocked for repair mode to end.
