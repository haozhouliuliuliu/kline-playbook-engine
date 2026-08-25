#!/usr/bin/env python3
"""Seal the exact outcome-blind V0.1 replay slice from the accepted local corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.replay_v0_1_exact_slice import select_and_seal_exact_v0_1_slice


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Select and seal the exact SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1 slice."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPO_ROOT / "data/canonical/manifest.json",
        help="Accepted local canonical manifest (default: data/canonical/manifest.json).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional JSON seal output path. Write is atomic.",
    )
    return parser


def main() -> int:
    args = _parser().parse_args()
    seal = select_and_seal_exact_v0_1_slice(
        manifest_path=args.manifest,
        trading_calendar_path=REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json",
        session_schedule_path=REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json",
        e07_path=REPO_ROOT / "docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json",
        corpus_identity_path=REPO_ROOT / "docs/evidence/CANONICAL_CORPUS_IDENTITY.json",
    )
    payload = json.dumps(seal.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_name(output.name + ".partial")
        try:
            partial.write_text(payload, encoding="utf-8")
            partial.replace(output)
        finally:
            if partial.exists():
                partial.unlink()
    sys.stdout.write(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
