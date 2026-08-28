"""Side-effect-free composition for the eventual external PAPER candidate path.

All account/session/provider objects arrive through an explicit local factory.
This module opens only project-owned local state; connection is owned by the
controller's explicit preflight/start boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.paper_activation_profile import PaperActivationProfile
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import PaperAuthoritySource
from src.paper_execution_chain import PaperDeterministicExecutionChain
from src.paper_live_causal_context import LiveCausalContextBuilder, LiveSessionCalendar
from src.paper_order_journal import PaperOrderJournal
from src.paper_runtime import JournalManagedPaperBroker, PaperTrader
from src.paper_runtime_assembly import (
    PaperRuntimeAssemblyInputs,
    assemble_paper_runtime,
)
from src.paper_runtime_bindings import PaperExecutableBindings, PaperToolRoleBinding
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_runtime_controller import PaperRuntimeController
from src.paper_runtime_layout import PaperRuntimeLayout
from src.paper_wake_journal import PaperWakeJournal


@dataclass(frozen=True)
class PaperExternalComponents:
    broker: JournalManagedPaperBroker
    source: object
    trader: PaperTrader
    execution_chain: PaperDeterministicExecutionChain
    executable_bindings: PaperExecutableBindings


@dataclass(frozen=True)
class PaperExternalFactories:
    authority_source: PaperAuthoritySource
    activation_profile: PaperActivationProfile
    paper_tool_role: PaperToolRoleBinding
    sessions: LiveSessionCalendar
    create_components: Callable[
        [PaperOrderJournal, PaperWakeJournal, LiveCausalContextBuilder],
        PaperExternalComponents,
    ]


def build_external_paper_controller(
    *,
    config: PaperRuntimeConfig,
    layout: PaperRuntimeLayout,
    factories: PaperExternalFactories,
) -> PaperRuntimeController:
    """Build the exact external candidate graph without connecting anything."""
    if config.activation_profile is not factories.activation_profile:
        raise ValueError("PAPER_EXTERNAL_CONFIG_PROFILE_MISMATCH")
    if config.authority is None or (
        factories.authority_source.current().identity_id != config.authority.identity_id
    ):
        raise ValueError("PAPER_EXTERNAL_CONFIG_AUTHORITY_MISMATCH")
    if config.paper_tool_role is not factories.paper_tool_role:
        raise ValueError("PAPER_EXTERNAL_CONFIG_TOOL_ROLE_MISMATCH")
    if config.account_identity is None:
        raise ValueError("PAPER_EXTERNAL_ACCOUNT_IDENTITY_REQUIRED")

    lease = layout.acquire_lease()
    order_journal = None
    wake_journal = None
    try:
        layout.ensure_initialized()
        order_journal = PaperOrderJournal(
            layout.order_journal_path, require_full_envelope=True
        )
        wake_journal = PaperWakeJournal(layout.wake_journal_path)
        if layout.causal_checkpoint_path.exists():
            context_builder = LiveCausalContextBuilder.from_checkpoint(
                layout.read_causal_checkpoint(), calendar=factories.sessions
            )
        else:
            instrument = config.concrete_contract_id.split(".", 1)[1]
            context_builder = LiveCausalContextBuilder(
                exchange=config.exchange,
                concrete_instrument=instrument,
                product=config.product,
                calendar=factories.sessions,
            )
        components = factories.create_components(
            order_journal, wake_journal, context_builder
        )
        mirror = PaperBrokerTruthMirror(
            broker_id=components.broker.broker_id,
            expected_account_id=config.account_identity,
        )
        assembly = assemble_paper_runtime(PaperRuntimeAssemblyInputs(
            trader_identity=config.trader_identity,
            concrete_contract_id=config.concrete_contract_id,
            exchange=config.exchange,
            product=config.product,
            actual_tqsdk_runtime_version=config.tqsdk_runtime_version,
            authority=config.authority,
            authority_source=factories.authority_source,
            activation_profile=factories.activation_profile,
            sessions=factories.sessions,
            context_builder=context_builder,
            wake_journal=wake_journal,
            order_journal=order_journal,
            broker_mirror=mirror,
            broker=components.broker,
            trader=components.trader,
            risk_planner=None,
            execution_chain=components.execution_chain,
            executable_bindings=components.executable_bindings,
            paper_tool_role=factories.paper_tool_role,
            source=components.source,
            timezone=config.timezone,
            symbol=config.symbol,
            source_poll_limit=config.source_poll_limit,
            max_source_age_seconds=config.max_source_age_seconds,
            require_external_readiness=True,
        ))
        controller = PaperRuntimeController(
            config=config, layout=layout, assembly=assembly, state_lease=lease
        )
        lease = None
        return controller
    except Exception:
        if order_journal is not None:
            order_journal.close()
        if wake_journal is not None:
            wake_journal.close()
        raise
    finally:
        if lease is not None:
            lease.release()


__all__ = [
    "PaperExternalComponents",
    "PaperExternalFactories",
    "build_external_paper_controller",
]
