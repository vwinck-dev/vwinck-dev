#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""Render the animated vwinck-dev banner at the top of the README.

Same trick as the terminal: the animation is CSS ``@keyframes`` inside the
SVG, which GitHub serves untouched. The work lives in the ``logo_svg``
package; this is only the entry point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from logo_svg import BannerBuilder  # noqa: E402

DEFAULT_OUT_DIR = Path("out")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args(argv)

    for path in BannerBuilder().build(args.out_dir):
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
