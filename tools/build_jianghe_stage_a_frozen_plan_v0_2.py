#!/usr/bin/env python3
"""Deterministically build/check the offline Stage-A V0.2 frozen plan."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
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
from src.jianghe_stage_a_runtime import STAGE_A_REQUEST_VERSION  # noqa: E402


DEFAULT_OUTPUT = ROOT / "docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_2.json"
V0_1_PLAN_PATH = ROOT / "docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_1.json"
PROMPT_PATH = ROOT / "docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_2.json"
OWNER_DECISION_PATH = ROOT / "docs/reviews/JIANGHE_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_OWNER_DECISION.md"
PLAN_AS_OF = datetime(2026, 8, 24, 9, 14, tzinfo=timezone.utc)
V0_1_PLAN_IDENTITY = "7d6a1838962345c36dd3449f27adfd6c7d18c4988b5e3e2cb4bc65acb52b2fd4"
ATTEMPT_001_EVIDENCE_IDENTITY = "d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55"
CARRY_FORWARD_CNY = Decimal("0.219222")


def _compact_frozen_stimulus(plan: dict[str, object]) -> None:
    stimulus = plan.get("stimulus")
    if not isinstance(stimulus, dict):
        raise ValueError("Stage-A V0.2 stimulus is malformed")
    rows = stimulus.pop("fine_5m_bars", None)
    if not isinstance(rows, list) or len(rows) != FROZEN_STAGE_A_FINE_BAR_COUNT:
        raise ValueError("Stage-A V0.2 frozen fine-bar recipe is wrong-sized")
    first, poke, last = rows[0], rows[20], rows[-1]
    source_path = ROOT / "src/jianghe_stage_a_frozen_stimulus.py"
    stimulus.update({
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
        "recipe_source_path": "src/jianghe_stage_a_frozen_stimulus.py",
        "recipe_source_sha256": sha256(base._repository_blob_bytes(source_path)).hexdigest(),
        "recipe_materialization": "DETERMINISTIC_COMMITTED_SOURCE_PLUS_RECIPE_IDENTITY",
    })


def build_frozen_plan() -> dict[str, object]:
    base.PLAN_AS_OF = PLAN_AS_OF
    base.MAX_OUTPUT_TOKENS = 1024
    base.REQUEST_CONTRACT_VERSION = STAGE_A_REQUEST_VERSION
    base.PROMPT_PACKAGE_PATH = PROMPT_PATH
    base.PROTOCOL_AUTHORITY_PATH = OWNER_DECISION_PATH
    base.STAGE_A_PLAN_VERSION = "JIANGHE_STAGE_A_FROZEN_PLAN_V0_2"
    base.STAGE_A_PROTOCOL_VERSION = "JIANGHE_STAGE_A_PROVIDER_RESPONSE_COMPATIBILITY_V0_2"
    base.build_stage_a_stimulus = build_frozen_stage_a_stimulus
    plan = base.build_plan()
    _compact_frozen_stimulus(plan)

    old_blob = base._repository_blob_bytes(V0_1_PLAN_PATH)
    old_plan = json.loads(old_blob.decode("utf-8"))
    if old_plan.get("plan_identity") != V0_1_PLAN_IDENTITY:
        raise ValueError("V0.1 frozen plan identity drifted")
    old_deepseek_slot_1 = old_plan["providers"][1]["slots"][0]

    future_count = 0
    stage_total = Decimal("0")
    for provider in plan["providers"]:
        provider_id = provider["provider_id"]
        future_total = Decimal("0")
        for slot in provider["slots"]:
            executable = not (provider_id == "DEEPSEEK" and slot["slot"] == 1)
            slot["future_executable"] = executable
            if executable:
                slot["execution_semantics"] = "FUTURE_UNATTEMPTED"
                future_count += 1
                future_total += Decimal(slot["worst_case_cny"])
            else:
                slot.clear()
                slot.update({
                    "slot": 1,
                    "track": "OPERATIONAL_PROVIDER",
                    "fixture_id": "JH-FIX-C-001",
                    "future_executable": False,
                    "execution_semantics": "CARRY_FORWARD_V0_1_ATTEMPT__NON_EXECUTABLE__NON_RETRYABLE",
                    "request_identity": old_deepseek_slot_1["request_identity"],
                    "payload_sha256": old_deepseek_slot_1["payload_sha256"],
                    "inference_configuration_identity": old_deepseek_slot_1["inference_configuration_identity"],
                    "worst_case_cny": "0.219222",
                    "attempt_evidence_identity": ATTEMPT_001_EVIDENCE_IDENTITY,
                })
        total = future_total + (CARRY_FORWARD_CNY if provider_id == "DEEPSEEK" else Decimal("0"))
        provider["future_executable_worst_case_cny"] = base._decimal_text(future_total)
        provider["total_stage_a_worst_case_including_carry_forward_cny"] = base._decimal_text(total)
        provider["five_slot_worst_case_cny"] = base._decimal_text(total)
        if total > Decimal("6"):
            raise ValueError(f"{provider_id} V0.2 total exceeds frozen CNY6 cap: {total}")
        stage_total += total

    if future_count != 14:
        raise ValueError("V0.2 must expose exactly 14 future executable slots")
    if stage_total > Decimal("18"):
        raise ValueError("V0.2 total exceeds frozen CNY18 cap")
    plan.update({
        "status": "FROZEN_V0_2_OFFLINE__REMOTE_BOOTSTRAP_PENDING_AFTER_MERGE",
        "max_output_tokens_per_call": 1024,
        "max_total_stage_a_calls": 15,
        "future_executable_call_count": future_count,
        "stage_a_total_worst_case_including_carry_forward_cny": base._decimal_text(stage_total),
        "v0_1_plan_identity": V0_1_PLAN_IDENTITY,
        "v0_1_plan_blob_sha256": sha256(old_blob).hexdigest(),
        "v0_1_remote_ref": "refs/heads/stage-a-live-state-v0-1",
        "v0_2_remote_ref": "refs/heads/stage-a-live-state-v0-2",
        "caller_selected_remote_ref": "FORBIDDEN",
        "carry_forward": {
            "live_calls": 1,
            "project_accounted_cny": "0.219222",
            "stage_accounted_cny": "0.219222",
            "provider_accounted_cny": {"DEEPSEEK": "0.219222"},
            "provider_attempts": {"DEEPSEEK": 1},
            "attempted_slots": ["DEEPSEEK:1"],
            "attempt_001_evidence_identity": ATTEMPT_001_EVIDENCE_IDENTITY,
            "automatic_retry": "FORBIDDEN",
            "replacement_call": "FORBIDDEN"
        },
    })
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
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != expected:
            raise SystemExit("frozen Stage-A V0.2 plan differs from deterministic rebuild")
        print("STAGE_A_FROZEN_PLAN_V0_2_CHECK=PASS")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
