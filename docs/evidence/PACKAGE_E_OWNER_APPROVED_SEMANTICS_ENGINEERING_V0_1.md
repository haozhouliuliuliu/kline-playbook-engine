# PACKAGE_E_OWNER_APPROVED_SEMANTICS_ENGINEERING_V0_1

> Date: 2026-08-20
> Status: ENGINEERING_COMPLETE
> Authority: `docs/reviews/PACKAGE_E_OWNER_DECISION_APPROVAL_2026-08-20.md`
> Scope: E-04, E-05, E-08 only (E-06, E-07, F/G/H excluded; E-10 already fixed in R1)

This document records the engineering of the Owner-approved semantics. It is
not a re-decision; it implements exactly the approved binding rules.

```text
APPROVE_E04=OPTION_C_EXPLICIT_BUCKET_CHILD_ORDERS
APPROVE_E05=PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS
APPROVE_E08=AVAILABLE_CAPITAL_ONLY
```

## E-04 — generic CLOSE across today + previous buckets

Owner approved `OPTION_C_EXPLICIT_BUCKET_CHILD_ORDERS`.

If one generic `CLOSE` quantity cannot be satisfied wholly by the today bucket
or wholly by the previous bucket, the engine forbids automatic splitting. The
upper execution layer must submit explicit `CLOSE_TODAY` and `CLOSE_PREVIOUS`
child order requests.

Engineering:

- `src/validation_runner.py` `ChronologicalValidationRunner._apply_capital_constraints`
  resolves a generic `CLOSE` to `CLOSE_TODAY` only when the today bucket alone
  satisfies the quantity, and to `CLOSE_PREVIOUS` only when the previous bucket
  alone satisfies it. Otherwise it fails closed with
  `GENERIC_CLOSE_REQUIRES_EXPLICIT_BUCKET_CHILD_ORDERS`.
- No today-first / previous-first automatic split, proportional split, or
  hidden synthetic child-order creation was added. No parent/child OMS
  framework was introduced.

Regression (`tests/test_contract_execution_semantics.py`
`test_generic_close_across_buckets_fails_closed_and_explicit_bucket_orders_flat`):

- Builds `today_quantity=1`, `previous_quantity=1`.
- A generic `CLOSE quantity=2` fails closed with
  `GENERIC_CLOSE_REQUIRES_EXPLICIT_BUCKET_CHILD_ORDERS`.
- The test then explicitly submits `CLOSE_TODAY quantity=1` and
  `CLOSE_PREVIOUS quantity=1` as two independent order requests (never
  auto-generated), producing two independent transitions, each using the
  correct offset fee (`close_today_fee_per_unit` vs `close_previous_fee_per_unit`),
  ending flat with `charged_costs` accumulated across both.

```text
E04_STATUS=ENGINEERED
E04_FAIL_CLOSED=GENERIC_CLOSE_REQUIRES_EXPLICIT_BUCKET_CHILD_ORDERS
E04_AUTO_SPLIT=FORBIDDEN
E04_APPROVED_PATH_EXECUTABLE=VERIFIED
```

## E-05 — heterogeneous portfolio capital assumptions

Owner approved `PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS`.

Each portfolio member resolves its concrete contract first and then uses the
capital/margin assumptions bound to that member + resolved contract.
`ContractSpecification.contract_multiplier` remains the factual multiplier
authority. No single global multiplier, unconstrained multiplier-map, or
global capital service was introduced.

Engineering (`src/portfolio_semantics.py`):

- Added immutable `PortfolioCapitalBinding` with the complete triple
  `strategy_identity_id`, `concrete_contract_id`, `capital_assumptions`.
  `PortfolioCapitalBinding.identity_id` binds the strategy identity, the
  concrete contract, and the capital-assumptions identity.
- `PortfolioRequest` now carries `capital_bindings: tuple[PortfolioCapitalBinding, ...]`
  instead of a single `capital_assumptions`. Rules enforced in
  `PortfolioRequest.__post_init__`:
  - canonical sorted by `(strategy_identity_id, concrete_contract_id)`;
  - `(strategy_identity_id, concrete_contract_id)` unique (no duplicate binding);
  - every `PortfolioMember` strategy has at least one binding (no global fallback;
    no first/default-assumption backdoor).
- `PortfolioCoordinator._resolve_candidates` resolves each candidate by:
  1. finding its member;
  2. resolving the concrete contract first;
  3. finding the unique binding
     `(strategy_identity_id, resolution.concrete_instrument_id)`;
  4. requiring `candidate.capital_assumption_id == binding.capital_assumptions.identity_id`;
  5. requiring the resolved
     `ContractSpecification.contract_multiplier == binding.capital_assumptions.contract_multiplier`;
     otherwise failing closed.
- `PortfolioEvaluationBindings` now binds `capital_binding_ids: tuple[str, ...]`
  (canonical sorted, unique) instead of a single `capital_assumption_id`. The
  portfolio evaluation identity changes whenever any member's capital binding
  changes (not merely the multiplier).
- The portfolio candidate-outcome path is NOT reopened:
  `PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED` remains the final
  fail-closed stop for any test that reaches the outcome path.

Regressions (`tests/test_portfolio_semantics.py`):

- `test_e05_heterogeneous_multiplier_bindings_resolve_structurally` (E05-A):
  member A resolves contract multiplier 5, member B resolves multiplier 10,
  each with its own correct binding; structural resolution succeeds.
- `test_e05_wrong_binding_multiplier_fails_closed` (E05-B): a binding whose
  multiplier does not match the resolved contract fails closed.
- `test_e05_candidate_cannot_borrow_another_member_capital_assumption` (E05-C):
  a candidate referencing another member's capital assumption fails closed.
- `test_e05_duplicate_binding_fails_closed` (E05-D): duplicate
  `(strategy, concrete_contract)` binding fails closed.
- `test_e05_missing_member_binding_fails_closed` (E05-E): a member with no
  binding fails closed (no global fallback).
- `test_e05_evaluation_identity_tracks_member_capital_bindings` (E05-F):
  changing one member's capital binding changes the portfolio evaluation identity.
- `test_e05_outcome_path_remains_closed` (E05-G): after a fully heterogeneous
  structure resolves structurally, the candidate-outcome path still fails
  closed at `PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED`.

```text
E05_STATUS=ENGINEERED
E05_REPRESENTATION=PER_MEMBER_RESOLVED_CONTRACT_ASSUMPTIONS
E05_NO_GLOBAL_FALLBACK=ENFORCED
E05_CANDIDATE_OUTCOME_PATH=REMAINS_CLOSED
```

## E-08 — margin-admission resource

Owner approved `AVAILABLE_CAPITAL_ONLY`.

Open/add admission uses `available_capital = cash_balance - reserved_margin`.
Unrealized PnL neither increases nor decreases new-position admission capacity.
`available_resources = equity - reserved_margin` remains available only for
reporting / maintenance semantics, not as the admission authority.

Engineering:

- `CapitalMarginAssumptions` gained the fixed field
  `margin_admission_resource: str = "AVAILABLE_CAPITAL_ONLY"`.
  `__post_init__` accepts only `AVAILABLE_CAPITAL_ONLY`; no alternative runtime
  option and no generic admission-policy framework were added.
- `CapitalMarginAssumptions.identity_id` now binds
  `margin_admission_resource`, so the admission semantic belongs to the capital
  model identity.
- `_apply_capital_constraints` explicitly decides open/add admission on
  `current.available_capital` against `required_margin + required_cost`. It does
  not use `available_resources`, `equity`, `max(...)`, or any positive-unrealized
  special case. No second admission-helper framework was created.

Regressions (`tests/test_capital_margin_constraints.py`):

- `test_e08_positive_unrealized_pnl_cannot_finance_new_admission` (case A):
  cash-based `available_capital` is insufficient while `available_resources`
  is sufficient due to a large positive unrealized PnL; admission is
  `INSUFFICIENT_MARGIN` (floating profit cannot finance a new position).
- `test_e08_negative_unrealized_pnl_does_not_reduce_admission_capacity`
  (case B): `available_capital` is sufficient while `available_resources` is
  insufficient due to a large negative unrealized PnL; open/add admission is
  still decided by `available_capital` and fills (not silently switched to an
  equity model).
- `test_e08_margin_admission_resource_binds_available_capital_only` (case C):
  `CapitalMarginAssumptions` identity is bound to `AVAILABLE_CAPITAL_ONLY`;
  any other value is rejected and the field participates in the identity.

```text
E08_STATUS=ENGINEERED
E08_MARGIN_ADMISSION_RESOURCE=AVAILABLE_CAPITAL_ONLY
E08_UNREALIZED_PNL_NOT_ADMISSION_AUTHORITY=VERIFIED
E08_ADMISSION_BOUND_TO_IDENTITY=VERIFIED
```

## Excluded scope

Per authority and the Owner implementation instruction, this repair did not
touch E-06 historical fee/margin schedule, E-07 mapping, F/G/H,
`ResearchFirewall` authorization, the canonical corpus, frozen protocol, or
`CURRENT_STATE`. No candidate outcome data were used or authorized.
