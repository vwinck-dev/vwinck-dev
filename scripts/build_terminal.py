#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Render ``terminal.txt`` as a pair of self-animating SVG terminals.

GitHub strips ``<script>`` and ``<style>`` from README markup, but it serves
SVG files untouched, and CSS *inside* an SVG still runs. That is the whole
trick: the typing effect is declared as ``@keyframes`` in the document itself.

The work lives in the ``terminal_svg`` package; this is only the entry point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from terminal_svg import TerminalScript, TerminalSvgBuilder  # noqa: E402

DEFAULT_SOURCE = Path("terminal.txt")
DEFAULT_OUT_DIR = Path("out")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args(argv)

    builder = TerminalSvgBuilder(TerminalScript.from_file(args.source))
    for path in builder.build(args.out_dir):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
