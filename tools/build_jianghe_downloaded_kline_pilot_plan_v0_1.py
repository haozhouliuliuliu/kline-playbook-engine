#!/usr/bin/env python3
"""Build or verify the frozen five-sample downloaded-Kline pilot plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_downloaded_kline_pilot import build_plan, pretty_plan_bytes, verify_plan

DEFAULT_DATA_ROOT = Path(r"C:\Users\H\Documents\kline-playbook-engine\data\canonical")
DEFAULT_OUTPUT = ROOT / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_PLAN_V0_1.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        plan = json.loads(args.output.read_text(encoding="utf-8"))
        print(json.dumps({"pilot_plan_identity": verify_plan(plan), "sample_count": len(plan["samples"]), "check": "PASS"}, sort_keys=True))
        return
    plan = build_plan(args.data_root, ROOT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(pretty_plan_bytes(plan))
    print(json.dumps({"pilot_plan_identity": plan["pilot_plan_identity"], "sample_count": len(plan["samples"]), "output": str(args.output)}, sort_keys=True))


if __name__ == "__main__":
    main()
