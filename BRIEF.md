# Paste this into the new Claude Code project

Fill in the six bracketed lines, delete this heading, paste the rest as your first message.

---

Build a landing page for **[CLIENT NAME]**, a **[trade — e.g. lawn care / landscaping]**
business in **[TOWN, STATE]**. Phone **[NUMBER]**.

The hero video already exists — `media/hero_1920x1080.mp4` with `media/hero-poster.webp`.
**Do not generate or replace it.** Read `CLAUDE.md` in this folder first; it documents the
asset and three non-negotiable rules about heroes, theme handling and type scaling that
this specific video imposes. Follow them.

## What I want

A static site — no framework, no CDN, no external font or script requests. Plain HTML, CSS
and vanilla JS, servable from any static host. If it grows past two pages, generate them
from templates with a small Python build script rather than duplicating the shell.

Pages: **[Home / Services / Work / About / Contact — cut what doesn't apply]**

## Tone

**[e.g. plain and local, short declaratives, no agency language. Or: premium and
restrained. Or: loud and blue-collar.]**

Whatever it is, find the client's actual differentiator before writing a headline — read
their reviews, their bio, how customers describe them — and build the copy on that instead
of generic trade claims. Every trade says "quality workmanship"; it persuades nobody.

## Design direction

- Dark, photography-first, with the hero video full-bleed at `100svh`
- One accent colour, pulled from something real in the client's own photos (their uniform,
  their equipment, their truck) rather than invented
- Editorial type scale — large display headings, a monospace for small caps labels
- Restrained motion: entrance reveals on scroll, no parallax, no cursor that trails the
  pointer. If you want click feedback, a small ripple at the pointer is enough.
- Respect `prefers-reduced-motion` throughout

## Non-negotiables

1. **Never invent proof.** No made-up review counts, star ratings, years in business,
   number of customers, or service towns. If I haven't given you the number, leave the
   section out and tell me what you need.
2. **Never generate fake job photos.** In the trades the real before/afters *are* the
   credential; a fabricated result is both a legal risk and a worse sell.
3. Real content or a clearly-labelled placeholder. Nothing in between.

## Before you say it's done

- No horizontal overflow at 375px and 1440px, on every page
- No broken images
- Hero copy clears the video's subject at 1280x720, 1440x900 and 1920x1080 — check all
  three, a fix that works at one routinely fails at another
- Every internal link resolves
- Tell me plainly what still needs the client's confirmation before it can go public
