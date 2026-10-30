"""Render index.html and 404.html: the Tiny Depth Studio home page.

Cards come from site/games.py (name, genre, description, site) plus
site/data/games.json (Steam button, release date, header image), which
site/steam.py writes.

The pages ship no JavaScript and no inline style. The Content-Security-Policy
allows the stylesheet and images from this origin only, so nothing on the page
can load or run anything from anywhere else.

Links to game sites are absolute, so the page also works when opened from disk.

Run:  python site/steam.py && python site/build_site.py
"""

import html
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from games import GAMES

DATA = os.path.join(HERE, "data", "games.json")

STUDIO = "Tiny Depth Studio"
SITE_URL = "https://tiny-depth-studio.github.io/"
EMAIL = "tinydepthstudio@gmail.com"
YEAR = 2026

CSP = "; ".join([
    "default-src 'none'",
    "img-src 'self'",
    "style-src 'self'",
    "base-uri 'none'",
    "form-action 'none'",
    "upgrade-insecure-requests",
])

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{description}">
<meta property="og:title" content="{studio}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{site_url}assets/logo.png">
<meta property="og:type" content="website">
<link rel="canonical" href="{site_url}">
<link rel="icon" type="image/png" href="{root}assets/favicon.png">
<link rel="apple-touch-icon" href="{root}assets/apple-touch-icon.png">
<link rel="stylesheet" href="{root}assets/site.css">
</head>
<body>

<header class="top">
  <div class="wrap">
    <a class="brand" href="{root}"><img src="{root}assets/logo.png" alt=""><span>{studio}</span></a>
    <nav class="links">
      <a href="{root}#games">Games</a>
      <a href="{root}#about">About</a>
      <a href="{root}#contact">Contact</a>
    </nav>
  </div>
</header>
"""

FOOT = """
<div class="wrap">
  <footer class="site">
    <span>© {year} {studio}</span>
    <span class="footer-games">{game_links}</span>
  </footer>
</div>

</body>
</html>
"""

INDEX = """
<main>
  <section class="hero wrap">
    <img src="assets/logo.png" alt="{studio} logo">
    <h1>{studio}</h1>
    <p>An independent game studio making games that are easy to start and hard to put down.</p>
  </section>

  <section class="block" id="games">
    <div class="wrap">
      <span class="kicker">Games</span>
      <h2>Our games</h2>
      <div class="games">
{cards}
        <div class="game soon">More games are on the way.</div>
      </div>
    </div>
  </section>

  <section class="block about" id="about">
    <div class="wrap">
      <span class="kicker">About</span>
      <h2>The studio</h2>
      <p>{studio} builds and runs its games end to end: design, code, art direction, live updates and player support. Every game gets its own site with guides, update notes and its legal pages.</p>
    </div>
  </section>

  <section class="block" id="contact">
    <div class="wrap">
      <span class="kicker">Contact</span>
      <h2>Get in touch</h2>
      <div class="contact-row">
        <a class="btn" href="mailto:{email}">{email}</a>
      </div>
    </div>
  </section>
</main>
"""

CARD = """        <article class="game {slug}">
          <a href="{site}"><img src="{image}" alt="{name}" width="460" height="215" loading="lazy"></a>
          <div class="body">
            <h3>{name}</h3>
            <span class="meta">{meta}</span>
            <p>{description}</p>
            <div class="actions">
              <a class="btn primary" href="{site}">Game website</a>
              {store}
            </div>
            <div class="legal">
              <a href="{site}privacy-policy.html">Privacy Policy</a>
              <a href="{site}terms-of-service.html">Terms of Service</a>
            </div>
          </div>
        </article>"""

NOT_FOUND = """
<main>
  <section class="not-found wrap hero">
    <span class="kicker">404</span>
    <h1>Nothing down here</h1>
    <p>This page does not exist. It may have moved, or the link was mistyped.</p>
    <div class="actions">
      <a class="btn primary" href="/">Back to the studio</a>
      <a class="btn" href="/#games">Our games</a>
    </div>
  </section>
</main>
"""


def esc(text):
    return html.escape(text or "", quote=True)


def meta_line(game, store):
    parts = [game["genre"], "Steam"]
    if not store["store_live"] or store.get("coming_soon"):
        parts.append("Coming soon")
    elif store.get("release_date"):
        parts.append("Released " + store["release_date"])
    return " · ".join(esc(part) for part in parts)


def store_button(store):
    if not store["store_live"]:
        return '<span class="btn soon" aria-disabled="true">Coming soon to Steam</span>'
    label = "Wishlist on Steam" if store.get("coming_soon") else "Steam page"
    return '<a class="btn" href="{0}">{1}</a>'.format(esc(store["store_url"]), label)


def card(game, store):
    site = game["site"]
    if not site.startswith("https://") or not site.endswith("/"):
        raise ValueError("game site must be an https URL ending in '/': {0}".format(site))
    if not os.path.exists(os.path.join(ROOT, store["header_image"])):
        raise FileNotFoundError("missing card image {0}".format(store["header_image"]))
    return CARD.format(
        slug=esc(game["slug"]),
        site=esc(site),
        name=esc(game["name"]),
        image=esc(store["header_image"]),
        meta=meta_line(game, store),
        description=esc(game["description"]),
        store=store_button(store),
    )


def page(title, description, root, body):
    head = HEAD.format(csp=CSP, title=esc(title), description=esc(description),
                       studio=STUDIO, site_url=SITE_URL, root=root)
    links = " · ".join('<a href="{0}">{1}</a>'.format(esc(game["site"]), esc(game["name"]))
                       for game in GAMES)
    return head + body + FOOT.format(year=YEAR, studio=STUDIO, game_links=links)


def write(name, text):
    io.open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n").write(text)


def main():
    data = json.load(io.open(DATA, encoding="utf-8"))
    names = [game["name"] for game in GAMES]
    description = "{0} is an independent game studio. Home of {1}.".format(
        STUDIO, " and ".join([", ".join(names[:-1]), names[-1]]) if len(names) > 1 else names[0])

    cards = "\n".join(card(game, data[game["slug"]]) for game in GAMES)
    write("index.html", page(STUDIO, description, "",
                             INDEX.format(studio=STUDIO, email=EMAIL, cards=cards)))
    write("404.html", page("Page not found - " + STUDIO, description, "/", NOT_FOUND))
    print("index.html: {0} games".format(len(GAMES)))


if __name__ == "__main__":
    main()
