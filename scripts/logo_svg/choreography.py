# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""When each part of the banner moves.

The story, left to right: the V branch is committed and climbs to the merge,
the eye opens there, the W branch leaves it and makes the W. Once the graph is
whole the eye winks shut -- the manual's resting state -- and the signature
types itself out beside it, then the title, then the caption fades in.

Knows nothing about SVG: it turns a ``Pace`` into seconds per element.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .symbol import V_BRANCH, W_BRANCH, Commit, Edge


@dataclass(frozen=True)
class Pace:
    """Tempo of the animation.

    ``lead_in``
        Quiet beat before anything moves, so a reader scrolling in sees the
        first commit land rather than missing it.
    ``commit_pop``
        How long a commit takes to pop in. The next mark starts at
        ``commit_overlap`` of the way through, so the graph reads as one
        gesture instead of a list of steps.
    ``draw_speed``
        Grid units per second a branch line is drawn at. Speed, not duration,
        so a long leg takes longer than a short one.
    ``eye_hold``
        How long the eye stays open over the finished graph before winking.
    ``wink``
        Length of the wink itself. The manual's blink keeps the eye shut for
        0.4s; closing is a fraction of that.
    ``seconds_per_char``
        Typing speed of the signature and the title.
    ``title_pause``
        Beat between the signature and the title.
    ``caption_fade``
        Fade-in of the footer caption.
    """

    lead_in: float = 0.35
    commit_pop: float = 0.22
    commit_overlap: float = 0.5
    draw_speed: float = 360.0
    eye_hold: float = 0.55
    wink: float = 0.18
    seconds_per_char: float = 0.075
    title_pause: float = 0.3
    caption_fade: float = 0.7


PACE = Pace()


@dataclass(frozen=True)
class Cue:
    """One element's moment: when it starts moving and for how long."""

    starts_at: float
    duration: float

    @property
    def ends_at(self) -> float:
        return self.starts_at + self.duration


@dataclass(frozen=True)
class Choreography:
    marks: dict[str, Cue]
    eye_opens: Cue
    wink: Cue
    wordmark: Cue
    title: Cue
    caption: Cue

    @property
    def settles_at(self) -> float:
        return self.caption.ends_at


def choreograph(
    wordmark_chars: int, title_chars: int, pace: Pace = PACE
) -> Choreography:
    marks: dict[str, Cue] = {}
    clock = pace.lead_in

    def pop() -> Cue:
        nonlocal clock
        cue = Cue(clock, pace.commit_pop)
        clock += pace.commit_pop * pace.commit_overlap
        return cue

    def walk(branch: Sequence[Commit | Edge]) -> None:
        nonlocal clock
        for mark in branch:
            if isinstance(mark, Commit):
                marks[mark.name] = pop()
            else:
                marks[mark.name] = Cue(clock, mark.length / pace.draw_speed)
                clock = marks[mark.name].ends_at

    walk(V_BRANCH)
    eye_opens = pop()
    walk(W_BRANCH)

    graph_done = max(cue.ends_at for cue in marks.values())
    wink = Cue(graph_done + pace.eye_hold, pace.wink)
    wordmark = Cue(wink.starts_at, wordmark_chars * pace.seconds_per_char)
    title = Cue(
        wordmark.ends_at + pace.title_pause, title_chars * pace.seconds_per_char
    )
    caption = Cue(title.ends_at, pace.caption_fade)
    return Choreography(
        marks=marks,
        eye_opens=eye_opens,
        wink=wink,
        wordmark=wordmark,
        title=title,
        caption=caption,
    )
