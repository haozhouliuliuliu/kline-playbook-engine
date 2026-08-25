#!/usr/bin/env python3
"""Deterministically build/check the offline Stage-A V0.3 capability-first plan."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_v03_plan import (  # noqa: E402
    DEFAULT_OUTPUT,
    build_v03_frozen_plan,
    pretty_plan_bytes,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = pretty_plan_bytes(build_v03_frozen_plan())
    if args.check:
        if not args.output.exists():
            raise SystemExit(f"frozen V0.3 plan is missing: {args.output}")
        if args.output.read_bytes() != expected:
            raise SystemExit("frozen Stage-A V0.3 plan differs from deterministic rebuild")
        print("STAGE_A_FROZEN_PLAN_V0_3_CHECK=PASS")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(expected)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
