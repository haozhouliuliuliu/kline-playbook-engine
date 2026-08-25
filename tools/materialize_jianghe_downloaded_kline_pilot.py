#!/usr/bin/env python3
"""Materialize secret-safe remote pilot evidence and fixed adjudication."""

from __future__ import annotations

from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_downloaded_kline_pilot import identity, verify_plan

REMOTE_REF = "refs/heads/downloaded-kline-pilot-state-v0-1"
LEDGER_FILE = "downloaded-kline-pilot-ledger-v0-1.json"
HISTORICAL_ACCOUNTED = Decimal("2.4886842")

ADJUDICATIONS = {
    "DKL-DS-001": {"factual_error_count": 0, "visual_structured_contradiction": False, "unsupported_numeric_claim_count": 0, "invented_rule_count": 0, "unsupported_jianghe_claim_count": 0, "no_trade_discipline": "PASS", "family_internal_consistency": "PASS", "notes": []},
    "DKL-DS-002": {"factual_error_count": 0, "visual_structured_contradiction": False, "unsupported_numeric_claim_count": 0, "invented_rule_count": 0, "unsupported_jianghe_claim_count": 0, "no_trade_discipline": "PASS", "family_internal_consistency": "PASS", "notes": []},
    "DKL-DS-003": {
        "factual_error_count": 2, "visual_structured_contradiction": False,
        "unsupported_numeric_claim_count": 2, "invented_rule_count": 0,
        "unsupported_jianghe_claim_count": 0, "no_trade_discipline": "PASS",
        "family_internal_consistency": "PASS",
        "notes": [
            "回答把倒数第二根 5m（14:50-14:55，O20695/H20710/L20690/C20710/V29）误称为最后一根；实际最后一根为 14:55-15:00，O20710/H20710/L20700/C20710/V20。",
            "回答声称最后 15m 的三根 5m 成交量为 5+5+29=39 并与 V54 矛盾；实际为 5+29+20=54，不存在该量能矛盾。",
        ],
    },
    "DKL-DS-004": {"factual_error_count": 0, "visual_structured_contradiction": False, "unsupported_numeric_claim_count": 0, "invented_rule_count": 0, "unsupported_jianghe_claim_count": 0, "no_trade_discipline": "PASS", "family_internal_consistency": "PASS", "notes": []},
    "DKL-DS-005": {"factual_error_count": 0, "visual_structured_contradiction": False, "unsupported_numeric_claim_count": 0, "invented_rule_count": 0, "unsupported_jianghe_claim_count": 0, "no_trade_discipline": "PASS", "family_internal_consistency": "PASS", "notes": []},
}


def _git(*args: str) -> bytes:
    completed = subprocess.run(["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode:
        raise RuntimeError("cannot read downloaded-Kline remote evidence")
    return completed.stdout


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    _git("fetch", "--no-tags", "origin", f"+{REMOTE_REF}:refs/downloaded-kline-pilot/materialize")
    head = _git("rev-parse", "refs/downloaded-kline-pilot/materialize").decode("ascii").strip()
    ledger = json.loads(_git("show", f"{head}:{LEDGER_FILE}"))
    plan = json.loads((ROOT / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_PLAN_V0_1.json").read_text(encoding="utf-8"))
    verify_plan(plan)
    terminals = [event for event in ledger["events"] if event["event_type"] == "ATTEMPT_TERMINAL"]
    if len(terminals) != 5 or {item["sample_id"] for item in terminals} != set(ADJUDICATIONS):
        raise ValueError("remote pilot does not contain exactly five terminal samples")
    plan_samples = {item["sample_id"]: item for item in plan["samples"]}
    cases = []
    for terminal in terminals:
        evidence = json.loads(_git("show", f'{head}:evidence-{terminal["evidence_identity"]}.json'))
        sample_id = terminal["sample_id"]
        normalized = evidence["normalized_evaluation_view"]
        case = {
            "schema_version": "jianghe-downloaded-kline-pilot-case-v0.1",
            "pilot_id": plan["pilot_id"], "pilot_plan_identity": plan["pilot_plan_identity"],
            "sample_id": sample_id, "sample_identity": evidence["sample_identity"],
            "contract": evidence["contract"], "decision_time": evidence["decision_time"],
            "png_sha256": evidence["png_sha256"], "attempt_id": terminal["attempt_slot"],
            "network_status": terminal["terminal_status"], "scoreable": normalized["scoreable"],
            "family": normalized["family"], "action": normalized["action"], "direction": normalized["direction"],
            "safe_invocation_evidence_identity": terminal["evidence_identity"],
            "safe_invocation_evidence": evidence, "adjudication": ADJUDICATIONS[sample_id],
            "outcome_access": "NO", "future_access": "NO",
        }
        case["case_evidence_identity"] = identity(case)
        filename = f"JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_{sample_id.replace('-', '_')}_V0_1.json"
        _write_json(ROOT / "docs/evidence" / filename, case)
        cases.append(case)
    cases.sort(key=lambda item: item["sample_id"])
    costs = [Decimal(item["safe_invocation_evidence"]["accounted_cny_for_hard_cap"]) for item in cases]
    latencies = [int(item["safe_invocation_evidence"]["latency_ms"]) for item in cases]
    families: dict[str, int] = {}
    actions: dict[str, int] = {"NO_TRADE": 0, "WAIT": 0, "ENTER": 0}
    for case in cases:
        families[case["family"]] = families.get(case["family"], 0) + 1
        actions[case["action"]] = actions.get(case["action"], 0) + 1
    total = sum(costs, Decimal("0"))
    summary = {
        "schema_version": "jianghe-downloaded-kline-pilot-summary-v0.1",
        "pilot_id": plan["pilot_id"], "pilot_plan_identity": plan["pilot_plan_identity"],
        "remote_ledger_head": head, "pilot_sample_count": 5, "network_calls": 5,
        "automatic_retries": 0, "scoreable_count": sum(bool(item["scoreable"]) for item in cases),
        "complete_output_count": sum(item["safe_invocation_evidence"]["output_state"] == "TEXT_NONEMPTY" for item in cases),
        "total_factual_errors": sum(item["adjudication"]["factual_error_count"] for item in cases),
        "total_invented_rules": sum(item["adjudication"]["invented_rule_count"] for item in cases),
        "total_unsupported_jianghe_claims": sum(item["adjudication"]["unsupported_jianghe_claim_count"] for item in cases),
        "action_distribution": actions, "family_distribution": families,
        "total_accounted_cny": format(total, "f"), "average_actual_cost_per_sample_cny": format(total / Decimal(5), "f"),
        "project_accounted_cny_after": format(HISTORICAL_ACCOUNTED + total, "f"),
        "latency_ms": {"median": int(statistics.median(latencies)), "min": min(latencies), "max": max(latencies)},
        "model_mismatch_count": sum(item["safe_invocation_evidence"]["requested_model_id"] != item["safe_invocation_evidence"]["resolved_model_id"] for item in cases),
        "output_truncation_count": sum(item["safe_invocation_evidence"]["finish_reason"] == "length" for item in cases),
        "pilot_verdict": "REVIEW_BEFORE_EXPAND",
        "verdict_basis": "All five calls are complete and scoreable, but DKL-DS-003 contains two mechanically confirmed factual errors, including a fabricated volume contradiction.",
        "outcome_access": "NO", "future_access": "NO",
        "cases": [{
            "sample_id": item["sample_id"], "contract": item["contract"], "decision_time": item["decision_time"],
            "png_sha256": item["png_sha256"], "attempt_id": item["attempt_id"], "network_status": item["network_status"],
            "scoreable": item["scoreable"], "family": item["family"], "action": item["action"], "direction": item["direction"],
            "factual_errors": item["adjudication"]["factual_error_count"], "invented_rules": item["adjudication"]["invented_rule_count"],
            "accounted_cny": item["safe_invocation_evidence"]["accounted_cny_for_hard_cap"], "latency_ms": item["safe_invocation_evidence"]["latency_ms"],
            "evidence_identity": item["case_evidence_identity"],
        } for item in cases],
    }
    summary["summary_evidence_identity"] = identity(summary)
    _write_json(ROOT / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_SUMMARY_V0_1.json", summary)
    lines = [
        "# 江河 downloaded-Kline DeepSeek pilot V0.1", "", "```text",
        f"PILOT_ID={summary['pilot_id']}", f"PILOT_PLAN_IDENTITY={summary['pilot_plan_identity']}",
        "PILOT_SAMPLE_COUNT=5", "NETWORK_CALLS=5", "AUTOMATIC_RETRIES=0", "SCOREABLE_COUNT=5", "COMPLETE_OUTPUT_COUNT=5",
        f"TOTAL_FACTUAL_ERRORS={summary['total_factual_errors']}", "TOTAL_INVENTED_RULES=0", "TOTAL_UNSUPPORTED_JIANGHE_CLAIMS=0",
        f"TOTAL_ACCOUNTED_CNY={summary['total_accounted_cny']}", f"PROJECT_ACCOUNTED_CNY_AFTER={summary['project_accounted_cny_after']}",
        f"LATENCY_MEDIAN_MS={summary['latency_ms']['median']}", f"LATENCY_MIN_MS={summary['latency_ms']['min']}", f"LATENCY_MAX_MS={summary['latency_ms']['max']}",
        "MODEL_MISMATCH_COUNT=0", "OUTPUT_TRUNCATION_COUNT=0", "PILOT_VERDICT=REVIEW_BEFORE_EXPAND",
        f"REMOTE_LEDGER_HEAD={head}", f"SUMMARY_EVIDENCE_IDENTITY={summary['summary_evidence_identity']}", "```", "",
        "五例均完成、可评分且未发生模型错配或截断；但 DKL-DS-003 有两项机械事实错误，因此不能直接扩批。未读取后续行情、future return 或 outcome。", "",
        "| sample | contract | FAMILY | ACTION | factual | invented | cost CNY | latency ms |", "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for case in summary["cases"]:
        lines.append(f"| {case['sample_id']} | {case['contract']} | {case['family']} | {case['action']} | {case['factual_errors']} | {case['invented_rules']} | {case['accounted_cny']} | {case['latency_ms']} |")
    lines.extend(["", "## Adjudication", "", "四例机械事实无误；DKL-DS-003 将倒数第二根 5m 误认为最后一根，并据此虚构了量能不一致。五例均保持 WAIT/NO_TRADE 纪律，没有自创固定阈值或‘两根 K’之类的未授权交易规则。", "", "下一步应先审查并修正真实 K 线 prompt 中的时间序列定位与跨周期成交量核算要求，再决定是否扩批。", ""])
    (ROOT / "docs/reviews/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_V0_1.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"remote_ledger_head": head, "summary_evidence_identity": summary["summary_evidence_identity"], "pilot_verdict": summary["pilot_verdict"]}, sort_keys=True))


if __name__ == "__main__":
    main()
