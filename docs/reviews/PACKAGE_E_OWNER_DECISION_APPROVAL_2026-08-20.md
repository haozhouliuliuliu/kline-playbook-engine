# PACKAGE_E_OWNER_DECISION_APPROVAL_2026-08-20

> Date: 2026-08-20
> Status: OWNER_APPROVED_BINDING
> Decision authority: Owner explicit approval in project conversation
> Proposal basis: `docs/reviews/PACKAGE_E_OWNER_DECISION_PROPOSAL_V0_1.md`
> Research basis: `docs/research/PACKAGE_E_GOVERNANCE_AUTHORITY_RESEARCH_V0_1.md`

The Owner explicitly approved all four project-brain recommendations as one decision. These semantics are now binding for subsequent implementation. Workers may implement them but may not substitute alternative rules without a new Owner decision.

```text
APPROVE_E04=OPTION_C_EXPLICIT_BUCKET_CHILD_ORDERS
APPROVE_E05=PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS
APPROVE_E07=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
APPROVE_E08=AVAILABLE_CAPITAL_ONLY
```

## E-04 — generic CLOSE across today + previous buckets

If one generic `CLOSE` cannot be satisfied wholly by one position bucket, the engine must not invent an automatic allocation order. The upper execution layer must emit explicit `CLOSE_TODAY` and `CLOSE_PREVIOUS` child orders. Fee/accounting evidence remains bound to those explicit bucket orders.

```text
E04_STATUS=OWNER_APPROVED_BINDING
E04_AUTO_SPLIT_GENERIC_CLOSE=FORBIDDEN
E04_REQUIRED_SEMANTIC=EXPLICIT_BUCKET_CHILD_ORDERS
```

## E-05 — heterogeneous portfolio capital assumptions

Each portfolio member resolves its concrete contract first and then uses capital/margin assumptions bound to that resolved contract. `ContractMaster` / `ContractSpecification.contract_multiplier` remains the factual multiplier authority. Do not replace this with one global multiplier or an unconstrained generic multiplier-map framework.

```text
E05_STATUS=OWNER_APPROVED_BINDING
E05_CAPITAL_REPRESENTATION=PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS
```

## E-07 — research concrete-contract mapping

The adopted research mapping direction is a source-governed historical TqSdk main-contract mapping / documented `KQ.m@` convention, applied only to select the project's canonical concrete-contract bars. Pseudo-main price bars do not enter the canonical corpus. Mapping must be point-in-time and apply only at the source-defined next-trading-day switch. Exact historical mapping provenance must be recorded.

If complete historical source-governed mapping cannot be obtained under the project's free/public/no-login source policy or cannot be provenance-bound, the project must fail closed and return to the Owner. It must not substitute a project-tuned OI/volume rule and must not choose a rule using outcomes.

```text
E07_STATUS=OWNER_APPROVED_BINDING
E07_MAPPING=SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS
E07_PSEUDO_MAIN_PRICE_BARS_IN_CANONICAL_CORPUS=FORBIDDEN
E07_OUTCOME_BASED_MAPPING_SELECTION=FORBIDDEN
```

## E-08 — margin-admission resource

Open/add admission uses `available_capital = cash_balance - reserved_margin`. Unrealized PnL does not increase new-position admission capacity. `available_resources = equity - reserved_margin` remains available for reporting/maintenance semantics but is not the opening/addition admission authority.

```text
E08_STATUS=OWNER_APPROVED_BINDING
E08_MARGIN_ADMISSION_RESOURCE=AVAILABLE_CAPITAL_ONLY
```

## Non-decisions

This approval does not authorize candidate outcome access, Validation, historical final holdout access, Shadow/Forward, real-money trading, broker access, paid source purchases, or any change to the frozen 12/6/6 protocol.

E-06 historical fee/margin evidence remains an evidence-collection prerequisite and is not resolved by this decision.

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
E06_HISTORICAL_FEE_MARGIN_EVIDENCE=STILL_REQUIRED
```
