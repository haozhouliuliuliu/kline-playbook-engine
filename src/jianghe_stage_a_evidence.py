"""Deterministic, credential-free Stage-A attempt-evidence materialization.

This module is a mechanical bridge from the local execution journal to a durable
artifact. It deliberately does not create evaluator judgments, fidelity scores,
provider ranks, retries, or provider network activity.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from typing import Mapping, Sequence

from src.jianghe_prespend_runtime import ProviderUsage
from src.jianghe_stage_a_runner import (
    ATTEMPT_TERMINAL,
    FROZEN_PLAN_PATH,
    NETWORK_ATTEMPT_STARTED,
    StageAExecutionJournal,
    VerifiedFrozenStageAPlan,
    prepare_frozen_slot,
)
from src.jianghe_stage_a_runtime import (
    StageAInputRequest,
    StageAInputTrack,
    StageAProviderInvocationEvidence,
)
from tools.build_jianghe_stage_a_frozen_plan_v0_2 import build_frozen_plan

EVIDENCE_SCHEMA_VERSION = "JIANGHE_STAGE_A_ATTEMPT_EVIDENCE_V0_2"
EVALUATOR_JUDGMENT_REQUIRED = "EVALUATOR_JUDGMENT_REQUIRED"
SEMANTIC_SCORE_INELIGIBLE = "INELIGIBLE_CURRENT_ATTEMPT"
INCOMPLETE_STATUS = "INCOMPLETE_UNCERTAIN"
DEFAULT_JOURNAL_NAME = "journal.jsonl"

_ARTIFACT_FIELDS = frozenset(
    {
        "artifact_schema_version",
        "artifact_identity",
        "plan_identity",
        "plan_sha256",
        "source_journal_sha256",
        "source_journal_event_count",
        "source_journal_last_event_identity",
        "attempt_count",
        "accounted_cny",
        "automatic_retry",
        "outcome_access",
        "evaluator_boundary",
        "attempts",
    }
)

_PROVIDER_EVIDENCE_FIELDS = frozenset(
    {
        "identity",
        "input_track",
        "request_identity",
        "source_observation_identity",
        "selected_context_identity",
        "context_selection_policy_identity",
        "local_structured_observation_identity",
        "transmitted_structured_observation_identity",
        "transmitted_visual_identities",
        "provider_spec_identity",
        "requested_model_id",
        "resolved_model_id",
        "provider_request_id",
        "usage",
        "latency_ms",
        "rate_card_identity",
        "budget_reservation_id",
        "charged_cny",
        "http_status_class",
        "finish_reason",
        "final_content_state",
        "final_content_sha256",
        "reasoning_present",
        "reasoning_length",
        "reasoning_sha256",
        "reasoning_token_count",
    }
)
_USAGE_FIELDS = frozenset({"prompt_tokens", "image_tokens", "completion_tokens"})
_FORBIDDEN_JUDGMENT_FIELDS = frozenset(
    {
        "acknowledged_principles",
        "violated_principles",
        "invented_thresholds",
        "fidelity_score",
        "fidelity_pass",
        "fidelity_fail",
        "provider_rank",
    }
)
_FORBIDDEN_SECRET_KEYS = frozenset(
    {
        "authorization",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "client_secret",
        "credential",
        "credential_value",
        "secret",
    }
)
_SECRET_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bBearer\s+[A-Za-z0-9._~+/=-]{8,}",
        r"\bsk-[A-Za-z0-9_-]{8,}",
        r"\b(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|credential)\s*[:=]\s*['\"]?[^\s,'\"]{8,}",
    )
)


class StageAEvidenceError(RuntimeError):
    """Raised when durable evidence cannot be produced safely."""


class SecretExposureError(StageAEvidenceError):
    """Raised when candidate output contains credential-like material."""


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _identity(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def _decimal(value: object, field_name: str) -> Decimal:
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise StageAEvidenceError(f"{field_name} must be a finite non-negative Decimal") from None
    if not result.is_finite() or result < 0:
        raise StageAEvidenceError(f"{field_name} must be a finite non-negative Decimal")
    return result


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _require_sha256(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise StageAEvidenceError(f"{field_name} must be lowercase SHA-256")
    return value


def _scan_forbidden_fields(value: object, path: str = "artifact") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.lower()
            if normalized in _FORBIDDEN_SECRET_KEYS:
                raise SecretExposureError(f"forbidden secret field at {path}.{key_text}")
            if normalized in _FORBIDDEN_JUDGMENT_FIELDS:
                raise StageAEvidenceError(f"exporter cannot emit evaluator judgment field: {key_text}")
            _scan_forbidden_fields(child, f"{path}.{key_text}")
        return
    if isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            _scan_forbidden_fields(child, f"{path}[{index}]")
        return
    if isinstance(value, str):
        for pattern in _SECRET_PATTERNS:
            if pattern.search(value):
                raise SecretExposureError(f"credential-like value detected at {path}")


def load_verified_frozen_plan() -> VerifiedFrozenStageAPlan:
    return VerifiedFrozenStageAPlan.load(
        committed_path=FROZEN_PLAN_PATH,
        deterministic_rebuild_bytes=canonical_json_bytes(build_frozen_plan()),
    )


def _validated_provider_evidence(
    raw: object,
    *,
    provider_row: Mapping[str, object],
    slot_row: Mapping[str, object],
    expected_request: StageAInputRequest,
) -> dict[str, object]:
    if not isinstance(raw, Mapping) or frozenset(raw) != _PROVIDER_EVIDENCE_FIELDS:
        raise StageAEvidenceError("provider evidence schema mismatch")
    usage_raw = raw.get("usage")
    if usage_raw is not None and (
        not isinstance(usage_raw, Mapping) or frozenset(usage_raw) != _USAGE_FIELDS
    ):
        raise StageAEvidenceError("provider usage schema mismatch")
    try:
        usage_values = None if usage_raw is None else {
            name: usage_raw[name] for name in _USAGE_FIELDS
        }
        if usage_values is not None and any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in usage_values.values()
        ):
            raise ValueError
        latency_ms = raw.get("latency_ms")
        if isinstance(latency_ms, bool) or not isinstance(latency_ms, int) or latency_ms < 0:
            raise ValueError
        for name in ("resolved_model_id", "provider_request_id", "finish_reason"):
            value = raw.get(name)
            if value is not None and (not isinstance(value, str) or not value):
                raise ValueError
        final_state = raw.get("final_content_state")
        final_hash = raw.get("final_content_sha256")
        if final_state in {"TEXT_NONEMPTY", "TEXT_EMPTY"}:
            if not isinstance(final_hash, str) or re.fullmatch(r"[0-9a-f]{64}", final_hash) is None:
                raise ValueError
        elif final_hash is not None:
            raise ValueError
        reasoning_present = raw.get("reasoning_present")
        if not isinstance(reasoning_present, bool):
            raise ValueError
        reasoning_length = raw.get("reasoning_length")
        reasoning_hash = raw.get("reasoning_sha256")
        reasoning_tokens = raw.get("reasoning_token_count")
        if reasoning_length is not None and (
            isinstance(reasoning_length, bool)
            or not isinstance(reasoning_length, int)
            or reasoning_length < 0
        ):
            raise ValueError
        if reasoning_hash is not None and (
            not isinstance(reasoning_hash, str)
            or re.fullmatch(r"[0-9a-f]{64}", reasoning_hash) is None
        ):
            raise ValueError
        if reasoning_tokens is not None and (
            isinstance(reasoning_tokens, bool)
            or not isinstance(reasoning_tokens, int)
            or reasoning_tokens < 0
        ):
            raise ValueError
        if not reasoning_present and any(
            value is not None for value in (reasoning_length, reasoning_hash, reasoning_tokens)
        ):
            raise ValueError
        visual_ids = raw.get("transmitted_visual_identities")
        if not isinstance(visual_ids, list) or any(not isinstance(item, str) for item in visual_ids):
            raise ValueError
        rebuilt = StageAProviderInvocationEvidence(
            input_track=StageAInputTrack(str(raw.get("input_track"))),
            request_identity=str(raw.get("request_identity")),
            source_observation_identity=str(raw.get("source_observation_identity")),
            selected_context_identity=str(raw.get("selected_context_identity")),
            context_selection_policy_identity=str(raw.get("context_selection_policy_identity")),
            local_structured_observation_identity=str(raw.get("local_structured_observation_identity")),
            transmitted_structured_observation_identity=raw.get(
                "transmitted_structured_observation_identity"
            ),
            transmitted_visual_identities=tuple(visual_ids),
            provider_spec_identity=str(raw.get("provider_spec_identity")),
            requested_model_id=str(raw.get("requested_model_id")),
            resolved_model_id=raw.get("resolved_model_id"),
            provider_request_id=raw.get("provider_request_id"),
            raw_provider_response_body="{}",
            raw_response_text=None,
            usage=None if usage_values is None else ProviderUsage(
                text_input_tokens=usage_values["prompt_tokens"],
                image_tokens=usage_values["image_tokens"],
                output_tokens=usage_values["completion_tokens"],
            ),
            latency_ms=latency_ms,
            rate_card_identity=str(raw.get("rate_card_identity")),
            budget_reservation_id=str(raw.get("budget_reservation_id")),
            charged_cny=_decimal_text(_decimal(raw.get("charged_cny"), "provider.charged_cny")),
            http_status_class=str(raw.get("http_status_class")),
            finish_reason=raw.get("finish_reason"),
            final_content_state=str(raw.get("final_content_state")),
            final_content_sha256=raw.get("final_content_sha256"),
            reasoning_present=raw.get("reasoning_present"),
            reasoning_length=raw.get("reasoning_length"),
            reasoning_sha256=raw.get("reasoning_sha256"),
            reasoning_token_count=raw.get("reasoning_token_count"),
        )
    except (TypeError, ValueError) as error:
        raise StageAEvidenceError("provider evidence contains invalid values") from error

    expected = {
        "identity": rebuilt.identity,
        "input_track": slot_row.get("track"),
        "request_identity": slot_row.get("request_identity"),
        "provider_spec_identity": provider_row.get("provider_spec_identity"),
        "requested_model_id": provider_row.get("model_id"),
        "rate_card_identity": provider_row.get("rate_card_identity"),
        "source_observation_identity": expected_request.stimulus.observation.identity.identity,
        "selected_context_identity": expected_request.context.identity,
        "context_selection_policy_identity": (
            expected_request.context.context_selection_policy_identity
        ),
        "local_structured_observation_identity": expected_request.stimulus.structured.identity,
        "transmitted_structured_observation_identity": slot_row.get(
            "transmitted_structured_observation_identity"
        ),
        "transmitted_visual_identities": slot_row.get("transmitted_visual_identities"),
    }
    for name, expected_value in expected.items():
        if raw.get(name) != expected_value:
            raise StageAEvidenceError(f"provider evidence differs from frozen slot: {name}")
    return dict(raw)


def _attempt_record(
    *,
    plan: VerifiedFrozenStageAPlan,
    start: Mapping[str, object],
    terminal: Mapping[str, object] | None,
) -> dict[str, object]:
    provider_id = str(start["provider_id"])
    slot = int(start["slot"])
    provider_row = plan.provider_row(provider_id)
    slot_row = plan.slot_row(provider_id, slot)
    plan_as_of = plan.payload.get("plan_as_of")
    if not isinstance(plan_as_of, str):
        raise StageAEvidenceError("frozen plan_as_of is malformed")
    try:
        plan_time = datetime.fromisoformat(plan_as_of)
    except ValueError as error:
        raise StageAEvidenceError("frozen plan_as_of is malformed") from error
    prepared = prepare_frozen_slot(
        plan,
        provider_id=provider_id,
        slot=slot,
        now=plan_time,
    )
    worst = _decimal(slot_row.get("worst_case_cny"), "slot.worst_case_cny")
    provider_evidence: dict[str, object] | None = None
    terminal_status: str
    terminal_identity: str | None
    normalized_identity: str | None
    error_type: str | None
    error_message: str | None

    if terminal is None:
        terminal_status = INCOMPLETE_STATUS
        terminal_identity = None
        accounted = worst
        normalized_identity = None
        error_type = None
        error_message = None
        semantic_score_status = SEMANTIC_SCORE_INELIGIBLE
    else:
        terminal_status = str(terminal["status"])
        terminal_identity = _require_sha256(
            terminal.get("event_identity"), "terminal.event_identity"
        )
        accounted = _decimal(terminal.get("accounted_cny"), "terminal.accounted_cny")
        normalized_raw = terminal.get("normalized_decision_identity")
        normalized_identity = (
            None
            if normalized_raw is None
            else _require_sha256(normalized_raw, "normalized_decision_identity")
        )
        error_type = terminal.get("error_type")
        error_message = terminal.get("error_message")
        if error_type is not None and not isinstance(error_type, str):
            raise StageAEvidenceError("terminal error_type must be text or null")
        if error_message is not None and not isinstance(error_message, str):
            raise StageAEvidenceError("terminal error_message must be text or null")
        if terminal.get("provider_evidence") is not None:
            provider_evidence = _validated_provider_evidence(
                terminal["provider_evidence"],
                provider_row=provider_row,
                slot_row=slot_row,
                expected_request=prepared.request,
            )

        if terminal_status == "SUCCESS_NORMALIZED":
            if provider_evidence is None or normalized_identity is None:
                raise StageAEvidenceError(
                    "SUCCESS_NORMALIZED requires provider evidence and normalized decision identity"
                )
            if provider_evidence["resolved_model_id"] != provider_row.get("model_id"):
                raise StageAEvidenceError("successful attempt cannot contain provider model drift")
            semantic_score_status = EVALUATOR_JUDGMENT_REQUIRED
        else:
            if normalized_identity is not None:
                raise StageAEvidenceError("non-scoreable attempt cannot claim normalized semantic success")
            semantic_score_status = SEMANTIC_SCORE_INELIGIBLE
            if terminal_status in {
                "NON_SCOREABLE_NORMALIZER",
                "NON_SCOREABLE_PROVIDER_RESPONSE",
                "PROVIDER_MODEL_DRIFT",
            }:
                if provider_evidence is None:
                    raise StageAEvidenceError(f"{terminal_status} requires provider evidence")
            if terminal_status == "PROVIDER_MODEL_DRIFT":
                if provider_evidence["resolved_model_id"] == provider_row.get("model_id"):
                    raise StageAEvidenceError("PROVIDER_MODEL_DRIFT requires a different resolved model")
                if accounted != worst:
                    raise StageAEvidenceError("provider model drift must account full frozen worst-case")

    if accounted > worst:
        raise StageAEvidenceError("attempt accounting exceeds frozen worst-case")
    if terminal is None and accounted != worst:
        raise StageAEvidenceError("incomplete attempt must account full frozen worst-case")

    record = {
        "attempt_identity": _identity(
            {
                "network_start_event_identity": start["event_identity"],
                "terminal_event_identity": terminal_identity,
            }
        ),
        "plan_identity": plan.plan_identity,
        "plan_sha256": plan.sha256,
        "provider_id": provider_id,
        "requested_model_id": provider_row.get("model_id"),
        "slot": slot,
        "slot_key": start["slot_key"],
        "track": slot_row.get("track"),
        "request_identity": start["request_identity"],
        "payload_sha256": start["payload_sha256"],
        "frozen_worst_case_cny": _decimal_text(worst),
        "accounted_cny": _decimal_text(accounted),
        "network_start_event_identity": start["event_identity"],
        "terminal_event_identity": terminal_identity,
        "terminal_status": terminal_status,
        "automatic_retry": "FORBIDDEN",
        "semantic_score_status": semantic_score_status,
        "normalized_decision_identity": normalized_identity,
        "provider_evidence": provider_evidence,
        "error_type": error_type,
        "error_message": error_message,
        "request_provenance": {
            "fixture_id": slot_row.get("fixture_id"),
            "inference_configuration_identity": slot_row.get(
                "inference_configuration_identity"
            ),
            "transmitted_structured_observation_identity": slot_row.get(
                "transmitted_structured_observation_identity"
            ),
            "transmitted_visual_identities": slot_row.get(
                "transmitted_visual_identities"
            ),
        },
    }
    _scan_forbidden_fields(record)
    return record


def build_stage_a_attempt_evidence(
    *,
    plan: VerifiedFrozenStageAPlan,
    journal_path: Path,
) -> dict[str, object]:
    path = Path(journal_path)
    if not path.is_file():
        raise StageAEvidenceError(f"Stage-A journal is missing: {path}")
    raw_before = path.read_bytes()
    if not raw_before:
        raise StageAEvidenceError("Stage-A journal is empty")
    journal = StageAExecutionJournal(path, plan)
    events, snapshot = journal.verified_state_from_bytes(raw_before)
    if not events:
        raise StageAEvidenceError("Stage-A journal contains no attempts")

    starts: dict[str, Mapping[str, object]] = {}
    terminals: dict[str, Mapping[str, object]] = {}
    for event in events:
        key = str(event["slot_key"])
        if event["event_type"] == NETWORK_ATTEMPT_STARTED:
            starts[key] = event
        elif event["event_type"] == ATTEMPT_TERMINAL:
            terminals[key] = event
    if not starts:
        raise StageAEvidenceError("Stage-A journal contains no network-start attempts")

    records = [
        _attempt_record(plan=plan, start=start, terminal=terminals.get(key))
        for key, start in starts.items()
    ]
    artifact: dict[str, object] = {
        "artifact_schema_version": EVIDENCE_SCHEMA_VERSION,
        "artifact_identity": None,
        "plan_identity": plan.plan_identity,
        "plan_sha256": plan.sha256,
        "source_journal_sha256": sha256(raw_before).hexdigest(),
        "source_journal_event_count": len(events),
        "source_journal_last_event_identity": events[-1]["event_identity"],
        "attempt_count": len(records),
        "accounted_cny": _decimal_text(snapshot.stage_accounted_cny),
        "automatic_retry": "FORBIDDEN",
        "outcome_access": "NO",
        "evaluator_boundary": "EXPLICIT_EVALUATOR_SIDE_ADJUDICATION_REQUIRED",
        "attempts": records,
    }
    identity_payload = dict(artifact)
    identity_payload.pop("artifact_identity", None)
    artifact["artifact_identity"] = _identity(identity_payload)
    _scan_forbidden_fields(artifact)
    if raw_before != path.read_bytes():
        raise StageAEvidenceError("Stage-A journal changed during materialization")
    return artifact


def validate_stage_a_attempt_evidence_bytes(
    *,
    plan: VerifiedFrozenStageAPlan,
    raw_bytes: bytes,
) -> dict[str, object]:
    """Validate one previously materialized artifact without journal or network access."""

    if not isinstance(raw_bytes, bytes):
        raise TypeError("raw_bytes must be bytes")
    try:
        artifact = json.loads(raw_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StageAEvidenceError("Stage-A evidence is not valid UTF-8 JSON") from error
    if not isinstance(artifact, dict) or frozenset(artifact) != _ARTIFACT_FIELDS:
        raise StageAEvidenceError("Stage-A evidence top-level schema mismatch")
    if canonical_json_bytes(artifact) != raw_bytes:
        raise StageAEvidenceError("Stage-A evidence bytes are not canonical")
    if artifact["artifact_schema_version"] != EVIDENCE_SCHEMA_VERSION:
        raise StageAEvidenceError("Stage-A evidence schema version mismatch")
    if (
        artifact["plan_identity"] != plan.plan_identity
        or artifact["plan_sha256"] != plan.sha256
    ):
        raise StageAEvidenceError("Stage-A evidence is bound to a different frozen plan")
    _require_sha256(artifact["source_journal_sha256"], "source_journal_sha256")
    _require_sha256(
        artifact["source_journal_last_event_identity"],
        "source_journal_last_event_identity",
    )
    event_count = artifact["source_journal_event_count"]
    attempt_count = artifact["attempt_count"]
    if (
        isinstance(event_count, bool)
        or not isinstance(event_count, int)
        or event_count <= 0
        or isinstance(attempt_count, bool)
        or not isinstance(attempt_count, int)
        or attempt_count <= 0
    ):
        raise StageAEvidenceError("Stage-A evidence counts must be positive integers")
    attempts = artifact["attempts"]
    if not isinstance(attempts, list) or len(attempts) != attempt_count:
        raise StageAEvidenceError("Stage-A evidence attempt count mismatch")
    if event_count < attempt_count:
        raise StageAEvidenceError("Stage-A evidence journal event count is impossible")
    if artifact["automatic_retry"] != "FORBIDDEN" or artifact["outcome_access"] != "NO":
        raise StageAEvidenceError("Stage-A evidence safety invariant mismatch")
    if artifact["evaluator_boundary"] != "EXPLICIT_EVALUATOR_SIDE_ADJUDICATION_REQUIRED":
        raise StageAEvidenceError("Stage-A evidence evaluator boundary mismatch")

    rebuilt_records: list[dict[str, object]] = []
    seen_slots: set[str] = set()
    total = plan.carry_forward_snapshot().stage_accounted_cny
    for raw_record in attempts:
        if not isinstance(raw_record, Mapping):
            raise StageAEvidenceError("Stage-A evidence attempt must be an object")
        try:
            provider_id = raw_record["provider_id"]
            slot = raw_record["slot"]
            terminal_identity = raw_record["terminal_event_identity"]
            start = {
                "provider_id": provider_id,
                "slot": slot,
                "slot_key": raw_record["slot_key"],
                "request_identity": raw_record["request_identity"],
                "payload_sha256": raw_record["payload_sha256"],
                "event_identity": raw_record["network_start_event_identity"],
            }
            terminal = None
            if terminal_identity is not None:
                terminal = {
                    "status": raw_record["terminal_status"],
                    "event_identity": terminal_identity,
                    "accounted_cny": raw_record["accounted_cny"],
                    "normalized_decision_identity": raw_record[
                        "normalized_decision_identity"
                    ],
                    "error_type": raw_record["error_type"],
                    "error_message": raw_record["error_message"],
                    "provider_evidence": raw_record["provider_evidence"],
                }
        except KeyError as error:
            raise StageAEvidenceError("Stage-A evidence attempt schema mismatch") from error
        rebuilt = _attempt_record(plan=plan, start=start, terminal=terminal)
        if dict(raw_record) != rebuilt:
            raise StageAEvidenceError("Stage-A evidence attempt differs from mechanical rebuild")
        slot_key = str(rebuilt["slot_key"])
        if slot_key in seen_slots:
            raise StageAEvidenceError("Stage-A evidence contains a duplicate frozen slot")
        seen_slots.add(slot_key)
        total += _decimal(rebuilt["accounted_cny"], "attempt.accounted_cny")
        rebuilt_records.append(rebuilt)

    if artifact["accounted_cny"] != _decimal_text(total):
        raise StageAEvidenceError("Stage-A evidence aggregate accounting mismatch")
    identity_payload = dict(artifact)
    declared_identity = _require_sha256(
        identity_payload.pop("artifact_identity"), "artifact_identity"
    )
    if declared_identity != _identity(identity_payload):
        raise StageAEvidenceError("Stage-A evidence identity does not match content")
    _scan_forbidden_fields(artifact)
    return dict(artifact)


def materialize_stage_a_attempt_evidence(
    *,
    state_dir: Path,
    output_path: Path,
) -> dict[str, object]:
    state = Path(state_dir)
    journal_path = state / DEFAULT_JOURNAL_NAME
    output = Path(output_path)
    if output.resolve() == journal_path.resolve():
        raise StageAEvidenceError("evidence output cannot overwrite the source journal")
    plan = load_verified_frozen_plan()
    artifact = build_stage_a_attempt_evidence(
        plan=plan,
        journal_path=journal_path,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    try:
        temporary.write_bytes(canonical_json_bytes(artifact))
        os.replace(temporary, output)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
    return artifact


def forbidden_judgment_fields() -> Sequence[str]:
    """Expose the closed evaluator boundary for defensive tests and callers."""

    return tuple(sorted(_FORBIDDEN_JUDGMENT_FIELDS))


__all__ = [
    "DEFAULT_JOURNAL_NAME",
    "EVALUATOR_JUDGMENT_REQUIRED",
    "EVIDENCE_SCHEMA_VERSION",
    "INCOMPLETE_STATUS",
    "SecretExposureError",
    "StageAEvidenceError",
    "build_stage_a_attempt_evidence",
    "canonical_json_bytes",
    "forbidden_judgment_fields",
    "load_verified_frozen_plan",
    "materialize_stage_a_attempt_evidence",
    "validate_stage_a_attempt_evidence_bytes",
]
