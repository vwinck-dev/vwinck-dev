"""How fast the imaginary person at the keyboard works."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cadence:
    """Timing policy for the animation.

    ``seconds_per_char``
        Time to type one character. Human touch-typing sits around 0.04-0.09s.
        Below ~0.02s the steps blur together and the typing stops reading as
        typing.
    ``pause_after_command``
        The beat between the last character and the output appearing -- the
        "pressed enter, waiting" moment. Too short and the command never
        registers as a command.
    ``seconds_per_output_line``
        How fast output cascades. Near zero the whole block lands at once,
        which looks like a cached result; larger values look like real work.
    ``hold_at_end``
        Dead air on the finished screen before the loop restarts.
    """

    seconds_per_char: float
    pause_after_command: float
    seconds_per_output_line: float
    hold_at_end: float


# The terminal renders at a fixed height, so until the screen fills, a visitor
# is looking at an empty box roughly 1200px tall. That makes fill time the
# constraint that matters, not per-character realism: these values fill the
# screen in about six seconds and then hold it for nine, so most of the loop
# shows a complete terminal rather than an empty frame.
CADENCE = Cadence(
    seconds_per_char=0.022,
    pause_after_command=0.18,
    seconds_per_output_line=0.028,
    hold_at_end=9.0,
)
