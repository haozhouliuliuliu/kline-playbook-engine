#!/usr/bin/env python3
"""Build/check the committed Stage-A frozen qualification plan.

The generic plan builder first computes every exact request, payload, budget bound
and the full synthetic 5m recipe. This wrapper binds the Owner-approved frozen
36-bar stimulus, then stores a compact manifest: the bar recipe itself remains
content-addressed by ``recipe_identity`` and by the exact committed stimulus-source
bytes, while semantic anchor/count/time summary fields make offline inspection
possible without duplicating all 36 bars into the plan artifact.

This tool is deterministic and offline. It never reads provider credentials and
never makes a network request.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tools.build_jianghe_stage_a_plan as base  # noqa: E402
from src.jianghe_stage_a_frozen_stimulus import (  # noqa: E402
    FROZEN_STAGE_A_15M_BAR_COUNT,
    FROZEN_STAGE_A_1H_BAR_COUNT,
    FROZEN_STAGE_A_FINE_BAR_COUNT,
    FROZEN_STAGE_A_WINDOW_VERSION,
    build_frozen_stage_a_stimulus,
)


FROZEN_STIMULUS_SOURCE_RELATIVE_PATH = "src/jianghe_stage_a_frozen_stimulus.py"
DEFAULT_OUTPUT = ROOT / "docs" / "evidence" / "JIANGHE_STAGE_A_FROZEN_PLAN_V0_1.json"


def build_frozen_plan() -> dict[str, object]:
    # Historical V0.1 rebuild stays pinned even though the current runtime is V0.2.
    base.PLAN_AS_OF = base.datetime(2026, 8, 24, 1, 3, tzinfo=base.timezone.utc)
    base.MAX_OUTPUT_TOKENS = 400
    base.REQUEST_CONTRACT_VERSION = "JIANGHE_STAGE_A_REQUEST_V0_1"
    base.PROMPT_PACKAGE_PATH = (
        ROOT / "docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json"
    )
    base.PROTOCOL_AUTHORITY_PATH = (
        ROOT / "docs/reviews/JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md"
    )
    base.STAGE_A_PLAN_VERSION = "JIANGHE_STAGE_A_FROZEN_PLAN_V0_1"
    base.STAGE_A_PROTOCOL_VERSION = "JIANGHE_STAGE_A_INPUT_PROTOCOL_V0_1"
    base.build_stage_a_stimulus = build_frozen_stage_a_stimulus
    plan = base.build_plan()
    stimulus = plan.get("stimulus")
    if not isinstance(stimulus, dict):
        raise ValueError("Stage-A plan stimulus section is malformed")
    rows = stimulus.pop("fine_5m_bars", None)
    if not isinstance(rows, list) or len(rows) != FROZEN_STAGE_A_FINE_BAR_COUNT:
        raise ValueError("Stage-A frozen fine-bar recipe is missing or wrong-sized")
    first, poke, last = rows[0], rows[20], rows[-1]
    if not all(isinstance(item, dict) for item in (first, poke, last)):
        raise ValueError("Stage-A frozen bar summary rows are malformed")
    if poke.get("high") != "103" or poke.get("close") != "101.1":
        raise ValueError("Stage-A frozen semantic anchor drifted")

    source_path = ROOT / FROZEN_STIMULUS_SOURCE_RELATIVE_PATH
    repository_source_bytes = base._repository_blob_bytes(source_path)
    stimulus.update(
        {
            "window_version": FROZEN_STAGE_A_WINDOW_VERSION,
            "fine_5m_bar_count": FROZEN_STAGE_A_FINE_BAR_COUNT,
            "derived_15m_bar_count": FROZEN_STAGE_A_15M_BAR_COUNT,
            "derived_1H_bar_count": FROZEN_STAGE_A_1H_BAR_COUNT,
            "fine_5m_first_open_time": first.get("open_time"),
            "fine_5m_last_close_time": last.get("close_time"),
            "semantic_anchor": {
                "pre_poke_5m_count": 20,
                "poke_5m_index": 20,
                "poke_high": poke.get("high"),
                "poke_close": poke.get("close"),
                "post_poke_5m_count": 15,
                "other_5m_highs_below": "102",
            },
            "recipe_source_path": FROZEN_STIMULUS_SOURCE_RELATIVE_PATH,
            "recipe_source_sha256": sha256(repository_source_bytes).hexdigest(),
            "recipe_materialization": "DETERMINISTIC_COMMITTED_SOURCE_PLUS_RECIPE_IDENTITY",
        }
    )
    plan.pop("plan_identity", None)
    plan["plan_identity"] = base._hash(plan)
    return plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = base._pretty(build_frozen_plan())
    if args.check:
        if not args.output.exists():
            raise SystemExit(f"frozen plan is missing: {args.output}")
        actual = args.output.read_text(encoding="utf-8")
        if actual != expected:
            raise SystemExit("frozen Stage-A plan differs from deterministic rebuild")
        print("STAGE_A_FROZEN_PLAN_CHECK=PASS")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
