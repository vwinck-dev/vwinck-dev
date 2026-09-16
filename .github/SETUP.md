# Setup

The README embeds four stats cards served from the `actions_branch` branch.
They are produced by [`.github/workflows/stats.yml`](workflows/stats.yml),
which runs daily at 05:00 UTC and can be triggered by hand from the Actions
tab.

## Required secret

| secret | value |
| --- | --- |
| `ACCESS_TOKEN` | A classic personal access token with the `read:user` and `repo` scopes. |

Without it the workflow stops at `A personal access token is required to
proceed!`, `actions_branch` is never created, and the images in the README
render broken.

> The `GITHUB_TOKEN` that Actions injects automatically is **not** enough: it
> cannot read statistics for private repositories or for repositories owned by
> other people that you contributed to.

## Optional secrets

| secret | value |
| --- | --- |
| `EXCLUDED` | Comma-separated `owner/repo` entries to leave out of the stats. |
| `EXCLUDED_LANGS` | Comma-separated language names to leave out of the language card. |
| `COUNT_STATS_FROM_FORKS` | Set to any value to also count forks you contributed to. |

## How the two themes work

GitHub does not tell an embedded SVG which theme the reader is using, so the
theme has to be picked when the file is served. The README relies on the
`#gh-dark-mode-only` and `#gh-light-mode-only` fragments, which means each card
needs two separate files. The workflow therefore runs the generator twice,
rewriting the palette in the SVG templates between runs.

Credit for the generator: [rahul-jha98/github-stats-transparent](https://github.com/rahul-jha98/github-stats-transparent),
itself a fork of [jstrieb/github-stats](https://github.com/jstrieb/github-stats).

## The animated terminal

`terminal.txt` is the single source of truth for the shell session at the top
of the README. Lines opening with `$ ` are typed out; everything else is
output. Edit that file and nothing else.

[`.github/workflows/terminal.yml`](workflows/terminal.yml) watches it and
re-renders `terminalDarkMode.svg` / `terminalLightMode.svg` into
`actions_branch` on every push that touches it. The generator,
[`scripts/build_terminal.py`](../scripts/build_terminal.py), is stdlib-only
and needs no secret, so it keeps working even while the stats workflow is
failing.

The generator lives in `scripts/terminal_svg/`. Typing speed, the pause after
each command and the hold before the loop restarts live in `CADENCE` in
`scripts/terminal_svg/cadence.py`.

Those numbers are chosen around one constraint: the SVG has a fixed height, so
until the screen fills, a visitor is looking at an empty box. The current
values fill it in about five seconds and hold it for nine, so most of the loop
shows a finished terminal.

### Working on it

```
docker compose run --rm test     # the suite
docker compose run --rm build    # regenerate into out/
```

Both work without Docker too -- the generator is stdlib-only:

```
python3 -m unittest discover -s scripts/tests -t scripts
python3 scripts/build_terminal.py --source terminal.txt --out-dir out
```

Enable the commit hook once per clone. It runs the suite when anything under
`scripts/` is staged, and re-renders the terminal when `terminal.txt` changes,
so a commit can never leave the published SVG behind the source:

```
git config core.hooksPath .githooks
```

> Both workflows write to `actions_branch`, so both publish additively and
> share a `concurrency` group. Neither may force-push the branch: that would
> delete the other's files.

### Known trade-offs

Because the terminal is an image, its text cannot be selected or copied, it
is not indexed, and any link inside it is dead. Contact links therefore live
in the README itself, below the terminal, as real HTML.

GitHub proxies README images through *camo*, which caches aggressively, so a
regenerated terminal can take a few minutes to appear.

