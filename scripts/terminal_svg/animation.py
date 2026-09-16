"""CSS keyframes that drive the terminal.

Every animated element shares one ``animation-duration`` -- the full cycle --
and encodes its own moment as percentages inside its keyframes. That is what
keeps dozens of independently animated lines in sync without a timeline
runtime to coordinate them.

This module knows about CSS and nothing else: it is handed percentages and
pixel distances, never a ``Timeline`` or a ``Metrics``.
"""

from __future__ import annotations

from enum import Enum, unique

#: Width of the instant used to "pop" an element into view, as a fraction of
#: the cycle. Small enough to read as instant, non-zero so the two keyframe
#: stops never collide.
REVEAL_EPSILON = 0.0005

FULL_CYCLE_PERCENT = 100.0
BLINK_ANIMATION = "blink"
BLINK_SECONDS = 1.0


@unique
class CssClass(Enum):
    """Style hooks emitted into the SVG."""

    PROMPT = "prompt"
    COMMAND = "cmd"
    OUTPUT = "out"
    CURSOR = "cursor"
    BACKGROUND = "bg"


class KeyframeFactory:
    """Builds the per-element ``@keyframes`` rules and their bindings."""

    def reveal(self, element_id: str, at_percent: float) -> str:
        """Pop an element into view at one instant, then leave it alone."""
        hidden_until = max(0.0, at_percent - REVEAL_EPSILON)
        return (
            f"#{element_id}{{animation-name:r{element_id};}}"
            f"@keyframes r{element_id}{{"
            f"0%,{hidden_until:.4f}%{{opacity:0;}}"
            f"{at_percent:.4f}%,{FULL_CYCLE_PERCENT:.0f}%{{opacity:1;}}}}"
        )

    def typing(
        self,
        element_id: str,
        from_percent: float,
        to_percent: float,
        characters: int,
    ) -> str:
        """Reveal a line one character at a time.

        ``steps(n)`` over a ``clip-path`` inset is what makes this read as
        typing rather than as a wipe: on a monospace grid each step uncovers
        exactly one glyph.
        """
        return (
            f"#{element_id}{{animation-name:t{element_id};"
            f"animation-timing-function:steps({characters},end);}}"
            f"@keyframes t{element_id}{{"
            f"0%,{from_percent:.4f}%{{clip-path:inset(0 100% 0 0);}}"
            f"{to_percent:.4f}%,{FULL_CYCLE_PERCENT:.0f}%"
            f"{{clip-path:inset(0 0 0 0);}}}}"
        )

    def cursor(
        self,
        element_id: str,
        from_percent: float,
        to_percent: float,
        characters: int,
        travel: float,
    ) -> str:
        """Walk the cursor along the line while it is being typed.

        Two animations run at once: one steps the cursor across the grid and
        gates its visibility to this command's window, the other blinks it on
        its own short loop.
        """
        hidden_before = max(0.0, from_percent - REVEAL_EPSILON)
        hidden_after = min(FULL_CYCLE_PERCENT, to_percent + REVEAL_EPSILON)
        return (
            f"#{element_id}{{animation-name:w{element_id},{BLINK_ANIMATION};"
            f"animation-timing-function:steps({characters},end),step-end;}}"
            f"@keyframes w{element_id}{{"
            f"0%,{hidden_before:.4f}%{{visibility:hidden;transform:translateX(0);}}"
            f"{from_percent:.4f}%{{visibility:visible;transform:translateX(0);}}"
            f"{to_percent:.4f}%{{visibility:visible;"
            f"transform:translateX({travel:.2f}px);}}"
            f"{hidden_after:.4f}%,{FULL_CYCLE_PERCENT:.0f}%{{visibility:hidden;"
            f"transform:translateX({travel:.2f}px);}}}}"
        )

    def blink(self) -> str:
        """The shared cursor blink, referenced by every cursor."""
        return (
            f"@keyframes {BLINK_ANIMATION}"
            f"{{0%,50%{{opacity:1;}}50.01%,{FULL_CYCLE_PERCENT:.0f}%{{opacity:0;}}}}"
        )
