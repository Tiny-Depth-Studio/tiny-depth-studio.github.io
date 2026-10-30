"""Pull the store data of every game in site/games.py off Steam.

Steam's endpoints send no CORS header, so the page cannot fetch them from the
browser - the data is baked in at build time, the same way the game sites do it.
Writes site/data/games.json and, for every game with a public store page, the
store header image to assets/games/<slug>/header.jpg.

Images are downloaded rather than hotlinked so the page's Content-Security-Policy
can keep img-src at 'self'. A download is accepted only from Steam's CDN over
HTTPS, only as a JPEG or PNG, and only up to MAX_IMAGE_BYTES.

A game without a public store page keeps its previous entry (or a "coming
soon" entry), so the scheduled run is harmless before a launch.

Deliberately no fetch timestamp in the output: the scheduled workflow commits
only when a file actually changes.

Run:  python site/steam.py
"""

import datetime
import io
import json
import os
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from games import GAMES

OUT = os.path.join(HERE, "data", "games.json")
DETAILS_URL = "https://store.steampowered.com/api/appdetails?appids={0}&l=english&cc=us"
STORE_URL = "https://store.steampowered.com/app/{0}/"
IMAGE_HOST_SUFFIX = ".steamstatic.com"
MAX_IMAGE_BYTES = 3 * 1024 * 1024
DATE_FORMATS = ["%d %b, %Y", "%b %d, %Y", "%d %B %Y", "%B %d, %Y", "%d %b %Y"]


def open_url(url):
    request = urllib.request.Request(url, headers={"User-Agent": "tiny-depth-studio-site/1.0"})
    return urllib.request.urlopen(request, timeout=30)


def release_date(raw):
    text = (raw or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.datetime.strptime(text, fmt).strftime("%d %b %Y").lstrip("0")
        except ValueError:
            continue
    return text


def download_image(url, slug):
    parsed = urllib.parse.urlsplit(url or "")
    if parsed.scheme != "https" or not (parsed.hostname or "").endswith(IMAGE_HOST_SUFFIX):
        raise ValueError("refusing image from {0}".format(url))
    with open_url(parsed._replace(query="").geturl()) as response:
        kind = response.headers.get_content_type()
        if kind not in ("image/jpeg", "image/png"):
            raise ValueError("unexpected image type {0} for {1}".format(kind, url))
        body = response.read(MAX_IMAGE_BYTES + 1)
    if len(body) > MAX_IMAGE_BYTES:
        raise ValueError("image too large: {0}".format(url))
    target = os.path.join(ROOT, "assets", "games", slug, "header.jpg")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    previous = io.open(target, "rb").read() if os.path.exists(target) else b""
    if body != previous:
        io.open(target, "wb").write(body)
    return "assets/games/{0}/header.jpg".format(slug)


def collect(game):
    with open_url(DETAILS_URL.format(game["app_id"])) as response:
        payload = json.loads(response.read().decode("utf-8"))
    entry = payload.get(str(game["app_id"]), {})
    if not entry.get("success"):
        return None
    data = entry["data"]
    release = data.get("release_date") or {}
    return {
        "header_image": download_image(data.get("header_image"), game["slug"]),
        "store_live": True,
        "is_free": bool(data.get("is_free")),
        "coming_soon": bool(release.get("coming_soon")),
        "release_date": release_date(release.get("date")),
        "platforms": [name for name, on in (data.get("platforms") or {}).items() if on],
    }


def main():
    previous = json.load(io.open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    result = {}
    for game in GAMES:
        slug = game["slug"]
        entry = collect(game)
        if entry is None:
            entry = previous.get(slug) or {
                "header_image": "assets/games/{0}/header.jpg".format(slug),
                "store_live": False,
                "is_free": False,
                "coming_soon": True,
                "release_date": "",
                "platforms": ["windows"],
            }
            print("{0}: no public store page, keeping the current card".format(slug))
        else:
            print("{0}: store data refreshed".format(slug))
        entry["store_url"] = STORE_URL.format(game["app_id"])
        result[slug] = entry
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(text)


if __name__ == "__main__":
    sys.exit(main())
