# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Orchestration: script plus timeline plus theme becomes one SVG."""

from __future__ import annotations

from typing import Mapping

from .animation import KeyframeFactory
from .document import Canvas, SvgDocument
from .geometry import METRICS, Metrics
from .lines import DEFAULT_LINE_RENDERERS, LineRenderer, RenderContext, SvgFragment
from .script import LineKind, TerminalScript
from .stylesheet import StyleSheet
from .theme import Theme
from .timeline import Timeline

#: One spare column so a cursor at the end of the widest line still fits.
CURSOR_MARGIN_COLUMNS = 1


class TerminalSvgRenderer:
    """Turns a scheduled script into one themed SVG document.

    Composes the pieces rather than doing their work: line renderers produce
    markup and rules, the stylesheet produces the shared CSS, and the document
    wraps the result.
    """

    def __init__(
        self,
        script: TerminalScript,
        timeline: Timeline,
        metrics: Metrics = METRICS,
        line_renderers: Mapping[LineKind, LineRenderer] | None = None,
        stylesheet: StyleSheet | None = None,
    ) -> None:
        self._script = script
        self._timeline = timeline
        self._metrics = metrics
        self._line_renderers = line_renderers or DEFAULT_LINE_RENDERERS
        keyframes = KeyframeFactory()
        self._stylesheet = stylesheet or StyleSheet(keyframes)
        self._context = RenderContext(
            metrics=metrics, timeline=timeline, keyframes=keyframes
        )
        self._document = SvgDocument(self._canvas(), metrics)

    def _canvas(self) -> Canvas:
        columns = self._script.widest_line + CURSOR_MARGIN_COLUMNS
        return Canvas(
            width=self._metrics.width_for_columns(columns),
            height=self._metrics.height_for_rows(len(self._script)),
        )

    def render(self, theme: Theme) -> str:
        fragment = self._render_lines()
        stylesheet = self._stylesheet.render(
            palette=theme.palette,
            metrics=self._metrics,
            cycle_seconds=self._timeline.cycle_seconds,
        )
        return self._document.render(
            stylesheet=stylesheet,
            element_rules=fragment.rules,
            body=fragment.markup,
        )

    def _render_lines(self) -> SvgFragment:
        fragment = SvgFragment.EMPTY
        for index, entry in enumerate(self._timeline):
            renderer = self._line_renderers.get(entry.line.kind)
            if renderer is None:
                continue
            fragment += renderer.render(index, entry, self._context)
        return fragment
