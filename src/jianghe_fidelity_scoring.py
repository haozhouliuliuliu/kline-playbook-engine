"""江河 AI 忠实度夹具语料的确定性评分核心。

本模块只回答一个问题：给定一个夹具（fixture）和一个被规范化的模型回复，
该回复是否符合江河来源语义约束（“是否像江河”），而不是“该模型是否赚钱”。

规则：
- 夹具语料只包含合成的、无结果的观察描述；不允许出现真实候选 PnL、
  未来价格表现、win/loss 标签或任何结果选择逻辑。
- 评分以语义约束为主：PASS 路径可以有多个等价语言答案；FAIL 条件把
  违反来源硬负例的推理结构判为不合格。
- 本模块不做模型请求、不读取真实行情、不计算收益。

约束类型（constraint）：
- family_in / family_not_in          : 策略家族 A/B/C/D/NONE
- action_in / action_not_in          : WAIT/NO_TRADE/WATCH/CANDIDATE/ENTER/MANAGE/EXIT
- direction_in / direction_not_in    : LONG/SHORT/NONE
- principle_acknowledged             : 回复显式满足某条江河原则（任意命中）
- principle_violated                 : 回复显式违反某条江河原则（任意命中）
- no_invented_threshold              : 回复没有发明来源未钉死的阈值
- invented_threshold                 : 回复发明了任意来源未钉死的阈值（FAIL 用）
- declares_unknown                   : 回复把给定的 UNKNOWN 概念标记为未知
- no_outcome_reference               : 回复没有引用未来价格/结果/盈亏（PASS 用）
- outcome_referenced                 : 回复引用了未来价格/结果/盈亏（FAIL 用）

判定：fixture PASS 当且仅当至少一个 pass_path 全部成立且没有任何
fail_condition 全部成立。其余情况 FAIL。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import re
from typing import Any, Iterable, Mapping, Sequence

from src.jianghe_ai_trader import DecisionAction, Direction, JiangheDecision, StrategyFamily

# --------------------------------------------------------------------------
# 常量与路径
# --------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

CORPUS_RELATIVE = "docs/evidence/JIANGHE_AI_FIDELITY_FIXTURES_V0_1.json"
CORPUS_PATH = ROOT / CORPUS_RELATIVE

# 语料自称身份；validate_corpus 会强制一致。
CORPUS_ID = "JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1"

FAMILY_CODES = {"A", "B", "C", "D", "NONE"}
ACTION_CODES = {action.value for action in DecisionAction}
DIRECTION_CODES = {direction.value for direction in Direction}

# 9 条强制硬负例（任务指定）。
REQUIRED_HARD_NEGATIVES = (
    "HN-001",
    "HN-002",
    "HN-003",
    "HN-004",
    "HN-005",
    "HN-006",
    "HN-007",
    "HN-008",
    "HN-009",
)

# 结果/未来价格污染词。夹具正文任何文本字段出现这些词即判污染。
# 只针对“结果/表现/未来走势”主张；止盈止损、防守位等管理语义不算。
OUTCOME_CONTAMINATION_PATTERNS: tuple[tuple[str, str], ...] = (
    ("pnl", r"\bpnl\b"),
    ("profit", r"\bprofit\b"),
    ("profit", r"\bprofits\b"),
    ("win_rate", r"\bwin\s*rate\b"),
    ("winrate", r"\bwinrate\b"),
    ("sharpe", r"\bsharpe\b"),
    ("equity", r"\bequity\b"),
    ("盈利率", r"盈利率"),
    ("胜率", r"胜率"),
    ("盈亏", r"盈亏"),
    ("收益率", r"收益率"),
    ("权益曲线", r"权益曲线"),
    ("后来涨", r"后来涨"),
    ("后来跌", r"后来跌"),
    ("后来真的", r"后来真的"),
    ("后续大涨", r"后续大涨"),
    ("后续大跌", r"后续大跌"),
    ("后市上涨", r"后市上涨"),
    ("后市下跌", r"后市下跌"),
    ("所以应该买", r"所以应该买"),
    ("所以应该做多", r"所以应该做多"),
    ("所以会涨", r"所以会涨"),
    ("最终盈利", r"最终盈利"),
    ("最终亏损", r"最终亏损"),
)

# 若正文出现这些管理语义词但上下文是“禁止/不依据结果”，允许误报排查。
# 这里只做统计提示，真正的判据是上面 OUTCOME_CONTAMINATION_PATTERNS。

CONSTRAINT_TYPES = (
    "family_in",
    "family_not_in",
    "action_in",
    "action_not_in",
    "direction_in",
    "direction_not_in",
    "principle_acknowledged",
    "principle_violated",
    "no_invented_threshold",
    "invented_threshold",
    "declares_unknown",
    "no_outcome_reference",
    "outcome_referenced",
)

_VALUE_KEYS = {
    "family_in": "family",
    "family_not_in": "family",
    "action_in": "action",
    "action_not_in": "action",
    "direction_in": "direction",
    "direction_not_in": "direction",
    "principle_acknowledged": "principle",
    "principle_violated": "principle",
    "declares_unknown": "unknown",
}

_ALLOWED_VALUE_SETS = {
    "family_in": FAMILY_CODES,
    "family_not_in": FAMILY_CODES,
    "action_in": ACTION_CODES,
    "action_not_in": ACTION_CODES,
    "direction_in": DIRECTION_CODES,
    "direction_not_in": DIRECTION_CODES,
    "principle_acknowledged": None,  # 语料原则注册表校验
    "principle_violated": None,
    "declares_unknown": None,  # UNKNOWN 注册表校验
    "no_invented_threshold": None,
    "invented_threshold": None,
    "no_outcome_reference": None,
    "outcome_referenced": None,
}


# --------------------------------------------------------------------------
# 回复记录
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class FidelityResponse:
    """一个被规范化后的模型回复记录。

    ``family``/``action``/``direction`` 是从原始回复抽取的结构化决策；
    ``acknowledged_principles``/``violated_principles`` 是评审者从回复理由
    中抽取的语义标记（体现“是否像江河”）；其余字段记录诚实性特征。

    本记录不含任何收益、未来价格或结果字段。
    """

    family: str | None = None
    action: str | None = None
    direction: str | None = None
    acknowledged_principles: tuple[str, ...] = ()
    violated_principles: tuple[str, ...] = ()
    declared_unknown: tuple[str, ...] = ()
    invented_thresholds: tuple[str, ...] = ()
    outcome_reference: bool = False
    raw_text: str | None = None

    def __post_init__(self) -> None:
        if self.family is not None and self.family not in FAMILY_CODES:
            raise ValueError(f"非法家族代码: {self.family!r}")
        if self.action is not None and self.action not in ACTION_CODES:
            raise ValueError(f"非法动作代码: {self.action!r}")
        if self.direction is not None and self.direction not in DIRECTION_CODES:
            raise ValueError(f"非法方向代码: {self.direction!r}")

    @classmethod
    def from_decision(
        cls,
        decision: JiangheDecision,
        *,
        acknowledged_principles: Sequence[str] = (),
        violated_principles: Sequence[str] = (),
        declared_unknown: Sequence[str] = (),
        invented_thresholds: Sequence[str] = (),
        outcome_reference: bool = False,
        raw_text: str | None = None,
    ) -> "FidelityResponse":
        """从 `JiangheDecision`（src/jianghe_ai_trader.py）构造回复记录。"""
        return cls(
            family=None if decision.family is StrategyFamily.NONE else decision.family.value,
            action=decision.action.value,
            direction=None if decision.direction is Direction.NONE else decision.direction.value,
            acknowledged_principles=tuple(acknowledged_principles),
            violated_principles=tuple(violated_principles),
            declared_unknown=tuple(declared_unknown),
            invented_thresholds=tuple(invented_thresholds),
            outcome_reference=outcome_reference,
            raw_text=raw_text,
        )


@dataclass(frozen=True)
class FixtureScore:
    """一个夹具的评分结果。"""

    fixture_id: str
    verdict: str  # "PASS" | "FAIL"
    satisfied_paths: tuple[str, ...] = ()
    triggered_failures: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.verdict == "PASS"


# --------------------------------------------------------------------------
# 约束求值
# --------------------------------------------------------------------------


def evaluate_constraint(constraint: Mapping[str, Any], response: FidelityResponse) -> bool:
    """求值单个约束；未知类型或非法参数抛 ValueError。"""
    ctype = constraint.get("type")
    values = constraint.get("values", ())
    if ctype not in CONSTRAINT_TYPES:
        raise ValueError(f"未知约束类型: {ctype!r}")
    if ctype == "family_in":
        return response.family in values
    if ctype == "family_not_in":
        return response.family not in values
    if ctype == "action_in":
        return response.action in values
    if ctype == "action_not_in":
        return response.action not in values
    if ctype == "direction_in":
        return response.direction in values
    if ctype == "direction_not_in":
        return response.direction not in values
    if ctype == "principle_acknowledged":
        return bool(set(values) & set(response.acknowledged_principles))
    if ctype == "principle_violated":
        return bool(set(values) & set(response.violated_principles))
    if ctype == "no_invented_threshold":
        return not response.invented_thresholds
    if ctype == "invented_threshold":
        return bool(response.invented_thresholds)
    if ctype == "declares_unknown":
        return set(values) <= set(response.declared_unknown)
    if ctype == "no_outcome_reference":
        return not response.outcome_reference
    if ctype == "outcome_referenced":
        return response.outcome_reference
    raise ValueError(f"未实现的约束类型: {ctype!r}")


def evaluate_fixture(fixture: Mapping[str, Any], response: FidelityResponse) -> FixtureScore:
    """按夹具的 rubric 对回复评分。PASS 需要至少一个 pass_path 全部成立且
    没有任何 fail_condition 全部成立。"""
    rubric = fixture["rubric"]
    satisfied_paths = [
        path["name"]
        for path in rubric["pass_paths"]
        if all(evaluate_constraint(constraint, response) for constraint in path["constraints"])
    ]
    triggered_failures = [
        condition["name"]
        for condition in rubric["fail_conditions"]
        if all(evaluate_constraint(constraint, response) for constraint in condition["constraints"])
    ]
    reasons: list[str] = []
    if not satisfied_paths:
        reasons.append("没有满足任何 PASS 路径")
    else:
        reasons.append(f"满足 PASS 路径: {', '.join(satisfied_paths)}")
    if triggered_failures:
        reasons.append(f"触发 FAIL 条件: {', '.join(triggered_failures)}")
    verdict = "PASS" if satisfied_paths and not triggered_failures else "FAIL"
    return FixtureScore(
        fixture_id=fixture["fixture_id"],
        verdict=verdict,
        satisfied_paths=tuple(satisfied_paths),
        triggered_failures=tuple(triggered_failures),
        reasons=tuple(reasons),
    )


def evaluate_corpus(
    corpus: Mapping[str, Any],
    responses: Mapping[str, FidelityResponse],
) -> dict[str, FixtureScore]:
    """批量评分；返回 {fixture_id: FixtureScore}。缺失回复按 FAIL 处理并记原因。"""
    scores: dict[str, FixtureScore] = {}
    for fixture in corpus["fixtures"]:
        fixture_id = fixture["fixture_id"]
        if fixture_id not in responses:
            scores[fixture_id] = FixtureScore(fixture_id, "FAIL", reasons=("缺少回复记录",))
            continue
        scores[fixture_id] = evaluate_fixture(fixture, responses[fixture_id])
    return scores


# --------------------------------------------------------------------------
# 语料校验
# --------------------------------------------------------------------------


def _text_of(obj: object) -> str:
    """把任意嵌套结构拍平成文本，用于污染扫描。"""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, Mapping):
        return " ".join(_text_of(value) for value in obj.values())
    if isinstance(obj, (list, tuple)):
        return " ".join(_text_of(item) for item in obj)
    return str(obj)


# 明确“排除保证”的元数据区，不参与污染扫描：
# - ``non_outcome_guarantee`` 声明语料不含 PnL/未来价格/结果；
# - ``hidden_future_information`` 声明哪些信息绝不提供给模型。
# 这两节是“保证语句”，不是被评分的夹具内容；被评分内容
# （visible_information / expected / rubric / title 等）仍会被严格扫描。
_SKIP_SCAN_KEYS = frozenset({"hidden_future_information", "non_outcome_guarantee"})


def scan_outcome_contamination(corpus: Mapping[str, Any]) -> list[tuple[str, str]]:
    """扫描被评分夹具内容的全部文本字段，返回 [(字段路径, 命中词), ...]。

    只对“结果/未来表现”主张判污染；不含未来价格路径等管理语义。
    排除保证区（non_outcome_guarantee / hidden_future_information）是声明
    “这些信息被排除”的元数据，不是夹具的评分内容，因此跳过。
    """
    hits: list[tuple[str, str]] = []

    def walk(node: object, path: str) -> None:
        if isinstance(node, str):
            lowered = node.lower()
            for label, pattern in OUTCOME_CONTAMINATION_PATTERNS:
                if re.search(pattern, lowered):
                    hits.append((path, label))
            return
        if isinstance(node, Mapping):
            for key, value in node.items():
                if key in _SKIP_SCAN_KEYS:
                    continue
                walk(value, f"{path}.{key}")
            return
        if isinstance(node, (list, tuple)):
            for index, item in enumerate(node):
                walk(item, f"{path}[{index}]")
            return

    walk(corpus, "corpus")
    return hits


def validate_corpus(corpus: Mapping[str, Any]) -> list[str]:
    """结构校验。返回错误列表；空列表表示通过。"""
    errors: list[str] = []
    if corpus.get("corpus_id") != CORPUS_ID:
        errors.append(f"corpus_id 必须是 {CORPUS_ID}")

    principles = {item["id"] for item in corpus.get("principles", [])}
    hard_negatives = {item["id"] for item in corpus.get("hard_negatives", [])}
    unknowns = set(corpus.get("unknown_register_ids", []))
    fixtures = corpus.get("fixtures", [])
    if not isinstance(fixtures, list) or not fixtures:
        errors.append("fixtures 不能为空")

    fixture_ids: set[str] = set()
    coverage_seen: set[str] = set()
    hn_seen: set[str] = set()

    for fixture in fixtures:
        fixture_id = fixture.get("fixture_id")
        if not fixture_id:
            errors.append("存在缺少 fixture_id 的夹具")
            continue
        if fixture_id in fixture_ids:
            errors.append(f"重复 fixture_id: {fixture_id}")
        fixture_ids.add(fixture_id)

        coverage = fixture.get("coverage")
        if coverage not in FAMILY_CODES:
            errors.append(f"{fixture_id}: coverage 非法 {coverage!r}")
        else:
            coverage_seen.add(coverage)

        expected = fixture.get("expected", {})
        permissible = set(expected.get("permissible_family_set", []))
        forbidden = set(expected.get("forbidden_family_set", []))
        if not permissible:
            errors.append(f"{fixture_id}: permissible_family_set 不能为空")
        if not permissible <= FAMILY_CODES:
            errors.append(f"{fixture_id}: permissible_family_set 含非法家族")
        if not forbidden <= FAMILY_CODES:
            errors.append(f"{fixture_id}: forbidden_family_set 含非法家族")
        if permissible & forbidden:
            errors.append(f"{fixture_id}: permissible 与 forbidden 家族重叠")

        required_principles = expected.get("required_principles", [])
        for principle_id in required_principles:
            if principle_id not in principles:
                errors.append(f"{fixture_id}: required_principles 引用未知原则 {principle_id}")

        if not expected.get("acceptable_ambiguity"):
            errors.append(f"{fixture_id}: acceptable_ambiguity 不能为空")

        explicit_unknown = expected.get("explicit_unknown", [])
        for unknown_id in explicit_unknown:
            if unknown_id not in unknowns:
                errors.append(f"{fixture_id}: explicit_unknown 引用未知条目 {unknown_id}")

        for tag in fixture.get("hard_negative_tags", []):
            if tag not in hard_negatives:
                errors.append(f"{fixture_id}: hard_negative_tags 引用未知条目 {tag}")
            hn_seen.add(tag)

        rubric = fixture.get("rubric", {})
        pass_paths = rubric.get("pass_paths", [])
        fail_conditions = rubric.get("fail_conditions", [])
        if not pass_paths:
            errors.append(f"{fixture_id}: rubric.pass_paths 不能为空")
        if not fail_conditions:
            errors.append(f"{fixture_id}: rubric.fail_conditions 不能为空")

        has_outcome_fail = any(
            any(constraint.get("type") == "outcome_referenced" for constraint in condition["constraints"])
            for condition in fail_conditions
        )
        if not has_outcome_fail:
            errors.append(f"{fixture_id}: fail_conditions 必须包含 outcome_referenced 约束")

        for path in pass_paths:
            for constraint in path.get("constraints", []):
                _validate_constraint(fixture_id, constraint, principles, unknowns, errors)
        for condition in fail_conditions:
            for constraint in condition.get("constraints", []):
                _validate_constraint(fixture_id, constraint, principles, unknowns, errors)

    if coverage_seen != {"A", "B", "C", "D", "NONE"}:
        errors.append(f"coverage 必须覆盖 A/B/C/D/NONE，实际缺: {sorted({'A','B','C','D','NONE'} - coverage_seen)}")

    missing_hard_negatives = set(REQUIRED_HARD_NEGATIVES) - hn_seen
    if missing_hard_negatives:
        errors.append(f"缺少硬负例覆盖: {sorted(missing_hard_negatives)}")

    contamination = scan_outcome_contamination(corpus)
    if contamination:
        errors.append(f"检测到结果/未来价格污染: {contamination[:5]}")

    return errors


def _validate_constraint(
    fixture_id: str,
    constraint: Mapping[str, Any],
    principles: set[str],
    unknowns: set[str],
    errors: list[str],
) -> None:
    ctype = constraint.get("type")
    if ctype not in CONSTRAINT_TYPES:
        errors.append(f"{fixture_id}: 非法约束类型 {ctype!r}")
        return
    allowed_values = _ALLOWED_VALUE_SETS.get(ctype)
    if allowed_values is not None:
        for value in constraint.get("values", []):
            if value not in allowed_values:
                errors.append(f"{fixture_id}: 约束 {ctype} 的非法值 {value!r}")
    if ctype in ("principle_acknowledged", "principle_violated"):
        for value in constraint.get("values", []):
            if value not in principles:
                errors.append(f"{fixture_id}: 约束 {ctype} 引用未知原则 {value!r}")
    if ctype == "declares_unknown":
        for value in constraint.get("values", []):
            if value not in unknowns:
                errors.append(f"{fixture_id}: 约束 declares_unknown 引用未知条目 {value!r}")


# --------------------------------------------------------------------------
# 载入与顶层入口
# --------------------------------------------------------------------------


def load_corpus(path: Path = CORPUS_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def verify_corpus(path: Path = CORPUS_PATH) -> tuple[bool, list[str]]:
    """载入并校验语料；返回 (是否通过, 错误列表)。"""
    corpus = load_corpus(path)
    errors = validate_corpus(corpus)
    return (not errors), errors


if __name__ == "__main__":  # pragma: no cover
    passed, errors = verify_corpus()
    if not passed:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(f"OK: {CORPUS_ID} 结构校验通过")
