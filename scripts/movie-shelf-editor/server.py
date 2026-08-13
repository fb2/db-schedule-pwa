#!/usr/bin/env python3
"""Local-only Movie Shelf CMS. Not deployed (scripts/** is hosting-ignored).

Binds to 127.0.0.1 only. Never prints or returns the TMDB key.
No git commit, no email/author metadata.

  python3 scripts/movie-shelf-editor/server.py
  http://127.0.0.1:8766/
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


ROOT = pathlib.Path(__file__).resolve().parents[2]
EDITOR_DIR = pathlib.Path(__file__).resolve().parent
APP_DIR = ROOT / "utilities" / "movie-shelf"
COLLECTION = APP_DIR / "collection.json"
POSTERS_DIR = APP_DIR / "posters"
BUILD_SCRIPT = ROOT / "scripts" / "build-movie-shelf.py"
HOST = "127.0.0.1"
PORT = 8766

HOMES = ("hk", "penang")
SLUG_SAFE = re.compile(r"[^a-z0-9\s-]")


def load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for path in (
        EDITOR_DIR / ".env",
        ROOT / ".env",
        ROOT.parent / "MovieCollection" / ".env",
    ):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            env[key.strip()] = val.strip().strip('"').strip("'")
        break
    return env


def tmdb_key() -> str:
    return os.environ.get("TMDB_API_KEY", "").strip() or load_env().get("TMDB_API_KEY", "").strip()


def film_id(title: str, year: int) -> str:
    slug = SLUG_SAFE.sub("", title.lower())
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug).strip("-")
    return f"{slug}-{year}"


def load_collection() -> dict:
    data = json.loads(COLLECTION.read_text(encoding="utf-8"))
    data.setdefault("homes", {})
    data.setdefault("movies", [])
    return data


def save_collection(data: dict) -> None:
    COLLECTION.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], check=True, cwd=ROOT)


def tmdb_poster(title: str, year: int) -> str | None:
    key = tmdb_key()
    if not key:
        raise RuntimeError("No TMDB_API_KEY in scripts/movie-shelf-editor/.env")
    base = "https://api.themoviedb.org/3/search/movie"
    queries = [f"{base}?api_key={urllib.parse.quote(key)}&query={urllib.parse.quote(title)}"]
    if year:
        queries.insert(
            0,
            f"{base}?api_key={urllib.parse.quote(key)}&query={urllib.parse.quote(title)}&year={year}",
        )
    for url in queries:
        with urllib.request.urlopen(url, timeout=12) as resp:
            payload = json.loads(resp.read())
        results = payload.get("results") or []
        if results and results[0].get("poster_path"):
            return results[0]["poster_path"]
        time.sleep(0.15)
    return None


def download_poster(title: str, year: int) -> str | None:
    path = tmdb_poster(title, year)
    if not path:
        return None
    fname = f"{film_id(title, year)}.jpg"
    POSTERS_DIR.mkdir(parents=True, exist_ok=True)
    dest = POSTERS_DIR / fname
    urllib.request.urlretrieve(f"https://image.tmdb.org/t/p/w342{path}", dest)
    return fname


PAGE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Movie Shelf CMS</title>
  <style>
    :root { color-scheme: dark; font-family: ui-sans-serif, system-ui, sans-serif; }
    body { margin: 0; background: #111; color: #eee; }
    main { width: min(1100px, 100%); margin: 0 auto; padding: 24px 16px 64px; }
    h1 { font-size: 1.4rem; margin: 0 0 8px; }
    .lede { color: #9aa; margin: 0 0 20px; }
    form.add, .toolbar { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; align-items: end; }
    label { display: grid; gap: 4px; font-size: 12px; color: #9aa; }
    input, select, button { font: inherit; padding: 8px 10px; border-radius: 8px; border: 1px solid #333; background: #1a1a1a; color: #eee; }
    button { cursor: pointer; background: #2a2418; border-color: #d4a55366; color: #d4a553; }
    button.secondary { background: #1a1a1a; color: #ccc; border-color: #333; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th, td { text-align: left; padding: 8px 6px; border-bottom: 1px solid #222; }
    th { color: #888; font-size: 11px; letter-spacing: .06em; text-transform: uppercase; }
    .ok { color: #86efac; font-size: 13px; }
    .err { color: #fca5a5; font-size: 13px; }
    .count { color: #888; margin-bottom: 12px; }
  </style>
</head>
<body>
<main>
  <h1>Movie Shelf CMS</h1>
  <p class="lede">Localhost only. Posters stay gitignored. Deploy uploads them to Firebase Hosting without a git commit.</p>
  <p id="status" class="count"></p>

  <form class="add" id="add-form">
    <label>Title <input name="t" required /></label>
    <label>Year <input name="y" type="number" min="1900" max="2100" required /></label>
    <label>Letterboxd URL <input name="l" type="url" placeholder="https://letterboxd.com/film/..." /></label>
    <label>Home
      <select name="home">
        <option value="">Untagged</option>
        <option value="hk">Hong Kong · Coral Court</option>
        <option value="penang">Penang · Tanjung Bungah</option>
      </select>
    </label>
    <button type="submit">Add film + poster</button>
  </form>

  <div class="toolbar">
    <label>Filter
      <select id="filter">
        <option value="all">All</option>
        <option value="untagged">Untagged</option>
        <option value="hk">Hong Kong</option>
        <option value="penang">Penang</option>
      </select>
    </label>
    <label>Search <input id="q" type="search" placeholder="Title" /></label>
    <button id="save" type="button">Save homes</button>
    <button id="deploy" class="secondary" type="button">Deploy hosting</button>
  </div>
  <p id="msg"></p>
  <table>
    <thead><tr><th>Title</th><th>Year</th><th>Home</th><th>Poster</th></tr></thead>
    <tbody id="rows"></tbody>
  </table>
</main>
<script>
const rowsEl = document.getElementById("rows");
const msg = document.getElementById("msg");
let movies = [];

function say(text, ok) {
  msg.className = ok ? "ok" : "err";
  msg.textContent = text;
}

async function load() {
  const data = await (await fetch("/api/collection")).json();
  movies = data.movies || [];
  document.getElementById("status").textContent =
    movies.length + " discs · " + movies.filter(m => !m.home).length + " untagged";
  render();
}

function render() {
  const filter = document.getElementById("filter").value;
  const q = document.getElementById("q").value.trim().toLowerCase();
  rowsEl.replaceChildren();
  for (const m of movies) {
    if (filter === "untagged" && m.home) continue;
    if (filter === "hk" && m.home !== "hk") continue;
    if (filter === "penang" && m.home !== "penang") continue;
    if (q && !(m.t + " " + m.y).toLowerCase().includes(q)) continue;
    const tr = document.createElement("tr");
    const titleTd = document.createElement("td");
    titleTd.textContent = m.t;
    const yearTd = document.createElement("td");
    yearTd.textContent = String(m.y);
    const homeTd = document.createElement("td");
    const posterTd = document.createElement("td");
    posterTd.textContent = m.poster ? "yes" : "—";
    const sel = document.createElement("select");
    sel.dataset.id = m.id;
    sel.innerHTML = `<option value="">Untagged</option>
      <option value="hk">Hong Kong</option>
      <option value="penang">Penang</option>`;
    sel.value = m.home || "";
    sel.addEventListener("change", () => { m.home = sel.value || null; });
    homeTd.append(sel);
    tr.append(titleTd, yearTd, homeTd, posterTd);
    rowsEl.append(tr);
  }
}

document.getElementById("filter").addEventListener("change", render);
document.getElementById("q").addEventListener("input", render);

document.getElementById("save").addEventListener("click", async () => {
  const homes = {};
  for (const m of movies) homes[m.id] = m.home;
  const res = await fetch("/api/homes", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ homes }),
  });
  const out = await res.json();
  say(out.error || "Saved " + out.updated + " homes and rebuilt movies.js", res.ok);
  if (res.ok) load();
});

document.getElementById("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const res = await fetch("/api/add", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      t: fd.get("t"),
      y: Number(fd.get("y")),
      l: fd.get("l") || "",
      home: fd.get("home") || null,
    }),
  });
  const out = await res.json();
  say(out.error || "Added " + out.id, res.ok);
  if (res.ok) { e.target.reset(); load(); }
});

document.getElementById("deploy").addEventListener("click", async () => {
  say("Deploying Firebase Hosting…", true);
  const res = await fetch("/api/deploy", { method: "POST" });
  const out = await res.json();
  say(out.error || out.message || "Deploy finished", res.ok);
});

load();
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self._send(code, raw, "application/json; charset=utf-8")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length") or "0")
        if length > 2_000_000:
            raise ValueError("payload too large")
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if self.path == "/api/collection":
            self._json(200, load_collection())
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        try:
            if self.path == "/api/homes":
                payload = self._read_json()
                homes = payload.get("homes") or {}
                data = load_collection()
                updated = 0
                for movie in data["movies"]:
                    if movie["id"] in homes:
                        value = homes[movie["id"]]
                        movie["home"] = value if value in HOMES else None
                        updated += 1
                save_collection(data)
                self._json(200, {"updated": updated})
                return
            if self.path == "/api/add":
                payload = self._read_json()
                title = str(payload.get("t") or "").strip()
                year = int(payload.get("y") or 0)
                letterboxd = str(payload.get("l") or "").strip()
                home = payload.get("home") if payload.get("home") in HOMES else None
                if not title or year < 1890:
                    self._json(400, {"error": "title and year required"})
                    return
                ident = film_id(title, year)
                data = load_collection()
                if any(m["id"] == ident for m in data["movies"]):
                    self._json(409, {"error": "already in the catalogue"})
                    return
                poster = None
                try:
                    poster = download_poster(title, year)
                except Exception as exc:
                    self._json(400, {"error": str(exc)})
                    return
                data["movies"].append(
                    {
                        "id": ident,
                        "t": title,
                        "y": year,
                        "home": home,
                        "l": letterboxd,
                        "poster": poster,
                        "kind": "disc",
                    }
                )
                def sort_key(movie: dict) -> tuple:
                    title = movie["t"].lower()
                    for article in ("the ", "a ", "an "):
                        if title.startswith(article):
                            title = title[len(article) :]
                            break
                    return (title, movie["y"])

                data["movies"].sort(key=sort_key)
                save_collection(data)
                self._json(200, {"id": ident, "poster": poster})
                return
            if self.path == "/api/deploy":
                result = subprocess.run(
                    ["npx", "firebase-tools", "deploy", "--only", "hosting"],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    err = (result.stderr or result.stdout or "deploy failed")[-800:]
                    self._json(500, {"error": err})
                    return
                self._json(
                    200,
                    {
                        "message": "Deployed. Live: https://fb-personal-utilities.web.app/utilities/movie-shelf/"
                    },
                )
                return
            self._json(404, {"error": "not found"})
        except Exception as exc:
            self._json(500, {"error": str(exc)})


def main() -> int:
    POSTERS_DIR.mkdir(parents=True, exist_ok=True)
    if not COLLECTION.is_file():
        print(f"ERROR: missing {COLLECTION}", file=sys.stderr)
        return 1
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Movie Shelf CMS (localhost only) http://{HOST}:{PORT}/")
    print("TMDB key:", "present" if tmdb_key() else "missing — add posters via .env")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
