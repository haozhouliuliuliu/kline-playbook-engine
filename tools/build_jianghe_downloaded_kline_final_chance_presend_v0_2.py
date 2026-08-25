#!/usr/bin/env python3
"""Final-Chance V0.2 pre-send review tool (offline; creates no network call).

This is the only tool that may create the single explicit paid-slot authority for
the Jianghe downloaded-Kline Final-Chance V0.2 plan. It performs the full pre-send
review:

* verify the materialized plan (identity + file SHA-256);
* verify provider/model against the frozen plan;
* verify the Owner paid-call authorization authority;
* verify the shared CNY ledger authority (current project accounted carry-forward);
* accept/verify the current rate-card / pricing evidence for every provider;
* compute per-slot worst-case CNY reservations and verify the project hard cap;
* optionally generate exactly ONE explicit paid-slot authority.

Two modes:

``--check`` (default) performs the review only and reports
``next_explicit_paid_slot = NONE``. It writes nothing.

``--freeze-slot DKL_FC_V0_2:DEEPSEEK:DKL-FC-001`` performs every gate and then
writes the explicit-slot authority for exactly that slot to ``--output`` (default:
the committed authority path). Only the project brain may run this mode after
reviewing the report; it requires every gate to pass.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_final_chance_live_lane import (  # noqa: E402
    FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY,
    FINAL_CHANCE_REMOTE_REF,
    HARD_PROJECT_CAP_CNY,
    FinalChanceError,
    FinalChanceExplicitSlotAuthority,
    FinalChanceGateError,
    FinalChanceGitRemoteLedgerStore,
    build_final_chance_request,
    committed_plan_file_sha256,
    compute_final_chance_reservation,
    find_final_chance_slot_identity,
    load_verified_final_chance_plan,
    provider_spec_for,
)
from src.jianghe_prespend_runtime import load_current_repository_rate_card, load_owner_paid_call_authorization  # noqa: E402

SLOT_RE = __import__("re").compile(r"^DKL_FC_V0_2:(DEEPSEEK|MINIMAX|KIMI):(DKL-FC-00[1-4])$")
SLOT_AUTHORITY_OUTPUT = ROOT / "docs" / "evidence" / "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_EXPLICIT_SLOT_V0_2.json"


def _pretty_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def _verify_shared_ledger_authority():
    """Re-verify the shared ledger carry-forward against committed evidence."""
    from src.jianghe_final_chance_live_lane import _verify_shared_ledger_authority as verify
    return verify()


def _provider_and_sample(slot_identity: str) -> tuple[str, str]:
    match = SLOT_RE.fullmatch(slot_identity)
    if match is None:
        raise FinalChanceGateError(f"invalid final-chance slot identity {slot_identity}")
    return match.group(1), match.group(2)


def build_presend_review(*, now: datetime) -> dict[str, object]:
    """Run every pre-send gate and return a review report (no slot freeze)."""
    _require_aware(now)
    plan = load_verified_final_chance_plan()
    plan_file_sha256 = committed_plan_file_sha256()

    paid_auth = load_owner_paid_call_authorization(now=now)
    _verify_shared_ledger_authority()

    provider_reports = []
    total_worst = Decimal("0")
    for provider_id in plan.get("provider_order", []):
        spec = provider_spec_for(provider_id)
        rate_card = load_current_repository_rate_card(spec, now=now)
        if not paid_auth.permits(spec):
            raise FinalChanceGateError(f"paid authorization does not permit {provider_id}")
        slot_reports = []
        for sample in plan.get("samples", []):
            sample_id = str(sample["sample_id"])
            slot_identity = find_final_chance_slot_identity(plan, provider_id, sample_id)
            request, transport, config, _ = build_final_chance_request(
                plan, provider_id=provider_id, sample_id=sample_id, now=now
            )
            worst, image_bound = compute_final_chance_reservation(request, transport, config, rate_card)
            total_worst += worst
            slot_reports.append(
                {
                    "slot_identity": slot_identity,
                    "sample_id": sample_id,
                    "provider_id": provider_id,
                    "model_id": config.model_id,
                    "worst_case_reservation_cny": _decimal_text(worst),
                    "text_input_bound_tokens": transport.conservative_text_input_token_bound(request),
                    "image_input_bound_tokens": image_bound,
                    "max_output_tokens": config.max_output_tokens,
                    "rate_card_identity": rate_card.identity,
                }
            )
        provider_reports.append(
            {
                "provider_id": provider_id,
                "model_id": spec.model_id,
                "endpoint": spec.endpoint,
                "rate_card_identity": rate_card.identity,
                "rate_card_currency": rate_card.currency,
                "input_per_million": _decimal_text(rate_card.input_per_million),
                "output_per_million": _decimal_text(rate_card.output_per_million),
                "rate_card_effective_at": rate_card.effective_at.isoformat(),
                "rate_card_expires_at": rate_card.expires_at.isoformat(),
                "worst_case_total_cny": _decimal_text(
                    sum((Decimal(s["worst_case_reservation_cny"]) for s in slot_reports), Decimal("0"))
                ),
                "slots": slot_reports,
            }
        )

    # Shared ledger snapshot (final-chance remote ledger if it exists yet).
    store = FinalChanceGitRemoteLedgerStore(repository=ROOT, remote_ref=FINAL_CHANCE_REMOTE_REF)
    observed = store.load(str(plan["pilot_plan_identity"]), plan_file_sha256)
    snapshot = observed.ledger.snapshot()
    shared_accounted = snapshot.project_accounted_cny
    remaining = HARD_PROJECT_CAP_CNY - shared_accounted

    if shared_accounted + total_worst > HARD_PROJECT_CAP_CNY:
        raise FinalChanceGateError(
            "sum of worst-case reservations would exceed the CNY100 hard cap"
        )

    return {
        "artifact_schema_version": "JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PRESEND_REVIEW_V0_1",
        "reviewed_at": now.isoformat(),
        "pilot_id": plan["pilot_id"],
        "pilot_plan_identity": plan["pilot_plan_identity"],
        "plan_file_sha256": plan_file_sha256,
        "materialization_status": plan["status"],
        "paid_authorization_id": paid_auth.authorization_id,
        "paid_authorization_effective_at": paid_auth.effective_at.isoformat(),
        "paid_authorization_expires_at": paid_auth.expires_at.isoformat(),
        "shared_accounted_cny": _decimal_text(shared_accounted),
        "shared_ledger_historical_carry": _decimal_text(FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY),
        "hard_cap_cny": _decimal_text(HARD_PROJECT_CAP_CNY),
        "remaining_cny_after_shared": _decimal_text(remaining),
        "total_worst_case_all_slots_cny": _decimal_text(total_worst),
        "next_explicit_paid_slot": "NONE",
        "providers": provider_reports,
        "automatic_retry": "FORBIDDEN",
        "automatic_next_slot": "FORBIDDEN",
        "network_request_made": False,
        "credential_value_exposed": False,
    }


def build_explicit_slot_authority(*, slot_identity: str, now: datetime) -> FinalChanceExplicitSlotAuthority:
    """Build (and validate) the single explicit paid-slot authority for a slot."""
    _require_aware(now)
    provider_id, sample_id = _provider_and_sample(slot_identity)
    plan = load_verified_final_chance_plan()
    plan_file_sha256 = committed_plan_file_sha256()
    if find_final_chance_slot_identity(plan, provider_id, sample_id) != slot_identity:
        raise FinalChanceGateError("slot identity does not match the frozen plan")

    paid_auth = load_owner_paid_call_authorization(now=now)
    _verify_shared_ledger_authority()
    spec = provider_spec_for(provider_id)
    rate_card = load_current_repository_rate_card(spec, now=now)
    if not paid_auth.permits(spec):
        raise FinalChanceGateError(f"paid authorization does not permit {provider_id}")

    request, transport, config, _ = build_final_chance_request(
        plan, provider_id=provider_id, sample_id=sample_id, now=now
    )
    worst, _image_bound = compute_final_chance_reservation(request, transport, config, rate_card)

    store = FinalChanceGitRemoteLedgerStore(repository=ROOT, remote_ref=FINAL_CHANCE_REMOTE_REF)
    observed = store.load(str(plan["pilot_plan_identity"]), plan_file_sha256)
    snapshot = observed.ledger.snapshot()
    if slot_identity in snapshot.attempted_slots:
        raise FinalChanceGateError("slot is already attempted; freezing it again is forbidden")
    if snapshot.project_accounted_cny + worst > HARD_PROJECT_CAP_CNY:
        raise FinalChanceGateError("worst-case reservation would exceed the CNY100 hard cap")

    case_identity = None
    for binding in plan.get("common_case_bindings", []):
        if binding.get("sample_id") == sample_id:
            case_identity = str(binding["common_case_identity"])
            break
    if case_identity is None:
        raise FinalChanceGateError("common case binding missing")

    effective_at = now
    expires_at = min(paid_auth.expires_at, rate_card.expires_at)
    if not (effective_at < expires_at):
        raise FinalChanceGateError("explicit-slot authority validity window is invalid")

    authority = FinalChanceExplicitSlotAuthority(
        explicit_slot_identity=slot_identity,
        plan_identity=str(plan["pilot_plan_identity"]),
        plan_file_sha256=plan_file_sha256,
        provider_id=provider_id,
        model_id=config.model_id,
        sample_id=sample_id,
        case_identity=case_identity,
        authorization_id=paid_auth.authorization_id,
        rate_card_identity=rate_card.identity,
        worst_case_reservation_cny=_decimal_text(worst),
        effective_at=effective_at,
        expires_at=expires_at,
        authority_identity="",
    )
    payload = authority.payload()
    return FinalChanceExplicitSlotAuthority.from_payload(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Final-Chance V0.2 pre-send review")
    parser.add_argument(
        "--freeze-slot",
        metavar="SLOT",
        help="freeze exactly one explicit paid slot, e.g. DKL_FC_V0_2:DEEPSEEK:DKL-FC-001",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=SLOT_AUTHORITY_OUTPUT,
        help="output path for the explicit-slot authority (freeze mode only)",
    )
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    try:
        if args.freeze_slot is None:
            report = build_presend_review(now=now)
            print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        authority = build_explicit_slot_authority(slot_identity=args.freeze_slot, now=now)
        payload = authority.payload()
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(_pretty_bytes(payload))
        print(
            json.dumps(
                {
                    "authority_written": True,
                    "output": str(args.output),
                    "explicit_slot_identity": payload["explicit_slot_identity"],
                    "next_explicit_paid_slot": payload["next_explicit_paid_slot"],
                    "plan_identity": payload["plan_identity"],
                    "worst_case_reservation_cny": payload["worst_case_reservation_cny"],
                    "authority_identity": payload["authority_identity"],
                    "effective_at": payload["effective_at"],
                    "expires_at": payload["expires_at"],
                    "network_request_made": False,
                    "credential_value_exposed": False,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except FinalChanceGateError as error:
        print(json.dumps({"error": "FAIL_CLOSED_GATE", "detail": str(error)}, ensure_ascii=False, sort_keys=True))
        return 4
    except FinalChanceError as error:
        print(json.dumps({"error": "FINAL_CHANCE_ERROR", "detail": str(error)}, ensure_ascii=False, sort_keys=True))
        return 5
    except Exception as error:  # noqa: BLE001
        print(
            json.dumps({"error": "UNEXPECTED", "detail": str(error), "credential_value_exposed": False}, ensure_ascii=False, sort_keys=True)
        )
        return 6


def _require_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("now must be timezone-aware")
    return value


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


if __name__ == "__main__":
    raise SystemExit(main())
