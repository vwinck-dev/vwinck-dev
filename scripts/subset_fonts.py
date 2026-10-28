#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Regenerate the Geist Mono subsets in ``assets/fonts``.

A one-off maintenance tool, not part of the build: the subsets are committed,
so the generators and CI stay stdlib-only. Run it only to pick up a new Geist
release or to widen the character range.

    pip install fonttools brotli
    python3 scripts/subset_fonts.py path/to/geist-font/GeistMono/ttf

The ttf directory comes from the release zip at
https://github.com/vercel/geist-font/releases.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from fontTools import subset  # type: ignore[import-not-found]

OUT_DIR = Path(__file__).resolve().parents[1] / "assets" / "fonts"
WEIGHTS = ("Regular", "SemiBold")

#: Basic Latin, Latin-1 (accents, middle dot) and the punctuation the
#: terminal and the banner actually print: dashes, quotes, bullet, ellipsis,
#: arrow.
UNICODES = (
    "U+0020-007E,U+00A0-00FF,U+2013,U+2014,U+2018,U+2019,"
    "U+201C,U+201D,U+2022,U+2026,U+2192"
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ttf_dir", type=Path)
    args = parser.parse_args(argv)

    for weight in WEIGHTS:
        source = args.ttf_dir / f"GeistMono-{weight}.ttf"
        target = OUT_DIR / f"GeistMono-{weight}.woff2"
        subset.main(
            [
                str(source),
                f"--unicodes={UNICODES}",
                "--layout-features=",
                "--no-hinting",
                "--desubroutinize",
                "--flavor=woff2",
                f"--output-file={target}",
            ]
        )
        print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
