# Callahan Landscaping

Static site — plain HTML/CSS/vanilla JS. No framework, no CDN, no external font or
script requests. Serves from any static host as-is.

**Live:** https://callahan-landscaping.vercel.app — Vercel serves the built HTML as static files (`vercel.json` sets clean URLs and cache headers). Requires Python 3 locally; no environment variables. On Vercel `server.py` does not run, so the quote form falls back to a plain POST and nothing is written to `data/quotes.jsonl`.

## Build & run

```bash
python3 build.py && python3 server.py
```

`build.py` renders 5 pages from `templates/base.html` + `templates/pages/*.html`.
Repeated blocks (gallery, reviews, services, seasons) are generated from data at the top
of `build.py` — edit them there, never in the built HTML, which is overwritten.

`server.py` is standard library only. It exists for byte-range support (Safari will not
play the videos without it) and the quote endpoint, which appends JSON Lines to
`data/quotes.jsonl`. On a static host the form degrades to a normal POST.

## Pages

`index` · `work` · `services` · `about` · `contact`

## Everything on the page is real

| Item | Source |
|---|---|
| Phone (802) 503-9275 | Google Business, Yelp, their Facebook bio |
| 639 Hinesburg Rd, Ste 1, South Burlington VT 05403 | Yelp / Google listing |
| "5.0 from 5 Google reviews" | Their Google Business listing |
| 6 customer quotes | 5 Google + 1 Facebook, word for word |
| Hunter, owner operator | Named in Stefan Radan's Google review |
| Est. 2024 | Printed on their logo |
| "residential and commercial properties" | Their Facebook bio, verbatim |
| 31 job photos (14 used) | Their Facebook photo grid |
| Logo + brand green #1A8436 / #4BB93E | Sampled from their own logo file |

Two Google reviews are shown as excerpts ending in "…" because Google truncates them.
Nothing was reworded, padded, or invented.

## Still open

- **Service area.** Not drawn on the map on purpose — marked in-page with a dashed box
  (`[data-needs="client"]`). Confirm the towns and it gets marked.
- **Hours.** Only "opens 6 AM" was visible publicly, so hours are omitted rather than guessed.
- **Photo resolution.** Facebook serves its grid at 414x414; those files are upscaled to
  800px in `media/work/`. They hold at display size but not larger. Drop the originals in
  under the same filenames and nothing else changes.

## Theming

Two rooms. The **page room** (light/parchment, dark on toggle or system preference) and
the **media room** — hero, interior page headers, mountains, footer — which is
permanently dark and never inherits the page theme. That is deliberate: see CLAUDE.md
rule 1. `--media-*` tokens are defined once on `:root` and never redefined inside a theme
block; the hero scrim is literal rgba, not derived from `--bg`.

## The hero video — read before launch

See `CLAUDE.md`. It is AI-generated, the mower deck carries a garbled brand name that is
not a real make, and it is not footage of a Callahan job. Fine as atmosphere behind a
headline; do not describe it as documentary footage of their work.

`media/lawn-*.mp4` are generated from Callahan's own cover photograph — camera motion
only, nothing added to the scene.
