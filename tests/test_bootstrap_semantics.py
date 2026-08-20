import unittest
from dataclasses import FrozenInstanceError
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.bootstrap_semantics import (
    BrokerEvent,
    CrossTradingDayConflict,
    EventIdentityConflict,
    Ledger,
    NormalizedSessionCalendar,
    SequenceConflict,
    TradingSession,
    TradingState,
)
from src.data_substrate import SessionMetadata, SessionWindow

CN = ZoneInfo("Asia/Shanghai")


class SessionSemanticsTests(unittest.TestCase):
    def setUp(self):
        # Feasibility fixture mirrors SHFE semantics: a trading day may begin in
        # the previous workday's continuous-trading period. Exact exchange and
        # product calendars must be supplied as explicit normalized metadata.
        td = date(2025, 6, 16)  # Monday trading day fixture
        self.calendar = NormalizedSessionCalendar(
            [
                TradingSession("SHFE", "AD", td, datetime(2025, 6, 13, 21, 0, tzinfo=CN), datetime(2025, 6, 14, 1, 0, tzinfo=CN), "continuous"),
                TradingSession("SHFE", "AD", td, datetime(2025, 6, 16, 9, 0, tzinfo=CN), datetime(2025, 6, 16, 10, 15, tzinfo=CN), "day"),
                TradingSession("SHFE", "AD", td, datetime(2025, 6, 16, 10, 30, tzinfo=CN), datetime(2025, 6, 16, 11, 30, tzinfo=CN), "day"),
                TradingSession("SHFE", "AD", td, datetime(2025, 6, 16, 13, 30, tzinfo=CN), datetime(2025, 6, 16, 15, 0, tzinfo=CN), "day"),
            ]
        )

    def test_previous_workday_night_maps_to_next_trading_day(self):
        self.assertEqual(
            self.calendar.trading_day_at("SHFE", "AD", datetime(2025, 6, 13, 21, 30, tzinfo=CN)),
            date(2025, 6, 16),
        )

    def test_after_midnight_continuous_session_keeps_same_trading_day(self):
        self.assertEqual(
            self.calendar.trading_day_at("SHFE", "AD", datetime(2025, 6, 14, 0, 30, tzinfo=CN)),
            date(2025, 6, 16),
        )

    def test_calendar_does_not_infer_unpublished_sessions(self):
        self.assertIsNone(
            self.calendar.trading_day_at("SHFE", "AD", datetime(2025, 6, 14, 10, 0, tzinfo=CN))
        )


class TradingDayAuthorityTests(unittest.TestCase):
    """TD-001: one timestamp maps to exactly one official trading day/week.

    The bootstrap feasibility calendar must delegate trading-day and weekly
    attribution to the authoritative ``SessionMetadata`` semantics, so no
    second, competing trading-day algorithm exists anywhere in the trusted
    path.
    """

    def setUp(self):
        td = date(2025, 6, 16)  # Monday trading day fixture
        sessions = [
            TradingSession("SHFE", "AD", td, datetime(2025, 6, 13, 21, 0, tzinfo=CN), datetime(2025, 6, 14, 1, 0, tzinfo=CN), "continuous"),
            TradingSession("SHFE", "AD", td, datetime(2025, 6, 16, 9, 0, tzinfo=CN), datetime(2025, 6, 16, 10, 15, tzinfo=CN), "day"),
            TradingSession("SHFE", "AD", td, datetime(2025, 6, 16, 10, 30, tzinfo=CN), datetime(2025, 6, 16, 11, 30, tzinfo=CN), "day"),
            TradingSession("SHFE", "AD", td, datetime(2025, 6, 16, 13, 30, tzinfo=CN), datetime(2025, 6, 16, 15, 0, tzinfo=CN), "day"),
        ]
        self.calendar = NormalizedSessionCalendar(sessions)
        # The same session facts expressed directly through the authoritative
        # SessionMetadata, used to prove there is no second truth source.
        self.authoritative = SessionMetadata(
            "bootstrap-feasibility-fixture-v1",
            [
                SessionWindow("SHFE", "AD", td, datetime(2025, 6, 13, 21, 0, tzinfo=CN), datetime(2025, 6, 14, 1, 0, tzinfo=CN), "continuous"),
                SessionWindow("SHFE", "AD", td, datetime(2025, 6, 16, 9, 0, tzinfo=CN), datetime(2025, 6, 16, 10, 15, tzinfo=CN), "day"),
                SessionWindow("SHFE", "AD", td, datetime(2025, 6, 16, 10, 30, tzinfo=CN), datetime(2025, 6, 16, 11, 30, tzinfo=CN), "day"),
                SessionWindow("SHFE", "AD", td, datetime(2025, 6, 16, 13, 30, tzinfo=CN), datetime(2025, 6, 16, 15, 0, tzinfo=CN), "day"),
            ],
        )

    def test_normal_daytime_session_maps_to_its_own_trading_day(self):
        self.assertEqual(
            self.calendar.trading_day_at("SHFE", "AD", datetime(2025, 6, 16, 9, 30, tzinfo=CN)),
            date(2025, 6, 16),
        )

    def test_night_session_crossing_civil_midnight_is_deterministic(self):
        # 21:30 civil Friday and 00:30 civil Saturday both belong to the
        # official trading day Monday 2025-06-16, never to their civil dates.
        self.assertEqual(
            self.calendar.trading_day_at("SHFE", "AD", datetime(2025, 6, 13, 21, 30, tzinfo=CN)),
            date(2025, 6, 16),
        )
        self.assertEqual(
            self.calendar.trading_day_at("SHFE", "AD", datetime(2025, 6, 14, 0, 30, tzinfo=CN)),
            date(2025, 6, 16),
        )

    def test_transition_into_official_next_trading_day_is_deterministic(self):
        # The night window ends at 01:00 civil Saturday (end-exclusive), so at
        # 01:00 the timestamp no longer maps to the night session and no other
        # window claims the civil date.
        self.assertEqual(
            self.calendar.trading_day_at("SHFE", "AD", datetime(2025, 6, 13, 23, 59, tzinfo=CN)),
            date(2025, 6, 16),
        )
        self.assertIsNone(
            self.calendar.trading_day_at("SHFE", "AD", datetime(2025, 6, 14, 1, 0, tzinfo=CN))
        )
        self.assertIsNone(
            self.calendar.trading_day_at("SHFE", "AD", datetime(2025, 6, 14, 10, 0, tzinfo=CN))
        )

    def test_week_attribution_uses_official_trading_day_identity(self):
        # Civil Friday 2025-06-13 is ISO week 24, but the night session opens
        # for Monday 2025-06-16 (ISO week 25).  Weekly attribution must follow
        # the official trading-day identity, so it is week 25 everywhere.
        self.assertEqual(
            self.calendar.trading_week_at("SHFE", "AD", datetime(2025, 6, 13, 21, 30, tzinfo=CN)),
            (2025, 25),
        )
        self.assertEqual(
            self.calendar.trading_week_at("SHFE", "AD", datetime(2025, 6, 14, 0, 30, tzinfo=CN)),
            (2025, 25),
        )
        self.assertEqual(
            self.calendar.trading_week_at("SHFE", "AD", datetime(2025, 6, 16, 9, 30, tzinfo=CN)),
            (2025, 25),
        )
        self.assertIsNone(
            self.calendar.trading_week_at("SHFE", "AD", datetime(2025, 6, 14, 10, 0, tzinfo=CN))
        )

    def test_same_event_receives_same_trading_day_everywhere(self):
        timestamps = (
            datetime(2025, 6, 13, 21, 30, tzinfo=CN),
            datetime(2025, 6, 14, 0, 30, tzinfo=CN),
            datetime(2025, 6, 16, 9, 30, tzinfo=CN),
            datetime(2025, 6, 16, 14, 0, tzinfo=CN),
        )
        for ts in timestamps:
            with self.subTest(ts=ts):
                fixture_day = self.calendar.trading_day_at("SHFE", "AD", ts)
                authority_day = self.authoritative.trading_day_at("SHFE", "AD", ts)
                self.assertEqual(fixture_day, authority_day)
                self.assertEqual(
                    self.calendar.trading_week_at("SHFE", "AD", ts),
                    self.authoritative.trading_week_at("SHFE", "AD", ts),
                )


class BrokerEventSemanticsTests(unittest.TestCase):
    def test_out_of_order_is_buffered_then_applied_in_sequence(self):
        state = TradingState()
        td = date(2025, 6, 16)
        seq2 = BrokerEvent("E2", td, 2, "AD2508", 2)
        seq1 = BrokerEvent("E1", td, 1, "AD2508", 1)

        r2 = state.ingest(seq2)
        self.assertTrue(r2.buffered)
        self.assertEqual(state.position("AD2508"), 0)

        r1 = state.ingest(seq1)
        self.assertEqual([x.event_id for x in r1.applied], ["E1", "E2"])
        self.assertEqual(state.position("AD2508"), 3)
        self.assertEqual(state.last_sequence(td), 2)

    def test_duplicate_event_is_idempotent(self):
        state = TradingState()
        event = BrokerEvent("E1", date(2025, 6, 16), 1, "AD2508", 1)
        state.ingest(event)
        duplicate = state.ingest(event)
        self.assertTrue(duplicate.duplicate)
        self.assertEqual(duplicate.applied, ())
        self.assertEqual(state.position("AD2508"), 1)

    def test_conflicting_event_identity_fails_closed(self):
        state = TradingState()
        td = date(2025, 6, 16)
        state.ingest(BrokerEvent("E1", td, 1, "AD2508", 1))
        with self.assertRaises(EventIdentityConflict):
            state.ingest(BrokerEvent("E1", td, 2, "AD2508", 5))

    def test_unseen_stale_sequence_fails_closed(self):
        state = TradingState()
        td = date(2025, 6, 16)
        state.ingest(BrokerEvent("E1", td, 1, "AD2508", 1))
        with self.assertRaises(SequenceConflict):
            state.ingest(BrokerEvent("OTHER", td, 1, "AD2508", 9))


class StateLedgerBoundaryTests(unittest.TestCase):
    def test_ledger_records_facts_but_does_not_own_mutable_state(self):
        state = TradingState()
        ledger = Ledger()
        event = BrokerEvent("E1", date(2025, 6, 16), 1, "AD2508", 4)
        result = state.ingest(event)
        self.assertEqual(state.position("AD2508"), 4)
        self.assertEqual(len(ledger.records), 0)

        for transition in result.applied:
            ledger.append_transition(transition)

        self.assertEqual(len(ledger.records), 1)
        self.assertEqual(ledger.records[0].quantity_after, 4)
        self.assertEqual(state.position("AD2508"), 4)
        with self.assertRaises(FrozenInstanceError):
            ledger.records[0].quantity_after = 99

    def test_duplicate_broker_event_creates_no_second_transition(self):
        state = TradingState()
        ledger = Ledger()
        event = BrokerEvent("E1", date(2025, 6, 16), 1, "AD2508", 4)
        first = state.ingest(event)
        for transition in first.applied:
            ledger.append_transition(transition)
        second = state.ingest(event)
        for transition in second.applied:
            ledger.append_transition(transition)
        self.assertEqual(len(ledger.records), 1)
        self.assertEqual(state.position("AD2508"), 4)


class CrossTradingDayChronologyBarrierTests(unittest.TestCase):
    """E-13: the feasibility TradingState enforces a cross-trading-day
    chronology barrier so a missing prior-day event can never mutate the
    shared position after a future trading day has already applied."""

    D1 = date(2025, 6, 16)
    D2 = date(2025, 6, 17)

    def test_prior_day_gap_blocks_future_trading_day(self):
        state = TradingState()
        # D1 seq1 applied, D1 seq3 buffered (seq2 missing).
        state.ingest(BrokerEvent("D1E1", self.D1, 1, "AD2508", 1))
        state.ingest(BrokerEvent("D1E3", self.D1, 3, "AD2508", 2))
        self.assertEqual(state.position("AD2508"), 1)
        # D2 seq1 must fail closed while D1 still has a buffered gap.
        with self.assertRaises(CrossTradingDayConflict):
            state.ingest(BrokerEvent("D2E1", self.D2, 1, "AD2508", 4))
        # The shared position is not mutated by the rejected future day.
        self.assertEqual(state.position("AD2508"), 1)
        # Filling the D1 gap then allows D2 to begin normally.
        applied_d1 = state.ingest(BrokerEvent("D1E2", self.D1, 2, "AD2508", 3))
        self.assertEqual([x.event_id for x in applied_d1.applied], ["D1E2", "D1E3"])
        self.assertEqual(state.position("AD2508"), 6)
        applied_d2 = state.ingest(BrokerEvent("D2E1", self.D2, 1, "AD2508", 4))
        self.assertEqual([x.event_id for x in applied_d2.applied], ["D2E1"])
        self.assertEqual(state.position("AD2508"), 10)

    def test_late_prior_day_event_after_future_day_is_rejected(self):
        state = TradingState()
        # D1 complete, D2 seq1 applied.
        state.ingest(BrokerEvent("D1E1", self.D1, 1, "AD2508", 1))
        state.ingest(BrokerEvent("D1E2", self.D1, 2, "AD2508", 2))
        state.ingest(BrokerEvent("D2E1", self.D2, 1, "AD2508", 3))
        self.assertEqual(state.position("AD2508"), 6)
        # A late prior-day event after D2 already applied is rejected.
        with self.assertRaises(CrossTradingDayConflict):
            state.ingest(BrokerEvent("D1E3", self.D1, 3, "AD2508", 1))
        self.assertEqual(state.position("AD2508"), 6)

    def test_same_day_sequence_behavior_is_preserved(self):
        state = TradingState()
        # Out-of-order within one trading day is still buffered then applied.
        r2 = state.ingest(BrokerEvent("E2", self.D1, 2, "AD2508", 2))
        self.assertTrue(r2.buffered)
        r1 = state.ingest(BrokerEvent("E1", self.D1, 1, "AD2508", 1))
        self.assertEqual([x.event_id for x in r1.applied], ["E1", "E2"])
        self.assertEqual(state.position("AD2508"), 3)
        self.assertEqual(state.last_sequence(self.D1), 2)


if __name__ == "__main__":
    unittest.main()
