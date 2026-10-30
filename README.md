# Tiny Depth Studio site

Studio home page, served by GitHub Pages at https://tiny-depth-studio.github.io/ (organization site: the repository
name `tiny-depth-studio.github.io` is what puts it at the domain root).

- `index.html` and `404.html` are **generated** by `site/build_site.py`; never hand-edit them. The stylesheet is
  `assets/site.css`. `assets/` also holds the studio logo (512 px, square), the favicon, the touch icon and the card headers in `assets/games/<slug>/header.jpg`.
- Every game keeps its own site in its own repository, published as a project page under this domain:
  - Clicker Ore: `Tiny-Depth-Studio/Clicker-Ore-Legal` at https://tiny-depth-studio.github.io/Clicker-Ore-Legal/.
    Its address must not move: shipped game builds read its privacy policy and `site/data/updates_*.json` from there.
  - Clicker Button: `Tiny-Depth-Studio/Clicker-Button-Legal` at https://tiny-depth-studio.github.io/Clicker-Button-Legal/.
    The game opens its privacy policy and terms from there.
- Links to game sites are absolute (`https://tiny-depth-studio.github.io/...`) so the page also works when opened from
  disk.

## Build

```bash
python site/steam.py        # Steam status, release date and header art -> site/data/games.json, assets/games/
python site/build_site.py   # render index.html and 404.html
```

`.github/workflows/refresh.yml` runs both twice a day, on every push that touches `site/` or the stylesheet, and on
demand, and commits only when something changed. When a game's store page goes public, its card switches from
"Coming soon to Steam" to the Steam button and the store header on the next run.

## Adding a game

1. Create its `<Game>-Legal` repository with the same layout as `Clicker-Button-Legal` and enable Pages.
2. Add one entry to `GAMES` in `site/games.py` (slug, name, Steam app id, site URL, genre, description).
3. Until the store page is public, put a 920x430 header at `assets/games/<slug>/header.jpg`.
4. Optional: give the card its own button colour with `.game.<slug> { --game-accent: ...; }` in `assets/site.css`.

## Security

See [SECURITY.md](SECURITY.md): no JavaScript, no cookies, no third-party requests, a strict Content-Security-Policy on
every page, HTTPS enforced by Pages, and build-time fetching restricted to Steam's CDN.
