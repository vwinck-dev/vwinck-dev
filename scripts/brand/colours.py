# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""The four brand colours, plus the neutrals the manual leaves implicit.

The manual's rule for light backgrounds drives most of the light themes:
blue and pink have too little contrast on white, so there they may only fill
a shape outlined in Terminal -- never a line, never text.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Main background. "The brand lives in the dark, like in a terminal."
TERMINAL = "#16181A"
#: The V branch, "vw" in the signature, highlights in code.
AZUL = "#5BCEFA"
#: The W branch, "nck" in the signature, active states.
ROSA = "#F5A9B8"
#: Commits, the eye, and text on Terminal.
BRANCO = "#FFFFFF"


@dataclass(frozen=True)
class Neutrals:
    """Greys for borders and secondary text.

    Not brand colours: the manual only specifies the four above. These are
    picked to sit quietly next to them on each GitHub theme.
    """

    border: str
    #: Body copy that is not the headline: terminal output, card values.
    text: str
    #: Captions, labels, icons.
    muted: str


NEUTRALS_DARK = Neutrals(border="#2D3237", text="#B9BEC3", muted="#8B9298")
NEUTRALS_LIGHT = Neutrals(border="#D0D7DE", text="#3D4349", muted="#5C6369")
