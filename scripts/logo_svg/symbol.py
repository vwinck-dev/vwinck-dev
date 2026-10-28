# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""The VW symbol as a git graph, in the manual's own units.

The manual draws the symbol on a 280 x 140 grid: three baselines (top, middle
of the W, base), a 12u stroke and 28u commits. The blue V branch descends to
a commit and climbs back to the merge; the pink W branch leaves the merge and
makes the W with four commits. The merge itself is the only node drawn as an
arc -- the closed eye -- and both lines stop short of it, leaving the eye
free-standing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, unique

GRID_WIDTH = 280.0
GRID_HEIGHT = 140.0
STROKE = 12.0
COMMIT_RADIUS = 14.0

TOP = 14.0
MIDDLE = 56.0
BASE = 126.0

#: How far the branch lines stop short of the merge, so the eye floats.
EYE_GAP = 22.0
#: Half the width of the closed eye, and how far above the top line its tips
#: sit. The arc radius sets how deep it curves.
EYE_HALF_WIDTH = 20.0
EYE_LIFT = 3.0
EYE_ARC_RADIUS = 24.0


@unique
class Branch(Enum):
    """Which branch a mark belongs to; the palette colours by branch."""

    V = "v"
    W = "w"


@dataclass(frozen=True)
class Point:
    x: float
    y: float

    def toward(self, other: Point, distance: float) -> Point:
        """The point ``distance`` units from here along the line to ``other``."""
        length = math.dist((self.x, self.y), (other.x, other.y))
        ratio = distance / length
        return Point(
            self.x + (other.x - self.x) * ratio,
            self.y + (other.y - self.y) * ratio,
        )


@dataclass(frozen=True)
class Commit:
    name: str
    at: Point
    branch: Branch


@dataclass(frozen=True)
class Edge:
    name: str
    start: Point
    end: Point
    branch: Branch

    @property
    def length(self) -> float:
        return math.dist((self.start.x, self.start.y), (self.end.x, self.end.y))


@dataclass(frozen=True)
class Eye:
    """The merge: open while the graph is being drawn, closed at rest."""

    centre: Point

    @property
    def closed_path(self) -> str:
        left = self.centre.x - EYE_HALF_WIDTH
        right = self.centre.x + EYE_HALF_WIDTH
        tips = self.centre.y - EYE_LIFT
        return (
            f"M{left:.2f} {tips:.2f} "
            f"A{EYE_ARC_RADIUS} {EYE_ARC_RADIUS} 0 0 0 {right:.2f} {tips:.2f}"
        )


V_TOP = Point(14.0, TOP)
V_BASE = Point(58.0, BASE)
MERGE = Point(101.0, TOP)
W_FIRST_BASE = Point(144.0, BASE)
W_MIDDLE = Point(183.0, MIDDLE)
W_SECOND_BASE = Point(222.0, BASE)
W_TOP = Point(266.0, TOP)

EYE = Eye(MERGE)

#: The graph in drawing order, left to right -- the order the animation
#: follows. Commits and edges alternate; the eye sits between the branches.
V_BRANCH: tuple[Commit | Edge, ...] = (
    Commit("c1", V_TOP, Branch.V),
    Edge("e1", V_TOP, V_BASE, Branch.V),
    Commit("c2", V_BASE, Branch.V),
    Edge("e2", V_BASE, MERGE.toward(V_BASE, EYE_GAP), Branch.V),
)

W_BRANCH: tuple[Commit | Edge, ...] = (
    Edge("e3", MERGE.toward(W_FIRST_BASE, EYE_GAP), W_FIRST_BASE, Branch.W),
    Commit("c3", W_FIRST_BASE, Branch.W),
    Edge("e4", W_FIRST_BASE, W_MIDDLE, Branch.W),
    Commit("c4", W_MIDDLE, Branch.W),
    Edge("e5", W_MIDDLE, W_SECOND_BASE, Branch.W),
    Commit("c5", W_SECOND_BASE, Branch.W),
    Edge("e6", W_SECOND_BASE, W_TOP, Branch.W),
    Commit("c6", W_TOP, Branch.W),
)
