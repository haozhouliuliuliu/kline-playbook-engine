"""Fail-closed tests for the Jianghe downloaded-Kline Final-Chance V0.2 live runner.

These tests cover the 16 required behaviors:

1. correct plan + correct slot + dry-run/preflight => PASS
2. plan identity mismatch => FAIL
3. plan file SHA mismatch => FAIL
4. provider mismatch => FAIL
5. model mismatch => FAIL
6. missing case => FAIL
7. payload identity mismatch => FAIL
8. NEXT_EXPLICIT_PAID_SLOT=NONE => live execution FAIL
9. slot authority vs command arguments mismatch => FAIL
10. re-executing an already-successful attempt => FAIL
11. HTTP/network failure => no automatic retry
12. malformed provider response => no automatic retry
13. no automatic next-slot behavior
14. secrets never enter evidence/log
15. dry-run makes no network request
16. full repository suite does not regress (run outside this module)

The provider HTTP layer is always mocked; no real paid API call is ever made.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import unittest

from src.jianghe_final_chance_live_lane import (
    FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY,
    PLAN_FILE_SHA256,
    PLAN_PATH,
    FinalChanceError,
    FinalChanceExplicitSlotAuthority,
    FinalChanceGateError,
    FinalChanceInMemoryLedgerStore,
    FinalChancePlanError,
    FinalChanceRemoteExecutionLedger,
    FinalChanceSlotAuthorityError,
    build_final_chance_request,
    committed_plan_file_sha256,
    compute_final_chance_reservation,
    execute_final_chance_slot,
    find_final_chance_slot_identity,
    load_final_chance_explicit_slot_authority,
    load_verified_final_chance_plan,
    preflight_final_chance_slot,
    provider_spec_for,
    reconstruct_final_chance_artifacts,
    verify_final_chance_plan,
)
from src.jianghe_prespend_runtime import load_current_repository_rate_card, load_owner_paid_call_authorization
from src.jianghe_v03_runtime import V03HttpResponse

NOW = datetime(2026, 8, 25, 2, 0, 0, tzinfo=timezone.utc)

_DEEPSEEK_MODEL = "deepseek-v4-flash-vision-exp"
_SCOREABLE_ANSWER = "\n".join(
    [
        "MARKET_INTERPRETATION:",
        "Uptrend continuation with expanding volume and higher lows.",
        "FAMILY:",
        "C",
        "SETUP_OR_NO_SETUP:",
        "Setup present on the 15m continuation leg.",
        "ACTION:",
        "WAIT",
        "DIRECTION_IF_APPLICABLE:",
        "LONG",
        "EVIDENCE:",
        "Higher highs, higher lows and a defended demand zone.",
        "INVALIDATION_OR_UNCERTAINTY:",
        "A close back below the breakout level would invalidate the read.",
        "JIANGHE_PRINCIPLES_USED:",
        "Trend-following continuation and key-zone respect.",
        "VISUAL_OBSERVATIONS:",
        "The 5m panel shows a clean trend structure.",
        "STRUCTURED_OBSERVATIONS:",
        "Structured bars agree with the visual panel.",
        "CONTRADICTIONS:",
        "NONE",
        "DECLARED_UNKNOWN:",
        "NONE",
        "",
    ]
)


def _plan_bytes() -> bytes:
    return PLAN_PATH.read_bytes()


def _load_plan() -> dict[str, object]:
    return load_verified_final_chance_plan(plan_bytes=_plan_bytes())


def _ok_body(model_id: str = _DEEPSEEK_MODEL, text: str = _SCOREABLE_ANSWER) -> bytes:
    return json.dumps(
        {
            "id": "req-test-001",
            "model": model_id,
            "choices": [
                {"message": {"content": text}, "finish_reason": "stop"}
            ],
            "usage": {"prompt_tokens": 1000, "completion_tokens": 500},
        }
    ).encode("utf-8")


def _ok_http(url: str, headers, body: bytes, timeout: float) -> V03HttpResponse:
    return V03HttpResponse(200, _ok_body())


def _make_authority(
    plan: dict[str, object],
    provider_id: str,
    sample_id: str,
    now: datetime,
    *,
    model_id_override: str | None = None,
    plan_identity_override: str | None = None,
    plan_file_sha_override: str | None = None,
) -> FinalChanceExplicitSlotAuthority:
    spec = provider_spec_for(provider_id)
    rate_card = load_current_repository_rate_card(spec, now=now)
    request, transport, config, _prompt_hashes = build_final_chance_request(
        plan, provider_id=provider_id, sample_id=sample_id, now=now
    )
    worst, _image_bound = compute_final_chance_reservation(request, transport, config, rate_card)
    case_identity = next(
        binding["common_case_identity"]
        for binding in plan["common_case_bindings"]
        if binding["sample_id"] == sample_id
    )
    paid_auth = load_owner_paid_call_authorization(now=now)
    authority = FinalChanceExplicitSlotAuthority(
        explicit_slot_identity=f"DKL_FC_V0_2:{provider_id}:{sample_id}",
        plan_identity=plan_identity_override or str(plan["pilot_plan_identity"]),
        plan_file_sha256=plan_file_sha_override or committed_plan_file_sha256(),
        provider_id=provider_id,
        model_id=model_id_override or config.model_id,
        sample_id=sample_id,
        case_identity=str(case_identity),
        authorization_id=paid_auth.authorization_id,
        rate_card_identity=rate_card.identity,
        worst_case_reservation_cny=(_decimal_text(worst) or "0"),
        effective_at=datetime(2026, 8, 24, 0, 0, tzinfo=timezone.utc),
        expires_at=datetime(2026, 8, 30, 23, 59, 59, tzinfo=timezone.utc),
        authority_identity="",
    )
    payload = authority.payload()
    return FinalChanceExplicitSlotAuthority.from_payload(payload)


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


class FinalChanceLiveRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = _load_plan()
        self.plan_sha = committed_plan_file_sha256()

    # --- 1. correct plan + correct slot + dry-run/preflight => PASS ---
    def test_correct_plan_slot_dry_run_passes(self) -> None:
        authority = _make_authority(self.plan, "DEEPSEEK", "DKL-FC-001", NOW)
        store = FinalChanceInMemoryLedgerStore()
        result = execute_final_chance_slot(
            provider_id="DEEPSEEK",
            sample_id="DKL-FC-001",
            now=NOW,
            store=store,
            slot_authority=authority,
            dry_run=True,
        )
        self.assertTrue(result.dry_run)
        self.assertEqual("PREFLIGHT_PASS", result.status)
        self.assertEqual("DKL_FC_V0_2:DEEPSEEK:DKL-FC-001", result.slot_identity)

        preflight = preflight_final_chance_slot(
            plan=self.plan,
            provider_id="DEEPSEEK",
            sample_id="DKL-FC-001",
            now=NOW,
            slot_authority=authority,
            store=store,
            plan_file_sha256=self.plan_sha,
        )
        self.assertTrue(preflight.passed)
        self.assertEqual("PASS", preflight.gates["E_EXPLICIT_SLOT_AUTHORITY"])
        self.assertEqual("PASS", preflight.gates["F_ATTEMPT_FRESH"])
        self.assertGreater(Decimal(preflight.remaining_cny), Decimal("0"))

    def test_all_four_cases_reconstruct_against_committed_plan(self) -> None:
        for sample in self.plan["samples"]:
            observation, structured, visual, _hashes = reconstruct_final_chance_artifacts(sample)
            self.assertEqual(sample["observation_identity"], observation.identity.identity)
            self.assertEqual(sample["full_structured_observation_identity"], structured.identity)
            self.assertEqual(sample["png_sha256"], visual.content_sha256)

    # --- 2. plan identity mismatch => FAIL ---
    def test_plan_identity_mismatch_fails(self) -> None:
        tampered = dict(self.plan)
        tampered["decision_prompt_addendum"] = "TAMPERED_ADDENDUM"
        with self.assertRaisesRegex(FinalChancePlanError, "plan identity mismatch"):
            verify_final_chance_plan(tampered)

    # --- 3. plan file SHA mismatch => FAIL ---
    def test_plan_file_sha_mismatch_fails(self) -> None:
        bad_bytes = _plan_bytes() + b" "
        with self.assertRaisesRegex(FinalChancePlanError, "SHA-256"):
            load_verified_final_chance_plan(plan_bytes=bad_bytes)
        self.assertNotEqual(sha256(bad_bytes).hexdigest(), PLAN_FILE_SHA256)

    # --- 4. provider mismatch => FAIL ---
    def test_provider_mismatch_fails(self) -> None:
        with self.assertRaisesRegex(FinalChanceGateError, "unsupported final-chance provider"):
            build_final_chance_request(self.plan, provider_id="OTHER", sample_id="DKL-FC-001", now=NOW)

    # --- 5. model mismatch => FAIL ---
    def test_model_mismatch_fails(self) -> None:
        tampered = copy.deepcopy(self.plan)
        tampered["provider_configs"][0]["model_id"] = "wrong-model"
        with self.assertRaisesRegex(FinalChanceGateError, "provider model differs"):
            build_final_chance_request(tampered, provider_id="DEEPSEEK", sample_id="DKL-FC-001", now=NOW)

    # --- 6. missing case => FAIL ---
    def test_missing_case_fails(self) -> None:
        with self.assertRaisesRegex(FinalChanceGateError, "no sample"):
            build_final_chance_request(self.plan, provider_id="DEEPSEEK", sample_id="DKL-FC-999", now=NOW)

    # --- 7. payload identity mismatch => FAIL ---
    def test_payload_identity_mismatch_fails(self) -> None:
        sample = copy.deepcopy(self.plan["samples"][0])
        sample["png_sha256"] = "0" * 64
        with self.assertRaisesRegex(FinalChancePlanError, "png_sha256"):
            reconstruct_final_chance_artifacts(sample)

    # --- 8. NEXT_EXPLICIT_PAID_SLOT=NONE => live execution FAIL ---
    def test_none_explicit_slot_blocks_live_execution(self) -> None:
        with self.assertRaisesRegex(FinalChanceGateError, "NEXT_EXPLICIT_PAID_SLOT"):
            preflight_final_chance_slot(
                plan=self.plan,
                provider_id="DEEPSEEK",
                sample_id="DKL-FC-001",
                now=NOW,
                slot_authority=None,
            )
        # The committed loader returns None when the authority file is absent.
        def absent() -> bytes:
            raise ValueError("absent")

        self.assertIsNone(load_final_chance_explicit_slot_authority(read_bytes=absent))

    # --- 9. slot authority vs command arguments mismatch => FAIL ---
    def test_slot_authority_mismatch_fails(self) -> None:
        authority = _make_authority(self.plan, "DEEPSEEK", "DKL-FC-001", NOW)
        with self.assertRaisesRegex(FinalChanceGateError, "requested slot identity"):
            preflight_final_chance_slot(
                plan=self.plan,
                provider_id="MINIMAX",
                sample_id="DKL-FC-001",
                now=NOW,
                slot_authority=authority,
                store=FinalChanceInMemoryLedgerStore(),
                plan_file_sha256=self.plan_sha,
            )

    def test_slot_authority_plan_binding_mismatch_fails(self) -> None:
        authority = _make_authority(
            self.plan,
            "DEEPSEEK",
            "DKL-FC-001",
            NOW,
            plan_identity_override="0" * 64,
        )
        with self.assertRaisesRegex(FinalChanceGateError, "plan binding"):
            preflight_final_chance_slot(
                plan=self.plan,
                provider_id="DEEPSEEK",
                sample_id="DKL-FC-001",
                now=NOW,
                slot_authority=authority,
                store=FinalChanceInMemoryLedgerStore(),
                plan_file_sha256=self.plan_sha,
            )

    def test_slot_authority_model_binding_mismatch_fails(self) -> None:
        authority = _make_authority(
            self.plan, "DEEPSEEK", "DKL-FC-001", NOW, model_id_override="wrong-model"
        )
        with self.assertRaisesRegex(FinalChanceGateError, "model differs"):
            preflight_final_chance_slot(
                plan=self.plan,
                provider_id="DEEPSEEK",
                sample_id="DKL-FC-001",
                now=NOW,
                slot_authority=authority,
                store=FinalChanceInMemoryLedgerStore(),
                plan_file_sha256=self.plan_sha,
            )

    # --- 10. re-executing an already-successful attempt => FAIL ---
    def test_successful_attempt_re_execution_fails(self) -> None:
        authority = _make_authority(self.plan, "DEEPSEEK", "DKL-FC-001", NOW)
        store = FinalChanceInMemoryLedgerStore()
        first = execute_final_chance_slot(
            provider_id="DEEPSEEK",
            sample_id="DKL-FC-001",
            now=NOW,
            store=store,
            slot_authority=authority,
            http_post=_ok_http,
            credential_lookup=lambda _name: "TEST_KEY",
        )
        self.assertEqual("CAPABILITY_SCOREABLE", first.status)
        with self.assertRaisesRegex(FinalChanceGateError, "already exists"):
            execute_final_chance_slot(
                provider_id="DEEPSEEK",
                sample_id="DKL-FC-001",
                now=NOW,
                store=store,
                slot_authority=authority,
                http_post=_ok_http,
                credential_lookup=lambda _name: "TEST_KEY",
            )

    # --- 11. HTTP/network failure => no automatic retry ---
    def test_network_failure_never_retries(self) -> None:
        def failing_http(url, headers, body: bytes, timeout: float) -> V03HttpResponse:
            raise RuntimeError("provider transport failed: <urlopen error timed out>")

        authority = _make_authority(self.plan, "DEEPSEEK", "DKL-FC-001", NOW)
        store = FinalChanceInMemoryLedgerStore()
        result = execute_final_chance_slot(
            provider_id="DEEPSEEK",
            sample_id="DKL-FC-001",
            now=NOW,
            store=store,
            slot_authority=authority,
            http_post=failing_http,
            credential_lookup=lambda _name: "TEST_KEY",
        )
        self.assertEqual("INFRASTRUCTURE_FAILURE", result.status)
        self.assertEqual(0, result.automatic_retries)
        observed = store.load(str(self.plan["pilot_plan_identity"]), self.plan_sha)
        self.assertEqual(1, observed.ledger.snapshot().total_attempts)
        self.assertEqual(1, len(store.artifacts()))

    # --- 12. malformed provider response => no automatic retry ---
    def test_malformed_response_never_retries(self) -> None:
        def malformed_http(url, headers, body: bytes, timeout: float) -> V03HttpResponse:
            return V03HttpResponse(200, b"this is not json")

        authority = _make_authority(self.plan, "DEEPSEEK", "DKL-FC-001", NOW)
        store = FinalChanceInMemoryLedgerStore()
        result = execute_final_chance_slot(
            provider_id="DEEPSEEK",
            sample_id="DKL-FC-001",
            now=NOW,
            store=store,
            slot_authority=authority,
            http_post=malformed_http,
            credential_lookup=lambda _name: "TEST_KEY",
        )
        self.assertEqual("PROVIDER_RESPONSE_MALFORMED", result.status)
        self.assertEqual(0, result.automatic_retries)
        observed = store.load(str(self.plan["pilot_plan_identity"]), self.plan_sha)
        self.assertEqual(1, observed.ledger.snapshot().total_attempts)
        self.assertEqual(1, len(store.artifacts()))

    # --- 13. no automatic next-slot behavior ---
    def test_no_automatic_next_slot(self) -> None:
        authority = _make_authority(self.plan, "DEEPSEEK", "DKL-FC-001", NOW)
        store = FinalChanceInMemoryLedgerStore()
        result = execute_final_chance_slot(
            provider_id="DEEPSEEK",
            sample_id="DKL-FC-001",
            now=NOW,
            store=store,
            slot_authority=authority,
            http_post=_ok_http,
            credential_lookup=lambda _name: "TEST_KEY",
        )
        self.assertEqual(0, result.automatic_next_slots)
        snapshot = store.load(str(self.plan["pilot_plan_identity"]), self.plan_sha).ledger.snapshot()
        self.assertEqual(1, snapshot.total_attempts)
        self.assertEqual(frozenset({"DKL_FC_V0_2:DEEPSEEK:DKL-FC-001"}), snapshot.attempted_slots)

    # --- 14. secrets never enter evidence/log ---
    def test_secrets_never_enter_evidence(self) -> None:
        secret = "DEEPSEEK_SUPER_SECRET_TOKEN_9f8e7d6c5b4a"
        captured_headers: dict[str, str] = {}

        def capturing_http(url, headers, body: bytes, timeout: float) -> V03HttpResponse:
            captured_headers.update(headers)
            return V03HttpResponse(200, _ok_body())

        authority = _make_authority(self.plan, "DEEPSEEK", "DKL-FC-001", NOW)
        store = FinalChanceInMemoryLedgerStore()
        execute_final_chance_slot(
            provider_id="DEEPSEEK",
            sample_id="DKL-FC-001",
            now=NOW,
            store=store,
            slot_authority=authority,
            http_post=capturing_http,
            credential_lookup=lambda _name: secret,
        )
        self.assertIn(secret, captured_headers.get("Authorization", ""))
        for name, content in store.artifacts().items():
            decoded = content.decode("utf-8", errors="ignore")
            self.assertNotIn(secret, decoded, f"secret leaked into {name}")
            payload = json.loads(content.decode("utf-8"))
            self.assertFalse(payload["credential_value_exposed"])
            self.assertFalse(payload["hidden_reasoning_persisted"])

    # --- 15. dry-run makes no network request ---
    def test_dry_run_makes_no_network_request(self) -> None:
        calls = {"count": 0}

        def counting_http(url, headers, body: bytes, timeout: float) -> V03HttpResponse:
            calls["count"] += 1
            return V03HttpResponse(200, _ok_body())

        authority = _make_authority(self.plan, "DEEPSEEK", "DKL-FC-001", NOW)
        store = FinalChanceInMemoryLedgerStore()
        result = execute_final_chance_slot(
            provider_id="DEEPSEEK",
            sample_id="DKL-FC-001",
            now=NOW,
            store=store,
            slot_authority=authority,
            http_post=counting_http,
            credential_lookup=lambda _name: "TEST_KEY",
            dry_run=True,
        )
        self.assertTrue(result.dry_run)
        self.assertEqual(0, calls["count"])
        ledger = store.load(str(self.plan["pilot_plan_identity"]), self.plan_sha).ledger
        self.assertEqual((), ledger.events)

    # --- ledger integrity: duplicate start is rejected ---
    def test_ledger_rejects_duplicate_start(self) -> None:
        ledger = FinalChanceRemoteExecutionLedger(str(self.plan["pilot_plan_identity"]), self.plan_sha)
        ledger = ledger.append_start(
            now=NOW,
            provider_id="DEEPSEEK",
            slot_identity="DKL_FC_V0_2:DEEPSEEK:DKL-FC-001",
            request_identity="0" * 64,
            worst_case_cny=Decimal("0.01"),
        )
        with self.assertRaises(Exception):
            ledger.append_start(
                now=NOW,
                provider_id="DEEPSEEK",
                slot_identity="DKL_FC_V0_2:DEEPSEEK:DKL-FC-001",
                request_identity="1" * 64,
                worst_case_cny=Decimal("0.01"),
            )

    def test_shared_ledger_carry_is_authoritative(self) -> None:
        self.assertEqual(Decimal("3.1609662"), FINAL_CHANCE_HISTORICAL_PROJECT_ACCOUNTED_CNY)


if __name__ == "__main__":
    unittest.main()
