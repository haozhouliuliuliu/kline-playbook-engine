"""Deterministic offline tests for the PAPER startup preflight.

Proves the real external profile fails closed today, an offline-rehearsal fake
profile can pass, incomplete result-dependent activation fails closed, no secret
leaks through public lines, and journal/order/wake state is read correctly.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_live_causal_context import LiveCausalContextBuilder
from src.paper_offline_activation_rehearsal import (
    BROKER_ID,
    CONTRACT,
    EXCHANGE,
    INSTRUMENT,
    MORNING_UNTIL,
    PRODUCT,
    RUNTIME_VERSION,
    TRADER_IDENTITY,
    RehearsalFakeBroker,
    RehearsalFakeRiskPlanner,
    RehearsalFakeTrader,
    RehearsalLiveSource,
    build_rehearsal_calendar,
    rehearsal_authority,
    rehearsal_profile,
)
from src.paper_order_journal import PaperOrderJournal
from src.paper_preflight import EXTERNAL, OFFLINE_REHEARSAL, PaperPreflightReport, run_paper_preflight
from src.paper_runtime_assembly import PaperRuntimeAssemblyInputs, assemble_paper_runtime
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_runtime_layout import PaperRuntimeLayout
from src.paper_wake_journal import PaperWakeJournal


def _base_config(state_root: Path) -> PaperRuntimeConfig:
    return PaperRuntimeConfig(
        config_id="PREFLIGHT_CONFIG",
        state_root=state_root,
        trader_identity=TRADER_IDENTITY,
        concrete_contract_id=CONTRACT,
        product=PRODUCT,
        exchange=EXCHANGE,
        tqsdk_runtime_version=RUNTIME_VERSION,
        broker_kind="TQSDK_CANDIDATE",
        account_kind="TQSDK_PAPER",
        symbol=INSTRUMENT,
    )


def _layout(state_root: Path, config: PaperRuntimeConfig) -> PaperRuntimeLayout:
    return PaperRuntimeLayout(
        state_root=state_root,
        trader_identity=config.trader_identity,
        concrete_contract_id=config.concrete_contract_id,
        config_identity=config.stable_identity,
    )


class _Harness:
    def __init__(self, state_root: Path, config: PaperRuntimeConfig) -> None:
        self.config = config
        self.layout = _layout(state_root, config)
        self.layout.ensure_initialized()
        self.order_journal = PaperOrderJournal(self.layout.order_journal_path)
        self.wake_journal = PaperWakeJournal(self.layout.wake_journal_path)
        self.mirror = PaperBrokerTruthMirror(broker_id=BROKER_ID)
        self.calendar = build_rehearsal_calendar()
        self.builder = LiveCausalContextBuilder(
            exchange=EXCHANGE, concrete_instrument=INSTRUMENT, product=PRODUCT, calendar=self.calendar
        )

    def assembly(self) -> object:
        broker = RehearsalFakeBroker(self.order_journal)
        return assemble_paper_runtime(
            PaperRuntimeAssemblyInputs(
                trader_identity=self.config.trader_identity,
                concrete_contract_id=self.config.concrete_contract_id,
                exchange=EXCHANGE,
                product=PRODUCT,
                actual_tqsdk_runtime_version=RUNTIME_VERSION,
                authority=self.config.authority,
                activation_profile=self.config.activation_profile,
                sessions=self.calendar,
                context_builder=self.builder,
                wake_journal=self.wake_journal,
                order_journal=self.order_journal,
                broker_mirror=self.mirror,
                broker=broker,
                trader=RehearsalFakeTrader(),
                risk_planner=RehearsalFakeRiskPlanner(),
                source=RehearsalLiveSource(()),
                symbol=INSTRUMENT,
            )
        )

    def close(self) -> None:
        try:
            self.order_journal.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            self.wake_journal.close()
        except Exception:  # noqa: BLE001
            pass


class PaperPreflightTests(unittest.TestCase):
    def test_real_external_profile_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _base_config(root)
            report = run_paper_preflight(config=config, layout=_layout(root, config), mode=EXTERNAL)
            self.assertFalse(report.ready)
            self.assertEqual(report.overall, "BLOCKED")
            names = {check.name for check in report.checks}
            self.assertIn("AUTHORITY_STATE", names)
            self.assertIn("ACTIVATION_PROFILE_COMPLETE", names)
            authority = next(check for check in report.checks if check.name == "AUTHORITY_STATE")
            self.assertIn("PAPER_CONNECT_AUTHORITY_UNBOUND", authority.detail)
            external_role = next(
                check for check in report.checks if check.name == "EXTERNAL_PAPER_ROLE_NOT_SILENTLY_ADOPTED"
            )
            self.assertEqual(external_role.status, "BLOCK")
            self.assertIn("EXTERNAL_PAPER_ROLE_NOT_ADOPTED", external_role.detail)

    def test_offline_rehearsal_profile_can_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = (
                _base_config(root)
                .bind_activation_profile(rehearsal_profile())
                .bind_authority(rehearsal_authority())
            )
            harness = _Harness(root, config)
            try:
                report = run_paper_preflight(
                    config=config,
                    layout=harness.layout,
                    activation_profile=config.activation_profile,
                    authority=config.authority,
                    assembly=harness.assembly(),
                    mode=OFFLINE_REHEARSAL,
                )
                self.assertTrue(report.ready)
                self.assertEqual(report.overall, "READY")
            finally:
                harness.close()

    def test_incomplete_result_dependent_activation_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            # bind an ACTIVE authority but keep the profile unbound
            config = _base_config(root).bind_authority(rehearsal_authority())
            report = run_paper_preflight(config=config, layout=_layout(root, config), mode=EXTERNAL)
            self.assertFalse(report.ready)
            profile_check = next(
                check for check in report.checks if check.name == "ACTIVATION_PROFILE_COMPLETE"
            )
            self.assertEqual(profile_check.status, "BLOCK")
            self.assertIn("ACTIVATION_PROFILE_UNBOUND", profile_check.detail)

    def test_preflight_leaks_no_secret(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _base_config(root)
            report = run_paper_preflight(config=config, layout=_layout(root, config), mode=EXTERNAL)
            text = "\n".join(report.public_lines())
            self.assertNotIn("DEEPSEEK_API_KEY", text)
            self.assertNotIn("password", text.lower())
            self.assertIn("PAPER_PREFLIGHT_OVERALL=BLOCKED", text)

    def test_report_identity_is_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _base_config(root)
            one = run_paper_preflight(config=config, layout=_layout(root, config), mode=EXTERNAL)
            two = run_paper_preflight(config=config, layout=_layout(root, config), mode=EXTERNAL)
            self.assertEqual(one.identity, two.identity)
            self.assertEqual(one.public_lines(), two.public_lines())

    def test_report_type_validation(self) -> None:
        with self.assertRaises(ValueError):
            PaperPreflightReport(mode="BAD", overall="READY", checks=())
        # a BLOCKED report requires at least one BLOCK check
        with self.assertRaises(ValueError):
            PaperPreflightReport(mode=EXTERNAL, overall="BLOCKED", checks=())
        # a READY report cannot contain a BLOCK check
        from src.paper_preflight import BLOCK, PaperPreflightCheck
        with self.assertRaises(ValueError):
            PaperPreflightReport(
                mode=EXTERNAL,
                overall="READY",
                checks=(PaperPreflightCheck(name="X", status=BLOCK, detail="d"),),
            )

    def test_unresolved_wake_dispatch_blocks_preflight(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = (
                _base_config(root)
                .bind_activation_profile(rehearsal_profile())
                .bind_authority(rehearsal_authority())
            )
            harness = _Harness(root, config)
            try:
                # insert an unresolved dispatch directly
                harness.wake_journal.observe(
                    wake_identity="wake-1",
                    trader_identity=TRADER_IDENTITY,
                    concrete_contract_id=CONTRACT,
                    bar_identity="bar-1",
                    bar_start=MORNING_UNTIL,
                    bar_end=MORNING_UNTIL.replace(minute=MORNING_UNTIL.minute + 5),
                    observed_at=MORNING_UNTIL.replace(minute=MORNING_UNTIL.minute + 5),
                )
                harness.wake_journal.mark_dispatch_started("wake-1", request_id="req-1", at=MORNING_UNTIL)
                report = run_paper_preflight(
                    config=config,
                    layout=harness.layout,
                    activation_profile=config.activation_profile,
                    authority=config.authority,
                    mode=OFFLINE_REHEARSAL,
                )
                self.assertFalse(report.ready)
                wake_check = next(
                    check for check in report.checks if check.name == "NO_UNRESOLVED_WAKE_DISPATCH"
                )
                self.assertEqual(wake_check.status, "BLOCK")
                self.assertIn("UNRESOLVED_TRADER_WAKE_DISPATCH", wake_check.detail)
            finally:
                harness.close()

    def test_journal_schema_and_order_state_checks(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _base_config(root)
            harness = _Harness(root, config)
            try:
                report = run_paper_preflight(config=config, layout=harness.layout, mode=EXTERNAL)
                names = {check.name for check in report.checks}
                self.assertIn("JOURNAL_SCHEMA_READABLE", names)
                self.assertIn("NO_UNRESOLVED_ORDER_STATE", names)
                self.assertIn("PERSISTENCE_ACCESSIBLE", names)
            finally:
                harness.close()


if __name__ == "__main__":
    unittest.main()
