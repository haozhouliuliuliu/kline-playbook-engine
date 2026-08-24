from __future__ import annotations

import struct
import unittest

from src.jianghe_stage_a_frozen_stimulus import (
    FROZEN_STAGE_A_CANVAS_HEIGHT,
    FROZEN_STAGE_A_CANVAS_WIDTH,
    build_frozen_stage_a_stimulus,
)
from src.jianghe_stage_a_runtime import build_stage_a_stimulus


class StageAFrozenStimulusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.base = build_stage_a_stimulus()
        cls.frozen = build_frozen_stage_a_stimulus()

    def test_market_observation_and_bar_recipe_are_unchanged(self) -> None:
        self.assertEqual(self.base.observation.identity.identity, self.frozen.observation.identity.identity)
        self.assertEqual(self.base.structured.identity, self.frozen.structured.identity)
        self.assertEqual(self.base.recipe_identity, self.frozen.recipe_identity)
        self.assertEqual(self.base.observation.bars, self.frozen.observation.bars)

    def test_only_visual_presentation_identity_changes(self) -> None:
        self.assertNotEqual(self.base.renderer_config_identity, self.frozen.renderer_config_identity)
        self.assertNotEqual(self.base.visual.identity, self.frozen.visual.identity)
        self.assertEqual(
            self.frozen.observation.identity.identity,
            self.frozen.visual.source_observation_identity,
        )

    def test_png_dimensions_are_frozen_and_keep_deepseek_pixel_budget(self) -> None:
        png = self.frozen.visual.png_bytes
        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
        width, height = struct.unpack(">II", png[16:24])
        self.assertEqual(FROZEN_STAGE_A_CANVAS_WIDTH, width)
        self.assertEqual(FROZEN_STAGE_A_CANVAS_HEIGHT, height)
        self.assertLessEqual(width * height, 640_000)

    def test_compact_visual_is_deterministic(self) -> None:
        again = build_frozen_stage_a_stimulus()
        self.assertEqual(self.frozen.identity, again.identity)
        self.assertEqual(self.frozen.png_sha256, again.png_sha256)
        self.assertEqual(self.frozen.visual.identity, again.visual.identity)


if __name__ == "__main__":
    unittest.main()
