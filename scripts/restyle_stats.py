#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Dress the third-party stats cards in the vwinck-dev identity.

The stats workflow runs github-stats-transparent, whose SVG templates carry
their own palette and system fonts. Rather than rewriting its colours one
``sed`` at a time -- which broke silently whenever upstream touched a value --
this appends a stylesheet *after* the template's own, so the cascade does the
overriding, and resizes the card to half the profile column so two of them
sit flush under the banner and the terminal.

Run it on the templates before the generator renders them:

    python3 scripts/restyle_stats.py --theme dark generator/templates/*.svg
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))

from brand import (  # noqa: E402
    AZUL,
    BRANCO,
    CARD_RADIUS,
    FONT_STACK,
    LAYOUT_WIDTH,
    NEUTRALS_DARK,
    NEUTRALS_LIGHT,
    TERMINAL,
    font_faces,
)

#: Two cards per row, edge to edge: each owns half the column.
CARD_WIDTH = LAYOUT_WIDTH // 2

#: Marks a template as already restyled, so a second run is a no-op rather
#: than a second stylesheet.
MARKER = "/* vwinck-dev brand */"

SVG_WIDTH = re.compile(r'(<svg\b[^>]*?\bwidth=")\d+(")')
STYLE_END = "</style>"


@dataclass(frozen=True)
class StatsPalette:
    background: str
    border: str
    title: str
    value: str
    label: str


PALETTES = {
    "dark": StatsPalette(
        background=TERMINAL,
        border=NEUTRALS_DARK.border,
        title=AZUL,
        value=BRANCO,
        label=NEUTRALS_DARK.muted,
    ),
    # Blue on white is below the manual's contrast floor: titles go Terminal.
    "light": StatsPalette(
        background="#00000000",
        border=NEUTRALS_LIGHT.border,
        title=TERMINAL,
        value=TERMINAL,
        label=NEUTRALS_LIGHT.muted,
    ),
}


def brand_stylesheet(palette: StatsPalette) -> str:
    """Overrides for both templates; selectors one template lacks are inert."""
    return (
        f"{MARKER}{font_faces()}"
        f"svg{{font-family:{FONT_STACK};}}"
        f"#background{{fill:{palette.background};stroke:{palette.border};"
        f"rx:{CARD_RADIUS}px;ry:{CARD_RADIUS}px;}}"
        f"th,h2{{color:{palette.title};fill:{palette.title};font-weight:600;"
        f"font-size:14px;}}"
        f"td,.lang{{color:{palette.value};}}"
        f".label,.percent{{color:{palette.label};font-weight:400;}}"
        # Language dots carry an inline fill per language, which beats this;
        # only the overview's icons pick it up.
        f".octicon{{fill:{palette.label};}}"
    )


def restyle(template: str, palette: StatsPalette) -> str:
    if MARKER in template:
        return template
    if STYLE_END not in template:
        raise ValueError("template has no <style> block to extend")
    resized, count = SVG_WIDTH.subn(rf"\g<1>{CARD_WIDTH}\g<2>", template, count=1)
    if not count:
        raise ValueError("template has no root <svg width> to resize")
    return resized.replace(STYLE_END, brand_stylesheet(palette) + STYLE_END, 1)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--theme", choices=sorted(PALETTES), required=True)
    parser.add_argument("templates", type=Path, nargs="+")
    args = parser.parse_args(argv)

    palette = PALETTES[args.theme]
    for path in args.templates:
        path.write_text(restyle(path.read_text(encoding="utf-8"), palette), encoding="utf-8")
        print(f"restyled {path} ({args.theme})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
