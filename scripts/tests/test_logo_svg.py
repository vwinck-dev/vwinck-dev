# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Tests for the animated banner, and the brand rules it has to keep."""

from __future__ import annotations

import math
import re
import sys
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from brand import AZUL, ROSA, TERMINAL, FontWeight, font_faces
from logo_svg.builder import BannerBuilder
from logo_svg.choreography import choreograph
from logo_svg.renderer import SUFFIX, TAGLINE, WORDMARK, BannerRenderer
from logo_svg.symbol import (
    EYE,
    EYE_GAP,
    GRID_HEIGHT,
    GRID_WIDTH,
    V_BRANCH,
    W_BRANCH,
    Branch,
    Commit,
    Edge,
)
from logo_svg.theme import THEME_DARK, THEME_LIGHT, THEMES

SVG_NS = "{http://www.w3.org/2000/svg}"


def edges() -> list[Edge]:
    return [mark for mark in (*V_BRANCH, *W_BRANCH) if isinstance(mark, Edge)]


def commits() -> list[Commit]:
    return [mark for mark in (*V_BRANCH, *W_BRANCH) if isinstance(mark, Commit)]


class SymbolTest(unittest.TestCase):
    def test_the_grid_keeps_the_manuals_two_to_one_proportion(self) -> None:
        self.assertEqual(GRID_WIDTH / GRID_HEIGHT, 2)

    def test_six_commits_plus_the_eye(self) -> None:
        self.assertEqual(len(commits()), 6)

    def test_the_v_branch_has_two_commits_and_the_w_branch_four(self) -> None:
        by_branch = [commit.branch for commit in commits()]
        self.assertEqual(by_branch.count(Branch.V), 2)
        self.assertEqual(by_branch.count(Branch.W), 4)

    def test_both_branches_stop_short_of_the_merge(self) -> None:
        """The eye floats: no line may touch it."""
        merge = EYE.centre
        for edge in edges():
            for end in (edge.start, edge.end):
                with self.subTest(edge=edge.name):
                    self.assertGreaterEqual(
                        math.dist((end.x, end.y), (merge.x, merge.y)),
                        EYE_GAP - 1e-6,
                    )

    def test_the_graph_is_drawn_left_to_right(self) -> None:
        xs = [mark.at.x if isinstance(mark, Commit) else mark.start.x
              for mark in (*V_BRANCH, *W_BRANCH)]
        self.assertEqual(xs, sorted(xs))


class ChoreographyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cues = choreograph(wordmark_chars=6, suffix_chars=4, tagline_chars=29)

    def test_marks_start_in_drawing_order(self) -> None:
        names = [mark.name for mark in (*V_BRANCH, *W_BRANCH)]
        starts = [self.cues.marks[name].starts_at for name in names]
        self.assertEqual(starts, sorted(starts))

    def test_the_eye_opens_between_the_branches(self) -> None:
        last_v = self.cues.marks[V_BRANCH[-1].name]
        first_w = self.cues.marks[W_BRANCH[0].name]
        self.assertGreaterEqual(self.cues.eye_opens.starts_at, last_v.ends_at)
        self.assertLessEqual(self.cues.eye_opens.starts_at, first_w.starts_at)

    def test_the_first_wink_waits_for_the_whole_graph(self) -> None:
        graph_done = max(cue.ends_at for cue in self.cues.marks.values())
        self.assertGreater(self.cues.blink.starts_at, graph_done)

    def test_the_eye_blinks_on_the_manuals_cycle(self) -> None:
        """Manual: one blink every 3s, eye shut for 0.4s."""
        self.assertEqual(self.cues.blink.period, 3.0)
        self.assertEqual(self.cues.blink.closed, 0.4)

    def test_the_signature_arrives_with_the_wink_then_dev_then_the_tagline(self) -> None:
        cues = self.cues
        self.assertEqual(cues.wordmark.starts_at, cues.blink.starts_at)
        self.assertEqual(cues.suffix.starts_at, cues.wordmark.ends_at)
        self.assertGreater(cues.tagline.starts_at, cues.suffix.ends_at)
        self.assertGreaterEqual(cues.caption.starts_at, cues.tagline.ends_at)


class BannerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = BannerRenderer()
        self.dark = self.renderer.render(THEME_DARK)
        self.light = self.renderer.render(THEME_LIGHT)

    def test_documents_are_well_formed_xml(self) -> None:
        for svg in (self.dark, self.light):
            ElementTree.fromstring(svg)

    def test_every_referenced_animation_is_defined(self) -> None:
        for svg in (self.dark, self.light):
            defined = set(re.findall(r"@keyframes\s+([A-Za-z0-9_-]+)", svg))
            used = set()
            for value in re.findall(r"animation:([^;}]+)", svg):
                # Split the shorthand list, not the commas inside steps(n,end).
                for part in re.split(r",(?![^(]*\))", value):
                    used.add(part.split()[0])
            self.assertEqual(used - defined - {"none!important"}, set())

    def test_every_mark_is_animated(self) -> None:
        for mark in (*V_BRANCH, *W_BRANCH):
            with self.subTest(mark=mark.name):
                self.assertIn(f"#{mark.name}{{animation:", self.dark)

    def test_only_the_eye_keeps_moving(self) -> None:
        """The eye blinks for as long as the banner is on screen; everything
        else plays once and rests, like the terminal."""
        looping = re.findall(r"#([\w-]+)\{animation:[^}]*infinite", self.dark)
        self.assertEqual(sorted(looping), ["eye-closed", "eye-open"])

    def test_reduced_motion_readers_get_the_resting_logo(self) -> None:
        self.assertIn("prefers-reduced-motion", self.dark)
        # At rest the eye is closed: the open eye is hidden by default and
        # the closed one is not.
        self.assertIn("#eye-open{opacity:0;}", self.dark)
        self.assertNotRegex(self.dark, r"#eye-closed\{[^}]*opacity:0")

    def test_the_wordmark_and_title_are_typed(self) -> None:
        self.assertIn(f"steps({sum(map(len, WORDMARK))},end)", self.dark)
        self.assertIn(f"steps({len(SUFFIX)},end)", self.dark)
        self.assertIn(f"steps({len(TAGLINE)},end)", self.dark)

    def test_typing_lands_before_the_animation_ends(self) -> None:
        """Regression: Chrome finished the title at progress 0.99999...,
        which steps(n,end) floors to n-1 glyphs. The last glyph has to land
        on a keyframe that is then held."""
        keyframes = re.search(r"@keyframes type\{(.*?)\}\}", self.dark).group(1)
        self.assertRegex(keyframes, r"\b(?!100%)\d+(\.\d+)?%,100%\{clip-path:inset\(0 0 0 0\)")

    def test_the_wordmark_spells_vw_semicolon_nck(self) -> None:
        self.assertEqual("".join(WORDMARK), "vw;nck")

    def test_dark_colours_the_v_blue_and_the_w_pink(self) -> None:
        root = ElementTree.fromstring(self.dark)
        strokes = {
            path.get("id"): path.get("stroke") for path in root.iter(f"{SVG_NS}path")
        }
        for edge in edges():
            expected = AZUL if edge.branch is Branch.V else ROSA
            self.assertEqual(strokes[edge.name], expected)

    def test_light_never_uses_blue_or_pink_for_lines_or_text(self) -> None:
        """Manual: on light backgrounds blue and pink only fill commits,
        inside a Terminal outline."""
        root = ElementTree.fromstring(self.light)
        for element in root.iter():
            tag = element.tag.removeprefix(SVG_NS)
            if tag == "circle":
                self.assertEqual(element.get("stroke"), TERMINAL)
                continue
            for attribute in ("fill", "stroke"):
                with self.subTest(tag=tag, attribute=attribute):
                    self.assertNotIn(element.get(attribute), (AZUL, ROSA))

    def test_the_label_names_the_brand(self) -> None:
        root = ElementTree.fromstring(self.dark)
        self.assertTrue(root.get("aria-label").startswith("vwinck-dev"))

    def test_dev_sits_beside_the_wordmark_on_its_baseline(self) -> None:
        root = ElementTree.fromstring(self.dark)
        texts = {t.get("id"): t for t in root.iter(f"{SVG_NS}text")}
        wordmark, suffix = texts["wordmark"], texts["suffix"]
        self.assertEqual(suffix.text, "-dev")
        self.assertEqual(suffix.get("y"), wordmark.get("y"))
        self.assertGreater(float(suffix.get("x")), float(wordmark.get("x")))

    def test_the_tagline_never_prints_the_full_name(self) -> None:
        self.assertTrue(TAGLINE.startswith("V. Winck's"))

    def test_the_font_travels_inside_the_file(self) -> None:
        self.assertIn("data:font/woff2;base64,", self.dark)


class FontsTest(unittest.TestCase):
    def test_every_weight_has_its_subset_committed(self) -> None:
        for weight in FontWeight:
            with self.subTest(weight=weight.name):
                self.assertTrue(weight.path.is_file())

    def test_one_face_per_weight(self) -> None:
        self.assertEqual(font_faces().count("@font-face"), len(FontWeight))


class BannerBuilderTest(unittest.TestCase):
    def test_writes_one_file_per_theme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            written = BannerBuilder().build(Path(tmp) / "out")
            self.assertEqual(
                sorted(path.name for path in written),
                sorted(theme.filename for theme in THEMES),
            )


if __name__ == "__main__":
    unittest.main()
