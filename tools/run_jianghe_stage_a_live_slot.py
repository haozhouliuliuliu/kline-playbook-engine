#!/usr/bin/env python3
"""Run exactly one Stage-A slot behind the durable remote write-ahead lane."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_stage_a_evidence import load_verified_frozen_plan  # noqa: E402
from src.jianghe_stage_a_live_lane import execute_remote_reserved_slot  # noqa: E402
from src.jianghe_stage_a_remote_ledger import (  # noqa: E402
    DEFAULT_REMOTE_REF,
    GitRemoteLedgerStore,
)
from src.jianghe_stage_a_runner import DEFAULT_STATE_DIR, StageAExecutionLock  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, choices=("KIMI", "DEEPSEEK", "MINIMAX"))
    parser.add_argument("--slot", required=True, type=int, choices=range(1, 6))
    args = parser.parse_args()
    if args.provider == "DEEPSEEK" and args.slot == 1:
        parser.error("CARRY_FORWARD_ATTEMPTED__NON_RETRYABLE")

    plan = load_verified_frozen_plan()
    state_dir = DEFAULT_STATE_DIR.resolve()
    store = GitRemoteLedgerStore(
        repository=ROOT,
        remote="origin",
        remote_ref=DEFAULT_REMOTE_REF,
    )
    with StageAExecutionLock(state_dir / "execution.lock"):
        result = execute_remote_reserved_slot(
            plan=plan,
            store=store,
            state_dir=state_dir,
            provider_id=args.provider,
            slot=args.slot,
            now=datetime.now(timezone.utc),
            credential_lookup=os.environ.get,
        )
    print(
        json.dumps(
            {
                "provider_id": result.slot_result.provider_id,
                "slot": result.slot_result.slot,
                "status": result.slot_result.status,
                "accounted_cny": format(result.slot_result.accounted_cny, "f"),
                "evidence_identity": result.evidence_identity,
                "remote_start_head": result.remote_start_head,
                "remote_terminal_head": result.remote_terminal_head,
                "automatic_retry": "FORBIDDEN",
                "credential_value_exposed": False,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if result.slot_result.status == "SUCCESS_NORMALIZED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
