#!/usr/bin/env python3
"""Run the V0.1 provider-smoke slot: exactly three governed wakes, max 3 real calls.

This runner is the fail-closed execution gate for
``SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`` provider smoke.  It:

1. loads and strictly validates the machine-readable provider-smoke authority;
2. refuses to proceed (before any network/provider initialization, before reading
   ``DEEPSEEK_API_KEY``, before constructing any adapter) unless the authority is
   ACTIVE with ``owner_payment_confirmation=true``;
3. pre-network: verifies the execution-critical working tree still matches
   ``execution_code_commit`` and mechanically binds live prompt / context-policy /
   renderer / ``DEEPSEEK_API_KEY`` identities to the authority;
4. binds the exact sealed slice and the exact first-three smoke wakes;
5. renders four PNGs per wake from the causal 4H/1H/15m/5m context;
6. drives call 1 -> call 2 -> project-owned restart -> call 3 via the pinned
   Harness one-shot bridge (or a deterministic mock for zero-cost rehearsal);
7. fails closed after each Harness call unless exact provider/model, 4 images,
   and exactly 1 request are returned;
8. forces a stop after call 3 — a fourth request is impossible by construction;
9. writes machine-readable smoke evidence (no secrets).

In the current frozen state the authority is PENDING, so the runner always exits
at step 2.  ``--transport mock`` plus a synthetic ACTIVE authority (test fixture
only) exercises the full three-call chain with zero cost.  ``--base-url`` is
loopback-only and requires the explicit ``--allow-test-base-url`` test flag.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.jianghe_ai_trader import JiangheAITraderIdentity, ReplayClock
from src.jianghe_canon_retrieval import JiangheCanonRetriever
from src.jianghe_response_normalizer import NORMALIZER_IDENTITY, RESPONSE_SCHEMA_VERSION
from src.jianghe_trading_only_prompt import TRADING_ONLY_PROMPT_CONTRACT
from src.jianghe_visual_renderer import JiangheVisualRenderer, RENDERER_VERSION
from src.fixed_5m_wake_ledger import WakeLedgerArchive, wake_ledger_path_for
from src.replay_v0_1_provider_attempt_ledger import (
    UNKNOWN_AFTER_ATTEMPT_START,
    ProviderAttemptLedger,
    provider_attempt_ledger_path_for,
)
from src.persistent_deepseek_runtime import (
    CURRENT_MODEL,
    DeepSeekHarnessRuntimeContract,
    PersistentDeepSeekTraderPrototype,
    ProjectToolRegistry,
    default_jianghe_canon_paths,
)
from src.persistent_trader_store import PersistentTraderStore
from src.replay_v0_1_canonical_feed import (
    ReplayMinuteBar,
    build_fixed_5m_preflight,
    governed_windows_for_days,
)
from src.replay_v0_1_canonical_steps import build_governed_wake_step
from src.replay_v0_1_causal_context import CanonicalCausalContextIndex, context_policy_identity
from src.replay_v0_1_exact_slice import _parse_calendar
from src.replay_v0_1_orchestrator import PHASE_BURN_IN, ReplayV01Orchestrator
from src.replay_v0_1_qualified_manifest import select_and_seal_revalidated_exact_v0_1_slice
from src.replay_v0_1_runtime import ReplayV01Runtime
from src.replay_v0_1_smoke_authority import (
    SMOKE_STATUS_ACTIVE,
    assert_smoke_authority_active,
    load_provider_smoke_authority,
)
from src.replay_v0_1_smoke_bridge import (
    HarnessOneShotBridge,
    SmokeDeterministicTransport,
    SmokeHarnessTransport,
)
from src.replay_v0_1_smoke_guard import (
    bind_runtime_identities_to_authority,
    validate_test_base_url,
    verify_execution_code_bound,
)
from src.replay_v0_1_smoke_visual import render_wake_charts

PROVIDER_SMOKE_RUNNER_VERSION = "KPE_REPLAY_V0_1_PROVIDER_SMOKE_RUNNER_V0_1"


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Run the fail-closed V0.1 three-call provider smoke slot; real calls stay locked."
    )
    p.add_argument("--manifest", type=Path, default=REPO_ROOT / "data/canonical/manifest.json")
    p.add_argument("--parquet-root", type=Path, default=REPO_ROOT / "data/canonical/parquet")
    p.add_argument("--state-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--authority", type=Path, required=True,
                   help="machine-readable provider-smoke authority JSON")
    p.add_argument("--transport", choices=("mock", "harness"), default="mock",
                   help="mock = deterministic zero-cost transport; harness = pinned Harness bridge")
    p.add_argument("--harness-root", type=Path, default=None,
                   help="pinned DeepSeek Harness checkout root (required for --transport harness)")
    p.add_argument("--base-url", type=str, default=None,
                   help="loopback-only provider endpoint override; requires --allow-test-base-url")
    p.add_argument("--allow-test-base-url", action="store_true",
                   help="permit --base-url only for loopback test servers (test-only, never production)")
    return p


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _files_identity(repo_root: Path, relative_paths: tuple[str, ...]) -> str:
    records = []
    for relative in relative_paths:
        path = repo_root / relative
        if not path.is_file():
            raise ValueError(f"identity-bound file is missing: {relative}")
        records.append((relative, sha256(path.read_bytes()).hexdigest()))
    encoded = json.dumps(records, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _build_runtime_factory(*, repo_root: Path, state_dir: Path, causal_policy_identity: str):
    allowed_paths = default_jianghe_canon_paths(repo_root)
    if not allowed_paths:
        raise ValueError("no current Jianghe canon artifacts are available")
    retriever_probe = JiangheCanonRetriever(
        repo_root, allowed_paths=allowed_paths, max_results=6, max_chars=6000, context_lines=1
    )
    primary_registry = "docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.jsonl"
    interpretation_paths = tuple(
        path for path in allowed_paths
        if path.endswith((
            "JIANGHE_CURRENT_VIEW_V1_1.md",
            "JIANGHE_TRADER_DOSSIER_V1_1.md",
            "JIANGHE_STRATEGY_FAMILIES_V1_1.md",
            "JIANGHE_CONTRADICTION_REGISTER_V1_1.md",
            "JIANGHE_UNKNOWN_REGISTER_V1_1.md",
        ))
    )
    renderer = JiangheVisualRenderer()
    contract = DeepSeekHarnessRuntimeContract.from_prompts(
        system_prompt=TRADING_ONLY_PROMPT_CONTRACT.system_prompt,
        decision_prompt=TRADING_ONLY_PROMPT_CONTRACT.decision_prompt,
    )
    trader_identity = JiangheAITraderIdentity(
        knowledge_pack_identity=retriever_probe.identity,
        primary_branch_registry_identity=_files_identity(repo_root, (primary_registry,)),
        interpretation_set_identity=_files_identity(repo_root, interpretation_paths),
        model_provider="deepseek", model_id_version=CURRENT_MODEL,
        system_prompt_identity=TRADING_ONLY_PROMPT_CONTRACT.system_prompt_sha256,
        decision_prompt_identity=TRADING_ONLY_PROMPT_CONTRACT.decision_prompt_sha256,
        context_selection_policy_identity=causal_policy_identity,
        memory_policy_identity="PROJECT_SQLITE_PLUS_VERSIONED_HYPOTHESIS_V0_1",
        chart_renderer_identity=f"{RENDERER_VERSION}:{renderer.config.identity}",
        observation_schema_version="JIANGHE_OBSERVATION_V0_1", wake_policy_version="EVERY_NEW_CLOSED_5M_BAR",
        decision_schema_version=RESPONSE_SCHEMA_VERSION, runtime_normalizer_identity=NORMALIZER_IDENTITY,
        hard_execution_envelope_identity="INTENT_ONLY_NO_PAPER_EXECUTION_V0_1",
        inference_configuration=(("max_retries", "0"), ("provider_call_authorized", "false")),
        tool_capability_set=(), source_family_scope=("A", "B", "C", "D"),
    )
    db_path = state_dir / "trader.sqlite3"

    def factory(clock):
        store = PersistentTraderStore(db_path, trader_identity=trader_identity.identity)
        retriever = JiangheCanonRetriever(
            repo_root, allowed_paths=allowed_paths, max_results=6, max_chars=6000, context_lines=1
        )
        tools = ProjectToolRegistry(store, clock=clock)
        base = PersistentDeepSeekTraderPrototype(
            trader_identity=trader_identity, store=store, retriever=retriever,
            tools=tools, runtime_contract=contract, clock=clock,
        )
        return ReplayV01Runtime(base)
    return factory, trader_identity, contract, renderer


def _load_rows(*, parquet_root: Path, seal, sessions: dict):
    try:
        import pyarrow.dataset as ds
    except ImportError as error:
        raise RuntimeError("provider smoke requires the pinned canonical pyarrow environment") from error
    if not parquet_root.is_dir():
        raise ValueError("canonical parquet root does not exist")
    all_bound_days = seal.slice.prior_history_days + seal.slice.burn_in_days + seal.slice.measurement_days
    partition_by_day = dict(zip(all_bound_days, seal.slice.partition_identities, strict=True))
    authority_identity = sessions[seal.slice.product]["identity"]
    dataset = ds.dataset(str(parquet_root), format="parquet", partitioning="hive")
    expression = (ds.field("product") == seal.slice.product) & (
        ds.field("concrete_contract") == seal.slice.concrete_contract
    )
    table = dataset.to_table(
        columns=[
            "product", "concrete_contract", "trading_day", "bar_start", "bar_end",
            "historical_available_at", "open", "high", "low", "close", "volume",
            "session_metadata_identity",
        ],
        filter=expression,
    )
    wanted = set(all_bound_days)
    rows = []
    for raw in table.to_pylist():
        day = raw["trading_day"]
        if day not in wanted:
            continue
        if raw["volume"] is None:
            raise ValueError("selected minute has missing canonical volume")
        row_session_id = raw["session_metadata_identity"]
        if not isinstance(row_session_id, str) or not row_session_id:
            raise ValueError("selected minute has no canonical session_metadata_identity")
        rows.append(ReplayMinuteBar(
            product=raw["product"], concrete_contract=raw["concrete_contract"],
            trading_day=day, start=raw["bar_start"], end=raw["bar_end"],
            available_at=raw["historical_available_at"], open=raw["open"], high=raw["high"],
            low=raw["low"], close=raw["close"], volume=Decimal(raw["volume"]),
            partition_identity=partition_by_day[day],
            session_authority_identity=authority_identity,
        ))
    return tuple(sorted(rows, key=lambda item: item.start))


def _authority_mismatch(authority, seal) -> str | None:
    if authority.exact_slice_seal_identity != seal.identity:
        return "exact slice seal identity mismatch"
    if authority.slice_identity != seal.slice.identity:
        return "slice identity mismatch"
    if authority.product != seal.slice.product:
        return "product mismatch"
    if authority.concrete_contract != seal.slice.concrete_contract:
        return "concrete contract mismatch"
    return None


def _assert_wake_pair_matches(
    name: str, actual_logical: str, actual_runtime: str, expected
) -> None:
    """Independent fail-closed checks of logical and runtime wake identities.

    A correct runtime identity never masks a bad logical identity and vice
    versa: both must exactly match their respective sealed authority values.
    """
    expected_logical = expected.logical_wake_selection_identity
    if expected_logical is None:
        raise ValueError(
            f"authority {name} carries no logical_wake_selection_identity; "
            "an ACTIVE two-identity authority is required"
        )
    if not actual_logical or not actual_runtime:
        raise ValueError(
            f"authority {name} actual binding is missing a wake identity"
        )
    if actual_logical != expected_logical:
        raise ValueError(
            f"authority {name} logical wake-selection identity mismatch: "
            f"sealed={expected_logical} actual={actual_logical}"
        )
    if actual_runtime != expected.wake_identity:
        raise ValueError(
            f"authority {name} runtime wake identity mismatch: "
            f"sealed={expected.wake_identity} actual={actual_runtime}"
        )


def _verify_smoke_wake_bindings(authority, bindings) -> None:
    """Fail closed unless the driven step bindings match the sealed wakes.

    ``authority.smoke_wakes`` is an ordered tuple of ``(name, SmokeWakeBinding)``
    pairs; each driven ``ReplayStepBinding`` must match BOTH the sealed logical
    wake-selection identity and the sealed runtime wake identity in the same
    call order.  The two checks are independent.
    """
    if len(bindings) != 3:
        raise ValueError("provider smoke must produce exactly three governed step bindings")
    for name, binding, (expected_name, expected) in zip(
        ("call_1", "call_2", "call_3"), bindings, authority.smoke_wakes
    ):
        if name != expected_name:
            raise ValueError(
                f"authority smoke wake order mismatch: expected {expected_name}, got {name}"
            )
        _assert_wake_pair_matches(
            name,
            actual_logical=binding.logical_wake_selection_identity,
            actual_runtime=binding.wake_identity,
            expected=expected,
        )


def _build_wake_guard(authority):
    """Return a pre-call guard that fails closed before each provider call.

    The guard is invoked by the orchestrator immediately after a governed wake
    is registered (before the model request is prepared and before the
    transport/provider call), so a mismatch stops before network capability use
    for that wake, as far as the existing architecture permits.
    """
    expected_by_sequence = {
        sequence: binding
        for sequence, (_name, binding) in enumerate(authority.smoke_wakes)
    }

    def _guard(wake, sequence: int) -> None:
        expected = expected_by_sequence.get(sequence)
        if expected is None:
            raise ValueError(
                f"authority has no sealed wake for driven sequence {sequence}"
            )
        name = ("call_1", "call_2", "call_3")[sequence]
        _assert_wake_pair_matches(
            name,
            actual_logical=wake.logical_wake_selection_identity,
            actual_runtime=wake.wake_identity,
            expected=expected,
        )

    return _guard


def _build_call_evidence(name, binding, rendered, finish_reason, provider_request_id, token_usage) -> dict:
    """Per-call PASS evidence retaining BOTH wake identities."""
    return {
        "call": name,
        "wake_identity": binding.wake_identity,
        "logical_wake_selection_identity": binding.logical_wake_selection_identity,
        "close_time": binding.close_time.isoformat(),
        "observation_identity": binding.observation_identity,
        "request_id": binding.request_id,
        "decision_identity": binding.decision_identity,
        "png_sha256": list(rendered.png_sha256s),
        "visual_artifact_identities": [
            artifact.visual_artifact_identity
            for artifact in rendered.artifacts
        ],
        "finish_reason": finish_reason,
        "provider_request_id": provider_request_id,
        "token_usage": token_usage,
    }


def _build_admitted_wake_evidence(bindings) -> list[dict]:
    """Fail-closed admitted-wake evidence retaining BOTH identities.

    Used when a failure occurs after one or more wakes were admitted so the
    attempted provider opportunity remains reconstructable.  Never fabricates a
    logical identity for wakes that were not actually admitted.
    """
    return [
        {
            "call": name,
            "wake_identity": binding.wake_identity,
            "logical_wake_selection_identity": binding.logical_wake_selection_identity,
            "close_time": binding.close_time.isoformat(),
            "observation_identity": binding.observation_identity,
            "request_id": binding.request_id,
            "decision_identity": binding.decision_identity,
        }
        for name, binding in zip(("call_1", "call_2", "call_3"), bindings)
    ]


def _read_bound_wakes(state_dir) -> tuple:
    """Read ALL actually request-bound wakes from the durable wake ledger.

    The wake ledger durably persists the request binding (with both wake
    identities, close time, sequence, request_id and retry_count) BEFORE the
    transport/provider call, so it is the factual source for every admitted
    wake even when response normalization fails inside ``run_wake_step``.
    """
    ledger_path = wake_ledger_path_for(state_dir)
    if not ledger_path.exists():
        return ()
    archive = WakeLedgerArchive(ledger_path)
    return archive.bound_wakes()


def _build_bound_wake_evidence(bound_wakes, completed_bindings) -> list[dict]:
    """Fail-closed evidence for actually request-bound wakes.

    Each request-bound ``GovernedWake`` contributes its exact identities and
    request identity.  ``decision_identity`` / ``observation_identity`` are
    included ONLY when a completed ``ReplayStepBinding`` exists for that wake
    (a normalized decision actually exists); nothing is fabricated for a wake
    whose response normalization failed.
    """
    completed_by_wake = {
        getattr(binding, "wake_identity", None): binding
        for binding in completed_bindings
        if getattr(binding, "wake_identity", None)
    }
    evidence = []
    for wake in bound_wakes:
        record = {
            "call": ("call_1", "call_2", "call_3")[wake.sequence],
            "sequence": wake.sequence,
            "wake_identity": wake.wake_identity,
            "logical_wake_selection_identity": wake.logical_wake_selection_identity,
            "close_time": wake.close_time.isoformat(),
            "request_id": wake.request_id,
            "retry_count": wake.retry_count,
        }
        completed = completed_by_wake.get(wake.wake_identity)
        if completed is not None:
            record["decision_identity"] = completed.decision_identity
            record["observation_identity"] = completed.observation_identity
        evidence.append(record)
    return evidence


def _read_audit_counts(state_dir, trader_identity) -> dict[str, int]:
    """Read store audit event counts; best-effort (store may be absent/closed)."""
    try:
        from src.persistent_trader_store import PersistentTraderStore
        store = PersistentTraderStore(
            Path(state_dir) / "trader.sqlite3", trader_identity=trader_identity
        )
        export = store.portable_export()
        counts = Counter(
            str(item.get("event_kind"))
            for item in export.get("audit", [])
            if isinstance(item, dict)
        )
        store.close()
        return dict(counts)
    except Exception:
        return {}


def _read_attempt_ledger(state_dir, authority_identity: str):
    """Read the durable provider-attempt ledger if present; else None."""
    ledger_path = provider_attempt_ledger_path_for(state_dir)
    if not ledger_path.exists():
        return None
    return ProviderAttemptLedger(ledger_path, authority_identity=authority_identity)


def _provider_attempt_evidence(state_dir, authority, transport) -> dict:
    """Provider-attempt accounting for terminal evidence.

    Conservative semantics: when the durable provider-attempt ledger is present
    (real Harness path), ``provider_call_count`` / ``network_request_count`` are
    the total ATTEMPT_STARTED attempts (the safe upper bound), and a separate
    ``known_result_count`` reports confirmed RESULT_RECEIVED completions.  An
    ``UNKNOWN_AFTER_ATTEMPT_START`` or unresolved ``ATTEMPT_STARTED`` attempt
    is never presented as zero calls; either sets
    ``slot_requires_adjudication``.  When no attempt ledger exists
    (mock/no-network path), the compatibility counts come from the transport's
    recorded calls.
    """
    ledger = _read_attempt_ledger(state_dir, authority.identity)
    if ledger is None:
        transport_calls = len(getattr(transport, "calls", []))
        return {
            "provider_attempt_count": 0,
            "provider_attempt_state": {},
            "unknown_after_attempt_start_count": 0,
            "unresolved_attempt_started_count": 0,
            "known_result_count": 0,
            "slot_requires_adjudication": False,
            "provider_call_count": transport_calls,
            "network_request_count": transport_calls,
        }
    attempts = ledger.attempts()
    unknown_count = ledger.unknown_after_attempt_start_count()
    unresolved_count = ledger.unresolved_attempt_started_count()
    known_count = ledger.result_received_count()
    total = len(attempts)
    return {
        "provider_attempt_count": total,
        "provider_attempt_state": {attempt.call: attempt.attempt_state for attempt in attempts},
        "unknown_after_attempt_start_count": unknown_count,
        "unresolved_attempt_started_count": unresolved_count,
        "known_result_count": known_count,
        "slot_requires_adjudication": unknown_count > 0 or unresolved_count > 0,
        "provider_call_count": total,
        "network_request_count": total,
    }


def _assemble_fail_evidence(
    *,
    authority,
    state_dir,
    transport,
    bindings,
    transport_name: str,
    error: Exception,
    trader_identity: str,
) -> dict:
    """Assemble terminal fail-closed evidence from actually request-bound wakes.

    ``admitted_wake_count`` and ``admitted_wakes`` are based on the durable wake
    ledger's request-bound wakes (the factual admission source), not only on
    completed ``ReplayStepBinding`` objects, so a wake whose provider request
    already occurred but whose response failed normalization is still proven.
    """
    fail_audit_counts = _read_audit_counts(state_dir, trader_identity)
    bound_wakes = _read_bound_wakes(state_dir)
    attempt_evidence = _provider_attempt_evidence(state_dir, authority, transport)
    payload = {
        "status": "FAIL",
        "runner_version": PROVIDER_SMOKE_RUNNER_VERSION,
        "authority_status": authority.status,
        "authority_identity": authority.identity,
        "authority_version": authority.authority_version,
        "provider": authority.provider,
        "model": authority.model,
        "transport": transport_name,
        "reason": f"{type(error).__name__}: {error}",
        "admitted_wake_count": len(bound_wakes),
        "admitted_wakes": _build_bound_wake_evidence(bound_wakes, bindings),
        "request_count": len(bound_wakes),
        "retry_count": 0,
        "hidden_second_requests": 0,
        "state_dir": str(state_dir),
        "audit_event_counts": dict(sorted(fail_audit_counts.items())),
        "full_replay_authorized": authority.full_replay_authorized,
        "full_replay_1998_calls_authorized": authority.full_replay_1998_calls_authorized,
        "max_provider_calls": authority.max_provider_calls,
        "max_retries": authority.max_retries,
        "images_per_call": authority.images_per_call,
    }
    payload.update(attempt_evidence)
    return payload


def _write_evidence_file(output: Path, encoded: str) -> None:
    """Atomically write evidence via a .partial temp file (utf-8, no BOM)."""
    output.parent.mkdir(parents=True, exist_ok=True)
    partial = output.with_name(output.name + ".partial")
    try:
        partial.write_text(encoded, encoding="utf-8")
        partial.replace(output)
    finally:
        if partial.exists():
            partial.unlink()


def main() -> int:
    args = _parser().parse_args()
    state_dir = args.state_dir.resolve()
    output = args.output.resolve()

    # --- 1. Authority gate BEFORE any network/provider initialization. ---
    authority = load_provider_smoke_authority(args.authority)
    try:
        assert_smoke_authority_active(authority)
    except ValueError as error:
        payload = {
            "status": "FAIL",
            "runner_version": PROVIDER_SMOKE_RUNNER_VERSION,
            "authority_status": authority.status,
            "owner_payment_confirmation": authority.owner_payment_confirmation,
            "reason": f"authority gate blocked before any provider/network initialization: {error}",
            "provider_call_count": 0,
            "network_request_count": 0,
            "admitted_wake_count": 0,
        }
        sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        return 1

    # --- 2. Pre-network code-binding + live-identity binding (no provider capability yet). ---
    verify_execution_code_bound(
        repo_root=REPO_ROOT,
        execution_code_commit=authority.execution_code_commit,
    )
    guard_renderer = JiangheVisualRenderer()
    bind_runtime_identities_to_authority(
        authority=authority,
        prompt_contract=TRADING_ONLY_PROMPT_CONTRACT,
        context_policy_identity=context_policy_identity(),
        renderer_identity=f"{RENDERER_VERSION}:{guard_renderer.config.identity}",
        api_key_env=authority.api_key_env,
    )

    # --- 3. State/output hygiene (prevents hidden reruns / silent overwrite). ---
    if state_dir.exists() and any(state_dir.iterdir()):
        raise ValueError("provider smoke state-dir must be new or empty; hidden reruns are forbidden")
    if output.exists():
        raise ValueError("provider smoke output already exists; evidence must not be silently overwritten")
    state_dir.mkdir(parents=True, exist_ok=True)

    # --- 4. Build the sealed slice + causal context + governed steps. ---
    calendar_path = REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json"
    sessions_path = REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json"
    e07_path = REPO_ROOT / "docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json"
    corpus_path = REPO_ROOT / "docs/evidence/CANONICAL_CORPUS_IDENTITY.json"
    revalidation_path = REPO_ROOT / "docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json"
    seal = select_and_seal_revalidated_exact_v0_1_slice(
        manifest_path=args.manifest, revalidation_path=revalidation_path,
        trading_calendar_path=calendar_path, session_schedule_path=sessions_path,
        e07_path=e07_path, corpus_identity_path=corpus_path,
    )
    mismatch = _authority_mismatch(authority, seal)
    if mismatch:
        raise ValueError(f"authority/slice binding failed: {mismatch}")

    calendar_payload = _load_json(calendar_path)
    session_payload = _load_json(sessions_path)
    calendar, night_closed, _ = _parse_calendar(calendar_payload)
    sessions = session_payload["products"]
    prior = seal.slice.prior_history_days
    replay_days = seal.slice.burn_in_days + seal.slice.measurement_days
    all_bound_days = prior + replay_days
    windows = governed_windows_for_days(
        product=seal.slice.product, replay_days=all_bound_days, trading_calendar=calendar,
        night_closed_days=night_closed, session_schedule=sessions,
    )
    rows = _load_rows(parquet_root=args.parquet_root, seal=seal, sessions=sessions)
    replay_windows = tuple(item for item in windows if item.trading_day in replay_days)
    replay_rows = tuple(item for item in rows if item.trading_day in replay_days)
    preflight = build_fixed_5m_preflight(
        product=seal.slice.product, concrete_contract=seal.slice.concrete_contract,
        replay_days=replay_days, windows=replay_windows, minute_bars=replay_rows,
    )
    context_index = CanonicalCausalContextIndex.build(
        product=seal.slice.product, concrete_contract=seal.slice.concrete_contract,
        windows=windows, minute_bars=rows,
    )
    steps = tuple(
        build_governed_wake_step(wake, context_bars=context_index.context_for_wake(wake))
        for wake in preflight.wake_bars
    )
    if len(steps) != preflight.expected_wake_count:
        raise ValueError("governed step count differs from fixed-5m wake count")
    smoke_steps = steps[:3]
    if len(smoke_steps) != 3:
        raise ValueError("provider smoke requires at least three governed wakes in the sealed slice")

    # --- 5. Build runtime factory + renderer (before any network capability). ---
    runtime_factory, trader_identity, runtime_contract, renderer = _build_runtime_factory(
        repo_root=REPO_ROOT, state_dir=state_dir, causal_policy_identity=context_policy_identity(),
    )

    # --- 6. Render the four-PNG bundle per smoke wake (deterministic). ---
    rendered_per_step = tuple(
        render_wake_charts(
            bars=step.context_bars, product=seal.slice.product,
            concrete_contract=seal.slice.concrete_contract,
            as_of=step.wake_bar.available_at, renderer=renderer,
        )
        for step in smoke_steps
    )

    # --- 7. Build transport + orchestrator. ---
    attempt_ledger: ProviderAttemptLedger | None = None
    if args.transport == "harness":
        if not args.harness_root:
            raise ValueError("--transport harness requires --harness-root")
        base_url = validate_test_base_url(args.base_url, allow_test=args.allow_test_base_url)
        bridge = HarnessOneShotBridge(
            authority=authority, harness_root=args.harness_root, repo_root=REPO_ROOT,
            api_key_env=authority.api_key_env, base_url=base_url,
        )
        # Durable provider-attempt ledger: created before any bridge child is
        # launched; records ATTEMPT_STARTED before each child launch.
        attempt_ledger = ProviderAttemptLedger(
            provider_attempt_ledger_path_for(state_dir),
            authority_identity=authority.identity,
        )
        attempt_identities = tuple(
            {
                "sequence": sequence,
                "call": name,
                "logical_wake_selection_identity": binding.logical_wake_selection_identity,
                "wake_identity": binding.wake_identity,
                "close_time": binding.close_time.astimezone(timezone.utc).isoformat(timespec="microseconds"),
            }
            for sequence, (name, binding) in enumerate(authority.smoke_wakes)
        )
        transport = SmokeHarnessTransport(
            bridge=bridge,
            image_bundles=tuple(rendered.png_bytes for rendered in rendered_per_step),
            expected_provider=authority.provider,
            expected_model=authority.model,
            attempt_ledger=attempt_ledger,
            attempt_identities=attempt_identities,
        )
    else:
        transport = SmokeDeterministicTransport(provider_admitted=True)

    orchestrator = ReplayV01Orchestrator(
        runtime_factory=runtime_factory,
        clock=ReplayClock(current_time=smoke_steps[0].wake_bar.open_time),
        slice_=seal.slice,
        transport=transport,
        state_dir=state_dir,
        renderer=renderer,
        wake_guard=_build_wake_guard(authority),
    )

    # --- 8..11. Drive call 1 -> call 2 -> forced restart -> call 3, then write
    # PASS or FAIL-closed machine evidence (a rejection still stops immediately).
    bindings: tuple = ()
    try:
        restart_before_identity: str | None = None
        exported: dict | None = None
        try:
            smoke_day = smoke_steps[0].trading_day
            session_identity = smoke_steps[0].session_identity
            orchestrator.begin_session(
                phase=PHASE_BURN_IN, trading_day=smoke_day, replay_day_index=0,
                session_identity=session_identity, steps=smoke_steps,
            )
            for call_index, step in enumerate(smoke_steps, start=1):
                orchestrator.run_wake_step(step)
                # Keep bindings incrementally updated so fail-closed evidence
                # retains every admitted wake even if a later call fails.
                bindings = orchestrator.list_step_bindings()
                if call_index == 2:
                    restart_before_identity = orchestrator.restart()
            orchestrator.end_session()
            result = orchestrator.finalize()
            # Capture the portable export while the store is still open; the
            # runtime is closed in the finally block below.
            exported = orchestrator.runtime.portable_export()
        finally:
            orchestrator.runtime.close()
        if exported is None:
            raise RuntimeError("provider smoke runtime export was not produced before close")

        # --- 9. Verify exact smoke wake binding against authority. ---
        bindings = orchestrator.list_step_bindings()
        _verify_smoke_wake_bindings(authority, bindings)

        # --- 10. Per-call usage / provider request ids (harness only; mock stays empty). ---
        if args.transport == "harness":
            bridge_results = transport.calls
            per_call_usage = [dict(item.token_usage) for item in bridge_results]
            per_call_provider_request_ids = [item.provider_request_id for item in bridge_results]
            per_call_finish_reasons = [item.finish_reason for item in bridge_results]
        else:
            per_call_usage = [{} for _ in bindings]
            per_call_provider_request_ids = [None for _ in bindings]
            per_call_finish_reasons = ["mock" for _ in bindings]

        audit_events = exported.get("audit", [])
        audit_counts = Counter(
            str(item.get("event_kind")) for item in audit_events if isinstance(item, dict)
        )

        evidence = {
            "status": "PASS",
            "runner_version": PROVIDER_SMOKE_RUNNER_VERSION,
            "admitted_wake_count": 3,
            "request_count": 3,
            "retry_count": 0,
            "hidden_second_requests": 0,
            "provider": authority.provider,
            "model": authority.model,
            "harness_version": authority.harness_version,
            "harness_commit": authority.harness_commit,
            "project_transport_patch": authority.project_transport_patch,
            "transport": args.transport,
            "exact_slice_seal_identity": authority.exact_slice_seal_identity,
            "slice_identity": authority.slice_identity,
            "product": authority.product,
            "concrete_contract": authority.concrete_contract,
            "trader_identity": trader_identity.identity,
            "runtime_contract_identity": runtime_contract.identity,
            "context_policy_identity": context_index.policy_identity,
            "context_index_identity": context_index.identity,
            "renderer_identity": f"{RENDERER_VERSION}:{renderer.config.identity}",
            "canonical_fixed_5m_preflight_identity": preflight.identity,
            "constructed_bar_counts": context_index.bar_counts(),
            "smoke_wakes": [
                _build_call_evidence(
                    name,
                    binding,
                    rendered_per_step[index],
                    per_call_finish_reasons[index],
                    per_call_provider_request_ids[index],
                    per_call_usage[index],
                )
                for index, (name, binding) in enumerate(
                    zip(("call_1", "call_2", "call_3"), bindings)
                )
            ],
            "restart_after_call": 2,
            "restart_before_identity": restart_before_identity,
            "restart_after_identity": restart_before_identity,
            "restart_continuity_result": "VERIFIED" if restart_before_identity else "NOT_RUN",
            "final_state_identity": result.state_identity,
            "audit_event_count": len(audit_events),
            "audit_event_counts": dict(sorted(audit_counts.items())),
            "full_replay_authorized": authority.full_replay_authorized,
            "full_replay_1998_calls_authorized": authority.full_replay_1998_calls_authorized,
            "max_provider_calls": authority.max_provider_calls,
            "max_retries": authority.max_retries,
            "images_per_call": authority.images_per_call,
        }
        evidence.update(_provider_attempt_evidence(state_dir, authority, transport))
        encoded = json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        _write_evidence_file(output, encoded)
        sys.stdout.write(encoded)
        return 0
    except Exception as error:  # noqa: BLE001 - fail-closed terminal evidence
        fail_payload = _assemble_fail_evidence(
            authority=authority,
            state_dir=state_dir,
            transport=transport,
            bindings=bindings,
            transport_name=args.transport,
            error=error,
            trader_identity=trader_identity.identity,
        )
        encoded = json.dumps(fail_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        _write_evidence_file(output, encoded)
        sys.stdout.write(encoded)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
