# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Geist Mono, embedded into the SVG itself.

GitHub serves README images through an ``<img>`` tag, and an SVG loaded that
way may not fetch anything -- a webfont URL is simply ignored. A ``data:``
URI is not a fetch, so the font travels inside the file.

The files in ``assets/fonts`` are subsets (Latin only) made once by
``scripts/subset_fonts.py``; reading them here keeps the generators
stdlib-only.
"""

from __future__ import annotations

import base64
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Iterable

FONT_FAMILY = "Geist Mono"

#: Geist Mono first; the rest only matter if a renderer refuses the embed.
FONT_STACK = (
    f"'{FONT_FAMILY}', ui-monospace, SFMono-Regular, 'SF Mono', Menlo, "
    "Consolas, 'Liberation Mono', monospace"
)

FONTS_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"


class FontWeight(Enum):
    """The two weights the manual uses: SemiBold for the signature and
    titles, Regular for code."""

    REGULAR = (400, "GeistMono-Regular.woff2")
    SEMIBOLD = (600, "GeistMono-SemiBold.woff2")

    @property
    def css_weight(self) -> int:
        return self.value[0]

    @property
    def path(self) -> Path:
        return FONTS_DIR / self.value[1]


@lru_cache(maxsize=None)
def _encoded(weight: FontWeight) -> str:
    return base64.b64encode(weight.path.read_bytes()).decode("ascii")


def font_faces(weights: Iterable[FontWeight] = tuple(FontWeight)) -> str:
    """``@font-face`` rules carrying the requested weights inline."""
    return "".join(
        f"@font-face{{font-family:'{FONT_FAMILY}';"
        f"font-weight:{weight.css_weight};font-style:normal;"
        f"src:url(data:font/woff2;base64,{_encoded(weight)}) format('woff2');}}"
        for weight in weights
    )
