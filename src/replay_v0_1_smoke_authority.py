"""Machine-readable provider-smoke authority for SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1.

The authority is the single gate that turns the offline smoke preparation into an
admitted three-call provider slot.  Until the Owner confirms payment the authority
stays ``PENDING_OWNER_PAYMENT_CONFIRMATION`` with ``owner_payment_confirmation=false``
and no smoke runner may initialize a network client, read the API key, or issue a
provider request.

The loader is fail-closed: any missing, mismatched, or out-of-bound field raises
before any network capability is constructed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping

from src.persistent_deepseek_runtime import (
    CURRENT_MODEL,
    PINNED_HARNESS_COMMIT,
    PINNED_HARNESS_VERSION,
    PROJECT_TRANSPORT_PATCH,
)

SMOKE_AUTHORITY_VERSION = "KPE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_V0_1"
SMOKE_RETEST_AUTHORITY_VERSION = "KPE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_V0_1"
# Forward two-identity authority form: every smoke wake carries BOTH the stable
# logical wake-selection identity and the runtime wake identity.  Historical
# V0_1 terminal authorities remain readable with runtime-only wakes.
SMOKE_AUTHORITY_VERSION_V0_2 = "KPE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_V0_2"
SMOKE_RETEST_AUTHORITY_VERSION_V0_2 = "KPE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_V0_2"
ALLOWED_AUTHORITY_VERSIONS = frozenset({
    SMOKE_AUTHORITY_VERSION,
    SMOKE_RETEST_AUTHORITY_VERSION,
    SMOKE_AUTHORITY_VERSION_V0_2,
    SMOKE_RETEST_AUTHORITY_VERSION_V0_2,
})
SMOKE_STATUS_PENDING = "PENDING_OWNER_PAYMENT_CONFIRMATION"
SMOKE_STATUS_ACTIVE = "ACTIVE"
SMOKE_STATUS_REVOKED = "REVOKED"
ALLOWED_STATUSES = frozenset({SMOKE_STATUS_PENDING, SMOKE_STATUS_ACTIVE, SMOKE_STATUS_REVOKED})

WORK_PACKAGE = "SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1"
WAKE_POLICY = "EVERY_NEW_CLOSED_5M_BAR"
SMOKE_MAX_PROVIDER_CALLS = 3
SMOKE_MAX_RETRIES = 0
SMOKE_IMAGES_PER_CALL = 4
SMOKE_RESTART_AFTER_CALL = 2
PROVIDER = "deepseek"
SPEND_PENDING = "PENDING_OWNER_CONFIRMATION"


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _non_empty(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"smoke authority {field_name} must be non-empty")
    return value


def _require_bool(value: object, field_name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"smoke authority {field_name} must be a strict boolean")
    return value


def _require_int(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"smoke authority {field_name} must be an integer")
    return value


def _parse_date(value: object, field_name: str) -> date:
    if not isinstance(value, str) or not value:
        raise ValueError(f"smoke authority {field_name} must be an ISO date")
    return date.fromisoformat(value)


def _parse_dt(value: object, field_name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"smoke authority {field_name} must be an ISO datetime")
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"smoke authority {field_name} must be timezone-aware")
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class SmokeWakeBinding:
    """One exact smoke wake: deterministic runtime identity, logical selection
    identity and close time.

    Historical V0_1 terminal authorities are runtime-only (``logical_wake_selection_identity``
    is ``None``).  Future ACTIVE/PENDING authorities must carry both identities.
    """

    wake_identity: str
    close_time: datetime
    logical_wake_selection_identity: str | None = None

    def __post_init__(self) -> None:
        _non_empty(self.wake_identity, "smoke_wake.wake_identity")
        _aware(self.close_time, "smoke_wake.close_time")
        if self.logical_wake_selection_identity is not None:
            _non_empty(
                self.logical_wake_selection_identity,
                "smoke_wake.logical_wake_selection_identity",
            )

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "wake_identity": self.wake_identity,
            "close_time": self.close_time.astimezone(timezone.utc).isoformat(timespec="microseconds"),
        }
        if self.logical_wake_selection_identity is not None:
            payload["logical_wake_selection_identity"] = self.logical_wake_selection_identity
        return payload


def _aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")


@dataclass(frozen=True)
class PromptIdentitySet:
    prompt_contract_version: str
    prompt_contract_identity: str
    system_prompt_sha256: str
    decision_prompt_sha256: str

    def __post_init__(self) -> None:
        _non_empty(self.prompt_contract_version, "prompt_contract_version")
        _non_empty(self.prompt_contract_identity, "prompt_contract_identity")
        for value, name in (
            (self.system_prompt_sha256, "system_prompt_sha256"),
            (self.decision_prompt_sha256, "decision_prompt_sha256"),
        ):
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError(f"smoke authority {name} must be a SHA-256 hex string")

    def to_payload(self) -> dict[str, object]:
        return {
            "prompt_contract_version": self.prompt_contract_version,
            "prompt_contract_identity": self.prompt_contract_identity,
            "system_prompt_sha256": self.system_prompt_sha256,
            "decision_prompt_sha256": self.decision_prompt_sha256,
        }


@dataclass(frozen=True)
class ProviderSmokeAuthority:
    authority_version: str
    status: str
    owner_payment_confirmation: bool
    work_package: str
    product: str
    concrete_contract: str
    slice_identity: str
    exact_slice_seal_identity: str
    prior_history_days: tuple[date, ...]
    burn_in_days: tuple[date, ...]
    measurement_days: tuple[date, ...]
    provider: str
    model: str
    harness_version: str
    harness_commit: str
    project_transport_patch: str
    max_provider_calls: int
    max_retries: int
    images_per_call: int
    wake_policy: str
    restart_after_call: int
    smoke_wakes: tuple[tuple[str, SmokeWakeBinding], ...]
    prompt_identities: PromptIdentitySet
    context_policy_identity: str
    renderer_identity: str
    api_key_env: str
    execution_code_commit: str
    full_replay_authorized: bool
    full_replay_1998_calls_authorized: bool
    max_spend_cny: str
    created_at: datetime
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.authority_version not in ALLOWED_AUTHORITY_VERSIONS:
            raise ValueError("smoke authority version is not supported")
        if self.status not in ALLOWED_STATUSES:
            raise ValueError(f"smoke authority status {self.status!r} is not allowed")
        _require_bool(self.owner_payment_confirmation, "owner_payment_confirmation")
        if self.work_package != WORK_PACKAGE:
            raise ValueError("smoke authority work_package mismatch")
        _non_empty(self.product, "product")
        _non_empty(self.concrete_contract, "concrete_contract")
        _non_empty(self.slice_identity, "slice_identity")
        _non_empty(self.exact_slice_seal_identity, "exact_slice_seal_identity")
        if not self.prior_history_days or len(self.prior_history_days) != 20:
            raise ValueError("smoke authority prior_history_days must contain 20 days")
        if len(self.burn_in_days) != 2 or len(self.measurement_days) != 20:
            raise ValueError("smoke authority requires 2 burn-in + 20 measurement days")
        if self.provider != PROVIDER or self.model != CURRENT_MODEL:
            raise ValueError("smoke authority provider/model mismatch")
        if (self.harness_version, self.harness_commit) != (PINNED_HARNESS_VERSION, PINNED_HARNESS_COMMIT):
            raise ValueError("smoke authority must pin the admitted Harness build")
        if self.project_transport_patch != PROJECT_TRANSPORT_PATCH:
            raise ValueError("smoke authority must bind the project fail-closed transport patch")
        if self.max_provider_calls != SMOKE_MAX_PROVIDER_CALLS:
            raise ValueError("smoke authority max_provider_calls must be exactly 3")
        if self.max_retries != SMOKE_MAX_RETRIES:
            raise ValueError("smoke authority max_retries must be exactly 0")
        if self.images_per_call != SMOKE_IMAGES_PER_CALL:
            raise ValueError("smoke authority images_per_call must be exactly 4")
        if self.wake_policy != WAKE_POLICY:
            raise ValueError("smoke authority wake_policy mismatch")
        if self.restart_after_call != SMOKE_RESTART_AFTER_CALL:
            raise ValueError("smoke authority restart_after_call must be exactly 2")
        if len(self.smoke_wakes) != 3 or [name for name, _ in self.smoke_wakes] != ["call_1", "call_2", "call_3"]:
            raise ValueError("smoke authority must bind exactly call_1/call_2/call_3 wakes")
        if len({binding.wake_identity for _, binding in self.smoke_wakes}) != 3:
            raise ValueError("smoke wake identities must be distinct")
        two_identity_required = self.authority_version in (
            SMOKE_AUTHORITY_VERSION_V0_2,
            SMOKE_RETEST_AUTHORITY_VERSION_V0_2,
        )
        runtime_only = any(
            binding.logical_wake_selection_identity is None for _, binding in self.smoke_wakes
        )
        if two_identity_required and runtime_only:
            raise ValueError(
                "V0_2 smoke authority requires both logical and runtime wake identities"
            )
        if runtime_only and self.status != SMOKE_STATUS_REVOKED:
            raise ValueError(
                "a runtime-only smoke authority is terminal only; "
                "it may not be PENDING or ACTIVE"
            )
        _non_empty(self.context_policy_identity, "context_policy_identity")
        _non_empty(self.renderer_identity, "renderer_identity")
        _non_empty(self.api_key_env, "api_key_env")
        if not self.api_key_env.startswith(("DEEPSEEK_", "OPENAI_", "ANTHROPIC_")):
            raise ValueError("smoke authority api_key_env must be a credential environment variable name")
        _non_empty(self.execution_code_commit, "execution_code_commit")
        _require_bool(self.full_replay_authorized, "full_replay_authorized")
        _require_bool(self.full_replay_1998_calls_authorized, "full_replay_1998_calls_authorized")
        if self.full_replay_authorized or self.full_replay_1998_calls_authorized:
            raise ValueError("smoke authority must not authorize a full 1998-call replay")
        if not isinstance(self.max_spend_cny, str) or not self.max_spend_cny:
            raise ValueError("smoke authority max_spend_cny must be non-empty")
        if self.status == SMOKE_STATUS_ACTIVE:
            if self.owner_payment_confirmation is not True:
                raise ValueError("ACTIVE smoke authority requires owner_payment_confirmation=true")
            try:
                spend = Decimal(self.max_spend_cny)
            except InvalidOperation as error:
                raise ValueError(
                    "ACTIVE smoke authority requires a positive finite max_spend_cny"
                ) from error
            if not spend.is_finite() or spend <= 0:
                raise ValueError(
                    "ACTIVE smoke authority requires a positive finite max_spend_cny"
                )
        object.__setattr__(self, "identity", _hash(self.to_payload(include_identity=False)))

    def to_payload(self, *, include_identity: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "authority_version": self.authority_version,
            "status": self.status,
            "owner_payment_confirmation": self.owner_payment_confirmation,
            "work_package": self.work_package,
            "product": self.product,
            "concrete_contract": self.concrete_contract,
            "slice_identity": self.slice_identity,
            "exact_slice_seal_identity": self.exact_slice_seal_identity,
            "prior_history_days": [day.isoformat() for day in self.prior_history_days],
            "burn_in_days": [day.isoformat() for day in self.burn_in_days],
            "measurement_days": [day.isoformat() for day in self.measurement_days],
            "provider": self.provider,
            "model": self.model,
            "harness_version": self.harness_version,
            "harness_commit": self.harness_commit,
            "project_transport_patch": self.project_transport_patch,
            "max_provider_calls": self.max_provider_calls,
            "max_retries": self.max_retries,
            "images_per_call": self.images_per_call,
            "wake_policy": self.wake_policy,
            "restart_after_call": self.restart_after_call,
            "smoke_wakes": {
                name: binding.to_payload() for name, binding in self.smoke_wakes
            },
            "prompt_identities": self.prompt_identities.to_payload(),
            "context_policy_identity": self.context_policy_identity,
            "renderer_identity": self.renderer_identity,
            "api_key_env": self.api_key_env,
            "execution_code_commit": self.execution_code_commit,
            "full_replay_authorized": self.full_replay_authorized,
            "full_replay_1998_calls_authorized": self.full_replay_1998_calls_authorized,
            "max_spend_cny": self.max_spend_cny,
            "created_at": self.created_at.astimezone(timezone.utc).isoformat(timespec="microseconds"),
        }
        if include_identity:
            payload["authority_identity"] = self.identity
        return payload


def _parse_smoke_wakes(raw: object) -> tuple[tuple[str, SmokeWakeBinding], ...]:
    if not isinstance(raw, Mapping):
        raise ValueError("smoke authority smoke_wakes must be an object")
    order = ("call_1", "call_2", "call_3")
    if list(raw) != list(order):
        raise ValueError("smoke authority smoke_wakes must contain exactly call_1/call_2/call_3 in order")
    result = []
    for name in order:
        entry = raw[name]
        if not isinstance(entry, Mapping):
            raise ValueError(f"smoke wake {name} must be an object")
        logical = entry.get("logical_wake_selection_identity")
        result.append((name, SmokeWakeBinding(
            wake_identity=_non_empty(entry.get("wake_identity"), f"{name}.wake_identity"),
            close_time=_parse_dt(entry.get("close_time"), f"{name}.close_time"),
            logical_wake_selection_identity=(
                None if logical is None else _non_empty(logical, f"{name}.logical_wake_selection_identity")
            ),
        )))
    return tuple(result)


def load_provider_smoke_authority(path: str | Path) -> ProviderSmokeAuthority:
    """Load and strictly validate the provider-smoke authority; fail closed."""
    authority_path = Path(path)
    raw = json.loads(authority_path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("smoke authority file must contain a JSON object")
    stored_identity = raw.get("authority_identity")
    if not isinstance(stored_identity, str) or len(stored_identity) != 64:
        raise ValueError("smoke authority identity is missing or malformed")
    authority = ProviderSmokeAuthority(
        authority_version=_non_empty(raw.get("authority_version"), "authority_version"),
        status=_non_empty(raw.get("status"), "status"),
        owner_payment_confirmation=_require_bool(raw.get("owner_payment_confirmation"), "owner_payment_confirmation"),
        work_package=_non_empty(raw.get("work_package"), "work_package"),
        product=_non_empty(raw.get("product"), "product"),
        concrete_contract=_non_empty(raw.get("concrete_contract"), "concrete_contract"),
        slice_identity=_non_empty(raw.get("slice_identity"), "slice_identity"),
        exact_slice_seal_identity=_non_empty(raw.get("exact_slice_seal_identity"), "exact_slice_seal_identity"),
        prior_history_days=tuple(
            _parse_date(day, "prior_history_days") for day in raw.get("prior_history_days", [])
        ),
        burn_in_days=tuple(_parse_date(day, "burn_in_days") for day in raw.get("burn_in_days", [])),
        measurement_days=tuple(
            _parse_date(day, "measurement_days") for day in raw.get("measurement_days", [])
        ),
        provider=_non_empty(raw.get("provider"), "provider"),
        model=_non_empty(raw.get("model"), "model"),
        harness_version=_non_empty(raw.get("harness_version"), "harness_version"),
        harness_commit=_non_empty(raw.get("harness_commit"), "harness_commit"),
        project_transport_patch=_non_empty(raw.get("project_transport_patch"), "project_transport_patch"),
        max_provider_calls=_require_int(raw.get("max_provider_calls"), "max_provider_calls"),
        max_retries=_require_int(raw.get("max_retries"), "max_retries"),
        images_per_call=_require_int(raw.get("images_per_call"), "images_per_call"),
        wake_policy=_non_empty(raw.get("wake_policy"), "wake_policy"),
        restart_after_call=_require_int(raw.get("restart_after_call"), "restart_after_call"),
        smoke_wakes=_parse_smoke_wakes(raw.get("smoke_wakes")),
        prompt_identities=_parse_prompt_identities(raw.get("prompt_identities")),
        context_policy_identity=_non_empty(raw.get("context_policy_identity"), "context_policy_identity"),
        renderer_identity=_non_empty(raw.get("renderer_identity"), "renderer_identity"),
        api_key_env=_non_empty(raw.get("api_key_env"), "api_key_env"),
        execution_code_commit=_non_empty(raw.get("execution_code_commit"), "execution_code_commit"),
        full_replay_authorized=_require_bool(raw.get("full_replay_authorized"), "full_replay_authorized"),
        full_replay_1998_calls_authorized=_require_bool(
            raw.get("full_replay_1998_calls_authorized"), "full_replay_1998_calls_authorized"
        ),
        max_spend_cny=_non_empty(raw.get("max_spend_cny"), "max_spend_cny"),
        created_at=_parse_dt(raw.get("created_at"), "created_at"),
    )
    if stored_identity != authority.identity:
        raise ValueError("smoke authority identity does not match its canonical payload")
    return authority


def _parse_prompt_identities(raw: object) -> PromptIdentitySet:
    if not isinstance(raw, Mapping):
        raise ValueError("smoke authority prompt_identities must be an object")
    return PromptIdentitySet(
        prompt_contract_version=_non_empty(raw.get("prompt_contract_version"), "prompt_contract_version"),
        prompt_contract_identity=_non_empty(raw.get("prompt_contract_identity"), "prompt_contract_identity"),
        system_prompt_sha256=_non_empty(raw.get("system_prompt_sha256"), "system_prompt_sha256"),
        decision_prompt_sha256=_non_empty(raw.get("decision_prompt_sha256"), "decision_prompt_sha256"),
    )


def assert_smoke_authority_active(authority: ProviderSmokeAuthority) -> None:
    """Fail closed unless the authority is ACTIVE with Owner payment confirmed.

    This is the single gate a smoke runner must pass before it may read any
    provider credential or construct any network capability.
    """
    if authority.status != SMOKE_STATUS_ACTIVE:
        raise ValueError(
            f"provider smoke is not admitted: authority.status={authority.status!r} "
            "(must be ACTIVE)"
        )
    if authority.owner_payment_confirmation is not True:
        raise ValueError("provider smoke is not admitted: owner_payment_confirmation is false")


__all__ = [
    "PROVIDER",
    "ProviderSmokeAuthority",
    "SMOKE_AUTHORITY_VERSION",
    "SMOKE_AUTHORITY_VERSION_V0_2",
    "SMOKE_IMAGES_PER_CALL",
    "SMOKE_MAX_PROVIDER_CALLS",
    "SMOKE_MAX_RETRIES",
    "SMOKE_RESTART_AFTER_CALL",
    "SMOKE_RETEST_AUTHORITY_VERSION",
    "SMOKE_RETEST_AUTHORITY_VERSION_V0_2",
    "SMOKE_STATUS_ACTIVE",
    "SMOKE_STATUS_PENDING",
    "SMOKE_STATUS_REVOKED",
    "SPEND_PENDING",
    "SmokeWakeBinding",
    "assert_smoke_authority_active",
    "load_provider_smoke_authority",
]
