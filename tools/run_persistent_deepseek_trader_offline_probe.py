#!/usr/bin/env python3
"""Run the local, no-provider-call persistent trader prototype probe.

This is intentionally a project-core probe, not a DeepSeek provider smoke test.  It
uses the real project observation types, deterministic PNG renderer, Jianghe source
retrieval, local SQLite state, project tools, strict normalizer, guards and audit.
There is no provider transport in this program.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.deepseek_mechanical_guards import assert_no_4h_exact_volume_reconciliation
from src.jianghe_ai_trader import (
    ChartRender,
    JiangheAITraderIdentity,
    JiangheObservation,
    ObservationBar,
    ObservationIdentity,
)
from src.jianghe_canon_retrieval import JiangheCanonRetriever
from src.jianghe_response_normalizer import NORMALIZER_IDENTITY, RESPONSE_SCHEMA_VERSION
from src.jianghe_visual_renderer import (
    ARTIFACT_KIND,
    PNG_MIME,
    RENDERER_VERSION,
    JiangheVisualRenderer,
    VisualObservationSpec,
    VisualPanel,
)
from src.persistent_deepseek_runtime import (
    ACTIVE_TIMEFRAMES,
    CURRENT_MODEL,
    DeepSeekHarnessRuntimeContract,
    PersistentDeepSeekTraderPrototype,
    ProjectToolRegistry,
    default_jianghe_canon_paths,
)
from src.persistent_trader_store import PersistentTraderStore


SYSTEM_PROMPT = (
    "OFFLINE_PROBE_ONLY_NO_PROVIDER_CALL: You are the governed Jianghe DeepSeek futures trader."
)
DECISION_PROMPT = (
    "OFFLINE_PROBE_ONLY_NO_PROVIDER_CALL: Return only JIANGHE_RUNTIME_RESPONSE_V0_1."
)


def _bars(as_of: datetime) -> tuple[ObservationBar, ...]:
    durations = {
        "4H": timedelta(hours=4),
        "1H": timedelta(hours=1),
        "15m": timedelta(minutes=15),
        "5m": timedelta(minutes=5),
    }
    result: list[ObservationBar] = []
    for index, timeframe in enumerate(ACTIVE_TIMEFRAMES):
        duration = durations[timeframe]
        result.append(
            ObservationBar(
                timeframe=timeframe,
                open_time=as_of - duration,
                close_time=as_of,
                available_at=as_of,
                open_price=str(3100 + index * 4),
                high_price=str(3120 + index * 4),
                low_price=str(3090 + index * 4),
                close_price=str(3110 + index * 4),
                volume=str(1000 + index * 100),
                is_closed=True,
            )
        )
    return tuple(result)


def _render_charts(
    *,
    state_dir: Path,
    bars: tuple[ObservationBar, ...],
    as_of: datetime,
) -> tuple[ChartRender, ...]:
    renderer = JiangheVisualRenderer()
    charts: list[ChartRender] = []
    by_timeframe = {bar.timeframe: bar for bar in bars}
    chart_dir = state_dir / "charts"
    chart_dir.mkdir(parents=True, exist_ok=True)

    for timeframe in ACTIVE_TIMEFRAMES:
        bar = by_timeframe[timeframe]
        artifact = renderer.render(
            VisualObservationSpec(
                product="rb",
                concrete_contract="SHFE.RB2605",
                as_of=as_of,
                panels=(VisualPanel(timeframe=timeframe, bars=(bar,)),),
            )
        )
        (chart_dir / f"{timeframe}.png").write_bytes(artifact.png_bytes)
        (chart_dir / f"{timeframe}.manifest.json").write_text(
            artifact.manifest_json(), encoding="utf-8"
        )
        charts.append(
            ChartRender(
                renderer_identity=RENDERER_VERSION,
                timeframe=timeframe,
                window_definition="OFFLINE_PROTOTYPE_SINGLE_VISIBLE_BAR_FIXTURE",
                current_time=as_of,
                render_content_hash=artifact.png_sha256,
                partial_bar_marked=False,
                renderer_config_identity=artifact.renderer_config_identity,
                artifact_kind=ARTIFACT_KIND,
                mime_type=PNG_MIME,
            )
        )
    return tuple(charts)


def _valid_response() -> str:
    return json.dumps(
        {
            "schema_version": RESPONSE_SCHEMA_VERSION,
            "family": "NONE",
            "action": "WAIT",
            "direction": "NONE",
            "attention_mode": "SCAN",
            "decision_state": "offline_probe_wait",
            "rationale": "Offline fixture only; no provider call occurred.",
            "declared_unknown": [],
            "principle_references": [],
            "source_references": [],
            "numeric_claims": [],
        },
        ensure_ascii=False,
        sort_keys=True,
    )


def run_probe(*, repo_root: Path, state_dir: Path) -> dict[str, object]:
    repo_root = repo_root.resolve()
    state_dir = state_dir.resolve()
    state_dir.mkdir(parents=True, exist_ok=True)

    allowed_paths = default_jianghe_canon_paths(repo_root)
    if not allowed_paths:
        raise RuntimeError("no current Jianghe canon artifacts were found")
    retriever = JiangheCanonRetriever(
        repo_root,
        allowed_paths=allowed_paths,
        max_results=6,
        max_chars=6000,
        context_lines=1,
    )
    retrieval_hits = retriever.search("UNKNOWN")
    if not retrieval_hits:
        raise RuntimeError("bounded Jianghe retrieval returned no attributable hit for UNKNOWN")

    as_of = datetime(2026, 1, 5, 8, 0, tzinfo=timezone.utc)
    bars = _bars(as_of)
    charts = _render_charts(state_dir=state_dir, bars=bars, as_of=as_of)
    observation = JiangheObservation(
        identity=ObservationIdentity(
            decision_time=as_of,
            exchange_time=as_of,
            product="rb",
            concrete_contract="SHFE.rb2605",
            mapping_identity="OFFLINE_PROBE_MAPPING_V0_1",
            session_identity="OFFLINE_PROBE_SESSION_V0_1",
        ),
        bars=bars,
        charts=charts,
        visible_metadata=(("probe_mode", "OFFLINE_NO_PROVIDER_CALL"),),
    )

    contract = DeepSeekHarnessRuntimeContract.from_prompts(
        system_prompt=SYSTEM_PROMPT,
        decision_prompt=DECISION_PROMPT,
    )
    renderer = JiangheVisualRenderer()
    trader_identity = JiangheAITraderIdentity(
        knowledge_pack_identity=retriever.identity,
        primary_branch_registry_identity="OFFLINE_PROBE_PRIMARY_REGISTRY_V0_1",
        interpretation_set_identity="OFFLINE_PROBE_INTERPRETATION_SET_V0_1",
        model_provider="deepseek",
        model_id_version=CURRENT_MODEL,
        system_prompt_identity=contract.system_prompt_sha256,
        decision_prompt_identity=contract.decision_prompt_sha256,
        context_selection_policy_identity="BOUNDED_ATTRIBUTABLE_CONTEXT_V0_1",
        memory_policy_identity="PROJECT_OWNED_SQLITE_PERSISTENCE_V0_1",
        chart_renderer_identity=f"{RENDERER_VERSION}:{renderer.config.identity}",
        observation_schema_version=observation.schema_version,
        wake_policy_version="OFFLINE_PROBE_NO_WAKE_LOOP_V0_1",
        decision_schema_version=RESPONSE_SCHEMA_VERSION,
        runtime_normalizer_identity=NORMALIZER_IDENTITY,
        hard_execution_envelope_identity="OFFLINE_NO_EXECUTION_ENVELOPE_V0_1",
        inference_configuration=(("max_retries", "0"), ("provider_call_authorized", "false")),
        tool_capability_set=("jianghe_kline_snapshot",),
        source_family_scope=("A", "B", "C", "D"),
    )

    db_path = state_dir / f"trader-{trader_identity.identity}.sqlite3"
    store = PersistentTraderStore(db_path, trader_identity=trader_identity.identity)
    tools = ProjectToolRegistry(store)
    bars_by_tf = {bar.timeframe: bar for bar in bars}

    def kline_snapshot(args: dict[str, object]) -> dict[str, object]:
        timeframe = str(args.get("timeframe", "5m"))
        if timeframe not in bars_by_tf:
            raise ValueError(f"unsupported timeframe: {timeframe}")
        bar = bars_by_tf[timeframe]
        return {
            "source": "PROJECT_CAUSAL_OFFLINE_PROBE",
            "symbol": str(args.get("symbol", observation.identity.concrete_contract)),
            "timeframe": timeframe,
            "open_time": bar.open_time.isoformat(),
            "close_time": bar.close_time.isoformat(),
            "open": bar.open_price,
            "high": bar.high_price,
            "low": bar.low_price,
            "close": bar.close_price,
            "volume": bar.volume,
            "is_closed": bar.is_closed,
        }

    tools.register("jianghe_kline_snapshot", kline_snapshot)
    runtime = PersistentDeepSeekTraderPrototype(
        trader_identity=trader_identity,
        store=store,
        retriever=retriever,
        tools=tools,
        runtime_contract=contract,
    )

    run_id = uuid4().hex
    runtime.mutate_working_memory(
        field_name="current_market_hypothesis",
        new_value="OFFLINE_PROBE_WAIT_FOR_GOVERNED_CONFIRMATION",
        reason="LOCAL_OFFLINE_PROTOTYPE_PROBE",
        observation_identity=observation.identity.identity,
    )
    journal_identity = runtime.append_journal(
        entry_id=f"journal-{run_id}",
        body="Offline probe reflection; not market fact or policy.",
        observation_identity=observation.identity.identity,
        tags=("offline-probe",),
    )
    hypothesis_identity = runtime.put_hypothesis(
        hypothesis_id=f"hypothesis-{run_id}",
        statement="Offline probe candidate hypothesis; not executable policy.",
        falsifier="Any counterexample is sufficient to keep this candidate unpromoted.",
        evidence_references=(retrieval_hits[0].retrieval_identity,),
    )

    request = runtime.prepare_model_request(
        observation=observation,
        retrieval_query="UNKNOWN",
        system_prompt=SYSTEM_PROMPT,
        decision_prompt=DECISION_PROMPT,
    )
    tool_result = tools.call(
        "jianghe_kline_snapshot",
        {"symbol": observation.identity.concrete_contract, "timeframe": "5m"},
        observation_identity=observation.identity.identity,
        request_id=request.request_id,
    )
    normalized = runtime.record_model_response(
        request_id=request.request_id,
        raw_response=_valid_response(),
    )

    invalid_request = runtime.prepare_model_request(
        observation=observation,
        retrieval_query="UNKNOWN",
        system_prompt=SYSTEM_PROMPT,
        decision_prompt=DECISION_PROMPT,
    )
    invalid_payload = json.loads(_valid_response())
    invalid_payload["action"] = "HOLD"
    enum_rejected = False
    try:
        runtime.record_model_response(
            request_id=invalid_request.request_id,
            raw_response=json.dumps(invalid_payload, ensure_ascii=False),
        )
    except ValueError:
        enum_rejected = True

    four_hour_reconciliation_rejected = False
    try:
        assert_no_4h_exact_volume_reconciliation(
            {"timeframe": "4H", "volume_reconciliation": {"component_volume_sum": "123"}}
        )
    except ValueError:
        four_hour_reconciliation_rejected = True

    pre_restart_audit_count = len(store.list_audit())
    store.close()

    reopened = PersistentTraderStore(db_path, trader_identity=trader_identity.identity)
    try:
        restored_memory = reopened.load_working_memory()
        exported = reopened.portable_export()
        audit = reopened.list_audit()
    finally:
        reopened.close()

    audit_kinds = [event.event_kind for event in audit]
    checks = {
        "exact_model_contract": contract.model_id == CURRENT_MODEL and contract.general_max_retries == 0,
        "provider_call_locked": contract.provider_call_authorized is False and not hasattr(runtime, "call_provider"),
        "causal_four_timeframe_observation": set(observation.timeframes) == set(ACTIVE_TIMEFRAMES),
        "four_png_charts_exposed": len(observation.charts) == 4 and all(chart.mime_type == "image/png" for chart in observation.charts),
        "working_memory_survived_restart": restored_memory.current_market_hypothesis == "OFFLINE_PROBE_WAIT_FOR_GOVERNED_CONFIRMATION",
        "bounded_attributable_jianghe_retrieval": 1 <= len(retrieval_hits) <= 6 and sum(len(hit.excerpt) for hit in retrieval_hits) <= 6000,
        "project_kline_tool_audited": tool_result["source"] == "PROJECT_CAUSAL_OFFLINE_PROBE" and "TOOL_CALL" in audit_kinds and "TOOL_RESULT" in audit_kinds,
        "journal_persisted_separately": any(item["identity"] == journal_identity for item in exported["journal"]),
        "hypothesis_persisted_non_executable": any(item["identity"] == hypothesis_identity and item["executable_policy"] is False for item in exported["hypotheses"]),
        "request_response_reconstructable": "MODEL_REQUEST_PREPARED_OFFLINE" in audit_kinds and "MODEL_RESPONSE_RAW" in audit_kinds and "MODEL_RESPONSE_NORMALIZED" in audit_kinds,
        "strict_output_enum_enforcement": enum_rejected and "MODEL_RESPONSE_REJECTED" in audit_kinds,
        "no_4h_exact_volume_reconciliation": four_hour_reconciliation_rejected,
        "project_state_portable": exported["harness_opaque_state_included"] is False,
    }
    if not all(checks.values()):
        failed = sorted(name for name, passed in checks.items() if not passed)
        raise RuntimeError(f"offline prototype probe failed checks: {failed}")

    summary = {
        "probe": "MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1_OFFLINE_CORE",
        "provider_call_made": False,
        "model": CURRENT_MODEL,
        "runtime_contract_identity": contract.identity,
        "trader_identity": trader_identity.identity,
        "retriever_identity": retriever.identity,
        "observation_identity": observation.identity.identity,
        "database_path": str(db_path),
        "chart_directory": str(state_dir / "charts"),
        "retrieval_identities": [hit.retrieval_identity for hit in retrieval_hits],
        "request_id": request.request_id,
        "normalized_decision_identity": normalized.identity,
        "pre_restart_audit_count": pre_restart_audit_count,
        "post_restart_audit_count": len(audit),
        "portable_journal_count": len(exported["journal"]),
        "portable_hypothesis_count": len(exported["hypotheses"]),
        "checks": checks,
    }
    (state_dir / "offline-probe-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="kline-playbook-engine checkout (default: repository containing this script)",
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        default=Path.home() / ".kline-playbook-engine" / "prototype-v0-1",
        help="local project-owned persistent state directory",
    )
    args = parser.parse_args()
    summary = run_probe(repo_root=args.repo_root, state_dir=args.state_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
