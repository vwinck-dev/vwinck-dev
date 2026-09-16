# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Parsing ``terminal.txt`` into a typed model of the shell session."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
from typing import Iterator, Sequence

from .prompt import PROMPT_TEXT

#: A source line opening with this marker is typed out; anything else is output.
COMMAND_MARKER = "$ "


@unique
class LineKind(Enum):
    """What a single line of the source script represents."""

    COMMAND = "command"
    OUTPUT = "output"
    BLANK = "blank"


@dataclass(frozen=True)
class ScriptLine:
    """One parsed line, before any timing is attached."""

    kind: LineKind
    text: str

    @property
    def width_in_chars(self) -> int:
        if self.kind is LineKind.COMMAND:
            return len(PROMPT_TEXT) + len(self.text)
        return len(self.text)


class TerminalScript:
    """The shell session, parsed from its source file."""

    def __init__(self, lines: Sequence[ScriptLine]) -> None:
        self._lines = tuple(lines)

    @classmethod
    def from_file(cls, path: Path) -> TerminalScript:
        return cls.from_text(path.read_text(encoding="utf-8"))

    @classmethod
    def from_text(cls, text: str) -> TerminalScript:
        return cls([cls._parse_line(raw) for raw in text.rstrip("\n").split("\n")])

    @staticmethod
    def _parse_line(raw: str) -> ScriptLine:
        if raw.startswith(COMMAND_MARKER):
            return ScriptLine(kind=LineKind.COMMAND, text=raw[len(COMMAND_MARKER):])
        if not raw.strip():
            return ScriptLine(kind=LineKind.BLANK, text="")
        return ScriptLine(kind=LineKind.OUTPUT, text=raw)

    def __iter__(self) -> Iterator[ScriptLine]:
        return iter(self._lines)

    def __len__(self) -> int:
        return len(self._lines)

    @property
    def widest_line(self) -> int:
        return max((line.width_in_chars for line in self._lines), default=0)
