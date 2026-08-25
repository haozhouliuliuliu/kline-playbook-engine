#!/usr/bin/env python3
"""Run exactly one V0.3 matched capability slot behind the durable remote lane.

This command is intentionally single-slot and provider-selectable only. The caller
can never choose slot identity, remote ref, model, token ceiling or timeout; all of
those are frozen by the deterministic V0.3 plan and the committed Owner authority.

This worker never executes this command against a real provider. The tool is the
executable machinery that the project brain may run after review/merge.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_prespend_runtime import (
    DEEPSEEK_VISION_SPEC,
    KIMI_K3_SPEC,
    MINIMAX_M3_SPEC,
    SelectedJiangheContextArtifact,
    load_current_repository_rate_card,
    load_owner_paid_call_authorization,
)
from src.jianghe_stage_a_frozen_stimulus import build_frozen_stage_a_stimulus
from src.jianghe_v03_live_lane import (
    DEFAULT_REMOTE_REF,
    V03GitRemoteLedgerStore,
    V03RemoteExecutionLedger,
)
from src.jianghe_v03_plan import (
    build_v03_frozen_plan,
    pretty_plan_bytes,
)
from src.jianghe_v03_runtime import (
    V03_PROVIDER_CONFIGS,
    V03AttemptIdentity,
    V03BudgetLedger,
    V03CapabilityAdapter,
    V03CommonExamIdentity,
    V03ProviderInferenceConfig,
    V03ProviderTransport,
    V03Request,
    V03TerminalStatus,
    v03_capability_answer_contract_identity,
    v03_slot_identity,
)

SPEC_BY_PROVIDER = {
    "KIMI": KIMI_K3_SPEC,
    "DEEPSEEK": DEEPSEEK_VISION_SPEC,
    "MINIMAX": MINIMAX_M3_SPEC,
}
CONFIG_BY_PROVIDER = {config.provider_id: config for config in V03_PROVIDER_CONFIGS}

RED_EXIT_STATUSES = frozenset({
    V03TerminalStatus.INFRASTRUCTURE_FAILURE.value,
    V03TerminalStatus.TRANSPORT_FAILURE.value,
    V03TerminalStatus.TRANSPORT_HTTP_ERROR.value,
    V03TerminalStatus.PROVIDER_RESPONSE_MALFORMED.value,
})


def _load_prompt_package() -> tuple[str, str]:
    path = ROOT / "docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_3.json"
    package = json.loads(path.read_text(encoding="utf-8"))
    return package["system_prompt"], package["decision_prompt"]


def _build_request(
    provider_id: str,
    plan: dict[str, object],
    now: datetime,
) -> tuple[V03Request, V03ProviderInferenceConfig, V03BudgetLedger, object, object]:
    config = CONFIG_BY_PROVIDER[provider_id]
    spec = SPEC_BY_PROVIDER[provider_id]
    system_prompt, decision_prompt = _load_prompt_package()
    stimulus = build_frozen_stage_a_stimulus()
    context = SelectedJiangheContextArtifact.from_fixture_id(plan["fixture_id"])
    common_exam = V03CommonExamIdentity(
        fixture_id=str(plan["fixture_id"]),
        stimulus_identity=stimulus.identity,
        source_observation_identity=stimulus.observation.identity.identity,
        point_in_time=stimulus.observation.identity.decision_time.isoformat(),
        system_prompt_sha256=hashlib.sha256(system_prompt.encode("utf-8")).hexdigest(),
        decision_prompt_sha256=hashlib.sha256(decision_prompt.encode("utf-8")).hexdigest(),
        capability_answer_contract_identity=v03_capability_answer_contract_identity(),
        selected_context_identity=context.identity,
        model_context_identity=context.model_payload()["model_context_identity"],
        structured_observation_identity=stimulus.structured.identity,
        png_sha256=stimulus.png_sha256,
        visual_artifact_identity=stimulus.visual_artifact_identity,
        renderer_config_identity=stimulus.renderer_config_identity,
    )
    attempt = V03AttemptIdentity(
        common_exam_identity=common_exam.identity,
        provider_inference_config_identity=config.identity,
        slot_identity=v03_slot_identity(provider_id),
        model_request_at=now.isoformat(),
    )
    request = V03Request(
        system_prompt=system_prompt,
        decision_prompt=decision_prompt,
        context=context,
        structured_observation=stimulus.structured,
        visual=stimulus.visual,
        common_exam_identity=common_exam,
        provider_config=config,
        attempt_identity=attempt,
        point_in_time=stimulus.observation.identity.decision_time.isoformat(),
    )
    rate_card = load_current_repository_rate_card(spec, now=now)
    budget = V03BudgetLedger()
    return request, config, budget, rate_card, spec


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", required=True, choices=("DEEPSEEK", "MINIMAX", "KIMI"))
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    plan = build_v03_frozen_plan()
    plan_sha256 = hashlib.sha256(pretty_plan_bytes(plan)).hexdigest()
    slot_identity = v03_slot_identity(args.provider)
    request, config, budget, rate_card, spec = _build_request(args.provider, plan, now)
    transport = V03ProviderTransport(config)

    store = V03GitRemoteLedgerStore(repository=ROOT, remote="origin", remote_ref=DEFAULT_REMOTE_REF)
    observed = store.load()
    if slot_identity in observed.ledger.snapshot().attempted_slots:
        raise SystemExit("V0.3 remote slot has already been attempted; automatic retry forbidden")

    authorization = load_owner_paid_call_authorization(now=now)
    if not authorization.permits(spec):
        raise SystemExit("current Owner authorization does not permit this V0.3 provider/model")

    ledger = observed.ledger
    reserved = ledger.append_start(
        now=now,
        provider_id=args.provider,
        slot_identity=slot_identity,
        request_identity=request.identity,
        worst_case_cny=_worst_case_from_plan(plan, args.provider),
    )
    reserved_bytes = reserved.to_bytes()
    start_head = store.compare_and_swap(
        expected_head=observed.head_sha,
        ledger_bytes=reserved_bytes,
    )

    terminal_status = V03TerminalStatus.INFRASTRUCTURE_FAILURE.value
    accounted = _worst_case_from_plan(plan, args.provider)
    evidence_payload = None
    try:
        evidence = transport.invoke(
            request,
            budget=budget,
            rate_card=rate_card,
            max_image_tokens=_image_bound_from_plan(plan, args.provider),
            now=now,
        )
    except Exception as error:
        terminal_status = V03TerminalStatus.TRANSPORT_FAILURE.value
        error_type = type(error).__name__
        print(json.dumps({"error_type": error_type, "status": terminal_status}, sort_keys=True))
    else:
        terminal_status = evidence.terminal_status
        accounted = Decimal(evidence.accounted_cny_for_hard_cap)
        adapter = V03CapabilityAdapter()
        try:
            answer = adapter.adapt(
                evidence.model_raw_final_answer or "",
                truncated=(evidence.finish_reason == "length"),
            )
        except Exception:
            terminal_status = V03TerminalStatus.FORMAT_ADAPTER_INCOMPATIBLE.value
        else:
            if terminal_status == V03TerminalStatus.COMPLETE_CAPABILITY_ANSWER.value:
                terminal_status = (
                    V03TerminalStatus.CAPABILITY_SCOREABLE.value
                    if answer.scoreable
                    else V03TerminalStatus.CAPABILITY_NOT_SCOREABLE.value
                )
        evidence_payload = evidence.to_durable(redact=(os.environ.get(config.api_key_env) or "",))

    evidence_identity = ""
    if evidence_payload is not None:
        evidence_identity = str(evidence_payload["evidence_identity"])
        evidence_bytes = (
            json.dumps(evidence_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
    else:
        evidence_bytes = None

    terminal = ledger.append_terminal(
        now=now,
        provider_id=args.provider,
        slot_identity=slot_identity,
        status=terminal_status,
        accounted_cny=accounted,
        evidence_identity=evidence_identity or "0" * 64,
        evidence_network_start_event_identity="0" * 64,
        evidence_terminal_event_identity="0" * 64,
    )
    terminal_bytes = terminal.to_bytes()
    evidence_artifacts = None
    if evidence_bytes is not None and evidence_identity:
        evidence_artifacts = {f"evidence-{evidence_identity}.json": evidence_bytes}
    terminal_head = store.compare_and_swap(
        expected_head=start_head,
        ledger_bytes=terminal_bytes,
        evidence_artifacts=evidence_artifacts,
    )
    print(json.dumps({
        "provider_id": args.provider,
        "slot_identity": slot_identity,
        "terminal_status": terminal_status,
        "accounted_cny": format(accounted, "f"),
        "evidence_identity": evidence_identity,
        "remote_start_head": start_head,
        "remote_terminal_head": terminal_head,
        "automatic_retry": "FORBIDDEN",
        "credential_value_exposed": False,
    }, ensure_ascii=False, sort_keys=True))
    return 1 if terminal_status in RED_EXIT_STATUSES else 0


def _worst_case_from_plan(plan: dict[str, object], provider_id: str) -> Decimal:
    for provider in plan["providers"]:
        if provider["provider_id"] == provider_id:
            return Decimal(provider["worst_case_reservation_cny"])
    raise KeyError(provider_id)


def _image_bound_from_plan(plan: dict[str, object], provider_id: str) -> int:
    for provider in plan["providers"]:
        if provider["provider_id"] == provider_id:
            return int(provider["image_input_bound_tokens"])
    raise KeyError(provider_id)


if __name__ == "__main__":
    raise SystemExit(main())
