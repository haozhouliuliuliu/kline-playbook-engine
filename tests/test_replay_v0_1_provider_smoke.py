"""Provider-smoke prep tests for SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1.

All tests are zero-cost: the smoke runner runs only with the deterministic mock
transport or a PENDING authority (which fails the gate before any network
capability).  The pinned Harness bridge is never executed here, and no provider
credential is ever read.

``REAL_DEEPSEEK_PROVIDER_CALLS = 0`` holds for the entire module.
"""
from __future__ import annotations

from datetime import date, datetime, time, timezone
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest

from src.jianghe_ai_trader import ReplayClock
from src.fixed_5m_wake_ledger import WakeLedgerArchive, wake_ledger_path_for
from src.jianghe_visual_renderer import JiangheVisualRenderer, RENDERER_VERSION
from src.replay_v0_1_orchestrator import (
    PHASE_BURN_IN,
    ReplayV01Orchestrator,
    SyntheticScriptedTransport,
)
from src.replay_v0_1_provider_attempt_ledger import (
    ATTEMPT_STARTED,
    RESULT_RECEIVED,
    UNKNOWN_AFTER_ATTEMPT_START,
    ProviderAttemptLedger,
    provider_attempt_ledger_path_for,
)
from src.replay_v0_1_smoke_authority import (
    CNY_CEILING_MODE_NUMERIC,
    CNY_CEILING_MODE_WAIVED,
    OWNER_CNY_CEILING_WAIVED,
    PROVIDER,
    SMOKE_AUTHORITY_VERSION,
    SMOKE_AUTHORITY_VERSION_V0_2,
    SMOKE_RETEST_AUTHORITY_VERSION_V0_2,
    SMOKE_RETEST_AUTHORITY_VERSION_V0_3,
    SMOKE_STATUS_ACTIVE,
    SMOKE_STATUS_PENDING,
    SMOKE_STATUS_REVOKED,
    SPEND_PENDING,
    WAKE_POLICY,
    ProviderSmokeAuthority,
    PromptIdentitySet,
    SmokeWakeBinding,
    assert_smoke_authority_active,
    load_provider_smoke_authority,
)
from src.replay_v0_1_smoke_bridge import (
    HarnessOneShotBridge,
    SmokeBridgeResult,
    SmokeDeterministicTransport,
    SmokeHarnessTransport,
    _valid_mock_response,
)
from src.replay_v0_1_smoke_visual import (
    ACTIVE_SMOKE_TIMEFRAMES,
    render_wake_charts,
)
from src.replay_v0_1_smoke_guard import (
    EXECUTION_CRITICAL_PATHS,
    bind_runtime_identities_to_authority,
    positive_finite_decimal,
    validate_test_base_url,
    verify_execution_code_bound,
)
from src.persistent_deepseek_runtime import (
    CURRENT_MODEL,
    PINNED_HARNESS_COMMIT,
    PINNED_HARNESS_VERSION,
    PROJECT_TRANSPORT_PATCH,
)
from src.jianghe_trading_only_prompt import TRADING_ONLY_PROMPT_CONTRACT
from src.persistent_trader_store import PersistentTraderStore
from tests.replay_v0_1_synthetic_fixture import (
    ReplayV01RuntimeFixture,
    build_session_steps,
    build_slice,
    valid_response,
)

TZ = timezone.utc
WAIT = valid_response(action="WAIT", attention_mode="SCAN", direction="NONE")
REAL_DEEPSEEK_PROVIDER_CALLS = 0


def _day_start(day: date, hour: int = 9) -> datetime:
    return datetime.combine(day, time(hour), tzinfo=TZ)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _git_rev(repo_root: Path, rev: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", rev],
        capture_output=True, text=True, check=True,
    )
    return completed.stdout.strip()


def _three_wakes(*, logical: bool = True) -> tuple[tuple[str, SmokeWakeBinding], ...]:
    """Three distinct smoke wakes; two-identity (logical) or historical runtime-only."""
    wakes = []
    for index, name in enumerate(("call_1", "call_2", "call_3")):
        char = "abc"[index]
        wakes.append((
            name,
            SmokeWakeBinding(
                char * 64,
                _day_start(date(2024, 1, 22), 9 + index),
                logical_wake_selection_identity=("l" + char * 63) if logical else None,
            ),
        ))
    return tuple(wakes)


def _authority_payload(
    *,
    status: str,
    owner_payment_confirmation: bool,
    max_spend_cny: str,
    smoke_wakes: tuple[tuple[str, SmokeWakeBinding], ...],
    authority_version: str = SMOKE_AUTHORITY_VERSION_V0_2,
    cny_ceiling_mode: str = CNY_CEILING_MODE_NUMERIC,
    slice_identity: str = "slice-test",
    exact_slice_seal_identity: str = "seal-test",
    product: str = "cu",
    concrete_contract: str = "SHFE.cu2406",
    api_key_env: str = "DEEPSEEK_API_KEY",
    execution_code_commit: str = "TEST_COMMIT",
    context_policy_identity: str = "context-policy-test",
) -> dict:
    authority = ProviderSmokeAuthority(
        authority_version=authority_version,
        status=status,
        owner_payment_confirmation=owner_payment_confirmation,
        work_package="SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1",
        product=product,
        concrete_contract=concrete_contract,
        slice_identity=slice_identity,
        exact_slice_seal_identity=exact_slice_seal_identity,
        prior_history_days=tuple(date(2024, 1, 2) + __import__("datetime").timedelta(days=i) for i in range(20)),
        burn_in_days=(date(2024, 1, 22), date(2024, 1, 23)),
        measurement_days=tuple(date(2024, 1, 24) + __import__("datetime").timedelta(days=i) for i in range(20)),
        provider=PROVIDER,
        model=CURRENT_MODEL,
        harness_version=PINNED_HARNESS_VERSION,
        harness_commit=PINNED_HARNESS_COMMIT,
        project_transport_patch=PROJECT_TRANSPORT_PATCH,
        max_provider_calls=3,
        max_retries=0,
        images_per_call=4,
        wake_policy=WAKE_POLICY,
        restart_after_call=2,
        smoke_wakes=smoke_wakes,
        prompt_identities=PromptIdentitySet(
            prompt_contract_version=TRADING_ONLY_PROMPT_CONTRACT.version,
            prompt_contract_identity=TRADING_ONLY_PROMPT_CONTRACT.identity,
            system_prompt_sha256=TRADING_ONLY_PROMPT_CONTRACT.system_prompt_sha256,
            decision_prompt_sha256=TRADING_ONLY_PROMPT_CONTRACT.decision_prompt_sha256,
        ),
        context_policy_identity=context_policy_identity,
        renderer_identity=f"{RENDERER_VERSION}:{JiangheVisualRenderer().config.identity}",
        api_key_env=api_key_env,
        execution_code_commit=execution_code_commit,
        full_replay_authorized=False,
        full_replay_1998_calls_authorized=False,
        max_spend_cny=max_spend_cny,
        cny_ceiling_mode=cny_ceiling_mode,
        created_at=datetime(2026, 8, 26, 12, 0, 0, tzinfo=TZ),
    )
    return authority.to_payload()


def _write_authority(root: Path, payload: dict) -> Path:
    path = root / "authority.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return path


class ProviderSmokeAuthorityTests(unittest.TestCase):
    def test_pending_authority_loads_and_active_gate_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _authority_payload(
                status=SMOKE_STATUS_PENDING,
                owner_payment_confirmation=False,
                max_spend_cny=SPEND_PENDING,
                smoke_wakes=_three_wakes(),
            )
            path = _write_authority(root, payload)
            authority = load_provider_smoke_authority(path)
            self.assertEqual(authority.status, SMOKE_STATUS_PENDING)
            self.assertFalse(authority.owner_payment_confirmation)
            self.assertEqual(authority.identity, payload["authority_identity"])
            with self.assertRaises(ValueError):
                assert_smoke_authority_active(authority)

    def test_active_requires_payment_confirmation_and_concrete_spend(self) -> None:
        wakes = _three_wakes()
        with self.assertRaises(ValueError):
            ProviderSmokeAuthority(**{  # type: ignore[arg-type]
                "authority_version": "KPE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_V0_1",
                "status": SMOKE_STATUS_ACTIVE,
                "owner_payment_confirmation": False,
                "work_package": "SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1",
                "product": "cu", "concrete_contract": "SHFE.cu2406",
                "slice_identity": "s", "exact_slice_seal_identity": "e",
                "prior_history_days": tuple(date(2024, 1, 2) + __import__("datetime").timedelta(days=i) for i in range(20)),
                "burn_in_days": (date(2024, 1, 22), date(2024, 1, 23)),
                "measurement_days": tuple(date(2024, 1, 24) + __import__("datetime").timedelta(days=i) for i in range(20)),
                "provider": PROVIDER, "model": CURRENT_MODEL,
                "harness_version": PINNED_HARNESS_VERSION, "harness_commit": PINNED_HARNESS_COMMIT,
                "project_transport_patch": PROJECT_TRANSPORT_PATCH,
                "max_provider_calls": 3, "max_retries": 0, "images_per_call": 4,
                "wake_policy": WAKE_POLICY, "restart_after_call": 2,
                "smoke_wakes": wakes,
                "prompt_identities": PromptIdentitySet(
                    prompt_contract_version=TRADING_ONLY_PROMPT_CONTRACT.version,
                    prompt_contract_identity=TRADING_ONLY_PROMPT_CONTRACT.identity,
                    system_prompt_sha256=TRADING_ONLY_PROMPT_CONTRACT.system_prompt_sha256,
                    decision_prompt_sha256=TRADING_ONLY_PROMPT_CONTRACT.decision_prompt_sha256,
                ),
                "context_policy_identity": "c", "renderer_identity": "r",
                "api_key_env": "DEEPSEEK_API_KEY", "execution_code_commit": "t",
                "full_replay_authorized": False, "full_replay_1998_calls_authorized": False,
                "max_spend_cny": SPEND_PENDING,
                "created_at": datetime(2026, 8, 26, 12, 0, 0, tzinfo=TZ),
            })

    def test_loader_rejects_tampered_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _authority_payload(
                status=SMOKE_STATUS_PENDING, owner_payment_confirmation=False,
                max_spend_cny=SPEND_PENDING,
                smoke_wakes=_three_wakes(),
            )
            payload["images_per_call"] = 5  # tamper
            path = _write_authority(root, payload)
            with self.assertRaises(ValueError):
                load_provider_smoke_authority(path)

    def test_v0_2_authority_requires_both_wake_identities(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Start from a valid V0_2 two-identity payload, then drop the logical
            # identities so the loader must reject the runtime-only V0_2 slot.
            payload = _authority_payload(
                authority_version=SMOKE_AUTHORITY_VERSION_V0_2,
                status=SMOKE_STATUS_PENDING, owner_payment_confirmation=False,
                max_spend_cny=SPEND_PENDING,
                smoke_wakes=_three_wakes(),
            )
            for name in ("call_1", "call_2", "call_3"):
                payload["smoke_wakes"][name].pop("logical_wake_selection_identity")
            path = _write_authority(root, payload)
            with self.assertRaises(ValueError):
                load_provider_smoke_authority(path)

    def test_runtime_only_authority_cannot_be_pending_or_active(self) -> None:
        for status in (SMOKE_STATUS_PENDING, SMOKE_STATUS_ACTIVE):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                owner_confirmed = status == SMOKE_STATUS_ACTIVE
                payload = _authority_payload(
                    status=status,
                    owner_payment_confirmation=owner_confirmed,
                    max_spend_cny="1.00" if owner_confirmed else SPEND_PENDING,
                    smoke_wakes=_three_wakes(),
                )
                for name in ("call_1", "call_2", "call_3"):
                    payload["smoke_wakes"][name].pop("logical_wake_selection_identity")
                path = _write_authority(root, payload)
                with self.assertRaises(ValueError):
                    load_provider_smoke_authority(path)

    def test_historical_runtime_only_revoked_authority_remains_readable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _authority_payload(
                authority_version=SMOKE_AUTHORITY_VERSION,
                status=SMOKE_STATUS_REVOKED, owner_payment_confirmation=True,
                max_spend_cny="1.00",
                smoke_wakes=_three_wakes(logical=False),
            )
            path = _write_authority(root, payload)
            authority = load_provider_smoke_authority(path)
            self.assertEqual(authority.authority_version, SMOKE_AUTHORITY_VERSION)
            self.assertEqual(authority.status, SMOKE_STATUS_REVOKED)
            self.assertTrue(
                all(binding.logical_wake_selection_identity is None for _, binding in authority.smoke_wakes)
            )
            self.assertEqual(authority.identity, payload["authority_identity"])

    def test_bridge_construction_requires_active_authority_before_any_env_or_tsx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _authority_payload(
                status=SMOKE_STATUS_PENDING, owner_payment_confirmation=False,
                max_spend_cny=SPEND_PENDING,
                smoke_wakes=_three_wakes(),
            )
            authority = load_provider_smoke_authority(_write_authority(root, payload))
            # Missing harness root, missing tsx, unset env — none matter because the
            # ACTIVE gate raises first (fail closed before any credential/network step).
            with self.assertRaises(ValueError):
                HarnessOneShotBridge(
                    authority=authority,
                    harness_root=root / "missing-harness",
                    repo_root=root,
                )


class ProviderSmokeVisualTests(unittest.TestCase):
    def test_renders_exactly_four_deterministic_charts(self) -> None:
        renderer = JiangheVisualRenderer()
        day = date(2024, 1, 22)
        steps = build_session_steps(
            trading_day=day, session_identity="sess-vis", start=_day_start(day), count=3
        )
        first = steps[0]
        one = render_wake_charts(
            bars=first.context_bars, product="cu", concrete_contract="SHFE.cu2406",
            as_of=first.wake_bar.available_at, renderer=renderer,
        )
        two = render_wake_charts(
            bars=first.context_bars, product="cu", concrete_contract="SHFE.cu2406",
            as_of=first.wake_bar.available_at, renderer=renderer,
        )
        self.assertEqual(len(one.charts), 4)
        self.assertEqual(len(one.png_bytes), 4)
        self.assertEqual(len(one.artifacts), 4)
        self.assertEqual(tuple(chart.timeframe for chart in one.charts), ACTIVE_SMOKE_TIMEFRAMES)
        self.assertEqual(one.png_sha256s, two.png_sha256s)
        for chart, artifact, png_sha in zip(one.charts, one.artifacts, one.png_sha256s):
            self.assertEqual(chart.render_content_hash, png_sha)
            self.assertEqual(artifact.png_sha256, png_sha)
            self.assertEqual(len(chart.render_content_hash), 64)
        # No future bars: every rendered panel closes at or before the wake decision time.
        for artifact in one.artifacts:
            self.assertTrue(artifact.png_bytes.startswith(b"\x89PNG\r\n\x1a\n"))


class ProviderSmokeTransportTests(unittest.TestCase):
    def test_harness_transport_maps_one_wake_to_one_request_and_exhausts(self) -> None:
        def result(text: str, request_id: str | None) -> SmokeBridgeResult:
            return SmokeBridgeResult(
                status="OK", provider=PROVIDER, model=CURRENT_MODEL,
                raw_response_text=_valid_mock_response(), finish_reason="stop",
                token_usage={"inputTokens": 1, "outputTokens": 1}, provider_request_id=request_id,
                image_count=4, request_count=1,
            )

        class FakeBridge:
            def __init__(self) -> None:
                self.invocations: list[tuple[str, tuple[bytes, ...]]] = []
                self.calls = 0

            def execute(self, *, system_prompt, decision_prompt, context, png_images):
                self.invocations.append((system_prompt, png_images))
                self.calls += 1
                return result("ok", f"req-{self.calls}")

        bridge = FakeBridge()
        bundles = (
            (b"png-1a", b"png-1b", b"png-1c", b"png-1d"),
            (b"png-2a", b"png-2b", b"png-2c", b"png-2d"),
            (b"png-3a", b"png-3b", b"png-3c", b"png-3d"),
        )
        transport = SmokeHarnessTransport(bridge=bridge, image_bundles=bundles, expected_provider=PROVIDER, expected_model=CURRENT_MODEL)  # type: ignore[arg-type]
        self.assertTrue(transport.provider_admitted)
        self.assertFalse(transport.mock)
        for index, expected_bundle in enumerate(bundles, start=1):
            response = transport.execute(type("R", (), {"system_prompt": f"s{index}", "decision_prompt": "d", "context": {}})())
            self.assertEqual(response, _valid_mock_response())
            self.assertEqual(bridge.invocations[index - 1][1], expected_bundle)
        self.assertEqual(len(transport.calls), 3)
        with self.assertRaises(RuntimeError):
            transport.execute(type("R", (), {"system_prompt": "s4", "decision_prompt": "d", "context": {}})())


class ProviderSmokeRunnerGateTests(unittest.TestCase):
    def test_pending_authority_blocks_runner_before_any_network(self) -> None:
        runner = Path(__file__).resolve().parents[1] / "tools" / "run_replay_v0_1_provider_smoke.py"
        self.assertTrue(runner.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _authority_payload(
                status=SMOKE_STATUS_PENDING, owner_payment_confirmation=False,
                max_spend_cny=SPEND_PENDING,
                smoke_wakes=_three_wakes(),
            )
            authority_path = _write_authority(root, payload)
            state_dir = root / "state"
            output = root / "smoke.json"
            completed = subprocess.run(
                [
                    sys.executable, str(runner),
                    "--authority", str(authority_path),
                    "--state-dir", str(state_dir),
                    "--output", str(output),
                    "--transport", "mock",
                ],
                capture_output=True, text=True, cwd=str(root), timeout=120,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertFalse(state_dir.exists(), "runner must not create state before the authority gate")
            self.assertFalse(output.exists(), "runner must not write evidence before the authority gate")
            parsed = json.loads(completed.stdout)
            self.assertEqual(parsed["status"], "FAIL")
            self.assertEqual(parsed["provider_call_count"], 0)
            self.assertEqual(parsed["network_request_count"], 0)
            self.assertEqual(parsed["admitted_wake_count"], 0)
            self.assertEqual(parsed["authority_status"], SMOKE_STATUS_PENDING)
            self.assertFalse(parsed["owner_payment_confirmation"])


class ProviderSmokeThreeCallMockChainTests(unittest.TestCase):
    def test_three_call_mock_chain_with_restart_is_zero_cost_and_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp1:
            throwaway_root = Path(tmp1)
            fixture = ReplayV01RuntimeFixture(throwaway_root)
            slice_ = build_slice()
            replay_days = slice_.burn_in_days + slice_.measurement_days
            trading_day = replay_days[0]
            steps = build_session_steps(
                trading_day=trading_day, session_identity="sess-smoke",
                start=_day_start(trading_day), count=8,
            )
            smoke_steps = steps[:3]
            renderer = JiangheVisualRenderer()

            def build_orchestrator(root: Path, transport, fixture):
                return ReplayV01Orchestrator(
                    runtime_factory=fixture.make_runtime_factory(),
                    clock=ReplayClock(current_time=smoke_steps[0].wake_bar.open_time),
                    slice_=slice_, transport=transport,
                    state_dir=root / "state", renderer=renderer,
                )

            # Throwaway run: capture the exact wake identities the ledger will seal.
            throwaway = build_orchestrator(throwaway_root, SmokeDeterministicTransport(provider_admitted=True), fixture)
            try:
                throwaway.begin_session(
                    phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
                    session_identity="sess-smoke", steps=smoke_steps,
                )
                for step in smoke_steps:
                    throwaway.run_wake_step(step)
                throwaway.end_session()
                pre_bindings = throwaway.list_step_bindings()
            finally:
                throwaway.runtime.close()
            self.assertEqual(len(pre_bindings), 3)

            wakes = tuple(
                (
                    name,
                    SmokeWakeBinding(
                        binding.wake_identity,
                        binding.close_time,
                        logical_wake_selection_identity=binding.logical_wake_selection_identity,
                    ),
                )
                for name, binding in zip(("call_1", "call_2", "call_3"), pre_bindings)
            )
            with tempfile.TemporaryDirectory() as tmp2:
                root = Path(tmp2)
                fresh_fixture = ReplayV01RuntimeFixture(root)
                self.assertEqual(fresh_fixture.identity.identity, fixture.identity.identity)
                payload = _authority_payload(
                    status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
                    max_spend_cny="1.00", smoke_wakes=wakes,
                )
                authority = load_provider_smoke_authority(_write_authority(root, payload))
                assert_smoke_authority_active(authority)

                transport = SmokeDeterministicTransport(provider_admitted=True)
                orchestrator = build_orchestrator(root, transport, fresh_fixture)
                try:
                    orchestrator.begin_session(
                        phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
                        session_identity="sess-smoke", steps=smoke_steps,
                    )
                    restart_sealed = None
                    for index, step in enumerate(smoke_steps, start=1):
                        binding = orchestrator.run_wake_step(step)
                        if index == 2:
                            restart_sealed = orchestrator.restart()
                    orchestrator.end_session()
                    bindings = orchestrator.list_step_bindings()
                    result = orchestrator.finalize()
                finally:
                    orchestrator.runtime.close()

                self.assertEqual(len(bindings), 3)
                self.assertEqual(len(transport.calls), 3)
                self.assertEqual(result.request_count, 3)
                for name, binding, expected in zip(("call_1", "call_2", "call_3"), bindings, authority.smoke_wakes):
                    self.assertEqual(binding.wake_identity, expected[1].wake_identity)
                self.assertIsNotNone(restart_sealed)
                # A fourth wake must be impossible: the ledger schedule has only 3 closes.
                rerun_transport = SmokeDeterministicTransport(provider_admitted=True)
                rerun = build_orchestrator(root / "rerun", rerun_transport, fresh_fixture)
                rerun.begin_session(
                    phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
                    session_identity="sess-smoke", steps=smoke_steps,
                )
                try:
                    with self.assertRaises(ValueError):
                        rerun.run_wake_step(steps[3])
                finally:
                    rerun.runtime.close()
    def test_provider_metadata_retained_and_execution_stops_on_rejection(self) -> None:
        """A schema rejection must retain provider usage metadata and stop immediately."""
        with tempfile.TemporaryDirectory() as tmp1:
            throwaway_root = Path(tmp1)
            fixture = ReplayV01RuntimeFixture(throwaway_root)
            slice_ = build_slice()
            replay_days = slice_.burn_in_days + slice_.measurement_days
            trading_day = replay_days[0]
            steps = build_session_steps(
                trading_day=trading_day, session_identity="sess-smoke",
                start=_day_start(trading_day), count=8,
            )
            smoke_steps = steps[:3]
            renderer = JiangheVisualRenderer()

            bad_response = json.dumps({
                "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_2",
                "family": "NONE",
                "action": "WAIT",
                "direction": "NONE",
                "attention_mode": "SCAN",
                "decision_state": "no_active_setup",
                "rationale": "test",
                "declared_unknown": [],
                "principle_references": [],
                "source_references": [],
                "numeric_claims": {"latest_5m_close": 76780},  # object shape -> rejected
                "current_market_hypothesis": None,
                "timeframe_trend_view": [],
                "key_location_hypotheses": [],
                "expected_trigger": None,
                "invalidation_hypothesis": None,
                "open_questions": [],
            })

            class BadBridge:
                def execute(self, *, system_prompt, decision_prompt, context, png_images):
                    return SmokeBridgeResult(
                        status="OK", provider=PROVIDER, model=CURRENT_MODEL,
                        raw_response_text=bad_response, finish_reason="stop",
                        token_usage={"inputTokens": 5, "outputTokens": 3},
                        provider_request_id="prov-req-1", image_count=4, request_count=1, error=None,
                    )

            bundles = (
                (b"p", b"p", b"p", b"p"),
                (b"p", b"p", b"p", b"p"),
                (b"p", b"p", b"p", b"p"),
            )
            transport = SmokeHarnessTransport(
                bridge=BadBridge(), image_bundles=bundles,
                expected_provider=PROVIDER, expected_model=CURRENT_MODEL,
            )

            with tempfile.TemporaryDirectory() as tmp2:
                root = Path(tmp2)
                fresh_fixture = ReplayV01RuntimeFixture(root)
                orchestrator = ReplayV01Orchestrator(
                    runtime_factory=fresh_fixture.make_runtime_factory(),
                    clock=ReplayClock(current_time=smoke_steps[0].wake_bar.open_time),
                    slice_=slice_, transport=transport, state_dir=root / "state", renderer=renderer,
                )
                try:
                    orchestrator.begin_session(
                        phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
                        session_identity="sess-smoke", steps=smoke_steps,
                    )
                    # Immediate stop: the rejection raises and no second wake is driven.
                    with self.assertRaises(ValueError):
                        orchestrator.run_wake_step(smoke_steps[0])
                    self.assertEqual(len(transport.calls), 1)
                    self.assertEqual(len(orchestrator.list_step_bindings()), 0)
                    events = orchestrator.runtime.store.list_audit()
                    kinds = [event.event_kind for event in events]
                    self.assertIn("MODEL_PROVIDER_RESPONSE_METADATA", kinds)
                    self.assertIn("MODEL_RESPONSE_RAW", kinds)
                    self.assertIn("MODEL_RESPONSE_REJECTED", kinds)
                    self.assertNotIn("MODEL_RESPONSE_NORMALIZED", kinds)
                    metadata = next(
                        event for event in events
                        if event.event_kind == "MODEL_PROVIDER_RESPONSE_METADATA"
                    )
                    self.assertEqual(metadata.payload["token_usage"], {"inputTokens": 5, "outputTokens": 3})
                    self.assertEqual(metadata.payload["provider_request_id"], "prov-req-1")
                    self.assertEqual(metadata.payload["model"], CURRENT_MODEL)
                    self.assertEqual(metadata.payload["provider"], PROVIDER)
                    rejected = next(
                        event for event in events
                        if event.event_kind == "MODEL_RESPONSE_REJECTED"
                    )
                    self.assertIn("numeric_claims", str(rejected.payload.get("error")))
                finally:
                    orchestrator.runtime.close()

class ProviderSmokeGuardTests(unittest.TestCase):
    def test_execution_code_bound_passes_at_clean_head(self) -> None:
        head = _git_rev(REPO_ROOT, "HEAD")
        # With a clean worktree at HEAD, every execution-critical path must match
        # the pinned commit (CRLF-normalized). Raises otherwise (fail closed).
        verify_execution_code_bound(repo_root=REPO_ROOT, execution_code_commit=head)

    def test_execution_code_bound_fails_when_path_missing_at_commit(self) -> None:
        # Hermetic: a tiny temp repo where the critical path is not tracked at
        # HEAD must fail closed (no dependence on checkout history depth).
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "tracked.txt").write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "add", "."],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed"],
                check=True,
            )
            head = _git_rev(repo, "HEAD")
            with self.assertRaises(ValueError):
                verify_execution_code_bound(
                    repo_root=repo, execution_code_commit=head,
                    critical_paths=("missing.py",),
                )

    def test_execution_code_bound_covers_and_detects_drift_in_attempt_ledger_module(self) -> None:
        # The new provider-attempt ledger is on the real execution path, so it
        # must be inside the machine authority's code-binding surface and drift
        # must be detected.
        self.assertIn("src/replay_v0_1_provider_attempt_ledger.py", EXECUTION_CRITICAL_PATHS)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            critical = repo / "src" / "replay_v0_1_provider_attempt_ledger.py"
            critical.parent.mkdir(parents=True)
            critical.write_text("content-a\n", encoding="utf-8")
            (repo / "tracked.txt").write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
            subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "add", "."],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed"],
                check=True,
            )
            head = _git_rev(repo, "HEAD")
            # Drift the working tree of the execution-critical module.
            critical.write_text("content-b\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                verify_execution_code_bound(
                    repo_root=repo, execution_code_commit=head,
                    critical_paths=("src/replay_v0_1_provider_attempt_ledger.py",),
                )

    def test_execution_code_bound_rejects_bogus_commit(self) -> None:
        with self.assertRaises(ValueError):
            verify_execution_code_bound(
                repo_root=REPO_ROOT, execution_code_commit="0" * 40,
                critical_paths=EXECUTION_CRITICAL_PATHS,
            )

    def test_bind_runtime_identities_binds_live_authority(self) -> None:
        # Use a synthetic ACTIVE authority built from the LIVE prompt contract so
        # the mechanical identity binding is exercised against the current
        # prompt/context/renderer/credential identities (independent of the
        # terminal old-slot machine authority).
        context_policy = "98262c9ab0614b4145fe56cb8746a44d754d03a38a25584aba810991cd666371"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _authority_payload(
                status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
                max_spend_cny="3.00",
                context_policy_identity=context_policy,
                smoke_wakes=_three_wakes(),
            )
            authority = load_provider_smoke_authority(_write_authority(root, payload))
            renderer = JiangheVisualRenderer()
            bind_runtime_identities_to_authority(
                authority=authority,
                prompt_contract=TRADING_ONLY_PROMPT_CONTRACT,
                context_policy_identity=context_policy,
                renderer_identity=f"{RENDERER_VERSION}:{renderer.config.identity}",
                api_key_env="DEEPSEEK_API_KEY",
            )
            with self.assertRaises(ValueError):
                bind_runtime_identities_to_authority(
                    authority=authority,
                    prompt_contract=TRADING_ONLY_PROMPT_CONTRACT,
                    context_policy_identity="wrong-context-policy",
                    renderer_identity=f"{RENDERER_VERSION}:{renderer.config.identity}",
                    api_key_env="DEEPSEEK_API_KEY",
                )
            with self.assertRaises(ValueError):
                bind_runtime_identities_to_authority(
                    authority=authority,
                    prompt_contract=TRADING_ONLY_PROMPT_CONTRACT,
                    context_policy_identity=context_policy,
                    renderer_identity=f"{RENDERER_VERSION}:{renderer.config.identity}",
                    api_key_env="OPENAI_API_KEY",
                )

    def test_positive_finite_decimal(self) -> None:
        self.assertEqual(positive_finite_decimal("1.50", "x"), Decimal("1.50"))
        self.assertEqual(positive_finite_decimal("0.01", "x"), Decimal("0.01"))
        for bad in ("PENDING_OWNER_CONFIRMATION", "abc", "0", "-1", "NaN", "Infinity", ""):
            with self.assertRaises(ValueError):
                positive_finite_decimal(bad, "max_spend_cny")

    def test_active_max_spend_cny_must_be_positive_finite_decimal(self) -> None:
        for bad in (SPEND_PENDING, "abc", "0", "-5", "NaN"):
            with tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(ValueError):
                    payload = _authority_payload(
                        status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
                        max_spend_cny=bad,
                        smoke_wakes=_three_wakes(),
                    )
                    load_provider_smoke_authority(_write_authority(Path(tmp), payload))

    def test_test_base_url_is_loopback_only_and_gated(self) -> None:
        self.assertIsNone(validate_test_base_url(None, allow_test=False))
        with self.assertRaises(ValueError):
            validate_test_base_url("http://127.0.0.1:8000", allow_test=False)
        with self.assertRaises(ValueError):
            validate_test_base_url("https://api.deepseek.com/v1", allow_test=True)
        self.assertEqual(validate_test_base_url("http://127.0.0.1:56533", allow_test=True), "http://127.0.0.1:56533")
        self.assertEqual(validate_test_base_url("http://localhost:8000", allow_test=True), "http://localhost:8000")

    def test_harness_transport_fails_closed_on_bad_bridge_result(self) -> None:
        def result(status="OK", provider=PROVIDER, model=CURRENT_MODEL, image_count=4, request_count=1, error=None):
            return SmokeBridgeResult(
                status=status, provider=provider, model=model,
                raw_response_text=_valid_mock_response(), finish_reason="stop",
                token_usage={}, provider_request_id=None,
                image_count=image_count, request_count=request_count, error=error,
            )

        class ScriptedBridge:
            def __init__(self, entries) -> None:
                self._entries = list(entries)
                self.calls = 0

            def execute(self, **kwargs):
                self.calls += 1
                entry = self._entries.pop(0)
                return entry() if callable(entry) else entry

        bundles = ((b"p", b"p", b"p", b"p"), (b"p", b"p", b"p", b"p"), (b"p", b"p", b"p", b"p"))
        for bad in (
            lambda: result(provider="other-provider"),
            lambda: result(model="other-model"),
            lambda: result(image_count=3),
            lambda: result(request_count=2),
            lambda: result(status="ERROR", error="boom"),
        ):
            bridge = ScriptedBridge([bad])
            transport = SmokeHarnessTransport(
                bridge=bridge, image_bundles=bundles,
                expected_provider=PROVIDER, expected_model=CURRENT_MODEL,
            )
            with self.assertRaises(RuntimeError):
                transport.execute(type("R", (), {"system_prompt": "s", "decision_prompt": "d", "context": {}})())


class ProviderSmokeRunnerWakeBindingVerificationTests(unittest.TestCase):
    """F-01 regression: the runner must verify BOTH the stable logical
    wake-selection identity and the runtime wake identity independently, and
    PASS/fail evidence must retain both identities."""

    def _runner_module(self):
        path = REPO_ROOT / "tools" / "run_replay_v0_1_provider_smoke.py"
        spec = importlib.util.spec_from_file_location("kpe_smoke_runner_mod", path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def _preflight_module(self):
        path = REPO_ROOT / "tools" / "preflight_replay_v0_1_provider_smoke.py"
        spec = importlib.util.spec_from_file_location("kpe_preflight_mod", path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def _load_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = _authority_payload(
                status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
                max_spend_cny="3.00",
                smoke_wakes=_three_wakes(),
            )
            return load_provider_smoke_authority(_write_authority(Path(tmp), payload))

    def _exact_bindings(self):
        """Bindings matching ``_three_wakes()`` exactly (logical + runtime)."""
        class _Binding:
            def __init__(self, wake_identity, logical, sequence=0):
                self.wake_identity = wake_identity
                self.logical_wake_selection_identity = logical
                self.close_time = datetime(2024, 1, 22, 9, 0, tzinfo=TZ)
                self.sequence = sequence
                self.observation_identity = f"obs-{sequence}"
                self.request_id = f"req-{sequence}"
                self.decision_identity = f"dec-{sequence}"
        return [
            _Binding("a" * 64, "l" + "a" * 63, 0),
            _Binding("b" * 64, "l" + "b" * 63, 1),
            _Binding("c" * 64, "l" + "c" * 63, 2),
        ]

    def test_verify_accepts_exact_logical_and_runtime_match(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        module._verify_smoke_wake_bindings(authority, self._exact_bindings())

    def test_verify_rejects_reordered_wakes(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        with self.assertRaises(ValueError):
            module._verify_smoke_wake_bindings(authority, list(reversed(self._exact_bindings())))

    def test_verify_rejects_runtime_tamper_while_logical_correct(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        bindings = self._exact_bindings()
        bindings[1].wake_identity = "d" * 64  # runtime tamper, logical stays correct
        with self.assertRaisesRegex(ValueError, "runtime wake identity mismatch"):
            module._verify_smoke_wake_bindings(authority, bindings)

    def test_verify_rejects_logical_only_tamper_while_runtime_correct(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        bindings = self._exact_bindings()
        bindings[1].logical_wake_selection_identity = "l" + "d" * 63  # logical tamper only
        with self.assertRaisesRegex(ValueError, "logical wake-selection identity mismatch"):
            module._verify_smoke_wake_bindings(authority, bindings)

    def test_verify_rejects_swapped_logical_identities_between_slots(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        bindings = self._exact_bindings()
        bindings[0].logical_wake_selection_identity, bindings[2].logical_wake_selection_identity = (
            bindings[2].logical_wake_selection_identity,
            bindings[0].logical_wake_selection_identity,
        )
        with self.assertRaisesRegex(ValueError, "logical wake-selection identity mismatch"):
            module._verify_smoke_wake_bindings(authority, bindings)

    def test_verify_rejects_wrong_logical_identity_with_same_close_time(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        bindings = self._exact_bindings()
        # Preserve close_time (and runtime identity) but change the logical id.
        bindings[2].logical_wake_selection_identity = "x" * 64
        with self.assertRaisesRegex(ValueError, "logical wake-selection identity mismatch"):
            module._verify_smoke_wake_bindings(authority, bindings)

    def test_verify_rejects_wrong_binding_count(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        with self.assertRaises(ValueError):
            module._verify_smoke_wake_bindings(authority, self._exact_bindings()[:2])

    def test_assert_wake_pair_requires_two_identity_authority(self) -> None:
        module = self._runner_module()
        expected = SmokeWakeBinding("a" * 64, _day_start(date(2024, 1, 22)), logical_wake_selection_identity=None)
        with self.assertRaisesRegex(ValueError, "no logical_wake_selection_identity"):
            module._assert_wake_pair_matches("call_1", "l" + "a" * 63, "a" * 64, expected)

    def test_pre_call_guard_passes_on_match(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        guard = module._build_wake_guard(authority)

        class _Wake:
            def __init__(self, seq, logical, runtime):
                self.sequence = seq
                self.logical_wake_selection_identity = logical
                self.wake_identity = runtime
        guard(_Wake(0, "l" + "a" * 63, "a" * 64), 0)
        guard(_Wake(1, "l" + "b" * 63, "b" * 64), 1)
        guard(_Wake(2, "l" + "c" * 63, "c" * 64), 2)

    def test_pre_call_guard_rejects_logical_only_tamper_before_call(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        guard = module._build_wake_guard(authority)

        class _Wake:
            def __init__(self, seq, logical, runtime):
                self.sequence = seq
                self.logical_wake_selection_identity = logical
                self.wake_identity = runtime
        with self.assertRaisesRegex(ValueError, "logical wake-selection identity mismatch"):
            guard(_Wake(0, "l" + "d" * 63, "a" * 64), 0)

    def test_pre_call_guard_rejects_runtime_only_tamper_before_call(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        guard = module._build_wake_guard(authority)

        class _Wake:
            def __init__(self, seq, logical, runtime):
                self.sequence = seq
                self.logical_wake_selection_identity = logical
                self.wake_identity = runtime
        with self.assertRaisesRegex(ValueError, "runtime wake identity mismatch"):
            guard(_Wake(1, "l" + "b" * 63, "d" * 64), 1)

    def test_pre_call_guard_rejects_unknown_sequence(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        guard = module._build_wake_guard(authority)

        class _Wake:
            sequence = 3
            logical_wake_selection_identity = "l" + "a" * 63
            wake_identity = "a" * 64
        with self.assertRaisesRegex(ValueError, "no sealed wake"):
            guard(_Wake(), 3)

    def test_preflight_blueprint_carries_both_identities_from_actual_bindings(self) -> None:
        module = self._preflight_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = ReplayV01RuntimeFixture(root)
            slice_ = build_slice()
            replay_days = slice_.burn_in_days + slice_.measurement_days
            trading_day = replay_days[0]
            steps = build_session_steps(
                trading_day=trading_day, session_identity="sess-pre",
                start=_day_start(trading_day), count=3,
            )
            renderer = JiangheVisualRenderer()
            transport = SmokeDeterministicTransport(provider_admitted=True)
            orchestrator = ReplayV01Orchestrator(
                runtime_factory=fixture.make_runtime_factory(),
                clock=ReplayClock(current_time=steps[0].wake_bar.open_time),
                slice_=slice_, transport=transport, state_dir=root / "state", renderer=renderer,
            )
            try:
                orchestrator.begin_session(
                    phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
                    session_identity="sess-pre", steps=steps,
                )
                rendered = []
                for step in steps:
                    rendered.append(render_wake_charts(
                        bars=step.context_bars, product=slice_.product,
                        concrete_contract=slice_.concrete_contract,
                        as_of=step.wake_bar.available_at, renderer=renderer,
                    ))
                    orchestrator.run_wake_step(step)
                orchestrator.end_session()
                bindings = orchestrator.list_step_bindings()
            finally:
                orchestrator.runtime.close()
            blueprint = module._build_smoke_wakes_blueprint(bindings, rendered)
            for name, binding in zip(("call_1", "call_2", "call_3"), bindings):
                item = blueprint[name]
                self.assertEqual(item["wake_identity"], binding.wake_identity)
                self.assertEqual(
                    item["logical_wake_selection_identity"],
                    binding.logical_wake_selection_identity,
                )
                self.assertIn("close_time", item)
                self.assertTrue(item["logical_wake_selection_identity"])

    def test_pass_call_evidence_retains_both_identities(self) -> None:
        module = self._runner_module()
        bindings = self._exact_bindings()
        for index, (name, binding) in enumerate(zip(("call_1", "call_2", "call_3"), bindings)):
            rendered = type("R", (), {"png_sha256s": ("s" + str(index),), "artifacts": ()})()
            evidence = module._build_call_evidence(
                name, binding, rendered, "stop", None, {}
            )
            self.assertEqual(evidence["wake_identity"], binding.wake_identity)
            self.assertEqual(
                evidence["logical_wake_selection_identity"],
                binding.logical_wake_selection_identity,
            )
            self.assertEqual(evidence["call"], name)

    def test_fail_closed_evidence_after_admitted_wake_retains_both_identities(self) -> None:
        module = self._runner_module()
        bindings = self._exact_bindings()[:2]  # two wakes admitted before failure
        evidence = module._build_admitted_wake_evidence(bindings)
        self.assertEqual(len(evidence), 2)
        for name, binding, item in zip(("call_1", "call_2"), bindings, evidence):
            self.assertEqual(item["call"], name)
            self.assertEqual(item["wake_identity"], binding.wake_identity)
            self.assertEqual(
                item["logical_wake_selection_identity"],
                binding.logical_wake_selection_identity,
            )


def _malformed_response() -> str:
    """A V0_2 strict-schema response with object-shaped numeric_claims -> rejected."""
    return json.dumps({
        "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_2",
        "family": "NONE",
        "action": "WAIT",
        "direction": "NONE",
        "attention_mode": "SCAN",
        "decision_state": "malformed",
        "rationale": "malformed response for F-02 regression",
        "declared_unknown": [],
        "principle_references": [],
        "source_references": [],
        "numeric_claims": {"latest_5m_close": 76780},  # object shape -> rejected
        "current_market_hypothesis": None,
        "timeframe_trend_view": [],
        "key_location_hypotheses": [],
        "expected_trigger": None,
        "invalidation_hypothesis": None,
        "open_questions": [],
    }, ensure_ascii=False)


class ProviderSmokeFailClosedEvidenceTests(unittest.TestCase):
    """F-02: terminal fail-closed evidence must prove EVERY actually
    admitted/request-bound wake, including the wake whose provider response
    failed normalization AFTER the transport was invoked (no completed
    ReplayStepBinding exists for it)."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.state_dir = self.root / "state"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _runner_module(self):
        path = REPO_ROOT / "tools" / "run_replay_v0_1_provider_smoke.py"
        spec = importlib.util.spec_from_file_location("kpe_smoke_runner_mod2", path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def _load_authority(self):
        payload = _authority_payload(
            status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
            max_spend_cny="3.00",
            smoke_wakes=_three_wakes(),
        )
        with tempfile.TemporaryDirectory() as tmp:
            return load_provider_smoke_authority(_write_authority(Path(tmp), payload))

    def _run_until_failure(self, responses: list[str]) -> dict:
        """Drive the real orchestrator until a response fails; return context.

        Exercises the REAL failure window: wake registration -> pre-call guard ->
        request binding (durably persisted) -> transport invocation -> malformed
        response -> normalization failure -> durable request-bound wakes.
        """
        fixture = ReplayV01RuntimeFixture(self.root)
        slice_ = build_slice()
        replay_days = slice_.burn_in_days + slice_.measurement_days
        trading_day = replay_days[0]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="sess-f02",
            start=_day_start(trading_day), count=3,
        )
        transport = SyntheticScriptedTransport(responses)
        orchestrator = ReplayV01Orchestrator(
            runtime_factory=fixture.make_runtime_factory(),
            clock=ReplayClock(current_time=steps[0].wake_bar.open_time),
            slice_=slice_, transport=transport, state_dir=self.state_dir,
        )
        try:
            orchestrator.begin_session(
                phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
                session_identity="sess-f02", steps=steps,
            )
            bindings: list = []
            failure: Exception | None = None
            for step in steps:
                try:
                    orchestrator.run_wake_step(step)
                except Exception as exc:  # normalization/recording failure
                    failure = exc
                    break
                bindings = list(orchestrator.list_step_bindings())
            return {
                "root": self.root,
                "state_dir": self.state_dir,
                "fixture": fixture,
                "transport": transport,
                "bindings": bindings,
                "failure": failure,
                "trader_identity": fixture.identity.identity,
            }
        finally:
            orchestrator.runtime.close()

    def test_first_call_post_transport_normalization_failure(self) -> None:
        module = self._runner_module()
        ctx = self._run_until_failure([_malformed_response()])
        self.assertIsInstance(ctx["failure"], ValueError)
        # Fake transport invoked exactly once; no second call.
        self.assertEqual(len(ctx["transport"].calls), 1)
        ledger = WakeLedgerArchive(wake_ledger_path_for(ctx["state_dir"]))
        bound = ledger.bound_wakes()
        self.assertEqual(len(bound), 1)
        wake = bound[0]
        self.assertEqual(wake.sequence, 0)
        self.assertTrue(wake.request_id)
        self.assertEqual(wake.retry_count, 0)
        # No unadmitted/future wake was fabricated.
        self.assertEqual(len(ledger.all_wakes()), 1)
        # Evidence helper: exact call_1 identity pair + request identity, no decision identity.
        evidence = module._build_bound_wake_evidence(bound, ctx["bindings"])
        self.assertEqual(len(evidence), 1)
        record = evidence[0]
        self.assertEqual(record["call"], "call_1")
        self.assertEqual(record["sequence"], 0)
        self.assertEqual(record["wake_identity"], wake.wake_identity)
        self.assertEqual(
            record["logical_wake_selection_identity"],
            wake.logical_wake_selection_identity,
        )
        self.assertEqual(record["request_id"], wake.request_id)
        self.assertEqual(record["retry_count"], 0)
        self.assertNotIn("decision_identity", record)
        # Full fail-closed terminal evidence.
        authority = self._load_authority()
        payload = module._assemble_fail_evidence(
            authority=authority,
            state_dir=ctx["state_dir"],
            transport=ctx["transport"],
            bindings=ctx["bindings"],
            transport_name="mock",
            error=ctx["failure"],
            trader_identity=ctx["trader_identity"],
        )
        self.assertEqual(payload["provider_call_count"], 1)
        self.assertEqual(payload["network_request_count"], 1)
        self.assertEqual(payload["admitted_wake_count"], 1)
        self.assertEqual(payload["request_count"], 1)
        self.assertEqual(payload["retry_count"], 0)
        self.assertEqual(len(payload["admitted_wakes"]), 1)
        self.assertEqual(payload["admitted_wakes"][0]["call"], "call_1")
        self.assertEqual(payload["admitted_wakes"][0]["wake_identity"], wake.wake_identity)
        self.assertEqual(
            payload["admitted_wakes"][0]["logical_wake_selection_identity"],
            wake.logical_wake_selection_identity,
        )
        self.assertNotIn("decision_identity", payload["admitted_wakes"][0])

    def test_later_call_post_transport_normalization_failure(self) -> None:
        module = self._runner_module()
        ctx = self._run_until_failure([valid_response(), _malformed_response()])
        self.assertIsInstance(ctx["failure"], ValueError)
        # call_1 succeeded; call_2 provider request occurred then failed normalization.
        self.assertEqual(len(ctx["transport"].calls), 2)
        ledger = WakeLedgerArchive(wake_ledger_path_for(ctx["state_dir"]))
        bound = ledger.bound_wakes()
        self.assertEqual(len(bound), 2)
        call1, call2 = bound
        self.assertEqual(call1.sequence, 0)
        self.assertEqual(call2.sequence, 1)
        self.assertTrue(call1.request_id)
        self.assertTrue(call2.request_id)
        self.assertEqual(call1.retry_count, 0)
        self.assertEqual(call2.retry_count, 0)
        # call_1 has a completed decision; call_2 must NOT fabricate one.
        evidence = module._build_bound_wake_evidence(bound, ctx["bindings"])
        self.assertEqual(len(evidence), 2)
        self.assertEqual(evidence[0]["call"], "call_1")
        self.assertEqual(evidence[1]["call"], "call_2")
        self.assertIn("decision_identity", evidence[0])
        self.assertNotIn("decision_identity", evidence[1])
        self.assertEqual(evidence[1]["wake_identity"], call2.wake_identity)
        self.assertEqual(
            evidence[1]["logical_wake_selection_identity"],
            call2.logical_wake_selection_identity,
        )
        # No call_3.
        self.assertEqual(len(ctx["transport"].calls), 2)
        # Full fail-closed terminal evidence.
        authority = self._load_authority()
        payload = module._assemble_fail_evidence(
            authority=authority,
            state_dir=ctx["state_dir"],
            transport=ctx["transport"],
            bindings=ctx["bindings"],
            transport_name="mock",
            error=ctx["failure"],
            trader_identity=ctx["trader_identity"],
        )
        self.assertEqual(payload["provider_call_count"], 2)
        self.assertEqual(payload["admitted_wake_count"], 2)
        self.assertEqual(len(payload["admitted_wakes"]), 2)
        self.assertIn("decision_identity", payload["admitted_wakes"][0])
        self.assertNotIn("decision_identity", payload["admitted_wakes"][1])
        self.assertEqual(payload["admitted_wakes"][1]["call"], "call_2")

    def test_bound_wakes_survive_restart_model(self) -> None:
        # The durable request-bound ledger is a file; reopening it after the
        # runtime is closed (restart/persistence model) yields the same wakes.
        ctx = self._run_until_failure([valid_response(), _malformed_response()])
        first = WakeLedgerArchive(wake_ledger_path_for(ctx["state_dir"])).bound_wakes()
        reopened = WakeLedgerArchive(wake_ledger_path_for(ctx["state_dir"])).bound_wakes()
        self.assertEqual(len(first), 2)
        self.assertEqual(
            [wake.wake_identity for wake in first],
            [wake.wake_identity for wake in reopened],
        )
        self.assertEqual(
            [wake.logical_wake_selection_identity for wake in first],
            [wake.logical_wake_selection_identity for wake in reopened],
        )


def _attempt_identities() -> tuple[dict, ...]:
    """Three attempt identities matching ``_three_wakes()``."""
    return tuple(
        {
            "sequence": index,
            "call": name,
            "logical_wake_selection_identity": "l" + char * 63,
            "wake_identity": char * 64,
            "close_time": _day_start(date(2024, 1, 22), 9 + index).isoformat(),
        }
        for index, (name, char) in enumerate(
            zip(("call_1", "call_2", "call_3"), "abc")
        )
    )


def _fake_request(request_id: str = "req-1"):
    return type("R", (), {
        "request_id": request_id,
        "system_prompt": "system",
        "decision_prompt": "decision",
        "context": {},
    })()


def _valid_bridge_result(**kwargs) -> SmokeBridgeResult:
    return SmokeBridgeResult(
        status="OK", provider=PROVIDER, model=CURRENT_MODEL,
        raw_response_text=_valid_mock_response(), finish_reason="stop",
        token_usage={"inputTokens": 5, "outputTokens": 3},
        provider_request_id="prov-req-1", image_count=4, request_count=1, error=None,
    )


def _canonical_identity(payload: dict) -> str:
    without = dict(payload)
    without.pop("authority_identity", None)
    return sha256(json.dumps(
        without, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _raw_authority_payload(**overrides) -> dict:
    """Build a raw authority JSON payload from a valid base with overrides.

    Used to author intentionally INVALID authorities whose loader rejection is
    the thing under test (the dataclass constructor cannot build them).
    """
    base = _authority_payload(
        status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
        max_spend_cny="3.00", smoke_wakes=_three_wakes(),
    )
    payload = dict(base)
    payload.update(overrides)
    payload["authority_identity"] = _canonical_identity(payload)
    return payload


class _ScriptedBridge:
    """Fake one-shot bridge; records launches and can raise / return per script."""

    def __init__(self, behavior) -> None:
        self._behavior = behavior
        self.launches = 0

    def execute(self, **kwargs):
        self.launches += 1
        if isinstance(self._behavior, Exception):
            raise self._behavior
        return self._behavior(**kwargs)


class ProviderAttemptLedgerTests(unittest.TestCase):
    """Durable provider-attempt ledger state machine."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.ledger = ProviderAttemptLedger(
            provider_attempt_ledger_path_for(self.root / "state"),
            authority_identity="auth-1",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_attempt_started_persisted_before_any_result(self) -> None:
        attempt = self.ledger.record_attempt_started(
            sequence=0, call="call_1",
            logical_wake_selection_identity="l" + "a" * 63,
            wake_identity="a" * 64, close_time=_day_start(date(2024, 1, 22)),
            request_id="req-1", retry_count=0,
        )
        self.assertEqual(attempt.attempt_state, ATTEMPT_STARTED)
        # Reopen -> durable.
        reopened = ProviderAttemptLedger(
            provider_attempt_ledger_path_for(self.root / "state"),
            authority_identity="auth-1",
        )
        self.assertEqual(reopened.attempts()[0].attempt_state, ATTEMPT_STARTED)
        self.assertEqual(reopened.attempts()[0].request_id, "req-1")

    def test_valid_transition_to_result_received(self) -> None:
        self.ledger.record_attempt_started(
            sequence=0, call="call_1",
            logical_wake_selection_identity="l" + "a" * 63,
            wake_identity="a" * 64, close_time=_day_start(date(2024, 1, 22)),
            request_id="req-1",
        )
        attempt = self.ledger.record_result_received(sequence=0, metadata={"provider": "deepseek"})
        self.assertEqual(attempt.attempt_state, RESULT_RECEIVED)
        self.assertEqual(attempt.result_metadata, (("provider", "deepseek"),))

    def test_transition_to_unknown_after_attempt_start(self) -> None:
        self.ledger.record_attempt_started(
            sequence=0, call="call_1",
            logical_wake_selection_identity="l" + "a" * 63,
            wake_identity="a" * 64, close_time=_day_start(date(2024, 1, 22)),
            request_id="req-1",
        )
        attempt = self.ledger.record_unknown_after_attempt_start(sequence=0, reason="timeout")
        self.assertEqual(attempt.attempt_state, UNKNOWN_AFTER_ATTEMPT_START)
        self.assertEqual(attempt.reason, "timeout")
        self.assertEqual(self.ledger.unknown_after_attempt_start_count(), 1)
        self.assertEqual(self.ledger.result_received_count(), 0)

    def test_terminal_state_cannot_transition(self) -> None:
        self.ledger.record_attempt_started(
            sequence=0, call="call_1",
            logical_wake_selection_identity="l" + "a" * 63,
            wake_identity="a" * 64, close_time=_day_start(date(2024, 1, 22)),
            request_id="req-1",
        )
        self.ledger.record_result_received(sequence=0, metadata={})
        with self.assertRaises(ValueError):
            self.ledger.record_unknown_after_attempt_start(sequence=0, reason="late")
        with self.assertRaises(ValueError):
            self.ledger.record_result_received(sequence=0, metadata={})

    def test_unknown_cannot_transition_to_result(self) -> None:
        self.ledger.record_attempt_started(
            sequence=0, call="call_1",
            logical_wake_selection_identity="l" + "a" * 63,
            wake_identity="a" * 64, close_time=_day_start(date(2024, 1, 22)),
            request_id="req-1",
        )
        self.ledger.record_unknown_after_attempt_start(sequence=0, reason="no-result")
        with self.assertRaises(ValueError):
            self.ledger.record_result_received(sequence=0, metadata={})

    def test_retry_count_must_be_zero(self) -> None:
        with self.assertRaises(ValueError):
            self.ledger.record_attempt_started(
                sequence=0, call="call_1",
                logical_wake_selection_identity="l" + "a" * 63,
                wake_identity="a" * 64, close_time=_day_start(date(2024, 1, 22)),
                request_id="req-1", retry_count=1,
            )


class SmokeHarnessTransportAttemptTests(unittest.TestCase):
    """F-03: transport records ATTEMPT_STARTED before the bridge child launch."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.state_dir = self.root / "state"
        self.ledger = ProviderAttemptLedger(
            provider_attempt_ledger_path_for(self.state_dir), authority_identity="auth-1"
        )
        self.bundles = ((b"p", b"p", b"p", b"p"),) * 3

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _transport(self, bridge, *, ledger=None):
        return SmokeHarnessTransport(
            bridge=bridge,
            image_bundles=self.bundles,
            expected_provider=PROVIDER,
            expected_model=CURRENT_MODEL,
            attempt_ledger=ledger if ledger is not None else self.ledger,
            attempt_identities=_attempt_identities(),
        )

    def test_attempt_start_persisted_before_child_launch(self) -> None:
        bridge = _ScriptedBridge(_valid_bridge_result)
        transport = self._transport(bridge)
        transport.execute(_fake_request("req-1"))
        # ATTEMPT_STARTED was durable before launch; now RESULT_RECEIVED.
        self.assertEqual(self.ledger.attempts()[0].attempt_state, RESULT_RECEIVED)
        self.assertEqual(self.ledger.attempts()[0].request_id, "req-1")
        self.assertEqual(bridge.launches, 1)

    def test_attempt_ledger_metadata_is_not_passed_to_strict_production_signature(self) -> None:
        """The production bridge has no ``attempt_identity`` keyword argument."""
        class _StrictProductionSignatureBridge:
            def __init__(self) -> None:
                self.launches = 0

            def execute(self, *, system_prompt, decision_prompt, context, png_images):
                self.launches += 1
                return _valid_bridge_result()

        bridge = _StrictProductionSignatureBridge()
        transport = self._transport(bridge)
        raw = transport.execute(_fake_request("req-1"))

        self.assertEqual(raw, _valid_mock_response())
        self.assertEqual(bridge.launches, 1)
        self.assertEqual(self.ledger.attempts()[0].attempt_state, RESULT_RECEIVED)

    def test_attempt_persistence_failure_prevents_child_launch(self) -> None:
        class _FailingLedger:
            def record_attempt_started(self, **kwargs):
                raise RuntimeError("persistence failed")
        bridge = _ScriptedBridge(_valid_bridge_result)
        transport = self._transport(bridge, ledger=_FailingLedger())
        with self.assertRaisesRegex(RuntimeError, "persistence failed"):
            transport.execute(_fake_request("req-1"))
        self.assertEqual(bridge.launches, 0, "child must not launch when attempt persistence fails")

    def test_child_timeout_transitions_to_unknown_and_blocks_next_call(self) -> None:
        bridge = _ScriptedBridge(subprocess.TimeoutExpired("tsx", 300))
        transport = self._transport(bridge)
        with self.assertRaises(subprocess.TimeoutExpired):
            transport.execute(_fake_request("req-1"))
        attempt = self.ledger.attempts()[0]
        self.assertEqual(attempt.attempt_state, UNKNOWN_AFTER_ATTEMPT_START)
        self.assertEqual(attempt.wake_identity, "a" * 64)
        self.assertEqual(attempt.logical_wake_selection_identity, "l" + "a" * 63)
        self.assertEqual(attempt.request_id, "req-1")
        self.assertEqual(attempt.retry_count, 0)
        self.assertEqual(self.ledger.unknown_after_attempt_start_count(), 1)
        self.assertEqual(len(transport.calls), 0)
        # Terminal barrier: a second call is refused outright (no child launch).
        with self.assertRaisesRegex(RuntimeError, "terminally blocked"):
            transport.execute(_fake_request("req-2"))
        self.assertEqual(bridge.launches, 1, "no second child launch after an unknown attempt")

    def test_no_result_after_child_launch_transitions_to_unknown(self) -> None:
        bridge = _ScriptedBridge(RuntimeError("provider-smoke bridge produced no result"))
        transport = self._transport(bridge)
        with self.assertRaisesRegex(RuntimeError, "no result"):
            transport.execute(_fake_request("req-1"))
        self.assertEqual(self.ledger.attempts()[0].attempt_state, UNKNOWN_AFTER_ATTEMPT_START)
        self.assertEqual(self.ledger.unknown_after_attempt_start_count(), 1)

    def test_malformed_result_after_child_launch_transitions_to_unknown(self) -> None:
        def _malformed(**kwargs):
            raise ValueError("invalid result artifact")
        bridge = _ScriptedBridge(_malformed)
        transport = self._transport(bridge)
        with self.assertRaises(ValueError):
            transport.execute(_fake_request("req-1"))
        self.assertEqual(self.ledger.attempts()[0].attempt_state, UNKNOWN_AFTER_ATTEMPT_START)

    def test_valid_result_transitions_to_result_received_and_normal_path_unchanged(self) -> None:
        bridge = _ScriptedBridge(_valid_bridge_result)
        transport = self._transport(bridge)
        raw = transport.execute(_fake_request("req-1"))
        self.assertEqual(raw, _valid_mock_response())
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(self.ledger.attempts()[0].attempt_state, RESULT_RECEIVED)
        self.assertEqual(self.ledger.result_received_count(), 1)
        self.assertEqual(self.ledger.unknown_after_attempt_start_count(), 0)

    def test_terminal_barrier_holds_when_result_and_unknown_persistence_both_fail(self) -> None:
        """A residual ATTEMPT_STARTED row can never permit a second child launch."""
        class _ResultTransitionFailingLedger:
            def __init__(self, ledger) -> None:
                self._ledger = ledger

            def record_attempt_started(self, **kwargs):
                return self._ledger.record_attempt_started(**kwargs)

            def record_result_received(self, **kwargs):
                raise OSError("result ledger write failed")

            def record_unknown_after_attempt_start(self, **kwargs):
                raise OSError("unknown ledger write failed")

        bridge = _ScriptedBridge(_valid_bridge_result)
        transport = self._transport(bridge, ledger=_ResultTransitionFailingLedger(self.ledger))

        with self.assertRaisesRegex(RuntimeError, "slot is terminally blocked"):
            transport.execute(_fake_request("req-1"))
        self.assertEqual(self.ledger.attempts()[0].attempt_state, ATTEMPT_STARTED)
        self.assertEqual(bridge.launches, 1)
        with self.assertRaisesRegex(RuntimeError, "terminally blocked"):
            transport.execute(_fake_request("req-2"))
        self.assertEqual(bridge.launches, 1, "residual attempted state must block call 2")


class ProviderAttemptEvidenceTests(unittest.TestCase):
    """F-03: terminal evidence must distinguish no-attempt / known / unknown."""

    def _runner_module(self):
        path = REPO_ROOT / "tools" / "run_replay_v0_1_provider_smoke.py"
        spec = importlib.util.spec_from_file_location("kpe_smoke_runner_mod3", path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def _load_authority(self):
        payload = _authority_payload(
            status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
            max_spend_cny="3.00", smoke_wakes=_three_wakes(),
        )
        with tempfile.TemporaryDirectory() as tmp:
            return load_provider_smoke_authority(_write_authority(Path(tmp), payload))

    def test_no_attempt_ever_started_is_zero_and_not_adjudication(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        transport = SmokeDeterministicTransport(provider_admitted=True)
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "state"
            state_dir.mkdir()
            evidence = module._provider_attempt_evidence(state_dir, authority, transport)
        self.assertEqual(evidence["provider_attempt_count"], 0)
        self.assertEqual(evidence["unknown_after_attempt_start_count"], 0)
        self.assertEqual(evidence["known_result_count"], 0)
        self.assertFalse(evidence["slot_requires_adjudication"])
        self.assertEqual(evidence["provider_call_count"], 0)

    def test_known_result_evidence(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "state"
            ledger = ProviderAttemptLedger(
                provider_attempt_ledger_path_for(state_dir), authority_identity=authority.identity
            )
            for index in range(3):
                ledger.record_attempt_started(
                    sequence=index, call=("call_1", "call_2", "call_3")[index],
                    logical_wake_selection_identity="l" + "abc"[index] * 63,
                    wake_identity="abc"[index] * 64,
                    close_time=_day_start(date(2024, 1, 22), 9 + index),
                    request_id=f"req-{index}",
                )
                ledger.record_result_received(sequence=index, metadata={"provider": "deepseek"})
            evidence = module._provider_attempt_evidence(state_dir, authority, object())
        self.assertEqual(evidence["provider_attempt_count"], 3)
        self.assertEqual(evidence["known_result_count"], 3)
        self.assertEqual(evidence["unknown_after_attempt_start_count"], 0)
        self.assertFalse(evidence["slot_requires_adjudication"])
        self.assertEqual(evidence["provider_call_count"], 3)

    def test_unknown_attempt_is_never_zero_and_requires_adjudication(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        transport = SmokeDeterministicTransport(provider_admitted=True)
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "state"
            ledger = ProviderAttemptLedger(
                provider_attempt_ledger_path_for(state_dir), authority_identity=authority.identity
            )
            ledger.record_attempt_started(
                sequence=0, call="call_1",
                logical_wake_selection_identity="l" + "a" * 63,
                wake_identity="a" * 64,
                close_time=_day_start(date(2024, 1, 22)),
                request_id="req-1",
            )
            ledger.record_unknown_after_attempt_start(sequence=0, reason="timeout")
            evidence = module._provider_attempt_evidence(state_dir, authority, transport)
        self.assertEqual(evidence["provider_attempt_count"], 1)
        self.assertEqual(evidence["unknown_after_attempt_start_count"], 1)
        self.assertEqual(evidence["known_result_count"], 0)
        self.assertTrue(evidence["slot_requires_adjudication"])
        self.assertEqual(evidence["provider_attempt_state"], {"call_1": UNKNOWN_AFTER_ATTEMPT_START})
        self.assertEqual(evidence["provider_call_count"], 1, "unknown started attempt must never be zero")

    def test_unresolved_attempt_started_requires_adjudication(self) -> None:
        module = self._runner_module()
        authority = self._load_authority()
        with tempfile.TemporaryDirectory() as tmp:
            state_dir = Path(tmp) / "state"
            ledger = ProviderAttemptLedger(
                provider_attempt_ledger_path_for(state_dir), authority_identity=authority.identity
            )
            ledger.record_attempt_started(
                sequence=0, call="call_1",
                logical_wake_selection_identity="l" + "a" * 63,
                wake_identity="a" * 64,
                close_time=_day_start(date(2024, 1, 22)), request_id="req-1",
            )
            evidence = module._provider_attempt_evidence(state_dir, authority, object())
        self.assertEqual(evidence["provider_attempt_count"], 1)
        self.assertEqual(evidence["unresolved_attempt_started_count"], 1)
        self.assertEqual(evidence["unknown_after_attempt_start_count"], 0)
        self.assertTrue(evidence["slot_requires_adjudication"])
        self.assertEqual(evidence["provider_call_count"], 1)

    def test_unknown_attempt_terminal_barrier_in_driven_run(self) -> None:
        """An unknown attempt in a real orchestrator run must stop before call 2."""
        module = self._runner_module()
        authority = self._load_authority()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_dir = root / "state"
            fixture = ReplayV01RuntimeFixture(root)
            slice_ = build_slice()
            replay_days = slice_.burn_in_days + slice_.measurement_days
            trading_day = replay_days[0]
            steps = build_session_steps(
                trading_day=trading_day, session_identity="sess-f03",
                start=_day_start(trading_day), count=3,
            )
            ledger = ProviderAttemptLedger(
                provider_attempt_ledger_path_for(state_dir), authority_identity=authority.identity
            )
            bridge = _ScriptedBridge(subprocess.TimeoutExpired("tsx", 300))
            transport = SmokeHarnessTransport(
                bridge=bridge,
                image_bundles=((b"p", b"p", b"p", b"p"),) * 3,
                expected_provider=PROVIDER,
                expected_model=CURRENT_MODEL,
                attempt_ledger=ledger,
                attempt_identities=_attempt_identities(),
            )
            orchestrator = ReplayV01Orchestrator(
                runtime_factory=fixture.make_runtime_factory(),
                clock=ReplayClock(current_time=steps[0].wake_bar.open_time),
                slice_=slice_, transport=transport, state_dir=state_dir,
            )
            try:
                orchestrator.begin_session(
                    phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
                    session_identity="sess-f03", steps=steps,
                )
                failure = None
                for step in steps:
                    try:
                        orchestrator.run_wake_step(step)
                    except Exception as exc:
                        failure = exc
                        break
                self.assertIsInstance(failure, subprocess.TimeoutExpired)
                self.assertEqual(bridge.launches, 1, "no call 2 after an unknown attempt")
                # Terminal evidence from the durable attempt ledger.
                payload = module._assemble_fail_evidence(
                    authority=authority,
                    state_dir=state_dir,
                    transport=transport,
                    bindings=orchestrator.list_step_bindings(),
                    transport_name="harness",
                    error=failure,
                    trader_identity=fixture.identity.identity,
                )
                self.assertEqual(payload["provider_attempt_count"], 1)
                self.assertEqual(payload["unknown_after_attempt_start_count"], 1)
                self.assertTrue(payload["slot_requires_adjudication"])
                self.assertEqual(payload["provider_call_count"], 1)
                self.assertEqual(payload["admitted_wake_count"], 1)
                self.assertEqual(payload["admitted_wakes"][0]["call"], "call_1")
                # The attempt ledger recorded the exact attempt identity it was
                # given (authority-sealed), while the bound-wake evidence carries
                # the actual ledger wake identity.
                self.assertEqual(ledger.attempts()[0].wake_identity, "a" * 64)
                self.assertEqual(
                    ledger.attempts()[0].logical_wake_selection_identity, "l" + "a" * 63,
                )
                self.assertEqual(ledger.attempts()[0].attempt_state, UNKNOWN_AFTER_ATTEMPT_START)
                self.assertTrue(payload["admitted_wakes"][0]["wake_identity"])
                self.assertNotIn("decision_identity", payload["admitted_wakes"][0])
            finally:
                orchestrator.runtime.close()

    def test_harness_attempt_identity_construction_is_timezone_aware(self) -> None:
        """F-05 regression: the harness attempt-identity construction must build
        cleanly (module imports ``timezone``) and emit exact timezone-aware
        close times and both wake identities for all three calls."""
        module = self._runner_module()
        authority = self._load_authority()
        identities = module._build_attempt_identities(authority)
        self.assertEqual(len(identities), 3)
        for index, (name, item) in enumerate(zip(("call_1", "call_2", "call_3"), identities)):
            self.assertEqual(item["call"], name)
            self.assertEqual(item["sequence"], index)
            self.assertTrue(item["wake_identity"])
            self.assertTrue(item["logical_wake_selection_identity"])
            self.assertTrue(item["close_time"].endswith("+00:00"))
        # Exact close times match the authority wake bindings (UTC, microseconds).
        for index, (name, item) in enumerate(zip(("call_1", "call_2", "call_3"), identities)):
            expected = authority.smoke_wakes[index][1].close_time.astimezone(timezone.utc)
            self.assertEqual(item["close_time"], expected.isoformat(timespec="microseconds"))


class CostWaiverAuthorityTests(unittest.TestCase):
    """Part B: forward V0_3 authority with explicit Owner CNY-ceiling waiver."""

    def _write_and_load(self, payload):
        with tempfile.TemporaryDirectory() as tmp:
            return load_provider_smoke_authority(_write_authority(Path(tmp), payload))

    def test_forward_waiver_authority_loads(self) -> None:
        payload = _authority_payload(
            authority_version=SMOKE_RETEST_AUTHORITY_VERSION_V0_3,
            status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
            max_spend_cny=OWNER_CNY_CEILING_WAIVED,
            cny_ceiling_mode=CNY_CEILING_MODE_WAIVED,
            smoke_wakes=_three_wakes(),
        )
        authority = self._write_and_load(payload)
        self.assertEqual(authority.authority_version, SMOKE_RETEST_AUTHORITY_VERSION_V0_3)
        self.assertEqual(authority.cny_ceiling_mode, CNY_CEILING_MODE_WAIVED)
        self.assertEqual(authority.max_spend_cny, OWNER_CNY_CEILING_WAIVED)
        self.assertEqual(authority.max_provider_calls, 3)
        self.assertEqual(authority.max_retries, 0)
        self.assertEqual(authority.images_per_call, 4)
        self.assertEqual(authority.restart_after_call, 2)
        assert_smoke_authority_active(authority)

    def test_waiver_requires_owner_payment_confirmation_for_active(self) -> None:
        payload = _raw_authority_payload(
            authority_version=SMOKE_RETEST_AUTHORITY_VERSION_V0_3,
            owner_payment_confirmation=False,
            max_spend_cny=OWNER_CNY_CEILING_WAIVED,
            cny_ceiling_mode=CNY_CEILING_MODE_WAIVED,
        )
        with self.assertRaises(ValueError):
            self._write_and_load(payload)

    def test_waiver_requires_explicit_sentinel_max_spend_cny(self) -> None:
        payload = _raw_authority_payload(
            authority_version=SMOKE_RETEST_AUTHORITY_VERSION_V0_3,
            max_spend_cny="3.00",
            cny_ceiling_mode=CNY_CEILING_MODE_WAIVED,
        )
        with self.assertRaises(ValueError):
            self._write_and_load(payload)

    def test_deleting_max_spend_cny_from_old_authority_still_fails(self) -> None:
        payload = _raw_authority_payload()
        payload.pop("max_spend_cny")
        payload["authority_identity"] = _canonical_identity(payload)
        with self.assertRaises(ValueError):
            self._write_and_load(payload)

    def test_waiver_cannot_be_applied_to_historical_v0_2_authority(self) -> None:
        payload = _raw_authority_payload(
            authority_version=SMOKE_AUTHORITY_VERSION_V0_2,
            max_spend_cny=OWNER_CNY_CEILING_WAIVED,
            cny_ceiling_mode=CNY_CEILING_MODE_WAIVED,
        )
        with self.assertRaises(ValueError):
            self._write_and_load(payload)

    def test_old_numeric_active_rules_remain_strict(self) -> None:
        # V0_2 ACTIVE with non-finite / non-positive max_spend_cny still fails.
        for bad in ("abc", "0", "-1", "NaN", "Infinity"):
            payload = _raw_authority_payload(max_spend_cny=bad)
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    self._write_and_load(payload)
        # Valid V0_2 numeric ACTIVE still loads.
        ok = _authority_payload(
            status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
            max_spend_cny="3.00", smoke_wakes=_three_wakes(),
        )
        authority = self._write_and_load(ok)
        self.assertEqual(authority.cny_ceiling_mode, CNY_CEILING_MODE_NUMERIC)

    def test_forward_numeric_mode_requires_positive_finite(self) -> None:
        payload = _raw_authority_payload(
            authority_version=SMOKE_RETEST_AUTHORITY_VERSION_V0_3,
            max_spend_cny="abc", cny_ceiling_mode=CNY_CEILING_MODE_NUMERIC,
        )
        with self.assertRaises(ValueError):
            self._write_and_load(payload)

    def test_historical_terminal_authorities_still_readable(self) -> None:
        for payload in (
            _authority_payload(
                authority_version=SMOKE_AUTHORITY_VERSION, status=SMOKE_STATUS_REVOKED,
                owner_payment_confirmation=True, max_spend_cny="1.00",
                smoke_wakes=_three_wakes(logical=False),
            ),
            _authority_payload(
                authority_version=SMOKE_RETEST_AUTHORITY_VERSION_V0_2, status=SMOKE_STATUS_REVOKED,
                owner_payment_confirmation=True, max_spend_cny="1.00",
                smoke_wakes=_three_wakes(),
            ),
        ):
            with self.subTest(version=payload["authority_version"]):
                authority = self._write_and_load(payload)
                self.assertEqual(authority.status, SMOKE_STATUS_REVOKED)


if __name__ == "__main__":
    unittest.main()
