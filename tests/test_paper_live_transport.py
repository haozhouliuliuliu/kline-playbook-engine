"""Deterministic offline tests for the live 1m transport seam.

Proves the transport (``PaperLiveOneMinuteTransport``) drives an injected
TqSdk-like source into a runtime consumer with zero construction side effects,
bootstrap wake suppression, newly-completed-minute delivery, unfinished-minute
invisibility, and fail-closed behavior on duplicate/out-of-order/gap/wrong-
contract/disconnected/stale/session-mismatch inputs. No provider, credential,
network or external PAPER action occurs.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
import unittest
from zoneinfo import ZoneInfo

from src.paper_live_transport import (
    LiveSessionCalendarResolver,
    PaperLiveOneMinuteTransport,
    TransportPollResult,
)
from tests.test_paper_live_causal_context import (
    EXCHANGE,
    INSTRUMENT,
    PRODUCT,
    TARGET_DAY,
    TZ,
    _CALENDAR,
    _morning_until,
    _prior_days,
)

_ONE_MINUTE = timedelta(minutes=1)
_AT_0915 = _morning_until()
_AT_0920 = datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 20, tzinfo=TZ)


def _ns(value: datetime) -> int:
    """Encode a timestamp in TqSdk-style integer nanoseconds."""
    return int(value.timestamp() * 1_000_000_000)


def _row_for_minute(start: datetime, *, symbol: str = INSTRUMENT, price: str | None = None) -> dict:
    base = Decimal(price) if price is not None else Decimal("70000") + Decimal(start.minute % 60)
    return {
        "datetime": _ns(start),
        "symbol": symbol,
        "open": str(base),
        "high": str(base + Decimal("2")),
        "low": str(base - Decimal("2")),
        "close": str(base + Decimal("1")),
        "volume": "3",
    }


def _rows_for_days(days, *, until: datetime | None = None) -> list[dict]:
    rows: list[dict] = []
    for day in days:
        for window in _CALENDAR.session_windows_for(day):
            cursor = window.start
            while cursor < window.end:
                if until is not None and cursor >= until:
                    break
                rows.append(_row_for_minute(cursor))
                cursor += _ONE_MINUTE
    return rows


def _history_rows(until: datetime | None = None) -> list[dict]:
    days = _prior_days(_CALENDAR.trading_days, 3) + (TARGET_DAY,)
    return _rows_for_days(days, until=until)


class FakeLiveOneMinuteSource:
    """Injected source double; never touches anything external."""

    def __init__(self, rows=(), *, connected: bool = True, last_activity=None):
        self._rows = list(rows)
        self.connected = connected
        self.last_activity = last_activity
        self.read_calls = 0

    def last_activity_at(self):
        return self.last_activity

    def read_recent_1m_rows(self, *, symbol: str, limit: int):
        self.read_calls += 1
        return tuple(self._rows[-limit:])

    def extend(self, rows):
        self._rows.extend(rows)


class FakeTransportConsumer:
    """Structural double for ``TransportConsumer`` / the coordinator surface."""

    def __init__(self):
        self.market_bootstrapped = False
        self.bootstrap_calls: list[tuple] = []
        self.process_calls: list[tuple] = []

    def bootstrap_market(self, bars, *, observed_at):
        self.bootstrap_calls.append((tuple(bars), observed_at))
        self.market_bootstrapped = True

    def process_closed_minutes(self, bars, *, observed_at):
        self.process_calls.append((tuple(bars), observed_at))
        return tuple(bars)


def _transport(source, consumer, *, max_source_age_seconds=None):
    return PaperLiveOneMinuteTransport(
        exchange=EXCHANGE,
        concrete_instrument=INSTRUMENT,
        product=PRODUCT,
        sessions=_CALENDAR,
        source=source,
        consumer=consumer,
        symbol=INSTRUMENT,
        max_source_age_seconds=max_source_age_seconds,
    )


class TransportConstructionTests(unittest.TestCase):
    def test_construction_has_zero_side_effects_and_does_not_touch_source(self) -> None:
        source = FakeLiveOneMinuteSource(_history_rows())
        consumer = FakeTransportConsumer()
        transport = _transport(source, consumer)
        # Neither the injected source nor the consumer may be touched.
        self.assertEqual(source.read_calls, 0)
        self.assertEqual(consumer.bootstrap_calls, [])
        self.assertEqual(consumer.process_calls, [])
        self.assertFalse(transport.bootstrapped)
        self.assertIsNone(transport.watermark_start)
        self.assertIs(transport.source, source)
        self.assertIs(transport.consumer, consumer)

    def test_session_resolver_adapter_reuses_calendar_authority(self) -> None:
        resolver = LiveSessionCalendarResolver(_CALENDAR)
        start = datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 0, tzinfo=TZ)
        day = resolver.trading_day_at(EXCHANGE, INSTRUMENT, start)
        self.assertEqual(day, TARGET_DAY)
        starts = resolver.expected_bar_starts_between(
            EXCHANGE, INSTRUMENT, start, start + timedelta(minutes=5), _ONE_MINUTE)
        self.assertEqual(
            starts,
            tuple(start + timedelta(minutes=i) for i in range(5)),
        )


class TransportBootstrapTests(unittest.TestCase):
    def test_bootstrap_suppresses_historical_wakes(self) -> None:
        source = FakeLiveOneMinuteSource(_history_rows(until=_AT_0915))
        consumer = FakeTransportConsumer()
        transport = _transport(source, consumer)
        bars = transport.bootstrap(observed_at=_AT_0915)
        self.assertTrue(bars)
        self.assertEqual(bars[-1].completed_bar.start, datetime(
            TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 14, tzinfo=TZ))
        # exactly one bootstrap delivery and zero closed-minute processing
        self.assertEqual(len(consumer.bootstrap_calls), 1)
        self.assertEqual(consumer.process_calls, [])
        self.assertTrue(transport.bootstrapped)
        self.assertEqual(transport.watermark_start, bars[-1].completed_bar.start)

    def test_bootstrap_with_no_closed_minutes_fails_closed(self) -> None:
        # only the currently forming minute (end after observed_at) is offered,
        # so there is no completed causal minute to seed the watermark.
        forming = [_row_for_minute(datetime(
            TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 15, tzinfo=TZ))]
        source = FakeLiveOneMinuteSource(forming)
        transport = _transport(source, FakeTransportConsumer())
        with self.assertRaisesRegex(RuntimeError, "PAPER_TRANSPORT_BOOTSTRAP_NO_CLOSED_MINUTES"):
            transport.bootstrap(observed_at=_AT_0915)

    def test_rebootstrap_catches_up_without_reseeding_consumer(self) -> None:
        source = FakeLiveOneMinuteSource(_history_rows(until=_AT_0915))
        consumer = FakeTransportConsumer()
        transport = _transport(source, consumer)
        transport.bootstrap(observed_at=_AT_0915)
        source.extend(_history_rows(until=_AT_0920))
        transport.bootstrap(observed_at=_AT_0920)
        # still exactly one bootstrap delivery (no duplicate historical seeding)
        self.assertEqual(len(consumer.bootstrap_calls), 1)
        self.assertEqual(len(consumer.process_calls), 1)
        self.assertEqual(len(consumer.process_calls[0][0]), 5)


class TransportPollTests(unittest.TestCase):
    def _bootstrapped(self, until=_AT_0915):
        source = FakeLiveOneMinuteSource(_history_rows(until=until))
        consumer = FakeTransportConsumer()
        transport = _transport(source, consumer)
        transport.bootstrap(observed_at=until)
        return source, consumer, transport

    def test_newly_completed_minutes_reach_consumer(self) -> None:
        source, consumer, transport = self._bootstrapped()
        source.extend(_history_rows(until=_AT_0920))
        result = transport.poll(observed_at=_AT_0920)
        self.assertIsInstance(result, TransportPollResult)
        # strictly the 09:15..09:19 newly closed minutes
        self.assertEqual(
            [bar.completed_bar.start for bar in result.bars],
            [datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 15 + i, tzinfo=TZ)
             for i in range(5)],
        )
        self.assertEqual(len(consumer.process_calls), 1)
        delivered = consumer.process_calls[0][0]
        self.assertEqual(len(delivered), 5)
        self.assertEqual(result.consumer_result, delivered)

    def test_unfinished_minute_is_not_visible(self) -> None:
        source, consumer, transport = self._bootstrapped()
        # 09:15 closes at 09:16; the 09:16 minute (end 09:17) is still forming
        # at observed_at 09:16 and must not be delivered.
        source.extend(_history_rows(until=datetime(
            TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 16, tzinfo=TZ)))
        result = transport.poll(observed_at=datetime(
            TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 16, tzinfo=TZ))
        self.assertEqual(len(result.bars), 1)
        self.assertEqual(result.bars[0].completed_bar.start, datetime(
            TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 15, tzinfo=TZ))

    def test_repeated_poll_does_not_duplicate_delivery(self) -> None:
        source, consumer, transport = self._bootstrapped()
        source.extend(_history_rows(until=_AT_0920))
        first = transport.poll(observed_at=_AT_0920)
        self.assertEqual(len(first.bars), 5)
        second = transport.poll(observed_at=_AT_0920)
        self.assertEqual(second.bars, ())
        self.assertIsNone(second.consumer_result)
        self.assertEqual(len(consumer.process_calls), 1)


class TransportFailClosedTests(unittest.TestCase):
    def _bootstrapped(self):
        source = FakeLiveOneMinuteSource(_history_rows(until=_AT_0915))
        consumer = FakeTransportConsumer()
        transport = _transport(source, consumer)
        transport.bootstrap(observed_at=_AT_0915)
        return source, consumer, transport

    def test_duplicate_rows_fail_closed(self) -> None:
        source, _, transport = self._bootstrapped()
        # duplicate of the most recent closed minute (09:19) inside one serial
        duplicate = _row_for_minute(datetime(
            TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 19, tzinfo=TZ))
        source.extend(_history_rows(until=_AT_0920))
        source.extend([duplicate])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            transport.poll(observed_at=_AT_0920)

    def test_out_of_order_rows_fail_closed(self) -> None:
        source, _, transport = self._bootstrapped()
        a = _row_for_minute(datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 17, tzinfo=TZ))
        b = _row_for_minute(datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 16, tzinfo=TZ))
        source.extend([a, b])
        with self.assertRaisesRegex(ValueError, "out-of-order"):
            transport.poll(observed_at=_AT_0920)

    def test_missing_governed_minute_fails_closed(self) -> None:
        source, _, transport = self._bootstrapped()
        rows = [
            row for row in _history_rows(until=_AT_0920)
            if _ns(datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 16, tzinfo=TZ))
            != row["datetime"]
        ]
        source.extend(rows)
        with self.assertRaisesRegex(ValueError, "LIVE_BAR_SEQUENCE_MISMATCH"):
            transport.poll(observed_at=_AT_0920)

    def test_wrong_contract_fails_closed(self) -> None:
        source = FakeLiveOneMinuteSource(
            [_row_for_minute(datetime(
                TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 0, tzinfo=TZ),
                symbol="rb9999")])
        transport = _transport(source, FakeTransportConsumer())
        with self.assertRaisesRegex(ValueError, "contract identity mismatch"):
            transport.bootstrap(observed_at=_AT_0915)

    def test_disconnected_source_fails_closed(self) -> None:
        source, _, transport = self._bootstrapped()
        source.connected = False
        with self.assertRaisesRegex(RuntimeError, "PAPER_TRANSPORT_SOURCE_DISCONNECTED"):
            transport.poll(observed_at=_AT_0920)

    def test_stale_source_fails_closed(self) -> None:
        source = FakeLiveOneMinuteSource(
            _history_rows(until=_AT_0915),
            last_activity=_AT_0915 - timedelta(minutes=10),
        )
        consumer = FakeTransportConsumer()
        transport = _transport(source, consumer, max_source_age_seconds=30)
        with self.assertRaisesRegex(RuntimeError, "PAPER_TRANSPORT_SOURCE_STALE"):
            transport.bootstrap(observed_at=_AT_0915)

    def test_non_governed_minute_fails_closed(self) -> None:
        # a minute during the 10:15-10:30 governed break is outside any session
        break_minute = datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 10, 15, tzinfo=TZ)
        source = FakeLiveOneMinuteSource([_row_for_minute(break_minute)])
        transport = _transport(source, FakeTransportConsumer())
        with self.assertRaisesRegex(ValueError, "outside governed session"):
            transport.bootstrap(observed_at=datetime(
                TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 10, 16, tzinfo=TZ))


if __name__ == "__main__":
    unittest.main()
