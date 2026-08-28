"""TqSdk-like live 1m transport seam that drives the generic PAPER runtime.

OFFLINE ONLY. Importing or constructing this module performs zero network
connection, credential read, account login, provider call or broker action. The
actual third-party/TqSdk-like market-data source is injected and is never touched
until an explicit runtime action (``bootstrap`` / ``poll``) is called.

The transport is the smallest project-owned pump between a TqSdk-like live 1m
source and ``PaperRuntimeCoordinator`` (or any structurally compatible consumer):

- ``bootstrap`` normalizes a current/recent 1m serial, establishes the tracker
  watermark and seeds the consumer's causal context through its ``bootstrap``
  path (no historical wake storm). It is idempotent: it never re-seeds an
  already-bootstrapped consumer, so reconnect/restart cannot duplicate wakes.
- ``poll`` obtains newly closed 1m rows from the injected source, keeps only
  rows strictly after the watermark and drives the consumer's closed-minute
  path. It never supplies unfinished/future data.

The transport reuses the already-proven replay/live causal semantics (session
authority, contiguous-window / civil-4H aggregation and wake rules) via
``LiveSessionCalendar`` and ``LiveCausalContextBuilder``; it invents no new
timeframe policy. Fail-closed guarantees:

- disconnected / stale injected source;
- missing governed minute (sequence mismatch);
- out-of-order rows and conflicting duplicate rows in one serial;
- wrong contract/symbol identity;
- session/calendar mismatch (non-governed minute);
- re-bootstrap / reconnect duplicating already admitted wakes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Mapping, Protocol, Sequence

from src.live_market_data import (
    LiveClosedBar,
    LiveSessionResolver,
    TqSdkClosedBarTracker,
)
from src.paper_live_causal_context import LiveSessionCalendar

PAPER_LIVE_TRANSPORT_VERSION = "KPE_PAPER_LIVE_TRANSPORT_V0_1"
_ONE_MINUTE = timedelta(minutes=1)


class LiveOneMinuteSource(Protocol):
    """Injected TqSdk-like live 1m market-data source.

    The real TqSdk object (or any test double) is supplied by the caller. This
    module never imports TqSdk and never reads credentials. ``read_recent_1m_rows``
    returns raw kline rows compatible with the project ``normalize_tqsdk_live_kline_row``
    contract (``datetime`` in nanoseconds, ``open/high/low/close/volume``, optional
    ``symbol``).
    """

    @property
    def connected(self) -> bool: ...

    @property
    def contract_identity(self) -> str: ...

    @property
    def identity_id(self) -> str: ...

    def last_activity_at(self) -> datetime | None:
        """Most recent source activity time, or None if the source cannot report it."""
        ...

    def read_recent_1m_rows(
        self, *, symbol: str, limit: int
    ) -> tuple[Mapping[str, object], ...]:
        """Return a current/recent closed 1m kline serial for ``symbol``."""
        ...


class TransportConsumer(Protocol):
    """Downstream runtime surface driven by the transport (structural).

    ``PaperRuntimeCoordinator`` satisfies this protocol: ``market_bootstrapped``
    is a public boolean, ``bootstrap_market`` seeds the causal context without
    emitting wakes, and ``process_closed_minutes`` drives wake -> trader ->
    governed execution. A test double may stand in for isolation.
    """

    @property
    def market_bootstrapped(self) -> bool: ...

    def bootstrap_market(self, bars: Sequence[object], *, observed_at: datetime) -> None: ...

    def process_closed_minutes(
        self, bars: Sequence[object], *, observed_at: datetime
    ) -> object: ...


class LiveSessionCalendarResolver:
    """Adapt ``LiveSessionCalendar`` to the ``LiveSessionResolver`` contract used
    by the project TqSdk closed-bar normalization.

    ``LiveSessionCalendar`` already owns the governed session/calendar authority
    for the live causal context; this adapter only widens its method signatures
    for the 1m normalization seam. It invents no new session semantics.
    """

    def __init__(self, calendar: LiveSessionCalendar) -> None:
        if not isinstance(calendar, LiveSessionCalendar):
            raise ValueError("live 1m transport requires LiveSessionCalendar")
        self._calendar = calendar

    def trading_day_at(
        self, exchange: str, instrument: str, timestamp: datetime
    ) -> date | None:
        return self._calendar.trading_day_at(timestamp)

    def expected_bar_starts_between(
        self,
        exchange: str,
        instrument: str,
        coverage_start: datetime,
        coverage_end: datetime,
        interval: timedelta,
    ) -> tuple[datetime, ...]:
        if interval != _ONE_MINUTE:
            raise ValueError("live 1m transport only supports a 1-minute interval")
        return self._calendar.expected_minute_starts_between(
            coverage_start, coverage_end
        )


@dataclass(frozen=True)
class TransportPollResult:
    """One poll outcome: the closed bars delivered and the consumer result."""

    bars: tuple[LiveClosedBar, ...]
    consumer_result: object


class PaperLiveOneMinuteTransport:
    """Project-owned pump between an injected TqSdk-like 1m source and the runtime.

    Construction is side-effect free: the injected source and consumer are not
    touched until ``bootstrap`` / ``poll`` is explicitly called.
    """

    def __init__(
        self,
        *,
        exchange: str,
        concrete_instrument: str,
        product: str,
        sessions: LiveSessionCalendar,
        source: LiveOneMinuteSource,
        consumer: TransportConsumer,
        timezone: str = "Asia/Shanghai",
        duration_seconds: int = 60,
        symbol: str | None = None,
        source_poll_limit: int = 512,
        max_source_age_seconds: int | None = None,
        require_source_freshness: bool = False,
        tracker: TqSdkClosedBarTracker | None = None,
        concrete_contract_id: str | None = None,
        require_exact_source_identity: bool = False,
    ) -> None:
        if not isinstance(exchange, str) or not exchange.strip():
            raise ValueError("live transport exchange must be non-empty")
        if not isinstance(concrete_instrument, str) or not concrete_instrument.strip():
            raise ValueError("live transport concrete instrument must be non-empty")
        if concrete_contract_id is None:
            concrete_contract_id = f"{exchange}.{concrete_instrument}"
        if not isinstance(concrete_contract_id, str) or not concrete_contract_id.strip():
            raise ValueError("live transport concrete contract must be non-empty")
        if concrete_contract_id != f"{exchange}.{concrete_instrument}":
            raise ValueError("live transport full contract disagrees with exchange/instrument")
        if not isinstance(product, str) or not product.strip():
            raise ValueError("live transport product must be non-empty")
        if timezone != "Asia/Shanghai":
            raise ValueError("live 1m transport timezone must be Asia/Shanghai")
        if type(duration_seconds) is not int or duration_seconds <= 0:
            raise ValueError("live transport duration must be a positive integer")
        if duration_seconds != 60:
            raise ValueError("live transport only supports a 1-minute duration")
        if type(source_poll_limit) is not int or source_poll_limit <= 0:
            raise ValueError("live transport poll limit must be a positive integer")
        if max_source_age_seconds is not None and (
            type(max_source_age_seconds) is not int or max_source_age_seconds <= 0
        ):
            raise ValueError("live transport max source age must be a positive integer")
        if type(require_source_freshness) is not bool:
            raise ValueError("live transport freshness requirement must be bool")
        if type(require_exact_source_identity) is not bool:
            raise ValueError("live transport source identity requirement must be bool")
        if not isinstance(sessions, LiveSessionCalendar):
            raise ValueError("live transport requires LiveSessionCalendar")
        if sessions.product != product:
            raise ValueError("live transport product disagrees with the session calendar")
        if not isinstance(source, object) or source is None:
            raise ValueError("live transport requires an injected 1m source")
        if not isinstance(consumer, object) or consumer is None:
            raise ValueError("live transport requires a runtime consumer")

        self.exchange = exchange
        self.concrete_contract_id = concrete_contract_id
        self.concrete_instrument = concrete_instrument
        self.product = product
        self.sessions = sessions
        self.timezone = timezone
        self.duration_seconds = duration_seconds
        self._symbol = symbol if symbol is not None else concrete_contract_id
        if not isinstance(self._symbol, str) or not self._symbol.strip():
            raise ValueError("live transport kline symbol must be non-empty")
        if require_exact_source_identity and self._symbol != concrete_contract_id:
            raise ValueError("live transport source symbol must equal the full concrete contract id")
        self._source_poll_limit = source_poll_limit
        self._max_source_age_seconds = max_source_age_seconds
        self._require_source_freshness = require_source_freshness
        self._source = source
        self._consumer = consumer
        source_contract = getattr(source, "contract_identity", None)
        if require_exact_source_identity and source_contract != concrete_contract_id:
            raise ValueError("LIVE_TRANSPORT_SOURCE_CONTRACT_IDENTITY_MISMATCH")
        if source_contract is not None and source_contract != concrete_contract_id:
            raise ValueError("LIVE_TRANSPORT_SOURCE_CONTRACT_IDENTITY_MISMATCH")
        resolver = LiveSessionCalendarResolver(sessions)
        self._tracker = tracker if tracker is not None else TqSdkClosedBarTracker(
            exchange=exchange,
            concrete_instrument=concrete_instrument,
            duration_seconds=duration_seconds,
            timezone=timezone,
            sessions=resolver,
        )
        consumer_watermark = getattr(consumer, "context_builder", None)
        consumer_watermark = getattr(consumer_watermark, "last_accepted_minute_start", None)
        if consumer_watermark is not None:
            if self._tracker.watermark_start not in (None, consumer_watermark):
                raise ValueError("LIVE_TRANSPORT_TRACKER_CONTEXT_WATERMARK_MISMATCH")
            self._tracker.restore_watermark(consumer_watermark)
        # The consumer is intentionally not touched here.

    # ------------------------------------------------------------------ public

    @property
    def version(self) -> str:
        return PAPER_LIVE_TRANSPORT_VERSION

    @property
    def symbol(self) -> str:
        return self._symbol

    @property
    def watermark_start(self) -> datetime | None:
        """Last normalized closed 1m bar start accepted by the tracker."""
        return self._tracker.watermark_start

    @property
    def bootstrapped(self) -> bool:
        return self._tracker.watermark_start is not None

    @property
    def consumer(self) -> TransportConsumer:
        return self._consumer

    @property
    def source(self) -> LiveOneMinuteSource:
        return self._source

    @property
    def identity_id(self) -> str:
        from hashlib import sha256
        import json
        payload = {
            "version": PAPER_LIVE_TRANSPORT_VERSION,
            "exchange": self.exchange,
            "concrete_contract_id": self.concrete_contract_id,
            "concrete_instrument": self.concrete_instrument,
            "product": self.product,
            "symbol": self._symbol,
            "source_identity": getattr(self._source, "identity_id", None),
            "source_poll_limit": self._source_poll_limit,
            "max_source_age_seconds": self._max_source_age_seconds,
            "require_source_freshness": self._require_source_freshness,
        }
        return sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def bootstrap(self, *, observed_at: datetime) -> tuple[LiveClosedBar, ...]:
        """Normalize a current/recent serial, set the watermark and seed context.

        Delivers the normalized closed bars through the consumer's bootstrap path
        exactly once. Re-invoking ``bootstrap`` (e.g. after a source reconnect)
        only refreshes the tracker watermark and never re-seeds an already
        bootstrapped consumer, so already admitted wakes cannot be duplicated.
        """
        _aware(observed_at, "live transport bootstrap time")
        self._require_source_ready(observed_at)
        rows = self._read_rows()
        bars = self._tracker.normalize_closed(rows, observed_at=observed_at)
        if not bars:
            raise RuntimeError("PAPER_TRANSPORT_BOOTSTRAP_NO_CLOSED_MINUTES")
        previous_watermark = self._tracker.watermark_start
        if not self._consumer.market_bootstrapped:
            try:
                self._consumer.bootstrap_market(bars, observed_at=observed_at)
                self._tracker.bootstrap(rows, observed_at=observed_at)
            except Exception:
                self._tracker.restore_watermark(previous_watermark)
                raise
            return bars

        # Restart/reconnect: resume strictly from the restored causal cursor.
        # Never move the watermark to the latest serial row before the missing
        # governed minutes have been accepted downstream.
        if self._tracker.watermark_start is None:
            raise RuntimeError("PAPER_TRANSPORT_RESTART_WATERMARK_MISSING")
        return self.poll(observed_at=observed_at).bars

    def poll(self, *, observed_at: datetime) -> TransportPollResult:
        """Drive newly closed 1m bars from the injected source into the consumer.

        Fails closed on a disconnected/stale source or a governed-minute gap /
        out-of-order / conflicting-duplicate / wrong-contract / session mismatch.
        Never returns or delivers unfinished/future data and never re-delivers an
        already admitted minute (the tracker watermark plus the consumer's causal
        builder deduplicate, so a reconnect/repeated poll cannot duplicate a wake).
        """
        _aware(observed_at, "live transport poll time")
        self._require_source_ready(observed_at)
        rows = self._read_rows()
        previous_watermark = self._tracker.watermark_start
        bars = self._tracker.poll(rows, observed_at=observed_at)
        if not bars:
            return TransportPollResult(bars=(), consumer_result=None)
        try:
            result = self._consumer.process_closed_minutes(bars, observed_at=observed_at)
        except Exception:
            self._tracker.restore_watermark(previous_watermark)
            raise
        return TransportPollResult(bars=bars, consumer_result=result)

    # ------------------------------------------------------------- internal

    def _read_rows(self) -> tuple[Mapping[str, object], ...]:
        read = getattr(self._source, "read_recent_1m_rows", None)
        if not callable(read):
            raise ValueError("LIVE_TRANSPORT_SOURCE_MISSING_READ")
        rows = read(symbol=self._symbol, limit=self._source_poll_limit)
        if not isinstance(rows, (tuple, list)):
            raise ValueError("live 1m source must return a sequence of kline rows")
        return tuple(rows)

    def _require_source_ready(self, observed_at: datetime) -> None:
        connected = getattr(self._source, "connected", None)
        if connected is not True:
            raise RuntimeError("PAPER_TRANSPORT_SOURCE_DISCONNECTED")
        if self._max_source_age_seconds is None:
            if self._require_source_freshness:
                raise RuntimeError("PAPER_TRANSPORT_SOURCE_FRESHNESS_POLICY_UNBOUND")
            return
        last_activity = getattr(self._source, "last_activity_at", None)
        last: datetime | None = None
        if callable(last_activity):
            last = last_activity()
        if last is None:
            raise RuntimeError("PAPER_TRANSPORT_SOURCE_FRESHNESS_UNPROVABLE")
        _aware(last, "live transport source activity time")
        age = observed_at - last
        if age.total_seconds() < 0:
            raise RuntimeError("PAPER_TRANSPORT_SOURCE_ACTIVITY_IN_FUTURE")
        if age > timedelta(seconds=self._max_source_age_seconds):
            raise RuntimeError("PAPER_TRANSPORT_SOURCE_STALE")


def _aware(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


__all__ = [
    "LiveOneMinuteSource",
    "LiveSessionCalendarResolver",
    "PAPER_LIVE_TRANSPORT_VERSION",
    "PaperLiveOneMinuteTransport",
    "TransportConsumer",
    "TransportPollResult",
]
