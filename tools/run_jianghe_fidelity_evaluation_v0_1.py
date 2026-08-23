#!/usr/bin/env python3
"""江河 AI 忠实度评估 harness 的命令行 runner。

用法示例：
    python tools/run_jianghe_fidelity_evaluation_v0_1.py \
        docs/evidence/sample_model_responses.jsonl

输入文件支持 JSON（对象或数组）或 JSONL。
输出为机器可读确定性 JSON 报告；默认写到 stdout，可用 --output 指定文件。
报告包含 processing_status / evidence_completeness / evidence_eligibility 三态
与确定性 report_identity。

退出码：0 当且仅当 processing_status == "OK"；否则 1（fail-closed）。
本脚本不调用任何真实模型、不访问网络、不读取 outcome/PnL。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.jianghe_fidelity_evaluation import (
    CORPUS_PATH,
    evaluate_response_records,
    load_corpus,
    load_response_records,
    render_report,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="run_jianghe_fidelity_evaluation_v0_1",
        description="Run the Jianghe fidelity evaluation harness on response records.",
    )
    parser.add_argument(
        "records",
        type=Path,
        help="Path to JSON or JSONL response-record file.",
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=CORPUS_PATH,
        help="Path to fidelity fixture corpus JSON (default: docs/evidence/JIANGHE_AI_FIDELITY_FIXTURES_V0_1.json).",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Output report path (default: stdout).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.records.exists():
        print(f"ERROR: records file not found: {args.records}", file=sys.stderr)
        return 2

    try:
        corpus = load_corpus(args.corpus)
    except Exception as exc:
        print(f"ERROR: failed to load corpus {args.corpus}: {exc}", file=sys.stderr)
        return 2

    try:
        raw_records = load_response_records(args.records)
    except Exception as exc:
        print(f"ERROR: failed to load records {args.records}: {exc}", file=sys.stderr)
        return 2

    report = evaluate_response_records(corpus, raw_records)
    rendered = render_report(report)

    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered, encoding="utf-8")

    return 0 if report.get("processing_status", report.get("status")) == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
