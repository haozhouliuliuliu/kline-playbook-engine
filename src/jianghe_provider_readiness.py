"""Read-only provider credential/balance readiness for Jianghe Stage-A.

This module is deliberately separate from model transport. It never calls a model
endpoint and never serializes credential values. Kimi and DeepSeek are checked only
through their official read-only balance endpoints. MiniMax pay-as-you-go remains
fail-closed until an official machine-readable non-billable balance surface is
established.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
from typing import Callable, Mapping
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from src.jianghe_prespend_runtime import IMPLEMENTATION_TARGET_SPECS, ProviderSpec
from src.jianghe_stage_a_runner import VerifiedFrozenStageAPlan

READINESS_VERSION = "JIANGHE_PROVIDER_BALANCE_READINESS_V0_1"
KIMI_BALANCE_ENDPOINT = "https://api.moonshot.cn/v1/users/me/balance"
DEEPSEEK_BALANCE_ENDPOINT = "https://api.deepseek.com/user/balance"

READY_EXISTING_FUNDS = "READY_EXISTING_FUNDS"
CREDENTIAL_MISSING = "CREDENTIAL_MISSING"
AUTH_FAILED = "AUTH_FAILED"
INSUFFICIENT_EXISTING_FUNDS = "INSUFFICIENT_EXISTING_FUNDS"
BALANCE_CHECK_FAILED = "BALANCE_CHECK_FAILED"
UNRESOLVED_NON_CNY_BALANCE = "UNRESOLVED_NON_CNY_BALANCE"
UNRESOLVED_NO_READ_ONLY_PAYGO_BALANCE_API = (
    "UNRESOLVED_NO_READ_ONLY_PAYGO_BALANCE_API"
)


class ProviderReadinessError(RuntimeError):
    pass


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _decimal(value: object, field_name: str) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ProviderReadinessError(f"{field_name} must be a finite Decimal") from None
    if not result.is_finite() or result < 0:
        raise ProviderReadinessError(f"{field_name} has invalid Decimal value")
    return result


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _find_spec(provider_id: str) -> ProviderSpec:
    matches = [item for item in IMPLEMENTATION_TARGET_SPECS if item.provider_id == provider_id]
    if len(matches) != 1:
        raise ProviderReadinessError("provider is not in the Stage-A implementation target set")
    return matches[0]


def required_stage_a_cny(plan: VerifiedFrozenStageAPlan, provider_id: str) -> Decimal:
    row = plan.provider_row(provider_id)
    return _decimal(row.get("five_slot_worst_case_cny"), "five_slot_worst_case_cny")


@dataclass(frozen=True)
class ProviderBalanceReadiness:
    provider_id: str
    model_id: str
    credential_present: bool
    balance_method: str
    balance_checked: bool
    existing_balance_cny: Decimal | None
    required_stage_a_cny: Decimal
    shortfall_cny: Decimal | None
    status: str
    detail: str
    model_endpoint_called: bool = False
    credential_value_exposed: bool = False
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.model_endpoint_called:
            raise ValueError("readiness checker must never call a model endpoint")
        if self.credential_value_exposed:
            raise ValueError("readiness checker must never expose credentials")
        payload = self.to_dict(include_identity=False)
        object.__setattr__(
            self,
            "identity",
            sha256(_canonical_json(payload).encode("utf-8")).hexdigest(),
        )

    def to_dict(self, *, include_identity: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "artifact_schema_version": READINESS_VERSION,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "credential_present": self.credential_present,
            "balance_method": self.balance_method,
            "balance_checked": self.balance_checked,
            "existing_balance_cny": _decimal_text(self.existing_balance_cny),
            "required_stage_a_cny": _decimal_text(self.required_stage_a_cny),
            "shortfall_cny": _decimal_text(self.shortfall_cny),
            "status": self.status,
            "detail": self.detail,
            "model_endpoint_called": False,
            "credential_value_exposed": False,
        }
        if include_identity:
            payload["identity"] = self.identity
        return payload


HttpGet = Callable[[str, Mapping[str, str], float], tuple[int, bytes]]


def _default_http_get(url: str, headers: Mapping[str, str], timeout: float) -> tuple[int, bytes]:
    request = urllib_request.Request(url, headers=dict(headers), method="GET")
    try:
        with urllib_request.urlopen(request, timeout=timeout) as response:
            return int(response.status), response.read()
    except HTTPError as error:
        return int(error.code), error.read()
    except URLError as error:
        raise ProviderReadinessError("read-only balance request failed at network layer") from error


def _parse_json(body: bytes) -> Mapping[str, object]:
    try:
        value = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ProviderReadinessError("balance endpoint returned malformed JSON") from error
    if not isinstance(value, Mapping):
        raise ProviderReadinessError("balance endpoint returned a non-object payload")
    return value


def _parse_kimi_balance(payload: Mapping[str, object]) -> Decimal:
    if payload.get("status") is not True:
        raise ProviderReadinessError("Kimi balance response did not report success")
    data = payload.get("data")
    if not isinstance(data, Mapping):
        raise ProviderReadinessError("Kimi balance response is missing data")
    return _decimal(data.get("available_balance"), "Kimi.available_balance")


def _parse_deepseek_balance(payload: Mapping[str, object]) -> tuple[Decimal | None, str | None]:
    if not isinstance(payload.get("is_available"), bool):
        raise ProviderReadinessError("DeepSeek balance response is missing is_available")
    infos = payload.get("balance_infos")
    if not isinstance(infos, list):
        raise ProviderReadinessError("DeepSeek balance response is missing balance_infos")
    cny_rows = [
        item
        for item in infos
        if isinstance(item, Mapping) and item.get("currency") == "CNY"
    ]
    if len(cny_rows) > 1:
        raise ProviderReadinessError("DeepSeek balance response has multiple CNY rows")
    if not cny_rows:
        currencies = sorted(
            {
                str(item.get("currency"))
                for item in infos
                if isinstance(item, Mapping) and item.get("currency") is not None
            }
        )
        return None, ",".join(currencies) if currencies else "NONE"
    balance = _decimal(cny_rows[0].get("total_balance"), "DeepSeek.total_balance")
    if payload.get("is_available") is False:
        return Decimal("0"), None
    return balance, None


def _missing_credential(spec: ProviderSpec, required: Decimal) -> ProviderBalanceReadiness:
    return ProviderBalanceReadiness(
        provider_id=spec.provider_id,
        model_id=spec.model_id,
        credential_present=False,
        balance_method="NOT_ATTEMPTED_WITHOUT_CREDENTIAL",
        balance_checked=False,
        existing_balance_cny=None,
        required_stage_a_cny=required,
        shortfall_cny=None,
        status=CREDENTIAL_MISSING,
        detail=f"{spec.api_key_env} is unavailable in the current execution environment",
    )


def _auth_failed(spec: ProviderSpec, required: Decimal, method: str) -> ProviderBalanceReadiness:
    return ProviderBalanceReadiness(
        provider_id=spec.provider_id,
        model_id=spec.model_id,
        credential_present=True,
        balance_method=method,
        balance_checked=False,
        existing_balance_cny=None,
        required_stage_a_cny=required,
        shortfall_cny=None,
        status=AUTH_FAILED,
        detail="official read-only balance endpoint rejected authentication",
    )


def _balance_result(
    spec: ProviderSpec,
    required: Decimal,
    *,
    method: str,
    balance: Decimal,
) -> ProviderBalanceReadiness:
    if balance >= required:
        status = READY_EXISTING_FUNDS
        shortfall = Decimal("0")
        detail = "existing CNY balance covers the provider's full frozen Stage-A worst case"
    else:
        status = INSUFFICIENT_EXISTING_FUNDS
        shortfall = required - balance
        detail = "existing CNY balance is below the provider's full frozen Stage-A worst case"
    return ProviderBalanceReadiness(
        provider_id=spec.provider_id,
        model_id=spec.model_id,
        credential_present=True,
        balance_method=method,
        balance_checked=True,
        existing_balance_cny=balance,
        required_stage_a_cny=required,
        shortfall_cny=shortfall,
        status=status,
        detail=detail,
    )


def check_provider_readiness(
    plan: VerifiedFrozenStageAPlan,
    *,
    provider_id: str,
    credential_lookup: Callable[[str], str | None] = os.environ.get,
    http_get: HttpGet = _default_http_get,
    timeout_seconds: float = 10.0,
) -> ProviderBalanceReadiness:
    if not isinstance(timeout_seconds, (int, float)) or isinstance(timeout_seconds, bool) or timeout_seconds <= 0:
        raise ProviderReadinessError("timeout_seconds must be positive")
    spec = _find_spec(provider_id)
    required = required_stage_a_cny(plan, provider_id)
    credential = credential_lookup(spec.api_key_env)
    if not isinstance(credential, str) or not credential:
        return _missing_credential(spec, required)

    if provider_id == "MINIMAX":
        return ProviderBalanceReadiness(
            provider_id=spec.provider_id,
            model_id=spec.model_id,
            credential_present=True,
            balance_method="NO_VERIFIED_READ_ONLY_PAYGO_BALANCE_API",
            balance_checked=False,
            existing_balance_cny=None,
            required_stage_a_cny=required,
            shortfall_cny=None,
            status=UNRESOLVED_NO_READ_ONLY_PAYGO_BALANCE_API,
            detail="MiniMax pay-as-you-go readiness remains unresolved; no billable model probe is permitted",
        )

    endpoint = KIMI_BALANCE_ENDPOINT if provider_id == "KIMI" else DEEPSEEK_BALANCE_ENDPOINT
    method = f"GET {endpoint}"
    status_code, body = http_get(
        endpoint,
        {"Authorization": f"Bearer {credential}", "Accept": "application/json"},
        float(timeout_seconds),
    )
    if status_code in {401, 403}:
        return _auth_failed(spec, required, method)
    if status_code != 200:
        return ProviderBalanceReadiness(
            provider_id=spec.provider_id,
            model_id=spec.model_id,
            credential_present=True,
            balance_method=method,
            balance_checked=False,
            existing_balance_cny=None,
            required_stage_a_cny=required,
            shortfall_cny=None,
            status=BALANCE_CHECK_FAILED,
            detail=f"official read-only balance endpoint returned HTTP {status_code}",
        )

    try:
        payload = _parse_json(body)
        if provider_id == "KIMI":
            balance = _parse_kimi_balance(payload)
            return _balance_result(spec, required, method=method, balance=balance)
        balance, non_cny = _parse_deepseek_balance(payload)
    except ProviderReadinessError as error:
        return ProviderBalanceReadiness(
            provider_id=spec.provider_id,
            model_id=spec.model_id,
            credential_present=True,
            balance_method=method,
            balance_checked=False,
            existing_balance_cny=None,
            required_stage_a_cny=required,
            shortfall_cny=None,
            status=BALANCE_CHECK_FAILED,
            detail=str(error),
        )
    if balance is None:
        return ProviderBalanceReadiness(
            provider_id=spec.provider_id,
            model_id=spec.model_id,
            credential_present=True,
            balance_method=method,
            balance_checked=True,
            existing_balance_cny=None,
            required_stage_a_cny=required,
            shortfall_cny=None,
            status=UNRESOLVED_NON_CNY_BALANCE,
            detail=f"DeepSeek returned no CNY balance row; currencies={non_cny}",
        )
    return _balance_result(spec, required, method=method, balance=balance)


def check_all_provider_readiness(
    plan: VerifiedFrozenStageAPlan,
    *,
    credential_lookup: Callable[[str], str | None] = os.environ.get,
    http_get: HttpGet = _default_http_get,
    timeout_seconds: float = 10.0,
) -> tuple[ProviderBalanceReadiness, ...]:
    return tuple(
        check_provider_readiness(
            plan,
            provider_id=spec.provider_id,
            credential_lookup=credential_lookup,
            http_get=http_get,
            timeout_seconds=timeout_seconds,
        )
        for spec in IMPLEMENTATION_TARGET_SPECS
    )


__all__ = [
    "AUTH_FAILED",
    "BALANCE_CHECK_FAILED",
    "CREDENTIAL_MISSING",
    "DEEPSEEK_BALANCE_ENDPOINT",
    "INSUFFICIENT_EXISTING_FUNDS",
    "KIMI_BALANCE_ENDPOINT",
    "ProviderBalanceReadiness",
    "ProviderReadinessError",
    "READY_EXISTING_FUNDS",
    "READINESS_VERSION",
    "UNRESOLVED_NON_CNY_BALANCE",
    "UNRESOLVED_NO_READ_ONLY_PAYGO_BALANCE_API",
    "check_all_provider_readiness",
    "check_provider_readiness",
    "required_stage_a_cny",
]
