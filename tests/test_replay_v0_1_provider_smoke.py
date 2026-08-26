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
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest

from src.jianghe_ai_trader import ReplayClock
from src.jianghe_visual_renderer import JiangheVisualRenderer, RENDERER_VERSION
from src.replay_v0_1_orchestrator import PHASE_BURN_IN, ReplayV01Orchestrator
from src.replay_v0_1_smoke_authority import (
    PROVIDER,
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


def _authority_payload(
    *,
    status: str,
    owner_payment_confirmation: bool,
    max_spend_cny: str,
    smoke_wakes: tuple[tuple[str, SmokeWakeBinding], ...],
    slice_identity: str = "slice-test",
    exact_slice_seal_identity: str = "seal-test",
    product: str = "cu",
    concrete_contract: str = "SHFE.cu2406",
    api_key_env: str = "DEEPSEEK_API_KEY",
    execution_code_commit: str = "TEST_COMMIT",
    context_policy_identity: str = "context-policy-test",
) -> dict:
    authority = ProviderSmokeAuthority(
        authority_version="KPE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_V0_1",
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
                smoke_wakes=(
                    ("call_1", SmokeWakeBinding("a" * 64, _day_start(date(2024, 1, 22)))),
                    ("call_2", SmokeWakeBinding("b" * 64, _day_start(date(2024, 1, 22), 10))),
                    ("call_3", SmokeWakeBinding("c" * 64, _day_start(date(2024, 1, 22), 11))),
                ),
            )
            path = _write_authority(root, payload)
            authority = load_provider_smoke_authority(path)
            self.assertEqual(authority.status, SMOKE_STATUS_PENDING)
            self.assertFalse(authority.owner_payment_confirmation)
            self.assertEqual(authority.identity, payload["authority_identity"])
            with self.assertRaises(ValueError):
                assert_smoke_authority_active(authority)

    def test_active_requires_payment_confirmation_and_concrete_spend(self) -> None:
        wakes = (
            ("call_1", SmokeWakeBinding("a" * 64, _day_start(date(2024, 1, 22)))),
            ("call_2", SmokeWakeBinding("b" * 64, _day_start(date(2024, 1, 22), 10))),
            ("call_3", SmokeWakeBinding("c" * 64, _day_start(date(2024, 1, 22), 11))),
        )
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
                smoke_wakes=(
                    ("call_1", SmokeWakeBinding("a" * 64, _day_start(date(2024, 1, 22)))),
                    ("call_2", SmokeWakeBinding("b" * 64, _day_start(date(2024, 1, 22), 10))),
                    ("call_3", SmokeWakeBinding("c" * 64, _day_start(date(2024, 1, 22), 11))),
                ),
            )
            payload["images_per_call"] = 5  # tamper
            path = _write_authority(root, payload)
            with self.assertRaises(ValueError):
                load_provider_smoke_authority(path)

    def test_bridge_construction_requires_active_authority_before_any_env_or_tsx(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _authority_payload(
                status=SMOKE_STATUS_PENDING, owner_payment_confirmation=False,
                max_spend_cny=SPEND_PENDING,
                smoke_wakes=(
                    ("call_1", SmokeWakeBinding("a" * 64, _day_start(date(2024, 1, 22)))),
                    ("call_2", SmokeWakeBinding("b" * 64, _day_start(date(2024, 1, 22), 10))),
                    ("call_3", SmokeWakeBinding("c" * 64, _day_start(date(2024, 1, 22), 11))),
                ),
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
                smoke_wakes=(
                    ("call_1", SmokeWakeBinding("a" * 64, _day_start(date(2024, 1, 22)))),
                    ("call_2", SmokeWakeBinding("b" * 64, _day_start(date(2024, 1, 22), 10))),
                    ("call_3", SmokeWakeBinding("c" * 64, _day_start(date(2024, 1, 22), 11))),
                ),
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
                (name, SmokeWakeBinding(binding.wake_identity, binding.close_time))
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
                "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_1",
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
                smoke_wakes=(
                    ("call_1", SmokeWakeBinding("a" * 64, _day_start(date(2024, 1, 22)))),
                    ("call_2", SmokeWakeBinding("b" * 64, _day_start(date(2024, 1, 22), 10))),
                    ("call_3", SmokeWakeBinding("c" * 64, _day_start(date(2024, 1, 22), 11))),
                ),
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
                        smoke_wakes=(
                            ("call_1", SmokeWakeBinding("a" * 64, _day_start(date(2024, 1, 22)))),
                            ("call_2", SmokeWakeBinding("b" * 64, _day_start(date(2024, 1, 22), 10))),
                            ("call_3", SmokeWakeBinding("c" * 64, _day_start(date(2024, 1, 22), 11))),
                        ),
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
    """Regression: the runner's step-9 wake-binding check must unpack the
    ``(name, SmokeWakeBinding)`` pairs of ``authority.smoke_wakes`` correctly."""

    def _runner_module(self):
        path = REPO_ROOT / "tools" / "run_replay_v0_1_provider_smoke.py"
        spec = importlib.util.spec_from_file_location("kpe_smoke_runner_mod", path)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def test_wake_binding_verification_matches_authority(self) -> None:
        module = self._runner_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = _authority_payload(
                status=SMOKE_STATUS_ACTIVE, owner_payment_confirmation=True,
                max_spend_cny="3.00",
                smoke_wakes=(
                    ("call_1", SmokeWakeBinding("a" * 64, _day_start(date(2024, 1, 22)))),
                    ("call_2", SmokeWakeBinding("b" * 64, _day_start(date(2024, 1, 22), 10))),
                    ("call_3", SmokeWakeBinding("c" * 64, _day_start(date(2024, 1, 22), 11))),
                ),
            )
            authority = load_provider_smoke_authority(_write_authority(root, payload))

            class _Binding:
                def __init__(self, wake_identity):
                    self.wake_identity = wake_identity

            # Exact match passes (regression for the tuple-decomposition bug).
            module._verify_smoke_wake_bindings(authority, [
                _Binding("a" * 64), _Binding("b" * 64), _Binding("c" * 64),
            ])
            # Reordered wakes fail closed (order is sealed).
            with self.assertRaises(ValueError):
                module._verify_smoke_wake_bindings(authority, [
                    _Binding("c" * 64), _Binding("b" * 64), _Binding("a" * 64),
                ])
            # Any identity mismatch fails closed.
            with self.assertRaises(ValueError):
                module._verify_smoke_wake_bindings(authority, [
                    _Binding("a" * 64), _Binding("d" * 64), _Binding("c" * 64),
                ])
            # Wrong count fails closed.
            with self.assertRaises(ValueError):
                module._verify_smoke_wake_bindings(authority, [
                    _Binding("a" * 64), _Binding("b" * 64),
                ])


if __name__ == "__main__":
    unittest.main()
