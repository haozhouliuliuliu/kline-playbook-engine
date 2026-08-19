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
- frozen 12/6/6 chronology classification;
- canonical identity-bound outcome-test registration (candidate outcome access is
  keyed by one registered hypothesis identity; all other facts are resolved and
  verified from project-owned registries, never asserted by the caller).

The legacy `FinalUnseenFirewall` in `src/strategy_evidence.py` delegates here.
There is deliberately no second parallel firewall rule set in the project.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
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


# Single governed TEST_ONLY synthetic data-version identity. The authoritative
# candidate-outcome API derives synthetic status ONLY from exact equality with
# this constant (never from a caller-supplied boolean, prefix/suffix match, or
# any other truthy marker). A future version change requires a formal protocol
# version change.
TEST_ONLY_SYNTHETIC_DATA_VERSION = "TEST_ONLY_SYNTHETIC_DATA_V1"


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
    """Immutable SOURCE_ONLY session evidence record (Claim Schema v1.0 §4).

    `verification_evidence` is a project-issued token produced only by
    `SourceOnlyPolicy.open_verified_session`. A session that merely declares
    `TECHNICALLY_DENIED` without project-issued evidence is never verified.
    """

    session_id: str
    model_identity: str
    prompt_spec_version: str
    source_bundle_identity: str
    source_bundle_hash: str
    tool_retrieval_mode: str
    protected_market_access_mode: ProtectedMarketAccessMode
    researcher_model_exposure_note: str | None = None
    verification_evidence: str | None = None

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

    Verification is project-issued: only `open_verified_session` produces the
    `verification_evidence` token that `is_verified` accepts. Manually constructed
    sessions cannot self-verify.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SourceOnlySession] = {}
        self._denials: list[ProtectedOutcomeRequestResult] = []
        self._issuer_nonce = _canonical_hash(("SOURCE_ONLY_PROJECT_ISSUER_V1",))

    @property
    def sessions(self) -> tuple[SourceOnlySession, ...]:
        return tuple(self._sessions.values())

    @property
    def denial_records(self) -> tuple[ProtectedOutcomeRequestResult, ...]:
        return tuple(self._denials)

    def _expected_evidence(self, session: SourceOnlySession) -> str:
        return _canonical_hash((self._issuer_nonce, session.session_identity))

    def open_verified_session(
        self,
        *,
        session_id: str,
        model_identity: str,
        prompt_spec_version: str,
        source_bundle_identity: str,
        source_bundle_hash: str,
        tool_retrieval_mode: str,
        researcher_model_exposure_note: str | None = None,
    ) -> SourceOnlySession:
        """Project-owned verified-session creation path.

        Builds a session whose `protected_market_access_mode` is
        `TECHNICALLY_DENIED` and stamps project-issued verification evidence.
        """
        if session_id in self._sessions:
            raise ValueError("duplicate SOURCE_ONLY session id")
        base = SourceOnlySession(
            session_id=session_id,
            model_identity=model_identity,
            prompt_spec_version=prompt_spec_version,
            source_bundle_identity=source_bundle_identity,
            source_bundle_hash=source_bundle_hash,
            tool_retrieval_mode=tool_retrieval_mode,
            protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
            researcher_model_exposure_note=researcher_model_exposure_note,
        )
        session = replace(base, verification_evidence=self._expected_evidence(base))
        self._sessions[session_id] = session
        return session

    def record_session(self, session: SourceOnlySession) -> SourceOnlySession:
        """Compatibility/test recording path.

        Records a session as supplied. It is NOT verified unless it carries valid
        project-issued verification evidence.
        """
        if session.session_id in self._sessions:
            raise ValueError("duplicate SOURCE_ONLY session id")
        self._sessions[session.session_id] = session
        return session

    def get(self, session_id: str) -> SourceOnlySession | None:
        return self._sessions.get(session_id)

    def is_verified(self, session_id: str) -> bool:
        """A session is verified only with project-issued technical-denial evidence."""
        session = self._sessions.get(session_id)
        if session is None:
            return False
        if session.protected_market_access_mode is not ProtectedMarketAccessMode.TECHNICALLY_DENIED:
            return False
        if not session.verification_evidence:
            return False
        return session.verification_evidence == self._expected_evidence(session)

    def request_protected_market_outcome(self, session_id: str | None) -> ProtectedOutcomeRequestResult:
        """Technical denial surface: any attempt to obtain project market outcomes
        through SOURCE_ONLY is DENIED. No retrieval surface is ever exposed."""
        denial = ProtectedOutcomeRequestResult(session_id, "DENIED", "SOURCE_ONLY_TECHNICAL_DENIAL")
        self._denials.append(denial)
        return denial


# ---------------------------------------------------------------------------
# SOURCE_ONLY claim-extraction runner/context (bounded)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ApprovedSourceBundle:
    """Provenance pointer to an approved source; no redistributed content."""

    source_bundle_id: str
    source_bundle_hash: str
    source_anchor_reference: str
    content_note: str | None = None

    def __post_init__(self) -> None:
        if not self.source_bundle_id or not self.source_bundle_hash or not self.source_anchor_reference:
            raise ValueError("approved source bundle requires identity, hash, and anchor reference")


@dataclass(frozen=True)
class ClaimRecordDraft:
    """Minimal provenance/claim-record output (Claim Schema v1.0 structural subset)."""

    claim_id: str
    source_id: str
    source_anchor: str
    claim_status: str
    source_excerpt_short_or_paraphrase: str
    source_only_session_id: str
    created_at: str

    def __post_init__(self) -> None:
        required = (
            self.claim_id,
            self.source_id,
            self.source_anchor,
            self.claim_status,
            self.source_excerpt_short_or_paraphrase,
            self.source_only_session_id,
            self.created_at,
        )
        if not all(required):
            raise ValueError("claim record draft has required empty fields")


class ClaimRecordOutput:
    """Append-only provenance/claim-record surface. Contains no market data."""

    def __init__(self) -> None:
        self._records: list[ClaimRecordDraft] = []

    @property
    def records(self) -> tuple[ClaimRecordDraft, ...]:
        return tuple(self._records)

    def record(self, draft: ClaimRecordDraft) -> ClaimRecordDraft:
        if any(record.claim_id == draft.claim_id for record in self._records):
            raise ValueError("duplicate claim id")
        self._records.append(draft)
        return draft


class SourceOnlyClaimExtractionContext:
    """Minimal bounded SOURCE_ONLY claim-extraction environment.

    Structurally holds ONLY:
    - an approved source bundle (provenance, not redistributed content);
    - SOURCE_ONLY services/session;
    - a provenance/claim-record output surface.

    It deliberately does NOT hold any canonical market-data repository, historical
    outcome API, validation/final data surface, or generic market-outcome retrieval
    service. The only market-outcome-related entry point always DENIES and audits.
    """

    def __init__(
        self,
        *,
        source_bundle: ApprovedSourceBundle,
        source_only: SourceOnlyPolicy,
        session_id: str,
        output_surface: ClaimRecordOutput,
    ) -> None:
        self._source_bundle = source_bundle
        self._source_only = source_only
        self._session_id = session_id
        self._output_surface = output_surface
        self._denials: list[ProtectedOutcomeRequestResult] = []

    @property
    def source_bundle(self) -> ApprovedSourceBundle:
        return self._source_bundle

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def denial_records(self) -> tuple[ProtectedOutcomeRequestResult, ...]:
        return tuple(self._denials)

    @property
    def verified(self) -> bool:
        session = self._source_only.get(self._session_id)
        if session is None or not self._source_only.is_verified(self._session_id):
            return False
        return (
            session.source_bundle_identity == self._source_bundle.source_bundle_id
            and session.source_bundle_hash == self._source_bundle.source_bundle_hash
        )

    def record_claim(self, draft: ClaimRecordDraft) -> ClaimRecordDraft:
        """Append a claim to the provenance output surface (no market data)."""
        if not self.verified:
            raise ValueError("SOURCE_ONLY runner requires a verified session bound to the approved source bundle")
        if draft.source_only_session_id != self._session_id:
            raise ValueError("claim record is bound to a different SOURCE_ONLY session")
        if draft.source_id != self._source_bundle.source_bundle_id:
            raise ValueError("claim record is bound to a different source bundle")
        return self._output_surface.record(draft)

    def request_protected_market_outcome(self, request_reference: str | None) -> ProtectedOutcomeRequestResult:
        """Technical denial: the runner has no market-outcome surface; always DENY + audit."""
        denial = self._source_only.request_protected_market_outcome(self._session_id)
        self._denials.append(denial)
        return denial


# ---------------------------------------------------------------------------
# RESEARCH_WAVE
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class WaveHypothesisBinding:
    """Immutable, machine-comparable per-hypothesis identity binding frozen by a
    wave.

    This is the deterministic security identity authority for PRIMARY / scope /
    parameter-search for each tested hypothesis. Human-readable manifest
    descriptions are never used for identity comparison.
    """

    hypothesis_test_id: str
    primary_branch_identity: str
    scope_identity: str
    parameter_search_identity: str

    def __post_init__(self) -> None:
        required = (
            self.hypothesis_test_id,
            self.primary_branch_identity,
            self.scope_identity,
            self.parameter_search_identity,
        )
        if not all(required):
            raise ValueError("wave hypothesis binding has required empty fields")

    def as_dict(self) -> dict[str, str]:
        return {
            "hypothesis_test_id": self.hypothesis_test_id,
            "primary_branch_identity": self.primary_branch_identity,
            "scope_identity": self.scope_identity,
            "parameter_search_identity": self.parameter_search_identity,
        }


@dataclass(frozen=True)
class ResearchWaveManifest:
    """Immutable pre-registered research wave (Protocol v1.0 §7).

    The canonical tested denominator is `tested_hypothesis_test_ids`, bound
    directly in this immutable manifest. The registry derives the permanent
    denominator from the manifest, so the manifest and the denominator can never
    diverge (no split-brain).

    `hypothesis_bindings` is the deterministic PRIMARY/scope/parameter-search
    identity authority per tested hypothesis; the human-readable scope/search
    descriptions are informational only.
    """

    research_wave_id: str
    protocol_version: str
    statistical_profile_id: str
    statistical_profile_identity: str
    multiplicity_counting_unit_identity: str
    tested_hypothesis_test_ids: tuple[str, ...]
    hypothesis_bindings: tuple[WaveHypothesisBinding, ...]
    declared_outcome_tested_alternatives: tuple[str, ...]
    instrument_timeframe_context_scope: str
    parameter_search_ranges: str
    denominator_counting_semantics: str
    created_at: str

    def __post_init__(self) -> None:
        required = (
            self.research_wave_id,
            self.protocol_version,
            self.statistical_profile_id,
            self.statistical_profile_identity,
            self.multiplicity_counting_unit_identity,
            self.instrument_timeframe_context_scope,
            self.parameter_search_ranges,
            self.denominator_counting_semantics,
            self.created_at,
        )
        if not all(required):
            raise ValueError("research wave manifest has required empty fields")
        if not self.tested_hypothesis_test_ids:
            raise ValueError("research wave must declare a non-empty tested hypothesis set")
        if len(self.tested_hypothesis_test_ids) != len(set(self.tested_hypothesis_test_ids)):
            raise ValueError("tested hypothesis identities must be unique")
        if not self.hypothesis_bindings:
            raise ValueError("research wave must declare hypothesis bindings")
        binding_ids = tuple(binding.hypothesis_test_id for binding in self.hypothesis_bindings)
        if len(binding_ids) != len(set(binding_ids)):
            raise ValueError("wave hypothesis binding ids must be unique")
        if set(binding_ids) != set(self.tested_hypothesis_test_ids):
            raise ValueError("wave hypothesis bindings must exactly match the tested hypothesis set")

    def binding_for(self, hypothesis_test_id: str) -> WaveHypothesisBinding | None:
        for binding in self.hypothesis_bindings:
            if binding.hypothesis_test_id == hypothesis_test_id:
                return binding
        return None

    @property
    def manifest_identity(self) -> str:
        return _canonical_hash(
            {
                "research_wave_id": self.research_wave_id,
                "protocol_version": self.protocol_version,
                "statistical_profile_id": self.statistical_profile_id,
                "statistical_profile_identity": self.statistical_profile_identity,
                "multiplicity_counting_unit_identity": self.multiplicity_counting_unit_identity,
                "tested_hypothesis_test_ids": self.tested_hypothesis_test_ids,
                "hypothesis_bindings": tuple(
                    sorted(
                        (binding.as_dict() for binding in self.hypothesis_bindings),
                        key=lambda item: item["hypothesis_test_id"],
                    )
                ),
                "declared_outcome_tested_alternatives": self.declared_outcome_tested_alternatives,
                "instrument_timeframe_context_scope": self.instrument_timeframe_context_scope,
                "parameter_search_ranges": self.parameter_search_ranges,
                "denominator_counting_semantics": self.denominator_counting_semantics,
                "created_at": self.created_at,
            }
        )


class ResearchWaveRegistry:
    """Immutable research waves; the denominator is derived from the locked manifest."""

    def __init__(self) -> None:
        self._manifests: dict[str, ResearchWaveManifest] = {}
        self._locked: set[str] = set()
        self._outcome_started: set[str] = set()
        self._outcomes: dict[str, dict[str, str]] = {}

    @property
    def wave_ids(self) -> tuple[str, ...]:
        return tuple(self._manifests)

    def register(self, manifest: ResearchWaveManifest) -> ResearchWaveManifest:
        if manifest.research_wave_id in self._manifests:
            raise ValueError("duplicate research wave id")
        self._manifests[manifest.research_wave_id] = manifest
        self._outcomes[manifest.research_wave_id] = {}
        return manifest

    def get(self, wave_id: str) -> ResearchWaveManifest | None:
        return self._manifests.get(wave_id)

    def lock(self, wave_id: str, outcome_registry: "OutcomeTestRegistry") -> None:
        """Fail-closed lock.

        Verifies the tested denominator is non-empty and every tested hypothesis
        registration exists, points to this wave, and binds the same profile and
        counting-unit identity as the manifest. Inconsistency -> lock fails.
        """
        self._require_exists(wave_id)
        if wave_id in self._locked:
            raise ValueError("wave is already locked")
        if wave_id in self._outcome_started:
            raise ValueError("cannot lock a wave after outcome testing has started")
        manifest = self._manifests[wave_id]
        if not manifest.tested_hypothesis_test_ids:
            raise ValueError("cannot lock a wave with an empty tested denominator")
        for hypothesis_test_id in manifest.tested_hypothesis_test_ids:
            registration = outcome_registry.get(hypothesis_test_id)
            if registration is None:
                raise ValueError(f"tested hypothesis is not registered: {hypothesis_test_id}")
            if registration.research_wave_id != wave_id:
                raise ValueError(f"tested hypothesis registration points to another wave: {hypothesis_test_id}")
            if registration.statistical_profile_id != manifest.statistical_profile_id:
                raise ValueError("tested hypothesis registration profile id mismatches the wave manifest")
            if registration.statistical_profile_identity != manifest.statistical_profile_identity:
                raise ValueError("tested hypothesis registration profile identity mismatches the wave manifest")
            if registration.multiplicity_counting_unit_identity != manifest.multiplicity_counting_unit_identity:
                raise ValueError("tested hypothesis registration counting-unit identity mismatches the wave manifest")
            binding = manifest.binding_for(hypothesis_test_id)
            if binding is None:
                raise ValueError(f"tested hypothesis has no wave PRIMARY/scope/search binding: {hypothesis_test_id}")
            if registration.primary_branch_identity != binding.primary_branch_identity:
                raise ValueError("tested hypothesis registration PRIMARY identity mismatches the wave binding")
            if registration.scope_identity != binding.scope_identity:
                raise ValueError("tested hypothesis registration scope identity mismatches the wave binding")
            if registration.parameter_search_identity != binding.parameter_search_identity:
                raise ValueError("tested hypothesis registration parameter/search identity mismatches the wave binding")
        self._locked.add(wave_id)

    def is_locked(self, wave_id: str) -> bool:
        return wave_id in self._locked

    def declare_outcome_test_start(self, wave_id: str) -> bool:
        """Durable first-look fact. Returns True if newly started, else False."""
        self._require_exists(wave_id)
        if wave_id not in self._locked:
            raise ValueError("cannot start outcome testing on an unlocked wave")
        if wave_id in self._outcome_started:
            return False
        self._outcome_started.add(wave_id)
        return True

    def has_outcome_test_started(self, wave_id: str) -> bool:
        return wave_id in self._outcome_started

    def denominator(self, wave_id: str) -> tuple[str, ...]:
        """Permanent tested denominator derived from the immutable manifest."""
        manifest = self._manifests.get(wave_id)
        if manifest is None:
            return ()
        return tuple(sorted(manifest.tested_hypothesis_test_ids))

    def record_terminal_outcome(self, wave_id: str, hypothesis_test_id: str, outcome: str) -> None:
        """Append-only terminal outcome recording.

        The first terminal outcome for a hypothesis is immutable: re-recording the
        same fact is idempotent, a different outcome is rejected, and the tested
        denominator always keeps FAIL / INSUFFICIENT_EVIDENCE.
        """
        self._require_exists(wave_id)
        if wave_id not in self._locked:
            raise ValueError("cannot record an outcome for an unlocked wave")
        if hypothesis_test_id not in self.denominator(wave_id):
            raise ValueError("hypothesis is not in the wave tested set")
        existing = self._outcomes[wave_id].get(hypothesis_test_id)
        if existing is not None:
            if existing == outcome:
                return  # explicit idempotent re-record of the same fact
            raise ValueError(
                f"cannot overwrite a recorded outcome {existing!r} with {outcome!r}; "
                "use an explicit evidence/revision event instead"
            )
        self._outcomes[wave_id][hypothesis_test_id] = outcome

    def outcome_records(self, wave_id: str) -> tuple[tuple[str, str], ...]:
        return tuple(
            sorted(
                (hypothesis_test_id, outcome)
                for hypothesis_test_id, outcome in self._outcomes.get(wave_id, {}).items()
            )
        )

    def _require_exists(self, wave_id: str) -> None:
        if wave_id not in self._manifests:
            raise ValueError("unknown research wave id")


# ---------------------------------------------------------------------------
# OUTCOME TEST REGISTRATION (canonical identity-bound hypothesis registration)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class OutcomeTestRegistration:
    """Immutable, canonical identity binding for one outcome test / hypothesis.

    Every candidate outcome access is keyed by `hypothesis_test_id`; all other
    binding facts are resolved from this registration and verified against the
    project-owned registries at access time. It is never possible to combine an
    unrelated locked wave + session + experiment + profile just because each is
    individually locked.
    """

    hypothesis_test_id: str
    experiment_identity_id: str
    strategy_identity_id: str
    research_lineage_id: str
    family_claim_identity: str
    primary_branch_identity: str
    scope_identity: str
    parameter_search_identity: str
    source_only_session_id: str
    source_only_session_identity: str
    source_bundle_identity: str
    source_bundle_hash: str
    research_wave_id: str
    statistical_profile_id: str
    statistical_profile_identity: str
    multiplicity_counting_unit_identity: str
    protocol_version: str

    def __post_init__(self) -> None:
        required = (
            self.hypothesis_test_id,
            self.experiment_identity_id,
            self.strategy_identity_id,
            self.research_lineage_id,
            self.family_claim_identity,
            self.primary_branch_identity,
            self.scope_identity,
            self.parameter_search_identity,
            self.source_only_session_id,
            self.source_only_session_identity,
            self.source_bundle_identity,
            self.source_bundle_hash,
            self.research_wave_id,
            self.statistical_profile_id,
            self.statistical_profile_identity,
            self.multiplicity_counting_unit_identity,
            self.protocol_version,
        )
        if not all(required):
            raise ValueError("outcome test registration has required empty fields")

    @property
    def registration_identity(self) -> str:
        return _canonical_hash(
            {
                "hypothesis_test_id": self.hypothesis_test_id,
                "experiment_identity_id": self.experiment_identity_id,
                "strategy_identity_id": self.strategy_identity_id,
                "research_lineage_id": self.research_lineage_id,
                "family_claim_identity": self.family_claim_identity,
                "primary_branch_identity": self.primary_branch_identity,
                "scope_identity": self.scope_identity,
                "parameter_search_identity": self.parameter_search_identity,
                "source_only_session_id": self.source_only_session_id,
                "source_only_session_identity": self.source_only_session_identity,
                "source_bundle_identity": self.source_bundle_identity,
                "source_bundle_hash": self.source_bundle_hash,
                "research_wave_id": self.research_wave_id,
                "statistical_profile_id": self.statistical_profile_id,
                "statistical_profile_identity": self.statistical_profile_identity,
                "multiplicity_counting_unit_identity": self.multiplicity_counting_unit_identity,
                "protocol_version": self.protocol_version,
            }
        )


class OutcomeTestRegistry:
    """Append-only registry of identity-bound outcome-test registrations."""

    def __init__(self) -> None:
        self._registrations: dict[str, OutcomeTestRegistration] = {}

    @property
    def registrations(self) -> tuple[OutcomeTestRegistration, ...]:
        return tuple(self._registrations.values())

    def register(self, registration: OutcomeTestRegistration) -> OutcomeTestRegistration:
        if registration.hypothesis_test_id in self._registrations:
            raise ValueError("duplicate hypothesis test id")
        self._registrations[registration.hypothesis_test_id] = registration
        return registration

    def get(self, hypothesis_test_id: str) -> OutcomeTestRegistration | None:
        return self._registrations.get(hypothesis_test_id)


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
        """Fail-closed profile lock.

        Current project policy (`HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0`)
        has no adopted real (non-TEST_ONLY) statistical profile:
        ``STATISTICAL_POSITIVE_ACCEPTANCE_PACKAGE=PARKED`` and
        ``CURRENT_INFERENCE_CANDIDATE=NONE_ADOPTED_FOR_POSITIVE_PASS``. Therefore
        only explicitly TEST_ONLY profiles may be locked (for synthetic engine
        fixtures). An arbitrary real-looking profile is rejected instead of being
        silently treated as a locked acceptance profile.
        """
        if profile_id not in self._profiles:
            raise ValueError("unknown statistical profile id")
        profile = self._profiles[profile_id]
        if not profile.is_test_only:
            raise ValueError(
                "REAL_STATISTICAL_PROFILE_NOT_ADOPTED: only TEST_ONLY profiles can be locked"
            )
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

    @staticmethod
    def build_controls(
        *,
        source_only_verified: bool,
        statistical_profile_locked: bool,
        multiplicity_counting_unit_locked: bool,
        research_wave_locked: bool,
        primary_scope_search_identities_locked: bool,
    ) -> tuple[GateControl, ...]:
        return (
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
        controls = self.build_controls(
            source_only_verified=source_only_verified,
            statistical_profile_locked=statistical_profile_locked,
            multiplicity_counting_unit_locked=multiplicity_counting_unit_locked,
            research_wave_locked=research_wave_locked,
            primary_scope_search_identities_locked=primary_scope_search_identities_locked,
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

    Composes the outcome-test registry, research-wave registry, statistical
    profile registry, SOURCE_ONLY policy, the pre-outcome gate, and the
    historical final-holdout state machine. Candidate outcome access is keyed by
    a single registered hypothesis/test identity and every other fact is resolved
    and verified from project-owned registries — callers never declare frozen lock
    state themselves.
    """

    def __init__(self, ledger: EvidenceLedger) -> None:
        self._ledger = ledger
        self._source_only = SourceOnlyPolicy()
        self._tests = OutcomeTestRegistry()
        self._waves = ResearchWaveRegistry()
        self._profiles = StatisticalProfileRegistry()
        self._gate = PreOutcomeGate()
        self._final_state = HistoricalFinalHoldoutStateMachine()

    @property
    def source_only(self) -> SourceOnlyPolicy:
        return self._source_only

    @property
    def tests(self) -> OutcomeTestRegistry:
        return self._tests

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

    # -- outcome-test registration (identity-bound) -----------------------------

    def register_outcome_test(
        self,
        *,
        hypothesis_test_id: str,
        strategy: StrategyIdentity,
        experiment: ExperimentIdentity,
        family_claim_identity: str,
        primary_branch_identity: str,
        scope_identity: str,
        parameter_search_identity: str,
        source_only_session_id: str,
        research_wave_id: str,
        statistical_profile_id: str,
        multiplicity_counting_unit_identity: str,
    ) -> OutcomeTestRegistration:
        """Create and register a canonical identity-bound outcome-test registration.

        All referenced identities are resolved and validated against the
        project-owned registries at registration time.
        """
        if experiment.strategy_identity_id != strategy.identity_id:
            raise ValueError("experiment does not bind the supplied strategy identity")
        wave = self._waves.get(research_wave_id)
        if wave is None:
            raise ValueError("unknown research wave id")
        if wave.protocol_version != FrozenResearchProtocol.RESEARCH_PROTOCOL_VERSION:
            raise ValueError("wave protocol version mismatch")
        profile = self._profiles.get(statistical_profile_id)
        if profile is None:
            raise ValueError("unknown statistical profile id")
        if wave.statistical_profile_id != profile.profile_id:
            raise ValueError("wave profile id does not match the supplied profile")
        if wave.statistical_profile_identity != profile.profile_identity:
            raise ValueError("wave profile identity does not match the supplied profile")
        if wave.multiplicity_counting_unit_identity != multiplicity_counting_unit_identity:
            raise ValueError("wave counting-unit identity does not match the supplied counting unit")
        binding = wave.binding_for(hypothesis_test_id)
        if binding is None:
            raise ValueError(f"hypothesis has no wave PRIMARY/scope/search binding: {hypothesis_test_id}")
        if primary_branch_identity != binding.primary_branch_identity:
            raise ValueError("primary identity does not match the wave hypothesis binding")
        if scope_identity != binding.scope_identity:
            raise ValueError("scope identity does not match the wave hypothesis binding")
        if parameter_search_identity != binding.parameter_search_identity:
            raise ValueError("parameter/search identity does not match the wave hypothesis binding")
        session = self._source_only.get(source_only_session_id)
        if session is None:
            raise ValueError("unknown SOURCE_ONLY session id")
        registration = OutcomeTestRegistration(
            hypothesis_test_id=hypothesis_test_id,
            experiment_identity_id=experiment.experiment_id,
            strategy_identity_id=strategy.identity_id,
            research_lineage_id=strategy.research_lineage_id,
            family_claim_identity=family_claim_identity,
            primary_branch_identity=primary_branch_identity,
            scope_identity=scope_identity,
            parameter_search_identity=parameter_search_identity,
            source_only_session_id=session.session_id,
            source_only_session_identity=session.session_identity,
            source_bundle_identity=session.source_bundle_identity,
            source_bundle_hash=session.source_bundle_hash,
            research_wave_id=wave.research_wave_id,
            statistical_profile_id=profile.profile_id,
            statistical_profile_identity=profile.profile_identity,
            multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
            protocol_version=FrozenResearchProtocol.RESEARCH_PROTOCOL_VERSION,
        )
        return self._tests.register(registration)

    def lock_wave(self, wave_id: str) -> None:
        """Fail-closed wave lock with cross-registry identity validation."""
        self._waves.lock(wave_id, self._tests)

    # -- authoritative candidate-outcome path -----------------------------------

    @staticmethod
    def cohort_for_dates(data_dates: tuple[date, ...]) -> Cohort:
        """Derive the security cohort from the actual input dates (F-04).

        This is the only way the authoritative candidate API learns its cohort:
        the caller never declares it. Empty input or a mixed-cohort input set
        fails closed.
        """
        if not data_dates:
            raise ValueError("candidate outcome access requires at least one input date")
        cohorts = {classify_cohort(day) for day in data_dates}
        if len(cohorts) != 1:
            raise ValueError("candidate outcome access spans multiple research cohorts")
        return cohorts.pop()

    @staticmethod
    def dataset_class_for_cohort(cohort: Cohort) -> DatasetClass:
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

    def _resolve_binding(self, hypothesis_test_id: str, experiment: ExperimentIdentity) -> tuple[str | None, dict[str, bool] | None]:
        """Resolve the registration and verify every identity binding.

        Returns (None, controls) on success, or (reason, None) on any mismatch.
        No caller-supplied lock booleans are consulted; every fact is derived from
        project-owned registries.
        """
        registration = self._tests.get(hypothesis_test_id)
        if registration is None:
            return "UNREGISTERED_HYPOTHESIS_TEST", None
        if experiment.experiment_id != registration.experiment_identity_id:
            return "EXPERIMENT_IDENTITY_MISMATCH", None
        if experiment.strategy_identity_id != registration.strategy_identity_id:
            return "STRATEGY_IDENTITY_MISMATCH", None
        wave = self._waves.get(registration.research_wave_id)
        if wave is None:
            return "WAVE_MISSING", None
        if not self._waves.is_locked(wave.research_wave_id):
            return "WAVE_NOT_LOCKED", None
        if hypothesis_test_id not in self._waves.denominator(wave.research_wave_id):
            return "HYPOTHESIS_NOT_IN_WAVE_TEST_SET", None
        if registration.research_wave_id != wave.research_wave_id:
            return "REGISTRATION_WAVE_MISMATCH", None
        profile = self._profiles.get(registration.statistical_profile_id)
        if profile is None:
            return "PROFILE_MISSING", None
        if not self._profiles.is_locked(profile.profile_id):
            return "PROFILE_NOT_LOCKED", None
        if profile.profile_identity != registration.statistical_profile_identity:
            return "PROFILE_IDENTITY_MISMATCH", None
        if wave.statistical_profile_id != registration.statistical_profile_id:
            return "WAVE_PROFILE_ID_MISMATCH", None
        if wave.statistical_profile_identity != registration.statistical_profile_identity:
            return "WAVE_PROFILE_IDENTITY_MISMATCH", None
        if registration.multiplicity_counting_unit_identity != wave.multiplicity_counting_unit_identity:
            return "MULTIPLICITY_COUNTING_UNIT_MISMATCH", None
        binding = wave.binding_for(hypothesis_test_id)
        if binding is None:
            return "PRIMARY_SCOPE_SEARCH_BINDING_MISSING", None
        if registration.primary_branch_identity != binding.primary_branch_identity:
            return "PRIMARY_BRANCH_IDENTITY_MISMATCH", None
        if registration.scope_identity != binding.scope_identity:
            return "SCOPE_IDENTITY_MISMATCH", None
        if registration.parameter_search_identity != binding.parameter_search_identity:
            return "PARAMETER_SEARCH_IDENTITY_MISMATCH", None
        session = self._source_only.get(registration.source_only_session_id)
        if session is None:
            return "SOURCE_ONLY_SESSION_MISSING", None
        if session.session_identity != registration.source_only_session_identity:
            return "SOURCE_ONLY_SESSION_IDENTITY_MISMATCH", None
        if session.source_bundle_identity != registration.source_bundle_identity:
            return "SOURCE_BUNDLE_IDENTITY_MISMATCH", None
        if session.source_bundle_hash != registration.source_bundle_hash:
            return "SOURCE_BUNDLE_HASH_MISMATCH", None
        if not self._source_only.is_verified(registration.source_only_session_id):
            return "SOURCE_ONLY_NOT_VERIFIED", None
        if registration.protocol_version != FrozenResearchProtocol.RESEARCH_PROTOCOL_VERSION:
            return "PROTOCOL_VERSION_MISMATCH", None
        controls = {
            "source_only_verified": True,
            "statistical_profile_locked": True,
            "statistical_profile_test_only": profile.is_test_only,
            "multiplicity_counting_unit_locked": True,
            "research_wave_locked": True,
            "primary_scope_search_identities_locked": True,
        }
        return None, controls

    def evaluate_gate(
        self,
        *,
        data_dates: tuple[date, ...],
        experiment: ExperimentIdentity,
        hypothesis_test_id: str,
    ) -> PreOutcomeGateDecision:
        """Authoritative gate evaluation, fully derived from project registries.

        The cohort is derived from the actual input dates (F-04) and the TEST_ONLY
        synthetic status is derived from the governed data version (exact
        equality only). The caller never declares either security fact.
        """
        cohort = self.cohort_for_dates(data_dates)
        synthetic_fixture = experiment.data_version == TEST_ONLY_SYNTHETIC_DATA_VERSION
        mismatch, controls = self._resolve_binding(hypothesis_test_id, experiment)
        if cohort in (
            Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT,
            Cohort.SHADOW_FORWARD,
            Cohort.OUT_OF_SCOPE,
            Cohort.VALIDATION,
        ):
            # Cohort itself is always denied; the gate produces the canonical reason.
            return self._gate.evaluate(
                cohort=cohort,
                source_only_verified=False,
                statistical_profile_locked=False,
                statistical_profile_test_only=False,
                multiplicity_counting_unit_locked=False,
                research_wave_locked=False,
                primary_scope_search_identities_locked=False,
                synthetic_fixture=synthetic_fixture,
            )
        if mismatch is not None or controls is None:
            failed_controls = PreOutcomeGate.build_controls(
                source_only_verified=False,
                statistical_profile_locked=False,
                multiplicity_counting_unit_locked=False,
                research_wave_locked=False,
                primary_scope_search_identities_locked=False,
            )
            return PreOutcomeGateDecision(
                False,
                cohort,
                False,
                "IDENTITY_BINDING:" + (mismatch or "UNRESOLVED"),
                failed_controls,
            )
        return self._gate.evaluate(
            cohort=cohort,
            source_only_verified=controls["source_only_verified"],
            statistical_profile_locked=controls["statistical_profile_locked"],
            statistical_profile_test_only=controls["statistical_profile_test_only"],
            multiplicity_counting_unit_locked=controls["multiplicity_counting_unit_locked"],
            research_wave_locked=controls["research_wave_locked"],
            primary_scope_search_identities_locked=controls["primary_scope_search_identities_locked"],
            synthetic_fixture=synthetic_fixture,
        )

    def request_candidate_outcome_access(
        self,
        *,
        data_dates: tuple[date, ...],
        experiment: ExperimentIdentity,
        hypothesis_test_id: str,
    ) -> AccessResult:
        """Authoritative candidate outcome-bearing access. Fail closed by default.

        Only accepts a registered hypothesis/test identity plus the actual input
        dates. The security cohort is derived from the input dates (F-04) and the
        TEST_ONLY synthetic status from the governed data version (exact equality
        only) — the caller never declares either. Every other fact is resolved and
        verified from the registries. On the first grant, the wave's
        outcome-test-start is recorded durably.
        """
        cohort = self.cohort_for_dates(data_dates)
        decision = self.evaluate_gate(
            data_dates=data_dates,
            experiment=experiment,
            hypothesis_test_id=hypothesis_test_id,
        )
        dataset_class = self.dataset_class_for_cohort(cohort)
        if decision.allowed:
            registration = self._tests.get(hypothesis_test_id)
            profile = self._profiles.get(registration.statistical_profile_id)
            test_only = profile is not None and profile.is_test_only
            first_look = self._waves.declare_outcome_test_start(registration.research_wave_id)
            if first_look:
                self._ledger.append(
                    EvidenceRecord(
                        "WAVE_OUTCOME_TEST_STARTED",
                        experiment,
                        dataset_class,
                        "STARTED",
                        evidence_reference=(
                            f"wave:{registration.research_wave_id};hypothesis:{hypothesis_test_id}"
                        ),
                    )
                )
            audit_note = "SYNTHETIC_TEST_ONLY_FIRST_LOOK" if test_only else "DEVELOPMENT_OUTCOME_GRANTED"
            record = EvidenceRecord(
                "PRE_OUTCOME_GATE_GRANTED",
                experiment,
                dataset_class,
                "GRANTED",
                evidence_reference=(
                    f"{decision.reason};{audit_note};wave:{registration.research_wave_id};"
                    f"hypothesis:{hypothesis_test_id}"
                ),
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
