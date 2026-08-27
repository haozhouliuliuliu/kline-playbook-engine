"""Shared frozen causal-context semantic constants for replay and live PAPER.

Single canonical source for the four-timeframe observation semantics so
historical replay (``replay_v0_1_causal_context``) and future real-time PAPER
(``paper_live_causal_context``) cannot silently drift apart on bucket/aggregation
parameters at the same causal information cutoff.

The exact Owner-approved semantic labels (contiguous-window lower grid, the
Asia/Shanghai civil 4H grid and the 4H role) are frozen and shared. Per-surface
schema/context *version* strings remain intentionally local to each
implementation because their identity documents are distinct.
"""

from __future__ import annotations

# Lower timeframes: each contiguous official session window starts a fresh
# bucket; a session break disconnects immediately; a shortened trailing bucket
# is never a complete bar.  ``SESSION_AUTHORITY_CONTIGUOUS_WINDOW_GRID_V0_1``.
LOWER_AGGREGATION_VERSION = "SESSION_AUTHORITY_CONTIGUOUS_WINDOW_GRID_V0_1"

# 4H: Asia/Shanghai civil 4-hour grid (``floor(hour/4)*4``); only official
# trading minutes of one official trading day inside that grid; lunch-break
# minutes are not missing minutes; no cross official trading day; a bar is
# complete only when all its official minutes have ended and are causally
# visible.  ``SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1``.
FOUR_HOUR_AGGREGATION_VERSION = "SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1"

FOUR_HOUR_ROLE = "BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY"

# Owner-approved four-timeframe bounded input shape.
ACTIVE_TIMEFRAMES = ("4H", "1H", "15m", "5m")
CONTEXT_WINDOW_COUNTS = {"4H": 2, "1H": 3, "15m": 12, "5m": 36}
LOWER_TIMEFRAME_PERIODS = {"5m": 5, "15m": 15, "1H": 60}

FOUR_HOUR_CIVIL_GRID_HOURS = 4

__all__ = [
    "ACTIVE_TIMEFRAMES",
    "CONTEXT_WINDOW_COUNTS",
    "FOUR_HOUR_AGGREGATION_VERSION",
    "FOUR_HOUR_CIVIL_GRID_HOURS",
    "FOUR_HOUR_ROLE",
    "LOWER_AGGREGATION_VERSION",
    "LOWER_TIMEFRAME_PERIODS",
]
