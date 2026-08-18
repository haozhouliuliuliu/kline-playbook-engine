"""Single-owner pre-outcome research firewall for Human Playbook First.

Authority (frozen — do not modify):
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`

This module is the single owner of the frozen pre-outcome access rules:

- SOURCE_ONLY session/policy with *technical* denial of protected-period market
  outcome retrieval (a prompt instruction such as "do not look" is not enough);
- immutable RESEARCH_WAVE manifests with a permanent tested denominator;
- common statistical profile identity/lock interface (identity/lock only — the
  real numerical standard is deliberately NOT designed here);
- the single fail-closed pre-outcome gate;
- historical final-holdout semantic state machine (never auto-unlocks);
- frozen 12/6/6 chronology classification.

The legacy `FinalUnseenFirewall` in `src/strategy_evidence.py` delegates here.
There is deliberately no second parallel firewall rule set in the project.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from hashlib import sha256
import json
from typing import Any

from src.strategy_evidence import (
    AccessResult,
    DatasetClass,
    EvidenceLedger,
    EvidenceRecord,
    ExperimentIdentity,
    StrategyIdentity,
)


def _canonical_hash(value: Any) -> str:
    """Same canonical JSON+sha256 scheme as src.strategy_evidence."""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class FrozenResearchProtocol:
    """Frozen facts from Research Protocol v1.0 and the 12/6/6 split. Do not modify."""

    RESEARCH_PROTOCOL_VERSION = "1.0"
    RESEARCH_PROTOCOL_STATUS = "FROZEN_BINDING"

    DEVELOPMENT_START = date(2024, 1, 1)
    DEVELOPMENT_END = date(2024, 12, 31)
    VALIDATION_START = date(2025, 1, 1)
    VALIDATION_END = date(2025, 6, 30)
    FINAL_HOLDOUT_START = date(2025, 7, 1)
    FINAL_HOLDOUT_END = date(2025, 12, 31)

    # Canonical corpus boundaries (docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md)
    CANONICAL_CORPUS_START = date(2024, 1, 1)
    CANONICAL_CORPUS_END = date(2025, 12, 31)


class Cohort(str, Enum):
    """Frozen cohort semantics. Shadow/Forward is the genuinely-prospective path."""

    DEVELOPMENT = "DEVELOPMENT"
    VALIDATION = "VALIDATION"
    PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT = "PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT"
    SHADOW_FORWARD = "SHADOW_FORWARD"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"


def classify_cohort(day: date) -> Cohort:
    """Classify a calendar day into the frozen 12/6/6 cohorts (fail closed)."""
    if FrozenResearchProtocol.DEVELOPMENT_START <= day <= FrozenResearchProtocol.DEVELOPMENT_END:
        return Cohort.DEVELOPMENT
    if FrozenResearchProtocol.VALIDATION_START <= day <= FrozenResearchProtocol.VALIDATION_END:
        return Cohort.VALIDATION
    if FrozenResearchProtocol.FINAL_HOLDOUT_START <= day <= FrozenResearchProtocol.FINAL_HOLDOUT_END:
        return Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT
    if day < FrozenResearchProtocol.CANONICAL_CORPUS_START:
        return Cohort.OUT_OF_SCOPE
    return Cohort.SHADOW_FORWARD


# ---------------------------------------------------------------------------
# SOURCE_ONLY
# ---------------------------------------------------------------------------


class ProtectedMarketAccessMode(str, Enum):
    TECHNICALLY_DENIED = "TECHNICALLY_DENIED"
    PROMPT_ONLY = "PROMPT_ONLY"  # "prompt says do not look" is NOT technical denial
    UNVERIFIED = "UNVERIFIED"
    ACCESSIBLE = "ACCESSIBLE"


@dataclass(frozen=True)
class SourceOnlySession:
    """Immutable SOURCE_ONLY session evidence record (Claim Schema v1.0 §4)."""

    session_id: str
    model_identity: str
    prompt_spec_version: str
    source_bundle_identity: str
    source_bundle_hash: str
    tool_retrieval_mode: str
    protected_market_access_mode: ProtectedMarketAccessMode
    researcher_model_exposure_note: str | None = None

    def __post_init__(self) -> None:
        required = (
            self.session_id,
            self.model_identity,
            self.prompt_spec_version,
            self.source_bundle_identity,
            self.source_bundle_hash,
            self.tool_retrieval_mode,
        )
        if not all(required):
            raise ValueError("SOURCE_ONLY session identity fields are required")
        if not isinstance(self.protected_market_access_mode, ProtectedMarketAccessMode):
            raise ValueError("protected market access mode must be explicit")

    @property
    def session_identity(self) -> str:
        return _canonical_hash(
            {
                "session_id": self.session_id,
                "model_identity": self.model_identity,
                "prompt_spec_version": self.prompt_spec_version,
                "source_bundle_identity": self.source_bundle_identity,
                "source_bundle_hash": self.source_bundle_hash,
                "tool_retrieval_mode": self.tool_retrieval_mode,
                "protected_market_access_mode": self.protected_market_access_mode.value,
                "researcher_model_exposure_note": self.researcher_model_exposure_note,
            }
        )


@dataclass(frozen=True)
class ProtectedOutcomeRequestResult:
    session_id: str | None
    outcome: str
    reason: str


class SourceOnlyPolicy:
    """Owns SOURCE_ONLY verification and technical denial.

    There is deliberately NO protected-period market outcome retrieval surface here.
    The only market-outcome-related entry point always DENIES, which is what makes
    the denial technical rather than a prompt instruction.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SourceOnlySession] = {}
        self._denials: list[ProtectedOutcomeRequestResult] = []

    @property
    def sessions(self) -> tuple[SourceOnlySession, ...]:
        return tuple(self._sessions.values())

    @property
    def denial_records(self) -> tuple[ProtectedOutcomeRequestResult, ...]:
        return tuple(self._denials)

    def record_session(self, session: SourceOnlySession) -> SourceOnlySession:
        if session.session_id in self._sessions:
            raise ValueError("duplicate SOURCE_ONLY session id")
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> SourceOnlySession | None:
        return self._sessions.get(session_id)

    def is_verified(self, session_id: str) -> bool:
        """A session is SOURCE_ONLY verified only if technical denial is in effect."""
        session = self._sessions.get(session_id)
        if session is None:
            return False
        if session.protected_market_access_mode is not ProtectedMarketAccessMode.TECHNICALLY_DENIED:
            return False
        required = (
            session.model_identity,
            session.prompt_spec_version,
            session.source_bundle_identity,
            session.source_bundle_hash,
            session.tool_retrieval_mode,
        )
        return bool(session.session_id) and all(required)

    def request_protected_market_outcome(self, session_id: str | None) -> ProtectedOutcomeRequestResult:
        """Technical denial surface: any attempt to obtain project market outcomes
        through SOURCE_ONLY is DENIED. No retrieval surface is ever exposed."""
        denial = ProtectedOutcomeRequestResult(session_id, "DENIED", "SOURCE_ONLY_TECHNICAL_DENIAL")
        self._denials.append(denial)
        return denial


# ---------------------------------------------------------------------------
# RESEARCH_WAVE
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ResearchWaveManifest:
    """Immutable pre-registered research wave (Protocol v1.0 §7)."""

    research_wave_id: str
    protocol_version: str
    statistical_profile_version: str
    tested_family_claim_identities: tuple[str, ...]
    primary_branch_identities: tuple[str, ...]
    declared_outcome_tested_alternatives: tuple[str, ...]
    instrument_timeframe_context_scope: str
    parameter_search_ranges: str
    denominator_counting_semantics: str
    created_at: str

    def __post_init__(self) -> None:
        required = (
            self.research_wave_id,
            self.protocol_version,
            self.statistical_profile_version,
            self.instrument_timeframe_context_scope,
            self.parameter_search_ranges,
            self.denominator_counting_semantics,
            self.created_at,
        )
        if not all(required):
            raise ValueError("research wave manifest has required empty fields")
        if not self.tested_family_claim_identities:
            raise ValueError("research wave must declare a tested family/claim set")

    @property
    def manifest_identity(self) -> str:
        return _canonical_hash(
            {
                "research_wave_id": self.research_wave_id,
                "protocol_version": self.protocol_version,
                "statistical_profile_version": self.statistical_profile_version,
                "tested_family_claim_identities": self.tested_family_claim_identities,
                "primary_branch_identities": self.primary_branch_identities,
                "declared_outcome_tested_alternatives": self.declared_outcome_tested_alternatives,
                "instrument_timeframe_context_scope": self.instrument_timeframe_context_scope,
                "parameter_search_ranges": self.parameter_search_ranges,
                "denominator_counting_semantics": self.denominator_counting_semantics,
                "created_at": self.created_at,
            }
        )


class ResearchWaveRegistry:
    """Immutable research waves with a permanent tested denominator."""

    def __init__(self) -> None:
        self._manifests: dict[str, ResearchWaveManifest] = {}
        self._locked: set[str] = set()
        self._outcome_started: set[str] = set()
        self._denominator: dict[str, dict[str, str]] = {}

    @property
    def wave_ids(self) -> tuple[str, ...]:
        return tuple(self._manifests)

    def register(self, manifest: ResearchWaveManifest) -> ResearchWaveManifest:
        if manifest.research_wave_id in self._manifests:
            raise ValueError("duplicate research wave id")
        self._manifests[manifest.research_wave_id] = manifest
        self._denominator[manifest.research_wave_id] = {}
        return manifest

    def get(self, wave_id: str) -> ResearchWaveManifest | None:
        return self._manifests.get(wave_id)

    def lock(self, wave_id: str) -> None:
        self._require_exists(wave_id)
        if wave_id in self._outcome_started:
            raise ValueError("cannot lock a wave after outcome testing has started")
        self._locked.add(wave_id)

    def is_locked(self, wave_id: str) -> bool:
        return wave_id in self._locked

    def declare_outcome_test_start(self, wave_id: str) -> None:
        self._require_exists(wave_id)
        if wave_id not in self._locked:
            raise ValueError("cannot start outcome testing on an unlocked wave")
        self._outcome_started.add(wave_id)

    def has_outcome_test_started(self, wave_id: str) -> bool:
        return wave_id in self._outcome_started

    def add_tested_hypothesis(self, wave_id: str, hypothesis_id: str) -> None:
        """Pre-registration before lock. Once locked, the test set is immutable."""
        self._require_exists(wave_id)
        if wave_id in self._locked:
            raise ValueError("cannot append a hypothesis to a locked wave; create a new wave")
        if wave_id in self._outcome_started:
            raise ValueError("cannot append a hypothesis after outcome testing has started")
        denominator = self._denominator[wave_id]
        if hypothesis_id in denominator:
            raise ValueError("duplicate tested hypothesis")
        denominator[hypothesis_id] = "PENDING"

    def record_outcome(self, wave_id: str, hypothesis_id: str, outcome: str) -> None:
        """FAIL and INSUFFICIENT_EVIDENCE remain permanently in the denominator."""
        self._require_exists(wave_id)
        denominator = self._denominator[wave_id]
        if hypothesis_id not in denominator:
            raise ValueError("hypothesis is not in the wave test set")
        denominator[hypothesis_id] = outcome

    def denominator(self, wave_id: str) -> tuple[str, ...]:
        """Permanent tested denominator; includes FAIL and INSUFFICIENT_EVIDENCE."""
        return tuple(sorted(self._denominator.get(wave_id, {})))

    def denominator_with_outcomes(self, wave_id: str) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted((hypothesis_id, outcome) for hypothesis_id, outcome in self._denominator.get(wave_id, {}).items())
        )

    def _require_exists(self, wave_id: str) -> None:
        if wave_id not in self._manifests:
            raise ValueError("unknown research wave id")


# ---------------------------------------------------------------------------
# COMMON STATISTICAL PROFILE (identity / lock interface only)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CommonStatisticalProfile:
    """Identity/lock interface for the common statistical profile.

    This is deliberately NOT the real numerical standard. It binds method/procedure
    identities so a profile version can be locked and gated. The real
    COMMON_STATISTICAL_PROFILE_V1 numeric standard must be designed and
    independently reviewed separately under Protocol v1.0 before candidate outcomes.
    Test fixtures must be clearly marked `test_only_marker="TEST_ONLY"`.
    """

    profile_id: str
    profile_version: str
    uncertainty_precision_method: str
    evidence_sufficiency_procedure: str
    dependence_handling: str
    multiplicity_decision_rule: str
    common_acceptance_procedure: str
    test_only_marker: str | None = None

    def __post_init__(self) -> None:
        required = (
            self.profile_id,
            self.profile_version,
            self.uncertainty_precision_method,
            self.evidence_sufficiency_procedure,
            self.dependence_handling,
            self.multiplicity_decision_rule,
            self.common_acceptance_procedure,
        )
        if not all(required):
            raise ValueError("statistical profile identity fields are required")

    @property
    def is_test_only(self) -> bool:
        return self.test_only_marker == "TEST_ONLY"

    @property
    def profile_identity(self) -> str:
        return _canonical_hash(
            {
                "profile_id": self.profile_id,
                "profile_version": self.profile_version,
                "uncertainty_precision_method": self.uncertainty_precision_method,
                "evidence_sufficiency_procedure": self.evidence_sufficiency_procedure,
                "dependence_handling": self.dependence_handling,
                "multiplicity_decision_rule": self.multiplicity_decision_rule,
                "common_acceptance_procedure": self.common_acceptance_procedure,
                "test_only_marker": self.test_only_marker,
            }
        )


class StatisticalProfileRegistry:
    """Append-only profile registry with an explicit lock."""

    def __init__(self) -> None:
        self._profiles: dict[str, CommonStatisticalProfile] = {}
        self._locked: set[str] = set()

    @property
    def profile_ids(self) -> tuple[str, ...]:
        return tuple(self._profiles)

    def register(self, profile: CommonStatisticalProfile) -> CommonStatisticalProfile:
        if profile.profile_id in self._profiles:
            raise ValueError("duplicate statistical profile id")
        self._profiles[profile.profile_id] = profile
        return profile

    def get(self, profile_id: str) -> CommonStatisticalProfile | None:
        return self._profiles.get(profile_id)

    def lock(self, profile_id: str) -> None:
        if profile_id not in self._profiles:
            raise ValueError("unknown statistical profile id")
        self._locked.add(profile_id)

    def is_locked(self, profile_id: str) -> bool:
        return profile_id in self._locked


# ---------------------------------------------------------------------------
# HISTORICAL FINAL HOLDOUT STATE MACHINE
# ---------------------------------------------------------------------------


class FinalHoldoutState(str, Enum):
    FINAL_HISTORICAL_HOLDOUT_LOCKED = "FINAL_HISTORICAL_HOLDOUT_LOCKED"
    FINAL_HISTORICAL_HOLDOUT_EXPOSED = "FINAL_HISTORICAL_HOLDOUT_EXPOSED"
    FINAL_ACCEPTED = "FINAL_ACCEPTED"
    FINAL_REJECTED = "FINAL_REJECTED"
    FINAL_VOID_IMPLEMENTATION_DEFECT = "FINAL_VOID_IMPLEMENTATION_DEFECT"


_TERMINAL_FINAL_STATES = frozenset(
    {
        FinalHoldoutState.FINAL_ACCEPTED,
        FinalHoldoutState.FINAL_REJECTED,
        FinalHoldoutState.FINAL_VOID_IMPLEMENTATION_DEFECT,
    }
)


class HistoricalFinalHoldoutStateMachine:
    """Semantic state machine for the historical final holdout.

    FINAL_HISTORICAL_HOLDOUT_LOCKED
      -> FINAL_HISTORICAL_HOLDOUT_EXPOSED
      -> FINAL_ACCEPTED | FINAL_REJECTED | FINAL_VOID_IMPLEMENTATION_DEFECT

    This package never auto-unlocks the final holdout: exposure requires a separate,
    explicitly registered unlock authority, and no such authority is registered by
    default. The pre-outcome gate also always denies final-cohort outcome access.
    `FINAL_VOID_IMPLEMENTATION_DEFECT` never restores holdout status.
    """

    def __init__(self) -> None:
        self._state = FinalHoldoutState.FINAL_HISTORICAL_HOLDOUT_LOCKED
        self._unlock_authority: str | None = None

    @property
    def state(self) -> FinalHoldoutState:
        return self._state

    @property
    def is_locked(self) -> bool:
        return self._state is FinalHoldoutState.FINAL_HISTORICAL_HOLDOUT_LOCKED

    @property
    def is_exposed(self) -> bool:
        return self._state is FinalHoldoutState.FINAL_HISTORICAL_HOLDOUT_EXPOSED

    def register_unlock_authority(self, authority_id: str) -> None:
        if not authority_id:
            raise ValueError("unlock authority id is required")
        self._unlock_authority = authority_id

    def expose(self, authority_id: str) -> None:
        if self._unlock_authority is None:
            raise ValueError("no final-holdout unlock authority is registered; cannot expose")
        if authority_id != self._unlock_authority:
            raise ValueError("final-holdout unlock authority mismatch")
        if self._state is not FinalHoldoutState.FINAL_HISTORICAL_HOLDOUT_LOCKED:
            raise ValueError("final holdout is not in LOCKED state")
        self._state = FinalHoldoutState.FINAL_HISTORICAL_HOLDOUT_EXPOSED

    def conclude(self, outcome: FinalHoldoutState) -> None:
        if outcome not in _TERMINAL_FINAL_STATES:
            raise ValueError("only terminal final conclusions are allowed")
        if self._state is not FinalHoldoutState.FINAL_HISTORICAL_HOLDOUT_EXPOSED:
            raise ValueError("final holdout must be EXPOSED before a terminal conclusion")
        self._state = outcome


# ---------------------------------------------------------------------------
# PRE-OUTCOME GATE
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class GateControl:
    name: str
    satisfied: bool
    detail: str


@dataclass(frozen=True)
class PreOutcomeGateDecision:
    allowed: bool
    cohort: Cohort
    synthetic_only: bool
    reason: str
    controls: tuple[GateControl, ...]


class PreOutcomeGate:
    """Single fail-closed pre-outcome gate for candidate outcome-bearing access.

    Before the first candidate outcome-bearing performance test for a wave, all
    must be true:

        SOURCE_ONLY_CONTROLS            = ACTIVE_AND_VERIFIED
        COMMON_STATISTICAL_PROFILE      = LOCKED
        MULTIPLICITY_COUNTING_UNIT      = LOCKED
        RESEARCH_WAVE                   = LOCKED
        PRIMARY_SCOPE_SEARCH_IDENTITIES = LOCKED

    Any missing/unknown prerequisite denies access (fail closed).
    """

    REQUIRED_CONTROLS = (
        "SOURCE_ONLY_CONTROLS",
        "COMMON_STATISTICAL_PROFILE",
        "MULTIPLICITY_COUNTING_UNIT",
        "RESEARCH_WAVE",
        "PRIMARY_SCOPE_SEARCH_IDENTITIES",
    )

    def evaluate(
        self,
        *,
        cohort: Cohort,
        source_only_verified: bool,
        statistical_profile_locked: bool,
        statistical_profile_test_only: bool,
        multiplicity_counting_unit_locked: bool,
        research_wave_locked: bool,
        primary_scope_search_identities_locked: bool,
        synthetic_fixture: bool,
    ) -> PreOutcomeGateDecision:
        controls = (
            GateControl(
                "SOURCE_ONLY_CONTROLS",
                source_only_verified,
                "ACTIVE_AND_VERIFIED" if source_only_verified else "MISSING_OR_UNVERIFIED",
            ),
            GateControl(
                "COMMON_STATISTICAL_PROFILE",
                statistical_profile_locked,
                "LOCKED" if statistical_profile_locked else "MISSING_DRAFT_OR_UNLOCKED",
            ),
            GateControl(
                "MULTIPLICITY_COUNTING_UNIT",
                multiplicity_counting_unit_locked,
                "LOCKED" if multiplicity_counting_unit_locked else "MISSING_OR_UNLOCKED",
            ),
            GateControl(
                "RESEARCH_WAVE",
                research_wave_locked,
                "LOCKED" if research_wave_locked else "MISSING_OR_UNLOCKED",
            ),
            GateControl(
                "PRIMARY_SCOPE_SEARCH_IDENTITIES",
                primary_scope_search_identities_locked,
                "LOCKED" if primary_scope_search_identities_locked else "MISSING_OR_UNLOCKED",
            ),
        )
        missing = tuple(control.name for control in controls if not control.satisfied)

        if cohort is Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT:
            return PreOutcomeGateDecision(False, cohort, False, "FINAL_HISTORICAL_HOLDOUT_ALWAYS_LOCKED", controls)
        if cohort is Cohort.SHADOW_FORWARD:
            return PreOutcomeGateDecision(False, cohort, False, "SHADOW_FORWARD_NOT_AUTHORIZED", controls)
        if cohort is Cohort.OUT_OF_SCOPE:
            return PreOutcomeGateDecision(False, cohort, False, "OUT_OF_SCOPE_NOT_A_RESEARCH_COHORT", controls)
        if cohort is Cohort.VALIDATION:
            return PreOutcomeGateDecision(False, cohort, False, "VALIDATION_DEFAULT_DENY_NO_VALIDATION_AUTHORITY", controls)

        # DEVELOPMENT is the only cohort that the gate can allow, and only when the
        # full control stack is satisfied. Until the real COMMON_STATISTICAL_PROFILE
        # is locked, only TEST_ONLY profiles exist, so only synthetic fixtures pass.
        if missing:
            return PreOutcomeGateDecision(False, cohort, False, "MISSING_CONTROLS:" + ",".join(missing), controls)
        if statistical_profile_test_only and not synthetic_fixture:
            return PreOutcomeGateDecision(False, cohort, True, "TEST_ONLY_PROFILE_REQUIRES_SYNTHETIC_FIXTURE", controls)
        return PreOutcomeGateDecision(
            True,
            cohort,
            statistical_profile_test_only or synthetic_fixture,
            "SYNTHETIC_DEVELOPMENT_OUTCOME_ONLY",
            controls,
        )


# ---------------------------------------------------------------------------
# RESEARCH FIREWALL (single owner)
# ---------------------------------------------------------------------------


class ResearchFirewall:
    """Single owner of pre-outcome research access rules.

    Composes SOURCE_ONLY policy, research waves, statistical profile registry,
    the pre-outcome gate, and the historical final-holdout state machine.
    """

    def __init__(self, ledger: EvidenceLedger) -> None:
        self._ledger = ledger
        self._source_only = SourceOnlyPolicy()
        self._waves = ResearchWaveRegistry()
        self._profiles = StatisticalProfileRegistry()
        self._gate = PreOutcomeGate()
        self._final_state = HistoricalFinalHoldoutStateMachine()

    @property
    def source_only(self) -> SourceOnlyPolicy:
        return self._source_only

    @property
    def waves(self) -> ResearchWaveRegistry:
        return self._waves

    @property
    def profiles(self) -> StatisticalProfileRegistry:
        return self._profiles

    @property
    def gate(self) -> PreOutcomeGate:
        return self._gate

    @property
    def final_state(self) -> HistoricalFinalHoldoutStateMachine:
        return self._final_state

    # -- legacy compatibility path (FinalUnseenFirewall delegates here) ---------

    @staticmethod
    def _always_denied_dataset_classes() -> frozenset[DatasetClass]:
        return frozenset(
            {
                DatasetClass.FINAL_UNSEEN,
                DatasetClass.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT,
                DatasetClass.SHADOW_FORWARD,
            }
        )

    def legacy_request_access(self, experiment: ExperimentIdentity, dataset_class: DatasetClass) -> AccessResult:
        """Coarse dataset-cohort access used by the legacy FinalUnseenFirewall.

        The historical final cohort (both the legacy FINAL_UNSEEN name and the
        canonical PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT name) and Shadow/Forward
        are always denied. Coarse DEVELOPMENT/VALIDATION grants here are NOT
        candidate-outcome authorization; candidate outcome-bearing access requires
        the pre-outcome gate (`request_candidate_outcome_access`).
        """
        if dataset_class in self._always_denied_dataset_classes():
            record = EvidenceRecord("DATASET_ACCESS_DENIED", experiment, dataset_class, "DENIED")
            self._ledger.append(record)
            return AccessResult(False, record)
        record = EvidenceRecord("DATASET_ACCESS_GRANTED", experiment, dataset_class, "GRANTED")
        self._ledger.append(record)
        return AccessResult(True, record)

    def has_exposure(self, strategy: StrategyIdentity, dataset_class: DatasetClass) -> bool:
        return dataset_class in self._ledger.exposures_for(strategy.research_lineage_id)

    # -- authoritative candidate-outcome path -----------------------------------

    @staticmethod
    def _dataset_class_for_cohort(cohort: Cohort) -> DatasetClass:
        mapping = {
            Cohort.DEVELOPMENT: DatasetClass.DEVELOPMENT,
            Cohort.VALIDATION: DatasetClass.VALIDATION,
            Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: DatasetClass.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT,
            Cohort.SHADOW_FORWARD: DatasetClass.SHADOW_FORWARD,
        }
        try:
            return mapping[cohort]
        except KeyError:
            raise ValueError("cohort has no dataset-class representation") from None

    def evaluate_gate(
        self,
        *,
        cohort: Cohort,
        source_only_session_id: str,
        wave_id: str,
        profile_id: str,
        multiplicity_counting_unit_locked: bool,
        primary_scope_search_identities_locked: bool,
        synthetic_fixture: bool,
    ) -> PreOutcomeGateDecision:
        """Resolve control state from the registries and evaluate the gate (fail closed)."""
        source_only_verified = self._source_only.is_verified(source_only_session_id)
        profile = self._profiles.get(profile_id)
        statistical_profile_locked = profile is not None and self._profiles.is_locked(profile_id)
        statistical_profile_test_only = profile is not None and profile.is_test_only
        wave = self._waves.get(wave_id)
        research_wave_locked = wave is not None and self._waves.is_locked(wave_id)
        return self._gate.evaluate(
            cohort=cohort,
            source_only_verified=source_only_verified,
            statistical_profile_locked=statistical_profile_locked,
            statistical_profile_test_only=statistical_profile_test_only,
            multiplicity_counting_unit_locked=multiplicity_counting_unit_locked,
            research_wave_locked=research_wave_locked,
            primary_scope_search_identities_locked=primary_scope_search_identities_locked,
            synthetic_fixture=synthetic_fixture,
        )

    def request_candidate_outcome_access(
        self,
        *,
        cohort: Cohort,
        experiment: ExperimentIdentity,
        source_only_session_id: str,
        wave_id: str,
        profile_id: str,
        multiplicity_counting_unit_locked: bool,
        primary_scope_search_identities_locked: bool,
        synthetic_fixture: bool,
    ) -> AccessResult:
        """Authoritative candidate outcome-bearing access. Fail closed by default."""
        decision = self.evaluate_gate(
            cohort=cohort,
            source_only_session_id=source_only_session_id,
            wave_id=wave_id,
            profile_id=profile_id,
            multiplicity_counting_unit_locked=multiplicity_counting_unit_locked,
            primary_scope_search_identities_locked=primary_scope_search_identities_locked,
            synthetic_fixture=synthetic_fixture,
        )
        dataset_class = self._dataset_class_for_cohort(cohort)
        if decision.allowed:
            record = EvidenceRecord(
                "PRE_OUTCOME_GATE_GRANTED",
                experiment,
                dataset_class,
                "GRANTED",
                evidence_reference=decision.reason,
            )
        else:
            record = EvidenceRecord(
                "PRE_OUTCOME_GATE_DENIED",
                experiment,
                dataset_class,
                "DENIED",
                evidence_reference=decision.reason,
            )
        self._ledger.append(record)
        return AccessResult(decision.allowed, record)
