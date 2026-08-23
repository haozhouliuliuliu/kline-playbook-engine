from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "jianghe_prespend_runtime.py"
TEST = ROOT / "tests" / "test_jianghe_prespend_repair.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one exact replacement, found {count}: {old[:120]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


replace_once(
    RUNTIME,
    '            "selection_semantics": "FIXTURE_SOURCE_ANCHORS_TO_PRIMARY_V0_5_EXACT_JSONL_RECORDS",\n',
    '            "selection_semantics": "FIXTURE_SOURCE_ANCHORS_TO_PRIMARY_V0_5_SAFE_SEMANTIC_PROJECTION",\n',
)

anchor = '''    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _scan_forbidden(nested, f"{path}[{index}]")


@dataclass(frozen=True)
class SelectedContextDocument:
'''
insert = '''    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _scan_forbidden(nested, f"{path}[{index}]")


_PRIMARY_MODEL_CONTEXT_FIELDS = (
    "claim_category",
    "claim_id",
    "contradiction_ids",
    "family_scope",
    "invalidation_scope",
    "management_or_exit_scope",
    "no_trade_guard",
    "operationalization_interpretation",
    "pre_freeze_disposition",
    "selected_interpretation_text",
    "semantic_mode",
    "source_meaning",
    "unknown_ids",
)
_FORBIDDEN_MODEL_CONTEXT_CATEGORY_MARKERS = ("OUTCOME", "PERFORMANCE", "PNL", "PROFIT", "RETURN")
_FORBIDDEN_MODEL_CONTEXT_VALUE_MARKERS = (
    "candidate_outcome",
    "future_price",
    "future_return",
    "real_candidate_pnl",
    "win_rate",
    "sharpe",
    "expectancy",
    "后续价格路径",
    "任何盈亏结果",
    "任何结果标签",
    "胜率/期望值",
)


def _primary_model_context_projection(record: Mapping[str, object]) -> str:
    """Return the only PRIMARY V0.5 fields allowed to leave the process as model context.

    The full PRIMARY registry record remains local provenance. Review metadata, source-file
    paths, fixture material, historical outcome text and other audit baggage are not sent.
    """
    if not isinstance(record, Mapping):
        raise ValueError("PRIMARY context source record must be an object")
    claim_id = _require_text(record.get("claim_id"), "primary_context.claim_id")
    claim_category = _require_text(record.get("claim_category"), "primary_context.claim_category")
    upper_category = claim_category.upper()
    if any(marker in upper_category for marker in _FORBIDDEN_MODEL_CONTEXT_CATEGORY_MARKERS):
        raise ValueError("outcome/performance claim category is not spend-eligible context")

    def text_or_unknown(name: str) -> str:
        value = record.get(name)
        if value is None:
            return "UNKNOWN"
        return _require_text(value, f"primary_context.{name}")

    def text_list(name: str) -> list[str]:
        value = record.get(name)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
            raise ValueError(f"primary_context.{name} must be a string list")
        if len(set(value)) != len(value):
            raise ValueError(f"primary_context.{name} must be unique")
        return sorted(value)

    projection: dict[str, object] = {
        "claim_category": claim_category,
        "claim_id": claim_id,
        "contradiction_ids": text_list("contradiction_ids"),
        "family_scope": text_list("family_scope"),
        "invalidation_scope": text_or_unknown("invalidation_scope"),
        "management_or_exit_scope": text_or_unknown("management_or_exit_scope"),
        "no_trade_guard": text_or_unknown("no_trade_guard"),
        "operationalization_interpretation": text_or_unknown("operationalization_interpretation"),
        "pre_freeze_disposition": text_or_unknown("pre_freeze_disposition"),
        "selected_interpretation_text": text_or_unknown("selected_interpretation_text"),
        "semantic_mode": text_or_unknown("semantic_mode"),
        "source_meaning": text_or_unknown("source_meaning"),
        "unknown_ids": text_list("unknown_ids"),
    }
    _scan_forbidden(projection, "primary_model_context")
    serialized = _canonical_json(projection)
    lowered = serialized.lower()
    if any(marker.lower() in lowered for marker in _FORBIDDEN_MODEL_CONTEXT_VALUE_MARKERS):
        raise ValueError("selected PRIMARY semantic projection contains forbidden outcome/future material")
    return serialized


@dataclass(frozen=True)
class SelectedContextDocument:
'''
replace_once(RUNTIME, anchor, insert)

old_payload_tail = '''        if include_identity:
            payload["selected_context_identity"] = self.identity
        return payload


@dataclass(frozen=True, init=False)
class CanonicalStructuredObservationArtifact:
'''
new_payload_tail = '''        payload["model_context_identity"] = self.model_payload()["model_context_identity"]
        if include_identity:
            payload["selected_context_identity"] = self.identity
        return payload

    def model_payload(self) -> dict[str, object]:
        """Exact context material sent to the model; fixture answers and audit baggage stay local."""
        if self.fixture_id is None or self.selection_basis_identity is None:
            raise ValueError("model context requires deterministic fixture-bound selection")
        projected_documents: list[dict[str, object]] = []
        for item in self.documents:
            if item.repository_path != PRIMARY_REGISTRY_RELATIVE_PATH:
                raise ValueError("spend-eligible model context must project current PRIMARY V0.5 records")
            try:
                record = json.loads(item.selected_text)
            except json.JSONDecodeError as error:
                raise ValueError("selected PRIMARY source record is malformed") from error
            if not isinstance(record, Mapping):
                raise ValueError("selected PRIMARY source record must be an object")
            claim_id = _require_text(record.get("claim_id"), "selected_primary.claim_id")
            if claim_id not in self.source_claim_ids:
                raise ValueError("selected PRIMARY record is outside fixture source anchors")
            projected_text = _primary_model_context_projection(record)
            projected_documents.append(
                {
                    "claim_id": claim_id,
                    "source_record_identity": item.identity,
                    "selected_text": projected_text,
                    "selected_text_sha256": sha256(projected_text.encode("utf-8")).hexdigest(),
                }
            )
        projected_documents.sort(key=lambda value: (str(value["claim_id"]), str(value["source_record_identity"])))
        payload: dict[str, object] = {
            "version": SELECTED_CONTEXT_VERSION,
            "knowledge_pack_identity": self.knowledge_pack_identity,
            "primary_manifest_identity": self.primary_manifest_identity,
            "primary_registry_version": self.primary_registry_version,
            "context_selection_policy_identity": self.context_selection_policy_identity,
            "source_claim_ids": list(self.source_claim_ids),
            "selection_basis_identity": self.selection_basis_identity,
            "documents": projected_documents,
        }
        payload["model_context_identity"] = _hash(payload)
        return payload


@dataclass(frozen=True, init=False)
class CanonicalStructuredObservationArtifact:
'''
replace_once(RUNTIME, old_payload_tail, new_payload_tail)

replace_once(
    RUNTIME,
    '                    "selected_context_identity": self.context.identity,\n                    "structured_observation_identity": self.structured_observation.identity,\n',
    '                    "selected_context_identity": self.context.identity,\n                    "model_context_identity": self.context.model_payload()["model_context_identity"],\n                    "structured_observation_identity": self.structured_observation.identity,\n',
)
replace_once(
    RUNTIME,
    '                "jianghe_context": self.context.to_payload(),\n',
    '                "jianghe_context": self.context.model_payload(),\n',
)

old_test = '''    def test_request_identity_changes_with_fixture_selected_context(self):
        first = _request("JH-FIX-A-001")
        second = _request("JH-FIX-A-002")
        self.assertNotEqual(first.context.identity, second.context.identity)
        self.assertNotEqual(first.identity, second.identity)
        self.assertIn("JH-CLM-006-SP01", first.common_model_text())

    def test_manual_unrelated_context_cannot_become_spend_eligible(self):
'''
new_test = '''    def test_request_identity_changes_with_fixture_selected_context(self):
        first = _request("JH-FIX-A-001")
        second = _request("JH-FIX-A-002")
        self.assertNotEqual(first.context.identity, second.context.identity)
        self.assertNotEqual(first.identity, second.identity)
        self.assertIn("JH-CLM-006-SP01", first.common_model_text())

    def test_model_receives_safe_primary_projection_not_fixture_answers_or_audit_baggage(self):
        request = _request("JH-FIX-A-001")
        model_text = request.common_model_text()
        for forbidden in (
            "JH-FIX-A-001",
            "hidden_future_information",
            '"expected"',
            '"rubric"',
            "review_evidence",
            "source_finding",
            '"bvid"',
        ):
            self.assertNotIn(forbidden, model_text)
        payload = request.context.model_payload()
        self.assertEqual(payload["source_claim_ids"], list(request.context.source_claim_ids))
        self.assertEqual(
            payload["model_context_identity"], request.context.to_payload()["model_context_identity"]
        )
        expected_fields = {
            "claim_category", "claim_id", "contradiction_ids", "family_scope",
            "invalidation_scope", "management_or_exit_scope", "no_trade_guard",
            "operationalization_interpretation", "pre_freeze_disposition",
            "selected_interpretation_text", "semantic_mode", "source_meaning", "unknown_ids",
        }
        for document in payload["documents"]:
            projection = json.loads(document["selected_text"])
            self.assertEqual(set(projection), expected_fields)
            self.assertEqual(document["claim_id"], projection["claim_id"])

    def test_manual_unrelated_context_cannot_become_spend_eligible(self):
'''
replace_once(TEST, old_test, new_test)

print("prespend context projection v06 staged")
