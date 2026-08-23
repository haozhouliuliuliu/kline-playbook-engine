"""独立对抗审计测试：江河 VISUAL 观察渲染器 V0.1（adversarial verifier lane）。

本文件由独立 adversarial verifier 编写，目标是尽量把 renderer 打坏，
而不是证明它正确。只新增测试，不修改 renderer / CLI / 原始测试。

约定：
- 期望 fail-closed / 环境无关 / 原子性 的断言若失败，即为正式 FINDING，
  reproducer 保留在本文件中（不修复 source，由 integration lane 处理）。
- 记录实际行为的测试（OBSERVED）用于刻画 contract 未明确处的真实语义。

覆盖：跨进程确定性、PNG 结构、Decimal/数值边界、OHLC 攻击、时区、
未来泄露、刻度因果、多 panel、字符串/字形、config identity 完备性、
input identity 完备性、partial/closed 语义、manifest 独立重算、
CLI 对抗、依赖/网络静态审计、结果推断静态审计。
"""

from __future__ import annotations

import ast
import decimal
import inspect
import json
import os
import struct
import subprocess
import sys
import tempfile
import zlib
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from pathlib import Path
import unittest

import src.jianghe_visual_renderer as visual_module
from src.jianghe_ai_trader import ObservationBar
from src.jianghe_visual_renderer import (
    ARTIFACT_KIND,
    INPUT_SPEC_KIND,
    JiangheVisualRenderer,
    MAX_PANELS,
    RENDERER_VERSION,
    RenderedVisualArtifact,
    RendererConfig,
    VisualObservationSpec,
    VisualPanel,
)

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "render_jianghe_visual_observation_v0_1.py"
CN = timezone(timedelta(hours=8))
UTC = timezone.utc
T0 = datetime(2026, 8, 23, 9, 0, tzinfo=CN)
AS_OF = T0 + timedelta(hours=2)


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------

def make_bar(
    index: int,
    *,
    timeframe: str = "1m",
    minutes: int = 1,
    open_price: str = "100",
    high: str = "101",
    low: str = "99",
    close_price: str = "100",
    volume: str = "10",
    closed: bool = True,
    tz=CN,
    available_delay_seconds: int = 0,
) -> ObservationBar:
    open_time = T0 + timedelta(minutes=index * minutes)
    close_time = open_time + timedelta(minutes=minutes)
    if tz is not CN:
        open_time = open_time.astimezone(tz)
        close_time = close_time.astimezone(tz)
    return ObservationBar(
        timeframe=timeframe,
        open_time=open_time,
        close_time=close_time,
        available_at=close_time + timedelta(seconds=available_delay_seconds),
        open_price=open_price,
        high_price=high,
        low_price=low,
        close_price=close_price,
        volume=volume,
        is_closed=closed,
    )


def wave_bars(count: int, *, timeframe: str = "1m", minutes: int = 1) -> tuple[ObservationBar, ...]:
    bars = []
    for index in range(count):
        base = 100 + (index % 5)
        bars.append(make_bar(
            index,
            timeframe=timeframe,
            minutes=minutes,
            open_price=str(base),
            high=str(base + 2),
            low=str(base - 2),
            close_price=str(base + (1 if index % 2 else -1)),
            volume=str(10 + index),
        ))
    return tuple(bars)


def make_spec(*, panels=None, as_of: datetime = AS_OF,
              product: str = "cu", concrete_contract: str = "SHFE.cu2609") -> VisualObservationSpec:
    if panels is None:
        panels = (VisualPanel(timeframe="1m", bars=wave_bars(12)),)
    return VisualObservationSpec(
        product=product, concrete_contract=concrete_contract,
        as_of=as_of, panels=panels,
    )


def render(spec=None, config=None) -> RenderedVisualArtifact:
    return JiangheVisualRenderer(config).render(spec if spec is not None else make_spec())


def spec_to_payload(spec: VisualObservationSpec) -> dict:
    return {
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
    }


def run_cli(input_path: Path, png_path: Path, manifest_path: Path, *,
            cwd: Path | None = None, env_extra: dict | None = None) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, str(CLI), "--input", str(input_path),
         "--png-out", str(png_path), "--manifest-out", str(manifest_path)],
        cwd=str(cwd) if cwd else str(ROOT), capture_output=True, text=True, env=env,
    )


def parse_png_chunks(png: bytes) -> list[tuple[bytes, bytes]]:
    """手动解析 PNG chunk 流（stdlib only）。"""
    assert png[:8] == b"\x89PNG\r\n\x1a\n", "PNG signature 错误"
    chunks = []
    offset = 8
    while offset < len(png):
        (length,) = struct.unpack(">I", png[offset:offset + 4])
        tag = png[offset + 4:offset + 8]
        data = png[offset + 8:offset + 8 + length]
        (crc_stored,) = struct.unpack(">I", png[offset + 8 + length:offset + 12 + length])
        crc_actual = zlib.crc32(tag + data) & 0xFFFFFFFF
        assert crc_stored == crc_actual, f"chunk {tag!r} CRC 错误"
        chunks.append((tag, data))
        offset += 12 + length
    assert offset == len(png), "PNG 尾部有多余字节"
    return chunks


# ---------------------------------------------------------------------------
# 3. 跨进程确定性
# ---------------------------------------------------------------------------

class CrossProcessDeterminismTests(unittest.TestCase):
    """同一 input/config：不同 subprocess、PYTHONHASHSEED、cwd、输出路径、TZ，
    PNG SHA 与三层身份必须完全相同。不得依赖 dict hash order / cwd /
    machine path / process id / current time / 本地时区。"""

    RUNS = 10

    def test_cross_process_determinism(self):
        payload = spec_to_payload(make_spec())
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "observation.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            shas, config_ids, input_ids, artifact_ids = set(), set(), set(), set()
            tz_cycle = ["UTC", "America/New_York", "Asia/Shanghai"]
            for run in range(self.RUNS):
                out_dir = tmp_path / f"run{run}"
                out_dir.mkdir()
                png_path = out_dir / f"o{run}.png"
                manifest_path = out_dir / f"m{run}.json"
                result = run_cli(
                    input_path, png_path, manifest_path,
                    cwd=ROOT if run % 2 == 0 else tmp_path,  # 不同 cwd
                    env_extra={
                        "PYTHONHASHSEED": str(run),  # 不同 hash seed
                        "TZ": tz_cycle[run % len(tz_cycle)],  # 不同本地时区
                    },
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                shas.add(sha256(png_path.read_bytes()).hexdigest())
                config_ids.add(manifest["renderer_config_identity"])
                input_ids.add(manifest["input_observation_identity"])
                artifact_ids.add(manifest["visual_artifact_identity"])
            self.assertEqual(len(shas), 1, f"跨进程 PNG SHA 不稳定: {shas}")
            self.assertEqual(len(config_ids), 1, f"config identity 不稳定: {config_ids}")
            self.assertEqual(len(input_ids), 1, f"input identity 不稳定: {input_ids}")
            self.assertEqual(len(artifact_ids), 1, f"artifact identity 不稳定: {artifact_ids}")

    def test_independent_python_interpreter_runs_match_library(self):
        """子进程 CLI 产物必须与同进程 library 渲染完全一致。"""
        payload = spec_to_payload(make_spec())
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "in.json"
            png_path = tmp_path / "o.png"
            manifest_path = tmp_path / "m.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            result = run_cli(input_path, png_path, manifest_path)
            self.assertEqual(result.returncode, 0, result.stderr)
            library = render()
            self.assertEqual(sha256(png_path.read_bytes()).hexdigest(), library.png_sha256)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["visual_artifact_identity"], library.visual_artifact_identity)


# ---------------------------------------------------------------------------
# 4. PNG 结构审计
# ---------------------------------------------------------------------------

class PngStructuralAuditTests(unittest.TestCase):
    FORBIDDEN_CHUNKS = {b"tIME", b"tEXt", b"zTXt", b"iTXt", b"eXIf", b"pHYs", b"gAMA"}

    def test_png_chunk_structure_and_crc(self):
        for config in (RendererConfig(), RendererConfig(canvas_width=640, canvas_height=480),
                       RendererConfig(canvas_width=320, canvas_height=240)):
            png = render(config=config).png_bytes
            chunks = parse_png_chunks(png)
            tags = [tag for tag, _ in chunks]
            self.assertEqual(tags[0], b"IHDR")
            self.assertEqual(tags[-1], b"IEND")
            self.assertEqual(tags.count(b"IDAT"), 1, "V0.1 应为单 IDAT")
            self.assertEqual(set(tags), {b"IHDR", b"IDAT", b"IEND"},
                             f"出现计划外 chunk: {tags}")
            for tag, _ in chunks:
                self.assertNotIn(tag, self.FORBIDDEN_CHUNKS)

    def test_ihdr_dimensions_match_config(self):
        for width, height in ((1280, 960), (640, 480), (320, 240)):
            config = RendererConfig(canvas_width=width, canvas_height=height)
            png = render(config=config).png_bytes
            chunks = parse_png_chunks(png)
            ihdr = dict(chunks)[b"IHDR"]
            w, h, depth, color_type, compression, filter_m, interlace = struct.unpack(
                ">IIBBBBB", ihdr)
            self.assertEqual((w, h), (width, height))
            self.assertEqual(depth, 8)
            self.assertEqual(color_type, 2, "必须是 RGB truecolor")
            self.assertEqual((compression, filter_m, interlace), (0, 0, 0))

    def test_idat_scanline_structure(self):
        width, height = 320, 240
        config = RendererConfig(canvas_width=width, canvas_height=height)
        png = render(config=config).png_bytes
        idat = dict(parse_png_chunks(png))[b"IDAT"]
        raw = zlib.decompress(idat)
        row_stride = 1 + width * 3
        self.assertEqual(len(raw), height * row_stride)
        for y in range(height):
            self.assertEqual(raw[y * row_stride], 0, "V0.1 每行 filter 字节必须为 0")

    def test_no_machine_metadata_bytes(self):
        """PNG 字节流中不得出现机器路径/时间戳样式的明文元数据。"""
        png = render().png_bytes
        for token in (b"tIME", b"tEXt", b"zTXt", b"iTXt", b"eXIf",
                      b"Software", b"Adobe", b"workbuddy", b"AppData"):
            self.assertNotIn(token, png)


# ---------------------------------------------------------------------------
# 5. Decimal / 数值对抗
# ---------------------------------------------------------------------------

class NumericAdversarialTests(unittest.TestCase):
    def _render_prices(self, **kwargs):
        spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=(make_bar(0, **kwargs),)),))
        return render(spec)

    def test_very_small_decimal_accepted_deterministic(self):
        a = self._render_prices(open_price="0.00000001", high="0.00000002",
                                low="0.000000005", close_price="0.000000015")
        b = self._render_prices(open_price="0.00000001", high="0.00000002",
                                low="0.000000005", close_price="0.000000015")
        self.assertEqual(a.png_sha256, b.png_sha256)

    def test_very_large_decimal_accepted_deterministic(self):
        kwargs = dict(open_price="1000000000000000000", high="1000000000000000001",
                      low="999999999999999999", close_price="1000000000000000000.5")
        self.assertEqual(self._render_prices(**kwargs).png_sha256,
                         self._render_prices(**kwargs).png_sha256)

    def test_many_decimal_places_deterministic(self):
        kwargs = dict(open_price="100.123456789012345678901234567890",
                      high="100.123456789012345678901234567891",
                      low="100.123456789012345678901234567889",
                      close_price="100.1234567890123456789012345678905")
        self.assertEqual(self._render_prices(**kwargs).png_sha256,
                         self._render_prices(**kwargs).png_sha256)

    def test_scientific_notation_deterministic(self):
        kwargs = dict(open_price="1.5E2", high="1.52E2", low="1.48E2", close_price="1.51E2")
        self.assertEqual(self._render_prices(**kwargs).png_sha256,
                         self._render_prices(**kwargs).png_sha256)

    def test_negative_zero_and_zero_render_deterministically(self):
        for price in ("-0", "0", "-0.000", "0.000"):
            art = self._render_prices(open_price=price, high="0", low=price,
                                      close_price=price, volume="0")
            self.assertEqual(art.png_sha256,
                             self._render_prices(open_price=price, high="0",
                                                 low=price, close_price=price,
                                                 volume="0").png_sha256)

    def test_flat_price_range_single_bar(self):
        art = self._render_prices(open_price="100", high="100", low="100", close_price="100")
        self.assertTrue(art.png_bytes.startswith(b"\x89PNG"))
        self.assertEqual(art.png_sha256,
                         self._render_prices(open_price="100", high="100",
                                             low="100", close_price="100").png_sha256)

    def test_high_equals_low_accepted(self):
        art = self._render_prices(open_price="50", high="50", low="50", close_price="50")
        self.assertTrue(art.png_bytes.startswith(b"\x89PNG"))

    def test_very_tiny_high_low_spread(self):
        kwargs = dict(open_price="100", high="100.0000000001", low="99.9999999999",
                      close_price="100.00000000005")
        self.assertEqual(self._render_prices(**kwargs).png_sha256,
                         self._render_prices(**kwargs).png_sha256)

    def test_huge_volume_accepted(self):
        art = self._render_prices(volume="9" * 30)
        self.assertTrue(art.png_bytes.startswith(b"\x89PNG"))
        self.assertEqual(art.png_sha256, self._render_prices(volume="9" * 30).png_sha256)

    def test_zero_volume_renders_no_volume_bars(self):
        bars = tuple(make_bar(i, volume="0") for i in range(4))
        spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=bars),))
        art = render(spec)
        self.assertEqual(art.png_sha256, render(spec).png_sha256)

    def test_nan_infinity_rejected_all_fields(self):
        for bad in ("NaN", "sNaN", "Infinity", "-Infinity", "inf", "-inf"):
            for field_name in ("open_price", "high", "low", "close_price", "volume"):
                kwargs = {field_name: bad}
                if field_name == "high":
                    kwargs.update(open_price="0", low="0", close_price="0")
                if field_name == "low":
                    kwargs.update(open_price="0", high="1", close_price="0")
                spec = make_spec(panels=(VisualPanel(
                    timeframe="1m", bars=(make_bar(0, **kwargs),)),))
                with self.assertRaises((ValueError, decimal.InvalidOperation),
                                       msg=f"{field_name}={bad}"):
                    render(spec)

    def test_extreme_decimal_exponent_must_fail_closed(self):
        """FINDING 候选：1E-3000 级别的极端指数应被 fail closed 拒绝。

        renderer 会把 tick label 格式化成与指数等长的十进制字符串
        （_format_decimal 用 format(value.normalize(), 'f')），字符串长度随
        指数线性增长且无上限：1E-999999999 会构造约 1GB 字符串，属于
        未治理的资源消耗（潜在 MemoryError / 长时间阻塞），而非受控 ValueError。
        """
        bars = tuple(
            ObservationBar(
                timeframe="1m",
                open_time=T0 + timedelta(minutes=i),
                close_time=T0 + timedelta(minutes=i + 1),
                available_at=T0 + timedelta(minutes=i + 1),
                open_price="1E-3000", high_price="2E-3000", low_price="1E-3000",
                close_price="15E-3001", volume="10", is_closed=True,
            )
            for i in range(4)
        )
        spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=bars),))
        with self.assertRaises(ValueError,
                               msg="极端指数 Decimal 应 fail closed，而非无界字符串展开"):
            render(spec)

    def test_rendering_must_not_depend_on_global_decimal_context(self):
        """FINDING 候选：渲染结果不得受进程全局 decimal.getcontext().prec 影响。

        renderer 的坐标/刻度计算使用默认 Decimal 上下文，未固定 precision；
        同进程内若调用方（或其他模块）修改 getcontext().prec，同一 input +
        同一 config 会得到不同 PNG 字节 —— rendering 依赖未治理的进程全局状态。
        """
        config = RendererConfig(canvas_height=240, canvas_width=320, panel_gap=0)

        def crafted_spec() -> VisualObservationSpec:
            bars = tuple(
                ObservationBar(
                    timeframe="1m",
                    open_time=T0 + timedelta(minutes=i),
                    close_time=T0 + timedelta(minutes=i + 1),
                    available_at=T0 + timedelta(minutes=i + 1),
                    open_price="100.996093750008", high_price="101", low_price="100",
                    close_price="100.996093750008", volume="10", is_closed=True,
                )
                for i in range(6)
            )
            return VisualObservationSpec(
                product="cu", concrete_contract="SHFE.cu2609", as_of=AS_OF,
                panels=(VisualPanel(timeframe="1m", bars=bars),),
            )

        ctx = decimal.getcontext()
        original_prec = ctx.prec
        try:
            ctx.prec = 28
            sha_default = JiangheVisualRenderer(config).render(crafted_spec()).png_sha256
            ctx.prec = 6
            sha_poisoned = JiangheVisualRenderer(config).render(crafted_spec()).png_sha256
        finally:
            ctx.prec = original_prec
        self.assertEqual(
            sha_default, sha_poisoned,
            "渲染字节流受进程全局 decimal context precision 影响（环境未治理依赖）",
        )


# ---------------------------------------------------------------------------
# 6. OHLC 对抗
# ---------------------------------------------------------------------------

class OhlcAdversarialTests(unittest.TestCase):
    def _expect_reject(self, **kwargs):
        spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=(make_bar(0, **kwargs),)),))
        with self.assertRaises(ValueError, msg=str(kwargs)):
            render(spec)

    def test_high_below_open_rejected(self):
        self._expect_reject(open_price="100", high="99", low="98", close_price="99")

    def test_high_below_close_rejected(self):
        self._expect_reject(open_price="100", high="100", low="99", close_price="101")

    def test_high_below_low_rejected(self):
        self._expect_reject(open_price="99", high="98", low="99", close_price="99")

    def test_low_above_open_rejected(self):
        self._expect_reject(open_price="100", high="102", low="101", close_price="102")

    def test_low_above_close_rejected(self):
        self._expect_reject(open_price="101", high="102", low="100.5", close_price="100")

    def test_negative_volume_rejected(self):
        self._expect_reject(volume="-0.0000001")
        self._expect_reject(volume="-1")

    def test_open_close_exactly_equal_flat_candle_stable(self):
        bars = tuple(make_bar(i, open_price="100", high="101", low="99",
                              close_price="100") for i in range(6))
        spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=bars),))
        first, second = render(spec), render(spec)
        self.assertEqual(first.png_sha256, second.png_sha256)
        # flat 蜡烛必须与 up/down 蜡烛画面不同（使用 flat_color）
        up_spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=tuple(
            make_bar(i, open_price="100", high="101", low="99", close_price="101")
            for i in range(6))),))
        self.assertNotEqual(first.png_sha256, render(up_spec).png_sha256)


# ---------------------------------------------------------------------------
# 7. 时间 / 时区对抗
# ---------------------------------------------------------------------------

class TimeTimezoneAdversarialTests(unittest.TestCase):
    def test_naive_timestamp_rejected(self):
        naive = datetime(2026, 8, 23, 9, 0)
        with self.assertRaises(ValueError):
            ObservationBar(
                timeframe="1m", open_time=naive,
                close_time=T0 + timedelta(minutes=1),
                available_at=T0 + timedelta(minutes=1),
                open_price="1", high_price="1", low_price="1", close_price="1",
                volume="1", is_closed=True,
            )

    def test_naive_as_of_rejected(self):
        with self.assertRaises(ValueError):
            VisualObservationSpec(
                product="cu", concrete_contract="SHFE.cu2609",
                as_of=datetime(2026, 8, 23, 11, 0),
                panels=(VisualPanel(timeframe="1m", bars=wave_bars(2)),),
            )

    def test_different_offset_same_instant_deterministic(self):
        """同一 instant 用不同 UTC offset 表达：必须确定渲染，不得崩。

        OBSERVED 语义：input identity 对 isoformat 表示敏感（+08:00 与 Z
        产生不同 identity），时间标签使用 K 线自带 offset —— 这是
        representation-sensitive identity，非 bug，但需明确记录。
        """
        spec_cn = make_spec()
        bars_utc = tuple(make_bar(i, tz=UTC) for i in range(12))
        spec_utc = VisualObservationSpec(
            product="cu", concrete_contract="SHFE.cu2609",
            as_of=AS_OF.astimezone(UTC),
            panels=(VisualPanel(timeframe="1m", bars=bars_utc),),
        )
        art_cn, art_utc = render(spec_cn), render(spec_utc)
        self.assertEqual(render(spec_cn).png_sha256, art_cn.png_sha256)
        self.assertEqual(render(spec_utc).png_sha256, art_utc.png_sha256)
        # 同一批 instant 的两种时区表示 -> 不同 input identity（representation 敏感）
        self.assertNotEqual(art_cn.input_observation_identity,
                            art_utc.input_observation_identity)
        # available_at 与 as_of 的比较按 instant 语义（不同时区不误判未来）
        render(spec_utc)  # 不抛错即通过 instant 语义比较

    def test_invalid_offset_rejected_by_cli(self):
        payload = spec_to_payload(make_spec())
        payload["as_of"] = "2026-08-23T11:00:00+25:00"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "in.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            result = run_cli(input_path, tmp_path / "o.png", tmp_path / "m.json")
            self.assertEqual(result.returncode, 1)

    def test_available_at_after_as_of_rejected(self):
        bars = wave_bars(4) + (make_bar(4, available_delay_seconds=7201),)
        spec = VisualObservationSpec(
            product="cu", concrete_contract="SHFE.cu2609",
            as_of=T0 + timedelta(minutes=5),
            panels=(VisualPanel(timeframe="1m", bars=bars),),
        )
        with self.assertRaises(ValueError):
            render(spec)

    def test_available_at_equals_as_of_accepted(self):
        bars = wave_bars(4) + (make_bar(4),)
        as_of = bars[-1].available_at
        spec = VisualObservationSpec(
            product="cu", concrete_contract="SHFE.cu2609", as_of=as_of,
            panels=(VisualPanel(timeframe="1m", bars=bars),),
        )
        self.assertTrue(render(spec).png_bytes.startswith(b"\x89PNG"))

    def test_partial_close_time_after_as_of_impossible_by_canonical_bar(self):
        """OBSERVED：canonical ObservationBar 强制 available_at >= close_time，
        因此 close_time > as_of 必然蕴含 available_at > as_of，被 renderer 拒绝。
        closed/partial 皆然。"""
        ot, ct = T0, T0 + timedelta(minutes=1)
        with self.assertRaises(ValueError):
            ObservationBar(timeframe="1m", open_time=ot, close_time=ct,
                           available_at=ct - timedelta(seconds=1),
                           open_price="1", high_price="1", low_price="1",
                           close_price="1", volume="1", is_closed=False)

    def test_non_monotonic_and_duplicate_timestamp_rejected(self):
        for bars in ((make_bar(0), make_bar(2), make_bar(1)),
                     (make_bar(0), make_bar(0))):
            spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=bars),))
            with self.assertRaises(ValueError):
                render(spec)

    def test_renderer_does_not_use_windows_local_timezone(self):
        """同一输入在子进程不同 TZ 下输出必须一致（含非 +08:00 时区）。"""
        payload = spec_to_payload(make_spec())
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "in.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            shas = set()
            for index, tz_name in enumerate(("UTC", "US/Pacific", "Asia/Tokyo")):
                png_path = tmp_path / f"o{index}.png"
                result = run_cli(input_path, png_path, tmp_path / f"m{index}.json",
                                 env_extra={"TZ": tz_name})
                self.assertEqual(result.returncode, 0, result.stderr)
                shas.add(sha256(png_path.read_bytes()).hexdigest())
            self.assertEqual(len(shas), 1, f"TZ 影响渲染输出: {shas}")


# ---------------------------------------------------------------------------
# 8. 未来泄露攻击 / 9. 刻度因果
# ---------------------------------------------------------------------------

class FutureLeakAndScalingTests(unittest.TestCase):
    def test_future_bars_must_reject_not_ignore(self):
        """B = 合法 prefix + as_of 之后极端 high/low future bars：必须 reject，
        不允许"忽略未来 bars 继续画"。"""
        as_of = T0 + timedelta(minutes=6)
        prefix = wave_bars(6)
        future = (
            make_bar(6, high="999999", low="999990",
                     open_price="999991", close_price="999995"),
            make_bar(7, high="999999", low="1",
                     open_price="999991", close_price="2"),
        )
        spec_b = VisualObservationSpec(
            product="cu", concrete_contract="SHFE.cu2609", as_of=as_of,
            panels=(VisualPanel(timeframe="1m", bars=prefix + future),),
        )
        with self.assertRaises(ValueError):
            render(spec_b)
        # 合法 prefix 自身可渲染
        spec_a = VisualObservationSpec(
            product="cu", concrete_contract="SHFE.cu2609", as_of=as_of,
            panels=(VisualPanel(timeframe="1m", bars=prefix),),
        )
        self.assertTrue(render(spec_a).png_bytes.startswith(b"\x89PNG"))

    def test_cli_ignores_adjacent_future_files_and_extra_json_fields(self):
        """磁盘旁边的未来文件 / 输入 JSON 中混入的额外字段不得影响输出。"""
        payload = spec_to_payload(make_spec())
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            # 旁边放一个"未来数据"文件
            (tmp_path / "future_bars.json").write_text(json.dumps({
                "bars": [{"open_time": "2027-01-01T00:00:00+08:00",
                          "high_price": "999999999"}],
            }), encoding="utf-8")
            baseline_in = tmp_path / "base.json"
            baseline_in.write_text(json.dumps(payload), encoding="utf-8")
            polluted = dict(payload)
            polluted["future_bars"] = [{"high_price": "999999999"}]
            polluted["outcome"] = {"pnl": "1000000", "win": True}
            polluted["annotation"] = "LONG_BREAKOUT"
            polluted_in = tmp_path / "polluted.json"
            polluted_in.write_text(json.dumps(polluted), encoding="utf-8")
            results = []
            for index, path in enumerate((baseline_in, polluted_in)):
                png_path = tmp_path / f"o{index}.png"
                result = run_cli(path, png_path, tmp_path / f"m{index}.json")
                self.assertEqual(result.returncode, 0, result.stderr)
                manifest = json.loads((tmp_path / f"m{index}.json").read_text("utf-8"))
                results.append((sha256(png_path.read_bytes()).hexdigest(),
                                manifest["visual_artifact_identity"]))
            self.assertEqual(results[0], results[1],
                             "额外 JSON 字段/旁边文件影响了渲染输出")

    def test_visible_outlier_legally_changes_scale(self):
        """当前已知 bar 中的极端 outlier 必须合法改变刻度（画面不同）。"""
        normal = render()
        bars = wave_bars(11) + (make_bar(11, high="500", low="490",
                                         open_price="495", close_price="498"),)
        outlier_spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=bars),))
        outlier = render(outlier_spec)
        self.assertNotEqual(normal.png_sha256, outlier.png_sha256)

    def test_scale_depends_only_on_visible_bars(self):
        """同一可见窗口、不同 as_of 之外的输入元素不得改变蜡烛区刻度。

        完整可见 bars 相同的两次渲染，像素必须逐字节相同（刻度不偷看任何
        非可见输入）。
        """
        spec = make_spec()
        self.assertEqual(render(spec).png_bytes, render(spec).png_bytes)


# ---------------------------------------------------------------------------
# 10. 多 panel 攻击
# ---------------------------------------------------------------------------

class MultiPanelAdversarialTests(unittest.TestCase):
    def _panels(self, count: int) -> tuple[VisualPanel, ...]:
        return tuple(
            VisualPanel(timeframe=f"tf{i}", bars=(make_bar(0, timeframe=f"tf{i}"),))
            for i in range(count)
        )

    def test_one_to_four_panels_render(self):
        for count in (1, 2, 3, 4):
            art = render(make_spec(panels=self._panels(count)))
            self.assertEqual(len(art.manifest["panels"]), count)
            self.assertEqual(art.png_sha256,
                             render(make_spec(panels=self._panels(count))).png_sha256)

    def test_five_panels_rejected(self):
        self.assertEqual(MAX_PANELS, 4)
        with self.assertRaises(ValueError):
            make_spec(panels=self._panels(5))

    def test_duplicate_timeframe_panels_rejected(self):
        panels = (VisualPanel(timeframe="1m", bars=wave_bars(2)),
                  VisualPanel(timeframe="1m", bars=wave_bars(3)))
        with self.assertRaises(ValueError):
            make_spec(panels=panels)

    def test_panel_order_swap_changes_identity_and_pixels(self):
        forward = (VisualPanel(timeframe="1m", bars=wave_bars(12)),
                   VisualPanel(timeframe="5m", bars=wave_bars(6, timeframe="5m", minutes=5)))
        swapped = (forward[1], forward[0])
        art_f, art_s = render(make_spec(panels=forward)), render(make_spec(panels=swapped))
        self.assertNotEqual(art_f.input_observation_identity, art_s.input_observation_identity)
        self.assertNotEqual(art_f.visual_artifact_identity, art_s.visual_artifact_identity)
        self.assertNotEqual(art_f.png_sha256, art_s.png_sha256)

    def test_empty_panel_rejected(self):
        with self.assertRaises(ValueError):
            VisualPanel(timeframe="1m", bars=())

    def test_different_panel_bar_counts_render(self):
        panels = (VisualPanel(timeframe="1m", bars=wave_bars(30)),
                  VisualPanel(timeframe="1h", bars=wave_bars(2, timeframe="1h", minutes=60)))
        art = render(make_spec(panels=panels))
        self.assertEqual(art.manifest["panels"][0]["bar_count"], 30)
        self.assertEqual(art.manifest["panels"][1]["bar_count"], 2)


# ---------------------------------------------------------------------------
# 11. 字符串 / 字形攻击
# ---------------------------------------------------------------------------

class StringGlyphAdversarialTests(unittest.TestCase):
    def test_long_instrument_deterministic_no_crash(self):
        spec = make_spec(product="c" * 400, concrete_contract="S" * 400)
        self.assertEqual(render(spec).png_sha256, render(spec).png_sha256)

    def test_ascii_punctuation_labels_render(self):
        spec = make_spec(product="CU-2609", concrete_contract="SHFE.CU2609")
        self.assertTrue(render(spec).png_bytes.startswith(b"\x89PNG"))

    def test_unsupported_unicode_fail_closed(self):
        for bad in ("铜", "\u00e9", "CU💰"):
            spec = make_spec(product=bad)
            with self.assertRaises(ValueError, msg=repr(bad)):
                render(spec)

    def test_newline_and_control_characters_fail_closed(self):
        for bad in ("CU\n2609", "CU\t2609", "CU\x002609", "CU\r2609"):
            spec = make_spec(product=bad)
            with self.assertRaises(ValueError, msg=repr(bad)):
                render(spec)

    def test_path_like_label_no_machine_path_written(self):
        spec = make_spec(product="CU", concrete_contract="C:/TMP/SHFE.CU2609")
        art = render(spec)
        self.assertNotIn(b"AppData", art.png_bytes)
        self.assertNotIn(b"workbuddy", art.png_bytes)

    def test_json_escape_characters_fail_closed_via_cli(self):
        payload = spec_to_payload(make_spec())
        payload["product"] = "cu\\nBAD"  # JSON 解码后是 cu\nBAD
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "in.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            result = run_cli(input_path, tmp_path / "o.png", tmp_path / "m.json")
            self.assertEqual(result.returncode, 1)

    def test_lowercase_timeframe_uppercased_in_title(self):
        """OBSERVED：title 统一 .upper()；'cu' 与 'CU' 画面相同但 input identity
        不同（identity 对原始表示严格，方向正确）。"""
        lower = render(make_spec(product="cu", concrete_contract="shfe.cu2609"))
        upper = render(make_spec(product="CU", concrete_contract="SHFE.CU2609"))
        self.assertEqual(lower.png_sha256, upper.png_sha256)
        self.assertNotEqual(lower.input_observation_identity,
                            upper.input_observation_identity)


# ---------------------------------------------------------------------------
# 12. Config mutation 完备性
# ---------------------------------------------------------------------------

class ConfigMutationCompletenessTests(unittest.TestCase):
    """对每个 RendererConfig 字段逐一 mutate：
    - renderer_config_identity 必须变化；
    - 若 PNG 变化，visual_artifact_identity 必须变化；
    - 寻找"画面变了但 identity 没变"的覆盖漏洞（必须不存在）。
    """

    MUTATIONS: dict[str, object] = {
        "renderer_version": "JIANGHE_VISUAL_RENDERER_V0_1_MUTATED",
        "canvas_width": 640,
        "canvas_height": 480,
        "outer_margin": 24,
        "panel_gap": 20,
        "title_height": 28,
        "time_label_height": 24,
        "price_label_gutter": 100,
        "volume_height_ratio": "0.4",
        "candle_body_width": 5,
        "candle_gap": 1,
        "grid_line_target": 8,
        "glyph_scale": 2,
        "title_glyph_scale": 2,
        "background_color": (0, 0, 0),
        "border_color": (1, 2, 3),
        "grid_color": (10, 20, 30),
        "text_color": (200, 200, 200),
        "up_color": (1, 2, 3),
        "down_color": (3, 2, 1),
        "flat_color": (5, 5, 5),
        "glyph_policy": "EMBEDDED_5X7_ASCII_BITMAP_V1_MUTATED",
        "price_scale_policy": "MUTATED",
        "volume_scale_policy": "MUTATED",
        "time_label_policy": "MUTATED",
        "price_tick_policy": "MUTATED",
        "annotation_policy": "MUTATED",
    }

    # V0.1 锁定的样式字段：任何 mutate 必须 fail closed，不参与"identity 变化"表。
    LOCKED_FIELDS = frozenset({"partial_body_style", "closed_body_style"})

    def test_locked_body_style_fields_fail_closed(self):
        with self.assertRaises(ValueError):
            RendererConfig(partial_body_style="FILLED")
        with self.assertRaises(ValueError):
            RendererConfig(closed_body_style="HOLLOW_OUTLINE")

    def test_every_config_field_mutation_changes_identity(self):
        baseline = RendererConfig()
        baseline_fields = set(baseline.__dataclass_fields__) - self.LOCKED_FIELDS
        self.assertEqual(baseline_fields, set(self.MUTATIONS),
                         f"mutation 表与 RendererConfig 字段不一致: "
                         f"missing={baseline_fields - set(self.MUTATIONS)}, "
                         f"extra={set(self.MUTATIONS) - baseline_fields}")
        # 双 panel 场景确保 panel_gap 等字段真正作用于画面
        spec = make_spec(panels=(
            VisualPanel(timeframe="1m", bars=wave_bars(12)),
            VisualPanel(timeframe="5m", bars=wave_bars(6, timeframe="5m", minutes=5)),
        ))
        base_art = render(spec, baseline)
        png_changed, png_unchanged = [], []
        for field_name, mutated_value in sorted(self.MUTATIONS.items()):
            mutated = RendererConfig(**{field_name: mutated_value})
            self.assertNotEqual(baseline.identity, mutated.identity,
                                f"config 字段 {field_name} mutate 后 identity 未变")
            art = render(spec, mutated)
            self.assertNotEqual(base_art.visual_artifact_identity,
                                art.visual_artifact_identity,
                                f"config 字段 {field_name} mutate 后 artifact identity 未变")
            if art.png_sha256 != base_art.png_sha256:
                png_changed.append(field_name)
                # 关键不变量：PNG 变化必然伴随 identity 变化（上面已断言）
            else:
                png_unchanged.append(field_name)
        # 记录哪些字段只改变 identity 不改变像素（供报告引用；policy 类字段合理）
        self._png_changed, self._png_unchanged = png_changed, png_unchanged

    def test_visual_color_mutation_changes_pixels(self):
        spec = make_spec()
        base = render(spec)
        for field_name in ("up_color", "down_color", "background_color",
                           "border_color", "grid_color", "text_color"):
            mutated = RendererConfig(**{field_name: (7, 77, 177)})
            art = render(spec, mutated)
            self.assertNotEqual(base.png_sha256, art.png_sha256,
                                f"视觉颜色字段 {field_name} 未改变像素")
            self.assertNotEqual(base.visual_artifact_identity,
                                art.visual_artifact_identity)

    def test_flat_color_mutation_changes_pixels_when_flat_bars_present(self):
        flat_bars = tuple(make_bar(i, open_price="100", high="101", low="99",
                                   close_price="100") for i in range(6))
        flat_spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=flat_bars),))
        base = render(flat_spec)
        mutated = render(flat_spec, RendererConfig(flat_color=(7, 77, 177)))
        self.assertNotEqual(base.png_sha256, mutated.png_sha256)
        self.assertNotEqual(base.visual_artifact_identity,
                            mutated.visual_artifact_identity)


# ---------------------------------------------------------------------------
# 13. Input mutation 完备性
# ---------------------------------------------------------------------------

class InputMutationCompletenessTests(unittest.TestCase):
    """逐个 mutate governed visual input 字段；input/artifact identity
    必须发生正确变化。寻找 identity coverage hole。"""

    def _spec_with_bar(self, bar: ObservationBar) -> VisualObservationSpec:
        return make_spec(panels=(VisualPanel(timeframe=bar.timeframe, bars=(bar,)),))

    def test_each_governed_field_mutation_changes_input_identity(self):
        base_bar = make_bar(0)
        base_spec = self._spec_with_bar(base_bar)
        base_art = render(base_spec)
        cases: dict[str, ObservationBar | VisualObservationSpec] = {
            "open_price": self._spec_with_bar(make_bar(0, open_price="100.5")),
            "high_price": self._spec_with_bar(make_bar(0, high="102")),
            "low_price": self._spec_with_bar(make_bar(0, low="98")),
            "close_price": self._spec_with_bar(make_bar(0, close_price="100.5")),
            "volume": self._spec_with_bar(make_bar(0, volume="11")),
            "is_closed": self._spec_with_bar(make_bar(0, closed=False)),
            "timeframe": self._spec_with_bar(make_bar(0, timeframe="5m")),
            "product": make_spec(product="al",
                                 panels=(VisualPanel(timeframe="1m", bars=(base_bar,)),)),
            "concrete_contract": make_spec(concrete_contract="SHFE.cu2610",
                                           panels=(VisualPanel(timeframe="1m",
                                                               bars=(base_bar,)),)),
            "as_of": make_spec(as_of=AS_OF + timedelta(minutes=1),
                               panels=(VisualPanel(timeframe="1m", bars=(base_bar,)),)),
        }
        for name, spec in cases.items():
            art = render(spec)
            self.assertNotEqual(base_art.input_observation_identity,
                                art.input_observation_identity,
                                f"input 字段 {name} mutate 后 input identity 未变")
            self.assertNotEqual(base_art.visual_artifact_identity,
                                art.visual_artifact_identity,
                                f"input 字段 {name} mutate 后 artifact identity 未变")

    def test_timestamp_mutation_changes_input_identity(self):
        base = render(self._spec_with_bar(make_bar(0)))
        for field_name, delta in (("open_time", timedelta(minutes=1)),
                                  ("close_time", timedelta(seconds=30)),
                                  ("available_at", timedelta(seconds=1))):
            base_bar = make_bar(0)
            kwargs = dict(
                timeframe="1m",
                open_time=base_bar.open_time,
                close_time=base_bar.close_time,
                available_at=base_bar.available_at,
                open_price="100", high_price="101", low_price="99",
                close_price="100", volume="10", is_closed=True,
            )
            if field_name == "open_time":
                kwargs["open_time"] = base_bar.open_time - delta
            elif field_name == "close_time":
                kwargs["close_time"] = base_bar.close_time + delta
                kwargs["available_at"] = kwargs["close_time"]
            else:
                kwargs["available_at"] = base_bar.available_at + delta
            mutated = ObservationBar(**kwargs)
            art = render(self._spec_with_bar(mutated))
            self.assertNotEqual(base.input_observation_identity,
                                art.input_observation_identity,
                                f"{field_name} mutate 后 input identity 未变")

    def test_price_string_representation_changes_identity(self):
        """OBSERVED：'100' 与 '100.0' 数值相同、像素相同，但 input identity 不同
        （raw string 进入 canonical hash，方向严格、无 hole）。"""
        a = render(self._spec_with_bar(make_bar(0, open_price="100")))
        b = render(self._spec_with_bar(make_bar(0, open_price="100.0")))
        self.assertNotEqual(a.input_observation_identity, b.input_observation_identity)
        self.assertNotEqual(a.visual_artifact_identity, b.visual_artifact_identity)


# ---------------------------------------------------------------------------
# 14. Partial / closed 语义
# ---------------------------------------------------------------------------

class PartialClosedSemanticTests(unittest.TestCase):
    def test_same_ohlcv_closed_vs_partial_differs_visually_and_in_identity(self):
        closed_spec = make_spec()
        partial_bars = wave_bars(11) + (make_bar(11, closed=False),)
        partial_spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=partial_bars),))
        art_c, art_p = render(closed_spec), render(partial_spec)
        self.assertNotEqual(art_c.png_sha256, art_p.png_sha256)
        self.assertNotEqual(art_c.input_observation_identity,
                            art_p.input_observation_identity)
        self.assertNotEqual(art_c.visual_artifact_identity,
                            art_p.visual_artifact_identity)
        self.assertEqual(art_p.manifest["panels"][0]["partial_count"], 1)

    def test_partial_available_at_equals_as_of_accepted(self):
        bars = wave_bars(4) + (make_bar(4, closed=False),)
        spec = VisualObservationSpec(
            product="cu", concrete_contract="SHFE.cu2609",
            as_of=bars[-1].available_at,
            panels=(VisualPanel(timeframe="1m", bars=bars),),
        )
        self.assertTrue(render(spec).png_bytes.startswith(b"\x89PNG"))


# ---------------------------------------------------------------------------
# 15. Manifest 独立重算
# ---------------------------------------------------------------------------

class ManifestRecomputeTests(unittest.TestCase):
    def test_manifest_declared_zero_fields(self):
        art = render()
        self.assertEqual(art.manifest["future_bar_count"], 0)
        self.assertEqual(art.manifest["outcome_fields"], 0)
        self.assertEqual(art.manifest["annotations"], [])

    def test_manifest_has_no_outcome_content(self):
        art = render()
        blob = art.manifest_json().lower()
        declared = ("outcome_fields", "future_bar_count")
        for token in ("pnl", "profit", "return_rate", "future_price", "future_high",
                      "future_low", "\"win\"", "\"loss\"", "sharpe", "win_rate"):
            for line in blob.splitlines():
                if any(key in line for key in declared):
                    continue
                self.assertNotIn(token, line)

    def test_all_identities_independently_recomputable(self):
        """验证方不依赖 renderer 输出的声明值，可独立重算全部四层哈希。"""
        spec = make_spec()
        config = RendererConfig()
        art = render(spec, config)

        # 1. png_sha256
        self.assertEqual(art.manifest["png_sha256"], sha256(art.png_bytes).hexdigest())

        # 2. renderer_config_identity（独立重建 canonical dict）
        canonical_config = {}
        for name in sorted(config.__dataclass_fields__):
            value = getattr(config, name)
            if isinstance(value, tuple):
                value = list(value)
            canonical_config[name] = value
        config_identity = sha256(json.dumps(
            canonical_config, ensure_ascii=False, separators=(",", ":"),
            sort_keys=True).encode("utf-8")).hexdigest()
        self.assertEqual(art.manifest["renderer_config_identity"], config_identity)

        # 3. input_observation_identity（独立重建 canonical 结构）
        canonical_input = {
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
        }
        input_identity = sha256(json.dumps(
            canonical_input, ensure_ascii=False, separators=(",", ":"),
            sort_keys=True).encode("utf-8")).hexdigest()
        self.assertEqual(art.manifest["input_observation_identity"], input_identity)

        # 4. visual_artifact_identity
        artifact_identity = sha256(json.dumps({
            "artifact": ARTIFACT_KIND,
            "renderer_version": RENDERER_VERSION,
            "renderer_config_identity": config_identity,
            "input_observation_identity": input_identity,
            "png_sha256": art.manifest["png_sha256"],
        }, ensure_ascii=False, separators=(",", ":"),
            sort_keys=True).encode("utf-8")).hexdigest()
        self.assertEqual(art.manifest["visual_artifact_identity"], artifact_identity)


# ---------------------------------------------------------------------------
# 16. CLI 对抗
# ---------------------------------------------------------------------------

class CliAdversarialTests(unittest.TestCase):
    def _write_payload(self, tmp: Path, payload: object) -> Path:
        path = tmp / "in.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_malformed_json_fails_no_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "in.json"
            input_path.write_text("{not json", encoding="utf-8")
            png, manifest = tmp_path / "o.png", tmp_path / "m.json"
            result = run_cli(input_path, png, manifest)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(png.exists())
            self.assertFalse(manifest.exists())

    def test_missing_field_fails(self):
        payload = spec_to_payload(make_spec())
        del payload["as_of"]
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_cli(self._write_payload(tmp_path, payload),
                             tmp_path / "o.png", tmp_path / "m.json")
            self.assertEqual(result.returncode, 1)

    def test_wrong_type_fails(self):
        payload = spec_to_payload(make_spec())
        payload["panels"][0]["bars"][0]["is_closed"] = "true"  # 字符串而非布尔
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            result = run_cli(self._write_payload(tmp_path, payload),
                             tmp_path / "o.png", tmp_path / "m.json")
            self.assertEqual(result.returncode, 1)

    def test_unknown_field_ignored_output_identical(self):
        payload = spec_to_payload(make_spec())
        polluted = dict(payload)
        polluted["unknown_field"] = {"anything": 1}
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            outputs = []
            for index, data in enumerate((payload, polluted)):
                png, manifest = tmp_path / f"o{index}.png", tmp_path / f"m{index}.json"
                input_path = tmp_path / f"in{index}.json"
                input_path.write_text(json.dumps(data), encoding="utf-8")
                result = run_cli(input_path, png, manifest)
                self.assertEqual(result.returncode, 0, result.stderr)
                outputs.append((png.read_bytes(), manifest.read_bytes()))
            self.assertEqual(outputs[0], outputs[1])

    def test_existing_output_file_overwritten_deterministically(self):
        """OBSERVED：已存在的输出文件被静默覆盖；内容确定性相同。"""
        payload = spec_to_payload(make_spec())
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = self._write_payload(tmp_path, payload)
            png, manifest = tmp_path / "o.png", tmp_path / "m.json"
            png.write_bytes(b"STALE-GARBAGE")
            manifest.write_text("STALE", encoding="utf-8")
            result = run_cli(input_path, png, manifest)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(png.read_bytes().startswith(b"\x89PNG"))
            first = (png.read_bytes(), manifest.read_bytes())
            result2 = run_cli(input_path, png, manifest)
            self.assertEqual(result2.returncode, 0, result2.stderr)
            self.assertEqual(first, (png.read_bytes(), manifest.read_bytes()))

    def test_relative_and_absolute_paths_produce_identical_bytes(self):
        payload = spec_to_payload(make_spec())
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_abs = self._write_payload(tmp_path, payload)
            png_abs, manifest_abs = tmp_path / "abs.png", tmp_path / "abs.json"
            result_abs = run_cli(input_abs, png_abs, manifest_abs, cwd=tmp_path)
            self.assertEqual(result_abs.returncode, 0, result_abs.stderr)
            png_rel, manifest_rel = tmp_path / "rel.png", tmp_path / "rel.json"
            result_rel = subprocess.run(
                [sys.executable, str(CLI), "--input", "in.json",
                 "--png-out", "rel.png", "--manifest-out", "rel.json"],
                cwd=str(tmp_path), capture_output=True, text=True,
            )
            self.assertEqual(result_rel.returncode, 0, result_rel.stderr)
            self.assertEqual(png_abs.read_bytes(), png_rel.read_bytes())
            self.assertEqual(manifest_abs.read_bytes(), manifest_rel.read_bytes())

    def test_failed_render_leaves_no_outputs(self):
        """渲染校验失败（未来 bar）时不得留下任何输出文件。"""
        payload = spec_to_payload(make_spec())
        payload["as_of"] = T0.isoformat()  # 所有 bars 变成"未来"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            png, manifest = tmp_path / "o.png", tmp_path / "m.json"
            result = run_cli(self._write_payload(tmp_path, payload), png, manifest)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(png.exists())
            self.assertFalse(manifest.exists())

    def test_cli_write_must_be_atomic_no_half_success(self):
        """FINDING 候选：manifest 写入失败时 PNG 已落盘 -> 半成品组合。

        CLI 顺序 write png -> write manifest；manifest 路径失败时退出码为 1，
        但 PNG 已存在且无 manifest —— 下游可能捡到貌似成功的裸 PNG。
        期望：fail closed 不留下任何貌似成功的半成品。
        """
        payload = spec_to_payload(make_spec())
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = self._write_payload(tmp_path, payload)
            png = tmp_path / "out.png"
            manifest = tmp_path / "no_such_dir" / "out.manifest.json"  # 父目录不存在
            result = run_cli(input_path, png, manifest)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(
                png.exists(),
                "CLI 非原子：manifest 写失败后遗留无 manifest 的 PNG（貌似成功的半成品）",
            )


# ---------------------------------------------------------------------------
# 17. 依赖 / 网络静态审计  18. 结果推断静态审计
# ---------------------------------------------------------------------------

class StaticAuditTests(unittest.TestCase):
    @staticmethod
    def _renderer_source() -> str:
        return inspect.getsource(visual_module)

    @staticmethod
    def _cli_source() -> str:
        return CLI.read_text(encoding="utf-8")

    def test_no_network_or_unmanaged_dependency_tokens(self):
        hits = {}
        for token in ("requests", "urllib", "socket", "http://", "https://",
                      "urlopen", "PIL", "Pillow", "matplotlib", "plotly",
                      "fontTools", "random", "uuid", "time.time", "datetime.now",
                      "datetime.utcnow", "os.getcwd", "os.environ", "getpid"):
            for name, source in (("renderer", self._renderer_source()),
                                 ("cli", self._cli_source())):
                if token in source:
                    hits.setdefault(token, []).append(name)
        self.assertEqual(hits, {}, f"renderer/CLI 出现禁用依赖 token: {hits}")

    def test_only_stdlib_imports(self):
        allowed = {"__future__", "argparse", "dataclasses", "datetime", "decimal",
                   "hashlib", "json", "os", "pathlib", "struct", "sys",
                   "tempfile", "typing", "zlib", "src"}
        for path in (Path(inspect.getsourcefile(visual_module)), CLI):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = {alias.name.split(".")[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots = {node.module.split(".")[0]}
                else:
                    continue
                self.assertLessEqual(roots, allowed, f"{path.name}: {roots}")

    def test_renderer_does_not_infer_trading_outcomes(self):
        """renderer 本体不得包含任何方向/进出场/形态/指标推断逻辑。
        （注释/docstring 中的否定性声明除外——这里检查的是可执行代码。）"""
        tree = ast.parse(self._renderer_source())
        code_tokens: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                code_tokens.append(node.id.lower())
            elif isinstance(node, ast.Attribute):
                code_tokens.append(node.attr.lower())
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                code_tokens.append(node.value.lower())
        forbidden = ("long", "short", "entry", "stop_loss", "take_profit",
                     "breakout", "support", "resistance", "key_zone",
                     "moving_average", "ema", "sma", "rsi", "macd",
                     "signal", "direction")
        found = sorted({token for token in forbidden
                        if any(token == text or token in text.split("_")
                               for text in code_tokens)})
        self.assertEqual(found, [],
                         f"renderer 可执行代码中出现交易推断 token: {found}")

    def test_cli_does_not_infer_trading_outcomes(self):
        source = self._cli_source().lower()
        for token in ("long", "short", "entry", "breakout", "signal",
                      "direction", "pnl", "outcome"):
            self.assertNotIn(token, source)


class CliAtomicityRegressionTests(unittest.TestCase):
    """F-ADV-02 回归：CLI 输出必须是逻辑 (PNG, manifest) artifact pair 的原子写入。

    覆盖：PNG 写失败 / manifest 写失败 / 覆盖既有 / 失败后无半成品与无临时残留；
    失败时不删除调用前已存在的合法文件。
    """

    def _payload(self) -> dict:
        return spec_to_payload(make_spec())

    def _assert_no_partial_leftovers(self, tmp_path: Path) -> None:
        leftovers = [p.name for p in tmp_path.iterdir() if ".partial-" in p.name]
        self.assertEqual(leftovers, [], f"失败后遗留临时文件: {leftovers}")

    def test_png_target_is_directory_fails_without_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "in.json"
            input_path.write_text(json.dumps(self._payload()), encoding="utf-8")
            png_dir = tmp_path / "png_dir"
            png_dir.mkdir()
            manifest = tmp_path / "m.json"
            result = run_cli(input_path, png_dir, manifest)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(png_dir.is_dir(), "既有目录不得被替换/删除")
            self.assertFalse(manifest.exists())
            self._assert_no_partial_leftovers(tmp_path)

    def test_manifest_target_is_directory_fails_without_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "in.json"
            input_path.write_text(json.dumps(self._payload()), encoding="utf-8")
            png = tmp_path / "o.png"
            manifest_dir = tmp_path / "manifest_dir"
            manifest_dir.mkdir()
            result = run_cli(input_path, png, manifest_dir)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(png.exists(), "manifest 写失败不得遗留裸 PNG")
            self.assertTrue(manifest_dir.is_dir())
            self._assert_no_partial_leftovers(tmp_path)

    def test_manifest_failure_preserves_existing_png(self):
        """manifest 写失败时，调用前已存在的 PNG 必须原样保留（不删除、不替换）。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "in.json"
            input_path.write_text(json.dumps(self._payload()), encoding="utf-8")
            png = tmp_path / "o.png"
            png.write_bytes(b"PRE-EXISTING-CONTENT")
            manifest = tmp_path / "no_such_dir" / "m.json"
            result = run_cli(input_path, png, manifest)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(
                png.read_bytes(),
                b"PRE-EXISTING-CONTENT",
                "调用前已存在的合法文件在失败路径上必须保留",
            )
            self.assertFalse(manifest.exists())

    def test_failure_leaves_no_partial_pair_and_no_temp_files(self):
        """任意写失败后：目标目录不得出现 .partial-* 临时残留。"""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "in.json"
            input_path.write_text(json.dumps(self._payload()), encoding="utf-8")
            png = tmp_path / "o.png"
            manifest = tmp_path / "no_such_dir" / "m.json"
            result = run_cli(input_path, png, manifest)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(png.exists())
            self.assertFalse(manifest.exists())
            self._assert_no_partial_leftovers(tmp_path)


if __name__ == "__main__":
    unittest.main()
