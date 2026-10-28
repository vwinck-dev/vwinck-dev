# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Colour schemes and the filenames they publish under.

The manual's terminal application: main in blue, features in pink, on the
Terminal background. On light backgrounds blue and pink are too faint for
text, so the light theme keeps to Terminal and greys.
"""

from __future__ import annotations

from dataclasses import dataclass

from brand import AZUL, BRANCO, NEUTRALS_DARK, NEUTRALS_LIGHT, ROSA, TERMINAL

TRANSPARENT = "#00000000"


@dataclass(frozen=True)
class Palette:
    """Colours for one GitHub theme."""

    background: str
    border: str
    prompt: str
    command: str
    output: str
    cursor: str


@dataclass(frozen=True)
class Theme:
    """A palette plus the filename it is published under."""

    palette: Palette
    filename: str


THEME_DARK = Theme(
    palette=Palette(
        background=TERMINAL,
        border=NEUTRALS_DARK.border,
        prompt=AZUL,
        command=BRANCO,
        output=NEUTRALS_DARK.text,
        cursor=ROSA,
    ),
    filename="terminalDarkMode.svg",
)

THEME_LIGHT = Theme(
    palette=Palette(
        background=TRANSPARENT,
        border=NEUTRALS_LIGHT.border,
        prompt=TERMINAL,
        command=TERMINAL,
        output=NEUTRALS_LIGHT.text,
        cursor=TERMINAL,
    ),
    filename="terminalLightMode.svg",
)

THEMES: tuple[Theme, ...] = (THEME_DARK, THEME_LIGHT)
