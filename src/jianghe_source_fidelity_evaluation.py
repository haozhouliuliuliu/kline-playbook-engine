"""Deterministic evaluator-side Jianghe source-fidelity adjudication.

Source-fidelity adjudication belongs to evaluation, never to model self-report.
This module provides a bounded, fixture/corpus-bound mechanism that records the
canonical semantics of a Jianghe claim (its category and minimal proposition)
and adjudicates whether a given, evaluator-supplied use of that claim stays
inside its canonical meaning.

The ``observed_use_category`` is an evaluator-side assertion (bound from the
actual accepted response evidence by a human/project reviewer), NOT something
parsed from rationale by the deterministic layer.  This preserves the existing
principle that the model never grades its own source faithfulness.

The canonical fixture for ``JH-CLM-034-002`` is grounded in the committed
claim-level branch registry; a regression test verifies the fixture agrees with
the registry record.  This keeps the known three-call smoke finding
(``JH-CLM-034-002`` used as a PRE_ENTRY_REQUIREMENT while its canonical category
is MANAGEMENT) detectable as a deterministic source-faithfulness finding.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

SOURCE_FIDELITY_EVALUATOR_VERSION = "KPE_JIANGHE_SOURCE_FIDELITY_EVALUATOR_V0_1"
SOURCE_FAITHFULNESS_FINDING = "SOURCE_FAITHFULNESS_FINDING"
SOURCE_FIDELITY_OK = "SOURCE_FIDELITY_OK"


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _strict_string_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise ValueError(f"{field_name} must be a non-empty array of non-empty strings")
    return tuple(value)


@dataclass(frozen=True)
class SourceClaimFidelityFixture:
    """Canonical claim semantics used by the evaluator (not by the model)."""

    claim_id: str
    canonical_category: str
    canonical_proposition: str
    allowed_use_categories: tuple[str, ...]
    fixture_id: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.claim_id, "claim_id")
        _require_text(self.canonical_category, "canonical_category")
        _require_text(self.canonical_proposition, "canonical_proposition")
        _require_text(self.fixture_id, "fixture_id")
        categories = _strict_string_tuple(self.allowed_use_categories, "allowed_use_categories")
        if self.canonical_category not in categories:
            raise ValueError("allowed_use_categories must include the canonical category")
        object.__setattr__(
            self,
            "identity",
            _hash({
                "source_fidelity_evaluator_version": SOURCE_FIDELITY_EVALUATOR_VERSION,
                "claim_id": self.claim_id,
                "canonical_category": self.canonical_category,
                "canonical_proposition": self.canonical_proposition,
                "allowed_use_categories": self.allowed_use_categories,
                "fixture_id": self.fixture_id,
            }),
        )

    def assert_registry_consistent(self, registry_record: Mapping[str, object]) -> None:
        """Fail closed if this fixture disagrees with the canonical registry record."""
        if not isinstance(registry_record, Mapping):
            raise ValueError("registry record must be a mapping")
        record_claim_id = registry_record.get("claim_id")
        record_category = registry_record.get("claim_category")
        if record_claim_id != self.claim_id:
            raise ValueError(
                f"registry record claim_id {record_claim_id!r} does not match fixture {self.claim_id!r}"
            )
        if record_category != self.canonical_category:
            raise ValueError(
                f"registry record category {record_category!r} does not match fixture "
                f"canonical_category {self.canonical_category!r}"
            )
        return None


@dataclass(frozen=True)
class SourceFidelityFinding:
    """One evaluator-side source-faithfulness adjudication for a claim use."""

    claim_id: str
    canonical_category: str
    observed_use_category: str
    finding_type: str
    finding_evidence: tuple[str, ...]
    fixture_identity: str
    source_fidelity_evaluator_version: str = SOURCE_FIDELITY_EVALUATOR_VERSION
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("claim_id", "canonical_category", "observed_use_category", "finding_type"):
            _require_text(getattr(self, name), name)
        _require_text(self.fixture_identity, "fixture_identity")
        _require_text(self.source_fidelity_evaluator_version, "source_fidelity_evaluator_version")
        if self.finding_type not in (SOURCE_FAITHFULNESS_FINDING, SOURCE_FIDELITY_OK):
            raise ValueError(f"unsupported finding_type {self.finding_type!r}")
        if not isinstance(self.finding_evidence, tuple) or any(
            not isinstance(item, str) or not item for item in self.finding_evidence
        ):
            raise ValueError("finding_evidence must be a tuple of non-empty strings")
        object.__setattr__(
            self,
            "identity",
            _hash({
                "claim_id": self.claim_id,
                "canonical_category": self.canonical_category,
                "observed_use_category": self.observed_use_category,
                "finding_type": self.finding_type,
                "finding_evidence": self.finding_evidence,
                "fixture_identity": self.fixture_identity,
                "source_fidelity_evaluator_version": self.source_fidelity_evaluator_version,
            }),
        )

    def to_payload(self) -> dict[str, object]:
        return {
            "claim_id": self.claim_id,
            "canonical_category": self.canonical_category,
            "observed_use_category": self.observed_use_category,
            "finding_type": self.finding_type,
            "finding_evidence": list(self.finding_evidence),
            "fixture_identity": self.fixture_identity,
            "source_fidelity_evaluator_version": self.source_fidelity_evaluator_version,
            "identity": self.identity,
        }


def adjudicate_source_fidelity(
    fixture: SourceClaimFidelityFixture,
    *,
    observed_use_category: str,
    finding_evidence: tuple[str, ...],
) -> SourceFidelityFinding:
    """Adjudicate one evaluator-supplied claim use against the canonical fixture.

    Deterministic: a use is a SOURCE_FAITHFULNESS_FINDING when its observed
    category is outside the fixture's canonical allowed use categories; otherwise
    SOURCE_FIDELITY_OK.  No natural-language parsing occurs here.
    """
    if not isinstance(fixture, SourceClaimFidelityFixture):
        raise TypeError("fixture must be a SourceClaimFidelityFixture")
    _require_text(observed_use_category, "observed_use_category")
    if not isinstance(finding_evidence, tuple) or not finding_evidence:
        raise ValueError("finding_evidence must be a non-empty tuple")
    if observed_use_category in fixture.allowed_use_categories:
        finding_type = SOURCE_FIDELITY_OK
    else:
        finding_type = SOURCE_FAITHFULNESS_FINDING
    return SourceFidelityFinding(
        claim_id=fixture.claim_id,
        canonical_category=fixture.canonical_category,
        observed_use_category=observed_use_category,
        finding_type=finding_type,
        finding_evidence=finding_evidence,
        fixture_identity=fixture.identity,
    )


# Canonical fixture grounded in the committed claim-level branch registry:
# JH-CLM-034-002 is a MANAGEMENT claim ("盈利订单可随新发力/防守结构推进止损；
# 二推不能突破前高是动能减弱退出线索。").  The known three-call smoke finding is
# that the model used it as a PRE_ENTRY_REQUIREMENT, outside its canonical category.
JH_CLM_034_002_FIDELITY_FIXTURE = SourceClaimFidelityFixture(
    claim_id="JH-CLM-034-002",
    canonical_category="MANAGEMENT",
    canonical_proposition="盈利订单可随新发力/防守结构推进止损；二推不能突破前高是动能减弱退出线索。",
    allowed_use_categories=("MANAGEMENT",),
    fixture_id="JIANGHE_SOURCE_FIDELITY_FIXTURE_JH_CLM_034_002_V0_1",
)

# Evaluator-side observed use from the accepted three-call smoke evidence.
JH_CLM_034_002_SMOKE_OBSERVED_USE_CATEGORY = "PRE_ENTRY_REQUIREMENT"
JH_CLM_034_002_SMOKE_FINDING_EVIDENCE = (
    "The three-call smoke response cites JH-CLM-034-002 to support that a real "
    "entry usually appears after a new launch point from a push-pull-push, "
    "converting a canonical MANAGEMENT claim into a pre-entry requirement.",
)


def load_source_claim_registry(path: str | Path) -> dict[str, dict[str, object]]:
    """Read the committed claim-level branch registry into a claim_id -> record map."""
    registry_path = Path(path)
    records: dict[str, dict[str, object]] = {}
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        if not isinstance(record, dict):
            raise ValueError("registry line must be a JSON object")
        claim_id = record.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            raise ValueError("registry record has no claim_id")
        records[claim_id] = record
    if not records:
        raise ValueError("registry is empty")
    return records


__all__ = [
    "JH_CLM_034_002_FIDELITY_FIXTURE",
    "JH_CLM_034_002_SMOKE_FINDING_EVIDENCE",
    "JH_CLM_034_002_SMOKE_OBSERVED_USE_CATEGORY",
    "SOURCE_FIDELITY_EVALUATOR_VERSION",
    "SOURCE_FIDELITY_OK",
    "SOURCE_FAITHFULNESS_FINDING",
    "SourceClaimFidelityFixture",
    "SourceFidelityFinding",
    "adjudicate_source_fidelity",
    "load_source_claim_registry",
]
