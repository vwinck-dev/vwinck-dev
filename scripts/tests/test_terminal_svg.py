"""Tests for the terminal SVG generator."""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from terminal_svg.animation import KeyframeFactory
from terminal_svg.builder import TerminalSvgBuilder
from terminal_svg.cadence import Cadence
from terminal_svg.geometry import METRICS
from terminal_svg.lines import (
    BlankLineRenderer,
    CommandLineRenderer,
    OutputLineRenderer,
    RenderContext,
)
from terminal_svg.prompt import PROMPT_TEXT
from terminal_svg.renderer import TerminalSvgRenderer
from terminal_svg.script import LineKind, TerminalScript
from terminal_svg.theme import THEME_DARK, THEME_LIGHT, THEMES
from terminal_svg.timeline import Timeline

CADENCE = Cadence(
    seconds_per_char=0.1,
    pause_after_command=1.0,
    seconds_per_output_line=0.5,
    hold_at_end=2.0,
)

SCRIPT_TEXT = "$ whoami\n\n  Valentine\n"


def build_timeline(text: str = SCRIPT_TEXT) -> tuple[TerminalScript, Timeline]:
    script = TerminalScript.from_text(text)
    return script, Timeline(script, CADENCE)


class TerminalScriptTest(unittest.TestCase):
    def test_classifies_each_kind_of_line(self) -> None:
        kinds = [line.kind for line in TerminalScript.from_text(SCRIPT_TEXT)]
        self.assertEqual(
            kinds, [LineKind.COMMAND, LineKind.BLANK, LineKind.OUTPUT]
        )

    def test_strips_the_marker_from_a_command(self) -> None:
        line = next(iter(TerminalScript.from_text("$ whoami")))
        self.assertEqual(line.text, "whoami")

    def test_command_width_includes_the_prompt(self) -> None:
        line = next(iter(TerminalScript.from_text("$ ls")))
        self.assertEqual(line.width_in_chars, len(PROMPT_TEXT) + len("ls"))

    def test_a_line_of_only_spaces_is_blank(self) -> None:
        line = next(iter(TerminalScript.from_text("    ")))
        self.assertEqual(line.kind, LineKind.BLANK)


class TimelineTest(unittest.TestCase):
    def test_typing_a_command_takes_one_beat_per_character(self) -> None:
        _, timeline = build_timeline("$ whoami")
        entry = next(iter(timeline))
        self.assertAlmostEqual(
            entry.ends_at - entry.starts_at,
            len("whoami") * CADENCE.seconds_per_char,
        )

    def test_output_waits_for_the_command_and_its_pause(self) -> None:
        _, timeline = build_timeline()
        command, _blank, output = list(timeline)
        self.assertAlmostEqual(
            output.starts_at, command.ends_at + CADENCE.pause_after_command
        )

    def test_cycle_holds_the_finished_screen_before_looping(self) -> None:
        _, timeline = build_timeline()
        self.assertAlmostEqual(
            timeline.cycle_seconds, timeline.settles_at + CADENCE.hold_at_end
        )

    def test_percentages_stay_within_the_cycle(self) -> None:
        _, timeline = build_timeline()
        self.assertEqual(timeline.percent_of(-5.0), 0.0)
        self.assertEqual(timeline.percent_of(timeline.cycle_seconds * 2), 100.0)


class LineRendererTest(unittest.TestCase):
    def setUp(self) -> None:
        self.script, self.timeline = build_timeline()
        self.ctx = RenderContext(
            metrics=METRICS, timeline=self.timeline, keyframes=KeyframeFactory()
        )
        self.command, self.blank, self.output = list(self.timeline)

    def test_blank_lines_draw_nothing(self) -> None:
        fragment = BlankLineRenderer().render(1, self.blank, self.ctx)
        self.assertEqual(fragment.markup, ())
        self.assertEqual(fragment.rules, ())

    def test_output_is_one_element_revealed_at_one_instant(self) -> None:
        fragment = OutputLineRenderer().render(2, self.output, self.ctx)
        self.assertEqual(len(fragment.markup), 1)
        self.assertEqual(len(fragment.rules), 1)
        self.assertIn("opacity", fragment.rules[0])

    def test_a_command_draws_prompt_text_and_cursor(self) -> None:
        fragment = CommandLineRenderer().render(0, self.command, self.ctx)
        self.assertEqual(len(fragment.markup), 3)
        self.assertEqual(len(fragment.rules), 3)

    def test_a_command_is_revealed_one_glyph_at_a_time(self) -> None:
        fragment = CommandLineRenderer().render(0, self.command, self.ctx)
        typing = [rule for rule in fragment.rules if "clip-path" in rule]
        self.assertEqual(len(typing), 1)
        self.assertIn(f"steps({len('whoami')},end)", typing[0])

    def test_output_text_is_escaped(self) -> None:
        _, timeline = build_timeline("  a < b & c")
        ctx = RenderContext(
            metrics=METRICS, timeline=timeline, keyframes=KeyframeFactory()
        )
        fragment = OutputLineRenderer().render(0, next(iter(timeline)), ctx)
        self.assertIn("&lt;", fragment.markup[0])
        self.assertIn("&amp;", fragment.markup[0])
        self.assertNotIn(" < b", fragment.markup[0])


class RendererTest(unittest.TestCase):
    def setUp(self) -> None:
        self.script, self.timeline = build_timeline()
        self.renderer = TerminalSvgRenderer(self.script, self.timeline)
        self.svg = self.renderer.render(THEME_DARK)

    def test_every_animated_element_has_its_keyframes_in_the_document(self) -> None:
        """Regression: the keyframe rules were built and then dropped on the
        floor, so nothing animated and the whole screen showed at once."""
        # The background rect carries no class and is deliberately static.
        animated = set(
            re.findall(r'<(?:text|rect) id="([^"]+)" class="[^"]+"', self.svg)
        )
        self.assertTrue(animated, "expected animated elements in the document")
        for element_id in animated:
            with self.subTest(element=element_id):
                self.assertRegex(
                    self.svg,
                    rf"#{re.escape(element_id)}\{{animation-name:",
                    f"element {element_id} is never bound to an animation",
                )

    def test_every_referenced_animation_is_actually_defined(self) -> None:
        referenced = set()
        for names in re.findall(r"animation-name:([^;}]+)", self.svg):
            referenced.update(name.strip() for name in names.split(","))
        defined = set(re.findall(r"@keyframes\s+([A-Za-z0-9_-]+)", self.svg))
        self.assertEqual(referenced - defined, set())

    def test_all_elements_share_one_cycle_duration(self) -> None:
        durations = set(re.findall(r"animation-duration:([^;}]+)", self.svg))
        self.assertEqual(len(durations), 1)

    def test_canvas_is_sized_from_the_widest_line(self) -> None:
        expected = METRICS.width_for_columns(self.script.widest_line + 1)
        self.assertIn(f'width="{expected:.0f}"', self.svg)

    def test_themes_differ_only_in_colour(self) -> None:
        light = self.renderer.render(THEME_LIGHT)
        self.assertIn(THEME_DARK.palette.prompt, self.svg)
        self.assertNotIn(THEME_DARK.palette.prompt, light)
        self.assertIn(THEME_LIGHT.palette.prompt, light)

    def test_reduced_motion_readers_get_the_finished_screen(self) -> None:
        self.assertIn("prefers-reduced-motion", self.svg)

    def test_document_is_well_formed_xml(self) -> None:
        from xml.etree import ElementTree

        ElementTree.fromstring(self.svg)


class BuilderTest(unittest.TestCase):
    def test_writes_one_file_per_theme(self) -> None:
        script, timeline = build_timeline()
        builder = TerminalSvgBuilder(script, CADENCE)
        with tempfile.TemporaryDirectory() as tmp:
            written = builder.build(Path(tmp))
            self.assertEqual(
                sorted(path.name for path in written),
                sorted(theme.filename for theme in THEMES),
            )
            for path in written:
                self.assertTrue(path.read_text(encoding="utf-8").startswith("<svg"))

    def test_creates_the_output_directory(self) -> None:
        script, _ = build_timeline()
        builder = TerminalSvgBuilder(script, CADENCE)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "nested" / "out"
            builder.build(target)
            self.assertTrue(target.is_dir())


if __name__ == "__main__":
    unittest.main()
