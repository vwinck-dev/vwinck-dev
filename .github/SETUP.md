# Setup

The README is one column of images, all served from the `actions_branch`
branch: the animated vwinck-dev banner, two stats cards side by side, and the
animated terminal. Every image follows the brand manual (colours, Geist Mono,
the light-background rule) through the shared `scripts/brand/` package.

The four stats card files (two cards, two themes each) are produced by [`.github/workflows/stats.yml`](workflows/stats.yml),
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
dressing a fresh copy of its templates in each theme first with
[`scripts/restyle_stats.py`](../scripts/restyle_stats.py). That script appends
a brand stylesheet after the template's own instead of rewriting upstream's
colours, so the cascade keeps working whatever upstream changes, and it widens
each card to half the column so the two sit flush with the images around them.

The light themes follow the manual's rule for light backgrounds: blue and pink
are too faint on white, so there they only ever fill a shape outlined in
Terminal (`#16181A`) -- never a line, never text.

Credit for the generator: [rahul-jha98/github-stats-transparent](https://github.com/rahul-jha98/github-stats-transparent),
itself a fork of [jstrieb/github-stats](https://github.com/jstrieb/github-stats).

## The layout

Every image is `LAYOUT_WIDTH` (800px, in `scripts/brand/layout.py`) wide and
draws its card 5px in, like the stats generator does, so all the edges line up
into one column. The README gives the full-width images `width="100%"` and the
stats cards `width="50%"`, so the column stays aligned even when GitHub's is
narrower than 800px.

## The animated banner

[`scripts/build_logo.py`](../scripts/build_logo.py) renders
`logoDarkMode.svg` / `logoLightMode.svg`: the manual's horizontal signature,
animated. The git graph is drawn left to right -- the blue V branch, the eye
opening at the merge, the pink W branch -- then the eye winks shut (the
manual's resting state) as `vw;nck` types itself out, followed by `dev` beneath it.
It plays once; with `prefers-reduced-motion` it shows the resting logo.

The symbol's geometry, in the manual's 280 x 140 units, lives in
`scripts/logo_svg/symbol.py`; the tempo in `PACE` in
`scripts/logo_svg/choreography.py`. The terminal workflow renders it on every
push, alongside the terminal.

## The font

An SVG shown through `<img>` may not fetch anything, so Geist Mono travels
inside each file as a `data:` URI. The subsets in `assets/fonts/` (Latin only,
about 7 KB per weight, OFL-licensed) are committed so the build stays
stdlib-only. To pick up a new Geist release:

```
pip install fonttools brotli
python3 scripts/subset_fonts.py path/to/geist-font/GeistMono/ttf
```

## The animated terminal

`terminal.txt` is the single source of truth for the shell session at the top
of the README. Lines opening with `$ ` are typed out; everything else is
output. Edit that file and nothing else.

[`.github/workflows/terminal.yml`](workflows/terminal.yml) re-renders
`terminalDarkMode.svg` / `terminalLightMode.svg`, together with the banner,
into `actions_branch` on every push. The generator,
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
docker compose run --rm build    # regenerate the banner and terminal into out/
```

Both work without Docker too -- the generators are stdlib-only:

```
python3 -m unittest discover -s scripts/tests -t scripts
python3 scripts/build_logo.py --out-dir out
python3 scripts/build_terminal.py --source terminal.txt --out-dir out
```

Enable the commit hook once per clone. It runs the suite when anything under
`scripts/` or `assets/` is staged, and re-renders the banner and the terminal
when they or `terminal.txt` change, so a commit can never break what gets
published:

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

