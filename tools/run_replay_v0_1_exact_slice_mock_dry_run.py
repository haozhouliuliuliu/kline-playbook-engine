#!/usr/bin/env python3
"""Run the complete V0.1 exact-slice lifecycle with a deterministic no-provider mock."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
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
from src.persistent_deepseek_runtime import CURRENT_MODEL, DeepSeekHarnessRuntimeContract, PersistentDeepSeekTraderPrototype, ProjectToolRegistry, default_jianghe_canon_paths
from src.persistent_trader_store import PersistentTraderStore
from src.replay_v0_1_canonical_feed import ReplayMinuteBar, build_fixed_5m_preflight, governed_windows_for_days
from src.replay_v0_1_canonical_steps import build_governed_wake_step
from src.replay_v0_1_causal_context import CanonicalCausalContextIndex, context_policy_identity
from src.replay_v0_1_exact_slice import _parse_calendar
from src.replay_v0_1_mock_dry_run import DeterministicWaitTransport, drive_full_mock_replay
from src.replay_v0_1_orchestrator import ReplayV01Orchestrator
from src.replay_v0_1_qualified_manifest import select_and_seal_revalidated_exact_v0_1_slice
from src.replay_v0_1_runtime import ReplayV01Runtime


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run full exact-slice V0.1 mock lifecycle; zero provider calls.")
    p.add_argument("--manifest", type=Path, default=REPO_ROOT / "data/canonical/manifest.json")
    p.add_argument("--parquet-root", type=Path, default=REPO_ROOT / "data/canonical/parquet")
    p.add_argument("--state-dir", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
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
    retriever_probe = JiangheCanonRetriever(repo_root, allowed_paths=allowed_paths, max_results=6, max_chars=6000, context_lines=1)
    primary_registry = "docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.jsonl"
    interpretation_paths = tuple(path for path in allowed_paths if path.endswith(("JIANGHE_CURRENT_VIEW_V1_1.md", "JIANGHE_TRADER_DOSSIER_V1_1.md", "JIANGHE_STRATEGY_FAMILIES_V1_1.md", "JIANGHE_CONTRADICTION_REGISTER_V1_1.md", "JIANGHE_UNKNOWN_REGISTER_V1_1.md")))
    renderer = JiangheVisualRenderer()
    contract = DeepSeekHarnessRuntimeContract.from_prompts(system_prompt=TRADING_ONLY_PROMPT_CONTRACT.system_prompt, decision_prompt=TRADING_ONLY_PROMPT_CONTRACT.decision_prompt)
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
        retriever = JiangheCanonRetriever(repo_root, allowed_paths=allowed_paths, max_results=6, max_chars=6000, context_lines=1)
        tools = ProjectToolRegistry(store, clock=clock)
        base = PersistentDeepSeekTraderPrototype(trader_identity=trader_identity, store=store, retriever=retriever, tools=tools, runtime_contract=contract, clock=clock)
        return ReplayV01Runtime(base)
    return factory, trader_identity, contract


def _load_rows(*, parquet_root: Path, seal, sessions: dict):
    try:
        import pyarrow.dataset as ds
    except ImportError as error:
        raise RuntimeError("full mock dry run requires the pinned canonical pyarrow environment") from error
    if not parquet_root.is_dir():
        raise ValueError("canonical parquet root does not exist")
    all_bound_days = seal.slice.prior_history_days + seal.slice.burn_in_days + seal.slice.measurement_days
    partition_by_day = dict(zip(all_bound_days, seal.slice.partition_identities, strict=True))
    authority_identity = sessions[seal.slice.product]["identity"]
    dataset = ds.dataset(str(parquet_root), format="parquet", partitioning="hive")
    expression = (ds.field("product") == seal.slice.product) & (ds.field("concrete_contract") == seal.slice.concrete_contract)
    table = dataset.to_table(columns=["product","concrete_contract","trading_day","bar_start","bar_end","historical_available_at","open","high","low","close","volume","session_metadata_identity"], filter=expression)
    wanted = set(all_bound_days); row_session_ids: dict[date, set[str]] = defaultdict(set); rows = []
    for raw in table.to_pylist():
        day = raw["trading_day"]
        if day not in wanted:
            continue
        if raw["volume"] is None:
            raise ValueError("selected minute has missing canonical volume")
        row_session_id = raw["session_metadata_identity"]
        if not isinstance(row_session_id, str) or not row_session_id:
            raise ValueError("selected minute has no canonical session_metadata_identity")
        row_session_ids[day].add(row_session_id)
        rows.append(ReplayMinuteBar(product=raw["product"], concrete_contract=raw["concrete_contract"], trading_day=day, start=raw["bar_start"], end=raw["bar_end"], available_at=raw["historical_available_at"], open=raw["open"], high=raw["high"], low=raw["low"], close=raw["close"], volume=Decimal(raw["volume"]), partition_identity=partition_by_day[day], session_authority_identity=authority_identity))
    missing = wanted - set(row_session_ids)
    if missing:
        raise ValueError(f"canonical parquet has no rows for {len(missing)} bound days")
    if any(len(values) != 1 for values in row_session_ids.values()):
        raise ValueError("canonical row session metadata identity changes within a bound trading day")
    return tuple(sorted(rows, key=lambda item: item.start)), {day.isoformat(): sorted(values) for day, values in sorted(row_session_ids.items())}


def main() -> int:
    args = _parser().parse_args(); state_dir = args.state_dir.resolve(); output = args.output.resolve()
    if state_dir.exists() and any(state_dir.iterdir()):
        raise ValueError("mock dry-run state-dir must be new or empty; hidden reruns are forbidden")
    if output.exists():
        raise ValueError("mock dry-run output already exists; evidence must not be silently overwritten")
    state_dir.mkdir(parents=True, exist_ok=True)
    calendar_path = REPO_ROOT/"docs/evidence/CANONICAL_TRADING_CALENDAR.json"; sessions_path = REPO_ROOT/"docs/evidence/CANONICAL_SESSION_SCHEDULES.json"; e07_path = REPO_ROOT/"docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json"; corpus_path = REPO_ROOT/"docs/evidence/CANONICAL_CORPUS_IDENTITY.json"; revalidation_path = REPO_ROOT/"docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json"
    seal = select_and_seal_revalidated_exact_v0_1_slice(manifest_path=args.manifest, revalidation_path=revalidation_path, trading_calendar_path=calendar_path, session_schedule_path=sessions_path, e07_path=e07_path, corpus_identity_path=corpus_path)
    calendar_payload = _load_json(calendar_path); session_payload = _load_json(sessions_path); calendar, night_closed, _ = _parse_calendar(calendar_payload); sessions = session_payload["products"]
    prior = seal.slice.prior_history_days; replay_days = seal.slice.burn_in_days + seal.slice.measurement_days; all_bound_days = prior + replay_days
    windows = governed_windows_for_days(product=seal.slice.product, replay_days=all_bound_days, trading_calendar=calendar, night_closed_days=night_closed, session_schedule=sessions)
    rows, row_session_ids = _load_rows(parquet_root=args.parquet_root, seal=seal, sessions=sessions); replay_windows = tuple(item for item in windows if item.trading_day in replay_days); replay_rows = tuple(item for item in rows if item.trading_day in replay_days)
    preflight = build_fixed_5m_preflight(product=seal.slice.product, concrete_contract=seal.slice.concrete_contract, replay_days=replay_days, windows=replay_windows, minute_bars=replay_rows)
    context_index = CanonicalCausalContextIndex.build(product=seal.slice.product, concrete_contract=seal.slice.concrete_contract, windows=windows, minute_bars=rows)
    steps = tuple(build_governed_wake_step(wake, context_bars=context_index.context_for_wake(wake)) for wake in preflight.wake_bars)
    if len(steps) != preflight.expected_wake_count:
        raise ValueError("governed step count differs from fixed-5m wake count")
    runtime_factory, trader_identity, runtime_contract = _build_runtime_factory(repo_root=REPO_ROOT, state_dir=state_dir, causal_policy_identity=context_policy_identity())
    transport = DeterministicWaitTransport(); orchestrator = ReplayV01Orchestrator(runtime_factory=runtime_factory, clock=ReplayClock(current_time=steps[0].wake_bar.open_time), slice_=seal.slice, transport=transport, state_dir=state_dir)
    try:
        summary = drive_full_mock_replay(orchestrator=orchestrator, slice_=seal.slice, steps=steps, transport=transport)
        exported = orchestrator.runtime.portable_export(); audit_events = exported.get("audit", []); audit_counts = Counter(str(item.get("event_kind")) for item in audit_events if isinstance(item, dict))
        payload = {
            "status":"PASS","exact_slice_seal_identity":seal.identity,"base_exact_slice_seal_identity":seal.base_seal.identity,"slice_identity":seal.slice.identity,"canonical_corpus_identity":seal.canonical_corpus_identity,"raw_manifest_root_identity":seal.raw_manifest_root_identity,"revalidation_identity":seal.revalidation_identity,"qualified_partition_count":seal.qualified_partition_count,"excluded_partition_count":seal.excluded_partition_count,"trading_calendar_identity":seal.trading_calendar_identity,"session_authority_root_identity":seal.session_authority_root_identity,"e07_schedule_identity":seal.e07_schedule_identity,"product":seal.slice.product,"concrete_contract":seal.slice.concrete_contract,"prior_history_days":[item.isoformat() for item in prior],"burn_in_days":[item.isoformat() for item in seal.slice.burn_in_days],"measurement_days":[item.isoformat() for item in seal.slice.measurement_days],"canonical_fixed_5m_preflight_identity":preflight.identity,"context_policy_identity":context_index.policy_identity,"context_index_identity":context_index.identity,"constructed_bar_counts":context_index.bar_counts(),"trader_identity":trader_identity.identity,"runtime_contract_identity":runtime_contract.identity,"mock_transport_identity":transport.provider_identity,"full_mock_dry_run":summary.to_payload(),"audit_event_counts":dict(sorted(audit_counts.items())),"audit_event_count":len(audit_events),"hypothesis_revision_export":exported.get("hypothesis_revisions", {}),"canonical_row_session_metadata_identities":row_session_ids,"provider_call_authorized":False,
        }
    finally:
        orchestrator.runtime.close()
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)+"\n"; output.parent.mkdir(parents=True, exist_ok=True); partial = output.with_name(output.name+".partial")
    try:
        partial.write_text(encoded, encoding="utf-8"); partial.replace(output)
    finally:
        if partial.exists(): partial.unlink()
    sys.stdout.write(encoded); return 0

if __name__ == "__main__":
    raise SystemExit(main())
