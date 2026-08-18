#!/usr/bin/env python3
"""
Static build for the Callahan Landscaping site.

Every page shares one shell (templates/base.html). Page bodies live in
templates/pages/*.html and the repeated blocks — gallery tiles, review cards,
service list — are generated here from the data below so nothing is duplicated
by hand.

    python3 build.py

Writes index.html, work.html, services.html, about.html and contact.html.
"""

import pathlib, re, sys

ROOT = pathlib.Path(__file__).parent
TPL  = ROOT / "templates"

PHONE_D, PHONE_T = "(802) 503-9275", "+18025039275"

PAGES = [
    ("index",    "Home",     "Callahan Landscaping — South Burlington, Vermont",
     f"Vermont based landscaping company servicing both residential and commercial properties. Text or call {PHONE_D}."),
    ("work",     "Work",     "Work — Callahan Landscaping",
     "Mowing stripes, bed edging, mulch and hedge work across South Burlington and Chittenden County."),
    ("services", "Services", "Services — Callahan Landscaping",
     "Mowing, edging, mulch, hedge and shrub pruning, spring and fall cleanups, and excavation."),
    ("about",    "About",    "About — Callahan Landscaping",
     "Owner operated out of South Burlington, Vermont. Established 2024."),
    ("contact",  "Contact",  "Get a quote — Callahan Landscaping",
     f"Tell us about the property, or text or call {PHONE_D} for a free quote."),
]

# --- gallery -----------------------------------------------------------------
TILES = [
    ("work-01", "Large open lawn, cut in alternating passes."),
    ("work-02", "Residential front lawn, stripes held to the walk."),
    ("work-03", "Cut and trimmed around foundation plantings."),
    ("work-04", "Stripes run the full length of the property."),
    ("work-05", "Beds edged, lawn cut to the bed line."),
    ("work-06", "Back lawn, cut height set for the season."),
    ("work-07", "Street frontage kept square to the curb."),
    ("work-08", "Foundation shrubs shaped and held to size."),
    ("work-09", "Hedge line kept off the siding and the walk."),
    ("work-10", "Bed cleared, edged and mulched flat."),
    ("work-11", "Mulch run tight against a curved bed edge."),
    ("work-12", "Excavator on site for heavier ground work."),
    ("work-13", "Commercial frontage on a regular rotation."),
    ("work-14", "Open ground under mature trees."),
]

# --- reviews. Verbatim from public listings; `True` = Google truncated it. ----
REVIEWS = [
    ("Steph McGarghan", "We had a great experience with this landscaping company. They always showed up on time, were professional and easy to work with, and did a fantastic job. The quality of their work was excellent and their pricing was very fair. Highly recommend!", "Google", False),
    ("Tammy Pidgeon", "I used Callahan landscaping for weekly mowings, my yard always looked amazing. Also had him do some brush removal, loved the results. Very professional and reliable services!", "Google", False),
    ("Stefan Radan", "Amazing work at a very reasonable price! Hunter is the owner operator and has been fantastic to work with!", "Google", False),
    ("Christine W", "Callahan Landscaping did an excellent job with my lawn mowing! They were prompt, professional, and paid great attention to detail. The yard looked neat, clean, and perfectly trimmed afterward. I appreciated their reliability and how easy", "Google", True),
    ("breanna pidgeon", "We had such a great experience! We're a young couple and keeping up with our yard has been a bit overwhelming, but they made everything so easy. They did an amazing job mowing our lawn and it honestly looks the best it has since", "Google", True),
    ("Adnan Hasanovich", "Used Callahan Landscaping while away for a month and they did a fantastic job, very reasonably priced and went above and beyond. Highly recommend!", "Facebook", False),
]

SERVICES = [
    ("Mowing", "Weekly or bi-weekly through the season, cut height set for the property rather than the calendar."),
    ("Edging", "Beds, walkways and drives cut back to a defined line so the lawn stops where it is supposed to."),
    ("Mulch", "Beds cleared, edged, then mulched flat and level to the edge."),
    ("Hedge &amp; shrub pruning", "Foundation plantings shaped and kept to size, not just sheared flat."),
    ("Brush removal", "Overgrown edges and scrub cleared back to usable ground."),
    ("Spring &amp; fall cleanups", "Winter debris off before the first cut; leaves off the lawn before snow sits on them."),
    ("Excavation", "Heavier ground work handled with our own machine rather than subbed out."),
]

SEASONS = [
    ("Spring", "Cleanup, first cuts, beds edged and mulched while the ground is still soft."),
    ("Summer", "The steady stretch. Mowing on a fixed rotation, hedges shaped once growth slows."),
    ("Fall", "Leaves cleared, final cut, beds put to bed before the first hard freeze."),
]

VT_PATH = ("M20.2,0.6 L136.0,0.0 L288.0,1.0 L279.3,42.9 L269.2,75.1 L247.5,123.4 L225.8,134.4 "
           "L209.9,163.6 L198.3,197.8 L188.1,224.0 L170.8,264.2 L160.6,290.4 L157.7,324.6 "
           "L152.0,358.8 L149.1,395.0 L138.9,433.2 L135.2,460.0 L32.7,456.2 L30.9,399.0 "
           "L34.3,342.7 L31.8,290.4 L35.4,278.3 L27.5,250.1 L15.5,224.0 L12.0,193.8 L27.5,163.6 "
           "L25.7,115.3 L34.3,83.1 L48.5,63.0 L27.5,42.9 L20.2,0.6 Z")


def tiles(items):
    return "\n".join(
        f'''        <figure class="tile">
          <picture>
            <source srcset="media/work/{n}.webp" type="image/webp">
            <img src="media/work/{n}.jpg" alt="{c}" loading="lazy" decoding="async" width="800" height="800">
          </picture>
          <figcaption>{c}</figcaption>
        </figure>''' for n, c in items)


def reviews(items):
    return "\n".join(
        f'''        <figure class="rev">
          <blockquote><p>{t}{'…' if tr else ''}</p></blockquote>
          <figcaption>{n}<span>{src}{' · excerpt' if tr else ''}</span></figcaption>
        </figure>''' for n, t, src, tr in items)


def services(items):
    return "\n".join(f'      <li><h3>{h}</h3><p>{p}</p></li>' for h, p in items)


def seasons(items):
    return "\n".join(
        f'      <li><span class="season-k">{k}</span><p>{p}</p></li>' for k, p in items)


BLOCKS = {
    "TILES_ALL":      lambda: tiles(TILES),
    "TILES_FEATURED": lambda: tiles(TILES[:6]),
    "REVIEWS_ALL":    lambda: reviews(REVIEWS),
    "REVIEWS_TOP":    lambda: reviews(REVIEWS[:3]),
    "SERVICES":       lambda: services(SERVICES),
    "SEASONS":        lambda: seasons(SEASONS),
    "VT_PATH":        lambda: VT_PATH,
    "PHONE_D":        lambda: PHONE_D,
    "PHONE_T":        lambda: PHONE_T,
}


def navlinks(active):
    out = []
    for slug, label, *_ in PAGES:
        if slug == "index":
            continue
        cls = ' class="is-active"' if slug == active else ""
        aria = ' aria-current="page"' if slug == active else ""
        out.append(f'      <a href="{slug}.html"{cls}{aria}>{label}</a>')
    return "\n".join(out)


def main():
    base = (TPL / "base.html").read_text()
    built = []
    for slug, label, title, desc in PAGES:
        body = (TPL / "pages" / f"{slug}.html").read_text()
        for key, fn in BLOCKS.items():
            body = body.replace("{{" + key + "}}", fn())
        page = (base
                .replace("{{title}}", title)
                .replace("{{desc}}", desc)
                .replace("{{navmod}}", "" if slug == "index" else " stuck")
                .replace("{{navlinks}}", navlinks(slug))
                .replace("{{content}}", body))
        leftover = re.findall(r"\{\{(\w+)\}\}", page)
        if leftover:
            sys.exit(f"ERROR: unresolved placeholders in {slug}.html: {sorted(set(leftover))}")
        out = ROOT / f"{slug}.html"
        out.write_text(page)
        built.append((out.name, len(page)))
    for name, size in built:
        print(f"  {name:16s} {size:6d} bytes")
    print(f"{len(built)} pages built")


if __name__ == "__main__":
    main()
