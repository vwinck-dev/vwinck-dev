# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Tests for restyling the third-party stats cards."""

from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brand import AZUL, LAYOUT_WIDTH, TERMINAL
from restyle_stats import CARD_WIDTH, MARKER, PALETTES, main, restyle

# The shape of the upstream templates, trimmed to what restyling touches.
TEMPLATE = (
    '<svg width="360" height="210" xmlns="http://www.w3.org/2000/svg">\n'
    "<style>\nth { color: rgb(72, 148, 224); }\n</style>\n"
    '<g><rect x="5" y="5" id="background" />'
    '<foreignObject x="21" y="19" width="318" height="172"></foreignObject></g>\n'
    "</svg>\n"
)


class RestyleTest(unittest.TestCase):
    def setUp(self) -> None:
        self.dark = restyle(TEMPLATE, PALETTES["dark"])

    def test_two_cards_fill_the_column(self) -> None:
        self.assertEqual(CARD_WIDTH * 2, LAYOUT_WIDTH)
        self.assertIn(f'<svg width="{CARD_WIDTH}"', self.dark)

    def test_only_the_root_width_changes(self) -> None:
        self.assertIn('<foreignObject x="21" y="19" width="318"', self.dark)

    def test_brand_rules_come_after_the_templates_own(self) -> None:
        """Appending, not replacing: the cascade lets the later rule win,
        whatever colour upstream picks next."""
        self.assertLess(
            self.dark.index("rgb(72, 148, 224)"), self.dark.index(MARKER)
        )
        self.assertLess(self.dark.index(MARKER), self.dark.index("</style>"))

    def test_titles_take_the_brand_colour(self) -> None:
        self.assertIn(f"color:{AZUL}", self.dark)
        light = restyle(TEMPLATE, PALETTES["light"])
        self.assertIn(f"color:{TERMINAL}", light)
        self.assertNotIn(AZUL, light)

    def test_the_font_is_embedded(self) -> None:
        self.assertIn("data:font/woff2;base64,", self.dark)

    def test_restyling_twice_changes_nothing(self) -> None:
        self.assertEqual(restyle(self.dark, PALETTES["dark"]), self.dark)

    def test_a_template_without_a_stylesheet_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            restyle('<svg width="360"></svg>', PALETTES["dark"])

    def test_the_cli_rewrites_files_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "overview.svg"
            path.write_text(TEMPLATE, encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                main(["--theme", "light", str(path)])
            self.assertIn(MARKER, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
