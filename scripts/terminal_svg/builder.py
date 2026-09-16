# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Writing the rendered terminal to disk, one file per theme."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .cadence import CADENCE, Cadence
from .renderer import TerminalSvgRenderer
from .script import TerminalScript
from .theme import THEMES, Theme
from .timeline import Timeline


class TerminalSvgBuilder:
    """Renders a script under every theme and writes the results out."""

    def __init__(self, script: TerminalScript, cadence: Cadence = CADENCE) -> None:
        self._renderer = TerminalSvgRenderer(script, Timeline(script, cadence))

    def build(
        self, out_dir: Path, themes: Sequence[Theme] = THEMES
    ) -> list[Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for theme in themes:
            destination = out_dir / theme.filename
            destination.write_text(self._renderer.render(theme), encoding="utf-8")
            written.append(destination)
        return written
