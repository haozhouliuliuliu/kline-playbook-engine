#!/usr/bin/env python3
"""Execute exactly one frozen downloaded-Kline DeepSeek sample, without retry."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_downloaded_kline_pilot import PILOT_ID, identity, reconstruct_sample, verify_plan
from src.jianghe_prespend_runtime import DEEPSEEK_VISION_SPEC, SelectedJiangheContextArtifact, load_current_repository_rate_card, load_owner_paid_call_authorization
from src.jianghe_v03_runtime import DEEPSEEK_V03_CONFIG, V03AttemptIdentity, V03BudgetLedger, V03CapabilityAdapter, V03CommonExamIdentity, V03ProviderTransport, V03Request, V03TerminalStatus, v03_capability_answer_contract_identity

PLAN_PATH = ROOT / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_PLAN_V0_1.json"
PROMPT_PATH = ROOT / "docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_3.json"
REMOTE_REF = "refs/heads/downloaded-kline-pilot-state-v0-1"
LEDGER_FILE = "downloaded-kline-pilot-ledger-v0-1.json"
HISTORICAL_ACCOUNTED_CNY = Decimal("2.4886842")
HARD_CAP_CNY = Decimal("100")
_OID = re.compile(r"^[0-9a-f]{40,64}$")


def _run_git(args: list[str], input_bytes: bytes | None = None) -> bytes:
    environment = dict(os.environ)
    environment.pop("DEEPSEEK_API_KEY", None)
    environment.setdefault("GIT_AUTHOR_NAME", "Downloaded Kline Pilot Lane")
    environment.setdefault("GIT_AUTHOR_EMAIL", "downloaded-kline-pilot@invalid.local")
    environment.setdefault("GIT_COMMITTER_NAME", environment["GIT_AUTHOR_NAME"])
    environment.setdefault("GIT_COMMITTER_EMAIL", environment["GIT_AUTHOR_EMAIL"])
    completed = subprocess.run(["git", *args], cwd=ROOT, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment)
    if completed.returncode != 0:
        raise RuntimeError("Git remote pilot ledger operation failed")
    return completed.stdout


def _remote_head() -> str | None:
    output = _run_git(["ls-remote", "--heads", "origin", REMOTE_REF]).decode("ascii").strip()
    if not output:
        return None
    fields = output.split()
    if len(fields) != 2 or fields[1] != REMOTE_REF or not _OID.fullmatch(fields[0]):
        raise RuntimeError("remote pilot ledger ref is ambiguous")
    return fields[0]


def _tree(head: str | None) -> dict[str, str]:
    if head is None:
        return {}
    entries: dict[str, str] = {}
    for row in _run_git(["ls-tree", head]).decode("utf-8").splitlines():
        metadata, filename = row.split("\t", 1)
        mode, kind, oid = metadata.split()
        if mode != "100644" or kind != "blob" or not _OID.fullmatch(oid):
            raise RuntimeError("remote pilot ledger tree is invalid")
        if filename != LEDGER_FILE and re.fullmatch(r"evidence-[0-9a-f]{64}\.json", filename) is None:
            raise RuntimeError("remote pilot ledger tree contains an unsupported file")
        entries[filename] = oid
    return entries


def _read(head: str, filename: str) -> bytes:
    return _run_git(["show", f"{head}:{filename}"])


def _load_ledger(plan_identity: str) -> tuple[str | None, dict[str, object]]:
    head = _remote_head()
    if head is None:
        return None, {"schema_version": "downloaded-kline-pilot-remote-ledger-v0.1", "pilot_id": PILOT_ID, "pilot_plan_identity": plan_identity, "historical_project_accounted_cny": str(HISTORICAL_ACCOUNTED_CNY), "events": []}
    _run_git(["fetch", "--no-tags", "origin", f"{REMOTE_REF}:refs/downloaded-kline-pilot/observed"])
    raw = json.loads(_read(head, LEDGER_FILE).decode("utf-8"))
    if raw.get("pilot_id") != PILOT_ID or raw.get("pilot_plan_identity") != plan_identity:
        raise RuntimeError("remote pilot ledger plan binding mismatch")
    events = raw.get("events")
    if not isinstance(events, list):
        raise RuntimeError("remote pilot ledger events are malformed")
    previous = None
    starts: set[str] = set()
    terminals: set[str] = set()
    for sequence, event in enumerate(events, 1):
        if event.get("sequence") != sequence or event.get("previous_event_identity") != previous:
            raise RuntimeError("remote pilot ledger chain is invalid")
        declared = event.get("event_identity")
        payload = dict(event); payload.pop("event_identity", None)
        if declared != identity(payload):
            raise RuntimeError("remote pilot ledger event identity mismatch")
        slot = event.get("attempt_slot")
        if event.get("event_type") == "NETWORK_ATTEMPT_STARTED":
            if slot in starts:
                raise RuntimeError("remote pilot ledger has duplicate start")
            starts.add(slot)
        elif event.get("event_type") == "ATTEMPT_TERMINAL":
            if slot not in starts or slot in terminals:
                raise RuntimeError("remote pilot ledger terminal is unpaired")
            terminals.add(slot)
        else:
            raise RuntimeError("remote pilot ledger event type is invalid")
        previous = declared
    expected_evidence = {f'evidence-{event["evidence_identity"]}.json' for event in events if event.get("event_type") == "ATTEMPT_TERMINAL"}
    if set(_tree(head)) - {LEDGER_FILE} != expected_evidence:
        raise RuntimeError("remote pilot evidence inventory mismatch")
    return head, raw


def _accounted(ledger: dict[str, object]) -> Decimal:
    total = HISTORICAL_ACCOUNTED_CNY
    starts: dict[str, Decimal] = {}
    for event in ledger["events"]:
        slot = str(event["attempt_slot"])
        if event["event_type"] == "NETWORK_ATTEMPT_STARTED":
            starts[slot] = Decimal(str(event["precall_conservative_reservation_cny"]))
        else:
            total += Decimal(str(event["accounted_cny_for_hard_cap"]))
            starts.pop(slot, None)
    return total + sum(starts.values(), Decimal("0"))


def _append(ledger: dict[str, object], values: dict[str, object]) -> dict[str, object]:
    updated = json.loads(json.dumps(ledger))
    events = updated["events"]
    event = {
        "sequence": len(events) + 1,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "previous_event_identity": None if not events else events[-1]["event_identity"],
        **values,
    }
    event["event_identity"] = identity(event)
    events.append(event)
    return updated


def _persist(expected_head: str | None, ledger: dict[str, object], evidence: dict[str, object] | None = None) -> str:
    if _remote_head() != expected_head:
        raise RuntimeError("remote pilot ledger changed before CAS")
    entries = _tree(expected_head)
    files = {LEDGER_FILE: (json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")}
    if evidence is not None:
        files[f'evidence-{evidence["evidence_identity"]}.json'] = (json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    for filename, content in files.items():
        oid = _run_git(["hash-object", "-w", "--stdin"], content).decode("ascii").strip()
        if not _OID.fullmatch(oid):
            raise RuntimeError("Git returned invalid pilot evidence blob identity")
        entries[filename] = oid
    tree_input = "".join(f"100644 blob {oid}\t{name}\n" for name, oid in sorted(entries.items())).encode("utf-8")
    tree_oid = _run_git(["mktree"], tree_input).decode("ascii").strip()
    args = ["commit-tree", tree_oid]
    if expected_head is not None:
        args.extend(["-p", expected_head])
    args.extend(["-m", "pilot: persist downloaded-Kline execution state"])
    commit = _run_git(args).decode("ascii").strip()
    _run_git(["push", "--porcelain", "origin", f"{commit}:{REMOTE_REF}"])
    if _remote_head() != commit:
        raise RuntimeError("remote pilot ledger verification failed after CAS")
    return commit


def _request(sample: dict[str, object], now: datetime, attempt_slot: str) -> tuple[V03Request, V03ProviderTransport, object]:
    prompt = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
    context = SelectedJiangheContextArtifact.from_fixture_id("JH-FIX-C-001")
    observation, structured, visual, hashes = reconstruct_sample(sample)
    for name, value in hashes.items():
        if sample[name] != value:
            raise RuntimeError(f"frozen sample {name} drifted")
    common = V03CommonExamIdentity(
        fixture_id=str(sample["sample_id"]), stimulus_identity=str(sample["sample_identity"]),
        source_observation_identity=observation.identity.identity,
        point_in_time=str(sample["decision_time"]),
        system_prompt_sha256=sha256(prompt["system_prompt"].encode("utf-8")).hexdigest(),
        decision_prompt_sha256=sha256(prompt["decision_prompt"].encode("utf-8")).hexdigest(),
        capability_answer_contract_identity=v03_capability_answer_contract_identity(),
        selected_context_identity=context.identity, model_context_identity=context.model_payload()["model_context_identity"],
        structured_observation_identity=structured.identity, png_sha256=visual.content_sha256,
        visual_artifact_identity=str(sample["visual_artifact_identity"]), renderer_config_identity=visual.renderer_identity,
    )
    attempt = V03AttemptIdentity(common.identity, DEEPSEEK_V03_CONFIG.identity, attempt_slot, now.isoformat())
    request = V03Request(prompt["system_prompt"], prompt["decision_prompt"], context, structured, visual, common, DEEPSEEK_V03_CONFIG, attempt, str(sample["decision_time"]))
    transport = V03ProviderTransport(DEEPSEEK_V03_CONFIG)
    rate_card = load_current_repository_rate_card(DEEPSEEK_VISION_SPEC, now=now)
    return request, transport, rate_card


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-id", required=True, choices=tuple(f"DKL-DS-{index:03d}" for index in range(1, 6)))
    args = parser.parse_args()
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8")); verify_plan(plan)
    sample = next(item for item in plan["samples"] if item["sample_id"] == args.sample_id)
    attempt_slot = f"DOWNLOADED_KLINE_V0_1:DEEPSEEK:{args.sample_id}:001"
    head, ledger = _load_ledger(str(plan["pilot_plan_identity"]))
    if any(event["attempt_slot"] == attempt_slot for event in ledger["events"]):
        raise SystemExit("sample attempt was already started; automatic retry is forbidden")
    now = datetime.now(timezone.utc)
    authorization = load_owner_paid_call_authorization(now=now)
    if not authorization.permits(DEEPSEEK_VISION_SPEC):
        raise SystemExit("current Owner paid-call authorization does not permit DeepSeek")
    request, transport, rate_card = _request(sample, now, attempt_slot)
    text_bound = transport.conservative_text_input_token_bound(request)
    million = Decimal("1000000")
    reservation = (Decimal(text_bound + int(plan["image_input_bound_tokens"])) * Decimal(rate_card.input_per_million) + Decimal(DEEPSEEK_V03_CONFIG.max_output_tokens) * Decimal(rate_card.output_per_million)) / million
    if _accounted(ledger) + reservation > HARD_CAP_CNY:
        raise SystemExit("next pilot reservation would exceed CNY100 hard cap")
    started = _append(ledger, {
        "event_type": "NETWORK_ATTEMPT_STARTED", "sample_id": args.sample_id,
        "attempt_slot": attempt_slot, "request_identity": request.identity,
        "precall_conservative_reservation_cny": format(reservation, "f"),
    })
    start_head = _persist(head, started)
    budget = V03BudgetLedger(historical_accounted_cny=_accounted(ledger))
    terminal_status = V03TerminalStatus.INFRASTRUCTURE_FAILURE.value
    accounted = reservation
    evidence_payload: dict[str, object]
    try:
        invocation = transport.invoke(request, budget=budget, rate_card=rate_card, max_image_tokens=int(plan["image_input_bound_tokens"]), now=now)
        normalized = V03CapabilityAdapter().adapt(invocation.model_raw_final_answer or "", truncated=invocation.finish_reason == "length")
        terminal_status = V03TerminalStatus.CAPABILITY_SCOREABLE.value if normalized.scoreable else V03TerminalStatus.CAPABILITY_NOT_SCOREABLE.value
        accounted = Decimal(invocation.accounted_cny_for_hard_cap)
        evidence_payload = invocation.to_durable(redact=(os.environ.get("DEEPSEEK_API_KEY") or "",))
        evidence_payload.update({
            "http_status": 200, "sample_id": args.sample_id, "sample_identity": sample["sample_identity"],
            "decision_time": sample["decision_time"], "contract": sample["concrete_contract"],
            "source_data_identity": sample["source_1m_input_identity"], "png_sha256": sample["png_sha256"],
            "structured_observation_identity": sample["structured_observation_identity"],
            "normalized_evaluation_view": {
                "identity": normalized.identity, "family": normalized.family, "action": normalized.action,
                "direction": normalized.direction, "missing_headings": list(normalized.missing_headings),
                "invalid_enum_fields": list(normalized.invalid_enum_fields), "scoreable": normalized.scoreable,
            },
            "request_id": invocation.provider_request_id, "output_state": invocation.final_content_state,
            "prompt_tokens": None if invocation.usage is None else invocation.usage.prompt_tokens,
            "cached_tokens": None if invocation.usage is None else invocation.usage.cached_input_tokens,
            "image_tokens": None if invocation.usage is None else invocation.usage.image_tokens,
            "reasoning_tokens": None if invocation.usage is None else invocation.usage.reasoning_tokens,
            "output_tokens": None if invocation.usage is None else invocation.usage.completion_tokens,
        })
    except Exception as error:
        evidence_payload = {
            "artifact_schema_version": "downloaded-kline-pilot-failure-evidence-v0.1",
            "sample_id": args.sample_id, "sample_identity": sample["sample_identity"], "attempt_slot": attempt_slot,
            "network_started": True, "automatic_retry": 0, "error_type": type(error).__name__,
            "http_status": None, "model_raw_final_answer": None, "normalized_evaluation_view": None,
            "requested_model_id": DEEPSEEK_V03_CONFIG.model_id, "resolved_model_id": None,
            "request_id": None, "finish_reason": None, "output_state": "FAILED",
            "prompt_tokens": None, "cached_tokens": None, "image_tokens": None,
            "reasoning_tokens": None, "output_tokens": None, "latency_ms": None,
            "precall_conservative_reservation_cny": format(reservation, "f"),
            "postcall_calculated_cny": format(reservation, "f"), "provider_reported_billed_cny": None,
            "accounted_cny_for_hard_cap": format(reservation, "f"),
            "hidden_reasoning_persisted": False, "raw_provider_body_persisted": False,
        }
    evidence_payload["terminal_status"] = terminal_status
    payload_for_identity = dict(evidence_payload); payload_for_identity.pop("evidence_identity", None)
    evidence_payload["evidence_identity"] = identity(payload_for_identity)
    terminal = _append(started, {
        "event_type": "ATTEMPT_TERMINAL", "sample_id": args.sample_id, "attempt_slot": attempt_slot,
        "request_identity": request.identity, "terminal_status": terminal_status,
        "accounted_cny_for_hard_cap": format(accounted, "f"), "evidence_identity": evidence_payload["evidence_identity"],
    })
    terminal_head = _persist(start_head, terminal, evidence_payload)
    print(json.dumps({"sample_id": args.sample_id, "attempt_slot": attempt_slot, "terminal_status": terminal_status, "accounted_cny": format(accounted, "f"), "evidence_identity": evidence_payload["evidence_identity"], "remote_start_head": start_head, "remote_terminal_head": terminal_head, "automatic_retries": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
