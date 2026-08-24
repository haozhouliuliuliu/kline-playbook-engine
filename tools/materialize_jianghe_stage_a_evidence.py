#!/usr/bin/env python3
"""Materialize durable Stage-A attempt evidence from the local journal only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_stage_a_evidence import (  # noqa: E402
    materialize_stage_a_attempt_evidence,
)
from src.jianghe_stage_a_runner import (  # noqa: E402
    DEFAULT_STATE_DIR,
    StageAExecutionLock,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Materialize deterministic, credential-free Stage-A attempt evidence."
    )
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE_DIR)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    state_dir = args.state_dir.resolve()
    output_path = args.output.resolve()
    with StageAExecutionLock(state_dir / "execution.lock"):
        artifact = materialize_stage_a_attempt_evidence(
            state_dir=state_dir,
            output_path=output_path,
        )
    print(
        json.dumps(
            {
                "artifact_identity": artifact["artifact_identity"],
                "attempt_count": artifact["attempt_count"],
                "output": str(output_path),
                "automatic_retry": "FORBIDDEN",
                "network_calls": 0,
                "credential_value_exposed": False,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
