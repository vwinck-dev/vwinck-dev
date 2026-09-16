# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Contracts between the README, the generator and the workflows.

The generator had thorough unit tests and the profile still shipped broken:
the terminal workflow never ran, so the README pointed at files that were
never published. These tests cover that gap -- the delivery path, not the
rendering.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from terminal_svg.theme import THEMES

REPO = Path(__file__).resolve().parents[2]
README = REPO / "README.md"
TERMINAL_WORKFLOW = REPO / ".github" / "workflows" / "terminal.yml"
STATS_WORKFLOW = REPO / ".github" / "workflows" / "stats.yml"
PUBLISH_BRANCH = "actions_branch"
DEFAULT_BRANCH = "main"

needs_yaml = unittest.skipIf(yaml is None, "PyYAML not installed")


def readme_references() -> set[str]:
    pattern = rf"{PUBLISH_BRANCH}/([A-Za-z0-9_.-]+\.svg)"
    return set(re.findall(pattern, README.read_text(encoding="utf-8")))


class ReadmeContractTest(unittest.TestCase):
    def test_readme_references_every_file_the_generator_produces(self) -> None:
        produced = {theme.filename for theme in THEMES}
        self.assertTrue(produced <= readme_references())

    def test_readme_references_no_terminal_file_nobody_produces(self) -> None:
        produced = {theme.filename for theme in THEMES}
        referenced_terminals = {
            name for name in readme_references() if name.startswith("terminal")
        }
        self.assertEqual(referenced_terminals - produced, set())

    def test_every_reference_has_a_light_and_dark_variant(self) -> None:
        text = README.read_text(encoding="utf-8")
        for name in readme_references():
            with self.subTest(file=name):
                self.assertRegex(text, rf"{re.escape(name)}#gh-(dark|light)-mode-only")


@needs_yaml
class WorkflowContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.terminal = yaml.safe_load(TERMINAL_WORKFLOW.read_text(encoding="utf-8"))
        self.stats = yaml.safe_load(STATS_WORKFLOW.read_text(encoding="utf-8"))
        # "on" is parsed as the boolean True by YAML 1.1.
        self.terminal_on = self.terminal.get("on", self.terminal.get(True))
        self.stats_on = self.stats.get("on", self.stats.get(True))

    def test_terminal_builds_on_every_push_to_the_default_branch(self) -> None:
        """Regression: a paths filter meant a force push published nothing."""
        push = self.terminal_on["push"]
        self.assertIn(DEFAULT_BRANCH, push["branches"])
        self.assertNotIn(
            "paths",
            push,
            "a paths filter is not evaluated on a force push that rewrites "
            "history, so the terminal silently never builds",
        )

    def test_terminal_can_be_triggered_by_hand(self) -> None:
        self.assertIn("workflow_dispatch", self.terminal_on)

    def test_neither_workflow_force_pushes_the_shared_branch(self) -> None:
        """Both publish to actions_branch; a force push would delete the
        other's files."""
        for name, workflow in (("terminal", self.terminal), ("stats", self.stats)):
            with self.subTest(workflow=name):
                steps = workflow["jobs"]["build"]["steps"]
                script = "\n".join(step.get("run", "") for step in steps)
                self.assertNotRegex(
                    script, rf"push\s+(--force|-f)\s+origin\s+{PUBLISH_BRANCH}"
                )

    def test_both_workflows_share_a_concurrency_group(self) -> None:
        self.assertEqual(
            self.terminal["concurrency"]["group"],
            self.stats["concurrency"]["group"],
        )
