#!/usr/bin/env python3
"""Check Stage-A provider credential/existing-balance readiness without model calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_provider_readiness import (  # noqa: E402
    READY_EXISTING_FUNDS,
    check_all_provider_readiness,
    check_provider_readiness,
)
from src.jianghe_stage_a_runner import FROZEN_PLAN_PATH, VerifiedFrozenStageAPlan  # noqa: E402
from tools.build_jianghe_stage_a_frozen_plan_v0_2 import build_frozen_plan  # noqa: E402


def _pretty_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider",
        choices=("KIMI", "DEEPSEEK", "MINIMAX"),
        help="check one provider; omit to check all three",
    )
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    args = parser.parse_args()

    plan = VerifiedFrozenStageAPlan.load(
        committed_path=FROZEN_PLAN_PATH,
        deterministic_rebuild_bytes=_pretty_bytes(build_frozen_plan()),
    )
    if args.provider:
        results = (
            check_provider_readiness(
                plan,
                provider_id=args.provider,
                timeout_seconds=args.timeout_seconds,
            ),
        )
    else:
        results = check_all_provider_readiness(
            plan,
            timeout_seconds=args.timeout_seconds,
        )

    payload = {
        "artifact_schema_version": "JIANGHE_PROVIDER_BALANCE_READINESS_REPORT_V0_1",
        "frozen_plan_identity": plan.plan_identity,
        "model_endpoint_called": False,
        "credential_value_exposed": False,
        "providers": [item.to_dict() for item in results],
        "all_providers_ready_from_existing_funds": all(
            item.status == READY_EXISTING_FUNDS for item in results
        ),
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if payload["all_providers_ready_from_existing_funds"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
