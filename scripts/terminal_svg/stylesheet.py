# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""The document-level stylesheet: everything not tied to a single element."""

from __future__ import annotations

from .animation import CssClass, KeyframeFactory
from .geometry import FONT_STACK, Metrics
from .theme import Palette


class StyleSheet:
    """Builds the ``<style>`` body for one themed document."""

    def __init__(self, keyframes: KeyframeFactory) -> None:
        self._keyframes = keyframes

    def render(self, palette: Palette, metrics: Metrics, cycle_seconds: float) -> str:
        return "".join(
            (
                self._typography(metrics),
                self._colours(palette),
                self._animation_defaults(cycle_seconds),
                self._keyframes.blink(),
                self._reduced_motion(),
            )
        )

    def _typography(self, metrics: Metrics) -> str:
        return (
            f"text{{font-family:{FONT_STACK};"
            f"font-size:{metrics.font_size}px;white-space:pre;}}"
        )

    def _colours(self, palette: Palette) -> str:
        return (
            f".{CssClass.PROMPT.value}{{fill:{palette.prompt};font-weight:600;}}"
            f".{CssClass.COMMAND.value}{{fill:{palette.command};}}"
            f".{CssClass.OUTPUT.value}{{fill:{palette.output};}}"
            f".{CssClass.CURSOR.value}{{fill:{palette.cursor};}}"
            f"#{CssClass.BACKGROUND.value}{{fill:{palette.background};"
            f"stroke:{palette.border};stroke-width:1px;}}"
        )

    def _animation_defaults(self, cycle_seconds: float) -> str:
        """One duration for everyone; the per-element keyframes carry the rest."""
        return (
            f"{self._animated_selector()}{{"
            f"animation-duration:{cycle_seconds:.3f}s;"
            f"animation-iteration-count:infinite;animation-fill-mode:both;}}"
        )

    def _reduced_motion(self) -> str:
        """Readers who asked for less motion get the finished screen."""
        return (
            f"@media (prefers-reduced-motion:reduce){{"
            f"{self._animated_selector()}{{animation:none;opacity:1;"
            f"clip-path:none;}}"
            f"rect.{CssClass.CURSOR.value}{{visibility:hidden;}}}}"
        )

    @staticmethod
    def _animated_selector() -> str:
        return f"text,rect.{CssClass.CURSOR.value}"
