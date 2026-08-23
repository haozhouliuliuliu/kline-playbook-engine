"""合成对抗测试：江河 VISUAL 观察渲染器 V0.1（无真实行情、无模型、无网络、无结果）。"""

from __future__ import annotations

import inspect
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

import src.jianghe_visual_renderer as visual_module
from src.jianghe_ai_trader import ObservationBar
from src.jianghe_visual_renderer import (
    ARTIFACT_KIND,
    JiangheVisualRenderer,
    RENDERER_VERSION,
    RenderedVisualArtifact,
    RendererConfig,
    VisualObservationSpec,
    VisualPanel,
    panels_from_observation_bars,
)


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "tools" / "render_jianghe_visual_observation_v0_1.py"
CN = timezone(timedelta(hours=8))
T0 = datetime(2026, 8, 23, 9, 0, tzinfo=CN)

# golden fixture：固定小型输入的确定性身份（由确定性 renderer 重建验证）。
GOLDEN_PNG_SHA256 = "ff7d849417c9d7eea2c050afaf3e3879b3251d2d93ca503f2e60076afd93cdb8"
GOLDEN_CONFIG_IDENTITY = "2397764a0f3e2b453456fd8735caeb59881d19ea5a2399fc91fb7e7307525851"
GOLDEN_ARTIFACT_IDENTITY = "1c2da6d7cb43f9db6f68cf2b384981655fc6987e0c77340bfceae43e32a211a2"


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
    available_delay_seconds: int = 0,
) -> ObservationBar:
    open_time = T0 + timedelta(minutes=index * minutes)
    close_time = open_time + timedelta(minutes=minutes)
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


def make_spec(*, panels: tuple[VisualPanel, ...] | None = None) -> VisualObservationSpec:
    if panels is None:
        panels = (VisualPanel(timeframe="1m", bars=wave_bars(12)),)
    return VisualObservationSpec(
        product="cu",
        concrete_contract="SHFE.cu2609",
        as_of=T0 + timedelta(hours=2),
        panels=panels,
    )


def render(spec: VisualObservationSpec | None = None, config: RendererConfig | None = None) -> RenderedVisualArtifact:
    return JiangheVisualRenderer(config).render(spec if spec is not None else make_spec())


def _walk_strings(value: object, *, skip_keys: frozenset[str] = frozenset()) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str) and key in skip_keys:
                continue
            found.extend(_walk_strings(key, skip_keys=skip_keys))
            found.extend(_walk_strings(item, skip_keys=skip_keys))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.extend(_walk_strings(item, skip_keys=skip_keys))
    elif isinstance(value, str):
        found.append(value)
    return found


class DeterminismTests(unittest.TestCase):
    def test_deterministic_png_bytes(self):
        first, second = render(), render()
        self.assertEqual(first.png_bytes, second.png_bytes)
        self.assertEqual(first.png_sha256, second.png_sha256)

    def test_deterministic_renderer_config_identity(self):
        self.assertEqual(RendererConfig().identity, RendererConfig().identity)
        self.assertEqual(render().renderer_config_identity, RendererConfig().identity)

    def test_deterministic_visual_artifact_identity(self):
        self.assertEqual(render().visual_artifact_identity, render().visual_artifact_identity)

    def test_png_signature_and_mime(self):
        artifact = render()
        self.assertTrue(artifact.png_bytes.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertEqual(artifact.manifest["image"]["mime"], "image/png")
        self.assertEqual(artifact.manifest["image"]["width"], 1280)
        self.assertEqual(artifact.manifest["image"]["height"], 960)

    def test_same_input_config_same_sha(self):
        spec = make_spec()
        self.assertEqual(render(spec).png_sha256, render(spec).png_sha256)

    def test_config_change_changes_identity(self):
        baseline = RendererConfig()
        changed = RendererConfig(up_color=(1, 2, 3))
        self.assertNotEqual(baseline.identity, changed.identity)
        self.assertNotEqual(render(config=baseline).visual_artifact_identity,
                            render(config=changed).visual_artifact_identity)

    def test_bar_change_changes_visual_artifact_identity(self):
        original = render().visual_artifact_identity
        moved = wave_bars(12)[:5] + (make_bar(5, close_price="120", high="121"),) + wave_bars(12)[6:]
        altered = render(make_spec(panels=(VisualPanel(timeframe="1m", bars=moved),)))
        self.assertNotEqual(original, altered.visual_artifact_identity)
        self.assertNotEqual(render().input_observation_identity, altered.input_observation_identity)

    def test_golden_fixture(self):
        artifact = render()
        self.assertEqual(artifact.png_sha256, GOLDEN_PNG_SHA256)
        self.assertEqual(artifact.renderer_config_identity, GOLDEN_CONFIG_IDENTITY)
        self.assertEqual(artifact.visual_artifact_identity, GOLDEN_ARTIFACT_IDENTITY)

    def test_multi_panel_deterministic(self):
        panels = (
            VisualPanel(timeframe="1m", bars=wave_bars(24)),
            VisualPanel(timeframe="5m", bars=wave_bars(12, timeframe="5m", minutes=5)),
            VisualPanel(timeframe="15m", bars=wave_bars(8, timeframe="15m", minutes=15)),
        )
        spec = make_spec(panels=panels)
        first, second = render(spec), render(spec)
        self.assertEqual(first.png_bytes, second.png_bytes)
        self.assertEqual(len(first.manifest["panels"]), 3)
        self.assertNotEqual(first.png_sha256, render().png_sha256)


class CausalRejectionTests(unittest.TestCase):
    def test_future_available_at_rejected(self):
        bars = wave_bars(4) + (make_bar(4, available_delay_seconds=7201),)
        spec = VisualObservationSpec(
            product="cu", concrete_contract="SHFE.cu2609",
            as_of=T0 + timedelta(minutes=5),
            panels=(VisualPanel(timeframe="1m", bars=bars),),
        )
        with self.assertRaises(ValueError):
            render(spec)

    def test_duplicate_timestamp_rejected(self):
        bars = wave_bars(4) + (make_bar(3),)
        spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=bars),))
        with self.assertRaises(ValueError):
            render(spec)

    def test_non_monotonic_timestamp_rejected(self):
        bars = (make_bar(0), make_bar(2), make_bar(1))
        spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=bars),))
        with self.assertRaises(ValueError):
            render(spec)

    def test_invalid_ohlc_rejected(self):
        for kwargs in (
            {"high": "99", "open_price": "100"},   # high < open
            {"high": "100", "close_price": "101"},  # high < close
            {"low": "101", "open_price": "100"},    # low > open
            {"low": "100.5", "close_price": "100"},  # low > close
            {"high": "98", "low": "99"},            # high < low
        ):
            spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=(make_bar(0, **kwargs),)),))
            with self.assertRaises(ValueError, msg=str(kwargs)):
                render(spec)

    def test_negative_volume_rejected(self):
        spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=(make_bar(0, volume="-1"),)),))
        with self.assertRaises(ValueError):
            render(spec)

    def test_nan_and_infinity_rejected(self):
        for bad in ("NaN", "Infinity", "-Infinity"):
            spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=(make_bar(0, close_price=bad),)),))
            with self.assertRaises(ValueError, msg=bad):
                render(spec)

    def test_too_many_bars_rejected_not_cropped(self):
        spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=wave_bars(500)),))
        with self.assertRaises(ValueError):
            render(spec)

    def test_naive_timestamp_rejected(self):
        naive = datetime(2026, 8, 23, 9, 0)
        with self.assertRaises(ValueError):
            ObservationBar(
                timeframe="1m", open_time=naive, close_time=T0 + timedelta(minutes=1),
                available_at=T0 + timedelta(minutes=1), open_price="1", high_price="1",
                low_price="1", close_price="1", volume="1", is_closed=True,
            )


class CausalContentTests(unittest.TestCase):
    def test_no_future_bars_included(self):
        artifact = render()
        self.assertEqual(artifact.manifest["future_bar_count"], 0)
        as_of = datetime.fromisoformat(str(artifact.manifest["as_of"]))
        for panel in artifact.manifest["panels"]:
            latest = datetime.fromisoformat(str(panel["latest_available_at"]))
            self.assertLessEqual(latest, as_of)
            self.assertEqual(datetime.fromisoformat(str(panel["first_bar_open_time"])), T0)

    def test_partial_bar_renders_differently_from_closed(self):
        closed_spec = make_spec()
        partial_bars = wave_bars(11) + (make_bar(11, closed=False),)
        partial_spec = make_spec(panels=(VisualPanel(timeframe="1m", bars=partial_bars),))
        closed_artifact = render(closed_spec)
        partial_artifact = render(partial_spec)
        self.assertNotEqual(closed_artifact.png_sha256, partial_artifact.png_sha256)
        differing = sum(
            1 for a, b in zip(closed_artifact.png_bytes, partial_artifact.png_bytes) if a != b
        )
        self.assertGreater(differing, 0)
        panel = partial_artifact.manifest["panels"][0]
        self.assertEqual(panel["partial_count"], 1)
        self.assertEqual(panel["closed_count"], 11)

    def test_manifest_has_no_outcome_or_pnl_fields(self):
        artifact = render()
        self.assertEqual(artifact.manifest["outcome_fields"], 0)
        self.assertEqual(artifact.manifest["annotations"], [])
        forbidden = ("pnl", "outcome", "profit", "sharpe", "win_rate", "expectancy",
                     "future_return", "future_high", "future_low")
        # outcome_fields / future_bar_count 是协议要求的显式零值声明，豁免扫描。
        declared_zero_keys = frozenset({"outcome_fields", "future_bar_count"})
        for text in _walk_strings(artifact.manifest, skip_keys=declared_zero_keys):
            for token in forbidden:
                self.assertNotIn(token, text.lower())

    def test_renderer_does_not_infer_trading_decisions(self):
        artifact = render()
        forbidden = ("family", "direction", "entry", "stop", "target", "trend",
                     "support", "resistance", "key_zone", "breakout",
                     "long", "short", "signal")
        keys = [text for text in _walk_strings(artifact.manifest)]
        for text in keys:
            lowered = text.lower()
            for token in ("entry", "stop", "target", "trend", "support",
                          "resistance", "breakout", "signal"):
                self.assertNotIn(token, lowered)
        self.assertNotIn("family", keys)
        self.assertNotIn("direction", keys)


class ProviderNeutralAndEnvironmentTests(unittest.TestCase):
    @staticmethod
    def _sources() -> str:
        return inspect.getsource(visual_module) + "\n" + CLI.read_text(encoding="utf-8")

    def test_no_network_calls(self):
        source = self._sources()
        for token in ("socket", "urllib", "requests", "http://", "https://", "urlopen"):
            self.assertNotIn(token, source)

    def test_no_random_or_system_clock_dependency(self):
        source = self._sources()
        for token in ("random", "uuid", "time.time", "datetime.now",
                      "datetime.utcnow", "time_ns", "monotonic"):
            self.assertNotIn(token, source)

    def test_no_machine_font_dependency(self):
        source = self._sources()
        for token in ("PIL", "Pillow", "matplotlib", "fontTools", "tkinter",
                      "ctypes", "win32", "SystemFonts"):
            self.assertNotIn(token, source)

    def test_provider_neutral(self):
        artifact = render()
        self.assertEqual(artifact.manifest["provider"], "PROVIDER_NEUTRAL")
        source = self._sources()
        for token in ("openai", "anthropic", "deepseek", "gemini", "base64"):
            self.assertNotIn(token, source.lower())
        self.assertEqual(artifact.manifest["renderer_version"], RENDERER_VERSION)
        self.assertEqual(artifact.manifest["artifact"], ARTIFACT_KIND)

    def test_only_stdlib_imports(self):
        allowed_roots = {"__future__", "argparse", "dataclasses", "datetime", "decimal",
                         "hashlib", "json", "os", "pathlib", "struct", "sys",
                         "tempfile", "typing", "zlib", "src"}
        import ast
        for path in (Path(inspect.getsourcefile(visual_module)), CLI):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    roots = {alias.name.split(".")[0] for alias in node.names}
                elif isinstance(node, ast.ImportFrom) and node.module:
                    roots = {node.module.split(".")[0]}
                else:
                    continue
                self.assertLessEqual(roots, allowed_roots, f"{path.name}: {roots}")


class AdapterTests(unittest.TestCase):
    def test_panels_adapter_groups_without_resampling(self):
        bars = wave_bars(3) + wave_bars(2, timeframe="5m", minutes=5)
        panels = panels_from_observation_bars(bars)
        self.assertEqual([panel.timeframe for panel in panels], ["1m", "5m"])
        self.assertEqual(len(panels[0].bars), 3)
        self.assertEqual(len(panels[1].bars), 2)
        self.assertEqual(panels[0].bars[0].open_price, wave_bars(3)[0].open_price)

    def test_spec_rejects_duplicate_panel_timeframes(self):
        panels = (
            VisualPanel(timeframe="1m", bars=wave_bars(2)),
            VisualPanel(timeframe="1m", bars=wave_bars(2)),
        )
        with self.assertRaises(ValueError):
            make_spec(panels=panels)

    def test_spec_rejects_too_many_panels(self):
        panels = tuple(
            VisualPanel(timeframe=f"tf{i}", bars=(make_bar(0, timeframe=f"tf{i}"),))
            for i in range(5)
        )
        with self.assertRaises(ValueError):
            make_spec(panels=panels)


class CliTests(unittest.TestCase):
    def _input_payload(self) -> dict:
        spec = make_spec()
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

    def test_cli_produces_png_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "observation.json"
            png_path = tmp_path / "observation.png"
            manifest_path = tmp_path / "observation.manifest.json"
            input_path.write_text(json.dumps(self._input_payload()), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "--input", str(input_path),
                 "--png-out", str(png_path), "--manifest-out", str(manifest_path)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            png_bytes = png_path.read_bytes()
            self.assertTrue(png_bytes.startswith(b"\x89PNG\r\n\x1a\n"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["png_sha256"], sha256(png_bytes).hexdigest())
            self.assertEqual(manifest["visual_artifact_identity"], render().visual_artifact_identity)
            self.assertEqual(manifest["outcome_fields"], 0)

    def test_cli_rejects_future_bar(self):
        payload = self._input_payload()
        payload["as_of"] = T0.isoformat()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            input_path = tmp_path / "observation.json"
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "--input", str(input_path),
                 "--png-out", str(tmp_path / "o.png"),
                 "--manifest-out", str(tmp_path / "o.json")],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
