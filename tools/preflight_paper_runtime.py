#!/usr/bin/env python3
"""PAPER startup preflight tool — machine-clear READY/BLOCKED facts.

OFFLINE ONLY. This tool runs the project-owned PAPER preflight BEFORE any
external connection. It performs no login, no credential read, no provider call,
no network action and no order/broker mutation. It prints machine-clear facts
without any secret values.

Current canonical project state has NO active PAPER connection/order authority,
so a real ``EXTERNAL`` preflight with no bound ACTIVE authority/profile reports
BLOCKED. That is correct. An explicit ``--mode offline-rehearsal`` binds
deterministic fake ACTIVE objects (fakes only) and may report READY to prove the
startup surface.

Usage examples (Windows-first, cross-platform Python):

    python tools/preflight_paper_runtime.py --state-root C:\\kpe-paper-state
    python tools/preflight_paper_runtime.py --state-root .\\state --mode offline-rehearsal
    python tools/preflight_paper_runtime.py --state-root .\\state --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.paper_offline_activation_rehearsal import (
    CONTRACT,
    EXCHANGE,
    INSTRUMENT,
    PRODUCT,
    RUNTIME_VERSION,
    TRADER_IDENTITY,
    rehearsal_authority,
    rehearsal_profile,
)
from src.paper_preflight import EXTERNAL, OFFLINE_REHEARSAL, run_paper_preflight
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_runtime_layout import PaperRuntimeLayout


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", required=True, help="explicit PAPER runtime state root")
    parser.add_argument(
        "--mode",
        choices=(EXTERNAL, OFFLINE_REHEARSAL, "external", "offline-rehearsal"),
        default=EXTERNAL,
        help="EXTERNAL (real, fail-closed today) or OFFLINE_REHEARSAL (fakes, may pass)",
    )
    parser.add_argument("--config-id", default="PAPER_PREFLIGHT_CONFIG")
    parser.add_argument("--trader-identity", default=TRADER_IDENTITY)
    parser.add_argument("--concrete-contract", default=CONTRACT)
    parser.add_argument("--product", default=PRODUCT)
    parser.add_argument("--exchange", default=EXCHANGE)
    parser.add_argument("--tqsdk-runtime-version", default=RUNTIME_VERSION)
    parser.add_argument("--broker-kind", default="TQSDK_CANDIDATE")
    parser.add_argument("--account-kind", default="TQSDK_PAPER")
    parser.add_argument("--symbol", default=INSTRUMENT)
    parser.add_argument("--source-poll-limit", type=int, default=512)
    parser.add_argument("--max-source-age-seconds", type=int, default=None)
    parser.add_argument("--json", action="store_true", help="emit a JSON document")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    mode = args.mode.upper().replace("-", "_")
    config = PaperRuntimeConfig(
        config_id=args.config_id,
        state_root=Path(args.state_root),
        trader_identity=args.trader_identity,
        concrete_contract_id=args.concrete_contract,
        product=args.product,
        exchange=args.exchange,
        tqsdk_runtime_version=args.tqsdk_runtime_version,
        broker_kind=args.broker_kind,
        account_kind=args.account_kind,
        symbol=args.symbol,
        source_poll_limit=args.source_poll_limit,
        max_source_age_seconds=args.max_source_age_seconds,
    )
    if mode == OFFLINE_REHEARSAL:
        config = config.bind_activation_profile(rehearsal_profile()).bind_authority(rehearsal_authority())

    layout = PaperRuntimeLayout(
        state_root=config.state_root,
        trader_identity=config.trader_identity,
        concrete_contract_id=config.concrete_contract_id,
        config_identity=config.stable_identity,
    )
    report = run_paper_preflight(
        config=config,
        layout=layout,
        activation_profile=config.activation_profile,
        authority=config.authority,
        assembly=None,
        mode=mode,
    )

    if args.json:
        payload = {
            "schema_version": "KPE_PAPER_PREFLIGHT_CLI_V0_1",
            "mode": report.mode,
            "overall": report.overall,
            "ready": report.ready,
            "checks": [
                {"name": check.name, "status": check.status, "detail": check.detail}
                for check in report.checks
            ],
            "config": config.to_public_document(),
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        for line in report.public_lines():
            print(line)

    return 0 if report.ready else 1


if __name__ == "__main__":
    sys.exit(main())
