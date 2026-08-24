#!/usr/bin/env python3
"""Build/check the Stage-A plan using the frozen compact visual presentation.

The underlying plan builder, bar recipe, request isolation and budget arithmetic
remain unchanged. This wrapper only freezes which deterministic visual stimulus
is bound before the first paid call.
"""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.build_jianghe_stage_a_plan as base  # noqa: E402
from src.jianghe_stage_a_frozen_stimulus import build_frozen_stage_a_stimulus  # noqa: E402


base.build_stage_a_stimulus = build_frozen_stage_a_stimulus


if __name__ == "__main__":
    raise SystemExit(base.main())
