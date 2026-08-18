# Project: landing page built around the mower hero video

Drop this folder into a new Claude Code project. `media/` already holds a finished,
upscaled hero loop — **do not regenerate it**, build the page around it.

---

## The asset

| File | What it is |
|---|---|
| `media/hero_1920x1080.mp4` | Ship this. 12 MB, 8.7s, silent, H.264, faststart. |
| `media/hero-master_2880x1620.mp4` | 47 MB master. Archive; re-encode from this if you need another size. |
| `media/hero-poster.webp` | 146 KB poster — always set it, the first frame is otherwise black. |
| `media/hero-poster.jpg` | JPEG fallback. |

Content: low ground-level shot, a man on a red zero-turn mower on a striped lawn in front
of a suburban house, cumulus sky, slow camera move. Frame is **16:9, fills edge to edge,
no letterbox bars**.

```html
<video src="media/hero_1920x1080.mp4" poster="media/hero-poster.webp"
       autoplay muted loop playsinline></video>
```

`autoplay` only works with `muted` **and** `playsinline`. Missing either and iOS shows a
still frame.

---

## Rules that this video specifically imposes

These were learned the hard way on the build this came from. Ignoring them produces the
exact bugs listed.

### 1. A photographic hero must NOT inherit the page theme

If the page has a light mode, do not build the hero scrim from the page background token.
Painting a near-white scrim over a photograph washes it out and leaves dark text sitting on
dark pixels.

Define a separate, theme-independent set:

```css
:root{
  --media-fg:#F5F3EB;
  --media-muted:rgba(245,243,235,.74);
  --media-line:rgba(245,243,235,.34);
  --media-ink:#0A0D0B;
  --media-accent:/* your brand accent, chosen to read on a dark photo */;
}
.hero::after{                       /* always dark, regardless of theme */
  background:
    linear-gradient(180deg, rgba(10,13,11,.58) 0%, rgba(10,13,11,.10) 24%,
                    rgba(10,13,11,.28) 52%, rgba(10,13,11,.74) 78%, rgba(10,13,11,.93) 100%),
    radial-gradient(120% 78% at 50% 42%, transparent 42%, rgba(10,13,11,.42) 100%);
}
.hero-inner{color:var(--media-fg)}
.hero .eyebrow,.hero .lede{color:var(--media-muted)}
```

The nav sits on the photo too until it sticks — give it the same treatment while
`:not(.stuck)`.

### 2. Hero type must scale on height, not just width

The classic bug: `font-size: clamp(2.8rem, 9.5vw, 9.5rem)` on a `100svh` hero. On a
wide-but-short viewport (1440x860, 1280x720) the headline scales off **width** while the
hero is capped by **height**, so the text block grows tall enough to cover the subject.

```css
.display{font-size:clamp(2.6rem, min(9vw, 11svh), 8.6rem)}
```

Cap the lede and the stack gaps the same way (`min(1.5vw, 2.4svh)`, `clamp(.7rem,1.4vh,1.4rem)`).

### 3. Put the copy where the subject isn't — measure it

In this clip the mower and rider occupy roughly the **middle band** of the frame and drift
as the camera moves. Don't guess where text is safe. Sample frames, find the rows the
subject occupies at *any* point in the clip, and keep the text block outside that band.

Then verify the text block's top edge against that band at real viewport sizes —
375x667, 375x812, 768x1024, 1280x720, 1366x768, 1440x900, 1920x1080, 2560x1080.
A fix that works at 1920x1080 routinely fails at 1280x720.

---

## If you need to re-cut or re-encode

```bash
# smaller web copy from the master
ffmpeg -i media/hero-master_2880x1620.mp4 -vf scale=1280:720 \
  -c:v libx264 -crf 22 -preset slow -pix_fmt yuv420p -movflags +faststart -an out.mp4

# fresh poster
ffmpeg -ss 0.2 -i media/hero-master_2880x1620.mp4 -frames:v 1 -q:v 80 poster.webp
```

**Always `-an`.** A hero loop with an audio track will be blocked from autoplaying.

---

## Provenance — read before this ships

This is an **AI-generated video** (Seedance image-to-video), produced from a real
photograph, then upscaled. Two things follow from that:

1. **A recognisable real person appears in it.** The source photograph came from a
   different business's own photo library. Whether it's appropriate to use in another
   company's marketing is a commercial and permissions question — settle it before launch.
2. **Do not describe it as documentary footage of the client's own crew or work.** It
   isn't. It's fine as atmosphere behind a headline; it is not a photo of a job they did.

If the client needs footage that genuinely represents their work, the right move is to
generate from *their* photographs.
