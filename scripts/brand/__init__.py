# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""The vwinck-dev visual identity, shared by every generated image.

Everything here comes from the brand manual (``manual de marca v1.0``):
colours, typeface and the grid the profile is laid out on. The generators
import these values rather than restating them, so the profile cannot drift
from the manual one SVG at a time.
"""

from .colours import AZUL, BRANCO, ROSA, TERMINAL, Neutrals, NEUTRALS_DARK, NEUTRALS_LIGHT
from .fonts import FONT_FAMILY, FONT_STACK, FontWeight, font_faces
from .layout import CARD_INSET, CARD_RADIUS, LAYOUT_WIDTH

__all__ = [
    "AZUL",
    "BRANCO",
    "CARD_INSET",
    "CARD_RADIUS",
    "FONT_FAMILY",
    "FONT_STACK",
    "FontWeight",
    "LAYOUT_WIDTH",
    "NEUTRALS_DARK",
    "NEUTRALS_LIGHT",
    "Neutrals",
    "ROSA",
    "TERMINAL",
    "font_faces",
]
