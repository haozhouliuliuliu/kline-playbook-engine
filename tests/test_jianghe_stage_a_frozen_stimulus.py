from __future__ import annotations

from decimal import Decimal
import struct
import unittest

from src.jianghe_stage_a_frozen_stimulus import (
    FROZEN_STAGE_A_15M_BAR_COUNT,
    FROZEN_STAGE_A_1H_BAR_COUNT,
    FROZEN_STAGE_A_CANVAS_HEIGHT,
    FROZEN_STAGE_A_CANVAS_WIDTH,
    FROZEN_STAGE_A_FINE_BAR_COUNT,
    build_frozen_stage_a_stimulus,
)
from src.jianghe_stage_a_runtime import build_stage_a_stimulus


class StageAFrozenStimulusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = build_stage_a_stimulus()
        cls.frozen = build_frozen_stage_a_stimulus()

    def test_frozen_window_is_exact_tail_of_pre_freeze_visible_recipe(self) -> None:
        base_fine = tuple(
            sorted(
                (bar for bar in self.base.observation.bars if bar.timeframe == "5m"),
                key=lambda bar: bar.open_time,
            )
        )
        frozen_fine = tuple(
            sorted(
                (bar for bar in self.frozen.observation.bars if bar.timeframe == "5m"),
                key=lambda bar: bar.open_time,
            )
        )
        self.assertEqual(FROZEN_STAGE_A_FINE_BAR_COUNT, len(frozen_fine))
        self.assertEqual(base_fine[-FROZEN_STAGE_A_FINE_BAR_COUNT:], frozen_fine)
        self.assertNotEqual(
            self.base.observation.identity.identity,
            self.frozen.observation.identity.identity,
        )

    def test_frozen_counts_and_false_breakout_shape_are_exact(self) -> None:
        by_tf = {
            timeframe: tuple(
                sorted(
                    (bar for bar in self.frozen.observation.bars if bar.timeframe == timeframe),
                    key=lambda bar: bar.open_time,
                )
            )
            for timeframe in ("5m", "15m", "1H")
        }
        self.assertEqual(FROZEN_STAGE_A_FINE_BAR_COUNT, len(by_tf["5m"]))
        self.assertEqual(FROZEN_STAGE_A_15M_BAR_COUNT, len(by_tf["15m"]))
        self.assertEqual(FROZEN_STAGE_A_1H_BAR_COUNT, len(by_tf["1H"]))

        poke = by_tf["5m"][20]
        self.assertEqual("103", poke.high_price)
        self.assertEqual("101.1", poke.close_price)
        self.assertLess(Decimal(poke.close_price), Decimal("102"))
        self.assertTrue(
            all(Decimal(bar.high_price) < Decimal("102") for bar in by_tf["5m"][:20])
        )
        self.assertTrue(
            all(Decimal(bar.high_price) < Decimal("102") for bar in by_tf["5m"][21:])
        )
        self.assertEqual("103", by_tf["15m"][6].high_price)
        self.assertEqual("103", by_tf["1H"][1].high_price)
        self.assertEqual(20, len(by_tf["5m"][:20]))
        self.assertEqual(15, len(by_tf["5m"][21:]))

    def test_structured_and_visual_bind_same_frozen_observation(self) -> None:
        observation_identity = self.frozen.observation.identity.identity
        self.assertEqual(observation_identity, self.frozen.structured.source_observation_identity)
        self.assertEqual(observation_identity, self.frozen.visual.source_observation_identity)
        self.assertNotEqual(self.base.structured.identity, self.frozen.structured.identity)
        self.assertNotEqual(self.base.visual.identity, self.frozen.visual.identity)

    def test_png_dimensions_are_frozen_and_keep_deepseek_pixel_budget(self) -> None:
        png = self.frozen.visual.png_bytes
        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
        width, height = struct.unpack(">II", png[16:24])
        self.assertEqual(FROZEN_STAGE_A_CANVAS_WIDTH, width)
        self.assertEqual(FROZEN_STAGE_A_CANVAS_HEIGHT, height)
        self.assertLessEqual(width * height, 640_000)

    def test_frozen_stimulus_is_deterministic(self) -> None:
        again = build_frozen_stage_a_stimulus()
        self.assertEqual(self.frozen.identity, again.identity)
        self.assertEqual(self.frozen.recipe_identity, again.recipe_identity)
        self.assertEqual(self.frozen.structured.identity, again.structured.identity)
        self.assertEqual(self.frozen.png_sha256, again.png_sha256)
        self.assertEqual(self.frozen.visual.identity, again.visual.identity)


if __name__ == "__main__":
    unittest.main()
