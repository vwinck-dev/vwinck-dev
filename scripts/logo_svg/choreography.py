# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""When each part of the banner moves.

The story, left to right: the V branch is committed and climbs to the merge,
the eye opens there, the W branch leaves it and makes the W. Once the graph is
whole the eye winks for the first time and the signature types itself out
beside it -- ``vw;nck``, then ``-dev`` -- followed by the tagline, then the
caption fades in. From the first wink on, the eye keeps blinking on the
manual's cycle.

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
        How long the eye stays open over the finished graph before the first
        wink.
    ``blink_every``
        One blink every this many seconds. Longer than the manual's 3s: on a
        profile that is read rather than watched, a blink every 3s nags.
    ``blink_closed``
        How long the eye stays shut -- the manual's 0.4s.
    ``lid_travel``
        How long the eye takes to shut, and again to open. A real blink is
        quick; it is the wait between blinks that should feel unhurried.
    ``seconds_per_char``
        Typing speed of the signature and the tagline.
    ``tagline_pause``
        Beat between the signature and the tagline.
    ``caption_fade``
        Fade-in of the footer caption.
    """

    lead_in: float = 0.35
    commit_pop: float = 0.22
    commit_overlap: float = 0.5
    draw_speed: float = 360.0
    eye_hold: float = 0.55
    blink_every: float = 7.0
    blink_closed: float = 0.4
    lid_travel: float = 0.1
    seconds_per_char: float = 0.075
    tagline_pause: float = 0.3
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
class Blink:
    """The eye's loop: starts with the first wink and never stops."""

    starts_at: float
    period: float
    closed: float
    lid_travel: float


@dataclass(frozen=True)
class Choreography:
    marks: dict[str, Cue]
    eye_opens: Cue
    blink: Blink
    wordmark: Cue
    suffix: Cue
    tagline: Cue
    caption: Cue

    @property
    def settles_at(self) -> float:
        """When everything but the blinking eye has come to rest."""
        return self.caption.ends_at


def choreograph(
    wordmark_chars: int,
    suffix_chars: int,
    tagline_chars: int,
    pace: Pace = PACE,
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
    blink = Blink(
        starts_at=graph_done + pace.eye_hold,
        period=pace.blink_every,
        closed=pace.blink_closed,
        lid_travel=pace.lid_travel,
    )

    def typed(starts_at: float, characters: int) -> Cue:
        return Cue(starts_at, characters * pace.seconds_per_char)

    wordmark = typed(blink.starts_at, wordmark_chars)
    suffix = typed(wordmark.ends_at, suffix_chars)
    tagline = typed(suffix.ends_at + pace.tagline_pause, tagline_chars)
    caption = Cue(tagline.ends_at, pace.caption_fade)
    return Choreography(
        marks=marks,
        eye_opens=eye_opens,
        blink=blink,
        wordmark=wordmark,
        suffix=suffix,
        tagline=tagline,
        caption=caption,
    )
