# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Per-line rendering.

Each kind of script line gets its own renderer behind a common protocol, and
the renderers are looked up by kind. Supporting a new kind of line means
adding a class and registering it -- no existing renderer changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Mapping, Protocol, Sequence
from xml.sax.saxutils import escape

from .animation import CssClass, KeyframeFactory
from .geometry import Metrics
from .prompt import PROMPT_TEXT
from .script import LineKind
from .timeline import ScheduledLine, Timeline


@dataclass(frozen=True)
class SvgFragment:
    """Markup plus the CSS rules that animate it."""

    markup: tuple[str, ...] = ()
    rules: tuple[str, ...] = ()

    #: Shared "nothing to draw" instance. ClassVar, so it is not a field.
    EMPTY: ClassVar["SvgFragment"]

    def __add__(self, other: "SvgFragment") -> "SvgFragment":
        return SvgFragment(
            markup=self.markup + other.markup,
            rules=self.rules + other.rules,
        )


SvgFragment.EMPTY = SvgFragment()


@dataclass(frozen=True)
class RenderContext:
    """Everything a line renderer is allowed to depend on."""

    metrics: Metrics
    timeline: Timeline
    keyframes: KeyframeFactory


class LineRenderer(Protocol):
    """Renders one scheduled line into markup and its animation rules."""

    def render(self, index: int, entry: ScheduledLine, ctx: RenderContext) -> SvgFragment:
        ...


def _text_element(
    element_id: str,
    x: float,
    y: float,
    css_class: CssClass,
    content: str,
) -> str:
    return (
        f'<text id="{element_id}" class="{css_class.value}" '
        f'x="{x:.2f}" y="{y:.2f}" xml:space="preserve">'
        f"{escape(content)}</text>"
    )


class BlankLineRenderer:
    """Blank lines occupy a row and draw nothing."""

    def render(self, index: int, entry: ScheduledLine, ctx: RenderContext) -> SvgFragment:
        return SvgFragment.EMPTY


class OutputLineRenderer:
    """Command output: appears whole, at one instant."""

    def render(self, index: int, entry: ScheduledLine, ctx: RenderContext) -> SvgFragment:
        element_id = f"o{index}"
        markup = _text_element(
            element_id=element_id,
            x=ctx.metrics.x_for_column(0),
            y=ctx.metrics.baseline_for_row(entry.row),
            css_class=CssClass.OUTPUT,
            content=entry.line.text,
        )
        rule = ctx.keyframes.reveal(
            element_id, ctx.timeline.percent_of(entry.starts_at)
        )
        return SvgFragment(markup=(markup,), rules=(rule,))


class CommandLineRenderer:
    """A typed command: prompt, then the text revealed a glyph at a time,
    with a cursor walking along behind it."""

    def render(self, index: int, entry: ScheduledLine, ctx: RenderContext) -> SvgFragment:
        metrics = ctx.metrics
        baseline = metrics.baseline_for_row(entry.row)
        appears_at = ctx.timeline.percent_of(entry.starts_at)

        prompt_id = f"p{index}"
        fragment = SvgFragment(
            markup=(
                _text_element(
                    element_id=prompt_id,
                    x=metrics.x_for_column(0),
                    y=baseline,
                    css_class=CssClass.PROMPT,
                    content=PROMPT_TEXT,
                ),
            ),
            rules=(ctx.keyframes.reveal(prompt_id, appears_at),),
        )

        characters = len(entry.line.text)
        if not characters:
            return fragment

        typed_at = ctx.timeline.percent_of(entry.ends_at)
        command_x = metrics.x_for_column(len(PROMPT_TEXT))

        command_id = f"c{index}"
        fragment += SvgFragment(
            markup=(
                _text_element(
                    element_id=command_id,
                    x=command_x,
                    y=baseline,
                    css_class=CssClass.COMMAND,
                    content=entry.line.text,
                ),
            ),
            rules=(
                ctx.keyframes.typing(command_id, appears_at, typed_at, characters),
            ),
        )

        cursor_id = f"u{index}"
        fragment += SvgFragment(
            markup=(
                f'<rect id="{cursor_id}" class="{CssClass.CURSOR.value}" '
                f'x="{command_x:.2f}" y="{baseline - metrics.font_size:.2f}" '
                f'width="{metrics.cursor_width:.2f}" '
                f'height="{metrics.cursor_height:.2f}" />',
            ),
            rules=(
                ctx.keyframes.cursor(
                    cursor_id,
                    appears_at,
                    typed_at,
                    characters,
                    travel=metrics.char_width * characters,
                ),
            ),
        )
        return fragment


#: Which renderer handles which kind of line.
DEFAULT_LINE_RENDERERS: Mapping[LineKind, LineRenderer] = {
    LineKind.COMMAND: CommandLineRenderer(),
    LineKind.OUTPUT: OutputLineRenderer(),
    LineKind.BLANK: BlankLineRenderer(),
}


def renderers_for(kinds: Sequence[LineKind]) -> Mapping[LineKind, LineRenderer]:
    """Narrow the default registry, mostly so tests can isolate one kind."""
    return {kind: DEFAULT_LINE_RENDERERS[kind] for kind in kinds}
