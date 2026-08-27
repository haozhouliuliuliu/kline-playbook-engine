"""Project-owned PAPER startup preflight (usable before any external connection).

OFFLINE ONLY. This module computes a machine-clear READY / BLOCKED fact set for
starting a future PAPER runtime. It performs no login, no credential read, no
provider call, no network action and no order/broker mutation. Journal files may
be created/initialized locally on first startup (a safe, allowed first-startup
action), but no consequential external action ever occurs.

The current canonical project state has NO active PAPER connection/order
authority, so a real ``EXTERNAL`` preflight with no bound ACTIVE authority and
no bound ACTIVE activation profile correctly reports BLOCKED. An explicit
``OFFLINE_REHEARSAL`` mode may bind deterministic fake ACTIVE objects (fakes
only, never real account/order action) and pass preflight to prove the startup
surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json

from src.paper_activation_profile import PaperActivationProfile, PaperActivationStatus
from src.paper_execution_authority import PaperAuthorityStatus, PaperExecutionAuthority
from src.paper_order_journal import PaperOrderJournal
from src.paper_runtime_assembly import PaperRuntimeAssembly
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_runtime_layout import PaperRuntimeLayout
from src.paper_wake_journal import PaperWakeJournal

PAPER_PREFLIGHT_SCHEMA_VERSION = "KPE_PAPER_PREFLIGHT_V0_1"

EXTERNAL = "EXTERNAL"
OFFLINE_REHEARSAL = "OFFLINE_REHEARSAL"
_MODES = frozenset({EXTERNAL, OFFLINE_REHEARSAL})

PASS = "PASS"
BLOCK = "BLOCK"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PaperPreflightCheck:
    name: str
    status: str  # PASS | BLOCK
    detail: str

    def __post_init__(self) -> None:
        if self.status not in {PASS, BLOCK}:
            raise ValueError("preflight check status must be PASS or BLOCK")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("preflight check name must be non-empty")
        if not isinstance(self.detail, str):
            raise ValueError("preflight check detail must be text")


@dataclass(frozen=True)
class PaperPreflightReport:
    mode: str
    overall: str  # READY | BLOCKED
    checks: tuple[PaperPreflightCheck, ...]

    def __post_init__(self) -> None:
        if self.mode not in _MODES:
            raise ValueError("preflight mode must be EXTERNAL or OFFLINE_REHEARSAL")
        if self.overall not in {"READY", "BLOCKED"}:
            raise ValueError("preflight overall must be READY or BLOCKED")
        if self.overall == "READY" and any(check.status == BLOCK for check in self.checks):
            raise ValueError("READY preflight cannot contain a BLOCK check")
        if self.overall == "BLOCKED" and all(check.status == PASS for check in self.checks):
            raise ValueError("BLOCKED preflight requires at least one BLOCK check")

    @property
    def ready(self) -> bool:
        return self.overall == "READY"

    @property
    def blocked(self) -> bool:
        return self.overall == "BLOCKED"

    @property
    def blocked_checks(self) -> tuple[PaperPreflightCheck, ...]:
        return tuple(check for check in self.checks if check.status == BLOCK)

    @property
    def identity(self) -> str:
        return _hash(
            {
                "schema_version": PAPER_PREFLIGHT_SCHEMA_VERSION,
                "mode": self.mode,
                "overall": self.overall,
                "checks": [
                    {"name": check.name, "status": check.status, "detail": check.detail}
                    for check in self.checks
                ],
            }
        )

    def public_lines(self) -> tuple[str, ...]:
        """Machine-clear lines for CLI/console output. No secret values."""
        return (
            f"PAPER_PREFLIGHT_SCHEMA={PAPER_PREFLIGHT_SCHEMA_VERSION}",
            f"PAPER_PREFLIGHT_MODE={self.mode}",
            f"PAPER_PREFLIGHT_OVERALL={self.overall}",
            *(
                f"PAPER_PREFLIGHT_CHECK_{check.name}={check.status}:{check.detail}"
                for check in self.checks
            ),
            f"PAPER_PREFLIGHT_IDENTITY={self.identity}",
        )


def run_paper_preflight(
    *,
    config: PaperRuntimeConfig,
    layout: PaperRuntimeLayout,
    activation_profile: PaperActivationProfile | None = None,
    authority: PaperExecutionAuthority | None = None,
    assembly: PaperRuntimeAssembly | None = None,
    mode: str = EXTERNAL,
) -> PaperPreflightReport:
    """Compute a machine-clear READY/BLOCKED fact set for PAPER startup.

    Never performs login/connect/order/provider/credential action. Opening the
    layout journals is a safe local first-startup initialization; existing
    durable state is reopened, never wiped.
    """
    if not isinstance(config, PaperRuntimeConfig):
        raise TypeError("preflight requires PaperRuntimeConfig")
    if not isinstance(layout, PaperRuntimeLayout):
        raise TypeError("preflight requires PaperRuntimeLayout")
    if mode not in _MODES:
        raise ValueError("preflight mode must be EXTERNAL or OFFLINE_REHEARSAL")
    if activation_profile is None:
        activation_profile = config.activation_profile
    if authority is None:
        authority = config.authority
    if activation_profile is not None and not isinstance(activation_profile, PaperActivationProfile):
        raise TypeError("preflight activation profile must be PaperActivationProfile")
    if authority is not None and not isinstance(authority, PaperExecutionAuthority):
        raise TypeError("preflight authority must be PaperExecutionAuthority")
    if assembly is not None and not isinstance(assembly, PaperRuntimeAssembly):
        raise TypeError("preflight assembly must be PaperRuntimeAssembly")

    checks: list[PaperPreflightCheck] = []

    # 1. configuration completeness ------------------------------------------
    config_blockers: list[str] = []
    if not config.config_id:
        config_blockers.append("CONFIG_ID_MISSING")
    if not config.trader_identity:
        config_blockers.append("TRADER_IDENTITY_MISSING")
    if not config.concrete_contract_id:
        config_blockers.append("CONCRETE_CONTRACT_MISSING")
    if not config.exchange:
        config_blockers.append("EXCHANGE_MISSING")
    if not config.product:
        config_blockers.append("PRODUCT_MISSING")
    if not config.tqsdk_runtime_version:
        config_blockers.append("TQSDK_RUNTIME_VERSION_MISSING")
    checks.append(_check("CONFIGURATION_COMPLETE", config_blockers,
                         "all required stable identities are present"))

    # 2. activation-profile completeness ---------------------------------------
    profile_blockers: list[str] = []
    if activation_profile is None:
        profile_blockers.append("ACTIVATION_PROFILE_UNBOUND")
    elif activation_profile.status is not PaperActivationStatus.ACTIVE:
        profile_blockers.append("ACTIVATION_PROFILE_NOT_ACTIVE")
    else:
        missing = config.unbound_result_dependent_bindings()
        if missing:
            profile_blockers.append("RESULT_DEPENDENT_BINDINGS_MISSING:" + ",".join(sorted(missing)))
    checks.append(_check("ACTIVATION_PROFILE_COMPLETE", profile_blockers,
                         "bound ACTIVE activation profile with complete result-dependent bindings"))

    # 3. authority state --------------------------------------------------------
    authority_blockers: list[str] = []
    if authority is None:
        authority_blockers.append("PAPER_CONNECT_AUTHORITY_UNBOUND")
    elif authority.status is not PaperAuthorityStatus.ACTIVE:
        authority_blockers.append("PAPER_CONNECT_AUTHORITY_NOT_ACTIVE")
    elif not authority.allow_connect:
        authority_blockers.append("PAPER_CONNECT_AUTHORITY_DENIED")
    checks.append(_check("AUTHORITY_STATE", authority_blockers,
                         "ACTIVE authority with explicit connect permission"))

    # 4. contract identity consistency -------------------------------------------
    contract_blockers: list[str] = []
    if "." in config.concrete_contract_id:
        contract_exchange, instrument = config.concrete_contract_id.split(".", 1)
        if contract_exchange != config.exchange:
            contract_blockers.append("CONTRACT_EXCHANGE_MISMATCH")
        if not instrument.startswith(config.product):
            contract_blockers.append("CONTRACT_PRODUCT_MISMATCH")
    if activation_profile is not None and activation_profile.status is PaperActivationStatus.ACTIVE:
        try:
            activation_profile.require_active_for(config.concrete_contract_id)
        except PermissionError:
            contract_blockers.append("CONTRACT_NOT_IN_ACTIVATION_WHITELIST")
    checks.append(_check("CONTRACT_IDENTITY_CONSISTENT", contract_blockers,
                         "contract/exchange/product identity agrees with config and profile"))

    # 5. runtime/TqSdk version consistency ---------------------------------------
    version_blockers: list[str] = []
    if activation_profile is not None and activation_profile.tqsdk_runtime_version != config.tqsdk_runtime_version:
        version_blockers.append("TQSDK_RUNTIME_VERSION_PROFILE_MISMATCH")
    checks.append(_check("RUNTIME_VERSION_CONSISTENT", version_blockers,
                         "configured TqSdk runtime identity agrees with activation profile"))

    # 6. persistence state accessibility ------------------------------------------
    persistence_blockers: list[str] = []
    try:
        layout.ensure_initialized()
        layout.reopen()
    except Exception as error:  # noqa: BLE001 - preflight reports any fail-closed path
        persistence_blockers.append(type(error).__name__ + ":" + str(error))
    checks.append(_check("PERSISTENCE_ACCESSIBLE", persistence_blockers,
                         "state root initialized/reopened with identity agreement"))

    # 7. journal identity/schema readability --------------------------------------
    journal_blockers: list[str] = []
    order_journal: PaperOrderJournal | None = None
    wake_journal: PaperWakeJournal | None = None
    try:
        order_journal = PaperOrderJournal(layout.order_journal_path)
        wake_journal = PaperWakeJournal(layout.wake_journal_path)
    except Exception as error:  # noqa: BLE001
        journal_blockers.append("JOURNAL_OPEN_FAILED:" + type(error).__name__)
    finally:
        if order_journal is not None:
            try:
                order_journal.close()
            except Exception:  # noqa: BLE001
                pass
        if wake_journal is not None:
            try:
                wake_journal.close()
            except Exception:  # noqa: BLE001
                pass
    checks.append(_check("JOURNAL_SCHEMA_READABLE", journal_blockers,
                         "order/wake journal open with supported schema"))

    # 8. unresolved wake dispatch state --------------------------------------------
    wake_blockers: list[str] = []
    wake_journal = None
    try:
        wake_journal = PaperWakeJournal(layout.wake_journal_path)
        if wake_journal.unresolved_dispatches():
            wake_blockers.append("UNRESOLVED_TRADER_WAKE_DISPATCH")
    except Exception as error:  # noqa: BLE001
        wake_blockers.append("WAKE_JOURNAL_READ_FAILED:" + type(error).__name__)
    finally:
        if wake_journal is not None:
            try:
                wake_journal.close()
            except Exception:  # noqa: BLE001
                pass
    checks.append(_check("NO_UNRESOLVED_WAKE_DISPATCH", wake_blockers,
                         "no durable wake is stuck in DISPATCH_STARTED"))

    # 9. unresolved order / UNKNOWN state -------------------------------------------
    order_blockers: list[str] = []
    order_journal = None
    try:
        order_journal = PaperOrderJournal(layout.order_journal_path)
        if order_journal.unresolved_attempts():
            order_blockers.append("UNRESOLVED_PAPER_ORDER_SUBMISSION")
        for blocker in order_journal.recovery_blockers():
            order_blockers.append("PAPER_ORDER_RECOVERY:" + blocker)
    except Exception as error:  # noqa: BLE001
        order_blockers.append("ORDER_JOURNAL_READ_FAILED:" + type(error).__name__)
    finally:
        if order_journal is not None:
            try:
                order_journal.close()
            except Exception:  # noqa: BLE001
                pass
    checks.append(_check("NO_UNRESOLVED_ORDER_STATE", order_blockers,
                         "no unresolved/UNKNOWN order submission or recovery blocker"))

    # 10. broker/runtime assembly compatibility --------------------------------------
    assembly_blockers: list[str] = []
    if assembly is not None:
        coordinator = assembly.coordinator
        if coordinator.order_journal is not coordinator.broker.order_journal:
            assembly_blockers.append("ASSEMBLY_ORDER_JOURNAL_MISMATCH")
        if coordinator.broker_mirror.broker_id != coordinator.broker.broker_id:
            assembly_blockers.append("ASSEMBLY_BROKER_IDENTITY_MISMATCH")
        if getattr(coordinator.broker, "journal_managed_execution", False) is not True:
            assembly_blockers.append("ASSEMBLY_BROKER_NOT_JOURNAL_MANAGED")
        if coordinator.concrete_contract_id != config.concrete_contract_id:
            assembly_blockers.append("ASSEMBLY_CONTRACT_MISMATCH")
        if coordinator.trader_identity != config.trader_identity:
            assembly_blockers.append("ASSEMBLY_TRADER_IDENTITY_MISMATCH")
        if assembly.transport is None or assembly.supervisor is None:
            assembly_blockers.append("ASSEMBLY_INCOMPLETE")
    else:
        # Pre-construction preflight legitimately has no assembly yet; this is
        # informational, not a blocker. Real authority/profile checks still gate
        # external activation.
        assembly_blockers.append("NOT_EVALUATED_BEFORE_ASSEMBLY")
    checks.append(_check("ASSEMBLY_COMPATIBLE", assembly_blockers,
                         "assembled coordinator/transport/supervisor are identity-consistent"))

    # 11. required injected runtime components available -------------------------------
    component_blockers: list[str] = []
    if assembly is not None:
        for name, value in (
            ("coordinator", assembly.coordinator),
            ("supervisor", assembly.supervisor),
            ("transport", assembly.transport),
            ("context_builder", assembly.context_builder),
            ("broker", assembly.broker),
            ("source", getattr(assembly.transport, "source", None)),
        ):
            if value is None:
                component_blockers.append("REQUIRED_COMPONENT_MISSING:" + name)
        trader = getattr(assembly.coordinator, "trader", None)
        planner = getattr(assembly.coordinator, "risk_planner", None)
        if trader is None:
            component_blockers.append("REQUIRED_COMPONENT_MISSING:trader")
        if planner is None:
            component_blockers.append("REQUIRED_COMPONENT_MISSING:risk_planner")
    else:
        component_blockers.append("NOT_EVALUATED_BEFORE_ASSEMBLY")
    checks.append(_check("REQUIRED_COMPONENTS_AVAILABLE", component_blockers,
                         "all injected runtime components are bound in the assembly"))

    # 12. external PAPER role is not silently treated as adopted ------------------------
    role_blockers: list[str] = []
    if mode == EXTERNAL:
        # Code/credentials existing does NOT grant PAPER adoption. Only an explicit
        # ACTIVE connect authority may do that. This mirrors AUTHORITY_STATE but is
        # named separately so the guard is explicit.
        if authority is None:
            role_blockers.append("EXTERNAL_PAPER_ROLE_NOT_ADOPTED")
        elif authority.status is not PaperAuthorityStatus.ACTIVE or not authority.allow_connect:
            role_blockers.append("EXTERNAL_PAPER_ROLE_NOT_ADOPTED")
    checks.append(_check("EXTERNAL_PAPER_ROLE_NOT_SILENTLY_ADOPTED", role_blockers,
                         "PAPER connect role requires an explicit ACTIVE authority, never code/credential presence"))
    # -----------------------------------------------------------------------------------

    overall = "READY" if all(check.status == PASS for check in checks) else "BLOCKED"
    return PaperPreflightReport(mode=mode, overall=overall, checks=tuple(checks))


def _check(name: str, blockers: list[str], detail: str) -> PaperPreflightCheck:
    non_blocks = [value for value in blockers if value != "NOT_EVALUATED_BEFORE_ASSEMBLY"]
    if non_blocks:
        return PaperPreflightCheck(name=name, status=BLOCK, detail=";".join(sorted(set(non_blocks))))
    if blockers:
        return PaperPreflightCheck(
            name=name, status=PASS, detail="NOT_EVALUATED_BEFORE_ASSEMBLY (pre-construction)"
        )
    return PaperPreflightCheck(name=name, status=PASS, detail=detail)


__all__ = [
    "BLOCK",
    "EXTERNAL",
    "OFFLINE_REHEARSAL",
    "PAPER_PREFLIGHT_SCHEMA_VERSION",
    "PASS",
    "PaperPreflightCheck",
    "PaperPreflightReport",
    "run_paper_preflight",
]
