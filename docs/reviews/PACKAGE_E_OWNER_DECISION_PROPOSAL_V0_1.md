# PACKAGE_E_OWNER_DECISION_PROPOSAL_V0_1

> Date: 2026-08-20
> Status: PROPOSAL_ONLY_NOT_ADOPTED
> Authority input: `docs/research/PACKAGE_E_GOVERNANCE_AUTHORITY_RESEARCH_V0_1.md`

This document proposes the project-brain preferred choices for the four Owner-gated Package E semantics. Nothing here is frozen or adopted until explicit Owner approval.

## E-04 generic CLOSE across today + previous

Recommended choice:

```text
E04_RECOMMENDATION=OPTION_C_EXPLICIT_BUCKET_CHILD_ORDERS
```

If a generic CLOSE quantity cannot be satisfied wholly by one bucket, the engine does not invent an allocation order. The upper execution layer must emit explicit CLOSE_TODAY and CLOSE_PREVIOUS child orders. This minimizes hidden fee/allocation freedom and is closest to explicit SHFE/TqSdk offset semantics.

## E-05 heterogeneous portfolio capital assumptions

Recommended choice:

```text
E05_RECOMMENDATION=PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS
```

Each portfolio member resolves its concrete contract first, then uses capital/margin assumptions bound to that resolved contract. Contract multiplier remains factual authority from ContractMaster/ContractSpecification. Do not create one global multiplier or a generic multiplier-map framework.

## E-07 research concrete-contract mapping

Recommended choice:

```text
E07_RECOMMENDATION=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
```

Use a source-governed historical TqSdk main-contract mapping / documented KQ.m convention as the mapping authority, while continuing to execute research only on the project's canonical concrete-contract bars. Do not store or substitute pseudo MAIN price bars into the canonical corpus. The mapping must be point-in-time and effective only at the vendor-defined next-trading-day switch; exact historical mapping provenance must be recorded. If a complete historical vendor mapping cannot be obtained without paid/login access or cannot be byte/provenance-bound, fail closed and return to the Owner rather than substitute a project-tuned rule.

Rationale: this minimizes project-authored selection freedom compared with inventing and tuning an OI/volume formula, while keeping the canonical corpus concrete-contract-only.

## E-08 margin-admission resource

Recommended choice:

```text
E08_RECOMMENDATION=AVAILABLE_CAPITAL_ONLY
```

Open/add admission uses cash balance minus reserved margin and does not finance new exposure using unrealized PnL. This is the conservative fail-closed research-account choice. Equity-aware available_resources remains observable for reporting/maintenance but does not enlarge admission capacity.

## Owner approval block

Owner may approve all recommendations in one decision:

```text
APPROVE_E04=OPTION_C_EXPLICIT_BUCKET_CHILD_ORDERS
APPROVE_E05=PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS
APPROVE_E07=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
APPROVE_E08=AVAILABLE_CAPITAL_ONLY
```

Or replace any individual line. Until explicit approval, all four remain NOT_ADOPTED / NOT_FROZEN and workers must not implement them.
