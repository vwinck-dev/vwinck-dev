# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Writing the banner to disk, one file per theme."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .renderer import BannerRenderer
from .theme import THEMES, LogoTheme


class BannerBuilder:
    def __init__(self, renderer: BannerRenderer | None = None) -> None:
        self._renderer = renderer or BannerRenderer()

    def build(
        self, out_dir: Path, themes: Sequence[LogoTheme] = THEMES
    ) -> list[Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for theme in themes:
            destination = out_dir / theme.filename
            destination.write_text(self._renderer.render(theme), encoding="utf-8")
            written.append(destination)
        return written
