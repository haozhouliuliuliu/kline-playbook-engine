"""Side-effect-free PAPER runtime assembly seam for future login-time startup.

OFFLINE ONLY. This module composes the existing project runtime objects from
explicit injected dependencies. Calling ``assemble_paper_runtime`` performs
ZERO side effects: it never calls ``broker.connect()``, never starts a network
session, never reads credentials, never calls DeepSeek, never submits/cancels/
replaces an order and never mutates external account state.

The future activation boundary stays explicit:

    construct != connect != observe != submit order

This factory only wires objects. Activation (connect -> broker truth ->
market bootstrap -> trader-ready -> observe) is performed later through the
returned ``PaperRuntimeCoordinator`` / ``PaperLiveOneMinuteTransport`` under the
separate exact PAPER authorization. Result-dependent values (sizing, execution
price, close-offset, permanent risk, final contract whitelist) are never
invented here; they arrive as approved injected objects (activation profile,
authority, trader, risk planner, policies) when they exist.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.paper_activation_profile import PaperActivationProfile
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import PaperAuthoritySource, PaperExecutionAuthority
from src.paper_execution_chain import PaperDeterministicExecutionChain
from src.paper_runtime_bindings import PaperExecutableBindings, PaperToolRoleBinding
from src.paper_live_causal_context import LiveCausalContextBuilder, LiveSessionCalendar
from src.paper_live_transport import (
    PAPER_LIVE_TRANSPORT_VERSION,
    LiveOneMinuteSource,
    PaperLiveOneMinuteTransport,
)
from src.paper_order_journal import PaperOrderJournal
from src.paper_runtime import (
    PAPER_RUNTIME_COORDINATOR_VERSION,
    JournalManagedPaperBroker,
    PaperRiskPlanner,
    PaperRuntimeCoordinator,
    PaperTrader,
)
from src.paper_supervisor import PaperRuntimeSupervisor
from src.paper_wake_journal import PaperWakeJournal

PAPER_RUNTIME_ASSEMBLY_VERSION = "KPE_PAPER_RUNTIME_ASSEMBLY_V0_1"


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


@dataclass(frozen=True)
class PaperRuntimeAssemblyInputs:
    """Every injected dependency/config the factory wires together.

    Strategy-result-dependent values are NOT defined here. The caller supplies
    the approved authority, activation profile, trader, risk planner, broker and
    source objects when (and only when) they exist.
    """

    trader_identity: str
    concrete_contract_id: str
    exchange: str
    product: str
    actual_tqsdk_runtime_version: str

    authority: PaperExecutionAuthority
    activation_profile: PaperActivationProfile
    sessions: LiveSessionCalendar
    context_builder: LiveCausalContextBuilder
    wake_journal: PaperWakeJournal
    order_journal: PaperOrderJournal
    broker_mirror: PaperBrokerTruthMirror
    broker: JournalManagedPaperBroker
    trader: PaperTrader
    risk_planner: PaperRiskPlanner
    source: LiveOneMinuteSource

    supervisor: PaperRuntimeSupervisor | None = None
    authority_source: PaperAuthoritySource | None = None
    execution_chain: PaperDeterministicExecutionChain | None = None
    executable_bindings: PaperExecutableBindings | None = None
    paper_tool_role: PaperToolRoleBinding | None = None
    require_external_readiness: bool = False
    timezone: str = "Asia/Shanghai"
    symbol: str | None = None
    source_poll_limit: int = 512
    max_source_age_seconds: int | None = None
    max_broker_snapshot_age_seconds: int = 30


@dataclass(frozen=True)
class PaperRuntimeAssembly:
    """Composed, side-effect-free runtime bundle returned by the factory."""

    assembly_identity: str
    coordinator: PaperRuntimeCoordinator
    supervisor: PaperRuntimeSupervisor
    transport: PaperLiveOneMinuteTransport
    context_builder: LiveCausalContextBuilder
    broker: JournalManagedPaperBroker
    trader_identity: str
    concrete_contract_id: str
    activation_profile: PaperActivationProfile
    authority_source: PaperAuthoritySource
    executable_bindings: PaperExecutableBindings | None
    paper_tool_role: PaperToolRoleBinding | None
    require_external_readiness: bool

    def startup_steps(self) -> tuple[tuple[str, str], ...]:
        """Informational, non-executing ordered activation steps.

        These steps are the explicit activation boundary; this method only
        documents them and never performs any of them.
        """
        return (
            ("construct", "assemble_paper_runtime (this bundle, already done, zero side effects)"),
            ("connect", "coordinator.connect(at=...) -> broker.connect + broker truth/reconciliation"),
            ("bootstrap", "transport.bootstrap(observed_at=...) -> seed causal context, no historical wake storm"),
            ("ready", "coordinator.mark_trader_runtime_ready(True)"),
            ("observe", "transport.poll(observed_at=...) -> coordinator.process_closed_minutes"),
            ("submit_order", "only via coordinator risk-planner path under require_order_ready"),
        )


def assemble_paper_runtime(inputs: PaperRuntimeAssemblyInputs) -> PaperRuntimeAssembly:
    """Compose the existing project runtime objects with NO side effects.

    Raises on any wiring/identity inconsistency (fail closed); it never connects,
    reads credentials, calls a provider, submits/cancels/replaces an order or
    mutates external state.
    """
    if not isinstance(inputs, PaperRuntimeAssemblyInputs):
        raise TypeError("paper runtime assembly requires PaperRuntimeAssemblyInputs")
    trader_identity = _text(inputs.trader_identity, "paper assembly trader identity")
    concrete_contract_id = _text(inputs.concrete_contract_id, "paper assembly concrete contract")
    exchange = _text(inputs.exchange, "paper assembly exchange")
    product = _text(inputs.product, "paper assembly product")
    declared_runtime_version = _text(
        inputs.actual_tqsdk_runtime_version, "paper assembly runtime version"
    )
    broker_runtime_version = getattr(inputs.broker, "runtime_version", None)
    runtime_version = (
        _text(broker_runtime_version, "paper broker runtime version")
        if inputs.require_external_readiness
        else declared_runtime_version
    )
    if inputs.require_external_readiness and runtime_version == "UNVERIFIED":
        raise ValueError("PAPER_EXTERNAL_RUNTIME_VERSION_UNPROVABLE")
    if inputs.require_external_readiness and runtime_version != declared_runtime_version:
        raise ValueError("PAPER_EXTERNAL_RUNTIME_VERSION_MISMATCH")
    if inputs.timezone != "Asia/Shanghai":
        raise ValueError("paper assembly timezone must be Asia/Shanghai")
    if type(inputs.source_poll_limit) is not int or inputs.source_poll_limit <= 0:
        raise ValueError("paper assembly source poll limit must be a positive integer")
    if inputs.max_source_age_seconds is not None and (
        type(inputs.max_source_age_seconds) is not int or inputs.max_source_age_seconds <= 0
    ):
        raise ValueError("paper assembly max source age must be a positive integer")
    if type(inputs.max_broker_snapshot_age_seconds) is not int or inputs.max_broker_snapshot_age_seconds < 0:
        raise ValueError("paper assembly broker snapshot age must be a non-negative integer")
    if type(inputs.require_external_readiness) is not bool:
        raise ValueError("paper external readiness flag must be bool")

    # Identity consistency checks (fail closed; all offline).
    if not isinstance(inputs.authority, PaperExecutionAuthority):
        raise ValueError("paper assembly requires PaperExecutionAuthority")
    if not isinstance(inputs.activation_profile, PaperActivationProfile):
        raise ValueError("paper assembly requires PaperActivationProfile")
    if not isinstance(inputs.sessions, LiveSessionCalendar):
        raise ValueError("paper assembly requires LiveSessionCalendar")
    if not isinstance(inputs.context_builder, LiveCausalContextBuilder):
        raise ValueError("paper assembly requires LiveCausalContextBuilder")
    if not isinstance(inputs.wake_journal, PaperWakeJournal):
        raise ValueError("paper assembly requires PaperWakeJournal")
    if not isinstance(inputs.order_journal, PaperOrderJournal):
        raise ValueError("paper assembly requires PaperOrderJournal")
    if not isinstance(inputs.broker_mirror, PaperBrokerTruthMirror):
        raise ValueError("paper assembly requires PaperBrokerTruthMirror")
    if inputs.sessions.product != product:
        raise ValueError("paper assembly product disagrees with the session calendar")
    if inputs.context_builder.product != product:
        raise ValueError("paper assembly product disagrees with the context builder")
    if inputs.context_builder.exchange != exchange:
        raise ValueError("paper assembly exchange disagrees with the context builder")
    authority_source = inputs.authority_source
    if authority_source is None and inputs.supervisor is not None:
        authority_source = inputs.supervisor.authority_source
    if authority_source is None:
        from src.paper_execution_authority import MutablePaperAuthoritySource
        authority_source = MutablePaperAuthoritySource(
            inputs.authority, source_identity="STATIC_LEGACY_AUTHORITY_SOURCE"
        )
    if authority_source.current().identity_id != inputs.authority.identity_id:
        raise ValueError("PAPER_ASSEMBLY_AUTHORITY_SOURCE_MISMATCH")
    if inputs.executable_bindings is not None:
        inputs.executable_bindings.require_matches(inputs.activation_profile)
    if inputs.require_external_readiness:
        from src.tqsdk_live_source import TqSdkLiveOneMinuteSource
        from src.tqsdk_paper_candidate import TqSdkPaperBrokerAdapter

        if authority_source.source_identity == "STATIC_LEGACY_AUTHORITY_SOURCE":
            raise ValueError("PAPER_EXTERNAL_CURRENT_AUTHORITY_SOURCE_REQUIRED")
        if not isinstance(inputs.broker, TqSdkPaperBrokerAdapter):
            raise ValueError("PAPER_EXTERNAL_TQSDK_CANDIDATE_BROKER_REQUIRED")
        if not isinstance(inputs.source, TqSdkLiveOneMinuteSource):
            raise ValueError("PAPER_EXTERNAL_TQSDK_LIVE_SOURCE_REQUIRED")
        if inputs.source.session_owner is not inputs.broker.session_owner:
            raise ValueError("PAPER_EXTERNAL_TQSDK_SESSION_OWNERSHIP_MISMATCH")
        if inputs.execution_chain is None or inputs.risk_planner is not None:
            raise ValueError("PAPER_EXTERNAL_REQUIRES_CANONICAL_EXECUTION_CHAIN")
        if inputs.executable_bindings is None:
            raise ValueError("PAPER_EXTERNAL_EXECUTABLE_BINDINGS_REQUIRED")
        if inputs.paper_tool_role is None:
            raise ValueError("PAPER_EXTERNAL_TOOL_ROLE_BINDING_REQUIRED")
        if inputs.max_source_age_seconds is None:
            raise ValueError("PAPER_EXTERNAL_SOURCE_FRESHNESS_POLICY_REQUIRED")
        if inputs.symbol != concrete_contract_id:
            raise ValueError("PAPER_EXTERNAL_FULL_CONTRACT_SYMBOL_REQUIRED")
        if inputs.broker_mirror.expected_account_id != inputs.authority.account_identity:
            raise ValueError("PAPER_EXTERNAL_ACCOUNT_MIRROR_BINDING_MISMATCH")
        if getattr(inputs.broker, "account_identity", None) != inputs.authority.account_identity:
            raise ValueError("PAPER_EXTERNAL_BROKER_ACCOUNT_BINDING_MISMATCH")
        if not inputs.order_journal.require_full_envelope:
            raise ValueError("PAPER_EXTERNAL_FULL_ORDER_ENVELOPE_REQUIRED")
        if inputs.executable_bindings.live_data_policy is not inputs.source:
            raise ValueError("PAPER_EXTERNAL_LIVE_POLICY_OBJECT_MISMATCH")
        if inputs.executable_bindings.broker_adapter is not inputs.broker:
            raise ValueError("PAPER_EXTERNAL_BROKER_OBJECT_MISMATCH")
        if inputs.executable_bindings.risk_policy is not inputs.execution_chain.risk_gate:
            raise ValueError("PAPER_EXTERNAL_RISK_OBJECT_MISMATCH")
        if inputs.executable_bindings.sizing_policy is not inputs.execution_chain.bridge.policy:
            raise ValueError("PAPER_EXTERNAL_SIZING_OBJECT_MISMATCH")
        if getattr(inputs.broker, "execution_price_policy", None) is not inputs.executable_bindings.execution_price_policy:
            raise ValueError("PAPER_EXTERNAL_PRICE_POLICY_OBJECT_MISMATCH")
        if getattr(inputs.broker, "close_offset_policy", None) is not inputs.executable_bindings.close_offset_policy:
            raise ValueError("PAPER_EXTERNAL_CLOSE_OFFSET_OBJECT_MISMATCH")
    # The live context layer keys on the bare instrument (e.g. ``cu2406``) while
    # the coordinator/order layer keys on the full concrete contract id (e.g.
    # ``SHFE.cu2406``). Both are preserved here; the transport reuses the context
    # builder's instrument so the causal substrate and the runtime agree.
    live_instrument = inputs.context_builder.concrete_instrument
    if not isinstance(live_instrument, str) or not live_instrument.strip():
        raise ValueError("paper assembly context builder instrument must be non-empty")
    # The coordinator itself re-validates broker/journal/mirror identities.

    supervisor = inputs.supervisor
    if supervisor is None:
        supervisor = PaperRuntimeSupervisor(
            actual_tqsdk_runtime_version=runtime_version,
            authority=inputs.authority,
            activation_profile=inputs.activation_profile,
            broker_mirror=inputs.broker_mirror,
            order_journal=inputs.order_journal,
            wake_journal=inputs.wake_journal,
            authority_source=authority_source,
        )
    else:
        if supervisor.activation_profile is not inputs.activation_profile:
            raise ValueError("PAPER_ASSEMBLY_SUPERVISOR_PROFILE_MISMATCH")
        if supervisor.authority_source.current().identity_id != inputs.authority.identity_id:
            raise ValueError("PAPER_ASSEMBLY_SUPERVISOR_AUTHORITY_MISMATCH")

    coordinator = PaperRuntimeCoordinator(
        trader_identity=trader_identity,
        concrete_contract_id=concrete_contract_id,
        context_builder=inputs.context_builder,
        wake_journal=inputs.wake_journal,
        order_journal=inputs.order_journal,
        broker_mirror=inputs.broker_mirror,
        supervisor=supervisor,
        broker=inputs.broker,
        trader=inputs.trader,
        risk_planner=inputs.risk_planner,
        execution_chain=inputs.execution_chain,
        authority_source=authority_source,
        max_broker_snapshot_age_seconds=inputs.max_broker_snapshot_age_seconds,
    )

    transport = PaperLiveOneMinuteTransport(
        exchange=exchange,
        concrete_contract_id=concrete_contract_id,
        concrete_instrument=live_instrument,
        product=product,
        sessions=inputs.sessions,
        source=inputs.source,
        consumer=coordinator,
        timezone=inputs.timezone,
        duration_seconds=60,
        symbol=inputs.symbol,
        source_poll_limit=inputs.source_poll_limit,
        max_source_age_seconds=inputs.max_source_age_seconds,
        require_source_freshness=inputs.require_external_readiness,
        require_exact_source_identity=inputs.require_external_readiness,
    )

    assembly_identity = _hash({
        "assembly_version": PAPER_RUNTIME_ASSEMBLY_VERSION,
        "trader_identity": trader_identity,
        "concrete_contract_id": concrete_contract_id,
        "exchange": exchange,
        "product": product,
        "authority_identity": inputs.authority.identity_id,
        "authority_source_identity": authority_source.source_identity,
        "activation_profile_identity": inputs.activation_profile.identity_id,
        "session_calendar_identity": inputs.sessions.identity,
        "context_policy_identity": inputs.context_builder.policy_identity,
        "broker_mirror_id": inputs.broker_mirror.broker_id,
        "broker_id": inputs.broker.broker_id,
        "broker_implementation_identity": getattr(inputs.broker, "identity_id", None),
        "trader_implementation_identity": getattr(inputs.trader, "identity_id", None),
        "source_implementation_identity": getattr(inputs.source, "identity_id", None),
        "execution_chain_identity": (
            None if inputs.execution_chain is None else inputs.execution_chain.identity_id
        ),
        "executable_bindings_identity": (
            None if inputs.executable_bindings is None else inputs.executable_bindings.identity_id
        ),
        "paper_tool_role_identity": (
            None if inputs.paper_tool_role is None else inputs.paper_tool_role.identity_id
        ),
        "order_journal_path": str(inputs.order_journal.path.resolve()),
        "wake_journal_path": str(inputs.wake_journal.path.resolve()),
        "coordinator_version": PAPER_RUNTIME_COORDINATOR_VERSION,
        "transport_version": PAPER_LIVE_TRANSPORT_VERSION,
    })

    return PaperRuntimeAssembly(
        assembly_identity=assembly_identity,
        coordinator=coordinator,
        supervisor=supervisor,
        transport=transport,
        context_builder=inputs.context_builder,
        broker=inputs.broker,
        trader_identity=trader_identity,
        concrete_contract_id=concrete_contract_id,
        activation_profile=inputs.activation_profile,
        authority_source=authority_source,
        executable_bindings=inputs.executable_bindings,
        paper_tool_role=inputs.paper_tool_role,
        require_external_readiness=inputs.require_external_readiness,
    )


__all__ = [
    "PAPER_RUNTIME_ASSEMBLY_VERSION",
    "PaperRuntimeAssembly",
    "PaperRuntimeAssemblyInputs",
    "assemble_paper_runtime",
]
