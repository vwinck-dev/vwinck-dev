# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

"""The shell prompt the session is rendered under."""

from __future__ import annotations

PROMPT_USER = "vwinck-dev"
PROMPT_HOST = "arch"
PROMPT_CWD = "~"
PROMPT_SIGIL = "$"

#: Rendered prompt, including the trailing space the cursor starts after.
PROMPT_TEXT = f"{PROMPT_USER}@{PROMPT_HOST} {PROMPT_CWD} {PROMPT_SIGIL} "
