#!/usr/bin/env python3
"""Execute exactly one frozen Jianghe downloaded-Kline Final-Chance V0.2 slot.

This runner is deliberately single-slot: one provider x one frozen case x one
explicit frozen attempt/slot per invocation. It never batches the 12 slots,
never retries, never advances to a next slot, never falls back to another
provider/model, never modifies the payload or case, and never touches
outcome / future / validation / holdout / shadow / broker / real-money lanes.

Every fail-closed gate runs before any network attempt:

* A: materialized plan identity + plan-file SHA-256 equal the frozen authority;
* B: the requested case exists in the frozen materialized plan;
* C: provider/model equal the frozen slot provider/model;
* D: payload / image / prompt / structured-artifact identities equal the plan;
* E: a formal explicit-slot authority is required (``NEXT_EXPLICIT_PAID_SLOT``
  must not be ``NONE``);
* F: an already-successful attempt is never re-executed;
* G: network timeout / HTTP failure / malformed JSON record failure evidence and
  stop (no automatic retry).

``--dry-run`` runs the full preflight (all gates) and produces no network request.
"""

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

from src.jianghe_final_chance_live_lane import (  # noqa: E402
    FinalChanceError,
    FinalChanceGateError,
    FinalChanceGitRemoteLedgerStore,
    FinalChanceSlotAuthorityError,
    FINAL_CHANCE_REMOTE_REF,
    execute_final_chance_slot,
    load_final_chance_explicit_slot_authority,
    load_verified_final_chance_plan,
    preflight_final_chance_slot,
)

PROVIDER_CHOICES = ("DEEPSEEK", "MINIMAX", "KIMI")
SAMPLE_CHOICES = ("DKL-FC-001", "DKL-FC-002", "DKL-FC-003", "DKL-FC-004")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute exactly one frozen Jianghe downloaded-Kline Final-Chance V0.2 slot"
    )
    parser.add_argument("--provider", required=True, choices=PROVIDER_CHOICES)
    parser.add_argument("--sample-id", required=True, choices=SAMPLE_CHOICES)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="run every fail-closed pre-send gate and print a report without any network request",
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    try:
        plan = load_verified_final_chance_plan()
        slot_authority = load_final_chance_explicit_slot_authority()
        if slot_authority is None:
            raise FinalChanceGateError(
                "NEXT_EXPLICIT_PAID_SLOT=NONE; no committed explicit-slot authority exists; "
                "refusing to send"
            )
        if args.dry_run:
            result = preflight_final_chance_slot(
                plan=plan,
                provider_id=args.provider,
                sample_id=args.sample_id,
                now=now,
                slot_authority=slot_authority,
                store=FinalChanceGitRemoteLedgerStore(repository=ROOT, remote_ref=FINAL_CHANCE_REMOTE_REF),
            )
            print(
                json.dumps(
                    {
                        "mode": "dry-run",
                        "provider_id": result.provider_id,
                        "sample_id": result.sample_id,
                        "slot_identity": result.slot_identity,
                        "passed": result.passed,
                        "gates": dict(result.gates),
                        "worst_case_reservation_cny": result.worst_case_reservation_cny,
                        "shared_accounted_cny": result.shared_accounted_cny,
                        "remaining_cny": result.remaining_cny,
                        "network_request_made": False,
                        "credential_value_exposed": False,
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
            return 0

        store = FinalChanceGitRemoteLedgerStore(repository=ROOT, remote_ref=FINAL_CHANCE_REMOTE_REF)
        result = execute_final_chance_slot(
            provider_id=args.provider,
            sample_id=args.sample_id,
            now=now,
            store=store,
            slot_authority=slot_authority,
            credential_lookup=os.environ.get,
        )
        print(
            json.dumps(
                {
                    "provider_id": result.provider_id,
                    "sample_id": result.sample_id,
                    "slot_identity": result.slot_identity,
                    "status": result.status,
                    "accounted_cny": format(result.accounted_cny, "f"),
                    "evidence_identity": result.evidence_identity,
                    "remote_start_head": result.remote_start_head,
                    "remote_terminal_head": result.remote_terminal_head,
                    "dry_run": False,
                    "automatic_retries": result.automatic_retries,
                    "automatic_next_slots": result.automatic_next_slots,
                    "credential_value_exposed": False,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0 if result.status in {"CAPABILITY_SCOREABLE", "CAPABILITY_NOT_SCOREABLE"} else 2
    except FinalChanceSlotAuthorityError as error:
        print(json.dumps({"error": "EXPLICIT_SLOT_AUTHORITY_INVALID", "detail": str(error)}, ensure_ascii=False, sort_keys=True))
        return 3
    except FinalChanceGateError as error:
        print(json.dumps({"error": "FAIL_CLOSED_GATE", "detail": str(error)}, ensure_ascii=False, sort_keys=True))
        return 4
    except FinalChanceError as error:
        print(json.dumps({"error": "FINAL_CHANCE_ERROR", "detail": str(error)}, ensure_ascii=False, sort_keys=True))
        return 5
    except Exception as error:  # noqa: BLE001 - surface unexpected failures without secrets
        print(
            json.dumps(
                {"error": "UNEXPECTED", "detail": str(error), "credential_value_exposed": False},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 6


if __name__ == "__main__":
    raise SystemExit(main())
