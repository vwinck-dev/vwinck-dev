# MIT License
#
# Copyright (c) 2026 vwinck-dev <https://github.com/vwinck-dev>
# SPDX-License-Identifier: MIT
#
# Full terms in the LICENSE file at the repository root.

# The generator is stdlib-only, so this image installs nothing: it exists to
# pin the interpreter, not to carry dependencies.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /repo

# Run as a non-root user so files written into the mounted volume are not
# owned by root on the host.
ARG UID=1000
ARG GID=1000
RUN groupadd --gid "${GID}" app 2>/dev/null || true \
 && useradd --uid "${UID}" --gid "${GID}" --create-home app 2>/dev/null || true
USER ${UID}:${GID}

CMD ["python3", "scripts/build_terminal.py", "--help"]
