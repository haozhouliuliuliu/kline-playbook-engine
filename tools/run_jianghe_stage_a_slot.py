#!/usr/bin/env python3
"""Execute exactly one frozen Jianghe Stage-A slot.

This command is intentionally single-slot. It verifies the committed frozen plan
against a deterministic rebuild before touching credentials, uses a persistent
hash-chained attempt journal, and never retries a started slot automatically.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_stage_a_runner import (  # noqa: E402
    DEFAULT_STATE_DIR,
    FROZEN_PLAN_PATH,
    StageAExecutionJournal,
    StageAExecutionLock,
    VerifiedFrozenStageAPlan,
    execute_frozen_slot,
)
from tools.build_jianghe_stage_a_frozen_plan_v0_2 import build_frozen_plan  # noqa: E402


def _pretty_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--provider", required=True, choices=("KIMI", "DEEPSEEK", "MINIMAX")
    )
    parser.add_argument("--slot", required=True, type=int, choices=range(1, 6))
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    args = parser.parse_args()

    plan = VerifiedFrozenStageAPlan.load(
        committed_path=FROZEN_PLAN_PATH,
        deterministic_rebuild_bytes=_pretty_bytes(build_frozen_plan()),
    )
    state_dir = args.state_dir.resolve()
    journal = StageAExecutionJournal(state_dir / "journal.jsonl", plan)
    lock_path = state_dir / "execution.lock"

    with StageAExecutionLock(lock_path):
        result = execute_frozen_slot(
            plan,
            journal,
            provider_id=args.provider,
            slot=args.slot,
            now=datetime.now(timezone.utc),
        )

    summary = {
        "provider_id": result.provider_id,
        "slot": result.slot,
        "status": result.status,
        "accounted_cny": format(Decimal(result.accounted_cny), "f"),
        "provider_evidence_identity": result.provider_evidence_identity,
        "normalized_decision_identity": result.normalized_decision_identity,
        "terminal_event_identity": result.terminal_event_identity,
        "credential_value_exposed": False,
        "automatic_retry": "FORBIDDEN",
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if result.status == "SUCCESS_NORMALIZED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
