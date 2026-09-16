# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

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
        Tail after the last line lands. The session does not loop, so this
        only keeps the final element off the 100% keyframe.
    """

    seconds_per_char: float
    pause_after_command: float
    seconds_per_output_line: float
    hold_at_end: float


# The session plays once and then stays on screen, so fill time no longer has
# to fight a loop: these are the numbers of someone typing at a normal pace,
# pausing after each command before its output lands.
CADENCE = Cadence(
    seconds_per_char=0.055,
    pause_after_command=0.5,
    seconds_per_output_line=0.09,
    # Nothing restarts, so this is only a tail so no element lands exactly on
    # the final keyframe.
    hold_at_end=1.5,
)
