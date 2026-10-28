# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Assembling the finished SVG document."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
from xml.sax.saxutils import escape

from .animation import CssClass
from .geometry import Metrics
from .prompt import PROMPT_USER

NEWLINE = "\n"


@dataclass(frozen=True)
class Canvas:
    """The finished document's dimensions."""

    width: float
    height: float


class SvgDocument:
    """Wraps rendered fragments in the SVG envelope."""

    def __init__(self, canvas: Canvas, metrics: Metrics) -> None:
        self._canvas = canvas
        self._metrics = metrics

    def render(
        self,
        stylesheet: str,
        element_rules: Sequence[str],
        body: Sequence[str],
    ) -> str:
        width, height = self._canvas.width, self._canvas.height
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
            f'height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" '
            f'role="img" aria-label="{self._label()}">'
            f"{NEWLINE}<style>{stylesheet}{''.join(element_rules)}</style>"
            f"{NEWLINE}{self._background()}"
            f"{NEWLINE}{NEWLINE.join(body)}{NEWLINE}</svg>{NEWLINE}"
        )

    def _label(self) -> str:
        return escape(f"Terminal session on the {PROMPT_USER} GitHub profile")

    def _background(self) -> str:
        radius = self._metrics.border_radius
        # Half a pixel more so the 1px border lands on whole pixels.
        inset = self._metrics.card_inset + 0.5
        return (
            f'<rect id="{CssClass.BACKGROUND.value}" x="{inset}" y="{inset}" '
            f'width="{self._canvas.width - 2 * inset:.0f}" '
            f'height="{self._canvas.height - 2 * inset:.0f}" '
            f'rx="{radius}" ry="{radius}" />'
        )
