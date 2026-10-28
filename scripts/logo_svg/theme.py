# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""The banner's two colourways, straight from the manual's "Versões" page.

Dark is the preferred version: blue V, pink W, white commits and eye. Light
follows the manual's light-background rule: lines, eye and text in Terminal,
with blue and pink surviving only as commit fills inside a Terminal outline.
"""

from __future__ import annotations

from dataclasses import dataclass

from brand import AZUL, BRANCO, NEUTRALS_DARK, NEUTRALS_LIGHT, ROSA, TERMINAL

from .symbol import Branch

TRANSPARENT = "none"


@dataclass(frozen=True)
class LogoPalette:
    background: str
    border: str
    line: dict[Branch, str]
    commit: dict[Branch, str]
    #: Outline around each commit; ``0`` draws none.
    commit_outline: str
    commit_outline_width: float
    eye: str
    #: The three parts of ``vw;nck``.
    wordmark: tuple[str, str, str]
    title: str
    muted: str
    #: ``main`` and ``feature`` in the footer caption.
    caption_branches: tuple[str, str]
    cursor: str


@dataclass(frozen=True)
class LogoTheme:
    palette: LogoPalette
    filename: str


THEME_DARK = LogoTheme(
    palette=LogoPalette(
        background=TERMINAL,
        border=NEUTRALS_DARK.border,
        line={Branch.V: AZUL, Branch.W: ROSA},
        commit={Branch.V: BRANCO, Branch.W: BRANCO},
        commit_outline=TRANSPARENT,
        commit_outline_width=0.0,
        eye=BRANCO,
        wordmark=(AZUL, BRANCO, ROSA),
        title=NEUTRALS_DARK.muted,
        muted=NEUTRALS_DARK.muted,
        caption_branches=(AZUL, ROSA),
        cursor=ROSA,
    ),
    filename="logoDarkMode.svg",
)

THEME_LIGHT = LogoTheme(
    palette=LogoPalette(
        background=TRANSPARENT,
        border=NEUTRALS_LIGHT.border,
        line={Branch.V: TERMINAL, Branch.W: TERMINAL},
        commit={Branch.V: AZUL, Branch.W: ROSA},
        commit_outline=TERMINAL,
        commit_outline_width=4.0,
        eye=TERMINAL,
        wordmark=(TERMINAL, TERMINAL, TERMINAL),
        title=NEUTRALS_LIGHT.muted,
        muted=NEUTRALS_LIGHT.muted,
        caption_branches=(TERMINAL, TERMINAL),
        cursor=TERMINAL,
    ),
    filename="logoLightMode.svg",
)

THEMES: tuple[LogoTheme, ...] = (THEME_DARK, THEME_LIGHT)
