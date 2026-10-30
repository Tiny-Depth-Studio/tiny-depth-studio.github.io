"""The studio's games, in the order the home page lists them.

A new game is one entry here. `site` is the game's own site (its `<Game>-Legal`
repository on GitHub Pages); its privacy policy and terms live next to it.

`genre` and `description` are written by hand for the card. Everything else on
the card (Steam button, release date, header image) comes from Steam through
site/steam.py. Until a game's store page is public, its card shows
"Coming soon to Steam" and the local header at assets/games/<slug>/header.jpg.
"""

GAMES = [
    {
        "slug": "clicker-ore",
        "name": "Clicker Ore",
        "app_id": 3810540,
        "site": "https://tiny-depth-studio.github.io/Clicker-Ore-Legal/",
        "genre": "Idle mining & clicker",
        "description": "Grab your pickaxe, descend into the depths, and become the master of wealth. "
                       "Your mine keeps working even while you're away.",
    },
    {
        "slug": "clicker-button",
        "name": "Clicker Button",
        "app_id": 5526030,
        "site": "https://tiny-depth-studio.github.io/Clicker-Button-Legal/",
        "genre": "Shape-fitting 3D clicker",
        "description": "Buy buttons shaped like blocks, fit them onto your grid and click them for cash. "
                       "Harder shapes pay bigger multipliers.",
    },
]
