#!/usr/bin/env python3
"""Offline Stage-A budget diagnostic; no credentials and no network."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.build_jianghe_stage_a_plan as base  # noqa: E402
from src.jianghe_stage_a_frozen_stimulus import build_frozen_stage_a_stimulus  # noqa: E402


base.build_stage_a_stimulus = build_frozen_stage_a_stimulus
base.STAGE_A_PROVIDER_CAP_CNY = Decimal("999")
base.STAGE_A_TOTAL_CAP_CNY = Decimal("2997")

plan = base.build_plan()
for provider in plan["providers"]:
    print(
        provider["provider_id"],
        provider["model_id"],
        "five_slot_worst_case_cny=",
        provider["five_slot_worst_case_cny"],
    )
    for slot in provider["slots"]:
        print(
            " ",
            slot["slot"],
            slot["track"],
            "worst_case_cny=",
            slot["worst_case_cny"],
            "text_bound=",
            slot["bounds"]["max_text_input_tokens"],
            "image_bound=",
            slot["bounds"]["max_image_tokens"],
            "output_bound=",
            slot["bounds"]["max_output_tokens"],
        )
