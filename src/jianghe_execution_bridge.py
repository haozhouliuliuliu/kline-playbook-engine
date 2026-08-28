"""Fail-closed seam from Jianghe model decisions to executable strategy intents.

The active Jianghe response contract contains trading judgment but intentionally
does not freeze quantity/order-type/sizing semantics.  This bridge therefore
allows non-executable decisions through as HOLD and blocks any decision that
would create/change exposure until an explicit project-owned execution policy
is supplied.  It never infers quantity or order type from free text.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from hashlib import sha256
import json

from src.intent import IntentAction, StrategyIntent
from src.jianghe_ai_trader import DecisionAction
from src.jianghe_response_normalizer import NormalizedJiangheDecision


JIANGHE_EXECUTION_BRIDGE_VERSION = "KPE_JIANGHE_EXECUTION_BRIDGE_V0_1"


class ExecutionSemanticsRequired(RuntimeError):
    """Raised when a model decision needs execution semantics that are not frozen."""


class JiangheExecutionPolicy(Protocol):
    """Future project-owned policy that translates executable Jianghe decisions.

    The policy, not the model rationale, owns quantity/order semantics.  A
    permanent policy is a trading/risk semantics decision and therefore remains
    an Owner gate.
    """

    identity_id: str

    def translate(
        self,
        decision: NormalizedJiangheDecision,
        *,
        strategy_identity_id: str,
        instrument: str,
        concrete_contract_id: str,
        decision_at: datetime,
        context_identity: str,
    ) -> tuple[StrategyIntent, ...]: ...


@dataclass(frozen=True)
class JiangheExecutionResolution:
    decision_identity: str
    executable: bool
    intents: tuple[StrategyIntent, ...]
    reason: str


class JiangheExecutionBridge:
    """Translate a normalized Jianghe decision without inventing order facts."""

    _NON_EXECUTABLE_ACTIONS = frozenset({
        DecisionAction.WAIT,
        DecisionAction.NO_TRADE,
        DecisionAction.WATCH,
        DecisionAction.CANDIDATE,
    })
    _EXECUTION_ACTIONS = frozenset({
        DecisionAction.ENTER,
        DecisionAction.MANAGE,
        DecisionAction.EXIT,
    })

    def __init__(self, policy: JiangheExecutionPolicy | None = None) -> None:
        if policy is not None:
            identity = getattr(policy, "identity_id", None)
            if not isinstance(identity, str) or not identity.strip():
                raise ValueError("Jianghe execution policy must expose identity_id")
        self._policy = policy

    @property
    def policy(self) -> JiangheExecutionPolicy | None:
        return self._policy

    @property
    def identity_id(self) -> str:
        payload = {
            "version": JIANGHE_EXECUTION_BRIDGE_VERSION,
            "policy_identity": None if self._policy is None else self._policy.identity_id,
        }
        return sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

    def resolve(
        self,
        decision: NormalizedJiangheDecision,
        *,
        strategy_identity_id: str,
        instrument: str,
        concrete_contract_id: str,
        decision_at: datetime,
        context_identity: str,
    ) -> JiangheExecutionResolution:
        if not isinstance(decision, NormalizedJiangheDecision):
            raise TypeError("decision must be NormalizedJiangheDecision")
        if decision_at.tzinfo is None:
            raise ValueError("decision_at must be timezone-aware")
        required = (strategy_identity_id, instrument, concrete_contract_id, context_identity)
        if any(not isinstance(value, str) or not value.strip() for value in required):
            raise ValueError("execution bridge requires complete identities")

        if decision.action in self._NON_EXECUTABLE_ACTIONS:
            intent = StrategyIntent(
                intent_id=f"jianghe-hold-{decision.identity}",
                strategy_identity_id=strategy_identity_id,
                instrument=instrument,
                concrete_contract_id=concrete_contract_id,
                action=IntentAction.HOLD,
                decision_at=decision_at,
                context_identity=context_identity,
                reason=f"JIANGHE_{decision.action.value}_NO_EXTERNAL_ORDER",
            )
            return JiangheExecutionResolution(
                decision_identity=decision.identity,
                executable=False,
                intents=(intent,),
                reason="NON_EXECUTABLE_JIANGHE_ACTION",
            )

        if decision.action not in self._EXECUTION_ACTIONS:
            raise ExecutionSemanticsRequired("UNRECOGNIZED_JIANGHE_EXECUTION_ACTION")
        if self._policy is None:
            raise ExecutionSemanticsRequired(
                f"JIANGHE_{decision.action.value}_REQUIRES_EXPLICIT_EXECUTION_POLICY"
            )

        intents = tuple(self._policy.translate(
            decision,
            strategy_identity_id=strategy_identity_id,
            instrument=instrument,
            concrete_contract_id=concrete_contract_id,
            decision_at=decision_at,
            context_identity=context_identity,
        ))
        if not intents:
            raise ExecutionSemanticsRequired("EXECUTION_POLICY_RETURNED_NO_INTENT")
        if any(not isinstance(intent, StrategyIntent) for intent in intents):
            raise TypeError("execution policy must return StrategyIntent values")
        return JiangheExecutionResolution(
            decision_identity=decision.identity,
            executable=True,
            intents=intents,
            reason="EXPLICIT_EXECUTION_POLICY",
        )
