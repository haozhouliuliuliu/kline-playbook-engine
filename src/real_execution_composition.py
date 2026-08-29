"""Durable offline REAL execution composition and recovery seam.

This is the single project-owned seam between the injected Fangzheng/CTP
candidate adapter and the existing ``TradingState`` / REAL reconciliation
contracts.  It performs no connection setup and owns no broker credentials.
Its SQLite journal persists complete project order semantics before transport,
keeps project and broker identities separate, enriches sparse callbacks, and
replays durable facts into ``TradingState`` after restart.
"""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerOrderInstruction,
    BrokerPositionSnapshot,
    canonical_decimal,
)
from src.contract_semantics import OrderAction, PositionDirection
from src.fangzheng_ctp_candidate import (
    BrokerTruthUnknownError,
    CtpOrderRecord,
    CtpTradeRecord,
    FangzhengCtpBrokerAdapter,
)
from src.real_reconciliation import (
    QueryCompleteness,
    RealBrokerOrder,
    RealBrokerQueryRound,
    RealLocalExecutionState,
    RealLocalOrder,
)
from src.real_runtime_recovery import RealRuntimeRecoveryReport, recover_real_runtime
from src.real_safety_state import (
    ExternalMutationStatus,
    RealSafetyController,
)
from src.runtime_events import (
    BrokerConnectionState,
    BrokerEvent,
    BrokerEventType,
    event_pairs,
)
from src.trading_state import EventApplicationResult, OrderStatus, TradingState


REAL_EXECUTION_COMPOSITION_SCHEMA_VERSION = "KPE_REAL_EXECUTION_COMPOSITION_V0_2"
LEGACY_REAL_EXECUTION_COMPOSITION_SCHEMA_VERSION = "KPE_REAL_EXECUTION_COMPOSITION_V0_1"
REAL_EXECUTION_LINEAGE_SCHEMA_VERSION = "KPE_REAL_EXECUTION_LINEAGE_V0_1"
REAL_POSITION_BASELINE_SCHEMA_VERSION = "KPE_REAL_POSITION_BASELINE_V0_1"


class RealOrderLifecycle(str, Enum):
    PENDING_SUBMIT = "PENDING_SUBMIT"
    UNKNOWN = "UNKNOWN"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    INCONSISTENT = "INCONSISTENT"


class RealExecutionInconsistencyError(RuntimeError):
    """Durable identity or economic-fact conflict; never auto-repaired."""


@dataclass(frozen=True)
class DurableRealOrder:
    project_order_id: str
    client_request_id: str
    instruction_identity: str
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    requested_quantity: Decimal
    trading_day: str
    session_identity: str
    broker_order_id: str | None
    lifecycle: RealOrderLifecycle
    filled_quantity: Decimal
    average_fill_price: Decimal | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class RealExecutionRecoveryResult:
    recovery: RealRuntimeRecoveryReport
    broker_truth_complete: bool
    new_risk_allowed: bool
    blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.broker_truth_complete and not self.recovery.broker_truth_complete:
            raise ValueError("composition cannot exceed REAL recovery completeness")
        if self.blockers != tuple(sorted(set(self.blockers))):
            raise ValueError("composition blockers must be sorted and unique")
        if self.new_risk_allowed and (not self.broker_truth_complete or self.blockers):
            raise ValueError("new risk requires complete unblocked broker truth")


@dataclass(frozen=True)
class CurrentReconciliationProof:
    """Process-local proof that one exact composition observed current broker truth."""

    composition_instance_id: str
    session_identity: str
    trading_day: str
    round_id: str
    requested_at: datetime
    observed_at: datetime

    def __post_init__(self) -> None:
        _required_text(self.composition_instance_id, "composition instance id")
        _required_text(self.session_identity, "session identity")
        _validate_trading_day(self.trading_day)
        _required_text(self.round_id, "query round id")
        _aware(self.requested_at, "query request timestamp")
        _aware(self.observed_at, "query observation timestamp")
        if self.observed_at < self.requested_at:
            raise ValueError("reconciliation proof cannot predate its query request")

    @property
    def identity_id(self) -> str:
        return _fingerprint({
            "composition_instance_id": self.composition_instance_id,
            "session_identity": self.session_identity,
            "trading_day": self.trading_day,
            "round_id": self.round_id,
            "requested_at": self.requested_at.isoformat(),
            "observed_at": self.observed_at.isoformat(),
        })


def _required_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _aware(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _validate_trading_day(value: str) -> str:
    if not isinstance(value, str) or len(value) != 8 or not value.isdigit():
        raise ValueError("trading day must use YYYYMMDD")
    return value


def _fingerprint(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


class RealExecutionComposition:
    """Small interface owning durable CTP composition and restart recovery."""

    _STREAM_PREFIX = "real-execution-composition:"

    def __init__(
        self,
        *,
        path: str | Path,
        adapter: FangzhengCtpBrokerAdapter,
        trading_state: TradingState,
        expected_trading_day: str,
        session_identity: str,
        safety_controller: RealSafetyController | None = None,
    ) -> None:
        if not isinstance(adapter, FangzhengCtpBrokerAdapter):
            raise TypeError("REAL execution composition requires FangzhengCtpBrokerAdapter")
        if not isinstance(trading_state, TradingState):
            raise TypeError("REAL execution composition requires TradingState")
        if safety_controller is not None and not isinstance(safety_controller, RealSafetyController):
            raise TypeError("safety controller must be RealSafetyController or None")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.adapter = adapter
        self.trading_state = trading_state
        self.expected_trading_day = _validate_trading_day(expected_trading_day)
        self.session_identity = _required_text(session_identity, "session identity")
        self.safety_controller = safety_controller
        self._stream_id = self._STREAM_PREFIX + self.session_identity
        self._reconciliation_proof: CurrentReconciliationProof | None = None
        self._readiness_state = "CURRENT_RECONCILIATION_REQUIRED"
        self._composition_instance_id = self._initialize()
        self._position_baseline = self._ensure_position_baseline()
        self._repair_or_block_legacy_fill_aggregates()
        existing_sequences = tuple(
            event.sequence
            for event in self.trading_state.applied_events()
            if event.stream_id == self._stream_id
        )
        self._sequence = 0 if not existing_sequences else max(existing_sequences) + 1
        self._restore_persistent_safety()
        self._rehydrate_trading_state()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> str:
        with closing(self._connect()) as connection, connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS real_execution_meta(
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS real_execution_orders(
                    project_order_id TEXT PRIMARY KEY,
                    client_request_id TEXT NOT NULL UNIQUE,
                    instruction_identity TEXT NOT NULL,
                    concrete_contract_id TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    action TEXT NOT NULL,
                    requested_quantity TEXT NOT NULL,
                    trading_day TEXT NOT NULL,
                    session_identity TEXT NOT NULL,
                    broker_order_id TEXT UNIQUE,
                    lifecycle TEXT NOT NULL,
                    filled_quantity TEXT NOT NULL,
                    average_fill_price TEXT,
                    created_at TEXT NOT NULL,
                    acknowledgement_at TEXT,
                    terminal_at TEXT,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS real_execution_facts(
                    fact_key TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL,
                    fact_type TEXT NOT NULL,
                    project_order_id TEXT NOT NULL,
                    broker_order_id TEXT,
                    quantity TEXT,
                    price TEXT,
                    occurred_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS real_execution_blockers(
                    code TEXT PRIMARY KEY,
                    detail TEXT NOT NULL,
                    latched_at TEXT NOT NULL,
                    resolved_at TEXT
                );
                CREATE TABLE IF NOT EXISTS real_position_baseline(
                    baseline_key TEXT PRIMARY KEY CHECK(baseline_key='journal_start'),
                    schema_version TEXT NOT NULL,
                    expected_trading_day TEXT NOT NULL,
                    session_identity TEXT NOT NULL,
                    positions_json TEXT NOT NULL,
                    baseline_identity TEXT NOT NULL
                );
                """
            )
            schema_row = connection.execute(
                "SELECT value FROM real_execution_meta WHERE key='schema_version'"
            ).fetchone()
            order_count = connection.execute(
                "SELECT COUNT(*) FROM real_execution_orders"
            ).fetchone()[0]
            fact_count = connection.execute(
                "SELECT COUNT(*) FROM real_execution_facts"
            ).fetchone()[0]
            baseline_initialization_allowed = False
            if schema_row is None:
                connection.execute(
                    "INSERT INTO real_execution_meta(key,value) VALUES('schema_version',?)",
                    (REAL_EXECUTION_COMPOSITION_SCHEMA_VERSION,),
                )
                baseline_initialization_allowed = True
            elif schema_row[0] == LEGACY_REAL_EXECUTION_COMPOSITION_SCHEMA_VERSION:
                if order_count == 0 and fact_count == 0:
                    connection.execute(
                        "UPDATE real_execution_meta SET value=? WHERE key='schema_version'",
                        (REAL_EXECUTION_COMPOSITION_SCHEMA_VERSION,),
                    )
                    baseline_initialization_allowed = True
            elif schema_row[0] != REAL_EXECUTION_COMPOSITION_SCHEMA_VERSION:
                raise ValueError("REAL_EXECUTION_COMPOSITION_BINDING_MISMATCH:schema_version")
            expected_meta = {
                "expected_trading_day": self.expected_trading_day,
                "session_identity": self.session_identity,
                "broker_adapter_identity": self.adapter.broker_id,
            }
            for key, value in expected_meta.items():
                recorded = connection.execute(
                    "SELECT value FROM real_execution_meta WHERE key=?", (key,)
                ).fetchone()
                if recorded is not None and recorded[0] != value:
                    raise ValueError(f"REAL_EXECUTION_COMPOSITION_BINDING_MISMATCH:{key}")
                connection.execute(
                    "INSERT OR IGNORE INTO real_execution_meta(key,value) VALUES(?,?)",
                    (key, value),
                )
            baseline_row = connection.execute(
                "SELECT baseline_key FROM real_position_baseline WHERE baseline_key='journal_start'"
            ).fetchone()
            if baseline_row is None and baseline_initialization_allowed:
                positions = self._baseline_position_document(self.trading_state.positions)
                connection.execute(
                    """INSERT INTO real_position_baseline(
                           baseline_key,schema_version,expected_trading_day,
                           session_identity,positions_json,baseline_identity
                       ) VALUES('journal_start',?,?,?,?,?)""",
                    (
                        REAL_POSITION_BASELINE_SCHEMA_VERSION,
                        self.expected_trading_day,
                        self.session_identity,
                        json.dumps(
                            positions,
                            ensure_ascii=False,
                            sort_keys=True,
                            separators=(",", ":"),
                        ),
                        self._position_baseline_identity(positions),
                    ),
                )
            generation_row = connection.execute(
                "SELECT value FROM real_execution_meta WHERE key='construction_generation'"
            ).fetchone()
            try:
                generation = 1 if generation_row is None else int(generation_row[0]) + 1
            except (TypeError, ValueError) as error:
                raise ValueError(
                    "REAL_EXECUTION_COMPOSITION_BINDING_MISMATCH:construction_generation"
                ) from error
            if generation <= 0:
                raise ValueError(
                    "REAL_EXECUTION_COMPOSITION_BINDING_MISMATCH:construction_generation"
                )
            connection.execute(
                """INSERT INTO real_execution_meta(key,value)
                   VALUES('construction_generation',?)
                   ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
                (str(generation),),
            )
        return _fingerprint({
            "schema_version": REAL_EXECUTION_COMPOSITION_SCHEMA_VERSION,
            "expected_trading_day": self.expected_trading_day,
            "session_identity": self.session_identity,
            "broker_adapter_identity": self.adapter.broker_id,
            "construction_generation": generation,
        })

    def _ensure_position_baseline(
        self,
    ) -> dict[tuple[str, PositionDirection], tuple[Decimal, Decimal]] | None:
        with closing(self._connect()) as connection, connection:
            row = connection.execute(
                "SELECT * FROM real_position_baseline WHERE baseline_key='journal_start'"
            ).fetchone()
            schema_row = connection.execute(
                "SELECT value FROM real_execution_meta WHERE key='schema_version'"
            ).fetchone()

        if row is None:
            self._latch_position_baseline_failure(
                "POSITION_BASELINE_MISSING",
                "nonempty REAL journal has no explicit position baseline",
            )
            return None
        try:
            positions = json.loads(row["positions_json"])
            projection = self._position_projection_from_document(positions)
            identity = self._position_baseline_identity(positions)
            valid = (
                schema_row is not None
                and schema_row[0] == REAL_EXECUTION_COMPOSITION_SCHEMA_VERSION
                and row["schema_version"] == REAL_POSITION_BASELINE_SCHEMA_VERSION
                and row["expected_trading_day"] == self.expected_trading_day
                and row["session_identity"] == self.session_identity
                and row["baseline_identity"] == identity
            )
        except (json.JSONDecodeError, TypeError, ValueError, KeyError, InvalidOperation):
            valid = False
            projection = None
        if not valid:
            self._latch_position_baseline_failure(
                "POSITION_BASELINE_INVALID",
                "position baseline content, identity, or journal scope is invalid",
            )
            return None
        return projection

    @staticmethod
    def _baseline_position_document(positions) -> list[dict[str, str]]:
        return [
            {
                "average_open_price": canonical_decimal(position.average_open_price),
                "concrete_contract_id": position.concrete_contract_id,
                "direction": position.direction.value,
                "quantity": canonical_decimal(position.quantity),
            }
            for position in sorted(
                positions,
                key=lambda item: (item.concrete_contract_id, item.direction.value),
            )
        ]

    def _position_baseline_identity(self, positions: object) -> str:
        return _fingerprint({
            "schema_version": REAL_POSITION_BASELINE_SCHEMA_VERSION,
            "expected_trading_day": self.expected_trading_day,
            "session_identity": self.session_identity,
            "positions": positions,
        })

    @staticmethod
    def _position_projection_from_document(
        positions: object,
    ) -> dict[tuple[str, PositionDirection], tuple[Decimal, Decimal]]:
        if not isinstance(positions, list):
            raise ValueError("position baseline must be a list")
        projection: dict[tuple[str, PositionDirection], tuple[Decimal, Decimal]] = {}
        expected_keys = {
            "average_open_price",
            "concrete_contract_id",
            "direction",
            "quantity",
        }
        for raw in positions:
            if not isinstance(raw, dict) or set(raw) != expected_keys:
                raise ValueError("position baseline entry has invalid fields")
            contract = _required_text(raw["concrete_contract_id"], "baseline contract")
            direction = PositionDirection(raw["direction"])
            quantity = Decimal(_required_text(raw["quantity"], "baseline quantity"))
            average = Decimal(
                _required_text(raw["average_open_price"], "baseline average price")
            )
            if (
                not quantity.is_finite()
                or quantity <= 0
                or not average.is_finite()
                or average <= 0
            ):
                raise ValueError("position baseline values must be positive finite Decimals")
            key = (contract, direction)
            if key in projection:
                raise ValueError("position baseline rejects duplicate position identities")
            projection[key] = (quantity, average)
        return projection

    def _latch_position_baseline_failure(self, code: str, detail: str) -> None:
        occurred_at = datetime.now().astimezone()
        self._latch_blocker(code, detail, occurred_at)
        self._latch_inconsistency("position-baseline", detail, occurred_at)

    @property
    def composition_instance_id(self) -> str:
        return self._composition_instance_id

    @property
    def reconciliation_proof(self) -> CurrentReconciliationProof | None:
        return self._reconciliation_proof

    @property
    def reconciliation_readiness_state(self) -> str:
        return self._readiness_state

    @property
    def unresolved_order_count(self) -> int:
        unresolved = {
            RealOrderLifecycle.PENDING_SUBMIT.value,
            RealOrderLifecycle.UNKNOWN.value,
            RealOrderLifecycle.INCONSISTENT.value,
        }
        with closing(self._connect()) as connection:
            placeholders = ",".join("?" for _ in unresolved)
            row = connection.execute(
                f"SELECT COUNT(*) FROM real_execution_orders WHERE lifecycle IN ({placeholders})",
                tuple(sorted(unresolved)),
            ).fetchone()
        return int(row[0])

    @property
    def new_risk_allowed(self) -> bool:
        proof = self._reconciliation_proof
        if proof is None:
            return False
        if (
            proof.composition_instance_id != self._composition_instance_id
            or proof.session_identity != self.session_identity
            or proof.trading_day != self.expected_trading_day
            or not self.adapter.ready
            or self.adapter.trading_day != self.expected_trading_day
        ):
            return False
        if self.unresolved_order_count != 0 or self.active_blockers():
            return False
        if self.safety_controller is not None and not self.safety_controller.state.allows_risk_increase():
            return False
        return True

    def active_blockers(self) -> tuple[str, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT code FROM real_execution_blockers WHERE resolved_at IS NULL ORDER BY code"
            ).fetchall()
        return tuple(str(row[0]) for row in rows)

    def orders(self) -> tuple[DurableRealOrder, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM real_execution_orders ORDER BY project_order_id"
            ).fetchall()
        return tuple(self._row_to_order(row) for row in rows)

    def order_for(self, project_order_id: str) -> DurableRealOrder | None:
        _required_text(project_order_id, "project order id")
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM real_execution_orders WHERE project_order_id=?",
                (project_order_id,),
            ).fetchone()
        return None if row is None else self._row_to_order(row)

    @staticmethod
    def _row_to_order(row: sqlite3.Row) -> DurableRealOrder:
        return DurableRealOrder(
            project_order_id=row["project_order_id"],
            client_request_id=row["client_request_id"],
            instruction_identity=row["instruction_identity"],
            concrete_contract_id=row["concrete_contract_id"],
            direction=PositionDirection(row["direction"]),
            action=OrderAction(row["action"]),
            requested_quantity=Decimal(row["requested_quantity"]),
            trading_day=row["trading_day"],
            session_identity=row["session_identity"],
            broker_order_id=row["broker_order_id"],
            lifecycle=RealOrderLifecycle(row["lifecycle"]),
            filled_quantity=Decimal(row["filled_quantity"]),
            average_fill_price=(
                None if row["average_fill_price"] is None else Decimal(row["average_fill_price"])
            ),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def submit_order(
        self, instruction: BrokerOrderInstruction, *, submitted_at: datetime
    ) -> DurableRealOrder:
        if not isinstance(instruction, BrokerOrderInstruction):
            raise TypeError("REAL composition submit requires BrokerOrderInstruction")
        _aware(submitted_at, "submit timestamp")
        self._invalidate_reconciliation_proof("SUBMIT_ATTEMPT")
        if not self.adapter.ready:
            raise BrokerTruthUnknownError("CTP_BROKER_TRUTH_NOT_READY")
        project_order_id = instruction.client_order_id or instruction.client_request_id
        existing = self.order_for(project_order_id)
        if existing is not None:
            if existing.instruction_identity != instruction.identity_id:
                self._latch_inconsistency(
                    project_order_id,
                    "PROJECT_ORDER_ID_REUSED_WITH_DIFFERENT_INSTRUCTION",
                    submitted_at,
                )
                raise RealExecutionInconsistencyError(
                    "PROJECT_ORDER_ID_REUSED_WITH_DIFFERENT_INSTRUCTION"
                )
            return existing

        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                INSERT INTO real_execution_orders(
                    project_order_id,client_request_id,instruction_identity,
                    concrete_contract_id,direction,action,requested_quantity,
                    trading_day,session_identity,broker_order_id,lifecycle,
                    filled_quantity,average_fill_price,created_at,
                    acknowledgement_at,terminal_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?,?,NULL,?,?,NULL,?,NULL,NULL,?)
                """,
                (
                    project_order_id,
                    instruction.client_request_id,
                    instruction.identity_id,
                    instruction.concrete_contract_id,
                    instruction.direction.value,
                    instruction.action.value,
                    canonical_decimal(instruction.quantity),
                    self.expected_trading_day,
                    self.session_identity,
                    RealOrderLifecycle.UNKNOWN.value,
                    "0",
                    submitted_at.isoformat(),
                    submitted_at.isoformat(),
                ),
            )
        durable_order = self.order_for(project_order_id)
        if durable_order is None:
            raise RuntimeError("durable REAL order disappeared before transport submit")
        self._apply_submit_event(durable_order, submitted_at, acknowledged=False)
        # The durable UNKNOWN state exists before crossing the transport seam.
        # A return without an acknowledgement still remains UNKNOWN.
        self.adapter.submit_order(instruction)
        durable_order = self.order_for(project_order_id)
        if durable_order is None:
            raise RuntimeError("durable REAL order disappeared after transport submit")
        return durable_order

    def consume_adapter_events(self) -> tuple[EventApplicationResult, ...]:
        try:
            events = self.adapter.pump_callbacks()
        except Exception as error:
            self._mark_all_unresolved_unknown(
                "CTP_CALLBACK_OR_SESSION_INCONSISTENCY:" + type(error).__name__
            )
            if self.safety_controller is not None:
                self.safety_controller.set_unknown(
                    "CTP callback/session inconsistency", datetime.now().astimezone()
                )
            raise
        results: list[EventApplicationResult] = []
        for event in events:
            result = self._consume_event(event)
            if result is not None:
                results.append(result)
        return tuple(results)

    def _consume_event(self, event: BrokerEvent) -> EventApplicationResult | None:
        payload = dict(event.payload)
        if event.event_type is BrokerEventType.CONNECTION_STATE:
            self._invalidate_reconciliation_proof("CONNECTION_STATE_CHANGED")
            raw_state = payload.get("state", "UNKNOWN")
            if raw_state in {"DISCONNECTED", "RECONNECTING"}:
                connection_state = raw_state
                self._mark_all_unresolved_unknown("CTP_CONNECTION_TRUTH_UNKNOWN")
            elif raw_state in {"READY_FOR_RECONCILIATION", "CONNECTED"}:
                connection_state = BrokerConnectionState.CONNECTED.value
            else:
                connection_state = BrokerConnectionState.RECONNECTING.value
                self._mark_all_unresolved_unknown("CTP_CONNECTION_TRUTH_UNKNOWN")
            translated = self._event(
                event_id="real:" + event.event_id,
                event_type=BrokerEventType.CONNECTION_STATE,
                occurred_at=event.occurred_at,
                payload=event_pairs(connection_state=connection_state),
            )
            return self._apply(translated)
        if event.order_id is None:
            return None
        order = self.order_for(event.order_id)
        if order is None or event.client_request_id != order.client_request_id:
            self._latch_external_mutation(
                "EXTERNAL_OR_UNMAPPED_CALLBACK:" + event.order_id, event.occurred_at
            )
            return None
        if event.event_type is BrokerEventType.ORDER_SUBMITTED:
            return self._acknowledge(
                order,
                _required_text(payload.get("broker_order_id"), "broker order id"),
                event.occurred_at,
                fact_key="ack:" + _required_text(payload.get("broker_order_id"), "broker order id"),
            )
        if event.event_type is BrokerEventType.ORDER_FILLED:
            return self._record_fill(
                order=order,
                broker_order_id=_required_text(payload.get("broker_order_id"), "broker order id"),
                broker_trade_id=_required_text(payload.get("broker_trade_id"), "broker trade id"),
                quantity=Decimal(_required_text(payload.get("quantity"), "fill quantity")),
                price=Decimal(_required_text(payload.get("price"), "fill price")),
                occurred_at=event.occurred_at,
            )
        if event.event_type is BrokerEventType.ORDER_CANCELLED:
            return self._terminal(order, RealOrderLifecycle.CANCELLED, event.occurred_at)
        if event.event_type is BrokerEventType.ORDER_REJECTED:
            return self._terminal(order, RealOrderLifecycle.REJECTED, event.occurred_at)
        if event.event_type is BrokerEventType.ORDER_AMBIGUOUS:
            self._invalidate_reconciliation_proof("ORDER_AMBIGUOUS")
            self._set_order_lifecycle(order.project_order_id, RealOrderLifecycle.UNKNOWN, event.occurred_at)
            ambiguous = self._event(
                event_id="real:" + event.event_id,
                event_type=BrokerEventType.ORDER_AMBIGUOUS,
                occurred_at=event.occurred_at,
                order=order,
                payload=event_pairs(reason=payload.get("reason", "CTP_ORDER_AMBIGUOUS")),
            )
            return self._apply(ambiguous)
        return None

    def reconcile_adapter_truth(
        self,
        *,
        round_id: str,
        requested_at: datetime,
        observed_at: datetime,
        expected_account: BrokerAccountSnapshot,
        expected_positions: tuple[BrokerPositionSnapshot, ...],
        confirm_external_resolution: bool = False,
    ) -> RealExecutionRecoveryResult:
        _required_text(round_id, "query round id")
        _aware(requested_at, "query request timestamp")
        _aware(observed_at, "query observation timestamp")
        if not isinstance(expected_account, BrokerAccountSnapshot):
            raise TypeError("expected account must be BrokerAccountSnapshot")
        if not isinstance(expected_positions, tuple) or any(
            not isinstance(item, BrokerPositionSnapshot) for item in expected_positions
        ):
            raise TypeError("expected positions must be BrokerPositionSnapshot values")

        self._invalidate_reconciliation_proof("RECONCILIATION_IN_PROGRESS")

        account_status, account = self._fetch_account()
        position_status, positions = self._fetch_positions()
        order_status, raw_orders = self._fetch_orders()
        trade_status, trades = self._fetch_trades()
        actual_day = self.adapter.trading_day
        day_matches = actual_day == self.expected_trading_day
        if not day_matches:
            account_status = position_status = order_status = trade_status = QueryCompleteness.STALE
        broker_orders = tuple(self._to_real_broker_order(item) for item in raw_orders)
        query = RealBrokerQueryRound(
            round_id=round_id,
            trading_day=self.expected_trading_day if actual_day is None else actual_day,
            requested_at=requested_at,
            observed_at=observed_at,
            account_status=account_status,
            position_status=position_status,
            order_status=order_status,
            account=account,
            positions=positions,
            orders=broker_orders,
        )
        local_state = RealLocalExecutionState(
            trading_day=self.expected_trading_day,
            expected_account=expected_account,
            expected_positions=expected_positions,
            project_orders=tuple(
                RealLocalOrder(
                    project_order_id=item.project_order_id,
                    client_request_id=item.client_request_id,
                    broker_order_id=item.broker_order_id,
                    concrete_contract_id=item.concrete_contract_id,
                    direction=item.direction,
                    action=item.action,
                    requested_quantity=item.requested_quantity,
                    locally_applied_filled_quantity=item.filled_quantity,
                )
                for item in self.orders()
            ),
        )
        recovery = recover_real_runtime(
            local_state, query, expected_trading_day=self.expected_trading_day
        )
        blockers = list(recovery.blockers)
        if trade_status is not QueryCompleteness.COMPLETE:
            blockers.append("TRADE_QUERY_" + trade_status.value)

        if not recovery.broker_truth_complete or trade_status is not QueryCompleteness.COMPLETE:
            self._mark_all_unresolved_unknown("INCOMPLETE_REAL_BROKER_QUERY")
        else:
            for mutation in recovery.reconciliation.external_mutations:
                self._latch_external_mutation(
                    f"{mutation.kind.value}:{mutation.subject_id}", observed_at
                )
            for resolution in recovery.reconciliation.order_resolutions:
                if resolution.broker_order is None or resolution.status == "UNKNOWN":
                    continue
                order = self.order_for(resolution.project_order_id)
                if order is None:
                    continue
                broker = resolution.broker_order
                self._acknowledge(
                    order,
                    broker.broker_order_id,
                    broker.snapshot_at,
                    fact_key=f"query-ack:{round_id}:{broker.broker_order_id}",
                )
                for trade in sorted(
                    (
                        item
                        for item in trades
                        if item.broker_order_id == broker.broker_order_id
                    ),
                    key=lambda item: (item.occurred_at, item.broker_trade_id),
                ):
                    current = self.order_for(order.project_order_id)
                    self._record_fill(
                        order=current,
                        broker_order_id=trade.broker_order_id,
                        broker_trade_id=trade.broker_trade_id,
                        quantity=trade.quantity,
                        price=trade.price,
                        occurred_at=trade.occurred_at,
                    )
                current = self.order_for(order.project_order_id)
                if current.filled_quantity != broker.filled_quantity:
                    blockers.append("BROKER_FILL_FACTS_INCOMPLETE:" + order.project_order_id)
                    self._latch_inconsistency(
                        order.project_order_id,
                        "BROKER_FILL_FACTS_INCOMPLETE",
                        observed_at,
                    )
                elif broker.status == "CANCELLED":
                    self._terminal(current, RealOrderLifecycle.CANCELLED, broker.snapshot_at)
                elif broker.status == "REJECTED":
                    self._terminal(current, RealOrderLifecycle.REJECTED, broker.snapshot_at)
            if recovery.reconciliation.external_mutations:
                blockers.append("EXTERNAL_MUTATION_UNRESOLVED")
            elif confirm_external_resolution:
                self._confirm_external_resolution(observed_at)
            if not any(
                item.startswith("BROKER_FILL_FACTS_INCOMPLETE") for item in blockers
            ):
                self._resolve_blocker("BROKER_TRUTH_UNKNOWN", observed_at)

        blockers.extend(self.active_blockers())
        if self.unresolved_order_count:
            blockers.append("REAL_ORDER_TRUTH_UNRESOLVED")
        sorted_blockers = tuple(sorted(set(blockers)))
        composition_truth_complete = (
            recovery.broker_truth_complete
            and trade_status is QueryCompleteness.COMPLETE
            and day_matches
            and self.adapter.ready
        )
        if (
            composition_truth_complete
            and not sorted_blockers
            and self.unresolved_order_count == 0
        ):
            self._establish_reconciliation_proof(
                round_id=round_id,
                requested_at=requested_at,
                observed_at=observed_at,
            )
        return RealExecutionRecoveryResult(
            recovery=recovery,
            broker_truth_complete=composition_truth_complete,
            new_risk_allowed=(
                composition_truth_complete
                and not sorted_blockers
                and self.new_risk_allowed
            ),
            blockers=sorted_blockers,
        )

    def _fetch_account(self) -> tuple[QueryCompleteness, BrokerAccountSnapshot | None]:
        try:
            return QueryCompleteness.COMPLETE, self.adapter.fetch_account_snapshot()
        except BrokerTruthUnknownError:
            return QueryCompleteness.UNKNOWN, None

    def _fetch_positions(self) -> tuple[QueryCompleteness, tuple[BrokerPositionSnapshot, ...]]:
        try:
            return QueryCompleteness.COMPLETE, self.adapter.fetch_position_snapshot()
        except BrokerTruthUnknownError:
            return QueryCompleteness.UNKNOWN, ()

    def _fetch_orders(self) -> tuple[QueryCompleteness, tuple[CtpOrderRecord, ...]]:
        try:
            return QueryCompleteness.COMPLETE, self.adapter.fetch_ctp_order_snapshot()
        except BrokerTruthUnknownError:
            return QueryCompleteness.UNKNOWN, ()

    def _fetch_trades(self) -> tuple[QueryCompleteness, tuple[CtpTradeRecord, ...]]:
        try:
            return QueryCompleteness.COMPLETE, self.adapter.fetch_trade_snapshot()
        except BrokerTruthUnknownError:
            return QueryCompleteness.UNKNOWN, ()

    def _resolve_project_order_id(self, record: CtpOrderRecord) -> str | None:
        candidates = [
            item
            for item in self.orders()
            if (
                item.project_order_id == record.project_order_id
                or item.client_request_id == record.client_request_id
                or item.broker_order_id == record.broker_order_id
            )
        ]
        if len(candidates) != 1:
            return None
        candidate = candidates[0]
        if record.project_order_id not in (None, candidate.project_order_id):
            return None
        if candidate.client_request_id != record.client_request_id:
            return None
        if candidate.broker_order_id not in (None, record.broker_order_id):
            return None
        return candidate.project_order_id

    def _to_real_broker_order(self, record: CtpOrderRecord) -> RealBrokerOrder:
        return RealBrokerOrder(
            broker_order_id=record.broker_order_id,
            project_order_id=self._resolve_project_order_id(record),
            client_request_id=record.client_request_id,
            concrete_contract_id=record.concrete_contract_id,
            direction=record.direction,
            action=record.action,
            status=record.status,
            requested_quantity=record.requested_quantity,
            filled_quantity=record.filled_quantity,
            snapshot_at=record.snapshot_at,
        )

    def _acknowledge(
        self,
        order: DurableRealOrder,
        broker_order_id: str,
        occurred_at: datetime,
        *,
        fact_key: str,
    ) -> EventApplicationResult | None:
        _aware(occurred_at, "acknowledgement timestamp")
        self._invalidate_reconciliation_proof("ORDER_ACKNOWLEDGED")
        self._require_broker_mapping_available(
            order.project_order_id, broker_order_id, occurred_at
        )
        fingerprint = _fingerprint({
            "project_order_id": order.project_order_id,
            "client_request_id": order.client_request_id,
            "broker_order_id": broker_order_id,
        })
        if not self._record_fact(
            fact_key, fingerprint, "ACK", order.project_order_id,
            broker_order_id, None, None, occurred_at,
        ):
            return None
        if order.broker_order_id not in (None, broker_order_id):
            self._latch_inconsistency(order.project_order_id, "BROKER_ORDER_ID_CONFLICT", occurred_at)
            raise RealExecutionInconsistencyError("BROKER_ORDER_ID_CONFLICT")
        with closing(self._connect()) as connection:
            acknowledgement = connection.execute(
                "SELECT acknowledgement_at FROM real_execution_orders WHERE project_order_id=?",
                (order.project_order_id,),
            ).fetchone()
        already_acknowledged = acknowledgement is not None and acknowledgement[0] is not None
        lifecycle = order.lifecycle
        if lifecycle in {RealOrderLifecycle.UNKNOWN, RealOrderLifecycle.PENDING_SUBMIT}:
            lifecycle = RealOrderLifecycle.OPEN
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """UPDATE real_execution_orders
                   SET broker_order_id=?, lifecycle=?, acknowledgement_at=?, updated_at=?
                   WHERE project_order_id=?""",
                (broker_order_id, lifecycle.value, occurred_at.isoformat(),
                 occurred_at.isoformat(), order.project_order_id),
            )
        updated = self.order_for(order.project_order_id)
        if already_acknowledged:
            return None
        return self._apply_submit_event(updated, occurred_at, acknowledged=True)

    def _record_fill(
        self,
        *,
        order: DurableRealOrder,
        broker_order_id: str,
        broker_trade_id: str,
        quantity: Decimal,
        price: Decimal,
        occurred_at: datetime,
    ) -> EventApplicationResult | None:
        if order is None:
            raise ValueError("fill requires a durable project order")
        if type(quantity) is not Decimal or not quantity.is_finite() or quantity <= 0:
            raise ValueError("fill quantity must be a positive finite Decimal")
        if type(price) is not Decimal or not price.is_finite() or price <= 0:
            raise ValueError("fill price must be a positive finite Decimal")
        _aware(occurred_at, "fill timestamp")
        self._invalidate_reconciliation_proof("ORDER_FILLED")
        self._require_broker_mapping_available(
            order.project_order_id, broker_order_id, occurred_at
        )
        fingerprint = _fingerprint({
            "project_order_id": order.project_order_id,
            "broker_order_id": broker_order_id,
            "broker_trade_id": broker_trade_id,
            "quantity": canonical_decimal(quantity),
            "price": canonical_decimal(price),
        })
        if order.broker_order_id not in (None, broker_order_id):
            self._latch_inconsistency(order.project_order_id, "BROKER_ORDER_ID_CONFLICT", occurred_at)
            raise RealExecutionInconsistencyError("BROKER_ORDER_ID_CONFLICT")
        fact_key = "trade:" + broker_trade_id
        inserted = False
        try:
            with closing(self._connect()) as connection, connection:
                existing = connection.execute(
                    "SELECT fingerprint,project_order_id FROM real_execution_facts WHERE fact_key=?",
                    (fact_key,),
                ).fetchone()
                if existing is not None:
                    if existing[0] != fingerprint or existing[1] != order.project_order_id:
                        raise RealExecutionInconsistencyError(
                            "DUPLICATE_EXTERNAL_FACT_DIFFERENT_CONTENT:" + fact_key
                        )
                else:
                    connection.execute(
                        """INSERT INTO real_execution_facts(
                            fact_key,fingerprint,fact_type,project_order_id,broker_order_id,
                            quantity,price,occurred_at
                        ) VALUES(?,?,?,?,?,?,?,?)""",
                        (
                            fact_key, fingerprint, "FILL", order.project_order_id,
                            broker_order_id, canonical_decimal(quantity),
                            canonical_decimal(price), occurred_at.isoformat(),
                        ),
                    )
                    inserted = True
                self._rebuild_fill_aggregate(connection, order.project_order_id)
        except RealExecutionInconsistencyError as error:
            self._latch_inconsistency(order.project_order_id, str(error), occurred_at)
            raise
        if not inserted:
            return None
        fill_event = self._event(
            event_id="real-fill:" + broker_trade_id,
            event_type=BrokerEventType.ORDER_FILLED,
            occurred_at=occurred_at,
            order=order,
            payload=event_pairs(
                broker_order_id=broker_order_id,
                broker_trade_id=broker_trade_id,
                concrete_contract_id=order.concrete_contract_id,
                direction=order.direction,
                action=order.action,
                quantity=quantity,
                price=price,
                trading_day=self.expected_trading_day,
                session_identity=self.session_identity,
            ),
        )
        return self._apply(fill_event)

    def _record_fact(
        self,
        fact_key: str,
        fingerprint: str,
        fact_type: str,
        project_order_id: str,
        broker_order_id: str | None,
        quantity: Decimal | None,
        price: Decimal | None,
        occurred_at: datetime,
    ) -> bool:
        with closing(self._connect()) as connection, connection:
            existing = connection.execute(
                "SELECT fingerprint,project_order_id FROM real_execution_facts WHERE fact_key=?",
                (fact_key,),
            ).fetchone()
            if existing is not None:
                if existing[0] != fingerprint or existing[1] != project_order_id:
                    self._latch_inconsistency(
                        project_order_id,
                        "DUPLICATE_EXTERNAL_FACT_DIFFERENT_CONTENT:" + fact_key,
                        occurred_at,
                    )
                    raise RealExecutionInconsistencyError(
                        "DUPLICATE_EXTERNAL_FACT_DIFFERENT_CONTENT:" + fact_key
                    )
                return False
            connection.execute(
                """INSERT INTO real_execution_facts(
                    fact_key,fingerprint,fact_type,project_order_id,broker_order_id,
                    quantity,price,occurred_at
                ) VALUES(?,?,?,?,?,?,?,?)""",
                (fact_key, fingerprint, fact_type, project_order_id, broker_order_id,
                 None if quantity is None else canonical_decimal(quantity),
                 None if price is None else canonical_decimal(price), occurred_at.isoformat()),
            )
        return True

    def _terminal(
        self, order: DurableRealOrder, lifecycle: RealOrderLifecycle, occurred_at: datetime
    ) -> EventApplicationResult | None:
        if lifecycle not in {RealOrderLifecycle.CANCELLED, RealOrderLifecycle.REJECTED}:
            raise ValueError("unsupported terminal lifecycle")
        self._invalidate_reconciliation_proof("ORDER_" + lifecycle.value)
        current = self.order_for(order.project_order_id)
        if current.lifecycle is lifecycle:
            return None
        self._set_order_lifecycle(order.project_order_id, lifecycle, occurred_at, terminal=True)
        event_type = (
            BrokerEventType.ORDER_CANCELLED
            if lifecycle is RealOrderLifecycle.CANCELLED
            else BrokerEventType.ORDER_REJECTED
        )
        return self._apply(self._event(
            event_id=f"real-{lifecycle.value.lower()}:" + order.project_order_id,
            event_type=event_type,
            occurred_at=occurred_at,
            order=current,
        ))

    def _set_order_lifecycle(
        self,
        project_order_id: str,
        lifecycle: RealOrderLifecycle,
        at: datetime,
        *,
        terminal: bool = False,
    ) -> None:
        _aware(at, "order lifecycle timestamp")
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """UPDATE real_execution_orders
                   SET lifecycle=?,terminal_at=CASE WHEN ? THEN ? ELSE terminal_at END,updated_at=?
                   WHERE project_order_id=?""",
                (lifecycle.value, int(terminal), at.isoformat(), at.isoformat(), project_order_id),
            )

    def _apply_submit_event(
        self, order: DurableRealOrder, occurred_at: datetime, *, acknowledged: bool
    ) -> EventApplicationResult:
        status = OrderStatus.LIVE if acknowledged else OrderStatus.PENDING_SUBMIT
        event = self._event(
            event_id=("real-ack:" if acknowledged else "real-submit:") + order.project_order_id,
            event_type=BrokerEventType.ORDER_SUBMITTED,
            occurred_at=occurred_at,
            order=order,
            payload=event_pairs(
                concrete_contract_id=order.concrete_contract_id,
                direction=order.direction,
                action=order.action,
                quantity=order.requested_quantity,
                lifecycle_status=status,
                broker_order_id=order.broker_order_id,
                trading_day=order.trading_day,
                session_identity=order.session_identity,
            ),
        )
        return self._apply(event)

    def _event(
        self,
        *,
        event_id: str,
        event_type: BrokerEventType,
        occurred_at: datetime,
        order: DurableRealOrder | None = None,
        payload: tuple[tuple[str, str], ...] = (),
    ) -> BrokerEvent:
        event = BrokerEvent(
            event_id=event_id,
            event_type=event_type,
            occurred_at=occurred_at,
            stream_id=self._stream_id,
            sequence=self._sequence,
            order_id=None if order is None else order.project_order_id,
            client_request_id=None if order is None else order.client_request_id,
            payload=payload,
        )
        self._sequence += 1
        return event

    def _apply(self, event: BrokerEvent) -> EventApplicationResult:
        result = self.trading_state.apply_broker_event(event)
        if not result.applied and result.outcome.value != "APPLIED_ALREADY_NOOP":
            self._latch_inconsistency(
                event.order_id or "runtime",
                "TRADING_STATE_REJECTED_COMPOSED_EVENT:" + result.outcome.value,
                event.occurred_at,
            )
            raise RealExecutionInconsistencyError(
                "TRADING_STATE_REJECTED_COMPOSED_EVENT:" + result.outcome.value
            )
        return result

    def _require_broker_mapping_available(
        self,
        project_order_id: str,
        broker_order_id: str,
        occurred_at: datetime,
    ) -> None:
        with closing(self._connect()) as connection:
            conflict = connection.execute(
                """SELECT project_order_id FROM real_execution_orders
                   WHERE broker_order_id=? AND project_order_id<>?""",
                (broker_order_id, project_order_id),
            ).fetchone()
        if conflict is None:
            return
        self._latch_inconsistency(
            project_order_id,
            "BROKER_ORDER_ID_ALREADY_BOUND_TO_OTHER_PROJECT_ORDER",
            occurred_at,
        )
        raise RealExecutionInconsistencyError(
            "BROKER_ORDER_ID_ALREADY_BOUND_TO_OTHER_PROJECT_ORDER"
        )

    def _rehydrate_trading_state(self) -> None:
        for order in self.orders():
            if order.lifecycle is RealOrderLifecycle.INCONSISTENT:
                continue
            existing = self.trading_state.order_for(order.project_order_id)
            if existing is not None:
                if (
                    not self._trading_order_matches_durable(existing, order)
                    or not self._trading_fill_lineage_matches_durable(order)
                ):
                    self._latch_inconsistency(
                        order.project_order_id,
                        "TRADING_STATE_DURABLE_ORDER_DIVERGENCE",
                        order.updated_at,
                    )
                    continue
                continue
            self._apply_submit_event(order, order.created_at, acknowledged=False)
            with closing(self._connect()) as connection:
                row = connection.execute(
                    "SELECT acknowledgement_at FROM real_execution_orders WHERE project_order_id=?",
                    (order.project_order_id,),
                ).fetchone()
                facts = connection.execute(
                    """SELECT * FROM real_execution_facts
                       WHERE project_order_id=? AND fact_type='FILL'
                       ORDER BY occurred_at,fact_key""",
                    (order.project_order_id,),
                ).fetchall()
                terminal = connection.execute(
                    "SELECT terminal_at,lifecycle FROM real_execution_orders WHERE project_order_id=?",
                    (order.project_order_id,),
                ).fetchone()
            if row[0] is not None and order.broker_order_id is not None:
                self._apply_submit_event(
                    order, datetime.fromisoformat(row[0]), acknowledged=True
                )
            for fact in facts:
                fill_event = self._event(
                    event_id="real-fill:" + fact["fact_key"].removeprefix("trade:"),
                    event_type=BrokerEventType.ORDER_FILLED,
                    occurred_at=datetime.fromisoformat(fact["occurred_at"]),
                    order=order,
                    payload=event_pairs(
                        broker_order_id=fact["broker_order_id"],
                        broker_trade_id=fact["fact_key"].removeprefix("trade:"),
                        concrete_contract_id=order.concrete_contract_id,
                        direction=order.direction,
                        action=order.action,
                        quantity=Decimal(fact["quantity"]),
                        price=Decimal(fact["price"]),
                        trading_day=order.trading_day,
                        session_identity=order.session_identity,
                    ),
                )
                self._apply(fill_event)
            if terminal[0] is not None and terminal[1] in {
                RealOrderLifecycle.CANCELLED.value,
                RealOrderLifecycle.REJECTED.value,
            }:
                lifecycle = RealOrderLifecycle(terminal[1])
                terminal_event_type = (
                    BrokerEventType.ORDER_CANCELLED
                    if lifecycle is RealOrderLifecycle.CANCELLED
                    else BrokerEventType.ORDER_REJECTED
                )
                self._apply(self._event(
                    event_id=f"real-{lifecycle.value.lower()}:" + order.project_order_id,
                    event_type=terminal_event_type,
                    occurred_at=datetime.fromisoformat(terminal[0]),
                    order=order,
                ))
        for order in self.orders():
            if order.lifecycle is RealOrderLifecycle.INCONSISTENT:
                continue
            runtime_order = self.trading_state.order_for(order.project_order_id)
            if (
                runtime_order is None
                or not self._trading_order_matches_durable(runtime_order, order)
                or not self._trading_fill_lineage_matches_durable(order)
            ):
                self._latch_inconsistency(
                    order.project_order_id,
                    "TRADING_STATE_DURABLE_ORDER_DIVERGENCE",
                    order.updated_at,
                )
        self._validate_trading_position_projection()

    def _mark_all_unresolved_unknown(self, reason: str) -> None:
        self._invalidate_reconciliation_proof(reason)
        now = datetime.now().astimezone().isoformat()
        terminal = (
            RealOrderLifecycle.FILLED.value,
            RealOrderLifecycle.CANCELLED.value,
            RealOrderLifecycle.REJECTED.value,
        )
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """UPDATE real_execution_orders SET lifecycle=?,updated_at=?
                   WHERE lifecycle NOT IN (?,?,?)""",
                (RealOrderLifecycle.UNKNOWN.value, now, *terminal),
            )
            connection.execute(
                """INSERT INTO real_execution_blockers(code,detail,latched_at,resolved_at)
                   VALUES('BROKER_TRUTH_UNKNOWN',?,?,NULL)
                   ON CONFLICT(code) DO UPDATE SET detail=excluded.detail,
                     latched_at=excluded.latched_at,resolved_at=NULL""",
                (reason, now),
            )

    def _latch_external_mutation(self, detail: str, at: datetime) -> None:
        self._invalidate_reconciliation_proof("EXTERNAL_MUTATION_UNRESOLVED")
        self._latch_blocker("EXTERNAL_MUTATION_UNRESOLVED", detail, at)
        if self.safety_controller is not None and (
            self.safety_controller.state.external_mutation_status
            is not ExternalMutationStatus.UNRESOLVED
        ):
            self.safety_controller.record_external_mutation(detail, at)

    def _latch_inconsistency(self, project_order_id: str, detail: str, at: datetime) -> None:
        self._invalidate_reconciliation_proof("HARD_EXECUTION_INCONSISTENCY")
        if self.order_for(project_order_id) is not None:
            self._set_order_lifecycle(project_order_id, RealOrderLifecycle.INCONSISTENT, at)
        self._latch_blocker("HARD_EXECUTION_INCONSISTENCY", detail, at)
        if self.safety_controller is not None and not self.safety_controller.state.hard_inconsistency_latched:
            self.safety_controller.latch_hard_inconsistency(detail, at)

    def _latch_blocker(self, code: str, detail: str, at: datetime) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """INSERT INTO real_execution_blockers(code,detail,latched_at,resolved_at)
                   VALUES(?,?,?,NULL)
                   ON CONFLICT(code) DO UPDATE SET detail=excluded.detail,
                     latched_at=excluded.latched_at,resolved_at=NULL""",
                (code, detail, at.isoformat()),
            )

    def _confirm_external_resolution(self, at: datetime) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """UPDATE real_execution_blockers SET resolved_at=?
                   WHERE code='EXTERNAL_MUTATION_UNRESOLVED' AND resolved_at IS NULL""",
                (at.isoformat(),),
            )
        if self.safety_controller is not None and (
            self.safety_controller.state.external_mutation_status
            is ExternalMutationStatus.UNRESOLVED
        ):
            self.safety_controller.resolve_external_mutation(
                "complete broker reconciliation verified external truth", at
            )

    def _resolve_blocker(self, code: str, at: datetime) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """UPDATE real_execution_blockers SET resolved_at=?
                   WHERE code=? AND resolved_at IS NULL""",
                (at.isoformat(), code),
            )

    def _restore_persistent_safety(self) -> None:
        if self.safety_controller is None:
            return
        blockers = self.active_blockers()
        now = datetime.now().astimezone()
        if "EXTERNAL_MUTATION_UNRESOLVED" in blockers:
            self.safety_controller.record_external_mutation(
                "restored durable external mutation latch", now
            )
        if "HARD_EXECUTION_INCONSISTENCY" in blockers:
            self.safety_controller.latch_hard_inconsistency(
                "restored durable execution inconsistency latch", now
            )

    def _invalidate_reconciliation_proof(self, reason: str) -> None:
        self._reconciliation_proof = None
        self._readiness_state = "CURRENT_RECONCILIATION_REQUIRED:" + _required_text(
            reason, "reconciliation invalidation reason"
        )

    def _establish_reconciliation_proof(
        self, *, round_id: str, requested_at: datetime, observed_at: datetime
    ) -> None:
        proof = CurrentReconciliationProof(
            composition_instance_id=self._composition_instance_id,
            session_identity=self.session_identity,
            trading_day=self.expected_trading_day,
            round_id=round_id,
            requested_at=requested_at,
            observed_at=observed_at,
        )
        self._reconciliation_proof = proof
        self._readiness_state = "CURRENT_RECONCILIATION_PROVEN:" + proof.identity_id

    def _repair_or_block_legacy_fill_aggregates(self) -> None:
        problems: list[tuple[str, str, datetime]] = []
        with closing(self._connect()) as connection, connection:
            rows = connection.execute(
                "SELECT project_order_id,filled_quantity,updated_at FROM real_execution_orders"
            ).fetchall()
            known_order_ids = {row["project_order_id"] for row in rows}
            orphan_facts = connection.execute(
                """SELECT project_order_id,occurred_at FROM real_execution_facts
                   WHERE fact_type='FILL'"""
            ).fetchall()
            for fact in orphan_facts:
                if fact["project_order_id"] not in known_order_ids:
                    problems.append((
                        fact["project_order_id"],
                        "FILL_FACT_WITHOUT_DURABLE_ORDER",
                        datetime.fromisoformat(fact["occurred_at"]),
                    ))
            for row in rows:
                fact_count = connection.execute(
                    """SELECT COUNT(*) FROM real_execution_facts
                       WHERE project_order_id=? AND fact_type='FILL'""",
                    (row["project_order_id"],),
                ).fetchone()[0]
                if fact_count == 0 and Decimal(row["filled_quantity"]) != 0:
                    problems.append((
                        row["project_order_id"],
                        "ORDER_AGGREGATE_HAS_NO_CANONICAL_FILL_FACTS",
                        datetime.fromisoformat(row["updated_at"]),
                    ))
                    continue
                try:
                    self._rebuild_fill_aggregate(connection, row["project_order_id"])
                except RealExecutionInconsistencyError as error:
                    problems.append((
                        row["project_order_id"],
                        str(error),
                        datetime.fromisoformat(row["updated_at"]),
                    ))
        for project_order_id, detail, occurred_at in problems:
            self._latch_inconsistency(project_order_id, detail, occurred_at)

    def _rebuild_fill_aggregate(
        self, connection: sqlite3.Connection, project_order_id: str
    ) -> None:
        order = connection.execute(
            "SELECT * FROM real_execution_orders WHERE project_order_id=?",
            (project_order_id,),
        ).fetchone()
        if order is None:
            raise RealExecutionInconsistencyError("FILL_FACT_WITHOUT_DURABLE_ORDER")
        facts = connection.execute(
            """SELECT * FROM real_execution_facts
               WHERE project_order_id=? AND fact_type='FILL'
               ORDER BY occurred_at,fact_key""",
            (project_order_id,),
        ).fetchall()
        total = Decimal("0")
        weighted = Decimal("0")
        broker_order_id = order["broker_order_id"]
        latest_at = datetime.fromisoformat(order["updated_at"])
        for fact in facts:
            quantity = Decimal(fact["quantity"])
            price = Decimal(fact["price"])
            if (
                not quantity.is_finite() or quantity <= 0
                or not price.is_finite() or price <= 0
            ):
                raise RealExecutionInconsistencyError("INVALID_CANONICAL_FILL_FACT")
            if broker_order_id not in (None, fact["broker_order_id"]):
                raise RealExecutionInconsistencyError("BROKER_ORDER_ID_CONFLICT")
            broker_order_id = fact["broker_order_id"]
            total += quantity
            weighted += price * quantity
            latest_at = max(latest_at, datetime.fromisoformat(fact["occurred_at"]))
        requested = Decimal(order["requested_quantity"])
        if total > requested:
            raise RealExecutionInconsistencyError("BROKER_OVERFILL")
        average = None if total == 0 else weighted / total
        current_lifecycle = RealOrderLifecycle(order["lifecycle"])
        if current_lifecycle is RealOrderLifecycle.INCONSISTENT:
            lifecycle = current_lifecycle
        elif order["terminal_at"] is not None and current_lifecycle in {
            RealOrderLifecycle.CANCELLED,
            RealOrderLifecycle.REJECTED,
        }:
            lifecycle = current_lifecycle
        elif total == requested:
            lifecycle = RealOrderLifecycle.FILLED
        elif total > 0:
            lifecycle = RealOrderLifecycle.PARTIALLY_FILLED
        else:
            lifecycle = current_lifecycle
        connection.execute(
            """UPDATE real_execution_orders
               SET broker_order_id=?,lifecycle=?,filled_quantity=?,average_fill_price=?,updated_at=?
               WHERE project_order_id=?""",
            (
                broker_order_id, lifecycle.value, canonical_decimal(total),
                None if average is None else canonical_decimal(average),
                latest_at.isoformat(), project_order_id,
            ),
        )

    @staticmethod
    def _runtime_status_for(order: DurableRealOrder) -> OrderStatus:
        mapping = {
            RealOrderLifecycle.PENDING_SUBMIT: OrderStatus.PENDING_SUBMIT,
            RealOrderLifecycle.UNKNOWN: OrderStatus.PENDING_SUBMIT,
            RealOrderLifecycle.OPEN: OrderStatus.LIVE,
            RealOrderLifecycle.PARTIALLY_FILLED: OrderStatus.PARTIALLY_FILLED,
            RealOrderLifecycle.FILLED: OrderStatus.FILLED,
            RealOrderLifecycle.CANCELLED: OrderStatus.CANCELLED,
            RealOrderLifecycle.REJECTED: OrderStatus.REJECTED,
        }
        if order.lifecycle not in mapping:
            raise RealExecutionInconsistencyError("DURABLE_ORDER_LIFECYCLE_UNPROVABLE")
        return mapping[order.lifecycle]

    def _trading_order_matches_durable(self, runtime_order, durable_order: DurableRealOrder) -> bool:
        return (
            runtime_order.order_id == durable_order.project_order_id
            and runtime_order.client_request_id == durable_order.client_request_id
            and runtime_order.concrete_contract_id == durable_order.concrete_contract_id
            and runtime_order.direction is durable_order.direction
            and runtime_order.action is durable_order.action
            and runtime_order.requested_quantity == durable_order.requested_quantity
            and runtime_order.status is self._runtime_status_for(durable_order)
            and runtime_order.filled_quantity == durable_order.filled_quantity
            and runtime_order.average_fill_price == durable_order.average_fill_price
        )

    def _trading_fill_lineage_matches_durable(self, order: DurableRealOrder) -> bool:
        try:
            durable = self._durable_fill_lineage(order)
            runtime = self._trading_fill_lineage(order)
        except (TypeError, ValueError, InvalidOperation):
            return False
        if runtime is None:
            return False
        return _fingerprint({
            "schema_version": REAL_EXECUTION_LINEAGE_SCHEMA_VERSION,
            "fills": runtime,
        }) == _fingerprint({
            "schema_version": REAL_EXECUTION_LINEAGE_SCHEMA_VERSION,
            "fills": durable,
        })

    def _durable_fill_lineage(
        self, order: DurableRealOrder
    ) -> tuple[tuple[tuple[str, str], ...], ...]:
        with closing(self._connect()) as connection:
            facts = connection.execute(
                """SELECT fact_key,broker_order_id,quantity,price,occurred_at
                   FROM real_execution_facts
                   WHERE project_order_id=? AND fact_type='FILL'
                   ORDER BY occurred_at,fact_key""",
                (order.project_order_id,),
            ).fetchall()
        return tuple(
            event_pairs(
                event_id="real-fill:" + fact["fact_key"].removeprefix("trade:"),
                broker_trade_id=fact["fact_key"].removeprefix("trade:"),
                project_order_id=order.project_order_id,
                client_request_id=order.client_request_id,
                broker_order_id=fact["broker_order_id"],
                quantity=Decimal(fact["quantity"]),
                price=Decimal(fact["price"]),
                occurred_at=datetime.fromisoformat(fact["occurred_at"]),
                concrete_contract_id=order.concrete_contract_id,
                direction=order.direction,
                action=order.action,
                trading_day=order.trading_day,
                session_identity=order.session_identity,
            )
            for fact in facts
        )

    def _trading_fill_lineage(
        self, order: DurableRealOrder
    ) -> tuple[tuple[tuple[str, str], ...], ...] | None:
        records: list[tuple[tuple[str, str], ...]] = []
        for event in self.trading_state.applied_events():
            if (
                event.event_type is not BrokerEventType.ORDER_FILLED
                or event.order_id != order.project_order_id
            ):
                continue
            payload = dict(event.payload)
            broker_trade_id = payload.get("broker_trade_id")
            broker_order_id = payload.get("broker_order_id")
            if (
                not broker_trade_id
                or not broker_order_id
                or event.event_id != "real-fill:" + broker_trade_id
                or event.stream_id != self._stream_id
                or event.client_request_id != order.client_request_id
            ):
                return None
            try:
                records.append(event_pairs(
                    event_id=event.event_id,
                    broker_trade_id=broker_trade_id,
                    project_order_id=event.order_id,
                    client_request_id=event.client_request_id,
                    broker_order_id=broker_order_id,
                    quantity=Decimal(_required_text(payload.get("quantity"), "fill quantity")),
                    price=Decimal(_required_text(payload.get("price"), "fill price")),
                    occurred_at=event.occurred_at,
                    concrete_contract_id=_required_text(
                        payload.get("concrete_contract_id"), "fill contract"
                    ),
                    direction=_required_text(payload.get("direction"), "fill direction"),
                    action=_required_text(payload.get("action"), "fill action"),
                    trading_day=_required_text(payload.get("trading_day"), "fill trading day"),
                    session_identity=_required_text(
                        payload.get("session_identity"), "fill session identity"
                    ),
                ))
            except (ValueError, TypeError, InvalidOperation):
                return None
        return tuple(sorted(
            records,
            key=lambda record: (
                dict(record)["occurred_at"],
                dict(record)["broker_trade_id"],
            ),
        ))

    def _validate_trading_position_projection(self) -> None:
        if self._position_baseline is None:
            return
        projections = dict(self._position_baseline)
        with closing(self._connect()) as connection:
            facts = connection.execute(
                """SELECT f.quantity,f.price,o.project_order_id,o.concrete_contract_id,
                          o.direction,o.action,f.occurred_at,f.fact_key
                   FROM real_execution_facts f
                   JOIN real_execution_orders o ON o.project_order_id=f.project_order_id
                   WHERE f.fact_type='FILL' AND o.lifecycle<>?
                   ORDER BY f.occurred_at,f.fact_key""",
                (RealOrderLifecycle.INCONSISTENT.value,),
            ).fetchall()
        for fact in facts:
            key = (fact["concrete_contract_id"], PositionDirection(fact["direction"]))
            quantity, average = projections.get(key, (Decimal("0"), Decimal("0")))
            fill_quantity = Decimal(fact["quantity"])
            fill_price = Decimal(fact["price"])
            if OrderAction(fact["action"]) is OrderAction.OPEN:
                new_quantity = quantity + fill_quantity
                average = (average * quantity + fill_price * fill_quantity) / new_quantity
                quantity = new_quantity
            else:
                if fill_quantity > quantity:
                    self._latch_inconsistency(
                        fact["project_order_id"],
                        "TRADING_POSITION_PROJECTION_UNPROVABLE",
                        datetime.fromisoformat(fact["occurred_at"]),
                    )
                    return
                quantity -= fill_quantity
                if quantity == 0:
                    average = Decimal("0")
            projections[key] = (quantity, average)
        actual_positions = {
            (position.concrete_contract_id, position.direction): position
            for position in self.trading_state.positions
        }
        position_keys = set(projections) | set(actual_positions)
        for contract, direction in sorted(
            position_keys, key=lambda item: (item[0], item[1].value)
        ):
            quantity, average = projections.get(
                (contract, direction), (Decimal("0"), Decimal("0"))
            )
            actual = actual_positions.get((contract, direction))
            matches = (
                (quantity == 0 and actual is None)
                or (
                    quantity > 0
                    and actual is not None
                    and actual.quantity == quantity
                    and actual.average_open_price == average
                )
            )
            if not matches:
                related = next(
                    (
                        item for item in self.orders()
                        if item.concrete_contract_id == contract
                        and item.direction is direction
                    ),
                    None,
                )
                self._latch_inconsistency(
                    (
                        related.project_order_id
                        if related is not None
                        else f"position:{contract}:{direction.value}"
                    ),
                    "TRADING_STATE_POSITION_DIVERGENCE",
                    (
                        related.updated_at
                        if related is not None
                        else datetime.now().astimezone()
                    ),
                )


__all__ = [
    "REAL_EXECUTION_COMPOSITION_SCHEMA_VERSION",
    "REAL_EXECUTION_LINEAGE_SCHEMA_VERSION",
    "REAL_POSITION_BASELINE_SCHEMA_VERSION",
    "CurrentReconciliationProof",
    "DurableRealOrder",
    "RealExecutionComposition",
    "RealExecutionInconsistencyError",
    "RealExecutionRecoveryResult",
    "RealOrderLifecycle",
]
