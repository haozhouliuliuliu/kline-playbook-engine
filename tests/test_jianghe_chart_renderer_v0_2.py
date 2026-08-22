"""合成对抗测试：江河标准化 K 线图表渲染器 V0.2（无真实行情、无候选结果）。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from src.jianghe_ai_trader import ObservationBar
from src.jianghe_chart_renderer import (
    ChartOverlay,
    JiangheChartRenderer,
    SUPPORTED_TIMEFRAMES,
)


UTC = timezone.utc
T0 = datetime(2026, 8, 23, 10, 0, tzinfo=UTC)


def bar(index: int, *, close_offset: int = 0, high: str = "101", low: str = "99",
        open_price: str = "100", close_price: str = "100", closed: bool = True) -> ObservationBar:
    open_time = T0 + timedelta(minutes=index)
    close_time = open_time + timedelta(minutes=1)
    return ObservationBar(
        timeframe="1m",
        open_time=open_time,
        close_time=close_time,
        available_at=close_time + timedelta(seconds=close_offset),
        open_price=open_price,
        high_price=high,
        low_price=low,
        close_price=close_price,
        volume="10",
        is_closed=closed,
    )


def grid_columns(text: str) -> list[str]:
    rows = [
        line
        for line in text.splitlines()
        if line.count("|") == 2 and not line.startswith("bars:")
    ]
    row_strings = [line.split("|")[1] for line in rows]
    return ["".join(chars) for chars in zip(*row_strings)]


class JiangheChartRendererTests(unittest.TestCase):
    def test_rejects_sub_minute_and_unsupported_timeframes(self):
        renderer = JiangheChartRenderer()
        for timeframe in ("30s", "1s", "tick", "2m", "4h"):
            with self.assertRaises(ValueError):
                renderer.render(
                    timeframe=timeframe,
                    bars=(bar(0),),
                    product="cu",
                    concrete_contract="SHFE.cu2609",
                    current_time=T0 + timedelta(minutes=1),
                )
        self.assertEqual(SUPPORTED_TIMEFRAMES, ("1m", "5m", "15m", "1h"))

    def test_rejects_future_bar_and_duplicate_or_unsorted_bars(self):
        renderer = JiangheChartRenderer()
        with self.assertRaises(ValueError):
            renderer.render(
                timeframe="1m",
                bars=(bar(0),),
                product="cu",
                concrete_contract="SHFE.cu2609",
                current_time=T0,
            )
        with self.assertRaises(ValueError):
            renderer.render(
                timeframe="1m",
                bars=(bar(1), bar(1)),
                product="cu",
                concrete_contract="SHFE.cu2609",
                current_time=T0 + timedelta(minutes=3),
            )

    def test_deterministic_identity_and_no_future_scaling(self):
        renderer = JiangheChartRenderer()
        past = tuple(bar(i) for i in range(50))
        render_time = T0 + timedelta(minutes=50)
        first = renderer.render(
            timeframe="1m", bars=past, product="cu",
            concrete_contract="SHFE.cu2609", current_time=render_time,
        )
        second = renderer.render(
            timeframe="1m", bars=past, product="cu",
            concrete_contract="SHFE.cu2609", current_time=render_time,
        )
        self.assertEqual(first.text, second.text)
        self.assertEqual(first.content_hash, second.content_hash)
        # 即使存在未来 K 线，重渲同一窗口的布局与刻度也完全不变。
        future_known = tuple(
            bar(i, open_price="800", close_price="810", high="888", low="777")
            for i in range(50, 60)
        )
        later = renderer.render(
            timeframe="1m", bars=past, product="cu",
            concrete_contract="SHFE.cu2609", current_time=render_time,
        )
        self.assertEqual(first.text, later.text)
        full = renderer.render(
            timeframe="1m", bars=past + future_known, product="cu",
            concrete_contract="SHFE.cu2609", current_time=T0 + timedelta(minutes=60),
        )
        self.assertIn("888", full.text)
        self.assertNotIn("888", first.text)
        self.assertNotIn("777", first.text)
        top_label = full.text.splitlines()[
            [i for i, line in enumerate(full.text.splitlines()) if line.count("|") == 2 and not line.startswith("bars:")][0]
        ].strip().split(" ")[0]
        self.assertIn("888", top_label)
        first_top_label = first.text.splitlines()[
            [i for i, line in enumerate(first.text.splitlines()) if line.count("|") == 2 and not line.startswith("bars:")][0]
        ].strip().split(" ")[0]
        self.assertIn("101", first_top_label)

    def test_partial_bar_is_clearly_marked(self):
        renderer = JiangheChartRenderer()
        rendered = renderer.render(
            timeframe="1m",
            bars=(bar(0, closed=True), bar(1, closed=False)),
            product="cu",
            concrete_contract="SHFE.cu2609",
            current_time=T0 + timedelta(minutes=2),
        )
        self.assertTrue(rendered.partial_bar_present)
        self.assertIn("closed=1 partial=1", rendered.text)
        self.assertIn("PARTIAL", rendered.text)
        columns = grid_columns(rendered.text)
        self.assertIn("#", columns[0])
        self.assertIn("o", columns[1])
        metadata = rendered.to_chart_render()
        self.assertTrue(metadata.partial_bar_marked)
        self.assertEqual(metadata.window_definition, "LAST_2_BARS")

    def test_header_declares_time_product_and_timeframe(self):
        renderer = JiangheChartRenderer()
        current = T0 + timedelta(minutes=5)
        five_minute_bar = ObservationBar(
            timeframe="5m",
            open_time=T0,
            close_time=current,
            available_at=current,
            open_price="100", high_price="101", low_price="99", close_price="100",
            volume="10", is_closed=True,
        )
        rendered = renderer.render(
            timeframe="5m",
            bars=(five_minute_bar,),
            product="cu",
            concrete_contract="SHFE.cu2609",
            current_time=current,
        )
        self.assertIn("product=cu", rendered.text)
        self.assertIn("contract=SHFE.cu2609", rendered.text)
        self.assertIn("timeframe=5m", rendered.text)
        self.assertIn(f"current_time={current.isoformat()}", rendered.text)
        self.assertIn("AI hypotheses; NOT market facts", rendered.text)

    def test_annotations_are_hypotheses_and_never_rewrite_market_facts(self):
        renderer = JiangheChartRenderer()
        bars = tuple(bar(i) for i in range(10))
        current = T0 + timedelta(minutes=10)
        plain = renderer.render(
            timeframe="1m", bars=bars, product="cu",
            concrete_contract="SHFE.cu2609", current_time=current,
        )
        annotated = renderer.render(
            timeframe="1m", bars=bars, product="cu",
            concrete_contract="SHFE.cu2609", current_time=current,
            overlays=(
                ChartOverlay("AI_WATCH_REGION", "99", "101", "watch-1"),
                ChartOverlay("AI_HYPOTHESIS_KEY_ZONE", "100", "100", "zone-1"),
                ChartOverlay("AI_DEFENSE_INTERPRETATION", "105", "105", "level-1"),
            ),
        )
        # 市场事实（K 线网格）不因叠加 AI 假设而改变。
        self.assertEqual(grid_columns(plain.text), grid_columns(annotated.text))
        columns = grid_columns(annotated.text)
        for column in columns:
            for marker in ("W", "I", "K"):
                self.assertNotIn(marker, column)
        metadata = annotated.to_chart_render()
        self.assertEqual(
            {kind for kind, _ in metadata.annotations},
            {"AI_WATCH_REGION", "AI_HYPOTHESIS_KEY_ZONE", "AI_DEFENSE_INTERPRETATION"},
        )
        self.assertTrue(all(kind.startswith("AI_") for kind, _ in metadata.annotations))
        self.assertNotEqual(plain.content_hash, annotated.content_hash)
        self.assertIn("W", annotated.text)
        self.assertIn("I", annotated.text)
        self.assertIn("K", annotated.text)
        self.assertFalse(hasattr(bar(0), "annotations"))

    def test_overlay_validation(self):
        with self.assertRaises(ValueError):
            ChartOverlay("MARKET_FACT", "99", "101", "bad-kind")
        with self.assertRaises(ValueError):
            ChartOverlay("AI_WATCH_REGION", "102", "101", "inverted")
        with self.assertRaises(ValueError):
            ChartOverlay("AI_WATCH_REGION", "abc", "101", "unparseable")
        with self.assertRaises(ValueError):
            ChartOverlay("AI_WATCH_REGION", "99", "101", "")


if __name__ == "__main__":
    unittest.main()
