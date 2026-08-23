"""江河 VISUAL 观察渲染器 V0.1（厂商中立、非结果、纯标准库 PNG）。

本模块把"截止某个 as_of 时刻、模型依法可见的多周期 K 线"渲染成：

1. 确定性 PNG 字节流（纯 Python 标准库编码，无第三方依赖）；
2. 确定性机器可读 render manifest；
3. 稳定的 ``renderer_config_identity``；
4. 稳定的 ``visual_artifact_identity``。

边界（与冻结研究协议一致）：

- 本模块复用 ``src/jianghe_ai_trader.py`` 的 ``ObservationBar``，不另造第二套
  timestamp / available_at / closed-partial / OHLCV 语义；
- renderer 不生成、不聚合 timeframe；调用方必须传入已经合法准备好的各周期 panel；
- fail closed：任何 ``available_at > as_of`` 的 K 线、非单调/重复时间戳、NaN/无穷、
  非法 OHLC、负成交量一律拒绝；
- 价格与成交量刻度只来自输入 panel 当前可见 K 线（point-in-time visible-window
  scaling），绝不偷看未来；
- 不判断 A/B/C/D、方向、进出场、止损目标、趋势、支撑阻力或关键区；不叠加任何
  技术指标；V0.1 无 AI annotation；
- 颜色只是 presentation，不构成任何交易语义；
- 输出为 provider-neutral 的 PNG bytes + manifest；不绑定任何具体模型厂商；
- 不读系统时钟、不用随机数、不依赖机器字体、不写任何机器相关元数据。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import (
    Context,
    Decimal,
    DivisionByZero,
    InvalidOperation,
    MAX_EMAX,
    MIN_EMIN,
    Overflow,
    ROUND_FLOOR,
    ROUND_HALF_EVEN,
    ROUND_HALF_UP,
    localcontext,
)
from hashlib import sha256
import json
import struct
from typing import Mapping, Sequence
import zlib

from src.jianghe_ai_trader import ObservationBar


RENDERER_VERSION = "JIANGHE_VISUAL_RENDERER_V0_1"
ARTIFACT_KIND = "JIANGHE_VISUAL_OBSERVATION_V0_1"
INPUT_SPEC_KIND = "JIANGHE_VISUAL_OBSERVATION_INPUT_V0_1"
GLYPH_POLICY = "EMBEDDED_5X7_ASCII_BITMAP_V1"
PNG_MIME = "image/png"

MAX_PANELS = 4

# Decimal 治理（F-ADV-01 / F-ADV-03）：
# - 所有渲染内的 Decimal 运算都在固定 context 中执行，与调用进程的全局
#   decimal.getcontext() 无关（决定论 / 环境无关）。
# - 数值字段的 adjusted 指数有受控上限，极端指数（如 1E-3000）fail closed，
#   防止 label 无界字符串展开（潜在 MemoryError / 长时间阻塞）。
_DECIMAL_PRECISION = 28
_MAX_DECIMAL_ADJUSTED_EXPONENT = 100
_MAX_DECIMAL_FORMAT_LENGTH = 256


def _fixed_decimal_context() -> Context:
    """返回一个完全确定、与进程全局 context 无关的 Decimal context。"""
    return Context(
        prec=_DECIMAL_PRECISION,
        rounding=ROUND_HALF_EVEN,
        Emin=MIN_EMIN,
        Emax=MAX_EMAX,
        traps=[InvalidOperation, DivisionByZero, Overflow],
    )


# ---------------------------------------------------------------------------
# 内嵌 5x7 ASCII bitmap 字体（确定性；不依赖任何机器字体）。
# 每个字形为 7 行、每行 5 bit（高位在左）。
# ---------------------------------------------------------------------------

def _g(rows: str) -> tuple[int, ...]:
    lines = [line for line in rows.strip().splitlines() if line.strip()]
    if len(lines) != 7 or any(len(line) != 5 for line in lines):
        raise ValueError("字形必须是 7 行 5 列")
    return tuple(int(line, 2) for line in lines)


_GLYPHS: dict[str, tuple[int, ...]] = {
    " ": _g("""
00000
00000
00000
00000
00000
00000
00000"""),
    "0": _g("""
01110
10001
10011
10101
11001
10001
01110"""),
    "1": _g("""
00100
01100
00100
00100
00100
00100
01110"""),
    "2": _g("""
01110
10001
00001
00110
01000
10000
11111"""),
    "3": _g("""
01110
10001
00001
00110
00001
10001
01110"""),
    "4": _g("""
00010
00110
01010
10010
11111
00010
00010"""),
    "5": _g("""
11111
10000
11110
00001
00001
10001
01110"""),
    "6": _g("""
00110
01000
10000
11110
10001
10001
01110"""),
    "7": _g("""
11111
00001
00010
00100
01000
01000
01000"""),
    "8": _g("""
01110
10001
10001
01110
10001
10001
01110"""),
    "9": _g("""
01110
10001
10001
01111
00001
00010
01100"""),
    "A": _g("""
01110
10001
10001
11111
10001
10001
10001"""),
    "B": _g("""
11110
10001
10001
11110
10001
10001
11110"""),
    "C": _g("""
01110
10001
10000
10000
10000
10001
01110"""),
    "D": _g("""
11110
10001
10001
10001
10001
10001
11110"""),
    "E": _g("""
11111
10000
10000
11110
10000
10000
11111"""),
    "F": _g("""
11111
10000
10000
11110
10000
10000
10000"""),
    "G": _g("""
01110
10001
10000
10111
10001
10001
01111"""),
    "H": _g("""
10001
10001
10001
11111
10001
10001
10001"""),
    "I": _g("""
01110
00100
00100
00100
00100
00100
01110"""),
    "J": _g("""
00111
00010
00010
00010
00010
10010
01100"""),
    "K": _g("""
10001
10010
10100
11000
10100
10010
10001"""),
    "L": _g("""
10000
10000
10000
10000
10000
10000
11111"""),
    "M": _g("""
10001
11011
10101
10101
10001
10001
10001"""),
    "N": _g("""
10001
11001
10101
10011
10001
10001
10001"""),
    "O": _g("""
01110
10001
10001
10001
10001
10001
01110"""),
    "P": _g("""
11110
10001
10001
11110
10000
10000
10000"""),
    "Q": _g("""
01110
10001
10001
10001
10101
10010
01101"""),
    "R": _g("""
11110
10001
10001
11110
10100
10010
10001"""),
    "S": _g("""
01111
10000
10000
01110
00001
00001
11110"""),
    "T": _g("""
11111
00100
00100
00100
00100
00100
00100"""),
    "U": _g("""
10001
10001
10001
10001
10001
10001
01110"""),
    "V": _g("""
10001
10001
10001
10001
01010
01010
00100"""),
    "W": _g("""
10001
10001
10001
10101
10101
11011
10001"""),
    "X": _g("""
10001
01010
00100
00100
00100
01010
10001"""),
    "Y": _g("""
10001
01010
00100
00100
00100
00100
00100"""),
    "Z": _g("""
11111
00001
00010
00100
01000
10000
11111"""),
    "-": _g("""
00000
00000
00000
11111
00000
00000
00000"""),
    ":": _g("""
00000
00100
00100
00000
00100
00100
00000"""),
    ".": _g("""
00000
00000
00000
00000
00000
00110
00110"""),
    ",": _g("""
00000
00000
00000
00000
00110
00100
01000"""),
    "=": _g("""
00000
00000
11111
00000
11111
00000
00000"""),
    "/": _g("""
00001
00010
00010
00100
01000
01000
10000"""),
    "+": _g("""
00000
00100
00100
11111
00100
00100
00000"""),
    "%": _g("""
11001
11010
00010
00100
01000
01011
10011"""),
    "(": _g("""
00010
00100
01000
01000
01000
00100
00010"""),
    ")": _g("""
01000
00100
00010
00010
00010
00100
01000"""),
    "[": _g("""
01110
01000
01000
01000
01000
01000
01110"""),
    "]": _g("""
01110
00010
00010
00010
00010
00010
01110"""),
    "_": _g("""
00000
00000
00000
00000
00000
00000
11111"""),
}

_GLYPH_WIDTH = 5
_GLYPH_HEIGHT = 7
_GLYPH_ADVANCE = 6


# ---------------------------------------------------------------------------
# 通用确定性工具
# ---------------------------------------------------------------------------

def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _canonical_hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_aware(value: datetime, field_name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} 必须是带时区的时间")


def _decimal(value: str, field_name: str) -> Decimal:
    """解析并校验数字字符串；fail closed on 非有限 / 极端指数。"""
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} 必须是非空数字字符串")
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ValueError(f"{field_name} 不是有效数字字符串: {value!r}") from None
    if not result.is_finite():
        raise ValueError(f"{field_name} 必须是有限数字: {value!r}")
    if abs(result.adjusted()) > _MAX_DECIMAL_ADJUSTED_EXPONENT:
        raise ValueError(
            f"{field_name} 的十进制指数超出受控范围: adjusted={result.adjusted()} "
            f"(允许 |adjusted| <= {_MAX_DECIMAL_ADJUSTED_EXPONENT})"
        )
    return result


def _format_decimal(value: Decimal) -> str:
    """把 tick label 格式化为十进制字符串；超长即 fail closed。"""
    text = format(value.normalize(), "f")
    if len(text) > _MAX_DECIMAL_FORMAT_LENGTH:
        raise ValueError(
            f"价格标签超出受控长度（{len(text)} 字符 > {_MAX_DECIMAL_FORMAT_LENGTH}）"
        )
    return text


# ---------------------------------------------------------------------------
# 输入模型（复用 canonical ObservationBar；renderer 不生成/聚合 timeframe）
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class VisualPanel:
    """一个已经由调用方合法准备好的单周期 panel；renderer 只画不重采样。"""

    timeframe: str
    bars: tuple[ObservationBar, ...]

    def __post_init__(self) -> None:
        if not self.timeframe:
            raise ValueError("panel 周期不能为空")
        if not self.bars:
            raise ValueError("panel 至少需要一根 K 线")
        for bar in self.bars:
            if not isinstance(bar, ObservationBar):
                raise TypeError("panel bars 只能包含 canonical ObservationBar")
            if bar.timeframe != self.timeframe:
                raise ValueError("K 线周期与 panel 周期不一致")


@dataclass(frozen=True)
class VisualObservationSpec:
    """截止 as_of 的多周期可见 K 线输入；只含市场事实，不含任何结果字段。"""

    product: str
    concrete_contract: str
    as_of: datetime
    panels: tuple[VisualPanel, ...]

    def __post_init__(self) -> None:
        if not self.product or not self.concrete_contract:
            raise ValueError("品种与具体合约不能为空")
        _require_aware(self.as_of, "as_of")
        if not 1 <= len(self.panels) <= MAX_PANELS:
            raise ValueError(f"panel 数量必须在 1 到 {MAX_PANELS} 之间")
        timeframes = [panel.timeframe for panel in self.panels]
        if len(set(timeframes)) != len(timeframes):
            raise ValueError("panel 周期不得重复")


def panels_from_observation_bars(
    bars: Sequence[ObservationBar], *, timeframe_order: Sequence[str] = ("1m", "5m", "15m", "1h")
) -> tuple[VisualPanel, ...]:
    """严格 adapter：把 canonical ObservationBar 序列按周期分组为 panel。

    不修改、不重采样、不补全任何 K 线；只分组并按 open_time 排序。
    """
    groups: dict[str, list[ObservationBar]] = {}
    for bar in bars:
        if not isinstance(bar, ObservationBar):
            raise TypeError("bars 只能包含 canonical ObservationBar")
        groups.setdefault(bar.timeframe, []).append(bar)
    order = {timeframe: index for index, timeframe in enumerate(timeframe_order)}
    panels = []
    for timeframe in sorted(groups, key=lambda tf: (order.get(tf, len(order)), tf)):
        ordered = tuple(sorted(groups[timeframe], key=lambda bar: bar.open_time))
        panels.append(VisualPanel(timeframe=timeframe, bars=ordered))
    return tuple(panels)


# ---------------------------------------------------------------------------
# 渲染器配置与身份
# ---------------------------------------------------------------------------

def _color(value: tuple[int, int, int], field_name: str) -> tuple[int, int, int]:
    if (
        not isinstance(value, tuple)
        or len(value) != 3
        or any(not isinstance(channel, int) or not 0 <= channel <= 255 for channel in value)
    ):
        raise ValueError(f"{field_name} 必须是 0-255 的 RGB 三元组")
    return value


@dataclass(frozen=True)
class RendererConfig:
    """所有会改变模型所见图像的配置；整体参与 renderer_config_identity。

    颜色只是 presentation：up/down/flat/partial 的配色不构成任何交易语义，
    renderer 也不据此推断方向或结论。
    """

    renderer_version: str = RENDERER_VERSION
    canvas_width: int = 1280
    canvas_height: int = 960
    outer_margin: int = 16
    panel_gap: int = 12
    title_height: int = 20
    time_label_height: int = 16
    price_label_gutter: int = 84
    volume_height_ratio: str = "0.25"
    candle_body_width: int = 7
    candle_gap: int = 3
    grid_line_target: int = 5
    glyph_scale: int = 1
    title_glyph_scale: int = 1
    background_color: tuple[int, int, int] = (255, 255, 255)
    border_color: tuple[int, int, int] = (120, 120, 120)
    grid_color: tuple[int, int, int] = (225, 225, 225)
    text_color: tuple[int, int, int] = (40, 40, 40)
    up_color: tuple[int, int, int] = (200, 30, 30)
    down_color: tuple[int, int, int] = (20, 140, 60)
    flat_color: tuple[int, int, int] = (110, 110, 110)
    partial_body_style: str = "HOLLOW_OUTLINE"
    closed_body_style: str = "FILLED"
    glyph_policy: str = GLYPH_POLICY
    price_scale_policy: str = "VISIBLE_BARS_ONLY_NO_FUTURE"
    volume_scale_policy: str = "VISIBLE_BARS_ONLY_NO_FUTURE"
    time_label_policy: str = "BAR_OPEN_TIME_ORIGINAL_TZ"
    price_tick_policy: str = "DECIMAL_1_2_5_GRID"
    annotation_policy: str = "NONE_V0_1"

    def __post_init__(self) -> None:
        if not self.renderer_version:
            raise ValueError("renderer_version 不能为空")
        if not 320 <= self.canvas_width <= 8192 or not 240 <= self.canvas_height <= 8192:
            raise ValueError("画布尺寸超出允许范围")
        for name in ("outer_margin", "panel_gap"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} 不能为负")
        if self.title_height < 8 or self.time_label_height < 8 or self.price_label_gutter < 40:
            raise ValueError("标题/时间标签/价格标签区高度过小")
        ratio = _decimal(self.volume_height_ratio, "volume_height_ratio")
        if not Decimal(0) < ratio < Decimal(1):
            raise ValueError("volume_height_ratio 必须在 (0,1) 内")
        if self.candle_body_width < 1 or self.candle_gap < 0:
            raise ValueError("蜡烛宽度必须为正、间隙不能为负")
        if not 2 <= self.grid_line_target <= 20:
            raise ValueError("grid_line_target 必须在 2 到 20 之间")
        if self.glyph_scale < 1 or self.title_glyph_scale < 1:
            raise ValueError("字形缩放必须为正整数")
        for name in (
            "background_color", "border_color", "grid_color", "text_color",
            "up_color", "down_color", "flat_color",
        ):
            _color(getattr(self, name), name)
        if self.partial_body_style != "HOLLOW_OUTLINE" or self.closed_body_style != "FILLED":
            raise ValueError("V0.1 固定 closed=FILLED、partial=HOLLOW_OUTLINE")
        for name in (
            "glyph_policy", "price_scale_policy", "volume_scale_policy",
            "time_label_policy", "price_tick_policy", "annotation_policy",
        ):
            if not getattr(self, name):
                raise ValueError(f"{name} 不能为空")

    def to_canonical_dict(self) -> dict[str, object]:
        result: dict[str, object] = {}
        for name in sorted(self.__dataclass_fields__):
            value = getattr(self, name)
            if isinstance(value, tuple):
                value = list(value)
            result[name] = value
        return result

    @property
    def identity(self) -> str:
        return _canonical_hash(self.to_canonical_dict())


# ---------------------------------------------------------------------------
# 纯 stdlib PNG 编码（无第三方依赖；字节流不含时间戳/机器元数据）
# ---------------------------------------------------------------------------

def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def encode_png_rgb(width: int, height: int, rgb: bytes) -> bytes:
    """把 8-bit RGB 帧缓冲编码为 PNG 字节流；同一输入永远得到同一字节流。"""
    if len(rgb) != width * height * 3:
        raise ValueError("帧缓冲大小与画布尺寸不一致")
    row_stride = width * 3
    raw = b"".join(b"\x00" + rgb[y * row_stride:(y + 1) * row_stride] for y in range(height))
    compressed = zlib.compress(raw, 9)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", compressed)
        + _png_chunk(b"IEND", b"")
    )


class _FrameBuffer:
    """确定性 RGB 帧缓冲；只提供绘制原语，无任何环境依赖。"""

    def __init__(self, width: int, height: int, background: tuple[int, int, int]) -> None:
        self.width = width
        self.height = height
        self.data = bytearray(bytes(background) * (width * height))

    def pixel(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            offset = (y * self.width + x) * 3
            self.data[offset:offset + 3] = bytes(color)

    def fill_rect(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int]) -> None:
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.width, x + w), min(self.height, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        for yy in range(y0, y1):
            offset = (yy * self.width + x0) * 3
            self.data[offset:offset + len(row)] = row

    def outline_rect(self, x: int, y: int, w: int, h: int, color: tuple[int, int, int]) -> None:
        self.fill_rect(x, y, w, 1, color)
        self.fill_rect(x, y + h - 1, w, 1, color)
        self.fill_rect(x, y, 1, h, color)
        self.fill_rect(x + w - 1, y, 1, h, color)

    def vline(self, x: int, y0: int, y1: int, color: tuple[int, int, int]) -> None:
        self.fill_rect(x, min(y0, y1), 1, abs(y1 - y0) + 1, color)

    def hline(self, x0: int, x1: int, y: int, color: tuple[int, int, int]) -> None:
        self.fill_rect(min(x0, x1), y, abs(x1 - x0) + 1, 1, color)

    def text(self, x: int, y: int, content: str, color: tuple[int, int, int], scale: int = 1) -> int:
        """绘制内嵌 bitmap 文本；返回下一个 x。未知字符 fail closed。"""
        cursor = x
        for char in content:
            glyph = _GLYPHS.get(char)
            if glyph is None:
                raise ValueError(f"内嵌字体不支持的字符: {char!r}（V0.1 标签仅支持受限 ASCII）")
            for row_index, row_bits in enumerate(glyph):
                for col in range(_GLYPH_WIDTH):
                    if row_bits >> (_GLYPH_WIDTH - 1 - col) & 1:
                        self.fill_rect(
                            cursor + col * scale, y + row_index * scale, scale, scale, color
                        )
            cursor += _GLYPH_ADVANCE * scale
        return cursor

    @staticmethod
    def text_width(content: str, scale: int = 1) -> int:
        if not content:
            return 0
        return len(content) * _GLYPH_ADVANCE * scale - scale


# ---------------------------------------------------------------------------
# 渲染结果
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RenderedVisualArtifact:
    """一次确定性渲染的完整结果：PNG 字节、manifest 与三层身份。"""

    png_bytes: bytes
    manifest: Mapping[str, object]

    @property
    def png_sha256(self) -> str:
        return sha256(self.png_bytes).hexdigest()

    @property
    def renderer_config_identity(self) -> str:
        return str(self.manifest["renderer_config_identity"])

    @property
    def input_observation_identity(self) -> str:
        return str(self.manifest["input_observation_identity"])

    @property
    def visual_artifact_identity(self) -> str:
        return str(self.manifest["visual_artifact_identity"])

    def manifest_json(self) -> str:
        return json.dumps(self.manifest, ensure_ascii=False, indent=2, sort_keys=True)


# ---------------------------------------------------------------------------
# 渲染器
# ---------------------------------------------------------------------------

class JiangheVisualRenderer:
    """把 VisualObservationSpec 渲染为确定性 PNG + manifest。

    不判断任何交易语义；只绘制调用方提供的、已通过 causal 校验的 K 线。
    """

    def __init__(self, config: RendererConfig | None = None) -> None:
        self.config = config if config is not None else RendererConfig()

    # ---------------- causal / 输入校验（fail closed） ----------------

    def _validate_spec(self, spec: VisualObservationSpec) -> None:
        if not isinstance(spec, VisualObservationSpec):
            raise TypeError("spec 必须是 VisualObservationSpec")
        for panel in spec.panels:
            previous_open: datetime | None = None
            for bar in panel.bars:
                if bar.available_at > spec.as_of:
                    raise ValueError(
                        "拒绝渲染：K 线 available_at 晚于 as_of（未来数据不得进入画面）"
                    )
                if previous_open is not None and bar.open_time <= previous_open:
                    raise ValueError("拒绝渲染：K 线时间戳必须严格递增且不重复")
                previous_open = bar.open_time
                open_price = _decimal(bar.open_price, "open_price")
                high_price = _decimal(bar.high_price, "high_price")
                low_price = _decimal(bar.low_price, "low_price")
                close_price = _decimal(bar.close_price, "close_price")
                volume = _decimal(bar.volume, "volume")
                if high_price < open_price or high_price < close_price or high_price < low_price:
                    raise ValueError("拒绝渲染：非法 OHLC（high 不是最高值）")
                if low_price > open_price or low_price > close_price:
                    raise ValueError("拒绝渲染：非法 OHLC（low 不是最低值）")
                if volume < 0:
                    raise ValueError("拒绝渲染：成交量不能为负")

    # ---------------- 刻度（只使用可见窗口） ----------------

    @staticmethod
    def _nice_step(span: Decimal, target: int) -> Decimal:
        base = Decimal(1).scaleb(span.adjusted())
        for multiplier in (1, 2, 5, 10):
            step = base * multiplier
            if span / step <= target:
                return step
        return base * 10

    def _price_ticks(self, low: Decimal, high: Decimal) -> tuple[Decimal, ...]:
        span = high - low
        if span <= 0:
            return (low,)
        step = self._nice_step(span, self.config.grid_line_target)
        first = (low / step).to_integral_value(rounding=ROUND_FLOOR) * step
        ticks: list[Decimal] = []
        tick = first
        while tick <= high and len(ticks) < 16:
            if tick >= low:
                ticks.append(tick)
            tick += step
        if len(ticks) < 2:
            return (low, high)
        return tuple(ticks)

    # ---------------- 主入口 ----------------

    def render(self, spec: VisualObservationSpec) -> RenderedVisualArtifact:
        """渲染入口：所有 Decimal 运算在固定 context 中执行，与进程全局
        decimal context 无关（F-ADV-01 决定论治理）。"""
        with localcontext(_fixed_decimal_context()):
            return self._render_impl(spec)

    def _render_impl(self, spec: VisualObservationSpec) -> RenderedVisualArtifact:
        self._validate_spec(spec)
        config = self.config
        width, height = config.canvas_width, config.canvas_height
        fb = _FrameBuffer(width, height, config.background_color)

        panel_count = len(spec.panels)
        inner_x0 = config.outer_margin
        inner_x1 = width - config.outer_margin
        total_gap = config.panel_gap * (panel_count - 1)
        panel_height = (height - 2 * config.outer_margin - total_gap) // panel_count
        if panel_height < config.title_height + config.time_label_height + 40:
            raise ValueError("画布高度不足以容纳全部 panel")

        manifest_panels: list[dict[str, object]] = []
        for index, panel in enumerate(spec.panels):
            py0 = config.outer_margin + index * (panel_height + config.panel_gap)
            self._render_panel(fb, spec, panel, inner_x0, py0, inner_x1 - inner_x0, panel_height)
            closed_count = sum(1 for bar in panel.bars if bar.is_closed)
            manifest_panels.append({
                "timeframe": panel.timeframe,
                "bar_count": len(panel.bars),
                "closed_count": closed_count,
                "partial_count": len(panel.bars) - closed_count,
                "first_bar_open_time": panel.bars[0].open_time.isoformat(),
                "last_bar_close_time": panel.bars[-1].close_time.isoformat(),
                "latest_available_at": max(bar.available_at for bar in panel.bars).isoformat(),
            })

        png_bytes = encode_png_rgb(width, height, bytes(fb.data))
        png_sha = sha256(png_bytes).hexdigest()
        input_identity = self._input_identity(spec)
        config_identity = config.identity
        artifact_identity = _canonical_hash({
            "artifact": ARTIFACT_KIND,
            "renderer_version": config.renderer_version,
            "renderer_config_identity": config_identity,
            "input_observation_identity": input_identity,
            "png_sha256": png_sha,
        })
        manifest: dict[str, object] = {
            "artifact": ARTIFACT_KIND,
            "renderer_version": config.renderer_version,
            "renderer_config_identity": config_identity,
            "input_observation_identity": input_identity,
            "visual_artifact_identity": artifact_identity,
            "png_sha256": png_sha,
            "image": {"mime": PNG_MIME, "width": width, "height": height},
            "as_of": spec.as_of.isoformat(),
            "product": spec.product,
            "concrete_contract": spec.concrete_contract,
            "panels": manifest_panels,
            "future_bar_count": 0,
            "outcome_fields": 0,
            "annotations": [],
            "scaling_policy": config.price_scale_policy,
            "provider": "PROVIDER_NEUTRAL",
        }
        return RenderedVisualArtifact(png_bytes=png_bytes, manifest=manifest)

    @staticmethod
    def _input_identity(spec: VisualObservationSpec) -> str:
        """渲染输入的 canonical 身份。

        注意：这是 rendering-input 身份，不冒充整个 JiangheObservation 的正式项目身份。
        """
        return _canonical_hash({
            "spec_kind": INPUT_SPEC_KIND,
            "product": spec.product,
            "concrete_contract": spec.concrete_contract,
            "as_of": spec.as_of.isoformat(),
            "panels": [
                {
                    "timeframe": panel.timeframe,
                    "bars": [
                        {
                            "open_time": bar.open_time.isoformat(),
                            "close_time": bar.close_time.isoformat(),
                            "available_at": bar.available_at.isoformat(),
                            "open_price": bar.open_price,
                            "high_price": bar.high_price,
                            "low_price": bar.low_price,
                            "close_price": bar.close_price,
                            "volume": bar.volume,
                            "is_closed": bar.is_closed,
                        }
                        for bar in panel.bars
                    ],
                }
                for panel in spec.panels
            ],
        })

    # ---------------- 单 panel 绘制 ----------------

    def _render_panel(
        self,
        fb: _FrameBuffer,
        spec: VisualObservationSpec,
        panel: VisualPanel,
        x0: int,
        y0: int,
        panel_width: int,
        panel_height: int,
    ) -> None:
        config = self.config
        bars = panel.bars
        count = len(bars)

        slot = config.candle_body_width + config.candle_gap
        plot_x0 = x0 + 1
        plot_x1 = x0 + panel_width - config.price_label_gutter
        plot_width = plot_x1 - plot_x0
        required = count * slot - config.candle_gap
        if required > plot_width:
            raise ValueError(
                f"panel {panel.timeframe} 的 {count} 根 K 线超出固定画布宽度；"
                "调用方必须收窄可见窗口（renderer 不裁减、不重采样）"
            )

        # 标题区：product contract timeframe as_of 与 partial 计数（全部确定性）
        closed_count = sum(1 for bar in bars if bar.is_closed)
        title = (
            f"{spec.product} {spec.concrete_contract} {panel.timeframe} "
            f"AS_OF={spec.as_of.isoformat()} BARS={count} "
            f"CLOSED={closed_count} PARTIAL={count - closed_count}"
        ).upper()
        title_scale = config.title_glyph_scale
        title_y = y0 + max(0, (config.title_height - _GLYPH_HEIGHT * title_scale) // 2)
        fb.text(x0 + 4, title_y, title, config.text_color, title_scale)

        chart_y0 = y0 + config.title_height
        chart_height = panel_height - config.title_height - config.time_label_height
        volume_height = int(chart_height * float(config.volume_height_ratio))
        price_height = chart_height - volume_height
        price_y0 = chart_y0
        price_y1 = price_y0 + price_height  # 排他
        volume_y0 = price_y1
        volume_y1 = volume_y0 + volume_height  # 排他
        if price_height < 8 or volume_height < 4:
            raise ValueError("panel 内部价格/成交量区域高度不足")

        # 可见窗口刻度（绝不使用 as_of 之后的数据）
        lows = [_decimal(bar.low_price, "low_price") for bar in bars]
        highs = [_decimal(bar.high_price, "high_price") for bar in bars]
        lo, hi = min(lows), max(highs)
        if hi == lo:
            lo, hi = lo - Decimal(1), hi + Decimal(1)
        span = hi - lo
        denominator = Decimal(price_height - 1)

        def y_of(price: Decimal) -> int:
            ratio = (hi - price) / span
            row = int((ratio * denominator).to_integral_value(rounding=ROUND_HALF_UP))
            return price_y0 + max(0, min(price_height - 1, row))

        # 边框与分隔线
        fb.outline_rect(x0, y0, panel_width, panel_height, config.border_color)
        fb.hline(plot_x0, x0 + panel_width - 2, price_y1, config.border_color)

        # 水平网格 + 价格标签（右 gutter）
        for tick in self._price_ticks(lo, hi):
            yy = y_of(tick)
            fb.hline(plot_x0, plot_x1 - 1, yy, config.grid_color)
            label = _format_decimal(tick)
            label_y = yy - (_GLYPH_HEIGHT * config.glyph_scale) // 2
            label_y = max(price_y0, min(price_y1 - _GLYPH_HEIGHT * config.glyph_scale, label_y))
            fb.text(plot_x1 + 4, label_y, label, config.text_color, config.glyph_scale)

        # 蜡烛与成交量
        offset_x = plot_x0 + (plot_width - required) // 2
        volumes = [_decimal(bar.volume, "volume") for bar in bars]
        max_volume = max(volumes)
        volume_span = volume_height - 2
        for index, bar in enumerate(bars):
            open_price = _decimal(bar.open_price, "open_price")
            close_price = _decimal(bar.close_price, "close_price")
            if close_price > open_price:
                color = config.up_color
            elif close_price < open_price:
                color = config.down_color
            else:
                color = config.flat_color
            cx0 = offset_x + index * slot
            center = cx0 + config.candle_body_width // 2
            y_high = y_of(highs[index])
            y_low = y_of(lows[index])
            fb.vline(center, y_high, y_low, color)
            body_top = y_of(max(open_price, close_price))
            body_bottom = y_of(min(open_price, close_price))
            body_height = body_bottom - body_top + 1
            if bar.is_closed:
                fb.fill_rect(cx0, body_top, config.candle_body_width, body_height, color)
            else:
                fb.outline_rect(cx0, body_top, config.candle_body_width, body_height, color)

            # 成交量（原始 volume；方向色仅继承蜡烛 presentation）
            if max_volume > 0:
                bar_vol_height = int(
                    (volumes[index] / max_volume * volume_span).to_integral_value(
                        rounding=ROUND_HALF_UP
                    )
                )
            else:
                bar_vol_height = 0
            if bar_vol_height > 0:
                fb.fill_rect(
                    cx0, volume_y1 - 1 - bar_vol_height, config.candle_body_width,
                    bar_vol_height, color,
                )

        # 时间标签：确定性选取首/1/4/中/3/4/尾，使用 K 线自带时区；
        # 位置冲突时按固定顺序确定性跳过，绝不移动到其他（非输入决定的）位置。
        label_indices = sorted({0, count // 4, count // 2, (3 * count) // 4, count - 1})
        label_y = volume_y1 + max(0, (config.time_label_height - _GLYPH_HEIGHT * config.glyph_scale) // 2)
        last_label_end: int | None = None
        for index in label_indices:
            label = bars[index].open_time.strftime("%m-%d %H:%M")
            center = offset_x + index * slot + config.candle_body_width // 2
            label_width = _FrameBuffer.text_width(label, config.glyph_scale)
            label_x = center - label_width // 2
            label_x = max(plot_x0, min(plot_x1 - label_width, label_x))
            if last_label_end is not None and label_x < last_label_end + 4:
                continue
            fb.text(label_x, label_y, label, config.text_color, config.glyph_scale)
            last_label_end = label_x + label_width


__all__ = [
    "ARTIFACT_KIND",
    "GLYPH_POLICY",
    "INPUT_SPEC_KIND",
    "JiangheVisualRenderer",
    "MAX_PANELS",
    "PNG_MIME",
    "RENDERER_VERSION",
    "RenderedVisualArtifact",
    "RendererConfig",
    "VisualObservationSpec",
    "VisualPanel",
    "encode_png_rgb",
    "panels_from_observation_bars",
]
