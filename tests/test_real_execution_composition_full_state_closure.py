"""Adversarial closure tests for the REAL journal restart boundary."""

from __future__ import annotations

from contextlib import closing
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
import json
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from src.contract_semantics import PositionDirection
from src.fangzheng_ctp_candidate import FangzhengCtpBrokerAdapter
from src.fangzheng_ctp_fake import FakeCtpOperation, FakeCtpStep, ScriptedCtpTransport
from src.real_execution_composition import (
    REAL_JOURNAL_START_CHECKPOINT_SCHEMA_VERSION,
    RealExecutionComposition,
    _fingerprint,
)
from src.runtime_ledger import (
    RuntimeLedger,
    RuntimeLedgerRecordKind,
    ledger_pairs,
)
from tests.test_fangzheng_ctp_candidate import CONTRACT
from tests.test_fangzheng_ctp_fake import establish_ready
from tests.runtime_synthetic_fixture import make_accounting, make_contract_spec
from tests.test_real_execution_composition import (
    NOW,
    TRADING_DAY,
    _ready_query_steps,
    _trading_state,
)
from tests.test_real_execution_composition_orp004_closure import _runtime_state_with_order
from tests.test_real_execution_composition_restart_state import (
    _close_instruction,
    _close_profile,
    _create_carried_partial_close,
)


class JournalInitializationClosureTests(unittest.TestCase):
    def test_partial_unknown_empty_journal_structure_cannot_initialize(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "partial-structure.sqlite3"
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute(
                    "CREATE TABLE real_execution_unknown(value TEXT)"
                )

            composition = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-partial-structure",
            )

            self.assertIn("JOURNAL_STRUCTURE_UNPROVABLE", composition.active_blockers())
            self.assertIn(
                "HARD_EXECUTION_INCONSISTENCY", composition.active_blockers()
            )
            self.assertFalse(composition.new_risk_allowed)

    def test_nonempty_journal_missing_schema_baseline_and_checkpoint_fails_closed(
        self,
    ) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-schema-baseline.sqlite3"
            state = _runtime_state_with_order(fills=((Decimal("2"), Decimal("3500")),))
            transport = ScriptedCtpTransport(
                _ready_query_steps()
                + (
                    FakeCtpStep(
                        FakeCtpOperation.SUBMIT,
                        expected_project_order_id="close-order-1",
                    ),
                )
            )
            adapter = FangzhengCtpBrokerAdapter(transport, _close_profile())
            establish_ready(adapter)
            first = RealExecutionComposition(
                path=path,
                adapter=adapter,
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-missing-schema-baseline",
            )
            first.submit_order(_close_instruction(), submitted_at=NOW)

            position_key = (CONTRACT, PositionDirection.LONG)
            state._positions[position_key] = replace(
                state._positions[position_key], quantity=Decimal("3")
            )
            with closing(sqlite3.connect(path)) as connection, connection:
                generation_before = connection.execute(
                    "SELECT value FROM real_execution_meta "
                    "WHERE key='construction_generation'"
                ).fetchone()[0]
                connection.execute("DELETE FROM real_position_baseline")
                connection.execute("DELETE FROM real_journal_start_checkpoint")
                connection.execute(
                    "DELETE FROM real_execution_meta WHERE key='schema_version'"
                )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-missing-schema-baseline",
            )

            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)
            with closing(sqlite3.connect(path)) as connection:
                self.assertIsNone(connection.execute(
                    "SELECT value FROM real_execution_meta WHERE key='schema_version'"
                ).fetchone())
                self.assertEqual(
                    connection.execute(
                        "SELECT value FROM real_execution_meta "
                        "WHERE key='construction_generation'"
                    ).fetchone()[0],
                    generation_before,
                )

    def test_nonempty_journal_missing_scope_is_not_silently_repaired(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-scope.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-missing-scope"
            )
            with closing(sqlite3.connect(path)) as connection, connection:
                generation_before = connection.execute(
                    "SELECT value FROM real_execution_meta "
                    "WHERE key='construction_generation'"
                ).fetchone()[0]
                connection.execute(
                    "DELETE FROM real_execution_meta WHERE key='session_identity'"
                )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-missing-scope",
            )

            self.assertIn("JOURNAL_SCOPE_UNPROVABLE", reopened.active_blockers())
            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)
            with closing(sqlite3.connect(path)) as connection:
                self.assertIsNone(connection.execute(
                    "SELECT value FROM real_execution_meta WHERE key='session_identity'"
                ).fetchone())
                self.assertEqual(
                    connection.execute(
                        "SELECT value FROM real_execution_meta "
                        "WHERE key='construction_generation'"
                    ).fetchone()[0],
                    generation_before,
                )

    def test_nonempty_journal_missing_generation_is_not_silently_repaired(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-generation.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-missing-generation"
            )
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute(
                    "DELETE FROM real_execution_meta "
                    "WHERE key='construction_generation'"
                )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-missing-generation",
            )

            self.assertIn("JOURNAL_SCOPE_UNPROVABLE", reopened.active_blockers())
            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)
            with closing(sqlite3.connect(path)) as connection:
                self.assertIsNone(connection.execute(
                    "SELECT value FROM real_execution_meta "
                    "WHERE key='construction_generation'"
                ).fetchone())

    def test_missing_or_tampered_checkpoint_fails_closed(self) -> None:
        mutations = ("missing", "partial", "identity", "ledger_anchor")
        for mutation in mutations:
            with self.subTest(mutation=mutation), TemporaryDirectory() as tmp:
                path = Path(tmp) / f"checkpoint-{mutation}.sqlite3"
                session_identity = f"session-checkpoint-{mutation}"
                state = _create_carried_partial_close(
                    path, session_identity=session_identity
                )
                with closing(sqlite3.connect(path)) as connection, connection:
                    if mutation == "missing":
                        connection.execute(
                            "DELETE FROM real_journal_start_checkpoint"
                        )
                    elif mutation == "identity":
                        connection.execute(
                            "UPDATE real_journal_start_checkpoint "
                            "SET checkpoint_identity=?",
                            ("0" * 64,),
                        )
                    else:
                        raw = connection.execute(
                            "SELECT checkpoint_json "
                            "FROM real_journal_start_checkpoint"
                        ).fetchone()[0]
                        checkpoint = json.loads(raw)
                        if mutation == "partial":
                            checkpoint.pop("account")
                        else:
                            checkpoint["ledger_anchor"]["identity"] = "not-a-digest"
                        connection.execute(
                            "UPDATE real_journal_start_checkpoint "
                            "SET checkpoint_json=?,checkpoint_identity=?",
                            (
                                json.dumps(checkpoint, sort_keys=True),
                                _fingerprint({
                                    "schema_version": (
                                        REAL_JOURNAL_START_CHECKPOINT_SCHEMA_VERSION
                                    ),
                                    "checkpoint": checkpoint,
                                }),
                            ),
                        )

                reopened = RealExecutionComposition(
                    path=path,
                    adapter=FangzhengCtpBrokerAdapter(
                        ScriptedCtpTransport(()), _close_profile()
                    ),
                    trading_state=state,
                    expected_trading_day=TRADING_DAY,
                    session_identity=session_identity,
                )

                self.assertIn(
                    "HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers()
                )
                self.assertFalse(reopened.new_risk_allowed)


class EconomicCheckpointClosureTests(unittest.TestCase):
    def test_tampered_position_realized_pnl_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "position-realized-pnl.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-position-realized-pnl"
            )
            position_key = (CONTRACT, PositionDirection.LONG)
            exact = state._positions[position_key]
            state._positions[position_key] = replace(
                exact, realized_pnl=exact.realized_pnl + Decimal("1")
            )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-position-realized-pnl",
            )

            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)

    def test_neighboring_position_economic_mutations_fail_closed(self) -> None:
        mutations = {
            "reserved_margin": Decimal("1"),
            "unrealized_pnl": Decimal("1"),
            "last_mark_price": Decimal("1"),
        }
        for field, delta in mutations.items():
            with self.subTest(field=field), TemporaryDirectory() as tmp:
                path = Path(tmp) / f"position-{field}.sqlite3"
                state = _create_carried_partial_close(
                    path, session_identity=f"session-position-{field}"
                )
                position_key = (CONTRACT, PositionDirection.LONG)
                exact = state._positions[position_key]
                state._positions[position_key] = replace(
                    exact, **{field: getattr(exact, field) + delta}
                )

                reopened = RealExecutionComposition(
                    path=path,
                    adapter=FangzhengCtpBrokerAdapter(
                        ScriptedCtpTransport(()), _close_profile()
                    ),
                    trading_state=state,
                    expected_trading_day=TRADING_DAY,
                    session_identity=f"session-position-{field}",
                )

                self.assertIn(
                    "HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers()
                )

    def test_tampered_account_charged_costs_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "account-charged-costs.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-account-charged-costs"
            )
            state._account = replace(
                state.account,
                charged_costs=state.account.charged_costs + Decimal("1"),
            )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-account-charged-costs",
            )

            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)

    def test_economic_semantic_identity_drift_fails_closed(self) -> None:
        mutations = ("accounting", "contract_specification")
        for mutation in mutations:
            with self.subTest(mutation=mutation), TemporaryDirectory() as tmp:
                path = Path(tmp) / f"semantic-{mutation}.sqlite3"
                session_identity = f"session-semantic-{mutation}"
                state = _create_carried_partial_close(
                    path, session_identity=session_identity
                )
                if mutation == "accounting":
                    state._accounting = make_accounting(
                        additive_cost_per_fill=Decimal("6")
                    )
                else:
                    state._contract_specs[CONTRACT] = make_contract_spec(
                        instrument=CONTRACT, multiplier=Decimal("301")
                    )

                reopened = RealExecutionComposition(
                    path=path,
                    adapter=FangzhengCtpBrokerAdapter(
                        ScriptedCtpTransport(()), _close_profile()
                    ),
                    trading_state=state,
                    expected_trading_day=TRADING_DAY,
                    session_identity=session_identity,
                )

                self.assertIn(
                    "JOURNAL_START_CHECKPOINT_INVALID", reopened.active_blockers()
                )
                self.assertIn(
                    "HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers()
                )


class RuntimeLedgerClosureTests(unittest.TestCase):
    def test_populated_state_with_replaced_empty_ledger_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "replaced-ledger.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-replaced-ledger"
            )
            state._ledger = RuntimeLedger()

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-replaced-ledger",
            )

            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)

    def test_valid_anchored_chain_missing_composition_records_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-composition-records.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-missing-composition-records"
            )
            with closing(sqlite3.connect(path)) as connection:
                checkpoint = json.loads(connection.execute(
                    "SELECT checkpoint_json FROM real_journal_start_checkpoint"
                ).fetchone()[0])
            anchor = checkpoint["ledger_anchor"]
            divergent = RuntimeLedger()
            divergent.restore_anchor(
                sequence=anchor["sequence"], identity=anchor["identity"]
            )
            divergent.append(
                RuntimeLedgerRecordKind.SAFETY,
                "unrelated-valid-record",
                ledger_pairs(reason="unrelated valid history"),
                NOW + timedelta(seconds=30),
            )
            self.assertTrue(divergent.verify_chain())
            state._ledger = divergent

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-missing-composition-records",
            )

            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)

    def test_broken_runtime_ledger_chain_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken-ledger-chain.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-broken-ledger-chain"
            )
            state._ledger._records.pop()
            self.assertFalse(state.runtime_ledger_chain_valid())

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-broken-ledger-chain",
            )

            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())

    def test_unrelated_valid_ledger_record_can_coexist(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "unrelated-ledger-record.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-unrelated-ledger-record"
            )
            state._ledger.append(
                RuntimeLedgerRecordKind.SAFETY,
                "unrelated-valid-record",
                ledger_pairs(reason="unrelated valid history"),
                NOW + timedelta(seconds=30),
            )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-unrelated-ledger-record",
            )

            self.assertNotIn(
                "HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers()
            )
            self.assertFalse(reopened.new_risk_allowed)

    def test_duplicate_equivalent_composition_ledger_record_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate-composition-ledger-record.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-duplicate-composition-ledger-record"
            )
            duplicate = state.runtime_ledger_records()[-1]
            state._ledger.append(
                duplicate.record_kind,
                duplicate.reference_id,
                duplicate.payload,
                duplicate.recorded_at,
            )
            self.assertTrue(state.runtime_ledger_chain_valid())

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-duplicate-composition-ledger-record",
            )

            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)


class FreshRehydrationClosureTests(unittest.TestCase):
    def test_fresh_state_rebuilds_full_carried_economics_and_stays_risk_blocked(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "fresh-full-rehydration.sqlite3"
            exact_state = _create_carried_partial_close(
                path, session_identity="session-fresh-full-rehydration"
            )
            expected_account = exact_state.account
            expected_positions = exact_state.positions
            fresh_state = _trading_state()

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=fresh_state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-fresh-full-rehydration",
            )

            self.assertEqual(fresh_state.account, expected_account)
            self.assertEqual(fresh_state.positions, expected_positions)
            self.assertTrue(fresh_state.runtime_ledger_chain_valid())
            self.assertNotIn(
                "HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers()
            )
            self.assertFalse(reopened.new_risk_allowed)


if __name__ == "__main__":
    unittest.main()
