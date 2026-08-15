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
    CandidateDecision,
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
    FillStatus,
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

    def test_same_contract_opposing_intents_are_order_independent_and_loser_never_executes(self):
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidate_a = self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG)
        candidate_b = self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.SHORT)

        first, first_ledger = self.run_portfolio((member_a, member_b), (candidate_a, candidate_b))
        second, second_ledger = self.run_portfolio((member_b, member_a), (candidate_b, candidate_a))

        first_summary = tuple(
            (outcome.request_id, outcome.decision, outcome.reason)
            for outcome in first.candidate_outcomes
        )
        second_summary = tuple(
            (outcome.request_id, outcome.decision, outcome.reason)
            for outcome in second.candidate_outcomes
        )
        self.assertEqual(first_summary, second_summary)
        self.assertEqual(first.evaluation_identity.identity_id, second.evaluation_identity.identity_id)
        self.assertEqual(first.conflicts, second.conflicts)
        self.assertEqual(
            [record.record_id for record in first_ledger.records],
            [record.record_id for record in second_ledger.records],
        )
        self.assertEqual({item.resolution.concrete_instrument_id for item in first.candidate_outcomes}, {"A"})
        accepted = [item for item in first.candidate_outcomes if item.decision is CandidateDecision.ACCEPTED]
        rejected = [item for item in first.candidate_outcomes if item.decision is CandidateDecision.REJECTED_CONFLICT]
        self.assertEqual(len(accepted), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(accepted[0].execution_outcome.status, FillStatus.FILLED)
        expected_fill_price = (
            Decimal("100.5")
            if accepted[0].direction is PositionDirection.LONG
            else Decimal("99.5")
        )
        self.assertEqual(accepted[0].execution_outcome.fill_price, expected_fill_price)
        self.assertIsNone(rejected[0].execution_outcome)
        self.assertIsNone(rejected[0].capital_transition)

    def test_same_direction_candidates_keep_separate_strategy_attribution_and_reconcile(self):
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidates = (
            self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
            self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
        )

        result, ledger = self.run_portfolio((member_a, member_b), candidates)

        self.assertTrue(result.confirmed)
        self.assertEqual(result.conflicts, ())
        self.assertTrue(
            all(item.execution_outcome.status is FillStatus.FILLED for item in result.candidate_outcomes)
        )
        self.assertEqual(len(result.sleeves), 2)
        self.assertEqual({len(sleeve.positions) for sleeve in result.sleeves}, {1})
        self.assertEqual(
            {position.strategy_identity_id for sleeve in result.sleeves for position in sleeve.positions},
            {member_a.strategy.identity_id, member_b.strategy.identity_id},
        )
        self.assertEqual(
            {position.concrete_contract_id for sleeve in result.sleeves for position in sleeve.positions},
            {"A"},
        )
        self.assertEqual(
            {position.execution_assumption_id for sleeve in result.sleeves for position in sleeve.positions},
            {self.execution_assumptions.identity_id},
        )
        self.assertEqual(
            {position.capital_assumption_id for sleeve in result.sleeves for position in sleeve.positions},
            {self.capital_assumptions.identity_id},
        )
        self.assertEqual(result.shared_capital.reserved_margin, Decimal("20.10"))
        self.assertEqual(result.shared_capital.charged_costs, Decimal("0.50"))
        self.assertEqual(
            result.reconciliation.shared_reserved_margin,
            result.reconciliation.sleeve_reserved_margin,
        )
        self.assertEqual(
            result.reconciliation.shared_charged_costs,
            result.reconciliation.sleeve_charged_costs,
        )
        self.assertEqual(
            result.reconciliation.shared_realized_pnl,
            result.reconciliation.sleeve_realized_pnl,
        )
        self.assertEqual(
            result.reconciliation.shared_unrealized_pnl,
            result.reconciliation.sleeve_unrealized_pnl,
        )
        self.assertNotIn("VALIDATION_CONFIRMED", [record.event_type for record in ledger.records])
        self.assertEqual(
            [record.event_type for record in ledger.records].count("PORTFOLIO_CONFIRMED"),
            2,
        )

    def test_shared_capital_makes_later_candidate_unaffordable_without_double_spending(self):
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidates = (
            self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
            self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
        )

        result, ledger = self.run_portfolio(
            (member_a, member_b),
            reversed(candidates),
            starting_capital=Decimal("15"),
        )
        repeated, repeated_ledger = self.run_portfolio(
            (member_b, member_a),
            candidates,
            starting_capital=Decimal("15"),
        )

        filled = [
            item
            for item in result.candidate_outcomes
            if item.execution_outcome.status is FillStatus.FILLED
        ]
        denied = [
            item
            for item in result.candidate_outcomes
            if item.execution_outcome.reason == "INSUFFICIENT_MARGIN"
        ]
        self.assertEqual(len(filled), 1)
        self.assertEqual(len(denied), 1)
        self.assertEqual(result.shared_capital.reserved_margin, Decimal("10.050"))
        self.assertEqual(result.shared_capital.charged_costs, Decimal("0.25"))
        self.assertEqual(result.reconciliation.position_count, 1)
        self.assertEqual(
            [record.event_type for record in ledger.records].count("PORTFOLIO_CAPITAL_DENIED"),
            1,
        )
        self.assertEqual(result.candidate_outcomes, repeated.candidate_outcomes)
        self.assertEqual(result.shared_capital, repeated.shared_capital)
        self.assertEqual(
            [record.record_id for record in ledger.records],
            [record.record_id for record in repeated_ledger.records],
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

    def test_final_unseen_cannot_be_laundered_through_portfolio_identity(self):
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        candidates = (
            self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
            self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
        )

        result, ledger = self.run_portfolio(
            (member_a, member_b),
            candidates,
            dataset_class=DatasetClass.FINAL_UNSEEN,
        )

        self.assertFalse(result.allowed)
        self.assertFalse(result.confirmed)
        self.assertEqual(result.candidate_outcomes, ())
        self.assertEqual(
            [record.event_type for record in ledger.records],
            ["DATASET_ACCESS_DENIED", "DATASET_ACCESS_DENIED"],
        )
        self.assertEqual(
            {record.experiment.experiment_id for record in ledger.records},
            {member_a.experiment.experiment_id, member_b.experiment.experiment_id},
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
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        result, _ = self.run_portfolio(
            (member_a, member_b),
            (
                self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
                self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
            ),
        )
        corrupted_state = SharedCapitalState(
            result.shared_capital.starting_capital,
            result.shared_capital.reserved_margin + Decimal("1"),
            result.shared_capital.charged_costs,
            result.shared_capital.realized_pnl,
            result.shared_capital.unrealized_pnl,
        )

        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            reconcile_portfolio(corrupted_state, result.sleeves, result.candidate_outcomes)

        first_sleeve, second_sleeve = result.sleeves
        with self.assertRaisesRegex(ValueError, "another strategy"):
            replace(first_sleeve, strategy_identity_id=second_sleeve.strategy_identity_id)

    def test_portfolio_evidence_binds_members_policies_candidates_and_reconciliation(self):
        member_a = self.make_member("a", "MAIN_A")
        member_b = self.make_member("b", "MAIN_B")
        result, ledger = self.run_portfolio(
            (member_a, member_b),
            (
                self.make_candidate(member_a, "request-a", "MAIN_A", PositionDirection.LONG),
                self.make_candidate(member_b, "request-b", "MAIN_B", PositionDirection.LONG),
            ),
        )

        portfolio_records = [
            record for record in ledger.records if record.event_type.startswith("PORTFOLIO_")
        ]
        self.assertTrue(portfolio_records)
        self.assertEqual(
            {record.experiment.experiment_id for record in portfolio_records},
            {member_a.experiment.experiment_id, member_b.experiment.experiment_id},
        )
        self.assertTrue(
            all(result.evaluation_identity.identity_id in record.evidence_reference for record in portfolio_records)
        )
        self.assertTrue(
            all(self.conflict_policy.identity_id in record.evidence_reference for record in portfolio_records)
        )
        reconciled = [record for record in portfolio_records if record.event_type == "PORTFOLIO_RECONCILED"]
        self.assertEqual(len(reconciled), 2)
        self.assertTrue(
            all(record.fact_reference == result.reconciliation.reference_id for record in reconciled)
        )


if __name__ == "__main__":
    unittest.main()
