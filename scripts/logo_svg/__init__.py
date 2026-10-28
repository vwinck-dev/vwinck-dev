# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Render the vwinck-dev signature as a pair of self-animating SVG banners."""

from .builder import BannerBuilder
from .choreography import PACE, Pace
from .renderer import BannerRenderer
from .theme import THEMES, LogoTheme

__all__ = [
    "PACE",
    "THEMES",
    "BannerBuilder",
    "BannerRenderer",
    "LogoTheme",
    "Pace",
]
