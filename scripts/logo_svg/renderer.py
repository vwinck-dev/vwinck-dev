# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""The banner: the horizontal signature, animated, on a card.

Every element is styled in its *final* state, and each animation runs from an
earlier state to that one with ``animation-fill-mode: both``. Two things fall
out of that: before its cue an element sits in its starting state, and a
reader with ``prefers-reduced-motion`` -- for whom every animation is switched
off -- sees the static logo the manual calls the resting state.
"""

from __future__ import annotations

from dataclasses import dataclass
from xml.sax.saxutils import escape

from brand import CARD_INSET, CARD_RADIUS, FONT_STACK, LAYOUT_WIDTH, BRANCO, FontWeight, font_faces

from .choreography import PACE, Choreography, Cue, Pace, choreograph
from .symbol import (
    COMMIT_RADIUS,
    EYE,
    GRID_HEIGHT,
    GRID_WIDTH,
    STROKE,
    V_BRANCH,
    W_BRANCH,
    Commit,
    Edge,
)
from .theme import LogoPalette, LogoTheme

NEWLINE = "\n"

#: The manual's wordmark: "i" is always replaced by ";".
WORDMARK = ("vw", ";", "nck")
#: The descriptor under the wordmark, where the manual's signature puts DEV.
TITLE = "dev"
CAPTION_LEFT = ("main", " + ", "feature", " → merge")
CAPTION_RIGHT = "fullstack devsecops · brazil"
LABEL = "vwinck-dev"

EDGE_NAMES = frozenset(
    mark.name for mark in (*V_BRANCH, *W_BRANCH) if isinstance(mark, Edge)
)

#: Advance width of a Geist Mono glyph, as a fraction of the font size.
CHAR_WIDTH_RATIO = 0.6
#: How far below the baseline the cursor block extends, as a fraction of the
#: font size.
CURSOR_DESCENT_RATIO = 0.2
CURSOR_BLINK_SECONDS = 0.9
#: Where typing finishes inside the "type" keyframes. Regression: ending on
#: 100% left Chrome a hair short of it (progress 0.9999999999999994), and
#: steps(n,end) floored that to n-1 -- the title rested one glyph short.
TYPED_AT_PERCENT = 90
#: How long the cursor lingers, blinking, once the title is typed.
CURSOR_LINGER_SECONDS = 2.7


@dataclass(frozen=True)
class BannerLayout:
    """Where everything sits on the card. Units are pixels."""

    width: float = LAYOUT_WIDTH
    height: float = 230.0
    symbol_scale: float = 0.75
    gap: float = 44.0
    #: Vertical centre of the symbol and signature, above the caption.
    centre_y: float = 100.0
    wordmark_size: float = 72.0
    #: Wordmark baseline, below ``centre_y``.
    wordmark_drop: float = 12.0
    title_size: float = 20.0
    #: Title baseline, below the wordmark baseline.
    title_drop: float = 36.0
    caption_size: float = 12.0
    #: Caption baseline, up from the bottom edge.
    caption_rise: float = 30.0
    caption_margin: float = 32.0

    @property
    def symbol_width(self) -> float:
        return GRID_WIDTH * self.symbol_scale

    @property
    def wordmark_width(self) -> float:
        return sum(map(len, WORDMARK)) * self.wordmark_size * CHAR_WIDTH_RATIO

    @property
    def symbol_x(self) -> float:
        content = self.symbol_width + self.gap + self.wordmark_width
        return (self.width - content) / 2

    @property
    def symbol_y(self) -> float:
        return self.centre_y - GRID_HEIGHT * self.symbol_scale / 2

    @property
    def text_x(self) -> float:
        return self.symbol_x + self.symbol_width + self.gap

    @property
    def wordmark_baseline(self) -> float:
        return self.centre_y + self.wordmark_drop

    @property
    def title_baseline(self) -> float:
        return self.wordmark_baseline + self.title_drop

    @property
    def caption_baseline(self) -> float:
        return self.height - self.caption_rise


LAYOUT = BannerLayout()


class BannerRenderer:
    def __init__(self, layout: BannerLayout = LAYOUT, pace: Pace = PACE) -> None:
        self._layout = layout
        self._cues = choreograph(
            wordmark_chars=sum(map(len, WORDMARK)),
            title_chars=len(TITLE),
            pace=pace,
        )

    @property
    def choreography(self) -> Choreography:
        return self._cues

    def render(self, theme: LogoTheme) -> str:
        palette = theme.palette
        layout = self._layout
        return NEWLINE.join(
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'width="{layout.width:.0f}" height="{layout.height:.0f}" '
                f'viewBox="0 0 {layout.width:.0f} {layout.height:.0f}" '
                f'role="img" aria-label="{escape(LABEL)}">',
                f"<title>{escape(LABEL)}</title>",
                f"<style>{self._stylesheet(palette)}</style>",
                self._card(palette),
                self._symbol(palette),
                self._signature(palette),
                self._caption(palette),
                "</svg>",
                "",
            )
        )

    # -- markup -----------------------------------------------------------

    def _card(self, palette: LogoPalette) -> str:
        inset = CARD_INSET + 0.5
        return (
            f'<rect x="{inset}" y="{inset}" '
            f'width="{self._layout.width - 2 * inset:.0f}" '
            f'height="{self._layout.height - 2 * inset:.0f}" '
            f'rx="{CARD_RADIUS}" fill="{palette.background}" '
            f'stroke="{palette.border}" stroke-width="1" />'
        )

    def _symbol(self, palette: LogoPalette) -> str:
        layout = self._layout
        edges, commits = [], []
        for mark in (*V_BRANCH, *W_BRANCH):
            if isinstance(mark, Edge):
                edges.append(
                    f'<path id="{mark.name}" class="edge" '
                    f'd="M{mark.start.x:.2f} {mark.start.y:.2f} '
                    f'L{mark.end.x:.2f} {mark.end.y:.2f}" pathLength="1" '
                    f'stroke="{palette.line[mark.branch]}" />'
                )
            else:
                commits.append(self._commit(mark.name, mark, palette))
        eye = EYE.centre
        open_eye = (
            f'<circle id="eye-open" class="node" cx="{eye.x}" cy="{eye.y}" '
            f'r="{self._commit_radius(palette):.2f}" fill="{BRANCO}" '
            f'stroke="{palette.commit_outline}" '
            f'stroke-width="{palette.commit_outline_width}" />'
        )
        closed_eye = (
            f'<path id="eye-closed" class="edge-static" d="{EYE.closed_path}" '
            f'stroke="{palette.eye}" />'
        )
        return (
            f'<g transform="translate({layout.symbol_x:.2f} {layout.symbol_y:.2f}) '
            f'scale({layout.symbol_scale})">'
            + "".join(edges)
            + closed_eye
            + open_eye
            + "".join(commits)
            + "</g>"
        )

    def _commit(self, element_id: str, commit: Commit, palette: LogoPalette) -> str:
        return (
            f'<circle id="{element_id}" class="node" '
            f'cx="{commit.at.x}" cy="{commit.at.y}" '
            f'r="{self._commit_radius(palette):.2f}" '
            f'fill="{palette.commit[commit.branch]}" '
            f'stroke="{palette.commit_outline}" '
            f'stroke-width="{palette.commit_outline_width}" />'
        )

    @staticmethod
    def _commit_radius(palette: LogoPalette) -> float:
        # An outline is drawn centred on the edge; shrink the circle so the
        # outlined commit keeps the manual's 28u outer diameter.
        return COMMIT_RADIUS - palette.commit_outline_width / 2

    def _signature(self, palette: LogoPalette) -> str:
        layout = self._layout
        vw, semicolon, nck = WORDMARK
        colour_vw, colour_semicolon, colour_nck = palette.wordmark
        wordmark = (
            f'<text id="wordmark" class="wordmark" x="{layout.text_x:.2f}" '
            f'y="{layout.wordmark_baseline:.2f}">'
            f'<tspan fill="{colour_vw}">{vw}</tspan>'
            f'<tspan fill="{colour_semicolon}">{semicolon}</tspan>'
            f'<tspan fill="{colour_nck}">{nck}</tspan></text>'
        )
        title = (
            f'<text id="title" class="title" x="{layout.text_x + self._title_indent:.2f}" '
            f'y="{layout.title_baseline:.2f}" fill="{palette.title}">'
            f"{escape(TITLE)}</text>"
        )
        cursor_height = layout.title_size * (1 + CURSOR_DESCENT_RATIO)
        cursor = (
            f'<rect id="cursor" x="{layout.text_x + self._title_indent:.2f}" '
            f'y="{layout.title_baseline - layout.title_size:.2f}" '
            f'width="{layout.title_size * CHAR_WIDTH_RATIO:.2f}" '
            f'height="{cursor_height:.2f}" fill="{palette.cursor}" />'
        )
        return wordmark + title + cursor

    @property
    def _title_indent(self) -> float:
        # Geist Mono's "v" sits a hair inside its cell at 72px; nudging the
        # title by the same amount lines the two left edges up optically.
        return self._layout.wordmark_size * 0.04

    def _caption(self, palette: LogoPalette) -> str:
        layout = self._layout
        main, plus, feature, merge = CAPTION_LEFT
        colour_main, colour_feature = palette.caption_branches
        left = (
            f'<text class="caption" x="{layout.caption_margin:.2f}" '
            f'y="{layout.caption_baseline:.2f}" fill="{palette.muted}">'
            f'<tspan fill="{colour_main}">{main}</tspan>{escape(plus)}'
            f'<tspan fill="{colour_feature}">{feature}</tspan>{escape(merge)}</text>'
        )
        right = (
            f'<text class="caption" x="{layout.width - layout.caption_margin:.2f}" '
            f'y="{layout.caption_baseline:.2f}" text-anchor="end" '
            f'fill="{palette.muted}">{escape(CAPTION_RIGHT)}</text>'
        )
        return f'<g id="caption">{left}{right}</g>'

    # -- style ------------------------------------------------------------

    def _stylesheet(self, palette: LogoPalette) -> str:
        layout = self._layout
        cues = self._cues
        return "".join(
            (
                font_faces((FontWeight.REGULAR, FontWeight.SEMIBOLD)),
                f"text{{font-family:{FONT_STACK};white-space:pre;}}",
                f".wordmark{{font-size:{layout.wordmark_size}px;font-weight:600;"
                f"letter-spacing:0;}}",
                f".title{{font-size:{layout.title_size}px;font-weight:400;}}",
                f".caption{{font-size:{layout.caption_size}px;letter-spacing:0.04em;}}",
                f".edge,.edge-static{{fill:none;stroke-width:{STROKE};"
                f"stroke-linecap:round;}}",
                ".edge{stroke-dasharray:1;}",
                ".node,#eye-closed{transform-box:fill-box;transform-origin:center;}",
                "#eye-open{opacity:0;}",
                "#cursor{visibility:hidden;}",
                self._keyframes(),
                "".join(self._bind(name, cue) for name, cue in cues.marks.items()),
                self._bind_eye(cues),
                self._bind_typing("wordmark", cues.wordmark, sum(map(len, WORDMARK))),
                self._bind_typing("title", cues.title, len(TITLE)),
                self._bind_cursor(cues.title),
                f"#caption{{animation:fade {cues.caption.duration:.3f}s ease-out "
                f"{cues.caption.starts_at:.3f}s 1 both;}}",
                "@media (prefers-reduced-motion:reduce){*{animation:none!important;}}",
            )
        )

    @staticmethod
    def _keyframes() -> str:
        return (
            "@keyframes pop{0%{transform:scale(0);}"
            "70%{transform:scale(1.15);}100%{transform:scale(1);}}"
            "@keyframes draw{0%{stroke-dashoffset:1;opacity:0;}"
            "1%{opacity:1;}100%{stroke-dashoffset:0;opacity:1;}}"
            "@keyframes shut{0%{transform:scaleY(0.15);opacity:0;}"
            "100%{transform:scaleY(1);opacity:1;}}"
            "@keyframes fade{0%{opacity:0;transform:translateY(4px);}"
            "100%{opacity:1;transform:translateY(0);}}"
            "@keyframes type{0%{clip-path:inset(0 100% 0 0);}"
            f"{TYPED_AT_PERCENT}%,100%{{clip-path:inset(0 0 0 0);}}}}"
            "@keyframes blink{0%,50%{opacity:1;}50.01%,100%{opacity:0;}}"
        )

    @staticmethod
    def _bind(element_id: str, cue: Cue) -> str:
        if element_id in EDGE_NAMES:
            return (
                f"#{element_id}{{animation:draw {cue.duration:.3f}s linear "
                f"{cue.starts_at:.3f}s 1 both;}}"
            )
        return (
            f"#{element_id}{{animation:pop {cue.duration:.3f}s ease-out "
            f"{cue.starts_at:.3f}s 1 both;}}"
        )

    @staticmethod
    def _bind_eye(cues: Choreography) -> str:
        """Open at the merge, hold over the finished graph, then wink shut.

        The open eye is one animation across its whole life, so its keyframes
        are percentages of that span; the closed eye simply appears as the
        open one collapses.
        """
        opens, wink = cues.eye_opens, cues.wink
        span = wink.ends_at - opens.starts_at
        popped = opens.duration / span * 100
        winking = (wink.starts_at - opens.starts_at) / span * 100
        return (
            f"@keyframes eye{{0%{{transform:scale(0);opacity:1;}}"
            f"{popped * 0.7:.3f}%{{transform:scale(1.15);opacity:1;}}"
            f"{popped:.3f}%,{winking:.3f}%{{transform:scale(1);opacity:1;}}"
            f"100%{{transform:scaleY(0.1);opacity:0;}}}}"
            f"#eye-open{{animation:eye {span:.3f}s ease-in-out "
            f"{opens.starts_at:.3f}s 1 both;}}"
            f"#eye-closed{{animation:shut {wink.duration:.3f}s ease-out "
            f"{wink.starts_at + wink.duration / 2:.3f}s 1 both;}}"
        )

    @staticmethod
    def _bind_typing(element_id: str, cue: Cue, characters: int) -> str:
        # steps() over a clip-path inset uncovers exactly one glyph per step
        # on a monospace face: typing, not a wipe. The animation runs a little
        # past the typing so the last glyph lands on a held keyframe, not on
        # the final instant (see TYPED_AT_PERCENT).
        duration = cue.duration * 100 / TYPED_AT_PERCENT
        return (
            f"#{element_id}{{animation:type {duration:.3f}s "
            f"steps({characters},end) {cue.starts_at:.3f}s 1 both;}}"
        )

    def _bind_cursor(self, title: Cue) -> str:
        """Walk the cursor along the title as it types, blink a few times,
        then leave the finished banner alone."""
        travel = len(TITLE) * self._layout.title_size * CHAR_WIDTH_RATIO
        span = title.duration + CURSOR_LINGER_SECONDS
        typed = title.duration / span * 100
        blinks = max(1, round(CURSOR_LINGER_SECONDS / CURSOR_BLINK_SECONDS))
        return (
            f"@keyframes caret{{0%{{visibility:visible;transform:translateX(0);}}"
            f"{typed:.3f}%{{visibility:visible;transform:translateX({travel:.2f}px);}}"
            f"99.99%{{visibility:visible;transform:translateX({travel:.2f}px);}}"
            f"100%{{visibility:hidden;transform:translateX({travel:.2f}px);}}}}"
            f"#cursor{{animation:caret {span:.3f}s steps({len(TITLE)},end) "
            f"{title.starts_at:.3f}s 1 forwards,"
            f"blink {CURSOR_BLINK_SECONDS}s step-end "
            f"{title.ends_at:.3f}s {blinks};}}"
        )
