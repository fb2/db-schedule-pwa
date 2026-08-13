# Movie Shelf editor (local only)

Mini CMS for the public Movie Shelf PWA. **Not deployed** — `scripts/**` is ignored by Firebase Hosting.

Do not put API keys, emails, or tokens in `utilities/movie-shelf/`. The TMDB key stays in a gitignored `.env` and is read only by this localhost server.

## Setup

```sh
cp scripts/movie-shelf-editor/.env.example scripts/movie-shelf-editor/.env
# paste TMDB_API_KEY (free: https://www.themoviedb.org/settings/api)
```

If `.env` is missing, the editor also looks at `../MovieCollection/.env` on this machine (never copied into the repo).

## Run

From the repo root:

```sh
python3 scripts/movie-shelf-editor/server.py
```

Open http://127.0.0.1:8766/

## Actions

| Action | Effect |
| --- | --- |
| **Save homes** | Writes `utilities/movie-shelf/collection.json` and regenerates `movies.js` |
| **Add film** | Appends a disc, fetches a TMDB poster to gitignored `posters/` |
| **Deploy** | `npx firebase-tools deploy --only hosting` — uploads shell + posters from disk. No git commit. |

Local preview: `python3 -m http.server 5173` then `/utilities/movie-shelf/`.

Live URL: `https://fb-personal-utilities.web.app/utilities/movie-shelf/` (Firebase Hosting). GitHub Pages will not have posters because JPEGs are gitignored.
