# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Render a shell session as a pair of self-animating SVG terminals."""

from .builder import TerminalSvgBuilder
from .cadence import CADENCE, Cadence
from .script import TerminalScript
from .theme import THEMES, Theme

__all__ = [
    "CADENCE",
    "THEMES",
    "Cadence",
    "TerminalScript",
    "TerminalSvgBuilder",
    "Theme",
]
