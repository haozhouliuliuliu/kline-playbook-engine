#!/usr/bin/env python3
"""Owner-workstation PAPER runtime CLI entrypoint.

OFFLINE ENGINEERING ONLY. This is the single clear local entrypoint for eventual
PAPER use. Current required behavior:

- default mode is preflight-only and NEVER bypasses authority;
- no implicit account login;
- no implicit credential loading;
- no DeepSeek/provider call merely to inspect/preflight;
- ``--preflight`` runs a machine-clear preflight (real external profile is
  fail-closed/BLOCKED today);
- ``--offline-rehearsal`` runs the deterministic fake activation rehearsal
  (no real account/order/provider action);
- a future external run reaches consequential operations only through the
  existing PAPER authority/activation-profile gates (which are inactive in
  current canonical state, so external connect/order remains BLOCKED).

The Owner workstation is Windows-first; the script keeps ordinary cross-platform
Python compatibility. No installer, Docker stack, web service or deployment
platform is involved.
"""
from __future__ import annotations

import argparse
import importlib
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
    run_offline_activation_rehearsal,
)
from src.paper_preflight import EXTERNAL, run_paper_preflight
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_runtime_layout import PaperRuntimeLayout


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-root", required=True, help="explicit PAPER runtime state root")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--preflight",
        action="store_true",
        help="run preflight only (default); never reaches broker/account/provider",
    )
    mode.add_argument(
        "--offline-rehearsal",
        action="store_true",
        help="run the deterministic fake offline activation rehearsal (fakes only)",
    )
    mode.add_argument(
        "--external-run",
        action="store_true",
        help="run an explicitly supplied external PAPER composition",
    )
    parser.add_argument("--config-id", default="PAPER_RUNTIME_CLI_CONFIG")
    parser.add_argument("--trader-identity", default=TRADER_IDENTITY)
    parser.add_argument("--concrete-contract")
    parser.add_argument("--product")
    parser.add_argument("--exchange")
    parser.add_argument("--tqsdk-runtime-version", default=RUNTIME_VERSION)
    parser.add_argument("--broker-kind", default="TQSDK_CANDIDATE")
    parser.add_argument("--account-kind", default="TQSDK_PAPER")
    parser.add_argument("--symbol")
    parser.add_argument("--source-poll-limit", type=int, default=512)
    parser.add_argument("--max-source-age-seconds", type=int, default=None)
    parser.add_argument("--json", action="store_true", help="emit a JSON document")
    parser.add_argument("--bindings-module", help="explicit local external composition module")
    parser.add_argument("--max-polls", type=int, default=None)
    return parser


def _config_from_args(args: argparse.Namespace) -> PaperRuntimeConfig:
    # EXTERNAL runs never bind an authority/profile implicitly; they remain
    # fail-closed until an explicit future activation binds them.
    offline = bool(args.offline_rehearsal)
    contract = args.concrete_contract or (CONTRACT if offline else None)
    product = args.product or (PRODUCT if offline else None)
    exchange = args.exchange or (EXCHANGE if offline else None)
    symbol = args.symbol or (INSTRUMENT if offline else None)
    missing = [
        name for name, value in (
            ("--concrete-contract", contract),
            ("--product", product),
            ("--exchange", exchange),
            ("--symbol", symbol),
        ) if value is None
    ]
    if missing:
        raise ValueError("external PAPER configuration requires " + ", ".join(missing))
    return PaperRuntimeConfig(
        config_id=args.config_id,
        state_root=Path(args.state_root),
        trader_identity=args.trader_identity,
        concrete_contract_id=contract,
        product=product,
        exchange=exchange,
        tqsdk_runtime_version=args.tqsdk_runtime_version,
        broker_kind=args.broker_kind,
        account_kind=args.account_kind,
        symbol=symbol,
        source_poll_limit=args.source_poll_limit,
        max_source_age_seconds=args.max_source_age_seconds,
    )


def _run_preflight(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
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
        mode=EXTERNAL,
    )
    if args.json:
        print(json.dumps({
            "mode": report.mode,
            "overall": report.overall,
            "ready": report.ready,
            "checks": [
                {"name": check.name, "status": check.status, "detail": check.detail}
                for check in report.checks
            ],
        }, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        for line in report.public_lines():
            print(line)
    return 0 if report.ready else 1


def _run_offline_rehearsal(args: argparse.Namespace) -> int:
    config = _config_from_args(args)
    # Offline-rehearsal explicitly binds the deterministic rehearsal fakes so
    # the same startup surfaces (preflight, connect, order) can be exercised
    # with no real account/order/provider action.
    config = config.bind_activation_profile(rehearsal_profile()).bind_authority(rehearsal_authority())
    result = run_offline_activation_rehearsal(state_root=config.state_root, config=config)
    if args.json:
        print(json.dumps({
            "passed": result.passed,
            "steps": [{"step": step, "status": status} for step, status in result.steps],
            "checks": list(result.checks),
            "wake_count_after_restart": result.wake_count_after_restart,
            "order_count_after_restart": result.order_count_after_restart,
        }, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        for line in result.public_lines():
            print(line)
    return 0 if result.passed else 1


def _run_external(args: argparse.Namespace) -> int:
    if not args.bindings_module:
        raise ValueError("--external-run requires --bindings-module")
    requested_config = _config_from_args(args)
    module = importlib.import_module(args.bindings_module)
    build_setup = getattr(module, "build_paper_external_setup", None)
    if not callable(build_setup):
        raise ValueError("bindings module must expose build_paper_external_setup")
    setup = build_setup(
        state_root=Path(args.state_root),
        arguments={key: value for key, value in vars(args).items() if key != "bindings_module"},
    )
    if not isinstance(setup, tuple) or len(setup) != 3:
        raise TypeError("external setup must return (config, layout, factories)")
    config, layout, factories = setup
    if not isinstance(config, PaperRuntimeConfig):
        raise TypeError("external setup config must be PaperRuntimeConfig")
    requested_identity = (
        requested_config.concrete_contract_id,
        requested_config.product,
        requested_config.exchange,
        requested_config.symbol,
    )
    actual_identity = (
        config.concrete_contract_id,
        config.product,
        config.exchange,
        config.symbol,
    )
    if actual_identity != requested_identity:
        raise ValueError("PAPER_EXTERNAL_SETUP_CONTRACT_IDENTITY_MISMATCH")
    from datetime import datetime
    from zoneinfo import ZoneInfo
    from src.paper_external_composition import build_external_paper_controller

    controller = build_external_paper_controller(
        config=config, layout=layout, factories=factories
    )
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    try:
        controller.start(at=now)
        controller.run_loop(
            observed_at_provider=lambda: datetime.now(ZoneInfo("Asia/Shanghai")),
            max_polls=args.max_polls,
        )
    finally:
        controller.shutdown(
            at=datetime.now(ZoneInfo("Asia/Shanghai")),
            persist_checkpoint=controller.assembly.context_builder.bootstrap_done,
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.offline_rehearsal:
        return _run_offline_rehearsal(args)
    if args.external_run:
        return _run_external(args)
    return _run_preflight(args)


if __name__ == "__main__":
    sys.exit(main())
