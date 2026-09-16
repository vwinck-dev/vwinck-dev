# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Assigning every line of the script its moment in the animation cycle."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator

from .cadence import Cadence
from .script import LineKind, ScriptLine, TerminalScript

FULL_CYCLE_PERCENT = 100.0


@dataclass(frozen=True)
class ScheduledLine:
    """A script line with its moment in the cycle resolved."""

    line: ScriptLine
    row: int
    starts_at: float
    ends_at: float


class Timeline:
    """Walks the script once, assigning every line a start and end second.

    Knows nothing about SVG: it converts a script plus a cadence into seconds,
    and answers what share of the cycle any given second represents.
    """

    def __init__(self, script: TerminalScript, cadence: Cadence) -> None:
        self._cadence = cadence
        self._entries = tuple(self._schedule(script))
        self._settles_at = max((entry.ends_at for entry in self._entries), default=0.0)
        self._cycle_seconds = self._settles_at + cadence.hold_at_end

    def _schedule(self, script: TerminalScript) -> Iterable[ScheduledLine]:
        clock = 0.0
        for row, line in enumerate(script):
            if line.kind is LineKind.COMMAND:
                duration = len(line.text) * self._cadence.seconds_per_char
                yield ScheduledLine(line, row, clock, clock + duration)
                clock += duration + self._cadence.pause_after_command
            elif line.kind is LineKind.OUTPUT:
                yield ScheduledLine(line, row, clock, clock)
                clock += self._cadence.seconds_per_output_line
            else:
                yield ScheduledLine(line, row, clock, clock)

    def __iter__(self) -> Iterator[ScheduledLine]:
        return iter(self._entries)

    @property
    def cycle_seconds(self) -> float:
        return self._cycle_seconds

    @property
    def settles_at(self) -> float:
        """Second at which the last line has finished appearing."""
        return self._settles_at

    def percent_of(self, seconds: float) -> float:
        """Convert an absolute second into its percentage of the cycle."""
        if self._cycle_seconds <= 0:
            return 0.0
        ratio = seconds / self._cycle_seconds * FULL_CYCLE_PERCENT
        return min(FULL_CYCLE_PERCENT, max(0.0, ratio))
