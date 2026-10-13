"""Deterministic REAL risk policy bindings (additive, UNBOUND by default).

This module owns the *policy* side of the REAL risk/safety primitives: an
explicit, versioned set of risk-policy bindings that a future real-risk
authority may BOUND. Every permanent value is UNBOUND by default and no value is
derived from any capital envelope. A
binding is only ``BOUND`` when an explicit value was supplied by authority.

This is a pure, deterministic, offline decision-input schema. It performs no
broker, provider, account or real-money action and decides nothing by itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Any

REAL_RISK_POLICY_SCHEMA_VERSION = "real-risk-policy-v0.1"

FIXTURE_ONLY_WARNING = (
    "Any numeric value used in tests is an explicit FIXTURE-ONLY value; "
    "it is not a permanent real-money risk limit."
)


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class BindingStatus(str, Enum):
    """Explicit per-binding status (BOUND only when a value was supplied)."""

    BOUND = "BOUND"
    UNBOUND = "UNBOUND"


class PolicyBinding(str, Enum):
    """Every explicit policy binding a future real-risk authority may BOUND."""

    PRODUCT_WHITELIST = "product_whitelist"
    CONTRACT_AUTHORIZATION = "contract_authorization"
    MAX_POSITION_QUANTITY = "max_position_quantity"
    ALLOW_ADD_ON = "allow_add_on"
    PER_TRADE_RISK_CEILING = "per_trade_risk_ceiling"
    DAILY_LOSS_CEILING = "daily_loss_ceiling"
    DAILY_RISK_CEILING = "daily_risk_ceiling"
    CUMULATIVE_LOSS_CEILING = "cumulative_loss_ceiling"
    DRAWDOWN_CEILING = "drawdown_ceiling"
    MINIMUM_MARGIN_HEADROOM = "minimum_margin_headroom"
    OPERATIONAL_RESERVE_HEADROOM = "operational_reserve_headroom"


# Bindings that must be BOUND before any risk-increasing action may be ALLOWED.
# The operational reserve is deliberately excluded: it is enforced only when a
# real-risk authority actually supplies it.
REQUIRED_BINDINGS = frozenset(
    {
        PolicyBinding.PRODUCT_WHITELIST,
        PolicyBinding.CONTRACT_AUTHORIZATION,
        PolicyBinding.MAX_POSITION_QUANTITY,
        PolicyBinding.ALLOW_ADD_ON,
        PolicyBinding.PER_TRADE_RISK_CEILING,
        PolicyBinding.DAILY_LOSS_CEILING,
        PolicyBinding.DAILY_RISK_CEILING,
        PolicyBinding.CUMULATIVE_LOSS_CEILING,
        PolicyBinding.DRAWDOWN_CEILING,
        PolicyBinding.MINIMUM_MARGIN_HEADROOM,
    }
)

OPTIONAL_BINDINGS = frozenset({PolicyBinding.OPERATIONAL_RESERVE_HEADROOM})

_ALL_BINDINGS = tuple(sorted(REQUIRED_BINDINGS | OPTIONAL_BINDINGS, key=lambda item: item.value))


def _positive_decimal(value: Decimal, name: str) -> None:
    if type(value) is not Decimal or not value.is_finite() or value <= 0:
        raise ValueError(f"{name} must be a positive finite Decimal")


def _identifier_set(value: frozenset[str] | None, name: str) -> None:
    if value is None:
        return
    if not isinstance(value, frozenset) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{name} must be a frozenset of non-empty strings or None")


@dataclass(frozen=True)
class RealRiskPolicy:
    """Versioned REAL risk-policy bindings (all permanent values UNBOUND by default).

    Every binding is ``None`` (UNBOUND) until a real-risk authority explicitly
    supplies a value. Values are never derived from a capital envelope.
    """

    policy_id: str
    version: str
    product_whitelist: frozenset[str] | None = None
    contract_authorization: frozenset[str] | None = None
    max_position_quantity: Decimal | None = None
    allow_add_on: bool | None = None
    per_trade_risk_ceiling: Decimal | None = None
    daily_loss_ceiling: Decimal | None = None
    daily_risk_ceiling: Decimal | None = None
    cumulative_loss_ceiling: Decimal | None = None
    drawdown_ceiling: Decimal | None = None
    minimum_margin_headroom: Decimal | None = None
    operational_reserve_headroom: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.policy_id or not self.version:
            raise ValueError("risk policy requires an id and version")
        _identifier_set(self.product_whitelist, "product whitelist")
        _identifier_set(self.contract_authorization, "contract authorization")
        for name in (
            "max_position_quantity",
            "per_trade_risk_ceiling",
            "daily_loss_ceiling",
            "daily_risk_ceiling",
            "cumulative_loss_ceiling",
            "drawdown_ceiling",
            "minimum_margin_headroom",
            "operational_reserve_headroom",
        ):
            value = getattr(self, name)
            if value is not None:
                _positive_decimal(value, name)
        if self.allow_add_on is not None and type(self.allow_add_on) is not bool:
            raise ValueError("allow_add_on must be a bool or None")

    def _value_for(self, binding: PolicyBinding) -> Any:
        return {
            PolicyBinding.PRODUCT_WHITELIST: self.product_whitelist,
            PolicyBinding.CONTRACT_AUTHORIZATION: self.contract_authorization,
            PolicyBinding.MAX_POSITION_QUANTITY: self.max_position_quantity,
            PolicyBinding.ALLOW_ADD_ON: self.allow_add_on,
            PolicyBinding.PER_TRADE_RISK_CEILING: self.per_trade_risk_ceiling,
            PolicyBinding.DAILY_LOSS_CEILING: self.daily_loss_ceiling,
            PolicyBinding.DAILY_RISK_CEILING: self.daily_risk_ceiling,
            PolicyBinding.CUMULATIVE_LOSS_CEILING: self.cumulative_loss_ceiling,
            PolicyBinding.DRAWDOWN_CEILING: self.drawdown_ceiling,
            PolicyBinding.MINIMUM_MARGIN_HEADROOM: self.minimum_margin_headroom,
            PolicyBinding.OPERATIONAL_RESERVE_HEADROOM: self.operational_reserve_headroom,
        }[binding]

    def binding_status(self, binding: PolicyBinding) -> BindingStatus:
        """Explicit BOUND/UNBOUND for one binding.

        An empty whitelist / authorization set is not an established binding
        (it authorizes nothing) and is reported as UNBOUND.
        """
        if not isinstance(binding, PolicyBinding):
            raise ValueError("binding must be a PolicyBinding")
        value = self._value_for(binding)
        if value is None:
            return BindingStatus.UNBOUND
        if binding in (PolicyBinding.PRODUCT_WHITELIST, PolicyBinding.CONTRACT_AUTHORIZATION):
            if len(value) == 0:
                return BindingStatus.UNBOUND
        return BindingStatus.BOUND

    def unbound_bindings(self) -> tuple[PolicyBinding, ...]:
        return tuple(binding for binding in _ALL_BINDINGS if self.binding_status(binding) is BindingStatus.UNBOUND)

    def bound_bindings(self) -> tuple[PolicyBinding, ...]:
        return tuple(binding for binding in _ALL_BINDINGS if self.binding_status(binding) is BindingStatus.BOUND)

    def required_unbound_bindings(self) -> tuple[PolicyBinding, ...]:
        """Required bindings that are still UNBOUND (fail-closed for risk increase)."""
        return tuple(
            binding
            for binding in sorted(REQUIRED_BINDINGS, key=lambda item: item.value)
            if self.binding_status(binding) is BindingStatus.UNBOUND
        )

    def is_fully_bound(self) -> bool:
        """True when every required binding is BOUND (operational reserve optional)."""
        return not self.required_unbound_bindings()

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "policy_id": self.policy_id,
                "version": self.version,
                "product_whitelist": None
                if self.product_whitelist is None
                else sorted(self.product_whitelist),
                "contract_authorization": None
                if self.contract_authorization is None
                else sorted(self.contract_authorization),
                "max_position_quantity": None
                if self.max_position_quantity is None
                else str(self.max_position_quantity),
                "allow_add_on": self.allow_add_on,
                "per_trade_risk_ceiling": None
                if self.per_trade_risk_ceiling is None
                else str(self.per_trade_risk_ceiling),
                "daily_loss_ceiling": None
                if self.daily_loss_ceiling is None
                else str(self.daily_loss_ceiling),
                "daily_risk_ceiling": None
                if self.daily_risk_ceiling is None
                else str(self.daily_risk_ceiling),
                "cumulative_loss_ceiling": None
                if self.cumulative_loss_ceiling is None
                else str(self.cumulative_loss_ceiling),
                "drawdown_ceiling": None
                if self.drawdown_ceiling is None
                else str(self.drawdown_ceiling),
                "minimum_margin_headroom": None
                if self.minimum_margin_headroom is None
                else str(self.minimum_margin_headroom),
                "operational_reserve_headroom": None
                if self.operational_reserve_headroom is None
                else str(self.operational_reserve_headroom),
            }
        )
