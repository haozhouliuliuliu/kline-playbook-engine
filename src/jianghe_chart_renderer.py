"""确定性标准化 K 线图表渲染器（江河 AI 观察与历史回放工程 V0.2）。

厂商中立、非结果：本模块只用渲染窗口内（过去）的 K 线推导布局。同一输入永远
生成同一布局和同一内容哈希。AI 标注以明确的假设形式绘制，绝不混入市场事实。
图表不使用未来自动缩放、不引用未来高低点、不显示未来标记：渲染器只看调用方
传入的 K 线，并拒绝收盘时间晚于图表当前时间的 K 线。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from hashlib import sha256
from typing import Mapping, Sequence

from src.jianghe_ai_trader import ChartRender, ObservationBar


SUPPORTED_TIMEFRAMES: tuple[str, ...] = ("1m", "5m", "15m", "1h")
DEFAULT_WINDOW_SIZES: dict[str, int] = {"1m": 60, "5m": 48, "15m": 36, "1h": 24}
DEFAULT_ROWS = 24
RENDERER_IDENTITY_V0_1 = "JIANGHE_CHART_RENDERER_V0_1"

_OVERLAY_GUTTER_CHAR = {
    "AI_WATCH_REGION": "W",
    "AI_DEFENSE_INTERPRETATION": "I",
    "AI_HYPOTHESIS_KEY_ZONE": "K",
}
_OVERLAY_PRIORITY: tuple[str, ...] = (
    "AI_WATCH_REGION",
    "AI_DEFENSE_INTERPRETATION",
    "AI_HYPOTHESIS_KEY_ZONE",
)
_PRICE_QUANTUM = Decimal("0.000001")


def _require_aware(value: datetime, field_name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} 必须是带时区的时间")


def _decimal(value: str, field_name: str) -> Decimal:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} 必须是非空数字字符串")
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ValueError(f"{field_name} 不是有效数字字符串: {value!r}") from None
    if not result.is_finite():
        raise ValueError(f"{field_name} 必须是有限数字: {value!r}")
    return result


def _format_price(value: Decimal) -> str:
    return format(value.normalize(), "f")


@dataclass(frozen=True)
class ChartOverlay:
    """要叠加到图表上的 AI 假设；与市场事实严格分离。"""

    kind: str
    lower_bound: str
    upper_bound: str
    label: str

    def __post_init__(self) -> None:
        if self.kind not in _OVERLAY_GUTTER_CHAR:
            raise ValueError("叠加类型必须是受支持的 AI 假设类型")
        if not self.label:
            raise ValueError("叠加标签不能为空")
        lower = _decimal(self.lower_bound, "lower_bound")
        upper = _decimal(self.upper_bound, "upper_bound")
        if lower > upper:
            raise ValueError("叠加区间下界不能高于上界")

    @property
    def description(self) -> str:
        return f"{self.label}:{self.lower_bound}-{self.upper_bound}"


@dataclass(frozen=True)
class RenderedChart:
    """一次确定性渲染的完整结果；文本与元数据来自同一输入。"""

    renderer_identity: str
    timeframe: str
    product: str
    concrete_contract: str
    current_time: datetime
    window_definition: str
    bar_count: int
    partial_bar_present: bool
    annotations: tuple[tuple[str, str], ...]
    text: str
    content_hash: str

    def to_chart_render(self) -> ChartRender:
        return ChartRender(
            renderer_identity=self.renderer_identity,
            timeframe=self.timeframe,
            window_definition=self.window_definition,
            current_time=self.current_time,
            render_content_hash=self.content_hash,
            partial_bar_marked=self.partial_bar_present,
            annotations=self.annotations,
        )


class JiangheChartRenderer:
    """标准化 K 线图表渲染器：固定布局规则，价格刻度只来自窗口内 K 线。"""

    def __init__(
        self,
        *,
        renderer_identity: str = RENDERER_IDENTITY_V0_1,
        rows: int = DEFAULT_ROWS,
        window_sizes: Mapping[str, int] | None = None,
    ) -> None:
        if not renderer_identity:
            raise ValueError("渲染器身份不能为空")
        if not isinstance(rows, int) or not 8 <= rows <= 200:
            raise ValueError("图表行数必须在 8 到 200 之间")
        merged = dict(DEFAULT_WINDOW_SIZES)
        if window_sizes is not None:
            for timeframe, size in window_sizes.items():
                if timeframe not in SUPPORTED_TIMEFRAMES:
                    raise ValueError(f"不支持的图表周期: {timeframe}")
                if not isinstance(size, int) or size < 1:
                    raise ValueError("窗口大小必须是正整数")
                merged[timeframe] = size
        self.renderer_identity = renderer_identity
        self.rows = rows
        self.window_sizes: dict[str, int] = {tf: merged[tf] for tf in SUPPORTED_TIMEFRAMES}

    def render(
        self,
        *,
        timeframe: str,
        bars: Sequence[ObservationBar],
        product: str,
        concrete_contract: str,
        current_time: datetime,
        overlays: Sequence[ChartOverlay] = (),
    ) -> RenderedChart:
        if timeframe not in SUPPORTED_TIMEFRAMES:
            raise ValueError(f"不支持或低于 1 分钟基线的图表周期: {timeframe}")
        _require_aware(current_time, "current_time")
        if not product or not concrete_contract:
            raise ValueError("品种与具体合约不能为空")
        bars = tuple(bars)
        if not bars:
            raise ValueError("渲染图表至少需要一根 K 线")
        for bar in bars:
            if not isinstance(bar, ObservationBar):
                raise TypeError("bars 只能包含 ObservationBar")
            if bar.timeframe != timeframe:
                raise ValueError("K 线周期与图表周期不一致")
            if bar.close_time > current_time:
                raise ValueError("图表拒绝收盘时间晚于当前时间的未来 K 线")
        for earlier, later in zip(bars, bars[1:]):
            if later.open_time <= earlier.open_time:
                raise ValueError("K 线必须按开盘时间严格递增且不重复")
        overlays = tuple(sorted(overlays, key=lambda o: (o.kind, o.label, o.lower_bound, o.upper_bound)))

        rows = self.rows
        lows = [_decimal(bar.low_price, "low_price") for bar in bars]
        highs = [_decimal(bar.high_price, "high_price") for bar in bars]
        lo, hi = min(lows), max(highs)
        if hi == lo:
            lo, hi = lo - Decimal(1), hi + Decimal(1)
        span = hi - lo
        row_denominator = Decimal(rows - 1)

        def row_of(price: Decimal) -> int:
            ratio = (hi - price) / span
            scaled = ratio * row_denominator
            row = int(scaled.to_integral_value(rounding=ROUND_HALF_UP))
            return max(0, min(rows - 1, row))

        grid = [["." for _ in bars] for _ in range(rows)]
        for index, bar in enumerate(bars):
            open_price = _decimal(bar.open_price, "open_price")
            close_price = _decimal(bar.close_price, "close_price")
            row_high, row_low = row_of(highs[index]), row_of(lows[index])
            for row in range(min(row_high, row_low), max(row_high, row_low) + 1):
                grid[row][index] = ":"
            body = "#" if bar.is_closed else "o"
            row_open, row_close = row_of(open_price), row_of(close_price)
            for row in range(min(row_open, row_close), max(row_open, row_close) + 1):
                grid[row][index] = body

        row_prices = [hi - span * Decimal(row) / row_denominator for row in range(rows)]
        labels = [_format_price(price.quantize(_PRICE_QUANTUM)) for price in row_prices]
        width = max(len(label) for label in labels)
        overlay_bounds = tuple(
            (_decimal(overlay.lower_bound, "lower_bound"), _decimal(overlay.upper_bound, "upper_bound"), overlay.kind)
            for overlay in overlays
        )
        gutter: list[str] = []
        for price in row_prices:
            char = "."
            for kind in _OVERLAY_PRIORITY:
                if any(lower <= price <= upper for lower, upper, bound_kind in overlay_bounds if bound_kind == kind):
                    char = _OVERLAY_GUTTER_CHAR[kind]
                    break
            gutter.append(char)

        closed_count = sum(1 for bar in bars if bar.is_closed)
        partial_count = len(bars) - closed_count
        window_definition = f"LAST_{len(bars)}_BARS"
        lines: list[str] = []
        lines.append(f"JIANGHE_CHART renderer={self.renderer_identity}")
        lines.append(f"product={product} contract={concrete_contract} timeframe={timeframe}")
        lines.append(
            f"current_time={current_time.isoformat()} bars={len(bars)} closed={closed_count} partial={partial_count}"
        )
        lines.append(f"window={window_definition} rows={rows}")
        lines.append("legend: closed_body=# partial_body=o wick=: empty=.")
        lines.append(
            "AI_HYPOTHESIS overlay gutter: W=AI_WATCH_REGION I=AI_DEFENSE_INTERPRETATION "
            "K=AI_HYPOTHESIS_KEY_ZONE .=none (AI hypotheses; NOT market facts)"
        )
        border = f"{'':>{width}} +{'-' * len(bars)}+"
        lines.append(border)
        for row in range(rows):
            lines.append(f"{labels[row]:>{width}} |{''.join(grid[row])}| {gutter[row]}")
        lines.append(border)
        lines.append(
            f"first_bar_open={bars[0].open_time.isoformat()} last_bar_close={bars[-1].close_time.isoformat()}"
        )
        time_entries = [
            f"c{index:02d}={bar.open_time.strftime('%m-%d %H:%M')}->{bar.close_time.strftime('%m-%d %H:%M')}"
            f"[{'CLOSED' if bar.is_closed else 'PARTIAL'}]"
            for index, bar in enumerate(bars)
        ]
        for start in range(0, len(time_entries), 3):
            lines.append("bars: " + " | ".join(time_entries[start : start + 3]))
        text = "\n".join(lines)
        content_hash = sha256(text.encode("utf-8")).hexdigest()
        annotations = tuple((overlay.kind, overlay.description) for overlay in overlays)
        return RenderedChart(
            renderer_identity=self.renderer_identity,
            timeframe=timeframe,
            product=product,
            concrete_contract=concrete_contract,
            current_time=current_time,
            window_definition=window_definition,
            bar_count=len(bars),
            partial_bar_present=partial_count > 0,
            annotations=annotations,
            text=text,
            content_hash=content_hash,
        )
