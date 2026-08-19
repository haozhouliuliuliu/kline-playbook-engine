import unittest
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.contract_semantics import (
    ContractMappingEntry,
    ContractMappingSchedule,
    ContractMaster,
    ContractSpecification,
    OffsetCostAssumptions,
    OrderAction,
    PriceLimitFact,
)
from src.data_substrate import CompletedBar, SessionMetadata, SessionWindow
from src.portfolio_semantics import (
    AttributedPosition,
    PortfolioCandidate,
    PortfolioConflictPolicy,
    PortfolioCoordinator,
    PortfolioEvaluationBindings,
    PortfolioEvaluationIdentity,
    PortfolioMember,
    PortfolioRequest,
    PositionDirection,
    SharedCapitalState,
    SharedCapitalPolicy,
    StrategySleeve,
    reconcile_portfolio,
)
from src.strategy_evidence import (
    DatasetClass,
    EvidenceLedger,
    ExperimentIdentity,
    FinalUnseenFirewall,
    LifecycleState,
    StrategyIdentity,
    TypedParameter,
)
from src.validation_runner import (
    CapitalMarginAssumptions,
    ExecutionAssumptions,
    ExecutionObservation,
    OrderSpecification,
    ValidationInput,
    ValidationMode,
)


CN = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 6, 16)


def at(hour, minute):
    return datetime(2025, 6, 16, hour, minute, tzinfo=CN)


def make_strategy(name, instruments=("SYNTH_MAIN",)):
    return StrategyIdentity(
        research_lineage_id=f"portfolio-lineage-{name}",
        family_id=f"portfolio-family-{name}",
        strategy_version="1.0",
        source="deterministic-synthetic-portfolio-fixture",
        applicable_instruments=tuple(sorted(instruments)),
        timeframe="5m",
        parameters=(TypedParameter("window", "int", 3),),
        code_hash=f"portfolio-code-{name}",
        environment_hash="portfolio-environment-v1",
        required_feature_versions=("portfolio-feature-v1",),
        lifecycle_state=LifecycleState.DRAFT,
        data_exposure_history_reference=f"portfolio-exposure-{name}",
    )


class PortfolioSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.execution_assumptions = ExecutionAssumptions(
            "synthetic-portfolio-execution-v1",
            Decimal("0.5"),
            Decimal("0.25"),
        )
        self.capital_assumptions = CapitalMarginAssumptions(
            "synthetic-portfolio-capital-v1",
            Decimal("1"),
            Decimal("0.1"),
            "SYNTH",
            Decimal("0.05"),
        )
        self.offset_costs = OffsetCostAssumptions(
            "synthetic-portfolio-offset-v1",
            Decimal("1"),
            Decimal("2"),
        )
        self.contract = ContractSpecification(
            "SYNTH_EX",
            "SYNTH_PRODUCT",
            "A",
            at(8, 0),
            at(18, 0),
            Decimal("1"),
            Decimal("0.5"),
            "SYNTH",
            "SYNTH_UNIT",
            "synthetic-portfolio-limit-rule-v1",
            self.offset_costs.identity_id,
            "synthetic-portfolio-contract-v1",
        )
        self.master = ContractMaster("synthetic-portfolio-master-v1", (self.contract,))
        self.mapping_entries = (
            ContractMappingEntry("MAIN_A", "A", at(8, 0), at(18, 0), at(8, 0), "mapping-a-v1"),
            ContractMappingEntry("MAIN_B", "A", at(8, 0), at(18, 0), at(8, 0), "mapping-b-v1"),
        )
        self.schedule = ContractMappingSchedule(
            "synthetic-portfolio-schedule-v1",
            ("MAIN_A", "MAIN_B"),
            self.mapping_entries,
        )
        self.sessions = SessionMetadata(
            "synthetic-portfolio-session-v1",
            (SessionWindow("SYNTH_EX", "A", DAY, at(9, 0), at(11, 0), "DAY"),),
        )
        self.limit_fact = PriceLimitFact(
            "synthetic-portfolio-limit-a",
            "A",
            self.contract.identity_id,
            DAY,
            Decimal("90"),
            Decimal("110"),
            at(8, 50),
            at(8, 50),
            "synthetic-portfolio-limit-rule-v1",
        )
        self.conflict_policy = PortfolioConflictPolicy("synthetic-conflict-v1")
        self.shared_policy = SharedCapitalPolicy("synthetic-shared-capital-v1")

    def make_member(self, name, symbol):
        strategy = make_strategy(name, (symbol,))
        return PortfolioMember(
            strategy,
            ExperimentIdentity.from_strategy(
                strategy,
                "portfolio-data-v1",
                f"portfolio-exposure-{name}",
            ),
        )

    def make_candidate(self, member, request_id, symbol, direction, quantity=Decimal("1")):
        decision_at = at(9, 5)
        validation_input = ValidationInput(
            request_id,
            CompletedBar(
                symbol,
                DAY,
                decision_at - timedelta(minutes=5),
                decision_at,
                decision_at,
            ),
            decision_at,
            member.experiment.data_version,
        )
        return PortfolioCandidate(
            member.strategy.identity_id,
            member.experiment.experiment_id,
            validation_input,
            OrderSpecification(request_id, quantity, OrderAction.OPEN, direction=direction),
            ExecutionObservation(
                request_id,
                at(9, 6),
                at(9, 6),
                Decimal("100"),
                concrete_contract_id="A",
            ),
            direction,
            self.execution_assumptions.identity_id,
            self.capital_assumptions.identity_id,
        )

    def run_portfolio(
        self,
        members,
        candidates,
        starting_capital=Decimal("100"),
        dataset_class=DatasetClass.VALIDATION,
        mode=ValidationMode.CONFIRMATORY,
    ):
        ledger = EvidenceLedger()
        coordinator = PortfolioCoordinator(ledger, FinalUnseenFirewall(ledger))
        result = coordinator.evaluate(
            PortfolioRequest(
                mode,
                dataset_class,
                tuple(members),
                tuple(candidates),
                starting_capital,
                self.conflict_policy,
                self.shared_policy,
                self.master,
                self.schedule,
                self.sessions,
                (self.limit_fact,),
                self.execution_assumptions,
                self.capital_assumptions,
                self.offset_costs,
                at(9, 30),
            )
        )
        return result, ledger

    def test_portfolio_identity_is_order_independent_and_policy_sensitive(self):
        strategy_a = make_strategy("a")
        strategy_b = make_strategy("b")
        members = (
            PortfolioMember(
                strategy_a,
                ExperimentIdentity.from_strategy(strategy_a, "portfolio-data-v1", "portfolio-exposure-a"),
            ),
            PortfolioMember(
                strategy_b,
                ExperimentIdentity.from_strategy(strategy_b, "portfolio-data-v1", "portfolio-exposure-b"),
            ),
        )
        conflict_policy = PortfolioConflictPolicy("synthetic-conflict-v1")
        shared_policy = SharedCapitalPolicy("synthetic-shared-capital-v1")
        bindings = PortfolioEvaluationBindings(
            DatasetClass.VALIDATION,
            "contract-master-id",
            "mapping-schedule-id",
            "session-metadata-v1",
            "execution-assumption-id",
            "capital-assumption-id",
            ("limit-fact-b", "limit-fact-a"),
            "offset-cost-id",
        )

        first = PortfolioEvaluationIdentity.create(members, conflict_policy, shared_policy, bindings)
        reordered = PortfolioEvaluationIdentity.create(reversed(members), conflict_policy, shared_policy, bindings)
        changed_policy = PortfolioEvaluationIdentity.create(
            members,
            PortfolioConflictPolicy("synthetic-conflict-v2"),
            shared_policy,
            bindings,
        )

        self.assertEqual(first.identity_id, reordered.identity_id)
        self.assertEqual(first.member_bindings, reordered.member_bindings)
        self.assertNotEqual(first.identity_id, changed_policy.identity_id)

    def test_confirmatory_portfolio_opposing_intent_path_is_closed(self):
        # F-02: the CONFIRMATORY portfolio candidate-outcome path is closed; no
        # order-independent arbitration or loser-execution can occur.
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidate_a = self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG)
        candidate_b = self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.SHORT)

        with self.assertRaisesRegex(ValueError, "PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED"):
            self.run_portfolio((member_a, member_b), (candidate_a, candidate_b))
        with self.assertRaisesRegex(ValueError, "PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED"):
            self.run_portfolio((member_b, member_a), (candidate_b, candidate_a))

    def test_confirmatory_portfolio_same_direction_path_is_closed(self):
        # F-02: no strategy attribution / shared-capital reconciliation can be
        # produced through the closed CONFIRMATORY portfolio path.
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidates = (
            self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
            self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
        )

        with self.assertRaisesRegex(ValueError, "PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED"):
            self.run_portfolio((member_a, member_b), candidates)

    def test_confirmatory_portfolio_shared_capital_path_is_closed(self):
        # F-02: the shared-capital execution path cannot run through the closed
        # CONFIRMATORY portfolio path.
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidates = (
            self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
            self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
        )

        with self.assertRaisesRegex(ValueError, "PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED"):
            self.run_portfolio(
                (member_a, member_b),
                reversed(candidates),
                starting_capital=Decimal("15"),
            )

    def test_member_binding_duplicate_membership_and_duplicate_request_fail_closed(self):
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        with self.assertRaisesRegex(ValueError, "does not bind"):
            PortfolioMember(member_a.strategy, member_b.experiment)

        bindings = PortfolioEvaluationBindings(
            DatasetClass.VALIDATION,
            self.master.identity_id,
            self.schedule.identity_id,
            self.sessions.version,
            self.execution_assumptions.identity_id,
            self.capital_assumptions.identity_id,
            (self.limit_fact.identity_id,),
            self.offset_costs.identity_id,
        )
        with self.assertRaisesRegex(ValueError, "duplicate strategy"):
            PortfolioEvaluationIdentity.create(
                (member_a, member_a),
                self.conflict_policy,
                self.shared_policy,
                bindings,
            )

        duplicate_a = self.make_candidate(
            member_a,
            "duplicate-request",
            "MAIN_A",
            PositionDirection.LONG,
        )
        duplicate_b = self.make_candidate(
            member_b,
            "duplicate-request",
            "MAIN_B",
            PositionDirection.LONG,
        )
        with self.assertRaisesRegex(ValueError, "duplicate portfolio request"):
            self.run_portfolio((member_a, member_b), (duplicate_a, duplicate_b))

    def test_candidate_assumption_and_mapping_inconsistency_fail_closed(self):
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        valid_a = self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG)
        valid_b = self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG)
        with self.assertRaisesRegex(ValueError, "execution assumption"):
            self.run_portfolio(
                (member_a, member_b),
                (replace(valid_a, execution_assumption_id="wrong-execution-id"), valid_b),
            )

        unknown_member = self.make_member("unknown", "UNKNOWN_MAIN")
        unknown_candidate = self.make_candidate(
            unknown_member,
            "request-unknown",
            "UNKNOWN_MAIN",
            PositionDirection.LONG,
        )
        with self.assertRaisesRegex(ValueError, "neither an explicit concrete contract"):
            self.run_portfolio(
                (unknown_member, member_b),
                (unknown_candidate, valid_b),
            )

    def test_final_unseen_portfolio_path_is_closed(self):
        # F-02: even for FINAL_UNSEEN the CONFIRMATORY portfolio outcome path
        # fails closed instead of running a legacy grant path.
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidates = (
            self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
            self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
        )

        with self.assertRaisesRegex(ValueError, "PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED"):
            self.run_portfolio(
                (member_a, member_b),
                candidates,
                dataset_class=DatasetClass.FINAL_UNSEEN,
            )

    def test_fast_portfolio_path_cannot_emit_confirmation(self):
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        with self.assertRaisesRegex(ValueError, "FAST"):
            self.run_portfolio(
                (member_a, member_b),
                (
                    self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
                    self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
                ),
                mode=ValidationMode.FAST,
            )

    def test_reconciliation_mismatch_fails_closed(self):
        # The reconciliation invariant is unit-tested directly now that the
        # CONFIRMATORY portfolio outcome path is closed (Package A / F-02).
        position = AttributedPosition(
            "strategy-a-id",
            "experiment-a-id",
            "request-1",
            "A",
            "contract-a-id",
            PositionDirection.LONG,
            Decimal("1"),
            Decimal("10"),
            Decimal("0.25"),
            Decimal("0"),
            Decimal("0"),
            "exec-a",
            "cap-a",
            "snap-a",
        )
        sleeve = StrategySleeve.from_positions("strategy-a-id", "experiment-a-id", (position,))
        state = SharedCapitalState(
            Decimal("100"),
            reserved_margin=Decimal("10"),
            charged_costs=Decimal("0.25"),
        )
        reconciled = reconcile_portfolio(state, (sleeve,), ())
        self.assertEqual(reconciled.position_count, 1)

        corrupted_state = SharedCapitalState(
            Decimal("100"),
            reserved_margin=Decimal("11"),
            charged_costs=Decimal("0.25"),
        )
        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            reconcile_portfolio(corrupted_state, (sleeve,), ())

        with self.assertRaisesRegex(ValueError, "another strategy"):
            replace(sleeve, strategy_identity_id="strategy-b-id")

    def test_portfolio_evidence_path_is_closed(self):
        # F-02: no PORTFOLIO_* outcome evidence records can be produced through
        # the closed CONFIRMATORY portfolio path.
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidates = (
            self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
            self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
        )

        with self.assertRaisesRegex(ValueError, "PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED"):
            self.run_portfolio((member_a, member_b), candidates)

    def test_portfolio_legacy_coarse_grant_path_is_closed(self):
        # A10 / F-02: the portfolio legacy coarse-grant path is closed; no
        # execution outcome, capital mutation, or PORTFOLIO_CONFIRMED can occur.
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidates = (
            self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
            self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
        )
        ledger = EvidenceLedger()
        coordinator = PortfolioCoordinator(ledger, FinalUnseenFirewall(ledger))
        with self.assertRaisesRegex(ValueError, "PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED"):
            coordinator.evaluate(
                PortfolioRequest(
                    ValidationMode.CONFIRMATORY,
                    DatasetClass.DEVELOPMENT,
                    (member_a, member_b),
                    candidates,
                    Decimal("100"),
                    self.conflict_policy,
                    self.shared_policy,
                    self.master,
                    self.schedule,
                    self.sessions,
                    (self.limit_fact,),
                    self.execution_assumptions,
                    self.capital_assumptions,
                    self.offset_costs,
                    at(9, 30),
                )
            )
        # No legacy coarse grant, no execution, no capital mutation, no confirmation.
        self.assertEqual(ledger.records, ())


if __name__ == "__main__":
    unittest.main()
