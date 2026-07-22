# Penang Pulse

Weekly Penang events and food/popup radar. Static PWA driven by `feed.json`, plus editorial **Guides** under `/guides/<slug>/`.

**Editorial charter + URL scheme:** see [`EDITORIAL.md`](./EDITORIAL.md) (purpose, audience, series framework, canonical `https://penangpulse.com` paths).

## Local test

```sh
python3 -m http.server 5173
```

Open `http://localhost:5173/utilities/penang-pulse/`.

## Weekly feed refresh

See `scripts/penang-weekly-agent.md`.

```sh
python3 scripts/fetch-penang-sources.py
python3 scripts/build-penang-feed.py
python3 scripts/build-penang-feed.py --publish
```

Draft artifacts stay under `private/penang-pulse/` (not committed).

## Guides (editorial)

Separate from the weekly feed. Source posts live in `guides/posts/<slug>/post.md` (not deployed). Series registry: `guides/posts/_series.json`. Built output is `guides/index.json`, `guides/<slug>/`, and `guides/series/<series-slug>/` (including empty series).

Home strip personality: **Penang Pulse Says** + personal dek on a soft teal/cream band (quiet strip A).

### Edit locally

```sh
python3 -m venv scripts/penang-guides-editor/.venv
scripts/penang-guides-editor/.venv/bin/pip install Pillow
python3 scripts/penang-guides-editor/server.py
```

Open `http://127.0.0.1:8765/`. Series dashboard → series detail → episode editor. See `scripts/penang-guides-editor/README.md`.

### Build

```sh
scripts/penang-guides-editor/.venv/bin/python scripts/build-penang-guides.py
```

- Resizes `media/orig/` → web JPEGs (max width 1400, quality ~82)
- Rewrites `./media/orig/…` links to `./media/….jpg`
- Emits guide HTML (field note, series badge, spot widget), series index pages from registry + posts, and `guides/index.json`

Optional HEIC: `pip install pillow-heif` in the same venv.

### Deploy

GitHub Pages serves `/db-schedule-pwa/utilities/penang-pulse/`, but production custom domain `https://penangpulse.com/` and `https://fb-penang-pulse.web.app/` are Firebase Hosting target `penang-pulse`. After push to `main`:

```sh
npx firebase-tools deploy --only hosting:penang-pulse,hosting:main
```

Verify:

- `https://penangpulse.com/` / `https://fb-penang-pulse.web.app/`
- `https://penangpulse.com/guides/series/mee-myself-and-i/`
- `https://penangpulse.com/guides/series/family-matters/`
- `https://penangpulse.com/guides/index.json`
- `https://fb-penang-pulse.web.app/feed.json`
