# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""The grid every image on the profile is laid out on.

GitHub renders each image at its intrinsic width, capped by the README
column. Giving every image the same width is what lines their edges up into
one column instead of a ragged stack.
"""

from __future__ import annotations

#: Outer width of every full-width image. The profile README column is a
#: little wider on desktop; staying under it keeps the two stats cards on one
#: row instead of wrapping.
LAYOUT_WIDTH = 800

#: Gap between a card's drawn edge and its image edge. The stats generator
#: draws its cards 5px in, so everything else does too.
CARD_INSET = 5

CARD_RADIUS = 8
