# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Colour schemes and the filenames they publish under."""

from __future__ import annotations

from dataclasses import dataclass

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
        background=TRANSPARENT,
        border="#444c56",
        prompt="#539bf5",
        command="#adbac7",
        output="#768390",
        cursor="#adbac7",
    ),
    filename="terminalDarkMode.svg",
)

THEME_LIGHT = Theme(
    palette=Palette(
        background=TRANSPARENT,
        border="#d0d7de",
        prompt="#0969da",
        command="#24292f",
        output="#57606a",
        cursor="#24292f",
    ),
    filename="terminalLightMode.svg",
)

THEMES: tuple[Theme, ...] = (THEME_DARK, THEME_LIGHT)
